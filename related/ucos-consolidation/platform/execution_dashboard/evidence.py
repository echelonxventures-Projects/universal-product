"""EC2-TASK-000131 — Execution Dashboard Evidence (EC2-EPIC-008).

The deterministic, content-addressed record of the execution-dashboard runtime state
(evidence). It embeds no wall-clock and no ambient state, so an identical runtime state
(the consumed registry fingerprint, the surfaced census, the number of governed views /
searches / access evaluations, and health) yields a byte-identical
:class:`DashboardEvidence` and fingerprint (P5 / Mandatory Rule 6 — every determination
yields evidence). It is *runtime* evidence over the dashboard itself; the request data it
surfaces belongs to the certified Generation Request Runtime (EPIC-007) and is consumed by
reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class DashboardEvidence:
    """A deterministic, content-addressed record of dashboard runtime state (evidence)."""

    registry_fingerprint: str
    request_count: int
    active_count: int
    terminal_count: int
    queue_depth: int
    view_count: int
    search_count: int
    access_evaluation_count: int
    status_census: tuple[tuple[str, int], ...]
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        request_count: int,
        active_count: int,
        terminal_count: int,
        queue_depth: int,
        view_count: int,
        search_count: int,
        access_evaluation_count: int,
        status_census: tuple[tuple[str, int], ...],
        health_status: str,
    ) -> DashboardEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "request_count": request_count,
            "active_count": active_count,
            "terminal_count": terminal_count,
            "queue_depth": queue_depth,
            "view_count": view_count,
            "search_count": search_count,
            "access_evaluation_count": access_evaluation_count,
            "status_census": [list(pair) for pair in status_census],
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            request_count=request_count,
            active_count=active_count,
            terminal_count=terminal_count,
            queue_depth=queue_depth,
            view_count=view_count,
            search_count=search_count,
            access_evaluation_count=access_evaluation_count,
            status_census=status_census,
            health_status=health_status,
            evidence_id=f"UCOS-EDEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "request_count": self.request_count,
            "active_count": self.active_count,
            "terminal_count": self.terminal_count,
            "queue_depth": self.queue_depth,
            "view_count": self.view_count,
            "search_count": self.search_count,
            "access_evaluation_count": self.access_evaluation_count,
            "status_census": {name: count for name, count in self.status_census},
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["DashboardEvidence"]
