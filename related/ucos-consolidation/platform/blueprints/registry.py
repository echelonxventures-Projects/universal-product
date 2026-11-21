"""EC2-TASK-000102 — Blueprint Registry (EC2-EPIC-006).

The deterministic, append-only store of blueprints — the runtime home of blueprint
**creation**, **registration**, **discovery**, **resolution**, and immutable
**versioning** (Program §2.1 #7, PC-05). A blueprint's identity is its ``slug`` within
its parent ``workspace_id`` (content-addressed ``blueprint_id``), so registration is
idempotent-safe and fail-closed on genuine duplicates. Mutable facets are applied
immutably: a lifecycle transition or metadata update replaces the stored
:class:`~platform.blueprints.contracts.Blueprint` with a new immutable record (the id
is preserved) and records an ordered, append-only
:class:`~platform.blueprints.lifecycle.BlueprintEvent`; a new version appends an
immutable :class:`~platform.blueprints.versioning.BlueprintVersion` to the blueprint's
lineage — so the registry's history is reproducible and auditable (OP-C3).

The registry holds *records only* — it enforces no authorization (that is the Identity
Layer), no isolation (the reused workspace isolation rule), no classification/validation
(the EC-1 façade), and it does not resolve the parent workspace (the service binds it);
it is the substrate the blueprint service composes. It mirrors the certified
:mod:`platform.projects.registry` topology exactly.
"""

from __future__ import annotations

from platform.blueprints.contracts import Blueprint, BlueprintFamily, BlueprintStatus
from platform.blueprints.errors import BlueprintRegistryError
from platform.blueprints.lifecycle import BlueprintEvent, validate_transition
from platform.blueprints.metadata import BlueprintMetadata
from platform.blueprints.versioning import BlueprintVersion, VersionLineage
from platform.foundation.contracts import content_hash
from typing import Any


