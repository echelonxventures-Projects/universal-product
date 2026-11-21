"""Universal Meta-Object and the reflective root Meta-Type.

Two abstractions carry the entire open world:

    * :class:`MetaObject` — the single universal thing. *Anything* the platform ever
      represents (a capability, a contract, a context, a policy, a relationship, a
      provider, a registered instance, a whole civilization) is a ``MetaObject``. It has
      identity, is classified by exactly one meta-type reference, carries an **open**
      attribute map (no fixed schema), may relate to other meta-objects, records its
      provenance, and hashes its own content.

    * :data:`META_TYPE_ROOT` — the reflective root. A *meta-type* is simply a
      ``MetaObject`` whose classifying meta-type is ``MetaType``. The root meta-type is
      classified by itself, so the type-of-types is registered rather than hard-coded.
      This single reflective fixed point is what lets the kernel be finite in code yet
      unbounded in what it can represent: there is no closed base set of "kinds".

A ``MetaObject`` is an immutable value. Evolution (a new version) and composition (a new
relationship) produce *new* value objects; the registry keeps the append-only chain.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.foundation.contracts.contract import Version
from engine.kernel.errors import RelationshipError
from engine.kernel.identity import content_digest, mint, normalize_segment

#: The reflective root. The natural key of the root meta-type and the meta-type reference
#: every meta-type is classified by. It is deliberately a single opaque token, not an
#: enumeration of kinds.
META_TYPE_ROOT = "MetaType"

#: A reference to a meta-type is just its natural key (a string). Open by construction.
MetaTypeRef = str


@dataclass(frozen=True)
class Relationship:
    """A directed, governed edge from a meta-object to another by identifier.

    ``relation`` names the *kind* of relationship (itself an open token — new relation
    kinds need no code change). ``target`` is the identifier of the related meta-object.
    """

    relation: str
    target: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "relation", normalize_segment(self.relation, field="relation"))
        if not isinstance(self.target, str) or not self.target.strip():
            raise RelationshipError("relationship target must be a non-empty identifier")
        object.__setattr__(self, "target", self.target.strip())

    def to_dict(self) -> dict[str, str]:
        """A deterministic, serialisable rendering of the edge."""
        return {"relation": self.relation, "target": self.target}


@dataclass(frozen=True)
class MetaObject:
    """The single universal thing. Immutable; identity is derived, never assigned."""

    metatype: MetaTypeRef
    namespace: str
    natural_key: str
    name: str = ""
    version: Version = field(default_factory=lambda: Version(1, 0, 0))
    attributes: Mapping[str, Any] = field(default_factory=dict)
    relationships: tuple[Relationship, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)

    # Derived, set in __post_init__ (kept out of the constructor surface).
    identity: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        mt = normalize_segment(self.metatype, field="metatype")
        ns = normalize_segment(self.namespace, field="namespace")
        key = normalize_segment(self.natural_key, field="natural_key")
        object.__setattr__(self, "metatype", mt)
        object.__setattr__(self, "namespace", ns)
        object.__setattr__(self, "natural_key", key)
        object.__setattr__(self, "name", self.name or key)
        object.__setattr__(self, "attributes", _freeze_mapping(self.attributes))
        object.__setattr__(self, "provenance", _freeze_mapping(self.provenance))
        object.__setattr__(self, "relationships", _freeze_relationships(self.relationships))
        object.__setattr__(self, "identity", mint(mt, ns, key))

    # -- classification --------------------------------------------------------

    @property
    def is_meta_type(self) -> bool:
        """True iff this object *is a meta-type* (classified by the reflective root)."""
        return self.metatype == META_TYPE_ROOT

    @property
    def is_reflective_root(self) -> bool:
        """True iff this object is the root meta-type classified by itself."""
        return self.metatype == META_TYPE_ROOT and self.natural_key == META_TYPE_ROOT

    @property
    def version_str(self) -> str:
        """The version rendered as ``MAJOR.MINOR.PATCH``."""
        return str(self.version)

    # -- content + evolution + composition -------------------------------------

    def content(self) -> dict[str, Any]:
        """The substantive knowledge body, used for the Knowledge-Once hash.

        Deliberately excludes the *homing* keys (``namespace``/``natural_key``) and the
        ``version``: Knowledge Once is about *what a thing is*, not where it is homed or
        which revision it is. Two distinct identities that carry identical bodies are the
        same knowledge admitted twice — the constitutional violation the hash detects.
        Classification (``metatype``) is part of what a thing *is*, so it is included.
        """
        return {
            "metatype": self.metatype,
            "name": self.name,
            "attributes": dict(self.attributes),
            "relationships": sorted(
                (r.to_dict() for r in self.relationships),
                key=lambda d: (d["relation"], d["target"]),
            ),
        }

    def content_hash(self) -> str:
        """SHA-256 over the substantive body — the Knowledge-Once key."""
        return content_digest(self.content())

    def body_with_home(self) -> dict[str, Any]:
        """The full canonical payload including homing keys and version (for snapshots)."""
        payload = self.content()
        payload["namespace"] = self.namespace
        payload["natural_key"] = self.natural_key
        payload["version"] = self.version_str
        return payload

    def evolve(
        self,
        version: Version,
        *,
        attributes: Mapping[str, Any] | None = None,
        relationships: Sequence[Relationship] | None = None,
        provenance: Mapping[str, Any] | None = None,
        name: str | None = None,
    ) -> MetaObject:
        """Return a new version of this meta-object (same identity, newer version).

        Governed evolution without loss of identity (Universal Evolution): the identifier
        is unchanged because the identity tuple is unchanged.
        """
        return MetaObject(
            metatype=self.metatype,
            namespace=self.namespace,
            natural_key=self.natural_key,
            name=self.name if name is None else name,
            version=version,
            attributes=self.attributes if attributes is None else attributes,
            relationships=(self.relationships if relationships is None else tuple(relationships)),
            provenance=self.provenance if provenance is None else provenance,
        )

    def with_relationship(self, relation: str, target: str) -> MetaObject:
        """Return a copy with an additional relationship (Universal Composition)."""
        edge = Relationship(relation, target)
        if edge in self.relationships:
            return self
        return MetaObject(
            metatype=self.metatype,
            namespace=self.namespace,
            natural_key=self.natural_key,
            name=self.name,
            version=self.version,
            attributes=self.attributes,
            relationships=(*self.relationships, edge),
            provenance=self.provenance,
        )

    def related(self, relation: str | None = None) -> tuple[str, ...]:
        """Identifiers of related targets, optionally filtered by relation kind."""
        return tuple(
            r.target for r in self.relationships if relation is None or r.relation == relation
        )

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serialisable rendering (Universal Discoverability)."""
        payload = self.body_with_home()
        payload["identity"] = self.identity
        payload["is_meta_type"] = self.is_meta_type
        payload["content_hash"] = self.content_hash()
        payload["provenance"] = dict(self.provenance)
        return payload

    def describe(self) -> str:
        """A short human-legible description (Universal Explainability)."""
        role = "meta-type" if self.is_meta_type else f"instance of {self.metatype}"
        return f"{self.identity} — {self.name} [{role}] v{self.version_str}"


