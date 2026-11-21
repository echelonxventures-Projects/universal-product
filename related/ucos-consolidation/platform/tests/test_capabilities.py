"""EC2-TASK-000061 — Platform capability model tests."""

from __future__ import annotations

from platform.foundation.capabilities import (
    Capability,
    CapabilityCatalog,
    CapabilityKind,
    default_capability_catalog,
    default_engine_capabilities,
    default_platform_capabilities,
)
from platform.foundation.contracts import ContractRef
from platform.foundation.errors import CapabilityError

import pytest


def test_engine_capability_requires_contract():
    with pytest.raises(CapabilityError):
        Capability("X", "x", CapabilityKind.ENGINE)


def test_platform_capability_forbids_contract():
    with pytest.raises(CapabilityError):
        Capability("X", "x", CapabilityKind.PLATFORM, engine_contract=ContractRef("e", "1.0.0"))


def test_capability_requires_id():
    with pytest.raises(CapabilityError):
        Capability("", "x", CapabilityKind.PLATFORM)


def test_default_engine_capabilities_map_to_certified_thirteen():
    caps = default_engine_capabilities()
    assert len(caps) == 13
    names = {c.name for c in caps}
    assert "Registry Resolution" in names
    assert "Certification Ledger" in names
    assert all(c.kind is CapabilityKind.ENGINE and c.engine_contract for c in caps)


def test_default_platform_capabilities_are_eighteen():
    caps = default_platform_capabilities()
    assert len(caps) == 18
    assert all(c.kind is CapabilityKind.PLATFORM for c in caps)
    assert {c.capability_id for c in caps} >= {"PC-01", "PC-18"}


def test_default_catalog_is_seeded_and_valid():
    catalog = default_capability_catalog()
    assert len(catalog) == 31
    assert len(catalog.of_kind(CapabilityKind.ENGINE)) == 13
    assert len(catalog.of_kind(CapabilityKind.PLATFORM)) == 18
    catalog.validate()  # does not raise
    assert catalog.get("ENG-CAP-01").name == "Registry Resolution"


def test_duplicate_capability_rejected():
    catalog = CapabilityCatalog()
    catalog.register(Capability("PC-01", "x", CapabilityKind.PLATFORM))
    with pytest.raises(CapabilityError):
        catalog.register(Capability("PC-01", "y", CapabilityKind.PLATFORM))


def test_unknown_capability_lookup_raises():
    catalog = CapabilityCatalog()
    with pytest.raises(CapabilityError):
        catalog.get("nope")


def test_catalog_contains_operator():
    catalog = default_capability_catalog()
    assert "PC-01" in catalog
    assert "NOPE" not in catalog


def test_capability_order_is_dependency_honest():
    catalog = CapabilityCatalog()
    catalog.register(Capability("B", "b", CapabilityKind.PLATFORM, depends_on=("A",)))
    catalog.register(Capability("A", "a", CapabilityKind.PLATFORM))
    order = catalog.order()
    assert order.index("A") < order.index("B")


def test_catalog_to_dict():
    catalog = default_capability_catalog()
    d = catalog.to_dict()
    assert d["capability_count"] == 31
    assert "ENG-CAP-01" in {c["capability_id"] for c in d["capabilities"]}
