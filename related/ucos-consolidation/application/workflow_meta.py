"""EC3-B12-U05 — Workflow meta-model constants (read-only projections of
APPLICATION-001/003/004/005/009).

This module carries, as executable constants, the fixed identifiers of the frozen
Application Foundation (APPLICATION-001 Constitution, APPLICATION-003 Ontology,
APPLICATION-004 Taxonomy, APPLICATION-005 Meta-Model) and the frozen Workflow
Architecture (APPLICATION-009, AMC-05 / UAWA) that the Universal Workflow realization must
conform to. It **defines no new law and redefines no foundation concept**
(UAL-02 / AMI-05 / UAL-15); it only names the frozen obligations so the realization can
be checked against them deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification
at the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Realization unit (EC-3 Band 12, Unit 05) — defined locally so the frozen U01
# ``application/__init__.py`` (REALIZATION_UNIT = "EC3-B12-U01") is left untouched.
# ---------------------------------------------------------------------------

#: The realization unit this module set realizes (EC-3 Band 12, Unit 05).
REALIZATION_UNIT = "EC3-B12-U05"

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
#: ``application.module`` + U04 Universal Feature ``application.feature`` at HEAD
#: ``7e042ec``).
IMPLEMENTATION_ANCHOR = "7e042ec"

#: The backward traceability chain every realized Workflow records
#: (APPLICATION-009 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "AMC-05",  # APPLICATION-005 §2 — Workflow meta-class
    "APPLICATION-009",  # Universal Application Workflow Architecture (UAWA)
    "APPLICATION-005",  # Universal Application Meta-Model (AMC/AMR/AMK/AMI)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Workflow construct reuses **directly** by reference
#: (UAL-02 / AMI-05). A Workflow is the ordered/conditional arrangement of
#: features/operations over time: it reuses EL-1 (identity, value, typing, reference),
#: RL-F2 (the workflow concern + state advancement it binds by reference — §7 / AMR-06/11),
#: and SF-2 (the operations its steps consume under contract + the orchestration it binds —
#: AMR-13 / AMR-11). It does **not** deliver a capability (AMR-01), present DF-2 data
#: (AMR-14), group features (AMR-03), or assemble a PLATFORM composition (AMR-07/12) —
#: those are the Application / Capability / Module / Feature concerns (AMC-01/02/03/04).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, AMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity; canonical core)
    "ENG-004",  # Type      (typed, UAL-03)
    "ENG-005",  # Relationship/Reference (sequencing/consumption/state/behavior refs)
    "RL-F2",  # Runtime workflow + state (behaves-as / holds-state, §7, by reference)
    "SF-2",  # Contracted operation + orchestration (consumes-operation AMR-13, by reference)
)

#: The prior CERTIFIED / frozen constructs the Workflow reuses **by reference through its
#: relationships** (never redefined; reused only by reference — mission reuse list):
#:   AMC-01 (Application) / AMC-04 (Feature) — sequenced-by the workflow (AMR-04, the
#:                          DEFINING relationship: the workflow sequences features/ops).
#:   AMC-07 (State)       — held by the workflow (AMR-06 holds-state; reference-only —
#:                          State is a downstream Band-12 unit, referenced by id → RL-F2).
#:   SF-2                 — the operations the workflow's steps consume (AMR-13) +
#:                          the orchestration it behaves-as (AMR-11).
#:   RL-F2                — the workflow concern + state it behaves-as / holds (AMR-11/06).
REFERENCED_UNITS: tuple[str, ...] = (
    "AMC-01",  # Universal Application (EC3-B12-U01, CERTIFIED) — sequenced-by (AMR-04)
    "AMC-04",  # Universal Feature (EC3-B12-U04, CERTIFIED) — sequenced-by (AMR-04)
    "AMC-07",  # Universal State (downstream) — held-state (AMR-06, by reference → RL-F2)
    "SF-2",  # Contracted operation(s) consumed by the workflow's steps (AMR-13)
    "RL-F2",  # Runtime workflow + state the workflow behaves-as / holds (AMR-11/06)
)

# ---------------------------------------------------------------------------
# APPLICATION-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (AMI-01 closure). Workflow is AMC-05.
META_CLASSES: tuple[str, ...] = tuple(f"AMC-{n:02d}" for n in range(1, 11))

#: The Workflow meta-class id (APPLICATION-005 §2; APPLICATION-009).
WORKFLOW_META_CLASS = "AMC-05"

#: The fourteen admitted meta-relationships (AMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"AMR-{n:02d}" for n in range(1, 15))

#: The meta-relationships a Workflow participates in (APPLICATION-009 §6/§16):
#:   AMR-04 sequenced-by      (Application/Feature → Workflow; the DEFINING relationship —
#:                             the workflow sequences features/operations; NEW: no prior
#:                             Band-12 unit used AMR-04)
#:   AMR-06 holds-state       (Workflow → State; forward-only state advancement, by
#:                             reference → RL-F2; NEW: no prior Band-12 unit used AMR-06)
#:   AMR-10 identified-by     (ENG-001 via ENG-002)
#:   AMR-11 behaves-as        (RUNTIME workflow + SF-2 orchestration, by reference — §7)
#:   AMR-13 consumes-operation(SF-2 SERVICE operation(s) the steps consume, by reference)
WORKFLOW_RELATIONSHIPS: tuple[str, ...] = (
    "AMR-04",
    "AMR-06",
    "AMR-10",
    "AMR-11",
    "AMR-13",
)


class WorkflowKind(str, Enum):
    """AXH-05 Workflow Hierarchy (APPLICATION-004 §3; APPLICATION-009 §5) — the
    classification of an application Workflow.

    A Workflow is classified by exactly one kind (single-facet, AXC-02 / AXC-04):
    """

    SEQUENTIAL = "Sequential-Workflow"  # ordered features/operations toward an outcome
    CONDITIONAL = "Conditional-Workflow"  # branch-governed arrangement of features (≥2 branches)
    PROCESS = "Process-Workflow"  # long-running, state-advancing orchestration (a process)


class WorkflowState(str, Enum):
    """AOS-01…06 (APPLICATION-003 §4; APPLICATION-009 §8) — the forward-only workflow
    lifecycle states (UAL-12)."""

    DEFINED = "DEFINED"  # AOS-01 — declared (sequence/ops/state/behavior) but not composed
    COMPOSED = "COMPOSED"  # AOS-02 — sequenced steps assembled (bound by reference)
    CONTEXTUALIZED = "CONTEXTUALIZED"  # AOS-03 — placed within a state context
    EXECUTABLE = "EXECUTABLE"  # AOS-04 — sequenced + advanceable (authoritative)
    DEPRECATED = "DEPRECATED"  # AOS-05 — superseded-in-waiting (lineage recorded)
    RETIRED = "RETIRED"  # AOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (UAL-12 / AOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[WorkflowState, ...] = (
    WorkflowState.DEFINED,
    WorkflowState.COMPOSED,
    WorkflowState.CONTEXTUALIZED,
    WorkflowState.EXECUTABLE,
    WorkflowState.DEPRECATED,
    WorkflowState.RETIRED,
)

#: Workflow kinds that are branch-governed and must sequence more than one step
#: (AXH-05 Conditional; WKF-05 conditional determinacy — ≥2 decidable branches).
MULTI_STEP_KINDS: frozenset[WorkflowKind] = frozenset({WorkflowKind.CONDITIONAL})

#: Workflow kinds that are long-running processes whose intermediate states are recorded
#: (AXH-05 Process; WKF-07 / WKF-C5).
PROCESS_KINDS: frozenset[WorkflowKind] = frozenset({WorkflowKind.PROCESS})

# ---------------------------------------------------------------------------
# APPLICATION-009 §7 — Workflow behavior binding (sequence / transition / emit)
# ---------------------------------------------------------------------------

#: The RUNTIME/SF-2 behavior bindings a workflow references (never re-implemented).
WORKFLOW_BEHAVIOR_BINDINGS: dict[str, str] = {
    "workflow-sequence": "RUNTIME workflow + SF-2 orchestration (order features/ops, AOB-04)",
    "workflow-transition": "RUNTIME state (advance application/feature state, AOB-05)",
    "workflow-emit": "RUNTIME event (signal a workflow-sequenced occurrence, AOV-05)",
}

# ---------------------------------------------------------------------------
# APPLICATION-009 §4 — Workflow principles (WKF-01…10)
# ---------------------------------------------------------------------------

#: The ten Workflow principles (APPLICATION-009 §4), each mapped to its short rule.
WORKFLOW_PRINCIPLES: dict[str, str] = {
    "WKF-01": "Every workflow is classified by an ENG-004 Type; no untyped workflow exists.",
    "WKF-02": "Every workflow is an ENG-002 Object bearing an ENG-001 identity; no 2nd scheme.",
    "WKF-03": "A workflow binds the frozen RL-F2 workflow + SF-2 orchestration by reference.",
    "WKF-04": "A workflow sequences declared features/operations toward an outcome; explicit.",
    "WKF-05": "Branch conditions are decidable and typed; no implicit or non-terminating branch.",
    "WKF-06": "A workflow advances state within a declared context, forward-only and recorded.",
    "WKF-07": "A process is a long-running workflow whose intermediate states are recorded.",
    "WKF-08": "New workflow types append additively (AXH-05) without renumber or invalidation.",
    "WKF-09": "A workflow confers no authority, embeds no secret, selects no technology.",
    "WKF-10": "Any consumed ARCH/CAT/REF/GEN/IMP/UKB asset is labelled INPUT, never COMPLETION.",
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

#: The Application laws the Workflow construct is directly obligated by. **UAL-10 (workflow/
#: process binds RL-F2 + SF-2 orchestration by reference) is THE governing law**, together
#: with **UAL-12 (decidable, forward-only, recorded lifecycle/state advancement)**. The
#: workflow is also typed (UAL-03), identified/object-borne (UAL-04/05), founded on the
#: frozen substrate (UAL-01), reuse-integral (UAL-02), and non-constitutive (UAL-14/15).
#: UAL-06/07/08/09/11/13 are scoped to the Feature/Module/Application/Interaction units
#: (AMC-01/02/03/04/06): a workflow *sequences* what features *deliver* — it neither
#: delivers capability, groups features, declares a feature contract, structurally composes
#: modules, engages an actor through an interaction, nor presents DF-2 data itself.
WORKFLOW_APPLICABLE_LAWS: tuple[str, ...] = (
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

#: Application laws scoped to other units (Feature/Module/Application/Interaction), N/A to
#: the Workflow — recorded honestly (never silently dropped).
WORKFLOW_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-06",
    "UAL-07",
    "UAL-08",
    "UAL-09",
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
    "V1": "Instantiates exactly one meta-class (Workflow → AMC-05).",
    "V2": "All relationships used are within AMR-01…14.",
    "V3": "Satisfies all applicable meta-constraints (AMK-01…08).",
    "V4": "Founding graph is acyclic (AMK-03 / AMI-04).",
    "V5": "Every construct has a valid lifecycle state (AOS-01…06).",
}

#: Meta-constraints a Workflow is bound by (APPLICATION-005 §4; APPLICATION-009 §10).
#: **AMK-05 (every behavior/state reference AMR-06/11 resolves to an RL-F2 construct; none
#: redefined) is materially exercised at the Workflow level** — it is THE defining
#: workflow meta-constraint (the workflow holds-state AMR-06 and behaves-as AMR-11, both →
#: RL-F2). AMK-07 (the consumed operation AMR-13 resolves to an SF-2 operation) is also
#: materially exercised (the workflow's steps consume SF-2 operations). AMK-02-analog
#: (WKF-K2: every sequenced feature/operation is declared and typed) is materially
#: exercised. AMK-03 (the founding meta-relationship graph AMR-02/03/05 is acyclic) is
#: satisfied vacuously — the workflow uses **none** of AMR-02/03/05; its sequencing (AMR-04)
#: is reference-only, so no founding cycle can arise. AMK-04 (a feature is engaged through
#: an interaction before EXECUTABLE) and AMK-06 (composition ref AMR-07/12 → PL-F2) are
#: scoped to the Feature (AMC-04) and Module/Application (AMC-01/03) units respectively —
#: recorded not-applicable-to-workflow.
WORKFLOW_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "AMK-02": "Every sequenced feature/operation is declared and typed (WKF-K2 analog).",
    "AMK-03": "The founding meta-relationship graph (AMR-02/03/05) is acyclic (a DAG).",
    "AMK-05": "Every behavior/state ref (AMR-06/11) resolves to an RL-F2 construct; none redef.",
    "AMK-07": "Every consumed operation ref (AMR-13) resolves to an SF-2 operation; none redef.",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

#: Meta-constraints scoped to the Feature (AMC-04) and Module/Application (AMC-01/03) units,
#: N/A to the Workflow.
WORKFLOW_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("AMK-04", "AMK-06")

#: The Workflow sequencing & process rules (APPLICATION-009 §9; WKF-C1…C5).
WORKFLOW_SEQUENCING_RULES: dict[str, str] = {
    "WKF-C1": "A workflow's sequence of features/ops is explicit, typed, decidable (UAL-10).",
    "WKF-C2": "Branch conditions are decidable and terminating; no infinite or implicit branch.",
    "WKF-C3": "State advancement is forward-only and recorded; no silent reversal (UAL-12).",
    "WKF-C4": "A workflow binds RL-F2 workflow / SF-2 orchestration by reference; re-founds none.",
    "WKF-C5": "A process records its intermediate states so long-running progress is auditable.",
}

#: The Workflow constraints (APPLICATION-009 §10; WKF-K1…K5).
WORKFLOW_CONSTRAINTS: dict[str, str] = {
    "WKF-K1": "Every workflow is typed (ENG-004), identified (ENG-001), object-bound (ENG-002).",
    "WKF-K2": "Every sequenced feature/operation is declared and typed (AMK-02 analog).",
    "WKF-K3": "Every behavior/state reference resolves to an RL-F2 construct; none redefined.",
    "WKF-K4": "Every consumed operation resolves to an SF-2 operation; none redefined.",
    "WKF-K5": "No workflow selects technology or confers authority.",
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
    "WORKFLOW_META_CLASS",
    "META_RELATIONSHIPS",
    "WORKFLOW_RELATIONSHIPS",
    "WorkflowKind",
    "WorkflowState",
    "LIFECYCLE_ORDER",
    "MULTI_STEP_KINDS",
    "PROCESS_KINDS",
    "WORKFLOW_BEHAVIOR_BINDINGS",
    "WORKFLOW_PRINCIPLES",
    "APPLICATION_LAWS",
    "WORKFLOW_APPLICABLE_LAWS",
    "WORKFLOW_INAPPLICABLE_LAWS",
    "APPLICATION_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "WORKFLOW_META_CONSTRAINTS",
    "WORKFLOW_INAPPLICABLE_CONSTRAINTS",
    "WORKFLOW_SEQUENCING_RULES",
    "WORKFLOW_CONSTRAINTS",
    "CCE_GATES",
]
