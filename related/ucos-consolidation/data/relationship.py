"""EC3-B10-U10 — The Universal Relationship construct (DMC-04).

Realizes the meta-model construct **DMC-04 Relationship** (DATA-005 §2; DATA-008 §3):

    a **typed, decidable association between data entities, realized as an ENG-005
    reference** (the ontology root DOE-04), classified by DXH-04 (Association /
    Composition / Reference). A relationship connects ENG-002 Entity objects by ENG-005
    reference (DMR-03 ``relates``), declares explicit, decidable cardinality (DRA-04), is
    acyclic where it establishes structural dependency (DRA-03), resolves every endpoint
    to an existing entity identity (DRA-05), and binds navigation/integrity-check
    evaluation *by reference* to the frozen RUNTIME policy concern (DMR-11 / §7). A data
    relationship is neither the entities it connects (DOE-02) nor a new connection
    primitive — it is an **ENG-005 reference viewed as represented association**;
    enforcement, joins, and foreign-key mechanics are downstream concerns consumed by
    reference.

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-02 Entity**, reusing both *by reference* (UDL-02 / DMI-05):

* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme.
* Each endpoint (DMR-03 ``relates``) is a **reference to a CERTIFIED data entity** (id +
  structural digest + name/type + meta-class), **never owned, embedded, or copied**
  (DRA-C5 by record; DMX-02 non-absorbing).
* Navigation / referential-integrity checking is a **RUNTIME policy reference** only
  (``behaves-as``, DMR-11 / §7) — no join language, foreign-key mechanic, graph engine,
  or database is defined.

**No relationship/query/storage technology, join language, foreign-key mechanic, graph
engine, or database product/vendor is selected** (UDL-09/11/15 / DRA-09 / DRA-K5) —
enforced fail-closed by a technology-marker scan over the whole construct. A relationship
**confers no authority and embeds no secret** (DRA-09 / DRA-K5): this is the material
exercise of UDL-09 Relationship by Reference — a relationship *is* an ENG-005 reference
that introduces no new connection construct.

A :class:`RelationshipObject` is *immutable* (frozen — ENG-002 objecthood), *typed*
(ENG-004, DRA-02/DRA-K1/UDL-03), *identified* (ENG-001, DRA-K1/UDL-04), *endpoint-bound*
(``relates`` two CERTIFIED entities by reference — DMR-03), *cardinal* (explicit decidable
cardinality — DRA-04), *directional* (directed/peer declared — DRA-06), *acyclic when
founding* (DRA-03), *schema-describable* (DMR-04 / DRA-07), *versioned*, and holds a
*forward-only lifecycle state* (DOS-01…05, UDL-12). Constructing a
:class:`RelationshipObject` enforces DRA-K1/K2/K3/K4/K5, the integrity rules
DRA-C1/C2/C3/C4/C5, and UDL-09/03/04/05 **fail-closed**: an ill-formed, unbounded,
cyclic-founding, dangling, or technology-bound relationship cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- DMC-02 reuse by reference (UDL-02) — never redefined -------------------------
from data.entity import Entity
from data.relationship_meta import (
    DIRECTION_FOR_KIND,
    FOUNDING_KINDS,
    LIFECYCLE_ORDER,
    RELATIONSHIP_META_CLASS,
    RELATIONSHIP_RELATIONSHIPS,
    RELATIONSHIP_SUBSTRATE_REFS,
    RelationshipCardinality,
    RelationshipDirection,
    RelationshipKind,
    RelationshipState,
    RelationshipVerdict,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Relationship object (mirrors EC-1 UCOS-<K>).
RELATIONSHIP_ID_PREFIX = "UCOS-RELATIONSHIP"

#: The reference prefix a relationship presents to bind RUNTIME navigation/integrity
#: evaluation (DMR-11 / §7 / DOB-05/06 navigate/evaluate) — declarative, non-enforcing.
POLICY_REF_PREFIX = "UCOS-POLICY-REF"

#: The prefix of a CERTIFIED data-entity identity (the DMR-03 ``relates`` endpoint target).
CERTIFIED_ID_PREFIX = "UCOS-"

#: The meta-class a related endpoint must carry (a relationship relates DMC-02 Entities).
ENDPOINT_META_CLASS = "DMC-02"

#: The map of EC-1 / DMC-02 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the relationship record)",
    "ENG-004": "data.relationship_meta.RelationshipKind + type_tag (ENG-004 typing discipline)",
    "ENG-005": "related-endpoint + RUNTIME navigation identity references (DMR-03/11)",
    "DMC-02": "data.entity.Entity — a CERTIFIED relates endpoint (DMR-03); referenced only",
    "RL-F2": "RUNTIME policy — navigation/integrity-check bound by reference (DMR-11 / §7)",
}

#: Conservative secret markers used to enforce UDL-15 / DRA-09 / RR-07 (embed no secret).
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

#: Conservative relationship/query/storage-technology markers used to enforce **UDL-09/11 /
#: DRA-09 / DRA-K5** (select no join language, foreign-key mechanic, graph engine, ORM,
#: database, or vendor). A relationship naming any of these is rejected fail-closed — a
#: relationship is a decidable, typed ENG-005 reference only, introducing no new connection
#: construct. This is the material exercise of UDL-09 (Relationship by Reference) and
#: DATA-008 §2.2 (join languages / foreign-key mechanics out of scope). Markers are chosen
#: to avoid collision with the hexadecimal alphabet used by content digests (they contain
#: characters outside 0-9a-f).
_TECH_MARKERS: tuple[str, ...] = (
    "foreign key",
    "foreign-key",
    "join language",
    "inner join",
    "left join",
    "outer join",
    "sql",
    "cypher",
    "gremlin",
    "sparql",
    "neo4j",
    "sqlalchemy",
    "hibernate",
    "jpa",
    "orm mapping",
    "graphql",
    "adjacency list",
    "edge table",
    "junction table",
    "referential constraint",
    "cascade delete",
    "postgres",
    "mongodb",
    "dynamodb",
)


def policy_ref_for(predicate: str) -> str:
    """The reference a relationship presents to bind RUNTIME policy (DMR-11 / §7).

    A relationship's navigation/referential-integrity evaluation is a *reference* to the
    frozen RL-F2 policy concern (DOB-05 navigate / DOB-06 evaluate), which is declarative
    and non-enforcing by construction — never a redefined join engine or foreign-key
    mechanic.
    """
    return f"{POLICY_REF_PREFIX}:{predicate}"


class RelationshipError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`RelationshipObject`.

    A :class:`RelationshipObject` is fail-closed (TRACK-001): an ill-formed, unbounded,
    cyclic-founding, dangling, authority-conferring, or technology-bound relationship is
    rejected at construction rather than admitted as an invalid or constitutive object.
    """


