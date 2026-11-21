"""UKIP Part 02 — the Knowledge Constitution (EPIC-UKDA-003).

The binding law of *knowledge intelligence*: what must be true of knowledge itself
once it may arrive from an unbounded number of providers. Authored once, as data.

This constitution is deliberately **subordinate and composed**, not parallel:

    * the founding law it derives from is the Knowledge Once Principle
      (``UCKO-PRIN-0001``), authored in :mod:`engine.knowledge.seed`;
    * the integration laws that govern *how* knowledge is wired into the
      constitutional execution path (``UKI-LAW-001`` … ``UKI-LAW-010``) are
      **reused verbatim** from
      :mod:`engine.knowledge.integration.constitution` via
      :data:`INHERITED_LAWS` — they are referenced, never restated;
    * the laws authored *here* (``UKIP-LAW-*``) are only those the integration
      constitution cannot express, because they concern properties of a knowledge
      *corpus fed by many providers*: provider unboundedness, content-derived
      identity, single canonical home with corroboration, mandatory provenance,
      classification totality, relationship symmetry, and composability.

Each law binds to one or more :class:`KnowledgeCapability` values, so the
capability matrix ("which law governs Discovery?") is derived rather than curated.
:func:`constitution_objects` projects the constitution into the very corpus it
governs, linked to ``UCKO-PRIN-0001`` and ``UCKO-PRIN-UKI-0001``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord, RejectedOption
from engine.knowledge.integration.constitution import (
    INTEGRATION_LAWS,
    INTEGRATION_PRINCIPLE_ID,
    KNOWLEDGE_ONCE_PRINCIPLE,
    IntegrationLaw,
)
from engine.knowledge.integration.constitution import (
    extend_base_with_constitution as extend_base_with_integration_constitution,
)
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

_OWNER = "UCOS-ARCHITECTURE-BOARD"
_REVIEW = "UCOS-CONSTITUTIONAL-REVIEW"
_VERSION = "1.0.0"

#: The canonical identities the Knowledge Constitution authors — exactly once.
KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID = "UCKO-PRIN-UKIP-0001"
KNOWLEDGE_INTELLIGENCE_DECISION_OBJECT_ID = "UCKO-DEC-UKIP-0001"
KNOWLEDGE_INTELLIGENCE_DECISION_RECORD_ID = "UKDA-DEC-0003"

#: The integration laws this constitution inherits rather than re-authoring.
#: Referencing the module-level tuple (not a copy) guarantees that a change to the
#: integration constitution is a change here too — one source, one edit.
INHERITED_LAWS: tuple[IntegrationLaw, ...] = INTEGRATION_LAWS


class KnowledgeCapability(str, Enum):
    """UKIP Part 02 — the eleven capabilities of Knowledge Intelligence."""

    CONSTITUTION = "constitution"
    GRAPH = "graph"
    REGISTRY = "registry"
    DISCOVERY = "discovery"
    ASSIMILATION = "assimilation"
    RELATIONSHIPS = "relationships"
    CLASSIFICATION = "classification"
    PROVENANCE = "provenance"
    EVIDENCE = "evidence"
    VALIDATION = "validation"
    CERTIFICATION = "certification"


#: Every capability, in canonical declaration order.
KNOWLEDGE_CAPABILITIES: tuple[KnowledgeCapability, ...] = tuple(KnowledgeCapability)


@dataclass(frozen=True, slots=True)
class KnowledgeLaw:
    """A single binding law of knowledge intelligence (``UKIP-LAW-*``)."""

    law_id: str
    title: str
    statement: str
    capabilities: tuple[KnowledgeCapability, ...]
    derives_from: tuple[str, ...] = ()

    def governs(self, capability: KnowledgeCapability) -> bool:
        """True iff this law binds the given capability."""
        return capability in self.capabilities

    def to_dict(self) -> dict[str, Any]:
        return {
            "law_id": self.law_id,
            "title": self.title,
            "statement": self.statement,
            "capabilities": [c.value for c in self.capabilities],
            "derives_from": list(self.derives_from),
        }


#: The laws of knowledge intelligence, authored once, in stable id order.
KNOWLEDGE_LAWS: tuple[KnowledgeLaw, ...] = (
    KnowledgeLaw(
        "UKIP-LAW-001",
        "Unlimited Providers",
        "The platform admits an unbounded number of knowledge providers. No provider "
        "is privileged by being built in, no provider count is assumed, and adding a "
        "provider requires no change to the registry, graph, discovery, validation, or "
        "certification engines.",
        (
            KnowledgeCapability.REGISTRY,
            KnowledgeCapability.DISCOVERY,
            KnowledgeCapability.ASSIMILATION,
        ),
        (KNOWLEDGE_ONCE_PRINCIPLE,),
    ),
    KnowledgeLaw(
        "UKIP-LAW-002",
        "Content-Derived Identity",
        "A canonical knowledge identifier is derived from the knowledge substance "
        "itself, never asserted by the provider that supplied it. Two providers "
        "observing the same knowledge independently derive the same identifier.",
        (
            KnowledgeCapability.REGISTRY,
            KnowledgeCapability.CLASSIFICATION,
            KnowledgeCapability.ASSIMILATION,
        ),
        (KNOWLEDGE_ONCE_PRINCIPLE,),
    ),
    KnowledgeLaw(
        "UKIP-LAW-003",
        "Single Canonical Home With Corroboration",
        "Knowledge has exactly one canonical home. A second provider supplying the "
        "same knowledge is recorded as corroborating evidence on the existing record — "
        "never as a second record. Duplication is therefore structurally impossible "
        "rather than merely detected after the fact.",
        (
            KnowledgeCapability.REGISTRY,
            KnowledgeCapability.ASSIMILATION,
            KnowledgeCapability.PROVENANCE,
        ),
        (KNOWLEDGE_ONCE_PRINCIPLE, "UKI-LAW-004"),
    ),
    KnowledgeLaw(
        "UKIP-LAW-004",
        "Mandatory Provenance",
        "Nothing is registered without a complete, hash-chained provenance chain "
        "terminating in a content-addressed source citation. Knowledge whose origin "
        "cannot be reproduced is not knowledge.",
        (
            KnowledgeCapability.PROVENANCE,
            KnowledgeCapability.EVIDENCE,
            KnowledgeCapability.REGISTRY,
        ),
        ("UKI-LAW-006",),
    ),
    KnowledgeLaw(
        "UKIP-LAW-005",
        "Total Classification",
        "Every admitted record carries a decided kind, authority, lifecycle, universe, "
        "owner, and version. Classification is deterministic and total: an "
        "unclassifiable unit is rejected, never admitted as unknown.",
        (KnowledgeCapability.CLASSIFICATION, KnowledgeCapability.REGISTRY),
        ("UKI-LAW-005",),
    ),
    KnowledgeLaw(
        "UKIP-LAW-006",
        "Relationship Symmetry And Closure",
        "Every relationship is navigable in both directions: symmetric relations close "
        "symmetrically, asymmetric relations expose a structural inverse. A "
        "relationship asserted once is answerable from either endpoint.",
        (KnowledgeCapability.RELATIONSHIPS, KnowledgeCapability.GRAPH),
    ),
    KnowledgeLaw(
        "UKIP-LAW-007",
        "Universal Discoverability",
        "Every registered record is reachable by identifier, by content digest, by "
        "classification, by provider, and by ranked search. Knowledge that cannot be "
        "discovered cannot be reused, and unreusable knowledge invites duplication.",
        (KnowledgeCapability.DISCOVERY, KnowledgeCapability.GRAPH),
        ("UKI-LAW-002",),
    ),
    KnowledgeLaw(
        "UKIP-LAW-008",
        "Composability",
        "Knowledge composes: records combine through typed relationships into derived "
        "views without copying their content. Every composition cites its inputs, so a "
        "derived view is never a second source of truth.",
        (
            KnowledgeCapability.RELATIONSHIPS,
            KnowledgeCapability.GRAPH,
            KnowledgeCapability.DISCOVERY,
        ),
        ("UKI-LAW-009",),
    ),
    KnowledgeLaw(
        "UKIP-LAW-009",
        "Canonical Knowledge Only",
        "Only canonical knowledge is registered. Draft, speculative, conversational, "
        "and unratified material is either promoted to canonical form with full "
        "provenance or excluded; it is never held in a parallel non-canonical store.",
        (KnowledgeCapability.REGISTRY, KnowledgeCapability.ASSIMILATION),
        ("UKI-LAW-001",),
    ),
    KnowledgeLaw(
        "UKIP-LAW-010",
        "End-To-End Knowledge Traceability",
        "Every record traces provider -> source -> unit -> classification -> "
        "registration -> relationship -> validation -> certification -> evidence, and "
        "every step is independently verifiable from its recorded digest.",
        (
            KnowledgeCapability.PROVENANCE,
            KnowledgeCapability.EVIDENCE,
            KnowledgeCapability.VALIDATION,
            KnowledgeCapability.CERTIFICATION,
        ),
        ("UKI-LAW-006",),
    ),
    KnowledgeLaw(
        "UKIP-LAW-011",
        "Fail Closed On Knowledge Defects",
        "A duplicate home, a broken provenance chain, an unresolved relationship, an "
        "unclassified record, or an integrity failure blocks certification. Knowledge "
        "intelligence never reports a partial verdict as success.",
        (
            KnowledgeCapability.VALIDATION,
            KnowledgeCapability.CERTIFICATION,
            KnowledgeCapability.EVIDENCE,
        ),
        ("UKI-LAW-010",),
    ),
    KnowledgeLaw(
        "UKIP-LAW-012",
        "Constitution In Corpus",
        "The Knowledge Constitution is itself canonical knowledge inside the corpus it "
        "governs, subordinate to the Knowledge Once Principle, and is registered under "
        "the same rules as everything else.",
        (KnowledgeCapability.CONSTITUTION,),
        (KNOWLEDGE_ONCE_PRINCIPLE, INTEGRATION_PRINCIPLE_ID),
    ),
)


@dataclass(frozen=True, slots=True)
class KnowledgeConstitution:
    """The authored-once Knowledge Constitution: capabilities, laws, inheritance."""

    capabilities: tuple[KnowledgeCapability, ...]
    laws: tuple[KnowledgeLaw, ...]
    inherited: tuple[IntegrationLaw, ...]

    def law(self, law_id: str) -> KnowledgeLaw | None:
        """Look up an authored law by id (inherited laws are not shadowed here)."""
        for law in self.laws:
            if law.law_id == law_id:
                return law
        return None

    def laws_for(self, capability: KnowledgeCapability) -> tuple[KnowledgeLaw, ...]:
        """Every authored law binding the given capability."""
        return tuple(law for law in self.laws if law.governs(capability))

    def capability_matrix(self) -> dict[str, tuple[str, ...]]:
        """Derived capability -> governing law ids (never curated by hand)."""
        return {
            capability.value: tuple(law.law_id for law in self.laws_for(capability))
            for capability in self.capabilities
        }

    def ungoverned_capabilities(self) -> tuple[KnowledgeCapability, ...]:
        """Capabilities no authored law binds — a constitutional gap, if any."""
        return tuple(c for c in self.capabilities if not self.laws_for(c))

    @property
    def is_complete(self) -> bool:
        """True iff every capability is bound by at least one authored law."""
        return not self.ungoverned_capabilities()

    def to_dict(self) -> dict[str, Any]:
        return {
            "capabilities": [c.value for c in self.capabilities],
            "laws": [law.to_dict() for law in self.laws],
            "inherited_laws": [law.law_id for law in self.inherited],
            "capability_matrix": {k: list(v) for k, v in self.capability_matrix().items()},
            "complete": self.is_complete,
        }


def knowledge_constitution() -> KnowledgeConstitution:
    """Return the single, authored-once Knowledge Constitution."""
    return KnowledgeConstitution(
        capabilities=KNOWLEDGE_CAPABILITIES,
        laws=KNOWLEDGE_LAWS,
        inherited=INHERITED_LAWS,
    )


def _laws_statement() -> str:
    return " ".join(f"{law.law_id}: {law.title}." for law in KNOWLEDGE_LAWS)


def constitution_objects() -> (
    tuple[tuple[CanonicalKnowledgeObject, ...], tuple[DecisionRecord, ...]]
):
    """Project the Knowledge Constitution as canonical knowledge (UKIP-LAW-012).

    Additive: the caller merges the result into a base explicitly, and the frozen
    UKDA seed is never mutated.
    """
    principle = CanonicalKnowledgeObject.create(
        cko_id=KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID,
        kind=KnowledgeKind.PRINCIPLE,
        title="Universal Knowledge Intelligence",
        statement=(
            "Knowledge may arrive from an unbounded number of providers, but exists "
            "canonically exactly once: identity is derived from the knowledge substance, "
            "the first admission establishes the single canonical home, and every further "
            "provider supplying the same knowledge corroborates that home instead of "
            "creating a second record. Every record is classified, provenance-chained, "
            "related, discoverable, and composable. " + _laws_statement()
        ),
        rationale=(
            "Detecting duplicates after they are authored is remediation, not prevention. "
            "Deriving identity from content and admitting additional providers as "
            "corroboration makes duplicate knowledge structurally unrepresentable, which "
            "is the only form of the Knowledge Once Principle that survives an unbounded "
            "number of knowledge sources."
        ),
        universe="GOVERNANCE",
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        owner=_OWNER,
        lifecycle=Lifecycle.RATIFIED,
        version=_VERSION,
        dependencies=(KNOWLEDGE_ONCE_PRINCIPLE, INTEGRATION_PRINCIPLE_ID),
        knowledge_links=(KNOWLEDGE_ONCE_PRINCIPLE, INTEGRATION_PRINCIPLE_ID),
        tags=("constitution", "knowledge-intelligence"),
    )

    decision_record = DecisionRecord.create(
        decision_id=KNOWLEDGE_INTELLIGENCE_DECISION_RECORD_ID,
        title="Adopt Universal Knowledge Intelligence",
        problem_statement=(
            "The canonical knowledge store could only be fed by hand-authored records in "
            "two fixed files. Knowledge held in documents, decision logs, registries, "
            "code, and evidence had no admission path, so it was either re-authored by "
            "hand (risking duplication) or left unassimilated (losing traceability)."
        ),
        context=(
            "UKDA (EPIC-UKDA) owns canonical knowledge and UKI (EPIC-UKDA-002) wires it "
            "into the constitutional execution path, but neither defines how knowledge "
            "enters the corpus from an arbitrary, growing set of sources."
        ),
        objective=(
            "Admit knowledge from an unbounded number of providers while keeping exactly "
            "one canonical record per distinct piece of knowledge, with complete "
            "provenance, classification, relationships, validation, and certification."
        ),
        chosen_architecture=(
            "An additive engine.knowledge.ukip layer: a provider protocol with an "
            "unbounded provider registry; content-derived knowledge identity reusing the "
            "UKDA semantic hash verbatim; a Knowledge Registry whose second admission of "
            "identical knowledge becomes corroboration on the existing canonical home; "
            "hash-chained provenance; deterministic total classification; a relationship "
            "algebra and graph projected over the UKDA Part 05 graph; discovery; a "
            "fail-closed validation suite; certification; and sealed evidence."
        ),
        rationale=(
            "Reusing the UKDA semantic hash as the duplication key means UKIP cannot "
            "develop a second, drifting notion of 'the same knowledge'. Making the "
            "canonical home a function of content rather than of provider order removes "
            "the only mechanism by which multiple providers could duplicate knowledge."
        ),
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        owner=_OWNER,
        lifecycle=Lifecycle.RATIFIED,
        version=_VERSION,
        review_authority=_REVIEW,
        supersession_rules=(
            "Superseded only by a ratified successor that preserves content-derived "
            "identity, the single canonical home, and mandatory provenance."
        ),
        alternatives=(
            "Hand-author every record into the canonical store.",
            "Give each provider its own store and reconcile periodically.",
            "Admit all providers into one registry keyed by derived content identity (chosen).",
        ),
        evaluation_criteria=(
            "unlimited providers",
            "zero duplicate knowledge",
            "complete provenance",
            "deterministic classification",
            "composability",
        ),
        tradeoffs=(
            "Providers lose the ability to name their own canonical ids in exchange for "
            "structurally impossible duplication.",
            "Classification must be total, so a provider supplying insufficient signal "
            "is rejected rather than admitted as unknown.",
        ),
        rejected_options=(
            RejectedOption(
                "Hand-authored records only",
                "Cannot scale to many sources and makes re-authoring — hence "
                "duplication — the normal way knowledge enters the corpus.",
            ),
            RejectedOption(
                "Per-provider stores with periodic reconciliation",
                "Creates parallel sources of truth between reconciliations, which is a "
                "direct violation of the Knowledge Once Principle.",
            ),
            RejectedOption(
                "Provider-asserted canonical identifiers",
                "Two providers observing the same knowledge would assert different ids, "
                "reintroducing duplicates the registry could not recognise.",
            ),
        ),
        consequences=(
            "Knowledge enters the corpus only through a provider with a citable source.",
            "The number of providers is unbounded and requires no engine change.",
            "Duplicate knowledge is corroboration, not a second record.",
        ),
        risks=(
            "A weak provider could contribute low-quality units at scale.",
            "Content-derived ids change if the knowledge substance is edited.",
        ),
        mitigations=(
            "Total classification plus the fail-closed validation suite rejects "
            "insufficient units at admission.",
            "Supersession links the old identity to the new one, so edits are traceable "
            "rather than silent.",
        ),
        dependencies=(
            KNOWLEDGE_ONCE_PRINCIPLE,
            INTEGRATION_PRINCIPLE_ID,
            "UKDA-DEC-0001",
            "UKDA-DEC-0002",
        ),
        impact_analysis=(
            "Establishes the admission path every future knowledge source uses; the UKDA "
            "store, graph, intelligence, validation, and certification engines are reused "
            "unchanged."
        ),
        implementation_guidance=(
            "Register providers on engine.knowledge.ukip.providers.ProviderRegistry; run "
            "engine.knowledge.ukip.assimilation.KnowledgeAssimilator; validate and certify "
            "the resulting registry; emit sealed evidence."
        ),
        validation_strategy=(
            "engine.knowledge.ukip.validation default suite (fail-closed), composed with "
            "the UKDA engine.knowledge.validation suite over the projected base."
        ),
        certification_requirements=(
            "every-record-provenanced",
            "every-record-classified",
            "no-duplicate-home",
            "relationships-resolved",
            "discoverable",
        ),
    )

    decision_object = CanonicalKnowledgeObject.create(
        cko_id=KNOWLEDGE_INTELLIGENCE_DECISION_OBJECT_ID,
        kind=KnowledgeKind.DECISION,
        title="Adopt Universal Knowledge Intelligence",
        statement=(
            "Ratified adoption of the Universal Knowledge Intelligence Platform "
            "(EPIC-UKDA-003). See the linked decision record for full rationale."
        ),
        rationale=(
            "Recorded once; all explanation lives in "
            + KNOWLEDGE_INTELLIGENCE_DECISION_RECORD_ID
            + "."
        ),
        universe="GOVERNANCE",
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        owner=_OWNER,
        lifecycle=Lifecycle.RATIFIED,
        version=_VERSION,
        dependencies=(KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID,),
        decision_links=(KNOWLEDGE_INTELLIGENCE_DECISION_RECORD_ID,),
        tags=("constitution", "knowledge-intelligence"),
    )

    return (principle, decision_object), (decision_record,)


def extend_base_with_knowledge_constitution(base: KnowledgeBase) -> KnowledgeBase:
    """Return a new base with the Knowledge Constitution merged in (idempotent).

    The UKIP principle is subordinate to the UKI integration principle, so this
    merges the integration constitution first — by delegating to UKI's own extender
    rather than re-authoring its objects. A caller therefore cannot end up with a
    UKIP constitution whose declared parent is missing.
    """
    result = extend_base_with_integration_constitution(base)
    objects, decisions = constitution_objects()
    for obj in objects:
        if not result.has_object(obj.cko_id):
            result = result.with_object(obj)
    for dec in decisions:
        if not result.has_decision(dec.decision_id):
            result = result.with_decision(dec)
    return result


__all__ = [
    "KNOWLEDGE_ONCE_PRINCIPLE",
    "KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID",
    "KNOWLEDGE_INTELLIGENCE_DECISION_OBJECT_ID",
    "KNOWLEDGE_INTELLIGENCE_DECISION_RECORD_ID",
    "INHERITED_LAWS",
    "KnowledgeCapability",
    "KNOWLEDGE_CAPABILITIES",
    "KnowledgeLaw",
    "KNOWLEDGE_LAWS",
    "KnowledgeConstitution",
    "knowledge_constitution",
    "constitution_objects",
    "extend_base_with_knowledge_constitution",
]
