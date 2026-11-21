"""Tests for the Universal Provider Framework facade over the kernel."""

from __future__ import annotations

import pytest

from engine.foundation.contracts.contract import Version
from engine.kernel.errors import GovernanceRejection
from engine.kernel.meta import MetaObject
from engine.provider.errors import (
    ProviderCategoryUnknownError,
    ProviderContractError,
    ProviderResolutionError,
)
from engine.provider.framework import NegotiationResult, ProviderFramework
from engine.provider.metatypes import (
    CATEGORY_ROLE,
    PROVIDER_INSTANCE_NS,
    PROVIDER_META_NS,
    facet_keys,
)


@pytest.fixture
def fw():
    return ProviderFramework()


def _reg(fw, category="StorageProvider", key="s1", cap="storage.persist", version="1.0.0", **kw):
    if category not in fw.category_keys():
        fw.register_category(category)
    return fw.register_provider(
        category=category,
        key=key,
        capabilities=[cap],
        contract={"name": f"{category}.contract", "version": version},
        health=kw.pop("health", {"status": "serving"}),
        **kw,
    )


def test_facets_seeded_as_metatypes(fw):
    keys = set(fw.kernel.registry.metatype_keys())
    for facet in facet_keys():
        assert facet in keys
    # facets live in the provider meta namespace
    meta = [m for m in fw.kernel.metatypes() if m.namespace == PROVIDER_META_NS]
    assert len(meta) == len(facet_keys())


def test_register_category_is_open_and_marked(fw):
    before = len(fw.categories())
    cat = fw.register_category("NovelProvider", description="x")
    assert cat.attributes["role"] == CATEGORY_ROLE
    assert len(fw.categories()) == before + 1
    assert "NovelProvider" in fw.category_keys()


def test_register_provider_and_classify(fw):
    p = _reg(fw)
    assert p.namespace == PROVIDER_INSTANCE_NS
    assert p.metatype == "StorageProvider"
    assert p.attributes["capabilities"] == ["storage.persist"]
    assert p.attributes["contract"]["version"] == "1.0.0"
    assert fw.kernel.classify(p.identity) == "StorageProvider"


def test_register_provider_unknown_category_raises(fw):
    with pytest.raises(ProviderCategoryUnknownError):
        fw.register_provider(
            category="Nope",
            key="x",
            capabilities=["c"],
            contract={"name": "n", "version": "1.0.0"},
        )


def test_register_provider_requires_capability(fw):
    fw.register_category("StorageProvider")
    with pytest.raises(ProviderContractError):
        fw.register_provider(
            category="StorageProvider",
            key="x",
            capabilities=[],
            contract={"name": "n", "version": "1.0.0"},
        )


def test_register_provider_requires_wellformed_contract(fw):
    fw.register_category("StorageProvider")
    with pytest.raises(ProviderContractError):
        fw.register_provider(
            category="StorageProvider",
            key="x",
            capabilities=["c"],
            contract={"name": "", "version": "1.0.0"},
        )
    with pytest.raises(ProviderContractError):
        fw.register_provider(
            category="StorageProvider",
            key="y",
            capabilities=["c"],
            contract={"name": "n", "version": "not-a-version"},
        )


def test_relationships_recorded(fw):
    _reg(fw, key="dep")
    p = _reg(
        fw,
        key="s2",
        dependencies=["UMK-DEP-000000000000"],
        policy_bindings=["policy-x"],
        context_bindings=["ctx-1"],
    )
    assert "UMK-DEP-000000000000" in p.related("depends-on")
    assert "policy-x" in p.related("bound-policy")
    assert "ctx-1" in p.related("bound-context")


def test_providers_filter_by_category(fw):
    _reg(fw, category="StorageProvider", key="s1")
    fw.register_category("DatabaseProvider")
    _reg(fw, category="DatabaseProvider", key="d1", cap="database.query")
    assert len(fw.providers()) == 2
    assert len(fw.providers(category="StorageProvider")) == 1


def test_discover_by_capability_and_context(fw):
    _reg(fw, key="s1", cap="storage.persist", context_bindings=["ctx-1"])
    _reg(fw, key="s2", cap="storage.persist")
    assert len(fw.discover(capability="storage.persist")) == 2
    assert len(fw.discover(capability="storage.persist", context="ctx-1")) == 1
    assert fw.discover(capability="nonexistent") == ()


def test_resolve_selects_highest_version(fw):
    _reg(fw, key="s1", version="1.0.0")
    _reg(fw, key="s2", version="2.0.0")
    best = fw.resolve("storage.persist")
    assert best.attributes["contract"]["version"] == "2.0.0"


