"""UCOS-EPIC-014 — Validation Execution runtime tests (runtime-facing scope).

`execution.py` contributes no rule runtime of its own; what it adds is the *policy
binding* over the reused engine's results. So these tests target the binding, not the
rules: an obligation whose rule never ran must be a fail-closed failure rather than a
pass, and where the shipped rule's severity and the policy's severity disagree, the
policy must win in both directions.

Runtime scope only: this file exercises `ValidationExecutor` and the `ValidationExecution`
record. Rule correctness belongs to `platform.universal_validation`, and plan/suite
semantics belong to another session — both are used here, neither is asserted about.
"""

from __future__ import annotations

from platform.universal_assurance.contracts import AssuranceSubject, Outcome, Severity, Verdict
from platform.universal_assurance.errors import AssuranceExecutionError
from platform.universal_assurance.execution import (
    EXECUTION_FORMAT,
    REASON_NO_SUITE,
    REASON_NOT_EXECUTED,
    REASON_UNBOUND,
    ObligationOutcome,
    ValidationExecution,
    ValidationExecutor,
)
from platform.universal_assurance.generation import SuiteGenerator
from platform.universal_assurance.planning import ValidationPlanner
from platform.universal_assurance.policy import parse_policy
from platform.universal_validation.contracts import (
    RuleResult,
    RuleSeverity,
    RuleStatus,
    ValidationDomain,
)
from typing import Any

import pytest

from .universal_assurance_helpers import (
    REAL_ADVISORY_RULE_REF,
    REAL_RULE_REF,
    make_subject,
    policy_mapping,
    subject_mapping,
)

#: A rule ref the reused validation catalogue does not ship — it can never bind.
GHOST_RULE_REF = "architecture.no-such-rule-exists"


def _rule_policy(*obligations: dict[str, Any]):
    """A policy whose only obligations are the validation rules under test."""
    return parse_policy(policy_mapping(obligations=list(obligations), gates=[], metrics=[]))


def _obligation(obligation_id: str, ref: str, severity: str = "blocking") -> dict[str, Any]:
    return {
        "id": obligation_id,
        "stage": "validation-execution",
        "kind": "validation-rule",
        "ref": ref,
        "severity": severity,
        "requires_facts": ["validation.architecture"],
    }


def _execute(policy, subject) -> ValidationExecution:
    """Drive the real planning → generation → execution path."""
    suite = SuiteGenerator().generate(ValidationPlanner(policy).plan(subject))
    return ValidationExecutor().execute(suite, subject)


def _architecture_subject(**facts: Any) -> AssuranceSubject:
    """A subject whose architecture facts are supplied (so the rule can decide)."""
    validation_facts = {
        "architecture": {
            "layers": ["platform", "engine"],
            "dependencies": [{"from": "platform", "to": "engine"}],
            **facts,
        }
    }
    return AssuranceSubject.from_mapping(subject_mapping(validation_facts=validation_facts))


# -- guard rails -------------------------------------------------------------


def test_execution_requires_a_generated_suite():
    with pytest.raises(AssuranceExecutionError):
        ValidationExecutor().execute("not-a-suite", make_subject())


def test_execution_requires_an_assurance_subject():
    policy = _rule_policy(_obligation("OB-REAL", REAL_RULE_REF))
    suite = SuiteGenerator().generate(ValidationPlanner(policy).plan(make_subject()))

    with pytest.raises(AssuranceExecutionError):
        ValidationExecutor().execute(suite, {"subject_id": "not-a-subject"})


# -- fail-closed reconciliation ----------------------------------------------


def test_an_obligation_whose_rule_does_not_exist_fails_closed_as_unbound():
    execution = _execute(
        _rule_policy(_obligation("OB-GHOST", GHOST_RULE_REF)), _architecture_subject()
    )

    outcome = execution.outcomes[0]
    assert outcome.executed is False
    assert outcome.outcome is Outcome.FAIL
    assert outcome.implementation_status == "unknown-validation-rule"
    assert execution.not_executed() == ("OB-GHOST",)
    assert execution.verdict is Verdict.FAIL


