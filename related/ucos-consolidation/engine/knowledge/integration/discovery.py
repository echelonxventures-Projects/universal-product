"""UKI Deliverable 2 — Knowledge Discovery Protocol (EPIC-UKDA-002).

Specifies the **deterministic discovery** that is mandatory before creation,
implementation, validation, certification, and governance (``UKI-LAW-002``). Before
anything is created, the corpus is consulted: does this exact identity exist? Does
identical knowledge already exist under another id? What existing knowledge is
related, and which constitutional/architectural authorities govern it?

    * :class:`DiscoveryResult` — the immutable, deterministic answer for one intent
      in one :class:`~engine.knowledge.integration.contracts.DiscoveryPhase`.
    * :class:`DiscoveryProtocol` — a read-only facade over the UKDA
      :class:`~engine.knowledge.intelligence.KnowledgeIntelligence` (reused verbatim);
      it adds no second search engine.

Discovery is pure and reproducible: identical bases and intents yield identical
results (IMP-007 §5).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.integration.contracts import ArtifactIntent, DiscoveryPhase
from engine.knowledge.intelligence import KnowledgeIntelligence, SearchHit
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind
from engine.knowledge.store import KnowledgeBase

# Kinds that carry governing authority over other artifacts in a universe.
_GOVERNING_KINDS: frozenset[KnowledgeKind] = frozenset(
    {
        KnowledgeKind.PRINCIPLE,
        KnowledgeKind.POLICY,
        KnowledgeKind.CONSTRAINT,
        KnowledgeKind.STANDARD,
        KnowledgeKind.RULE,
    }
)

# Authorities that constitute "governing" (advisory does not govern).
_GOVERNING_AUTHORITY: frozenset[KnowledgeAuthority] = frozenset(
    {KnowledgeAuthority.CONSTITUTIONAL, KnowledgeAuthority.ARCHITECTURAL}
)


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    """The deterministic outcome of a mandatory discovery pass (Deliverable 2)."""

    phase: DiscoveryPhase
    query: str
    exact_match: str | None
    semantic_matches: tuple[str, ...]
    related: tuple[SearchHit, ...]
    governing: tuple[str, ...]
    decision_matches: tuple[str, ...]

    @property
    def found_existing(self) -> bool:
        """True iff discovery located an exact or semantic match to the intent."""
        return self.exact_match is not None or bool(self.semantic_matches)

    def related_ids(self) -> tuple[str, ...]:
        return tuple(hit.cko_id for hit in self.related)

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase.value,
            "query": self.query,
            "exact_match": self.exact_match,
            "semantic_matches": list(self.semantic_matches),
            "related": [hit.to_dict() for hit in self.related],
            "governing": list(self.governing),
            "decision_matches": list(self.decision_matches),
            "found_existing": self.found_existing,
        }


class DiscoveryProtocol:
    """Runs mandatory, deterministic discovery over the canonical base (Deliverable 2)."""

    __slots__ = ("_base", "_intel")

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._intel = KnowledgeIntelligence(base)

    @property
    def intelligence(self) -> KnowledgeIntelligence:
        return self._intel

    def _query_for(self, intent: ArtifactIntent) -> str:
        return " ".join((intent.title, intent.statement, *intent.tags))

    def _semantic_matches(self, intent: ArtifactIntent) -> tuple[str, ...]:
        target = intent.semantic_hash()
        return tuple(
            sorted(
                obj.cko_id
                for obj in self._base.objects()
                if obj.cko_id != intent.intent_id and obj.semantic_hash() == target
            )
        )

    def _governing(self, intent: ArtifactIntent) -> tuple[str, ...]:
        governing = [
            obj.cko_id
            for obj in self._base.by_universe(intent.universe)
            if obj.cko_id != intent.intent_id
            and obj.is_active
            and obj.kind in _GOVERNING_KINDS
            and obj.authority in _GOVERNING_AUTHORITY
        ]
        return tuple(sorted(governing))

    def discover(
        self,
        intent: ArtifactIntent,
        *,
        phase: DiscoveryPhase = DiscoveryPhase.CREATION,
        limit: int = 20,
    ) -> DiscoveryResult:
        """Consult constitutional knowledge for ``intent`` in a given ``phase``."""
        query = self._query_for(intent)
        related = tuple(
            hit for hit in self._intel.search(query, limit=limit) if hit.cko_id != intent.intent_id
        )
        return DiscoveryResult(
            phase=phase,
            query=query,
            exact_match=intent.intent_id if self._base.has_object(intent.intent_id) else None,
            semantic_matches=self._semantic_matches(intent),
            related=related,
            governing=self._governing(intent),
            decision_matches=self._intel.search_decisions(query),
        )


__all__ = ["DiscoveryResult", "DiscoveryProtocol"]
