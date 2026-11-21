"""UKIP Part 10 — Knowledge Assimilation (EPIC-UKDA-003).

The one pipeline by which knowledge enters the corpus, however many providers there
are and whatever they are:

    collect -> classify -> screen -> admit -> relate -> record provenance -> ledger

Each stage is a call into the layer that owns it — providers, classification,
discovery, registry, relationships, provenance — so assimilation contains no
knowledge logic of its own. That is deliberate: an orchestrator that re-implemented
any of those rules would become a second source of truth for them.

The result is a :class:`AssimilationReport` whose ledger records, for every single
contribution, which provider supplied it, what it classified as, whether it
established a canonical home or corroborated an existing one, and the digest of the
knowledge involved. Because corroboration is a first-class outcome rather than an
error, adding the tenth provider that repeats what the first said produces ten
ledger entries and one record — the Knowledge Once Principle, observable in the
output (UKIP-LAW-001, UKIP-LAW-003).

Deterministic: providers run in ``(priority, provider_id)`` order, units in key
order, and nothing consults the wall clock, so the same inputs always yield a
byte-identical report and the same seal (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.knowledge.cko import DecisionRecord
from engine.knowledge.model import content_hash
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.ukip.classification import Classification, KnowledgeClassifier
from engine.knowledge.ukip.contracts import KnowledgeUnit
from engine.knowledge.ukip.discovery import KnowledgeDiscovery
from engine.knowledge.ukip.errors import AssimilationError, ProviderError
from engine.knowledge.ukip.provenance import (
    ProvenanceLedger,
    Stage,
)
from engine.knowledge.ukip.providers import (
    KnowledgeProvider,
    ProviderRegistry,
    default_registry,
)
from engine.knowledge.ukip.registry import (
    Admission,
    AdmissionOutcome,
    KnowledgeRegistry,
)
from engine.knowledge.ukip.relationships import RelationshipSet, build_relationships

#: The assimilation evidence envelope schema.
ASSIMILATION_SCHEMA = "ucos-ukip-knowledge-assimilation"
ASSIMILATION_VERSION = "1.0.0"

#: The actor recorded for pipeline-performed provenance steps.
ASSIMILATOR_ACTOR = "ukip-assimilator"


class Disposition(str, Enum):
    """What happened to a single contribution."""

    HOMED = "homed"
    CORROBORATED = "corroborated"
    SKIPPED = "skipped"
    FAILED = "failed"

    @property
    def admitted(self) -> bool:
        return self in (Disposition.HOMED, Disposition.CORROBORATED)


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """One contribution's complete disposition — the audit unit of assimilation."""

    provider_id: str
    unit_key: str
    disposition: Disposition
    knowledge_id: str = ""
    knowledge_sha256: str = ""
    kind: str = ""
    authority: str = ""
    classification_rules: tuple[str, ...] = ()
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "unit_key": self.unit_key,
            "disposition": self.disposition.value,
            "knowledge_id": self.knowledge_id,
            "knowledge_sha256": self.knowledge_sha256,
            "kind": self.kind,
            "authority": self.authority,
            "classification_rules": list(self.classification_rules),
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class AssimilationReport:
    """The deterministic outcome of one assimilation run."""

    registry: KnowledgeRegistry
    relationships: RelationshipSet
    provenance: ProvenanceLedger
    ledger: tuple[LedgerEntry, ...]
    provider_ids: tuple[str, ...]
    failures: tuple[LedgerEntry, ...] = ()
    decisions: tuple[DecisionRecord, ...] = ()

    # -- ledger views ----------------------------------------------------------

    def homed(self) -> tuple[LedgerEntry, ...]:
        return tuple(e for e in self.ledger if e.disposition is Disposition.HOMED)

    def corroborated(self) -> tuple[LedgerEntry, ...]:
        return tuple(e for e in self.ledger if e.disposition is Disposition.CORROBORATED)

    def skipped(self) -> tuple[LedgerEntry, ...]:
        return tuple(e for e in self.ledger if e.disposition is Disposition.SKIPPED)

    def entries_for(self, provider_id: str) -> tuple[LedgerEntry, ...]:
        return tuple(e for e in self.ledger if e.provider_id == provider_id)

    @property
    def duplicates_created(self) -> int:
        """Records created beyond one per distinct piece of knowledge.

        Structurally always zero; reported explicitly so the invariant is observable
        in evidence rather than merely asserted in prose.
        """
        return len(self.registry) - len(
            {e.knowledge_sha256 for e in self.ledger if e.disposition.admitted}
        )

    @property
    def accepted(self) -> bool:
        """True iff nothing failed and no duplicate record was produced."""
        return not self.failures and self.duplicates_created == 0

    def counts(self) -> dict[str, int]:
        return {
            "contributions": len(self.ledger),
            "records": len(self.registry),
            "homed": len(self.homed()),
            "corroborated": len(self.corroborated()),
            "skipped": len(self.skipped()),
            "failed": len(self.failures),
            "providers": len(self.provider_ids),
            "relationships": len(self.relationships),
            "dangling_relationships": len(self.relationships.dangling()),
            "duplicates_created": self.duplicates_created,
        }

    def seal(self) -> str:
        """A single deterministic seal binding registry, relationships and provenance."""
        return content_hash(
            {
                "registry": self.registry.seal(),
                "relationships": self.relationships.seal(),
                "provenance": self.provenance.seal(),
                "ledger": [e.to_dict() for e in self.ledger],
            }
        )

    def to_knowledge_base(self) -> KnowledgeBase:
        """Project the assimilated registry as a UKDA knowledge base."""
        return self.registry.to_knowledge_base(self.decisions)

    def to_document(self) -> dict[str, Any]:
        return {
            "schema": ASSIMILATION_SCHEMA,
            "version": ASSIMILATION_VERSION,
            "accepted": self.accepted,
            "counts": self.counts(),
            "seal": self.seal(),
            "providers": list(self.provider_ids),
            "ledger": [e.to_dict() for e in self.ledger],
            "failures": [e.to_dict() for e in self.failures],
            "registry_seal": self.registry.seal(),
            "relationships_seal": self.relationships.seal(),
            "provenance_seal": self.provenance.seal(),
        }


