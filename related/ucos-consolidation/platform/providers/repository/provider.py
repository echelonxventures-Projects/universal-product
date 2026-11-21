"""UCOS Ω∞ — Repository Provider (Terminal-04, Repository First).

The reference implementation of the Universal Provider Architecture, and the proof
that the constitutional interface is sufficient for a real substrate. It provides
**repository artifacts** — files in a UCOS working tree — as attested, content-hashed
provider resources.

It is deliberately unremarkable. That is the point: everything constitutional comes
from :class:`~platform.universal_provider.sdk.BaseProvider`, and this module supplies
only substrate access:

    * :meth:`RepositoryProvider.resolve_query`    — enumerate matching artifacts.
    * :meth:`RepositoryProvider.resolve_resource` — resolve one artifact by path.
    * :meth:`RepositoryProvider.probe`            — is the working tree readable?

Every other constitutional obligation — capability admission, selector validation,
deterministic ordering, pagination, provenance injection, attestation derivation,
fault isolation — is inherited and cannot be bypassed. A second provider, for any
substrate whatsoever, is written exactly this way.

**Containment.** The provider reads only inside its configured ``root``, resolves every
candidate path, and refuses anything that escapes the root — so a crafted resource id
cannot be used to read outside the declared substrate. Its sole declared effect is
``fs:read`` (PC-08); it never writes.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from pathlib import Path
from platform.universal_provider.constitution import ProviderOperation
from platform.universal_provider.contracts import (
    ProviderCapability,
    ProviderDescriptor,
    ProviderQuery,
    ProviderResource,
)
from platform.universal_provider.sdk import BaseProvider, declare_capability, declare_provider
from typing import Any

#: Provider identity. Declared here *and* in the catalog manifest; the framework binds
#: to the manifest, and gate ``PV-11-CERTIFIABLE`` refuses any divergence between the
#: registered descriptor and the one under validation.
REPOSITORY_PROVIDER_ID = "ucos.repository"
REPOSITORY_PROVIDER_KIND = "repository"
REPOSITORY_PROVIDER_VERSION = "1.0.0"

#: The resource kind this provider yields.
ARTIFACT_KIND = "repository.artifact"

#: Capability names.
CAPABILITY_ARTIFACTS = "repository.artifacts"
CAPABILITY_ARTIFACT = "repository.artifact"
CAPABILITY_ATTESTATION = "repository.attestation"

#: Default glob patterns, applied relative to ``root``. Bounded on purpose: a provider
#: declares a substrate, not "everything reachable".
DEFAULT_PATTERNS: tuple[str, ...] = ("*.md",)

#: Ceiling on indexed artifacts, so an unexpected substrate cannot make a query
#: unbounded. Exceeding it truncates deterministically rather than hanging.
MAX_INDEXED_ARTIFACTS = 5_000


def repository_root() -> Path:
    """Return the repository root inferred from this module's location.

    ``platform/providers/repository/provider.py`` -> ``parents[3]`` is the root.
    """
    return Path(__file__).resolve().parents[3]


def repository_capabilities() -> tuple[ProviderCapability, ...]:
    """Declare the Repository provider's capability surface (PC-04)."""
    return (
        declare_capability(
            CAPABILITY_ARTIFACTS,
            ProviderOperation.QUERY,
            resource_kind=ARTIFACT_KIND,
            description="Enumerate repository artifacts matching a path/name selector.",
            selector_keys=("path_prefix", "suffix", "name_contains"),
            deterministic=True,
            effects=("fs:read",),
        ),
        declare_capability(
            CAPABILITY_ARTIFACT,
            ProviderOperation.FETCH,
            resource_kind=ARTIFACT_KIND,
            description="Resolve one repository artifact by its repository-relative path.",
            deterministic=True,
            effects=("fs:read",),
        ),
        declare_capability(
            CAPABILITY_ATTESTATION,
            ProviderOperation.VERIFY,
            resource_kind=ARTIFACT_KIND,
            description="Attest a repository artifact's content hash and provenance chain.",
            deterministic=True,
            effects=("fs:read",),
        ),
    )


def repository_descriptor(
    *, entry_point: str = "platform.providers.repository.provider:build"
) -> ProviderDescriptor:
    """Return the Repository provider's descriptor (PC-03).

    Kept in code as well as in the catalog manifest so the two can be diffed: the
    manifest is authoritative for the framework, and this function is what a manifest
    author writes against.
    """
    return declare_provider(
        REPOSITORY_PROVIDER_ID,
        REPOSITORY_PROVIDER_KIND,
        REPOSITORY_PROVIDER_VERSION,
        name="UCOS Repository Provider",
        authority="TERMINAL-04",
        description=(
            "Provides UCOS repository artifacts as attested, content-hashed resources. "
            "Reference implementation of the Universal Provider Architecture."
        ),
        source_of_record="UCOS repository working tree",
        entry_point=entry_point,
        capabilities=repository_capabilities(),
        config_schema={
            "root": "absolute path to the repository working tree",
            "patterns": "list of glob patterns applied relative to root",
        },
        metadata={"reference_implementation": True, "repository_first": True},
    )


