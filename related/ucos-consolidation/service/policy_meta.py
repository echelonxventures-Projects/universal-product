"""EC3-B11-U09 — Policy meta-model constants (read-only projections of SERVICE-001…013).

Carries, as executable constants, the fixed identifiers of the frozen Service Foundation
that the Universal **Policy** realization (SMC-09) must conform to. It **defines no new
law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it only names the
frozen obligations so the realization can be checked deterministically.

Derived verbatim from the frozen ``11-SERVICE/`` specification at anchor ``b7e7657``:

* SMC-09 **Policy** models ontology entity **SOE-09** — *"a declarative, decidable,
  non-enforcing governing rule applied at a contract/operation boundary — a predicate over
  service constructs that is evaluated to produce a judgment, never a mechanism that enacts a
  decision"* (SERVICE-003 §2; SERVICE-013 §3) — classified by hierarchy **SXH-09**
  (Authorization / Validation / Quota-SLA; SERVICE-004 / SERVICE-013 §5).
* A Policy is **bound-by** a Contract that declares it applicable (SMR-02 bound-by; SOR-02;
  reference-only; SERVICE-013 §6), **governs** Services/Operations/Executions that reference it
  via governed-by (SMR-08 governed-by; SOR-08; reference-only), **behaves-as** the RUNTIME
  policy concern for its evaluation (SMR-11 behaves-as; SOR-11; RUNTIME-010, by reference;
  §7 / SPL-05), carries the DF-2-represented data its predicate operates over via
  **operates-on** (SMR-13; SOR-13; by reference; SPL-C4), and is identified via
  **identified-by** (SMR-10; SOR-10; ENG-001 via ENG-002).
* Policy principles SPL-01…10 (SERVICE-013 §4) govern the construct; **USL-13** (policy as
  declarative constraint) is THE governing law, grounded in USL-06 (boundary binding) and
  USL-10 (evaluation reuses the RUNTIME policy concern by reference).
"""

from __future__ import annotations

from enum import Enum

