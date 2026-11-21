"""EPIC-RTE-003 — Runtime Integration & Repository Execution Bridge unit tests.

Proves the single canonical Runtime Bridge wires the repository lifecycle through
the reused engines — RepositorySubject → Composition → Execution → Validation →
Certification → Acceptance, and Execution Evidence → Knowledge — deterministically,
replayably, and resumably, adding no duplicate runtime logic. Every branch of the
bridge is exercised (no skipped path).
"""

from __future__ import annotations

import json

import pytest

from engine.acceptance.contracts import RepositorySubject
from engine.acceptance.engine import AcceptanceDecision
from engine.acceptance.errors import AcceptanceRejectedError
from engine.acceptance.evidence import AcceptanceEvidence
from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase
from engine.runtime.bridge import (
    BRIDGE_RECORD_FORMAT,
    BridgeInputError,
    RepositoryExecutionRecord,
    RuntimeBridge,
    RuntimeBridgeError,
    UnitAssurance,
    ValidatedUnit,
    accept_execution,
    certify_execution,
    compose_repository,
    execute_composition,
    record_execution_evidence,
    validate_execution,
)
from engine.runtime.bridge.contracts import BRIDGE_AUTHORITY
from engine.runtime.composition import RuntimeComposition, Universe
from engine.runtime.execution.platform import ExecutionPlatform, ExecutionResult
from engine.runtime.execution.state import COMPLETED, FAILED, SUCCEEDED
from engine.validation.contracts import ValidationReport

# --------------------------------------------------------------------------- #
# Fixtures                                                                     #
# --------------------------------------------------------------------------- #

_FACTS = {"repository_id": "UCOS-REPO-RTE-0003", "epic_id": "EPIC-RTE-003"}


@pytest.fixture
def facts() -> dict:
    return dict(_FACTS)


@pytest.fixture
def units(make_runtime_unit) -> list[Universe]:
    """A diamond of disclosed universes A→{B,C}→D built from synthetic units."""
    a = Universe.of(make_runtime_unit("A"), context_id="ctx1")
    b = Universe.of(make_runtime_unit("B"), context_id="ctx1", depends_on=["A"])
    c = Universe.of(make_runtime_unit("C"), context_id="ctx1", depends_on=["A"])
    d = Universe.of(make_runtime_unit("D"), context_id="ctx1", depends_on=["B", "C"])
    return [a, b, c, d]


@pytest.fixture
def bridge() -> RuntimeBridge:
    return RuntimeBridge()


# --------------------------------------------------------------------------- #
# Bridge 1 — RepositorySubject → Runtime Composition                           #
# --------------------------------------------------------------------------- #


def test_compose_from_facts_mapping(facts, units):
    composition = compose_repository(facts, units)
    assert isinstance(composition, RuntimeComposition)
    assert composition.universe_ids() == ("A", "B", "C", "D")


def test_compose_from_repository_subject(facts, units):
    subject = RepositorySubject.from_mapping(facts)
    composition = compose_repository(subject, units, coordination="sequential")
    assert composition.coordination == "sequential"


def test_compose_binds_bare_runtime_units(facts, make_runtime_unit):
    # A bare RuntimeUnit (not wrapped in a Universe) is bound verbatim.
    composition = compose_repository(facts, [make_runtime_unit("solo")])
    assert composition.universe_ids() == ("solo",)


def test_compose_rejects_empty_universe_set(facts):
    with pytest.raises(BridgeInputError):
        compose_repository(facts, [])


def test_compose_rejects_foreign_member(facts):
    with pytest.raises(BridgeInputError):
        compose_repository(facts, ["not-a-universe"])


def test_compose_rejects_bad_subject(units):
    # A non-mapping subject is rejected by the reused acceptance assimilation.
    from engine.acceptance.errors import RepositorySubjectError

    with pytest.raises(RepositorySubjectError):
        compose_repository(["bad"], units)


# --------------------------------------------------------------------------- #
# Bridge 2 — Runtime Composition → Runtime Execution                           #
# --------------------------------------------------------------------------- #


def test_execute_composition_returns_result(facts, units):
    composition = compose_repository(facts, units)
    result = execute_composition(composition)
    assert isinstance(result, ExecutionResult)
    assert result.status == SUCCEEDED


def test_execute_composition_honours_outcomes_and_platform(facts, units):
    composition = compose_repository(facts, units)
    platform = ExecutionPlatform()
    result = execute_composition(
        composition, outcomes={"A": FAILED}, execution_subject="engineering", platform=platform
    )
    # A failed root blocks its dependents (deterministic skip propagation).
    assert result.status == FAILED


# --------------------------------------------------------------------------- #
# Bridge 3 — Runtime Execution → Validation                                    #
# --------------------------------------------------------------------------- #


