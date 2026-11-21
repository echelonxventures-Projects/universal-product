"""EPIC-RTE-002 — Execution Diagnostics (Runtime Execution Platform).

Realises **Execution Diagnostics**: a deterministic, actionable report over an
:class:`~engine.runtime.execution.coordinator.ExecutionRun` that explains *why* a
run is not fully healthy — which universes failed, and which were skipped and by
which unmet dependency (blocked propagation). Diagnostics derive purely from the
run's recorded states and each universe's declared dependencies (no ambient state,
ORL-20). They observe and explain; they change nothing (RUNTIME-013 ORL-15).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.runtime.execution.state import COMPLETED, FAILED, SKIPPED

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.execution.coordinator import ExecutionRun

#: The recorded diagnostics format.
DIAGNOSTICS_FORMAT = "ucos-execution-diagnostics/1.0.0"


@dataclass(frozen=True, slots=True)
class Finding:
    """One diagnostic finding about a single universe (non-secret, auditable)."""

    universe_id: str
    status: str
    reason: str
    blocked_by: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "universe_id": self.universe_id,
            "status": self.status,
            "reason": self.reason,
            "blocked_by": list(self.blocked_by),
        }


@dataclass(frozen=True, slots=True)
class ExecutionDiagnostics:
    """A deterministic diagnostic report over a run (a pure observation)."""

    run_id: str
    status: str
    findings: tuple[Finding, ...]

    @property
    def clean(self) -> bool:
        """True iff the run produced no adverse findings."""
        return not self.findings

    def to_dict(self) -> dict[str, Any]:
        return {
            "diagnostics_format": DIAGNOSTICS_FORMAT,
            "run_id": self.run_id,
            "status": self.status,
            "clean": self.clean,
            "finding_count": len(self.findings),
            "findings": [finding.to_dict() for finding in self.findings],
        }


def diagnose(run: ExecutionRun) -> ExecutionDiagnostics:
    """Produce a deterministic :class:`ExecutionDiagnostics` report for ``run``."""
    state_map = run.state_map()
    findings: list[Finding] = []
    for state in run.states:
        if state.status == FAILED:
            findings.append(
                Finding(
                    universe_id=state.universe_id,
                    status=FAILED,
                    reason="modelled execution failed",
                )
            )
        elif state.status == SKIPPED:
            blockers = tuple(
                dependency
                for dependency in state.depends_on
                if state_map[dependency].status != COMPLETED
            )
            reason = (
                "skipped because a dependency did not complete"
                if blockers
                else "skipped by operator request"
            )
            findings.append(
                Finding(
                    universe_id=state.universe_id,
                    status=SKIPPED,
                    reason=reason,
                    blocked_by=blockers,
                )
            )
    findings.sort(key=lambda f: f.universe_id)
    return ExecutionDiagnostics(run_id=run.run_id, status=run.status, findings=tuple(findings))


__all__ = [
    "DIAGNOSTICS_FORMAT",
    "Finding",
    "ExecutionDiagnostics",
    "diagnose",
]
