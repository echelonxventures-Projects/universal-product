"""UCOS-EPIC-014 — Pricing Intelligence (Terminal T5).

A **quote** is the only priced commitment this platform makes, so it is computed, never
estimated: every amount is an integer count of minor units, every discount is expressed
in basis points, and rounding is half-up on the magnitude. An identical price book, an
identical discount set and an identical request therefore produce a byte-identical quote
on every machine.

Pricing Intelligence enforces three commercial invariants structurally:

    * **one currency per price book** — a book may not mix currencies, so a quote can
      never silently combine them;
    * **a bounded discount** — the cumulative discount applied to a line may not exceed
      the book's declared maximum, and a request that would exceed it is refused rather
      than quietly capped; and
    * **no negative net** — a quote line's net amount is never below zero.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from platform.commercial_intelligence.contracts import BASIS_POINTS_SCALE, Money, sum_money
from platform.commercial_intelligence.errors import PricingError
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class DiscountRule:
    """An immutable, quantity-gated discount expressed in basis points."""

    rule_id: str
    basis_points: int
    min_quantity: int = 1

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise PricingError("a discount rule requires a non-empty rule_id")
        if (
            isinstance(self.basis_points, bool)
            or not isinstance(self.basis_points, int)
            or not 0 <= self.basis_points <= BASIS_POINTS_SCALE
        ):
            raise PricingError(
                "a discount must be an integer between 0 and 10000 basis points",
                rule_id=self.rule_id,
                basis_points=repr(self.basis_points),
            )
        if (
            isinstance(self.min_quantity, bool)
            or not isinstance(self.min_quantity, int)
            or self.min_quantity < 1
        ):
            raise PricingError(
                "a discount rule requires an integer minimum quantity of at least one",
                rule_id=self.rule_id,
                min_quantity=repr(self.min_quantity),
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> DiscountRule:
        if not isinstance(raw, Mapping):
            raise PricingError("a discount rule must be a mapping")
        return cls(
            rule_id=str(raw.get("rule_id") or ""),
            basis_points=raw.get("basis_points"),
            min_quantity=raw.get("min_quantity", 1),
        )

    def applies_to(self, quantity: int) -> bool:
        return quantity >= self.min_quantity

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "basis_points": self.basis_points,
            "min_quantity": self.min_quantity,
        }


@dataclass(frozen=True, slots=True)
class PriceBook:
    """An immutable, single-currency list-price book with a bounded discount authority."""

    book_id: str
    currency: str
    prices: Mapping[str, Money]
    discounts: tuple[DiscountRule, ...] = ()
    max_discount_basis_points: int = BASIS_POINTS_SCALE

    def __post_init__(self) -> None:
        if not self.book_id:
            raise PricingError("a price book requires a non-empty book_id")
        if not self.prices:
            raise PricingError("a price book requires at least one price", book_id=self.book_id)
        for sku, amount in self.prices.items():
            if amount.currency != self.currency:
                raise PricingError(
                    "a price book may not mix currencies",
                    book_id=self.book_id,
                    sku=sku,
                    book_currency=self.currency,
                    price_currency=amount.currency,
                )
            if amount.is_negative:
                raise PricingError(
                    "a list price may not be negative", book_id=self.book_id, sku=sku
                )
        if (
            isinstance(self.max_discount_basis_points, bool)
            or not isinstance(self.max_discount_basis_points, int)
            or not 0 <= self.max_discount_basis_points <= BASIS_POINTS_SCALE
        ):
            raise PricingError(
                "the maximum discount must be an integer between 0 and 10000 basis points",
                book_id=self.book_id,
                max_discount_basis_points=repr(self.max_discount_basis_points),
            )
        seen: set[str] = set()
        for rule in self.discounts:
            if rule.rule_id in seen:
                raise PricingError(
                    "duplicate discount rule_id in price book",
                    book_id=self.book_id,
                    rule_id=rule.rule_id,
                )
            seen.add(rule.rule_id)

    @classmethod
    def from_mapping(cls, raw: Any) -> PriceBook:
        """Assimilate ``{book_id, currency, prices, discounts, max_discount_basis_points}``."""
        if not isinstance(raw, Mapping):
            raise PricingError("a price book must be a mapping")
        book_id = str(raw.get("book_id") or "")
        currency = str(raw.get("currency") or "")
        raw_prices = raw.get("prices")
        if not isinstance(raw_prices, Mapping):
            raise PricingError(
                "price book prices must be a mapping of SKU to amount", book_id=book_id
            )
        prices = {
            str(sku): Money.from_mapping(amount, context=f"{book_id}:{sku}")
            for sku, amount in sorted(raw_prices.items())
        }
        raw_discounts = raw.get("discounts", ())
        if isinstance(raw_discounts, str | bytes) or not isinstance(raw_discounts, Sequence):
            raise PricingError("price book discounts must be a sequence", book_id=book_id)
        discounts = tuple(
            sorted(
                (DiscountRule.from_mapping(item) for item in raw_discounts),
                key=lambda rule: rule.rule_id,
            )
        )
        return cls(
            book_id=book_id,
            currency=currency,
            prices=prices,
            discounts=discounts,
            max_discount_basis_points=raw.get("max_discount_basis_points", BASIS_POINTS_SCALE),
        )

    def price_of(self, sku: str) -> Money | None:
        return self.prices.get(sku)

    def discount(self, rule_id: str) -> DiscountRule | None:
        for rule in self.discounts:
            if rule.rule_id == rule_id:
                return rule
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "book_id": self.book_id,
            "currency": self.currency,
            "prices": {sku: amount.to_dict() for sku, amount in sorted(self.prices.items())},
            "discounts": [rule.to_dict() for rule in self.discounts],
            "max_discount_basis_points": self.max_discount_basis_points,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class QuoteLineRequest:
    """A request for one priced line: a SKU, a quantity, and the discounts claimed."""

    sku: str
    quantity: int
    discount_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.sku:
            raise PricingError("a quote line requires a SKU")
        if (
            isinstance(self.quantity, bool)
            or not isinstance(self.quantity, int)
            or self.quantity < 1
        ):
            raise PricingError(
                "a quote line requires an integer quantity of at least one",
                sku=self.sku,
                quantity=repr(self.quantity),
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> QuoteLineRequest:
        if not isinstance(raw, Mapping):
            raise PricingError("a quote line request must be a mapping")
        discount_ids = raw.get("discount_ids", ())
        if isinstance(discount_ids, str) or not isinstance(discount_ids, Sequence):
            raise PricingError("quote line discount_ids must be a sequence", sku=raw.get("sku"))
        return cls(
            sku=str(raw.get("sku") or ""),
            quantity=raw.get("quantity"),
            discount_ids=tuple(sorted(str(d) for d in discount_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "quantity": self.quantity,
            "discount_ids": list(self.discount_ids),
        }


@dataclass(frozen=True, slots=True)
class QuoteLine:
    """An immutable priced quote line: list, discount and net, all in integer minor units."""

    sku: str
    quantity: int
    unit_price: Money
    list_amount: Money
    discount_basis_points: int
    discount_amount: Money
    net_amount: Money
    applied_discounts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "quantity": self.quantity,
            "unit_price": self.unit_price.to_dict(),
            "list_amount": self.list_amount.to_dict(),
            "discount_basis_points": self.discount_basis_points,
            "discount_amount": self.discount_amount.to_dict(),
            "net_amount": self.net_amount.to_dict(),
            "applied_discounts": list(self.applied_discounts),
        }


@dataclass(frozen=True, slots=True)
class Quote:
    """The immutable, content-addressed result of pricing a request against a book."""

    quote_id: str
    book_id: str
    currency: str
    lines: tuple[QuoteLine, ...]
    list_total: Money
    discount_total: Money
    net_total: Money

    @property
    def effective_discount_basis_points(self) -> int:
        """The realised discount over the whole quote, in basis points (0 when list is 0)."""
        if self.list_total.is_zero:
            return 0
        return self.discount_total.minor_units * BASIS_POINTS_SCALE // self.list_total.minor_units

    def to_dict(self) -> dict[str, Any]:
        return {
            "quote_id": self.quote_id,
            "book_id": self.book_id,
            "currency": self.currency,
            "lines": [line.to_dict() for line in self.lines],
            "list_total": self.list_total.to_dict(),
            "discount_total": self.discount_total.to_dict(),
            "net_total": self.net_total.to_dict(),
            "effective_discount_basis_points": self.effective_discount_basis_points,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def price_line(book: PriceBook, request: QuoteLineRequest) -> QuoteLine:
    """Price one line against ``book``, refusing anything the book does not authorise."""
    unit_price = book.price_of(request.sku)
    if unit_price is None:
        raise PricingError(
            "the price book carries no price for the requested SKU",
            book_id=book.book_id,
            sku=request.sku,
        )
    applied: list[str] = []
    basis_points = 0
    for rule_id in request.discount_ids:
        rule = book.discount(rule_id)
        if rule is None:
            raise PricingError(
                "the price book does not declare the claimed discount",
                book_id=book.book_id,
                rule_id=rule_id,
            )
        if not rule.applies_to(request.quantity):
            raise PricingError(
                "the claimed discount requires a higher quantity",
                book_id=book.book_id,
                rule_id=rule_id,
                min_quantity=rule.min_quantity,
                quantity=request.quantity,
            )
        basis_points += rule.basis_points
        applied.append(rule_id)
    if basis_points > book.max_discount_basis_points:
        raise PricingError(
            "the cumulative discount exceeds the price book's discount authority",
            book_id=book.book_id,
            sku=request.sku,
            requested_basis_points=basis_points,
            max_discount_basis_points=book.max_discount_basis_points,
        )
    list_amount = unit_price.scale(request.quantity)
    discount_amount = list_amount.apply_basis_points(basis_points)
    net_amount = list_amount.subtract(discount_amount)
    if net_amount.is_negative:
        raise PricingError(
            "a quote line's net amount may not be negative",
            book_id=book.book_id,
            sku=request.sku,
        )
    return QuoteLine(
        sku=request.sku,
        quantity=request.quantity,
        unit_price=unit_price,
        list_amount=list_amount,
        discount_basis_points=basis_points,
        discount_amount=discount_amount,
        net_amount=net_amount,
        applied_discounts=tuple(applied),
    )


def build_quote(book: PriceBook, requests: Sequence[QuoteLineRequest], *, quote_id: str) -> Quote:
    """Price every requested line against ``book`` and total the quote deterministically."""
    if not quote_id:
        raise PricingError("a quote requires a non-empty quote_id", book_id=book.book_id)
    if not requests:
        raise PricingError("a quote requires at least one line", quote_id=quote_id)
    lines = tuple(price_line(book, request) for request in requests)
    list_total = sum_money([line.list_amount for line in lines], currency=book.currency)
    discount_total = sum_money([line.discount_amount for line in lines], currency=book.currency)
    return Quote(
        quote_id=quote_id,
        book_id=book.book_id,
        currency=book.currency,
        lines=lines,
        list_total=list_total,
        discount_total=discount_total,
        net_total=list_total.subtract(discount_total),
    )


__all__ = [
    "DiscountRule",
    "PriceBook",
    "QuoteLineRequest",
    "QuoteLine",
    "Quote",
    "price_line",
    "build_quote",
]
