#!/usr/bin/env python3
"""Main orchestrator: run the full database reactivation workflow.

This version uses a minimal agentic layer:
  1. State machine persists campaign progress per customer.
  2. Planner decides offer type + channel using history.
  3. Guardrail validates generated offers before sending.
"""
import argparse
import sys
import time
from dataclasses import asdict
from pathlib import Path

import config
from guardrail import validate_offer
from planner import CampaignPlan, decide_plan
from state import CampaignState, CampaignStatus, StateStore
from tools.fetch_customers import fetch_customers
from tools.generate_offer import generate_offer
from tools.log_action import log_action
from tools.send_email import send_email
from tools.send_instagram_dm import send_instagram_dm

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

    direction = "rtl" if language == "ar" else "ltr"
    lang_attr = "ar" if language == "ar" else "en"
    font_family = "'Segoe UI', Tahoma, Arial, sans-serif"
    if language == "ar":
        font_family = "'Segoe UI', 'Tahoma', 'Arial', 'Noto Sans Arabic', sans-serif"
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


def _generate_and_validate_offer(customer: dict, plan: CampaignPlan, demo_mode: bool) -> tuple[dict | None, str]:
    """Generate an offer and run it through the guardrail.

    Returns (offer, error_message). If generation or guardrail fails, offer is None.
    """
    offer = generate_offer(customer, force_mock=demo_mode)
    if offer is None:
        return None, "Invalid JSON from AI"

    result = validate_offer(offer, plan)
    if not result:
        return None, f"Guardrail failed: {'; '.join(result.reasons)}"

    return offer, ""


def _send_to_channels(customer: dict, offer: dict, plan: CampaignPlan) -> dict:
    """Execute send across the chosen channel(s).

    Returns a dict with email_success, ig_success, quota_exceeded, errors.
    """
    email = (customer.get("email") or "").strip()
    ig_handle = (customer.get("instagram_handle") or "").strip()
    channel = plan.channel

    email_success = False
    ig_success = False
    quota_exceeded = False
    errors: list[str] = []

    should_send_email = channel in ("email", "both") and bool(email)
    should_send_ig = channel in ("instagram", "both") or (not email and bool(ig_handle))

    if should_send_email:
        result = send_email(email, offer)
        email_success = result.get("success", False)
        if result.get("quota_exceeded"):
            quota_exceeded = True
        elif not email_success:
            errors.append(result.get("error") or "email_send_failed")

    if should_send_ig and not ig_success:
        result = send_instagram_dm(ig_handle, offer)
        ig_success = result.get("success", False)
        if not ig_success:
            errors.append(result.get("error") or "instagram_send_failed")

    return {
        "email_success": email_success,
        "ig_success": ig_success,
        "any_success": email_success or ig_success,
        "quota_exceeded": quota_exceeded,
        "errors": errors,
    }


def _run_campaign(
    customer: dict,
    store: StateStore,
    demo_mode: bool,
) -> CampaignState:
    """Run the full agentic pipeline for one customer.

    Updates the state store after each major step.
    """
    cid = customer["customer_id"]
    name = customer.get("name", "Unknown")
    state = store.get_or_create(cid)

    # Step 1: Plan
    plan = decide_plan(customer)
    state = state.transition(CampaignStatus.PLANNED, plan=asdict(plan))
    store.update(state)
    print(f"--- Processing {cid}: {name} ---")
    print(f"Plan: {plan.offer_type} via {plan.channel} | reasoning: {plan.reasoning}")

    if plan.channel == "none":
        error = "No contact information available"
        state = state.transition(CampaignStatus.SKIPPED, error_message=error)
        store.update(state)
        log_action(cid, "SKIPPED", plan.offer_type, "failed", error)
        print(f"Skipped: {error}\n")
        return state

    # Step 2: Generate + guardrail
    state = state.transition(CampaignStatus.GENERATED)
    store.update(state)

    offer, error = _generate_and_validate_offer(customer, plan, demo_mode)
    if offer is None:
        state = state.transition(CampaignStatus.GUARDRAIL_FAILED, error_message=error)
        store.update(state)
        log_action(cid, "FAILED_GENERATION", plan.offer_type, "failed", error)
        print(f"Skipping {cid}: {error}\n")
        return state

    state = state.transition(CampaignStatus.GUARDRAIL_PASSED, offer=offer)
    store.update(state)
    print(f"Generated offer: {offer['offer_type']} | {offer['offer_title']}")

    # Demo mode: save HTML preview and stop before sending
    if demo_mode:
        language = config.CAMPAIGN_LANGUAGE
        html_path = _save_demo_html(cid, offer, offer["offer_title"], language)
        state = state.transition(CampaignStatus.SENT, send_result={"demo": True, "html_path": str(html_path)})
        store.update(state)
        log_action(cid, "SENT_WINBACK_OFFER", offer["offer_type"], "success", "demo_mode")
        print(f"Preview saved to: {html_path}\n")
        time.sleep(0.5)
        return state

    # Step 3: Send
    send_result = _send_to_channels(customer, offer, plan)

    if send_result["quota_exceeded"]:
        state = state.transition(CampaignStatus.QUEUED_FOR_TOMORROW, error_message="Resend quota exceeded")
        store.update(state)
        log_action(cid, "QUEUED_FOR_TOMORROW", offer["offer_type"], "success", "Resend quota exceeded")
        print("Resend quota exceeded. Stopping. Remaining customers queued for tomorrow.\n")
        return state

    if send_result["any_success"]:
        state = state.transition(CampaignStatus.SENT, send_result=send_result)
        store.update(state)
        log_action(cid, "SENT_WINBACK_OFFER", offer["offer_type"], "success", "")
        print(f"Sent successfully via {plan.channel}\n")
        time.sleep(1)
        return state

    error = ", ".join(send_result["errors"]) or "unknown"
    state = state.transition(CampaignStatus.FAILED, error_message=error, send_result=send_result)
    store.update(state)
    log_action(cid, "SENT_WINBACK_OFFER", offer["offer_type"], "failed", error)
    print(f"Send failed: {error}\n")
    time.sleep(1)
    return state


