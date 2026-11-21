"""UCOS-EPIC-014 — Policy Governance (Terminal T5).

Every commercial action — publishing a listing, quoting a discount, granting a licence,
assembling a package — is governed. Policy Governance decides whether an action is
permitted, and it is **fail-closed by construction**: an action that no policy governs is
DENIED, never allowed by default. There is no implicit commercial freedom in this
platform.

The decision algebra is a total order over effects, so a decision never depends on
declaration order:

    ``DENY`` > ``REQUIRES_APPROVAL`` > ``ALLOW``

A policy may bound a magnitude (a discount in basis points, a seat count, a contract
value in minor units). A request that exceeds a bound matches the policy's *breach*
effect rather than its permitted effect, so a bound is enforced rather than advisory.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from platform.commercial_intelligence.contracts import CommercialDomain
from platform.commercial_intelligence.errors import PolicyError
from platform.foundation.contracts import content_hash
from typing import Any


class PolicyEffect(str, Enum):
    """The closed policy-effect vocabulary, in increasing restrictiveness."""

    ALLOW = "allow"
    REQUIRES_APPROVAL = "requires_approval"
    DENY = "deny"

    @classmethod
    def parse(cls, value: Any) -> PolicyEffect:
        try:
            return cls(value)
        except ValueError as exc:
            raise PolicyError(
                "unknown policy effect",
                effect=value,
                supported=[e.value for e in cls],
            ) from exc

    @property
    def rank(self) -> int:
        """The restrictiveness rank — the higher rank always governs."""
        return _EFFECT_RANK[self]


_EFFECT_RANK: dict[PolicyEffect, int] = {
    PolicyEffect.ALLOW: 0,
    PolicyEffect.REQUIRES_APPROVAL: 1,
    PolicyEffect.DENY: 2,
}

#: The effect of an action no policy governs. Fail-closed: silence is refusal.
UNGOVERNED_EFFECT = PolicyEffect.DENY


@dataclass(frozen=True, slots=True)
class CommercialPolicy:
    """An immutable commercial policy over one action in one domain.

    ``max_magnitude`` optionally bounds the action's declared magnitude (basis points,
    seats, minor units — the unit is the action's own). When a request's magnitude exceeds
    the bound, ``breach_effect`` governs instead of ``effect``.
    """

    policy_id: str
    domain: CommercialDomain
    action: str
    effect: PolicyEffect
    max_magnitude: int | None = None
    breach_effect: PolicyEffect = PolicyEffect.DENY
    approval_role: str = ""

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise PolicyError("a commercial policy requires a non-empty policy_id")
        if not self.action:
            raise PolicyError(
                "a commercial policy requires the action it governs", policy_id=self.policy_id
            )
        if self.max_magnitude is not None and (
            isinstance(self.max_magnitude, bool)
            or not isinstance(self.max_magnitude, int)
            or self.max_magnitude < 0
        ):
            raise PolicyError(
                "a policy bound must be a non-negative integer magnitude",
                policy_id=self.policy_id,
                max_magnitude=repr(self.max_magnitude),
            )
        if self.effect is PolicyEffect.REQUIRES_APPROVAL and not self.approval_role:
            raise PolicyError(
                "a policy requiring approval must name the accountable approval role",
                policy_id=self.policy_id,
            )
        if self.breach_effect is PolicyEffect.REQUIRES_APPROVAL and not self.approval_role:
            raise PolicyError(
                "a policy escalating a breach to approval must name the approval role",
                policy_id=self.policy_id,
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> CommercialPolicy:
        if not isinstance(raw, Mapping):
            raise PolicyError("a commercial policy must be a mapping")
        bound = raw.get("max_magnitude")
        return cls(
            policy_id=str(raw.get("policy_id") or ""),
            domain=CommercialDomain.parse(raw.get("domain")),
            action=str(raw.get("action") or ""),
            effect=PolicyEffect.parse(raw.get("effect")),
            max_magnitude=None if bound is None else bound,
            breach_effect=PolicyEffect.parse(raw.get("breach_effect", PolicyEffect.DENY.value)),
            approval_role=str(raw.get("approval_role") or ""),
        )

    def governs(self, domain: CommercialDomain, action: str) -> bool:
        return self.domain is domain and self.action == action

    def effect_for(self, magnitude: int) -> PolicyEffect:
        """The effect this policy imposes on an action of ``magnitude``."""
        if self.max_magnitude is not None and magnitude > self.max_magnitude:
            return self.breach_effect
        return self.effect

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "domain": self.domain.value,
            "action": self.action,
            "effect": self.effect.value,
            "max_magnitude": self.max_magnitude,
            "breach_effect": self.breach_effect.value,
            "approval_role": self.approval_role,
        }


@dataclass(frozen=True, slots=True)
class PolicyRequest:
    """A request to take one commercial action, with its declared magnitude."""

    domain: CommercialDomain
    action: str
    magnitude: int = 0
    subject_id: str = ""

    def __post_init__(self) -> None:
        if not self.action:
            raise PolicyError("a policy request requires an action")
        if isinstance(self.magnitude, bool) or not isinstance(self.magnitude, int):
            raise PolicyError(
                "a policy request magnitude must be an integer", magnitude=repr(self.magnitude)
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> PolicyRequest:
        if not isinstance(raw, Mapping):
            raise PolicyError("a policy request must be a mapping")
        return cls(
            domain=CommercialDomain.parse(raw.get("domain")),
            action=str(raw.get("action") or ""),
            magnitude=raw.get("magnitude", 0),
            subject_id=str(raw.get("subject_id") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "action": self.action,
            "magnitude": self.magnitude,
            "subject_id": self.subject_id,
        }


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """The immutable, content-addressed decision on one commercial action."""

    request: PolicyRequest
    effect: PolicyEffect
    matched_policies: tuple[str, ...]
    required_roles: tuple[str, ...]
    reasons: tuple[str, ...]

    @property
    def allowed(self) -> bool:
        """True only when the action is permitted outright — approval pending is not allowed."""
        return self.effect is PolicyEffect.ALLOW

    @property
    def requires_approval(self) -> bool:
        return self.effect is PolicyEffect.REQUIRES_APPROVAL

    @property
    def denied(self) -> bool:
        return self.effect is PolicyEffect.DENY

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "effect": self.effect.value,
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "denied": self.denied,
            "matched_policies": list(self.matched_policies),
            "required_roles": list(self.required_roles),
            "reasons": list(self.reasons),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class PolicyRegister:
    """An immutable, deterministically ordered register of commercial policies."""

    policies: tuple[CommercialPolicy, ...] = ()

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for policy in self.policies:
            if policy.policy_id in seen:
                raise PolicyError(
                    "duplicate policy_id in the policy register", policy_id=policy.policy_id
                )
            seen.add(policy.policy_id)

    @classmethod
    def from_sequence(cls, raw: Any) -> PolicyRegister:
        if isinstance(raw, str | bytes) or not isinstance(raw, Sequence):
            raise PolicyError("a policy register must be a sequence of policies")
        policies = tuple(
            sorted(
                (CommercialPolicy.from_mapping(item) for item in raw),
                key=lambda policy: policy.policy_id,
            )
        )
        return cls(policies=policies)

    def get(self, policy_id: str) -> CommercialPolicy | None:
        for policy in self.policies:
            if policy.policy_id == policy_id:
                return policy
        return None

    def governing(self, request: PolicyRequest) -> tuple[CommercialPolicy, ...]:
        return tuple(p for p in self.policies if p.governs(request.domain, request.action))

    def decide(self, request: PolicyRequest) -> PolicyDecision:
        """Decide ``request`` — the most restrictive matching effect governs; silence denies."""
        matching = self.governing(request)
        if not matching:
            return PolicyDecision(
                request=request,
                effect=UNGOVERNED_EFFECT,
                matched_policies=(),
                required_roles=(),
                reasons=(
                    f"no policy governs action {request.action!r} in domain "
                    f"{request.domain.value} — an ungoverned commercial action is refused",
                ),
            )
        effects = {policy.policy_id: policy.effect_for(request.magnitude) for policy in matching}
        governing_effect = max(effects.values(), key=lambda effect: effect.rank)
        reasons: list[str] = []
        roles: set[str] = set()
        for policy in matching:
            effect = effects[policy.policy_id]
            if effect is not policy.effect:
                reasons.append(
                    f"{policy.policy_id}: magnitude {request.magnitude} exceeds the bound "
                    f"{policy.max_magnitude} — {effect.value} governs"
                )
            if effect is PolicyEffect.REQUIRES_APPROVAL and policy.approval_role:
                roles.add(policy.approval_role)
            if effect is PolicyEffect.DENY and effect is policy.effect:
                reasons.append(f"{policy.policy_id}: denies action {request.action!r}")
        return PolicyDecision(
            request=request,
            effect=governing_effect,
            matched_policies=tuple(policy.policy_id for policy in matching),
            required_roles=tuple(sorted(roles)),
            reasons=tuple(reasons),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policies": [policy.to_dict() for policy in self.policies],
            "total": len(self.policies),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "PolicyEffect",
    "UNGOVERNED_EFFECT",
    "CommercialPolicy",
    "PolicyRequest",
    "PolicyDecision",
    "PolicyRegister",
]
