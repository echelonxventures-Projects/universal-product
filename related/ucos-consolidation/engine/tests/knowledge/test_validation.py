"""Tests for engine.knowledge.validation — the Part 10 fail-closed gate."""

from __future__ import annotations

import dataclasses

from engine.knowledge.model import KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.validation import (
    KnowledgeValidator,
    NoDuplicateKnowledgeCheck,
    Verdict,
    default_checks,
    validate_base,
)

from .conftest import make_cko, make_decision


def _finding(report, check_id):
    return next(f for f in report.findings if f.check_id == check_id)


def test_seed_base_is_valid(seed_base):
    report = validate_base(seed_base)
    assert report.accepted
    assert report.verdict is Verdict.VALID
    assert report.counts()["blocking_failed"] == 0
    assert report.to_dict()["accepted"] is True


def test_duplicate_knowledge_blocks():
    base = KnowledgeBase([make_cko("A", statement="dup"), make_cko("B", statement="dup")])
    report = validate_base(base)
    assert not report.accepted
    assert not _finding(report, "no-duplicate-knowledge").passed


def test_broken_reference_blocks():
    base = KnowledgeBase([make_cko("A", dependencies=("GONE",))])
    report = validate_base(base)
    assert not report.accepted
    assert not _finding(report, "no-broken-reference").passed


def test_undocumented_decision_blocks():
    base = KnowledgeBase([make_cko("D", kind=KnowledgeKind.DECISION)])
    report = validate_base(base)
    assert not _finding(report, "every-decision-documented").passed


def test_missing_rationale_and_owner_block():
    base = KnowledgeBase(
        [
            make_cko("R", kind=KnowledgeKind.RULE, rationale=""),
            make_cko("O", owner="UNASSIGNED"),
        ]
    )
    report = validate_base(base)
    assert not _finding(report, "rationale-present").passed
    assert not _finding(report, "ownership-present").passed


def test_orphan_is_advisory_not_blocking():
    base = KnowledgeBase([make_cko("LONE", owner="X", rationale="r")])
    report = validate_base(base)
    orphan = _finding(report, "no-orphan-knowledge")
    assert not orphan.passed
    assert orphan.severity.value == "advisory"
    assert report.accepted  # advisory does not block


def test_conflict_blocks():
    base = KnowledgeBase(
        [
            make_cko("X", lifecycle=Lifecycle.OPERATIONAL, conflicts_with=("Y",), rationale="r"),
            make_cko("Y", lifecycle=Lifecycle.OPERATIONAL, rationale="r"),
        ]
    )
    report = validate_base(base)
    assert not _finding(report, "no-conflicting-decision").passed
    assert not report.accepted


def test_undocumented_exception_blocks():
    base = KnowledgeBase([make_cko("E", kind=KnowledgeKind.EXCEPTION)])
    report = validate_base(base)
    assert not _finding(report, "documented-exception").passed


def test_documented_exception_passes_with_link():
    base = KnowledgeBase(
        [
            make_cko("E", kind=KnowledgeKind.EXCEPTION, knowledge_links=("R",)),
            make_cko("R", kind=KnowledgeKind.RULE, rationale="r"),
        ]
    )
    report = validate_base(base)
    assert _finding(report, "documented-exception").passed


def test_integrity_failure_blocks():
    good = make_cko("A")
    tampered = dataclasses.replace(good, title="tampered")  # hash no longer matches
    # KnowledgeBase does not re-seal; inject the tampered object via replace_object.
    base = KnowledgeBase([good]).replace_object(tampered)
    report = validate_base(base)
    assert not _finding(report, "integrity-sealed").passed
    assert not report.accepted


def test_custom_check_list_and_ids():
    validator = KnowledgeValidator([NoDuplicateKnowledgeCheck()])
    assert validator.check_ids == ("no-duplicate-knowledge",)
    assert len(default_checks()) == 9


def test_a_decision_whose_seal_no_longer_matches_is_named_as_an_offender():
    """OBJECTS AND DECISIONS ARE CHECKED SEPARATELY, and only the object arm had a test.

    A decision record is content-addressed exactly as an object is, and the integrity rule
    exists so that a store edited outside the engine is refused rather than trusted. With
    only the object loop exercised, a decision could have been edited in place and the rule
    would have reported a clean base — the offender list would simply never mention it.
    """

    sound = make_decision("UDR-1")
    assert validate_base(KnowledgeBase([], [sound])).accepted

    edited = dataclasses.replace(sound, rationale="a rationale the seal was not computed over")
    assert not edited.verify_integrity()

    report = validate_base(KnowledgeBase([], [edited]))
    assert not report.accepted
    integrity = _finding(report, "integrity-sealed")
    assert not integrity.passed
    assert "UDR-1" in integrity.offenders
