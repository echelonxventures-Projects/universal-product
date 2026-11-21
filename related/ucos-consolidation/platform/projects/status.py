"""EC2-TASK-000093 — Project Derived Status (EC2-EPIC-005).

The deterministic **derived-status** computation (Program §5 "status derivable
deterministically"). A project's derived status is a **pure function** of its stored
lifecycle state plus its association posture — it consults no wall-clock and no
external state, so identical inputs always yield an identical
:class:`DerivedProjectStatus` and an identical fingerprint (P5).

The derived posture summarizes lifecycle + associations:

    * ``ARCHIVED``  — the project is in the terminal archived state.
    * ``COMPLETED`` — the project lifecycle is completed.
    * ``SUSPENDED`` — the project lifecycle is suspended.
    * ``EMPTY``     — the project is active with **no** associations.
    * ``POPULATED`` — the project is active with **at least one** association.

This module records/enacts nothing; it derives.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.projects.contracts import (
    AssociationKind,
    Project,
    ProjectAssociation,
    ProjectStatus,
    all_association_kinds,
)
from platform.projects.errors import ProjectStatusError
from typing import Any


class ProjectPosture(str, Enum):
    """The deterministic derived posture of a project (lifecycle + associations)."""

    ARCHIVED = "archived"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    EMPTY = "empty"
    POPULATED = "populated"


@dataclass(frozen=True, slots=True)
class DerivedProjectStatus:
    """An immutable, content-addressed derived project status (pure function output)."""

    project_id: str
    lifecycle_status: ProjectStatus
    posture: ProjectPosture
    association_total: int
    association_counts: tuple[tuple[str, int], ...]
    status_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        project_id: str,
        lifecycle_status: ProjectStatus,
        posture: ProjectPosture,
        association_counts: tuple[tuple[str, int], ...],
    ) -> DerivedProjectStatus:
        total = sum(count for _, count in association_counts)
        core = {
            "project_id": project_id,
            "lifecycle_status": lifecycle_status.value,
            "posture": posture.value,
            "association_total": total,
            "association_counts": [list(pair) for pair in association_counts],
        }
        return cls(
            project_id=project_id,
            lifecycle_status=lifecycle_status,
            posture=posture,
            association_total=total,
            association_counts=association_counts,
            status_id=f"UCOS-PDST-{content_hash(core)[:16]}",
        )

    @property
    def is_associated(self) -> bool:
        """True iff the project has at least one association."""
        return self.association_total > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_id": self.status_id,
            "project_id": self.project_id,
            "lifecycle_status": self.lifecycle_status.value,
            "posture": self.posture.value,
            "association_total": self.association_total,
            "association_counts": {kind: count for kind, count in self.association_counts},
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _counts_by_kind(
    associations: Iterable[ProjectAssociation],
) -> tuple[tuple[str, int], ...]:
    """Deterministic per-kind association counts (every kind present, stable order)."""
    tally: dict[AssociationKind, int] = {kind: 0 for kind in all_association_kinds()}
    for association in associations:
        if not isinstance(association, ProjectAssociation):
            raise ProjectStatusError("status derivation requires ProjectAssociation records")
        tally[association.kind] += 1
    return tuple((kind.value, tally[kind]) for kind in all_association_kinds())


def _posture(status: ProjectStatus, total: int) -> ProjectPosture:
    if status is ProjectStatus.ARCHIVED:
        return ProjectPosture.ARCHIVED
    if status is ProjectStatus.COMPLETED:
        return ProjectPosture.COMPLETED
    if status is ProjectStatus.SUSPENDED:
        return ProjectPosture.SUSPENDED
    return ProjectPosture.POPULATED if total > 0 else ProjectPosture.EMPTY


def derive_status(
    project: Project, associations: Iterable[ProjectAssociation]
) -> DerivedProjectStatus:
    """Derive a deterministic :class:`DerivedProjectStatus` (pure; fail-closed)."""
    if not isinstance(project, Project):
        raise ProjectStatusError("status derivation requires a Project")
    counts = _counts_by_kind(associations)
    total = sum(count for _, count in counts)
    return DerivedProjectStatus.create(
        project_id=project.project_id,
        lifecycle_status=project.status,
        posture=_posture(project.status, total),
        association_counts=counts,
    )


__all__ = [
    "ProjectPosture",
    "DerivedProjectStatus",
    "derive_status",
]
