"""UPA-000003 — Universal Provider contracts (Terminal-04).

The value types that cross the **one constitutional provider boundary**. Every type
here is immutable, typed, deterministic, and serializable, and holds no runtime state
(no handles, no wall-clock, no provider instances), so identical inputs over an
identical substrate yield byte-identical results and stable content hashes.

    * :class:`ProviderIdentity`    — who the provider is (id, open kind, version).
    * :class:`ProviderCapability`  — one declared capability (PC-04/PC-05/PC-08).
    * :class:`ProviderDependency`  — a provider this provider composes by reference.
    * :class:`ProviderDescriptor`  — the complete, content-addressed declaration.
    * :class:`ProviderQuery`       — the universal read-many request.
    * :class:`ProviderResource`    — one provider-returned unit, with provenance.
    * :class:`ProviderResponse`    — the universal read-many result.
    * :class:`ProviderHealth`      — structural serviceability.
    * :class:`ProviderAttestation` — integrity + provenance over one resource.
    * :class:`Provider`            — the runtime protocol: six operations, no more.

Nothing in this module knows that a repository, a patent office, or a market feed
exists. Provider *kind* is an open string carried as data (PC-02).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from platform.universal_provider.constitution import (
    PROVIDER_INTERFACE,
    PROVIDER_INTERFACE_VERSION,
    ProviderOperation,
    normalize_kind,
    normalize_provider_id,
    require_semver,
)
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderContractError,
)
from typing import Any, Protocol, runtime_checkable

# The canonical serialization primitive has exactly one definition, in UCKP Layer Zero
# (UCKP-LAW-0001 Art-13, UCKP-INV-03). Re-exported unchanged for existing callers.
from engine.uckp.canonical import canonical_json, content_hash

#: Semantic version of the provider contract surface (AR-03 / PL-05).
PROVIDER_CONTRACT_VERSION = "1.0.0"

#: Default page size applied when a query declares no limit.
DEFAULT_QUERY_LIMIT = 100

#: Hard ceiling on a single page, so a provider cannot be coerced into unbounded work.
MAX_QUERY_LIMIT = 10_000


def _require_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProviderContractError(
            f"{field_name} is required and must be a non-empty string",
            {"field": field_name, "value": repr(value)},
        )
    return value


def _freeze_mapping(value: Mapping[str, Any] | None, *, field_name: str) -> dict[str, Any]:
    """Return a JSON-safe copy of ``value``, refusing unserializable content."""
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ProviderContractError(
            f"{field_name} must be a mapping", {"field": field_name, "value": repr(value)}
        )
    plain = {str(key): value[key] for key in value}
    try:
        canonical_json(plain)
    except (TypeError, ValueError) as exc:
        raise ProviderContractError(
            f"{field_name} must be JSON-serializable (determinism, PC-05)",
            {"field": field_name, "reason": str(exc)},
        ) from exc
    return plain


def _freeze_str_tuple(value: Iterable[str] | None, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raise ProviderContractError(
            f"{field_name} must be a sequence of strings, not a string",
            {"field": field_name},
        )
    items = tuple(_require_text(item, field_name=f"{field_name}[]") for item in value)
    return items


class ProviderState(str, Enum):
    """Health states a provider may report.

    Deliberately coarse: the framework needs to know whether a provider may serve,
    may serve partially, or may not serve. Anything finer is provider detail carried
    in :attr:`ProviderHealth.checks`.
    """

    SERVING = "serving"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class ProviderIdentity:
    """The stable identity of a provider (PC-03).

    ``kind`` is an **open** slug supplied as data. The framework validates its form
    and never its membership, which is precisely why a provider class that does not
    exist yet needs no framework change (PC-02 / PC-14).
    """

    provider_id: str
    kind: str
    version: str
    name: str = ""
    authority: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider_id", normalize_provider_id(self.provider_id))
        object.__setattr__(self, "kind", normalize_kind(self.kind))
        object.__setattr__(self, "version", require_semver(self.version))
        object.__setattr__(self, "name", self.name or self.provider_id)
        if not isinstance(self.authority, str):
            raise ProviderContractError("authority must be a string")

    @property
    def qualified_id(self) -> str:
        """Return the version-pinned identity ``<provider_id>@<version>``."""
        return f"{self.provider_id}@{self.version}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "kind": self.kind,
            "version": self.version,
            "name": self.name,
            "authority": self.authority,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ProviderIdentity:
        if not isinstance(payload, Mapping):
            raise ProviderContractError("provider identity payload must be a mapping")
        return cls(
            provider_id=_require_text(payload.get("provider_id"), field_name="provider_id"),
            kind=_require_text(payload.get("kind"), field_name="kind"),
            version=_require_text(payload.get("version"), field_name="version"),
            name=str(payload.get("name") or ""),
            authority=str(payload.get("authority") or ""),
        )


@dataclass(frozen=True, slots=True)
class ProviderCapability:
    """One declared capability (PC-04).

    A capability is the provider's own authority surface. It binds a constitutional
    ``operation`` to a named contract, declares the selector keys it understands,
    the ``resource_kind`` it yields, whether it is ``deterministic`` (PC-05), and the
    external ``effects`` it requires (PC-08). Nothing undeclared may be invoked.
    """

    name: str
    operation: ProviderOperation
    resource_kind: str = ""
    description: str = ""
    selector_keys: tuple[str, ...] = ()
    required_selector_keys: tuple[str, ...] = ()
    deterministic: bool = True
    effects: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_text(self.name, field_name="capability name"))
        if not isinstance(self.operation, ProviderOperation):
            try:
                object.__setattr__(self, "operation", ProviderOperation(str(self.operation)))
            except ValueError as exc:
                raise ProviderContractError(
                    "capability operation must be a constitutional operation (PC-01)",
                    {"capability": self.name, "operation": repr(self.operation)},
                ) from exc
        object.__setattr__(
            self, "selector_keys", _freeze_str_tuple(self.selector_keys, field_name="selector_keys")
        )
        object.__setattr__(
            self,
            "required_selector_keys",
            _freeze_str_tuple(self.required_selector_keys, field_name="required_selector_keys"),
        )
        object.__setattr__(self, "effects", _freeze_str_tuple(self.effects, field_name="effects"))
        unknown_required = tuple(
            key for key in self.required_selector_keys if key not in self.selector_keys
        )
        if unknown_required:
            raise ProviderContractError(
                "required selector keys must also be declared as selector keys (PC-04)",
                {"capability": self.name, "undeclared": list(unknown_required)},
            )
        if not isinstance(self.deterministic, bool):
            raise ProviderContractError(
                "capability determinism must be declared as a boolean (PC-05)",
                {"capability": self.name},
            )

    def accepts(self, selector: Mapping[str, Any]) -> tuple[str, ...]:
        """Return the selector keys this capability did not declare.

        An empty tuple means the selector is fully within the declared surface.
        """
        return tuple(sorted(key for key in selector if key not in self.selector_keys))

    def missing_required(self, selector: Mapping[str, Any]) -> tuple[str, ...]:
        """Return declared-required selector keys absent from ``selector``."""
        return tuple(sorted(key for key in self.required_selector_keys if key not in selector))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "operation": self.operation.value,
            "resource_kind": self.resource_kind,
            "description": self.description,
            "selector_keys": list(self.selector_keys),
            "required_selector_keys": list(self.required_selector_keys),
            "deterministic": self.deterministic,
            "effects": list(self.effects),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ProviderCapability:
        if not isinstance(payload, Mapping):
            raise ProviderContractError("capability payload must be a mapping")
        return cls(
            name=_require_text(payload.get("name"), field_name="name"),
            operation=ProviderOperation(
                _require_text(payload.get("operation"), field_name="operation")
            ),
            resource_kind=str(payload.get("resource_kind") or ""),
            description=str(payload.get("description") or ""),
            selector_keys=_freeze_str_tuple(
                payload.get("selector_keys"), field_name="selector_keys"
            ),
            required_selector_keys=_freeze_str_tuple(
                payload.get("required_selector_keys"), field_name="required_selector_keys"
            ),
            deterministic=bool(payload.get("deterministic", True)),
            effects=_freeze_str_tuple(payload.get("effects"), field_name="effects"),
        )


@dataclass(frozen=True, slots=True)
class ProviderDependency:
    """A provider composed **by reference**, never by import (PC-12)."""

    provider_id: str
    min_version: str = "0.0.0"
    optional: bool = False
    alias: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider_id", normalize_provider_id(self.provider_id))
        object.__setattr__(
            self, "min_version", require_semver(self.min_version, field_name="min_version")
        )
        object.__setattr__(self, "alias", self.alias or self.provider_id)
        if not isinstance(self.optional, bool):
            raise ProviderContractError("dependency optionality must be a boolean")

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "min_version": self.min_version,
            "optional": self.optional,
            "alias": self.alias,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ProviderDependency:
        if not isinstance(payload, Mapping):
            raise ProviderContractError("dependency payload must be a mapping")
        return cls(
            provider_id=_require_text(payload.get("provider_id"), field_name="provider_id"),
            min_version=str(payload.get("min_version") or "0.0.0"),
            optional=bool(payload.get("optional", False)),
            alias=str(payload.get("alias") or ""),
        )


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    """The complete, content-addressed declaration of a provider (PC-03).

    A descriptor is the *only* thing the framework needs in order to register,
    discover, validate, certify, and compose a provider. It is pure data: it can be
    authored as JSON, shipped in a catalog, discovered from disk, and resolved to a
    live instance through :attr:`entry_point` — which is what makes provider
    onboarding a data act rather than a code act (PC-14).
    """

    identity: ProviderIdentity
    capabilities: tuple[ProviderCapability, ...] = ()
    dependencies: tuple[ProviderDependency, ...] = ()
    interface: str = PROVIDER_INTERFACE
    interface_version: str = PROVIDER_INTERFACE_VERSION
    entry_point: str = ""
    source_of_record: str = ""
    description: str = ""
    config_schema: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.identity, ProviderIdentity):
            raise ProviderContractError("descriptor identity must be a ProviderIdentity")
        if self.interface != PROVIDER_INTERFACE:
            raise ProviderContractError(
                "a provider may only declare the one constitutional interface (PC-01)",
                {"declared": self.interface, "constitutional": PROVIDER_INTERFACE},
            )
        object.__setattr__(
            self,
            "interface_version",
            require_semver(self.interface_version, field_name="interface_version"),
        )
        object.__setattr__(self, "capabilities", tuple(self.capabilities))
        object.__setattr__(self, "dependencies", tuple(self.dependencies))
        for capability in self.capabilities:
            if not isinstance(capability, ProviderCapability):
                raise ProviderContractError(
                    "every declared capability must be a ProviderCapability",
                    {"provider_id": self.identity.provider_id},
                )
        for dependency in self.dependencies:
            if not isinstance(dependency, ProviderDependency):
                raise ProviderContractError(
                    "every declared dependency must be a ProviderDependency",
                    {"provider_id": self.identity.provider_id},
                )
        names = [capability.name for capability in self.capabilities]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ProviderContractError(
                "capability names must be unique within a provider",
                {"provider_id": self.identity.provider_id, "duplicates": duplicates},
            )
        aliases = [dependency.alias for dependency in self.dependencies]
        duplicate_aliases = sorted({alias for alias in aliases if aliases.count(alias) > 1})
        if duplicate_aliases:
            raise ProviderContractError(
                "dependency aliases must be unique within a provider",
                {"provider_id": self.identity.provider_id, "duplicates": duplicate_aliases},
            )
        if self.identity.provider_id in {d.provider_id for d in self.dependencies}:
            raise ProviderContractError(
                "a provider may not depend on itself (PC-12 acyclicity)",
                {"provider_id": self.identity.provider_id},
            )
        object.__setattr__(
            self, "config_schema", _freeze_mapping(self.config_schema, field_name="config_schema")
        )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata, field_name="metadata"))

    @property
    def provider_id(self) -> str:
        return self.identity.provider_id

    @property
    def kind(self) -> str:
        return self.identity.kind

    @property
    def version(self) -> str:
        return self.identity.version

    @property
    def qualified_id(self) -> str:
        return self.identity.qualified_id

    def capability(self, name: str) -> ProviderCapability:
        """Return the declared capability ``name`` or refuse (PC-04 / PC-07)."""
        for candidate in self.capabilities:
            if candidate.name == name:
                return candidate
        raise ProviderCapabilityError(
            f"capability {name!r} is not declared by provider {self.provider_id!r}",
            {
                "provider_id": self.provider_id,
                "capability": name,
                "declared": [c.name for c in self.capabilities],
            },
        )

    def capabilities_for(self, operation: ProviderOperation) -> tuple[ProviderCapability, ...]:
        """Return declared capabilities bound to ``operation``, in declared order."""
        return tuple(c for c in self.capabilities if c.operation is operation)

    def declared_effects(self) -> tuple[str, ...]:
        """Return the union of all declared external effects (PC-08), sorted."""
        return tuple(sorted({effect for c in self.capabilities for effect in c.effects}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "interface": self.interface,
            "interface_version": self.interface_version,
            "entry_point": self.entry_point,
            "source_of_record": self.source_of_record,
            "description": self.description,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "config_schema": dict(self.config_schema),
            "metadata": dict(self.metadata),
        }

    def content_hash(self) -> str:
        """Return the content hash pinning exactly this declaration."""
        return content_hash(self.to_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ProviderDescriptor:
        """Build a descriptor from a plain mapping (the JSON catalog path)."""
        if not isinstance(payload, Mapping):
            raise ProviderContractError("provider descriptor payload must be a mapping")
        identity_payload = payload.get("identity")
        if isinstance(identity_payload, Mapping):
            identity = ProviderIdentity.from_dict(identity_payload)
        else:
            identity = ProviderIdentity.from_dict(payload)
        raw_capabilities = payload.get("capabilities") or ()
        if isinstance(raw_capabilities, Mapping) or isinstance(raw_capabilities, str):
            raise ProviderContractError("capabilities must be a sequence of mappings")
        raw_dependencies = payload.get("dependencies") or ()
        if isinstance(raw_dependencies, Mapping) or isinstance(raw_dependencies, str):
            raise ProviderContractError("dependencies must be a sequence of mappings")
        return cls(
            identity=identity,
            capabilities=tuple(ProviderCapability.from_dict(c) for c in raw_capabilities),
            dependencies=tuple(ProviderDependency.from_dict(d) for d in raw_dependencies),
            interface=str(payload.get("interface") or PROVIDER_INTERFACE),
            interface_version=str(payload.get("interface_version") or PROVIDER_INTERFACE_VERSION),
            entry_point=str(payload.get("entry_point") or ""),
            source_of_record=str(payload.get("source_of_record") or ""),
            description=str(payload.get("description") or ""),
            config_schema=dict(payload.get("config_schema") or {}),
            metadata=dict(payload.get("metadata") or {}),
        )


@dataclass(frozen=True, slots=True)
class ProviderQuery:
    """The universal read-many request (PC-01).

    A ``capability`` name plus an opaque ``selector``. The framework validates the
    selector against the capability's *declared* keys and refuses anything
    undeclared (PC-04) — it never interprets selector semantics, which belong
    entirely to the provider.
    """

    capability: str
    selector: dict[str, Any] = field(default_factory=dict)
    limit: int = DEFAULT_QUERY_LIMIT
    cursor: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "capability", _require_text(self.capability, field_name="query capability")
        )
        object.__setattr__(self, "selector", _freeze_mapping(self.selector, field_name="selector"))
        if not isinstance(self.limit, int) or isinstance(self.limit, bool) or self.limit < 1:
            raise ProviderContractError(
                "query limit must be a positive integer", {"limit": repr(self.limit)}
            )
        if self.limit > MAX_QUERY_LIMIT:
            raise ProviderContractError(
                "query limit exceeds the framework ceiling",
                {"limit": self.limit, "max": MAX_QUERY_LIMIT},
            )
        if not isinstance(self.cursor, str):
            raise ProviderContractError("query cursor must be a string")

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "selector": dict(self.selector),
            "limit": self.limit,
            "cursor": self.cursor,
        }

    def fingerprint(self) -> str:
        """Return the content hash of this query (the determinism key, PC-05)."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ProviderResource:
    """One unit a provider returns, carrying mandatory provenance (PC-06).

    ``payload`` is provider-shaped and framework-opaque. ``provenance`` names the
    source of record the unit was drawn from. ``resource_hash`` is computed over the
    canonical payload, so a consumer can prove the unit was not altered in transit
    and an evidence bundle can reference it by hash.
    """

    resource_id: str
    kind: str
    provider_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "resource_id", _require_text(self.resource_id, field_name="resource_id")
        )
        object.__setattr__(self, "kind", normalize_kind(self.kind))
        object.__setattr__(self, "provider_id", normalize_provider_id(self.provider_id))
        object.__setattr__(self, "payload", _freeze_mapping(self.payload, field_name="payload"))
        provenance = _freeze_mapping(self.provenance, field_name="provenance")
        if (
            "source_of_record" not in provenance
            or not str(provenance.get("source_of_record") or "").strip()
        ):
            raise ProviderContractError(
                "every resource must declare provenance.source_of_record (PC-06)",
                {"resource_id": self.resource_id, "provider_id": self.provider_id},
            )
        object.__setattr__(self, "provenance", provenance)

    @property
    def resource_hash(self) -> str:
        """Return the content hash over kind + payload."""
        return content_hash({"kind": self.kind, "payload": dict(self.payload)})

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "kind": self.kind,
            "provider_id": self.provider_id,
            "payload": dict(self.payload),
            "provenance": dict(self.provenance),
            "resource_hash": self.resource_hash,
        }


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    """The universal read-many result.

    Content-addressed over the query plus the returned resources, so an identical
    query over an identical substrate produces an identical ``response_hash`` — the
    executable form of PC-05.
    """

    provider_id: str
    capability: str
    query_fingerprint: str
    resources: tuple[ProviderResource, ...] = ()
    truncated: bool = False
    next_cursor: str = ""
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider_id", normalize_provider_id(self.provider_id))
        object.__setattr__(
            self, "capability", _require_text(self.capability, field_name="capability")
        )
        object.__setattr__(self, "resources", tuple(self.resources))
        for resource in self.resources:
            if not isinstance(resource, ProviderResource):
                raise ProviderContractError(
                    "every response resource must be a ProviderResource",
                    {"provider_id": self.provider_id, "capability": self.capability},
                )
        object.__setattr__(
            self, "diagnostics", _freeze_mapping(self.diagnostics, field_name="diagnostics")
        )
        if not isinstance(self.truncated, bool):
            raise ProviderContractError("truncated must be a boolean")

    def __len__(self) -> int:
        return len(self.resources)

    def resource_ids(self) -> tuple[str, ...]:
        return tuple(resource.resource_id for resource in self.resources)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "capability": self.capability,
            "query_fingerprint": self.query_fingerprint,
            "resources": [resource.to_dict() for resource in self.resources],
            "truncated": self.truncated,
            "next_cursor": self.next_cursor,
            "diagnostics": dict(self.diagnostics),
        }

    @property
    def response_hash(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    """Structural serviceability of a provider (PC-09).

    Health is reportable without invoking a domain operation, which is what lets the
    framework isolate a faulty provider instead of discovering the fault through a
    consumer.
    """

    provider_id: str
    state: ProviderState
    checks: dict[str, bool] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider_id", normalize_provider_id(self.provider_id))
        if not isinstance(self.state, ProviderState):
            try:
                object.__setattr__(self, "state", ProviderState(str(self.state)))
            except ValueError as exc:
                raise ProviderContractError(
                    "health state must be a ProviderState", {"state": repr(self.state)}
                ) from exc
        checks = _freeze_mapping(self.checks, field_name="checks")
        for key, value in checks.items():
            if not isinstance(value, bool):
                raise ProviderContractError(
                    "each health check must be a boolean", {"check": key, "value": repr(value)}
                )
        object.__setattr__(self, "checks", checks)
        object.__setattr__(self, "reasons", _freeze_str_tuple(self.reasons, field_name="reasons"))
        if self.state is ProviderState.SERVING and self.reasons:
            raise ProviderContractError(
                "a serving provider may not report degradation reasons",
                {"provider_id": self.provider_id, "reasons": list(self.reasons)},
            )

    @property
    def serving(self) -> bool:
        return self.state is ProviderState.SERVING

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "state": self.state.value,
            "checks": dict(self.checks),
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class ProviderAttestation:
    """Integrity + provenance attestation over one resource (PC-06).

    Asymmetric on purpose. A **verified** attestation must carry both a content hash
    and a non-empty provenance chain — that is what makes it evidence. An
    **unverified** attestation may carry no hash at all (an unresolvable resource has
    none) but must state a reason, so "not attested" is never silently
    indistinguishable from "attested" (PC-07).
    """

    provider_id: str
    resource_id: str
    resource_hash: str
    verified: bool
    provenance_chain: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider_id", normalize_provider_id(self.provider_id))
        object.__setattr__(
            self, "resource_id", _require_text(self.resource_id, field_name="resource_id")
        )
        if not isinstance(self.verified, bool):
            raise ProviderContractError("attestation verdict must be a boolean")
        if self.verified:
            object.__setattr__(
                self, "resource_hash", _require_text(self.resource_hash, field_name="resource_hash")
            )
        elif not isinstance(self.resource_hash, str):
            raise ProviderContractError(
                "attestation resource hash must be a string",
                {"resource_hash": repr(self.resource_hash)},
            )
        object.__setattr__(
            self,
            "provenance_chain",
            _freeze_str_tuple(self.provenance_chain, field_name="provenance_chain"),
        )
        object.__setattr__(self, "reasons", _freeze_str_tuple(self.reasons, field_name="reasons"))
        if self.verified and not self.provenance_chain:
            raise ProviderContractError(
                "a verified attestation requires a non-empty provenance chain (PC-06)",
                {"provider_id": self.provider_id, "resource_id": self.resource_id},
            )
        if not self.verified and not self.reasons:
            raise ProviderContractError(
                "an unverified attestation must state why (PC-07)",
                {"provider_id": self.provider_id, "resource_id": self.resource_id},
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "resource_id": self.resource_id,
            "resource_hash": self.resource_hash,
            "verified": self.verified,
            "provenance_chain": list(self.provenance_chain),
            "reasons": list(self.reasons),
        }


@runtime_checkable
class Provider(Protocol):
    """The one constitutional provider interface — six operations, no more (PC-01).

    A repository, a patent office, a journal index, a standards body, a government
    data source, an AI model host, a marketplace, a ledger, and a provider class
    nobody has thought of yet all satisfy exactly this protocol. Consumers bind
    here; they never bind to a provider.
    """

    def describe(self) -> ProviderDescriptor:  # pragma: no cover - protocol
        """Return this provider's own content-addressed declaration."""
        ...

    def capabilities(self) -> Sequence[ProviderCapability]:  # pragma: no cover - protocol
        """Return the declared capability set (the provider's authority surface)."""
        ...

    def health(self) -> ProviderHealth:  # pragma: no cover - protocol
        """Return structural serviceability without invoking a domain operation."""
        ...

    def query(self, request: ProviderQuery) -> ProviderResponse:  # pragma: no cover - protocol
        """Return zero or more resources matching ``request`` (read-many)."""
        ...

    def fetch(self, resource_id: str) -> ProviderResource:  # pragma: no cover - protocol
        """Return exactly one resource, or fail closed (read-one)."""
        ...

    def verify(self, resource_id: str) -> ProviderAttestation:  # pragma: no cover - protocol
        """Return an integrity + provenance attestation over ``resource_id``."""
        ...


def provider_operations(candidate: object) -> tuple[str, ...]:
    """Return the constitutional operations ``candidate`` implements, sorted.

    Used by validation gate ``PV-01-INTERFACE-COMPLETE`` to prove interface
    completeness structurally rather than by trusting a declaration.
    """
    return tuple(
        sorted(op.value for op in ProviderOperation if callable(getattr(candidate, op.value, None)))
    )


__all__ = [
    "DEFAULT_QUERY_LIMIT",
    "MAX_QUERY_LIMIT",
    "PROVIDER_CONTRACT_VERSION",
    "Provider",
    "ProviderAttestation",
    "ProviderCapability",
    "ProviderDependency",
    "ProviderDescriptor",
    "ProviderHealth",
    "ProviderIdentity",
    "ProviderQuery",
    "ProviderResource",
    "ProviderResponse",
    "ProviderState",
    "canonical_json",
    "content_hash",
    "provider_operations",
]
