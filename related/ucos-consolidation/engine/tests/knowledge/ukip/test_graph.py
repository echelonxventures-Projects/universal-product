"""UKIP Part 08 — the knowledge graph as a projection, exercised as one.

WHY THIS MODULE EXISTS. Every other UKIP part carried a suite; Part 08 carried none, so
the graph's attribution cuts, its projections, its blast radius and — most consequentially
— :meth:`KnowledgeIntelligenceGraph.unresolved` were reachable only by reading them. An
edge whose endpoint has no record is the one condition the graph declares "must be empty
for a valid graph", and nothing had ever shown it firing.
"""

from __future__ import annotations

import pytest

from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    RelationType,
)
from engine.knowledge.ukip.contracts import RelationDeclaration
from engine.knowledge.ukip.graph import (
    PROJECTION_NAMES,
    PROJECTIONS,
    KnowledgeIntelligenceGraph,
    build_graph,
)
from engine.knowledge.ukip.registry import KnowledgeRegistry
from engine.knowledge.ukip.relationships import Relationship, RelationshipSet

from .conftest import make_unit, register, unit_from


@pytest.fixture
def graph(simple_registry: KnowledgeRegistry) -> KnowledgeIntelligenceGraph:
    return build_graph(simple_registry)


def _by_title(graph: KnowledgeIntelligenceGraph, title: str) -> str:
    """A knowledge identifier addressed by the thing a test can actually name.

    Identifiers are content-addressed, so a test that hardcoded one would be asserting a
    digest rather than a behaviour, and would break on any unrelated wording change.
    """
    for node in graph.nodes():
        if node.title == title:
            return node.knowledge_id
    raise AssertionError(f"no node titled {title!r} in {[n.title for n in graph.nodes()]}")


# -- structure ------------------------------------------------------------------------


def test_the_graph_holds_one_node_per_record_and_reuses_the_part_05_edges(graph):
    assert len(graph) == 3
    assert graph.node_ids() == tuple(sorted(graph.node_ids()))
    assert len(graph.edges()) == 1
    assert graph.registry.knowledge_ids() == graph.node_ids()
    assert len(graph.relationships) == 1


def test_a_node_carries_labels_and_never_the_content(graph):
    node = graph.node(_by_title(graph, "Title a"))
    assert node is not None
    assert node.kind is KnowledgeKind.FACT
    assert node.authority is KnowledgeAuthority.ENGINEERING
    assert node.lifecycle is Lifecycle.OPERATIONAL
    assert node.universe == "TEST"
    assert node.owner == "TEST-OWNER"
    assert not hasattr(node, "statement")
    payload = node.to_dict()
    assert payload["knowledge_id"] == node.knowledge_id
    assert payload["single_sourced"] is True
    assert payload["degree"] == node.degree


def test_an_unknown_identifier_resolves_to_nothing_rather_than_raising(graph):
    assert graph.node("UKID-NOT-A-RECORD") is None
    assert graph.record("UKID-NOT-A-RECORD") is None


def test_the_record_is_fetched_from_the_registry_rather_than_duplicated(graph):
    identifier = _by_title(graph, "Title b")
    assert graph.record(identifier) is graph.registry.get(identifier)


# -- attribution ----------------------------------------------------------------------


def test_provider_attribution_answers_who_supplied_what(graph):
    assert graph.provider_contribution() == {"test-provider": 3}
    assert len(graph.nodes_by_provider("test-provider")) == 3
    assert graph.nodes_by_provider("nobody") == ()


def test_single_sourcing_is_a_corroboration_gap_and_corroboration_closes_it():
    solo = unit_from("alpha", "shared", "One statement two providers agree on.")
    echo = unit_from("beta", "shared", "One statement two providers agree on.")
    registry = register((solo, echo))
    graph = build_graph(registry)
    (node,) = graph.nodes()
    assert node.provider_ids == ("alpha", "beta")
    assert node.is_single_sourced is False
    assert graph.single_sourced() == ()
    assert graph.provider_contribution() == {"alpha": 1, "beta": 1}


