"""UCOS-EPIC-014 — Validation Generation tests.

Generation's claim is that "nothing is generated *ex nihilo*": it never writes a rule
implementation, it resolves declared refs against the reused catalogue. These tests hold
it to that — the catalogue is proven to be the reused platform suite, an unresolvable ref
is proven to be *recorded* rather than raised, and the severity-divergence rule ("at
execution time the policy severity governs") is exercised against a real reused rule whose
shipped severity genuinely disagrees with the policy's.
"""

from __future__ import annotations

from platform.universal_assurance.contracts import ObligationKind, Severity
from platform.universal_assurance.errors import AssuranceGenerationError
from platform.universal_assurance.generation import (
    SUITE_FORMAT,
    UNBOUND_UNKNOWN_DIMENSION,
    UNBOUND_UNKNOWN_RULE,
    UNBOUND_UNSATISFIABLE,
    GeneratedCheck,
    GeneratedSuite,
    RuleCatalog,
    SuiteGenerator,
    obligations_by_ref,
)
from platform.universal_assurance.planning import CertificationPlanner, ValidationPlanner
from platform.universal_assurance.policy import parse_policy
from platform.universal_validation.rules import default_rules

import pytest

from .universal_assurance_helpers import (
    REAL_ADVISORY_RULE_REF,
    REAL_DIMENSION_REF,
    REAL_RULE_REF,
    factless_subject,
    make_policy,
    make_subject,
    policy_mapping,
)


def _generate(policy=None, subject=None):
    policy = policy if policy is not None else make_policy()
    subject = subject if subject is not None else make_subject()
    return SuiteGenerator().generate(ValidationPlanner(policy).plan(subject))


# -- the catalogue is the reused platform, not a local copy -------------------


def test_the_default_catalogue_is_exactly_the_reused_validation_suite():
    catalog = RuleCatalog()
    assert catalog.rule_ids == tuple(sorted(r.rule_id for r in default_rules()))
    assert catalog.rule(REAL_RULE_REF) is not None


def test_the_default_dimension_set_is_the_reused_intelligence_vocabulary():
    from platform.validation_intelligence.contracts import IntelligenceDimension

    catalog = RuleCatalog()
    assert catalog.dimension_ids == tuple(sorted(d.value for d in IntelligenceDimension))
    assert catalog.dimension(REAL_DIMENSION_REF) is not None


def test_the_catalogue_returns_none_rather_than_raising_on_an_unknown_ref():
    catalog = RuleCatalog()
    assert catalog.rule("no.such.rule") is None
    assert catalog.dimension("no_such_dimension") is None


def test_a_catalogue_can_be_narrowed_to_an_explicit_rule_and_dimension_set():
    from platform.validation_intelligence.contracts import IntelligenceDimension

    only = [r for r in default_rules() if r.rule_id == REAL_RULE_REF]
    catalog = RuleCatalog(only, dimensions=[IntelligenceDimension.ARCHITECTURE_COMPLIANCE])
    assert catalog.rule_ids == (REAL_RULE_REF,)
    assert catalog.dimension_ids == (REAL_DIMENSION_REF,)


def test_a_catalogue_entry_without_a_rule_id_is_an_authoring_fault():
    class Nameless:
        pass

    with pytest.raises(AssuranceGenerationError) as exc:
        RuleCatalog([Nameless()])
    assert "no rule_id" in str(exc.value)


def test_a_duplicate_rule_id_in_the_catalogue_is_rejected():
    rule = next(r for r in default_rules() if r.rule_id == REAL_RULE_REF)
    with pytest.raises(AssuranceGenerationError) as exc:
        RuleCatalog([rule, rule])
    assert "duplicate" in str(exc.value)


def test_catalogue_serializes_both_indexes():
    payload = RuleCatalog().to_dict()
    assert REAL_RULE_REF in payload["rules"]
    assert REAL_DIMENSION_REF in payload["dimensions"]


# -- binding ------------------------------------------------------------------


def test_a_planned_obligation_binds_to_the_reused_implementation():
    suite = _generate()
    check = next(c for c in suite.checks if c.obligation_id == "OB-RULE")
    assert check.bound is True
    assert check.ref == REAL_RULE_REF
    assert check.domain == "architecture"
    assert "platform.universal_validation" in check.implementation
    assert check.unbound_reason == ""


