# Product Requirements Document: Database Reactivation Workflow

## 1. Executive Summary

The Database Reactivation Workflow is a Python-based automation system that identifies dormant customers in a business's contact database, generates personalized AI-driven reactivation messages, and sends them via email — all on a daily schedule. It serves two purposes: (1) a **sellable product** delivered to SMB clients (gyms, dental clinics, coaching businesses with 4,000+ inactive leads), and (2) a **demo mode** that proves the concept to potential clients before they buy.

The core value proposition is simple: businesses already have a database of contacts who know them. Reactivating dormant customers is far cheaper and more effective than acquiring new ones. Industry benchmarks suggest 2–3% conversion is achievable for win-back campaigns, though actual results depend on list quality, offer relevance, and deliverability — this should be validated with each client's first campaign rather than promised upfront.

**MVP Goal:** Deliver a production-ready v1 that runs end-to-end — from scheduled trigger through AI-generated personalized emails to delivery and logging — with a fully functional demo mode for client presentations, all deployable via GitHub Actions or local execution.

---

## 2. Mission

**Mission Statement:** Help small and medium businesses recover dormant customers by making personal, AI-powered re-engagement accessible, affordable, and automatic — turning forgotten contact lists into new revenue with zero ad spend.

**Core Principles:**

1. **Zero technical barrier for clients** — A gym owner or dentist should be able to run this by filling a Google Sheet and clicking a button. No coding knowledge required.
2. **Personalization at scale** — Every email reads like it was written personally for that customer, not mass-blasted. AI adapts tone, offer, and content to each individual's history, preferences, and churn risk.
3. **Compliance by default** — Every email includes sender identification, a physical address, and an unsubscribe mechanism. The system filters out opted-out customers and maintains 3-year consent records.
4. **Safety first** — Production sends require explicit confirmation. Demo mode never sends real emails. No API keys = automatic dry-run.
5. **Transparent and auditable** — Every action is logged. Clients can see exactly who was contacted, when, with what offer, and whether it succeeded.
6. **Cost transparency** — Clients pay for their own API usage (Resend + Claude). The workflow itself is a one-time setup fee with no recurring SaaS lock-in.

---

## 3. Target Users

### Primary Persona: Gym Owners, Dentists, Coaches (SMB Operators)

- **Who:** Small business owners who have been operating for 2+ years and built up a contact database of 4,000+ leads or past customers who have gone silent.
- **Technical comfort:** Low. They can fill out a Google Sheet, copy-paste an API key, and click "Run." They do not write code.
- **Key needs:**
  - A system that runs automatically every day without their attention
  - Emails that sound personal and warm, not spammy
  - Clear reporting on who was contacted and which offers were sent
  - No risk of accidentally spamming or sending duplicate emails
  - Ability to see the exact output before going live (demo mode)

### Secondary Persona: Marketing Agencies / Freelancers

- **Who:** Freelancers or small agencies who sell marketing automation services to SMBs. They deploy and configure the workflow for multiple clients.
- **Technical comfort:** Medium. They can set up GitHub Actions, configure `.env` files, and troubleshoot API issues.
- **Key needs:**
  - Quick, repeatable deployment per client
  - Industry-specific prompt templates they can customize
  - Clean separation of client data (one Sheet per client)
  - Easy onboarding documentation they can hand to clients

### Tertiary Persona: Developers (Self-Hosters)

- **Who:** Developers who want to fork and extend the workflow for their own use or for resale.
- **Technical comfort:** High. They modify Python code, add new channels, customize prompts.
- **Key needs:**
  - Clean, well-documented codebase
  - Pluggable architecture (swappable email providers, new AI models)
  - Configurable via `.env` without code changes
  - Extensible with new business types and message strategies

> **Note on Instagram DM:** Instagram DM is an **experimental, optional fallback channel** — not a core feature to lead with in client sales pitches. It relies on `instagrapi`, an unofficial library that carries a risk of account suspension. Position email as the primary channel; Instagram DM is only a supplementary reach method when email is missing.

---

## 4. MVP Scope

### In Scope

**Core Functionality:**
- ✅ Daily scheduled execution (GitHub Actions cron at 9:00 AM UTC) + manual trigger
- ✅ Auto-detect data source: Google Sheets (if `GOOGLE_SHEET_ID` set) or CSV fallback
- ✅ Configurable churn score thresholds (0.70 / 0.80 / 0.90 default, editable in `.env`)
- ✅ Filter logic: churn score > threshold AND (no campaign in 30+ days OR no prior campaign) AND 90+ days since last contact
- ✅ Double-guard duplicate prevention: checks `last_campaign_date` in data AND `system_log.csv` for recent sends
- ✅ Unsubscribe filtering: skips customers with `unsubscribed = yes`
- ✅ Heuristic churn score computation if `churn_score` column missing/empty
- ✅ AI-generated personalized emails via Anthropic Claude API
- ✅ Per-business-type prompt templates (gym, dental, coaching) stored as editable markdown files
- ✅ Model selection per offer tier: Haiku (informational), Sonnet (bonus/discount)
- ✅ Retry-once on invalid JSON from AI
- ✅ Configurable discount percentage (default 25%)
- ✅ Multilingual support: English + Arabic, with full RTL HTML when `language=ar`
- ✅ Email delivery via Resend API with HTML generation, inline CSS, CTA button
- ✅ `List-Unsubscribe` header + physical address footer (CAN-SPAM / Egypt PDPL compliance)
- ✅ Quota detection (Resend 429 → stops and queues remaining for tomorrow)
- ✅ Instagram DM fallback when email is missing but `instagram_handle` exists
- ✅ Comprehensive logging to `data/system_log.csv` (or Google Sheets SYSTEM_LOG)
- ✅ Demo mode (`--demo`): no API calls, generates styled HTML preview per customer
- ✅ Production safety (`--confirm` flag required to actually send)
- ✅ CLI overrides: `--business-type`, `--language`, `--customer-id`, `--channel`
- ✅ End-of-run console summary with sent/failed/queued counts

