"""UCOS-EPIC-014 — Validation Planning & Certification Planning tests.

Planning's central claim is that "an obligation whose required facts are absent is
planned and recorded as unsatisfiable — never silently dropped", so absence of evidence
can never be mistaken for evidence of correctness. These tests drive a subject with no
facts at all through both planners and assert the obligations survive into the plan
marked undecidable, with the blocking ones closing the plan.

The fact-address grammar is the only coupling between a policy document and a subject's
shape, so each of its four prefixes is resolved positively and negatively, and an
unrecognized prefix is proven to be an authoring fault rather than a fail-closed verdict.
"""

from __future__ import annotations

from platform.universal_assurance.contracts import AssuranceStage, ObligationKind
from platform.universal_assurance.errors import AssurancePlanError
from platform.universal_assurance.planning import (
    PLAN_FORMAT,
    REASON_UNSATISFIABLE,
    AssurancePlan,
    CertificationPlanner,
    PlanKind,
    PlannedObligation,
    ValidationPlanner,
    evaluate_gates,
    gate_outcomes,
    resolve_fact_address,
)

import pytest

from .universal_assurance_helpers import (
    REAL_CRITERION_REF,
    REAL_FRAME_REF,
    factless_subject,
    make_policy,
    make_subject,
    policy_mapping,
    subject_mapping,
)

# -- the fact-address grammar -------------------------------------------------


@pytest.mark.parametrize(
    "address,expected",
    [
        ("repository_truth", True),
        ("validation.architecture", True),
        ("validation.quality", False),
        ("intelligence.architecture_compliance", True),
        ("intelligence.governance_compliance", False),
        ("observations.coverage_line_percent", True),
        ("observations.absent", False),
    ],
)
def test_every_supported_fact_address_resolves_against_the_subject(address, expected):
    assert resolve_fact_address(make_subject(), address) is expected


def test_an_unrecognized_fact_prefix_is_an_authoring_fault():
    with pytest.raises(AssurancePlanError) as exc:
        resolve_fact_address(make_subject(), "telemetry.latency")
    assert "unrecognized fact address" in str(exc.value)


def test_an_empty_fact_block_does_not_count_as_present_evidence():
    """A declared-but-empty domain is absence of evidence, not evidence."""
    subject = make_subject(validation_facts={"architecture": {}})
    assert resolve_fact_address(subject, "validation.architecture") is False


def test_a_zero_observation_still_counts_as_observed():
    """Presence is keyed on the key existing, not on the value being truthy."""
    subject = make_subject(observations={"zero": 0.0})
    assert resolve_fact_address(subject, "observations.zero") is True


# -- planned obligations ------------------------------------------------------


def test_a_planned_obligation_records_exactly_which_facts_were_missing():
    policy = make_policy()
    planned = PlannedObligation.create(policy.obligation("OB-RULE"), factless_subject())
    assert planned.satisfiable is False
    assert planned.missing_facts == ("validation.architecture",)
    assert planned.is_blocking_shortfall is True


def test_an_advisory_obligation_shortfall_does_not_close_the_plan():
    policy = make_policy()
    planned = PlannedObligation.create(policy.obligation("OB-FRAME"), factless_subject())
    assert planned.satisfiable is False
    assert planned.blocking is False
    assert planned.is_blocking_shortfall is False


def test_planned_obligation_core_excludes_the_rationale_prose():
    policy = make_policy()
    planned = PlannedObligation.create(policy.obligation("OB-RULE"), make_subject())
    assert "rationale" not in planned.core()
    assert planned.to_dict()["rationale"] == "the architecture must declare its layers"


# -- plan synthesis -----------------------------------------------------------


def test_the_validation_planner_plans_its_two_declared_stages():
    plan = ValidationPlanner(make_policy()).plan(make_subject())
    assert plan.plan_kind is PlanKind.VALIDATION
    assert plan.plan_id.startswith("UCOS-VPLAN-")
    assert set(plan.obligation_ids()) == {"OB-RULE", "OB-DIM"}
    assert plan.stages == ValidationPlanner.DEFAULT_STAGES


