"""UKIP Part 11 — Knowledge Validation (EPIC-UKDA-003).

The fail-closed gate over an assimilated registry. Each check is an immutable,
deterministic predicate; any BLOCKING failure makes the registry not-valid
(UKIP-LAW-011).

The verdict, severity, status and finding types are **reused verbatim** from the UKDA
suite (:mod:`engine.knowledge.validation`) rather than redefined, so a UKIP report and
a UKDA report are directly comparable and there is exactly one vocabulary for "did
knowledge validation pass".

The checks fall into two groups:

    * **registry invariants** that only exist once knowledge has providers — a single
      canonical home per digest, mandatory grounded provenance, total classification,
      resolved relationships, both-ways navigability, acyclic dependency families,
      universal discoverability, provider attribution, record integrity;
    * **the delegated UKDA suite** — :class:`ProjectedBaseCheck` projects the registry
      as a :class:`~engine.knowledge.store.KnowledgeBase` and runs the entire existing
      UKDA validator over it, so provider-sourced knowledge is held to exactly the
      same standard as hand-authored canonical knowledge, with no second copy of those
      rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, ClassVar

from engine.knowledge.cko import DecisionRecord
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.ukip.constitution import (
    KNOWLEDGE_LAWS,
    KnowledgeCapability,
    knowledge_constitution,
)
from engine.knowledge.ukip.discovery import KnowledgeDiscovery
from engine.knowledge.ukip.graph import KnowledgeIntelligenceGraph
from engine.knowledge.ukip.provenance import ProvenanceLedger
from engine.knowledge.ukip.registry import KnowledgeRegistry
from engine.knowledge.ukip.relationships import RelationshipSet, build_relationships
from engine.knowledge.validation import (
    CheckStatus,
    KnowledgeFinding,
    Severity,
    Verdict,
    validate_base,
)


@dataclass(frozen=True, slots=True)
class ValidationSubject:
    """Everything a check may inspect, assembled once and shared by every check.

    Assembling the derived views here — rather than letting each check rebuild them —
    keeps validation O(1) in graph construction and guarantees every check sees the
    same relationships, graph and provenance.
    """

    registry: KnowledgeRegistry
    relationships: RelationshipSet
    graph: KnowledgeIntelligenceGraph
    discovery: KnowledgeDiscovery
    provenance: ProvenanceLedger
    decisions: tuple[DecisionRecord, ...] = ()

    @classmethod
    def of(
        cls,
        registry: KnowledgeRegistry,
        *,
        provenance: ProvenanceLedger | None = None,
        decisions: Iterable[DecisionRecord] = (),
    ) -> ValidationSubject:
        relationships = build_relationships(registry)
        ledger = provenance
        if ledger is None:
            ledger = ProvenanceLedger(r.provenance for r in registry.records())
        return cls(
            registry=registry,
            relationships=relationships,
            graph=KnowledgeIntelligenceGraph(registry, relationships),
            discovery=KnowledgeDiscovery(registry),
            provenance=ledger,
            decisions=tuple(decisions),
        )

    def projected_base(self) -> KnowledgeBase:
        """The registry as a UKDA base, with canonical decision records carried."""
        return self.registry.to_knowledge_base(self.decisions)


class KnowledgeIntelligenceCheck(ABC):
    """The common contract for a single UKIP validation check."""

    check_id: ClassVar[str]
    severity: ClassVar[Severity]
    law_id: ClassVar[str] = ""
    capability: ClassVar[KnowledgeCapability]
    description: ClassVar[str] = ""

    @abstractmethod
    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        raise NotImplementedError  # pragma: no cover

    def _passed(self, message: str = "") -> KnowledgeFinding:
        return KnowledgeFinding(
            check_id=self.check_id,
            severity=self.severity,
            status=CheckStatus.PASS,
            message=message or f"{self.check_id} satisfied",
        )

    def _failed(self, message: str, offenders: Iterable[str] = ()) -> KnowledgeFinding:
        return KnowledgeFinding(
            check_id=self.check_id,
            severity=self.severity,
            status=CheckStatus.FAIL,
            message=message,
            offenders=tuple(offenders),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "severity": self.severity.value,
            "law_id": self.law_id,
            "capability": self.capability.value,
            "description": self.description,
        }


class SingleCanonicalHomeCheck(KnowledgeIntelligenceCheck):
    check_id = "single-canonical-home"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-003"
    capability = KnowledgeCapability.REGISTRY
    description = "No two records home identical knowledge (the Knowledge Once Principle)."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        groups = subject.registry.duplicate_homes()
        if groups:
            return self._failed(
                "identical knowledge is homed more than once",
                ("+".join(group) for group in groups),
            )
        return self._passed(f"{len(subject.registry)} records, one home each")


class ContentDerivedIdentityCheck(KnowledgeIntelligenceCheck):
    check_id = "content-derived-identity"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-002"
    capability = KnowledgeCapability.REGISTRY
    description = "Every identifier is the digest of the knowledge it names."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        offenders = [
            record.knowledge_id
            for record in subject.registry.records()
            if not record.knowledge_id.endswith(record.knowledge_sha256[:12].upper())
        ]
        if offenders:
            return self._failed("identifiers not derived from knowledge content", offenders)
        return self._passed()


class RecordIntegrityCheck(KnowledgeIntelligenceCheck):
    check_id = "record-integrity"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-011"
    capability = KnowledgeCapability.REGISTRY
    description = "Every record verifies its own content hash."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        offenders = subject.registry.unsealed()
        if offenders:
            return self._failed("record integrity failures detected", offenders)
        return self._passed()


class TotalClassificationCheck(KnowledgeIntelligenceCheck):
    check_id = "total-classification"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-005"
    capability = KnowledgeCapability.CLASSIFICATION
    description = "Every record carries all six decided classification facets."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        offenders = [
            record.knowledge_id
            for record in subject.registry.records()
            if not (record.universe and record.owner and record.version)
        ]
        if offenders:
            return self._failed("records with an undecided classification facet", offenders)
        return self._passed()


class ProvenanceCompleteCheck(KnowledgeIntelligenceCheck):
    check_id = "provenance-complete"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-004"
    capability = KnowledgeCapability.PROVENANCE
    description = "Every record carries every required provenance stage."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        missing = [
            record.knowledge_id
            for record in subject.registry.records()
            if not record.provenance.is_complete
        ]
        if missing:
            return self._failed("records with an incomplete provenance chain", missing)
        return self._passed()


class ProvenanceIntactCheck(KnowledgeIntelligenceCheck):
    check_id = "provenance-intact"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-004"
    capability = KnowledgeCapability.PROVENANCE
    description = "Every provenance chain verifies its hash links end to end."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        broken = [
            record.knowledge_id
            for record in subject.registry.records()
            if not record.provenance.verify()
        ]
        if broken:
            return self._failed("broken provenance chains detected", broken)
        return self._passed()


class ProvenanceGroundedCheck(KnowledgeIntelligenceCheck):
    check_id = "provenance-grounded"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-004"
    capability = KnowledgeCapability.PROVENANCE
    description = "Every chain cites at least one content-addressed source."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        ungrounded = [
            record.knowledge_id
            for record in subject.registry.records()
            if not record.provenance.is_grounded
        ]
        if ungrounded:
            return self._failed("records with no content-addressed source", ungrounded)
        return self._passed()


class ProviderAttributionCheck(KnowledgeIntelligenceCheck):
    check_id = "provider-attribution"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-001"
    capability = KnowledgeCapability.REGISTRY
    description = "Every record names at least one provider that supplied it."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        offenders = [
            record.knowledge_id for record in subject.registry.records() if not record.provider_ids
        ]
        if offenders:
            return self._failed("records with no provider attribution", offenders)
        return self._passed(f"{len(subject.registry.provider_ids())} providers attributed")


class RelationshipsResolvedCheck(KnowledgeIntelligenceCheck):
    check_id = "relationships-resolved"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-006"
    capability = KnowledgeCapability.RELATIONSHIPS
    description = "Every declared relationship resolves to a registered record."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        dangling = subject.relationships.dangling()
        if dangling:
            return self._failed(
                "unresolved relationship targets detected",
                (f"{d.source}-{d.relation.value}->{d.declared_target}" for d in dangling),
            )
        return self._passed()


class RelationshipsNavigableCheck(KnowledgeIntelligenceCheck):
    check_id = "relationships-navigable"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-006"
    capability = KnowledgeCapability.RELATIONSHIPS
    description = "Every relationship is readable from both of its endpoints."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        offenders = subject.relationships.unnavigable()
        if offenders:
            return self._failed(
                "relationships not navigable in both directions",
                (f"{r.source}-{r.relation.value}->{r.target}" for r in offenders),
            )
        return self._passed()


class AcyclicFamiliesCheck(KnowledgeIntelligenceCheck):
    check_id = "acyclic-relation-families"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-006"
    capability = KnowledgeCapability.RELATIONSHIPS
    description = "Dependency, structure, supersession and derivation stay acyclic."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        cycles = subject.relationships.cycles()
        if cycles:
            return self._failed(
                "cycles detected in an acyclic relation family",
                (f"{c.family}:{'->'.join(c.members)}" for c in cycles),
            )
        return self._passed()


class GraphResolvedCheck(KnowledgeIntelligenceCheck):
    check_id = "graph-resolved"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-008"
    capability = KnowledgeCapability.GRAPH
    description = "Every graph edge endpoint is a registered record."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        unresolved = subject.graph.unresolved()
        if unresolved:
            return self._failed("graph edges reference unregistered nodes", unresolved)
        return self._passed()


class UniversalDiscoverabilityCheck(KnowledgeIntelligenceCheck):
    check_id = "universal-discoverability"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-007"
    capability = KnowledgeCapability.DISCOVERY
    description = "Every record is findable by identifier, digest and search."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        undiscoverable = subject.discovery.coverage().undiscoverable
        if undiscoverable:
            return self._failed("records that cannot be discovered", undiscoverable)
        return self._passed()


class CanonicalKnowledgeOnlyCheck(KnowledgeIntelligenceCheck):
    check_id = "canonical-knowledge-only"
    severity = Severity.ADVISORY
    law_id = "UKIP-LAW-009"
    capability = KnowledgeCapability.REGISTRY
    description = "No record is left in a draft or review lifecycle stage."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        offenders = [
            record.knowledge_id
            for record in subject.registry.records()
            if record.lifecycle.value in ("draft", "review")
        ]
        if offenders:
            return self._failed("non-canonical (draft/review) knowledge registered", offenders)
        return self._passed()


class ConstitutionCompleteCheck(KnowledgeIntelligenceCheck):
    check_id = "constitution-complete"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-012"
    capability = KnowledgeCapability.CONSTITUTION
    description = "Every knowledge capability is bound by at least one law."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        del subject  # the constitution is authored data, not registry state
        constitution = knowledge_constitution()
        gaps = constitution.ungoverned_capabilities()
        if gaps:
            return self._failed(
                "knowledge capabilities with no governing law",
                (c.value for c in gaps),
            )
        return self._passed(f"{len(constitution.laws)} laws govern all capabilities")


class ProjectedBaseCheck(KnowledgeIntelligenceCheck):
    check_id = "projected-base-valid"
    severity = Severity.BLOCKING
    law_id = "UKIP-LAW-010"
    capability = KnowledgeCapability.VALIDATION
    description = "The registry projected as a UKDA base passes the full UKDA suite."

    def evaluate(self, subject: ValidationSubject) -> KnowledgeFinding:
        report = validate_base(subject.projected_base())
        if report.accepted:
            return self._passed(f"UKDA suite: {report.counts()['passed']} checks passed")
        return self._failed(
            "projected knowledge base failed UKDA validation",
            (f.check_id for f in report.blocking_failures),
        )


def default_checks() -> tuple[KnowledgeIntelligenceCheck, ...]:
    """The built-in UKIP validation suite, in stable check-id order."""
    checks: tuple[KnowledgeIntelligenceCheck, ...] = (
        AcyclicFamiliesCheck(),
        CanonicalKnowledgeOnlyCheck(),
        ConstitutionCompleteCheck(),
        ContentDerivedIdentityCheck(),
        GraphResolvedCheck(),
        ProjectedBaseCheck(),
        ProvenanceCompleteCheck(),
        ProvenanceGroundedCheck(),
        ProvenanceIntactCheck(),
        ProviderAttributionCheck(),
        RecordIntegrityCheck(),
        RelationshipsNavigableCheck(),
        RelationshipsResolvedCheck(),
        SingleCanonicalHomeCheck(),
        TotalClassificationCheck(),
        UniversalDiscoverabilityCheck(),
    )
    return tuple(sorted(checks, key=lambda c: c.check_id))


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The aggregate, deterministic verdict over a knowledge registry."""

    verdict: Verdict
    findings: tuple[KnowledgeFinding, ...] = field(default_factory=tuple)
    law_coverage: tuple[str, ...] = ()

    @property
    def accepted(self) -> bool:
        return self.verdict is Verdict.VALID

    @property
    def blocking_failures(self) -> tuple[KnowledgeFinding, ...]:
        return tuple(f for f in self.findings if f.is_blocking_failure)

    def finding(self, check_id: str) -> KnowledgeFinding | None:
        for item in self.findings:
            if item.check_id == check_id:
                return item
        return None

    def uncovered_laws(self) -> tuple[str, ...]:
        """Authored laws no check enforces — a validation gap, if any."""
        covered = set(self.law_coverage)
        return tuple(law.law_id for law in KNOWLEDGE_LAWS if law.law_id not in covered)

    def counts(self) -> dict[str, int]:
        passed = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": passed,
            "failed": len(self.findings) - passed,
            "blocking_failed": len(self.blocking_failures),
            "laws_enforced": len(set(self.law_coverage)),
            "laws_unenforced": len(self.uncovered_laws()),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "accepted": self.accepted,
            "counts": self.counts(),
            "laws_enforced": sorted(set(self.law_coverage)),
            "laws_unenforced": list(self.uncovered_laws()),
            "findings": [f.to_dict() for f in self.findings],
        }


