"""UCOS-EPIC-001 — the Universal Constitutional Identifier Dictionary (D-03).

Repository truth before this module
-----------------------------------
The repository had a **term** dictionary (:mod:`engine.uckp.vocabulary` — thirteen
vocabularies, append-only, fail-closed at use) and an id *ledger* covering only the
sequential ``UCOS-<CAT>-NNNNNN`` page family. Neither is an **assigned-identifier**
dictionary: nothing enumerated the identifiers actually minted by
:func:`engine.registry.universal.identity.deterministic_id`. Lifecycle stage
``UCL-S-0320`` ("Update Universal Constitutional Identifier Dictionary") therefore bound
to nothing.

This module is that dictionary. It is a **projection**, not a second authority: it stores
no identifier it did not receive, mints nothing, and every entry it holds must parse under
the one identifier grammar. Two properties make it useful rather than decorative:

    * **exactly once** — registering the same identity tuple twice is idempotent, while a
      second *different* entry under one identifier is refused. That is what makes "every
      minted id appears exactly once" a checkable statement;
    * **round-trip provable** — every entry records the ``(kind, namespace, natural_key)``
      it was minted from, so :meth:`IdentifierDictionary.verify` re-mints each identifier
      and fails closed on any that does not reproduce.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.registry.universal.errors import RegistrationValidationError
from engine.registry.universal.identity import (
    canonical_json,
    content_digest,
    deterministic_id,
    is_well_formed,
    normalize_namespace,
    normalize_natural_key,
    parse_kind_name,
    resolve_kind_code,
)


@dataclass(frozen=True, slots=True)
class IdentifierEntry:
    """One assigned identifier and the identity tuple it was minted from."""

    universal_id: str
    kind: str
    namespace: str
    natural_key: str
    owner: str = ""
    lineage: tuple[str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not is_well_formed(self.universal_id):
            raise RegistrationValidationError(
                "dictionary entries carry identifiers minted by the one authority",
                value=self.universal_id,
            )
        object.__setattr__(self, "kind", str(self.kind).strip().upper())
        object.__setattr__(self, "namespace", normalize_namespace(self.namespace))
        object.__setattr__(self, "natural_key", normalize_natural_key(self.natural_key))
        object.__setattr__(self, "lineage", tuple(self.lineage))
        object.__setattr__(self, "attributes", dict(self.attributes or {}))

    @classmethod
    def of(
        cls,
        kind: Any,
        namespace: str,
        natural_key: str,
        *,
        owner: str = "",
        lineage: Iterable[str] = (),
        attributes: Mapping[str, Any] | None = None,
    ) -> IdentifierEntry:
        """Mint the identifier for an identity tuple and return the dictionary entry."""
        return cls(
            universal_id=deterministic_id(kind, namespace, natural_key),
            kind=str(getattr(kind, "value", kind)),
            namespace=namespace,
            natural_key=natural_key,
            owner=owner,
            lineage=tuple(lineage),
            attributes=dict(attributes or {}),
        )

    def reproduces(self) -> bool:
        """True iff re-minting from the recorded identity tuple returns this identifier."""
        try:
            minted = deterministic_id(self.kind, self.namespace, self.natural_key)
            return minted == self.universal_id
        except RegistrationValidationError:
            return False

    @property
    def code(self) -> str:
        """The kind code embedded in the identifier."""
        return self.universal_id.split("-")[1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "universal_id": self.universal_id,
            "kind": self.kind,
            "code": self.code,
            "namespace": self.namespace,
            "natural_key": self.natural_key,
            "owner": self.owner,
            "lineage": list(self.lineage),
            "attributes": dict(self.attributes),
        }


class IdentifierDictionary:
    """The register of every assigned universal identifier, each appearing exactly once."""

    __slots__ = ("_entries",)

    def __init__(self, entries: Iterable[IdentifierEntry] = ()) -> None:
        self._entries: dict[str, IdentifierEntry] = {}
        for entry in entries:
            self.add(entry)

    # -- registration ------------------------------------------------------- #

    def add(self, entry: IdentifierEntry) -> IdentifierEntry:
        """Record one identifier. Idempotent for an identical entry, refusing conflicts.

        Raises:
            RegistrationValidationError: a *different* entry already holds this identifier.
        """
        existing = self._entries.get(entry.universal_id)
        if existing is not None:
            if existing == entry:
                return existing
            raise RegistrationValidationError(
                "an assigned identifier may not be re-bound to a different identity",
                value=entry.universal_id,
                existing=existing.to_dict(),
                given=entry.to_dict(),
            )
        self._entries[entry.universal_id] = entry
        return entry

    def assign(
        self,
        kind: Any,
        namespace: str,
        natural_key: str,
        *,
        owner: str = "",
        lineage: Iterable[str] = (),
        attributes: Mapping[str, Any] | None = None,
    ) -> IdentifierEntry:
        """Mint and record an identifier in one call — the common path."""
        return self.add(
            IdentifierEntry.of(
                kind,
                namespace,
                natural_key,
                owner=owner,
                lineage=lineage,
                attributes=attributes,
            )
        )

    # -- lookup ------------------------------------------------------------- #

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, universal_id: object) -> bool:
        return str(universal_id) in self._entries

    def resolve(self, universal_id: str) -> IdentifierEntry:
        """Return the entry for ``universal_id`` or fail closed (D-01 resolution)."""
        entry = self._entries.get(str(universal_id))
        if entry is None:
            raise RegistrationValidationError(
                "identifier is not in the dictionary", value=universal_id
            )
        return entry

    def lookup(self, kind: Any, namespace: str, natural_key: str) -> IdentifierEntry:
        """Resolve by identity tuple rather than by identifier."""
        return self.resolve(deterministic_id(kind, namespace, natural_key))

    def identifiers(self) -> tuple[str, ...]:
        return tuple(sorted(self._entries))

    def entries(
        self, *, kind: Any = None, namespace: str | None = None
    ) -> tuple[IdentifierEntry, ...]:
        found = tuple(self._entries[k] for k in sorted(self._entries))
        if kind is not None:
            code = resolve_kind_code(kind)
            found = tuple(e for e in found if e.code == code)
        if namespace is not None:
            wanted = normalize_namespace(namespace)
            found = tuple(e for e in found if e.namespace == wanted)
        return found

    def by_kind(self) -> dict[str, int]:
        """The population by kind name, ordered."""
        counts: dict[str, int] = {}
        for entry in self._entries.values():
            name = parse_kind_name(entry.universal_id)
            counts[name] = counts.get(name, 0) + 1
        return {k: counts[k] for k in sorted(counts)}

    # -- validation --------------------------------------------------------- #

    def unreproducible(self) -> tuple[str, ...]:
        """Identifiers that do not re-mint from their own recorded identity tuple."""
        return tuple(sorted(k for k, e in self._entries.items() if not e.reproduces()))

    def unparsed(self) -> tuple[str, ...]:
        """Identifiers the one grammar cannot parse. Must always be empty."""
        return tuple(sorted(k for k in self._entries if not is_well_formed(k)))

    def duplicated_natural_keys(self) -> tuple[str, ...]:
        """``kind/namespace/natural_key`` triples claimed by more than one identifier.

        Always empty when every identifier was minted by the one authority, because the
        identifier is a pure function of the triple. A non-empty result means an
        identifier entered from outside the authority.
        """
        seen: dict[tuple[str, str, str], str] = {}
        clashes: set[str] = set()
        for entry in self._entries.values():
            key = (entry.code, entry.namespace, entry.natural_key)
            if key in seen and seen[key] != entry.universal_id:
                clashes.add("/".join(key))
            seen[key] = entry.universal_id
        return tuple(sorted(clashes))

    def verify(self) -> dict[str, Any]:
        """Verify the whole dictionary. Fail-closed report; empty lists mean healthy."""
        unreproducible = self.unreproducible()
        unparsed = self.unparsed()
        duplicated = self.duplicated_natural_keys()
        return {
            "schema": "ucos-identifier-dictionary-verification",
            "version": "1.0.0",
            "count": len(self._entries),
            "by_kind": self.by_kind(),
            "unreproducible": list(unreproducible),
            "unparsed": list(unparsed),
            "duplicated_natural_keys": list(duplicated),
            "parse_coverage": 1.0 if self._entries and not unparsed else (0.0 if unparsed else 1.0),
            "status": "PASS" if not (unreproducible or unparsed or duplicated) else "FAIL",
        }

    @property
    def is_verified(self) -> bool:
        return self.verify()["status"] == "PASS"

    # -- serialisation ------------------------------------------------------ #

    def to_document(self) -> dict[str, Any]:
        return {
            "schema": "ucos-universal-identifier-dictionary",
            "version": "1.0.0",
            "count": len(self._entries),
            "by_kind": self.by_kind(),
            "entries": [self._entries[k].to_dict() for k in sorted(self._entries)],
            "closed_set": False,
            "upper_limit": None,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_document())

    def digest(self) -> str:
        return content_digest(self.to_document())

    @classmethod
    def from_document(cls, payload: Mapping[str, Any]) -> IdentifierDictionary:
        """Rebuild a dictionary from its own document — the replay path."""
        raw = payload.get("entries")
        if not isinstance(raw, list):
            raise RegistrationValidationError(
                "dictionary document must carry an 'entries' list", value=type(raw).__name__
            )
        return cls(
            IdentifierEntry(
                universal_id=item["universal_id"],
                kind=item["kind"],
                namespace=item["namespace"],
                natural_key=item["natural_key"],
                owner=item.get("owner", ""),
                lineage=tuple(item.get("lineage", ())),
                attributes=item.get("attributes", {}),
            )
            for item in raw
        )


def dictionary_for(registry: Any) -> IdentifierDictionary:
    """Project a :class:`~engine.nucleus.registry.NucleusRegistry` into the dictionary.

    Every structural subject and every capability contributes exactly one entry, with the
    owning nucleus recorded as the entry's owner and the ownership authority as its
    lineage. Imported lazily-by-duck-typing (``registry`` is only read) so this module
    keeps no dependency on the nucleus package and the layering stays one-directional.

    If the registry is bound to a reference frame, that frame's identifier joins every
    entry's ``lineage`` and the frame key its attributes. The projection therefore carries
    the same context the population was registered under: an identifier assigned in one
    reality is distinguishable, in the dictionary itself, from the same key assigned in
    another. An unbound registry projects exactly as before.
    """
    dictionary = IdentifierDictionary()
    context = dict(getattr(registry, "context", {}) or {})
    frame = str(context.get("frame", ""))
    frame_id = str(context.get("frame_id", ""))
    context_lineage: tuple[str, ...] = (frame_id,) if frame_id else ()
    context_attributes = {"context_frame": frame} if frame else {}
    for subject in registry.subjects():
        dictionary.assign(
            subject.role.value.upper() if subject.role.value != "composition" else "COMPOSITION",
            subject.namespace,
            subject.key,
            owner=subject.universal_id,
            lineage=context_lineage,
            attributes={
                "role": subject.role.value,
                "concept": subject.concept,
                **context_attributes,
            },
        )
    for capability in registry.capabilities():
        dictionary.assign(
            "CAPABILITY",
            capability.namespace,
            capability.key,
            owner=capability.owner_id,
            lineage=(capability.owner_id, *context_lineage),
            attributes={"owner_key": capability.owner_key, **context_attributes},
        )
    return dictionary


__all__ = ["IdentifierEntry", "IdentifierDictionary", "dictionary_for"]
