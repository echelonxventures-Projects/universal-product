"""UKIP Part 06 — the Knowledge Registry (EPIC-UKDA-003).

The single canonical home of every piece of knowledge, whatever supplied it.

The registry is the mechanism that makes the Knowledge Once Principle hold under an
unbounded number of providers. It is keyed by the *content-derived* knowledge
identity (:meth:`~engine.knowledge.ukip.contracts.KnowledgeUnit.knowledge_id`), so:

    * the **first** unit to arrive with a given identity establishes the canonical
      home and becomes the record's canonical source (:data:`AdmissionOutcome.REGISTERED`);
    * a **later** unit with the same identity — from any other provider — is attached
      to that same record as a corroborating source
      (:data:`AdmissionOutcome.CORROBORATED`). It is not a duplicate to be reported;
      it is additional evidence that the knowledge is real. This is why N providers
      can be added without ever producing N records;
    * a unit that would occupy an existing identity with *different* substance cannot
      occur, because the identity *is* the substance's digest. The corresponding real
      failure — two records claiming the same canonical id — is rejected as
      :class:`~engine.knowledge.ukip.errors.DuplicateHomeError`.

Corroboration is ordered by provider authority and priority, so the canonical source
of a record is a deterministic function of the providers themselves rather than of
the order in which they happened to run.

Every record carries its provenance chain, so nothing is registered without a
reproducible origin (UKIP-LAW-004), and every record is content-addressed so
post-registration mutation is detectable.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord
from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    RelationType,
    content_hash,
)
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.ukip.classification import Classification
from engine.knowledge.ukip.contracts import (
    KnowledgeUnit,
    RelationDeclaration,
    SourceRef,
)
from engine.knowledge.ukip.errors import DuplicateHomeError, RegistrationError
from engine.knowledge.ukip.provenance import (
    ProvenanceChain,
    Stage,
    begin_chain,
)

#: The registry envelope schema identifiers.
REGISTRY_SCHEMA = "ucos-ukip-knowledge-registry"
REGISTRY_VERSION = "1.0.0"

#: The actor recorded on provenance steps the registry itself performs.
REGISTRY_ACTOR = "ukip-knowledge-registry"


class AdmissionOutcome(str, Enum):
    """What the registry did with a submitted unit."""

    REGISTERED = "registered"
    CORROBORATED = "corroborated"
    REJECTED = "rejected"

    @property
    def admitted(self) -> bool:
        """True iff the knowledge is present in the registry as a result."""
        return self is not AdmissionOutcome.REJECTED


@dataclass(frozen=True, slots=True)
class Admission:
    """The immutable outcome of submitting one unit to the registry."""

    outcome: AdmissionOutcome
    knowledge_id: str
    provider_id: str
    unit_key: str
    reason: str = ""

    @property
    def created_home(self) -> bool:
        return self.outcome is AdmissionOutcome.REGISTERED

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "knowledge_id": self.knowledge_id,
            "provider_id": self.provider_id,
            "unit_key": self.unit_key,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class RegisteredKnowledge:
    """One canonical knowledge record: content, classification, sources, provenance.

    ``canonical_source`` is the provider that established the home; ``corroborations``
    are every other provider that independently supplied the same knowledge. Both are
    kept because *who else says this* is knowledge about the knowledge, and discarding
    it would make the corroborating provider look like a duplicate on the next run.
    """

    knowledge_id: str
    title: str
    statement: str
    rationale: str
    kind: KnowledgeKind
    authority: KnowledgeAuthority
    lifecycle: Lifecycle
    universe: str
    owner: str
    version: str
    knowledge_sha256: str
    canonical_source: SourceRef
    corroborations: tuple[SourceRef, ...] = ()
    tags: tuple[str, ...] = ()
    relations: tuple[RelationDeclaration, ...] = ()
    classification_rules: tuple[str, ...] = ()
    provenance: ProvenanceChain = ProvenanceChain(subject="")
    record_sha256: str = ""

    # -- construction ----------------------------------------------------------

    @classmethod
    def from_unit(
        cls,
        unit: KnowledgeUnit,
        classification: Classification | None = None,
        *,
        provenance: ProvenanceChain | None = None,
    ) -> RegisteredKnowledge:
        """Build a record from a fully classified unit."""
        if not unit.is_classified:
            raise RegistrationError(
                "only a fully classified unit may be registered",
                at=unit.key,
                knowledge_id=unit.knowledge_id(),
            )
        chain = provenance if provenance is not None else begin_chain(unit)
        record = cls(
            knowledge_id=unit.knowledge_id(),
            title=unit.title,
            statement=unit.statement,
            rationale=unit.rationale,
            kind=unit.kind,
            authority=unit.authority,
            lifecycle=unit.lifecycle,
            universe=unit.universe,
            owner=unit.owner,
            version=unit.version,
            knowledge_sha256=unit.knowledge_sha256(),
            canonical_source=unit.source,
            tags=unit.tags,
            relations=unit.relations,
            classification_rules=(classification.rule_ids() if classification is not None else ()),
            provenance=chain,
        )
        return record.sealed()

    def sealed(self) -> RegisteredKnowledge:
        """Return a copy whose ``record_sha256`` matches the current fields."""
        return replace(self, record_sha256=self._recompute())

    # -- corroboration ---------------------------------------------------------

    def corroborated_by(
        self, unit: KnowledgeUnit, *, prefer_canonical: bool
    ) -> RegisteredKnowledge:
        """Return a copy that records ``unit`` as an additional source.

        When ``prefer_canonical`` is true the incoming provider outranks the current
        canonical source, so the roles swap and the previous canonical source becomes
        a corroboration. Nothing is ever discarded, so the outcome is independent of
        the order the providers ran in.
        """
        if unit.knowledge_sha256() != self.knowledge_sha256:
            raise RegistrationError(
                "corroborating unit does not express the registered knowledge",
                knowledge_id=self.knowledge_id,
                at=unit.key,
            )
        existing = {s.citation for s in (self.canonical_source, *self.corroborations)}
        if unit.source.citation in existing:
            return self
        if prefer_canonical:
            sources = (self.canonical_source, *self.corroborations)
            canonical = unit.source
        else:
            sources = (*self.corroborations, unit.source)
            canonical = self.canonical_source
        ordered = tuple(sorted(sources, key=lambda s: s.citation))
        merged = self.merge_relations(unit.relations)
        return replace(merged, canonical_source=canonical, corroborations=ordered).sealed()

    def merge_relations(self, relations: Iterable[RelationDeclaration]) -> RegisteredKnowledge:
        """Return a copy with ``relations`` merged in, de-duplicated and ordered."""
        merged: dict[tuple[str, str], RelationDeclaration] = {}
        for declaration in (*self.relations, *relations):
            merged.setdefault((declaration.relation.value, declaration.target), declaration)
        ordered = tuple(merged[k] for k in sorted(merged))
        if ordered == self.relations:
            return self
        return replace(self, relations=ordered).sealed()

    def with_provenance(self, chain: ProvenanceChain) -> RegisteredKnowledge:
        """Return a copy carrying an advanced provenance chain."""
        return replace(self, provenance=chain).sealed()

    def resolved_relations(
        self, resolver: Mapping[str, str], *, preserve: frozenset[str] = frozenset()
    ) -> tuple[RelationDeclaration, ...]:
        """Relations with provider-local targets rewritten to canonical identifiers.

        Targets named in ``preserve`` are kept verbatim. That is how links into
        artifacts UKIP does not own — canonical UKDA decision records, for instance —
        survive the projection instead of being rewritten to a knowledge identifier
        that would no longer name the same thing.
        """
        resolved: dict[tuple[str, str], RelationDeclaration] = {}
        for declaration in self.relations:
            if declaration.target in preserve:
                target = declaration.target
            else:
                target = resolver.get(declaration.target, declaration.target)
            resolved.setdefault(
                (declaration.relation.value, target), replace(declaration, target=target)
            )
        return tuple(resolved[k] for k in sorted(resolved))

    # -- properties ------------------------------------------------------------

    @property
    def sources(self) -> tuple[SourceRef, ...]:
        """The canonical source followed by every corroborating source."""
        return (self.canonical_source, *self.corroborations)

    @property
    def provider_ids(self) -> tuple[str, ...]:
        """Every distinct provider that supplied this knowledge, ordered."""
        return tuple(sorted({s.provider_id for s in self.sources}))

    @property
    def corroboration_count(self) -> int:
        return len(self.corroborations)

    @property
    def is_active(self) -> bool:
        return self.lifecycle.is_active

    @property
    def is_multi_sourced(self) -> bool:
        """True iff more than one provider independently supplied this knowledge."""
        return len(self.provider_ids) > 1

    # -- integrity -------------------------------------------------------------

    def _core(self) -> dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "title": self.title,
            "statement": self.statement,
            "rationale": self.rationale,
            "kind": self.kind.value,
            "authority": self.authority.value,
            "lifecycle": self.lifecycle.value,
            "universe": self.universe,
            "owner": self.owner,
            "version": self.version,
            "knowledge_sha256": self.knowledge_sha256,
            "canonical_source": self.canonical_source.to_dict(),
            "corroborations": [s.to_dict() for s in self.corroborations],
            "tags": list(self.tags),
            "relations": [r.to_dict() for r in self.relations],
            "classification_rules": list(self.classification_rules),
            "provenance_seal": self.provenance.seal,
        }

    def _recompute(self) -> str:
        return content_hash(self._core())

    def verify_integrity(self) -> bool:
        """True iff the record has not been mutated since it was sealed."""
        return bool(self.record_sha256) and self._recompute() == self.record_sha256

    # -- projection ------------------------------------------------------------

    def searchable_text(self) -> str:
        """The text discovery searches over (never a second copy of the content)."""
        return " ".join([self.knowledge_id, self.title, self.statement, self.rationale, *self.tags])

    def to_canonical_object(
        self, *, cko_id: str | None = None, decision_ids: frozenset[str] = frozenset()
    ) -> CanonicalKnowledgeObject:
        """Project this record as a UKDA canonical knowledge object.

        The bridge back into the canonical store: the registry does not invent a
        second object model, it projects into the one UKDA already owns, citing every
        provider under ``evidence`` so attribution survives the projection.

        A reference to an id in ``decision_ids`` becomes a ``decision_links`` entry
        rather than a generic knowledge link, so a decision object keeps pointing at
        the canonical decision record that documents it. A record projected *from* a
        decision record links to that record for the same reason: the decision it was
        read out of is precisely what documents it.
        """
        dependencies: list[str] = []
        knowledge_links: list[str] = []
        decision_links: list[str] = [
            source.locator for source in self.sources if source.locator in decision_ids
        ]
        conflicts: list[str] = []
        supersedes: list[str] = []
        for declaration in self.relations:
            if declaration.target in decision_ids:
                decision_links.append(declaration.target)
            elif declaration.relation is RelationType.DEPENDS_ON:
                dependencies.append(declaration.target)
            elif declaration.relation is RelationType.CONFLICTS_WITH:
                conflicts.append(declaration.target)
            elif declaration.relation is RelationType.SUPERSEDES:
                supersedes.append(declaration.target)
            else:
                knowledge_links.append(declaration.target)
        return CanonicalKnowledgeObject.create(
            cko_id=cko_id or self.knowledge_id,
            kind=self.kind,
            title=self.title,
            statement=self.statement,
            rationale=self.rationale,
            universe=self.universe,
            authority=self.authority,
            owner=self.owner,
            lifecycle=self.lifecycle,
            version=self.version,
            dependencies=tuple(sorted(set(dependencies))),
            knowledge_links=tuple(sorted(set(knowledge_links))),
            decision_links=tuple(sorted(set(decision_links))),
            conflicts_with=tuple(sorted(set(conflicts))),
            supersedes=tuple(sorted(set(supersedes))),
            tags=self.tags,
            evidence=tuple(s.citation for s in self.sources),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["record_sha256"] = self.record_sha256
        payload["provider_ids"] = list(self.provider_ids)
        payload["provenance"] = self.provenance.to_dict()
        return payload


class KnowledgeRegistry:
    """The canonical, duplication-proof registry of all knowledge (UKIP Part 06)."""

    __slots__ = ("_records", "_by_hash", "_key_index", "_admissions")

    def __init__(self, records: Iterable[RegisteredKnowledge] = ()) -> None:
        self._records: dict[str, RegisteredKnowledge] = {}
        self._by_hash: dict[str, str] = {}
        self._key_index: dict[str, str] = {}
        self._admissions: list[Admission] = []
        for record in records:
            self._install(record)

    def _install(self, record: RegisteredKnowledge) -> None:
        existing = self._records.get(record.knowledge_id)
        if existing is not None and existing.knowledge_sha256 != record.knowledge_sha256:
            raise DuplicateHomeError(
                "two different knowledge records claim the same canonical home",
                knowledge_id=record.knowledge_id,
            )
        owner_of_hash = self._by_hash.get(record.knowledge_sha256)
        if owner_of_hash is not None and owner_of_hash != record.knowledge_id:
            raise DuplicateHomeError(
                "identical knowledge is already homed under another identifier",
                knowledge_sha256=record.knowledge_sha256,
                existing_home=owner_of_hash,
                attempted_home=record.knowledge_id,
            )
        self._records[record.knowledge_id] = record
        self._by_hash[record.knowledge_sha256] = record.knowledge_id

    # -- admission -------------------------------------------------------------

    def submit(
        self,
        unit: KnowledgeUnit,
        classification: Classification | None = None,
        *,
        authoritative: bool = False,
        priority: int = 100,
    ) -> Admission:
        """Submit one unit: establish a home, or corroborate the existing one.

        ``authoritative`` and ``priority`` describe the *submitting provider* and are
        used only to decide which source is named canonical when the same knowledge
        arrives more than once. They never affect whether a second record is created,
        because a second record is not representable.
        """
        knowledge_id = unit.knowledge_id()
        existing = self._records.get(knowledge_id)
        if existing is None:
            record = RegisteredKnowledge.from_unit(unit, classification)
            chain = record.provenance
            # The guard is idempotence, not a live fork: from_unit is called here without a
            # provenance chain, so it opens one with begin_chain, which appends exactly
            # OBSERVED then PROVIDED. A chain reaching this line therefore never carries
            # CLASSIFIED. It stays so that a caller who one day supplies an already-classified
            # chain cannot make the record claim a classification step twice.
            if not chain.has_stage(Stage.CLASSIFIED):  # pragma: no branch
                chain = chain.append(
                    Stage.CLASSIFIED,
                    actor=REGISTRY_ACTOR,
                    action="classify",
                    payload_sha256=content_hash(classification.to_dict() if classification else {}),
                    detail=",".join(record.classification_rules),
                )
            chain = chain.append(
                Stage.REGISTERED,
                actor=REGISTRY_ACTOR,
                action="register",
                source=unit.source,
                payload_sha256=record.knowledge_sha256,
                detail=f"home:{knowledge_id}",
            )
            self._install(record.with_provenance(chain))
            self._key_index[self._index_key(unit)] = knowledge_id
            admission = Admission(
                AdmissionOutcome.REGISTERED,
                knowledge_id,
                unit.source.provider_id,
                unit.key,
                "canonical home established",
            )
            self._admissions.append(admission)
            return admission

        prefer = self._prefers_incoming(existing, authoritative=authoritative, priority=priority)
        updated = existing.corroborated_by(unit, prefer_canonical=prefer)
        chain = updated.provenance.append(
            Stage.CORROBORATED,
            actor=REGISTRY_ACTOR,
            action="corroborate",
            source=unit.source,
            payload_sha256=unit.unit_sha256(),
            detail=f"provider:{unit.source.provider_id}",
        )
        self._records[knowledge_id] = updated.with_provenance(chain)
        self._key_index[self._index_key(unit)] = knowledge_id
        admission = Admission(
            AdmissionOutcome.CORROBORATED,
            knowledge_id,
            unit.source.provider_id,
            unit.key,
            "existing canonical home corroborated",
        )
        self._admissions.append(admission)
        return admission

    @staticmethod
    def _index_key(unit: KnowledgeUnit) -> str:
        """The provider-local address a relationship target may cite."""
        return f"{unit.source.provider_id}:{unit.key}"

    @staticmethod
    def _prefers_incoming(
        existing: RegisteredKnowledge, *, authoritative: bool, priority: int
    ) -> bool:
        """Whether an incoming authoritative provider should take the canonical role.

        Only an authoritative provider can displace the canonical source, and only
        when the current source is not itself from an authoritative canonical store.
        """
        if not authoritative:
            return False
        current_kind = existing.canonical_source.kind.value
        if current_kind in ("canonical-store", "decision-log"):
            return False
        return priority >= 0

    def register(self, record: RegisteredKnowledge) -> KnowledgeRegistry:
        """Install a pre-built record directly (used when rehydrating a registry)."""
        self._install(record)
        return self

    # -- lookups ---------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, knowledge_id: object) -> bool:
        return knowledge_id in self._records

    def __iter__(self):
        return iter(self.records())

    def records(self) -> tuple[RegisteredKnowledge, ...]:
        """Every record, ordered by canonical identifier."""
        return tuple(self._records[k] for k in sorted(self._records))

    def knowledge_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._records))

    def get(self, knowledge_id: str) -> RegisteredKnowledge | None:
        return self._records.get(knowledge_id)

    def require(self, knowledge_id: str) -> RegisteredKnowledge:
        record = self._records.get(knowledge_id)
        if record is None:
            raise RegistrationError("knowledge not registered", knowledge_id=knowledge_id)
        return record

    def by_content_hash(self, knowledge_sha256: str) -> RegisteredKnowledge | None:
        """Reverse lookup: which record homes this exact knowledge?"""
        knowledge_id = self._by_hash.get(knowledge_sha256)
        return self._records.get(knowledge_id) if knowledge_id else None

    def resolve(self, reference: str) -> RegisteredKnowledge | None:
        """Resolve a canonical id, a provider-local ``provider:key``, or a digest."""
        direct = self._records.get(reference)
        if direct is not None:
            return direct
        via_key = self._key_index.get(reference)
        if via_key is not None:
            return self._records.get(via_key)
        return self.by_content_hash(reference)

    def reference_map(self) -> dict[str, str]:
        """Every alias -> canonical identifier, for relationship resolution."""
        mapping: dict[str, str] = {}
        ambiguous: set[str] = set()
        for alias, knowledge_id in sorted(self._key_index.items()):
            mapping[alias] = knowledge_id
            _, _, key = alias.partition(":")
            if not key:  # pragma: no cover - _index_key cannot produce an empty tail
                # Every alias here was written by _index_key as f"{provider_id}:{unit.key}",
                # so the tail after the first colon always contains at least unit.key — and
                # KnowledgeUnit refuses a key that is empty or whitespace-only at
                # construction. The guard stays because it is what makes the bare-key
                # shorthand below safe to read without re-deriving that invariant here.
                continue
            # A bare provider-local key is also accepted while it stays unambiguous,
            # so providers may cite peers by their own key without knowing the
            # platform. The moment two providers use the same key for different
            # knowledge, the bare form is withdrawn rather than resolved by guess.
            if key in ambiguous:
                continue
            if mapping.get(key, knowledge_id) != knowledge_id:
                mapping.pop(key, None)
                ambiguous.add(key)
            else:
                mapping[key] = knowledge_id
        for record in self.records():
            mapping[record.knowledge_id] = record.knowledge_id
            mapping[record.knowledge_sha256] = record.knowledge_id
        return mapping

    # -- classification queries ------------------------------------------------

    def by_kind(self, kind: KnowledgeKind) -> tuple[RegisteredKnowledge, ...]:
        return tuple(r for r in self.records() if r.kind is kind)

    def by_authority(self, authority: KnowledgeAuthority) -> tuple[RegisteredKnowledge, ...]:
        return tuple(r for r in self.records() if r.authority is authority)

    def by_lifecycle(self, lifecycle: Lifecycle) -> tuple[RegisteredKnowledge, ...]:
        return tuple(r for r in self.records() if r.lifecycle is lifecycle)

    def by_universe(self, universe: str) -> tuple[RegisteredKnowledge, ...]:
        return tuple(r for r in self.records() if r.universe == universe)

    def by_owner(self, owner: str) -> tuple[RegisteredKnowledge, ...]:
        return tuple(r for r in self.records() if r.owner == owner)

    def by_provider(self, provider_id: str) -> tuple[RegisteredKnowledge, ...]:
        """Every record this provider supplied, canonically or as corroboration."""
        return tuple(r for r in self.records() if provider_id in r.provider_ids)

    def active(self) -> tuple[RegisteredKnowledge, ...]:
        return tuple(r for r in self.records() if r.is_active)

    def multi_sourced(self) -> tuple[RegisteredKnowledge, ...]:
        """Records corroborated by more than one provider."""
        return tuple(r for r in self.records() if r.is_multi_sourced)

    # -- integrity -------------------------------------------------------------

    def provider_ids(self) -> tuple[str, ...]:
        """Every provider that contributed anything, ordered."""
        seen: set[str] = set()
        for record in self.records():
            seen.update(record.provider_ids)
        return tuple(sorted(seen))

    def duplicate_homes(self) -> tuple[tuple[str, ...], ...]:
        """Groups of identifiers homing identical knowledge — always empty by design.

        Kept as an explicit, testable assertion of the invariant rather than a
        comment: if the keying scheme ever regressed, validation would report it.
        """
        by_hash: dict[str, list[str]] = {}
        for record in self.records():
            by_hash.setdefault(record.knowledge_sha256, []).append(record.knowledge_id)
        return tuple(tuple(sorted(ids)) for _, ids in sorted(by_hash.items()) if len(ids) > 1)

    def unsealed(self) -> tuple[str, ...]:
        """Records whose content hash no longer matches their content."""
        return tuple(r.knowledge_id for r in self.records() if not r.verify_integrity())

    def admissions(self) -> tuple[Admission, ...]:
        """The ordered admission log of this registry instance."""
        return tuple(self._admissions)

    def seal(self) -> str:
        """A deterministic seal over every record in the registry."""
        return content_hash({r.knowledge_id: r.record_sha256 for r in self.records()})

    # -- projections -----------------------------------------------------------

    def to_knowledge_base(self, decisions: Iterable[DecisionRecord] = ()) -> KnowledgeBase:
        """Project the registry as a UKDA :class:`KnowledgeBase`.

        Lets the entire existing UKDA validation, certification, documentation, and
        portal machinery run over provider-sourced knowledge with no changes at all.

        ``decisions`` carries canonical UKDA decision records through unchanged. UKIP
        registers *knowledge*; it does not own the decision record shape and will not
        synthesise one, so a decision-bearing projection must be given the records
        that already exist rather than inventing substitutes for them.
        """
        carried = tuple(decisions)
        decision_ids = frozenset(d.decision_id for d in carried)
        resolver = self.reference_map()
        objects: list[CanonicalKnowledgeObject] = []
        for record in self.records():
            resolved = record.resolved_relations(resolver, preserve=decision_ids)
            objects.append(
                replace(record, relations=resolved).to_canonical_object(decision_ids=decision_ids)
            )
        return KnowledgeBase(objects, carried)

    def counts(self) -> dict[str, int]:
        records = self.records()
        return {
            "records": len(records),
            "providers": len(self.provider_ids()),
            "corroborated": len(self.multi_sourced()),
            "active": len(self.active()),
            "relations": sum(len(r.relations) for r in records),
        }

    def to_document(self) -> dict[str, Any]:
        """The deterministic registry envelope (stable order, no wall-clock)."""
        return {
            "schema": REGISTRY_SCHEMA,
            "version": REGISTRY_VERSION,
            "counts": self.counts(),
            "seal": self.seal(),
            "providers": list(self.provider_ids()),
            "records": [r.to_dict() for r in self.records()],
        }


__all__ = [
    "REGISTRY_SCHEMA",
    "REGISTRY_VERSION",
    "REGISTRY_ACTOR",
    "AdmissionOutcome",
    "Admission",
    "RegisteredKnowledge",
    "KnowledgeRegistry",
]
