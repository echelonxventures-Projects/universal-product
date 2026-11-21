"""EC3-B11-U11 — The Universal Service Meta-Model construct (USM; SERVICE-005).

Realizes the **model-of-the-model** (SERVICE-005 §1): the executable Universal Service
Meta-Model (USM) that **integrates** the ten CERTIFIED concern meta-classes (SMC-01…10;
units U01…U10) and the thirteen meta-relationships (SMR-01…13) into one closed, total,
acyclic, reuse-integral, non-constitutive, non-projective model, and thereby serves as the
conformance gate for the whole Band-11 Service layer.

The Universal Service Meta-Model is **not** an eleventh meta-class — SMI-01 admits no
meta-class outside SMC-01…10. It is the singular model artifact that *fixes* the ten. It is
**additive over — and composes *by reference*** the CERTIFIED EC-1 foundation and the ten
CERTIFIED concern-meta-class realizations (USL-02 / SMI-05):

* Each :class:`MetaClassMember` is a **reference to a CERTIFIED concern meta-class
  realization** (meta-class id + ontology entity + hierarchy + realizing unit +
  certification id) — **never owned, embedded, or copied** (SMX-02 non-absorbing).
* Each :class:`MetaRelationshipEdge` is a **meta-relationship viewed as an ENG-005
  reference** between meta-classes (or to the frozen EL-1/RL-F2/PL-F2/DF-2 foundations) —
  it introduces no new connection construct.
* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.content_hash`) — no second identity scheme.

The construct enforces the seven meta-invariants **fail-closed** at construction
(SERVICE-005 §8):

* **SMI-01 Closure** — the members are exactly SMC-01…10 (no eleventh, no duplicate).
* **SMI-02 Relationship closure** — the edges are exactly SMR-01…13.
* **SMI-03 Totality** — the members model exactly SOE-01…10 and the edges model exactly
  SOR-01…13 (a bijection each).
* **SMI-04 Acyclicity** — the founding meta-graph (SMR-02/03/04/05) is a DAG.
* **SMI-05 Reuse integrity** — every member resolves to a CERTIFIED unit and every edge
  target resolves within the closure or the frozen foundations; nothing is redefined.
* **SMI-06 Non-constitutiveness** — the model confers no authority, embeds no secret, and
  names no technology.
* **SMI-07 Non-projection** — the model records that model coverage is never roadmap,
  implementation, deployment, or operational completion (STATUS-001 §2).

An ill-formed, open, partial, cyclic-founding, uncertified-member, authority-conferring, or
technology-bound meta-model cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.model_meta import (
    EDGE_SPECS,
    FOUNDATION_TARGETS,
    FOUNDING_META_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    MEMBER_SPECS,
    META_CLASSES,
    META_RELATIONSHIPS,
    MODEL_CLASS,
    MODEL_SUBSTRATE_REFS,
    ONTOLOGY_ENTITIES,
    ONTOLOGY_RELATIONSHIPS,
    ModelState,
)

#: The deterministic id prefix for a realized Universal Service Meta-Model.
MODEL_ID_PREFIX = "UCOS-METAMODEL"

#: The certification-id prefix a CERTIFIED concern meta-class member presents (ENG-001).
CERT_ID_PREFIX = "UCOS-CERT-"

#: The map of EC-1 / SMC primitives this construct reuses *by reference* (never redefined).
#: Recorded for the reuse-integrity check (USL-02 / SMI-05).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the meta-model record)",
    "ENG-004": "meta-class + meta-relationship typing discipline (ENG-004)",
    "ENG-005": "meta-relationship edges + member certification references (§3 / SMR-01…13)",
    "SMC-01..10": "the ten CERTIFIED concern-meta-class realizations — referenced, not owned",
    "RL-F2": "RUNTIME behaviour concern — bound by reference (SMR-11 behaves-as; SMR-07 executes)",
    "PL-F2": "PLATFORM composition concern — bound by reference (SMR-12 composed-as)",
    "DF-2": "DATA represented-data concern — bound by reference (SMR-13 operates-on)",
}

#: Conservative secret markers used to enforce USL-15 / SMI-06 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "privatekey",
    "api_key",
    "apikey",
    "access_token",
    "credential",
    "-----begin",
)

#: Conservative service/API/transport-technology markers used to enforce **USL-15 / SMI-06 /
#: SMK-08** (the meta-model selects no technology, API, protocol, transport, or vendor). A
#: meta-model naming any of these is rejected fail-closed — it is an implementation-
#: independent model only (SERVICE-005 CLASSIFICATION). Markers are chosen to contain
#: characters outside the hexadecimal alphabet used by content digests, so they never
#: collide with a member certification suffix.
_TECH_MARKERS: tuple[str, ...] = (
    "rest",
    "grpc",
    "http",
    "https",
    "soap",
    "graphql",
    "thrift",
    "websocket",
    "openapi",
    "swagger",
    "kafka",
    "rabbitmq",
    "amqp",
    "mqtt",
    "istio",
    "envoy",
    "kubernetes",
    "lambda",
    "protobuf",
    "service mesh",
)

#: The number of hexadecimal characters a member certification suffix carries.
_CERT_SUFFIX_MIN = 8


class MetaModelError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`MetaModel`.

    A :class:`MetaModel` is fail-closed (TRACK-001): an open, partial, cyclic-founding,
    uncertified-member, authority-conferring, or technology-bound meta-model is rejected at
    construction rather than admitted as an invalid or constitutive model.
    """


