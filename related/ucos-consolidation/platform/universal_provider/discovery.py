"""UPA-000006 — Provider Discovery (Terminal-04).

Discovery answers "which providers exist?" **without the framework knowing any
provider**. There is no import of any provider module here, no list of provider
names, and no branch on provider kind. Providers are found because they were
*declared* — as a JSON manifest on disk, as an in-process descriptor, or as an
existing registration — and each declaration names its own :attr:`entry_point`, which
discovery resolves dynamically only when a live instance is actually required.

    * :class:`DiscoverySource` — the discovery source protocol.
    * :class:`CatalogSource` — a directory of JSON provider manifests.
    * :class:`DeclarationSource` — in-process descriptors.
    * :class:`RegistrySource` — providers already registered.
    * :class:`DiscoveredProvider` — one discovered declaration plus its origin.
    * :class:`DiscoveryResult` — the deterministic, content-addressed outcome.
    * :class:`ProviderDiscovery` — aggregates sources, deduplicates, orders.
    * :func:`resolve_entry_point` — descriptor → live provider, by declaration only.

This module is the mechanical proof of PC-14: onboarding a provider is dropping a
manifest and pointing it at an entry point. No framework file changes.
"""

from __future__ import annotations

import importlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from platform.universal_provider.constitution import version_tuple
from platform.universal_provider.contracts import (
    ProviderDescriptor,
    content_hash,
)
from platform.universal_provider.errors import (
    ProviderDiscoveryError,
    ProviderFrameworkError,
)
from platform.universal_provider.registry import ProviderRegistry
from typing import Any, Protocol, runtime_checkable

#: Semantic version of the Provider Discovery contract surface.
PROVIDER_DISCOVERY_VERSION = "1.0.0"

#: Manifest key holding a list of descriptors, when a file declares several.
MANIFEST_PROVIDERS_KEY = "providers"

#: Glob applied to a catalog directory. Manifests are plain JSON — no code executes
#: during discovery, which is what keeps discovery safe over untrusted catalogs.
MANIFEST_GLOB = "*.json"


@dataclass(frozen=True, slots=True)
class DiscoveredProvider:
    """One discovered provider declaration together with its origin."""

    descriptor: ProviderDescriptor
    source: str
    origin: str = ""

    @property
    def provider_id(self) -> str:
        return self.descriptor.provider_id

    @property
    def qualified_id(self) -> str:
        return self.descriptor.qualified_id

    @property
    def resolvable(self) -> bool:
        """Whether this declaration names an entry point it could be instantiated from."""
        return bool(self.descriptor.entry_point)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "origin": self.origin,
            "resolvable": self.resolvable,
            "descriptor_hash": self.descriptor.content_hash(),
            "descriptor": self.descriptor.to_dict(),
        }


@runtime_checkable
class DiscoverySource(Protocol):
    """A place providers may be declared.

    Any object with a ``name`` and a ``discover()`` returning
    :class:`DiscoveredProvider` values is a discovery source. Adding a new kind of
    source — a database, a federated peer, a package index — requires no change to
    :class:`ProviderDiscovery`.
    """

    @property
    def name(self) -> str:  # pragma: no cover - protocol
        """Return the stable source name recorded on every discovery."""
        ...

    def discover(self) -> Iterable[DiscoveredProvider]:  # pragma: no cover - protocol
        """Yield every provider declaration this source holds."""
        ...


class DeclarationSource:
    """In-process descriptors, declared directly in code or in a test."""

    def __init__(
        self, descriptors: Sequence[ProviderDescriptor], name: str = "declaration"
    ) -> None:
        self._descriptors = tuple(descriptors)
        self._name = name
        for descriptor in self._descriptors:
            if not isinstance(descriptor, ProviderDescriptor):
                raise ProviderDiscoveryError(
                    "a declaration source holds ProviderDescriptor values only",
                    {"source": name, "received": type(descriptor).__name__},
                )

    @property
    def name(self) -> str:
        return self._name

    def discover(self) -> tuple[DiscoveredProvider, ...]:
        return tuple(
            DiscoveredProvider(descriptor=descriptor, source=self._name, origin="in-process")
            for descriptor in self._descriptors
        )


class RegistrySource:
    """Providers already present in a :class:`ProviderRegistry`."""

    def __init__(self, registry: ProviderRegistry, name: str = "registry") -> None:
        self._registry = registry
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def discover(self) -> tuple[DiscoveredProvider, ...]:
        return tuple(
            DiscoveredProvider(
                descriptor=record.descriptor,
                source=self._name,
                origin=f"registration:{record.registration_id[:16]}",
            )
            for record in self._registry.registrations()
        )


