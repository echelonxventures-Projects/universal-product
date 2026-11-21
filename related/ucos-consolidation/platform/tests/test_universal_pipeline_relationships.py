"""UAPF-000001 — tests for the event engine and the dependency/relationship engine.

Two claims are under test. First, that UAPF adds no second event substrate: the bus is a
category-guarded façade over the canonical Merkle-linked DAG, so branch/merge are first-class
and history is tamper-evident and append-only. Second, that the dependency graph and the impact
graph are one edge set read from two ends, so they cannot disagree — and that declaration order
never affects validity, while closure honesty is still enforced at use.
"""

from __future__ import annotations

from platform.universal_pipeline.dependencies import DependencyClosure, DependencyManager
from platform.universal_pipeline.errors import PipelineDependencyError, PipelineEventError
from platform.universal_pipeline.events import (
    EVENT_SOURCE,
    SEED_EVENT_CATEGORIES,
    PipelineEventBus,
    event_categories,
    event_category_description,
    register_event_category,
    require_event_category,
)

import pytest

CATEGORY = "uapf.pipeline.registered"
OTHER = "uapf.queue.enqueued"


# --------------------------------------------------------------------------- event engine


def test_every_seeded_event_category_is_registered_with_its_description() -> None:
    registered = set(event_categories())
    for category, description in SEED_EVENT_CATEGORIES:
        assert category in registered
        assert event_category_description(category) == description
    assert EVENT_SOURCE == "UAPF-000001"


def test_categories_are_open_by_registration_and_append_only() -> None:
    register_event_category("test.category.admitted", "admitted by a test")
    require_event_category("test.category.admitted")
    with pytest.raises(PipelineEventError, match="already registered"):
        register_event_category("test.category.admitted")


def test_emitting_an_unregistered_category_fails_closed() -> None:
    bus = PipelineEventBus()
    with pytest.raises(PipelineEventError, match="unregistered term"):
        bus.emit("uapf.never.registered", "subject")
    with pytest.raises(PipelineEventError, match="unregistered term"):
        bus.events_of("uapf.never.registered")


def test_bus_records_a_linear_chain_when_no_parents_are_named() -> None:
    bus = PipelineEventBus()
    first = bus.emit(CATEGORY, "p", payload={"v": "1.0.0"})
    second = bus.emit(OTHER, "u1")
    assert len(bus) == 2
    assert second.parents == (first.event_hash,)
    assert bus.heads == (second.event_hash,)
    assert bus.events == (first, second)
    assert bus.events_of(CATEGORY) == (first,)
    assert bus.events_about("u1") == (second,)
    assert bus.categories_recorded() == tuple(sorted({CATEGORY, OTHER}))
    assert bus.verify()
    bus.require_intact()


def test_divergence_and_convergence_are_first_class() -> None:
    bus = PipelineEventBus()
    root = bus.emit(CATEGORY, "p")
    left = bus.emit(OTHER, "u1")
    right = bus.branch(root.event_hash, "uapf.queue.promoted", "u2")
    assert len(bus.heads) == 2
    # With the DAG diverged, a plain append is ambiguous and must fail rather than guess.
    with pytest.raises(PipelineEventError, match="could not be recorded"):
        bus.emit(OTHER, "u3")
    merged = bus.merge([left.event_hash, right.event_hash], "uapf.orchestration.tick", "tick-0")
    assert set(merged.parents) == {left.event_hash, right.event_hash}
    assert bus.heads == (merged.event_hash,)
    bus.require_intact()


def test_branch_and_merge_fail_closed_on_dangling_or_insufficient_parents() -> None:
    bus = PipelineEventBus()
    root = bus.emit(CATEGORY, "p")
    with pytest.raises(PipelineEventError, match="branch refused"):
        bus.branch("0" * 64, OTHER, "u1")
    with pytest.raises(PipelineEventError, match="merge refused"):
        bus.merge([root.event_hash], OTHER, "u1")
    with pytest.raises(PipelineEventError, match="unregistered term"):
        bus.branch(root.event_hash, "uapf.unknown", "u1")
    with pytest.raises(PipelineEventError, match="unregistered term"):
        bus.merge([root.event_hash], "uapf.unknown", "u1")


