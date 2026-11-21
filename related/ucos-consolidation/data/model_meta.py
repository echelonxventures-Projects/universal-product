"""EC3-B10-U11 — Universal Data Meta-Model constants (read-only projections of DATA-005).

This module carries, as executable constants, the fixed identifiers of the frozen Data
Foundation and the **Universal Data Meta-Model (UDM)** master architecture (DATA-001
Constitution, DATA-003 Ontology, DATA-004 Taxonomy, **DATA-005 Universal Data Meta-Model**)
that the meta-model realization must integrate and conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the frozen
obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at the
constitutional anchor ``b7e7657`` (DATA-005 §2…§12) — no obligation is invented, none is
dropped. The Universal Data Meta-Model is the **model-of-the-model**: it fixes exactly the
ten meta-classes (DMC-01…10, §2), the twelve meta-relationships (DMR-01…12, §3), the
meta-constraints (DMK-01…08, §4), and the seven meta-invariants (DMI-01…07, §8) that keep
the model **closed, total, acyclic, reuse-integral, non-constitutive, and non-projective**.
It is the conformance gate every concern architecture (DATA-006…014) — and every realized
concern meta-class DMC-01…10 (units U01…U10) — is validated against.

Shared foundation constants (anchors, laws, compliance conditions, meta-validity gate, CCE
gates, lifecycle states, the ten meta-classes, the twelve meta-relationships) are **reused
by reference** from the CERTIFIED DMC-01 surface (:mod:`data.meta`); re-exported, never
re-defined.
"""

from __future__ import annotations

# --- DMC-01 reuse by reference (UDL-02) — shared foundation constants, never re-defined
from data.meta import (
    CCE_GATES,
    CONSTITUTIONAL_ANCHOR,
    DATA_COMPLIANCE,
    DATA_LAWS,
    IMPLEMENTATION_ANCHOR,
    LIFECYCLE_ORDER,
    META_CLASSES,
    META_RELATIONSHIPS,
    META_VALIDITY_CHECKS,
    DatumState,
)

# ---------------------------------------------------------------------------
# The meta-model follows the frozen ontology lifecycle DOS-01…05 (UDL-12). Identical
# forward-only state machine as every other data construct, reused by reference.
# ---------------------------------------------------------------------------

#: The meta-model lifecycle state type (reused DOS-01…05; UDL-12).
ModelState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 — the meta-model identity (it is the model, not a concern meta-class)
# ---------------------------------------------------------------------------

#: The meta-model "class" label. The Universal Data Meta-Model is **not** one of the ten
#: concern meta-classes (DMI-01 admits no eleventh meta-class); it is the model that fixes
#: them. It is labelled ``UDM`` — the singular model-of-the-model artifact.
MODEL_CLASS = "UDM"

#: The governing architecture the meta-model realizes (DATA-005 §1).
GOVERNING_SPEC = "DATA-005"

# ---------------------------------------------------------------------------
# DATA-005 §2 — the ten meta-classes (DMC-01…10), each modelling one ontology entity
# (DOE-0n, DATA-003 §2) classified by one hierarchy (DXH-0n, DATA-004 §3), realized by
# exactly one CERTIFIED Band-10 unit (U01…U10). No eleventh meta-class (DMI-01).
# ---------------------------------------------------------------------------

#: Each meta-class member spec, verbatim from DATA-005 §2 + the CERTIFIED realization map:
#:   (meta_class, name, models_entity DOE, classified_by DXH, unit, realize_module)
MEMBER_SPECS: tuple[tuple[str, str, str, str, str, str], ...] = (
    ("DMC-01", "Datum", "DOE-01", "DXH-01", "EC3-B10-U01", "data.realize"),
    ("DMC-02", "Entity", "DOE-02", "DXH-02", "EC3-B10-U03", "data.entity_realize"),
    ("DMC-03", "Attribute", "DOE-03", "DXH-03", "EC3-B10-U02", "data.attribute_realize"),
    ("DMC-04", "Relationship", "DOE-04", "DXH-04", "EC3-B10-U10", "data.relationship_realize"),
    ("DMC-05", "Schema", "DOE-05", "DXH-05", "EC3-B10-U04", "data.schema_realize"),
    ("DMC-06", "Storage", "DOE-06", "DXH-06", "EC3-B10-U05", "data.storage_realize"),
    ("DMC-07", "Lifecycle", "DOE-07", "DXH-07", "EC3-B10-U06", "data.lifecycle_realize"),
    ("DMC-08", "Governance-Object", "DOE-08", "DXH-08", "EC3-B10-U07", "data.governance_realize"),
    ("DMC-09", "Quality-Object", "DOE-09", "DXH-09", "EC3-B10-U08", "data.quality_realize"),
    ("DMC-10", "Security-Object", "DOE-10", "DXH-10", "EC3-B10-U09", "data.security_realize"),
)

