"""EC3-B12-U10 — Governance meta-model constants (read-only projections of
APPLICATION-001/003/004/005/014).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen Governance Architecture
(APPLICATION-014, AMC-10 / UAGA) that the Universal Governance realization must conform to.
It **defines no new law and redefines no foundation concept** (UAL-02 / AMI-05 / UAL-15); it
only names the frozen obligations so the realization can be checked against them
deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification at
the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.

* AMC-10 **Governance** models ontology entity **AOE-10** — *"the declarative, record-only
  classification of an application/feature's conformance, lifecycle, and policy concerns"*
  (APPLICATION-003 §2; APPLICATION-014 §3) — classified by hierarchy **AXH-10**
  (Conformance-Record / Lifecycle-Record / Policy-Record; APPLICATION-004 / APPLICATION-014 §5).
* A Governance record is the *target* of **governed-by** (AMR-09; AOR-09) — the application/
  feature construct it governs is **governed-by** this record (reference-only, the DEFINING
  relationship) — **secures-by** a Security record whose conformance it references (AMR-08;
  AOR-08; reference-only), **holds-state** a State construct for its lifecycle records (AMR-06;
  AOR-06; reference-only), and is **identified-by** ENG-001 via ENG-002 (AMR-10; AOR-10).
* Its evaluation **behaves-as** the frozen RUNTIME policy concern (§7 governance-evaluate,
  AOB-06) bound by reference; it records judgments via the RUNTIME event concern (§7
  governance-record, AOV-08/09); breaking change is supersession under ENG-000 change control
  (§7 governance-supersede; UCI-001).
* Governance principles GOV-01…10 (APPLICATION-014 §4) govern the construct; **UAL-14**
  (application security/governance is declarative, evaluative, non-enforcing) is THE governing
  law, grounded in UAL-15 (non-constitutiveness) and UAL-10 (evaluation reuses the RUNTIME
  policy concern by reference).
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 10) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 10).
REALIZATION_UNIT = "EC3-B12-U10"

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
#: ``application.composition`` + U09 Universal Security ``application.security`` at HEAD
#: ``81582a1``).
IMPLEMENTATION_ANCHOR = "81582a1"

#: The backward traceability chain every realized Governance record records
#: (APPLICATION-014 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-10",  # APPLICATION-005 §2 — Governance meta-class
    "APPLICATION-014",  # Universal Application Governance Architecture (UAGA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Governance construct reuses **directly** by reference
#: (UAL-02 / AMI-05). A Governance record is the declarative record-only judgment: it reuses
#: EL-1 (identity, value, typing, reference) and RL-F2 (the RUNTIME policy concern its
#: evaluation behaves-as — §7 governance-evaluate; and the RUNTIME event concern it records
#: judgments through — §7 governance-record). It does **not** deliver a capability (AMR-01),
#: consume an SF-2 operation (AMR-13), present DF-2 data (AMR-14), group features (AMR-03),
#: sequence features (AMR-04), engage a feature (AMR-05), or assemble a PLATFORM composition
#: (AMR-07/12) — those are the Application / Capability / Module / Feature / Workflow /
#: Interaction / State / Composition / Security concerns (AMC-01…09).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity; canonical core)
    "ENG-004",  # Type      (typed governance record, UAL-03 / GOV-01)
    "ENG-005",  # Relationship/Reference (governed/security/state/behavior refs)
    "RL-F2",  # Runtime policy/event (governance-evaluate / governance-record, §7, by reference)
)

#: The prior CERTIFIED / frozen constructs the Governance record reuses **by reference through
#: its relationships** (never redefined; reused only by reference — mission reuse list):
#:   AMC-01 (Application) — a construct governed-by this record (AMR-09; the governed subject).
#:   AMC-04 (Feature)     — a construct governed-by this record (AMR-09; the governed subject).
#:   AMC-09 (Security)    — a Security record whose conformance this record references
#:                          (AMR-08 secured-by; reference-only).
#:   AMC-07 (State)       — a State a Lifecycle-Record holds (AMR-06 holds-state; reference-only).
#:   RL-F2              — the RUNTIME policy the evaluation behaves-as (§7, by reference).
REFERENCED_UNITS: tuple[str, ...] = (
    "AMC-01",  # Universal Application (EC3-B12-U01, CERTIFIED) — governed-by boundary (AMR-09)
    "AMC-04",  # Universal Feature (EC3-B12-U04, CERTIFIED) — governed-by boundary (AMR-09)
    "AMC-07",  # Universal State (EC3-B12-U07, CERTIFIED) — held by a lifecycle-record (AMR-06)
    "AMC-09",  # Universal Security (EC3-B12-U09, CERTIFIED) — conformance-of (AMR-08 secured-by)
    "RL-F2",  # Runtime policy the evaluation behaves-as / records through (§7, by reference)
)

#: The frozen ENG-000 change-control concern a Governance record references for supersession
#: lineage (APPLICATION-014 §7 governance-supersede; GOV-06 / UCI-001). Referenced, never
#: redefined.
CHANGE_CONTROL_CONCERN = "ENG-000"

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Governance is AMC-10.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Governance meta-class id (APPLICATION-005 §2; APPLICATION-014).
GOVERNANCE_META_CLASS = "AMC-10"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a Governance record participates in (APPLICATION-014 §6/§16):
#:   AMR-06 holds-state   (Governance → State; lifecycle-record; reference-only)
#:   AMR-08 secured-by    (Governance → Security; conformance-of; reference-only)
#:   AMR-09 governed-by   (Application/Feature → Governance; the DEFINING relationship — the
#:                         Governance record is the *target* that governs; reference-only)
#:   AMR-10 identified-by (ENG-001 via ENG-002)
GOVERNANCE_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-06",
    "AMR-08",
    "AMR-09",
    "AMR-10",
)


class GovernanceKind(str, Enum):
    """AXH-10 Governance Hierarchy (APPLICATION-004 §3; APPLICATION-014 §5) — the classification
    of an application Governance record.

    A Governance record is classified by exactly one kind (single-facet, AXC-02 / AXC-04). Every
    kind is a distinct family of decidable, declarative, record-only classification
    (GOV-03 / UAL-14):

    * ``CONFORMANCE`` — a declarative conformance classification against the meta-model.
    * ``LIFECYCLE``   — a declarative lifecycle-transition record (AOS, forward-only).
    * ``POLICY``      — a declarative policy classification (measures, does not enforce).

    Every kind evaluates via the RUNTIME policy concern (RUNTIME-010) by reference (§7): the
    distinction between kinds is *what governance concern* is recorded, not *how* it is enacted
    — no kind approves, enforces, ratifies, or confers authority (GOV-C1…C5).
    """

    CONFORMANCE = "Conformance-Record"  # conformance classification against the meta-model
    LIFECYCLE = "Lifecycle-Record"  # lifecycle-transition record (AOS, forward-only)
    POLICY = "Policy-Record"  # policy classification (measures, does not enforce)


#: AXH-10 kind → the governance concern it records (APPLICATION-014 §5).
GOVERNANCE_FACETS: dict[GovernanceKind, str] = {
    GovernanceKind.CONFORMANCE: "conformance",
    GovernanceKind.LIFECYCLE: "lifecycle",
    GovernanceKind.POLICY: "policy",
}

#: The RUNTIME concern every governance kind reuses by reference for evaluation
#: (APPLICATION-014 §7 governance-evaluate; AOB-06). A Governance record re-founds no runtime
#: concern; its evaluation references RUNTIME-010 (policy) via RL-F2 — declarative,
#: evaluative, and non-enforcing (GOV-03 / UAL-14).
KIND_RUNTIME_CONCERN: dict[GovernanceKind, str] = {
    GovernanceKind.CONFORMANCE: "RUNTIME-010",  # policy — declarative conformance classify
    GovernanceKind.LIFECYCLE: "RUNTIME-010",  # policy — declarative lifecycle classify
    GovernanceKind.POLICY: "RUNTIME-010",  # policy — declarative policy classify
}

#: The RUNTIME event concern a Governance record reuses by reference to record an evaluation
#: judgment / lifecycle transition (APPLICATION-014 §7 governance-record / AOV-08/09).
#: Referenced, never redefined.
RUNTIME_EVENT_CONCERN = "RUNTIME-008"

#: The governance kinds whose record holds a State construct by reference (AMR-06 holds-state;
#: APPLICATION-014 §6). Only a Lifecycle-Record holds state; Conformance/Policy records classify
#: against the meta-model / policy and need hold no state.
STATE_BEARING_KINDS: frozenset[GovernanceKind] = frozenset({GovernanceKind.LIFECYCLE})

#: Deterministic evaluation-precedence rank per governance kind, grounded in the AXH-10
#: declaration order (APPLICATION-014 §5: Conformance → Lifecycle → Policy). A *lower* rank is
#: evaluated first. This is a decidable, evaluative ordering only (GOV-03 / UAL-14): it enacts
#: nothing, approves nothing, and blocks nothing — it merely records the deterministic order in
#: which governance facets are considered. No business rule is invented; the order is the frozen
#: taxonomy order (GOV-08 / UAL-15).
KIND_PRECEDENCE: dict[GovernanceKind, int] = {
    GovernanceKind.CONFORMANCE: 0,  # evaluated first (AXH-10 declaration order)
    GovernanceKind.LIFECYCLE: 1,
    GovernanceKind.POLICY: 2,
}


class GovernanceState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-014 §8) — the forward-only Governance
    lifecycle states (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared (kind/subject/concern) but not composed
    COMPOSED = "COMPOSED"  # AOS-02 — classification + bindings assembled (by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — bound at an application boundary
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — live/decidable classification (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[GovernanceState, ...] = (
    GovernanceState.DEFINED,
    GovernanceState.COMPOSED,
    GovernanceState.CONTEXTUALIZED,
    GovernanceState.EXECUTABLE,
    GovernanceState.DEPRECATED,
    GovernanceState.RETIRED,
)

# ---------------------------------------------------------------------------
# APPLICATION-014 §7 — Governance evaluation binding (evaluate / record / supersede)
# ---------------------------------------------------------------------------

#: The RUNTIME/change-control behavior bindings a governance record references (never
#: re-implemented).
GOVERNANCE_BEHAVIOR_BINDINGS: dict[str, str] = {
    "governance-evaluate": "RUNTIME policy (declarative, non-enforcing evaluation, AOB-06)",
    "governance-record": "RUNTIME event (record a judgment / lifecycle transition, AOV-08/09)",
    "governance-supersede": "ENG-000 change control (supersession lineage; UCI-001)",
}

# ---------------------------------------------------------------------------
# APPLICATION-014 §4 — Governance principles (GOV-01…10)
# ---------------------------------------------------------------------------

#: The ten Governance principles (APPLICATION-014 §4), each mapped to its short rule.
GOVERNANCE_PRINCIPLES: dict[str, str] = {
    "GOV-01": "Every governance record is classified by an ENG-004 Type; no untyped record.",
    "GOV-02": "Every governance record is an ENG-002 Object bearing an ENG-001 identity; no 2nd.",
    "GOV-03": "Record-Only — a declarative judgment recorded against a construct; enacts nothing.",
    "GOV-04": "Non-Enforcement — approves/enforces/ratifies nothing; confers no authority.",
    "GOV-05": "Custodial Discharge — discharged through the ENG-000 custodian/Registrar.",
    "GOV-06": "Additive Change Control — breaking change is supersession under ENG-000; no mutate.",
    "GOV-07": "Boundary Recording — recorded at app/module/feature/workflow/interaction (AOR-09).",
    "GOV-08": "Additive Growth — new record types append additively (AXH-10) without renumber.",
    "GOV-09": "Non-Constitutiveness — confers no constitutional standing; authorizes no EC step.",
    "GOV-10": "Reuse Labelling — consumed ARCH/CAT/REF/GEN/IMP/UKB assets are INPUT, never DONE.",
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

#: The Application laws the Governance construct is directly obligated by. **UAL-14 (application
#: security/governance is declarative, evaluative, non-enforcing) is THE governing law** of
#: AMC-10, grounded in UAL-10 (the evaluation binds the frozen RL-F2 policy concern by
#: reference) and UAL-15 (non-constitutiveness). A governance record is also typed (UAL-03),
#: identified/object-borne (UAL-04/05), founded on the frozen substrate (UAL-01), reuse-integral
#: (UAL-02), and has a forward-only recorded lifecycle (UAL-12). UAL-06/07/08/09/11 are scoped
#: to the Feature/Module/Application/Composition/Interaction units (AMC-01/02/03/04/06/08): a
#: governance record is *recorded against* those constructs and *classifies* their conformance/
#: lifecycle/policy concerns — it neither delivers capability, groups features, declares a
#: feature contract, structurally composes, nor is an actor-to-application exchange. UAL-13
#: (DF-2 data by reference) is scoped to the Feature/Interaction/State units — a governance
#: record presents no data (it uses no AMR-14), so UAL-13 is N/A.
GOVERNANCE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-01",
    "UAL-02",
    "UAL-03",
    "UAL-04",
    "UAL-05",
    "UAL-10",
    "UAL-12",
    "UAL-14",
    "UAL-15",
)

#: Application laws scoped to other units (Feature/Module/Application/Composition/Interaction/
#: State-and-feature data), N/A to the Governance record — recorded honestly (never silently
#: dropped).
GOVERNANCE_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-06",
    "UAL-07",
    "UAL-08",
    "UAL-09",
    "UAL-11",
    "UAL-13",
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
    "V1": "Instantiates exactly one meta-class (Governance → AMC-10).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints a Governance record is bound by (APPLICATION-005 §4; APPLICATION-014 §10
#: GOV-K1…K5). **AMK-07 (governance is declarative and non-enforcing) is THE materially-exercised
#: constraint** — a Governance record *records* conformance/lifecycle/policy judgments and enacts
#: nothing (GOV-K3 → AMK-07). **AMK-05 (the governance-evaluate behavior reference resolves to an
#: RL-F2 construct — §7; none redefined) is materially exercised** — the evaluation behaves-as
#: the frozen RUNTIME policy concern by reference. AMK-01 (typed/identified/object-bound) and
#: AMK-02-analog (GOV-K2: declares the construct it governs and the concern) are materially
#: exercised. **AMK-03 (the founding meta-relationship graph is acyclic) is satisfied
#: *vacuously*** — a Governance record participates in **no** founding relationship (its
#: relationships AMR-06/08/09/10 are all reference-only), so its founding graph is empty and
#: therefore acyclic (V4 PASS), exactly as the State/Security used no founding edge. AMK-04 (a
#: feature is engaged through an interaction before EXECUTABLE) is a Feature (AMC-04) obligation
#: — recorded not-applicable-to-the-governance-record; and AMK-06 (composition ref AMR-07/12 →
#: PL-F2) is scoped to the Module/Application/Composition units (a governance record binds
#: RUNTIME policy by reference, not PLATFORM composition) — recorded N/A.
GOVERNANCE_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002). [GOV-K1]",
    "AMK-02": "Declares the construct it governs and the concern (conformance/lifecycle/policy). "
    "[GOV-K2]",
    "AMK-03": "Founding graph acyclic — vacuous: a governance record has no founding edge.",
    "AMK-05": "The governance-evaluate behavior ref resolves to an RL-F2 construct (§7); none "
    "redef. [GOV-K4]",
    "AMK-07": "Governance is declarative/non-enforcing; it approves/enforces/ratifies nothing. "
    "[GOV-K3]",
    "AMK-08": "No governance record selects technology or confers authority. [GOV-K5]",
}

#: Meta-constraints scoped to the Feature (AMC-04) and Module/Application/Composition
#: (AMC-01/03/08) units, N/A to the Governance record.
GOVERNANCE_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-04", "AMK-06")

#: The Governance change-control & non-enforcement rules (APPLICATION-014 §9; GOV-C1…C5).
GOVERNANCE_EVALUATION_RULES: dict[str, str] = {
    "GOV-C1": "Governance is a declarative judgment recorded against a construct; enacts nothing.",
    "GOV-C2": "Governance approves, enforces, and ratifies nothing; confers no authority.",
    "GOV-C3": "Change is additive; breaking change is supersession under ENG-000; no mutation.",
    "GOV-C4": "Governance is discharged through the ENG-000 custodian/Registrar.",
    "GOV-C5": "Governance confers no constitutional standing and authorizes no EC-series step.",
}

#: The Governance constraints (APPLICATION-014 §10; GOV-K1…K5).
GOVERNANCE_CONSTRAINTS: dict[str, str] = {
    "GOV-K1": "Every governance record is typed (ENG-004), identified (ENG-001), object-bound.",
    "GOV-K2": "Every record declares the construct it governs and the concern (AMK-02).",
    "GOV-K3": "Governance meta-objects are declarative and non-enforcing (AMK-07).",
    "GOV-K4": "Every state reference resolves to a RL-F2 construct; none redefined (AMK-05).",
    "GOV-K5": "No governance record selects technology or confers authority (AMK-08).",
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
    "CHANGE_CONTROL_CONCERN",
    "META_CLASSES",
    "GOVERNANCE_META_CLASS",
    "META_RELATIONSHIPS",
    "GOVERNANCE_RELATIONSHIPS",
    "GovernanceKind",
    "GOVERNANCE_FACETS",
    "KIND_RUNTIME_CONCERN",
    "RUNTIME_EVENT_CONCERN",
    "STATE_BEARING_KINDS",
    "KIND_PRECEDENCE",
    "GovernanceState",
    "LIFECYCLE_ORDER",
    "GOVERNANCE_BEHAVIOR_BINDINGS",
    "GOVERNANCE_PRINCIPLES",
    "APPLICATION_LAWS",
    "GOVERNANCE_APPLICABLE_LAWS",
    "GOVERNANCE_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "GOVERNANCE_META_CONSTRAINTS",
    "GOVERNANCE_INAPPLICABLE_CONSTRAINTS",
    "GOVERNANCE_EVALUATION_RULES",
    "GOVERNANCE_CONSTRAINTS",
    "CCE_GATES",
]
