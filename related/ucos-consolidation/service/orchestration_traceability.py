"""EC3-B11-U07 — Orchestration traceability (No-Orphan closure, GOV-001-T3).

Every realized Orchestration records a closed lineage (EC-3 AP-3 §5/§9):

* **Backward:** ``SMC-07 → SOE-07 → SERVICE-011 → SERVICE-005 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) + ``RL-F2`` (workflow/
  orchestration/event behavior) + ``DF-2`` (inter-step data) — referenced, not redefined
  (USL-02).
* **Forward:** the realized Orchestration construct + its validation/certification evidence.

The generic :class:`service.service_traceability.TraceabilityRecord` is **reused verbatim**
(no duplication); this module only supplies the orchestration-rooted lineage.
"""

from __future__ import annotations

from service.orchestration import ORCHESTRATION_FOUNDATION_REUSE, Orchestration
from service.orchestration_meta import (
    ORCHESTRATION_SUBSTRATE_REFS,
    TRACE_BACKWARD_ORCHESTRATION,
)
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
OrchestrationTraceabilityRecord = TraceabilityRecord


def build_orchestration_traceability(
    orchestration: Orchestration, *, unit: str, forward: tuple[str, ...]
) -> OrchestrationTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``orchestration``."""
    return TraceabilityRecord(
        target_id=orchestration.orchestration_id,
        unit=unit,
        meta_class=orchestration.meta_class,
        backward=TRACE_BACKWARD_ORCHESTRATION,
        substrate=ORCHESTRATION_SUBSTRATE_REFS,
        substrate_reuse=dict(ORCHESTRATION_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["OrchestrationTraceabilityRecord", "build_orchestration_traceability"]
