"""EC2-TASK-000157 — Certification Console Context (EC2-EPIC-011).

The immutable, content-addressed **runtime context** produced when a principal
successfully selects/resolves a certification record: the binding of *who* (principal +
subject) to *what* (record + certification + target + status/posture) and *where*
(optional workspace/project + tenant) and *in what standing* (surfacing owner or not). It
is the value a downstream surface (later presentation) carries to operate against a
resolved certification by reference. The context is derived only from an already-authorized,
isolation-cleared selection — it grants nothing on its own and holds no secret material
(SEC-04). It is deterministic: identical bindings yield an identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.certification.contracts import CertificationConsoleRecord
from platform.certification.errors import CertificationServiceError
from platform.certification.status import CertificationPosture, derive_status
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from typing import Any


@dataclass(frozen=True, slots=True)
class CertificationContext:
    """An immutable, content-addressed certification-console runtime context binding."""

    context_id: str
    record_id: str
    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    certified: bool
    posture: CertificationPosture
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
        record: CertificationConsoleRecord,
        principal: Principal,
        *,
        is_owner: bool = False,
    ) -> CertificationContext:
        """Build the deterministic runtime context for a resolved selection."""
        if not isinstance(record, CertificationConsoleRecord):
            raise CertificationServiceError(
                "certification context requires a CertificationConsoleRecord"
            )
        if not isinstance(principal, Principal):
            raise CertificationServiceError("certification context requires a Principal")
        if not isinstance(is_owner, bool):
            raise CertificationServiceError("is_owner must be a bool")
        posture = derive_status(record.decision).posture
        core = {
            "record_id": record.record_id,
            "certification_id": record.certification_id,
            "target_id": record.target_id,
            "blueprint_id": record.blueprint_id,
            "version": record.version,
            "status": record.record.status.value,
            "certified": record.certified,
            "posture": posture.value,
            "request_ref": record.request_ref,
            "workspace_id": record.workspace_id,
            "project_id": record.project_id,
            "principal_id": principal.principal_id,
            "tenant": record.tenant,
            "is_owner": is_owner,
        }
        return cls(
            context_id=f"UCOS-CCTX-{content_hash(core)[:16]}",
            record_id=record.record_id,
            certification_id=record.certification_id,
            target_id=record.target_id,
            blueprint_id=record.blueprint_id,
            version=record.version,
            status=record.record.status.value,
            certified=record.certified,
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
            "record_id": self.record_id,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status,
            "certified": self.certified,
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


__all__ = ["CertificationContext"]