def test_validate_execution_projects_every_unit(facts, units):
    composition = compose_repository(facts, units)
    execution = execute_composition(composition)
    validated = validate_execution(execution)
    assert tuple(v.universe_id for v in validated) == ("A", "B", "C", "D")
    assert all(isinstance(v, ValidatedUnit) for v in validated)
    assert all(isinstance(v.report, ValidationReport) for v in validated)
    # per-universe terminal state is COMPLETED (the run-level status is SUCCEEDED)
    assert all(v.execution_status == COMPLETED for v in validated)


def test_validate_carries_failed_execution_status(facts, units):
    composition = compose_repository(facts, units)
    execution = execute_composition(composition, outcomes={"A": FAILED})
    validated = {v.universe_id: v for v in validate_execution(execution)}
    assert validated["A"].execution_status == FAILED
    assert validated["B"].execution_status == "skipped"


# --------------------------------------------------------------------------- #
# Bridge 4 — Runtime Execution → Certification                                 #
# --------------------------------------------------------------------------- #


def test_certify_execution_produces_assurances(facts, units):
    composition = compose_repository(facts, units)
    execution = execute_composition(composition)
    validated = validate_execution(execution)
    assurances = certify_execution(validated)
    assert tuple(a.universe_id for a in assurances) == ("A", "B", "C", "D")
    assert all(isinstance(a, UnitAssurance) for a in assurances)
    for a in assurances:
        assert a.validated == a.validation.accepted
        assert a.certified == a.certification.certified
        refs = a.evidence_refs()
        assert len(refs) == 2
        assert refs[0].startswith("validation:")
        assert refs[1].startswith("certification:")


def test_assurance_to_dict_is_complete(facts, units):
    composition = compose_repository(facts, units)
    execution = execute_composition(composition)
    assurance = certify_execution(validate_execution(execution))[0]
    blob = assurance.to_dict()
    for key in (
        "universe_id",
        "runtime_id",
        "blueprint_id",
        "execution_status",
        "validated",
        "certified",
        "validation",
        "validation_evidence",
        "certification",
        "certification_evidence",
    ):
        assert key in blob


# --------------------------------------------------------------------------- #
# Bridge 5 — Runtime Execution → Acceptance                                    #
# --------------------------------------------------------------------------- #


def test_accept_execution_returns_decision_and_evidence(facts, units):
    composition = compose_repository(facts, units)
    execution = execute_composition(composition)
    decision, evidence = accept_execution(facts, execution)
    assert isinstance(decision, AcceptanceDecision)
    assert isinstance(evidence, AcceptanceEvidence)
    assert decision.repository_id == facts["repository_id"]
    assert evidence.subject_ref == decision.evidence_ref


def test_accept_execution_strict_raises_when_rejected(facts, units):
    composition = compose_repository(facts, units)
    execution = execute_composition(composition)
    # A minimal subject fails the blocking acceptance gates → strict raises.
    with pytest.raises(AcceptanceRejectedError):
        accept_execution(facts, execution, strict=True)


# --------------------------------------------------------------------------- #
# Bridge 6 — Execution Evidence → Knowledge                                    #
# --------------------------------------------------------------------------- #


def test_record_execution_evidence_authors_evidence_cko(facts, units):
    composition = compose_repository(facts, units)
    execution = execute_composition(composition)
    assurances = certify_execution(validate_execution(execution))
    acceptance, acc_evidence = accept_execution(facts, execution)

    base, cko = record_execution_evidence(
        subject=facts,
        execution=execution,
        assurances=assurances,
        acceptance=acceptance,
        acceptance_evidence=acc_evidence,
    )
    assert isinstance(base, KnowledgeBase)
    assert isinstance(cko, CanonicalKnowledgeObject)
    assert cko.kind is KnowledgeKind.EVIDENCE
    assert cko.authority is KnowledgeAuthority.ENGINEERING
    assert cko.lifecycle is Lifecycle.DRAFT
    assert base.has_object(cko.cko_id)
    # evidence topology carries the execution + per-unit + acceptance references
    assert any(r.startswith("execution:") for r in cko.evidence)
    assert any(r.startswith("acceptance:") for r in cko.evidence)
    assert any(r.startswith("certification:") for r in cko.evidence)
    assert cko.verify_integrity()


def test_record_into_existing_base_and_idempotent_replace(facts, units):
    composition = compose_repository(facts, units)
    execution = execute_composition(composition)
    assurances = certify_execution(validate_execution(execution))
    acceptance, acc_evidence = accept_execution(facts, execution)

    seed = CanonicalKnowledgeObject.create(
        cko_id="UCOS-SEED-0001",
        kind=KnowledgeKind.FACT,
        title="seed",
        statement="pre-existing knowledge",
        universe="runtime",
        authority=KnowledgeAuthority.ENGINEERING,
        owner="tester",
        lifecycle=Lifecycle.DRAFT,
        version="1.0.0",
    )
    base0 = KnowledgeBase([seed])

    base1, cko = record_execution_evidence(
        subject=facts,
        execution=execution,
        assurances=assurances,
        acceptance=acceptance,
        acceptance_evidence=acc_evidence,
        base=base0,
        owner="custom-owner",
        universe="custom-universe",
    )
    assert base1.has_object("UCOS-SEED-0001")
    assert base1.has_object(cko.cko_id)
    assert cko.owner == "custom-owner"
    assert cko.universe == "custom-universe"

    # Re-recording the identical evidence into a base that already holds it replaces
    # it idempotently (deterministic content-address ⇒ same id).
    base2, cko2 = record_execution_evidence(
        subject=facts,
        execution=execution,
        assurances=assurances,
        acceptance=acceptance,
        acceptance_evidence=acc_evidence,
        base=base1,
        owner="custom-owner",
        universe="custom-universe",
    )
    assert cko2.cko_id == cko.cko_id
    assert len(base2.objects()) == len(base1.objects())


