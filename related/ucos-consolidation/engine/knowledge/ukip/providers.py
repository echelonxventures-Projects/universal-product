"""UKIP Part 03 — knowledge providers, unbounded by construction (EPIC-UKDA-003).

The admission surface of the platform. A **provider** is anything that can yield
:class:`~engine.knowledge.ukip.contracts.KnowledgeUnit` values with citable sources:
the canonical store, a decision log, a directory of documents, a registry export, a
runtime probe, an external service, a human.

Unboundedness is structural, not aspirational (UKIP-LAW-001):

    * :class:`KnowledgeProvider` is the *only* thing the rest of the platform knows
      about. The registry, graph, discovery, validation, and certification engines
      never name a concrete provider, so adding one requires no change to them.
    * :class:`ProviderRegistry` holds an arbitrary number of providers, ordered
      deterministically by ``(priority, provider_id)`` rather than by insertion, so
      the assimilation result never depends on registration order.
    * :class:`CallableProvider` adapts any zero-argument callable, so a provider can
      be contributed without defining a class at all.

The built-in providers are conveniences, not privileges: each is implemented purely
through the public protocol and could live outside this module unchanged.

Providers are read-only. They never write to the corpus and never mutate the base
they read from (DP-03), and each is deterministic: the same inputs yield the same
units in the same order (IMP-007 §5).
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord
from engine.knowledge.model import RelationType, content_hash
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.ukip.contracts import (
    KnowledgeUnit,
    ProviderKind,
    RelationDeclaration,
    SourceRef,
    normalize_text,
)
from engine.knowledge.ukip.errors import ProviderConflictError, ProviderError

#: Maximum bytes read from a single document (guards against pathological inputs).
MAX_DOCUMENT_BYTES = 2_000_000

#: Default priority for a provider that does not declare one. Lower runs first, so
#: the canonical store (priority 0) establishes canonical homes before any external
#: provider can, making corroboration the normal outcome for derived sources.
DEFAULT_PRIORITY = 100


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    """The self-description every provider must supply.

    ``priority`` orders providers deterministically; ``authoritative`` marks a
    provider whose units may establish a canonical home on their own authority
    (the canonical store), as opposed to providers that normally corroborate.
    """

    provider_id: str
    kind: ProviderKind
    title: str
    priority: int = DEFAULT_PRIORITY
    authoritative: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        if not self.provider_id or not self.provider_id.strip():
            raise ProviderError("provider_id must be a non-empty string")
        if not isinstance(self.kind, ProviderKind):
            raise ProviderError("provider kind must be a ProviderKind", at=self.provider_id)

    @property
    def order_key(self) -> tuple[int, str]:
        """The deterministic ordering key (never insertion order)."""
        return (self.priority, self.provider_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "kind": self.kind.value,
            "title": self.title,
            "priority": self.priority,
            "authoritative": self.authoritative,
            "description": self.description,
        }


class KnowledgeProvider(ABC):
    """The single contract every knowledge provider implements.

    Two methods, no state requirements, no inheritance from anything in the
    platform's internals — this is what keeps the provider set unbounded.
    """

    @abstractmethod
    def descriptor(self) -> ProviderDescriptor:
        """Return this provider's immutable self-description."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def provide(self) -> tuple[KnowledgeUnit, ...]:
        """Return every unit this provider can currently cite, deterministically."""
        raise NotImplementedError  # pragma: no cover

    # -- helpers available to every implementation -----------------------------

    @property
    def provider_id(self) -> str:
        return self.descriptor().provider_id

    def source(
        self, locator: str, *, revision: str = "", content_sha256: str = "", excerpt: str = ""
    ) -> SourceRef:
        """Build a :class:`SourceRef` bound to this provider's identity and kind."""
        descriptor = self.descriptor()
        return SourceRef(
            provider_id=descriptor.provider_id,
            kind=descriptor.kind,
            locator=locator,
            revision=revision,
            content_sha256=content_sha256,
            excerpt=excerpt,
        )

    def units(self) -> tuple[KnowledgeUnit, ...]:
        """Return :meth:`provide` output after protocol enforcement.

        Wrapping the call here means a misbehaving provider is reported as a provider
        error with its identity attached, rather than corrupting the assimilation of
        every other provider.
        """
        descriptor = self.descriptor()
        try:
            produced = self.provide()
        except ProviderError:
            raise
        except Exception as exc:  # contain third-party provider failures
            raise ProviderError(
                "provider failed while producing knowledge units",
                provider_id=descriptor.provider_id,
                detail=str(exc),
            ) from exc
        if isinstance(produced, str) or not isinstance(produced, Iterable):
            raise ProviderError(
                "provider must return an iterable of knowledge units",
                provider_id=descriptor.provider_id,
            )
        units = tuple(produced)
        seen: set[str] = set()
        for unit in units:
            if not isinstance(unit, KnowledgeUnit):
                raise ProviderError(
                    "provider yielded a non-KnowledgeUnit value",
                    provider_id=descriptor.provider_id,
                )
            if unit.source.provider_id != descriptor.provider_id:
                raise ProviderError(
                    "unit source cites a different provider",
                    provider_id=descriptor.provider_id,
                    unit_source=unit.source.provider_id,
                )
            if unit.key in seen:
                raise ProviderError(
                    "provider yielded a duplicate unit key",
                    provider_id=descriptor.provider_id,
                    key=unit.key,
                )
            seen.add(unit.key)
        return tuple(sorted(units, key=lambda u: u.key))


