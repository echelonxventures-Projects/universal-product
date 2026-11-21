"""Unit tests for engine.graph.projections — the ten mission graphs."""

from __future__ import annotations

import pytest

from engine.graph.errors import ProjectionError
from engine.graph.model import (
    KIND_ARTIFACT,
    KIND_CATEGORY,
    KIND_CERT_DOMAIN,
    KIND_PROGRAM,
    KIND_SIGNAL,
    Edge,
    KnowledgeGraph,
    Node,
)
from engine.graph.projections import (
    _VALIDATION_DIMENSIONS,
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
    build_projection,
)


def test_projection_names_are_ten():
    assert len(PROJECTION_NAMES) == 10
    assert PROJECTION_NAMES[0] == "ontology"
    assert PROJECTION_NAMES[-1] == "impact"


def test_build_projection_unknown_raises(core):
    with pytest.raises(ProjectionError):
        build_projection("nope", core)


# --- 1. Ontology ---------------------------------------------------------------
def test_ontology_graph(core):
    onto = OntologyGraph(core)
    assert "CON" in onto.categories()
    assert "ARCH" in onto.programs()
    anchor = onto.anchor_of("UCOS-ARCH-000001")
    assert anchor["volume"] == "VOL-003"
    assert anchor["category"] == "ARCH"
    assert anchor["program"] == "ARCH"
    # synthetic anchor nodes exist
    assert onto.graph.nodes_of_kind(KIND_CATEGORY)
    assert onto.graph.nodes_of_kind(KIND_PROGRAM)
    # a volume node has no artifact anchor
    assert onto.anchor_of("VOL-003") == {}
    assert onto.summary()["projection"] == "ontology"


# --- 2. Capability -------------------------------------------------------------
def test_capability_graph(core):
    cap = CapabilityGraph(core)
    assert cap.consumes("UCOS-SVC-000001") == ("UCOS-REG-000001",)
    assert cap.consumers_of("UCOS-REG-000001") == ("UCOS-SVC-000001",)
    assert "UCOS-ARCH-000001" in cap.required_by("UCOS-CON-000001")


# --- 3. Dependency -------------------------------------------------------------
def test_dependency_graph(core):
    dep = DependencyGraph(core)
    assert dep.dependencies_of("UCOS-IMP-000001") == ("UCOS-ARCH-000001",)
    assert dep.dependents_of("UCOS-ARCH-000001") == ("UCOS-IMP-000001",)
    assert set(dep.transitive_dependencies("UCOS-IMP-000001")) == {
        "UCOS-ARCH-000001",
        "UCOS-CON-000001",
    }
    assert dep.is_acyclic() is True
    order = dep.topological_order()
    # standard topological order: every Depends-On edge points forward
    # (IMP Depends-On ARCH Depends-On CON  =>  IMP before ARCH before CON)
    assert order.index("UCOS-IMP-000001") < order.index("UCOS-ARCH-000001")
    assert order.index("UCOS-ARCH-000001") < order.index("UCOS-CON-000001")
    assert dep.find_cycle() == ()


# --- 4. Traceability -----------------------------------------------------------
def test_traceability_graph(core):
    trace = TraceabilityGraph(core)
    # IMP implements + traces-to reach ARCH and CON
    assert "UCOS-ARCH-000001" in trace.trace_forward("UCOS-IMP-000001")
    assert "UCOS-IMP-000001" in trace.trace_backward("UCOS-ARCH-000001")
    stages = trace.stages_of("UCOS-ARCH-000001")
    assert stages["requirement"] == ("UCOS-CON-000001",)


# --- 5. Evidence ---------------------------------------------------------------
def test_evidence_graph(core, sample_signals):
    ev = EvidenceGraph(core, tuple(sample_signals))
    signals = ev.evidence_for("UCOS-IMP-000001")
    assert {n.attributes["dimension"] for n in signals} == {"build", "unit_testing"}
    assert ev.by_dimension("security")[0].node_id == "USIG-000000003"
    assert "build" in ev.dimensions()
    # signal nodes are present as a distinct kind
    assert ev.graph.nodes_of_kind(KIND_SIGNAL)


