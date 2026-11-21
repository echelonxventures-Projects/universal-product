"""UCOS-EPIC-005 — Universal Validation engine tests (Terminal T5)."""

from __future__ import annotations

from platform.tests.universal_validation_helpers import passing_facts, passing_target
from platform.universal_validation.contracts import (
    EngineVerdict,
    ValidationDomain,
    ValidationTarget,
)
from platform.universal_validation.engine import UniversalValidationEngine
from platform.universal_validation.errors import ValidationEngineError

import pytest


def test_full_suite_passes_on_good_target():
    report = UniversalValidationEngine().validate(passing_target())
    assert report.verdict is EngineVerdict.PASS
    assert report.counts()["domains"] == 7
    assert report.counts()["total"] == 21
    assert report.blocking_failures() == ()
    # domains reported in canonical order
    assert report.domains_run() == tuple(d.value for d in ValidationDomain)


def test_empty_target_fails_closed():
    report = UniversalValidationEngine().validate(ValidationTarget(target_id="T"))
    assert report.verdict is EngineVerdict.FAIL
    # every blocking rule fails when no evidence is supplied
    assert len(report.blocking_failures()) == 19  # 21 rules - 2 advisory
    assert report.counts()["advisory_failed"] == 2


def test_single_blocking_failure_fails_run():
    facts = passing_facts()
    facts["quality"]["tests"] = {"passed": 3, "failed": 1}
    report = UniversalValidationEngine().validate(ValidationTarget(target_id="T", facts=facts))
    assert report.verdict is EngineVerdict.FAIL
    assert "quality.tests-passing" in report.blocking_failures()
    # only the quality domain fails; others still pass
    assert report.domain_verdicts()["architecture"] == "pass"
    assert report.domain_verdicts()["quality"] == "fail"


def test_advisory_failure_does_not_fail_run():
    facts = passing_facts()
    facts["quality"]["lint_violations"] = 7
    report = UniversalValidationEngine().validate(ValidationTarget(target_id="T", facts=facts))
    assert report.verdict is EngineVerdict.PASS
    assert "quality.lint-clean" in report.advisory_failures()


def test_domain_scoping():
    engine = UniversalValidationEngine(domains=[ValidationDomain.QUALITY])
    report = engine.validate(passing_target())
    assert report.domains_run() == ("quality",)
    assert engine.domains == (ValidationDomain.QUALITY,)
    assert all(r.startswith("quality.") for r in engine.rule_ids)


def test_engine_rejects_empty_domain_selection():
    with pytest.raises(ValidationEngineError):
        UniversalValidationEngine(domains=[])


def test_engine_rejects_empty_rule_set():
    with pytest.raises(ValidationEngineError):
        UniversalValidationEngine(rules=[])


def test_engine_rejects_non_target():
    with pytest.raises(ValidationEngineError):
        UniversalValidationEngine().validate("not-a-target")  # type: ignore[arg-type]