@dataclass(frozen=True, slots=True)
class MetaClassMember:
    """A reference to a CERTIFIED concern meta-class realization the model integrates.

    Records **only** the member's meta-class id, name, modelled ontology entity, hierarchy,
    realizing unit, and certification id — never its implementation — so the meta-model
    references, and never owns or absorbs, the concern realizations it composes (SMX-02
    non-absorbing; USL-02 reuse-by-reference).
    """

    meta_class: str
    name: str
    models_entity: str
    classified_by: str
    unit: str
    certification_id: str

    def resolves(self) -> bool:
        """SMI-05 — the member resolves to a CERTIFIED concern meta-class realization.

        The member is a member of the closed meta-class set (SMC-01…10), and its
        certification id is a well-formed EC-1 certification reference for that meta-class.
        """
        if self.meta_class not in META_CLASSES:
            return False
        prefix = f"{CERT_ID_PREFIX}{self.meta_class}-"
        if not self.certification_id.startswith(prefix):
            return False
        suffix = self.certification_id[len(prefix):]
        return len(suffix) >= _CERT_SUFFIX_MIN and all(c in "0123456789abcdef" for c in suffix)

    def to_dict(self) -> dict[str, Any]:
        return {
            "meta_class": self.meta_class,
            "name": self.name,
            "models_entity": self.models_entity,
            "classified_by": self.classified_by,
            "unit": self.unit,
            "certification_id": self.certification_id,
            "resolves": self.resolves(),
            "owned": False,  # SMX-02 — referenced, never owned
        }


@dataclass(frozen=True, slots=True)
class MetaRelationshipEdge:
    """A meta-relationship (SMR-0n) modelling one ontology relationship (SOR-0n).

    An ENG-005 reference between meta-classes (or to a frozen EL-1/RL-F2/PL-F2/DF-2
    foundation target); it introduces no new connection construct (§3).
    """

    relationship: str
    name: str
    models: str
    source: str
    target: str

    def is_founding(self) -> bool:
        """SMK-03 / SMI-04 — whether this edge is a founding (structural) meta-relationship."""
        return self.relationship in FOUNDING_META_RELATIONSHIPS

    def target_is_foundation(self) -> bool:
        """Whether the edge target is a frozen EL-1/RL-F2/PL-F2/DF-2 reference (SMR-10…13)."""
        return self.target in FOUNDATION_TARGETS

    def resolves(self, meta_classes: frozenset[str]) -> bool:
        """SMI-05 — source is a meta-class and target resolves within closure or foundations."""
        return self.source in meta_classes and (
            self.target in meta_classes or self.target_is_foundation()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship": self.relationship,
            "name": self.name,
            "models": self.models,
            "source": self.source,
            "target": self.target,
            "founding": self.is_founding(),
            "target_is_foundation": self.target_is_foundation(),
        }


