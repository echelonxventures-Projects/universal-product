"""UKDA — Canonical seed knowledge (EPIC-UKDA).

The founding, authored-once canonical knowledge of the Universal Knowledge &
Decision Architecture. It ratifies the **Knowledge Once Principle** and records the
constitutional/architectural principles the repository already lives by (the frozen
corpus is read-only, the core is vendor-neutral/stdlib-only, all interaction is via
versioned contracts, and generation is deterministic), plus the founding decisions
that establish the architecture.

This module is the single place these objects are authored; every handbook,
bootstrap digest, and derived document is generated from
:func:`build_seed_base`. The seed is designed to pass knowledge validation and
certification with a clean bill of health, so it doubles as the reference example
of a well-formed canonical base.
"""

from __future__ import annotations

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord, RejectedOption
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

_OWNER = "UCOS-ARCHITECTURE-BOARD"
_REVIEW = "UCOS-CONSTITUTIONAL-REVIEW"
_VERSION = "1.0.0"


def _principle(
    cko_id: str,
    title: str,
    statement: str,
    rationale: str,
    *,
    authority: KnowledgeAuthority,
    universe: str,
    knowledge_links: tuple[str, ...] = (),
    dependencies: tuple[str, ...] = (),
) -> CanonicalKnowledgeObject:
    return CanonicalKnowledgeObject.create(
        cko_id=cko_id,
        kind=KnowledgeKind.PRINCIPLE,
        title=title,
        statement=statement,
        rationale=rationale,
        universe=universe,
        authority=authority,
        owner=_OWNER,
        lifecycle=Lifecycle.RATIFIED,
        version=_VERSION,
        knowledge_links=knowledge_links,
        dependencies=dependencies,
        tags=("constitution",) if authority is KnowledgeAuthority.CONSTITUTIONAL else (),
    )


