"""EC3-B10-U09 — Security meta-model constants (read-only projections of DATA-014).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Security Architecture (DATA-001 Constitution, DATA-004
Taxonomy, DATA-005 Meta-Model, **DATA-014 Universal Data Security Architecture**) that
the Security realization (**DMC-10**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the frozen
obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at the
constitutional anchor ``b7e7657`` (DATA-014 §1…§18) — no obligation is invented, none
is dropped. Data security is **representation-level, decidable, evaluative, and
non-enforcing** — a security object *classifies and records* a data construct's
sensitivity, confidentiality, and integrity requirements; it grants no access, selects
no cryptography, and enforces nothing (UDL-14 / DZA-01/02/03). Shared foundation
constants (anchors, laws, compliance conditions, meta-validity gate, CCE gates,
lifecycle states) are **reused by reference** from the CERTIFIED DMC-01 surface
(:mod:`data.meta`); re-exported, never re-defined.
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
# A security object follows the frozen ontology lifecycle DOS-01…05 (DATA-014 §8).
# Identical forward-only state machine as every other data construct, so it is reused by
# reference (no parallel lifecycle model).
# ---------------------------------------------------------------------------

#: The Security-object lifecycle state type (reused DOS-01…05; DATA-014 §8, UDL-12).
SecurityState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-014 §3 — the Security meta-class and its founding units
# ---------------------------------------------------------------------------

#: The Security meta-class id (DATA-005 §2; DMC-10).
SECURITY_META_CLASS = "DMC-10"

#: The CERTIFIED unit whose construct the Security object ``classifies`` (DMR-09, ref-only).
#: Security records a sensitivity/confidentiality/integrity classification of a data
#: construct; it references the CERTIFIED DMC-02 Entity **by reference** as its classified
#: subject (DOR-09 / DMR-09) and carries no entity model of its own.
ENTITY_FOUNDING_UNIT = "EC3-B10-U03"
#: The certification id of the CERTIFIED DMC-02 Entity construct (classifies anchor).
ENTITY_CERTIFICATION_ID = "UCOS-CERT-DMC-02-def41470d3bac196"

#: The transitively-closed founding roots (classifies → Entity bears Attribute values Datum).
ATTRIBUTE_FOUNDING_UNIT = "EC3-B10-U02"
ATTRIBUTE_CERTIFICATION_ID = "UCOS-CERT-DMC-03-c57d36d3dbb2763d"
DATUM_FOUNDING_UNIT = "EC3-B10-U01"
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-014 §17)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Security object records.
TRACE_BACKWARD_SECURITY: tuple[str, ...] = (
    "DMC-10",  # DATA-005 §2 / DATA-014 §3 — Security meta-class
    "DATA-014",  # Universal Data Security Architecture (UDZA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-14)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Security object reuses by reference (UDL-02):
#:   ENG-001 Identity (identified object — DZA-K1); ENG-002 Object (the record IS an
#:   object bearing the classification — DZA-K4); ENG-004 Type (object + kind typing —
#:   DZA-K1); ENG-005 Reference (classifies a construct + binds RUNTIME policy by
#:   reference — DMR-09/11).
SECURITY_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified object — DZA-K1 / UDL-04)
    "ENG-002",  # Object     (the record IS an ENG-002 object — DZA-K4 / UDL-05)
    "ENG-004",  # Type       (object + kind typedness — DZA-K1 / UDL-03)
    "ENG-005",  # Reference  (classifies + RUNTIME policy references — DMR-09/11)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-014 §5 — DXH-10 Security-Object Hierarchy
# ---------------------------------------------------------------------------


class SecurityKind(str, Enum):
    """DXH-10 Security-Object Hierarchy (DATA-004 §3; DATA-014 §5).

    A security object is classified by exactly one kind (single-facet, DXC-02); each is a
    decidable, evaluative classification dimension (DZA-02) — none names or implies a
    cipher, key scheme, access-control/IAM system, DLP, or security product
    (UDL-14 / DZA-K5):
    """

    CLASSIFICATION_LABEL = "Classification-Label"  # sensitivity/category (evaluative label)
    CONFIDENTIALITY_RECORD = "Confidentiality-Record"  # confidentiality/disclosure classification
    INTEGRITY_RECORD = "Integrity-Record"  # integrity requirement classification


class SecurityVerdict(str, Enum):
    """A recorded, decidable security-classification judgment (DZA-C1; DOV-08).

    The verdict *records* a classification outcome; it enforces and grants nothing
    (DZA-01 / DZA-C2).
    """

    PASS = "pass"  # noqa: S105 — classification verdict value, not a credential (DZA-C1 / DOV-08)
    FAIL = "fail"  # a classification deficiency is recorded (routed to a Gap Report, DZA-C1)
    NOT_APPLICABLE = "not-applicable"  # no applicable dimension to classify


# ---------------------------------------------------------------------------
# DATA-014 §2/§5 — the decidable security dimensions and their facet mapping
# ---------------------------------------------------------------------------

#: The three decidable security dimensions (DZA-02; DXH-10). A classification records a
#: requirement along exactly one of these; membership is decidable and single-facet
#: (DXC-02).
SECURITY_DIMENSIONS: tuple[str, ...] = ("sensitivity", "confidentiality", "integrity")

#: The single dimension each DXH-10 kind classifies (single-facet, DXC-02 / DZA-02).
DIMENSION_FOR_KIND: dict[SecurityKind, str] = {
    SecurityKind.CLASSIFICATION_LABEL: "sensitivity",
    SecurityKind.CONFIDENTIALITY_RECORD: "confidentiality",
    SecurityKind.INTEGRITY_RECORD: "integrity",
}

#: The minimum/maximum recorded classification level — a decidable, bounded ordinal
#: (0 = lowest/public … 3 = highest/restricted). This is an *evaluative label ordinal*
#: (DATA-014 §5: public/internal/restricted as evaluative labels); it selects no scheme,
#: cipher, or product (DZA-07 / DZA-C5).
LEVEL_MIN = 0
LEVEL_MAX = 3

# ---------------------------------------------------------------------------
# DATA-014 §6 — Security relationships (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which the Security object participates (DATA-014 §6):
#:   DMR-09 classifies   (Security-Object ← Data construct; reference-only; MATERIAL —
#:                        the object classifies the construct it protects, DOR-09)
#:   DMR-10 identified-by(Security-Object → ENG-001 via ENG-002; MATERIAL, DOR-10)
#:   DMR-11 behaves-as   (Security-Object → RUNTIME policy integrity-check evaluation;
#:                        reference-only; MATERIAL — evaluation binds by reference,
#:                        DZA-06 / DOR-11)
#: No relationship outside DMR-01…12 is admitted (DOI-01 / DMI-02).
SECURITY_RELATIONSHIPS: tuple[str, ...] = ("DMR-09", "DMR-10", "DMR-11")

# ---------------------------------------------------------------------------
# DATA-014 §4 — Security principles (DZA-01…10)
# ---------------------------------------------------------------------------

#: The ten Security principles (DATA-014 §4), each mapped to its short obligation.
SECURITY_PRINCIPLES: dict[str, str] = {
    "DZA-01": "Classification, Not Enforcement — classifies and records; grants no access.",
    "DZA-02": "Sensitivity Dimensioned — sensitivity/confidentiality/integrity are decidable.",
    "DZA-03": "Enforcement by Reference — any enforcement is a downstream concern, by reference.",
    "DZA-04": "Classification Recording — every classification is recorded; immutable once made.",
    "DZA-05": "Least-Disclosure as Representation — confidentiality represents disclosure needs.",
    "DZA-06": "Integrity as Classification — integrity-checking binds by reference to RUNTIME.",
    "DZA-07": "No Cryptography Selection — selects no cipher, key scheme, protocol, or product.",
    "DZA-08": "Additive Growth — new classification kinds append additively (DXH-10).",
    "DZA-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "DZA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-014 §9 — Security classification rules (DZA-C1…C5)
# ---------------------------------------------------------------------------

#: The five classification rules (DATA-014 §9).
SECURITY_CLASSIFICATION_RULES: dict[str, str] = {
    "DZA-C1": "Each classification dimension is a decidable predicate over a data construct.",
    "DZA-C2": "A classification records a requirement; it grants no access (DZA-01).",
    "DZA-C3": "Enforcement obligations are expressed as references to downstream concerns.",
    "DZA-C4": "A classification is immutable once recorded; a re-classification is a new record.",
    "DZA-C5": "No cryptography, key scheme, or product is named or selected (DZA-07).",
}

# ---------------------------------------------------------------------------
# DATA-014 §10 — Security contracts & constraints (DZA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Security contracts / constraints (DATA-014 §10).
SECURITY_CONSTRAINTS: dict[str, str] = {
    "DZA-K1": "Every security object is typed (ENG-004) and identified (ENG-001) — DMK-01.",
    "DZA-K2": "Every security object is evaluative and non-enforcing — DMK-07; UDL-14.",
    "DZA-K3": "Every classification/integrity-check binds by reference to RUNTIME — DMK-05.",
    "DZA-K4": "Every classification is recorded against an ENG-002 object (DOV-08) — DME-02.",
    "DZA-K5": "No security object selects crypto/controls tech or confers authority (DMK-08).",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Security construct
# ---------------------------------------------------------------------------

#: The Data laws the Security construct is directly obligated by (subset of UDL-*),
#: with **UDL-14 (Quality & Security as Evaluative Facets) now materially in scope at the
#: strongest level**.
SECURITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. RUNTIME policy + certified Entity)
    "UDL-03",  # typed (object + kind)
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-09",  # references via ENG-005; founding acyclic
    "UDL-12",  # forward-only lifecycle + append-only re-classification
    "UDL-14",  # SECURITY — decidable evaluative facet; classifies/records, enacts nothing
    "UDL-15",  # non-constitutive
)

#: Laws scoped to units not realized here (deferred for the Security construct):
#:   UDL-06 (value fidelity — transitive via classified construct); UDL-07 (entity
#:   boundedness); UDL-08 (attribute typedness); UDL-10 (schema explicitness); UDL-11
#:   (storage independence — no crypto/masking technology, exercised via DZA-C5); UDL-13
#:   (governance) — each another unit's obligation.
SECURITY_DEFERRED_LAWS: tuple[str, ...] = (
    "UDL-06",
    "UDL-07",
    "UDL-08",
    "UDL-10",
    "UDL-11",
    "UDL-13",
)

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Security object is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints a Security object is bound by (DATA-005 §4; DATA-014 §16).
SECURITY_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-03": "The founding/classification meta-relationship graph is acyclic (a DAG).",
    "DMK-05": "Classification/integrity-check resolves to a RUNTIME reference; none redefined.",
    "DMK-07": "Evaluative and non-enforcing (classifies/records, does not enact).",
    "DMK-08": "Confers no authority, selects no cryptography/controls technology.",
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
    "SecurityState",
    # security-specific projections
    "SECURITY_META_CLASS",
    "ENTITY_FOUNDING_UNIT",
    "ENTITY_CERTIFICATION_ID",
    "ATTRIBUTE_FOUNDING_UNIT",
    "ATTRIBUTE_CERTIFICATION_ID",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "TRACE_BACKWARD_SECURITY",
    "SECURITY_SUBSTRATE_REFS",
    "SecurityKind",
    "SecurityVerdict",
    "SECURITY_DIMENSIONS",
    "DIMENSION_FOR_KIND",
    "LEVEL_MIN",
    "LEVEL_MAX",
    "SECURITY_RELATIONSHIPS",
    "SECURITY_PRINCIPLES",
    "SECURITY_CLASSIFICATION_RULES",
    "SECURITY_CONSTRAINTS",
    "SECURITY_APPLICABLE_LAWS",
    "SECURITY_DEFERRED_LAWS",
    "SECURITY_META_CONSTRAINTS",
]
