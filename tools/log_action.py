#!/usr/bin/env python3
"""Step 4: Append action result to system_log.csv."""
import csv
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import config

LOG_PATH = Path(config.SYSTEM_LOG_PATH)
HEADERS = ["timestamp", "customer_id", "action_taken", "offer_type", "status", "error_message"]


def log_action(customer_id: str, action_taken: str, offer_type: str, status: str, error_message: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = LOG_PATH.exists()

    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(HEADERS)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer_id,
            action_taken,
            offer_type,
            status,
            error_message,
        ])


if __name__ == "__main__":
    log_action("C999", "TEST_ACTION", "discount", "success", "")
    print(f"Logged test row to {LOG_PATH}")
