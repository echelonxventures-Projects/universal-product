"""UCOS-EPIC-014 — Licensing Intelligence (Terminal T5).

A **licence grant** is the only instrument that converts an offer into a right to use.
Licensing Intelligence therefore never *infers* a right: an entitlement request is
satisfied only when a located grant covers the requested product, the requested
capability, the requested seat count and the requested day of the term. Anything it
cannot prove is denied — a denied request carries the exact reasons, so a commercial
decision is always auditable rather than asserted.

Determinism: a term is a **day offset from grant day zero**, never a wall-clock instant,
so an identical grant and an identical request always yield an identical decision on
every machine and in every timezone.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from platform.commercial_intelligence.errors import LicensingError
from platform.foundation.contracts import content_hash
from typing import Any


class LicenseModel(str, Enum):
    """The closed licence-model vocabulary."""

    PERPETUAL = "perpetual"
    SUBSCRIPTION = "subscription"
    USAGE = "usage"
    EVALUATION = "evaluation"

    @classmethod
    def parse(cls, value: Any) -> LicenseModel:
        try:
            return cls(value)
        except ValueError as exc:
            raise LicensingError(
                "unknown licence model",
                model=value,
                supported=[m.value for m in cls],
            ) from exc


#: Models whose right to use is bounded by a term. A perpetual grant has no term bound;
#: every other model must declare a positive term in days.
TERMED_MODELS = frozenset({LicenseModel.SUBSCRIPTION, LicenseModel.USAGE, LicenseModel.EVALUATION})


@dataclass(frozen=True, slots=True)
class LicenseGrant:
    """An immutable grant of the right to use one product's capabilities.

    ``term_days`` is the length of the term in days from grant day zero; ``0`` means
    unbounded and is legal only for a perpetual grant. ``seats`` is the maximum number of
    concurrently entitled principals.
    """

    grant_id: str
    product_id: str
    customer_id: str
    model: LicenseModel
    seats: int
    term_days: int
    capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.grant_id:
            raise LicensingError("a licence grant requires a non-empty grant_id")
        if not self.product_id:
            raise LicensingError(
                "a licence grant requires the product_id it licenses", grant_id=self.grant_id
            )
        if not self.customer_id:
            raise LicensingError(
                "a licence grant requires the customer_id it is granted to",
                grant_id=self.grant_id,
            )
        if isinstance(self.seats, bool) or not isinstance(self.seats, int) or self.seats < 1:
            raise LicensingError(
                "a licence grant requires an integer seat count of at least one",
                grant_id=self.grant_id,
                seats=repr(self.seats),
            )
        if isinstance(self.term_days, bool) or not isinstance(self.term_days, int):
            raise LicensingError(
                "a licence term must be an integer number of days",
                grant_id=self.grant_id,
                term_days=repr(self.term_days),
            )
        if self.term_days < 0:
            raise LicensingError(
                "a licence term may not be negative",
                grant_id=self.grant_id,
                term_days=self.term_days,
            )
        if self.model in TERMED_MODELS and self.term_days == 0:
            raise LicensingError(
                "a termed licence model requires a positive term in days",
                grant_id=self.grant_id,
                model=self.model.value,
            )
        if self.model is LicenseModel.PERPETUAL and self.term_days != 0:
            raise LicensingError(
                "a perpetual licence may not declare a bounded term",
                grant_id=self.grant_id,
                term_days=self.term_days,
            )
        if not self.capabilities:
            raise LicensingError(
                "a licence grant must name the capabilities it entitles",
                grant_id=self.grant_id,
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> LicenseGrant:
        if not isinstance(raw, Mapping):
            raise LicensingError("a licence grant must be a mapping")
        capabilities = raw.get("capabilities", ())
        if isinstance(capabilities, str) or not isinstance(capabilities, Sequence):
            raise LicensingError(
                "licence capabilities must be a sequence", grant_id=raw.get("grant_id")
            )
        return cls(
            grant_id=str(raw.get("grant_id") or ""),
            product_id=str(raw.get("product_id") or ""),
            customer_id=str(raw.get("customer_id") or ""),
            model=LicenseModel.parse(raw.get("model")),
            seats=raw.get("seats"),
            term_days=raw.get("term_days", 0),
            capabilities=tuple(sorted(str(c) for c in capabilities)),
        )

    @property
    def perpetual(self) -> bool:
        return self.term_days == 0

    def covers_day(self, day: int) -> bool:
        """True iff ``day`` (a day offset from grant day zero) falls inside the term."""
        if day < 0:
            return False
        return self.perpetual or day < self.term_days

    def to_dict(self) -> dict[str, Any]:
        return {
            "grant_id": self.grant_id,
            "product_id": self.product_id,
            "customer_id": self.customer_id,
            "model": self.model.value,
            "seats": self.seats,
            "term_days": self.term_days,
            "perpetual": self.perpetual,
            "capabilities": list(self.capabilities),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class EntitlementRequest:
    """A request to exercise a right: who, what product, what capability, how many, when."""

    customer_id: str
    product_id: str
    capability: str
    seats: int = 1
    day: int = 0

    def __post_init__(self) -> None:
        if not self.customer_id or not self.product_id or not self.capability:
            raise LicensingError(
                "an entitlement request requires a customer_id, product_id and capability"
            )
        if isinstance(self.seats, bool) or not isinstance(self.seats, int) or self.seats < 1:
            raise LicensingError(
                "an entitlement request requires an integer seat count of at least one",
                seats=repr(self.seats),
            )
        if isinstance(self.day, bool) or not isinstance(self.day, int):
            raise LicensingError(
                "an entitlement request day must be an integer day offset", day=repr(self.day)
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> EntitlementRequest:
        if not isinstance(raw, Mapping):
            raise LicensingError("an entitlement request must be a mapping")
        return cls(
            customer_id=str(raw.get("customer_id") or ""),
            product_id=str(raw.get("product_id") or ""),
            capability=str(raw.get("capability") or ""),
            seats=raw.get("seats", 1),
            day=raw.get("day", 0),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "capability": self.capability,
            "seats": self.seats,
            "day": self.day,
        }


@dataclass(frozen=True, slots=True)
class EntitlementDecision:
    """The fail-closed, content-addressed decision on one entitlement request."""

    request: EntitlementRequest
    granted: bool
    grant_id: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "granted": self.granted,
            "grant_id": self.grant_id,
            "reasons": list(self.reasons),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class LicenseRegister:
    """An immutable, deterministically ordered register of licence grants."""

    grants: tuple[LicenseGrant, ...] = ()

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for grant in self.grants:
            if grant.grant_id in seen:
                raise LicensingError("duplicate grant_id in register", grant_id=grant.grant_id)
            seen.add(grant.grant_id)

    @classmethod
    def from_sequence(cls, raw: Any) -> LicenseRegister:
        if isinstance(raw, str | bytes) or not isinstance(raw, Sequence):
            raise LicensingError("a licence register must be a sequence of grants")
        grants = tuple(
            sorted((LicenseGrant.from_mapping(item) for item in raw), key=lambda g: g.grant_id)
        )
        return cls(grants=grants)

    def get(self, grant_id: str) -> LicenseGrant | None:
        for grant in self.grants:
            if grant.grant_id == grant_id:
                return grant
        return None

    def grants_for(self, customer_id: str, product_id: str) -> tuple[LicenseGrant, ...]:
        return tuple(
            grant
            for grant in self.grants
            if grant.customer_id == customer_id and grant.product_id == product_id
        )

    def evaluate(self, request: EntitlementRequest) -> EntitlementDecision:
        """Decide ``request`` against the register — fail-closed, with explicit reasons.

        The first grant (in canonical grant-id order) that covers the product, the
        capability, the seats and the day satisfies the request. When none does, the
        decision is a denial carrying the reason for every candidate grant considered, or
        the fact that no grant exists at all.
        """
        candidates = self.grants_for(request.customer_id, request.product_id)
        if not candidates:
            return EntitlementDecision(
                request=request,
                granted=False,
                grant_id="",
                reasons=(
                    f"no licence grant exists for customer {request.customer_id} "
                    f"on product {request.product_id}",
                ),
            )
        reasons: list[str] = []
        for grant in candidates:
            defects: list[str] = []
            if request.capability not in grant.capabilities:
                defects.append(f"does not entitle capability {request.capability}")
            if request.seats > grant.seats:
                defects.append(f"entitles {grant.seats} seat(s), {request.seats} requested")
            if not grant.covers_day(request.day):
                defects.append(f"term of {grant.term_days} day(s) does not cover day {request.day}")
            if not defects:
                return EntitlementDecision(
                    request=request, granted=True, grant_id=grant.grant_id, reasons=()
                )
            reasons.append(f"{grant.grant_id}: " + "; ".join(defects))
        return EntitlementDecision(
            request=request, granted=False, grant_id="", reasons=tuple(reasons)
        )

    def model_counts(self) -> dict[str, int]:
        return {
            model.value: sum(1 for grant in self.grants if grant.model is model)
            for model in LicenseModel
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "grants": [grant.to_dict() for grant in self.grants],
            "total": len(self.grants),
            "model_counts": self.model_counts(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "LicenseModel",
    "TERMED_MODELS",
    "LicenseGrant",
    "EntitlementRequest",
    "EntitlementDecision",
    "LicenseRegister",
]