# --- 6. Requirement ------------------------------------------------------------
def test_requirement_graph(core):
    req = RequirementGraph(core)
    # ARCH declares CON-000001 as a requirement
    assert "UCOS-CON-000001" in req.requirements_of("UCOS-ARCH-000001")
    assert "UCOS-ARCH-000001" in req.satisfied_by("UCOS-CON-000001")


# --- 7. Implementation ---------------------------------------------------------
def test_implementation_graph(core):
    impl = ImplementationGraph(core)
    assert impl.implements("UCOS-IMP-000001") == ("UCOS-ARCH-000001",)
    assert "UCOS-IMP-000001" in impl.implemented_by("UCOS-ARCH-000001")


# --- 8. Validation -------------------------------------------------------------
def test_validation_graph(core, sample_signals, sample_twin):
    val = ValidationGraph(core, tuple(sample_signals), sample_twin)
    sigs = val.validation_signals("UCOS-IMP-000001")
    assert {n.attributes["dimension"] for n in sigs} == {"build", "unit_testing"}
    assert val.twin_state("build")["status"] == "IMPLEMENTED"
    assert val.twin_state("nonexistent") == {}
    assert "security" in val.dimensions()


# --- 9. Certification ----------------------------------------------------------
def test_certification_graph(core, sample_certification):
    cert = CertificationGraph(core, sample_certification)
    assert cert.verdict() == "CERTIFIED"
    assert cert.domains() == ("identity", "knowledge_graph")
    assert cert.is_certified() is True
    assert cert.graph.nodes_of_kind(KIND_CERT_DOMAIN)
    # certified artifacts: CON (FROZEN) and REG (CERTIFIED)
    assert set(cert.certified_artifacts()) == {"UCOS-CON-000001", "UCOS-REG-000001"}


def test_certification_graph_empty_record(core):
    cert = CertificationGraph(core, {})
    assert cert.verdict() == "UNKNOWN"
    assert cert.is_certified() is False
    assert cert.domains() == ()


# --- 10. Impact ----------------------------------------------------------------
def test_impact_graph(core):
    impact = ImpactGraph(core)
    # CON is depended on (transitively) by ARCH and IMP -> impact reaches both
    impacted = impact.impact_of("UCOS-CON-000001")
    assert "UCOS-ARCH-000001" in impacted
    assert "UCOS-IMP-000001" in impacted
    assert impact.blast_radius("UCOS-CON-000001") >= 2
    # upstream of IMP reaches its transitive dependencies
    assert "UCOS-CON-000001" in impact.upstream_of("UCOS-IMP-000001")
    # unknown node -> empty
    assert impact.impact_of("UCOS-NOPE-000000") == ()
    assert impact.upstream_of("UCOS-NOPE-000000") == ()


def test_build_projection_all_names(core, sample_signals, sample_certification, sample_twin):
    for name in PROJECTION_NAMES:
        proj = build_projection(
            name,
            core,
            signals=tuple(sample_signals),
            certification=sample_certification,
            twin=sample_twin,
        )
        assert proj.name == name
        assert proj.summary()["nodes"] >= 0


# --- the attributes a projection SKIPS, and why skipping is the correct answer ---


def _bare_core(**attributes):
    """A one-artifact core graph whose artifact carries exactly ``attributes``."""

    graph = KnowledgeGraph()
    graph.add_node(
        Node(
            "UCOS-TEST-000001", KIND_ARTIFACT, label="Bare", version="1.0.0", attributes=attributes
        )
    )
    return graph


def test_the_ontology_synthesises_a_node_only_for_an_attribute_that_is_declared():
    """CATEGORY, PROGRAM AND VOLUME ARE EACH OPTIONAL, and each absence is skipped.

    The ontology projection invents a node per declared attribute so the graph can be
    navigated by them. An artifact declaring none would otherwise acquire three synthetic
    nodes labelled with the empty string — one category called "", one program called "" —
    and every artifact missing that attribute would appear to share it.

    The volume arm is different again: a declared volume that the core graph does not hold
    is skipped rather than synthesised, because a volume is a REAL registry node and
    inventing one would assert that a volume exists which nothing declared.
    """
    empty = OntologyGraph(_bare_core(category="", program="", volume=""))
    assert empty.categories() == ()
    assert empty.programs() == ()

    dangling = OntologyGraph(_bare_core(category="CON", program="ARCH", volume="UCOS-VOL-ABSENT"))
    assert "CON" in dangling.categories()
    assert "ARCH" in dangling.programs()
    assert not any(e.target == "UCOS-VOL-ABSENT" for e in dangling.graph.edges())


