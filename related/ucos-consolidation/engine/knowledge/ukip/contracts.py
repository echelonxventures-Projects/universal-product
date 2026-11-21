"""UKIP Part 01 — Knowledge Intelligence contracts (EPIC-UKDA-003).

The value types every knowledge provider speaks, and the single definition of
*knowledge identity* that makes the Knowledge Once Principle enforceable across an
unbounded number of providers.

    * :class:`ProviderKind` — the open taxonomy of *where* knowledge can come from.
      Adding a provider kind is a one-member edit; adding a *provider* requires no
      edit at all (see :mod:`engine.knowledge.ukip.providers`).
    * :class:`SourceRef` — the immutable, content-addressed citation of the exact
      place a unit was read from. Nothing enters the registry without one, so
      everything is traceable back to a locator and a byte-level digest.
    * :class:`RelationDeclaration` — a provider's claim that its unit relates to
      another unit or canonical id, drawn from the seventeen canonical UKDA
      :class:`~engine.knowledge.model.RelationType` values (no second vocabulary).
    * :class:`KnowledgeUnit` — a provider-emitted candidate unit of knowledge,
      content-addressed twice: :meth:`KnowledgeUnit.unit_sha256` binds the whole
      contribution *including its source* (integrity, provider attribution), while
      :meth:`KnowledgeUnit.knowledge_sha256` binds only the knowledge *substance*
      (kind + statement + rationale) and is therefore the identity under which
      duplication is judged.

**Knowledge identity is deliberately not re-defined here.**
:meth:`KnowledgeUnit.knowledge_sha256` reproduces
:meth:`engine.knowledge.cko.CanonicalKnowledgeObject.semantic_hash` field-for-field
and reuses :func:`engine.knowledge.model.content_hash`, so UKIP's notion of "the
same knowledge" is structurally identical to UKDA's and cannot drift from it. A unit
read from a document and the canonical object authored from it therefore collapse to
one identity — which is precisely what makes N providers safe.

Standard-library only (TP-04/TP-05), deterministic and wall-clock free (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    RelationType,
    canonical_json,
    content_hash,
)
from engine.knowledge.ukip.errors import UnitError
from engine.temporal.coordinate import ValidityPeriod

#: The version of the knowledge-unit wire shape (bumped only on a breaking change).
UNIT_SCHEMA = "ucos-ukip-knowledge-unit"
UNIT_SCHEMA_VERSION = "1.0.0"

#: The prefix of every deterministically derived canonical knowledge identifier.
KNOWLEDGE_ID_PREFIX = "UKID"

#: Hex characters of the knowledge digest carried by a derived identifier. Matches
#: the 12-character discipline of :mod:`engine.registry.universal.identity`.
KNOWLEDGE_ID_DIGEST_LEN = 12


class ProviderKind(str, Enum):
    """UKIP Part 01 — the open taxonomy of knowledge origins.

    Deliberately *kinds*, not providers: the platform admits an unbounded number of
    providers, and each merely declares which kind of origin it speaks for.
    """

    CANONICAL_STORE = "canonical-store"
    DECISION_LOG = "decision-log"
    DOCUMENT = "document"
    SPECIFICATION = "specification"
    CODE = "code"
    REGISTRY = "registry"
    GRAPH = "graph"
    EVIDENCE = "evidence"
    CERTIFICATION = "certification"
    RUNTIME = "runtime"
    CONVERSATION = "conversation"
    EXTERNAL = "external"
    HUMAN = "human"
    DERIVED = "derived"

    @classmethod
    def coerce(cls, value: Any, *, context: str = "provider") -> ProviderKind:
        """Return the enum member for ``value`` or fail loudly (never silently)."""
        try:
            return cls(str(value))
        except ValueError as exc:
            raise UnitError("unknown provider kind", value=value, at=context) from exc


def normalize_text(text: str) -> str:
    """Collapse a free-text field to a stable comparison form.

    Used for provider-supplied prose so that reformatting (line wrapping, trailing
    whitespace, indentation) can never manufacture a second identity for knowledge
    that is in substance the same.
    """
    return " ".join(text.split())


def _require_text(value: Any, *, field_name: str, at: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise UnitError("expected a non-empty string", field=field_name, at=at)
    return value


def _optional_text(value: Any, *, field_name: str, at: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise UnitError("expected a string or null", field=field_name, at=at)
    return value


def _string_tuple(value: Any, *, field_name: str, at: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str) or not isinstance(value, Iterable):
        raise UnitError("expected an array of strings", field=field_name, at=at)
    items = list(value)
    if any(not isinstance(item, str) or not item for item in items):
        raise UnitError("expected an array of non-empty strings", field=field_name, at=at)
    return tuple(items)


@dataclass(frozen=True, slots=True)
class SourceRef:
    """UKIP Part 01 — the content-addressed citation of where a unit was read.

    ``locator`` is provider-relative and opaque to the platform (a repository-relative
    path, a registry id, a URL, a conversation turn); ``revision`` pins *which*
    version of that locator was read; ``content_sha256`` is the digest of the exact
    bytes or payload observed. Together they make every registered record traceable
    to a reproducible observation.
    """

    provider_id: str
    kind: ProviderKind
    locator: str
    revision: str = ""
    content_sha256: str = ""
    excerpt: str = ""

    def __post_init__(self) -> None:
        _require_text(self.provider_id, field_name="provider_id", at="source")
        _require_text(self.locator, field_name="locator", at=self.provider_id)
        if not isinstance(self.kind, ProviderKind):
            raise UnitError("source kind must be a ProviderKind", at=self.provider_id)

    @property
    def citation(self) -> str:
        """A single stable, human-readable citation string."""
        if self.revision:
            return f"{self.provider_id}:{self.locator}@{self.revision}"
        return f"{self.provider_id}:{self.locator}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "kind": self.kind.value,
            "locator": self.locator,
            "revision": self.revision,
            "content_sha256": self.content_sha256,
            "excerpt": self.excerpt,
        }

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> SourceRef:
        if not isinstance(record, Mapping):
            raise UnitError("source reference must be an object")
        provider_id = _require_text(
            record.get("provider_id"), field_name="provider_id", at="source"
        )
        return cls(
            provider_id=provider_id,
            kind=ProviderKind.coerce(record.get("kind"), context=provider_id),
            locator=_require_text(record.get("locator"), field_name="locator", at=provider_id),
            revision=_optional_text(record.get("revision"), field_name="revision", at=provider_id),
            content_sha256=_optional_text(
                record.get("content_sha256"), field_name="content_sha256", at=provider_id
            ),
            excerpt=_optional_text(record.get("excerpt"), field_name="excerpt", at=provider_id),
        )


@dataclass(frozen=True, slots=True)
class RelationDeclaration:
    """UKIP Part 01 — a provider's claim that its unit relates to something else.

    ``target`` is resolved late (at registration) so a provider may cite either a
    peer unit key it also emitted, an existing canonical id, or a derived
    ``UKID-*`` identifier. Unresolvable targets are reported, never silently dropped.

    ``validity`` is the interval over which the claim holds, in the canonical
    :class:`~engine.temporal.coordinate.ValidityPeriod` (UCKP-ART-07 temporal
    validity, P4-F-002). ``None`` means timeless, which is the prior behaviour and
    stays the default: a provider that never mentions time gets exactly today's
    single-assertion-per-triple semantics.
    """

    relation: RelationType
    target: str
    note: str = ""
    validity: ValidityPeriod | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.relation, RelationType):
            raise UnitError("relation must be a RelationType", at=self.target or "relation")
        _require_text(self.target, field_name="target", at="relation")

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation": self.relation.value,
            "target": self.target,
            "note": self.note,
            "validity": None if self.validity is None else self.validity.to_dict(),
        }

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> RelationDeclaration:
        if not isinstance(record, Mapping):
            raise UnitError("relation declaration must be an object")
        if record.get("validity") is not None:
            # engine/temporal (CMG-000002) declares no ValidityPeriod.from_dict — a
            # raw-record round trip would have to invent one, which is that owner's
            # capability to add, not this module's. Referred, not repaired (P4-F-007
            # companion gap): construct the declaration in code with a real
            # ValidityPeriod instead of through this wire format until it exists.
            raise UnitError(
                "relation declaration validity cannot be rehydrated from a raw record "
                "(engine.temporal.coordinate has no ValidityPeriod.from_dict yet); "
                "construct RelationDeclaration(validity=...) directly",
                at="relation.validity",
            )
        return cls(
            relation=RelationType.coerce(record.get("relation"), context="relation"),
            target=_require_text(record.get("target"), field_name="target", at="relation"),
            note=_optional_text(record.get("note"), field_name="note", at="relation"),
        )


@dataclass(frozen=True, slots=True)
class KnowledgeUnit:
    """UKIP Part 01 — a provider-emitted candidate unit of knowledge.

    A unit is a *claim*, not yet canonical knowledge: it becomes canonical only when
    the Knowledge Registry admits it (or attaches it as corroboration to knowledge
    that already has a canonical home). ``key`` is provider-local and only has to be
    unique within the emitting provider; canonical identity is *derived* from content
    by :meth:`knowledge_id`, never asserted by the provider.
    """

    key: str
    title: str
    statement: str
    source: SourceRef
    rationale: str = ""
    kind: KnowledgeKind | None = None
    authority: KnowledgeAuthority | None = None
    lifecycle: Lifecycle | None = None
    universe: str = ""
    owner: str = ""
    version: str = ""
    tags: tuple[str, ...] = ()
    relations: tuple[RelationDeclaration, ...] = ()
    attributes: tuple[tuple[str, str], ...] = field(default=())

    def __post_init__(self) -> None:
        _require_text(self.key, field_name="key", at="unit")
        _require_text(self.title, field_name="title", at=self.key)
        _require_text(self.statement, field_name="statement", at=self.key)
        if not isinstance(self.source, SourceRef):
            raise UnitError("unit source must be a SourceRef", at=self.key)
        for attribute in self.attributes:
            if len(attribute) != 2 or not all(isinstance(part, str) for part in attribute):
                raise UnitError("attributes must be (name, value) string pairs", at=self.key)

    # -- construction ----------------------------------------------------------

    @classmethod
    def create(
        cls,
        *,
        key: str,
        title: str,
        statement: str,
        source: SourceRef,
        attributes: Mapping[str, str] | None = None,
        **rest: Any,
    ) -> KnowledgeUnit:
        """Build a unit, accepting ``attributes`` as a mapping for ergonomics."""
        pairs = tuple(sorted((str(k), str(v)) for k, v in (attributes or {}).items()))
        return cls(
            key=key, title=title, statement=statement, source=source, attributes=pairs, **rest
        )

    def with_relations(self, relations: Iterable[RelationDeclaration]) -> KnowledgeUnit:
        """Return a copy carrying ``relations`` (de-duplicated, stably ordered)."""
        merged: dict[tuple[str, str], RelationDeclaration] = {}
        for declaration in (*self.relations, *relations):
            merged.setdefault((declaration.relation.value, declaration.target), declaration)
        ordered = tuple(merged[k] for k in sorted(merged))
        return replace(self, relations=ordered)

    def with_classification(
        self,
        *,
        kind: KnowledgeKind,
        authority: KnowledgeAuthority,
        lifecycle: Lifecycle,
        universe: str,
        owner: str,
        version: str,
    ) -> KnowledgeUnit:
        """Return a copy with the classification decision applied."""
        return replace(
            self,
            kind=kind,
            authority=authority,
            lifecycle=lifecycle,
            universe=universe,
            owner=owner,
            version=version,
        )

    # -- attributes ------------------------------------------------------------

    def attribute(self, name: str, default: str = "") -> str:
        """Return a provider-supplied classification signal, or ``default``."""
        for key, value in self.attributes:
            if key == name:
                return value
        return default

    def attribute_map(self) -> dict[str, str]:
        """The provider-supplied signals as an ordered mapping."""
        return dict(self.attributes)

    # -- identity --------------------------------------------------------------

    def knowledge_core(self) -> dict[str, Any]:
        """The substance of the knowledge, and nothing else.

        Field-for-field identical to
        :meth:`engine.knowledge.cko.CanonicalKnowledgeObject.semantic_hash`'s payload
        so a unit and the canonical object authored from it share one identity. An
        unclassified unit hashes with an empty ``kind``, which is why classification
        runs *before* registration in the assimilation pipeline.
        """
        return {
            "kind": self.kind.value if self.kind is not None else "",
            "statement": self.statement.strip().lower(),
            "rationale": self.rationale.strip().lower(),
        }

    def knowledge_sha256(self) -> str:
        """The identity under which duplication is judged (the Knowledge Once key)."""
        return content_hash(self.knowledge_core())

    def knowledge_id(self) -> str:
        """The deterministic canonical identifier derived from the knowledge itself.

        Content-derived rather than provider-asserted: two providers that observe the
        same knowledge independently compute the same identifier, which is what lets
        the registry recognise corroboration instead of manufacturing a duplicate.
        """
        digest = self.knowledge_sha256()[:KNOWLEDGE_ID_DIGEST_LEN].upper()
        return f"{KNOWLEDGE_ID_PREFIX}-{digest}"

    def unit_core(self) -> dict[str, Any]:
        """The whole contribution, including its source (integrity + attribution)."""
        return {
            "key": self.key,
            "title": self.title,
            "statement": self.statement,
            "rationale": self.rationale,
            "kind": self.kind.value if self.kind is not None else None,
            "authority": self.authority.value if self.authority is not None else None,
            "lifecycle": self.lifecycle.value if self.lifecycle is not None else None,
            "universe": self.universe,
            "owner": self.owner,
            "version": self.version,
            "tags": list(self.tags),
            "relations": [r.to_dict() for r in self.relations],
            "attributes": [list(pair) for pair in self.attributes],
            "source": self.source.to_dict(),
        }

    def unit_sha256(self) -> str:
        """SHA-256 of the entire contribution (used for provenance and evidence)."""
        return content_hash(self.unit_core())

    @property
    def is_classified(self) -> bool:
        """True iff every classification facet has been decided."""
        return None not in (self.kind, self.authority, self.lifecycle) and bool(
            self.universe and self.owner and self.version
        )

    # -- serialization ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        payload = self.unit_core()
        payload["knowledge_id"] = self.knowledge_id()
        payload["knowledge_sha256"] = self.knowledge_sha256()
        payload["unit_sha256"] = self.unit_sha256()
        return payload

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> KnowledgeUnit:
        """Parse a unit from an external provider payload, failing loudly."""
        if not isinstance(record, Mapping):
            raise UnitError("knowledge unit must be an object")
        key = _require_text(record.get("key"), field_name="key", at="unit")
        source_raw = record.get("source")
        if not isinstance(source_raw, Mapping):
            raise UnitError("knowledge unit requires a source object", at=key)
        relations_raw = record.get("relations") or []
        if isinstance(relations_raw, Mapping) or not isinstance(relations_raw, Iterable):
            raise UnitError("relations must be an array", at=key)
        attributes_raw = record.get("attributes") or {}
        if not isinstance(attributes_raw, Mapping):
            raise UnitError("attributes must be an object", at=key)
        kind = record.get("kind")
        authority = record.get("authority")
        lifecycle = record.get("lifecycle")
        return cls(
            key=key,
            title=_require_text(record.get("title"), field_name="title", at=key),
            statement=_require_text(record.get("statement"), field_name="statement", at=key),
            source=SourceRef.from_dict(source_raw),
            rationale=_optional_text(record.get("rationale"), field_name="rationale", at=key),
            kind=KnowledgeKind.coerce(kind, context=key) if kind else None,
            authority=KnowledgeAuthority.coerce(authority, context=key) if authority else None,
            lifecycle=Lifecycle.coerce(lifecycle, context=key) if lifecycle else None,
            universe=_optional_text(record.get("universe"), field_name="universe", at=key),
            owner=_optional_text(record.get("owner"), field_name="owner", at=key),
            version=_optional_text(record.get("version"), field_name="version", at=key),
            tags=_string_tuple(record.get("tags"), field_name="tags", at=key),
            relations=tuple(RelationDeclaration.from_dict(r) for r in relations_raw),
            attributes=tuple(sorted((str(k), str(v)) for k, v in attributes_raw.items())),
        )


def unit_document(units: Iterable[KnowledgeUnit]) -> dict[str, Any]:
    """Wrap units in the deterministic UKIP envelope (stable order, no wall-clock)."""
    ordered = sorted(units, key=lambda u: (u.source.provider_id, u.key))
    return {
        "schema": UNIT_SCHEMA,
        "version": UNIT_SCHEMA_VERSION,
        "count": len(ordered),
        "units": [u.to_dict() for u in ordered],
    }


__all__ = [
    "UNIT_SCHEMA",
    "UNIT_SCHEMA_VERSION",
    "KNOWLEDGE_ID_PREFIX",
    "KNOWLEDGE_ID_DIGEST_LEN",
    "ProviderKind",
    "SourceRef",
    "RelationDeclaration",
    "KnowledgeUnit",
    "normalize_text",
    "unit_document",
    "canonical_json",
    "content_hash",
]
