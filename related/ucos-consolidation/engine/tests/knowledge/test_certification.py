"""Tests for engine.knowledge.certification — Part 11 completeness certification."""

from __future__ import annotations

import dataclasses

from engine.knowledge.certification import (
    CertStatus,
    KnowledgeCertifier,
    certify_base,
)
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko, make_decision


def _criteria(record):
    return {c.criterion_id: c.passed for c in record.criteria}


def test_seed_base_is_certified(seed_base):
    report = certify_base(seed_base)
    assert report.certified
    assert report.status is CertStatus.CERTIFIED
    assert report.not_certified_ids == ()
    d = report.to_dict()
    assert d["certified"] is True
    assert d["count"] == len(seed_base.objects())


def test_record_is_content_addressed_and_verifies():
    base = KnowledgeBase([make_cko("A", owner="X", rationale="r")])
    record = KnowledgeCertifier().certify_object(base.require_object("A"), base)
    assert record.certification_id.startswith("UKDA-CERT-A-")
    assert record.verify_integrity()
    assert record.to_dict()["cko_id"] == "A"


def test_missing_owner_fails_certification():
    base = KnowledgeBase([make_cko("A", owner="UNASSIGNED")])
    record = KnowledgeCertifier().certify_object(base.require_object("A"), base)
    assert not record.certified
    assert not _criteria(record)["owner-identified"]


def test_missing_rationale_for_principle_fails():
    obj = make_cko(
        "P",
        kind=KnowledgeKind.PRINCIPLE,
        rationale="",
        authority=KnowledgeAuthority.CONSTITUTIONAL,
    )
    base = KnowledgeBase([obj])
    record = KnowledgeCertifier().certify_object(base.require_object("P"), base)
    assert not _criteria(record)["rationale-present"]


def test_unresolved_dependency_fails():
    base = KnowledgeBase([make_cko("A", dependencies=("MISSING",), rationale="r")])
    record = KnowledgeCertifier().certify_object(base.require_object("A"), base)
    assert not _criteria(record)["dependencies-resolve"]


def test_decision_object_unreviewable_fails():
    # DECISION object with no linked decision record.
    base = KnowledgeBase([make_cko("D", kind=KnowledgeKind.DECISION, rationale="r")])
    record = KnowledgeCertifier().certify_object(base.require_object("D"), base)
    assert not _criteria(record)["decision-reviewable"]


def test_decision_object_reviewable_when_linked():
    base = KnowledgeBase(
        [make_cko("D", kind=KnowledgeKind.DECISION, rationale="r", decision_links=("DEC1",))],
        [make_decision("DEC1")],
    )
    record = KnowledgeCertifier().certify_object(base.require_object("D"), base)
    assert _criteria(record)["decision-reviewable"]
    assert _criteria(record)["decisions-resolve"]


def test_unresolved_decision_link_fails():
    obj = make_cko("D", kind=KnowledgeKind.DECISION, rationale="r", decision_links=("MISSING",))
    base = KnowledgeBase([obj])
    record = KnowledgeCertifier().certify_object(base.require_object("D"), base)
    assert not _criteria(record)["decisions-resolve"]


def test_integrity_failure_fails_certification():
    good = make_cko("A", owner="X", rationale="r")
    tampered = dataclasses.replace(good, title="t")
    base = KnowledgeBase([good]).replace_object(tampered)
    record = KnowledgeCertifier().certify_object(base.require_object("A"), base)
    assert not _criteria(record)["integrity-sealed"]


def test_base_report_not_certified_ids():
    base = KnowledgeBase(
        [make_cko("A", owner="X", rationale="r"), make_cko("B", owner="UNASSIGNED")]
    )
    report = certify_base(base)
    assert not report.certified
    assert "B" in report.not_certified_ids
