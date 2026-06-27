#!/usr/bin/env python3
"""Step 2: Generate personalized offer via Claude API or dry-run fallback."""
import json
import sys
from pathlib import Path

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import config

# =============================================================================
# Constants
# =============================================================================
MODEL_INFORMATIONAL = "claude-3-haiku-20240307"
MODEL_BONUS_DISCOUNT = "claude-3-sonnet-20240229"

DRY_RUN = config.is_dry_run()

# Retry once on rate limit (first attempt only)
RATE_LIMIT_RETRIES = 1

# =============================================================================
# Prompt loading
# =============================================================================

def _load_prompt_template(business_type: str) -> str:
    """Load the base prompt and append industry-specific additions.
    
    Args:
        business_type: One of 'gym', 'dental', 'coaching'
    
    Returns:
        Combined prompt string with {placeholders} for str.format().
    """
    prompts_dir = Path(__file__).parent / "prompts"
    
    # Load base template
    base_path = prompts_dir / "base.md"
    if base_path.exists():
        with open(base_path, "r", encoding="utf-8") as f:
            template = f.read()
    else:
        # Fallback inline template if file missing
        template = """You are a specialist in writing customer re-engagement emails.
Write a personalized re-engagement email for this customer:

Name: {name}
Churn score: {churn_score}
Preferred categories: {preferred_categories}
Last purchase date: {last_purchase_date}
Total purchases: {total_purchases}
Days since last contact: {days_since_last_contact}

Offer type to use: {offer_type}
- informational: mention new products in their preferred categories
- bonus_points: offer reward points on their next purchase
- discount: offer a direct {discount_pct}% discount with urgency

Rules:
- Start with their name
- Mention how long it has been since their last visit
- Keep tone warm, never pushy
- 3-4 short paragraphs
- End with a clear call to action
- Write in {language}

Return ONLY valid JSON, no extra text, in this exact format:
{{
  "offer_type": "informational|bonus_points|discount",
  "offer_title": "email subject line here",
  "offer_details": "full email body here",
  "cta_text": "call to action button text"
}}"""
    
    # Load industry-specific template and append
    industry_path = prompts_dir / f"{business_type}.md"
    if industry_path.exists():
        with open(industry_path, "r", encoding="utf-8") as f:
            industry_template = f.read()
        template = template + "\n\n---\n\n" + industry_template
    
    return template


def _offer_type_from_score(churn_score: float) -> str:
    """Determine offer type based on churn score and configurable thresholds."""
    if churn_score < config.CHURN_THRESHOLD_BONUS:
        return "informational"
    if churn_score < config.CHURN_THRESHOLD_DISCOUNT:
        return "bonus_points"
    return "discount"


def _mock_offer(customer: dict, offer_type: str) -> dict:
    """Generate a mock offer for dry-run mode."""
    name = customer["name"]
    days = customer.get("days_since_last_contact", 90)
    discount_pct = config.DISCOUNT_PCT
    
    if offer_type == "discount":
        title = f"{name}, {discount_pct}% off your next visit — only for you"
        details = (
            f"Hi {name},\n\n"
            f"It's been {days} days since your last visit, and we wanted to reach out personally.\n\n"
            f"As a special welcome back, we're offering you {discount_pct}% off your next purchase. "
            "This is our way of saying we miss you and want to welcome you back.\n\n"
            "Don't miss out — this offer is available for a limited time."
        )
        cta = "Claim My Discount"
    elif offer_type == "bonus_points":
        title = f"{name}, we added bonus points to your account"
        details = (
            f"Hi {name},\n\n"
            f"It's been {days} days since your last visit, and we wanted to reach out personally.\n\n"
            "We've added bonus reward points to your account as a thank-you for being a valued customer. "
            "Use them on your next visit and treat yourself to something special.\n\n"
            "Points never expire — take your time."
        )
        cta = "View My Points"
    else:  # informational
        title = f"{name}, we miss you — here is something special"
        details = (
            f"Hi {name},\n\n"
            f"It's been {days} days since your last visit, and we wanted to reach out personally.\n\n"
            "We have curated new arrivals in the categories you love, and as a valued customer, "
            "we would love to welcome you back with something extra.\n\n"
            "Take a look — we think you will be pleasantly surprised."
        )
        cta = "Shop Now"
    
    return {
        "offer_type": offer_type,
        "offer_title": title,
        "offer_details": details,
        "cta_text": cta,
    }


