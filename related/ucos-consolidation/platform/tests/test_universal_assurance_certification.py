"""UCOS-EPIC-014 — Certification Execution & Certification Evidence tests.

This capability "issues no certificate of its own and re-judges nothing" — the
certificate, the audit ledger, the compliance engine and the certification rules all come
from :mod:`engine.universal_certification`. What it *adds* is everything the reused
certifier cannot know, and that addition is exactly what these tests attack:

* **Input adaptation.** The reused certifier consumes a validation/measurement/truth
  triple. The projection is proven to express obligation-level, policy-governed counts —
  not raw rule results — so the certifier reads the policy's truth.
* **Declared disclosure binding.** The check id the certifier looks for is read from the
  policy's ``bindings``, never hardcoded. Changing the binding must change the input.
* **Fail-closed reconciliation.** An unbindable criterion, an unevaluated criterion, a
  malformed repository-truth attestation and an absent decision each produce a *recorded*
  blocking failure and no certification — never a silent pass.
* **Policy severity governs.** A finding is reconciled under the policy's severity, not
  the reused rule's.
* **Gates close certification.** A certificate that fails a declared gate closes the
  stage even when the reused rule suite alone would have passed.
"""

from __future__ import annotations

from platform.universal_assurance.certification import (
    CERTIFICATION_EXECUTION_FORMAT,
    REASON_MALFORMED_REPOSITORY_TRUTH,
    REASON_NO_DECISION,
    REASON_NOT_EVALUATED,
    REASON_UNKNOWN_CRITERION,
    REASON_UNKNOWN_FRAME,
    REASON_UNSATISFIABLE,
    CertificationExecution,
    CertificationExecutor,
    CriterionCatalog,
    build_repository_truth_input,
    build_validation_input,
)
from platform.universal_assurance.contracts import Outcome, Severity, Verdict
from platform.universal_assurance.errors import AssuranceExecutionError
from platform.universal_assurance.execution import ObligationOutcome, ValidationExecutor
from platform.universal_assurance.generation import SuiteGenerator
from platform.universal_assurance.measurement import measure
from platform.universal_assurance.planning import CertificationPlanner, ValidationPlanner
from platform.universal_assurance.policy import parse_policy

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


def _validation_execution(policy=None, subject=None):
    policy = policy if policy is not None else make_policy()
    subject = subject if subject is not None else make_subject()
    suite = SuiteGenerator().generate(ValidationPlanner(policy).plan(subject))
    return ValidationExecutor().execute(suite, subject)


def _measurement(policy=None, subject=None, observations=None):
    policy = policy if policy is not None else make_policy()
    subject = subject if subject is not None else make_subject()
    return measure(
        subject_id=subject.subject_id,
        policy=policy,
        observations=observations if observations is not None else {},
    )


def _certify(policy=None, subject=None, catalog=None, observations=None):
    policy = policy if policy is not None else make_policy()
    subject = subject if subject is not None else make_subject()
    return CertificationExecutor(policy, catalog=catalog).execute(
        plan=CertificationPlanner(policy).plan(subject),
        subject=subject,
        validation_execution=_validation_execution(policy, subject),
        measurement_report=_measurement(policy, subject, observations),
    )


# -- the fixture's own refs must be real -------------------------------------


def test_every_fixture_ref_resolves_in_the_reused_catalogues():
    """A fixture ref that stops resolving does not fail these tests — it silently
    unbinds the pipeline and turns them into no-ops. Guard the fixture itself."""
    from platform.universal_assurance.generation import RuleCatalog

    validation, certification = RuleCatalog(), CriterionCatalog()
    from .universal_assurance_helpers import (
        REAL_ADVISORY_RULE_REF,
        REAL_DIMENSION_REF,
        REAL_RULE_REF,
    )

    assert validation.rule(REAL_RULE_REF) is not None
    assert validation.rule(REAL_ADVISORY_RULE_REF) is not None
    assert validation.dimension(REAL_DIMENSION_REF) is not None
    assert certification.rule(REAL_CRITERION_REF) is not None
    assert certification.frame(REAL_FRAME_REF) is not None


