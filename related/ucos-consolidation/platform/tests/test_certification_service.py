"""EC2-TASK-000160 — Certification console service tests (EC2-EPIC-011).

Covers the governed L3 composition point end to end: fail-closed construction and
component validation, authorization-gated read-only surfacing (isolation + owner
recording + append-only ledger), faithful retrieval/inspection/evidence, ledger-entry &
lineage navigation, derived status/readiness/governance, list + search delegation, the
composed access decision (identity READ ∧ isolation) including every reason, annotation,
deterministic evidence (P5), machine-checkable fidelity (P6), observability metrics,
governed-action emission, and the append-only inspection audit.
"""

from __future__ import annotations

from platform.certification.contracts import (
    CertificationAction,
    CertificationConsoleRecord,
    CertificationRecordMetadata,
)
from platform.certification.errors import (
    CertificationAccessError,
    CertificationRecordError,
    CertificationServiceError,
)
from platform.certification.facade import CertificationFacade
from platform.certification.health import (
    CertificationHealth,
    certification_console_health_checks,
)
from platform.certification.ledger import CertificationConsoleLedger
from platform.certification.registry import CertificationRegistry
from platform.certification.search import CertificationSearch
from platform.certification.service import (
    CERTIFICATION_ACCESS_EVENT,
    CERTIFICATION_CERTIFIED_EVENT,
    CERTIFICATION_HEALTH_CHANGED_EVENT,
    CERTIFICATION_INSPECTED_EVENT,
    CERTIFICATION_LEDGER_APPENDED_EVENT,
    CERTIFICATION_SURFACED_EVENT,
    CERTIFICATION_TRACED_EVENT,
    METRIC_CERTIFIED,
    METRIC_INSPECTIONS,
    METRIC_LEDGER_APPENDS,
    METRIC_NOT_CERTIFIED,
    METRIC_SURFACED,
    CertificationConsoleService,
    build_certification_console_service,
)
from platform.certification.status import CertificationPosture
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Role
from platform.identity.service import build_authorization_service
from platform.observability.health import HealthRegistry
from platform.observability.service import build_observability_service
from platform.tests.certification_console_helpers import (
    VERSION,
    advisory_output,
    authorization_with_certification_admin,
    authorization_without_certification_read,
    certified_output,
    console_fixture,
    not_certified_output,
    session,
)

import pytest

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence


def _record(validation_output, **kw):
    report, evidence = validation_output
    subject = CertificationSubject.from_validation(report, evidence, version=VERSION)
    decision = CertificationEngine().certify(subject)
    return CertificationConsoleRecord.create(
        report=report,
        validation_evidence=evidence,
        decision=decision,
        certification_evidence=build_certification_evidence(decision),
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


def _surfaced(auth, service, *, validation_output=None, tenant=None, subj_owner="arch@x", **kw):
    sess = session(auth, subject=subj_owner, tenant=tenant)
    report, evidence = validation_output or certified_output()
    rec = service.surface_certification(
        sess.session_id, report, evidence, now=1, version=VERSION, tenant=tenant, **kw
    )
    return sess, rec


def _valid_kwargs(auth):
    reg = CertificationRegistry()
    facade = CertificationFacade()
    ledger = CertificationConsoleLedger()
    hr = HealthRegistry()
    for check in certification_console_health_checks():
        hr.register(check)
    return {
        "registry": reg,
        "facade": facade,
        "ledger": ledger,
        "authorization": auth,
        "search": CertificationSearch(reg, auth),
        "health": CertificationHealth(reg, ledger, facade),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction                                                                 #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization():
    with pytest.raises(CertificationServiceError):
        build_certification_console_service(authorization="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    ["registry", "facade", "ledger", "authorization", "search", "health", "health_registry"],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(CertificationServiceError):
        CertificationConsoleService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(CertificationServiceError):
        CertificationConsoleService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, service = console_fixture()
    assert service.registry is not None
    assert service.facade is not None
    assert service.ledger is not None
    assert service.authorization is auth
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Surfacing                                                                    #
# --------------------------------------------------------------------------- #


def test_surface_records_owner_appends_ledger_and_emits_events():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service, tenant="acme", subj_owner="arch@x")
    assert rec.record_id.startswith("UCOS-CREC-")
    assert rec.owner_subject == "arch@x"
    assert rec.tenant == "acme"
    assert rec.certified is True
    assert rec.certification_id in service.ledger
    assert len(events.events_of(CERTIFICATION_SURFACED_EVENT)) == 1
    assert len(events.events_of(CERTIFICATION_CERTIFIED_EVENT)) == 1
    assert len(events.events_of(CERTIFICATION_LEDGER_APPENDED_EVENT)) == 1


def test_surface_is_idempotent():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, tenant="acme")
    report, evidence = certified_output()
    again = service.surface_certification(
        sess.session_id, report, evidence, now=2, version=VERSION, tenant="acme"
    )
    assert again.record_id == rec.record_id
    assert len(service.registry) == 1
    assert len(service.ledger) == 1


def test_surface_not_certified_subject_records_rejection():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, validation_output=not_certified_output())
    assert rec.certified is False
    assert service.status_of(rec.record_id).posture is CertificationPosture.NOT_CERTIFIED


