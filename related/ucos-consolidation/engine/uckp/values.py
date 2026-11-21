"""UCKP Layer Zero — the facet value types.

Every facet of a UCKO is carried by an immutable value type declared here. They are
deliberately small, total and free of behaviour beyond serialization and their own
integrity: a value type that can reach out to a store, a clock or a network is a
value type whose digest is not reproducible, and Article 13 requires that identical
inputs always produce identical bytes.

Two conventions hold throughout:

    * ``to_dict`` / ``from_dict`` are exact inverses, so a UCKO survives every
      persistence and projection round trip with no loss (Article 19).
    * No field defaults to ``None`` where the law demands an answer. Where nothing
      has been attested yet the value is the explicit sentinel ``UNATTESTED`` rather
      than absence, because Article 6 distinguishes "not yet judged" from
      "unanswerable".
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.uckp.canonical import content_hash
from engine.uckp.errors import FacetError, ProjectionAuthorityError

#: The verdict of an attestation that no authority has yet judged.
UNATTESTED = "unattested"

#: The temporal coordinate of an object whose history is stated in constitutional
#: state sequence rather than wall-clock time. Layer Zero never reads a clock; a
#: caller that has a trustworthy timestamp supplies it, and a caller that does not
#: says so, rather than inventing one.
TIMELESS = "timeless"


def _text(value: Any, field_name: str, *, required: bool = True) -> str:
    text = "" if value is None else str(value).strip()
    if required and not text:
        raise FacetError("facet field is required", field=field_name)
    return text


def _tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raise FacetError("facet field must be a sequence, not a string", field=field_name)
    return tuple(str(item) for item in value)


def _mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise FacetError("facet field must be a mapping", field=field_name)
    return value


@dataclass(frozen=True, slots=True)
class SemanticIdentity:
    """What an object *means*, independent of what it is called (Facet 2).

    The digest is computed from the normalised concept and definition alone, so two
    objects that say the same thing under different names, owners or versions
    collide — which is precisely how Article 3 detects a duplicate that renaming
    was meant to hide.
    """

    concept: str
    definition: str

    def __post_init__(self) -> None:
        _text(self.concept, "semantic_identity.concept")
        _text(self.definition, "semantic_identity.definition")

    def normalised(self) -> dict[str, str]:
        return {
            "concept": " ".join(self.concept.split()).casefold(),
            "definition": " ".join(self.definition.split()).casefold(),
        }

    def digest(self) -> str:
        return content_hash(self.normalised())

    def to_dict(self) -> dict[str, str]:
        return {"concept": self.concept, "definition": self.definition, "digest": self.digest()}

    @classmethod
    def from_dict(cls, data: Any) -> SemanticIdentity:
        record = _mapping(data, "semantic_identity")
        return cls(
            concept=_text(record.get("concept"), "semantic_identity.concept"),
            definition=_text(record.get("definition"), "semantic_identity.definition"),
        )


@dataclass(frozen=True, slots=True)
class OntologyRef:
    """What kind of being an object is (Facet 3)."""

    ontology_id: str
    class_id: str
    superclasses: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "ontology_id": self.ontology_id,
            "class_id": self.class_id,
            "superclasses": list(self.superclasses),
        }

    @classmethod
    def from_dict(cls, data: Any) -> OntologyRef:
        record = _mapping(data, "ontology")
        return cls(
            ontology_id=_text(record.get("ontology_id"), "ontology.ontology_id"),
            class_id=_text(record.get("class_id"), "ontology.class_id"),
            superclasses=_tuple(record.get("superclasses"), "ontology.superclasses"),
        )


@dataclass(frozen=True, slots=True)
class TaxonomyRef:
    """Where an object sits in the classification of knowledge (Facet 4)."""

    kind: str
    category: str
    path: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "category": self.category,
            "path": list(self.path),
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: Any) -> TaxonomyRef:
        record = _mapping(data, "taxonomy")
        return cls(
            kind=_text(record.get("kind"), "taxonomy.kind"),
            category=_text(record.get("category"), "taxonomy.category"),
            path=_tuple(record.get("path"), "taxonomy.path"),
            tags=_tuple(record.get("tags"), "taxonomy.tags"),
        )


@dataclass(frozen=True, slots=True)
class AuthorityBinding:
    """By what authority an object exists, and from whom that is derived (Facet 5).

    ``derives_from`` is the URN of the single parent authority. Exactly one parent
    is permitted: two parents is two authorities over one object, which Article 1
    forbids. The root law is the only object whose ``derives_from`` is itself.
    """

    tier: str
    derives_from: str
    instrument: str = ""

    def __post_init__(self) -> None:
        _text(self.tier, "authority.tier")
        _text(self.derives_from, "authority.derives_from")

    def to_dict(self) -> dict[str, str]:
        return {
            "tier": self.tier,
            "derives_from": self.derives_from,
            "instrument": self.instrument,
        }

    @classmethod
    def from_dict(cls, data: Any) -> AuthorityBinding:
        record = _mapping(data, "authority")
        return cls(
            tier=_text(record.get("tier"), "authority.tier"),
            derives_from=_text(record.get("derives_from"), "authority.derives_from"),
            instrument=_text(record.get("instrument"), "authority.instrument", required=False),
        )


@dataclass(frozen=True, slots=True)
class ProvenanceStep:
    """One hand an object passed through (Facet 6)."""

    actor: str
    action: str
    source: str
    digest: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "actor": self.actor,
            "action": self.action,
            "source": self.source,
            "digest": self.digest,
        }

    @classmethod
    def from_dict(cls, data: Any) -> ProvenanceStep:
        record = _mapping(data, "provenance")
        return cls(
            actor=_text(record.get("actor"), "provenance.actor"),
            action=_text(record.get("action"), "provenance.action"),
            source=_text(record.get("source"), "provenance.source"),
            digest=_text(record.get("digest"), "provenance.digest", required=False),
        )


@dataclass(frozen=True, slots=True)
class Ownership:
    """Who is accountable for an object (Facet 7)."""

    owner: str
    stewards: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.owner, "ownership.owner")

    def to_dict(self) -> dict[str, object]:
        return {"owner": self.owner, "stewards": list(self.stewards)}

    @classmethod
    def from_dict(cls, data: Any) -> Ownership:
        record = _mapping(data, "ownership")
        return cls(
            owner=_text(record.get("owner"), "ownership.owner"),
            stewards=_tuple(record.get("stewards"), "ownership.stewards"),
        )


@dataclass(frozen=True, slots=True)
class Relationship:
    """An executable binding to another object (Facet 9)."""

    relation: str
    target: str
    relationship_class: str

    def __post_init__(self) -> None:
        _text(self.relation, "relationship.relation")
        _text(self.target, "relationship.target")
        _text(self.relationship_class, "relationship.relationship_class")

    def to_dict(self) -> dict[str, str]:
        return {
            "relation": self.relation,
            "target": self.target,
            "relationship_class": self.relationship_class,
        }

    @classmethod
    def from_dict(cls, data: Any) -> Relationship:
        record = _mapping(data, "relationship")
        return cls(
            relation=_text(record.get("relation"), "relationship.relation"),
            target=_text(record.get("target"), "relationship.target"),
            relationship_class=_text(
                record.get("relationship_class"), "relationship.relationship_class"
            ),
        )


@dataclass(frozen=True, slots=True)
class TemporalEvent:
    """Something that happened to an object, ordered by constitutional state (Facet 11)."""

    sequence: int
    event: str
    state_id: str = ""
    at: str = TIMELESS

    def to_dict(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "event": self.event,
            "state_id": self.state_id,
            "at": self.at,
        }

    @classmethod
    def from_dict(cls, data: Any) -> TemporalEvent:
        record = _mapping(data, "temporal_history")
        return cls(
            sequence=int(record.get("sequence", 0)),
            event=_text(record.get("event"), "temporal_history.event"),
            state_id=_text(record.get("state_id"), "temporal_history.state_id", required=False),
            at=_text(record.get("at"), "temporal_history.at", required=False) or TIMELESS,
        )


@dataclass(frozen=True, slots=True)
class Attestation:
    """A judgement made about an object (Facets 12, 13, 14).

    ``verdict`` is :data:`UNATTESTED` until an authority speaks. An attestation that
    claims a verdict without naming its authority and its evidence is not an
    attestation, so both are required whenever the verdict is not ``UNATTESTED``.
    """

    kind: str
    verdict: str = UNATTESTED
    authority: str = ""
    standard: str = ""
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.kind, "attestation.kind")
        if self.verdict != UNATTESTED and not self.authority:
            raise FacetError(
                "an attested verdict must name its authority",
                kind=self.kind,
                verdict=self.verdict,
            )

    @property
    def attested(self) -> bool:
        return self.verdict != UNATTESTED

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "verdict": self.verdict,
            "authority": self.authority,
            "standard": self.standard,
            "evidence": list(self.evidence),
        }

    @classmethod
    def from_dict(cls, data: Any) -> Attestation:
        record = _mapping(data, "attestation")
        return cls(
            kind=_text(record.get("kind"), "attestation.kind"),
            verdict=_text(record.get("verdict"), "attestation.verdict", required=False)
            or UNATTESTED,
            authority=_text(record.get("authority"), "attestation.authority", required=False),
            standard=_text(record.get("standard"), "attestation.standard", required=False),
            evidence=_tuple(record.get("evidence"), "attestation.evidence"),
        )


@dataclass(frozen=True, slots=True)
class TraceLink:
    """A binding between upstream intent and downstream effect (Facet 15)."""

    upstream: str
    downstream: str
    kind: str = "traceability"

    def to_dict(self) -> dict[str, str]:
        return {"upstream": self.upstream, "downstream": self.downstream, "kind": self.kind}

    @classmethod
    def from_dict(cls, data: Any) -> TraceLink:
        record = _mapping(data, "traceability")
        return cls(
            upstream=_text(record.get("upstream"), "traceability.upstream"),
            downstream=_text(record.get("downstream"), "traceability.downstream"),
            kind=_text(record.get("kind"), "traceability.kind", required=False) or "traceability",
        )


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    """Content-addressed proof supporting a claim (Facet 16).

    The locator is deliberately advisory and the digest authoritative: a locator
    points into some persistence mechanism, and Article 4 forbids a persistence
    mechanism from being the truth. Evidence is identified by what it *is*, not by
    where a particular storage system happens to keep it.
    """

    evidence_id: str
    digest: str
    kind: str = "observation"
    locator: str = ""

    def __post_init__(self) -> None:
        _text(self.evidence_id, "evidence.evidence_id")
        _text(self.digest, "evidence.digest")

    def to_dict(self) -> dict[str, str]:
        return {
            "evidence_id": self.evidence_id,
            "digest": self.digest,
            "kind": self.kind,
            "locator": self.locator,
        }

    @classmethod
    def from_dict(cls, data: Any) -> EvidenceRef:
        record = _mapping(data, "evidence")
        return cls(
            evidence_id=_text(record.get("evidence_id"), "evidence.evidence_id"),
            digest=_text(record.get("digest"), "evidence.digest"),
            kind=_text(record.get("kind"), "evidence.kind", required=False) or "observation",
            locator=_text(record.get("locator"), "evidence.locator", required=False),
        )


@dataclass(frozen=True, slots=True)
class ContextBinding:
    """The conditions under which a statement about an object holds (Facets 17, 28-33)."""

    context_kind: str
    value: str
    qualifiers: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.context_kind, "context.context_kind")
        _text(self.value, "context.value")

    def to_dict(self) -> dict[str, object]:
        return {
            "context_kind": self.context_kind,
            "value": self.value,
            "qualifiers": list(self.qualifiers),
        }

    @classmethod
    def from_dict(cls, data: Any) -> ContextBinding:
        record = _mapping(data, "context")
        return cls(
            context_kind=_text(record.get("context_kind"), "context.context_kind"),
            value=_text(record.get("value"), "context.value"),
            qualifiers=_tuple(record.get("qualifiers"), "context.qualifiers"),
        )


@dataclass(frozen=True, slots=True)
class Constraint:
    """Something that must always hold of an object (Facet 23)."""

    constraint_id: str
    expression: str
    blocking: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "constraint_id": self.constraint_id,
            "expression": self.expression,
            "blocking": self.blocking,
        }

    @classmethod
    def from_dict(cls, data: Any) -> Constraint:
        record = _mapping(data, "constraints")
        return cls(
            constraint_id=_text(record.get("constraint_id"), "constraints.constraint_id"),
            expression=_text(record.get("expression"), "constraints.expression"),
            blocking=bool(record.get("blocking", True)),
        )


@dataclass(frozen=True, slots=True)
class Policy:
    """A rule governing the use of an object (Facet 24)."""

    policy_id: str
    statement: str
    enforcement: str = "advisory"

    def to_dict(self) -> dict[str, str]:
        return {
            "policy_id": self.policy_id,
            "statement": self.statement,
            "enforcement": self.enforcement,
        }

    @classmethod
    def from_dict(cls, data: Any) -> Policy:
        record = _mapping(data, "policies")
        return cls(
            policy_id=_text(record.get("policy_id"), "policies.policy_id"),
            statement=_text(record.get("statement"), "policies.statement"),
            enforcement=_text(record.get("enforcement"), "policies.enforcement", required=False)
            or "advisory",
        )


@dataclass(frozen=True, slots=True)
class RuntimeBinding:
    """An execution environment able to act on an object (Facet 25)."""

    execution_kind: str
    capability: str
    adapter: str = ""

    def __post_init__(self) -> None:
        _text(self.execution_kind, "runtime_bindings.execution_kind")
        _text(self.capability, "runtime_bindings.capability")

    def to_dict(self) -> dict[str, str]:
        return {
            "execution_kind": self.execution_kind,
            "capability": self.capability,
            "adapter": self.adapter,
        }

    @classmethod
    def from_dict(cls, data: Any) -> RuntimeBinding:
        record = _mapping(data, "runtime_bindings")
        return cls(
            execution_kind=_text(record.get("execution_kind"), "runtime_bindings.execution_kind"),
            capability=_text(record.get("capability"), "runtime_bindings.capability"),
            adapter=_text(record.get("adapter"), "runtime_bindings.adapter", required=False),
        )


@dataclass(frozen=True, slots=True)
class ProjectionBinding:
    """A generated view of an object (Facet 26).

    ``authoritative`` exists so the prohibition is *representable and refused*
    rather than merely undocumented: constructing a binding that claims authority
    raises :class:`ProjectionAuthorityError`. A rule that cannot be violated in the
    type system is a rule that is never tested.
    """

    projection_kind: str
    target: str
    generated: bool = True
    authoritative: bool = False

    def __post_init__(self) -> None:
        _text(self.projection_kind, "projection_bindings.projection_kind")
        _text(self.target, "projection_bindings.target")
        if self.authoritative:
            raise ProjectionAuthorityError(
                "a projection may not hold authority",
                projection_kind=self.projection_kind,
                target=self.target,
            )
        if not self.generated:
            raise ProjectionAuthorityError(
                "a projection that is not generated is an independent authority",
                projection_kind=self.projection_kind,
                target=self.target,
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "projection_kind": self.projection_kind,
            "target": self.target,
            "generated": self.generated,
            "authoritative": self.authoritative,
        }

    @classmethod
    def from_dict(cls, data: Any) -> ProjectionBinding:
        record = _mapping(data, "projection_bindings")
        return cls(
            projection_kind=_text(
                record.get("projection_kind"), "projection_bindings.projection_kind"
            ),
            target=_text(record.get("target"), "projection_bindings.target"),
            generated=bool(record.get("generated", True)),
            authoritative=bool(record.get("authoritative", False)),
        )


@dataclass(frozen=True, slots=True)
class PersistenceBinding:
    """A storage mechanism holding a copy of an object (Facet 27)."""

    persistence_kind: str
    locator: str
    authoritative: bool = False

    def __post_init__(self) -> None:
        _text(self.persistence_kind, "persistence_bindings.persistence_kind")
        _text(self.locator, "persistence_bindings.locator")
        if self.authoritative:
            raise ProjectionAuthorityError(
                "a persistence mechanism may not hold authority",
                persistence_kind=self.persistence_kind,
                locator=self.locator,
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "persistence_kind": self.persistence_kind,
            "locator": self.locator,
            "authoritative": self.authoritative,
        }

    @classmethod
    def from_dict(cls, data: Any) -> PersistenceBinding:
        record = _mapping(data, "persistence_bindings")
        return cls(
            persistence_kind=_text(
                record.get("persistence_kind"), "persistence_bindings.persistence_kind"
            ),
            locator=_text(record.get("locator"), "persistence_bindings.locator"),
            authoritative=bool(record.get("authoritative", False)),
        )


@dataclass(frozen=True, slots=True)
class DiscoveryDescriptor:
    """How an object is found without anyone listing it (Facet 21)."""

    discoverable: bool = True
    self_describing: bool = True
    provider: str = ""
    keywords: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "discoverable": self.discoverable,
            "self_describing": self.self_describing,
            "provider": self.provider,
            "keywords": list(self.keywords),
        }

    @classmethod
    def from_dict(cls, data: Any) -> DiscoveryDescriptor:
        record = _mapping(data, "discovery")
        return cls(
            discoverable=bool(record.get("discoverable", True)),
            self_describing=bool(record.get("self_describing", True)),
            provider=_text(record.get("provider"), "discovery.provider", required=False),
            keywords=_tuple(record.get("keywords"), "discovery.keywords"),
        )


@dataclass(frozen=True, slots=True)
class ReplayProof:
    """How an object can be reproduced exactly (Facet 19)."""

    procedure: str
    input_digest: str
    output_digest: str

    def __post_init__(self) -> None:
        _text(self.procedure, "replay.procedure")
        _text(self.input_digest, "replay.input_digest")
        _text(self.output_digest, "replay.output_digest")

    def holds(self, observed_output_digest: str) -> bool:
        """True iff a re-execution produced the recorded output."""
        return self.output_digest == str(observed_output_digest)

    def to_dict(self) -> dict[str, str]:
        return {
            "procedure": self.procedure,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
        }

    @classmethod
    def from_dict(cls, data: Any) -> ReplayProof:
        record = _mapping(data, "replay")
        return cls(
            procedure=_text(record.get("procedure"), "replay.procedure"),
            input_digest=_text(record.get("input_digest"), "replay.input_digest"),
            output_digest=_text(record.get("output_digest"), "replay.output_digest"),
        )


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """Who did what, provably (Facet 20)."""

    actor: str
    action: str
    subject: str
    digest: str = ""
    at: str = TIMELESS

    def to_dict(self) -> dict[str, str]:
        return {
            "actor": self.actor,
            "action": self.action,
            "subject": self.subject,
            "digest": self.digest,
            "at": self.at,
        }

    @classmethod
    def from_dict(cls, data: Any) -> AuditEntry:
        record = _mapping(data, "audit")
        return cls(
            actor=_text(record.get("actor"), "audit.actor"),
            action=_text(record.get("action"), "audit.action"),
            subject=_text(record.get("subject"), "audit.subject"),
            digest=_text(record.get("digest"), "audit.digest", required=False),
            at=_text(record.get("at"), "audit.at", required=False) or TIMELESS,
        )


@dataclass(frozen=True, slots=True)
class MetadataSet:
    """The machine-readable description an object publishes (Facet 22).

    Stored as sorted key/value pairs rather than a dict so a UCKO stays hashable
    and its canonical encoding is order-independent.
    """

    entries: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    @classmethod
    def of(cls, mapping: Mapping[str, Any] | None = None, **extra: Any) -> MetadataSet:
        merged: dict[str, str] = {}
        for source in (mapping or {}, extra):
            for key, value in source.items():
                merged[str(key)] = str(value)
        return cls(tuple(sorted(merged.items())))

    def as_dict(self) -> dict[str, str]:
        return dict(self.entries)

    def get(self, key: str, default: str = "") -> str:
        return self.as_dict().get(str(key), default)

    def keys(self) -> tuple[str, ...]:
        return tuple(key for key, _ in self.entries)

    def to_dict(self) -> dict[str, str]:
        return self.as_dict()

    @classmethod
    def from_dict(cls, data: Any) -> MetadataSet:
        return cls.of(_mapping(data, "metadata"))


__all__ = [
    "TIMELESS",
    "UNATTESTED",
    "Attestation",
    "AuditEntry",
    "AuthorityBinding",
    "Constraint",
    "ContextBinding",
    "DiscoveryDescriptor",
    "EvidenceRef",
    "MetadataSet",
    "OntologyRef",
    "Ownership",
    "PersistenceBinding",
    "Policy",
    "ProjectionBinding",
    "ProvenanceStep",
    "Relationship",
    "ReplayProof",
    "RuntimeBinding",
    "SemanticIdentity",
    "TaxonomyRef",
    "TemporalEvent",
    "TraceLink",
]
