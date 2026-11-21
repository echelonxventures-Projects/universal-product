"""EC2-TASK-000078 — Portal platform-services access tests.

Covers the service-discovery / capability-access model (a deterministic read view
over the Foundation registries) and the authorization-gated observability integration
(health/runtime/monitoring visibility), including fail-closed handling of unauthorized
callers and an unbound observability layer.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck
from platform.observability.service import build_observability_service
from platform.portal.access import PortalAccessGateway
from platform.portal.discovery import ObservabilityView, ServiceDirectory
from platform.portal.errors import ServiceDiscoveryError
from platform.portal.service import bootstrap_portal

import pytest

# --------------------------------------------------------------------------- #
# ServiceDirectory                                                            #
# --------------------------------------------------------------------------- #


def _directory() -> ServiceDirectory:
    context = bootstrap_platform()
    bootstrap_portal(context)
    return ServiceDirectory(context.services, context.capabilities)


def test_directory_requires_valid_registries():
    with pytest.raises(ServiceDiscoveryError):
        ServiceDirectory("nope", None)  # type: ignore[arg-type]


def test_directory_requires_valid_capability_catalog():
    from platform.foundation.services import ServiceRegistry

    with pytest.raises(ServiceDiscoveryError):
        ServiceDirectory(ServiceRegistry(), "nope")  # type: ignore[arg-type]


def test_directory_lists_published_services():
    directory = _directory()
    names = directory.service_names
    assert "portal.shell.entry" in names
    assert "identity.authorization.authorize" in names
    assert "observability.audit.trail" in names


def test_services_for_capability_returns_providers():
    directory = _directory()
    search_services = directory.services_for_capability("PC-13")
    assert any(d.name == "portal.search.query" for d in search_services)


def test_services_for_unknown_capability_is_fail_closed():
    directory = _directory()
    with pytest.raises(ServiceDiscoveryError):
        directory.services_for_capability("PC-999")


def test_describe_unknown_service_is_fail_closed():
    directory = _directory()
    with pytest.raises(ServiceDiscoveryError):
        directory.describe("no.such.service")


def test_describe_known_service_returns_descriptor():
    directory = _directory()
    descriptor = directory.describe("portal.shell.entry")
    assert descriptor.name == "portal.shell.entry"


def test_directory_is_deterministic():
    a = _directory()
    b = _directory()
    assert a.fingerprint() == b.fingerprint()
    assert a.capability_ids() == b.capability_ids()


# --------------------------------------------------------------------------- #
# ObservabilityView                                                           #
# --------------------------------------------------------------------------- #


def _view(bound: bool = True) -> tuple[PortalAccessGateway, ObservabilityView]:
    gateway = PortalAccessGateway(build_authorization_service())
    observability = build_observability_service() if bound else None
    if observability is not None:
        observability.register_health_check(HealthCheck("portal", critical=True))
    return gateway, ObservabilityView(gateway, observability)


def _session(gateway: PortalAccessGateway, role: Role, tenant: str | None = None):
    principal = Principal.create("u@ucos", [role], tenant=tenant)
    return gateway.establish_session(principal, issued_at=0, ttl=100)


def test_view_requires_valid_gateway():
    with pytest.raises(ServiceDiscoveryError):
        ObservabilityView("nope")  # type: ignore[arg-type]


def test_view_rejects_non_observability_service():
    gateway = PortalAccessGateway(build_authorization_service())
    with pytest.raises(ServiceDiscoveryError):
        ObservabilityView(gateway, "nope")  # type: ignore[arg-type]


def test_authorized_health_runtime_monitoring():
    gateway, view = _view()
    session = _session(gateway, Role.PLATFORM_ADMINISTRATOR)
    health = view.health(session.session_id, {"portal": HealthStatus.HEALTHY}, now=1)
    assert health["healthy"] is True
    runtime = view.runtime(session.session_id, now=1)
    assert "governed_action_count" in runtime and runtime["audit_chain_intact"] is True
    monitoring = view.monitoring(session.session_id, now=1)
    assert "series" in monitoring


def test_unauthorized_caller_is_denied():
    gateway, view = _view()
    # Integrator's monitoring grant is scoped; a tenant-less request is denied.
    session = _session(gateway, Role.INTEGRATOR, tenant=None)
    with pytest.raises(ServiceDiscoveryError):
        view.runtime(session.session_id, now=1)


def test_unbound_view_is_fail_closed():
    gateway, view = _view(bound=False)
    assert view.bound is False
    session = _session(gateway, Role.PLATFORM_ADMINISTRATOR)
    with pytest.raises(ServiceDiscoveryError):
        view.monitoring(session.session_id, now=1)
