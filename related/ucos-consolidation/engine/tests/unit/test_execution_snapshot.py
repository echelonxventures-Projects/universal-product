"""EPIC-RTE-002 — Execution Snapshot unit tests."""

from __future__ import annotations

import json

from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.snapshot import SNAPSHOT_FORMAT, snapshot


def test_snapshot_captures_full_observability(composition):
    snap = snapshot(coordinate(composition))
    assert snap.snapshot_id.startswith("UCOS-EXEC-SNAP-")
    assert snap.run["run_id"] == snap.run_id
    assert snap.monitor["is_complete"] is True
    assert snap.metrics["total"] == 4
    assert snap.health["health"] == "healthy"
    assert snap.diagnostics["clean"] is True
    assert snap.disclosure["gate"] == "EC-1"


def test_snapshot_to_dict(composition):
    blob = snapshot(coordinate(composition)).to_dict()
    assert blob["snapshot_format"] == SNAPSHOT_FORMAT
    assert "run" in blob and "monitor" in blob and "metrics" in blob


def test_snapshot_is_deterministic(composition):
    a = snapshot(coordinate(composition))
    b = snapshot(coordinate(composition))
    assert a.snapshot_id == b.snapshot_id
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)
