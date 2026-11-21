"""EC3-B12-U06 — Interaction meta-model constants (read-only projections of
APPLICATION-001/003/004/005/010).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen Interaction
Architecture (APPLICATION-010, AMC-06 / UAIA) that the Universal Interaction realization
must conform to. It **defines no new law and redefines no foundation concept**
(UAL-02 / AMI-05 / UAL-15); it only names the frozen obligations so the realization can
be checked against them deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification
at the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 06) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 06).
REALIZATION_UNIT = "EC3-B12-U06"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-AP-4 §5/§9)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 12-APPLICATION/ specification commit.
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the certified baseline this builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` CERTIFIED-COMPLETE + FROZEN + the
#: CERTIFIED Band-12 U01 Universal Application root ``application.application`` + U02
#: Universal Capability ``application.capability`` + U03 Universal Module
#: ``application.module`` + U04 Universal Feature ``application.feature`` + U05 Universal
#: Workflow ``application.workflow`` at HEAD ``f650e0b``).
IMPLEMENTATION_ANCHOR = "f650e0b"

#: The backward traceability chain every realized Interaction records
#: (APPLICATION-010 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-06",  # APPLICATION-005 §2 — Interaction meta-class
    "APPLICATION-010",  # Universal Application Interaction Architecture (UAIA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Interaction construct reuses **directly** by reference
#: (UAL-02 / AMI-05). An Interaction is the typed actor-to-application exchange addressed
#: through an abstract surface: it reuses EL-1 (identity, value, typing, reference),
#: RL-F2 (the event/state concern it binds by reference — §7 / AMR-06/11), and DF-2 (the
#: exchanged data it presents by reference — AMR-14). It does **not** deliver a capability
#: (AMR-01), consume an SF-2 operation (AMR-13), group features (AMR-03), sequence
#: features (AMR-04), or assemble a PLATFORM composition (AMR-07/12) — those are the
#: Application / Capability / Module / Feature / Workflow concerns (AMC-01/02/03/04/05).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity; canonical core)
    "ENG-004",  # Type      (typed, UAL-03 / UAL-11)
    "ENG-005",  # Relationship/Reference (engaged-feature/surface/data/state/behavior refs)
    "RL-F2",  # Runtime event + state (behaves-as / holds-state, §7, by reference)
    "DF-2",  # Represented data presented by the interaction (presents-data AMR-14, by ref)
)

#: The prior CERTIFIED / frozen constructs the Interaction reuses **by reference through
#: its relationships** (never redefined; reused only by reference — mission reuse list):
#:   AMC-04 (Feature)  — engaged-through the interaction (AMR-05, the FOUNDING relationship:
#:                       the interaction is the sole engagement point through which a
#:                       feature is reachable — INT-04/INT-C2).
#:   AMC-07 (State)    — held by the interaction (AMR-06 holds-state; reference-only —
#:                       State is a downstream Band-12 unit, referenced by id → RL-F2).
#:   DF-2              — the data the interaction presents/exchanges (AMR-14, by reference).
#:   RL-F2             — the event/state the interaction behaves-as / holds (AMR-11/06).
REFERENCED_UNITS: tuple[str, ...] = (
    "AMC-04",  # Universal Feature (EC3-B12-U04, CERTIFIED) — engaged-through (AMR-05, founding)
    "AMC-07",  # Universal State (downstream) — held-state (AMR-06, by reference → RL-F2)
    "DF-2",  # Represented data the interaction presents/exchanges (AMR-14, by reference)
    "RL-F2",  # Runtime event + state the interaction behaves-as / holds (AMR-11/06)
)

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Interaction is AMC-06.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Interaction meta-class id (APPLICATION-005 §2; APPLICATION-010).
INTERACTION_META_CLASS = "AMC-06"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships an Interaction participates in (APPLICATION-010 §6/§16):
#:   AMR-05 engaged-through   (Feature → Interaction; FOUNDING, acyclic — the interaction
#:                             is the sole point through which a feature is engaged; INT-04)
#:   AMR-06 holds-state       (Interaction → State; interaction/session state, by
#:                             reference → RL-F2)
#:   AMR-10 identified-by     (ENG-001 via ENG-002)
#:   AMR-11 behaves-as        (RUNTIME event/state, by reference — §7)
#:   AMR-14 presents-data     (DATA / DF-2 exchanged data, by reference)
INTERACTION_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-05",
    "AMR-06",
    "AMR-10",
    "AMR-11",
    "AMR-14",
)


class InteractionKind(str, Enum):
    """AXH-06 Interaction Hierarchy (APPLICATION-004 §3; APPLICATION-010 §5) — the
    classification of an application Interaction.

    An Interaction is classified by exactly one kind (single-facet, AXC-02 / AXC-04). The
    kind **is** the interaction's decidable direction (INT-07 / INT-C5):
    """

    INPUT = "Input-Interaction"  # actor provides input at a boundary
    COMMAND = "Command-Interaction"  # actor invokes an intended change
    QUERY = "Query-Interaction"  # actor requests retrieval
    RESPONSE = "Response-Interaction"  # application returns a response to the actor


#: AXH-06 kind → the decidable exchange direction it declares (INT-07 / INT-C5).
INTERACTION_DIRECTIONS: dict[InteractionKind, str] = {
    InteractionKind.INPUT: "input",
    InteractionKind.COMMAND: "command",
    InteractionKind.QUERY: "query",
    InteractionKind.RESPONSE: "response",
}


class InteractionState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-010 §8) — the forward-only interaction
    lifecycle states (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared (direction/feature/surface/data) but not composed
    COMPOSED = "COMPOSED"  # AOS-02 — surface + exchange assembled (bound by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — placed within a state/session context
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — engageable (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[InteractionState, ...] = (
    InteractionState.DEFINED,
    InteractionState.COMPOSED,
    InteractionState.CONTEXTUALIZED,
    InteractionState.EXECUTABLE,
    InteractionState.DEPRECATED,
    InteractionState.RETIRED,
)

# ---------------------------------------------------------------------------
# APPLICATION-010 §7 — Interaction behavior binding (exchange / transition / emit)
# ---------------------------------------------------------------------------

#: The RUNTIME behavior bindings an interaction references (never re-implemented).
INTERACTION_BEHAVIOR_BINDINGS: dict[str, str] = {
    "interaction-exchange": "RUNTIME event (input/command/query/response exchange, AOB-03)",
    "interaction-transition": "RUNTIME state (interaction/session state, AOB-05)",
    "interaction-emit": "RUNTIME event (signal an interaction-engaged occurrence, AOV-04)",
}

# ---------------------------------------------------------------------------
# APPLICATION-010 §4 — Interaction principles (INT-01…10)
# ---------------------------------------------------------------------------

#: The ten Interaction principles (APPLICATION-010 §4), each mapped to its short rule.
INTERACTION_PRINCIPLES: dict[str, str] = {
    "INT-01": "Every interaction is classified by an ENG-004 Type; no untyped interaction.",
    "INT-02": "Every interaction is an ENG-002 Object bearing an ENG-001 identity; no 2nd scheme.",
    "INT-03": "Presentation (screen) is an abstract surface; no rendering technology selected.",
    "INT-04": "A feature is reachable by an actor only through a declared, typed interaction.",
    "INT-05": "Interaction behavior binds the RL-F2 event/state concern by reference.",
    "INT-06": "An interaction's exchanged data is DF-2 data by reference; it re-models none.",
    "INT-07": "Each interaction declares its direction (input/command/query/response) decidably.",
    "INT-08": "New interaction types append additively (AXH-06) without renumber or invalidation.",
    "INT-09": "An interaction confers no authority, embeds no secret, selects no technology.",
    "INT-10": "Any consumed ARCH/CAT/REF/GEN/IMP/UKB asset is labelled INPUT, never COMPLETION.",
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

#: The Application laws the Interaction construct is directly obligated by. **UAL-11 (every
#: interaction is a typed actor-to-application exchange at an abstract surface) is THE
#: governing law**, together with **UAL-13 (the exchanged data is DF-2 data by reference)**
#: and **UAL-10 (interaction behavior binds RL-F2 event/state by reference)**. The
#: interaction is also typed (UAL-03), identified/object-borne (UAL-04/05), founded on the
#: frozen substrate (UAL-01), reuse-integral (UAL-02), forward-only/recorded (UAL-12), and
#: non-constitutive (UAL-14/15). UAL-06/07/08/09 are scoped to the Feature/Module/
#: Application/Composition units (AMC-01/02/03/04/08): an interaction *engages* a feature —
#: it neither delivers capability, groups features, declares a feature contract, nor
#: structurally composes modules.
INTERACTION_APPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-01",
    "UAL-02",
    "UAL-03",
    "UAL-04",
    "UAL-05",
    "UAL-10",
    "UAL-11",
    "UAL-12",
    "UAL-13",
    "UAL-14",
    "UAL-15",
)

#: Application laws scoped to other units (Feature/Module/Application/Composition), N/A to
#: the Interaction — recorded honestly (never silently dropped).
INTERACTION_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-06",
    "UAL-07",
    "UAL-08",
    "UAL-09",
)

#: The seven Application compliance conditions (APPLICATION-001 §12). A construct is
#: COMPLIANT iff all applicable conditions hold, decided on evidence and
#: deterministically.
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
    "V1": "Instantiates exactly one meta-class (Interaction → AMC-06).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints an Interaction is bound by (APPLICATION-005 §4; APPLICATION-010 §10).
#: **AMK-03 (the founding meta-relationship graph AMR-02/03/05 is acyclic) is materially
#: exercised at the Interaction level** — the interaction is the *target* of the founding
#: engaged-through edge (Feature → Interaction, AMR-05), so its founding participation is
#: real (unlike the Workflow, which used no founding edge). **AMK-05 (every behavior/state
#: reference AMR-06/11 resolves to an RL-F2 construct; none redefined) is materially
#: exercised** — the interaction holds-state (AMR-06) and behaves-as (AMR-11), both →
#: RL-F2. **AMK-07 (the data reference AMR-14 resolves to a DF-2 construct; none redefined)
#: is materially exercised** — the interaction presents DF-2 data. AMK-02-analog (INT-K2:
#: declares direction, engaged feature, exchanged data) is materially exercised. AMK-04 (a
#: feature is engaged through an interaction before EXECUTABLE) is a Feature (AMC-04)
#: obligation *about* interactions — recorded not-applicable-to-the-interaction-itself; and
#: AMK-06 (composition ref AMR-07/12 → PL-F2) is scoped to the Module/Application/
#: Composition units (the interaction uses no AMR-07/12) — recorded not-applicable.
INTERACTION_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "AMK-02": "Declares its direction, engaged feature, and exchanged data (INT-K2 analog).",
    "AMK-03": "The founding meta-relationship graph (AMR-02/03/05) is acyclic (a DAG).",
    "AMK-05": "Every behavior/state ref (AMR-06/11) resolves to an RL-F2 construct; none redef.",
    "AMK-07": "Every data ref (AMR-14) resolves to a DF-2 construct; none redefined.",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

#: Meta-constraints scoped to the Feature (AMC-04) and Module/Application/Composition
#: (AMC-01/03/08) units, N/A to the Interaction.
INTERACTION_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-04", "AMK-06")

#: The Interaction surface & engagement rules (APPLICATION-010 §9; INT-C1…C5).
INTERACTION_SURFACE_RULES: dict[str, str] = {
    "INT-C1": "The presentation surface (screen) is abstract: surface/region/exchange, no tech.",
    "INT-C2": "A feature is engaged only through a declared, typed interaction (INT-04).",
    "INT-C3": "Founding relations (engaged-through) form a DAG (AMK-03).",
    "INT-C4": "An interaction's exchanged data references (does not embed) DF-2 data (AOR-14).",
    "INT-C5": "Each interaction declares a decidable direction (input/command/query/response).",
}

#: The Interaction constraints (APPLICATION-010 §10; INT-K1…K5).
INTERACTION_CONSTRAINTS: dict[str, str] = {
    "INT-K1": "Every interaction is typed (ENG-004), identified (ENG-001), object-bound (ENG-002).",
    "INT-K2": "Every interaction declares its direction, engaged feature, and exchanged data.",
    "INT-K3": "Every behavior/state reference resolves to an RL-F2 construct; none redefined.",
    "INT-K4": "Every data reference resolves to a DF-2 construct; none redefined.",
    "INT-K5": "No interaction selects rendering tech/UI framework/design system or authority.",
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
    "INTERACTION_META_CLASS",
    "META_RELATIONSHIPS",
    "INTERACTION_RELATIONSHIPS",
    "InteractionKind",
    "INTERACTION_DIRECTIONS",
    "InteractionState",
    "LIFECYCLE_ORDER",
    "INTERACTION_BEHAVIOR_BINDINGS",
    "INTERACTION_PRINCIPLES",
    "APPLICATION_LAWS",
    "INTERACTION_APPLICABLE_LAWS",
    "INTERACTION_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "INTERACTION_META_CONSTRAINTS",
    "INTERACTION_INAPPLICABLE_CONSTRAINTS",
    "INTERACTION_SURFACE_RULES",
    "INTERACTION_CONSTRAINTS",
    "CCE_GATES",
]