class KnowledgeAssimilator:
    """Runs the assimilation pipeline over an unbounded set of providers.

    ``screen`` enables the discover-before-create gate for non-authoritative
    providers: their units are checked against what is already registered, and a unit
    that merely restates existing knowledge in different words is skipped with the
    match recorded, rather than admitted as near-duplicate knowledge. Authoritative
    providers are never screened, because the canonical store *is* the answer that
    screening would compare against.

    ``strict`` turns a provider failure into an immediate error instead of a recorded
    failure entry — the fail-closed posture for gates (UKIP-LAW-011).
    """

    __slots__ = ("_classifier", "_screen", "_strict")

    def __init__(
        self,
        *,
        classifier: KnowledgeClassifier | None = None,
        screen: bool = False,
        strict: bool = False,
    ) -> None:
        self._classifier = classifier or KnowledgeClassifier()
        self._screen = screen
        self._strict = strict

    @property
    def classifier(self) -> KnowledgeClassifier:
        return self._classifier

    def assimilate(
        self,
        providers: ProviderRegistry | Iterable[KnowledgeProvider],
        *,
        registry: KnowledgeRegistry | None = None,
        decisions: Iterable[DecisionRecord] = (),
    ) -> AssimilationReport:
        """Assimilate every unit from every provider into one canonical registry.

        ``decisions`` are canonical UKDA decision records carried through to the
        projected base unchanged; UKIP registers knowledge and never synthesises a
        decision record it does not own.
        """
        provider_registry = (
            providers if isinstance(providers, ProviderRegistry) else ProviderRegistry(providers)
        )
        target = registry if registry is not None else KnowledgeRegistry()
        provenance = ProvenanceLedger()
        ledger: list[LedgerEntry] = []
        failures: list[LedgerEntry] = []

        for provider in provider_registry.ordered():
            descriptor = provider.descriptor()
            try:
                units = provider.units()
            except ProviderError as exc:
                if self._strict:
                    raise AssimilationError(
                        "provider failed during assimilation",
                        provider_id=descriptor.provider_id,
                        detail=str(exc),
                    ) from exc
                entry = LedgerEntry(
                    provider_id=descriptor.provider_id,
                    unit_key="*",
                    disposition=Disposition.FAILED,
                    reason=f"provider error: {exc}",
                )
                ledger.append(entry)
                failures.append(entry)
                continue

            for unit in units:
                entry = self._assimilate_unit(
                    unit,
                    target,
                    provenance,
                    authoritative=descriptor.authoritative,
                    priority=descriptor.priority,
                )
                ledger.append(entry)
                if entry.disposition is Disposition.FAILED:
                    failures.append(entry)

        relationships = build_relationships(target)
        self._record_relationship_provenance(target, relationships, provenance)

        return AssimilationReport(
            registry=target,
            relationships=relationships,
            provenance=provenance,
            ledger=tuple(ledger),
            provider_ids=provider_registry.provider_ids(),
            failures=tuple(failures),
            decisions=tuple(decisions),
        )

    # -- per-unit ---------------------------------------------------------------

    def _assimilate_unit(
        self,
        unit: KnowledgeUnit,
        registry: KnowledgeRegistry,
        provenance: ProvenanceLedger,
        *,
        authoritative: bool,
        priority: int,
    ) -> LedgerEntry:
        classification: Classification | None = None
        try:
            classification = self._classifier.classify(unit)
            classified = classification.apply(unit)
        except Exception as exc:  # contain a bad unit without losing the run
            if self._strict:
                raise AssimilationError(
                    "unit could not be classified",
                    provider_id=unit.source.provider_id,
                    unit_key=unit.key,
                    detail=str(exc),
                ) from exc
            return LedgerEntry(
                provider_id=unit.source.provider_id,
                unit_key=unit.key,
                disposition=Disposition.FAILED,
                reason=f"classification error: {exc}",
            )

        if self._screen and not authoritative:
            answer = KnowledgeDiscovery(registry).screen_unit(classified)
            if answer.must_reuse and answer.best is not None:
                best = answer.best
                # An exact digest match is not a skip: it is the same knowledge, so it
                # belongs on the record as corroboration. Only a *near* match — the
                # same idea in different words — is withheld from the corpus.
                if not best.exact:
                    return LedgerEntry(
                        provider_id=unit.source.provider_id,
                        unit_key=unit.key,
                        disposition=Disposition.SKIPPED,
                        knowledge_id=best.knowledge_id,
                        knowledge_sha256=classified.knowledge_sha256(),
                        kind=classified.kind.value if classified.kind else "",
                        authority=(classified.authority.value if classified.authority else ""),
                        classification_rules=classification.rule_ids(),
                        reason=f"reuse {best.knowledge_id}: {best.reason}",
                    )

        admission = registry.submit(
            classified,
            classification,
            authoritative=authoritative,
            priority=priority,
        )
        record = registry.require(admission.knowledge_id)
        provenance.put(record.provenance)
        return self._entry_for(admission, classified, classification)

    @staticmethod
    def _entry_for(
        admission: Admission,
        unit: KnowledgeUnit,
        classification: Classification,
    ) -> LedgerEntry:
        disposition = (
            Disposition.HOMED
            if admission.outcome is AdmissionOutcome.REGISTERED
            else Disposition.CORROBORATED
        )
        return LedgerEntry(
            provider_id=admission.provider_id,
            unit_key=admission.unit_key,
            disposition=disposition,
            knowledge_id=admission.knowledge_id,
            knowledge_sha256=unit.knowledge_sha256(),
            kind=unit.kind.value if unit.kind else "",
            authority=unit.authority.value if unit.authority else "",
            classification_rules=classification.rule_ids(),
            reason=admission.reason,
        )

    @staticmethod
    def _record_relationship_provenance(
        registry: KnowledgeRegistry,
        relationships: RelationshipSet,
        provenance: ProvenanceLedger,
    ) -> None:
        """Append a RELATED step for every record that ended up wired into the graph."""
        for record in registry.records():
            wired = relationships.outbound(record.knowledge_id) + relationships.inbound(
                record.knowledge_id
            )
            if not wired:
                continue
            chain = provenance.append(
                record.knowledge_id,
                Stage.RELATED,
                actor=ASSIMILATOR_ACTOR,
                action="relate",
                payload_sha256=content_hash([list(r.key()) for r in wired]),
                detail=f"relationships:{len(wired)}",
            )
            registry.register(record.with_provenance(chain))


def assimilate_base(
    base: KnowledgeBase,
    *,
    extra_providers: Iterable[KnowledgeProvider] = (),
    screen: bool = False,
    strict: bool = False,
) -> AssimilationReport:
    """Assimilate the canonical store plus any additional providers.

    The convenience entry point used by the CLI and evidence generation: it shows the
    intended composition — the authoritative canonical providers first, then however
    many further providers a caller supplies.
    """
    providers = default_registry(base).extend(extra_providers)
    return KnowledgeAssimilator(screen=screen, strict=strict).assimilate(
        providers, decisions=base.decisions()
    )


__all__ = [
    "ASSIMILATION_SCHEMA",
    "ASSIMILATION_VERSION",
    "ASSIMILATOR_ACTOR",
    "Disposition",
    "LedgerEntry",
    "AssimilationReport",
    "KnowledgeAssimilator",
    "assimilate_base",
]