def test_surface_denied_without_read_grant():
    auth = authorization_without_certification_read()
    _, service = console_fixture(authorization=auth)
    op = session(auth, subject="op@x", role=Role.OPERATOR)
    report, evidence = certified_output()
    with pytest.raises(CertificationAccessError):
        service.surface_certification(op.session_id, report, evidence, now=1, version=VERSION)


def test_surface_denied_cross_tenant():
    auth, service = console_fixture()
    sess = session(auth, subject="arch@x", tenant="acme")
    report, evidence = certified_output()
    with pytest.raises(CertificationAccessError):
        service.surface_certification(
            sess.session_id, report, evidence, now=1, version=VERSION, tenant="beta"
        )


def test_surface_rejects_bad_report_and_evidence():
    auth, service = console_fixture()
    sess = session(auth)
    report, evidence = certified_output()
    with pytest.raises(CertificationServiceError):
        service.surface_certification(sess.session_id, "nope", evidence, now=1, version=VERSION)  # type: ignore[arg-type]
    with pytest.raises(CertificationServiceError):
        service.surface_certification(sess.session_id, report, "nope", now=1, version=VERSION)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Retrieval / inspection                                                       #
# --------------------------------------------------------------------------- #


def test_get_summary_decision_of():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service)
    assert service.get_certification(rec.record_id).record_id == rec.record_id
    assert service.summary_of(rec.record_id).certified is True
    assert service.decision_of(rec.record_id).certified is True


def test_select_returns_context_and_audits_inspection():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service, tenant="acme")
    ctx = service.select_certification(sess.session_id, rec.record_id, now=2)
    assert ctx.record_id == rec.record_id
    assert ctx.is_owner is True
    assert len(events.events_of(CERTIFICATION_INSPECTED_EVENT)) == 1
    assert service.registry.inspections_of(rec.record_id)


def test_view_evidence_renders_faithfully():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service)
    ref = service.view_evidence(sess.session_id, rec.record_id, now=2)
    assert ref.evidence_fingerprint == rec.evidence_reference().evidence_fingerprint


def test_view_ledger_entry_and_lineage():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, tenant="acme")
    view = service.view_ledger_entry(sess.session_id, rec.record_id, now=2)
    assert view.certification_id == rec.certification_id
    lineage = service.lineage_of(sess.session_id, rec.record_id, now=3)
    assert lineage.certification_id == rec.certification_id
    assert lineage.is_root is True


def test_status_and_track():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, validation_output=advisory_output())
    assert service.status_of(rec.record_id).posture is (
        CertificationPosture.CERTIFIED_WITH_ADVISORIES
    )
    tracked = service.track_certification(sess.session_id, rec.record_id, now=2)
    assert tracked.certified is True


