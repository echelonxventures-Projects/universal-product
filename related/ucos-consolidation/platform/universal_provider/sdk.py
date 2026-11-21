"""UPA-000004 — Provider SDK (Terminal-04).

The SDK is how a provider author obtains constitutional conformance **by default**.
:class:`BaseProvider` implements the whole constitutional interface and enforces the
constitution on every call; the author supplies only substrate access through three
narrow hooks:

    * :meth:`BaseProvider.resolve_query`    — yield resources for a declared capability.
    * :meth:`BaseProvider.resolve_resource` — resolve one resource id, or ``None``.
    * :meth:`BaseProvider.probe`            — report substrate health checks.

Everything constitutional is handled for the author and cannot be opted out of:

    * capability resolution and undeclared-capability refusal (PC-04, PC-07);
    * selector-key admission against the declared surface (PC-04);
    * deterministic ordering and stable pagination (PC-05);
    * provenance and content-hash enforcement on every returned resource (PC-06);
    * fault isolation — an author exception becomes a typed
      :class:`ProviderExecutionError`, never an escaping crash (PC-09);
    * attestation derivation, so ``verify`` is correct without author effort (PC-06).

The SDK contains no knowledge of any provider kind. It is the same SDK for a
repository provider and for a provider class that does not exist yet (PC-02, PC-14).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping, Sequence
from platform.universal_provider.constitution import (
    PROVIDER_INTERFACE,
    PROVIDER_INTERFACE_VERSION,
    SUBSTRATE_OPERATIONS,
    ProviderOperation,
)
from platform.universal_provider.contracts import (
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
)
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderContractError,
    ProviderExecutionError,
    ProviderFrameworkError,
)
from typing import Any

#: Semantic version of the Provider SDK surface.
PROVIDER_SDK_VERSION = "1.0.0"


def declare_capability(
    name: str,
    operation: ProviderOperation | str,
    *,
    resource_kind: str = "",
    description: str = "",
    selector_keys: Sequence[str] = (),
    required_selector_keys: Sequence[str] = (),
    deterministic: bool = True,
    effects: Sequence[str] = (),
) -> ProviderCapability:
    """Declare one capability (PC-04).

    A thin, keyword-only front door onto :class:`ProviderCapability` so a provider's
    declaration reads as a declaration rather than as construction.
    """
    return ProviderCapability(
        name=name,
        operation=(
            operation if isinstance(operation, ProviderOperation) else ProviderOperation(operation)
        ),
        resource_kind=resource_kind,
        description=description,
        selector_keys=tuple(selector_keys),
        required_selector_keys=tuple(required_selector_keys),
        deterministic=deterministic,
        effects=tuple(effects),
    )


def declare_dependency(
    provider_id: str,
    *,
    min_version: str = "0.0.0",
    optional: bool = False,
    alias: str = "",
) -> ProviderDependency:
    """Declare a by-reference dependency on another provider (PC-12)."""
    return ProviderDependency(
        provider_id=provider_id, min_version=min_version, optional=optional, alias=alias
    )


def declare_provider(
    provider_id: str,
    kind: str,
    version: str,
    *,
    name: str = "",
    authority: str = "",
    description: str = "",
    source_of_record: str = "",
    entry_point: str = "",
    capabilities: Sequence[ProviderCapability] = (),
    dependencies: Sequence[ProviderDependency] = (),
    config_schema: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> ProviderDescriptor:
    """Declare a complete provider descriptor (PC-03).

    ``kind`` is an open slug carried as data — the SDK validates its form and never
    its membership, so this one function declares every provider that will ever
    exist (PC-02 / PC-14).
    """
    return ProviderDescriptor(
        identity=ProviderIdentity(
            provider_id=provider_id, kind=kind, version=version, name=name, authority=authority
        ),
        capabilities=tuple(capabilities),
        dependencies=tuple(dependencies),
        interface=PROVIDER_INTERFACE,
        interface_version=PROVIDER_INTERFACE_VERSION,
        entry_point=entry_point,
        source_of_record=source_of_record,
        description=description,
        config_schema=dict(config_schema or {}),
        metadata=dict(metadata or {}),
    )


class BaseProvider(ABC):
    """The constitutional base every provider should extend.

    Subclasses supply a descriptor plus substrate access. The base class supplies —
    and enforces — the constitution.
    """

    def __init__(
        self, descriptor: ProviderDescriptor, config: Mapping[str, Any] | None = None
    ) -> None:
        if not isinstance(descriptor, ProviderDescriptor):
            raise ProviderContractError(
                "a provider must be constructed with a ProviderDescriptor",
                {"received": type(descriptor).__name__},
            )
        missing_operations = tuple(
            operation.value
            for operation in SUBSTRATE_OPERATIONS
            if not descriptor.capabilities_for(operation)
        )
        if missing_operations:
            raise ProviderCapabilityError(
                "a provider must declare at least one capability per substrate operation (PC-04)",
                {
                    "provider_id": descriptor.provider_id,
                    "undeclared_operations": list(missing_operations),
                },
            )
        self._descriptor = descriptor
        self._config: dict[str, Any] = dict(config or {})

    # ------------------------------------------------------------------ intrinsics

    def describe(self) -> ProviderDescriptor:
        """Return this provider's own content-addressed declaration."""
        return self._descriptor

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return the declared capability set, in declared order."""
        return self._descriptor.capabilities

    def health(self) -> ProviderHealth:
        """Return structural serviceability, isolating any probe fault (PC-09).

        A probe that raises does not propagate: it is recorded as a failed check and
        an ``UNAVAILABLE`` state, so an unhealthy provider degrades its own scope and
        nothing else.
        """
        try:
            checks = dict(self.probe())
        except Exception as exc:  # noqa: BLE001 - PC-09 fault isolation is the point
            return ProviderHealth(
                provider_id=self._descriptor.provider_id,
                state=ProviderState.UNAVAILABLE,
                checks={"probe": False},
                reasons=(f"probe raised {type(exc).__name__}",),
            )
        failed = tuple(sorted(name for name, ok in checks.items() if not ok))
        if not failed:
            return ProviderHealth(
                provider_id=self._descriptor.provider_id,
                state=ProviderState.SERVING,
                checks=checks,
            )
        state = ProviderState.UNAVAILABLE if len(failed) == len(checks) else ProviderState.DEGRADED
        return ProviderHealth(
            provider_id=self._descriptor.provider_id,
            state=state,
            checks=checks,
            reasons=tuple(f"check failed: {name}" for name in failed),
        )

    # ------------------------------------------------------------------- substrate

    def query(self, request: ProviderQuery) -> ProviderResponse:
        """Return zero or more resources for a **declared** capability.

        Enforces PC-04 (declared capability, declared selector keys), PC-05
        (deterministic ordering and stable pagination), PC-06 (provenance on every
        resource), PC-07 (fail closed) and PC-09 (fault isolation).
        """
        if not isinstance(request, ProviderQuery):
            raise ProviderContractError(
                "query requires a ProviderQuery", {"received": type(request).__name__}
            )
        capability = self._descriptor.capability(request.capability)
        if capability.operation is not ProviderOperation.QUERY:
            raise ProviderCapabilityError(
                "capability is not bound to the QUERY operation (PC-01)",
                {
                    "provider_id": self._descriptor.provider_id,
                    "capability": capability.name,
                    "operation": capability.operation.value,
                },
            )
        undeclared = capability.accepts(request.selector)
        if undeclared:
            raise ProviderCapabilityError(
                "query selector uses keys the capability did not declare (PC-04)",
                {
                    "provider_id": self._descriptor.provider_id,
                    "capability": capability.name,
                    "undeclared": list(undeclared),
                    "declared": list(capability.selector_keys),
                },
            )
        missing = capability.missing_required(request.selector)
        if missing:
            raise ProviderCapabilityError(
                "query selector omits keys the capability declared as required (PC-07)",
                {
                    "provider_id": self._descriptor.provider_id,
                    "capability": capability.name,
                    "missing": list(missing),
                },
            )
        resolved = self._isolate(
            "query",
            lambda: tuple(self.resolve_query(capability, request)),
            capability=capability.name,
        )
        resources = self._admit(resolved, capability=capability)
        if capability.deterministic:
            resources = tuple(sorted(resources, key=lambda item: item.resource_id))
        offset = self._cursor_offset(request.cursor)
        page = resources[offset : offset + request.limit]
        consumed = offset + len(page)
        truncated = consumed < len(resources)
        return ProviderResponse(
            provider_id=self._descriptor.provider_id,
            capability=capability.name,
            query_fingerprint=request.fingerprint(),
            resources=page,
            truncated=truncated,
            next_cursor=str(consumed) if truncated else "",
            diagnostics={"matched": len(resources), "returned": len(page), "offset": offset},
        )

    def fetch(self, resource_id: str) -> ProviderResource:
        """Return exactly one resource, or fail closed (PC-07)."""
        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ProviderContractError(
                "fetch requires a non-empty resource id", {"resource_id": repr(resource_id)}
            )
        resolved = self._isolate(
            "fetch", lambda: self.resolve_resource(resource_id), resource_id=resource_id
        )
        if resolved is None:
            raise ProviderExecutionError(
                "resource not found (fail closed, PC-07)",
                {"provider_id": self._descriptor.provider_id, "resource_id": resource_id},
            )
        (admitted,) = self._admit((resolved,), capability=None)
        return admitted

    def verify(self, resource_id: str) -> ProviderAttestation:
        """Return an integrity + provenance attestation over ``resource_id`` (PC-06).

        Derived, not asserted: the resource is re-resolved, its content hash
        recomputed over the canonical payload, and the provenance chain built from
        the resource's own declared source of record. A resource that cannot be
        re-resolved yields an unverified attestation rather than an exception, so a
        consumer can distinguish "absent" from "tampered".
        """
        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ProviderContractError(
                "verify requires a non-empty resource id", {"resource_id": repr(resource_id)}
            )
        try:
            resource = self.fetch(resource_id)
        except ProviderFrameworkError as exc:
            return ProviderAttestation(
                provider_id=self._descriptor.provider_id,
                resource_id=resource_id,
                resource_hash="",
                verified=False,
                provenance_chain=(),
                reasons=(f"unresolvable: {exc.code}",),
            )
        chain = self.provenance_chain(resource)
        if not chain:
            return ProviderAttestation(
                provider_id=self._descriptor.provider_id,
                resource_id=resource.resource_id,
                resource_hash=resource.resource_hash,
                verified=False,
                provenance_chain=(),
                reasons=("empty provenance chain (PC-06)",),
            )
        return ProviderAttestation(
            provider_id=self._descriptor.provider_id,
            resource_id=resource.resource_id,
            resource_hash=resource.resource_hash,
            verified=True,
            provenance_chain=chain,
        )

    # ----------------------------------------------------------------- author hooks

    @abstractmethod
    def resolve_query(
        self, capability: ProviderCapability, request: ProviderQuery
    ) -> Iterable[ProviderResource]:
        """Yield every resource matching ``request`` for ``capability``.

        The hook may return them in any order and need not paginate: the base class
        orders deterministically and paginates. It must not filter by ``limit``.
        """

    @abstractmethod
    def resolve_resource(self, resource_id: str) -> ProviderResource | None:
        """Return the resource identified by ``resource_id``, or ``None`` if absent."""

    def probe(self) -> Mapping[str, bool]:
        """Return substrate health checks. Default: no checks, therefore serving."""
        return {}

    def provenance_chain(self, resource: ProviderResource) -> tuple[str, ...]:
        """Return the provenance chain for ``resource`` (override to extend).

        The default chain is ``(source_of_record, provider@version)`` — the minimum
        that makes a resource attributable to both its origin and its conveyor.
        """
        source = str(resource.provenance.get("source_of_record") or "")
        return (source, self._descriptor.qualified_id)

    # --------------------------------------------------------------------- helpers

    @property
    def config(self) -> dict[str, Any]:
        """Return a copy of the provider's resolved configuration."""
        return dict(self._config)

    def resource(
        self,
        resource_id: str,
        kind: str,
        payload: Mapping[str, Any],
        *,
        provenance: Mapping[str, Any] | None = None,
    ) -> ProviderResource:
        """Build a conformant :class:`ProviderResource` (PC-06).

        Injects ``provider_id`` and defaults ``provenance.source_of_record`` to the
        descriptor's declared source of record, so an author cannot accidentally emit
        an unattributable resource.
        """
        merged = dict(provenance or {})
        merged.setdefault("source_of_record", self._descriptor.source_of_record)
        return ProviderResource(
            resource_id=resource_id,
            kind=kind,
            provider_id=self._descriptor.provider_id,
            payload=dict(payload),
            provenance=merged,
        )

    def _isolate(self, operation: str, call: Any, **detail: Any) -> Any:
        """Run ``call``, converting any non-framework fault into a typed error (PC-09)."""
        try:
            return call()
        except ProviderFrameworkError:
            raise
        except Exception as exc:  # noqa: BLE001 - PC-09 fault isolation is the point
            raise ProviderExecutionError(
                f"provider operation {operation!r} failed",
                {
                    "provider_id": self._descriptor.provider_id,
                    "operation": operation,
                    "cause": f"{type(exc).__name__}: {exc}",
                    **detail,
                },
            ) from exc

    def _admit(
        self, resources: Sequence[Any], *, capability: ProviderCapability | None
    ) -> tuple[ProviderResource, ...]:
        """Refuse any resource that is not attributable to this provider (PC-06)."""
        admitted: list[ProviderResource] = []
        for item in resources:
            if not isinstance(item, ProviderResource):
                raise ProviderContractError(
                    "a provider may only return ProviderResource values",
                    {
                        "provider_id": self._descriptor.provider_id,
                        "received": type(item).__name__,
                    },
                )
            if item.provider_id != self._descriptor.provider_id:
                raise ProviderContractError(
                    "a provider may not attribute a resource to another provider (PC-06)",
                    {
                        "provider_id": self._descriptor.provider_id,
                        "attributed_to": item.provider_id,
                        "resource_id": item.resource_id,
                    },
                )
            if (
                capability is not None
                and capability.resource_kind
                and item.kind != capability.resource_kind
            ):
                raise ProviderContractError(
                    "resource kind does not match the capability's declared kind (PC-04)",
                    {
                        "provider_id": self._descriptor.provider_id,
                        "capability": capability.name,
                        "declared_kind": capability.resource_kind,
                        "resource_kind": item.kind,
                        "resource_id": item.resource_id,
                    },
                )
            admitted.append(item)
        return tuple(admitted)

    @staticmethod
    def _cursor_offset(cursor: str) -> int:
        """Return the integer offset encoded by ``cursor``, failing closed (PC-07)."""
        if not cursor:
            return 0
        try:
            offset = int(cursor)
        except ValueError as exc:
            raise ProviderContractError(
                "query cursor is not a valid framework cursor", {"cursor": cursor}
            ) from exc
        if offset < 0:
            raise ProviderContractError("query cursor may not be negative", {"cursor": cursor})
        return offset


__all__ = [
    "PROVIDER_SDK_VERSION",
    "BaseProvider",
    "declare_capability",
    "declare_dependency",
    "declare_provider",
]
