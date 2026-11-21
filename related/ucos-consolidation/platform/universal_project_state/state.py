"""UCOS-CTRL-STATE-000001 — Project State (Wave 11).

The constitutional source of truth for **project state**: the immutable, content-addressed
record of what the project is, at one logical tick, across every entity the control plane
already models — plans, roadmaps, objectives, milestones, work packages, assignments,
dependencies, progress and execution.

Why this exists, and what it deliberately does not do. The Universal Control Plane already
*derives* those entities from Repository Truth: its ``PlanEngine`` owns visions, goals and
objectives, its ``RoadmapEngine`` owns milestones, its ``BacklogEngine`` owns work packages,
and so on. Re-deriving any of them here would be a second measurement over one
population, which is exactly the defect the repository has already litigated. So this module
derives **nothing about plan content**. It observes what the plane holds, fixes it as state,
and makes that state persistable, replayable, governable and certifiable — which is the one
thing the plane could not previously do, because its project state lived only in memory.

The vocabulary is not new either. A state entity kind is whatever the control-plane
*ontology* already defines as an immutable value object, discovered by introspection exactly
as :func:`~platform.universal_control_plane.registration.discover_engines` discovers engines.
Adding an object to the ontology therefore adds a state entity kind with no change here, and
nothing in this module names a single entity.

Deterministic and clock-free: identity is a content digest, ordering is explicit, and the
logical ``tick`` is supplied by the caller. Stdlib only.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from platform.universal_control_plane import ontology as control_plane_ontology
from platform.universal_control_plane.ontology import payload_digest
from types import ModuleType
from typing import Any

#: The key every control-plane projection carries naming the object's own type. It is the
#: join between the plane's public projection and this module's entity vocabulary.
KIND_KEY = "kind"

#: The key every control-plane value object carries naming its content identity.
IDENTITY_KEY = "identity"

#: The suffix borne by the field that names an object's own identifier.
ID_SUFFIX = "_id"

#: Keys consulted, in order, for an entity's lifecycle state and its owner. Every key names a
#: field the control-plane ontology actually publishes — a key for a field no object declares
#: would be configuration that can never fire, so none is listed speculatively.
LIFECYCLE_KEYS: tuple[str, ...] = ("state", "status", "lifecycle_state")
OWNER_KEYS: tuple[str, ...] = ("owner", "owner_id", "agent_id")


class ProjectStateError(Exception):
    """Raised when project state cannot be projected, persisted or reconstructed."""


# ---------------------------------------------------------------------------
# entity-kind discovery — the vocabulary is the existing ontology
# ---------------------------------------------------------------------------


def discover_entity_kinds(module: ModuleType | None = None) -> tuple[str, ...]:
    """Every entity kind the control-plane ontology defines, in sorted order.

    A kind is an immutable (frozen) dataclass declared *in* the ontology module. The
    frozen test is what separates a value object — the thing project state is made of —
    from an engine, which is mutable by construction. Re-exports are excluded by the
    ``__module__`` check so a name cannot be discovered twice under two paths.
    """
    target = module or control_plane_ontology
    kinds: list[str] = []
    for name in dir(target):
        if name.startswith("_"):
            continue
        obj = getattr(target, name)
        if not isinstance(obj, type) or not dataclasses.is_dataclass(obj):
            continue
        if obj.__module__ != target.__name__:
            continue
        params = getattr(obj, "__dataclass_params__", None)
        if params is None or not params.frozen:
            continue
        kinds.append(name)
    return tuple(sorted(kinds))


def entity_id_of(raw: Mapping[str, Any]) -> str:
    """The identifier an ontology projection declares for itself.

    Every ontology ``to_dict`` emits its own identifier as the first ``*_id`` key, ahead of
    any foreign key it also carries. Reading it positionally rather than by a per-kind name
    is what keeps this function total over a vocabulary it does not enumerate; a sorted scan
    would instead pick ``capability_id`` out of an ownership record and silently mis-key it.
    """
    for key, value in raw.items():
        if key.endswith(ID_SUFFIX) and str(value).strip():
            return str(value)
    identity = str(raw.get(IDENTITY_KEY, "")).strip()
    if identity:
        return identity
    raise ProjectStateError(f"projection declares no identifier: {sorted(raw)!r}")


def _first_present(raw: Mapping[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


# ---------------------------------------------------------------------------
# the state model
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StateEntity:
    """One project-state entity: a kind, an identity, a lifecycle and its attributes."""

    kind: str
    entity_id: str
    lifecycle: str = ""
    owner: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @classmethod
    def from_projection(cls, raw: Mapping[str, Any], *, tick: int = 0) -> StateEntity:
        """Project one control-plane object projection into a state entity."""
        kind = str(raw.get(KIND_KEY, "")).strip()
        if not kind:
            raise ProjectStateError(f"projection declares no {KIND_KEY!r}: {sorted(raw)!r}")
        return cls(
            kind=kind,
            entity_id=entity_id_of(raw),
            lifecycle=_first_present(raw, LIFECYCLE_KEYS),
            owner=_first_present(raw, OWNER_KEYS),
            attributes=dict(raw),
            tick=tick,
        )

    @property
    def subject_id(self) -> str:
        """The stable, kind-qualified subject identifier used by every downstream engine."""
        return f"{self.kind}::{self.entity_id}"

    @property
    def identity(self) -> str:
        """The content-addressed identity of this entity."""
        return payload_digest(self.core())

    def core(self) -> dict[str, Any]:
        """The hashable core: content only, no wall-clock."""
        return {
            "kind": self.kind,
            "entity_id": self.entity_id,
            "lifecycle": self.lifecycle,
            "owner": self.owner,
            "attributes": dict(sorted(self.attributes.items())),
        }

    def fact(self, name: str) -> Any:
        """Resolve *name* against the entity's own attributes (the open fact bag)."""
        return self.attributes.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "StateEntity",
            "identity": self.identity,
            "entity_kind": self.kind,
            "entity_id": self.entity_id,
            "subject_id": self.subject_id,
            "lifecycle": self.lifecycle,
            "owner": self.owner,
            "attributes": dict(sorted(self.attributes.items())),
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ProjectStateSnapshot:
    """An immutable, content-addressed projection of project state at one tick."""

    universe_id: str
    truth_id: str
    entities: tuple[StateEntity, ...] = ()
    tick: int = 0

    @property
    def snapshot_id(self) -> str:
        """The content-addressed identity of this snapshot."""
        return payload_digest(self.core())

    @property
    def identity(self) -> str:
        return self.snapshot_id

    def core(self) -> dict[str, Any]:
        """The hashable core: the universe, the Truth it was taken over, and its entities."""
        return {
            "universe_id": self.universe_id,
            "truth_id": self.truth_id,
            "entities": [e.identity for e in self.entities],
        }

    def kinds(self) -> tuple[str, ...]:
        return tuple(sorted({e.kind for e in self.entities}))

    def of_kind(self, kind: str) -> tuple[StateEntity, ...]:
        return tuple(e for e in self.entities if e.kind == kind)

    def entity(self, subject_id: str) -> StateEntity:
        for entity in self.entities:
            if entity.subject_id == subject_id:
                return entity
        raise ProjectStateError(f"no such state entity: {subject_id!r}")

    def counts(self) -> dict[str, int]:
        by_kind: dict[str, int] = {}
        for entity in self.entities:
            by_kind[entity.kind] = by_kind.get(entity.kind, 0) + 1
        return dict(sorted(by_kind.items()))

    def owned(self) -> tuple[StateEntity, ...]:
        """Every entity carrying an owner — the population ownership analysis can adjudicate."""
        return tuple(e for e in self.entities if e.owner)

    def coverage(self) -> float:
        """The fraction of entities carrying an owner, rounded to four places."""
        if not self.entities:
            return 0.0
        return round(len(self.owned()) / len(self.entities), 4)

    def digest(self) -> str:
        return payload_digest([e.identity for e in self.entities])

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ProjectStateSnapshot",
            "identity": self.snapshot_id,
            "snapshot_id": self.snapshot_id,
            "universe_id": self.universe_id,
            "truth_id": self.truth_id,
            "tick": self.tick,
            "total": len(self.entities),
            "kinds": list(self.kinds()),
            "counts": self.counts(),
            "ownership_coverage": self.coverage(),
            "digest": self.digest(),
        }


