"""UCOS-EPIC-001 — Universal Registry Platform domain records.

Immutable, typed value objects for the registration authority:

    * :class:`RegistrationRequest` — the validated *input* to a registration act;
    * :class:`Registration` — an immutable *record of record* for one artifact
      version (append-only; supersede-not-overwrite);
    * :class:`AuditEntry` / :class:`AuditAct` — the hash-chained audit trail unit.

The models parse defensively and never mutate. Version ordering reuses the frozen
Foundation :class:`~engine.foundation.contracts.contract.Version` (semantic
versioning, PL-05). Every record exposes :meth:`to_dict` for deterministic
serialisation (persistence, evidence, and audit hashing).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from engine.foundation.contracts.contract import Version
from engine.registry.universal.errors import RegistrationValidationError
from engine.registry.universal.identity import (
    RegistryKind,
    content_digest,
    deterministic_id,
    normalize_namespace,
    normalize_natural_key,
)


class RegistrationState(str, Enum):
    """The lifecycle state of a single registered version (append-only)."""

    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


class AuditAct(str, Enum):
    """The governed acts recorded on the append-only audit trail."""

    REGISTER = "REGISTER"
    REGISTER_VERSION = "REGISTER_VERSION"
    SUPERSEDE = "SUPERSEDE"
    DEPRECATE = "DEPRECATE"
    RETIRE = "RETIRE"


def _as_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistrationValidationError("expected a non-empty string", field=field_name)
    return value


def _as_str_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str) or not all(isinstance(v, str) and v for v in value):
        raise RegistrationValidationError(
            "expected an array of non-empty strings", field=field_name
        )
    # De-duplicate while preserving order (stable, deterministic).
    seen: dict[str, None] = {}
    for item in value:
        seen.setdefault(item, None)
    return tuple(seen)


def _freeze(payload: Any) -> Any:
    """Recursively convert mappings/lists into hashable, ordered structures.

    Attribute payloads are stored as canonical, immutable structures so a
    :class:`Registration` is hashable and its content digest is stable.
    """
    if isinstance(payload, Mapping):
        return tuple(sorted((str(k), _freeze(v)) for k, v in payload.items()))
    if isinstance(payload, list | tuple):
        return tuple(_freeze(v) for v in payload)
    if isinstance(payload, bool | int | float | str) or payload is None:
        return payload
    raise RegistrationValidationError(
        "attribute values must be JSON scalars, lists, or objects",
        got=type(payload).__name__,
    )


def _thaw(frozen: Any) -> Any:
    """Inverse of :func:`_freeze` — reconstruct plain dict/list structures."""
    if isinstance(frozen, tuple):
        # A frozen mapping is a tuple of (str, value) pairs; anything else a list.
        if frozen and all(
            isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str)
            for item in frozen
        ):
            return {key: _thaw(value) for key, value in frozen}
        return [_thaw(item) for item in frozen]
    return frozen


@dataclass(frozen=True, slots=True)
class RegistrationRequest:
    """A validated request to register (a version of) an artifact.

    ``natural_key`` + ``namespace`` + ``kind`` determine the deterministic
    ``universal_id``; ``attributes`` is the kind-specific payload that determines
    the content digest (Knowledge Once). All string collections are de-duplicated.
    """

    kind: RegistryKind
    namespace: str
    natural_key: str
    name: str
    version: Version
    attributes: Mapping[str, Any] = field(default_factory=dict)
    description: str = ""
    owner: str = "UNASSIGNED"
    dependencies: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()

    @classmethod
    def build(
        cls,
        *,
        kind: RegistryKind | str,
        namespace: str,
        natural_key: str,
        name: str,
        version: str | Version,
        attributes: Mapping[str, Any] | None = None,
        description: str = "",
        owner: str = "UNASSIGNED",
        dependencies: Any = None,
        tags: Any = None,
        provenance: Any = None,
    ) -> RegistrationRequest:
        """Validate raw inputs and return an immutable request."""
        resolved_kind = RegistryKind.coerce(kind)
        resolved_version = version if isinstance(version, Version) else Version.parse(version)
        attrs = attributes or {}
        if not isinstance(attrs, Mapping):
            raise RegistrationValidationError("attributes must be an object", field="attributes")
        # Round-trip through _freeze to validate value types eagerly (fail loud).
        _freeze(dict(attrs))
        return cls(
            kind=resolved_kind,
            namespace=normalize_namespace(namespace),
            natural_key=normalize_natural_key(natural_key),
            name=_as_str(name, field_name="name"),
            version=resolved_version,
            attributes=dict(attrs),
            description=description or "",
            owner=owner or "UNASSIGNED",
            dependencies=_as_str_tuple(dependencies, field_name="dependencies"),
            tags=_as_str_tuple(tags, field_name="tags"),
            provenance=_as_str_tuple(provenance, field_name="provenance"),
        )

    @property
    def universal_id(self) -> str:
        """The deterministic identity this request resolves to."""
        return deterministic_id(self.kind, self.namespace, self.natural_key)

    def content_hash(self) -> str:
        """The SHA-256 content digest for Knowledge-Once equality.

        Covers the *substantive* payload (kind, name, attributes, dependencies)
        but deliberately **not** the identity (namespace / natural_key) nor the
        version. This makes identical content registered under a *different*
        identity detectable (Knowledge Once), while a genuine content change
        across versions is not falsely flagged as a duplicate.
        """
        return content_digest(
            {
                "kind": self.kind.value,
                "name": self.name,
                "attributes": dict(self.attributes),
                "dependencies": list(self.dependencies),
            }
        )


@dataclass(frozen=True, slots=True)
class Registration:
    """An immutable record of one registered artifact version (append-only)."""

    universal_id: str
    kind: RegistryKind
    namespace: str
    natural_key: str
    name: str
    version: Version
    state: RegistrationState
    content_hash: str
    owner: str
    description: str
    dependencies: tuple[str, ...]
    tags: tuple[str, ...]
    provenance: tuple[str, ...]
    sequence: int
    _attributes: Any = ()
    superseded_by: str | None = None

    @classmethod
    def from_request(cls, request: RegistrationRequest, *, sequence: int) -> Registration:
        """Materialise an ``ACTIVE`` registration record from a request."""
        return cls(
            universal_id=request.universal_id,
            kind=request.kind,
            namespace=request.namespace,
            natural_key=request.natural_key,
            name=request.name,
            version=request.version,
            state=RegistrationState.ACTIVE,
            content_hash=request.content_hash(),
            owner=request.owner,
            description=request.description,
            dependencies=request.dependencies,
            tags=request.tags,
            provenance=request.provenance,
            sequence=sequence,
            _attributes=_freeze(dict(request.attributes)),
        )

    @property
    def attributes(self) -> dict[str, Any]:
        """The kind-specific attribute payload as a plain dict."""
        thawed = _thaw(self._attributes)
        return thawed if isinstance(thawed, dict) else {}

    @property
    def version_str(self) -> str:
        return str(self.version)

    def with_state(
        self, state: RegistrationState, *, superseded_by: str | None = None
    ) -> Registration:
        """Return a copy in a new lifecycle ``state`` (immutable transition)."""
        return replace(self, state=state, superseded_by=superseded_by)

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serialisable representation (persistence/evidence)."""
        return {
            "universal_id": self.universal_id,
            "kind": self.kind.value,
            "namespace": self.namespace,
            "natural_key": self.natural_key,
            "name": self.name,
            "version": self.version_str,
            "state": self.state.value,
            "content_hash": self.content_hash,
            "owner": self.owner,
            "description": self.description,
            "dependencies": list(self.dependencies),
            "tags": list(self.tags),
            "provenance": list(self.provenance),
            "sequence": self.sequence,
            "attributes": self.attributes,
            "superseded_by": self.superseded_by,
        }


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """One tamper-evident entry on the append-only audit trail.

    ``entry_hash`` chains over the previous entry's hash plus this entry's
    canonical body, so any retroactive edit or reordering breaks the chain.
    """

    sequence: int
    act: AuditAct
    universal_id: str
    version: str
    content_hash: str
    state: str
    actor: str
    timestamp: str
    prev_hash: str
    entry_hash: str = ""

    def body(self) -> dict[str, Any]:
        """The canonical, hashed body (everything except ``entry_hash``)."""
        return {
            "sequence": self.sequence,
            "act": self.act.value,
            "universal_id": self.universal_id,
            "version": self.version,
            "content_hash": self.content_hash,
            "state": self.state,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
        }

    def compute_hash(self) -> str:
        """Recompute the chained hash for this entry."""
        return content_digest(self.body())

    def sealed(self) -> AuditEntry:
        """Return a copy with ``entry_hash`` set to the computed chain hash."""
        return replace(self, entry_hash=self.compute_hash())

    def to_dict(self) -> dict[str, Any]:
        payload = self.body()
        payload["entry_hash"] = self.entry_hash
        return payload


__all__ = [
    "RegistrationState",
    "AuditAct",
    "RegistrationRequest",
    "Registration",
    "AuditEntry",
]
