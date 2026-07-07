"""Tests for the strategy planner."""
from pathlib import Path

import pytest

from planner import CampaignPlan, decide_plan


@pytest.fixture
def base_customer():
    return {
        "customer_id": "C001",
        "name": "Ahmed Hassan",
        "email": "ahmed@example.com",
        "instagram_handle": "ahmed_hassan_ig",
        "churn_score": 0.85,
        "days_since_last_contact": 120,
    }


def test_offer_type_from_churn_score(base_customer):
    base_customer["churn_score"] = 0.75
    plan = decide_plan(base_customer, history=[])
    assert plan.offer_type == "informational"

    base_customer["churn_score"] = 0.85
    plan = decide_plan(base_customer, history=[])
    assert plan.offer_type == "bonus_points"

    base_customer["churn_score"] = 0.95
    plan = decide_plan(base_customer, history=[])
    assert plan.offer_type == "discount"


def test_channel_defaults_to_email(base_customer):
    plan = decide_plan(base_customer, history=[])
    assert plan.channel == "email"
    assert "Email is available" in plan.reasoning


def test_channel_fallback_to_instagram_after_email_failures(base_customer):
    history = [
        {"timestamp": "2026-06-25 10:00:00", "customer_id": "C001", "action_taken": "SENT_WINBACK_OFFER", "status": "failed", "error_message": "email bounced"},
        {"timestamp": "2026-06-26 10:00:00", "customer_id": "C001", "action_taken": "SENT_WINBACK_OFFER", "status": "failed", "error_message": "email bounced"},
    ]
    plan = decide_plan(base_customer, history=history)
    assert plan.channel == "instagram"
    assert "Email has 2 recent failures" in plan.reasoning


def test_high_risk_uses_both_channels(base_customer):
    base_customer["churn_score"] = 0.95
    plan = decide_plan(base_customer, history=[])
    assert plan.channel == "both"
    assert "both email and Instagram" in plan.reasoning


def test_no_contact_info_returns_none_channel(base_customer):
    base_customer["email"] = ""
    base_customer["instagram_handle"] = ""
    plan = decide_plan(base_customer, history=[])
    assert plan.channel == "none"


def test_instagram_only_when_email_missing(base_customer):
    base_customer["email"] = ""
    plan = decide_plan(base_customer, history=[])
    assert plan.channel == "instagram"


def test_model_matches_offer_type(base_customer):
    base_customer["churn_score"] = 0.75
    plan = decide_plan(base_customer, history=[])
    assert "haiku" in plan.model.lower()

    base_customer["churn_score"] = 0.95
    plan = decide_plan(base_customer, history=[])
    assert "sonnet" in plan.model.lower()
