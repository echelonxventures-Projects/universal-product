"""EC2-TASK-000102 — Blueprint Associations (EC2-EPIC-006).

The deterministic, append-only **association-by-reference** registry for blueprints,
reusing the certified EPIC-005 :mod:`platform.projects.associations` pattern exactly.
A blueprint is bound to a typed external reference through an immutable
:class:`BlueprintAssociation` record. The registry models associations **by reference
only**: each ``ref_id`` is opaque, and the runtime resolves/validates no referenced
entity — "associations intact" means the **referential integrity of the association
records themselves**:

    * no duplicate ``{blueprint_id, kind, ref_id}`` binding (fail-closed);
    * no cross-blueprint leakage — an ``association_id`` is content-addressed from its
      blueprint, so the same reference under a different blueprint is a distinct record;
    * deterministic removal (an append-only removal event).

The supported association kinds realize the full EPIC-006 association surface: a
blueprint may be bound to a workspace, a project (the EPIC-005 seam, by reference), a
generation request (EPIC-007), an implementation artifact, a produced artifact,
another blueprint, and — crucially for link-4 — its originating **generation
artifact**. EPIC-006 does **not** write to the EPIC-005 project association registry;
it owns the blueprint side of the reference (Determination §6.3).

Every change is recorded as an ordered, append-only :class:`BlueprintAssociationEvent`
(no wall-clock; a caller-supplied logical ``tick``) so association history is
reproducible and auditable (OP-C3).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.blueprints.errors import BlueprintAssociationError
from platform.foundation.contracts import content_hash
from typing import Any


class BlueprintAssociationKind(str, Enum):
    """The typed external references a blueprint may bind **by reference**.

    ``WORKSPACE`` / ``PROJECT`` (EPIC-004/005), ``REQUEST`` (EPIC-007),
    ``IMPLEMENTATION`` / ``ARTIFACT`` (downstream), ``BLUEPRINT`` (blueprint↔blueprint
    lineage/composition), and ``GENERATION_ARTIFACT`` (the ``05-GENERATION`` origin,
    the link-4 backward edge). Each ``ref_id`` is opaque; nothing is resolved.
    """

    WORKSPACE = "workspace"
    PROJECT = "project"
    REQUEST = "request"
    IMPLEMENTATION = "implementation"
    ARTIFACT = "artifact"
    BLUEPRINT = "blueprint"
    GENERATION_ARTIFACT = "generation-artifact"


def all_association_kinds() -> tuple[BlueprintAssociationKind, ...]:
    """Return every blueprint association kind in stable declaration order."""
    return tuple(BlueprintAssociationKind)


@dataclass(frozen=True, slots=True)
class BlueprintAssociation:
    """An immutable, content-addressed binding of a blueprint to a typed reference.

    The ``association_id`` is content-addressed from ``{blueprint_id, kind, ref_id}``
    so an identical binding always yields the same id (idempotency key) and the same
    reference can never be rebound across blueprints to the same id.
    """

    association_id: str
    blueprint_id: str
    kind: BlueprintAssociationKind
    ref_id: str

    @classmethod
    def create(
        cls, blueprint_id: str, kind: BlueprintAssociationKind, ref_id: str
    ) -> BlueprintAssociation:
        """Build an association with a deterministic, content-addressed id."""
        if not isinstance(blueprint_id, str) or not blueprint_id:
            raise BlueprintAssociationError("association requires a blueprint_id")
        if not isinstance(kind, BlueprintAssociationKind):
            raise BlueprintAssociationError("association kind must be a BlueprintAssociationKind")
        if not isinstance(ref_id, str) or not ref_id:
            raise BlueprintAssociationError(
                "association requires a ref_id", blueprint_id=blueprint_id
            )
        key = {"blueprint_id": blueprint_id, "kind": kind.value, "ref_id": ref_id}
        return cls(
            association_id=f"UCOS-BASC-{content_hash(key)[:16]}",
            blueprint_id=blueprint_id,
            kind=kind,
            ref_id=ref_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "association_id": self.association_id,
            "blueprint_id": self.blueprint_id,
            "kind": self.kind.value,
            "ref_id": self.ref_id,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class BlueprintAssociationEvent:
    """An immutable, ordered record of an association change (append-only)."""

    sequence: int
    blueprint_id: str
    association_id: str
    kind: BlueprintAssociationKind
    ref_id: str
    action: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "blueprint_id": self.blueprint_id,
            "association_id": self.association_id,
            "kind": self.kind.value,
            "ref_id": self.ref_id,
            "action": self.action,
            "tick": self.tick,
        }


class BlueprintAssociationRegistry:
    """A deterministic, append-only registry of blueprint associations (by reference)."""

    __slots__ = ("_by_blueprint", "_log")

    def __init__(self) -> None:
        self._by_blueprint: dict[str, dict[str, BlueprintAssociation]] = {}
        self._log: list[BlueprintAssociationEvent] = []

    def add(
        self, blueprint_id: str, kind: BlueprintAssociationKind, ref_id: str, *, tick: int
    ) -> BlueprintAssociation:
        """Bind a typed reference to a blueprint (fail-closed on duplicate binding)."""
        association = BlueprintAssociation.create(blueprint_id, kind, ref_id)
        associations = self._by_blueprint.setdefault(blueprint_id, {})
        if association.association_id in associations:
            raise BlueprintAssociationError(
                "association already exists",
                blueprint_id=blueprint_id,
                kind=kind.value,
                ref_id=ref_id,
            )
        associations[association.association_id] = association
        self._record(association, "added", tick)
        return association

    def remove(
        self, blueprint_id: str, kind: BlueprintAssociationKind, ref_id: str, *, tick: int
    ) -> BlueprintAssociation:
        """Unbind a typed reference from a blueprint (fail-closed on absent binding)."""
        probe = BlueprintAssociation.create(blueprint_id, kind, ref_id)
        associations = self._by_blueprint.get(blueprint_id, {})
        association = associations.get(probe.association_id)
        if association is None:
            raise BlueprintAssociationError(
                "no such association",
                blueprint_id=blueprint_id,
                kind=kind.value,
                ref_id=ref_id,
            )
        del associations[association.association_id]
        self._record(association, "removed", tick)
        return association

    def has(self, blueprint_id: str, kind: BlueprintAssociationKind, ref_id: str) -> bool:
        """True iff ``{blueprint_id, kind, ref_id}`` is currently bound."""
        probe = BlueprintAssociation.create(blueprint_id, kind, ref_id)
        return probe.association_id in self._by_blueprint.get(blueprint_id, {})

    def associations_of(self, blueprint_id: str) -> tuple[BlueprintAssociation, ...]:
        """Every current association of a blueprint, in stable (association-id) order."""
        associations = self._by_blueprint.get(blueprint_id, {})
        return tuple(associations[aid] for aid in sorted(associations))

    def associations_of_kind(
        self, blueprint_id: str, kind: BlueprintAssociationKind
    ) -> tuple[BlueprintAssociation, ...]:
        """Every current association of a blueprint of a given kind (stable order)."""
        return tuple(a for a in self.associations_of(blueprint_id) if a.kind is kind)

    def count_of(self, blueprint_id: str) -> int:
        """The number of current associations bound to a blueprint."""
        return len(self._by_blueprint.get(blueprint_id, {}))

    @property
    def blueprint_ids(self) -> tuple[str, ...]:
        """Every blueprint id that currently has at least one association (stable order)."""
        return tuple(bid for bid in sorted(self._by_blueprint) if self._by_blueprint[bid])

    @property
    def events(self) -> tuple[BlueprintAssociationEvent, ...]:
        """An immutable snapshot of the append-only association event log (in order)."""
        return tuple(self._log)

    def __len__(self) -> int:
        """The total number of current associations across all blueprints."""
        return sum(len(a) for a in self._by_blueprint.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "association_count": len(self),
            "associations": [
                self._by_blueprint[bid][aid].to_dict()
                for bid in sorted(self._by_blueprint)
                for aid in sorted(self._by_blueprint[bid])
            ],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def _record(self, association: BlueprintAssociation, action: str, tick: int) -> None:
        self._log.append(
            BlueprintAssociationEvent(
                sequence=len(self._log),
                blueprint_id=association.blueprint_id,
                association_id=association.association_id,
                kind=association.kind,
                ref_id=association.ref_id,
                action=action,
                tick=tick,
            )
        )


__all__ = [
    "BlueprintAssociationKind",
    "all_association_kinds",
    "BlueprintAssociation",
    "BlueprintAssociationEvent",
    "BlueprintAssociationRegistry",
]
