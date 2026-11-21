"""UCOS-EPIC-002 (Terminal T2) — the ten Universal Knowledge Graph projections.

Per UMB-006 (*three roots, one graph*), the mission's graphs are **projections of
one graph**, not ten separate stores. Each projection is a deterministic,
read-only view derived from the core :class:`~engine.graph.model.KnowledgeGraph`
(itself a projection of Registry Truth) plus, where relevant, the read-only
auxiliary registry documents (signals / certification / twin).

The ten projections:

======================  ==============================================================
Projection              Derivation
======================  ==============================================================
OntologyGraph           Volume / Category / Program anchoring + Parent/Child hierarchy
CapabilityGraph         Consumes / Consumed-By / Required-By capability provision
DependencyGraph         Depends-On / Parent / Child (a DAG) — topological + cycles
TraceabilityGraph       Implements/Traces-To/Evolves-From/Authorizes + trace stages
EvidenceGraph           Signal records bound to their subject artifacts
RequirementGraph        Requirement-bearing artifacts + requirement trace stage
ImplementationGraph     Implementation artifacts + Implements + implementation stage
ValidationGraph         Test/quality/security signals + twin validation dimensions
CertificationGraph      Certification domains + certified artifacts
ImpactGraph             Normalised "Affects" closure (blast radius / upstream)
======================  ==============================================================

Every projection exposes ``.graph`` (a :class:`KnowledgeGraph` view) and a
``summary()`` plus projection-specific semantic queries. Synthetic anchor
nodes/edges use deterministic immutable identifiers so projections are
reproducible and never duplicate a registry identifier.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from engine.graph import queries
from engine.graph.engine import (
    AUTHORIZED_BY,
    AUTHORIZES,
    CHILD,
    CONSUMED_BY,
    CONSUMES,
    DEPENDS_ON,
    EVOLVES_FROM,
    EVOLVES_FROM_INVERSE,
    IMPLEMENTED_BY,
    IMPLEMENTS,
    IN_PROGRAM,
    IN_VOLUME,
    OF_CATEGORY,
    PARENT,
    REQUIRED_BY,
    TRACED_FROM,
    TRACES_TO,
)
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

# Synthetic node/edge identifier prefixes (namespaced so they can never collide
# with a registry identifier — UCOS-* / UEDGE-* / VOL-* / USIG-*).
_CATEGORY_PREFIX = "CATEGORY::"
_PROGRAM_PREFIX = "PROGRAM::"
_CERT_PREFIX = "CERTDOMAIN::"


def _syn_edge_id(kind: str, source: str, target: str) -> str:
    """Deterministic, immutable identifier for a synthetic projection edge."""
    return f"KGE::{kind}::{source}=>{target}"


class Projection:
    """Base class for a named, read-only knowledge-graph projection."""

    #: Stable, human-facing projection name (used by the CLI and adapter).
    name: str = "projection"

    def __init__(self, graph: KnowledgeGraph) -> None:
        self._graph = graph

    @property
    def graph(self) -> KnowledgeGraph:
        """The projected :class:`KnowledgeGraph` view."""
        return self._graph

    def summary(self) -> dict[str, Any]:
        """A small, loggable summary of the projection's size."""
        return {
            "projection": self.name,
            "nodes": self._graph.order(),
            "edges": self._graph.size(),
            "kinds": list(self._graph.kinds()),
            "edge_types": list(self._graph.edge_types()),
        }


def _artifact_nodes(core: KnowledgeGraph) -> tuple[Node, ...]:
    return core.nodes_of_kind(KIND_ARTIFACT)


