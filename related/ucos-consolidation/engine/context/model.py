"""UCXI-000001 Part 04 — Context value objects (declarations, values, records).

The immutable value types every other part of the layer exchanges. Three properties
are structural rather than conventional here:

    * **Provenance is mandatory** (CXL-08): a :class:`ContextValue` cannot exist
      without an authority and a source. There is no constructor path that yields an
      unattributed value, so an unprovenanced context cannot enter the registry.
    * **Identity is derived, never supplied** (CXL-05): a :class:`ContextRecord`'s
      ``context_id`` is minted by the single registration authority
      (:mod:`engine.registry.universal.identity`) as a pure function of
      ``(kind, namespace, natural_key)`` — the same identity function every other
      registered artifact uses, so context identities never collide with them and are
      reproducible across machines and runs.
    * **Content is sealed** (CXL-09): every record carries the SHA-256 of its own
      canonical rendering, computed with the hash field excluded, so tampering and
      drift are detectable and *Context Once* (CXL-06) is enforceable by content.

Canonical JSON, content digests and identifier minting are **reused** from the
registry's identity module rather than reimplemented, so the platform has exactly one
canonicalisation and one identifier authority.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.context.errors import ContextValidationError
from engine.context.taxonomy import (
    ContextAuthority,
    ContextLifecycle,
    ContextRelation,
)
from engine.registry.universal.identity import (
    RegistryKind,
    canonical_json,
    content_digest,
    deterministic_id,
    normalize_namespace,
    normalize_natural_key,
)

#: The field excluded from a payload when computing that payload's own hash.
HASH_FIELD = "content_hash"

_JSON_SCALARS = (str, int, float, bool, type(None))


def json_safe(value: Any, *, at: str = "value") -> Any:
    """Return ``value`` normalised to a canonical, JSON-representable form.

    Tuples become lists and mappings are key-sorted, so two structurally equal
    values always canonicalise to the same bytes. Anything not representable is
    refused rather than coerced through ``str`` (which would silently invent data).
    """
    if isinstance(value, _JSON_SCALARS):
        return value
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for key in sorted(value):
            if not isinstance(key, str):
                raise ContextValidationError(
                    "mapping keys must be strings to be canonical", at=at, key=repr(key)
                )
            out[key] = json_safe(value[key], at=f"{at}.{key}")
        return out
    if isinstance(value, list | tuple):
        return [json_safe(item, at=f"{at}[]") for item in value]
    raise ContextValidationError(
        "context values must be JSON-representable", at=at, type=type(value).__name__
    )


def seal(payload: Mapping[str, Any]) -> str:
    """Return the content digest of ``payload`` with its own hash field excluded."""
    return content_digest({k: v for k, v in payload.items() if k != HASH_FIELD})


@dataclass(frozen=True, slots=True)
class ContextValue:
    """One dimension of one context, with the provenance that makes it assertable.

    ``source`` is a reference (a path, an instrument id, a sensor name) — never a
    secret value (SEC-04). ``authority`` fixes precedence during resolution.
    """

    dimension: str
    value: Any
    authority: ContextAuthority
    source: str

    def __post_init__(self) -> None:
        if not isinstance(self.dimension, str) or not self.dimension.strip():
            raise ContextValidationError("dimension must be a non-empty string")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ContextValidationError(
                "a context value must name its source (provenance is mandatory)",
                dimension=self.dimension,
            )
        object.__setattr__(self, "dimension", self.dimension.strip())
        object.__setattr__(self, "source", self.source.strip())
        object.__setattr__(
            self, "authority", ContextAuthority.coerce(self.authority, at=self.dimension)
        )
        object.__setattr__(self, "value", json_safe(self.value, at=self.dimension))

    def outranks(self, other: ContextValue) -> bool:
        """True iff this value's authority strictly outranks ``other``'s."""
        return self.authority.outranks(other.authority)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "value": self.value,
            "authority": self.authority.value,
            "source": self.source,
        }


def values_from_mapping(
    values: Mapping[str, Any], *, authority: ContextAuthority, source: str
) -> tuple[ContextValue, ...]:
    """Build provenanced values from a plain ``{dimension: value}`` mapping."""
    return tuple(
        ContextValue(dimension=name, value=values[name], authority=authority, source=source)
        for name in sorted(values)
    )


@dataclass(frozen=True, slots=True)
class ContextDeclaration:
    """A request to register one context (the pre-identity form of a record).

    ``boundary`` is the bounding frame the context belongs to — a context is never
    unbounded (CXL-03). ``parent`` optionally names a broader context that contains
    this one.
    """

    kind: str
    namespace: str
    natural_key: str
    values: tuple[ContextValue, ...]
    authority: ContextAuthority = ContextAuthority.OPERATIONAL
    boundary: str = "universal"
    parent: str | None = None
    description: str = ""

    def __post_init__(self) -> None:
        kind = getattr(self.kind, "value", self.kind)
        if not isinstance(kind, str) or not kind.strip():
            raise ContextValidationError("a declaration must name its context kind")
        object.__setattr__(self, "kind", kind.strip())
        object.__setattr__(self, "namespace", normalize_namespace(self.namespace))
        object.__setattr__(self, "natural_key", normalize_natural_key(self.natural_key))
        object.__setattr__(
            self, "authority", ContextAuthority.coerce(self.authority, at=self.natural_key)
        )
        if not isinstance(self.boundary, str) or not self.boundary.strip():
            raise ContextValidationError(
                "a context must declare its bounding frame (no unbounded context)",
                kind=self.kind,
                natural_key=self.natural_key,
            )
        object.__setattr__(self, "boundary", self.boundary.strip())
        if not self.values:
            raise ContextValidationError(
                "a context must assert at least one dimension",
                kind=self.kind,
                natural_key=self.natural_key,
            )
        seen: set[str] = set()
        for value in self.values:
            if value.dimension in seen:
                raise ContextValidationError(
                    "duplicate dimension in a declaration",
                    kind=self.kind,
                    dimension=value.dimension,
                )
            seen.add(value.dimension)
        object.__setattr__(self, "values", tuple(sorted(self.values, key=lambda v: v.dimension)))

    @property
    def identity(self) -> str:
        """The deterministic ``universal_id`` this declaration will be registered as."""
        return deterministic_id(RegistryKind.CONTEXT, self.namespace, self.natural_key)

    def value_mapping(self) -> dict[str, Any]:
        """The declaration's dimensions as a plain ``{dimension: value}`` mapping."""
        return {value.dimension: value.value for value in self.values}

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "namespace": self.namespace,
            "natural_key": self.natural_key,
            "authority": self.authority.value,
            "boundary": self.boundary,
            "parent": self.parent,
            "description": self.description,
            "values": [value.to_dict() for value in self.values],
        }


