"""UCOS-EPIC-014 — Portfolio Intelligence (Terminal T5).

A **portfolio** is the commercial view over a product catalog: what the portfolio is
*required* to cover, what it actually covers today, where the coverage gaps are, and how
concentrated the offer is in a single product. Every metric is integer arithmetic over
declared facts — coverage is a set relation and concentration is expressed in basis
points — so the portfolio verdict is reproducible and never a judgement call.

Portfolio Intelligence answers, deterministically:

    * does the offerable catalog cover every capability the portfolio declares it must;
    * which capabilities are offered but not required (out-of-mandate offer); and
    * how concentrated the offer is — the largest share of covered capabilities carried
      by any single offerable product, in basis points.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from platform.commercial_intelligence.contracts import BASIS_POINTS_SCALE
from platform.commercial_intelligence.errors import PortfolioError
from platform.commercial_intelligence.product import Product, ProductCatalog
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class PortfolioCoverage:
    """The deterministic coverage projection of a portfolio over its mandate."""

    required: tuple[str, ...]
    covered: tuple[str, ...]
    gaps: tuple[str, ...]
    out_of_mandate: tuple[str, ...]
    coverage_basis_points: int

    @property
    def complete(self) -> bool:
        return not self.gaps and bool(self.required)

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": list(self.required),
            "covered": list(self.covered),
            "gaps": list(self.gaps),
            "out_of_mandate": list(self.out_of_mandate),
            "coverage_basis_points": self.coverage_basis_points,
            "complete": self.complete,
        }


@dataclass(frozen=True, slots=True)
class Portfolio:
    """An immutable portfolio: a mandate (required capabilities) over a product catalog."""

    portfolio_id: str
    catalog: ProductCatalog
    required_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.portfolio_id:
            raise PortfolioError("a portfolio requires a non-empty portfolio_id")
        if not self.required_capabilities:
            raise PortfolioError(
                "a portfolio requires at least one mandated capability — an unmandated "
                "portfolio cannot be assessed",
                portfolio_id=self.portfolio_id,
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> Portfolio:
        """Assimilate ``{portfolio_id, required_capabilities, products}`` into a portfolio."""
        if not isinstance(raw, Mapping):
            raise PortfolioError("a portfolio must be a mapping")
        required = raw.get("required_capabilities", ())
        if isinstance(required, str) or not isinstance(required, Sequence):
            raise PortfolioError(
                "portfolio required_capabilities must be a sequence",
                portfolio_id=raw.get("portfolio_id"),
            )
        catalog = ProductCatalog.from_sequence(raw.get("products", ()))
        return cls(
            portfolio_id=str(raw.get("portfolio_id") or ""),
            catalog=catalog,
            required_capabilities=tuple(sorted({str(c) for c in required})),
        )

    def offerable(self) -> tuple[Product, ...]:
        return self.catalog.offerable()

    def offered_capabilities(self) -> tuple[str, ...]:
        """The capabilities offered by the *offerable* products, in canonical order."""
        offered: set[str] = set()
        for product in self.offerable():
            offered.update(product.capabilities)
        return tuple(sorted(offered))

    def coverage(self) -> PortfolioCoverage:
        """The deterministic coverage projection of this portfolio over its mandate."""
        required = set(self.required_capabilities)
        offered = set(self.offered_capabilities())
        covered = required & offered
        basis_points = len(covered) * BASIS_POINTS_SCALE // len(required) if required else 0
        return PortfolioCoverage(
            required=tuple(sorted(required)),
            covered=tuple(sorted(covered)),
            gaps=tuple(sorted(required - offered)),
            out_of_mandate=tuple(sorted(offered - required)),
            coverage_basis_points=basis_points,
        )

    def concentration_basis_points(self) -> int:
        """The largest share of *covered* capabilities carried by one offerable product."""
        covered = set(self.coverage().covered)
        if not covered:
            return 0
        largest = max(
            (len(covered & set(product.capabilities)) for product in self.offerable()), default=0
        )
        return largest * BASIS_POINTS_SCALE // len(covered)

    def to_dict(self) -> dict[str, Any]:
        return {
            "portfolio_id": self.portfolio_id,
            "catalog": self.catalog.to_dict(),
            "coverage": self.coverage().to_dict(),
            "offered_capabilities": list(self.offered_capabilities()),
            "concentration_basis_points": self.concentration_basis_points(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["PortfolioCoverage", "Portfolio"]
