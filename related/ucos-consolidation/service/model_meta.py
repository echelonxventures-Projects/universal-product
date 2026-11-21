"""EC3-B11-U11 — Universal Service Meta-Model constants (read-only projections of SERVICE-005).

This module carries, as executable constants, the fixed identifiers of the frozen Service
Foundation and the **Universal Service Meta-Model (USM)** master architecture (SERVICE-001
Constitution, SERVICE-003 Ontology, SERVICE-004 Taxonomy, **SERVICE-005 Universal Service
Meta-Model**) that the meta-model realization must **integrate** and conform to. It
**defines no new law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it
only names the frozen obligations so the realization can be checked against them
deterministically.

Everything here is derived verbatim from the frozen ``11-SERVICE/`` specification at the
constitutional anchor ``b7e7657`` (SERVICE-005 §2…§12) — no obligation is invented, none is
dropped. The Universal Service Meta-Model is the **model-of-the-model**: it fixes exactly
the ten meta-classes (SMC-01…10, §2), the thirteen meta-relationships (SMR-01…13, §3), the
meta-constraints (SMK-01…08, §4), and the seven meta-invariants (SMI-01…07, §8) that keep
the model **closed, total, acyclic, reuse-integral, non-constitutive, and non-projective**.
It is the conformance gate every concern architecture (SERVICE-006…014) — and every realized
concern meta-class SMC-01…10 (units U01…U10) — is validated against.

Shared foundation constants (anchors, laws, compliance conditions, meta-validity gate, CCE
gates, lifecycle states, the ten meta-classes, the thirteen meta-relationships) are **reused
by reference** from the CERTIFIED SMC-01 surface (:mod:`service.service_meta`); re-exported,
never re-defined.
"""

from __future__ import annotations

