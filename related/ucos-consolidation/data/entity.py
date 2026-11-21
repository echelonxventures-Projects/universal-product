"""EC3-B10-U03 — The Universal Entity construct (DMC-02).

Realizes the meta-model construct **DMC-02 Entity** (DATA-005 §2; DATA-006 §3):

    an identified, typed data construct that bears a bounded set of typed attributes
    and participates in relationships — a *represented thing* (the ontology root
    DOE-02). An entity is an ENG-002 Object bearing an ENG-001 Identity, classified
    by an ENG-004 Type, carrying value through its attributes (ENG-003, by
    reference), classified by DXH-02. It is neither its attributes (DOE-03), nor its
    schema (DOE-05), nor the storage that persists it (DOE-06) — it is the *bounded
    unit of represented identity*.

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-03 Attribute construct**, reusing both *by reference* (UDL-02 / DMI-05):

* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme.
* The borne attribute set (DMR-01 ``bears``) is a tuple of **references to CERTIFIED
  :class:`~data.attribute.Attribute` objects** (id + structural digest + name/type),
  **not** owned, embedded, or copied Attribute models (DEA-04 — an entity *never owns
  attribute implementation*; DMX-02 non-absorbing).
* The described-by schema (DMR-04) is recorded only as an optional **reference
  obligation** — no Schema construct (DMC-05) is realized or embedded here (the same
  additive reference-by discipline the certified Attribute used to record DMR-01
  ``borne-by`` without a realized Entity).

An :class:`Entity` is *immutable* (frozen — ENG-002 objecthood), *typed* (ENG-004,
DEA-01/UDL-03), *identified* (ENG-001, DEA-02/UDL-04), *bounded* (an explicit,
decidable attribute set — DEA-03/UDL-07), *attribute-bearing by reference*
(DMR-01/DEA-04), *classified* by one DXH-02 kind, and holds a *forward-only
lifecycle state* (DOS-01…05, UDL-12). Constructing an :class:`Entity` enforces
DEA-K1/K2, the boundary rules DEA-C1/C2, and UDL-07/03/04/05 **fail-closed**: an
ill-formed entity cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- DMC-03 reuse by reference (UDL-02 / DMR-01 bears target) — never redefined ---
from data.attribute import Attribute
from data.entity_meta import (
    ENTITY_META_CLASS,
    ENTITY_RELATIONSHIPS,
    ENTITY_SUBSTRATE_REFS,
    LIFECYCLE_ORDER,
    EntityKind,
    EntityState,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Entity (mirrors EC-1 UCOS-<KIND>-<hex16>).
ENTITY_ID_PREFIX = "UCOS-ENTITY"

#: The bearing-reference prefix an entity presents to the attributes it bears.
#: An Attribute records ``bearing_entity_ref`` (DMR-01 borne-by) as this ref form, so
#: an entity's boundary can be decided by matching (DEA-C2 — an attribute is borne by
#: exactly one entity). This is a *name-based reference*, distinct from ``entity_id``.
ENTITY_REF_PREFIX = "UCOS-ENTITY-REF"

#: The identity-reference prefix a borne Attribute carries (DMR-01 ``bears`` target).
ATTRIBUTE_ID_PREFIX = "UCOS-ATTR"

#: The map of EC-1 / DMC-03 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the entity)",
    "ENG-004": "data.entity_meta.EntityKind + type_tag (ENG-004 typing discipline)",
    "ENG-005": "borne-attribute + described-by identity references (DMR-01/04; by reference)",
    "DMC-03": "data.attribute.Attribute — the CERTIFIED bears target (DMR-01); referenced only",
}

#: Conservative secret markers used to enforce UDL-15 / DEA-09 / RR-07 (embed no secret).
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


def entity_ref_for(name: str) -> str:
    """The name-based bearing reference an entity presents to its borne attributes.

    An Attribute's ``bearing_entity_ref`` (DMR-01 borne-by) equals this value for the
    entity that bears it, so an entity's boundary (DEA-C2) is decidable by matching.
    """
    return f"{ENTITY_REF_PREFIX}:{name}"


class EntityError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`Entity`.

    An :class:`Entity` is fail-closed (TRACK-001): an ill-formed represented thing is
    rejected at construction rather than admitted as an invalid entity.
    """