# --------------------------------------------------------------------------- #
# 1. Ontology Graph                                                           #
# --------------------------------------------------------------------------- #
class OntologyGraph(Projection):
    """The taxonomy backbone: every artifact anchored to Volume/Category/Program.

    Realises the ROOT ONTOLOGY (*to transform, a thing must relate; to relate, it
    must exist*) by anchoring each artifact to exactly one Volume, one Category,
    and one Program, and preserving the Parent/Child structural hierarchy. Node
    types are open (UMB-006 §3): Category and Program anchors are synthesised.
    """

    name = "ontology"

    def __init__(self, core: KnowledgeGraph) -> None:
        extra_nodes: dict[str, Node] = {}
        extra_edges: list[Edge] = []
        for art in _artifact_nodes(core):
            category = str(art.attributes.get("category") or "")
            program = str(art.attributes.get("program") or "")
            volume = str(art.attributes.get("volume") or "")
            if category:
                cid = _CATEGORY_PREFIX + category
                extra_nodes.setdefault(cid, Node(cid, KIND_CATEGORY, label=category, version=""))
                extra_edges.append(
                    Edge(_syn_edge_id(OF_CATEGORY, art.node_id, cid), art.node_id, cid, OF_CATEGORY)
                )
            if program:
                pid = _PROGRAM_PREFIX + program
                extra_nodes.setdefault(pid, Node(pid, KIND_PROGRAM, label=program, version=""))
                extra_edges.append(
                    Edge(_syn_edge_id(IN_PROGRAM, art.node_id, pid), art.node_id, pid, IN_PROGRAM)
                )
            if volume and core.has_node(volume):
                extra_edges.append(
                    Edge(
                        _syn_edge_id(IN_VOLUME, art.node_id, volume),
                        art.node_id,
                        volume,
                        IN_VOLUME,
                    )
                )
        graph = core.subgraph(
            edge_types={PARENT, CHILD},
            extra_nodes=tuple(extra_nodes.values()),
            extra_edges=tuple(extra_edges),
            keep_isolated=False,
        )
        super().__init__(graph)

    def categories(self) -> tuple[str, ...]:
        """Distinct category anchors, ordered."""
        return tuple(n.label for n in self._graph.nodes_of_kind(KIND_CATEGORY))

    def programs(self) -> tuple[str, ...]:
        """Distinct program anchors, ordered."""
        return tuple(n.label for n in self._graph.nodes_of_kind(KIND_PROGRAM))

    def anchor_of(self, artifact_id: str) -> dict[str, str]:
        """Return the ``{volume, category, program}`` anchor of an artifact."""
        node = self._graph.node(artifact_id)
        return (
            {
                "volume": next(
                    (e.target for e in self._graph.edges_from(artifact_id, type=IN_VOLUME)), ""
                ),
                "category": next(
                    (
                        self._graph.node(e.target).label
                        for e in self._graph.edges_from(artifact_id, type=OF_CATEGORY)
                    ),
                    "",
                ),
                "program": next(
                    (
                        self._graph.node(e.target).label
                        for e in self._graph.edges_from(artifact_id, type=IN_PROGRAM)
                    ),
                    "",
                ),
            }
            if node.kind == KIND_ARTIFACT
            else {}
        )


# --------------------------------------------------------------------------- #
# 2. Capability Graph                                                         #
# --------------------------------------------------------------------------- #
class CapabilityGraph(Projection):
    """Which artifacts provide capabilities and which consume/require them.

    Projected from the ``Consumes`` / ``Consumed-By`` / ``Required-By`` edge
    families — the capability provision/consumption topology.
    """

    name = "capability"

    def __init__(self, core: KnowledgeGraph) -> None:
        super().__init__(core.subgraph(edge_types={CONSUMES, CONSUMED_BY, REQUIRED_BY}))

    def consumes(self, node_id: str) -> tuple[str, ...]:
        """Capabilities ``node_id`` consumes (outbound ``Consumes``)."""
        return self._graph.successors(node_id, type=CONSUMES)

    def consumers_of(self, node_id: str) -> tuple[str, ...]:
        """Artifacts that consume ``node_id`` (inbound ``Consumes``)."""
        return self._graph.predecessors(node_id, type=CONSUMES)

    def required_by(self, node_id: str) -> tuple[str, ...]:
        """Artifacts that require ``node_id`` (outbound ``Required-By``)."""
        return self._graph.successors(node_id, type=REQUIRED_BY)


