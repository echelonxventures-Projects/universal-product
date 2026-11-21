"""EC2-TASK-000076 — Portal Routing Model (EC2-EPIC-003).

The deterministic routing model of the portal shell. It maps an absolute route
``path`` to the :class:`~platform.portal.contracts.PortalSurface` that serves it and,
because every surface binds a §3.2 capability group and required permission, each
:class:`Route` **carries the authorization requirement** for its target. Routing is
therefore the join point between navigation and access control: the portal service
resolves a path here and then authorizes the resolved surface's
``(group, permission)`` through the access gateway before serving it.

The router is a pure function of the surface catalog: resolution is O(1), stable, and
**fail-closed** — an unknown or malformed path raises :class:`RoutingError` rather
than defaulting to any surface.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.portal.contracts import PortalSurface, default_portal_surfaces
from platform.portal.errors import RoutingError
from typing import Any


@dataclass(frozen=True, slots=True)
class Route:
    """An immutable route: a path bound to a surface and its authorization need."""

    path: str
    surface: PortalSurface

    @property
    def group(self) -> CapabilityGroup:
        """The capability group a caller must be authorized on to follow this route."""
        return self.surface.group

    @property
    def required_permission(self) -> Permission:
        """The permission a caller must hold on :attr:`group` to follow this route."""
        return self.surface.required_permission

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "surface_id": self.surface.surface_id,
            "group": self.group.value,
            "required_permission": self.required_permission.value,
        }


def normalize_path(path: str) -> str:
    """Normalize a route path (fail-closed).

    Requires an absolute path. A trailing slash is stripped except for the root
    ``/`` so ``/foo`` and ``/foo/`` resolve identically and deterministically.
    """
    if not isinstance(path, str) or not path:
        raise RoutingError("route path is required")
    if not path.startswith("/"):
        raise RoutingError("route path must be absolute", path=path)
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return path


class Router:
    """A deterministic, fail-closed router over the portal surface catalog."""

    __slots__ = ("_routes",)

    def __init__(self, surfaces: Iterable[PortalSurface] | None = None) -> None:
        catalog = tuple(surfaces) if surfaces is not None else default_portal_surfaces()
        if not catalog:
            raise RoutingError("router requires at least one surface")
        routes: dict[str, Route] = {}
        for surface in catalog:
            if not isinstance(surface, PortalSurface):
                raise RoutingError("router surfaces must be PortalSurface instances")
            path = normalize_path(surface.path)
            if path in routes:
                raise RoutingError("duplicate route path", path=path)
            routes[path] = Route(path=path, surface=surface)
        self._routes = routes

    def __contains__(self, path: str) -> bool:
        try:
            return normalize_path(path) in self._routes
        except RoutingError:
            return False

    def __len__(self) -> int:
        return len(self._routes)

    @property
    def paths(self) -> tuple[str, ...]:
        """Every routable path in stable (sorted) order."""
        return tuple(sorted(self._routes))

    def routes(self) -> tuple[Route, ...]:
        """Every route in stable (path) order."""
        return tuple(self._routes[p] for p in self.paths)

    def resolve(self, path: str) -> Route:
        """Resolve ``path`` to its :class:`Route` (fail-closed on unknown path)."""
        normalized = normalize_path(path)
        route = self._routes.get(normalized)
        if route is None:
            raise RoutingError("no route for path", path=normalized)
        return route

    def to_dict(self) -> dict[str, Any]:
        return {
            "route_count": len(self._routes),
            "routes": [self._routes[p].to_dict() for p in self.paths],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["Route", "normalize_path", "Router"]
