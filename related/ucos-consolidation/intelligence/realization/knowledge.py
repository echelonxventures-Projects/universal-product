"""URI-000001 — canonical knowledge intake: the only input the pipeline trusts.

Everything URI generates is derived here and nowhere else. The intake:

1. loads the UKDA canonical knowledge store (``knowledge/canonical-knowledge.json`` +
   ``knowledge/decisions.json``), falling back to the authored-once seed base when the
   store has not yet been written;
2. **re-verifies** the content hash of every canonical object and decision — a mutated
   record fails intake rather than silently propagating into generated artifacts;
3. projects the Universal Knowledge Graph and derives one
   :class:`~intelligence.realization.contracts.RealizationTarget` per knowledge
   universe, reading membership, layers, and invariants out of the store;
4. computes the **knowledge seal**: a single content hash over the whole intake state.
   Identical canonical knowledge ⇒ identical seal ⇒ byte-identical realization.

The intake never writes. URI has no authority to author knowledge (UCKO-PRIN-0001):
knowledge absent from the store is reported as a coverage gap, never invented.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord
from engine.knowledge.errors import KnowledgeError
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind
from engine.knowledge.seed import build_seed_base
from engine.knowledge.store import KnowledgeBase, KnowledgeStore
from intelligence.realization.canonical import content_hash
from intelligence.realization.contracts import (
    Invariant,
    RealizationTarget,
    dedupe,
)
from intelligence.realization.errors import KnowledgeIntakeError

#: Kinds whose statements are normative — they become runtime invariants and are the
#: obligations the Test Generator turns into executable assertions.
NORMATIVE_KINDS: frozenset[KnowledgeKind] = frozenset(
    {
        KnowledgeKind.PRINCIPLE,
        KnowledgeKind.RULE,
        KnowledgeKind.CONSTRAINT,
        KnowledgeKind.POLICY,
        KnowledgeKind.STANDARD,
        KnowledgeKind.CONVENTION,
    }
)

#: Kinds that carry realization obligations at all. Descriptive kinds (example,
#: reference, evidence) are realized as documentation only, never as invariants.
REALIZABLE_KINDS: frozenset[KnowledgeKind] = frozenset(
    {
        KnowledgeKind.PRINCIPLE,
        KnowledgeKind.RULE,
        KnowledgeKind.CONSTRAINT,
        KnowledgeKind.POLICY,
        KnowledgeKind.STANDARD,
        KnowledgeKind.CONVENTION,
        KnowledgeKind.PATTERN,
        KnowledgeKind.ANTI_PATTERN,
        KnowledgeKind.DECISION,
        KnowledgeKind.FACT,
        KnowledgeKind.GUIDELINE,
        KnowledgeKind.BEST_PRACTICE,
    }
)


def _statements(
    objects: Sequence[CanonicalKnowledgeObject], kind: KnowledgeKind
) -> tuple[str, ...]:
    return tuple(o.cko_id for o in objects if o.kind is kind)


@dataclass(frozen=True, slots=True)
class KnowledgeIntake:
    """A sealed, integrity-verified projection of canonical knowledge.

    Constructed only through :meth:`load` or :meth:`from_base` so the integrity
    verification can never be bypassed.
    """

    base: KnowledgeBase
    source: str
    targets: tuple[RealizationTarget, ...]
    knowledge_seal: str
    integrity: tuple[Mapping[str, Any], ...]

    # -- construction ---------------------------------------------------------

    @classmethod
    def load(cls, knowledge_dir: Path | str | None = None) -> KnowledgeIntake:
        """Load the canonical store, or the authored-once seed base when absent."""
        try:
            store = KnowledgeStore(knowledge_dir)
            if store.exists():
                return cls.from_base(store.load(), source=str(store.directory))
            return cls.from_base(build_seed_base(), source="engine.knowledge.seed")
        except KnowledgeError as exc:
            raise KnowledgeIntakeError(
                "canonical knowledge could not be loaded",
                detail=exc.message,
                code_from=exc.code,
            ) from exc

    @classmethod
    def from_base(cls, base: KnowledgeBase, *, source: str) -> KnowledgeIntake:
        """Verify, project, and seal an in-memory canonical knowledge base."""
        if not base.objects():
            raise KnowledgeIntakeError(
                "canonical knowledge store contains no objects; nothing to realize",
                source=source,
            )
        integrity = _verify_integrity(base)
        failures = [record for record in integrity if not record["verified"]]
        if failures:
            raise KnowledgeIntakeError(
                "canonical knowledge failed integrity verification",
                source=source,
                failed=[record["id"] for record in failures],
            )
        targets = _derive_targets(base)
        seal = content_hash(
            {
                "objects": [o.to_dict() for o in base.objects()],
                "decisions": [d.to_dict() for d in base.decisions()],
                "targets": [t.to_dict() for t in targets],
            }
        )
        return cls(
            base=base,
            source=source,
            targets=targets,
            knowledge_seal=seal,
            integrity=tuple(integrity),
        )

    # -- accessors ------------------------------------------------------------

    def object_ids(self) -> tuple[str, ...]:
        return self.base.object_ids()

    def decision_ids(self) -> tuple[str, ...]:
        return self.base.decision_ids()

    def objects_for(self, target: RealizationTarget) -> tuple[CanonicalKnowledgeObject, ...]:
        return tuple(self.base.require_object(cko_id) for cko_id in target.cko_ids)

    def decisions_for(self, target: RealizationTarget) -> tuple[DecisionRecord, ...]:
        return tuple(self.base.require_decision(did) for did in target.decision_ids)

    def target(self, target_id: str) -> RealizationTarget:
        for candidate in self.targets:
            if candidate.target_id == target_id:
                return candidate
        raise KnowledgeIntakeError("unknown realization target", target_id=target_id)

    def realizable_ids(self) -> tuple[str, ...]:
        """Canonical objects that carry a realization obligation."""
        return dedupe(o.cko_id for o in self.base.objects() if o.kind in REALIZABLE_KINDS)

    def semantic_index(self) -> dict[str, tuple[str, ...]]:
        """Map semantic hash → cko ids, exposing Knowledge Once Principle violations."""
        index: dict[str, list[str]] = {}
        for obj in self.base.objects():
            index.setdefault(obj.semantic_hash(), []).append(obj.cko_id)
        return {k: tuple(sorted(v)) for k, v in sorted(index.items())}

    def conflict_pairs(self) -> tuple[tuple[str, str], ...]:
        """Every declared ``conflicts_with`` pair, normalized and de-duplicated."""
        pairs: set[tuple[str, str]] = set()
        for obj in self.base.objects():
            for other in obj.conflicts_with:
                pairs.add(tuple(sorted((obj.cko_id, other))))  # type: ignore[arg-type]
        return tuple(sorted(pairs))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "knowledge_seal": self.knowledge_seal,
            "object_count": len(self.base.objects()),
            "decision_count": len(self.base.decisions()),
            "target_count": len(self.targets),
            "targets": [t.to_dict() for t in self.targets],
            "integrity": [dict(record) for record in self.integrity],
            "realizable_ids": list(self.realizable_ids()),
        }


def _verify_integrity(base: KnowledgeBase) -> list[dict[str, Any]]:
    """Re-verify every content-addressed record. Fail-closed input validation."""
    records: list[dict[str, Any]] = []
    for obj in base.objects():
        records.append(
            {
                "id": obj.cko_id,
                "record": "canonical-object",
                "content_sha256": obj.content_sha256,
                "verified": obj.verify_integrity(),
            }
        )
    for dec in base.decisions():
        records.append(
            {
                "id": dec.decision_id,
                "record": "decision",
                "content_sha256": dec.content_sha256,
                "verified": dec.verify_integrity(),
            }
        )
    return sorted(records, key=lambda r: (r["record"], r["id"]))


def _derive_targets(base: KnowledgeBase) -> tuple[RealizationTarget, ...]:
    """Derive one realization target per knowledge universe. Nothing is declared."""
    universes = dedupe(o.universe for o in base.objects())
    graph = base.graph()
    targets: list[RealizationTarget] = []
    for universe in universes:
        objects = sorted(base.by_universe(universe), key=lambda o: o.cko_id)
        members = {o.cko_id for o in objects}
        decision_ids = dedupe(
            link for obj in objects for link in obj.decision_links if base.has_decision(link)
        )
        invariants = tuple(
            Invariant(
                cko_id=obj.cko_id,
                kind=obj.kind.value,
                authority=obj.authority.value,
                statement=obj.statement,
            )
            for obj in objects
            if obj.kind in NORMATIVE_KINDS
        )
        edges = tuple(
            sorted(
                (edge.source, edge.type.value, edge.target)
                for edge in graph.all()
                if edge.source in members and edge.target in members
            )
        )
        targets.append(
            RealizationTarget(
                universe=universe,
                cko_ids=tuple(o.cko_id for o in objects),
                decision_ids=decision_ids,
                kinds=dedupe(o.kind.value for o in objects),
                authorities=tuple(
                    a.value for a in sorted({o.authority for o in objects}, key=lambda a: a.rank)
                ),
                lifecycles=dedupe(o.lifecycle.value for o in objects),
                owners=dedupe(o.owner for o in objects),
                invariants=invariants,
                principles=_statements(objects, KnowledgeKind.PRINCIPLE),
                patterns=_statements(objects, KnowledgeKind.PATTERN),
                conventions=_statements(objects, KnowledgeKind.CONVENTION),
                anti_patterns=_statements(objects, KnowledgeKind.ANTI_PATTERN),
                edges=edges,
            )
        )
    return tuple(targets)


def authority_rank(value: str) -> int:
    """Return the numeric precedence of an authority value (lower = more authoritative)."""
    return KnowledgeAuthority.coerce(value, context="realization").rank


__all__ = [
    "NORMATIVE_KINDS",
    "REALIZABLE_KINDS",
    "KnowledgeIntake",
    "authority_rank",
]
