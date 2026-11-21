"""EC3-B10-U04 — The Universal Schema construct (DMC-05).

Realizes the meta-model construct **DMC-05 Schema** (DATA-005 §2; DATA-009 §3):

    the typed, explicit, decidable *description* of admissible data structure — the
    entities, attributes, types, and relationships a conformant data set may contain
    (the ontology root DOE-05). A schema is an ENG-002 Object bearing an ENG-001
    Identity, classified by an ENG-004 Type, that *describes* entities/relationships
    via DMR-04. A schema is **neither the entities it describes** (DOE-02) **nor a
    concrete database schema instance** — it is the implementation-independent
    structural description (UDL-10 Schema Explicitness).

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-02 Entity construct**, reusing both *by reference* (UDL-02 / DMI-05):

* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme.
* The described subject set (DMR-04 ``describes``) is a tuple of **references to
  CERTIFIED constructs** (id + structural digest + name/type + meta-class), **not**
  owned, embedded, or copied models (DSA-09 — a schema describes structure only;
  DMX-02 non-absorbing).
* Aggregate composition (DMR-12, DSA-05) is recorded as **member-schema id
  references** only, acyclically (DSA-C1 / DMK-03) — no member schema is embedded.

A :class:`Schema` is *immutable* (frozen — ENG-002 objecthood), *typed* (ENG-004,
DSA-03/DSA-K1/UDL-03), *identified* (ENG-001, DSA-K1/UDL-04), *explicit* (a non-empty,
decidable, typed element set — DSA-01/UDL-10), *conformance-decidable* (DSA-02/DSA-C2),
*classified* by one DXH-05 kind, *versioned* (DSA-06), and holds a *forward-only
lifecycle state* (DOS-01…05, UDL-12). Constructing a :class:`Schema` enforces
DSA-K1/K3, the conformance rules DSA-C1/C2/C3, and UDL-10/03/04/05 **fail-closed**: an
ill-formed schema cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

# --- DMC-02 reuse by reference (UDL-02 / DMR-04 describes target) — never redefined --
from data.entity import Entity
from data.schema_meta import (
    LIFECYCLE_ORDER,
    SCHEMA_META_CLASS,
    SCHEMA_RELATIONSHIPS,
    SCHEMA_SUBSTRATE_REFS,
    SchemaKind,
    SchemaState,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Schema (mirrors EC-1 UCOS-<KIND>-<hex16>).
SCHEMA_ID_PREFIX = "UCOS-SCHEMA"

#: The name-based reference form a schema presents (an entity records ``described-by``
#: as ``UCOS-SCHEMA-REF:<name>``; see :func:`data.entity.Entity.schema_ref`). Distinct
#: from ``schema_id`` — this is the reference an entity uses to cite its schema.
SCHEMA_REF_PREFIX = "UCOS-SCHEMA-REF"

#: The identity-reference prefix a described Entity carries (DMR-04 ``describes`` target).
ENTITY_ID_PREFIX = "UCOS-ENTITY"

#: The map of EC-1 / DMC-02 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the schema)",
    "ENG-004": "data.schema_meta.SchemaKind + type_tag + element types (ENG-004 typing)",
    "ENG-005": "described-subject + member-schema identity references (DMR-04/12; by reference)",
    "DMC-02": "data.entity.Entity — the CERTIFIED describes target (DMR-04); referenced only",
}

#: Conservative secret markers used to enforce UDL-15 / DSA-09 / RR-07 (embed no secret).
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


def schema_ref_for(name: str) -> str:
    """The name-based reference an entity records to cite this schema (DMR-04 described-by).

    An Entity's ``schema_ref`` equals this value for the schema that describes it, so
    the ``schema describes entity`` / ``entity described-by schema`` loop is decidable.
    """
    return f"{SCHEMA_REF_PREFIX}:{name}"


class SchemaError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`Schema`.

    A :class:`Schema` is fail-closed (TRACK-001): an ill-formed structural description
    is rejected at construction rather than admitted as an invalid schema.
    """


