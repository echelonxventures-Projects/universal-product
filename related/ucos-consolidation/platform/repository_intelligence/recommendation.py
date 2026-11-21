"""UCOS-EPIC-014 — Repository Recommendation Engine (Terminal T5).

Discovery says what is true; the recommendation engine says what to *do* about it — and it
is deliberately incapable of recommending a duplicate. Every recommendation is one of
:class:`~platform.repository_intelligence.contracts.RecommendationAction`, and
``CREATE`` is only ever reached after :meth:`RepositoryRecommendationEngine.advise` has
failed to find any existing capability that could be reused, extended or composed.

Two entry points:

    * :meth:`RepositoryRecommendationEngine.recommend` — rank everything the eight
      dimensions found into an ordered work list. Priority is *derived* from severity and
      dimension, never hand-assigned, so the ordering is reproducible and arguable from
      evidence rather than taste.
    * :meth:`RepositoryRecommendationEngine.advise` — the **never-duplicate guard**. Given
      a capability someone proposes to build, it answers with the existing capability to
      reuse or extend, and only permits creation when the repository genuinely has no
      candidate. This is the mechanism that makes "never duplicate capabilities" and
      "everything must extend the existing repository" enforceable at proposal time,
      before any code exists to detect as a duplicate.

Aggregation policy: blocking findings each yield their own recommendation (there are few,
and each needs individual repair); advisory findings are aggregated per finding code (there
are many, and they share one remedy), with their subjects carried as evidence. This keeps
the work list short enough to act on without discarding any finding.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from platform.repository_intelligence.contracts import (
    DiscoveryDimension,
    Finding,
    Recommendation,
    RecommendationAction,
)
from platform.repository_intelligence.discovery import (
    CATALOG_OMISSION,
    CONFLICT_ENTRY_POINT_ALIASED,
    DUPLICATE_CAPABILITY_NAME,
    DUPLICATE_SYMBOL_SURFACE,
    DUPLICATE_TRIVIAL_CONTENT,
    GAP_MISSING_CONVENTION_MODULE,
    GAP_UNPUBLISHED_CLI,
    GAP_UNREGISTERED_COV_OPTION,
    GAP_UNREGISTERED_COVERAGE,
    GAP_UNTESTED,
    OWNERSHIP_UNOWNED,
    REUSE_UNPROVEN,
    DiscoveryOutcome,
)
from platform.repository_intelligence.errors import RecommendationError
from platform.repository_intelligence.graph import RepositoryGraph
from platform.repository_intelligence.substrate import RepositorySubstrate
from typing import Any

#: Derived priority bands (lower is more urgent). A blocking contradiction in the
#: dependency or conflict dimension is the most urgent thing a repository can have, because
#: it invalidates the reuse guarantees every other recommendation depends on.
PRIORITY_STRUCTURAL_CONTRADICTION = 1
PRIORITY_BLOCKING = 2
PRIORITY_DUPLICATION = 3
PRIORITY_REGISTRATION = 4
PRIORITY_COMPLETENESS = 5
PRIORITY_REUSE_OPPORTUNITY = 6
PRIORITY_ADVISORY = 7
PRIORITY_NONE = 9

#: Finding code → (action, priority, remedy) for aggregated advisory findings.
_ADVISORY_REMEDY: dict[str, tuple[RecommendationAction, int, str]] = {
    DUPLICATE_SYMBOL_SURFACE: (
        RecommendationAction.COMPOSE,
        PRIORITY_DUPLICATION,
        "compose the overlapping public surface into one owning capability and have the "
        "other consume it, rather than maintaining two implementations of the same surface",
    ),
    DUPLICATE_CAPABILITY_NAME: (
        RecommendationAction.REUSE,
        PRIORITY_DUPLICATION,
        "confirm each same-named capability pair is an intentional layered pair whose "
        "upper layer composes the lower, and not two independent implementations",
    ),
    DUPLICATE_TRIVIAL_CONTENT: (
        RecommendationAction.NO_ACTION,
        PRIORITY_ADVISORY,
        "byte-identical trivial modules are a package-marker convention; no action required",
    ),
    GAP_UNREGISTERED_COVERAGE: (
        RecommendationAction.REGISTER,
        PRIORITY_REGISTRATION,
        "add the capability to the coverage source list so the repository coverage gate "
        "measures it",
    ),
    GAP_UNREGISTERED_COV_OPTION: (
        RecommendationAction.REGISTER,
        PRIORITY_REGISTRATION,
        "add a --cov entry for the capability so the test gate reports it",
    ),
    CATALOG_OMISSION: (
        RecommendationAction.REGISTER,
        PRIORITY_REGISTRATION,
        "regenerate the UCOS-RIE-001 capability catalog so the composed capability "
        "inventory matches the code substrate",
    ),
    GAP_UNTESTED: (
        RecommendationAction.EXTEND,
        PRIORITY_COMPLETENESS,
        "extend the existing test suite to import and exercise the capability",
    ),
    GAP_MISSING_CONVENTION_MODULE: (
        RecommendationAction.EXTEND,
        PRIORITY_COMPLETENESS,
        "add the convention module its peer capabilities already declare, so the layer "
        "presents one uniform surface",
    ),
    GAP_UNPUBLISHED_CLI: (
        RecommendationAction.REGISTER,
        PRIORITY_REGISTRATION,
        "publish the capability's cli module as a console script, or remove the cli module",
    ),
    REUSE_UNPROVEN: (
        RecommendationAction.REUSE,
        PRIORITY_REUSE_OPPORTUNITY,
        "compose the capability from an existing consumer or publish an entry point; an "
        "unconsumed capability is the precondition for someone re-implementing it",
    ),
    OWNERSHIP_UNOWNED: (
        RecommendationAction.REGISTER,
        PRIORITY_REGISTRATION,
        "declare the owning terminal or programme in the capability's package docstring so "
        "ownership is derivable",
    ),
    CONFLICT_ENTRY_POINT_ALIASED: (
        RecommendationAction.NO_ACTION,
        PRIORITY_ADVISORY,
        "confirm the aliased console scripts are an intentional compatibility alias",
    ),
}

#: Tokens carried by nearly every capability name; useless for similarity matching.
_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "with",
        "universal",
        "engine",
        "platform",
        "ucos",
        "core",
        "common",
        "base",
        "util",
        "utils",
        "helper",
        "helpers",
        "manager",
        "service",
        "system",
    }
)

_TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9]*")

#: A candidate must reach this token-overlap score, and share at least this many tokens,
#: before it is offered as a reuse target. Both bars exist because either alone
#: over-matches: a score alone fires on one incidental shared word, and a shared count
#: alone fires on two words shared between otherwise unrelated capabilities.
_ADVICE_MIN_SCORE = 0.34
_ADVICE_MIN_SHARED = 2


@dataclass(frozen=True, slots=True)
class ReuseCandidate:
    """An existing capability that could satisfy a proposed capability."""

    capability: str
    score: float
    matched_tokens: tuple[str, ...]
    reuse_directive: str
    replacement_prohibited: bool
    location: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "score": self.score,
            "matched_tokens": list(self.matched_tokens),
            "reuse_directive": self.reuse_directive,
            "replacement_prohibited": self.replacement_prohibited,
            "location": self.location,
        }


class RepositoryRecommendationEngine:
    """Derives ranked, evidence-cited recommendations from a discovery outcome."""

    __slots__ = ("_substrate", "_outcome", "_graph", "_capabilities")

    def __init__(
        self,
        substrate: RepositorySubstrate,
        outcome: DiscoveryOutcome,
        graph: RepositoryGraph,
    ) -> None:
        if not isinstance(outcome, DiscoveryOutcome):
            raise RecommendationError(
                "the recommendation engine requires a DiscoveryOutcome",
                received=type(outcome).__name__,
            )
        self._substrate = substrate
        self._outcome = outcome
        self._graph = graph
        self._capabilities = tuple(c for c in outcome.capabilities if c.present_on_disk)

    # -- ranked work list -------------------------------------------------
    def recommend(self) -> tuple[Recommendation, ...]:
        """Return every recommendation, deterministically ranked by derived priority."""
        recommendations: list[Recommendation] = []
        advisory_groups: dict[str, list[Finding]] = {}

        for result in self._outcome.results:
            for finding in result.findings:
                if finding.is_blocking_failure:
                    recommendations.append(self._repair(finding))
                elif finding.is_advisory_failure:
                    advisory_groups.setdefault(finding.code, []).append(finding)

        for code, findings in sorted(advisory_groups.items()):
            recommendations.append(self._aggregate(code, findings))

        if not recommendations:
            recommendations.append(
                Recommendation(
                    action=RecommendationAction.NO_ACTION,
                    subject=self._substrate.config.repository_id,
                    priority=PRIORITY_NONE,
                    rationale="every discovery dimension passed with no advisory findings; "
                    "the repository is consistent, fully registered and fully owned",
                )
            )
        return tuple(
            sorted(
                recommendations,
                key=lambda r: (r.priority, r.action.value, r.subject),
            )
        )

    def _repair(self, finding: Finding) -> Recommendation:
        """A blocking finding always yields an individually-targeted REPAIR."""
        structural = finding.dimension in (
            DiscoveryDimension.DEPENDENCY,
            DiscoveryDimension.CONFLICT,
        )
        priority = PRIORITY_STRUCTURAL_CONTRADICTION if structural else PRIORITY_BLOCKING
        return Recommendation(
            action=RecommendationAction.REPAIR,
            subject=finding.subject,
            priority=priority,
            rationale=f"{finding.code}: {finding.message}",
            target=self._repair_target(finding),
            evidence=(finding.finding_id, finding.code),
        )

    def _repair_target(self, finding: Finding) -> str:
        """Name the concrete place the repair must happen, when the finding implies one."""
        cycle = finding.details.get("cycle")
        if isinstance(cycle, list) and cycle:
            heaviest = self._heaviest_back_edge(tuple(str(node) for node in cycle))
            if heaviest:
                return (
                    f"break {heaviest} — invert it behind an interface owned by the "
                    f"lower-layer capability"
                )
        components = finding.details.get("components")
        if isinstance(components, list) and components:
            return f"{len(components)} cyclic component(s); see the conflict dimension detail"
        for key in ("expected_entry", "expected_option", "claimed_location", "target"):
            value = finding.details.get(key)
            if value:
                return str(value)
        return ""

    def _heaviest_back_edge(self, cycle: tuple[str, ...]) -> str:
        """The highest-weight edge inside a cycle — the cheapest single edge to invert.

        Weight is the number of importing modules, so the heaviest edge is the one whose
        inversion removes the most coupling; ties break on the edge name for determinism.
        """
        members = set(cycle)
        internal = [
            edge
            for edge in self._graph.dependency_edges()
            if edge.source in members and edge.target in members
        ]
        if not internal:
            return ""
        heaviest = sorted(internal, key=lambda e: (-e.weight, e.source, e.target))[0]
        return f"{heaviest.source} -> {heaviest.target} ({heaviest.weight} module(s))"

    def _aggregate(self, code: str, findings: list[Finding]) -> Recommendation:
        """Advisory findings sharing a code share one remedy, so they aggregate."""
        action, priority, remedy = _ADVISORY_REMEDY.get(
            code,
            (
                RecommendationAction.EXTEND,
                PRIORITY_ADVISORY,
                "extend the existing repository to close this finding; do not introduce a "
                "parallel implementation",
            ),
        )
        subjects = sorted({f.subject for f in findings})
        return Recommendation(
            action=action,
            subject=code,
            priority=priority,
            rationale=f"{len(subjects)} subject(s): {remedy}",
            target=subjects[0] if len(subjects) == 1 else f"{len(subjects)} subjects",
            evidence=tuple(subjects[:25]),
        )

    # -- the never-duplicate guard ---------------------------------------
    def advise(self, proposal: str, description: str = "") -> Recommendation:
        """Advise on a *proposed* capability before it is built.

        Returns ``REUSE`` when an existing capability already carries the proposed name,
        ``EXTEND`` when one carries the same terminal name in another layer, ``COMPOSE``
        when one or more existing capabilities substantially match the proposal's
        vocabulary, and ``CREATE`` only when the repository genuinely offers no candidate.

        Raises:
            RecommendationError: if ``proposal`` is empty — advising on nothing would
                silently return a permissive CREATE.
        """
        if not proposal or not proposal.strip():
            raise RecommendationError("a capability proposal must be a non-empty name")
        normalized = proposal.strip()
        existing = {record.name: record for record in self._capabilities}

        if normalized in existing:
            record = existing[normalized]
            return Recommendation(
                action=RecommendationAction.REUSE,
                subject=normalized,
                priority=PRIORITY_DUPLICATION,
                rationale=(
                    f"capability '{normalized}' already exists with reuse directive "
                    f"'{record.reuse_directive}'"
                    + (" and replacement is prohibited" if record.replacement_prohibited else "")
                    + "; reuse it rather than creating a second implementation"
                ),
                target=record.location,
                evidence=(record.capability_id,),
            )

        short = normalized.rsplit(".", 1)[-1]
        same_short = sorted(
            (record for record in self._capabilities if record.name.rsplit(".", 1)[-1] == short),
            key=lambda r: r.name,
        )
        if same_short:
            record = same_short[0]
            return Recommendation(
                action=RecommendationAction.EXTEND,
                subject=normalized,
                priority=PRIORITY_DUPLICATION,
                rationale=(
                    f"'{short}' already exists as '{record.name}'; extend or compose that "
                    f"capability instead of introducing a same-named parallel one"
                ),
                target=record.location,
                evidence=tuple(r.capability_id for r in same_short),
            )

        candidates = self.reuse_candidates(normalized, description)
        if candidates:
            best = candidates[0]
            return Recommendation(
                action=RecommendationAction.COMPOSE,
                subject=normalized,
                priority=PRIORITY_DUPLICATION,
                rationale=(
                    f"{len(candidates)} existing capability/capabilities cover this "
                    f"vocabulary (closest: '{best.capability}', score {best.score}); compose "
                    f"them rather than duplicating their responsibility"
                ),
                target=best.capability,
                evidence=tuple(c.capability for c in candidates),
            )

        root = self._composition_root()
        return Recommendation(
            action=RecommendationAction.CREATE,
            subject=normalized,
            priority=PRIORITY_COMPLETENESS,
            rationale=(
                f"no existing capability matches '{normalized}' by name, terminal name or "
                f"vocabulary across {len(self._capabilities)} capabilities; creation is "
                f"permitted and must compose the existing layers rather than replace them"
            ),
            target=f"{root}/{_snake(short)}",
        )

    def reuse_candidates(
        self, proposal: str, description: str = "", limit: int = 5
    ) -> tuple[ReuseCandidate, ...]:
        """Existing capabilities whose vocabulary overlaps a proposal, best first.

        Similarity is token overlap between the proposal (name plus optional description) and
        each capability's *derived vocabulary* — its name, its self-description, the docstring
        first line of every module it owns, and every public symbol it exports. Using the
        public surface is what makes the guard effective: a capability that exports
        ``discover_gaps`` will be found by someone proposing to build a gap finder, which a
        name-only comparison would miss entirely.
        """
        wanted = _tokens(f"{proposal} {description}")
        if not wanted:
            return ()
        scored: list[ReuseCandidate] = []
        for record in self._capabilities:
            have = self._vocabulary(record.name, record.description)
            if not have:
                continue
            shared = wanted & have
            # Normalize by the smaller vocabulary so a terse capability name is not
            # penalised against a verbose proposal (or the reverse), and require more than
            # a single incidental shared word before offering a reuse target.
            score = round(len(shared) / min(len(wanted), len(have)), 4)
            if len(shared) >= _ADVICE_MIN_SHARED and score >= _ADVICE_MIN_SCORE:
                scored.append(
                    ReuseCandidate(
                        capability=record.name,
                        score=min(score, 1.0),
                        matched_tokens=tuple(sorted(shared)),
                        reuse_directive=record.reuse_directive,
                        replacement_prohibited=record.replacement_prohibited,
                        location=record.location,
                    )
                )
        scored.sort(key=lambda c: (-c.score, c.capability))
        return tuple(scored[:limit])

    def _vocabulary(self, capability: str, description: str) -> set[str]:
        """The full derived vocabulary of a capability (name, docs and public surface)."""
        modules = self._substrate.modules_of(capability)
        parts = [capability, description]
        parts.extend(module.docline for module in modules)
        parts.extend(self._substrate.symbols_of(capability))
        return _tokens(" ".join(parts))

    def _composition_root(self) -> str:
        """The code root a genuinely new capability belongs in: the composing layer.

        Derived from the declared root order — the last declared root is the one that
        composes the others — rather than naming a layer literally.
        """
        roots = self._substrate.config.code_roots
        return roots[-1] if roots else "."

    # -- projections ------------------------------------------------------
    def summary(self, recommendations: tuple[Recommendation, ...]) -> dict[str, Any]:
        """A compact, deterministic projection of the ranked work list."""
        by_action: dict[str, int] = {}
        for recommendation in recommendations:
            by_action[recommendation.action.value] = (
                by_action.get(recommendation.action.value, 0) + 1
            )
        return {
            "total": len(recommendations),
            "by_action": dict(sorted(by_action.items())),
            "highest_priority": min((r.priority for r in recommendations), default=PRIORITY_NONE),
            "next_action": recommendations[0].to_dict() if recommendations else None,
        }


def _tokens(text: str) -> set[str]:
    """Lower-cased, stopword-filtered word tokens, camelCase and snake_case aware.

    A naive trailing-``s`` strip unifies singular and plural forms (``gap``/``gaps``,
    ``conflict``/``conflicts``) so a proposal phrased in one number still matches a
    capability phrased in the other. It is applied to both sides of every comparison, so its
    crudeness is symmetric and harmless.
    """
    raw: set[str] = set()
    for match in _TOKEN_PATTERN.finditer(text.replace(".", " ").replace("_", " ")):
        word = match.group(0)
        parts = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+", word) or [word]
        for part in parts:
            lowered = part.lower()
            if len(lowered) <= 2 or lowered in _STOPWORDS:
                continue
            if len(lowered) > 3 and lowered.endswith("s") and not lowered.endswith("ss"):
                lowered = lowered[:-1]
            if lowered not in _STOPWORDS:
                raw.add(lowered)
    return raw


def _snake(name: str) -> str:
    """Normalize a proposed capability name to the repository's package naming style."""
    stepped = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    return re.sub(r"[^a-z0-9]+", "_", stepped.lower()).strip("_")


def build_recommendations(
    substrate: RepositorySubstrate, outcome: DiscoveryOutcome, graph: RepositoryGraph
) -> tuple[Recommendation, ...]:
    """Convenience: rank the recommendations for a discovery outcome."""
    return RepositoryRecommendationEngine(substrate, outcome, graph).recommend()


__all__ = [
    "PRIORITY_STRUCTURAL_CONTRADICTION",
    "PRIORITY_BLOCKING",
    "PRIORITY_DUPLICATION",
    "PRIORITY_REGISTRATION",
    "PRIORITY_COMPLETENESS",
    "PRIORITY_REUSE_OPPORTUNITY",
    "PRIORITY_ADVISORY",
    "PRIORITY_NONE",
    "ReuseCandidate",
    "RepositoryRecommendationEngine",
    "build_recommendations",
]
