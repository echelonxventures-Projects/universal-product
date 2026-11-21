"""UCOS-EPIC-014 — Assurance Orchestrator runtime tests (runtime-facing scope).

The orchestrator is the only module that composes all ten stages, and it is the one place
where the package's two strongest claims are testable together: that the *core* of a run
is a pure function of subject and policy, and that the parts of a run which are **not**
pure — the registry, the evidence directory — are the only parts that change.

So these tests separate the two. `core()` is driven twice and compared byte-for-byte.
`run()` is driven for its side effects: exactly one registration per run, an append-only
registry that refuses the same determination twice, and evidence written only where the
policy permits.

Runtime scope only: this file exercises orchestration. Stage verdicts are read from the
report rather than re-derived, because certification verdict logic belongs to another
session — these tests assert *that* the orchestrator reports them, never *what* they are.
"""

from __future__ import annotations

import dataclasses
from platform.universal_assurance.contracts import AssuranceStage, Verdict
from platform.universal_assurance.errors import (
    AssuranceEvidenceError,
    AssuranceExecutionError,
    AssuranceRegistryError,
)
from platform.universal_assurance.orchestrator import (
    OUTCOME_FORMAT,
    REPLAY_LABEL,
    AssuranceOrchestrator,
    stages_before,
)
from platform.universal_assurance.registry import CertificationRegistry

import pytest

from .universal_assurance_helpers import factless_subject, make_policy, make_subject


@pytest.fixture
def policy():
    return make_policy()


@pytest.fixture
def subject():
    return make_subject()


@pytest.fixture
def orchestrator(policy):
    return AssuranceOrchestrator(policy)


# --- stage ordering --------------------------------------------------------------


def test_stages_before_is_derived_from_the_stage_vocabulary_not_enumerated():
    """Adding a stage must not require editing the orchestrator."""
    for stage in AssuranceStage:
        preceding = stages_before(stage)
        assert all(s.order < stage.order for s in preceding)
        assert list(preceding) == sorted(preceding, key=lambda s: s.order)


def test_the_first_stage_has_nothing_before_it_and_the_last_has_every_other():
    ordered = sorted(AssuranceStage, key=lambda s: s.order)

    assert stages_before(ordered[0]) == ()
    assert len(stages_before(ordered[-1])) == len(ordered) - 1


# --- construction ----------------------------------------------------------------


def test_the_orchestrator_refuses_anything_that_is_not_an_assurance_policy():
    with pytest.raises(AssuranceExecutionError):
        AssuranceOrchestrator({"policy": "not-assimilated"})


def test_the_registry_id_comes_from_the_policy_binding_never_hardcoded(policy):
    assert AssuranceOrchestrator(policy).registry.registry_id == policy.binding("registry_id")


def test_an_injected_registry_is_used_as_is(policy):
    supplied = CertificationRegistry("SUPPLIED-REGISTRY")

    orchestrator = AssuranceOrchestrator(policy, registry=supplied)

    assert orchestrator.registry is supplied
    assert orchestrator.policy is policy


def test_the_default_policy_is_loaded_when_none_is_supplied():
    orchestrator = AssuranceOrchestrator()

    assert orchestrator.policy.identity.id
    assert orchestrator.registry.registry_id == orchestrator.policy.binding("registry_id")


# --- the deterministic core ------------------------------------------------------


def test_the_core_refuses_anything_that_is_not_an_assurance_subject(orchestrator):
    with pytest.raises(AssuranceExecutionError):
        orchestrator.core({"subject_id": "not-assimilated"})


def test_the_core_is_a_pure_function_of_subject_and_policy(orchestrator, subject):
    """Two independent compositions must agree byte-for-byte."""
    first = orchestrator.core(subject)
    second = orchestrator.core(subject)

    assert first.digest() == second.digest()
    assert first.payload() == second.payload()


def test_two_separate_orchestrators_reproduce_the_same_core(policy, subject):
    """Purity must not depend on instance state carried between stages."""
    left = AssuranceOrchestrator(policy).core(subject)
    right = AssuranceOrchestrator(policy).core(subject)

    assert left.digest() == right.digest()


def test_the_core_touches_no_registry_and_no_filesystem(orchestrator, subject, tmp_path):
    before = len(orchestrator.registry)

    orchestrator.core(subject)

    assert len(orchestrator.registry) == before
    assert list(tmp_path.iterdir()) == []


