"""UAUE — the declared exit criteria, measured (UAUE-000001, Epoch 6).

Fifteen exit criteria are declared, one per implementation phase of the programme, and each one
states the condition under which that phase may be called complete. For three epochs they were
loaded into the authority, rendered into the capability matrix, and evaluated by nothing. That is
the defect class this repository names explicitly and refuses: an obligation nothing evaluates is
of UNKNOWN compliance and must never be presumed satisfied. Rendered beside a column of declared
text, fifteen unmeasured conditions read exactly like fifteen met ones.

This module is the measurement. It follows the pattern the mandatory invariants already
established, deliberately rather than by coincidence:

* The declaration names a **measure** and this module implements one function per name. Which
  criteria exist, what they say, and which measure answers each is the declaration's business; how
  a measure is computed is this module's. Neither holds the other's half.
* Every measure counts **violations**, so the declared expectation is zero and the count names
  what is wrong rather than merely that something is.
* A measure the declaration names and this module cannot compute is a **refusal**, never a zero.
  A missing measure that defaulted to zero would report an unmet exit criterion as met, which is
  worse than not measuring it at all — it would be a false statement rather than a silent one.

Everything is computed from the conducted runs and the measured tree. Nothing is read back from a
rendered register: a criterion checked against this programme's own output would be measuring its
own claim, and the whole point of an exit criterion is that something else gets to say no.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any

from engine.uaue.model import PRESENT, EvolutionAuthority, EvolutionAuthorityError
from engine.uaue.resolution import REPO_ROOT

if TYPE_CHECKING:  # pragma: no cover - import cycle guard, types only
    from engine.uaue.controller import EvolutionRun
    from engine.uaue.gate import GateReport


def _runs(report: GateReport) -> Sequence[EvolutionRun]:
    return report.runs


def _authority(report: GateReport) -> EvolutionAuthority:
    return report.context.authority


# --------------------------------------------------------------------------------------------
# One function per declared measure. Each returns a violation count.
# --------------------------------------------------------------------------------------------


def _unclassified_capability_surface(report: GateReport) -> int:
    """AUE-EXIT-01 — every position classified against repository truth, and the matrix renders.

    Two halves, because the criterion has two. A position with no classification has not been
    measured against the tree. A register whose declared renderer is not implemented cannot be
    produced, so the matrix the criterion requires would not exist.

    The second half is measured against the renderer map rather than by rendering. That is not a
    weaker check — ``UAUE-GATE-08`` renders every register and scans the bytes — it is a necessary
    one: the capability matrix publishes these very measurements, so measuring this criterion *by*
    rendering would make the matrix render itself.
    """
    from engine.uaue.registers import RENDERERS

    authority = _authority(report)
    violations = sum(1 for phase in authority.phases if not phase.classification)
    violations += sum(1 for register in authority.registers if register.renderer not in RENDERERS)
    return violations


def _object_kinds_or_mandated_fields_unmet(report: GateReport) -> int:
    """AUE-EXIT-02 — every mandated object kind exists and carries every mandated field.

    Kinds are matched by the identifier an object records, not by the human name the declaration
    also carries: the object model stores the declared identifier, and comparing against the name
    would report every mandated kind missing while all eleven were produced.
    """
    authority = _authority(report)
    produced = {obj.object_kind for run in _runs(report) for obj in run.chain.objects}
    violations = sum(
        1 for kind in authority.object_kinds if kind.mandated and kind.identifier not in produced
    )
    for field in authority.required_fields:
        if not field.non_empty:
            continue
        violations += sum(
            1
            for run in _runs(report)
            for obj in run.chain.objects
            if not obj.field_value(field.field_name)
        )
    return violations


def _discovery_duties_unsatisfied(report: GateReport) -> int:
    """AUE-EXIT-03 — every duty has a resolving source, and discovery yields a candidate.

    A duty satisfied by a source that does not resolve is a duty nothing discharges, so the
    source's own resolution is measured rather than its declaration trusted. The candidate half
    is non-vacuity: duties satisfied over an empty discovery would all pass and mean nothing.
    """
    authority = _authority(report)
    resolving = {
        source.identifier
        for source in authority.discovery_sources
        if not source.path or report.context.substrate.state(source.path) == PRESENT
    }
    violations = sum(
        1 for duty in authority.discovery_duties if not (set(duty.satisfied_by) & resolving)
    )
    if not _runs(report):
        violations += 1
    return violations


def _understanding_questions_unanswered(report: GateReport) -> int:
    """AUE-EXIT-04 — every candidate answers all five understanding questions."""
    violations = 0
    for run in _runs(report):
        understanding = run.chain.understanding
        if understanding is None:
            violations += 5
            continue
        answers: tuple[object, ...] = (
            understanding.why,
            understanding.target_state,
            understanding.dependencies,
            understanding.breaks,
            understanding.obj.evidence,
        )
        violations += sum(1 for answer in answers if not answer)
    return violations


def _plan_components_missing(report: GateReport) -> int:
    """AUE-EXIT-05 — every plan carries objectives, steps, dependencies, risk, criteria, rollback.

    The component set is read off the declared plan contract rather than listed here: the
    contract names where each part is composed from, so it is the declaration that decides what a
    complete plan is, and a seventh component would be measured without editing this module.
    """
    authority = _authority(report)
    contract = authority.plan_contract
    violations = 0
    for run in _runs(report):
        plan = run.chain.plan
        if plan is None:
            violations += 1
            continue
        parts: dict[str, object] = {
            contract.objectives_from: plan.objectives,
            contract.steps_from: plan.steps,
            contract.dependencies_from: plan.dependencies,
            contract.risk_from: plan.risk,
            contract.validation_criteria_from: plan.validation_criteria,
            contract.verification_criteria_from: plan.verification_criteria,
            contract.certification_criteria_from: plan.certification_criteria,
            contract.rollback_strategy: plan.rollback_strategy,
        }
        violations += sum(1 for value in parts.values() if not value)
    return violations


def _executions_without_simulation(report: GateReport) -> int:
    """AUE-EXIT-06 — no execution object exists without a preceding simulation object."""
    violations = 0
    for run in _runs(report):
        chain = run.chain
        if chain.execution is None:
            continue
        if chain.simulation is None:
            violations += 1
            continue
        # Preceding, not merely present: the execution's own simulation reference must be the
        # simulation of this chain. An execution carrying someone else's evaluation would satisfy
        # a presence check and evaluate nothing about itself.
        if chain.execution.simulation is not chain.simulation:
            violations += 1
    return violations


def _executions_without_the_single_mutation_path(report: GateReport) -> int:
    """AUE-EXIT-07 — every execution binds the one authorised path, and offers no second.

    The path an execution binds is compared against the path its own position declares — the
    first owner home of the position that produced it — rather than against a literal written
    here, and the set of *distinct* paths bound across every run is compared against one. Both
    halves are needed: per object, an execution could bind a resolving path that is not the
    declared gateway; across objects, two executions could each bind a correct-looking path and
    the engine would have two mutation gateways.
    """
    authority = _authority(report)
    executions = [run.chain.execution for run in _runs(report) if run.chain.execution is not None]
    violations = 0
    bound = {execution.mutation_path for execution in executions}
    if len(bound) > 1:
        violations += len(bound) - 1
    for execution in executions:
        phase = authority.phase(execution.obj.phase)
        declared = phase.homes[0] if phase.homes else ""
        if not execution.mutation_path or execution.mutation_path != declared:
            violations += 1
        if not execution.path_resolves:
            violations += 1
        if not execution.gate_wired:
            violations += 1
        if execution.mutation_performed:
            violations += 1
    return violations


def _observations_without_expected_actual_deviation(report: GateReport) -> int:
    """AUE-EXIT-08 — every chain records expected, actual and deviation.

    Deviation is a *record*, not a requirement to differ: an empty deviation tuple is a measured
    match. What is refused is an observation that never compared, which is why the two contexts
    are required to be present and the deviation to be a tuple rather than absent.
    """
    violations = 0
    for run in _runs(report):
        observation = run.chain.observation
        if observation is None:
            violations += 1
            continue
        if not observation.expected or not observation.actual:
            violations += 1
        if observation.deviation is None or not isinstance(observation.deviation, tuple):
            violations += 1
        if not observation.measured_by:
            violations += 1
    return violations


def _verdict_shortfall(
    report: GateReport, declared: Sequence[Any], selector: Callable[[EvolutionRun], Any]
) -> int:
    """Shared shape of the three verdict criteria: every declared dimension, every run."""
    declared_ids = [entry.identifier for entry in declared]
    violations = 0
    for run in _runs(report):
        verdict = selector(run)
        if verdict is None:
            violations += len(declared_ids)
            continue
        measured = {entry.identifier: entry.satisfied for entry in verdict.outcomes}
        for identifier in declared_ids:
            if not measured.get(identifier, False):
                violations += 1
    return violations


def _validation_dimensions_unsatisfied(report: GateReport) -> int:
    """AUE-EXIT-09 — every declared validation dimension is measured and satisfied."""
    return _verdict_shortfall(report, _authority(report).validations, lambda run: run.validation)


def _verification_dimensions_unsatisfied_or_ungated(report: GateReport) -> int:
    """AUE-EXIT-10 — every verification dimension is measured, satisfied and bound to a wired gate.

    The gate half is the one that catches a report nobody runs: a dimension bound to a gate that
    is not wired is a dimension whose satisfaction rests on a command the repository cannot
    perform.
    """
    authority = _authority(report)
    violations = _verdict_shortfall(report, authority.verifications, lambda run: run.verification)
    wired = {phase.gate.command for phase in authority.phases if phase.gate.wired}
    for dimension in authority.verifications:
        bound = getattr(dimension, "bound_gate", "")
        if not bound:
            violations += 1
        elif bound not in wired and not report.context.substrate.gate_state(bound)[0]:
            violations += 1
    return violations


def _certification_proofs_unsatisfied(report: GateReport) -> int:
    """AUE-EXIT-11 — every declared certification proof is measured and satisfied."""
    return _verdict_shortfall(
        report, _authority(report).certifications, lambda run: run.certification
    )


def _controller_subject_specific_branches(report: GateReport) -> int:
    """AUE-EXIT-12 — the controller traverses every position with no subject-specific branch.

    Measured over the conductor's *code literals* — every string constant that is not a docstring.
    The distinction is load-bearing rather than lenient: prose may name a position, and several
    declared stage names are ordinary English words (``observe``, ``simulate``, ``learn``) that a
    substring scan finds inside comments, function names and unrelated document keys. What a
    subject-specific branch actually looks like is a *code* literal naming something the
    declaration owns, because that is the form a hard-coded declaration takes.

    A literal match means the traversal can depend on what it is carrying — and the unknown
    subject, which by construction matches none of these names, could then not settle. The names
    come from the authority, so a literal added to the controller tomorrow is measured here
    without anyone extending a list.
    """
    import ast

    source = (REPO_ROOT / "engine" / "uaue" / "controller.py").read_text("utf-8")
    tree = ast.parse(source)
    docstrings = {
        doc
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        and (doc := ast.get_docstring(node, clean=False))
    }
    literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value not in docstrings
    }
    authority = _authority(report)
    owned = (
        {phase.identifier for phase in authority.phases}
        | {kind.identifier for kind in authority.object_kinds}
        | {kind.name for kind in authority.object_kinds}
        | {entry.identifier for entry in authority.classifications}
        | {register.file for register in authority.registers}
        | {source_entry.identifier for source_entry in authority.discovery_sources}
    )
    return len({name for name in owned if name} & literals)


def _history_projection_gaps(report: GateReport) -> int:
    """AUE-EXIT-13 — the projection holds every object, rehydrates, and answers every key.

    Rehydration is performed through the symbol the declaration names, not through a local
    parser: the claim is that the canonical ledger can read this document back, and only the
    ledger can settle that.
    """
    from engine.uaue.history import query_history, rehydrate_history

    authority = _authority(report)
    projection = report.projection
    ledger = projection.get("ledger", {})
    recorded: set[str] = set()
    if isinstance(ledger, Mapping):
        for record in ledger.get("records", []) or []:
            if isinstance(record, Mapping) and isinstance(record.get("subject"), str):
                recorded.add(record["subject"])
    violations = sum(
        1 for run in _runs(report) for obj in run.chain.objects if obj.evolution_id not in recorded
    )
    try:
        rehydrated = rehydrate_history(projection)
    except Exception:  # noqa: BLE001 - any failure is one violation: it did not rehydrate
        violations += 1
    else:
        if len(rehydrated) == 0 or rehydrated.is_terminated():
            violations += 1
    for key in authority.history.queryable_by:
        try:
            query_history(projection, key, "")
        except Exception:  # noqa: BLE001 - a declared key the projection cannot answer
            violations += 1
    return violations


def _self_evolution_unclosed(report: GateReport) -> int:
    """AUE-EXIT-14 — the self-evolution gap is measured closed and its symbols resolve."""
    self_evolution = _authority(report).self_evolution
    violations = 0
    if not self_evolution.home_resolves:
        violations += 1
    violations += len(self_evolution.missing_symbols)
    violations += len(self_evolution.unresolved_evidence)
    if not self_evolution.closed:
        violations += 1
    return violations


def _unknown_subject_or_vocabulary_unmet(report: GateReport) -> int:
    """AUE-EXIT-15 — the probe traverses every position and the vocabulary admits its stage term.

    The second half is what makes the first meaningful. A subject can only occupy a stage nobody
    legislated if the stage vocabulary is open, so the declared unknown stage term is put through
    the vocabulary's own extension surface and three things are required: the canonical cycle does
    not already declare the term (a term that is already a stage would prove nothing), the
    extension admits it, and the original vocabulary is unchanged — the surface is append-only, and
    an extension that mutated the base would be a legislative act rather than an admission.
    """
    from engine.uckp.vocabulary import LIFECYCLE_STAGE_VOCABULARY, Term

    authority = _authority(report)
    probe = authority.unknown_probe
    violations = 0
    conducted = [run for run in _runs(report) if run.subject_identity == probe.subject]
    if not conducted:
        violations += 1
    for run in conducted:
        if len(run.stage_results) != len(authority.phases):
            violations += 1
        if not run.certified or run.halted:
            violations += 1

    term = probe.unknown_stage_term
    declared_stages = {state.name for state in authority.lifecycle_states}
    if not term:
        violations += 1
    elif term in declared_stages or LIFECYCLE_STAGE_VOCABULARY.has(term):
        violations += 1
    else:
        before = LIFECYCLE_STAGE_VOCABULARY.term_ids()
        try:
            extended = LIFECYCLE_STAGE_VOCABULARY.extended_with(
                Term(term_id=term, definition=probe.subject_class)
            )
        except Exception:  # noqa: BLE001 - a vocabulary that refuses is a closed vocabulary
            violations += 1
        else:
            if not extended.has(term):
                violations += 1
            if LIFECYCLE_STAGE_VOCABULARY.term_ids() != before:
                violations += 1
    return violations


#: Measure name to the function that computes it. The declaration chooses the names; this maps
#: them to code, and :func:`exit_measures` refuses a name with no entry rather than reporting a
#: zero for a criterion nothing evaluated.
MEASURES: dict[str, Callable[[GateReport], int]] = {
    "certification_proofs_unsatisfied": _certification_proofs_unsatisfied,
    "controller_subject_specific_branches": _controller_subject_specific_branches,
    "discovery_duties_unsatisfied": _discovery_duties_unsatisfied,
    "executions_without_simulation": _executions_without_simulation,
    "executions_without_the_single_mutation_path": _executions_without_the_single_mutation_path,
    "history_projection_gaps": _history_projection_gaps,
    "object_kinds_or_mandated_fields_unmet": _object_kinds_or_mandated_fields_unmet,
    "observations_without_expected_actual_deviation": (
        _observations_without_expected_actual_deviation
    ),
    "plan_components_missing": _plan_components_missing,
    "self_evolution_unclosed": _self_evolution_unclosed,
    "unclassified_capability_surface": _unclassified_capability_surface,
    "understanding_questions_unanswered": _understanding_questions_unanswered,
    "unknown_subject_or_vocabulary_unmet": _unknown_subject_or_vocabulary_unmet,
    "validation_dimensions_unsatisfied": _validation_dimensions_unsatisfied,
    "verification_dimensions_unsatisfied_or_ungated": (
        _verification_dimensions_unsatisfied_or_ungated
    ),
}


def exit_measures(report: GateReport) -> dict[str, int]:
    """Every declared exit-criterion measure, computed from the conducted runs.

    Returns:
        A mapping from the declared measure name to its violation count. Deterministic over a
        fixed declaration and tree.

    Raises:
        EvolutionAuthorityError: the declaration names a measure this module cannot compute, so
            the criterion would otherwise be reported met without being evaluated.
    """
    authority = _authority(report)
    unknown = sorted(
        {entry.measure for entry in authority.exit_criteria if entry.measure not in MEASURES}
    )
    if unknown:
        raise EvolutionAuthorityError(
            "the declaration names an exit-criterion measure this module cannot compute, "
            "so the criterion would be reported satisfied without being measured",
            measures=unknown,
        )
    return {entry.measure: MEASURES[entry.measure](report) for entry in authority.exit_criteria}


__all__ = ["MEASURES", "exit_measures"]
