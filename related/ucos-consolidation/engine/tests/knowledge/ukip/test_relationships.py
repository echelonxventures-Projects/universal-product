"""Tests for engine.knowledge.ukip.relationships (EPIC-UKDA-003).

Coverage targets every reachable path in:
    Relationship, DanglingRelationship, Cycle, RelationshipSet, build_relationships,
    relationships_of.
"""

from __future__ import annotations

import pytest

from engine.knowledge.model import RelationType
from engine.knowledge.ukip.contracts import RelationDeclaration
from engine.knowledge.ukip.errors import RelationshipCompositionError
from engine.knowledge.ukip.relationships import (
    ACYCLIC_FAMILIES,
    COMPOSITION_RULES,
    SEMANTIC_INVERSES,
    SYMMETRIC,
    Cycle,
    DanglingRelationship,
    Relationship,
    RelationshipSet,
    _lt,
    build_relationships,
    relationships_of,
)
from engine.temporal.coordinate import (
    CreationMethod,
    Precision,
    Provenance,
    ReferenceSystem,
    SystemType,
    TemporalCoordinate,
    ValidityPeriod,
)

from .conftest import make_unit, register


def _coord(counter: int, *, system: str = "test-clock") -> TemporalCoordinate:
    return TemporalCoordinate.logical(counter, system_identifier=system, authority="test")


