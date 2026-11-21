"""UVI-000001 Part 07 — composing one deterministic verification plan.

The plan is the whole decision, taken once, before anything executes: which declared
stages run, which are answered from evidence, which the mode does not admit, what the
test selection is, and how it is partitioned. ``./verify.sh`` then executes the plan
rather than deciding as it goes, which is what makes the run reproducible and what makes
``UVI-L-10`` — plan twice, get identical bytes — a meaningful measurement rather than a
statement of intent.

No wall clock, no host name, no absolute path reaches a plan. Those are observations of
one run on one machine, and a plan that carries them cannot be compared with the plan
another machine produced from the same state.
"""

from __future__ import annotations

import hashlib
import json
import os

from engine.verification_intelligence.constitution import (
    Constitution,
    load_constitution,
    verify_source,
)
from engine.verification_intelligence.evidence import decide, store_home
from engine.verification_intelligence.execution import (
    FALLBACK_MAX_WORKERS,
    plan_shards,
    resolve_workers,
    split_currency,
)
from engine.verification_intelligence.model import (
    Action,
    Coverage,
    Mode,
    Plan,
    Selection,
    SelectionResult,
    StagePlan,
    VerificationIntelligenceError,
)
from engine.verification_intelligence.registry import (
    Substrates,
    TestObjectRegistry,
    build_test_registry,
    load_substrates,
)
from engine.verification_intelligence.selection import select


def build_plan(
    mode_id: str | None = None,
    *,
    constitution: Constitution | None = None,
    substrates: Substrates | None = None,
    tests: TestObjectRegistry | None = None,
    changed: tuple[str, ...] | None = None,
    base: str | None = None,
    root: str | None = None,
    workers_override: str | None = None,
) -> Plan:
    """Compute the complete plan for ``mode_id`` (the declared default when omitted)."""
    constitution = constitution or load_constitution()
    substrates = substrates or load_substrates(root)
    tests = tests or build_test_registry(substrates, root)
    mode = constitution.mode(mode_id) if mode_id else constitution.default_mode

    selection, notes = _resolve_selection(mode, substrates, tests, changed, base, root)
    coverage, escalated = _resolve_coverage(mode, selection)
    if escalated:
        notes.append(
            "the selection escalated, so this run is executed under the coverage floor "
            "exactly as a certification-eligible mode would execute it"
        )

    # THE SPLIT TABLE'S CURRENCY IS A PROPERTY OF THE PLAN, so it is reported with the plan.
    # Splitting is hash-gated and the fallback used to be silent: an object whose content moved
    # was placed whole, the plan quietly lost its largest object's divisibility, and the run
    # read identically. Not a gate — a stale entry makes a plan slower and never wrong — but a
    # plan that cannot say which prices it could actually use is reporting less than it knows.
    if currency := split_currency(tests):
        notes.append(currency)

    shards, workers = _resolve_shards(constitution, selection, tests, mode, workers_override)
    stages = _resolve_stages(constitution, mode, substrates, coverage, root)

    return Plan(
        mode=mode,
        stages=stages,
        selection=selection,
        shards=shards,
        coverage=coverage,
        workers=workers,
        escalated_coverage=escalated,
        notes=tuple(notes),
    )


def _resolve_selection(
    mode: Mode,
    substrates: Substrates,
    tests: TestObjectRegistry,
    changed: tuple[str, ...] | None,
    base: str | None,
    root: str | None,
) -> tuple[SelectionResult, list[str]]:
    """The test selection, resolving every fault to the whole suite.

    A mode declaring WHOLE_SUITE never asks the selector anything. A mode declaring
    IMPACT asks, and a selector FAULT — an unreadable substrate, an unresolvable diff
    base — is answered with the whole suite rather than with an exception, because the
    caller's alternative to a wide plan is no plan at all.
    """
    notes: list[str] = []
    if mode.selection is Selection.WHOLE_SUITE:
        return (
            SelectionResult(
                selection=Selection.WHOLE_SUITE,
                test_paths=tests.paths,
                changed=(),
                affected_objects=(),
                affected_owners=(),
                affected_capabilities=(),
                affected_evidence=(),
                affected_certification=(),
                escalations=(f"{mode.mode_id} declares the whole suite; nothing is selected away",),
                layers=(),
            ),
            notes,
        )
    try:
        result = select(changed, substrates=substrates, tests=tests, base=base, root=root)
    except VerificationIntelligenceError as exc:
        notes.append(f"selection faulted and was answered with the whole suite: {exc}")
        return (
            SelectionResult(
                selection=Selection.WHOLE_SUITE,
                test_paths=tests.paths,
                changed=(),
                affected_objects=(),
                affected_owners=(),
                affected_capabilities=(),
                affected_evidence=(),
                affected_certification=(),
                escalations=(str(exc),),
                layers=(),
            ),
            notes,
        )
    if not result.test_paths and not result.changed:
        notes.append("no change was found; the plan selects nothing and claims nothing")
    return result, notes