class CatalogSource:
    """A directory of JSON provider manifests — the data path to onboarding (PC-14).

    Each ``*.json`` file may declare a single descriptor object, or several under the
    ``providers`` key. Files are read in sorted filename order and descriptors within
    a file in declared order, so discovery over an identical directory is
    byte-reproducible. Nothing in the manifest is executed.
    """

    def __init__(self, directory: Path | str, name: str = "catalog") -> None:
        self._directory = Path(directory)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def directory(self) -> Path:
        return self._directory

    def discover(self) -> tuple[DiscoveredProvider, ...]:
        if not self._directory.exists():
            raise ProviderDiscoveryError(
                "provider catalog directory does not exist (fail closed, PC-07)",
                {"source": self._name, "directory": str(self._directory)},
            )
        if not self._directory.is_dir():
            raise ProviderDiscoveryError(
                "provider catalog path is not a directory",
                {"source": self._name, "directory": str(self._directory)},
            )
        discovered: list[DiscoveredProvider] = []
        for path in sorted(self._directory.glob(MANIFEST_GLOB)):
            for payload in self._read_manifest(path):
                try:
                    descriptor = ProviderDescriptor.from_dict(payload)
                except ProviderFrameworkError as exc:
                    raise ProviderDiscoveryError(
                        "provider manifest declares a malformed descriptor",
                        {
                            "source": self._name,
                            "manifest": path.name,
                            "reason": exc.message,
                            "detail": exc.detail,
                        },
                    ) from exc
                discovered.append(
                    DiscoveredProvider(descriptor=descriptor, source=self._name, origin=path.name)
                )
        return tuple(discovered)

    def _read_manifest(self, path: Path) -> tuple[Mapping[str, Any], ...]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProviderDiscoveryError(
                "provider manifest is unreadable or is not valid JSON",
                {"source": self._name, "manifest": path.name, "reason": str(exc)},
            ) from exc
        if isinstance(raw, Mapping) and MANIFEST_PROVIDERS_KEY in raw:
            entries = raw[MANIFEST_PROVIDERS_KEY]
            if not isinstance(entries, list):
                raise ProviderDiscoveryError(
                    f"manifest {MANIFEST_PROVIDERS_KEY!r} must be a list",
                    {"source": self._name, "manifest": path.name},
                )
            payloads = entries
        elif isinstance(raw, Mapping):
            payloads = [raw]
        elif isinstance(raw, list):
            payloads = raw
        else:
            raise ProviderDiscoveryError(
                "provider manifest must be an object or a list of objects",
                {"source": self._name, "manifest": path.name},
            )
        for entry in payloads:
            if not isinstance(entry, Mapping):
                raise ProviderDiscoveryError(
                    "every provider manifest entry must be an object",
                    {"source": self._name, "manifest": path.name},
                )
        return tuple(payloads)


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    """The deterministic, content-addressed outcome of a discovery pass."""

    discovered: tuple[DiscoveredProvider, ...] = ()
    sources: tuple[str, ...] = ()
    conflicts: tuple[dict[str, Any], ...] = ()
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.discovered)

    def descriptors(self) -> tuple[ProviderDescriptor, ...]:
        return tuple(item.descriptor for item in self.discovered)

    def provider_ids(self) -> tuple[str, ...]:
        return tuple(sorted({item.provider_id for item in self.discovered}))

    def kinds(self) -> tuple[str, ...]:
        """Return the kinds discovered — **derived from the data** (PC-02)."""
        return tuple(sorted({item.descriptor.kind for item in self.discovered}))

    def resolvable(self) -> tuple[DiscoveredProvider, ...]:
        """Return declarations that name an entry point and can be instantiated."""
        return tuple(item for item in self.discovered if item.resolvable)

    def declared_only(self) -> tuple[DiscoveredProvider, ...]:
        """Return declarations with no entry point yet — declared, not yet realizable.

        A declared-only provider is a legitimate, useful state: it is registered,
        discoverable, and inventoried, and it simply cannot be activated until an
        implementation is pointed at it. This is how a catalog carries a roadmap
        without the framework hardcoding one.
        """
        return tuple(item for item in self.discovered if not item.resolvable)

    def to_dict(self) -> dict[str, Any]:
        return {
            "discovery_version": PROVIDER_DISCOVERY_VERSION,
            "sources": list(self.sources),
            "count": len(self.discovered),
            "kinds": list(self.kinds()),
            "resolvable": len(self.resolvable()),
            "declared_only": len(self.declared_only()),
            "conflicts": [dict(conflict) for conflict in self.conflicts],
            "discovered": [item.to_dict() for item in self.discovered],
            "diagnostics": dict(self.diagnostics),
        }

    def discovery_hash(self) -> str:
        return content_hash(self.to_dict())


