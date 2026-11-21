"""UCKP Layer Zero — the Universal Constitutional Knowledge Object (Articles 2, 5, 6).

The UCKO is the only thing in UCOS Ω∞ that holds authority. Everything else — every
repository, document, file, schema, module, table, graph, interface and future
technology — is a view of one, an environment that acts on one, or a mechanism that
stores one.

The object carries all thirty-three universal facets as typed, immutable fields, one
per facet, so :meth:`UniversalConstitutionalKnowledgeObject.facet_value` is total:
every question the law says an object must answer has a field that answers it. Facet
completeness is therefore a structural property, not a convention someone has to
remember.

Three properties are worth stating explicitly because they are what make the rest of
Layer Zero possible:

    * **Content-addressed.** ``content_sha256`` seals the whole facet core through the
      one canonical form (Article 13). Any later edit is detectable by anyone,
      anywhere, with no access to the original.
    * **Semantically addressed.** :meth:`semantic_digest` hashes *meaning* alone, so
      renaming a duplicate does not hide it (Article 3).
    * **Self-proving.** :meth:`verify_replay` re-derives the object's substance digest
      and compares it to the recorded proof, so "this object is reproducible" is a
      check rather than a claim (Article 13, Invariant 15).

Construction goes through :meth:`create` or :meth:`mint`. The raw constructor is
deliberately still reachable: a law that cannot be violated in the type system is a
law whose enforcement is never tested, so an incomplete object is *representable* and
:meth:`require_complete` is what refuses it.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.uckp.canonical import content_hash
from engine.uckp.errors import (
    FacetError,
    IntegrityError,
    LawViolation,
)
from engine.uckp.facets import REQUIRED_FACETS, Facet
from engine.uckp.identity import UniversalIdentity
from engine.uckp.values import (
    UNATTESTED,
    Attestation,
    AuditEntry,
    AuthorityBinding,
    Constraint,
    ContextBinding,
    DiscoveryDescriptor,
    EvidenceRef,
    MetadataSet,
    OntologyRef,
    Ownership,
    PersistenceBinding,
    Policy,
    ProjectionBinding,
    ProvenanceStep,
    Relationship,
    ReplayProof,
    RuntimeBinding,
    SemanticIdentity,
    TaxonomyRef,
    TemporalEvent,
    TraceLink,
)
from engine.uckp.vocabulary import (
    AUTHORITY_TIER,
    GOVERNED_CATEGORY,
    KNOWLEDGE_KIND,
    LIFECYCLE_STAGE,
    RELATION_TYPE,
    RELATIONSHIP_CLASS,
    VocabularyRegistry,
)

#: The procedure name recorded in the replay proof of a minted object.
MINT_PROCEDURE = "uckp.mint/1.0.0"

#: The ontology every Layer Zero object is classified under by default.
DEFAULT_ONTOLOGY = "uckp.core-ontology/1.0.0"

_DEFAULT_CERTIFICATION = Attestation("certification")
_DEFAULT_VALIDATION = Attestation("validation")
_DEFAULT_VERIFICATION = Attestation("verification")
_DEFAULT_SECURITY = ContextBinding("security", "constitutional-read-open-write-owner")
_DEFAULT_GOVERNANCE = ContextBinding("governance", "uckp-root-authority")
_DEFAULT_COMPLIANCE = ContextBinding("compliance", "uckp-root-law")
_DEFAULT_KNOWLEDGE = ContextBinding("knowledge", "ucos-omega-infinity")
_DEFAULT_OBSERVER = ContextBinding("observer", "constitutional-observer")
_DEFAULT_EXISTENCE = ContextBinding("existence", "declared-and-registered")


@dataclass(frozen=True, slots=True)
class UniversalConstitutionalKnowledgeObject:
    """The canonical object: one per constitutional entity, and never a second."""

    # Facet 1-7 — what it is, what it means, and by whose authority.
    identity: UniversalIdentity
    semantic_identity: SemanticIdentity
    ontology: OntologyRef
    taxonomy: TaxonomyRef
    authority: AuthorityBinding
    ownership: Ownership
    lifecycle: str
    # Facet 6, 8-11 — where it came from and what it is bound to.
    provenance: tuple[ProvenanceStep, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    relationships: tuple[Relationship, ...] = field(default_factory=tuple)
    temporal_history: tuple[TemporalEvent, ...] = field(default_factory=tuple)
    # Facet 12-16 — what has been judged about it and on what proof.
    certification: Attestation = _DEFAULT_CERTIFICATION
    validation: Attestation = _DEFAULT_VALIDATION
    verification: Attestation = _DEFAULT_VERIFICATION
    traceability: tuple[TraceLink, ...] = field(default_factory=tuple)
    evidence: tuple[EvidenceRef, ...] = field(default_factory=tuple)
    # Facet 17-24 — the conditions of its truth and the rules of its use.
    context: tuple[ContextBinding, ...] = field(default_factory=tuple)
    evolution_history: tuple[str, ...] = field(default_factory=tuple)
    replay: ReplayProof | None = None
    audit: tuple[AuditEntry, ...] = field(default_factory=tuple)
    discovery: DiscoveryDescriptor = DiscoveryDescriptor()
    metadata: MetadataSet = MetadataSet()
    constraints: tuple[Constraint, ...] = field(default_factory=tuple)
    policies: tuple[Policy, ...] = field(default_factory=tuple)
    # Facet 25-27 — the environments and mechanisms that may touch it.
    runtime_bindings: tuple[RuntimeBinding, ...] = field(default_factory=tuple)
    projection_bindings: tuple[ProjectionBinding, ...] = field(default_factory=tuple)
    persistence_bindings: tuple[PersistenceBinding, ...] = field(default_factory=tuple)
    # Facet 28-33 — the six named contexts of its existence.
    security_context: ContextBinding = _DEFAULT_SECURITY
    governance_context: ContextBinding = _DEFAULT_GOVERNANCE
    compliance_context: ContextBinding = _DEFAULT_COMPLIANCE
    knowledge_context: ContextBinding = _DEFAULT_KNOWLEDGE
    observer_context: ContextBinding = _DEFAULT_OBSERVER
    existence_context: ContextBinding = _DEFAULT_EXISTENCE
    # The seal.
    content_sha256: str = ""

    # --- identity ---------------------------------------------------------------

    @property
    def ucko_id(self) -> str:
        """The canonical identity of the object — its URN."""
        return self.identity.urn

    @property
    def local_name(self) -> str:
        return self.identity.local_name

    # --- construction -----------------------------------------------------------

    @classmethod
    def create(cls, **fields: Any) -> UniversalConstitutionalKnowledgeObject:
        """Construct and seal an object, deriving the replay proof from its substance."""
        provisional = cls(**fields)
        if provisional.replay is None:
            subject = provisional.substance_digest()
            provisional = dataclasses.replace(
                provisional,
                replay=ReplayProof(
                    procedure=MINT_PROCEDURE,
                    input_digest=provisional.semantic_digest(),
                    output_digest=subject,
                ),
            )
        return provisional.sealed()

    @classmethod
    def mint(
        cls,
        *,
        namespace: str,
        local_name: str,
        concept: str,
        definition: str,
        kind: str,
        category: str,
        authority_tier: str,
        derives_from: str,
        owner: str,
        lifecycle: str = "ratified",
        ontology_class: str = "",
        taxonomy_path: Iterable[str] = (),
        tags: Iterable[str] = (),
        provenance: Iterable[ProvenanceStep] = (),
        dependencies: Iterable[str] = (),
        relationships: Iterable[Relationship] = (),
        metadata: Mapping[str, Any] | None = None,
        evidence: Iterable[EvidenceRef] = (),
        constraints: Iterable[Constraint] = (),
        policies: Iterable[Policy] = (),
        runtime_bindings: Iterable[RuntimeBinding] = (),
        projection_bindings: Iterable[ProjectionBinding] = (),
        persistence_bindings: Iterable[PersistenceBinding] = (),
        keywords: Iterable[str] = (),
        provider: str = "",
        instrument: str = "",
        **overrides: Any,
    ) -> UniversalConstitutionalKnowledgeObject:
        """Mint a complete object from its essential facts, deriving the rest.

        This is the ergonomic path: a caller states what the thing *is* and Layer Zero
        derives identity, semantic identity, the replay proof, the six named contexts,
        the discovery descriptor, the opening audit entry and the seal. Deriving them
        is what makes Article 8 true — an object self-describes because nothing had to
        be filled in by hand and therefore nothing can be left out.
        """
        identity = UniversalIdentity.mint(namespace, local_name)
        semantic = SemanticIdentity(concept=concept, definition=definition)
        steps = tuple(provenance) or (
            ProvenanceStep(
                actor=owner,
                action="declared",
                source=instrument or "engine.uckp.law",
                digest=semantic.digest(),
            ),
        )
        fields: dict[str, Any] = {
            "identity": identity,
            "semantic_identity": semantic,
            "ontology": OntologyRef(
                ontology_id=DEFAULT_ONTOLOGY,
                class_id=ontology_class or category,
                superclasses=(category,) if ontology_class else (),
            ),
            "taxonomy": TaxonomyRef(
                kind=kind,
                category=category,
                path=tuple(taxonomy_path) or (category, kind),
                tags=tuple(sorted(tags)),
            ),
            "authority": AuthorityBinding(
                tier=authority_tier, derives_from=derives_from, instrument=instrument
            ),
            "ownership": Ownership(owner=owner),
            "lifecycle": lifecycle,
            "provenance": steps,
            "dependencies": tuple(dependencies),
            "relationships": tuple(relationships),
            "temporal_history": (TemporalEvent(sequence=0, event=f"minted:{lifecycle}"),),
            "evidence": tuple(evidence),
            "context": (ContextBinding("declaration", instrument or "engine.uckp.law"),),
            "audit": (
                AuditEntry(
                    actor=owner,
                    action="mint",
                    subject=identity.urn,
                    digest=semantic.digest(),
                ),
            ),
            "discovery": DiscoveryDescriptor(
                discoverable=True,
                self_describing=True,
                provider=provider or "engine.uckp",
                keywords=tuple(sorted({*keywords, kind, category})),
            ),
            "metadata": MetadataSet.of(metadata),
            "constraints": tuple(constraints),
            "policies": tuple(policies),
            "runtime_bindings": tuple(runtime_bindings),
            "projection_bindings": tuple(projection_bindings),
            "persistence_bindings": tuple(persistence_bindings),
        }
        fields.update(overrides)
        return cls.create(**fields)

    # --- sealing and integrity --------------------------------------------------

    def _facet_core(self) -> dict[str, Any]:
        """The canonical facet core: every facet, no seal."""
        return {
            "identity": self.identity.to_dict(),
            "semantic_identity": self.semantic_identity.to_dict(),
            "ontology": self.ontology.to_dict(),
            "taxonomy": self.taxonomy.to_dict(),
            "authority": self.authority.to_dict(),
            "provenance": [item.to_dict() for item in self.provenance],
            "ownership": self.ownership.to_dict(),
            "dependencies": list(self.dependencies),
            "relationships": [item.to_dict() for item in self.relationships],
            "lifecycle": self.lifecycle,
            "temporal_history": [item.to_dict() for item in self.temporal_history],
            "certification": self.certification.to_dict(),
            "validation": self.validation.to_dict(),
            "verification": self.verification.to_dict(),
            "traceability": [item.to_dict() for item in self.traceability],
            "evidence": [item.to_dict() for item in self.evidence],
            "context": [item.to_dict() for item in self.context],
            "evolution_history": list(self.evolution_history),
            "replay": self.replay.to_dict() if self.replay is not None else None,
            "audit": [item.to_dict() for item in self.audit],
            "discovery": self.discovery.to_dict(),
            "metadata": self.metadata.to_dict(),
            "constraints": [item.to_dict() for item in self.constraints],
            "policies": [item.to_dict() for item in self.policies],
            "runtime_bindings": [item.to_dict() for item in self.runtime_bindings],
            "projection_bindings": [item.to_dict() for item in self.projection_bindings],
            "persistence_bindings": [item.to_dict() for item in self.persistence_bindings],
            "security_context": self.security_context.to_dict(),
            "governance_context": self.governance_context.to_dict(),
            "compliance_context": self.compliance_context.to_dict(),
            "knowledge_context": self.knowledge_context.to_dict(),
            "observer_context": self.observer_context.to_dict(),
            "existence_context": self.existence_context.to_dict(),
        }

    def substance_digest(self) -> str:
        """The digest of every facet except the replay proof itself.

        The replay proof asserts that re-deriving the object reproduces its substance.
        Excluding the proof from the digest it certifies is what keeps the assertion
        well-founded rather than self-referential.
        """
        core = self._facet_core()
        core.pop("replay", None)
        return content_hash(core)

    def semantic_digest(self) -> str:
        """The digest of meaning alone — the duplicate-detection identity."""
        return self.semantic_identity.digest()

    def sealed(self) -> UniversalConstitutionalKnowledgeObject:
        """Return the object with ``content_sha256`` recomputed."""
        return dataclasses.replace(self, content_sha256=content_hash(self._facet_core()))

    def verify_integrity(self) -> bool:
        """True iff the seal still matches the facet core."""
        return bool(self.content_sha256) and self.content_sha256 == content_hash(self._facet_core())

    def require_integrity(self) -> None:
        if not self.verify_integrity():
            raise IntegrityError(
                "constitutional knowledge object was mutated after sealing",
                ucko_id=self.ucko_id,
            )

    def verify_replay(self) -> bool:
        """True iff the recorded replay proof still holds for this object."""
        return self.replay is not None and self.replay.holds(self.substance_digest())

    # --- facets -----------------------------------------------------------------

    def facet_value(self, facet: Facet | str) -> Any:
        """Return the value carried for ``facet``. Total over every facet."""
        resolved = Facet.coerce(facet)
        return getattr(self, resolved.attribute)

    def missing_facets(self) -> tuple[Facet, ...]:
        """Facets carrying no answer at all (Article 6 forbids all of these)."""
        missing: list[Facet] = []
        for facet in REQUIRED_FACETS:
            value = self.facet_value(facet)
            if value is None:
                missing.append(facet)
                continue
            if isinstance(value, str) and not value.strip():
                missing.append(facet)
        return tuple(missing)

    def unattested_facets(self) -> tuple[Facet, ...]:
        """Facets that are present but on which no authority has yet spoken."""
        unattested: list[Facet] = []
        for facet in (Facet.CERTIFICATION, Facet.VALIDATION, Facet.VERIFICATION):
            attestation = self.facet_value(facet)
            if isinstance(attestation, Attestation) and not attestation.attested:
                unattested.append(facet)
        return tuple(unattested)

    def require_complete(self) -> None:
        """Fail closed unless every facet carries an answer (Article 6)."""
        missing = self.missing_facets()
        if missing:
            raise FacetError(
                "object does not answer every universal facet",
                ucko_id=self.ucko_id,
                missing=[facet.value for facet in missing],
            )

    def require_lawful(self, vocabularies: VocabularyRegistry) -> None:
        """Fail closed unless every vocabulary-bound facet uses a registered term.

        Openness is register-then-use (Article 17): an unknown kind, tier, stage,
        relation or class is admitted by registration and refused until it is.
        """
        self.require_complete()
        vocabularies.require_term(KNOWLEDGE_KIND, self.taxonomy.kind)
        vocabularies.require_term(GOVERNED_CATEGORY, self.taxonomy.category)
        vocabularies.require_term(AUTHORITY_TIER, self.authority.tier)
        vocabularies.require_term(LIFECYCLE_STAGE, self.lifecycle)
        for relationship in self.relationships:
            vocabularies.require_term(RELATION_TYPE, relationship.relation)
            vocabularies.require_term(RELATIONSHIP_CLASS, relationship.relationship_class)

    # --- lawful evolution -------------------------------------------------------

    def transition_to(
        self, stage: str, vocabularies: VocabularyRegistry, *, state_id: str = ""
    ) -> UniversalConstitutionalKnowledgeObject:
        """Return a new object in ``stage``, recording the transition (Article 12)."""
        lifecycle = vocabularies.require(LIFECYCLE_STAGE)
        if not lifecycle.can_transition(self.lifecycle, stage):
            raise LawViolation(
                "unlawful lifecycle transition",
                ucko_id=self.ucko_id,
                source=self.lifecycle,
                target=str(stage),
            )
        event = TemporalEvent(
            sequence=len(self.temporal_history),
            event=f"transition:{self.lifecycle}->{stage}",
            state_id=state_id,
        )
        entry = AuditEntry(
            actor=self.ownership.owner,
            action="transition",
            subject=self.ucko_id,
            digest=self.content_sha256,
        )
        return dataclasses.replace(
            self,
            lifecycle=str(stage),
            temporal_history=(*self.temporal_history, event),
            audit=(*self.audit, entry),
            replay=None,
        ).create_from_self()

    def create_from_self(self) -> UniversalConstitutionalKnowledgeObject:
        """Re-derive the replay proof and seal after a lawful facet change."""
        return type(self).create(
            **{
                f.name: getattr(self, f.name)
                for f in dataclasses.fields(self)
                if f.name != "content_sha256"
            }
        )

    def with_relationships(
        self, *relationships: Relationship
    ) -> UniversalConstitutionalKnowledgeObject:
        merged = {(r.relation, r.target, r.relationship_class): r for r in self.relationships}
        for relationship in relationships:
            merged[
                (relationship.relation, relationship.target, relationship.relationship_class)
            ] = relationship
        ordered = tuple(merged[key] for key in sorted(merged))
        return dataclasses.replace(self, relationships=ordered, replay=None).create_from_self()

    def with_projection_binding(
        self, binding: ProjectionBinding
    ) -> UniversalConstitutionalKnowledgeObject:
        return dataclasses.replace(
            self,
            projection_bindings=(*self.projection_bindings, binding),
            replay=None,
        ).create_from_self()

    def with_persistence_binding(
        self, binding: PersistenceBinding
    ) -> UniversalConstitutionalKnowledgeObject:
        return dataclasses.replace(
            self,
            persistence_bindings=(*self.persistence_bindings, binding),
            replay=None,
        ).create_from_self()

    def with_runtime_binding(
        self, binding: RuntimeBinding
    ) -> UniversalConstitutionalKnowledgeObject:
        return dataclasses.replace(
            self,
            runtime_bindings=(*self.runtime_bindings, binding),
            replay=None,
        ).create_from_self()

    def with_attestation(self, attestation: Attestation) -> UniversalConstitutionalKnowledgeObject:
        """Record a certification, validation or verification judgement."""
        facet_by_kind = {
            "certification": "certification",
            "validation": "validation",
            "verification": "verification",
        }
        attribute = facet_by_kind.get(attestation.kind)
        if attribute is None:
            raise FacetError("unknown attestation kind", kind=attestation.kind)
        return dataclasses.replace(self, **{attribute: attestation}, replay=None).create_from_self()

    def with_evidence(self, *refs: EvidenceRef) -> UniversalConstitutionalKnowledgeObject:
        return dataclasses.replace(
            self, evidence=(*self.evidence, *refs), replay=None
        ).create_from_self()

    def with_evolution_state(self, state_id: str) -> UniversalConstitutionalKnowledgeObject:
        if state_id in self.evolution_history:
            return self
        return dataclasses.replace(
            self, evolution_history=(*self.evolution_history, str(state_id)), replay=None
        ).create_from_self()

    def with_audit(self, entry: AuditEntry) -> UniversalConstitutionalKnowledgeObject:
        return dataclasses.replace(self, audit=(*self.audit, entry), replay=None).create_from_self()

    # --- graph and discovery surfaces -------------------------------------------

    def referenced_ids(self) -> tuple[str, ...]:
        """Every object identity this object points at."""
        targets = {
            *self.dependencies,
            *(r.target for r in self.relationships),
            *(link.upstream for link in self.traceability),
            *(link.downstream for link in self.traceability),
        }
        if self.authority.derives_from and self.authority.derives_from != self.ucko_id:
            targets.add(self.authority.derives_from)
        return tuple(sorted(target for target in targets if target))

    def describe(self) -> dict[str, Any]:
        """The machine-readable self-description (Article 8)."""
        return {
            "ucko_id": self.ucko_id,
            "uuid": self.identity.uuid,
            "concept": self.semantic_identity.concept,
            "semantic_digest": self.semantic_digest(),
            "kind": self.taxonomy.kind,
            "category": self.taxonomy.category,
            "authority_tier": self.authority.tier,
            "derives_from": self.authority.derives_from,
            "owner": self.ownership.owner,
            "lifecycle": self.lifecycle,
            "facets": [facet.value for facet in REQUIRED_FACETS],
            "unattested": [facet.value for facet in self.unattested_facets()],
            "keywords": list(self.discovery.keywords),
            "content_sha256": self.content_sha256,
        }

    # --- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        record = self._facet_core()
        record["content_sha256"] = self.content_sha256
        return record

    @classmethod
    def from_dict(cls, data: Any) -> UniversalConstitutionalKnowledgeObject:
        if not isinstance(data, Mapping):
            raise FacetError("object record must be a mapping")
        replay = data.get("replay")
        obj = cls(
            identity=UniversalIdentity.from_dict(data.get("identity")),
            semantic_identity=SemanticIdentity.from_dict(data.get("semantic_identity")),
            ontology=OntologyRef.from_dict(data.get("ontology")),
            taxonomy=TaxonomyRef.from_dict(data.get("taxonomy")),
            authority=AuthorityBinding.from_dict(data.get("authority")),
            ownership=Ownership.from_dict(data.get("ownership")),
            lifecycle=str(data.get("lifecycle", "")).strip(),
            provenance=tuple(
                ProvenanceStep.from_dict(item) for item in data.get("provenance") or ()
            ),
            dependencies=tuple(str(item) for item in data.get("dependencies") or ()),
            relationships=tuple(
                Relationship.from_dict(item) for item in data.get("relationships") or ()
            ),
            temporal_history=tuple(
                TemporalEvent.from_dict(item) for item in data.get("temporal_history") or ()
            ),
            certification=Attestation.from_dict(
                data.get("certification") or {"kind": "certification"}
            ),
            validation=Attestation.from_dict(data.get("validation") or {"kind": "validation"}),
            verification=Attestation.from_dict(
                data.get("verification") or {"kind": "verification"}
            ),
            traceability=tuple(
                TraceLink.from_dict(item) for item in data.get("traceability") or ()
            ),
            evidence=tuple(EvidenceRef.from_dict(item) for item in data.get("evidence") or ()),
            context=tuple(ContextBinding.from_dict(item) for item in data.get("context") or ()),
            evolution_history=tuple(str(item) for item in data.get("evolution_history") or ()),
            replay=ReplayProof.from_dict(replay) if replay else None,
            audit=tuple(AuditEntry.from_dict(item) for item in data.get("audit") or ()),
            discovery=DiscoveryDescriptor.from_dict(data.get("discovery")),
            metadata=MetadataSet.from_dict(data.get("metadata")),
            constraints=tuple(Constraint.from_dict(item) for item in data.get("constraints") or ()),
            policies=tuple(Policy.from_dict(item) for item in data.get("policies") or ()),
            runtime_bindings=tuple(
                RuntimeBinding.from_dict(item) for item in data.get("runtime_bindings") or ()
            ),
            projection_bindings=tuple(
                ProjectionBinding.from_dict(item) for item in data.get("projection_bindings") or ()
            ),
            persistence_bindings=tuple(
                PersistenceBinding.from_dict(item)
                for item in data.get("persistence_bindings") or ()
            ),
            security_context=ContextBinding.from_dict(data.get("security_context")),
            governance_context=ContextBinding.from_dict(data.get("governance_context")),
            compliance_context=ContextBinding.from_dict(data.get("compliance_context")),
            knowledge_context=ContextBinding.from_dict(data.get("knowledge_context")),
            observer_context=ContextBinding.from_dict(data.get("observer_context")),
            existence_context=ContextBinding.from_dict(data.get("existence_context")),
            content_sha256=str(data.get("content_sha256", "")),
        )
        if obj.content_sha256:
            obj.require_integrity()
            return obj
        return obj.sealed()


#: The short public alias. The full name states what the object *is*; the alias is
#: what callers type.
UCKO = UniversalConstitutionalKnowledgeObject


__all__ = [
    "DEFAULT_ONTOLOGY",
    "MINT_PROCEDURE",
    "UCKO",
    "UNATTESTED",
    "UniversalConstitutionalKnowledgeObject",
]