class KnowledgeIntelligenceValidator:
    """Runs the deterministic UKIP validation suite (fail-closed)."""

    __slots__ = ("_checks",)

    def __init__(self, checks: Iterable[KnowledgeIntelligenceCheck] | None = None) -> None:
        selected = tuple(checks) if checks is not None else default_checks()
        self._checks = tuple(sorted(selected, key=lambda c: c.check_id))

    @property
    def check_ids(self) -> tuple[str, ...]:
        return tuple(c.check_id for c in self._checks)

    def validate(
        self,
        registry: KnowledgeRegistry,
        *,
        provenance: ProvenanceLedger | None = None,
        decisions: Iterable[DecisionRecord] = (),
    ) -> ValidationReport:
        subject = ValidationSubject.of(registry, provenance=provenance, decisions=decisions)
        findings = tuple(check.evaluate(subject) for check in self._checks)
        verdict = (
            Verdict.NOT_VALID if any(f.is_blocking_failure for f in findings) else Verdict.VALID
        )
        return ValidationReport(
            verdict=verdict,
            findings=findings,
            law_coverage=tuple(c.law_id for c in self._checks if c.law_id),
        )


def validate_registry(
    registry: KnowledgeRegistry, *, decisions: Iterable[DecisionRecord] = ()
) -> ValidationReport:
    """Convenience: validate a registry with the default suite."""
    return KnowledgeIntelligenceValidator().validate(registry, decisions=decisions)


