"""EC2-TASK-000133 — Artifact Explorer service tests (EC2-EPIC-009).

Covers the governed L3 read-only composition point end to end: fail-closed construction
and component validation, the pure substrate projections, artifact lookup, request-to
-artifact navigation, discovery, lineage/provenance/trace navigation, search delegation,
the composed access decision (identity READ ∧ tenant isolation with owner/administrator
standings) including every denial reason, read-only integrity health refresh, deterministic
evidence, observability metrics, and governed-action emission (append-only audit).
"""

from __future__ import annotations

from platform.artifact_explorer.contracts import ExplorerAction
from platform.artifact_explorer.errors import (
    ArtifactAccessError,
    ArtifactProvenanceError,
    ArtifactServiceError,
)
from platform.artifact_explorer.health import ExplorerHealth
from platform.artifact_explorer.search import ArtifactSearch
from platform.artifact_explorer.service import (
    ARTIFACT_ACCESS_EVENT,
    ARTIFACT_DISCOVERED_EVENT,
    ARTIFACT_HEALTH_CHANGED_EVENT,
    ARTIFACT_LINEAGE_NAVIGATED_EVENT,
    ARTIFACT_NAVIGATED_EVENT,
    ARTIFACT_PROVENANCE_NAVIGATED_EVENT,
    ARTIFACT_SEARCHED_EVENT,
    ARTIFACT_TRACE_NAVIGATED_EVENT,
    ARTIFACT_VIEWED_EVENT,
    METRIC_DISCOVERIES,
    METRIC_LINEAGE,
    METRIC_LOOKUPS,
    METRIC_PROVENANCE,
    METRIC_SEARCHES,
    METRIC_TRACE,
    ArtifactExplorerService,
    build_artifact_explorer_service,
)
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Role
from platform.generation.contracts import RequestStatus
from platform.generation.dispatch import DispatchLedger, DispatchRecord
from platform.generation.provenance import ProvenanceLedger
from platform.generation.registry import GenerationRequestRegistry
from platform.identity.service import build_authorization_service
from platform.observability.service import build_observability_service
from platform.tests.artifact_explorer_helpers import (
    admin_auth,
    drive_to_queued,
    explorer,
    make_request,
    no_grant_auth,
    seeded_artifact,
    session,
)

import pytest


