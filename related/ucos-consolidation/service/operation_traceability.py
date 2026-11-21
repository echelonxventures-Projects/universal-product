"""EC3-B11-U05 — Operation traceability (No-Orphan closure, GOV-001-T3).

Every realized Operation records a closed lineage (EC-3 AP-3 §5/§9):

* **Backward:** ``SMC-05 → SOE-05 → SERVICE-009 → SERVICE-005 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) + ``RL-F2`` (execution/
  behavior) + ``DF-2`` (typed I/O) — referenced, not redefined (USL-02).
* **Forward:** the realized Operation construct + its validation/certification evidence.

The generic :class:`service.service_traceability.TraceabilityRecord` is **reused verbatim**
(no duplication); this module only supplies the operation-rooted lineage.
"""

from __future__ import annotations

from service.operation import OPERATION_FOUNDATION_REUSE, Operation
from service.operation_meta import OPERATION_SUBSTRATE_REFS, TRACE_BACKWARD_OPERATION
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
OperationTraceabilityRecord = TraceabilityRecord


def build_operation_traceability(
    operation: Operation, *, unit: str, forward: tuple[str, ...]
) -> OperationTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``operation``."""
    return TraceabilityRecord(
        target_id=operation.operation_id,
        unit=unit,
        meta_class=operation.meta_class,
        backward=TRACE_BACKWARD_OPERATION,
        substrate=OPERATION_SUBSTRATE_REFS,
        substrate_reuse=dict(OPERATION_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["OperationTraceabilityRecord", "build_operation_traceability"]
