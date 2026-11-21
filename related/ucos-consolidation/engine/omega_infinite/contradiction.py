"""UCOS Ω∞ — the Universal Contradiction Engine.

AUTHORITY = NONE (DERIVED TRUTH). This module legislates nothing, certifies nothing and
seals nothing. It compares claims that already exist and reports the pairs that cannot both
be true. Every verdict it produces is a MEASUREMENT of other instruments' assertions.

WHY THIS EXISTS. A repository accumulates instruments faster than it accumulates ways for
them to disagree in public. Coverage says a module is measured; the execution graph says
nothing reaches it. A registry says an artifact is generated; the working tree says it was
edited by hand. An authority chain says a file is governed; no owner resolves. Each
instrument is individually green, and the contradiction between them is carried by nobody —
so it is discovered by a human, late, or never. Ω∞ calls that a SILENT FAILURE, and the
whole point of this module is that there is no such thing here: a contradiction becomes an
open finding the moment two claims meet, whether or not anyone thought to look for it.

WHAT A CONTRADICTION IS. Two claims about ONE subject, from two sources, that cannot both
hold. Not a rule violation — a rule violation is one instrument refusing. A contradiction is
two instruments each satisfied while disagreeing with each other, which is precisely the
condition no single gate can see.

THE THREE THINGS THIS MODULE REFUSES TO DO
  * It refuses to know what a Python file is. Rules read ``Artifact.metadata`` and
    ``Artifact.authority``; a Rust crate, a Terraform plan, a dataset and a trained model
    reach the engine through the same door, because the door is ``Artifact``.
  * It refuses to hold a closed rule list. ``ContradictionRegistry`` is open the way
    ``ArtifactTypeRegistry`` and ``CapabilityRegistry`` are open — a future domain declares
    its rule and the engine admits it with no edit here (UCKP-ART-17).
  * It refuses to be silent. A subject no rule examined is reported as UNEXAMINED, and a
    rule that claimed no subject is reported as IDLE. Both are findings. A contradiction
    engine that quietly examines nothing would pass every repository ever written, which is
    the vacuous-verifier failure this repository already documents.

UNKNOWN CANNOT CERTIFY. ``ContradictionReport.blocks_certification`` is true when any
contradiction stands OR when any subject went unexamined. Certification is a claim about
what is known; a subject nothing looked at is not known to be consistent, and the difference
between "verified consistent" and "never asked" may never be collapsed.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from engine.omega_infinite.artifact import Artifact

__all__ = [
    "Claim",
    "Contradiction",
    "ContradictionError",
    "ContradictionRegistry",
    "ContradictionReport",
    "ContradictionRule",
    "AuthorityOpposition",
    "MetadataOpposition",
    "detect",
    "seed_registry",
]


class ContradictionError(RuntimeError):
    """A malformed rule or registry. Never raised for a contradiction itself.

    A contradiction is DATA — the engine's ordinary output — so raising on one would make
    the first disagreement hide every later one. This is raised only when the engine is
    asked to operate on something that is not a rule.
    """


# ------------------------------------------------------------------------------------- claims


#: The value a dimension carries when an instrument was asked and had no answer. Distinct
#: from absence: "asked, and the answer was nothing" and "nobody asked" are different states,
#: and only the second one is UNEXAMINED.
UNKNOWN_VALUE = "UNKNOWN"


@dataclass(frozen=True, order=True)
class Claim:
    """One instrument's assertion about one artifact, along one dimension.

    ``source`` is load-bearing. A contradiction with no attributable sources is a complaint;
    a contradiction naming the two instruments that disagree is a work item that can be
    routed to an owner without further investigation.
    """

    dimension: str
    value: str
    source: str

    def __post_init__(self) -> None:
        if not self.dimension.strip():
            raise ContradictionError("a claim must name the dimension it speaks about")
        if not self.source.strip():
            raise ContradictionError(f"the {self.dimension!r} claim names no source")

    @property
    def known(self) -> bool:
        return bool(self.value) and self.value != UNKNOWN_VALUE

    def as_record(self) -> dict[str, str]:
        return {"dimension": self.dimension, "value": self.value, "source": self.source}


@dataclass(frozen=True, order=True)
class Contradiction:
    """Two claims about one subject that cannot both hold, and the rule that said so."""

    rule: str
    subject: str
    left: Claim
    right: Claim
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.rule.strip():
            raise ContradictionError("a contradiction must name the rule that found it")
        if not self.subject.strip():
            raise ContradictionError(f"{self.rule} reports a contradiction about no subject")

    def as_record(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "subject": self.subject,
            "left": self.left.as_record(),
            "right": self.right.as_record(),
            "detail": self.detail,
        }

    def __str__(self) -> str:
        return (
            f"{self.rule}: {self.subject} — "
            f"{self.left.source} says {self.left.dimension}={self.left.value}, "
            f"{self.right.source} says {self.right.dimension}={self.right.value}"
            + (f" ({self.detail})" if self.detail else "")
        )


# -------------------------------------------------------------------------------------- rules


@runtime_checkable
class ContradictionRule(Protocol):
    """One question that two instruments can answer incompatibly.

    A rule EXAMINES a subject or it does not, and that is reported separately from whether it
    found anything. The distinction is the whole guard against a vacuous engine: a rule that
    finds nothing because everything is consistent and a rule that finds nothing because it
    never applied to anything look identical in a pass/fail count, and only one of them is
    good news.
    """

    @property
    def identifier(self) -> str:
        """Stable id, e.g. ``OMEGA-C-01``."""

    @property
    def question(self) -> str:
        """The disagreement this rule looks for, in one sentence."""

    def examines(self, artifact: Artifact) -> bool:
        """True when this rule has an opinion about this subject."""

    def contradictions(self, artifact: Artifact) -> Iterable[Contradiction]:
        """Every contradiction this rule finds in a subject it examines."""


@dataclass(frozen=True)
class MetadataOpposition:
    """A declarative rule: one metadata state that obliges another.

    Most contradictions in a governed corpus have this shape — *measured* obliges *in scope*,
    *certified* obliges *verified*, *archived* forbids *executed*. Expressing them as data
    rather than as functions means a new domain adds a row, not a module, and the rule set
    stays auditable by reading it instead of by reading code.
    """

    identifier: str
    question: str
    when_key: str
    when_value: str
    expect_key: str
    expect_value: str
    when_source: str = "declaration"
    expect_source: str = "measurement"
    detail: str = ""
    #: When true the expectation is INVERTED: holding ``expect_value`` is the contradiction.
    #: This is how a rule says "archived artifacts must NOT be executed" without a second class.
    forbid: bool = False

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ContradictionError("a rule must carry an identifier")
        if not self.question.strip():
            raise ContradictionError(f"{self.identifier} asks no question")

    def examines(self, artifact: Artifact) -> bool:
        return artifact.metadata.get(self.when_key) == self.when_value

    def contradictions(self, artifact: Artifact) -> Iterable[Contradiction]:
        if not self.examines(artifact):
            return ()
        observed = artifact.metadata.get(self.expect_key, UNKNOWN_VALUE)
        holds = observed == self.expect_value
        if holds is not self.forbid:
            return ()
        return (
            Contradiction(
                rule=self.identifier,
                subject=artifact.identifier,
                left=Claim(self.when_key, self.when_value, self.when_source),
                right=Claim(self.expect_key, observed, self.expect_source),
                detail=self.detail or self.question,
            ),
        )


@dataclass(frozen=True)
class AuthorityOpposition:
    """Every artifact in a declared state must resolve to an owner.

    Separate from ``MetadataOpposition`` because authority is a FIELD of the artifact and not
    a metadata string: the model gives ownership its own type precisely so that "no owner was
    derived" cannot be spelled forty different ways by forty providers.
    """

    identifier: str
    question: str
    when_key: str
    when_value: str
    when_source: str = "declaration"

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ContradictionError("a rule must carry an identifier")
        if not self.question.strip():
            raise ContradictionError(f"{self.identifier} asks no question")

    def examines(self, artifact: Artifact) -> bool:
        return artifact.metadata.get(self.when_key) == self.when_value

    def contradictions(self, artifact: Artifact) -> Iterable[Contradiction]:
        if not self.examines(artifact) or artifact.authority.resolved:
            return ()
        return (
            Contradiction(
                rule=self.identifier,
                subject=artifact.identifier,
                left=Claim(self.when_key, self.when_value, self.when_source),
                right=Claim(
                    "authority",
                    artifact.authority.owner,
                    artifact.authority.rule or "authority chain",
                ),
                detail=self.question,
            ),
        )


# ----------------------------------------------------------------------------------- registry


class ContradictionRegistry:
    """The open set of rules in force.

    Open in the same sense as every other Ω∞ registry: a rule is DECLARED, never listed in
    this file. A future domain — planetary, interstellar, a data platform, a model registry —
    brings its own rules and needs no edit here, which is UCKP-ART-17 as a mechanism rather
    than as a promise.
    """

    def __init__(self, rules: Iterable[ContradictionRule] = ()) -> None:
        self._rules: dict[str, ContradictionRule] = {}
        for rule in rules:
            self.declare(rule)

    def declare(self, rule: ContradictionRule) -> ContradictionRule:
        """Admit a rule. Re-declaring the same identifier with a different rule is refused."""
        if not isinstance(rule, ContradictionRule):
            raise ContradictionError(
                f"{rule!r} is not a contradiction rule: it must carry identifier, question, "
                "examines() and contradictions()"
            )
        existing = self._rules.get(rule.identifier)
        if existing is not None and existing is not rule:
            raise ContradictionError(
                f"{rule.identifier} is already declared by a different rule — a second "
                "definition of one rule is a competing authority (UCKP-ART-03)"
            )
        self._rules[rule.identifier] = rule
        return rule

    def resolve(self, identifier: str) -> ContradictionRule:
        try:
            return self._rules[identifier]
        except KeyError:
            raise ContradictionError(
                f"no rule named {identifier!r} is declared; declare it before asking for it"
            ) from None

    @property
    def known(self) -> tuple[ContradictionRule, ...]:
        return tuple(self._rules[key] for key in sorted(self._rules))

    def __len__(self) -> int:
        return len(self._rules)


# ------------------------------------------------------------------------------------- report


@dataclass(frozen=True)
class ContradictionReport:
    """What the engine found, and — just as importantly — what it did not look at."""

    contradictions: tuple[Contradiction, ...] = ()
    subjects_examined: int = 0
    subjects_total: int = 0
    unexamined: tuple[str, ...] = ()
    idle_rules: tuple[str, ...] = ()
    rules_applied: tuple[str, ...] = field(default_factory=tuple)

    @property
    def clean(self) -> bool:
        """No contradiction stands. Says nothing about coverage of the rule set."""
        return not self.contradictions

    @property
    def blocks_certification(self) -> bool:
        """UNKNOWN CANNOT CERTIFY.

        A standing contradiction blocks, and so does an unexamined subject: certification
        asserts that a thing is consistent, and nothing that was never examined has earned
        that assertion. An idle rule does NOT block — it is a finding about the rule set's
        relevance, not about any subject's truth.
        """
        return bool(self.contradictions) or bool(self.unexamined)

    def by_rule(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for found in self.contradictions:
            counts[found.rule] = counts.get(found.rule, 0) + 1
        return counts

    def as_record(self) -> dict[str, object]:
        return {
            "clean": self.clean,
            "blocks_certification": self.blocks_certification,
            "subjects_total": self.subjects_total,
            "subjects_examined": self.subjects_examined,
            "unexamined": list(self.unexamined),
            "idle_rules": list(self.idle_rules),
            "rules_applied": list(self.rules_applied),
            "by_rule": self.by_rule(),
            "contradictions": [found.as_record() for found in self.contradictions],
        }


def detect(
    artifacts: Sequence[Artifact],
    registry: ContradictionRegistry,
) -> ContradictionReport:
    """Apply every declared rule to every artifact and report what disagrees.

    Deterministic by construction: rules are applied in identifier order and findings are
    sorted, so two runs over the same population produce byte-identical records and the
    report can be content-addressed (UCKP-ART-13).
    """
    if not isinstance(registry, ContradictionRegistry):
        raise ContradictionError("detect() needs a ContradictionRegistry")

    rules = registry.known
    if not rules:
        raise ContradictionError(
            "no contradiction rule is declared — an engine with no rules reports every "
            "repository consistent, which is the vacuous pass this engine exists to prevent"
        )

    found: list[Contradiction] = []
    examined: set[str] = set()
    claimed: set[str] = set()

    for rule in rules:
        for artifact in artifacts:
            if not rule.examines(artifact):
                continue
            examined.add(artifact.identifier)
            claimed.add(rule.identifier)
            found.extend(rule.contradictions(artifact))

    unexamined = tuple(sorted(a.identifier for a in artifacts if a.identifier not in examined))
    idle = tuple(sorted(r.identifier for r in rules if r.identifier not in claimed))

    return ContradictionReport(
        contradictions=tuple(sorted(found)),
        subjects_examined=len(examined),
        subjects_total=len(artifacts),
        unexamined=unexamined,
        idle_rules=idle,
        rules_applied=tuple(r.identifier for r in rules),
    )


# --------------------------------------------------------------------------------- seed rules


#: The contradictions Ω∞ names in its own directive, expressed as data.
#:
#: THIS IS A SEED, NOT A CEILING. Each row is one row; a domain that needs a different
#: opposition declares it into the registry and the engine is unchanged. The metadata keys
#: below are the vocabulary a provider must attach for a rule to apply — a provider that
#: attaches none simply leaves its artifacts UNEXAMINED, which is reported rather than
#: silently treated as consistent.
_SEED: tuple[ContradictionRule, ...] = (
    MetadataOpposition(
        identifier="OMEGA-C-01",
        question="is every measured artifact inside the declared scope?",
        when_key="measured",
        when_value="true",
        expect_key="in_scope",
        expect_value="true",
        when_source="coverage",
        expect_source="scope derivation",
        detail="measured but outside scope",
    ),
    MetadataOpposition(
        identifier="OMEGA-C-02",
        question="is every certified artifact also verified?",
        when_key="certified",
        when_value="true",
        expect_key="verified",
        expect_value="true",
        when_source="certificate",
        expect_source="verification plane",
        detail="certified but unverified",
    ),
    MetadataOpposition(
        identifier="OMEGA-C-03",
        question="is every verified artifact reproducible?",
        when_key="verified",
        when_value="true",
        expect_key="reproducible",
        expect_value="true",
        when_source="verification plane",
        expect_source="reproduction run",
        detail="verified but unreproducible",
    ),
    MetadataOpposition(
        identifier="OMEGA-C-04",
        question="is every reachable artifact tested?",
        when_key="reachable",
        when_value="true",
        expect_key="tested",
        expect_value="true",
        when_source="execution graph",
        expect_source="test graph",
        detail="reachable but untested",
    ),
    MetadataOpposition(
        identifier="OMEGA-C-05",
        question="is every tested artifact reachable?",
        when_key="tested",
        when_value="true",
        expect_key="reachable",
        expect_value="true",
        when_source="test graph",
        expect_source="execution graph",
        detail="tested but unreachable",
    ),
    MetadataOpposition(
        identifier="OMEGA-C-06",
        question="is any archived artifact still executed?",
        when_key="governance_state",
        when_value="archived",
        expect_key="executed",
        expect_value="true",
        when_source="governance state",
        expect_source="execution plane",
        detail="archived but executed",
        forbid=True,
    ),
    MetadataOpposition(
        identifier="OMEGA-C-07",
        question="is any generated artifact hand-modified?",
        when_key="governance_state",
        when_value="generated",
        expect_key="hand_modified",
        expect_value="true",
        when_source="generated-artifact registry",
        expect_source="working tree",
        detail="generated but modified",
        forbid=True,
    ),
    MetadataOpposition(
        identifier="OMEGA-C-08",
        question="does a ratchet claiming improvement agree with its measurement?",
        when_key="ratchet_direction",
        when_value="improving",
        expect_key="measurement_direction",
        expect_value="improving",
        when_source="ratchet",
        expect_source="measurement",
        detail="ratchet says improving, measurement says worsening",
    ),
    AuthorityOpposition(
        identifier="OMEGA-C-09",
        question="does every governed artifact resolve to an owner?",
        when_key="governance_state",
        when_value="governed",
        when_source="governance state",
    ),
    AuthorityOpposition(
        identifier="OMEGA-C-10",
        question="does every discoverable artifact resolve to an owner?",
        when_key="discoverable",
        when_value="true",
        when_source="discovery",
    ),
)


def seed_registry(extra: Iterable[ContradictionRule] = ()) -> ContradictionRegistry:
    """The ten seed rules, plus anything a caller brings.

    ``extra`` is the extension point that keeps this function from becoming the closed list
    it exists to avoid: a caller adds rules without editing this module.
    """
    registry = ContradictionRegistry(_SEED)
    for rule in extra:
        registry.declare(rule)
    return registry


def from_metadata(
    identifier: str,
    facts: Mapping[str, str],
    *,
    owner: str = "",
    owner_rule: str = "",
) -> Artifact:
    """Build a subject from plain facts, for callers that already hold measurements.

    The engine's input is an ``Artifact``; this saves every adapter from re-deriving how to
    construct one, which is the duplication UCKP-ART-18 forbids.
    """
    from engine.omega_infinite.artifact import Authority, Location

    artifact = Artifact(
        identifier=identifier,
        location=Location(provider="measurement", locator=identifier),
        metadata=dict(facts),
    )
    if owner:
        artifact = artifact.with_authority(Authority(owner=owner, rule=owner_rule))
    return artifact
