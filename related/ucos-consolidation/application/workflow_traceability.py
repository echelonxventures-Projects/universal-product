"""EC3-B12-U05 — Traceability record (No-Orphan closure, GOV-001-T3).

Every realized Workflow records a closed lineage (EC-3 AP-4 §5/§9):

* **Backward:** ``AMC-05 → APPLICATION-009 → APPLICATION-005 → APPLICATION-001 →
  ARCH-APPLICATION-001 → 12-APPLICATION@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1), ``RL-F2``, ``SF-2`` —
  referenced, not redefined (UAL-02). The CERTIFIED AMC-01/AMC-04 units and the downstream
  AMC-07 State are referenced through the workflow's relationships (sequences features/
  operations; consumes SF-2 operations; holds/advances state; behaves-as RL-F2 workflow +
  SF-2 orchestration), never redefined.
* **Forward:** the realized Workflow construct + its validation/certification evidence.

The record is deterministic and content-addressed via the CERTIFIED EC-1
``content_hash`` (reuse by reference), so identical inputs yield an identical lineage
fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.workflow import FOUNDATION_REUSE, Workflow
from application.workflow_meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    REFERENCED_UNITS,
    SUBSTRATE_REFS,
    TRACE_BACKWARD,
)
from engine.certification.contracts import content_hash

#: The traceability record format identifier.
TRACE_FORMAT = "ucos-application-workflow-traceability/1.0.0"

#: The anchor prefix the backward lineage must close to (frozen Application spec set).
_ANCHOR_PREFIX = "12-APPLICATION@"


@dataclass(frozen=True, slots=True)
class TraceabilityRecord:
    """A deterministic, closed No-Orphan lineage record for a realized Workflow."""

    target_id: str
    unit: str
    meta_class: str
    backward: tuple[str, ...]
    substrate: tuple[str, ...]
    substrate_reuse: dict[str, str]
    referenced_units: tuple[str, ...]
    constitutional_anchor: str
    implementation_anchor: str
    forward: tuple[str, ...]

    @property
    def rooted(self) -> bool:
        """True iff the backward chain is non-empty and rooted at the meta-class."""
        return bool(self.backward) and self.backward[0] == self.meta_class

    @property
    def closed(self) -> bool:
        """True iff backward closes to the 12-APPLICATION anchor and substrate/forward present."""
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
            "referenced_units": list(self.referenced_units),
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
    workflow: Workflow, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``workflow``."""
    return TraceabilityRecord(
        target_id=workflow.workflow_id,
        unit=unit,
        meta_class=workflow.meta_class,
        backward=TRACE_BACKWARD,
        substrate=SUBSTRATE_REFS,
        substrate_reuse=dict(FOUNDATION_REUSE),
        referenced_units=REFERENCED_UNITS,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["TRACE_FORMAT", "TraceabilityRecord", "build_traceability"]
