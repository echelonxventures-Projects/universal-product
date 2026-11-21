"""EC2-TASK-000103 — Blueprint Catalog (EC2-EPIC-006).

The **L6 Knowledge-Layer read model / index** over registered blueprints (Program §4.1
L6, §2.2 PC-05). The catalog is a **platform-owned read model, never a source of
generation truth** (Determination §4.6, §8): it surfaces only blueprints that have been
structurally validated + classified and published (``CATALOGUED``; ``SUPERSEDED``
entries remain visible for audit/provenance), each carrying its **provenance-by-
reference** to the ``05-GENERATION`` origin — so every catalog entry is a materialized
``05-GENERATION → 06-IMPLEMENTATION`` trace edge (link-4, §5.5).

The catalog raises no new query engine and no new persistence — it is a deterministic
in-memory index over the blueprint registry and the provenance ledger (no server, no
socket, no filesystem write). An admissibility invariant makes traceability
machine-checkable: **a cataloged blueprint must carry provenance** (missing provenance
⇒ not admissible, §10 traceability validation) — the service enforces this at publish
time and the catalog surfaces it.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.contracts import Blueprint, BlueprintFamily, BlueprintStatus
from platform.blueprints.errors import BlueprintCatalogError
from platform.blueprints.provenance import BlueprintProvenance, ProvenanceLedger
from platform.blueprints.registry import BlueprintRegistry
from platform.foundation.contracts import content_hash
from typing import Any

#: The lifecycle states a blueprint is visible in the catalog read model.
_CATALOG_VISIBLE: frozenset[BlueprintStatus] = frozenset(
    {BlueprintStatus.CATALOGUED, BlueprintStatus.SUPERSEDED}
)


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    """An immutable catalog entry: a cataloged blueprint plus its link-4 provenance."""

    blueprint: Blueprint
    provenance: BlueprintProvenance

    @property
    def blueprint_id(self) -> str:
        return self.blueprint.blueprint_id

    @property
    def is_traceable(self) -> bool:
        """True iff the entry carries a materially present generation→implementation edge."""
        return self.provenance.is_traceable

    def trace_edge(self) -> dict[str, Any]:
        """The link-4 trace edge for this catalog entry (§5.5)."""
        return self.provenance.trace_edge()

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint": self.blueprint.to_dict(),
            "provenance": self.provenance.to_dict(),
            "is_traceable": self.is_traceable,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class BlueprintCatalog:
    """A deterministic L6 read model / index over cataloged, provenance-carrying blueprints."""

    __slots__ = ("_registry", "_provenance")

    def __init__(self, registry: BlueprintRegistry, provenance: ProvenanceLedger) -> None:
        if not isinstance(registry, BlueprintRegistry):
            raise BlueprintCatalogError("a valid BlueprintRegistry is required")
        if not isinstance(provenance, ProvenanceLedger):
            raise BlueprintCatalogError("a valid ProvenanceLedger is required")
        self._registry = registry
        self._provenance = provenance

    def _visible(
        self,
        *,
        workspace_id: str | None = None,
        tenant: str | None = None,
        family: BlueprintFamily | None = None,
    ) -> tuple[Blueprint, ...]:
        blueprints = self._registry.discover(
            workspace_id=workspace_id, tenant=tenant, family=family
        )
        return tuple(b for b in blueprints if b.status in _CATALOG_VISIBLE)

    def __len__(self) -> int:
        """The number of blueprints currently visible in the catalog."""
        return len(self._visible())

    def __contains__(self, blueprint_id: str) -> bool:
        if blueprint_id not in self._registry:
            return False
        blueprint = self._registry.get(blueprint_id)
        return blueprint.status in _CATALOG_VISIBLE and self._provenance.has(blueprint_id)

    def entry(self, blueprint_id: str) -> CatalogEntry:
        """Resolve a catalog entry by blueprint id (fail-closed on absent/uncataloged).

        Enforces the admissibility invariant: a cataloged blueprint must carry
        provenance (§10) — an entry without provenance is not admissible.
        """
        blueprint = self._registry.get(blueprint_id)
        if blueprint.status not in _CATALOG_VISIBLE:
            raise BlueprintCatalogError(
                "blueprint is not published in the catalog",
                blueprint_id=blueprint_id,
                status=blueprint.status.value,
            )
        if not self._provenance.has(blueprint_id):
            raise BlueprintCatalogError(
                "cataloged blueprint lacks provenance (not admissible)",
                blueprint_id=blueprint_id,
            )
        return CatalogEntry(blueprint=blueprint, provenance=self._provenance.get(blueprint_id))

    def entries(
        self,
        *,
        workspace_id: str | None = None,
        tenant: str | None = None,
        family: BlueprintFamily | None = None,
    ) -> tuple[CatalogEntry, ...]:
        """Every admissible catalog entry (optionally scoped), in stable (id) order."""
        result: list[CatalogEntry] = []
        for blueprint in self._visible(workspace_id=workspace_id, tenant=tenant, family=family):
            if self._provenance.has(blueprint.blueprint_id):
                result.append(
                    CatalogEntry(
                        blueprint=blueprint,
                        provenance=self._provenance.get(blueprint.blueprint_id),
                    )
                )
        result.sort(key=lambda e: e.blueprint_id)
        return tuple(result)

    def blueprint_ids(self) -> tuple[str, ...]:
        """Every admissible cataloged blueprint id, in stable (sorted) order."""
        return tuple(e.blueprint_id for e in self.entries())

    def trace(self, blueprint_id: str) -> dict[str, Any]:
        """The link-4 trace edge for a cataloged blueprint (fail-closed)."""
        return self.entry(blueprint_id).trace_edge()

    def to_dict(self) -> dict[str, Any]:
        entries = self.entries()
        return {
            "entry_count": len(entries),
            "entries": [e.to_dict() for e in entries],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["CatalogEntry", "BlueprintCatalog"]
