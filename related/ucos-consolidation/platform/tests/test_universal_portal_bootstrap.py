"""Tests for bootstrapping the Universal Portal onto a PlatformContext (T8)."""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability
from platform.universal_portal.contracts import (
    UNIVERSAL_PORTAL_CONTRACTS,
    PortalApplication,
)
from platform.universal_portal.service import (
    UNIVERSAL_PORTAL_BOOTSTRAP_EVENT,
    bootstrap_universal_portal,
)


def _admin_session(service):
    auth = service.gateway.authorization
    established = auth.establish_session(
        Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR]), issued_at=0, ttl=1000
    )
    return established.session_id


def test_bootstrap_binds_all_eight_surfaces():
    ctx = bootstrap_platform()
    service = bootstrap_universal_portal(ctx)
    assert len(service.applications()) == 8
    assert service.applications_registry.bound_count == 8


def test_bootstrap_publishes_contracts_into_service_registry():
    ctx = bootstrap_platform()
    bootstrap_universal_portal(ctx)
    for ref in UNIVERSAL_PORTAL_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrap_emits_completion_event():
    ctx = bootstrap_platform()
    bootstrap_universal_portal(ctx)
    events = ctx.events.events_of(UNIVERSAL_PORTAL_BOOTSTRAP_EVENT)
    assert len(events) == 1
    assert events[0].payload["applications"] == 8
    assert events[0].payload["bound"] == 8


def test_bootstrap_portal_is_fully_operational():
    ctx = bootstrap_platform()
    service = bootstrap_universal_portal(ctx)
    sid = _admin_session(service)
    assert service.enter(sid, now=1).landing_path == "/"
    for app in PortalApplication:
        view = service.open(sid, app, now=1)
        assert view.authorized is True
        assert view.available is True
        assert view.served is True
    assert service.health().passed is True


def test_bootstrap_reuses_supplied_identity_and_observability():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    service = bootstrap_universal_portal(ctx, authorization=auth, observability=obs)
    assert service.gateway.authorization is auth


def test_bootstrap_knowledge_snapshot_reads_published_knowledge_graph():
    ctx = bootstrap_platform()
    service = bootstrap_universal_portal(ctx)
    sid = _admin_session(service)
    view = service.knowledge_graph(sid, now=1)
    assert view.snapshot["source"] == "engine.knowledge"
    assert view.snapshot["node_count"] >= 1
    assert view.snapshot["object_count"] >= 1


def test_bootstrap_registry_explorer_reads_service_directory():
    ctx = bootstrap_platform()
    service = bootstrap_universal_portal(ctx)
    sid = _admin_session(service)
    view = service.registry_explorer(sid, now=1)
    assert view.snapshot["service_count"] >= 1


def test_bootstrap_is_idempotent_on_contracts():
    ctx = bootstrap_platform()
    bootstrap_universal_portal(ctx)
    before = len(ctx.services)
    # Re-registering the same contracts must not duplicate service declarations.
    bootstrap_universal_portal(ctx)
    assert len(ctx.services) == before
