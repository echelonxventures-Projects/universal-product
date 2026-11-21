"""EPIC-PLAT-003 — Pipeline stage executors (Terminal T5).

Each stage kind is a **thin adapter over existing canonical machinery** — a canonical
script/target, the certified EC-1 Acceptance / Validation / Certification engines, the
certified frozen-corpus guard, or the canonical coverage report. No stage re-implements
a check or invents a verdict (TP-01): it delegates and records the outcome.

A legitimate fail-closed outcome (a rejected repository, a below-threshold coverage
report, a frozen-corpus write) is reported as a FAILED
:class:`~platform.repository_operations.contracts.StageResult`; only a malformed stage
definition raises :class:`~platform.repository_operations.errors.StageExecutionError`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.repository_operations.commands import CommandRunner, resolve_command
from platform.repository_operations.contracts import (
    CoverageSummary,
    StageKind,
    StageOutcome,
    StageResult,
    StageSpec,
)
from platform.repository_operations.coverage import load_coverage_summary
from platform.repository_operations.errors import StageExecutionError
from platform.repository_operations.subjects import build_validation_subject
from typing import Any

from engine.acceptance.contracts import RepositorySubject
from engine.acceptance.engine import AcceptanceEngine
from engine.acceptance.errors import RepositorySubjectError
from engine.acceptance.readiness import build_repository_readiness
from engine.certification.engine import certify_validation
from engine.foundation.guards.frozen_paths import FROZEN_PREFIXES, find_frozen_writes
from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine

#: Declared sources a FREEZE stage may draw its subject (the candidate write set) from.
#: ``declared`` uses ``params.paths`` verbatim; ``working-tree`` derives the real set of
#: paths this working tree has actually written relative to HEAD.
FREEZE_SUBJECT_SOURCES: tuple[str, ...] = ("declared", "working-tree")


def execute_stage(
    spec: StageSpec,
    *,
    command_runner: CommandRunner,
    repo_root: str | Path,
    measured_coverage: CoverageSummary | None = None,
) -> tuple[StageResult, CoverageSummary | None]:
    """Execute one stage, returning its result and (for COVERAGE) the parsed summary.

    ``measured_coverage`` carries the summary produced by an earlier COVERAGE stage in
    the same run, so a later ACCEPTANCE stage can be judged against *measured* coverage
    rather than against coverage it declares about itself.
    """
    if spec.kind is StageKind.COMMAND:
        return _run_command(spec, command_runner), None
    if spec.kind is StageKind.ACCEPTANCE:
        return _run_acceptance(spec, measured_coverage), None
    if spec.kind is StageKind.VALIDATION:
        return _run_validation(spec), None
    if spec.kind is StageKind.CERTIFICATION:
        return _run_certification(spec), None
    if spec.kind is StageKind.FREEZE:
        return _run_freeze(spec, repo_root), None
    return _run_coverage(spec, repo_root)


def _require_mapping(spec: StageSpec, key: str) -> Mapping[str, Any]:
    value = spec.params.get(key)
    if not isinstance(value, Mapping):
        raise StageExecutionError(
            f"{spec.kind.value} stage requires a '{key}' mapping",
            stage_id=spec.stage_id,
        )
    return value


def _run_command(spec: StageSpec, command_runner: CommandRunner) -> StageResult:
    name = spec.params.get("command")
    if not name or not isinstance(name, str):
        raise StageExecutionError("command stage requires a 'command' name", stage_id=spec.stage_id)
    argv = resolve_command(name)
    returncode = command_runner(argv)
    outcome = StageOutcome.PASSED if returncode == 0 else StageOutcome.FAILED
    return StageResult.create(
        spec,
        outcome,
        f"canonical command '{name}' exited {returncode}",
        detail={"command": name, "argv": list(argv), "returncode": returncode},
    )


def _measured_coverage_facts(summary: CoverageSummary) -> list[dict[str, Any]]:
    """Project a measured coverage report onto acceptance coverage dimensions.

    Only the dimensions the canonical coverage tool actually measures are emitted.
    Dimensions it cannot measure are deliberately NOT synthesised: acceptance treats a
    missing required dimension as incomplete, which is the correct reading — an
    unmeasured dimension is unproven, never 100%.
    """
    return [
        {
            "name": "statements",
            "covered": summary.lines_covered,
            "total": summary.lines_valid,
        },
        {
            "name": "branches",
            "covered": summary.branches_covered,
            "total": summary.branches_valid,
        },
    ]


def _run_acceptance(spec: StageSpec, measured_coverage: CoverageSummary | None) -> StageResult:
    facts = dict(_require_mapping(spec, "facts"))

    # EIP-018 (FP-13): the acceptance subject used to declare its own coverage as
    # covered=1/total=1 across all six required dimensions — 100% by fiat, not by
    # measurement — so this stage could not fail no matter what the repository
    # actually measured. When `coverage_from_measurement` is declared, the measured
    # report replaces any declared coverage facts, and the absence of a measurement
    # is a fail-closed configuration fault rather than a silent fallback to
    # self-declaration.
    if spec.params.get("coverage_from_measurement"):
        if measured_coverage is None:
            raise StageExecutionError(
                "acceptance stage declares coverage_from_measurement but no COVERAGE "
                "stage produced a measured report earlier in this pipeline; refusing to "
                "fall back to self-declared coverage",
                stage_id=spec.stage_id,
            )
        facts["coverage"] = _measured_coverage_facts(measured_coverage)

    try:
        subject = RepositorySubject.from_mapping(facts)
    except RepositorySubjectError as exc:
        raise StageExecutionError(
            "acceptance facts could not be assimilated",
            stage_id=spec.stage_id,
            detail=str(exc),
        ) from exc
    decision = AcceptanceEngine().accept(subject)
    readiness = build_repository_readiness(decision)
    outcome = StageOutcome.PASSED if decision.accepted else StageOutcome.FAILED
    return StageResult.create(
        spec,
        outcome,
        f"repository acceptance {decision.status.value} (readiness {readiness.verdict})",
        evidence_ref=decision.acceptance_id,
        detail={
            "acceptance_id": decision.acceptance_id,
            "status": decision.status.value,
            "readiness_verdict": readiness.verdict,
            "freeze_ready": readiness.freeze_ready,
            "blocking_failures": list(decision.blocking_failures),
            "counts": decision.counts(),
            "coverage_source": (
                "measured" if spec.params.get("coverage_from_measurement") else "declared"
            ),
        },
    )


def _run_validation(spec: StageSpec) -> StageResult:
    subject = build_validation_subject(_require_mapping(spec, "subject"))
    report = ValidationEngine().validate(subject)
    outcome = StageOutcome.PASSED if report.accepted else StageOutcome.FAILED
    return StageResult.create(
        spec,
        outcome,
        f"validation {report.verdict.value}",
        evidence_ref=content_hash(report.to_dict()),
        detail={
            "target_id": report.target_id,
            "verdict": report.verdict.value,
            "counts": report.counts(),
            "blocking_failures": [f.check_id for f in report.blocking_failures],
        },
    )


def _run_certification(spec: StageSpec) -> StageResult:
    subject = build_validation_subject(_require_mapping(spec, "subject"))
    version = str(spec.params.get("version", "1.0.0"))
    report = ValidationEngine().validate(subject)
    evidence = build_validation_evidence(report)
    decision = certify_validation(report, evidence, version=version)
    outcome = StageOutcome.PASSED if decision.certified else StageOutcome.FAILED
    return StageResult.create(
        spec,
        outcome,
        f"certification {decision.status.value}",
        evidence_ref=decision.certification_id,
        detail={
            "certification_id": decision.certification_id,
            "status": decision.status.value,
            "blocking_failures": list(decision.blocking_failures),
            "counts": decision.counts(),
        },
    )


def _working_tree_write_set(repo_root: str | Path, *, stage_id: str) -> list[str]:
    """Every path this working tree has written relative to HEAD.

    Tracked modifications plus untracked-not-ignored additions. ``-z`` is mandatory:
    without it git quotes any path containing a non-ASCII byte, and a quoted path is
    not the path.
    """
    # THE PROVIDER, NOT THE TOOL. Two capabilities, each answering the question it names:
    # CHANGE_SET for what differs from the recorded point, WORKING_TREE_STATE for what the working
    # copy holds that no recorded point does. The union is made HERE, deliberately — a provider
    # merging them would hide which half a write-set entry came from, and this stage's whole
    # purpose is to know what it is about to freeze.
    #
    # Fail-closed is preserved: the provider raises, and the raise is translated into the same
    # StageExecutionError this function already promised, because an empty write set would make
    # the freeze guard a guaranteed PASS over nothing — the defect EIP-018 records.
    from engine.omega_infinite.capability import CHANGE_SET, WORKING_TREE_STATE
    from engine.omega_infinite.git_provider import GitDiscoveryProvider
    from engine.omega_infinite.provider import ProviderError

    provider = GitDiscoveryProvider(root=str(repo_root))
    try:
        modified = provider.supply(CHANGE_SET)
        working = provider.supply(WORKING_TREE_STATE)
    except ProviderError as exc:
        raise StageExecutionError(
            "freeze stage could not determine the write set",
            stage_id=stage_id,
            detail=str(exc),
        ) from exc
    return sorted(set(modified) | set(working["untracked"]))


def _run_freeze(spec: StageSpec, repo_root: str | Path) -> StageResult:
    # EIP-018 (FP-14): this stage was configured with `paths: []`. find_frozen_writes
    # over an empty subject returns no violations, so the architecture-freeze guard
    # was a guaranteed PASS over nothing. A guard with an empty subject evidences
    # nothing, so an empty DECLARED subject is now a fail-closed configuration fault,
    # and the stage can instead derive its subject from the real working-tree write set.
    source = str(spec.params.get("subject", "declared"))
    if source not in FREEZE_SUBJECT_SOURCES:
        raise StageExecutionError(
            f"freeze stage 'subject' must be one of {list(FREEZE_SUBJECT_SOURCES)}",
            stage_id=spec.stage_id,
            detail=f"got {source!r}",
        )

    if source == "working-tree":
        paths = _working_tree_write_set(repo_root, stage_id=spec.stage_id)
    else:
        paths_raw = spec.params.get("paths", [])
        if not isinstance(paths_raw, Sequence) or isinstance(paths_raw, str | bytes):
            raise StageExecutionError("freeze stage 'paths' must be a list", stage_id=spec.stage_id)
        paths = [str(p) for p in paths_raw]
        if not paths:
            raise StageExecutionError(
                "freeze stage declares an empty path set; a guard over an empty subject "
                "cannot evidence corpus read-only-ness. Declare the paths explicitly or "
                'set "subject": "working-tree" to guard the real write set',
                stage_id=spec.stage_id,
            )

    violations = find_frozen_writes(paths)
    outcome = StageOutcome.FAILED if violations else StageOutcome.PASSED
    summary = (
        f"{len(violations)} frozen-corpus write(s) detected"
        if violations
        else f"no frozen-corpus writes across {len(paths)} path(s)"
    )
    return StageResult.create(
        spec,
        outcome,
        summary,
        detail={
            "subject_source": source,
            "checked": len(paths),
            "violations": violations,
            "frozen_prefixes": list(FROZEN_PREFIXES),
        },
    )


def _run_coverage(
    spec: StageSpec, repo_root: str | Path
) -> tuple[StageResult, CoverageSummary | None]:
    try:
        min_percent = float(spec.params.get("min_percent", 90.0))
    except (TypeError, ValueError) as exc:
        raise StageExecutionError(
            "coverage stage 'min_percent' must be numeric",
            stage_id=spec.stage_id,
            detail=str(exc),
        ) from exc

    coverage_path = Path(spec.params.get("path", "coverage.xml"))
    if not coverage_path.is_absolute():
        coverage_path = Path(repo_root) / coverage_path

    if not coverage_path.is_file():
        result = StageResult.create(
            spec,
            StageOutcome.FAILED,
            f"coverage report not found at {coverage_path}",
            detail={"path": str(coverage_path), "min_percent": min_percent},
        )
        return result, None

    summary = load_coverage_summary(coverage_path)
    outcome = StageOutcome.PASSED if summary.meets(min_percent) else StageOutcome.FAILED
    result = StageResult.create(
        spec,
        outcome,
        f"line coverage {summary.line_percent}% (minimum {min_percent}%)",
        evidence_ref=content_hash(summary.to_dict()),
        detail={"path": str(coverage_path), "min_percent": min_percent, **summary.to_dict()},
    )
    return result, summary


__all__ = ["execute_stage"]
