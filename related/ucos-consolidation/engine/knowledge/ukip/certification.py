"""UKIP Part 12 — Knowledge Certification (EPIC-UKDA-003).

Certification answers a different question from validation. Validation asks *is this
knowledge defective?*; certification asks *is this knowledge complete enough to be
relied on?* — and answers per capability, so a caller learns which of the eleven
knowledge capabilities is fully established and which is merely present.

The status vocabulary is reused from the UKDA certifier
(:class:`engine.knowledge.certification.CertStatus`) rather than redefined, so a UKIP
certificate and a UKDA certificate mean the same thing by the same words.

Certification is fail-closed (UKIP-LAW-011): a single blocking validation failure
denies the certificate outright, regardless of how many criteria pass. Criteria are
declared as data (:data:`CRITERIA`), each bound to the capability it certifies and to
the constitutional law it derives from, so the certificate is traceable back to the
constitution rather than being an opaque score.

The certificate carries a deterministic ``seal`` over the exact facts it asserts, so
two runs over identical knowledge produce an identical, comparable seal (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from engine.knowledge.certification import CertStatus
from engine.knowledge.cko import DecisionRecord
from engine.knowledge.model import content_hash
from engine.knowledge.ukip.constitution import (
    KNOWLEDGE_CAPABILITIES,
    KnowledgeCapability,
    knowledge_constitution,
)
from engine.knowledge.ukip.discovery import KnowledgeDiscovery
from engine.knowledge.ukip.registry import KnowledgeRegistry
from engine.knowledge.ukip.relationships import build_relationships
from engine.knowledge.ukip.validation import (
    KnowledgeIntelligenceValidator,
    ValidationReport,
)

#: The certification authority and standard this layer certifies against. Engineering
#: execution only: UKIP certifies the *state of knowledge*, never constitutional
#: authority, which remains with the architecture board.
KNOWLEDGE_INTELLIGENCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"
KNOWLEDGE_INTELLIGENCE_STANDARD = "UCOS-UKIP-KNOWLEDGE-INTELLIGENCE-CERTIFICATION-STANDARD"

#: The certificate envelope schema.
CERTIFICATE_SCHEMA = "ucos-ukip-knowledge-certificate"
CERTIFICATE_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class CertificationSubject:
    """The facts a criterion may assert over, gathered once."""

    registry: KnowledgeRegistry
    validation: ValidationReport
    discovery: KnowledgeDiscovery
    relationship_count: int
    dangling_count: int
    cycle_count: int

    @classmethod
    def of(
        cls,
        registry: KnowledgeRegistry,
        *,
        decisions: Iterable[DecisionRecord] = (),
        validation: ValidationReport | None = None,
    ) -> CertificationSubject:
        carried = tuple(decisions)
        report = validation
        if report is None:
            report = KnowledgeIntelligenceValidator().validate(registry, decisions=carried)
        relationships = build_relationships(registry)
        return cls(
            registry=registry,
            validation=report,
            discovery=KnowledgeDiscovery(registry),
            relationship_count=len(relationships),
            dangling_count=len(relationships.dangling()),
            cycle_count=len(relationships.cycles()),
        )


@dataclass(frozen=True, slots=True)
class Criterion:
    """One certification criterion, bound to a capability and a constitutional law."""

    criterion_id: str
    capability: KnowledgeCapability
    law_id: str
    description: str
    predicate: Callable[[CertificationSubject], bool]

    def evaluate(self, subject: CertificationSubject) -> bool:
        return bool(self.predicate(subject))

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "capability": self.capability.value,
            "law_id": self.law_id,
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class CriterionResult:
    """The outcome of one criterion."""

    criterion_id: str
    capability: KnowledgeCapability
    law_id: str
    satisfied: bool
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "capability": self.capability.value,
            "law_id": self.law_id,
            "satisfied": self.satisfied,
            "description": self.description,
        }


def _check_passed(subject: CertificationSubject, check_id: str) -> bool:
    finding = subject.validation.finding(check_id)
    return finding is not None and finding.passed


#: The certification criteria, authored once as data, one per capability at minimum.
CRITERIA: tuple[Criterion, ...] = (
    Criterion(
        "constitution-governs-every-capability",
        KnowledgeCapability.CONSTITUTION,
        "UKIP-LAW-012",
        "Every knowledge capability is bound by at least one constitutional law.",
        lambda s: knowledge_constitution().is_complete,
    ),
    Criterion(
        "registry-single-home",
        KnowledgeCapability.REGISTRY,
        "UKIP-LAW-003",
        "Exactly one canonical home exists per distinct piece of knowledge.",
        lambda s: not s.registry.duplicate_homes(),
    ),
    Criterion(
        "registry-sealed",
        KnowledgeCapability.REGISTRY,
        "UKIP-LAW-011",
        "Every record verifies its content hash.",
        lambda s: not s.registry.unsealed(),
    ),
    Criterion(
        "registry-populated",
        KnowledgeCapability.REGISTRY,
        "UKIP-LAW-009",
        "The registry holds at least one canonical record.",
        lambda s: len(s.registry) > 0,
    ),
    Criterion(
        "providers-unbounded",
        KnowledgeCapability.ASSIMILATION,
        "UKIP-LAW-001",
        "Knowledge is attributed to at least one provider, with no provider ceiling.",
        lambda s: bool(s.registry.provider_ids()),
    ),
    Criterion(
        "classification-total",
        KnowledgeCapability.CLASSIFICATION,
        "UKIP-LAW-005",
        "Every record carries a fully decided classification.",
        lambda s: _check_passed(s, "total-classification"),
    ),
    Criterion(
        "identity-content-derived",
        KnowledgeCapability.REGISTRY,
        "UKIP-LAW-002",
        "Every canonical identifier is derived from the knowledge it names.",
        lambda s: _check_passed(s, "content-derived-identity"),
    ),
    Criterion(
        "provenance-complete",
        KnowledgeCapability.PROVENANCE,
        "UKIP-LAW-004",
        "Every record carries a complete, intact, grounded provenance chain.",
        lambda s: (
            _check_passed(s, "provenance-complete")
            and _check_passed(s, "provenance-intact")
            and _check_passed(s, "provenance-grounded")
        ),
    ),
    Criterion(
        "relationships-resolved",
        KnowledgeCapability.RELATIONSHIPS,
        "UKIP-LAW-006",
        "Every declared relationship resolves and is navigable both ways.",
        lambda s: s.dangling_count == 0 and _check_passed(s, "relationships-navigable"),
    ),
    Criterion(
        "relationships-acyclic",
        KnowledgeCapability.RELATIONSHIPS,
        "UKIP-LAW-006",
        "The dependency, structure, supersession and derivation families are acyclic.",
        lambda s: s.cycle_count == 0,
    ),
    Criterion(
        "graph-resolved",
        KnowledgeCapability.GRAPH,
        "UKIP-LAW-008",
        "Every graph edge endpoint is a registered record.",
        lambda s: _check_passed(s, "graph-resolved"),
    ),
    Criterion(
        "graph-composable",
        KnowledgeCapability.GRAPH,
        "UKIP-LAW-008",
        "Knowledge composes: relationships exist to compose, or nothing to relate.",
        lambda s: s.relationship_count > 0 or len(s.registry) <= 1,
    ),
    Criterion(
        "discovery-universal",
        KnowledgeCapability.DISCOVERY,
        "UKIP-LAW-007",
        "Every record is discoverable by identifier, digest and ranked search.",
        lambda s: s.discovery.coverage().is_fully_discoverable,
    ),
    Criterion(
        "evidence-traceable",
        KnowledgeCapability.EVIDENCE,
        "UKIP-LAW-010",
        "Every record cites a content-addressed source in its provenance.",
        lambda s: _check_passed(s, "provenance-grounded"),
    ),
    Criterion(
        "validation-fail-closed",
        KnowledgeCapability.VALIDATION,
        "UKIP-LAW-011",
        "The validation suite reports no blocking failure.",
        lambda s: not s.validation.blocking_failures,
    ),
    Criterion(
        "validation-enforces-every-law",
        KnowledgeCapability.VALIDATION,
        "UKIP-LAW-010",
        "Every authored constitutional law is enforced by at least one check.",
        lambda s: not s.validation.uncovered_laws(),
    ),
    Criterion(
        "certification-grounded",
        KnowledgeCapability.CERTIFICATION,
        "UKIP-LAW-010",
        "The projected knowledge base passes the full UKDA validation suite.",
        lambda s: _check_passed(s, "projected-base-valid"),
    ),
)


@dataclass(frozen=True, slots=True)
class KnowledgeCertificate:
    """The deterministic certificate over a knowledge registry."""

    status: CertStatus
    results: tuple[CriterionResult, ...]
    registry_seal: str
    record_count: int
    provider_count: int
    authority: str = KNOWLEDGE_INTELLIGENCE_AUTHORITY
    standard: str = KNOWLEDGE_INTELLIGENCE_STANDARD

    # -- verdict ---------------------------------------------------------------

    @property
    def certified(self) -> bool:
        return self.status is CertStatus.CERTIFIED

    def unsatisfied(self) -> tuple[CriterionResult, ...]:
        return tuple(r for r in self.results if not r.satisfied)

    def result(self, criterion_id: str) -> CriterionResult | None:
        for item in self.results:
            if item.criterion_id == criterion_id:
                return item
        return None

    # -- per-capability verdicts ----------------------------------------------

    def capability_status(self) -> dict[str, str]:
        """Each capability's status, derived from the criteria bound to it."""
        statuses: dict[str, str] = {}
        for capability in KNOWLEDGE_CAPABILITIES:
            bound = [r for r in self.results if r.capability is capability]
            if not bound:
                statuses[capability.value] = CertStatus.INCOMPLETE.value
            elif all(r.satisfied for r in bound):
                statuses[capability.value] = CertStatus.CERTIFIED.value
            else:
                statuses[capability.value] = CertStatus.DENIED.value
        return statuses

    def certified_capabilities(self) -> tuple[str, ...]:
        return tuple(
            name
            for name, status in sorted(self.capability_status().items())
            if status == CertStatus.CERTIFIED.value
        )

    def uncertified_capabilities(self) -> tuple[str, ...]:
        return tuple(
            name
            for name, status in sorted(self.capability_status().items())
            if status != CertStatus.CERTIFIED.value
        )

    def counts(self) -> dict[str, int]:
        satisfied = sum(1 for r in self.results if r.satisfied)
        return {
            "criteria": len(self.results),
            "satisfied": satisfied,
            "unsatisfied": len(self.results) - satisfied,
            "records": self.record_count,
            "providers": self.provider_count,
            "capabilities_certified": len(self.certified_capabilities()),
            "capabilities_total": len(KNOWLEDGE_CAPABILITIES),
        }

    # -- seal ------------------------------------------------------------------

    def seal(self) -> str:
        """A deterministic seal over exactly the facts the certificate asserts."""
        return content_hash(
            {
                "status": self.status.value,
                "standard": self.standard,
                "authority": self.authority,
                "registry_seal": self.registry_seal,
                "results": [r.to_dict() for r in self.results],
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": CERTIFICATE_SCHEMA,
            "version": CERTIFICATE_VERSION,
            "status": self.status.value,
            "certified": self.certified,
            "authority": self.authority,
            "standard": self.standard,
            "registry_seal": self.registry_seal,
            "seal": self.seal(),
            "counts": self.counts(),
            "capability_status": self.capability_status(),
            "uncertified_capabilities": list(self.uncertified_capabilities()),
            "results": [r.to_dict() for r in self.results],
        }


class KnowledgeIntelligenceCertifier:
    """Evaluates the certification criteria over a knowledge registry (fail-closed)."""

    __slots__ = ("_criteria",)

    def __init__(self, criteria: Iterable[Criterion] | None = None) -> None:
        selected = tuple(criteria) if criteria is not None else CRITERIA
        self._criteria = tuple(sorted(selected, key=lambda c: c.criterion_id))

    @property
    def criterion_ids(self) -> tuple[str, ...]:
        return tuple(c.criterion_id for c in self._criteria)

    def certify(
        self,
        registry: KnowledgeRegistry,
        *,
        decisions: Iterable[DecisionRecord] = (),
        validation: ValidationReport | None = None,
    ) -> KnowledgeCertificate:
        """Certify a registry. A blocking validation failure denies outright."""
        subject = CertificationSubject.of(registry, decisions=decisions, validation=validation)
        results = tuple(
            CriterionResult(
                criterion_id=criterion.criterion_id,
                capability=criterion.capability,
                law_id=criterion.law_id,
                satisfied=criterion.evaluate(subject),
                description=criterion.description,
            )
            for criterion in self._criteria
        )
        if subject.validation.blocking_failures:
            status = CertStatus.DENIED
        elif all(r.satisfied for r in results):
            status = CertStatus.CERTIFIED
        else:
            status = CertStatus.INCOMPLETE
        return KnowledgeCertificate(
            status=status,
            results=results,
            registry_seal=registry.seal(),
            record_count=len(registry),
            provider_count=len(registry.provider_ids()),
        )


def certify_registry(
    registry: KnowledgeRegistry, *, decisions: Iterable[DecisionRecord] = ()
) -> KnowledgeCertificate:
    """Convenience: certify a registry with the default criteria."""
    return KnowledgeIntelligenceCertifier().certify(registry, decisions=decisions)


def certify_assimilation(report: Any) -> KnowledgeCertificate:
    """Certify an :class:`~engine.knowledge.ukip.assimilation.AssimilationReport`."""
    return KnowledgeIntelligenceCertifier().certify(report.registry, decisions=report.decisions)


__all__ = [
    "KNOWLEDGE_INTELLIGENCE_AUTHORITY",
    "KNOWLEDGE_INTELLIGENCE_STANDARD",
    "CERTIFICATE_SCHEMA",
    "CERTIFICATE_VERSION",
    "CertStatus",
    "CertificationSubject",
    "Criterion",
    "CriterionResult",
    "CRITERIA",
    "KnowledgeCertificate",
    "KnowledgeIntelligenceCertifier",
    "certify_registry",
    "certify_assimilation",
]