# --- SMC-01 reuse by reference (USL-02) — shared foundation constants, never re-defined
from service.service_meta import (
    CCE_GATES,
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    LIFECYCLE_ORDER,
    META_CLASSES,
    META_RELATIONSHIPS,
    META_VALIDITY_CHECKS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

# ---------------------------------------------------------------------------
# The meta-model follows the frozen service lifecycle SOS-01…06 (USL-12). Identical
# forward-only state machine as every other service construct, reused by reference.
# ---------------------------------------------------------------------------

#: The meta-model lifecycle state type (reused SOS-01…06; USL-12).
ModelState = ServiceState

# ---------------------------------------------------------------------------
# SERVICE-005 — the meta-model identity (it is the model, not a concern meta-class)
# ---------------------------------------------------------------------------

#: The meta-model "class" label. The Universal Service Meta-Model is **not** one of the ten
#: concern meta-classes (SMI-01 admits no eleventh meta-class); it is the model that fixes
#: them. It is labelled ``USM`` — the singular model-of-the-model artifact.
MODEL_CLASS = "USM"

#: The governing architecture the meta-model realizes (SERVICE-005 §1).
GOVERNING_SPEC = "SERVICE-005"

# ---------------------------------------------------------------------------
# SERVICE-005 §2 — the ten meta-classes (SMC-01…10), each modelling one ontology entity
# (SOE-0n, SERVICE-003 §2) classified by one hierarchy (SXH-0n, SERVICE-004 §3), realized
# by exactly one CERTIFIED Band-11 unit (U01…U10). No eleventh meta-class (SMI-01).
# ---------------------------------------------------------------------------

#: Each meta-class member spec, verbatim from SERVICE-005 §2 + the CERTIFIED realization map:
#:   (meta_class, name, models_entity SOE, classified_by SXH, unit, realize_module)
MEMBER_SPECS: tuple[tuple[str, str, str, str, str, str], ...] = (
    ("SMC-01", "Service", "SOE-01", "SXH-01", "EC3-B11-U01", "service.service_realize"),
    ("SMC-02", "Capability", "SOE-02", "SXH-02", "EC3-B11-U02", "service.capability_realize"),
    ("SMC-03", "Contract", "SOE-03", "SXH-03", "EC3-B11-U03", "service.contract_realize"),
    ("SMC-04", "Interface", "SOE-04", "SXH-04", "EC3-B11-U04", "service.interface_realize"),
    ("SMC-05", "Operation", "SOE-05", "SXH-05", "EC3-B11-U05", "service.operation_realize"),
    ("SMC-06", "Composition", "SOE-06", "SXH-06", "EC3-B11-U06", "service.composition_realize"),
    ("SMC-07", "Orchestration", "SOE-07", "SXH-07", "EC3-B11-U07", "service.orchestration_realize"),
    ("SMC-08", "Execution", "SOE-08", "SXH-08", "EC3-B11-U08", "service.execution_realize"),
    ("SMC-09", "Policy", "SOE-09", "SXH-09", "EC3-B11-U09", "service.policy_realize"),
    ("SMC-10", "Security", "SOE-10", "SXH-10", "EC3-B11-U10", "service.security_realize"),
)

# ---------------------------------------------------------------------------
# SERVICE-005 §3 / §9 — the thirteen meta-relationships (SMR-01…13), each modelling one
# ontology relationship (SOR-0n), reusing ENG-005 by reference. Sources/targets are the
# meta-model map edges (§9). No fourteenth meta-relationship (SMI-02).
# ---------------------------------------------------------------------------

#: Each meta-relationship edge spec, verbatim from SERVICE-005 §3/§9:
#:   (relationship SMR, name, models SOR, source meta-class, target)
#: Targets SMR-10/11/12/13 point to the frozen EL-1/RL-F2/PL-F2/DF-2 foundations *by
#: reference*.
EDGE_SPECS: tuple[tuple[str, str, str, str, str], ...] = (
    ("SMR-01", "realizes", "SOR-01", "SMC-01", "SMC-02"),
    ("SMR-02", "bound-by", "SOR-02", "SMC-05", "SMC-03"),
    ("SMR-03", "exposes", "SOR-03", "SMC-01", "SMC-04"),
    ("SMR-04", "provides", "SOR-04", "SMC-01", "SMC-05"),
    ("SMR-05", "composes", "SOR-05", "SMC-01", "SMC-06"),
    ("SMR-06", "orchestrates", "SOR-06", "SMC-07", "SMC-01"),
    ("SMR-07", "executes", "SOR-07", "SMC-05", "SMC-08"),
    ("SMR-08", "governed-by", "SOR-08", "SMC-01", "SMC-09"),
    ("SMR-09", "classified-by", "SOR-09", "SMC-01", "SMC-10"),
    ("SMR-10", "identified-by", "SOR-10", "SMC-01", "ENG-001"),
    ("SMR-11", "behaves-as", "SOR-11", "SMC-01", "RL-F2"),
    ("SMR-12", "composed-as", "SOR-12", "SMC-01", "PL-F2"),
    ("SMR-13", "operates-on", "SOR-13", "SMC-05", "DF-2"),
)

#: The founding meta-relationships (SMK-03 / SMI-04) — the founding meta-graph over these
#: edges is required to be a DAG. Per SERVICE-005 §4 SMK-03: the founding graph is
#: SMR-02/03/04/05 (bound-by / exposes / provides / composes).
FOUNDING_META_RELATIONSHIPS: tuple[str, ...] = ("SMR-02", "SMR-03", "SMR-04", "SMR-05")

#: The frozen foundation targets a meta-relationship may reference (never redefine): EL-1
#: identity (ENG-001 via ENG-002), the RL-F2 runtime concern, the PL-F2 platform concern,
#: the DF-2 represented-data concern.
FOUNDATION_TARGETS: tuple[str, ...] = ("ENG-001", "RL-F2", "PL-F2", "DF-2")

# ---------------------------------------------------------------------------
# SERVICE-003 §2/§3 — the ontology closure sets the meta-model must totally cover (SMI-03).
# ---------------------------------------------------------------------------

#: The ten ontology entities (SOE-01…10) — each modelled by exactly one meta-class (SMI-03).
ONTOLOGY_ENTITIES: tuple[str, ...] = tuple(f"SOE-{n:02d}" for n in range(1, 11))

#: The thirteen ontology relationships (SOR-01…13) — each modelled by exactly one
#: meta-relationship (SMI-03).
ONTOLOGY_RELATIONSHIPS: tuple[str, ...] = tuple(f"SOR-{n:02d}" for n in range(1, 14))

# ---------------------------------------------------------------------------
# SERVICE-005 §8 — the seven meta-invariants (SMI-01…07)
# ---------------------------------------------------------------------------

#: The seven meta-invariants (SERVICE-005 §8) the realized meta-model must satisfy.
META_INVARIANTS: dict[str, str] = {
    "SMI-01": "Closure — no meta-class outside SMC-01…10.",
    "SMI-02": "Relationship closure — no meta-relationship outside SMR-01…13.",
    "SMI-03": "Totality — every ontology entity/relationship modelled by exactly one.",
    "SMI-04": "Acyclicity — the founding meta-graph (SMR-02/03/04/05) is a DAG (SMK-03).",
    "SMI-05": "Reuse integrity — EL-1/RL-F2/PL-F2/DF-2 referenced, never redefined.",
    "SMI-06": "Non-constitutiveness — no meta-element confers authority or selects technology.",
    "SMI-07": "Non-projection — model coverage is never roadmap completion (STATUS-001 §2).",
}

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from SERVICE-005 §10)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized meta-model records (SERVICE-005 §10).
TRACE_BACKWARD_MODEL: tuple[str, ...] = (
    MODEL_CLASS,  # the Universal Service Meta-Model artifact (this construct)
    "SERVICE-005",  # Universal Service Meta-Model (USM) Master Architecture
    "SERVICE-004",  # Universal Service Taxonomy (SXH-01…11)
    "SERVICE-003",  # Universal Service Ontology (SOE-01…10; SOR-01…13)
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen substrate the meta-model reuses by reference (USL-02 / SMI-05): the EL-1
#: identity/object/type/reference primitives (via each member), plus the RL-F2, PL-F2, and
#: DF-2 concerns referenced through SMR-11/SMR-12/SMR-13.
MODEL_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (SMR-10 identified-by; via ENG-002)
    "ENG-002",  # Object     (every meta-class is objecthood-bound — SMK-01)
    "ENG-004",  # Type       (every meta-class is typed — SMK-01)
    "ENG-005",  # Reference  (every meta-relationship IS an ENG-005 reference — §3)
    "RL-F2",  # RUNTIME behaviour concern (SMR-11 behaves-as; SMR-07 executes; by reference)
    "PL-F2",  # PLATFORM composition concern (SMR-12 composed-as; by reference)
    "DF-2",  # DATA represented-data concern (SMR-13 operates-on; by reference)
)