# --------------------------------------------------------------------------- #
# 3. Dependency Graph                                                         #
# --------------------------------------------------------------------------- #
class DependencyGraph(Projection):
    """The ``Depends-On`` / ``Parent`` / ``Child`` projection — a DAG."""

    name = "dependency"

    def __init__(self, core: KnowledgeGraph) -> None:
        super().__init__(core.subgraph(edge_types={DEPENDS_ON, PARENT, CHILD}))

    def dependencies_of(self, node_id: str) -> tuple[str, ...]:
        """Direct dependencies (outbound ``Depends-On``)."""
        return self._graph.successors(node_id, type=DEPENDS_ON)

    def dependents_of(self, node_id: str) -> tuple[str, ...]:
        """Direct dependents (inbound ``Depends-On``)."""
        return self._graph.predecessors(node_id, type=DEPENDS_ON)

    def transitive_dependencies(self, node_id: str) -> tuple[str, ...]:
        """Everything ``node_id`` (transitively) depends on."""
        return queries.descendants(self._graph, node_id, types=[DEPENDS_ON])

    def topological_order(self) -> tuple[str, ...]:
        """Deterministic topological order over the ``Depends-On`` DAG."""
        return queries.topological_order(self._graph, types=[DEPENDS_ON])

    def is_acyclic(self) -> bool:
        """True iff the ``Depends-On`` projection is acyclic (certification check)."""
        return queries.is_acyclic(self._graph, types=[DEPENDS_ON])

    def find_cycle(self) -> tuple[str, ...]:
        """One ``Depends-On`` cycle as a node path (empty if acyclic)."""
        return queries.find_cycle(self._graph, types=[DEPENDS_ON])


# --------------------------------------------------------------------------- #
# 4. Traceability Graph                                                       #
# --------------------------------------------------------------------------- #
_TRACE_EDGE_TYPES = frozenset(
    {
        IMPLEMENTS,
        IMPLEMENTED_BY,
        TRACES_TO,
        TRACED_FROM,
        EVOLVES_FROM,
        EVOLVES_FROM_INVERSE,
        AUTHORIZED_BY,
        AUTHORIZES,
    }
)
_TRACE_STAGES = ("requirement", "architecture", "design", "implementation")


class TraceabilityGraph(Projection):
    """Bidirectional traceability: trace edges + artifact traceability stages.

    Combines the ``Implements``/``Traces-To``/``Evolves-From``/``Authorizes`` edge
    families with synthetic ``Traces-Stage:<stage>`` edges derived from each
    artifact's ``traceability`` chain, so any artifact is reverse-traceable to the
    requirement/architecture/design/implementation references it declares.
    """

    name = "traceability"

    def __init__(self, core: KnowledgeGraph) -> None:
        extra_edges: list[Edge] = []
        for art in _artifact_nodes(core):
            trace = art.attributes.get("traceability")
            if not isinstance(trace, Mapping):
                continue
            for stage in _TRACE_STAGES:
                for ref in trace.get(stage, ()):  # type: ignore[union-attr]
                    if not core.has_node(ref):
                        continue
                    etype = f"Traces-Stage:{stage}"
                    extra_edges.append(
                        Edge(_syn_edge_id(etype, art.node_id, ref), art.node_id, ref, etype)
                    )
        super().__init__(
            core.subgraph(edge_types=_TRACE_EDGE_TYPES, extra_edges=tuple(extra_edges))
        )

    def trace_forward(self, node_id: str) -> tuple[str, ...]:
        """Everything ``node_id`` traces to (transitive outbound)."""
        return queries.descendants(self._graph, node_id)

    def trace_backward(self, node_id: str) -> tuple[str, ...]:
        """Everything that traces to ``node_id`` (transitive inbound)."""
        return queries.ancestors(self._graph, node_id)

    def stages_of(self, node_id: str) -> dict[str, tuple[str, ...]]:
        """The per-stage trace references declared by ``node_id``."""
        result: dict[str, tuple[str, ...]] = {}
        for stage in _TRACE_STAGES:
            etype = f"Traces-Stage:{stage}"
            targets = self._graph.successors(node_id, type=etype)
            if targets:
                result[stage] = targets
        return result