def _resolve_coverage(mode: Mode, selection: SelectionResult) -> tuple[Coverage, bool]:
    """The floor this run actually evaluates.

    A developer mode does not own the floor — until its selection escalates. At that
    point it is running the whole suite anyway, and running the whole suite WITHOUT the
    floor would be strictly less than the default path used to do for the same work.
    """
    if mode.coverage is Coverage.FLOOR_90:
        return Coverage.FLOOR_90, False
    if selection.escalated and selection.test_paths:
        return Coverage.FLOOR_90, True
    return Coverage.NOT_EVALUATED, False


def _resolve_shards(
    constitution: Constitution,
    selection: SelectionResult,
    tests: TestObjectRegistry,
    mode: Mode,
    workers_override: str | None,
):
    max_workers = int(constitution.sharding.get("max_workers", FALLBACK_MAX_WORKERS))
    isolated = tuple(
        str(entry.get("prefix"))
        for entry in constitution.sharding.get("isolated") or ()
        if isinstance(entry, dict) and entry.get("prefix")
    )
    enabled = bool(constitution.sharding.get("enabled", True)) and mode.parallel
    count = len(selection.test_paths)
    if not count:
        return (), 1
    units = tests.units_for(selection.test_paths)
    workers = (
        resolve_workers(len(units), max_workers=max_workers, override=workers_override)
        if enabled
        else 1
    )
    return plan_shards(units, tests, workers, isolated=isolated), workers


def _resolve_stages(
    constitution: Constitution,
    mode: Mode,
    substrates: Substrates,
    coverage: Coverage,
    root: str | None,
) -> tuple[StagePlan, ...]:
    """One decision per DECLARED stage — including the ones this mode does not admit.

    Every declared stage appears in the plan, because ``./verify.sh`` looks every stage
    up by label and a stage missing from the plan would be executed by the shell's
    fail-safe default. Saying SKIP explicitly is how a mode's exclusions become visible
    rather than implicit.
    """
    admitted = {stage.stage_id for stage in constitution.stages_for(mode)}
    home = store_home(root, constitution.evidence_home)
    # ONE read of the entry point per plan, not one per stage. The execution contract of
    # every stage comes out of the same file, and a plan that read it fifteen times could
    # observe fifteen different versions of it if the file were edited mid-plan.
    verify = verify_source(root)
    decisions: list[StagePlan] = []
    for stage in constitution.stages:
        if stage.stage_id not in admitted:
            # The floor is the exception the declaration cannot express statically: a
            # developer mode that escalated is running the whole suite under coverage,
            # so the stage that summarises coverage has data and must run.
            if stage.stage_id == "coverage-report" and coverage is Coverage.FLOOR_90:
                decisions.append(
                    StagePlan(
                        stage=stage,
                        action=Action.RUN,
                        reason=(
                            "the selection escalated under the coverage floor, so "
                            "coverage data exists to summarise"
                        ),
                    )
                )
                continue
            decisions.append(
                StagePlan(
                    stage=stage,
                    action=Action.SKIP,
                    reason=f"{mode.mode_id} does not admit this stage and claims nothing from it",
                )
            )
            continue
        reuse, reason, digest = decide(mode, stage, substrates, home=home, root=root, verify=verify)
        decisions.append(
            StagePlan(
                stage=stage,
                action=Action.REUSE if reuse else Action.RUN,
                reason=reason,
                input_digest=digest,
            )
        )
    return tuple(decisions)


def plan_json(plan: Plan) -> str:
    """The plan as canonical JSON — sorted, stable, and free of any observation."""
    return json.dumps(plan.to_dict(), indent=2, sort_keys=True)


def plan_digest(plan: Plan) -> str:
    """The identity of a plan: sha256 over its canonical JSON."""
    return hashlib.sha256(plan_json(plan).encode("utf-8")).hexdigest()


def plan_tsv(plan: Plan) -> str:
    """The plan as ``./verify.sh`` consumes it: ``action<TAB>phase<TAB>digest<TAB>label``.

    A three-column file rather than shell variables, because a stage label is a free
    sentence — it holds spaces, parentheses, en dashes and version ranges — and turning
    it into a shell identifier would mean two names for one stage and a mapping to keep
    in step. The shell looks a stage up by the same literal it passes to ``run_stage``,
    which is the same literal the canonical validation record digests.
    """
    lines = [
        "\t".join(
            (entry.action.value, entry.stage.phase, entry.input_digest or "-", entry.stage.label)
        )
        for entry in plan.stages
    ]
    return "\n".join(lines) + "\n"


def evidence_home(constitution: Constitution, root: str | None = None) -> str:
    return os.path.join(store_home(root, constitution.evidence_home))
