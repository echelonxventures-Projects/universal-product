"""UCOS-EPIC-014 — Universal Assurance contracts (Terminal T7).

The immutable, deterministic vocabulary the Universal Assurance Engine speaks. Every
type is **immutable, typed, deterministic, and serializable** and holds no runtime
state, so an identical :class:`AssuranceSubject` assured under an identical policy
yields a byte-identical :class:`AssuranceReport` and content hash (IMP-007 §5) — no
wall-clock or ambient state leaks into any identity.

    * :class:`AssuranceStage` — the ten owned capabilities, in mission order, from
      Validation Planning through Certification Intelligence.
    * :class:`ObligationKind` — what a policy obligation binds to: a reusable validation
      rule, an intelligence dimension, a certification criterion, or a compliance frame.
    * :class:`Severity` / :class:`Outcome` / :class:`Verdict` — fail-closed outcomes.
    * :class:`AssuranceSubject` — the normalized projection of the system under
      assurance; it carries the validation domain facts, the intelligence dimension
      facts, the repository-truth attestation, and external observations. Every stage is
      a pure function of it and of the policy.
    * :class:`StageRecord` — the immutable, measured outcome of one stage.
    * :class:`AssuranceReport` — the content-addressed aggregate across all stages; it
      asserts ``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1
      provisional-state disclosure (DE-05 / IP-01).
    * :class:`AssuranceDashboard` — the deterministic dashboard projection.

Nothing here is hardcoded to a specific system: the vocabulary defines the *shape*, the
concrete facts are supplied by the subject, and every obligation, criterion, gate, and
metric is supplied by the **policy** (:mod:`platform.universal_assurance.policy`).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.universal_assurance.errors import AssuranceSubjectError
from platform.universal_validation.contracts import ValidationDomain, ValidationTarget
from platform.validation_intelligence.contracts import IntelligenceDimension, IntelligenceTarget
from typing import Any

from engine.runtime.disclosure import build_disclosure

#: The semantic version of the Universal Assurance contract surface (AR-03/PL-05).
UNIVERSAL_ASSURANCE_CONTRACT_VERSION = "1.0.0"

#: The assurance report / dashboard format identifiers.
ASSURANCE_REPORT_FORMAT = "ucos-universal-assurance-report/1.0.0"
ASSURANCE_DASHBOARD_FORMAT = "ucos-universal-assurance-dashboard/1.0.0"

#: Universal assurance confers no constitutional authority (DE-05 / IP-01): a run
#: records engineering readiness only. Embedded verbatim in every report.
ASSURANCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

#: The determination strings a completed assurance run may record (fail-closed).
DETERMINATION_ASSURED = "ASSURED"
DETERMINATION_NOT_ASSURED = "NOT-ASSURED"


class AssuranceStage(str, Enum):
    """The ten owned assurance capabilities, in the mission's canonical order."""

    VALIDATION_PLANNING = "validation-planning"
    VALIDATION_GENERATION = "validation-generation"
    VALIDATION_EXECUTION = "validation-execution"
    EVIDENCE_COLLECTION = "evidence-collection"
    CERTIFICATION_PLANNING = "certification-planning"
    CERTIFICATION_EXECUTION = "certification-execution"
    CERTIFICATION_EVIDENCE = "certification-evidence"
    CERTIFICATION_REGISTRY = "certification-registry"
    VALIDATION_INTELLIGENCE = "validation-intelligence"
    CERTIFICATION_INTELLIGENCE = "certification-intelligence"

    @classmethod
    def parse(cls, value: Any) -> AssuranceStage:
        """Parse a stage, raising :class:`AssuranceSubjectError` on an unknown one."""
        try:
            return cls(value)
        except ValueError as exc:
            raise AssuranceSubjectError(
                "unknown assurance stage",
                stage=value,
                supported=[s.value for s in cls],
            ) from exc

    @property
    def order(self) -> int:
        """The canonical (declaration-order) index, for deterministic ordering."""
        return _STAGE_ORDER[self]