def test_a_different_subject_produces_a_different_core(orchestrator, subject):
    other = make_subject(subject_id="OTHER-SUBJECT")

    assert orchestrator.core(subject).digest() != orchestrator.core(other).digest()


def test_the_core_payload_carries_every_stage_artifact(orchestrator, subject):
    payload = orchestrator.core(subject).payload()

    assert set(payload) == {
        "validation_plan",
        "validation_suite",
        "validation_execution",
        "validation_intelligence",
        "certification_plan",
        "interim_measurement",
        "certification_execution",
    }


def test_core_observations_merge_every_stage_that_published_one(orchestrator, subject):
    core = orchestrator.core(subject)
    observations = core.observations()

    assert observations
    assert all(isinstance(value, float) for value in observations.values())
    for key in core.validation_execution.observations():
        assert key in observations


def test_the_core_is_immutable(orchestrator, subject):
    core = orchestrator.core(subject)

    with pytest.raises(dataclasses.FrozenInstanceError):
        core.validation_plan = None  # type: ignore[misc]


# --- the full run ----------------------------------------------------------------


def test_a_run_completes_every_declared_stage(orchestrator, subject):
    outcome = orchestrator.run(subject)

    assert outcome.report.counts()["stages"] == len(AssuranceStage)
    assert set(outcome.report.stage_verdicts()) == {s.value for s in AssuranceStage}


def test_a_run_registers_exactly_one_certification(orchestrator, subject):
    outcome = orchestrator.run(subject)

    assert len(orchestrator.registry) == 1
    assert outcome.registry_entry is not None
    assert outcome.registry_entry.certification_id == outcome.certification_id
    assert orchestrator.registry.verify() is True


def test_the_registered_entry_binds_the_certification_to_the_run_that_produced_it(
    orchestrator, subject
):
    outcome = orchestrator.run(subject)
    entry = outcome.registry_entry

    assert entry.validation_plan_sha256 == outcome.core.validation_plan.plan_sha256
    assert entry.certification_plan_sha256 == outcome.core.certification_plan.plan_sha256
    assert entry.validation_execution_sha256 == outcome.core.validation_execution.execution_sha256
    assert entry.policy_digest == outcome.policy_digest
    assert entry.subject_id == subject.subject_id


def test_the_append_only_registry_refuses_the_same_determination_twice(orchestrator, subject):
    """The certification id is deterministic, so a replayed run must not re-register."""
    orchestrator.run(subject)

    with pytest.raises(AssuranceRegistryError):
        orchestrator.run(subject)

    assert len(orchestrator.registry) == 1


def test_the_outcome_hash_is_reproducible_across_independent_orchestrators(policy, subject):
    left = AssuranceOrchestrator(policy).run(subject)
    right = AssuranceOrchestrator(policy).run(subject)

    assert left.outcome_sha256 == right.outcome_sha256
    assert left.seal_line() == right.seal_line()


def test_a_material_change_moves_the_outcome_hash(policy, subject):
    baseline = AssuranceOrchestrator(policy).run(subject)
    altered = AssuranceOrchestrator(policy).run(make_subject(subject_id="OTHER-SUBJECT"))

    assert altered.outcome_sha256 != baseline.outcome_sha256


# --- replay ----------------------------------------------------------------------


def test_a_run_replays_its_own_core_and_proves_byte_identity(orchestrator, subject):
    outcome = orchestrator.run(subject, replay=True)

    assert outcome.reproducibility is not None
    assert outcome.reproducibility.label == REPLAY_LABEL
    assert outcome.reproducibility.byte_identical is True
    assert outcome.reproducibility.replays == orchestrator.policy.reproducibility.replays


def test_replay_can_be_declined_and_is_then_reported_as_absent(orchestrator, subject):
    outcome = orchestrator.run(subject, replay=False)

    assert outcome.reproducibility is None
    assert outcome.to_dict()["reproducibility"] is None


def test_declining_replay_changes_the_outcome_hash(policy, subject):
    """The reproducibility proof is part of what the outcome commits to."""
    replayed = AssuranceOrchestrator(policy).run(subject, replay=True)
    unreplayed = AssuranceOrchestrator(policy).run(subject, replay=False)

    assert replayed.outcome_sha256 != unreplayed.outcome_sha256


