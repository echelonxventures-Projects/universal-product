"""TASK-000049 — Validation evidence tests (TASK-000048)."""

from __future__ import annotations

import json

from engine.validation import ValidationEngine, build_validation_evidence
from engine.validation.evidence import EVIDENCE_FORMAT

from .conftest import mutate


def test_evidence_from_passing_report(valid_subject):
    report = ValidationEngine().validate(valid_subject)
    evidence = build_validation_evidence(report)
    d = evidence.to_dict()
    assert d["evidence_format"] == EVIDENCE_FORMAT
    assert d["verdict"] == "pass"
    assert d["accepted"] is True
    assert d["blocking_failures"] == []
    assert len(d["checks_run"]) == 7
    assert d["counts"]["passed"] == 7


def test_evidence_from_failing_report(valid_subject):
    report = ValidationEngine().validate(mutate(valid_subject, sbom={}))
    evidence = build_validation_evidence(report).to_dict()
    assert evidence["verdict"] == "fail"
    assert evidence["accepted"] is False
    assert "sbom-present" in evidence["blocking_failures"]


def test_evidence_is_deterministic(valid_subject):
    report = ValidationEngine().validate(valid_subject)
    a = build_validation_evidence(report).to_dict()
    b = build_validation_evidence(report).to_dict()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