@dataclass(frozen=True, slots=True)
class StateDelta:
    """The measured difference between two snapshots, by subject identifier."""

    added: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    changed: tuple[str, ...] = ()

    @classmethod
    def between(cls, before: ProjectStateSnapshot, after: ProjectStateSnapshot) -> StateDelta:
        """The delta from *before* to *after*, keyed on subject identity."""
        prior = {e.subject_id: e.identity for e in before.entities}
        current = {e.subject_id: e.identity for e in after.entities}
        return cls(
            added=tuple(sorted(set(current) - set(prior))),
            removed=tuple(sorted(set(prior) - set(current))),
            changed=tuple(sorted(k for k in set(prior) & set(current) if prior[k] != current[k])),
        )

    @property
    def empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def counts(self) -> dict[str, int]:
        return {
            "added": len(self.added),
            "removed": len(self.removed),
            "changed": len(self.changed),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "StateDelta",
            "identity": payload_digest(self.counts()),
            "counts": self.counts(),
            "added": list(self.added),
            "removed": list(self.removed),
            "changed": list(self.changed),
            "empty": self.empty,
        }


__all__ = [
    "IDENTITY_KEY",
    "ID_SUFFIX",
    "KIND_KEY",
    "LIFECYCLE_KEYS",
    "OWNER_KEYS",
    "ProjectStateError",
    "ProjectStateSnapshot",
    "StateDelta",
    "StateEntity",
    "discover_entity_kinds",
    "entity_id_of",
]