@dataclass(frozen=True, slots=True)
class AttributeRef:
    """A reference to a CERTIFIED Attribute an entity ``bears`` (DMR-01).

    Records **only** the borne attribute's identity, structural fingerprint, name,
    type, and declared bearing reference — never its implementation — so the entity
    references, and never owns or absorbs, the Attribute model (DEA-04 — an entity
    never owns attribute implementation; DMX-02 non-absorbing; UDL-02 reuse-by-ref).
    """

    attribute_id: str
    structure_digest: str
    name: str
    type_tag: str
    bearing_entity_ref: str

    @classmethod
    def from_attribute(cls, attribute: Attribute) -> AttributeRef:
        """Project a CERTIFIED :class:`~data.attribute.Attribute` into a reference-only bearer."""
        if not isinstance(attribute, Attribute):
            raise EntityError("an entity bears a data.attribute.Attribute (DMR-01)")
        return cls(
            attribute_id=attribute.attribute_id,
            structure_digest=attribute.structure_digest,
            name=attribute.name,
            type_tag=attribute.type_tag,
            bearing_entity_ref=attribute.bearing_entity_ref,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "attribute_id": self.attribute_id,
            "structure_digest": self.structure_digest,
            "name": self.name,
            "type_tag": self.type_tag,
            "bearing_entity_ref": self.bearing_entity_ref,
            "binding": "DMR-01:bears",
            "owned": False,  # DEA-04 — referenced, never owned
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class Entity:
    """DMC-02 — an immutable, typed, identified, bounded, attribute-bearing entity.

    Fields:
        name:            the explicit, decidable entity name (DEA-02; part of identity).
        type_tag:        the ENG-004 Type of the entity (DEA-01; UDL-03).
        kind:            the DXH-02 classification (DMR-09 classified-by; DEA-01).
        attribute_refs:  the explicit, bounded set of borne attributes, each a
                         reference to a CERTIFIED Attribute (DMR-01; DEA-03/04;
                         DMX-02 non-absorbing). Membership is closed at declaration.
        state:           the DOS-01…05 forward-only lifecycle state (UDL-12).
        schema_ref:      the optional described-by schema reference (DMR-04; DEA-06).
                         A *reference obligation* only — no Schema construct (DMC-05)
                         is realized here. Required (non-empty) before an entity may
                         validly be ACTIVE (DEA-K3 / schema-before-ACTIVE).
    """

    name: str
    type_tag: str
    kind: EntityKind
    attribute_refs: tuple[AttributeRef, ...]
    state: EntityState = EntityState.DEFINED
    schema_ref: str = ""

    def __post_init__(self) -> None:
        # DEA-02 — explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise EntityError("entity must have an explicit name (DEA-02)")
        # DEA-01 / DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise EntityError("entity must be typed with a non-empty ENG-004 type_tag (DEA-01)")
        # DXH-02 / DMR-09 — classified by exactly one Entity kind.
        if not isinstance(self.kind, EntityKind):
            raise EntityError("entity kind must be a DXH-02 EntityKind (DMR-09)")
        # DEA-03 / DEA-04 / UDL-07 — an explicit, decidable, bounded attribute set.
        if not isinstance(self.attribute_refs, tuple) or not self.attribute_refs:
            raise EntityError(
                "entity must declare an explicit, non-empty attribute set (DEA-03/04 / UDL-07)"
            )
        expected_ref = entity_ref_for(self.name)
        seen: set[str] = set()
        for ref in self.attribute_refs:
            if not isinstance(ref, AttributeRef):
                raise EntityError("borne attributes are AttributeRef references (DMR-01)")
            if not ref.attribute_id.startswith(f"{ATTRIBUTE_ID_PREFIX}-"):
                raise EntityError("a borne attribute is not a CERTIFIED Attribute id (DMR-01)")
            if len(ref.structure_digest) != 64 or any(
                c not in "0123456789abcdef" for c in ref.structure_digest
            ):
                raise EntityError("a borne attribute carries no structural digest (UDL-06)")
            # DEA-04 / DEA-K2 — every borne attribute is typed (ENG-004).
            if not ref.type_tag.strip():
                raise EntityError("a borne attribute is untyped (DEA-04 / DEA-K2 / UDL-08)")
            # DEA-C2 / DOC-02 — each borne attribute is borne by exactly this entity.
            if ref.bearing_entity_ref != expected_ref:
                raise EntityError(
                    "a borne attribute is not bound to this entity's boundary (DEA-C2)"
                )
            # DEA-C1 / DXC-02 — membership is decidable: no duplicate attribute names.
            if ref.name in seen:
                raise EntityError("entity attribute set has a duplicate member (DEA-C1)")
            seen.add(ref.name)
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, EntityState):
            raise EntityError("entity state must be a DOS-01…05 state (UDL-12)")
        # DEA-06 — the described-by reference is a string obligation (may be empty).
        if not isinstance(self.schema_ref, str):
            raise EntityError("entity schema reference must be a string (DEA-06 / DMR-04)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    @property
    def bearing_ref(self) -> str:
        """The name-based reference this entity presents to its borne attributes (DEA-C2)."""
        return entity_ref_for(self.name)

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the entity (structure + borne references)."""
        return {
            "meta_class": ENTITY_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "attribute_refs": [
                {
                    "attribute_id": r.attribute_id,
                    "structure_digest": r.structure_digest,
                    "name": r.name,
                    "type_tag": r.type_tag,
                }
                for r in self.attribute_refs
            ],
            "schema_ref": self.schema_ref,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the entity core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def entity_id(self) -> str:
        """The deterministic ENG-001 identity of the entity (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second
        identity scheme): identical structure + borne references always yields the
        identical id, so identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{ENTITY_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-006) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-02)."""
        return ENTITY_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the entity participates in."""
        return ENTITY_RELATIONSHIPS

    def borne_attribute_ids(self) -> tuple[str, ...]:
        """The identities of the attributes this entity bears (DMR-01; by reference)."""
        return tuple(r.attribute_id for r in self.attribute_refs)

    @property
    def attribute_count(self) -> int:
        """The size of the entity's bounded attribute set (DEA-03)."""
        return len(self.attribute_refs)

    def is_bounded(self) -> bool:
        """DEA-03 / UDL-07 — the attribute set is explicit, non-empty, and decidable.

        Decidable membership requires a non-empty set with no duplicate members.
        """
        names = [r.name for r in self.attribute_refs]
        return bool(names) and len(set(names)) == len(names)

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 / UDL-09 / DEA-C3 — the founding graph is acyclic.

        The entity's founding references (``bears`` → Attributes, ``described-by`` →
        Schema) are recorded by *identity reference*; none may reference the entity
        itself, so the founding graph is a DAG.
        """
        own = self.entity_id
        refs = set(self.borne_attribute_ids())
        refs.update(r.bearing_entity_ref for r in self.attribute_refs)
        if self.schema_ref:
            refs.add(self.schema_ref)
        return own not in refs

    def absorbs_attributes(self) -> bool:
        """DEA-04 / DMX-02 — the entity references the attributes it bears, never owns them."""
        return False

    def is_schema_described(self) -> bool:
        """DEA-06 / DMR-04 — whether a described-by schema reference is recorded."""
        return bool(self.schema_ref.strip())

    # -- non-constitutiveness (UDL-15 / DEA-09) --------------------------------

    def confers_authority(self) -> bool:
        """UDL-15 / DEA-09 / C7 — an entity confers no authority (structurally none)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DEA-09 / RR-07 / C7 — True iff the entity appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — an entity redefines no EL-1/DMC-03 model (reuse-only)."""
        return False

    def selects_technology(self) -> bool:
        """UDL-11 / DEA-K5 — an entity selects no storage/technology (structurally none)."""
        return False

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: EntityState) -> Entity:
        """Return a new entity advanced to ``to_state`` (forward-only; UDL-12).

        Raises:
            EntityError: on a backward transition (breaking change is supersession,
                never in-place reversal — DATA-006 §8; UDL-12/15).
        """
        if not isinstance(to_state, EntityState):
            raise EntityError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise EntityError(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the entity."""
        return {
            "entity_id": self.entity_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "bearing_ref": self.bearing_ref,
            "attribute_refs": [r.to_dict() for r in self.attribute_refs],
            "attribute_ids": list(self.borne_attribute_ids()),
            "attribute_count": self.attribute_count,
            "bounded": self.is_bounded(),
            "schema_ref": self.schema_ref,
            "schema_described": self.is_schema_described(),
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(ENTITY_SUBSTRATE_REFS),
            "absorbs_attributes": self.absorbs_attributes(),
        }


def make_entity(
    name: str,
    type_tag: str,
    attributes: tuple[Attribute | AttributeRef, ...],
    *,
    kind: EntityKind = EntityKind.MASTER,
    state: EntityState = EntityState.DEFINED,
    schema_ref: str = "",
) -> Entity:
    """Construct a well-formed :class:`Entity` (fail-closed factory).

    ``attributes`` is the bounded set the entity bears — each item a CERTIFIED
    :class:`~data.attribute.Attribute` (reused by reference — the DMR-01 ``bears``
    target) or an already-projected :class:`AttributeRef`.
    """
    refs = tuple(
        a if isinstance(a, AttributeRef) else AttributeRef.from_attribute(a) for a in attributes
    )
    return Entity(
        name=name,
        type_tag=type_tag,
        kind=kind,
        attribute_refs=refs,
        state=state,
        schema_ref=schema_ref,
    )


__all__ = [
    "ENTITY_ID_PREFIX",
    "ENTITY_REF_PREFIX",
    "REUSE_REFS",
    "entity_ref_for",
    "EntityError",
    "AttributeRef",
    "Entity",
    "make_entity",
]
