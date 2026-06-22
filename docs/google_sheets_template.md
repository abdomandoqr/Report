# Google Sheets Template Setup Guide

This guide explains how to set up Google Sheets as a data source for the Database Reactivation Workflow. Using Google Sheets allows multiple team members to update customer data without touching code.

---

## Step 1: Create a New Google Sheet

1. Go to [Google Sheets](https://sheets.google.com) and sign in
2. Click **Blank** to create a new spreadsheet
3. Name it something like "Customer Database - Reactivation Campaign"

---

## Step 2: Set Up the Required Columns

Create a sheet with exactly these columns in row 1 (headers):

| Column | Description |
|--------|-------------|
| `customer_id` | Unique customer identifier |
| `name` | Customer's full name |
| `email` | Email address |
| `instagram_handle` | Instagram username (optional) |
| `last_purchase_date` | Last purchase date (YYYY-MM-DD format) |
| `predicted_churn_score` | Churn probability 0.0-1.0 (optional — computed if empty) |
| `preferred_categories` | Customer preferences, comma-separated |
| `created_campaign_date` | Date last campaign was sent (YYYY-MM-DD) |
| `total_purchases` | Total number of purchases |
| `days_since_last_contact` | Days since last email/contact |
| `unsubscribed` | `yes` to exclude, `no` to include |

---

## Step 3: Add Sample Data

Below are example rows for each business type:

### Gym Example

| customer_id | name | email | instagram_handle | last_purchase_date | predicted_churn_score | preferred_categories | created_campaign_date | total_purchases | days_since_last_contact | unsubscribed |
|-------------|------|-------|------------------|-------------------|----------------------|---------------------|----------------------|-----------------|------------------------|--------------|
| GYM001 | John Smith | john.smith@email.com | @johnsmith_fit | 2025-01-15 | 0.85 | Personal Training,HIIT,Supplements | 2025-03-10 | 45 | 120 | no |
| GYM002 | Sarah Connor | sarah.c@email.com | @sarahconnor | 2025-02-20 | 0.72 | Yoga,Meditation | | 28 | 95 | no |
| GYM003 | Mike Johnson | mike.j@email.com | | 2024-12-01 | 0.91 | CrossFit,Weightlifting | 2025-04-01 | 62 | 180 | no |

### Dental Clinic Example

| customer_id | name | email | instagram_handle | last_purchase_date | predicted_churn_score | preferred_categories | created_campaign_date | total_purchases | days_since_last_contact | unsubscribed |
|-------------|------|-------|------------------|-------------------|----------------------|---------------------|----------------------|-----------------|------------------------|--------------|
| DEN001 | Emily Watson | emily.w@email.com | @emilywatson_dental | 2025-02-10 | 0.78 | Teeth Cleaning,Cosmetic | 2025-04-15 | 12 | 88 | no |
| DEN002 | Robert Chen | robert.chen@email.com | | 2025-01-25 | 0.88 | Orthodontics,Whitening | | 8 | 105 | no |
| DEN003 | Maria Garcia | maria.g@email.com | @mariagarcia_dds | 2024-11-15 | 0.94 | Implants,Root Canal | 2025-02-20 | 24 | 195 | no |

### Coaching Business Example

| customer_id | name | email | instagram_handle | last_purchase_date | predicted_churn_score | preferred_categories | created_campaign_date | total_purchases | days_since_last_contact | unsubscribed |
|-------------|------|-------|------------------|-------------------|----------------------|---------------------|----------------------|-----------------|------------------------|--------------|
| COA001 | David Park | david.park@email.com | @davidpark_coach | 2025-01-05 | 0.92 | Business Coaching,Leadership | 2025-03-15 | 30 | 150 | no |
| COA002 | Lisa Thompson | lisa.t@email.com | @lisathompsonbiz | 2025-02-28 | 0.75 | Sales Training,Time Management | | 18 | 78 | no |
| COA003 | James Wilson | james.w@email.com | | 2024-12-20 | 0.89 | Executive Coaching,Strategy | 2025-04-01 | 42 | 165 | no |

---

## Step 4: Create a Service Account for Google Sheets Access

### 4.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Name your project (e.g., "Reactivation Workflow")
4. Click **Create**

### 4.2 Enable Google Sheets API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Sheets API"
3. Click on it and click **Enable**

### 4.3 Create a Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Name it (e.g., "reactivation-workflow")
4. Click **Create and Continue**
5. Skip optional steps and click **Done**

### 4.4 Generate JSON Key

1. Click on your new service account
2. Go to the **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON** and click **Create**
5. The key file will download automatically — save it securely

### 4.5 Share Your Google Sheet with the Service Account

1. Open your Google Sheet
2. Click the **Share** button
3. In "Add people and groups", paste the service account email (found in the downloaded JSON file as `client_email`)
4. Set permission to **Viewer**
5. Check "Notify people" (optional)
6. Click **Share**

---

## Step 5: Get Your Google Sheet ID

The Sheet ID is found in the URL:

```
https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
```

For example, if the URL is:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
```

Then the Sheet ID is:
```
1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

---

## Step 6: Configure the Workflow

### Option A: Local Development

Add to your `.env` file:

```env
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_PATH=path/to/your/service-account-key.json
```

### Option B: GitHub Actions

1. Base64 encode your credentials file:
   ```bash
   base64 -i path/to/your/service-account-key.json
   ```

2. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**

3. Add a new secret:
   - Name: `GOOGLE_CREDENTIALS_JSON`
   - Value: (paste the base64-encoded string)

4. Add another secret:
   - Name: `GOOGLE_SHEET_ID`
   - Value: (your sheet ID)

---

## Updating Customer Data

Simply add, edit, or remove rows in the Google Sheet. The workflow will pick up changes on its next run.

**Tips:**
- Do not change column headers
- Use consistent date formats (YYYY-MM-DD)
- Use lowercase `yes`/`no` for the `unsubscribed` column
- Leave `predicted_churn_score` empty to let the system compute it

---

## Troubleshooting

### "Spreadsheet not found" error

1. Verify your `GOOGLE_SHEET_ID` is correct
2. Make sure the service account email has access to the sheet

### "Invalid credentials" error

1. Verify the JSON key file is valid
2. Make sure the service account has the "Viewer" role on the sheet
3. Check that the Google Sheets API is enabled in your Cloud project

### Sheet not updating

The workflow reads the sheet at runtime. Make sure the sheet name is exactly `Customer Data`, or update `config.py` to match your sheet name.

---

## Support

If you need help setting up Google Sheets integration, refer to the [Google Sheets API documentation](https://developers.google.com/sheets/api) or open an issue in the repository.