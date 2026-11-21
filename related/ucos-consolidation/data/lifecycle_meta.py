"""EC3-B10-U06 — Lifecycle meta-model constants (read-only projections of DATA-011).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Lifecycle Architecture (DATA-001 Constitution, DATA-004
Taxonomy, DATA-005 Meta-Model, **DATA-011 Universal Data Lifecycle Architecture**) that
the Lifecycle realization (**DMC-07**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the frozen
obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at the
constitutional anchor ``b7e7657`` (DATA-011 §1…§17) — no obligation is invented, none
is dropped. A lifecycle is **abstract, forward-only state progression only** — it
selects no workflow engine, ETL/migration tool, scheduler, orchestration engine, or
vendor (UDL-12 / DLA-09 / DLA-K5). Shared foundation constants (anchors, laws,
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
# The Lifecycle IS the frozen ontology lifecycle DOS-01…05 (DATA-011 §5/§8).
# DATA-011 §5 — the Lifecycle's own state set is the closed forward-only DOS-01…05
# (DEFINED → ACTIVE → DEPRECATED → SUPERSEDED → RETIRED, forward-only DOI-05; UDL-12).
# Identical forward-only state machine as the Datum/Attribute/Entity/Schema/Storage, so
# it is reused by reference (no parallel lifecycle model). This is the material subject
# the Lifecycle architecture governs.
# ---------------------------------------------------------------------------

#: The Lifecycle state type (reused DOS-01…05; DATA-011 §5, UDL-12).
LifecycleState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-011 §3 — the Lifecycle meta-class and its founding units
# ---------------------------------------------------------------------------

#: The Lifecycle meta-class id (DATA-005 §2; DMC-07).
LIFECYCLE_META_CLASS = "DMC-07"

#: The CERTIFIED unit whose construct the Lifecycle ``transitions`` (DMR-06, ref-only).
#: A lifecycle governs the forward-only state progression of a datum/entity; it
#: references the CERTIFIED DMC-02 Entity **by reference** as its transitioned subject
#: (DOR-06 / DMR-06) and carries no entity model of its own.
ENTITY_FOUNDING_UNIT = "EC3-B10-U03"
#: The certification id of the CERTIFIED DMC-02 Entity construct (transitions anchor).
ENTITY_CERTIFICATION_ID = "UCOS-CERT-DMC-02-def41470d3bac196"

#: The transitively-closed founding roots (transitions → Entity bears Attribute values Datum).
ATTRIBUTE_FOUNDING_UNIT = "EC3-B10-U02"
ATTRIBUTE_CERTIFICATION_ID = "UCOS-CERT-DMC-03-c57d36d3dbb2763d"
DATUM_FOUNDING_UNIT = "EC3-B10-U01"
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-011 §16)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Lifecycle records (DATA-011 → root).
TRACE_BACKWARD_LIFECYCLE: tuple[str, ...] = (
    "DMC-07",  # DATA-005 §2 / DATA-011 §3 — Lifecycle meta-class
    "DATA-011",  # Universal Data Lifecycle Architecture (UDLA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-12)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Lifecycle reuses by reference (UDL-02; DATA-011 §3):
#:   ENG-001 Identity (identified lifecycle — DLA-K1); ENG-002 Object (the lifecycle IS
#:   an object); ENG-004 Type (lifecycle + state typing — DLA-K1); ENG-005 Reference
#:   (transitions entity + binds RUNTIME state/event/policy by reference — DMR-06/11).
LIFECYCLE_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified lifecycle — DLA-K1 / UDL-04)
    "ENG-002",  # Object     (the lifecycle IS an ENG-002 object — UDL-05)
    "ENG-004",  # Type       (lifecycle + state typedness — DLA-K1 / UDL-03)
    "ENG-005",  # Reference  (transitions + RUNTIME state/event/policy refs — DMR-06/11)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-011 §5 — DXH-07 Lifecycle Hierarchy (state facets)
# ---------------------------------------------------------------------------


class StateFacet(str, Enum):
    """DXH-07 Lifecycle Hierarchy (DATA-004 §3; DATA-011 §5) — the facet of a state.

    Every lifecycle state is classified into exactly one DXH-07 facet (single-facet,
    DXC-02); none names or implies a workflow/scheduler product (UDL-12 / DLA-K5):
    """

    DEFINITIONAL = "Definitional-State"  # DEFINED — declared but not yet operative
    OPERATIVE = "Operative-State"  # ACTIVE — in use and authoritative
    TERMINAL = "Terminal-State"  # DEPRECATED / SUPERSEDED / RETIRED — end-of-life


#: DATA-011 §5 — the fixed, decidable mapping of each DOS-01…05 state to its DXH-07 facet.
STATE_FACETS: dict[DatumState, StateFacet] = {
    DatumState.DEFINED: StateFacet.DEFINITIONAL,
    DatumState.ACTIVE: StateFacet.OPERATIVE,
    DatumState.DEPRECATED: StateFacet.TERMINAL,
    DatumState.SUPERSEDED: StateFacet.TERMINAL,
    DatumState.RETIRED: StateFacet.TERMINAL,
}

# ---------------------------------------------------------------------------
# DATA-011 §6 — Lifecycle relationships (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which the Lifecycle participates (DATA-011 §6):
#:   DMR-06 transitions   (Lifecycle ← Entity/Datum; reference-only; MATERIAL — the
#:                         lifecycle transitions the entity/datum it governs, DOR-06)
#:   DMR-10 identified-by (Lifecycle → ENG-001 via ENG-002; MATERIAL, DOR-10)
#:   DMR-11 behaves-as    (Lifecycle → RUNTIME state/event; reference-only; MATERIAL —
#:                         state/event/guard behavior binds by reference, DLA-07 / DOR-11)
#: No relationship outside DMR-01…12 is admitted (DOI-01 / DMI-02).
LIFECYCLE_RELATIONSHIPS: tuple[str, ...] = ("DMR-06", "DMR-10", "DMR-11")

# ---------------------------------------------------------------------------
# DATA-011 §4 — Lifecycle principles (DLA-01…10)
# ---------------------------------------------------------------------------

#: The ten Lifecycle principles (DATA-011 §4), each mapped to its short obligation.
LIFECYCLE_PRINCIPLES: dict[str, str] = {
    "DLA-01": "Forward-Only Progression — transitions forward-only; undo is a new forward step.",
    "DLA-02": "Decidable States — every state is decidable, typed (ENG-004); the set is closed.",
    "DLA-03": "Recorded Transitions — every transition emits a recorded RUNTIME event by ref.",
    "DLA-04": "Guarded Transitions — each transition declares a decidable, non-enforcing guard.",
    "DLA-05": "Supersession Not Mutation — breaking change is supersession (new id + lineage).",
    "DLA-06": "Retention as Representation — retention/archival are Terminal-State records.",
    "DLA-07": "Lifecycle by Reference — state/event behavior binds by reference to RL-F2.",
    "DLA-08": "Additive Growth — new lifecycle state-kinds append additively (DXH-07); no renum.",
    "DLA-09": "Non-Constitutiveness — no authority, no secret, no technology selected.",
    "DLA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is labelled INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-011 §9 — Lifecycle transition & retention rules (DLA-C1…C5)
# ---------------------------------------------------------------------------

#: The five transition/retention rules (DATA-011 §9).
LIFECYCLE_TRANSITION_RULES: dict[str, str] = {
    "DLA-C1": "Transitions follow forward-only DEFINED→ACTIVE→DEPRECATED→SUPERSEDED→RETIRED; "
    "forward skips permitted, reversals not (DLA-01).",
    "DLA-C2": "Every transition is guarded by a decidable predicate and recorded (DLA-03/04).",
    "DLA-C3": "Retention/archival are represented as Terminal-State records; no scheduler.",
    "DLA-C4": "Supersession records lineage from the superseded identity to the new one (DLA-05).",
    "DLA-C5": "A datum/entity is in exactly one lifecycle state at any point (single-state).",
}

# ---------------------------------------------------------------------------
# DATA-011 §10 — Lifecycle contracts & constraints (DLA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Lifecycle contracts / constraints (DATA-011 §10).
LIFECYCLE_CONSTRAINTS: dict[str, str] = {
    "DLA-K1": "Every lifecycle and state is typed (ENG-004) and identified (ENG-001) — DMK-01.",
    "DLA-K2": "Every transition resolves to a RUNTIME event/state reference; redefines 0 — DMK-05.",
    "DLA-K3": "Transitions are forward-only and recorded — DOC-07; DOI-05.",
    "DLA-K4": "Guards are declarative and non-enforcing — DMK-07.",
    "DLA-K5": "No lifecycle selects technology or confers authority — DMK-08.",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Lifecycle construct
# ---------------------------------------------------------------------------

#: The Data laws the Lifecycle construct is directly obligated by (subset of UDL-*),
#: with **UDL-12 (forward-only recorded lifecycle) now materially in scope at the
#: strongest level**.
LIFECYCLE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. RUNTIME state/event + certified Entity)
    "UDL-03",  # typed (lifecycle + state)
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-09",  # references via ENG-005; founding acyclic
    "UDL-12",  # FORWARD-ONLY LIFECYCLE — decidable, recorded, guarded transitions (material)
    "UDL-13",  # non-enforcing governance (guards evaluate, do not enact)
    "UDL-14",  # evaluative facets (quality)
    "UDL-15",  # non-constitutive
)

#: Laws scoped to units not realized here (deferred for the Lifecycle construct):
#:   UDL-06 (ENG-003 value fidelity) is the Datum's obligation (transitive via subject);
#:   UDL-07 (entity boundedness) is the Entity unit's obligation; UDL-08 (attribute
#:   typedness) is the Attribute unit's obligation; UDL-10 (schema explicitness) is the
#:   Schema unit's obligation; UDL-11 (storage independence) is the Storage unit's.
LIFECYCLE_DEFERRED_LAWS: tuple[str, ...] = ("UDL-06", "UDL-07", "UDL-08", "UDL-10", "UDL-11")

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Lifecycle is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints a Lifecycle is bound by (DATA-005 §4; DATA-011 §15).
LIFECYCLE_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-03": "The founding/transition meta-relationship graph is acyclic (a DAG).",
    "DMK-05": "Transition behavior resolves to a RUNTIME event/state reference; none redefined.",
    "DMK-07": "Guards are declarative and non-enforcing (evaluate, do not enact).",
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
    "LifecycleState",
    # lifecycle-specific projections
    "LIFECYCLE_META_CLASS",
    "ENTITY_FOUNDING_UNIT",
    "ENTITY_CERTIFICATION_ID",
    "ATTRIBUTE_FOUNDING_UNIT",
    "ATTRIBUTE_CERTIFICATION_ID",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "TRACE_BACKWARD_LIFECYCLE",
    "LIFECYCLE_SUBSTRATE_REFS",
    "StateFacet",
    "STATE_FACETS",
    "LIFECYCLE_RELATIONSHIPS",
    "LIFECYCLE_PRINCIPLES",
    "LIFECYCLE_TRANSITION_RULES",
    "LIFECYCLE_CONSTRAINTS",
    "LIFECYCLE_APPLICABLE_LAWS",
    "LIFECYCLE_DEFERRED_LAWS",
    "LIFECYCLE_META_CONSTRAINTS",
]
