"""EC3-B12-U11 — Universal Application Meta-Model constants (projections of APPLICATION-005).

This module carries, as executable constants, the fixed identifiers of the frozen Application
Foundation and the **Universal Application Meta-Model (UAM)** master architecture
(APPLICATION-001 Constitution, APPLICATION-003 Ontology, APPLICATION-004 Taxonomy,
**APPLICATION-005 Universal Application Meta-Model**) that the meta-model realization must
**integrate** and conform to. It **defines no new law and redefines no foundation concept**
(UAL-02 / AMI-05 / UAL-15); it only names the frozen obligations so the realization can be
checked against them deterministically.

Everything here is derived verbatim from the frozen ``12-APPLICATION/`` specification at the
constitutional anchor ``b7e7657`` (APPLICATION-005 §2…§12) — no obligation is invented, none
is dropped. The Universal Application Meta-Model is the **model-of-the-model**: it fixes
exactly the ten meta-classes (AMC-01…10, §2), the fourteen meta-relationships (AMR-01…14,
§3), the meta-constraints (AMK-01…08, §4), and the seven meta-invariants (AMI-01…07, §8) that
keep the model **closed, total, acyclic, reuse-integral, non-constitutive, and
non-projective**. It is the conformance gate every concern architecture (APPLICATION-006…014)
— and every realized concern meta-class AMC-01…10 (units U01…U10) — is validated against.

Shared foundation constants (anchors, laws, compliance conditions, meta-validity gate, CCE
gates, lifecycle states, the ten meta-classes, the fourteen meta-relationships) are **reused
by reference** from the CERTIFIED AMC-01 surface (:mod:`application.application_meta`);
re-exported, never re-defined.
"""

from __future__ import annotations

# --- AMC-01 reuse by reference (UAL-02) — shared foundation constants, never re-defined
from application.application_meta import (
    APPLICATION_COMPLIANCE,
    APPLICATION_LAWS,
    CCE_GATES,
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    LIFECYCLE_ORDER,
    META_CLASSES,
    META_RELATIONSHIPS,
    META_VALIDITY_CHECKS,
    ApplicationState,
)

# ---------------------------------------------------------------------------
# The meta-model follows the frozen application lifecycle AOS-01…06 (UAL-12). Identical
# forward-only state machine as every other application construct, reused by reference.
# ---------------------------------------------------------------------------

#: The meta-model lifecycle state type (reused AOS-01…06; UAL-12).
ModelState = ApplicationState

# ---------------------------------------------------------------------------
# APPLICATION-005 — the meta-model identity (it is the model, not a concern meta-class)
# ---------------------------------------------------------------------------

#: The meta-model "class" label. The Universal Application Meta-Model is **not** one of the
#: ten concern meta-classes (AMI-01 admits no eleventh meta-class); it is the model that
#: fixes them. It is labelled ``UAM`` — the singular model-of-the-model artifact.
MODEL_CLASS = "UAM"

#: The governing architecture the meta-model realizes (APPLICATION-005 §1).
GOVERNING_SPEC = "APPLICATION-005"

# ---------------------------------------------------------------------------
# APPLICATION-005 §2 — the ten meta-classes (AMC-01…10), each modelling one ontology entity
# (AOE-0n, APPLICATION-003 §2) classified by one hierarchy (AXH-0n, APPLICATION-004 §3),
# realized by exactly one CERTIFIED Band-12 unit (U01…U10). No eleventh meta-class (AMI-01).
# ---------------------------------------------------------------------------

#: Each meta-class member spec, verbatim from APPLICATION-005 §2 + the CERTIFIED realization
#: map:
#:   (meta_class, name, models_entity AOE, classified_by AXH, unit, realize_module)
MEMBER_SPECS: tuple[tuple[str, str, str, str, str, str], ...] = (
    ("AMC-01", "Application", "AOE-01", "AXH-01", "EC3-B12-U01", "application.application_realize"),
    ("AMC-02", "Capability", "AOE-02", "AXH-02", "EC3-B12-U02", "application.capability_realize"),
    ("AMC-03", "Module", "AOE-03", "AXH-03", "EC3-B12-U03", "application.module_realize"),
    ("AMC-04", "Feature", "AOE-04", "AXH-04", "EC3-B12-U04", "application.feature_realize"),
    ("AMC-05", "Workflow", "AOE-05", "AXH-05", "EC3-B12-U05", "application.workflow_realize"),
    ("AMC-06", "Interaction", "AOE-06", "AXH-06", "EC3-B12-U06", "application.interaction_realize"),
    ("AMC-07", "State", "AOE-07", "AXH-07", "EC3-B12-U07", "application.state_realize"),
    ("AMC-08", "Composition", "AOE-08", "AXH-08", "EC3-B12-U08", "application.composition_realize"),
    ("AMC-09", "Security", "AOE-09", "AXH-09", "EC3-B12-U09", "application.security_realize"),
    ("AMC-10", "Governance", "AOE-10", "AXH-10", "EC3-B12-U10", "application.governance_realize"),
)

