"""EC3-B13-U07 — Infrastructure Resilience & Availability meta-model constants.

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003
(Ontology), INFRASTRUCTURE-005 (Meta-Model), and INFRASTRUCTURE-012 (Resilience &
Availability concern architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Resilience & Availability realization must conform to.
It **defines no new law and redefines no foundation concept** (UIL-02 / UIL-15); it only
names the frozen obligations so the realization can be checked against them
deterministically. The shared Infrastructure vocabulary (lifecycle states, admitted
relationships, the fifteen Infrastructure Laws, the twelve well-formedness rules, the
seven compliance conditions, and the CCE gate ids) is **imported by reference** from the
first Band-13 unit (:mod:`infrastructure.capability_meta`) and never redefined.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification
at the constitutional anchor ``b7e7657``:

* The **two** leaf meta-classes concern 012 instantiates (INFRASTRUCTURE-005 §2/§7;
  INFRASTRUCTURE-012 §2): **AvailabilityTopology** and **ScalingArrangement**.
* The **two** constructs that realise these: **AvailabilityTopology** (evaluative continuity
  arrangement) and **ScalingArrangement** (evaluative expand/contract topology).
* Its concern rules IRES-01…06 (INFRASTRUCTURE-012 §3) and the well-formedness / law /
  compliance obligations each construct is validated against (INFRASTRUCTURE-005 §5;
  INFRASTRUCTURE-001 §7/§12).

This unit is a **dual-construct** concern: concern 012 instantiates two leaf meta-classes
via two constructs, materially exercising governing conditions **C6** (scaling posture
unbounded — UIL-13/WF-9) and **C7** (no technology — UIL-15), and is evaluative
non-enforcing (WF-10).
"""

from __future__ import annotations

# --- Infrastructure vocabulary reused by reference from the first Band-13 unit ---
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

#: The realization unit this module belongs to (EC-3 Band 13, Unit 07).
REALIZATION_UNIT = "EC3-B13-U07"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Implementation substrate anchor: the certified/frozen baseline this unit builds upon.
#: EC-1 engine CERTIFIED + EC-2 platform FROZEN + Band-10 data CERTIFIED-COMPLETE +
#: Band-11 service FROZEN + Band-12 application FROZEN + Band-13 U01…U06 CERTIFIED.
IMPLEMENTATION_ANCHOR = "2d8af7a"

#: The two Infrastructure leaf meta-class ids realized by this unit (INFRASTRUCTURE-005
#: §2/§7 — concern 012's non-overlapping meta-class set). Every construct instantiates
#: exactly one of these (WF-1).
RESILIENCE_META_CLASSES: tuple[str, ...] = (
    "AvailabilityTopology",
    "ScalingArrangement",
)

#: The two constructs realized by this unit mapping to the two meta-classes.
#: AvailabilityTopology meta-class: AvailabilityTopology (evaluative continuity
#: arrangement). ScalingArrangement meta-class: ScalingArrangement (evaluative
#: expand/contract topology).
RESILIENCE_CONSTRUCT_CLASSES: tuple[str, ...] = (
    "AvailabilityTopology",
    "ScalingArrangement",
)

