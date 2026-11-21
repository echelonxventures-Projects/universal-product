"""Tests for the Universal Portal service composition root (UCOS-EPIC-008 / T8)."""

from __future__ import annotations

from platform.foundation.events import EventBus
from platform.foundation.identity import Role
from platform.tests.universal_portal_helpers import (
    FakeService,
    all_providers,
    build_service,
    session,
)
from platform.universal_portal.contracts import PortalApplication
from platform.universal_portal.documentation import DocumentationPortal
from platform.universal_portal.errors import UniversalPortalServiceError
from platform.universal_portal.service import (
    UNIVERSAL_PORTAL_OPENED_EVENT,
    UniversalPortalEvidence,
    UniversalPortalService,
    build_universal_portal_service,
)

import pytest


def test_build_requires_authorization_service():
    with pytest.raises(UniversalPortalServiceError):
        build_universal_portal_service(authorization=object())


def test_service_constructor_validates_components():
    auth, service = build_service()
    with pytest.raises(UniversalPortalServiceError):
        UniversalPortalService(
            portal=object(),
            registry=service.applications_registry,
            developer=service.developer_portal,
            documentation=service.documentation_portal,
        )
    with pytest.raises(UniversalPortalServiceError):
        UniversalPortalService(
            portal=service.portal,
            registry=object(),
            developer=service.developer_portal,
            documentation=service.documentation_portal,
        )
    with pytest.raises(UniversalPortalServiceError):
        UniversalPortalService(
            portal=service.portal,
            registry=service.applications_registry,
            developer=object(),
            documentation=service.documentation_portal,
        )
    with pytest.raises(UniversalPortalServiceError):
        UniversalPortalService(
            portal=service.portal,
            registry=service.applications_registry,
            developer=service.developer_portal,
            documentation=object(),
        )
    with pytest.raises(UniversalPortalServiceError):
        UniversalPortalService(
            portal=service.portal,
            registry=service.applications_registry,
            developer=service.developer_portal,
            documentation=service.documentation_portal,
            events=object(),
        )


def test_developer_and_documentation_are_auto_bound():
    _auth, service = build_service(providers={})
    reg = service.applications_registry
    assert reg.is_bound(PortalApplication.DEVELOPER_PORTAL)
    assert reg.is_bound(PortalApplication.DOCUMENTATION_PORTAL)


def test_authorized_open_serves_snapshot_and_counts():
    auth, service = build_service()
    sid = session(auth)
    view = service.administration(sid, now=1)
    assert view.authorized is True
    assert view.available is True
    assert view.served is True
    assert view.snapshot == {"service": "administration", "value": 1}
    assert service.open_count == 1


def test_unauthorized_open_is_fail_closed_no_snapshot():
    auth, service = build_service()
    sid = session(auth, role=Role.OPERATOR, subject="op@x")
    view = service.administration(sid, now=1)
    assert view.authorized is False
    assert view.served is False
    assert view.snapshot is None
    assert service.open_count == 0  # denied opens are not counted


def test_open_unbound_surface_authorized_but_unavailable():
    auth, service = build_service(providers={})  # only dev/doc auto-bound
    sid = session(auth)
    view = service.measurement(sid, now=1)
    assert view.authorized is True
    assert view.available is False
    assert view.served is False


def test_open_rejects_bad_application():
    auth, service = build_service()
    sid = session(auth)
    with pytest.raises(UniversalPortalServiceError):
        service.open(sid, "nope", now=1)


def test_convenience_accessors_cover_all_surfaces():
    auth, service = build_service(providers=all_providers())
    sid = session(auth)
    assert service.administration(sid, now=1).served
    assert service.registry_explorer(sid, now=1).served
    assert service.knowledge_graph(sid, now=1).served
    assert service.measurement(sid, now=1).served
    assert service.validation(sid, now=1).served
    assert service.certification(sid, now=1).served
    assert service.developer(sid, now=1).served
    assert service.documentation(sid, now=1).served


def test_open_emits_governed_event_only_when_authorized():
    events = EventBus()
    auth, service = build_service(events=events)
    sid = session(auth)
    service.administration(sid, now=1)
    opened = events.events_of(UNIVERSAL_PORTAL_OPENED_EVENT)
    assert len(opened) == 1
    assert opened[0].payload["application"] == "administration-portal"


def test_enter_delegates_to_portal_shell():
    auth, service = build_service()
    sid = session(auth)
    view = service.enter(sid, now=1)
    assert view.landing_path == "/"


def test_navigate_and_search_delegate_to_shell():
    auth, service = build_service()
    sid = session(auth)
    result = service.navigate(sid, "/", now=1)
    assert result.path == "/"
    response = service.search(sid, "a", now=1)
    assert response is not None


def test_discover_services_available_when_directory_bound():
    from platform.foundation.bootstrap import bootstrap_platform
    from platform.identity.service import bootstrap_identity

    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    service = build_universal_portal_service(
        authorization=auth, services=ctx.services, capabilities=ctx.capabilities
    )
    directory = service.discover_services()
    assert directory.service_names


def test_health_and_evidence_and_to_dict():
    auth, service = build_service()
    session(auth)
    health = service.health()
    assert health.passed is True
    evidence = service.evidence()
    assert isinstance(evidence, UniversalPortalEvidence)
    assert evidence.application_count == 8
    assert evidence.bound_count >= 4
    assert evidence.contract_count == 9
    assert evidence.evidence_id.startswith("UCOS-T8EV-")
    body = service.to_dict()
    assert body["applications"]["application_count"] == 8
    assert body["developer_catalog"]["api_count"] > 0
    assert body["documentation_index"]["page_count"] == 17
    assert body["contract_count"] == 9


def test_evidence_open_count_tracks_authorized_opens():
    auth, service = build_service()
    sid = session(auth)
    service.administration(sid, now=1)
    service.validation(sid, now=1)
    assert service.evidence().open_count == 2


def test_documentation_portal_property_is_shared():
    _auth, service = build_service()
    assert isinstance(service.documentation_portal, DocumentationPortal)


def test_snapshot_reflects_bound_service_value():
    providers = {PortalApplication.ADMINISTRATION_PORTAL: lambda: FakeService("admin", value=7)}
    auth, service = build_service(providers=providers)
    sid = session(auth)
    assert service.administration(sid, now=1).snapshot == {"service": "admin", "value": 7}
