"""EC3-B13-U09 — Infrastructure Governance meta-model constants (identity / ownership / lifecycle).

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003 (Ontology),
INFRASTRUCTURE-005 (Meta-Model / UIMM), and INFRASTRUCTURE-014 (Universal Infrastructure
Governance concern architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Governance realization must conform to. It **defines no
new law and redefines no foundation concept** (UIL-02 / UIL-15); it only names the frozen
obligations so the realization can be checked against them deterministically. The shared
Infrastructure vocabulary (lifecycle states, admitted relationships, the fifteen
Infrastructure Laws, the twelve well-formedness rules, the seven compliance conditions, and
the CCE gate ids) is **imported by reference** from the first Band-13 unit
(:mod:`infrastructure.capability_meta`) and never redefined.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification at
the constitutional anchor ``b7e7657``:

* The **one** leaf meta-class concern 014 instantiates (INFRASTRUCTURE-005 §2;
  INFRASTRUCTURE-014 §2/§4): **GovernanceFacet** — *"the record-only, non-enforcing
  architecture of conformance, lifecycle, and policy as evaluative facets over the hosting
  substrate"*.
* The **five** constructs that realize it (INFRASTRUCTURE-014 §2): **Conformance Facet,
  Lifecycle Facet, Policy Facet, Gap Report, Change Record** — each reuses a frozen lower
  concern **by reference** (IGOV-05) and evaluates an ENG-002 object.
* Its concern rules IGOV-01…06 (INFRASTRUCTURE-014 §3) and the well-formedness / law /
  compliance obligations each construct is validated against (INFRASTRUCTURE-005 §5;
  INFRASTRUCTURE-001 §7/§12).

This unit is a **single-meta-class** concern (WF-1): every construct instantiates exactly
one leaf meta-class (GovernanceFacet) and is an **EvaluativeFacet** — record-only and
NON-ENFORCING (WF-10 / UIL-14 / IGOV-01). It materially exercises **C4** (evaluative,
non-enforcing) and **C7** (no technology/authority/secret — UIL-15 / IGOV-04/06).
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

# ===========================================================================
# Identity binding (ENG-001 / WF-1)
# ===========================================================================

#: The realization unit this module set realizes (EC-3 Band 13, Unit 09).
REALIZATION_UNIT = "EC3-B13-U09"

#: The single Infrastructure leaf meta-class realized by this unit (INFRASTRUCTURE-005 §2).
#: Every construct instantiates exactly this one meta-class (WF-1).
GOVERNANCE_META_CLASS = "GovernanceFacet"

#: The shared id-family prefix every Governance construct id begins with (ENG-001).
INFRA_GOVERNANCE_ID_FAMILY = "UCOS-INFRA-"

#: The deterministic id prefix for a realized Governance construct.
INFRA_GOVERNANCE_ID_PREFIX = "UCOS-INFRA-GOVERNANCE"

# ===========================================================================
# Ownership (CEP-002 single-owner) — non-constitutive (UIL-15 / IGOV-04)
# ===========================================================================

#: The single owner of this realization unit (CEP-002 single-owner rule).
OWNER = "EC-3 execution (AP-1)"

#: The authority this unit holds — engineering execution only; confers nothing (AUTH-06).
AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

# ===========================================================================
# Lifecycle metadata (INFRASTRUCTURE-003 §3) — forward-only
# ===========================================================================
# Re-exported by reference (never redefined): InfrastructureState, LIFECYCLE_ORDER.

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Implementation substrate anchor: the certified/frozen baseline this unit builds upon
#: (EC-1 engine CERTIFIED + EC-2 platform FROZEN + Band-10 data CERTIFIED-COMPLETE +
#: Band-11 service FROZEN + Band-12 application FROZEN + Band-13 U01…U07 CERTIFIED +
#: U08 Security CERTIFIED & PROVISIONALLY RATIFIED; U09 admitted at S4-07/UCOS-CEP-000031).
IMPLEMENTATION_ANCHOR = "78cbfc8"

#: The single Infrastructure leaf meta-class id realized by this unit (INFRASTRUCTURE-005
#: §2 — concern 014's meta-class). Every construct instantiates exactly this one (WF-1).
GOVERNANCE_META_CLASSES: tuple[str, ...] = ("GovernanceFacet",)

#: The five constructs concern 014 realizes over the GovernanceFacet meta-class
#: (INFRASTRUCTURE-014 §2). Each is a decidable, record-only, non-enforcing evaluative
#: classification/record.
GOVERNANCE_FACET_KINDS: tuple[str, ...] = (
    "conformance",
    "lifecycle",
    "policy",
    "gap_report",
    "change_record",
)

#: Each construct's frozen lower concern reused **by reference** (IGOV-05;
#: INFRASTRUCTURE-014 §2). Never re-founded — reference-only.
GOVERNANCE_FACET_REUSE: dict[str, str] = {
    "conformance": "UIMM-CONF (INFRASTRUCTURE-005) — evaluative conformance basis, by reference",
    "lifecycle": "UITX §3.3 — architectural lifecycle state basis, by reference",
    "policy": "RL-F2 policy (RUNTIME-GOV-003) — referenced, never enforced (UIL-14)",
    "gap_report": "ENG-000 custodian/Registrar — violation routing, by reference",
    "change_record": "UCI-001 + REG-AUTO-001 — additive/supersession change, by reference",
}

#: The backward-lineage tail every realized construct records after its meta-class root.
TRACE_TAIL: tuple[str, ...] = (
    "INFRASTRUCTURE-014",  # Universal Infrastructure Governance Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Governance constructs reuse by reference (UIL-02): ENG-001…005
#: (EL-1) · ENG-000 (custodian/Registrar) · RL-F2 (policy concern — referenced, never
#: enforced) · UIMM-CONF (conformance) · UITX (lifecycle) · UCI-001 (change) · REG-AUTO-001
#: (append-only registration).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",        # Identity (identified-by)
    "ENG-002",        # Object (evaluates an ENG-002 object)
    "ENG-003",        # Value (value fidelity)
    "ENG-004",        # Type (typed construct, UIL-03)
    "ENG-005",        # Relationship/Reference (evaluates/reuse refs)
    "ENG-000",        # Custodian/Registrar (governance recording substrate, by reference)
    "RL-F2",          # Runtime policy referenced by reference (UIL-14; never enforced)
    "UIMM-CONF",      # INFRASTRUCTURE-005 conformance basis reused by reference
    "UITX",           # Infrastructure transition/lifecycle basis reused by reference
    "UCI-001",        # Universal change instrument (additive/supersession) by reference
    "REG-AUTO-001",   # Append-only registration law by reference
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §4 — meta-relationships each construct participates in
# ---------------------------------------------------------------------------

#: The admitted meta-relationships a GovernanceFacet participates in as a domain
#: (INFRASTRUCTURE-005 §4). A construct ``evaluates`` an ENG-002 object (non-founding) and
#: may ``dependsOn`` other constructs (reference-only). It is the domain of no founding edge
#: — EvaluativeFacets are vacuously acyclic (WF-3).
CONSTRUCT_RELATIONSHIPS: dict[str, tuple[str, ...]] = {
    "GovernanceFacet": ("evaluates", "dependsOn"),
}

#: The admitted evaluative verdict vocabulary (non-projecting — IGOV-01/04). A verdict
#: records a decidable evaluation; it asserts no operational governance readiness and
#: enacts nothing.
ADMITTED_VERDICTS: tuple[str, ...] = (
    "unassessed",
    "indeterminate",
    "conformant",
    "nonconformant",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-014 §3 — concern rules (IGOV-01…06)
# ---------------------------------------------------------------------------

#: The six Infrastructure Governance concern rules (INFRASTRUCTURE-014 §3).
GOVERNANCE_CONCERN_RULES: dict[str, str] = {
    "IGOV-01": "Record-only and non-enforcing; enacts nothing (UIL-14; UIT-INV-10).",
    "IGOV-02": "Conformance decided against UIL-01…15 and UIMM-CONF, deterministically.",
    "IGOV-03": "Change is additive/supersession-only; nothing renumbered (UIL-15; UCI-001).",
    "IGOV-04": "Creates no operational/approval/enforcement/ratification authority (AUTH-06).",
    "IGOV-05": "Registration is append-only via the UKB build; native IDs kept (REG-AUTO-001).",
    "IGOV-06": "No policy engine/technology/vendor; projects no operational governance (§2).",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for concern 014
# ---------------------------------------------------------------------------

#: The Infrastructure laws the Governance constructs are directly obligated by. Universal
#: laws (UIL-01…05, UIL-15) + UIL-14 (security/governance evaluative, non-enforcing —
#: IGOV-01/04).
GOVERNANCE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-14",
    "UIL-15",
)

#: Laws scoped to Capability/Resource/Environment/Topology/Storage/Distribution/Provisioning
#: /Scaling/Isolation units, N/A to the Governance constructs.
GOVERNANCE_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",
    "UIL-07",
    "UIL-08",
    "UIL-09",
    "UIL-10",
    "UIL-11",
    "UIL-12",
    "UIL-13",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for concern 014
# ---------------------------------------------------------------------------

#: The WF rules the Governance constructs are directly subject to. WF-10 (every
#: EvaluativeFacet has nonEnforcing=true — THE governing rule for this concern) +
#: WF-1/2/3/11/12.
GOVERNANCE_APPLICABLE_WF: tuple[str, ...] = (
    "WF-1",
    "WF-2",
    "WF-3",
    "WF-10",
    "WF-11",
    "WF-12",
)

#: WF rules scoped to other leaf meta-classes, N/A to the Governance constructs.
GOVERNANCE_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-5",
    "WF-6",
    "WF-7",
    "WF-8",
    "WF-9",
)

__all__ = [
    "REALIZATION_UNIT",
    "GOVERNANCE_META_CLASS",
    "INFRA_GOVERNANCE_ID_FAMILY",
    "INFRA_GOVERNANCE_ID_PREFIX",
    "OWNER",
    "AUTHORITY",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "GOVERNANCE_META_CLASSES",
    "GOVERNANCE_FACET_KINDS",
    "GOVERNANCE_FACET_REUSE",
    "TRACE_TAIL",
    "SUBSTRATE_REFS",
    "CONSTRUCT_RELATIONSHIPS",
    "ADMITTED_VERDICTS",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "GOVERNANCE_APPLICABLE_LAWS",
    "GOVERNANCE_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "GOVERNANCE_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "GOVERNANCE_APPLICABLE_WF",
    "GOVERNANCE_INAPPLICABLE_WF",
    "CCE_GATES",
]
