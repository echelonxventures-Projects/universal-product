"""UCKP — the Universal Constitutional Knowledge Universe, assembled.

Every layer below this module is a part. This module is the whole: the one place that
puts the law, the registry, the graph, the projections, the persistence adapters, the
execution adapters, the constitutional timeline, the evolution ledger, the intelligence
and the governance runtime together and hands back a single value.

Two design choices are worth stating because they are constitutional, not stylistic.

**Nothing is enumerated.** :func:`build_universe` does not contain a list of the
objects in the universe. It calls
:meth:`engine.uckp.registry.UniversalKnowledgeRegistry.discover`, which walks the
package and admits whatever any module offers through the provider hook. Adding a new
family of constitutional objects therefore means adding a provider module — never
editing this one. That is Article 8, and it is the difference between a universe that
discovers itself and a universe someone maintains a list of.

**The assembled universe is immutable.** :class:`ConstitutionalUniverse` is a frozen
value. Evolving the universe means building a successor and appending a state to the
timeline; it never means mutating the object you are holding (Article 12). The
components inside it — the registry, timeline, ledger and governance engine — are
themselves append-only.
"""

from __future__ import annotations

import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from engine.uckp.canonical import content_hash
from engine.uckp.errors import LawViolation
from engine.uckp.evolution import (
    EVOLUTION_CYCLE,
    EVOLUTION_STAGE,
    EvolutionLedger,
    EvolutionRecord,
    evolution_stage_vocabulary,
)
from engine.uckp.execution import (
    ExecutionAdapter,
    ExecutionRequest,
    build_execution_suite,
)
from engine.uckp.governance import GovernanceEngine
from engine.uckp.graph import UniversalKnowledgeGraph
from engine.uckp.intelligence import UniversalIntelligence, build_intelligence
from engine.uckp.law import ROOT_LAW, RootLaw
from engine.uckp.persistence import (
    KNOWN_PERSISTENCE_KINDS,
    PersistenceAdapter,
    build_persistence_suite,
    universe_digest,
)
from engine.uckp.projection import (
    KNOWN_PROJECTION_KINDS,
    ProjectionEngine,
    build_projection_engine,
)
from engine.uckp.registry import DiscoveryReport, UniversalKnowledgeRegistry
from engine.uckp.state import (
    KNOWLEDGE,
    ConstitutionalDelta,
    ConstitutionalState,
    ConstitutionalTimeline,
)
from engine.uckp.ucko import UCKO
from engine.uckp.vocabulary import VocabularyRegistry, build_vocabulary_registry

#: The default discovery root. A root, not a list of modules: what lives under it is
#: discovered, so this constant never grows as the universe does.
DEFAULT_DISCOVERY_ROOTS: tuple[str, ...] = ("engine.uckp",)

#: The actor recorded in the audit trail of states this module creates.
BUILDER_ACTOR = "engine.uckp.universe"


