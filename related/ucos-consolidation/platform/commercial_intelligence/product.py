"""UCOS-EPIC-014 — Product Intelligence (Terminal T5).

A **product** is the commercially offerable unit: a stable identity, a stable SKU, a
semantic version, a lifecycle state, and the set of platform capabilities it offers. The
lifecycle is an explicit, closed state machine — a transition that is not declared is
refused rather than silently applied, so a product can never be marketed in a state it
never legally reached.

Product Intelligence answers three questions deterministically from declared facts:

    * is every declared product *well-formed* (identity, SKU shape, version, capabilities);
    * is every declared lifecycle transition *legal* under the closed transition map; and
    * is a product *offerable* — i.e. generally available, with at least one capability.

Nothing here knows a specific product, market or technology: the product set is data.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from platform.commercial_intelligence.errors import ProductError
from platform.foundation.contracts import content_hash
from typing import Any

#: A SKU is an upper-case, dash/dot-separated stable commercial code.
SKU_PATTERN = re.compile(r"^[A-Z0-9]+(?:[-.][A-Z0-9]+)*$")

#: A version is a dotted numeric triple (the repository's semantic-version discipline).
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


class ProductState(str, Enum):
    """The closed product lifecycle vocabulary, in lifecycle order."""

    PROPOSED = "proposed"
    DEVELOPMENT = "development"
    GENERAL_AVAILABILITY = "general_availability"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

    @classmethod
    def parse(cls, value: Any) -> ProductState:
        try:
            return cls(value)
        except ValueError as exc:
            raise ProductError(
                "unknown product lifecycle state",
                state=value,
                supported=[s.value for s in cls],
            ) from exc


#: The only legal product lifecycle transitions. A retired product is terminal: it may
#: never be re-offered under the same identity (that would break commercial traceability).
PRODUCT_TRANSITIONS: Mapping[ProductState, frozenset[ProductState]] = {
    ProductState.PROPOSED: frozenset({ProductState.DEVELOPMENT, ProductState.RETIRED}),
    ProductState.DEVELOPMENT: frozenset({ProductState.GENERAL_AVAILABILITY, ProductState.RETIRED}),
    ProductState.GENERAL_AVAILABILITY: frozenset({ProductState.DEPRECATED}),
    ProductState.DEPRECATED: frozenset({ProductState.RETIRED}),
    ProductState.RETIRED: frozenset(),
}

#: The states in which a product may legally be offered to a customer.
OFFERABLE_STATES = frozenset({ProductState.GENERAL_AVAILABILITY, ProductState.DEPRECATED})


@dataclass(frozen=True, slots=True)
class Product:
    """An immutable, offerable product definition."""

    product_id: str
    name: str
    sku: str
    version: str
    state: ProductState
    #: The **set** of capabilities the product offers, normalized: de-duplicated and
    #: ordered. A capability is either offered or it is not; offering it twice is not a
    #: different commercial fact, so a repeated declaration must not produce a different
    #: product identity (:meth:`digest`).
    capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.product_id:
            raise ProductError("a product requires a non-empty product_id")
        if not self.name:
            raise ProductError("a product requires a name", product_id=self.product_id)
        if not SKU_PATTERN.match(self.sku or ""):
            raise ProductError(
                "a product requires an upper-case dash/dot-separated SKU",
                product_id=self.product_id,
                sku=self.sku,
            )
        if not VERSION_PATTERN.match(self.version or ""):
            raise ProductError(
                "a product requires a dotted numeric version (major.minor.patch)",
                product_id=self.product_id,
                version=self.version,
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> Product:
        """Assimilate a mapping into an immutable :class:`Product`."""
        if not isinstance(raw, Mapping):
            raise ProductError("a product must be a mapping")
        capabilities = raw.get("capabilities", ())
        if isinstance(capabilities, str) or not isinstance(capabilities, Sequence):
            raise ProductError(
                "product capabilities must be a sequence",
                product_id=raw.get("product_id"),
            )
        return cls(
            product_id=str(raw.get("product_id") or ""),
            name=str(raw.get("name") or ""),
            sku=str(raw.get("sku") or ""),
            version=str(raw.get("version") or ""),
            state=ProductState.parse(raw.get("state")),
            capabilities=tuple(sorted({str(c) for c in capabilities})),
        )

    @property
    def offerable(self) -> bool:
        """True iff the product may legally be offered and offers at least one capability."""
        return self.state in OFFERABLE_STATES and bool(self.capabilities)

    def may_transition_to(self, target: ProductState) -> bool:
        return target in PRODUCT_TRANSITIONS[self.state]

    def transition_to(self, target: ProductState) -> Product:
        """Return the product in ``target`` state, refusing an undeclared transition."""
        if not self.may_transition_to(target):
            raise ProductError(
                "undeclared product lifecycle transition",
                product_id=self.product_id,
                current=self.state.value,
                requested=target.value,
                permitted=sorted(s.value for s in PRODUCT_TRANSITIONS[self.state]),
            )
        return Product(
            product_id=self.product_id,
            name=self.name,
            sku=self.sku,
            version=self.version,
            state=target,
            capabilities=self.capabilities,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "sku": self.sku,
            "version": self.version,
            "state": self.state.value,
            "capabilities": list(self.capabilities),
            "offerable": self.offerable,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ProductCatalog:
    """An immutable, deterministically ordered set of products with unique identity."""

    products: tuple[Product, ...] = ()

    def __post_init__(self) -> None:
        seen_ids: set[str] = set()
        seen_skus: set[str] = set()
        for product in self.products:
            if product.product_id in seen_ids:
                raise ProductError("duplicate product_id in catalog", product_id=product.product_id)
            if product.sku in seen_skus:
                raise ProductError("duplicate SKU in catalog", sku=product.sku)
            seen_ids.add(product.product_id)
            seen_skus.add(product.sku)

    @classmethod
    def from_sequence(cls, raw: Any) -> ProductCatalog:
        """Assimilate a sequence of product mappings, in canonical (SKU) order."""
        if isinstance(raw, str | bytes) or not isinstance(raw, Sequence):
            raise ProductError("a product catalog must be a sequence of products")
        products = tuple(sorted((Product.from_mapping(item) for item in raw), key=lambda p: p.sku))
        return cls(products=products)

    def get(self, product_id: str) -> Product | None:
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def by_sku(self, sku: str) -> Product | None:
        for product in self.products:
            if product.sku == sku:
                return product
        return None

    def offerable(self) -> tuple[Product, ...]:
        return tuple(p for p in self.products if p.offerable)

    def state_counts(self) -> dict[str, int]:
        return {
            state.value: sum(1 for p in self.products if p.state is state) for state in ProductState
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "products": [p.to_dict() for p in self.products],
            "total": len(self.products),
            "offerable": len(self.offerable()),
            "state_counts": self.state_counts(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "SKU_PATTERN",
    "VERSION_PATTERN",
    "ProductState",
    "PRODUCT_TRANSITIONS",
    "OFFERABLE_STATES",
    "Product",
    "ProductCatalog",
]
