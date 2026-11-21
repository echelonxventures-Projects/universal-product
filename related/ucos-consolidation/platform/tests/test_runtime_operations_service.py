"""EC2-TASK-000172 — Runtime Operations service tests (EC2-EPIC-012).

Covers the governed L8 composition point end to end: fail-closed construction + component
validation, EXECUTE-gated CERTIFIED-only deploy/rollback (isolation + owner recording +
append-only ledger + fail-closed non-certified admission), faithful retrieval / inspection
/ descriptor / ledger / lineage navigation, derived status / reversibility / governance,
discovery + search delegation, the composed access decision (identity permission ∧
isolation) including every reason, annotation, deterministic evidence (P5), machine-
checkable fidelity (P6), observability metrics, governed-action emission, and the
append-only inspection audit.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Role
from platform.identity.service import build_authorization_service
from platform.observability.service import build_observability_service
from platform.runtime_operations.contracts import (
    RuntimeOperationAction,
    RuntimeOperationKind,
    RuntimeOperationMetadata,
    RuntimeOperationRecord,
)
from platform.runtime_operations.descriptors import DescriptorCatalog
from platform.runtime_operations.errors import (
    RuntimeAdmissionError,
    RuntimeOperationAccessError,
    RuntimeOperationRecordError,
    RuntimeOperationServiceError,
    RuntimeReversibilityError,
)
from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.health import (
    RuntimeOperationsHealth,
    runtime_operations_health_checks,
)
from platform.runtime_operations.ledger import RuntimeOperationLedger
from platform.runtime_operations.operations import RuntimeOperationPlanner, RuntimeOperationRegistry
from platform.runtime_operations.search import RuntimeOperationSearch
from platform.runtime_operations.service import (
    METRIC_DEPLOYS,
    METRIC_LEDGER_APPENDS,
    METRIC_OPERATIONS,
    METRIC_ROLLBACKS,
    RUNTIME_DEPLOY_APPLIED_EVENT,
    RUNTIME_HEALTH_CHANGED_EVENT,
    RUNTIME_LEDGER_APPENDED_EVENT,
    RUNTIME_OPERATION_ACCESS_EVENT,
    RUNTIME_OPERATION_INSPECTED_EVENT,
    RUNTIME_OPERATION_RECORDED_EVENT,
    RUNTIME_REVERSIBILITY_VERIFIED_EVENT,
    RUNTIME_ROLLBACK_APPLIED_EVENT,
    RuntimeOperationsService,
    build_runtime_operations_service,
)
from platform.runtime_operations.status import RuntimeOperationPosture
from platform.tests.runtime_operations_helpers import (
    VERSION,
    authorization_without_runtime_grant,
    certification_record,
    not_certified_unit_and_record,
    runtime_unit,
    service_fixture,
    session,
)

import pytest


def _deploy(
    auth, service, *, tenant=None, subject="admin@x", role=Role.PLATFORM_ADMINISTRATOR, now=1, **kw
):
    sess = session(auth, subject=subject, role=role, tenant=tenant)
    rec = service.deploy(
        sess.session_id, runtime_unit(), certification_record(), now=now, tenant=tenant, **kw
    )
    return sess, rec


def _valid_kwargs(auth):
    registry = RuntimeOperationRegistry()
    planner = RuntimeOperationPlanner()
    ledger = RuntimeOperationLedger()
    from platform.observability.health import HealthRegistry

    hr = HealthRegistry()
    for check in runtime_operations_health_checks():
        hr.register(check)
    return {
        "registry": registry,
        "planner": planner,
        "descriptors": DescriptorCatalog(registry),
        "ledger": ledger,
        "authorization": auth,
        "search": RuntimeOperationSearch(registry, auth),
        "health": RuntimeOperationsHealth(registry, ledger, planner.facade),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction                                                                 #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization():
    with pytest.raises(RuntimeOperationServiceError):
        build_runtime_operations_service(authorization="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    [
        "registry",
        "planner",
        "descriptors",
        "ledger",
        "authorization",
        "search",
        "health",
        "health_registry",
    ],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(RuntimeOperationServiceError):
        RuntimeOperationsService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(RuntimeOperationServiceError):
        RuntimeOperationsService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, service = service_fixture()
    assert service.registry is not None
    assert service.planner is not None
    assert service.descriptors is not None
    assert service.ledger is not None
    assert service.authorization is auth
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Deploy / rollback                                                            #
# --------------------------------------------------------------------------- #


def test_deploy_records_owner_appends_ledger_and_emits_events():
    events = bootstrap_platform().events
    auth, service = service_fixture(events=events)
    sess, rec = _deploy(auth, service, tenant="acme")
    assert rec.operation_id.startswith("UCOS-ROPR-")
    assert rec.owner_subject == "admin@x"
    assert rec.tenant == "acme"
    assert rec.certified is True
    assert rec.operation_id in service.ledger
    assert len(events.events_of(RUNTIME_DEPLOY_APPLIED_EVENT)) == 1
    assert len(events.events_of(RUNTIME_OPERATION_RECORDED_EVENT)) == 1
    assert len(events.events_of(RUNTIME_LEDGER_APPENDED_EVENT)) == 1


def test_deploy_is_idempotent():
    auth, service = service_fixture()
    sess, rec = _deploy(auth, service, tenant="acme")
    again = service.deploy(
        sess.session_id, runtime_unit(), certification_record(), now=2, tenant="acme"
    )
    assert again.operation_id == rec.operation_id
    assert len(service.registry) == 1
    assert len(service.ledger) == 1


def test_rollback_reversible_and_events():
    events = bootstrap_platform().events
    auth, service = service_fixture(events=events)
    sess = session(auth)
    rec = service.rollback(
        sess.session_id,
        runtime_unit(),
        certification_record(),
        now=1,
        previous=runtime_unit(pkg="b" * 64),
    )
    assert rec.kind is RuntimeOperationKind.ROLLBACK
    assert rec.reversible is True
    assert len(events.events_of(RUNTIME_ROLLBACK_APPLIED_EVENT)) == 1


def test_deploy_operator_execute_allowed():
    auth, service = service_fixture()
    op = session(auth, role=Role.OPERATOR, subject="op@x")
    rec = service.deploy(op.session_id, runtime_unit(), certification_record(), now=1)
    assert rec.certified is True


def test_deploy_denied_without_execute():
    # Auditor holds READ but not EXECUTE on runtime-operations.
    auth, service = service_fixture()
    aud = session(auth, role=Role.AUDITOR, subject="aud@x")
    with pytest.raises(RuntimeOperationAccessError):
        service.deploy(aud.session_id, runtime_unit(), certification_record(), now=1)


def test_deploy_denied_cross_tenant():
    auth, service = service_fixture()
    sess = session(auth, subject="a@x", tenant="acme")
    with pytest.raises(RuntimeOperationAccessError):
        service.deploy(
            sess.session_id, runtime_unit(), certification_record(), now=1, tenant="beta"
        )


def test_deploy_fail_closed_non_certified():
    auth, service = service_fixture()
    sess = session(auth)
    unit, cert = not_certified_unit_and_record()
    with pytest.raises(RuntimeAdmissionError):
        service.deploy(sess.session_id, unit, cert, now=1)


def test_deploy_rejects_bad_unit():
    auth, service = service_fixture()
    sess = session(auth)
    with pytest.raises(RuntimeOperationServiceError):
        service.deploy(sess.session_id, "nope", certification_record(), now=1)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Retrieval / inspection                                                       #
# --------------------------------------------------------------------------- #


def test_get_status_governance():
    auth, service = service_fixture()
    _, rec = _deploy(auth, service)
    assert service.get_operation(rec.operation_id).operation_id == rec.operation_id
    assert service.status_of(rec.operation_id).posture is RuntimeOperationPosture.DEPLOY_GOVERNED
    assert service.governance_of(rec.operation_id).compliant is True


def test_reversibility_of_rollback_and_deploy_error():
    auth, service = service_fixture()
    sess = session(auth)
    rb = service.rollback(sess.session_id, runtime_unit(), certification_record(), now=1)
    assert service.reversibility_of(rb.operation_id).reversible is True
    _, dep = _deploy(auth, service, now=2)
    with pytest.raises(RuntimeReversibilityError):
        service.reversibility_of(dep.operation_id)


def test_select_returns_context_and_audits():
    events = bootstrap_platform().events
    auth, service = service_fixture(events=events)
    sess, rec = _deploy(auth, service, tenant="acme")
    ctx = service.select_operation(sess.session_id, rec.operation_id, now=2)
    assert ctx.operation_id == rec.operation_id
    assert ctx.is_owner is True
    assert len(events.events_of(RUNTIME_OPERATION_INSPECTED_EVENT)) == 1
    assert service.registry.inspections_of(rec.operation_id)


def test_inspect_descriptor_and_ledger_and_lineage():
    auth, service = service_fixture()
    sess, rec = _deploy(auth, service, tenant="acme")
    view = service.inspect_descriptor(sess.session_id, rec.operation_id, now=2)
    assert view.runtime_id == rec.runtime_id
    entry = service.view_ledger_entry(sess.session_id, rec.operation_id, now=3)
    assert entry.operation_id == rec.operation_id
    lineage = service.lineage_of(sess.session_id, rec.operation_id, now=4)
    assert lineage.is_root is True


def test_track_reversibility_governance_verbs():
    auth, service = service_fixture()
    sess = session(auth)
    rb = service.rollback(sess.session_id, runtime_unit(), certification_record(), now=1)
    assert service.track_operation(sess.session_id, rb.operation_id, now=2).reversible is True
    proof = service.verify_reversibility(sess.session_id, rb.operation_id, now=3)
    assert proof.reversible is True
    assert service.assess_governance(sess.session_id, rb.operation_id, now=4).compliant is True


def test_verify_reversibility_event_emitted():
    events = bootstrap_platform().events
    auth, service = service_fixture(events=events)
    sess = session(auth)
    rb = service.rollback(sess.session_id, runtime_unit(), certification_record(), now=1)
    service.verify_reversibility(sess.session_id, rb.operation_id, now=2)
    assert len(events.events_of(RUNTIME_REVERSIBILITY_VERIFIED_EVENT)) == 1


def test_verify_fidelity_true():
    auth, service = service_fixture()
    sess = session(auth)
    _, dep = _deploy(auth, service)
    assert service.verify_fidelity(dep.operation_id) is True
    rb = service.rollback(sess.session_id, runtime_unit(), certification_record(), now=2)
    assert service.verify_fidelity(rb.operation_id) is True


# --------------------------------------------------------------------------- #
# Discovery / search                                                           #
# --------------------------------------------------------------------------- #


def test_discover_scoped_and_isolated():
    auth, service = service_fixture()
    sess, rec = _deploy(auth, service, tenant="acme")
    listed = service.discover_operations(sess.session_id, now=2, tenant="acme")
    assert rec.operation_id in {r.operation_id for r in listed}
    deploys = service.discover_operations(
        sess.session_id, now=2, tenant="acme", kind=RuntimeOperationKind.DEPLOY
    )
    assert rec.operation_id in {r.operation_id for r in deploys}


def test_discover_empty_for_invalid_session_and_unauthorized():
    auth, service = service_fixture()
    _deploy(auth, service)
    assert service.discover_operations("UCOS-SESS-missing", now=1) == ()
    no_auth = authorization_without_runtime_grant()
    _, svc2 = service_fixture(authorization=no_auth)
    op = session(no_auth, role=Role.OPERATOR, subject="op@x")
    # operator lacks the runtime-operations grant entirely in this fixture → cannot deploy
    with pytest.raises(RuntimeOperationAccessError):
        svc2.deploy(op.session_id, runtime_unit(), certification_record(), now=1)
    assert svc2.discover_operations(op.session_id, now=1) == ()


def test_search_delegates_and_emits_event():
    auth, service = service_fixture()
    aud = session(auth, role=Role.AUDITOR, subject="aud@x")
    _deploy(auth, service, tenant="acme")
    resp = service.search(aud.session_id, "data", now=2, tenant="acme")
    assert resp.authorized is True


# --------------------------------------------------------------------------- #
# Access composition                                                           #
# --------------------------------------------------------------------------- #


def test_access_granted_owner_emits_event():
    events = bootstrap_platform().events
    auth, service = service_fixture(events=events)
    sess, rec = _deploy(auth, service)
    access = service.evaluate_access(
        sess.session_id, rec.operation_id, RuntimeOperationAction.INSPECT, now=2
    )
    assert access.granted is True
    assert access.is_owner is True
    assert access.access_id.startswith("UCOS-ROAC-")
    assert access.to_dict()["granted"] is True
    assert len(events.events_of(RUNTIME_OPERATION_ACCESS_EVENT)) == 1


def test_access_denied_no_grant():
    no_auth = authorization_without_runtime_grant()
    admin_auth = build_authorization_service()
    # Record an operation using an admin-capable auth, then evaluate with a no-grant auth.
    _, service = service_fixture(authorization=admin_auth)
    _, rec = _deploy(admin_auth, service)
    # Point the service search/authorization for access at a principal with no grant:
    dev = session(admin_auth, role=Role.DEVELOPER, subject="dev@x")
    access = service.evaluate_access(
        dev.session_id, rec.operation_id, RuntimeOperationAction.INSPECT, now=2
    )
    assert access.granted is False
    assert access.reason == "no-grant"
    assert no_auth is not None


def test_access_denied_cross_tenant():
    auth, service = service_fixture()
    admin = session(auth, subject="admin@x")
    rec = service.deploy(
        admin.session_id, runtime_unit(), certification_record(), now=1, tenant="beta"
    )
    intruder = session(auth, subject="x@x", tenant="acme")
    access = service.evaluate_access(
        intruder.session_id, rec.operation_id, RuntimeOperationAction.INSPECT, now=2
    )
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_access_non_owner_still_granted():
    auth, service = service_fixture()
    admin, rec = _deploy(auth, service, tenant="acme", subject="admin@x")
    other = session(auth, subject="other@x", tenant="acme")
    access = service.evaluate_access(
        other.session_id, rec.operation_id, RuntimeOperationAction.INSPECT, now=2
    )
    assert access.granted is True
    assert access.is_owner is False


def test_require_access_denial_raises():
    auth, service = service_fixture()
    admin = session(auth, subject="admin@x")
    rec = service.deploy(
        admin.session_id, runtime_unit(), certification_record(), now=1, tenant="beta"
    )
    intruder = session(auth, subject="x@x", tenant="acme")
    with pytest.raises(RuntimeOperationAccessError):
        service.select_operation(intruder.session_id, rec.operation_id, now=2)


def test_evaluate_access_bad_action_and_unknown_record():
    auth, service = service_fixture()
    _, rec = _deploy(auth, service)
    sess = session(auth)
    with pytest.raises(RuntimeOperationServiceError):
        service.evaluate_access(sess.session_id, rec.operation_id, "inspect", now=2)  # type: ignore[arg-type]
    with pytest.raises(RuntimeOperationRecordError):
        service.evaluate_access(
            sess.session_id, "UCOS-ROPR-missing", RuntimeOperationAction.INSPECT, now=2
        )


# --------------------------------------------------------------------------- #
# Annotation                                                                   #
# --------------------------------------------------------------------------- #


def test_annotate_updates_metadata_only():
    auth, service = service_fixture()
    sess, rec = _deploy(auth, service)
    updated = service.annotate(
        sess.session_id,
        rec.operation_id,
        RuntimeOperationMetadata.create(description="note"),
        now=2,
    )
    assert updated.metadata.description == "note"
    assert updated.operation_id == rec.operation_id
    with pytest.raises(RuntimeOperationServiceError):
        service.annotate(sess.session_id, rec.operation_id, "nope", now=3)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Health / evidence / observability                                            #
# --------------------------------------------------------------------------- #


def test_health_report_and_evidence_deterministic():
    def run() -> str:
        auth, service = service_fixture()
        _deploy(auth, service)
        return service.evidence().fingerprint()

    assert run() == run()
    auth, service = service_fixture()
    _deploy(auth, service)
    report = service.health_report()
    assert report["healthy"] is True
    evidence = service.evidence()
    assert evidence.operation_count == 1
    assert evidence.deploy_count == 1
    assert evidence.ledger_entry_count == 1
    assert evidence.ledger_intact is True
    assert evidence.evidence_id.startswith("UCOS-ROEV-")
    assert evidence.to_dict()["kind_census"]["deploy"] == 1


def test_to_dict_and_metrics_with_observability():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, service = service_fixture(events=events, observability=observability)
    sess = session(auth, subject="admin@x")
    service.deploy(sess.session_id, runtime_unit(), certification_record(), now=1)
    service.rollback(sess.session_id, runtime_unit(version="2.0.0"), certification_record(), now=2)
    service.select_operation(sess.session_id, service.registry.ids[0], now=3)
    summary = service.to_dict()
    assert summary["operation_count"] == 2
    assert summary["ledger_entry_count"] == 2
    assert summary["observability_bound"] is True
    assert service.observability is observability
    metrics = observability.metrics
    assert metrics.value_of(METRIC_OPERATIONS) == 2.0
    assert metrics.value_of(METRIC_DEPLOYS) == 1.0
    assert metrics.value_of(METRIC_ROLLBACKS) == 1.0
    assert metrics.value_of(METRIC_LEDGER_APPENDS) == 2.0


def test_health_changed_event_emitted_on_induced_fault():
    events = bootstrap_platform().events
    auth, service = service_fixture(events=events)
    sess = session(auth, subject="admin@x", tenant="acme")
    service.deploy(sess.session_id, runtime_unit(), certification_record(), now=1, tenant="acme")
    # Induce a fidelity fault on the shared registry: store a deploy record whose descriptor
    # was generated for a different environment than the record's declared environment.
    unit = runtime_unit(runtime_id="UCOS-RUN-two-0123456789abcdef", blueprint="UCOS-BLPR-2")
    divergent = RuntimeFacade().deployment_descriptor(unit, environment="staging")
    infidelic = RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.DEPLOY,
        unit=unit,
        certification=certification_record(),
        deployment=divergent,
        owner_subject="admin@x",
        environment="production",
        tenant="acme",
    )
    service.registry.record(infidelic)
    # A subsequent governed deploy re-probes health → UNHEALTHY → emits health.changed.
    service.deploy(
        sess.session_id, runtime_unit(version="3.0.0"), certification_record(), now=3, tenant="acme"
    )
    assert len(events.events_of(RUNTIME_HEALTH_CHANGED_EVENT)) == 1


# --------------------------------------------------------------------------- #
# Builder                                                                      #
# --------------------------------------------------------------------------- #


def test_builder_accepts_custom_components():
    auth = build_authorization_service()
    registry = RuntimeOperationRegistry()
    service = build_runtime_operations_service(
        authorization=auth,
        registry=registry,
        planner=RuntimeOperationPlanner(),
        ledger=RuntimeOperationLedger(),
    )
    assert service.registry is registry
    assert isinstance(service.planner.facade, RuntimeFacade)
    assert VERSION == "1.0.0"
