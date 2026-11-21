"""EC3-B12-U01 — Application meta-model constants (read-only projections of
APPLICATION-001/003/004/005).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) that the Universal Application
realization must conform to. It **defines no new law and redefines no foundation
concept** (UAL-02 / AMI-05 / UAL-15); it only names the frozen obligations so the
realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification
at the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-AP-4 §5/§9)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 12-APPLICATION/ specification commit.
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the certified baseline this builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` CERTIFIED-COMPLETE + FROZEN at HEAD
#: ``3899a1f``).
IMPLEMENTATION_ANCHOR = "3899a1f"

#: The backward traceability chain every realized Application records
#: (APPLICATION-005 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-01",  # APPLICATION-005 §2 — Application meta-class (root)
    "APPLICATION-005",  # Universal Application Meta-Model
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Application reuses by reference (UAL-02 / AMI-05).
#:   ENG-001…005 (EL-1) · RL-F2 (behavior/state) · PL-F2 (experience composition) ·
#:   DF-2 (represented data) · SF-2 (contracted operation).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity)
    "ENG-004",  # Type      (typed, UAL-03)
    "ENG-005",  # Relationship/Reference (composition/reference, AMR-02/12)
    "RL-F2",  # Runtime behavior/state (behaves-as / holds-state, AMR-11/06)
    "PL-F2",  # Platform experience composition (composed-as, AMR-12; PLATFORM-009)
    "DF-2",  # Represented data (presents-data, AMR-14; scoped to the Feature unit)
    "SF-2",  # Contracted operation (consumes-operation, AMR-13; scoped to Feature)
)

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Application is AMC-01.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Application meta-class id (APPLICATION-005 §2).
APPLICATION_META_CLASS = "AMC-01"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a standalone Application root intrinsically participates in
#: (APPLICATION-003 §3; all reference-only, requiring no realized peer at U01):
#:   AMR-01 delivers      (Application → Capability, by reference)
#:   AMR-10 identified-by (ENG-001 via ENG-002)
#:   AMR-11 behaves-as    (RUNTIME construct: state/interaction/workflow, by reference)
#:   AMR-12 composed-as   (PLATFORM experience composition, by reference; PLATFORM-009)
APPLICATION_RELATIONSHIPS: tuple[str, ...] = ("AMR-01", "AMR-10", "AMR-11", "AMR-12")


class ApplicationKind(str, Enum):
    """AXH-01 Application Hierarchy (APPLICATION-004 §3) — the classification of an
    Application.

    An Application is classified by exactly one kind (single-facet, AXC-02):
    """

    SINGLE_MODULE = "Single-Module-Application"  # delivers capability via one module
    COMPOSITE = "Composite-Application"  # composed from multiple modules (AOR-02)
    FEDERATED = "Federated-Application"  # composes bounded sub-applications (peer)


class ApplicationState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4) — the forward-only application lifecycle states
    (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared but not yet composed
    COMPOSED = "COMPOSED"  # AOS-02 — modules/features assembled (bound by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — context/state bound (actor/session/tenant)
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — composed, contextualized, deliverable (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[ApplicationState, ...] = (
    ApplicationState.DEFINED,
    ApplicationState.COMPOSED,
    ApplicationState.CONTEXTUALIZED,
    ApplicationState.EXECUTABLE,
    ApplicationState.DEPRECATED,
    ApplicationState.RETIRED,
)

# ---------------------------------------------------------------------------
# APPLICATION-001 §7 — Application Laws (UAL-01…15) and §12 — Compliance (C1…C7)
# ---------------------------------------------------------------------------

#: The fifteen Application Laws (APPLICATION-001 §7), each mapped to its short
#: obligation.
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

#: The Application laws the bare Application root construct is directly obligated by.
#: UAL-06/07/08/11/13 (feature-service-consumption / module cohesion / feature
#: explicitness / interaction typedness / feature-interaction data) apply to the
#: Capability/Module/Feature/Interaction units (AMC-02/03/04/06); they are recorded
#: not-applicable-to-the-Application-root with rationale.
APPLICATION_APPLICABLE_LAWS: tuple[str, ...] = (
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

#: Laws scoped to Module/Feature/Interaction concerns (U03/U04/U06), N/A to the root.
APPLICATION_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-06",
    "UAL-07",
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
    "V1": "Instantiates exactly one meta-class (Application → AMC-01).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints an Application root is bound by (APPLICATION-005 §4). AMK-02/04/07
#: (feature-declares-capability / feature-engaged-through-interaction / feature
#: data-and-operation binding) are scoped to the Feature unit (AMC-04) and are
#: recorded not-applicable-to-root.
APPLICATION_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "AMK-03": "The founding meta-relationship graph (AMR-02/03/05) is acyclic (a DAG).",
    "AMK-05": "Every behavior/state ref (AMR-06/11) resolves to an RL-F2 construct; none redef.",
    "AMK-06": "Every composition reference (AMR-07/12) resolves to a PL-F2 construct; none redef.",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

#: Meta-constraints scoped to the Feature unit (AMC-04), N/A to the Application root.
APPLICATION_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-02", "AMK-04", "AMK-07")

#: The CCE ten-gate identifiers (EC-3 AP-4 certification strategy, CC-1…CC-10).
CCE_GATES: tuple[str, ...] = tuple(f"CC-{n}" for n in range(1, 11))

__all__ = [
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "TRACE_BACKWARD",
    "SUBSTRATE_REFS",
    "META_CLASSES",
    "APPLICATION_META_CLASS",
    "META_RELATIONSHIPS",
    "APPLICATION_RELATIONSHIPS",
    "ApplicationKind",
    "ApplicationState",
    "LIFECYCLE_ORDER",
    "APPLICATION_LAWS",
    "APPLICATION_APPLICABLE_LAWS",
    "APPLICATION_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "APPLICATION_META_CONSTRAINTS",
    "APPLICATION_INAPPLICABLE_CONSTRAINTS",
    "CCE_GATES",
]
