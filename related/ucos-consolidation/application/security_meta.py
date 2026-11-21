"""EC3-B12-U09 — Security meta-model constants (read-only projections of
APPLICATION-001/003/004/005/013).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen Security Architecture
(APPLICATION-013, AMC-09 / UASecA) that the Universal Security realization must conform to.
It **defines no new law and redefines no foundation concept** (UAL-02 / AMI-05 / UAL-15); it
only names the frozen obligations so the realization can be checked against them
deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification at
the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.

* AMC-09 **Security** models ontology entity **AOE-09** — *"the evaluative, non-enforcing
  classification of an application/feature's authentication, authorization, confidentiality,
  and integrity concerns"* (APPLICATION-003 §2; APPLICATION-013 §3) — classified by hierarchy
  **AXH-09** (Authentication-Record / Authorization-Record / Confidentiality-Record /
  Integrity-Record; APPLICATION-004 / APPLICATION-013 §5).
* A Security record is the *target* of **secured-by** (AMR-08; AOR-08) — the boundary it
  classifies is **secured-by** this record (reference-only) — is **governed-by** a Governance
  security-policy record (AMR-09; AOR-09; reference-only), is **identified-by** ENG-001 via
  ENG-002 (AMR-10; AOR-10), and **presents-data** as DF-2/DATA-014 data (AMR-14; AOR-14).
* Its evaluation **behaves-as** the frozen RUNTIME policy concern (§7 security-evaluate,
  AOB-06) bound by reference; it records judgments via the RUNTIME event concern (§7
  security-record, AOV-09); it reuses DATA-014 / SERVICE-014 security classifications by
  reference (§7 security-reference).
* Security principles SEC-01…10 (APPLICATION-013 §4) govern the construct; **UAL-14**
  (application security/governance is declarative, evaluative, non-enforcing) is THE governing
  law, grounded in UAL-15 (non-constitutiveness), UAL-10 (evaluation reuses the RUNTIME policy
  concern by reference), and UAL-13 (confidentiality/integrity data by reference; DATA-014
  reuse).
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 09) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 09).
REALIZATION_UNIT = "EC3-B12-U09"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-AP-4 §5/§9)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 12-APPLICATION/ specification commit.
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the certified baseline this builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` CERTIFIED-COMPLETE + FROZEN + the CERTIFIED
#: Band-12 U01 Universal Application root ``application.application`` + U02 Universal
#: Capability ``application.capability`` + U03 Universal Module ``application.module`` +
#: U04 Universal Feature ``application.feature`` + U05 Universal Workflow
#: ``application.workflow`` + U06 Universal Interaction ``application.interaction`` + U07
#: Universal State ``application.state`` + U08 Universal Composition
#: ``application.composition`` at HEAD ``1aae24a``).
IMPLEMENTATION_ANCHOR = "1aae24a"

#: The backward traceability chain every realized Security record records
#: (APPLICATION-013 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-09",  # APPLICATION-005 §2 — Security meta-class
    "APPLICATION-013",  # Universal Application Security Architecture (UASecA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Security construct reuses **directly** by reference
#: (UAL-02 / AMI-05). A Security record is the evaluative protection facet: it reuses EL-1
#: (identity, value, typing, reference), RL-F2 (the RUNTIME policy concern its evaluation
#: behaves-as — §7 security-evaluate; and the RUNTIME event concern it records judgments
#: through — §7 security-record), and DF-2 (the confidentiality/integrity data it presents
#: by reference — AMR-14; DATA-014). It does **not** deliver a capability (AMR-01), consume
#: an SF-2 operation (AMR-13), group features (AMR-03), sequence features (AMR-04), engage a
#: feature (AMR-05), hold state (AMR-06), or assemble a PLATFORM composition (AMR-07/12) —
#: those are the Application / Capability / Module / Feature / Workflow / Interaction / State
#: / Composition concerns (AMC-01…08).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity; canonical core)
    "ENG-004",  # Type      (typed security record, UAL-03 / SEC-01)
    "ENG-005",  # Relationship/Reference (subject/governance/data/behavior refs)
    "RL-F2",  # Runtime policy/event (security-evaluate / security-record, §7, by reference)
    "DF-2",  # Represented data the record presents (presents-data AMR-14; DATA-014, by ref)
)

#: The prior CERTIFIED / frozen constructs the Security record reuses **by reference through
#: its relationships** (never redefined; reused only by reference — mission reuse list):
#:   AMC-01 (Application) — a boundary secured-by this record (AMR-08; the classified subject).
#:   AMC-04 (Feature)     — a boundary secured-by this record (AMR-08; the classified subject).
#:   DF-2               — the data the record presents (AMR-14, by reference; DATA-014).
#:   RL-F2              — the RUNTIME policy the evaluation behaves-as (§7, by reference).
REFERENCED_UNITS: tuple[str, ...] = (
    "AMC-01",  # Universal Application (EC3-B12-U01, CERTIFIED) — secured-by boundary (AMR-08)
    "AMC-04",  # Universal Feature (EC3-B12-U04, CERTIFIED) — secured-by boundary (AMR-08)
    "DF-2",  # Represented data the record presents (AMR-14, by reference; DATA-014)
    "RL-F2",  # Runtime policy the evaluation behaves-as / records through (§7, by reference)
)

#: The frozen data-/service-security architectures a Security record reuses by reference for
#: its confidentiality/integrity classification vocabulary (APPLICATION-013 §7
#: security-reference; SEC-06 / SEC-C4). Referenced, never redefined.
DATA_SECURITY_CONCERN = "DATA-014"
SERVICE_SECURITY_CONCERN = "SERVICE-014"

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Security is AMC-09.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Security meta-class id (APPLICATION-005 §2; APPLICATION-013).
SECURITY_META_CLASS = "AMC-09"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a Security record participates in (APPLICATION-013 §6/§16):
#:   AMR-08 secured-by    (Application/Feature → Security; the DEFINING relationship — the
#:                         Security record is the *target* that classifies; reference-only)
#:   AMR-09 governed-by   (Application/Feature → Governance security-policy record; reference)
#:   AMR-10 identified-by (ENG-001 via ENG-002)
#:   AMR-14 presents-data (DATA / DF-2 / DATA-014 classified data, by reference)
SECURITY_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-08",
    "AMR-09",
    "AMR-10",
    "AMR-14",
)


class SecurityKind(str, Enum):
    """AXH-09 Security Hierarchy (APPLICATION-004 §3; APPLICATION-013 §5) — the classification
    of an application Security record.

    A Security record is classified by exactly one kind (single-facet, AXC-02 / AXC-04). Every
    kind is a distinct family of decidable, evaluative, non-enforcing classification
    (SEC-03 / UAL-14):

    * ``AUTHENTICATION`` — an identity-assertion classification (issues no credential — SEC-C2).
    * ``AUTHORIZATION``  — an access classification (grants nothing — SEC-C1/C2).
    * ``CONFIDENTIALITY``— a confidentiality classification (selects no crypto; reuses DATA-014).
    * ``INTEGRITY``      — an integrity classification (selects no control technology; DATA-014).

    Every kind evaluates via the RUNTIME policy concern (RUNTIME-010) by reference (§7): the
    distinction between kinds is *what protection concern* is classified, not *how* it is enacted
    — no kind grants access, issues a credential, or encrypts anything (SEC-C1…C5).
    """

    AUTHENTICATION = "Authentication-Record"  # identity-assertion classification (no credential)
    AUTHORIZATION = "Authorization-Record"  # access classification (grants nothing)
    CONFIDENTIALITY = "Confidentiality-Record"  # confidentiality classification (no crypto)
    INTEGRITY = "Integrity-Record"  # integrity classification (no control technology)


#: AXH-09 kind → the security facet it classifies (APPLICATION-013 §5).
SECURITY_FACETS: dict[SecurityKind, str] = {
    SecurityKind.AUTHENTICATION: "authentication",
    SecurityKind.AUTHORIZATION: "authorization",
    SecurityKind.CONFIDENTIALITY: "confidentiality",
    SecurityKind.INTEGRITY: "integrity",
}

#: The RUNTIME concern every security kind reuses by reference for evaluation
#: (APPLICATION-013 §7 security-evaluate; AOB-06). A Security record re-founds no runtime
#: concern; its evaluation references RUNTIME-010 (policy) via RL-F2 — declarative,
#: evaluative, and non-enforcing (SEC-03 / UAL-14).
KIND_RUNTIME_CONCERN: dict[SecurityKind, str] = {
    SecurityKind.AUTHENTICATION: "RUNTIME-010",  # policy — declarative authentication classify
    SecurityKind.AUTHORIZATION: "RUNTIME-010",  # policy — declarative authorization classify
    SecurityKind.CONFIDENTIALITY: "RUNTIME-010",  # policy — declarative confidentiality classify
    SecurityKind.INTEGRITY: "RUNTIME-010",  # policy — declarative integrity classify
}

#: The RUNTIME event concern a Security record reuses by reference to record an evaluation
#: judgment (APPLICATION-013 §7 security-record / AOV-09). Referenced, never redefined.
RUNTIME_EVENT_CONCERN = "RUNTIME-008"

#: The security kinds whose classification presents DF-2 data and reuses DATA-014
#: data-security classifications by reference (APPLICATION-013 §7 security-reference; SEC-06
#: / SEC-C4). Authentication/Authorization records classify identity/access and need not
#: present data.
DATA_BEARING_KINDS: frozenset[SecurityKind] = frozenset(
    {SecurityKind.CONFIDENTIALITY, SecurityKind.INTEGRITY}
)

#: Deterministic evaluation-precedence rank per security kind, grounded in the AXH-09
#: declaration order (APPLICATION-013 §5: Authentication → Authorization → Confidentiality →
#: Integrity). A *lower* rank is evaluated first. This is a decidable, evaluative ordering only
#: (SEC-03 / UAL-14): it enacts nothing, grants nothing, and blocks nothing — it merely records
#: the deterministic order in which classification facets are considered. No business rule is
#: invented; the order is the frozen taxonomy order (SEC-08 / UAL-15).
KIND_PRECEDENCE: dict[SecurityKind, int] = {
    SecurityKind.AUTHENTICATION: 0,  # evaluated first (AXH-09 declaration order)
    SecurityKind.AUTHORIZATION: 1,
    SecurityKind.CONFIDENTIALITY: 2,
    SecurityKind.INTEGRITY: 3,
}


class SecurityState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-013 §8) — the forward-only Security
    lifecycle states (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared (kind/subject/concern) but not composed
    COMPOSED = "COMPOSED"  # AOS-02 — classification + bindings assembled (by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — bound at an application boundary
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — live/decidable classification (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[SecurityState, ...] = (
    SecurityState.DEFINED,
    SecurityState.COMPOSED,
    SecurityState.CONTEXTUALIZED,
    SecurityState.EXECUTABLE,
    SecurityState.DEPRECATED,
    SecurityState.RETIRED,
)

# ---------------------------------------------------------------------------
# APPLICATION-013 §7 — Security evaluation binding (evaluate / record / reference)
# ---------------------------------------------------------------------------

#: The RUNTIME/DATA behavior bindings a security record references (never re-implemented).
SECURITY_BEHAVIOR_BINDINGS: dict[str, str] = {
    "security-evaluate": "RUNTIME policy (declarative, non-enforcing evaluation, AOB-06)",
    "security-record": "RUNTIME event (record an evaluation judgment, AOV-09)",
    "security-reference": "DATA-014 / SERVICE-014 security concern (reuse classification vocab)",
}

# ---------------------------------------------------------------------------
# APPLICATION-013 §4 — Security principles (SEC-01…10)
# ---------------------------------------------------------------------------

#: The ten Security principles (APPLICATION-013 §4), each mapped to its short rule.
SECURITY_PRINCIPLES: dict[str, str] = {
    "SEC-01": "Every security record is classified by an ENG-004 Type; no untyped record.",
    "SEC-02": "Every security record is an ENG-002 Object bearing an ENG-001 identity; no 2nd.",
    "SEC-03": "Evaluative-Only — a decidable predicate over a construct; it enacts nothing.",
    "SEC-04": "Non-Enforcement — grants no access, issues no credential, enforces no policy.",
    "SEC-05": "No Technology — selects no security/cryptographic technology/provider/protocol.",
    "SEC-06": "Foundation Reuse — reuses DATA-014 / SERVICE-014 by reference; re-founds none.",
    "SEC-07": "Boundary Recording — recorded at application/module/feature/interaction (AOR-08).",
    "SEC-08": "Additive Growth — new record types append additively (AXH-09) without renumber.",
    "SEC-09": "Non-Constitutiveness — confers no authority and embeds no secret (RR-07).",
    "SEC-10": "Reuse Labelling — consumed ARCH/CAT/REF/GEN/IMP/UKB assets are INPUT, never DONE.",
}

# ---------------------------------------------------------------------------
# APPLICATION-001 §7 — Application Laws (UAL-01…15) and §12 — Compliance (C1…C7)
# ---------------------------------------------------------------------------

#: The fifteen Application Laws (APPLICATION-001 §7), each mapped to its short obligation.
APPLICATION_LAWS: dict[str, str] = {
    "UAL-01": "Application is an experience layer founded on frozen EL-1/RL-F2/PL-F2/DF-2/SF-2.",
    "UAL-02": "Every construct reuses ENG/runtime/platform/data/service by reference; redefines 0.",
    "UAL-03": "Every application construct is classified by an ENG-004 Type; none is untyped.",
    "UAL-04": "A construct-as-thing bears an ENG-001 Identity via an ENG-002 Object; one scheme.",
    "UAL-05": "Every application construct-as-thing IS an ENG-002 Object; no parallel thing-model.",
    "UAL-06": "Every feature delivers capability by consuming SF-2 operations under contract.",
    "UAL-07": "Every application is composed of bounded, cohesive modules that group features.",
    "UAL-08": "Every feature declares its capability, composed operations, typed I/O, interaction.",
    "UAL-09": "Composition (features→modules→applications) reuses PL-F2/ENG-005; founding acyclic.",
    "UAL-10": "Application workflow/process binds to frozen RL-F2 (and SF-2 orchestration) by ref.",
    "UAL-11": "Every interaction is a typed actor-to-application exchange at an abstract surface.",
    "UAL-12": "Every application/feature has a decidable, forward-only, recorded lifecycle.",
    "UAL-13": "Every feature's/interaction's data is DF-2-represented data referenced by contract.",
    "UAL-14": "Application security/governance is declarative, evaluative, non-enforcing.",
    "UAL-15": "Non-constitutive: no new primitive, no authority, no secret, no technology/UI.",
}

#: The Application laws the Security construct is directly obligated by. **UAL-14 (application
#: security/governance is declarative, evaluative, non-enforcing) is THE governing law** of
#: AMC-09, grounded in UAL-10 (the evaluation binds the frozen RL-F2 policy concern by
#: reference), UAL-13 (the classified confidentiality/integrity data is DF-2 data by reference;
#: DATA-014 reuse), and UAL-15 (non-constitutiveness). A security record is also typed
#: (UAL-03), identified/object-borne (UAL-04/05), founded on the frozen substrate (UAL-01),
#: reuse-integral (UAL-02), and has a forward-only recorded lifecycle (UAL-12). UAL-06/07/08/09/
#: 11 are scoped to the Feature/Module/Application/Composition/Interaction units
#: (AMC-01/02/03/04/06/08): a security record is *recorded against* those constructs and
#: *classifies* their protection concerns — it neither delivers capability, groups features,
#: declares a feature contract, structurally composes, nor is an actor-to-application exchange.
SECURITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-01",
    "UAL-02",
    "UAL-03",
    "UAL-04",
    "UAL-05",
    "UAL-10",
    "UAL-12",
    "UAL-13",
    "UAL-14",
    "UAL-15",
)

#: Application laws scoped to other units (Feature/Module/Application/Composition/
#: Interaction), N/A to the Security record — recorded honestly (never silently dropped).
SECURITY_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-06",
    "UAL-07",
    "UAL-08",
    "UAL-09",
    "UAL-11",
)

#: The seven Application compliance conditions (APPLICATION-001 §12). A construct is
#: COMPLIANT iff all applicable conditions hold, decided on evidence and deterministically.
APPLICATION_COMPLIANCE: dict[str, str] = {
    "C1": "Typed (UAL-03), identified and objecthood-bound (UAL-04/05).",
    "C2": "Reuses frozen foundations by reference without redefinition (UAL-02).",
    "C3": "Delivers capability via SF-2 operations under contract; I/O is DF-2 by ref (UAL-06/13).",
    "C4": "Modules bounded, features explicit, interactions typed (UAL-07/08/11).",
    "C5": "Composition uses ENG-005 references; founding structure acyclic (UAL-09).",
    "C6": "Workflow/process and state bind to RL-F2/SF-2 by reference (UAL-10/12).",
    "C7": "Selects no technology, confers no authority, embeds no secret (UAL-15).",
}

# ---------------------------------------------------------------------------
# APPLICATION-005 §8 — Meta-validity gate (V1…V5) and constraints (AMK-01…08)
# ---------------------------------------------------------------------------

#: The five meta-validity checks (APPLICATION-005 §8) — a construct is META-VALID iff
#: all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Security → AMC-09).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints a Security record is bound by (APPLICATION-005 §4; APPLICATION-013 §10
#: SEC-K1…K5). **AMK-07 (security is declarative and non-enforcing, and every data reference
#: AMR-14 resolves to a DF-2/DATA-014 construct; none redefined) is THE materially-exercised
#: constraint** — a Security record *classifies* protection concerns and enacts nothing
#: (SEC-K3/K4 → AMK-07). **AMK-05 (the security-evaluate behavior reference resolves to an
#: RL-F2 construct — §7; none redefined) is materially exercised** — the evaluation behaves-as
#: the frozen RUNTIME policy concern by reference. AMK-01 (typed/identified/object-bound) and
#: AMK-02-analog (SEC-K2: declares the construct it classifies and the concern) are materially
#: exercised. **AMK-03 (the founding meta-relationship graph is acyclic) is satisfied
#: *vacuously*** — a Security record participates in **no** founding relationship (its
#: relationships AMR-08/09/10/14 are all reference-only), so its founding graph is empty and
#: therefore acyclic (V4 PASS), exactly as the State used no founding edge. AMK-04 (a feature is
#: engaged through an interaction before EXECUTABLE) is a Feature (AMC-04) obligation — recorded
#: not-applicable-to-the-security-record; and AMK-06 (composition ref AMR-07/12 → PL-F2) is
#: scoped to the Module/Application/Composition units (a security record binds RUNTIME policy by
#: reference, not PLATFORM composition) — recorded N/A.
SECURITY_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002). [SEC-K1]",
    "AMK-02": "Declares the construct it classifies and the concern (authn/authz/conf/int). "
    "[SEC-K2]",
    "AMK-03": "Founding graph acyclic — vacuous: a security record has no founding edge.",
    "AMK-05": "The security-evaluate behavior ref resolves to an RL-F2 construct (§7); none redef.",
    "AMK-07": "Security is declarative/non-enforcing; every data ref (AMR-14) resolves to a "
    "DF-2/DATA-014 construct; none redefined. [SEC-K3/K4]",
    "AMK-08": "No security record selects technology, grants access, or confers authority. "
    "[SEC-K5]",
}

#: Meta-constraints scoped to the Feature (AMC-04) and Module/Application/Composition
#: (AMC-01/03/08) units, N/A to the Security record.
SECURITY_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-04", "AMK-06")

#: The Security evaluation & non-enforcement rules (APPLICATION-013 §9; SEC-C1…C5).
SECURITY_EVALUATION_RULES: dict[str, str] = {
    "SEC-C1": "Security is a decidable predicate over a construct; the result is a record.",
    "SEC-C2": "Security grants no access, issues no credential, and enforces no policy (SEC-04).",
    "SEC-C3": "Security selects no security/cryptographic technology, provider, or protocol.",
    "SEC-C4": "Security records reuse DATA-014 / SERVICE-014 by reference; they re-found none.",
    "SEC-C5": "Security embeds no secret and confers no authority (RR-07; SEC-09).",
}

#: The Security constraints (APPLICATION-013 §10; SEC-K1…K5).
SECURITY_CONSTRAINTS: dict[str, str] = {
    "SEC-K1": "Every security record is typed (ENG-004), identified (ENG-001), object-bound.",
    "SEC-K2": "Every record declares the construct it classifies and the concern (AMK-02).",
    "SEC-K3": "Security meta-objects are declarative and non-enforcing (AMK-07).",
    "SEC-K4": "Every data reference resolves to a DF-2/DATA-014 construct; none redefined.",
    "SEC-K5": "No security record selects technology, grants access, or confers authority.",
}

#: The CCE ten-gate identifiers (EC-3 AP-4 certification strategy, CC-1…CC-10).
CCE_GATES: tuple[str, ...] = tuple(f"CC-{n}" for n in range(1, 11))

__all__ = [
    "REALIZATION_UNIT",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "TRACE_BACKWARD",
    "SUBSTRATE_REFS",
    "REFERENCED_UNITS",
    "DATA_SECURITY_CONCERN",
    "SERVICE_SECURITY_CONCERN",
    "META_CLASSES",
    "SECURITY_META_CLASS",
    "META_RELATIONSHIPS",
    "SECURITY_RELATIONSHIPS",
    "SecurityKind",
    "SECURITY_FACETS",
    "KIND_RUNTIME_CONCERN",
    "RUNTIME_EVENT_CONCERN",
    "DATA_BEARING_KINDS",
    "KIND_PRECEDENCE",
    "SecurityState",
    "LIFECYCLE_ORDER",
    "SECURITY_BEHAVIOR_BINDINGS",
    "SECURITY_PRINCIPLES",
    "APPLICATION_LAWS",
    "SECURITY_APPLICABLE_LAWS",
    "SECURITY_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "SECURITY_META_CONSTRAINTS",
    "SECURITY_INAPPLICABLE_CONSTRAINTS",
    "SECURITY_EVALUATION_RULES",
    "SECURITY_CONSTRAINTS",
    "CCE_GATES",
]