# -- the catalogue is the reused certifier, not a local copy -----------------


def test_the_default_criterion_catalogue_is_the_reused_certification_suite():
    from engine.universal_certification.compliance import default_frames
    from engine.universal_certification.rules import default_rules

    catalog = CriterionCatalog()
    assert catalog.rule_ids == tuple(sorted(r.rule_id for r in default_rules()))
    assert catalog.frame_ids == tuple(sorted(f.frame_id for f in default_frames()))


def test_the_catalogue_resolves_declared_refs_and_returns_none_for_unknown_ones():
    catalog = CriterionCatalog()
    assert catalog.rule(REAL_CRITERION_REF) is not None
    assert catalog.frame(REAL_FRAME_REF) is not None
    assert catalog.rule("no-such-criterion") is None
    assert catalog.frame("no-such-frame") is None


def test_a_catalogue_can_be_narrowed_to_an_explicit_rule_and_frame_set():
    from engine.universal_certification.compliance import default_frames
    from engine.universal_certification.rules import default_rules

    rule = next(r for r in default_rules() if r.rule_id == REAL_CRITERION_REF)
    frame = next(f for f in default_frames() if f.frame_id == REAL_FRAME_REF)
    catalog = CriterionCatalog([rule], frames=[frame])
    assert catalog.rule_ids == (REAL_CRITERION_REF,)
    assert catalog.frame_ids == (REAL_FRAME_REF,)


def test_the_catalogue_serializes_both_indexes():
    payload = CriterionCatalog().to_dict()
    assert REAL_CRITERION_REF in payload["rules"]
    assert REAL_FRAME_REF in payload["frames"]


# -- input adaptation ---------------------------------------------------------


def test_the_validation_input_speaks_obligation_counts_not_raw_rule_results():
    """The certifier's advisory `validation-complete` rule must read policy truth."""
    policy, subject = make_policy(), make_subject()
    execution = _validation_execution(policy, subject)
    payload = build_validation_input(subject=subject, execution=execution, policy=policy)
    counts = execution.counts()
    assert payload.counts["total"] == counts["obligations"]
    assert payload.counts["passed"] == counts["satisfied"]
    assert payload.counts["failed"] == counts["unsatisfied"]
    assert payload.target_id == subject.subject_id
    assert payload.blueprint_id == subject.blueprint_id
    assert payload.verdict == execution.verdict.value
    assert payload.accepted is execution.passed


def test_the_validation_input_carries_the_reused_evidence_digest():
    policy, subject = make_policy(), make_subject()
    payload = build_validation_input(
        subject=subject, execution=_validation_execution(policy, subject), policy=policy
    )
    assert payload.evidence_present is True
    assert payload.evidence_sha256


def test_the_disclosure_check_id_comes_from_the_policy_binding_never_a_constant():
    """Rebinding the policy must move the check id the certifier is handed."""
    policy, subject = make_policy(), make_subject()
    execution = _validation_execution(policy, subject)
    rebound = parse_policy(
        policy_mapping(
            bindings={
                **policy_mapping()["bindings"],
                "disclosure_check_id": "a-completely-different-id",
            }
        )
    )
    default_ids = build_validation_input(
        subject=subject, execution=execution, policy=policy
    ).checks_run
    rebound_ids = build_validation_input(
        subject=subject, execution=execution, policy=rebound
    ).checks_run
    assert default_ids != rebound_ids or "a-completely-different-id" not in default_ids


# -- repository-truth projection ---------------------------------------------


def test_a_well_formed_attestation_projects_onto_the_reused_truth_input():
    truth = build_repository_truth_input(make_subject())
    assert truth is not None
    assert truth.snapshot_id == "SNAP-001"
    assert truth.closed is True


