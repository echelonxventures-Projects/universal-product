"""UCXI-000001 Part 05 — Context Registry: the single registration authority for context.

Every context the platform reasons about is registered exactly once, here. The
registry is the *write* surface of the layer and enforces four constitutional rules at
the moment of registration, so an invalid context can never reach resolution,
composition, the graph, or a certificate:

    1. **Classified** (CXL-02) — the kind must be classified by the taxonomy. An
       unclassified kind is refused, not auto-created.
    2. **Conformant** (CXL-01) — the asserted dimensions must match the ontological
       shape of the kind: complete, closed, correctly typed.
    3. **Deterministically identified** (CXL-05) — the identity is minted by
       :func:`engine.registry.universal.identity.deterministic_id` from
       ``(CONTEXT, namespace, natural_key)``. Registration order, wall-clock and
       machine are irrelevant to the identity.
    4. **Registered once** (CXL-06) — re-registering byte-identical content under the
       same identity is idempotent; a *different* context under the same identity is a
       duplicate refusal, and the *same substance* under a different identity is a
       Context Once refusal.

Mutation is append-only: a context is superseded, never overwritten (a superseded
record stays queryable and the supersession is an edge in the graph). Every write
appends a hash-chained :class:`AuditEntry`, so the registry's history is tamper
evident and verifiable with :meth:`ContextRegistry.verify_audit` — and contains no
timestamp, so an unchanged sequence of registrations always seals to the same digest.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from engine.compiler.cycles import detect_cycle
from engine.context.errors import (
    ContextGraphError,
    ContextNotFoundError,
    ContextOnceViolation,
    ContextRegistrationError,
    DuplicateContextError,
)
from engine.context.model import (
    ContextDeclaration,
    ContextRecord,
    ContextRelationEdge,
    content_digest,
    seal,
)
from engine.context.ontology import UNIVERSAL_ONTOLOGY, ContextOntology
from engine.context.taxonomy import (
    UNIVERSAL_TAXONOMY,
    ContextKind,
    ContextLifecycle,
    ContextRelation,
    ContextTaxonomy,
)
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("context.registry")

#: The actions the audit journal records.
ACTION_REGISTER = "register"
ACTION_RELATE = "relate"
ACTION_TRANSITION = "transition"
ACTION_SUPERSEDE = "supersede"


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """One tamper-evident, hash-chained entry of the registry journal.

    The chain carries no timestamp: ``entry_hash`` is a pure function of the action,
    the subject, the affected content and the previous entry, so an identical
    sequence of registrations always produces an identical chain (determinism).
    """

    sequence: int
    action: str
    subject: str
    content_hash: str
    previous_hash: str
    entry_hash: str = ""

    def __post_init__(self) -> None:
        if not self.entry_hash:
            object.__setattr__(self, "entry_hash", self.expected_hash())

    def expected_hash(self) -> str:
        return content_digest(
            [self.sequence, self.action, self.subject, self.content_hash, self.previous_hash]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "action": self.action,
            "subject": self.subject,
            "content_hash": self.content_hash,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }


#: The genesis link of the audit chain.
GENESIS_HASH = "0" * 64


class ContextRegistry:
    """The append-only registration authority for every context.

    The registry owns no policy of its own: it enforces the taxonomy and ontology it
    is constructed with, so extending the platform to a future context type is a data
    extension of those two, not a change here.
    """

    __slots__ = ("_taxonomy", "_ontology", "_records", "_relations", "_substance", "_audit")

    def __init__(
        self,
        *,
        taxonomy: ContextTaxonomy = UNIVERSAL_TAXONOMY,
        ontology: ContextOntology = UNIVERSAL_ONTOLOGY,
    ) -> None:
        self._taxonomy = taxonomy
        self._ontology = ontology
        self._records: dict[str, ContextRecord] = {}
        self._relations: dict[str, ContextRelationEdge] = {}
        self._substance: dict[str, str] = {}
        self._audit: list[AuditEntry] = []

    # -- properties --------------------------------------------------------- #

    @property
    def taxonomy(self) -> ContextTaxonomy:
        """The classification this registry enforces."""
        return self._taxonomy

    @property
    def ontology(self) -> ContextOntology:
        """The structural specification this registry enforces."""
        return self._ontology

    def __len__(self) -> int:
        return len(self._records)

    # -- registration ------------------------------------------------------- #

    def register(self, declaration: ContextDeclaration) -> ContextRecord:
        """Register one context and return its canonical record.

        Raises:
            TaxonomyError: the kind is not classified.
            OntologyError: the asserted dimensions do not match the kind's shape.
            DuplicateContextError: a different context holds this identity.
            ContextOnceViolation: this substance is already registered elsewhere.
        """
        with trace("context.registry.register", kind=str(declaration.kind)):
            taxon = self._taxonomy.taxon_for_kind(declaration.kind)
            self._ontology.require_values(
                declaration.kind,
                declaration.value_mapping(),
                at=f"{declaration.namespace}/{declaration.natural_key}",
            )
            if declaration.parent is not None and declaration.parent not in self._records:
                raise ContextRegistrationError(
                    "declared parent context is not registered",
                    parent=declaration.parent,
                    natural_key=declaration.natural_key,
                )

            record = ContextRecord(
                context_id=declaration.identity,
                kind=declaration.kind,
                taxon_id=taxon.taxon_id,
                namespace=declaration.namespace,
                natural_key=declaration.natural_key,
                values=declaration.values,
                authority=declaration.authority,
                lifecycle=ContextLifecycle.REGISTERED,
                boundary=declaration.boundary,
                parent=declaration.parent,
                description=declaration.description,
                universal=self._taxonomy.is_universal(declaration.kind),
            )

            existing = self._records.get(record.context_id)
            if existing is not None:
                if existing.content_hash == record.content_hash:
                    return existing  # idempotent re-registration of identical content
                raise DuplicateContextError(
                    "a different context is already registered under this identity",
                    context_id=record.context_id,
                    registered_kind=existing.kind,
                    incoming_kind=record.kind,
                )

            substance = self.substance_hash(record)
            owner = self._substance.get(substance)
            if owner is not None:
                raise ContextOnceViolation(
                    "identical context substance is already registered under another identity",
                    context_id=record.context_id,
                    canonical_home=owner,
                    kind=record.kind,
                )

            self._records[record.context_id] = record
            self._substance[substance] = record.context_id
            self._append(ACTION_REGISTER, record.context_id, record.content_hash)

            if record.parent is not None:
                self.relate(ContextRelation.CONTAINS, record.parent, record.context_id)
        _logger.info(
            "context.registry.registered",
            context_id=record.context_id,
            kind=record.kind,
            boundary=record.boundary,
        )
        return record

    def register_all(self, declarations: Iterable[ContextDeclaration]) -> tuple[ContextRecord, ...]:
        """Register a batch in the given order, returning the records."""
        return tuple(self.register(declaration) for declaration in declarations)

    def substance_hash(self, record: ContextRecord) -> str:
        """The identity-independent digest used to enforce Context Once (CXL-06)."""
        return content_digest(
            {
                "kind": record.kind,
                "boundary": record.boundary,
                "authority": record.authority.value,
                "values": [value.to_dict() for value in record.values],
            }
        )

    # -- relations ---------------------------------------------------------- #

    def relate(
        self, relation: ContextRelation | str, source: str, target: str, *, note: str = ""
    ) -> ContextRelationEdge:
        """Relate two registered contexts, refusing inadmissible or cyclic edges.

        Raises:
            ContextNotFoundError: an endpoint is not registered.
            OntologyError: the relation is not admissible between these kinds.
            ContextGraphError: the edge would make a hierarchical relation cyclic.
        """
        edge = ContextRelationEdge(
            relation=ContextRelation.coerce(relation), source=source, target=target, note=note
        )
        source_record = self.get(edge.source)
        target_record = self.get(edge.target)
        self._ontology.require_relation(edge.relation, source_record.kind, target_record.kind)

        existing = self._relations.get(edge.edge_id)
        if existing is not None:
            return existing  # idempotent: the same triple asserted twice is one edge

        if self._ontology.rule_for(edge.relation).acyclic:
            adjacency = self._adjacency(edge.relation)
            adjacency.setdefault(edge.source, []).append(edge.target)
            adjacency.setdefault(edge.target, [])
            cycle = detect_cycle({node: tuple(sorted(kids)) for node, kids in adjacency.items()})
            if cycle is not None:
                raise ContextGraphError(
                    "relation would introduce a cycle in a hierarchical relation",
                    relation=edge.relation.value,
                    cycle=list(cycle),
                )

        self._relations[edge.edge_id] = edge
        self._append(ACTION_RELATE, edge.edge_id, content_digest(edge.to_dict()))
        return edge

    def _adjacency(self, relation: ContextRelation) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = {cid: [] for cid in self._records}
        for edge in self._relations.values():
            if edge.relation is relation:
                adjacency.setdefault(edge.source, []).append(edge.target)
        return adjacency

    def relations(
        self, *, relation: ContextRelation | str | None = None
    ) -> tuple[ContextRelationEdge, ...]:
        """Every relation edge, optionally filtered by relation type (ordered)."""
        edges = tuple(self._relations[eid] for eid in sorted(self._relations))
        if relation is None:
            return edges
        wanted = ContextRelation.coerce(relation)
        return tuple(edge for edge in edges if edge.relation is wanted)

    # -- lifecycle ---------------------------------------------------------- #

    def transition(self, context_id: str, target: ContextLifecycle | str) -> ContextRecord:
        """Advance a registered context to ``target``, refusing illegal transitions."""
        record = self.get(context_id)
        advanced = record.with_lifecycle(ContextLifecycle.coerce(target))
        self._records[context_id] = advanced
        self._append(ACTION_TRANSITION, context_id, content_digest(advanced.lifecycle.value))
        return advanced

    def supersede(self, context_id: str, declaration: ContextDeclaration) -> ContextRecord:
        """Register ``declaration`` as the successor of ``context_id``.

        The predecessor is retained (append-only) and marked superseded, and a
        ``supersedes`` edge records the succession, so history is never lost.
        """
        predecessor = self.get(context_id)
        if declaration.kind != predecessor.kind:
            raise ContextRegistrationError(
                "a context may only be superseded by one of the same kind",
                context_id=context_id,
                registered_kind=predecessor.kind,
                incoming_kind=declaration.kind,
            )
        successor = self.register(declaration)
        self._records[context_id] = predecessor.with_lifecycle(ContextLifecycle.SUPERSEDED)
        self.relate(ContextRelation.SUPERSEDES, successor.context_id, context_id)
        self._append(ACTION_SUPERSEDE, context_id, successor.content_hash)
        return successor

    # -- reads -------------------------------------------------------------- #

    def has(self, context_id: str) -> bool:
        return context_id in self._records

    def get(self, context_id: str) -> ContextRecord:
        """Return the record or raise :class:`ContextNotFoundError`."""
        try:
            return self._records[context_id]
        except KeyError as exc:
            raise ContextNotFoundError("context is not registered", context_id=context_id) from exc

    def find(self, context_id: str) -> ContextRecord | None:
        return self._records.get(context_id)

    def records(self) -> tuple[ContextRecord, ...]:
        """Every registered record, ordered by identity."""
        return tuple(self._records[cid] for cid in sorted(self._records))

    def by_kind(self, kind: ContextKind | str) -> tuple[ContextRecord, ...]:
        """Every record of one kind, ordered by identity."""
        wanted = kind.value if isinstance(kind, ContextKind) else str(kind)
        return tuple(record for record in self.records() if record.kind == wanted)

    def by_namespace(self, namespace: str) -> tuple[ContextRecord, ...]:
        """Every record in a namespace or below it, ordered by identity."""
        prefix = namespace.strip().lower()
        return tuple(
            record
            for record in self.records()
            if record.namespace == prefix or record.namespace.startswith(prefix + ".")
        )

    def by_boundary(self, boundary: str) -> tuple[ContextRecord, ...]:
        """Every record bound to one frame, ordered by identity."""
        return tuple(record for record in self.records() if record.boundary == boundary)

    def by_lifecycle(self, stage: ContextLifecycle | str) -> tuple[ContextRecord, ...]:
        wanted = ContextLifecycle.coerce(stage)
        return tuple(record for record in self.records() if record.lifecycle is wanted)

    def kinds(self) -> tuple[str, ...]:
        """Distinct registered kinds, ordered."""
        return tuple(sorted({record.kind for record in self._records.values()}))

    def boundaries(self) -> tuple[str, ...]:
        """Distinct bounding frames in use, ordered."""
        return tuple(sorted({record.boundary for record in self._records.values()}))

    def bindings(self) -> dict[str, str]:
        """The ``context_id -> boundary`` binding of every registered context."""
        return {cid: record.boundary for cid, record in sorted(self._records.items())}

    def universal_coverage(self) -> dict[str, bool]:
        """Which universal kinds have at least one active registered context."""
        active = {record.kind for record in self._records.values() if record.lifecycle.is_active}
        return {kind: kind in active for kind in self._taxonomy.universal_kinds()}

    def is_universally_covered(self) -> bool:
        """True iff every universal kind is represented by an active context."""
        return all(self.universal_coverage().values())

    # -- audit -------------------------------------------------------------- #

    def _append(self, action: str, subject: str, content_hash: str) -> AuditEntry:
        previous = self._audit[-1].entry_hash if self._audit else GENESIS_HASH
        entry = AuditEntry(
            sequence=len(self._audit) + 1,
            action=action,
            subject=subject,
            content_hash=content_hash,
            previous_hash=previous,
        )
        self._audit.append(entry)
        return entry

    def audit(self) -> tuple[AuditEntry, ...]:
        """The append-only journal, in order."""
        return tuple(self._audit)

    def verify_audit(self) -> list[str]:
        """Return findings if the hash chain is broken (empty means intact)."""
        findings: list[str] = []
        previous = GENESIS_HASH
        for index, entry in enumerate(self._audit, start=1):
            if entry.sequence != index:
                findings.append(f"audit entry {index}: sequence is {entry.sequence}")
            if entry.previous_hash != previous:
                findings.append(f"audit entry {index}: previous-hash link is broken")
            if entry.entry_hash != entry.expected_hash():
                findings.append(f"audit entry {index}: entry hash does not reproduce")
            previous = entry.entry_hash
        return findings

    # -- serialisation ------------------------------------------------------ #

    def seal(self) -> str:
        """The digest of the registry's whole state (records, relations, journal)."""
        return seal(self.to_dict())

    def summary(self) -> dict[str, Any]:
        coverage = self.universal_coverage()
        return {
            "contexts": len(self._records),
            "relations": len(self._relations),
            "audit_entries": len(self._audit),
            "kinds_registered": list(self.kinds()),
            "boundaries": list(self.boundaries()),
            "universal_kinds": len(coverage),
            "universal_covered": sum(1 for present in coverage.values() if present),
            "universally_covered": self.is_universally_covered(),
            "future_kinds": list(self._taxonomy.future_kinds()),
            "audit_intact": not self.verify_audit(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "contexts": [record.to_dict() for record in self.records()],
            "relations": [edge.to_dict() for edge in self.relations()],
            "audit": [entry.to_dict() for entry in self._audit],
            "universal_coverage": self.universal_coverage(),
        }


def declarations_from_mapping(payload: Mapping[str, Any]) -> tuple[ContextDeclaration, ...]:
    """Build declarations from a plain mapping (the CLI / catalog entry point).

    ``payload`` is ``{"contexts": [{kind, namespace, natural_key, boundary, authority,
    values: {dimension: value}, source, ...}]}``.
    """
    from engine.context.model import values_from_mapping  # local: avoids a cycle at import
    from engine.context.taxonomy import ContextAuthority

    out: list[ContextDeclaration] = []
    for entry in payload.get("contexts", ()):
        authority = ContextAuthority.coerce(entry.get("authority", "operational"))
        source = entry.get("source")
        if not source:
            raise ContextRegistrationError(
                "a declared context must name its source (provenance is mandatory)",
                natural_key=entry.get("natural_key"),
            )
        out.append(
            ContextDeclaration(
                kind=entry["kind"],
                namespace=entry["namespace"],
                natural_key=entry["natural_key"],
                values=values_from_mapping(
                    entry.get("values", {}), authority=authority, source=source
                ),
                authority=authority,
                boundary=entry.get("boundary", "universal"),
                parent=entry.get("parent"),
                description=entry.get("description", ""),
            )
        )
    return tuple(out)


__all__ = [
    "ACTION_REGISTER",
    "ACTION_RELATE",
    "ACTION_TRANSITION",
    "ACTION_SUPERSEDE",
    "GENESIS_HASH",
    "AuditEntry",
    "ContextRegistry",
    "declarations_from_mapping",
]