def test_every_node_of_a_one_provider_registry_is_single_sourced(graph):
    assert len(graph.single_sourced()) == 3


# -- classification cuts --------------------------------------------------------------


def test_classification_cuts_select_and_reject(graph):
    assert len(graph.nodes_by_kind(KnowledgeKind.FACT)) == 3
    assert graph.nodes_by_kind(KnowledgeKind.PRINCIPLE) == ()
    assert len(graph.nodes_by_authority(KnowledgeAuthority.ENGINEERING)) == 3
    assert graph.nodes_by_authority(KnowledgeAuthority.CONSTITUTIONAL) == ()
    assert len(graph.nodes_by_universe("TEST")) == 3
    assert graph.nodes_by_universe("OTHER") == ()


def test_a_record_in_no_relationship_is_isolated(graph):
    assert graph.isolated() == (_by_title(graph, "Title c"),)


# -- navigation -----------------------------------------------------------------------


def test_navigation_primitives_agree_with_the_declared_dependency(graph):
    a, b = _by_title(graph, "Title a"), _by_title(graph, "Title b")
    assert graph.dependencies_of(b) == (a,)
    assert graph.dependents_of(a) == (b,)
    assert b in {edge.source for edge in graph.edges()}
    assert graph.successors(b, relation=RelationType.DEPENDS_ON)
    assert graph.predecessors(a, relation=RelationType.DEPENDS_ON)
    assert graph.conflicts_of(a) == ()
    assert a in graph.reachable_from(b)


def test_blast_radius_summarises_impact_by_authority(graph):
    a = _by_title(graph, "Title a")
    radius = graph.blast_radius(a)
    assert radius["knowledge_id"] == a
    assert radius["affected"] == list(graph.impact_of(a))
    assert radius["affected_count"] == len(radius["affected"])
    assert radius["by_authority"] == {"engineering": radius["affected_count"]}


def test_blast_radius_ignores_affected_identifiers_that_have_no_node():
    """The summary counts authorities it can resolve and stays silent about the rest,
    because an edge endpoint with no record is reported by ``unresolved`` — counting it
    here as well would make one defect appear twice under two names."""
    registry = register((make_unit("a", statement="Alpha knowledge statement."),))
    identifier = registry.knowledge_ids()[0]
    graph = KnowledgeIntelligenceGraph(
        registry,
        RelationshipSet((Relationship("UKID-ABSENT", identifier, RelationType.DEPENDS_ON),)),
    )
    resolved = graph.blast_radius("UKID-ABSENT")
    assert resolved["affected"] == []
    assert resolved["by_authority"] == {}

    unresolved = graph.blast_radius(identifier)
    assert unresolved["affected"] == ["UKID-ABSENT"]
    assert unresolved["affected_count"] == 1
    assert unresolved["by_authority"] == {}


# -- projections ----------------------------------------------------------------------


def test_every_declared_projection_is_counted_and_the_names_are_sorted():
    assert PROJECTION_NAMES == tuple(sorted(PROJECTIONS))


def test_a_projection_returns_relationships_and_never_a_second_graph(graph):
    dependency = graph.projection("dependency")
    assert len(dependency) == 1
    assert all(r.relation in PROJECTIONS["dependency"] for r in dependency)
    assert not isinstance(dependency, KnowledgeIntelligenceGraph)
    counts = graph.projection_counts()
    assert set(counts) == set(PROJECTION_NAMES)
    assert counts["dependency"] == 1
    assert counts["conflict"] == 0


def test_an_undeclared_projection_is_refused_rather_than_returned_empty(graph):
    with pytest.raises(KeyError):
        graph.projection("not-a-projection")


def test_the_governance_projection_collects_the_relations_it_declares():
    governed = make_unit("g", statement="Governed knowledge statement.")
    governor = make_unit(
        "h",
        statement="Governing knowledge statement.",
        relations=(RelationDeclaration(RelationType.GOVERNS, "g"),),
    )
    graph = build_graph(register((governed, governor)))
    assert len(graph.projection("governance")) == 1
    assert graph.projection_counts()["governance"] == 1


