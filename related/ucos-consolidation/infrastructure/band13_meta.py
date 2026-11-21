"""EC3-B13-U11 — Band-13 Realization Certification & Completion constants (read-only).

This module carries, as executable constants, the fixed inventory of the ten CERTIFIED
Band-13 (Infrastructure) realization units (U01…U10), the band-level readiness criteria
(mirroring the INFRASTRUCTURE-016 RC-1…RC-8 structure) and completion criteria (mirroring
INFRASTRUCTURE-017 CC-1…CC-8) **applied to the EC-3 Infrastructure (Band-13) code
realization**, and the No-Orphan traceability anchors. It **defines no new infrastructure
concern, no new leaf meta-class, no new ontology, and no new primitive** (UIL-02 / UIL-15):
it names only the already-realized units so the band completion can be checked against them
deterministically.

Distinction (normative). INFRASTRUCTURE-015…018-style architecture-program governance
determinations assess/freeze the INFRASTRUCTURE-001…014 *documents* (physical existence).
This unit (EC3-B13-U11) is the **EC-3 realization** certification: it certifies that the ten
Band-13 *code realizations* (U01…U10, under ``infrastructure/**``) are CCE-COMPLETE and
closed. Its governing determination is the ``MCP-003`` **MEP-04** exit criterion ("Band-13
CCE-COMPLETE + certification") and the ``EC-3-AP-5-BAND-13-ADMISSION-DETERMINATION``; the
readiness/completion criteria mirror the structure of the INFRASTRUCTURE-016/017 band pattern
without re-determining the architecture (charter ``EC-3-B13-P01`` §8).

Shared foundation constants (constitutional/implementation anchors, INFRASTRUCTURE-001 §12
compliance conditions, the seventeen leaf meta-classes, the forward-only lifecycle state) are
**reused by reference** from the CERTIFIED U01 surface (:mod:`infrastructure.capability_meta`);
re-exported, never re-defined (UIL-02).
"""

from __future__ import annotations

# --- U01 reuse by reference (UIL-02) — shared foundation constants, never re-defined ---
from infrastructure.capability_meta import (
    CONSTITUTIONAL_ANCHOR,
    INFRASTRUCTURE_COMPLIANCE,
    LEAF_META_CLASSES,
    InfrastructureState,
)

# ---------------------------------------------------------------------------
# The band-completion record follows the frozen infrastructure lifecycle
# (DEFINED→PROVISIONED→ACTIVE→DECOMMISSIONED; INFRASTRUCTURE-003 §3), reused by reference —
# identical forward-only state machine as every infrastructure construct.
# ---------------------------------------------------------------------------

#: The band-completion lifecycle state type (reused; INFRASTRUCTURE-003 §3).
BandState = InfrastructureState

# ---------------------------------------------------------------------------
# Band identity — the completion record is a certification-of-certifications, NOT an
# eighteenth infrastructure leaf meta-class (it introduces no new meta-class; WF-11 preserved).
# ---------------------------------------------------------------------------

#: The band-completion "class" label. This is a certification/completion record over the
#: EC-3 Band-13 realization; it is **not** one of the seventeen leaf meta-classes.
BAND_CLASS = "BAND-13"

#: The blueprint id the band-completion validation/certification declares (drives the
#: deterministic certification id ``UCOS-CERT-BAND-13-<digest16>``).
BAND_BLUEPRINT_ID = "BAND-13"

#: The deterministic id prefix for a realized Band-13 completion record.
BAND_ID_PREFIX = "UCOS-BAND13"

#: The realization unit this module governs (EC-3 Band 13, Unit 11).
BAND_UNIT = "EC3-B13-U11"

#: The governing determination + program-execution anchor authorizing this certification.
GOVERNING_DETERMINATION = "EC-3-AP-5-BAND-13-ADMISSION-DETERMINATION"
PROGRAM_EXIT_CRITERION = (
    "MCP-003 MEP-04 (All Band-13 units CCE-COMPLETE; Band-13 certification + completion report)"
)