# --------------------------------------------------------------------------- #
# The RuntimeBridge facade — end-to-end                                        #
# --------------------------------------------------------------------------- #


def test_run_threads_all_six_bridges(bridge, facts, units):
    record = bridge.run(facts, units)
    assert isinstance(record, RepositoryExecutionRecord)
    assert record.repository_id == facts["repository_id"]
    assert record.epic_id == facts["epic_id"]
    assert record.bridge_id.startswith("UCOS-RTE-BRIDGE-")
    assert record.status == SUCCEEDED
    assert record.composition_id == record.composition.composition_id
    assert record.run_id == record.execution.run_id
    # validated/certified faithfully aggregate the per-unit reused determinations
    assert record.validated == all(a.validated for a in record.assurances)
    assert record.certified == all(a.certified for a in record.assurances)
    assert len(record.assurances) == 4
    assert record.knowledge_id == record.knowledge_object.cko_id
    assert record.evidence_refs() == record.knowledge_object.evidence
    assert record.verify_integrity()


def test_run_record_to_dict_and_format(bridge, facts, units):
    blob = bridge.run(facts, units).to_dict()
    assert blob["bridge_record_format"] == BRIDGE_RECORD_FORMAT
    assert blob["authority"] == BRIDGE_AUTHORITY
    for key in (
        "composition",
        "execution",
        "assurances",
        "acceptance",
        "acceptance_evidence",
        "knowledge_object",
        "bridge_id",
        "content_sha256",
    ):
        assert key in blob


def test_run_is_deterministic(bridge, facts, units):
    a = bridge.run(facts, units)
    b = bridge.run(facts, units)
    assert a.bridge_id == b.bridge_id
    assert a.content_sha256 == b.content_sha256
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)


def test_run_strict_raises_when_repository_rejected(bridge, facts, units):
    with pytest.raises(AcceptanceRejectedError):
        bridge.run(facts, units, strict=True)


def test_run_with_outcomes_records_failure(bridge, facts, units):
    record = bridge.run(facts, units, outcomes={"A": FAILED})
    assert record.status == FAILED
    # the failed root is carried into the per-unit assurance execution status
    a_state = {a.universe_id: a.execution_status for a in record.assurances}
    assert a_state["A"] == FAILED


def test_facade_individual_stages_compose(bridge, facts, units):
    composition = bridge.compose(facts, units)
    execution = bridge.execute(composition)
    validated = bridge.validate(execution)
    assurances = bridge.certify(validated)
    acceptance, evidence = bridge.accept(facts, execution)
    new_base, cko = bridge.record(
        subject=facts,
        execution=execution,
        assurances=assurances,
        acceptance=acceptance,
        acceptance_evidence=evidence,
    )
    assert new_base.has_object(cko.cko_id)
    assert bridge.platform is not None


def test_into_knowledge_adds_and_replaces(bridge, facts, units):
    record = bridge.run(facts, units)
    base = bridge.into_knowledge(record)
    assert base.has_object(record.knowledge_id)
    # into an existing base that already holds it → replaced (idempotent)
    base2 = bridge.into_knowledge(record, base=base)
    assert len(base2.objects()) == 1


# --------------------------------------------------------------------------- #
# Replayability & resumability (reused platform capabilities)                  #
# --------------------------------------------------------------------------- #


def test_replay_reproduces_run(bridge, facts, units):
    record = bridge.run(facts, units)
    replayed = bridge.replay(record)
    assert replayed.run_id == record.run_id
    assert bridge.verify_replay(record).valid
    assert bridge.require_replay(record).valid


def test_checkpoint_resume_and_recover(bridge, facts, units):
    record = bridge.run(facts, units)
    cp = bridge.checkpoint(record, through_stage=0)
    resumed = bridge.resume(record, cp)
    assert bridge.platform.verify_continuation(record.execution.run, resumed)
    recovered = bridge.recover(record)
    assert recovered.run_id == record.run_id


# --------------------------------------------------------------------------- #
# Record integrity                                                             #
# --------------------------------------------------------------------------- #


def test_record_integrity_detects_mutation(bridge, facts, units):
    import dataclasses

    record = bridge.run(facts, units)
    record.require_integrity()  # clean
    tampered = dataclasses.replace(record, repository_id="MUTATED")
    assert not tampered.verify_integrity()
    with pytest.raises(RuntimeBridgeError):
        tampered.require_integrity()
