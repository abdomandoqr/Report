#!/usr/bin/env python3
"""Strategy planner for the reactivation workflow.

Decides, per customer, what offer to send and through which channel.
The decision is rule-based but explains itself (minimal agentic lift).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
# Use config.SYSTEM_LOG_PATH for history lookups.


@dataclass
class CampaignPlan:
    """Strategy decision for one customer."""

    customer_id: str
    offer_type: str
    channel: str  # "email", "instagram", or "both"
    reasoning: str
    model: str = ""


def _offer_type_from_score(churn_score: float) -> str:
    """Map churn score to offer tier using config thresholds."""
    if churn_score < config.CHURN_THRESHOLD_BONUS:
        return "informational"
    if churn_score < config.CHURN_THRESHOLD_DISCOUNT:
        return "bonus_points"
    return "discount"


def _model_for_offer_type(offer_type: str) -> str:
    """Select Claude model based on offer complexity."""
    if offer_type == "informational":
        return "claude-3-haiku-20240307"
    return "claude-3-sonnet-20240229"


def _read_customer_history(customer_id: str, log_path: Path = Path(config.SYSTEM_LOG_PATH)) -> List[Dict[str, Any]]:
    """Read prior log rows for a customer, newest first."""
    if not log_path.exists():
        return []

    rows: List[Dict[str, Any]] = []
    try:
        import csv
        with open(log_path, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("customer_id") == customer_id:
                    rows.append(dict(row))
    except Exception:
        return []

    rows.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return rows


def _recent_failures(history: List[Dict[str, Any]], days: int = 30) -> Dict[str, int]:
    """Count recent failures per channel/action from log history.

    A failed row is attributed to email unless the error explicitly mentions
    instagram. This captures bounces, quota errors, and missing-email cases.
    """
    cutoff = datetime.now() - timedelta(days=days)
    failures: Dict[str, int] = {"email": 0, "instagram": 0}
    for row in history:
        try:
            ts = datetime.strptime(row.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        if ts < cutoff:
            continue
        if row.get("status") != "failed":
            continue
        error = (row.get("error_message") or "").lower()
        if "instagram" in error or "dm" in error:
            failures["instagram"] += 1
        else:
            failures["email"] += 1
    return failures


def decide_plan(customer: Dict[str, Any], history: Optional[List[Dict[str, Any]]] = None) -> CampaignPlan:
    """Generate a strategy plan for a single customer.

    Combines churn score, contact availability, and recent historical outcomes
    to choose the offer type and channel(s).
    """
    customer_id = customer["customer_id"]
    churn_score = float(customer.get("churn_score") or 0.0)
    email = (customer.get("email") or "").strip()
    instagram_handle = (customer.get("instagram_handle") or "").strip()

    if history is None:
        history = _read_customer_history(customer_id)

    recent_failures = _recent_failures(history)
    offer_type = _offer_type_from_score(churn_score)
    model = _model_for_offer_type(offer_type)

    # Channel selection with history-aware fallback
    available_channels: List[str] = []
    if email:
        available_channels.append("email")
    if instagram_handle:
        available_channels.append("instagram")

    if not available_channels:
        return CampaignPlan(
            customer_id=customer_id,
            offer_type=offer_type,
            channel="none",
            reasoning="No contact information available; cannot reach customer.",
            model=model,
        )

    # Allow CLI override of the chosen channel.
    channel_override = (customer.get("_planner_channel_override") or "").strip()
    if channel_override and channel_override in available_channels:
        return CampaignPlan(
            customer_id=customer_id,
            offer_type=offer_type,
            channel=channel_override,
            reasoning=(
                f"churn_score={churn_score:.2f} maps to offer_type={offer_type}. "
                f"Channel overridden by operator to {channel_override}."
            ),
            model=model,
        )

    # Prefer email unless it has recent repeated failures.
    channel = "email"
    reasoning_parts = [
        f"churn_score={churn_score:.2f} maps to offer_type={offer_type}.",
    ]

    if "email" in available_channels:
        if recent_failures["email"] >= 2:
            if "instagram" in available_channels:
                channel = "instagram"
                reasoning_parts.append(
                    f"Email has {recent_failures['email']} recent failures; falling back to Instagram DM."
                )
            else:
                reasoning_parts.append(
                    f"Email has {recent_failures['email']} recent failures but no Instagram fallback exists."
                )
        else:
            reasoning_parts.append("Email is available and has no recent repeated failures.")

    if channel == "email" and "instagram" in available_channels and recent_failures["email"] == 0:
        # Optional: use both channels for high-value discount customers.
        if offer_type == "discount":
            channel = "both"
            reasoning_parts.append("High-risk discount customer: using both email and Instagram DM for maximum reach.")

    if channel == "instagram" and "email" not in available_channels:
        reasoning_parts.append("No email available; Instagram DM is the only channel.")

    return CampaignPlan(
        customer_id=customer_id,
        offer_type=offer_type,
        channel=channel,
        reasoning=" ".join(reasoning_parts),
        model=model,
    )


if __name__ == "__main__":
    test_customer = {
        "customer_id": "C001",
        "name": "Ahmed Hassan",
        "email": "ahmed@example.com",
        "instagram_handle": "ahmed_hassan_ig",
        "churn_score": 0.92,
        "days_since_last_contact": 120,
    }
    plan = decide_plan(test_customer)
    print(plan)
