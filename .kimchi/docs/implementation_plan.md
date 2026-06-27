# Database Reactivation Workflow — v1 Implementation Plan

**Target:** Enhance existing `/workspaces/Report` with all 30 answered requirements.
**Date:** 2026-06-19

---

## Chunk 1: Configuration & Project Setup
**Files:** `.env.example`, `requirements.txt`, `config.py`, `tools/prompts/gym.md`, `tools/prompts/dental.md`, `tools/prompts/coaching.md`, `tools/prompts/base.md`
**Complexity:** simple

### Acceptance Criteria
- [ ] `.env.example` contains every tunable variable with comments
- [ ] `requirements.txt` pins exact versions of all packages
- [ ] `config.py` provides a central config loader used by all tools
- [ ] 4 prompt templates exist: base + 3 industry-specific (editable by clients)

### Details
**`.env.example` variables:**
```
ANTHROPIC_API_KEY=
RESEND_API_KEY=
SENDER_EMAIL=
SENDER_NAME=
SENDER_PHYSICAL_ADDRESS=
INSTAGRAM_USERNAME=
INSTAGRAM_PASSWORD=

# Configurable thresholds
CHURN_THRESHOLD_INFO=0.70
CHURN_THRESHOLD_BONUS=0.80
CHURN_THRESHOLD_DISCOUNT=0.90

# Offer settings
DISCOUNT_PCT=25
BUSINESS_TYPE=gym                    # gym | dental | coaching
CAMPAIGN_LANGUAGE=en                 # en | ar

# Google Sheets (optional — falls back to CSV if empty)
GOOGLE_SHEET_ID=
GOOGLE_CREDENTIALS_PATH=credentials.json

# Data paths
CUSTOMERS_CSV_PATH=data/customers.csv
SYSTEM_LOG_PATH=data/system_log.csv
```

**`config.py`:**
- `load_config()` reads `.env` via `python-dotenv`
- Returns a dict with typed values (floats for thresholds, ints for discount)
- Raises clear errors for missing critical vars in production mode

**Prompt templates (`tools/prompts/*.md`):**
- `base.md` — shared structure and JSON format instructions
- `gym.md`, `dental.md`, `coaching.md` — industry-specific context, tone guidance, offer examples
- Templates use Python `str.format()` placeholders

---

## Chunk 2: Data Layer — Enhanced `fetch_customers.py`
**Files:** `tools/fetch_customers.py`
**Complexity:** simple

### Acceptance Criteria
- [ ] Auto-detects CSV vs Google Sheets based on `GOOGLE_SHEET_ID` presence
- [ ] Reads configurable churn thresholds from `config.py`
- [ ] Filters out customers with `unsubscribed = yes`
- [ ] Double-guard duplicate prevention: `last_campaign_date` AND `system_log.csv`
- [ ] Falls back to computed churn score if `churn_score` column is missing/empty
- [ ] Returns identical dict structure regardless of data source

### Details
**Churn score fallback:**
If `churn_score` missing, compute a heuristic:
```python
def compute_churn_score(days_since_contact, total_purchases, days_since_purchase):
    recency = min(days_since_contact / 180, 1.0)
    frequency = max(1 - (total_purchases / 50), 0.0)
    return round((recency * 0.7 + frequency * 0.3), 2)
```

**Duplicate guard:**
1. Check `last_campaign_date` in data source (> 30 days)
2. Check `system_log.csv` for `SENT_WINBACK_OFFER` with same `customer_id` within last 30 days

**Google Sheets integration:**
- Use `gspread` + service-account OAuth
- Read from worksheet named `Customer Data`
- Expected columns include: `unsubscribed` (yes/no)

---

## Chunk 3: AI Message Generation — Enhanced `generate_offer.py`
**Files:** `tools/generate_offer.py`
**Complexity:** simple

### Acceptance Criteria
- [ ] Loads per-business-type prompt template from `tools/prompts/`
- [ ] Uses Haiku for informational tier, Sonnet for bonus/discount tiers
- [ ] Retries Claude call once on invalid JSON before returning None
- [ ] Injects `business_type`, `language`, `discount_pct` into prompt
- [ ] Returns None + logs reason if retry also fails

### Details
**Model selection:**
- informational → `claude-haiku-4-5`
- bonus_points, discount → `claude-sonnet-4-6`