def test_recording_the_same_event_twice_is_idempotent() -> None:
    bus = PipelineEventBus()
    root = bus.emit(CATEGORY, "p")
    again = bus.emit(CATEGORY, "p", parents=())
    assert again.event_hash == root.event_hash
    assert len(bus) == 1


def test_identical_emission_sequences_produce_identical_recorded_history() -> None:
    def build() -> PipelineEventBus:
        bus = PipelineEventBus()
        bus.emit(CATEGORY, "p", payload={"v": "1.0.0"})
        bus.emit(OTHER, "u1", payload={"wave": 1})
        return bus

    left, right = build(), build()
    assert left.fingerprint() == right.fingerprint()
    assert left.export() == right.export()
    assert left.to_dict()["event_count"] == 2
    assert left.to_dict()["fingerprint"] == left.fingerprint()


def test_bus_validates_its_own_construction_and_subjects() -> None:
    with pytest.raises(PipelineEventError, match="event source is required"):
        PipelineEventBus(source="")
    bus = PipelineEventBus(source="TEST-SOURCE")
    assert bus.source == "TEST-SOURCE"
    with pytest.raises(PipelineEventError, match="subject must be a string"):
        bus.emit(CATEGORY, 7)  # type: ignore[arg-type]


# ---------------------------------------------------------------------- dependency engine


def _manager() -> DependencyManager:
    manager = DependencyManager()
    manager.declare("leaf")
    manager.declare("middle", ["leaf"])
    manager.declare("top", ["middle", "leaf"])
    manager.declare("standalone")
    return manager


def test_declaration_is_order_independent_and_deduplicated() -> None:
    forward = DependencyManager()
    forward.declare("a")
    forward.declare("b", ["a"])
    backward = DependencyManager()
    backward.declare("b", ["a", "a"])
    backward.declare("a")
    assert forward.order() == backward.order()
    assert backward.dependencies_of("b") == ("a",)


def test_derived_order_places_every_node_after_what_it_requires() -> None:
    manager = _manager()
    order = manager.order()
    assert order.index("leaf") < order.index("middle") < order.index("top")
    assert set(order) == {"leaf", "middle", "top", "standalone"}
    assert manager.node_ids == ("leaf", "middle", "standalone", "top")
    assert manager.edge_count == 3
    assert len(manager) == 4
    assert "leaf" in manager
    assert not manager.has_cycle()


def test_closure_and_impact_are_one_edge_set_read_from_two_ends() -> None:
    manager = _manager()
    closure = manager.closure("top")
    assert closure.direct == ("leaf", "middle")
    assert closure.transitive == ("leaf", "middle")
    assert closure.order == ("leaf", "middle", "top")
    assert closure.depth == 2
    assert closure.is_closed
    assert closure.identity.kind == "dependency-closure"
    assert closure.fingerprint() == manager.closure("top").fingerprint()
    # Backward reading of the same edges.
    assert manager.impact("leaf") == ("middle", "top")
    assert manager.impact("top") == ()
    assert manager.dependents_of("leaf") == ("middle", "top")
    # A root's closure is itself.
    assert manager.closure("leaf").transitive == ()
    assert manager.closure("leaf").depth == 0


def test_roots_leaves_and_orphans_are_reported_rather_than_implied() -> None:
    manager = _manager()
    assert manager.roots() == ("leaf", "standalone")
    assert manager.leaves() == ("standalone", "top")
    assert manager.orphans() == ("standalone",)
    assert manager.unresolved_edges() == ()


def test_an_edge_may_name_an_undeclared_node_but_use_fails_closed() -> None:
    manager = DependencyManager()
    manager.declare("x", ["not-yet-declared"])
    # Declaring is permitted — catalogue order is not meaningful.
    assert manager.unresolved_edges() == (("x", "not-yet-declared"),)
    for act in (manager.validate, manager.order, manager.has_cycle):
        with pytest.raises(PipelineDependencyError):
            act()
    with pytest.raises(PipelineDependencyError, match="not valid"):
        manager.closure("x")
    # Declaring the missing node resolves it, with no re-declaration of x.
    manager.declare("not-yet-declared")
    assert manager.order() == ("not-yet-declared", "x")