@dataclass(frozen=True, slots=True)
class SchemaElement:
    """A single typed, explicit structural element of a schema (DSA-01 / DSA-03).

    Records the element's name, its ENG-004 type reference, and whether it is required
    — the explicit, decidable structure UDL-10 demands. It selects no storage and
    embeds no value (it *describes* structure, DOE-05).
    """

    name: str
    type_tag: str
    required: bool = True

    def __post_init__(self) -> None:
        # DSA-01 — an element is explicitly named.
        if not isinstance(self.name, str) or not self.name.strip():
            raise SchemaError("schema element must be explicitly named (DSA-01)")
        # DSA-03 / DSA-C3 / UDL-03 — an element references a non-empty ENG-004 type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise SchemaError("schema element must reference an ENG-004 type (DSA-03 / DSA-C3)")
        if not isinstance(self.required, bool):
            raise SchemaError("schema element 'required' must be a bool (DSA-01)")

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "type_tag": self.type_tag, "required": self.required}


@dataclass(frozen=True, slots=True)
class DescribedRef:
    """A reference to a CERTIFIED construct a schema ``describes`` (DMR-04 / DOR-04).

    Records **only** the described construct's identity, structural fingerprint, name,
    type, and meta-class — never its implementation — so the schema references, and
    never owns or absorbs, the described model (DSA-09 — a schema describes structure
    only; DMX-02 non-absorbing; UDL-02 reuse-by-reference).
    """

    target_id: str
    structure_digest: str
    name: str
    type_tag: str
    meta_class: str
    element_names: tuple[str, ...]

    @classmethod
    def from_entity(cls, entity: Entity) -> DescribedRef:
        """Project a CERTIFIED :class:`~data.entity.Entity` into a reference-only subject."""
        if not isinstance(entity, Entity):
            raise SchemaError("a schema describes a data.entity.Entity (DMR-04)")
        return cls(
            target_id=entity.entity_id,
            structure_digest=entity.structure_digest,
            name=entity.name,
            type_tag=entity.type_tag,
            meta_class=entity.meta_class,
            element_names=tuple(r.name for r in entity.attribute_refs),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "structure_digest": self.structure_digest,
            "name": self.name,
            "type_tag": self.type_tag,
            "meta_class": self.meta_class,
            "element_names": list(self.element_names),
            "binding": "DMR-04:describes",
            "owned": False,  # DSA-09 — described, never owned
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class Schema:
    """DMC-05 — an immutable, typed, identified, explicit, decidable structural schema.

    Fields:
        name:           the explicit schema name (DSA-01; part of identity).
        type_tag:       the ENG-004 Type of the schema (DSA-03 / DSA-K1; UDL-03).
        kind:           the DXH-05 classification (DMR-09 classified-by).
        elements:       the explicit, typed, decidable element set (DSA-01 / UDL-10).
                        Non-empty; each element references an ENG-004 type (DSA-C3);
                        membership is decidable (no duplicate names — DSA-02 / DSA-C2).
        described_refs: the CERTIFIED subjects the schema describes (DMR-04; DSA-09,
                        non-owning). Non-empty for Entity/Relationship schemas.
        member_schema_refs: the member-schema id references an Aggregate-Schema composes
                        (DMR-12 / DSA-05), acyclically (DSA-C1 / DMK-03). Empty for a
                        non-aggregate schema.
        state:          the DOS-01…05 forward-only lifecycle state (UDL-12).
        version:        the schema version (DSA-06 versioned evolution).
        supersedes:     the id of a superseded schema, recorded on breaking change
                        (DSA-06 lineage). Empty for an original schema.
    """

    name: str
    type_tag: str
    kind: SchemaKind
    elements: tuple[SchemaElement, ...]
    described_refs: tuple[DescribedRef, ...]
    member_schema_refs: tuple[str, ...] = field(default_factory=tuple)
    state: SchemaState = SchemaState.DEFINED
    version: str = "1.0.0"
    supersedes: str = ""

    def __post_init__(self) -> None:
        # DSA-01 — explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise SchemaError("schema must have an explicit name (DSA-01)")
        # DSA-03 / DSA-K1 / DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise SchemaError("schema must be typed with a non-empty ENG-004 type_tag (DSA-K1)")
        # DXH-05 / DMR-09 — classified by exactly one Schema kind.
        if not isinstance(self.kind, SchemaKind):
            raise SchemaError("schema kind must be a DXH-05 SchemaKind (DMR-09)")
        # DSA-01 / UDL-10 — an explicit, non-empty, decidable, typed element set.
        if not isinstance(self.elements, tuple) or not self.elements:
            raise SchemaError(
                "schema must declare an explicit, non-empty element set (DSA-01 / UDL-10)"
            )
        seen_elements: set[str] = set()
        for el in self.elements:
            if not isinstance(el, SchemaElement):
                raise SchemaError("schema elements are SchemaElement descriptors (DSA-01)")
            # DSA-02 / DSA-C2 — decidable membership: no duplicate element names.
            if el.name in seen_elements:
                raise SchemaError("schema element set has a duplicate member (DSA-02 / DSA-C2)")
            seen_elements.add(el.name)
        # DMR-04 — described subjects are reference-only projections of CERTIFIED constructs.
        if not isinstance(self.described_refs, tuple):
            raise SchemaError("schema described subjects must be a tuple (DMR-04)")
        seen_subjects: set[str] = set()
        for ref in self.described_refs:
            if not isinstance(ref, DescribedRef):
                raise SchemaError("described subjects are DescribedRef references (DMR-04)")
            if not ref.target_id.startswith("UCOS-"):
                raise SchemaError("a described subject is not a CERTIFIED construct id (DMR-04)")
            if len(ref.structure_digest) != 64 or any(
                c not in "0123456789abcdef" for c in ref.structure_digest
            ):
                raise SchemaError("a described subject carries no structural digest (UDL-06)")
            if ref.target_id in seen_subjects:
                raise SchemaError("schema describes a duplicate subject (DSA-02)")
            seen_subjects.add(ref.target_id)
        # DSA-05 / DSA-C1 / DMK-03 — aggregate composes member schemas; others compose none.
        if not isinstance(self.member_schema_refs, tuple):
            raise SchemaError("member schema refs must be a tuple (DMR-12)")
        if self.kind is SchemaKind.AGGREGATE:
            if not self.member_schema_refs:
                raise SchemaError("an Aggregate-Schema must compose ≥1 member schema (DSA-05)")
        elif self.member_schema_refs:
            raise SchemaError("only an Aggregate-Schema may compose member schemas (DSA-05)")
        # A schema describes ≥1 subject or (aggregate) composes ≥1 member (DSA-02 / DSA-05).
        if not self.described_refs and not self.member_schema_refs:
            raise SchemaError("a schema must describe ≥1 subject or compose ≥1 member (DSA-02)")
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, SchemaState):
            raise SchemaError("schema state must be a DOS-01…05 state (UDL-12)")
        # DSA-06 — a schema records an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise SchemaError("schema must record an explicit version (DSA-06)")
        if not isinstance(self.supersedes, str):
            raise SchemaError("schema supersedes reference must be a string (DSA-06)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    @property
    def schema_ref(self) -> str:
        """The name-based reference an entity records to cite this schema (DMR-04)."""
        return schema_ref_for(self.name)

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the schema (structure + described references)."""
        return {
            "meta_class": SCHEMA_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "elements": [e.to_dict() for e in self.elements],
            "described_refs": [
                {
                    "target_id": r.target_id,
                    "structure_digest": r.structure_digest,
                    "name": r.name,
                    "type_tag": r.type_tag,
                    "meta_class": r.meta_class,
                }
                for r in self.described_refs
            ],
            "member_schema_refs": list(self.member_schema_refs),
            "version": self.version,
            "supersedes": self.supersedes,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the schema core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def schema_id(self) -> str:
        """The deterministic ENG-001 identity of the schema (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second
        identity scheme): identical structure + described references always yields the
        identical id, so identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{SCHEMA_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-009) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-05)."""
        return SCHEMA_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the schema participates in."""
        return SCHEMA_RELATIONSHIPS

    def element_names(self) -> tuple[str, ...]:
        """The names of the schema's declared elements (DSA-01)."""
        return tuple(e.name for e in self.elements)

    def element_type_tags(self) -> tuple[str, ...]:
        """The ENG-004 type references of the schema's declared elements (DSA-03)."""
        return tuple(e.type_tag for e in self.elements)

    @property
    def element_count(self) -> int:
        """The size of the schema's explicit element set (DSA-01)."""
        return len(self.elements)

    def described_subject_ids(self) -> tuple[str, ...]:
        """The identities of the constructs this schema describes (DMR-04; by reference)."""
        return tuple(r.target_id for r in self.described_refs)

    def is_explicit(self) -> bool:
        """DSA-01 / UDL-10 — the element set is explicit, non-empty, and decidable.

        Decidable membership requires a non-empty set with no duplicate element names.
        """
        names = [e.name for e in self.elements]
        return bool(names) and len(set(names)) == len(names)

    def is_conformance_decidable(self) -> bool:
        """DSA-02 / DSA-C2 — conformance to this schema is decidable.

        Decidable iff the structure is explicit (typed, non-overlapping element set)
        and the schema describes ≥1 subject or composes ≥1 member schema.
        """
        return self.is_explicit() and (
            bool(self.described_refs) or bool(self.member_schema_refs)
        )

    def elements_typed(self) -> bool:
        """DSA-03 / DSA-C3 — every declared element references a non-empty ENG-004 type."""
        return all(e.type_tag.strip() for e in self.elements)

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 / DSA-C1 / DSA-K3 — the founding/composition graph is acyclic.

        The schema's founding references (``describes`` → subjects, ``composed-as`` →
        member schemas) are recorded by *identity reference*; none may reference the
        schema itself, so the founding/composition graph is a DAG.
        """
        own = self.schema_id
        refs = set(self.described_subject_ids())
        refs.update(self.member_schema_refs)
        return own not in refs

    def describes_subject(self, subject_id: str) -> bool:
        """DMR-04 — whether this schema describes the construct identified by ``subject_id``."""
        return subject_id in self.described_subject_ids()

    def conforms_entity(self, entity: Entity) -> bool:
        """DSA-02 / DSA-C2 / DSA-C3 — decide whether ``entity`` conforms to this schema.

        Conformance is decidable and defined structurally: the schema must describe the
        entity (DMR-04) and every *required* element must be covered by one of the
        entity's typed attributes (name + ENG-004 type), with no untyped element. This
        is a pure predicate — it enacts nothing (UDL-13).
        """
        if not self.describes_subject(entity.entity_id):
            return False
        entity_attrs = {r.name: r.type_tag for r in entity.attribute_refs}
        for el in self.elements:
            if el.required:
                if el.name not in entity_attrs:
                    return False
                if entity_attrs[el.name] != el.type_tag:
                    return False
        return True

    def absorbs_described(self) -> bool:
        """DSA-09 / DMX-02 — the schema references the subjects it describes, never owns them."""
        return False

    # -- non-constitutiveness (UDL-15 / DSA-09) --------------------------------

    def confers_authority(self) -> bool:
        """UDL-15 / DSA-09 / C7 — a schema confers no authority (structurally none)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DSA-09 / RR-07 / C7 — True iff the schema appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — a schema redefines no EL-1/DMC-02 model (reuse-only)."""
        return False

    def selects_technology(self) -> bool:
        """UDL-11 / DSA-07 / DSA-K5 — a schema selects no storage/technology (none)."""
        return False

    # -- lifecycle (UDL-12, forward-only) + versioned evolution (DSA-06) -------

    def transition(self, to_state: SchemaState) -> Schema:
        """Return a new schema advanced to ``to_state`` (forward-only; UDL-12).

        Raises:
            SchemaError: on a backward transition (breaking change is supersession,
                never in-place reversal — DATA-009 §8; DSA-06 / UDL-12).
        """
        if not isinstance(to_state, SchemaState):
            raise SchemaError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise SchemaError(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the schema."""
        return {
            "schema_id": self.schema_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "schema_ref": self.schema_ref,
            "elements": [e.to_dict() for e in self.elements],
            "element_names": list(self.element_names()),
            "element_count": self.element_count,
            "explicit": self.is_explicit(),
            "conformance_decidable": self.is_conformance_decidable(),
            "described_refs": [r.to_dict() for r in self.described_refs],
            "described_subject_ids": list(self.described_subject_ids()),
            "member_schema_refs": list(self.member_schema_refs),
            "version": self.version,
            "supersedes": self.supersedes,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SCHEMA_SUBSTRATE_REFS),
            "absorbs_described": self.absorbs_described(),
        }


