"""EC3-B12-U08 — Composition meta-model constants (read-only projections of
APPLICATION-001/003/004/005/012).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen Composition
Architecture (APPLICATION-012, AMC-08 / UACpA) that the Universal Composition realization
must conform to. It **defines no new law and redefines no foundation concept**
(UAL-02 / AMI-05 / UAL-15); it only names the frozen obligations so the realization can be
checked against them deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification at
the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 08) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 08).
REALIZATION_UNIT = "EC3-B12-U08"

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
#: Universal State ``application.state`` at HEAD ``8ed6781``).
IMPLEMENTATION_ANCHOR = "8ed6781"

#: The backward traceability chain every realized Composition records
#: (APPLICATION-012 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-08",  # APPLICATION-005 §2 — Composition meta-class
    "APPLICATION-012",  # Universal Application Composition Architecture (UACpA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Composition construct reuses **directly** by reference
#: (UAL-02 / AMI-05). A Composition is the structural assembly relationship: it reuses
#: EL-1 (identity, value, typing, reference), RL-F2 (the composition-emit event behavior it
#: binds — §7), and PL-F2 (experience composition — PLATFORM-009/010, the AMR-12 binding it
#: reuses and re-founds NOT). It does **not** itself consume an SF-2 operation (AMR-13) or
#: present DF-2 data (AMR-14) — those are Feature/Capability concerns (AMC-04/02).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity)
    "ENG-004",  # Type      (typed, UAL-03 / CMP-01)
    "ENG-005",  # Relationship/Reference (member/assembled/composition refs; no new construct)
    "RL-F2",  # Runtime event (composition-emit, §7, by reference); none redefined
    "PL-F2",  # Platform experience composition (composed-as, AMR-12; PLATFORM-009/010); none redef
)

#: The prior CERTIFIED / frozen constructs the Composition reuses **by reference through
#: its relationships** (never redefined; reused only by reference — mission reuse list):
#:   AMC-01 (Application) — assembled-by / federated peer (AMR-07/AMR-02); the whole.
#:   AMC-03 (Module)      — assembled whole (Module-into-Application) or member; groups feats.
#:   AMC-04 (Feature)     — the constituent assembled into a module (Feature-into-Module).
#:   PL-F2                — the PLATFORM experience composition the composition is composed-as.
REFERENCED_UNITS: tuple[str, ...] = (
    "AMC-01",  # Universal Application root (EC3-B12-U01, CERTIFIED) — assembled/federated whole
    "AMC-03",  # Universal Module (EC3-B12-U03, CERTIFIED) — assembled whole / member
    "AMC-04",  # Universal Feature (EC3-B12-U04, CERTIFIED) — assembled member
    "PL-F2",  # PLATFORM experience composition (composed-as, AMR-12, by reference)
)

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Composition is AMC-08.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Composition meta-class id (APPLICATION-005 §2; APPLICATION-012).
COMPOSITION_META_CLASS = "AMC-08"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a Composition participates in (APPLICATION-012 §6/§16):
#:   AMR-02 composed-of   (Application → Module; founding, acyclic — reused by reference)
#:   AMR-03 groups        (Module → Feature; founding, acyclic — reused by reference)
#:   AMR-07 assembled-by  (Application/Module → Composition; the DEFINING relationship —
#:                         the Composition is the *target* that assembles; reference-only)
#:   AMR-10 identified-by (ENG-001 via ENG-002)
#:   AMR-12 composed-as   (PLATFORM composition PLATFORM-009/010, by reference)
COMPOSITION_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-02",
    "AMR-03",
    "AMR-07",
    "AMR-10",
    "AMR-12",
)


class CompositionKind(str, Enum):
    """AXH-08 Composition Hierarchy (APPLICATION-004 §3; APPLICATION-012 §5) — the
    classification of an application Composition.

    A Composition is classified by exactly one kind (single-facet, AXC-02 / AXC-04). The
    kind fixes which founding relationship the assembly reuses:
    """

    FEATURE_INTO_MODULE = "Feature-into-Module"  # assembles features into a module (founding)
    MODULE_INTO_APPLICATION = "Module-into-Application"  # assembles modules into an app (founding)
    APPLICATION_FEDERATION = "Application-Federation"  # peer composition of apps (reference)


#: AXH-08 kind → the assembly facet it classifies (APPLICATION-012 §5).
COMPOSITION_FACETS: dict[CompositionKind, str] = {
    CompositionKind.FEATURE_INTO_MODULE: "feature-into-module",
    CompositionKind.MODULE_INTO_APPLICATION: "module-into-application",
    CompositionKind.APPLICATION_FEDERATION: "application-federation",
}

#: AXH-08 kind → the founding meta-relationship the assembly reuses (APPLICATION-012 §6).
#: Feature-into-Module reuses AMR-03 groups; Module-into-Application reuses AMR-02
#: composed-of (both founding, acyclic). Application-Federation is **peer** (AMR-07,
#: reference-only) and participates in **no** founding edge (CMP-07 / CMP-C4).
COMPOSITION_FOUNDING_RELATIONSHIP: dict[CompositionKind, str] = {
    CompositionKind.FEATURE_INTO_MODULE: "AMR-03",
    CompositionKind.MODULE_INTO_APPLICATION: "AMR-02",
    CompositionKind.APPLICATION_FEDERATION: "AMR-07",
}

#: AXH-08 kind → whether the assembly is founding (a DAG edge) or peer (reference-only).
#: Founding kinds (Feature-into-Module, Module-into-Application) form the acyclic founding
#: graph (CMP-C1); Application-Federation is peer/by-reference (CMP-C4), non-founding.
COMPOSITION_IS_FOUNDING: dict[CompositionKind, bool] = {
    CompositionKind.FEATURE_INTO_MODULE: True,
    CompositionKind.MODULE_INTO_APPLICATION: True,
    CompositionKind.APPLICATION_FEDERATION: False,
}

#: AXH-08 kind → the minimum number of assembled constituents (topology decidability,
#: CMP-C4). Founding kinds assemble ≥1 constituent; federation composes ≥2 peer apps.
COMPOSITION_MIN_MEMBERS: dict[CompositionKind, int] = {
    CompositionKind.FEATURE_INTO_MODULE: 1,
    CompositionKind.MODULE_INTO_APPLICATION: 1,
    CompositionKind.APPLICATION_FEDERATION: 2,
}


class CompositionState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-012 §8) — the forward-only composition
    lifecycle states (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared (kind/members/assembled) but not composed
    COMPOSED = "COMPOSED"  # AOS-02 — constituents assembled by reference
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — assembly bound within an application context
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — assembled whole deliverable (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[CompositionState, ...] = (
    CompositionState.DEFINED,
    CompositionState.COMPOSED,
    CompositionState.CONTEXTUALIZED,
    CompositionState.EXECUTABLE,
    CompositionState.DEPRECATED,
    CompositionState.RETIRED,
)

# ---------------------------------------------------------------------------
# APPLICATION-012 §7 — Composition behavior binding (assemble / federate / emit)
# ---------------------------------------------------------------------------

#: The RUNTIME/PLATFORM behavior bindings a composition references (never re-implemented).
COMPOSITION_BEHAVIOR_BINDINGS: dict[str, str] = {
    "composition-assemble": "PLATFORM composition (assemble features/modules/applications, AOB-01)",
    "composition-federate": "PLATFORM composition (peer application federation)",
    "composition-emit": "RUNTIME event (signal a module-composed occurrence, AOV-02)",
}

# ---------------------------------------------------------------------------
# APPLICATION-012 §4 — Composition principles (CMP-01…10)
# ---------------------------------------------------------------------------

#: The ten Composition principles (APPLICATION-012 §4), each mapped to its short rule.
COMPOSITION_PRINCIPLES: dict[str, str] = {
    "CMP-01": "Every composition is classified by an ENG-004 Type; no untyped composition.",
    "CMP-02": "Every composition is an ENG-002 Object bearing an ENG-001 identity; no 2nd scheme.",
    "CMP-03": "Composition reuses PL-F2 composition (PLATFORM-009/010) + ENG-005 refs; refounds 0.",
    "CMP-04": "Composition introduces no new connection construct; all links are ENG-005 refs.",
    "CMP-05": "The founding structural graph (features→modules→applications) is a DAG.",
    "CMP-06": "Composition preserves module/feature boundaries; it absorbs no constituent id.",
    "CMP-07": "Application federation composes peer applications by reference, not by absorption.",
    "CMP-08": "New composition types append additively (AXH-08) without renumber or invalidation.",
    "CMP-09": "A composition confers no authority, embeds no secret, selects no technology.",
    "CMP-10": "Any consumed ARCH/CAT/REF/GEN/IMP/UKB asset is labelled INPUT, never COMPLETION.",
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

#: The Application laws the Composition construct is directly obligated by. **UAL-09
#: (composition reuses PL-F2/ENG-005 references with an acyclic founding graph) is THE
#: governing law** of AMC-08. A composition is also typed (UAL-03), identified/object-borne
#: (UAL-04/05), founded on the frozen substrate (UAL-01), reuse-integral (UAL-02), binds its
#: composition-emit behavior to RL-F2 by reference (UAL-10), has a forward-only recorded
#: lifecycle (UAL-12), and is non-constitutive (UAL-14/15). UAL-06/08 (feature capability
#: delivery + declaration), UAL-07 (a *module* is the bounded, cohesive grouping — the
#: governing law of AMC-03, distinct from the assembly relationship AMC-08 governs),
#: UAL-11 (interaction typedness), and UAL-13 (feature/interaction DF-2 data) are scoped to
#: the Feature/Module/Interaction units (AMC-03/04/06) and recorded not-applicable-to-
#: composition — a composition *assembles* what modules bound and features deliver.
COMPOSITION_APPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-01",
    "UAL-02",
    "UAL-03",
    "UAL-04",
    "UAL-05",
    "UAL-09",
    "UAL-10",
    "UAL-12",
    "UAL-14",
    "UAL-15",
)

#: Laws scoped to the Feature/Module/Interaction concerns (U03/U04/U06), N/A to Composition.
COMPOSITION_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-06",
    "UAL-07",
    "UAL-08",
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
    "V1": "Instantiates exactly one meta-class (Composition → AMC-08).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints a Composition is bound by (APPLICATION-005 §4; APPLICATION-012 §10
#: CMP-K1…K5). **AMK-03 (the founding meta-relationship graph AMR-02/03 is acyclic) is THE
#: materially-exercised constraint** — a Composition *is* the structural assembly, and its
#: founding graph (features→modules→applications) is proven a DAG at construction (CMP-C1 /
#: CMP-K3 / UAL-09, the governing condition). **AMK-06 (every composition reference
#: AMR-07/12 resolves to a PL-F2 construct; none redefined) is materially exercised**
#: (CMP-K4 / CMP-C5). AMK-01 (typed/identified/object) and AMK-02 (CMP-K2 analog: every
#: assembled constituent is declared and typed) are materially exercised. AMK-05 (the
#: composition-emit behavior binds an RL-F2 construct — §7) is exercised for the emit
#: binding. AMK-04 (a feature is engaged through an interaction before EXECUTABLE) is a
#: Feature (AMC-04) obligation — recorded not-applicable-to-composition; and AMK-07
#: (delivered-capability ref → SF-2, data ref → DF-2) is scoped to the Feature/Capability
#: units (a composition consumes no operation and presents no data) — recorded N/A.
COMPOSITION_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "AMK-02": "Every assembled constituent is declared and typed (CMP-K2 analog).",
    "AMK-03": "The founding meta-relationship graph (AMR-02/03) is acyclic (a DAG).",
    "AMK-05": "The composition-emit behavior reference resolves to an RL-F2 construct (§7).",
    "AMK-06": "Every composition reference (AMR-07/12) resolves to a PL-F2 construct; none redef.",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

#: Meta-constraints scoped to the Feature/Capability units (AMC-02/04), N/A to Composition.
COMPOSITION_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-04", "AMK-07")

#: The Composition assembly & federation rules (APPLICATION-012 §9; CMP-C1…C5).
COMPOSITION_ASSEMBLY_RULES: dict[str, str] = {
    "CMP-C1": "Founding composition (features→modules→applications) forms a DAG; no cycle.",
    "CMP-C2": "All composition links are ENG-005 references; no new connection construct.",
    "CMP-C3": "Composition preserves constituent boundaries and identities; it absorbs none.",
    "CMP-C4": "Application federation is by reference (peer), never by absorption.",
    "CMP-C5": "Composition reuses PL-F2 composition; it re-founds no platform concern.",
}

#: The Composition constraints (APPLICATION-012 §10; CMP-K1…K5).
COMPOSITION_CONSTRAINTS: dict[str, str] = {
    "CMP-K1": "Every composition is typed (ENG-004), identified (ENG-001), object-bound (ENG-002).",
    "CMP-K2": "Every assembled constituent is declared and typed.",
    "CMP-K3": "The founding composition graph is acyclic.",
    "CMP-K4": "Every composition reference resolves to a PL-F2 construct; none redefined.",
    "CMP-K5": "No composition selects technology or confers authority.",
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
    "COMPOSITION_META_CLASS",
    "META_RELATIONSHIPS",
    "COMPOSITION_RELATIONSHIPS",
    "CompositionKind",
    "COMPOSITION_FACETS",
    "COMPOSITION_FOUNDING_RELATIONSHIP",
    "COMPOSITION_IS_FOUNDING",
    "COMPOSITION_MIN_MEMBERS",
    "CompositionState",
    "LIFECYCLE_ORDER",
    "COMPOSITION_BEHAVIOR_BINDINGS",
    "COMPOSITION_PRINCIPLES",
    "APPLICATION_LAWS",
    "COMPOSITION_APPLICABLE_LAWS",
    "COMPOSITION_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "COMPOSITION_META_CONSTRAINTS",
    "COMPOSITION_INAPPLICABLE_CONSTRAINTS",
    "COMPOSITION_ASSEMBLY_RULES",
    "COMPOSITION_CONSTRAINTS",
    "CCE_GATES",
]
