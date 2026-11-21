"""Dynamic Capability Composition — execution derived from declarations, not a pipeline.

This module holds no workflow and no predefined sequence of steps. A **capability** declares
what it requires, which dimensions it is bound to, which policies govern it, and what
evidence it carries; a **plan** is then *derived* from those declarations together with the
requesting context, the governing policies and the available evidence. Registering one more
capability changes the plan with no change to this module — which is the property a fixed
pipeline cannot have.

The rule by which a plan is derived is itself open: a :data:`CompositionStrategy` is a named,
deterministic, pure function over the resolved dependency graph, and new strategies are
registered (:func:`register_strategy`). Two ship by name, so callers may always request one:
a total :func:`dependency_order` and a wave-parallel :func:`parallel_waves`. Neither is
privileged by the planner — both are looked up through the same registry.

That registry, the layering algorithm and the act of derivation are **not defined here**.
They are the single ordering authority owned by :mod:`engine.foundation.composition`, which
this module consumes and re-exports unchanged. ``WP-UCDA-018`` required that exactly one
ordering mechanism remain reachable in the repository: this planner derives *capability*
composition and :mod:`engine.factory.phases` derives *generation-runtime* phase order, and
both derive through that one authority, so a strategy registered by either is available to
both and neither can drift from the other. What remains this module's own is the capability
declaration model, the requirement closure, the satisfiability rules and the plan identity.

Requirements are declared by **capability key**, not by minted identity, so declarations are
order independent: a capability may require one that is not registered yet. That freedom is
what makes a declared cycle possible, so the planner detects cycles itself rather than
assuming the kernel's relationship acyclicity has already excluded them. Where a requirement
*is* already registered and the edge does not close a cycle, a governed kernel relationship
is recorded too, so the dependency graph is traceable through the kernel.

A plan is derived truth: it is computed, never registered. Registering a derivation of
already-registered knowledge would itself breach Knowledge Once.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.civilization.errors import (
    CapabilityUnknownError,
    CompositionCycleError,
    CompositionStrategyError,
    CompositionUnsatisfiedError,
)
from engine.civilization.metatypes import CAPABILITY_NS, REQUIRES
from engine.civilization.seeding import seed_facets
from engine.foundation.composition import (
    DEFAULT_STRATEGY,
    CompositionStrategy,
    DependencyGraph,
    dependency_order,
    parallel_waves,
    register_strategy,
    strategy_names,
    unresolved_keys,
)
from engine.foundation.composition import (
    get_strategy as _located_strategy,
)
from engine.kernel.identity import content_digest
from engine.kernel.kernel import MetaKernel
from engine.kernel.meta import MetaObject


def get_strategy(name: str) -> CompositionStrategy:
    """Return a registered composition strategy by name.

    Delegates to the single ordering authority and translates its ``KeyError`` into this
    layer's own error, so the civilization surface keeps its structured error contract
    without declaring a second strategy registry.
    """
    try:
        return _located_strategy(name)
    except KeyError:
        raise CompositionStrategyError(
            "composition strategy is not registered",
            strategy=name,
            registered=strategy_names(),
        ) from None


@dataclass(frozen=True)
class CompositionStep:
    """One derived step of a composition plan."""

    sequence: int
    wave: int
    capability: str
    identity: str
    requires: tuple[str, ...]
    dimensions: tuple[str, ...]
    policies: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """A deterministic, serialisable rendering of this step."""
        return {
            "sequence": self.sequence,
            "wave": self.wave,
            "capability": self.capability,
            "identity": self.identity,
            "requires": list(self.requires),
            "dimensions": list(self.dimensions),
            "policies": list(self.policies),
        }


@dataclass(frozen=True)
class CompositionPlan:
    """A composition derived from declarations, context, policies and evidence."""

    targets: tuple[str, ...]
    strategy: str
    steps: tuple[CompositionStep, ...]
    context: tuple[str, ...]
    policies: tuple[str, ...]

    @property
    def waves(self) -> int:
        """The number of distinct execution waves in this plan."""
        return len({step.wave for step in self.steps})

    def body(self) -> dict[str, object]:
        """The substantive plan body (used for the plan hash)."""
        return {
            "targets": list(self.targets),
            "strategy": self.strategy,
            "context": list(self.context),
            "policies": list(self.policies),
            "steps": [step.to_dict() for step in self.steps],
        }

    def plan_hash(self) -> str:
        """SHA-256 over the plan body — a deterministic plan identity."""
        return content_digest(self.body())

    def to_dict(self) -> dict[str, object]:
        """A deterministic, serialisable rendering of the plan."""
        payload = self.body()
        payload["waves"] = self.waves
        payload["plan_hash"] = self.plan_hash()
        return payload


# --------------------------------------------------------------------------- planner


class CompositionPlanner:
    """Derives execution from registered capability declarations."""

    __slots__ = ("_kernel",)

    def __init__(self, *, kernel: MetaKernel | None = None) -> None:
        self._kernel = kernel if kernel is not None else MetaKernel()
        seed_facets(self._kernel)

    # -- registration ----------------------------------------------------------

    def register_capability(
        self,
        key: str,
        *,
        name: str = "",
        requires: Sequence[str] = (),
        dimensions: Sequence[str] = (),
        policies: Sequence[str] = (),
        evidence: Sequence[str] = (),
        version: str = "1.0.0",
        attributes: Mapping[str, Any] | None = None,
    ) -> MetaObject:
        """Register a capability declaration. Adding one changes future plans."""
        attrs: dict[str, Any] = dict(attributes or {})
        attrs["requires"] = sorted(requires)
        attrs["dimensions"] = sorted(dimensions)
        attrs["policies"] = sorted(policies)
        attrs["evidence"] = sorted(evidence)
        declared = self._kernel.register_object(
            metatype="CapabilityDeclaration",
            natural_key=key,
            namespace=CAPABILITY_NS,
            name=name or key,
            version=version,
            attributes=attrs,
        )
        return self._link_requirements(declared, attrs["requires"])

    def _link_requirements(self, declared: MetaObject, requires: Sequence[str]) -> MetaObject:
        """Record a governed kernel edge for each requirement already registered.

        A requirement naming a capability that is not registered yet, or one whose edge
        would close a cycle, is carried by the declaration attribute alone: declarations
        stay order independent, and the kernel graph stays acyclic.
        """
        current = declared
        for requirement in requires:
            target = self._lookup(requirement)
            if target is None:
                continue
            if self._kernel.registry.would_cycle(current.identity, (target.identity,)):
                continue
            current = self._kernel.compose(current.identity, REQUIRES, target.identity)
        return current

    # -- lookup + discovery ----------------------------------------------------

    @property
    def kernel(self) -> MetaKernel:
        """The kernel this planner reads from — there is no second registry."""
        return self._kernel

    def _lookup(self, key: str) -> MetaObject | None:
        for declared in self.capabilities():
            if declared.natural_key == key:
                return declared
        return None

    def capability(self, key: str) -> MetaObject:
        """The declaration of a registered capability."""
        found = self._lookup(key)
        if found is None:
            raise CapabilityUnknownError("capability is not registered", capability=key)
        return found

    def capabilities(self) -> tuple[MetaObject, ...]:
        """Every registered capability declaration, ordered by natural key."""
        found = self._kernel.discover(namespace=CAPABILITY_NS)
        return tuple(sorted(found, key=lambda o: o.natural_key))

    def capability_keys(self) -> tuple[str, ...]:
        """The natural keys of every registered capability, ordered."""
        return tuple(c.natural_key for c in self.capabilities())

    def discover(
        self,
        *,
        dimension: str | None = None,
        policy: str | None = None,
        requires: str | None = None,
    ) -> tuple[MetaObject, ...]:
        """Find capabilities by open predicates. Every capability is discoverable."""
        results = self.capabilities()
        if dimension is not None:
            results = tuple(c for c in results if dimension in c.attributes.get("dimensions", ()))
        if policy is not None:
            results = tuple(c for c in results if policy in c.attributes.get("policies", ()))
        if requires is not None:
            results = tuple(c for c in results if requires in c.attributes.get("requires", ()))
        return results

    # -- composition -----------------------------------------------------------

    def closure(self, targets: Sequence[str]) -> dict[str, tuple[str, ...]]:
        """The transitive requirement closure of ``targets`` as a dependency graph.

        Expansion is unbounded in depth and breadth; the closure is whatever the
        declarations say it is.
        """
        graph: dict[str, tuple[str, ...]] = {}
        pending = list(dict.fromkeys(targets))
        while pending:
            key = pending.pop()
            if key in graph:
                continue
            requires = tuple(self.capability(key).attributes.get("requires", ()))
            graph[key] = requires
            pending.extend(requirement for requirement in requires if requirement not in graph)
        return graph

    def plan(
        self,
        targets: Sequence[str],
        *,
        context: Sequence[str] = (),
        policies: Sequence[str] = (),
        evidence: Sequence[str] = (),
        require_evidence: bool = False,
        strategy: str = DEFAULT_STRATEGY,
    ) -> CompositionPlan:
        """Derive a composition plan from declarations, context, policies and evidence.

        ``context`` names the dimensions the caller binds; a capability requiring a
        dimension the context does not bind makes the plan unsatisfiable and is refused
        rather than silently dropped. ``policies`` names the policies in force; a capability
        governed by a policy that is not in force is likewise refused. With
        ``require_evidence`` the plan additionally refuses a capability whose declared
        evidence is not covered by ``evidence``.
        """
        if not targets:
            raise CompositionUnsatisfiedError("no composition target was requested")
        chosen = get_strategy(strategy)
        graph = self.closure(targets)
        self._assert_satisfiable(graph, context, policies, evidence, require_evidence)
        ordering = chosen(graph)
        if len(ordering) != len(graph):
            raise CompositionCycleError(
                "capability requirements contain a cycle, so no order exists",
                unresolved=unresolved_keys(graph, ordering),
            )
        steps = tuple(
            CompositionStep(
                sequence=sequence,
                wave=wave,
                capability=key,
                identity=self.capability(key).identity,
                requires=graph[key],
                dimensions=tuple(self.capability(key).attributes.get("dimensions", ())),
                policies=tuple(self.capability(key).attributes.get("policies", ())),
            )
            for sequence, (wave, key) in enumerate(ordering)
        )
        return CompositionPlan(
            targets=tuple(dict.fromkeys(targets)),
            strategy=strategy,
            steps=steps,
            context=tuple(sorted(context)),
            policies=tuple(sorted(policies)),
        )

    def _assert_satisfiable(
        self,
        graph: DependencyGraph,
        context: Sequence[str],
        policies: Sequence[str],
        evidence: Sequence[str],
        require_evidence: bool,
    ) -> None:
        """Refuse a plan whose declared dimension, policy or evidence needs are unmet."""
        bound = set(context)
        in_force = set(policies)
        supplied = set(evidence)
        for key in sorted(graph):
            declared = self.capability(key)
            unbound = sorted(set(declared.attributes.get("dimensions", ())) - bound)
            if unbound:
                raise CompositionUnsatisfiedError(
                    "capability requires a dimension the context does not bind",
                    capability=key,
                    unbound_dimensions=unbound,
                )
            ungoverned = sorted(set(declared.attributes.get("policies", ())) - in_force)
            if ungoverned:
                raise CompositionUnsatisfiedError(
                    "capability is governed by a policy that is not in force",
                    capability=key,
                    policies_not_in_force=ungoverned,
                )
            if require_evidence:
                missing = sorted(set(declared.attributes.get("evidence", ())) - supplied)
                if missing or not declared.attributes.get("evidence"):
                    raise CompositionUnsatisfiedError(
                        "capability evidence is required but not supplied",
                        capability=key,
                        missing_evidence=missing,
                    )

    # -- validation + description ----------------------------------------------

    def validate(self) -> bool:
        """True iff every declared requirement resolves to a registered capability."""
        known = set(self.capability_keys())
        for declared in self.capabilities():
            if set(declared.attributes.get("requires", ())) - known:
                return False
        return self._kernel.validate()

    def describe(self) -> dict[str, object]:
        """A deterministic, machine-readable description of the composition surface."""
        return {
            "subject": "DynamicCapabilityComposition",
            "capabilities": list(self.capability_keys()),
            "count": len(self.capabilities()),
            "strategies": strategy_names(),
            "default_strategy": DEFAULT_STRATEGY,
            "fixed_pipeline": False,
            "upper_limit": None,
        }


__all__ = [
    "CompositionPlanner",
    "CompositionPlan",
    "CompositionStep",
    "CompositionStrategy",
    "DependencyGraph",
    "dependency_order",
    "parallel_waves",
    "register_strategy",
    "get_strategy",
    "strategy_names",
    "DEFAULT_STRATEGY",
]
