"""EC3-B13-U05 — Traceability record (No-Orphan closure, GOV-001-T3).

Every realized Environment & Provisioning construct records a closed lineage
(EC-3-B13-P01 §5), rooted at **its own** leaf meta-class (one of the six concern-011
meta-classes) and closing to the frozen spec anchor:

* **Backward:** ``<meta-class> → INFRASTRUCTURE-011 → INFRASTRUCTURE-005 →
  INFRASTRUCTURE-001 → ARCH-INFRASTRUCTURE-001 → 13-INFRASTRUCTURE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) and ``RL-F2`` (the
  workflow/state a ProvisioningProcess binds) — referenced, not redefined (UIL-02 / UIL-10).
* **Forward:** the realized construct + its validation/certification evidence.

The record is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``
(reuse by reference), so identical inputs yield an identical lineage fingerprint. Its shape
reuses the EC3-B13-U01/U04 :class:`TraceabilityRecord` contract by reference — the same
closed-lineage structure, re-parameterized per construct so a multi-construct unit roots
each construct's lineage at the meta-class it instantiates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.certification.contracts import content_hash
from infrastructure.environment import FOUNDATION_REUSE, _InfraConstruct
from infrastructure.environment_meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    SUBSTRATE_REFS,
    TRACE_TAIL,
)

#: The traceability record format identifier.
TRACE_FORMAT = "ucos-infrastructure-traceability/1.0.0"

#: The anchor prefix the backward lineage must close to (frozen Infrastructure spec set).
_ANCHOR_PREFIX = "13-INFRASTRUCTURE@"


def backward_chain(meta_class: str) -> tuple[str, ...]:
    """The backward lineage for a construct instantiating ``meta_class`` (rooted at it)."""
    return (meta_class, *TRACE_TAIL)


@dataclass(frozen=True, slots=True)
class TraceabilityRecord:
    """A deterministic, closed No-Orphan lineage record for a realized construct."""

    target_id: str
    unit: str
    meta_class: str
    backward: tuple[str, ...]
    substrate: tuple[str, ...]
    substrate_reuse: dict[str, str]
    constitutional_anchor: str
    implementation_anchor: str
    forward: tuple[str, ...]

    @property
    def rooted(self) -> bool:
        """True iff the backward chain is non-empty and rooted at the meta-class."""
        return bool(self.backward) and self.backward[0] == self.meta_class

    @property
    def closed(self) -> bool:
        """True iff backward closes to the 13-INFRASTRUCTURE anchor with substrate/forward."""
        return (
            self.rooted
            and any(link.startswith(_ANCHOR_PREFIX) for link in self.backward)
            and bool(self.substrate)
            and bool(self.forward)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_format": TRACE_FORMAT,
            "target_id": self.target_id,
            "unit": self.unit,
            "meta_class": self.meta_class,
            "backward": list(self.backward),
            "substrate": list(self.substrate),
            "substrate_reuse": dict(self.substrate_reuse),
            "constitutional_anchor": self.constitutional_anchor,
            "implementation_anchor": self.implementation_anchor,
            "forward": list(self.forward),
            "rooted": self.rooted,
            "closed": self.closed,
        }

    def fingerprint(self) -> str:
        """The deterministic content hash of the lineage record."""
        return content_hash(self.to_dict())


def build_traceability(
    construct: _InfraConstruct, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``construct`` (rooted at its meta-class)."""
    return TraceabilityRecord(
        target_id=construct.construct_id,
        unit=unit,
        meta_class=construct.meta_class,
        backward=backward_chain(construct.meta_class),
        substrate=SUBSTRATE_REFS,
        substrate_reuse=dict(FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["TRACE_FORMAT", "backward_chain", "TraceabilityRecord", "build_traceability"]
