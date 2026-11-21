"""UCKP Layer Zero — Universal Intelligence (Article 15).

Article 15 requires that knowledge reason about itself, and that no conclusion rest on a
hardcoded assumption. Both clauses are design constraints here.

Every reasoner takes the registry and returns findings derived from what the objects
actually declare. None contains a list of expected identities, a threshold tuned to the
present corpus, or a special case for a particular object. That is not a stylistic
preference: a reasoner with a hardcoded expectation reports "correct" for the corpus it
was written against and quietly goes blind as the universe grows, which is the failure
mode Article 15 exists to prevent.

Thirteen reasoners are provided, one per reasoning kind the mission names. They report;
they never mutate. Findings carry a severity so a consumer can distinguish a violation
from an observation, and :meth:`UniversalIntelligence.report` aggregates all thirteen
into one deterministic document.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum

from engine.uckp.canonical import content_hash
from engine.uckp.errors import UCKPValidationError
from engine.uckp.graph import OBJECT_SCOPE
from engine.uckp.law import ROOT_LAW
from engine.uckp.registry import UniversalKnowledgeRegistry
from engine.uckp.resolution import Resolution, ResolutionReader, binding_reader
from engine.uckp.ucko import UCKO

#: Similarity at or above which two statements are reported as near-duplicates.
#: Derived from the mission's own duplicate-prevention discipline rather than tuned to
#: this corpus, and exposed so a caller can reason at a different tolerance.
NEAR_DUPLICATE_SIMILARITY = 0.85


class ReasoningKind(str, Enum):
    """The thirteen ways the universe reasons about itself."""

    DEPENDENCY = "dependency"
    SEMANTIC = "semantic"
    CONSTITUTIONAL = "constitutional"
    AUTHORITY = "authority"
    GOVERNANCE = "governance"
    EVOLUTION = "evolution"
    RISK = "risk"
    IMPACT = "impact"
    CONSISTENCY = "consistency"
    GAP = "gap"
    REDUNDANCY = "redundancy"
    OPTIMIZATION = "optimization"
    FUTURE = "future"

    @classmethod
    def coerce(cls, value: object) -> ReasoningKind:
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.value == text:
                return member
        raise UCKPValidationError("unknown reasoning kind", kind=str(value))


VIOLATION = "violation"
OBSERVATION = "observation"


@dataclass(frozen=True, slots=True)
class Finding:
    """One conclusion the universe reached about itself."""

    reasoning: str
    severity: str
    subject: str
    statement: str

    def to_dict(self) -> dict[str, str]:
        return {
            "reasoning": self.reasoning,
            "severity": self.severity,
            "subject": self.subject,
            "statement": self.statement,
        }


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    """The findings and measurements of one reasoner."""

    kind: ReasoningKind
    findings: tuple[Finding, ...] = field(default_factory=tuple)
    observations: Mapping[str, float] = field(default_factory=dict)

    @property
    def violations(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity == VIOLATION)

    @property
    def clean(self) -> bool:
        return not self.violations

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "clean": self.clean,
            "counts": {"findings": len(self.findings), "violations": len(self.violations)},
            "observations": {k: self.observations[k] for k in sorted(self.observations)},
            "findings": [finding.to_dict() for finding in self.findings],
        }


#: Where a category-integrity observation's evidence is read from. Named in every such
#: finding so the statement cites its source rather than asserting a conclusion: a reader
#: can recompute the whole map from these two facets and nothing else.
CATEGORY_EVIDENCE = "taxonomy.category x discovery.provider"


@dataclass(frozen=True, slots=True)
class CategoryPopulation:
    """Who actually populates one category, measured over the whole registry.

    ``by_provider`` pairs each distinct, named provider with the number of objects it
    minted into the category, provider-sorted so the value is deterministic.
    ``unattributed`` counts objects in the category that name no provider at all.

    That last count is defence in depth rather than a live expectation: ``UCKO.mint``
    coerces an empty provider to its own module name, so nothing minted lawfully arrives
    without one. But the guarantee lives in that one coercion, not in the type —
    ``DiscoveryDescriptor.provider`` is an ordinary string defaulting to empty, and no
    facet check refuses a blank one, because ``Facet.DISCOVERY`` resolves to the
    descriptor rather than to the field. Skipping unattributed objects would therefore
    report a clean attribution for a population this reasoner had not attributed, and
    would do so silently, the first time anything reached the registry by another path.
    """

    category: str
    by_provider: tuple[tuple[str, int], ...]
    unattributed: int

    @property
    def providers(self) -> tuple[str, ...]:
        return tuple(provider for provider, _ in self.by_provider)

    @property
    def objects(self) -> int:
        return sum(count for _, count in self.by_provider) + self.unattributed

    def cite(self) -> str:
        """The providers and their object counts, as a finding may quote them."""
        return ", ".join(f"{provider} ({count})" for provider, count in self.by_provider)

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "providers": {provider: count for provider, count in self.by_provider},
            "unattributed": self.unattributed,
            "objects": self.objects,
            "evidence": CATEGORY_EVIDENCE,
        }


def _category_populations(objects: Iterable[UCKO]) -> tuple[CategoryPopulation, ...]:
    """Every populated category and the providers populating it, in one pass.

    Whole-population by necessity, not by preference: the question is not answerable
    per object. Two providers populating one category is a lawful admission twice over
    — the first admits cleanly and the collision only exists once the second has landed
    — so nothing at admission time can see it, and only a pass over the assembled
    population can.
    """
    counts: dict[str, dict[str, int]] = {}
    unattributed: dict[str, int] = {}
    for obj in objects:
        category = obj.taxonomy.category
        by_provider = counts.setdefault(category, {})
        unattributed.setdefault(category, 0)
        provider = obj.discovery.provider
        if provider:
            by_provider[provider] = by_provider.get(provider, 0) + 1
        else:
            unattributed[category] += 1
    return tuple(
        CategoryPopulation(
            category,
            tuple((provider, counts[category][provider]) for provider in sorted(counts[category])),
            unattributed[category],
        )
        for category in sorted(counts)
    )


#: The constitutional resolution section this reasoner consumes when it is declared. It
#: is *recognitive*, like the six sections beside it: it records the populator a category
#: already has and the authority accountable for that population, and grants nothing
#: (`PHASE-UCF-012` D1). This module reads it; it never writes it, and its absence is a
#: lawful state (:data:`UNKNOWN`), not a defect.
CATEGORY_OWNERSHIP_RESOLUTION = "category_ownership_resolution"

#: The list the section declares its recognitions under, and the three fields of one
#: entry. Named here because the consumer and the eventual ledger must agree on exactly
#: one set of names; a reader that guessed among several would make two shapes lawful.
RECOGNITIONS = "recognitions"
RECOGNITION_CATEGORY = "category"
RECOGNISED_POPULATORS = "recognised_populators"
ACCOUNTABLE_AUTHORITY = "accountable_authority"

#: The three integrity states of one category. These are *states*, not severities: every
#: finding this reasoner emits is an :data:`OBSERVATION` whatever the state, because a
#: recognition is evidence about the repository, not a gate over it.
#:
#: :data:`UNKNOWN` is permanent, never transitional (`PHASE-UCF-012` D7). Removing it once
#: every category is declared would make the check silently pass for any category
#: populated after the ledger was written — the same blind spot one layer up.
MATCH = "match"
CONFLICT = "conflict"
UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class CategoryRecognition:
    """One category's recognised population, as a resolution declares it.

    ``accountable_authority`` is deliberately *not* a value from the Facet 7 owner space
    (`PHASE-UCF-012` D4): object ownership is per-object accountability, and no
    aggregation of it yields a category owner. It is the governance entity accountable
    for the category's population policy, and a finding reports it when it turns out to
    name a measured provider instead.
    """

    category: str
    populators: tuple[str, ...]
    accountable_authority: str

    def recognises(self, provider: str) -> bool:
        return provider in self.populators

    def cite(self) -> str:
        """The recognition as a finding may quote it."""
        return f"[{', '.join(self.populators)}] accountable to {self.accountable_authority}"

    def to_dict(self) -> dict[str, object]:
        return {
            RECOGNITION_CATEGORY: self.category,
            RECOGNISED_POPULATORS: list(self.populators),
            ACCOUNTABLE_AUTHORITY: self.accountable_authority,
        }


@dataclass(frozen=True, slots=True)
class CategoryIntegrity:
    """Measured reality and recognised resolution for one category, compared.

    Both sides are carried rather than collapsed into a verdict, because the whole point
    of the comparison is that a reader can recompute it: ``measured`` comes from the two
    facets :data:`CATEGORY_EVIDENCE` names, ``declared`` from the resolution record, and
    ``state`` from those two and nothing else.
    """

    category: str
    state: str
    population: CategoryPopulation | None = None
    recognition: CategoryRecognition | None = None

    @property
    def measured(self) -> tuple[str, ...]:
        return self.population.providers if self.population is not None else ()

    @property
    def declared(self) -> tuple[str, ...]:
        return self.recognition.populators if self.recognition is not None else ()

    @property
    def unrecognised(self) -> tuple[str, ...]:
        """Providers measured in the category that the resolution does not recognise."""
        declared = frozenset(self.declared)
        return tuple(provider for provider in self.measured if provider not in declared)

    @property
    def unmeasured(self) -> tuple[str, ...]:
        """Populators the resolution recognises that no object measures."""
        measured = frozenset(self.measured)
        return tuple(provider for provider in self.declared if provider not in measured)

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "state": self.state,
            "measured_populators": list(self.measured),
            "recognised_populators": list(self.declared),
            "accountable_authority": (
                self.recognition.accountable_authority if self.recognition is not None else ""
            ),
            "evidence": CATEGORY_EVIDENCE,
            "resolution": CATEGORY_OWNERSHIP_RESOLUTION,
        }


def _recognition(entry: Mapping[str, object]) -> CategoryRecognition | None:
    """One ledger entry as a recognition, or None if it cannot be read as one.

    Total and silent about *why*: :func:`_recognitions` reports the reason, because a
    complaint needs the entry's position and this function does not have it.
    """
    category = entry.get(RECOGNITION_CATEGORY)
    authority = entry.get(ACCOUNTABLE_AUTHORITY)
    declared = entry.get(RECOGNISED_POPULATORS)
    if not isinstance(category, str) or not category.strip():
        return None
    if not isinstance(authority, str) or not authority.strip():
        return None
    if not isinstance(declared, list | tuple) or not declared:
        return None
    populators = tuple(str(name).strip() for name in declared)
    if not all(populators):
        return None
    return CategoryRecognition(category.strip(), populators, authority.strip())


def _recognitions(
    resolution: Resolution,
) -> tuple[dict[str, CategoryRecognition], tuple[str, ...]]:
    """Every readable recognition in ``resolution``, and every way it could not be read.

    Fail-closed in the only sense available to an advisory stage: an entry that cannot be
    read is *dropped and reported*, never repaired and never assumed. A dropped entry
    leaves its category :data:`UNKNOWN`, which is the one disposition that cannot turn an
    unreadable claim into a pass (`PHASE-UCF-012 § 12.1`).

    An **absent** section produces no complaint. Absence is the repository's present,
    lawful state — the ledger has not been written — and reporting it once per reasoning
    pass would be reporting a decision that has already been recorded as deferred. An
    **unreadable** one always produces a complaint, because that is a claim that exists
    and could not be checked.
    """
    complaints: list[str] = []
    if not resolution.readable:
        return {}, (f"could not be read, so no recognition can be resolved: {resolution.detail}",)
    if not resolution.present:
        return {}, ()

    entries = resolution.entries(RECOGNITIONS)
    declared = resolution.declared(RECOGNITIONS)
    if not declared:
        complaints.append(f"is declared and states no {RECOGNITIONS}")
    if len(entries) < declared:
        complaints.append(
            f"declares {declared} {RECOGNITIONS}, of which {declared - len(entries)} "
            "cannot be read as an entry"
        )

    by_category: dict[str, CategoryRecognition] = {}
    duplicated: set[str] = set()
    for index, entry in enumerate(entries):
        recognition = _recognition(entry)
        if recognition is None:
            complaints.append(
                f"entry {index} names no category, no populator, or no "
                f"{ACCOUNTABLE_AUTHORITY}, so it recognises nothing"
            )
            continue
        category = recognition.category
        if category in by_category or category in duplicated:
            if category not in duplicated:
                complaints.append(
                    f"recognises category {category!r} more than once, so no recognition "
                    "of it can be resolved"
                )
            duplicated.add(category)
            by_category.pop(category, None)
            continue
        by_category[category] = recognition
    return by_category, tuple(complaints)


def _category_integrity(
    populations: Iterable[CategoryPopulation],
    recognitions: Mapping[str, CategoryRecognition],
) -> tuple[CategoryIntegrity, ...]:
    """Compare measured reality with recognised resolution, per category.

    Total over the union of both sides, never over the measured side alone: a recognition
    of a category nothing populates is exactly as much a divergence as a populator nothing
    recognises, and a comparison that only iterated what it could measure would report
    that it had checked something it never looked at.

    :data:`MATCH` requires the measured providers to be non-empty *and* wholly recognised.
    An empty measured side is not a subset that passes: a category whose objects name no
    provider at all has nothing to compare against the declaration, and calling that a
    match would certify a declaration against no evidence.
    """
    by_category = {population.category: population for population in populations}
    states: list[CategoryIntegrity] = []
    for category in sorted(set(by_category) | set(recognitions)):
        population = by_category.get(category)
        recognition = recognitions.get(category)
        measured = population.providers if population is not None else ()
        if recognition is None:
            state = UNKNOWN
        elif measured and all(recognition.recognises(provider) for provider in measured):
            state = MATCH
        else:
            state = CONFLICT
        states.append(CategoryIntegrity(category, state, population, recognition))
    return tuple(states)


def _category_findings(
    integrity: CategoryIntegrity, providers: frozenset[str]
) -> tuple[Finding, ...]:
    """What one category's comparison reports. Advisory at every state.

    ``providers`` is every provider measured anywhere in the registry, which is what makes
    the provider-named-as-owner check possible: naming a provider as the accountable
    authority for category A is the same substitution whether or not that provider
    populates A (`PHASE-UCF-012` D5).
    """
    subject = f"category:{integrity.category}"
    population = integrity.population
    recognition = integrity.recognition
    findings: list[Finding] = []

    if recognition is None:
        # UNKNOWN — the observational stage's own statements, unchanged. One populating
        # provider is not evidence of authority; it is evidence of one populator.
        if population is None:  # pragma: no cover - not enumerated by _category_integrity
            return ()
        if len(population.providers) > 1:
            findings.append(
                Finding(
                    "gap",
                    OBSERVATION,
                    subject,
                    f"is populated by {len(population.providers)} providers "
                    f"[{population.cite()}] and no declared owner reconciles them; "
                    f"ownership clarification is required (per {CATEGORY_EVIDENCE})",
                )
            )
        elif population.providers:
            findings.append(
                Finding(
                    "gap",
                    OBSERVATION,
                    subject,
                    f"is populated only by [{population.cite()}], and no owner is "
                    "declared for it: an undeclared default, not a decision "
                    f"(per {CATEGORY_EVIDENCE})",
                )
            )
    elif integrity.state == MATCH and population is not None:
        statement = (
            f"is populated by [{population.cite()}], every populator of it recognised by "
            f"{recognition.accountable_authority} in {CATEGORY_OWNERSHIP_RESOLUTION} "
            f"(per {CATEGORY_EVIDENCE})"
        )
        if len(population.providers) > 1:
            # A plurality that a ledger merely lists is not a plurality that a ledger
            # reconciles. Recognising both populators must not be the move that makes a
            # contamination finding disappear (`PHASE-UCF-012` D9).
            statement += (
                "; a recognised plurality is reconciled only where the resolution "
                "declares a bounded question for each populator, so the plurality "
                "stands reported rather than closed"
            )
        findings.append(Finding("gap", OBSERVATION, subject, statement))
    elif integrity.unrecognised and population is not None:
        findings.append(
            Finding(
                "gap",
                OBSERVATION,
                subject,
                f"is populated by [{population.cite()}], and "
                f"[{', '.join(integrity.unrecognised)}] is not among the populators "
                f"{recognition.accountable_authority} recognises "
                f"[{', '.join(integrity.declared)}] "
                f"(per {CATEGORY_EVIDENCE} against {CATEGORY_OWNERSHIP_RESOLUTION})",
            )
        )
    else:
        findings.append(
            Finding(
                "gap",
                OBSERVATION,
                subject,
                f"is recognised for [{', '.join(integrity.declared)}] by "
                f"{recognition.accountable_authority} in {CATEGORY_OWNERSHIP_RESOLUTION}, "
                "and no object attributes it to any provider "
                f"(per {CATEGORY_EVIDENCE})",
            )
        )

    if recognition is not None and recognition.accountable_authority in providers:
        findings.append(
            Finding(
                "gap",
                OBSERVATION,
                subject,
                f"recognises {recognition.accountable_authority} as accountable for it, and "
                "that name is a measured provider: a provider is a discovery fact, never "
                f"an owner (per {CATEGORY_EVIDENCE} against {CATEGORY_OWNERSHIP_RESOLUTION})",
            )
        )
    return tuple(findings)


def _tokens(text: str) -> frozenset[str]:
    return frozenset(part for part in str(text).casefold().split() if len(part) > 2)


def _similarity(left: frozenset[str], right: frozenset[str]) -> float:
    if not left or not right:
        return 0.0
    union = len(left | right)
    return len(left & right) / union if union else 0.0


class UniversalIntelligence:
    """Reasoning over the canonical universe. Reports; never mutates."""

    __slots__ = ("_registry", "_graph", "_resolutions")

    def __init__(
        self,
        registry: UniversalKnowledgeRegistry,
        resolutions: ResolutionReader | None = None,
    ) -> None:
        """Reason over ``registry``, resolving declarations through ``resolutions``.

        ``resolutions`` defaults to the repository's constitutional binding. Constructing
        the reader touches no disk — it loads lazily on first read — so an intelligence
        that never asks a declaration question costs exactly what it did before.
        """
        self._registry = registry
        self._graph = registry.graph()
        self._resolutions = binding_reader() if resolutions is None else resolutions

    # --- measurement the reasoners share ----------------------------------------

    def category_populations(self) -> tuple[CategoryPopulation, ...]:
        """Which providers populate which category, over the whole registry.

        Exposed because it is the evidence behind every category-integrity finding, and
        a finding whose evidence cannot be recomputed by its reader is an assertion. It
        derives nothing and owns nothing: ownership is not inferred from population here
        or anywhere, because a provider that populates a category is a fact about
        discovery (Facet 21), not a claim of authority (Facet 5) or accountability
        (Facet 7) — three questions the constitution deliberately keeps apart.
        """
        return _category_populations(self._registry.objects())

    def category_integrity(self) -> tuple[CategoryIntegrity, ...]:
        """Measured population against recognised resolution, one state per category.

        The join `PHASE-UCF-011` could not build, because the declared side did not exist
        to read. It derives no ownership and confers none: it reports whether what the
        repository *does* and what a resolution *recognises* are the same thing, and
        reports :data:`UNKNOWN` — never a pass — wherever there is nothing to compare.
        """
        recognitions, _ = _recognitions(self._resolutions.read(CATEGORY_OWNERSHIP_RESOLUTION))
        return _category_integrity(self.category_populations(), recognitions)

    # --- the thirteen reasoners -------------------------------------------------

    def dependency_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        depths: list[int] = []
        for obj in self._registry.objects():
            for dependency in obj.dependencies:
                if dependency not in self._registry:
                    findings.append(
                        Finding(
                            "dependency",
                            VIOLATION,
                            obj.ucko_id,
                            f"depends on {dependency}, which does not exist",
                        )
                    )
            depths.append(len(self._graph.authority_chain(obj.ucko_id)))
        for edge in self._graph.dangling():
            findings.append(
                Finding(
                    "dependency",
                    VIOLATION,
                    edge.source,
                    f"{edge.relation} edge to {edge.target} cannot be executed",
                )
            )
        return ReasoningResult(
            ReasoningKind.DEPENDENCY,
            tuple(findings),
            {
                "objects": float(len(self._registry)),
                "edges": float(len(self._graph.edges())),
                "max_authority_depth": float(max(depths) if depths else 0),
            },
        )

    def semantic_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        objects = self._registry.objects()
        profiles = [
            (obj, _tokens(f"{obj.semantic_identity.concept} {obj.semantic_identity.definition}"))
            for obj in objects
        ]
        near = 0
        for index, (left, left_tokens) in enumerate(profiles):
            for right, right_tokens in profiles[index + 1 :]:
                score = _similarity(left_tokens, right_tokens)
                if score >= NEAR_DUPLICATE_SIMILARITY:
                    near += 1
                    # An OBSERVATION, not a VIOLATION. This is a token-overlap
                    # heuristic, and a heuristic cannot establish a breach — the
                    # registry has already admitted both objects as semantically
                    # distinct, which is the actual finding of fact. Reporting a
                    # score as a violation is the same category error as reporting
                    # an unmeasured invariant as satisfied: it asserts more than the
                    # measurement supports.
                    #
                    # It would also make the constitution self-contradicting. Articles
                    # 9 and 10 require that every persistence and execution technology
                    # satisfy *one identical contract*, so a family of ten adapters
                    # necessarily describes itself in near-identical words. High overlap
                    # there is the property being demanded, not a defect in it.
                    findings.append(
                        Finding(
                            "semantic",
                            OBSERVATION,
                            left.ucko_id,
                            f"is worded much like {right.ucko_id} (score {score:.2f}); "
                            "distinct meanings, so worth a look but not a breach",
                        )
                    )
        # Identical meaning under two identities *is* a fact, and a breach of Article 3.
        for group in self._registry.duplicate_semantics():
            findings.append(
                Finding("semantic", VIOLATION, group[0], f"identical meaning homed at {group}")
            )
        return ReasoningResult(
            ReasoningKind.SEMANTIC,
            tuple(findings),
            {"objects": float(len(objects)), "near_duplicates": float(near)},
        )

    def constitutional_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        for obj in self._registry.objects():
            if not ROOT_LAW.governs(obj.taxonomy.category):
                findings.append(
                    Finding(
                        "constitutional",
                        VIOLATION,
                        obj.ucko_id,
                        f"category {obj.taxonomy.category!r} is not a governed category",
                    )
                )
            if ROOT_LAW.is_non_authoritative(obj.taxonomy.category):
                findings.append(
                    Finding(
                        "constitutional",
                        VIOLATION,
                        obj.ucko_id,
                        f"category {obj.taxonomy.category!r} may only ever be a projection",
                    )
                )
        covered = {obj.taxonomy.category for obj in self._registry.objects()}
        return ReasoningResult(
            ReasoningKind.CONSTITUTIONAL,
            tuple(findings),
            {
                "governed_categories": float(len(ROOT_LAW.governed_categories)),
                "categories_populated": float(len(covered)),
                "articles": float(len(ROOT_LAW.articles)),
            },
        )

    def authority_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        roots = self._registry.root_ids()
        if len(roots) != 1:
            findings.append(
                Finding(
                    "authority",
                    VIOLATION,
                    "uckp.universe",
                    f"the universe declares {len(roots)} constitutional roots, not one",
                )
            )
        tiers = self._registry.vocabularies().require("uckp.authority-tier")
        for obj in self._registry.objects():
            parent_id = obj.authority.derives_from
            if parent_id == obj.ucko_id:
                continue
            parent = self._registry.get(parent_id)
            if parent is None:
                findings.append(
                    Finding(
                        "authority",
                        VIOLATION,
                        obj.ucko_id,
                        f"derives authority from {parent_id}, which does not exist",
                    )
                )
                continue
            child_rank = tiers.require(obj.authority.tier).rank
            parent_rank = tiers.require(parent.authority.tier).rank
            if parent_rank > child_rank:
                findings.append(
                    Finding(
                        "authority",
                        VIOLATION,
                        obj.ucko_id,
                        f"outranks the authority it derives from ({parent_id})",
                    )
                )
        for cycle in self._graph.cycles("authority"):
            findings.append(
                Finding("authority", VIOLATION, cycle[0], f"authority cycle {list(cycle)}")
            )
        return ReasoningResult(
            ReasoningKind.AUTHORITY,
            tuple(findings),
            {"roots": float(len(roots)), "objects": float(len(self._registry))},
        )

    def governance_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        ungoverned = 0
        for obj in self._registry.objects():
            if not obj.governance_context.value:
                ungoverned += 1
                findings.append(
                    Finding("governance", VIOLATION, obj.ucko_id, "names no governance authority")
                )
        return ReasoningResult(
            ReasoningKind.GOVERNANCE,
            tuple(findings),
            {
                "objects": float(len(self._registry)),
                "ungoverned": float(ungoverned),
                "governance_edges": float(len(self._graph.edges_of_class("governance"))),
            },
        )

    def evolution_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        without_history = [
            obj.ucko_id for obj in self._registry.objects() if not obj.temporal_history
        ]
        for ucko_id in without_history:
            findings.append(Finding("evolution", VIOLATION, ucko_id, "records no temporal history"))
        stateless = sum(1 for obj in self._registry.objects() if not obj.evolution_history)
        return ReasoningResult(
            ReasoningKind.EVOLUTION,
            tuple(findings),
            {
                "objects": float(len(self._registry)),
                "without_temporal_history": float(len(without_history)),
                "not_yet_in_a_state": float(stateless),
            },
        )

    def risk_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        owners: dict[str, int] = {}
        uncertified = 0
        for obj in self._registry.objects():
            owners[obj.ownership.owner] = owners.get(obj.ownership.owner, 0) + 1
            if obj.authority.tier == "constitutional" and not obj.certification.attested:
                uncertified += 1
                findings.append(
                    Finding(
                        "risk",
                        OBSERVATION,
                        obj.ucko_id,
                        "carries constitutional authority with no certification",
                    )
                )
        total = max(len(self._registry), 1)
        concentration = max(owners.values()) / total if owners else 0.0
        return ReasoningResult(
            ReasoningKind.RISK,
            tuple(findings),
            {
                "owners": float(len(owners)),
                "ownership_concentration": round(concentration, 4),
                "uncertified_constitutional": float(uncertified),
            },
        )

    def impact_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        fan_in: dict[str, int] = {}
        for edge in self._graph.edges():
            fan_in[edge.target] = fan_in.get(edge.target, 0) + 1
        top = sorted(fan_in.items(), key=lambda item: (-item[1], item[0]))[:3]
        for ucko_id, count in top:
            findings.append(
                Finding(
                    "impact",
                    OBSERVATION,
                    ucko_id,
                    f"{count} relationships point at it; changing it changes them",
                )
            )
        return ReasoningResult(
            ReasoningKind.IMPACT,
            tuple(findings),
            {
                "max_fan_in": float(top[0][1] if top else 0),
                "objects_referenced": float(len(fan_in)),
            },
        )

    def consistency_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        for obj in self._registry.objects():
            if obj.lifecycle == "operational" and not obj.validation.attested:
                findings.append(
                    Finding(
                        "consistency",
                        VIOLATION,
                        obj.ucko_id,
                        "is operational but was never validated",
                    )
                )
            if not obj.verify_integrity():
                findings.append(
                    Finding("consistency", VIOLATION, obj.ucko_id, "seal does not match content")
                )
            if not obj.verify_replay():
                findings.append(
                    Finding("consistency", VIOLATION, obj.ucko_id, "replay proof does not hold")
                )
        return ReasoningResult(
            ReasoningKind.CONSISTENCY,
            tuple(findings),
            {"objects": float(len(self._registry))},
        )

    def gap_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        populated = {obj.taxonomy.category for obj in self._registry.objects()}
        missing = tuple(
            category for category in ROOT_LAW.governed_categories if category not in populated
        )
        for category in missing:
            findings.append(
                Finding(
                    "gap",
                    OBSERVATION,
                    f"category:{category}",
                    "a governed category with no canonical object yet",
                )
            )
        # Provider category integrity, observed rather than enforced. A category is a
        # classification, not a claim of identity, so two providers populating one is
        # not a breach of any invariant the law declares — which is precisely why it
        # went undetected until a provider contaminated three closed categories and was
        # caught by an unrelated count assertion.
        #
        # Two planes, one truth. The population is MEASURED here, over the assembled
        # registry; ownership is RECOGNISED in a constitutional resolution, read through
        # engine.uckp.resolution. Neither derives the other, and this reasoner asserts
        # neither: it reports whether they agree. Every state stays an OBSERVATION,
        # because a recognition is evidence and not a gate — including CONFLICT, whose
        # promotion to a verdict is a separate, deliberately separate decision
        # (`PHASE-UCF-012` D15).
        populations = self.category_populations()
        resolution = self._resolutions.read(CATEGORY_OWNERSHIP_RESOLUTION)
        recognitions, complaints = _recognitions(resolution)
        for complaint in complaints:
            findings.append(
                Finding(
                    "gap",
                    OBSERVATION,
                    f"resolution:{CATEGORY_OWNERSHIP_RESOLUTION}",
                    f"{complaint} (read from {resolution.source})",
                )
            )
        providers = frozenset(
            provider for population in populations for provider in population.providers
        )
        integrity = _category_integrity(populations, recognitions)
        for state in integrity:
            findings.extend(_category_findings(state, providers))
            population = state.population
            if population is not None and population.unattributed:
                findings.append(
                    Finding(
                        "gap",
                        OBSERVATION,
                        f"category:{population.category}",
                        f"{population.unattributed} of its {population.objects} objects "
                        "name no provider, so their category assignment cannot be "
                        f"attributed to anyone (per {CATEGORY_EVIDENCE})",
                    )
                )
        for obj in self._registry.objects():
            for facet in obj.missing_facets():
                findings.append(
                    Finding("gap", VIOLATION, obj.ucko_id, f"facet {facet.value} is absent")
                )
        return ReasoningResult(
            ReasoningKind.GAP,
            tuple(findings),
            {
                "governed_categories": float(len(ROOT_LAW.governed_categories)),
                "unpopulated_categories": float(len(missing)),
                "categories_populated": float(len(populations)),
                "categories_multi_provider": float(
                    sum(1 for p in populations if len(p.providers) > 1)
                ),
                # Populated, and still nothing recognises the population. Unchanged in
                # meaning from the observational stage; it simply now has a declared side
                # that can retire a category from the count instead of no side at all.
                "categories_without_declared_owner": float(
                    sum(1 for s in integrity if s.state == UNKNOWN and s.measured)
                ),
                "categories_recognised": float(sum(1 for s in integrity if s.state == MATCH)),
                "categories_ownership_conflict": float(
                    sum(1 for s in integrity if s.state == CONFLICT)
                ),
                "categories_ownership_unknown": float(
                    sum(1 for s in integrity if s.state == UNKNOWN)
                ),
                "category_recognitions": float(len(recognitions)),
                "categories_unattributed": float(sum(1 for p in populations if p.unattributed)),
                "coverage": round(
                    len(populated & set(ROOT_LAW.governed_categories))
                    / max(len(ROOT_LAW.governed_categories), 1),
                    4,
                ),
            },
        )

    def redundancy_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        by_definition: dict[str, list[str]] = {}
        for obj in self._registry.objects():
            key = content_hash(" ".join(obj.semantic_identity.definition.split()).casefold())
            by_definition.setdefault(key, []).append(obj.ucko_id)
        repeated = 0
        for _, ids in sorted(by_definition.items()):
            if len(ids) > 1:
                repeated += 1
                findings.append(
                    Finding(
                        "redundancy",
                        VIOLATION,
                        sorted(ids)[0],
                        f"the identical definition is stated by {sorted(ids)}",
                    )
                )
        return ReasoningResult(
            ReasoningKind.REDUNDANCY,
            tuple(findings),
            {
                "distinct_definitions": float(len(by_definition)),
                "repeated_definitions": float(repeated),
            },
        )

    def optimization_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        # Object-scoped edges only. An ownership edge points at an accountable *person*
        # and every object carries one (Facet 7 is mandatory), so counting every edge
        # would make "participates in nothing" a statement that is never true of
        # anything — a measurement whose finding is unreachable measures nothing. The
        # graph draws the same distinction for dangling edges and reachability.
        fan_out = {
            obj.ucko_id: len(
                tuple(
                    edge
                    for edge in self._graph.out_edges(obj.ucko_id)
                    if edge.scope == OBJECT_SCOPE
                )
            )
            for obj in self._registry.objects()
        }
        isolated = tuple(sorted(key for key, count in fan_out.items() if count == 0))
        for ucko_id in isolated:
            findings.append(
                Finding(
                    "optimization",
                    OBSERVATION,
                    ucko_id,
                    "declares no relationship to another object; it participates in nothing",
                )
            )
        average = sum(fan_out.values()) / max(len(fan_out), 1)
        return ReasoningResult(
            ReasoningKind.OPTIMIZATION,
            tuple(findings),
            {
                "average_fan_out": round(average, 4),
                "isolated_objects": float(len(isolated)),
            },
        )

    def future_reasoning(self) -> ReasoningResult:
        findings: list[Finding] = []
        future_edges = self._graph.edges_of_class("future")
        for edge in future_edges:
            findings.append(
                Finding(
                    "future",
                    OBSERVATION,
                    edge.source,
                    f"declares an intended future binding to {edge.target}",
                )
            )
        extensible = self._registry.vocabularies().is_extensible()
        if not extensible:
            findings.append(
                Finding(
                    "future",
                    VIOLATION,
                    "uckp.universe",
                    "a vocabulary refuses an unknown future member",
                )
            )
        return ReasoningResult(
            ReasoningKind.FUTURE,
            tuple(findings),
            {
                "future_bindings": float(len(future_edges)),
                "vocabularies_extensible": 1.0 if extensible else 0.0,
            },
        )

    # --- dispatch ---------------------------------------------------------------

    def reasoners(self) -> Mapping[ReasoningKind, Callable[[], ReasoningResult]]:
        return {
            ReasoningKind.AUTHORITY: self.authority_reasoning,
            ReasoningKind.CONSISTENCY: self.consistency_reasoning,
            ReasoningKind.CONSTITUTIONAL: self.constitutional_reasoning,
            ReasoningKind.DEPENDENCY: self.dependency_reasoning,
            ReasoningKind.EVOLUTION: self.evolution_reasoning,
            ReasoningKind.FUTURE: self.future_reasoning,
            ReasoningKind.GAP: self.gap_reasoning,
            ReasoningKind.GOVERNANCE: self.governance_reasoning,
            ReasoningKind.IMPACT: self.impact_reasoning,
            ReasoningKind.OPTIMIZATION: self.optimization_reasoning,
            ReasoningKind.REDUNDANCY: self.redundancy_reasoning,
            ReasoningKind.RISK: self.risk_reasoning,
            ReasoningKind.SEMANTIC: self.semantic_reasoning,
        }

    def reason(self, kind: ReasoningKind | str) -> ReasoningResult:
        resolved = ReasoningKind.coerce(kind)
        return self.reasoners()[resolved]()

    def reason_all(self) -> tuple[ReasoningResult, ...]:
        reasoners = self.reasoners()
        return tuple(reasoners[kind]() for kind in sorted(reasoners, key=lambda k: k.value))

    def report(self) -> dict[str, object]:
        results = self.reason_all()
        violations = [f for result in results for f in result.violations]
        return {
            "schema": "ucos-uckp-intelligence-report",
            "version": "1.0.0",
            "counts": {
                "reasoners": len(results),
                "findings": sum(len(r.findings) for r in results),
                "violations": len(violations),
            },
            "clean": not violations,
            "graph_fingerprint": self._graph.fingerprint(),
            "results": [result.to_dict() for result in results],
        }


def build_intelligence(
    registry: UniversalKnowledgeRegistry,
    resolutions: ResolutionReader | None = None,
) -> UniversalIntelligence:
    return UniversalIntelligence(registry, resolutions)


def reasoning_kinds() -> tuple[str, ...]:
    return tuple(kind.value for kind in ReasoningKind)


__all__ = [
    "ACCOUNTABLE_AUTHORITY",
    "CATEGORY_EVIDENCE",
    "CATEGORY_OWNERSHIP_RESOLUTION",
    "CONFLICT",
    "MATCH",
    "NEAR_DUPLICATE_SIMILARITY",
    "OBSERVATION",
    "RECOGNISED_POPULATORS",
    "RECOGNITIONS",
    "RECOGNITION_CATEGORY",
    "UNKNOWN",
    "VIOLATION",
    "CategoryIntegrity",
    "CategoryPopulation",
    "CategoryRecognition",
    "Finding",
    "ReasoningKind",
    "ReasoningResult",
    "UCKO",
    "UniversalIntelligence",
    "build_intelligence",
    "reasoning_kinds",
]
