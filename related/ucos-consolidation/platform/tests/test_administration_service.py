"""EC2-CAP-ADMIN-001 — Administration service tests.

Covers the governed administration composition point end to end: fail-closed
construction and component validation, the composed access decision (identity ∧ tenant
isolation) including every denial reason, administrative context entry, operational
configuration, membership administration (tenant/workspace/platform), operational
lifecycle management, authorization-scoped search, health integration, deterministic
evidence (P5), administrative audit/activity tracking, and governed-action emission
(PC-16). Cross-tenant administration is denied; unauthorized administration is denied.
"""

from __future__ import annotations

from platform.administration.audit import AdministrativeAuditLog
from platform.administration.configuration import AdministrativeConfiguration
from platform.administration.contracts import (
    AdministrativeAction,
    AdministrativeDomain,
    AdministrativeScope,
    AdministrativeTarget,
    OperationalState,
)
from platform.administration.errors import (
    AdministrationAccessError,
    AdministrationServiceError,
)
from platform.administration.health import AdministrationHealth, administration_health_checks
from platform.administration.membership import AdministrativeMembershipRegistry
from platform.administration.search import AdministrativeSearch
from platform.administration.service import (
    ADMIN_ACCESS_EVENT,
    ADMIN_CONFIG_EVENT,
    ADMIN_CONTEXT_EVENT,
    ADMIN_LIFECYCLE_EVENT,
    ADMIN_MEMBER_ASSIGNED_EVENT,
    ADMIN_MEMBER_REVOKED_EVENT,
    AdministrationService,
    build_administration_service,
)
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.observability.health import HealthRegistry
from platform.observability.service import build_observability_service

import pytest

# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _service(*, events=None, observability=None):
    auth = build_authorization_service(events=events)
    service = build_administration_service(
        authorization=auth, observability=observability, events=events
    )
    return auth, service


def _session(auth, role: Role, subject: str = "u@x", tenant: str | None = None):
    principal = Principal.create(subject, [role], tenant=tenant)
    return auth.establish_session(principal, issued_at=0, ttl=1000)


def _valid_kwargs(auth):
    config = AdministrativeConfiguration()
    members = AdministrativeMembershipRegistry()
    hr = HealthRegistry()
    for check in administration_health_checks():
        hr.register(check)
    return {
        "configuration": config,
        "membership": members,
        "authorization": auth,
        "audit": AdministrativeAuditLog(),
        "search": AdministrativeSearch(config, members, auth),
        "health": AdministrationHealth(config, members),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction / composition                                                   #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization_service():
    with pytest.raises(AdministrationServiceError):
        build_administration_service(authorization="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    [
        "configuration",
        "membership",
        "authorization",
        "audit",
        "search",
        "health",
        "health_registry",
    ],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(AdministrationServiceError):
        AdministrationService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(AdministrationServiceError):
        AdministrationService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, service = _service()
    assert service.configuration is not None
    assert service.membership is not None
    assert service.authorization is auth
    assert service.audit is not None
    assert service.permissions is not None
    assert service.roles is not None
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Access evaluation (identity ∧ tenant isolation)                             #
# --------------------------------------------------------------------------- #


def _target(
    scope=AdministrativeScope.PLATFORM,
    domain=AdministrativeDomain.CONFIGURATION,
    identifier="platform",
    tenant=None,
):
    return AdministrativeTarget.create(scope, domain, identifier, tenant=tenant)


def _ev(service, session, action, target=None, *, now=1):
    return service.evaluate_access(
        session.session_id, action, target if target is not None else _target(), now=now
    )


def test_access_granted_for_platform_administrator():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    access = _ev(service, session, AdministrativeAction.CONFIGURE)
    assert access.granted is True
    assert access.reason == "granted"
    assert AdministrativeAction.CONFIGURE in access.actions
    assert access.access_id.startswith("UCOS-AACC-")
    assert access.to_dict()["granted"] is True
    assert service.access_evaluation_count == 1


def test_access_denied_for_unauthorized_role():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    access = _ev(service, session, AdministrativeAction.INSPECT)
    assert access.granted is False
    assert access.reason == "no-grant"
    assert access.actions == frozenset()


def test_access_denied_for_auditor_mutation_read_only():
    auth, service = _service()
    session = _session(auth, Role.AUDITOR, subject="aud@x")
    access = _ev(service, session, AdministrativeAction.CONFIGURE)
    assert access.granted is False
    assert access.reason == "read-only-role-no-mutation"


def test_access_granted_for_auditor_inspect():
    auth, service = _service()
    session = _session(auth, Role.AUDITOR, subject="aud@x")
    access = _ev(service, session, AdministrativeAction.INSPECT)
    assert access.granted is True


def test_access_denied_cross_tenant():
    auth, service = _service()
    # A tenant-bound administrator administering a *different* tenant is isolated.
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x", tenant="acme")
    target = _target(AdministrativeScope.TENANT, AdministrativeDomain.TENANT, "beta", tenant="beta")
    access = _ev(service, session, AdministrativeAction.CONFIGURE, target)
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_access_denied_for_invalid_session():
    _, service = _service()
    access = service.evaluate_access(
        "UCOS-SESS-missing", AdministrativeAction.INSPECT, _target(), now=1
    )
    assert access.granted is False
    assert access.reason == "session-absent"
    assert access.principal_id == "anonymous"


def test_evaluate_access_rejects_bad_action():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR)
    with pytest.raises(AdministrationServiceError):
        service.evaluate_access(session.session_id, "configure", _target(), now=1)  # type: ignore[arg-type]


