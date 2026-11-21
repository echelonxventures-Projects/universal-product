"""EC3-B10-U11 — The Universal Data Meta-Model construct (UDM; DATA-005).

Realizes the **model-of-the-model** (DATA-005 §1): the executable Universal Data
Meta-Model (UDM) that **integrates** the ten CERTIFIED concern meta-classes (DMC-01…10;
units U01…U10) and the twelve meta-relationships (DMR-01…12) into one closed, total,
acyclic, reuse-integral, non-constitutive, non-projective model, and thereby serves as the
conformance gate for the whole Band-10 Data layer.

The Universal Data Meta-Model is **not** an eleventh meta-class — DMI-01 admits no
meta-class outside DMC-01…10. It is the singular model artifact that *fixes* the ten. It
is **additive over — and composes *by reference*** the CERTIFIED EC-1 foundation and the
ten CERTIFIED concern-meta-class realizations (UDL-02 / DMI-05):

* Each :class:`MetaClassMember` is a **reference to a CERTIFIED concern meta-class
  realization** (meta-class id + ontology entity + hierarchy + realizing unit +
  certification id) — **never owned, embedded, or copied** (DMX-02 non-absorbing).
* Each :class:`MetaRelationshipEdge` is a **meta-relationship viewed as an ENG-005
  reference** between meta-classes (or to the frozen EL-1/RL-F2/PL-F2 foundations) — it
  introduces no new connection construct.
* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.content_hash`) — no second identity scheme.

The construct enforces the seven meta-invariants **fail-closed** at construction
(DATA-005 §8):

* **DMI-01 Closure** — the members are exactly DMC-01…10 (no eleventh, no duplicate).
* **DMI-02 Relationship closure** — the edges are exactly DMR-01…12.
* **DMI-03 Totality** — the members model exactly DOE-01…10 and the edges model exactly
  DOR-01…12 (a bijection each).
* **DMI-04 Acyclicity** — the founding meta-graph (DMR-01/04) is a DAG.
* **DMI-05 Reuse integrity** — every member resolves to a CERTIFIED unit and every edge
  target resolves within the closure or the frozen foundations; nothing is redefined.
* **DMI-06 Non-constitutiveness** — the model confers no authority, embeds no secret, and
  names no technology.
* **DMI-07 Non-projection** — the model records that model coverage is never roadmap,
  implementation, storage, deployment, or operational completion (STATUS-001 §2).

An ill-formed, open, partial, cyclic-founding, uncertified-member, authority-conferring,
or technology-bound meta-model cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from data.model_meta import (
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

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Universal Data Meta-Model (mirrors UCOS-<K>).
MODEL_ID_PREFIX = "UCOS-METAMODEL"

#: The certification-id prefix a CERTIFIED concern meta-class member presents (ENG-001).
CERT_ID_PREFIX = "UCOS-CERT-"

#: The map of EC-1 / DMC primitives this construct reuses *by reference* (never redefined).
#: Recorded for the reuse-integrity check (UDL-02 / DMI-05 / DMI-05-evidence).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the meta-model record)",
    "ENG-004": "meta-class + meta-relationship typing discipline (ENG-004)",
    "ENG-005": "meta-relationship edges + member certification references (§3 / DMR-01…12)",
    "DMC-01..10": "the ten CERTIFIED concern-meta-class realizations — referenced, not owned",
    "RL-F2": "RUNTIME behaviour concern — bound by reference (DMR-11 behaves-as)",
    "PL-F2": "PLATFORM composition concern — bound by reference (DMR-12 composed-as)",
}

#: Conservative secret markers used to enforce UDL-15 / DMI-06 (embed no secret).
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

#: Conservative data/storage/relationship-technology markers used to enforce **UDL-15 /
#: DMI-06 / DMK-08** (the meta-model selects no technology or vendor). A meta-model naming
#: any of these is rejected fail-closed — it is an implementation-independent model only
#: (DATA-005 CLASSIFICATION). Markers are chosen to avoid collision with the hexadecimal
#: alphabet used by content digests (they contain characters outside 0-9a-f).
_TECH_MARKERS: tuple[str, ...] = (
    "postgres",
    "mysql",
    "mongodb",
    "dynamodb",
    "cassandra",
    "sqlite",
    "redis",
    "sql",
    "cypher",
    "gremlin",
    "sparql",
    "neo4j",
    "sqlalchemy",
    "hibernate",
    "parquet",
    "protobuf",
    "avro",
    "kafka",
    "s3 bucket",
    "filesystem path",
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
    references, and never owns or absorbs, the concern realizations it composes (DMX-02
    non-absorbing; UDL-02 reuse-by-reference).
    """

    meta_class: str
    name: str
    models_entity: str
    classified_by: str
    unit: str
    certification_id: str

    def resolves(self) -> bool:
        """DMI-05 — the member resolves to a CERTIFIED concern meta-class realization.

        The member is a member of the closed meta-class set (DMC-01…10), and its
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
            "owned": False,  # DMX-02 — referenced, never owned
        }


@dataclass(frozen=True, slots=True)
class MetaRelationshipEdge:
    """A meta-relationship (DMR-0n) modelling one ontology relationship (DOR-0n).

    An ENG-005 reference between meta-classes (or to a frozen EL-1/RL-F2/PL-F2 foundation
    target); it introduces no new connection construct (§3).
    """

    relationship: str
    name: str
    models: str
    source: str
    target: str

    def is_founding(self) -> bool:
        """DMK-03 / DMI-04 — whether this edge is a founding (structural) meta-relationship."""
        return self.relationship in FOUNDING_META_RELATIONSHIPS

    def target_is_foundation(self) -> bool:
        """Whether the edge target is a frozen EL-1/RL-F2/PL-F2 reference (DMR-10/11/12)."""
        return self.target in FOUNDATION_TARGETS

    def resolves(self, meta_classes: frozenset[str]) -> bool:
        """DMI-05 — source is a meta-class and target resolves within closure or foundations."""
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
    """True iff the founding meta-graph (DMR-01/04 edges) contains a directed cycle.

    A genuine DFS cycle detection over the founding subgraph (DMI-04 / DMK-03): the model is
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
    """UDM — an immutable, closed, total, acyclic integration of DMC-01…10 + DMR-01…12.

    Fields:
        name:        the explicit meta-model name (part of identity).
        type_tag:    the ENG-004 Type of the meta-model (DMK-01; UDL-03).
        members:     the ten CERTIFIED concern meta-class references (DMI-01 closure).
        edges:       the twelve meta-relationship edges (DMI-02 closure).
        state:       the DOS-01…05 forward-only lifecycle state (UDL-12).
        version:     the object version (append-only supersession; UDL-12/15).
        supersedes:  the id of a superseded meta-model object (append-only).

    Constructing a :class:`MetaModel` enforces DMI-01…07 fail-closed.
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
        # DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise MetaModelError("meta-model must be typed with an ENG-004 type_tag (DMK-01)")
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
        # DMI-01 — closure: the members are exactly DMC-01…10 (no eleventh, no duplicate).
        member_classes = [m.meta_class for m in self.members]
        if sorted(member_classes) != sorted(META_CLASSES) or len(set(member_classes)) != len(
            member_classes
        ):
            raise MetaModelError(
                "meta-model members must be exactly the ten meta-classes DMC-01…10 (DMI-01)"
            )
        # DMI-05 — every member resolves to a CERTIFIED concern meta-class realization.
        for member in self.members:
            if not member.resolves():
                raise MetaModelError(
                    f"member {member.meta_class} does not resolve to a CERTIFIED "
                    f"realization (DMI-05)"
                )
        # DMI-02 — relationship closure: the edges are exactly DMR-01…12 (no thirteenth).
        edge_rels = [e.relationship for e in self.edges]
        if sorted(edge_rels) != sorted(META_RELATIONSHIPS) or len(set(edge_rels)) != len(edge_rels):
            raise MetaModelError(
                "meta-model edges must be exactly the twelve meta-relationships DMR-01…12 (DMI-02)"
            )
        # DMI-03 — totality: members model exactly DOE-01…10; edges model exactly DOR-01…12.
        modelled_entities = [m.models_entity for m in self.members]
        if sorted(modelled_entities) != sorted(ONTOLOGY_ENTITIES) or len(
            set(modelled_entities)
        ) != len(modelled_entities):
            raise MetaModelError(
                "meta-model must model exactly the ten ontology entities DOE-01…10 (DMI-03)"
            )
        modelled_relationships = [e.models for e in self.edges]
        if sorted(modelled_relationships) != sorted(ONTOLOGY_RELATIONSHIPS) or len(
            set(modelled_relationships)
        ) != len(modelled_relationships):
            raise MetaModelError(
                "meta-model must model exactly the twelve ontology relationships "
                "DOR-01…12 (DMI-03)"
            )
        # DMI-05 — every edge resolves within the closure or the frozen foundations.
        classes = frozenset(member_classes)
        for edge in self.edges:
            if not edge.resolves(classes):
                raise MetaModelError(
                    f"edge {edge.relationship} does not resolve within the closure/"
                    f"foundations (DMI-05)"
                )
        # DMI-04 — the founding meta-graph (DMR-01/04) is acyclic (a DAG).
        if _has_founding_cycle(self.edges):
            raise MetaModelError("meta-model founding graph is not acyclic (DMI-04 / DMK-03)")
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, ModelState):
            raise MetaModelError("meta-model state must be a DOS-01…05 state (UDL-12)")
        # an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise MetaModelError("meta-model must record an explicit version (UDL-12/15)")
        if not isinstance(self.supersedes, str):
            raise MetaModelError("meta-model supersedes reference must be a string")
        # DMI-06 / UDL-15 / DMK-08 — names no technology (material).
        if self._scan_technology():
            raise MetaModelError(
                "meta-model names a data/storage/relationship technology or vendor "
                "(DMI-06 / UDL-15 / DMK-08)"
            )

    # -- technology-neutrality (DMI-06, material) ------------------------------

    def _scan_technology(self) -> bool:
        """True iff any technology marker appears in the object's declared surface."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECH_MARKERS)

    def names_technology(self) -> bool:
        """DMI-06 / UDL-15 / DMK-08 / C6 — True iff the object names a technology."""
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

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second identity
        scheme): an identical model always yields the identical id (determinism, VC-4).
        """
        return f"{MODEL_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005) -----------------------------------

    @property
    def meta_class(self) -> str:
        """The singular model-class label (UDM) — not a concern meta-class (DMI-01)."""
        return MODEL_CLASS

    def meta_classes(self) -> tuple[str, ...]:
        """The closed set of meta-classes the model fixes (DMC-01…10, sorted)."""
        return tuple(sorted(m.meta_class for m in self.members))

    def meta_relationships(self) -> tuple[str, ...]:
        """The closed set of meta-relationships the model fixes (DMR-01…12, sorted)."""
        return tuple(sorted(e.relationship for e in self.edges))

    def modelled_entities(self) -> tuple[str, ...]:
        """The ontology entities the model totally covers (DOE-01…10, sorted)."""
        return tuple(sorted(m.models_entity for m in self.members))

    def modelled_relationships(self) -> tuple[str, ...]:
        """The ontology relationships the model totally covers (DOR-01…12, sorted)."""
        return tuple(sorted(e.models for e in self.edges))

    # -- meta-invariant predicates (DMI-01…07) ---------------------------------

    def declares_closure(self) -> bool:
        """DMI-01 — the members are exactly the ten meta-classes DMC-01…10."""
        return self.meta_classes() == tuple(sorted(META_CLASSES))

    def declares_relationship_closure(self) -> bool:
        """DMI-02 — the edges are exactly the twelve meta-relationships DMR-01…12."""
        return self.meta_relationships() == tuple(sorted(META_RELATIONSHIPS))

    def is_total(self) -> bool:
        """DMI-03 — the members/edges model exactly DOE-01…10 / DOR-01…12 (bijection)."""
        return self.modelled_entities() == tuple(sorted(ONTOLOGY_ENTITIES)) and (
            self.modelled_relationships() == tuple(sorted(ONTOLOGY_RELATIONSHIPS))
        )

    def is_founding_acyclic(self) -> bool:
        """DMI-04 / DMK-03 — the founding meta-graph (DMR-01/04) is a DAG."""
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
        """DMI-05 — members + edges + foundations referenced, redefined nowhere."""
        return (
            self.members_certified()
            and self.map_resolves()
            and not self.redefines_el1()
            and bool(MODEL_SUBSTRATE_REFS)
        )

    def is_non_projection(self) -> bool:
        """DMI-07 — model coverage is never roadmap/implementation/operational completion.

        Structurally guaranteed: the meta-model is an implementation-independent model
        (it holds references and structure only — no storage, deployment, or operational
        artifact), so its existence asserts no completion beyond model coverage
        (STATUS-001 §2).
        """
        return True

    # -- non-constitutiveness (DMI-06 / UDL-15) --------------------------------

    def confers_authority(self) -> bool:
        """DMI-06 / UDL-15 / C7 — the meta-model confers no authority (structurally none)."""
        return False

    def embeds_secret(self) -> bool:
        """DMI-06 / UDL-15 / RR-07 / C7 — True iff the object appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """DMI-05 / UDL-02 — the meta-model redefines no EL-1/RL-F2/PL-F2/DMC model."""
        return False

    def selects_technology(self) -> bool:
        """DMI-06 / UDL-15 / DMK-08 — the meta-model selects no technology (material)."""
        return self._scan_technology()

    def is_non_constitutive(self) -> bool:
        """DMI-06 — confers no authority, embeds no secret, selects no technology."""
        return not (self.confers_authority() or self.embeds_secret() or self.selects_technology())

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: ModelState) -> MetaModel:
        """Return a new object advanced to ``to_state`` (forward-only; UDL-12).

        Raises:
            MetaModelError: on a backward transition.
        """
        if not isinstance(to_state, ModelState):
            raise MetaModelError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise MetaModelError(
                f"lifecycle is forward-only (UDL-12): "
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
    """Build a :class:`MetaClassMember` from a DATA-005 §2 spec + a certification id."""
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
    """Build the twelve meta-relationship edges from the frozen DATA-005 §3/§9 projection."""
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

    ``certification_ids`` maps each meta-class id (``DMC-01`` … ``DMC-10``) to the EC-1
    certification id of its CERTIFIED realization (reused by reference). ``edges`` defaults
    to the frozen DATA-005 §3/§9 twelve-edge projection when omitted.
    """
    missing = [spec[0] for spec in MEMBER_SPECS if spec[0] not in certification_ids]
    if missing:
        raise MetaModelError(
            f"missing certification ids for {missing} — the meta-model integrates all ten "
            f"CERTIFIED meta-classes (DMI-01)"
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
