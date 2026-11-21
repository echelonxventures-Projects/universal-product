"""UPA-000005 — Provider Registry (Terminal-04).

The single registration authority for providers. The registry is **append-only,
content-addressed, deterministic, and provider-agnostic**: it stores descriptors as
data and resolves them by identity and version. It never enumerates, branches on, or
special-cases a provider kind (PC-02), so the set of registrable provider classes is
unbounded (PC-14).

    * :class:`ProviderRegistration` — the immutable record of one registration.
    * :class:`ProviderRegistry` — registration, resolution, and dependency ordering.

Three constitutional properties are enforced here rather than documented:

    * **Append-only.** A registered ``id@version`` is never mutated or replaced. A
      change is a new version (PC-13).
    * **Additive evolution.** A new version within an existing major line must be a
      capability superset of the highest prior version in that line. Removing or
      renaming a capability inside a major version is refused (PC-13).
    * **Acyclic composition.** Dependency resolution returns a dependency-first
      topological order and refuses cycles (PC-12).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.universal_provider.constitution import (
    normalize_kind,
    normalize_provider_id,
    require_semver,
    version_tuple,
)
from platform.universal_provider.contracts import (
    ProviderDescriptor,
    content_hash,
)
from platform.universal_provider.errors import ProviderRegistryError
from typing import Any

#: Semantic version of the Provider Registry contract surface.
PROVIDER_REGISTRY_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class ProviderRegistration:
    """The immutable, content-addressed record of one provider registration."""

    sequence: int
    descriptor: ProviderDescriptor
    descriptor_hash: str
    registration_id: str

    @property
    def provider_id(self) -> str:
        return self.descriptor.provider_id

    @property
    def kind(self) -> str:
        return self.descriptor.kind

    @property
    def version(self) -> str:
        return self.descriptor.version

    @property
    def qualified_id(self) -> str:
        return self.descriptor.qualified_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "registration_id": self.registration_id,
            "descriptor_hash": self.descriptor_hash,
            "descriptor": self.descriptor.to_dict(),
        }


class ProviderRegistry:
    """The append-only registration authority for providers.

    Holds descriptors only — never provider instances, never wall-clock, never
    lifecycle state (lifecycle is governed exclusively by
    :mod:`platform.universal_provider.lifecycle`, PC-10). Two registries fed the same
    descriptors in the same order are byte-identical.
    """

    def __init__(self) -> None:
        self._records: dict[str, ProviderRegistration] = {}
        self._sequence = 0

    # ----------------------------------------------------------------- registration

    def register(self, descriptor: ProviderDescriptor) -> ProviderRegistration:
        """Register ``descriptor`` and return its immutable record.

        Refuses duplicate ``id@version`` (append-only), a non-monotonic version
        within an existing major line, and any non-additive change within a major
        line (PC-13).
        """
        if not isinstance(descriptor, ProviderDescriptor):
            raise ProviderRegistryError(
                "only a ProviderDescriptor may be registered",
                {"received": type(descriptor).__name__},
            )
        key = descriptor.qualified_id
        existing = self._records.get(key)
        if existing is not None:
            raise ProviderRegistryError(
                "provider version is already registered; registration is append-only (PC-13)",
                {
                    "qualified_id": key,
                    "registered_hash": existing.descriptor_hash,
                    "offered_hash": descriptor.content_hash(),
                },
            )
        self._require_additive(descriptor)
        self._sequence += 1
        descriptor_hash = descriptor.content_hash()
        record = ProviderRegistration(
            sequence=self._sequence,
            descriptor=descriptor,
            descriptor_hash=descriptor_hash,
            registration_id=content_hash({"qualified_id": key, "descriptor_hash": descriptor_hash}),
        )
        self._records[key] = record
        return record

    def register_all(
        self, descriptors: Iterable[ProviderDescriptor]
    ) -> tuple[ProviderRegistration, ...]:
        """Register every descriptor, in the order supplied."""
        return tuple(self.register(descriptor) for descriptor in descriptors)

    def _require_additive(self, descriptor: ProviderDescriptor) -> None:
        """Enforce monotonic, additive evolution within a major line (PC-13)."""
        major = version_tuple(descriptor.version)[0]
        same_line = [
            record
            for record in self._records.values()
            if record.provider_id == descriptor.provider_id
            and version_tuple(record.version)[0] == major
        ]
        if not same_line:
            return
        highest = max(same_line, key=lambda record: version_tuple(record.version))
        if version_tuple(descriptor.version) < version_tuple(highest.version):
            raise ProviderRegistryError(
                "a version older than the registered head of its major line is refused (PC-13)",
                {
                    "provider_id": descriptor.provider_id,
                    "offered": descriptor.version,
                    "registered_head": highest.version,
                },
            )
        if descriptor.kind != highest.kind:
            raise ProviderRegistryError(
                "a provider may not change kind within a major version line (PC-13)",
                {
                    "provider_id": descriptor.provider_id,
                    "registered_kind": highest.kind,
                    "offered_kind": descriptor.kind,
                },
            )
        prior = {capability.name for capability in highest.descriptor.capabilities}
        offered = {capability.name for capability in descriptor.capabilities}
        removed = sorted(prior - offered)
        if removed:
            raise ProviderRegistryError(
                "capabilities may not be removed within a major version line (PC-13)",
                {
                    "provider_id": descriptor.provider_id,
                    "from_version": highest.version,
                    "to_version": descriptor.version,
                    "removed": removed,
                },
            )

    # -------------------------------------------------------------------- resolution

    def resolve(self, provider_id: str, min_version: str = "0.0.0") -> ProviderRegistration:
        """Return the highest registered version of ``provider_id`` at or above ``min_version``.

        Fails closed when nothing satisfies the constraint (PC-07).
        """
        normalized = normalize_provider_id(provider_id)
        floor = version_tuple(require_semver(min_version, field_name="min_version"))
        candidates = [
            record
            for record in self._records.values()
            if record.provider_id == normalized and version_tuple(record.version) >= floor
        ]
        if not candidates:
            raise ProviderRegistryError(
                "no registered provider satisfies the requested version constraint",
                {
                    "provider_id": normalized,
                    "min_version": min_version,
                    "registered": self.versions(normalized),
                },
            )
        return max(candidates, key=lambda record: version_tuple(record.version))

    def get(self, provider_id: str, version: str) -> ProviderRegistration:
        """Return the exact registration ``provider_id@version`` or fail closed."""
        key = f"{normalize_provider_id(provider_id)}@{require_semver(version)}"
        record = self._records.get(key)
        if record is None:
            raise ProviderRegistryError("provider version is not registered", {"qualified_id": key})
        return record

    def versions(self, provider_id: str) -> tuple[str, ...]:
        """Return every registered version of ``provider_id``, ascending."""
        normalized = normalize_provider_id(provider_id)
        return tuple(
            sorted(
                (
                    record.version
                    for record in self._records.values()
                    if record.provider_id == normalized
                ),
                key=version_tuple,
            )
        )

    def __contains__(self, provider_id: object) -> bool:
        if not isinstance(provider_id, str):
            return False
        try:
            normalized = normalize_provider_id(provider_id)
        except Exception:  # noqa: BLE001 - membership never raises
            return False
        return any(record.provider_id == normalized for record in self._records.values())

    def __len__(self) -> int:
        return len(self._records)

    # ------------------------------------------------------------------ enumeration

    def registrations(self, *, kind: str | None = None) -> tuple[ProviderRegistration, ...]:
        """Return registrations in deterministic order, optionally filtered by kind.

        ``kind`` is matched as **data**. The registry has no opinion about which kinds
        exist (PC-02).
        """
        records = tuple(
            sorted(
                self._records.values(),
                key=lambda record: (record.provider_id, version_tuple(record.version)),
            )
        )
        if kind is None:
            return records
        wanted = normalize_kind(kind)
        return tuple(record for record in records if record.kind == wanted)

    def heads(self) -> tuple[ProviderRegistration, ...]:
        """Return the highest registered version of each provider, id-ordered."""
        by_id: dict[str, ProviderRegistration] = {}
        for record in self._records.values():
            current = by_id.get(record.provider_id)
            if current is None or version_tuple(record.version) > version_tuple(current.version):
                by_id[record.provider_id] = record
        return tuple(by_id[provider_id] for provider_id in sorted(by_id))

    def kinds(self) -> tuple[str, ...]:
        """Return the kinds present in the registry, **derived from data** (PC-02)."""
        return tuple(sorted({record.kind for record in self._records.values()}))

    def provider_ids(self) -> tuple[str, ...]:
        return tuple(sorted({record.provider_id for record in self._records.values()}))

    # ------------------------------------------------------------------- composition

    def resolution_order(self, provider_id: str) -> tuple[ProviderRegistration, ...]:
        """Return ``provider_id`` and its transitive dependencies, dependency-first.

        Refuses dependency cycles and unresolvable required dependencies (PC-12).
        Optional dependencies that are absent are skipped rather than fatal, so a
        partially populated registry degrades scope rather than failing wholesale
        (PC-09).
        """
        order: list[ProviderRegistration] = []
        visited: set[str] = set()
        visiting: list[str] = []

        def walk(target_id: str, min_version: str) -> None:
            record = self.resolve(target_id, min_version)
            key = record.qualified_id
            if key in visited:
                return
            if record.provider_id in visiting:
                raise ProviderRegistryError(
                    "provider dependency graph contains a cycle (PC-12)",
                    {"cycle": [*visiting, record.provider_id]},
                )
            visiting.append(record.provider_id)
            for dependency in record.descriptor.dependencies:
                try:
                    walk(dependency.provider_id, dependency.min_version)
                except ProviderRegistryError as exc:
                    if dependency.optional and exc.detail.get("provider_id"):
                        continue
                    raise
            visiting.pop()
            visited.add(key)
            order.append(record)

        walk(normalize_provider_id(provider_id), "0.0.0")
        return tuple(order)

    # ---------------------------------------------------------------------- evidence

    def to_dict(self) -> dict[str, Any]:
        """Return the deterministic projection of the whole registry."""
        return {
            "registry_version": PROVIDER_REGISTRY_VERSION,
            "count": len(self._records),
            "kinds": list(self.kinds()),
            "registrations": [record.to_dict() for record in self.registrations()],
        }

    def registry_hash(self) -> str:
        """Return the content hash over the whole registry projection."""
        return content_hash(self.to_dict())

    @classmethod
    def from_descriptors(cls, descriptors: Iterable[ProviderDescriptor]) -> ProviderRegistry:
        """Build a registry from descriptors (the discovery → registry path)."""
        registry = cls()
        registry.register_all(descriptors)
        return registry

    @classmethod
    def from_payloads(cls, payloads: Iterable[Mapping[str, Any]]) -> ProviderRegistry:
        """Build a registry from plain descriptor mappings (the JSON catalog path)."""
        return cls.from_descriptors(ProviderDescriptor.from_dict(payload) for payload in payloads)


__all__ = [
    "PROVIDER_REGISTRY_VERSION",
    "ProviderRegistration",
    "ProviderRegistry",
]
