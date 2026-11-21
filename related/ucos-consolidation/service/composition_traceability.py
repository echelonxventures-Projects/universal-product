"""EC3-B11-U06 — Composition traceability (No-Orphan closure, GOV-001-T3).

Every realized Composition records a closed lineage (EC-3 AP-3 §5/§9):

* **Backward:** ``SMC-06 → SOE-06 → SERVICE-010 → SERVICE-005 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) + ``PL-F2`` (composition/
  integration) + ``RL-F2`` (delegated invocation) + ``DF-2`` (cross-composition data) —
  referenced, not redefined (USL-02).
* **Forward:** the realized Composition construct + its validation/certification evidence.

The generic :class:`service.service_traceability.TraceabilityRecord` is **reused verbatim**
(no duplication); this module only supplies the composition-rooted lineage.
"""

from __future__ import annotations

from service.composition import COMPOSITION_FOUNDATION_REUSE, Composition
from service.composition_meta import COMPOSITION_SUBSTRATE_REFS, TRACE_BACKWARD_COMPOSITION
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
CompositionTraceabilityRecord = TraceabilityRecord


def build_composition_traceability(
    composition: Composition, *, unit: str, forward: tuple[str, ...]
) -> CompositionTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``composition``."""
    return TraceabilityRecord(
        target_id=composition.composition_id,
        unit=unit,
        meta_class=composition.meta_class,
        backward=TRACE_BACKWARD_COMPOSITION,
        substrate=COMPOSITION_SUBSTRATE_REFS,
        substrate_reuse=dict(COMPOSITION_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["CompositionTraceabilityRecord", "build_composition_traceability"]
