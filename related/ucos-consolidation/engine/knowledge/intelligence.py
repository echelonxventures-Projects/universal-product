"""UKDA Part 04/09 — Institutional Memory Engine + Repository Intelligence.

The query surface that makes the Knowledge Once Principle operational: no
architectural question is answered twice, every previous decision is searchable,
and every implementation can locate the knowledge that governs it.

    * :class:`KnowledgeIntelligence` — a read-only analytical facade over a
      :class:`~engine.knowledge.store.KnowledgeBase`. It provides deterministic
      full-text/keyword search, dependency and reverse-dependency search, transitive
      impact analysis, and the discovery primitives (duplicate, conflict, orphan,
      missing-knowledge, coverage, consistency) that the Validation Layer (Part 10)
      escalates into gates.

Search is a pure, deterministic ranking over tokenised object text — no wall-clock,
no external index, standard library only (TP-04/TP-05) — so identical bases yield
identical results.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.graph import KnowledgeGraph
from engine.knowledge.model import KnowledgeKind
from engine.knowledge.store import KnowledgeBase

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Lower-case alphanumeric tokenisation, splitting camelCase and separators."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    return _TOKEN.findall(spaced.lower())


def subject_terms(*texts: str) -> tuple[str, ...]:
    """The sorted, de-duplicated searchable terms of free text.

    Uses the same tokenisation as :meth:`KnowledgeIntelligence.search`, so a caller can
    build a query from an object's *subject* fields (title, statement, tags) without
    also picking up its structural metadata (identifier, kind, universe). Those
    structural fields are what a query should be matched *against*, never with: an
    identifier contributes no subject matter, and matching on it manufactures
    similarity out of bookkeeping.
    """
    return tuple(sorted({term for text in texts for term in _tokenize(text)}))


@dataclass(frozen=True, slots=True)
class SearchHit:
    """A single ranked search result over the canonical knowledge base."""

    cko_id: str
    title: str
    kind: str
    score: int
    matched: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "cko_id": self.cko_id,
            "title": self.title,
            "kind": self.kind,
            "score": self.score,
            "matched": list(self.matched),
        }


@dataclass(frozen=True, slots=True)
class DuplicateFinding:
    """Two or more canonical objects that express identical knowledge."""

    semantic_sha256: str
    cko_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"semantic_sha256": self.semantic_sha256, "cko_ids": list(self.cko_ids)}


@dataclass(frozen=True, slots=True)
class ConflictFinding:
    """A pair of active objects declared to conflict, or a broken supersession."""

    left: str
    right: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"left": self.left, "right": self.right, "reason": self.reason}


@dataclass(frozen=True, slots=True)
class CoverageReport:
    """A deterministic coverage/consistency snapshot of the knowledge base."""

    total_objects: int
    total_decisions: int
    by_kind: dict[str, int]
    by_authority: dict[str, int]
    by_lifecycle: dict[str, int]
    objects_missing_rationale: tuple[str, ...]
    objects_missing_owner: tuple[str, ...]
    orphans: tuple[str, ...]
    undocumented_decisions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_objects": self.total_objects,
            "total_decisions": self.total_decisions,
            "by_kind": dict(self.by_kind),
            "by_authority": dict(self.by_authority),
            "by_lifecycle": dict(self.by_lifecycle),
            "objects_missing_rationale": list(self.objects_missing_rationale),
            "objects_missing_owner": list(self.objects_missing_owner),
            "orphans": list(self.orphans),
            "undocumented_decisions": list(self.undocumented_decisions),
        }


# Kinds that are legitimately standalone roots and are never "orphans" even with
# no inbound/outbound edges (a constitution root governs by existing).
_ROOT_KINDS: frozenset[KnowledgeKind] = frozenset(
    {KnowledgeKind.PRINCIPLE, KnowledgeKind.CONSTRAINT, KnowledgeKind.POLICY}
)


class KnowledgeIntelligence:
    """Read-only analytical facade over the canonical knowledge base (Part 09)."""

    __slots__ = ("_base", "_graph")

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._graph: KnowledgeGraph = base.graph()

    @property
    def base(self) -> KnowledgeBase:
        return self._base

    @property
    def graph(self) -> KnowledgeGraph:
        return self._graph

    # -- searchable text -------------------------------------------------------

    @staticmethod
    def _document_tokens(obj: CanonicalKnowledgeObject) -> list[str]:
        parts = [
            obj.cko_id,
            obj.title,
            obj.statement,
            obj.rationale,
            obj.kind.value,
            obj.universe,
            *obj.tags,
        ]
        tokens: list[str] = []
        for part in parts:
            tokens.extend(_tokenize(part))
        return tokens

    def document_terms(self, obj: CanonicalKnowledgeObject) -> tuple[str, ...]:
        """The sorted, de-duplicated searchable terms of one object (public projection).

        Reuses the exact tokenisation the ranked search uses, so a generated search
        index can never diverge from what :meth:`search` actually matches.
        """
        return tuple(sorted(set(self._document_tokens(obj))))

    # -- search (Part 04/09) ---------------------------------------------------

    def search(self, query: str, *, limit: int = 20) -> tuple[SearchHit, ...]:
        """Deterministic keyword search ranked by matched-term frequency."""
        terms = _tokenize(query)
        if not terms:
            return ()
        term_set = set(terms)
        hits: list[SearchHit] = []
        for obj in self._base.objects():
            tokens = self._document_tokens(obj)
            token_set = set(tokens)
            matched = sorted(term_set & token_set)
            if not matched:
                continue
            score = sum(tokens.count(term) for term in matched)
            # Authority weighting: more authoritative knowledge ranks higher.
            score += 4 - obj.authority.rank
            hits.append(
                SearchHit(
                    cko_id=obj.cko_id,
                    title=obj.title,
                    kind=obj.kind.value,
                    score=score,
                    matched=tuple(matched),
                )
            )
        hits.sort(key=lambda h: (-h.score, h.cko_id))
        return tuple(hits[:limit])

    def search_decisions(self, query: str) -> tuple[str, ...]:
        """Return decision ids whose recorded text matches every ``query`` term."""
        terms = set(_tokenize(query))
        if not terms:
            return ()
        found: list[str] = []
        for dec in self._base.decisions():
            haystack = " ".join(
                [
                    dec.decision_id,
                    dec.title,
                    dec.problem_statement,
                    dec.context,
                    dec.objective,
                    dec.chosen_architecture,
                    dec.rationale,
                ]
            )
            if terms <= set(_tokenize(haystack)):
                found.append(dec.decision_id)
        return tuple(sorted(found))

    # -- dependency / impact search (Part 09) ----------------------------------

    def dependencies_of(self, cko_id: str) -> tuple[str, ...]:
        return self._graph.dependencies_of(cko_id)

    def dependents_of(self, cko_id: str) -> tuple[str, ...]:
        """Reverse-dependency search: direct dependents of ``cko_id``."""
        return self._graph.dependents_of(cko_id)

    def impact_analysis(self, cko_id: str) -> tuple[str, ...]:
        """Transitive impact: every object affected if ``cko_id`` changes."""
        return self._graph.impact_of(cko_id)

    # -- discovery (Part 09) ---------------------------------------------------

    def find_duplicates(self) -> tuple[DuplicateFinding, ...]:
        """Objects expressing identical knowledge under different ids (Knowledge Once)."""
        by_hash: dict[str, list[str]] = {}
        for obj in self._base.objects():
            by_hash.setdefault(obj.semantic_hash(), []).append(obj.cko_id)
        findings = [
            DuplicateFinding(semantic_sha256=h, cko_ids=tuple(sorted(ids)))
            for h, ids in by_hash.items()
            if len(ids) > 1
        ]
        findings.sort(key=lambda f: f.semantic_sha256)
        return tuple(findings)

    def find_conflicts(self) -> tuple[ConflictFinding, ...]:
        """Active objects that declare a conflict, or contradictory supersession."""
        findings: list[ConflictFinding] = []
        seen: set[tuple[str, str]] = set()
        for obj in self._base.objects():
            for other in self._graph.conflicts_of(obj.cko_id):
                pair = tuple(sorted((obj.cko_id, other)))
                if pair in seen:
                    continue
                seen.add(pair)
                left, right = pair
                left_obj = self._base.get_object(left)
                right_obj = self._base.get_object(right)
                if left_obj and right_obj and left_obj.is_active and right_obj.is_active:
                    findings.append(
                        ConflictFinding(left, right, "both objects active and declared conflicting")
                    )
        # A superseded object that is still marked active is a lifecycle conflict.
        for obj in self._base.objects():
            if obj.superseded_by and obj.is_active:
                findings.append(
                    ConflictFinding(
                        obj.cko_id,
                        obj.superseded_by,
                        "object is superseded yet still active",
                    )
                )
        findings.sort(key=lambda f: (f.left, f.right, f.reason))
        return tuple(findings)

    def find_orphans(self) -> tuple[str, ...]:
        """Non-root objects with no inbound or outbound relationships."""
        orphans = [
            obj.cko_id
            for obj in self._base.objects()
            if obj.kind not in _ROOT_KINDS and self._graph.degree(obj.cko_id) == 0
        ]
        return tuple(sorted(orphans))

    def find_broken_references(self) -> tuple[tuple[str, str], ...]:
        """(source, missing_target) pairs where a link points to an absent object."""
        known = set(self._base.object_ids())
        known_decisions = set(self._base.decision_ids())
        broken: list[tuple[str, str]] = []
        for obj in self._base.objects():
            for ref in obj.all_links():
                if ref not in known:
                    broken.append((obj.cko_id, ref))
            for ref in obj.decision_links:
                if ref not in known_decisions:
                    broken.append((obj.cko_id, ref))
        return tuple(sorted(set(broken)))

    def find_undocumented_decisions(self) -> tuple[str, ...]:
        """DECISION-kind objects that do not link a recorded :class:`DecisionRecord`."""
        known_decisions = set(self._base.decision_ids())
        undocumented = [
            obj.cko_id
            for obj in self._base.by_kind(KnowledgeKind.DECISION)
            if not (set(obj.decision_links) & known_decisions)
        ]
        return tuple(sorted(undocumented))

    def coverage(self) -> CoverageReport:
        """A deterministic coverage/consistency snapshot (Part 09)."""
        objects = self._base.objects()
        by_kind: dict[str, int] = {}
        by_authority: dict[str, int] = {}
        by_lifecycle: dict[str, int] = {}
        for obj in objects:
            by_kind[obj.kind.value] = by_kind.get(obj.kind.value, 0) + 1
            by_authority[obj.authority.value] = by_authority.get(obj.authority.value, 0) + 1
            by_lifecycle[obj.lifecycle.value] = by_lifecycle.get(obj.lifecycle.value, 0) + 1
        missing_rationale = tuple(
            o.cko_id
            for o in objects
            if o.kind in (KnowledgeKind.DECISION, KnowledgeKind.RULE) and not o.rationale
        )
        missing_owner = tuple(o.cko_id for o in objects if not o.owner or o.owner == "UNASSIGNED")
        return CoverageReport(
            total_objects=len(objects),
            total_decisions=len(self._base.decisions()),
            by_kind=dict(sorted(by_kind.items())),
            by_authority=dict(sorted(by_authority.items())),
            by_lifecycle=dict(sorted(by_lifecycle.items())),
            objects_missing_rationale=missing_rationale,
            objects_missing_owner=missing_owner,
            orphans=self.find_orphans(),
            undocumented_decisions=self.find_undocumented_decisions(),
        )


def build_intelligence(base: KnowledgeBase) -> KnowledgeIntelligence:
    """Convenience constructor mirroring the other engine layers."""
    return KnowledgeIntelligence(base)


__all__ = [
    "SearchHit",
    "DuplicateFinding",
    "ConflictFinding",
    "CoverageReport",
    "KnowledgeIntelligence",
    "build_intelligence",
]
