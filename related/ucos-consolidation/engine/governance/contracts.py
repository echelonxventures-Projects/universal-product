"""EPIC-VAL-003 — Repository Governance Pipeline contracts (Terminal T3).

The value types that flow across the Repository Governance Pipeline boundary. Every
type is **immutable, typed, deterministic, and serializable** and holds no runtime
state:

    * :class:`GovernanceStatus` — the aggregate governance verdict (fail-closed
      GOVERNED / NOT-GOVERNED).
    * :class:`GovernanceUnit` — one implementation unit to be driven through the
      full Validation → Certification pipeline (carries the reused
      :class:`~engine.validation.contracts.ValidationSubject`, plus the
      acceptance-relevant unit metadata that validation cannot derive: owner,
      registration, traceability).
    * :class:`GovernanceInput` — the assimilated repository the pipeline governs: a
      non-empty set of units plus the repository-level acceptance facts.
    * :class:`StageOutcome` — the immutable, per-stage (validation / certification /
      acceptance) pass/fail summary the unified decision aggregates.
    * :class:`RepositoryDecision` — the **unified repository decision**: the single,
      content-addressed, fail-closed verdict aggregating all three stages.

The pipeline invents no verdict (TP-01): the unified decision is GOVERNED **iff**
every stage passed — a single failing stage fails the whole determination closed.
Every hash is over the canonical JSON encoding reused from the Acceptance Layer, so
an identical input yields a byte-identical decision (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from engine.acceptance.contracts import canonical_json, content_hash
from engine.certification.contracts import CertificationClass
from engine.governance.errors import GovernanceInputError

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.validation.contracts import ValidationSubject

#: The semantic version of the Governance Pipeline contract surface (AR-03/PL-05).
GOVERNANCE_CONTRACT_VERSION = "1.0.0"

#: The governance standard the pipeline attests against (record-only, IMP-007 §13).
GOVERNANCE_STANDARD = "UCOS-REPOSITORY-GOVERNANCE-STANDARD"
GOVERNANCE_STANDARD_VERSION = "1.0.0"

#: Governance confers no constitutional authority (DE-05 / IP-01): it records the
#: engineering-readiness verdict only. Embedded verbatim in every unified decision.
GOVERNANCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

#: The three ordered stages of the constitutional governance pipeline.
VALIDATION_STAGE = "validation"
CERTIFICATION_STAGE = "certification"
ACCEPTANCE_STAGE = "acceptance"
GOVERNANCE_STAGES: tuple[str, ...] = (
    VALIDATION_STAGE,
    CERTIFICATION_STAGE,
    ACCEPTANCE_STAGE,
)


class GovernanceStatus(str, Enum):
    """The aggregate verdict of a repository governance determination (fail-closed)."""

    GOVERNED = "governed"
    NOT_GOVERNED = "not-governed"


# ---------------------------------------------------------------------------
# pipeline input
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class GovernanceUnit:
    """One implementation unit driven through the Validation → Certification flow.

    The unit carries the reused Validation Layer subject (never a re-implemented
    validator) plus the acceptance-relevant facts that validation cannot derive: its
    resolved ``owner``, whether it is ``registered``, and its traceability stages.
    The pipeline computes ``validated`` and ``certified`` from the real engine runs —
    they are never supplied by the caller (soundness, TP-01).
    """

    unit_id: str
    subject: ValidationSubject
    version: str = "0.0.0"
    owner: str | None = None
    registered: bool = False
    traceability: tuple[str, ...] = ()
    certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS

    def __post_init__(self) -> None:
        if not self.unit_id:
            raise GovernanceInputError("governance unit requires a non-empty unit_id")
        if getattr(self.subject, "target_id", None) is None:
            raise GovernanceInputError(
                "governance unit requires a validation subject",
                unit_id=self.unit_id,
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "version": self.version,
            "owner": self.owner,
            "registered": self.registered,
            "traceability": list(self.traceability),
            "certification_class": self.certification_class.value,
            "subject": self.subject.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class GovernanceInput:
    """The assimilated repository the pipeline governs end to end.

    ``units`` is the non-empty set of implementation units to validate and certify;
    ``repository_facts`` is the repository-level acceptance facts mapping (ownership
    is per-unit, but dependencies, reuse, inventory, coverage, integrations,
    architecture, health, and freeze blockers are repository-wide). The pipeline
    derives the per-unit ``validated`` / ``certified`` acceptance facts from the real
    engine runs and merges them with ``repository_facts`` — the caller never asserts
    a validation or certification verdict directly.
    """

    repository_id: str
    epic_id: str
    units: tuple[GovernanceUnit, ...]
    repository_facts: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.repository_id or not self.epic_id:
            raise GovernanceInputError(
                "governance input requires a repository_id and an epic_id",
                repository_id=self.repository_id,
                epic_id=self.epic_id,
            )
        if not self.units:
            raise GovernanceInputError(
                "governance input requires at least one unit (nothing is governed "
                "vacuously — fail-closed)",
                repository_id=self.repository_id,
            )
        if not isinstance(self.repository_facts, Mapping):
            raise GovernanceInputError(
                "repository_facts must be a mapping", repository_id=self.repository_id
            )
        seen: set[str] = set()
        for unit in self.units:
            if unit.unit_id in seen:
                raise GovernanceInputError("duplicate governance unit id", unit_id=unit.unit_id)
            seen.add(unit.unit_id)

    def ordered_units(self) -> tuple[GovernanceUnit, ...]:
        """The units in stable id order (deterministic pipeline execution)."""
        return tuple(sorted(self.units, key=lambda u: u.unit_id))

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "units": [u.to_dict() for u in self.ordered_units()],
            "repository_facts": dict(self.repository_facts),
        }


# ---------------------------------------------------------------------------
# per-stage outcome
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class StageOutcome:
    """The immutable pass/fail summary of one governance stage (fail-closed).

    A stage passes iff at least one item was evaluated and none failed — an empty
    stage never passes vacuously (fail-closed). ``failures`` names the failing items
    (unit ids for validation/certification, gate ids for acceptance), so the unified
    decision is fully attributable.
    """

    stage: str
    passed: bool
    total: int
    passed_count: int
    failures: tuple[str, ...] = ()

    @classmethod
    def of(cls, stage: str, *, total: int, failures: tuple[str, ...]) -> StageOutcome:
        """Build a stage outcome from a total count and its failing item ids."""
        failed = len(failures)
        passed_count = total - failed
        passed = total > 0 and failed == 0
        return cls(
            stage=stage,
            passed=passed,
            total=total,
            passed_count=passed_count,
            failures=failures,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "passed": self.passed,
            "total": self.total,
            "passed_count": self.passed_count,
            "failed": len(self.failures),
            "failures": list(self.failures),
        }


# ---------------------------------------------------------------------------
# the unified repository decision
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class RepositoryDecision:
    """The unified, content-addressed repository governance decision (fail-closed).

    The decision aggregates the three stage outcomes into a single verdict: the
    repository is GOVERNED **iff** validation, certification, and acceptance all
    passed. It is self-verifying — its ``decision_sha256`` is the canonical hash of
    every field but the hash itself — so any mutation is detectable via
    :meth:`verify_integrity`. It embeds the EC-1 provisional-state disclosure and
    asserts ``ENGINEERING-EXECUTION-ONLY`` authority (governance confers no
    constitutional finality — DE-05 / IP-01).
    """

    repository_id: str
    epic_id: str
    status: GovernanceStatus
    validation_passed: bool
    certification_passed: bool
    acceptance_passed: bool
    stages: tuple[StageOutcome, ...]
    blocking_reasons: tuple[str, ...]
    standard: str
    standard_version: str
    authority: str
    disclosure: Mapping[str, Any]
    decision_sha256: str

    @staticmethod
    def _core(
        *,
        repository_id: str,
        epic_id: str,
        status: GovernanceStatus,
        stages: tuple[StageOutcome, ...],
        blocking_reasons: tuple[str, ...],
        standard: str,
        standard_version: str,
        authority: str,
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        """The canonical, hashable core of a decision (excludes the content hash)."""
        return {
            "repository_id": repository_id,
            "epic_id": epic_id,
            "status": status.value,
            "stages": [s.to_dict() for s in stages],
            "blocking_reasons": list(blocking_reasons),
            "standard": standard,
            "standard_version": standard_version,
            "authority": authority,
            "disclosure": dict(disclosure),
        }

    @classmethod
    def create(
        cls,
        *,
        repository_id: str,
        epic_id: str,
        validation: StageOutcome,
        certification: StageOutcome,
        acceptance: StageOutcome,
        disclosure: Mapping[str, Any],
        standard: str = GOVERNANCE_STANDARD,
        standard_version: str = GOVERNANCE_STANDARD_VERSION,
        authority: str = GOVERNANCE_AUTHORITY,
    ) -> RepositoryDecision:
        """Aggregate the three stage outcomes into a fail-closed unified decision."""
        stages = (validation, certification, acceptance)
        governed = validation.passed and certification.passed and acceptance.passed
        status = GovernanceStatus.GOVERNED if governed else GovernanceStatus.NOT_GOVERNED
        blocking_reasons = tuple(
            f"{stage.stage}:{item}" for stage in stages for item in stage.failures
        )
        core = cls._core(
            repository_id=repository_id,
            epic_id=epic_id,
            status=status,
            stages=stages,
            blocking_reasons=blocking_reasons,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            disclosure=disclosure,
        )
        return cls(
            repository_id=repository_id,
            epic_id=epic_id,
            status=status,
            validation_passed=validation.passed,
            certification_passed=certification.passed,
            acceptance_passed=acceptance.passed,
            stages=stages,
            blocking_reasons=blocking_reasons,
            standard=standard,
            standard_version=standard_version,
            authority=authority,
            disclosure=dict(disclosure),
            decision_sha256=content_hash(core),
        )

    @property
    def governed(self) -> bool:
        return self.status is GovernanceStatus.GOVERNED

    def recompute_hash(self) -> str:
        """Recompute the content hash from the current field values."""
        return content_hash(
            self._core(
                repository_id=self.repository_id,
                epic_id=self.epic_id,
                status=self.status,
                stages=self.stages,
                blocking_reasons=self.blocking_reasons,
                standard=self.standard,
                standard_version=self.standard_version,
                authority=self.authority,
                disclosure=self.disclosure,
            )
        )

    def verify_integrity(self) -> bool:
        """Return True iff the stored content hash matches a recomputation."""
        return self.recompute_hash() == self.decision_sha256

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "status": self.status.value,
            "governed": self.governed,
            "validation_passed": self.validation_passed,
            "certification_passed": self.certification_passed,
            "acceptance_passed": self.acceptance_passed,
            "stages": [s.to_dict() for s in self.stages],
            "blocking_reasons": list(self.blocking_reasons),
            "standard": self.standard,
            "standard_version": self.standard_version,
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
            "decision_sha256": self.decision_sha256,
        }


__all__ = [
    "GOVERNANCE_CONTRACT_VERSION",
    "GOVERNANCE_STANDARD",
    "GOVERNANCE_STANDARD_VERSION",
    "GOVERNANCE_AUTHORITY",
    "VALIDATION_STAGE",
    "CERTIFICATION_STAGE",
    "ACCEPTANCE_STAGE",
    "GOVERNANCE_STAGES",
    "canonical_json",
    "content_hash",
    "GovernanceStatus",
    "GovernanceUnit",
    "GovernanceInput",
    "StageOutcome",
    "RepositoryDecision",
]
