"""EC3-B10-U08 — Quality meta-model constants (read-only projections of DATA-013).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Quality Architecture (DATA-001 Constitution, DATA-004
Taxonomy, DATA-005 Meta-Model, **DATA-013 Universal Data Quality Architecture**) that
the Quality realization (**DMC-09**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the frozen
obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at the
constitutional anchor ``b7e7657`` (DATA-013 §1…§17) — no obligation is invented, none
is dropped. Data quality is **decidable, evaluative, record-only, and non-remediating**
— a quality object *measures and records*; it does not cleanse, remediate, enforce, or
enact anything (UDL-14 / DQA-01/02/03). Shared foundation constants (anchors, laws,
compliance conditions, meta-validity gate, CCE gates, lifecycle states) are **reused by
reference** from the CERTIFIED DMC-01 surface (:mod:`data.meta`); re-exported, never
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
# A quality object follows the frozen ontology lifecycle DOS-01…05 (DATA-013 §8).
# Identical forward-only state machine as every other data construct, so it is reused by
# reference (no parallel lifecycle model).
# ---------------------------------------------------------------------------

#: The Quality-object lifecycle state type (reused DOS-01…05; DATA-013 §8, UDL-12).
QualityState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-013 §3 — the Quality meta-class and its founding units
# ---------------------------------------------------------------------------

#: The Quality meta-class id (DATA-005 §2; DMC-09).
QUALITY_META_CLASS = "DMC-09"

#: The CERTIFIED unit whose construct the Quality object ``measures`` (DMR-08, ref-only).
#: Quality records a fidelity measurement of a data construct; it references the CERTIFIED
#: DMC-02 Entity **by reference** as its measured subject (DOR-08 / DMR-08) and carries no
#: entity model of its own.
ENTITY_FOUNDING_UNIT = "EC3-B10-U03"
#: The certification id of the CERTIFIED DMC-02 Entity construct (measures anchor).
ENTITY_CERTIFICATION_ID = "UCOS-CERT-DMC-02-def41470d3bac196"

#: The transitively-closed founding roots (measures → Entity bears Attribute values Datum).
ATTRIBUTE_FOUNDING_UNIT = "EC3-B10-U02"
ATTRIBUTE_CERTIFICATION_ID = "UCOS-CERT-DMC-03-c57d36d3dbb2763d"
DATUM_FOUNDING_UNIT = "EC3-B10-U01"
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

#: The CERTIFIED DMC-05 Schema unit a schema-relative measure cites (DQA-05 / DQA-C2).
#: Completeness/consistency are measured relative to a declared schema (DATA-009); the
#: Quality object binds that schema **by reference** — it realizes no Schema of its own.
SCHEMA_FOUNDING_UNIT = "EC3-B10-U04"
SCHEMA_CERTIFICATION_ID = "UCOS-CERT-DMC-05-e9edc215907c8695"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-013 §16)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Quality object records.
TRACE_BACKWARD_QUALITY: tuple[str, ...] = (
    "DMC-09",  # DATA-005 §2 / DATA-013 §3 — Quality meta-class
    "DATA-013",  # Universal Data Quality Architecture (UDQA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-14)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Quality object reuses by reference (UDL-02):
#:   ENG-001 Identity (identified object — DQA-K1); ENG-002 Object (the record IS an
#:   object bearing the measurement — DQA-K4); ENG-004 Type (object + kind typing —
#:   DQA-K1); ENG-005 Reference (measures a construct + binds RUNTIME policy by
#:   reference — DMR-08/11).
QUALITY_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified object — DQA-K1 / UDL-04)
    "ENG-002",  # Object     (the record IS an ENG-002 object — DQA-K4 / UDL-05)
    "ENG-004",  # Type       (object + kind typedness — DQA-K1 / UDL-03)
    "ENG-005",  # Reference  (measures + RUNTIME policy references — DMR-08/11)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-013 §5 — DXH-09 Quality-Object Hierarchy
# ---------------------------------------------------------------------------


class QualityKind(str, Enum):
    """DXH-09 Quality-Object Hierarchy (DATA-004 §3; DATA-013 §5).

    A quality object is classified by exactly one kind (single-facet, DXC-02); each is a
    decidable, evaluative measurement dimension (DQA-02) — none names or implies a
    profiling engine, quality tool, or benchmark technology (UDL-14 / DQA-K5):
    """

    ACCURACY_MEASURE = "Accuracy-Measure"  # correctness of value vs. its referent
    COMPLETENESS_MEASURE = "Completeness-Measure"  # presence of required attrs (schema-relative)
    CONSISTENCY_MEASURE = "Consistency-Measure"  # non-contradiction across related data
    INTEGRITY_MEASURE = "Integrity-Measure"  # referential/structural integrity conformance


class QualityVerdict(str, Enum):
    """A recorded, decidable quality judgment (DQA-C1; DOV-08) — evaluative only.

    The verdict *records* a measurement outcome; it enforces and remediates nothing
    (DQA-03).
    """

    PASS = "pass"  # noqa: S105 — quality verdict value, not a credential (DQA-C1 / DOV-08)
    FAIL = "fail"  # a deficiency is recorded (routed to a Gap Report, DQA-C4)
    NOT_APPLICABLE = "not-applicable"  # no applicable dimension to measure


# ---------------------------------------------------------------------------
# DATA-013 §2/§5 — the decidable quality dimensions and their facet mapping
# ---------------------------------------------------------------------------

#: The four decidable quality dimensions (DQA-02; DXH-09). A measurement records a value
#: along exactly one of these; membership is decidable and single-facet (DXC-02).
QUALITY_DIMENSIONS: tuple[str, ...] = ("accuracy", "completeness", "consistency", "integrity")

#: The single dimension each DXH-09 kind measures (single-facet, DXC-02 / DQA-02).
DIMENSION_FOR_KIND: dict[QualityKind, str] = {
    QualityKind.ACCURACY_MEASURE: "accuracy",
    QualityKind.COMPLETENESS_MEASURE: "completeness",
    QualityKind.CONSISTENCY_MEASURE: "consistency",
    QualityKind.INTEGRITY_MEASURE: "integrity",
}

#: The kinds whose measurement is schema-relative (DQA-05 / DQA-C2): completeness and
#: consistency are measured relative to a declared schema (DATA-009), bound by reference.
SCHEMA_RELATIVE_KINDS: frozenset[QualityKind] = frozenset(
    {QualityKind.COMPLETENESS_MEASURE, QualityKind.CONSISTENCY_MEASURE}
)

#: The minimum/maximum recorded measurement score (a decidable, bounded metric value).
SCORE_MIN = 0
SCORE_MAX = 100

# ---------------------------------------------------------------------------
# DATA-013 §6 — Quality relationships (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which the Quality object participates (DATA-013 §6):
#:   DMR-08 measures     (Quality-Object ← Data construct; reference-only; MATERIAL —
#:                        the object measures the construct it evaluates, DOR-08)
#:   DMR-10 identified-by(Quality-Object → ENG-001 via ENG-002; MATERIAL, DOR-10)
#:   DMR-11 behaves-as   (Quality-Object → RUNTIME policy evaluation; reference-only;
#:                        MATERIAL — measurement binds by reference, DQA-06 / DOR-11)
#: No relationship outside DMR-01…12 is admitted (DOI-01 / DMI-02).
QUALITY_RELATIONSHIPS: tuple[str, ...] = ("DMR-08", "DMR-10", "DMR-11")

# ---------------------------------------------------------------------------
# DATA-013 §4 — Quality principles (DQA-01…10)
# ---------------------------------------------------------------------------

#: The ten Quality principles (DATA-013 §4), each mapped to its short obligation.
QUALITY_PRINCIPLES: dict[str, str] = {
    "DQA-01": "Evaluativeness — quality is a decidable measurement; it records, not enforces.",
    "DQA-02": (
        "Dimensioned Measurement — measured along "
        "accuracy/completeness/consistency/integrity."
    ),
    "DQA-03": "Non-Remediation — quality measures and reports; it does not cleanse or mutate.",
    "DQA-04": (
        "Measurement Recording — every measurement is recorded (DOV-08); immutable once made."
    ),
    "DQA-05": "Schema-Relative — completeness/consistency are measured relative to a schema.",
    "DQA-06": "Reuse by Reference — measurement evaluation binds by reference to RUNTIME policy.",
    "DQA-07": (
        "Benchmark Neutrality — encodes no technology benchmark, threshold, or vendor metric."
    ),
    "DQA-08": "Additive Growth — new quality dimensions append additively (DXH-09).",
    "DQA-09": (
        "Non-Constitutiveness — confers no authority, embeds no secret, selects no technology."
    ),
    "DQA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-013 §9 — Quality measurement rules (DQA-C1…C5)
# ---------------------------------------------------------------------------

#: The five measurement rules (DATA-013 §9).
QUALITY_MEASUREMENT_RULES: dict[str, str] = {
    "DQA-C1": "Each quality dimension is a decidable predicate/metric over a data construct.",
    "DQA-C2": "Completeness/consistency are measured relative to a declared schema (DATA-009).",
    "DQA-C3": "A measurement records a value/verdict; it triggers no remediation or mutation.",
    "DQA-C4": "A failing measurement is routed to a Gap Report; the object does not remediate.",
    "DQA-C5": "Measurements are append-only records; a new assessment is a new record.",
}

# ---------------------------------------------------------------------------
# DATA-013 §10 — Quality contracts & constraints (DQA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Quality contracts / constraints (DATA-013 §10).
QUALITY_CONSTRAINTS: dict[str, str] = {
    "DQA-K1": "Every quality object is typed (ENG-004) and identified (ENG-001) — DMK-01.",
    "DQA-K2": "Every quality object is evaluative and non-enforcing — DMK-07; UDL-14.",
    "DQA-K3": "Every measurement binds by reference to RUNTIME policy; none redefined — DMK-05.",
    "DQA-K4": "Every measurement is recorded against an ENG-002 object (DOV-08) — DME-02.",
    "DQA-K5": "No quality object selects benchmark technology or confers authority — DMK-08.",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Quality construct
# ---------------------------------------------------------------------------

#: The Data laws the Quality construct is directly obligated by (subset of UDL-*),
#: with **UDL-14 (Quality & Security as Evaluative Facets) now materially in scope at the
#: strongest level**.
QUALITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. RUNTIME policy + certified Entity)
    "UDL-03",  # typed (object + kind)
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-09",  # references via ENG-005; founding acyclic
    "UDL-12",  # forward-only lifecycle + append-only re-measurement
    "UDL-14",  # QUALITY — decidable evaluative facet; measures/records, enacts nothing
    "UDL-15",  # non-constitutive
)

#: Laws scoped to units not realized here (deferred for the Quality construct):
#:   UDL-06 (value fidelity — transitive via measured construct); UDL-07 (entity
#:   boundedness); UDL-08 (attribute typedness); UDL-10 (schema explicitness — bound by
#:   reference for schema-relative measures); UDL-11 (storage independence); UDL-13
#:   (governance) — each another unit's obligation.
QUALITY_DEFERRED_LAWS: tuple[str, ...] = (
    "UDL-06",
    "UDL-07",
    "UDL-08",
    "UDL-10",
    "UDL-11",
    "UDL-13",
)

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Quality object is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints a Quality object is bound by (DATA-005 §4; DATA-013 §15).
QUALITY_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-03": "The founding/measurement meta-relationship graph is acyclic (a DAG).",
    "DMK-05": "Measurement resolves to a RUNTIME policy reference; none redefined.",
    "DMK-07": "Evaluative and non-enforcing (measures/records, does not enact).",
    "DMK-08": "Confers no authority, selects no benchmark technology.",
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
    "QualityState",
    # quality-specific projections
    "QUALITY_META_CLASS",
    "ENTITY_FOUNDING_UNIT",
    "ENTITY_CERTIFICATION_ID",
    "ATTRIBUTE_FOUNDING_UNIT",
    "ATTRIBUTE_CERTIFICATION_ID",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "SCHEMA_FOUNDING_UNIT",
    "SCHEMA_CERTIFICATION_ID",
    "TRACE_BACKWARD_QUALITY",
    "QUALITY_SUBSTRATE_REFS",
    "QualityKind",
    "QualityVerdict",
    "QUALITY_DIMENSIONS",
    "DIMENSION_FOR_KIND",
    "SCHEMA_RELATIVE_KINDS",
    "SCORE_MIN",
    "SCORE_MAX",
    "QUALITY_RELATIONSHIPS",
    "QUALITY_PRINCIPLES",
    "QUALITY_MEASUREMENT_RULES",
    "QUALITY_CONSTRAINTS",
    "QUALITY_APPLICABLE_LAWS",
    "QUALITY_DEFERRED_LAWS",
    "QUALITY_META_CONSTRAINTS",
]