def _validity(
    since: int, until: int | None = None, *, system: str = "test-clock"
) -> ValidityPeriod:
    return ValidityPeriod(
        since=_coord(since, system=system),
        until=None if until is None else _coord(until, system=system),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_rel(
    source: str = "A",
    target: str = "B",
    relation: RelationType = RelationType.DEPENDS_ON,
    *,
    derived: bool = False,
    path: tuple[str, ...] = (),
    note: str = "",
    validity: ValidityPeriod | None = None,
) -> Relationship:
    return Relationship(
        source=source,
        target=target,
        relation=relation,
        note=note,
        derived=derived,
        path=path,
        validity=validity,
    )


def _symmetric_rel(source: str = "A", target: str = "B") -> Relationship:
    return Relationship(
        source=source,
        target=target,
        relation=RelationType.EQUIVALENT_TO,
    )


# ---------------------------------------------------------------------------
# Relationship — inverse_reading (symmetric branch, line 122)
# ---------------------------------------------------------------------------


class TestRelationshipInverseReading:
    def test_asymmetric_relation_returns_semantic_inverse(self) -> None:
        rel = _make_rel(relation=RelationType.DEPENDS_ON)
        assert rel.inverse_reading == SEMANTIC_INVERSES[RelationType.DEPENDS_ON]

    def test_symmetric_relation_returns_its_own_value(self) -> None:
        # line 122: the symmetric branch of inverse_reading
        rel = _symmetric_rel()
        assert rel.inverse_reading == RelationType.EQUIVALENT_TO.value

    def test_is_symmetric_property(self) -> None:
        assert _symmetric_rel().is_symmetric is True
        assert _make_rel().is_symmetric is False


# ---------------------------------------------------------------------------
# Relationship — mirrored (fail-closed line 134)
# ---------------------------------------------------------------------------


class TestRelationshipMirrored:
    def test_symmetric_relation_is_mirrored_correctly(self) -> None:
        rel = _symmetric_rel("A", "B")
        mirror = rel.mirrored()
        assert mirror.source == "B"
        assert mirror.target == "A"
        assert mirror.note == "symmetric-closure"

    def test_mirroring_asymmetric_relation_raises(self) -> None:
        # line 134: fail-closed guard — only symmetric relations may be mirrored
        rel = _make_rel(relation=RelationType.DEPENDS_ON)
        with pytest.raises(RelationshipCompositionError):
            rel.mirrored()


# ---------------------------------------------------------------------------
# DanglingRelationship.to_dict (line 163)
# ---------------------------------------------------------------------------


class TestDanglingRelationshipToDict:
    def test_to_dict_contains_all_fields(self) -> None:
        # line 163
        dang = DanglingRelationship(
            source="UKID-A",
            declared_target="unknown-ref",
            relation=RelationType.DEPENDS_ON,
            note="provider declared this",
        )
        d = dang.to_dict()
        assert d["source"] == "UKID-A"
        assert d["declared_target"] == "unknown-ref"
        assert d["relation"] == RelationType.DEPENDS_ON.value
        assert d["note"] == "provider declared this"


# ---------------------------------------------------------------------------
# Cycle.to_dict (line 179)
# ---------------------------------------------------------------------------


class TestCycleToDict:
    def test_to_dict_roundtrips_fields(self) -> None:
        # line 179
        cycle = Cycle(family="dependency", members=("A", "B", "C"))
        d = cycle.to_dict()
        assert d["family"] == "dependency"
        assert d["members"] == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# RelationshipSet construction — dedup: asserted beats derived (branch 197→193)
# ---------------------------------------------------------------------------


class TestRelationshipSetDedup:
    def test_asserted_beats_derived_with_same_key(self) -> None:
        # 197→193: existing is not None and existing.derived and not rel.derived →
        # asserted replaces derived
        derived = Relationship("A", "B", RelationType.DEPENDS_ON, derived=True)
        asserted = Relationship("A", "B", RelationType.DEPENDS_ON, derived=False, note="real")
        rset = RelationshipSet([derived, asserted])
        assert len(rset) == 1
        kept = rset.all()[0]
        assert not kept.derived
        assert kept.note == "real"

    def test_derived_does_not_beat_asserted(self) -> None:
        # second derived with same key must NOT replace an already-stored asserted
        asserted = Relationship("A", "B", RelationType.DEPENDS_ON, derived=False, note="real")
        derived2 = Relationship("A", "B", RelationType.DEPENDS_ON, derived=True, note="derived")
        rset = RelationshipSet([asserted, derived2])
        assert len(rset) == 1
        assert rset.all()[0].note == "real"


class TestRelationshipTemporalValidity:
    """UCKP-ART-07 temporal validity (P4-F-002): the same (source, target, relation)
    triple can carry more than one relationship instance over time."""

    def test_non_overlapping_validity_windows_coexist(self) -> None:
        earlier = _make_rel(note="v1", validity=_validity(0, 10))
        later = _make_rel(note="v2", validity=_validity(10, None))
        rset = RelationshipSet([earlier, later])
        assert len(rset) == 2
        assert {r.note for r in rset.all()} == {"v1", "v2"}

    def test_overlapping_validity_windows_collapse_asserted_over_derived(self) -> None:
        derived = _make_rel(derived=True, note="derived", validity=_validity(0, None))
        asserted = _make_rel(derived=False, note="asserted", validity=_validity(0, None))
        rset = RelationshipSet([derived, asserted])
        assert len(rset) == 1
        assert rset.all()[0].note == "asserted"

    def test_timeless_relationship_still_behaves_as_single_winner(self) -> None:
        # No validity anywhere in the group: identical to the pre-existing behaviour.
        derived = _make_rel(derived=True)
        asserted = _make_rel(derived=False, note="real")
        rset = RelationshipSet([derived, asserted])
        assert len(rset) == 1
        assert rset.all()[0].note == "real"

    def test_incomparable_validity_windows_do_not_collapse(self) -> None:
        a = _make_rel(note="a", validity=_validity(0, None, system="clock-a"))
        b = _make_rel(note="b", validity=_validity(0, None, system="clock-b"))
        rset = RelationshipSet([a, b])
        assert len(rset) == 2

    def test_valid_at_reconstructs_the_historical_subgraph(self) -> None:
        superseded = _make_rel(note="old", validity=_validity(0, 10))
        current = _make_rel(note="new", validity=_validity(10, None))
        rset = RelationshipSet([superseded, current])
        assert [r.note for r in rset.valid_at(_coord(5)).all()] == ["old"]
        assert [r.note for r in rset.valid_at(_coord(15)).all()] == ["new"]
        # The instant a window opens belongs to the new window (half-open [since, until)).
        assert [r.note for r in rset.valid_at(_coord(10)).all()] == ["new"]

    def test_valid_at_excludes_incomparable_windows(self) -> None:
        rel = _make_rel(validity=_validity(0, None, system="clock-a"))
        rset = RelationshipSet([rel])
        assert rset.valid_at(_coord(5, system="clock-b")).all() == ()

    def test_timeless_relationship_always_holds(self) -> None:
        rel = _make_rel()
        rset = RelationshipSet([rel])
        assert len(rset.valid_at(_coord(999)).all()) == 1

    def test_identity_distinguishes_temporal_versions(self) -> None:
        earlier = _make_rel(validity=_validity(0, 10))
        later = _make_rel(validity=_validity(10, None))
        assert earlier.key() == later.key()
        assert earlier.identity() != later.identity()

    def test_seal_changes_when_a_temporal_version_is_added(self) -> None:
        base = RelationshipSet([_make_rel(validity=_validity(0, 10))])
        extended = RelationshipSet(
            [_make_rel(validity=_validity(0, 10)), _make_rel(validity=_validity(10, None))]
        )
        assert base.seal() != extended.seal()

    def test_compose_preserves_every_temporal_version_of_the_seed_set(self) -> None:
        earlier = _make_rel("A", "B", validity=_validity(0, 10))
        later = _make_rel("A", "B", validity=_validity(10, None))
        rset = RelationshipSet([earlier, later])
        composed = rset.compose()
        assert len([r for r in composed.all() if r.key() == ("A", "B", "depends-on")]) == 2

    def test_build_relationships_threads_declared_validity(self) -> None:
        window = _validity(0, None)
        unit_a = make_unit("val-target")
        unit_b = make_unit(
            "val-source",
            relations=(
                RelationDeclaration(RelationType.DEPENDS_ON, "val-target", validity=window),
            ),
        )
        registry = register((unit_a, unit_b))
        rset = build_relationships(registry)
        source_id = next(
            r.knowledge_id for r in registry.records() if "val-source" in r.canonical_source.locator
        )
        edge = rset.outbound(source_id)[0]
        assert edge.validity == window


# ---------------------------------------------------------------------------
# RelationshipSet — all(), asserted(), derived(), nodes(), types() (line 220)
# ---------------------------------------------------------------------------


class TestRelationshipSetAccessors:
    def _build(self) -> RelationshipSet:
        a = _make_rel("A", "B", RelationType.DEPENDS_ON)
        b = _make_rel("B", "C", RelationType.DEPENDS_ON, derived=True)
        return RelationshipSet([a, b])

    def test_all_returns_all_relationships(self) -> None:
        # line 220
        rset = self._build()
        assert len(rset.all()) == 2

    def test_asserted_filters_to_non_derived(self) -> None:
        rset = self._build()
        assert all(not r.derived for r in rset.asserted())
        assert len(rset.asserted()) == 1

    def test_derived_filters_to_derived_only(self) -> None:
        rset = self._build()
        assert all(r.derived for r in rset.derived())
        assert len(rset.derived()) == 1

    def test_nodes_returns_sorted_set_of_endpoints(self) -> None:
        rset = self._build()
        assert rset.nodes() == ("A", "B", "C")

    def test_types_returns_sorted_relation_types(self) -> None:
        rset = self._build()
        assert rset.types() == (RelationType.DEPENDS_ON,)

    def test_len_and_iter(self) -> None:
        rset = self._build()
        assert len(rset) == 2
        assert list(rset) == list(rset.all())

    def test_counts_dict_is_consistent(self) -> None:
        rset = self._build()
        c = rset.counts()
        assert c["relationships"] == 2
        assert c["asserted"] == 1
        assert c["derived"] == 1
        assert c["dangling"] == 0

    def test_seal_is_a_hex_string(self) -> None:
        rset = self._build()
        seal = rset.seal()
        assert isinstance(seal, str) and len(seal) > 0

    def test_to_dict_contains_expected_keys(self) -> None:
        rset = self._build()
        d = rset.to_dict()
        assert set(d) == {
            "counts",
            "seal",
            "acyclic",
            "types",
            "relationships",
            "dangling",
            "cycles",
        }


# ---------------------------------------------------------------------------
# RelationshipSet — outbound() with relation filter (line 245)
# ---------------------------------------------------------------------------


class TestRelationshipSetQueries:
    def _rset(self) -> RelationshipSet:
        deps = _make_rel("A", "B", RelationType.DEPENDS_ON)
        ext = _make_rel("A", "C", RelationType.EXTENDS)
        return RelationshipSet([deps, ext])

    def test_outbound_no_filter_returns_all_from_node(self) -> None:
        rset = self._rset()
        assert len(rset.outbound("A")) == 2

    def test_outbound_with_relation_filter(self) -> None:
        # line 245: the `if relation is not None` filter branch
        rset = self._rset()
        found = rset.outbound("A", relation=RelationType.DEPENDS_ON)
        assert len(found) == 1
        assert found[0].relation is RelationType.DEPENDS_ON

    def test_outbound_unknown_node_returns_empty(self) -> None:
        rset = self._rset()
        assert rset.outbound("X") == ()

    def test_inbound_no_filter(self) -> None:
        # line 253: inbound() default path
        rset = self._rset()
        inb = rset.inbound("B")
        assert len(inb) == 1
        assert inb[0].source == "A"

    def test_inbound_with_relation_filter(self) -> None:
        # line 257: inbound with relation kwarg
        rset = self._rset()
        found = rset.inbound("C", relation=RelationType.EXTENDS)
        assert len(found) == 1

    def test_inbound_filter_excludes_wrong_type(self) -> None:
        rset = self._rset()
        assert rset.inbound("C", relation=RelationType.DEPENDS_ON) == ()

    def test_of_type_returns_matching_relations(self) -> None:
        # line 261
        rset = self._rset()
        assert len(rset.of_type(RelationType.DEPENDS_ON)) == 1
        assert len(rset.of_type(RelationType.EQUIVALENT_TO)) == 0

    def test_neighbours_outbound_branch(self) -> None:
        # line 263: outbound loop body — need a node that has outbound edges
        rset = self._rset()
        neighbours_a = rset.neighbours("A")
        # A has outbound edges to B and C
        assert "B" in neighbours_a
        assert "C" in neighbours_a

    def test_neighbours_inbound_branch(self) -> None:
        # line 264-265: inbound loop body
        rset = self._rset()
        # B has only inbound (from A), so outbound loop body is skipped,
        # inbound loop body is executed
        neighbours_b = rset.neighbours("B")
        assert "A" in neighbours_b

    def test_degree_counts_both_directions(self) -> None:
        rset = self._rset()
        assert rset.degree("A") == 2  # two outbound
        assert rset.degree("B") == 1  # one inbound

    def test_dangling_returns_tuple(self) -> None:
        dang = DanglingRelationship("A", "missing", RelationType.DEPENDS_ON)
        rset = RelationshipSet([], [dang])
        assert len(rset.dangling()) == 1
        assert rset.dangling()[0].declared_target == "missing"


# ---------------------------------------------------------------------------
# RelationshipSet — is_navigable_both_ways / unnavigable
# ---------------------------------------------------------------------------


class TestNavigability:
    def test_symmetric_relation_is_navigable_when_mirror_present(self) -> None:
        fwd = _symmetric_rel("A", "B")
        bwd = fwd.mirrored()
        rset = RelationshipSet([fwd, bwd])
        assert rset.is_navigable_both_ways(fwd)

    def test_symmetric_relation_is_not_navigable_without_mirror(self) -> None:
        fwd = _symmetric_rel("A", "B")
        rset = RelationshipSet([fwd])
        assert not rset.is_navigable_both_ways(fwd)
        assert len(rset.unnavigable()) == 1

    def test_asymmetric_relation_is_navigable_via_inbound(self) -> None:
        dep = _make_rel("A", "B", RelationType.DEPENDS_ON)
        rset = RelationshipSet([dep])
        assert rset.is_navigable_both_ways(dep)

    def test_is_acyclic_true_when_no_cycles(self) -> None:
        dep = _make_rel("A", "B", RelationType.DEPENDS_ON)
        rset = RelationshipSet([dep])
        assert rset.is_acyclic


# ---------------------------------------------------------------------------
# RelationshipSet.compose (lines 296, 299→323, 307, 317)
# ---------------------------------------------------------------------------


class TestCompose:
    def test_compose_max_depth_less_than_1_raises(self) -> None:
        # line 296: fail-closed guard
        rset = RelationshipSet([_make_rel("A", "B")])
        with pytest.raises(RelationshipCompositionError):
            rset.compose(max_depth=0)

    def test_compose_derives_transitive_dependency(self) -> None:
        ab = _make_rel("A", "B", RelationType.DEPENDS_ON)
        bc = _make_rel("B", "C", RelationType.DEPENDS_ON)
        rset = RelationshipSet([ab, bc])
        composed = rset.compose()
        keys = {r.key() for r in composed}
        # A→C should be derived
        assert ("A", "C", RelationType.DEPENDS_ON.value) in keys

    def test_compose_skips_when_no_composition_rule(self) -> None:
        # line 307: composite is None → continue
        # GOVERNS + DEPENDS_ON has no rule → no derived edge
        gov = _make_rel("A", "B", RelationType.GOVERNS)
        dep = _make_rel("B", "C", RelationType.DEPENDS_ON)
        rset = RelationshipSet([gov, dep])
        composed = rset.compose()
        derived = [r for r in composed if r.derived]
        assert all(r.source != "A" or r.target != "C" for r in derived)

    def test_compose_skips_back_onto_origin(self) -> None:
        # line 317: left.source == right.target → skip
        ab = _make_rel("A", "B", RelationType.DEPENDS_ON)
        ba = _make_rel("B", "A", RelationType.DEPENDS_ON)
        rset = RelationshipSet([ab, ba])
        composed = rset.compose()
        # A→A must not appear
        for r in composed:
            assert not (r.source == "A" and r.target == "A")

    def test_compose_all_depth_iterations_consumed(self) -> None:
        # line 299→323 (loop runs to max_depth without early break):
        # A→B→C→D — one edge per depth. At depth=1: A→C derived. At depth=2: A→D derived.
        # At depth=3: no new edges → early break after the third iteration,
        # but with max_depth=2 both iterations produce edges → no early break.
        ab = _make_rel("A", "B", RelationType.DEPENDS_ON)
        bc = _make_rel("B", "C", RelationType.DEPENDS_ON)
        cd = _make_rel("C", "D", RelationType.DEPENDS_ON)
        rset = RelationshipSet([ab, bc, cd])
        # max_depth=2 means two full iterations, both producing edges → 299→323 taken
        composed = rset.compose(max_depth=2)
        keys = {r.key() for r in composed}
        assert ("A", "C", RelationType.DEPENDS_ON.value) in keys
        assert ("A", "D", RelationType.DEPENDS_ON.value) in keys

    def test_compose_skips_already_known_candidate(self) -> None:
        # line 317: two paths that would derive the same edge — only one is kept
        # A→B (DEPENDS_ON), B→C (DEPENDS_ON), A→B2 (DEPENDS_ON), B2→C (DEPENDS_ON)
        # Both produce A→C; the second candidate hits `if candidate.key() in known: continue`
        ab = _make_rel("A", "B", RelationType.DEPENDS_ON)
        bc = _make_rel("B", "C", RelationType.DEPENDS_ON)
        ab2 = _make_rel("A", "B2", RelationType.DEPENDS_ON)
        b2c = _make_rel("B2", "C", RelationType.DEPENDS_ON)
        rset = RelationshipSet([ab, bc, ab2, b2c])
        composed = rset.compose()
        ac_count = sum(
            1
            for r in composed
            if r.source == "A" and r.target == "C" and r.relation is RelationType.DEPENDS_ON
        )
        assert ac_count == 1


# ---------------------------------------------------------------------------
# RelationshipSet.transitive (lines 329–345)
# ---------------------------------------------------------------------------


class TestTransitive:
    def _chain(self) -> RelationshipSet:
        return RelationshipSet(
            [
                _make_rel("A", "B", RelationType.DEPENDS_ON),
                _make_rel("B", "C", RelationType.DEPENDS_ON),
                _make_rel("C", "D", RelationType.DEPENDS_ON),
            ]
        )

    def test_transitive_outbound_collects_full_chain(self) -> None:
        # lines 329-345
        rset = self._chain()
        result = rset.transitive("A", relation=RelationType.DEPENDS_ON)
        assert set(result) == {"B", "C", "D"}

    def test_transitive_inbound_collects_predecessors(self) -> None:
        rset = self._chain()
        result = rset.transitive("D", relation=RelationType.DEPENDS_ON, inbound=True)
        assert set(result) == {"A", "B", "C"}

    def test_transitive_on_leaf_returns_empty(self) -> None:
        rset = self._chain()
        assert rset.transitive("D", relation=RelationType.DEPENDS_ON) == ()

    def test_transitive_visited_skip_in_diamond(self) -> None:
        # line 341→340: candidate already in visited — diamond graph
        # A→B, A→C, B→D, C→D — D is reachable from A via both B and C
        # When D is first seen via B it enters visited; via C it hits the skip
        ab = _make_rel("A", "B", RelationType.DEPENDS_ON)
        ac = _make_rel("A", "C", RelationType.DEPENDS_ON)
        bd = _make_rel("B", "D", RelationType.DEPENDS_ON)
        cd = _make_rel("C", "D", RelationType.DEPENDS_ON)
        rset = RelationshipSet([ab, ac, bd, cd])
        result = rset.transitive("A", relation=RelationType.DEPENDS_ON)
        assert set(result) == {"B", "C", "D"}
        # D appears exactly once
        assert result.count("D") == 1


# ---------------------------------------------------------------------------
# RelationshipSet.cycles — _find_cycle inner paths (lines 362, 374, 376)
# ---------------------------------------------------------------------------


class TestCycles:
    def test_cycle_detected_in_dependency_family(self) -> None:
        # line 362, 374: neighbour == start → return path
        ab = _make_rel("A", "B", RelationType.DEPENDS_ON)
        ba = _make_rel("B", "A", RelationType.DEPENDS_ON)
        rset = RelationshipSet([ab, ba])
        found = rset.cycles()
        assert len(found) >= 1
        assert any(c.family == "dependency" for c in found)

    def test_cycle_detected_in_structure_family(self) -> None:
        ab = _make_rel("A", "B", RelationType.EXTENDS)
        bc = _make_rel("B", "C", RelationType.EXTENDS)
        ca = _make_rel("C", "A", RelationType.EXTENDS)
        rset = RelationshipSet([ab, bc, ca])
        found = rset.cycles()
        assert any(c.family == "structure" for c in found)

    def test_inner_cycle_branch_hit(self) -> None:
        # line 376: neighbour in path but != start → return inner-cycle slice
        # Graph: A→B, B→C, C→B
        # _find_cycle(start=A): path=[A,B,C]; C's neighbour is B; B in path, B!=start → line 376
        adjacency = {"A": ["B"], "B": ["C"], "C": ["B"]}
        result = RelationshipSet._find_cycle(adjacency, "A")
        # returns the inner-cycle members (B onward)
        assert "B" in result
        assert "C" in result

    def test_seen_skip_branch_hit(self) -> None:
        # line 378: neighbour in seen → continue (already fully explored)
        # Graph: A→B, A→C, B→D, C→D (diamond, no cycle)
        # DFS from A: C explored first (LIFO), D added to seen;
        # then B is explored, B→D but D already in seen → line 378
        adjacency = {"A": ["B", "C"], "B": ["D"], "C": ["D"]}
        result = RelationshipSet._find_cycle(adjacency, "A")
        assert result == ()  # no cycle — but seen-skip branch was exercised

    def test_inner_cycle_not_involving_start(self) -> None:
        # same shape expressed as a RelationshipSet to cover the full cycles() path
        ab = _make_rel("X", "Y", RelationType.DEPENDS_ON)
        bc = _make_rel("Y", "Z", RelationType.DEPENDS_ON)
        cb = _make_rel("Z", "Y", RelationType.DEPENDS_ON)  # inner cycle Y↔Z
        rset = RelationshipSet([ab, bc, cb])
        found = rset.cycles()
        # A cycle must be detected in the dependency family
        assert any(c.family == "dependency" for c in found)

    def test_no_cycle_in_linear_chain(self) -> None:
        rset = RelationshipSet(
            [
                _make_rel("A", "B", RelationType.DEPENDS_ON),
                _make_rel("B", "C", RelationType.DEPENDS_ON),
            ]
        )
        assert rset.cycles() == ()

    def test_supersession_cycle_detected(self) -> None:
        ab = _make_rel("A", "B", RelationType.SUPERSEDES)
        ba = _make_rel("B", "A", RelationType.SUPERSEDES)
        rset = RelationshipSet([ab, ba])
        found = rset.cycles()
        assert any(c.family == "supersession" for c in found)


# ---------------------------------------------------------------------------
# build_relationships — self-relation skip (line 440), dangling, symmetric close
# ---------------------------------------------------------------------------


class TestBuildRelationships:
    def test_self_relation_is_silently_dropped(self) -> None:
        # line 440: target == record.knowledge_id → skip
        # Build a registry where a unit declares a relation to itself via its own key

        unit_a = make_unit(
            "self-ref",
            relations=(RelationDeclaration(RelationType.DEPENDS_ON, "self-ref"),),
        )
        registry = register((unit_a,))
        rset = build_relationships(registry)
        for r in rset:
            assert r.source != r.target

    def test_dangling_target_becomes_dangling_relationship(self) -> None:
        unit_a = make_unit(
            "unit-a",
            relations=(RelationDeclaration(RelationType.DEPENDS_ON, "nonexistent-key"),),
        )
        registry = register((unit_a,))
        rset = build_relationships(registry)
        assert len(rset.dangling()) == 1
        assert rset.dangling()[0].declared_target == "nonexistent-key"

    def test_symmetric_relation_is_closed_in_both_directions(self) -> None:
        unit_a = make_unit("bld-sym-a")
        unit_b = make_unit(
            "bld-sym-b",
            relations=(RelationDeclaration(RelationType.EQUIVALENT_TO, "bld-sym-a"),),
        )
        registry = register((unit_a, unit_b))
        rset = build_relationships(registry)
        # canonical_source.locator contains the original key via make_source helper
        a_id = next(
            r.knowledge_id for r in registry.records() if "bld-sym-a" in r.canonical_source.locator
        )
        b_id = next(
            r.knowledge_id for r in registry.records() if "bld-sym-b" in r.canonical_source.locator
        )
        keys = {r.key() for r in rset}
        assert (b_id, a_id, RelationType.EQUIVALENT_TO.value) in keys
        assert (a_id, b_id, RelationType.EQUIVALENT_TO.value) in keys

    def test_close_symmetric_false_suppresses_mirror(self) -> None:
        unit_a = make_unit("bld-asym-a")
        unit_b = make_unit(
            "bld-asym-b",
            relations=(RelationDeclaration(RelationType.EQUIVALENT_TO, "bld-asym-a"),),
        )
        registry = register((unit_a, unit_b))
        rset = build_relationships(registry, close_symmetric=False)
        a_id = next(
            r.knowledge_id for r in registry.records() if "bld-asym-a" in r.canonical_source.locator
        )
        b_id = next(
            r.knowledge_id for r in registry.records() if "bld-asym-b" in r.canonical_source.locator
        )
        # only the declared direction
        assert (b_id, a_id, RelationType.EQUIVALENT_TO.value) in {r.key() for r in rset}
        assert (a_id, b_id, RelationType.EQUIVALENT_TO.value) not in {r.key() for r in rset}

    def test_resolved_asymmetric_relation_appears_in_set(self) -> None:
        unit_a = make_unit("bld-dep-target")
        unit_b = make_unit(
            "bld-dep-source",
            relations=(RelationDeclaration(RelationType.DEPENDS_ON, "bld-dep-target"),),
        )
        registry = register((unit_a, unit_b))
        rset = build_relationships(registry)
        a_id = next(
            r.knowledge_id
            for r in registry.records()
            if "bld-dep-target" in r.canonical_source.locator
        )
        b_id = next(
            r.knowledge_id
            for r in registry.records()
            if "bld-dep-source" in r.canonical_source.locator
        )
        keys = {r.key() for r in rset}
        assert (b_id, a_id, RelationType.DEPENDS_ON.value) in keys


# ---------------------------------------------------------------------------
# relationships_of (lines 457–458)
# ---------------------------------------------------------------------------


class TestRelationshipsOf:
    def test_returns_sorted_relationships_touching_record(self) -> None:
        # lines 457-458
        unit_a = make_unit("rof-target")
        unit_b = make_unit(
            "rof-source",
            relations=(RelationDeclaration(RelationType.DEPENDS_ON, "rof-target"),),
        )
        registry = register((unit_a, unit_b))
        record_a = next(r for r in registry.records() if "rof-target" in r.canonical_source.locator)
        result = relationships_of(registry, record_a)
        assert len(result) >= 1
        assert result == tuple(sorted(result, key=lambda r: r.key()))
        for rel in result:
            assert record_a.knowledge_id in (rel.source, rel.target)

    def test_returns_empty_for_isolated_record(self) -> None:
        unit_a = make_unit("rof-isolated")
        registry = register((unit_a,))
        record_a = next(r for r in registry.records())
        result = relationships_of(registry, record_a)
        assert result == ()


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class TestModuleConstants:
    def test_symmetric_set_contains_only_symmetric_types(self) -> None:
        for rt in SYMMETRIC:
            assert rt.is_symmetric

    def test_semantic_inverses_covers_all_asymmetric_types(self) -> None:
        asymmetric = [rt for rt in RelationType if not rt.is_symmetric]
        for rt in asymmetric:
            assert rt in SEMANTIC_INVERSES, f"{rt} missing from SEMANTIC_INVERSES"

    def test_composition_rules_keys_are_relation_pairs(self) -> None:
        for (a, b), result in COMPOSITION_RULES.items():
            assert isinstance(a, RelationType)
            assert isinstance(b, RelationType)
            assert isinstance(result, RelationType)

    def test_acyclic_families_are_non_empty(self) -> None:
        for _name, types in ACYCLIC_FAMILIES.items():
            assert len(types) > 0


# ---------------------------------------------------------------------------
# Law 7: a partial order, where "before" is not a question every pair answers
# ---------------------------------------------------------------------------
#
# Every temporal test above uses a TOTAL order, where any two coordinates are ordered and
# INCOMPARABLE only arises across systems — which the cross-system guards catch first. A
# system that declares `total_order=False` produces INCOMPARABLE for two coordinates in the
# SAME frame, which is the case the three guards below were written for and the only one
# that reaches them. Vector clocks and causal orders are exactly this shape, so it is a
# repository this package is meant to serve rather than a contrivance.


def _partial(counter: int) -> TemporalCoordinate:
    """A coordinate in a declared PARTIAL order: comparable to itself and nothing else."""

    return TemporalCoordinate(
        primary=str(counter),
        reference_system=ReferenceSystem(
            system_type=SystemType.LOGICAL,
            system_identifier="causal-clock",
            total_order=False,
            causality_tracking=True,
        ),
        precision=Precision(resolution="tick"),
        provenance=Provenance(
            creation_authority="test", creation_method=CreationMethod.COMPUTATION
        ),
    )


def test_before_is_unprovable_rather_than_false_in_a_partial_order() -> None:
    """``None``, never ``False``. "Not provably before" and "provably not before" are
    different answers, and collapsing them would let an unprovable ordering be read as a
    proven one — the whole reason ``Ordering`` carries an INCOMPARABLE member."""

    assert _lt(_partial(1), _partial(2)) is None
    assert _lt(_coord(1), _coord(2)) is True
    assert _lt(_coord(2), _coord(1)) is False


def test_windows_that_cannot_be_ordered_are_not_merged() -> None:
    """Deduplication merges relationships whose windows provably overlap. Two windows in a
    partial order provably overlap with nothing, so they stay separate — merging them would
    assert a shared instant that no comparison established."""
    a = _make_rel(note="a", validity=ValidityPeriod(since=_partial(1), until=_partial(9)))
    b = _make_rel(note="b", validity=ValidityPeriod(since=_partial(2), until=_partial(8)))
    rset = RelationshipSet([a, b])
    assert len(rset) == 2
    assert {r.note for r in rset.all()} == {"a", "b"}


def test_a_window_whose_end_cannot_be_ordered_holds_at_no_instant() -> None:
    """The closing bound is checked separately from the opening one, and an unprovable end
    excludes the relationship. Admitting it would mean reporting a historical subgraph that
    includes an assertion nobody can show was still in force."""
    rel = _make_rel(validity=ValidityPeriod(since=_partial(1), until=_partial(9)))
    rset = RelationshipSet([rel])
    assert rset.valid_at(_partial(5)).all() == ()


def test_a_window_that_opens_exactly_now_but_ends_unprovably_still_excludes() -> None:
    """The opening and closing bounds are checked SEPARATELY, and this is the only shape
    that reaches the second check in a partial order.

    A coordinate compares EQUAL to itself even where the order is partial, so a window whose
    ``since`` IS the instant being asked about passes the opening check — and its ``until``,
    being a different coordinate in the same partial frame, is then INCOMPARABLE. Without the
    second check the relationship would be reported as in force at an instant no comparison
    ever placed inside its window.
    """
    rel = _make_rel(validity=ValidityPeriod(since=_partial(5), until=_partial(9)))
    rset = RelationshipSet([rel])
    assert rset.valid_at(_partial(5)).all() == ()
