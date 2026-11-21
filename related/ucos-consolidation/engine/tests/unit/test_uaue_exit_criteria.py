"""UAUE-000001 Epoch 6 — the declared exit criteria, and the measurement of them.

Fifteen exit criteria, one per implementation phase, each stating the condition under which that
phase may be called complete. They were declared, loaded into the authority and rendered into the
capability matrix, and evaluated by nothing — which is the defect this repository refuses by rule:
an obligation nothing evaluates is of unknown compliance and may never be presumed satisfied.
Rendered beside a column of declared text, fifteen unmeasured conditions read exactly like fifteen
met ones.

What this suite measures, and the failure each property closes:

1. **Every declared measure is implemented and computed.** A criterion whose measure nothing
   computes is a criterion nobody evaluates.
2. **An uncomputable measure is a refusal, never a zero.** A missing measure defaulting to zero
   would report an unmet exit criterion as met — a false statement rather than a silent one.
3. **The obligation can close.** Each measure is driven to a non-zero count and the gate's verdict
   is required to follow it, because a criterion that cannot fail measures nothing.
4. **The measures are deterministic.** They are read by a rendered register and by a gate that
   must replay, so a measure that varied between calls would break both.
5. **Nothing measures its own output.** No measure reads a rendered register, which is what keeps
   an exit criterion from being satisfied by the file that publishes it.
"""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from pathlib import Path

import pytest

from engine.uaue import exits, registers
from engine.uaue import gate as gate_module
from engine.uaue.exits import MEASURES, exit_measures
from engine.uaue.gate import GateReport, measure
from engine.uaue.model import EvolutionAuthorityError, ExitCriterion
from engine.uaue.registers import RENDERERS
from engine.uaue.resolution import REPO_ROOT
from engine.uckp import vocabulary as vocabulary_module

EXITS_SOURCE = REPO_ROOT / "engine" / "uaue" / "exits.py"


@pytest.fixture(scope="module")
def report() -> GateReport:
    return measure()


@pytest.fixture(scope="module")
def measured(report: GateReport) -> dict[str, int]:
    return exit_measures(report)


# --------------------------------------------------------------------------------------
# 1. Every declared criterion is measured, and every measure is declared
# --------------------------------------------------------------------------------------


def test_every_declared_criterion_binds_a_measure_this_engine_implements(
    report: GateReport,
) -> None:
    declared = {entry.measure for entry in report.context.authority.exit_criteria}
    assert declared <= set(MEASURES), sorted(declared - set(MEASURES))
    assert (
        set(MEASURES) == declared
    ), f"implemented but declared by nothing: {sorted(set(MEASURES) - declared)}"


def test_every_criterion_is_measured_and_meets_its_declared_expectation(
    report: GateReport, measured: dict[str, int]
) -> None:
    """The live measurement over repository truth. This is the epoch's own exit condition."""
    unmet = []
    for entry in report.context.authority.exit_criteria:
        assert entry.measure in measured, f"{entry.identifier} names an uncomputed measure"
        if measured[entry.measure] != entry.expect:
            unmet.append(
                f"{entry.identifier} ({entry.criterion}): "
                f"expected {entry.expect}, measured {measured[entry.measure]}"
            )
    assert not unmet, "unmet exit criteria:\n  " + "\n  ".join(unmet)


def test_every_criterion_names_a_phase_and_an_obligation(report: GateReport) -> None:
    criteria = report.context.authority.exit_criteria
    assert len(criteria) == len({entry.identifier for entry in criteria})
    for entry in criteria:
        assert entry.identifier and entry.phase and entry.criterion
        assert entry.expect == 0, (
            f"{entry.identifier} expects {entry.expect}: every measure counts violations, "
            "so a non-zero expectation would be declaring a tolerated violation"
        )


def test_the_gate_carries_the_exit_obligation_and_it_is_satisfied(report: GateReport) -> None:
    obligation = next(entry for entry in report.obligations if entry.identifier == "UAUE-GATE-10")
    assert obligation.satisfied, obligation.detail
    assert str(len(report.context.authority.exit_criteria)) in obligation.detail


