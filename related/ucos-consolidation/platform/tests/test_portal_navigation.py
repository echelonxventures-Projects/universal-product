"""EC2-TASK-000075 — Portal navigation model tests.

Covers authorization-filtered navigation (navigation to all authorized surfaces),
deterministic section ordering and content-addressed navigation ids, the accessibility
report (accessibility checks pass), and fail-closed predicate handling.
"""

from __future__ import annotations

from platform.identity.contracts import CapabilityGroup
from platform.portal.contracts import PortalSection, PortalSurface, default_portal_surfaces
from platform.portal.errors import NavigationError
from platform.portal.navigation import NavigationModel

import pytest


def _model() -> NavigationModel:
    return NavigationModel()


def test_full_navigation_when_everything_visible():
    nav = _model().build(lambda surface: True)
    assert len(nav.items) == 16
    assert nav.navigation_id.startswith("UCOS-PNAV-")
    # Sections appear in declaration order and only when populated.
    sections = [s.section for s in nav.sections]
    assert sections == sorted(sections, key=list(PortalSection).index)


def test_empty_navigation_when_nothing_visible():
    nav = _model().build(lambda surface: False)
    assert nav.sections == ()
    assert nav.items == ()


def test_navigation_filters_to_authorized_surfaces():
    # Only surfaces in the GOVERNANCE section are visible.
    nav = _model().build(lambda s: s.section is PortalSection.GOVERNANCE)
    assert {i.section for i in nav.items} == {PortalSection.GOVERNANCE}
    assert all(i.key.startswith("nav-") for i in nav.items)


def test_navigation_is_deterministic():
    a = _model().build(lambda s: True)
    b = _model().build(lambda s: True)
    assert a.fingerprint() == b.fingerprint()
    assert a.navigation_id == b.navigation_id


def test_has_path_and_paths():
    nav = _model().build(lambda s: True)
    assert nav.has_path("/")
    assert "/api-access" in nav.paths


def test_predicate_failure_hides_surface_fail_closed():
    def boom(_surface: PortalSurface) -> bool:
        raise RuntimeError("predicate error")

    nav = _model().build(boom)
    assert nav.items == ()  # fail-closed: on doubt, hide


def test_accessibility_report_passes():
    report = _model().accessibility_report()
    assert report.passed is True
    assert report.report_id.startswith("UCOS-PA11Y-")
    names = {name for name, _ in report.checks}
    assert {"routes-unique", "keys-unique", "labels-non-empty", "home-surface-present"} <= names


def test_model_rejects_duplicate_paths():
    surfaces = list(default_portal_surfaces())
    dup = PortalSurface.create(
        "Dup", CapabilityGroup.API_ACCESS, PortalSection.MAIN, surfaces[1].path
    )
    with pytest.raises(NavigationError):
        NavigationModel(surfaces + [dup])


def test_model_rejects_duplicate_navigation_keys():
    # Two surfaces sharing a capability group share a navigation key.
    a = PortalSurface.create("A", CapabilityGroup.API_ACCESS, PortalSection.MAIN, "/a")
    b = PortalSurface.create("B", CapabilityGroup.API_ACCESS, PortalSection.MAIN, "/b")
    with pytest.raises(NavigationError):
        NavigationModel([a, b])


def test_model_rejects_non_surface_entries():
    with pytest.raises(NavigationError):
        NavigationModel(["not-a-surface"])  # type: ignore[list-item]


def test_model_rejects_empty_catalog():
    with pytest.raises(NavigationError):
        NavigationModel([])


def test_build_requires_callable():
    with pytest.raises(NavigationError):
        _model().build("not-callable")  # type: ignore[arg-type]


def test_surfaces_in_section_and_validation():
    model = _model()
    gov = model.surfaces_in(PortalSection.GOVERNANCE)
    assert all(s.section is PortalSection.GOVERNANCE for s in gov)
    with pytest.raises(NavigationError):
        model.surfaces_in("gov")  # type: ignore[arg-type]
