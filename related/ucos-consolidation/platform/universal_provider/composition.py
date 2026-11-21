"""UPA-000010 — Provider Composition (Terminal-04).

Composition is **closed under the constitutional interface**: a composite of
providers is itself a provider (PC-12). Because a composite satisfies exactly the
same six operations as its members, a composite may be a member of another
composite, to unbounded depth, and every consumer — including the framework itself —
treats a composite and a single provider identically.

    * :class:`CompositionStrategy` — how member results combine.
    * :class:`CompositeProvider` — a provider whose substrate is other providers.
    * :func:`compose_providers` — build a composite from members.

Three strategies, each with a precise, deterministic merge rule:

    * ``FEDERATED`` — fan out to every member declaring the capability and return the
      union, ordered by ``(provider_id, resource_id)``. Nothing is dropped; resources
      remain attributed to the member that produced them.
    * ``LAYERED``   — fan out in member order and return the union deduplicated by
      ``resource_id``, first member winning. Precedence, not federation.
    * ``FALLBACK``  — try members in order and return the first non-empty response.
      Resilience: the composite serves as long as one member can.

A member fault never propagates. Under every strategy a failing member is recorded in
the response diagnostics and the composite continues with the remainder, so a
composition degrades in scope rather than failing wholesale (PC-09).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum
from platform.universal_provider.constitution import (
    PROVIDER_INTERFACE,
    PROVIDER_INTERFACE_VERSION,
    ProviderOperation,
    normalize_kind,
    normalize_provider_id,
    require_semver,
)
from platform.universal_provider.contracts import (
    Provider,
    ProviderAttestation,
    ProviderCapability,
    ProviderDependency,
    ProviderDescriptor,
    ProviderHealth,
    ProviderIdentity,
    ProviderQuery,
    ProviderResource,
    ProviderResponse,
    ProviderState,
    content_hash,
    provider_operations,
)
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderCompositionError,
    ProviderExecutionError,
    ProviderFrameworkError,
)
from typing import Any

#: Semantic version of the Provider Composition contract surface.
PROVIDER_COMPOSITION_VERSION = "1.0.0"


class CompositionStrategy(str, Enum):
    """How member results are combined into one composite result."""

    FEDERATED = "federated"
    LAYERED = "layered"
    FALLBACK = "fallback"


def _require_provider(candidate: Any, *, position: int) -> Provider:
    """Refuse any member that does not satisfy the constitutional interface (PC-01)."""
    implemented = provider_operations(candidate)
    expected = tuple(sorted(op.value for op in ProviderOperation))
    missing = [op for op in expected if op not in implemented]
    if missing:
        raise ProviderCompositionError(
            "a composition member must satisfy the one constitutional interface (PC-01)",
            {
                "position": position,
                "received": type(candidate).__name__,
                "missing_operations": missing,
            },
        )
    return candidate


class CompositeProvider:
    """A provider whose substrate is other providers (PC-12).

    Satisfies the constitutional interface exactly, so it is indistinguishable from a
    single provider to every consumer — which is what makes composition closed and
    arbitrarily nestable.
    """

    def __init__(
        self,
        identity: ProviderIdentity,
        members: Sequence[Provider],
        *,
        strategy: CompositionStrategy = CompositionStrategy.FEDERATED,
        description: str = "",
        source_of_record: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if not isinstance(identity, ProviderIdentity):
            raise ProviderCompositionError(
                "a composite requires a ProviderIdentity",
                {"received": type(identity).__name__},
            )
        if not members:
            raise ProviderCompositionError(
                "a composite requires at least one member (PC-07)",
                {"provider_id": identity.provider_id},
            )
        self._identity = identity
        self._strategy = (
            strategy
            if isinstance(strategy, CompositionStrategy)
            else CompositionStrategy(str(strategy))
        )
        self._members: tuple[Provider, ...] = tuple(
            _require_provider(member, position=index) for index, member in enumerate(members)
        )
        self._member_descriptors: tuple[ProviderDescriptor, ...] = tuple(
            member.describe() for member in self._members
        )
        self._guard_acyclic()
        self._guard_unique_members()
        self._description = description
        self._source_of_record = source_of_record or self._derive_source_of_record()
        self._metadata = dict(metadata or {})
        self._capabilities = self._merge_capabilities()
        self._descriptor = self._build_descriptor()

    # ------------------------------------------------------------------- invariants

    def _guard_acyclic(self) -> None:
        """Refuse a composite that contains itself, directly or transitively (PC-12)."""
        reachable = self._reachable_provider_ids()
        if self._identity.provider_id in reachable:
            raise ProviderCompositionError(
                "a composite may not contain itself; composition must be acyclic (PC-12)",
                {"provider_id": self._identity.provider_id, "reachable": sorted(reachable)},
            )

    def _reachable_provider_ids(self) -> set[str]:
        reachable: set[str] = set()
        for member in self._members:
            descriptor = member.describe()
            reachable.add(descriptor.provider_id)
            if isinstance(member, CompositeProvider):
                reachable |= member._reachable_provider_ids()
        return reachable

    def _guard_unique_members(self) -> None:
        ids = [descriptor.provider_id for descriptor in self._member_descriptors]
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        if duplicates:
            raise ProviderCompositionError(
                "a composite may not include the same provider twice",
                {"provider_id": self._identity.provider_id, "duplicates": duplicates},
            )

    def _derive_source_of_record(self) -> str:
        """Return a composite source of record derived from the members."""
        sources = sorted(
            {
                descriptor.source_of_record
                for descriptor in self._member_descriptors
                if descriptor.source_of_record
            }
        )
        return " + ".join(sources)

    def _merge_capabilities(self) -> tuple[ProviderCapability, ...]:
        """Merge member capabilities into the composite's declared surface.

        Same-named capabilities merge additively: selector keys union, required keys
        intersect (the composite requires only what *every* provider of that
        capability requires), determinism conjoins, effects union. A resource-kind
        disagreement is refused rather than silently coerced.
        """
        merged: dict[str, ProviderCapability] = {}
        order: list[str] = []
        for descriptor in self._member_descriptors:
            for capability in descriptor.capabilities:
                existing = merged.get(capability.name)
                if existing is None:
                    merged[capability.name] = capability
                    order.append(capability.name)
                    continue
                if existing.operation is not capability.operation:
                    raise ProviderCompositionError(
                        "members bind the same capability name to different operations",
                        {
                            "provider_id": self._identity.provider_id,
                            "capability": capability.name,
                            "operations": sorted(
                                {existing.operation.value, capability.operation.value}
                            ),
                        },
                    )
                if (
                    existing.resource_kind
                    and capability.resource_kind
                    and existing.resource_kind != capability.resource_kind
                ):
                    raise ProviderCompositionError(
                        "members declare incompatible resource kinds for one capability",
                        {
                            "provider_id": self._identity.provider_id,
                            "capability": capability.name,
                            "kinds": sorted({existing.resource_kind, capability.resource_kind}),
                        },
                    )
                merged[capability.name] = ProviderCapability(
                    name=existing.name,
                    operation=existing.operation,
                    resource_kind=existing.resource_kind or capability.resource_kind,
                    description=existing.description or capability.description,
                    selector_keys=tuple(
                        sorted(set(existing.selector_keys) | set(capability.selector_keys))
                    ),
                    required_selector_keys=tuple(
                        sorted(
                            set(existing.required_selector_keys)
                            & set(capability.required_selector_keys)
                        )
                    ),
                    deterministic=existing.deterministic and capability.deterministic,
                    effects=tuple(sorted(set(existing.effects) | set(capability.effects))),
                )
        return tuple(merged[name] for name in order)

    def _build_descriptor(self) -> ProviderDescriptor:
        return ProviderDescriptor(
            identity=self._identity,
            capabilities=self._capabilities,
            dependencies=tuple(
                ProviderDependency(
                    provider_id=descriptor.provider_id, min_version=descriptor.version
                )
                for descriptor in self._member_descriptors
            ),
            interface=PROVIDER_INTERFACE,
            interface_version=PROVIDER_INTERFACE_VERSION,
            source_of_record=self._source_of_record,
            description=self._description,
            metadata={
                **self._metadata,
                "composition_strategy": self._strategy.value,
                "composition_members": [
                    descriptor.qualified_id for descriptor in self._member_descriptors
                ],
                "composition_version": PROVIDER_COMPOSITION_VERSION,
            },
        )

    # -------------------------------------------------------- constitutional surface

    def describe(self) -> ProviderDescriptor:
        """Return the composite's own synthesized, content-addressed declaration."""
        return self._descriptor

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return the merged capability surface of the composition."""
        return self._capabilities

    def health(self) -> ProviderHealth:
        """Return aggregate health: serving only if every member is serving (PC-09)."""
        checks: dict[str, bool] = {}
        reasons: list[str] = []
        serving = 0
        for descriptor, member in zip(self._member_descriptors, self._members, strict=True):
            try:
                member_health = member.health()
                ok = member_health.state is ProviderState.SERVING
                checks[descriptor.provider_id] = ok
                if ok:
                    serving += 1
                else:
                    reasons.append(f"{descriptor.provider_id}: {member_health.state.value}")
            except Exception as exc:  # noqa: BLE001 - PC-09 fault isolation
                checks[descriptor.provider_id] = False
                reasons.append(f"{descriptor.provider_id}: health raised {type(exc).__name__}")
        if serving == len(self._members):
            return ProviderHealth(
                provider_id=self._identity.provider_id,
                state=ProviderState.SERVING,
                checks=checks,
            )
        state = ProviderState.UNAVAILABLE if serving == 0 else ProviderState.DEGRADED
        return ProviderHealth(
            provider_id=self._identity.provider_id,
            state=state,
            checks=checks,
            reasons=tuple(reasons),
        )

    def query(self, request: ProviderQuery) -> ProviderResponse:
        """Fan out ``request`` and merge member results per the strategy."""
        if not isinstance(request, ProviderQuery):
            raise ProviderCompositionError(
                "query requires a ProviderQuery", {"received": type(request).__name__}
            )
        capability = self._descriptor.capability(request.capability)
        if capability.operation is not ProviderOperation.QUERY:
            raise ProviderCapabilityError(
                "capability is not bound to the QUERY operation (PC-01)",
                {"provider_id": self._identity.provider_id, "capability": capability.name},
            )
        # PC-07: the composite must admit the request against its OWN merged capability
        # before fanning out. Delegating selector admission to the members cannot work:
        # a member's refusal is a ProviderFrameworkError, which the fan-out below
        # deliberately absorbs as fault isolation (PC-09), so an undeclared or omitted
        # selector key would silently degrade to an empty response instead of being
        # refused. The composite therefore enforces the same two admission rules the SDK
        # enforces for a single provider, against the merged surface it publishes.
        undeclared = capability.accepts(request.selector)
        if undeclared:
            raise ProviderCapabilityError(
                "query selector uses keys the merged capability did not declare (PC-04)",
                {
                    "provider_id": self._identity.provider_id,
                    "capability": capability.name,
                    "undeclared": list(undeclared),
                    "declared": list(capability.selector_keys),
                },
            )
        missing = capability.missing_required(request.selector)
        if missing:
            raise ProviderCapabilityError(
                "query selector omits keys the merged capability declared as required (PC-07)",
                {
                    "provider_id": self._identity.provider_id,
                    "capability": capability.name,
                    "missing": list(missing),
                },
            )
        participants = self._participants(request.capability)
        if not participants:
            raise ProviderCapabilityError(
                "no composition member declares this capability (PC-07)",
                {"provider_id": self._identity.provider_id, "capability": request.capability},
            )
        member_query = ProviderQuery(
            capability=request.capability,
            selector=dict(request.selector),
            limit=request.limit,
        )
        collected: list[tuple[str, ProviderResource]] = []
        degraded: dict[str, str] = {}
        contributions: dict[str, int] = {}
        for descriptor, member in participants:
            try:
                response = member.query(member_query)
            except ProviderFrameworkError as exc:
                degraded[descriptor.provider_id] = exc.code
                continue
            except Exception as exc:  # noqa: BLE001 - PC-09 fault isolation
                degraded[descriptor.provider_id] = f"untyped:{type(exc).__name__}"
                continue
            if not isinstance(response, ProviderResponse):
                degraded[descriptor.provider_id] = "non-response"
                continue
            contributions[descriptor.provider_id] = len(response.resources)
            for resource in response.resources:
                collected.append((descriptor.provider_id, resource))
            if self._strategy is CompositionStrategy.FALLBACK and response.resources:
                break
        resources = self._merge_resources(collected)
        page = resources[: request.limit]
        return ProviderResponse(
            provider_id=self._identity.provider_id,
            capability=request.capability,
            query_fingerprint=request.fingerprint(),
            resources=page,
            truncated=len(page) < len(resources),
            next_cursor=str(len(page)) if len(page) < len(resources) else "",
            diagnostics={
                "strategy": self._strategy.value,
                "participants": [descriptor.provider_id for descriptor, _ in participants],
                "contributions": contributions,
                "degraded": degraded,
                "matched": len(resources),
                "returned": len(page),
            },
        )

    def fetch(self, resource_id: str) -> ProviderResource:
        """Return the first member resolution of ``resource_id``, else fail closed."""
        attempts: dict[str, str] = {}
        for descriptor, member in zip(self._member_descriptors, self._members, strict=True):
            try:
                return member.fetch(resource_id)
            except ProviderFrameworkError as exc:
                attempts[descriptor.provider_id] = exc.code
            except Exception as exc:  # noqa: BLE001 - PC-09 fault isolation
                attempts[descriptor.provider_id] = f"untyped:{type(exc).__name__}"
        raise ProviderExecutionError(
            "no composition member could resolve the resource (fail closed, PC-07)",
            {
                "provider_id": self._identity.provider_id,
                "resource_id": resource_id,
                "attempts": attempts,
            },
        )

    def verify(self, resource_id: str) -> ProviderAttestation:
        """Delegate attestation to the member that can resolve ``resource_id``.

        The composite never re-attests: provenance stays with the provider that owns
        the source of record, and the composite's own identity is appended to the
        chain so the conveyance is itself attributable (PC-06).
        """
        for member in self._members:
            try:
                member.fetch(resource_id)
            except ProviderFrameworkError:  # noqa: S112 - probing the next member is the strategy
                continue
            except Exception:  # noqa: BLE001, S112 - PC-09 fault isolation
                continue
            attestation = member.verify(resource_id)
            if not attestation.verified:
                return attestation
            return ProviderAttestation(
                provider_id=self._identity.provider_id,
                resource_id=attestation.resource_id,
                resource_hash=attestation.resource_hash,
                verified=True,
                provenance_chain=(
                    *attestation.provenance_chain,
                    self._identity.qualified_id,
                ),
                reasons=attestation.reasons,
            )
        return ProviderAttestation(
            provider_id=self._identity.provider_id,
            resource_id=resource_id,
            resource_hash="",
            verified=False,
            provenance_chain=(),
            reasons=("no composition member could resolve the resource",),
        )

    # --------------------------------------------------------------------- internals

    def _participants(
        self, capability_name: str
    ) -> tuple[tuple[ProviderDescriptor, Provider], ...]:
        """Return members declaring ``capability_name``, in member order."""
        participants: list[tuple[ProviderDescriptor, Provider]] = []
        for descriptor, member in zip(self._member_descriptors, self._members, strict=True):
            if any(c.name == capability_name for c in descriptor.capabilities):
                participants.append((descriptor, member))
        return tuple(participants)

    def _merge_resources(
        self, collected: Sequence[tuple[str, ProviderResource]]
    ) -> tuple[ProviderResource, ...]:
        """Apply the strategy's deterministic merge rule."""
        if self._strategy is CompositionStrategy.FEDERATED:
            unique: dict[tuple[str, str], ProviderResource] = {}
            for provider_id, resource in collected:
                unique.setdefault((provider_id, resource.resource_id), resource)
            return tuple(unique[key] for key in sorted(unique, key=lambda item: (item[0], item[1])))
        first_wins: dict[str, ProviderResource] = {}
        for _, resource in collected:
            first_wins.setdefault(resource.resource_id, resource)
        return tuple(first_wins.values())

    @property
    def members(self) -> tuple[Provider, ...]:
        return self._members

    @property
    def strategy(self) -> CompositionStrategy:
        return self._strategy

    def composition_hash(self) -> str:
        """Return the content hash pinning this exact composition."""
        return content_hash(
            {
                "provider_id": self._identity.provider_id,
                "version": self._identity.version,
                "strategy": self._strategy.value,
                "members": [descriptor.content_hash() for descriptor in self._member_descriptors],
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "composition_version": PROVIDER_COMPOSITION_VERSION,
            "identity": self._identity.to_dict(),
            "strategy": self._strategy.value,
            "members": [descriptor.qualified_id for descriptor in self._member_descriptors],
            "capabilities": [capability.name for capability in self._capabilities],
            "composition_hash": self.composition_hash(),
        }


def compose_providers(
    provider_id: str,
    kind: str,
    version: str,
    members: Sequence[Provider],
    *,
    strategy: CompositionStrategy | str = CompositionStrategy.FEDERATED,
    name: str = "",
    authority: str = "",
    description: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> CompositeProvider:
    """Compose ``members`` into a single provider (PC-12).

    ``kind`` is supplied by the caller as data: the framework does not invent a
    reserved "composite" kind, because doing so would put one privileged kind into the
    architecture and violate PC-02.
    """
    identity = ProviderIdentity(
        provider_id=normalize_provider_id(provider_id),
        kind=normalize_kind(kind),
        version=require_semver(version),
        name=name,
        authority=authority,
    )
    return CompositeProvider(
        identity=identity,
        members=members,
        strategy=(
            strategy if isinstance(strategy, CompositionStrategy) else CompositionStrategy(strategy)
        ),
        description=description,
        metadata=metadata,
    )


__all__ = [
    "PROVIDER_COMPOSITION_VERSION",
    "CompositeProvider",
    "CompositionStrategy",
    "compose_providers",
]