# ---------------------------------------------------------------------------
# APPLICATION-005 §3 / §9 — the fourteen meta-relationships (AMR-01…14), each modelling one
# ontology relationship (AOR-0n), reusing ENG-005 by reference. Sources/targets are the
# meta-model map edges (§9). No fifteenth meta-relationship (AMI-02).
# ---------------------------------------------------------------------------

#: Each meta-relationship edge spec, verbatim from APPLICATION-005 §3/§9:
#:   (relationship AMR, name, models AOR, source meta-class, target)
#: Targets AMR-10/11/12/13/14 point to the frozen EL-1/RL-F2/PL-F2/SF-2/DF-2 foundations *by
#: reference*.
EDGE_SPECS: tuple[tuple[str, str, str, str, str], ...] = (
    ("AMR-01", "delivers", "AOR-01", "AMC-01", "AMC-02"),
    ("AMR-02", "composed-of", "AOR-02", "AMC-01", "AMC-03"),
    ("AMR-03", "groups", "AOR-03", "AMC-03", "AMC-04"),
    ("AMR-04", "sequenced-by", "AOR-04", "AMC-05", "AMC-01"),
    ("AMR-05", "engaged-through", "AOR-05", "AMC-04", "AMC-06"),
    ("AMR-06", "holds-state", "AOR-06", "AMC-01", "AMC-07"),
    ("AMR-07", "assembled-by", "AOR-07", "AMC-01", "AMC-08"),
    ("AMR-08", "secured-by", "AOR-08", "AMC-01", "AMC-09"),
    ("AMR-09", "governed-by", "AOR-09", "AMC-01", "AMC-10"),
    ("AMR-10", "identified-by", "AOR-10", "AMC-01", "ENG-001"),
    ("AMR-11", "behaves-as", "AOR-11", "AMC-01", "RL-F2"),
    ("AMR-12", "composed-as", "AOR-12", "AMC-01", "PL-F2"),
    ("AMR-13", "consumes-operation", "AOR-13", "AMC-04", "SF-2"),
    ("AMR-14", "presents-data", "AOR-14", "AMC-04", "DF-2"),
)

#: The founding meta-relationships (AMK-03 / AMI-04) — the founding meta-graph over these
#: edges is required to be a DAG. Per APPLICATION-005 §4 AMK-03: the founding graph is
#: AMR-02/03/05 (composed-of / groups / engaged-through) — the chain
#: Application → Module → Feature → Interaction.
FOUNDING_META_RELATIONSHIPS: tuple[str, ...] = ("AMR-02", "AMR-03", "AMR-05")

#: The frozen foundation targets a meta-relationship may reference (never redefine): EL-1
#: identity (ENG-001 via ENG-002), the RL-F2 runtime concern (behaves-as / holds-state), the
#: PL-F2 platform concern (assembled-by / composed-as; PLATFORM-009), the SF-2 service concern
#: (consumes-operation), and the DF-2 represented-data concern (presents-data).
FOUNDATION_TARGETS: tuple[str, ...] = ("ENG-001", "RL-F2", "PL-F2", "SF-2", "DF-2")

# ---------------------------------------------------------------------------
# APPLICATION-003 §2/§3 — the ontology closure sets the meta-model must totally cover
# (AMI-03).
# ---------------------------------------------------------------------------

#: The ten ontology entities (AOE-01…10) — each modelled by exactly one meta-class (AMI-03).
ONTOLOGY_ENTITIES: tuple[str, ...] = tuple(f"AOE-{n:02d}" for n in range(1, 11))

#: The fourteen ontology relationships (AOR-01…14) — each modelled by exactly one
#: meta-relationship (AMI-03).
ONTOLOGY_RELATIONSHIPS: tuple[str, ...] = tuple(f"AOR-{n:02d}" for n in range(1, 15))

# ---------------------------------------------------------------------------
# APPLICATION-005 §8 — the seven meta-invariants (AMI-01…07)
# ---------------------------------------------------------------------------