class BlueprintRegistry:
    """A deterministic, append-only registry of blueprints (create/resolve/version)."""

    __slots__ = ("_by_id", "_lineages", "_log")

    def __init__(self) -> None:
        self._by_id: dict[str, Blueprint] = {}
        self._lineages: dict[str, VersionLineage] = {}
        self._log: list[BlueprintEvent] = []

    def register(self, blueprint: Blueprint) -> Blueprint:
        """Register a blueprint record (fail-closed on duplicate id)."""
        if not isinstance(blueprint, Blueprint):
            raise BlueprintRegistryError("register requires a Blueprint")
        if blueprint.blueprint_id in self._by_id:
            raise BlueprintRegistryError(
                "blueprint already registered",
                blueprint_id=blueprint.blueprint_id,
                slug=blueprint.slug,
            )
        self._by_id[blueprint.blueprint_id] = blueprint
        return blueprint

    def create(
        self,
        slug: str,
        name: str,
        workspace_id: str,
        owner_subject: str,
        family: BlueprintFamily,
        *,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: BlueprintMetadata | None = None,
    ) -> Blueprint:
        """Build and register a new DRAFT blueprint (fail-closed on duplicate)."""
        blueprint = Blueprint.create(
            slug,
            name,
            workspace_id,
            owner_subject,
            family,
            project_id=project_id,
            tenant=tenant,
            metadata=metadata,
        )
        return self.register(blueprint)

    def __contains__(self, blueprint_id: str) -> bool:
        return blueprint_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def get(self, blueprint_id: str) -> Blueprint:
        """Resolve a blueprint by id (fail-closed on absent)."""
        blueprint = self._by_id.get(blueprint_id)
        if blueprint is None:
            raise BlueprintRegistryError("no such blueprint", blueprint_id=blueprint_id)
        return blueprint

    def exists(self, slug: str, workspace_id: str) -> bool:
        """True iff a blueprint with ``slug`` exists in ``workspace_id``."""
        probe = Blueprint.create(slug, slug, workspace_id, "probe", BlueprintFamily.DATA)
        return probe.blueprint_id in self._by_id

    def resolve(self, slug: str, workspace_id: str) -> Blueprint:
        """Resolve a blueprint by its ``slug`` within ``workspace_id`` (fail-closed)."""
        probe = Blueprint.create(slug, slug, workspace_id, "probe", BlueprintFamily.DATA)
        blueprint = self._by_id.get(probe.blueprint_id)
        if blueprint is None:
            raise BlueprintRegistryError(
                "no such blueprint", slug=probe.slug, workspace_id=workspace_id
            )
        return blueprint

    @property
    def ids(self) -> tuple[str, ...]:
        """Every registered blueprint id in stable (sorted) order."""
        return tuple(sorted(self._by_id))

    def all(self) -> tuple[Blueprint, ...]:
        """Every registered blueprint in stable (id) order."""
        return tuple(self._by_id[bid] for bid in self.ids)

    def discover(
        self,
        *,
        workspace_id: str | None = None,
        tenant: str | None = None,
        family: BlueprintFamily | None = None,
        status: BlueprintStatus | None = None,
    ) -> tuple[Blueprint, ...]:
        """Discover blueprints, optionally scoped (stable order; pure read view).

        Authorization and isolation are applied by the service. ``tenant`` (when set)
        returns that tenant's blueprints plus every untenanted (global) blueprint
        (mirrors the project discovery semantics).
        """
        blueprints = self.all()
        if workspace_id is not None:
            blueprints = tuple(b for b in blueprints if b.workspace_id == workspace_id)
        if tenant is not None:
            blueprints = tuple(b for b in blueprints if b.tenant == tenant or b.tenant is None)
        if family is not None:
            blueprints = tuple(b for b in blueprints if b.family is family)
        if status is not None:
            blueprints = tuple(b for b in blueprints if b.status is status)
        return blueprints

    def transition(self, blueprint_id: str, target: BlueprintStatus, *, tick: int) -> Blueprint:
        """Apply a lifecycle transition (fail-closed) and record the event."""
        blueprint = self.get(blueprint_id)
        validate_transition(blueprint.status, target)
        updated = blueprint.with_status(target)
        self._by_id[blueprint_id] = updated
        self._log.append(
            BlueprintEvent(
                sequence=len(self._log),
                blueprint_id=blueprint_id,
                from_status=blueprint.status,
                to_status=target,
                tick=tick,
            )
        )
        return updated

    def update_metadata(self, blueprint_id: str, metadata: BlueprintMetadata) -> Blueprint:
        """Replace a blueprint's metadata immutably (the id/status are preserved)."""
        blueprint = self.get(blueprint_id)
        updated = blueprint.with_metadata(metadata)
        self._by_id[blueprint_id] = updated
        return updated

    # -- versioning -------------------------------------------------------------

    def add_version(
        self, blueprint_id: str, content_hash: str, *, metadata: BlueprintMetadata | None = None
    ) -> BlueprintVersion:
        """Append an immutable content-addressed version to a blueprint's lineage."""
        self.get(blueprint_id)  # fail-closed on absent blueprint
        lineage = self._lineages.get(blueprint_id)
        if lineage is None:
            lineage = VersionLineage(blueprint_id)
            self._lineages[blueprint_id] = lineage
        return lineage.append(content_hash, metadata=metadata)

    def lineage_of(self, blueprint_id: str) -> tuple[BlueprintVersion, ...]:
        """Every version of a blueprint in revision order (empty if never versioned)."""
        lineage = self._lineages.get(blueprint_id)
        return lineage.revisions if lineage is not None else ()

    def current_version(self, blueprint_id: str) -> BlueprintVersion:
        """The current (head) version of a blueprint (fail-closed if never versioned)."""
        lineage = self._lineages.get(blueprint_id)
        if lineage is None:
            raise BlueprintRegistryError("blueprint has no versions", blueprint_id=blueprint_id)
        return lineage.head()

    def version_count(self, blueprint_id: str) -> int:
        """The number of versions recorded for a blueprint."""
        lineage = self._lineages.get(blueprint_id)
        return len(lineage) if lineage is not None else 0

    @property
    def events(self) -> tuple[BlueprintEvent, ...]:
        """An immutable snapshot of the append-only lifecycle event log (in order)."""
        return tuple(self._log)

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_count": len(self._by_id),
            "blueprints": [self._by_id[bid].to_dict() for bid in self.ids],
            "lineages": [self._lineages[bid].to_dict() for bid in sorted(self._lineages)],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["BlueprintRegistry"]
