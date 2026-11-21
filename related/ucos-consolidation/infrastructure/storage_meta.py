"""EC3-B13-U04 — Infrastructure Storage-Hosting meta-model constants.

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003
(Ontology), INFRASTRUCTURE-005 (Meta-Model), and INFRASTRUCTURE-009 (Storage-Hosting
concern architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Storage-Hosting realization must conform to. It
**defines no new law and redefines no foundation concept** (UIL-02 / UIL-15); it only
names the frozen obligations so the realization can be checked against them
deterministically. The shared Infrastructure vocabulary (lifecycle states, admitted
relationships, the fifteen Infrastructure Laws, the twelve well-formedness rules, the
seven compliance conditions, and the CCE gate ids) is **imported by reference** from the
first Band-13 unit (:mod:`infrastructure.capability_meta`) and never redefined.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification
at the constitutional anchor ``b7e7657``:

* The **StorageHostingResource** leaf meta-class (INFRASTRUCTURE-005 §2/§7) — *the
  implementation-independent abstraction of where and how DF-2-represented data
  (DATA-010) is hosted and located — the hosting locus of represented data, never the
  representation itself* (INFRASTRUCTURE-009 §1).
* Its storage-hosting constructs (INFRASTRUCTURE-009 §2): Storage-Hosting Resource /
  Data Placement / Hosting Locality / Storage Capacity / Storage Hosting Class.
* Its concern rules ISTO-01…05 (INFRASTRUCTURE-009 §3) and the well-formedness / law /
  compliance obligations it is validated against (INFRASTRUCTURE-005 §5; INFRASTRUCTURE-001
  §7/§12).
"""

from __future__ import annotations

# --- Infrastructure vocabulary reused by reference from the first Band-13 unit ---
#     (UIL-02 — imported, never redefined).
from infrastructure.capability_meta import (
    ADMITTED_META_RELATIONSHIPS,
    CCE_GATES,
    CONSTITUTIONAL_ANCHOR,
    INFRASTRUCTURE_COMPLIANCE,
    INFRASTRUCTURE_LAWS,
    LEAF_META_CLASSES,
    LIFECYCLE_ORDER,
    WELL_FORMEDNESS_RULES,
    InfrastructureState,
)

