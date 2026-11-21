"""EC2-TASK-000167 — Runtime Operations Context (EC2-EPIC-012).

The immutable, content-addressed **runtime context** produced when a principal
successfully selects/resolves a governed runtime-operation record: the binding of *who*
(principal + subject) to *what* (operation + kind + runtime unit + certification +
posture) and *where* (optional workspace/project + tenant + environment) and *in what
standing* (operating owner or not). It is the value a downstream surface (later
presentation) carries to operate against a resolved operation by reference. The context is
derived only from an already-authorized, isolation-cleared selection — it grants nothing
on its own and holds no secret material (SEC-04). It is deterministic: identical bindings
yield an identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from platform.runtime_operations.contracts import RuntimeOperationRecord
from platform.runtime_operations.errors import RuntimeOperationServiceError
from platform.runtime_operations.status import RuntimeOperationPosture, derive_status
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeOperationContext:
    """An immutable, content-addressed runtime-operations runtime context binding."""

    context_id: str
    operation_id: str
    kind: str
    runtime_id: str
    blueprint_id: str
    version: str
    environment: str
    certification_id: str
    certified: bool
    reversible: bool
    posture: RuntimeOperationPosture
    request_ref: str | None
    workspace_id: str | None
    project_id: str | None
    principal_id: str
    subject: str
    tenant: str | None
    is_owner: bool

    @classmethod
    def create(
        cls,
        record: RuntimeOperationRecord,
        principal: Principal,
        *,
        is_owner: bool = False,
    ) -> RuntimeOperationContext:
        """Build the deterministic runtime context for a resolved selection."""
        if not isinstance(record, RuntimeOperationRecord):
            raise RuntimeOperationServiceError(
                "runtime operation context requires a RuntimeOperationRecord"
            )
        if not isinstance(principal, Principal):
            raise RuntimeOperationServiceError("runtime operation context requires a Principal")
        if not isinstance(is_owner, bool):
            raise RuntimeOperationServiceError("is_owner must be a bool")
        posture = derive_status(record).posture
        core = {
            "operation_id": record.operation_id,
            "kind": record.kind.value,
            "runtime_id": record.runtime_id,
            "blueprint_id": record.blueprint_id,
            "version": record.version,
            "environment": record.environment,
            "certification_id": record.certification.certification_id,
            "certified": record.certified,
            "reversible": record.reversible,
            "posture": posture.value,
            "request_ref": record.request_ref,
            "workspace_id": record.workspace_id,
            "project_id": record.project_id,
            "principal_id": principal.principal_id,
            "tenant": record.tenant,
            "is_owner": is_owner,
        }
        return cls(
            context_id=f"UCOS-ROCX-{content_hash(core)[:16]}",
            operation_id=record.operation_id,
            kind=record.kind.value,
            runtime_id=record.runtime_id,
            blueprint_id=record.blueprint_id,
            version=record.version,
            environment=record.environment,
            certification_id=record.certification.certification_id,
            certified=record.certified,
            reversible=record.reversible,
            posture=posture,
            request_ref=record.request_ref,
            workspace_id=record.workspace_id,
            project_id=record.project_id,
            principal_id=principal.principal_id,
            subject=principal.subject,
            tenant=record.tenant,
            is_owner=is_owner,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "operation_id": self.operation_id,
            "kind": self.kind,
            "runtime_id": self.runtime_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "environment": self.environment,
            "certification_id": self.certification_id,
            "certified": self.certified,
            "reversible": self.reversible,
            "posture": self.posture.value,
            "request_ref": self.request_ref,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "tenant": self.tenant,
            "is_owner": self.is_owner,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["RuntimeOperationContext"]
