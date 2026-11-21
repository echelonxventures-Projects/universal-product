"""EC2-TASK-000080 — Portal service (shell) tests.

Covers the epic's headline acceptance criteria end to end: an authenticated portal is
reachable (fail-closed admission), navigation reaches all authorized surfaces,
routing authorizes each surface, the workspace handoff and global search work,
observability visibility is integrated, portal evidence is deterministic, contracts
are published on bootstrap, and every portal entry is captured as a governed action
(PC-16). Also exercises authorization boundaries and failure handling.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck
from platform.observability.service import build_observability_service
from platform.portal.errors import (
    PortalAccessError,
    PortalServiceError,
    RoutingError,
    ServiceDiscoveryError,
)
from platform.portal.service import (
    PORTAL_BOOTSTRAP_EVENT,
    PORTAL_ENTERED_EVENT,
    PortalService,
    bootstrap_portal,
    build_portal_service,
)

import pytest


def _platform_portal():
    context = bootstrap_platform()
    service = bootstrap_portal(context)
    return context, service


def _service_with_health_probe():
    """A portal wired over an observability layer carrying a registered health check."""
    context = bootstrap_platform()
    observability = build_observability_service(events=context.events)
    observability.register_health_check(HealthCheck("portal", critical=True))
    authorization = build_authorization_service(events=context.events)
    service = build_portal_service(
        authorization=authorization,
        observability=observability,
        events=context.events,
        services=context.services,
        capabilities=context.capabilities,
    )
    return context, service


def _session(service, role: Role, subject: str = "u@ucos", tenant: str | None = None):
    principal = Principal.create(subject, [role], tenant=tenant)
    return service.gateway.establish_session(principal, issued_at=0, ttl=1000)


# --------------------------------------------------------------------------- #
# Bootstrap / composition                                                     #
# --------------------------------------------------------------------------- #


def test_bootstrap_publishes_contracts_and_emits_event():
    context = bootstrap_platform()
    bootstrap_portal(context)
    assert "portal.shell.entry" in context.services
    assert "portal.search.query" in context.services
    assert len(context.events.events_of(PORTAL_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_is_idempotent_on_contracts():
    context = bootstrap_platform()
    authorization = build_authorization_service(events=context.events)
    bootstrap_portal(context, authorization=authorization)
    before = len(context.services)
    bootstrap_portal(context, authorization=authorization)
    assert len(context.services) == before


def test_build_portal_service_requires_authorization():
    with pytest.raises(PortalServiceError):
        build_portal_service(authorization="nope")  # type: ignore[arg-type]


def test_service_rejects_invalid_components():
    with pytest.raises(PortalServiceError):
        PortalService(
            gateway="nope",  # type: ignore[arg-type]
            navigation=None,  # type: ignore[arg-type]
            router=None,  # type: ignore[arg-type]
            workspace=None,  # type: ignore[arg-type]
            search=None,  # type: ignore[arg-type]
        )


def _valid_components():
    from platform.portal.access import PortalAccessGateway
    from platform.portal.navigation import NavigationModel
    from platform.portal.routing import Router
    from platform.portal.search import GlobalSearch, default_search_index
    from platform.portal.workspace import WorkspaceSelector

    gateway = PortalAccessGateway(build_authorization_service())
    return {
        "gateway": gateway,
        "navigation": NavigationModel(),
        "router": Router(),
        "workspace": WorkspaceSelector(gateway),
        "search": GlobalSearch(default_search_index(), gateway),
    }


@pytest.mark.parametrize(
    "field",
    ["navigation", "router", "workspace", "search"],
)
def test_service_rejects_each_invalid_component(field):
    kwargs = _valid_components()
    kwargs[field] = "nope"
    with pytest.raises(PortalServiceError):
        PortalService(**kwargs)  # type: ignore[arg-type]


def test_service_rejects_invalid_optional_components():
    base = _valid_components()
    with pytest.raises(PortalServiceError):
        PortalService(**base, directory="nope")  # type: ignore[arg-type]
    with pytest.raises(PortalServiceError):
        PortalService(**base, observability_view="nope")  # type: ignore[arg-type]
    with pytest.raises(PortalServiceError):
        PortalService(**base, events="nope")  # type: ignore[arg-type]


def test_service_property_getters():
    from platform.portal.search import GlobalSearch
    from platform.portal.workspace import WorkspaceSelector

    service = PortalService(**_valid_components())
    assert isinstance(service.workspace, WorkspaceSelector)
    assert isinstance(service.search_engine, GlobalSearch)
    assert service.observability is None


def test_enter_without_event_bus_emits_nothing():
    service = PortalService(**_valid_components())  # no events bus bound
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    view = service.enter(session.session_id, now=1)
    assert view.principal_id.startswith("UCOS-PRIN-")
    assert service.entry_count == 1


def test_view_and_navigation_result_serialize():
    _, service = _platform_portal()
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    view = service.enter(session.session_id, now=1)
    view_dict = view.to_dict()
    assert view_dict["landing_path"] == "/"
    assert "navigation" in view_dict and "accessibility" in view_dict
    result = service.navigate(session.session_id, "/generation-requests", now=1)
    result_dict = result.to_dict()
    assert result_dict["authorized"] is True
    assert result_dict["route"]["path"] == "/generation-requests"


# --------------------------------------------------------------------------- #
# Shell entry (authenticated portal reachable)                                #
# --------------------------------------------------------------------------- #


def test_admin_enters_portal_with_full_navigation():
    _, service = _platform_portal()
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    view = service.enter(session.session_id, now=1)
    assert view.view_id.startswith("UCOS-PVEW-")
    assert len(view.navigation.items) == 16
    assert view.landing_path == "/"
    assert view.accessibility.passed is True


def test_developer_enters_with_reduced_navigation():
    _, service = _platform_portal()
    session = _session(service, Role.DEVELOPER)
    view = service.enter(session.session_id, now=1)
    paths = set(view.navigation.paths)
    assert "/" in paths  # portal-navigation readable
    assert "/user-role-quota-admin" not in paths  # admin surface hidden


def test_integrator_cannot_enter_portal():
    _, service = _platform_portal()
    session = _session(service, Role.INTEGRATOR)
    with pytest.raises(PortalAccessError):
        service.enter(session.session_id, now=1)


def test_entry_is_observed_as_governed_action():
    context, service = _platform_portal()
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    service.enter(session.session_id, now=1)
    assert len(context.events.events_of(PORTAL_ENTERED_EVENT)) == 1
    assert service.entry_count == 1


# --------------------------------------------------------------------------- #
# Routing (navigation to authorized surfaces)                                 #
# --------------------------------------------------------------------------- #


def test_navigate_authorized_surface():
    _, service = _platform_portal()
    session = _session(service, Role.DEVELOPER)
    result = service.navigate(session.session_id, "/generation-requests", now=1)
    assert result.authorized is True


def test_navigate_denied_surface_is_data_not_exception():
    _, service = _platform_portal()
    session = _session(service, Role.DEVELOPER)
    result = service.navigate(session.session_id, "/user-role-quota-admin", now=1)
    assert result.authorized is False
    assert result.reason == "no-grant"


def test_navigate_unknown_path_is_fail_closed():
    _, service = _platform_portal()
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    with pytest.raises(RoutingError):
        service.navigate(session.session_id, "/nope", now=1)


# --------------------------------------------------------------------------- #
# Workspace / search / discovery / observability                              #
# --------------------------------------------------------------------------- #


def test_select_workspace_handoff():
    _, service = _platform_portal()
    session = _session(service, Role.DEVELOPER)
    handoff = service.select_workspace(session.session_id, "ws-1", now=1)
    assert handoff.authorized is True
    assert handoff.landing_path == "/workspace-project-lifecycle"


def test_search_spans_multiple_entities():
    _, service = _platform_portal()
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    response = service.search(session.session_id, "workspace blueprint artifact project", now=1)
    assert len(response.kinds_present) >= 4


def test_discover_services_returns_directory():
    _, service = _platform_portal()
    directory = service.discover_services()
    assert "portal.shell.entry" in directory.service_names


def test_discover_services_without_directory_is_fail_closed():
    service = build_portal_service(authorization=build_authorization_service())
    with pytest.raises(PortalServiceError):
        service.discover_services()


def test_observability_views_through_shell():
    _, service = _service_with_health_probe()
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    assert service.health(session.session_id, {"portal": HealthStatus.HEALTHY}, now=1)["healthy"]
    assert "governed_action_count" in service.runtime(session.session_id, now=1)
    assert "series" in service.monitoring(session.session_id, now=1)


def test_observability_views_require_bound_layer():
    service = build_portal_service(authorization=build_authorization_service())
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    # An unbound observability view is fail-closed.
    with pytest.raises(ServiceDiscoveryError):
        service.runtime(session.session_id, now=1)


def test_service_without_observability_view_is_fail_closed():
    from platform.portal.access import PortalAccessGateway
    from platform.portal.navigation import NavigationModel
    from platform.portal.routing import Router
    from platform.portal.search import GlobalSearch, default_search_index
    from platform.portal.workspace import WorkspaceSelector

    authorization = build_authorization_service()
    gateway = PortalAccessGateway(authorization)
    service = PortalService(
        gateway=gateway,
        navigation=NavigationModel(),
        router=Router(),
        workspace=WorkspaceSelector(gateway),
        search=GlobalSearch(default_search_index(), gateway),
        observability_view=None,
    )
    session = _session(service, Role.PLATFORM_ADMINISTRATOR)
    with pytest.raises(PortalServiceError):
        service.runtime(session.session_id, now=1)


# --------------------------------------------------------------------------- #
# Evidence / determinism                                                      #
# --------------------------------------------------------------------------- #


def test_portal_evidence_is_deterministic_across_identical_runs():
    def run() -> str:
        context = bootstrap_platform()
        service = bootstrap_portal(context)
        admin = Principal.create("admin@ucos", [Role.PLATFORM_ADMINISTRATOR])
        session = service.gateway.establish_session(admin, issued_at=0, ttl=1000)
        service.enter(session.session_id, now=1)
        return service.evidence().fingerprint()

    assert run() == run()


def test_evidence_reports_accessibility_and_counts():
    _, service = _platform_portal()
    evidence = service.evidence()
    assert evidence.accessibility_passed is True
    assert evidence.surface_count == 16
    assert evidence.contract_count == 7
    assert evidence.evidence_id.startswith("UCOS-PTEV-")


def test_to_dict_summary():
    _, service = _platform_portal()
    summary = service.to_dict()
    assert summary["surface_count"] == 16
    assert summary["route_count"] == 16
    assert summary["observability_bound"] is True