#: The realization unit this module belongs to (EC-3 Band 13, Unit 04). Declared here —
#: never in ``infrastructure/__init__.py`` (whose ``REALIZATION_UNIT`` pins the first
#: unit, EC3-B13-U01, and is left untouched, per the Band-10/11/12 precedent).
REALIZATION_UNIT = "EC3-B13-U04"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Implementation substrate anchor: the certified/frozen baseline this unit builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` FROZEN + Band-12 ``application/**`` FROZEN
#: + Band-13 ``infrastructure.capability`` (EC3-B13-U01) + ``infrastructure.compute``
#: (EC3-B13-U02) + ``infrastructure.network`` (EC3-B13-U03) CERTIFIED, at HEAD ``7814a8d``).
IMPLEMENTATION_ANCHOR = "7814a8d"

#: The Infrastructure leaf meta-class id realized by this unit (INFRASTRUCTURE-005 §2/§7).
INFRASTRUCTURE_META_CLASS = "StorageHostingResource"

#: The backward traceability chain every realized Storage-Hosting Resource records
#: (INFRASTRUCTURE-009 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "StorageHostingResource",  # INFRASTRUCTURE-005 §2 — leaf meta-class
    "INFRASTRUCTURE-009",  # Universal Infrastructure Storage-Hosting Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Storage-Hosting Resource reuses by reference (UIL-02):
#:   ENG-001…005 (EL-1) · DF-2 (the hosted DATA-010 represented-data concern; ISTO-01 /
#:   UIL-11 — the defining reuse). A StorageHostingResource **hosts** a DATA-010 datum by
#:   ENG-005 reference and declares its locality by an intra-band ENG-005 reference to a
#:   Locality (realized by the INFRASTRUCTURE-011 unit) and honors isolation boundaries by
#:   ENG-005 reference to an IsolationBoundary (likewise INFRASTRUCTURE-011). It hosts no
#:   RL-F2 execution (that is Compute), connects no endpoints (that is Network), and
#:   delivers no SF-2/AF-3 (that is Distribution); it redefines **no** DATA-010 data
#:   representation (UIL-11 — infrastructure governs *where/how hosted*, never the data).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (capacity / value fidelity)
    "ENG-004",  # Type      (typed Storage Hosting Class, UIL-03)
    "ENG-005",  # Relationship/Reference (hosts / locatedAt / boundary references)
    "DF-2",  # Represented data hosted by reference (ISTO-01 / UIL-11); redefined nowhere
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §2 — leaf meta-class closure (re-exported for local checks)
# ---------------------------------------------------------------------------

#: The meta-relationships a Storage-Hosting Resource intrinsically participates in.
#: A Resource is the domain of ``hosts`` ({Resource,Distribution} → FrozenLowerConstruct,
#: 1..*, downward-only/non-mutating) and ``locatedAt`` ({HostingStructure,Resource} →
#: Locality, multiplicity 1, total) — INFRASTRUCTURE-005 §4. For a Storage-Hosting Resource
#: the ``hosts`` edges are realized as its **data placements** — the typed ENG-005
#: reference to the frozen DATA-010 datum each hosts (ISTO-01/02; WF-7; no data concern
#: re-modeled — UIL-11). It is the domain of no ``contains``/``provisions``/``scales``/
#: ``sustains``/``evaluates`` edge (those are HostingStructure/Process/Arrangement/Facet
#: concerns), and it holds no upward founding edge (a Resource is placed on a Node by the
#: Node's ``contains`` edge, realized by the INFRASTRUCTURE-011 unit — a Resource never
#: founds upward).
STORAGE_RELATIONSHIPS: tuple[str, ...] = ("hosts", "locatedAt")

# Re-export the shared, frozen vocabulary so downstream storage modules import it from
# a single place without redefining any of it (UIL-02).
__SHARED__ = (
    ADMITTED_META_RELATIONSHIPS,
    LEAF_META_CLASSES,
    LIFECYCLE_ORDER,
    InfrastructureState,
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for the Storage Resource
# ---------------------------------------------------------------------------

#: The Infrastructure laws a Storage-Hosting Resource construct is directly obligated by.
#: The universal laws (UIL-01…05, UIL-15) plus the Resource/Storage laws mapped from the
#: concern rules: UIL-07 (data placement honors isolation boundaries and locality
#: declarations — ISTO-03), UIL-08 (a resource declares type/capacity/locality/hosted
#: datum reference — ISTO-02), UIL-11 (storage-hosting hosts DF-2 DATA-010 data by
#: reference; redefines no data — ISTO-01, the defining reuse), UIL-13 (storage capacity
#: scaling unbounded — ISTO-04).
STORAGE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-07",
    "UIL-08",
    "UIL-11",
    "UIL-13",
    "UIL-15",
)

#: Laws scoped to Capability-reuse / Network / Provisioning / Distribution / Topology /
#: EvaluativeFacet units, N/A to a Storage-Hosting Resource: UIL-06 (PL-F2/SF-2/AF-3
#: hosting/delivery — Capability/Distribution), UIL-09 (topology/connectivity typed
#: ENG-005 reference — Network/Topology), UIL-10 (provisioning binds RL-F2 —
#: ProvisioningProcess; a StorageHostingResource hosts no execution), UIL-12
#: (distribution/delivery transport — Distribution), UIL-14 (security/governance
#: evaluative non-enforcing — EvaluativeFacet).
STORAGE_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",
    "UIL-09",
    "UIL-10",
    "UIL-12",
    "UIL-14",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-009 §3 — concern rules (ISTO-01…05)
# ---------------------------------------------------------------------------

#: The five Storage-Hosting concern rules (INFRASTRUCTURE-009 §3).
STORAGE_CONCERN_RULES: dict[str, str] = {
    "ISTO-01": "Storage-hosting locates DATA-010 data by reference; no data concern "
    "re-modeled/redefined.",
    "ISTO-02": "Every storage-hosting resource declares type, capacity, locality, and a "
    "hosted datum reference.",
    "ISTO-03": "Data placement honors isolation boundaries and locality declarations.",
    "ISTO-04": "Storage capacity scaling is evaluative and unbounded (no artificial "
    "ceiling).",
    "ISTO-05": "No storage technology/product/vendor selected; no authority conferred.",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for the Storage Resource
# ---------------------------------------------------------------------------

#: The WF rules a Storage-Hosting Resource is directly subject to. WF-5 (*every Resource
#: declares capacity and locality*) and **WF-7** (*every StorageHostingResource hosts a
#: DATA-010 datum by reference*) are the **governing, materially-exercised** rules for
#: this unit — WF-7 being the storage-unique obligation absent from the Compute/Network
#: Resources. WF-4/6/8/9/10 are scoped to Environment/ProvisioningProcess/Distribution/
#: ScalingArrangement/EvaluativeFacet constructs (INFRASTRUCTURE-005 §5) and are recorded
#: N/A to the Storage-Hosting Resource with rationale.
STORAGE_APPLICABLE_WF: tuple[str, ...] = (
    "WF-1",
    "WF-2",
    "WF-3",
    "WF-5",
    "WF-7",
    "WF-11",
    "WF-12",
)

#: WF rules scoped to other leaf meta-classes, N/A to the Storage-Hosting Resource.
STORAGE_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-6",
    "WF-8",
    "WF-9",
    "WF-10",
)

__all__ = [
    "REALIZATION_UNIT",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "INFRASTRUCTURE_META_CLASS",
    "TRACE_BACKWARD",
    "SUBSTRATE_REFS",
    "STORAGE_RELATIONSHIPS",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "STORAGE_APPLICABLE_LAWS",
    "STORAGE_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "STORAGE_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "STORAGE_APPLICABLE_WF",
    "STORAGE_INAPPLICABLE_WF",
    "CCE_GATES",
]