def _valid_kwargs(auth):
    reg = GenerationRequestRegistry()
    disp = DispatchLedger()
    prov = ProvenanceLedger()
    from platform.artifact_explorer.health import artifact_explorer_health_checks
    from platform.observability.health import HealthRegistry

    hr = HealthRegistry()
    for check in artifact_explorer_health_checks():
        hr.register(check)
    return {
        "registry": reg,
        "dispatch": disp,
        "provenance": prov,
        "authorization": auth,
        "search": ArtifactSearch(reg, disp, prov, auth),
        "health": ExplorerHealth(reg, disp, prov),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction                                                                 #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization():
    with pytest.raises(ArtifactServiceError):
        build_artifact_explorer_service(authorization="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    ["registry", "dispatch", "provenance", "authorization", "search", "health", "health_registry"],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(ArtifactServiceError):
        ArtifactExplorerService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(ArtifactServiceError):
        ArtifactExplorerService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, registry, dispatch, provenance, service = explorer()
    assert service.registry is registry
    assert service.dispatch is dispatch
    assert service.provenance is provenance
    assert service.authorization is auth
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Pure substrate projections (no authorization)                                #
# --------------------------------------------------------------------------- #


def test_pure_projections_reference_summary_view_status():
    auth, registry, dispatch, provenance, service = explorer()
    req = seeded_artifact(registry, dispatch, provenance)
    assert service.reference_of(req.request_id).generation_artifact_id == "BP-DATA-0001"
    assert service.summary_of(req.request_id).is_traceable is True
    assert service.view_of(req.request_id).is_traceable is True
    assert service.status_of(req.request_id).is_traceable is True


# --------------------------------------------------------------------------- #
# Artifact lookup                                                              #
# --------------------------------------------------------------------------- #


def test_get_artifact_returns_view_and_emits_event():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    req = seeded_artifact(registry, dispatch, provenance)
    sess = session(auth)
    view = service.get_artifact(sess.session_id, req.request_id, now=1)
    assert view.request_ref == req.request_id
    assert view.is_traceable is True
    assert len(events.events_of(ARTIFACT_VIEWED_EVENT)) == 1


def test_get_artifact_denied_without_grant():
    auth = no_grant_auth()
    _, registry, dispatch, provenance, service = explorer(authorization=auth)
    req = make_request(registry)
    sess = session(auth, role=Role.OPERATOR, subject="op@x")
    with pytest.raises(ArtifactAccessError):
        service.get_artifact(sess.session_id, req.request_id, now=1)


def test_get_artifact_denied_cross_tenant():
    auth, registry, dispatch, provenance, service = explorer()
    req = make_request(registry, tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    with pytest.raises(ArtifactAccessError):
        service.get_artifact(intruder.session_id, req.request_id, now=1)


# --------------------------------------------------------------------------- #
# Request-to-artifact navigation                                              #
# --------------------------------------------------------------------------- #


def test_navigate_from_request_binds_context():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    req = seeded_artifact(registry, dispatch, provenance, owner="arch@x")
    sess = session(auth, subject="arch@x")
    ctx = service.navigate_from_request(sess.session_id, req.request_id, now=1)
    assert ctx.request_ref == req.request_id
    assert ctx.is_owner is True
    assert len(events.events_of(ARTIFACT_NAVIGATED_EVENT)) == 1


# --------------------------------------------------------------------------- #
# Discovery                                                                    #
# --------------------------------------------------------------------------- #


def test_discover_lists_authorized_artifacts():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    req = make_request(registry, tenant="acme")
    sess = session(auth, tenant="acme")
    summaries = service.discover_artifacts(sess.session_id, now=1, tenant="acme")
    assert req.request_id in {s.request_ref for s in summaries}
    assert len(events.events_of(ARTIFACT_DISCOVERED_EVENT)) == 1


def test_discover_filters_by_status_and_family():
    auth, registry, dispatch, provenance, service = explorer()
    req = make_request(registry)
    drive_to_queued(registry, req)
    sess = session(auth)
    queued = service.discover_artifacts(sess.session_id, now=1, status=RequestStatus.QUEUED)
    assert req.request_id in {s.request_ref for s in queued}
    submitted = service.discover_artifacts(sess.session_id, now=1, status=RequestStatus.SUBMITTED)
    assert req.request_id not in {s.request_ref for s in submitted}
    data = service.discover_artifacts(sess.session_id, now=1, family=BlueprintFamily.DATA)
    assert req.request_id in {s.request_ref for s in data}


def test_discover_empty_for_invalid_session_and_unauthorized():
    auth, registry, dispatch, provenance, service = explorer()
    make_request(registry)
    assert service.discover_artifacts("UCOS-SESS-missing", now=1) == ()
    ng = no_grant_auth()
    _, registry2, _, _, service2 = explorer(authorization=ng)
    make_request(registry2)
    op = session(ng, role=Role.OPERATOR, subject="op@x")
    assert service2.discover_artifacts(op.session_id, now=1) == ()


def test_discover_excludes_cross_tenant():
    auth, registry, dispatch, provenance, service = explorer()
    make_request(registry, slug="secret", tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    assert service.discover_artifacts(intruder.session_id, now=1) == ()


# --------------------------------------------------------------------------- #
# Lineage / provenance / trace navigation                                      #
# --------------------------------------------------------------------------- #


def test_lineage_navigation():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    req = seeded_artifact(registry, dispatch, provenance)
    sess = session(auth)
    lineage = service.lineage(sess.session_id, req.request_id, now=1)
    assert lineage.is_complete is True
    assert len(events.events_of(ARTIFACT_LINEAGE_NAVIGATED_EVENT)) == 1


def test_provenance_navigation_and_absent_fail_closed():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    req = seeded_artifact(registry, dispatch, provenance)
    sess = session(auth)
    projection = service.artifact_provenance(sess.session_id, req.request_id, now=1)
    assert projection.provenance_id == provenance.get(req.request_id).provenance_id
    assert len(events.events_of(ARTIFACT_PROVENANCE_NAVIGATED_EVENT)) == 1
    # An artifact with no provenance fails closed.
    bare = make_request(registry, slug="bare")
    with pytest.raises(ArtifactProvenanceError):
        service.artifact_provenance(sess.session_id, bare.request_id, now=2)


def test_trace_navigation():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    req = seeded_artifact(registry, dispatch, provenance)
    sess = session(auth)
    trace = service.trace(sess.session_id, req.request_id, now=1)
    assert trace.is_traceable is True
    assert len(events.events_of(ARTIFACT_TRACE_NAVIGATED_EVENT)) == 1


# --------------------------------------------------------------------------- #
# Search delegation                                                            #
# --------------------------------------------------------------------------- #


def test_search_delegates_and_emits_event():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    make_request(registry, slug="alpha-data")
    sess = session(auth)
    resp = service.search(sess.session_id, "alpha", now=1)
    assert resp.authorized is True
    assert len(events.events_of(ARTIFACT_SEARCHED_EVENT)) == 1


# --------------------------------------------------------------------------- #
# Access composition                                                           #
# --------------------------------------------------------------------------- #


def test_access_granted_owner_emits_event():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    req = make_request(registry, owner="arch@x")
    sess = session(auth, subject="arch@x")
    access = service.evaluate_access(sess.session_id, req.request_id, ExplorerAction.LOOKUP, now=1)
    assert access.granted is True
    assert access.is_owner is True
    assert access.is_administrator is False
    assert access.access_id.startswith("UCOS-AXAC-")
    assert access.to_dict()["granted"] is True
    assert len(events.events_of(ARTIFACT_ACCESS_EVENT)) == 1


def test_access_granted_non_owner_tenant_reader():
    auth, registry, dispatch, provenance, service = explorer()
    req = make_request(registry, owner="arch@x", tenant="acme")
    other = session(auth, subject="other@x", tenant="acme")
    access = service.evaluate_access(other.session_id, req.request_id, ExplorerAction.LOOKUP, now=1)
    assert access.granted is True  # tenant access (read-only) — not owner
    assert access.is_owner is False


def test_access_administrator_standing():
    auth = admin_auth()
    _, registry, dispatch, provenance, service = explorer(authorization=auth)
    req = make_request(registry, owner="arch@x")
    admin = session(auth, role=Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    access = service.evaluate_access(admin.session_id, req.request_id, ExplorerAction.LOOKUP, now=1)
    assert access.granted is True
    assert access.is_owner is False
    assert access.is_administrator is True


def test_access_denied_authorization_refused():
    auth = no_grant_auth()
    _, registry, dispatch, provenance, service = explorer(authorization=auth)
    req = make_request(registry)
    op = session(auth, role=Role.OPERATOR, subject="op@x")
    access = service.evaluate_access(op.session_id, req.request_id, ExplorerAction.LOOKUP, now=1)
    assert access.granted is False
    assert access.reason == "no-grant"


def test_access_denied_cross_tenant():
    auth, registry, dispatch, provenance, service = explorer()
    req = make_request(registry, tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    access = service.evaluate_access(
        intruder.session_id, req.request_id, ExplorerAction.LOOKUP, now=1
    )
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_evaluate_access_rejects_bad_action_and_unknown_request():
    auth, registry, dispatch, provenance, service = explorer()
    req = make_request(registry)
    sess = session(auth)
    with pytest.raises(ArtifactServiceError):
        service.evaluate_access(sess.session_id, req.request_id, "lookup", now=1)  # type: ignore[arg-type]
    with pytest.raises(Exception):  # noqa: B017 - registry error for unknown request
        service.evaluate_access(sess.session_id, "UCOS-GREQ-missing", ExplorerAction.LOOKUP, now=1)


# --------------------------------------------------------------------------- #
# Health / evidence / observability                                            #
# --------------------------------------------------------------------------- #


def test_health_report_and_refresh_health_no_change():
    auth, registry, dispatch, provenance, service = explorer()
    seeded_artifact(registry, dispatch, provenance)
    report = service.health_report()
    assert report["healthy"] is True
    assert service.refresh_health() == "healthy"  # no transition → no event needed


def test_refresh_health_emits_on_transition():
    events = bootstrap_platform().events
    auth, registry, dispatch, provenance, service = explorer(events=events)
    # Induce an integrity fault: a dispatch referencing an unregistered request.
    dispatch.record(
        DispatchRecord.create(
            request_ref="UCOS-GREQ-orphan",
            blueprint_ref="UCOS-BLPR-1",
            family=BlueprintFamily.DATA,
            content_hash="c0ffee",
            tick=5,
        )
    )
    status = service.refresh_health()
    assert status == "unhealthy"
    assert len(events.events_of(ARTIFACT_HEALTH_CHANGED_EVENT)) == 1


def test_evidence_is_deterministic_and_counts_navigations():
    def run() -> str:
        auth, registry, dispatch, provenance, service = explorer()
        req = seeded_artifact(registry, dispatch, provenance)
        sess = session(auth)
        service.get_artifact(sess.session_id, req.request_id, now=1)
        service.lineage(sess.session_id, req.request_id, now=2)
        service.artifact_provenance(sess.session_id, req.request_id, now=3)
        service.trace(sess.session_id, req.request_id, now=4)
        return service.evidence().fingerprint()

    assert run() == run()
    auth, registry, dispatch, provenance, service = explorer()
    req = seeded_artifact(registry, dispatch, provenance)
    sess = session(auth)
    service.get_artifact(sess.session_id, req.request_id, now=1)
    evidence = service.evidence()
    assert evidence.artifact_count == 1
    assert evidence.dispatched_count == 1
    assert evidence.provenance_count == 1
    assert evidence.traceable_count == 1
    assert evidence.lookup_count == 1
    assert evidence.evidence_id.startswith("UCOS-AXEV-")
    assert evidence.health_status in {"healthy", "degraded", "unhealthy"}


def test_to_dict_and_metrics_with_observability():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, registry, dispatch, provenance, service = explorer(
        events=events, observability=observability
    )
    req = seeded_artifact(registry, dispatch, provenance)
    sess = session(auth)
    service.get_artifact(sess.session_id, req.request_id, now=1)
    service.discover_artifacts(sess.session_id, now=2)
    service.lineage(sess.session_id, req.request_id, now=3)
    service.artifact_provenance(sess.session_id, req.request_id, now=4)
    service.trace(sess.session_id, req.request_id, now=5)
    service.search(sess.session_id, "artifact", now=6)
    summary = service.to_dict()
    assert summary["artifact_count"] == 1
    assert summary["observability_bound"] is True
    assert service.observability is observability
    metrics = observability.metrics
    assert metrics.value_of(METRIC_LOOKUPS, family="data") == 1.0
    assert metrics.value_of(METRIC_DISCOVERIES) == 1.0
    assert metrics.value_of(METRIC_LINEAGE) == 1.0
    assert metrics.value_of(METRIC_PROVENANCE) == 1.0
    assert metrics.value_of(METRIC_TRACE) == 1.0
    assert metrics.value_of(METRIC_SEARCHES) == 1.0
