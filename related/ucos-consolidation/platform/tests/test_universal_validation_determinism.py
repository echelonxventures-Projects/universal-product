"""UCOS-EPIC-005 — Universal Validation determinism tests (Terminal T5).

An identical target validated by an identical suite must yield a byte-identical
report, dashboard, and evidence record (IMP-007 §5) — no wall-clock or ambient state
may leak into any identity, and finding order must be independent of fact-insertion
order.
"""

from __future__ import annotations

from platform.tests.universal_validation_helpers import passing_facts
from platform.universal_validation.contracts import ValidationTarget
from platform.universal_validation.engine import UniversalValidationEngine
from platform.universal_validation.evidence import build_validation_evidence


def _target_from(facts):
    return ValidationTarget(target_id="UCOS-EPIC-005", facts=facts)


def test_report_is_byte_identical_across_runs():
    engine = UniversalValidationEngine()
    first = engine.validate(_target_from(passing_facts())).to_dict()
    second = engine.validate(_target_from(passing_facts())).to_dict()
    assert first == second
    assert first["report_sha256"] == second["report_sha256"]


def test_report_hash_is_independent_of_fact_ordering():
    facts = passing_facts()
    reordered = {key: facts[key] for key in reversed(list(facts))}
    engine = UniversalValidationEngine()
    a = engine.validate(_target_from(facts))
    b = engine.validate(_target_from(reordered))
    assert a.report_sha256 == b.report_sha256
    assert a.dashboard().dashboard_sha256 == b.dashboard().dashboard_sha256


def test_evidence_hash_stable_across_runs():
    engine = UniversalValidationEngine()
    a = build_validation_evidence(engine.validate(_target_from(passing_facts())))
    b = build_validation_evidence(engine.validate(_target_from(passing_facts())))
    assert a.evidence_sha256 == b.evidence_sha256


def test_target_digest_is_deterministic():
    assert _target_from(passing_facts()).digest() == _target_from(passing_facts()).digest()


def test_different_targets_have_different_report_hashes():
    engine = UniversalValidationEngine()
    good = engine.validate(_target_from(passing_facts()))
    facts = passing_facts()
    facts["quality"]["tests"] = {"passed": 1, "failed": 9}
    bad = engine.validate(_target_from(facts))
    assert good.report_sha256 != bad.report_sha256