**Technical:**
- ✅ Central `config.py` for all tunable parameters
- ✅ `.env.example` with comprehensive documentation
- ✅ `requirements.txt` with pinned versions
- ✅ Dry-run behavior when API keys are missing (no crashes)
- ✅ Graceful error handling: log failure, skip customer, continue loop
- ✅ Rate limiting: 1-second delay between sends in production, 0.5s in demo
- ✅ GitHub Actions workflow with all secrets and variables

**Documentation:**
- ✅ README.md with setup, demo, production, and troubleshooting
- ✅ Google Sheets template instructions for clients
- ✅ Sample demo data in `data/customers.csv` (gym + dental + coaching examples)

### Out of Scope

- ❌ A/B testing of message variants
- ❌ SMS via Twilio (Phase 2)
- ❌ Open/click tracking pixel
- ❌ Auto-stop if customer replies or purchases
- ❌ Webhook handling for bounces/complaints (Phase 2)
- ❌ Multi-user SaaS dashboard with web UI
- ❌ Client billing / subscription management
- ❌ Custom domain configuration for sender emails
- ❌ Advanced RFM segmentation (beyond simple heuristic fallback)
- ❌ Multi-language beyond English + Arabic
- ❌ Mobile app or web dashboard
- ❌ Admin panel for managing multiple clients
- ❌ PostgreSQL / database backend (uses CSV / Google Sheets)
- ❌ Two-factor authentication

---

## 5. User Stories

### US-1: Demo to a Potential Client
**As a** freelancer selling marketing automation services, **I want to** run `python main.py --demo` and see beautifully formatted preview emails for all three business types, **so that** I can show a gym owner exactly what their reactivation campaign will look like before they commit to buying.
> *Example: Running the demo command generates `.tmp/demo_emails/C001_bonus_points.html` — a styled HTML email with Ahmed's personalized message, CTA button, and footer. The console shows a summary: "4 eligible customers, 4 emails generated."*

### US-2: First Production Run
**As a** dentist who just bought the workflow, **I want to** fill in my `.env` with API keys, prepare my customer Google Sheet, and run `python main.py --confirm`, **so that** dormant patients receive personalized reactivation offers automatically.
> *Example: Dr. Samira runs the command. The workflow reads 4,200 patients from her Sheet, filters 89 eligible ones, generates personalized Arabic emails via Claude, sends them via Resend, and logs every action to the SYSTEM_LOG tab. She checks her Resend dashboard and sees 89 emails sent successfully.*

### US-3: Prevent Duplicate Spam
**As a** gym owner, **I want** the system to automatically skip customers who already received an offer in the last 30 days, **so that** I never accidentally send the same person multiple emails in a short period.
> *Example: The workflow checks both the `created_campaign_date` column AND its own `system_log.csv`. A member who got an email last week is silently skipped. The log shows: `C001 SKIPPED — campaign sent 2025-06-15 (< 30 days ago)` (or equivalent).*

### US-4: Handle High-Risk vs Low-Risk Differently
**As a** business coach, **I want** customers with very high churn scores (0.9+) to receive direct discount offers while medium-risk ones (0.7–0.8) just get an informational update, **so that** I'm not giving away discounts to people who only need a gentle nudge.
> *Example: Coach Omar has a client with churn_score=0.95 → they get "20% exclusive offer just for you." Another client with 0.75 → they get "Here's what's new in our coaching programs." The offer type is logged.*

### US-5: Fallback When Email Is Missing
**As a** gym manager, **I want** the system to try sending an Instagram DM when a member doesn't have an email on file but has an Instagram handle, **so that** I can still reach people even with incomplete contact data.
> *Example: Member Fatima only has `instagram_handle = fatima_fitness`. The workflow skips email, prints "Email missing for C003 — falling back to Instagram DM," sends a DM via `send_instagram_dm.py`, and logs it.*

### US-6: Arabic-Language Campaigns
**As a** dental clinic in Cairo, **I want** all reactivation emails to be written in Modern Standard Arabic with right-to-left text direction, **so that** my patients feel the communication is personal and culturally appropriate.
> *Example: Setting `CAMPAIGN_LANGUAGE=ar` in `.env` triggers RTL HTML (`<html dir="rtl" lang="ar">`) and the AI prompt includes: "Write the email in Modern Standard Arabic." The email renders correctly on mobile and desktop.*

