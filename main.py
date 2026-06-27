#!/usr/bin/env python3
"""Main orchestrator: run the full database reactivation workflow."""
import argparse
import sys
import time
from pathlib import Path

import config
from tools.fetch_customers import fetch_customers
from tools.generate_offer import generate_offer
from tools.send_email import send_email
from tools.send_instagram_dm import send_instagram_dm
from tools.log_action import log_action

DEMO_OUTPUT_DIR = Path(".tmp/demo_emails")


def _print_config_summary():
    """Print a one-line config summary at startup."""
    print(
        f"Config: business_type={config.BUSINESS_TYPE}, language={config.CAMPAIGN_LANGUAGE}, "
        f"thresholds=({config.CHURN_THRESHOLD_INFO}/{config.CHURN_THRESHOLD_BONUS}/{config.CHURN_THRESHOLD_DISCOUNT}), "
        f"discount={config.DISCOUNT_PCT}%"
    )


def _save_demo_html(customer_id: str, offer: dict, subject: str, language: str = "en") -> Path:
    """Save offer as a styled HTML file for demo viewing."""
    DEMO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{customer_id}_{offer['offer_type']}.html"
    path = DEMO_OUTPUT_DIR / safe_name

    # Determine RTL/LTR and language attributes
    direction = "rtl" if language == "ar" else "ltr"
    lang_attr = "ar" if language == "ar" else "en"
    
    # Arabic-friendly font stack
    font_family = "'Segoe UI', Tahoma, Arial, sans-serif"
    if language == "ar":
        font_family = "'Segoe UI', 'Tahoma', 'Arial', 'Noto Sans Arabic', sans-serif"
    
    # Text alignment for RTL
    text_align = "right" if language == "ar" else "left"

    offer_details_html = offer.get("offer_details", "").replace("\n", "<br>")
    cta_text = offer.get("cta_text", "Click Here")

    html = f'''<!DOCTYPE html>
<html dir="{direction}" lang="{lang_attr}">
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
    h1 {{
      color: #007bff;
      font-size: 24px;
      margin: 0 0 20px 0;
      text-align: center;
    }}
    p {{
      font-size: 16px;
      margin: 20px 0;
    }}
    .offer-details {{
      text-align: {text_align};
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
  </style>
</head>
<body>
  <div class="email-container">
    <h1>{subject}</h1>
    <div class="offer-details">
      <p>{offer_details_html}</p>
    </div>
    <div class="cta-container">
      <a href="#" class="cta">{cta_text}</a>
    </div>
    <div class="footer">
      <p>Demo output — no email was actually sent</p>
    </div>
  </div>
</body>
</html>'''
    path.write_text(html, encoding="utf-8")
    return path


def _demo_mode(customers: list[dict], channel: str):
    """Run in demo mode: generate offers, save HTML files, print summary."""
    # Force CSV-only data source for demo mode (ignores Google Sheets config)
    original_sheet_id = config.GOOGLE_SHEET_ID
    config.GOOGLE_SHEET_ID = ""
    try:
        # Re-fetch customers from CSV to ensure we use local data
        customers = fetch_customers(Path(config.CUSTOMERS_CSV_PATH))
    finally:
        config.GOOGLE_SHEET_ID = original_sheet_id
    
    print(f"\n========== DATABASE REACTIVATION DEMO ==========\n")
    print(f"Found {len(customers)} eligible customer{'s' if len(customers) != 1 else ''}\n")

    language = config.CAMPAIGN_LANGUAGE

    for i, customer in enumerate(customers, 1):
        cid = customer["customer_id"]
        name = customer.get("name", "Unknown")
        business_type = config.BUSINESS_TYPE

        offer = generate_offer(customer, force_mock=True)
        if offer is None:
            print(f"[{i}/{len(customers)}] {cid} - {name} ({business_type})")
            print(f"    ERROR: offer generation failed, skipping.\n")
            log_action(cid, "FAILED_GENERATION", "none", "failed", "Invalid JSON from AI")
            continue

        subject = offer.get("offer_title", "")
        html_path = _save_demo_html(cid, offer, subject, language)

        print(f"[{i}/{len(customers)}] {cid} - {name} ({business_type})")
        print(f"    Offer: {offer['offer_type']}")
        print(f"    Subject: {subject}")
        print(f"    Preview saved to: {html_path}\n")

        log_action(cid, "SENT_WINBACK_OFFER", offer["offer_type"], "success", "demo_mode")
        time.sleep(0.5)

    total = len(customers)
    print(f"========== DEMO COMPLETE ==========\n")
    print(f"Total processed: {total}")
    print(f"Emails generated: {total}")
    print(f"Outputs saved to: {DEMO_OUTPUT_DIR}/\n")


