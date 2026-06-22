# Workflow: Database Reactivation

## Objective
Re-engage dormant customers by sending personalized AI-generated emails based on each customer's history. Run this daily to recover revenue from contacts who have gone silent.

## Current Version
- **Data source:** CSV file (local) — upgrade to Google Sheets when first real client is onboarded
- **Email provider:** Resend API (simple, no OAuth needed)
- **AI provider:** Anthropic Claude API (claude-sonnet-4-6)
- **Scheduling:** Run manually for now — add cron job after v1 is confirmed working

---

## Required Inputs

Before running this workflow, confirm the following exist:

| Input | Location | Notes |
|-------|----------|-------|
| Customer CSV | `data/customers.csv` | See schema below |
| Resend API key | `.env` → `RESEND_API_KEY` | Get from resend.com |
| Anthropic API key | `.env` → `ANTHROPIC_API_KEY` | Get from console.anthropic.com |
| Sender email | `.env` → `SENDER_EMAIL` | Must be verified in Resend |
| Log file | `data/system_log.csv` | Auto-created on first run |

---

## Data Schema

### customers.csv (input)
```
customer_id, name, email, last_purchase_date, churn_score, preferred_categories, last_campaign_date, total_purchases, days_since_last_contact
C001, Ahmed Hassan, ahmed@example.com, 2024-09-01, 0.85, "Electronics,Books", , 15, 120
C002, Sara Ali, sara@example.com, 2024-07-15, 0.92, "Fashion,Sports", , 8, 180
C003, Mohamed Kamal, mo@example.com, 2024-10-01, 0.65, "Home,Garden", , 22, 45
C004, Nour Ibrahim, nour@example.com, 2024-06-01, 0.91, "Electronics", , 5, 200
C005, Layla Ahmed, layla@example.com, 2024-08-20, 0.78, "Fashion,Beauty", , 12, 95
```

### system_log.csv (output — auto-created)
```
timestamp, customer_id, action_taken, offer_type, status, error_message
```

---

## Tools Required (in execution order)

```
tools/
├── fetch_customers.py       # Step 1: Read and filter CSV
├── generate_offer.py        # Step 2: Call Claude API for personalized message
├── send_email.py            # Step 3: Send via Resend API
└── log_action.py            # Step 4: Write result to system_log.csv
```

If any of these do not exist in `tools/`, create them before running.

---

## Execution Steps

### Step 1 — Fetch and filter eligible customers
**Tool:** `tools/fetch_customers.py`

**What it does:**
- Reads `data/customers.csv`
- Filters rows where ALL three conditions are true:
  - `churn_score > 0.7`
  - `last_campaign_date` is empty OR more than 30 days ago
  - `days_since_last_contact > 90`
- Returns a list of eligible customer objects

**Expected output:**
```python
[
  {
    "customer_id": "C001",
    "name": "Ahmed Hassan",
    "email": "ahmed@example.com",
    "churn_score": 0.85,
    "preferred_categories": "Electronics,Books",
    "last_purchase_date": "2024-09-01",
    "total_purchases": 15,
    "days_since_last_contact": 120
  },
  ...
]
```

**Edge case — no eligible customers:**
- Print: `"No eligible customers found. Logging NOT_FOUND and stopping."`
- Write one row to `system_log.csv` with `action_taken = NOT_FOUND`
- Exit cleanly (no error)

---

### Step 2 — Generate personalized offer for each customer
**Tool:** `tools/generate_offer.py`

**What it does:**
- Receives one customer object at a time
- Determines offer type based on churn score:
  - `0.70 – 0.79` → `informational` (new products in their categories)
  - `0.80 – 0.89` → `bonus_points` (earn points on next purchase)
  - `0.90 – 1.00` → `discount` (direct % discount, 20–30%)
- Calls Claude API with a structured prompt
- Returns a JSON object with the email content