# --------------------------------------------------------------------------- #
# 5. Evidence Graph                                                           #
# --------------------------------------------------------------------------- #
class EvidenceGraph(Projection):
    """Signal records bound to the artifacts they are evidence for.

    Each signal becomes a ``Signal`` node (immutable ``signal_id``) with an
    ``Evidences`` edge to its subject artifact, carrying the dimension, state,
    source and evidence reference (secret-free — RR-07).
    """

    name = "evidence"
    EDGE_TYPE = "Evidences"

    def __init__(self, core: KnowledgeGraph, signals: tuple[Mapping[str, Any], ...]) -> None:
        extra_nodes: list[Node] = []
        extra_edges: list[Edge] = []
        subject_ids: set[str] = set()
        for sig in signals:
            sid = str(sig.get("signal_id") or "")
            subject = str(sig.get("subject_universal_id") or "")
            if not sid or not subject:
                continue
            extra_nodes.append(
                Node(
                    sid,
                    KIND_SIGNAL,
                    label=f"{sig.get('dimension', '')}:{sig.get('state', '')}",
                    version="",
                    attributes={
                        "dimension": sig.get("dimension", ""),
                        "state": sig.get("state", ""),
                        "source": sig.get("source", ""),
                        "as_of": sig.get("as_of", ""),
                        "evidence": sig.get("evidence", ""),
                    },
                )
            )
            if core.has_node(subject):
                subject_ids.add(subject)
            extra_edges.append(
                Edge(
                    _syn_edge_id(self.EDGE_TYPE, sid, subject),
                    sid,
                    subject,
                    self.EDGE_TYPE,
                    note=str(sig.get("dimension", "")),
                )
            )
        graph = core.subgraph(
            node_ids=subject_ids,
            edge_types=set(),  # only the synthetic Evidences edges belong here
            extra_nodes=tuple(extra_nodes),
            extra_edges=tuple(extra_edges),
            keep_isolated=True,
        )
        super().__init__(graph)
        self._signals = signals

    def evidence_for(self, artifact_id: str) -> tuple[Node, ...]:
        """The signal nodes that are evidence for ``artifact_id``."""
        return tuple(
            self._graph.node(e.source)
            for e in self._graph.edges_to(artifact_id, type=self.EDGE_TYPE)
        )

    def by_dimension(self, dimension: str) -> tuple[Node, ...]:
        """All signal nodes for a given ``dimension``."""
        return tuple(
            n
            for n in self._graph.nodes_of_kind(KIND_SIGNAL)
            if n.attributes.get("dimension") == dimension
        )

    def dimensions(self) -> tuple[str, ...]:
        """Distinct evidence dimensions present, ordered."""
        return tuple(
            sorted(
                {
                    str(n.attributes.get("dimension"))
                    for n in self._graph.nodes_of_kind(KIND_SIGNAL)
                    if n.attributes.get("dimension")
                }
            )
        )


# --------------------------------------------------------------------------- #
# 6. Requirement Graph                                                        #
# --------------------------------------------------------------------------- #
# Requirement-bearing categories in the certified corpus: constitution, registry,
# architecture, decisions, governance, and the master-book/UMB specifications.
_REQUIREMENT_CATEGORIES = frozenset({"CON", "REG", "ARCH", "ADR", "GOV", "UMB", "MASTER"})