def test_the_replay_proof_covers_the_actual_run_not_two_fresh_ones(orchestrator, subject):
    """The first sample is the completed core, so the proof binds to what really ran."""
    outcome = orchestrator.run(subject, replay=True)

    assert outcome.reproducibility.samples[0].digest == outcome.core.digest()


# --- evidence --------------------------------------------------------------------


def test_no_evidence_is_written_unless_a_directory_is_requested(orchestrator, subject, tmp_path):
    orchestrator.run(subject)

    assert list(tmp_path.iterdir()) == []


def test_evidence_is_written_when_a_directory_is_requested(orchestrator, subject, tmp_path):
    target = tmp_path / "assurance"

    outcome = orchestrator.run(subject, evidence_dir=str(target))

    written = list(target.rglob("*"))
    assert written, "an evidence directory was requested but nothing was written"
    assert outcome.bundle.counts()["artifacts"] > 0


def test_evidence_writing_is_refused_under_a_policy_forbidden_prefix(policy, subject, tmp_path):
    forbidden = policy.evidence.forbidden_write_prefixes
    assert forbidden, "the fixture policy must declare a forbidden prefix to test this"

    with pytest.raises(AssuranceEvidenceError):
        AssuranceOrchestrator(policy).run(subject, evidence_dir=forbidden[0])


def test_the_bundle_carries_every_stage_the_policy_requires(orchestrator, subject):
    outcome = orchestrator.run(subject)

    assert outcome.bundle.counts()["artifacts"] > 0
    assert outcome.bundle.bundle_sha256


# --- the outcome record ----------------------------------------------------------


def test_the_outcome_reports_gates_without_re_deriving_their_verdicts(orchestrator, subject):
    outcome = orchestrator.run(subject)

    assert outcome.gates_passed() + len(outcome.gates_failed()) == len(outcome.gates)
    assert all("gate_id" in gate for gate in outcome.gates)


def test_the_determination_and_pass_flag_come_from_the_report(orchestrator, subject):
    outcome = orchestrator.run(subject)

    assert outcome.determination == outcome.report.determination
    assert outcome.passed is outcome.report.passed
    assert outcome.certified is outcome.core.certification_execution.certified


def test_a_failed_stage_prevents_an_assured_determination(orchestrator, subject):
    outcome = orchestrator.run(subject)
    failed = [s for s, v in outcome.report.stage_verdicts().items() if v == Verdict.FAIL.value]

    if failed:
        assert outcome.passed is False
        assert outcome.determination != "ASSURED"
    else:
        assert outcome.passed is True


def test_the_seal_line_is_a_single_line_summarising_the_whole_run(orchestrator, subject):
    outcome = orchestrator.run(subject)
    seal = outcome.seal_line()

    assert "\n" not in seal
    assert outcome.policy_id in seal
    assert outcome.determination in seal
    assert outcome.outcome_sha256[:16] in seal
    assert f"certified={str(outcome.certified).lower()}" in seal


def test_the_serialized_outcome_declares_its_format_and_embeds_no_wall_clock(orchestrator, subject):
    payload = orchestrator.run(subject).to_dict()

    assert payload["outcome_format"] == OUTCOME_FORMAT
    assert payload["registry_entry"] is not None
    assert "timestamp" not in payload
    assert set(payload) >= {
        "validation_plan",
        "validation_suite",
        "validation_execution",
        "certification_execution",
        "certification_registry",
        "measurement",
        "evidence_bundle",
        "dashboard",
    }


def test_the_outcome_is_immutable(orchestrator, subject):
    outcome = orchestrator.run(subject)

    with pytest.raises(dataclasses.FrozenInstanceError):
        outcome.outcome_sha256 = "tampered"  # type: ignore[misc]


# --- fail-closed on an undecidable subject ---------------------------------------


def test_a_subject_supplying_no_facts_still_completes_and_fails_closed(policy):
    """Absent evidence must produce a recorded failure, never an exception or a pass."""
    outcome = AssuranceOrchestrator(policy).run(factless_subject())

    assert outcome.passed is False
    assert outcome.determination != "ASSURED"
    assert outcome.report.counts()["stages"] == len(AssuranceStage)


def test_a_factless_run_is_still_reproducible(policy):
    outcome = AssuranceOrchestrator(policy).run(factless_subject(), replay=True)

    assert outcome.reproducibility.byte_identical is True
