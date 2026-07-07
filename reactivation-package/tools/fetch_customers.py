#!/usr/bin/env python3
"""Step 1: Read and filter eligible customers from CSV or Google Sheets."""
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

import config
from tools.log_action import log_action

CSV_PATH = Path(config.CUSTOMERS_CSV_PATH)
SYSTEM_LOG_PATH = Path(config.SYSTEM_LOG_PATH)


def compute_churn_score(days_since_contact: int, total_purchases: int, days_since_purchase: int) -> float:
    """Compute a heuristic churn score when the column is missing/empty.
    
    Args:
        days_since_contact: Days since last contact
        total_purchases: Total number of purchases
        days_since_purchase: Days since last purchase
    
    Returns:
        Churn score between 0.0 and 1.0
    """
    recency = min(days_since_contact / 180, 1.0)
    frequency = max(1 - (total_purchases / 50), 0.0)
    return round((recency * 0.7 + frequency * 0.3), 2)


def _check_duplicate_in_system_log(customer_id: str, days_threshold: int = 30) -> bool:
    """Check if customer_id has SENT_WINBACK_OFFER in system_log.csv within days_threshold.
    
    Returns:
        True if duplicate found (should skip), False otherwise.
    """
    if not SYSTEM_LOG_PATH.exists():
        return False
    
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(SYSTEM_LOG_PATH, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row.get("customer_id") == customer_id and
                    row.get("action_taken") == "SENT_WINBACK_OFFER" and
                    row.get("timestamp", "") >= cutoff_str):
                    return True
    except Exception:
        pass
    
    return False


def _fetch_from_google_sheets() -> list[dict]:
    """Fetch customer data from Google Sheets.
    
    Returns:
        List of customer record dicts.
    """
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(config.GOOGLE_CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(config.GOOGLE_SHEET_ID)
    worksheet = sheet.worksheet("Customer Data")
    records = worksheet.get_all_records()
    
    return records


def _fetch_from_csv(csv_path: Path) -> pd.DataFrame:
    """Fetch customer data from CSV file."""
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found.", file=sys.stderr)
        sys.exit(1)
    return pd.read_csv(csv_path)


def fetch_customers(csv_path=CSV_PATH):
    """Fetch and filter eligible customers.
    
    Auto-detects data source: Google Sheets if GOOGLE_SHEET_ID is set,
    otherwise falls back to CSV.
    
    Returns:
        List of customer dicts with plain types for JSON-serializability.
    """
    # Auto-detect data source
    if config.GOOGLE_SHEET_ID:
        print(f"Fetching from Google Sheets: {config.GOOGLE_SHEET_ID}")
        raw_records = _fetch_from_google_sheets()
        df = pd.DataFrame(raw_records)
    else:
        print(f"Fetching from CSV: {csv_path}")
        df = _fetch_from_csv(csv_path)
    
    # Validate required columns
    required_cols = ["customer_id", "name", "email", "days_since_last_contact"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required column(s): {', '.join(missing_cols)}. Please check your data source schema.")
    
    # Coerce date columns
    df["last_campaign_date"] = pd.to_datetime(df.get("last_campaign_date"), errors="coerce")
    df["last_purchase_date"] = pd.to_datetime(df.get("last_purchase_date"), errors="coerce")
    
    # Convert churn_score to numeric, coerce errors to NaN
    df["churn_score"] = pd.to_numeric(df.get("churn_score"), errors="coerce")
    
    now = pd.Timestamp.now()
    thirty_days_ago = now - pd.Timedelta(days=30)
    
    # Use configurable thresholds from config
    threshold_info = config.CHURN_THRESHOLD_INFO
    threshold_bonus = config.CHURN_THRESHOLD_BONUS
    threshold_discount = config.CHURN_THRESHOLD_DISCOUNT
    
    # Filter eligible customers:
    # 1. Churn score meets minimum threshold
    # 2. No recent campaign (last_campaign_date > 30 days or empty)
    # 3. Days since last contact > 90
    # 4. Not unsubscribed
    eligible_mask = (
        (df["churn_score"] >= threshold_info)
        & ((df["last_campaign_date"].isna()) | (df["last_campaign_date"] < thirty_days_ago))
        & (df.get("days_since_last_contact", 0).fillna(0) > 90)
    )
    
    # Handle unsubscribed column (may not exist in all data sources)
    if "unsubscribed" in df.columns:
        # Filter out unsubscribed customers (yes, true, 1)
        unsubscribed_mask = df["unsubscribed"].astype(str).str.lower().isin(["yes", "true", "1"])
        eligible_mask = eligible_mask & ~unsubscribed_mask
    
    eligible = df[eligible_mask].copy()
    
    # Compute churn score if missing/empty
    for idx, row in eligible.iterrows():
        if pd.isna(row["churn_score"]) or row["churn_score"] == "":
            days_contact = int(row.get("days_since_last_contact", 180) or 180)
            total_purch = int(row.get("total_purchases", 0) or 0)
            days_purchase = int(row.get("days_since_purchase", 180) or 180)
            eligible.at[idx, "churn_score"] = compute_churn_score(days_contact, total_purch, days_purchase)
    
    # Double-guard duplicate prevention:
    # Check last_campaign_date in data AND system_log.csv
    records = []
    for _, row in eligible.iterrows():
        customer_id = row.get("customer_id", "")
        
        # Check system_log.csv for SENT_WINBACK_OFFER within last 30 days
        if _check_duplicate_in_system_log(customer_id, days_threshold=30):
            log_action(customer_id, "SKIPPED", "none", "success", "Campaign sent within last 30 days")
            continue
        
        record = row.to_dict()
        # Convert NaT/NaN to None or plain values
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif hasattr(value, "isoformat"):
                record[key] = value.strftime("%Y-%m-%d")
        records.append(record)
    
    return records


if __name__ == "__main__":
    customers = fetch_customers()
    if customers:
        print(f"Found {len(customers)} eligible customer(s).")
        for c in customers:
            print(f"  - {c['customer_id']}: {c['name']} (churn={c['churn_score']}, silent={c['days_since_last_contact']}d)")
    else:
        print("No eligible customers found. Logging NOT_FOUND and stopping.")
