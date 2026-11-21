"""EPIC-VAL-002 — Repository Acceptance decision (Terminal T3).

The :class:`AcceptanceEngine` runs a suite of gates over an assimilated
:class:`~engine.acceptance.contracts.RepositorySubject` and aggregates the findings
into a deterministic :class:`AcceptanceDecision` that carries an **immutable,
content-addressed** :class:`~engine.acceptance.contracts.AcceptanceRecord` — the
Repository Acceptance Certificate.

The decision is *fail-closed*: the status is **ACCEPTED** iff **no blocking gate
failed**; any blocking failure yields **REJECTED**. Nothing is accepted without this
engine. Execution is deterministic (IMP-007 §5): gates run in stable id order and
the record embeds no wall-clock or ambient state, so an identical subject yields a
byte-identical decision, record, and ``acceptance_id`` (reproducible acceptance).

:func:`enforce_acceptance` turns a decision into a hard gate — in ``strict`` mode a
rejected repository raises :class:`~engine.acceptance.errors.AcceptanceRejectedError`
carrying the failing gates as evidence.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from engine.acceptance.contracts import (
    AcceptanceFinding,
    AcceptanceRecord,
    AcceptanceStatus,
    RepositorySubject,
)
from engine.acceptance.errors import AcceptanceRejectedError
from engine.acceptance.gates import AcceptanceGate, default_gates
from engine.foundation.contracts.disclosure import build_disclosure
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("acceptance.engine")


@dataclass(frozen=True, slots=True)
class AcceptanceDecision:
    """The immutable outcome of an acceptance run over a repository subject."""

    repository_id: str
    epic_id: str
    status: AcceptanceStatus
    record: AcceptanceRecord
    findings: tuple[AcceptanceFinding, ...]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]

    @property
    def accepted(self) -> bool:
        return self.status is AcceptanceStatus.ACCEPTED

    @property
    def acceptance_id(self) -> str:
        return self.record.acceptance_id

    @property
    def evidence_ref(self) -> str:
        return self.record.evidence_ref

    def counts(self) -> dict[str, int]:
        passed = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": passed,
            "failed": len(self.findings) - passed,
            "blocking_failed": len(self.blocking_failures),
            "advisory_failed": len(self.advisory_failures),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "status": self.status.value,
            "accepted": self.accepted,
            "acceptance_id": self.acceptance_id,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "record": self.record.to_dict(),
        }


class AcceptanceEngine:
    """Runs a deterministic suite of gates and issues a fail-closed acceptance."""

    __slots__ = ("_gates",)

    def __init__(self, gates: Iterable[AcceptanceGate] | None = None) -> None:
        selected = tuple(gates) if gates is not None else default_gates()
        # Stable id order guarantees deterministic finding ordering.
        self._gates = tuple(sorted(selected, key=lambda g: g.gate_id))

    @property
    def gate_ids(self) -> tuple[str, ...]:
        return tuple(g.gate_id for g in self._gates)

    def accept(self, subject: RepositorySubject) -> AcceptanceDecision:
        """Evaluate every gate over ``subject`` and issue a decision + certificate."""
        with trace("acceptance.accept", repository=subject.repository_id):
            findings = tuple(g.evaluate(subject) for g in self._gates)
            blocking = tuple(f.gate_id for f in findings if f.is_blocking_failure)
            advisory = tuple(
                f.gate_id
                for f in findings
                if f.status.value == "fail" and not f.is_blocking_failure
            )
            status = AcceptanceStatus.REJECTED if blocking else AcceptanceStatus.ACCEPTED
            record = AcceptanceRecord.create(
                repository_id=subject.repository_id,
                epic_id=subject.epic_id,
                status=status,
                evidence_ref=subject.digest(),
                gates=findings,
                disclosure=build_disclosure(),
            )
            decision = AcceptanceDecision(
                repository_id=subject.repository_id,
                epic_id=subject.epic_id,
                status=status,
                record=record,
                findings=findings,
                blocking_failures=blocking,
                advisory_failures=advisory,
            )
        _logger.info(
            "acceptance.decided",
            repository=subject.repository_id,
            acceptance_id=record.acceptance_id,
            status=status.value,
            blocking_failed=len(blocking),
        )
        return decision


def accept_repository(
    subject: RepositorySubject | Mapping[str, Any],
    *,
    gates: Iterable[AcceptanceGate] | None = None,
) -> AcceptanceDecision:
    """Convenience: accept a subject (or a raw facts mapping) with the given suite."""
    if isinstance(subject, Mapping):
        subject = RepositorySubject.from_mapping(subject)
    return AcceptanceEngine(gates).accept(subject)


def enforce_acceptance(decision: AcceptanceDecision, *, strict: bool = False) -> AcceptanceDecision:
    """Return ``decision``; in strict mode raise when the repository is rejected.

    Raises:
        AcceptanceRejectedError: when ``strict`` and the repository is not accepted —
            carrying the exact blocking gate ids as evidence (every rejection is
            auditable, fail-closed).
    """
    if strict and not decision.accepted:
        raise AcceptanceRejectedError(
            "repository acceptance gate rejected the repository",
            repository_id=decision.repository_id,
            epic_id=decision.epic_id,
            blocking_failures=list(decision.blocking_failures),
        )
    return decision


__all__ = [
    "AcceptanceDecision",
    "AcceptanceEngine",
    "accept_repository",
    "enforce_acceptance",
]
