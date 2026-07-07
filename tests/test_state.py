"""Tests for the campaign state machine and persistence."""
import json
from pathlib import Path

import pytest

from state import CampaignState, CampaignStatus, StateStore


@pytest.fixture
def temp_store(tmp_path):
    return StateStore(path=tmp_path / "campaign_state.json")


def test_state_transition_updates_status_and_timestamp(temp_store):
    state = temp_store.get_or_create("C001")
    assert state.status == CampaignStatus.QUEUED

    planned = state.transition(CampaignStatus.PLANNED, plan={"offer_type": "discount"})
    assert planned.status == CampaignStatus.PLANNED
    assert planned.plan == {"offer_type": "discount"}
    assert planned.updated_at >= state.updated_at


def test_store_persists_and_reloads(temp_store):
    state = temp_store.get_or_create("C002")
    state = state.transition(CampaignStatus.SENT, send_result={"success": True})
    temp_store.update(state)

    reloaded = StateStore(path=temp_store.path)
    loaded_state = reloaded.get("C002")
    assert loaded_state is not None
    assert loaded_state.status == CampaignStatus.SENT
    assert loaded_state.send_result == {"success": True}


def test_store_summary_counts(temp_store):
    temp_store.get_or_create("C003")
    s = temp_store.get_or_create("C004")
    temp_store.update(s.transition(CampaignStatus.SENT))

    summary = temp_store.summary()
    assert summary[CampaignStatus.QUEUED.value] == 1
    assert summary[CampaignStatus.SENT.value] == 1


def test_store_corrupt_file_starts_fresh(tmp_path):
    path = tmp_path / "corrupt.json"
    path.write_text("not valid json", encoding="utf-8")
    store = StateStore(path=path)
    assert store.get("x") is None
