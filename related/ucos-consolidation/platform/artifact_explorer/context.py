"""EC2-TASK-000129 — Artifact Explorer Context (EC2-EPIC-009).

The immutable, content-addressed **runtime context** produced when a principal
successfully navigates to (resolves) an artifact: the binding of *who* (principal +
subject) to *what* (artifact view + request ref + blueprint ref + family +
lifecycle/execution posture) and *where* (workspace + optional project + tenant) and *in
what standing* (request owner or not). It is the value the request-to-artifact
navigation returns to a downstream surface (portal, presentation) to operate against a
resolved artifact by reference. The context is derived only from an already-authorized,
isolation-cleared navigation — it grants nothing on its own and holds no secret material
(SEC-04). It is deterministic: identical bindings yield an identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.artifact_explorer.errors import ArtifactServiceError
from platform.artifact_explorer.references import ArtifactView
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from platform.generation.contracts import ExecutionState, RequestStatus
from platform.generation.status import RequestPosture
from typing import Any


@dataclass(frozen=True, slots=True)
class ArtifactContext:
    """An immutable, content-addressed artifact-explorer runtime context binding."""

    context_id: str
    request_ref: str
    slug: str
    blueprint_ref: str
    family: BlueprintFamily
    lifecycle_status: RequestStatus
    execution_state: ExecutionState
    posture: RequestPosture
    workspace_id: str
    project_id: str | None
    principal_id: str
    subject: str
    tenant: str | None
    is_owner: bool
    has_dispatch: bool
    has_provenance: bool
    is_traceable: bool

    @classmethod
    def create(
        cls,
        view: ArtifactView,
        principal: Principal,
        *,
        is_owner: bool = False,
    ) -> ArtifactContext:
        """Build the deterministic runtime context for a resolved navigation."""
        if not isinstance(view, ArtifactView):
            raise ArtifactServiceError("artifact context requires an ArtifactView")
        if not isinstance(principal, Principal):
            raise ArtifactServiceError("artifact context requires a Principal")
        if not isinstance(is_owner, bool):
            raise ArtifactServiceError("is_owner must be a bool")
        core = {
            "request_ref": view.request_ref,
            "slug": view.slug,
            "blueprint_ref": view.blueprint_ref,
            "family": view.family.value,
            "lifecycle_status": view.lifecycle_status.value,
            "execution_state": view.execution_state.value,
            "posture": view.posture.value,
            "workspace_id": view.workspace_id,
            "project_id": view.project_id,
            "principal_id": principal.principal_id,
            "tenant": view.tenant,
            "is_owner": is_owner,
        }
        return cls(
            context_id=f"UCOS-AXCX-{content_hash(core)[:16]}",
            request_ref=view.request_ref,
            slug=view.slug,
            blueprint_ref=view.blueprint_ref,
            family=view.family,
            lifecycle_status=view.lifecycle_status,
            execution_state=view.execution_state,
            posture=view.posture,
            workspace_id=view.workspace_id,
            project_id=view.project_id,
            principal_id=principal.principal_id,
            subject=principal.subject,
            tenant=view.tenant,
            is_owner=is_owner,
            has_dispatch=view.has_dispatch,
            has_provenance=view.has_provenance,
            is_traceable=view.is_traceable,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "request_ref": self.request_ref,
            "slug": self.slug,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "lifecycle_status": self.lifecycle_status.value,
            "execution_state": self.execution_state.value,
            "posture": self.posture.value,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "tenant": self.tenant,
            "is_owner": self.is_owner,
            "has_dispatch": self.has_dispatch,
            "has_provenance": self.has_provenance,
            "is_traceable": self.is_traceable,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["ArtifactContext"]
