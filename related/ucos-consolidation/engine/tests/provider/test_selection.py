"""Tests for the open provider selection-strategy registry."""

from __future__ import annotations

import pytest

from engine.provider.framework import ProviderFramework
from engine.provider.selection import (
    DEFAULT_STRATEGY,
    get_strategy,
    highest_version,
    register_strategy,
    strategy_names,
)


def _providers():
    fw = ProviderFramework()
    fw.register_category("StorageProvider")
    a = fw.register_provider(
        category="StorageProvider",
        key="a",
        capabilities=["c"],
        contract={"name": "n", "version": "1.0.0"},
        health={"status": "serving"},
    )
    b = fw.register_provider(
        category="StorageProvider",
        key="b",
        capabilities=["c"],
        contract={"name": "n", "version": "2.0.0"},
        health={"status": "serving"},
    )
    return a, b


def test_default_strategy_registered():
    assert DEFAULT_STRATEGY in strategy_names()
    assert get_strategy(DEFAULT_STRATEGY) is highest_version


def test_highest_version_orders_desc():
    a, b = _providers()
    ordered = highest_version([a, b], {})
    assert [p.attributes["contract"]["version"] for p in ordered] == ["2.0.0", "1.0.0"]


def test_malformed_version_sorts_lowest():
    fw = ProviderFramework()
    fw.register_category("StorageProvider")
    good = fw.register_provider(
        category="StorageProvider",
        key="good",
        capabilities=["c"],
        contract={"name": "n", "version": "1.0.0"},
        health={"status": "serving"},
    )
    # A provider whose stored contract version is malformed sorts below any valid version.
    from engine.kernel.meta import MetaObject

    bad = MetaObject(
        metatype="StorageProvider",
        namespace="umk.provider.instance",
        natural_key="bad",
        attributes={
            "capabilities": ["c"],
            "contract": {"name": "n", "version": "x"},
            "health": {"status": "serving"},
        },
    )
    ordered = highest_version([bad, good], {})
    assert ordered[0].identity == good.identity


def test_register_duplicate_strategy_rejected():
    with pytest.raises(ValueError):
        register_strategy(DEFAULT_STRATEGY, highest_version)


def test_register_and_use_custom_strategy():
    def reverse_by_id(candidates, _requirements):
        return sorted(candidates, key=lambda p: p.identity, reverse=True)

    register_strategy("reverse-id-unique", reverse_by_id)
    assert "reverse-id-unique" in strategy_names()
    a, b = _providers()
    ordered = get_strategy("reverse-id-unique")([a, b], {})
    assert ordered == sorted([a, b], key=lambda p: p.identity, reverse=True)
