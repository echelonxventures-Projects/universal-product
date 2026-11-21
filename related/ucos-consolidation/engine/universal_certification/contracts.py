"""UCOS-EPIC-006 — Universal Certification Contracts (Terminal T6).

The value types that flow across the Universal Certification Engine boundary. Every
type is **immutable, typed, deterministic, and serializable** and holds no runtime
state. The engine is *universal* because it does not depend on any single producer:
it consumes three normalized inputs —

    * :class:`ValidationInput` — a projection of a validation verdict + evidence,
    * :class:`MeasurementInput` — a set of decidable :class:`Measurement` results,
    * :class:`RepositoryTruthInput` — a repository-truth closure attestation,

— and aggregates them into a normalized :class:`UniversalCertificationSubject`. The
subject is a **pure projection** of the three inputs, so every certification rule and
compliance frame *aggregates* the upstream verdicts rather than re-judging any
artifact (TP-01, soundness): certification adds no new judgment of its own.

A certification determination is recorded as an **immutable, content-addressed**
:class:`Certificate`: its ``content_sha256`` is the canonical hash of every field but
the id and the hash itself, and ``certification_id`` derives from that hash — so an
identical set of inputs yields a byte-identical subject, decision, and certificate
(reproducible certification). The certificate is *record-only* — it confers no
authority (``ENGINEERING-EXECUTION-ONLY``) and carries the EC-1 provisional-state
disclosure (DE-05 / IP-01): it records **universal engineering readiness**, not
constitutional finality.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from engine.uckp.canonical import canonical_json, content_hash
from engine.universal_certification.errors import (
    CertificateIntegrityError,
    CertificationInputError,
    CertificationSubjectError,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.validation.contracts import ValidationReport
    from engine.validation.evidence import ValidationEvidence

#: The semantic version of the Universal Certification contract surface (AR-03/PL-05).
UCERT_CONTRACT_VERSION = "1.0.0"

#: The readiness standard a universal certificate attests against (record-only).
UCERT_STANDARD = "UCOS-UNIVERSAL-CERTIFICATION-STANDARD"
UCERT_STANDARD_VERSION = "1.0.0"

#: Universal certification confers no constitutional authority (DE-05 / IP-01): it
#: records engineering readiness only. Embedded verbatim in every certificate.
UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

#: The validation check id that proves the EC-1 provisional-state disclosure (DE-05).
DISCLOSURE_CHECK_ID = "provisional-state-disclosure"


# --------------------------------------------------------------------------- #
# Enumerations.                                                               #
# --------------------------------------------------------------------------- #


class RuleSeverity(str, Enum):
    """Whether a failing certification rule blocks certification or is advisory."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class RuleStatus(str, Enum):
    """The outcome of a single certification rule."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class CertificationStatus(str, Enum):
    """The aggregate verdict of a certification determination (fail-closed)."""

    CERTIFIED = "certified"
    NOT_CERTIFIED = "not-certified"


class CertificationClass(str, Enum):
    """What a universal certificate attests. It records **readiness only**."""

    UNIVERSAL_READINESS = "universal-readiness"


class ComplianceStatus(str, Enum):
    """The conformance verdict of a compliance frame or aggregate report."""

    CONFORMANT = "conformant"
    NON_CONFORMANT = "non-conformant"


class MeasurementComparator(str, Enum):
    """How a measured value is compared to its threshold to decide satisfaction."""

    GE = "ge"  # value >= threshold
    LE = "le"  # value <= threshold
    GT = "gt"  # value > threshold
    LT = "lt"  # value < threshold
    EQ = "eq"  # value == threshold


# --------------------------------------------------------------------------- #
# Consumed input: Measurement.                                                #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class Measurement:
    """A single decidable measurement result (a measured value vs. a threshold).

    ``satisfied`` is a *computed* verdict (measurement over assertion): it is derived
    from the value, comparator, and threshold, never hand-set — so a measurement input
    cannot claim satisfaction it did not measure.
    """

    metric_id: str
    value: float
    threshold: float
    comparator: MeasurementComparator
    severity: RuleSeverity
    satisfied: bool
    unit: str = ""

    @classmethod
    def evaluate(
        cls,
        *,
        metric_id: str,
        value: float,
        threshold: float,
        comparator: MeasurementComparator = MeasurementComparator.GE,
        severity: RuleSeverity = RuleSeverity.BLOCKING,
        unit: str = "",
    ) -> Measurement:
        """Build a measurement whose ``satisfied`` is computed from the comparison."""
        if not isinstance(metric_id, str) or not metric_id:
            raise CertificationInputError("measurement metric_id must be a non-empty string")
        if not isinstance(value, int | float) or not isinstance(threshold, int | float):
            raise CertificationInputError(
                "measurement value and threshold must be numeric", metric_id=metric_id
            )
        if not isinstance(comparator, MeasurementComparator):
            raise CertificationInputError("comparator must be a MeasurementComparator")
        if not isinstance(severity, RuleSeverity):
            raise CertificationInputError("severity must be a RuleSeverity")
        satisfied = _compare(float(value), float(threshold), comparator)
        return cls(
            metric_id=metric_id,
            value=float(value),
            threshold=float(threshold),
            comparator=comparator,
            severity=severity,
            satisfied=satisfied,
            unit=unit,
        )

    @property
    def is_blocking_shortfall(self) -> bool:
        """True iff this is an unsatisfied blocking measurement."""
        return not self.satisfied and self.severity is RuleSeverity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "value": self.value,
            "threshold": self.threshold,
            "comparator": self.comparator.value,
            "severity": self.severity.value,
            "satisfied": self.satisfied,
            "unit": self.unit,
        }


def _compare(value: float, threshold: float, comparator: MeasurementComparator) -> bool:
    if comparator is MeasurementComparator.GE:
        return value >= threshold
    if comparator is MeasurementComparator.LE:
        return value <= threshold
    if comparator is MeasurementComparator.GT:
        return value > threshold
    if comparator is MeasurementComparator.LT:
        return value < threshold
    return value == threshold


# --------------------------------------------------------------------------- #
# Consumed inputs: Validation, Measurement set, Repository Truth.             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ValidationInput:
    """A normalized projection of a validation verdict + evidence (consumed input)."""

    target_id: str
    blueprint_id: str
    verdict: str
    accepted: bool
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
    ) -> ValidationInput:
        """Project an EC-1 Validation Report + Validation Evidence into an input.

        A *missing* evidence record is tolerated and recorded as
        ``evidence_present=False`` (fail-closed — it cannot be certified). A supplied
        evidence record that describes a different target is a caller error.
        """
        if not getattr(report, "target_id", None):
            raise CertificationInputError("validation report has no target_id")
        evidence_present = evidence is not None
        evidence_sha256 = ""
        if evidence is not None:
            if evidence.target_id != report.target_id:
                raise CertificationInputError(
                    "validation evidence does not match the report target",
                    report_target=report.target_id,
                    evidence_target=evidence.target_id,
                )
            evidence_sha256 = content_hash(evidence.to_dict())
        return cls(
            target_id=report.target_id,
            blueprint_id=report.blueprint_id,
            verdict=report.verdict.value,
            accepted=report.accepted,
            checks_run=tuple(f.check_id for f in report.findings),
            blocking_failures=tuple(f.check_id for f in report.blocking_failures),
            counts=dict(report.counts()),
            evidence_present=evidence_present,
            evidence_sha256=evidence_sha256,
        )

    @property
    def disclosure_validated(self) -> bool:
        """True iff validation ran and passed the provisional-state disclosure check."""
        return (
            DISCLOSURE_CHECK_ID in self.checks_run
            and DISCLOSURE_CHECK_ID not in self.blocking_failures
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "verdict": self.verdict,
            "accepted": self.accepted,
            "checks_run": list(self.checks_run),
            "blocking_failures": list(self.blocking_failures),
            "counts": dict(self.counts),
            "evidence_present": self.evidence_present,
            "evidence_sha256": self.evidence_sha256,
            "disclosure_validated": self.disclosure_validated,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class MeasurementInput:
    """A normalized set of decidable :class:`Measurement` results (consumed input)."""

    measurements: tuple[Measurement, ...]
    source: str = ""

    @classmethod
    def create(
        cls,
        measurements: Iterable[Measurement],
        *,
        source: str = "",
    ) -> MeasurementInput:
        """Build a measurement input from an iterable of measurements (deterministic).

        Measurements are ordered by ``metric_id`` so an identical set yields an
        identical digest regardless of supplied order.
        """
        items = tuple(measurements)
        for m in items:
            if not isinstance(m, Measurement):
                raise CertificationInputError("every measurement must be a Measurement")
        ordered = tuple(sorted(items, key=lambda m: m.metric_id))
        return cls(measurements=ordered, source=source)

    @property
    def present(self) -> bool:
        return bool(self.measurements)

    @property
    def blocking_shortfalls(self) -> tuple[str, ...]:
        """The metric ids of unsatisfied blocking measurements (in stable order)."""
        return tuple(m.metric_id for m in self.measurements if m.is_blocking_shortfall)

    @property
    def advisory_shortfalls(self) -> tuple[str, ...]:
        """The metric ids of unsatisfied advisory measurements (in stable order)."""
        return tuple(
            m.metric_id
            for m in self.measurements
            if not m.satisfied and m.severity is RuleSeverity.ADVISORY
        )

    @property
    def all_blocking_satisfied(self) -> bool:
        return not self.blocking_shortfalls

    def counts(self) -> dict[str, int]:
        satisfied = sum(1 for m in self.measurements if m.satisfied)
        return {
            "total": len(self.measurements),
            "satisfied": satisfied,
            "unsatisfied": len(self.measurements) - satisfied,
            "blocking_shortfalls": len(self.blocking_shortfalls),
            "advisory_shortfalls": len(self.advisory_shortfalls),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "counts": self.counts(),
            "measurements": [m.to_dict() for m in self.measurements],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class RepositoryTruthInput:
    """A repository-truth closure attestation (consumed input).

    Models the output of a repository-truth closure determination (concepts homed to a
    canonical home, gaps closed) — e.g. a UAKOS closure summary. ``consistent`` is the
    computed invariant the engine aggregates: the store is closed, every concept is
    homed, and no gap category is open.
    """

    snapshot_id: str
    content_sha256: str
    total_concepts: int
    homed_concepts: int
    gaps: Mapping[str, int]
    closed: bool

    @classmethod
    def create(
        cls,
        *,
        snapshot_id: str,
        content_sha256: str,
        total_concepts: int,
        homed_concepts: int,
        gaps: Mapping[str, int] | None = None,
        closed: bool,
    ) -> RepositoryTruthInput:
        """Build a validated repository-truth input (deterministic)."""
        if not isinstance(snapshot_id, str) or not snapshot_id:
            raise CertificationInputError("repository-truth snapshot_id must be a non-empty string")
        if not isinstance(content_sha256, str) or not content_sha256:
            raise CertificationInputError(
                "repository-truth content_sha256 must be a non-empty string"
            )
        if not isinstance(total_concepts, int) or total_concepts < 0:
            raise CertificationInputError(
                "repository-truth total_concepts must be a non-negative int"
            )
        if not isinstance(homed_concepts, int) or homed_concepts < 0:
            raise CertificationInputError(
                "repository-truth homed_concepts must be a non-negative int"
            )
        if homed_concepts > total_concepts:
            raise CertificationInputError(
                "repository-truth homed_concepts cannot exceed total_concepts",
                homed=homed_concepts,
                total=total_concepts,
            )
        gap_map = {}
        for key, value in dict(gaps or {}).items():
            if not isinstance(key, str) or not key:
                raise CertificationInputError(
                    "repository-truth gap category must be a non-empty string"
                )
            if not isinstance(value, int) or value < 0:
                raise CertificationInputError(
                    "repository-truth gap count must be a non-negative int", category=key
                )
            gap_map[key] = value
        return cls(
            snapshot_id=snapshot_id,
            content_sha256=content_sha256,
            total_concepts=total_concepts,
            homed_concepts=homed_concepts,
            gaps=gap_map,
            closed=bool(closed),
        )

    @property
    def gap_total(self) -> int:
        return sum(self.gaps.values())

    @property
    def fully_homed(self) -> bool:
        return self.total_concepts > 0 and self.homed_concepts == self.total_concepts

    @property
    def consistent(self) -> bool:
        """True iff the store is closed, fully homed, and has zero open gaps."""
        return self.closed and self.fully_homed and self.gap_total == 0

    @property
    def open_gap_categories(self) -> tuple[str, ...]:
        return tuple(sorted(k for k, v in self.gaps.items() if v > 0))

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "content_sha256": self.content_sha256,
            "total_concepts": self.total_concepts,
            "homed_concepts": self.homed_concepts,
            "gaps": {k: self.gaps[k] for k in sorted(self.gaps)},
            "gap_total": self.gap_total,
            "closed": self.closed,
            "consistent": self.consistent,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The certification subject (a pure projection of the three inputs).          #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class UniversalCertificationSubject:
    """A normalized projection binding the three consumed inputs to a versioned target.

    Every field is derived **purely** from the validation, measurement, and repository
    -truth inputs, so certification rules and compliance frames aggregate the upstream
    verdicts rather than re-judging any artifact (TP-01, soundness).
    """

    target_id: str
    blueprint_id: str
    version: str
    certification_class: CertificationClass
    validation: ValidationInput
    measurement: MeasurementInput
    repository_truth: RepositoryTruthInput

    @classmethod
    def create(
        cls,
        *,
        validation: ValidationInput,
        measurement: MeasurementInput,
        repository_truth: RepositoryTruthInput,
        version: str,
        target_id: str | None = None,
        blueprint_id: str | None = None,
        certification_class: CertificationClass = CertificationClass.UNIVERSAL_READINESS,
    ) -> UniversalCertificationSubject:
        """Build a subject from the three inputs (fail-closed; no re-derivation)."""
        if not isinstance(validation, ValidationInput):
            raise CertificationSubjectError("subject requires a ValidationInput")
        if not isinstance(measurement, MeasurementInput):
            raise CertificationSubjectError("subject requires a MeasurementInput")
        if not isinstance(repository_truth, RepositoryTruthInput):
            raise CertificationSubjectError("subject requires a RepositoryTruthInput")
        if not isinstance(certification_class, CertificationClass):
            raise CertificationSubjectError("subject requires a CertificationClass")
        resolved_target = target_id or validation.target_id
        resolved_blueprint = blueprint_id or validation.blueprint_id
        if not resolved_target:
            raise CertificationSubjectError("subject has no target_id")
        if not resolved_blueprint:
            raise CertificationSubjectError("subject has no blueprint_id")
        return cls(
            target_id=resolved_target,
            blueprint_id=resolved_blueprint,
            version=version,
            certification_class=certification_class,
            validation=validation,
            measurement=measurement,
            repository_truth=repository_truth,
        )

    def digests(self) -> dict[str, str]:
        """The three consumed-input content digests (evidence anchors)."""
        return {
            "validation": self.validation.digest(),
            "measurement": self.measurement.digest(),
            "repository_truth": self.repository_truth.digest(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "certification_class": self.certification_class.value,
            "validation": self.validation.to_dict(),
            "measurement": self.measurement.to_dict(),
            "repository_truth": self.repository_truth.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# Findings.                                                                   #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class RuleFinding:
    """The immutable outcome of a single certification rule."""

    rule_id: str
    severity: RuleSeverity
    status: RuleStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is RuleStatus.PASS

    @property
    def is_blocking_failure(self) -> bool:
        return self.status is RuleStatus.FAIL and self.severity is RuleSeverity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True, slots=True)
class ComplianceFinding:
    """The immutable outcome of a single compliance frame."""

    frame_id: str
    severity: RuleSeverity
    status: ComplianceStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def conformant(self) -> bool:
        return self.status is ComplianceStatus.CONFORMANT

    @property
    def is_blocking_nonconformance(self) -> bool:
        return (
            self.status is ComplianceStatus.NON_CONFORMANT
            and self.severity is RuleSeverity.BLOCKING
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
        }


# --------------------------------------------------------------------------- #
# The immutable, content-addressed certificate.                              #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class Certificate:
    """An immutable, content-addressed universal certificate.

    The certificate is **immutable** (frozen) and **self-verifying**: its
    ``content_sha256`` is the canonical hash of every field but the id and the hash
    itself, and ``certification_id`` derives from that hash — so any mutation is
    detectable via :meth:`verify_integrity`. It aggregates the validation, measurement,
    and repository-truth evidence *by reference* (their content digests), embeds the
    EC-1 provisional-state disclosure, and asserts ``ENGINEERING-EXECUTION-ONLY``
    authority (it confers no constitutional finality — DE-05).
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
    validation_evidence_ref: str
    measurement_digest: str
    repository_truth_digest: str
    compliance_digest: str
    rules: tuple[RuleFinding, ...]
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
        validation_evidence_ref: str,
        measurement_digest: str,
        repository_truth_digest: str,
        compliance_digest: str,
        rules: tuple[RuleFinding, ...],
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        """The canonical, hashable core of a certificate (excludes id + content hash)."""
        return {
            "target_id": target_id,
            "blueprint_id": blueprint_id,
            "version": version,
            "status": status.value,
            "certification_class": certification_class.value,
            "standard": standard,
            "standard_version": standard_version,
            "authority": authority,
            "validation_evidence_ref": validation_evidence_ref,
            "measurement_digest": measurement_digest,
            "repository_truth_digest": repository_truth_digest,
            "compliance_digest": compliance_digest,
            "rules": [r.to_dict() for r in rules],
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
        validation_evidence_ref: str,
        measurement_digest: str,
        repository_truth_digest: str,
        compliance_digest: str,
        rules: tuple[RuleFinding, ...],
        disclosure: Mapping[str, Any],
        standard: str = UCERT_STANDARD,
        standard_version: str = UCERT_STANDARD_VERSION,
        authority: str = UCERT_AUTHORITY,
    ) -> Certificate:
        """Assemble an immutable, content-addressed :class:`Certificate`."""
        core = cls._core(
            target_id=target_id,
            blueprint_id=blueprint_id,
            version=version,
            status=status,
            certification_class=certification_class,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            validation_evidence_ref=validation_evidence_ref,
            measurement_digest=measurement_digest,
            repository_truth_digest=repository_truth_digest,
            compliance_digest=compliance_digest,
            rules=rules,
            disclosure=disclosure,
        )
        digest = content_hash(core)
        certification_id = f"UCOS-UCERT-{blueprint_id}-{digest[:16]}"
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
            validation_evidence_ref=validation_evidence_ref,
            measurement_digest=measurement_digest,
            repository_truth_digest=repository_truth_digest,
            compliance_digest=compliance_digest,
            rules=rules,
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
                validation_evidence_ref=self.validation_evidence_ref,
                measurement_digest=self.measurement_digest,
                repository_truth_digest=self.repository_truth_digest,
                compliance_digest=self.compliance_digest,
                rules=self.rules,
                disclosure=self.disclosure,
            )
        )

    def verify_integrity(self) -> bool:
        """Return True iff the stored content hash matches a recomputation."""
        return self.recompute_hash() == self.content_sha256

    def require_integrity(self) -> None:
        """Raise :class:`CertificateIntegrityError` if the certificate was mutated."""
        if not self.verify_integrity():
            raise CertificateIntegrityError(
                "certificate integrity check failed (content mutated)",
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
            "validation_evidence_ref": self.validation_evidence_ref,
            "measurement_digest": self.measurement_digest,
            "repository_truth_digest": self.repository_truth_digest,
            "compliance_digest": self.compliance_digest,
            "rules": [r.to_dict() for r in self.rules],
            "disclosure": dict(self.disclosure),
            "content_sha256": self.content_sha256,
        }


__all__ = [
    "UCERT_CONTRACT_VERSION",
    "UCERT_STANDARD",
    "UCERT_STANDARD_VERSION",
    "UCERT_AUTHORITY",
    "DISCLOSURE_CHECK_ID",
    "canonical_json",
    "content_hash",
    "RuleSeverity",
    "RuleStatus",
    "CertificationStatus",
    "CertificationClass",
    "ComplianceStatus",
    "MeasurementComparator",
    "Measurement",
    "ValidationInput",
    "MeasurementInput",
    "RepositoryTruthInput",
    "UniversalCertificationSubject",
    "RuleFinding",
    "ComplianceFinding",
    "Certificate",
]