**Prompt to send to Claude:**
```
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

**Expected output:**
```json
{
  "offer_type": "bonus_points",
  "offer_title": "Ahmed, we have a reward waiting for you",
  "offer_details": "Hi Ahmed,\n\nIt's been a while since we last saw you...",
  "cta_text": "Claim Your Reward Points"
}
```

**Edge case — Claude returns invalid JSON:**
- Log error: `"AI returned invalid JSON for customer {customer_id}"`
- Set status = `failed` in log
- Skip to next customer, do not crash

---

### Step 3 — Send the email
**Tool:** `tools/send_email.py`

**What it does:**
- Receives customer email + offer JSON from Step 2
- Sends email via Resend API:
  - `to` → customer email
  - `subject` → `offer_title`
  - `html` → `offer_details` (wrap in basic HTML if plain text)
  - `from` → `SENDER_EMAIL` from `.env`

**Resend API call structure:**
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

**Edge case — send fails:**
- Catch the exception
- Log status = `failed` + error message
- Continue to next customer

**Important — during development:**
- Set `to` to your own email first
- Confirm the email looks correct before pointing at real customers

---

### Step 4 — Log the action
**Tool:** `tools/log_action.py`

**What it does:**
- Appends one row to `data/system_log.csv` after every action (success or failure)
- Creates the file with headers if it does not exist

**Row structure:**
```
timestamp, customer_id, action_taken, offer_type, status, error_message
2025-01-15 09:00:12, C001, SENT_WINBACK_OFFER, bonus_points, success,
2025-01-15 09:00:15, C002, SENT_WINBACK_OFFER, discount, failed, Resend timeout
2025-01-15 09:00:15, NONE, NOT_FOUND, none, success,
```

---

## Full Execution Flow

```python
# Main orchestration logic (Claude Code handles this)

customers = fetch_customers()          # Step 1

if not customers:
    log_action("NONE", "NOT_FOUND", "none", "success", "")
    print("No eligible customers. Done.")
    exit()

for customer in customers:
    offer = generate_offer(customer)   # Step 2

    if offer is None:
        log_action(customer["customer_id"], "FAILED_GENERATION", "none", "failed", "Invalid JSON from AI")
        continue

    result = send_email(customer["email"], offer)   # Step 3

    if result["success"]:
        log_action(customer["customer_id"], "SENT_WINBACK_OFFER", offer["offer_type"], "success", "")
    else:
        log_action(customer["customer_id"], "SENT_WINBACK_OFFER", offer["offer_type"], "failed", result["error"])

    time.sleep(1)   # 1 second between sends to avoid rate limits

print("Done. Check data/system_log.csv for results.")
```

---

## .env File Structure

```
ANTHROPIC_API_KEY=sk-ant-...
RESEND_API_KEY=re_...
SENDER_EMAIL=you@yourdomain.com
```

Never put real keys in any other file. Never commit `.env` to git.

---

## Required Python Packages

```
anthropic
resend
python-dotenv
pandas
```

Install with:
```bash
pip install anthropic resend python-dotenv pandas
```

---

## How to Run (v1 — Manual)

```bash
# 1. Make sure .env is filled in
# 2. Make sure data/customers.csv exists with real or test data
# 3. Run:
python tools/fetch_customers.py      # Test Step 1 alone first
python tools/generate_offer.py       # Test Step 2 alone with one customer
python tools/send_email.py           # Test Step 3 with your own email
# 4. When all three work individually, run the full workflow:
python main.py
```

---

## Failure Recovery

| What broke | What to do |
|------------|------------|
| AI returns bad JSON | Check prompt in `generate_offer.py`, make JSON instruction more explicit |
| Resend rejects email | Verify sender email is confirmed in Resend dashboard |
| CSV column not found | Check column names match schema exactly (case-sensitive) |
| Rate limit on Claude API | Add `time.sleep(2)` between API calls instead of 1 |
| No customers pass filter | Lower thresholds temporarily to test: `churn_score > 0.5` |

When you fix a failure, document what you learned here in this section.

---

## Lessons Learned
*(Update this section every time something breaks and gets fixed)*

- [ ] First run notes go here

---

## Upgrade Path — After v1 Works

**Phase 2: Replace CSV with Google Sheets**
- Add `gspread` package
- Update `fetch_customers.py` to read from Sheets
- Add `credentials.json` for Google OAuth
- Update `log_action.py` to append to Sheets instead of CSV

**Phase 3: Automate scheduling**
- Add a cron job (Linux/Mac) or Task Scheduler (Windows)
- Or deploy to a free cloud service (Railway, Render)

**Phase 4: Add SMS**
- Integrate Twilio alongside Resend
- Add `phone` column to customer schema

---

## Quick Reference

```
Data in:     data/customers.csv
Data out:    data/system_log.csv
Filter:      churn_score > 0.7 + no recent campaign + 90+ days silent
AI:          Claude API → JSON offer (3 types: info / points / discount)
Email:       Resend API → subject + body → customer inbox
Log:         Every action recorded whether success or failure
Test first:  Send to your own email before real customers
```