def generate_offer(customer: dict, force_mock: bool = False):
    """Generate a personalized offer for a customer.
    
    Loads the appropriate prompt template based on business_type,
    selects the model based on offer tier, and retries once on invalid JSON.
    
    Args:
        customer: Customer dict with required fields.
        force_mock: If True, always return a mock offer without calling the API.
    
    Returns:
        Offer dict with keys: offer_type, offer_title, offer_details, cta_text
        or None if generation fails.
    """
    offer_type = _offer_type_from_score(float(customer["churn_score"]))
    
    if force_mock or DRY_RUN:
        mode_label = "MOCK" if force_mock else "DRY RUN"
        print(f"[{mode_label}] Returning mock offer for {customer['customer_id']} with offer_type={offer_type}")
        return _mock_offer(customer, offer_type)
    
    # Load prompt template by business_type
    business_type = config.BUSINESS_TYPE
    language = config.CAMPAIGN_LANGUAGE
    discount_pct = config.DISCOUNT_PCT
    
    prompt_template = _load_prompt_template(business_type)
    
    # Build prompt with all placeholders
    prompt = prompt_template.format(
        name=customer["name"],
        churn_score=customer["churn_score"],
        preferred_categories=customer.get("preferred_categories", ""),
        last_purchase_date=customer.get("last_purchase_date", ""),
        total_purchases=customer.get("total_purchases", 0),
        days_since_last_contact=customer.get("days_since_last_contact", 90),
        offer_type=offer_type,
        business_type=business_type,
        language=language,
        discount_pct=discount_pct,
    )
    
    # Add Arabic language instruction if needed
    if language == "ar":
        prompt = prompt + "\n\nWrite the email in Modern Standard Arabic. Use a warm, friendly tone."
    
    # Select model based on offer tier
    model = MODEL_INFORMATIONAL if offer_type == "informational" else MODEL_BONUS_DISCOUNT
    
    # Retry once on rate limit, retry once on invalid JSON
    for attempt in range(2):
        try:
            from anthropic import Anthropic, RateLimitError
            client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            
            # Extract JSON from markdown code blocks if present
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
            
            offer = json.loads(raw)
            
            # Validate required keys
            required_keys = {"offer_type", "offer_title", "offer_details", "cta_text"}
            if not all(k in offer for k in required_keys):
                raise ValueError(f"Missing required JSON keys. Got: {offer.keys()}")
            
            return offer
        except RateLimitError as exc:
            print(f"Attempt {attempt + 1}: Rate limit hit for customer {customer['customer_id']}: {exc}", file=sys.stderr)
            if attempt < RATE_LIMIT_RETRIES:
                print("Retrying after 2 seconds...", file=sys.stderr)
                time.sleep(2)
                continue
            print(f"ERROR: Rate limit retry failed for customer {customer['customer_id']}. Giving up.", file=sys.stderr)
            return None
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"Attempt {attempt + 1}: Invalid JSON from AI for customer {customer['customer_id']}: {exc}", file=sys.stderr)
            if attempt == 0:
                print("Retrying once...", file=sys.stderr)
                continue
            print(f"ERROR: Retry failed for customer {customer['customer_id']}. Giving up.", file=sys.stderr)
            return None
        except Exception as exc:
            print(f"ERROR: Unexpected error calling Claude API for customer {customer['customer_id']}: {exc}", file=sys.stderr)
            return None
    
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--customer-id", default="C001")
    args = parser.parse_args()

    # Quick test harness
    from tools.fetch_customers import fetch_customers
    customers = fetch_customers()
    customer = next((c for c in customers if c["customer_id"] == args.customer_id), None)
    if not customer:
        print(f"Customer {args.customer_id} not found or not eligible.")
        sys.exit(1)

    offer = generate_offer(customer)
    print(json.dumps(offer, indent=2))
