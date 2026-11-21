"""EC2-TASK-000075 — Portal Navigation Model (EC2-EPIC-003).

The deterministic navigation model of the portal shell. It answers the acceptance
criterion *"navigation to all authorized surfaces"*: given an authorization predicate
(supplied by the :class:`~platform.portal.access.PortalAccessGateway`), it renders the
subset of the sixteen :class:`~platform.portal.contracts.PortalSurface` s the caller
is authorized to see, grouped by :class:`~platform.portal.contracts.PortalSection`
and stably ordered. The model is a **pure function** of the surface catalog and the
predicate — it performs no I/O and holds no session state.

It also produces a deterministic :class:`AccessibilityReport` satisfying the
acceptance criterion *"accessibility checks pass"*: every surface must carry a
non-empty human-readable label, a unique stable navigation key, a unique absolute
route, and an explicit required permission — the machine-checkable analogue of
accessible, unambiguous navigation for a headless presentation model.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.portal.contracts import (
    PortalSection,
    PortalSurface,
    all_portal_sections,
    default_portal_surfaces,
)
from platform.portal.errors import NavigationError
from typing import Any

#: A predicate deciding whether a surface is visible to the current caller.
SurfacePredicate = Callable[[PortalSurface], bool]


def _navigation_key(surface: PortalSurface) -> str:
    """A stable, unique navigation key (ARIA-like identifier) for a surface."""
    return f"nav-{surface.group.value}"


@dataclass(frozen=True, slots=True)
class NavigationItem:
    """An immutable navigation entry for a single authorized surface."""

    key: str
    label: str
    path: str
    section: PortalSection
    surface_id: str

    @classmethod
    def of(cls, surface: PortalSurface) -> NavigationItem:
        return cls(
            key=_navigation_key(surface),
            label=surface.title,
            path=surface.path,
            section=surface.section,
            surface_id=surface.surface_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "path": self.path,
            "section": self.section.value,
            "surface_id": self.surface_id,
        }


@dataclass(frozen=True, slots=True)
class NavigationSection:
    """An immutable, ordered group of navigation items under one section."""

    section: PortalSection
    items: tuple[NavigationItem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "section": self.section.value,
            "items": [i.to_dict() for i in self.items],
        }


@dataclass(frozen=True, slots=True)
class Navigation:
    """An immutable, content-addressed navigation tree for one caller."""

    sections: tuple[NavigationSection, ...]
    navigation_id: str = ""

    @classmethod
    def create(cls, sections: tuple[NavigationSection, ...]) -> Navigation:
        core = [s.to_dict() for s in sections]
        return cls(
            sections=sections,
            navigation_id=f"UCOS-PNAV-{content_hash(core)[:16]}",
        )

    @property
    def items(self) -> tuple[NavigationItem, ...]:
        """Every visible item across all sections in stable order."""
        return tuple(item for section in self.sections for item in section.items)

    @property
    def paths(self) -> tuple[str, ...]:
        """Every visible route path in stable order."""
        return tuple(item.path for item in self.items)

    def has_path(self, path: str) -> bool:
        return path in set(self.paths)

    def to_dict(self) -> dict[str, Any]:
        return {
            "navigation_id": self.navigation_id,
            "section_count": len(self.sections),
            "item_count": len(self.items),
            "sections": [s.to_dict() for s in self.sections],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class AccessibilityReport:
    """A deterministic, content-addressed accessibility conformance report."""

    passed: bool
    checks: tuple[tuple[str, bool], ...]
    report_id: str = ""

    @classmethod
    def create(cls, checks: tuple[tuple[str, bool], ...]) -> AccessibilityReport:
        ordered = tuple(sorted(checks, key=lambda c: c[0]))
        passed = all(ok for _, ok in ordered)
        core = {"passed": passed, "checks": [list(c) for c in ordered]}
        return cls(
            passed=passed,
            checks=ordered,
            report_id=f"UCOS-PA11Y-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "passed": self.passed,
            "checks": [{"name": name, "passed": ok} for name, ok in self.checks],
        }


class NavigationModel:
    """The deterministic portal navigation model over the surface catalog."""

    __slots__ = ("_surfaces",)

    def __init__(self, surfaces: Iterable[PortalSurface] | None = None) -> None:
        catalog = tuple(surfaces) if surfaces is not None else default_portal_surfaces()
        if not catalog:
            raise NavigationError("navigation model requires at least one surface")
        seen_paths: set[str] = set()
        seen_keys: set[str] = set()
        for surface in catalog:
            if not isinstance(surface, PortalSurface):
                raise NavigationError("navigation surfaces must be PortalSurface instances")
            if surface.path in seen_paths:
                raise NavigationError("duplicate surface route path", path=surface.path)
            key = _navigation_key(surface)
            if key in seen_keys:
                raise NavigationError("duplicate navigation key", key=key)
            seen_paths.add(surface.path)
            seen_keys.add(key)
        self._surfaces = catalog

    @property
    def surfaces(self) -> tuple[PortalSurface, ...]:
        return self._surfaces

    def surfaces_in(self, section: PortalSection) -> tuple[PortalSurface, ...]:
        """Every surface in ``section`` in stable catalog order."""
        if not isinstance(section, PortalSection):
            raise NavigationError("section must be a PortalSection")
        return tuple(s for s in self._surfaces if s.section is section)

    def build(self, is_visible: SurfacePredicate) -> Navigation:
        """Build the authorized :class:`Navigation` tree for one caller.

        ``is_visible`` is called once per surface; only surfaces for which it returns
        ``True`` appear. Sections with no visible items are omitted. Ordering is
        deterministic: sections in declaration order, items in catalog order.
        """
        if not callable(is_visible):
            raise NavigationError("is_visible must be callable")
        sections: list[NavigationSection] = []
        for section in all_portal_sections():
            items = tuple(
                NavigationItem.of(surface)
                for surface in self._surfaces
                if surface.section is section and self._safe_visible(is_visible, surface)
            )
            if items:
                sections.append(NavigationSection(section=section, items=items))
        return Navigation.create(tuple(sections))

    def accessibility_report(self) -> AccessibilityReport:
        """Verify the navigation catalog is accessible/unambiguous (deterministic)."""
        titles_present = all(bool(s.title.strip()) for s in self._surfaces)
        paths = [s.path for s in self._surfaces]
        keys = [_navigation_key(s) for s in self._surfaces]
        sections_known = all(isinstance(s.section, PortalSection) for s in self._surfaces)
        perms_explicit = all(s.required_permission is not None for s in self._surfaces)
        home_present = any(s.is_home for s in self._surfaces)
        checks = (
            ("labels-non-empty", titles_present),
            ("routes-unique", len(paths) == len(set(paths))),
            ("keys-unique", len(keys) == len(set(keys))),
            ("sections-known", sections_known),
            ("permissions-explicit", perms_explicit),
            ("home-surface-present", home_present),
        )
        return AccessibilityReport.create(checks)

    @staticmethod
    def _safe_visible(is_visible: SurfacePredicate, surface: PortalSurface) -> bool:
        """Evaluate the predicate fail-closed (any error hides the surface)."""
        try:
            return bool(is_visible(surface))
        except Exception:  # noqa: BLE001 — fail-closed: on doubt, hide the surface
            return False


__all__ = [
    "SurfacePredicate",
    "NavigationItem",
    "NavigationSection",
    "Navigation",
    "AccessibilityReport",
    "NavigationModel",
]