def test_resolve_no_compatible_raises(fw):
    with pytest.raises(ProviderResolutionError):
        fw.resolve("no.such.capability")


def test_resolve_with_min_version_filters(fw):
    _reg(fw, key="s1", version="1.0.0")
    with pytest.raises(ProviderResolutionError):
        fw.resolve("storage.persist", requirements={"min_version": "2.0.0"})


def test_negotiate_compatible_and_incompatible(fw):
    p = _reg(fw, key="s1", version="1.2.0")
    ok = fw.negotiate(
        {
            "capability": "storage.persist",
            "contract": "StorageProvider.contract",
            "min_version": "1.0.0",
        },
        p,
    )
    assert ok.compatible is True
    assert "storage.persist" in ok.matched_capabilities
    bad = fw.negotiate({"capability": "other", "contract": "wrong", "min_version": "9.0.0"}, p)
    assert bad.compatible is False
    assert len(bad.reasons) == 3
    d = bad.to_dict()
    assert d["compatible"] is False


def test_compatible_handles_malformed_versions(fw):
    p = _reg(fw, key="s1", version="1.0.0")
    assert fw.compatible("1.0.0", p) is True
    assert fw.compatible("bad", p) is False


def test_transition_lifecycle_records_new_version(fw):
    p = _reg(fw, key="s1")
    assert p.attributes["lifecycle"] == "registered"
    active = fw.transition(p.identity, "active")
    assert active.attributes["lifecycle"] == "active"
    assert active.version == Version(1, 0, 1)
    assert p.identity == active.identity


def test_health_reports_serving_and_unavailable(fw):
    up = _reg(fw, key="s1", health={"status": "serving"})
    down = _reg(fw, key="s2", health={"status": "unavailable"})
    assert fw.health(up.identity)["serving"] is True
    assert fw.health(down.identity)["serving"] is False


def test_health_default_unknown(fw):
    fw.register_category("StorageProvider")
    p = fw.register_provider(
        category="StorageProvider",
        key="s1",
        capabilities=["c"],
        contract={"name": "n", "version": "1.0.0"},
    )
    assert fw.health(p.identity)["status"] == "unknown"


def test_compose_and_trace(fw):
    a = _reg(fw, key="s1")
    b = _reg(fw, key="s2")
    composed = fw.compose(a.identity, "peers", b.identity)
    assert b.identity in composed.related("peers")
    assert fw.trace(a.identity)["identity"] == a.identity


def test_select_unavailable_ranked_last(fw):
    up = _reg(fw, key="s1", version="1.0.0", health={"status": "serving"})
    down = _reg(fw, key="s2", version="9.0.0", health={"status": "unavailable"})
    ordered = fw.select([down, up], requirements={})
    assert ordered[0].identity == up.identity  # serving beats a higher-version unavailable


def test_validate_and_certify(fw):
    _reg(fw)
    assert fw.validate() is True
    cert = fw.certify()
    assert cert["determination"] == "CERTIFIED"
    assert cert["providers"] == 1


def test_describe(fw):
    d = fw.describe()
    assert d["open_world"] is True
    assert d["realizes_over_kernel"]
    assert "StorageProvider" not in d["categories"]  # none registered yet


def test_governance_constraint_provider_has_category(fw):
    # Register a NON-category meta-type, then attempt a provider instance under it.
    fw.kernel.register_metatype("PlainType", namespace="umk.demo")
    candidate = MetaObject(
        metatype="PlainType",
        namespace=PROVIDER_INSTANCE_NS,
        natural_key="rogue",
        attributes={"capabilities": ["c"], "contract": {"name": "n", "version": "1.0.0"}},
    )
    with pytest.raises(GovernanceRejection):
        fw.kernel.registry.register(candidate)


def test_governance_constraint_capability_and_contract(fw):
    fw.register_category("StorageProvider")
    no_cap = MetaObject(
        metatype="StorageProvider",
        namespace=PROVIDER_INSTANCE_NS,
        natural_key="nocap",
        attributes={"capabilities": [], "contract": {"name": "n", "version": "1.0.0"}},
    )
    with pytest.raises(GovernanceRejection):
        fw.kernel.registry.register(no_cap)
    no_contract = MetaObject(
        metatype="StorageProvider",
        namespace=PROVIDER_INSTANCE_NS,
        natural_key="nocontract",
        attributes={"capabilities": ["c"], "contract": {}},
    )
    with pytest.raises(GovernanceRejection):
        fw.kernel.registry.register(no_contract)


def test_negotiation_result_type(fw):
    p = _reg(fw)
    r = fw.negotiate({"capability": "storage.persist"}, p)
    assert isinstance(r, NegotiationResult)
    assert r.compatible is True
