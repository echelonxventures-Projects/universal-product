"""UAUE-000001 Epoch 3 — the refusal paths.

Every guard in the engine has a mutation here that reaches it. A guard with no test is a guard
that has never run, and a refusal that has never run is indistinguishable from a refusal that does
not work. These are separated from the happy-path suite because they are about a single question:
when the declaration or the substrate is wrong, does the engine refuse, and does it say why.

Three groups: declaration blocks the loader must refuse, discovery sources it must survive, and
execution preconditions it must not authorise past.
"""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from engine.uaue import validation as validation_module
from engine.uaue import verification as verification_module
from engine.uaue.authority import load_evolution_authority
from engine.uaue.certification import certification_object, certify_evolution
from engine.uaue.discovery import discover_evolution_candidates
from engine.uaue.execution import execute_evolution
from engine.uaue.history import (
    history_digest,
    learning_object,
    project_history,
    rehydrate_history,
    state_transition_object,
)
from engine.uaue.model import Dependency, EvolutionAuthority, EvolutionAuthorityError
from engine.uaue.objects import (
    EvolutionCandidate,
    EvolutionChain,
    EvolutionObject,
    as_context,
    identity_inputs,
    phase_object,
)
from engine.uaue.observation import observe_evolution
from engine.uaue.planning import create_evolution_plan
from engine.uaue.resolution import DECLARATION_PATH, REPO_ROOT, DeclarationReader, Substrate
from engine.uaue.simulation import simulate_evolution
from engine.uaue.understanding import understand_evolution
from engine.uaue.validation import measurable_dimensions, validate_evolution, validation_object
from engine.uaue.verification import verification_object, verify_evolution


@pytest.fixture(scope="module")
def declaration() -> dict[str, Any]:
    return json.loads((REPO_ROOT / DECLARATION_PATH).read_text("utf-8"))


