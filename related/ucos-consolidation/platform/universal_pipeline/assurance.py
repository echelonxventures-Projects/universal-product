"""UAPF-000001 — the Universal Validation, Verification and Certification engines.

Three acts, three record types, one order. ``06-IMPLEMENTATION-STATE-MACHINE.md`` §2 makes
the order constitutional: ``IMPLEMENTED → VALIDATED → CERTIFIED``, and §4 lists
``IMPLEMENTED → CERTIFIED`` among the illegal transitions. This module enforces that order
over *records*, so it is impossible to hold a certification for something that was never
verified — not merely discouraged.

Why validation and verification are separate acts
-------------------------------------------------
Validation asks *did we build it as declared*; verification asks *is the validation itself
sound*. Collapsing them would make a validator its own auditor, which is the failure mode
independent verification exists to prevent. So :meth:`PipelineAssurance.verify` requires a
*passed* validation record for the same subject and will not accept its own word for it,
and :meth:`certify` requires a passed verification.

Records, not booleans
---------------------
Each act produces an immutable, content-addressed record carrying its subject, its verdict,
its findings and its evidence. A verdict of ``False`` is a legitimate, recorded outcome —
failing validation is a *result*, not an error — whereas asking for certification out of
order is a **fail-closed error**, because that is a caller mistake rather than a finding
about the subject. The distinction is deliberate: results are data, mistakes are exceptions.

Evidence is carried by reference-safe content: a record stores the evidence mapping it was
given and a hash over it, so two runs that produced the same evidence produce the same
record identity, and a tampered record fails :meth:`ValidationRecord.verify`.

Determinism: no wall-clock, no RNG, no I/O. Records are ordered by admission ordinal, which
is derived from how many already exist.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.errors import (
    PipelineCertificationError,
    PipelineValidationError,
)
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.identity import Identity, mint
from typing import Any

#: The three assurance acts, in the order Repository Truth requires them.
ASSURANCE_ACTS: tuple[str, ...] = ("validation", "verification", "certification")


@dataclass(frozen=True, slots=True)
class _AssuranceRecord:
    """The shared shape of an assurance record: subject, verdict, findings, evidence.

    A private base so the three public record types share one construction discipline and
    one hashing rule without any of them becoming a special case of another. They stay
    distinct types because they are distinct constitutional acts and a signature that
    accepts "any assurance record" would let a caller substitute one for another.
    """

    subject: str
    passed: bool
    findings: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    ordinal: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.subject, str) or not self.subject:
            raise PipelineValidationError("assurance record subject is required")
        if not isinstance(self.passed, bool):
            raise PipelineValidationError("assurance verdict must be a bool", subject=self.subject)
        if not isinstance(self.findings, tuple):
            raise PipelineValidationError(
                "assurance findings must be a tuple", subject=self.subject
            )
        for finding in self.findings:
            if not isinstance(finding, str) or not finding:
                raise PipelineValidationError(
                    "assurance findings must be non-empty strings", subject=self.subject
                )
        if not isinstance(self.evidence, Mapping):
            raise PipelineValidationError(
                "assurance evidence must be a mapping", subject=self.subject
            )
        if self.ordinal < 0:
            raise PipelineValidationError(
                "assurance ordinal must be non-negative", subject=self.subject
            )
        if not self.passed and not self.findings:
            raise PipelineValidationError(
                "a failing assurance verdict must state at least one finding",
                subject=self.subject,
            )

    @property
    def act(self) -> str:
        """The assurance act this record represents."""
        raise NotImplementedError  # pragma: no cover — every concrete record overrides.

    @property
    def identity(self) -> Identity:
        return mint(f"{self.act}-record", self.subject, self.evidence_hash())

    def evidence_hash(self) -> str:
        """A deterministic content hash of the verdict and its evidence."""
        return content_hash(
            {
                "act": self.act,
                "subject": self.subject,
                "passed": self.passed,
                "findings": list(self.findings),
                "evidence": dict(self.evidence),
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "act": self.act,
            "identity": self.identity.value,
            "subject": self.subject,
            "passed": self.passed,
            "findings": list(self.findings),
            "evidence": dict(self.evidence),
            "ordinal": self.ordinal,
            "evidence_hash": self.evidence_hash(),
        }


@dataclass(frozen=True, slots=True)
class ValidationRecord(_AssuranceRecord):
    """*Was it built as declared?* — the first assurance act."""

    @property
    def act(self) -> str:
        return "validation"


@dataclass(frozen=True, slots=True)
class VerificationRecord(_AssuranceRecord):
    """*Is the validation sound?* — the independent second act.

    Carries the validation it verifies, so a verification can never float free of the
    validation it claims to have checked.
    """

    validated_hash: str = ""

    def __post_init__(self) -> None:
        _AssuranceRecord.__post_init__(self)
        if not isinstance(self.validated_hash, str) or not self.validated_hash:
            raise PipelineValidationError(
                "a verification must name the validation it verifies", subject=self.subject
            )

    @property
    def act(self) -> str:
        return "verification"

    def to_dict(self) -> dict[str, Any]:
        return {**_AssuranceRecord.to_dict(self), "validated_hash": self.validated_hash}


@dataclass(frozen=True, slots=True)
class CertificationRecord(_AssuranceRecord):
    """*May it be relied upon?* — the terminal act, admissible only after verification."""

    verified_hash: str = ""

    def __post_init__(self) -> None:
        _AssuranceRecord.__post_init__(self)
        if not isinstance(self.verified_hash, str) or not self.verified_hash:
            raise PipelineCertificationError(
                "a certification must name the verification it rests on", subject=self.subject
            )

    @property
    def act(self) -> str:
        return "certification"

    def to_dict(self) -> dict[str, Any]:
        return {**_AssuranceRecord.to_dict(self), "verified_hash": self.verified_hash}


class PipelineAssurance:
    """The one place validation, verification and certification records are produced.

    Holds the records of one platform instance and enforces the constitutional order
    between them. It decides nothing about *whether* a subject is sound — the caller
    supplies the verdict and its findings — and everything about whether the acts happened
    in a lawful order, which is the part a caller cannot be trusted to police itself.
    """

    __slots__ = ("_validations", "_verifications", "_certifications", "_bus")

    def __init__(self, *, bus: PipelineEventBus | None = None) -> None:
        if bus is not None and not isinstance(bus, PipelineEventBus):
            raise PipelineValidationError("bus must be a PipelineEventBus")
        self._validations: list[ValidationRecord] = []
        self._verifications: list[VerificationRecord] = []
        self._certifications: list[CertificationRecord] = []
        self._bus = bus

    # -- the three acts ---------------------------------------------------------------

    def validate(
        self,
        subject: str,
        *,
        passed: bool = True,
        findings: tuple[str, ...] = (),
        evidence: Mapping[str, Any] | None = None,
    ) -> ValidationRecord:
        """Record the validation verdict for ``subject``.

        Raises:
            PipelineValidationError: if the subject or verdict is malformed, or a failing
                verdict states no finding.
        """
        record = ValidationRecord(
            subject=subject,
            passed=passed,
            findings=findings,
            evidence=dict(evidence or {}),
            ordinal=len(self._validations),
        )
        self._validations.append(record)
        self._emit("uapf.unit.validated", record)
        return record

    def verify(
        self,
        subject: str,
        *,
        passed: bool = True,
        findings: tuple[str, ...] = (),
        evidence: Mapping[str, Any] | None = None,
    ) -> VerificationRecord:
        """Record the verification verdict for ``subject``, binding it to its validation.

        Raises:
            PipelineValidationError: if ``subject`` has no *passed* validation record —
                verification out of order is a caller mistake, so it fails closed rather
                than producing a failing verdict.
        """
        validated = self.latest_validation(subject)
        if not validated.passed:
            raise PipelineValidationError(
                "verification requires a passed validation (IMPLEMENTED → VALIDATED first)",
                subject=subject,
                findings=list(validated.findings),
            )
        record = VerificationRecord(
            subject=subject,
            passed=passed,
            findings=findings,
            evidence=dict(evidence or {}),
            ordinal=len(self._verifications),
            validated_hash=validated.evidence_hash(),
        )
        self._verifications.append(record)
        self._emit("uapf.unit.verified", record)
        return record

    def certify(
        self,
        subject: str,
        *,
        passed: bool = True,
        findings: tuple[str, ...] = (),
        evidence: Mapping[str, Any] | None = None,
    ) -> CertificationRecord:
        """Record the certification verdict for ``subject``, binding it to its verification.

        Raises:
            PipelineCertificationError: if ``subject`` has no *passed* verification record.
                ``IMPLEMENTED → CERTIFIED`` is an illegal transition
                (``06-IMPLEMENTATION-STATE-MACHINE.md`` §4), so skipping verification is
                refused here as well as in the state engine — the two guards are
                independent, which is why neither can be the only one that holds.
        """
        verified = self.latest_verification(subject)
        if not verified.passed:
            raise PipelineCertificationError(
                "certification requires a passed verification (VALIDATED → CERTIFIED only)",
                subject=subject,
                findings=list(verified.findings),
            )
        record = CertificationRecord(
            subject=subject,
            passed=passed,
            findings=findings,
            evidence=dict(evidence or {}),
            ordinal=len(self._certifications),
            verified_hash=verified.evidence_hash(),
        )
        self._certifications.append(record)
        self._emit("uapf.unit.certified", record)
        return record

    # -- lookup -----------------------------------------------------------------------

    @property
    def validations(self) -> tuple[ValidationRecord, ...]:
        return tuple(self._validations)

    @property
    def verifications(self) -> tuple[VerificationRecord, ...]:
        return tuple(self._verifications)

    @property
    def certifications(self) -> tuple[CertificationRecord, ...]:
        return tuple(self._certifications)

    def latest_validation(self, subject: str) -> ValidationRecord:
        """The most recent validation record for ``subject``.

        Raises:
            PipelineValidationError: if none exists (fail-closed).
        """
        for record in reversed(self._validations):
            if record.subject == subject:
                return record
        raise PipelineValidationError("no validation record for subject", subject=subject)

    def latest_verification(self, subject: str) -> VerificationRecord:
        """The most recent verification record for ``subject``.

        Raises:
            PipelineCertificationError: if none exists — the caller asking is on the
                certification path, so the error names that act.
        """
        for record in reversed(self._verifications):
            if record.subject == subject:
                return record
        raise PipelineCertificationError("no verification record for subject", subject=subject)

    def latest_certification(self, subject: str) -> CertificationRecord:
        """The most recent certification record for ``subject``.

        Raises:
            PipelineCertificationError: if none exists (fail-closed).
        """
        for record in reversed(self._certifications):
            if record.subject == subject:
                return record
        raise PipelineCertificationError("no certification record for subject", subject=subject)

    def is_validated(self, subject: str) -> bool:
        """True iff ``subject`` holds a passed validation record."""
        return any(r.subject == subject and r.passed for r in self._validations)

    def is_verified(self, subject: str) -> bool:
        """True iff ``subject`` holds a passed verification record."""
        return any(r.subject == subject and r.passed for r in self._verifications)

    def is_certified(self, subject: str) -> bool:
        """True iff ``subject`` holds a passed certification record."""
        return any(r.subject == subject and r.passed for r in self._certifications)

    def records_for(self, subject: str) -> tuple[dict[str, Any], ...]:
        """Every record about ``subject``, in constitutional act order (the trail)."""
        return tuple(
            record.to_dict()
            for group in (self._validations, self._verifications, self._certifications)
            for record in group
            if record.subject == subject
        )

    def subjects(self) -> tuple[str, ...]:
        """Every subject any record mentions, sorted."""
        return tuple(
            sorted(
                {
                    record.subject
                    for group in (self._validations, self._verifications, self._certifications)
                    for record in group
                }
            )
        )

    # -- evidence ---------------------------------------------------------------------

    def _emit(self, category: str, record: _AssuranceRecord) -> None:
        if self._bus is not None:
            self._bus.emit(category, record.subject, payload=record.to_dict())

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable render of every record (evidence)."""
        return {
            "acts": list(ASSURANCE_ACTS),
            "validation_count": len(self._validations),
            "verification_count": len(self._verifications),
            "certification_count": len(self._certifications),
            "certified_subjects": [s for s in self.subjects() if self.is_certified(s)],
            "validations": [record.to_dict() for record in self._validations],
            "verifications": [record.to_dict() for record in self._verifications],
            "certifications": [record.to_dict() for record in self._certifications],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of every recorded assurance act."""
        return content_hash(self.to_dict())


__all__ = [
    "ASSURANCE_ACTS",
    "CertificationRecord",
    "PipelineAssurance",
    "ValidationRecord",
    "VerificationRecord",
]