def test_an_unbound_obligation_is_never_counted_as_satisfied():
    execution = _execute(
        _rule_policy(
            _obligation("OB-REAL", REAL_RULE_REF),
            _obligation("OB-GHOST", GHOST_RULE_REF),
        ),
        _architecture_subject(),
    )

    assert "OB-GHOST" not in execution.satisfied()
    assert "OB-GHOST" in execution.blocking_failures()
    assert execution.obligation_coverage() == 0.5


def test_the_verdict_is_governed_by_policy_severity_not_the_shipped_rule():
    # `implementation.no-open-markers` is advisory in the reused catalogue; the policy
    # declares it blocking, so a failure must close the run.
    subject = AssuranceSubject.from_mapping(
        subject_mapping(
            validation_facts={
                "architecture": {"layers": ["platform"], "dependencies": []},
                "implementation": {
                    "modules": [{"id": "m", "present": True}],
                    "markers": ["TODO: unfinished"],
                },
            }
        )
    )
    obligation = _obligation("OB-ADV", REAL_ADVISORY_RULE_REF, severity="blocking")
    obligation["requires_facts"] = ["validation.implementation"]

    execution = _execute(_rule_policy(obligation), subject)

    outcome = execution.outcomes[0]
    assert outcome.executed is True
    assert outcome.severity is Severity.BLOCKING
    assert outcome.severity_escalated is True
    assert execution.verdict is Verdict.FAIL


def test_an_advisory_failure_does_not_close_the_run():
    outcome = ObligationOutcome.unmet(
        _Check("OB-A", "some.ref", Severity.ADVISORY), reason=REASON_UNBOUND
    )
    execution = ValidationExecution.create(
        subject_id="S",
        plan_id="P",
        suite_id="SU",
        policy_digest="d",
        outcomes=[outcome],
        report=None,
    )

    assert execution.advisory_failures() == ("OB-A",)
    assert execution.blocking_failures() == ()
    assert execution.verdict is Verdict.PASS


class _Check:
    """The minimal GeneratedCheck surface `ObligationOutcome` reads."""

    def __init__(self, obligation_id: str, ref: str, severity: Severity, reason: str = "") -> None:
        self.obligation_id = obligation_id
        self.ref = ref
        self.policy_severity = severity
        self.unbound_reason = reason


def test_reasons_distinguish_no_suite_from_a_rule_that_simply_did_not_run():
    check = _Check("OB-A", "some.ref", Severity.BLOCKING)

    no_suite = ObligationOutcome.unmet(check, reason=REASON_NO_SUITE)
    not_executed = ObligationOutcome.unmet(check, reason=REASON_NOT_EXECUTED)

    assert no_suite.implementation_status == REASON_NO_SUITE
    assert not_executed.implementation_status == REASON_NOT_EXECUTED
    assert no_suite.passed is False and not_executed.passed is False


def test_an_outcome_reconciled_from_a_result_adopts_the_policy_severity():
    check = _Check("OB-A", "some.ref", Severity.BLOCKING)
    result = RuleResult(
        rule_id="some.ref",
        domain=ValidationDomain.ARCHITECTURE,
        severity=RuleSeverity.BLOCKING,
        status=RuleStatus.FAIL,
        message="nope",
        details={"k": "v"},
    )

    outcome = ObligationOutcome.from_result(check, result, severity=Severity.ADVISORY)

    assert outcome.severity is Severity.ADVISORY
    assert outcome.is_advisory_failure is True
    assert outcome.is_blocking_failure is False
    assert outcome.severity_escalated is False
    assert outcome.details == {"k": "v"}
    assert outcome.to_dict()["details"] == {"k": "v"}
    assert "details" not in outcome.core()


# -- the execution record ----------------------------------------------------


def test_an_empty_execution_is_vacuously_covered_and_passes():
    execution = ValidationExecution.create(
        subject_id="S", plan_id="P", suite_id="SU", policy_digest="d", outcomes=[], report=None
    )

    assert execution.obligation_coverage() == 1.0
    assert execution.verdict is Verdict.PASS
    assert execution.passed is True
    assert execution.evidence() is None
    assert execution.report_sha256 == ""


