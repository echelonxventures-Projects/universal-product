"""Tests for engine.knowledge.intelligence — search + discovery (Part 04/09)."""

from __future__ import annotations

from engine.knowledge.intelligence import KnowledgeIntelligence, build_intelligence
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko, make_decision


def test_search_empty_query_and_ranking():
    base = KnowledgeBase(
        [
            make_cko(
                "A",
                title="Knowledge Once",
                statement="knowledge knowledge once",
                authority=KnowledgeAuthority.CONSTITUTIONAL,
            ),
            make_cko("B", title="Other", statement="something once"),
        ]
    )
    intel = KnowledgeIntelligence(base)
    assert intel.search("") == ()
    hits = intel.search("knowledge once")
    assert hits[0].cko_id == "A"  # more matches + higher authority
    assert {h.cko_id for h in hits} == {"A", "B"}
    assert hits[0].to_dict()["cko_id"] == "A"
    assert intel.search("knowledge", limit=1)[0].cko_id == "A"
    assert intel.search("nonexistentterm") == ()


def test_search_decisions():
    base = KnowledgeBase([], [make_decision("D1", problem_statement="pagination is slow")])
    intel = KnowledgeIntelligence(base)
    assert intel.search_decisions("pagination slow") == ("D1",)
    assert intel.search_decisions("") == ()
    assert intel.search_decisions("unrelated") == ()


def test_dependency_and_impact():
    base = KnowledgeBase(
        [make_cko("A", dependencies=("B",)), make_cko("B", dependencies=("C",)), make_cko("C")]
    )
    intel = build_intelligence(base)
    assert intel.dependencies_of("A") == ("B",)
    assert intel.dependents_of("B") == ("A",)
    assert set(intel.impact_analysis("C")) == {"A", "B"}
    assert intel.base is base
    assert intel.graph is not None


def test_find_duplicates():
    base = KnowledgeBase(
        [make_cko("A", statement="same thing"), make_cko("B", statement="same thing")]
    )
    dupes = KnowledgeIntelligence(base).find_duplicates()
    assert dupes and dupes[0].cko_ids == ("A", "B")
    assert "semantic_sha256" in dupes[0].to_dict()


def test_find_conflicts_declared_and_superseded():
    # Superseded-yet-active is a conflict.
    base = KnowledgeBase(
        [
            make_cko("A", lifecycle=Lifecycle.OPERATIONAL, superseded_by="B"),
            make_cko("B", lifecycle=Lifecycle.OPERATIONAL),
        ]
    )
    conflicts = KnowledgeIntelligence(base).find_conflicts()
    reasons = {c.reason for c in conflicts}
    assert any("superseded" in r for r in reasons)
    assert conflicts[0].to_dict()["left"]
    # Declared conflict between two active objects.
    declared = KnowledgeBase(
        [
            make_cko("X", lifecycle=Lifecycle.OPERATIONAL, conflicts_with=("Y",)),
            make_cko("Y", lifecycle=Lifecycle.OPERATIONAL),
        ]
    )
    dc = KnowledgeIntelligence(declared).find_conflicts()
    assert any(c.left == "X" and c.right == "Y" for c in dc)


def test_find_orphans_and_broken_refs_and_undocumented():
    base = KnowledgeBase(
        [
            make_cko("ORPH", kind=KnowledgeKind.FACT),  # not a root kind, no edges
            make_cko("ROOT", kind=KnowledgeKind.PRINCIPLE),  # root kind, exempt
            make_cko("BROKEN", dependencies=("MISSING",)),
            make_cko("DEC", kind=KnowledgeKind.DECISION),  # no decision_links -> undocumented
        ]
    )
    intel = KnowledgeIntelligence(base)
    assert "ORPH" in intel.find_orphans()
    assert "ROOT" not in intel.find_orphans()
    assert ("BROKEN", "MISSING") in intel.find_broken_references()
    assert "DEC" in intel.find_undocumented_decisions()


def test_coverage_report():
    base = KnowledgeBase(
        [
            make_cko("A", kind=KnowledgeKind.DECISION, rationale=""),  # missing rationale
            make_cko("B", owner="UNASSIGNED"),  # missing owner
        ]
    )
    cov = KnowledgeIntelligence(base).coverage()
    d = cov.to_dict()
    assert d["total_objects"] == 2
    assert "A" in d["objects_missing_rationale"]
    assert "B" in d["objects_missing_owner"]
    assert d["by_kind"]


def test_a_conflict_pair_is_reported_only_while_both_sides_are_live():
    """A conflict is a contradiction between two things that are BOTH in force.

    A declared conflict with an object that has been deprecated is a resolved conflict —
    the two claims no longer both stand — so reporting it would keep a finished argument
    permanently open. The loop moves on rather than recording it, and the same pair with
    both sides active is still reported, so the filter narrows the answer without hiding one.
    """

    live = make_cko("LIVE", conflicts_with=("RIVAL",))
    rival = make_cko("RIVAL")
    both_active = KnowledgeIntelligence(KnowledgeBase([live, rival])).find_conflicts()
    assert {tuple(sorted((f.left, f.right))) for f in both_active} == {("LIVE", "RIVAL")}

    retired = rival.transition_to(Lifecycle.DEPRECATED)
    assert not retired.is_active
    resolved = KnowledgeIntelligence(KnowledgeBase([live, retired])).find_conflicts()
    assert not any({f.left, f.right} == {"LIVE", "RIVAL"} for f in resolved)


def test_a_decision_link_naming_no_recorded_decision_is_a_broken_reference():
    """Decision links are resolved against the DECISION ids, not the object ids.

    They are checked in a second loop for that reason, and it was the loop with no test: an
    object citing a decision the base does not record would have read as fully grounded,
    which is the shape that lets a decision link point at nothing indefinitely.
    """

    recorded = make_decision("UDR-1")
    citing = make_cko("A", decision_links=("UDR-1", "UDR-ABSENT"))
    broken = KnowledgeIntelligence(KnowledgeBase([citing], [recorded])).find_broken_references()

    assert ("A", "UDR-ABSENT") in broken
    assert ("A", "UDR-1") not in broken
