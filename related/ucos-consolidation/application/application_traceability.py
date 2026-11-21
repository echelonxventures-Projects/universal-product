"""EC3-B12-U01 — Traceability record (No-Orphan closure, GOV-001-T3).

Every realized Application records a closed lineage (EC-3 AP-4 §5/§9):

* **Backward:** ``AMC-01 → APPLICATION-005 → APPLICATION-001 → ARCH-APPLICATION-001 →
  12-APPLICATION@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1), ``RL-F2``, ``PL-F2``,
  ``DF-2``, ``SF-2`` — referenced, not redefined (UAL-02).
* **Forward:** the realized Application construct + its validation/certification evidence.

The record is deterministic and content-addressed via the CERTIFIED EC-1
``content_hash`` (reuse by reference), so identical inputs yield an identical lineage
fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.application import FOUNDATION_REUSE, Application
from application.application_meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    SUBSTRATE_REFS,
    TRACE_BACKWARD,
)
from engine.certification.contracts import content_hash

#: The traceability record format identifier.
TRACE_FORMAT = "ucos-application-traceability/1.0.0"

#: The anchor prefix the backward lineage must close to (frozen Application spec set).
_ANCHOR_PREFIX = "12-APPLICATION@"


@dataclass(frozen=True, slots=True)
class TraceabilityRecord:
    """A deterministic, closed No-Orphan lineage record for a realized Application."""

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
    application: Application, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``application``."""
    return TraceabilityRecord(
        target_id=application.application_id,
        unit=unit,
        meta_class=application.meta_class,
        backward=TRACE_BACKWARD,
        substrate=SUBSTRATE_REFS,
        substrate_reuse=dict(FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["TRACE_FORMAT", "TraceabilityRecord", "build_traceability"]