@pytest.fixture
def mutable(declaration: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(declaration)


@pytest.fixture(scope="module")
def authority() -> EvolutionAuthority:
    return load_evolution_authority()


@pytest.fixture(scope="module")
def candidate(authority: EvolutionAuthority) -> EvolutionCandidate:
    report = discover_evolution_candidates(authority)
    return next(entry for entry in report.candidates if entry.candidate_class == "UNKNOWN_OBJECT")


def _load(document: dict[str, Any], root: Path | None = None) -> EvolutionAuthority:
    return load_evolution_authority(DeclarationReader.from_document(document), Substrate(root))


# --------------------------------------------------------------------------------------
# Declaration blocks the loader must refuse
# --------------------------------------------------------------------------------------


def test_a_zero_identity_width_is_refused(mutable: dict[str, Any]) -> None:
    mutable["identity"]["width"] = 0
    with pytest.raises(EvolutionAuthorityError, match="width must be positive"):
        _load(mutable)


def test_an_identity_rule_with_no_inputs_is_refused(mutable: dict[str, Any]) -> None:
    mutable["identity"]["inputs"] = []
    with pytest.raises(EvolutionAuthorityError, match="declares no inputs"):
        _load(mutable)


def test_an_identity_input_declared_twice_is_refused(mutable: dict[str, Any]) -> None:
    mutable["identity"]["inputs"] = ["reason", "reason"]
    with pytest.raises(EvolutionAuthorityError, match="same input twice"):
        _load(mutable)


def test_an_identity_input_the_object_model_lacks_is_refused(
    mutable: dict[str, Any], candidate: EvolutionCandidate
) -> None:
    mutable["identity"]["inputs"] = ["telepathic_intent"]
    authority = _load(mutable)
    with pytest.raises(EvolutionAuthorityError, match="the object model does not carry"):
        understand_evolution(candidate, authority)


def test_a_discovery_source_with_an_unimplemented_form_is_refused(
    mutable: dict[str, Any],
) -> None:
    mutable["discovery_sources"][0]["form"] = "telepathy"
    with pytest.raises(EvolutionAuthorityError, match="a form this engine cannot read"):
        _load(mutable)


def test_a_discovery_source_with_an_unimplemented_operator_is_refused(
    mutable: dict[str, Any],
) -> None:
    mutable["discovery_sources"][3]["include_when"][0]["op"] = "approximately"
    with pytest.raises(EvolutionAuthorityError, match="operator this engine does not implement"):
        _load(mutable)


def test_a_discovery_source_with_no_selector_is_refused(mutable: dict[str, Any]) -> None:
    mutable["discovery_sources"][0]["selector"] = []
    with pytest.raises(EvolutionAuthorityError, match="declares no selector"):
        _load(mutable)


def test_a_discovery_source_declared_twice_is_refused(mutable: dict[str, Any]) -> None:
    mutable["discovery_sources"].append(copy.deepcopy(mutable["discovery_sources"][0]))
    with pytest.raises(EvolutionAuthorityError, match="same discovery source twice"):
        _load(mutable)


def test_a_duty_naming_an_undeclared_source_is_refused(mutable: dict[str, Any]) -> None:
    mutable["discovery_duties"][0]["satisfied_by"] = ["AUE-SRC-99"]
    with pytest.raises(EvolutionAuthorityError, match="a source the declaration does not"):
        _load(mutable)


def test_a_duty_with_no_source_is_refused(mutable: dict[str, Any]) -> None:
    mutable["discovery_duties"][0]["satisfied_by"] = []
    with pytest.raises(EvolutionAuthorityError, match="names no source"):
        _load(mutable)


def test_a_criterion_declared_twice_is_refused(mutable: dict[str, Any]) -> None:
    mutable["validations"].append(copy.deepcopy(mutable["validations"][0]))
    with pytest.raises(EvolutionAuthorityError, match="same criterion twice"):
        _load(mutable)


def test_two_invariants_sharing_a_measure_are_refused(mutable: dict[str, Any]) -> None:
    mutable["mandatory"][1]["measure"] = mutable["mandatory"][0]["measure"]
    with pytest.raises(EvolutionAuthorityError, match="share a measure name"):
        _load(mutable)


def test_a_history_with_no_projection_owner_is_refused(mutable: dict[str, Any]) -> None:
    del mutable["history"]["projection_of"]
    with pytest.raises(EvolutionAuthorityError, match="no 'projection_of'"):
        _load(mutable)


def test_a_history_projection_owner_that_does_not_resolve_is_refused(
    mutable: dict[str, Any],
) -> None:
    mutable["history"]["projection_of"]["home"] = "engine/uckp/absent.py"
    with pytest.raises(EvolutionAuthorityError, match="projection owner does not resolve"):
        _load(mutable)


def test_a_history_projection_missing_its_loader_is_refused(mutable: dict[str, Any]) -> None:
    mutable["history"]["projection_of"]["rehydration_symbol"] = "no_such_loader"
    with pytest.raises(EvolutionAuthorityError, match="does not bind a symbol"):
        _load(mutable)


def test_a_history_with_no_recorded_dimension_is_refused(mutable: dict[str, Any]) -> None:
    mutable["history"]["records"] = []
    with pytest.raises(EvolutionAuthorityError, match="no recorded dimension"):
        _load(mutable)


def test_an_unknown_probe_forbidding_nothing_is_refused(mutable: dict[str, Any]) -> None:
    mutable["unknown_probe"]["must_not_require"] = []
    with pytest.raises(EvolutionAuthorityError, match="forbids nothing"):
        _load(mutable)


def test_an_empty_criterion_block_is_refused(mutable: dict[str, Any]) -> None:
    mutable["certifications"] = []
    with pytest.raises(EvolutionAuthorityError, match="declares no criterion|empty block"):
        _load(mutable)


def test_a_source_with_a_non_string_path_is_refused(mutable: dict[str, Any]) -> None:
    mutable["discovery_sources"][0]["path"] = 7
    with pytest.raises(EvolutionAuthorityError, match="declares 'path'"):
        _load(mutable)


def test_a_source_with_non_mapping_fields_is_refused(mutable: dict[str, Any]) -> None:
    mutable["discovery_sources"][0]["fields"] = []
    with pytest.raises(EvolutionAuthorityError, match="declares 'fields'"):
        _load(mutable)


def test_a_source_with_non_list_include_when_is_refused(mutable: dict[str, Any]) -> None:
    mutable["discovery_sources"][0]["include_when"] = {}
    with pytest.raises(EvolutionAuthorityError, match="declares 'include_when'"):
        _load(mutable)


def test_a_phase_with_non_list_owners_is_refused(mutable: dict[str, Any]) -> None:
    mutable["phases"][0]["owners"] = {}
    with pytest.raises(EvolutionAuthorityError, match="declares 'owners'"):
        _load(mutable)


def test_authority_accessors_refuse_unknown_names(authority: EvolutionAuthority) -> None:
    with pytest.raises(EvolutionAuthorityError, match="no such classification"):
        authority.classification("NOPE")
    with pytest.raises(EvolutionAuthorityError, match="no such phase"):
        authority.phase("NOPE")
    with pytest.raises(EvolutionAuthorityError, match="no such register"):
        authority.register("99-NOPE.md")
    with pytest.raises(EvolutionAuthorityError, match="not a canonical evolution stage"):
        authority.phases_claiming("telepathy")
    with pytest.raises(EvolutionAuthorityError, match="no such discovery source"):
        authority.discovery_source("AUE-SRC-99")
    with pytest.raises(EvolutionAuthorityError, match="no object kind"):
        authority.object_kind_of("AUE-P-99")
    with pytest.raises(EvolutionAuthorityError, match="claims no canonical stage"):
        authority.stage_of("AUE-P-99")
    with pytest.raises(EvolutionAuthorityError, match="no phase at that position"):
        authority.phase_by_ordinal(99)


def test_an_object_refuses_an_unmandated_field_name(candidate: EvolutionCandidate) -> None:
    obj = EvolutionObject(
        evolution_id="x",
        object_kind="k",
        phase="p",
        lifecycle_state="s",
        subject_identity=candidate.subject_identity,
        candidate_class="c",
        previous_state="a",
        target_state="b",
        reason="r",
        context=as_context({"a": "b"}),
        dependencies=(),
        evidence=("x",),
        plan="p",
        execution_record="e",
        validation_result="v",
        verification_result="w",
        certification_result="c",
        authority="auth",
    )
    with pytest.raises(EvolutionAuthorityError, match="does not carry"):
        obj.field_value("telepathy")


# --------------------------------------------------------------------------------------
# Discovery sources the engine must survive
# --------------------------------------------------------------------------------------


def _source_tree(tmp_path: Path, declaration: dict[str, Any], payload: object) -> Path:
    """A tree in which one declared artifact exists and carries ``payload``."""
    path = declaration["discovery_sources"][0]["path"]
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_an_unreadable_artifact_is_a_finding_not_a_crash(
    authority: EvolutionAuthority, tmp_path: Path, declaration: dict[str, Any]
) -> None:
    path = declaration["discovery_sources"][0]["path"]
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{not json", encoding="utf-8")
    report = discover_evolution_candidates(authority, Substrate(tmp_path))
    assert any("unreadable" in finding for finding in report.findings)


def test_an_absent_selector_is_a_finding(
    authority: EvolutionAuthority, tmp_path: Path, declaration: dict[str, Any]
) -> None:
    root = _source_tree(tmp_path, declaration, {"something_else": []})
    report = discover_evolution_candidates(authority, Substrate(root))
    assert any("is absent from" in finding for finding in report.findings)


def test_a_selector_of_the_wrong_shape_is_a_finding(
    authority: EvolutionAuthority, tmp_path: Path, declaration: dict[str, Any]
) -> None:
    root = _source_tree(tmp_path, declaration, {"known_spine_gaps": {"not": "a list"}})
    report = discover_evolution_candidates(authority, Substrate(root))
    assert any("is not a list" in finding for finding in report.findings)


def test_an_entry_naming_no_subject_is_dropped_with_a_finding(
    authority: EvolutionAuthority, tmp_path: Path, declaration: dict[str, Any]
) -> None:
    root = _source_tree(
        tmp_path, declaration, {"known_spine_gaps": [{"id": "G-01", "severity": "HIGH"}]}
    )
    report = discover_evolution_candidates(authority, Substrate(root))
    assert any("named no subject" in finding for finding in report.findings)


def test_a_mapping_source_of_the_wrong_shape_is_a_finding(
    authority: EvolutionAuthority, tmp_path: Path, declaration: dict[str, Any]
) -> None:
    mapping_source = next(
        entry for entry in declaration["discovery_sources"] if entry["form"] == "mapping_of_objects"
    )
    target = tmp_path / mapping_source["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({mapping_source["selector"][0]: []}), encoding="utf-8")
    report = discover_evolution_candidates(authority, Substrate(tmp_path))
    assert any("is not a mapping" in finding for finding in report.findings)


def test_include_when_excludes_an_entry_that_fails_the_condition(
    authority: EvolutionAuthority, tmp_path: Path, declaration: dict[str, Any]
) -> None:
    """A gap class measuring zero is not a candidate; the same class above zero is."""
    gated = next(entry for entry in declaration["discovery_sources"] if entry["include_when"])
    target = tmp_path / gated["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                gated["selector"][0]: [
                    {"id": "GAP-A", "subject": "a", "class": "X", "count": 0},
                    {"id": "GAP-B", "subject": "b", "class": "Y", "count": 3},
                ]
            }
        ),
        encoding="utf-8",
    )
    report = discover_evolution_candidates(authority, Substrate(tmp_path))
    subjects = {entry.subject_identity for entry in report.for_source(gated["id"])}
    assert subjects == {"b"}