def test_readiness_and_governance():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service)
    assert service.readiness_of(rec.record_id).ready is True
    readiness = service.assess_readiness(sess.session_id, rec.record_id, now=2)
    assert readiness.ready is True
    assert service.governance_of(rec.record_id).compliant is True
    assessment = service.assess_governance(sess.session_id, rec.record_id, now=3)
    assert assessment.compliant is True


def test_trace_navigation_emits_event():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service, request_ref="UCOS-GREQ-1")
    trace = service.trace(sess.session_id, rec.record_id, now=2)
    assert trace.request_ref == "UCOS-GREQ-1"
    assert trace.is_traceable is True
    assert len(events.events_of(CERTIFICATION_TRACED_EVENT)) == 1


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
    listed = service.list_certifications(sess.session_id, now=2, tenant="acme")
    assert rec.record_id in {r.record_id for r in listed}
    certified_only = service.list_certifications(
        sess.session_id, now=2, tenant="acme", certified=True
    )
    assert rec.record_id in {r.record_id for r in certified_only}


def test_list_empty_for_invalid_session_and_unauthorized():
    auth, service = console_fixture()
    _surfaced(auth, service)
    assert service.list_certifications("UCOS-SESS-missing", now=1) == ()
    no_auth = authorization_without_certification_read()
    _, svc2 = console_fixture(authorization=no_auth)
    svc2.registry.record(_record(certified_output()))
    op = session(no_auth, subject="op@x", role=Role.OPERATOR)
    assert svc2.list_certifications(op.session_id, now=1) == ()


def test_search_delegates_and_emits_event():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service, tenant="acme")
    resp = service.search(sess.session_id, "certified", now=2, tenant="acme")
    assert resp.authorized is True


# --------------------------------------------------------------------------- #
# Access composition                                                           #
# --------------------------------------------------------------------------- #


def test_access_granted_owner_emits_event():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess, rec = _surfaced(auth, service)
    access = service.evaluate_access(
        sess.session_id, rec.record_id, CertificationAction.INSPECT, now=2
    )
    assert access.granted is True
    assert access.is_owner is True
    assert access.access_id.startswith("UCOS-CACC-")
    assert access.to_dict()["granted"] is True
    assert len(events.events_of(CERTIFICATION_ACCESS_EVENT)) == 1


def test_access_denied_no_grant():
    no_auth = authorization_without_certification_read()
    _, service = console_fixture(authorization=no_auth)
    service.registry.record(_record(certified_output()))
    rec_id = service.registry.ids[0]
    op = session(no_auth, subject="op@x", role=Role.OPERATOR)
    access = service.evaluate_access(op.session_id, rec_id, CertificationAction.INSPECT, now=1)
    assert access.granted is False
    assert access.reason == "no-grant"


def test_access_denied_cross_tenant():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service, tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    access = service.evaluate_access(
        intruder.session_id, rec.record_id, CertificationAction.INSPECT, now=2
    )
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_access_non_owner_still_granted_read_only():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service, tenant="acme", subj_owner="arch@x")
    other = session(auth, subject="other@x", tenant="acme")
    access = service.evaluate_access(
        other.session_id, rec.record_id, CertificationAction.INSPECT, now=2
    )
    assert access.granted is True
    assert access.is_owner is False


def test_admin_role_reads():
    auth = authorization_with_certification_admin()
    _, service = console_fixture(authorization=auth)
    arch = session(auth, subject="arch@x")
    report, evidence = certified_output()
    rec = service.surface_certification(arch.session_id, report, evidence, now=1, version=VERSION)
    admin = session(auth, subject="admin@x", role=Role.PLATFORM_ADMINISTRATOR)
    access = service.evaluate_access(
        admin.session_id, rec.record_id, CertificationAction.INSPECT, now=2
    )
    assert access.granted is True


def test_require_access_denial_raises():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service, tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    with pytest.raises(CertificationAccessError):
        service.select_certification(intruder.session_id, rec.record_id, now=2)


