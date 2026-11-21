"""EC2-CAP-SEC-001 / SEC-CERT — Security Certification Runtime (§18 / §19).

The **Security Certification Runtime** (Phase 5) records the seven §18 security
certification objects (Identity · Security · Privacy · Compliance · Operational · Trust
· Governance), evaluates the §19 control-facet requirement, and rolls recorded
certifications into a deterministic **program certification**.

Certification is **record-only, immutable, evidence-backed, and non-constitutive**: a
``CERTIFIED`` decision **must** cite explicit evidence references — it is **never
inferred from source-asset coverage** (STATUS-001 §2; determination §11). The runtime
authorizes, ratifies, and enacts nothing (RG-02 / AR-04); it asserts no
operational/production security beyond recorded evidence.

The §19 failure guard evaluates a control's facets (Identity Model · Trust Model ·
Traceability · Testing · Observability · Certification · Governance) and produces a
:class:`GapReport` on any missing facet (determination §13.6). Determinism (IMP-007 §5):
all time inputs are caller-supplied logical ticks; every id and fingerprint is
content-addressed.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.security.contracts import (
    REQUIRED_CONTROL_FACETS,
    CertificationClass,
    CertificationDecision,
    ControlFacet,
    all_certification_classes,
)
from platform.security.errors import (
    CertificationValidationError,
    SecurityCertificationError,
)
from platform.security.intelligence import scan_for_secret
from typing import Any

#: The governed event emitted for every recorded certification (PC-16).
CERTIFICATION_RECORDED_EVENT = "security.certification.recorded"


@dataclass(frozen=True, slots=True)
class GapReport:
    """A §19 Gap Report: a control is missing one or more required facets.

    Record-only and content-addressed (``UCOS-SGAP-``). Its presence means the control
    fails generation (ARCH-SECURITY-001 §19) — the runtime records the gap rather than
    silently certifying.
    """

    subject_ref: str
    missing_facets: tuple[str, ...]
    present_facets: tuple[str, ...]
    gap_id: str = ""

    @classmethod
    def create(
        cls,
        subject_ref: str,
        *,
        missing_facets: tuple[ControlFacet, ...],
        present_facets: tuple[ControlFacet, ...],
    ) -> GapReport:
        missing = tuple(sorted(f.value for f in missing_facets))
        present = tuple(sorted(f.value for f in present_facets))
        core = {
            "subject_ref": subject_ref,
            "missing_facets": list(missing),
            "present_facets": list(present),
        }
        return cls(
            subject_ref=subject_ref,
            missing_facets=missing,
            present_facets=present,
            gap_id=f"UCOS-SGAP-{content_hash(core)[:16]}",
        )

    @property
    def has_gaps(self) -> bool:
        return bool(self.missing_facets)

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "subject_ref": self.subject_ref,
            "missing_facets": list(self.missing_facets),
            "present_facets": list(self.present_facets),
        }


def evaluate_control_facets(
    subject_ref: str, facets_present: set[ControlFacet] | frozenset[ControlFacet]
) -> GapReport:
    """Evaluate a control's §19 facets and return a :class:`GapReport` (fail-closed).

    A control must carry all of :data:`REQUIRED_CONTROL_FACETS`. The returned report's
    :attr:`GapReport.has_gaps` is ``True`` iff any required facet is missing.
    """
    if not isinstance(subject_ref, str) or not subject_ref.strip():
        raise SecurityCertificationError("control evaluation requires a non-empty subject_ref")
    present = frozenset(f for f in facets_present if isinstance(f, ControlFacet))
    missing = REQUIRED_CONTROL_FACETS - present
    return GapReport.create(
        subject_ref,
        missing_facets=tuple(missing),
        present_facets=tuple(present),
    )


@dataclass(frozen=True, slots=True)
class SecurityCertification:
    """An immutable, evidence-backed, non-constitutive §18 certification record.

    Records a certification ``decision`` for a ``subject_ref`` in a §18
    ``certification_class``, citing explicit ``evidence_refs`` and a ``basis``. A
    ``CERTIFIED`` decision **requires** at least one evidence reference (STATUS-001 §2:
    never inferred from source-asset coverage). ``non_constitutive`` is invariantly
    ``True``. ``certification_id`` is content-addressed (``UCOS-SCERT-``).
    """

    certification_class: CertificationClass
    subject_ref: str
    decision: CertificationDecision
    basis: str
    certified_at: int
    evidence_refs: tuple[str, ...] = ()
    gap_ref: str | None = None
    non_constitutive: bool = True
    certification_id: str = ""

    @classmethod
    def create(
        cls,
        certification_class: CertificationClass,
        subject_ref: str,
        decision: CertificationDecision,
        *,
        basis: str,
        certified_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
        gap_ref: str | None = None,
    ) -> SecurityCertification:
        """Build a certification with a deterministic id, fail-closed on any violation."""
        if not isinstance(certification_class, CertificationClass):
            raise SecurityCertificationError("certification_class must be a CertificationClass")
        if not isinstance(subject_ref, str) or not subject_ref.strip():
            raise SecurityCertificationError("certification requires a non-empty subject_ref")
        if not isinstance(decision, CertificationDecision):
            raise SecurityCertificationError("decision must be a CertificationDecision")
        if not isinstance(basis, str) or not basis.strip():
            raise SecurityCertificationError("certification requires a non-empty basis")
        if not isinstance(certified_at, int) or isinstance(certified_at, bool):
            raise SecurityCertificationError("certification requires a logical tick certified_at")
        refs_t = tuple(evidence_refs)
        # Evidence-backed (STATUS-001 §2): a CERTIFIED decision must cite evidence.
        if decision is CertificationDecision.CERTIFIED and not refs_t:
            raise SecurityCertificationError(
                "a CERTIFIED decision must cite at least one evidence reference "
                "(never inferred from source-asset coverage)",
                subject_ref=subject_ref,
            )
        # Secret defense (SEC-04 / RR-07).
        for value in (subject_ref, basis, *refs_t):
            if scan_for_secret(value):
                raise SecurityCertificationError(
                    "certification rejected: a field matched a secret pattern (RR-07)"
                )
        core = {
            "certification_class": certification_class.value,
            "subject_ref": subject_ref,
            "decision": decision.value,
            "basis": basis,
            "certified_at": certified_at,
            "evidence_refs": list(refs_t),
            "gap_ref": gap_ref,
            "non_constitutive": True,
        }
        return cls(
            certification_class=certification_class,
            subject_ref=subject_ref,
            decision=decision,
            basis=basis,
            certified_at=certified_at,
            evidence_refs=refs_t,
            gap_ref=gap_ref,
            non_constitutive=True,
            certification_id=f"UCOS-SCERT-{content_hash(core)[:16]}",
        )

    @property
    def is_certified(self) -> bool:
        return self.decision is CertificationDecision.CERTIFIED

    def validate(self) -> dict[str, Any]:
        """Re-affirm meta-validity (typed · identified · evidence-backed · non-constitutive)."""
        evidence_backed = (self.decision is not CertificationDecision.CERTIFIED) or bool(
            self.evidence_refs
        )
        checks = {
            "typed": isinstance(self.certification_class, CertificationClass)
            and isinstance(self.decision, CertificationDecision),
            "identified": self.certification_id.startswith("UCOS-SCERT-"),
            "evidence_backed": evidence_backed,
            "non_constitutive": self.non_constitutive is True,
        }
        if not all(checks.values()):
            failed = sorted(n for n, ok in checks.items() if not ok)
            raise CertificationValidationError(
                "certification failed meta-validity",
                certification_id=self.certification_id,
                failed=",".join(failed),
            )
        return {"certification_id": self.certification_id, "meta_valid": True, "checks": checks}

    def trace(self) -> dict[str, Any]:
        """Return the traceability chain (backward §18 class · subject · evidence refs)."""
        return {
            "certification_id": self.certification_id,
            "backward": {
                "certification_class": self.certification_class.value,
                "source_ref": "ARCH-SECURITY-001 §18",
            },
            "subject": {"subject_ref": self.subject_ref, "decision": self.decision.value},
            "evidence_refs": list(self.evidence_refs),
            "gap_ref": self.gap_ref,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "certification_class": self.certification_class.value,
            "subject_ref": self.subject_ref,
            "decision": self.decision.value,
            "basis": self.basis,
            "certified_at": self.certified_at,
            "evidence_refs": list(self.evidence_refs),
            "gap_ref": self.gap_ref,
            "non_constitutive": self.non_constitutive,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class CertificationLedger:
    """SEC-CERT's deterministic, append-only certification record surface.

    Idempotent by ``certification_id``; queryable by class / subject / decision. It
    exposes no ratify/enact/override operation (RG-02 / AR-04).
    """

    __slots__ = ("_entries", "_index")

    def __init__(self) -> None:
        self._entries: list[SecurityCertification] = []
        self._index: dict[str, int] = {}

    def record(self, certification: SecurityCertification) -> SecurityCertification:
        """Append a certification (idempotent by id); returns the stored entry."""
        if not isinstance(certification, SecurityCertification):
            raise SecurityCertificationError("only a SecurityCertification may be recorded")
        certification.validate()
        existing = self._index.get(certification.certification_id)
        if existing is not None:
            return self._entries[existing]
        self._index[certification.certification_id] = len(self._entries)
        self._entries.append(certification)
        return certification

    @property
    def certifications(self) -> tuple[SecurityCertification, ...]:
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, certification_id: str) -> bool:
        return certification_id in self._index

    def get(self, certification_id: str) -> SecurityCertification:
        idx = self._index.get(certification_id)
        if idx is None:
            raise SecurityCertificationError(
                "no such certification", certification_id=certification_id
            )
        return self._entries[idx]

    def by_class(
        self, certification_class: CertificationClass
    ) -> tuple[SecurityCertification, ...]:
        return tuple(c for c in self._entries if c.certification_class is certification_class)

    def by_subject(self, subject_ref: str) -> tuple[SecurityCertification, ...]:
        return tuple(c for c in self._entries if c.subject_ref == subject_ref)

    def by_decision(self, decision: CertificationDecision) -> tuple[SecurityCertification, ...]:
        return tuple(c for c in self._entries if c.decision is decision)

    def fingerprint(self) -> str:
        return content_hash([c.to_dict() for c in self._entries])

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_count": len(self._entries),
            "certifications": [c.to_dict() for c in self._entries],
        }


@dataclass(frozen=True, slots=True)
class ProgramCertification:
    """The deterministic program-certification roll-up over recorded certifications.

    Evidence-derived (never hand-set): ``CERTIFIED`` iff at least one certification is
    recorded and **no** recorded certification is ``NOT_CERTIFIED``; otherwise
    ``NOT_CERTIFIED``. Content-addressed (``UCOS-SCPR-``).
    """

    decision: CertificationDecision
    certification_count: int
    certified_count: int
    not_certified_count: int
    covered_classes: tuple[str, ...]
    program_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        decision: CertificationDecision,
        certification_count: int,
        certified_count: int,
        not_certified_count: int,
        covered_classes: tuple[str, ...],
    ) -> ProgramCertification:
        core = {
            "decision": decision.value,
            "certification_count": certification_count,
            "certified_count": certified_count,
            "not_certified_count": not_certified_count,
            "covered_classes": list(covered_classes),
        }
        return cls(
            decision=decision,
            certification_count=certification_count,
            certified_count=certified_count,
            not_certified_count=not_certified_count,
            covered_classes=covered_classes,
            program_id=f"UCOS-SCPR-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "program_id": self.program_id,
            "decision": self.decision.value,
            "certification_count": self.certification_count,
            "certified_count": self.certified_count,
            "not_certified_count": self.not_certified_count,
            "covered_classes": list(self.covered_classes),
            "constitutive": False,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def roll_up_program(certifications: tuple[SecurityCertification, ...]) -> ProgramCertification:
    """Roll recorded certifications into a deterministic program certification (pure)."""
    certified = sum(1 for c in certifications if c.is_certified)
    not_certified = sum(1 for c in certifications if not c.is_certified)
    covered = tuple(sorted({c.certification_class.value for c in certifications if c.is_certified}))
    if certifications and not_certified == 0:
        decision = CertificationDecision.CERTIFIED
    else:
        decision = CertificationDecision.NOT_CERTIFIED
    return ProgramCertification.create(
        decision=decision,
        certification_count=len(certifications),
        certified_count=certified,
        not_certified_count=not_certified,
        covered_classes=covered,
    )


@dataclass(frozen=True, slots=True)
class SecurityCertificationEvidence:
    """A deterministic, content-addressed report over recorded certifications (``UCOS-SCTE-``)."""

    ledger_fingerprint: str
    certification_count: int
    program: dict[str, Any]
    class_counts: tuple[tuple[str, int], ...]
    decision_counts: tuple[tuple[str, int], ...]
    certifications: tuple[dict[str, Any], ...]
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        ledger_fingerprint: str,
        program: dict[str, Any],
        class_counts: tuple[tuple[str, int], ...],
        decision_counts: tuple[tuple[str, int], ...],
        certifications: tuple[dict[str, Any], ...],
    ) -> SecurityCertificationEvidence:
        core = {
            "ledger_fingerprint": ledger_fingerprint,
            "program": program,
            "class_counts": [list(c) for c in class_counts],
            "decision_counts": [list(d) for d in decision_counts],
            "certifications": list(certifications),
        }
        return cls(
            ledger_fingerprint=ledger_fingerprint,
            certification_count=len(certifications),
            program=program,
            class_counts=class_counts,
            decision_counts=decision_counts,
            certifications=certifications,
            evidence_id=f"UCOS-SCTE-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "ledger_fingerprint": self.ledger_fingerprint,
            "certification_count": self.certification_count,
            "program": dict(self.program),
            "class_counts": [list(c) for c in self.class_counts],
            "decision_counts": [list(d) for d in self.decision_counts],
            "certifications": [dict(c) for c in self.certifications],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class SecurityCertificationService:
    """The governed SEC-CERT composition root (certify · control-guard · rollup · report)."""

    __slots__ = ("_ledger", "_events")

    def __init__(
        self,
        *,
        ledger: CertificationLedger | None = None,
        events: EventBus | None = None,
    ) -> None:
        if ledger is not None and not isinstance(ledger, CertificationLedger):
            raise SecurityCertificationError("ledger must be a CertificationLedger when provided")
        if events is not None and not isinstance(events, EventBus):
            raise SecurityCertificationError("events must be an EventBus when provided")
        self._ledger = ledger if ledger is not None else CertificationLedger()
        self._events = events

    @property
    def ledger(self) -> CertificationLedger:
        return self._ledger

    # -- certify ----------------------------------------------------------------

    def certify(
        self,
        certification_class: CertificationClass,
        subject_ref: str,
        decision: CertificationDecision,
        *,
        basis: str,
        certified_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
        gap_ref: str | None = None,
    ) -> SecurityCertification:
        """Record an evidence-backed §18 certification and emit a governed event."""
        certification = SecurityCertification.create(
            certification_class,
            subject_ref,
            decision,
            basis=basis,
            certified_at=certified_at,
            evidence_refs=evidence_refs,
            gap_ref=gap_ref,
        )
        recorded = self._ledger.record(certification)
        self._emit(recorded)
        return recorded

    def record(self, certification: SecurityCertification) -> SecurityCertification:
        """Record a pre-built certification (idempotent); emits a governed event."""
        if not isinstance(certification, SecurityCertification):
            raise SecurityCertificationError("only a SecurityCertification may be recorded")
        recorded = self._ledger.record(certification)
        self._emit(recorded)
        return recorded

    def certify_control(
        self,
        subject_ref: str,
        facets_present: set[ControlFacet] | frozenset[ControlFacet],
        *,
        certified_at: int,
        evidence_refs: tuple[str, ...] | list[str] = (),
        certification_class: CertificationClass = CertificationClass.OPERATIONAL,
    ) -> dict[str, Any]:
        """Apply the §19 facet guard, then record a CERTIFIED or NOT_CERTIFIED result.

        Evaluates the seven required control facets; on a complete control records a
        ``CERTIFIED`` certification (evidence-backed), otherwise records a
        ``NOT_CERTIFIED`` certification bound to a :class:`GapReport` (the control fails
        generation, §19). Returns the gap report and the recorded certification.
        """
        gap = evaluate_control_facets(subject_ref, facets_present)
        if gap.has_gaps:
            certification = self.certify(
                certification_class,
                subject_ref,
                CertificationDecision.NOT_CERTIFIED,
                basis=f"§19 facet gap: missing {','.join(gap.missing_facets)}",
                certified_at=certified_at,
                gap_ref=gap.gap_id,
            )
        else:
            refs = tuple(evidence_refs) or (gap.gap_id,)
            certification = self.certify(
                certification_class,
                subject_ref,
                CertificationDecision.CERTIFIED,
                basis="§19 facets complete (Identity/Trust/Traceability/Testing/"
                "Observability/Certification/Governance)",
                certified_at=certified_at,
                evidence_refs=refs,
            )
        return {
            "subject_ref": subject_ref,
            "gap_report": gap.to_dict(),
            "certified": certification.is_certified,
            "certification": certification.to_dict(),
        }

    # -- rollup + trace + validate + report -------------------------------------

    def program_certification(self) -> ProgramCertification:
        """Roll recorded certifications into a deterministic program certification."""
        return roll_up_program(self._ledger.certifications)

    def trace(self, certification_id: str) -> dict[str, Any]:
        return self._ledger.get(certification_id).trace()

    def validate(self, certification_id: str) -> dict[str, Any]:
        return self._ledger.get(certification_id).validate()

    def validate_all(self) -> dict[str, Any]:
        results = [c.validate() for c in self._ledger.certifications]
        return {
            "certification_count": len(results),
            "meta_valid": all(r["meta_valid"] for r in results),
            "results": results,
        }

    def report(self) -> SecurityCertificationEvidence:
        """Produce deterministic certification evidence over the ledger (record-only)."""
        certs = self._ledger.certifications
        class_counts = tuple(
            (c.value, sum(1 for x in certs if x.certification_class is c))
            for c in all_certification_classes()
        )
        decision_counts = tuple(
            (d.value, sum(1 for x in certs if x.decision is d)) for d in CertificationDecision
        )
        return SecurityCertificationEvidence.create(
            ledger_fingerprint=self._ledger.fingerprint(),
            program=self.program_certification().to_dict(),
            class_counts=class_counts,
            decision_counts=decision_counts,
            certifications=tuple(c.to_dict() for c in certs),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"ledger": self._ledger.to_dict(), "evidence": self.report().to_dict()}

    # -- internals --------------------------------------------------------------

    def _emit(self, certification: SecurityCertification) -> None:
        if self._events is None:
            return
        self._events.publish(
            CERTIFICATION_RECORDED_EVENT,
            source="platform.security.certification",
            subject=certification.subject_ref,
            payload={"certification": certification.to_dict(), "constitutive": False},
        )


def build_security_certification_service(
    *, events: EventBus | None = None
) -> SecurityCertificationService:
    """Default composition of the Security Certification Runtime (record-only)."""
    return SecurityCertificationService(ledger=CertificationLedger(), events=events)


__all__ = [
    "CERTIFICATION_RECORDED_EVENT",
    "GapReport",
    "evaluate_control_facets",
    "SecurityCertification",
    "CertificationLedger",
    "ProgramCertification",
    "roll_up_program",
    "SecurityCertificationEvidence",
    "SecurityCertificationService",
    "build_security_certification_service",
]
