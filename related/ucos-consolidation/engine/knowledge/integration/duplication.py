"""UKI Deliverable 6 — Duplicate Prevention Engine (EPIC-UKDA-002).

Automatically detects — and **fails closed** on — the duplication modes the
constitution forbids (``UKI-LAW-004``), for a proposed
:class:`~engine.knowledge.integration.contracts.ArtifactIntent`:

    * **duplicate-identity**       — the canonical id already exists (on a create);
    * **semantic-duplicate**       — identical knowledge exists under another id;
    * **overlapping-ownership**    — identical knowledge is owned by a different owner;
    * **conflicting-capability**   — an active artifact claims the same name/universe
      with different substance;
    * **redundant-universe**       — a new universe that normalizes to an existing one;
    * **parallel-implementation**  — a near-identical active artifact of the same kind
      and universe under a different id.

Screening reuses the UKDA content model (semantic hashing) verbatim. ``require``
raises :class:`~engine.knowledge.integration.errors.DuplicationViolationError` on any
violation so no creation path can proceed past a detected duplicate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from engine.knowledge.integration.contracts import ArtifactIntent, Operation
from engine.knowledge.integration.errors import DuplicationViolationError
from engine.knowledge.store import KnowledgeBase

_TOKEN = re.compile(r"[a-z0-9]+")

#: Statement token-set similarity at/above which two same-kind artifacts are a
#: parallel implementation of one another (deterministic Jaccard threshold).
_PARALLEL_SIMILARITY = 0.85


def _normalize_universe(name: str) -> str:
    """Collapse a universe name to its identity (case/separator-insensitive)."""
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def _word_set(text: str) -> frozenset[str]:
    return frozenset(_TOKEN.findall(text.lower()))


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


@dataclass(frozen=True, slots=True)
class DuplicationViolation:
    """A single detected duplication violation (fail-closed)."""

    kind: str
    offenders: tuple[str, ...]
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "offenders": list(self.offenders), "message": self.message}


@dataclass(frozen=True, slots=True)
class DuplicationReport:
    """The aggregate duplication screening for one intent (Deliverable 6)."""

    intent_id: str
    violations: tuple[DuplicationViolation, ...]

    @property
    def clean(self) -> bool:
        return not self.violations

    def kinds(self) -> tuple[str, ...]:
        return tuple(v.kind for v in self.violations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "clean": self.clean,
            "violations": [v.to_dict() for v in self.violations],
        }


class DuplicatePreventionEngine:
    """Detects forbidden duplication modes for an intent, fail-closed (Deliverable 6)."""

    __slots__ = ("_base",)

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base

    def screen(self, intent: ArtifactIntent) -> DuplicationReport:
        """Return every duplication violation for ``intent`` (non-raising)."""
        violations: list[DuplicationViolation] = []
        existing = self._base.get_object(intent.intent_id)

        # duplicate-identity: creating over an existing id.
        if intent.operation is Operation.CREATE and existing is not None:
            violations.append(
                DuplicationViolation(
                    "duplicate-identity",
                    (intent.intent_id,),
                    "canonical id already exists; a create would duplicate identity",
                )
            )

        # semantic-duplicate / overlapping-ownership.
        target_hash = intent.semantic_hash()
        semantic_twins = tuple(
            sorted(
                obj.cko_id
                for obj in self._base.objects()
                if obj.cko_id != intent.intent_id and obj.semantic_hash() == target_hash
            )
        )
        if semantic_twins:
            violations.append(
                DuplicationViolation(
                    "semantic-duplicate",
                    semantic_twins,
                    "identical knowledge already exists under another canonical id",
                )
            )
            foreign_owners = sorted(
                {
                    obj.owner
                    for cid in semantic_twins
                    if (obj := self._base.get_object(cid)) is not None and obj.owner != intent.owner
                }
            )
            if foreign_owners:
                violations.append(
                    DuplicationViolation(
                        "overlapping-ownership",
                        tuple(foreign_owners),
                        "identical knowledge is already owned by a different owner",
                    )
                )

        # conflicting-capability / parallel-implementation.
        intent_norm_title = _normalize_universe(intent.title)
        intent_words = _word_set(intent.statement)
        conflicting: list[str] = []
        parallel: list[str] = []
        for obj in self._base.objects():
            if obj.cko_id == intent.intent_id or not obj.is_active:
                continue
            same_slot = obj.universe == intent.universe
            if same_slot and _normalize_universe(obj.title) == intent_norm_title:
                if obj.semantic_hash() != target_hash:
                    conflicting.append(obj.cko_id)
            if same_slot and obj.kind is intent.kind and obj.cko_id not in semantic_twins:
                if _jaccard(intent_words, _word_set(obj.statement)) >= _PARALLEL_SIMILARITY:
                    parallel.append(obj.cko_id)
        if conflicting:
            violations.append(
                DuplicationViolation(
                    "conflicting-capability",
                    tuple(sorted(set(conflicting))),
                    "an active artifact claims the same name and universe with different substance",
                )
            )
        if parallel:
            violations.append(
                DuplicationViolation(
                    "parallel-implementation",
                    tuple(sorted(set(parallel))),
                    "a near-identical active artifact of the same kind and universe already exists",
                )
            )

        # redundant-universe: a new universe that normalizes to an existing one.
        known_universes = {obj.universe for obj in self._base.objects()}
        if intent.universe not in known_universes:
            norm = _normalize_universe(intent.universe)
            redundant = sorted(u for u in known_universes if _normalize_universe(u) == norm)
            if redundant:
                violations.append(
                    DuplicationViolation(
                        "redundant-universe",
                        tuple(redundant),
                        "the intent introduces a universe equivalent to an existing one",
                    )
                )

        return DuplicationReport(intent_id=intent.intent_id, violations=tuple(violations))

    def require(self, intent: ArtifactIntent) -> DuplicationReport:
        """Screen ``intent`` and raise on any violation (fail-closed)."""
        report = self.screen(intent)
        if not report.clean:
            raise DuplicationViolationError(
                "duplicate prevention engine rejected the intent",
                intent_id=intent.intent_id,
                violations=list(report.kinds()),
            )
        return report


__all__ = [
    "DuplicationViolation",
    "DuplicationReport",
    "DuplicatePreventionEngine",
]
