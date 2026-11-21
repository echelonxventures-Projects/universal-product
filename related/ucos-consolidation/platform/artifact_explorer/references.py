"""EC2-TASK-000128 — Artifact Explorer Reference Views (EC2-EPIC-009).

The immutable, content-addressed **read-only projections** of a generation artifact —
the value types the Artifact Explorer surfaces. Every projection is derived **by
reference** from a certified EC-2 :class:`~platform.generation.contracts.GenerationRequest`
(the artifact's originating request) plus its optional
:class:`~platform.generation.dispatch.DispatchRecord` (the execution handoff) and
:class:`~platform.generation.provenance.RequestProvenance` (the link-4 provenance-by
-reference). The explorer **generates no artifact and mutates none** — it composes a
faithful, deterministic view over references that already exist (no duplicate artifact
model). The recorded ``family`` is the frozen EC-1 classification the platform records
read-only.

    * :class:`ArtifactReference` — the minimal, content-addressed reference identifying an
      artifact by its request/blueprint/generation-artifact/implementation citations.
    * :class:`ArtifactSummary` — a lightweight discovery record (slug, family, derived
      posture, presence flags) suitable for lists and search hits.
    * :class:`ArtifactView` — the full read view of a single artifact (summary + reference
      + derived lifecycle/execution status + scoping) for artifact lookup.

All ids are content-addressed and reproducible (IMP-007 §5). The projections hold no
secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.artifact_explorer.errors import ArtifactReferenceError
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.generation.contracts import ExecutionState, GenerationRequest, RequestStatus
from platform.generation.dispatch import DispatchRecord
from platform.generation.provenance import RequestProvenance
from platform.generation.status import RequestPosture, derive_status
from typing import Any


def _require_request(request: Any) -> GenerationRequest:
    if not isinstance(request, GenerationRequest):
        raise ArtifactReferenceError("artifact projection requires a GenerationRequest")
    return request


def _optional_dispatch(dispatch: Any) -> DispatchRecord | None:
    if dispatch is not None and not isinstance(dispatch, DispatchRecord):
        raise ArtifactReferenceError("dispatch must be a DispatchRecord when provided")
    return dispatch


def _optional_provenance(provenance: Any) -> RequestProvenance | None:
    if provenance is not None and not isinstance(provenance, RequestProvenance):
        raise ArtifactReferenceError("provenance must be a RequestProvenance when provided")
    return provenance


@dataclass(frozen=True, slots=True)
class ArtifactReference:
    """An immutable, content-addressed reference to a generation artifact (by reference).

    Binds the artifact's originating ``request_ref`` and referenced ``blueprint_ref`` to
    its ``generation_artifact_id`` (the ``05-GENERATION`` origin, from provenance) and
    ``implementation_target`` (the downstream implementation, from provenance), carrying
    the ``content_hash`` handed off/recorded and the dispatch/provenance presence flags.
    ``reference_id`` is content-addressed (deterministic); it identifies the *reference*,
    not a new artifact record.
    """

    reference_id: str
    request_ref: str
    blueprint_ref: str
    family: BlueprintFamily
    generation_artifact_id: str
    implementation_target: str
    content_hash: str
    has_dispatch: bool
    has_provenance: bool

    @classmethod
    def create(
        cls,
        request: GenerationRequest,
        *,
        dispatch: DispatchRecord | None = None,
        provenance: RequestProvenance | None = None,
    ) -> ArtifactReference:
        """Build a content-addressed artifact reference from existing citations."""
        req = _require_request(request)
        disp = _optional_dispatch(dispatch)
        prov = _optional_provenance(provenance)
        generation_artifact_id = prov.generation_artifact_id if prov is not None else ""
        implementation_target = prov.implementation_target if prov is not None else ""
        if prov is not None:
            digest = prov.content_hash
        elif disp is not None:
            digest = disp.content_hash
        else:
            digest = ""
        core = {
            "request_ref": req.request_id,
            "blueprint_ref": req.blueprint_ref,
            "family": req.family.value,
            "generation_artifact_id": generation_artifact_id,
            "implementation_target": implementation_target,
            "content_hash": digest,
            "has_dispatch": disp is not None,
            "has_provenance": prov is not None,
        }
        return cls(
            reference_id=f"UCOS-AXRF-{content_hash(core)[:16]}",
            request_ref=req.request_id,
            blueprint_ref=req.blueprint_ref,
            family=req.family,
            generation_artifact_id=generation_artifact_id,
            implementation_target=implementation_target,
            content_hash=digest,
            has_dispatch=disp is not None,
            has_provenance=prov is not None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "request_ref": self.request_ref,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "generation_artifact_id": self.generation_artifact_id,
            "implementation_target": self.implementation_target,
            "content_hash": self.content_hash,
            "has_dispatch": self.has_dispatch,
            "has_provenance": self.has_provenance,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ArtifactSummary:
    """An immutable, content-addressed lightweight artifact discovery record.

    A faithful projection of a :class:`GenerationRequest` plus its dispatch/provenance
    presence, carrying the derived lifecycle status and posture — the value surfaced in
    discovery lists and search hits.
    """

    summary_id: str
    request_ref: str
    slug: str
    blueprint_ref: str
    family: BlueprintFamily
    lifecycle_status: RequestStatus
    posture: RequestPosture
    has_dispatch: bool
    has_provenance: bool
    is_traceable: bool
    tenant: str | None
    workspace_id: str
    project_id: str | None
    owner_subject: str

    @classmethod
    def from_request(
        cls,
        request: GenerationRequest,
        *,
        has_dispatch: bool,
        has_provenance: bool,
    ) -> ArtifactSummary:
        """Build a deterministic summary projection (pure; fail-closed)."""
        req = _require_request(request)
        if not isinstance(has_dispatch, bool):
            raise ArtifactReferenceError("has_dispatch must be a bool")
        if not isinstance(has_provenance, bool):
            raise ArtifactReferenceError("has_provenance must be a bool")
        derived = derive_status(req, has_dispatch=has_dispatch, has_provenance=has_provenance)
        core = {
            "request_ref": req.request_id,
            "slug": req.slug,
            "blueprint_ref": req.blueprint_ref,
            "family": req.family.value,
            "lifecycle_status": req.status.value,
            "posture": derived.posture.value,
            "has_dispatch": has_dispatch,
            "has_provenance": has_provenance,
            "is_traceable": derived.is_traceable,
            "tenant": req.tenant,
            "workspace_id": req.workspace_id,
            "project_id": req.project_id,
            "owner_subject": req.owner_subject,
        }
        return cls(
            summary_id=f"UCOS-AXSM-{content_hash(core)[:16]}",
            request_ref=req.request_id,
            slug=req.slug,
            blueprint_ref=req.blueprint_ref,
            family=req.family,
            lifecycle_status=req.status,
            posture=derived.posture,
            has_dispatch=has_dispatch,
            has_provenance=has_provenance,
            is_traceable=derived.is_traceable,
            tenant=req.tenant,
            workspace_id=req.workspace_id,
            project_id=req.project_id,
            owner_subject=req.owner_subject,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "request_ref": self.request_ref,
            "slug": self.slug,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "lifecycle_status": self.lifecycle_status.value,
            "posture": self.posture.value,
            "has_dispatch": self.has_dispatch,
            "has_provenance": self.has_provenance,
            "is_traceable": self.is_traceable,
            "tenant": self.tenant,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "owner_subject": self.owner_subject,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ArtifactView:
    """An immutable, content-addressed full read view of a single artifact.

    Composes the :class:`ArtifactSummary` scoping, the :class:`ArtifactReference`
    citations, and the derived lifecycle + execution status into the value returned by an
    artifact lookup. It grants nothing and holds no secret material (SEC-04).
    """

    view_id: str
    request_ref: str
    slug: str
    blueprint_ref: str
    family: BlueprintFamily
    lifecycle_status: RequestStatus
    execution_state: ExecutionState
    posture: RequestPosture
    workspace_id: str
    project_id: str | None
    tenant: str | None
    owner_subject: str
    has_dispatch: bool
    has_provenance: bool
    is_traceable: bool
    reference: ArtifactReference

    @classmethod
    def from_request(
        cls,
        request: GenerationRequest,
        *,
        dispatch: DispatchRecord | None = None,
        provenance: RequestProvenance | None = None,
    ) -> ArtifactView:
        """Build a deterministic full artifact view (pure; fail-closed)."""
        req = _require_request(request)
        disp = _optional_dispatch(dispatch)
        prov = _optional_provenance(provenance)
        has_dispatch = disp is not None
        has_provenance = prov is not None
        derived = derive_status(req, has_dispatch=has_dispatch, has_provenance=has_provenance)
        reference = ArtifactReference.create(req, dispatch=disp, provenance=prov)
        core = {
            "request_ref": req.request_id,
            "slug": req.slug,
            "blueprint_ref": req.blueprint_ref,
            "family": req.family.value,
            "lifecycle_status": req.status.value,
            "execution_state": req.execution_state.value,
            "posture": derived.posture.value,
            "workspace_id": req.workspace_id,
            "project_id": req.project_id,
            "tenant": req.tenant,
            "owner_subject": req.owner_subject,
            "reference": reference.to_dict(),
        }
        return cls(
            view_id=f"UCOS-AXVW-{content_hash(core)[:16]}",
            request_ref=req.request_id,
            slug=req.slug,
            blueprint_ref=req.blueprint_ref,
            family=req.family,
            lifecycle_status=req.status,
            execution_state=req.execution_state,
            posture=derived.posture,
            workspace_id=req.workspace_id,
            project_id=req.project_id,
            tenant=req.tenant,
            owner_subject=req.owner_subject,
            has_dispatch=has_dispatch,
            has_provenance=has_provenance,
            is_traceable=derived.is_traceable,
            reference=reference,
        )

    def summary(self) -> ArtifactSummary:
        """The lightweight summary projection for this view (deterministic)."""
        return ArtifactSummary(
            summary_id=f"UCOS-AXSM-{content_hash(self._summary_core())[:16]}",
            request_ref=self.request_ref,
            slug=self.slug,
            blueprint_ref=self.blueprint_ref,
            family=self.family,
            lifecycle_status=self.lifecycle_status,
            posture=self.posture,
            has_dispatch=self.has_dispatch,
            has_provenance=self.has_provenance,
            is_traceable=self.is_traceable,
            tenant=self.tenant,
            workspace_id=self.workspace_id,
            project_id=self.project_id,
            owner_subject=self.owner_subject,
        )

    def _summary_core(self) -> dict[str, Any]:
        return {
            "request_ref": self.request_ref,
            "slug": self.slug,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "lifecycle_status": self.lifecycle_status.value,
            "posture": self.posture.value,
            "has_dispatch": self.has_dispatch,
            "has_provenance": self.has_provenance,
            "is_traceable": self.is_traceable,
            "tenant": self.tenant,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "owner_subject": self.owner_subject,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "request_ref": self.request_ref,
            "slug": self.slug,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "lifecycle_status": self.lifecycle_status.value,
            "execution_state": self.execution_state.value,
            "posture": self.posture.value,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "tenant": self.tenant,
            "owner_subject": self.owner_subject,
            "has_dispatch": self.has_dispatch,
            "has_provenance": self.has_provenance,
            "is_traceable": self.is_traceable,
            "reference": self.reference.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["ArtifactReference", "ArtifactSummary", "ArtifactView"]