class ProviderRegistry:
    """An unbounded, deterministically ordered set of knowledge providers.

    The registry imposes no ceiling on provider count and no privileged position for
    any provider. Iteration order is ``(priority, provider_id)``, so the outcome of
    assimilation is a function of the providers themselves, not of the order in which
    somebody happened to add them.
    """

    __slots__ = ("_providers",)

    def __init__(self, providers: Iterable[KnowledgeProvider] = ()) -> None:
        self._providers: dict[str, KnowledgeProvider] = {}
        for provider in providers:
            self.add(provider)

    def add(self, provider: KnowledgeProvider) -> ProviderRegistry:
        """Register a provider, rejecting a colliding provider identity."""
        if not isinstance(provider, KnowledgeProvider):
            raise ProviderError("only KnowledgeProvider instances may be registered")
        descriptor = provider.descriptor()
        existing = self._providers.get(descriptor.provider_id)
        if existing is not None and existing is not provider:
            raise ProviderConflictError(
                "a different provider is already registered under this identity",
                provider_id=descriptor.provider_id,
            )
        self._providers[descriptor.provider_id] = provider
        return self

    def extend(self, providers: Iterable[KnowledgeProvider]) -> ProviderRegistry:
        """Register many providers at once."""
        for provider in providers:
            self.add(provider)
        return self

    def remove(self, provider_id: str) -> ProviderRegistry:
        """Deregister a provider by identity (a no-op if absent)."""
        self._providers.pop(provider_id, None)
        return self

    def get(self, provider_id: str) -> KnowledgeProvider | None:
        return self._providers.get(provider_id)

    def require(self, provider_id: str) -> KnowledgeProvider:
        provider = self._providers.get(provider_id)
        if provider is None:
            raise ProviderError("provider not registered", provider_id=provider_id)
        return provider

    def __len__(self) -> int:
        return len(self._providers)

    def __contains__(self, provider_id: object) -> bool:
        return provider_id in self._providers

    def __iter__(self):
        return iter(self.ordered())

    def ordered(self) -> tuple[KnowledgeProvider, ...]:
        """Providers in deterministic ``(priority, provider_id)`` order."""
        return tuple(sorted(self._providers.values(), key=lambda p: p.descriptor().order_key))

    def provider_ids(self) -> tuple[str, ...]:
        return tuple(p.descriptor().provider_id for p in self.ordered())

    def descriptors(self) -> tuple[ProviderDescriptor, ...]:
        return tuple(p.descriptor() for p in self.ordered())

    def by_kind(self, kind: ProviderKind) -> tuple[KnowledgeProvider, ...]:
        return tuple(p for p in self.ordered() if p.descriptor().kind is kind)

    def authoritative(self) -> tuple[KnowledgeProvider, ...]:
        return tuple(p for p in self.ordered() if p.descriptor().authoritative)

    def collect(self) -> tuple[KnowledgeUnit, ...]:
        """Collect every unit from every provider, in deterministic order."""
        collected: list[KnowledgeUnit] = []
        for provider in self.ordered():
            collected.extend(provider.units())
        return tuple(collected)

    def to_dict(self) -> dict[str, Any]:
        return {
            "count": len(self._providers),
            "providers": [d.to_dict() for d in self.descriptors()],
        }


