"""UKI Deliverable 10 — Autonomous Knowledge Composition (EPIC-UKDA-002).

Whenever sufficient constitutional knowledge exists, the integration **discovers,
composes, validates, and certifies automatically**, without manual duplication
(``UKI-LAW-009``). Given an
:class:`~engine.knowledge.integration.contracts.ArtifactIntent` whose declared
components already exist and are active, this engine:

    1. confirms sufficiency via the reuse engine (a ``compose`` disposition);
    2. composes a single canonical object from the components (links, not copies);
    3. validates the resulting base with the UKDA validator (fail-closed); and
    4. certifies the composed object with the UKDA certifier.

It reuses the UKDA reuse engine, store, validator, and certifier verbatim — it invents
no new composition model and copies no component knowledge (composition is by
reference, preserving Single Canonical Truth).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.certification import KnowledgeCertifier
from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.integration.contracts import ArtifactIntent, Disposition
from engine.knowledge.integration.errors import CompositionError
from engine.knowledge.integration.reuse import ReuseEngine
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.validation import validate_base

_RATIONALE_REQUIRED: frozenset[KnowledgeKind] = frozenset(
    {KnowledgeKind.DECISION, KnowledgeKind.RULE, KnowledgeKind.PRINCIPLE}
)


@dataclass(frozen=True, slots=True)
class CompositionResult:
    """The outcome of an autonomous composition attempt (Deliverable 10)."""

    intent_id: str
    sufficient: bool
    disposition: Disposition
    components: tuple[str, ...]
    composed: dict[str, Any] | None = None
    validated: bool = False
    certified: bool = False
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "sufficient": self.sufficient,
            "disposition": self.disposition.value,
            "components": list(self.components),
            "composed": self.composed,
            "validated": self.validated,
            "certified": self.certified,
            "reasons": list(self.reasons),
        }


class AutonomousComposer:
    """Autonomously composes/validates/certifies from sufficient knowledge (Deliverable 10)."""

    __slots__ = ("_base", "_reuse", "_certifier")

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._reuse = ReuseEngine(base)
        self._certifier = KnowledgeCertifier()

    def _compose_object(
        self, intent: ArtifactIntent, components: tuple[str, ...], *, lifecycle: Lifecycle
    ) -> CanonicalKnowledgeObject:
        statement = f"{intent.statement} Composed from: {', '.join(components)}."
        rationale = intent.rationale
        if not rationale and intent.kind in _RATIONALE_REQUIRED:
            rationale = (
                "Composed by autonomous constitutional composition from the listed active "
                "components; no new knowledge was authored."
            )
        links = tuple(sorted(set((*intent.knowledge_links, *components))))
        return CanonicalKnowledgeObject.create(
            cko_id=intent.intent_id,
            kind=intent.kind,
            title=intent.title,
            statement=statement,
            rationale=rationale,
            universe=intent.universe,
            authority=intent.authority,
            owner=intent.owner,
            lifecycle=lifecycle,
            version=intent.version,
            dependencies=components,
            knowledge_links=links,
            tags=intent.tags,
        )

    def compose(self, intent: ArtifactIntent) -> CompositionResult:
        """Attempt autonomous composition for ``intent`` (non-raising)."""
        assessment = self._reuse.assess(intent)
        if self._base.has_object(intent.intent_id):
            return CompositionResult(
                intent_id=intent.intent_id,
                sufficient=False,
                disposition=assessment.disposition,
                components=(),
                reasons=("canonical id already exists; composition would duplicate identity",),
            )
        if assessment.disposition is not Disposition.COMPOSE:
            return CompositionResult(
                intent_id=intent.intent_id,
                sufficient=False,
                disposition=assessment.disposition,
                components=(),
                reasons=(
                    "insufficient constitutional knowledge for autonomous composition "
                    f"(disposition={assessment.disposition.value})",
                ),
            )

        components = assessment.targets
        lifecycle = (
            Lifecycle.RATIFIED
            if intent.authority is KnowledgeAuthority.CONSTITUTIONAL
            else Lifecycle.OPERATIONAL
        )
        composed = self._compose_object(intent, components, lifecycle=lifecycle)
        trial = self._base.with_object(composed)
        validation = validate_base(trial)
        certification = self._certifier.certify_object(composed, trial)

        return CompositionResult(
            intent_id=intent.intent_id,
            sufficient=True,
            disposition=Disposition.COMPOSE,
            components=components,
            composed=composed.to_dict(),
            validated=validation.accepted,
            certified=certification.certified,
            reasons=(f"composed and self-verified from {len(components)} active components",),
        )

    def require(self, intent: ArtifactIntent) -> CompositionResult:
        """Compose or raise when constitutional knowledge is insufficient (fail-closed)."""
        result = self.compose(intent)
        if not result.sufficient:
            raise CompositionError(
                "insufficient constitutional knowledge for autonomous composition",
                intent_id=intent.intent_id,
                reasons=list(result.reasons),
            )
        return result


__all__ = ["CompositionResult", "AutonomousComposer"]