### US-7: Review Before Sending
**As a** cautious business owner, **I want** to run the workflow in demo mode first to preview every generated email, **so that** I can verify the content, tone, and offers before any real emails go out.
> *Example: `python main.py --demo` outputs HTML files. The owner opens them in a browser, sees subject lines, body text, CTA buttons, and the unsubscribe footer. Satisfied, she then runs `python main.py --confirm` for production.*

### US-8: Schedule Without Touching Code
**As a** non-technical gym owner, **I want** the workflow to run every day at 9 AM automatically without me having to run any commands, **so that** I never miss a day of reactivation outreach.
> *Example: The freelancer set up GitHub Actions for the gym's forked repo. Every morning, the workflow runs at 9 AM UTC, checks for eligible members, sends emails, and stops if no one qualifies. The owner only checks the log occasionally.*

---

## 6. Core Architecture & Patterns

### High-Level Architecture

```
[GitHub Actions Trigger: Daily 9 AM UTC + Manual]
            ↓
    [main.py — Orchestrator]
            ↓
    +-------------------+-------------------+
    |                   |                   |
[--demo]           [--confirm]        [--customer-id]
    |                   |                   |
[CSV only]      [CSV or Sheets]     [Single customer]
    |                   |                   |
    ↓                   ↓                   ↓
[tools/fetch_customers.py]          [filter by ID]
    |                   |
    +-------+-----------+
            |
            ↓
[Eligible customers list]
            |
            ↓
[Loop per customer]
    |
    +→ [tools/generate_offer.py] → AI prompt (business_type + language)
    |         |                           |
    |    [Claude Haiku]            [Claude Sonnet]
    |    (informational)           (bonus/discount)
    |         |
    |         ↓
    |    [JSON offer: title, body, CTA]
    |         |
    +←←←←←←←←←+
            |
            ↓
    [Route to channel(s)]
    |        |
    |        +→ [tools/send_email.py] → Resend API
    |        |       |
    |        |   [HTML email]
    |        |   [List-Unsubscribe header]
    |        |   [Physical address footer]
    |        |   [RTL support if ar]
    |        |
    |        +→ [tools/send_instagram_dm.py] → instagrapi
    |                |
    +←←←←←←←←←←←←←←←+
            |
            ↓
    [tools/log_action.py] → data/system_log.csv
            |
            ↓
    [Next customer or stop on quota]
```

### Directory Structure

```
/
├── main.py                          # Orchestrator (CLI args, modes, loop)
├── config.py                        # Central config loader
├── .env.example                     # Template for all environment variables
├── requirements.txt                 # Pinned Python dependencies
├── data/
│   ├── customers.csv                # Or: Google Sheets "Customer Data" tab
│   ├── system_log.csv               # Or: Google Sheets "SYSTEM_LOG" tab
│   └── demo_output/                 # .gitkeep (unused — demo writes to .tmp/)
├── .tmp/
│   └── demo_emails/                 # Demo mode HTML outputs
├── tools/
│   ├── fetch_customers.py           # Data fetcher + filter engine
│   ├── generate_offer.py            # Claude AI prompt + JSON extraction
│   ├── send_email.py                # Resend API integration
│   ├── send_instagram_dm.py         # Instagram DM fallback
│   ├── log_action.py                # CSV / Sheet logging
│   └── prompts/
│       ├── base.md                  # Base prompt template
│       ├── gym.md                   # Fitness center addendum
│       ├── dental.md                # Dental clinic addendum
│       └── coaching.md              # Coaching business addendum
├── docs/
│   └── google_sheets_template.md    # Client onboarding guide
├── .github/workflows/
│   └── daily_reactivation.yml       # GitHub Actions CI/CD
└── README.md                        # Full documentation
```

### Key Design Patterns

1. **Configuration-driven** — All tunable parameters (thresholds, discount, business type, language) live in `.env` and are loaded via `config.py`. No code changes needed to adapt to a new client.
2. **Auto-detection** — The system automatically detects whether to use CSV or Google Sheets based on the presence of `GOOGLE_SHEET_ID`. No manual mode switching.
3. **Dry-run by default** — If API keys are missing, every tool falls back to dry-run mode that previews actions without sending anything. Safe for local development.
4. **Fail-forward** — If one customer fails (invalid JSON, send error, missing email), the loop logs the failure and continues with the next customer. The workflow is never killed by a single bad record.
5. **Pluggable email provider** — `EmailSender` abstract base class with `ResendSender` implementation. Switching to SendGrid or SMTP requires only a new subclass.
6. **Editable prompts as markdown** — Industry-specific prompt context lives in `.md` files that clients or agencies can edit without touching Python code.

---

## 7. Features

### 7.1 Demo Mode

**Trigger:** `python main.py --demo`

The demo mode is designed for client presentations and local testing — it requires zero API keys and produces tangible outputs.

