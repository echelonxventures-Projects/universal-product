"""The Universal Provider Framework facade — realization over the immutable kernel.

:class:`ProviderFramework` holds a :class:`~engine.kernel.kernel.MetaKernel` and exposes
the universal provider mechanisms the mission requires — registration, capability
advertisement, discovery, resolution, selection, negotiation, compatibility, composition,
lifecycle, health, governance, validation, certification, and traceability — each built on
kernel primitives. It modifies neither the kernel nor any other package.

Modelling:
    * a provider **category** is a kernel meta-type (open set) tagged
      :data:`~engine.provider.metatypes.CATEGORY_ROLE`;
    * a **provider** is a kernel ``MetaObject`` classified by its category meta-type,
      carrying its contract, capabilities, metadata, health and lifecycle as open
      attributes, and its dependencies / policy / context as governed relationships.

Everything is deterministic: no wall-clock, no RNG.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.foundation.contracts.contract import Version
from engine.kernel.governance import Constraint
from engine.kernel.kernel import MetaKernel
from engine.kernel.meta import MetaObject
from engine.provider.errors import (
    ProviderCategoryUnknownError,
    ProviderContractError,
    ProviderResolutionError,
)
from engine.provider.metatypes import (
    CATEGORY_ROLE,
    PROVIDER_CATEGORY_NS,
    PROVIDER_FACETS,
    PROVIDER_INSTANCE_NS,
    PROVIDER_META_NS,
)
from engine.provider.selection import DEFAULT_STRATEGY, get_strategy


@dataclass(frozen=True)
class NegotiationResult:
    """The outcome of negotiating a set of requirements against one provider."""

    provider: str
    compatible: bool
    matched_capabilities: tuple[str, ...]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serialisable rendering of the negotiation."""
        return {
            "provider": self.provider,
            "compatible": self.compatible,
            "matched_capabilities": list(self.matched_capabilities),
            "reasons": list(self.reasons),
        }


