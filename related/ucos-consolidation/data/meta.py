"""EC3-B10-U01 — Data meta-model constants (read-only projections of DATA-001/005).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation (DATA-001 Constitution, DATA-003 Ontology, DATA-004 Taxonomy,
DATA-005 Meta-Model) that the Datum realization must conform to. It **defines no
new law and redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only
names the frozen obligations so the realization can be checked against them
deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at
the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC3-B10 package §5/§6)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 10-DATA/ specification commit.
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the CERTIFIED EC-1 baseline this builds upon.
IMPLEMENTATION_ANCHOR = "30a2a02"

#: The backward traceability chain every realized Datum records (DATA-005 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "DMC-01",  # DATA-005 §2 — Datum meta-class (root)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Datum reuses by reference (UDL-02; ENG-001…004).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, DMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value-fidelity, DMK-02)
    "ENG-004",  # Type      (typed, DMK-01)
)

# ---------------------------------------------------------------------------
# DATA-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (DMI-01 closure). Datum is DMC-01.
META_CLASSES: tuple[str, ...] = tuple(f"DMC-{n:02d}" for n in range(1, 11))

#: The Datum meta-class id (DATA-005 §2).
DATUM_META_CLASS = "DMC-01"

#: The twelve admitted meta-relationships (DMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"DMR-{n:02d}" for n in range(1, 13))

#: The meta-relationships in which a Datum participates (EC3-B10 package §2):
#:   DMR-02 values (an Attribute values a Datum — Datum is the value target)
#:   DMR-09 classified-by (DXH-01 Datum hierarchy)
#:   DMR-10 identified-by (ENG-001 via ENG-002)
DATUM_RELATIONSHIPS: tuple[str, ...] = ("DMR-02", "DMR-09", "DMR-10")


class DatumKind(str, Enum):
    """DXH-01 Datum Hierarchy (DATA-004 §3) — the classification of a Datum.

    A Datum is classified by exactly one kind (DMR-09 classified-by):
    """

    PRIMITIVE = "Primitive-Datum"  # a single typed value (ENG-003 primitive)
    COMPOSITE = "Composite-Datum"  # a structured value (record/collection) of typed data
    DERIVED = "Derived-Datum"  # a datum computed/aggregated from other data


class DatumState(str, Enum):
    """DOS-01…05 (DATA-003 §4) — the forward-only data lifecycle states (UDL-12)."""

    DEFINED = "DEFINED"  # DOS-01 — declared but not yet in use
    ACTIVE = "ACTIVE"  # DOS-02 — in use and authoritative
    DEPRECATED = "DEPRECATED"  # DOS-03 — superseded-in-waiting
    SUPERSEDED = "SUPERSEDED"  # DOS-04 — replaced by a new identity (lineage recorded)
    RETIRED = "RETIRED"  # DOS-05 — removed from active use, retained for history


#: The forward-only lifecycle order (UDL-12: no in-place reversal).
LIFECYCLE_ORDER: tuple[DatumState, ...] = (
    DatumState.DEFINED,
    DatumState.ACTIVE,
    DatumState.DEPRECATED,
    DatumState.SUPERSEDED,
    DatumState.RETIRED,
)

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws (UDL-01…15) and §12 — Compliance (C1…C7)
# ---------------------------------------------------------------------------

#: The fifteen Data Laws (DATA-001 §7), each mapped to its short obligation.
DATA_LAWS: dict[str, str] = {
    "UDL-01": "Data is a layer founded on frozen EL-1/RL-F2/PL-F2, not a new primitive.",
    "UDL-02": "Every construct reuses ENG-001…005 (+runtime/platform) by reference; redefines 0.",
    "UDL-03": "Every construct is classified by an ENG-004 Type; no untyped construct exists.",
    "UDL-04": "A construct-as-thing bears an ENG-001 Identity via an ENG-002 Object; one scheme.",
    "UDL-05": "Every construct-as-thing IS an ENG-002 Object; no parallel thing-model.",
    "UDL-06": "Value is carried only as ENG-003 Value; no parallel value model or coercion.",
    "UDL-07": "An entity declares an explicit, typed boundary and a decidable attribute set.",
    "UDL-08": "Every attribute is typed, named, bound to one entity, carrying ENG-003 Value.",
    "UDL-09": "Relationships use ENG-005 references; founding structure is acyclic.",
    "UDL-10": "Structure is declared by an explicit, typed, decidable schema; never implicit.",
    "UDL-11": "Storage is abstract topology only; no engine, DB, format, query lang, or vendor.",
    "UDL-12": "Every datum/entity has a decidable, forward-only, recorded lifecycle.",
    "UDL-13": "Governance is declarative, evaluative, non-enforcing; confers no authority.",
    "UDL-14": "Quality and security are decidable evaluative facets; enact no enforcement.",
    "UDL-15": "Non-constitutive: no new primitive, no authority, no secret, no technology.",
}

#: The Data laws a bare Datum construct is directly obligated by (subset of UDL-*).
#: UDL-07/08/10 (entity/attribute/schema) apply to Entity/Attribute units, not the
#: atomic Datum; they are recorded as not-applicable-to-Datum with rationale.
DATUM_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",
    "UDL-02",
    "UDL-03",
    "UDL-04",
    "UDL-05",
    "UDL-06",
    "UDL-09",
    "UDL-11",
    "UDL-12",
    "UDL-13",
    "UDL-14",
    "UDL-15",
)

#: Laws scoped to composite data constructs (Entity/Attribute/Schema), N/A to atom.
DATUM_INAPPLICABLE_LAWS: tuple[str, ...] = ("UDL-07", "UDL-08", "UDL-10")

#: The seven Data compliance conditions (DATA-001 §12). A construct is COMPLIANT
#: iff all applicable conditions hold, decided on evidence and deterministically.
DATA_COMPLIANCE: dict[str, str] = {
    "C1": "Typed (UDL-03), identified and objecthood-bound (UDL-04/05).",
    "C2": "Reuses frozen foundations by reference without redefinition (UDL-02).",
    "C3": "Value is ENG-003 value (UDL-06).",
    "C4": "Entity/attribute/schema structure is explicit (UDL-07/08/10).",
    "C5": "Relationships are ENG-005 references; founding structure acyclic (UDL-09).",
    "C6": "Selects no technology; describes storage abstractly (UDL-11/15).",
    "C7": "Confers no authority and embeds no secret (UDL-15).",
}

# ---------------------------------------------------------------------------
# DATA-005 §8 — Meta-validity gate (V1…V5) and constraints (DMK-01…08)
# ---------------------------------------------------------------------------

#: The five meta-validity checks (DATA-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Datum → DMC-01).",
    "V2": "All relationships used are within DMR-01…12.",
    "V3": "Satisfies all applicable meta-constraints (DMK-01…08).",
    "V4": "Founding graph is acyclic (DMK-03 / DMI-04).",
    "V5": "Every construct has a valid lifecycle state (DOS-01…05).",
}

#: Meta-constraints a Datum is bound by (DATA-005 §4).
DATUM_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-02": "Value is ENG-003 value (no parallel value model).",
    "DMK-03": "The founding meta-relationship graph is acyclic (a DAG).",
    "DMK-08": "Selects no technology and confers no authority.",
}

#: The CCE ten-gate identifiers (EC3-B10 package §9, CC-1…CC-10).
CCE_GATES: tuple[str, ...] = tuple(f"CC-{n}" for n in range(1, 11))

__all__ = [
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "TRACE_BACKWARD",
    "SUBSTRATE_REFS",
    "META_CLASSES",
    "DATUM_META_CLASS",
    "META_RELATIONSHIPS",
    "DATUM_RELATIONSHIPS",
    "DatumKind",
    "DatumState",
    "LIFECYCLE_ORDER",
    "DATA_LAWS",
    "DATUM_APPLICABLE_LAWS",
    "DATUM_INAPPLICABLE_LAWS",
    "DATA_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "DATUM_META_CONSTRAINTS",
    "CCE_GATES",
]