# ---------------------------------------------------------------------------
# SERVICE-001 §7 — Service Laws applicability for the meta-model construct
# ---------------------------------------------------------------------------

#: The Service laws the meta-model construct is directly obligated by. The meta-model is the
#: layer's conformance gate; it materially exercises USL-02 (reuse-by-reference over all ten
#: CERTIFIED units + EL-1/RL-F2/PL-F2/DF-2) and USL-15 (non-constitutive) at the whole-model
#: level, and re-affirms USL-03/04/05 (typed/identified/objecthood) for its own object.
MODEL_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",  # founded on frozen EL-1 (layer)
    "USL-02",  # reuse by reference; redefine 0 (all ten units + EL-1/RL-F2/PL-F2/DF-2) — MATERIAL
    "USL-03",  # typed (the meta-model object is typed)
    "USL-04",  # identified via object (one scheme)
    "USL-05",  # objecthood
    "USL-12",  # the meta-model object itself carries a forward-only lifecycle state
    "USL-15",  # non-constitutive — MATERIAL (the model confers no authority, selects no tech)
)

#: Laws scoped to the concern meta-classes (each another realized unit's obligation), not
#: to the integrating meta-model: USL-06 (contract), USL-07 (interface), USL-08 (operation
#: I/O), USL-09 (composition/orchestration), USL-10 (execution), USL-11 (operation data),
#: USL-13 (policy), USL-14 (security). The meta-model *fixes* these laws' meta-shape; it
#: does not re-realize the concern constructs.
MODEL_DEFERRED_LAWS: tuple[str, ...] = (
    "USL-06",
    "USL-07",
    "USL-08",
    "USL-09",
    "USL-10",
    "USL-11",
    "USL-13",
    "USL-14",
)

# ---------------------------------------------------------------------------
# SERVICE-005 §4 — meta-constraints the meta-model object is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints the meta-model object is bound by (SERVICE-005 §4).
MODEL_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Every modelled construct is typed (ENG-004), identified (ENG-001), object-bound.",
    "SMK-03": "The founding meta-relationship graph (SMR-02/03/04/05) is acyclic (a DAG).",
    "SMK-08": "No modelled construct selects technology or confers authority.",
}

__all__ = [
    # reused-by-reference foundation constants (re-exported, not re-defined)
    "CCE_GATES",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "LIFECYCLE_ORDER",
    "META_CLASSES",
    "META_RELATIONSHIPS",
    "META_VALIDITY_CHECKS",
    "SERVICE_COMPLIANCE",
    "SERVICE_LAWS",
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
