"""EPIC-PLAT-003 — Repository Operations contracts (Terminal T5).

The immutable, deterministic value types the Repository Operations Runtime speaks.
Every type is **immutable, typed, deterministic, and serializable** and holds no
runtime state, so an identical configuration and an identical ordered set of stage
outcomes yield a byte-identical :class:`ExecutionReport`, :class:`RepositoryDashboard`,
and content hash (IMP-007 §5) — no wall-clock or ambient state leaks into any identity.

    * :class:`StageKind` — the kind of a pipeline stage; each maps to a canonical
      engine or a canonical script (no parallel tooling is ever introduced).
    * :class:`StageOutcome` / :class:`OperationsVerdict` — fail-closed outcomes.
    * :class:`StageSpec` — one declarative, configuration-driven stage (no hardcoding).
    * :class:`OperationsConfig` — the whole declarative pipeline.
    * :class:`StageResult` — the immutable outcome of one executed stage.
    * :class:`CoverageSummary` — the parsed coverage report (Coverage Reports).
    * :class:`ExecutionReport` — the content-addressed aggregate (Execution Reports).
    * :class:`RepositoryDashboard` — the deterministic dashboard projection
      (Repository Dashboards).

Nothing here is hardcoded to a specific pipeline: the vocabulary defines the *shape*;
the concrete stages are supplied by the configuration.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.repository_operations.errors import (
    OperationsConfigError,
    StageDefinitionError,
)
from typing import Any

from engine.runtime.disclosure import build_disclosure

#: The semantic version of the Repository Operations contract surface (AR-03/PL-05).
REPOSITORY_OPERATIONS_CONTRACT_VERSION = "1.0.0"

#: The operational-verification report format identifier.
EXECUTION_REPORT_FORMAT = "ucos-repository-operations-report/1.0.0"

#: The dashboard format identifier.
DASHBOARD_FORMAT = "ucos-repository-operations-dashboard/1.0.0"

#: Repository operations confer no constitutional authority (DE-05 / IP-01): the run
#: records engineering readiness only. Embedded verbatim in every report.
OPERATIONS_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"


class StageKind(str, Enum):
    """The kind of a pipeline stage. Each kind reuses existing canonical machinery."""

    #: Run a canonical script/target (``verify.sh`` / ``doctor.sh`` / ``bootstrap.sh`` / make).
    COMMAND = "command"
    #: Run the certified EC-1 Repository Acceptance engine over assimilated facts.
    ACCEPTANCE = "acceptance"
    #: Run the certified EC-1 Validation engine over a normalized subject.
    VALIDATION = "validation"
    #: Run the certified EC-1 Certification engine (validation → evidence → certify).
    CERTIFICATION = "certification"
    #: Run the certified frozen-corpus guard (Architecture Freeze Check).
    FREEZE = "freeze"
    #: Parse a coverage report produced by the canonical coverage tool.
    COVERAGE = "coverage"

    @classmethod
    def parse(cls, value: Any) -> StageKind:
        """Parse a stage kind, raising :class:`StageDefinitionError` on an unknown one."""
        try:
            return cls(value)
        except ValueError as exc:
            raise StageDefinitionError(
                "unknown stage kind",
                kind=value,
                supported=[k.value for k in cls],
            ) from exc


class StageOutcome(str, Enum):
    """The fail-closed outcome of a single executed (or resumed) stage."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"  # reused from a checkpoint on a resumed run