# --------------------------------------------------------------------------------------
# 2. An uncomputable measure is a refusal
# --------------------------------------------------------------------------------------


def test_a_measure_this_engine_cannot_compute_is_a_refusal_and_never_a_zero(
    report: GateReport,
) -> None:
    unmeasurable = ExitCriterion(
        identifier="AUE-EXIT-TEST",
        phase="AUE-TEST",
        criterion="a criterion whose measure nothing computes",
        measure="a_measure_no_module_can_compute",
        expect=0,
    )
    authority = replace(
        report.context.authority,
        exit_criteria=report.context.authority.exit_criteria + (unmeasurable,),
    )
    poisoned = replace(report, context=replace(report.context, authority=authority))
    with pytest.raises(EvolutionAuthorityError):
        exit_measures(poisoned)


def test_the_obligation_closes_when_a_declared_measure_is_absent(report: GateReport) -> None:
    """The other half: if the measure map were short, the verdict must not be silence."""
    unmeasurable = ExitCriterion(
        identifier="AUE-EXIT-TEST",
        phase="AUE-TEST",
        criterion="a criterion whose measure nothing computes",
        measure="a_measure_no_module_can_compute",
        expect=0,
    )
    authority = replace(
        report.context.authority,
        exit_criteria=report.context.authority.exit_criteria + (unmeasurable,),
    )
    context = replace(report.context, authority=authority)
    obligation = gate_module._exit_criteria_obligation(context, exit_measures(report))
    assert not obligation.satisfied
    assert "AUE-EXIT-TEST" in obligation.detail
    assert "not computed" in obligation.detail


# --------------------------------------------------------------------------------------
# 3. Every criterion can fail — measured one measure at a time
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("measure_name", sorted(MEASURES))
def test_each_criterion_closes_the_obligation_when_its_measure_reports_a_violation(
    report: GateReport, measure_name: str
) -> None:
    """A criterion that cannot fail measures nothing, so each one is driven to a violation.

    The measure is not called here — the obligation is. What has to hold is that a non-zero count
    reaches the verdict and names the criterion it came from: a gate that computed fifteen numbers
    and reported OPEN regardless would satisfy every other test in this file.
    """
    authority = report.context.authority
    entry = next(item for item in authority.exit_criteria if item.measure == measure_name)
    violated = dict(exit_measures(report))
    violated[measure_name] = entry.expect + 1
    obligation = gate_module._exit_criteria_obligation(report.context, violated)
    assert not obligation.satisfied
    assert entry.identifier in obligation.detail
    assert str(entry.expect + 1) in obligation.detail


