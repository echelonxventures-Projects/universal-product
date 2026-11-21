"""EPIC-VAL-002 — Repository Readiness report (Terminal T3).

The **Repository Readiness** report is the acceptance engine's freeze-readiness
attestation: a deterministic, content-addressed summary derived purely from an
:class:`~engine.acceptance.engine.AcceptanceDecision`. It renders the per-gate
status map, the aggregate acceptance verdict, and a **freeze verdict** — a
repository is freeze-ready iff acceptance is fail-closed ACCEPTED (every blocking
gate, including the 100% coverage and freeze-readiness gates, passed).

The report embeds no wall-clock or ambient state, so the same decision yields a
byte-identical readiness report. It asserts ``ENGINEERING-EXECUTION-ONLY`` authority
and carries the EC-1 provisional-state disclosure — readiness records engineering
readiness only, not constitutional finality (DE-05 / IP-01).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.acceptance.contracts import (
    ACCEPTANCE_AUTHORITY,
    content_hash,
)
from engine.acceptance.engine import AcceptanceDecision
from engine.foundation.contracts.disclosure import build_disclosure
from engine.foundation.obs.logging import get_logger

_logger = get_logger("acceptance.readiness")

#: The repository-readiness report format identifier.
READINESS_FORMAT = "ucos-repository-readiness/1.0.0"

READY = "READY"
NOT_READY = "NOT-READY"


@dataclass(frozen=True, slots=True)
class RepositoryReadiness:
    """A deterministic, content-addressed repository freeze-readiness report."""

    repository_id: str
    epic_id: str
    acceptance_id: str
    accepted: bool
    freeze_ready: bool
    verdict: str
    gates_total: int
    gates_passed: int
    gate_status: dict[str, str]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    authority: str
    disclosure: dict[str, Any]
    readiness_sha256: str

    @property
    def ready(self) -> bool:
        return self.verdict == READY

    def _core(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "acceptance_id": self.acceptance_id,
            "accepted": self.accepted,
            "freeze_ready": self.freeze_ready,
            "verdict": self.verdict,
            "gates_total": self.gates_total,
            "gates_passed": self.gates_passed,
            "gate_status": dict(self.gate_status),
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "readiness_format": READINESS_FORMAT,
            **self._core(),
            "readiness_sha256": self.readiness_sha256,
        }


def build_repository_readiness(decision: AcceptanceDecision) -> RepositoryReadiness:
    """Assemble the freeze-readiness report from an acceptance decision."""
    gate_status = {f.gate_id: f.status.value for f in decision.findings}
    gates_passed = sum(1 for f in decision.findings if f.passed)
    freeze_ready = decision.accepted
    verdict = READY if freeze_ready else NOT_READY

    core = {
        "repository_id": decision.repository_id,
        "epic_id": decision.epic_id,
        "acceptance_id": decision.acceptance_id,
        "accepted": decision.accepted,
        "freeze_ready": freeze_ready,
        "verdict": verdict,
        "gates_total": len(decision.findings),
        "gates_passed": gates_passed,
        "gate_status": dict(gate_status),
        "blocking_failures": list(decision.blocking_failures),
        "advisory_failures": list(decision.advisory_failures),
        "authority": ACCEPTANCE_AUTHORITY,
        "disclosure": build_disclosure(),
    }
    readiness_sha256 = content_hash(core)

    report = RepositoryReadiness(
        repository_id=decision.repository_id,
        epic_id=decision.epic_id,
        acceptance_id=decision.acceptance_id,
        accepted=decision.accepted,
        freeze_ready=freeze_ready,
        verdict=verdict,
        gates_total=len(decision.findings),
        gates_passed=gates_passed,
        gate_status=dict(gate_status),
        blocking_failures=tuple(decision.blocking_failures),
        advisory_failures=tuple(decision.advisory_failures),
        authority=ACCEPTANCE_AUTHORITY,
        disclosure=build_disclosure(),
        readiness_sha256=readiness_sha256,
    )
    _logger.info(
        "acceptance.readiness.built",
        repository=decision.repository_id,
        verdict=verdict,
        gates_passed=gates_passed,
        gates_total=len(decision.findings),
    )
    return report


__all__ = [
    "READINESS_FORMAT",
    "READY",
    "NOT_READY",
    "RepositoryReadiness",
    "build_repository_readiness",
]
