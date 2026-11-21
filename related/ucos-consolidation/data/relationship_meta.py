"""EC3-B10-U10 — Relationship meta-model constants (read-only projections of DATA-008).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Relationship Architecture (DATA-001 Constitution, DATA-004
Taxonomy, DATA-005 Meta-Model, **DATA-008 Universal Data Relationship Architecture**) that
the Relationship realization (**DMC-04**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the frozen
obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at the
constitutional anchor ``b7e7657`` (DATA-008 §1…§17) — no obligation is invented, none is
dropped. A data relationship is a **typed, decidable association between data entities,
realized as an ENG-005 reference** — it introduces no new connection construct (DRA-01 /
UDL-09), is classified by an ENG-004 Type (DRA-02), declares explicit cardinality (DRA-04),
is acyclic where founding (DRA-03), resolves its endpoints (DRA-05), and confers no
authority and selects no technology (DRA-09). Shared foundation constants (anchors, laws,
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
# A relationship follows the frozen ontology lifecycle DOS-01…05 (DATA-008 §8).
# Identical forward-only state machine as every other data construct, so it is reused by
# reference (no parallel lifecycle model).
# ---------------------------------------------------------------------------

#: The Relationship lifecycle state type (reused DOS-01…05; DATA-008 §8, UDL-12).
RelationshipState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-008 §3 — the Relationship meta-class and its founding units
# ---------------------------------------------------------------------------

#: The Relationship meta-class id (DATA-005 §2; DMC-04).
RELATIONSHIP_META_CLASS = "DMC-04"

#: The CERTIFIED unit whose construct a Relationship ``relates`` (DMR-03, ref-only).
#: A relationship connects data entities; it references the CERTIFIED DMC-02 Entity **by
#: reference** as each endpoint (DOR-03 / DMR-03) and carries no entity model of its own.
ENTITY_FOUNDING_UNIT = "EC3-B10-U03"
#: The certification id of the CERTIFIED DMC-02 Entity construct (relates endpoint anchor).
ENTITY_CERTIFICATION_ID = "UCOS-CERT-DMC-02-def41470d3bac196"

#: The transitively-closed founding roots (relates → Entity bears Attribute values Datum).
ATTRIBUTE_FOUNDING_UNIT = "EC3-B10-U02"
ATTRIBUTE_CERTIFICATION_ID = "UCOS-CERT-DMC-03-c57d36d3dbb2763d"
DATUM_FOUNDING_UNIT = "EC3-B10-U01"
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-008 §16)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Relationship records.
TRACE_BACKWARD_RELATIONSHIP: tuple[str, ...] = (
    "DMC-04",  # DATA-005 §2 / DATA-008 §3 — Relationship meta-class
    "DATA-008",  # Universal Data Relationship Architecture (UDRA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-09)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Relationship reuses by reference (UDL-02):
#:   ENG-001 Identity (identified object — DRA-K1); ENG-002 Object (the relationship IS an
#:   object — DRA-K1); ENG-004 Type (object + kind typing — DRA-02 / DRA-K1); ENG-005
#:   Reference (relates endpoints + binds RUNTIME navigation by reference — DMR-03/11).
RELATIONSHIP_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified object — DRA-K1 / UDL-04)
    "ENG-002",  # Object     (the relationship IS an ENG-002 object — DRA-K1 / UDL-05)
    "ENG-004",  # Type       (object + kind typedness — DRA-02 / UDL-03)
    "ENG-005",  # Reference  (relates endpoints + RUNTIME navigation references — DMR-03/11)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-008 §5 — DXH-04 Relationship Hierarchy
# ---------------------------------------------------------------------------


class RelationshipKind(str, Enum):
    """DXH-04 Relationship Hierarchy (DATA-004 §3; DATA-008 §5).

    A relationship is classified by exactly one kind (single-facet, DXC-02); each is an
    ENG-004 type (DRA-02) and an ENG-005 reference (DRA-01) — none introduces a new
    connection construct (UDL-09):
    """

    ASSOCIATION = "Association"  # peer, non-founding (DOR-03)
    COMPOSITION = "Composition"  # founding, acyclic (bears / described-by; DOR-01/04)
    REFERENCE = "Reference"  # cross-entity pointer (ENG-005 reference; DOR-02/10)


class RelationshipDirection(str, Enum):
    """The declared directionality of a relationship (DRA-06; DATA-008 §4).

    Whether a relationship is directed (source → target) or peer is declared explicitly.
    Association is peer; founding (Composition) and cross-entity Reference are directed.
    """

    DIRECTED = "directed"  # an ordered source → target relationship (founding / reference)
    PEER = "peer"  # a symmetric, non-founding association (DOR-03)


class RelationshipCardinality(str, Enum):
    """The explicit, decidable cardinality of a relationship (DRA-04 / DRA-C3).

    Cardinality is always one of these decidable ordinals; there is **no
    unbounded-by-default member** — an implicit/unbounded cardinality is structurally
    impossible (DRA-C3).
    """

    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_MANY = "N:M"


class RelationshipVerdict(str, Enum):
    """A recorded, decidable relationship-integrity judgment (DOV-08).

    The verdict *records* an integrity/cardinality-conformance outcome; it enforces and
    grants nothing (UDL-09 / DRA-09).
    """

    PASS = "pass"  # noqa: S105 — integrity verdict value, not a credential (DOV-08)
    FAIL = "fail"  # an integrity/cardinality deficiency is recorded (routed to a Gap Report)
    NOT_APPLICABLE = "not-applicable"  # no applicable integrity dimension to record


# ---------------------------------------------------------------------------
# DATA-008 §5/§6 — the founding kinds and the declared direction of each kind
# ---------------------------------------------------------------------------

#: The relationship kinds that establish a **founding (structural) dependency** and must
#: therefore be acyclic (DRA-03 / DRA-C1). Only Composition is founding; Association and
#: Reference are reference-only (DATA-008 §5/§6).
FOUNDING_KINDS: frozenset[RelationshipKind] = frozenset({RelationshipKind.COMPOSITION})

#: The declared direction each DXH-04 kind carries (DRA-06). Association is peer; founding
#: Composition and cross-entity Reference are directed (DATA-008 §4/§5).
DIRECTION_FOR_KIND: dict[RelationshipKind, RelationshipDirection] = {
    RelationshipKind.ASSOCIATION: RelationshipDirection.PEER,
    RelationshipKind.COMPOSITION: RelationshipDirection.DIRECTED,
    RelationshipKind.REFERENCE: RelationshipDirection.DIRECTED,
}

#: The explicit, decidable cardinalities a relationship may declare (DRA-04). The absence
#: of an unbounded member makes unbounded-by-default structurally impossible (DRA-C3).
RELATIONSHIP_CARDINALITIES: tuple[str, ...] = tuple(c.value for c in RelationshipCardinality)

# ---------------------------------------------------------------------------
# DATA-008 §6 — Relationship participation (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which the Relationship object participates (DATA-008 §6):
#:   DMR-03 relates      (Relationship → Entity endpoints; reference-only; MATERIAL —
#:                        the object connects the entities it relates, DOR-03)
#:   DMR-04 described-by (Relationship → Schema; a *reference obligation* — DRA-07; no
#:                        Schema construct (DMC-05) is realized here, only a reference)
#:   DMR-10 identified-by(Relationship → ENG-001 via ENG-002; MATERIAL, DOR-10)
#:   DMR-11 behaves-as   (Relationship → RUNTIME navigation/integrity-check evaluation;
#:                        reference-only; MATERIAL — navigation binds by reference,
#:                        DATA-008 §7 / DOB-05/06)
#: No relationship outside DMR-01…12 is admitted (DOI-01 / DMI-02).
RELATIONSHIP_RELATIONSHIPS: tuple[str, ...] = ("DMR-03", "DMR-04", "DMR-10", "DMR-11")

# ---------------------------------------------------------------------------
# DATA-008 §4 — Relationship principles (DRA-01…10)
# ---------------------------------------------------------------------------

#: The ten Relationship principles (DATA-008 §4), each mapped to its short obligation.
RELATIONSHIP_PRINCIPLES: dict[str, str] = {
    "DRA-01": "Relationship by Reference — every relationship IS an ENG-005 reference.",
    "DRA-02": "Relationship Typedness — every relationship is classified by an ENG-004 Type.",
    "DRA-03": "Founding Acyclicity — founding relationships form a DAG; no self-founding.",
    "DRA-04": "Cardinality Explicitness — every relationship declares decidable cardinality.",
    "DRA-05": "Referential Integrity — every endpoint resolves to an existing entity (ENG-001).",
    "DRA-06": "Directionality Declared — directed vs peer is declared explicitly.",
    "DRA-07": "Schema Description — a relationship is described by a schema before ACTIVE.",
    "DRA-08": "Additive Growth — new relationship types append additively (DXH-04).",
    "DRA-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "DRA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-008 §9 — Relationship integrity & cardinality rules (DRA-C1…C5)
# ---------------------------------------------------------------------------

#: The five integrity / cardinality rules (DATA-008 §9).
RELATIONSHIP_INTEGRITY_RULES: dict[str, str] = {
    "DRA-C1": "Founding (Composition) relationships form a DAG; cycles are rejected (DMK-03).",
    "DRA-C2": "Every relationship endpoint resolves to an existing entity identity (DOI-03).",
    "DRA-C3": "Cardinality (1:1, 1:N, N:M) is declared and decidable; unbounded is prohibited.",
    "DRA-C4": "Peer associations introduce no founding dependency (may cycle as non-founding).",
    "DRA-C5": "A relationship references entity identities; it never absorbs entity content.",
}

# ---------------------------------------------------------------------------
# DATA-008 §10 — Relationship contracts & constraints (DRA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Relationship contracts / constraints (DATA-008 §10).
RELATIONSHIP_CONSTRAINTS: dict[str, str] = {
    "DRA-K1": "Every relationship is typed (ENG-004) and IS an ENG-005 reference — DMK-01.",
    "DRA-K2": "Every founding relationship is acyclic — DMK-03.",
    "DRA-K3": "Every relationship is schema-described with declared cardinality before ACTIVE.",
    "DRA-K4": "Every endpoint resolves (referential integrity) — DOI-03.",
    "DRA-K5": "No relationship selects technology or confers authority — DMK-08.",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Relationship construct
# ---------------------------------------------------------------------------

#: The Data laws the Relationship construct is directly obligated by (subset of UDL-*),
#: with **UDL-09 (Relationship by Reference; founding acyclic) now materially in scope at
#: the strongest level**.
RELATIONSHIP_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. RUNTIME policy + certified Entity)
    "UDL-03",  # typed (object + kind)
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-09",  # RELATIONSHIP — ENG-005 references; founding acyclic (MATERIAL)
    "UDL-10",  # explicit, decidable cardinality declared; schema-describable (never implicit)
    "UDL-12",  # forward-only lifecycle + append-only supersession
    "UDL-15",  # non-constitutive
)

#: Laws scoped to units not realized here (deferred for the Relationship construct):
#:   UDL-06 (value fidelity — transitive via related entities); UDL-07 (entity
#:   boundedness — the endpoints); UDL-08 (attribute typedness); UDL-11 (storage
#:   independence — exercised via technology-neutrality); UDL-13 (governance); UDL-14
#:   (quality/security) — each another unit's obligation.
RELATIONSHIP_DEFERRED_LAWS: tuple[str, ...] = (
    "UDL-06",
    "UDL-07",
    "UDL-08",
    "UDL-11",
    "UDL-13",
    "UDL-14",
)

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Relationship object is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints a Relationship object is bound by (DATA-005 §4; DATA-008 §15).
RELATIONSHIP_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-03": "The founding meta-relationship graph is acyclic (a DAG).",
    "DMK-05": "Navigation/integrity-check resolves to a RUNTIME reference; none redefined.",
    "DMK-08": "Confers no authority, selects no relationship/query/storage technology.",
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
    "RelationshipState",
    # relationship-specific projections
    "RELATIONSHIP_META_CLASS",
    "ENTITY_FOUNDING_UNIT",
    "ENTITY_CERTIFICATION_ID",
    "ATTRIBUTE_FOUNDING_UNIT",
    "ATTRIBUTE_CERTIFICATION_ID",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "TRACE_BACKWARD_RELATIONSHIP",
    "RELATIONSHIP_SUBSTRATE_REFS",
    "RelationshipKind",
    "RelationshipDirection",
    "RelationshipCardinality",
    "RelationshipVerdict",
    "FOUNDING_KINDS",
    "DIRECTION_FOR_KIND",
    "RELATIONSHIP_CARDINALITIES",
    "RELATIONSHIP_RELATIONSHIPS",
    "RELATIONSHIP_PRINCIPLES",
    "RELATIONSHIP_INTEGRITY_RULES",
    "RELATIONSHIP_CONSTRAINTS",
    "RELATIONSHIP_APPLICABLE_LAWS",
    "RELATIONSHIP_DEFERRED_LAWS",
    "RELATIONSHIP_META_CONSTRAINTS",
]
