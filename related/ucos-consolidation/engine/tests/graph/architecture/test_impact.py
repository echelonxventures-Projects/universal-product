"""Tests for engine.graph.architecture.impact.

Proves: ImpactPrediction serialises correctly; ArchitectureImpactEngine
predict() covers known/unknown/empty change sets; risk score; severity bands;
capabilities_disrupted; blast_radius delegation; summary.
"""

from __future__ import annotations

from engine.graph.architecture.impact import ArchitectureImpactEngine, ImpactPrediction
from engine.graph.architecture.layers import LayerDependencyGraph
from engine.graph.model import KIND_ARTIFACT, Edge, KnowledgeGraph, Node
from engine.graph.projections import ImpactGraph


def _artifact(nid: str, **attrs) -> Node:
    return Node(nid, KIND_ARTIFACT, attributes=attrs)


def _depends(eid: str, src: str, tgt: str) -> Edge:
    return Edge(eid, src, tgt, "Depends-On")


def _consumes(eid: str, src: str, tgt: str) -> Edge:
    return Edge(eid, src, tgt, "Consumes")


# --- ImpactPrediction.to_dict --------------------------------------------------


def test_prediction_to_dict():
    p = ImpactPrediction(
        change_set=("A",),
        known=("A",),
        unknown=(),
        impacted=("B", "C"),
        ranked=(("B", 1), ("C", 2)),
        layers=("platform",),
        capabilities_disrupted=(),
        certified_impacted=(),
        max_depth=2,
        risk_score=5,
        severity="LOW",
    )
    d = p.to_dict()
    assert d["change_set"] == ["A"]
    assert d["known"] == ["A"]
    assert d["unknown"] == []
    assert d["impacted"] == ["B", "C"]
    assert d["ranked"] == [{"node": "B", "distance": 1}, {"node": "C", "distance": 2}]
    assert d["risk_score"] == 5
    assert d["severity"] == "LOW"


# --- ArchitectureImpactEngine: empty graph -------------------------------------


def test_empty_graph_predict():
    engine = ArchitectureImpactEngine(KnowledgeGraph())
    pred = engine.predict(["X"])
    assert pred.unknown == ("X",)
    assert pred.impacted == ()
    assert pred.severity == "NONE"
    assert pred.risk_score == 0


# --- ArchitectureImpactEngine: change set with known/unknown -------------------


def test_predict_distinguishes_known_unknown():
    nodes = [_artifact(n) for n in ("A", "B")]
    g = KnowledgeGraph(nodes, [])
    engine = ArchitectureImpactEngine(g)
    pred = engine.predict(["A", "GHOST"])
    assert "A" in pred.known
    assert "GHOST" in pred.unknown


def test_predict_empty_change_set():
    nodes = [_artifact(n) for n in ("A", "B")]
    g = KnowledgeGraph(nodes, [])
    engine = ArchitectureImpactEngine(g)
    pred = engine.predict([])
    assert pred.change_set == ()
    assert pred.impacted == ()


# --- ArchitectureImpactEngine: connected graph --------------------------------


def test_predict_downstream_impacted():
    # A Depends-On B  => B Affects A
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "A", "C")]
    g = KnowledgeGraph(nodes, edges)
    engine = ArchitectureImpactEngine(g)
    # changing B should affect A
    pred = engine.predict(["B"])
    assert "A" in pred.impacted


def test_predict_ranked_nearest_first():
    # A -> B -> C (Depends-On); changing C affects B then A
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "B", "C")]
    g = KnowledgeGraph(nodes, edges)
    engine = ArchitectureImpactEngine(g)
    pred = engine.predict(["C"])
    if len(pred.ranked) >= 2:
        # nearest (shorter distance) should come first
        assert pred.ranked[0][1] <= pred.ranked[1][1]


def test_predict_certified_impacted():
    nodes = [_artifact("BASE"), _artifact("DEP", status="CERTIFIED")]
    edges = [_depends("E1", "DEP", "BASE")]
    g = KnowledgeGraph(nodes, edges)
    engine = ArchitectureImpactEngine(g)
    pred = engine.predict(["BASE"])
    assert "DEP" in pred.certified_impacted


# --- capabilities_disrupted ---------------------------------------------------


