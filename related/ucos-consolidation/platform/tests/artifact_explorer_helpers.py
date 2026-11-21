"""Shared builders for the EC2-EPIC-009 Artifact Explorer test suite.

These helpers construct the read-only explorer over a directly-populated EC2-EPIC-007
substrate (registry + dispatch ledger + provenance ledger) so the explorer tests are
isolated from the generation-request authorization flow while still consuming genuine
EPIC-007 records by reference.
"""

from __future__ import annotations

from platform.artifact_explorer.service import build_artifact_explorer_service
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.identity import Permission, Principal, Role
from platform.generation.contracts import RequestStatus
from platform.generation.dispatch import DispatchLedger, DispatchRecord
from platform.generation.provenance import ProvenanceLedger, RequestProvenance
from platform.generation.registry import GenerationRequestRegistry
from platform.identity.contracts import CapabilityGroup
from platform.identity.roles import (
    RoleDefinition,
    RoleGrant,
    RoleRegistry,
    default_role_definitions,
)
from platform.identity.service import build_authorization_service

# --------------------------------------------------------------------------- #
# Substrate population (genuine EPIC-007 records, consumed by reference)        #
# --------------------------------------------------------------------------- #


def make_request(
    registry: GenerationRequestRegistry,
    *,
    slug: str = "artifact-1",
    blueprint: str = "UCOS-BLPR-1",
    workspace_id: str = "UCOS-WSPC-1",
    owner: str = "arch@x",
    tenant: str | None = None,
    family: BlueprintFamily = BlueprintFamily.DATA,
    tick: int = 1,
    project_id: str | None = None,
):
    """Create and register a SUBMITTED generation request (the artifact origin)."""
    return registry.create(
        slug,
        blueprint,
        workspace_id,
        owner,
        family,
        submitted_tick=tick,
        tenant=tenant,
        project_id=project_id,
    )


def drive_to_queued(registry: GenerationRequestRegistry, request):
    """Advance a request SUBMITTED → QUEUED (append-only transitions)."""
    registry.transition(request.request_id, RequestStatus.VALIDATING, tick=2)
    registry.transition(request.request_id, RequestStatus.APPROVED, tick=3)
    registry.transition(request.request_id, RequestStatus.QUEUED, tick=4)
    return registry.get(request.request_id)


def dispatch_for(dispatch: DispatchLedger, request, *, tick: int = 5, content_hash: str = "c0ffee"):
    """Record an execution-dispatch handoff for a request (by reference)."""
    return dispatch.record(
        DispatchRecord.create(
            request_ref=request.request_id,
            blueprint_ref=request.blueprint_ref,
            family=request.family,
            content_hash=content_hash,
            tick=tick,
        )
    )


def provenance_for(
    provenance: ProvenanceLedger, request, *, content_hash: str = "c0ffee"
) -> RequestProvenance:
    """Record a link-4 provenance-by-reference for a request."""
    return provenance.record(
        RequestProvenance.create(
            request_ref=request.request_id,
            blueprint_ref=request.blueprint_ref,
            family=request.family,
            generation_reference="GEN-DATA-001",
            generation_artifact_id="BP-DATA-0001",
            blueprint_provenance_ref="UCOS-BPRV-xyz",
            implementation_target="platform/generation",
            content_hash=content_hash,
            dependency_chain=("EPIC-006",),
        )
    )


# --------------------------------------------------------------------------- #
# Authorization fixtures                                                        #
# --------------------------------------------------------------------------- #


def session(
    auth, *, role: Role = Role.ARCHITECT, subject: str = "arch@x", tenant: str | None = None
):
    """Establish a session for a principal bearing ``role`` (default: architect)."""
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def no_grant_auth(*, events=None):
    """An authorization service whose OPERATOR role holds no artifact-explorer grant."""
    roles = RoleRegistry()
    roles.register_all([RoleDefinition(role=Role.OPERATOR, grants={})])
    return build_authorization_service(roles=roles, events=events)


def admin_auth(*, events=None):
    """An authorization service granting ADMINISTER on artifact-explorer to the admin role."""
    definitions = [
        d for d in default_role_definitions() if d.role is not Role.PLATFORM_ADMINISTRATOR
    ]
    definitions.append(
        RoleDefinition(
            role=Role.PLATFORM_ADMINISTRATOR,
            grants={
                CapabilityGroup.ARTIFACT_EXPLORER: RoleGrant(
                    group=CapabilityGroup.ARTIFACT_EXPLORER,
                    permissions=frozenset({Permission.READ, Permission.ADMINISTER}),
                )
            },
        )
    )
    roles = RoleRegistry()
    roles.register_all(definitions)
    return build_authorization_service(roles=roles, events=events)


# --------------------------------------------------------------------------- #
# Explorer composition                                                          #
# --------------------------------------------------------------------------- #


def explorer(*, events=None, observability=None, authorization=None):
    """Build an explorer over a fresh EPIC-007 substrate; return (auth, reg, disp, prov, svc)."""
    auth = authorization or build_authorization_service(events=events)
    registry = GenerationRequestRegistry()
    dispatch = DispatchLedger()
    provenance = ProvenanceLedger()
    service = build_artifact_explorer_service(
        authorization=auth,
        registry=registry,
        dispatch=dispatch,
        provenance=provenance,
        observability=observability,
        events=events,
    )
    return auth, registry, dispatch, provenance, service


def seeded_artifact(
    registry, dispatch, provenance, *, tenant=None, owner="arch@x", slug="artifact-1"
):
    """Create a fully-traceable artifact (queued, dispatched, provenance) and return the request."""
    req = make_request(registry, slug=slug, owner=owner, tenant=tenant)
    drive_to_queued(registry, req)
    registry.transition(req.request_id, RequestStatus.DISPATCHED, tick=5)
    dispatch_for(dispatch, req)
    provenance_for(provenance, req)
    return registry.get(req.request_id)
