"""EC3-B10-U01 — Traceability record (No-Orphan closure, GOV-001-T3).

Every realized Datum records a closed lineage (EC3-B10 package §6):

* **Backward:** ``DMC-01 → DATA-005 → DATA-001 → ARCH-DATA-001 → 10-DATA@b7e7657``.
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/003/004`` — referenced,
  not redefined (UDL-02).
* **Forward:** the realized Datum construct + its validation/certification evidence.

The record is deterministic and content-addressed via the CERTIFIED EC-1
``content_hash`` (reuse by reference), so identical inputs yield an identical
lineage fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.datum import EL1_REUSE, Datum
from data.meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    SUBSTRATE_REFS,
    TRACE_BACKWARD,
)
from engine.certification.contracts import content_hash

#: The traceability record format identifier.
TRACE_FORMAT = "ucos-data-traceability/1.0.0"


@dataclass(frozen=True, slots=True)
class TraceabilityRecord:
    """A deterministic, closed No-Orphan lineage record for a realized Datum."""

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
        """True iff backward closes to the 10-DATA anchor and substrate is present."""
        return (
            self.rooted
            and any(link.startswith("10-DATA@") for link in self.backward)
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


def build_traceability(datum: Datum, *, unit: str, forward: tuple[str, ...]) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``datum``."""
    return TraceabilityRecord(
        target_id=datum.datum_id,
        unit=unit,
        meta_class=datum.meta_class,
        backward=TRACE_BACKWARD,
        substrate=SUBSTRATE_REFS,
        substrate_reuse=dict(EL1_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["TRACE_FORMAT", "TraceabilityRecord", "build_traceability"]
