"""EC3-B13-U02 — Infrastructure Compute meta-model constants.

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003
(Ontology), INFRASTRUCTURE-005 (Meta-Model), and INFRASTRUCTURE-007 (Compute concern
architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Compute realization must conform to. It **defines no
new law and redefines no foundation concept** (UIL-02 / UIL-15); it only names the
frozen obligations so the realization can be checked against them deterministically. The
shared Infrastructure vocabulary (lifecycle states, admitted relationships, the fifteen
Infrastructure Laws, the twelve well-formedness rules, the seven compliance conditions,
and the CCE gate ids) is **imported by reference** from the first Band-13 unit
(:mod:`infrastructure.capability_meta`) and never redefined.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification
at the constitutional anchor ``b7e7657``:

* The **ComputeResource** leaf meta-class (INFRASTRUCTURE-005 §2/§7) — *the
  implementation-independent abstraction of execution-hosting capacity: where and with
  what capacity RL-F2 execution is hosted* (INFRASTRUCTURE-007 §1).
* Its compute constructs (INFRASTRUCTURE-007 §2): Compute Resource / Compute Node Binding
  / Execution Host / Compute Capacity / Compute Class.
* Its concern rules ICMP-01…05 (INFRASTRUCTURE-007 §3) and the well-formedness / law /
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

#: The realization unit this module belongs to (EC-3 Band 13, Unit 02). Declared here —
#: never in ``infrastructure/__init__.py`` (whose ``REALIZATION_UNIT`` pins the first
#: unit, EC3-B13-U01, and is left untouched, per the Band-10/11/12 precedent).
REALIZATION_UNIT = "EC3-B13-U02"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Implementation substrate anchor: the certified/frozen baseline this unit builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` FROZEN + Band-12 ``application/**`` FROZEN
#: + Band-13 ``infrastructure.capability`` (EC3-B13-U01) CERTIFIED, at HEAD ``ce7d5d0``).
IMPLEMENTATION_ANCHOR = "ce7d5d0"

#: The Infrastructure leaf meta-class id realized by this unit (INFRASTRUCTURE-005 §2/§7).
INFRASTRUCTURE_META_CLASS = "ComputeResource"

#: The backward traceability chain every realized Compute Resource records
#: (INFRASTRUCTURE-007 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "ComputeResource",  # INFRASTRUCTURE-005 §2 — leaf meta-class
    "INFRASTRUCTURE-007",  # Universal Infrastructure Compute Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Compute Resource reuses by reference (UIL-02):
#:   ENG-001…005 (EL-1) · RL-F2 (the hosted execution behavior; ICMP-01 / UIL-10 — the
#:   defining reuse). A ComputeResource hosts RL-F2 *execution* by reference and declares
#:   its locality by an intra-band ENG-005 reference to a Locality (realized by the
#:   INFRASTRUCTURE-011 unit); it consumes no PL-F2/SF-2/AF-3/DF-2 construct directly
#:   (those are Distribution/Storage-Hosting concerns).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (capacity / value fidelity)
    "ENG-004",  # Type      (typed Compute Class, UIL-03)
    "ENG-005",  # Relationship/Reference (hosts / locatedAt references)
    "RL-F2",  # Runtime execution hosted by reference (ICMP-01 / UIL-10); redefined nowhere
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §2 — leaf meta-class closure (re-exported for local checks)
# ---------------------------------------------------------------------------

#: The meta-relationships a Compute Resource intrinsically participates in.
#: A Resource is the domain of ``hosts`` ({Resource,Distribution} → FrozenLowerConstruct,
#: 1..*, downward-only/non-mutating) and ``locatedAt`` ({HostingStructure,Resource} →
#: Locality, multiplicity 1, total) — INFRASTRUCTURE-005 §4. It is the domain of no
#: ``contains``/``provisions``/``scales``/``sustains``/``evaluates`` edge (those are
#: HostingStructure/Process/Arrangement/Facet concerns), and it holds no ``dependsOn``
#: placement edge to a Node (the ``contains`` edge that places a Resource on a Node is the
#: Node's, realized by the INFRASTRUCTURE-011 unit — a Resource never founds upward).
COMPUTE_RELATIONSHIPS: tuple[str, ...] = ("hosts", "locatedAt")

# Re-export the shared, frozen vocabulary so downstream compute modules import it from
# a single place without redefining any of it (UIL-02).
__SHARED__ = (
    ADMITTED_META_RELATIONSHIPS,
    LEAF_META_CLASSES,
    LIFECYCLE_ORDER,
    InfrastructureState,
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for the Compute Resource
# ---------------------------------------------------------------------------

#: The Infrastructure laws a Compute Resource construct is directly obligated by.
#: The universal laws (UIL-01…05, UIL-15) plus the Resource/Compute laws mapped from the
#: concern rules: UIL-08 (a resource declares type/capacity/locality/hosted constructs —
#: ICMP-02), UIL-09 (placement acyclic, ENG-005 references — ICMP-03), UIL-10 (hosts
#: RL-F2 execution by reference — ICMP-01, the defining reuse), UIL-13 (compute capacity
#: scaling unbounded — ICMP-04).
COMPUTE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-08",
    "UIL-09",
    "UIL-10",
    "UIL-13",
    "UIL-15",
)

#: Laws scoped to Capability-reuse / Environment / Storage-Hosting / Distribution /
#: EvaluativeFacet units, N/A to a Compute Resource: UIL-06 (PL-F2/SF-2/AF-3 hosting —
#: Compute hosts RL-F2 *execution*, not PL-F2/SF-2/AF-3), UIL-07 (environment
#: boundedness), UIL-11 (storage-hosting DATA-010), UIL-12 (distribution/delivery
#: transport), UIL-14 (security/governance evaluative non-enforcing).
COMPUTE_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",
    "UIL-07",
    "UIL-11",
    "UIL-12",
    "UIL-14",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-007 §3 — concern rules (ICMP-01…05)
# ---------------------------------------------------------------------------

#: The five Compute concern rules (INFRASTRUCTURE-007 §3).
COMPUTE_CONCERN_RULES: dict[str, str] = {
    "ICMP-01": "Compute hosts RL-F2 execution by reference; redefines no runtime concern; "
    "re-founds no PLATFORM-012 Runtime.",
    "ICMP-02": "Every compute resource declares type, capacity, locality, and a hosted "
    "execution reference.",
    "ICMP-03": "Compute resources are placed on Nodes via ENG-005 references; founding "
    "placement acyclic.",
    "ICMP-04": "Compute capacity scaling is evaluative and unbounded (no artificial ceiling).",
    "ICMP-05": "No hardware/VM/container/orchestrator/technology selected; no authority "
    "conferred.",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for the Compute Resource
# ---------------------------------------------------------------------------

#: The WF rules a Compute Resource is directly subject to. WF-5 (*every Resource declares
#: capacity and locality*) is the **governing, materially-exercised** rule for this unit.
#: WF-4/6/7/8/9/10 are scoped to Environment/ProvisioningProcess/StorageHostingResource/
#: Distribution/ScalingArrangement/EvaluativeFacet constructs (INFRASTRUCTURE-005 §5) and
#: are recorded N/A to the Compute Resource with rationale.
COMPUTE_APPLICABLE_WF: tuple[str, ...] = ("WF-1", "WF-2", "WF-3", "WF-5", "WF-11", "WF-12")

#: WF rules scoped to other leaf meta-classes, N/A to the Compute Resource.
COMPUTE_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-6",
    "WF-7",
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
    "COMPUTE_RELATIONSHIPS",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "COMPUTE_APPLICABLE_LAWS",
    "COMPUTE_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "COMPUTE_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "COMPUTE_APPLICABLE_WF",
    "COMPUTE_INAPPLICABLE_WF",
    "CCE_GATES",
]
