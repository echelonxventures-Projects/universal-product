"""UCOS-CTRL-000001 — Intelligence Engines.

Three engines that measure, track, and surface execution health:

    ProgressEngine  — measures progress for any subject (universe, milestone, …)
    MetricsEngine   — records and aggregates named scalar metrics
    DashboardEngine — produces a unified state snapshot of all control-plane
                      engines for display or export
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from platform.universal_control_plane.ontology import (
    LIFECYCLE_ACTIVE,
    LIFECYCLE_COMPLETE,
    BacklogItem,
    Metric,
    ProgressRecord,
)
from typing import Any


def _mid(subject_id: str, name: str, tick: int) -> str:
    payload = {"s": subject_id, "n": name, "t": tick}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "MET-" + hashlib.sha256(blob.encode()).hexdigest()[:12]


def _prid(subject_id: str, tick: int) -> str:
    blob = json.dumps({"s": subject_id, "t": tick}, sort_keys=True, separators=(",", ":"))
    return "PRG-" + hashlib.sha256(blob.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Progress Engine
# ---------------------------------------------------------------------------


@dataclass
class ProgressEngine:
    """Measures and records progress for arbitrary subjects."""

    _records: dict[str, list[ProgressRecord]] = field(default_factory=dict)

    def measure(
        self,
        subject_id: str,
        items: list[BacklogItem],
        *,
        tick: int = 0,
    ) -> ProgressRecord:
        """Derive a ProgressRecord from the current state of *items*."""
        total = len(items)
        completed = sum(1 for i in items if i.state == LIFECYCLE_COMPLETE)
        record = ProgressRecord(
            record_id=_prid(subject_id, tick),
            subject_id=subject_id,
            total=total,
            completed=completed,
            state=LIFECYCLE_ACTIVE,
            tick=tick,
        )
        self._records.setdefault(subject_id, []).append(record)
        return record

    def measure_counts(
        self,
        subject_id: str,
        *,
        total: int,
        completed: int,
        tick: int = 0,
    ) -> ProgressRecord:
        """Record progress from counts a caller already measured.

        The counterpart of :meth:`measure` for populations that are not backlog
        items — governed objects, certified engines, closed linkages. Without it a
        caller would have to fabricate a list of items it does not have just to
        report a ratio it does.
        """
        if total < 0 or completed < 0:
            raise ValueError("progress counts must be non-negative")
        if completed > total:
            raise ValueError(
                f"completed ({completed}) cannot exceed total ({total}) for {subject_id!r}"
            )
        record = ProgressRecord(
            record_id=_prid(subject_id, tick),
            subject_id=subject_id,
            total=total,
            completed=completed,
            state=LIFECYCLE_ACTIVE,
            tick=tick,
        )
        self._records.setdefault(subject_id, []).append(record)
        return record

    def latest(self, subject_id: str) -> ProgressRecord | None:
        history = self._records.get(subject_id, [])
        return history[-1] if history else None

    def history(self, subject_id: str) -> list[ProgressRecord]:
        return list(self._records.get(subject_id, []))

    def all_subjects(self) -> list[str]:
        return sorted(self._records)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "ProgressEngine",
            "subjects": self.all_subjects(),
            "records": {
                sid: [r.to_dict() for r in records] for sid, records in self._records.items()
            },
        }


# ---------------------------------------------------------------------------
# Metrics Engine
# ---------------------------------------------------------------------------


@dataclass
class MetricsEngine:
    """Records scalar metrics and computes aggregates."""

    _metrics: dict[str, list[Metric]] = field(default_factory=dict)

    def record(
        self,
        subject_id: str,
        name: str,
        value: float,
        *,
        unit: str = "",
        tick: int = 0,
    ) -> Metric:
        metric = Metric(
            metric_id=_mid(subject_id, name, tick),
            subject_id=subject_id,
            name=name,
            value=value,
            unit=unit,
            tick=tick,
        )
        key = f"{subject_id}::{name}"
        self._metrics.setdefault(key, []).append(metric)
        return metric

    def latest(self, subject_id: str, name: str) -> Metric | None:
        series = self._metrics.get(f"{subject_id}::{name}", [])
        return series[-1] if series else None

    def series(self, subject_id: str, name: str) -> list[Metric]:
        return list(self._metrics.get(f"{subject_id}::{name}", []))

    def aggregate(self, subject_id: str, name: str) -> dict[str, float]:
        data = [m.value for m in self.series(subject_id, name)]
        if not data:
            return {}
        return {
            "count": float(len(data)),
            "min": min(data),
            "max": max(data),
            "sum": sum(data),
            "mean": round(sum(data) / len(data), 6),
        }

    def subjects(self) -> list[str]:
        seen: set[str] = set()
        for key in self._metrics:
            sid, _ = key.split("::", 1)
            seen.add(sid)
        return sorted(seen)

    def metric_names(self, subject_id: str) -> list[str]:
        prefix = f"{subject_id}::"
        return sorted(key[len(prefix) :] for key in self._metrics if key.startswith(prefix))

    def count(self) -> int:
        return sum(len(v) for v in self._metrics.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "MetricsEngine",
            "total_records": self.count(),
            "subjects": self.subjects(),
            "series": {key: [m.to_dict() for m in series] for key, series in self._metrics.items()},
        }


# ---------------------------------------------------------------------------
# Dashboard Engine
# ---------------------------------------------------------------------------


@dataclass
class DashboardEngine:
    """Produces a unified state snapshot of all control-plane engines."""

    def snapshot(
        self,
        *,
        plan_dict: dict[str, Any] | None = None,
        roadmap_dict: dict[str, Any] | None = None,
        backlog_dict: dict[str, Any] | None = None,
        schedule_dict: dict[str, Any] | None = None,
        assignment_dict: dict[str, Any] | None = None,
        progress_dict: dict[str, Any] | None = None,
        metrics_dict: dict[str, Any] | None = None,
        registry_dicts: list[dict[str, Any]] | None = None,
        tick: int = 0,
    ) -> dict[str, Any]:
        """Assemble all engine summaries into one dashboard payload."""
        dash: dict[str, Any] = {
            "dashboard": "UCOS-CTRL-000001",
            "tick": tick,
        }
        if plan_dict:
            dash["plan"] = {
                "visions": plan_dict.get("visions", 0),
                "goals": plan_dict.get("goals", 0),
                "objectives": plan_dict.get("objectives", 0),
                "completion_rate": plan_dict.get("completion_rate", 0.0),
            }
        if roadmap_dict:
            dash["roadmap"] = {
                "total_milestones": roadmap_dict.get("total_milestones", 0),
            }
        if backlog_dict:
            dash["backlog"] = {
                "count": backlog_dict.get("count", 0),
                "total_estimate": backlog_dict.get("total_estimate", 0),
            }
        if schedule_dict:
            dash["schedule"] = {
                "wave_count": schedule_dict.get("wave_count", 0),
                "total_entries": schedule_dict.get("total_entries", 0),
            }
        if assignment_dict:
            dash["assignments"] = {
                "total": assignment_dict.get("total", 0),
                "active": assignment_dict.get("active", 0),
            }
        if progress_dict:
            dash["progress"] = {
                "subjects": progress_dict.get("subjects", []),
            }
        if metrics_dict:
            dash["metrics"] = {
                "total_records": metrics_dict.get("total_records", 0),
                "subjects": metrics_dict.get("subjects", []),
            }
        if registry_dicts:
            dash["registries"] = [
                {"name": rd.get("registry", "?"), "count": rd.get("count", 0)}
                for rd in registry_dicts
            ]
        return dash
