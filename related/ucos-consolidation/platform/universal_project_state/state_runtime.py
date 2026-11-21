"""UCOS-CTRL-STATE-000001 — Project State Engine (Wave 11).

The runtime of the wave: the engine that turns a composed Universal Control Plane into
project state, holds that state in the canonical
:class:`~platform.universal_project_state.state_registry.ProjectStateRegistry`, and hands it
to the constitutional services the repository already runs — the durable journal for replay,
the governance engine for adjudication, the certification engine for certification, and the
lifecycle state machine for transitions.

It is a **consumer**, not an authority. Every one of those four is invoked, none is
re-implemented, and this engine derives no plan content of its own: what a goal is, which
milestones exist and how a backlog is ordered remain the business of the plane's own
engines. This module's whole contribution is that the answer becomes a fixed, addressable,
persistable state rather than a set of in-memory objects that vanish with the process.

Discovery is by introspection, twice over, so nothing is enumerated in code. The engines to
harvest are the plane's own declared fields; the entities to harvest are whatever the
control-plane ontology declares as immutable value objects, recognised in the plane's public
projections by the ``kind`` key each one already emits. A new engine on the plane or a new
object in the ontology therefore enters project state with no change here.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from platform.universal_control_plane.durable import DurableJournal
from platform.universal_control_plane.manifest import ControlPlaneManifest, default_manifest
from platform.universal_control_plane.ontology import CertificationState, GovernanceRecord
from platform.universal_control_plane.state import StateEngine
from platform.universal_project_state.state import (
    KIND_KEY,
    ProjectStateError,
    ProjectStateSnapshot,
    StateDelta,
    StateEntity,
    discover_entity_kinds,
)
from platform.universal_project_state.state_certification import snapshot_certification_subjects
from platform.universal_project_state.state_governance import snapshot_subjects
from platform.universal_project_state.state_registry import ProjectStateRegistry
from platform.universal_project_state.state_replay import record_snapshot, replays
from typing import Any

#: The maximum projection depth walked when harvesting entities from a plane projection.
#: A control-plane ``to_dict`` nests a plan three levels deep; the bound exists so a
#: self-referential projection cannot make harvesting non-terminating.
MAX_PROJECTION_DEPTH = 12


def _harvest(node: Any, kinds: frozenset[str], depth: int = 0) -> list[Mapping[str, Any]]:
    """Every object projection in *node* whose ``kind`` names a declared entity kind."""
    if depth > MAX_PROJECTION_DEPTH:
        return []
    found: list[Mapping[str, Any]] = []
    if isinstance(node, Mapping):
        if str(node.get(KIND_KEY, "")) in kinds:
            found.append(node)
        for value in node.values():
            found.extend(_harvest(value, kinds, depth + 1))
    elif isinstance(node, Sequence) and not isinstance(node, str | bytes):
        for item in node:
            found.extend(_harvest(item, kinds, depth + 1))
    return found


def plane_projections(plane: Any) -> tuple[Mapping[str, Any], ...]:
    """The public projection of every engine the plane declares as a field.

    The plane's fields are read through :mod:`dataclasses` rather than named, so an engine
    added to the composition root is harvested without a change here. A field that publishes
    no ``to_dict`` is skipped rather than guessed at.
    """
    if not dataclasses.is_dataclass(plane):
        raise ProjectStateError("project state requires a composed control plane")
    projections: list[Mapping[str, Any]] = []
    for spec in dataclasses.fields(plane):
        value = getattr(plane, spec.name, None)
        projector = getattr(value, "to_dict", None)
        if value is None or not callable(projector):
            continue
        projected = projector()
        if isinstance(projected, Mapping):
            projections.append(projected)
    return tuple(projections)


@dataclass
class ProjectStateEngine:
    """Projects, holds, persists, governs and certifies project state."""

    manifest: ControlPlaneManifest = field(default_factory=default_manifest)
    registry: ProjectStateRegistry = field(default_factory=ProjectStateRegistry)
    lifecycle: StateEngine = field(default_factory=StateEngine)
    journal: DurableJournal | None = None
    _snapshots: list[ProjectStateSnapshot] = field(default_factory=list)
    _lifecycles: dict[str, str] = field(default_factory=dict)

    # -- discovery -------------------------------------------------------

    def entity_kinds(self) -> tuple[str, ...]:
        """Every entity kind project state can hold, discovered from the ontology."""
        return discover_entity_kinds()

    def project(self, plane: Any, *, tick: int = 0) -> ProjectStateSnapshot:
        """Project *plane* into a snapshot, register every entity, and record it.

        Entities are de-duplicated by subject identifier: the same object reached through
        two engine projections is one state entity, not two, and the first projection
        encountered wins so the result does not depend on field order beyond declaration.
        """
        kinds = frozenset(self.entity_kinds())
        seen: dict[str, StateEntity] = {}
        for projection in plane_projections(plane):
            for raw in _harvest(projection, kinds):
                entity = StateEntity.from_projection(raw, tick=tick)
                seen.setdefault(entity.subject_id, entity)
        snapshot = ProjectStateSnapshot(
            universe_id=self.manifest.universe_id,
            truth_id=self._truth_id(plane),
            entities=tuple(seen[key] for key in sorted(seen)),
            tick=tick,
        )
        self.registry.register_snapshot(snapshot)
        for entity in snapshot.entities:
            if entity.lifecycle:
                self._lifecycles[entity.subject_id] = entity.lifecycle
        self._snapshots.append(snapshot)
        if self.journal is not None:
            record_snapshot(self.journal, snapshot, tick=tick)
        return snapshot

    @staticmethod
    def _truth_id(plane: Any) -> str:
        """The identity of the Repository Truth the plane was composed over, when it has one."""
        truth_engine = getattr(plane, "truth", None)
        resolver = getattr(truth_engine, "truth", None)
        if not callable(resolver):
            return ""
        try:
            return str(resolver().truth_id)
        except Exception as exc:  # noqa: BLE001 — an unreadable substrate is one failure mode
            raise ProjectStateError(f"repository truth is unreadable: {exc}") from exc

    # -- state -----------------------------------------------------------

    def snapshot(self) -> ProjectStateSnapshot:
        """The most recent snapshot; fail-closed before anything has been projected."""
        if not self._snapshots:
            raise ProjectStateError("no project state has been projected yet")
        return self._snapshots[-1]

    def snapshots(self) -> tuple[ProjectStateSnapshot, ...]:
        return tuple(self._snapshots)

    def delta(self) -> StateDelta:
        """The delta between the two most recent snapshots; empty when fewer than two exist."""
        if len(self._snapshots) < 2:
            return StateDelta()
        return StateDelta.between(self._snapshots[-2], self._snapshots[-1])

    def lifecycle_of(self, subject_id: str) -> str:
        """The lifecycle state held for *subject_id*, or the entity's own declared state."""
        if subject_id in self._lifecycles:
            return self._lifecycles[subject_id]
        return self.registry.entity(subject_id).lifecycle

    def transition(self, subject_id: str, event: str) -> str:
        """Advance *subject_id* through the plane's existing lifecycle state machine."""
        current = self.lifecycle_of(subject_id)
        if not current:
            raise ProjectStateError(f"{subject_id!r} declares no lifecycle state to advance")
        nxt = self.lifecycle.transition(current, event)
        self._lifecycles[subject_id] = nxt
        return nxt

    # -- replay ----------------------------------------------------------

    def replayable(self) -> bool:
        """Whether the journal replays the current snapshot exactly."""
        if self.journal is None or not self._snapshots:
            return False
        return replays(self.journal, self.snapshot())

    # -- governance and certification, through the existing services -----

    def govern(self, engine: Any, *, tick: int = 0) -> tuple[GovernanceRecord, ...]:
        """Adjudicate the current snapshot through the declared governance engine."""
        subjects = snapshot_subjects(self.snapshot(), registry=self.registry)
        return tuple(engine.resolve(subject, tick=tick) for subject in subjects)

    def certify(
        self, engine: Any, records: Iterable[GovernanceRecord], *, tick: int = 0
    ) -> tuple[CertificationState, ...]:
        """Certify governed state records through the declared certification engine."""
        subjects = snapshot_certification_subjects(self.snapshot(), records)
        return tuple(
            engine.assess(subject, tick=tick) for subject in subjects if engine.eligible(subject)
        )

    # -- projection ------------------------------------------------------

    def counts(self) -> dict[str, int]:
        return {
            "snapshots": len(self._snapshots),
            "entity_kinds": len(self.entity_kinds()),
            "entities": self.registry.count(),
            "populated_kinds": len(self.registry.kinds()),
            "lifecycles": len(self._lifecycles),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "ProjectStateEngine",
            "universe_id": self.manifest.universe_id,
            "counts": self.counts(),
            "registry": self.registry.to_dict(),
            "replayable": self.replayable(),
            "snapshot": self._snapshots[-1].to_dict() if self._snapshots else None,
        }


__all__ = ["MAX_PROJECTION_DEPTH", "ProjectStateEngine", "plane_projections"]
