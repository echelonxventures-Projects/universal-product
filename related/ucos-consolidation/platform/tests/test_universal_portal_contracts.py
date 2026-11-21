"""Tests for the Universal Portal contracts & vocabulary (UCOS-EPIC-008 / T8)."""

from __future__ import annotations

from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup, all_capability_groups
from platform.universal_portal.contracts import (
    UNIVERSAL_PORTAL_CONTRACT_VERSION,
    UNIVERSAL_PORTAL_CONTRACTS,
    ApplicationSection,
    PortalApplication,
    UniversalPortalSurface,
    all_portal_applications,
    application_group,
    application_section,
    application_title,
    consumed_contract_refs,
    default_universal_portal_contracts,
    default_universal_portal_surfaces,
    required_permission,
    universal_portal_contract,
)
from platform.universal_portal.errors import UniversalPortalContractError

import pytest


def test_eight_applications_declared():
    apps = all_portal_applications()
    assert len(apps) == 8
    assert apps == tuple(PortalApplication)


def test_every_application_binds_a_known_capability_group_read_only():
    known = set(all_capability_groups())
    for app in all_portal_applications():
        group = application_group(app)
        assert isinstance(group, CapabilityGroup)
        assert group in known  # creates no new authority
        assert required_permission(app) is Permission.READ
        assert isinstance(application_section(app), ApplicationSection)
        assert application_title(app).strip()


def test_consumed_contracts_are_published_references_for_every_application():
    for app in all_portal_applications():
        refs = consumed_contract_refs(app)
        assert refs, f"{app} must consume at least one published contract"
        for ref in refs:
            assert ref.name and str(ref.version)


def test_surface_is_content_addressed_and_deterministic():
    for app in all_portal_applications():
        s1 = UniversalPortalSurface.of(app)
        s2 = UniversalPortalSurface.of(app)
        assert s1 == s2
        assert s1.surface_id.startswith("UCOS-T8SUR-")
        assert s1.to_dict()["application"] == app.value
        assert s1.consumed_contracts


def test_default_surfaces_cover_all_applications_in_order():
    surfaces = default_universal_portal_surfaces()
    assert tuple(s.application for s in surfaces) == all_portal_applications()


def test_published_contracts_are_versioned_and_nine():
    assert len(UNIVERSAL_PORTAL_CONTRACTS) == 9
    for ref in UNIVERSAL_PORTAL_CONTRACTS:
        assert str(ref.version) == UNIVERSAL_PORTAL_CONTRACT_VERSION
    contracts = default_universal_portal_contracts()
    assert len(contracts) == 9
    assert {c.name for c in contracts} == {r.name for r in UNIVERSAL_PORTAL_CONTRACTS}


def test_universal_portal_contract_builds_at_version():
    c = universal_portal_contract("universal-portal.shell.compose", "desc")
    assert c.name == "universal-portal.shell.compose"
    assert str(c.version) == UNIVERSAL_PORTAL_CONTRACT_VERSION


def test_registry_explorer_consumes_engine_registry_and_portal_discovery():
    names = {r.name for r in consumed_contract_refs(PortalApplication.REGISTRY_EXPLORER)}
    assert "registry.read" in names
    assert "portal.discovery.services" in names


def test_knowledge_explorer_consumes_published_ukda_contract():
    names = {r.name for r in consumed_contract_refs(PortalApplication.KNOWLEDGE_GRAPH_EXPLORER)}
    assert names == {"knowledge.ukda"}


@pytest.mark.parametrize(
    "func",
    [
        application_group,
        application_section,
        application_title,
        required_permission,
        consumed_contract_refs,
        UniversalPortalSurface.of,
    ],
)
def test_vocabulary_functions_fail_closed_on_bad_input(func):
    with pytest.raises(UniversalPortalContractError):
        func("not-an-application")


def test_universal_portal_contract_requires_name():
    with pytest.raises(UniversalPortalContractError):
        universal_portal_contract("")