class ProviderDiscovery:
    """Aggregates discovery sources into one deterministic result.

    Precedence is source order: the first source to declare a given
    ``provider_id@version`` wins, and any later differing declaration of the same
    qualified id is recorded as a **conflict** rather than silently overwriting.
    Discovery reports; it never adjudicates.
    """

    def __init__(self, sources: Sequence[DiscoverySource] = ()) -> None:
        self._sources: list[DiscoverySource] = []
        for source in sources:
            self.add_source(source)

    def add_source(self, source: DiscoverySource) -> ProviderDiscovery:
        """Register a discovery source. Returns ``self`` for chaining."""
        if not hasattr(source, "discover") or not callable(source.discover):
            raise ProviderDiscoveryError(
                "a discovery source must implement discover()",
                {"received": type(source).__name__},
            )
        if not isinstance(getattr(source, "name", None), str) or not source.name:
            raise ProviderDiscoveryError(
                "a discovery source must expose a non-empty name",
                {"received": type(source).__name__},
            )
        self._sources.append(source)
        return self

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(source.name for source in self._sources)

    def discover(self) -> DiscoveryResult:
        """Run every source in order and return the aggregated result."""
        accepted: dict[str, DiscoveredProvider] = {}
        conflicts: list[dict[str, Any]] = []
        per_source: dict[str, Any] = {}
        for source in self._sources:
            found = tuple(source.discover())
            per_source[source.name] = len(found)
            for item in found:
                if not isinstance(item, DiscoveredProvider):
                    raise ProviderDiscoveryError(
                        "a discovery source must yield DiscoveredProvider values",
                        {"source": source.name, "received": type(item).__name__},
                    )
                key = item.qualified_id
                incumbent = accepted.get(key)
                if incumbent is None:
                    accepted[key] = item
                    continue
                if incumbent.descriptor.content_hash() != item.descriptor.content_hash():
                    conflicts.append(
                        {
                            "qualified_id": key,
                            "accepted_source": incumbent.source,
                            "accepted_origin": incumbent.origin,
                            "accepted_hash": incumbent.descriptor.content_hash(),
                            "rejected_source": item.source,
                            "rejected_origin": item.origin,
                            "rejected_hash": item.descriptor.content_hash(),
                        }
                    )
        ordered = tuple(
            sorted(
                accepted.values(),
                key=lambda item: (
                    item.descriptor.provider_id,
                    version_tuple(item.descriptor.version),
                ),
            )
        )
        return DiscoveryResult(
            discovered=ordered,
            sources=self.sources,
            conflicts=tuple(sorted(conflicts, key=lambda conflict: str(conflict["qualified_id"]))),
            diagnostics={"per_source": per_source},
        )


def resolve_entry_point(
    descriptor: ProviderDescriptor, config: Mapping[str, Any] | None = None
) -> Any:
    """Instantiate the provider a descriptor **declares**, and nothing else.

    ``entry_point`` is ``"package.module:attribute"``. The attribute may be a
    provider class or a factory; either way it is called with the descriptor and the
    resolved configuration. This one function is the whole bridge from data to a live
    provider, which is why no framework module ever needs to know a provider's name
    (PC-02 / PC-14).

    Fails closed (PC-07) on an absent, malformed, unimportable, or non-callable entry
    point, and isolates any construction fault as a typed error (PC-09).
    """
    if not descriptor.entry_point:
        raise ProviderDiscoveryError(
            "descriptor declares no entry point and cannot be instantiated (PC-07)",
            {"provider_id": descriptor.provider_id, "qualified_id": descriptor.qualified_id},
        )
    target = descriptor.entry_point
    if target.count(":") != 1:
        raise ProviderDiscoveryError(
            "entry point must be 'module:attribute'",
            {"provider_id": descriptor.provider_id, "entry_point": target},
        )
    module_name, attribute = (part.strip() for part in target.split(":"))
    if not module_name or not attribute:
        raise ProviderDiscoveryError(
            "entry point must name both a module and an attribute",
            {"provider_id": descriptor.provider_id, "entry_point": target},
        )
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ProviderDiscoveryError(
            "provider entry point module could not be imported",
            {
                "provider_id": descriptor.provider_id,
                "entry_point": target,
                "reason": str(exc),
            },
        ) from exc
    factory = getattr(module, attribute, None)
    if factory is None:
        raise ProviderDiscoveryError(
            "provider entry point attribute is absent from its module",
            {"provider_id": descriptor.provider_id, "entry_point": target},
        )
    if not callable(factory):
        raise ProviderDiscoveryError(
            "provider entry point attribute is not callable",
            {"provider_id": descriptor.provider_id, "entry_point": target},
        )
    try:
        return factory(descriptor, dict(config or {}))
    except ProviderFrameworkError:
        raise
    except Exception as exc:  # noqa: BLE001 - PC-09 fault isolation
        raise ProviderDiscoveryError(
            "provider entry point raised during construction",
            {
                "provider_id": descriptor.provider_id,
                "entry_point": target,
                "cause": f"{type(exc).__name__}: {exc}",
            },
        ) from exc


__all__ = [
    "MANIFEST_GLOB",
    "MANIFEST_PROVIDERS_KEY",
    "PROVIDER_DISCOVERY_VERSION",
    "CatalogSource",
    "DeclarationSource",
    "DiscoveredProvider",
    "DiscoveryResult",
    "DiscoverySource",
    "ProviderDiscovery",
    "RegistrySource",
    "resolve_entry_point",
]