def test_a_dimension_obligation_binds_to_the_reused_analyzer_suite():
    suite = _generate()
    check = next(c for c in suite.checks if c.obligation_id == "OB-DIM")
    assert check.bound is True
    assert check.dimension == REAL_DIMENSION_REF
    assert check.implementation == "platform.validation_intelligence.analyzers"


def test_an_unknown_rule_ref_is_recorded_unbound_and_never_raised():
    document = policy_mapping()
    document["obligations"][0]["ref"] = "no.such.rule"
    suite = _generate(policy=parse_policy(document))
    check = next(c for c in suite.checks if c.obligation_id == "OB-RULE")
    assert check.bound is False
    assert check.unbound_reason == UNBOUND_UNKNOWN_RULE
    assert check.is_blocking_shortfall is True
    assert suite.complete is False


def test_an_unknown_dimension_ref_is_recorded_unbound_and_never_raised():
    document = policy_mapping()
    document["obligations"][1]["ref"] = "no_such_dimension"
    document["obligations"][1]["requires_facts"] = []
    suite = _generate(policy=parse_policy(document))
    check = next(c for c in suite.checks if c.obligation_id == "OB-DIM")
    assert check.bound is False
    assert check.unbound_reason == UNBOUND_UNKNOWN_DIMENSION


def test_an_undecidable_obligation_is_not_even_attempted_against_the_catalogue():
    """Planning already proved the facts are absent; binding must not paper over it."""
    suite = _generate(subject=factless_subject())
    reasons = {c.obligation_id: c.unbound_reason for c in suite.checks}
    assert reasons == {
        "OB-RULE": UNBOUND_UNSATISFIABLE,
        "OB-DIM": UNBOUND_UNSATISFIABLE,
    }
    assert suite.blocking_shortfalls() == ("OB-RULE", "OB-DIM")


def test_certification_obligations_are_not_bound_by_the_validation_generator():
    """They belong to the certification executor; generation must leave them alone."""
    plan = CertificationPlanner(make_policy()).plan(make_subject())
    suite = SuiteGenerator().generate(plan)
    assert suite.checks == ()
    assert suite.rules == ()
    assert suite.complete is True


def test_the_generator_rejects_anything_that_is_not_a_plan():
    with pytest.raises(AssuranceGenerationError):
        SuiteGenerator().generate("not-a-plan")


def test_a_generator_exposes_the_catalogue_it_was_composed_with():
    catalog = RuleCatalog()
    assert SuiteGenerator(catalog).catalog is catalog
    assert SuiteGenerator().catalog.rule_ids == catalog.rule_ids


# -- policy severity governs --------------------------------------------------


def test_a_divergence_between_policy_and_implementation_severity_is_recorded():
    """The reused rule ships advisory; the policy declares it blocking."""
    document = policy_mapping()
    document["obligations"][0]["ref"] = REAL_ADVISORY_RULE_REF
    document["obligations"][0]["requires_facts"] = ["validation.architecture"]
    suite = _generate(policy=parse_policy(document))
    check = next(c for c in suite.checks if c.obligation_id == "OB-RULE")
    assert check.implementation_severity == "advisory"
    assert check.policy_severity is Severity.BLOCKING
    assert check.severity_diverges is True
    assert suite.severity_divergences() == ("OB-RULE",)


def test_agreeing_severities_are_not_reported_as_divergence():
    suite = _generate()
    check = next(c for c in suite.checks if c.obligation_id == "OB-RULE")
    assert check.implementation_severity == "blocking"
    assert check.severity_diverges is False
    assert suite.severity_divergences() == ()


def test_an_unbound_check_has_no_implementation_severity_to_diverge_from():
    check = GeneratedCheck(
        obligation_id="X",
        kind=ObligationKind.VALIDATION_RULE,
        ref="r",
        policy_severity=Severity.BLOCKING,
        bound=False,
    )
    assert check.severity_diverges is False


def test_the_suite_reports_the_policy_severity_for_a_ref_not_the_implementations():
    document = policy_mapping()
    document["obligations"][0]["ref"] = REAL_ADVISORY_RULE_REF
    suite = _generate(policy=parse_policy(document))
    assert suite.severity_for(REAL_ADVISORY_RULE_REF) is Severity.BLOCKING
    assert suite.severity_for("no.such.ref") is None


def test_an_advisory_obligation_that_cannot_bind_is_an_advisory_shortfall():
    document = policy_mapping()
    document["obligations"][0]["severity"] = "advisory"
    document["obligations"][0]["ref"] = "no.such.rule"
    suite = _generate(policy=parse_policy(document))
    assert suite.advisory_shortfalls() == ("OB-RULE",)
    assert suite.blocking_shortfalls() == ()
    assert suite.complete is True