def build_seed_base() -> KnowledgeBase:
    """Return the founding canonical knowledge base (authored exactly once)."""
    objects: list[CanonicalKnowledgeObject] = []

    # -- Principles (Part 01/02) ----------------------------------------------
    objects.append(
        _principle(
            "UCKO-PRIN-0001",
            "Knowledge Once Principle",
            "A canonical architectural decision shall exist exactly once. Everything "
            "else shall be generated, derived, linked, validated, certified, or "
            "consumed from that single authoritative source. Duplication of "
            "knowledge, decisions, or explanations is prohibited.",
            "Duplication is the root cause of drift, contradiction, and repeated "
            "rediscovery. Authoring once makes institutional memory permanent and "
            "every derived artifact traceable to a single source of truth.",
            authority=KnowledgeAuthority.CONSTITUTIONAL,
            universe="GOVERNANCE",
        )
    )
    objects.append(
        _principle(
            "UCKO-PRIN-0002",
            "Frozen Corpus Is Read-Only (DP-03)",
            "The certified corpus (00-BOOK, 00-SOURCE, 99-FREEZE) is read-only to "
            "implementation. Engineering code reads and projects it but never mutates it.",
            "A read-only certified substrate guarantees that derived state can always "
            "be regenerated and audited against an immutable source.",
            authority=KnowledgeAuthority.CONSTITUTIONAL,
            universe="GOVERNANCE",
            knowledge_links=("UCKO-PRIN-0001",),
        )
    )
    objects.append(
        _principle(
            "UCKO-PRIN-0003",
            "Vendor-Neutral Core (TP-04 / TP-05)",
            "The foundation is standard-library only and least-sufficient: no runtime "
            "dependency is introduced where the standard library suffices.",
            "Vendor neutrality keeps the core portable, auditable, and free of supply-"
            "chain and lock-in risk; least-sufficient technology minimises blast radius.",
            authority=KnowledgeAuthority.ARCHITECTURAL,
            universe="ARCHITECTURE",
            knowledge_links=("UCKO-PRIN-0001",),
        )
    )
    objects.append(
        _principle(
            "UCKO-PRIN-0004",
            "Versioned Interface Contracts (AR-03 / PL-05)",
            "All inter-module interaction occurs through documented, semantically "
            "versioned contracts that evolve backward-compatibly; breaking changes "
            "require a new major version.",
            "Explicit versioned contracts let independently evolving modules interoperate "
            "without silent breakage and make compatibility a checkable property.",
            authority=KnowledgeAuthority.ARCHITECTURAL,
            universe="ARCHITECTURE",
            knowledge_links=("UCKO-PRIN-0001",),
        )
    )
    objects.append(
        _principle(
            "UCKO-PRIN-0005",
            "Constitutional Determinism (IMP-007 §5)",
            "Identical inputs under an identical environment must produce byte-identical "
            "outputs; records embed no wall-clock or ambient state.",
            "Determinism makes every artifact reproducible, hashable, and independently "
            "verifiable, which is the precondition for content-addressing and drift gates.",
            authority=KnowledgeAuthority.CONSTITUTIONAL,
            universe="ARCHITECTURE",
            knowledge_links=("UCKO-PRIN-0001",),
        )
    )

    # -- Standards / conventions / patterns (Part 01) -------------------------
    objects.append(
        CanonicalKnowledgeObject.create(
            cko_id="UCKO-STD-0001",
            kind=KnowledgeKind.STANDARD,
            title="Content-Addressed Canonical Records",
            statement="Every canonical object and decision is sealed with a SHA-256 "
            "content hash over its canonical JSON, so mutation is detectable and "
            "duplicates are identifiable by hash equality.",
            rationale="",
            universe="ARCHITECTURE",
            authority=KnowledgeAuthority.ENGINEERING,
            owner=_OWNER,
            lifecycle=Lifecycle.OPERATIONAL,
            version=_VERSION,
            dependencies=("UCKO-PRIN-0005",),
            knowledge_links=("UCKO-PRIN-0001",),
        )
    )
    objects.append(
        CanonicalKnowledgeObject.create(
            cko_id="UCKO-CONV-0001",
            kind=KnowledgeKind.CONVENTION,
            title="Immutable, Slotted Value Types",
            statement="Value types are frozen, slotted dataclasses that parse "
            "defensively and never mutate their inputs.",
            rationale="",
            universe="ARCHITECTURE",
            authority=KnowledgeAuthority.ENGINEERING,
            owner=_OWNER,
            lifecycle=Lifecycle.OPERATIONAL,
            version=_VERSION,
            dependencies=("UCKO-STD-0001",),
        )
    )
    objects.append(
        CanonicalKnowledgeObject.create(
            cko_id="UCKO-PAT-0001",
            kind=KnowledgeKind.PATTERN,
            title="Read-Only Adapter Projection",
            statement="Higher layers consume the corpus through read-only adapters "
            "that project immutable views, never through direct mutation.",
            rationale="",
            universe="ARCHITECTURE",
            authority=KnowledgeAuthority.ENGINEERING,
            owner=_OWNER,
            lifecycle=Lifecycle.OPERATIONAL,
            version=_VERSION,
            knowledge_links=("UCKO-PRIN-0002",),
        )
    )
    objects.append(
        CanonicalKnowledgeObject.create(
            cko_id="UCKO-ANTI-0001",
            kind=KnowledgeKind.ANTI_PATTERN,
            title="Knowledge Duplication",
            statement="Copying a decision, rationale, or explanation into a second "
            "location. This forks the source of truth and guarantees future drift.",
            rationale="",
            universe="GOVERNANCE",
            authority=KnowledgeAuthority.ADVISORY,
            owner=_OWNER,
            lifecycle=Lifecycle.OPERATIONAL,
            version=_VERSION,
            knowledge_links=("UCKO-PRIN-0001",),
        )
    )

    # -- Rule (Part 01) --------------------------------------------------------
    objects.append(
        CanonicalKnowledgeObject.create(
            cko_id="UCKO-RULE-0001",
            kind=KnowledgeKind.RULE,
            title="No Duplicate Canonical Decision",
            statement="The knowledge validator rejects any base in which two canonical "
            "objects share an identical content hash.",
            rationale="Operationalises the Knowledge Once Principle as an enforced, "
            "automatic gate rather than a matter of discipline.",
            universe="GOVERNANCE",
            authority=KnowledgeAuthority.ARCHITECTURAL,
            owner=_OWNER,
            lifecycle=Lifecycle.OPERATIONAL,
            version=_VERSION,
            dependencies=("UCKO-PRIN-0001",),
        )
    )

    # -- Decisions (Part 03) ---------------------------------------------------
    decisions: list[DecisionRecord] = []
    decisions.append(
        DecisionRecord.create(
            decision_id="UKDA-DEC-0001",
            title="Adopt the Universal Knowledge & Decision Architecture",
            problem_statement="Architectural knowledge was scattered across documents, "
            "re-explained per contributor, and prone to drift and rediscovery.",
            context="UCOS Ω∞ is a large, evolving, multi-universe repository with many "
            "future developers and AI agents that each need identical architectural "
            "knowledge.",
            objective="Guarantee that every architectural decision is authored once, "
            "permanently rationalised, searchable, and automatically consumed.",
            chosen_architecture="A repository-native engine.knowledge package providing a "
            "canonical knowledge store, content-addressed objects/decisions, a knowledge "
            "graph, intelligence/search, validation, certification, generated handbooks, "
            "and an agent/developer bootstrap digest.",
            rationale="A single content-addressed source of truth with derived everything-"
            "else is the only design that structurally prevents duplication and drift.",
            authority=KnowledgeAuthority.CONSTITUTIONAL,
            owner=_OWNER,
            lifecycle=Lifecycle.RATIFIED,
            version=_VERSION,
            review_authority=_REVIEW,
            supersession_rules="Superseded only by a ratified successor decision that "
            "preserves the Knowledge Once Principle.",
            alternatives=(
                "Keep architectural knowledge in prose documents.",
                "Use an external wiki or third-party knowledge base.",
                "Author-once, derive-everything repository-native architecture (chosen).",
            ),
            evaluation_criteria=(
                "no duplication",
                "determinism",
                "vendor neutrality",
                "traceability",
            ),
            tradeoffs=(
                "Requires upfront modelling discipline in exchange for permanent, "
                "drift-free institutional memory.",
            ),
            rejected_options=(
                RejectedOption(
                    "Prose documents",
                    "No enforcement; duplication and drift are inevitable.",
                ),
                RejectedOption(
                    "External wiki / third-party KB",
                    "Violates vendor neutrality (TP-04) and separates knowledge from the "
                    "repository that is the sole implementation authority.",
                ),
            ),
            consequences=(
                "All future documentation is generated from canonical knowledge.",
                "A validation/certification gate can enforce knowledge integrity.",
            ),
            risks=("Modelling overhead for authors.",),
            mitigations=("Seed knowledge + generators lower the authoring cost.",),
            dependencies=("UCKO-PRIN-0001", "UCKO-PRIN-0005"),
            impact_analysis="Establishes a new foundational capability consumed by every "
            "future universe, runtime, and governance process.",
            implementation_guidance="Author objects in the canonical store; run the "
            "validator and certifier; generate handbooks and the bootstrap digest.",
            validation_strategy="engine.knowledge.validation default suite (fail-closed).",
            certification_requirements=(
                "complete",
                "authority-defined",
                "owner-identified",
                "rationale-present",
            ),
        )
    )

    objects.append(
        CanonicalKnowledgeObject.create(
            cko_id="UCKO-DEC-0001",
            kind=KnowledgeKind.DECISION,
            title="Adopt the Universal Knowledge & Decision Architecture",
            statement="Ratified adoption of the UKDA as a permanent, repository-native "
            "capability. See linked decision record for full rationale.",
            rationale="Recorded once; all explanation lives in UKDA-DEC-0001.",
            universe="GOVERNANCE",
            authority=KnowledgeAuthority.CONSTITUTIONAL,
            owner=_OWNER,
            lifecycle=Lifecycle.RATIFIED,
            version=_VERSION,
            dependencies=("UCKO-PRIN-0001",),
            decision_links=("UKDA-DEC-0001",),
            tags=("constitution",),
        )
    )

    return KnowledgeBase(objects, decisions)


__all__ = ["build_seed_base"]
