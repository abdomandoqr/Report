#!/usr/bin/env python3
"""Build a single showcase HTML page from demo customer data, state, and emails.

Usage:
    python build_demo_showcase.py
    python build_demo_showcase.py --state-path /tmp/campaign_state.json
"""
import argparse
import csv
import json
import sys
from pathlib import Path


def read_customers(csv_path: Path) -> dict[str, dict[str, str]]:
    """Read customers from CSV and return a dict keyed by customer_id."""
    customers: dict[str, dict[str, str]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers[row["customer_id"]] = row
    return customers


def read_state(state_path: Path) -> dict[str, dict]:
    """Read campaign state JSON and return campaigns dict."""
    if not state_path.exists():
        print(f"ERROR: State file not found: {state_path}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(state_path.read_text(encoding="utf-8"))
    return data.get("campaigns", {})


def find_email_file(email_dir: Path, customer_id: str) -> str:
    """Find the generated email HTML file for a customer."""
    matches = sorted(email_dir.glob(f"{customer_id}_*.html"))
    if not matches:
        print(f"ERROR: No email HTML found for {customer_id} in {email_dir}", file=sys.stderr)
        sys.exit(1)
    return matches[0].name


def format_customer_data(customer: dict[str, str]) -> str:
    """Build an HTML table from customer CSV fields."""
    fields = [
        ("Customer ID", customer.get("customer_id", "")),
        ("Name", customer.get("name", "")),
        ("Email", customer.get("email", "")),
        ("Instagram Handle", customer.get("instagram_handle", "")),
        ("Last Purchase Date", customer.get("last_purchase_date", "")),
        ("Churn Score", customer.get("churn_score", "")),
        ("Preferred Categories", customer.get("preferred_categories", "")),
        ("Last Campaign Date", customer.get("last_campaign_date") or "—"),
        ("Total Purchases", customer.get("total_purchases", "")),
        ("Days Since Last Contact", customer.get("days_since_last_contact", "")),
        ("Unsubscribed", customer.get("unsubscribed", "")),
        ("Business Type", customer.get("business_type", "")),
    ]
    rows = "\n".join(
        f"              <tr><td>{label}</td><td>{value}</td></tr>"
        for label, value in fields
    )
    return f"""
            <table>
              <tbody>
{rows}
              </tbody>
            </table>
"""


def build_showcase(
    customers: dict[str, dict[str, str]],
    campaigns: dict[str, dict],
    email_dir: Path,
    output_path: Path,
) -> None:
    """Compose the showcase HTML page."""
    sections: list[str] = []

    for cid in ["C001", "C002", "C003"]:
        if cid not in customers:
            print(f"WARNING: {cid} not found in customers.csv", file=sys.stderr)
            continue

        customer = customers[cid]
        campaign = campaigns.get(cid, {})
        plan = campaign.get("plan", {})

        email_filename = find_email_file(email_dir, cid)
        data_table = format_customer_data(customer)

        section = f"""
      <section class="customer-section" id="{cid}">
        <h2>Customer {cid} — {customer.get('name', '')}</h2>

        <div class="panel data-panel">
          <h3>📋 Customer Input Data</h3>
          {data_table}
        </div>

        <div class="panel decision-panel">
          <h3>🧠 Planner Decision</h3>
          <p><span class="label">Offer Type:</span> <span class="value">{plan.get('offer_type', 'N/A')}</span></p>
          <p><span class="label">Channel:</span> <span class="value">{plan.get('channel', 'N/A')}</span></p>
          <p><span class="label">Reasoning:</span> <span class="value reasoning">{plan.get('reasoning', 'N/A')}</span></p>
        </div>

        <div class="panel email-panel">
          <h3>📧 Final Generated Email</h3>
          <iframe src="{email_filename}" title="Email for {cid}" loading="lazy"></iframe>
        </div>
      </section>
"""
        sections.append(section)

    divider = '\n      <hr class="section-divider">\n'
    body_sections = divider.join(sections)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Database Reactivation Demo Showcase</title>
  <style>
    * {{ box-sizing: border-box; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
      line-height: 1.6;
      color: #333;
      background: #f5f7fa;
      margin: 0;
      padding: 20px;
    }}

    .container {{
      max-width: 960px;
      margin: 0 auto;
    }}

    header {{
      text-align: center;
      margin-bottom: 40px;
      padding: 30px;
      background: linear-gradient(135deg, #007bff, #0056b3);
      color: white;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}

    header h1 {{ margin: 0 0 10px; font-size: 28px; }}
    header p {{ margin: 0; opacity: 0.95; }}

    .customer-section {{
      background: white;
      border-radius: 12px;
      padding: 30px;
      margin-bottom: 30px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }}

    .customer-section h2 {{
      color: #007bff;
      margin-top: 0;
      margin-bottom: 24px;
      padding-bottom: 12px;
      border-bottom: 3px solid #e9ecef;
      font-size: 24px;
    }}

    .panel {{
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 24px;
    }}

    .panel h3 {{
      margin-top: 0;
      margin-bottom: 16px;
      font-size: 18px;
    }}

    .data-panel {{
      background: #f8f9fa;
      border: 1px solid #e9ecef;
    }}

    .data-panel table {{
      width: 100%;
      border-collapse: collapse;
    }}

    .data-panel td {{
      padding: 10px 12px;
      border-bottom: 1px solid #dee2e6;
      vertical-align: top;
    }}

    .data-panel td:first-child {{
      font-weight: 600;
      color: #495057;
      width: 40%;
    }}

    .decision-panel {{
      background: #fff8e1;
      border: 1px solid #ffecb3;
    }}

    .decision-panel p {{
      margin: 10px 0;
    }}

    .decision-panel .label {{
      font-weight: 700;
      color: #856404;
      display: inline-block;
      min-width: 110px;
    }}

    .decision-panel .value {{
      color: #333;
    }}

    .decision-panel .reasoning {{
      display: block;
      margin-top: 6px;
      line-height: 1.5;
    }}

    .email-panel {{
      background: #f0f0f0;
      border: 1px solid #d0d0d0;
      padding: 20px;
    }}

    .email-panel iframe {{
      width: 100%;
      height: 650px;
      border: none;
      border-radius: 8px;
      background: white;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }}

    .section-divider {{
      border: none;
      height: 4px;
      background: linear-gradient(90deg, transparent, #007bff, transparent);
      margin: 50px 0;
      border-radius: 2px;
    }}

    @media (max-width: 600px) {{
      body {{ padding: 12px; }}
      .customer-section {{ padding: 20px; }}
      .email-panel iframe {{ height: 500px; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Database Reactivation Demo Showcase</h1>
      <p>Three fashion customers · Planner decisions · Generated Arabic emails</p>
    </header>

{body_sections}
  </div>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a single showcase HTML page from demo outputs."
    )
    parser.add_argument(
        "--customers-csv",
        default="data/customers.csv",
        help="Path to customers CSV file (default: data/customers.csv)",
    )
    parser.add_argument(
        "--state-path",
        default="data/campaign_state.json",
        help="Path to campaign state JSON file (default: data/campaign_state.json)",
    )
    parser.add_argument(
        "--email-dir",
        default=".tmp/demo_emails",
        help="Directory containing generated email HTML files (default: .tmp/demo_emails)",
    )
    parser.add_argument(
        "--output",
        default=".tmp/demo_emails/showcase.html",
        help="Output showcase HTML path (default: .tmp/demo_emails/showcase.html)",
    )
    args = parser.parse_args()

    customers = read_customers(Path(args.customers_csv))
    campaigns = read_state(Path(args.state_path))
    email_dir = Path(args.email_dir)
    output_path = Path(args.output)

    build_showcase(customers, campaigns, email_dir, output_path)
    print(f"Showcase created: {output_path.resolve()}")


if __name__ == "__main__":
    main()