def test_the_execution_hash_is_reproducible_across_independent_runs():
    policy = _rule_policy(_obligation("OB-REAL", REAL_RULE_REF))
    subject = _architecture_subject()

    first = _execute(policy, subject)
    second = _execute(policy, subject)

    assert first.execution_sha256 == second.execution_sha256
    assert first.execution_id == second.execution_id
    assert first.execution_id.startswith("UCOS-VEXEC-")


def test_the_execution_hash_is_independent_of_the_order_outcomes_arrive():
    checks = [
        _Check("OB-B", "ref.b", Severity.BLOCKING),
        _Check("OB-A", "ref.a", Severity.BLOCKING),
    ]
    outcomes = [ObligationOutcome.unmet(c, reason=REASON_UNBOUND) for c in checks]

    forward = ValidationExecution.create(
        subject_id="S",
        plan_id="P",
        suite_id="SU",
        policy_digest="d",
        outcomes=outcomes,
        report=None,
    )
    backward = ValidationExecution.create(
        subject_id="S",
        plan_id="P",
        suite_id="SU",
        policy_digest="d",
        outcomes=list(reversed(outcomes)),
        report=None,
    )

    assert forward.execution_sha256 == backward.execution_sha256
    assert forward.failed_refs() == ("ref.a", "ref.b")


def test_counts_and_observations_are_consistent_with_the_outcomes():
    execution = _execute(
        _rule_policy(
            _obligation("OB-REAL", REAL_RULE_REF),
            _obligation("OB-GHOST", GHOST_RULE_REF),
        ),
        _architecture_subject(),
    )

    counts = execution.counts()
    observations = execution.observations()

    assert counts["obligations"] == 2
    assert counts["satisfied"] + counts["unsatisfied"] == counts["obligations"]
    assert counts["executed"] + counts["not_executed"] == counts["obligations"]
    assert observations["execution.obligations"] == float(counts["obligations"])
    assert observations["execution.obligation_coverage"] == execution.obligation_coverage()
    assert observations["execution.blocking_failures"] == float(counts["blocking_failed"])


def test_failure_reasons_name_every_unmet_obligation():
    execution = _execute(
        _rule_policy(
            _obligation("OB-REAL", REAL_RULE_REF),
            _obligation("OB-GHOST", GHOST_RULE_REF),
        ),
        _architecture_subject(),
    )

    reasons = execution.failure_reasons()

    assert "OB-GHOST" in reasons
    assert "OB-REAL" not in reasons
    assert reasons["OB-GHOST"] == "unknown-validation-rule"


def test_a_real_run_produces_a_report_and_reusable_validation_evidence():
    execution = _execute(
        _rule_policy(_obligation("OB-REAL", REAL_RULE_REF)), _architecture_subject()
    )

    assert execution.report is not None
    assert execution.report_sha256 != ""
    assert execution.rules_executed == (REAL_RULE_REF,)
    assert execution.evidence() is not None
    assert execution.domain_verdicts


def test_the_serialized_record_declares_its_format_and_embeds_no_wall_clock():
    execution = _execute(
        _rule_policy(_obligation("OB-REAL", REAL_RULE_REF)), _architecture_subject()
    )

    payload = execution.to_dict()

    assert payload["execution_format"] == EXECUTION_FORMAT
    assert payload["execution_sha256"] == execution.execution_sha256
    assert payload["observations"] == execution.observations()
    assert "timestamp" not in payload


# -- the certifier hand-off --------------------------------------------------


def test_the_disclosure_check_id_is_added_only_when_its_rule_ran_and_passed():
    execution = ValidationExecution.create(
        subject_id="S",
        plan_id="P",
        suite_id="SU",
        policy_digest="d",
        outcomes=[],
        report=_StubReport(("runtime.disclosure-present",)),
    )

    checks = execution.checks_run(
        disclosure_rule="runtime.disclosure-present", disclosure_check_id="ec1-disclosure"
    )

    assert "ec1-disclosure" in checks
    assert checks == tuple(sorted(checks))


