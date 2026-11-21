"""UCXI-000001 Parts 09/10 — context graph and context runtime tests.

The graph must agree with the registry by construction and detect the structural faults
the registry cannot see on its own. The runtime must bound execution: activation is
scoped, nesting may narrow but never widen, propagation is explicit, and activation
identity is deterministic so a runtime trace is comparable across runs.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.context.composition import compose
from engine.context.errors import ContextGraphError, ContextRuntimeError
from engine.context.graph import (
    NODE_CONTEXT,
    NODE_TAXON,
    TAXON_PARENT,
    ContextGraph,
    build_context_graph,
)
from engine.context.registry import ContextRegistry
from engine.context.runtime import (
    ContextRuntime,
    _reachable_frames,
    activate,
    current,
    current_context,
    require,
    value,
)
from engine.context.taxonomy import ContextKind, ContextRelation
from engine.graph.model import Edge, KnowledgeGraph, Node
from engine.tests.context.conftest import declaration, spatial_values

# -------------------------------------------------------------------------- graph


def test_graph_projects_contexts_and_taxa(universal_registry: ContextRegistry) -> None:
    graph = build_context_graph(universal_registry)
    assert len(graph.contexts()) == 16
    assert len(graph.taxa()) == 17
    assert graph.order() == 33
    assert graph.size() == 32  # 16 taxon-parent edges + 16 classified-as edges
    assert TAXON_PARENT in graph.graph.edge_types()
    assert graph.validate() == []
    assert graph.summary()["valid"] is True
    assert graph.seal() == build_context_graph(universal_registry).seal()
    assert graph.node(graph.contexts()[0]).kind == NODE_CONTEXT
    assert graph.node(graph.taxa()[0]).kind == NODE_TAXON


def test_every_context_is_classified(universal_registry: ContextRegistry) -> None:
    graph = build_context_graph(universal_registry)
    assert graph.unclassified() == ()
    temporal = universal_registry.by_kind(ContextKind.TEMPORAL)[0]
    assert graph.taxon_of(temporal.context_id) == "CTX-TEMPORAL"
    assert graph.by_kind("temporal") == (temporal.context_id,)
    assert graph.by_kind("quantum") == ()


def test_graph_navigation_over_declared_relations(empty_registry: ContextRegistry) -> None:
    outer = empty_registry.register(
        declaration(kind=ContextKind.SPATIAL, natural_key="outer", values=spatial_values())
    )
    inner = empty_registry.register(declaration(natural_key="inner", parent=outer.context_id))
    governance = empty_registry.register(
        declaration(
            kind=ContextKind.GOVERNANCE,
            natural_key="gov",
            values={"authority": "a", "policy": "p", "decision_rights": "d"},
        )
    )
    observer = empty_registry.register(
        declaration(
            kind=ContextKind.OBSERVER,
            natural_key="obs",
            values={"observer_id": "o", "vantage": "v", "epistemic_access": "e"},
        )
    )
    empty_registry.relate(ContextRelation.DEPENDS_ON, inner.context_id, governance.context_id)
    empty_registry.relate(ContextRelation.CONSTRAINS, governance.context_id, inner.context_id)
    empty_registry.relate(ContextRelation.OBSERVES, observer.context_id, inner.context_id)
    empty_registry.relate(ContextRelation.FEDERATES, inner.context_id, observer.context_id)

    graph = build_context_graph(empty_registry)
    assert graph.contains(outer.context_id) == (inner.context_id,)
    assert graph.contained_by(inner.context_id) == (outer.context_id,)
    assert graph.dependencies_of(inner.context_id) == (governance.context_id,)
    assert graph.dependents_of(governance.context_id) == (inner.context_id,)
    assert graph.transitive_dependencies(inner.context_id) == (governance.context_id,)
    assert graph.impact_of(governance.context_id) == (inner.context_id,)
    assert graph.blast_radius(governance.context_id) == 1
    assert graph.constrained_by(inner.context_id) == (governance.context_id,)
    assert graph.observed_by(inner.context_id) == (observer.context_id,)
    assert graph.federated_from(inner.context_id) == (observer.context_id,)
    assert graph.path(inner.context_id, governance.context_id) == (
        inner.context_id,
        governance.context_id,
    )
    assert graph.path(governance.context_id, "UCOS-CTX-000000000000") == ()
    assert graph.path(governance.context_id, outer.context_id) == ()
    order = graph.order_of_resolution()
    assert order.index(governance.context_id) < order.index(inner.context_id)


def test_supersession_is_navigable(empty_registry: ContextRegistry) -> None:
    original = empty_registry.register(declaration(natural_key="v1"))
    successor = empty_registry.supersede(
        original.context_id,
        declaration(
            natural_key="v2",
            values={"reference_frame": "new", "ordering": "a", "resolution": "b"},
        ),
    )
    graph = build_context_graph(empty_registry)
    assert graph.superseded_by(original.context_id) == (successor.context_id,)


def test_graph_detects_cycles_unclassified_and_dangling_edges() -> None:
    registry = ContextRegistry()
    substrate = KnowledgeGraph()
    substrate.add_node(Node(node_id="A", kind=NODE_CONTEXT, attributes={"context_kind": "x"}))
    substrate.add_node(Node(node_id="B", kind=NODE_CONTEXT, attributes={"context_kind": "x"}))
    substrate.add_edge(
        Edge(edge_id="E1", source="A", target="B", type=ContextRelation.CONTAINS.value)
    )
    substrate.add_edge(
        Edge(edge_id="E2", source="B", target="A", type=ContextRelation.CONTAINS.value)
    )
    substrate.add_edge(
        Edge(edge_id="E3", source="A", target="GHOST", type=ContextRelation.DEPENDS_ON.value)
    )
    graph = ContextGraph(substrate, registry)
    findings = graph.validate()
    assert any("cycle" in finding for finding in findings)
    assert any("unclassified" in finding for finding in findings)
    assert any("outside the graph" in finding for finding in findings)
    assert graph.cycles()[ContextRelation.CONTAINS.value]
    assert graph.dangling() == ("E3",)
    with pytest.raises(ContextGraphError):
        graph.require_valid()


def test_orphan_detection() -> None:
    substrate = KnowledgeGraph()
    substrate.add_node(Node(node_id="LONE", kind=NODE_CONTEXT))
    graph = ContextGraph(substrate, ContextRegistry())
    assert graph.orphans() == ("LONE",)


def test_require_valid_passes_on_a_clean_graph(universal_registry: ContextRegistry) -> None:
    build_context_graph(universal_registry).require_valid()


# ------------------------------------------------------------------------ runtime


def test_activation_is_scoped_and_released(composed: object) -> None:
    runtime = ContextRuntime()
    assert runtime.current() is None
    assert not runtime.is_active()
    with runtime.activate(composed) as activation:  # type: ignore[arg-type]
        assert runtime.is_active()
        assert runtime.depth() == 1
        assert runtime.current() == activation
        assert runtime.current_context() is composed
        assert runtime.frames() == ("ucos-universal",)
        assert activation.activation_id.startswith("CTXA-")
        assert activation.depth == 0
        assert activation.parent is None
        assert runtime.trace()["depth"] == 1
    assert runtime.current() is None
    assert runtime.snapshot() == ()


def test_activation_identity_is_deterministic(composed: object) -> None:
    runtime = ContextRuntime()
    with runtime.activate(composed) as first:  # type: ignore[arg-type]
        first_id = first.activation_id
    with runtime.activate(composed) as second:  # type: ignore[arg-type]
        assert second.activation_id == first_id


def test_reads_flow_through_the_active_context(composed: object) -> None:
    runtime = ContextRuntime()
    assert runtime.value("temporal", "ordering") is None
    with runtime.activate(composed):  # type: ignore[arg-type]
        assert runtime.value("temporal", "ordering")
        assert runtime.require("temporal", "ordering")
        assert runtime.provenance("temporal", "ordering") == "engine/determinism/reproduce.py"
        assert runtime.provenance("temporal", "absent") is None
        assert runtime.provenance("quantum", "absent") is None
        with pytest.raises(ContextRuntimeError):
            runtime.require("temporal", "absent")
        assert runtime.require_active() is composed


def test_require_active_fails_closed_when_nothing_is_active() -> None:
    with pytest.raises(ContextRuntimeError):
        ContextRuntime().require_active()


def test_nesting_may_narrow_but_not_widen(universal_registry: ContextRegistry) -> None:
    runtime = ContextRuntime()
    outer = compose(universal_registry)
    narrower = compose(universal_registry, context_ids=[outer.members[0]])
    with runtime.activate(outer):
        with runtime.activate(narrower) as inner:
            assert inner.depth == 1
            assert inner.parent is not None
            assert runtime.depth() == 2

    other = ContextRegistry()
    other.register(declaration(boundary="unrelated-frame"))
    unrelated = compose(other)
    with runtime.activate(outer), pytest.raises(ContextRuntimeError):
        with runtime.activate(unrelated):
            pass  # pragma: no cover - the activation is refused before the body runs


def test_federated_frames_may_be_activated(empty_registry: ContextRegistry) -> None:
    here = empty_registry.register(declaration(natural_key="here", boundary="frame-a"))
    there = empty_registry.register(
        declaration(
            kind=ContextKind.SPATIAL,
            natural_key="there",
            boundary="frame-b",
            values=spatial_values(),
        )
    )
    empty_registry.relate(ContextRelation.DEPENDS_ON, here.context_id, there.context_id)
    empty_registry.relate(ContextRelation.FEDERATES, here.context_id, there.context_id)
    outer = compose(empty_registry)
    inner = compose(empty_registry, context_ids=[there.context_id])
    runtime = ContextRuntime()
    with runtime.activate(outer), runtime.activate(inner) as activation:
        assert activation.frames == ("frame-b",)
        assert runtime.can_reference(here.context_id, there.context_id) is False


def test_binding_can_require_the_universal_set(universal_registry: ContextRegistry) -> None:
    runtime = ContextRuntime()
    composed = compose(universal_registry)
    assert runtime.bind(composed, require_universal=True).depth == 0

    partial = compose(universal_registry, context_ids=[composed.members[0]])
    with pytest.raises(ContextRuntimeError):
        runtime.bind(partial, require_universal=True)


def test_snapshot_and_restore_reestablish_the_stack(universal_registry: ContextRegistry) -> None:
    runtime = ContextRuntime()
    outer = compose(universal_registry)
    inner = compose(universal_registry, context_ids=[outer.members[0]])
    with runtime.activate(outer), runtime.activate(inner):
        snapshot = runtime.snapshot()
    assert len(snapshot) == 2
    assert runtime.current() is None
    with runtime.restore(snapshot) as activations:
        assert len(activations) == 2
        assert runtime.depth() == 2
    with runtime.restore(()) as nothing:
        assert nothing == ()


def test_module_level_helpers(composed: object) -> None:
    assert current() is None
    assert current_context() is None
    assert value("temporal", "ordering") is None
    with activate(composed) as activation:  # type: ignore[arg-type]
        assert current() == activation
        assert current_context() is composed
        assert value("temporal", "ordering")
        assert require("temporal", "ordering")


def test_can_reference_without_an_active_context() -> None:
    assert ContextRuntime().can_reference("a", "b") is False


def test_reachability_visits_a_shared_node_once_and_never_returns_to_its_origin(
    universal_registry: ContextRegistry,
) -> None:
    """TWO GUARDS, TWO DIFFERENT LOOPS, and a well-formed context set trips neither.

    ``current in seen`` is what stops a DIAMOND — two contexts depending on one shared
    context — from being walked twice; ``current == start`` is what stops a CYCLE from
    putting a context into its own blast radius, which would make every context in a cycle
    report itself as something a change to itself would reach.
    """
    records = universal_registry.records()
    top, left, right, shared = (r.context_id for r in records[:4])
    for source, target in ((top, left), (top, right), (left, shared), (right, shared)):
        universal_registry.relate(relation=ContextRelation.DEPENDS_ON, source=source, target=target)

    graph = build_context_graph(universal_registry)
    reached = graph.impact_of(shared)

    assert set(reached) >= {top, left, right}
    assert len(reached) == len(set(reached))
    assert shared not in reached, "a context reached itself"


def test_activating_a_composition_with_no_members_is_refused(
    universal_registry: ContextRegistry,
) -> None:
    """AN EMPTY COMPOSITION ADMITS EVERYTHING. Every admissibility question below this one —
    universal coverage, isolation, frame binding — is vacuously true over no members, so an
    empty activation would report a fully covered runtime that carries no context at all."""

    composed = compose(universal_registry)
    empty = dataclasses.replace(composed, members=())

    # ``activate`` is a context manager, so the refusal happens on entry; ``bind`` is the
    # same admissibility check without the block, and both must refuse.
    with pytest.raises(ContextRuntimeError, match="cannot activate an empty composition"):
        ContextRuntime().bind(empty)
    with pytest.raises(ContextRuntimeError, match="cannot activate an empty composition"):
        with ContextRuntime().activate(empty):
            pass


def test_a_federated_target_outside_the_composition_widens_no_frame(
    universal_registry: ContextRegistry,
) -> None:
    """A FEDERATION MAY ONLY WIDEN INTO A FRAME THE COMPOSITION ACTUALLY HOLDS.

    ``_reachable_frames`` is what bounds where an active composition may narrow to, and it is
    built by resolving each federated target to its frame. A target the composition does not
    carry resolves to nothing, and adding that nothing would put ``None`` into the reachable
    set — after which every frame comparison against it would be a comparison with a value
    that is not a frame. The target is skipped, so the bound stays a set of real frames.
    """

    composed = compose(universal_registry)
    frame = composed.reference_frames[0]
    assert composed.frame_of("UCOS-CTX-not-in-this-composition") is None

    widened = dataclasses.replace(
        composed,
        reference_frames=(
            dataclasses.replace(
                frame, federated=("UCOS-CTX-not-in-this-composition", frame.universe_id)
            ),
            *composed.reference_frames[1:],
        ),
    )
    reachable = _reachable_frames(widened)

    assert None not in reachable
    assert frame.context_id in reachable