class ProviderFramework:
    """The kernel realization layer: providers as governed, open kernel meta-objects."""

    __slots__ = ("_kernel",)

    version = "1.0.0"

    def __init__(self, *, kernel: MetaKernel | None = None) -> None:
        self._kernel = kernel if kernel is not None else MetaKernel()
        self._seed_facets()
        self._bind_governance()

    # -- seeding + governance --------------------------------------------------

    def _seed_facets(self) -> None:
        """Register the provider facet vocabulary as kernel meta-types (DATA)."""
        for natural_key, description in PROVIDER_FACETS:
            if natural_key not in self._kernel.registry.metatype_keys():
                self._kernel.register_metatype(
                    natural_key,
                    name=natural_key,
                    description=description,
                    namespace=PROVIDER_META_NS,
                )

    def _bind_governance(self) -> None:
        """Register provider governance constraints into the kernel (no kernel edit).

        Each constraint is scoped to provider instances, so it is a no-op for every other
        kind of meta-object. This uses the kernel's open governance extension point.
        """
        gov = self._kernel.governance
        existing = set(gov.admission.constraint_names())
        for name, check in (
            ("provider-has-category", self._check_has_category),
            ("provider-advertises-capability", self._check_capability),
            ("provider-declares-contract", self._check_contract),
        ):
            if name not in existing:
                gov.register_constraint(Constraint(name, check))

    # -- provider governance constraints (scoped to provider instances) --------

    def _check_has_category(self, candidate: MetaObject, _view: Any) -> tuple[bool, str]:
        """A provider instance must be classified by a registered provider category."""
        if candidate.namespace != PROVIDER_INSTANCE_NS:
            return True, ""
        if candidate.metatype in self.category_keys():
            return True, ""
        return False, f"provider category not registered: {candidate.metatype!r}"

    def _check_capability(self, candidate: MetaObject, _view: Any) -> tuple[bool, str]:
        """A provider instance must advertise at least one capability."""
        if candidate.namespace != PROVIDER_INSTANCE_NS:
            return True, ""
        caps = candidate.attributes.get("capabilities")
        if isinstance(caps, list | tuple) and len(caps) >= 1:
            return True, ""
        return False, "provider advertises no capability"

    def _check_contract(self, candidate: MetaObject, _view: Any) -> tuple[bool, str]:
        """A provider instance must declare a well-formed contract (name + version)."""
        if candidate.namespace != PROVIDER_INSTANCE_NS:
            return True, ""
        if _contract_is_wellformed(candidate.attributes.get("contract")):
            return True, ""
        return False, "provider declares no well-formed contract"

    # -- accessors -------------------------------------------------------------

    @property
    def kernel(self) -> MetaKernel:
        """The underlying immutable Universal Meta-Kernel."""
        return self._kernel

    def categories(self) -> tuple[MetaObject, ...]:
        """Every registered provider category (open set), id-ordered."""
        return tuple(
            mt for mt in self._kernel.metatypes() if mt.attributes.get("role") == CATEGORY_ROLE
        )

    def category_keys(self) -> tuple[str, ...]:
        """The natural keys of every registered provider category."""
        return tuple(sorted(c.natural_key for c in self.categories()))

    # -- registration ----------------------------------------------------------

    def register_category(
        self,
        key: str,
        *,
        name: str = "",
        description: str = "",
        attributes: Mapping[str, Any] | None = None,
    ) -> MetaObject:
        """Register a provider category (a kernel meta-type). Open by registration."""
        attrs = dict(attributes or {})
        attrs["role"] = CATEGORY_ROLE
        return self._kernel.register_metatype(
            key,
            name=name or key,
            description=description or f"Provider category {key}.",
            namespace=PROVIDER_CATEGORY_NS,
            attributes=attrs,
        )

    def register_provider(
        self,
        *,
        category: str,
        key: str,
        capabilities: Sequence[str],
        contract: Mapping[str, Any],
        name: str = "",
        version: str | Version = "1.0.0",
        metadata: Mapping[str, Any] | None = None,
        health: Mapping[str, Any] | None = None,
        lifecycle: str = "registered",
        dependencies: Sequence[str] = (),
        policy_bindings: Sequence[str] = (),
        context_bindings: Sequence[str] = (),
    ) -> MetaObject:
        """Register a concrete provider classified by an (already registered) category."""
        if category not in self.category_keys():
            raise ProviderCategoryUnknownError(
                "provider category is not registered (register it first)", category=category
            )
        if not capabilities:
            raise ProviderContractError("a provider must advertise at least one capability")
        if not _contract_is_wellformed(contract):
            raise ProviderContractError(
                "contract must be a mapping with a name and a semantic version",
                contract=dict(contract) if isinstance(contract, Mapping) else contract,
            )
        attributes = {
            "capabilities": sorted(str(c) for c in capabilities),
            "contract": {"name": str(contract["name"]), "version": str(contract["version"])},
            "metadata": dict(metadata or {}),
            "health": dict(health or {"status": "unknown"}),
            "lifecycle": str(lifecycle),
        }
        relationships = (
            [{"relation": "depends-on", "target": str(d)} for d in dependencies]
            + [{"relation": "bound-policy", "target": str(p)} for p in policy_bindings]
            + [{"relation": "bound-context", "target": str(c)} for c in context_bindings]
        )
        return self._kernel.register_object(
            metatype=category,
            natural_key=key,
            namespace=PROVIDER_INSTANCE_NS,
            name=name or key,
            version=version,
            attributes=attributes,
            relationships=relationships,
        )

    # -- discovery / resolution / selection / negotiation ----------------------

    def providers(self, *, category: str | None = None) -> tuple[MetaObject, ...]:
        """Every registered provider instance, optionally filtered by category."""
        out = [
            obj
            for obj in self._kernel.registry.instances()
            if obj.namespace == PROVIDER_INSTANCE_NS
            and (category is None or obj.metatype == category)
        ]
        return tuple(sorted(out, key=lambda o: o.identity))

    def discover(
        self,
        *,
        capability: str | None = None,
        category: str | None = None,
        context: str | None = None,
    ) -> tuple[MetaObject, ...]:
        """Find providers advertising a capability / in a category / bound to a context."""
        results = self.providers(category=category)
        if capability is not None:
            results = tuple(
                p for p in results if capability in p.attributes.get("capabilities", ())
            )
        if context is not None:
            results = tuple(p for p in results if context in p.related("bound-context"))
        return results

    def resolve(
        self,
        capability: str,
        *,
        requirements: Mapping[str, Any] | None = None,
        category: str | None = None,
        strategy: str = DEFAULT_STRATEGY,
    ) -> MetaObject:
        """Resolve a capability to the single best compatible provider, or raise."""
        reqs = dict(requirements or {})
        reqs.setdefault("capability", capability)
        candidates = [
            p
            for p in self.discover(capability=capability, category=category)
            if self.negotiate(reqs, p).compatible
        ]
        if not candidates:
            raise ProviderResolutionError(
                "no compatible provider for capability", capability=capability
            )
        return self.select(candidates, requirements=reqs, strategy=strategy)[0]

    def select(
        self,
        candidates: Sequence[MetaObject],
        *,
        requirements: Mapping[str, Any] | None = None,
        strategy: str = DEFAULT_STRATEGY,
    ) -> list[MetaObject]:
        """Order candidate providers best-first using a registered selection strategy."""
        return get_strategy(strategy)(candidates, dict(requirements or {}))

    def negotiate(self, requirements: Mapping[str, Any], provider: MetaObject) -> NegotiationResult:
        """Negotiate requirements against a provider; report compatibility + reasons."""
        reasons: list[str] = []
        caps = tuple(provider.attributes.get("capabilities", ()))
        matched: list[str] = []

        wanted_cap = requirements.get("capability")
        if wanted_cap is not None:
            if wanted_cap in caps:
                matched.append(str(wanted_cap))
            else:
                reasons.append(f"capability not advertised: {wanted_cap!r}")

        contract = provider.attributes.get("contract") or {}
        wanted_contract = requirements.get("contract")
        if wanted_contract is not None and str(contract.get("name")) != str(wanted_contract):
            reasons.append(
                f"contract name mismatch: wanted {wanted_contract!r}, have {contract.get('name')!r}"
            )

        min_version = requirements.get("min_version")
        if min_version is not None and not self.compatible(str(min_version), provider):
            reasons.append(
                f"contract version {contract.get('version')!r} < required {min_version!r}"
            )

        return NegotiationResult(
            provider=provider.identity,
            compatible=not reasons,
            matched_capabilities=tuple(sorted(matched)),
            reasons=tuple(reasons),
        )

    def compatible(self, min_version: str, provider: MetaObject) -> bool:
        """True iff the provider's contract version is backward-compatible with ``min_version``."""
        contract = provider.attributes.get("contract") or {}
        try:
            have = Version.parse(str(contract.get("version")))
            need = Version.parse(str(min_version))
        except Exception:  # noqa: BLE001 — a malformed version is treated as incompatible
            return False
        return have.is_backward_compatible_with(need)

    # -- composition / lifecycle / health / trace -----------------------------

    def compose(self, provider: str, relation: str, target: str) -> MetaObject:
        """Compose a provider with another meta-object via a governed relationship."""
        return self._kernel.compose(provider, relation, target)

    def transition(self, provider: str, to_state: str) -> MetaObject:
        """Advance a provider to a new (open) lifecycle state, recorded as a new version."""
        current = self._kernel.registry.get(provider)
        attributes = dict(current.attributes)
        attributes["lifecycle"] = str(to_state)
        nxt = Version(current.version.major, current.version.minor, current.version.patch + 1)
        return self._kernel.evolve(provider, nxt, attributes=attributes)

    def health(self, provider: str) -> dict[str, Any]:
        """Return the advertised health of a provider plus a derived serving flag."""
        obj = self._kernel.registry.get(provider)
        health = dict(obj.attributes.get("health") or {})
        status = str(health.get("status", "unknown")).lower()
        return {
            "provider": provider,
            "status": status,
            "serving": status != "unavailable",
            "detail": health,
        }

    def trace(self, provider: str) -> dict[str, Any]:
        """Return the traceable lineage of a provider (kernel trace)."""
        return self._kernel.trace(provider)

    # -- validation / certification / description ------------------------------

    def validate(self) -> bool:
        """Validate kernel integrity + provider invariants across all registrations."""
        if not self._kernel.validate():
            return False
        category_keys = set(self.category_keys())
        for provider in self.providers():
            if provider.metatype not in category_keys:
                return False
            if not provider.attributes.get("capabilities"):
                return False
            if not _contract_is_wellformed(provider.attributes.get("contract")):
                return False
        return True

    def certify(self) -> dict[str, Any]:
        """Emit a deterministic self-certification of the provider framework."""
        valid = self.validate()
        return {
            "subject": "UniversalProviderFramework",
            "framework_version": self.version,
            "determination": "CERTIFIED" if valid else "REJECTED",
            "categories": len(self.categories()),
            "providers": len(self.providers()),
            "kernel": self._kernel.certify(),
        }

    def describe(self) -> dict[str, Any]:
        """A deterministic, machine-readable description of the framework."""
        return {
            "framework": "UCOS Universal Provider Framework",
            "version": self.version,
            "realizes_over_kernel": self._kernel.version,
            "facets": [key for key, _d in PROVIDER_FACETS],
            "categories": list(self.category_keys()),
            "providers": len(self.providers()),
            "governance": self._kernel.governance.describe(),
            "open_world": True,
        }


def _contract_is_wellformed(contract: Any) -> bool:
    """True iff ``contract`` is a mapping carrying a name and a valid semantic version."""
    if not isinstance(contract, Mapping):
        return False
    if not str(contract.get("name", "")).strip():
        return False
    try:
        Version.parse(str(contract.get("version")))
    except Exception:  # noqa: BLE001 — malformed version => not well-formed
        return False
    return True


__all__ = ["ProviderFramework", "NegotiationResult"]