class RequirementGraph(Projection):
    """Requirement-bearing artifacts and what traces to them.

    A node participates if it either (a) belongs to a requirement-bearing category
    or (b) is referenced by another artifact's ``requirement`` trace stage. Edges
    are the ``Traces-To`` / ``Traced-From`` families plus synthetic
    ``Requirement-Of`` edges from the requirement trace stage.
    """

    name = "requirement"
    EDGE_TYPE = "Requirement-Of"

    def __init__(self, core: KnowledgeGraph) -> None:
        members: set[str] = set()
        extra_edges: list[Edge] = []
        for art in _artifact_nodes(core):
            category = str(art.attributes.get("category") or "")
            if category in _REQUIREMENT_CATEGORIES:
                members.add(art.node_id)
            trace = art.attributes.get("traceability")
            if isinstance(trace, Mapping):
                for ref in trace.get("requirement", ()):  # type: ignore[union-attr]
                    if core.has_node(ref):
                        members.add(ref)
                        members.add(art.node_id)
                        extra_edges.append(
                            Edge(
                                _syn_edge_id(self.EDGE_TYPE, ref, art.node_id),
                                ref,
                                art.node_id,
                                self.EDGE_TYPE,
                            )
                        )
        graph = core.subgraph(
            node_ids=members,
            edge_types={TRACES_TO, TRACED_FROM},
            extra_edges=tuple(extra_edges),
            keep_isolated=True,
        )
        super().__init__(graph)

    def requirements_of(self, artifact_id: str) -> tuple[str, ...]:
        """Requirement artifacts that ``artifact_id`` declares in its trace stage."""
        return self._graph.predecessors(artifact_id, type=self.EDGE_TYPE)

    def satisfied_by(self, requirement_id: str) -> tuple[str, ...]:
        """Artifacts that declare ``requirement_id`` as a requirement."""
        return self._graph.successors(requirement_id, type=self.EDGE_TYPE)


# --------------------------------------------------------------------------- #
# 7. Implementation Graph                                                     #
# --------------------------------------------------------------------------- #
_IMPLEMENTATION_CATEGORIES = frozenset({"IMP", "SRC", "ENG", "RUN", "GEN"})


class ImplementationGraph(Projection):
    """Implementation artifacts and what they implement.

    Nodes: implementation-bearing artifacts plus anything referenced by an
    ``implementation`` trace stage. Edges: the ``Implements`` / ``Implemented-By``
    families plus synthetic ``Implements-Stage`` edges.
    """

    name = "implementation"
    EDGE_TYPE = "Implements-Stage"

    def __init__(self, core: KnowledgeGraph) -> None:
        members: set[str] = set()
        extra_edges: list[Edge] = []
        # Both endpoints of every Implements / Implemented-By edge belong to the
        # implementation graph: the implementing artifact *and* the spec it
        # implements (so "what does this implement?" is answerable).
        for edge in core.edges():
            if edge.type in (IMPLEMENTS, IMPLEMENTED_BY):
                members.add(edge.source)
                members.add(edge.target)
        for art in _artifact_nodes(core):
            category = str(art.attributes.get("category") or "")
            if category in _IMPLEMENTATION_CATEGORIES:
                members.add(art.node_id)
            trace = art.attributes.get("traceability")
            if isinstance(trace, Mapping):
                for ref in trace.get("implementation", ()):  # type: ignore[union-attr]
                    if core.has_node(ref):
                        members.add(ref)
                        members.add(art.node_id)
                        extra_edges.append(
                            Edge(
                                _syn_edge_id(self.EDGE_TYPE, art.node_id, ref),
                                art.node_id,
                                ref,
                                self.EDGE_TYPE,
                            )
                        )
        graph = core.subgraph(
            node_ids=members,
            edge_types={IMPLEMENTS, IMPLEMENTED_BY},
            extra_edges=tuple(extra_edges),
            keep_isolated=True,
        )
        super().__init__(graph)

    def implements(self, node_id: str) -> tuple[str, ...]:
        """What ``node_id`` implements (outbound ``Implements``)."""
        return self._graph.successors(node_id, type=IMPLEMENTS)

    def implemented_by(self, node_id: str) -> tuple[str, ...]:
        """What implements ``node_id`` (inbound ``Implements`` / outbound inverse)."""
        seen: dict[str, None] = {}
        for src in self._graph.predecessors(node_id, type=IMPLEMENTS):
            seen.setdefault(src, None)
        for tgt in self._graph.successors(node_id, type=IMPLEMENTED_BY):
            seen.setdefault(tgt, None)
        return tuple(seen)