def test_the_certification_planner_plans_the_certification_stage():
    plan = CertificationPlanner(make_policy()).plan(make_subject())
    assert plan.plan_kind is PlanKind.CERTIFICATION
    assert plan.plan_id.startswith("UCOS-CPLAN-")
    assert set(plan.obligation_ids()) == {"OB-CRIT", "OB-FRAME"}


def test_nothing_is_dropped_when_a_subject_supplies_no_facts_at_all():
    """The whole fail-closed claim: undecidable obligations stay in the plan."""
    plan = ValidationPlanner(make_policy()).plan(factless_subject())
    assert set(plan.obligation_ids()) == {"OB-RULE", "OB-DIM"}
    assert len(plan.unsatisfiable) == 2
    assert plan.satisfiable == ()
    assert plan.decidable is False
    assert set(plan.blocking_shortfalls()) == {"OB-RULE", "OB-DIM"}


def test_a_decidable_plan_reports_itself_decidable():
    plan = ValidationPlanner(make_policy()).plan(make_subject())
    assert plan.decidable is True
    assert plan.blocking_shortfalls() == ()


def test_advisory_shortfalls_are_reported_separately_from_blocking_ones():
    plan = CertificationPlanner(make_policy()).plan(factless_subject())
    assert plan.blocking_shortfalls() == ("OB-CRIT",)
    assert plan.advisory_shortfalls() == ("OB-FRAME",)


def test_a_plan_requires_at_least_one_stage():
    with pytest.raises(AssurancePlanError) as exc:
        AssurancePlan.create(
            plan_kind=PlanKind.VALIDATION,
            subject=make_subject(),
            policy=make_policy(),
            stages=(),
        )
    assert "at least one stage" in str(exc.value)


def test_a_plan_can_be_narrowed_to_selected_obligation_kinds():
    plan = AssurancePlan.create(
        plan_kind=PlanKind.VALIDATION,
        subject=make_subject(),
        policy=make_policy(),
        stages=(AssuranceStage.VALIDATION_EXECUTION, AssuranceStage.VALIDATION_INTELLIGENCE),
        kinds=(ObligationKind.VALIDATION_RULE,),
    )
    assert plan.obligation_ids() == ("OB-RULE",)


def test_a_plan_admits_only_the_gates_spanning_its_stages():
    validation = ValidationPlanner(make_policy()).plan(make_subject())
    certification = CertificationPlanner(make_policy()).plan(make_subject())
    assert [g.id for g in validation.gates] == ["G-VALIDATION"]
    assert [g.id for g in certification.gates] == ["G-CERTIFICATION"]


def test_planners_reject_the_wrong_input_types():
    with pytest.raises(AssurancePlanError):
        ValidationPlanner("not-a-policy")
    with pytest.raises(AssurancePlanError):
        CertificationPlanner("not-a-policy")
    with pytest.raises(AssurancePlanError):
        ValidationPlanner(make_policy()).plan("not-a-subject")
    with pytest.raises(AssurancePlanError):
        CertificationPlanner(make_policy()).plan("not-a-subject")


def test_a_planner_accepts_an_explicit_stage_override():
    planner = ValidationPlanner(make_policy(), stages=(AssuranceStage.VALIDATION_EXECUTION,))
    assert planner.stages == (AssuranceStage.VALIDATION_EXECUTION,)
    assert planner.plan(make_subject()).obligation_ids() == ("OB-RULE",)
    assert planner.policy.identity.id == "TEST-POLICY-001"


def test_the_certification_planner_exposes_the_policy_and_stages_it_binds():
    policy = make_policy()
    default = CertificationPlanner(policy)
    assert default.policy is policy
    assert default.stages == CertificationPlanner.DEFAULT_STAGES

    overridden = CertificationPlanner(policy, stages=(AssuranceStage.CERTIFICATION_PLANNING,))
    assert overridden.stages == (AssuranceStage.CERTIFICATION_PLANNING,)


