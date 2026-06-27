# Database Reactivation Workflow

An AI-powered automated email system that identifies dormant customers and sends personalized reactivation campaigns. Designed for gyms, dental clinics, and coaching businesses to win back lapsed customers with tailored offers.

## Features

- **AI-Generated Personalization**: Uses Claude AI to create compelling, individualized emails based on customer history and behavior
- **Smart Audience Segmentation**: Automatically categorizes customers by churn risk (informational, bonus points, or discount offers)
- **Multi-Channel Fallback**: Sends Instagram DMs when email is unavailable or invalid
- **Bilingual Support**: Ready for English and Arabic campaigns
- **Demo Mode**: Preview all emails before any are sent
- **Google Sheets Integration**: Pull customer data directly from Google Sheets

## Two Operating Modes

### Demo Mode (`--demo`)
Generates HTML email previews without sending anything or making API calls. Perfect for reviewing email quality before production.

```bash
python main.py --demo
```

Demo outputs are saved to `.tmp/demo_emails/`.

### Production Mode (`--confirm`)
Actually sends emails to customers. **Requires** the `--confirm` flag as a safety measure.

```bash
python main.py --confirm
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Report
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# API Keys (required)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
RESEND_API_KEY=your_resend_api_key_here

# Sender Information (required)
SENDER_EMAIL=hello@yourbusiness.com
SENDER_NAME=Your Business Name
SENDER_PHYSICAL_ADDRESS=123 Business St, City, State 12345

# Instagram DM Fallback (optional — for customers without valid email)
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# Business Configuration
BUSINESS_TYPE=gym                    # gym | dental | coaching
CAMPAIGN_LANGUAGE=en                 # en | ar
CHURN_THRESHOLD_INFO=0.70
CHURN_THRESHOLD_BONUS=0.80
CHURN_THRESHOLD_DISCOUNT=0.90
DISCOUNT_PCT=25

# Google Sheets (optional — leave empty to use CSV)
GOOGLE_SHEET_ID=
GOOGLE_CREDENTIALS_PATH=credentials.json

# Data Paths
CUSTOMERS_CSV_PATH=data/customers.csv
SYSTEM_LOG_PATH=data/system_log.csv
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Customer Data

You can use either a CSV file or Google Sheets:

#### Option A: CSV File

Create `data/customers.csv` with the schema below.

#### Option B: Google Sheets

See [docs/google_sheets_template.md](docs/google_sheets_template.md) for setup instructions.

### 5. Run Demo Mode First

Always test with demo mode before sending any emails:

```bash
python main.py --demo
```

Review the generated emails in `.tmp/demo_emails/` to ensure quality.

### 6. Run Production Mode

```bash
python main.py --confirm
```

---

## Customer Data Schema

Your `customers.csv` (or Google Sheet) must include these columns:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `customer_id` | string | Yes | Unique customer identifier |
| `name` | string | Yes | Customer's full name |
| `email` | string | Yes | Email address |
| `instagram_handle` | string | No | Instagram username (for DM fallback) |
| `last_purchase_date` | date | Yes | Format: YYYY-MM-DD |
| `predicted_churn_score` | float | No | 0.0-1.0 (computed if missing) |
| `preferred_categories` | string | No | Comma-separated preferences |
| `created_campaign_date` | date | No | Last campaign sent date |
| `total_purchases` | int | Yes | Total number of purchases |
| `days_since_last_contact` | int | Yes | Days since last email/interaction |
| `unsubscribed` | string | Yes | `yes` to exclude, `no` to include |

### Sample Rows

**Gym:**
```
customer_id,name,email,instagram_handle,last_purchase_date,predicted_churn_score,preferred_categories,created_campaign_date,total_purchases,days_since_last_contact,unsubscribed
GYM001,John Smith,john@email.com,@johnfit,2025-01-15,0.85,HIIT,2025-03-10,45,120,no
```

**Dental:**
```
customer_id,name,email,instagram_handle,last_purchase_date,predicted_churn_score,preferred_categories,created_campaign_date,total_purchases,days_since_last_contact,unsubscribed
DEN001,Sarah Johnson,sarah@email.com,,2025-02-20,0.78,cleaning,2025-04-01,12,90,no
```

**Coaching:**
```
customer_id,name,email,instagram_handle,last_purchase_date,predicted_churn_score,preferred_categories,created_campaign_date,total_purchases,days_since_last_contact,unsubscribed
COA001,Mike Wilson,mike@email.com,@mikew,2025-01-05,0.92,business_coaching,2025-03-15,30,150,no
```

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | API key for Claude AI |
| `RESEND_API_KEY` | Yes | - | API key for Resend email service |
| `SENDER_EMAIL` | Yes | - | From email address |
| `SENDER_NAME` | Yes | - | From name displayed |
| `SENDER_PHYSICAL_ADDRESS` | Yes | - | Physical address (required by law) |
| `INSTAGRAM_USERNAME` | No | - | Instagram username for DM fallback |
| `INSTAGRAM_PASSWORD` | No | - | Instagram password for DM fallback |
| `BUSINESS_TYPE` | No | `gym` | Industry: `gym`, `dental`, or `coaching` |
| `CAMPAIGN_LANGUAGE` | No | `en` | `en` (English) or `ar` (Arabic) |
| `CHURN_THRESHOLD_INFO` | No | `0.70` | Min churn score for informational offer |
| `CHURN_THRESHOLD_BONUS` | No | `0.80` | Min churn score for bonus offer |
| `CHURN_THRESHOLD_DISCOUNT` | No | `0.90` | Min churn score for discount offer |
| `DISCOUNT_PCT` | No | `25` | Discount percentage in offers |
| `GOOGLE_SHEET_ID` | No | - | Google Sheet ID for customer data |
| `GOOGLE_CREDENTIALS_PATH` | No | `credentials.json` | Path to Google service account JSON |
| `CUSTOMERS_CSV_PATH` | No | `data/customers.csv` | Path to customer CSV file |
| `SYSTEM_LOG_PATH` | No | `data/system_log.csv` | Path to system log |

---

## GitHub Actions Deployment

This workflow runs automatically every day at 9:00 AM UTC, or can be triggered manually.

### Required Secrets

Configure these in your GitHub repository under `Settings > Secrets and variables > Actions`:

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `RESEND_API_KEY` | Your Resend API key |
| `SENDER_EMAIL` | Email address to send from |
| `SENDER_NAME` | Display name for sender |
| `SENDER_PHYSICAL_ADDRESS` | Physical mailing address |
| `INSTAGRAM_USERNAME` | Instagram username (optional) |
| `INSTAGRAM_PASSWORD` | Instagram password (optional) |
| `GOOGLE_SHEET_ID` | Your Google Sheet ID |
| `GOOGLE_CREDENTIALS_JSON` | Base64-encoded service account JSON |

### Required Variables

Set these under `Settings > Secrets and variables > Actions > Variables`:

| Variable | Default | Description |
|----------|---------|-------------|
| `BUSINESS_TYPE` | `gym` | Industry type |
| `CAMPAIGN_LANGUAGE` | `en` | Campaign language |
| `CHURN_THRESHOLD_INFO` | `0.70` | Churn threshold for info tier |
| `CHURN_THRESHOLD_BONUS` | `0.80` | Churn threshold for bonus tier |
| `CHURN_THRESHOLD_DISCOUNT` | `0.90` | Churn threshold for discount tier |
| `DISCOUNT_PCT` | `25` | Discount percentage |

### Manual Trigger

To run manually, go to the **Actions** tab in your GitHub repository, select **Daily Database Reactivation**, and click **Run workflow**.

You can also trigger via CLI:

```bash
gh workflow run daily_reactivation.yml
```

To run in demo mode:

```bash
gh workflow run daily_reactivation.yml -f dry_run=true
```

---

## Troubleshooting

### "Production mode requires --confirm flag"

You forgot to add `--confirm`. For demo mode, use `--demo` instead:

```bash
python main.py --demo
```

### "ANTHROPIC_API_KEY not found"

Your `.env` file is missing or doesn't contain the API key. Make sure you copied `.env.example` to `.env` and filled in all required values.

### "RESEND_API_KEY not found"

Same as above — ensure your `.env` file is configured.

### Emails not sending

1. Check your Resend dashboard to verify your API key is active
2. Confirm the sender email is verified in Resend
3. Check `data/system_log.csv` for error statuses

### Google Sheets not loading

1. Verify `GOOGLE_SHEET_ID` is correct in your `.env`
2. Ensure the service account has access to the sheet (share with the service account email)
3. Verify `credentials.json` or `GOOGLE_CREDENTIALS_JSON` is properly configured

### All customers marked as unsubscribed

Check your CSV/Sheet — make sure `unsubscribed` column contains lowercase `no` (not `No` or `NO`).

### Customers not being processed

The system skips customers who:
- Have `unsubscribed = yes`
- Have a `created_campaign_date` within the last 30 days
- Already appear in `system_log.csv` with `SENT_WINBACK_OFFER` in the last 30 days

---

## Pricing & Cost Estimates

### Resend (Email Delivery)

**Free Tier**: 3,000 emails per month

For most small businesses, the free tier is sufficient. If you need more:
- $20/month for 50,000 emails
- Custom pricing available for higher volumes

### Anthropic Claude API (AI Generation)

**Cost per email**: Approximately $0.01 - $0.03

Claude Haiku is used for informational tier emails (cheaper), and Claude Sonnet for bonus/discount offers (higher quality).

**Estimated monthly cost** for 1,000 customers:
- ~1,000 informational emails × $0.002 = ~$2
- ~100 bonus/discount emails × $0.015 = ~$1.50
- **Total: approximately $3-5 per month**

### Overall Monthly Cost

| Business Size | Emails/Month | Estimated Cost |
|---------------|--------------|----------------|
| Small | 0-500 | $0-2 |
| Medium | 500-2,000 | $2-10 |
| Large | 2,000-10,000 | $10-50 |

---

## License

MIT License - See LICENSE file for details.