- **No real API calls:** All AI generation uses mock offers. All email sending uses dry-run previews.
- **CSV-only data source:** Ignores Google Sheets config and reads `data/customers.csv` directly.
- **HTML email previews:** For each eligible customer, generates a styled HTML file at `.tmp/demo_emails/{customer_id}_{offer_type}.html` containing:
  - Email subject line (`<h1>`)
  - Fully formatted body with `<br>` line breaks
  - Styled CTA button
  - Footer with unsubscribe link and physical address placeholder
- **RTL support:** When `language=ar`, the HTML uses `dir="rtl"` and an Arabic-friendly font stack.
- **Console summary:** Prints a formatted table showing:
  - Total eligible customers
  - Per-customer: ID, name, business type, offer type, subject
  - Path to each generated HTML file
  - Final counts: total processed, emails generated, output directory
- **Logging:** Writes to `data/system_log.csv` as usual (with `status=demo_mode` or similar)

### 7.2 Production Mode

**Trigger:** `python main.py --confirm` (the `--confirm` flag is mandatory — running without it exits with an error)

The production mode connects to real APIs and sends real emails.

- **Data source auto-detection:** Uses Google Sheets if `GOOGLE_SHEET_ID` is set; otherwise CSV.
- **Eligible customer filtering:** Applies all configured filters (thresholds, unsubscribe, duplicate prevention, days-silent).
- **AI generation:** Calls Claude API with per-business-type prompt templates. Uses Haiku for informational offers, Sonnet for bonus/discount offers.
- **Real email sending:** Sends via Resend API with HTML body, List-Unsubscribe header, and physical address footer.
- **Instagram fallback:** When `--channel email` or `--channel both` is set and a customer has no email, tries Instagram DM if `instagram_handle` exists.
- **Quota handling:** On Resend 429 (quota exceeded), immediately stops the loop and logs all remaining customers as `QUEUED_FOR_TOMORROW`.
- **Rate limiting:** 1-second sleep between sends to avoid rate limits.
- **End-of-run summary:** Prints sent/failed/queued counts and log file path.

### 7.3 Customer Filtering Engine

The filtering logic in `fetch_customers.py` applies all three conditions simultaneously:

```python
eligible = (
    churn_score > CHURN_THRESHOLD_INFO   # e.g., > 0.70
    AND (last_campaign_date is empty OR > 30 days ago)
    AND days_since_last_contact > 90
    AND unsubscribed != "yes"
    AND NOT recently_sent_in_system_log   # within last 30 days
)
```

**Churn score fallback:** If the `churn_score` column is missing or empty, compute:
```python
recency = min(days_since_last_contact / 180, 1.0)
frequency = max(1 - (total_purchases / 50), 0.0)
score = round((recency * 0.7 + frequency * 0.3), 2)
```

**Duplicate prevention (double-guard):**
1. Check `last_campaign_date` in the data source > 30 days ago
2. Check `system_log.csv` for `SENT_WINBACK_OFFER` with matching `customer_id` within last 30 days
Both guards must pass for a customer to be eligible.

### 7.4 Offer Type Logic

Based on configurable thresholds:

| Churn Score Range | Offer Type | Claude Model | What AI Writes |
|---|---|---|---|
| CHURN_THRESHOLD_INFO – CHURN_THRESHOLD_BONUS (e.g., 0.70–0.79) | `informational` | `claude-haiku-4-5` | "Here's what's new in your preferred categories" |
| CHURN_THRESHOLD_BONUS – CHURN_THRESHOLD_DISCOUNT (e.g., 0.80–0.89) | `bonus_points` | `claude-sonnet-4-6` | "Earn rewards on your next visit" |
| CHURN_THRESHOLD_DISCOUNT – 1.00 (e.g., 0.90–1.00) | `discount` | `claude-sonnet-4-6` | "{DISCOUNT_PCT}% exclusive offer just for you" |

### 7.5 AI Message Generation

The prompt assembly in `generate_offer.py` works as follows:

