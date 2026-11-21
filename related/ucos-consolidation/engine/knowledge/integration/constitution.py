"""UKI Deliverable 1 — Universal Knowledge Integration Constitution (EPIC-UKDA-002).

Defines *how* the Universal Knowledge & Decision Architecture (UKDA) integrates with
every UCOS constitutional layer, as **data, authored once**. It enumerates:

    * :data:`CANONICAL_LAYERS` — every layer UKDA is the knowledge backbone for
      (constitution, governance, registry, ... deployment);
    * :data:`INTEGRATION_LAWS` — the binding laws (``UKI-LAW-*``) every future
      capability obeys: single canonical truth, discover-before-create,
      reuse-before-create, no-duplication, canonical ownership, end-to-end
      traceability, governance-grounded-in-knowledge, register-without-duplication,
      autonomous-composition-when-sufficient, and fail-closed;
    * :data:`CONSTITUTIONAL_SEQUENCE` — the ordered execution path each capability
      follows (Discover -> ... -> Evolve).

The constitution is also projected as **canonical knowledge** by
:func:`constitution_objects` so it lives inside the very corpus it governs (Single
Canonical Truth) — linked to, and subordinate to, the founding Knowledge Once
Principle (``UCKO-PRIN-0001``) rather than duplicating it. The projection is additive:
it never mutates the frozen UKDA seed; callers merge it into a base explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord, RejectedOption
from engine.knowledge.integration.contracts import (
    CANONICAL_LAYERS,
    CONSTITUTIONAL_SEQUENCE,
    ConstitutionalLayer,
    SequenceStage,
)
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

_OWNER = "UCOS-ARCHITECTURE-BOARD"
_REVIEW = "UCOS-CONSTITUTIONAL-REVIEW"
_VERSION = "1.0.0"

#: The founding principle every integration law is subordinate to.
KNOWLEDGE_ONCE_PRINCIPLE = "UCKO-PRIN-0001"

#: The canonical identities the integration constitution authors (once).
INTEGRATION_PRINCIPLE_ID = "UCKO-PRIN-UKI-0001"
INTEGRATION_DECISION_OBJECT_ID = "UCKO-DEC-UKI-0001"
INTEGRATION_DECISION_RECORD_ID = "UKDA-DEC-0002"


@dataclass(frozen=True, slots=True)
class IntegrationLaw:
    """A single binding constitutional-integration law (``UKI-LAW-*``)."""

    law_id: str
    title: str
    statement: str
    stage: SequenceStage
    layers: tuple[ConstitutionalLayer, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "law_id": self.law_id,
            "title": self.title,
            "statement": self.statement,
            "stage": self.stage.value,
            "layers": [layer.value for layer in self.layers],
        }


_ALL = CANONICAL_LAYERS


#: The binding integration laws, authored once, in stable id order (Deliverable 1).
INTEGRATION_LAWS: tuple[IntegrationLaw, ...] = (
    IntegrationLaw(
        "UKI-LAW-001",
        "Single Canonical Truth",
        "Every constitutional artifact has exactly one canonical source in the UKDA; "
        "no layer may hold a second, parallel source of the same knowledge.",
        SequenceStage.ANALYZE,
        _ALL,
    ),
    IntegrationLaw(
        "UKI-LAW-002",
        "Discover Before Create",
        "Deterministic discovery of existing constitutional knowledge is mandatory "
        "before any creation, implementation, validation, certification, or governance "
        "decision. Discovery may not be bypassed.",
        SequenceStage.DISCOVER,
        _ALL,
    ),
    IntegrationLaw(
        "UKI-LAW-003",
        "Reuse Before Create",
        "An artifact is reused, extended, or composed from existing knowledge whenever "
        "that knowledge suffices. Creation is the last resort and must be justified by a "
        "reuse determination.",
        SequenceStage.REUSE,
        _ALL,
    ),
    IntegrationLaw(
        "UKI-LAW-004",
        "No Duplication",
        "The integration fails closed on semantic duplicates, overlapping ownership, "
        "conflicting capabilities, redundant universes, and parallel implementations.",
        SequenceStage.ANALYZE,
        _ALL,
    ),
    IntegrationLaw(
        "UKI-LAW-005",
        "Canonical Ownership",
        "Every artifact declares exactly one owner, one canonical identifier, one "
        "constitutional authority, and one lifecycle. Ambiguous or absent ownership is "
        "rejected.",
        SequenceStage.ANALYZE,
        _ALL,
    ),
    IntegrationLaw(
        "UKI-LAW-006",
        "End-to-End Traceability",
        "Every artifact is deterministically traceable Constitution -> Universe -> "
        "Capability -> Implementation -> Validation -> Certification -> Evidence -> "
        "Deployment -> Runtime.",
        SequenceStage.EVOLVE,
        _ALL,
    ),
    IntegrationLaw(
        "UKI-LAW-007",
        "Governance Grounded In Knowledge",
        "Every governance decision references canonical knowledge, constitutional laws, "
        "prior decisions, and evidence. Ungrounded governance is rejected.",
        SequenceStage.ANALYZE,
        (ConstitutionalLayer.GOVERNANCE, ConstitutionalLayer.CONSTITUTION),
    ),
    IntegrationLaw(
        "UKI-LAW-008",
        "Registration Without Duplication",
        "Universes, capabilities, relationships, dependencies, decisions, evidence, and "
        "certifications are registered exactly once; re-registration of an existing "
        "canonical entity is a no-op, never a duplicate.",
        SequenceStage.REGISTER,
        (ConstitutionalLayer.REGISTRY, ConstitutionalLayer.KNOWLEDGE),
    ),
    IntegrationLaw(
        "UKI-LAW-009",
        "Autonomous Composition When Sufficient",
        "When sufficient constitutional knowledge exists, the integration discovers, "
        "composes, validates, and certifies automatically, without manual duplication.",
        SequenceStage.COMPOSE,
        _ALL,
    ),
    IntegrationLaw(
        "UKI-LAW-010",
        "Fail Closed",
        "Any constitutional-integration violation blocks the operation; nothing proceeds "
        "past a detected duplication, ownership, discovery, reuse, or traceability defect.",
        SequenceStage.CREATE,
        _ALL,
    ),
)


@dataclass(frozen=True, slots=True)
class IntegrationConstitution:
    """The authored-once integration constitution: layers, laws, and sequence."""

    layers: tuple[ConstitutionalLayer, ...]
    laws: tuple[IntegrationLaw, ...]
    sequence: tuple[SequenceStage, ...]

    def law(self, law_id: str) -> IntegrationLaw | None:
        for law in self.laws:
            if law.law_id == law_id:
                return law
        return None

    def laws_for_stage(self, stage: SequenceStage) -> tuple[IntegrationLaw, ...]:
        """Every law bound to a given execution-path stage."""
        return tuple(law for law in self.laws if law.stage is stage)

    def covers_layer(self, layer: ConstitutionalLayer) -> bool:
        """True iff at least one law governs the given canonical layer."""
        return any(layer in law.layers for law in self.laws)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layers": [layer.value for layer in self.layers],
            "laws": [law.to_dict() for law in self.laws],
            "sequence": [stage.value for stage in self.sequence],
        }


def integration_constitution() -> IntegrationConstitution:
    """Return the single, authored-once integration constitution (Deliverable 1)."""
    return IntegrationConstitution(
        layers=CANONICAL_LAYERS,
        laws=INTEGRATION_LAWS,
        sequence=CONSTITUTIONAL_SEQUENCE,
    )


def _laws_statement() -> str:
    return " ".join(f"{law.law_id}: {law.title}." for law in INTEGRATION_LAWS)


def constitution_objects() -> (
    tuple[tuple[CanonicalKnowledgeObject, ...], tuple[DecisionRecord, ...]]
):
    """Project the integration constitution as canonical knowledge (authored once).

    Returns the canonical objects and decision records that record EPIC-UKDA-002 in
    the corpus it governs, each subordinate to the Knowledge Once Principle. The
    result is well-formed: it passes UKDA validation and certification when merged
    into a base that already contains ``UCKO-PRIN-0001``.
    """
    principle = CanonicalKnowledgeObject.create(
        cko_id=INTEGRATION_PRINCIPLE_ID,
        kind=KnowledgeKind.PRINCIPLE,
        title="Universal Constitutional Knowledge Integration",
        statement=(
            "The UKDA is the mandatory constitutional knowledge backbone of every UCOS "
            "layer. Every capability first consults canonical knowledge before creating "
            "or modifying an artifact, and follows the constitutional sequence "
            "discover -> analyze -> reuse -> extend -> compose -> create -> validate -> "
            "certify -> register -> evolve. " + _laws_statement()
        ),
        rationale=(
            "An isolated knowledge engine cannot prevent drift; only a knowledge backbone "
            "wired into the constitutional execution path structurally guarantees zero "
            "duplication, single canonical truth, and deterministic traceability."
        ),
        universe="GOVERNANCE",
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        owner=_OWNER,
        lifecycle=Lifecycle.RATIFIED,
        version=_VERSION,
        dependencies=(KNOWLEDGE_ONCE_PRINCIPLE,),
        knowledge_links=(KNOWLEDGE_ONCE_PRINCIPLE,),
        tags=("constitution", "integration"),
    )

    decision_record = DecisionRecord.create(
        decision_id=INTEGRATION_DECISION_RECORD_ID,
        title="Adopt Universal Constitutional Knowledge Integration",
        problem_statement=(
            "The UKDA existed as an isolated engine; artifacts across UCOS layers could "
            "still be created without consulting canonical knowledge, permitting drift, "
            "duplication, and untraceable ownership."
        ),
        context=(
            "UCOS Ω∞ spans many canonical layers (constitution, governance, registry, "
            "runtime, intelligence, ... deployment), each of which produces artifacts "
            "that must remain a single source of truth."
        ),
        objective=(
            "Make the UKDA the mandatory knowledge backbone so every future capability "
            "discovers, reuses, and traces canonical knowledge before creating or "
            "modifying any artifact."
        ),
        chosen_architecture=(
            "An additive engine.knowledge.integration layer providing discovery, "
            "ownership, dependency, reuse, duplicate-prevention, traceability, governance, "
            "registration, and autonomous-composition engines bound by a single "
            "fail-closed constitutional execution path — reusing the UKDA store, graph, "
            "intelligence, validation, and certification verbatim."
        ),
        rationale=(
            "Wiring the backbone into the execution path — rather than adding features — "
            "is the only design that enforces the Knowledge Once Principle at the point of "
            "creation while preserving complete backward compatibility."
        ),
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        owner=_OWNER,
        lifecycle=Lifecycle.RATIFIED,
        version=_VERSION,
        review_authority=_REVIEW,
        supersession_rules=(
            "Superseded only by a ratified successor that preserves the Knowledge Once "
            "Principle and the fail-closed constitutional execution path."
        ),
        alternatives=(
            "Leave the UKDA as an isolated, opt-in engine.",
            "Duplicate discovery/ownership logic into each layer.",
            "Wire the UKDA into a single constitutional execution path (chosen).",
        ),
        evaluation_criteria=(
            "zero duplication",
            "single canonical truth",
            "deterministic traceability",
            "backward compatibility",
        ),
        tradeoffs=(
            "Every creation path gains a mandatory discovery/reuse gate in exchange for "
            "structural drift prevention.",
        ),
        rejected_options=(
            RejectedOption(
                "Isolated opt-in engine",
                "Does not prevent artifacts from being created without consulting "
                "canonical knowledge; drift remains possible.",
            ),
            RejectedOption(
                "Per-layer duplicated logic",
                "Violates the Knowledge Once Principle by forking discovery/ownership "
                "into many parallel implementations.",
            ),
        ),
        consequences=(
            "Every future artifact is discovered, screened, and traced before creation.",
            "Governance decisions must reference canonical knowledge.",
        ),
        risks=("Additional gate on every creation path.",),
        mitigations=(
            "The gate is deterministic, reuses the UKDA engines, and fails closed only on "
            "genuine violations.",
        ),
        dependencies=(KNOWLEDGE_ONCE_PRINCIPLE, "UKDA-DEC-0001"),
        impact_analysis=(
            "Establishes the constitutional execution path consumed by every future "
            "universe, capability, and governance process."
        ),
        implementation_guidance=(
            "Route every artifact intent through engine.knowledge.integration.pipeline; "
            "author accepted intents once; register without duplication."
        ),
        validation_strategy="engine.knowledge.validation default suite (fail-closed).",
        certification_requirements=(
            "complete",
            "authority-defined",
            "owner-identified",
            "rationale-present",
        ),
    )

    decision_object = CanonicalKnowledgeObject.create(
        cko_id=INTEGRATION_DECISION_OBJECT_ID,
        kind=KnowledgeKind.DECISION,
        title="Adopt Universal Constitutional Knowledge Integration",
        statement=(
            "Ratified adoption of the Universal Constitutional Knowledge Integration "
            "(EPIC-UKDA-002). See the linked decision record for full rationale."
        ),
        rationale="Recorded once; all explanation lives in " + INTEGRATION_DECISION_RECORD_ID + ".",
        universe="GOVERNANCE",
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        owner=_OWNER,
        lifecycle=Lifecycle.RATIFIED,
        version=_VERSION,
        dependencies=(INTEGRATION_PRINCIPLE_ID,),
        decision_links=(INTEGRATION_DECISION_RECORD_ID,),
        tags=("constitution", "integration"),
    )

    return (principle, decision_object), (decision_record,)


def extend_base_with_constitution(base: KnowledgeBase) -> KnowledgeBase:
    """Return a new base with the integration constitution merged in (idempotent).

    Additive and duplication-safe: objects/decisions already present (by identity) are
    not re-authored, so merging twice yields the same base and never raises a duplicate.
    """
    objects, decisions = constitution_objects()
    result = base
    for obj in objects:
        if not result.has_object(obj.cko_id):
            result = result.with_object(obj)
    for dec in decisions:
        if not result.has_decision(dec.decision_id):
            result = result.with_decision(dec)
    return result


__all__ = [
    "KNOWLEDGE_ONCE_PRINCIPLE",
    "INTEGRATION_PRINCIPLE_ID",
    "INTEGRATION_DECISION_OBJECT_ID",
    "INTEGRATION_DECISION_RECORD_ID",
    "IntegrationLaw",
    "INTEGRATION_LAWS",
    "IntegrationConstitution",
    "integration_constitution",
    "constitution_objects",
    "extend_base_with_constitution",
]
