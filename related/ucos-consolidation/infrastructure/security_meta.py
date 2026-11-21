"""EC3-B13-U08 — Infrastructure Security meta-model constants (identity / ownership / lifecycle).

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003 (Ontology),
INFRASTRUCTURE-005 (Meta-Model / UIMM), and INFRASTRUCTURE-013 (Universal Infrastructure
Security concern architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Security realization must conform to. It **defines no new
law and redefines no foundation concept** (UIL-02 / UIL-15); it only names the frozen
obligations so the realization can be checked against them deterministically. The shared
Infrastructure vocabulary (lifecycle states, admitted relationships, the fifteen
Infrastructure Laws, the twelve well-formedness rules, the seven compliance conditions, and
the CCE gate ids) is **imported by reference** from the first Band-13 unit
(:mod:`infrastructure.capability_meta`) and never redefined.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification at
the constitutional anchor ``b7e7657``:

* The **one** leaf meta-class concern 013 instantiates (INFRASTRUCTURE-005 §2;
  INFRASTRUCTURE-013 §2/§4): **SecurityFacet** — *"the evaluative, non-enforcing
  classification of isolation, authentication, authorization, confidentiality, and
  integrity as they pertain to the hosting substrate"*.
* The **five** evaluative facets that realize it (INFRASTRUCTURE-013 §2): **Isolation,
  Authentication, Authorization, Confidentiality, Integrity** — each reuses a frozen lower
  security concern **by reference** (ISEC-02) and evaluates an ENG-002 object.
* Its concern rules ISEC-01…06 (INFRASTRUCTURE-013 §3) and the well-formedness / law /
  compliance obligations each construct is validated against (INFRASTRUCTURE-005 §5;
  INFRASTRUCTURE-001 §7/§12).

This unit is a **single-meta-class** concern (WF-1): every construct instantiates exactly
one leaf meta-class (SecurityFacet) and is an **EvaluativeFacet** — evaluative and
NON-ENFORCING (WF-10 / UIL-14 / ISEC-01/04). It materially exercises **C4** (evaluative,
non-enforcing) and **C7** (no technology/authority/secret — UIL-15 / ISEC-03/05/06).
"""

from __future__ import annotations

from enum import Enum

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

#: The realization unit this module set realizes (EC-3 Band 13, Unit 08).
REALIZATION_UNIT = "EC3-B13-U08"

#: The single Infrastructure leaf meta-class realized by this unit (INFRASTRUCTURE-005 §2).
#: Every construct instantiates exactly this one meta-class (WF-1).
SECURITY_META_CLASS = "SecurityFacet"

#: The shared id-family prefix every Security facet construct id begins with (ENG-001).
INFRA_SECURITY_ID_FAMILY = "UCOS-INFRA-"

#: The deterministic id prefix for a realized Security facet construct.
INFRA_SECURITY_ID_PREFIX = "UCOS-INFRA-SECURITY"

# ===========================================================================
# Ownership (CEP-002 single-owner) — non-constitutive (UIL-15 / ISEC-06)
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
#: Band-11 service FROZEN + Band-12 application FROZEN + Band-13 U01…U07 CERTIFIED).
IMPLEMENTATION_ANCHOR = "990336f"

#: The single Infrastructure leaf meta-class id realized by this unit (INFRASTRUCTURE-005
#: §2 — concern 013's meta-class). Every construct instantiates exactly this one (WF-1).
SECURITY_META_CLASSES: tuple[str, ...] = ("SecurityFacet",)

#: The five evaluative facets concern 013 realizes over the SecurityFacet meta-class
#: (INFRASTRUCTURE-013 §2). Each is a decidable, non-enforcing evaluative classification.
SECURITY_FACET_KINDS: tuple[str, ...] = (
    "isolation",
    "authentication",
    "authorization",
    "confidentiality",
    "integrity",
)

#: Each facet's frozen lower-security concern reused **by reference** (ISEC-02;
#: INFRASTRUCTURE-013 §2). Never re-founded — reference-only.
SECURITY_FACET_REUSE: dict[str, str] = {
    "isolation": "IsolationBoundary (INFRASTRUCTURE-011) — realized by U05, by reference",
    "authentication": "RL-F2 policy (RUNTIME-GOV-003) — referenced, never enforced (UIL-14)",
    "authorization": "RL-F2 policy + APPLICATION-013 — by reference",
    "confidentiality": "DATA-014 — by reference",
    "integrity": "DATA-014 + SERVICE-014 — by reference",
}