# ---------------------------------------------------------------------------
# The ten CERTIFIED Band-13 realization units (U01…U10). Each entry is verbatim from the
# CERTIFIED realization map (INFRASTRUCTURE-005 §7 leaf-meta-class ownership + the concern
# architectures INFRASTRUCTURE-006…014 + the INFRASTRUCTURE-005 UIMM integration). The nine
# concern units (U01…U09) own the sixteen non-dependency leaf meta-classes; the UIMM
# integration unit (U10) owns the seventeenth leaf (InfrastructureDependency) and integrates
# all nine concerns — the band's capstone.
# ---------------------------------------------------------------------------

#: Each Band-13 unit spec: (unit, meta_classes, name, concern_doc).
#:   meta_classes is the tuple of UIMM leaf meta-classes the unit realizes (a Band-13 unit may
#:   realize a multi-construct concern — e.g. U05 realizes six leaf meta-classes).
#:   concern_doc names the frozen architecture the unit realizes (read-only anchor).
UNIT_INVENTORY: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
    (
        "EC3-B13-U01",
        ("InfrastructureCapability",),
        "Universal Infrastructure Capability",
        "INFRASTRUCTURE-006",
    ),
    ("EC3-B13-U02", ("ComputeResource",), "Universal Infrastructure Compute", "INFRASTRUCTURE-007"),
    ("EC3-B13-U03", ("NetworkResource",), "Universal Infrastructure Network", "INFRASTRUCTURE-008"),
    (
        "EC3-B13-U04",
        ("StorageHostingResource",),
        "Universal Infrastructure Storage-Hosting",
        "INFRASTRUCTURE-009",
    ),
    (
        "EC3-B13-U05",
        ("Locality", "IsolationBoundary", "Node", "Cluster", "Environment", "ProvisioningProcess"),
        "Universal Infrastructure Environment & Provisioning",
        "INFRASTRUCTURE-011",
    ),
    (
        "EC3-B13-U06",
        ("Topology", "Distribution"),
        "Universal Infrastructure Topology & Distribution",
        "INFRASTRUCTURE-010",
    ),
    (
        "EC3-B13-U07",
        ("AvailabilityTopology", "ScalingArrangement"),
        "Universal Infrastructure Resilience & Availability",
        "INFRASTRUCTURE-012",
    ),
    ("EC3-B13-U08", ("SecurityFacet",), "Universal Infrastructure Security", "INFRASTRUCTURE-013"),
    (
        "EC3-B13-U09",
        ("GovernanceFacet",),
        "Universal Infrastructure Governance",
        "INFRASTRUCTURE-014",
    ),
    (
        "EC3-B13-U10",
        ("InfrastructureDependency",),
        "Universal Infrastructure Integration (UIMM)",
        "INFRASTRUCTURE-005",
    ),
)

#: The exact number of Band-13 realization units the completion must cover (U01…U10).
EXPECTED_UNIT_COUNT = len(UNIT_INVENTORY)

#: The set of unit ids the completion must inventory (decidable closure).
EXPECTED_UNITS: tuple[str, ...] = tuple(spec[0] for spec in UNIT_INVENTORY)

#: The seventeen UIMM leaf meta-classes the band's units cover, reused by reference from the
#: CERTIFIED foundation — the band realizes exactly these, no eighteenth (INFRASTRUCTURE-005
#: §2 / §7).
BAND_META_CLASSES: tuple[str, ...] = tuple(LEAF_META_CLASSES)

#: The integration/meta-model unit that composes the nine concerns and closes the leaf
#: closure (U10, the UIMM InfrastructureDependency capstone) — the band's capstone.
META_MODEL_UNIT = "EC3-B13-U10"

# ---------------------------------------------------------------------------
# Band-13 READINESS criteria (charter EC-3-B13-P01 §8; mirror the INFRASTRUCTURE-016
# RC-1…RC-8 pattern, applied to the EC-3 realization).
# ---------------------------------------------------------------------------

