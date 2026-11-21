"""EC3-B11-U10 — Security meta-model constants (read-only projections of SERVICE-001…014).

Carries, as executable constants, the fixed identifiers of the frozen Service Foundation
that the Universal **Security** realization (SMC-10) must conform to. It **defines no new
law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it only names the
frozen obligations so the realization can be checked deterministically.

Derived verbatim from the frozen ``11-SERVICE/`` specification at anchor ``b7e7657``:

* SMC-10 **Security** models ontology entity **SOE-10** — *"a decidable record classifying a
  service/operation's authentication / authorization / confidentiality / integrity concerns"*
  (SERVICE-003 §2; SERVICE-014 §3) — classified by hierarchy **SXH-10** (Authentication-Record /
  Authorization-Record / Confidentiality-Record / Integrity-Record; SERVICE-004 / SERVICE-014 §5).
* A Security object **classifies** the Service/Operation/Execution boundary that references it
  (SMR-09 classified-by; SOR-09; reference-only; SERVICE-014 §6), is **governed-by** — i.e. its
  classification is *informed by* — a declarative Policy (SMR-08 governed-by; SOR-08;
  reference-only), **behaves-as** the RUNTIME policy concern for its evaluation (SMR-11
  behaves-as; SOR-11; RUNTIME-010, by reference; §7), reuses DATA-014 data-security
  classifications for confidentiality/integrity over DATA via **operates-on** (SMR-13; SOR-13;
  DF-2, by reference; SSE-06), and is identified via **identified-by** (SMR-10; SOR-10; ENG-001
  via ENG-002).
* Security principles SSE-01…10 (SERVICE-014 §4) govern the construct; **USL-14** (security as a
  decidable evaluative facet) is THE governing law, grounded in USL-13 (non-enforcement) and
  USL-10 (evaluation reuses the RUNTIME policy concern by reference) and USL-11 (data by
  reference; DATA-014 reuse).
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

#: The Security meta-class id (SERVICE-005 §2).
SECURITY_META_CLASS = "SMC-10"

#: Backward traceability chain every realized Security object records (SERVICE-005 → root).
TRACE_BACKWARD_SECURITY: tuple[str, ...] = (
    "SMC-10",  # SERVICE-005 §2 — Security meta-class
    "SOE-10",  # SERVICE-003 §2 — Security ontology entity
    "SERVICE-014",  # Universal Service Security Architecture (concern architecture)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations a Security object reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (policy-evaluation behavior, SMR-11; RUNTIME-010/008) ·
#:   DF-2 (confidentiality/integrity data, SMR-13; DATA-014). A Security object does not compose
#:   (PL-F2 N/A — composition is the SMC-06 concern) nor coordinate (that is the SMC-07 concern);
#:   it is a decidable, evaluative classification facet (USL-14).
SECURITY_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (structural value fidelity)
    "ENG-004",  # Type      (typed security object, USL-03 / SSE-01)
    "ENG-005",  # Relationship/Reference (classified-by/governed-by/behaves-as/operates-on refs)
    "RL-F2",  # Runtime policy/event (behaves-as, SMR-11; RUNTIME-010 evaluate / RUNTIME-008 record)
    "DF-2",  # Represented data (confidentiality/integrity data, SMR-13; DATA-014, by reference)
)

#: The DATA-security architecture a Security object reuses by reference for confidentiality/
#: integrity classifications over operation data (SERVICE-014 §7 data-security-reuse; SSE-06).
DATA_SECURITY_CONCERN = "DATA-014"

#: The meta-relationships a Security object intrinsically participates in (SERVICE-014 §6;
#: all within SMR-01…13):
#:   SMR-08 governed-by   (Security classification informed-by → Policy — reference-only; SOR-08)
#:   SMR-09 classified-by (Service/Operation/Execution → Security — reference-only; SOR-09)
#:   SMR-10 identified-by (ENG-001 via ENG-002; SOR-10)
#:   SMR-11 behaves-as    (Security evaluation → RUNTIME policy RUNTIME-010; SOR-11)
#:   SMR-13 operates-on   (confidentiality/integrity data → DATA DF-2/DATA-014, by ref; SOR-13)
SECURITY_RELATIONSHIPS: tuple[str, ...] = (
    "SMR-08",
    "SMR-09",
    "SMR-10",
    "SMR-11",
    "SMR-13",
)


class SecurityKind(str, Enum):
    """SXH-10 Security Hierarchy (SERVICE-004 / SERVICE-014 §5) — single-facet (SXC-02).

    Membership is decidable and single-facet; each kind is a distinct family of decidable,
    evaluative, non-enforcing classification (SSE-03 / USL-14):

    * ``AUTHENTICATION`` — an identity-assertion classification (issues no credential — SSE-C1).
    * ``AUTHORIZATION``  — an access classification (grants nothing — SSE-C1/C2).
    * ``CONFIDENTIALITY``— a confidentiality classification (selects no crypto; reuses DATA-014).
    * ``INTEGRITY``      — an integrity classification (selects no control technology; DATA-014).

    Every kind evaluates via the RUNTIME policy concern (RUNTIME-010) by reference (§7): the
    distinction between kinds is *what protection concern* is classified, not *how* it is enacted
    — no kind grants access, issues a credential, or encrypts anything (SSE-C1…C5).
    """

    AUTHENTICATION = "Authentication-Record"  # identity-assertion classification (no credential)
    AUTHORIZATION = "Authorization-Record"  # access classification (grants nothing)
    CONFIDENTIALITY = "Confidentiality-Record"  # confidentiality classification (no crypto)
    INTEGRITY = "Integrity-Record"  # integrity classification (no control technology)


#: The RUNTIME concern every security kind reuses by reference for evaluation
#: (SERVICE-014 §7 security-classify). A Security object re-founds no runtime concern; its
#: evaluation references RUNTIME-010 (policy) via RL-F2 (SMR-11 behaves-as) — declarative,
#: evaluative, and non-enforcing (SSE-03 / USL-14).
KIND_RUNTIME_CONCERN: dict[SecurityKind, str] = {
    SecurityKind.AUTHENTICATION: "RUNTIME-010",  # policy — declarative authentication classify
    SecurityKind.AUTHORIZATION: "RUNTIME-010",  # policy — declarative authorization classify
    SecurityKind.CONFIDENTIALITY: "RUNTIME-010",  # policy — declarative confidentiality classify
    SecurityKind.INTEGRITY: "RUNTIME-010",  # policy — declarative integrity classify
}

#: The abstract RUNTIME behavior binding suffix per kind (§7 security-classify — RUNTIME-010).
KIND_BEHAVIOR_SUFFIX: dict[SecurityKind, str] = {
    SecurityKind.AUTHENTICATION: "evaluate",  # §7 security-classify (RUNTIME-010)
    SecurityKind.AUTHORIZATION: "evaluate",
    SecurityKind.CONFIDENTIALITY: "evaluate",
    SecurityKind.INTEGRITY: "evaluate",
}

#: The RUNTIME event concern a Security object reuses by reference to record an evaluation
#: (SERVICE-014 §7 security-record / SOV-09). Referenced, never redefined.
RUNTIME_EVENT_CONCERN = "RUNTIME-008"

#: The security kinds whose classification reuses DATA-014 data-security classifications over the
#: operation's DF-2 data by reference (SERVICE-014 §7 data-security-reuse; SSE-06 / SSE-C3).
DATA_BEARING_KINDS: frozenset[SecurityKind] = frozenset(
    {SecurityKind.CONFIDENTIALITY, SecurityKind.INTEGRITY}
)

#: Deterministic evaluation-precedence rank per security kind, grounded in the SXH-10
#: declaration order (SERVICE-014 §5: Authentication → Authorization → Confidentiality →
#: Integrity). A *lower* rank is evaluated first. This is a decidable, evaluative ordering only
#: (SSE-03 / USL-14): it enacts nothing, grants nothing, and blocks nothing — it merely records
#: the deterministic order in which classification facets are considered. No business rule is
#: invented; the order is the frozen taxonomy order (SSE-08 / USL-15).
KIND_PRECEDENCE: dict[SecurityKind, int] = {
    SecurityKind.AUTHENTICATION: 0,  # evaluated first (SXH-10 declaration order)
    SecurityKind.AUTHORIZATION: 1,
    SecurityKind.CONFIDENTIALITY: 2,
    SecurityKind.INTEGRITY: 3,
}

#: Security principles SSE-01…10 (SERVICE-014 §4), each mapped to its short statement.
SECURITY_PRINCIPLES: dict[str, str] = {
    "SSE-01": "Security Typedness — classified by an ENG-004 Type.",
    "SSE-02": "Security Identity — an ENG-002 Object bearing an ENG-001 identity.",
    "SSE-03": "Evaluative-Only — classifies/measures; enacts no enforcement, grants no access.",
    "SSE-04": "No Technology Selection — selects no cryptography/IAM/key-management/protocol.",
    "SSE-05": "No Secret — embeds no secret, key, or credential (RR-07).",
    "SSE-06": "Data-Security Reuse — confidentiality/integrity reuse DATA-014 by reference.",
    "SSE-07": "Boundary Classification — classifies service/operation/execution (SOR-09).",
    "SSE-08": "Additive Growth — new classifications append additively (SXH-10).",
    "SSE-09": "Non-Constitutiveness — confers no authority and no standing.",
    "SSE-10": "Reuse Labelling — consumed source assets are labelled INPUT, never COMPLETION.",
}

#: The Service laws a Security construct is directly obligated by (per Stage-1 discovery).
#: USL-14 (security as evaluative facet) is THE governing law; USL-13 (non-enforcement),
#: USL-10 (evaluation reuses RUNTIME by reference, §7), and USL-11 (confidentiality/integrity
#: data by reference; DATA-014 reuse, SSE-06) are grounded here too. USL-06 (contract) is scoped
#: to the Contract unit (SMC-03), USL-07 (interface typedness) to the Interface unit (SMC-04),
#: USL-08 (operation I/O) to the Operation unit (SMC-05), and USL-09 (composition) to the
#: Composition/Orchestration units (SMC-06/07); all four recorded N/A.
SECURITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-10",
    "USL-11",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to other concern units, N/A to the Security object.
SECURITY_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-06", "USL-07", "USL-08", "USL-09")

#: Meta-constraints a Security object is bound by (SERVICE-005 §4 / SERVICE-014 §10 SSE-K1…K5).
#:   SMK-01 typed/identified/object · SMK-02 classifies a declared boundary · SMK-03 founding
#:   (classified-by/behaves-as) acyclic · SMK-05 runtime reference resolves · SMK-07 data
#:   reference resolves + evaluative/non-enforcing · SMK-08 no technology / no authority.
SECURITY_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002). [SSE-K1]",
    "SMK-02": "Classifies a declared boundary (service/operation/execution) (SMR-09). [SSE-K2]",
    "SMK-03": "The founding graph (classified-by / behaves-as) is acyclic. [SMI-04]",
    "SMK-05": "Every runtime/evaluation reference resolves to an RL-F2 construct; none "
    "redefined. [SSE-K4]",
    "SMK-07": "Every data reference resolves to a DF-2/DATA-014 construct; security is "
    "evaluative and non-enforcing; none redefined. [SSE-K3/K4]",
    "SMK-08": "No security object selects technology, embeds a secret, or confers "
    "authority. [SSE-K5]",
}

#: Meta-constraints scoped to other concern units, N/A to the Security object.
#:   SMK-04 (exposed-through-interface) is scoped to the Operation unit (SMC-05); SMK-06
#:   (platform composition reference) is scoped to Composition (SMC-06) — a Security object binds
#:   RUNTIME by reference (SMR-11), not PLATFORM composition (SMR-12).
SECURITY_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-04", "SMK-06")

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Security → SMC-10).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01/02/03/05/07/08).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "SECURITY_META_CLASS",
    "TRACE_BACKWARD_SECURITY",
    "SECURITY_SUBSTRATE_REFS",
    "DATA_SECURITY_CONCERN",
    "SECURITY_RELATIONSHIPS",
    "SecurityKind",
    "KIND_RUNTIME_CONCERN",
    "KIND_BEHAVIOR_SUFFIX",
    "RUNTIME_EVENT_CONCERN",
    "DATA_BEARING_KINDS",
    "KIND_PRECEDENCE",
    "SECURITY_PRINCIPLES",
    "SECURITY_APPLICABLE_LAWS",
    "SECURITY_INAPPLICABLE_LAWS",
    "SECURITY_META_CONSTRAINTS",
    "SECURITY_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]
