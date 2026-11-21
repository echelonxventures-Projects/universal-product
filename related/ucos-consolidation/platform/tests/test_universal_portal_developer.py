"""Tests for the Universal Portal Developer Portal / API catalog (UCOS-EPIC-008 / T8)."""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability
from platform.portal.discovery import ServiceDirectory
from platform.universal_portal.contracts import PortalApplication, all_portal_applications
from platform.universal_portal.developer import ApiEntry, DeveloperCatalog, DeveloperPortal
from platform.universal_portal.errors import DeveloperPortalError

import pytest


def test_catalog_covers_every_application_and_is_content_addressed():
    catalog = DeveloperPortal().catalog()
    assert isinstance(catalog, DeveloperCatalog)
    apps_in_catalog = {e.application for e in catalog.entries}
    assert apps_in_catalog == {a.value for a in all_portal_applications()}
    assert catalog.catalog_id.startswith("UCOS-T8CAT-")
    assert catalog.api_count == len(catalog.entries)
    assert catalog.platform_contracts  # the published T8 contracts


def test_catalog_entries_are_sorted_and_deterministic():
    c1 = DeveloperPortal().catalog()
    c2 = DeveloperPortal().catalog()
    assert c1.fingerprint() == c2.fingerprint()
    keys = [(e.application, e.contract_name) for e in c1.entries]
    assert keys == sorted(keys)


def test_entries_for_application_filters():
    portal = DeveloperPortal()
    entries = portal.entries_for(PortalApplication.KNOWLEDGE_GRAPH_EXPLORER)
    assert entries
    assert all(isinstance(e, ApiEntry) for e in entries)
    assert {e.contract_name for e in entries} == {"knowledge.ukda"}


def test_entries_for_rejects_bad_input():
    with pytest.raises(DeveloperPortalError):
        DeveloperPortal().entries_for("nope")


def test_directory_binding_rejects_bad_type():
    with pytest.raises(DeveloperPortalError):
        DeveloperPortal(directory=object())


def test_catalog_enriched_with_bound_service_directory():
    ctx = bootstrap_platform()
    bootstrap_identity(ctx)
    bootstrap_observability(ctx)
    directory = ServiceDirectory(ctx.services, ctx.capabilities)
    portal = DeveloperPortal(directory)
    assert portal.bound_directory is True
    catalog = portal.catalog()
    assert catalog.service_names  # live platform services discovered
    assert catalog.capability_ids  # published capability ids
    body = catalog.to_dict()
    assert body["service_count"] == len(catalog.service_names)


def test_api_entry_is_content_addressed():
    e = ApiEntry.create(
        application="developer-portal",
        section="developer",
        contract_name="x.y",
        contract_version="1.0.0",
        group="api-access",
        required_permission="read",
    )
    assert e.entry_id.startswith("UCOS-T8API-")
    assert e.to_dict()["contract_name"] == "x.y"