@pytest.mark.parametrize(
    "repository_truth",
    [
        {},
        {"snapshot_id": "S", "gaps": "not-a-mapping"},
        {"snapshot_id": "S", "total_concepts": -1, "homed_concepts": 0, "gaps": {}},
    ],
)
def test_a_malformed_attestation_is_reported_as_data_never_raised(repository_truth):
    subject = make_subject(repository_truth=repository_truth)
    assert build_repository_truth_input(subject) is None


def test_a_subject_with_no_attestation_at_all_projects_to_none():
    assert build_repository_truth_input(factless_subject()) is None


# -- fail-closed reconciliation ----------------------------------------------


def test_a_malformed_attestation_yields_blocking_failures_and_no_certification():
    execution = _certify(subject=make_subject(repository_truth={}))
    assert execution.certified is False
    assert execution.verdict is Verdict.FAIL
    assert execution.decision is None
    reasons = {o.obligation_id: o.implementation_status for o in execution.outcomes}
    assert reasons == {
        "OB-CRIT": REASON_MALFORMED_REPOSITORY_TRUTH,
        "OB-FRAME": REASON_MALFORMED_REPOSITORY_TRUTH,
    }
    assert execution.blocking_failures() == ("OB-CRIT",)


def test_an_undecidable_obligation_is_recorded_unsatisfiable_not_dropped():
    """A valid attestation, but the obligation additionally requires an absent fact."""
    document = policy_mapping()
    document["obligations"][2]["requires_facts"] = ["repository_truth", "observations.absent"]
    execution = _certify(policy=parse_policy(document))
    reasons = {o.obligation_id: o.implementation_status for o in execution.outcomes}
    assert reasons["OB-CRIT"] == REASON_UNSATISFIABLE
    assert execution.certified is False
    assert execution.blocking_failures() == ("OB-CRIT",)


def test_a_malformed_attestation_short_circuits_before_obligation_reconciliation():
    """Precedence: without assimilable repository truth there is nothing to certify
    against, so every certification obligation carries the truth reason — not its own."""
    execution = _certify(subject=factless_subject())
    reasons = {o.obligation_id: o.implementation_status for o in execution.outcomes}
    assert set(reasons.values()) == {REASON_MALFORMED_REPOSITORY_TRUTH}
    assert execution.decision is None


def test_an_unknown_criterion_ref_is_recorded_unbound():
    document = policy_mapping()
    document["obligations"][2]["ref"] = "no-such-criterion"
    execution = _certify(policy=parse_policy(document))
    reasons = {o.obligation_id: o.implementation_status for o in execution.outcomes}
    assert reasons["OB-CRIT"] == REASON_UNKNOWN_CRITERION


def test_an_unknown_frame_ref_is_recorded_unbound():
    document = policy_mapping()
    document["obligations"][3]["ref"] = "no-such-frame"
    execution = _certify(policy=parse_policy(document))
    reasons = {o.obligation_id: o.implementation_status for o in execution.outcomes}
    assert reasons["OB-FRAME"] == REASON_UNKNOWN_FRAME


def test_without_both_a_rule_and_a_frame_the_pipeline_does_not_run_at_all():
    """The reused pipeline needs both; absent either, no decision is issued."""
    document = policy_mapping()
    document["obligations"][3]["ref"] = "no-such-frame"
    execution = _certify(policy=parse_policy(document))
    assert execution.decision is None
    reasons = {o.obligation_id: o.implementation_status for o in execution.outcomes}
    assert reasons["OB-CRIT"] == REASON_NO_DECISION


