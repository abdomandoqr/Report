#!/usr/bin/env python3
"""Build a fully self-contained showcase HTML file with inlined emails.

All email HTML and CSS is embedded directly. CSS is sandboxed per customer
by prefixing class names and scoping every selector under a unique wrapper
class, so emails render correctly without iframe conflicts.

Usage:
    python build_showcase_standalone.py
    python build_showcase_standalone.py --state-path /tmp/campaign_state.json
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path


def read_customers(csv_path: Path) -> dict[str, dict[str, str]]:
    customers: dict[str, dict[str, str]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers[row["customer_id"]] = row
    return customers


def read_state(state_path: Path) -> dict[str, dict]:
    if not state_path.exists():
        print(f"ERROR: State file not found: {state_path}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(state_path.read_text(encoding="utf-8"))
    return data.get("campaigns", {})


def find_email_file(email_dir: Path, customer_id: str) -> Path:
    matches = sorted(email_dir.glob(f"{customer_id}_*.html"))
    if not matches:
        print(f"ERROR: No email HTML found for {customer_id} in {email_dir}", file=sys.stderr)
        sys.exit(1)
    return matches[0]


def extract_email_parts(email_html: str) -> tuple[str, str, str, str]:
    """Extract body HTML, CSS, text direction, and language from an email HTML."""
    html_match = re.search(r"<html\s+([^>]*)>", email_html, re.IGNORECASE)
    html_attrs = html_match.group(1) if html_match else ""

    dir_match = re.search(r'dir=["\']([^"\']+)["\']', html_attrs, re.IGNORECASE)
    lang_match = re.search(r'lang=["\']([^"\']+)["\']', html_attrs, re.IGNORECASE)
    direction = dir_match.group(1) if dir_match else "ltr"
    language = lang_match.group(1) if lang_match else "en"

    body_match = re.search(r"<body[^>]*>(.*?)</body>", email_html, re.DOTALL | re.IGNORECASE)
    body_html = body_match.group(1).strip() if body_match else email_html

    style_match = re.search(r"<style[^>]*>(.*?)</style>", email_html, re.DOTALL | re.IGNORECASE)
    css = style_match.group(1).strip() if style_match else ""

    return body_html, css, direction, language


def prefix_html_classes(html: str, prefix: str) -> str:
    """Add prefix to every class attribute value."""
    def repl(match):
        quote = match.group(1)
        classes = match.group(2).split()
        new_classes = " ".join(f"{prefix}{c}" for c in classes)
        return f"class={quote}{new_classes}{quote}"
    return re.sub(r'class=(["\'])(.*?)\1', repl, html)


def prefix_css_class_selectors(css: str, prefix: str) -> str:
    """Add prefix to every CSS class selector."""
    return re.sub(r"\.([a-zA-Z_-][a-zA-Z0-9_-]*)", lambda m: f".{prefix}{m.group(1)}", css)


def scope_css(css: str, sandbox_selector: str) -> str:
    """Scope every selector under the sandbox selector; replace body with sandbox."""
    def process_block(block: str) -> str:
        block = block.strip()
        if not block:
            return ""

        # Handle @media and other at-rules with a block
        at_match = re.match(r"(@[a-z-]+\s+[^{]+)\{(.+)\}\s*$", block, re.DOTALL | re.IGNORECASE)
        if at_match:
            header = at_match.group(1).strip()
            inner = at_match.group(2)
            return f"{header} {{\n{process_rules(inner)}\n}}"

        return process_rules(block)

    def process_rules(rules_text: str) -> str:
        rules = []
        depth = 0
        current = []
        for char in rules_text:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            current.append(char)
            if depth == 0 and char == "}":
                rules.append("".join(current).strip())
                current = []
        if current:
            rules.append("".join(current).strip())

        out = []
        for rule in rules:
            rule = rule.strip()
            if not rule:
                continue
            m = re.match(r"([^{]+)\{(.*)\}\s*$", rule, re.DOTALL)
            if not m:
                out.append(rule)
                continue

            selectors_part = m.group(1).strip()
            body_part = m.group(2).strip()
            selectors = [s.strip() for s in selectors_part.split(",")]
            new_selectors = []
            for sel in selectors:
                if sel.lower() == "body":
                    new_selectors.append(sandbox_selector)
                else:
                    new_selectors.append(f"{sandbox_selector} {sel}")
            new_selectors_part = ",\n".join(new_selectors)
            out.append(f"{new_selectors_part} {{\n  {body_part}\n}}")
        return "\n\n".join(out)

    return process_block(css)


def build_email_section(
    cid: str,
    customer: dict[str, str],
    campaign: dict,
    email_dir: Path,
) -> str:
    plan = campaign.get("plan", {})
    email_path = find_email_file(email_dir, cid)
    email_html = email_path.read_text(encoding="utf-8")

    body_html, css, direction, language = extract_email_parts(email_html)

    prefix = f"e{cid}-"
    sandbox_class = f"email-sandbox-{cid}"
    sandbox_selector = f".{sandbox_class}"

    body_html_prefixed = prefix_html_classes(body_html, prefix)
    css_prefixed = prefix_css_class_selectors(css, prefix)
    css_scoped = scope_css(css_prefixed, sandbox_selector)

    sandbox_attrs = f'class="{sandbox_class}" dir="{direction}" lang="{language}"'

    return f"""
      <section class="customer-section" id="{cid}">
        <h2>Customer {cid} — {customer.get('name', '')}</h2>

        <div class="panel data-panel">
          <h3>📋 Customer Input Data</h3>
          <table>
            <tbody>
              <tr><td>Customer ID</td><td>{customer.get('customer_id', '')}</td></tr>
              <tr><td>Name</td><td>{customer.get('name', '')}</td></tr>
              <tr><td>Email</td><td>{customer.get('email', '')}</td></tr>
              <tr><td>Instagram Handle</td><td>{customer.get('instagram_handle', '')}</td></tr>
              <tr><td>Last Purchase Date</td><td>{customer.get('last_purchase_date', '')}</td></tr>
              <tr><td>Churn Score</td><td>{customer.get('churn_score', '')}</td></tr>
              <tr><td>Preferred Categories</td><td>{customer.get('preferred_categories', '')}</td></tr>
              <tr><td>Last Campaign Date</td><td>{customer.get('last_campaign_date') or '—'}</td></tr>
              <tr><td>Total Purchases</td><td>{customer.get('total_purchases', '')}</td></tr>
              <tr><td>Days Since Last Contact</td><td>{customer.get('days_since_last_contact', '')}</td></tr>
              <tr><td>Unsubscribed</td><td>{customer.get('unsubscribed', '')}</td></tr>
              <tr><td>Business Type</td><td>{customer.get('business_type', '')}</td></tr>
            </tbody>
          </table>
        </div>

        <div class="panel decision-panel">
          <h3>🧠 Planner Decision</h3>
          <p><span class="label">Offer Type:</span> <span class="value">{plan.get('offer_type', 'N/A')}</span></p>
          <p><span class="label">Channel:</span> <span class="value">{plan.get('channel', 'N/A')}</span></p>
          <p><span class="label">Reasoning:</span> <span class="value reasoning">{plan.get('reasoning', 'N/A')}</span></p>
        </div>

        <div class="panel email-panel">
          <h3>📧 Final Generated Email</h3>
          <style>
{css_scoped}
          </style>
          <div {sandbox_attrs}>
{body_html_prefixed}
          </div>
        </div>
      </section>
