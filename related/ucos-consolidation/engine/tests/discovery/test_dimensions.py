"""Tests for engine.discovery.dimensions — the eight registry-driven discoverers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from engine.discovery.contracts import DiscoveryKind
from engine.discovery.dimensions import (
    REALIZED_STATUSES,
    _slug,
    discover_capabilities,
    discover_components,
    discover_dependencies,
    discover_documents,
    discover_evidence,
    discover_namespaces,
    discover_ontology,
    discover_registries,
)
from engine.registry.adapter import RegistryAdapter
from engine.registry.models import LifecycleStatus


@pytest.fixture
def clean(clean_data_dir):
    return RegistryAdapter.open(clean_data_dir)


@pytest.fixture
def gapped(gapped_data_dir):
    return RegistryAdapter.open(gapped_data_dir)


# --------------------------------------------------------------------------- namespace


def test_namespaces_clean(clean):
    result = discover_namespaces(clean.artifacts, clean.volumes)
    assert result.kind is DiscoveryKind.NAMESPACE
    assert result.complete
    assert result.gaps == ()
    axes = {i.attributes["axis"] for i in result.items}
    assert axes == {"volume", "category", "program"}
    # 2 volumes + 3 categories (BOOK/ENG/REG) + 2 programs (ENG/UKB)
    assert result.count() == 7
    vol_item = next(i for i in result.items if i.item_id == "UDNS-VOL-VOL-000")
    assert vol_item.attributes["member_count"] == 2
    assert vol_item.attributes["registered"] is True


def test_namespaces_gap_dangling_volume(gapped):
    result = discover_namespaces(gapped.artifacts, gapped.volumes)
    assert not result.complete
    assert "VOL-999" in result.gaps
    dangling = next(i for i in result.items if i.item_id == "UDNS-VOL-VOL-999")
    assert dangling.attributes["registered"] is False
    assert result.coverage.discovered == result.coverage.total - 1


# --------------------------------------------------------------------------- document


def test_documents_clean(clean):
    result = discover_documents(clean.artifacts)
    assert result.complete
    assert result.count() == 3
    ids = result.item_ids()
    assert ids == tuple(sorted(ids))  # stable order
    doc = next(i for i in result.items if i.item_id == "UDDOC-UCOS-REG-000001")
    assert doc.attributes["path"] == "00-BOOK/UCOS-REG-000001.md"
    assert doc.references == ("UCOS-BOOK-000000",)


# --------------------------------------------------------------------------- registry


def test_registries_clean(clean):
    result = discover_registries(clean.source, clean.artifacts, clean.graph, clean.volumes)
    assert result.complete
    assert result.count() == 3
    by_name = {i.name: i for i in result.items}
    assert by_name["artifacts"].attributes["record_count"] == 3
    assert by_name["relationships"].attributes["record_count"] == 3
    assert by_name["volumes"].attributes["record_count"] == 2
    assert all(i.attributes["present"] for i in result.items)


# --------------------------------------------------------------------------- component


def test_components_clean(clean):
    result = discover_components(clean.artifacts, clean.graph)
    assert result.complete
    assert result.count() == 3
    book = next(i for i in result.items if i.item_id == "UDCMP-UCOS-BOOK-000000")
    assert set(book.references) == {"UCOS-REG-000001", "UCOS-ENG-000001"}
    assert book.attributes["child_count"] == 2
    beta = next(i for i in result.items if i.item_id == "UDCMP-UCOS-ENG-000001")
    assert beta.attributes["realized"] is True  # FROZEN is a realised status


def test_components_gap_dangling_parent(gapped):
    result = discover_components(gapped.artifacts, gapped.graph)
    assert not result.complete
    assert "UCOS-GAP-PARENT" in result.gaps
    orphan = next(i for i in result.items if i.item_id == "UDCMP-UCOS-GAP-PARENT")
    assert orphan.attributes["parent_resolves"] is False


# --------------------------------------------------------------------------- dependency


def test_dependencies_clean_dedup_graph_and_declared(clean):
    result = discover_dependencies(clean.artifacts, clean.graph)
    assert result.complete
    # graph Depends-On (ENG->REG) and declared array (ENG deps [REG]) dedupe to one.
    assert result.count() == 1
    dep = result.items[0]
    assert dep.attributes["source_id"] == "UCOS-ENG-000001"
    assert dep.attributes["target_id"] == "UCOS-REG-000001"
    assert dep.attributes["resolved"] is True
    assert tuple(dep.attributes["via"]) == ("declared", "graph")


def test_dependencies_gap_unresolved_target(gapped):
    result = discover_dependencies(gapped.artifacts, gapped.graph)
    assert not result.complete
    assert "UCOS-GHOST" in result.gaps
    ghost = next(i for i in result.items if i.attributes["target_id"] == "UCOS-GHOST")
    assert ghost.attributes["resolved"] is False
    assert tuple(ghost.attributes["via"]) == ("declared",)


# --------------------------------------------------------------------------- evidence


def test_evidence_clean(clean):
    result = discover_evidence(clean.artifacts)
    assert result.complete
    assert result.count() == 3
    item = next(i for i in result.items if i.item_id == "UDEV-UCOS-REG-000001")
    assert item.attributes["has_content_hash"] is True
    assert item.attributes["traced"] is False


def test_evidence_gap_missing_hash(gapped):
    result = discover_evidence(gapped.artifacts)
    assert not result.complete
    assert "UCOS-GAP-EVID" in result.gaps
    item = next(i for i in result.items if i.item_id == "UDEV-UCOS-GAP-EVID")
    assert item.attributes["has_content_hash"] is False


def test_evidence_traceability_surfaced(clean_data_dir, clean_artifacts):
    # Give one artifact a traceability reference and confirm it is discovered.
    import json

    from engine.registry.source import ARTIFACTS_FILE

    records = clean_artifacts
    records[1]["traceability"]["requirement"] = ["UCOS-REQ-1"]
    (clean_data_dir / ARTIFACTS_FILE).write_text(
        json.dumps({"count": len(records), "artifacts": records}), encoding="utf-8"
    )
    adapter = RegistryAdapter.open(clean_data_dir)
    result = discover_evidence(adapter.artifacts)
    item = next(i for i in result.items if i.item_id == "UDEV-UCOS-REG-000001")
    assert item.attributes["traced"] is True
    assert item.references == ("UCOS-REQ-1",)
    assert item.attributes["traceability_stages"] == ["requirement"]


# --------------------------------------------------------------------------- ontology


def test_ontology_clean(clean):
    result = discover_ontology(clean.artifacts, clean.graph)
    assert result.complete  # ontology is complete by construction (derived from usage)
    kinds = {i.attributes["term_kind"] for i in result.items}
    assert kinds == {"relationship_type", "category", "lifecycle_status"}
    rel = next(i for i in result.items if i.item_id == "UDONT-REL-DEPENDS-ON")
    assert rel.attributes["usage"] == 1
    status = next(i for i in result.items if i.item_id == "UDONT-STATUS-ACTIVE")
    assert status.attributes["usage"] == 2


# --------------------------------------------------------------------------- capability


def test_capabilities_clean(clean):
    result = discover_capabilities(clean.artifacts, clean.volumes)
    assert result.complete
    names = {i.name for i in result.items}
    assert names == {"ENG", "UKB"}
    ukb = next(i for i in result.items if i.name == "UKB")
    assert ukb.attributes["member_count"] == 2
    assert ukb.attributes["realized"] is True


def test_capabilities_gap_unrealized_program(gapped):
    result = discover_capabilities(gapped.artifacts, gapped.volumes)
    assert not result.complete
    assert "PLANPROG" in result.gaps
    planprog = next(i for i in result.items if i.name == "PLANPROG")
    assert planprog.attributes["realized"] is False
    assert planprog.attributes["realized_count"] == 0


# --------------------------------------------------------------------------- vocabulary


def test_realized_statuses_are_registry_vocabulary():
    assert REALIZED_STATUSES <= set(LifecycleStatus)
    assert LifecycleStatus.PLANNED not in REALIZED_STATUSES
    assert LifecycleStatus.FROZEN in REALIZED_STATUSES


def test_a_document_without_an_addressable_path_is_counted_as_a_gap() -> None:
    """The schema forbids it, so a document with no path is malformed — and said so.

    ``discover_documents`` treats absence-of-path as a shortfall rather than dropping the
    artifact, because a silent drop is how a dimension reports completeness over records
    that cannot be read back.
    """
    artifact = SimpleNamespace(
        universal_id="UCOS-DOC-000001",
        native_id="DOC-1",
        name="a document",
        path="",
        return_link="#",
        version="1.0.0",
        status=SimpleNamespace(value="ACTIVE"),
        volume="VOL-000",
        category="DOC",
        page_start=1,
        page_end=1,
        parent=None,
    )
    artifacts = SimpleNamespace(all=lambda: [artifact], count=lambda: 1)
    result = discover_documents(artifacts)
    assert result.gaps == ("UCOS-DOC-000001",)


def test_a_registry_file_the_source_cannot_find_is_recorded_as_a_gap() -> None:
    """A registry named by the dimension but missing from the source is a finding, not
    an omission.
    """
    source = SimpleNamespace(exists=lambda name: False)
    empty = SimpleNamespace(all=lambda: [], count=lambda: 0)
    result = discover_registries(source, empty, empty, empty)
    assert result.gaps


def test_the_slug_folds_runs_of_dashes_and_keeps_leading_and_trailing_clean() -> None:
    """_slug collapses repeated separators and refuses to emit them at the ends.

    The dash-state machine has three arms — start, flush, keep — and identifiers built
    from names like "a--b " or "-x-" must normalise to one token, or the registry's slugs
    would multiply under spacing that means nothing.
    """
    assert _slug("a--b") == "A-B"
    assert _slug("  spaced  out ") == "SPACED-OUT"
    assert _slug("-lead and trail-") == "LEAD-AND-TRAIL"
