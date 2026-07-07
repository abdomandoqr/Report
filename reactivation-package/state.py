#!/usr/bin/env python3
"""Campaign state machine + JSON-backed persistence for the reactivation workflow.

This module turns each customer campaign into a stateful job that can be
paused, retried, and inspected. It is the minimal agentic lift over the
previous deterministic for-loop.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import config

STATE_PATH = Path(config.SYSTEM_LOG_PATH).parent / "campaign_state.json"


class CampaignStatus(str, Enum):
    """Finite set of campaign states."""

    QUEUED = "queued"
    FETCHED = "fetched"
    PLANNED = "planned"
    GENERATED = "generated"
    GUARDRAIL_PASSED = "guardrail_passed"
    GUARDRAIL_FAILED = "guardrail_failed"
    SENT = "sent"
    FAILED = "failed"
    QUEUED_FOR_TOMORROW = "queued_for_tomorrow"
    SKIPPED = "skipped"
    DONE = "done"


@dataclass
class CampaignState:
    """Snapshot of a single customer's campaign progress."""

    customer_id: str
    status: CampaignStatus = CampaignStatus.QUEUED
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    plan: Optional[Dict[str, Any]] = None
    offer: Optional[Dict[str, Any]] = None
    send_result: Optional[Dict[str, Any]] = None
    error_message: str = ""

    def transition(self, new_status: CampaignStatus, **updates: Any) -> "CampaignState":
        """Return a new state with updated status and optional fields."""
        data = asdict(self)
        data["status"] = new_status
        data["updated_at"] = datetime.now().isoformat()
        for key, value in updates.items():
            if key in data:
                data[key] = value
        return CampaignState(**data)


class StateStore:
    """JSON-backed store for campaign states.

    Uses pretty-printed JSON so operators can inspect it with cat/jq.
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = path or STATE_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._states: Dict[str, CampaignState] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for cid, payload in raw.get("campaigns", {}).items():
                payload["status"] = CampaignStatus(payload["status"])
                self._states[cid] = CampaignState(**payload)
        except Exception:
            # Corrupt state file: start fresh and let the next save overwrite.
            self._states = {}

    def save(self) -> None:
        """Persist current states to disk."""
        payload = {
            "saved_at": datetime.now().isoformat(),
            "campaigns": {
                cid: asdict(state) for cid, state in self._states.items()
            },
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def get(self, customer_id: str) -> Optional[CampaignState]:
        return self._states.get(customer_id)

    def get_or_create(self, customer_id: str) -> CampaignState:
        if customer_id not in self._states:
            self._states[customer_id] = CampaignState(customer_id=customer_id)
            self.save()
        return self._states[customer_id]

    def update(self, state: CampaignState) -> CampaignState:
        self._states[state.customer_id] = state
        self.save()
        return state

    def list_by_status(self, status: CampaignStatus) -> List[CampaignState]:
        return [s for s in self._states.values() if s.status == status]

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for status in CampaignStatus:
            counts[status.value] = 0
        for state in self._states.values():
            counts[state.status.value] += 1
        return counts


if __name__ == "__main__":
    store = StateStore()
    state = store.get_or_create("C999")
    print(f"Initial state: {state}")
    state = state.transition(CampaignStatus.PLANNED, plan={"offer_type": "discount", "channel": "email"})
    store.update(state)
    print(f"Updated state: {state}")
    print("Summary:", store.summary())