_STAGE_ORDER: dict[AssuranceStage, int] = {s: i for i, s in enumerate(AssuranceStage)}


class ObligationKind(str, Enum):
    """What a policy obligation binds to in the reused platform."""

    #: A rule in :mod:`platform.universal_validation.rules` (reused executor).
    VALIDATION_RULE = "validation-rule"
    #: A dimension in :mod:`platform.validation_intelligence` (reused analyzer suite).
    INTELLIGENCE_DIMENSION = "intelligence-dimension"
    #: A rule in :mod:`engine.universal_certification.rules` (reused certifier).
    CERTIFICATION_CRITERION = "certification-criterion"
    #: A compliance frame in :mod:`engine.universal_certification.compliance`.
    CERTIFICATION_FRAME = "certification-frame"

    @property
    def order(self) -> int:
        return _KIND_ORDER[self]


_KIND_ORDER: dict[ObligationKind, int] = {k: i for i, k in enumerate(ObligationKind)}


class Severity(str, Enum):
    """Whether an unsatisfied obligation blocks the verdict or is merely advisory."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class Outcome(str, Enum):
    """The fail-closed outcome of a single obligation, criterion, or metric."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class Verdict(str, Enum):
    """The aggregate verdict of a stage or of a whole assurance run (fail-closed)."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class GateStatus(str, Enum):
    """Whether the assurance gate is open (all blocking obligations discharged)."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


def _require_fact_mapping(raw: Any, *, label: str, subject_id: str) -> dict[str, dict[str, Any]]:
    """Normalize a ``key -> mapping`` facts block, failing closed on a malformed shape."""
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise AssuranceSubjectError(f"{label} must be a mapping", subject_id=subject_id)
    normalized: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not key:
            raise AssuranceSubjectError(
                f"{label} keys must be non-empty strings", subject_id=subject_id
            )
        if not isinstance(value, Mapping):
            raise AssuranceSubjectError(
                f"{label} entries must be mappings", subject_id=subject_id, key=key
            )
        normalized[key] = dict(value)
    return normalized