@dataclass(frozen=True, slots=True)
class ContextRecord:
    """A registered context: a declaration plus derived identity, taxon and seal."""

    context_id: str
    kind: str
    taxon_id: str
    namespace: str
    natural_key: str
    values: tuple[ContextValue, ...]
    authority: ContextAuthority
    lifecycle: ContextLifecycle
    boundary: str
    parent: str | None = None
    description: str = ""
    universal: bool = False
    content_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "authority", ContextAuthority.coerce(self.authority))
        object.__setattr__(self, "lifecycle", ContextLifecycle.coerce(self.lifecycle))
        object.__setattr__(self, "values", tuple(sorted(self.values, key=lambda v: v.dimension)))
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    def _payload(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "kind": self.kind,
            "taxon_id": self.taxon_id,
            "namespace": self.namespace,
            "natural_key": self.natural_key,
            "authority": self.authority.value,
            "boundary": self.boundary,
            "parent": self.parent,
            "description": self.description,
            "universal": self.universal,
            "values": [value.to_dict() for value in self.values],
        }

    # -- accessors ---------------------------------------------------------- #

    def dimension(self, name: str) -> ContextValue | None:
        """The value asserted for ``name``, or ``None``."""
        for value in self.values:
            if value.dimension == name:
                return value
        return None

    def dimensions(self) -> tuple[str, ...]:
        """Every asserted dimension name, ordered."""
        return tuple(value.dimension for value in self.values)

    def value_mapping(self) -> dict[str, Any]:
        """The record's dimensions as a plain ``{dimension: value}`` mapping."""
        return {value.dimension: value.value for value in self.values}

    def expected_identity(self) -> str:
        """The identity this record *should* carry, recomputed from its identity tuple."""
        return deterministic_id(RegistryKind.CONTEXT, self.namespace, self.natural_key)

    def recomputed_hash(self) -> str:
        """The content hash recomputed from the record's current payload."""
        return seal(self._payload())

    def is_intact(self) -> bool:
        """True iff identity and content hash both reproduce from the record itself."""
        return (
            self.context_id == self.expected_identity()
            and self.content_hash == self.recomputed_hash()
        )

    def with_lifecycle(self, target: ContextLifecycle) -> ContextRecord:
        """Return a copy advanced to ``target``, refusing illegal transitions."""
        stage = ContextLifecycle.coerce(target)
        self.lifecycle.require_transition(stage, at=self.context_id)
        return ContextRecord(
            context_id=self.context_id,
            kind=self.kind,
            taxon_id=self.taxon_id,
            namespace=self.namespace,
            natural_key=self.natural_key,
            values=self.values,
            authority=self.authority,
            lifecycle=stage,
            boundary=self.boundary,
            parent=self.parent,
            description=self.description,
            universal=self.universal,
            content_hash=self.content_hash,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["lifecycle"] = self.lifecycle.value
        payload[HASH_FIELD] = self.content_hash
        return payload


@dataclass(frozen=True, slots=True)
class ContextRelationEdge:
    """A typed, directed relation between two registered contexts."""

    relation: ContextRelation
    source: str
    target: str
    note: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "relation", ContextRelation.coerce(self.relation))
        for name in ("source", "target"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ContextValidationError("relation endpoint must be a context id", at=name)
        if self.source == self.target:
            raise ContextValidationError(
                "a context cannot relate to itself", context_id=self.source
            )

    @property
    def edge_id(self) -> str:
        """A deterministic edge identity derived from the triple it expresses."""
        return "CTXE-" + content_digest([self.relation.value, self.source, self.target])[:12]

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "relation": self.relation.value,
            "source": self.source,
            "target": self.target,
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class Observer:
    """An observer: the vantage from which context is asserted (CXL-10).

    An observer confers *no authority*. It records who is looking, so that an
    assertion can be attributed and its epistemic limits stated.
    """

    observer_id: str
    vantage: str
    epistemic_access: str = "unspecified"

    def __post_init__(self) -> None:
        for name in ("observer_id", "vantage"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ContextValidationError("observer field must be a non-empty string", at=name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observer_id": self.observer_id,
            "vantage": self.vantage,
            "epistemic_access": self.epistemic_access,
        }


@dataclass(frozen=True, slots=True)
class ResolvedContext:
    """The outcome of resolving one context kind: values plus their provenance."""

    kind: str
    values: tuple[ContextValue, ...]
    sources: tuple[str, ...] = ()
    considered: tuple[str, ...] = ()
    observer: Observer | None = None
    content_hash: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", tuple(sorted(self.values, key=lambda v: v.dimension)))
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    def _payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "values": [value.to_dict() for value in self.values],
            "sources": list(self.sources),
            "considered": list(self.considered),
            "observer": self.observer.to_dict() if self.observer else None,
        }

    def get(self, dimension: str) -> Any:
        """The resolved value for ``dimension``, or ``None`` if unresolved."""
        for value in self.values:
            if value.dimension == dimension:
                return value.value
        return None

    def provenance_of(self, dimension: str) -> str | None:
        """The source that won ``dimension``, or ``None``."""
        for value in self.values:
            if value.dimension == dimension:
                return value.source
        return None

    def value_mapping(self) -> dict[str, Any]:
        return {value.dimension: value.value for value in self.values}

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload[HASH_FIELD] = self.content_hash
        return payload


__all__ = [
    "HASH_FIELD",
    "canonical_json",
    "content_digest",
    "json_safe",
    "seal",
    "ContextValue",
    "values_from_mapping",
    "ContextDeclaration",
    "ContextRecord",
    "ContextRelationEdge",
    "Observer",
    "ResolvedContext",
]
