"""EC2-TASK-000114 — Generation Request Derived Status (EC2-EPIC-007).

The deterministic **derived-status** computation. A request's derived status is a
**pure function** of its stored lifecycle state, its dispatch presence, and its
provenance presence — it consults no wall-clock and no external state, so identical
inputs always yield an identical :class:`DerivedRequestStatus` and an identical
fingerprint (P5).

The derived posture summarizes lifecycle + execution:

    * ``CANCELLED`` — the request was withdrawn (terminal).
    * ``FAILED``    — the request failed (terminal).
    * ``COMPLETED`` — the request completed successfully (terminal).
    * ``RUNNING``   — the request is executing on the runtime.
    * ``DISPATCHED``— the request has been handed off to the runtime.
    * ``QUEUED``    — the request is admitted and awaiting dispatch.
    * ``PENDING``   — the request is submitted/validating/approved.

It also carries the derived :class:`~platform.generation.contracts.ExecutionState`, the
``is_dispatched`` and ``is_traceable`` predicates, and the terminality flag. This module
records/enacts nothing; it derives.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.generation.contracts import (
    ExecutionState,
    GenerationRequest,
    RequestStatus,
    execution_state_for,
)
from platform.generation.errors import RequestStatusError
from typing import Any


class RequestPosture(str, Enum):
    """The deterministic derived posture of a request (lifecycle + execution)."""

    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"
    RUNNING = "running"
    DISPATCHED = "dispatched"
    QUEUED = "queued"
    PENDING = "pending"


_POSTURE: dict[RequestStatus, RequestPosture] = {
    RequestStatus.SUBMITTED: RequestPosture.PENDING,
    RequestStatus.VALIDATING: RequestPosture.PENDING,
    RequestStatus.APPROVED: RequestPosture.PENDING,
    RequestStatus.QUEUED: RequestPosture.QUEUED,
    RequestStatus.DISPATCHED: RequestPosture.DISPATCHED,
    RequestStatus.RUNNING: RequestPosture.RUNNING,
    RequestStatus.COMPLETED: RequestPosture.COMPLETED,
    RequestStatus.FAILED: RequestPosture.FAILED,
    RequestStatus.CANCELLED: RequestPosture.CANCELLED,
}


@dataclass(frozen=True, slots=True)
class DerivedRequestStatus:
    """An immutable, content-addressed derived request status (pure function output)."""

    request_id: str
    lifecycle_status: RequestStatus
    execution_state: ExecutionState
    posture: RequestPosture
    has_dispatch: bool
    has_provenance: bool
    is_dispatched: bool
    is_traceable: bool
    is_terminal: bool
    status_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        request_id: str,
        lifecycle_status: RequestStatus,
        execution_state: ExecutionState,
        posture: RequestPosture,
        has_dispatch: bool,
        has_provenance: bool,
        is_dispatched: bool,
        is_terminal: bool,
    ) -> DerivedRequestStatus:
        # A request is traceable (link-4 present through this node) iff it has been
        # dispatched with a recorded dispatch and carries provenance.
        is_traceable = has_provenance and has_dispatch
        core = {
            "request_id": request_id,
            "lifecycle_status": lifecycle_status.value,
            "execution_state": execution_state.value,
            "posture": posture.value,
            "has_dispatch": has_dispatch,
            "has_provenance": has_provenance,
            "is_dispatched": is_dispatched,
            "is_traceable": is_traceable,
            "is_terminal": is_terminal,
        }
        return cls(
            request_id=request_id,
            lifecycle_status=lifecycle_status,
            execution_state=execution_state,
            posture=posture,
            has_dispatch=has_dispatch,
            has_provenance=has_provenance,
            is_dispatched=is_dispatched,
            is_traceable=is_traceable,
            is_terminal=is_terminal,
            status_id=f"UCOS-GDST-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_id": self.status_id,
            "request_id": self.request_id,
            "lifecycle_status": self.lifecycle_status.value,
            "execution_state": self.execution_state.value,
            "posture": self.posture.value,
            "has_dispatch": self.has_dispatch,
            "has_provenance": self.has_provenance,
            "is_dispatched": self.is_dispatched,
            "is_traceable": self.is_traceable,
            "is_terminal": self.is_terminal,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def derive_status(
    request: GenerationRequest,
    *,
    has_dispatch: bool,
    has_provenance: bool,
) -> DerivedRequestStatus:
    """Derive a deterministic :class:`DerivedRequestStatus` (pure; fail-closed)."""
    if not isinstance(request, GenerationRequest):
        raise RequestStatusError("status derivation requires a GenerationRequest")
    if not isinstance(has_dispatch, bool):
        raise RequestStatusError("has_dispatch must be a bool")
    if not isinstance(has_provenance, bool):
        raise RequestStatusError("has_provenance must be a bool")
    return DerivedRequestStatus.create(
        request_id=request.request_id,
        lifecycle_status=request.status,
        execution_state=execution_state_for(request.status),
        posture=_POSTURE[request.status],
        has_dispatch=has_dispatch,
        has_provenance=has_provenance,
        is_dispatched=request.is_dispatched,
        is_terminal=request.is_terminal,
    )


__all__ = [
    "RequestPosture",
    "DerivedRequestStatus",
    "derive_status",
]
