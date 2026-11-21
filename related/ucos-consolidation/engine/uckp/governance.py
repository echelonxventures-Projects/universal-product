"""UCKP Layer Zero — Universal Governance (Article 16).

Article 16 requires that every governance decision be discoverable, replayable,
deterministic, auditable, traceable, machine-verifiable and human-understandable. Seven
properties, and a decision that is merely *recorded* has none of them. So a decision here
is a value, not a log line:

    * **discoverable** — every decision is returned by :meth:`GovernanceEngine.decisions`
      and every question by :meth:`GovernanceEngine.questions`.
    * **deterministic / replayable** — a decision's identity is the digest of its inputs
      and outcome, and :meth:`GovernanceEngine.replay` re-asks the question and compares.
      A decision that cannot be re-derived is indistinguishable from an assertion.
    * **auditable / traceable** — the rule, the article it comes from and the digest of
      the universe it was taken against are all inside the decision.
    * **machine-verifiable** — the verdict is a closed string, not prose.
    * **human-understandable** — :meth:`GovernanceDecision.explain` renders the same
      facts as a sentence. Machine-checkable and human-readable are not alternatives;
      Article 16 demands both of every decision.

The rule catalogue is *derived from the law* — one rule per article, generated in
:func:`build_rules`. Restating the articles as a second list of rules would create a
second authority over the same clauses, which Article 3 forbids.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.uckp.canonical import content_hash
from engine.uckp.errors import GovernanceError
from engine.uckp.law import ROOT_LAW, Article
from engine.uckp.registry import UniversalKnowledgeRegistry
from engine.uckp.values import AuditEntry

#: Closed verdict vocabulary. A verdict outside this set is not machine-verifiable.
PERMITTED = "permitted"
REFUSED = "refused"
ANSWERED = "answered"
VERDICTS: tuple[str, ...] = (ANSWERED, PERMITTED, REFUSED)


@dataclass(frozen=True, slots=True)
class GovernanceRule:
    """An executable rule, derived from an article of the root law."""

    rule_id: str
    article_id: str
    statement: str
    invariants: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "article_id": self.article_id,
            "statement": self.statement,
            "invariants": list(self.invariants),
        }


def build_rules() -> tuple[GovernanceRule, ...]:
    """Derive one governance rule per article. Never enumerated by hand."""
    return tuple(
        GovernanceRule(
            rule_id=f"UCKP-RULE-{article.article_id.removeprefix('UCKP-ART-')}",
            article_id=article.article_id,
            statement=article.clause,
            invariants=article.enforces,
        )
        for article in ROOT_LAW.articles
    )


def rule_for_article(article: Article | str) -> GovernanceRule:
    article_id = article.article_id if isinstance(article, Article) else str(article)
    for rule in build_rules():
        if rule.article_id == article_id:
            return rule
    raise GovernanceError("no rule derives from that article", article_id=article_id)


def normalise_arguments(arguments: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Return the canonical, ordered, string-valued form of a question's arguments.

    Every handler reads its arguments through ``str()``, so the string form is the
    whole of what a decision actually depended on. Normalizing once here — rather
    than at each digest site — is what lets a decision carry its own inputs and be
    re-asked from itself.
    """
    return tuple(sorted((str(key), str(value)) for key, value in arguments.items()))


def inputs_digest_of(question: str, subject: str, arguments: tuple[tuple[str, str], ...]) -> str:
    """The digest of everything a decision was asked (pure)."""
    return content_hash(
        {
            "question": question,
            "subject": subject,
            "arguments": dict(arguments),
        }
    )


@dataclass(frozen=True, slots=True)
class GovernanceDecision:
    """A single governance decision, content-addressed and self-explaining.

    The decision carries its own ``arguments``, not merely their digest. A digest
    proves that inputs have not changed but cannot say what they *were*, so a
    decision holding only a digest can be re-asked exclusively by a caller who
    still remembers the question — which makes replay a property of the caller
    rather than of the decision. Article 16 places replayability in the decision,
    so the inputs live here and :meth:`GovernanceEngine.replay` needs nothing else.
    """

    question: str
    subject: str
    verdict: str
    rule_id: str
    article_id: str
    rationale: str
    inputs_digest: str
    universe_seal: str
    findings: tuple[str, ...] = field(default_factory=tuple)
    arguments: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    decision_id: str = ""

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise GovernanceError(
                "verdict is not machine-verifiable", verdict=self.verdict, question=self.question
            )
        if self.inputs_digest != self.derived_inputs_digest():
            raise GovernanceError(
                "recorded inputs do not hash to the recorded inputs digest",
                question=self.question,
                subject=self.subject,
            )

    def derived_inputs_digest(self) -> str:
        """The digest the recorded inputs actually produce (pure)."""
        return inputs_digest_of(self.question, self.subject, self.arguments)

    def _core(self) -> dict[str, object]:
        return {
            "question": self.question,
            "subject": self.subject,
            "verdict": self.verdict,
            "rule_id": self.rule_id,
            "article_id": self.article_id,
            "rationale": self.rationale,
            "inputs_digest": self.inputs_digest,
            "universe_seal": self.universe_seal,
            "findings": list(self.findings),
            "arguments": [list(pair) for pair in self.arguments],
        }

    def derived_decision_id(self) -> str:
        return content_hash(self._core())

    def sealed(self) -> GovernanceDecision:
        from dataclasses import replace

        return replace(self, decision_id=self.derived_decision_id())

    @property
    def permitted(self) -> bool:
        return self.verdict == PERMITTED

    def deterministic(self) -> bool:
        return bool(self.decision_id) and self.decision_id == self.derived_decision_id()

    def explain(self) -> str:
        """The same decision, in a sentence a person can check (Article 16)."""
        findings = f" Findings: {'; '.join(self.findings)}." if self.findings else ""
        return (
            f"{self.question} concerning {self.subject or 'the universe'}: {self.verdict}. "
            f"{self.rationale} Decided under {self.rule_id} ({self.article_id}), against "
            f"universe {self.universe_seal[:16]}.{findings}"
        )

    def audit_entry(self) -> AuditEntry:
        return AuditEntry(
            actor="engine.uckp.governance",
            action=f"decide:{self.question}",
            subject=self.subject or "uckp.universe",
            digest=self.decision_id,
        )

    def to_dict(self) -> dict[str, object]:
        record = self._core()
        record["decision_id"] = self.decision_id
        record["explanation"] = self.explain()
        return record