def test_the_certification_report_withholds_the_verdict_when_a_criterion_is_unmet(
    report: GateReport, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The published determination must follow the measurement, not the other way round."""

    authority = report.context.authority
    entry = authority.exit_criteria[0]
    monkeypatch.setattr(
        registers,
        "exit_measures",
        lambda _report: {
            item.measure: (1 if item is entry else 0) for item in authority.exit_criteria
        },
    )
    register = next(item for item in authority.registers if item.renderer == "certification_report")
    body = registers.render_register(report, register)
    assert "NOT-CERTIFIED" in body
    assert entry.identifier in body


# --------------------------------------------------------------------------------------
# 3b. Every MEASURE can detect its own defect — one break at a time
# --------------------------------------------------------------------------------------
#
# The tests above prove a non-zero count reaches the verdict. These prove the counts are not
# constants: each one breaks exactly the thing its criterion protects and requires the measure
# that owns it to notice. Without this, fifteen functions returning zero unconditionally would
# satisfy every other assertion in this file — which is the shape of a gate that passes because
# nothing it calls can say no.


def _one_measure(report: GateReport, name: str) -> int:
    return MEASURES[name](report)


def _with_runs(report: GateReport, runs) -> GateReport:
    return replace(report, runs=tuple(runs))


def _with_authority(report: GateReport, **changes) -> GateReport:
    authority = replace(report.context.authority, **changes)
    return replace(report, context=replace(report.context, authority=authority))


def _break_chain(report: GateReport, **changes) -> GateReport:
    """Every run, with one part of its chain removed or altered."""
    return _with_runs(
        report, [replace(run, chain=replace(run.chain, **changes)) for run in report.runs]
    )


def test_an_unclassified_position_is_measured(report: GateReport) -> None:
    authority = report.context.authority
    phases = (replace(authority.phases[0], classification=""),) + authority.phases[1:]
    assert _one_measure(_with_authority(report, phases=phases), "unclassified_capability_surface")


def test_an_unimplemented_renderer_is_measured_by_the_capability_criterion(
    report: GateReport, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delitem(RENDERERS, report.context.authority.registers[0].renderer)
    assert _one_measure(report, "unclassified_capability_surface")


def test_a_mandated_object_kind_nothing_produces_is_measured(report: GateReport) -> None:
    authority = report.context.authority
    absent = replace(authority.object_kinds[0], identifier="AUE-OBJ-NONE", mandated=True)
    assert _one_measure(
        _with_authority(report, object_kinds=authority.object_kinds + (absent,)),
        "object_kinds_or_mandated_fields_unmet",
    )


def test_a_duty_no_resolving_source_satisfies_is_measured(report: GateReport) -> None:
    authority = report.context.authority
    duties = (replace(authority.discovery_duties[0], satisfied_by=()),) + (
        authority.discovery_duties[1:]
    )
    assert _one_measure(
        _with_authority(report, discovery_duties=duties), "discovery_duties_unsatisfied"
    )


def test_discovery_that_yields_nothing_is_measured(report: GateReport) -> None:
    """Non-vacuity of the duty half: duties satisfied over an empty discovery mean nothing."""
    assert _one_measure(_with_runs(report, []), "discovery_duties_unsatisfied")


def test_an_unanswered_understanding_question_is_measured(report: GateReport) -> None:
    assert _one_measure(
        _break_chain(report, understanding=None), "understanding_questions_unanswered"
    )
    first = report.runs[0]
    blinded = replace(first.chain.understanding, why="")
    partial = _with_runs(
        report, [replace(first, chain=replace(first.chain, understanding=blinded))]
    )
    assert _one_measure(partial, "understanding_questions_unanswered") == 1


def test_a_missing_plan_component_is_measured(report: GateReport) -> None:
    assert _one_measure(_break_chain(report, plan=None), "plan_components_missing")
    first = report.runs[0]
    hollow = replace(first.chain.plan, objectives=())
    partial = _with_runs(report, [replace(first, chain=replace(first.chain, plan=hollow))])
    assert _one_measure(partial, "plan_components_missing") == 1


def test_an_execution_with_no_simulation_is_measured(report: GateReport) -> None:
    assert [
        run for run in report.runs if run.chain.execution is not None
    ], "no run produced an execution object, so this measure would be unmeasurable"
    assert _one_measure(_break_chain(report, simulation=None), "executions_without_simulation")


def test_an_execution_binding_the_wrong_path_is_measured(report: GateReport) -> None:
    first = next(run for run in report.runs if run.chain.execution is not None)
    strayed = replace(first.chain.execution, mutation_path="engine/somewhere/else.py")
    assert _one_measure(
        _with_runs(report, [replace(first, chain=replace(first.chain, execution=strayed))]),
        "executions_without_the_single_mutation_path",
    )


def test_an_execution_claiming_a_performed_mutation_is_measured(report: GateReport) -> None:
    """The distinction the whole register rests on: authorisation is not an effect."""
    first = next(run for run in report.runs if run.chain.execution is not None)
    mutated = replace(first.chain.execution, mutation_performed=True)
    assert _one_measure(
        _with_runs(report, [replace(first, chain=replace(first.chain, execution=mutated))]),
        "executions_without_the_single_mutation_path",
    )


def test_a_missing_observation_record_is_measured(report: GateReport) -> None:
    assert _one_measure(
        _break_chain(report, observation=None), "observations_without_expected_actual_deviation"
    )
    first = report.runs[0]
    uncompared = replace(first.chain.observation, expected=())
    assert _one_measure(
        _with_runs(report, [replace(first, chain=replace(first.chain, observation=uncompared))]),
        "observations_without_expected_actual_deviation",
    )


def test_an_unmeasured_validation_verdict_is_measured(report: GateReport) -> None:
    stripped = [replace(run, validation=None) for run in report.runs]
    assert _one_measure(_with_runs(report, stripped), "validation_dimensions_unsatisfied")


def test_an_unmeasured_verification_verdict_is_measured(report: GateReport) -> None:
    stripped = [replace(run, verification=None) for run in report.runs]
    assert _one_measure(
        _with_runs(report, stripped), "verification_dimensions_unsatisfied_or_ungated"
    )


def test_a_verification_dimension_bound_to_no_gate_is_measured(report: GateReport) -> None:
    authority = report.context.authority
    ungated = (replace(authority.verifications[0], bound_gate=""),) + authority.verifications[1:]
    assert _one_measure(
        _with_authority(report, verifications=ungated),
        "verification_dimensions_unsatisfied_or_ungated",
    )


def test_an_unmeasured_certification_verdict_is_measured(report: GateReport) -> None:
    stripped = [replace(run, certification=None) for run in report.runs]
    assert _one_measure(_with_runs(report, stripped), "certification_proofs_unsatisfied")


def test_a_controller_that_names_a_position_is_measured(
    report: GateReport, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Measured against a controller that does name one, in a tree of this test's making."""

    package = tmp_path / "engine" / "uaue"
    package.mkdir(parents=True)
    named = report.context.authority.phases[0].identifier
    (package / "controller.py").write_text(
        f'"""A conductor that knows its subject."""\nBRANCH = "{named}"\n', encoding="utf-8"
    )
    monkeypatch.setattr(exits, "REPO_ROOT", tmp_path)
    assert _one_measure(report, "controller_subject_specific_branches") == 1


def test_prose_naming_a_position_is_not_measured_as_a_branch(
    report: GateReport, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The other direction, which is what makes the measure usable: a docstring may say so."""

    package = tmp_path / "engine" / "uaue"
    package.mkdir(parents=True)
    named = report.context.authority.phases[0].identifier
    (package / "controller.py").write_text(
        f'"""This conductor realises {named} without naming it in code."""\n', encoding="utf-8"
    )
    monkeypatch.setattr(exits, "REPO_ROOT", tmp_path)
    assert _one_measure(report, "controller_subject_specific_branches") == 0


def test_a_projection_that_does_not_rehydrate_is_measured(report: GateReport) -> None:
    assert _one_measure(replace(report, projection={}), "history_projection_gaps")


def test_an_object_absent_from_the_history_is_measured(report: GateReport) -> None:
    ledger = dict(report.projection.get("ledger", {}))
    ledger["records"] = []
    projection = dict(report.projection)
    projection["ledger"] = ledger
    assert _one_measure(replace(report, projection=projection), "history_projection_gaps")


def test_a_reopened_self_evolution_gap_is_measured(report: GateReport) -> None:
    self_evolution = replace(
        report.context.authority.self_evolution, missing_symbols=("a_symbol_that_moved",)
    )
    assert _one_measure(
        _with_authority(report, self_evolution=self_evolution), "self_evolution_unclosed"
    )


def test_an_unconducted_unknown_probe_is_measured(report: GateReport) -> None:
    probe = replace(report.context.authority.unknown_probe, subject="nothing.conducted/0.0.0")
    assert _one_measure(
        _with_authority(report, unknown_probe=probe), "unknown_subject_or_vocabulary_unmet"
    )


def test_a_stage_term_the_cycle_already_declares_is_measured(report: GateReport) -> None:
    """The probe's term must be one no stage declares, or the openness proof proves nothing."""
    legislated = report.context.authority.lifecycle_states[0].name
    probe = replace(report.context.authority.unknown_probe, unknown_stage_term=legislated)
    assert _one_measure(
        _with_authority(report, unknown_probe=probe), "unknown_subject_or_vocabulary_unmet"
    )


# --------------------------------------------------------------------------------------
# 4 & 5. Determinism, and the layering that keeps a criterion from grading its own output
# --------------------------------------------------------------------------------------


def test_the_measures_are_deterministic(report: GateReport, measured: dict[str, int]) -> None:
    assert exit_measures(report) == measured
    assert exit_measures(measure()) == measured


def test_no_measure_reads_a_rendered_register(report: GateReport) -> None:
    """A criterion satisfied by the register that publishes it would be grading its own homework.

    Measured structurally: this module may not name a register file, and may not reach the
    surface-rendering function at module scope. ``AUE-EXIT-01`` needs to know whether every
    register *can* be produced, and it asks the renderer map — not the rendered bytes.
    """
    source = EXITS_SOURCE.read_text("utf-8")
    for register in report.context.authority.registers:
        assert register.file not in source, f"exits.py names the register {register.file}"
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "engine.uaue.registers":
            imported = {alias.name for alias in node.names}
            assert imported == {"RENDERERS"}, (
                f"exits.py imports {sorted(imported)} from the renderer module; a measure that "
                "consumes rendered bytes would be measuring this programme's own output"
            )


def test_this_module_writes_nothing() -> None:
    """The measurement layer is a measurement. It carries no write path at all."""
    source = EXITS_SOURCE.read_text("utf-8")
    for forbidden in ("write_text", "write_bytes", "mkdir", "unlink", "rmtree", "open("):
        assert forbidden not in source, forbidden


def test_the_declaration_binds_a_measure_to_every_criterion_on_disk() -> None:
    """The binding lives in the declaration, not in this engine.

    Read from the file rather than from the loaded authority: the loader could be made to
    tolerate a criterion with no measure, and this is the assertion that says the *declaration*
    is what carries the binding.
    """

    document = json.loads(
        (REPO_ROOT / "00-MASTER" / "UAUE-000001" / "uaue-evolution.json").read_text("utf-8")
    )
    for entry in document["exit_criteria"]:
        assert entry.get("measure"), f"{entry['id']} declares no measure"
        assert entry.get("expect") == 0, f"{entry['id']} declares expect {entry.get('expect')!r}"
    measures = [entry["measure"] for entry in document["exit_criteria"]]
    assert len(measures) == len(set(measures)), "two criteria share one measure"


def test_the_measurement_module_is_not_a_second_declaration(report: GateReport) -> None:
    """No criterion identifier appears in the engine: the declaration says which, code says how."""
    source = EXITS_SOURCE.read_text("utf-8")
    for entry in report.context.authority.exit_criteria:
        assert entry.identifier not in _code_literals(
            source
        ), f"exits.py carries the criterion identifier {entry.identifier} as a code literal"


def _code_literals(source: str) -> set[str]:
    tree = ast.parse(source)
    docstrings = {
        doc
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        and (doc := ast.get_docstring(node, clean=False))
    }
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value not in docstrings
    }


def test_the_measures_live_in_one_place(report: GateReport) -> None:
    """One module owns the computation, and the gate consumes it rather than reimplementing it."""
    gate_source = (REPO_ROOT / "engine" / "uaue" / "gate.py").read_text("utf-8")
    assert "exit_measures" in gate_source
    for name in MEASURES:
        assert name not in gate_source, f"gate.py reimplements the measure {name}"
    assert Path(EXITS_SOURCE).is_file()


# --------------------------------------------------------------------------------------
# the arms of each measure that a healthy run never takes


def test_an_execution_carrying_another_chains_evaluation_is_measured(report: GateReport) -> None:
    """Preceding, not merely present. An execution whose own simulation reference is not this
    chain's would satisfy a presence check while having evaluated nothing about itself."""
    borrowed = _with_runs(
        report,
        [
            replace(
                run,
                chain=replace(
                    run.chain,
                    execution=replace(
                        run.chain.execution,
                        simulation=replace(run.chain.simulation, fixed_point=False),
                    ),
                ),
            )
            for run in report.runs
        ],
    )
    assert _one_measure(borrowed, "executions_without_simulation")


def test_two_executions_binding_different_paths_are_measured(report: GateReport) -> None:
    """Per object, an execution could bind a resolving path that is not the declared gateway;
    across objects, two executions could each bind a correct-looking path and the engine would
    have two mutation gateways. The second is what this half counts."""
    runs = list(report.runs)
    assert runs, "the report conducted no run"
    doubled = _with_runs(
        report,
        [
            *runs,
            replace(
                runs[0],
                chain=replace(
                    runs[0].chain,
                    execution=replace(
                        runs[0].chain.execution, mutation_path="engine/uaue/a-second-gateway.py"
                    ),
                ),
            ),
        ],
    )
    assert _one_measure(doubled, "executions_without_the_single_mutation_path")


@pytest.mark.parametrize("field", ["path_resolves", "gate_wired"])
def test_an_execution_whose_path_or_gate_stopped_resolving_is_measured(
    report: GateReport, field: str
) -> None:
    """Authorised is not the same as authorisable now. Either fact going false means the
    authorisation was recorded against something that is no longer there."""
    broken = _with_runs(
        report,
        [
            replace(
                run,
                chain=replace(run.chain, execution=replace(run.chain.execution, **{field: False})),
            )
            for run in report.runs
        ],
    )
    assert _one_measure(broken, "executions_without_the_single_mutation_path")


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"deviation": None}, "an observation that never compared"),
        ({"measured_by": ""}, "an observation nobody owns"),
    ],
    ids=["no-deviation", "no-owner"],
)
def test_an_observation_that_never_compared_or_names_no_owner_is_measured(
    report: GateReport, changes: dict, reason: str
) -> None:
    """Deviation is a RECORD, not a requirement to differ — an empty tuple is a measured match.
    What is refused is an observation that never compared at all, and one nobody owns."""
    hollow = _with_runs(
        report,
        [
            replace(
                run, chain=replace(run.chain, observation=replace(run.chain.observation, **changes))
            )
            for run in report.runs
        ],
    )
    assert _one_measure(hollow, "observations_without_expected_actual_deviation"), reason