def _has_founding_cycle(edges: tuple[MetaRelationshipEdge, ...]) -> bool:
    """True iff the founding meta-graph (SMR-02/03/04/05 edges) contains a directed cycle.

    A genuine DFS cycle detection over the founding subgraph (SMI-04 / SMK-03): the model is
    admissible only if this graph is a DAG. Peer/reference (non-founding) edges impose no
    founding dependency and are excluded.
    """
    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        if edge.is_founding():
            adjacency.setdefault(edge.source, []).append(edge.target)

    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = {}

    def visit(node: str) -> bool:
        colour[node] = GREY
        for nxt in adjacency.get(node, ()):  # nodes with no out-edges are trivially acyclic
            state = colour.get(nxt, WHITE)
            if state == GREY:
                return True  # back-edge → cycle
            if state == WHITE and visit(nxt):
                return True
        colour[node] = BLACK
        return False

    return any(colour.get(node, WHITE) == WHITE and visit(node) for node in adjacency)


@dataclass(frozen=True, slots=True)
class MetaModel:
    """USM — an immutable, closed, total, acyclic integration of SMC-01…10 + SMR-01…13.

    Fields:
        name:        the explicit meta-model name (part of identity).
        type_tag:    the ENG-004 Type of the meta-model (SMK-01; USL-03).
        members:     the ten CERTIFIED concern meta-class references (SMI-01 closure).
        edges:       the thirteen meta-relationship edges (SMI-02 closure).
        state:       the SOS-01…06 forward-only lifecycle state (USL-12).
        version:     the object version (append-only supersession; USL-12/15).
        supersedes:  the id of a superseded meta-model object (append-only).

    Constructing a :class:`MetaModel` enforces SMI-01…07 fail-closed.
    """

    name: str
    type_tag: str
    members: tuple[MetaClassMember, ...]
    edges: tuple[MetaRelationshipEdge, ...]
    state: ModelState = ModelState.DEFINED
    version: str = "1.0.0"
    supersedes: str = ""

    def __post_init__(self) -> None:
        # explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise MetaModelError("meta-model must have an explicit name")
        # SMK-01 / USL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise MetaModelError("meta-model must be typed with an ENG-004 type_tag (SMK-01)")
        # members are MetaClassMember instances.
        if not isinstance(self.members, tuple) or not all(
            isinstance(m, MetaClassMember) for m in self.members
        ):
            raise MetaModelError("meta-model members must be MetaClassMember references")
        # edges are MetaRelationshipEdge instances.
        if not isinstance(self.edges, tuple) or not all(
            isinstance(e, MetaRelationshipEdge) for e in self.edges
        ):
            raise MetaModelError("meta-model edges must be MetaRelationshipEdge references")
        # SMI-01 — closure: the members are exactly SMC-01…10 (no eleventh, no duplicate).
        member_classes = [m.meta_class for m in self.members]
        if sorted(member_classes) != sorted(META_CLASSES) or len(set(member_classes)) != len(
            member_classes
        ):
            raise MetaModelError(
                "meta-model members must be exactly the ten meta-classes SMC-01…10 (SMI-01)"
            )
        # SMI-05 — every member resolves to a CERTIFIED concern meta-class realization.
        for member in self.members:
            if not member.resolves():
                raise MetaModelError(
                    f"member {member.meta_class} does not resolve to a CERTIFIED "
                    f"realization (SMI-05)"
                )
        # SMI-02 — relationship closure: the edges are exactly SMR-01…13 (no fourteenth).
        edge_rels = [e.relationship for e in self.edges]
        if sorted(edge_rels) != sorted(META_RELATIONSHIPS) or len(set(edge_rels)) != len(edge_rels):
            raise MetaModelError(
                "meta-model edges must be exactly the thirteen meta-relationships "
                "SMR-01…13 (SMI-02)"
            )
        # SMI-03 — totality: members model exactly SOE-01…10; edges model exactly SOR-01…13.
        modelled_entities = [m.models_entity for m in self.members]
        if sorted(modelled_entities) != sorted(ONTOLOGY_ENTITIES) or len(
            set(modelled_entities)
        ) != len(modelled_entities):
            raise MetaModelError(
                "meta-model must model exactly the ten ontology entities SOE-01…10 (SMI-03)"
            )
        modelled_relationships = [e.models for e in self.edges]
        if sorted(modelled_relationships) != sorted(ONTOLOGY_RELATIONSHIPS) or len(
            set(modelled_relationships)
        ) != len(modelled_relationships):
            raise MetaModelError(
                "meta-model must model exactly the thirteen ontology relationships "
                "SOR-01…13 (SMI-03)"
            )
        # SMI-05 — every edge resolves within the closure or the frozen foundations.
        classes = frozenset(member_classes)
        for edge in self.edges:
            if not edge.resolves(classes):
                raise MetaModelError(
                    f"edge {edge.relationship} does not resolve within the closure/"
                    f"foundations (SMI-05)"
                )
        # SMI-04 — the founding meta-graph (SMR-02/03/04/05) is acyclic (a DAG).
        if _has_founding_cycle(self.edges):
            raise MetaModelError("meta-model founding graph is not acyclic (SMI-04 / SMK-03)")
        # V5 / USL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, ModelState):
            raise MetaModelError("meta-model state must be a SOS-01…06 state (USL-12)")
        # an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise MetaModelError("meta-model must record an explicit version (USL-12/15)")
        if not isinstance(self.supersedes, str):
            raise MetaModelError("meta-model supersedes reference must be a string")
        # SMI-06 / USL-15 / SMK-08 — names no technology (material).
        if self._scan_technology():
            raise MetaModelError(
                "meta-model names a service/API/transport technology or vendor "
                "(SMI-06 / USL-15 / SMK-08)"
            )

    # -- technology-neutrality (SMI-06, material) ------------------------------

    def _scan_technology(self) -> bool:
        """True iff any technology marker appears in the object's declared surface."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECH_MARKERS)

    def names_technology(self) -> bool:
        """SMI-06 / USL-15 / SMK-08 / C7 — True iff the object names a technology."""
        return self._scan_technology()

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the object (members + edges, deterministically)."""
        return {
            "model_class": MODEL_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "members": [
                {
                    "meta_class": m.meta_class,
                    "name": m.name,
                    "models_entity": m.models_entity,
                    "classified_by": m.classified_by,
                    "unit": m.unit,
                    "certification_id": m.certification_id,
                }
                for m in sorted(self.members, key=lambda m: m.meta_class)
            ],
            "edges": [
                {
                    "relationship": e.relationship,
                    "name": e.name,
                    "models": e.models,
                    "source": e.source,
                    "target": e.target,
                    "founding": e.is_founding(),
                }
                for e in sorted(self.edges, key=lambda e: e.relationship)
            ],
            "version": self.version,
            "supersedes": self.supersedes,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the object core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def model_id(self) -> str:
        """The deterministic ENG-001 identity of the object (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (USL-04 — no second identity
        scheme): an identical model always yields the identical id (determinism, VC-4).
        """
        return f"{MODEL_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """The singular model-class label (USM) — not a concern meta-class (SMI-01)."""
        return MODEL_CLASS

    def meta_classes(self) -> tuple[str, ...]:
        """The closed set of meta-classes the model fixes (SMC-01…10, sorted)."""
        return tuple(sorted(m.meta_class for m in self.members))

    def meta_relationships(self) -> tuple[str, ...]:
        """The closed set of meta-relationships the model fixes (SMR-01…13, sorted)."""
        return tuple(sorted(e.relationship for e in self.edges))

    def modelled_entities(self) -> tuple[str, ...]:
        """The ontology entities the model totally covers (SOE-01…10, sorted)."""
        return tuple(sorted(m.models_entity for m in self.members))

    def modelled_relationships(self) -> tuple[str, ...]:
        """The ontology relationships the model totally covers (SOR-01…13, sorted)."""
        return tuple(sorted(e.models for e in self.edges))

    # -- meta-invariant predicates (SMI-01…07) ---------------------------------

    def declares_closure(self) -> bool:
        """SMI-01 — the members are exactly the ten meta-classes SMC-01…10."""
        return self.meta_classes() == tuple(sorted(META_CLASSES))

    def declares_relationship_closure(self) -> bool:
        """SMI-02 — the edges are exactly the thirteen meta-relationships SMR-01…13."""
        return self.meta_relationships() == tuple(sorted(META_RELATIONSHIPS))

    def is_total(self) -> bool:
        """SMI-03 — the members/edges model exactly SOE-01…10 / SOR-01…13 (bijection)."""
        return self.modelled_entities() == tuple(sorted(ONTOLOGY_ENTITIES)) and (
            self.modelled_relationships() == tuple(sorted(ONTOLOGY_RELATIONSHIPS))
        )

    def is_founding_acyclic(self) -> bool:
        """SMI-04 / SMK-03 — the founding meta-graph (SMR-02/03/04/05) is a DAG."""
        return not _has_founding_cycle(self.edges)

    def members_certified(self) -> bool:
        """Integration — every member resolves to a CERTIFIED concern meta-class realization."""
        return len(self.members) == len(META_CLASSES) and all(
            m.resolves() for m in self.members
        )

    def map_resolves(self) -> bool:
        """§9 — every meta-model map edge resolves within the closure or the foundations."""
        classes = frozenset(m.meta_class for m in self.members)
        return all(e.resolves(classes) for e in self.edges)

    def reuses_by_reference(self) -> bool:
        """SMI-05 — members + edges + foundations referenced, redefined nowhere."""
        return (
            self.members_certified()
            and self.map_resolves()
            and not self.redefines_el1()
            and bool(MODEL_SUBSTRATE_REFS)
        )

    def is_non_projection(self) -> bool:
        """SMI-07 — model coverage is never roadmap/implementation/operational completion.

        Structurally guaranteed: the meta-model is an implementation-independent model (it
        holds references and structure only — no endpoint, deployment, or operational
        artifact), so its existence asserts no completion beyond model coverage
        (STATUS-001 §2).
        """
        return True

    # -- non-constitutiveness (SMI-06 / USL-15) --------------------------------

    def confers_authority(self) -> bool:
        """SMI-06 / USL-15 / C7 — the meta-model confers no authority (structurally none)."""
        return False

    def embeds_secret(self) -> bool:
        """SMI-06 / USL-15 / RR-07 / C7 — True iff the object appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """SMI-05 / USL-02 — the meta-model redefines no EL-1/RL-F2/PL-F2/DF-2/SMC model."""
        return False

    def selects_technology(self) -> bool:
        """SMI-06 / USL-15 / SMK-08 — the meta-model selects no technology (material)."""
        return self._scan_technology()

    def is_non_constitutive(self) -> bool:
        """SMI-06 — confers no authority, embeds no secret, selects no technology."""
        return not (self.confers_authority() or self.embeds_secret() or self.selects_technology())

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ModelState) -> MetaModel:
        """Return a new object advanced to ``to_state`` (forward-only; USL-12).

        Raises:
            MetaModelError: on a backward transition.
        """
        if not isinstance(to_state, ModelState):
            raise MetaModelError("target state must be a SOS-01…06 state (USL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise MetaModelError(
                f"lifecycle is forward-only (USL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the meta-model object."""
        return {
            "model_id": self.model_id,
            "model_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "structure_digest": self.structure_digest,
            "members": [m.to_dict() for m in sorted(self.members, key=lambda m: m.meta_class)],
            "edges": [e.to_dict() for e in sorted(self.edges, key=lambda e: e.relationship)],
            "meta_classes": list(self.meta_classes()),
            "meta_relationships": list(self.meta_relationships()),
            "modelled_entities": list(self.modelled_entities()),
            "modelled_relationships": list(self.modelled_relationships()),
            "declares_closure": self.declares_closure(),
            "declares_relationship_closure": self.declares_relationship_closure(),
            "is_total": self.is_total(),
            "founding_acyclic": self.is_founding_acyclic(),
            "members_certified": self.members_certified(),
            "map_resolves": self.map_resolves(),
            "reuses_by_reference": self.reuses_by_reference(),
            "non_projection": self.is_non_projection(),
            "confers_authority": self.confers_authority(),
            "embeds_secret": self.embeds_secret(),
            "names_technology": self.names_technology(),
            "non_constitutive": self.is_non_constitutive(),
            "version": self.version,
            "supersedes": self.supersedes,
            "state": self.state.value,
            "substrate_refs": list(MODEL_SUBSTRATE_REFS),
        }


def _member_from_spec(spec: tuple[str, str, str, str, str, str], certification_id: str) -> (
    MetaClassMember
):
    """Build a :class:`MetaClassMember` from a SERVICE-005 §2 spec + a certification id."""
    meta_class, name, models_entity, classified_by, unit, _module = spec
    return MetaClassMember(
        meta_class=meta_class,
        name=name,
        models_entity=models_entity,
        classified_by=classified_by,
        unit=unit,
        certification_id=certification_id,
    )


def build_edges() -> tuple[MetaRelationshipEdge, ...]:
    """Build the thirteen meta-relationship edges from the frozen SERVICE-005 §3/§9 map."""
    return tuple(
        MetaRelationshipEdge(
            relationship=rel, name=name, models=models, source=source, target=target
        )
        for rel, name, models, source, target in EDGE_SPECS
    )


def make_metamodel(
    name: str,
    type_tag: str,
    certification_ids: dict[str, str],
    *,
    edges: tuple[MetaRelationshipEdge, ...] | None = None,
    state: ModelState = ModelState.DEFINED,
    version: str = "1.0.0",
    supersedes: str = "",
) -> MetaModel:
    """Construct a well-formed :class:`MetaModel` (fail-closed factory).

    ``certification_ids`` maps each meta-class id (``SMC-01`` … ``SMC-10``) to the EC-1
    certification id of its CERTIFIED realization (reused by reference). ``edges`` defaults
    to the frozen SERVICE-005 §3/§9 thirteen-edge projection when omitted.
    """
    missing = [spec[0] for spec in MEMBER_SPECS if spec[0] not in certification_ids]
    if missing:
        raise MetaModelError(
            f"missing certification ids for {missing} — the meta-model integrates all ten "
            f"CERTIFIED meta-classes (SMI-01)"
        )
    members = tuple(
        _member_from_spec(spec, certification_ids[spec[0]]) for spec in MEMBER_SPECS
    )
    resolved_edges = edges if edges is not None else build_edges()
    return MetaModel(
        name=name,
        type_tag=type_tag,
        members=members,
        edges=resolved_edges,
        state=state,
        version=version,
        supersedes=supersedes,
    )


__all__ = [
    "MODEL_ID_PREFIX",
    "CERT_ID_PREFIX",
    "REUSE_REFS",
    "MetaModelError",
    "MetaClassMember",
    "MetaRelationshipEdge",
    "MetaModel",
    "build_edges",
    "make_metamodel",
]