1. Read `tools/prompts/base.md` — contains the shared structure, JSON format rules, and placeholders.
2. Append the industry-specific file (`gym.md`, `dental.md`, or `coaching.md`) for tone and context.
3. Inject customer data: name, churn_score, preferred_categories, last_purchase_date, total_purchases, days_since_last_contact, offer_type, business_type, language, discount_pct.
4. If `language == 'ar'`, append Arabic writing instruction.
5. Call Claude API with the assembled prompt.
6. Extract JSON from response (handles markdown code fences like ```json).
7. **Retry once** on JSON parse failure (re-prompt with same data).
8. Return `None` if both attempts fail — the orchestrator logs the failure and skips the customer.

### 7.6 Email Delivery

The `send_email.py` module generates and sends HTML emails:

**HTML Structure:**
```html
<!DOCTYPE html>
<html dir="{dir}" lang="{lang}">
<head><meta charset="UTF-8">
<style>
  body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
  .cta { display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; }
  .footer { font-size: 12px; color: #888; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
</style>
</head>
<body>
  <p>{offer_details_with_br_tags}</p>
  <p><a href="#" class="cta">{cta_text}</a></p>
  <div class="footer">
    {SENDER_PHYSICAL_ADDRESS}<br>
    <a href="mailto:unsubscribe@{domain}">Unsubscribe</a>
  </div>
</body>
</html>
```

**Headers:**
- `List-Unsubscribe`: `<mailto:unsubscribe@domain.com>`
- `Reply-To`: `SENDER_EMAIL`

**Arabic RTL:**
- `dir="rtl"`, `lang="ar"`
- Font stack: `'Segoe UI', 'Tahoma', 'Arial', sans-serif`

### 7.7 Logging & Reporting

Every action appends a row to `data/system_log.csv`:

```
timestamp, customer_id, action_taken, offer_type, status, error_message
```

**Action types:**
- `SENT_WINBACK_OFFER` — email/DM successfully sent
- `FAILED_GENERATION` — AI returned invalid JSON after retry
- `FAILED_SEND` — email/DM send failed (Resend error, instagrapi error)
- `NOT_FOUND` — no eligible customers today
- `QUEUED_FOR_TOMORROW` — stopped due to quota, queued for next run
- `SKIPPED` — duplicate prevention filtered out (optional, for debugging)

**Reporting for clients:** The log CSV can be opened in Excel / Google Sheets to review campaign history, identify failures, and track conversion.

### 7.8 Instagram DM Fallback

When `--channel email` or `--channel both` is active and a customer has no `email` (or empty/invalid email), the system checks for `instagram_handle`. If present:

1. Print: `"Email missing for {customer_id} — falling back to Instagram DM"`
2. Call `send_instagram_dm(ig_handle, offer)`
3. Track the result alongside the email result
4. The overall success for that customer is `True` if either email or DM succeeds

> **Note:** Instagram DM is an **experimental, optional fallback channel** — not a core feature to lead with in client sales pitches. It relies on `instagrapi`, an unofficial library that carries a risk of account suspension. Use it only as a supplementary reach method when email is missing; do not position it as a primary selling point.

---

## 8. Technology Stack

### Core Framework
| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11+ | Primary language |
| **GitHub Actions** | N/A | Scheduled execution and CI/CD |

### Data Processing
| Technology | Version | Purpose |
|---|---|---|
| **pandas** | 2.2.3 | CSV reading, filtering, datetime handling |
| **gspread** | 6.1.0 | Google Sheets integration (optional) |
| **oauth2client** | 4.1.3 | Google OAuth for Sheets API |

### AI & Email
| Technology | Version | Purpose |
|---|---|---|
| **anthropic** | 0.26.0 | Claude API client |
| **resend** | 3.0.0 | Resend email API |
| **instagrapi** | 2.1.0 | Instagram DM sending (optional) |

### Configuration & Utilities
| Technology | Version | Purpose |
|---|---|---|
| **python-dotenv** | 1.0.1 | `.env` file loading |

### Dev Tooling
| Tool | Purpose |
|---|---|
| Git | Version control |
| GitHub | Hosting, Actions, secrets management |
| GitHub Codespaces | Primary development environment |

---

## 9. Security & Configuration

### Configuration Management

All tunable parameters live in `.env` (loaded via `python-dotenv` into `config.py`):

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
RESEND_API_KEY=re_...

# Sender Configuration
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=Your Business Name
SENDER_PHYSICAL_ADDRESS=123 Main St, Cairo, Egypt

# Instagram (optional)
INSTAGRAM_USERNAME=your_ig_handle
INSTAGRAM_PASSWORD=your_ig_password

# Google Sheets (optional — falls back to CSV if empty)
GOOGLE_SHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_CREDENTIALS_PATH=credentials.json

# Data Paths
CUSTOMERS_CSV_PATH=data/customers.csv
SYSTEM_LOG_PATH=data/system_log.csv

# Business & Campaign Settings
BUSINESS_TYPE=gym                    # gym | dental | coaching
CAMPAIGN_LANGUAGE=en                 # en | ar
DISCOUNT_PCT=25

# Churn Thresholds (floats)
CHURN_THRESHOLD_INFO=0.70
CHURN_THRESHOLD_BONUS=0.80
CHURN_THRESHOLD_DISCOUNT=0.90
```

### GitHub Actions Secrets & Variables

**Secrets (encrypted):**
- `ANTHROPIC_API_KEY`, `RESEND_API_KEY`
- `SENDER_EMAIL`, `SENDER_NAME`, `SENDER_PHYSICAL_ADDRESS`
- `INSTAGRAM_USERNAME`, `INSTAGRAM_PASSWORD`
- `GOOGLE_CREDENTIALS_JSON` (base64-encoded service account JSON)

**Variables (plain text):**
- `BUSINESS_TYPE`, `CAMPAIGN_LANGUAGE`, `DISCOUNT_PCT`
- `CHURN_THRESHOLD_INFO`, `CHURN_THRESHOLD_BONUS`, `CHURN_THRESHOLD_DISCOUNT`
- `GOOGLE_SHEET_ID`

### Authentication & Authorization

- **No user authentication within the app** — the workflow runs as a scheduled script with API keys stored in environment variables.
- **Client security model:** The freelancer or developer who deploys the workflow owns the GitHub repo and manages secrets. Clients never see API keys.
- **Google Sheets sharing:** The client shares their Sheet with a read-only service account email. The workflow never asks for the client's Google credentials.

### Compliance

**Egypt PDPL (Personal Data Protection Law No. 151/2020):**
- ✅ Prior consent assumed (existing customers who opted in)
- ✅ Clear sender identification in every email (SENDER_NAME, SENDER_EMAIL)
- ✅ Physical mailing address in footer (SENDER_PHYSICAL_ADDRESS)
- ✅ Working unsubscribe mechanism (`List-Unsubscribe` header + mailto link)
- ✅ Unsubscribed customer filter (`unsubscribed == yes` is skipped)
- ✅ Consent records: clients maintain their own opt-in records in Google Sheets

**CAN-SPAM (for clients outside Egypt):**
- ✅ Accurate header information
- ✅ Subject line matches content
- ✅ Clear identification as advertising
- ✅ Physical address included
- ✅ Working opt-out mechanism

### Security Scope

**In scope:**
- ✅ No hardcoded API keys or secrets in source code
- ✅ `.env` and `credentials.json` in `.gitignore`
- ✅ Input validation on customer data (robust pandas parsing)
- ✅ Rate limiting on sends (1-second sleep between emails)
- ✅ Quota detection prevents API abuse

**Out of scope for MVP:**
- ❌ Advanced bot protection
- ❌ IP allowlisting
- ❌ Audit trail beyond system_log.csv
- ❌ Encryption at rest for CSV files

---

## 10. API Specification

### Anthropic Claude API (Messages)

**Endpoint:** `POST https://api.anthropic.com/v1/messages`

**Headers:**
```
x-api-key: {ANTHROPIC_API_KEY}
anthropic-version: 2023-06-01
Content-Type: application/json
```

**Request Body:**
```json
{
  "model": "claude-haiku-4-5",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "[assembled prompt with customer data and business context]"
    }
  ]
}
```

**Response (success):**
```json
{
  "id": "msg_01X...",
  "type": "message",
  "role": "assistant",
  "model": "claude-haiku-4-5",
  "content": [
    {
      "type": "text",
      "text": "```json\n{\"offer_type\":\"discount\",\"offer_title\":\"...\",\"offer_details\":\"...\",\"cta_text\":\"...\"}\n```"
    }
  ]
}
```

**Error handling:**
- JSON parse error → retry once with same prompt
- Rate limit (429) → sleep 2 seconds and retry once
- Auth error (401) → log and skip customer

**Cost estimate:** ~$0.01–$0.03 per email (Sonnet 4.6 at $3/MTok input + $15/MTok output; Haiku 4.5 at $1/MTok input + $5/MTok output).

### Resend API (Send Email)

**Endpoint:** `POST https://api.resend.com/emails`