@pytest.mark.parametrize(
    ("measure_name", "verdict_field"),
    [
        ("validation_dimensions_unsatisfied", "validation"),
        ("verification_dimensions_unsatisfied_or_ungated", "verification"),
        ("certification_proofs_unsatisfied", "certification"),
    ],
)
def test_a_declared_dimension_measured_and_unsatisfied_is_counted(
    report: GateReport, measure_name: str, verdict_field: str
) -> None:
    """A verdict that is PRESENT and reports a dimension unsatisfied is a different failure from
    one that is absent. The absent case is already measured; this is the one where the run
    measured the dimension and found it wanting."""
    unsatisfied = _with_runs(
        report,
        [
            replace(
                run,
                **{
                    verdict_field: replace(
                        getattr(run, verdict_field),
                        outcomes=tuple(
                            replace(entry, satisfied=False)
                            for entry in getattr(run, verdict_field).outcomes
                        ),
                    )
                },
            )
            for run in report.runs
        ],
    )
    assert _one_measure(unsatisfied, measure_name)


def test_a_projection_whose_ledger_is_not_a_mapping_is_measured(report: GateReport) -> None:
    """A ledger of another shape records no subject this reader can name, so every object is
    absent from it — which is what the measure has to say rather than reading it as empty."""
    assert _one_measure(
        replace(report, projection={"ledger": "not a mapping"}), "history_projection_gaps"
    )
    ledger = {**report.projection.get("ledger", {}), "records": ["not a record", {"subject": 7}]}
    assert _one_measure(
        replace(report, projection={**report.projection, "ledger": ledger}),
        "history_projection_gaps",
    )