class GovernanceEngine:
    """Executable governance over the canonical universe."""

    __slots__ = ("_registry", "_decisions")

    def __init__(self, registry: UniversalKnowledgeRegistry) -> None:
        self._registry = registry
        self._decisions: list[GovernanceDecision] = []

    # --- catalogue --------------------------------------------------------------

    def rules(self) -> tuple[GovernanceRule, ...]:
        return build_rules()

    def questions(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers()))

    def _handlers(self) -> Mapping[str, Callable[[str, Mapping[str, Any]], GovernanceDecision]]:
        return {
            "may-create": self._may_create,
            "may-transition": self._may_transition,
            "who-owns": self._who_owns,
            "what-authority": self._what_authority,
            "is-lawful": self._is_lawful,
            "is-projection-authoritative": self._is_projection_authoritative,
        }

    # --- decisions --------------------------------------------------------------

    def decide(self, question: str, subject: str = "", **arguments: Any) -> GovernanceDecision:
        """Answer a governance question. Deterministic, recorded and explainable."""
        handler = self._handlers().get(str(question))
        if handler is None:
            raise GovernanceError("no such governance question", question=str(question))
        decision = handler(str(subject), arguments).sealed()
        self._decisions.append(decision)
        return decision

    def _build(
        self,
        *,
        question: str,
        subject: str,
        verdict: str,
        article_id: str,
        rationale: str,
        arguments: Mapping[str, Any],
        findings: Sequence[str] = (),
    ) -> GovernanceDecision:
        rule = rule_for_article(article_id)
        recorded = normalise_arguments(arguments)
        return GovernanceDecision(
            question=question,
            subject=subject,
            verdict=verdict,
            rule_id=rule.rule_id,
            article_id=article_id,
            rationale=rationale,
            inputs_digest=inputs_digest_of(question, subject, recorded),
            universe_seal=self._registry.seal(),
            findings=tuple(findings),
            arguments=recorded,
        )

    def _may_create(self, subject: str, arguments: Mapping[str, Any]) -> GovernanceDecision:
        """Reuse before create (Article 18): refuse if a canonical home already exists."""
        concept = str(arguments.get("concept", subject))
        definition = str(arguments.get("definition", ""))
        existing = self._registry.locate(concept, definition) if definition else None
        if existing is not None:
            return self._build(
                question="may-create",
                subject=subject or concept,
                verdict=REFUSED,
                article_id="UCKP-ART-18",
                rationale=(
                    "this knowledge already has a canonical home, so it must be reused, "
                    "extended or referenced rather than created again"
                ),
                arguments=arguments,
                findings=(f"canonical home: {existing.ucko_id}",),
            )
        return self._build(
            question="may-create",
            subject=subject or concept,
            verdict=PERMITTED,
            article_id="UCKP-ART-18",
            rationale="no canonical object carries this meaning, so a first home may be created",
            arguments=arguments,
        )

    def _may_transition(self, subject: str, arguments: Mapping[str, Any]) -> GovernanceDecision:
        target = str(arguments.get("target", ""))
        obj = self._registry.get(subject)
        if obj is None:
            return self._build(
                question="may-transition",
                subject=subject,
                verdict=REFUSED,
                article_id="UCKP-ART-12",
                rationale="the subject does not exist, so no transition of it is possible",
                arguments=arguments,
            )
        lifecycle = self._registry.vocabularies().require("uckp.lifecycle-stage")
        lawful = lifecycle.has(target) and lifecycle.can_transition(obj.lifecycle, target)
        return self._build(
            question="may-transition",
            subject=subject,
            verdict=PERMITTED if lawful else REFUSED,
            article_id="UCKP-ART-12",
            rationale=(
                f"{target!r} is a declared successor of {obj.lifecycle!r}"
                if lawful
                else f"{target!r} is not a declared successor of {obj.lifecycle!r}"
            ),
            arguments=arguments,
        )

    def _who_owns(self, subject: str, arguments: Mapping[str, Any]) -> GovernanceDecision:
        obj = self._registry.get(subject)
        return self._build(
            question="who-owns",
            subject=subject,
            verdict=ANSWERED if obj else REFUSED,
            article_id="UCKP-ART-06",
            rationale=(
                f"accountability rests with {obj.ownership.owner}"
                if obj
                else "the subject does not exist"
            ),
            arguments=arguments,
            findings=(obj.ownership.owner,) if obj else (),
        )

    def _what_authority(self, subject: str, arguments: Mapping[str, Any]) -> GovernanceDecision:
        obj = self._registry.get(subject)
        if obj is None:
            return self._build(
                question="what-authority",
                subject=subject,
                verdict=REFUSED,
                article_id="UCKP-ART-01",
                rationale="the subject does not exist",
                arguments=arguments,
            )
        chain = self._registry.authority_of(subject)
        return self._build(
            question="what-authority",
            subject=subject,
            verdict=ANSWERED,
            article_id="UCKP-ART-01",
            rationale=(
                f"it holds {obj.authority.tier} authority, grounded through "
                f"{len(chain)} links in {chain[-1]}"
            ),
            arguments=arguments,
            findings=chain,
        )

    def _is_lawful(self, subject: str, arguments: Mapping[str, Any]) -> GovernanceDecision:
        obj = self._registry.get(subject)
        if obj is None:
            return self._build(
                question="is-lawful",
                subject=subject,
                verdict=REFUSED,
                article_id="UCKP-ART-06",
                rationale="the subject does not exist",
                arguments=arguments,
            )
        findings: list[str] = []
        if not obj.verify_integrity():
            findings.append("seal does not match content")
        if not obj.verify_replay():
            findings.append("replay proof does not hold")
        findings.extend(f"facet absent: {facet.value}" for facet in obj.missing_facets())
        return self._build(
            question="is-lawful",
            subject=subject,
            verdict=PERMITTED if not findings else REFUSED,
            article_id="UCKP-ART-06",
            rationale=(
                "the object answers every facet and its seal and replay proof hold"
                if not findings
                else "the object does not satisfy the facet completeness of Article 6"
            ),
            arguments=arguments,
            findings=findings,
        )

    def _is_projection_authoritative(
        self, subject: str, arguments: Mapping[str, Any]
    ) -> GovernanceDecision:
        """Always refused. Article 4 admits no exception, so neither does this."""
        return self._build(
            question="is-projection-authoritative",
            subject=subject,
            verdict=REFUSED,
            article_id="UCKP-ART-04",
            rationale=(
                "no repository, document, schema, database, interface or future technology "
                "holds independent architectural authority"
            ),
            arguments=arguments,
        )

    # --- audit and replay -------------------------------------------------------

    def decisions(self) -> tuple[GovernanceDecision, ...]:
        return tuple(self._decisions)

    def replay(self, decision: GovernanceDecision) -> bool:
        """Re-ask the recorded question from the decision alone and compare identities.

        Total: a decision carries its own inputs, so replay never needs a caller to
        remember what was asked. That is the difference between a decision that *is*
        replayable and one that merely records a digest of inputs somebody else holds
        (Article 16, UCKP-INV-15).
        """
        handler = self._handlers().get(decision.question)
        if handler is None:  # pragma: no cover - unreachable for a recorded decision
            raise GovernanceError("recorded decision names no known question")
        replayed = handler(decision.subject, dict(decision.arguments)).sealed()
        return replayed.decision_id == decision.decision_id

    def replays_identically(self) -> bool:
        """True iff every recorded decision re-derives itself exactly."""
        return all(self.replay(decision) for decision in self._decisions)

    def audit(self) -> tuple[AuditEntry, ...]:
        return tuple(decision.audit_entry() for decision in self._decisions)

    def to_document(self) -> dict[str, object]:
        return {
            "schema": "ucos-uckp-governance",
            "version": "1.0.0",
            "counts": {
                "rules": len(self.rules()),
                "questions": len(self.questions()),
                "decisions": len(self._decisions),
            },
            "rules": [rule.to_dict() for rule in self.rules()],
            "questions": list(self.questions()),
            "decisions": [decision.to_dict() for decision in self._decisions],
            "replays_identically": self.replays_identically(),
            "audit": [entry.to_dict() for entry in self.audit()],
        }


__all__ = [
    "ANSWERED",
    "PERMITTED",
    "REFUSED",
    "VERDICTS",
    "GovernanceDecision",
    "GovernanceEngine",
    "GovernanceRule",
    "build_rules",
    "inputs_digest_of",
    "normalise_arguments",
    "rule_for_article",
]
