"""Tests for engine.knowledge.integration.duplication — Deliverable 6 (fail-closed)."""

from __future__ import annotations

import pytest

from engine.knowledge.integration.duplication import DuplicatePreventionEngine, _jaccard, _word_set
from engine.knowledge.integration.errors import DuplicationViolationError
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko, make_intent


def test_clean_intent(base):
    report = DuplicatePreventionEngine(base).screen(make_intent("NOVEL"))
    assert report.clean
    assert report.to_dict()["clean"] is True


def test_duplicate_identity(base):
    report = DuplicatePreventionEngine(base).screen(make_intent("COMP-A"))
    assert "duplicate-identity" in report.kinds()


def test_semantic_duplicate_and_overlapping_ownership():
    base = KnowledgeBase([make_cko("TWIN", statement="twin substance", owner="TEAM-A")])
    intent = make_intent("NEW", statement="twin substance", owner="TEAM-B")
    kinds = DuplicatePreventionEngine(base).screen(intent).kinds()
    assert "semantic-duplicate" in kinds
    assert "overlapping-ownership" in kinds


def test_conflicting_capability():
    base = KnowledgeBase([make_cko("ORIG", title="Shared Name", statement="original substance")])
    intent = make_intent("NEW", title="Shared Name", statement="different substance")
    assert "conflicting-capability" in DuplicatePreventionEngine(base).screen(intent).kinds()


def test_parallel_implementation():
    base = KnowledgeBase(
        [make_cko("P1", title="P One", statement="alpha beta gamma delta epsilon")]
    )
    intent = make_intent("NEW", title="P Two", statement="epsilon delta gamma beta alpha")
    report = DuplicatePreventionEngine(base).screen(intent)
    assert "parallel-implementation" in report.kinds()
    assert report.violations[0].to_dict()["kind"]


def test_redundant_universe():
    base = KnowledgeBase([make_cko("U1")])  # universe TEST
    intent = make_intent("NEW", universe="T.E.S.T", statement="wholly unique substance here")
    assert "redundant-universe" in DuplicatePreventionEngine(base).screen(intent).kinds()


def test_require_raises(base):
    engine = DuplicatePreventionEngine(base)
    with pytest.raises(DuplicationViolationError):
        engine.require(make_intent("COMP-A"))
    # a clean intent returns its report
    assert engine.require(make_intent("NOVEL")).clean


def test_two_empty_statements_are_identical_and_an_empty_union_is_not_a_match():
    """The Jaccard measure's two degenerate cases, which decide opposite things.

    Two texts that both tokenise to nothing ARE the same text, so the answer is 1.0 —
    treating them as unrelated would let two empty-statement objects coexist as though they
    said different things. The second guard is the arithmetic one: an empty union means the
    division has no denominator, and returning 0.0 there is the fail-open answer that can
    never be reached while the first guard stands. Both are asserted so that removing either
    one is a failure rather than a silent change of meaning.
    """

    assert _jaccard(_word_set(""), _word_set("   ...   ")) == 1.0
    assert _jaccard(frozenset(), frozenset()) == 1.0
    assert _jaccard(_word_set("alpha"), _word_set("")) == 0.0
    assert _jaccard(_word_set("alpha beta"), _word_set("beta gamma")) == pytest.approx(1 / 3)


def test_an_identical_title_carrying_identical_substance_is_not_a_conflict(base):
    """Same universe, same title, SAME content is a duplicate — not a rival.

    The conflict arm is for a title that has been claimed twice with different substance,
    which is two objects asserting different things under one name. Reporting it when the
    substance matches would make every idempotent re-registration look like a contradiction.
    """

    def _conflicting(intent):
        report = DuplicatePreventionEngine(base).screen(intent)
        return {
            member
            for violation in report.violations
            if violation.kind == "conflicting-capability"
            for member in violation.offenders
        }

    existing = base.require_object("COMP-A")
    identical = make_intent(
        "OTHER-ID", title=existing.title, statement=existing.statement, kind=existing.kind
    )
    assert "COMP-A" not in _conflicting(identical)

    divergent = make_intent(
        "OTHER-ID",
        title=existing.title,
        statement="a completely different substance under the same claimed title",
        kind=existing.kind,
    )
    assert "COMP-A" in _conflicting(divergent)


def test_the_empty_union_guard_stands_even_though_nothing_can_reach_it():
    """DEFENCE IN DEPTH, reached by disabling the check that makes it unreachable.

    ``if not union: return 0.0`` cannot fire while ``if not a and not b: return 1.0`` stands
    above it: a union is empty only when both sides are, and that case has already returned.
    The guard is still the thing standing between a future edit to the first check and a
    ZeroDivisionError inside a similarity measure, so it is exercised here by handing
    ``_jaccard`` a set that is non-empty and whose union is empty — the state the first check
    is currently what prevents. This test does not claim the case is reachable today; it
    claims the guard does what it says when it is reached.
    """

    class _EmptyUnion(frozenset):
        def __or__(self, other):  # type: ignore[override]
            return frozenset()

    non_empty = _EmptyUnion({"alpha"})
    assert non_empty, "the first guard must not be the thing that answers here"
    assert _jaccard(non_empty, frozenset({"beta"})) == 0.0
