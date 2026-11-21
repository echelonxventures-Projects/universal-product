"""UCOS-EPIC-014 — Product Intelligence tests (Terminal T5)."""

from __future__ import annotations

from platform.commercial_intelligence.errors import ProductError
from platform.commercial_intelligence.product import (
    OFFERABLE_STATES,
    PRODUCT_TRANSITIONS,
    Product,
    ProductCatalog,
    ProductState,
)
from platform.tests.commercial_helpers import product_a, product_b, product_dev, products

import pytest


def test_lifecycle_vocabulary_and_transition_map_are_closed():
    assert [s.value for s in ProductState] == [
        "proposed",
        "development",
        "general_availability",
        "deprecated",
        "retired",
    ]
    assert PRODUCT_TRANSITIONS[ProductState.RETIRED] == frozenset()
    assert OFFERABLE_STATES == frozenset(
        {ProductState.GENERAL_AVAILABILITY, ProductState.DEPRECATED}
    )


def test_state_parse_rejects_an_unknown_state():
    with pytest.raises(ProductError):
        ProductState.parse("shipping")
    assert ProductState.parse("retired") is ProductState.RETIRED


def test_product_from_mapping_normalizes_and_orders_capabilities():
    product = Product.from_mapping({**product_a(), "capabilities": ["beta", "alpha", "beta"]})
    assert product.capabilities == ("alpha", "beta")
    assert product.offerable
    assert product.digest() == Product.from_mapping(product_a()).digest()


@pytest.mark.parametrize(
    "override",
    [
        {"product_id": ""},
        {"name": ""},
        {"sku": "lower-case"},
        {"sku": "BAD_SKU"},
        {"sku": ""},
        {"version": "1.0"},
        {"version": ""},
    ],
)
def test_product_refuses_a_malformed_definition(override):
    with pytest.raises(ProductError):
        Product.from_mapping({**product_a(), **override})


def test_product_from_mapping_refuses_non_mapping_and_non_sequence_capabilities():
    with pytest.raises(ProductError):
        Product.from_mapping(["not", "a", "mapping"])
    with pytest.raises(ProductError):
        Product.from_mapping({**product_a(), "capabilities": "alpha"})


def test_a_product_without_a_capability_is_not_offerable():
    product = Product.from_mapping({**product_a(), "capabilities": []})
    assert not product.offerable


def test_a_development_product_is_not_offerable():
    assert not Product.from_mapping(product_dev()).offerable


def test_legal_transition_returns_a_new_product_and_preserves_identity():
    product = Product.from_mapping(product_dev())
    promoted = product.transition_to(ProductState.GENERAL_AVAILABILITY)
    assert promoted.state is ProductState.GENERAL_AVAILABILITY
    assert promoted.product_id == product.product_id
    assert promoted.capabilities == product.capabilities
    assert product.state is ProductState.DEVELOPMENT  # immutability preserved


@pytest.mark.parametrize(
    "state,target",
    [
        ("general_availability", "development"),
        ("general_availability", "retired"),
        ("proposed", "general_availability"),
        ("retired", "general_availability"),
        ("deprecated", "general_availability"),
    ],
)
def test_undeclared_transition_is_refused(state, target):
    product = Product.from_mapping({**product_a(), "state": state})
    assert not product.may_transition_to(ProductState.parse(target))
    with pytest.raises(ProductError):
        product.transition_to(ProductState.parse(target))


def test_catalog_orders_by_sku_and_reports_state_counts():
    catalog = ProductCatalog.from_sequence([product_dev(), product_b(), product_a()])
    assert [p.sku for p in catalog.products] == ["PROD-A", "PROD-B", "PROD-D"]
    assert catalog.state_counts()["general_availability"] == 2
    assert catalog.state_counts()["development"] == 1
    assert len(catalog.offerable()) == 2
    assert catalog.to_dict()["total"] == 3


def test_catalog_lookup_by_id_and_sku():
    catalog = ProductCatalog.from_sequence(products())
    assert catalog.get("PROD-A").name == "Product A"
    assert catalog.by_sku("PROD-B").product_id == "PROD-B"
    assert catalog.get("MISSING") is None
    assert catalog.by_sku("MISSING") is None


def test_catalog_refuses_duplicate_identity_or_sku():
    with pytest.raises(ProductError):
        ProductCatalog.from_sequence([product_a(), product_a()])
    with pytest.raises(ProductError):
        ProductCatalog.from_sequence([product_a(), {**product_b(), "sku": "PROD-A"}])


def test_catalog_refuses_a_non_sequence():
    with pytest.raises(ProductError):
        ProductCatalog.from_sequence("PROD-A")
    with pytest.raises(ProductError):
        ProductCatalog.from_sequence({"product_id": "PROD-A"})


def test_empty_catalog_is_legal_but_offers_nothing():
    catalog = ProductCatalog.from_sequence([])
    assert catalog.products == ()
    assert catalog.offerable() == ()
    assert catalog.digest() == ProductCatalog.from_sequence([]).digest()