def test_capabilities_disrupted():
    """Artifacts that Consumes a changed source are reported."""
    nodes = [_artifact(n) for n in ("PROVIDER", "CONSUMER")]
    edges = [_consumes("E1", "CONSUMER", "PROVIDER")]
    g = KnowledgeGraph(nodes, edges)
    engine = ArchitectureImpactEngine(g)
    pred = engine.predict(["PROVIDER"])
    assert "CONSUMER" in pred.capabilities_disrupted


# --- severity bands -----------------------------------------------------------


def test_severity_none():
    assert ArchitectureImpactEngine._severity(0) == "NONE"


def test_severity_low():
    assert ArchitectureImpactEngine._severity(5) == "LOW"


def test_severity_medium():
    assert ArchitectureImpactEngine._severity(20) == "MEDIUM"


def test_severity_high():
    assert ArchitectureImpactEngine._severity(50) == "HIGH"


def test_severity_critical():
    assert ArchitectureImpactEngine._severity(80) == "CRITICAL"


# --- blast_radius delegation --------------------------------------------------


def test_blast_radius_method(core):
    engine = ArchitectureImpactEngine(core)
    result = engine.blast_radius("UCOS-CON-000001")
    assert "subject" in result
    assert "radius" in result


# --- summary ------------------------------------------------------------------


def test_summary(core):
    engine = ArchitectureImpactEngine(core)
    s = engine.summary()
    assert "impactable_nodes" in s
    assert "blast_radius" in s


def test_summary_empty():
    engine = ArchitectureImpactEngine(KnowledgeGraph())
    s = engine.summary()
    assert s["impactable_nodes"] == 0


# --- prebuilt impact/layers injection -----------------------------------------


def test_accepts_prebuilt_impact_and_layers(core):
    impact = ImpactGraph(core)
    layers = LayerDependencyGraph(core)
    engine = ArchitectureImpactEngine(core, impact=impact, layers=layers)
    pred = engine.predict(["UCOS-CON-000001"])
    assert isinstance(pred, ImpactPrediction)


def test_a_prediction_over_a_diamond_measures_each_node_once():
    """THE DISTANCE MAP IS WHAT MAKES THE TRAVERSAL TERMINATE AND THE DEPTH HONEST.

    A node reachable by two routes must keep the FIRST distance it was assigned — the
    breadth-first one, which is the shortest — and must not be re-queued. Without the guard
    the depth would be whichever route happened to arrive last and the work would compound
    at every level; on a cycle the walk would not terminate at all.
    """
    nodes = [_artifact(n) for n in ("A", "B", "C", "D")]
    edges = [
        _depends("E1", "B", "A"),
        _depends("E2", "C", "A"),
        _depends("E3", "D", "B"),
        _depends("E4", "D", "C"),
    ]
    graph = KnowledgeGraph(nodes, edges)
    prediction = ArchitectureImpactEngine(graph).predict(["A"])
    assert set(prediction.impacted) == {"B", "C", "D"}
    assert len(prediction.impacted) == len(set(prediction.impacted))


def test_an_impacted_node_the_layer_model_cannot_place_contributes_no_layer(monkeypatch):
    """A LAYER IS READ FROM THE ARTIFACT, and the guard is for a node that answers with none.

    ``layer_of`` never does today — a node with no category is placed in ``unclassified``,
    which is a real layer and the correct answer — so the skip has never fired. It is what
    stands between a future layer model that returns "" and a prediction reporting an extra
    "layer" affected: an empty string in the layer set, counted alongside real layers and
    growing with the graph's untidiness rather than with the blast radius.

    The node stays impacted either way; it simply contributes no layer.
    """

    placed = _artifact("CON-1", category="CON")
    unplaceable = _artifact("UNK-1")
    graph = KnowledgeGraph([placed, unplaceable], [_depends("E1", "UNK-1", "CON-1")])

    assert LayerDependencyGraph(graph).layer_of("UNK-1") == "unclassified"
    placed_layers = ArchitectureImpactEngine(graph).predict(["CON-1"]).layers
    assert placed_layers == ("unclassified",)

    monkeypatch.setattr(
        LayerDependencyGraph,
        "layer_of",
        lambda self, node_id: "" if node_id == "UNK-1" else "constitution",
    )
    prediction = ArchitectureImpactEngine(graph).predict(["CON-1"])

    assert "UNK-1" in prediction.impacted
    assert prediction.layers == (), "an unplaceable node contributed a layer anyway"
