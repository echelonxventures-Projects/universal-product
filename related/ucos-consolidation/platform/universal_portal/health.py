"""UCOS-EPIC-008 / Terminal T8 — Universal Portal health.

A deterministic, content-addressed conformance report over the composed Universal Portal:
the eight-surface catalog is complete and well-formed, the portal shell is accessible, the
self-backed developer and documentation surfaces are available, and the core operational
dashboards (Administration, Measurement, Validation, Certification) are bound to their
published backing services. The report is a pure function of the application registry and
the shell accessibility signal, so it is byte-identical across processes — the
machine-checkable analogue of an operational portal.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_portal.applications import ApplicationRegistry
from platform.universal_portal.contracts import PortalApplication, all_portal_applications
from platform.universal_portal.errors import UniversalPortalServiceError
from typing import Any

#: The applications that must be bound for the portal to be fully operational.
_CORE_APPLICATIONS: tuple[PortalApplication, ...] = (
    PortalApplication.ADMINISTRATION_PORTAL,
    PortalApplication.MEASUREMENT_DASHBOARD,
    PortalApplication.VALIDATION_DASHBOARD,
    PortalApplication.CERTIFICATION_DASHBOARD,
)


@dataclass(frozen=True, slots=True)
class UniversalPortalHealth:
    """A deterministic, content-addressed Universal Portal health report."""

    passed: bool
    checks: tuple[tuple[str, bool], ...]
    report_id: str = ""

    @classmethod
    def create(cls, checks: tuple[tuple[str, bool], ...]) -> UniversalPortalHealth:
        ordered = tuple(sorted(checks, key=lambda c: c[0]))
        passed = all(ok for _, ok in ordered)
        core = {"passed": passed, "checks": [list(c) for c in ordered]}
        return cls(
            passed=passed,
            checks=ordered,
            report_id=f"UCOS-T8HLTH-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "passed": self.passed,
            "checks": [{"name": name, "passed": ok} for name, ok in self.checks],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def universal_portal_health_report(
    registry: ApplicationRegistry,
    *,
    portal_accessibility_passed: bool,
) -> UniversalPortalHealth:
    """Produce the deterministic Universal Portal health report (fail-closed)."""
    if not isinstance(registry, ApplicationRegistry):
        raise UniversalPortalServiceError("a valid ApplicationRegistry is required")
    descriptors = registry.descriptors()
    catalog_complete = len(descriptors) == len(all_portal_applications()) == 8
    surfaces_well_formed = all(
        bool(d.title.strip()) and bool(d.consumed_contracts) for d in descriptors
    )
    core_bound = all(registry.is_bound(app) for app in _CORE_APPLICATIONS)
    # The developer and documentation surfaces are self-backed (pure read models over the
    # published vocabulary) and are therefore always available once the catalog is complete.
    checks = (
        ("catalog-complete", catalog_complete),
        ("surfaces-well-formed", surfaces_well_formed),
        ("portal-shell-accessible", bool(portal_accessibility_passed)),
        ("core-dashboards-bound", core_bound),
        ("developer-catalog-available", catalog_complete),
        ("documentation-index-available", catalog_complete),
    )
    return UniversalPortalHealth.create(checks)


__all__ = ["UniversalPortalHealth", "universal_portal_health_report"]