def _demo_mode(customers: list[dict], store: StateStore):
    """Run in demo mode: generate offers, save HTML files, print summary."""
    original_sheet_id = config.GOOGLE_SHEET_ID
    config.GOOGLE_SHEET_ID = ""
    try:
        customers = fetch_customers(Path(config.CUSTOMERS_CSV_PATH))
    finally:
        config.GOOGLE_SHEET_ID = original_sheet_id

    print(f"\n========== DATABASE REACTIVATION DEMO ==========\n")
    print(f"Found {len(customers)} eligible customer{'s' if len(customers) != 1 else ''}\n")

    for i, customer in enumerate(customers, 1):
        cid = customer["customer_id"]
        print(f"[{i}/{len(customers)}] ", end="")
        _run_campaign(customer, store, demo_mode=True)

    total = len(customers)
    print(f"========== DEMO COMPLETE ==========\n")
    print(f"Total processed: {total}")
    print(f"Emails generated: {total}")
    print(f"Outputs saved to: {DEMO_OUTPUT_DIR}/\n")
    print(f"State summary: {store.summary()}\n")


def _production_send(customers: list[dict], store: StateStore):
    """Run in production mode: generate offers and actually send."""
    total = len(customers)
    sent_count = 0
    failed_count = 0
    queued_count = 0

    print(f"Found {total} eligible customer{'s' if total != 1 else ''}. Starting outreach...\n")

    for customer in customers:
        state = _run_campaign(customer, store, demo_mode=False)

        if state.status == CampaignStatus.SENT:
            sent_count += 1
        elif state.status == CampaignStatus.FAILED:
            failed_count += 1
        elif state.status == CampaignStatus.QUEUED_FOR_TOMORROW:
            queued_count += 1
            # Queue all remaining customers as well
            idx = customers.index(customer)
            for rem_customer in customers[idx + 1:]:
                rem_state = store.get_or_create(rem_customer["customer_id"])
                rem_state = rem_state.transition(
                    CampaignStatus.QUEUED_FOR_TOMORROW,
                    error_message="Resend quota exceeded",
                )
                store.update(rem_state)
                log_action(
                    rem_customer["customer_id"],
                    "QUEUED_FOR_TOMORROW",
                    "discount",
                    "success",
                    "Resend quota exceeded",
                )
                queued_count += 1
            break

    print(f"\n========== WORKFLOW COMPLETE ==========\n")
    print(f"Total eligible: {total}")
    print(f"Successfully sent: {sent_count}")
    print(f"Failed: {failed_count}")
    print(f"Queued for tomorrow: {queued_count}")
    print(f"Log file: {config.SYSTEM_LOG_PATH}")
    print(f"State file: {store.path}")
    print(f"State summary: {store.summary()}")
    print("=" * 42)


def main():
    parser = argparse.ArgumentParser(description="Database Reactivation Workflow")
    parser.add_argument("--demo", action="store_true", help="Demo mode: no API calls, outputs HTML files")
    parser.add_argument("--confirm", action="store_true", help="Required for production sends")
    parser.add_argument(
        "--channel",
        choices=["email", "instagram", "both"],
        default=None,
        help="Override planner channel choice (default: let planner decide)",
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
    parser.add_argument(
        "--state-path",
        default=None,
        help="Override campaign state file path",
    )
    args = parser.parse_args()

    if args.business_type is not None:
        config.BUSINESS_TYPE = args.business_type
    if args.language is not None:
        config.CAMPAIGN_LANGUAGE = args.language

    _print_config_summary()

    if not args.demo and not args.confirm:
        print(
            "ERROR: Production mode requires --confirm flag.\n"
            "       Use --demo to preview without sending.\n"
            "       Use --confirm to actually send emails."
        )
        sys.exit(1)

    store = StateStore(Path(args.state_path) if args.state_path else None)

    customers = fetch_customers()
    if not customers:
        log_action("NONE", "NOT_FOUND", "none", "success", "")
        print("No eligible customers found today.")
        sys.exit(0)

    # Mark all fetched customers in state
    for customer in customers:
        state = store.get_or_create(customer["customer_id"])
        state = state.transition(CampaignStatus.FETCHED)
        store.update(state)

    if args.customer_id is not None:
        matched = [c for c in customers if c["customer_id"] == args.customer_id]
        if not matched:
            print(f"Customer '{args.customer_id}' not found or not eligible.")
            log_action(args.customer_id, "NOT_FOUND", "none", "failed", "customer_id not eligible")
            sys.exit(0)
        customers = matched
        print(f"Processing single customer: {args.customer_id}\n")

    if args.channel:
        # If user overrides channel, force it in the planner by mutating config-like behavior
        # We inject a planner override into each customer record.
        for customer in customers:
            customer["_planner_channel_override"] = args.channel

    if args.demo:
        _demo_mode(customers, store)
    else:
        try:
            config.validate_production_config()
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            print("Cannot proceed with production send. Please set all required environment variables.", file=sys.stderr)
            sys.exit(1)
        _production_send(customers, store)


if __name__ == "__main__":
    main()
