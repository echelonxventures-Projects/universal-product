"""EC2-TASK-000111 — Generation Request Registry (EC2-EPIC-007).

The deterministic, append-only store of generation requests — the runtime home of
request **submission**, **registration**, **discovery**, **resolution**, and lifecycle
**transition** (Program §2.1 #8, PC-06). A request's identity is content-addressed from
its ``slug``, parent ``workspace_id``, ``blueprint_ref``, and ``submitted_tick``, so
registration is idempotent-safe and fail-closed on genuine duplicates. Mutable facets
are applied immutably: a lifecycle transition or metadata update replaces the stored
:class:`~platform.generation.contracts.GenerationRequest` with a new immutable record
(the id is preserved) and records an ordered, append-only
:class:`~platform.generation.lifecycle.RequestEvent` — so the registry's history is
reproducible and auditable (OP-C3), and any request's full lifecycle is reconstructable
from the event log (persistence / reconstruction, §6).

The registry holds *records only* — it enforces no authorization (that is the Identity
Layer), no isolation (the reused workspace isolation rule), and it resolves neither the
parent workspace nor the referenced blueprint (the service binds them); it is the
substrate the request service composes. It mirrors the certified
:mod:`platform.blueprints.registry` topology exactly.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.generation.contracts import GenerationRequest, RequestStatus
from platform.generation.errors import RequestRegistryError
from platform.generation.lifecycle import RequestEvent, validate_transition
from platform.generation.metadata import RequestMetadata
from typing import Any


class GenerationRequestRegistry:
    """A deterministic, append-only registry of generation requests (submit/resolve/transition)."""

    __slots__ = ("_by_id", "_log")

    def __init__(self) -> None:
        self._by_id: dict[str, GenerationRequest] = {}
        self._log: list[RequestEvent] = []

    def register(self, request: GenerationRequest) -> GenerationRequest:
        """Register a request record (fail-closed on duplicate id)."""
        if not isinstance(request, GenerationRequest):
            raise RequestRegistryError("register requires a GenerationRequest")
        if request.request_id in self._by_id:
            raise RequestRegistryError(
                "generation request already registered",
                request_id=request.request_id,
                slug=request.slug,
            )
        self._by_id[request.request_id] = request
        return request

    def create(
        self,
        slug: str,
        blueprint_ref: str,
        workspace_id: str,
        owner_subject: str,
        family: BlueprintFamily,
        *,
        submitted_tick: int,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: RequestMetadata | None = None,
    ) -> GenerationRequest:
        """Build and register a new SUBMITTED request (fail-closed on duplicate)."""
        request = GenerationRequest.create(
            slug,
            blueprint_ref,
            workspace_id,
            owner_subject,
            family,
            submitted_tick=submitted_tick,
            project_id=project_id,
            tenant=tenant,
            metadata=metadata,
        )
        return self.register(request)

    def __contains__(self, request_id: str) -> bool:
        return request_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def get(self, request_id: str) -> GenerationRequest:
        """Resolve a request by id (fail-closed on absent)."""
        request = self._by_id.get(request_id)
        if request is None:
            raise RequestRegistryError("no such generation request", request_id=request_id)
        return request

    def exists(self, slug: str, workspace_id: str, blueprint_ref: str, submitted_tick: int) -> bool:
        """True iff a request with the given identity coordinates exists."""
        probe = GenerationRequest.create(
            slug,
            blueprint_ref,
            workspace_id,
            "probe",
            BlueprintFamily.DATA,
            submitted_tick=submitted_tick,
        )
        return probe.request_id in self._by_id

    @property
    def ids(self) -> tuple[str, ...]:
        """Every registered request id in stable (sorted) order."""
        return tuple(sorted(self._by_id))

    def all(self) -> tuple[GenerationRequest, ...]:
        """Every registered request in stable (id) order."""
        return tuple(self._by_id[rid] for rid in self.ids)

    def discover(
        self,
        *,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        family: BlueprintFamily | None = None,
        status: RequestStatus | None = None,
        blueprint_ref: str | None = None,
    ) -> tuple[GenerationRequest, ...]:
        """Discover requests, optionally scoped (stable order; pure read view).

        Authorization and isolation are applied by the service. ``tenant`` (when set)
        returns that tenant's requests plus every untenanted (global) request (mirrors
        the blueprint/project discovery semantics).
        """
        requests = self.all()
        if workspace_id is not None:
            requests = tuple(r for r in requests if r.workspace_id == workspace_id)
        if project_id is not None:
            requests = tuple(r for r in requests if r.project_id == project_id)
        if tenant is not None:
            requests = tuple(r for r in requests if r.tenant == tenant or r.tenant is None)
        if family is not None:
            requests = tuple(r for r in requests if r.family is family)
        if status is not None:
            requests = tuple(r for r in requests if r.status is status)
        if blueprint_ref is not None:
            requests = tuple(r for r in requests if r.blueprint_ref == blueprint_ref)
        return requests

    def transition(self, request_id: str, target: RequestStatus, *, tick: int) -> GenerationRequest:
        """Apply a lifecycle transition (fail-closed) and record the event."""
        request = self.get(request_id)
        validate_transition(request.status, target)
        updated = request.with_status(target)
        self._by_id[request_id] = updated
        self._log.append(
            RequestEvent(
                sequence=len(self._log),
                request_id=request_id,
                from_status=request.status,
                to_status=target,
                tick=tick,
            )
        )
        return updated

    def update_metadata(self, request_id: str, metadata: RequestMetadata) -> GenerationRequest:
        """Replace a request's metadata immutably (the id/status are preserved)."""
        request = self.get(request_id)
        updated = request.with_metadata(metadata)
        self._by_id[request_id] = updated
        return updated

    def count_by_status(self) -> dict[str, int]:
        """A deterministic per-status census of the registry (every status present)."""
        tally = {status.value: 0 for status in RequestStatus}
        for request in self._by_id.values():
            tally[request.status.value] += 1
        return tally

    def events_of(self, request_id: str) -> tuple[RequestEvent, ...]:
        """Every recorded lifecycle event for a request, in order (reconstruction, §6)."""
        return tuple(e for e in self._log if e.request_id == request_id)

    @property
    def events(self) -> tuple[RequestEvent, ...]:
        """An immutable snapshot of the append-only lifecycle event log (in order)."""
        return tuple(self._log)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_count": len(self._by_id),
            "requests": [self._by_id[rid].to_dict() for rid in self.ids],
            "status_census": self.count_by_status(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["GenerationRequestRegistry"]