def test_traceability_skips_an_artifact_whose_trace_is_not_a_mapping():
    """A TRACE IS A STAGE MAP, and anything else cannot be walked stage by stage.

    A registry document carrying a list, a string or nothing at all under ``traceability``
    is a real shape — an artifact that has never been traced. Iterating it as a mapping
    would raise inside a projection whose job is to build a graph from whatever the registry
    holds, so the artifact contributes no trace edges and the projection still builds.
    """
    for wrong in (None, [], "requirement", 7):
        projection = TraceabilityGraph(_bare_core(traceability=wrong))
        assert projection.graph.size() == 0


def test_evidence_and_validation_skip_a_signal_that_names_no_subject():
    """A SIGNAL WITHOUT AN ID OR A SUBJECT ATTACHES TO NOTHING.

    Both projections turn signals into nodes joined to the subject they observe. One
    missing either half would be a node with an empty id — colliding with every other such
    signal — or an edge pointing at the empty subject. Skipping it keeps the projection a
    statement about the signals that actually observe something.
    """
    core_graph = _bare_core(category="CON")
    malformed = (
        {"signal_id": "", "subject_universal_id": "UCOS-TEST-000001"},
        {"signal_id": "SIG-1", "subject_universal_id": ""},
        {},
    )

    assert EvidenceGraph(core_graph, malformed).graph.nodes_of_kind(KIND_SIGNAL) == ()
    assert ValidationGraph(core_graph, malformed, {}).graph.nodes_of_kind(KIND_SIGNAL) == ()

    # And a well-formed signal still lands, so the skip is a filter rather than a refusal.
    sound = ({"signal_id": "SIG-1", "subject_universal_id": "UCOS-TEST-000001"},)
    assert EvidenceGraph(core_graph, sound).graph.nodes_of_kind(KIND_SIGNAL)


def test_requirement_and_implementation_skip_an_untraced_or_dangling_reference():
    """TWO PROJECTIONS, THE SAME TWO SKIPS, and each for the same reason.

    An artifact whose ``traceability`` is not a mapping has never been traced, and iterating
    it as one would raise inside a projection whose job is to build a graph from whatever the
    registry holds. A trace naming a reference the core graph does not carry is a stage
    pointing at nothing — admitting it would put a member into the projection that no node
    backs, which is the dangling endpoint every validation here refuses.
    """

    def _core(**attributes):
        graph = KnowledgeGraph()
        graph.add_node(
            Node(
                "UCOS-TEST-000001", KIND_ARTIFACT, label="T", version="1.0.0", attributes=attributes
            )
        )
        return graph

    for projection_class, stage in (
        (RequirementGraph, "requirement"),
        (ImplementationGraph, "implementation"),
    ):
        untraced = projection_class(_core(category="CON", traceability=None))
        assert not untraced.graph.has_node("UCOS-ABSENT-000001")

        dangling = projection_class(
            _core(category="CON", traceability={stage: ["UCOS-ABSENT-000001"]})
        )
        assert not dangling.graph.has_node("UCOS-ABSENT-000001")


def test_validation_skips_a_signal_of_the_right_dimension_that_names_nothing():
    """The dimension filter runs FIRST, so a signal of a validation dimension still has to
    carry an id and a subject. Without the second check a well-dimensioned but incomplete
    signal would become a node with an empty id, colliding with every other such signal."""

    graph = KnowledgeGraph()
    graph.add_node(Node("UCOS-TEST-000001", KIND_ARTIFACT, label="T", version="1.0.0"))
    dimension = next(iter(_VALIDATION_DIMENSIONS))

    incomplete = ValidationGraph(
        graph,
        (
            {"dimension": dimension, "signal_id": "", "subject_universal_id": "UCOS-TEST-000001"},
            {"dimension": dimension, "signal_id": "SIG-1", "subject_universal_id": ""},
        ),
        {},
    )
    assert incomplete.graph.nodes_of_kind(KIND_SIGNAL) == ()