def test_the_disclosure_check_id_is_withheld_when_its_rule_failed():
    outcome = ObligationOutcome.unmet(
        _Check("OB-D", "runtime.disclosure-present", Severity.BLOCKING), reason=REASON_UNBOUND
    )
    execution = ValidationExecution.create(
        subject_id="S",
        plan_id="P",
        suite_id="SU",
        policy_digest="d",
        outcomes=[outcome],
        report=_StubReport(("runtime.disclosure-present",)),
    )

    checks = execution.checks_run(
        disclosure_rule="runtime.disclosure-present", disclosure_check_id="ec1-disclosure"
    )

    assert "ec1-disclosure" not in checks


class _StubReport:
    """A minimal report stand-in exposing only what `ValidationExecution` reads."""

    def __init__(self, rule_ids: tuple[str, ...]) -> None:
        self.all_results = tuple(
            RuleResult(
                rule_id=rule_id,
                domain=ValidationDomain.RUNTIME,
                severity=RuleSeverity.BLOCKING,
                status=RuleStatus.PASS,
                message="",
            )
            for rule_id in rule_ids
        )
        self.report_sha256 = "r" * 64

    def domain_verdicts(self) -> dict[str, str]:
        return {}


# -- the engine seam ---------------------------------------------------------


def test_the_engine_factory_is_a_seam_and_receives_exactly_the_generated_rules():
    policy = _rule_policy(_obligation("OB-REAL", REAL_RULE_REF))
    subject = _architecture_subject()
    suite = SuiteGenerator().generate(ValidationPlanner(policy).plan(subject))
    seen: list[tuple[str, ...]] = []

    def factory(rules):
        rules = tuple(rules)
        seen.append(tuple(rule.rule_id for rule in rules))
        from platform.universal_validation.engine import UniversalValidationEngine

        return UniversalValidationEngine(rules)

    ValidationExecutor(engine_factory=factory).execute(suite, subject)

    assert seen == [(REAL_RULE_REF,)]


def test_a_bound_rule_the_engine_silently_skipped_fails_closed_as_not_executed():
    """The headline claim: a rule that did not run is a failure, never a pass.

    The obligation binds, so the engine is built and a report comes back — but the report
    carries no result for that rule. Nothing downstream can tell the difference between
    "ran and passed" and "never ran" unless execution records the absence, so it must.
    """
    policy = _rule_policy(_obligation("OB-REAL", REAL_RULE_REF))
    subject = _architecture_subject()
    suite = SuiteGenerator().generate(ValidationPlanner(policy).plan(subject))
    assert suite.bound_checks, "the obligation must bind for this to test the right branch"

    class _SilentEngine:
        """An engine that returns a report omitting the rule it was asked to run."""

        def validate(self, target):
            return _StubReport(())

    execution = ValidationExecutor(engine_factory=lambda rules: _SilentEngine()).execute(
        suite, subject
    )

    outcome = execution.outcomes[0]
    assert outcome.executed is False
    assert outcome.outcome is Outcome.FAIL
    assert outcome.implementation_status == REASON_NOT_EXECUTED
    assert execution.not_executed() == ("OB-REAL",)
    assert execution.blocking_failures() == ("OB-REAL",)
    assert execution.blocking_failed_refs() == (REAL_RULE_REF,)
    assert execution.verdict is Verdict.FAIL
    assert execution.obligation_coverage() == 0.0


def test_a_suite_with_no_rules_never_touches_the_engine():
    policy = _rule_policy(_obligation("OB-GHOST", GHOST_RULE_REF))
    subject = _architecture_subject()
    suite = SuiteGenerator().generate(ValidationPlanner(policy).plan(subject))

    def exploding_factory(rules):
        raise AssertionError("the engine must not be built for an unbindable suite")

    execution = ValidationExecutor(engine_factory=exploding_factory).execute(suite, subject)

    assert execution.report is None
    assert execution.not_executed() == ("OB-GHOST",)