**Headers:**
```
Authorization: Bearer {RESEND_API_KEY}
Content-Type: application/json
```

**Request Body:**
```json
{
  "from": "Your Business Name <noreply@yourdomain.com>",
  "to": "customer@example.com",
  "subject": "Email subject line",
  "html": "<!DOCTYPE html>...",
  "headers": {
    "List-Unsubscribe": "<mailto:unsubscribe@yourdomain.com>"
  }
}
```

**Response (success):**
```json
{
  "id": "email_123..."
}
```

**Response (quota exceeded — 429):**
```json
{
  "error": "daily_quota_exceeded",
  "message": "You have reached your daily email quota."
}
```

**Error handling:**
- 429 quota exceeded → stop loop immediately, queue remaining for tomorrow
- Other errors → log failure, continue to next customer

**Pricing:** Free tier = 3,000 emails/month (100/day cap). Pro = $20/month (50,000 emails).

### Google Sheets API (via gspread)

**Read — Customer Data:**
```python
import gspread
client = gspread.service_account(filename="credentials.json")
sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("Customer Data")
records = sheet.get_all_records()  # Returns list of dicts
```

**Write — SYSTEM_LOG:**
```python
log_sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("SYSTEM_LOG")
log_sheet.append_row([timestamp, customer_id, action, offer_type, status, error])
```

---

## 11. Success Criteria

### MVP Success Definition

The MVP is complete when a non-technical business owner can:
1. Receive the workflow files from a freelancer
2. Fill a Google Sheet with their customer data
3. Set up `.env` with API keys (or have the freelancer do it)
4. Run `python main.py --demo` and see preview HTML emails
5. Run `python main.py --confirm` and have real emails sent automatically
6. Check `data/system_log.csv` for a complete audit trail
7. Configure GitHub Actions to run daily without any manual steps

### Functional Requirements

