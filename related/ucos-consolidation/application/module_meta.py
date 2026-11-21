"""EC3-B12-U03 — Module meta-model constants (read-only projections of
APPLICATION-001/003/004/005/007).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen Module
Architecture (APPLICATION-007, AMC-03) that the Universal Module realization must
conform to. It **defines no new law and redefines no foundation concept**
(UAL-02 / AMI-05 / UAL-15); it only names the frozen obligations so the realization can
be checked against them deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification
at the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 03) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 03).
REALIZATION_UNIT = "EC3-B12-U03"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-AP-4 §5/§9)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 12-APPLICATION/ specification commit.
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the certified baseline this builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` CERTIFIED-COMPLETE + FROZEN + the
#: CERTIFIED Band-12 U01 Universal Application root ``application.application`` + the
#: CERTIFIED Band-12 U02 Universal Capability ``application.capability`` at HEAD
#: ``6051820``).
IMPLEMENTATION_ANCHOR = "6051820"

#: The backward traceability chain every realized Module records
#: (APPLICATION-007 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-03",  # APPLICATION-005 §2 — Module meta-class
    "APPLICATION-007",  # Universal Application Module Architecture (UAMA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Module construct reuses **directly** by reference
#: (UAL-02 / AMI-05). A Module is a structural grouping unit: it reuses EL-1 (identity,
#: value, typing, reference), RL-F2 (lifecycle transition / event behavior — §7), and
#: PL-F2 (experience composition — PLATFORM-009/010). It does **not** itself consume an
#: SF-2 operation or present DF-2 data — those are Feature/Capability concerns
#: (AMC-04/02); see :data:`REFERENCED_UNITS`.
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity)
    "ENG-004",  # Type      (typed, UAL-03)
    "ENG-005",  # Relationship/Reference (composition/reference, AMR-02/03/07/12)
    "RL-F2",  # Runtime behavior (module-transition / module-emit, §7, by reference)
    "PL-F2",  # Platform experience composition (composed-as, AMR-12; PLATFORM-009/010)
)

#: The prior CERTIFIED / frozen constructs the Module reuses **by reference through its
#: relationships** (never redefined; reused only by reference — mission reuse list):
#:   AMC-01 (Application) — composed-into (AMR-02); the Module is composed by an Application.
#:   AMC-02 (Capability)  — the ability the grouped Features (AMC-04) deliver.
#:   SF-2 / DF-2          — consumed/presented by the grouped Features, not by the Module.
REFERENCED_UNITS: tuple[str, ...] = (
    "AMC-01",  # Universal Application root (EC3-B12-U01, CERTIFIED) — composed-of parent
    "AMC-02",  # Universal Capability (EC3-B12-U02, CERTIFIED) — delivered by grouped features
    "SF-2",  # Contracted operation — consumed by grouped features (AMC-04), not the module
    "DF-2",  # Represented data — presented by grouped features (AMC-04), not the module
)

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Module is AMC-03.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Module meta-class id (APPLICATION-005 §2; APPLICATION-007).
MODULE_META_CLASS = "AMC-03"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a Module participates in (APPLICATION-007 §6/§16):
#:   AMR-02 composed-of     (Application → Module; the module is composed into an app)
#:   AMR-03 groups          (Module → Feature; the DEFINING relationship — MOD-07)
#:   AMR-07 assembled-by    (Application/Module → Composition; reference-only)
#:   AMR-10 identified-by   (ENG-001 via ENG-002)
#:   AMR-12 composed-as     (PLATFORM composition PLATFORM-009/010, by reference)
MODULE_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-02",
    "AMR-03",
    "AMR-07",
    "AMR-10",
    "AMR-12",
)


class ModuleKind(str, Enum):
    """AXH-03 Module Hierarchy (APPLICATION-004 §3; APPLICATION-007 §5) — the
    classification of an application Module.

    A Module is classified by exactly one kind (single-facet, AXC-02):
    """

    CORE = "Core-Module"  # owns primary features of the application
    SUPPORTING = "Supporting-Module"  # owns auxiliary / cross-cutting features
    EXTENSION = "Extension-Module"  # additively adds features to an application (acyclic)


class ModuleState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-007 §8) — the forward-only module
    lifecycle states (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared with a boundary but not yet composed
    COMPOSED = "COMPOSED"  # AOS-02 — features assembled into the module (by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — composed into an application context
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — bounded, cohesive, deliverable (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[ModuleState, ...] = (
    ModuleState.DEFINED,
    ModuleState.COMPOSED,
    ModuleState.CONTEXTUALIZED,
    ModuleState.EXECUTABLE,
    ModuleState.DEPRECATED,
    ModuleState.RETIRED,
)

# ---------------------------------------------------------------------------
# APPLICATION-007 §7 — Module behavior binding (compose / transition / emit)
# ---------------------------------------------------------------------------

#: The RUNTIME/PLATFORM behavior bindings a module references (never re-implemented).
MODULE_BEHAVIOR_BINDINGS: dict[str, str] = {
    "module-compose": "PLATFORM composition (assemble features into a module; module into app)",
    "module-transition": "RUNTIME state (module lifecycle transition, RL-F2)",
    "module-emit": "RUNTIME event (signal a module-composed occurrence, AOV-02)",
}

# ---------------------------------------------------------------------------
# APPLICATION-007 §4 — Module principles (MOD-01…10)
# ---------------------------------------------------------------------------

#: The ten Module principles (APPLICATION-007 §4), each mapped to its short rule.
MODULE_PRINCIPLES: dict[str, str] = {
    "MOD-01": "Every module is classified by an ENG-004 Type; no untyped module exists.",
    "MOD-02": "Every module is an ENG-002 Object bearing an ENG-001 identity; no 2nd scheme.",
    "MOD-03": "Every module declares an explicit, decidable boundary and the features it owns.",
    "MOD-04": "A module groups features that share a cohesive purpose; unrelated do not co-reside.",
    "MOD-05": "No module owns a feature across another boundary; feature ownership is a partition.",
    "MOD-06": "A module composes into an application via ENG-005/PL-F2 refs; founding acyclic.",
    "MOD-07": "Every feature belongs to exactly one owning module (AOR-03).",
    "MOD-08": "New module types append additively (AXH-03) without renumber or invalidation.",
    "MOD-09": "A module confers no authority, embeds no secret, selects no technology.",
    "MOD-10": "Any consumed ARCH/CAT/REF/GEN/IMP/UKB asset is labelled INPUT, never COMPLETION.",
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

#: The Application laws the Module construct is directly obligated by. A module is the
#: bounded, cohesive grouping of features (UAL-07 — the governing law), composes by
#: reference with an acyclic founding graph (UAL-09), binds lifecycle/behavior to RL-F2
#: by reference (UAL-10/12), and is non-constitutive (UAL-14/15). UAL-06/08 (feature
#: capability delivery + declaration), UAL-11 (interaction typedness), and UAL-13
#: (feature/interaction DF-2 data) are scoped to the Feature/Interaction units
#: (AMC-04/06) and recorded not-applicable-to-module.
MODULE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-01",
    "UAL-02",
    "UAL-03",
    "UAL-04",
    "UAL-05",
    "UAL-07",
    "UAL-09",
    "UAL-10",
    "UAL-12",
    "UAL-14",
    "UAL-15",
)

#: Laws scoped to the Feature/Interaction concerns (U04/U06), N/A to the Module.
MODULE_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-06",
    "UAL-08",
    "UAL-11",
    "UAL-13",
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
    "V1": "Instantiates exactly one meta-class (Module → AMC-03).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints a Module is bound by (APPLICATION-005 §4; APPLICATION-007 §10).
#: AMK-02 (feature declares capability + SF-2 ops + typed I/O + interactions), AMK-04
#: (feature engaged through an interaction before EXECUTABLE), and AMK-07
#: (delivered-capability ref → SF-2, data ref → DF-2) are scoped to the Feature/Capability
#: units (AMC-02/04) and recorded not-applicable-to-module — a module groups features but
#: consumes no operation and presents no data itself.
MODULE_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "AMK-03": "The founding meta-relationship graph (AMR-02/03) is acyclic (a DAG).",
    "AMK-05": "Every behavior/state ref (module-transition/emit) resolves to an RL-F2 construct.",
    "AMK-06": "Every composition reference (AMR-07/12) resolves to a PL-F2 construct; none redef.",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

#: Meta-constraints scoped to the Feature/Capability units (AMC-02/04), N/A to the Module.
MODULE_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-02", "AMK-04", "AMK-07")

#: The Module boundary & cohesion rules (APPLICATION-007 §9).
MODULE_BOUNDARY_RULES: dict[str, str] = {
    "MOD-C1": "Boundary is explicit, typed, decidable; owned features enumerated at declaration.",
    "MOD-C2": "Feature ownership is a partition: each feature has exactly one owning module.",
    "MOD-C3": "Founding relations (composed-of, groups) form a DAG; no transitive self-founding.",
    "MOD-C4": "A module composes into applications by reference; composition absorbs no feature.",
    "MOD-C5": "Extension-modules add features additively without renumbering existing modules.",
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
    "MODULE_META_CLASS",
    "META_RELATIONSHIPS",
    "MODULE_RELATIONSHIPS",
    "ModuleKind",
    "ModuleState",
    "LIFECYCLE_ORDER",
    "MODULE_BEHAVIOR_BINDINGS",
    "MODULE_PRINCIPLES",
    "APPLICATION_LAWS",
    "MODULE_APPLICABLE_LAWS",
    "MODULE_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "MODULE_META_CONSTRAINTS",
    "MODULE_INAPPLICABLE_CONSTRAINTS",
    "MODULE_BOUNDARY_RULES",
    "CCE_GATES",
]
