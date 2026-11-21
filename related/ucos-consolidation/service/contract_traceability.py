"""EC3-B11-U03 — Contract traceability (No-Orphan closure, GOV-001-T3).

Every realized Contract records a closed lineage (EC-3 AP-3 §5/§9):

* **Backward:** ``SMC-03 → SOE-03 → SERVICE-007 → SERVICE-005 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) + ``DF-2`` (typed I/O data,
  by reference) — referenced, not redefined (USL-02).
* **Forward:** the realized Contract construct + its validation/certification evidence.

The generic :class:`service.service_traceability.TraceabilityRecord` is **reused verbatim**
(no duplication); this module only supplies the contract-rooted lineage.
"""

from __future__ import annotations

from service.contract import CONTRACT_FOUNDATION_REUSE, Contract
from service.contract_meta import CONTRACT_SUBSTRATE_REFS, TRACE_BACKWARD_CONTRACT
from service.service_meta import CONSTITUTIONAL_ANCHOR, IMPLEMENTATION_ANCHOR
from service.service_traceability import TraceabilityRecord

#: Reuse the generic traceability record (no parallel model — USL-02).
ContractTraceabilityRecord = TraceabilityRecord


def build_contract_traceability(
    contract: Contract, *, unit: str, forward: tuple[str, ...]
) -> ContractTraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``contract``."""
    return TraceabilityRecord(
        target_id=contract.contract_id,
        unit=unit,
        meta_class=contract.meta_class,
        backward=TRACE_BACKWARD_CONTRACT,
        substrate=CONTRACT_SUBSTRATE_REFS,
        substrate_reuse=dict(CONTRACT_FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["ContractTraceabilityRecord", "build_contract_traceability"]
