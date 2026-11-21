"""Tests for engine.graph.architecture.engine.

Proves: ArchitectureIntelligenceEngine constructs with a pre-set adapter;
every lazy property memoises correctly; convenience methods delegate properly;
diagram() covers all three named models and rejects unknown names; build_all;
summary; register_contract.
"""

from __future__ import annotations

import pytest

from engine.foundation.contracts.contract import ContractRegistry
from engine.graph.adapter import KnowledgeGraphAdapter
from engine.graph.architecture.engine import (
    ARCHITECTURE_INTELLIGENCE_CONTRACT,
    DIAGRAM_NAMES,
    ArchitectureIntelligenceEngine,
)
from engine.graph.architecture.errors import UnknownEngineError

# Helpers -----------------------------------------------------------------------


def _engine(kg: KnowledgeGraphAdapter) -> ArchitectureIntelligenceEngine:
    return ArchitectureIntelligenceEngine(kg)


# --- construction --------------------------------------------------------------


def test_engine_constructs_with_kg(kg):
    engine = _engine(kg)
    assert engine.knowledge_graph is kg
    assert engine.core is kg.core


def test_engine_contract():
    engine = ArchitectureIntelligenceEngine.__new__(ArchitectureIntelligenceEngine)
    assert engine.contract is ARCHITECTURE_INTELLIGENCE_CONTRACT


def test_diagram_names_tuple():
    assert "layer" in DIAGRAM_NAMES
    assert "capability" in DIAGRAM_NAMES
    assert "condensation" in DIAGRAM_NAMES


# --- lazy memoised properties --------------------------------------------------


def test_dependency_memoised(kg):
    engine = _engine(kg)
    d1 = engine.dependency
    d2 = engine.dependency
    assert d1 is d2


def test_layers_memoised(kg):
    engine = _engine(kg)
    l1 = engine.layers
    l2 = engine.layers
    assert l1 is l2


def test_blast_radius_memoised(kg):
    engine = _engine(kg)
    b1 = engine.blast_radius
    b2 = engine.blast_radius
    assert b1 is b2


def test_critical_path_memoised(kg):
    engine = _engine(kg)
    c1 = engine.critical_path
    c2 = engine.critical_path
    assert c1 is c2


def test_impact_memoised(kg):
    engine = _engine(kg)
    i1 = engine.impact
    i2 = engine.impact
    assert i1 is i2


def test_reachability_memoised(kg):
    engine = _engine(kg)
    r1 = engine.reachability
    r2 = engine.reachability
    assert r1 is r2


# --- convenience methods -------------------------------------------------------


def test_analyze_blast_radius(kg):
    engine = _engine(kg)
    report = engine.analyze_blast_radius("UCOS-CON-000001")
    assert report.subject == "UCOS-CON-000001"


def test_analyze_critical_path(kg):
    engine = _engine(kg)
    report = engine.analyze_critical_path()
    assert hasattr(report, "length")


def test_predict_impact(kg):
    engine = _engine(kg)
    pred = engine.predict_impact(["UCOS-CON-000001"])
    assert hasattr(pred, "risk_score")


# --- diagram -------------------------------------------------------------------


def test_diagram_layer(kg):
    engine = _engine(kg)
    out = engine.diagram("layer")
    assert "layer-dependency" in out


def test_diagram_capability(kg):
    engine = _engine(kg)
    out = engine.diagram("capability", fmt="mermaid")
    assert "flowchart" in out


def test_diagram_condensation(kg):
    engine = _engine(kg)
    out = engine.diagram("condensation", fmt="dot")
    assert "digraph" in out


def test_diagram_unknown_raises(kg):
    engine = _engine(kg)
    with pytest.raises(UnknownEngineError):
        engine.diagram("unknown-diagram")


# --- insights ------------------------------------------------------------------


def test_insights_structure(kg):
    engine = _engine(kg)
    report = engine.insights(limit=3)
    assert "insights_version" in report
    assert "findings" in report
    assert "healthy" in report


# --- build_all -----------------------------------------------------------------


def test_build_all_populates_all_engines(kg):
    engine = _engine(kg)
    engine.build_all()
    assert engine._dependency is not None
    assert engine._layers is not None
    assert engine._blast is not None
    assert engine._critical is not None
    assert engine._impact is not None
    assert engine._reachability is not None


# --- summary -------------------------------------------------------------------


def test_summary_keys(kg):
    engine = _engine(kg)
    s = engine.summary()
    assert "contract" in s
    assert "provenance" in s
    assert "dependency_intelligence" in s
    assert "layer_intelligence" in s
    assert "critical_path" in s
    assert "blast_radius" in s


# --- register_contract --------------------------------------------------------


def test_register_contract(kg):
    engine = _engine(kg)
    registry = ContractRegistry()
    engine.register_contract(registry)
    registered = registry.get(ARCHITECTURE_INTELLIGENCE_CONTRACT.name)
    assert registered is not None


def test_the_engine_opens_over_the_default_corpus():
    """``open`` is the constructor every operational caller uses — the CLI, the evidence
    builder, anything that has a data directory rather than an adapter. Every test above
    constructs the engine from a prepared ``kg`` fixture instead, which left the one entry
    point a real invocation takes with no caller at all."""
    engine = ArchitectureIntelligenceEngine.open()

    assert engine.core.order() > 0
    assert engine.dependency is not None