#: The backward-lineage tail every realized construct records after its meta-class root.
TRACE_TAIL: tuple[str, ...] = (
    "INFRASTRUCTURE-013",  # Universal Infrastructure Security Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Security facets reuse by reference (UIL-02): ENG-001…005
#: (EL-1) · RL-F2 (policy concern — referenced, never enforced) · the frozen lower-layer
#: security concerns DATA-014 / SERVICE-014 / APPLICATION-013 · IsolationBoundary (011).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",        # Identity (identified-by)
    "ENG-002",        # Object (evaluates an ENG-002 object)
    "ENG-003",        # Value (value fidelity)
    "ENG-004",        # Type (typed construct, UIL-03)
    "ENG-005",        # Relationship/Reference (evaluates/reuse refs)
    "RL-F2",          # Runtime policy referenced by reference (UIL-14; never enforced)
    "IsolationBoundary",  # INFRASTRUCTURE-011 (U05) reused by reference (Isolation facet)
    "DATA-014",       # Data security classification reused by reference
    "SERVICE-014",    # Service security classification reused by reference
    "APPLICATION-013",  # Application security classification reused by reference
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §4 — meta-relationships each construct participates in
# ---------------------------------------------------------------------------

#: The admitted meta-relationships a SecurityFacet participates in as a domain
#: (INFRASTRUCTURE-005 §4). A facet ``evaluates`` an ENG-002 object (non-founding) and may
#: ``dependsOn`` other constructs (reference-only). It is the domain of no founding edge —
#: EvaluativeFacets are vacuously acyclic (WF-3).
CONSTRUCT_RELATIONSHIPS: dict[str, tuple[str, ...]] = {
    "SecurityFacet": ("evaluates", "dependsOn"),
}

#: The admitted evaluative verdict vocabulary (non-projecting — ISEC-06). A verdict
#: records a decidable evaluation; it asserts no operational security readiness.
ADMITTED_VERDICTS: tuple[str, ...] = (
    "unassessed",
    "indeterminate",
    "conformant",
    "nonconformant",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-013 §3 — concern rules (ISEC-01…06)
# ---------------------------------------------------------------------------

#: The six Infrastructure Security concern rules (INFRASTRUCTURE-013 §3).
SECURITY_CONCERN_RULES: dict[str, str] = {
    "ISEC-01": "Every security facet is evaluative and non-enforcing; records verdicts against ENG-002 objects.",
    "ISEC-02": "Security facets reuse DATA-014/SERVICE-014/APPLICATION-013 by reference; none is re-founded.",
    "ISEC-03": "No secret/credential/key/cryptographic material is embedded (RR-07).",
    "ISEC-04": "No enforcement is enacted; no access is granted; no credential is issued.",
    "ISEC-05": "No IAM/PKI/crypto technology/vendor selected.",
    "ISEC-06": "Confers no authority; projects no operational security readiness.",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for concern 013
# ---------------------------------------------------------------------------

#: The Infrastructure laws the Security facets are directly obligated by. Universal laws
#: (UIL-01…05, UIL-15) + UIL-14 (security/governance evaluative, non-enforcing — ISEC-01/04)
#: + UIL-07 (isolation boundaries — Isolation facet).
SECURITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-07",
    "UIL-14",
    "UIL-15",
)

#: Laws scoped to Capability/Resource/Environment/Topology/Storage/Distribution/Provisioning
#: /Scaling units, N/A to the Security facets.
SECURITY_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",
    "UIL-08",
    "UIL-09",
    "UIL-10",
    "UIL-11",
    "UIL-12",
    "UIL-13",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for concern 013
# ---------------------------------------------------------------------------

#: The WF rules the Security facets are directly subject to. WF-10 (every EvaluativeFacet
#: has nonEnforcing=true — THE governing rule for this concern) + WF-1/2/3/11/12.
SECURITY_APPLICABLE_WF: tuple[str, ...] = (
    "WF-1",
    "WF-2",
    "WF-3",
    "WF-10",
    "WF-11",
    "WF-12",
)

#: WF rules scoped to other leaf meta-classes, N/A to the Security facets.
SECURITY_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-5",
    "WF-6",
    "WF-7",
    "WF-8",
    "WF-9",
)

__all__ = [
    "REALIZATION_UNIT",
    "SECURITY_META_CLASS",
    "INFRA_SECURITY_ID_FAMILY",
    "INFRA_SECURITY_ID_PREFIX",
    "OWNER",
    "AUTHORITY",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "SECURITY_META_CLASSES",
    "SECURITY_FACET_KINDS",
    "SECURITY_FACET_REUSE",
    "TRACE_TAIL",
    "SUBSTRATE_REFS",
    "CONSTRUCT_RELATIONSHIPS",
    "ADMITTED_VERDICTS",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "SECURITY_APPLICABLE_LAWS",
    "SECURITY_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "SECURITY_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "SECURITY_APPLICABLE_WF",
    "SECURITY_INAPPLICABLE_WF",
    "CCE_GATES",
]
