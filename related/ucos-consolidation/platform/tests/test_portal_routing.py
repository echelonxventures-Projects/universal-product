"""EC2-TASK-000076 — Portal routing model tests.

Covers deterministic path→surface resolution, path normalization, authorization
requirements carried on each route, and fail-closed handling of unknown/malformed
paths and duplicate routes.
"""

from __future__ import annotations

from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.portal.contracts import PortalSection, PortalSurface, default_portal_surfaces
from platform.portal.errors import RoutingError
from platform.portal.routing import Router, normalize_path

import pytest


def test_router_resolves_home_and_carries_authorization():
    router = Router()
    route = router.resolve("/")
    assert route.group is CapabilityGroup.PORTAL_NAVIGATION
    assert route.required_permission is Permission.READ


def test_router_has_route_for_every_surface():
    router = Router()
    assert len(router) == 16
    for surface in default_portal_surfaces():
        assert surface.path in router


def test_resolve_unknown_path_is_fail_closed():
    router = Router()
    with pytest.raises(RoutingError):
        router.resolve("/does-not-exist")


def test_normalize_path_strips_trailing_slash_except_root():
    assert normalize_path("/") == "/"
    assert normalize_path("/api-access/") == "/api-access"
    assert normalize_path("/api-access") == "/api-access"


def test_normalize_path_rejects_relative_and_empty():
    with pytest.raises(RoutingError):
        normalize_path("relative")
    with pytest.raises(RoutingError):
        normalize_path("")


def test_resolve_is_normalization_insensitive():
    router = Router()
    assert router.resolve("/api-access/").path == router.resolve("/api-access").path


def test_contains_handles_bad_paths():
    router = Router()
    assert "relative" not in router
    assert "/api-access" in router


def test_router_rejects_duplicate_paths():
    surfaces = list(default_portal_surfaces())
    dup = PortalSurface.create(
        "Dup", CapabilityGroup.BLUEPRINT_CATALOG, PortalSection.MAIN, surfaces[2].path
    )
    with pytest.raises(RoutingError):
        Router(surfaces + [dup])


def test_router_rejects_empty_catalog():
    with pytest.raises(RoutingError):
        Router([])


def test_router_rejects_non_surface_entries():
    with pytest.raises(RoutingError):
        Router([123])  # type: ignore[list-item]


def test_routes_are_ordered_by_path():
    routes = Router().routes()
    assert [r.path for r in routes] == sorted(r.path for r in routes)


def test_router_is_deterministic():
    assert Router().fingerprint() == Router().fingerprint()
    assert Router().paths == tuple(sorted(Router().paths))


def test_routes_serialize_with_authorization():
    payload = Router().to_dict()
    assert payload["route_count"] == 16
    assert all("group" in r and "required_permission" in r for r in payload["routes"])