# ---------------------------------------------------------------------------
# built-in providers — conveniences implemented purely through the protocol
# ---------------------------------------------------------------------------


class CallableProvider(KnowledgeProvider):
    """Adapts any zero-argument callable into a provider.

    The cheapest possible extension point: contributing a provider requires no new
    class, so "unlimited providers" is true for callers who only have a function.
    """

    __slots__ = ("_descriptor", "_supplier")

    def __init__(
        self,
        descriptor: ProviderDescriptor,
        supplier: Callable[[], Iterable[KnowledgeUnit]],
    ) -> None:
        if not callable(supplier):
            raise ProviderError("supplier must be callable", provider_id=descriptor.provider_id)
        self._descriptor = descriptor
        self._supplier = supplier

    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    def provide(self) -> tuple[KnowledgeUnit, ...]:
        return tuple(self._supplier())


class CanonicalStoreProvider(KnowledgeProvider):
    """Projects the canonical UKDA knowledge store as knowledge units.

    The authoritative provider: because it runs first (priority 0), the canonical
    store establishes canonical homes, and every derived provider that later supplies
    the same knowledge is recorded as corroboration (UKIP-LAW-003).
    """

    __slots__ = ("_base", "_provider_id")

    def __init__(self, base: KnowledgeBase, *, provider_id: str = "ukda-canonical-store") -> None:
        self._base = base
        self._provider_id = provider_id

    def descriptor(self) -> ProviderDescriptor:
        return ProviderDescriptor(
            provider_id=self._provider_id,
            kind=ProviderKind.CANONICAL_STORE,
            title="UKDA canonical knowledge store",
            priority=0,
            authoritative=True,
            description="Canonical knowledge objects authored once in knowledge/.",
        )

    @staticmethod
    def _relations(obj: CanonicalKnowledgeObject) -> tuple[RelationDeclaration, ...]:
        declared: list[RelationDeclaration] = []
        if obj.parent:
            declared.append(RelationDeclaration(RelationType.EXTENDS, obj.parent, "cko:parent"))
        for dependency in obj.dependencies:
            declared.append(
                RelationDeclaration(RelationType.DEPENDS_ON, dependency, "cko:dependency")
            )
        for consumer in obj.consumers:
            declared.append(RelationDeclaration(RelationType.CONSUMES, consumer, "cko:consumer"))
        for superseded in obj.supersedes:
            declared.append(
                RelationDeclaration(RelationType.SUPERSEDES, superseded, "cko:supersedes")
            )
        for link in obj.knowledge_links:
            declared.append(
                RelationDeclaration(RelationType.RELATED_TO, link, "cko:knowledge-link")
            )
        for rival in obj.conflicts_with:
            declared.append(RelationDeclaration(RelationType.CONFLICTS_WITH, rival, "cko:conflict"))
        for decision in obj.decision_links:
            declared.append(
                RelationDeclaration(RelationType.REFERENCES, decision, "cko:decision-link")
            )
        return tuple(declared)

    def provide(self) -> tuple[KnowledgeUnit, ...]:
        produced: list[KnowledgeUnit] = []
        for obj in self._base.objects():
            unit = KnowledgeUnit(
                key=obj.cko_id,
                title=obj.title,
                statement=obj.statement,
                rationale=obj.rationale,
                source=self.source(
                    obj.cko_id,
                    revision=obj.version,
                    content_sha256=obj.content_sha256,
                ),
                kind=obj.kind,
                authority=obj.authority,
                lifecycle=obj.lifecycle,
                universe=obj.universe,
                owner=obj.owner,
                version=obj.version,
                tags=obj.tags,
                relations=self._relations(obj),
                attributes=(("cko_id", obj.cko_id),),
            )
            produced.append(unit)
        return tuple(produced)