- ✅ `--demo` generates HTML preview files without API keys
- ✅ `--confirm` is required for production sends
- ✅ Running without `--demo` or `--confirm` exits with a clear error
- ✅ Fetch customers from CSV or Google Sheets based on config
- ✅ Filter eligible customers using configurable thresholds
- ✅ Filter out `unsubscribed == yes` customers
- ✅ Double-guard duplicate prevention (source date + log file)
- ✅ Compute heuristic churn score when missing
- ✅ Generate AI offers per business type with correct model selection
- ✅ Retry once on invalid JSON from AI
- ✅ Send emails via Resend with HTML, unsubscribe header, physical address
- ✅ RTL support for Arabic emails
- ✅ Instagram DM fallback when email missing
- ✅ Quota exceeded → stop + queue remaining
- ✅ Log every action to CSV
- ✅ Console summary at end of run
- ✅ GitHub Actions runs daily at 9 AM UTC
- ✅ GitHub Actions supports manual trigger with dry-run option

### Quality Indicators

- All Python files pass `python -m py_compile` with zero errors
- Demo mode runs end-to-end on a fresh clone with no `.env` configured
- Production mode refuses to run without `--confirm`
- No hardcoded API keys in source code
- `.env` and `credentials.json` are in `.gitignore`
- All prompt templates are valid markdown with correct placeholders
- Email HTML renders correctly in popular clients (Gmail, Outlook, Apple Mail)

### User Experience Goals

- First demo run completes in under 10 seconds for a 10-customer sample
- Production run for 100 customers completes in under 5 minutes (AI generation is the bottleneck)
- A non-technical user can set up the workflow within 30 minutes using the README
- Client can onboard using Google Sheets within 15 minutes

---

## 12. Implementation Phases

### Phase 1: Core Backend + Demo Mode

**Goal:** All tools run end-to-end in demo mode. Configurable thresholds, industry-specific prompts, HTML email generation.

**Deliverables:**
- ✅ Project scaffolding: `config.py`, `.env.example`, `requirements.txt`
- ✅ `tools/prompts/` directory with 4 markdown templates
- ✅ Enhanced `fetch_customers.py` — CSV/Sheets auto-detection, thresholds, unsubscribe, duplicate guard, churn fallback
- ✅ Enhanced `generate_offer.py` — prompt template loading, model selection, retry, Arabic support
- ✅ Enhanced `send_email.py` — HTML generation, RTL, unsubscribe header, address footer, quota detection
- ✅ Enhanced `main.py` — `--demo`, `--confirm`, `--business-type`, `--language`, `--customer-id`, `--channel`, console summary
- ✅ Instagram fallback logic
- ✅ Sample `data/customers.csv` with all 3 business types + instagram_handle + unsubscribed
- ✅ Demo passes: `python main.py --demo` runs and generates HTML
- ✅ Safety passes: `python main.py` refuses without `--confirm`
- ✅ All acceptance criteria for Chunks 1–5 verified

### Phase 2: GitHub Actions + Client Documentation

**Goal:** Automated daily execution and comprehensive client onboarding docs.

**Deliverables:**
- ✅ `.github/workflows/daily_reactivation.yml` — cron + manual trigger
- ✅ GitHub Actions reads all secrets and variables correctly
- ✅ README.md with setup, demo, production, troubleshooting sections
- ✅ `docs/google_sheets_template.md` with step-by-step guide
- ✅ `data/demo_output/` directory prepared
- ✅ All CLI args documented
- ✅ Cost estimate documented (Resend + Claude pricing)

### Phase 3: Real-World Validation

**Goal:** Test with real API keys on a small batch to confirm deliverability and cost.

**Deliverables:**
- ✅ `.env` filled with real API keys
- ✅ Send 5–10 emails to test addresses (not real customers)
- ✅ Confirm emails land in inbox (not spam) for Gmail, Outlook
- ✅ Verify HTML rendering: CTA button, RTL, footer
- ✅ Confirm Resend dashboard shows delivery status
- ✅ Verify Claude API costs match estimates (~$0.01–$0.03/email)
- ✅ Document any deliverability adjustments needed
- ✅ Update `docs/research_findings.md` with learnings

### Phase 4: Client Delivery Package

**Goal:** Package the workflow as a deliverable the freelancer can hand to a client.

**Deliverables:**
- ✅ Final README with client-specific instructions
- ✅ Template Google Sheet with sample data (make a copy link)
- ✅ Pricing sheet: setup fee + estimated monthly API costs per client volume
- ✅ Onboarding checklist: what the client needs before going live
- ✅ Support guide: common errors and how to fix them
- ✅ Optional: one-page "sell sheet" explaining ROI (2–3% conversion = 80–130 customers from 4,000)

---

## 13. Future Considerations

### Post-MVP Enhancements
- **SMS via Twilio** — Multi-channel reactivation alongside email
- **A/B testing** — Test two message variants per batch and compare open rates
- **Open/click tracking pixel** — Embed invisible pixel to measure engagement
- **Auto-stop on reply/purchase** — Monitor for customer replies or new transactions and stop further outreach
- **Webhook handling** — Resend bounce/complaint webhooks to auto-update customer status
- **Web dashboard** — Simple web UI for clients to upload CSVs, preview emails, and trigger runs
- **Multi-client SaaS** — Single hosted instance serving multiple clients with data isolation