def test_a_non_numeric_value_fails_a_numeric_condition(
    authority: EvolutionAuthority, tmp_path: Path, declaration: dict[str, Any]
) -> None:
    gated = next(entry for entry in declaration["discovery_sources"] if entry["include_when"])
    target = tmp_path / gated["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {gated["selector"][0]: [{"id": "G", "subject": "s", "class": "X", "count": "many"}]}
        ),
        encoding="utf-8",
    )
    report = discover_evolution_candidates(authority, Substrate(tmp_path))
    assert not report.for_source(gated["id"])


def test_a_boolean_never_satisfies_a_numeric_condition(
    authority: EvolutionAuthority, tmp_path: Path, declaration: dict[str, Any]
) -> None:
    gated = next(entry for entry in declaration["discovery_sources"] if entry["include_when"])
    target = tmp_path / gated["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {gated["selector"][0]: [{"id": "G", "subject": "s", "class": "X", "count": True}]}
        ),
        encoding="utf-8",
    )
    report = discover_evolution_candidates(authority, Substrate(tmp_path))
    assert not report.for_source(gated["id"])


def test_an_authority_surface_gap_becomes_a_candidate(
    mutable: dict[str, Any],
) -> None:
    """The self-detection path: a declared surface that is not bound reopens as a candidate."""
    mutable["authority_symbols"][0]["symbol"] = "a_surface_that_does_not_exist"
    authority = _load(mutable)
    report = discover_evolution_candidates(
        authority, Substrate(), DeclarationReader.from_document(mutable)
    )
    gaps = [entry for entry in report.candidates if entry.candidate_class == "AUTHORITY_SYMBOL_GAP"]
    assert gaps, "an unbound declared surface must reopen as a candidate"
    assert gaps[0].severity == "a_surface_that_does_not_exist"


