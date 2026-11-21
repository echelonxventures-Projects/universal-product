"""EC3-B10-U03 — Entity meta-model constants (read-only projections of DATA-006).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Entity Architecture (DATA-001 Constitution, DATA-004
Taxonomy, DATA-005 Meta-Model, **DATA-006 Universal Data Entity Architecture**) that
the Entity realization (**DMC-02**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the
frozen obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at
the constitutional anchor ``b7e7657`` (DATA-006 §3…§16) — no obligation is invented,
none is dropped. Shared foundation constants (anchors, laws, compliance conditions,
meta-validity gate, CCE gates, lifecycle states) are **reused by reference** from the
CERTIFIED DMC-01 surface (:mod:`data.meta`); they are re-exported here, never
re-defined.
"""

from __future__ import annotations

from enum import Enum

# --- DMC-01 reuse by reference (UDL-02) — shared foundation constants, never re-defined
from data.meta import (
    CCE_GATES,
    CONSTITUTIONAL_ANCHOR,
    DATA_COMPLIANCE,
    DATA_LAWS,
    IMPLEMENTATION_ANCHOR,
    LIFECYCLE_ORDER,
    META_CLASSES,
    META_RELATIONSHIPS,
    META_VALIDITY_CHECKS,
    DatumState,
)

# ---------------------------------------------------------------------------
# The Entity lifecycle reuses the frozen ontology lifecycle DOS-01…05.
# DATA-006 §8 — an entity follows DOS-01…05 forward-only (UDL-12). It is the
# identical forward-only state machine as the Datum/Attribute, so it is reused by
# reference (no parallel lifecycle model).
# ---------------------------------------------------------------------------

#: The Entity lifecycle state type (reused DOS-01…05; DATA-006 §8, UDL-12).
EntityState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-006 §3 — the Entity meta-class and its founding unit
# ---------------------------------------------------------------------------

#: The Entity meta-class id (DATA-005 §2; DMC-02).
ENTITY_META_CLASS = "DMC-02"

#: The CERTIFIED founding unit whose construct the Entity ``bears`` (DMR-01).
#: The Entity references this unit's certified Attribute construct **by reference**;
#: it does not redefine, own, embed, or copy the Attribute model (UDL-02 / DMX-02 /
#: DEA-04 — an entity bears attributes only via DMR-01, never owning the impl).
ATTRIBUTE_FOUNDING_UNIT = "EC3-B10-U02"

#: The certification id of the CERTIFIED DMC-03 Attribute construct (founding-unit anchor).
ATTRIBUTE_CERTIFICATION_ID = "UCOS-CERT-DMC-03-c57d36d3dbb2763d"

#: The transitively-closed founding root (bears → Attribute → values → Datum).
DATUM_FOUNDING_UNIT = "EC3-B10-U01"
#: The certification id of the CERTIFIED DMC-01 Datum construct (transitive anchor).
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-006 §16)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Entity records (DATA-006 → root).
TRACE_BACKWARD_ENTITY: tuple[str, ...] = (
    "DMC-02",  # DATA-005 §2 / DATA-006 §3 — Entity meta-class
    "DATA-006",  # Universal Data Entity Architecture (UDEA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-07)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Entity reuses by reference (UDL-02; DATA-006 §3):
#:   ENG-001 Identity (identified); ENG-002 Object (the entity IS an object);
#:   ENG-004 Type (typed, DEA-01); ENG-005 Reference (bears attributes by reference,
#:   DMR-01). The entity carries value only through its attributes → Datum (ENG-003
#:   by reference), so ENG-003 is reused transitively, not directly redefined.
ENTITY_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified entity — DEA-02 / UDL-04)
    "ENG-002",  # Object     (the entity IS an ENG-002 object — DEA-02 / UDL-05)
    "ENG-004",  # Type       (entity typedness — DEA-01 / UDL-03)
    "ENG-005",  # Reference  (bears-attribute + described-by references — DMR-01/04)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-006 §5 — DXH-02 Entity Hierarchy
# ---------------------------------------------------------------------------


class EntityKind(str, Enum):
    """DXH-02 Entity Hierarchy (DATA-004 §3; DATA-006 §5).

    An entity is classified by exactly one kind (single-facet, DXC-02):
    """

    MASTER = "Master-Entity"  # canonical, authoritative reference entity (the exemplar)
    TRANSACTIONAL = "Transactional-Entity"  # records a discrete event/operation (RUNTIME by ref)
    REFERENCE = "Reference-Entity"  # controlled vocabulary / code set
    OPERATIONAL = "Operational-Entity"  # supports a running platform (RUNTIME state by ref)
    ANALYTICAL = "Analytical-Entity"  # organized for aggregation/derivation


# ---------------------------------------------------------------------------
# DATA-006 §6 — Entity relationships (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which the *minimal* Entity participates (DATA-006 §6):
#:   DMR-01 bears        (Entity → Attribute; founding, acyclic; MATERIAL — by reference)
#:   DMR-04 described-by (Entity → Schema; deferred *reference obligation* — no Schema
#:                        construct is realized here, only an optional reference string)
#:   DMR-10 identified-by(Entity → ENG-001 via ENG-002; MATERIAL)
#: The peer/behavior/composition/storage relationships (DMR-03 relates, DMR-05
#: persisted-in, DMR-11 behaves-as, DMR-12 composed-as) are **out of scope** for the
#: minimal Entity unit (Relationship=DATA-008, Storage/RUNTIME/PLATFORM references) —
#: they are not realized (DO-NOT-IMPLEMENT boundary).
ENTITY_RELATIONSHIPS: tuple[str, ...] = ("DMR-01", "DMR-04", "DMR-10")