def make_metatype(
    natural_key: str,
    *,
    namespace: str = "umk.metatype",
    name: str = "",
    description: str = "",
    attributes: Mapping[str, Any] | None = None,
    provenance: Mapping[str, Any] | None = None,
) -> MetaObject:
    """Build a meta-type: a ``MetaObject`` classified by the reflective root.

    Declaring a new concept-category is exactly this call (or its registry equivalent) —
    no kernel code changes to introduce a category the kernel has never seen.
    """
    attrs = dict(attributes or {})
    if description and "description" not in attrs:
        attrs["description"] = description
    return MetaObject(
        metatype=META_TYPE_ROOT,
        namespace=namespace,
        natural_key=natural_key,
        name=name or natural_key,
        attributes=attrs,
        provenance=dict(provenance or {}),
    )


def reflective_root(namespace: str = "umk.metatype") -> MetaObject:
    """Build the self-classifying root meta-type (``MetaType`` is a ``MetaType``)."""
    return make_metatype(
        META_TYPE_ROOT,
        namespace=namespace,
        name="Universal Meta-Type",
        description=(
            "The reflective root of the Universal Meta-Kernel. Every meta-type is a "
            "meta-object classified by this meta-type; this meta-type is classified by "
            "itself. It is the single fixed point that lets a finite kernel represent an "
            "unbounded, open world of concept-categories through registration alone."
        ),
    )


def _freeze_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    from types import MappingProxyType

    return MappingProxyType(dict(value or {}))


def _freeze_relationships(value: Sequence[Relationship] | None) -> tuple[Relationship, ...]:
    if not value:
        return ()
    out: list[Relationship] = []
    for item in value:
        if isinstance(item, Relationship):
            out.append(item)
        elif isinstance(item, Mapping):
            out.append(Relationship(item["relation"], item["target"]))
        else:
            raise RelationshipError("relationship must be a Relationship or a mapping")
    return tuple(out)


__all__ = [
    "MetaObject",
    "Relationship",
    "MetaTypeRef",
    "META_TYPE_ROOT",
    "make_metatype",
    "reflective_root",
]
