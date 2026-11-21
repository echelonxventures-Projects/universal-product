"""EC3-B12-U02 — Capability meta-model constants (read-only projections of
APPLICATION-001/003/004/005/006).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen Capability
Architecture (APPLICATION-006, AMC-02) that the Universal Capability realization must
conform to. It **defines no new law and redefines no foundation concept**
(UAL-02 / AMI-05 / UAL-15); it only names the frozen obligations so the realization can
be checked against them deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification
at the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 02) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 02).
REALIZATION_UNIT = "EC3-B12-U02"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-AP-4 §5/§9)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 12-APPLICATION/ specification commit.
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the certified baseline this builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` CERTIFIED-COMPLETE + FROZEN + the
#: CERTIFIED Band-12 U01 Universal Application root ``application.application`` at HEAD
#: ``53d1301``).
IMPLEMENTATION_ANCHOR = "53d1301"

#: The backward traceability chain every realized Capability records
#: (APPLICATION-006 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-02",  # APPLICATION-005 §2 — Capability meta-class
    "APPLICATION-006",  # Universal Application Capability Architecture (UACA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Capability reuses by reference (UAL-02 / AMI-05).
#:   ENG-001…005 (EL-1) · RL-F2 (behavior) · PL-F2 (experience composition,
#:   PLATFORM-006/009) · SF-2 (contracted operation) · DF-2 (represented data).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity)
    "ENG-004",  # Type      (typed, UAL-03)
    "ENG-005",  # Relationship/Reference (composition/reference, AMR-12)
    "RL-F2",  # Runtime behavior (behaves-as, AMR-11)
    "PL-F2",  # Platform experience composition (composed-as, AMR-12; PLATFORM-006/009)
    "SF-2",  # Contracted operation (consumes-operation, AMR-13)
    "DF-2",  # Represented data (presents-data, AMR-14)
)

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Capability is AMC-02.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Capability meta-class id (APPLICATION-005 §2; APPLICATION-006).
CAPABILITY_META_CLASS = "AMC-02"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a Capability participates in (APPLICATION-006 §6/§16):
#:   AMR-01 delivers          (Application → Capability; the capability is delivered)
#:   AMR-10 identified-by     (ENG-001 via ENG-002)
#:   AMR-11 behaves-as        (RUNTIME construct: deliver/transact/emit, by reference)
#:   AMR-12 composed-as       (PLATFORM composition PLATFORM-006/009, by reference)
#:   AMR-13 consumes-operation(SF-2 SERVICE operation, by reference — CAP-05)
#:   AMR-14 presents-data     (DF-2 DATA, by reference — CAP-07)
CAPABILITY_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-01",
    "AMR-10",
    "AMR-11",
    "AMR-12",
    "AMR-13",
    "AMR-14",
)


class CapabilityKind(str, Enum):
    """AXH-02 Capability Hierarchy (APPLICATION-004 §3; APPLICATION-006 §5) — the
    classification of an application Capability.

    A Capability is classified by exactly one kind (single-facet, AXC-02):
    """

    FUNCTIONAL = "Functional-Capability"  # delivers domain work to an actor
    INFORMATIONAL = "Informational-Capability"  # delivers retrieved/derived data (read-side)
    TRANSACTIONAL = "Transactional-Capability"  # delivers an intended state change (write-side)


class CapabilityState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-006 §8) — the forward-only capability
    lifecycle states (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared but not yet composed
    COMPOSED = "COMPOSED"  # AOS-02 — delivering features assembled (bound by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — context/state bound (actor/session/tenant)
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — delivered by a feature; deliverable (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[CapabilityState, ...] = (
    CapabilityState.DEFINED,
    CapabilityState.COMPOSED,
    CapabilityState.CONTEXTUALIZED,
    CapabilityState.EXECUTABLE,
    CapabilityState.DEPRECATED,
    CapabilityState.RETIRED,
)

#: Read-side capability kinds (deliver represented data) — CAP-C5 separation.
READ_SIDE_KINDS: frozenset[CapabilityKind] = frozenset({CapabilityKind.INFORMATIONAL})

#: Write-side capability kinds (deliver an intended state change) — CAP-C5 separation.
WRITE_SIDE_KINDS: frozenset[CapabilityKind] = frozenset({CapabilityKind.TRANSACTIONAL})

# ---------------------------------------------------------------------------
# APPLICATION-006 §7 — Capability behavior binding (deliver / transact / emit)
# ---------------------------------------------------------------------------

#: The RUNTIME/SF-2 behavior bindings a capability references (never re-implemented).
CAPABILITY_BEHAVIOR_BINDINGS: dict[str, str] = {
    "capability-deliver": "SF-2 operation invocation (deliver the ability by consuming a contract)",
    "capability-transact": "RUNTIME workflow + SF-2 orchestration (multi-step delivered work)",
    "capability-emit": "RUNTIME event (signal a capability-delivered occurrence, AOV-06)",
}

# ---------------------------------------------------------------------------
# APPLICATION-006 §4 — Capability principles (CAP-01…10)
# ---------------------------------------------------------------------------

#: The ten Capability principles (APPLICATION-006 §4), each mapped to its short rule.
CAPABILITY_PRINCIPLES: dict[str, str] = {
    "CAP-01": "Every application capability is classified by an ENG-004 Type; none untyped.",
    "CAP-02": "Every capability is an ENG-002 Object bearing an ENG-001 identity; no 2nd scheme.",
    "CAP-03": "Capability reuses the PLATFORM-006 / SF-2 capability construct by reference.",
    "CAP-04": "A capability is delivered to an actor by the application through features.",
    "CAP-05": "Capability is realized only by features consuming SF-2 operations under contract.",
    "CAP-06": "A capability declares an explicit, decidable scope of delivered ability.",
    "CAP-07": "A capability's delivered data references DF-2 constructs by reference.",
    "CAP-08": "New capability types append additively (AXH-02) without renumber/invalidation.",
    "CAP-09": "A capability confers no authority, embeds no secret, selects no technology.",
    "CAP-10": "Any consumed ARCH/CAT/REF/GEN/IMP/UKB asset is labelled INPUT, never COMPLETION.",
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

#: The Application laws the Capability construct is directly obligated by. A capability
#: consumes SF-2 operations (UAL-06 via AMR-13), declares an explicit bounded scope
#: (UAL-08), and references DF-2 data (UAL-13 via AMR-14) — so UAL-06/08/13 apply here
#: (unlike the atomic Application root U01). UAL-07 (module cohesion) and UAL-11
#: (interaction typedness) are scoped to the Module/Interaction units (AMC-03/06).
CAPABILITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-01",
    "UAL-02",
    "UAL-03",
    "UAL-04",
    "UAL-05",
    "UAL-06",
    "UAL-08",
    "UAL-09",
    "UAL-10",
    "UAL-12",
    "UAL-13",
    "UAL-14",
    "UAL-15",
)

#: Laws scoped to the Module/Interaction concerns (U03/U06), N/A to the Capability.
CAPABILITY_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-07",
    "UAL-11",
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
    "V1": "Instantiates exactly one meta-class (Capability → AMC-02).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints a Capability is bound by (APPLICATION-005 §4; APPLICATION-006 §10).
#: AMK-07 (delivered-capability reference resolves to SF-2 operation, data reference to
#: DF-2, none redefined) IS applicable to the Capability — it consumes SF-2 operations
#: (AMR-13) and presents DF-2 data (AMR-14). AMK-02 (feature declares capability + typed
#: I/O + interactions) and AMK-04 (feature engaged through interaction before EXECUTABLE)
#: are scoped to the Feature/Interaction units (AMC-04/06) and recorded N/A-to-capability.
CAPABILITY_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "AMK-03": "The founding meta-relationship graph (AMR-02/03/05) is acyclic (a DAG).",
    "AMK-05": "Every behavior/state ref (AMR-06/11) resolves to an RL-F2 construct; none redef.",
    "AMK-06": "Every composition reference (AMR-07/12) resolves to a PL-F2 construct; none redef.",
    "AMK-07": "Delivered-capability ref (AMR-13) resolves to an SF-2 operation and data ref "
    "(AMR-14) to a DF-2 construct; none redefined; security/governance meta-objects declarative.",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

#: Meta-constraints scoped to the Feature/Interaction units (AMC-04/06), N/A to the
#: Capability.
CAPABILITY_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-02", "AMK-04")

#: The Capability boundary & delivery rules (APPLICATION-006 §9).
CAPABILITY_DELIVERY_RULES: dict[str, str] = {
    "CAP-C1": "Scope of delivered ability is explicit, typed, decidable; closed at declaration.",
    "CAP-C2": "Delivered by ≥1 feature (AOR-01 via AOR-03/13); delivery does not absorb identity.",
    "CAP-C3": "Founding relations form a DAG; no capability founds itself transitively (AMK-03).",
    "CAP-C4": "A capability's delivered data references (does not embed) DF-2 data (AOR-14).",
    "CAP-C5": "Informational/Transactional separate read-side and write-side delivery.",
}

#: The CCE ten-gate identifiers (EC-3 AP-4 certification strategy, CC-1…CC-10).
CCE_GATES: tuple[str, ...] = tuple(f"CC-{n}" for n in range(1, 11))

__all__ = [
    "REALIZATION_UNIT",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "TRACE_BACKWARD",
    "SUBSTRATE_REFS",
    "META_CLASSES",
    "CAPABILITY_META_CLASS",
    "META_RELATIONSHIPS",
    "CAPABILITY_RELATIONSHIPS",
    "CapabilityKind",
    "CapabilityState",
    "LIFECYCLE_ORDER",
    "READ_SIDE_KINDS",
    "WRITE_SIDE_KINDS",
    "CAPABILITY_BEHAVIOR_BINDINGS",
    "CAPABILITY_PRINCIPLES",
    "APPLICATION_LAWS",
    "CAPABILITY_APPLICABLE_LAWS",
    "CAPABILITY_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "CAPABILITY_META_CONSTRAINTS",
    "CAPABILITY_INAPPLICABLE_CONSTRAINTS",
    "CAPABILITY_DELIVERY_RULES",
    "CCE_GATES",
]
