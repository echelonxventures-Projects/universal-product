"""EC2-TASK-000092 — Project Associations (EC2-EPIC-005).

The deterministic, append-only **association-by-reference** registry (Program §2.1 #4
"associate blueprints, requests, artifacts"; §5 "associations … intact"). A project is
bound to a typed external work reference (blueprint / request / artifact) through an
immutable :class:`~platform.projects.contracts.ProjectAssociation` record. The registry
models associations **by reference only**: each ``ref_id`` is opaque, and the runtime
resolves/validates no referenced entity — the referenced runtimes (EPIC-006/007/009)
do not yet exist, so "associations intact" means the **referential integrity of the
association records themselves** (§5.3):

    * no duplicate ``{project_id, kind, ref_id}`` binding (fail-closed);
    * no cross-project leakage — an ``association_id`` is content-addressed from its
      project, so the same reference under a different project is a distinct record and
      is never surfaced across projects;
    * deterministic removal (an append-only removal event) — associations of an
      archived project become immutable (the service refuses add/remove on a terminal
      project).

Every change is recorded as an ordered, append-only :class:`AssociationEvent` (no
wall-clock; a caller-supplied logical ``tick``) so association history is reproducible
and auditable (OP-C3). Like the workspace membership registry, this store holds
*records only* — valid-project enforcement is composed by the service, and orphan
detection is a health probe.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.projects.contracts import AssociationKind, ProjectAssociation
from platform.projects.errors import ProjectAssociationError
from typing import Any


@dataclass(frozen=True, slots=True)
class AssociationEvent:
    """An immutable, ordered record of an association change (append-only)."""

    sequence: int
    project_id: str
    association_id: str
    kind: AssociationKind
    ref_id: str
    action: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "project_id": self.project_id,
            "association_id": self.association_id,
            "kind": self.kind.value,
            "ref_id": self.ref_id,
            "action": self.action,
            "tick": self.tick,
        }


class AssociationRegistry:
    """A deterministic, append-only registry of project associations (by reference)."""

    __slots__ = ("_by_project", "_log")

    def __init__(self) -> None:
        # project_id -> {association_id -> ProjectAssociation}
        self._by_project: dict[str, dict[str, ProjectAssociation]] = {}
        self._log: list[AssociationEvent] = []

    def add(
        self, project_id: str, kind: AssociationKind, ref_id: str, *, tick: int
    ) -> ProjectAssociation:
        """Bind a typed reference to a project (fail-closed on duplicate binding)."""
        association = ProjectAssociation.create(project_id, kind, ref_id)
        associations = self._by_project.setdefault(project_id, {})
        if association.association_id in associations:
            raise ProjectAssociationError(
                "association already exists",
                project_id=project_id,
                kind=kind.value,
                ref_id=ref_id,
            )
        associations[association.association_id] = association
        self._record(association, "added", tick)
        return association

    def remove(
        self, project_id: str, kind: AssociationKind, ref_id: str, *, tick: int
    ) -> ProjectAssociation:
        """Unbind a typed reference from a project (fail-closed on absent binding)."""
        probe = ProjectAssociation.create(project_id, kind, ref_id)
        associations = self._by_project.get(project_id, {})
        association = associations.get(probe.association_id)
        if association is None:
            raise ProjectAssociationError(
                "no such association",
                project_id=project_id,
                kind=kind.value,
                ref_id=ref_id,
            )
        del associations[association.association_id]
        self._record(association, "removed", tick)
        return association

    def has(self, project_id: str, kind: AssociationKind, ref_id: str) -> bool:
        """True iff ``{project_id, kind, ref_id}`` is currently bound."""
        probe = ProjectAssociation.create(project_id, kind, ref_id)
        return probe.association_id in self._by_project.get(project_id, {})

    def associations_of(self, project_id: str) -> tuple[ProjectAssociation, ...]:
        """Every current association of a project, in stable (association-id) order."""
        associations = self._by_project.get(project_id, {})
        return tuple(associations[aid] for aid in sorted(associations))

    def associations_of_kind(
        self, project_id: str, kind: AssociationKind
    ) -> tuple[ProjectAssociation, ...]:
        """Every current association of a project of a given kind (stable order)."""
        return tuple(a for a in self.associations_of(project_id) if a.kind is kind)

    def count_of(self, project_id: str) -> int:
        """The number of current associations bound to a project."""
        return len(self._by_project.get(project_id, {}))

    @property
    def project_ids(self) -> tuple[str, ...]:
        """Every project id that currently has at least one association (stable order)."""
        return tuple(pid for pid in sorted(self._by_project) if self._by_project[pid])

    @property
    def events(self) -> tuple[AssociationEvent, ...]:
        """An immutable snapshot of the append-only association event log (in order)."""
        return tuple(self._log)

    def __len__(self) -> int:
        """The total number of current associations across all projects."""
        return sum(len(a) for a in self._by_project.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "association_count": len(self),
            "associations": [
                self._by_project[pid][aid].to_dict()
                for pid in sorted(self._by_project)
                for aid in sorted(self._by_project[pid])
            ],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def _record(self, association: ProjectAssociation, action: str, tick: int) -> None:
        self._log.append(
            AssociationEvent(
                sequence=len(self._log),
                project_id=association.project_id,
                association_id=association.association_id,
                kind=association.kind,
                ref_id=association.ref_id,
                action=action,
                tick=tick,
            )
        )


__all__ = ["AssociationEvent", "AssociationRegistry"]
