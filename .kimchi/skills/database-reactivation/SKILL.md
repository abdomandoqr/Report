---
name: database-reactivation
description: Use when re-engaging dormant customers via automated winback campaigns using Email and Instagram DM channels, AI-generated personalized offers, and CSV-based customer data, including dummy data for safe testing
---

# Database Reactivation

## Overview

Re-engage dormant customers with AI-generated personalized messages sent through Email (Resend) and Instagram DM. This 4-step deterministic Python workflow filters eligible contacts, generates tailored offers via Claude AI, sends messages through the chosen channel, and logs every action.

## When to Use

- Customer base has gone silent (90+ days since last contact)
- Churn score indicates high risk (> 0.7)
- Need to run recovery campaigns with personalized messaging
- Want to test campaigns safely with dummy data before real deployment
- Using Python tools in the WAT framework (workflows, agents, tools)

**When NOT to use:**
- Real-time messaging or live chat
- Single-message bulk blasts without personalization
- Non-English audiences (prompt is English-focused)
- GDPR-sensitive regions without consent verification

## Core Pattern (4-Step Flow)

```python
customers = fetch_customers()          # Step 1: Read + filter CSV

if not customers:
    log_action("NONE", "NOT_FOUND", "none", "success", "")
    print("No eligible customers. Done.")
    exit()

for customer in customers:
    offer = generate_offer(customer)   # Step 2: AI-generated message

    if offer is None:
        log_action(customer["customer_id"], "FAILED_GENERATION", "none", "failed", "Invalid JSON from AI")
        continue

    result = send_message(customer, offer)  # Step 3: Email OR Instagram DM

    status = "success" if result["success"] else "failed"
    log_action(customer["customer_id"], "SENT_WINBACK_OFFER", offer["offer_type"], status, result.get("error", ""))
    time.sleep(1)
```

## Quick Reference

| Step | Tool | Input | Output | Failure Action |
|------|------|-------|--------|----------------|
| 1 | `fetch_customers.py` | `data/customers.csv` | List of eligible customers | Log `NOT_FOUND`, exit |
| 2 | `generate_offer.py` | Customer object + Claude API | JSON with offer details | Log `FAILED_GENERATION`, skip |
| 3 | `send_email.py` | Email + offer JSON + Resend API | Send result | Log `failed`, continue |
| 3b | `send_instagram_dm.py` | IG handle + offer JSON + Instagrapi | Send result | Log `failed`, continue |
| 4 | `log_action.py` | Action result | `data/system_log.csv` append | Always succeeds |

## Prerequisites

```bash
pip install anthropic resend python-dotenv pandas
```

For Instagram DM channel, also:
```bash
pip install instagrapi
```

**Environment variables** (`.env`):
```
ANTHROPIC_API_KEY=sk-ant-...
RESEND_API_KEY=re_...
SENDER_EMAIL=you@yourdomain.com
INSTAGRAM_USERNAME=your_brand_account
INSTAGRAM_PASSWORD=your_brand_password
```

## Execution Steps

### Step 1 — Fetch and Filter Eligible Customers

**Tool:** `tools/fetch_customers.py`

**Logic:**
- Read `data/customers.csv`
- Filter where ALL are true:
  - `churn_score > 0.7`
  - `last_campaign_date` is empty OR > 30 days ago
  - `days_since_last_contact > 90`

**Output:** List of customer dicts

**Edge case — no eligible customers:**
- Print: `"No eligible customers found. Logging NOT_FOUND and stopping."`
- Log one row with `action_taken = NOT_FOUND`
- Exit cleanly

### Step 2 — Generate Personalized Offer

**Tool:** `tools/generate_offer.py`

**Offer type by churn score:**

| Score Range | Offer Type | Description |
|-------------|------------|-------------|
| 0.70 – 0.79 | `informational` | New products in preferred categories |
| 0.80 – 0.89 | `bonus_points` | Reward points on next purchase |
| 0.90 – 1.00 | `discount` | 20–30% direct discount with urgency |

**Claude prompt structure:**
```text
You are a specialist in writing customer re-engagement emails.
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
- discount: offer a direct 25% discount with urgency

Rules:
- Start with their name
- Mention how long it has been since their last visit
- Keep tone warm, never pushy
- 3-4 short paragraphs
- End with a clear call to action

Return ONLY valid JSON, no extra text, in this exact format:
{
  "offer_type": "informational|bonus_points|discount",
  "offer_title": "email subject line here",
  "offer_details": "full email body here",
  "cta_text": "call to action button text"
}
```

**Edge case — invalid JSON from Claude:**
- Log `"AI returned invalid JSON for customer {customer_id}"`
- Set status = `failed`
- Skip to next customer

