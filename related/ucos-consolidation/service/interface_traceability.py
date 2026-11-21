"""EC3-B11-U04 — Interface traceability (No-Orphan closure, GOV-001-T3).

Every realized Interface records a closed lineage (EC-3 AP-3 §5/§9):

* **Backward:** ``SMC-04 → SOE-04 → SERVICE-008 → SERVICE-005 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) + ``RL-F2`` (interaction
  behavior) + ``DF-2`` (carried I/O) — referenced, not redefined (USL-02).
* **Forward:** the realized Interface construct + its validation/certification evidence.

The generic :class:`service.service_traceability.TraceabilityRecord` is **reused verbatim**
(no duplication); this module only supplies the interface-rooted lineage.
"""

from __future__ import annotations

from service.interface import INTERFACE_FOUNDATION_REUSE, Interface
from service.interface_meta import INTERFACE_SUBSTRATE_REFS, TRACE_BACKWARD_INTERFACE
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
InterfaceTraceabilityRecord = TraceabilityRecord


def build_interface_traceability(
    interface: Interface, *, unit: str, forward: tuple[str, ...]
) -> InterfaceTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``interface``."""
    return TraceabilityRecord(
        target_id=interface.interface_id,
        unit=unit,
        meta_class=interface.meta_class,
        backward=TRACE_BACKWARD_INTERFACE,
        substrate=INTERFACE_SUBSTRATE_REFS,
        substrate_reuse=dict(INTERFACE_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["InterfaceTraceabilityRecord", "build_interface_traceability"]