class RepositoryProvider(BaseProvider):
    """A provider whose substrate is a UCOS repository working tree."""

    def __init__(
        self, descriptor: ProviderDescriptor, config: Mapping[str, Any] | None = None
    ) -> None:
        super().__init__(descriptor, config)
        resolved = dict(config or {})
        raw_root = resolved.get("root")
        self._root = Path(str(raw_root)).resolve() if raw_root else repository_root()
        raw_patterns = resolved.get("patterns")
        if isinstance(raw_patterns, str):
            patterns: tuple[str, ...] = (raw_patterns,)
        elif isinstance(raw_patterns, list | tuple) and raw_patterns:
            patterns = tuple(str(pattern) for pattern in raw_patterns)
        else:
            patterns = DEFAULT_PATTERNS
        self._patterns = patterns

    @property
    def root(self) -> Path:
        return self._root

    @property
    def patterns(self) -> tuple[str, ...]:
        return self._patterns

    # ------------------------------------------------------------------ author hooks

    def probe(self) -> dict[str, bool]:
        """Report whether the declared substrate is present and readable."""
        return {
            "root_exists": self._root.is_dir(),
            "root_readable": self._root.is_dir() and self._can_list(),
        }

    def resolve_query(
        self, capability: ProviderCapability, request: ProviderQuery
    ) -> Iterable[ProviderResource]:
        """Yield every artifact matching the selector.

        Ordering and pagination are the SDK's responsibility, so this hook is a pure
        filter over the indexed substrate.
        """
        del capability  # the SDK has already admitted the capability and selector
        selector = request.selector
        path_prefix = str(selector.get("path_prefix") or "")
        suffix = str(selector.get("suffix") or "")
        name_contains = str(selector.get("name_contains") or "")
        for path in self._index():
            relative = path.relative_to(self._root).as_posix()
            if path_prefix and not relative.startswith(path_prefix):
                continue
            if suffix and not relative.endswith(suffix):
                continue
            if name_contains and name_contains not in path.name:
                continue
            resource = self._as_resource(path, relative)
            if resource is not None:
                yield resource

    def resolve_resource(self, resource_id: str) -> ProviderResource | None:
        """Resolve one artifact by repository-relative path, refusing escapes."""
        candidate = (self._root / resource_id).resolve()
        if not self._contained(candidate):
            return None
        if not candidate.is_file():
            return None
        return self._as_resource(candidate, candidate.relative_to(self._root).as_posix())

    def provenance_chain(self, resource: ProviderResource) -> tuple[str, ...]:
        """Extend the default chain with the artifact's own repository path (PC-06)."""
        base = super().provenance_chain(resource)
        return (*base, f"path:{resource.resource_id}")

    # --------------------------------------------------------------------- internals

    def _can_list(self) -> bool:
        try:
            next(iter(self._root.iterdir()), None)
        except OSError:
            return False
        return True

    def _index(self) -> tuple[Path, ...]:
        """Return the bounded, deterministic artifact index."""
        if not self._root.is_dir():
            return ()
        found: set[Path] = set()
        for pattern in self._patterns:
            for path in self._root.glob(pattern):
                if path.is_file() and self._contained(path.resolve()):
                    found.add(path.resolve())
        ordered = sorted(found, key=lambda path: path.relative_to(self._root).as_posix())
        return tuple(ordered[:MAX_INDEXED_ARTIFACTS])

    def _contained(self, candidate: Path) -> bool:
        """Whether ``candidate`` lies inside the declared substrate root."""
        return candidate == self._root or self._root in candidate.parents

    def _as_resource(self, path: Path, relative: str) -> ProviderResource | None:
        """Project one file into a conformant provider resource."""
        try:
            data = path.read_bytes()
        except OSError:
            return None
        digest = hashlib.sha256(data).hexdigest()
        return self.resource(
            relative,
            ARTIFACT_KIND,
            {
                "path": relative,
                "name": path.name,
                "suffix": path.suffix,
                "size_bytes": len(data),
                "sha256": digest,
            },
            provenance={
                "source_of_record": self._descriptor.source_of_record,
                "root": self._root.as_posix(),
                "sha256": digest,
            },
        )


def build(
    descriptor: ProviderDescriptor, config: Mapping[str, Any] | None = None
) -> RepositoryProvider:
    """The declared entry point: ``platform.providers.repository.provider:build``.

    Discovery calls this with the registered descriptor and the resolved
    configuration. Nothing else in the framework references this module.
    """
    return RepositoryProvider(descriptor, config)


__all__ = [
    "ARTIFACT_KIND",
    "CAPABILITY_ARTIFACT",
    "CAPABILITY_ARTIFACTS",
    "CAPABILITY_ATTESTATION",
    "DEFAULT_PATTERNS",
    "MAX_INDEXED_ARTIFACTS",
    "REPOSITORY_PROVIDER_ID",
    "REPOSITORY_PROVIDER_KIND",
    "REPOSITORY_PROVIDER_VERSION",
    "RepositoryProvider",
    "build",
    "repository_capabilities",
    "repository_descriptor",
    "repository_root",
]