### Step 3a — Send Email (Resend)

**Tool:** `tools/send_email.py`

```python
import resend
resend.api_key = os.getenv("RESEND_API_KEY")

resend.Emails.send({
    "from": os.getenv("SENDER_EMAIL"),
    "to": customer_email,
    "subject": offer_title,
    "html": f"<p>{offer_details}</p>"
})
```

**Safety rule:** During development, set `to` to your own email first.

### Step 3b — Send Instagram DM (Instagrapi)

**Tool:** `tools/send_instagram_dm.py`

```python
from instagrapi import Client

cl = Client()
cl.login(os.getenv("INSTAGRAM_USERNAME"), os.getenv("INSTAGRAM_PASSWORD"))

cl.direct_send(
    text=f"{offer_title}\n\n{offer_details}\n\n{cta_text}",
    user_ids=[cl.user_id_from_username(customer_ig_handle)]
)
```

**Required column:** Add `instagram_handle` to `customers.csv`

**Safety rule:** Test with a dummy account first. Instagram has aggressive rate limits.

### Step 4 — Log Every Action

**Tool:** `tools/log_action.py`

Appends to `data/system_log.csv`:
```csv
timestamp, customer_id, action_taken, offer_type, status, error_message
```

Creates file with headers if missing.

## Dummy Data for Safe Testing

Use the included `dummy_customers.csv` in this skill directory (copy to `data/customers.csv`) to test without touching real customers:

```csv
customer_id,name,email,instagram_handle,last_purchase_date,churn_score,preferred_categories,last_campaign_date,total_purchases,days_since_last_contact
C001,Ahmed Hassan,ahmed@example.com,ahmed_hassan_ig,2024-09-01,0.85,"Electronics,Books",,15,120
C002,Sara Ali,sara@example.com,sara_ali_official,2024-07-15,0.92,"Fashion,Sports",,8,180
C003,Mohamed Kamal,mo@example.com,mo_kamal,2024-10-01,0.65,"Home,Garden",,22,45
C004,Nour Ibrahim,nour@example.com,nour_styles,2024-06-01,0.91,"Electronics",,5,200
C005,Layla Ahmed,layla@example.com,layla_beauty,2024-08-20,0.78,"Fashion,Beauty",,12,95
```

**Test checklist with dummy data:**
1. Run `fetch_customers.py` → should return C001, C002, C004, C005 (C003 excluded: churn_score 0.65)
2. Run `generate_offer.py` with C002 (score 0.92) → should return `discount` offer
3. Run `send_email.py` with your own email → verify format and tone
4. Run `send_instagram_dm.py` with a test IG account → verify DM delivery
5. Check `data/system_log.csv` → one row per action, all tracked

## Common Mistakes

| Mistake | Why It Breaks | Fix |
|---------|---------------|-----|
| Sending to real customers on first run | Unverified copy/format can damage brand | Always use dummy data + your own email first |
| Missing `last_campaign_date` column header | CSV parse fails or filter malfunctions | Ensure exact column names, case-sensitive |
| Hardcoding API keys in scripts | Security risk, harder to rotate | Always use `.env` + `python-dotenv` |
| No sleep between sends | Rate limit hits on Resend or Instagram | Keep `time.sleep(1)` minimum |
| Forgetting to verify sender email in Resend | Emails bounce silently | Confirm verification in Resend dashboard |
| Using personal Instagram for DM blasts | Account ban risk, no brand continuity | Use dedicated brand account |
| Claude returns markdown in JSON | JSONDecodeError on parse | Add explicit "Return ONLY valid JSON" instruction |

## Failure Recovery

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| AI returns bad JSON | Prompt ambiguity | Make JSON instruction more explicit; add example |
| Resend rejects email | Unverified sender | Check Resend dashboard → verify domain/email |
| CSV column not found | Case sensitivity or spacing | Match schema exactly, trim whitespace |
| Rate limit on Claude API | Too many rapid calls | Increase `time.sleep(2)` between API calls |
| No customers pass filter | Threshold too strict | Temporarily lower to `churn_score > 0.5` for testing |
| Instagram login blocked | Suspicious activity detection | Use session file; log in manually first from same IP |
| Instagram DM not delivered | Wrong username or private account | Verify handle exists and accepts DMs |

## Lessons Learned

Update this section every time something breaks and gets fixed:

- [ ] Initial deployment notes

## Upgrade Path

**Phase 2:** Replace CSV with Google Sheets (`gspread` + `credentials.json`)
**Phase 3:** Add cron job or deploy to Railway/Render for automation
**Phase 4:** Add SMS channel (Twilio) alongside Email and Instagram DM