def test_the_certification_root_falls_back_to_an_artifact_and_then_to_nothing():
    """THE ROOT IS THE NODE EVERY DOMAIN IS JOINED TO, and it is looked for in order.

    The canonical book root is preferred; a corpus that does not carry it falls back to the
    first artifact, so the certification projection still has something to hang domains from.
    A corpus with neither yields ``""``, and the domains are then emitted unjoined rather than
    joined to an invented node — a fabricated root would assert a containment nothing declared.
    """

    empty = KnowledgeGraph()
    assert CertificationGraph._pick_root(empty) == ""

    artifacts_only = KnowledgeGraph()
    artifacts_only.add_node(Node("UCOS-TEST-000001", KIND_ARTIFACT, label="T", version="1.0.0"))
    assert CertificationGraph._pick_root(artifacts_only) == "UCOS-TEST-000001"

    with_book = KnowledgeGraph()
    with_book.add_node(Node("UCOS-TEST-000001", KIND_ARTIFACT, label="T", version="1.0.0"))
    with_book.add_node(Node("UCOS-BOOK-000000", KIND_ARTIFACT, label="Book", version="1.0.0"))
    assert CertificationGraph._pick_root(with_book) == "UCOS-BOOK-000000"


def test_certification_emits_a_domain_without_a_root_edge_when_there_is_no_root(core):
    """The ``root`` guard appears twice — once when collecting members and once when joining
    each domain — and both must skip together. Emitting a domain edge to the empty node id
    would create an edge whose target is not a node, which is the state the model refuses."""
    empty = type(core)()
    projection = CertificationGraph(empty, {"domains": {"structural": {"checks": []}}})

    assert projection._domain_names == ("structural",)  # noqa: SLF001
    for edge in projection.graph.edges():
        assert edge.target != ""


def test_impact_does_not_relate_a_node_to_itself_or_to_one_the_graph_lacks(core):
    """AN AFFECTS EDGE IS A CLAIM THAT A CHANGE PROPAGATES.

    A self-edge claims a node's change reaches itself, which is true of everything and
    therefore says nothing; an edge to a node the graph does not carry claims propagation
    into somewhere unresolvable. Both are dropped, so the blast radius stays a count of
    things a reader can actually go and look at.
    """
    projection = ImpactGraph(core)

    for edge in projection.graph.edges():
        assert edge.source != edge.target
        assert projection.graph.has_node(edge.source)
        assert projection.graph.has_node(edge.target)


def test_impact_drops_a_self_edge_and_an_edge_into_a_node_the_graph_lacks():
    """AN AFFECTS EDGE IS A CLAIM THAT A CHANGE PROPAGATES, and two shapes claim nothing.

    A self-edge says a node's change reaches itself, which is true of everything and
    therefore distinguishes nothing; an edge to a node the core graph does not carry claims
    propagation into somewhere unresolvable. Both are dropped at the point the edge would be
    created, so the blast radius stays a count of things a reader can go and look at.
    """

    graph = KnowledgeGraph()
    for node_id in ("UCOS-A-000001", "UCOS-B-000001"):
        graph.add_node(Node(node_id, KIND_ARTIFACT, label=node_id, version="1.0.0"))
    graph.add_edge(Edge("UCOS-EDGE-000001", "UCOS-A-000001", "UCOS-A-000001", "Depends-On"))
    graph.add_edge(Edge("UCOS-EDGE-000002", "UCOS-A-000001", "UCOS-ABSENT-000001", "Depends-On"))
    graph.add_edge(Edge("UCOS-EDGE-000003", "UCOS-A-000001", "UCOS-B-000001", "Depends-On"))

    projection = ImpactGraph(graph)

    assert not projection.graph.has_node("UCOS-ABSENT-000001")
    for edge in projection.graph.edges():
        assert edge.source != edge.target
        assert projection.graph.has_node(edge.source)
        assert projection.graph.has_node(edge.target)
    assert projection.graph.size() >= 1
