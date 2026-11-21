"""EC2-TASK-000102 — Blueprint Derived Status (EC2-EPIC-006).

The deterministic **derived-status** computation. A blueprint's derived status is a
**pure function** of its stored lifecycle state, its provenance presence (link-4), and
its association posture — it consults no wall-clock and no external state, so identical
inputs always yield an identical :class:`DerivedBlueprintStatus` and an identical
fingerprint (P5).

The derived posture summarizes lifecycle + traceability:

    * ``RETIRED``    — the blueprint is in the terminal retired state.
    * ``SUPERSEDED`` — a later version supersedes this blueprint.
    * ``CATALOGUED`` — the blueprint is published in the L6 catalog.
    * ``VALIDATED``  — structurally validated + classified, not yet cataloged.
    * ``DRAFT``      — authored/imported, not yet validated.

This module records/enacts nothing; it derives.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from platform.blueprints.associations import (
    BlueprintAssociation,
    BlueprintAssociationKind,
    all_association_kinds,
)
from platform.blueprints.contracts import Blueprint, BlueprintStatus
from platform.blueprints.errors import BlueprintStatusError
from platform.foundation.contracts import content_hash
from typing import Any


class BlueprintPosture(str, Enum):
    """The deterministic derived posture of a blueprint (lifecycle + traceability)."""

    RETIRED = "retired"
    SUPERSEDED = "superseded"
    CATALOGUED = "catalogued"
    VALIDATED = "validated"
    DRAFT = "draft"


@dataclass(frozen=True, slots=True)
class DerivedBlueprintStatus:
    """An immutable, content-addressed derived blueprint status (pure function output)."""

    blueprint_id: str
    lifecycle_status: BlueprintStatus
    posture: BlueprintPosture
    has_provenance: bool
    is_traceable: bool
    association_total: int
    association_counts: tuple[tuple[str, int], ...]
    status_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        blueprint_id: str,
        lifecycle_status: BlueprintStatus,
        posture: BlueprintPosture,
        has_provenance: bool,
        association_counts: tuple[tuple[str, int], ...],
    ) -> DerivedBlueprintStatus:
        total = sum(count for _, count in association_counts)
        # A blueprint is traceable (link-4 present) iff it is cataloged with provenance.
        is_traceable = has_provenance and posture in (
            BlueprintPosture.CATALOGUED,
            BlueprintPosture.SUPERSEDED,
        )
        core = {
            "blueprint_id": blueprint_id,
            "lifecycle_status": lifecycle_status.value,
            "posture": posture.value,
            "has_provenance": has_provenance,
            "is_traceable": is_traceable,
            "association_total": total,
            "association_counts": [list(pair) for pair in association_counts],
        }
        return cls(
            blueprint_id=blueprint_id,
            lifecycle_status=lifecycle_status,
            posture=posture,
            has_provenance=has_provenance,
            is_traceable=is_traceable,
            association_total=total,
            association_counts=association_counts,
            status_id=f"UCOS-BDST-{content_hash(core)[:16]}",
        )

    @property
    def is_associated(self) -> bool:
        """True iff the blueprint has at least one association."""
        return self.association_total > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_id": self.status_id,
            "blueprint_id": self.blueprint_id,
            "lifecycle_status": self.lifecycle_status.value,
            "posture": self.posture.value,
            "has_provenance": self.has_provenance,
            "is_traceable": self.is_traceable,
            "association_total": self.association_total,
            "association_counts": {kind: count for kind, count in self.association_counts},
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _counts_by_kind(
    associations: Iterable[BlueprintAssociation],
) -> tuple[tuple[str, int], ...]:
    """Deterministic per-kind association counts (every kind present, stable order)."""
    tally: dict[BlueprintAssociationKind, int] = {kind: 0 for kind in all_association_kinds()}
    for association in associations:
        if not isinstance(association, BlueprintAssociation):
            raise BlueprintStatusError("status derivation requires BlueprintAssociation records")
        tally[association.kind] += 1
    return tuple((kind.value, tally[kind]) for kind in all_association_kinds())


def _posture(status: BlueprintStatus) -> BlueprintPosture:
    return {
        BlueprintStatus.RETIRED: BlueprintPosture.RETIRED,
        BlueprintStatus.SUPERSEDED: BlueprintPosture.SUPERSEDED,
        BlueprintStatus.CATALOGUED: BlueprintPosture.CATALOGUED,
        BlueprintStatus.VALIDATED: BlueprintPosture.VALIDATED,
        BlueprintStatus.DRAFT: BlueprintPosture.DRAFT,
    }[status]


def derive_status(
    blueprint: Blueprint,
    associations: Iterable[BlueprintAssociation],
    *,
    has_provenance: bool,
) -> DerivedBlueprintStatus:
    """Derive a deterministic :class:`DerivedBlueprintStatus` (pure; fail-closed)."""
    if not isinstance(blueprint, Blueprint):
        raise BlueprintStatusError("status derivation requires a Blueprint")
    if not isinstance(has_provenance, bool):
        raise BlueprintStatusError("has_provenance must be a bool")
    counts = _counts_by_kind(associations)
    return DerivedBlueprintStatus.create(
        blueprint_id=blueprint.blueprint_id,
        lifecycle_status=blueprint.status,
        posture=_posture(blueprint.status),
        has_provenance=has_provenance,
        association_counts=counts,
    )


__all__ = [
    "BlueprintPosture",
    "DerivedBlueprintStatus",
    "derive_status",
]