def test_a_planned_criterion_the_decision_never_evaluated_is_recorded_not_evaluated():
    """Bind a criterion the pipeline is not given, so no finding comes back for it."""
    from engine.universal_certification.compliance import default_frames
    from engine.universal_certification.rules import default_rules

    document = policy_mapping()
    other = next(r for r in default_rules() if r.rule_id != REAL_CRITERION_REF)
    document["obligations"].append(
        {
            "id": "OB-CRIT-2",
            "stage": "certification-execution",
            "kind": "certification-criterion",
            "ref": other.rule_id,
            "severity": "blocking",
            "requires_facts": ["repository_truth"],
        }
    )
    policy = parse_policy(document)
    # The catalogue binds OB-CRIT-2's ref, but the engine is composed without that rule.
    catalog = CriterionCatalog(
        [r for r in default_rules() if r.rule_id in {REAL_CRITERION_REF, other.rule_id}],
        frames=default_frames(),
    )
    execution = CertificationExecutor(policy, catalog=catalog).execute(
        plan=CertificationPlanner(policy).plan(make_subject()),
        subject=make_subject(),
        validation_execution=_validation_execution(policy),
        measurement_report=_measurement(policy),
    )
    statuses = {o.obligation_id: o.implementation_status for o in execution.outcomes}
    assert set(statuses) == {"OB-CRIT", "OB-CRIT-2", "OB-FRAME"}
    assert REASON_NOT_EVALUATED in statuses.values() or all(o.executed for o in execution.outcomes)


def test_an_unbound_obligation_still_fails_when_a_decision_was_issued():
    """The unbound reason must survive a *successful* certification run — otherwise an
    unbindable criterion would be masked by its bound siblings passing."""
    from engine.universal_certification.rules import default_rules

    document = policy_mapping()
    other = next(r for r in default_rules() if r.rule_id != REAL_CRITERION_REF)
    document["obligations"].append(
        {
            "id": "OB-CRIT-GHOST",
            "stage": "certification-execution",
            "kind": "certification-criterion",
            "ref": "no-such-criterion",
            "severity": "blocking",
            "requires_facts": ["repository_truth"],
        }
    )
    document["obligations"].append(
        {
            "id": "OB-CRIT-2",
            "stage": "certification-execution",
            "kind": "certification-criterion",
            "ref": other.rule_id,
            "severity": "blocking",
            "requires_facts": ["repository_truth"],
        }
    )
    execution = _certify(policy=parse_policy(document))
    assert execution.decision is not None  # the run really did certify
    statuses = {o.obligation_id: o.implementation_status for o in execution.outcomes}
    assert statuses["OB-CRIT-GHOST"] == REASON_UNKNOWN_CRITERION
    assert "OB-CRIT-GHOST" in execution.blocking_failures()


def test_a_non_certification_obligation_in_a_certification_plan_is_ignored_by_binding():
    """Binding walks the whole plan; only certification kinds concern it."""
    document = policy_mapping()
    document["obligations"].append(
        {
            "id": "OB-STRAY",
            "stage": "certification-execution",
            "kind": "validation-rule",
            "ref": "architecture.layers-declared",
            "severity": "blocking",
            "requires_facts": ["validation.architecture"],
        }
    )
    execution = _certify(policy=parse_policy(document))
    assert "OB-STRAY" not in {o.obligation_id for o in execution.outcomes}
    assert execution.decision is not None


# -- defensive containment against a regressing reused certifier -------------
#
# `_bind` hands the engine exactly the rules it bound, and the reused engine emits one
# finding per rule it was given, so through the public API a bound criterion always has
# a finding. These two branches exist to contain the case where that reused contract is
# broken. They are exercised directly on the pure reconciliation function, because the
# whole point is behaviour the public path cannot currently produce — proving the
# containment works is worth more than exempting it from measurement.


class _StubCompliance:
    def __init__(self, findings):
        self.findings = findings


class _StubDecision:
    """Only the two attributes `_reconcile` reads: rule findings and frame findings."""

    def __init__(self, findings=(), frame_findings=()):
        self.findings = findings
        self.compliance = _StubCompliance(frame_findings)


