"""UCOS-EPIC-013 — Validation Intelligence determinism and replay tests (Terminal T5).

IMP-007 §5: an identical target analyzed by an identical suite must reproduce a
byte-identical report, projection set, and evidence hash — in this process and in a
fresh one. The cross-process checks are the decisive ones: they are the only assertions
that would catch ambient state (hash seed, wall-clock, iteration order, environment)
leaking into a constitutional identity, which in-process repetition cannot see.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from platform.tests._validation_intelligence_helpers import passing_facts, passing_target
from platform.validation_intelligence.contracts import IntelligenceTarget
from platform.validation_intelligence.engine import ContinuousValidationIntelligenceEngine
from platform.validation_intelligence.evidence import build_validation_intelligence_evidence
from platform.validation_intelligence.service import build_validation_intelligence_service

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]

_REPLAY_SCRIPT = """
import json
from platform.tests._validation_intelligence_helpers import passing_target
from platform.validation_intelligence.evidence import build_validation_intelligence_evidence
from platform.validation_intelligence.service import build_validation_intelligence_service

service = build_validation_intelligence_service()
report = service.analyze(passing_target())
evidence = build_validation_intelligence_evidence(report)
print(json.dumps({
    "report": report.report_sha256,
    "dashboard": report.dashboard().dashboard_sha256,
    "compatibility": report.compatibility_report().report_sha256,
    "compliance": report.compliance_report().report_sha256,
    "evidence": evidence.evidence_sha256,
    "target": report.target_digest,
    "verdict": report.verdict.value,
}, sort_keys=True))
"""


def _replay_in_a_fresh_process(hash_seed: str = "0") -> dict[str, str]:
    """Run one full analysis in an independent interpreter and return its identities."""
    # Strip pytest-cov's subprocess hooks so the child is a clean, independent
    # interpreter (they otherwise error at child startup under coverage).
    env = {k: v for k, v in os.environ.items() if not k.startswith(("COV_CORE", "COVERAGE"))}
    env["PYTHONHASHSEED"] = hash_seed
    completed = subprocess.run(  # noqa: S603 - constant script, trusted interpreter
        [sys.executable, "-c", _REPLAY_SCRIPT],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return json.loads(completed.stdout.strip().splitlines()[-1])


def _analyze(target=None):
    return ContinuousValidationIntelligenceEngine().analyze(target or passing_target())


# --- in-process determinism ------------------------------------------------------
def test_the_report_hash_is_stable_in_process():
    assert _analyze().report_sha256 == _analyze().report_sha256


def test_every_projection_hash_is_stable_in_process():
    first, second = _analyze(), _analyze()
    assert first.dashboard().dashboard_sha256 == second.dashboard().dashboard_sha256
    assert first.compatibility_report().report_sha256 == second.compatibility_report().report_sha256
    assert first.compliance_report().report_sha256 == second.compliance_report().report_sha256


def test_the_evidence_hash_is_stable_in_process():
    first = build_validation_intelligence_evidence(_analyze())
    second = build_validation_intelligence_evidence(_analyze())
    assert first.evidence_sha256 == second.evidence_sha256


def test_the_serialized_report_is_byte_identical_across_runs():
    first = json.dumps(_analyze().to_dict(), sort_keys=True)
    second = json.dumps(_analyze().to_dict(), sort_keys=True)
    assert first == second


def test_the_serialized_evidence_is_byte_identical_across_runs():
    def dump() -> str:
        return json.dumps(
            build_validation_intelligence_evidence(_analyze()).to_dict(), sort_keys=True
        )

    assert dump() == dump()


# --- identity is a function of content, not of authoring order -------------------
def test_fact_insertion_order_does_not_change_any_identity():
    facts = passing_facts()
    forward = IntelligenceTarget(target_id="t", facts=dict(sorted(facts.items())))
    reverse = IntelligenceTarget(target_id="t", facts=dict(sorted(facts.items(), reverse=True)))
    assert _analyze(forward).report_sha256 == _analyze(reverse).report_sha256


def test_a_changed_fact_changes_the_report_identity():
    """Determinism is not constancy: a different corpus must hash differently."""
    facts = passing_facts()
    facts["repository_completeness"]["gaps"] = 1
    mutated = IntelligenceTarget(target_id="target-pass", facts=facts)
    assert _analyze(mutated).report_sha256 != _analyze().report_sha256


def test_the_target_id_participates_in_the_report_identity():
    first = _analyze(passing_target("a"))
    second = _analyze(passing_target("b"))
    assert first.report_sha256 != second.report_sha256


def test_two_independently_built_equal_targets_agree():
    assert passing_target().digest() == passing_target().digest()


# --- cross-process replay --------------------------------------------------------
@pytest.mark.parametrize(
    "identity", ["report", "dashboard", "compatibility", "compliance", "evidence", "target"]
)
def test_every_identity_reproduces_in_a_fresh_process(identity):
    first = _replay_in_a_fresh_process()
    second = _replay_in_a_fresh_process()
    assert first[identity]
    assert first[identity] == second[identity]


def test_a_fresh_process_agrees_with_this_one():
    """The decisive replay check: an independent interpreter must reach the same identity."""
    replayed = _replay_in_a_fresh_process()
    report = _analyze()
    evidence = build_validation_intelligence_evidence(report)
    assert replayed["report"] == report.report_sha256
    assert replayed["dashboard"] == report.dashboard().dashboard_sha256
    assert replayed["compatibility"] == report.compatibility_report().report_sha256
    assert replayed["compliance"] == report.compliance_report().report_sha256
    assert replayed["evidence"] == evidence.evidence_sha256
    assert replayed["target"] == report.target_digest
    assert replayed["verdict"] == report.verdict.value


def test_identities_survive_a_randomized_hash_seed():
    """No identity may depend on dict/set iteration order."""
    assert _replay_in_a_fresh_process("0") == _replay_in_a_fresh_process("random")


# --- the service composes to the same identity -----------------------------------
def test_the_service_and_a_bare_engine_reach_one_identity():
    target = passing_target()
    assert build_validation_intelligence_service().analyze(target).report_sha256 == (
        _analyze(target).report_sha256
    )


def test_repeated_service_evidence_is_stable():
    service = build_validation_intelligence_service()
    target = passing_target()
    assert service.evidence(target).evidence_sha256 == service.evidence(target).evidence_sha256