class DecisionLogProvider(KnowledgeProvider):
    """Projects UKDA decision records as knowledge units.

    Decisions are knowledge with a distinct shape, so they get their own provider
    rather than being folded into the store projection: the unit statement is the
    chosen architecture, and the rationale is the decision's permanent rationale.
    """

    __slots__ = ("_base", "_provider_id")

    def __init__(self, base: KnowledgeBase, *, provider_id: str = "ukda-decision-log") -> None:
        self._base = base
        self._provider_id = provider_id

    def descriptor(self) -> ProviderDescriptor:
        return ProviderDescriptor(
            provider_id=self._provider_id,
            kind=ProviderKind.DECISION_LOG,
            title="UKDA decision records",
            priority=10,
            authoritative=True,
            description="Permanent architectural decision records (UKDA Part 03).",
        )

    @staticmethod
    def _relations(record: DecisionRecord) -> tuple[RelationDeclaration, ...]:
        declared: list[RelationDeclaration] = []
        for dependency in record.dependencies:
            declared.append(
                RelationDeclaration(RelationType.DEPENDS_ON, dependency, "decision:dependency")
            )
        if record.supersedes:
            declared.append(
                RelationDeclaration(
                    RelationType.SUPERSEDES, record.supersedes, "decision:supersedes"
                )
            )
        return tuple(declared)

    def provide(self) -> tuple[KnowledgeUnit, ...]:
        produced: list[KnowledgeUnit] = []
        for record in self._base.decisions():
            produced.append(
                KnowledgeUnit(
                    key=record.decision_id,
                    title=record.title,
                    statement=record.chosen_architecture,
                    rationale=record.rationale,
                    source=self.source(
                        record.decision_id,
                        revision=record.version,
                        content_sha256=record.content_sha256,
                    ),
                    authority=record.authority,
                    lifecycle=record.lifecycle,
                    owner=record.owner,
                    version=record.version,
                    relations=self._relations(record),
                    attributes=(
                        ("decision_id", record.decision_id),
                        ("kind_hint", "decision"),
                        ("reviewable", "true" if record.is_reviewable else "false"),
                    ),
                )
            )
        return tuple(produced)


