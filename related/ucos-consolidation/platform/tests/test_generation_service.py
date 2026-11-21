"""EC2-TASK-000117 — Generation request service tests (EC2-EPIC-007).

Covers the governed L3 composition point end to end: fail-closed construction and
component validation, authorization-gated submission scoped to an active parent
workspace with owner recording, the full lifecycle (validate → approve → queue →
dispatch → run → complete) and the fail/cancel branches, the governed execution-dispatch
boundary (QUEUED-only, DispatchRecord recorded, no bypass), provenance recording, the
composed access decision (identity ∧ isolation ∧ owner/administrator scoping) including
every denial reason, retrieval/list/select/context, status tracking, trace (link-4
evidence), metadata, search delegation, deterministic evidence (P5), observability
metrics, and governed-action emission.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Permission, Principal, Role
from platform.generation.contracts import RequestAction, RequestStatus
from platform.generation.dispatch import FACTORY_CONTRACT, DispatchLedger
from platform.generation.errors import (
    RequestAccessError,
    RequestDispatchError,
    RequestServiceError,
)
from platform.generation.health import RequestHealth, generation_request_health_checks
from platform.generation.provenance import ProvenanceLedger, RequestProvenance
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.search import RequestSearch
from platform.generation.service import (
    METRIC_COMPLETED,
    METRIC_DISPATCHED,
    METRIC_LIFECYCLE_LATENCY,
    METRIC_QUEUE_DEPTH,
    METRIC_SUBMITTED,
    REQUEST_ACCESS_EVENT,
    REQUEST_DISPATCHED_EVENT,
    REQUEST_HEALTH_CHANGED_EVENT,
    REQUEST_PROVENANCE_LINKED_EVENT,
    REQUEST_SUBMITTED_EVENT,
    GenerationRequestService,
    build_generation_request_service,
)
from platform.identity.contracts import CapabilityGroup
from platform.identity.roles import (
    RoleDefinition,
    RoleGrant,
    RoleRegistry,
    default_role_definitions,
)
from platform.identity.service import build_authorization_service
from platform.observability.health import HealthRegistry
from platform.observability.service import build_observability_service
from platform.workspace.contracts import WorkspaceStatus
from platform.workspace.errors import WorkspaceRegistryError
from platform.workspace.registration import WorkspaceRegistry

import pytest

# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _fixture(*, events=None, observability=None, authorization=None):
    auth = authorization or build_authorization_service(events=events)
    workspaces = WorkspaceRegistry()
    service = build_generation_request_service(
        authorization=auth,
        workspaces=workspaces,
        observability=observability,
        events=events,
    )
    return auth, workspaces, service


def _session(auth, role=Role.ARCHITECT, subject="arch@x", tenant=None):
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def _workspace(workspaces, *, tenant=None, slug="team"):
    return workspaces.create(slug, slug.title(), "owner@x", tenant=tenant)


def _submitted(auth, workspaces, service, *, subject="arch@x", tenant=None, slug="req-1"):
    ws = _workspace(workspaces, tenant=tenant, slug=f"ws-{slug}")
    session = _session(auth, subject=subject, tenant=tenant)
    req = service.submit_request(
        session.session_id, slug, "UCOS-BLPR-abc", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    return session, req


def _queued(auth, workspaces, service, **kw):
    session, req = _submitted(auth, workspaces, service, **kw)
    service.start_validation(session.session_id, req.request_id, now=2)
    service.approve(session.session_id, req.request_id, now=3)
    service.enqueue(session.session_id, req.request_id, now=4)
    return session, req


def _completed(auth, workspaces, service, **kw):
    session, req = _queued(auth, workspaces, service, **kw)
    service.dispatch_request(session.session_id, req.request_id, now=5, content_hash="c0ffee")
    service.mark_running(session.session_id, req.request_id, now=6)
    service.complete(session.session_id, req.request_id, now=7)
    return session, req


def _provenance(request_id):
    return RequestProvenance.create(
        request_ref=request_id,
        blueprint_ref="UCOS-BLPR-abc",
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        blueprint_provenance_ref="UCOS-BPRV-xyz",
        implementation_target="platform/generation",
        content_hash="c0ffee",
        dependency_chain=("EPIC-006",),
    )


def _valid_kwargs(auth, workspaces):
    reg = GenerationRequestRegistry()
    dispatch = DispatchLedger()
    prov = ProvenanceLedger()
    hr = HealthRegistry()
    for check in generation_request_health_checks():
        hr.register(check)
    return {
        "registry": reg,
        "dispatch": dispatch,
        "provenance": prov,
        "authorization": auth,
        "workspaces": workspaces,
        "search": RequestSearch(reg, auth),
        "health": RequestHealth(reg, dispatch),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction                                                                 #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization_and_workspaces():
    with pytest.raises(RequestServiceError):
        build_generation_request_service(authorization="nope", workspaces=WorkspaceRegistry())  # type: ignore[arg-type]
    with pytest.raises(RequestServiceError):
        build_generation_request_service(
            authorization=build_authorization_service(),
            workspaces="nope",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "field",
    [
        "registry",
        "dispatch",
        "provenance",
        "authorization",
        "workspaces",
        "search",
        "health",
        "health_registry",
    ],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    workspaces = WorkspaceRegistry()
    kwargs = _valid_kwargs(auth, workspaces)
    kwargs[field] = "nope"
    with pytest.raises(RequestServiceError):
        GenerationRequestService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    workspaces = WorkspaceRegistry()
    kwargs = _valid_kwargs(auth, workspaces)
    kwargs[field] = "nope"
    with pytest.raises(RequestServiceError):
        GenerationRequestService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, _, service = _fixture()
    assert service.registry is not None
    assert service.dispatch is not None
    assert service.provenance is not None
    assert service.authorization is auth
    assert service.workspaces is not None
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Submission                                                                   #
# --------------------------------------------------------------------------- #


def test_submit_records_owner_and_emits_event():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    ws = _workspace(workspaces, tenant="acme")
    session = _session(auth, subject="arch@x", tenant="acme")
    req = service.submit_request(
        session.session_id, "req", "UCOS-BLPR-abc", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    assert req.owner_subject == "arch@x"
    assert req.status is RequestStatus.SUBMITTED
    assert req.tenant == "acme"
    assert req.blueprint_ref == "UCOS-BLPR-abc"
    assert len(events.events_of(REQUEST_SUBMITTED_EVENT)) == 1


def test_submit_denied_without_create_grant():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces)
    session = _session(auth, role=Role.OPERATOR, subject="op@x")  # no generation-requests grant
    with pytest.raises(RequestAccessError):
        service.submit_request(
            session.session_id, "req", "UCOS-BLPR-abc", ws.workspace_id, BlueprintFamily.DATA, now=1
        )


def test_submit_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces, tenant="beta")
    session = _session(auth, subject="arch@x", tenant="acme")
    with pytest.raises(RequestAccessError):
        service.submit_request(
            session.session_id, "req", "UCOS-BLPR-abc", ws.workspace_id, BlueprintFamily.DATA, now=1
        )


def test_submit_denied_when_workspace_not_active():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces)
    workspaces.transition(ws.workspace_id, WorkspaceStatus.SUSPENDED, tick=0)
    session = _session(auth)
    with pytest.raises(RequestAccessError):
        service.submit_request(
            session.session_id, "req", "UCOS-BLPR-abc", ws.workspace_id, BlueprintFamily.DATA, now=1
        )


def test_submit_unknown_workspace_fail_closed():
    auth, _, service = _fixture()
    session = _session(auth)
    with pytest.raises(WorkspaceRegistryError):
        service.submit_request(
            session.session_id,
            "req",
            "UCOS-BLPR-abc",
            "UCOS-WSPC-missing",
            BlueprintFamily.DATA,
            now=1,
        )


# --------------------------------------------------------------------------- #
# Lifecycle                                                                    #
# --------------------------------------------------------------------------- #


def test_full_lifecycle_to_completed():
    auth, workspaces, service = _fixture()
    session, req = _completed(auth, workspaces, service)
    final = service.get_request(req.request_id)
    assert final.status is RequestStatus.COMPLETED
    assert final.execution_state.value == "succeeded"


def test_fail_branch_from_validating():
    auth, workspaces, service = _fixture()
    session, req = _submitted(auth, workspaces, service)
    service.start_validation(session.session_id, req.request_id, now=2)
    failed = service.fail(session.session_id, req.request_id, now=3)
    assert failed.status is RequestStatus.FAILED


def test_cancel_branch_from_queued():
    auth, workspaces, service = _fixture()
    session, req = _queued(auth, workspaces, service)
    cancelled = service.cancel_request(session.session_id, req.request_id, now=5)
    assert cancelled.status is RequestStatus.CANCELLED


def test_transition_denied_for_non_owner():
    auth, workspaces, service = _fixture()
    session, req = _submitted(auth, workspaces, service, subject="arch@x")
    other = _session(auth, subject="other@x")  # has CREATE, not owner
    with pytest.raises(RequestAccessError):
        service.start_validation(other.session_id, req.request_id, now=2)


def test_mutation_denied_on_terminal_request():
    auth, workspaces, service = _fixture()
    session, req = _queued(auth, workspaces, service)
    service.cancel_request(session.session_id, req.request_id, now=5)
    access = service.evaluate_access(
        session.session_id, req.request_id, RequestAction.VALIDATE, now=6
    )
    assert access.granted is False
    assert access.reason == "request-terminal"


# --------------------------------------------------------------------------- #
# Dispatch (the governed execution boundary, §7)                               #
# --------------------------------------------------------------------------- #


def test_dispatch_records_handoff_and_transitions():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, req = _queued(auth, workspaces, service)
    record = service.dispatch_request(
        session.session_id, req.request_id, now=5, content_hash="c0ffee"
    )
    assert record.dispatch_id.startswith("UCOS-GDSP-")
    assert service.get_request(req.request_id).status is RequestStatus.DISPATCHED
    assert service.dispatch.has(req.request_id)
    assert len(events.events_of(REQUEST_DISPATCHED_EVENT)) == 1


def test_dispatch_accepts_explicit_engine_target():
    auth, workspaces, service = _fixture()
    session, req = _queued(auth, workspaces, service)
    record = service.dispatch_request(
        session.session_id,
        req.request_id,
        now=5,
        content_hash="c0ffee",
        execution_target=FACTORY_CONTRACT,
        parameters={"k": "v"},
    )
    assert record.execution_target == FACTORY_CONTRACT


def test_dispatch_requires_queued_state():
    auth, workspaces, service = _fixture()
    session, req = _submitted(auth, workspaces, service)  # SUBMITTED, not QUEUED
    with pytest.raises(RequestDispatchError):
        service.dispatch_request(session.session_id, req.request_id, now=5, content_hash="c0ffee")


def test_dispatch_denied_for_non_owner():
    auth, workspaces, service = _fixture()
    session, req = _queued(auth, workspaces, service, subject="arch@x")
    other = _session(auth, subject="other@x")
    with pytest.raises(RequestAccessError):
        service.dispatch_request(other.session_id, req.request_id, now=5, content_hash="c0ffee")


def test_no_runtime_bypass_dispatched_requires_record():
    # A request cannot be dispatched without a recorded handoff; the only path that
    # transitions to DISPATCHED (dispatch_request) always records a DispatchRecord.
    auth, workspaces, service = _fixture()
    session, req = _completed(auth, workspaces, service)
    assert service.dispatch.has(req.request_id)
    assert service.health.healthy is True


# --------------------------------------------------------------------------- #
# Provenance / trace                                                           #
# --------------------------------------------------------------------------- #


def test_record_provenance_and_trace():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, req = _completed(auth, workspaces, service)
    recorded = service.record_provenance(
        session.session_id, req.request_id, _provenance(req.request_id), now=8
    )
    assert recorded.is_traceable is True
    assert len(events.events_of(REQUEST_PROVENANCE_LINKED_EVENT)) == 1
    edge = service.trace(session.session_id, req.request_id, now=9)
    assert edge["link"] == "GOV-002-link-4"
    assert edge["traceable"] is True


def test_record_provenance_rejects_bad_type_and_mismatch():
    auth, workspaces, service = _fixture()
    session, req = _completed(auth, workspaces, service)
    with pytest.raises(RequestServiceError):
        service.record_provenance(session.session_id, req.request_id, "nope", now=8)  # type: ignore[arg-type]
    with pytest.raises(RequestServiceError):
        service.record_provenance(
            session.session_id, req.request_id, _provenance("UCOS-GREQ-other"), now=8
        )


def test_trace_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    session, req = _completed(auth, workspaces, service, subject="arch@x", tenant="beta")
    service.record_provenance(
        session.session_id, req.request_id, _provenance(req.request_id), now=8
    )
    intruder = _session(auth, subject="x@x", tenant="acme")
    with pytest.raises(RequestAccessError):
        service.trace(intruder.session_id, req.request_id, now=9)


# --------------------------------------------------------------------------- #
# Retrieval / list / select / status / track                                  #
# --------------------------------------------------------------------------- #


def test_get_request_and_list_and_select():
    auth, workspaces, service = _fixture()
    session, req = _submitted(auth, workspaces, service, tenant="acme")
    assert service.get_request(req.request_id).request_id == req.request_id
    listed = service.list_requests(session.session_id, now=2, tenant="acme")
    assert req.request_id in {r.request_id for r in listed}
    ctx = service.select_request(session.session_id, req.request_id, now=2)
    assert ctx.request_id == req.request_id
    assert ctx.is_owner is True


def test_list_empty_for_invalid_session_and_unauthorized():
    auth, _, service = _fixture()
    assert service.list_requests("UCOS-SESS-missing", now=1) == ()
    op = _session(auth, role=Role.OPERATOR, subject="op@x")
    assert service.list_requests(op.session_id, now=1) == ()


def test_list_filters_by_status():
    auth, workspaces, service = _fixture()
    session, req = _queued(auth, workspaces, service)
    queued = service.list_requests(session.session_id, now=5, status=RequestStatus.QUEUED)
    assert req.request_id in {r.request_id for r in queued}
    submitted = service.list_requests(session.session_id, now=5, status=RequestStatus.SUBMITTED)
    assert req.request_id not in {r.request_id for r in submitted}


def test_select_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    _, req = _submitted(auth, workspaces, service, subject="arch@x", tenant="beta")
    intruder = _session(auth, subject="x@x", tenant="acme")
    with pytest.raises(RequestAccessError):
        service.select_request(intruder.session_id, req.request_id, now=2)


def test_status_of_and_track_request():
    auth, workspaces, service = _fixture()
    session, req = _queued(auth, workspaces, service)
    assert service.status_of(req.request_id).posture.value == "queued"
    tracked = service.track_request(session.session_id, req.request_id, now=5)
    assert tracked.lifecycle_status is RequestStatus.QUEUED


def test_track_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    _, req = _submitted(auth, workspaces, service, subject="arch@x", tenant="beta")
    intruder = _session(auth, subject="x@x", tenant="acme")
    with pytest.raises(RequestAccessError):
        service.track_request(intruder.session_id, req.request_id, now=2)


# --------------------------------------------------------------------------- #
# Metadata / search                                                            #
# --------------------------------------------------------------------------- #


def test_update_metadata_requires_owner_and_validates():
    from platform.generation.metadata import RequestMetadata

    auth, workspaces, service = _fixture()
    session, req = _submitted(auth, workspaces, service)
    updated = service.update_metadata(
        session.session_id, req.request_id, RequestMetadata.create(description="d"), now=2
    )
    assert updated.metadata.description == "d"
    with pytest.raises(RequestServiceError):
        service.update_metadata(session.session_id, req.request_id, "nope", now=3)  # type: ignore[arg-type]


def test_search_delegates():
    auth, workspaces, service = _fixture()
    session, req = _submitted(auth, workspaces, service)
    resp = service.search(session.session_id, "req", now=2)
    assert resp.authorized is True


# --------------------------------------------------------------------------- #
# Access composition                                                           #
# --------------------------------------------------------------------------- #


def test_access_granted_owner_inspect_emits_event():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, req = _submitted(auth, workspaces, service)
    access = service.evaluate_access(
        session.session_id, req.request_id, RequestAction.INSPECT, now=2
    )
    assert access.granted is True
    assert access.is_owner is True
    assert access.access_id.startswith("UCOS-GACC-")
    assert access.to_dict()["granted"] is True
    assert len(events.events_of(REQUEST_ACCESS_EVENT)) == 1


def test_access_denied_authorization_refused():
    auth, workspaces, service = _fixture()
    _, req = _submitted(auth, workspaces, service)
    op = _session(auth, role=Role.OPERATOR, subject="op@x")
    access = service.evaluate_access(op.session_id, req.request_id, RequestAction.VALIDATE, now=2)
    assert access.granted is False
    assert access.reason == "no-grant"


def test_access_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    _, req = _submitted(auth, workspaces, service, subject="arch@x", tenant="beta")
    intruder = _session(auth, subject="x@x", tenant="acme")
    access = service.evaluate_access(
        intruder.session_id, req.request_id, RequestAction.INSPECT, now=2
    )
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_access_denied_not_owner_for_mutation():
    auth, workspaces, service = _fixture()
    _, req = _submitted(auth, workspaces, service, subject="arch@x")
    other = _session(auth, subject="other@x")  # CREATE grant, not owner
    access = service.evaluate_access(
        other.session_id, req.request_id, RequestAction.VALIDATE, now=2
    )
    assert access.granted is False
    assert access.reason == "not-an-owner"


def test_access_administrator_override_for_mutation():
    definitions = [
        d for d in default_role_definitions() if d.role is not Role.PLATFORM_ADMINISTRATOR
    ]
    admin_grants = {
        CapabilityGroup.GENERATION_REQUESTS: RoleGrant(
            group=CapabilityGroup.GENERATION_REQUESTS,
            permissions=frozenset(
                {Permission.CREATE, Permission.READ, Permission.EXECUTE, Permission.ADMINISTER}
            ),
        ),
        CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE: RoleGrant(
            group=CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE,
            permissions=frozenset({Permission.CREATE, Permission.READ, Permission.ADMINISTER}),
        ),
    }
    definitions.append(RoleDefinition(role=Role.PLATFORM_ADMINISTRATOR, grants=admin_grants))
    roles = RoleRegistry()
    roles.register_all(definitions)
    auth = build_authorization_service(roles=roles)
    _, workspaces, service = _fixture(authorization=auth)
    _, req = _submitted(auth, workspaces, service, subject="arch@x")
    admin = _session(auth, role=Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    access = service.evaluate_access(
        admin.session_id, req.request_id, RequestAction.VALIDATE, now=2
    )
    assert access.granted is True
    assert access.is_owner is False


def test_evaluate_access_rejects_bad_action_and_unknown_request():
    auth, workspaces, service = _fixture()
    session, req = _submitted(auth, workspaces, service)
    with pytest.raises(RequestServiceError):
        service.evaluate_access(session.session_id, req.request_id, "inspect", now=2)  # type: ignore[arg-type]
    with pytest.raises(Exception):  # noqa: B017 - registry error for unknown request
        service.evaluate_access(
            session.session_id, "UCOS-GREQ-missing", RequestAction.INSPECT, now=2
        )


# --------------------------------------------------------------------------- #
# Health / evidence / observability                                            #
# --------------------------------------------------------------------------- #


def test_health_report_and_evidence_deterministic():
    def run() -> str:
        auth, workspaces, service = _fixture()
        _completed(auth, workspaces, service)
        return service.evidence().fingerprint()

    assert run() == run()
    auth, workspaces, service = _fixture()
    _completed(auth, workspaces, service)
    report = service.health_report()
    assert report["healthy"] is True
    evidence = service.evidence()
    assert evidence.request_count == 1
    assert evidence.dispatched_count == 1
    assert evidence.terminal_count == 1
    assert evidence.evidence_id.startswith("UCOS-GEVT-")
    assert evidence.health_status in {"healthy", "degraded", "unhealthy"}
    assert evidence.to_dict()["status_census"]["completed"] == 1


def test_health_changed_event_emitted_when_status_changes():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, req = _submitted(auth, workspaces, service)  # healthy baseline
    # Induce a runtime-bypass fault directly on the shared registry the health probe
    # reads: a second request driven to DISPATCHED without a recorded dispatch.
    bp = service.registry.create(
        "req-x", "UCOS-BLPR-a", req.workspace_id, "arch@x", BlueprintFamily.DATA, submitted_tick=5
    )
    service.registry.transition(bp.request_id, RequestStatus.VALIDATING, tick=6)
    service.registry.transition(bp.request_id, RequestStatus.APPROVED, tick=7)
    service.registry.transition(bp.request_id, RequestStatus.QUEUED, tick=8)
    service.registry.transition(bp.request_id, RequestStatus.DISPATCHED, tick=9)
    # A governed terminal transition now re-probes health and emits health.changed.
    service.cancel_request(session.session_id, req.request_id, now=10)
    assert len(events.events_of(REQUEST_HEALTH_CHANGED_EVENT)) == 1


def test_to_dict_and_metrics_with_observability():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, workspaces, service = _fixture(events=events, observability=observability)
    _completed(auth, workspaces, service)
    summary = service.to_dict()
    assert summary["request_count"] == 1
    assert summary["dispatch_count"] == 1
    assert summary["observability_bound"] is True
    assert service.observability is observability
    metrics = observability.metrics
    assert metrics.value_of(METRIC_SUBMITTED, family="data") == 1.0
    assert metrics.value_of(METRIC_DISPATCHED, family="data") == 1.0
    assert metrics.value_of(METRIC_COMPLETED, family="data") == 1.0
    assert metrics.value_of(METRIC_QUEUE_DEPTH) == 0.0
    assert metrics.value_of(METRIC_LIFECYCLE_LATENCY, status="completed") == 6.0
