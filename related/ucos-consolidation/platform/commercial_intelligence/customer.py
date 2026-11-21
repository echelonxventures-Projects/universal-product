"""UCOS-EPIC-014 — Customer Intelligence (Terminal T5).

A **customer account** is the commercial counterparty: an identity, a lifecycle segment,
the licence grants it holds, and its contracted value. Customer Intelligence reports the
customer base as it is declared — segment distribution, contracted value, revenue
concentration — and, critically, whether every account's claimed grants actually exist in
the licence register. An account claiming a grant that does not exist is an unsound
commercial position, not a rounding error, so it is surfaced explicitly.

Concentration is expressed in basis points over integer minor units: the share of total
contracted value held by the single largest account. No float, no locale, no wall-clock.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from platform.commercial_intelligence.contracts import BASIS_POINTS_SCALE, Money, sum_money
from platform.commercial_intelligence.errors import CustomerError
from platform.commercial_intelligence.licensing import LicenseRegister
from platform.foundation.contracts import content_hash
from typing import Any


class CustomerSegment(str, Enum):
    """The closed customer-lifecycle segment vocabulary."""

    PROSPECT = "prospect"
    ACTIVE = "active"
    RENEWAL = "renewal"
    CHURNED = "churned"

    @classmethod
    def parse(cls, value: Any) -> CustomerSegment:
        try:
            return cls(value)
        except ValueError as exc:
            raise CustomerError(
                "unknown customer segment",
                segment=value,
                supported=[s.value for s in cls],
            ) from exc


#: Segments in which an account is expected to hold at least one licence grant. A
#: prospect holds none by definition; a churned account's grants have lapsed.
ENTITLED_SEGMENTS = frozenset({CustomerSegment.ACTIVE, CustomerSegment.RENEWAL})


@dataclass(frozen=True, slots=True)
class CustomerAccount:
    """An immutable customer account: identity, segment, grants held, contracted value."""

    customer_id: str
    name: str
    segment: CustomerSegment
    contracted_value: Money
    grant_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.customer_id:
            raise CustomerError("a customer account requires a non-empty customer_id")
        if not self.name:
            raise CustomerError("a customer account requires a name", customer_id=self.customer_id)
        if self.contracted_value.is_negative:
            raise CustomerError(
                "contracted value may not be negative", customer_id=self.customer_id
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> CustomerAccount:
        if not isinstance(raw, Mapping):
            raise CustomerError("a customer account must be a mapping")
        customer_id = str(raw.get("customer_id") or "")
        grant_ids = raw.get("grant_ids", ())
        if isinstance(grant_ids, str) or not isinstance(grant_ids, Sequence):
            raise CustomerError("customer grant_ids must be a sequence", customer_id=customer_id)
        return cls(
            customer_id=customer_id,
            name=str(raw.get("name") or ""),
            segment=CustomerSegment.parse(raw.get("segment")),
            contracted_value=Money.from_mapping(
                raw.get("contracted_value"), context=f"customer:{customer_id}"
            ),
            grant_ids=tuple(sorted(str(g) for g in grant_ids)),
        )

    @property
    def expects_entitlement(self) -> bool:
        return self.segment in ENTITLED_SEGMENTS

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "segment": self.segment.value,
            "contracted_value": self.contracted_value.to_dict(),
            "grant_ids": list(self.grant_ids),
            "expects_entitlement": self.expects_entitlement,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class AccountIntegrity:
    """The deterministic verdict on one account against the licence register."""

    customer_id: str
    sound: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "sound": self.sound,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class CustomerBase:
    """An immutable, deterministically ordered customer base in one currency."""

    currency: str
    accounts: tuple[CustomerAccount, ...] = ()

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for account in self.accounts:
            if account.customer_id in seen:
                raise CustomerError(
                    "duplicate customer_id in the customer base",
                    customer_id=account.customer_id,
                )
            if account.contracted_value.currency != self.currency:
                raise CustomerError(
                    "a customer base may not mix currencies",
                    customer_id=account.customer_id,
                    base_currency=self.currency,
                    account_currency=account.contracted_value.currency,
                )
            seen.add(account.customer_id)

    @classmethod
    def from_mapping(cls, raw: Any) -> CustomerBase:
        """Assimilate ``{currency, accounts}`` into a normalized customer base."""
        if not isinstance(raw, Mapping):
            raise CustomerError("a customer base must be a mapping")
        accounts_raw = raw.get("accounts", ())
        if isinstance(accounts_raw, str | bytes) or not isinstance(accounts_raw, Sequence):
            raise CustomerError("customer base accounts must be a sequence")
        accounts = tuple(
            sorted(
                (CustomerAccount.from_mapping(item) for item in accounts_raw),
                key=lambda account: account.customer_id,
            )
        )
        return cls(currency=str(raw.get("currency") or ""), accounts=accounts)

    def get(self, customer_id: str) -> CustomerAccount | None:
        for account in self.accounts:
            if account.customer_id == customer_id:
                return account
        return None

    def segment_counts(self) -> dict[str, int]:
        return {
            segment.value: sum(1 for a in self.accounts if a.segment is segment)
            for segment in CustomerSegment
        }

    def contracted_total(self) -> Money:
        return sum_money([a.contracted_value for a in self.accounts], currency=self.currency)

    def concentration_basis_points(self) -> int:
        """The share of contracted value held by the single largest account, in basis points."""
        total = self.contracted_total()
        if total.is_zero:
            return 0
        largest = max(a.contracted_value.minor_units for a in self.accounts)
        return largest * BASIS_POINTS_SCALE // total.minor_units

    def integrity(self, register: LicenseRegister) -> tuple[AccountIntegrity, ...]:
        """Verify every account's claimed grants against the licence register."""
        verdicts: list[AccountIntegrity] = []
        for account in self.accounts:
            reasons: list[str] = []
            for grant_id in account.grant_ids:
                grant = register.get(grant_id)
                if grant is None:
                    reasons.append(f"claims grant {grant_id} which is not in the licence register")
                elif grant.customer_id != account.customer_id:
                    reasons.append(
                        f"claims grant {grant_id} which is granted to {grant.customer_id}"
                    )
            if account.expects_entitlement and not account.grant_ids:
                reasons.append(f"is in segment {account.segment.value} but holds no licence grant")
            verdicts.append(
                AccountIntegrity(
                    customer_id=account.customer_id, sound=not reasons, reasons=tuple(reasons)
                )
            )
        return tuple(verdicts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "currency": self.currency,
            "accounts": [a.to_dict() for a in self.accounts],
            "total": len(self.accounts),
            "segment_counts": self.segment_counts(),
            "contracted_total": self.contracted_total().to_dict(),
            "concentration_basis_points": self.concentration_basis_points(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "CustomerSegment",
    "ENTITLED_SEGMENTS",
    "CustomerAccount",
    "AccountIntegrity",
    "CustomerBase",
]