class MappingProvider(KnowledgeProvider):
    """Provides units parsed from in-memory or JSON-file payloads.

    The general-purpose bridge for any external system that can emit the documented
    unit shape: an integration needs to produce JSON, not Python.
    """

    __slots__ = ("_descriptor", "_records")

    def __init__(
        self,
        descriptor: ProviderDescriptor,
        records: Sequence[Mapping[str, Any]],
    ) -> None:
        self._descriptor = descriptor
        self._records = tuple(records)

    @classmethod
    def from_json_file(
        cls,
        descriptor: ProviderDescriptor,
        path: str | Path,
        *,
        root_key: str = "units",
    ) -> MappingProvider:
        """Load units from a JSON document with a ``{root_key: [...]}`` shape."""
        resolved = Path(path)
        if not resolved.is_file():
            raise ProviderError(
                "provider payload not found",
                provider_id=descriptor.provider_id,
                path=str(resolved),
            )
        try:
            document = json.loads(resolved.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ProviderError(
                "provider payload is not valid JSON",
                provider_id=descriptor.provider_id,
                path=str(resolved),
                detail=str(exc),
            ) from exc
        if not isinstance(document, Mapping):
            raise ProviderError(
                "provider payload root must be an object",
                provider_id=descriptor.provider_id,
            )
        records = document.get(root_key)
        if not isinstance(records, list):
            raise ProviderError(
                "provider payload is missing its units array",
                provider_id=descriptor.provider_id,
                root_key=root_key,
            )
        return cls(descriptor, records)

    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    def provide(self) -> tuple[KnowledgeUnit, ...]:
        produced: list[KnowledgeUnit] = []
        for record in self._records:
            payload = dict(record)
            source = payload.get("source")
            if not isinstance(source, Mapping):
                payload["source"] = {
                    "provider_id": self._descriptor.provider_id,
                    "kind": self._descriptor.kind.value,
                    "locator": str(payload.get("key", "")),
                    "content_sha256": content_hash(payload),
                }
            else:
                merged = dict(source)
                merged.setdefault("provider_id", self._descriptor.provider_id)
                merged.setdefault("kind", self._descriptor.kind.value)
                payload["source"] = merged
            produced.append(KnowledgeUnit.from_dict(payload))
        return tuple(produced)


class DocumentProvider(KnowledgeProvider):
    """Extracts knowledge units from Markdown documents on disk.

    Each ``##``-and-deeper heading becomes one candidate unit whose statement is the
    prose immediately beneath it, cited by ``path#heading`` with the digest of the
    file's bytes as ``revision`` — so a document edit is visible as a provenance
    change rather than silently rewriting knowledge.

    Read-only by construction: the provider opens files and never writes, so it is
    safe to point at any part of the repository, including the frozen corpus (DP-03).
    """

    __slots__ = ("_descriptor", "_root", "_paths")

    def __init__(
        self,
        root: str | Path,
        *,
        provider_id: str = "repository-documents",
        title: str = "Repository Markdown documents",
        priority: int = 200,
        patterns: Sequence[str] = ("*.md",),
    ) -> None:
        self._root = Path(root)
        if not self._root.is_dir():
            raise ProviderError(
                "document provider root is not a directory",
                provider_id=provider_id,
                root=str(self._root),
            )
        self._descriptor = ProviderDescriptor(
            provider_id=provider_id,
            kind=ProviderKind.DOCUMENT,
            title=title,
            priority=priority,
            authoritative=False,
            description=f"Markdown knowledge extracted from {self._root.name}.",
        )
        discovered: list[Path] = []
        for pattern in patterns:
            discovered.extend(sorted(self._root.rglob(pattern)))
        self._paths = tuple(sorted({p for p in discovered if p.is_file()}))

    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    @property
    def document_count(self) -> int:
        return len(self._paths)

    @staticmethod
    def _sections(text: str) -> tuple[tuple[str, str], ...]:
        """Split Markdown into ``(heading, body)`` pairs, deterministically."""
        sections: list[tuple[str, list[str]]] = []
        for raw in text.splitlines():
            line = raw.rstrip()
            stripped = line.lstrip("#")
            level = len(line) - len(stripped)
            if 2 <= level <= 6 and stripped.startswith(" "):
                sections.append((stripped.strip(), []))
            elif sections and line.strip():
                sections[-1][1].append(line.strip())
        return tuple(
            (heading, normalize_text(" ".join(body))) for heading, body in sections if body
        )

    def provide(self) -> tuple[KnowledgeUnit, ...]:
        produced: list[KnowledgeUnit] = []
        for path in self._paths:
            try:
                raw = path.read_bytes()
            except OSError as exc:
                raise ProviderError(
                    "document could not be read",
                    provider_id=self._descriptor.provider_id,
                    path=str(path),
                    detail=str(exc),
                ) from exc
            if len(raw) > MAX_DOCUMENT_BYTES:
                continue
            revision = hashlib.sha256(raw).hexdigest()
            relative = path.relative_to(self._root).as_posix()
            for heading, body in self._sections(raw.decode("utf-8", errors="replace")):
                locator = f"{relative}#{heading}"
                produced.append(
                    KnowledgeUnit(
                        key=locator,
                        title=heading,
                        statement=body,
                        source=self.source(
                            locator,
                            revision=revision,
                            content_sha256=content_hash({"heading": heading, "body": body}),
                            excerpt=body[:200],
                        ),
                        attributes=(
                            ("document", relative),
                            ("heading", heading),
                        ),
                    )
                )
        return tuple(produced)


def default_providers(base: KnowledgeBase) -> tuple[KnowledgeProvider, ...]:
    """The two authoritative providers over the canonical store.

    Deliberately minimal: the platform's default posture is *canonical knowledge
    only* (UKIP-LAW-009). Additional providers are a caller's decision, not a
    default, and the engines behave identically however many are added.
    """
    return (CanonicalStoreProvider(base), DecisionLogProvider(base))


def default_registry(base: KnowledgeBase) -> ProviderRegistry:
    """A registry pre-loaded with :func:`default_providers`."""
    return ProviderRegistry(default_providers(base))


__all__ = [
    "MAX_DOCUMENT_BYTES",
    "DEFAULT_PRIORITY",
    "ProviderDescriptor",
    "KnowledgeProvider",
    "ProviderRegistry",
    "CallableProvider",
    "CanonicalStoreProvider",
    "DecisionLogProvider",
    "MappingProvider",
    "DocumentProvider",
    "default_providers",
    "default_registry",
]
