"""Tests for engine.knowledge.integration.ownership — Deliverable 3."""

from __future__ import annotations

import pytest

from engine.knowledge.integration.contracts import Operation
from engine.knowledge.integration.errors import OwnershipViolationError
from engine.knowledge.integration.ownership import OwnershipProtocol
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko, make_intent


def test_declare_and_satisfied_create():
    proto = OwnershipProtocol()
    intent = make_intent("N-1")
    ownership = proto.declare(intent)
    assert ownership.canonical_id == "N-1"
    assert ownership.owner == "TEAM-A"
    assert proto.assess(intent, KnowledgeBase([])).satisfied
    d = proto.assess(intent, KnowledgeBase([])).to_dict()
    assert d["satisfied"] is True


def test_unassigned_owner_and_existing_identity():
    proto = OwnershipProtocol()
    bad = make_intent("N-2", owner="UNASSIGNED")
    assert not proto.assess(bad, KnowledgeBase([])).satisfied
    base = KnowledgeBase([make_cko("N-3")])
    clash = make_intent("N-3")
    assessment = proto.assess(clash, base)
    assert not assessment.satisfied
    assert any("already owned" in issue for issue in assessment.issues)


def test_modify_semantics():
    proto = OwnershipProtocol()
    base = KnowledgeBase([make_cko("M-1", owner="OWN", authority=KnowledgeAuthority.ENGINEERING)])
    # modify missing
    missing = make_intent("MISSING", operation=Operation.MODIFY)
    assert not proto.assess(missing, base).satisfied
    # ownership takeover
    takeover = make_intent("M-1", owner="OTHER", operation=Operation.MODIFY)
    assert any("takeover" in i for i in proto.assess(takeover, base).issues)
    # authority change
    auth_change = make_intent(
        "M-1", owner="OWN", authority=KnowledgeAuthority.CONSTITUTIONAL, operation=Operation.MODIFY
    )
    assert any("authority change" in i for i in proto.assess(auth_change, base).issues)
    # a clean modify
    clean = make_intent("M-1", owner="OWN", operation=Operation.MODIFY)
    ownership = proto.require(clean, base)
    assert ownership.owner == "OWN"


def test_require_raises():
    proto = OwnershipProtocol()
    with pytest.raises(OwnershipViolationError):
        proto.require(make_intent("X", owner="UNASSIGNED"), KnowledgeBase([]))


def test_find_overlaps():
    proto = OwnershipProtocol()
    # two active objects, identical substance, different owners -> overlap
    base = KnowledgeBase(
        [
            make_cko("O-1", statement="same substance", owner="TEAM-A", kind=KnowledgeKind.FACT),
            make_cko("O-2", statement="same substance", owner="TEAM-B", kind=KnowledgeKind.FACT),
        ]
    )
    overlaps = proto.find_overlaps(base)
    assert overlaps
    assert set(overlaps[0].owners) == {"TEAM-A", "TEAM-B"}
    assert overlaps[0].cko_ids == ("O-1", "O-2")
    assert "semantic_sha256" in overlaps[0].to_dict()
    # single owner -> no overlap
    solo = KnowledgeBase([make_cko("S-1"), make_cko("S-2", statement="different")])
    assert proto.find_overlaps(solo) == ()


def test_a_retired_object_does_not_carry_its_owner_into_an_overlap():
    """Overlap is about who claims the SAME LIVE knowledge, not who ever claimed it.

    A DEPRECATED object keeps its owner and its semantic hash, so including it would report a
    permanent overlap between the team that gave a claim up and the team that replaced it —
    a contradiction that can never be resolved, because deprecating is exactly how a claim is
    given up. The active twin is still detected, so the filter narrows the answer without
    hiding one.
    """

    retired = make_cko("OLD", owner="TEAM-A", statement="one shared substance")
    retired = retired.transition_to(Lifecycle.DEPRECATED)
    assert not retired.is_active
    live = make_cko("NEW", owner="TEAM-B", statement="one shared substance")
    other = make_cko("ALSO", owner="TEAM-C", statement="one shared substance")

    protocol = OwnershipProtocol()
    with_retired = protocol.find_overlaps(KnowledgeBase([retired, live]))
    assert with_retired == ()

    both_live = protocol.find_overlaps(KnowledgeBase([live, other]))
    assert len(both_live) == 1
    assert set(both_live[0].owners) == {"TEAM-B", "TEAM-C"}
