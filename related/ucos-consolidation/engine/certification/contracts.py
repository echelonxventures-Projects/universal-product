"""TASK-000050 — Certification Contracts (EPIC-008).

The value types that flow across the Certification Layer boundary. Every type is
**immutable, typed, deterministic, and serializable** and holds no runtime state:

    * :class:`CertificationStatus` — the aggregate certification verdict.
    * :class:`CriterionSeverity` — whether a failing criterion blocks certification.
    * :class:`CriterionStatus` — the outcome of a single certification criterion.
    * :class:`CertificationClass` — what a certification attests (readiness only).
    * :class:`CertificationRequest` — a request to certify a validated target.
    * :class:`CertificationSubject` — the normalized projection of a validated
      artifact that criteria evaluate, built **purely** from a Validation Report +
      Validation Evidence (EPIC-007), so certification is decoupled from the
      producer and aggregates validation rather than re-judging artifacts (TP-01).
    * :class:`CertificationFinding` — the immutable outcome of one criterion.
    * :class:`CertificationRecord` — the **immutable, content-addressed** record of
      a certification determination (append-only, attributable, version-pinned,
      evidence-referenced, non-constitutive).

Certification is *sound* (attests only what validation substantiates), *record-only*
(confers no authority — ``ENGINEERING-EXECUTION-ONLY``), *version-pinned*, and
*reproducible*: an identical Validation Report + Validation Evidence yields a
byte-identical subject, decision, record (and thus a stable ``certification_id``).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from engine.certification.errors import (
    CertificationIntegrityError,
    CertificationSubjectError,
)

# The canonical serialization primitive has exactly one definition, in UCKP Layer Zero
# (UCKP-LAW-0001 Art-13, UCKP-INV-03). Re-exported unchanged, so callers of
# ``engine.certification.contracts.content_hash`` are unaffected.
from engine.uckp.canonical import canonical_json, content_hash

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.validation.contracts import ValidationReport
    from engine.validation.evidence import ValidationEvidence

#: The semantic version of the Certification Layer contract surface (AR-03/PL-05).
CERTIFICATION_CONTRACT_VERSION = "1.0.0"

#: The readiness standard a certification attests against (record-only, IMP-007 §13).
CERTIFICATION_STANDARD = "UCOS-EC1-CERTIFICATION-STANDARD"
CERTIFICATION_STANDARD_VERSION = "1.0.0"

#: Certification confers no constitutional authority (DE-05 / IP-01): it records
#: engineering readiness only. This is embedded verbatim in every record.
CERTIFICATION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"


class CriterionSeverity(str, Enum):
    """Whether a failing certification criterion blocks certification or is advisory."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class CriterionStatus(str, Enum):
    """The outcome of a single certification criterion."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class CertificationStatus(str, Enum):
    """The aggregate verdict of a certification determination (fail-closed)."""

    CERTIFIED = "certified"
    NOT_CERTIFIED = "not-certified"


class CertificationClass(str, Enum):
    """What a certification attests. Certification records **readiness only**."""

    ENGINEERING_READINESS = "engineering-readiness"


@dataclass(frozen=True, slots=True)
class CertificationRequest:
    """An immutable request to certify a validated target (no runtime state)."""

    target_id: str
    version: str
    certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS
    strict: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "version": self.version,
            "certification_class": self.certification_class.value,
            "strict": self.strict,
        }


@dataclass(frozen=True, slots=True)
class CertificationFinding:
    """The immutable outcome of a single certification criterion."""

    criterion_id: str
    severity: CriterionSeverity
    status: CriterionStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is CriterionStatus.PASS

    @property
    def is_blocking_failure(self) -> bool:
        return self.status is CriterionStatus.FAIL and self.severity is CriterionSeverity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True, slots=True)
class CertificationSubject:
    """A normalized projection of a validated artifact, built from validation output.

    Every field is derived **purely** from a Validation Report and its Validation
    Evidence, so certification criteria aggregate the validation verdict rather than
    re-judging the artifact (TP-01, soundness): certification adds no new judgment.
    """

    target_id: str
    blueprint_id: str
    version: str
    certification_class: CertificationClass
    validation_verdict: str
    validation_accepted: bool
    checks_run: tuple[str, ...]
    blocking_failures: tuple[str, ...]
    counts: Mapping[str, int]
    evidence_present: bool
    evidence_sha256: str

    @classmethod
    def from_validation(
        cls,
        report: ValidationReport,
        evidence: ValidationEvidence | None,
        *,
        version: str,
        certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
    ) -> CertificationSubject:
        """Project a Validation Report + Validation Evidence into a subject.

        Raises:
            CertificationSubjectError: if the report is empty, or the supplied
                evidence does not describe the same target (a caller error). A
                *missing* evidence record is tolerated and recorded as
                ``evidence_present=False`` (fail-closed — it cannot be certified).
        """
        if not getattr(report, "target_id", None):
            raise CertificationSubjectError("validation report has no target_id")

        evidence_present = evidence is not None
        evidence_sha256 = ""
        if evidence is not None:
            if evidence.target_id != report.target_id:
                raise CertificationSubjectError(
                    "validation evidence does not match the report target",
                    report_target=report.target_id,
                    evidence_target=evidence.target_id,
                )
            evidence_sha256 = content_hash(evidence.to_dict())

        return cls(
            target_id=report.target_id,
            blueprint_id=report.blueprint_id,
            version=version,
            certification_class=certification_class,
            validation_verdict=report.verdict.value,
            validation_accepted=report.accepted,
            checks_run=tuple(f.check_id for f in report.findings),
            blocking_failures=tuple(f.check_id for f in report.blocking_failures),
            counts=dict(report.counts()),
            evidence_present=evidence_present,
            evidence_sha256=evidence_sha256,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "certification_class": self.certification_class.value,
            "validation_verdict": self.validation_verdict,
            "validation_accepted": self.validation_accepted,
            "checks_run": list(self.checks_run),
            "blocking_failures": list(self.blocking_failures),
            "counts": dict(self.counts),
            "evidence_present": self.evidence_present,
            "evidence_sha256": self.evidence_sha256,
        }


@dataclass(frozen=True, slots=True)
class CertificationRecord:
    """An immutable, content-addressed record of a certification determination.

    The record is **immutable** (frozen) and **self-verifying**: its
    ``content_sha256`` is the canonical hash of every field but the id and the hash
    itself, and ``certification_id`` is derived from that hash — so any mutation is
    detectable via :meth:`verify_integrity`. It is append-only, attributable,
    version-pinned, references the reproducible validation evidence, embeds the EC-1
    provisional-state disclosure, and asserts ``ENGINEERING-EXECUTION-ONLY``
    authority (certification confers no constitutional finality — DE-05).
    """

    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: CertificationStatus
    certification_class: CertificationClass
    standard: str
    standard_version: str
    authority: str
    evidence_ref: str
    criteria: tuple[CertificationFinding, ...]
    disclosure: Mapping[str, Any]
    content_sha256: str

    @staticmethod
    def _core(
        *,
        target_id: str,
        blueprint_id: str,
        version: str,
        status: CertificationStatus,
        certification_class: CertificationClass,
        standard: str,
        standard_version: str,
        authority: str,
        evidence_ref: str,
        criteria: tuple[CertificationFinding, ...],
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        """The canonical, hashable core of a record (excludes id + content hash)."""
        return {
            "target_id": target_id,
            "blueprint_id": blueprint_id,
            "version": version,
            "status": status.value,
            "certification_class": certification_class.value,
            "standard": standard,
            "standard_version": standard_version,
            "authority": authority,
            "evidence_ref": evidence_ref,
            "criteria": [c.to_dict() for c in criteria],
            "disclosure": dict(disclosure),
        }

    @classmethod
    def create(
        cls,
        *,
        target_id: str,
        blueprint_id: str,
        version: str,
        status: CertificationStatus,
        certification_class: CertificationClass,
        evidence_ref: str,
        criteria: tuple[CertificationFinding, ...],
        disclosure: Mapping[str, Any],
        standard: str = CERTIFICATION_STANDARD,
        standard_version: str = CERTIFICATION_STANDARD_VERSION,
        authority: str = CERTIFICATION_AUTHORITY,
    ) -> CertificationRecord:
        """Assemble an immutable, content-addressed :class:`CertificationRecord`.

        The ``content_sha256`` and ``certification_id`` are derived deterministically
        from the record core, so identical determinations produce an identical id.
        """
        core = cls._core(
            target_id=target_id,
            blueprint_id=blueprint_id,
            version=version,
            status=status,
            certification_class=certification_class,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            evidence_ref=evidence_ref,
            criteria=criteria,
            disclosure=disclosure,
        )
        digest = content_hash(core)
        certification_id = f"UCOS-CERT-{blueprint_id}-{digest[:16]}"
        return cls(
            certification_id=certification_id,
            target_id=target_id,
            blueprint_id=blueprint_id,
            version=version,
            status=status,
            certification_class=certification_class,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            evidence_ref=evidence_ref,
            criteria=criteria,
            disclosure=dict(disclosure),
            content_sha256=digest,
        )

    @property
    def certified(self) -> bool:
        return self.status is CertificationStatus.CERTIFIED

    def recompute_hash(self) -> str:
        """Recompute the content hash from the current field values."""
        return content_hash(
            self._core(
                target_id=self.target_id,
                blueprint_id=self.blueprint_id,
                version=self.version,
                status=self.status,
                certification_class=self.certification_class,
                standard=self.standard,
                standard_version=self.standard_version,
                authority=self.authority,
                evidence_ref=self.evidence_ref,
                criteria=self.criteria,
                disclosure=self.disclosure,
            )
        )

    def verify_integrity(self) -> bool:
        """Return True iff the stored content hash matches a recomputation."""
        return self.recompute_hash() == self.content_sha256

    def require_integrity(self) -> None:
        """Raise :class:`CertificationIntegrityError` if the record was mutated."""
        if not self.verify_integrity():
            raise CertificationIntegrityError(
                "certification record integrity check failed (content mutated)",
                certification_id=self.certification_id,
                expected=self.content_sha256,
                actual=self.recompute_hash(),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status.value,
            "certified": self.certified,
            "certification_class": self.certification_class.value,
            "standard": self.standard,
            "standard_version": self.standard_version,
            "authority": self.authority,
            "evidence_ref": self.evidence_ref,
            "criteria": [c.to_dict() for c in self.criteria],
            "disclosure": dict(self.disclosure),
            "content_sha256": self.content_sha256,
        }


__all__ = [
    "CERTIFICATION_CONTRACT_VERSION",
    "CERTIFICATION_STANDARD",
    "CERTIFICATION_STANDARD_VERSION",
    "CERTIFICATION_AUTHORITY",
    "canonical_json",
    "content_hash",
    "CriterionSeverity",
    "CriterionStatus",
    "CertificationStatus",
    "CertificationClass",
    "CertificationRequest",
    "CertificationFinding",
    "CertificationSubject",
    "CertificationRecord",
]