#: The band readiness criteria, verbatim from charter §8, each substantiated by validation
#: check ids (see band13_realize._BRC_CHECKS).
BAND_READINESS_CRITERIA: dict[str, str] = {
    "BRC-1": "Completeness — every leaf meta-class realized (all ten concern units CERTIFIED).",
    "BRC-2": "Dependency closure — realized founding graph downward-only, acyclic, closed.",
    "BRC-3": "Coverage — each UIMM leaf owned by exactly one unit; complete and non-overlapping.",
    "BRC-4": "Consistency — no contradiction across units; UIL/WF alignments hold (UIMM closure).",
    "BRC-5": "Reuse integrity — no redefinition; no new primitive; frozen refs intact.",
    "BRC-6": "Foundation intact — EC-1/EC-2/DF-2/SF-2/AF freeze preserved (non-constitutive).",
    "BRC-7": "Discipline conformance — every unit passed UCIC-001 + CCE + determinism.",
    "BRC-8": "Meta-validity — U10 UIMM CERTIFIED; UIMM-CONF total over the realized set.",
}

# ---------------------------------------------------------------------------
# Band-13 COMPLETION criteria (charter EC-3-B13-P01 §8; mirror the INFRASTRUCTURE-017
# CC-1…CC-8 pattern, applied to the EC-3 realization).
# ---------------------------------------------------------------------------

#: The band completion criteria, decided on the same validation evidence.
BAND_COMPLETION_CRITERIA: dict[str, str] = {
    "BCC-1": "Completeness — all ten realization units physically exist and are CERTIFIED.",
    "BCC-2": "Predecessor units frozen-clean — no certified unit mutated (reuse by reference).",
    "BCC-3": "Readiness discharged — the band readiness criteria BRC-1…8 all PASS.",
    "BCC-4": "Dependency closure — downward-only, acyclic; no forward/upward dependency.",
    "BCC-5": "Consistency — the UIMM integration closes over the ten realized units.",
    "BCC-6": "Reuse integrity — no EL-1/prior-unit concept redefined; no new primitive.",
    "BCC-7": "Discipline conformance per unit — UCIC-001 + CCE + determinism.",
    "BCC-8": "Governance records — all evidence bundles + completion reports present (traceable).",
}

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine) — the band certification's lineage.
# ---------------------------------------------------------------------------

#: The backward traceability chain the band-completion records (rooted at BAND-13).
TRACE_BACKWARD_BAND: tuple[str, ...] = (
    BAND_CLASS,  # the Band-13 completion record (this construct)
    "MCP-003-MEP-04",  # program-execution exit criterion authorizing band certification
    GOVERNING_DETERMINATION,  # EC-3 Band-13 admission determination (AP-5 SATISFIED)
    "ARCH-INFRASTRUCTURE-001",  # governing Infrastructure architecture model
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen spec set (INFRASTRUCTURE-001…018)
)

#: Implementation substrate anchor: the certified baseline this band-completion builds upon
#: (U10 UIMM integration realized/certified at commit ``2dee20b``; U01…U10 CERTIFIED &
#: COMPLETE, U08/U09/U10 also PROVISIONALLY RATIFIED via S4-06/S4-11/S4-12).
IMPLEMENTATION_ANCHOR = "2dee20b"

#: The frozen substrate the band-completion reuses by reference (UIL-02): the EC-1
#: certification/validation engines and the ten CERTIFIED unit realizations.
BAND_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity (deterministic id derivation via ENG-002)
    "ENG-002",  # Object (immutable objecthood bearing the completion record)
    "ENG-004",  # Type (the completion record is typed)
    "ENG-005",  # Reference (every unit is referenced by certification id, never owned)
    "CCE",  # the CERTIFIED ten-gate certification suite (reused verbatim)
)

__all__ = [
    # reused-by-reference foundation constants (re-exported, not re-defined)
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "INFRASTRUCTURE_COMPLIANCE",
    "LEAF_META_CLASSES",
    "BandState",
    # band-completion-specific projections
    "BAND_CLASS",
    "BAND_BLUEPRINT_ID",
    "BAND_ID_PREFIX",
    "BAND_UNIT",
    "GOVERNING_DETERMINATION",
    "PROGRAM_EXIT_CRITERION",
    "UNIT_INVENTORY",
    "EXPECTED_UNIT_COUNT",
    "EXPECTED_UNITS",
    "BAND_META_CLASSES",
    "META_MODEL_UNIT",
    "BAND_READINESS_CRITERIA",
    "BAND_COMPLETION_CRITERIA",
    "TRACE_BACKWARD_BAND",
    "BAND_SUBSTRATE_REFS",
]
