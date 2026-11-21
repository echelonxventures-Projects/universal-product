"""EC3-B11-U08 — Execution traceability (No-Orphan closure, GOV-001-T3).

Every realized Execution records a closed lineage (EC-3 AP-3 §5/§17):

* **Backward:** ``SMC-08 → SOE-08 → SERVICE-012 → SERVICE-005 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) + ``RL-F2`` (execution/state/
  workflow behavior) + ``DF-2`` (read/written data) — referenced, not redefined (USL-02).
* **Forward:** the realized Execution construct + its validation/certification evidence.

The generic :class:`service.service_traceability.TraceabilityRecord` is **reused verbatim**
(no duplication); this module only supplies the execution-rooted lineage.
"""

from __future__ import annotations

from service.execution import EXECUTION_FOUNDATION_REUSE, Execution
from service.execution_meta import (
    EXECUTION_SUBSTRATE_REFS,
    TRACE_BACKWARD_EXECUTION,
)
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
ExecutionTraceabilityRecord = TraceabilityRecord


def build_execution_traceability(
    execution: Execution, *, unit: str, forward: tuple[str, ...]
) -> ExecutionTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``execution``."""
    return TraceabilityRecord(
        target_id=execution.execution_id,
        unit=unit,
        meta_class=execution.meta_class,
        backward=TRACE_BACKWARD_EXECUTION,
        substrate=EXECUTION_SUBSTRATE_REFS,
        substrate_reuse=dict(EXECUTION_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["ExecutionTraceabilityRecord", "build_execution_traceability"]
