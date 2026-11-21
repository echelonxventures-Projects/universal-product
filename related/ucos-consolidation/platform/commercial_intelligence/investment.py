"""UCOS-EPIC-014 — Investment Intelligence (Terminal T5).

An **investment case** states, per period, what an initiative costs and what it returns.
Investment Intelligence computes the case; it never scores it with an opinion. Every
figure is an integer count of minor units in one currency, every ratio is expressed in
basis points, and the payback period is the first period at which cumulative return
reaches cumulative cost — an integer index, or *unrecovered* when it never does.

Because the arithmetic is integral and the horizon is a period index (never a wall-clock
date), an identical case always yields identical metrics — the property that lets an
investment determination be sealed as evidence.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from platform.commercial_intelligence.contracts import BASIS_POINTS_SCALE, Money, sum_money
from platform.commercial_intelligence.errors import InvestmentError
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class InvestmentMetrics:
    """The deterministic, integer-arithmetic metrics of one investment case."""

    total_cost: Money
    total_return: Money
    net_return: Money
    return_basis_points: int
    payback_period: int | None
    periods: int

    @property
    def recovered(self) -> bool:
        """True iff cumulative return reaches cumulative cost within the declared horizon."""
        return self.payback_period is not None

    @property
    def net_positive(self) -> bool:
        return self.net_return.minor_units > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cost": self.total_cost.to_dict(),
            "total_return": self.total_return.to_dict(),
            "net_return": self.net_return.to_dict(),
            "return_basis_points": self.return_basis_points,
            "payback_period": self.payback_period,
            "periods": self.periods,
            "recovered": self.recovered,
            "net_positive": self.net_positive,
        }


@dataclass(frozen=True, slots=True)
class InvestmentCase:
    """An immutable investment case: per-period cost and return flows in one currency.

    ``costs`` and ``returns`` are positional: index ``i`` is period ``i``. The two
    sequences must be the same length — the horizon — so no period is implicitly zero.
    """

    case_id: str
    currency: str
    costs: tuple[Money, ...]
    returns: tuple[Money, ...]

    def __post_init__(self) -> None:
        if not self.case_id:
            raise InvestmentError("an investment case requires a non-empty case_id")
        if not self.costs:
            raise InvestmentError(
                "an investment case requires at least one period", case_id=self.case_id
            )
        if len(self.costs) != len(self.returns):
            raise InvestmentError(
                "an investment case must declare a cost and a return for every period",
                case_id=self.case_id,
                cost_periods=len(self.costs),
                return_periods=len(self.returns),
            )
        for label, flows in (("cost", self.costs), ("return", self.returns)):
            for index, amount in enumerate(flows):
                if amount.currency != self.currency:
                    raise InvestmentError(
                        "an investment case may not mix currencies",
                        case_id=self.case_id,
                        flow=label,
                        period=index,
                        case_currency=self.currency,
                        flow_currency=amount.currency,
                    )
                if amount.is_negative:
                    raise InvestmentError(
                        "an investment flow may not be negative — model a reversal as a "
                        "flow on the opposite side",
                        case_id=self.case_id,
                        flow=label,
                        period=index,
                    )

    @classmethod
    def from_mapping(cls, raw: Any) -> InvestmentCase:
        """Assimilate ``{case_id, currency, costs, returns}`` into an investment case."""
        if not isinstance(raw, Mapping):
            raise InvestmentError("an investment case must be a mapping")
        case_id = str(raw.get("case_id") or "")
        currency = str(raw.get("currency") or "")
        flows: dict[str, tuple[Money, ...]] = {}
        for key in ("costs", "returns"):
            value = raw.get(key, ())
            if isinstance(value, str | bytes) or not isinstance(value, Sequence):
                raise InvestmentError(
                    f"investment {key} must be a sequence of amounts", case_id=case_id
                )
            flows[key] = tuple(
                Money.from_mapping(item, context=f"{case_id}:{key}") for item in value
            )
        return cls(
            case_id=case_id,
            currency=currency,
            costs=flows["costs"],
            returns=flows["returns"],
        )

    @property
    def periods(self) -> int:
        return len(self.costs)

    def cumulative(self) -> tuple[tuple[Money, Money], ...]:
        """The running (cumulative cost, cumulative return) pair for each period."""
        running_cost = Money.zero(self.currency)
        running_return = Money.zero(self.currency)
        rows: list[tuple[Money, Money]] = []
        for index in range(self.periods):
            running_cost = running_cost.add(self.costs[index])
            running_return = running_return.add(self.returns[index])
            rows.append((running_cost, running_return))
        return tuple(rows)

    def payback_period(self) -> int | None:
        """The first period index at which cumulative return reaches cumulative cost."""
        for index, (cost, ret) in enumerate(self.cumulative()):
            if ret.compare(cost) >= 0:
                return index
        return None

    def metrics(self) -> InvestmentMetrics:
        """Compute the case's metrics deterministically from the declared flows."""
        total_cost = sum_money(list(self.costs), currency=self.currency)
        total_return = sum_money(list(self.returns), currency=self.currency)
        net_return = total_return.subtract(total_cost)
        basis_points = (
            net_return.minor_units * BASIS_POINTS_SCALE // total_cost.minor_units
            if not total_cost.is_zero
            else 0
        )
        return InvestmentMetrics(
            total_cost=total_cost,
            total_return=total_return,
            net_return=net_return,
            return_basis_points=basis_points,
            payback_period=self.payback_period(),
            periods=self.periods,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "currency": self.currency,
            "costs": [amount.to_dict() for amount in self.costs],
            "returns": [amount.to_dict() for amount in self.returns],
            "metrics": self.metrics().to_dict(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["InvestmentMetrics", "InvestmentCase"]
