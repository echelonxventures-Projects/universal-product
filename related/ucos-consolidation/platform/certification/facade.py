"""EC2-TASK-000155 — Certification Console EC-1 Façade (EC2-EPIC-011).

The **L4 execution façade** — the single component that invokes the certified EC-1
Certification Layer (Program §4.2: "L4 Execution … the only component that invokes EC-1
… calls EC-1's published APIs … ``engine.certification``"). It consumes
``engine.certification`` **by reference**: it binds the published, versioned
:data:`~platform.certification.contracts.ENGINE_CERTIFICATION_CONTRACT`
(``engine.certification.certify`` v1, present in ``ENGINE_CONTRACTS``) and invokes the
certified, deterministic :class:`~engine.certification.engine.CertificationEngine`
**read-only** over a normalized :class:`~engine.certification.contracts.CertificationSubject`
(projected purely from the upstream :class:`~engine.validation.contracts.ValidationReport`
+ :class:`~engine.validation.evidence.ValidationEvidence`) to reproduce the authoritative
:class:`~engine.certification.engine.CertificationDecision`,
:class:`~engine.certification.contracts.CertificationRecord`, and
:class:`~engine.certification.evidence.CertificationEvidence`.

Because the engine is a **pure, deterministic function** of the subject (IMP-007 §5),
this reproduction is byte-for-byte identical to the engine's own output — the mechanism
by which the console guarantees fidelity (P6). The façade **redefines no criterion,
verdict, ledger rule, severity, or evidence format** (TP-01); it holds the certified
criteria suite (``default_criteria`` by default) and delegates entirely. It mutates
nothing, writes nothing to the corpus (DP-03), and performs no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.certification.contracts import ENGINE_CERTIFICATION_CONTRACT
from platform.certification.errors import CertificationFidelityError
from platform.foundation.contracts import ENGINE_CONTRACTS, ContractRef, content_hash
from typing import Any

from engine.certification.contracts import (
    CertificationClass,
    CertificationRecord,
    CertificationSubject,
)
from engine.certification.engine import CertificationDecision, CertificationEngine
from engine.certification.evidence import CertificationEvidence, build_certification_evidence
from engine.validation.contracts import ValidationReport
from engine.validation.evidence import ValidationEvidence

#: The certified EC-1 certification contract reference the façade binds to (by reference).
CERTIFICATION_ENGINE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ref for ref in ENGINE_CONTRACTS if ref.name == ENGINE_CERTIFICATION_CONTRACT
)


@dataclass(frozen=True, slots=True)
class SurfacedCertification:
    """The immutable bundle produced by a read-only engine reproduction.

    Carries the certified :class:`CertificationDecision`, its immutable
    :class:`CertificationRecord`, the :class:`CertificationEvidence`, the upstream
    :class:`ValidationReport` + :class:`ValidationEvidence` the certification aggregates,
    and the ``engine_contract`` reference that produced them. It re-derives nothing
    itself — it is the faithful projection the console records.
    """

    report: ValidationReport
    validation_evidence: ValidationEvidence
    decision: CertificationDecision
    record: CertificationRecord
    certification_evidence: CertificationEvidence
    version: str
    certification_class: CertificationClass
    engine_contract: str

    def record_fingerprint(self) -> str:
        return self.record.content_sha256

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine_contract": self.engine_contract,
            "version": self.version,
            "certification_class": self.certification_class.value,
            "report": self.report.to_dict(),
            "validation_evidence": self.validation_evidence.to_dict(),
            "decision": self.decision.to_dict(),
            "record": self.record.to_dict(),
            "certification_evidence": self.certification_evidence.to_dict(),
        }


class CertificationFacade:
    """The read-only EC-1 certification façade (consumes ``engine.certification`` by reference)."""

    __slots__ = ("_engine",)

    def __init__(self, engine: CertificationEngine | None = None) -> None:
        if engine is not None and not isinstance(engine, CertificationEngine):
            raise CertificationFidelityError(
                "CertificationFacade requires an engine.certification CertificationEngine"
            )
        # Bind the certified engine (default criteria suite) — never a re-implemented one.
        self._engine = engine if engine is not None else CertificationEngine()

    @property
    def engine_contract(self) -> str:
        """The certified EC-1 certification contract name this façade binds to."""
        return ENGINE_CERTIFICATION_CONTRACT

    @property
    def engine_contracts(self) -> tuple[ContractRef, ...]:
        """The certified EC-1 certification contract references (by reference)."""
        return CERTIFICATION_ENGINE_CONTRACTS

    def criterion_ids(self) -> tuple[str, ...]:
        """The stable ids of the certified criteria the bound engine runs."""
        return self._engine.criterion_ids

    def _subject(
        self,
        report: ValidationReport,
        evidence: ValidationEvidence,
        *,
        version: str,
        certification_class: CertificationClass,
    ) -> CertificationSubject:
        if not isinstance(report, ValidationReport):
            raise CertificationFidelityError("certification requires a ValidationReport")
        if not isinstance(evidence, ValidationEvidence):
            raise CertificationFidelityError("certification requires a ValidationEvidence")
        return CertificationSubject.from_validation(
            report, evidence, version=version, certification_class=certification_class
        )

    def reproduce(
        self,
        report: ValidationReport,
        evidence: ValidationEvidence,
        *,
        version: str,
        certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
    ) -> CertificationDecision:
        """Reproduce the certified :class:`CertificationDecision` (read-only)."""
        subject = self._subject(
            report, evidence, version=version, certification_class=certification_class
        )
        return self._engine.certify(subject)

    def surface(
        self,
        report: ValidationReport,
        evidence: ValidationEvidence,
        *,
        version: str,
        certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
    ) -> SurfacedCertification:
        """Reproduce the certified decision/record/evidence for the validation output (P6).

        Invokes the certified engine read-only; assembles the certification evidence
        through the certified builder. Re-derives no verdict of its own.
        """
        decision = self.reproduce(
            report, evidence, version=version, certification_class=certification_class
        )
        certification_evidence = build_certification_evidence(decision)
        return SurfacedCertification(
            report=report,
            validation_evidence=evidence,
            decision=decision,
            record=decision.record,
            certification_evidence=certification_evidence,
            version=version,
            certification_class=certification_class,
            engine_contract=ENGINE_CERTIFICATION_CONTRACT,
        )

    def verify_fidelity(
        self,
        record: CertificationRecord,
        report: ValidationReport,
        evidence: ValidationEvidence,
        *,
        version: str,
        certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
    ) -> bool:
        """True iff re-running the certified engine reproduces ``record`` byte-for-byte.

        The machine-checkable fidelity predicate (P6): a stored certification record is
        faithful iff a fresh certified reproduction over the same validation output yields
        a byte-identical record.
        """
        if not isinstance(record, CertificationRecord):
            raise CertificationFidelityError("verify_fidelity requires a CertificationRecord")
        reproduced = self.reproduce(
            report, evidence, version=version, certification_class=certification_class
        )
        return content_hash(reproduced.record.to_dict()) == content_hash(record.to_dict())


__all__ = [
    "CERTIFICATION_ENGINE_CONTRACTS",
    "SurfacedCertification",
    "CertificationFacade",
]