# -- reused-implementation refs ----------------------------------------------


def test_refs_of_kind_are_distinct_and_sorted():
    plan = CertificationPlanner(make_policy()).plan(make_subject())
    planner = CertificationPlanner(make_policy())
    assert planner.criteria_refs(plan) == (REAL_CRITERION_REF,)
    assert planner.frame_refs(plan) == (REAL_FRAME_REF,)
    assert plan.refs_of_kind(ObligationKind.VALIDATION_RULE) == ()


def test_obligations_of_kind_selects_the_planned_entries():
    plan = ValidationPlanner(make_policy()).plan(make_subject())
    rules = plan.obligations_of_kind(ObligationKind.VALIDATION_RULE)
    assert [item.id for item in rules] == ["OB-RULE"]


# -- the method the orchestrator depends on ----------------------------------


def test_a_decidable_plan_contributes_no_gate_failures():
    plan = ValidationPlanner(make_policy()).plan(make_subject())
    assert plan.failure_reasons_for_shortfalls() == {}


def test_undecidable_obligations_are_reported_as_gate_failures_at_either_severity():
    """The sibling contributors to the run-level gate map report every non-passing
    obligation regardless of severity; the plan's contribution matches, so an
    undecidable advisory obligation cannot quietly leave a gate open."""
    plan = CertificationPlanner(make_policy()).plan(factless_subject())
    assert plan.failure_reasons_for_shortfalls() == {
        "OB-CRIT": REASON_UNSATISFIABLE,
        "OB-FRAME": REASON_UNSATISFIABLE,
    }


def test_the_unsatisfiable_reason_has_exactly_one_spelling_across_the_package():
    from platform.universal_assurance.certification import REASON_UNSATISFIABLE as cert_reason
    from platform.universal_assurance.generation import UNBOUND_UNSATISFIABLE as gen_reason

    assert REASON_UNSATISFIABLE == gen_reason == cert_reason == "unsatisfiable-obligation"


# -- measurability ------------------------------------------------------------


def test_plan_coverage_is_one_when_the_policy_declares_nothing_for_the_stages():
    plan = AssurancePlan.create(
        plan_kind=PlanKind.VALIDATION,
        subject=make_subject(),
        policy=make_policy(),
        stages=(AssuranceStage.CERTIFICATION_REGISTRY,),
    )
    assert plan.declared_total == 0
    assert plan.coverage() == 1.0


def test_plan_observations_are_namespaced_by_planning_capability():
    validation = ValidationPlanner(make_policy()).plan(make_subject()).observations()
    certification = CertificationPlanner(make_policy()).plan(make_subject()).observations()
    assert all(key.startswith("plan.") for key in validation)
    assert all(key.startswith("certification_plan.") for key in certification)
    assert validation["plan.obligations_planned"] == 2.0
    assert certification["certification_plan.gate_count"] == 1.0


def test_plan_observations_expose_the_shortfall_count_metrics_decide_on():
    observations = ValidationPlanner(make_policy()).plan(factless_subject()).observations()
    assert observations["plan.unsatisfiable_obligations"] == 2.0
    assert observations["plan.blocking_shortfalls"] == 2.0


def test_plan_counts_reconcile_with_its_obligation_partitions():
    plan = CertificationPlanner(make_policy()).plan(factless_subject())
    counts = plan.counts()
    assert counts["planned"] == len(plan.planned)
    assert counts["satisfiable"] + counts["unsatisfiable"] == counts["planned"]


# -- reproducibility ----------------------------------------------------------


def test_an_identical_subject_and_policy_reproduce_an_identical_plan():
    first = ValidationPlanner(make_policy()).plan(make_subject())
    second = ValidationPlanner(make_policy()).plan(make_subject())
    assert first.plan_sha256 == second.plan_sha256
    assert first.plan_id == second.plan_id
    assert first.to_dict() == second.to_dict()


