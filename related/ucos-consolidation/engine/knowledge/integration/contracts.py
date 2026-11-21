"""UKI — Integration contracts + the proposed-artifact value type (EPIC-UKDA-002).

The value types that flow across the Universal Constitutional Knowledge Integration
boundary. Every type here is **immutable, typed, deterministic, and serializable**
and holds **no runtime state** (no store handles, no wall-clock): identical inputs
yield identical, byte-reproducible contract objects (IMP-007 §5).

    * :class:`ArtifactIntent` — the single, self-describing description of an artifact
      a future capability wants to *create or modify*. It is the input to the whole
      constitutional execution path: before anything is created, the intent is
      discovered against, screened for duplication, assessed for reuse, and only then
      composed/created, validated, certified, registered, and evolved. An intent can
      project itself as a candidate
      :class:`~engine.knowledge.cko.CanonicalKnowledgeObject` so it is screened with
      exactly the same content-addressing the canonical store uses (no second model).

    * :class:`Operation`, :class:`DiscoveryPhase`, :class:`Disposition`,
      :class:`SequenceStage`, :class:`ConstitutionalLayer` — the controlled
      vocabularies of the integration.

The integration exposes its capability through the versioned :data:`UKI_CONTRACT`
(AR-03 / PL-05), built additively on the :data:`~engine.knowledge.UKDA_CONTRACT`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.foundation.contracts.contract import Contract, Version
from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.integration.errors import IntentError
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle


class Operation(str, Enum):
    """What a capability intends to do to the canonical corpus."""

    CREATE = "create"
    MODIFY = "modify"


class DiscoveryPhase(str, Enum):
    """The constitutional phase that mandates a discovery pass before it proceeds.

    Discovery is deterministic and mandatory *before* each of these (Deliverable 2):
    nothing is created, implemented, validated, certified, or governed without first
    consulting constitutional knowledge.
    """

    CREATION = "creation"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    CERTIFICATION = "certification"
    GOVERNANCE = "governance"


class Disposition(str, Enum):
    """The reuse-engine determination for an intent (Deliverable 5), ordered.

    Creation is the *last resort*: an intent is reused, extended, or composed from
    existing constitutional knowledge whenever that knowledge suffices.
    """

    REUSE = "reuse"
    EXTEND = "extend"
    COMPOSE = "compose"
    CREATE = "create"


class SequenceStage(str, Enum):
    """The ten ordered stages of the constitutional execution path (final deliverable).

    Discover -> Analyze -> Reuse -> Extend -> Compose -> Create (only if necessary)
    -> Validate -> Certify -> Register -> Evolve.
    """

    DISCOVER = "discover"
    ANALYZE = "analyze"
    REUSE = "reuse"
    EXTEND = "extend"
    COMPOSE = "compose"
    CREATE = "create"
    VALIDATE = "validate"
    CERTIFY = "certify"
    REGISTER = "register"
    EVOLVE = "evolve"


class ConstitutionalLayer(str, Enum):
    """Every canonical UCOS layer the UKDA integrates with (Deliverable 1 scope)."""

    CONSTITUTION = "constitution"
    GOVERNANCE = "governance"
    REGISTRY = "registry"
    KNOWLEDGE = "knowledge"
    VALIDATION = "validation"
    CERTIFICATION = "certification"
    RUNTIME = "runtime"
    INTELLIGENCE = "intelligence"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    APPLICATIONS = "applications"
    SERVICES = "services"
    APIS = "apis"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    QUALITY = "quality"
    OBSERVABILITY = "observability"
    OPERATIONS = "operations"
    RELEASE = "release"
    DEPLOYMENT = "deployment"


#: The ordered tuple of canonical layers (stable for deterministic projection).
CANONICAL_LAYERS: tuple[ConstitutionalLayer, ...] = tuple(ConstitutionalLayer)

#: The ordered constitutional execution sequence (stable).
CONSTITUTIONAL_SEQUENCE: tuple[SequenceStage, ...] = tuple(SequenceStage)


def _as_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise IntentError("expected a non-empty string", field=field_name)
    return value


def _as_opt_str(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise IntentError("expected a string or null", field=field_name)
    return value


def _as_str_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list | tuple) or any(not isinstance(v, str) for v in value):
        raise IntentError("expected an array of strings", field=field_name)
    return tuple(value)


@dataclass(frozen=True, slots=True)
class ArtifactIntent:
    """A self-describing proposal to create or modify a canonical artifact."""

    intent_id: str
    kind: KnowledgeKind
    title: str
    statement: str
    universe: str
    authority: KnowledgeAuthority
    owner: str
    operation: Operation = Operation.CREATE
    rationale: str = ""
    parent: str | None = None
    dependencies: tuple[str, ...] = ()
    consumers: tuple[str, ...] = ()
    knowledge_links: tuple[str, ...] = ()
    decision_links: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    version: str = "1.0.0"

    def references(self) -> tuple[str, ...]:
        """Every distinct outbound reference the intent declares, ordered."""
        seen: dict[str, None] = {}
        if self.parent:
            seen.setdefault(self.parent, None)
        for group in (self.dependencies, self.consumers, self.knowledge_links):
            for ref in group:
                seen.setdefault(ref, None)
        return tuple(seen)

    def to_cko(self, *, lifecycle: Lifecycle = Lifecycle.DRAFT) -> CanonicalKnowledgeObject:
        """Project the intent as a candidate, content-addressed CKO for screening.

        The candidate reuses the exact canonical model (identity, links, hashing) so
        duplicate/reuse screening operates on the same substance the store enforces —
        there is no second, drifting representation of a proposed artifact.
        """
        return CanonicalKnowledgeObject.create(
            cko_id=self.intent_id,
            kind=self.kind,
            title=self.title,
            statement=self.statement,
            rationale=self.rationale,
            universe=self.universe,
            authority=self.authority,
            owner=self.owner,
            lifecycle=lifecycle,
            version=self.version,
            parent=self.parent,
            dependencies=self.dependencies,
            consumers=self.consumers,
            knowledge_links=self.knowledge_links,
            decision_links=self.decision_links,
            tags=self.tags,
        )

    def semantic_hash(self) -> str:
        """The semantic hash of the intent's substance (kind + statement + rationale)."""
        return self.to_cko().semantic_hash()

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> ArtifactIntent:
        """Parse an intent defensively (used by the CLI and callers)."""
        if not isinstance(record, Mapping):
            raise IntentError("artifact intent must be an object")
        op_raw = record.get("operation", Operation.CREATE.value)
        try:
            operation = Operation(str(op_raw))
        except ValueError as exc:
            raise IntentError("unknown operation", value=op_raw) from exc
        return cls(
            intent_id=_as_str(record.get("intent_id"), field_name="intent_id"),
            kind=KnowledgeKind.coerce(
                _as_str(record.get("kind"), field_name="kind"), context="intent"
            ),
            title=_as_str(record.get("title"), field_name="title"),
            statement=_as_str(record.get("statement"), field_name="statement"),
            universe=_as_str(record.get("universe"), field_name="universe"),
            authority=KnowledgeAuthority.coerce(
                _as_str(record.get("authority"), field_name="authority"), context="intent"
            ),
            owner=_as_str(record.get("owner"), field_name="owner"),
            operation=operation,
            rationale=record.get("rationale") or "",
            parent=_as_opt_str(record.get("parent"), field_name="parent"),
            dependencies=_as_str_tuple(record.get("dependencies"), field_name="dependencies"),
            consumers=_as_str_tuple(record.get("consumers"), field_name="consumers"),
            knowledge_links=_as_str_tuple(
                record.get("knowledge_links"), field_name="knowledge_links"
            ),
            decision_links=_as_str_tuple(record.get("decision_links"), field_name="decision_links"),
            tags=_as_str_tuple(record.get("tags"), field_name="tags"),
            version=record.get("version") or "1.0.0",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "kind": self.kind.value,
            "title": self.title,
            "statement": self.statement,
            "universe": self.universe,
            "authority": self.authority.value,
            "owner": self.owner,
            "operation": self.operation.value,
            "rationale": self.rationale,
            "parent": self.parent,
            "dependencies": list(self.dependencies),
            "consumers": list(self.consumers),
            "knowledge_links": list(self.knowledge_links),
            "decision_links": list(self.decision_links),
            "tags": list(self.tags),
            "version": self.version,
        }


#: The versioned public contract of the Constitutional Integration Layer (AR-03 / PL-05).
UKI_CONTRACT = Contract(
    name="knowledge.uki",
    version=Version(1, 0, 0),
    description=(
        "Universal Constitutional Knowledge Integration: make every canonical artifact "
        "discoverable, reusable, ownership-declared, duplication-screened, traceable, "
        "governance-grounded, and registered through the UKDA before it is created."
    ),
)


__all__ = [
    "Operation",
    "DiscoveryPhase",
    "Disposition",
    "SequenceStage",
    "ConstitutionalLayer",
    "CANONICAL_LAYERS",
    "CONSTITUTIONAL_SEQUENCE",
    "ArtifactIntent",
    "UKI_CONTRACT",
]