def _production_send(customers: list[dict], channel: str):
    """Run in production mode: generate offers and actually send."""
    total = len(customers)
    sent_count = 0
    failed_count = 0
    queued_count = 0

    print(f"Found {total} eligible customer{'s' if total != 1 else ''}. Starting outreach via {channel}...\n")

    for customer in customers:
        cid = customer["customer_id"]
        name = customer.get("name", "Unknown")
        print(f"--- Processing {cid}: {name} ---")

        offer = generate_offer(customer)
        if offer is None:
            log_action(cid, "FAILED_GENERATION", "none", "failed", "Invalid JSON from AI")
            print(f"Skipping {cid}: offer generation failed.\n")
            failed_count += 1
            continue

        print(f"Generated offer: {offer['offer_type']} | {offer['offer_title']}")

        # Determine channels to attempt
        email = customer.get("email") or ""
        ig_handle = customer.get("instagram_handle") or ""
        email_success = False
        ig_success = False

        # Decision tree for channel selection
        should_send_email = channel in ("email", "both") and bool(email)
        should_send_ig = channel in ("instagram", "both") or (not email and bool(ig_handle))

        # Email channel
        if should_send_email:
            result = send_email(email, offer)
            email_success = result.get("success", False)

            # Handle quota exceeded
            if result.get("quota_exceeded"):
                print("Resend quota exceeded. Stopping. Remaining customers queued for tomorrow.")
                # Queue all remaining customers
                remaining = customers[customers.index(customer) + 1:]
                for rem_customer in remaining:
                    log_action(
                        rem_customer["customer_id"],
                        "QUEUED_FOR_TOMORROW",
                        offer["offer_type"],
                        "success",
                        "Resend quota exceeded",
                    )
                    queued_count += 1
                queued_count += len(remaining)
                print(f"\n========== WORKFLOW COMPLETE ==========\n")
                print(f"Total eligible: {total}")
                print(f"Successfully sent: {sent_count}")
                print(f"Failed: {failed_count}")
                print(f"Queued for tomorrow: {queued_count}")
                print(f"Log file: {config.SYSTEM_LOG_PATH}")
                print("=" * 42)
                return

            # Fall back to Instagram if email succeeded but IG is available
            if email_success and ig_handle:
                print(f"    -> Falling back to Instagram DM for {cid}.")
                ig_result = send_instagram_dm(ig_handle, offer)
                ig_success = ig_result.get("success", False)
        elif not email and ig_handle:
            # No email available - send Instagram as fallback
            print(f"WARNING: No email for {cid}. Falling back to Instagram DM.")
            ig_result = send_instagram_dm(ig_handle, offer)
            ig_success = ig_result.get("success", False)

        # Instagram DM (standalone)
        if should_send_ig and not ig_success:
            ig_result = send_instagram_dm(ig_handle, offer)
            ig_success = ig_result.get("success", False)

        # Log result
        any_success = email_success or ig_success
        if any_success:
            sent_count += 1
            status = "success"
            error = ""
        else:
            failed_count += 1
            status = "failed"
            errors = []
            if channel in ("email", "both") and not email:
                errors.append("no_email")
            if not ig_handle:
                errors.append("no_instagram_handle")
            error = ", ".join(errors) or "unknown"

        log_action(cid, "SENT_WINBACK_OFFER", offer["offer_type"], status, error)
        print(f"Logged: {status} | errors: {error or 'none'}\n")

        time.sleep(1)

    print(f"\n========== WORKFLOW COMPLETE ==========\n")
    print(f"Total eligible: {total}")
    print(f"Successfully sent: {sent_count}")
    print(f"Failed: {failed_count}")
    print(f"Queued for tomorrow: {queued_count}")
    print(f"Log file: {config.SYSTEM_LOG_PATH}")
    print("=" * 42)


def main():
    parser = argparse.ArgumentParser(description="Database Reactivation Workflow")
    parser.add_argument("--demo", action="store_true", help="Demo mode: no API calls, outputs HTML files")
    parser.add_argument("--confirm", action="store_true", help="Required for production sends")
    parser.add_argument(
        "--channel",
        choices=["email", "instagram", "both"],
        default="email",
        help="Which channel(s) to use for outreach (default: email)",
    )
    parser.add_argument(
        "--business-type",
        choices=["gym", "dental", "coaching"],
        default=None,
        help="Override .env BUSINESS_TYPE",
    )
    parser.add_argument(
        "--language",
        choices=["en", "ar"],
        default=None,
        help="Override .env CAMPAIGN_LANGUAGE",
    )
    parser.add_argument(
        "--customer-id",
        default=None,
        help="Process a single customer only",
    )
    args = parser.parse_args()

    # Apply CLI overrides to config module
    if args.business_type is not None:
        config.BUSINESS_TYPE = args.business_type
    if args.language is not None:
        config.CAMPAIGN_LANGUAGE = args.language

    _print_config_summary()

    # Production safety guard
    if not args.demo and not args.confirm:
        print(
            "ERROR: Production mode requires --confirm flag.\n"
            "       Use --demo to preview without sending.\n"
            "       Use --confirm to actually send emails."
        )
        sys.exit(1)

    # Step 1: Fetch eligible customers
    customers = fetch_customers()

    if not customers:
        log_action("NONE", "NOT_FOUND", "none", "success", "")
        print("No eligible customers found today.")
        sys.exit(0)

    # Step 2: Filter to single customer if requested
    if args.customer_id is not None:
        matched = [c for c in customers if c["customer_id"] == args.customer_id]
        if not matched:
            print(f"Customer '{args.customer_id}' not found or not eligible.")
            log_action(args.customer_id, "NOT_FOUND", "none", "failed", "customer_id not eligible")
            sys.exit(0)
        customers = matched
        print(f"Processing single customer: {args.customer_id}\n")

    # Step 3: Route to demo or production
    if args.demo:
        _demo_mode(customers, args.channel)
    else:
        # Validate production config before sending
        try:
            config.validate_production_config()
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            print("Cannot proceed with production send. Please set all required environment variables.", file=sys.stderr)
            sys.exit(1)
        _production_send(customers, args.channel)


if __name__ == "__main__":
    main()