class OperationsVerdict(str, Enum):
    """The aggregate verdict of a repository operations run (fail-closed)."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


# ---------------------------------------------------------------------------
# declarative, configuration-driven pipeline
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class StageSpec:
    """One declarative pipeline stage (configuration-driven; nothing is hardcoded)."""

    stage_id: str
    kind: StageKind
    params: Mapping[str, Any] = field(default_factory=dict)
    #: A failing *blocking* stage fails the run verdict; a non-blocking (advisory)
    #: stage is recorded but never fails the verdict.
    blocking: bool = True

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> StageSpec:
        """Assimilate a stage declaration into a normalized :class:`StageSpec`."""
        if not isinstance(raw, Mapping):
            raise StageDefinitionError("a stage declaration must be a mapping")
        stage_id = raw.get("stage_id")
        if not stage_id or not isinstance(stage_id, str):
            raise StageDefinitionError("a stage requires a non-empty string stage_id")
        params = raw.get("params", {})
        if not isinstance(params, Mapping):
            raise StageDefinitionError("stage params must be a mapping", stage_id=stage_id)
        return cls(
            stage_id=stage_id,
            kind=StageKind.parse(raw.get("kind")),
            params=dict(params),
            blocking=bool(raw.get("blocking", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "kind": self.kind.value,
            "params": dict(self.params),
            "blocking": self.blocking,
        }


@dataclass(frozen=True, slots=True)
class OperationsConfig:
    """The whole declarative repository-operations pipeline (single source of truth)."""

    repository_id: str
    epic_id: str
    stages: tuple[StageSpec, ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> OperationsConfig:
        """Assimilate a configuration mapping into a normalized :class:`OperationsConfig`.

        Raises:
            OperationsConfigError: if the mapping is malformed, lacks identity, declares
                no stages, or declares duplicate stage ids (resumability keys on ids).
        """
        if not isinstance(raw, Mapping):
            raise OperationsConfigError("repository-operations config must be a mapping")
        repository_id = raw.get("repository_id")
        epic_id = raw.get("epic_id")
        if not repository_id or not epic_id:
            raise OperationsConfigError(
                "config requires a repository_id and an epic_id",
                repository_id=repository_id,
                epic_id=epic_id,
            )
        raw_stages = raw.get("stages")
        if not isinstance(raw_stages, Sequence) or isinstance(raw_stages, str | bytes):
            raise OperationsConfigError("config requires a list of stages")
        stages = tuple(StageSpec.from_mapping(s) for s in raw_stages)
        if not stages:
            raise OperationsConfigError("config declares no stages")
        seen: set[str] = set()
        duplicates: set[str] = set()
        for spec in stages:
            if spec.stage_id in seen:
                duplicates.add(spec.stage_id)
            seen.add(spec.stage_id)
        if duplicates:
            raise OperationsConfigError("duplicate stage ids", duplicates=sorted(duplicates))
        return cls(
            repository_id=str(repository_id),
            epic_id=str(epic_id),
            stages=stages,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "stages": [s.to_dict() for s in self.stages],
        }

    def digest(self) -> str:
        """The deterministic content hash of the configuration (checkpoint key)."""
        return content_hash(self.to_dict())


# ---------------------------------------------------------------------------
# per-stage and coverage results
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class StageResult:
    """The immutable, deterministic outcome of one executed (or resumed) stage."""

    stage_id: str
    kind: StageKind
    outcome: StageOutcome
    blocking: bool
    summary: str
    evidence_ref: str = ""
    detail: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        spec: StageSpec,
        outcome: StageOutcome,
        summary: str,
        *,
        evidence_ref: str = "",
        detail: Mapping[str, Any] | None = None,
    ) -> StageResult:
        """Build a result for ``spec`` (inheriting its id/kind/blocking severity)."""
        return cls(
            stage_id=spec.stage_id,
            kind=spec.kind,
            outcome=outcome,
            blocking=spec.blocking,
            summary=summary,
            evidence_ref=evidence_ref,
            detail=dict(detail or {}),
        )

    @property
    def passed(self) -> bool:
        return self.outcome is StageOutcome.PASSED

    @property
    def failed(self) -> bool:
        return self.outcome is StageOutcome.FAILED

    @property
    def skipped(self) -> bool:
        return self.outcome is StageOutcome.SKIPPED

    @property
    def is_blocking_failure(self) -> bool:
        return self.failed and self.blocking

    def core(self) -> dict[str, Any]:
        """The canonical, hashable core of the result (excludes volatile detail)."""
        return {
            "stage_id": self.stage_id,
            "kind": self.kind.value,
            "outcome": self.outcome.value,
            "blocking": self.blocking,
            "summary": self.summary,
            "evidence_ref": self.evidence_ref,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "detail": dict(self.detail)}


@dataclass(frozen=True, slots=True)
class CoverageSummary:
    """The parsed coverage report (Coverage Reports), from the canonical coverage tool."""

    line_rate: float
    branch_rate: float
    lines_covered: int
    lines_valid: int
    branches_covered: int
    branches_valid: int

    @property
    def line_percent(self) -> float:
        return round(self.line_rate * 100.0, 4)

    @property
    def branch_percent(self) -> float:
        return round(self.branch_rate * 100.0, 4)

    def meets(self, min_percent: float) -> bool:
        """True iff the line coverage meets or exceeds ``min_percent``."""
        return self.line_percent >= min_percent

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_rate": self.line_rate,
            "branch_rate": self.branch_rate,
            "line_percent": self.line_percent,
            "branch_percent": self.branch_percent,
            "lines_covered": self.lines_covered,
            "lines_valid": self.lines_valid,
            "branches_covered": self.branches_covered,
            "branches_valid": self.branches_valid,
        }


# ---------------------------------------------------------------------------
# the content-addressed execution report + dashboard
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class ExecutionReport:
    """The content-addressed aggregate of a repository operations run (Execution Reports).

    The report is a **pure function of the configuration and the ordered stage
    outcomes**: its ``report_sha256`` hashes only the stage cores (never the volatile
    per-stage detail, durations, or any wall-clock), so an identical pipeline over
    identical outcomes reproduces a byte-identical report. It asserts
    ``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1 provisional-state
    disclosure (DE-05 / IP-01).
    """

    repository_id: str
    epic_id: str
    verdict: OperationsVerdict
    config_digest: str
    stage_results: tuple[StageResult, ...]
    coverage: CoverageSummary | None
    resumed: bool
    authority: str
    disclosure: Mapping[str, Any]
    report_sha256: str

    @staticmethod
    def _core(
        *,
        repository_id: str,
        epic_id: str,
        verdict: OperationsVerdict,
        config_digest: str,
        stage_results: tuple[StageResult, ...],
        coverage: CoverageSummary | None,
        authority: str,
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "repository_id": repository_id,
            "epic_id": epic_id,
            "verdict": verdict.value,
            "config_digest": config_digest,
            "stages": [r.core() for r in stage_results],
            "coverage": coverage.to_dict() if coverage is not None else None,
            "authority": authority,
            "disclosure": dict(disclosure),
        }

    @classmethod
    def create(
        cls,
        *,
        repository_id: str,
        epic_id: str,
        config_digest: str,
        stage_results: tuple[StageResult, ...],
        coverage: CoverageSummary | None = None,
        resumed: bool = False,
    ) -> ExecutionReport:
        """Aggregate stage results into an immutable, content-addressed report.

        The verdict is fail-closed: FAIL iff any *blocking* stage failed.
        """
        verdict = (
            OperationsVerdict.FAIL
            if any(r.is_blocking_failure for r in stage_results)
            else OperationsVerdict.PASS
        )
        disclosure = build_disclosure()
        core = cls._core(
            repository_id=repository_id,
            epic_id=epic_id,
            verdict=verdict,
            config_digest=config_digest,
            stage_results=stage_results,
            coverage=coverage,
            authority=OPERATIONS_AUTHORITY,
            disclosure=disclosure,
        )
        return cls(
            repository_id=repository_id,
            epic_id=epic_id,
            verdict=verdict,
            config_digest=config_digest,
            stage_results=stage_results,
            coverage=coverage,
            resumed=resumed,
            authority=OPERATIONS_AUTHORITY,
            disclosure=disclosure,
            report_sha256=content_hash(core),
        )

    @property
    def passed(self) -> bool:
        return self.verdict is OperationsVerdict.PASS

    def counts(self) -> dict[str, int]:
        return {
            "total": len(self.stage_results),
            "passed": sum(1 for r in self.stage_results if r.passed),
            "failed": sum(1 for r in self.stage_results if r.failed),
            "skipped": sum(1 for r in self.stage_results if r.skipped),
            "blocking_failed": sum(1 for r in self.stage_results if r.is_blocking_failure),
        }

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(r.stage_id for r in self.stage_results if r.is_blocking_failure)

    def dashboard(self) -> RepositoryDashboard:
        """Project the deterministic Repository Dashboard from this report."""
        return RepositoryDashboard.from_report(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": EXECUTION_REPORT_FORMAT,
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "config_digest": self.config_digest,
            "counts": self.counts(),
            "blocking_failures": list(self.blocking_failures()),
            "stages": [r.to_dict() for r in self.stage_results],
            "coverage": self.coverage.to_dict() if self.coverage is not None else None,
            "resumed": self.resumed,
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
            "report_sha256": self.report_sha256,
        }


@dataclass(frozen=True, slots=True)
class RepositoryDashboard:
    """A deterministic, content-addressed dashboard projection (Repository Dashboards)."""

    repository_id: str
    epic_id: str
    verdict: OperationsVerdict
    stages_total: int
    stages_passed: int
    stages_failed: int
    stages_skipped: int
    blocking_failures: tuple[str, ...]
    stage_status: dict[str, str]
    coverage_line_percent: float | None
    dashboard_sha256: str

    @classmethod
    def from_report(cls, report: ExecutionReport) -> RepositoryDashboard:
        counts = report.counts()
        stage_status = {r.stage_id: r.outcome.value for r in report.stage_results}
        coverage_line_percent = (
            report.coverage.line_percent if report.coverage is not None else None
        )
        core = {
            "repository_id": report.repository_id,
            "epic_id": report.epic_id,
            "verdict": report.verdict.value,
            "stages_total": counts["total"],
            "stages_passed": counts["passed"],
            "stages_failed": counts["failed"],
            "stages_skipped": counts["skipped"],
            "blocking_failures": list(report.blocking_failures()),
            "stage_status": dict(stage_status),
            "coverage_line_percent": coverage_line_percent,
        }
        return cls(
            repository_id=report.repository_id,
            epic_id=report.epic_id,
            verdict=report.verdict,
            stages_total=counts["total"],
            stages_passed=counts["passed"],
            stages_failed=counts["failed"],
            stages_skipped=counts["skipped"],
            blocking_failures=report.blocking_failures(),
            stage_status=dict(stage_status),
            coverage_line_percent=coverage_line_percent,
            dashboard_sha256=content_hash(core),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dashboard_format": DASHBOARD_FORMAT,
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "verdict": self.verdict.value,
            "stages_total": self.stages_total,
            "stages_passed": self.stages_passed,
            "stages_failed": self.stages_failed,
            "stages_skipped": self.stages_skipped,
            "blocking_failures": list(self.blocking_failures),
            "stage_status": dict(self.stage_status),
            "coverage_line_percent": self.coverage_line_percent,
            "dashboard_sha256": self.dashboard_sha256,
        }


__all__ = [
    "REPOSITORY_OPERATIONS_CONTRACT_VERSION",
    "EXECUTION_REPORT_FORMAT",
    "DASHBOARD_FORMAT",
    "OPERATIONS_AUTHORITY",
    "StageKind",
    "StageOutcome",
    "OperationsVerdict",
    "StageSpec",
    "OperationsConfig",
    "StageResult",
    "CoverageSummary",
    "ExecutionReport",
    "RepositoryDashboard",
]