# ---------------------------------------------------------------------------
# DATA-005 §3 / §9 — the twelve meta-relationships (DMR-01…12), each modelling one
# ontology relationship (DOR-0n), reusing ENG-005 by reference. Sources/targets are the
# meta-model map edges (§9). No thirteenth meta-relationship (DMI-02).
# ---------------------------------------------------------------------------

#: Each meta-relationship edge spec, verbatim from DATA-005 §3/§9:
#:   (relationship DMR, name, models DOR, source meta-class, target)
#: Targets DMR-10/11/12 point to the frozen EL-1/RL-F2/PL-F2 foundations *by reference*.
EDGE_SPECS: tuple[tuple[str, str, str, str, str], ...] = (
    ("DMR-01", "bears", "DOR-01", "DMC-02", "DMC-03"),
    ("DMR-02", "values", "DOR-02", "DMC-03", "DMC-01"),
    ("DMR-03", "relates", "DOR-03", "DMC-02", "DMC-02"),
    ("DMR-04", "described-by", "DOR-04", "DMC-02", "DMC-05"),
    ("DMR-05", "persisted-in", "DOR-05", "DMC-02", "DMC-06"),
    ("DMR-06", "transitions", "DOR-06", "DMC-02", "DMC-07"),
    ("DMR-07", "governed-by", "DOR-07", "DMC-02", "DMC-08"),
    ("DMR-08", "measured-by", "DOR-08", "DMC-02", "DMC-09"),
    ("DMR-09", "classified-by", "DOR-09", "DMC-02", "DMC-10"),
    ("DMR-10", "identified-by", "DOR-10", "DMC-02", "ENG-001"),
    ("DMR-11", "behaves-as", "DOR-11", "DMC-02", "RL-F2"),
    ("DMR-12", "composed-as", "DOR-12", "DMC-02", "PL-F2"),
)

#: The founding meta-relationships (DMK-03 / DMI-04) — the founding meta-graph over these
#: edges is required to be a DAG. Per DATA-005 §4 DMK-03: the founding graph is DMR-01/04.
FOUNDING_META_RELATIONSHIPS: tuple[str, ...] = ("DMR-01", "DMR-04")

#: The frozen foundation targets a meta-relationship may reference (never redefine): EL-1
#: identity (ENG-001 via ENG-002), the RL-F2 runtime concern, the PL-F2 platform concern.
FOUNDATION_TARGETS: tuple[str, ...] = ("ENG-001", "RL-F2", "PL-F2")

# ---------------------------------------------------------------------------
# DATA-003 §2/§3 — the ontology closure sets the meta-model must totally cover (DMI-03).
# ---------------------------------------------------------------------------

#: The ten ontology entities (DOE-01…10) — each modelled by exactly one meta-class (DMI-03).
ONTOLOGY_ENTITIES: tuple[str, ...] = tuple(f"DOE-{n:02d}" for n in range(1, 11))

#: The twelve ontology relationships (DOR-01…12) — each modelled by exactly one
#: meta-relationship (DMI-03).
ONTOLOGY_RELATIONSHIPS: tuple[str, ...] = tuple(f"DOR-{n:02d}" for n in range(1, 13))

# ---------------------------------------------------------------------------
# DATA-005 §8 — the seven meta-invariants (DMI-01…07)
# ---------------------------------------------------------------------------