def test_an_authority_obligation_naming_no_symbol_is_a_finding(
    mutable: dict[str, Any],
) -> None:
    mutable["authority_symbols"][0]["symbol"] = ""
    authority = _load(mutable)
    report = discover_evolution_candidates(
        authority, Substrate(), DeclarationReader.from_document(mutable)
    )
    assert any("no home or no symbol" in finding for finding in report.findings)


def test_the_report_exposes_its_subjects_and_per_source_counts(
    authority: EvolutionAuthority,
) -> None:
    report = discover_evolution_candidates(authority)
    assert report.subjects()
    assert dict(report.per_source)
    assert report.duties_satisfied
    assert report.to_dict()["candidates"]


# --------------------------------------------------------------------------------------
# Execution preconditions
# --------------------------------------------------------------------------------------


def _through_simulation(candidate: EvolutionCandidate, authority: EvolutionAuthority):
    understanding = understand_evolution(candidate, authority)
    plan = create_evolution_plan(understanding, authority)
    return simulate_evolution(plan, authority)


def test_execution_refuses_when_the_mutation_path_does_not_resolve(
    mutable: dict[str, Any], candidate: EvolutionCandidate
) -> None:
    mutable["phases"][4]["owners"] = [{"home": "engine/absent/gateway.py", "symbols": []}]
    authority = _load(mutable)
    execution = execute_evolution(_through_simulation(candidate, authority), authority)
    assert not execution.authorised
    assert any("does not resolve" in entry for entry in execution.refusals)


def test_execution_refuses_when_the_mutation_path_lacks_a_declared_symbol(
    mutable: dict[str, Any], candidate: EvolutionCandidate
) -> None:
    mutable["phases"][4]["owners"][0]["symbols"] = ["not_a_real_gateway_symbol"]
    authority = _load(mutable)
    execution = execute_evolution(_through_simulation(candidate, authority), authority)
    assert not execution.authorised
    assert any("does not bind" in entry for entry in execution.refusals)


def test_planning_refuses_before_an_unownable_execution_phase_is_reached(
    mutable: dict[str, Any], candidate: EvolutionCandidate, authority: EvolutionAuthority
) -> None:
    """Defence in depth: planning refuses an unownable step, and execution refuses it again.

    Two guards, reached in that order. Planning refuses first, so the execution guard cannot be
    exercised through a normal traversal — which is the point of having it. It is exercised here by
    handing execution an authority whose mutation path was removed after the plan was made, the
    one way a caller could still get there.
    """
    mutable["phases"][4]["owners"] = []
    unowned = _load(mutable)
    understanding = understand_evolution(candidate, unowned)
    with pytest.raises(EvolutionAuthorityError, match="no located owner"):
        create_evolution_plan(understanding, unowned)

    simulation = _through_simulation(candidate, authority)
    execution = execute_evolution(simulation, unowned)
    assert not execution.authorised
    assert any("no mutation path" in entry for entry in execution.refusals)


