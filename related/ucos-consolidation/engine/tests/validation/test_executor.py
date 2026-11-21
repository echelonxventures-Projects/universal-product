"""TASK-000049 — Validation execution engine tests (TASK-000047)."""

from __future__ import annotations

import json

from engine.validation import (
    Severity,
    ValidationEngine,
    Verdict,
    validate_runtime_unit,
)
from engine.validation.checks import ProvenanceCheck

from .conftest import mutate


def test_engine_passes_on_valid_subject(valid_subject):
    report = ValidationEngine().validate(valid_subject)
    assert report.verdict is Verdict.PASS
    assert report.accepted is True
    assert report.blocking_failures == ()
    counts = report.counts()
    assert counts["total"] == 7
    assert counts["failed"] == 0


def test_engine_fails_on_blocking_failure(valid_subject):
    report = ValidationEngine().validate(mutate(valid_subject, provenance_chain=()))
    assert report.verdict is Verdict.FAIL
    assert report.accepted is False
    assert [f.check_id for f in report.blocking_failures] == ["provenance-chain"]


def test_advisory_failure_does_not_block(valid_subject):
    # a malformed runtime id is advisory only → verdict remains PASS
    report = ValidationEngine().validate(mutate(valid_subject, runtime_id="bad"))
    assert report.verdict is Verdict.PASS
    assert [f.check_id for f in report.advisory_failures] == ["identity-deterministic"]


def test_findings_are_deterministically_ordered(valid_subject):
    report = ValidationEngine().validate(valid_subject)
    ids = [f.check_id for f in report.findings]
    assert ids == sorted(ids)


def test_report_is_deterministic(valid_subject):
    a = ValidationEngine().validate(valid_subject)
    b = ValidationEngine().validate(valid_subject)
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)


def test_engine_accepts_custom_check_set(valid_subject):
    engine = ValidationEngine(checks=[ProvenanceCheck()])
    assert engine.check_ids == ("provenance-chain",)
    report = engine.validate(valid_subject)
    assert len(report.findings) == 1
    assert report.verdict is Verdict.PASS


def test_validate_runtime_unit_convenience(runtime_unit):
    report = validate_runtime_unit(runtime_unit)
    assert report.verdict is Verdict.PASS
    assert report.blueprint_id == "BP-DATA-0001"
    assert report.target_id.startswith("UCOS-RUN-BP-DATA-0001-")


def test_check_ids_reflect_default_suite():
    engine = ValidationEngine()
    assert "provenance-chain" in engine.check_ids
    assert len(engine.check_ids) == 7


def test_severity_values():
    assert Severity.BLOCKING.value == "blocking"
    assert Severity.ADVISORY.value == "advisory"
