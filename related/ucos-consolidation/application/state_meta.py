"""EC3-B12-U07 — State meta-model constants (read-only projections of
APPLICATION-001/003/004/005/011).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen State Architecture
(APPLICATION-011, AMC-07 / UASA) that the Universal State realization must conform to. It
**defines no new law and redefines no foundation concept** (UAL-02 / AMI-05 / UAL-15); it
only names the frozen obligations so the realization can be checked against them
deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification at
the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 07) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 07).
REALIZATION_UNIT = "EC3-B12-U07"

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
#: ``application.workflow`` + U06 Universal Interaction ``application.interaction`` at HEAD
#: ``1096d9d``).
IMPLEMENTATION_ANCHOR = "1096d9d"

#: The backward traceability chain every realized State records (APPLICATION-011 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-07",  # APPLICATION-005 §2 — State meta-class
    "APPLICATION-011",  # Universal Application State Architecture (UASA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the State construct reuses **directly** by reference
#: (UAL-02 / AMI-05). A State is the implementation-independent condition of an
#: application/module/feature/interaction within a context: it reuses EL-1 (identity,
#: value, typing, reference), RL-F2 (the RUNTIME state concern it behaves-as / binds by
#: reference — §7 / AMR-11 / STA-03), and DF-2 (the bound data it presents by reference —
#: AMR-14). It does **not** deliver a capability (AMR-01), consume an SF-2 operation
#: (AMR-13), group features (AMR-03), sequence features (AMR-04), engage a feature
#: (AMR-05), or assemble a PLATFORM composition (AMR-07/12) — those are the Application /
#: Capability / Module / Feature / Workflow / Interaction concerns (AMC-01…06).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity; canonical core)
    "ENG-004",  # Type      (typed, UAL-03 / STA-01)
    "ENG-005",  # Relationship/Reference (holder/context/data/behavior refs)
    "RL-F2",  # Runtime state (behaves-as / binds RUNTIME state, §7, AMR-11, by reference)
    "DF-2",  # Represented data the state binds/presents (presents-data AMR-14, by ref)
)

#: The prior CERTIFIED / frozen constructs the State reuses **by reference through its
#: relationships** (never redefined; reused only by reference — mission reuse list):
#:   AMC-06 (Interaction) — the construct that *holds* this state (AMR-06 held-by; the
#:                          canonical exemplar is an interaction/session State held by the
#:                          CERTIFIED AMC-06, reference-only). Application/Feature/Workflow
#:                          are the other admissible holders (AOR-06 source set).
#:   DF-2               — the data the state binds/presents (AMR-14, by reference).
#:   RL-F2              — the RUNTIME state the state behaves-as / binds (AMR-11, by ref).
REFERENCED_UNITS: tuple[str, ...] = (
    "AMC-06",  # Universal Interaction (EC3-B12-U06, CERTIFIED) — holds this state (AMR-06)
    "DF-2",  # Represented data the state binds/presents (AMR-14, by reference)
    "RL-F2",  # Runtime state the state behaves-as / binds (AMR-11, by reference)
)

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). State is AMC-07.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The State meta-class id (APPLICATION-005 §2; APPLICATION-011).
STATE_META_CLASS = "AMC-07"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a State participates in (APPLICATION-011 §6/§16):
#:   AMR-06 holds-state   (Application/Feature/Interaction/Workflow → State; the State is
#:                         the *held* condition — reference-only, NOT founding)
#:   AMR-10 identified-by (ENG-001 via ENG-002)
#:   AMR-11 behaves-as    (RUNTIME state, by reference — §7 / STA-03)
#:   AMR-14 presents-data (DATA / DF-2 bound data, by reference)
STATE_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-06",
    "AMR-10",
    "AMR-11",
    "AMR-14",
)


class StateKind(str, Enum):
    """AXH-07 State Hierarchy (APPLICATION-004 §3; APPLICATION-011 §5) — the classification
    of an application State.

    A State is classified by exactly one kind (single-facet, AXC-02 / AXC-04). Every kind
    is bound to a declared context and reuses the RUNTIME state concern by reference
    (STA-03/06):
    """

    LIFECYCLE = "Lifecycle-State"  # position in the AOS lifecycle (DEFINED…RETIRED)
    INTERACTION = "Interaction-State"  # condition of an interaction/session within a context
    CONTEXT = "Context-State"  # bound actor/session/tenant/locale/policy condition


#: AXH-07 kind → the condition facet it classifies (APPLICATION-011 §5).
STATE_FACETS: dict[StateKind, str] = {
    StateKind.LIFECYCLE: "lifecycle",
    StateKind.INTERACTION: "interaction",
    StateKind.CONTEXT: "context",
}


class StateLifecycle(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-011 §8) — the forward-only State lifecycle
    (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared (kind/holder/context/data) but not composed
    COMPOSED = "COMPOSED"  # AOS-02 — condition + bindings assembled (by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — bound within a declared context
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — live/decidable condition (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05 / STA-04: no in-place reversal).
LIFECYCLE_ORDER: tuple[StateLifecycle, ...] = (
    StateLifecycle.DEFINED,
    StateLifecycle.COMPOSED,
    StateLifecycle.CONTEXTUALIZED,
    StateLifecycle.EXECUTABLE,
    StateLifecycle.DEPRECATED,
    StateLifecycle.RETIRED,
)

# ---------------------------------------------------------------------------
# APPLICATION-011 §7 — State behavior binding (transition / record / contextualize)
# ---------------------------------------------------------------------------

#: The RUNTIME behavior bindings a state references (never re-implemented — §7).
STATE_BEHAVIOR_BINDINGS: dict[str, str] = {
    "state-transition": "RUNTIME state (change application/feature/interaction condition, AOB-05)",
    "state-record": "RUNTIME event (record the transition — STA-05 / AOV-07)",
    "state-contextualize": "RUNTIME context (bind the state to a declared context — STA-06)",
}

# ---------------------------------------------------------------------------
# APPLICATION-011 §4 — State principles (STA-01…10)
# ---------------------------------------------------------------------------

#: The ten State principles (APPLICATION-011 §4), each mapped to its short rule.
STATE_PRINCIPLES: dict[str, str] = {
    "STA-01": "Every state is classified by an ENG-004 Type; no untyped state exists.",
    "STA-02": "Every state is an ENG-002 Object bearing an ENG-001 identity; no 2nd scheme.",
    "STA-03": "Application state binds the RL-F2 state concern by reference; re-founds none.",
    "STA-04": "The lifecycle is a forward-only ordered set; no in-place-reversible transition.",
    "STA-05": "Every transition is recorded as a RUNTIME event (by reference); none silent.",
    "STA-06": "Every state is bound to a declared context (actor/session/tenant/locale/policy).",
    "STA-07": "Membership in a lifecycle state is decidable at any point.",
    "STA-08": "New state types append additively (AXH-07) without renumber or invalidation.",
    "STA-09": "A state confers no authority, embeds no secret, selects no technology.",
    "STA-10": "Any consumed ARCH/CAT/REF/GEN/IMP/UKB asset is labelled INPUT, never COMPLETION.",
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

#: The Application laws the State construct is directly obligated by. **UAL-12 (every
#: application/feature has a decidable, forward-only, recorded lifecycle — and its context
#: governance) is THE governing law**, together with **UAL-10 (state behavior binds the
#: frozen RL-F2 state concern by reference)** and **UAL-13 (the bound data is DF-2 data by
#: reference)**. The state is also typed (UAL-03), identified/object-borne (UAL-04/05),
#: founded on the frozen substrate (UAL-01), reuse-integral (UAL-02), and non-constitutive
#: (UAL-14/15). UAL-06/07/08/09/11 are scoped to the Feature/Module/Application/Composition/
#: Interaction units (AMC-01/02/03/04/06/08): a state is *held by* those constructs and
#: *conditions* delivery — it neither delivers capability, groups features, declares a
#: feature contract, structurally composes modules, nor is an actor-to-application exchange.
STATE_APPLICABLE_LAWS: tuple[str, ...] = (
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
#: Interaction), N/A to the State — recorded honestly (never silently dropped).
STATE_INAPPLICABLE_LAWS: tuple[str, ...] = (
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
    "V1": "Instantiates exactly one meta-class (State → AMC-07).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints a State is bound by (APPLICATION-005 §4; APPLICATION-011 §10 STA-K1…K5).
#: **AMK-05 (every behavior/state reference AMR-06/11 resolves to an RL-F2 construct; none
#: redefined) is THE materially-exercised constraint** — a State *is* the application-layer
#: condition that behaves-as (AMR-11) the frozen RUNTIME state concern, bound by reference
#: (STA-03/STA-K3). **AMK-07 (the data reference AMR-14 resolves to a DF-2 construct; none
#: redefined) is materially exercised** — the state's bound data is DF-2 (STA-C4/STA-K4).
#: AMK-01 (typed/identified/object-bound) and AMK-02-analog (STA-K2: declares its context
#: and current lifecycle position) are materially exercised. **AMK-03 (the founding
#: meta-relationship graph AMR-02/03/05 is acyclic) is satisfied *vacuously*** — a State
#: participates in **no** founding relationship (its relationships AMR-06/10/11/14 are all
#: reference-only), so its founding graph is empty and therefore acyclic (V4 PASS), exactly
#: as the Workflow used no founding edge. AMK-04 (a feature is engaged through an
#: interaction before EXECUTABLE) is a Feature (AMC-04) obligation — recorded
#: not-applicable-to-the-state; and AMK-06 (composition ref AMR-07/12 → PL-F2) is scoped to
#: the Module/Application/Composition units (the state uses no AMR-07/12) — recorded N/A.
STATE_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "AMK-02": "Declares its context and current lifecycle position (STA-K2 analog).",
    "AMK-03": "Founding graph (AMR-02/03/05) acyclic — vacuous: state has no founding edge.",
    "AMK-05": "Every behavior/state ref (AMR-06/11) resolves to an RL-F2 construct; none redef.",
    "AMK-07": "Every data ref (AMR-14) resolves to a DF-2 construct; none redefined.",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

#: Meta-constraints scoped to the Feature (AMC-04) and Module/Application/Composition
#: (AMC-01/03/08) units, N/A to the State.
STATE_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-04", "AMK-06")

#: The State transition & context rules (APPLICATION-011 §9; STA-C1…C5).
STATE_TRANSITION_RULES: dict[str, str] = {
    "STA-C1": "The lifecycle is forward-only; a state never reverts in place (UAL-12).",
    "STA-C2": "Every transition is recorded as a RUNTIME event; no silent transition (STA-05).",
    "STA-C3": "Every state is bound to a decidable context; context is explicit (STA-06).",
    "STA-C4": "A state's bound data references (does not embed) DF-2 data (AOR-14).",
    "STA-C5": "State binds RL-F2 state by reference; it re-founds no runtime concern (UAL-12).",
}

#: The State constraints (APPLICATION-011 §10; STA-K1…K5).
STATE_CONSTRAINTS: dict[str, str] = {
    "STA-K1": "Every state is typed (ENG-004), identified (ENG-001), object-bound (ENG-002).",
    "STA-K2": "Every state declares its context and current lifecycle position.",
    "STA-K3": "Every behavior/state reference resolves to an RL-F2 construct; none redefined.",
    "STA-K4": "Every data reference resolves to a DF-2 construct; none redefined.",
    "STA-K5": "No state selects technology (store/cache/db) or confers authority.",
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
    "META_CLASSES",
    "STATE_META_CLASS",
    "META_RELATIONSHIPS",
    "STATE_RELATIONSHIPS",
    "StateKind",
    "STATE_FACETS",
    "StateLifecycle",
    "LIFECYCLE_ORDER",
    "STATE_BEHAVIOR_BINDINGS",
    "STATE_PRINCIPLES",
    "APPLICATION_LAWS",
    "STATE_APPLICABLE_LAWS",
    "STATE_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "STATE_META_CONSTRAINTS",
    "STATE_INAPPLICABLE_CONSTRAINTS",
    "STATE_TRANSITION_RULES",
    "STATE_CONSTRAINTS",
    "CCE_GATES",
]
