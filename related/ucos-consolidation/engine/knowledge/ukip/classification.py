"""UKIP Part 04 — Knowledge Classification (EPIC-UKDA-003).

Assigns every knowledge unit its six classification facets — kind, authority,
lifecycle, universe, owner, version — using the UKDA controlled vocabularies
verbatim (:mod:`engine.knowledge.model`). No second taxonomy is introduced.

Classification is:

    * **total** (UKIP-LAW-005) — every facet is decided or the unit is rejected.
      There is no "unknown" bucket, because an unclassified record would be
      undiscoverable by classification and therefore an invitation to duplicate it;
    * **deterministic** — the same unit always classifies the same way, with no
      wall-clock, randomness, or dictionary-ordering dependence;
    * **explained** — every facet records *why* it was assigned (the rule id and the
      evidence that triggered it), so a classification is auditable rather than
      opaque;
    * **extensible** — a caller adds rules, it never edits the engine. Rules are
      ordered data (:class:`ClassificationRule`), evaluated in ``(precedence,
      rule_id)`` order, and the first match for a facet wins.

Resolution order for each facet: what the provider explicitly declared, then the
matching rules in precedence order, then the declared fallback. Provider-declared
facets win because a provider that already knows the answer (the canonical store)
must never be second-guessed by a heuristic.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.ukip.contracts import KnowledgeUnit
from engine.knowledge.ukip.errors import ClassificationError

#: The universe assigned when no rule matches — a real universe, never "unknown".
DEFAULT_UNIVERSE = "KNOWLEDGE"

#: The owner assigned when neither the provider nor a rule identifies one. It is a
#: real accountable body, so ownership is always answerable (UKI-LAW-005).
DEFAULT_OWNER = "UCOS-KNOWLEDGE-AUTHORITY"

#: The version assigned to a unit whose provider does not carry one.
DEFAULT_VERSION = "1.0.0"


class Facet(str, Enum):
    """The six facets a complete classification decides."""

    KIND = "kind"
    AUTHORITY = "authority"
    LIFECYCLE = "lifecycle"
    UNIVERSE = "universe"
    OWNER = "owner"
    VERSION = "version"


#: Every facet, in canonical order.
FACETS: tuple[Facet, ...] = tuple(Facet)


@dataclass(frozen=True, slots=True)
class FacetDecision:
    """One decided facet, with the rule and evidence that decided it."""

    facet: Facet
    value: str
    rule_id: str
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "facet": self.facet.value,
            "value": self.value,
            "rule_id": self.rule_id,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class Classification:
    """The complete, explained classification of a single unit."""

    kind: KnowledgeKind
    authority: KnowledgeAuthority
    lifecycle: Lifecycle
    universe: str
    owner: str
    version: str
    decisions: tuple[FacetDecision, ...] = ()

    def decision(self, facet: Facet) -> FacetDecision | None:
        """The recorded decision for one facet."""
        for item in self.decisions:
            if item.facet is facet:
                return item
        return None

    def rule_ids(self) -> tuple[str, ...]:
        """Every rule that contributed, in facet order."""
        return tuple(d.rule_id for d in self.decisions)

    def apply(self, unit: KnowledgeUnit) -> KnowledgeUnit:
        """Return ``unit`` with this classification applied."""
        return unit.with_classification(
            kind=self.kind,
            authority=self.authority,
            lifecycle=self.lifecycle,
            universe=self.universe,
            owner=self.owner,
            version=self.version,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "authority": self.authority.value,
            "lifecycle": self.lifecycle.value,
            "universe": self.universe,
            "owner": self.owner,
            "version": self.version,
            "decisions": [d.to_dict() for d in self.decisions],
        }


@dataclass(frozen=True, slots=True)
class ClassificationRule:
    """A single, data-only classification rule.

    A rule decides exactly one facet when any of its ``terms`` appears in the unit's
    searchable text, or when a provider attribute matches ``attribute``. Keeping a
    rule to one facet means rules compose instead of conflicting: adding a rule can
    never change a facet it does not name.
    """

    rule_id: str
    facet: Facet
    value: str
    terms: tuple[str, ...] = ()
    attribute: tuple[str, str] | None = None
    provider_kinds: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    precedence: int = 100

    @property
    def order_key(self) -> tuple[int, str]:
        return (self.precedence, self.rule_id)

    def matches(self, unit: KnowledgeUnit, haystack: str) -> str:
        """Return the matched evidence, or ``""`` when the rule does not apply."""
        if self.attribute is not None:
            name, expected = self.attribute
            if unit.attribute(name) == expected:
                return f"attribute:{name}={expected}"
            return ""
        if self.provider_kinds and unit.source.kind.value in self.provider_kinds:
            return f"provider-kind:{unit.source.kind.value}"
        for tag in self.tags:
            if tag in unit.tags:
                return f"tag:{tag}"
        for term in self.terms:
            if term in haystack:
                return f"term:{term}"
        return ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "facet": self.facet.value,
            "value": self.value,
            "terms": list(self.terms),
            "attribute": list(self.attribute) if self.attribute else None,
            "provider_kinds": list(self.provider_kinds),
            "tags": list(self.tags),
            "precedence": self.precedence,
        }


def _kind_rule(
    rule_id: str, kind: KnowledgeKind, terms: Sequence[str], *, precedence: int = 100
) -> ClassificationRule:
    return ClassificationRule(
        rule_id=rule_id,
        facet=Facet.KIND,
        value=kind.value,
        terms=tuple(terms),
        precedence=precedence,
    )


#: The built-in rule set, authored once as data, in stable id order.
DEFAULT_RULES: tuple[ClassificationRule, ...] = (
    # -- kind: explicit provider hints win over any textual signal ---------------
    ClassificationRule(
        rule_id="kind-hint-attribute",
        facet=Facet.KIND,
        value=KnowledgeKind.DECISION.value,
        attribute=("kind_hint", "decision"),
        precedence=1,
    ),
    ClassificationRule(
        rule_id="kind-from-decision-log",
        facet=Facet.KIND,
        value=KnowledgeKind.DECISION.value,
        provider_kinds=("decision-log",),
        precedence=2,
    ),
    ClassificationRule(
        rule_id="kind-from-evidence-provider",
        facet=Facet.KIND,
        value=KnowledgeKind.EVIDENCE.value,
        provider_kinds=("evidence",),
        precedence=3,
    ),
    # -- kind: textual signals, most specific first ------------------------------
    _kind_rule(
        "kind-anti-pattern",
        KnowledgeKind.ANTI_PATTERN,
        ("anti-pattern", "antipattern"),
        precedence=10,
    ),
    _kind_rule(
        "kind-best-practice",
        KnowledgeKind.BEST_PRACTICE,
        ("best practice", "best-practice"),
        precedence=11,
    ),
    _kind_rule(
        "kind-principle",
        KnowledgeKind.PRINCIPLE,
        ("principle", "law of", "doctrine"),
        precedence=20,
    ),
    _kind_rule(
        "kind-constraint",
        KnowledgeKind.CONSTRAINT,
        ("constraint", "must not", "may not", "forbidden"),
        precedence=21,
    ),
    _kind_rule("kind-policy", KnowledgeKind.POLICY, ("policy",), precedence=22),
    _kind_rule(
        "kind-standard",
        KnowledgeKind.STANDARD,
        ("standard", "specification"),
        precedence=23,
    ),
    _kind_rule("kind-rule", KnowledgeKind.RULE, ("rule", "shall", "must "), precedence=24),
    _kind_rule(
        "kind-convention", KnowledgeKind.CONVENTION, ("convention", "naming"), precedence=25
    ),
    _kind_rule("kind-pattern", KnowledgeKind.PATTERN, ("pattern",), precedence=26),
    _kind_rule("kind-guideline", KnowledgeKind.GUIDELINE, ("guideline", "should"), precedence=27),
    _kind_rule("kind-exception", KnowledgeKind.EXCEPTION, ("exception", "waiver"), precedence=28),
    _kind_rule("kind-rationale", KnowledgeKind.RATIONALE, ("rationale", "because"), precedence=29),
    _kind_rule("kind-evidence", KnowledgeKind.EVIDENCE, ("evidence", "attestation"), precedence=30),
    _kind_rule("kind-example", KnowledgeKind.EXAMPLE, ("example", "for instance"), precedence=31),
    _kind_rule("kind-reference", KnowledgeKind.REFERENCE, ("reference", "see also"), precedence=32),
    _kind_rule(
        "kind-decision",
        KnowledgeKind.DECISION,
        ("decision", "we adopt", "adopted"),
        precedence=33,
    ),
    # -- authority ---------------------------------------------------------------
    ClassificationRule(
        rule_id="authority-constitutional",
        facet=Facet.AUTHORITY,
        value=KnowledgeAuthority.CONSTITUTIONAL.value,
        terms=("constitution", "constitutional", "ratified law", "inviolable"),
        tags=("constitution",),
        precedence=10,
    ),
    ClassificationRule(
        rule_id="authority-architectural",
        facet=Facet.AUTHORITY,
        value=KnowledgeAuthority.ARCHITECTURAL.value,
        terms=("architecture", "architectural", "design decision"),
        precedence=20,
    ),
    ClassificationRule(
        rule_id="authority-engineering",
        facet=Facet.AUTHORITY,
        value=KnowledgeAuthority.ENGINEERING.value,
        terms=("implementation", "engineering", "runtime", "module"),
        precedence=30,
    ),
    # -- lifecycle ---------------------------------------------------------------
    ClassificationRule(
        rule_id="lifecycle-ratified",
        facet=Facet.LIFECYCLE,
        value=Lifecycle.RATIFIED.value,
        terms=("ratified", "certified", "frozen"),
        precedence=10,
    ),
    ClassificationRule(
        rule_id="lifecycle-operational",
        facet=Facet.LIFECYCLE,
        value=Lifecycle.OPERATIONAL.value,
        terms=("operational", "in production", "live"),
        precedence=20,
    ),
    ClassificationRule(
        rule_id="lifecycle-implemented",
        facet=Facet.LIFECYCLE,
        value=Lifecycle.IMPLEMENTED.value,
        terms=("implemented", "delivered"),
        precedence=30,
    ),
    ClassificationRule(
        rule_id="lifecycle-deprecated",
        facet=Facet.LIFECYCLE,
        value=Lifecycle.DEPRECATED.value,
        terms=("deprecated", "obsolete"),
        precedence=40,
    ),
    # -- universe ----------------------------------------------------------------
    ClassificationRule(
        rule_id="universe-governance",
        facet=Facet.UNIVERSE,
        value="GOVERNANCE",
        terms=("governance", "constitution", "policy", "authority"),
        precedence=10,
    ),
    ClassificationRule(
        rule_id="universe-architecture",
        facet=Facet.UNIVERSE,
        value="ARCHITECTURE",
        terms=("architecture", "component", "layer", "contract"),
        precedence=20,
    ),
    ClassificationRule(
        rule_id="universe-engineering",
        facet=Facet.UNIVERSE,
        value="ENGINEERING",
        terms=("implementation", "code", "module", "engine"),
        precedence=30,
    ),
    ClassificationRule(
        rule_id="universe-operations",
        facet=Facet.UNIVERSE,
        value="OPERATIONS",
        terms=("operations", "deployment", "runtime", "incident"),
        precedence=40,
    ),
)


class KnowledgeClassifier:
    """Deterministic, total, explained classification (UKIP Part 04).

    Extensible without modification: ``extra_rules`` are merged with the built-ins
    and the whole set is re-sorted by ``(precedence, rule_id)``, so a caller can
    both add new facets values and pre-empt built-in rules by precedence alone.
    """

    __slots__ = ("_rules", "_fallback_kind", "_strict")

    def __init__(
        self,
        *,
        extra_rules: Iterable[ClassificationRule] = (),
        rules: Iterable[ClassificationRule] | None = None,
        fallback_kind: KnowledgeKind = KnowledgeKind.FACT,
        strict: bool = False,
    ) -> None:
        base_rules = tuple(rules) if rules is not None else DEFAULT_RULES
        merged = {rule.rule_id: rule for rule in base_rules}
        for rule in extra_rules:
            merged[rule.rule_id] = rule
        self._rules = tuple(sorted(merged.values(), key=lambda r: r.order_key))
        self._fallback_kind = fallback_kind
        self._strict = strict

    @property
    def rules(self) -> tuple[ClassificationRule, ...]:
        return self._rules

    def rules_for(self, facet: Facet) -> tuple[ClassificationRule, ...]:
        return tuple(r for r in self._rules if r.facet is facet)

    @staticmethod
    def _haystack(unit: KnowledgeUnit) -> str:
        parts = [unit.title, unit.statement, unit.rationale, *unit.tags]
        parts.extend(value for _, value in unit.attributes)
        return " ".join(parts).lower()

    def _decide(
        self, unit: KnowledgeUnit, facet: Facet, haystack: str
    ) -> tuple[str, str, str] | None:
        """Return ``(value, rule_id, evidence)`` for the first matching rule."""
        for rule in self._rules:
            if rule.facet is not facet:
                continue
            evidence = rule.matches(unit, haystack)
            if evidence:
                return (rule.value, rule.rule_id, evidence)
        return None

    def classify(self, unit: KnowledgeUnit) -> Classification:
        """Classify one unit totally, or raise in strict mode when signal is absent."""
        haystack = self._haystack(unit)
        decisions: list[FacetDecision] = []

        def resolve(facet: Facet, declared: str | None, fallback: str) -> str:
            if declared:
                decisions.append(FacetDecision(facet, declared, "provider-declared", "provider"))
                return declared
            found = self._decide(unit, facet, haystack)
            if found is not None:
                value, rule_id, evidence = found
                decisions.append(FacetDecision(facet, value, rule_id, evidence))
                return value
            if self._strict:
                raise ClassificationError(
                    "no rule decided a required facet",
                    at=unit.key,
                    facet=facet.value,
                )
            decisions.append(FacetDecision(facet, fallback, "fallback", "no rule matched"))
            return fallback

        kind_value = resolve(
            Facet.KIND, unit.kind.value if unit.kind else None, self._fallback_kind.value
        )
        authority_value = resolve(
            Facet.AUTHORITY,
            unit.authority.value if unit.authority else None,
            KnowledgeAuthority.ADVISORY.value,
        )
        lifecycle_value = resolve(
            Facet.LIFECYCLE,
            unit.lifecycle.value if unit.lifecycle else None,
            Lifecycle.DRAFT.value,
        )
        universe_value = resolve(Facet.UNIVERSE, unit.universe or None, DEFAULT_UNIVERSE)
        owner_value = resolve(Facet.OWNER, unit.owner or None, DEFAULT_OWNER)
        version_value = resolve(Facet.VERSION, unit.version or None, DEFAULT_VERSION)

        return Classification(
            kind=KnowledgeKind.coerce(kind_value, context=unit.key),
            authority=KnowledgeAuthority.coerce(authority_value, context=unit.key),
            lifecycle=Lifecycle.coerce(lifecycle_value, context=unit.key),
            universe=universe_value,
            owner=owner_value,
            version=version_value,
            decisions=tuple(decisions),
        )

    def classify_all(
        self, units: Iterable[KnowledgeUnit]
    ) -> tuple[tuple[KnowledgeUnit, Classification], ...]:
        """Classify many units, returning each unit with the classification applied."""
        results: list[tuple[KnowledgeUnit, Classification]] = []
        for unit in units:
            classification = self.classify(unit)
            results.append((classification.apply(unit), classification))
        return tuple(results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_count": len(self._rules),
            "fallback_kind": self._fallback_kind.value,
            "strict": self._strict,
            "facets": [f.value for f in FACETS],
            "rules": [r.to_dict() for r in self._rules],
        }


def classify_unit(unit: KnowledgeUnit) -> Classification:
    """Convenience: classify a single unit with the default rule set."""
    return KnowledgeClassifier().classify(unit)


__all__ = [
    "DEFAULT_UNIVERSE",
    "DEFAULT_OWNER",
    "DEFAULT_VERSION",
    "Facet",
    "FACETS",
    "FacetDecision",
    "Classification",
    "ClassificationRule",
    "DEFAULT_RULES",
    "KnowledgeClassifier",
    "classify_unit",
]
