#!/usr/bin/env python3
"""Central configuration loader for the Database Reactivation Workflow.
Reads from .env and provides typed values with sensible defaults.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# =============================================================================
# Thresholds
# =============================================================================
CHURN_THRESHOLD_INFO: float = float(os.getenv("CHURN_THRESHOLD_INFO", "0.70"))
CHURN_THRESHOLD_BONUS: float = float(os.getenv("CHURN_THRESHOLD_BONUS", "0.80"))
CHURN_THRESHOLD_DISCOUNT: float = float(os.getenv("CHURN_THRESHOLD_DISCOUNT", "0.90"))

# =============================================================================
# Offer settings
# =============================================================================
DISCOUNT_PCT: int = int(os.getenv("DISCOUNT_PCT", "25"))
BUSINESS_TYPE: str = os.getenv("BUSINESS_TYPE", "gym")
CAMPAIGN_LANGUAGE: str = os.getenv("CAMPAIGN_LANGUAGE", "en")

# =============================================================================
# Sender info
# =============================================================================
SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "")
SENDER_NAME: str = os.getenv("SENDER_NAME", "")
SENDER_PHYSICAL_ADDRESS: str = os.getenv("SENDER_PHYSICAL_ADDRESS", "")

# =============================================================================
# API keys
# =============================================================================
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
INSTAGRAM_USERNAME: str = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD: str = os.getenv("INSTAGRAM_PASSWORD", "")

# =============================================================================
# Google Sheets (optional)
# =============================================================================
GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

# =============================================================================
# Data paths
# =============================================================================
CUSTOMERS_CSV_PATH: str = os.getenv("CUSTOMERS_CSV_PATH", "data/customers.csv")
SYSTEM_LOG_PATH: str = os.getenv("SYSTEM_LOG_PATH", "data/system_log.csv")

# =============================================================================
# Helpers
# =============================================================================


def is_dry_run() -> bool:
    """Return True if critical API keys are missing (dry-run mode)."""
    return not ANTHROPIC_API_KEY or not RESEND_API_KEY


def validate_production_config():
    """Validate that all required production config variables are set.
    
    Raises:
        ValueError: If any critical production variable is missing.
    """
    missing = []
    if not RESEND_API_KEY:
        missing.append("RESEND_API_KEY")
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not SENDER_EMAIL:
        missing.append("SENDER_EMAIL")
    if not SENDER_NAME:
        missing.append("SENDER_NAME")
    if not SENDER_PHYSICAL_ADDRESS:
        missing.append("SENDER_PHYSICAL_ADDRESS")
    
    if missing:
        raise ValueError(f"Missing required production config: {', '.join(missing)}")


def get_config() -> Dict[str, Any]:
    """Return a dictionary of all config values."""
    return {
        "churn_threshold_info": CHURN_THRESHOLD_INFO,
        "churn_threshold_bonus": CHURN_THRESHOLD_BONUS,
        "churn_threshold_discount": CHURN_THRESHOLD_DISCOUNT,
        "discount_pct": DISCOUNT_PCT,
        "business_type": BUSINESS_TYPE,
        "campaign_language": CAMPAIGN_LANGUAGE,
        "sender_email": SENDER_EMAIL,
        "sender_name": SENDER_NAME,
        "sender_physical_address": SENDER_PHYSICAL_ADDRESS,
        "anthropic_api_key": ANTHROPIC_API_KEY,
        "resend_api_key": RESEND_API_KEY,
        "instagram_username": INSTAGRAM_USERNAME,
        "instagram_password": INSTAGRAM_PASSWORD,
        "google_sheet_id": GOOGLE_SHEET_ID,
        "google_credentials_path": GOOGLE_CREDENTIALS_PATH,
        "customers_csv_path": CUSTOMERS_CSV_PATH,
        "system_log_path": SYSTEM_LOG_PATH,
        "is_dry_run": is_dry_run(),
    }


if __name__ == "__main__":
    # Quick test: print all config values
    import json

    config = get_config()
    # Mask API keys for display
    display_config = config.copy()
    if display_config.get("anthropic_api_key"):
        display_config["anthropic_api_key"] = "***" + display_config["anthropic_api_key"][-4:]
    if display_config.get("resend_api_key"):
        display_config["resend_api_key"] = "***" + display_config["resend_api_key"][-4:]

    print(json.dumps(display_config, indent=2))
    print(f"\nDry-run mode: {is_dry_run()}")