# --------------------------------------------------------------------------- #
# 8. Validation Graph                                                         #
# --------------------------------------------------------------------------- #
_VALIDATION_DIMENSIONS = frozenset(
    {"unit_testing", "build", "quality", "security", "integration_test", "functional_test"}
)


class ValidationGraph(Projection):
    """Test / quality / security validation evidence for artifacts.

    Projected from validation-dimension signals (``Validates`` edges to subjects)
    and enriched with the digital-twin per-dimension validation state.
    """

    name = "validation"
    EDGE_TYPE = "Validates"

    def __init__(
        self,
        core: KnowledgeGraph,
        signals: tuple[Mapping[str, Any], ...],
        twin: Mapping[str, Any],
    ) -> None:
        extra_nodes: list[Node] = []
        extra_edges: list[Edge] = []
        subjects: set[str] = set()
        for sig in signals:
            dimension = str(sig.get("dimension") or "")
            if dimension not in _VALIDATION_DIMENSIONS:
                continue
            sid = str(sig.get("signal_id") or "")
            subject = str(sig.get("subject_universal_id") or "")
            if not sid or not subject:
                continue
            metrics = sig.get("metrics") if isinstance(sig.get("metrics"), Mapping) else {}
            extra_nodes.append(
                Node(
                    sid,
                    KIND_SIGNAL,
                    label=f"{dimension}:{sig.get('state', '')}",
                    version="",
                    attributes={
                        "dimension": dimension,
                        "state": sig.get("state", ""),
                        "result": (metrics or {}).get("result", ""),
                        "coverage": (metrics or {}).get("coverage", ""),
                    },
                )
            )
            if core.has_node(subject):
                subjects.add(subject)
            extra_edges.append(
                Edge(
                    _syn_edge_id(self.EDGE_TYPE, sid, subject),
                    sid,
                    subject,
                    self.EDGE_TYPE,
                    note=dimension,
                )
            )
        graph = core.subgraph(
            node_ids=subjects,
            edge_types=set(),  # only the synthetic Validates edges belong here
            extra_nodes=tuple(extra_nodes),
            extra_edges=tuple(extra_edges),
            keep_isolated=True,
        )
        super().__init__(graph)
        dims = twin.get("dimensions") if isinstance(twin.get("dimensions"), Mapping) else {}
        self._twin_dimensions: Mapping[str, Any] = dims or {}

    def validation_signals(self, artifact_id: str) -> tuple[Node, ...]:
        """The validation signal nodes bound to ``artifact_id``."""
        return tuple(
            self._graph.node(e.source)
            for e in self._graph.edges_to(artifact_id, type=self.EDGE_TYPE)
        )

    def twin_state(self, dimension: str) -> dict[str, Any]:
        """The digital-twin state for a validation ``dimension`` (empty if absent)."""
        value = self._twin_dimensions.get(dimension)
        return dict(value) if isinstance(value, Mapping) else {}

    def dimensions(self) -> tuple[str, ...]:
        """Distinct validation dimensions present in the evidence, ordered."""
        return tuple(
            sorted(
                {
                    str(n.attributes.get("dimension"))
                    for n in self._graph.nodes_of_kind(KIND_SIGNAL)
                    if n.attributes.get("dimension")
                }
            )
        )


# --------------------------------------------------------------------------- #
# 9. Certification Graph                                                       #
# --------------------------------------------------------------------------- #
_CERTIFIED_STATUSES = frozenset({"CERTIFIED", "FROZEN", "FINAL"})


