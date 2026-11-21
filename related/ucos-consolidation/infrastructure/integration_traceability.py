"""EC3-B13-U10 — Traceability record (No-Orphan closure, GOV-001-T3).

Every realized InfrastructureDependency records a closed lineage (EC-3-B13-P01 §5), rooted
at its leaf meta-class (**InfrastructureDependency**) and closing to the frozen spec anchor —
binding the chain **construct → evidence → registry → certification**:

* **Backward:** ``InfrastructureDependency → INFRASTRUCTURE-018 → INFRASTRUCTURE-005 →
  INFRASTRUCTURE-001 → ARCH-INFRASTRUCTURE-001 → 13-INFRASTRUCTURE@b7e7657``.
* **Substrate:** the frozen foundations ``ENG-001…005`` (EL-1) — a dependency ``«⊑ ENG-005
  reference»`` reuses the frozen reference by reference (UIL-02 / UIL-09).
* **Endpoints:** the two already-CERTIFIED concern units the edge composes, referenced by
  their ``EC3-B13-U0N`` ids (reuse-by-reference — never re-implemented).
* **Forward:** the realized construct id → its validation/certification evidence → the
  completion report (the registry/certification linkage).

The record is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``
(reuse by reference), so identical inputs yield an identical lineage fingerprint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.certification.contracts import content_hash
from infrastructure.integration import InfrastructureDependency
from infrastructure.integration_meta import (
    CONSTITUTIONAL_ANCHOR,
    FOUNDATION_REUSE,
    IMPLEMENTATION_ANCHOR,
    SUBSTRATE_REFS,
    TRACE_TAIL,
)

TRACE_FORMAT = "ucos-infrastructure-traceability/1.0.0"
_ANCHOR_PREFIX = "13-INFRASTRUCTURE@"


def backward_chain(meta_class: str) -> tuple[str, ...]:
    """The backward lineage for a construct instantiating ``meta_class`` (rooted at it)."""
    return (meta_class, *TRACE_TAIL)


@dataclass(frozen=True, slots=True)
class TraceabilityRecord:
    """A deterministic, closed No-Orphan lineage record for a realized dependency."""

    target_id: str
    unit: str
    meta_class: str
    source_ref: str
    target_ref: str
    basis: str
    backward: tuple[str, ...]
    substrate: tuple[str, ...]
    substrate_reuse: dict[str, str]
    constitutional_anchor: str
    implementation_anchor: str
    forward: tuple[str, ...]

    @property
    def rooted(self) -> bool:
        return bool(self.backward) and self.backward[0] == self.meta_class

    @property
    def closed(self) -> bool:
        return (
            self.rooted
            and any(link.startswith(_ANCHOR_PREFIX) for link in self.backward)
            and bool(self.substrate)
            and bool(self.forward)
            and bool(self.source_ref)
            and bool(self.target_ref)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_format": TRACE_FORMAT,
            "target_id": self.target_id,
            "unit": self.unit,
            "meta_class": self.meta_class,
            "source_ref": self.source_ref,
            "target_ref": self.target_ref,
            "basis": self.basis,
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
        return content_hash(self.to_dict())


def build_traceability(
    dependency: InfrastructureDependency, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``dependency``."""
    return TraceabilityRecord(
        target_id=dependency.construct_id,
        unit=unit,
        meta_class=dependency.meta_class,
        source_ref=dependency.source_ref,
        target_ref=dependency.target_ref,
        basis=dependency.basis,
        backward=backward_chain(dependency.meta_class),
        substrate=SUBSTRATE_REFS,
        substrate_reuse=dict(FOUNDATION_REUSE),
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["TRACE_FORMAT", "backward_chain", "TraceabilityRecord", "build_traceability"]