@dataclass(frozen=True, slots=True)
class ConstitutionalUniverse:
    """The assembled Universal Constitutional Knowledge Universe."""

    law: RootLaw
    registry: UniversalKnowledgeRegistry
    projections: ProjectionEngine
    persistence: tuple[PersistenceAdapter, ...]
    execution: tuple[ExecutionAdapter, ...]
    timeline: ConstitutionalTimeline
    evolution: EvolutionLedger
    governance: GovernanceEngine
    discovery: DiscoveryReport
    persistence_base: str = ""
    _graph: list[UniversalKnowledgeGraph] = field(default_factory=list, repr=False)

    # --- knowledge --------------------------------------------------------------

    def objects(self) -> tuple[UCKO, ...]:
        return self.registry.objects()

    def ids(self) -> tuple[str, ...]:
        return self.registry.ids()

    def vocabularies(self) -> VocabularyRegistry:
        return self.registry.vocabularies()

    def graph(self) -> UniversalKnowledgeGraph:
        """The knowledge graph, derived once and cached (derivation is pure)."""
        if not self._graph:
            self._graph.append(self.registry.graph())
        return self._graph[0]

    def intelligence(self) -> UniversalIntelligence:
        return build_intelligence(self.registry)

    # --- identity ---------------------------------------------------------------

    def root_id(self) -> str:
        """The single self-grounding object every authority chain terminates at."""
        return self.registry.require_single_root()

    def seal(self) -> str:
        """The content seal of the whole universe."""
        return self.registry.seal()

    def knowledge_digest(self) -> str:
        return universe_digest(self.objects())

    def fingerprint(self) -> str:
        """A digest over knowledge, law, timeline and evolution together."""
        return content_hash(
            {
                "law": self.law.digest(),
                "knowledge": self.knowledge_digest(),
                "graph": self.graph().fingerprint(),
                "timeline": self.timeline.fingerprint(),
                "evolution": self.evolution.fingerprint(),
            }
        )

    # --- coherence --------------------------------------------------------------

    def require_coherent(self) -> None:
        """Fail closed unless the assembled universe holds together.

        Cheap structural checks only: the law is internally coherent, there is exactly
        one root, no relationship dangles and no authority chain loops. The full
        seventeen-invariant judgement lives in :mod:`engine.uckp.validation`; this is
        the guard that stops an incoherent universe from being handed out at all.
        """
        self.law.require_coherent()
        self.root_id()
        graph = self.graph()
        dangling = graph.dangling()
        if dangling:
            raise LawViolation(
                "relationships point at objects that do not exist",
                count=len(dangling),
                sample=[f"{edge.source} -{edge.relation}-> {edge.target}" for edge in dangling[:5]],
            )
        graph.require_acyclic_authority()
        orphans = graph.orphans(self.root_id())
        if orphans:
            raise LawViolation(
                "objects are unreachable from the root law",
                count=len(orphans),
                sample=list(orphans[:5]),
            )

    # --- description ------------------------------------------------------------

    def describe(self) -> dict[str, object]:
        """The machine-readable self-description of the universe (Article 8)."""
        graph = self.graph()
        return {
            "law_id": self.law.law_id,
            "law_version": self.law.version,
            "law_digest": self.law.digest(),
            "root_id": self.root_id(),
            "seal": self.seal(),
            "fingerprint": self.fingerprint(),
            "counts": {
                "objects": len(self.objects()),
                "edges": len(graph.edges()),
                "articles": len(self.law.articles),
                "invariants": len(self.law.invariants),
                "stop_conditions": len(self.law.stop_conditions),
                "projection_kinds": len(self.projections.kinds()),
                "persistence_adapters": len(self.persistence),
                "execution_adapters": len(self.execution),
                "states": len(self.timeline.states()),
                "evolution_records": len(self.evolution.records()),
                "governance_rules": len(self.governance.rules()),
                "governance_decisions": len(self.governance.decisions()),
                "providers": len(self.discovery.providers_found),
            },
            "providers": list(self.discovery.providers_found),
            "discovery_failures": list(self.discovery.failures),
        }

    def to_document(self) -> dict[str, object]:
        """The full canonical document of the universe — every layer, generated."""
        objects = self.objects()
        return {
            "schema": "ucos-uckp-universe",
            "version": "1.0.0",
            "description": self.describe(),
            "law": self.law.to_dict(),
            "registry": self.registry.to_document(),
            "graph": self.graph().to_document(),
            "projections": self.projections.to_document(objects),
            "persistence": [adapter.describe() for adapter in self.persistence],
            "execution": [adapter.describe() for adapter in self.execution],
            "timeline": self.timeline.to_document(),
            "evolution": self.evolution.to_document(),
            "intelligence": self.intelligence().report(),
            "governance": self.governance.to_document(),
        }


# --- assembly ------------------------------------------------------------------


def _genesis_timeline(objects: Sequence[UCKO]) -> ConstitutionalTimeline:
    """The opening two states: the universe coming into existence, then sealing itself.

    Two states rather than one, because a timeline of length one cannot demonstrate
    the property the timeline exists for. Article 12 is about what happens to a
    *previous* state when a new one is created, and with no previous state there is
    nothing for the append-only rule to be true of.
    """
    ids = tuple(sorted(obj.ucko_id for obj in objects))
    digest = universe_digest(objects)
    genesis = ConstitutionalState.genesis(
        knowledge_digest=digest, knowledge_ids=ids, actor=BUILDER_ACTOR
    )
    ratified = genesis.transition(
        knowledge_digest=digest,
        certification_delta=ConstitutionalDelta("certification", added=(ROOT_LAW.law_id,)),
        knowledge_delta=ConstitutionalDelta(KNOWLEDGE),
        actor=BUILDER_ACTOR,
    )
    return ConstitutionalTimeline((genesis, ratified))


def _opening_evolution(universe_seal: str) -> EvolutionLedger:
    """One complete cycle, plus the first stage of the next.

    The extra record is the point. A ledger that stops at ``continuation`` has merely
    *described* a cycle; a ledger that has already begun observing again has shown that
    the cycle wraps, which is what "evolution never terminates" has to mean if it is to
    be checkable (Article 14, UCKP-INV-13).
    """
    ledger = EvolutionLedger()
    ledger.extend(
        EvolutionRecord(
            cycle=0,
            stage=stage,
            subject="uckp.universe",
            outcome="appended",
            digest=content_hash({"stage": stage.value, "seal": universe_seal}),
            findings=(),
        )
        for stage in EVOLUTION_CYCLE
    )
    first = EVOLUTION_CYCLE[0]
    ledger.append(
        EvolutionRecord(
            cycle=1,
            stage=first,
            subject="uckp.universe",
            outcome="appended",
            digest=content_hash({"stage": first.value, "seal": universe_seal, "cycle": 1}),
            findings=("the cycle wrapped: evolution has no terminal stage",),
        )
    )
    return ledger