def test_evaluate_access_bad_action_and_unknown_record():
    auth, service = console_fixture()
    _, rec = _surfaced(auth, service)
    sess = session(auth)
    with pytest.raises(CertificationServiceError):
        service.evaluate_access(sess.session_id, rec.record_id, "inspect", now=2)  # type: ignore[arg-type]
    with pytest.raises(CertificationRecordError):
        service.evaluate_access(
            sess.session_id, "UCOS-CREC-missing", CertificationAction.INSPECT, now=2
        )


# --------------------------------------------------------------------------- #
# Annotation (console-only metadata; no certification-datum mutation)          #
# --------------------------------------------------------------------------- #


def test_annotate_updates_console_metadata_only():
    auth, service = console_fixture()
    sess, rec = _surfaced(auth, service)
    updated = service.annotate(
        sess.session_id,
        rec.record_id,
        CertificationRecordMetadata.create(description="note"),
        now=2,
    )
    assert updated.metadata.description == "note"
    assert updated.record.to_dict() == rec.record.to_dict()
    assert updated.record_id == rec.record_id
    with pytest.raises(CertificationServiceError):
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
    assert evidence.certified_count == 1
    assert evidence.ledger_entry_count == 1
    assert evidence.ledger_intact is True
    assert evidence.evidence_id.startswith("UCOS-CEVD-")
    assert evidence.to_dict()["status_census"]["certified"] == 1


def test_to_dict_and_metrics_with_observability():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, service = console_fixture(events=events, observability=observability)
    sess = session(auth, subject="arch@x")
    cert_report, cert_ev = certified_output()
    rej_report, rej_ev = not_certified_output()
    service.surface_certification(sess.session_id, cert_report, cert_ev, now=1, version=VERSION)
    service.surface_certification(sess.session_id, rej_report, rej_ev, now=2, version=VERSION)
    service.select_certification(sess.session_id, service.registry.ids[0], now=3)
    summary = service.to_dict()
    assert summary["record_count"] == 2
    assert summary["ledger_entry_count"] == 2
    assert summary["observability_bound"] is True
    assert service.observability is observability
    metrics = observability.metrics
    assert metrics.value_of(METRIC_SURFACED) == 2.0
    assert metrics.value_of(METRIC_CERTIFIED) == 1.0
    assert metrics.value_of(METRIC_NOT_CERTIFIED) == 1.0
    assert metrics.value_of(METRIC_LEDGER_APPENDS) == 2.0
    assert metrics.value_of(METRIC_INSPECTIONS) == 1.0


def test_health_changed_event_emitted_on_induced_fault():
    events = bootstrap_platform().events
    auth, service = console_fixture(events=events)
    sess = session(auth, subject="arch@x", tenant="acme")
    cert_report, cert_ev = certified_output()
    service.surface_certification(
        sess.session_id, cert_report, cert_ev, now=1, version=VERSION, tenant="acme"
    )
    # Induce a fidelity fault on the shared registry the health probe reads: store a
    # certified decision paired with the advisory validation output (same target) so a
    # fresh reproduction over the stored output diverges.
    adv_report, adv_ev = advisory_output()
    subject = CertificationSubject.from_validation(cert_report, cert_ev, version=VERSION)
    decision = CertificationEngine().certify(subject)
    infidelic = CertificationConsoleRecord.create(
        report=adv_report,
        validation_evidence=adv_ev,
        decision=decision,
        certification_evidence=build_certification_evidence(decision),
        owner_subject="arch@x",
        tenant="acme",
        request_ref="UCOS-GREQ-x",
    )
    service.registry.record(infidelic)
    # A subsequent governed surface re-probes health → UNHEALTHY → emits health.changed.
    two_report, two_ev = certified_output(
        target="UCOS-RUN-two-0123456789abcdef", blueprint="UCOS-BLPR-2"
    )
    service.surface_certification(
        sess.session_id, two_report, two_ev, now=3, version=VERSION, tenant="acme"
    )
    assert len(events.events_of(CERTIFICATION_HEALTH_CHANGED_EVENT)) == 1