def test_evaluate_access_rejects_bad_target():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR)
    with pytest.raises(AdministrationServiceError):
        service.evaluate_access(session.session_id, AdministrativeAction.INSPECT, "nope", now=1)  # type: ignore[arg-type]


def test_access_evaluation_is_recorded_and_emitted():
    events = bootstrap_platform().events
    auth, service = _service(events=events)
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.evaluate_access(session.session_id, AdministrativeAction.INSPECT, _target(), now=1)
    assert len(events.events_of(ADMIN_ACCESS_EVENT)) == 1
    assert len(service.audit) == 1
    assert service.audit.events[0].action is AdministrativeAction.INSPECT


# --------------------------------------------------------------------------- #
# Context entry                                                                #
# --------------------------------------------------------------------------- #


def test_enter_returns_context_for_administrator():
    events = bootstrap_platform().events
    auth, service = _service(events=events)
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    ctx = service.enter(session.session_id, AdministrativeScope.PLATFORM, now=1)
    assert ctx.scope is AdministrativeScope.PLATFORM
    assert ctx.can_administer is True
    assert ctx.context_id.startswith("UCOS-ACTX-")
    assert len(events.events_of(ADMIN_CONTEXT_EVENT)) == 1


def test_enter_returns_inspect_only_context_for_auditor():
    auth, service = _service()
    session = _session(auth, Role.AUDITOR, subject="aud@x")
    ctx = service.enter(session.session_id, AdministrativeScope.PLATFORM, now=1)
    assert ctx.can_administer is False
    assert ctx.permits(AdministrativeAction.INSPECT)


def test_enter_denied_for_unauthorized_role():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    with pytest.raises(AdministrationAccessError):
        service.enter(session.session_id, AdministrativeScope.PLATFORM, now=1)


def test_enter_rejects_bad_scope():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR)
    with pytest.raises(AdministrationServiceError):
        service.enter(session.session_id, "platform", now=1)  # type: ignore[arg-type]


def test_enter_tenant_scope_uses_tenant_identifier():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    ctx = service.enter(session.session_id, AdministrativeScope.TENANT, now=1, tenant="acme")
    assert ctx.tenant == "acme"


# --------------------------------------------------------------------------- #
# Configuration                                                                #
# --------------------------------------------------------------------------- #


def test_administrator_sets_gets_and_removes_configuration():
    events = bootstrap_platform().events
    auth, service = _service(events=events)
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    sid = session.session_id
    setting = service.set_configuration(sid, AdministrativeScope.PLATFORM, "flag", "on", now=1)
    assert setting.value == "on"
    fetched = service.get_configuration(sid, AdministrativeScope.PLATFORM, "flag", now=2)
    assert fetched.value == "on"
    removed = service.remove_configuration(sid, AdministrativeScope.PLATFORM, "flag", now=3)
    assert removed.key == "flag"
    assert len(events.events_of(ADMIN_CONFIG_EVENT)) == 2  # set + remove


def test_set_configuration_denied_for_auditor():
    auth, service = _service()
    session = _session(auth, Role.AUDITOR, subject="aud@x")
    with pytest.raises(AdministrationAccessError):
        service.set_configuration(
            session.session_id, AdministrativeScope.PLATFORM, "flag", "on", now=1
        )


def test_auditor_may_read_configuration_set_by_admin():
    auth, service = _service()
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.set_configuration(admin.session_id, AdministrativeScope.PLATFORM, "flag", "on", now=1)
    aud = _session(auth, Role.AUDITOR, subject="aud@x")
    fetched = service.get_configuration(aud.session_id, AdministrativeScope.PLATFORM, "flag", now=2)
    assert fetched.value == "on"


def test_remove_configuration_denied_for_unauthorized():
    auth, service = _service()
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.set_configuration(admin.session_id, AdministrativeScope.PLATFORM, "flag", "on", now=1)
    dev = _session(auth, Role.DEVELOPER, subject="dev@x")
    with pytest.raises(AdministrationAccessError):
        service.remove_configuration(dev.session_id, AdministrativeScope.PLATFORM, "flag", now=2)


# --------------------------------------------------------------------------- #
# Membership administration                                                    #
# --------------------------------------------------------------------------- #


def test_administrator_assigns_and_revokes_admins_with_events():
    events = bootstrap_platform().events
    auth, service = _service(events=events)
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    member = service.assign_administrator(
        session.session_id,
        AdministrativeScope.TENANT,
        "acme",
        "UCOS-PRIN-x",
        "x@x",
        now=1,
        tenant="acme",
    )
    assert member.principal_id == "UCOS-PRIN-x"
    revoked = service.revoke_administrator(
        session.session_id, AdministrativeScope.TENANT, "acme", "UCOS-PRIN-x", now=2, tenant="acme"
    )
    assert revoked.principal_id == "UCOS-PRIN-x"
    assert len(events.events_of(ADMIN_MEMBER_ASSIGNED_EVENT)) == 1
    assert len(events.events_of(ADMIN_MEMBER_REVOKED_EVENT)) == 1