# ---------------------------------------------------------------------------
# DATA-006 §4 — Entity principles (DEA-01…10)
# ---------------------------------------------------------------------------

#: The ten Entity principles (DATA-006 §4), each mapped to its short obligation.
ENTITY_PRINCIPLES: dict[str, str] = {
    "DEA-01": "Entity Typedness — every entity is an ENG-004 Type; none untyped (UDL-03).",
    "DEA-02": "Entity Identity — every entity is an ENG-002 Object bearing ENG-001 id (UDL-04/05).",
    "DEA-03": "Boundedness — every entity declares an explicit, decidable attribute set (UDL-07).",
    "DEA-04": "Attribute Bearing — an entity bears attributes only via DMR-01; each typed.",
    "DEA-05": "Relationship by Reference — entities relate only via ENG-005 (DMR-03); acyclic.",
    "DEA-06": "Schema Description — an entity is described by a schema (DMR-04) before ACTIVE.",
    "DEA-07": "Persistence by Reference — persistence is a RUNTIME reference (DMR-11); redefine 0.",
    "DEA-08": "Additive Growth — new entity types append additively (DXH-02); no renumber.",
    "DEA-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "DEA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-006 §9 — Entity boundary & composition rules (DEA-C1…C5)
# ---------------------------------------------------------------------------

#: The five boundary / composition rules (DATA-006 §9).
ENTITY_BOUNDARY_RULES: dict[str, str] = {
    "DEA-C1": "The attribute set is explicit, typed, decidable; membership closed at declaration.",
    "DEA-C2": "Boundaries do not overlap: an attribute is borne by exactly one entity (DOC-02).",
    "DEA-C3": "Founding relations (bears/described-by) form a DAG; no self-founding (DMK-03).",
    "DEA-C4": "An entity references (does not absorb) related entities' identities (DMR-03).",
    "DEA-C5": "Master/Reference are authoritative; Transactional/Operational reference RUNTIME.",
}

# ---------------------------------------------------------------------------
# DATA-006 §10 — Entity contracts & constraints (DEA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Entity contracts / constraints (DATA-006 §10).
ENTITY_CONSTRAINTS: dict[str, str] = {
    "DEA-K1": "Every entity is typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DEA-K2": "Every borne attribute is typed and carries ENG-003 value (DMK-01/02).",
    "DEA-K3": "Every entity is schema-described before ACTIVE (DMK-04).",
    "DEA-K4": "Every behavior/composition reference resolves; none redefined (DMK-05/06).",
    "DEA-K5": "No entity selects technology or confers authority (DMK-08).",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Entity construct
# ---------------------------------------------------------------------------

#: The Data laws the Entity construct is directly obligated by (subset of UDL-*),
#: with **UDL-07 (Entity Boundedness) now materially in scope**.
ENTITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. the certified Attribute)
    "UDL-03",  # typed
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-07",  # ENTITY BOUNDEDNESS — explicit, typed, decidable attribute-set boundary
    "UDL-08",  # attribute typedness — every borne attribute typed (by reference)
    "UDL-09",  # references via ENG-005; founding acyclic
    "UDL-11",  # storage-independence
    "UDL-12",  # forward-only lifecycle
    "UDL-13",  # non-enforcing governance
    "UDL-14",  # evaluative facets
    "UDL-15",  # non-constitutive
)

#: Laws scoped to units not realized here (deferred for the minimal Entity):
#:   UDL-06 (ENG-003 value fidelity) is the Datum's obligation — the entity carries
#:   value only through its borne attributes → Datum (by reference); UDL-10 (explicit
#:   schema structure) is a Schema-unit obligation (DMC-05), recorded as a deferred
#:   described-by reference only.
ENTITY_DEFERRED_LAWS: tuple[str, ...] = ("UDL-06", "UDL-10")

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Entity is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints an Entity is bound by (DATA-005 §4; DATA-006 §15).
ENTITY_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-03": "The founding meta-relationship graph is acyclic (a DAG).",
    "DMK-04": "Schema-described before ACTIVE (deferred reference obligation).",
    "DMK-08": "Selects no technology and confers no authority.",
}

__all__ = [
    # reused-by-reference foundation constants (re-exported, not re-defined)
    "CCE_GATES",
    "CONSTITUTIONAL_ANCHOR",
    "DATA_COMPLIANCE",
    "DATA_LAWS",
    "IMPLEMENTATION_ANCHOR",
    "LIFECYCLE_ORDER",
    "META_CLASSES",
    "META_RELATIONSHIPS",
    "META_VALIDITY_CHECKS",
    "EntityState",
    # entity-specific projections
    "ENTITY_META_CLASS",
    "ATTRIBUTE_FOUNDING_UNIT",
    "ATTRIBUTE_CERTIFICATION_ID",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "TRACE_BACKWARD_ENTITY",
    "ENTITY_SUBSTRATE_REFS",
    "EntityKind",
    "ENTITY_RELATIONSHIPS",
    "ENTITY_PRINCIPLES",
    "ENTITY_BOUNDARY_RULES",
    "ENTITY_CONSTRAINTS",
    "ENTITY_APPLICABLE_LAWS",
    "ENTITY_DEFERRED_LAWS",
    "ENTITY_META_CONSTRAINTS",
]