**Retry logic:**
```python
for attempt in range(2):
    try:
        offer = _call_claude(...)
        return offer
    except (json.JSONDecodeError, ValueError):
        if attempt == 0:
            continue
        return None
```

**Language handling:**
- If `language == 'ar'`, add instruction to the prompt: "Write the email in Modern Standard Arabic. Use a warm, friendly tone."
- If `language == 'en'`, default English.

**Discount injection:**
- Replace `25%` in prompt with `{discount_pct}%` from config.

---

## Chunk 4: Email Delivery — Enhanced `send_email.py`
**Files:** `tools/send_email.py`
**Complexity:** simple

### Acceptance Criteria
- [ ] Pluggable provider: `ResendSender` class, abstract `EmailSender` base
- [ ] Generates proper HTML email with RTL support when `language == 'ar'`
- [ ] Adds `List-Unsubscribe` header + physical address footer
- [ ] Catches Resend quota-exceeded (429) and returns special error code
- [ ] Dry-run mode produces nice preview in console

### Details
**HTML structure:**
```html
<!DOCTYPE html>
<html dir="{dir}" lang="{lang}">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
    .cta {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; }}
    .footer {{ font-size: 12px; color: #888; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }}
  </style>
</head>
<body>
  <p>{offer_details (with newlines→<br>)}</p>
  <p><a href="#" class="cta">{cta_text}</a></p>
  <div class="footer">
    {physical_address}<br>
    <a href="mailto:unsubscribe@{domain}">Unsubscribe</a>
  </div>
</body>
</html>
```

**RTL support:** When `language == 'ar'`, set `<html dir="rtl" lang="ar">` and use an Arabic-friendly font stack.

**Quota detection:**
- Catch Resend 429 errors
- Return `{"success": False, "error": "QUOTA_EXCEEDED", "quota_exceeded": True}`

---

## Chunk 5: Main Orchestrator & Demo Mode
**Files:** `main.py`
**Complexity:** simple

### Acceptance Criteria
- [ ] `--demo` flag: runs with CSV, generates HTML files in `.tmp/demo_emails/`, no API calls
- [ ] `--confirm` flag required for production sends (refuses otherwise)
- [ ] `--business-type` and `--language` CLI args override `.env`
- [ ] Instagram DM fallback when email missing/invalid
- [ ] On quota exceeded: stop loop, log remaining customers as `QUEUED_FOR_TOMORROW`
- [ ] Console summary at end: sent count, failed count, queued count, path to outputs

### Details
**Demo mode flow:**
```
1. Read CSV (never Sheets)
2. Filter customers
3. For each: generate offer using mock (no API calls)
4. Save as `.tmp/demo_emails/{customer_id}_{offer_type}.html`
5. Print nice console preview
6. Log to `data/system_log.csv`
```

**Production safety:**
```python
if not args.demo and not args.confirm:
    print("WARNING: Production mode requires --confirm flag. Use --demo to preview.")
    sys.exit(1)
```

**Instagram fallback:**
```python
if not email or email_invalid:
    if instagram_handle:
        result = send_instagram_dm(instagram_handle, offer)
```

**Quota stop:**
```python
if result.get("quota_exceeded"):
    for remaining in customers[i+1:]:
        log_action(remaining["customer_id"], "QUEUED_FOR_TOMORROW", offer_type, "success", "Resend quota exceeded")
    break
```

---

## Chunk 6: GitHub Actions + Docs
**Files:** `.github/workflows/daily_reactivation.yml`, `README.md`, `docs/google_sheets_template.md`
**Complexity:** simple

### Acceptance Criteria
- [ ] GitHub Actions workflow runs at 9:00 AM UTC daily
- [ ] README has setup, demo, and production instructions
- [ ] Google Sheets template instructions documented

### Details
**GitHub Actions:**
```yaml
name: Daily Database Reactivation
on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:
jobs:
  reactivate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: python main.py --confirm
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          ...
```

---

## Chunk 7: Review
**Reviewer:** Standard-tier Reviewer
**Scope:** All files changed/created in Chunks 1–6
**Checklist:**
- [ ] All acceptance criteria from each chunk are met
- [ ] `--demo` runs end-to-end without API keys
- [ ] `--confirm` is required for production mode
- [ ] Code handles missing `.env` gracefully (dry-run)
- [ ] No hardcoded secrets
- [ ] `requirements.txt` is complete
- [ ] No regression: existing dry-run behavior preserved
