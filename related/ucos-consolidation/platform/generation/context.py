"""EC2-TASK-000114 — Generation Request Context (EC2-EPIC-007).

The immutable, content-addressed **runtime context** produced when a principal
successfully selects/resolves a generation request: the binding of *who* (principal +
subject) to *what* (request + blueprint ref + family + lifecycle/execution state) and
*where* (workspace + optional project + tenant) and *in what standing* (request owner
or not). It is the value a downstream runtime surface (execution dashboard EPIC-008,
artifact explorer EPIC-009, validation console EPIC-010) carries to operate against a
resolved request by reference. The context is derived only from an already-authorized,
isolation-cleared selection — it grants nothing on its own and holds no secret material
(SEC-04). It is deterministic: identical bindings yield an identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from platform.generation.contracts import ExecutionState, GenerationRequest, RequestStatus
from platform.generation.errors import RequestServiceError
from typing import Any


@dataclass(frozen=True, slots=True)
class RequestContext:
    """An immutable, content-addressed generation-request runtime context binding."""

    context_id: str
    request_id: str
    request_slug: str
    blueprint_ref: str
    family: BlueprintFamily
    request_status: RequestStatus
    execution_state: ExecutionState
    workspace_id: str
    project_id: str | None
    principal_id: str
    subject: str
    tenant: str | None
    is_owner: bool

    @classmethod
    def create(
        cls,
        request: GenerationRequest,
        principal: Principal,
        *,
        is_owner: bool = False,
    ) -> RequestContext:
        """Build the deterministic runtime context for a resolved selection."""
        if not isinstance(request, GenerationRequest):
            raise RequestServiceError("request context requires a GenerationRequest")
        if not isinstance(principal, Principal):
            raise RequestServiceError("request context requires a Principal")
        if not isinstance(is_owner, bool):
            raise RequestServiceError("is_owner must be a bool")
        core = {
            "request_id": request.request_id,
            "request_status": request.status.value,
            "blueprint_ref": request.blueprint_ref,
            "family": request.family.value,
            "workspace_id": request.workspace_id,
            "project_id": request.project_id,
            "principal_id": principal.principal_id,
            "tenant": request.tenant,
            "is_owner": is_owner,
        }
        return cls(
            context_id=f"UCOS-GCTX-{content_hash(core)[:16]}",
            request_id=request.request_id,
            request_slug=request.slug,
            blueprint_ref=request.blueprint_ref,
            family=request.family,
            request_status=request.status,
            execution_state=request.execution_state,
            workspace_id=request.workspace_id,
            project_id=request.project_id,
            principal_id=principal.principal_id,
            subject=principal.subject,
            tenant=request.tenant,
            is_owner=is_owner,
        )

    @property
    def is_dispatched(self) -> bool:
        """True iff the bound request has been dispatched to the runtime or beyond."""
        return self.request_status in (
            RequestStatus.DISPATCHED,
            RequestStatus.RUNNING,
            RequestStatus.COMPLETED,
            RequestStatus.FAILED,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "request_id": self.request_id,
            "request_slug": self.request_slug,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "request_status": self.request_status.value,
            "execution_state": self.execution_state.value,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "tenant": self.tenant,
            "is_owner": self.is_owner,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["RequestContext"]
