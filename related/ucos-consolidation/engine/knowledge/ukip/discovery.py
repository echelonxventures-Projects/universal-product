"""UKIP Part 09 — Knowledge Discovery (EPIC-UKDA-003).

Everything registered must be findable, by every address anyone might hold
(UKIP-LAW-007). Knowledge that cannot be discovered cannot be reused, and knowledge
that cannot be reused gets re-authored — which is how duplication happens in the
first place. Discovery is therefore a duplication-prevention mechanism, not a
convenience.

Five addressing modes, all deterministic:

    * by canonical identifier, provider-local address, or content digest
      (:meth:`KnowledgeDiscovery.locate`);
    * by classification facet (kind / authority / lifecycle / universe / owner);
    * by provider;
    * by ranked keyword search (:meth:`KnowledgeDiscovery.search`);
    * by relationship neighbourhood (:meth:`KnowledgeDiscovery.related`).

:meth:`KnowledgeDiscovery.discover_before_create` is the gate that closes the loop:
before knowledge is authored, it answers whether an equivalent record already exists —
exactly (same content digest), semantically (high term overlap), or nearby (same
classification and owner) — and returns a verdict of ``reuse``, ``extend``, or
``create``. A caller that skips it and creates duplicate knowledge is detectable,
because the registry would have reported corroboration instead.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    content_hash,
)
from engine.knowledge.ukip.contracts import KnowledgeUnit
from engine.knowledge.ukip.errors import DiscoveryBypassError
from engine.knowledge.ukip.registry import KnowledgeRegistry, RegisteredKnowledge

_TOKEN = re.compile(r"[a-z0-9]+")

#: Term-overlap ratio at or above which two pieces of knowledge are treated as
#: semantically the same thing for reuse purposes.
SEMANTIC_REUSE_THRESHOLD = 0.72

#: Overlap ratio at or above which knowledge is a candidate for extension rather
#: than independent creation.
SEMANTIC_EXTEND_THRESHOLD = 0.45


def tokenize(text: str) -> tuple[str, ...]:
    """Lowercase alphanumeric tokenisation, shared by every discovery path."""
    return tuple(_TOKEN.findall(text.lower()))


class Verdict(str, Enum):
    """The determination a discover-before-create query returns."""

    REUSE = "reuse"
    EXTEND = "extend"
    CREATE = "create"


@dataclass(frozen=True, slots=True)
class DiscoveryHit:
    """One ranked discovery result."""

    knowledge_id: str
    title: str
    kind: str
    authority: str
    score: int
    matched: tuple[str, ...] = ()
    provider_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "title": self.title,
            "kind": self.kind,
            "authority": self.authority,
            "score": self.score,
            "matched": list(self.matched),
            "provider_ids": list(self.provider_ids),
        }


@dataclass(frozen=True, slots=True)
class ReuseCandidate:
    """An existing record that could serve instead of authoring new knowledge."""

    knowledge_id: str
    title: str
    overlap: float
    exact: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "title": self.title,
            "overlap": round(self.overlap, 4),
            "exact": self.exact,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class DiscoveryAnswer:
    """The determination returned before knowledge is created."""

    verdict: Verdict
    query: str
    candidates: tuple[ReuseCandidate, ...] = ()
    searched: int = 0

    @property
    def must_reuse(self) -> bool:
        return self.verdict is Verdict.REUSE

    @property
    def may_create(self) -> bool:
        return self.verdict is Verdict.CREATE

    @property
    def best(self) -> ReuseCandidate | None:
        return self.candidates[0] if self.candidates else None

    def require_create_allowed(self) -> None:
        """Raise if creation would duplicate existing knowledge (fail closed)."""
        if self.verdict is Verdict.REUSE:
            best = self.best
            raise DiscoveryBypassError(
                "equivalent canonical knowledge already exists; reuse it",
                query=self.query,
                existing=best.knowledge_id if best else "",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "query": self.query,
            "searched": self.searched,
            "candidates": [c.to_dict() for c in self.candidates],
        }


@dataclass(frozen=True, slots=True)
class CoverageReport:
    """A deterministic discoverability snapshot of the registry."""

    total_records: int
    total_providers: int
    by_kind: dict[str, int]
    by_authority: dict[str, int]
    by_lifecycle: dict[str, int]
    by_universe: dict[str, int]
    by_provider: dict[str, int]
    undiscoverable: tuple[str, ...] = ()
    single_sourced: tuple[str, ...] = ()

    @property
    def is_fully_discoverable(self) -> bool:
        return not self.undiscoverable

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_records": self.total_records,
            "total_providers": self.total_providers,
            "by_kind": self.by_kind,
            "by_authority": self.by_authority,
            "by_lifecycle": self.by_lifecycle,
            "by_universe": self.by_universe,
            "by_provider": self.by_provider,
            "undiscoverable": list(self.undiscoverable),
            "single_sourced": list(self.single_sourced),
            "fully_discoverable": self.is_fully_discoverable,
        }


class KnowledgeDiscovery:
    """The read-only discovery facade over the Knowledge Registry (UKIP Part 09)."""

    __slots__ = ("_registry", "_terms", "_aliases")

    def __init__(self, registry: KnowledgeRegistry) -> None:
        self._registry = registry
        self._terms: dict[str, tuple[str, ...]] = {
            record.knowledge_id: tokenize(record.searchable_text()) for record in registry.records()
        }
        self._aliases = registry.reference_map()

    @property
    def registry(self) -> KnowledgeRegistry:
        return self._registry

    def terms_of(self, knowledge_id: str) -> tuple[str, ...]:
        """The exact terms :meth:`search` matches, so an index cannot diverge."""
        return self._terms.get(knowledge_id, ())

    # -- addressing ------------------------------------------------------------

    def locate(self, reference: str) -> RegisteredKnowledge | None:
        """Resolve any address form to a record: id, provider:key, key, or digest.

        THE BARE PROVIDER-LOCAL KEY WAS AN ADDRESS THIS METHOD REFUSED. ``reference_map``
        admits it while it stays unambiguous — that is what lets a provider cite a peer by
        the peer's own key — and :meth:`addresses_of` therefore REPORTED it, under a
        docstring promising every address it returns resolves. ``KnowledgeRegistry.resolve``
        consults only the ``provider:key`` index, so the bare form resolved in relationship
        resolution and not here: one address, two answers, and the discoverability check
        (:meth:`is_discoverable`) could never see the disagreement because it addresses by
        identifier. The alias map this object already holds is consulted as the last step,
        so every address discovery advertises is an address discovery answers to.
        """
        direct = self._registry.resolve(reference)
        if direct is not None:
            return direct
        alias = self._aliases.get(reference)
        return self._registry.get(alias) if alias else None

    def addresses_of(self, knowledge_id: str) -> tuple[str, ...]:
        """Every address that resolves to this record."""
        return tuple(
            sorted(alias for alias, target in self._aliases.items() if target == knowledge_id)
        )

    def is_discoverable(self, knowledge_id: str) -> bool:
        """True iff the record answers to its identifier, its digest, and a search."""
        record = self._registry.get(knowledge_id)
        if record is None:
            return False
        by_id = self.locate(knowledge_id) is not None
        by_digest = self._registry.by_content_hash(record.knowledge_sha256) is not None
        by_search = any(hit.knowledge_id == knowledge_id for hit in self.search(record.title))
        return by_id and by_digest and by_search

    # -- classification / provider addressing ----------------------------------

    def by_kind(self, kind: KnowledgeKind) -> tuple[RegisteredKnowledge, ...]:
        return self._registry.by_kind(kind)

    def by_authority(self, authority: KnowledgeAuthority) -> tuple[RegisteredKnowledge, ...]:
        return self._registry.by_authority(authority)

    def by_lifecycle(self, lifecycle: Lifecycle) -> tuple[RegisteredKnowledge, ...]:
        return self._registry.by_lifecycle(lifecycle)

    def by_universe(self, universe: str) -> tuple[RegisteredKnowledge, ...]:
        return self._registry.by_universe(universe)

    def by_owner(self, owner: str) -> tuple[RegisteredKnowledge, ...]:
        return self._registry.by_owner(owner)

    def by_provider(self, provider_id: str) -> tuple[RegisteredKnowledge, ...]:
        return self._registry.by_provider(provider_id)

    # -- ranked search ---------------------------------------------------------

    def search(self, query: str, *, limit: int = 20) -> tuple[DiscoveryHit, ...]:
        """Deterministic keyword search ranked by term frequency then authority.

        Ties break on identifier, so an identical registry always returns an identical
        ordering (IMP-007 §5).
        """
        terms = tokenize(query)
        if not terms:
            return ()
        wanted = set(terms)
        hits: list[DiscoveryHit] = []
        for record in self._registry.records():
            tokens = self._terms.get(record.knowledge_id, ())
            matched = sorted(wanted & set(tokens))
            if not matched:
                continue
            score = sum(tokens.count(term) for term in matched)
            score += 4 - record.authority.rank
            score += len(record.provider_ids) - 1  # corroborated knowledge ranks higher
            hits.append(
                DiscoveryHit(
                    knowledge_id=record.knowledge_id,
                    title=record.title,
                    kind=record.kind.value,
                    authority=record.authority.value,
                    score=score,
                    matched=tuple(matched),
                    provider_ids=record.provider_ids,
                )
            )
        hits.sort(key=lambda h: (-h.score, h.knowledge_id))
        return tuple(hits[:limit])

    # -- relationship neighbourhood -------------------------------------------

    def related(self, knowledge_id: str) -> tuple[str, ...]:
        """Records this one declares a relationship to (resolved to canonical ids)."""
        record = self._registry.get(knowledge_id)
        if record is None:
            return ()
        resolved = record.resolved_relations(self._aliases)
        return tuple(sorted({r.target for r in resolved if r.target in self._registry}))

    # -- discover before create ------------------------------------------------

    def _overlap(self, left: Iterable[str], right: Iterable[str]) -> float:
        """Jaccard overlap of two term sets (0.0 when either side is empty)."""
        a, b = set(left), set(right)
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def discover_before_create(
        self,
        statement: str,
        *,
        title: str = "",
        rationale: str = "",
        kind: KnowledgeKind | None = None,
        limit: int = 5,
    ) -> DiscoveryAnswer:
        """Determine whether knowledge must be reused, may extend, or may be created.

        An exact content-digest match is decisive: it means the knowledge is already
        homed, so authoring it again is precisely the duplication the platform exists
        to prevent. Below that, term overlap distinguishes extension from creation.
        """
        probe = tokenize(" ".join([title, statement, rationale]))
        candidates: list[ReuseCandidate] = []

        exact_home: RegisteredKnowledge | None = None
        if kind is not None:
            digest = content_hash(
                {
                    "kind": kind.value,
                    "statement": statement.strip().lower(),
                    "rationale": rationale.strip().lower(),
                }
            )
            exact_home = self._registry.by_content_hash(digest)
            if exact_home is not None:
                candidates.append(
                    ReuseCandidate(
                        knowledge_id=exact_home.knowledge_id,
                        title=exact_home.title,
                        overlap=1.0,
                        exact=True,
                        reason="identical knowledge is already homed (content digest match)",
                    )
                )

        for record in self._registry.records():
            if exact_home is not None and record.knowledge_id == exact_home.knowledge_id:
                continue
            overlap = self._overlap(probe, self._terms.get(record.knowledge_id, ()))
            if overlap < SEMANTIC_EXTEND_THRESHOLD:
                continue
            reason = (
                "semantically equivalent to existing knowledge"
                if overlap >= SEMANTIC_REUSE_THRESHOLD
                else "closely related; extend or link instead of duplicating"
            )
            candidates.append(
                ReuseCandidate(
                    knowledge_id=record.knowledge_id,
                    title=record.title,
                    overlap=overlap,
                    exact=False,
                    reason=reason,
                )
            )

        candidates.sort(key=lambda c: (not c.exact, -c.overlap, c.knowledge_id))
        trimmed = tuple(candidates[:limit])
        if trimmed and (trimmed[0].exact or trimmed[0].overlap >= SEMANTIC_REUSE_THRESHOLD):
            verdict = Verdict.REUSE
        elif trimmed:
            verdict = Verdict.EXTEND
        else:
            verdict = Verdict.CREATE
        return DiscoveryAnswer(
            verdict=verdict,
            query=title or statement,
            candidates=trimmed,
            searched=len(self._terms),
        )

    def screen_unit(self, unit: KnowledgeUnit, *, limit: int = 5) -> DiscoveryAnswer:
        """Run discover-before-create for a provider unit before it is submitted."""
        return self.discover_before_create(
            unit.statement,
            title=unit.title,
            rationale=unit.rationale,
            kind=unit.kind,
            limit=limit,
        )

    # -- coverage --------------------------------------------------------------

    def coverage(self) -> CoverageReport:
        """A deterministic discoverability snapshot."""
        records = self._registry.records()
        by_kind: dict[str, int] = {}
        by_authority: dict[str, int] = {}
        by_lifecycle: dict[str, int] = {}
        by_universe: dict[str, int] = {}
        by_provider: dict[str, int] = {}
        undiscoverable: list[str] = []
        single_sourced: list[str] = []
        for record in records:
            by_kind[record.kind.value] = by_kind.get(record.kind.value, 0) + 1
            by_authority[record.authority.value] = by_authority.get(record.authority.value, 0) + 1
            by_lifecycle[record.lifecycle.value] = by_lifecycle.get(record.lifecycle.value, 0) + 1
            by_universe[record.universe] = by_universe.get(record.universe, 0) + 1
            for provider_id in record.provider_ids:
                by_provider[provider_id] = by_provider.get(provider_id, 0) + 1
            if not self.is_discoverable(record.knowledge_id):
                undiscoverable.append(record.knowledge_id)
            if not record.is_multi_sourced:
                single_sourced.append(record.knowledge_id)
        return CoverageReport(
            total_records=len(records),
            total_providers=len(self._registry.provider_ids()),
            by_kind=dict(sorted(by_kind.items())),
            by_authority=dict(sorted(by_authority.items())),
            by_lifecycle=dict(sorted(by_lifecycle.items())),
            by_universe=dict(sorted(by_universe.items())),
            by_provider=dict(sorted(by_provider.items())),
            undiscoverable=tuple(undiscoverable),
            single_sourced=tuple(single_sourced),
        )


def build_discovery(registry: KnowledgeRegistry) -> KnowledgeDiscovery:
    """Convenience constructor mirroring the other UKIP layers."""
    return KnowledgeDiscovery(registry)


__all__ = [
    "SEMANTIC_REUSE_THRESHOLD",
    "SEMANTIC_EXTEND_THRESHOLD",
    "tokenize",
    "Verdict",
    "DiscoveryHit",
    "ReuseCandidate",
    "DiscoveryAnswer",
    "CoverageReport",
    "KnowledgeDiscovery",
    "build_discovery",
]