class CertificationGraph(Projection):
    """Certification domains and the artifacts they certify.

    Each certification domain becomes a ``CertificationDomain`` node with a
    ``Certifies`` edge to the certified corpus root, carrying its pass/fail verdict
    and check summary. Certified artifacts (status CERTIFIED/FROZEN/FINAL) are
    retained so the certified surface is navigable.
    """

    name = "certification"
    EDGE_TYPE = "Certifies"

    def __init__(self, core: KnowledgeGraph, certification: Mapping[str, Any]) -> None:
        self._verdict = str(certification.get("verdict") or "UNKNOWN")
        self._standard = str(certification.get("standard") or "")
        domains = certification.get("domains")
        domains = domains if isinstance(domains, Mapping) else {}

        # Anchor certification to the BOOK root when present, else the lowest id.
        root = self._pick_root(core)
        certified = {
            a.node_id
            for a in _artifact_nodes(core)
            if str(a.attributes.get("status")) in _CERTIFIED_STATUSES
        }
        members = set(certified)
        if root:
            members.add(root)

        extra_nodes: list[Node] = []
        extra_edges: list[Edge] = []
        for domain_name, body in domains.items():
            did = _CERT_PREFIX + str(domain_name)
            passed = bool(body.get("pass")) if isinstance(body, Mapping) else False
            checks = body.get("checks") if isinstance(body, Mapping) else []
            extra_nodes.append(
                Node(
                    did,
                    KIND_CERT_DOMAIN,
                    label=str(domain_name),
                    version="",
                    attributes={
                        "pass": passed,
                        "check_count": len(checks) if isinstance(checks, list) else 0,
                    },
                )
            )
            if root:
                extra_edges.append(
                    Edge(
                        _syn_edge_id(self.EDGE_TYPE, did, root),
                        did,
                        root,
                        self.EDGE_TYPE,
                        note=self._verdict,
                    )
                )
        graph = core.subgraph(
            node_ids=members,
            edge_types=set(),  # only the synthetic Certifies edges belong here
            extra_nodes=tuple(extra_nodes),
            extra_edges=tuple(extra_edges),
            keep_isolated=True,
        )
        super().__init__(graph)
        self._domain_names = tuple(sorted(str(k) for k in domains))
        self._certified_ids = tuple(sorted(certified))

    @staticmethod
    def _pick_root(core: KnowledgeGraph) -> str:
        for candidate in ("UCOS-BOOK-000000",):
            if core.has_node(candidate):
                return candidate
        artifacts = _artifact_nodes(core)
        return artifacts[0].node_id if artifacts else ""

    def verdict(self) -> str:
        """The overall certification verdict (e.g. ``CERTIFIED``)."""
        return self._verdict

    def domains(self) -> tuple[str, ...]:
        """The certification domain names, ordered."""
        return self._domain_names

    def is_certified(self) -> bool:
        """True iff every certification domain passed and the verdict is CERTIFIED."""
        nodes = self._graph.nodes_of_kind(KIND_CERT_DOMAIN)
        return (
            bool(nodes)
            and all(n.attributes.get("pass") for n in nodes)
            and (self._verdict == "CERTIFIED")
        )

    def certified_artifacts(self) -> tuple[str, ...]:
        """Artifact ids whose lifecycle status is a certified terminal state."""
        return self._certified_ids


