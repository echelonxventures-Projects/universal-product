"""UCOS-EPIC-014 — Marketplace Intelligence (Terminal T5).

A **listing** is the governed publication of a product into a marketplace. Publication is
never a free action: a listing may only reach ``published`` through the declared listing
lifecycle, and only when the product it names is offerable, the commercial package it
names is present, and the publication was governed (policy + approval) — those latter two
conditions are asserted by the package and governance domains and consumed here by
reference, so this module duplicates no governance logic.

Marketplace Intelligence answers, deterministically, from declared facts:

    * is every listing well-formed and does it name a product that exists in the catalog;
    * is every listing in a state it could legally have reached; and
    * is every *published* listing backed by an offerable product (no phantom offer).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from platform.commercial_intelligence.errors import MarketplaceError
from platform.commercial_intelligence.product import ProductCatalog
from platform.foundation.contracts import content_hash
from typing import Any

#: A listing identity is a stable, lower-case dash-separated slug.
LISTING_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ListingState(str, Enum):
    """The closed marketplace listing lifecycle vocabulary, in lifecycle order."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"
    DELISTED = "delisted"

    @classmethod
    def parse(cls, value: Any) -> ListingState:
        try:
            return cls(value)
        except ValueError as exc:
            raise MarketplaceError(
                "unknown marketplace listing state",
                state=value,
                supported=[s.value for s in cls],
            ) from exc


#: The only legal listing transitions. ``delisted`` is terminal: a delisted listing is
#: never resurrected, so a consumer can never observe an offer that was governed away.
LISTING_TRANSITIONS: Mapping[ListingState, frozenset[ListingState]] = {
    ListingState.DRAFT: frozenset({ListingState.SUBMITTED, ListingState.DELISTED}),
    ListingState.SUBMITTED: frozenset({ListingState.PUBLISHED, ListingState.DRAFT}),
    ListingState.PUBLISHED: frozenset({ListingState.WITHDRAWN}),
    ListingState.WITHDRAWN: frozenset({ListingState.SUBMITTED, ListingState.DELISTED}),
    ListingState.DELISTED: frozenset(),
}

#: The states in which a listing is visible to a consumer.
VISIBLE_STATES = frozenset({ListingState.PUBLISHED})


@dataclass(frozen=True, slots=True)
class Listing:
    """An immutable marketplace listing: a governed publication of one product."""

    listing_id: str
    product_id: str
    seller_id: str
    state: ListingState
    package_id: str = ""

    def __post_init__(self) -> None:
        if not LISTING_ID_PATTERN.match(self.listing_id or ""):
            raise MarketplaceError(
                "a listing requires a lower-case dash-separated listing_id",
                listing_id=self.listing_id,
            )
        if not self.product_id:
            raise MarketplaceError(
                "a listing requires the product_id it publishes", listing_id=self.listing_id
            )
        if not self.seller_id:
            raise MarketplaceError(
                "a listing requires an accountable seller_id", listing_id=self.listing_id
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> Listing:
        if not isinstance(raw, Mapping):
            raise MarketplaceError("a listing must be a mapping")
        return cls(
            listing_id=str(raw.get("listing_id") or ""),
            product_id=str(raw.get("product_id") or ""),
            seller_id=str(raw.get("seller_id") or ""),
            state=ListingState.parse(raw.get("state")),
            package_id=str(raw.get("package_id") or ""),
        )

    @property
    def visible(self) -> bool:
        return self.state in VISIBLE_STATES

    def may_transition_to(self, target: ListingState) -> bool:
        return target in LISTING_TRANSITIONS[self.state]

    def transition_to(self, target: ListingState) -> Listing:
        """Return the listing in ``target`` state, refusing an undeclared transition."""
        if not self.may_transition_to(target):
            raise MarketplaceError(
                "undeclared marketplace listing transition",
                listing_id=self.listing_id,
                current=self.state.value,
                requested=target.value,
                permitted=sorted(s.value for s in LISTING_TRANSITIONS[self.state]),
            )
        return Listing(
            listing_id=self.listing_id,
            product_id=self.product_id,
            seller_id=self.seller_id,
            state=target,
            package_id=self.package_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "listing_id": self.listing_id,
            "product_id": self.product_id,
            "seller_id": self.seller_id,
            "state": self.state.value,
            "package_id": self.package_id,
            "visible": self.visible,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ListingIntegrity:
    """The deterministic verdict on one listing against the product catalog."""

    listing_id: str
    sound: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "listing_id": self.listing_id,
            "sound": self.sound,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class MarketplaceRegistry:
    """An immutable, deterministically ordered marketplace listing set."""

    listings: tuple[Listing, ...] = ()

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for listing in self.listings:
            if listing.listing_id in seen:
                raise MarketplaceError(
                    "duplicate listing_id in registry", listing_id=listing.listing_id
                )
            seen.add(listing.listing_id)

    @classmethod
    def from_sequence(cls, raw: Any) -> MarketplaceRegistry:
        if isinstance(raw, str | bytes) or not isinstance(raw, Sequence):
            raise MarketplaceError("a marketplace registry must be a sequence of listings")
        listings = tuple(
            sorted(
                (Listing.from_mapping(item) for item in raw),
                key=lambda listing: listing.listing_id,
            )
        )
        return cls(listings=listings)

    def get(self, listing_id: str) -> Listing | None:
        for listing in self.listings:
            if listing.listing_id == listing_id:
                return listing
        return None

    def visible(self) -> tuple[Listing, ...]:
        return tuple(listing for listing in self.listings if listing.visible)

    def state_counts(self) -> dict[str, int]:
        return {
            state.value: sum(1 for listing in self.listings if listing.state is state)
            for state in ListingState
        }

    def integrity(self, catalog: ProductCatalog) -> tuple[ListingIntegrity, ...]:
        """Verify every listing against the catalog; a published phantom offer is unsound."""
        verdicts: list[ListingIntegrity] = []
        for listing in self.listings:
            reasons: list[str] = []
            product = catalog.get(listing.product_id)
            if product is None:
                reasons.append(f"names product {listing.product_id} which is not in the catalog")
            elif listing.visible and not product.offerable:
                reasons.append(
                    f"published while product {product.product_id} is not offerable "
                    f"(state {product.state.value}, {len(product.capabilities)} capabilities)"
                )
            if listing.visible and not listing.package_id:
                reasons.append("published without naming the commercial package it publishes")
            verdicts.append(
                ListingIntegrity(
                    listing_id=listing.listing_id, sound=not reasons, reasons=tuple(reasons)
                )
            )
        return tuple(verdicts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "listings": [listing.to_dict() for listing in self.listings],
            "total": len(self.listings),
            "visible": len(self.visible()),
            "state_counts": self.state_counts(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "LISTING_ID_PATTERN",
    "ListingState",
    "LISTING_TRANSITIONS",
    "VISIBLE_STATES",
    "Listing",
    "ListingIntegrity",
    "MarketplaceRegistry",
]