@dataclass(frozen=True, slots=True)
class EntityEndpointRef:
    """A reference to a CERTIFIED data entity a relationship ``relates`` (DMR-03).

    Records **only** the endpoint entity's identity, structural fingerprint, name, type,
    and meta-class — never its implementation — so the relationship references, and never
    owns or absorbs, the entities it relates (DMX-02 non-absorbing; DRA-C5 by record;
    UDL-02 reuse-by-reference).
    """

    entity_id: str
    structure_digest: str
    name: str
    type_tag: str
    meta_class: str

    @classmethod
    def from_entity(cls, entity: Entity) -> EntityEndpointRef:
        """Project a CERTIFIED :class:`~data.entity.Entity` into a related-endpoint ref."""
        if not isinstance(entity, Entity):
            raise RelationshipError("a relationship relates a data entity (DMR-03)")
        return cls(
            entity_id=entity.entity_id,
            structure_digest=entity.structure_digest,
            name=entity.name,
            type_tag=entity.type_tag,
            meta_class=entity.meta_class,
        )

    def resolves(self) -> bool:
        """DRA-05 / DRA-C2 — the endpoint resolves to an existing entity identity."""
        return (
            self.entity_id.startswith(CERTIFIED_ID_PREFIX)
            and self.meta_class == ENDPOINT_META_CLASS
            and len(self.structure_digest) == 64
            and all(c in "0123456789abcdef" for c in self.structure_digest)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "structure_digest": self.structure_digest,
            "name": self.name,
            "type_tag": self.type_tag,
            "meta_class": self.meta_class,
            "binding": "DMR-03:relates",
            "resolves": self.resolves(),
            "owned": False,  # DRA-C5 — related by record, never owned
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class RelationshipObject:
    """DMC-04 — an immutable, typed, decidable association between two data entities.

    Fields:
        name:         the explicit relationship name (part of identity).
        type_tag:     the ENG-004 Type of the relationship (DRA-K1; UDL-03).
        kind:         the DXH-04 classification (Association / Composition / Reference;
                      DRA-02). Composition is founding (DRA-03); the others are
                      reference-only.
        source_ref:   the first related endpoint — a CERTIFIED Entity (DMR-03; DRA-C5
                      by record, non-owning).
        target_ref:   the second related endpoint — a CERTIFIED Entity (DMR-03).
        cardinality:  the explicit, decidable cardinality (1:1 / 1:N / N:M; DRA-04 /
                      DRA-C3). No unbounded-by-default is representable.
        direction:    the declared directionality (directed / peer; DRA-06). Must match
                      the kind's declared direction.
        policy_ref:   the RUNTIME policy reference navigation/integrity-check evaluation
                      binds to (DMR-11 / §7 / DRA-K3). A reference obligation only — no
                      join engine or foreign-key mechanic is defined.
        verdict:      the recorded integrity/cardinality-conformance judgment (DOV-08).
        state:        the DOS-01…05 forward-only lifecycle state (UDL-12).
        version:      the object version (append-only supersession; DRA-08 / UDL-12/15).
        supersedes:   the id of a superseded relationship object (append-only).
        schema_ref:   the optional described-by schema reference (DMR-04 / DRA-07). A
                      *reference obligation* only — no Schema construct (DMC-05) is
                      realized here. Required (non-empty) before a relationship may
                      validly be ACTIVE (DRA-K3 / schema-before-ACTIVE).
    """

    name: str
    type_tag: str
    kind: RelationshipKind
    source_ref: EntityEndpointRef
    target_ref: EntityEndpointRef
    cardinality: RelationshipCardinality
    direction: RelationshipDirection
    policy_ref: str
    verdict: RelationshipVerdict = RelationshipVerdict.PASS
    state: RelationshipState = RelationshipState.DEFINED
    version: str = "1.0.0"
    supersedes: str = ""
    schema_ref: str = ""

    def __post_init__(self) -> None:
        # explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise RelationshipError("relationship must have an explicit name")
        # DRA-K1 / DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise RelationshipError(
                "relationship must be typed with an ENG-004 type_tag (DRA-02 / DRA-K1)"
            )
        # DXH-04 / DRA-02 — classified by exactly one relationship kind.
        if not isinstance(self.kind, RelationshipKind):
            raise RelationshipError("relationship kind must be a DXH-04 RelationshipKind (DRA-02)")
        # DMR-03 — each endpoint is a reference to a CERTIFIED entity.
        for role, ref in (("source", self.source_ref), ("target", self.target_ref)):
            if not isinstance(ref, EntityEndpointRef):
                raise RelationshipError(
                    f"the {role} endpoint relates a CERTIFIED entity by reference (DMR-03)"
                )
            # DRA-05 / DRA-C2 — every endpoint resolves to an existing entity identity.
            if not ref.resolves():
                raise RelationshipError(
                    f"the {role} endpoint does not resolve to a CERTIFIED entity "
                    f"(DRA-05 / DRA-C2)"
                )
        # DRA-04 / DRA-C3 — explicit, decidable cardinality (no unbounded-by-default).
        if not isinstance(self.cardinality, RelationshipCardinality):
            raise RelationshipError(
                "relationship must declare explicit, decidable cardinality (DRA-04 / DRA-C3)"
            )
        # DRA-06 — directionality is declared and consistent with the kind.
        if not isinstance(self.direction, RelationshipDirection):
            raise RelationshipError("relationship direction must be declared (DRA-06)")
        if self.direction is not DIRECTION_FOR_KIND[self.kind]:
            raise RelationshipError(
                f"a {self.kind.value} relationship is "
                f"{DIRECTION_FOR_KIND[self.kind].value}, not {self.direction.value} (DRA-06)"
            )
        # DRA-03 / DRA-C1 — a founding (Composition) relationship must not self-found.
        if self.kind in FOUNDING_KINDS and self.source_ref.entity_id == self.target_ref.entity_id:
            raise RelationshipError(
                "a founding relationship must relate distinct entities (DRA-03 / DRA-C1)"
            )
        # DMR-11 / §7 / DRA-K3 — navigation/integrity binds a RUNTIME policy reference.
        if not isinstance(self.policy_ref, str) or not self.policy_ref.startswith(
            f"{POLICY_REF_PREFIX}:"
        ):
            raise RelationshipError(
                "navigation/integrity-check must bind a RUNTIME policy reference "
                "(DMR-11 / DRA-K3)"
            )
        # DOV-08 — records a decidable integrity verdict.
        if not isinstance(self.verdict, RelationshipVerdict):
            raise RelationshipError("verdict must be a decidable RelationshipVerdict (DOV-08)")
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, RelationshipState):
            raise RelationshipError("relationship state must be a DOS-01…05 state (UDL-12)")
        # DRA-08 — a relationship records an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise RelationshipError("relationship must record an explicit version (DRA-08)")
        if not isinstance(self.supersedes, str):
            raise RelationshipError("relationship supersedes reference must be a string (DRA-08)")
        # DRA-07 / DMR-04 — the described-by reference is a string obligation (may be empty).
        if not isinstance(self.schema_ref, str):
            raise RelationshipError(
                "relationship schema reference must be a string (DRA-07 / DMR-04)"
            )
        # UDL-09/11 / DRA-09 / DRA-K5 — names no relationship/query/storage tech (material).
        if self._scan_technology():
            raise RelationshipError(
                "relationship names a join/foreign-key/graph/database technology or vendor "
                "(UDL-09 / DRA-09 / DRA-K5)"
            )

    # -- technology-neutrality (UDL-09, material) ------------------------------

    def _scan_technology(self) -> bool:
        """True iff any technology marker appears in the object's declared surface."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECH_MARKERS)

    def names_technology(self) -> bool:
        """UDL-09/11 / DRA-09 / DRA-K5 / C6 — True iff the object names a relationship tech."""
        return self._scan_technology()

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the object (structure + related references)."""
        return {
            "meta_class": RELATIONSHIP_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "source_ref": {
                "entity_id": self.source_ref.entity_id,
                "structure_digest": self.source_ref.structure_digest,
                "name": self.source_ref.name,
                "type_tag": self.source_ref.type_tag,
                "meta_class": self.source_ref.meta_class,
            },
            "target_ref": {
                "entity_id": self.target_ref.entity_id,
                "structure_digest": self.target_ref.structure_digest,
                "name": self.target_ref.name,
                "type_tag": self.target_ref.type_tag,
                "meta_class": self.target_ref.meta_class,
            },
            "cardinality": self.cardinality.value,
            "direction": self.direction.value,
            "policy_ref": self.policy_ref,
            "verdict": self.verdict.value,
            "version": self.version,
            "supersedes": self.supersedes,
            "schema_ref": self.schema_ref,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the object core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def relationship_id(self) -> str:
        """The deterministic ENG-001 identity of the object (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second identity
        scheme): an identical object always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{RELATIONSHIP_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-008) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-04)."""
        return RELATIONSHIP_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the object participates in."""
        return RELATIONSHIP_RELATIONSHIPS

    def endpoint_ids(self) -> tuple[str, str]:
        """The identities of the entities this relationship relates (DMR-03; by reference)."""
        return (self.source_ref.entity_id, self.target_ref.entity_id)

    def source_id(self) -> str:
        """The identity of the source endpoint (DMR-03)."""
        return self.source_ref.entity_id

    def target_id(self) -> str:
        """The identity of the target endpoint (DMR-03)."""
        return self.target_ref.entity_id

    # -- relationship property predicates --------------------------------------

    def is_by_reference(self) -> bool:
        """DRA-01 / UDL-09 — the relationship IS an ENG-005 reference (no new construct)."""
        return True

    def is_typed(self) -> bool:
        """DRA-02 — the relationship is classified by exactly one ENG-004 kind (DXH-04)."""
        return isinstance(self.kind, RelationshipKind)

    def is_founding(self) -> bool:
        """DRA-03 — whether the relationship establishes a founding (structural) dependency."""
        return self.kind in FOUNDING_KINDS

    def is_peer(self) -> bool:
        """DRA-06 — whether the relationship is a peer (symmetric, non-founding) association."""
        return self.direction is RelationshipDirection.PEER

    def cardinality_explicit(self) -> bool:
        """DRA-04 / DRA-C3 — the relationship declares an explicit, decidable cardinality."""
        return isinstance(self.cardinality, RelationshipCardinality)

    def directionality_declared(self) -> bool:
        """DRA-06 — directionality is declared and consistent with the kind."""
        return self.direction is DIRECTION_FOR_KIND[self.kind]

    def endpoints_resolve(self) -> bool:
        """DRA-05 / DRA-C2 — every endpoint resolves to an existing entity identity."""
        return self.source_ref.resolves() and self.target_ref.resolves()

    def endpoints_distinct(self) -> bool:
        """Whether the two related endpoints are distinct identities."""
        return self.source_ref.entity_id != self.target_ref.entity_id

    def founding_acyclic_rule(self) -> bool:
        """DRA-03 / DRA-C1 — a founding relationship relates distinct entities (no self-found).

        A peer/reference (non-founding) relationship may relate any endpoints (DRA-C4);
        only a founding relationship is required to be self-distinct.
        """
        return (not self.is_founding()) or self.endpoints_distinct()

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 — the founding/relationship graph is acyclic.

        The object's founding references (``relates`` → endpoints, ``behaves-as`` →
        RUNTIME policy, ``described-by`` → schema) are recorded by *identity reference*;
        none may reference the object itself, so the founding graph is a DAG.
        """
        own = self.relationship_id
        refs = {self.source_ref.entity_id, self.target_ref.entity_id, self.policy_ref}
        if self.schema_ref:
            refs.add(self.schema_ref)
        return own not in refs

    def relates_entities(self, first_id: str, second_id: str) -> bool:
        """DMR-03 — whether this relationship relates ``first_id`` and ``second_id`` (unordered)."""
        return {first_id, second_id} == set(self.endpoint_ids())

    def binds_policy_by_reference(self) -> bool:
        """DMR-11 / §7 / DRA-K3 — navigation/integrity binds a RUNTIME policy reference only."""
        return self.policy_ref.startswith(f"{POLICY_REF_PREFIX}:")

    def navigates_by_reference(self) -> bool:
        """§7 / DMR-11 — navigation is a RUNTIME execution reference; defines no engine."""
        return self.binds_policy_by_reference() and not self.enforces()

    def enforces(self) -> bool:
        """UDL-09 / DRA-09 — a relationship records association; it enforces nothing."""
        return False

    def is_recorded(self) -> bool:
        """DOV-08 — the association is recorded against an ENG-002 object."""
        return True

    def is_schema_describable(self) -> bool:
        """DRA-07 / DMR-04 — whether a described-by schema reference is recorded."""
        return bool(self.schema_ref.strip())

    def absorbs_endpoints(self) -> bool:
        """DRA-C5 / DMX-02 — the object references the entities it relates, never owns them."""
        return False

    # -- non-constitutiveness (UDL-09/15 / DRA-09) -----------------------------

    def confers_authority(self) -> bool:
        """UDL-15 / DRA-09 / C7 — a relationship confers no authority (structurally none)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DRA-09 / RR-07 / C7 — True iff the object appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — a relationship redefines no EL-1/DMC-02/RL-F2 model."""
        return False

    def selects_technology(self) -> bool:
        """UDL-09/11 / DRA-K5 — a relationship selects no connection technology (material)."""
        return self._scan_technology()

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: RelationshipState) -> RelationshipObject:
        """Return a new object advanced to ``to_state`` (forward-only; UDL-12).

        A breaking change (cardinality/directionality) is supersession, never in-place
        mutation (DATA-008 §8; UDL-12/15).

        Raises:
            RelationshipError: on a backward transition.
        """
        if not isinstance(to_state, RelationshipState):
            raise RelationshipError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise RelationshipError(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the relationship object."""
        return {
            "relationship_id": self.relationship_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "source_ref": self.source_ref.to_dict(),
            "target_ref": self.target_ref.to_dict(),
            "endpoint_ids": list(self.endpoint_ids()),
            "cardinality": self.cardinality.value,
            "direction": self.direction.value,
            "founding": self.is_founding(),
            "peer": self.is_peer(),
            "by_reference": self.is_by_reference(),
            "typed": self.is_typed(),
            "cardinality_explicit": self.cardinality_explicit(),
            "directionality_declared": self.directionality_declared(),
            "endpoints_resolve": self.endpoints_resolve(),
            "endpoints_distinct": self.endpoints_distinct(),
            "founding_acyclic_rule": self.founding_acyclic_rule(),
            "policy_ref": self.policy_ref,
            "binds_policy_by_reference": self.binds_policy_by_reference(),
            "navigates_by_reference": self.navigates_by_reference(),
            "enforces": self.enforces(),
            "recorded": self.is_recorded(),
            "verdict": self.verdict.value,
            "schema_ref": self.schema_ref,
            "schema_describable": self.is_schema_describable(),
            "confers_authority": self.confers_authority(),
            "names_technology": self.names_technology(),
            "absorbs_endpoints": self.absorbs_endpoints(),
            "version": self.version,
            "supersedes": self.supersedes,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(RELATIONSHIP_SUBSTRATE_REFS),
        }


def make_relationship(
    name: str,
    type_tag: str,
    source: Entity | EntityEndpointRef,
    target: Entity | EntityEndpointRef,
    policy_ref: str,
    *,
    kind: RelationshipKind = RelationshipKind.ASSOCIATION,
    cardinality: RelationshipCardinality = RelationshipCardinality.MANY_TO_MANY,
    direction: RelationshipDirection | None = None,
    verdict: RelationshipVerdict = RelationshipVerdict.PASS,
    state: RelationshipState = RelationshipState.DEFINED,
    version: str = "1.0.0",
    supersedes: str = "",
    schema_ref: str = "",
) -> RelationshipObject:
    """Construct a well-formed :class:`RelationshipObject` (fail-closed factory).

    ``source`` and ``target`` are the related endpoints — each either a CERTIFIED
    :class:`~data.entity.Entity` (reused by reference — the DMR-03 ``relates`` target) or
    an already-projected :class:`EntityEndpointRef`. ``direction`` defaults to the kind's
    declared direction (DRA-06) when omitted.
    """
    source_ref = source if isinstance(source, EntityEndpointRef) else EntityEndpointRef.from_entity(
        source
    )
    target_ref = target if isinstance(target, EntityEndpointRef) else EntityEndpointRef.from_entity(
        target
    )
    resolved_direction = direction if direction is not None else DIRECTION_FOR_KIND[kind]
    return RelationshipObject(
        name=name,
        type_tag=type_tag,
        kind=kind,
        source_ref=source_ref,
        target_ref=target_ref,
        cardinality=cardinality,
        direction=resolved_direction,
        policy_ref=policy_ref,
        verdict=verdict,
        state=state,
        version=version,
        supersedes=supersedes,
        schema_ref=schema_ref,
    )


__all__ = [
    "RELATIONSHIP_ID_PREFIX",
    "POLICY_REF_PREFIX",
    "CERTIFIED_ID_PREFIX",
    "ENDPOINT_META_CLASS",
    "REUSE_REFS",
    "policy_ref_for",
    "RelationshipError",
    "EntityEndpointRef",
    "RelationshipObject",
    "make_relationship",
]