"""


def build_showcase(
    customers: dict[str, dict[str, str]],
    campaigns: dict[str, dict],
    email_dir: Path,
    output_path: Path,
) -> None:
    sections: list[str] = []
    for cid in ["C001", "C002", "C003"]:
        if cid not in customers:
            print(f"WARNING: {cid} not found in customers.csv", file=sys.stderr)
            continue
        sections.append(build_email_section(cid, customers[cid], campaigns.get(cid, {}), email_dir))

    sections_html = '\n      <hr class="section-divider">\n'.join(sections)

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
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Database Reactivation Demo Showcase</h1>
      <p>Three fashion customers · Planner decisions · Generated Arabic emails</p>
    </header>

{sections_html}
  </div>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a fully self-contained showcase HTML file."
    )
    parser.add_argument("--customers-csv", default="data/customers.csv")
    parser.add_argument("--state-path", default="/tmp/campaign_state.json")
    parser.add_argument("--email-dir", default=".tmp/demo_emails")
    parser.add_argument("--output", default=".tmp/demo_emails/showcase_standalone.html")
    args = parser.parse_args()

    customers = read_customers(Path(args.customers_csv))
    campaigns = read_state(Path(args.state_path))
    email_dir = Path(args.email_dir)
    output_path = Path(args.output)

    build_showcase(customers, campaigns, email_dir, output_path)
    print(f"Created: {output_path.resolve()}")


if __name__ == "__main__":
    main()