#: The seven meta-invariants (DATA-005 §8) the realized meta-model must satisfy.
META_INVARIANTS: dict[str, str] = {
    "DMI-01": "Closure — no meta-class outside DMC-01…10.",
    "DMI-02": "Relationship closure — no meta-relationship outside DMR-01…12.",
    "DMI-03": "Totality — every ontology entity/relationship modelled by exactly one.",
    "DMI-04": "Acyclicity — the founding meta-graph (DMR-01/04) is a DAG (DMK-03).",
    "DMI-05": "Reuse integrity — EL-1/RL-F2/PL-F2 referenced, never redefined.",
    "DMI-06": "Non-constitutiveness — no meta-element confers authority or selects technology.",
    "DMI-07": "Non-projection — model coverage is never roadmap completion (STATUS-001 §2).",
}

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-005 §10)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized meta-model records (DATA-005 §10).
TRACE_BACKWARD_MODEL: tuple[str, ...] = (
    MODEL_CLASS,  # the Universal Data Meta-Model artifact (this construct)
    "DATA-005",  # Universal Data Meta-Model (UDM) Master Architecture
    "DATA-004",  # Universal Data Taxonomy (DXH-01…11)
    "DATA-003",  # Universal Data Ontology (DOE-01…10; DOR-01…12)
    "DATA-001",  # Universal Data Constitution (UDL-01…15)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen substrate the meta-model reuses by reference (UDL-02 / DMI-05): the EL-1
#: identity/object/type primitives (via each member), plus the RL-F2 and PL-F2 concerns
#: referenced through DMR-11/DMR-12.
MODEL_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (DMR-10 identified-by; via ENG-002)
    "ENG-002",  # Object     (every meta-class is objecthood-bound — DMK-01)
    "ENG-004",  # Type       (every meta-class is typed — DMK-01)
    "ENG-005",  # Reference  (every meta-relationship IS an ENG-005 reference — §3)
    "RL-F2",  # RUNTIME behaviour concern (DMR-11 behaves-as; by reference)
    "PL-F2",  # PLATFORM composition concern (DMR-12 composed-as; by reference)
)

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the meta-model construct
# ---------------------------------------------------------------------------

#: The Data laws the meta-model construct is directly obligated by. The meta-model is the
#: layer's conformance gate; it materially exercises UDL-02 (reuse-by-reference over all
#: ten CERTIFIED units + EL-1/RL-F2/PL-F2) and UDL-15 (non-constitutive) at the whole-model
#: level, and re-affirms UDL-03/04/05 (typed/identified/objecthood) for its own object.
MODEL_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (all ten units + EL-1/RL-F2/PL-F2) — MATERIAL
    "UDL-03",  # typed (the meta-model object is typed)
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-15",  # non-constitutive — MATERIAL (the model confers no authority, selects no tech)
)

#: Laws scoped to the concern meta-classes (each another realized unit's obligation), not
#: to the integrating meta-model: UDL-06 (value), UDL-07 (entity boundedness), UDL-08
#: (attribute typedness), UDL-09 (relationship), UDL-10 (schema), UDL-11 (storage), UDL-12
#: (lifecycle — the model itself still carries a lifecycle state), UDL-13 (governance),
#: UDL-14 (quality/security). The meta-model *fixes* these laws' meta-shape; it does not
#: re-realize the concern constructs.
MODEL_DEFERRED_LAWS: tuple[str, ...] = (
    "UDL-06",
    "UDL-07",
    "UDL-08",
    "UDL-09",
    "UDL-10",
    "UDL-11",
    "UDL-13",
    "UDL-14",
)

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the meta-model object is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints the meta-model object is bound by (DATA-005 §4).
MODEL_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Every modelled construct is typed (ENG-004), identified (ENG-001), object-bound.",
    "DMK-03": "The founding meta-relationship graph (DMR-01/04) is acyclic (a DAG).",
    "DMK-08": "No modelled construct selects technology or confers authority.",
}

__all__ = [
    # reused-by-reference foundation constants (re-exported, not re-defined)
    "CCE_GATES",
    "CONSTITUTIONAL_ANCHOR",
    "DATA_COMPLIANCE",
    "DATA_LAWS",
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