# -- suite shape and measurability -------------------------------------------


def test_the_suite_collects_the_distinct_rules_and_dimensions_it_bound():
    suite = _generate()
    assert suite.rule_ids() == (REAL_RULE_REF,)
    assert [d.value for d in suite.dimensions] == [REAL_DIMENSION_REF]
    assert [d.value for d in suite.domains()] == ["architecture"]


def test_binding_coverage_is_one_when_the_plan_admitted_nothing():
    plan = CertificationPlanner(make_policy()).plan(make_subject())
    assert SuiteGenerator().generate(plan).binding_coverage() == 1.0


def test_binding_coverage_is_the_bound_over_planned_ratio():
    document = policy_mapping()
    document["obligations"][0]["ref"] = "no.such.rule"
    suite = _generate(policy=parse_policy(document))
    assert suite.binding_coverage() == 0.5
    assert len(suite.bound_checks) == 1
    assert len(suite.unbound_checks) == 1


def test_suite_observations_expose_what_the_generation_metrics_decide():
    observations = _generate().observations()
    assert observations["suite.checks"] == 2.0
    assert observations["suite.bound_obligations"] == 2.0
    assert observations["suite.unbound_obligations"] == 0.0
    assert observations["suite.binding_coverage"] == 1.0
    assert observations["suite.severity_divergences"] == 0.0


def test_suite_counts_reconcile_with_its_check_partitions():
    suite = _generate()
    counts = suite.counts()
    assert counts["bound"] + counts["unbound"] == counts["checks"]


def test_obligations_for_a_ref_are_indexed_deterministically():
    document = policy_mapping()
    document["obligations"].append(
        {
            "id": "OB-RULE-2",
            "stage": "validation-execution",
            "kind": "validation-rule",
            "ref": REAL_RULE_REF,
            "severity": "blocking",
            "requires_facts": ["validation.architecture"],
        }
    )
    suite = _generate(policy=parse_policy(document))
    assert suite.obligations_for_ref(REAL_RULE_REF) == ("OB-RULE", "OB-RULE-2")
    index = obligations_by_ref(suite)
    assert index[REAL_RULE_REF] == ("OB-RULE", "OB-RULE-2")
    assert list(index) == sorted(index)


# -- reproducibility ----------------------------------------------------------


def test_an_identical_plan_reproduces_an_identical_suite():
    first, second = _generate(), _generate()
    assert first.suite_sha256 == second.suite_sha256
    assert first.suite_id == second.suite_id
    assert first.to_dict() == second.to_dict()


def test_the_suite_hash_changes_when_a_ref_stops_binding():
    document = policy_mapping()
    document["obligations"][0]["ref"] = "no.such.rule"
    assert _generate().suite_sha256 != _generate(policy=parse_policy(document)).suite_sha256


def test_the_suite_hash_is_independent_of_check_discovery_order():
    """create() sorts canonically, so a shuffled input must hash identically."""
    suite = _generate()
    shuffled = GeneratedSuite.create(
        plan=ValidationPlanner(make_policy()).plan(make_subject()),
        checks=list(reversed(suite.checks)),
        rules=suite.rules,
        dimensions=suite.dimensions,
        catalog_rule_ids=suite.catalog_rule_ids,
    )
    assert shuffled.suite_sha256 == suite.suite_sha256


def test_the_suite_anchors_itself_to_the_plan_and_policy_that_produced_it():
    plan = ValidationPlanner(make_policy()).plan(make_subject())
    suite = SuiteGenerator().generate(plan)
    assert suite.plan_id == plan.plan_id
    assert suite.plan_sha256 == plan.plan_sha256
    assert suite.policy_digest == plan.policy_digest
    assert suite.suite_id.startswith("UCOS-VSUITE-")
    assert suite.to_dict()["suite_format"] == SUITE_FORMAT


def test_the_suite_records_the_catalogue_it_was_generated_against():
    suite = _generate()
    assert REAL_RULE_REF in suite.catalog_rule_ids


def test_a_generated_check_core_excludes_the_derived_divergence_flag():
    check = _generate().checks[0]
    assert "severity_diverges" not in check.core()
    assert "severity_diverges" in check.to_dict()


def test_a_suite_is_immutable():
    suite = _generate()
    with pytest.raises(Exception):  # noqa: B017 — frozen dataclass
        suite.suite_id = "x"  # type: ignore[misc]