# -- subgraph -------------------------------------------------------------------------


def test_a_subgraph_keeps_only_the_named_records_and_the_edges_among_them(graph):
    a, b = _by_title(graph, "Title a"), _by_title(graph, "Title b")
    restricted = graph.subgraph([a, b])
    assert restricted.node_ids() == tuple(sorted((a, b)))
    assert len(restricted.edges()) == 1
    assert restricted.unresolved() == ()


def test_a_subgraph_that_drops_an_endpoint_drops_the_edge_rather_than_dangling_it(graph):
    b = _by_title(graph, "Title b")
    restricted = graph.subgraph([b])
    assert restricted.node_ids() == (b,)
    assert len(restricted.edges()) == 0
    assert restricted.unresolved() == ()


# -- integrity ------------------------------------------------------------------------


def test_an_edge_whose_endpoint_has_no_record_is_reported_as_unresolved():
    """The one condition the graph declares must be empty for a graph to be valid.

    It is forged rather than waited for: :func:`build_relationships` resolves against the
    registry and cannot produce one, so the only way to show the check firing is to hand
    the graph a relationship set the resolver would never have built.
    """
    registry = register((make_unit("a", statement="Alpha knowledge statement."),))
    identifier = registry.knowledge_ids()[0]
    graph = KnowledgeIntelligenceGraph(
        registry,
        RelationshipSet(
            (
                Relationship(identifier, "UKID-MISSING-TARGET", RelationType.DEPENDS_ON),
                Relationship("UKID-MISSING-SOURCE", identifier, RelationType.DEPENDS_ON),
            )
        ),
    )
    assert graph.unresolved() == ("UKID-MISSING-SOURCE", "UKID-MISSING-TARGET")
    assert graph.counts()["unresolved"] == 2


def test_counts_summarise_the_graph(graph):
    assert graph.counts() == {
        "nodes": 3,
        "edges": 1,
        "isolated": 1,
        "single_sourced": 3,
        "unresolved": 0,
    }


def test_the_seal_is_content_addressed_and_moves_only_with_the_graph(graph, simple_registry):
    seal = graph.seal()
    assert len(seal) == 64
    assert build_graph(simple_registry).seal() == seal
    assert graph.subgraph(graph.node_ids()[:1]).seal() != seal


def test_to_dict_carries_every_derived_view_and_nothing_else(graph):
    payload = graph.to_dict()
    assert set(payload) == {
        "counts",
        "seal",
        "provider_contribution",
        "projections",
        "nodes",
        "edges",
        "unresolved",
    }
    assert payload["counts"] == graph.counts()
    assert payload["seal"] == graph.seal()
    assert len(payload["nodes"]) == 3
    assert len(payload["edges"]) == 1
    assert payload["unresolved"] == []


# -- construction ---------------------------------------------------------------------


def test_composition_admits_derived_relationships_the_asserted_set_does_not_hold():
    first = make_unit("a", statement="Alpha knowledge statement.")
    second = make_unit(
        "b",
        statement="Beta knowledge statement.",
        relations=(RelationDeclaration(RelationType.DEPENDS_ON, "a"),),
    )
    third = make_unit(
        "c",
        statement="Gamma knowledge statement.",
        relations=(RelationDeclaration(RelationType.DEPENDS_ON, "b"),),
    )
    registry = register((first, second, third))
    plain = build_graph(registry)
    composed = build_graph(registry, compose=True)
    assert len(composed.relationships) > len(plain.relationships)
    assert any(r.derived for r in composed.relationships)
    assert composed.node_ids() == plain.node_ids()


def test_from_registry_and_build_graph_are_the_same_construction(simple_registry):
    assert (
        KnowledgeIntelligenceGraph.from_registry(simple_registry).seal()
        == build_graph(simple_registry).seal()
    )