#: The seven meta-invariants (APPLICATION-005 §8) the realized meta-model must satisfy.
META_INVARIANTS: dict[str, str] = {
    "AMI-01": "Closure — no meta-class outside AMC-01…10.",
    "AMI-02": "Relationship closure — no meta-relationship outside AMR-01…14.",
    "AMI-03": "Totality — every ontology entity/relationship modelled by exactly one.",
    "AMI-04": "Acyclicity — the founding meta-graph (AMR-02/03/05) is a DAG (AMK-03).",
    "AMI-05": "Reuse integrity — EL-1/RL-F2/PL-F2/DF-2/SF-2 referenced, never redefined.",
    "AMI-06": "Non-constitutiveness — no meta-element confers authority or selects technology.",
    "AMI-07": "Non-projection — model coverage is never roadmap completion (STATUS-001 §2).",
}

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from APPLICATION-005 §10)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized meta-model records (APPLICATION-005 §10).
TRACE_BACKWARD_MODEL: tuple[str, ...] = (
    MODEL_CLASS,  # the Universal Application Meta-Model artifact (this construct)
    "APPLICATION-005",  # Universal Application Meta-Model (UAM) Master Architecture
    "APPLICATION-004",  # Universal Application Taxonomy (AXH-01…11)
    "APPLICATION-003",  # Universal Application Ontology (AOE-01…10; AOR-01…14)
    "APPLICATION-001",  # Universal Application Constitution (UAL-01…15)
    "ARCH-APPLICATION-001",  # Governing Application architecture model
    f"12-APPLICATION@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen substrate the meta-model reuses by reference (UAL-02 / AMI-05): the EL-1
#: identity/object/type/reference primitives (via each member), plus the RL-F2, PL-F2, SF-2,
#: and DF-2 concerns referenced through AMR-11/AMR-12/AMR-13/AMR-14 (and AMR-06/07).
MODEL_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (AMR-10 identified-by; via ENG-002)
    "ENG-002",  # Object     (every meta-class is objecthood-bound — AMK-01)
    "ENG-004",  # Type       (every meta-class is typed — AMK-01)
    "ENG-005",  # Reference  (every meta-relationship IS an ENG-005 reference — §3)
    "RL-F2",  # RUNTIME behaviour/state concern (AMR-11 behaves-as; AMR-06 holds-state; by ref)
    "PL-F2",  # PLATFORM composition concern (AMR-07 assembled-by; AMR-12 composed-as; by ref)
    "SF-2",  # SERVICE contracted-operation concern (AMR-13 consumes-operation; by ref)
    "DF-2",  # DATA represented-data concern (AMR-14 presents-data; by ref)
)

# ---------------------------------------------------------------------------
# APPLICATION-001 §7 — Application Laws applicability for the meta-model construct
# ---------------------------------------------------------------------------

#: The Application laws the meta-model construct is directly obligated by. The meta-model is
#: the layer's conformance gate; it materially exercises UAL-02 (reuse-by-reference over all
#: ten CERTIFIED units + EL-1/RL-F2/PL-F2/SF-2/DF-2) and UAL-15 (non-constitutive) at the
#: whole-model level, and re-affirms UAL-03/04/05 (typed/identified/objecthood) for its own
#: object.
MODEL_APPLICABLE_LAWS: tuple[str, ...] = (
    "UAL-01",  # founded on frozen EL-1 (layer)
    "UAL-02",  # reuse by reference; redefine 0 (ten units + EL-1/RL-F2/PL-F2/SF-2/DF-2) — MATERIAL
    "UAL-03",  # typed (the meta-model object is typed)
    "UAL-04",  # identified via object (one scheme)
    "UAL-05",  # objecthood
    "UAL-12",  # the meta-model object itself carries a forward-only lifecycle state
    "UAL-15",  # non-constitutive — MATERIAL (the model confers no authority, selects no tech)
)

#: Laws scoped to the concern meta-classes (each another realized unit's obligation), not to
#: the integrating meta-model: UAL-06 (feature capability-delivery), UAL-07 (module
#: cohesion), UAL-08 (feature explicitness), UAL-09 (composition), UAL-10 (workflow), UAL-11
#: (interaction typedness), UAL-13 (feature/interaction data), UAL-14 (security/governance).
#: The meta-model *fixes* these laws' meta-shape; it does not re-realize the concern
#: constructs.
MODEL_DEFERRED_LAWS: tuple[str, ...] = (
    "UAL-06",
    "UAL-07",
    "UAL-08",
    "UAL-09",
    "UAL-10",
    "UAL-11",
    "UAL-13",
    "UAL-14",
)

# ---------------------------------------------------------------------------
# APPLICATION-005 §4 — meta-constraints the meta-model object is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints the meta-model object is bound by (APPLICATION-005 §4).
MODEL_META_CONSTRAINTS: dict[str, str] = {
    "AMK-01": "Every modelled construct is typed (ENG-004), identified (ENG-001), object-bound.",
    "AMK-03": "The founding meta-relationship graph (AMR-02/03/05) is acyclic (a DAG).",
    "AMK-08": "No modelled construct selects technology, grants access, or confers authority.",
}

__all__ = [
    # reused-by-reference foundation constants (re-exported, not re-defined)
    "APPLICATION_COMPLIANCE",
    "APPLICATION_LAWS",
    "CCE_GATES",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "LIFECYCLE_ORDER",
    "META_CLASSES",
    "META_RELATIONSHIPS",
    "META_VALIDITY_CHECKS",
    "ModelState",
    # meta-model-specific projections
    "MODEL_CLASS",
    "GOVERNING_SPEC",
    "MEMBER_SPECS",
    "EDGE_SPECS",
    "FOUNDING_META_RELATIONSHIPS",
    "FOUNDATION_TARGETS",
    "ONTOLOGY_ENTITIES",
    "ONTOLOGY_RELATIONSHIPS",
    "META_INVARIANTS",
    "TRACE_BACKWARD_MODEL",
    "MODEL_SUBSTRATE_REFS",
    "MODEL_APPLICABLE_LAWS",
    "MODEL_DEFERRED_LAWS",
    "MODEL_META_CONSTRAINTS",
]
