"""EC3-B12-U04 — Traceability record (No-Orphan closure, GOV-001-T3).

Every realized Feature records a closed lineage (EC-3 AP-4 §5/§9):

* **Backward:** ``AMC-04 → APPLICATION-008 → APPLICATION-005 → APPLICATION-001 →
  ARCH-APPLICATION-001 → 12-APPLICATION@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1), ``RL-F2``, ``SF-2``,
  ``DF-2`` — referenced, not redefined (UAL-02). The CERTIFIED AMC-02/AMC-03 units and the
  downstream AMC-06 Interaction are referenced through the feature's relationships
  (delivers a Capability; grouped by a Module; engaged-through an Interaction; consumes
  SF-2 operations; presents DF-2 data), never redefined.
* **Forward:** the realized Feature construct + its validation/certification evidence.

The record is deterministic and content-addressed via the CERTIFIED EC-1
``content_hash`` (reuse by reference), so identical inputs yield an identical lineage
fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.feature import FOUNDATION_REUSE, Feature
from application.feature_meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    REFERENCED_UNITS,
    SUBSTRATE_REFS,
    TRACE_BACKWARD,
)
from engine.certification.contracts import content_hash

#: The traceability record format identifier.
TRACE_FORMAT = "ucos-application-feature-traceability/1.0.0"

#: The anchor prefix the backward lineage must close to (frozen Application spec set).
_ANCHOR_PREFIX = "12-APPLICATION@"


@dataclass(frozen=True, slots=True)
class TraceabilityRecord:
    """A deterministic, closed No-Orphan lineage record for a realized Feature."""

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
    feature: Feature, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``feature``."""
    return TraceabilityRecord(
        target_id=feature.feature_id,
        unit=unit,
        meta_class=feature.meta_class,
        backward=TRACE_BACKWARD,
        substrate=SUBSTRATE_REFS,
        substrate_reuse=dict(FOUNDATION_REUSE),
        referenced_units=REFERENCED_UNITS,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["TRACE_FORMAT", "TraceabilityRecord", "build_traceability"]