#: The backward-lineage tail every realized construct records after its own meta-class
#: root. The construct's meta-class (AvailabilityTopology or ScalingArrangement) is the
#: head (rooted per-construct).
TRACE_TAIL: tuple[str, ...] = (
    "INFRASTRUCTURE-012",  # Universal Infrastructure Resilience & Availability Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Resilience & Availability constructs reuse by reference
#: (UIL-02): ENG-001…005 (EL-1) · RL-F2 (runtime workflow/state — IRES-03, continuity/
#: scaling bind RL-F2 by reference) · PL-F2 (platform composition) · SF-2/AF-3 (hosted
#: operation/delivery capability — referenced by AvailabilityTopology).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",   # Identity (identified-by)
    "ENG-002",   # Object (borne-as-object)
    "ENG-003",   # Value (value fidelity)
    "ENG-004",   # Type (typed construct, UIL-03)
    "ENG-005",   # Relationship/Reference (sustains/scales refs)
    "PL-F2",     # Platform composition reused by reference
    "RL-F2",     # Runtime workflow/state bound by reference (IRES-03)
    "SF-2",      # Service capability hosted by reference
    "AF-3",      # Application experience hosted by reference
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §4 — meta-relationships each construct participates in
# ---------------------------------------------------------------------------

#: The admitted meta-relationships each of the two constructs participates in as a
#: domain (INFRASTRUCTURE-005 §4). AvailabilityTopology sustains Resources/Clusters;
#: ScalingArrangement scales Resources. Both may dependOn other constructs.
CONSTRUCT_RELATIONSHIPS: dict[str, tuple[str, ...]] = {
    "AvailabilityTopology": ("sustains", "dependsOn"),
    "ScalingArrangement": ("scales", "dependsOn"),
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-012 §3 — concern rules (IRES-01…06)
# ---------------------------------------------------------------------------

#: The six Resilience & Availability concern rules (INFRASTRUCTURE-012 §3).
RESILIENCE_CONCERN_RULES: dict[str, str] = {
    "IRES-01": "Resilience/availability/scaling are decidable evaluative topologies; they enact/provision nothing.",
    "IRES-02": "Scaling declares no artificial ceiling; only physical reality bounds it.",
    "IRES-03": "Continuity/scaling bind RL-F2 concerns by reference; no runtime concern redefined.",
    "IRES-04": "Every posture/metric is decided from declared attributes; nothing implicit.",
    "IRES-05": "Availability topology honors isolation boundaries.",
    "IRES-06": "No HA/failover/autoscale technology/vendor selected; no authority conferred.",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for concern 012
# ---------------------------------------------------------------------------

#: The Infrastructure laws the Resilience & Availability constructs are directly obligated by.
#: Universal laws (UIL-01…05, UIL-15) + resilience/scaling laws: UIL-13 (resilience/
#: availability/scaling evaluative RL-F2-bound, scaling unbounded — IRES-01/02),
#: UIL-14 (evaluative, non-enforcing — IRES-01), UIL-07 (isolation boundaries — IRES-05).
RESILIENCE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-07",
    "UIL-13",
    "UIL-14",
    "UIL-15",
)

#: Laws scoped to Resource/Environment/Provisioning/Storage/Topology/Distribution units,
#: N/A to Resilience & Availability constructs.
RESILIENCE_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",   # PL-F2/SF-2/AF-3 hosting/delivery as Capability behaviour — Capability unit
    "UIL-08",   # Resource capacity/locality — Resource units
    "UIL-09",   # Topology reuses PL-F2 + ENG-005 — Topology unit
    "UIL-10",   # Provisioning binds RL-F2 — ProvisioningProcess unit
    "UIL-11",   # Storage-hosting hosts DATA-010 — Storage unit
    "UIL-12",   # Distribution/delivery hosts AF-3/SF-2 — Distribution unit
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for concern 012
# ---------------------------------------------------------------------------

#: The WF rules the Resilience & Availability constructs are directly subject to.
#: WF-9 (every ScalingArrangement declares scalingPosture with no artificial ceiling —
#: THE governing Scaling rule), WF-10 (every EvaluativeFacet has nonEnforcing=true —
#: Resilience/availability/scaling are evaluative, non-enforcing — IRES-01).
#: WF-5/6/7/8 are scoped to Resource/ProvisioningProcess/Storage/Distribution constructs.
RESILIENCE_APPLICABLE_WF: tuple[str, ...] = (
    "WF-1",
    "WF-2",
    "WF-3",
    "WF-9",
    "WF-10",
    "WF-11",
    "WF-12",
)

#: WF rules scoped to other leaf meta-classes, N/A to Resilience & Availability constructs.
RESILIENCE_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-5",
    "WF-6",
    "WF-7",
    "WF-8",
)

__all__ = [
    "REALIZATION_UNIT",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "RESILIENCE_META_CLASSES",
    "RESILIENCE_CONSTRUCT_CLASSES",
    "TRACE_TAIL",
    "SUBSTRATE_REFS",
    "CONSTRUCT_RELATIONSHIPS",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "RESILIENCE_APPLICABLE_LAWS",
    "RESILIENCE_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "RESILIENCE_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "RESILIENCE_APPLICABLE_WF",
    "RESILIENCE_INAPPLICABLE_WF",
    "CCE_GATES",
]
