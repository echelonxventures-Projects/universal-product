"""EC3-B10-U07 — Governance meta-model constants (read-only projections of DATA-012).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Governance Architecture (DATA-001 Constitution, DATA-004
Taxonomy, DATA-005 Meta-Model, **DATA-012 Universal Data Governance Architecture**) that
the Governance realization (**DMC-08**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the frozen
obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at the
constitutional anchor ``b7e7657`` (DATA-012 §1…§17) — no obligation is invented, none
is dropped. Data governance is **declarative, record-only, and non-enforcing** — it
confers no operational/constitutional authority, grants no access, and enacts nothing
(UDL-13 / DGA-02/03/09). Shared foundation constants (anchors, laws, compliance
conditions, meta-validity gate, CCE gates, lifecycle states) are **reused by reference**
from the CERTIFIED DMC-01 surface (:mod:`data.meta`); re-exported, never re-defined.
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
# A governance object follows the frozen ontology lifecycle DOS-01…05 (DATA-012 §8).
# Identical forward-only state machine as every other data construct, so it is reused by
# reference (no parallel lifecycle model).
# ---------------------------------------------------------------------------

#: The Governance-object lifecycle state type (reused DOS-01…05; DATA-012 §8, UDL-12).
GovernanceState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-012 §3 — the Governance meta-class and its founding units
# ---------------------------------------------------------------------------

#: The Governance meta-class id (DATA-005 §2; DMC-08).
GOVERNANCE_META_CLASS = "DMC-08"

#: The CERTIFIED unit whose construct the Governance object ``governs`` (DMR-07, ref-only).
#: Governance records the conformance of a data construct to the Data Laws; it references
#: the CERTIFIED DMC-02 Entity **by reference** as its governed subject (DOR-07 / DMR-07)
#: and carries no entity model of its own.
ENTITY_FOUNDING_UNIT = "EC3-B10-U03"
#: The certification id of the CERTIFIED DMC-02 Entity construct (governs anchor).
ENTITY_CERTIFICATION_ID = "UCOS-CERT-DMC-02-def41470d3bac196"

#: The transitively-closed founding roots (governs → Entity bears Attribute values Datum).
ATTRIBUTE_FOUNDING_UNIT = "EC3-B10-U02"
ATTRIBUTE_CERTIFICATION_ID = "UCOS-CERT-DMC-03-c57d36d3dbb2763d"
DATUM_FOUNDING_UNIT = "EC3-B10-U01"
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-012 §16)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Governance object records.
TRACE_BACKWARD_GOVERNANCE: tuple[str, ...] = (
    "DMC-08",  # DATA-005 §2 / DATA-012 §3 — Governance meta-class
    "DATA-012",  # Universal Data Governance Architecture (UDGA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-13)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Governance object reuses by reference (UDL-02):
#:   ENG-001 Identity (identified object — DGA-K1); ENG-002 Object (the record IS an
#:   object bearing the judgment — DGA-K4); ENG-004 Type (object + kind typing — DGA-K1);
#:   ENG-005 Reference (governs a construct + binds RUNTIME policy by reference — DMR-07/11).
GOVERNANCE_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified object — DGA-K1 / UDL-04)
    "ENG-002",  # Object     (the record IS an ENG-002 object — DGA-K4 / UDL-05)
    "ENG-004",  # Type       (object + kind typedness — DGA-K1 / UDL-03)
    "ENG-005",  # Reference  (governs + RUNTIME policy references — DMR-07/11)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-012 §5 — DXH-08 Governance-Object Hierarchy
# ---------------------------------------------------------------------------


class GovernanceKind(str, Enum):
    """DXH-08 Governance-Object Hierarchy (DATA-004 §3; DATA-012 §5).

    A governance object is classified by exactly one kind (single-facet, DXC-02); none
    names or implies a policy/enforcement product (UDL-13 / DGA-K5):
    """

    CONFORMANCE_RECORD = "Conformance-Record"  # records law/meta-model conformance
    POLICY_OBJECT = "Policy-Object"  # declarative, non-enforcing data constraint
    EVALUATION_RECORD = "Evaluation-Record"  # recorded governance judgment (DOV-08)


class GovernanceVerdict(str, Enum):
    """A recorded, decidable governance judgment (DGA-06; DOV-08) — evaluative only.

    The verdict *records* an evaluation outcome; it enforces nothing (DGA-02).
    """

    CONFORMANT = "conformant"  # the governed construct satisfies its applicable laws
    NON_CONFORMANT = "non-conformant"  # a violation is recorded (routed to a Gap Report)
    NOT_APPLICABLE = "not-applicable"  # no applicable obligation to evaluate


# ---------------------------------------------------------------------------
# DATA-012 §6 — Governance relationships (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which the Governance object participates (DATA-012 §6):
#:   DMR-07 governs      (Governance-Object ← Data construct; reference-only; MATERIAL —
#:                        the object governs the construct it evaluates, DOR-07)
#:   DMR-10 identified-by(Governance-Object → ENG-001 via ENG-002; MATERIAL, DOR-10)
#:   DMR-11 behaves-as   (Governance-Object → RUNTIME policy evaluation; reference-only;
#:                        MATERIAL — evaluation binds by reference, DGA-07 / DOR-11)
#: No relationship outside DMR-01…12 is admitted (DOI-01 / DMI-02).
GOVERNANCE_RELATIONSHIPS: tuple[str, ...] = ("DMR-07", "DMR-10", "DMR-11")

# ---------------------------------------------------------------------------
# DATA-012 §4 — Governance principles (DGA-01…10)
# ---------------------------------------------------------------------------

#: The ten Governance principles (DATA-012 §4), each mapped to its short obligation.
GOVERNANCE_PRINCIPLES: dict[str, str] = {
    "DGA-01": "Declarativeness — governance is a declarative, decidable predicate.",
    "DGA-02": "Non-Enforcement — governance evaluates and records; enforces nothing.",
    "DGA-03": "Non-Authority — confers no authority and grants no access.",
    "DGA-04": "Conformance Focus — records conformance to UDL-01…15 + the meta-model.",
    "DGA-05": "Stewardship as Record — ownership/stewardship are recorded, not powers.",
    "DGA-06": "Evaluation Recording — every judgment is recorded (DOV-08) on an object.",
    "DGA-07": "Reuse by Reference — evaluation binds by reference to RUNTIME policy.",
    "DGA-08": "Additive Growth — new governance-object kinds append additively (DXH-08).",
    "DGA-09": "Non-Constitutiveness — embeds no secret and selects no technology.",
    "DGA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-012 §9 — Governance evaluation rules (DGA-C1…C5)
# ---------------------------------------------------------------------------

#: The five evaluation rules (DATA-012 §9).
GOVERNANCE_EVALUATION_RULES: dict[str, str] = {
    "DGA-C1": "A conformance-record decidably records satisfaction of each applicable Law.",
    "DGA-C2": "A policy-object is a declarative predicate; evaluating grants no access.",
    "DGA-C3": "An evaluation-record is immutable once recorded; re-evaluation is a new record.",
    "DGA-C4": "Stewardship/ownership are recorded descriptors; they confer no power.",
    "DGA-C5": "A violation is routed to a Gap Report; governance does not remediate/enforce.",
}

# ---------------------------------------------------------------------------
# DATA-012 §10 — Governance contracts & constraints (DGA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Governance contracts / constraints (DATA-012 §10).
GOVERNANCE_CONSTRAINTS: dict[str, str] = {
    "DGA-K1": "Every governance object is typed (ENG-004) and identified (ENG-001) — DMK-01.",
    "DGA-K2": "Every governance object is declarative and non-enforcing — DMK-07; UDL-13.",
    "DGA-K3": "Every evaluation binds by reference to RUNTIME policy; redefines 0 — DMK-05.",
    "DGA-K4": "Every judgment is recorded against an ENG-002 object (DOV-08) — DME-02.",
    "DGA-K5": "No governance object grants access, confers authority, or selects tech — DMK-08.",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Governance construct
# ---------------------------------------------------------------------------

#: The Data laws the Governance construct is directly obligated by (subset of UDL-*),
#: with **UDL-13 (Governance as Declarative Constraint) now materially in scope at the
#: strongest level**.
GOVERNANCE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. RUNTIME policy + certified Entity)
    "UDL-03",  # typed (object + kind)
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-09",  # references via ENG-005; founding acyclic
    "UDL-12",  # forward-only lifecycle + supersession on breaking policy change
    "UDL-13",  # GOVERNANCE — declarative, evaluative, non-enforcing; confers no authority
    "UDL-14",  # evaluative facets (quality)
    "UDL-15",  # non-constitutive
)

#: Laws scoped to units not realized here (deferred for the Governance construct):
#:   UDL-06 (value fidelity — transitive via governed construct); UDL-07 (entity
#:   boundedness); UDL-08 (attribute typedness); UDL-10 (schema explicitness);
#:   UDL-11 (storage independence) — each another unit's obligation.
GOVERNANCE_DEFERRED_LAWS: tuple[str, ...] = ("UDL-06", "UDL-07", "UDL-08", "UDL-10", "UDL-11")

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Governance object is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints a Governance object is bound by (DATA-005 §4; DATA-012 §15).
GOVERNANCE_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-03": "The founding/governance meta-relationship graph is acyclic (a DAG).",
    "DMK-05": "Evaluation resolves to a RUNTIME policy reference; none redefined.",
    "DMK-07": "Declarative and non-enforcing (evaluates, does not enact).",
    "DMK-08": "Grants no access, confers no authority, selects no technology.",
}

#: The representative applicable-law set the canonical Conformance-Record evaluates
#: (DGA-C1 / DGA-04) — a decidable subset of UDL-* the governed construct is obligated by.
CANONICAL_GOVERNED_LAWS: tuple[str, ...] = (
    "UDL-02",
    "UDL-03",
    "UDL-04",
    "UDL-05",
    "UDL-13",
    "UDL-15",
)

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
    "GovernanceState",
    # governance-specific projections
    "GOVERNANCE_META_CLASS",
    "ENTITY_FOUNDING_UNIT",
    "ENTITY_CERTIFICATION_ID",
    "ATTRIBUTE_FOUNDING_UNIT",
    "ATTRIBUTE_CERTIFICATION_ID",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "TRACE_BACKWARD_GOVERNANCE",
    "GOVERNANCE_SUBSTRATE_REFS",
    "GovernanceKind",
    "GovernanceVerdict",
    "GOVERNANCE_RELATIONSHIPS",
    "GOVERNANCE_PRINCIPLES",
    "GOVERNANCE_EVALUATION_RULES",
    "GOVERNANCE_CONSTRAINTS",
    "GOVERNANCE_APPLICABLE_LAWS",
    "GOVERNANCE_DEFERRED_LAWS",
    "GOVERNANCE_META_CONSTRAINTS",
    "CANONICAL_GOVERNED_LAWS",
]