def test_assign_administrator_denied_cross_tenant():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x", tenant="acme")
    with pytest.raises(AdministrationAccessError):
        service.assign_administrator(
            session.session_id,
            AdministrativeScope.TENANT,
            "beta",
            "UCOS-PRIN-x",
            "x@x",
            now=1,
            tenant="beta",
        )


def test_assign_administrator_denied_for_unauthorized_role():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    with pytest.raises(AdministrationAccessError):
        service.assign_administrator(
            session.session_id,
            AdministrativeScope.PLATFORM,
            "platform",
            "UCOS-PRIN-x",
            "x@x",
            now=1,
        )


def test_revoke_administrator_denied_for_unauthorized_role():
    auth, service = _service()
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.assign_administrator(
        admin.session_id, AdministrativeScope.PLATFORM, "platform", "UCOS-PRIN-x", "x@x", now=1
    )
    aud = _session(auth, Role.AUDITOR, subject="aud@x")
    with pytest.raises(AdministrationAccessError):
        service.revoke_administrator(
            aud.session_id, AdministrativeScope.PLATFORM, "platform", "UCOS-PRIN-x", now=2
        )


# --------------------------------------------------------------------------- #
# Operational lifecycle management                                             #
# --------------------------------------------------------------------------- #


def test_administrator_sets_and_reads_operational_state():
    events = bootstrap_platform().events
    auth, service = _service(events=events)
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    state = service.set_operational_state(
        session.session_id,
        AdministrativeScope.TENANT,
        "acme",
        OperationalState.SUSPENDED,
        now=1,
        tenant="acme",
    )
    assert state is OperationalState.SUSPENDED
    read = service.operational_state(
        session.session_id, AdministrativeScope.TENANT, "acme", now=2, tenant="acme"
    )
    assert read is OperationalState.SUSPENDED
    assert len(events.events_of(ADMIN_LIFECYCLE_EVENT)) == 1


def test_activation_uses_activate_action_and_reads_none_when_absent():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.set_operational_state(
        session.session_id, AdministrativeScope.PLATFORM, "platform", OperationalState.ACTIVE, now=1
    )
    # An absent resource reads as None (authorized inspect, no stored state).
    assert (
        service.operational_state(session.session_id, AdministrativeScope.PLATFORM, "other", now=2)
        is None
    )


def test_set_operational_state_rejects_bad_state():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR)
    with pytest.raises(AdministrationServiceError):
        service.set_operational_state(
            session.session_id,
            AdministrativeScope.PLATFORM,
            "platform",
            "suspended",
            now=1,  # type: ignore[arg-type]
        )


def test_set_operational_state_denied_for_auditor():
    auth, service = _service()
    session = _session(auth, Role.AUDITOR, subject="aud@x")
    with pytest.raises(AdministrationAccessError):
        service.set_operational_state(
            session.session_id,
            AdministrativeScope.PLATFORM,
            "platform",
            OperationalState.SUSPENDED,
            now=1,
        )


# --------------------------------------------------------------------------- #
# Search / health / evidence / summary                                         #
# --------------------------------------------------------------------------- #


def test_search_delegates_to_administrative_search():
    auth, service = _service()
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.set_configuration(
        admin.session_id, AdministrativeScope.PLATFORM, "retention", "long", now=1
    )
    response = service.search(admin.session_id, "retention", now=2)
    assert response.authorized is True
    assert any(h.kind == "setting" for h in response.results)


def test_health_report_uses_observability_model():
    _, service = _service()
    report = service.health_report()
    assert report["healthy"] is True


def test_evidence_is_deterministic_and_serializable():
    def run() -> str:
        auth, service = _service()
        session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
        service.set_configuration(session.session_id, AdministrativeScope.PLATFORM, "k", "v", now=1)
        service.assign_administrator(
            session.session_id,
            AdministrativeScope.PLATFORM,
            "platform",
            "UCOS-PRIN-x",
            "x@x",
            now=2,
        )
        return service.evidence().fingerprint()

    assert run() == run()


def test_evidence_reports_counts_and_health():
    auth, service = _service()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.set_configuration(session.session_id, AdministrativeScope.PLATFORM, "k", "v", now=1)
    evidence = service.evidence()
    assert evidence.setting_count == 1
    assert evidence.evidence_id.startswith("UCOS-ADEV-")
    assert evidence.to_dict()["health_status"] in {"healthy", "degraded", "unhealthy"}


def test_to_dict_summary_reports_observability_binding():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, service = _service(events=events, observability=observability)
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.set_configuration(session.session_id, AdministrativeScope.PLATFORM, "k", "v", now=1)
    summary = service.to_dict()
    assert summary["setting_count"] == 1
    assert summary["observability_bound"] is True
    assert service.observability is observability
