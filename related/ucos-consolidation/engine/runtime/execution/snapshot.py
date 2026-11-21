"""EPIC-RTE-002 — Execution Snapshot (Runtime Execution Platform).

Realises **Execution Snapshot**: a single, immutable, point-in-time capture of the
*complete observable state* of an :class:`~engine.runtime.execution.coordinator.ExecutionRun`
— its per-universe states, audit trail, monitor, metrics, health, and diagnostics —
in one deterministic, JSON-serialisable object. A snapshot reuses the observability
views verbatim (monitoring/metrics/health/diagnostics) and adds no new derivation.

A snapshot differs from a :class:`~engine.runtime.execution.checkpoint.Checkpoint`:
a checkpoint is the minimal, *resumable* subset needed to continue; a snapshot is
the full, *observable* capture used for persistence and forensic replay. It records
state; it changes nothing (RUNTIME-013 ORL-15) and is deterministic (ORL-20).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.diagnostics import diagnose
from engine.runtime.execution.health import health
from engine.runtime.execution.metrics import execution_metrics
from engine.runtime.execution.monitoring import monitor

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.execution.coordinator import ExecutionRun

_logger = get_logger("runtime.execution.snapshot")

#: The recorded snapshot format.
SNAPSHOT_FORMAT = "ucos-execution-snapshot/1.0.0"


@dataclass(frozen=True, slots=True)
class Snapshot:
    """An immutable, deterministic, full-observability capture of a run."""

    snapshot_id: str
    run_id: str
    composition_id: str
    status: str
    run: dict[str, Any]
    monitor: dict[str, Any]
    metrics: dict[str, Any]
    health: dict[str, Any]
    diagnostics: dict[str, Any]
    disclosure: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_format": SNAPSHOT_FORMAT,
            "snapshot_id": self.snapshot_id,
            "run_id": self.run_id,
            "composition_id": self.composition_id,
            "status": self.status,
            "run": self.run,
            "monitor": self.monitor,
            "metrics": self.metrics,
            "health": self.health,
            "diagnostics": self.diagnostics,
            "provisional_state_disclosure": self.disclosure,
        }


def snapshot(run: ExecutionRun) -> Snapshot:
    """Capture ``run`` as a full, immutable :class:`Snapshot` (deterministic)."""
    with trace("runtime.execution.snapshot", run=run.run_id):
        run_view = run.to_dict()
        monitor_view = monitor(run).to_dict()
        metrics_view = execution_metrics(run).to_dict()
        health_view = health(run).to_dict()
        diagnostics_view = diagnose(run).to_dict()
        snap = Snapshot(
            snapshot_id=_snapshot_id(run.run_id, run.status),
            run_id=run.run_id,
            composition_id=run.composition_id,
            status=run.status,
            run=run_view,
            monitor=monitor_view,
            metrics=metrics_view,
            health=health_view,
            diagnostics=diagnostics_view,
            disclosure=run.disclosure,
        )
    _logger.info(
        "runtime.execution.snapshotted",
        snapshot_id=snap.snapshot_id,
        run=run.run_id,
    )
    return snap


def _snapshot_id(run_id: str, status: str) -> str:
    digest = hashlib.sha256(f"{run_id}||status={status}".encode()).hexdigest()
    return f"UCOS-EXEC-SNAP-{digest[:16]}"


__all__ = ["SNAPSHOT_FORMAT", "Snapshot", "snapshot"]