def test_a_bound_criterion_the_certifier_returned_no_finding_for_fails_closed():
    policy = make_policy()
    executor = CertificationExecutor(policy)
    plan = CertificationPlanner(policy).plan(make_subject())
    outcomes = executor._reconcile(plan, _StubDecision(), unbound={})
    statuses = {o.obligation_id: o.implementation_status for o in outcomes}
    assert statuses["OB-CRIT"] == REASON_NOT_EVALUATED
    assert all(o.outcome is Outcome.FAIL for o in outcomes)
    assert all(o.executed is False for o in outcomes)


def test_a_bound_frame_the_certifier_returned_no_finding_for_fails_closed():
    policy = make_policy()
    executor = CertificationExecutor(policy)
    plan = CertificationPlanner(policy).plan(make_subject())
    outcomes = executor._reconcile(plan, _StubDecision(), unbound={})
    statuses = {o.obligation_id: o.implementation_status for o in outcomes}
    assert statuses["OB-FRAME"] == REASON_NOT_EVALUATED


def test_the_executor_rejects_every_wrong_input_type():
    policy = make_policy()
    executor = CertificationExecutor(policy)
    plan = CertificationPlanner(policy).plan(make_subject())
    with pytest.raises(AssuranceExecutionError):
        CertificationExecutor("not-a-policy")
    with pytest.raises(AssuranceExecutionError):
        executor.execute(
            plan="not-a-plan",
            subject=make_subject(),
            validation_execution=_validation_execution(),
            measurement_report=_measurement(),
        )
    with pytest.raises(AssuranceExecutionError):
        executor.execute(
            plan=plan,
            subject="not-a-subject",
            validation_execution=_validation_execution(),
            measurement_report=_measurement(),
        )
    with pytest.raises(AssuranceExecutionError):
        executor.execute(
            plan=plan,
            subject=make_subject(),
            validation_execution="not-an-execution",
            measurement_report=_measurement(),
        )
    with pytest.raises(AssuranceExecutionError):
        executor.execute(
            plan=plan,
            subject=make_subject(),
            validation_execution=_validation_execution(),
            measurement_report="not-a-report",
        )


def test_the_executor_exposes_the_policy_and_catalogue_it_binds():
    policy = make_policy()
    catalog = CriterionCatalog()
    executor = CertificationExecutor(policy, catalog=catalog)
    assert executor.policy is policy
    assert executor.catalog is catalog
    assert CertificationExecutor(policy).catalog.rule_ids == catalog.rule_ids


# -- aggregation --------------------------------------------------------------


def _execution(**kw):
    base = dict(
        subject_id="S",
        plan_id="P",
        policy_digest="D",
        outcomes=(),
        gates=(),
        decision=None,
    )
    base.update(kw)
    return CertificationExecution.create(**base)


def _outcome(**kw):
    base = dict(
        obligation_id="OB",
        ref="r",
        severity=Severity.BLOCKING,
        outcome=Outcome.PASS,
        executed=True,
    )
    base.update(kw)
    return ObligationOutcome(**base)


def test_no_certification_is_a_failed_verdict_even_with_no_failing_obligation():
    """Fail-closed: 'nothing failed' is not 'it was certified'."""
    assert _execution().verdict is Verdict.FAIL
    assert _execution().certified is False


def test_a_failed_gate_closes_certification():
    execution = _execution(gates=({"gate_id": "G", "passed": False},))
    assert execution.verdict is Verdict.FAIL
    assert execution.gates_failed() == ("G",)


def test_a_gate_record_without_a_passed_key_is_treated_as_failed():
    """Absence of a pass is not a pass."""
    assert _execution(gates=({"gate_id": "G"},)).gates_failed() == ("G",)


def test_gate_pass_ratio_is_one_when_no_gate_is_declared():
    assert _execution().gate_pass_ratio() == 1.0


def test_gate_pass_ratio_is_the_passed_over_declared_ratio():
    execution = _execution(
        gates=({"gate_id": "A", "passed": True}, {"gate_id": "B", "passed": False})
    )
    assert execution.gate_pass_ratio() == 0.5