def test_a_cycle_is_reported_with_the_nodes_that_could_not_be_placed() -> None:
    manager = DependencyManager()
    manager.declare("p", ["q"])
    manager.declare("q", ["p"])
    with pytest.raises(PipelineDependencyError, match="not valid") as raised:
        manager.order()
    assert raised.value.context["detail"]["unresolved"] == ["p", "q"]
    assert manager.has_cycle() is True


def test_declaration_is_validated_and_single() -> None:
    manager = DependencyManager()
    manager.declare("a")
    with pytest.raises(PipelineDependencyError, match="already declared"):
        manager.declare("a")
    with pytest.raises(PipelineDependencyError, match="node id is required"):
        manager.declare("")
    with pytest.raises(PipelineDependencyError, match="cannot depend on itself"):
        manager.declare("b", ["b"])
    with pytest.raises(PipelineDependencyError, match="non-empty strings"):
        manager.declare("c", [""])
    with pytest.raises(PipelineDependencyError, match="no such dependency node"):
        manager.dependencies_of("absent")
    with pytest.raises(PipelineDependencyError, match="no such dependency node"):
        manager.closure("absent")


def test_dependents_of_an_undeclared_node_is_still_answerable() -> None:
    """An edge may name a node a catalogue has not reached; asking who points at it is valid."""
    manager = DependencyManager()
    manager.declare("x", ["future"])
    assert manager.dependents_of("future") == ("x",)


def test_graph_evidence_is_deterministic() -> None:
    left, right = _manager(), _manager()
    assert left.fingerprint() == right.fingerprint()
    rendered = left.to_dict()
    assert rendered["node_count"] == 4
    assert rendered["edge_count"] == 3
    assert rendered["orphans"] == ["standalone"]
    assert [node["node_id"] for node in rendered["nodes"]] == list(left.node_ids)


def test_closure_validates_its_own_shape() -> None:
    with pytest.raises(PipelineDependencyError, match="closure node id is required"):
        DependencyClosure(node_id="", direct=(), transitive=(), order=(), depth=0)
    with pytest.raises(PipelineDependencyError, match="depth must be non-negative"):
        DependencyClosure(node_id="a", direct=(), transitive=(), order=(), depth=-1)


def test_a_mutated_event_makes_the_bus_refuse_rather_than_report_a_boolean() -> None:
    """RECORDED TRUTH IS TAMPER-EVIDENT, and the bus has two ways of saying so.

    ``verify()`` answers a boolean and had a test; ``require_intact()`` is the fail-closed
    form and its translation arm had none. The canonical ledger raises ``DagLedgerError``,
    which names the DAG rather than the framework — so it is re-raised as a
    ``PipelineEventError`` carrying the ledger's own reason, and a caller catching UAPF's
    error class does not have to also know which substrate happens to be underneath.

    The mutation is made directly on the recorded event because no API can make it: every
    write path recomputes the Merkle hash, which is exactly the property under test.
    """
    bus = PipelineEventBus()
    bus.emit(CATEGORY, "subject-a", payload={"declared": True})
    bus.emit(OTHER, "subject-b")

    assert bus.verify() is True
    bus.require_intact()

    recorded = bus.events[0]
    object.__setattr__(recorded, "payload", {"declared": False})

    assert bus.verify() is False
    with pytest.raises(PipelineEventError, match="recorded event history is not intact") as excinfo:
        bus.require_intact()
    assert "integrity check failed" in excinfo.value.context["reason"]


def test_depth_terminates_on_a_graph_that_closure_would_refuse() -> None:
    """DECLARATION ORDER INDEPENDENCE MEANS A CYCLE CAN BE DECLARED, and ``_depth`` is the
    one traversal in this module written by hand rather than delegated.

    ``closure`` validates before measuring depth, so on every path a caller can take the
    recursion guard is unreachable — which is precisely why it had never run. It is what
    stops a directly measured cyclic node from recursing until the interpreter's stack is
    gone: re-entering a node already on the current path contributes no new chain, so the
    walk returns 0 for it and the answer stays finite.
    """
    manager = DependencyManager()
    manager.declare("a", ["b"])
    manager.declare("b", ["a"])

    assert manager.has_cycle() is True
    with pytest.raises(PipelineDependencyError):
        manager.closure("a")

    # The chain a → b → (a, already visiting) is two edges long and then stops.
    assert manager._depth("a") == 2
