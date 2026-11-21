"""EC3-B11-U13 — Band-11 freeze traceability record (No-Orphan closure, GOV-001-T3).

Every realized Band-11 freeze records a closed lineage:

* **Backward:** ``BAND-11-FREEZE → EC3-B11-U12 →
  SERVICE-015-SERVICE-FOUNDATION-FREEZE-DETERMINATION → MCP-003-MEP-02 → ARCH-SERVICE-001 →
  11-SERVICE@b7e7657``.
* **Frozen units:** the twelve CERTIFIED Band-11 realizations (U01…U12), each cited by
  unit + meta-class + certification id and referenced, not owned (SMX-02 / USL-02).
* **Substrate:** the EC-1 ``engine/**`` certification/validation engines + the CERTIFIED
  SMC-01 CCE ten-gate suite — referenced, not redefined (USL-02).
* **Forward:** the realized freeze baseline record + its validation/certification evidence +
  the freeze completion report.

The record **reuses the CERTIFIED SMC-01 lineage type**
(:class:`service.service_traceability.TraceabilityRecord`) — no parallel traceability
model — and is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from service.band11_freeze import Band11Freeze
from service.band11_freeze_meta import (
    CONSTITUTIONAL_ANCHOR,
    FREEZE_SUBSTRATE_REFS,
    IMPLEMENTATION_ANCHOR,
    TRACE_BACKWARD_FREEZE,
)

# --- SMC-01 reuse by reference (USL-02) — the certified lineage type, never redefined
from service.service_traceability import TraceabilityRecord

#: The EC-1 substrate the freeze reuses by reference (recorded in the lineage).
_FREEZE_REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic baseline seal)",
    "ENG-002": "python frozen object (immutable objecthood bearing the freeze record)",
    "ENG-004": "freeze-record typing discipline (ENG-004)",
    "ENG-005": "each unit referenced by certification id (never owned)",
    "CCE": "service.service_certification.cce_gates — CERTIFIED ten-gate suite, reused verbatim",
}


def build_band11_freeze_traceability(
    freeze: Band11Freeze, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``freeze``.

    The twelve frozen-unit anchors are recorded in the substrate-reuse map so the lineage
    cites every realization the freeze establishes (reused by reference), using the SMC-01
    :class:`TraceabilityRecord` type.
    """
    substrate_reuse = dict(_FREEZE_REUSE_REFS)
    for ref in freeze.units:
        substrate_reuse[f"unit_{ref.unit}"] = (
            f"{ref.meta_class} {ref.name} ({ref.certification_id}) — "
            f"certified realization frozen by reference, not owned"
        )
    return TraceabilityRecord(
        target_id=freeze.freeze_id,
        unit=unit,
        meta_class=freeze.meta_class,
        backward=TRACE_BACKWARD_FREEZE,
        substrate=FREEZE_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["build_band11_freeze_traceability"]
