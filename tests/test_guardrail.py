"""Tests for the offer guardrail."""
import pytest

from guardrail import GuardrailResult, validate_offer
from planner import CampaignPlan


@pytest.fixture
def discount_plan():
    return CampaignPlan(
        customer_id="C001",
        offer_type="discount",
        channel="email",
        reasoning="test plan",
    )


def test_valid_offer_passes(discount_plan):
    offer = {
        "offer_type": "discount",
        "offer_title": "Welcome back — 25% off just for you",
        "offer_details": "Hi Ahmed, it's been 120 days since your last visit. We miss you! Enjoy 25% off your next purchase.",
        "cta_text": "Claim My Discount",
    }
    result = validate_offer(offer, discount_plan)
    assert result.passed is True
    assert not result.reasons


def test_missing_keys_fails(discount_plan):
    offer = {
        "offer_type": "discount",
        "offer_title": "Welcome back",
    }
    result = validate_offer(offer, discount_plan)
    assert result.passed is False
    assert any("Missing required key" in r for r in result.reasons)


def test_offer_type_mismatch_fails(discount_plan):
    offer = {
        "offer_type": "bonus_points",
        "offer_title": "Welcome back — 25% off just for you",
        "offer_details": "Some details here that are long enough to pass.",
        "cta_text": "Claim",
    }
    result = validate_offer(offer, discount_plan)
    assert result.passed is False
    assert any("mismatch" in r for r in result.reasons)


def test_short_content_fails(discount_plan):
    offer = {
        "offer_type": "discount",
        "offer_title": "Hi",
        "offer_details": "Short.",
        "cta_text": "",
    }
    result = validate_offer(offer, discount_plan)
    assert result.passed is False
    assert any("too short" in r for r in result.reasons)


def test_placeholder_detected(discount_plan):
    offer = {
        "offer_type": "discount",
        "offer_title": "Welcome back TODO",
        "offer_details": "Some details here that are long enough to pass the length check.",
        "cta_text": "Claim",
    }
    result = validate_offer(offer, discount_plan)
    assert result.passed is False
    assert any("Placeholder" in r for r in result.reasons)


def test_guardrail_result_bool(discount_plan):
    offer = {
        "offer_type": "discount",
        "offer_title": "Welcome back — 25% off just for you",
        "offer_details": "Hi Ahmed, it's been 120 days since your last visit. We miss you! Enjoy 25% off your next purchase.",
        "cta_text": "Claim My Discount",
    }
    assert bool(validate_offer(offer, discount_plan)) is True
