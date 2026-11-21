"""UKI Deliverable 5 — Knowledge Reuse Engine (EPIC-UKDA-002).

Determines automatically whether an existing capability can be **reused, extended,
or composed** *before* creation is allowed (``UKI-LAW-003``; creation is the last
resort). The determination is deterministic and follows the constitutional order
reuse > extend > compose > create:

    * **reuse**  — identical knowledge already exists (semantic-hash match), or an
      *implemented capability* the repository forbids replacing already covers the
      intent → point at it.
    * **extend** — an implemented capability, or a single existing artifact of the
      same kind and universe, is a specialization target → extend it.
    * **compose** — the intent's declared dependencies already exist and are active
      (>= 2 components) → compose from them.
    * **create** — no existing knowledge suffices; creation is justified.

It reuses the UKDA :class:`~engine.knowledge.intelligence.KnowledgeIntelligence` and
content model verbatim (semantic hashing, search) — no second analysis engine.

Capability awareness (Repository Self-Awareness)
-----------------------------------------------
Semantic-hash reuse only fires on knowledge that is *already authored*, and the
same-kind/same-universe extension path only fires when the caller happens to declare
the same ``kind`` and ``universe`` as the existing object. Neither can recognise
"the repository already implements this", because an implemented capability is a
different *kind* of knowledge than the intent proposing it. The engine was therefore
structurally blind to the repository's own implementation and answered ``CREATE``
for capabilities that demonstrably existed.

:meth:`ReuseEngine._capability_candidates` closes that hole by matching an intent
against the capability facts authored by :mod:`engine.knowledge.capability`,
independently of ``kind`` and ``universe``. Matching is *specificity-weighted*: a
term shared with many capabilities (``knowledge``, ``universal``) carries no signal,
while a rare term (``ukip``, ``substrate``) does — so the engine neither misses a
real owner nor rubber-stamps every intent as reuse.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import log, sqrt
from typing import Any

from engine.knowledge.capability import is_reuse_candidate, replacement_prohibited
from engine.knowledge.integration.contracts import ArtifactIntent, Disposition
from engine.knowledge.intelligence import KnowledgeIntelligence, subject_terms
from engine.knowledge.store import KnowledgeBase

#: Minimum search score for a related object to count as an extension candidate.
_EXTEND_MIN_SCORE = 2
#: Minimum number of resolvable active components required to justify composition.
_COMPOSE_MIN_COMPONENTS = 2

#: Minimum inverse-document-frequency cosine similarity between an intent and a
#: capability before that capability is reported as covering it.
#:
#: Calibrated empirically against the repository's own capability corpus, over ten
#: knowledge-domain intents whose owners were established by evidence and five
#: deliberately off-topic control intents (a cake recipe, a neural network, an SMS
#: gateway, a ray tracer, payroll tax). The floor is set for **recall, deliberately not
#: for precision**: at 0.05 no intent whose capability exists is answered ``CREATE``
#: (0/10 false CREATE), at the cost of one control intent in five attracting a
#: suggestion. Raising it to 0.08 buys precision but reintroduces two false ``CREATE``
#: verdicts, and those are the expensive error: a false ``REUSE`` is a ranked suggestion
#: a reviewer discards in seconds, whereas a false ``CREATE`` is a silent licence to
#: duplicate a capability that already exists — the failure this engine exists to prevent.
_CAPABILITY_MIN_SIMILARITY = 0.05

#: Candidates are reported when they score at least this fraction of the best score. A
#: relative band rather than a second absolute cut-off, because the *spread* of scores is
#: what indicates whether ownership is clear or contested.
_CAPABILITY_SCORE_BAND = 0.5

#: Upper bound on reported capability candidates. Reuse determination is adjudicated by
#: a human or a downstream gate; an unbounded list is not a determination.
_CAPABILITY_MAX_CANDIDATES = 10


def _idf(population: int, frequency: int) -> float:
    """Inverse document frequency of a term over the capability corpus.

    Smoothed so a term absent from the corpus is admissible, and floored at ``1.0`` so a
    term carried by *every* capability still contributes a little. The floor is not
    cosmetic: without it, ``log((N+1)/(N+1)) == 0`` for every term of a single-capability
    corpus, every similarity collapses to zero, and the engine silently goes blind again
    on exactly the small bases used to bootstrap or test it. With the floor, a unique term
    still outweighs a ubiquitous one by roughly five to one on this repository's corpus,
    which is the discrimination the ranking needs.
    """
    return log((population + 1) / (frequency + 1)) + 1.0


@dataclass(frozen=True, slots=True)
class ReuseCandidate:
    """A single existing artifact considered for reuse/extension/composition."""

    cko_id: str
    relation: str
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"cko_id": self.cko_id, "relation": self.relation, "score": self.score}


@dataclass(frozen=True, slots=True)
class ReuseAssessment:
    """The deterministic reuse determination for an intent (Deliverable 5)."""

    disposition: Disposition
    targets: tuple[str, ...]
    candidates: tuple[ReuseCandidate, ...]
    reasons: tuple[str, ...]

    @property
    def requires_creation(self) -> bool:
        return self.disposition is Disposition.CREATE

    def to_dict(self) -> dict[str, Any]:
        return {
            "disposition": self.disposition.value,
            "targets": list(self.targets),
            "candidates": [c.to_dict() for c in self.candidates],
            "reasons": list(self.reasons),
            "requires_creation": self.requires_creation,
        }


class ReuseEngine:
    """Determines reuse/extend/compose/create for an intent (Deliverable 5)."""

    __slots__ = ("_base", "_intel")

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._intel = KnowledgeIntelligence(base)

    def _semantic_reuse(self, intent: ArtifactIntent) -> tuple[str, ...]:
        target = intent.semantic_hash()
        return tuple(
            sorted(
                obj.cko_id
                for obj in self._base.objects()
                if obj.cko_id != intent.intent_id
                and obj.is_active
                and obj.semantic_hash() == target
            )
        )

    @staticmethod
    def _intent_terms(intent: ArtifactIntent) -> frozenset[str]:
        """The intent's subject vocabulary, excluding its structural metadata.

        Deliberately not ``document_terms(intent.to_cko())``: that also tokenises the
        intent's identifier, ``kind`` and ``universe``, and those terms are *rare* across
        the capability corpus, so they carry high inverse-document-frequency weight while
        carrying no subject matter. Including them made an intent declared as a
        ``pattern`` score against whichever capabilities happen to discuss patterns.
        """
        return frozenset(
            subject_terms(intent.title, intent.statement, intent.rationale, *intent.tags)
        )

    def _capability_terms(self) -> tuple[dict[str, frozenset[str]], Counter[str]]:
        """Searchable terms of every active capability, plus their document frequency.

        Frequency is measured over the capability corpus only, so specificity is judged
        against the population the question is asked of ("which capability owns this?")
        rather than against all knowledge.
        """
        terms: dict[str, frozenset[str]] = {}
        frequency: Counter[str] = Counter()
        for obj in self._base.objects():
            if not is_reuse_candidate(obj):
                continue
            document = frozenset(self._intel.document_terms(obj))
            terms[obj.cko_id] = document
            frequency.update(document)
        return terms, frequency

    @staticmethod
    def _similarity(
        query: frozenset[str],
        document: frozenset[str],
        idf: dict[str, float],
    ) -> float:
        """Cosine similarity of two term sets under inverse-document-frequency weights.

        Cosine rather than weighted overlap, because overlap rewards *verbosity*: a
        capability with a long description shares more rare terms with everything and
        would win every comparison regardless of subject. Normalising by both vector
        magnitudes removes that bias, so similarity measures topical agreement rather
        than document length.
        """
        shared = query & document
        if not shared:
            return 0.0
        numerator = sum(idf[term] ** 2 for term in shared)
        query_norm = sqrt(sum(idf[term] ** 2 for term in query))
        document_norm = sqrt(sum(idf[term] ** 2 for term in document))
        if query_norm == 0.0 or document_norm == 0.0:
            return 0.0
        return numerator / (query_norm * document_norm)

    def _capability_candidates(self, intent: ArtifactIntent) -> tuple[ReuseCandidate, ...]:
        """Implemented capabilities that already cover ``intent``, strongest first.

        Independent of ``kind`` and ``universe``: a capability fact and the intent
        proposing that capability are necessarily different kinds of knowledge, so
        requiring them to agree is what made the engine blind.

        Only candidates at or above :data:`_CAPABILITY_MIN_SIMILARITY` are returned, and
        every one of them is reported. The engine deliberately does **not** collapse the
        list to a single "the" owner: lexical evidence can establish that existing
        capabilities cover a subject, but it cannot by itself prove which one is the
        canonical owner, and asserting a single owner on that evidence would fabricate a
        determination. Ranked candidates are the honest output; the caller adjudicates.
        """
        terms, frequency = self._capability_terms()
        if not terms:
            return ()
        population = len(terms)
        query = self._intent_terms(intent)
        vocabulary = query | frozenset().union(*terms.values())
        idf = {term: _idf(population, frequency[term]) for term in vocabulary}
        scored: list[tuple[float, str]] = []
        for cko_id, document in terms.items():
            if cko_id == intent.intent_id:
                continue
            score = self._similarity(query, document, idf)
            if score > 0.0:
                scored.append((score, cko_id))
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        if not scored or scored[0][0] < _CAPABILITY_MIN_SIMILARITY:
            return ()
        cutoff = scored[0][0] * _CAPABILITY_SCORE_BAND
        return tuple(
            ReuseCandidate(
                cko_id=cko_id, relation="implemented-capability", score=round(score * 1000)
            )
            for score, cko_id in scored[:_CAPABILITY_MAX_CANDIDATES]
            if score >= cutoff
        )

    def _nearest_capabilities(self, intent: ArtifactIntent) -> tuple[ReuseCandidate, ...]:
        """The closest capabilities regardless of the confidence floor.

        Attached to a ``CREATE`` verdict so creation can never be authorised without the
        reader seeing what the repository already implements. A verdict of "nothing
        suffices" is only trustworthy alongside the evidence it was reached from.
        """
        terms, frequency = self._capability_terms()
        if not terms:
            return ()
        population = len(terms)
        query = self._intent_terms(intent)
        vocabulary = query | frozenset().union(*terms.values())
        idf = {term: _idf(population, frequency[term]) for term in vocabulary}
        scored = sorted(
            (
                (self._similarity(query, document, idf), cko_id)
                for cko_id, document in terms.items()
                if cko_id != intent.intent_id
            ),
            key=lambda pair: (-pair[0], pair[1]),
        )
        return tuple(
            ReuseCandidate(cko_id=cko_id, relation="nearest-capability", score=round(score * 1000))
            for score, cko_id in scored[:_CAPABILITY_MAX_CANDIDATES]
            if score > 0.0
        )

    def _extension_candidates(self, intent: ArtifactIntent) -> tuple[ReuseCandidate, ...]:
        query = " ".join((intent.title, intent.statement, *intent.tags))
        candidates: list[ReuseCandidate] = []
        for hit in self._intel.search(query):
            if hit.cko_id == intent.intent_id:
                continue
            obj = self._base.get_object(hit.cko_id)
            if obj is None or not obj.is_active:
                continue
            if obj.kind is intent.kind and obj.universe == intent.universe:
                candidates.append(
                    ReuseCandidate(
                        cko_id=hit.cko_id, relation="same-kind-universe", score=hit.score
                    )
                )
        return tuple(candidates)

    def _composition_components(self, intent: ArtifactIntent) -> tuple[str, ...]:
        components = [
            ref
            for ref in intent.dependencies
            if (obj := self._base.get_object(ref)) is not None and obj.is_active
        ]
        return tuple(sorted(set(components)))

    def assess(self, intent: ArtifactIntent) -> ReuseAssessment:
        """Return the constitutional reuse determination for ``intent`` (deterministic)."""
        # 1. reuse — identical knowledge already exists.
        reuse_targets = self._semantic_reuse(intent)
        if reuse_targets:
            candidates = tuple(
                ReuseCandidate(cko_id=cid, relation="semantic", score=100) for cid in reuse_targets
            )
            return ReuseAssessment(
                disposition=Disposition.REUSE,
                targets=reuse_targets,
                candidates=candidates,
                reasons=("identical knowledge already exists (semantic-hash match)",),
            )

        # 2. reuse/extend — implemented capabilities already cover the intent.
        #    Placed before the generic extension path because an *implemented* capability
        #    is stronger evidence than a same-kind neighbour, and before creation because
        #    a capability whose replacement is prohibited may never be re-created.
        capabilities = self._capability_candidates(intent)
        if capabilities:
            strongest = self._base.require_object(capabilities[0].cko_id)
            location = (
                strongest.documentation_links[0]
                if strongest.documentation_links
                else capabilities[0].cko_id
            )
            prohibited = tuple(
                candidate.cko_id
                for candidate in capabilities
                if (obj := self._base.get_object(candidate.cko_id)) is not None
                and replacement_prohibited(obj)
            )
            evidence = (
                f"{len(capabilities)} implemented capability/ies already cover this intent; "
                f"the strongest candidate is '{strongest.title}' at '{location}'"
            )
            if prohibited:
                return ReuseAssessment(
                    disposition=Disposition.REUSE,
                    targets=prohibited,
                    candidates=capabilities,
                    reasons=(
                        evidence,
                        f"{len(prohibited)} of them forbid replacement, so creation is "
                        "refused and the canonical owner must be adjudicated from these "
                        "candidates",
                    ),
                )
            return ReuseAssessment(
                disposition=Disposition.EXTEND,
                targets=tuple(candidate.cko_id for candidate in capabilities),
                candidates=capabilities,
                reasons=(evidence, "none forbid replacement, so extension is permitted"),
            )

        # 3. extend — a single same-kind/same-universe specialization target.
        extension = self._extension_candidates(intent)
        strong = tuple(c for c in extension if c.score >= _EXTEND_MIN_SCORE)
        if strong:
            top = strong[0]
            return ReuseAssessment(
                disposition=Disposition.EXTEND,
                targets=(top.cko_id,),
                candidates=extension,
                reasons=(
                    f"existing {intent.kind.value} '{top.cko_id}' in universe "
                    f"'{intent.universe}' can be extended",
                ),
            )

        # 4. compose — the declared dependencies already exist and are active.
        components = self._composition_components(intent)
        if len(components) >= _COMPOSE_MIN_COMPONENTS:
            return ReuseAssessment(
                disposition=Disposition.COMPOSE,
                targets=components,
                candidates=tuple(
                    ReuseCandidate(cko_id=cid, relation="component", score=50) for cid in components
                ),
                reasons=(f"{len(components)} existing active components can be composed",),
            )

        # 5. create — no existing knowledge suffices.
        #    The nearest capabilities are attached even though none cleared the
        #    confidence floor, so a CREATE verdict is auditable: the reader sees what the
        #    repository already implements and can overrule a false negative. A bare
        #    "nothing found" is the verdict that let duplication happen.
        nearest = self._nearest_capabilities(intent)
        reasons = ["no reusable, extensible, or composable knowledge found"]
        if nearest:
            reasons.append(
                f"{len(nearest)} implemented capability/ies are related but scored below the "
                "reuse confidence floor; review them before creating"
            )
        return ReuseAssessment(
            disposition=Disposition.CREATE,
            targets=(),
            candidates=(*extension, *nearest),
            reasons=tuple(reasons),
        )


__all__ = ["ReuseCandidate", "ReuseAssessment", "ReuseEngine"]
