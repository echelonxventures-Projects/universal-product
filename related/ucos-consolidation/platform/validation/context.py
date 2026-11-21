"""EC2-TASK-000148 — Validation Console Context (EC2-EPIC-010).

The immutable, content-addressed **runtime context** produced when a principal
successfully selects/resolves a validation record: the binding of *who* (principal +
subject) to *what* (record + target + blueprint + verdict/posture) and *where* (optional
workspace/project + tenant) and *in what standing* (surfacing owner or not). It is the
value a downstream surface (EPIC-011 certification console, later presentation) carries
to operate against a resolved validation by reference. The context is derived only from
an already-authorized, isolation-cleared selection — it grants nothing on its own and
holds no secret material (SEC-04). It is deterministic: identical bindings yield an
identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from platform.validation.contracts import ValidationRecord
from platform.validation.errors import ValidationServiceError
from platform.validation.status import ValidationPosture, derive_status
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationContext:
    """An immutable, content-addressed validation-console runtime context binding."""

    context_id: str
    record_id: str
    target_id: str
    blueprint_id: str
    verdict: str
    accepted: bool
    posture: ValidationPosture
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
        record: ValidationRecord,
        principal: Principal,
        *,
        is_owner: bool = False,
    ) -> ValidationContext:
        """Build the deterministic runtime context for a resolved selection."""
        if not isinstance(record, ValidationRecord):
            raise ValidationServiceError("validation context requires a ValidationRecord")
        if not isinstance(principal, Principal):
            raise ValidationServiceError("validation context requires a Principal")
        if not isinstance(is_owner, bool):
            raise ValidationServiceError("is_owner must be a bool")
        posture = derive_status(record.report).posture
        core = {
            "record_id": record.record_id,
            "target_id": record.target_id,
            "blueprint_id": record.blueprint_id,
            "verdict": record.report.verdict.value,
            "accepted": record.accepted,
            "posture": posture.value,
            "request_ref": record.request_ref,
            "workspace_id": record.workspace_id,
            "project_id": record.project_id,
            "principal_id": principal.principal_id,
            "tenant": record.tenant,
            "is_owner": is_owner,
        }
        return cls(
            context_id=f"UCOS-VCTX-{content_hash(core)[:16]}",
            record_id=record.record_id,
            target_id=record.target_id,
            blueprint_id=record.blueprint_id,
            verdict=record.report.verdict.value,
            accepted=record.accepted,
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
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "verdict": self.verdict,
            "accepted": self.accepted,
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


__all__ = ["ValidationContext"]