def _opening_governance(registry: UniversalKnowledgeRegistry) -> GovernanceEngine:
    """Exercise every governance question once against the root law.

    Recording a decision for each question is what makes the audit trail non-empty and
    the replay property testable on real decisions rather than on a hypothetical one.
    """
    engine = GovernanceEngine(registry)
    root_id = registry.require_single_root()
    root = registry.require(root_id)
    for question in engine.questions():
        if question == "may-transition":
            engine.decide(question, subject=root_id, target="operational")
        elif question == "may-create":
            engine.decide(
                question,
                subject=root_id,
                concept=root.semantic_identity.concept,
                definition=root.semantic_identity.definition,
            )
        else:
            engine.decide(question, subject=root_id)
    return engine


def _contribute_evolution_stage_vocabulary(vocabularies: VocabularyRegistry) -> None:
    """Publish the evolution stage set into the universe's vocabulary registry.

    ``build_vocabulary_registry`` cannot seed this one: it lives below
    :mod:`engine.uckp.evolution` in the layer order, and reaching upward for the cycle
    would invert the dependency. So the evolution layer contributes its own vocabulary
    here, exactly as :mod:`engine.uckp.assimilation` contributes the native ones.

    A caller may pass a registry that already carries it, so an identical registration is
    reused rather than refused; a *different* vocabulary under the same id still fails
    closed, because two competing stage sets under one name is the ambiguity the id exists
    to prevent.
    """
    published = evolution_stage_vocabulary()
    existing = vocabularies.get(EVOLUTION_STAGE)
    if existing is None:
        vocabularies.register(published)
        return
    if existing.digest() != published.digest():
        raise LawViolation(
            "a different evolution stage vocabulary is already registered",
            vocabulary_id=EVOLUTION_STAGE,
        )


def build_universe(
    *,
    roots: Iterable[str] = DEFAULT_DISCOVERY_ROOTS,
    persistence_base: str | Path | None = None,
    additional_objects: Iterable[UCKO] = (),
    vocabularies: VocabularyRegistry | None = None,
    require_coherent: bool = True,
) -> ConstitutionalUniverse:
    """Assemble the Universal Constitutional Knowledge Universe.

    ``additional_objects`` is the seam for assimilated artifacts
    (:mod:`engine.uckp.assimilation`): discovery finds everything the package
    declares, and assimilation supplies everything the repository already contained.
    Both arrive through the same registry and are subject to the same admission rules,
    so an assimilated object is not a second class of citizen.
    """
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies or build_vocabulary_registry())
    _contribute_evolution_stage_vocabulary(registry.vocabularies())
    discovery = registry.discover(*tuple(roots))
    extra = tuple(additional_objects)
    if extra:
        registry.register_all(extra, provider_id="engine.uckp.assimilation")

    projections = build_projection_engine()
    projections.require_covers(KNOWN_PROJECTION_KINDS)

    base = Path(persistence_base) if persistence_base is not None else None
    if base is None:
        base = Path(tempfile.mkdtemp(prefix="uckp-universe-"))
    persistence = build_persistence_suite(base)

    execution = build_execution_suite()

    objects = registry.objects()
    timeline = _genesis_timeline(objects)
    evolution = _opening_evolution(registry.seal())
    governance = _opening_governance(registry)

    universe = ConstitutionalUniverse(
        law=ROOT_LAW,
        registry=registry,
        projections=projections,
        persistence=persistence,
        execution=execution,
        timeline=timeline,
        evolution=evolution,
        governance=governance,
        discovery=discovery,
        persistence_base=str(base),
    )
    if require_coherent:
        universe.require_coherent()
    return universe


def universe_execution_request(
    operation: str = "universe-seal", subject: str = ""
) -> ExecutionRequest:
    """The canonical request used to prove execution interchangeability."""
    return ExecutionRequest.of(operation, subject)


__all__ = [
    "BUILDER_ACTOR",
    "DEFAULT_DISCOVERY_ROOTS",
    "KNOWN_PERSISTENCE_KINDS",
    "ConstitutionalUniverse",
    "build_universe",
    "universe_execution_request",
]
