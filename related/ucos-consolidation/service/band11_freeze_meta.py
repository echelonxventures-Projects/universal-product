"""EC3-B11-U13 — Band-11 Freeze constants (read-only).

This module carries, as executable constants, the fixed inventory of the **twelve
CERTIFIED Band-11 realization units** the freeze permanently establishes as the canonical
Band-11 baseline (U01…U10 concern meta-classes + U11 USM + U12 Band-11 Realization
Certification & Completion), the freeze preconditions (mirroring the SERVICE-015 P-1…P-6
structure), the freeze effects (mirroring SERVICE-015 OUTPUT 3), and the No-Orphan
traceability anchors. It **defines no new service concern, no new meta-class, no new
ontology, and no new primitive** (USL-02 / USL-15): it names only the already-CERTIFIED
units so the freeze baseline can be checked against them deterministically.

Distinction (normative). ``SERVICE-015`` (Service Foundation Freeze Determination) is the
*governance* determination that freezes the SERVICE-001…005 *documents* (physical
existence). This unit (EC3-B11-U13) is the **EC-3 realization** freeze: it establishes the
immutable certified baseline of the whole Band-11 *code realization* (U01…U12, under
``service/**``) — a content-addressed baseline record over the twelve CERTIFIED units and
the U12 certification-of-certifications. Its governing determination is the ``SERVICE-015``
freeze pattern applied to the EC-3 realization, discharged after the ``MCP-003`` **MEP-02**
exit criterion (Band-11 CERTIFIED-COMPLETE). It creates no new architecture, mutates no
frozen or certified artifact, and is append-only.

Shared foundation constants (constitutional/implementation anchors, SERVICE-001 §12
compliance conditions, the ten meta-classes, the SOS lifecycle state) and the eleven-unit
realization inventory are **reused by reference** from the CERTIFIED SMC-01 surface
(:mod:`service.service_meta`) and the CERTIFIED U12 band surface
(:mod:`service.band11_meta`); re-exported, never re-defined.
"""

from __future__ import annotations

# --- U12 reuse by reference (USL-02) — the eleven-unit realization inventory + anchors
from service.band11_meta import (
    BAND_META_CLASSES,
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    META_MODEL_UNIT,
    SERVICE_COMPLIANCE,
    UNIT_INVENTORY,
    BandState,
)

# ---------------------------------------------------------------------------
# The freeze record follows the frozen service lifecycle SOS-01…06 (USL-12), reused by
# reference — identical forward-only state machine as every service construct.
# ---------------------------------------------------------------------------

#: The freeze-record lifecycle state type (reused SOS-01…06; USL-12).
FreezeState = BandState

# ---------------------------------------------------------------------------
# Freeze identity — the freeze record is an immutable baseline, NOT a service concern
# meta-class (it introduces no meta-class; SMI-01 is preserved).
# ---------------------------------------------------------------------------

#: The freeze "class" label. This is a baseline/freeze record over the EC-3 Band-11
#: realization; it is **not** one of the ten service meta-classes.
FREEZE_CLASS = "BAND-11-FREEZE"

#: The blueprint id the freeze validation/certification declares (drives the deterministic
#: certification id ``UCOS-CERT-BAND-11-FREEZE-<digest16>``).
FREEZE_BLUEPRINT_ID = "BAND-11-FREEZE"

#: The deterministic id prefix for a realized Band-11 freeze baseline record.
FREEZE_ID_PREFIX = "UCOS-FREEZE-BAND11"

#: The realization unit this module governs (EC-3 Band 11, Unit 13).
FREEZE_UNIT = "EC3-B11-U13"

#: The band-completion (certification-of-certifications) unit the freeze crowns (U12).
BAND_COMPLETION_UNIT = "EC3-B11-U12"

#: The meta-model unit that integrates the ten meta-classes (U11) — reused by reference.
FREEZE_META_MODEL_UNIT = META_MODEL_UNIT

#: The governing determination authorizing this freeze (SERVICE-015 pattern) + the program
#: exit criterion that must be satisfied first (Band-11 CERTIFIED-COMPLETE).
GOVERNING_DETERMINATION = "SERVICE-015-SERVICE-FOUNDATION-FREEZE-DETERMINATION"
PROGRAM_EXIT_CRITERION = (
    "MCP-003 MEP-02 (Band-11 CERTIFIED-COMPLETE; U01…U12) → Band-11 Freeze"
)

# ---------------------------------------------------------------------------
# The twelve CERTIFIED Band-11 realization units the freeze establishes as the baseline.
# U01…U11 are reused verbatim from the CERTIFIED U12 inventory; U12 (the band completion,
# the certification-of-certifications) is the twelfth frozen unit.
# ---------------------------------------------------------------------------

#: Each frozen unit spec: (unit, meta_class, name, concern_doc).
FROZEN_UNIT_INVENTORY: tuple[tuple[str, str, str, str], ...] = UNIT_INVENTORY + (
    (
        BAND_COMPLETION_UNIT,
        FREEZE_CLASS.replace("-FREEZE", ""),  # "BAND-11"
        "Band-11 Realization Certification & Completion",
        "MCP-003 MEP-02 (certification-of-certifications over U01…U11)",
    ),
)