@dataclass(frozen=True, slots=True)
class AssuranceSubject:
    """A normalized projection of the system under assurance.

    ``validation_facts`` is keyed by :class:`~platform.universal_validation.contracts.
    ValidationDomain` value and ``intelligence_facts`` by
    :class:`~platform.validation_intelligence.contracts.IntelligenceDimension` value, so
    the subject projects directly onto the two reused engines' targets without any
    translation layer. ``repository_truth`` carries the closure attestation the reused
    certifier consumes, and ``observations`` carries externally measured numeric facts
    (e.g. coverage) that policy metrics may reference.
    """

    subject_id: str
    version: str
    blueprint_id: str
    validation_facts: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    intelligence_facts: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    repository_truth: Mapping[str, Any] = field(default_factory=dict)
    observations: Mapping[str, float] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> AssuranceSubject:
        """Assimilate a mapping into a normalized :class:`AssuranceSubject`.

        Raises:
            AssuranceSubjectError: if the mapping is malformed, lacks a subject id or a
                version, names an unknown validation domain or intelligence dimension,
                or carries a non-numeric observation.
        """
        if not isinstance(raw, Mapping):
            raise AssuranceSubjectError("an assurance subject must be a mapping")
        subject_id = raw.get("subject_id")
        if not subject_id or not isinstance(subject_id, str):
            raise AssuranceSubjectError("an assurance subject requires a non-empty subject_id")
        version = raw.get("version")
        if not version or not isinstance(version, str):
            raise AssuranceSubjectError(
                "an assurance subject requires a non-empty version", subject_id=subject_id
            )
        blueprint_id = raw.get("blueprint_id") or subject_id
        if not isinstance(blueprint_id, str):
            raise AssuranceSubjectError("blueprint_id must be a string", subject_id=subject_id)

        validation_facts = _require_fact_mapping(
            raw.get("validation_facts"), label="validation_facts", subject_id=subject_id
        )
        for key in validation_facts:
            ValidationDomain.parse(key)
        intelligence_facts = _require_fact_mapping(
            raw.get("intelligence_facts"), label="intelligence_facts", subject_id=subject_id
        )
        for key in intelligence_facts:
            if key not in {d.value for d in IntelligenceDimension}:
                raise AssuranceSubjectError(
                    "unknown intelligence dimension",
                    subject_id=subject_id,
                    dimension=key,
                    supported=[d.value for d in IntelligenceDimension],
                )

        raw_truth = raw.get("repository_truth", {})
        if not isinstance(raw_truth, Mapping):
            raise AssuranceSubjectError("repository_truth must be a mapping", subject_id=subject_id)

        observations = cls._parse_observations(raw.get("observations"), subject_id)
        return cls(
            subject_id=subject_id,
            version=version,
            blueprint_id=blueprint_id,
            validation_facts=validation_facts,
            intelligence_facts=intelligence_facts,
            repository_truth=dict(raw_truth),
            observations=observations,
        )

    @staticmethod
    def _parse_observations(raw: Any, subject_id: str) -> dict[str, float]:
        if raw is None:
            return {}
        if not isinstance(raw, Mapping):
            raise AssuranceSubjectError("observations must be a mapping", subject_id=subject_id)
        parsed: dict[str, float] = {}
        for key, value in raw.items():
            if not isinstance(key, str) or not key:
                raise AssuranceSubjectError(
                    "observation keys must be non-empty strings", subject_id=subject_id
                )
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise AssuranceSubjectError(
                    "observation values must be numeric", subject_id=subject_id, key=key
                )
            parsed[key] = float(value)
        return parsed

    # -- projections onto the reused engines -----------------------------------

    def declared_domains(self) -> tuple[ValidationDomain, ...]:
        """The validation domains for which the subject supplies facts, in order."""
        domains = [ValidationDomain.parse(key) for key in self.validation_facts]
        return tuple(sorted(domains, key=lambda d: d.order))

    def declared_dimensions(self) -> tuple[IntelligenceDimension, ...]:
        """The intelligence dimensions for which the subject supplies facts, in order."""
        dimensions = [IntelligenceDimension(key) for key in self.intelligence_facts]
        return tuple(sorted(dimensions, key=lambda d: d.order))

    def build_validation_target(self) -> ValidationTarget:
        """Project onto the reused Universal Validation target (no translation)."""
        return ValidationTarget(target_id=self.subject_id, facts=self.validation_facts)

    def build_intelligence_target(self) -> IntelligenceTarget:
        """Project onto the reused Validation Intelligence target (no translation)."""
        return IntelligenceTarget(target_id=self.subject_id, facts=self.intelligence_facts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "version": self.version,
            "blueprint_id": self.blueprint_id,
            "validation_facts": {
                key: dict(value) for key, value in sorted(self.validation_facts.items())
            },
            "intelligence_facts": {
                key: dict(value) for key, value in sorted(self.intelligence_facts.items())
            },
            "repository_truth": dict(self.repository_truth),
            "observations": {key: self.observations[key] for key in sorted(self.observations)},
        }

    def digest(self) -> str:
        """The deterministic content hash of the subject (a stable subject identity)."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class StageRecord:
    """The immutable, measured outcome of one assurance stage."""

    stage: AssuranceStage
    verdict: Verdict
    obligations_total: int
    obligations_satisfied: int
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    artifact_sha256: str
    summary: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        stage: AssuranceStage,
        obligations_total: int,
        obligations_satisfied: int,
        blocking_failures: Iterable[str] = (),
        advisory_failures: Iterable[str] = (),
        artifact_sha256: str,
        summary: Mapping[str, Any] | None = None,
    ) -> StageRecord:
        """Aggregate one stage; the verdict is FAIL iff a blocking obligation failed."""
        blocking = tuple(sorted({str(item) for item in blocking_failures}))
        advisory = tuple(sorted({str(item) for item in advisory_failures}))
        return cls(
            stage=stage,
            verdict=Verdict.FAIL if blocking else Verdict.PASS,
            obligations_total=obligations_total,
            obligations_satisfied=obligations_satisfied,
            blocking_failures=blocking,
            advisory_failures=advisory,
            artifact_sha256=artifact_sha256,
            summary=dict(summary or {}),
        )

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    @property
    def coverage(self) -> float:
        """The satisfied/total obligation ratio (1.0 when a stage has no obligations)."""
        if self.obligations_total <= 0:
            return 1.0
        return self.obligations_satisfied / self.obligations_total

    def core(self) -> dict[str, Any]:
        """The canonical, hashable core of the record (excludes volatile summary detail)."""
        return {
            "stage": self.stage.value,
            "verdict": self.verdict.value,
            "obligations_total": self.obligations_total,
            "obligations_satisfied": self.obligations_satisfied,
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "artifact_sha256": self.artifact_sha256,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "coverage": self.coverage, "summary": dict(self.summary)}


@dataclass(frozen=True, slots=True)
class AssuranceReport:
    """The content-addressed aggregate of a full ten-stage assurance run.

    The report is a **pure function of the subject, the policy, and the ordered stage
    outcomes**: ``report_sha256`` hashes only the stage cores (never volatile summary
    detail or any wall-clock), so an identical subject assured under an identical policy
    reproduces a byte-identical report. It asserts ``ENGINEERING-EXECUTION-ONLY``
    authority and carries the EC-1 provisional-state disclosure (DE-05 / IP-01).
    """

    subject_id: str
    verdict: Verdict
    determination: str
    gate: GateStatus
    subject_digest: str
    policy_digest: str
    stage_records: tuple[StageRecord, ...]
    authority: str
    disclosure: Mapping[str, Any]
    report_sha256: str

    @staticmethod
    def _core(
        *,
        subject_id: str,
        verdict: Verdict,
        determination: str,
        gate: GateStatus,
        subject_digest: str,
        policy_digest: str,
        stage_records: tuple[StageRecord, ...],
        authority: str,
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "subject_id": subject_id,
            "verdict": verdict.value,
            "determination": determination,
            "gate": gate.value,
            "subject_digest": subject_digest,
            "policy_digest": policy_digest,
            "stages": [record.core() for record in stage_records],
            "authority": authority,
            "disclosure": dict(disclosure),
        }

    @classmethod
    def create(
        cls,
        *,
        subject_id: str,
        subject_digest: str,
        policy_digest: str,
        stage_records: Iterable[StageRecord],
    ) -> AssuranceReport:
        """Aggregate stage records into an immutable, content-addressed report.

        The verdict is fail-closed: FAIL iff any stage recorded a *blocking* failure.
        Stage records are ordered canonically so an identical set of outcomes always
        hashes identically regardless of the order in which stages completed.
        """
        records = tuple(sorted(stage_records, key=lambda r: r.stage.order))
        verdict = Verdict.FAIL if any(r.verdict is Verdict.FAIL for r in records) else Verdict.PASS
        determination = (
            DETERMINATION_ASSURED if verdict is Verdict.PASS else DETERMINATION_NOT_ASSURED
        )
        gate = GateStatus.OPEN if verdict is Verdict.PASS else GateStatus.CLOSED
        disclosure = build_disclosure()
        core = cls._core(
            subject_id=subject_id,
            verdict=verdict,
            determination=determination,
            gate=gate,
            subject_digest=subject_digest,
            policy_digest=policy_digest,
            stage_records=records,
            authority=ASSURANCE_AUTHORITY,
            disclosure=disclosure,
        )
        return cls(
            subject_id=subject_id,
            verdict=verdict,
            determination=determination,
            gate=gate,
            subject_digest=subject_digest,
            policy_digest=policy_digest,
            stage_records=records,
            authority=ASSURANCE_AUTHORITY,
            disclosure=disclosure,
            report_sha256=content_hash(core),
        )

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def stages_run(self) -> tuple[str, ...]:
        return tuple(record.stage.value for record in self.stage_records)

    def stage_verdicts(self) -> dict[str, str]:
        return {record.stage.value: record.verdict.value for record in self.stage_records}

    def record_for(self, stage: AssuranceStage) -> StageRecord | None:
        """The record for ``stage``, or ``None`` when that stage did not run."""
        for record in self.stage_records:
            if record.stage is stage:
                return record
        return None

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(
            f"{record.stage.value}:{item}"
            for record in self.stage_records
            for item in record.blocking_failures
        )

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(
            f"{record.stage.value}:{item}"
            for record in self.stage_records
            for item in record.advisory_failures
        )

    def counts(self) -> dict[str, int]:
        records = self.stage_records
        return {
            "stages": len(records),
            "stages_passed": sum(1 for r in records if r.passed),
            "stages_failed": sum(1 for r in records if not r.passed),
            "obligations_total": sum(r.obligations_total for r in records),
            "obligations_satisfied": sum(r.obligations_satisfied for r in records),
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
        }

    def dashboard(self) -> AssuranceDashboard:
        """Project the deterministic Assurance Dashboard from this report."""
        return AssuranceDashboard.from_report(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": ASSURANCE_REPORT_FORMAT,
            "subject_id": self.subject_id,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "determination": self.determination,
            "gate": self.gate.value,
            "subject_digest": self.subject_digest,
            "policy_digest": self.policy_digest,
            "counts": self.counts(),
            "stage_verdicts": self.stage_verdicts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "stages": [record.to_dict() for record in self.stage_records],
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
            "report_sha256": self.report_sha256,
        }


@dataclass(frozen=True, slots=True)
class AssuranceDashboard:
    """A deterministic, content-addressed dashboard projection of an assurance run."""

    subject_id: str
    verdict: Verdict
    determination: str
    gate: GateStatus
    stages_total: int
    stages_passed: int
    obligations_total: int
    obligations_satisfied: int
    stage_verdicts: Mapping[str, str]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    dashboard_sha256: str

    @classmethod
    def from_report(cls, report: AssuranceReport) -> AssuranceDashboard:
        counts = report.counts()
        core = {
            "subject_id": report.subject_id,
            "verdict": report.verdict.value,
            "determination": report.determination,
            "gate": report.gate.value,
            "stages_total": counts["stages"],
            "stages_passed": counts["stages_passed"],
            "obligations_total": counts["obligations_total"],
            "obligations_satisfied": counts["obligations_satisfied"],
            "stage_verdicts": report.stage_verdicts(),
            "blocking_failures": list(report.blocking_failures()),
            "advisory_failures": list(report.advisory_failures()),
        }
        return cls(
            subject_id=report.subject_id,
            verdict=report.verdict,
            determination=report.determination,
            gate=report.gate,
            stages_total=counts["stages"],
            stages_passed=counts["stages_passed"],
            obligations_total=counts["obligations_total"],
            obligations_satisfied=counts["obligations_satisfied"],
            stage_verdicts=report.stage_verdicts(),
            blocking_failures=report.blocking_failures(),
            advisory_failures=report.advisory_failures(),
            dashboard_sha256=content_hash(core),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dashboard_format": ASSURANCE_DASHBOARD_FORMAT,
            "subject_id": self.subject_id,
            "verdict": self.verdict.value,
            "determination": self.determination,
            "gate": self.gate.value,
            "stages_total": self.stages_total,
            "stages_passed": self.stages_passed,
            "obligations_total": self.obligations_total,
            "obligations_satisfied": self.obligations_satisfied,
            "stage_verdicts": dict(self.stage_verdicts),
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "dashboard_sha256": self.dashboard_sha256,
        }


__all__ = [
    "UNIVERSAL_ASSURANCE_CONTRACT_VERSION",
    "ASSURANCE_REPORT_FORMAT",
    "ASSURANCE_DASHBOARD_FORMAT",
    "ASSURANCE_AUTHORITY",
    "DETERMINATION_ASSURED",
    "DETERMINATION_NOT_ASSURED",
    "AssuranceStage",
    "ObligationKind",
    "Severity",
    "Outcome",
    "Verdict",
    "GateStatus",
    "AssuranceSubject",
    "StageRecord",
    "AssuranceReport",
    "AssuranceDashboard",
]
