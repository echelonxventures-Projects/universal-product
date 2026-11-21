"""Contract + facade tests for engine.graph.adapter.KnowledgeGraphAdapter."""

from __future__ import annotations

from engine.foundation.contracts.contract import ContractRegistry, Version
from engine.graph.adapter import KNOWLEDGE_GRAPH_CONTRACT, emitted_kinds
from engine.graph.projections import (
    PROJECTION_NAMES,
    CapabilityGraph,
    CertificationGraph,
    DependencyGraph,
    EvidenceGraph,
    ImpactGraph,
    ImplementationGraph,
    OntologyGraph,
    RequirementGraph,
    TraceabilityGraph,
    ValidationGraph,
)


def test_contract_identity_and_registration(kg):
    assert KNOWLEDGE_GRAPH_CONTRACT.name == "knowledge.graph"
    assert KNOWLEDGE_GRAPH_CONTRACT.version == Version(1, 0, 0)
    assert kg.contract is KNOWLEDGE_GRAPH_CONTRACT
    registry = ContractRegistry()
    kg.register_contract(registry)
    assert registry.get("knowledge.graph").version == Version(1, 0, 0)


def test_core_and_aux_are_memoised(kg):
    assert kg.core is kg.core
    assert kg.signals is kg.signals
    assert kg.certification is kg.certification
    assert kg.twin is kg.twin


def test_projection_is_memoised(kg):
    dep1 = kg.projection("dependency")
    dep2 = kg.projection("dependency")
    assert dep1 is dep2


def test_typed_projection_accessors(kg):
    assert isinstance(kg.ontology(), OntologyGraph)
    assert isinstance(kg.capability(), CapabilityGraph)
    assert isinstance(kg.dependency(), DependencyGraph)
    assert isinstance(kg.traceability(), TraceabilityGraph)
    assert isinstance(kg.evidence(), EvidenceGraph)
    assert isinstance(kg.requirement(), RequirementGraph)
    assert isinstance(kg.implementation(), ImplementationGraph)
    assert isinstance(kg.validation(), ValidationGraph)
    assert isinstance(kg.certification_graph(), CertificationGraph)
    assert isinstance(kg.impact(), ImpactGraph)


def test_summary_shape(kg):
    summary = kg.summary()
    assert summary["contract"]["name"] == "knowledge.graph"
    assert set(summary["projections"]) == set(PROJECTION_NAMES)
    assert summary["core"]["nodes"] == 11
    assert summary["certification_verdict"] == "CERTIFIED"


def test_validate_and_visualize(kg):
    assert kg.validate().is_valid is True
    dot = kg.visualize("dependency", fmt="dot")
    assert dot.startswith("digraph")
    core_json = kg.visualize(fmt="json")
    assert '"nodes"' in core_json


def test_build_all(kg):
    kg.build_all()
    # all ten projections are now memoised
    assert len(kg._projections) == 10  # noqa: SLF001 - white-box check


def test_registry_property(kg):
    assert kg.registry is not None
    assert kg.registry.artifacts.count() == 7


def test_the_surface_reports_the_relationship_kinds_it_actually_emits():
    """CAA-INV-05 REQUIRES EVERY EMITTED KIND TO RESOLVE INTO ONE RELATIONSHIP MODEL, and
    this function is what the register consults to find out which kinds those are.

    It is declared as this surface's ``reporter`` and it is CALLED rather than trusted: a
    declared list would answer for the code it was written beside rather than the code that
    runs, which is the enumerated-governance failure the repository has already paid for
    elsewhere. Building the ten projections is the only way to know what they emit — and
    that also means the function had no caller in the suite, so the register's reporter was
    itself unmeasured.
    """

    kinds = emitted_kinds()

    assert kinds
    assert kinds == tuple(sorted(kinds))
    assert len(set(kinds)) == len(kinds)
    assert all(isinstance(kind, str) and kind for kind in kinds)
    assert emitted_kinds() == kinds, "the reported kinds are not stable"
