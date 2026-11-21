"""EC2-TASK-000147 — Validation Console EC-1 Façade (EC2-EPIC-010).

The **L4 execution façade** — the single component that invokes the certified EC-1
Validation Layer (Program §4.2: "L4 Execution … the only component that invokes EC-1
… calls EC-1's published APIs … ``engine.validation``"). It consumes
``engine.validation`` **by reference**: it binds the published, versioned
:data:`~platform.validation.contracts.ENGINE_VALIDATION_CONTRACT`
(``engine.validation.validate`` v1, present in ``ENGINE_CONTRACTS``) and invokes the
certified, deterministic :class:`~engine.validation.executor.ValidationEngine`
**read-only** over a normalized :class:`~engine.validation.contracts.ValidationSubject`
to reproduce the authoritative :class:`~engine.validation.contracts.ValidationReport`,
:class:`~engine.validation.evidence.ValidationEvidence`, and
:class:`~engine.validation.gates.AcceptanceDecision`.

Because the engine is a **pure, deterministic function** of the subject (IMP-007 §5),
this reproduction is byte-for-byte identical to the engine's own output — the mechanism
by which the console guarantees fidelity (P6). The façade **redefines no check, verdict,
gate, severity, or evidence format** (TP-01); it holds the certified check suite
(``default_checks`` by default) and delegates entirely. It mutates nothing, writes
nothing to the corpus (DP-03), and performs no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import ENGINE_CONTRACTS, ContractRef, content_hash
from platform.validation.contracts import ENGINE_VALIDATION_CONTRACT
from platform.validation.errors import ValidationFidelityError
from typing import Any

from engine.validation.contracts import ValidationReport, ValidationSubject
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The certified EC-1 validation contract reference the façade binds to (by reference).
VALIDATION_ENGINE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ref for ref in ENGINE_CONTRACTS if ref.name == ENGINE_VALIDATION_CONTRACT
)


@dataclass(frozen=True, slots=True)
class SurfacedValidation:
    """The immutable bundle produced by a read-only engine reproduction.

    Carries the certified :class:`ValidationReport`, :class:`ValidationEvidence`,
    :class:`AcceptanceDecision`, and the :class:`ValidationSubject` they were derived
    from, plus the ``engine_contract`` reference that produced them. It re-derives
    nothing itself — it is the faithful projection the console records.
    """

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision
    subject: ValidationSubject
    engine_contract: str

    def report_fingerprint(self) -> str:
        return content_hash(self.report.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine_contract": self.engine_contract,
            "report": self.report.to_dict(),
            "evidence": self.evidence.to_dict(),
            "decision": self.decision.to_dict(),
            "subject": self.subject.to_dict(),
        }


class ValidationFacade:
    """The read-only EC-1 validation façade (consumes ``engine.validation`` by reference)."""

    __slots__ = ("_engine",)

    def __init__(self, engine: ValidationEngine | None = None) -> None:
        if engine is not None and not isinstance(engine, ValidationEngine):
            raise ValidationFidelityError(
                "ValidationFacade requires an engine.validation ValidationEngine"
            )
        # Bind the certified engine (default suite) — never a re-implemented one.
        self._engine = engine if engine is not None else ValidationEngine()

    @property
    def engine_contract(self) -> str:
        """The certified EC-1 validation contract name this façade binds to."""
        return ENGINE_VALIDATION_CONTRACT

    @property
    def engine_contracts(self) -> tuple[ContractRef, ...]:
        """The certified EC-1 validation contract references (by reference)."""
        return VALIDATION_ENGINE_CONTRACTS

    def check_ids(self) -> tuple[str, ...]:
        """The stable ids of the certified checks the bound engine runs."""
        return self._engine.check_ids

    def reproduce(self, subject: ValidationSubject) -> ValidationReport:
        """Reproduce the certified :class:`ValidationReport` for ``subject`` (read-only)."""
        if not isinstance(subject, ValidationSubject):
            raise ValidationFidelityError("reproduce requires a ValidationSubject")
        return self._engine.validate(subject)

    def surface(self, subject: ValidationSubject) -> SurfacedValidation:
        """Reproduce the certified report/evidence/decision for ``subject`` (fidelity, P6).

        Invokes the certified engine read-only; assembles evidence and the acceptance
        decision through the certified builders. Re-derives no verdict of its own.
        """
        report = self.reproduce(subject)
        evidence = build_validation_evidence(report)
        decision = enforce_acceptance(report)
        return SurfacedValidation(
            report=report,
            evidence=evidence,
            decision=decision,
            subject=subject,
            engine_contract=ENGINE_VALIDATION_CONTRACT,
        )

    def verify_fidelity(self, report: ValidationReport, subject: ValidationSubject) -> bool:
        """True iff re-running the certified engine over ``subject`` reproduces ``report``.

        The machine-checkable fidelity predicate (P6): a stored report is faithful iff a
        fresh certified reproduction over the same subject yields a byte-identical report.
        """
        if not isinstance(report, ValidationReport):
            raise ValidationFidelityError("verify_fidelity requires a ValidationReport")
        reproduced = self.reproduce(subject)
        return content_hash(reproduced.to_dict()) == content_hash(report.to_dict())


__all__ = [
    "VALIDATION_ENGINE_CONTRACTS",
    "SurfacedValidation",
    "ValidationFacade",
]
