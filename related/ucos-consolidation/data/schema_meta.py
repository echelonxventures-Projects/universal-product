"""EC3-B10-U04 — Schema meta-model constants (read-only projections of DATA-009).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Schema Architecture (DATA-001 Constitution, DATA-004
Taxonomy, DATA-005 Meta-Model, **DATA-009 Universal Data Schema Architecture**) that
the Schema realization (**DMC-05**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the
frozen obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at
the constitutional anchor ``b7e7657`` (DATA-009 §3…§17) — no obligation is invented,
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
# The Schema lifecycle reuses the frozen ontology lifecycle DOS-01…05.
# DATA-009 §8 — a schema follows DOS-01…05 forward-only (DOI-05; UDL-12). It is the
# identical forward-only state machine as the Datum/Attribute/Entity, so it is reused
# by reference (no parallel lifecycle model).
# ---------------------------------------------------------------------------

#: The Schema lifecycle state type (reused DOS-01…05; DATA-009 §8, UDL-12).
SchemaState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-009 §3 — the Schema meta-class and its founding unit
# ---------------------------------------------------------------------------

#: The Schema meta-class id (DATA-005 §2; DMC-05).
SCHEMA_META_CLASS = "DMC-05"

#: The CERTIFIED founding unit whose construct the Schema ``describes`` (DMR-04).
#: The Schema references this unit's certified Entity construct **by reference**; it
#: does not redefine, own, embed, or copy the Entity model (UDL-02 / DMX-02 / DSA-09 —
#: a schema describes structure only, never owning the described construct).
ENTITY_FOUNDING_UNIT = "EC3-B10-U03"

#: The certification id of the CERTIFIED DMC-02 Entity construct (founding-unit anchor).
ENTITY_CERTIFICATION_ID = "UCOS-CERT-DMC-02-def41470d3bac196"

#: The transitively-closed founding roots (describes → Entity bears Attribute values Datum).
ATTRIBUTE_FOUNDING_UNIT = "EC3-B10-U02"
#: The certification id of the CERTIFIED DMC-03 Attribute construct (transitive anchor).
ATTRIBUTE_CERTIFICATION_ID = "UCOS-CERT-DMC-03-c57d36d3dbb2763d"
DATUM_FOUNDING_UNIT = "EC3-B10-U01"
#: The certification id of the CERTIFIED DMC-01 Datum construct (transitive anchor).
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-009 §16)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Schema records (DATA-009 → root).
TRACE_BACKWARD_SCHEMA: tuple[str, ...] = (
    "DMC-05",  # DATA-005 §2 / DATA-009 §3 — Schema meta-class
    "DATA-009",  # Universal Data Schema Architecture (UDSA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-10)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Schema reuses by reference (UDL-02; DATA-009 §3):
#:   ENG-001 Identity (identified schema — DSA-K1); ENG-002 Object (the schema IS an
#:   object); ENG-004 Type (schema + element typing — DSA-03); ENG-005 Reference
#:   (describes subjects + composes members by reference — DMR-04/12).
SCHEMA_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified schema — DSA-K1 / UDL-04)
    "ENG-002",  # Object     (the schema IS an ENG-002 object — UDL-05)
    "ENG-004",  # Type       (schema + element typedness — DSA-03 / UDL-03)
    "ENG-005",  # Reference  (describes/composes references — DMR-04/12)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-009 §5 — DXH-05 Schema Hierarchy
# ---------------------------------------------------------------------------


class SchemaKind(str, Enum):
    """DXH-05 Schema Hierarchy (DATA-004 §3; DATA-009 §5).

    A schema is classified by exactly one kind (single-facet, DXC-02):
    """

    ENTITY = "Entity-Schema"  # describes an entity's attributes/types
    RELATIONSHIP = "Relationship-Schema"  # describes admissible relationships (cardinality/dir.)
    AGGREGATE = "Aggregate-Schema"  # composes a set of entity/relationship schemas (acyclic)


# ---------------------------------------------------------------------------
# DATA-009 §6 — Schema relationships (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which the *minimal* Schema participates (DATA-009 §6):
#:   DMR-04 describes    (Schema → Entity/Attribute/Relationship; founding, acyclic; MATERIAL)
#:   DMR-10 identified-by(Schema → ENG-001 via ENG-002; MATERIAL)
#: The behavior/composition relationships (DMR-11 behaves-as → RUNTIME validation,
#: DMR-12 composed-as → PLATFORM composition) are **reference-only** (DATA-009 §6/§7)
#: and out of scope for a bare Entity-Schema; they are recorded as deferred, and are
#: materially exercised only by an Aggregate-Schema's member composition (DMR-04
#: describes remains the founding relationship). No relationship outside DMR-01…12 is
#: admitted (DOI-01 / DMI-02).
SCHEMA_RELATIONSHIPS: tuple[str, ...] = ("DMR-04", "DMR-10")

#: Reference-only relationships a schema may cite but never redefine (DATA-009 §6/§7).
SCHEMA_DEFERRED_RELATIONSHIPS: tuple[str, ...] = ("DMR-11", "DMR-12")

# ---------------------------------------------------------------------------
# DATA-009 §4 — Schema principles (DSA-01…10)
# ---------------------------------------------------------------------------

#: The ten Schema principles (DATA-009 §4), each mapped to its short obligation.
SCHEMA_PRINCIPLES: dict[str, str] = {
    "DSA-01": "Schema Explicitness — structure is declared by an explicit typed schema (UDL-10).",
    "DSA-02": "Conformance Decidability — conformance of a data set to a schema is decidable.",
    "DSA-03": "Type Groundedness — every schema element references an ENG-004 type (UDL-03).",
    "DSA-04": "Relationship Coverage — admissible relationships described via ENG-005 (UDL-09).",
    "DSA-05": "Composition — aggregate schemas compose member schemas acyclically (DMK-03).",
    "DSA-06": "Versioned Evolution — change is additive/supersession with recorded lineage.",
    "DSA-07": "Storage Neutrality — a schema selects no storage engine/format/query lang (UDL-11).",
    "DSA-08": "Additive Growth — new schema kinds append additively (DXH-05); no renumber.",
    "DSA-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "DSA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-009 §9 — Schema composition & conformance rules (DSA-C1…C5)
# ---------------------------------------------------------------------------

#: The five composition / conformance rules (DATA-009 §9).
SCHEMA_CONFORMANCE_RULES: dict[str, str] = {
    "DSA-C1": "An aggregate schema composes member schemas acyclically (DMK-03).",
    "DSA-C2": "Conformance is decidable: a data set satisfies a schema or is rejected decidably.",
    "DSA-C3": "Every schema element references an ENG-004 type; untyped elements are rejected.",
    "DSA-C4": "A schema describes cardinality/directionality of relationships explicitly (DSA-04).",
    "DSA-C5": "Additive change preserves prior-valid conformance; breaking change supersedes.",
}

# ---------------------------------------------------------------------------
# DATA-009 §10 — Schema contracts & constraints (DSA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Schema contracts / constraints (DATA-009 §10).
SCHEMA_CONSTRAINTS: dict[str, str] = {
    "DSA-K1": "Every schema is typed (ENG-004) and identified (ENG-001) — DMK-01.",
    "DSA-K2": "Every entity/attribute/relationship is schema-described before ACTIVE — DMK-04.",
    "DSA-K3": "Aggregate composition is acyclic — DMK-03.",
    "DSA-K4": "Conformance-checking resolves to a RUNTIME evaluation; none redefined — DMK-05.",
    "DSA-K5": "No schema selects storage/format/query technology or confers authority — DMK-08.",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Schema construct
# ---------------------------------------------------------------------------

#: The Data laws the Schema construct is directly obligated by (subset of UDL-*),
#: with **UDL-10 (Schema Explicitness) now materially in scope**.
SCHEMA_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. the certified Entity)
    "UDL-03",  # typed (schema + every element)
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-09",  # relationships/references via ENG-005; founding acyclic
    "UDL-10",  # SCHEMA EXPLICITNESS — explicit, typed, decidable structural description
    "UDL-11",  # storage-independence (schema neutrality — DSA-07)
    "UDL-12",  # forward-only lifecycle + versioned evolution (DSA-06)
    "UDL-13",  # non-enforcing governance (record-only)
    "UDL-14",  # evaluative facets (quality/conformance)
    "UDL-15",  # non-constitutive
)

#: Laws scoped to units not realized here (deferred for the Schema construct):
#:   UDL-06 (ENG-003 value fidelity) is the Datum's obligation — the schema describes
#:   structure, carrying value only transitively through the entities it describes;
#:   UDL-07 (entity boundedness) is the Entity unit's obligation (DMC-02); UDL-08
#:   (attribute typedness) is the Attribute unit's obligation (DMC-03).
SCHEMA_DEFERRED_LAWS: tuple[str, ...] = ("UDL-06", "UDL-07", "UDL-08")

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Schema is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints a Schema is bound by (DATA-005 §4; DATA-009 §15).
SCHEMA_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-03": "The founding/composition meta-relationship graph is acyclic (a DAG).",
    "DMK-04": "The describer that makes entities schema-described before ACTIVE.",
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
    "SchemaState",
    # schema-specific projections
    "SCHEMA_META_CLASS",
    "ENTITY_FOUNDING_UNIT",
    "ENTITY_CERTIFICATION_ID",
    "ATTRIBUTE_FOUNDING_UNIT",
    "ATTRIBUTE_CERTIFICATION_ID",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "TRACE_BACKWARD_SCHEMA",
    "SCHEMA_SUBSTRATE_REFS",
    "SchemaKind",
    "SCHEMA_RELATIONSHIPS",
    "SCHEMA_DEFERRED_RELATIONSHIPS",
    "SCHEMA_PRINCIPLES",
    "SCHEMA_CONFORMANCE_RULES",
    "SCHEMA_CONSTRAINTS",
    "SCHEMA_APPLICABLE_LAWS",
    "SCHEMA_DEFERRED_LAWS",
    "SCHEMA_META_CONSTRAINTS",
]