def test_execution_refuses_when_the_gate_is_not_wired(
    mutable: dict[str, Any], authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """An execution behind a gate nothing discharges is not authorised.

    The condition is constructed rather than found. Until Epoch 4 the register's own declared gate
    was absent from the Makefile, so this guard was reachable against the real tree — which meant
    it was being exercised by a defect rather than by a test. Wiring the gate removed that
    accident, so the unwired gate is now declared here explicitly and the guard is exercised on
    purpose.
    """
    mutable["phases"][4]["gate"] = "make no-such-gate-target"
    unwired = _load(mutable)
    execution = execute_evolution(_through_simulation(candidate, authority), unwired)
    assert not execution.authorised
    assert any("gate is not wired" in entry for entry in execution.refusals)
    assert execution.mutation_performed is False


def test_the_execution_record_names_the_refusal(
    mutable: dict[str, Any], authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    mutable["phases"][4]["gate"] = "make no-such-gate-target"
    execution = execute_evolution(_through_simulation(candidate, authority), _load(mutable))
    assert execution.obj.execution_record.startswith("refused:")


def test_execution_is_authorised_against_the_real_tree(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """The complement of the guards above, and the property Epoch 4 required.

    Every one of the seven preconditions is met against repository truth: the declared mutation
    path resolves, binds its symbols and sits behind a wired gate. Authorisation is still not an
    effect — ``mutation_performed`` remains false, and this engine holds no path to repository
    state through which it could become true.
    """
    execution = execute_evolution(_through_simulation(candidate, authority), authority)
    assert execution.authorised, execution.refusals
    assert execution.refusals == ()
    assert execution.mutation_performed is False
    assert execution.obj.execution_record.startswith("authorised via")


def test_observation_reports_a_deviation_when_the_substrate_changes(
    authority: EvolutionAuthority, candidate: EvolutionCandidate, tmp_path: Path
) -> None:
    """Authorised against the real tree, measured against an empty one: that is a deviation."""
    execution = execute_evolution(_through_simulation(candidate, authority), authority)
    observation = observe_evolution(execution, authority, Substrate(tmp_path))
    assert observation.deviation
    assert not observation.matches


# --------------------------------------------------------------------------------------
# Judgement edge cases
# --------------------------------------------------------------------------------------


def test_a_verification_dimension_the_engine_cannot_measure_is_not_satisfied(
    mutable: dict[str, Any], candidate: EvolutionCandidate
) -> None:
    mutable["verifications"].append(
        {
            "id": "AUE-VER-99",
            "dimension": "Telepathic integrity",
            "obligation": "the engine guesses",
            "bound_gate": "./verify.sh",
            "blocking": True,
        }
    )
    authority = _load(mutable)
    chain = EvolutionChain(
        candidate=candidate,
        objects=(
            phase_object(
                authority,
                EvolutionObject.derive(
                    rule=authority.identity,
                    candidate=candidate,
                    object_kind=authority.object_kind_of(
                        authority.phase_by_ordinal(1).identifier
                    ).identifier,
                    phase=authority.phase_by_ordinal(1).identifier,
                    lifecycle_state=authority.stage_of(authority.phase_by_ordinal(1).identifier),
                    dependencies=(),
                    evidence=candidate.evidence,
                    authority=authority.phase_by_ordinal(1).authority,
                ),
                ordinal=2,
            ),
        ),
    )
    verdict = verify_evolution(chain, authority)
    added = next(entry for entry in verdict.outcomes if entry.identifier == "AUE-VER-99")
    assert not added.satisfied
    assert "cannot measure" in added.detail


def test_a_certification_proof_the_engine_cannot_measure_is_not_satisfied(
    mutable: dict[str, Any], candidate: EvolutionCandidate
) -> None:
    mutable["certifications"].append(
        {
            "id": "AUE-CRT-99",
            "proof": "was telepathic",
            "obligation": "the engine guesses",
            "blocking": True,
        }
    )
    authority = _load(mutable)
    chain = EvolutionChain(candidate=candidate, objects=())
    verdict = certify_evolution(chain, authority)
    added = next(entry for entry in verdict.outcomes if entry.identifier == "AUE-CRT-99")
    assert not added.satisfied


def test_a_foreign_lifecycle_state_fails_verification(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    first = EvolutionObject.derive(
        rule=authority.identity,
        candidate=candidate,
        object_kind=authority.object_kind_of("AUE-P-01").identifier,
        phase="AUE-P-01",
        lifecycle_state="a-stage-nobody-declared",
        dependencies=(),
        evidence=candidate.evidence,
        authority=authority.phase_by_ordinal(1).authority,
    )
    chain = EvolutionChain(candidate=candidate, objects=(first,))
    verdict = verify_evolution(chain, authority)
    lifecycle = next(
        entry for entry in verdict.outcomes if entry.subject.lower().startswith("lifecycle")
    )
    assert not lifecycle.satisfied


def test_a_missing_phase_blocks_certification_readiness(
    mutable: dict[str, Any], candidate: EvolutionCandidate
) -> None:
    mutable["phases"][5]["owners"] = [{"home": "engine/absent/nowhere.py", "symbols": []}]
    authority = _load(mutable)
    chain = EvolutionChain(candidate=candidate, objects=())
    verdict = verify_evolution(chain, authority)
    readiness = next(
        entry for entry in verdict.outcomes if entry.subject.lower().startswith("certification")
    )
    assert not readiness.satisfied
    assert "MISSING" in readiness.detail


def test_an_object_with_no_authority_fails_the_authorisation_proof(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    first = EvolutionObject.derive(
        rule=authority.identity,
        candidate=candidate,
        object_kind=authority.object_kind_of("AUE-P-01").identifier,
        phase="AUE-P-01",
        lifecycle_state=authority.stage_of("AUE-P-01"),
        dependencies=(),
        evidence=candidate.evidence,
        authority=authority.phase_by_ordinal(1).authority,
    )
    chain = EvolutionChain(candidate=candidate, objects=(replace(first, authority=""),))
    outcome = next(
        entry
        for entry in certify_evolution(chain, authority).outcomes
        if entry.subject == "was authorized"
    )
    assert not outcome.satisfied


def test_judgement_objects_refuse_an_empty_chain(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    empty = EvolutionChain(candidate=candidate, objects=())
    verdict = validate_evolution(empty, authority)
    for producer in (validation_object, verification_object, certification_object):
        with pytest.raises(EvolutionAuthorityError, match="no prior object"):
            producer(empty, verdict, authority)
    with pytest.raises(EvolutionAuthorityError, match="nothing to learn"):
        learning_object(empty, authority)
    with pytest.raises(EvolutionAuthorityError, match="cannot transition state"):
        state_transition_object(empty, authority)


def test_a_history_document_must_be_a_mapping() -> None:
    with pytest.raises(EvolutionAuthorityError, match="must be a mapping"):
        rehydrate_history(["not", "a", "mapping"])


def test_the_history_digest_is_stable(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    document = {"schema": authority.history.schema, "ledger": {"records": []}}
    assert history_digest(document) == history_digest(dict(document))


def test_measurable_dimensions_covers_every_declared_dimension(
    authority: EvolutionAuthority,
) -> None:
    """Non-vacuity: the engine claims to measure exactly what the declaration declares."""
    declared = {entry.subject.strip().lower() for entry in authority.validations}
    assert declared == set(measurable_dimensions())


def test_identity_inputs_reads_every_declared_input(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    first = EvolutionObject.derive(
        rule=authority.identity,
        candidate=candidate,
        object_kind=authority.object_kind_of("AUE-P-01").identifier,
        phase="AUE-P-01",
        lifecycle_state=authority.stage_of("AUE-P-01"),
        dependencies=(),
        evidence=candidate.evidence,
        authority=authority.phase_by_ordinal(1).authority,
    )
    inputs = identity_inputs(authority.identity, first)
    assert set(inputs) == set(authority.identity.inputs)
    assert all(inputs.values())


def test_a_candidate_view_round_trips_from_an_object(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    first = EvolutionObject.derive(
        rule=authority.identity,
        candidate=candidate,
        object_kind=authority.object_kind_of("AUE-P-01").identifier,
        phase="AUE-P-01",
        lifecycle_state=authority.stage_of("AUE-P-01"),
        dependencies=(),
        evidence=candidate.evidence,
        authority=authority.phase_by_ordinal(1).authority,
    )
    view = EvolutionCandidate.from_object(first)
    assert view.subject_identity == candidate.subject_identity
    assert view.evolution_id == first.evolution_id
    assert view.digest()


def test_project_history_accepts_a_sequence_of_chains(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    with pytest.raises(EvolutionAuthorityError):
        project_history([EvolutionChain(candidate=candidate, objects=())], authority)


# --------------------------------------------------------------------------------------
# the accessors, and the integrity dimensions that have only ever passed
#
# Every dimension below returns (satisfied, detail). The unsatisfied arm of each is the one a
# real defect would take, and none of them had ever been produced — so a dimension that
# silently stopped measuring would have reported "satisfied" for ever.


def test_every_accessor_resolves_a_declared_member_and_refuses_an_undeclared_one(
    authority: EvolutionAuthority,
) -> None:
    """The refusals are already measured elsewhere. The resolutions are the other half, and an
    accessor that could only refuse would make every caller's lookup a failure path."""
    assert (
        authority.classification(authority.classifications[0].identifier)
        is (authority.classifications[0])
    )
    assert authority.phase(authority.phases[0].identifier) is authority.phases[0]
    assert authority.register(authority.registers[0].file) is authority.registers[0]
    for accessor, argument in (
        ("classification", "A-CLASSIFICATION-NOBODY-DECLARED"),
        ("phase", "A-PHASE-NOBODY-DECLARED"),
        ("register", "a-register-nobody-declared.md"),
    ):
        with pytest.raises(EvolutionAuthorityError, match="no such"):
            getattr(authority, accessor)(argument)


def _discovery_object(
    authority: EvolutionAuthority, candidate: EvolutionCandidate, **overrides: Any
) -> EvolutionObject:
    phase = authority.phase_by_ordinal(1)
    obj = EvolutionObject.derive(
        rule=authority.identity,
        candidate=candidate,
        object_kind=authority.object_kind_of(phase.identifier).identifier,
        phase=phase.identifier,
        lifecycle_state=authority.stage_of(phase.identifier),
        dependencies=(),
        evidence=candidate.evidence,
        authority=phase.authority,
    )
    return replace(obj, **overrides) if overrides else obj


def test_two_objects_sharing_one_identity_fail_verification(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """A collision makes one identity name two objects, and every later reference to it resolves
    to whichever the reader reached first."""
    first = _discovery_object(authority, candidate)
    chain = EvolutionChain(candidate=candidate, objects=(first, first))
    outcome = next(
        entry
        for entry in verify_evolution(chain, authority).outcomes
        if entry.subject.lower().startswith("identity")
    )
    assert not outcome.satisfied
    assert "share an identity" in outcome.detail


def test_an_object_whose_identity_inputs_cannot_be_read_is_anonymous(
    authority: EvolutionAuthority, candidate: EvolutionCandidate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unidentifiable is not merely mismatched: an object that cannot present its own identity
    inputs cannot be shown to be the object its identity claims."""

    def _unreadable(rule, obj):  # noqa: ANN001, ANN202
        raise EvolutionAuthorityError("the identity inputs could not be read")

    monkeypatch.setattr(verification_module, "identity_inputs", _unreadable)
    monkeypatch.setattr(validation_module, "identity_inputs", _unreadable)
    chain = EvolutionChain(candidate=candidate, objects=(_discovery_object(authority, candidate),))
    verified = next(
        entry
        for entry in verify_evolution(chain, authority).outcomes
        if entry.subject.lower().startswith("identity")
    )
    assert not verified.satisfied
    validated = next(
        entry
        for entry in validate_evolution(chain, authority).outcomes
        if entry.identifier == "AUE-VAL-01"
    )
    assert not validated.satisfied


def test_a_backward_phase_dependency_fails_verification(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """The loop's order is what makes "an earlier phase produced this" checkable, and an edge
    pointing forwards would let a phase depend on one that has not run.

    The edges are DERIVED from loop order, and the loader already refuses a phase whose ordinal
    disagrees with its position, so no declaration can produce a backward edge. That is what
    makes the check worth holding: it is the guard that survives a future loader deriving the
    edges some other way, and reaching it means handing the verifier an edge set the deriver
    cannot currently build.
    """

    forward = Dependency(
        phase=authority.phases[0].identifier,
        depends_on=authority.phases[-1].identifier,
        kind="phase",
    )
    doctored = replace(authority, dependencies=(*authority.dependencies, forward))
    chain = EvolutionChain(candidate=candidate, objects=())
    outcome = next(
        entry
        for entry in verify_evolution(chain, doctored).outcomes
        if entry.subject.lower().startswith("dependency")
    )
    assert not outcome.satisfied
    assert "backward dependency edges" in outcome.detail


def test_a_phase_naming_no_gate_fails_governance_verification(
    mutable: dict[str, Any], candidate: EvolutionCandidate
) -> None:
    """A phase with no gate is a position nothing refuses at, so every later claim that the
    position was governed rests on nothing having been asked."""
    mutable["phases"][0]["gate"] = ""
    authority = _load(mutable)
    chain = EvolutionChain(candidate=candidate, objects=())
    outcome = next(
        entry
        for entry in verify_evolution(chain, authority).outcomes
        if entry.subject.lower().startswith("governance")
    )
    assert not outcome.satisfied
    assert "phases naming no gate" in outcome.detail


def test_a_stage_claimed_by_no_phase_or_by_two_fails_validation(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """Exactly one phase per canonical stage is what makes the loop's coverage a partition. A
    stage claimed twice is measured twice; one claimed never is measured by nothing.

    The loader already refuses a declaration whose stages overlap, so the state set is doctored
    directly — this is the consistency dimension's own guard, not the loader's."""
    contested = replace(authority.lifecycle_states[0], claimed_by=("AUE-P-01", "AUE-P-02"))
    doctored = replace(authority, lifecycle_states=(contested, *authority.lifecycle_states[1:]))
    chain = EvolutionChain(candidate=candidate, objects=())
    outcome = next(
        entry
        for entry in validate_evolution(chain, doctored).outcomes
        if entry.subject.strip().lower() == "consistency"
    )
    assert not outcome.satisfied
    assert "not claimed by exactly one phase" in outcome.detail


def test_two_objects_of_one_kind_in_a_chain_fail_validation(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """One object per kind is what makes a chain a chain rather than a bag: two of one kind
    leaves no answer to "which one did the next phase read"."""
    first = _discovery_object(authority, candidate)
    chain = EvolutionChain(
        candidate=candidate, objects=(first, replace(first, evolution_id=f"{first.evolution_id}x"))
    )
    outcome = next(
        entry
        for entry in validate_evolution(chain, authority).outcomes
        if entry.subject.strip().lower() == "consistency"
    )
    assert not outcome.satisfied
    assert "claim one object kind" in outcome.detail


def test_an_owner_home_that_does_not_resolve_fails_compatibility(
    mutable: dict[str, Any], candidate: EvolutionCandidate
) -> None:
    """Compatibility is a statement about the tree, not about the declaration. A home nobody
    wrote makes every symbol the phase declares unbound and unbindable."""
    mutable["phases"][2]["owners"] = [{"home": "engine/absent/nowhere.py", "symbols": ["run"]}]
    authority = _load(mutable)
    chain = EvolutionChain(candidate=candidate, objects=())
    outcome = next(
        entry
        for entry in validate_evolution(chain, authority).outcomes
        if entry.subject.strip().lower() == "compatibility"
    )
    assert not outcome.satisfied
    assert "do not resolve" in outcome.detail


def test_a_chain_that_renders_differently_twice_fails_reproducibility(
    authority: EvolutionAuthority, candidate: EvolutionCandidate, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Two renders of one chain must be byte-identical or nothing downstream can be compared
    across runs — which is what every digest in this programme is for. Every object is frozen
    and every collection ordered, so a difference here would mean non-determinism entered the
    chain; producing one is the only way to show the dimension can see it."""
    calls = {"n": 0}

    def _drifting(self: EvolutionChain) -> str:
        calls["n"] += 1
        return f"digest-{calls['n']}"

    monkeypatch.setattr(EvolutionChain, "digest", _drifting)
    chain = EvolutionChain(candidate=candidate, objects=())
    outcome = next(
        entry
        for entry in validate_evolution(chain, authority).outcomes
        if entry.subject.strip().lower() == "reproducibility"
    )
    assert not outcome.satisfied
    assert "byte-identical" in outcome.detail


def test_a_declared_discovery_source_resolves_by_its_identifier(
    authority: EvolutionAuthority,
) -> None:
    """The refusal is measured elsewhere; the resolution is the half every candidate's
    provenance check depends on."""
    first = authority.discovery_sources[0]
    assert authority.discovery_source(first.identifier) is first
    with pytest.raises(EvolutionAuthorityError, match="no such discovery source"):
        authority.discovery_source("A-SOURCE-NOBODY-DECLARED")


def test_a_verdict_and_an_execution_record_each_digest_their_own_content(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """Both are recorded downstream under their digest. A digest that did not move with the
    content would record two different verdicts — or two different executions — under one
    identity, which is the collision every identity rule in this programme exists to prevent."""
    chain = EvolutionChain(candidate=candidate, objects=())
    verdict = validate_evolution(chain, authority)
    assert verdict.digest() == validate_evolution(chain, authority).digest()
    assert verdict.digest() != replace(verdict, subject="something else").digest()

    execution = execute_evolution(_through_simulation(candidate, authority), authority)
    assert (
        execution.digest()
        == execute_evolution(_through_simulation(candidate, authority), authority).digest()
    )
    assert execution.digest() != replace(execution, authorised=not execution.authorised).digest()


def test_execution_refuses_a_plan_object_that_authorises_nothing(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """An object carrying no plan authorises nothing, so there is nothing for execution to
    perform. The pipeline satisfies this on every real run, which is why the check had never
    been reached — it is what execution asks INSTEAD of trusting that planning did its job."""
    simulation = _through_simulation(candidate, authority)
    stripped = replace(
        simulation, plan=replace(simulation.plan, obj=replace(simulation.plan.obj, plan=()))
    )
    execution = execute_evolution(stripped, authority)
    assert not execution.authorised
    assert any("carries no plan" in refusal for refusal in execution.refusals)


def test_execution_refuses_an_anonymous_plan_object(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """An object with no identity cannot be traced back to the candidate it came from, so the
    execution record it would produce could never be joined to the chain it belongs to."""
    simulation = _through_simulation(candidate, authority)
    stripped = replace(
        simulation,
        plan=replace(simulation.plan, obj=replace(simulation.plan.obj, evolution_id="")),
    )
    execution = execute_evolution(stripped, authority)
    assert not execution.authorised
    assert any("is anonymous" in refusal for refusal in execution.refusals)


def test_execution_refuses_an_object_carrying_no_evidence(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """The refusal is recorded and the run then FAULTS, because the same emptiness that makes
    execution unauthorised also makes the execution object underivable: an evolution object must
    carry at least one resolving evidence path. Collecting the refusal first is what keeps the
    reason attributable when the fault surfaces."""
    simulation = _through_simulation(candidate, authority)
    stripped = replace(
        simulation, plan=replace(simulation.plan, obj=replace(simulation.plan.obj, evidence=()))
    )
    with pytest.raises(EvolutionAuthorityError, match="at least one resolving evidence path"):
        execute_evolution(stripped, authority)


def test_execution_refuses_a_simulation_that_did_not_authorise_it(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """Simulation is what decides whether execution may be authorised AT ALL. A run that
    executed past an unsettled evaluation would perform a mutation nobody predicted the impact
    of, which is the one thing this loop's ordering exists to prevent."""
    simulation = _through_simulation(candidate, authority)
    execution = execute_evolution(replace(simulation, fixed_point=False), authority)
    assert not execution.authorised
    assert any("did not authorise execution" in refusal for refusal in execution.refusals)


def test_execution_refuses_a_phase_that_names_no_authority(
    authority: EvolutionAuthority, candidate: EvolutionCandidate
) -> None:
    """The authority is what the execution record cites as having permitted the mutation, and a
    phase naming none would produce a record saying a mutation was authorised by nobody. The
    refusal is recorded before the object is derived, and the derivation then faults on the same
    empty field — an evolution object whose identity inputs are incomplete is anonymous, and
    anonymous evolution is refused rather than reported."""
    execution_phase = next(entry for entry in authority.phases if entry.ordinal == 5)
    unauthorised = replace(
        authority,
        phases=tuple(
            replace(entry, authority="") if entry is execution_phase else entry
            for entry in authority.phases
        ),
    )
    with pytest.raises(EvolutionAuthorityError, match="empty identity inputs"):
        execute_evolution(_through_simulation(candidate, authority), unauthorised)
