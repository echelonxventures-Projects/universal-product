"""EC2-TASK-000102 — Blueprint Context (EC2-EPIC-006).

The immutable, content-addressed **runtime context** produced when a principal
successfully selects/resolves a blueprint: the binding of *who* (principal + subject)
to *what* (blueprint + family + status) and *where* (workspace + optional project +
tenant) and *in what standing* (blueprint owner or not). It is the value a downstream
runtime surface (generation requests, EPIC-007) carries to operate against a resolved
blueprint by reference. The context is derived only from an already-authorized,
isolation-cleared selection — it grants nothing on its own and holds no secret material
(SEC-04). It is deterministic: identical bindings yield an identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.contracts import Blueprint, BlueprintFamily, BlueprintStatus
from platform.blueprints.errors import BlueprintServiceError
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from typing import Any


@dataclass(frozen=True, slots=True)
class BlueprintContext:
    """An immutable, content-addressed blueprint runtime context binding."""

    context_id: str
    blueprint_id: str
    blueprint_slug: str
    family: BlueprintFamily
    blueprint_status: BlueprintStatus
    workspace_id: str
    project_id: str | None
    principal_id: str
    subject: str
    tenant: str | None
    is_owner: bool

    @classmethod
    def create(
        cls,
        blueprint: Blueprint,
        principal: Principal,
        *,
        is_owner: bool = False,
    ) -> BlueprintContext:
        """Build the deterministic runtime context for a resolved selection."""
        if not isinstance(blueprint, Blueprint):
            raise BlueprintServiceError("blueprint context requires a Blueprint")
        if not isinstance(principal, Principal):
            raise BlueprintServiceError("blueprint context requires a Principal")
        if not isinstance(is_owner, bool):
            raise BlueprintServiceError("is_owner must be a bool")
        core = {
            "blueprint_id": blueprint.blueprint_id,
            "blueprint_status": blueprint.status.value,
            "family": blueprint.family.value,
            "workspace_id": blueprint.workspace_id,
            "project_id": blueprint.project_id,
            "principal_id": principal.principal_id,
            "tenant": blueprint.tenant,
            "is_owner": is_owner,
        }
        return cls(
            context_id=f"UCOS-BCTX-{content_hash(core)[:16]}",
            blueprint_id=blueprint.blueprint_id,
            blueprint_slug=blueprint.slug,
            family=blueprint.family,
            blueprint_status=blueprint.status,
            workspace_id=blueprint.workspace_id,
            project_id=blueprint.project_id,
            principal_id=principal.principal_id,
            subject=principal.subject,
            tenant=blueprint.tenant,
            is_owner=is_owner,
        )

    @property
    def is_catalogued(self) -> bool:
        """True iff the bound blueprint is CATALOGUED."""
        return self.blueprint_status is BlueprintStatus.CATALOGUED

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "blueprint_id": self.blueprint_id,
            "blueprint_slug": self.blueprint_slug,
            "family": self.family.value,
            "blueprint_status": self.blueprint_status.value,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "tenant": self.tenant,
            "is_owner": self.is_owner,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["BlueprintContext"]
