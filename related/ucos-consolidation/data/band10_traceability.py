"""EC3-B10-U12 — Band-10 completion traceability record (No-Orphan closure, GOV-001-T3).

Every realized Band-10 completion records a closed lineage:

* **Backward:** ``BAND-10 → MCP-003-MEP-01 → EC-3-AP-2-BAND-10-ADMISSION-DETERMINATION →
  ARCH-DATA-001 → 10-DATA@b7e7657``.
* **Certified units:** the eleven CERTIFIED Band-10 realizations (U01…U11), each cited by
  unit + meta-class + certification id and referenced, not owned (DMX-02 / UDL-02).
* **Substrate:** the EC-1 ``engine/**`` certification/validation engines + the CERTIFIED
  DMC-01 CCE ten-gate suite — referenced, not redefined (UDL-02).
* **Forward:** the realized completion record + its validation/certification evidence +
  the completion report.

The record **reuses the CERTIFIED DMC-01 lineage type**
(:class:`data.traceability.TraceabilityRecord`) — no parallel traceability model — and is
deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from data.band10 import Band10Completion
from data.band10_meta import (
    BAND_SUBSTRATE_REFS,
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    TRACE_BACKWARD_BAND,
)

# --- DMC-01 reuse by reference (UDL-02) — the certified lineage type, never redefined
from data.traceability import TraceabilityRecord

#: The EC-1 substrate the band-completion reuses by reference (recorded in the lineage).
_BAND_REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity)",
    "ENG-002": "python frozen object (immutable objecthood bearing the completion record)",
    "ENG-004": "band-completion typing discipline (ENG-004)",
    "ENG-005": "each unit referenced by certification id (never owned)",
    "CCE": "data.certification.cce_gates — the CERTIFIED ten-gate suite, reused verbatim",
}


def build_band10_traceability(
    completion: Band10Completion, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``completion``.

    The eleven certified-unit anchors are recorded in the substrate-reuse map so the
    lineage cites every realization the band certifies (reused by reference), using the
    DMC-01 :class:`TraceabilityRecord` type.
    """
    substrate_reuse = dict(_BAND_REUSE_REFS)
    for ref in completion.units:
        substrate_reuse[f"unit_{ref.unit}"] = (
            f"{ref.meta_class} {ref.name} ({ref.certification_id}) — "
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


__all__ = ["build_band10_traceability"]
