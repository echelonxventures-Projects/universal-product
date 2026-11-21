"""EC3-B11-U02 — Capability traceability (No-Orphan closure, GOV-001-T3).

Every realized Capability records a closed lineage (EC-3 AP-3 §5/§9):

* **Backward:** ``SMC-02 → SOE-02 → SERVICE-005 → SERVICE-001 → ARCH-SERVICE-001 →
  11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1), ``RL-F2`` (behavior),
  ``PL-F2``/``PLATFORM-006`` (capability composition) — referenced, not redefined (USL-02).
* **Forward:** the realized Capability construct + its validation/certification evidence.

The generic, content-addressed :class:`service.service_traceability.TraceabilityRecord`
is **reused verbatim** (no duplication); this module only supplies the capability-rooted
lineage. ``CapabilityTraceabilityRecord`` is an alias of that record.
"""

from __future__ import annotations

from service.capability import CAPABILITY_FOUNDATION_REUSE, Capability
from service.capability_meta import (
    CAPABILITY_SUBSTRATE_REFS,
    TRACE_BACKWARD_CAPABILITY,
)
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
CapabilityTraceabilityRecord = TraceabilityRecord


def build_capability_traceability(
    capability: Capability, *, unit: str, forward: tuple[str, ...]
) -> CapabilityTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``capability``."""
    return TraceabilityRecord(
        target_id=capability.capability_id,
        unit=unit,
        meta_class=capability.meta_class,
        backward=TRACE_BACKWARD_CAPABILITY,
        substrate=CAPABILITY_SUBSTRATE_REFS,
        substrate_reuse=dict(CAPABILITY_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["CapabilityTraceabilityRecord", "build_capability_traceability"]
