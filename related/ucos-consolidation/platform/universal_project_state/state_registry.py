"""UCOS-CTRL-STATE-000001 — Project State Registry (Wave 11).

The in-memory index of project state: every discovered
:class:`~platform.universal_project_state.state.StateEntity` held once, under its
kind-qualified subject identifier, with the ownership and dependency indices the wave's
analysis requirements need.

This is a registry in the same sense as :mod:`platform.universal_control_plane.registry` —
a container with queries, not an engine with policy. It adjudicates nothing, decides nothing
and derives no new attribute: dependency edges are read from the ``depends_on`` attribute the
ontology already publishes, and ownership is read from the owner the entity already carries.
Registration is idempotent by identity, so re-registering an unchanged entity is a no-op and
re-registering a changed one is a recorded replacement rather than a silent duplicate.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from platform.universal_project_state.state import (
    ProjectStateError,
    ProjectStateSnapshot,
    StateEntity,
)
from typing import Any

#: Attribute keys consulted for an entity's declared dependencies. ``dependencies`` is the
#: field the control-plane ontology publishes for this; no second spelling is invented here.
DEPENDENCY_KEYS: tuple[str, ...] = ("dependencies",)


def _edges_from(entity: StateEntity) -> tuple[str, ...]:
    """The dependency targets *entity* declares, in declared order, de-duplicated."""
    seen: list[str] = []
    for key in DEPENDENCY_KEYS:
        raw = entity.attributes.get(key)
        if isinstance(raw, Sequence) and not isinstance(raw, str | bytes):
            for item in raw:
                target = str(item).strip()
                if target and target not in seen:
                    seen.append(target)
    return tuple(seen)


@dataclass
class ProjectStateRegistry:
    """Holds every state entity once, indexed by subject, kind, owner and dependency."""

    _entities: dict[str, StateEntity] = field(default_factory=dict)
    _replaced: dict[str, int] = field(default_factory=dict)

    # -- registration ----------------------------------------------------

    def register(self, entity: StateEntity) -> StateEntity:
        """Register *entity*, replacing a prior registration only when its content changed."""
        if not entity.entity_id.strip():
            raise ProjectStateError("a state entity requires a non-empty entity_id")
        existing = self._entities.get(entity.subject_id)
        if existing is not None and existing.identity != entity.identity:
            self._replaced[entity.subject_id] = self._replaced.get(entity.subject_id, 0) + 1
        self._entities[entity.subject_id] = entity
        return entity

    def register_all(self, entities: Iterable[StateEntity]) -> tuple[StateEntity, ...]:
        """Register every entity in *entities*, in the order given."""
        return tuple(self.register(entity) for entity in entities)

    def register_snapshot(self, snapshot: ProjectStateSnapshot) -> int:
        """Register every entity a snapshot carries; returns how many were registered."""
        return len(self.register_all(snapshot.entities))

    # -- queries ---------------------------------------------------------

    def entity(self, subject_id: str) -> StateEntity:
        try:
            return self._entities[subject_id]
        except KeyError as exc:
            raise ProjectStateError(f"no such state entity: {subject_id!r}") from exc

    def entities(self) -> tuple[StateEntity, ...]:
        return tuple(self._entities[key] for key in sorted(self._entities))

    def subjects(self) -> tuple[str, ...]:
        return tuple(sorted(self._entities))

    def kinds(self) -> tuple[str, ...]:
        return tuple(sorted({e.kind for e in self._entities.values()}))

    def of_kind(self, kind: str) -> tuple[StateEntity, ...]:
        return tuple(e for e in self.entities() if e.kind == kind)

    def owners(self) -> tuple[str, ...]:
        return tuple(sorted({e.owner for e in self._entities.values() if e.owner}))

    def owned_by(self, owner: str) -> tuple[StateEntity, ...]:
        return tuple(e for e in self.entities() if e.owner == owner)

    def unowned(self) -> tuple[StateEntity, ...]:
        """Every registered entity carrying no owner — the ownership gap, measured."""
        return tuple(e for e in self.entities() if not e.owner)

    def replacements(self) -> Mapping[str, int]:
        """How many times each subject was re-registered with different content."""
        return dict(sorted(self._replaced.items()))

    def count(self) -> int:
        return len(self._entities)

    # -- dependency analysis ---------------------------------------------

    def dependencies_of(self, subject_id: str) -> tuple[str, ...]:
        """The dependency targets the entity declares (as declared, not as resolved)."""
        return _edges_from(self.entity(subject_id))

    def dependents_of(self, entity_id: str) -> tuple[str, ...]:
        """Every registered subject declaring a dependency on *entity_id*."""
        return tuple(
            entity.subject_id for entity in self.entities() if entity_id in _edges_from(entity)
        )

    def edges(self) -> tuple[tuple[str, str], ...]:
        """Every declared dependency edge as ``(subject_id, target_entity_id)``."""
        return tuple(
            (entity.subject_id, target)
            for entity in self.entities()
            for target in _edges_from(entity)
        )

    def unresolved_dependencies(self) -> tuple[tuple[str, str], ...]:
        """Every declared edge whose target is not itself registered — a measured gap."""
        known = {entity.entity_id for entity in self._entities.values()}
        return tuple((subject, target) for subject, target in self.edges() if target not in known)

    def coverage(self) -> float:
        """The fraction of registered entities carrying an owner, to four places."""
        if not self._entities:
            return 0.0
        return round(1 - (len(self.unowned()) / len(self._entities)), 4)

    # -- projection ------------------------------------------------------

    def counts(self) -> dict[str, int]:
        return {
            "entities": self.count(),
            "kinds": len(self.kinds()),
            "owners": len(self.owners()),
            "unowned": len(self.unowned()),
            "edges": len(self.edges()),
            "unresolved_dependencies": len(self.unresolved_dependencies()),
            "replacements": len(self._replaced),
        }

    def by_kind(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entity in self._entities.values():
            counts[entity.kind] = counts.get(entity.kind, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "ProjectStateRegistry",
            "counts": self.counts(),
            "by_kind": self.by_kind(),
            "ownership_coverage": self.coverage(),
            "kinds": list(self.kinds()),
        }


__all__ = ["DEPENDENCY_KEYS", "ProjectStateRegistry"]