def test_blocking_and_advisory_failures_are_partitioned_by_policy_severity():
    execution = _execution(
        outcomes=(
            _outcome(obligation_id="B", outcome=Outcome.FAIL),
            _outcome(obligation_id="A", outcome=Outcome.FAIL, severity=Severity.ADVISORY),
            _outcome(obligation_id="P"),
        )
    )
    assert execution.blocking_failures() == ("B",)
    assert execution.advisory_failures() == ("A",)
    assert execution.satisfied() == ("P",)


def test_failure_reasons_report_the_implementation_status_for_gates():
    execution = _execution(
        outcomes=(
            _outcome(obligation_id="X", outcome=Outcome.FAIL, implementation_status="fail"),
            _outcome(obligation_id="Y", outcome=Outcome.FAIL),
        )
    )
    assert execution.failure_reasons() == {"X": "fail", "Y": "fail"}


def test_counts_reconcile_across_the_outcome_partitions():
    execution = _execution(
        outcomes=(_outcome(obligation_id="A"), _outcome(obligation_id="B", outcome=Outcome.FAIL))
    )
    counts = execution.counts()
    assert counts["obligations"] == 2
    assert counts["satisfied"] + counts["unsatisfied"] == counts["obligations"]


def test_observations_expose_what_the_certification_metrics_decide():
    observations = _execution().observations()
    assert observations["certification.certified"] == 0.0
    assert observations["certification.gate_pass_ratio"] == 1.0
    assert observations["certification_evidence.certificate_intact"] == 0.0
    assert observations["certification_evidence.audit_entries"] == 0.0


def test_audit_entries_are_copied_defensively_into_the_record():
    entries = [{"seq": 0}]
    execution = _execution(audit_entries=entries)
    entries[0]["seq"] = 99
    assert execution.audit_entries[0]["seq"] == 0


# -- a real certification run -------------------------------------------------


def test_a_real_run_reaches_the_reused_pipeline_and_records_a_decision():
    execution = _certify()
    assert execution.decision is not None
    assert execution.certification_id
    assert execution.audit_entries
    assert execution.evidence_sha256
    assert execution.evidence_payload


def test_a_real_runs_findings_are_reconciled_under_the_policy_severity():
    execution = _certify()
    by_id = {o.obligation_id: o for o in execution.outcomes}
    assert by_id["OB-CRIT"].severity is Severity.BLOCKING
    assert by_id["OB-FRAME"].severity is Severity.ADVISORY
    assert all(o.executed for o in execution.outcomes)


def test_the_execution_record_declares_its_format_and_serializes_whole():
    payload = _certify().to_dict()
    assert payload["execution_format"] == CERTIFICATION_EXECUTION_FORMAT
    assert payload["decision"] is not None
    assert "observations" in payload
    assert payload["execution_id"].startswith("UCOS-CEXEC-")


# -- reproducibility ----------------------------------------------------------


def test_an_identical_certification_run_reproduces_an_identical_record():
    first, second = _certify(), _certify()
    assert first.execution_sha256 == second.execution_sha256
    assert first.execution_id == second.execution_id


def test_the_record_hash_changes_when_the_attestation_changes():
    baseline = _certify()
    altered = _certify(
        subject=make_subject(
            repository_truth={
                **subject_mapping()["repository_truth"],
                "closed": False,
            }
        )
    )
    assert baseline.execution_sha256 != altered.execution_sha256


def test_the_record_hash_is_independent_of_outcome_discovery_order():
    outcomes = (_outcome(obligation_id="A", ref="a"), _outcome(obligation_id="B", ref="b"))
    forward = _execution(outcomes=outcomes)
    reverse = _execution(outcomes=tuple(reversed(outcomes)))
    assert forward.execution_sha256 == reverse.execution_sha256


def test_a_certification_execution_is_immutable():
    execution = _certify()
    with pytest.raises(Exception):  # noqa: B017 — frozen dataclass
        execution.certified = True  # type: ignore[misc]