def test_a_self_evolution_home_that_stopped_resolving_is_measured(report: GateReport) -> None:
    """The gap closes when the surface appears and reopens when it goes. A home that no longer
    resolves is the reopening, and it must be counted rather than read as a closed gap."""
    self_evolution = replace(report.context.authority.self_evolution, home_state="absent")
    assert _one_measure(
        _with_authority(report, self_evolution=self_evolution), "self_evolution_unclosed"
    )


def test_a_probe_declaring_no_stage_term_is_measured(report: GateReport) -> None:
    """The openness proof needs a term to put through the vocabulary. With none declared there
    is nothing to admit, and the criterion is unmet rather than vacuously satisfied."""
    probe = replace(report.context.authority.unknown_probe, unknown_stage_term="")
    assert _one_measure(
        _with_authority(report, unknown_probe=probe), "unknown_subject_or_vocabulary_unmet"
    )


def test_a_vocabulary_that_refuses_the_term_or_mutates_itself_is_measured(
    report: GateReport, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Three things are required of the extension surface: it admits the term, the extension
    carries it, and the ORIGINAL vocabulary is unchanged. A surface that mutated the base would
    be a legislative act rather than an admission."""

    real = vocabulary_module.LIFECYCLE_STAGE_VOCABULARY

    class _Refusing:
        def has(self, term: str) -> bool:
            return real.has(term)

        def term_ids(self):  # noqa: ANN202
            return real.term_ids()

        def extended_with(self, term):  # noqa: ANN001, ANN202
            raise RuntimeError("this vocabulary admits nothing")

    monkeypatch.setattr(vocabulary_module, "LIFECYCLE_STAGE_VOCABULARY", _Refusing())
    assert _one_measure(report, "unknown_subject_or_vocabulary_unmet")

    class _Forgetful(_Refusing):
        """Admits the term and does not carry it — an extension that reported success and
        produced a vocabulary the term is not in."""

        def extended_with(self, term):  # noqa: ANN001, ANN202
            return self

    monkeypatch.setattr(vocabulary_module, "LIFECYCLE_STAGE_VOCABULARY", _Forgetful())
    assert _one_measure(report, "unknown_subject_or_vocabulary_unmet")

    class _Mutating(_Refusing):
        """Admits the term and rewrites ITSELF while doing it. The extension surface is
        append-only, and a base that moved is a legislative act rather than an admission."""

        def __init__(self) -> None:
            self._ids = real.term_ids()

        def term_ids(self):  # noqa: ANN202
            return self._ids

        def extended_with(self, term):  # noqa: ANN001, ANN202
            self._ids = (*self._ids, term.term_id)

            class _Extended:
                def has(self, candidate: str) -> bool:
                    return candidate == term.term_id

            return _Extended()

    monkeypatch.setattr(vocabulary_module, "LIFECYCLE_STAGE_VOCABULARY", _Mutating())
    assert _one_measure(report, "unknown_subject_or_vocabulary_unmet")


def test_a_run_of_the_probe_that_stopped_short_or_was_not_certified_is_measured(
    report: GateReport,
) -> None:
    """The probe's traversal IS the openness claim. A run that stopped short traversed fewer
    positions than the loop declares; one that was not certified reached the end and was refused.
    Both are unmet exit criteria and neither may be read as the other."""
    probe = report.context.authority.unknown_probe.subject
    conducted = next(run for run in report.runs if run.subject_identity == probe)
    short = replace(conducted, stage_results=conducted.stage_results[:-1])
    assert _one_measure(_with_runs(report, [short]), "unknown_subject_or_vocabulary_unmet")
    # `certified` and `halted` are DERIVED from the stage results and the refusals, so a run
    # that carries a refusal is refused — there is no flag to set, which is the point of
    # deriving them.
    refused = replace(conducted, refusals=("a position refused",))
    assert not refused.certified
    assert _one_measure(_with_runs(report, [refused]), "unknown_subject_or_vocabulary_unmet")


def test_a_chain_with_no_execution_object_contributes_no_simulation_violation(
    report: GateReport,
) -> None:
    """A chain that never reached execution has no execution to check against a simulation, and
    counting its absence here would double-count what the traversal criteria already measure."""
    assert _one_measure(_break_chain(report, execution=None), "executions_without_simulation") == 0


def test_a_verification_dimension_bound_to_an_unwired_gate_is_measured(
    report: GateReport,
) -> None:
    """The gate half catches a report nobody runs: a dimension bound to a command the repository
    cannot perform is a dimension whose satisfaction rests on nothing being executed."""
    authority = report.context.authority
    rebound = tuple(
        replace(entry, bound_gate="make a-target-no-makefile-declares")
        for entry in authority.verifications
    )
    assert _one_measure(
        _with_authority(report, verifications=rebound),
        "verification_dimensions_unsatisfied_or_ungated",
    )
