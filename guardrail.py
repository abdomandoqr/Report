#!/usr/bin/env python3
"""Output guardrail for generated offers.

Catches malformed, incomplete, or off-strategy offers before any send.
This is the minimal safety/reviewer layer in the agentic workflow.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from planner import CampaignPlan


class GuardrailResult:
    """Result of guardrail validation."""

    def __init__(self, passed: bool, reasons: Optional[List[str]] = None):
        self.passed = passed
        self.reasons = reasons or []

    def __bool__(self) -> bool:
        return self.passed

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"GuardrailResult({status}, reasons={self.reasons})"


def _has_required_keys(offer: Dict[str, Any]) -> List[str]:
    """Return missing required keys, if any."""
    required = {"offer_type", "offer_title", "offer_details", "cta_text"}
    missing = sorted(required - set(offer.keys()))
    return [f"Missing required key: {k}" for k in missing]


def _offer_type_matches_plan(offer: Dict[str, Any], plan: CampaignPlan) -> List[str]:
    """Ensure generated offer type matches the planner decision."""
    offer_type = offer.get("offer_type", "")
    if offer_type != plan.offer_type:
        return [f"Offer type mismatch: got {offer_type!r}, expected {plan.offer_type!r}"]
    return []


def _content_quality(offer: Dict[str, Any]) -> List[str]:
    """Basic content-length and placeholder checks."""
    reasons: List[str] = []

    title = str(offer.get("offer_title", "")).strip()
    details = str(offer.get("offer_details", "")).strip()
    cta = str(offer.get("cta_text", "")).strip()

    if len(title) < 5:
        reasons.append("Offer title is too short.")
    if len(details) < 20:
        reasons.append("Offer details are too short.")
    if len(cta) < 2:
        reasons.append("CTA text is too short.")

    placeholders = ["[", "]", "{{", "}}", "TODO", "FIXME", "XXX"]
    combined = (title + " " + details + " " + cta).upper()
    for placeholder in placeholders:
        if placeholder in combined:
            reasons.append(f"Placeholder text detected: {placeholder}")

    return reasons


def validate_offer(offer: Dict[str, Any], plan: CampaignPlan) -> GuardrailResult:
    """Validate an offer against the campaign plan.

    Returns a GuardrailResult. If validation fails, reasons list explains why.
    """
    reasons: List[str] = []
    reasons.extend(_has_required_keys(offer))
    if not reasons:  # only check type match if keys are present
        reasons.extend(_offer_type_matches_plan(offer, plan))
    reasons.extend(_content_quality(offer))

    if reasons:
        return GuardrailResult(passed=False, reasons=reasons)
    return GuardrailResult(passed=True)


if __name__ == "__main__":
    from planner import CampaignPlan
    plan = CampaignPlan(
        customer_id="C001",
        offer_type="discount",
        channel="email",
        reasoning="test",
    )
    good_offer = {
        "offer_type": "discount",
        "offer_title": "Welcome back — 25% off just for you",
        "offer_details": "Hi Ahmed, it's been 120 days since your last visit. We miss you! Enjoy 25% off your next purchase.",
        "cta_text": "Claim My Discount",
    }
    print(validate_offer(good_offer, plan))

    bad_offer = {
        "offer_type": "bonus_points",
        "offer_title": "Hi",
        "offer_details": "Short.",
        "cta_text": "",
    }
    print(validate_offer(bad_offer, plan))