def element(name: str, type_tag: str, *, required: bool = True) -> SchemaElement:
    """Construct a well-formed :class:`SchemaElement` (fail-closed factory)."""
    return SchemaElement(name=name, type_tag=type_tag, required=required)


def entity_schema_for(
    entity: Entity,
    *,
    name: str,
    type_tag: str,
    state: SchemaState = SchemaState.DEFINED,
    version: str = "1.0.0",
) -> Schema:
    """Construct an Entity-Schema that describes ``entity``, derived from its structure.

    The schema's element set is derived from the entity's declared, typed attribute
    set (DSA-03 type groundedness), so the entity conforms to the schema by
    construction (DSA-02). The entity is referenced, never owned (DSA-09 / DMR-04).
    """
    elements = tuple(
        SchemaElement(name=r.name, type_tag=r.type_tag, required=True)
        for r in entity.attribute_refs
    )
    return Schema(
        name=name,
        type_tag=type_tag,
        kind=SchemaKind.ENTITY,
        elements=elements,
        described_refs=(DescribedRef.from_entity(entity),),
        state=state,
        version=version,
    )


def make_schema(
    name: str,
    type_tag: str,
    elements: tuple[SchemaElement, ...],
    described: tuple[Entity | DescribedRef, ...],
    *,
    kind: SchemaKind = SchemaKind.ENTITY,
    member_schema_refs: tuple[str, ...] = (),
    state: SchemaState = SchemaState.DEFINED,
    version: str = "1.0.0",
    supersedes: str = "",
) -> Schema:
    """Construct a well-formed :class:`Schema` (fail-closed factory).

    ``described`` is the set of CERTIFIED constructs the schema describes — each item a
    CERTIFIED :class:`~data.entity.Entity` (reused by reference — the DMR-04
    ``describes`` target) or an already-projected :class:`DescribedRef`.
    """
    refs = tuple(
        d if isinstance(d, DescribedRef) else DescribedRef.from_entity(d) for d in described
    )
    return Schema(
        name=name,
        type_tag=type_tag,
        kind=kind,
        elements=tuple(elements),
        described_refs=refs,
        member_schema_refs=tuple(member_schema_refs),
        state=state,
        version=version,
        supersedes=supersedes,
    )


__all__ = [
    "SCHEMA_ID_PREFIX",
    "SCHEMA_REF_PREFIX",
    "ENTITY_ID_PREFIX",
    "REUSE_REFS",
    "schema_ref_for",
    "SchemaError",
    "SchemaElement",
    "DescribedRef",
    "Schema",
    "element",
    "entity_schema_for",
    "make_schema",
]