def test_the_plan_hash_changes_when_the_subject_loses_a_fact():
    decidable = ValidationPlanner(make_policy()).plan(make_subject())
    undecidable = ValidationPlanner(make_policy()).plan(factless_subject())
    assert decidable.plan_sha256 != undecidable.plan_sha256


def test_the_plan_hash_changes_when_the_policy_changes():
    document = policy_mapping()
    document["obligations"][0]["severity"] = "advisory"
    from platform.universal_assurance.policy import parse_policy

    base = ValidationPlanner(make_policy()).plan(make_subject())
    altered = ValidationPlanner(parse_policy(document)).plan(make_subject())
    assert base.plan_sha256 != altered.plan_sha256


def test_the_plan_anchors_itself_to_the_exact_subject_and_policy_text():
    subject, policy = make_subject(), make_policy()
    plan = ValidationPlanner(policy).plan(subject)
    assert plan.subject_digest == subject.digest()
    assert plan.policy_digest == policy.digest()
    assert plan.to_dict()["plan_format"] == PLAN_FORMAT


def test_a_plan_is_immutable():
    plan = ValidationPlanner(make_policy()).plan(make_subject())
    with pytest.raises(Exception):  # noqa: B017 — frozen dataclass
        plan.plan_id = "x"  # type: ignore[misc]


# -- gate evaluation ----------------------------------------------------------


def test_a_gate_passes_when_none_of_its_obligations_failed():
    plan = ValidationPlanner(make_policy()).plan(make_subject())
    outcomes = gate_outcomes(plan, {})
    assert [o["gate_id"] for o in outcomes] == ["G-VALIDATION"]
    assert outcomes[0]["passed"] is True


def test_a_gate_fails_when_an_obligation_it_composes_failed():
    plan = ValidationPlanner(make_policy()).plan(make_subject())
    outcomes = gate_outcomes(plan, {"OB-RULE": "not-executed"})
    assert outcomes[0]["passed"] is False
    assert outcomes[0]["failures"] == ["OB-RULE"]


def test_a_gate_over_a_failed_stage_cannot_pass_vacuously():
    """A gate spanning a stage that declares no obligation would otherwise always pass."""
    policy = make_policy()
    outcomes = evaluate_gates(
        policy.gates,
        failed_obligations={},
        failed_stages=(AssuranceStage.CERTIFICATION_EXECUTION,),
    )
    by_id = {o["gate_id"]: o for o in outcomes}
    assert by_id["G-CERTIFICATION"]["passed"] is False
    assert by_id["G-CERTIFICATION"]["failed_stages"] == ["certification-execution"]
    assert by_id["G-VALIDATION"]["passed"] is True


def test_gate_outcomes_are_returned_in_canonical_id_order():
    policy = make_policy()
    outcomes = evaluate_gates(reversed(policy.gates), failed_obligations={})
    assert [o["gate_id"] for o in outcomes] == ["G-CERTIFICATION", "G-VALIDATION"]


def test_gate_outcomes_report_their_composition_for_audit():
    policy = make_policy()
    outcome = evaluate_gates(policy.gates, failed_obligations={})[0]
    assert outcome["name"] == "certification gate"
    assert outcome["obligations"] == ["OB-CRIT", "OB-FRAME"]
    assert outcome["stages"] == ["certification-execution"]


def test_evaluating_no_gates_yields_no_outcomes():
    assert evaluate_gates((), failed_obligations={}) == ()


def test_planning_ignores_a_subject_fact_no_obligation_asked_for():
    """Extra facts are inert: the plan is a function of the policy's demands."""
    lean = ValidationPlanner(make_policy()).plan(make_subject())
    rich = ValidationPlanner(make_policy()).plan(
        make_subject(
            validation_facts={
                **subject_mapping()["validation_facts"],
                "quality": {"coverage": 99},
            }
        )
    )
    assert lean.obligation_ids() == rich.obligation_ids()
    assert lean.counts() == rich.counts()