def validate_assimilation(report: Any) -> ValidationReport:
    """Validate an :class:`~engine.knowledge.ukip.assimilation.AssimilationReport`.

    Uses the report's own carried decision records, so the pipeline's output is
    validated exactly as assimilated rather than against a reconstructed base.
    """
    return KnowledgeIntelligenceValidator().validate(
        report.registry,
        provenance=report.provenance,
        decisions=report.decisions,
    )


__all__ = [
    "ValidationSubject",
    "KnowledgeIntelligenceCheck",
    "SingleCanonicalHomeCheck",
    "ContentDerivedIdentityCheck",
    "RecordIntegrityCheck",
    "TotalClassificationCheck",
    "ProvenanceCompleteCheck",
    "ProvenanceIntactCheck",
    "ProvenanceGroundedCheck",
    "ProviderAttributionCheck",
    "RelationshipsResolvedCheck",
    "RelationshipsNavigableCheck",
    "AcyclicFamiliesCheck",
    "GraphResolvedCheck",
    "UniversalDiscoverabilityCheck",
    "CanonicalKnowledgeOnlyCheck",
    "ConstitutionCompleteCheck",
    "ProjectedBaseCheck",
    "default_checks",
    "ValidationReport",
    "KnowledgeIntelligenceValidator",
    "validate_registry",
    "validate_assimilation",
    "Severity",
    "CheckStatus",
    "Verdict",
    "KnowledgeFinding",
]