from service.service_meta import (
    CONSTITUTIONAL_ANCHOR,
    LIFECYCLE_ORDER,
    META_RELATIONSHIPS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

# Re-export the frozen sets (single source of truth — no duplication).
__all_reexport__ = (
    CONSTITUTIONAL_ANCHOR,
    LIFECYCLE_ORDER,
    META_RELATIONSHIPS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

#: The Policy meta-class id (SERVICE-005 §2).
POLICY_META_CLASS = "SMC-09"

#: Backward traceability chain every realized Policy records (SERVICE-005 → root).
TRACE_BACKWARD_POLICY: tuple[str, ...] = (
    "SMC-09",  # SERVICE-005 §2 — Policy meta-class
    "SOE-09",  # SERVICE-003 §2 — Policy ontology entity
    "SERVICE-013",  # Universal Service Policy Architecture (concern architecture)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations a Policy reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (policy-evaluation behavior, SMR-11; RUNTIME-010/008) ·
#:   DF-2 (predicate data, SMR-13). A Policy does not compose (PL-F2 N/A — composition is the
#:   SMC-06 concern) nor coordinate (that is the SMC-07 concern); it is declarative.
POLICY_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (structural value fidelity)
    "ENG-004",  # Type      (typed policy, USL-03 / SPL-01)
    "ENG-005",  # Relationship/Reference (bound-by/governed-by/behaves-as/operates-on refs)
    "RL-F2",  # Runtime policy/event (behaves-as, SMR-11; RUNTIME-010 evaluate / RUNTIME-008 record)
    "DF-2",  # Represented data (predicate data, SMR-13; by reference)
)

#: The meta-relationships a Policy intrinsically participates in (SERVICE-013 §6;
#: all within SMR-01…13):
#:   SMR-02 bound-by      (Policy → Contract that declares it applicable — reference-only; SOR-02)
#:   SMR-08 governed-by   (Service/Operation/Execution → Policy — reference-only; SOR-08)
#:   SMR-10 identified-by (ENG-001 via ENG-002; SOR-10)
#:   SMR-11 behaves-as    (Policy evaluation → RUNTIME policy RUNTIME-010; SOR-11)
#:   SMR-13 operates-on   (predicate data → DATA DF-2, by reference; SOR-13)
POLICY_RELATIONSHIPS: tuple[str, ...] = (
    "SMR-02",
    "SMR-08",
    "SMR-10",
    "SMR-11",
    "SMR-13",
)


class PolicyKind(str, Enum):
    """SXH-09 Policy Hierarchy (SERVICE-004 / SERVICE-013 §5) — single-facet (SXC-02).

    Membership is decidable and single-facet; each kind is a distinct family of declarative,
    non-enforcing constraint (SPL-03/04):

    * ``AUTHORIZATION`` — a declarative access constraint (evaluative; grants nothing — SPL-C2).
    * ``VALIDATION``    — a declarative input/output/contract constraint.
    * ``QUOTA_SLA``     — a declarative rate/quality constraint (measures, does not enforce).

    Every kind evaluates via the RUNTIME policy concern (RUNTIME-010) by reference (SPL-05 / §7):
    the distinction between kinds is *what* is constrained, not *how* it is carried out.
    """

    AUTHORIZATION = "Authorization-Policy"  # declarative access constraint (grants nothing)
    VALIDATION = "Validation-Policy"  # declarative input/output/contract constraint
    QUOTA_SLA = "Quota-SLA-Policy"  # declarative rate/quality constraint (measures only)


#: The RUNTIME concern every policy kind reuses by reference for evaluation
#: (SERVICE-013 §7 / SPL-05). A Policy re-founds no runtime concern; its evaluation references
#: RUNTIME-010 (policy) via RL-F2 (SMR-11 behaves-as) — declarative and non-enforcing.
KIND_RUNTIME_CONCERN: dict[PolicyKind, str] = {
    PolicyKind.AUTHORIZATION: "RUNTIME-010",  # policy — declarative access evaluation
    PolicyKind.VALIDATION: "RUNTIME-010",  # policy — declarative validation evaluation
    PolicyKind.QUOTA_SLA: "RUNTIME-010",  # policy — declarative quota/SLA evaluation
}

#: The abstract RUNTIME behavior binding suffix per kind (§7 policy-evaluate — RUNTIME-010).
KIND_BEHAVIOR_SUFFIX: dict[PolicyKind, str] = {
    PolicyKind.AUTHORIZATION: "evaluate",  # §7 policy-evaluate (RUNTIME-010)
    PolicyKind.VALIDATION: "evaluate",  # §7 policy-evaluate (RUNTIME-010)
    PolicyKind.QUOTA_SLA: "evaluate",  # §7 policy-evaluate (RUNTIME-010)
}

#: The RUNTIME event concern a policy reuses by reference to record an evaluation judgment
#: (SERVICE-013 §7 policy-record / SPL-C1 / SOV-09). Referenced, never redefined.
RUNTIME_EVENT_CONCERN = "RUNTIME-008"

#: Deterministic evaluation-precedence rank per policy kind, grounded in the SXH-09
#: declaration order (SERVICE-013 §5: Authorization → Validation → Quota-SLA). A *lower* rank is
#: evaluated first. This is a decidable, evaluative ordering only (SPL-03/04): it enacts nothing,
#: grants nothing, and blocks nothing — it merely records the deterministic order in which
#: declarative predicates are considered. No business rule is invented; the order is the frozen
#: taxonomy order (USL-13/15).
KIND_PRECEDENCE: dict[PolicyKind, int] = {
    PolicyKind.AUTHORIZATION: 0,  # evaluated first (SXH-09 declaration order)
    PolicyKind.VALIDATION: 1,
    PolicyKind.QUOTA_SLA: 2,
}

#: Policy principles SPL-01…10 (SERVICE-013 §4), each mapped to its short statement.
POLICY_PRINCIPLES: dict[str, str] = {
    "SPL-01": "Policy Typedness — classified by an ENG-004 Type.",
    "SPL-02": "Policy Identity — an ENG-002 Object bearing an ENG-001 identity.",
    "SPL-03": "Declarativeness — a declarative, decidable predicate over service constructs.",
    "SPL-04": "Non-Enforcement — evaluation records a judgment; enacts/grants/blocks nothing.",
    "SPL-05": "Runtime Reuse — reuses the RUNTIME policy concern (RUNTIME-010) by reference.",
    "SPL-06": "Boundary Binding — binds to a contract/operation/execution boundary (SOR-08).",
    "SPL-07": "No Authority — confers, delegates, and enacts no authority.",
    "SPL-08": "Additive Growth — new policy kinds append additively (SXH-09).",
    "SPL-09": "Non-Constitutiveness — embeds no secret, selects no technology, confers nothing.",
    "SPL-10": "Reuse Labelling — consumed source assets are labelled INPUT, never COMPLETION.",
}

#: The Service laws a Policy construct is directly obligated by (per Stage-1 discovery).
#: USL-13 (policy as declarative constraint) is THE governing law; USL-06 (boundary binding,
#: SPL-06) and USL-10 (evaluation reuses RUNTIME by reference, SPL-05) and USL-11 (data by
#: reference, SPL-C4) are grounded here too. USL-07 (interface typedness) is scoped to the
#: Interface unit (SMC-04), USL-08 (operation I/O) to the Operation unit (SMC-05), and USL-09
#: (composition) to the Composition/Orchestration units (SMC-06/07); all three recorded N/A.
POLICY_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-06",
    "USL-10",
    "USL-11",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to other concern units, N/A to the Policy.
POLICY_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-07", "USL-08", "USL-09")

#: Meta-constraints a Policy is bound by (SERVICE-005 §4 / SERVICE-013 §10 SPL-K1…K5).
#:   SMK-01 typed/identified/object · SMK-02 binds to a declared boundary · SMK-03 founding
#:   (bound-by/behaves-as) acyclic · SMK-05 runtime reference resolves · SMK-07 data reference
#:   resolves + declarative/non-enforcing · SMK-08 no technology / no authority.
POLICY_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002). [SPL-K1]",
    "SMK-02": "Binds to a declared boundary (contract/operation/execution) (SMR-02). [SPL-K2]",
    "SMK-03": "The founding graph (bound-by / behaves-as) is acyclic. [SMI-04]",
    "SMK-05": "Every runtime/evaluation reference resolves to an RL-F2 construct; none "
    "redefined. [SPL-K4]",
    "SMK-07": "Every data reference resolves to a DF-2 construct; policy is declarative and "
    "non-enforcing; none redefined. [SPL-K3/K4]",
    "SMK-08": "No policy selects technology or confers authority. [SPL-K5]",
}

#: Meta-constraints scoped to other concern units, N/A to the Policy.
#:   SMK-04 (exposed-through-interface) is scoped to the Operation unit (SMC-05); SMK-06
#:   (platform composition reference) is scoped to Composition (SMC-06) — a Policy binds RUNTIME
#:   by reference (SMR-11), not PLATFORM composition (SMR-12).
POLICY_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-04", "SMK-06")

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Policy → SMC-09).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01/02/03/05/07/08).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "POLICY_META_CLASS",
    "TRACE_BACKWARD_POLICY",
    "POLICY_SUBSTRATE_REFS",
    "POLICY_RELATIONSHIPS",
    "PolicyKind",
    "KIND_RUNTIME_CONCERN",
    "KIND_BEHAVIOR_SUFFIX",
    "RUNTIME_EVENT_CONCERN",
    "KIND_PRECEDENCE",
    "POLICY_PRINCIPLES",
    "POLICY_APPLICABLE_LAWS",
    "POLICY_INAPPLICABLE_LAWS",
    "POLICY_META_CONSTRAINTS",
    "POLICY_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]
