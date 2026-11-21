"""UCOS-UMPF-001 — Policy registry & the policy measurement engine.

The registry holds measurement policies the way the platform holds services: keyed by
identity, ordered by declared precedence, fail-closed on collision. The engine evaluates them
over one context and returns a
:class:`~platform.universal_measurement.contracts.PolicySuite` whose ``determination`` is the
conjunction of every blocking policy.

There is deliberately no place in the engine where a measurement is special-cased. Adding a
measurement means registering a policy; removing one means deregistering it. That is what
makes the same measurement framework serve every future project.
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.foundation.contracts import content_hash
from platform.measurement.contracts import Measurement, MeasurementKind
from platform.universal_measurement.contracts import (
    MeasurementContext,
    MeasurementPolicyDescriptor,
    PolicyOutcome,
    PolicySuite,
)
from platform.universal_measurement.errors import (
    MeasurementContextError,
    MeasurementPolicyRegistryError,
)
from platform.universal_measurement.policies import (
    MeasurementPolicy,
    default_measurement_policies,
)
from typing import Any


class MeasurementPolicyRegistry:
    """A deterministic, fail-closed registry of reusable measurement policies."""

    __slots__ = ("_policies",)

    def __init__(self, policies: Iterable[MeasurementPolicy] = ()) -> None:
        self._policies: dict[str, MeasurementPolicy] = {}
        self.register_all(policies)

    def register(self, policy: MeasurementPolicy) -> MeasurementPolicy:
        """Register ``policy``; idempotent by object, fail-closed on identity collision."""
        if not isinstance(policy, MeasurementPolicy):
            raise MeasurementPolicyRegistryError("registry accepts only MeasurementPolicy values")
        descriptor = policy.descriptor()
        existing = self._policies.get(descriptor.policy_id)
        if existing is not None:
            if existing is policy:
                return existing
            raise MeasurementPolicyRegistryError(
                "policy identity already registered", policy_id=descriptor.policy_id
            )
        self._policies[descriptor.policy_id] = policy
        return policy

    def register_all(self, policies: Iterable[MeasurementPolicy]) -> tuple[MeasurementPolicy, ...]:
        """Register every policy in ``policies``, returning them in evaluation order."""
        for policy in policies:
            self.register(policy)
        return self.ordered()

    def deregister(self, policy_id: str) -> None:
        """Remove ``policy_id`` from the registry (fail-closed when unknown)."""
        if policy_id not in self._policies:
            raise MeasurementPolicyRegistryError("unknown measurement policy", policy_id=policy_id)
        del self._policies[policy_id]

    def get(self, policy_id: str) -> MeasurementPolicy | None:
        """The registered policy ``policy_id``, or ``None``."""
        return self._policies.get(policy_id)

    def require(self, policy_id: str) -> MeasurementPolicy:
        """The registered policy ``policy_id`` (fail-closed)."""
        policy = self.get(policy_id)
        if policy is None:
            raise MeasurementPolicyRegistryError("unknown measurement policy", policy_id=policy_id)
        return policy

    @property
    def count(self) -> int:
        """How many policies are registered."""
        return len(self._policies)

    def ordered(self) -> tuple[MeasurementPolicy, ...]:
        """Every policy in declared precedence order — never insertion order."""
        return tuple(sorted(self._policies.values(), key=lambda item: item.descriptor().order_key))

    def descriptors(self) -> tuple[MeasurementPolicyDescriptor, ...]:
        """Every policy descriptor in evaluation order."""
        return tuple(policy.descriptor() for policy in self.ordered())

    def ids(self) -> tuple[str, ...]:
        """Every registered policy identity, sorted."""
        return tuple(sorted(self._policies))

    def of_kind(self, kind: MeasurementKind) -> tuple[MeasurementPolicy, ...]:
        """Every policy producing ``kind``, in evaluation order."""
        return tuple(policy for policy in self.ordered() if policy.descriptor().kind is kind)

    def blocking(self) -> tuple[MeasurementPolicy, ...]:
        """Every policy whose dissatisfaction withholds closure."""
        return tuple(policy for policy in self.ordered() if policy.descriptor().blocking)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this registry."""
        return {
            "policy_count": self.count,
            "blocking_count": len(self.blocking()),
            "policies": [descriptor.to_dict() for descriptor in self.descriptors()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this registry."""
        return content_hash(self.to_dict())


class PolicyMeasurementEngine:
    """Evaluates a registry of measurement policies over a determination context."""

    __slots__ = ("_registry",)

    def __init__(self, registry: MeasurementPolicyRegistry) -> None:
        if not isinstance(registry, MeasurementPolicyRegistry):
            raise MeasurementPolicyRegistryError(
                "policy engine requires a MeasurementPolicyRegistry"
            )
        self._registry = registry

    @property
    def registry(self) -> MeasurementPolicyRegistry:
        """The policy registry this engine evaluates."""
        return self._registry

    def evaluate(self, policy_id: str, context: MeasurementContext) -> PolicyOutcome:
        """Evaluate exactly one registered policy."""
        return self._registry.require(policy_id).apply(context)

    def measure(self, context: MeasurementContext) -> PolicySuite:
        """Evaluate every applicable registered policy over ``context``.

        Policies whose required determination is absent from the context are skipped rather
        than reported as satisfied — a measurement that was not made is never a pass.
        """
        outcomes: list[PolicyOutcome] = []
        for policy in self._registry.ordered():
            try:
                outcomes.append(policy.apply(context))
            except MeasurementContextError:
                continue
        return PolicySuite.create(outcomes, context_id=context.context_id)

    def measure_strict(self, context: MeasurementContext) -> PolicySuite:
        """Evaluate every registered policy, failing closed if any cannot be evaluated."""
        return PolicySuite.create(
            [policy.apply(context) for policy in self._registry.ordered()],
            context_id=context.context_id,
        )

    def measurements(self, context: MeasurementContext) -> tuple[Measurement, ...]:
        """Project the whole suite as recordable measurements."""
        return self.measure(context).as_measurements()

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this engine's composition (UFC-11)."""
        return {"registry": self._registry.to_dict()}

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this engine's composition."""
        return content_hash(self.to_dict())


def default_policy_registry() -> MeasurementPolicyRegistry:
    """A registry seeded with the shipped reusable policies."""
    return MeasurementPolicyRegistry(default_measurement_policies())


def build_policy_engine(
    registry: MeasurementPolicyRegistry | None = None,
) -> PolicyMeasurementEngine:
    """The default composition of the policy measurement engine."""
    return PolicyMeasurementEngine(registry or default_policy_registry())


__all__ = [
    "MeasurementPolicyRegistry",
    "PolicyMeasurementEngine",
    "default_policy_registry",
    "build_policy_engine",
]
