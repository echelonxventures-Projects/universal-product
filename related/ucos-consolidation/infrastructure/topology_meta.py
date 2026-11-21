"""EC3-B13-U06 — Infrastructure Topology & Distribution meta-model constants.

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003
(Ontology), INFRASTRUCTURE-005 (Meta-Model), and INFRASTRUCTURE-010 (Topology &
Distribution concern architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Topology & Distribution realization must conform to.
It **defines no new law and redefines no foundation concept** (UIL-02 / UIL-15); it only
names the frozen obligations so the realization can be checked against them
deterministically. The shared Infrastructure vocabulary (lifecycle states, admitted
relationships, the fifteen Infrastructure Laws, the twelve well-formedness rules, the
seven compliance conditions, and the CCE gate ids) is **imported by reference** from the
first Band-13 unit (:mod:`infrastructure.capability_meta`) and never redefined.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification
at the constitutional anchor ``b7e7657``:

* The **two** leaf meta-classes concern 010 instantiates (INFRASTRUCTURE-005 §2/§7;
  INFRASTRUCTURE-010 §2): **Topology** and **Distribution**.
* The **five** constructs that realise these: **Topology**, **LocalityMap**, and
  **PlacementRule** (Topology meta-class); **DistributionArrangement** and
  **DeliveryArrangement** (Distribution meta-class).
* Its concern rules ITOP-01…06 (INFRASTRUCTURE-010 §3) and the well-formedness / law /
  compliance obligations each construct is validated against (INFRASTRUCTURE-005 §5;
  INFRASTRUCTURE-001 §7/§12).

This unit is a **multi-construct** concern (like U05): concern 010 instantiates two leaf
meta-classes via five constructs, materially exercising governing conditions **C4**
(Distribution typed and hosts AF-3/SF-2 by reference, UIL-12), **C5** (Topology founding
acyclic via ENG-005 references, UIL-09), and **C7** (no technology selection, UIL-15).
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

#: The realization unit this module belongs to (EC-3 Band 13, Unit 06).
REALIZATION_UNIT = "EC3-B13-U06"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Implementation substrate anchor: the certified/frozen baseline this unit builds upon.
#: EC-1 engine CERTIFIED + EC-2 platform FROZEN + Band-10 data CERTIFIED-COMPLETE +
#: Band-11 service FROZEN + Band-12 application FROZEN + Band-13 U01…U05 CERTIFIED.
IMPLEMENTATION_ANCHOR = "074ffb2"

#: The two Infrastructure leaf meta-class ids realized by this unit (INFRASTRUCTURE-005
#: §2/§7 — concern 010's non-overlapping meta-class set). Every construct instantiates
#: exactly one of these (WF-1).
TOPOLOGY_META_CLASSES: tuple[str, ...] = (
    "Topology",
    "Distribution",
)

#: The five constructs realized by this unit mapping to the two meta-classes.
#: Topology meta-class: Topology (structural arrangement), LocalityMap (abstract
#: region/zone/location assignment), PlacementRule (evaluative placement rules).
#: Distribution meta-class: DistributionArrangement (capability distribution),
#: DeliveryArrangement (experience/operations delivery to actors).
TOPOLOGY_CONSTRUCT_CLASSES: tuple[str, ...] = (
    "Topology",
    "LocalityMap",
    "PlacementRule",
    "DistributionArrangement",
    "DeliveryArrangement",
)

#: The backward-lineage tail every realized construct records after its own meta-class
#: root. The construct's meta-class (Topology or Distribution) is the head (rooted
#: per-construct).
TRACE_TAIL: tuple[str, ...] = (
    "INFRASTRUCTURE-010",  # Universal Infrastructure Topology & Distribution Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Topology & Distribution constructs reuse by reference
#: (UIL-02): ENG-001…005 (EL-1) · PL-F2 (platform composition — ITOP-01, topology reuses
#: PL-F2 composition by reference) · RL-F2 (runtime workflow/state — Distribution hosts
#: AF-3/SF-2 by reference) · SF-2/AF-3 (hosted operation/delivery capability — ITOP-03,
#: Distribution hosts by reference).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",   # Identity (identified-by)
    "ENG-002",   # Object (borne-as-object)
    "ENG-003",   # Value (value fidelity)
    "ENG-004",   # Type (typed construct, UIL-03)
    "ENG-005",   # Relationship/Reference (contains/locatedAt/hosts refs)
    "PL-F2",     # Platform composition reused by reference (ITOP-01)
    "RL-F2",     # Runtime workflow/state bound by reference
    "SF-2",      # Service capability hosted by reference (ITOP-03)
    "AF-3",      # Application experience delivered by reference (ITOP-03)
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §4 — meta-relationships each construct participates in
# ---------------------------------------------------------------------------

#: The admitted meta-relationships each of the five constructs participates in as a
#: domain (INFRASTRUCTURE-005 §4). Topology uses contains + dependsOn; LocalityMap and
#: PlacementRule are evaluative; DistributionArrangement hosts + dependsOn;
#: DeliveryArrangement hosts + dependsOn.
CONSTRUCT_RELATIONSHIPS: dict[str, tuple[str, ...]] = {
    "Topology": ("contains", "dependsOn"),
    "LocalityMap": ("dependsOn",),
    "PlacementRule": ("dependsOn",),
    "DistributionArrangement": ("hosts", "dependsOn"),
    "DeliveryArrangement": ("hosts", "dependsOn"),
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-010 §3 — concern rules (ITOP-01…06)
# ---------------------------------------------------------------------------

#: The six Topology & Distribution concern rules (INFRASTRUCTURE-010 §3).
TOPOLOGY_CONCERN_RULES: dict[str, str] = {
    "ITOP-01": "Topology strictly reuses PL-F2 composition and ENG-005; no new connection constructs.",
    "ITOP-02": "Founding topology must be acyclic.",
    "ITOP-03": "Distribution/delivery is typed and hosts AF-3/SF-2 by reference; no transport/CDN selected.",
    "ITOP-04": "All locality (Region/Zone/Location) remains abstract; no provider-specific regions.",
    "ITOP-05": "Must honor isolation boundaries; cross-boundary arrangements explicitly declared and typed.",
    "ITOP-06": "Scaling is evaluative and unbounded; confers no inherent authority; selects no technology.",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for concern 010
# ---------------------------------------------------------------------------

#: The Infrastructure laws the Topology & Distribution constructs are directly obligated by.
#: Universal laws (UIL-01…05, UIL-15) + topology/distribution laws: UIL-09 (topology reuses
#: PL-F2 + ENG-005 references, founding acyclic — ITOP-01/02), UIL-12 (distribution/delivery
#: typed, hosts AF-3/SF-2 by reference — ITOP-03), UIL-07 (cross-boundary declarations —
#: ITOP-05), UIL-13 (unbounded evaluative scaling — ITOP-06).
TOPOLOGY_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-07",
    "UIL-09",
    "UIL-12",
    "UIL-13",
    "UIL-15",
)

#: Laws scoped to Resource/Environment/Provisioning/Storage/Capability units, N/A to
#: Topology & Distribution constructs.
TOPOLOGY_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",   # PL-F2/SF-2/AF-3 hosting/delivery as Capability behaviour — Distribution hosts by ref
    "UIL-08",   # Resource capacity/locality — Resource units
    "UIL-10",   # Provisioning binds RL-F2 — ProvisioningProcess unit
    "UIL-11",   # Storage-hosting hosts DATA-010 — Storage unit
    "UIL-14",   # Security/governance evaluative — Facet units
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for concern 010
# ---------------------------------------------------------------------------

#: The WF rules the Topology & Distribution constructs are directly subject to.
#: WF-8 (every Distribution hosts AF-3/SF-2 by reference, no transport technology — THE
#: governing Distribution rule), WF-3 (contains/dependsOn acyclic — THE governing Topology
#: rule), WF-9 (ScalingArrangement posture applies via Scaling, but PlacementRule evaluative
#: nature is captured by is_evaluative_facet). WF-5/6/7/10 are scoped to Resource/
#: ProvisioningProcess/Storage/EvaluativeFacet constructs.
TOPOLOGY_APPLICABLE_WF: tuple[str, ...] = (
    "WF-1",
    "WF-2",
    "WF-3",
    "WF-8",
    "WF-11",
    "WF-12",
)

#: WF rules scoped to other leaf meta-classes, N/A to Topology & Distribution constructs.
TOPOLOGY_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-5",
    "WF-6",
    "WF-7",
    "WF-9",
    "WF-10",
)

__all__ = [
    "REALIZATION_UNIT",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "TOPOLOGY_META_CLASSES",
    "TOPOLOGY_CONSTRUCT_CLASSES",
    "TRACE_TAIL",
    "SUBSTRATE_REFS",
    "CONSTRUCT_RELATIONSHIPS",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "TOPOLOGY_APPLICABLE_LAWS",
    "TOPOLOGY_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "TOPOLOGY_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "TOPOLOGY_APPLICABLE_WF",
    "TOPOLOGY_INAPPLICABLE_WF",
    "CCE_GATES",
]
