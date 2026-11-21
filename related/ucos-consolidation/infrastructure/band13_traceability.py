"""EC3-B13-U11 — Band-13 completion traceability record (No-Orphan closure, GOV-001-T3).

Every realized Band-13 completion records a closed lineage:

* **Backward:** ``BAND-13 → MCP-003-MEP-04 → EC-3-AP-5-BAND-13-ADMISSION-DETERMINATION →
  ARCH-INFRASTRUCTURE-001 → 13-INFRASTRUCTURE@b7e7657``.
* **Certified units:** the ten CERTIFIED Band-13 realizations (U01…U10), each cited by unit +
  meta-classes + certification id and referenced, not owned (UIL-02).
* **Substrate:** the EC-1 ``engine/**`` certification/validation engines + the CERTIFIED U01
  CCE ten-gate suite — referenced, not redefined (UIL-02).
* **Forward:** the realized completion record + its validation/certification evidence + the
  completion report.

The record **reuses the CERTIFIED U01 lineage type**
(:class:`infrastructure.capability_traceability.TraceabilityRecord`) — no parallel
traceability model — and is deterministic and content-addressed via the CERTIFIED EC-1
``content_hash``.
"""

from __future__ import annotations

from infrastructure.band13 import Band13Completion
from infrastructure.band13_meta import (
    BAND_SUBSTRATE_REFS,
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    TRACE_BACKWARD_BAND,
)

# --- U01 reuse by reference (UIL-02) — the certified lineage type, never redefined ---
from infrastructure.capability_traceability import TraceabilityRecord

#: The EC-1 substrate the band-completion reuses by reference (recorded in the lineage).
_BAND_REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity)",
    "ENG-002": "python frozen object (immutable objecthood bearing the completion record)",
    "ENG-004": "band-completion typing discipline (ENG-004)",
    "ENG-005": "each unit referenced by certification id (never owned)",
    "CCE": "infrastructure.capability_certification.cce_gates — CERTIFIED ten-gate suite (reused)",
}


def build_band13_traceability(
    completion: Band13Completion, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``completion``.

    The ten certified-unit anchors are recorded in the substrate-reuse map so the lineage
    cites every realization the band certifies (reused by reference), using the CERTIFIED U01
    :class:`TraceabilityRecord` type.
    """
    substrate_reuse = dict(_BAND_REUSE_REFS)
    for ref in completion.units:
        substrate_reuse[f"unit_{ref.unit}"] = (
            f"{'/'.join(ref.meta_classes)} — {ref.name} ({ref.certification_id}) — "
            f"certified realization referenced, not owned"
        )
    return TraceabilityRecord(
        target_id=completion.band_id,
        unit=unit,
        meta_class=completion.meta_class,
        backward=TRACE_BACKWARD_BAND,
        substrate=BAND_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["build_band13_traceability"]
