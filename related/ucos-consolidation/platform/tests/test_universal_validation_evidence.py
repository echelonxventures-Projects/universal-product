"""UCOS-EPIC-005 — Universal Validation evidence tests (Terminal T5)."""

from __future__ import annotations

from platform.tests.universal_validation_helpers import passing_facts, passing_target
from platform.universal_validation.contracts import ValidationTarget
from platform.universal_validation.engine import UniversalValidationEngine
from platform.universal_validation.evidence import EVIDENCE_FORMAT, build_validation_evidence


def _report(facts=None):
    target = passing_target() if facts is None else ValidationTarget(target_id="T", facts=facts)
    return UniversalValidationEngine().validate(target)


def test_evidence_captures_pass_run():
    evidence = build_validation_evidence(_report())
    assert evidence.passed is True
    assert evidence.verdict == "pass"
    assert len(evidence.rules_run) == 21
    assert evidence.blocking_failures == ()
    assert evidence.authority == "ENGINEERING-EXECUTION-ONLY"
    payload = evidence.to_dict()
    assert payload["evidence_format"] == EVIDENCE_FORMAT
    assert len(payload["evidence_sha256"]) == 64
    assert len(payload["findings"]) == 21


def test_evidence_captures_failures():
    facts = passing_facts()
    facts["runtime"]["units"] = [{"runtime_id": "bad"}]
    evidence = build_validation_evidence(_report(facts))
    assert evidence.passed is False
    assert "runtime.identity-deterministic" in evidence.blocking_failures
    assert "runtime.image-digest-pinned" in evidence.blocking_failures


def test_evidence_is_deterministic():
    first = build_validation_evidence(_report()).to_dict()
    second = build_validation_evidence(_report()).to_dict()
    assert first == second
    assert first["evidence_sha256"] == second["evidence_sha256"]
