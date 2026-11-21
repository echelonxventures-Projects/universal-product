"""EC3-B11-U10 — Security traceability (No-Orphan closure, GOV-001-T3).

Every realized Security object records a closed lineage (EC-3 AP-3 §5/§17):

* **Backward:** ``SMC-10 → SOE-10 → SERVICE-014 → SERVICE-005 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) + ``RL-F2`` (policy-evaluation
  behavior; RUNTIME-010) + ``DF-2`` (confidentiality/integrity data; DATA-014) — referenced,
  not redefined (USL-02).
* **Forward:** the realized Security construct + its validation/certification evidence.

The generic :class:`service.service_traceability.TraceabilityRecord` is **reused verbatim**
(no duplication); this module only supplies the security-rooted lineage.
"""

from __future__ import annotations

from service.security import SECURITY_FOUNDATION_REUSE, Security
from service.security_meta import (
    SECURITY_SUBSTRATE_REFS,
    TRACE_BACKWARD_SECURITY,
)
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
SecurityTraceabilityRecord = TraceabilityRecord


def build_security_traceability(
    security: Security, *, unit: str, forward: tuple[str, ...]
) -> SecurityTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``security``."""
    return TraceabilityRecord(
        target_id=security.security_id,
        unit=unit,
        meta_class=security.meta_class,
        backward=TRACE_BACKWARD_SECURITY,
        substrate=SECURITY_SUBSTRATE_REFS,
        substrate_reuse=dict(SECURITY_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["SecurityTraceabilityRecord", "build_security_traceability"]
