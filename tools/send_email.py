#!/usr/bin/env python3
"""Step 3a: Send email via Resend API or dry-run fallback."""
import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import config

# =============================================================================
# Constants
# =============================================================================
DRY_RUN = config.is_dry_run()
RESEND_API_KEY = config.RESEND_API_KEY
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_NAME = config.SENDER_NAME
SENDER_PHYSICAL_ADDRESS = config.SENDER_PHYSICAL_ADDRESS
CAMPAIGN_LANGUAGE = config.CAMPAIGN_LANGUAGE

# =============================================================================
# Email sender abstraction
# =============================================================================

class EmailSender(ABC):
    """Abstract base class for email providers."""
    
    @abstractmethod
    def send(self, to_email: str, subject: str, html_body: str) -> dict:
        """Send an email.
        
        Returns:
            dict with 'success' (bool), 'error' (str), and optionally 'quota_exceeded' (bool)
        """
        pass


class ResendSender(EmailSender):
    """Email sender implementation using Resend API."""
    
    def __init__(self, api_key: str, from_email: str, from_name: str = ""):
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name
    
    def send(self, to_email: str, subject: str, html_body: str) -> dict:
        """Send email via Resend API.
        
        Returns:
            dict with 'success', 'error', and 'quota_exceeded' (True if 429 error).
        """
        try:
            import resend
            resend.api_key = self.api_key
            
            from_header = self.from_email
            if self.from_name:
                from_header = f"{self.from_name} <{self.from_email}>"
            
            result = resend.Emails.send({
                "from": from_header,
                "to": to_email,
                "subject": subject,
                "html": html_body,
                "headers": {
                    "List-Unsubscribe": f"<mailto:unsubscribe@{self._get_domain()}?subject=Unsubscribe>",
                    "Reply-To": self.from_email
                }
            })
            print(f"Email sent: {result.get('id', 'ok')}")
            return {"success": True, "error": "", "quota_exceeded": False}
        except Exception as exc:
            error_msg = str(exc)
            # Check for quota exceeded (429)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                print(f"ERROR: Resend quota exceeded: {error_msg}", file=sys.stderr)
                return {"success": False, "error": "QUOTA_EXCEEDED", "quota_exceeded": True}
            print(f"ERROR sending email: {error_msg}", file=sys.stderr)
            return {"success": False, "error": error_msg, "quota_exceeded": False}
    
    def _get_domain(self) -> str:
        """Extract domain from sender email."""
        if "@" in self.from_email:
            return self.from_email.split("@")[1]
        return "example.com"


class DryRunSender(EmailSender):
    """Dry-run email sender that prints to console."""
    
    def send(self, to_email: str, subject: str, html_body: str) -> dict:
        """Print email details to console."""
        print(f"[DRY RUN] Would send email:")
        print(f"  from: {SENDER_EMAIL or '(not set)'} ({SENDER_NAME or 'no name'})")
        print(f"  to:   {to_email}")
        print(f"  subject: {subject}")
        print(f"  HTML body preview: {html_body[:200]}...")
        return {"success": True, "error": "", "quota_exceeded": False}


def _get_sender() -> EmailSender:
    """Get the appropriate email sender based on configuration."""
    if DRY_RUN or not RESEND_API_KEY:
        return DryRunSender()
    return ResendSender(RESEND_API_KEY, SENDER_EMAIL, SENDER_NAME)

# =============================================================================
# HTML generation
# =============================================================================

def _generate_html_email(offer: dict, language: str = "en") -> str:
    """Generate HTML email with styling.
    
    Args:
        offer: Offer dict with keys offer_title, offer_details, cta_text
        language: 'en' or 'ar' for RTL support
    
    Returns:
        HTML string for the email.
    """
    is_rtl = language == "ar"
    direction = "rtl" if is_rtl else "ltr"
    lang = "ar" if is_rtl else "en"
    
    # Arabic-friendly font stack
    font_family = "'Segoe UI', Tahoma, Arial, sans-serif"
    if is_rtl:
        font_family = "'Segoe UI', 'Tahoma', 'Arial', 'Noto Sans Arabic', sans-serif"
    
    # Replace newlines with <br> in offer_details
    offer_details_html = offer.get("offer_details", "").replace("\n", "<br>")
    
    # CTA button text
    cta_text = offer.get("cta_text", "Click Here")
    
    # Physical address for footer
    footer_address = SENDER_PHYSICAL_ADDRESS or ""
    
    # Get domain for unsubscribe link
    domain = "example.com"
    if "@" in SENDER_EMAIL:
        domain = SENDER_EMAIL.split("@")[1]
    
    html = f'''<!DOCTYPE html>
<html dir="{direction}" lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: {font_family};
      line-height: 1.6;
      color: #333333;
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      background-color: #f5f5f5;
    }}
    .email-container {{
      background-color: #ffffff;
      border-radius: 8px;
      padding: 30px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .header {{
      text-align: center;
      margin-bottom: 20px;
    }}
    .offer-title {{
      color: #007bff;
      font-size: 24px;
      margin: 0 0 20px 0;
      text-align: center;
    }}
    .offer-details {{
      font-size: 16px;
      margin: 20px 0;
      text-align: {'right' if is_rtl else 'left'};
    }}
    .cta-container {{
      text-align: center;
      margin: 30px 0;
    }}
    .cta {{
      display: inline-block;
      background: #007bff;
      color: white;
      padding: 12px 24px;
      text-decoration: none;
      border-radius: 4px;
      font-weight: bold;
    }}
    .footer {{
      font-size: 12px;
      color: #888888;
      margin-top: 30px;
      border-top: 1px solid #eeeeee;
      padding-top: 10px;
      text-align: center;
    }}
    .footer address {{
      font-style: normal;
      margin-bottom: 5px;
    }}
    .unsubscribe-link {{
      color: #888888;
      text-decoration: underline;
    }}
    @media only screen and (max-width: 480px) {{
      body {{
        padding: 10px;
      }}
      .email-container {{
        padding: 20px;
      }}
      .offer-title {{
        font-size: 20px;
      }}
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <h1 class="offer-title">{offer.get('offer_title', '')}</h1>
    <div class="offer-details">
      <p>{offer_details_html}</p>
    </div>
    <div class="cta-container">
      <a href="#" class="cta">{cta_text}</a>
    </div>
    <div class="footer">
      <address>{footer_address}</address>
      <a href="mailto:unsubscribe@{domain}?subject=Unsubscribe" class="unsubscribe-link">Unsubscribe</a>
    </div>
  </div>
</body>
</html>'''
    return html


def send_email(customer_email: str, offer: dict, language: str = None):
    """Send an email to a customer with the given offer.
    
    Args:
        customer_email: Recipient email address
        offer: Offer dict with keys offer_title, offer_details, cta_text
        language: Language code ('en' or 'ar'). Defaults to config.CAMPAIGN_LANGUAGE.
    
    Returns:
        dict with 'success', 'error', and 'quota_exceeded' keys.
    """
    if language is None:
        language = CAMPAIGN_LANGUAGE
    
    subject = offer.get("offer_title", "")
    html_body = _generate_html_email(offer, language)
    
    sender = _get_sender()
    return sender.send(customer_email, subject, html_body)


if __name__ == "__main__":
    import json
    test_offer = {
        "offer_type": "discount",
        "offer_title": "Test subject",
        "offer_details": "Test body line 1\nTest body line 2",
        "cta_text": "Click here",
    }
    result = send_email("test@example.com", test_offer)
    print(json.dumps(result))
