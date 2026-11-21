"""EC3-B13-U05 — Infrastructure Environment & Provisioning meta-model constants.

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003
(Ontology), INFRASTRUCTURE-005 (Meta-Model), and INFRASTRUCTURE-011 (Environment &
Provisioning concern architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Environment & Provisioning realization must conform to.
It **defines no new law and redefines no foundation concept** (UIL-02 / UIL-15); it only
names the frozen obligations so the realization can be checked against them
deterministically. The shared Infrastructure vocabulary (lifecycle states, admitted
relationships, the fifteen Infrastructure Laws, the twelve well-formedness rules, the
seven compliance conditions, and the CCE gate ids) is **imported by reference** from the
first Band-13 unit (:mod:`infrastructure.capability_meta`) and never redefined.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification
at the constitutional anchor ``b7e7657``:

* The **six** leaf meta-classes concern 011 instantiates (INFRASTRUCTURE-005 §2/§7;
  INFRASTRUCTURE-011 §2): **Locality** and **IsolationBoundary** (foundational);
  **Node**, **Cluster** and **Environment** (HostingStructures); and **ProvisioningProcess**
  (a Process bound to RL-F2 workflow by reference).
* Its concern rules IENV-01…06 (INFRASTRUCTURE-011 §3) and the well-formedness / law /
  compliance obligations each construct is validated against (INFRASTRUCTURE-005 §5;
  INFRASTRUCTURE-001 §7/§12).

This unit is unlike the single-construct Capability/Compute/Network/Storage-Hosting units:
concern 011 is the frozen meta-model's one **multi-construct** concern (INFRASTRUCTURE-005
§7 maps it to six leaf meta-classes), so this unit realizes all six, materially exercising
three governing conditions at once — **C4** (Environment bounded/isolated, WF-4 / UIL-07),
**C5** (containment founding acyclic, WF-3 / UIL-09), and **C6** (ProvisioningProcess binds
RL-F2 workflow, WF-6 / UIL-10).
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

#: The realization unit this module belongs to (EC-3 Band 13, Unit 05). Declared here —
#: never in ``infrastructure/__init__.py`` (whose ``REALIZATION_UNIT`` pins the first
#: unit, EC3-B13-U01, and is left untouched, per the Band-10/11/12 precedent).
REALIZATION_UNIT = "EC3-B13-U05"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Implementation substrate anchor: the certified/frozen baseline this unit builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` FROZEN + Band-12 ``application/**`` FROZEN
#: + Band-13 ``infrastructure.capability`` (U01) + ``infrastructure.compute`` (U02) +
#: ``infrastructure.network`` (U03) + ``infrastructure.storage`` (U04) CERTIFIED, at
#: HEAD ``2ee4842``).
IMPLEMENTATION_ANCHOR = "2ee4842"

#: The six Infrastructure leaf meta-class ids realized by this unit (INFRASTRUCTURE-005
#: §2/§7 — concern 011's complete, non-overlapping meta-class set). Every realized
#: construct instantiates exactly one of these (WF-1).
ENVIRONMENT_META_CLASSES: tuple[str, ...] = (
    "Locality",
    "IsolationBoundary",
    "Node",
    "Cluster",
    "Environment",
    "ProvisioningProcess",
)

#: The subset of :data:`ENVIRONMENT_META_CLASSES` that are HostingStructures
#: (INFRASTRUCTURE-005 §2) — the constructs that declare a ``locality`` meta-attribute and
#: participate in the ``contains`` founding relationship.
HOSTING_STRUCTURE_META_CLASSES: tuple[str, ...] = ("Node", "Cluster", "Environment")

#: The shared backward-lineage tail every realized construct records after its own
#: meta-class root (INFRASTRUCTURE-011 → root). The construct's own meta-class is the
#: head (rooted per-construct), so this unit's lineage is rooted at whichever of the six
#: leaf meta-classes the construct instantiates.
TRACE_TAIL: tuple[str, ...] = (
    "INFRASTRUCTURE-011",  # Universal Infrastructure Environment & Provisioning Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Environment & Provisioning constructs reuse by reference
#: (UIL-02): ENG-001…005 (EL-1) · RL-F2 (the workflow/state concern a ProvisioningProcess
#: binds by reference — IENV-04 / UIL-10; a ProvisioningProcess re-founds no PLATFORM-012/013
#: Runtime/Deployment). Environments/Nodes/Clusters host lower-layer constructs (Resources)
#: **by reference** and redefine none (UIL-02). The `hosts` of concrete DF-2/SF-2/AF-3 is a
#: Storage-Hosting / Distribution concern, not an Environment concern.
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity)
    "ENG-004",  # Type      (typed construct, UIL-03)
    "ENG-005",  # Relationship/Reference (contains / locatedAt / boundary / provisions refs)
    "RL-F2",  # Runtime workflow/state a ProvisioningProcess binds by reference (UIL-10)
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §4 — meta-relationships each construct participates in
# ---------------------------------------------------------------------------

#: The admitted meta-relationships each of the six leaf meta-classes participates in as a
#: domain (INFRASTRUCTURE-005 §4). Locality and IsolationBoundary are foundational targets
#: (participate in no founding edge as a domain); the HostingStructures use ``contains`` +
#: ``locatedAt``; the ProvisioningProcess uses ``provisions``. ``boundary`` is a mandatory
#: meta-attribute of an Environment (INFRASTRUCTURE-005 §3), not one of the eight admitted
#: meta-relationships, so it is not listed here.
CONSTRUCT_RELATIONSHIPS: dict[str, tuple[str, ...]] = {
    "Locality": (),
    "IsolationBoundary": (),
    "Node": ("contains", "locatedAt"),
    "Cluster": ("contains", "locatedAt"),
    "Environment": ("contains", "locatedAt"),
    "ProvisioningProcess": ("provisions",),
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-011 §3 — concern rules (IENV-01…06)
# ---------------------------------------------------------------------------

#: The six Environment & Provisioning concern rules (INFRASTRUCTURE-011 §3).
ENVIRONMENT_CONCERN_RULES: dict[str, str] = {
    "IENV-01": "Every environment declares exactly one isolation boundary and what it hosts.",
    "IENV-02": "Cross-environment hosting requires a declared, typed reference.",
    "IENV-03": "Node/cluster/environment containment is acyclic and uses ENG-005 references.",
    "IENV-04": "Provisioning binds RL-F2 workflow/state by reference; no runtime concern "
    "redefined; no new lifecycle model; PLATFORM-012/013 not re-founded.",
    "IENV-05": "The provisioning lifecycle is an evaluative architecture concept; the *act* "
    "of provisioning is out of scope.",
    "IENV-06": "No IaC/cloud/orchestrator/vendor selected; no authority conferred.",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for concern 011
# ---------------------------------------------------------------------------

#: The Infrastructure laws the Environment & Provisioning constructs are directly
#: obligated by. The universal laws (UIL-01…05, UIL-15) plus the environment/containment/
#: provisioning laws: UIL-07 (every environment is bounded/cohesive/isolated and declares
#: its boundary — IENV-01/02, the Environment governing law), UIL-09 (containment reuses
#: ENG-005 references and is founding-acyclic — IENV-03, the containment governing law),
#: UIL-10 (provisioning binds frozen RL-F2 by reference; re-founds no PLATFORM-012/013 —
#: IENV-04, the ProvisioningProcess governing law).
ENVIRONMENT_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-07",
    "UIL-09",
    "UIL-10",
    "UIL-15",
)

#: Laws scoped to Capability-reuse / Resource / Storage / Distribution / Scaling /
#: EvaluativeFacet units, N/A to the Environment & Provisioning constructs: UIL-06
#: (PL-F2/SF-2/AF-3 hosting/delivery — Capability/Distribution), UIL-08 (a Resource
#: declares capacity/locality — Resource units), UIL-11 (storage-hosting hosts DATA-010 —
#: Storage), UIL-12 (distribution/delivery transport — Distribution), UIL-13 (capacity
#: scaling unbounded — Scaling/Resource units), UIL-14 (security/governance evaluative
#: non-enforcing — EvaluativeFacet).
ENVIRONMENT_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",
    "UIL-08",
    "UIL-11",
    "UIL-12",
    "UIL-13",
    "UIL-14",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for concern 011
# ---------------------------------------------------------------------------

#: The WF rules the Environment & Provisioning constructs are directly subject to. **WF-4**
#: (*every Environment has exactly one boundary; cross-boundary hosts is a typed reference*),
#: **WF-3** (*the contains and dependsOn graphs are acyclic in founding structure*) and
#: **WF-6** (*every ProvisioningProcess binds an RL-F2 workflow; re-founds no PLATFORM-012/013*)
#: are the **governing, materially-exercised** rules for this unit — the three GATE 3
#: obligations (EC-3-B13-P01 §4.1). WF-5/7/8/9/10 are scoped to Resource/Storage/
#: Distribution/Scaling/EvaluativeFacet constructs and are recorded N/A with rationale.
ENVIRONMENT_APPLICABLE_WF: tuple[str, ...] = (
    "WF-1",
    "WF-2",
    "WF-3",
    "WF-4",
    "WF-6",
    "WF-11",
    "WF-12",
)

#: WF rules scoped to other leaf meta-classes, N/A to the Environment & Provisioning
#: constructs.
ENVIRONMENT_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-5",
    "WF-7",
    "WF-8",
    "WF-9",
    "WF-10",
)

__all__ = [
    "REALIZATION_UNIT",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "ENVIRONMENT_META_CLASSES",
    "HOSTING_STRUCTURE_META_CLASSES",
    "TRACE_TAIL",
    "SUBSTRATE_REFS",
    "CONSTRUCT_RELATIONSHIPS",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "ENVIRONMENT_APPLICABLE_LAWS",
    "ENVIRONMENT_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "ENVIRONMENT_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "ENVIRONMENT_APPLICABLE_WF",
    "ENVIRONMENT_INAPPLICABLE_WF",
    "CCE_GATES",
]