### Integration Opportunities
- **Zapier / Make** — Trigger runs from external events (new Stripe charge = remove from reactivation pool)
- **Stripe / payment gateways** — Auto-detect recent payments and exclude from campaigns
- **OpenAI GPT-4** — Alternative AI provider for clients who prefer OpenAI over Claude
- **SendGrid** — Alternative email provider (structure already supports pluggable providers)

### Advanced Features
- **Deep RFM segmentation** — Combine Recency, Frequency, Monetary with churn scores
- **Expected value targeting** — Weight churn probability by customer lifetime value
- **Decile-based targeting** — Target top deciles rather than fixed thresholds
- **Custom prompt builder** — Web UI for clients to customize AI prompts without editing `.md` files
- **Video message generation** — AI-generated personalized video scripts for high-value customers
- **Multi-step drip campaigns** — Day 1: informational, Day 7: bonus, Day 14: discount (if no response)

---

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| **Emails land in spam** — Reactivation emails to cold contacts have high spam risk. | High | Use verified domain in Resend, warm up sending volume, include unsubscribe + physical address, monitor Resend dashboard for bounces/complaints. Start with test sends to personal emails. Manually monitor the Resend dashboard for bounce/complaint rates during the first 2 weeks of any production launch, since automated bounce webhook handling is deferred to Phase 2. |
| **Claude API costs grow** — 4,000 customers × 3 campaigns/month = 12,000 API calls. | Medium | Use Haiku for informational tier (cheapest). Consider Batch API (50% discount) if latency tolerance increases. Costs remain low (~$120–$360/month at 12k emails). |
| **Client data quality** — Clients provide messy CSVs with missing columns, wrong formats. | Medium | Validate all required columns at startup with clear error messages. Use pandas `errors='coerce'`. Document exact schema. Provide template Google Sheet with data validation. |
| **Duplicate sends** — Multiple runs or rescheduled jobs could email the same person twice. | High | Double-guard prevention: check both data source date AND system log. Log every send with timestamp. GitHub Actions concurrency setting prevents overlapping runs. |
| **Instagram DM reliability** — `instagrapi` requires stable login session; Instagram may block automated DMs. | Medium | Mark Instagram as "experimental" in docs. Primary channel is email. Instagram is a fallback only. Document 2FA workaround. |
| **Claude returns invalid JSON** — AI may hallucinate non-JSON output despite instructions. | Medium | Retry once with same prompt. If still invalid, skip customer and log failure. Monitor failure rate; if >5%, tighten prompt or switch to structured outputs. |

---

## 15. Appendix

### Key Dependencies

| Package | Docs |
|---|---|
| Anthropic Python SDK | https://docs.anthropic.com/en/api/getting-started |
| Resend Python SDK | https://resend.com/docs/send-with-python |
| gspread | https://docs.gspread.org |
| pandas | https://pandas.pydata.org/docs |
| instagrapi | https://github.com/subzeroid/instagrapi |
| python-dotenv | https://saurabh-kumar.com/python-dotenv |

### Related Documents
- `database_reactivation (1).md` — Original workflow specification
- `.kimchi/docs/implementation_plan.md` — Implementation chunk plan
- `.kimchi/docs/research_findings.md` — Research on churn thresholds, email deliverability, competitor analysis
- `.kimchi/docs/research_churn_thresholds.md` — Deep dive on churn score calibration
- `.kimchi/docs/clarifying_questions.md` — Client Q&A (30 questions + answers)
- `docs/google_sheets_template.md` — Client onboarding guide
- `README.md` — Setup and usage instructions

### Directory Reference
```
/workspaces/Report/
├── main.py                          # Orchestrator
├── config.py                        # Config loader
├── .env.example                     # Env template
├── requirements.txt                 # Dependencies
├── data/
│   ├── customers.csv                # Sample data (5 rows, 3 industries)
│   ├── system_log.csv               # Action log
│   └── demo_output/                 # .gitkeep
├── .tmp/demo_emails/                # Demo HTML outputs (auto-created)
├── tools/
│   ├── fetch_customers.py           # Data layer
│   ├── generate_offer.py            # AI layer
│   ├── send_email.py                # Email delivery
│   ├── send_instagram_dm.py         # Instagram fallback
│   ├── log_action.py                # Logging
│   └── prompts/
│       ├── base.md                  # Base prompt
│       ├── gym.md                   # Fitness addendum
│       ├── dental.md                # Dental addendum
│       └── coaching.md              # Coaching addendum
├── docs/
│   └── google_sheets_template.md    # Client setup guide
└── .github/workflows/
    └── daily_reactivation.yml       # CI/CD
```

### Cost Benchmarks

| Volume | Resend Cost | Claude Cost | Total/Month |
|---|---|---|---|
| 100 emails/day (3k/mo) | $0 (Free tier) | ~$30 | ~$30 |
| 500 emails/day (15k/mo) | $20 (Pro 50k) | ~$150 | ~$170 |
| 1,000 emails/day (30k/mo) | $35 (Pro 100k) | ~$300 | ~$335 |
| 5,000 emails/day (150k/mo) | $90 (Scale 100k + overage) | ~$1,500 | ~$1,590 |

*Assumes average 600 input tokens + 800 output tokens per email, Sonnet for 60% of sends.*
