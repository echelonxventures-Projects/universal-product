"""EC2-TASK-000073 — Portal contracts + vocabulary tests.

Covers the portal surface catalog (transcribed from the §3.2 capability groups), the
section classification (main/account/administration/governance/observability), the
search entity kinds (≥4), and the published portal contract surface — all immutable,
deterministic, and fail-closed.
"""

from __future__ import annotations

from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup, all_capability_groups
from platform.portal.contracts import (
    PORTAL_CONTRACT_VERSION,
    PORTAL_CONTRACTS,
    PORTAL_HOME_PATH,
    EntityKind,
    PortalSection,
    PortalSurface,
    all_entity_kinds,
    all_portal_sections,
    default_portal_contracts,
    default_portal_surfaces,
    entity_kind_group,
    portal_contract,
)
from platform.portal.errors import PortalContractError, PortalSearchError

import pytest


def test_every_capability_group_has_exactly_one_surface():
    surfaces = default_portal_surfaces()
    assert len(surfaces) == len(all_capability_groups()) == 16
    groups = {s.group for s in surfaces}
    assert groups == set(all_capability_groups())


def test_surfaces_are_deterministic_and_content_addressed():
    a = default_portal_surfaces()
    b = default_portal_surfaces()
    assert [s.to_dict() for s in a] == [s.to_dict() for s in b]
    assert all(s.surface_id.startswith("UCOS-PSUR-") for s in a)


def test_home_surface_routes_to_root_and_requires_read():
    home = next(s for s in default_portal_surfaces() if s.is_home)
    assert home.group is CapabilityGroup.PORTAL_NAVIGATION
    assert home.path == PORTAL_HOME_PATH == "/"
    assert home.required_permission is Permission.READ


def test_non_home_paths_are_unique_and_absolute():
    surfaces = default_portal_surfaces()
    paths = [s.path for s in surfaces]
    assert len(paths) == len(set(paths))
    assert all(p.startswith("/") for p in paths)


def test_admin_and_governance_and_observability_sections_populated():
    surfaces = default_portal_surfaces()
    by_section: dict[PortalSection, list[PortalSurface]] = {
        sec: [] for sec in all_portal_sections()
    }
    for s in surfaces:
        by_section[s.section].append(s)
    assert by_section[PortalSection.ADMINISTRATION]
    assert by_section[PortalSection.GOVERNANCE]
    assert by_section[PortalSection.OBSERVABILITY]
    assert by_section[PortalSection.ACCOUNT]
    assert by_section[PortalSection.MAIN]


def test_surface_create_rejects_bad_inputs():
    with pytest.raises(PortalContractError):
        PortalSurface.create("", CapabilityGroup.API_ACCESS, PortalSection.MAIN, "/x")
    with pytest.raises(PortalContractError):
        PortalSurface.create("t", "not-a-group", PortalSection.MAIN, "/x")  # type: ignore[arg-type]
    with pytest.raises(PortalContractError):
        PortalSurface.create("t", CapabilityGroup.API_ACCESS, "nope", "/x")  # type: ignore[arg-type]
    with pytest.raises(PortalContractError):
        PortalSurface.create("t", CapabilityGroup.API_ACCESS, PortalSection.MAIN, "rel")
    with pytest.raises(PortalContractError):
        PortalSurface.create(
            "t",
            CapabilityGroup.API_ACCESS,
            PortalSection.MAIN,
            "/x",
            required_permission="R",  # type: ignore[arg-type]
        )


def test_entity_kinds_span_at_least_four_and_map_to_groups():
    kinds = all_entity_kinds()
    assert len(kinds) >= 4
    for kind in kinds:
        assert isinstance(entity_kind_group(kind), CapabilityGroup)


def test_entity_kind_group_rejects_non_kind():
    with pytest.raises(PortalSearchError):
        entity_kind_group("workspace")  # type: ignore[arg-type]


def test_published_portal_contracts():
    contracts = default_portal_contracts()
    assert len(contracts) == len(PORTAL_CONTRACTS) == 7
    names = {c.name for c in contracts}
    assert "portal.shell.entry" in names
    assert "portal.search.query" in names
    assert all(str(c.version) == PORTAL_CONTRACT_VERSION for c in contracts)


def test_portal_contract_rejects_empty_name():
    with pytest.raises(PortalContractError):
        portal_contract("")


def test_enum_values_stable():
    assert PortalSection.MAIN.value == "main"
    assert EntityKind.BLUEPRINT.value == "blueprint"
