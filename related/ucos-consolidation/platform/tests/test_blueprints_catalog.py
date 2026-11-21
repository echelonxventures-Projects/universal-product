"""EC2-TASK-000103 — Blueprint catalog (L6 read model) tests (EC2-EPIC-006)."""

from __future__ import annotations

from platform.blueprints.catalog import BlueprintCatalog, CatalogEntry
from platform.blueprints.contracts import BlueprintFamily, BlueprintStatus
from platform.blueprints.errors import BlueprintCatalogError
from platform.blueprints.provenance import BlueprintProvenance, ProvenanceLedger
from platform.blueprints.registry import BlueprintRegistry

import pytest


def _prov(blueprint_ref, family=BlueprintFamily.DATA):
    return BlueprintProvenance.create(
        blueprint_ref=blueprint_ref,
        family=family,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        generation_source="05-GENERATION/GEN-DATA-001",
        implementation_target="platform/blueprints",
        content_hash="c0ffee",
    )


def _catalogued_fixture():
    reg = BlueprintRegistry()
    prov = ProvenanceLedger()
    bp = reg.create("bp-1", "BP One", "ws1", "arch@x", BlueprintFamily.DATA, tenant="acme")
    # promote to catalogued and record provenance
    reg.transition(bp.blueprint_id, BlueprintStatus.VALIDATED, tick=1)
    reg.transition(bp.blueprint_id, BlueprintStatus.CATALOGUED, tick=2)
    prov.record(_prov(bp.blueprint_id))
    catalog = BlueprintCatalog(reg, prov)
    return reg, prov, catalog, bp


def test_catalog_requires_valid_components():
    with pytest.raises(BlueprintCatalogError):
        BlueprintCatalog("nope", ProvenanceLedger())  # type: ignore[arg-type]
    with pytest.raises(BlueprintCatalogError):
        BlueprintCatalog(BlueprintRegistry(), "nope")  # type: ignore[arg-type]


def test_catalog_surfaces_catalogued_entries_with_provenance():
    reg, prov, catalog, bp = _catalogued_fixture()
    assert len(catalog) == 1
    assert bp.blueprint_id in catalog
    entry = catalog.entry(bp.blueprint_id)
    assert isinstance(entry, CatalogEntry)
    assert entry.blueprint_id == bp.blueprint_id
    assert entry.is_traceable is True
    assert entry.trace_edge()["link"] == "GOV-002-link-4"
    assert catalog.blueprint_ids() == (bp.blueprint_id,)
    assert catalog.trace(bp.blueprint_id)["traceable"] is True
    assert catalog.to_dict()["entry_count"] == 1
    assert isinstance(catalog.fingerprint(), str)


def test_draft_blueprint_not_visible_in_catalog():
    reg = BlueprintRegistry()
    prov = ProvenanceLedger()
    bp = reg.create("bp-1", "n", "ws1", "o", BlueprintFamily.DATA)
    catalog = BlueprintCatalog(reg, prov)
    assert bp.blueprint_id not in catalog
    assert len(catalog) == 0
    with pytest.raises(BlueprintCatalogError):
        catalog.entry(bp.blueprint_id)  # not published


def test_catalogued_without_provenance_is_not_admissible():
    reg = BlueprintRegistry()
    prov = ProvenanceLedger()
    bp = reg.create("bp-1", "n", "ws1", "o", BlueprintFamily.DATA)
    reg.transition(bp.blueprint_id, BlueprintStatus.VALIDATED, tick=1)
    reg.transition(bp.blueprint_id, BlueprintStatus.CATALOGUED, tick=2)
    catalog = BlueprintCatalog(reg, prov)
    assert bp.blueprint_id not in catalog  # missing provenance
    assert catalog.entries() == ()
    with pytest.raises(BlueprintCatalogError):
        catalog.entry(bp.blueprint_id)


def test_superseded_entries_remain_visible():
    reg, prov, catalog, bp = _catalogued_fixture()
    reg.transition(bp.blueprint_id, BlueprintStatus.SUPERSEDED, tick=3)
    assert bp.blueprint_id in catalog
    assert catalog.entry(bp.blueprint_id).is_traceable is True


def test_entries_scoped_by_workspace_tenant_family():
    reg, prov, catalog, bp = _catalogued_fixture()
    assert len(catalog.entries(workspace_id="ws1")) == 1
    assert len(catalog.entries(workspace_id="other")) == 0
    assert len(catalog.entries(tenant="acme")) == 1
    assert len(catalog.entries(family=BlueprintFamily.DATA)) == 1
    assert len(catalog.entries(family=BlueprintFamily.API)) == 0


def test_contains_unknown_blueprint_is_false():
    _, _, catalog, _ = _catalogued_fixture()
    assert "UCOS-BLPR-missing" not in catalog


def test_catalog_entry_fingerprint_and_serialisation():
    _, _, catalog, bp = _catalogued_fixture()
    entry = catalog.entry(bp.blueprint_id)
    assert isinstance(entry.fingerprint(), str)
    assert entry.to_dict()["is_traceable"] is True
