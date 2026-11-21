"""EC3-B11-U09 — Policy traceability (No-Orphan closure, GOV-001-T3).

Every realized Policy records a closed lineage (EC-3 AP-3 §5/§17):

* **Backward:** ``SMC-09 → SOE-09 → SERVICE-013 → SERVICE-005 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) + ``RL-F2`` (policy-evaluation
  behavior) + ``DF-2`` (predicate data) — referenced, not redefined (USL-02).
* **Forward:** the realized Policy construct + its validation/certification evidence.

The generic :class:`service.service_traceability.TraceabilityRecord` is **reused verbatim**
(no duplication); this module only supplies the policy-rooted lineage.
"""

from __future__ import annotations

from service.policy import POLICY_FOUNDATION_REUSE, Policy
from service.policy_meta import (
    POLICY_SUBSTRATE_REFS,
    TRACE_BACKWARD_POLICY,
)
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
PolicyTraceabilityRecord = TraceabilityRecord


def build_policy_traceability(
    policy: Policy, *, unit: str, forward: tuple[str, ...]
) -> PolicyTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``policy``."""
    return TraceabilityRecord(
        target_id=policy.policy_id,
        unit=unit,
        meta_class=policy.meta_class,
        backward=TRACE_BACKWARD_POLICY,
        substrate=POLICY_SUBSTRATE_REFS,
        substrate_reuse=dict(POLICY_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["PolicyTraceabilityRecord", "build_policy_traceability"]