# --------------------------------------------------------------------------- #
# 10. Impact Graph                                                            #
# --------------------------------------------------------------------------- #
class ImpactGraph(Projection):
    """Normalised change-impact closure: *if X changes, who is affected?*

    Reduces the dependency/consumption/implementation edge families to a single
    directed ``Affects`` relation (``A Affects B`` iff a change to ``A`` propagates
    to ``B``), then answers blast-radius and upstream queries as closures over it.
    """

    name = "impact"
    EDGE_TYPE = "Affects"

    def __init__(self, core: KnowledgeGraph) -> None:
        affects: dict[tuple[str, str], Edge] = {}

        def affect(a: str, b: str) -> None:
            if a == b or not core.has_node(a) or not core.has_node(b):
                return
            key = (a, b)
            if key not in affects:
                affects[key] = Edge(_syn_edge_id(self.EDGE_TYPE, a, b), a, b, self.EDGE_TYPE)

        for edge in core.edges():
            # X Depends-On Y  => Y Affects X
            if edge.type == DEPENDS_ON:
                affect(edge.target, edge.source)
            # X Consumes Y    => Y Affects X
            elif edge.type == CONSUMES:
                affect(edge.target, edge.source)
            # X Implements Y  => Y Affects X (spec change impacts implementation)
            elif edge.type == IMPLEMENTS:
                affect(edge.target, edge.source)
            # Y Required-By X => Y Affects X
            elif edge.type == REQUIRED_BY:
                affect(edge.source, edge.target)
        members = {n for pair in affects for n in pair}
        graph = core.subgraph(
            node_ids=members,
            edge_types=set(),  # drop all raw edges; keep only synthetic Affects
            extra_edges=tuple(affects.values()),
            keep_isolated=False,
        )
        super().__init__(graph)

    def impact_of(self, node_id: str) -> tuple[str, ...]:
        """Everything (transitively) affected if ``node_id`` changes."""
        if not self._graph.has_node(node_id):
            return ()
        return queries.descendants(self._graph, node_id, types=[self.EDGE_TYPE])

    def upstream_of(self, node_id: str) -> tuple[str, ...]:
        """Everything ``node_id`` (transitively) depends upon (reverse ``Affects``)."""
        if not self._graph.has_node(node_id):
            return ()
        return queries.ancestors(self._graph, node_id, types=[self.EDGE_TYPE])

    def blast_radius(self, node_id: str) -> int:
        """The number of artifacts impacted by a change to ``node_id``."""
        return len(self.impact_of(node_id))


# --------------------------------------------------------------------------- #
# Projection registry                                                          #
# --------------------------------------------------------------------------- #
#: Names of the ten mission graph projections, in mission order.
PROJECTION_NAMES: tuple[str, ...] = (
    "ontology",
    "capability",
    "dependency",
    "traceability",
    "evidence",
    "requirement",
    "implementation",
    "validation",
    "certification",
    "impact",
)


def build_projection(
    name: str,
    core: KnowledgeGraph,
    *,
    signals: tuple[Mapping[str, Any], ...] = (),
    certification: Mapping[str, Any] | None = None,
    twin: Mapping[str, Any] | None = None,
) -> Projection:
    """Construct a single named projection over the core graph.

    Raises:
        ProjectionError: ``name`` is not one of the ten mission projections.
    """
    certification = certification or {}
    twin = twin or {}
    match name:
        case "ontology":
            return OntologyGraph(core)
        case "capability":
            return CapabilityGraph(core)
        case "dependency":
            return DependencyGraph(core)
        case "traceability":
            return TraceabilityGraph(core)
        case "evidence":
            return EvidenceGraph(core, signals)
        case "requirement":
            return RequirementGraph(core)
        case "implementation":
            return ImplementationGraph(core)
        case "validation":
            return ValidationGraph(core, signals, twin)
        case "certification":
            return CertificationGraph(core, certification)
        case "impact":
            return ImpactGraph(core)
        case _:
            raise ProjectionError("unknown graph projection", name=name, known=PROJECTION_NAMES)


__all__ = [
    "Projection",
    "OntologyGraph",
    "CapabilityGraph",
    "DependencyGraph",
    "TraceabilityGraph",
    "EvidenceGraph",
    "RequirementGraph",
    "ImplementationGraph",
    "ValidationGraph",
    "CertificationGraph",
    "ImpactGraph",
    "PROJECTION_NAMES",
    "build_projection",
]
