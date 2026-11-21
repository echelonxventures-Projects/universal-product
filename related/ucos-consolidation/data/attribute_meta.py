"""EC3-B10-U02 — Attribute meta-model constants (read-only projections of DATA-007).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Attribute Architecture (DATA-001 Constitution,
DATA-004 Taxonomy, DATA-005 Meta-Model, **DATA-007 Attribute Architecture**) that
the Attribute realization (**DMC-03**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the
frozen obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at
the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
Shared foundation constants (anchors, laws, compliance conditions, meta-validity
gate, CCE gates, lifecycle states) are **reused by reference** from the CERTIFIED
DMC-01 surface (:mod:`data.meta`); they are re-exported here, never re-defined.
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
# The Attribute lifecycle reuses the frozen ontology lifecycle DOS-01…05.
# DATA-007 §8 — an attribute follows DOS-01…05 as part of its bearing entity /
# schema. It is the identical forward-only state machine as the Datum (UDL-12),
# so it is reused by reference (no parallel lifecycle model).
# ---------------------------------------------------------------------------

#: The Attribute lifecycle state type (reused DOS-01…05; DATA-007 §8, UDL-12).
AttributeState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-007 — the Attribute meta-class and its founding unit
# ---------------------------------------------------------------------------

#: The Attribute meta-class id (DATA-005 §2; DMC-03).
ATTRIBUTE_META_CLASS = "DMC-03"

#: The CERTIFIED founding unit whose construct the Attribute ``values`` (DMR-02).
#: The Attribute references this unit's certified Datum construct **by reference**;
#: it does not redefine, embed, or copy the Datum model (UDL-06 / UDL-02 / DMX-02).
DATUM_FOUNDING_UNIT = "EC3-B10-U01"

#: The certification id of the CERTIFIED DMC-01 Datum construct (founding-unit anchor).
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC3-B10-DATA-REALIZATION-PACKAGE-002 §6)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Attribute records (DATA-007 → root).
TRACE_BACKWARD_ATTRIBUTE: tuple[str, ...] = (
    "DMC-03",  # DATA-005 §2 / DATA-007 — Attribute meta-class
    "DATA-007",  # Universal Data Attribute Architecture (UDAA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-08)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Attribute reuses by reference (UDL-02).
#:   ENG-004 Type (typed, DAA-01/UDL-08); ENG-003 Value (value fidelity, DAA-03/UDL-06);
#:   ENG-001 Identity (identified); ENG-005 Reference (borne-by/relational, DMR-01/03).
ATTRIBUTE_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified attribute; identifying-attribute participation)
    "ENG-003",  # Value      (the ENG-003 value the attribute carries — via DMR-02 → Datum)
    "ENG-004",  # Type       (attribute typedness — DAA-01 / UDL-08 / UDL-03)
    "ENG-005",  # Reference  (bearing-entity + relational references — DMR-01/03)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-007 §5 — DXH-03 Attribute Hierarchy
# ---------------------------------------------------------------------------


class AttributeKind(str, Enum):
    """DXH-03 Attribute Hierarchy (DATA-004 §3; DATA-007 §5).

    An attribute is classified by exactly one kind (single-facet, DXC-02):
    """

    IDENTIFYING = "Identifying-Attribute"  # participates in entity identity (ENG-001 by reference)
    DESCRIPTIVE = "Descriptive-Attribute"  # carries a descriptive value (the minimal exemplar)
    RELATIONAL = "Relational-Attribute"  # carries a reference to another entity (ENG-005)
    DERIVED = "Derived-Attribute"  # computed from other attributes (provenance recorded)


# ---------------------------------------------------------------------------
# DATA-007 §6 — Attribute relationships (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which an Attribute participates (DATA-007 §6/§15):
#:   DMR-01 borne-by     (Attribute ← Entity; single bearing, reference obligation)
#:   DMR-02 values       (Attribute → Datum; reference-only, non-absorbing)
#:   DMR-04 described-by (Attribute → Schema; deferred reference — no schema realized)
#:   DMR-08 measured-by  (Attribute → Quality-Object; reference-only)
#:   DMR-09 classified-by(Attribute → Security-Object / DXH-03 kind; reference-only)
ATTRIBUTE_RELATIONSHIPS: tuple[str, ...] = ("DMR-01", "DMR-02", "DMR-04", "DMR-08", "DMR-09")

# ---------------------------------------------------------------------------
# DATA-007 §4 — Attribute principles (DAA-01…10)
# ---------------------------------------------------------------------------

#: The ten Attribute principles (DATA-007 §4), each mapped to its short obligation.
ATTRIBUTE_PRINCIPLES: dict[str, str] = {
    "DAA-01": "Attribute Typedness — every attribute is an ENG-004 Type; none untyped.",
    "DAA-02": "Single Bearing — every attribute is borne by exactly one entity (DMR-01).",
    "DAA-03": "Value Fidelity — an attribute carries exactly one ENG-003 value (DMR-02).",
    "DAA-04": "Naming Explicitness — every attribute has an explicit, decidable name.",
    "DAA-05": "Nullability Declared — absence-admissibility is declared, never implicit.",
    "DAA-06": "Derivation Provenance — a derived attribute records its evaluation/provenance.",
    "DAA-07": "Relational by Reference — a referencing attribute uses ENG-005, never embeds.",
    "DAA-08": "Additive Growth — new attribute types append additively (DXH-03).",
    "DAA-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "DAA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-007 §9 — value & derivation rules (DAA-C1…C5)
# ---------------------------------------------------------------------------

#: The five value / derivation rules (DATA-007 §9).
ATTRIBUTE_VALUE_RULES: dict[str, str] = {
    "DAA-C1": "The declared ENG-004 type totally determines admissible values (DMK-02).",
    "DAA-C2": "Nullability is declared; an absent value is admissible only where declared.",
    "DAA-C3": "A derived attribute is a DME evaluation over existing data; provenance recorded.",
    "DAA-C4": "A relational attribute references a target entity's identity; never absorbs it.",
    "DAA-C5": "Type change is re-typing under a declared schema; never silent coercion.",
}

# ---------------------------------------------------------------------------
# DATA-007 §10 — Attribute contracts & constraints (DAA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Attribute contracts / constraints (DATA-007 §10).
ATTRIBUTE_CONSTRAINTS: dict[str, str] = {
    "DAA-K1": "Every attribute is typed (ENG-004) and named (DMK-01).",
    "DAA-K2": "Every attribute carries exactly one ENG-003 value and is borne by one entity.",
    "DAA-K3": "Every attribute is schema-declared before its bearing entity is ACTIVE (DMK-04).",
    "DAA-K4": "Every derivation resolves to a DME evaluation; provenance present (DME-02).",
    "DAA-K5": "No attribute selects technology or confers authority (DMK-08).",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Attribute construct
# ---------------------------------------------------------------------------

#: The Data laws the Attribute construct is directly obligated by (subset of UDL-*),
#: with **UDL-08 (Attribute Typedness) now materially in scope**.
ATTRIBUTE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. the certified Datum)
    "UDL-03",  # typed
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-06",  # ENG-003 value fidelity (single value)
    "UDL-08",  # ATTRIBUTE TYPEDNESS — typed + named + single-bearing + ENG-003 value
    "UDL-09",  # references via ENG-005; founding acyclic
    "UDL-11",  # storage-independence
    "UDL-12",  # forward-only lifecycle
    "UDL-13",  # non-enforcing governance
    "UDL-14",  # evaluative facets
    "UDL-15",  # non-constitutive
)

#: Laws scoped to Entity/Schema units (DMC-02/05), deferred for the minimal Attribute:
#:   UDL-07 (entity boundary) — no Entity realized; DAA-K3 (schema-before-ACTIVE)
#:   is vacuously satisfied (no entity ACTIVATED); UDL-10 (explicit schema structure)
#:   is a Schema-unit obligation (DMC-05).
ATTRIBUTE_DEFERRED_LAWS: tuple[str, ...] = ("UDL-07", "UDL-10")

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Attribute is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints an Attribute is bound by (DATA-005 §4; DATA-007 §15).
ATTRIBUTE_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), named, identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-02": "Carries exactly one ENG-003 value (no parallel value model).",
    "DMK-03": "The founding meta-relationship graph is acyclic (a DAG).",
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
    "AttributeState",
    # attribute-specific projections
    "ATTRIBUTE_META_CLASS",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "TRACE_BACKWARD_ATTRIBUTE",
    "ATTRIBUTE_SUBSTRATE_REFS",
    "AttributeKind",
    "ATTRIBUTE_RELATIONSHIPS",
    "ATTRIBUTE_PRINCIPLES",
    "ATTRIBUTE_VALUE_RULES",
    "ATTRIBUTE_CONSTRAINTS",
    "ATTRIBUTE_APPLICABLE_LAWS",
    "ATTRIBUTE_DEFERRED_LAWS",
    "ATTRIBUTE_META_CONSTRAINTS",
]