#: The exact number of Band-11 units the freeze must cover (U01…U12).
EXPECTED_FROZEN_UNIT_COUNT = len(FROZEN_UNIT_INVENTORY)

#: The set of unit ids the freeze must inventory (decidable closure).
EXPECTED_FROZEN_UNITS: tuple[str, ...] = tuple(spec[0] for spec in FROZEN_UNIT_INVENTORY)

#: The ten service meta-classes the concern units cover (SMC-01…10), reused by reference —
#: the freeze establishes exactly these, no eleventh (the U11/U12 units carry non-SMC
#: labels and are excluded from concern-coverage).
FREEZE_META_CLASSES: tuple[str, ...] = tuple(BAND_META_CLASSES)

#: The non-concern (capstone) meta-class labels excluded from meta-class coverage.
NON_CONCERN_LABELS: frozenset[str] = frozenset({"USM", "BAND-11"})

# ---------------------------------------------------------------------------
# Band-11 Freeze PRECONDITIONS (mirror the SERVICE-015 P-1…P-6 pattern, applied to EC-3).
# ---------------------------------------------------------------------------

#: The freeze preconditions, each substantiated by validation check ids (below).
FREEZE_PRECONDITIONS: dict[str, str] = {
    "FP-1": "Existence — all twelve realization units U01…U12 exist and are CERTIFIED.",
    "FP-2": "Dependency closure — the frozen unit founding graph is acyclic and downward-only.",
    "FP-3": "Coverage — the concern units cover exactly the ten meta-classes SMC-01…10.",
    "FP-4": "Consistency — the U12 band completion is CERTIFIED; the spine closes SMR-01…13.",
    "FP-5": "Reuse integrity — every unit reused by reference; no redefinition, no new primitive.",
    "FP-6": "Determinism — the freeze baseline recomputes byte-identically.",
}

# ---------------------------------------------------------------------------
# Band-11 Freeze EFFECTS (mirror the SERVICE-015 OUTPUT 3 freeze effects, applied to EC-3).
# ---------------------------------------------------------------------------

#: The freeze effects the baseline permanently establishes.
FREEZE_EFFECTS: dict[str, str] = {
    "FE-1": "Immutability — no in-place modification of any frozen unit U01…U12.",
    "FE-2": "Reuse mandate — downstream bands consume the Band-11 realization by reference.",
    "FE-3": "Redefinition prohibition — no frozen construct, meta-class, or law is redefined.",
    "FE-4": "Additive extension — new service concerns extend above, never inside, the baseline.",
    "FE-5": "Supersession-only change — breaking change is a new artifact under ENG-000 control.",
}

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine) — the freeze's lineage.
# ---------------------------------------------------------------------------

#: The backward traceability chain the freeze records (rooted at BAND-11-FREEZE).
TRACE_BACKWARD_FREEZE: tuple[str, ...] = (
    FREEZE_CLASS,  # the Band-11 freeze baseline record (this construct)
    BAND_COMPLETION_UNIT,  # the U12 certification-of-certifications it crowns
    GOVERNING_DETERMINATION,  # SERVICE-015 freeze determination (freeze pattern)
    "MCP-003-MEP-02",  # program-execution exit criterion (Band-11 CERTIFIED-COMPLETE)
    "ARCH-SERVICE-001",  # governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set (SERVICE-001…018)
)

#: The frozen substrate the freeze reuses by reference (USL-02): the EC-1
#: certification/validation engines and the twelve CERTIFIED Band-11 unit realizations.
FREEZE_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity (deterministic id derivation via ENG-002)
    "ENG-002",  # Object (immutable objecthood bearing the freeze record)
    "ENG-004",  # Type (the freeze record is typed)
    "ENG-005",  # Reference (every unit is referenced by certification id, never owned)
    "CCE",  # the CERTIFIED ten-gate certification suite (reused verbatim)
)

__all__ = [
    # reused-by-reference foundation constants (re-exported, not re-defined)
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "SERVICE_COMPLIANCE",
    "FreezeState",
    # freeze-specific projections
    "FREEZE_CLASS",
    "FREEZE_BLUEPRINT_ID",
    "FREEZE_ID_PREFIX",
    "FREEZE_UNIT",
    "BAND_COMPLETION_UNIT",
    "FREEZE_META_MODEL_UNIT",
    "GOVERNING_DETERMINATION",
    "PROGRAM_EXIT_CRITERION",
    "FROZEN_UNIT_INVENTORY",
    "EXPECTED_FROZEN_UNIT_COUNT",
    "EXPECTED_FROZEN_UNITS",
    "FREEZE_META_CLASSES",
    "NON_CONCERN_LABELS",
    "FREEZE_PRECONDITIONS",
    "FREEZE_EFFECTS",
    "TRACE_BACKWARD_FREEZE",
    "FREEZE_SUBSTRATE_REFS",
]
