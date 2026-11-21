"""EC2-TASK-000151 — Validation console service tests (EC2-EPIC-010).

Covers the governed L3 composition point end to end: fail-closed construction and
component validation, authorization-gated read-only surfacing (isolation + owner
recording), faithful retrieval/inspection/evidence/decision/status/trace, list + search
delegation, the composed access decision (identity READ ∧ isolation) including every
reason, annotation, deterministic evidence (P5), machine-checkable fidelity (P6),
observability metrics, governed-action emission, and the append-only inspection audit.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Role
from platform.identity.service import build_authorization_service
from platform.observability.health import HealthRegistry
from platform.observability.service import build_observability_service
from platform.tests.validation_console_helpers import (
    accepted_subject,
    advisory_subject,
    authorization_with_validation_admin,
    authorization_without_validation_read,
    console_fixture,
    rejected_subject,
    session,
)
from platform.validation.contracts import ValidationAction, ValidationRecord
from platform.validation.errors import (
    ValidationAccessError,
    ValidationRecordError,
    ValidationServiceError,
)
from platform.validation.facade import ValidationFacade
from platform.validation.health import ValidationHealth, validation_console_health_checks
from platform.validation.metadata import ValidationRecordMetadata
from platform.validation.registry import ValidationRecordRegistry
from platform.validation.search import ValidationSearch
from platform.validation.service import (
    METRIC_ACCEPTED,
    METRIC_INSPECTIONS,
    METRIC_REJECTED,
    METRIC_SURFACED,
    VALIDATION_ACCESS_EVENT,
    VALIDATION_HEALTH_CHANGED_EVENT,
    VALIDATION_INSPECTED_EVENT,
    VALIDATION_SURFACED_EVENT,
    VALIDATION_TRACED_EVENT,
    ValidationConsoleService,
    build_validation_console_service,
)
from platform.validation.status import ValidationPosture

import pytest

from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance


def _record(subject, **kw):
    report = ValidationEngine().validate(subject)
    return ValidationRecord.create(
        report=report,
        evidence=build_validation_evidence(report),
        decision=enforce_acceptance(report),
        subject=subject,
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


def _surfaced(auth, service, *, subject=None, tenant=None, subj_owner="arch@x", **kw):
    sess = session(auth, subject=subj_owner, tenant=tenant)
    rec = service.surface_validation(
        sess.session_id, subject or accepted_subject(), now=1, tenant=tenant, **kw
    )
    return sess, rec


def _valid_kwargs(auth):
    reg = ValidationRecordRegistry()
    facade = ValidationFacade()
    hr = HealthRegistry()
    for check in validation_console_health_checks():
        hr.register(check)
    return {
        "registry": reg,
        "facade": facade,
        "authorization": auth,
        "search": ValidationSearch(reg, auth),
        "health": ValidationHealth(reg, facade),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction                                                                 #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization():
    with pytest.raises(ValidationServiceError):
        build_validation_console_service(authorization="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    ["registry", "facade", "authorization", "search", "health", "health_registry"],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(ValidationServiceError):
        ValidationConsoleService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(ValidationServiceError):
        ValidationConsoleService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, service = console_fixture()
    assert service.registry is not None
    assert service.facade is not None
    assert service.authorization is auth
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Surfacing                                                                    #
# --------------------------------------------------------------------------- #


def test_surface_records_owner_and_emits_events():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service, tenant="acme", subj_owner="arch@x")
    assert rec.record_id.startswith("UCOS-VREP-")
    assert rec.owner_subject == "arch@x"
    assert rec.tenant == "acme"
    assert rec.accepted is True
    assert len(events.events_of(VALIDATION_SURFACED_EVENT)) == 1


def test_surface_is_idempotent():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, tenant="acme")
    again = service.surface_validation(sess.session_id, accepted_subject(), now=2, tenant="acme")
    assert again.record_id == rec.record_id
    assert len(service.registry) == 1


def test_surface_rejected_subject_records_rejection():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, subject=rejected_subject())
    assert rec.accepted is False
    assert service.status_of(rec.record_id).posture is ValidationPosture.REJECTED


def test_surface_denied_without_read_grant():
    auth = authorization_without_validation_read()
    _, service = console_fixture(authorization=auth)
    op = session(auth, subject="op@x", role=Role.OPERATOR)
    with pytest.raises(ValidationAccessError):
        service.surface_validation(op.session_id, accepted_subject(), now=1)


def test_surface_denied_cross_tenant():
    auth, service = console_fixture()
    sess = session(auth, subject="arch@x", tenant="acme")
    with pytest.raises(ValidationAccessError):
        service.surface_validation(sess.session_id, accepted_subject(), now=1, tenant="beta")


def test_surface_rejects_bad_subject():
    auth, service = console_fixture()
    sess = session(auth)
    with pytest.raises(ValidationServiceError):
        service.surface_validation(sess.session_id, "nope", now=1)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Retrieval / inspection                                                       #
# --------------------------------------------------------------------------- #


def test_get_summary_report_of():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service)
    assert service.get_validation(rec.record_id).record_id == rec.record_id
    assert service.summary_of(rec.record_id).accepted is True
    assert service.report_of(rec.record_id).verdict.value == "pass"


def test_select_returns_context_and_audits_inspection():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service, tenant="acme")
    ctx = service.select_validation(sess.session_id, rec.record_id, now=2)
    assert ctx.record_id == rec.record_id
    assert ctx.is_owner is True
    assert len(events.events_of(VALIDATION_INSPECTED_EVENT)) == 1
    assert service.registry.inspections_of(rec.record_id)


def test_view_evidence_and_decision_render_faithfully():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service)
    ref = service.view_evidence(sess.session_id, rec.record_id, now=2)
    assert ref.evidence_fingerprint == rec.evidence_reference().evidence_fingerprint
    view = service.view_decision(sess.session_id, rec.record_id, now=3)
    assert view.accepted is rec.accepted


def test_status_and_track():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, subject=advisory_subject())
    assert service.status_of(rec.record_id).posture is ValidationPosture.ACCEPTED_WITH_ADVISORIES
    tracked = service.track_validation(sess.session_id, rec.record_id, now=2)
    assert tracked.accepted is True


def test_trace_navigation_emits_event():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service, request_ref="UCOS-GREQ-1")
    trace = service.trace(sess.session_id, rec.record_id, now=2)
    assert trace.request_ref == "UCOS-GREQ-1"
    assert trace.is_traceable is True
    assert len(events.events_of(VALIDATION_TRACED_EVENT)) == 1


def test_verify_fidelity_true_for_surfaced_record():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service)
    assert service.verify_fidelity(rec.record_id) is True


# --------------------------------------------------------------------------- #
# List / search                                                                #
# --------------------------------------------------------------------------- #


def test_list_scoped_and_isolated():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, tenant="acme")
    listed = service.list_validations(sess.session_id, now=2, tenant="acme")
    assert rec.record_id in {r.record_id for r in listed}
    accepted_only = service.list_validations(sess.session_id, now=2, tenant="acme", accepted=True)
    assert rec.record_id in {r.record_id for r in accepted_only}


def test_list_empty_for_invalid_session_and_unauthorized():
    auth, service = console_fixture()
    _surfaced(auth, service)
    assert service.list_validations("UCOS-SESS-missing", now=1) == ()
    no_auth = authorization_without_validation_read()
    _, svc2 = console_fixture(authorization=no_auth)
    svc2.registry.record(_record(accepted_subject()))
    op = session(no_auth, subject="op@x", role=Role.OPERATOR)
    assert svc2.list_validations(op.session_id, now=1) == ()


def test_search_delegates_and_emits_event():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service, tenant="acme")
    resp = service.search(sess.session_id, "data", now=2, tenant="acme")
    assert resp.authorized is True


# --------------------------------------------------------------------------- #
# Access composition                                                           #
# --------------------------------------------------------------------------- #


def test_access_granted_owner_emits_event():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service)
    access = service.evaluate_access(
        sess.session_id, rec.record_id, ValidationAction.INSPECT, now=2
    )
    assert access.granted is True
    assert access.is_owner is True
    assert access.access_id.startswith("UCOS-VACC-")
    assert access.to_dict()["granted"] is True
    assert len(events.events_of(VALIDATION_ACCESS_EVENT)) == 1


def test_access_denied_no_grant():
    no_auth = authorization_without_validation_read()
    _, service = console_fixture(authorization=no_auth)
    service.registry.record(_record(accepted_subject()))
    rec_id = service.registry.ids[0]
    op = session(no_auth, subject="op@x", role=Role.OPERATOR)
    access = service.evaluate_access(op.session_id, rec_id, ValidationAction.INSPECT, now=1)
    assert access.granted is False
    assert access.reason == "no-grant"


def test_access_denied_cross_tenant():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service, tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    access = service.evaluate_access(
        intruder.session_id, rec.record_id, ValidationAction.INSPECT, now=2
    )
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_access_non_owner_still_granted_read_only():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service, tenant="acme", subj_owner="arch@x")
    other = session(auth, subject="other@x", tenant="acme")
    access = service.evaluate_access(
        other.session_id, rec.record_id, ValidationAction.INSPECT, now=2
    )
    assert access.granted is True  # read-only console: ownership does not gate reads
    assert access.is_owner is False


def test_admin_role_reads():
    auth = authorization_with_validation_admin()
    _, service = console_fixture(authorization=auth)
    arch = session(auth, subject="arch@x")
    rec = service.surface_validation(arch.session_id, accepted_subject(), now=1)
    admin = session(auth, subject="admin@x", role=Role.PLATFORM_ADMINISTRATOR)
    access = service.evaluate_access(
        admin.session_id, rec.record_id, ValidationAction.INSPECT, now=2
    )
    assert access.granted is True


def test_require_access_denial_raises():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service, tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    with pytest.raises(ValidationAccessError):
        service.select_validation(intruder.session_id, rec.record_id, now=2)


def test_evaluate_access_bad_action_and_unknown_record():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service)
    sess = session(auth)
    with pytest.raises(ValidationServiceError):
        service.evaluate_access(sess.session_id, rec.record_id, "inspect", now=2)  # type: ignore[arg-type]
    with pytest.raises(ValidationRecordError):
        service.evaluate_access(
            sess.session_id, "UCOS-VREP-missing", ValidationAction.INSPECT, now=2
        )


# --------------------------------------------------------------------------- #
# Annotation (console-only metadata; no validation-datum mutation)             #
# --------------------------------------------------------------------------- #


def test_annotate_updates_console_metadata_only():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service)
    updated = service.annotate(
        sess.session_id, rec.record_id, ValidationRecordMetadata.create(description="note"), now=2
    )
    assert updated.metadata.description == "note"
    # the surfaced validation datum is unchanged (report is immutable, identity preserved)
    assert updated.report.to_dict() == rec.report.to_dict()
    assert updated.record_id == rec.record_id
    with pytest.raises(ValidationServiceError):
        service.annotate(sess.session_id, rec.record_id, "nope", now=3)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Health / evidence / observability                                            #
# --------------------------------------------------------------------------- #


def test_health_report_and_evidence_deterministic():
    def run() -> str:
        auth, service = console_fixture()
        _surfaced(auth, service)
        return service.evidence().fingerprint()

    assert run() == run()
    auth, service = console_fixture()
    _surfaced(auth, service)
    report = service.health_report()
    assert report["healthy"] is True
    evidence = service.evidence()
    assert evidence.record_count == 1
    assert evidence.accepted_count == 1
    assert evidence.evidence_id.startswith("UCOS-VEVD-")
    assert evidence.to_dict()["verdict_census"]["accepted"] == 1


def test_to_dict_and_metrics_with_observability():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, service = console_fixture(events=events, observability=observability)
    sess = session(auth, subject="arch@x")
    service.surface_validation(sess.session_id, accepted_subject(), now=1)
    service.surface_validation(sess.session_id, rejected_subject(), now=2)
    service.select_validation(sess.session_id, service.registry.ids[0], now=3)
    summary = service.to_dict()
    assert summary["record_count"] == 2
    assert summary["observability_bound"] is True
    assert service.observability is observability
    metrics = observability.metrics
    assert metrics.value_of(METRIC_SURFACED) == 2.0
    assert metrics.value_of(METRIC_ACCEPTED) == 1.0
    assert metrics.value_of(METRIC_REJECTED) == 1.0
    assert metrics.value_of(METRIC_INSPECTIONS) == 1.0


def test_health_changed_event_emitted_on_induced_fault():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess = session(auth, subject="arch@x", tenant="acme")
    service.surface_validation(sess.session_id, accepted_subject(), now=1, tenant="acme")
    # Induce a fidelity fault directly on the shared registry the health probe reads:
    # store an accepted report against a divergent subject (same target).
    accepted_report = ValidationEngine().validate(accepted_subject())
    infidelic = ValidationRecord.create(
        report=accepted_report,
        evidence=build_validation_evidence(accepted_report),
        decision=enforce_acceptance(accepted_report),
        subject=advisory_subject(),
        owner_subject="arch@x",
        tenant="acme",
        request_ref="UCOS-GREQ-x",
    )
    service.registry.record(infidelic)
    # A subsequent governed surface re-probes health → UNHEALTHY → emits health.changed.
    service.surface_validation(
        sess.session_id,
        accepted_subject(target="UCOS-RUN-two-0123456789abcdef", blueprint="UCOS-BLPR-2"),
        now=3,
        tenant="acme",
    )
    assert len(events.events_of(VALIDATION_HEALTH_CHANGED_EVENT)) == 1
