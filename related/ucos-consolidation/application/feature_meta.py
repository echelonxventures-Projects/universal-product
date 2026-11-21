"""EC3-B12-U04 — Feature meta-model constants (read-only projections of
APPLICATION-001/003/004/005/008).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen Feature
Architecture (APPLICATION-008, AMC-04) that the Universal Feature realization must
conform to. It **defines no new law and redefines no foundation concept**
(UAL-02 / AMI-05 / UAL-15); it only names the frozen obligations so the realization can
be checked against them deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification
at the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 04) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 04).
REALIZATION_UNIT = "EC3-B12-U04"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-AP-4 §5/§9)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 12-APPLICATION/ specification commit.
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the certified baseline this builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` CERTIFIED-COMPLETE + FROZEN + the
#: CERTIFIED Band-12 U01 Universal Application root ``application.application`` + the
#: CERTIFIED Band-12 U02 Universal Capability ``application.capability`` + the CERTIFIED
#: Band-12 U03 Universal Module ``application.module`` at HEAD ``afeae55``).
IMPLEMENTATION_ANCHOR = "afeae55"

#: The backward traceability chain every realized Feature records
#: (APPLICATION-008 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-04",  # APPLICATION-005 §2 — Feature meta-class
    "APPLICATION-008",  # Universal Application Feature Architecture (UAFA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Feature construct reuses **directly** by reference
#: (UAL-02 / AMI-05). A Feature is the load-bearing unit of experience-over-operation: it
#: reuses EL-1 (identity, value, typing, reference), RL-F2 (invoke/sequence/interact/emit
#: behavior — §7), SF-2 (the operations it consumes under contract — AMR-13), and DF-2
#: (the typed I/O and presented data it references — AMR-14). It does **not** itself
#: assemble a PLATFORM experience composition (AMR-07/12) — that is the Module/Application
#: concern (AMC-01/03).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity; typed I/O)
    "ENG-004",  # Type      (typed, UAL-03)
    "ENG-005",  # Relationship/Reference (composition/reference, AMR-01/03/05/13/14)
    "RL-F2",  # Runtime behavior (feature-invoke/sequence/interact/emit, §7, by reference)
    "SF-2",  # Contracted operation (consumes-operation, AMR-13; §7 feature-invoke)
    "DF-2",  # Represented data (presents-data, AMR-14; typed I/O)
)

#: The prior CERTIFIED / frozen constructs the Feature reuses **by reference through its
#: relationships** (never redefined; reused only by reference — mission reuse list):
#:   AMC-02 (Capability)  — delivered by the feature (AMR-01 delivers, for the Application).
#:   AMC-03 (Module)      — owns the feature (AMR-03 groups; the feature belongs to one).
#:   AMC-06 (Interaction) — the feature is engaged-through it (AMR-05; reference-only —
#:                          Interaction is a downstream Band-12 unit, referenced by id).
#:   SF-2 / DF-2          — consumed operations + presented data (AMR-13/14).
REFERENCED_UNITS: tuple[str, ...] = (
    "AMC-02",  # Universal Capability (EC3-B12-U02, CERTIFIED) — delivered by the feature
    "AMC-03",  # Universal Module (EC3-B12-U03, CERTIFIED) — owning module (groups AMR-03)
    "AMC-06",  # Universal Interaction (downstream) — engaged-through (AMR-05, by reference)
    "SF-2",  # Contracted operation(s) consumed by the feature (AMR-13)
    "DF-2",  # Represented data presented by the feature (AMR-14)
)

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Feature is AMC-04.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Feature meta-class id (APPLICATION-005 §2; APPLICATION-008).
FEATURE_META_CLASS = "AMC-04"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a Feature participates in (APPLICATION-008 §6/§16):
#:   AMR-01 delivers          (Feature, for Application → Capability; reference-only)
#:   AMR-03 groups            (Module → Feature; the feature belongs to exactly one module)
#:   AMR-05 engaged-through   (Feature → Interaction; founding, acyclic — the NEW relationship)
#:   AMR-10 identified-by     (ENG-001 via ENG-002)
#:   AMR-11 behaves-as        (RUNTIME construct: invoke/sequence/interact/emit, by reference)
#:   AMR-13 consumes-operation(SF-2 SERVICE operation(s), by reference — FEA-04, the defining rel)
#:   AMR-14 presents-data     (DF-2 DATA, by reference — FEA-05)
FEATURE_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-01",
    "AMR-03",
    "AMR-05",
    "AMR-10",
    "AMR-11",
    "AMR-13",
    "AMR-14",
)


class FeatureKind(str, Enum):
    """AXH-04 Feature Hierarchy (APPLICATION-004 §3; APPLICATION-008 §5) — the
    classification of an application Feature.

    A Feature is classified by exactly one kind (single-facet, AXC-02 / AXC-04):
    """

    QUERY = "Query-Feature"  # composes read-side SF-2 operations (no represented state change)
    COMMAND = "Command-Feature"  # composes write-side SF-2 operations (intends state change)
    COMPOSITE = "Composite-Feature"  # composes multiple SF-2 operations toward one capability


class FeatureState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-008 §8) — the forward-only feature
    lifecycle states (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared (capability/ops/I-O/interaction) but not composed
    COMPOSED = "COMPOSED"  # AOS-02 — composed operations assembled (bound by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — engaged through an interaction (actor context)
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — engaged + deliverable (authoritative; AMK-04 gate)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[FeatureState, ...] = (
    FeatureState.DEFINED,
    FeatureState.COMPOSED,
    FeatureState.CONTEXTUALIZED,
    FeatureState.EXECUTABLE,
    FeatureState.DEPRECATED,
    FeatureState.RETIRED,
)

#: The lifecycle states at (or past) which a feature must be engaged through an
#: interaction (AMK-04 / FEA-06 / FEA-K3: engaged before EXECUTABLE).
ENGAGED_REQUIRED_STATES: frozenset[FeatureState] = frozenset(
    {FeatureState.EXECUTABLE, FeatureState.DEPRECATED, FeatureState.RETIRED}
)

#: Read-side feature kinds (compose read-side operations; no represented state change) —
#: FEA-C5 separation.
READ_SIDE_KINDS: frozenset[FeatureKind] = frozenset({FeatureKind.QUERY})

#: Write-side feature kinds (intend a represented state change) — FEA-C5 separation.
WRITE_SIDE_KINDS: frozenset[FeatureKind] = frozenset({FeatureKind.COMMAND})

#: Feature kinds that must compose more than one operation (AXH-04 Composite; FEA-C5).
MULTI_OPERATION_KINDS: frozenset[FeatureKind] = frozenset({FeatureKind.COMPOSITE})

# ---------------------------------------------------------------------------
# APPLICATION-008 §7 — Feature behavior binding (invoke / sequence / interact / emit)
# ---------------------------------------------------------------------------

#: The RUNTIME/SF-2 behavior bindings a feature references (never re-implemented).
FEATURE_BEHAVIOR_BINDINGS: dict[str, str] = {
    "feature-invoke": "SF-2 operation (deliver capability by consuming a contract, AOB-02)",
    "feature-sequence": "RUNTIME workflow + SF-2 orchestration (order composed operations, AOB-04)",
    "feature-interact": "RUNTIME event + state (engage the actor through an interaction, AOB-03)",
    "feature-emit": "RUNTIME event (signal a capability-delivered occurrence, AOV-06)",
}

# ---------------------------------------------------------------------------
# APPLICATION-008 §4 — Feature principles (FEA-01…10)
# ---------------------------------------------------------------------------

#: The ten Feature principles (APPLICATION-008 §4), each mapped to its short rule.
FEATURE_PRINCIPLES: dict[str, str] = {
    "FEA-01": "Every feature is classified by an ENG-004 Type; no untyped feature exists.",
    "FEA-02": "Every feature is an ENG-002 Object bearing an ENG-001 identity; no 2nd scheme.",
    "FEA-03": "Every feature declares capability, composed operations, typed I/O, interactions.",
    "FEA-04": "A feature delivers capability only by consuming SF-2 operations under contract.",
    "FEA-05": "A feature's inputs/outputs/presented data are DF-2 constructs by reference.",
    "FEA-06": "Every feature is engaged through a declared, typed interaction before EXECUTABLE.",
    "FEA-07": "Every feature belongs to exactly one owning module (AOR-03).",
    "FEA-08": "New feature types append additively (AXH-04) without renumber or invalidation.",
    "FEA-09": "A feature confers no authority, embeds no secret, selects no technology.",
    "FEA-10": "Any consumed ARCH/CAT/REF/GEN/IMP/UKB asset is labelled INPUT, never COMPLETION.",
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

#: The Application laws the Feature construct is directly obligated by. The Feature is the
#: **load-bearing unit of experience-over-operation** and is the single construct where
#: **every one of UAL-01…15 applies**: it delivers capability by consuming SF-2 operations
#: (UAL-06 — the governing law, FEA-04), declares its full contract (UAL-08 — the governing
#: law, FEA-03), is engaged through a typed interaction (UAL-11, FEA-06), belongs to exactly
#: one module (UAL-07, FEA-07), references DF-2 data (UAL-13, FEA-05), binds RL-F2 behavior
#: (UAL-10), composes acyclically by reference (UAL-09), and is non-constitutive (UAL-14/15).
FEATURE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-01",
    "UAL-02",
    "UAL-03",
    "UAL-04",
    "UAL-05",
    "UAL-06",
    "UAL-07",
    "UAL-08",
    "UAL-09",
    "UAL-10",
    "UAL-11",
    "UAL-12",
    "UAL-13",
    "UAL-14",
    "UAL-15",
)

#: No Application law is scoped-out for the Feature — it exercises all fifteen.
FEATURE_INAPPLICABLE_LAWS: tuple[str, ...] = ()

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
    "V1": "Instantiates exactly one meta-class (Feature → AMC-04).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints a Feature is bound by (APPLICATION-005 §4; APPLICATION-008 §10).
#: **AMK-02 (feature declares capability + SF-2 ops + typed I/O + interactions) and AMK-04
#: (feature engaged through an interaction before EXECUTABLE) are materially exercised at
#: the Feature level** — they are THE defining feature meta-constraints. AMK-07
#: (delivered-capability ref → SF-2 operation, data ref → DF-2) is also materially exercised
#: (the feature consumes SF-2 operations AMR-13 and presents DF-2 data AMR-14). AMK-06
#: (composition ref AMR-07/12 → PL-F2) is scoped to the Module/Application units (AMC-01/03):
#: a feature is *engaged through an interaction* and *grouped by a module*, but assembles no
#: PLATFORM composition itself — recorded not-applicable-to-feature.
FEATURE_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "AMK-02": "Feature declares delivered capability (AMR-01), composed SF-2 operations "
    "(AMR-13), typed I/O (DF-2 by reference, AMR-14), and its interactions (AMR-05).",
    "AMK-03": "The founding meta-relationship graph (AMR-02/03/05) is acyclic (a DAG).",
    "AMK-04": "Every feature is engaged through an interaction (AMR-05) before EXECUTABLE.",
    "AMK-05": "Every behavior/state ref (AMR-11) resolves to an RL-F2 construct; none redef.",
    "AMK-07": "Delivered-capability ref (AMR-13) resolves to an SF-2 operation and data ref "
    "(AMR-14) to a DF-2 construct; none redefined; security/governance meta-objects declarative.",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

#: Meta-constraints scoped to the Module/Application units (AMC-01/03), N/A to the Feature.
FEATURE_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-06",)

#: The Feature declaration & delivery rules (APPLICATION-008 §9).
FEATURE_DECLARATION_RULES: dict[str, str] = {
    "FEA-C1": "Declaration complete: delivered capability, composed SF-2 operations, typed "
    "I/O, and interactions are all explicit (UAL-08).",
    "FEA-C2": "Delivers capability only by consuming SF-2 operations under contract; "
    "re-founds no service (UAL-06).",
    "FEA-C3": "Founding relations (groups, engaged-through) form a DAG (AMK-03).",
    "FEA-C4": "I/O and presented data reference (do not embed) DF-2 data (AOR-14).",
    "FEA-C5": "Query/Command features separate read-side and write-side delivery; neither "
    "redefines a data, service, or runtime concern.",
}

#: The Feature constraints (APPLICATION-008 §10; FEA-K1…K5).
FEATURE_CONSTRAINTS: dict[str, str] = {
    "FEA-K1": "Every feature is typed (ENG-004), identified (ENG-001), object-bound (ENG-002).",
    "FEA-K2": "Every feature declares capability, composed operations, typed I/O, interactions.",
    "FEA-K3": "Every feature is engaged through an interaction before EXECUTABLE.",
    "FEA-K4": "Every operation reference resolves to an SF-2 operation and every data reference "
    "to a DF-2 construct; none redefined.",
    "FEA-K5": "No feature selects technology or confers authority.",
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
    "FEATURE_META_CLASS",
    "META_RELATIONSHIPS",
    "FEATURE_RELATIONSHIPS",
    "FeatureKind",
    "FeatureState",
    "LIFECYCLE_ORDER",
    "ENGAGED_REQUIRED_STATES",
    "READ_SIDE_KINDS",
    "WRITE_SIDE_KINDS",
    "MULTI_OPERATION_KINDS",
    "FEATURE_BEHAVIOR_BINDINGS",
    "FEATURE_PRINCIPLES",
    "APPLICATION_LAWS",
    "FEATURE_APPLICABLE_LAWS",
    "FEATURE_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "FEATURE_META_CONSTRAINTS",
    "FEATURE_INAPPLICABLE_CONSTRAINTS",
    "FEATURE_DECLARATION_RULES",
    "FEATURE_CONSTRAINTS",
    "CCE_GATES",
]
