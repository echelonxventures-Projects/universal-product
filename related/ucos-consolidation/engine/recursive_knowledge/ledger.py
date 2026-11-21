"""URKE-000001 Part 04 — the ledger. Append-only, hash-chained, and with no removal path.

There is no ``delete``, no ``retract`` and no ``forget``. The only way a subject stops being current
is :func:`KnowledgeLedger.supersede`, which links the replacement and keeps the original — so
"withdrawn" and "never existed" can never be the same observable state. That single absence is what
makes the silent-loss law computable rather than argued.

The journal chains each entry to the previous one through a digest taken over a body that *includes*
the previous hash, so an edit anywhere invalidates everything after it. Ordering is a sequence the
ledger assigns rather than a clock reading, because two runs over identical bytes must produce
identical output and a wall clock cannot do that.

:data:`POPULATION_READERS` is the self-application: every declared vocabulary is itself admitted as
a governed subject, through the same ``admit`` an unknown travels. There is deliberately no
privileged insert, because a founding row and a future row taking different paths would make the
extensibility laws measure the wrong one.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any

from engine.recursive_knowledge.composition import (
    SITUATION_ROLE,
    axes_for,
    qualify,
    situate,
)
from engine.recursive_knowledge.declaration import Declaration
from engine.recursive_knowledge.model import (
    Evidence,
    GovernedEntity,
    Lineage,
    RecursiveKnowledgeError,
    StateTransition,
    knowledge_id,
    missing_attributes,
)
from engine.uckp.canonical import content_hash

#: The role a vocabulary row is admitted under. A code symbol the declaration binds to a profile.
VOCABULARY_ROLE = "vocabulary_row"

#: The first link. A chain that started from nothing could be re-rooted without detection.
GENESIS = "0" * 64


class LedgerError(RecursiveKnowledgeError):
    """The admission, supersession or chain is unusable. A fault, never a state."""


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """One immutable link. ``prev_hash`` is inside the hashed body — that is what chains it."""

    sequence: int
    identity: str
    event: str
    state: str
    content_digest: str
    prev_hash: str
    entry_hash: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entry_hash", content_hash(self.body()))

    def body(self) -> dict[str, Any]:
        return {
            "content_digest": self.content_digest,
            "event": self.event,
            "identity": self.identity,
            "prev_hash": self.prev_hash,
            "sequence": self.sequence,
            "state": self.state,
        }

    def as_dict(self) -> dict[str, Any]:
        payload = self.body()
        payload["entry_hash"] = self.entry_hash
        return payload


# --- the declared vocabularies, read as populations ---------------------------------------

Row = tuple[str, Mapping[str, Any]]


def _rows(items: Iterable[tuple[str, Mapping[str, Any]]]) -> tuple[Row, ...]:
    return tuple((key, MappingProxyType(dict(payload))) for key, payload in items)


def seed_states(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.identifier, {"definition": spec.definition, "state_class": spec.state_class})
        for spec in declaration.states
    )


def seed_domains(declaration: Declaration) -> tuple[Row, ...]:
    return _rows((spec.identifier, {"definition": spec.definition}) for spec in declaration.domains)


def seed_qualifiers(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.qualifier, {"definition": spec.definition, "values": list(spec.values)})
        for spec in declaration.qualifiers
    )


def seed_relations(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.relation, {"definition": spec.definition, "inverse": spec.inverse})
        for spec in declaration.relations
    )


def seed_profiles(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (
            spec.profile,
            {"definition": spec.definition, "required_attributes": list(spec.required_attributes)},
        )
        for spec in declaration.profiles
    )


def seed_axes(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.axis, {"definition": spec.definition, "values": list(spec.values)})
        for spec in declaration.lifecycle_axes
    )


def seed_gap_classes(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.identifier, {"definition": spec.definition}) for spec in declaration.gap_classes
    )


def seed_realities(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.identifier, {"definition": spec.title, "systems": dict(spec.systems)})
        for spec in declaration.realities
    )


def seed_temporal_systems(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.identifier, {"definition": spec.title, "system_type": spec.system_type})
        for spec in declaration.temporal_systems
    )


def seed_context_kinds(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.identifier, {"definition": spec.definition}) for spec in declaration.context_kinds
    )


def seed_evolution_subjects(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.identifier, {"definition": spec.definition, "operators": list(spec.operators)})
        for spec in declaration.evolution_subjects
    )


def seed_discovery_sources(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.source_id, {"definition": spec.definition, "detector": spec.detector})
        for spec in declaration.discovery_sources
    )


def seed_learning_stages(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (spec.identifier, {"definition": spec.definition}) for spec in declaration.learning_stages
    )


def seed_future_capabilities(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (
            spec.identifier,
            {"definition": "declared future capability", "requires": list(spec.requires)},
        )
        for spec in declaration.future_capabilities
    )


def seed_substrate_elements(declaration: Declaration) -> tuple[Row, ...]:
    return _rows(
        (
            spec.substrate_id,
            {"definition": spec.mechanism, "module": spec.module, "symbol": spec.symbol},
        )
        for spec in declaration.substrate_elements
    )


#: Every declared population, mapped to the reader that reads it. Bound both ways at load time.
POPULATION_READERS: Mapping[str, Callable[[Declaration], tuple[Row, ...]]] = MappingProxyType(
    {
        "seed_axes": seed_axes,
        "seed_context_kinds": seed_context_kinds,
        "seed_discovery_sources": seed_discovery_sources,
        "seed_domains": seed_domains,
        "seed_evolution_subjects": seed_evolution_subjects,
        "seed_future_capabilities": seed_future_capabilities,
        "seed_gap_classes": seed_gap_classes,
        "seed_learning_stages": seed_learning_stages,
        "seed_profiles": seed_profiles,
        "seed_qualifiers": seed_qualifiers,
        "seed_realities": seed_realities,
        "seed_relations": seed_relations,
        "seed_states": seed_states,
        "seed_substrate_elements": seed_substrate_elements,
        "seed_temporal_systems": seed_temporal_systems,
    }
)


def available_population_readers() -> frozenset[str]:
    return frozenset(POPULATION_READERS)


# --- the store ----------------------------------------------------------------------------


class KnowledgeLedger:
    """The append-only store. Not frozen: it is an engine, and the values it holds are the frozen "
    "ones."""

    def __init__(self, declaration: Declaration, *, bootstrap: bool = True) -> None:
        self._declaration = declaration
        self._subjects: dict[str, GovernedEntity] = {}
        self._journal: list[JournalEntry] = []
        self._admitted = 0
        self._superseded = 0
        self._root = ""
        if bootstrap:
            self.bootstrap()

    # --- reading --------------------------------------------------------------------------

    @property
    def declaration(self) -> Declaration:
        return self._declaration

    @property
    def admitted(self) -> int:
        """Counted before anything can fail, so a drop cannot hide in an exception path."""
        return self._admitted

    @property
    def superseded(self) -> int:
        return self._superseded

    @property
    def journal(self) -> tuple[JournalEntry, ...]:
        return tuple(self._journal)

    @property
    def root_context(self) -> str:
        return self._root

    def has(self, identity: str) -> bool:
        return identity in self._subjects

    def get(self, identity: str) -> GovernedEntity:
        subject = self._subjects.get(identity)
        if subject is None:
            raise LedgerError(f"no subject is recorded under {identity!r}")
        return subject

    def all(self) -> tuple[GovernedEntity, ...]:
        return tuple(sorted(self._subjects.values(), key=lambda item: item.identity))

    def of_class(self, entity_class: str) -> tuple[GovernedEntity, ...]:
        """Subjects of one entity class. Also the declared coexistence mechanism: incompatible
        members sit here together and neither is removed to make room for the other."""
        return tuple(item for item in self.all() if item.entity_class == entity_class)

    def of_profile(self, profile: str) -> tuple[GovernedEntity, ...]:
        return tuple(item for item in self.all() if item.classification == profile)

    def with_state(self, state: str) -> tuple[GovernedEntity, ...]:
        return tuple(item for item in self.all() if item.state == state)

    def in_domain(self, domain: str) -> tuple[GovernedEntity, ...]:
        return tuple(item for item in self.all() if item.payload.get("domain") == domain)

    def active(self) -> tuple[GovernedEntity, ...]:
        return tuple(item for item in self.all() if item.active)

    # --- building a subject ----------------------------------------------------------------

    def subject(
        self,
        *,
        natural_key: str,
        profile: str,
        domain: str,
        owner: str,
        origin: str,
        context: str | None = None,
        entity_class: str | None = None,
        state: str | None = None,
        title: str = "",
        axes: Mapping[str, str] | None = None,
        qualifiers: Mapping[str, str] | None = None,
        payload: Mapping[str, Any] | None = None,
        evidence: tuple[Evidence, ...] = (),
        lineage: Lineage | None = None,
        **extras: Any,
    ) -> GovernedEntity:
        """Build a subject with every declared default filled in. Admits nothing by itself."""
        declaration = self._declaration
        declaration.profile(profile)
        declaration.domain(domain)
        resolved_class = entity_class or declaration.universal_entity_class
        resolved_state = state or declaration.initial_state
        declaration.state(resolved_state)
        body = dict(payload or {})
        body["domain"] = domain
        body["qualifiers"] = dict(qualify(declaration, qualifiers))
        identity = knowledge_id(
            resolved_class,
            f"{profile}:{natural_key}",
            namespace=declaration.namespace,
            key_domain=declaration.key_domain,
        )
        sequence = len(self._journal)
        return GovernedEntity(
            identity=identity,
            entity_class=resolved_class,
            natural_key=natural_key,
            state=resolved_state,
            owner=owner,
            origin=origin,
            governance=declaration.entity_class(resolved_class).governance,
            sequence=sequence,
            title=title or natural_key,
            classification=profile,
            context=context if context is not None else self._root,
            axes=axes_for(declaration, axes),
            evolution_metadata={"revision": "1", "operator": "", "basis": origin},
            lineage=lineage or Lineage(presented_by=declaration.artifact_id),
            evidence=evidence,
            payload=body,
            state_history=(
                StateTransition(
                    from_state="",
                    to_state=resolved_state,
                    basis=origin,
                    actor=owner,
                    sequence=sequence,
                ),
            ),
            **extras,
        )

    # --- writing ---------------------------------------------------------------------------

    def admit(self, entity: GovernedEntity) -> GovernedEntity:
        """Admit a subject, enforcing its profile's requirements. The only write path there is."""
        self._admitted += 1
        declaration = self._declaration
        required, payload_keys = declaration.required_for(
            entity.entity_class, entity.classification
        )
        absent = missing_attributes(entity, required)
        if absent:
            raise LedgerError(
                f"the {entity.classification!r} profile requires "
                f"{', '.join(absent)}, which this subject does not carry"
            )
        for key in payload_keys:
            value = entity.payload.get(key)
            if value is None or (isinstance(value, str) and not value.strip()) or value == []:
                raise LedgerError(
                    f"the {entity.classification!r} profile requires payload key {key!r}, which "
                    "this subject does not carry"
                )
        if entity.owner not in {spec.identifier for spec in declaration.ownership_roles}:
            raise LedgerError(
                f"{entity.owner!r} is not a declared ownership role; an undeclared owner would be "
                "an accountability nobody can resolve"
            )
        event = "re-admitted" if entity.identity in self._subjects else "admitted"
        self._subjects[entity.identity] = entity
        self._append(entity, event)
        return entity

    def supersede(self, identity: str, *, by: str, basis: str) -> GovernedEntity:
        """Replace a subject with a named later one, retaining the original. The only removal-shaped
        act in the capability, and it removes nothing — which is also the declared recovery path."""
        current = self.get(identity)
        if not self.has(by):
            raise LedgerError(
                f"cannot supersede {identity!r} by {by!r}, which is not recorded; a successor that "
                "does not exist would leave the original unreachable and unreplaced"
            )
        if not basis.strip():
            raise LedgerError("a supersession must name its basis")
        replaced = replace(current, superseded_by=by)
        self._subjects[identity] = replaced
        self._superseded += 1
        self._append(replaced, "supersession")
        return replaced

    def amend(self, entity: GovernedEntity, *, event: str) -> GovernedEntity:
        """Record a new version of a subject already admitted. Appends; overwrites no history."""
        if not self.has(entity.identity):
            raise LedgerError(f"{entity.identity!r} has not been admitted, so it cannot be amended")
        self._subjects[entity.identity] = entity
        self._append(entity, event)
        return entity

    def _append(self, entity: GovernedEntity, event: str) -> JournalEntry:
        previous = self._journal[-1].entry_hash if self._journal else GENESIS
        record = JournalEntry(
            sequence=len(self._journal),
            identity=entity.identity,
            event=event,
            state=entity.state,
            content_digest=entity.content_digest(),
            prev_hash=previous,
        )
        self._journal.append(record)
        return record

    # --- integrity -------------------------------------------------------------------------

    def chain_is_intact(self) -> bool:
        """Verify sequence, link and body hash. The declared self-auditing mechanism."""
        previous = GENESIS
        for index, record in enumerate(self._journal):
            if record.sequence != index or record.prev_hash != previous:
                return False
            if record.entry_hash != content_hash(record.body()):
                return False
            previous = record.entry_hash
        return True

    def verify(self) -> dict[str, Any]:
        """Reconcile the arithmetic. A drop shows up here as a mismatch, not as a smaller number."""
        unretrievable = [identity for identity in sorted(self._subjects) if not self.has(identity)]
        journalled = {record.identity for record in self._journal}
        unjournalled = sorted(set(self._subjects) - journalled)
        return {
            "admitted": self._admitted,
            "chain_intact": self.chain_is_intact(),
            "journal_entries": len(self._journal),
            "reconciles": not unretrievable and not unjournalled,
            "status": "PASS"
            if self.chain_is_intact() and not unretrievable and not unjournalled
            else "FAIL",
            "subjects": len(self._subjects),
            "superseded_count": self._superseded,
            "unjournalled": unjournalled,
            "unretrievable": unretrievable,
        }

    def summary(self) -> dict[str, Any]:
        """The declared self-observation mechanism: the ledger reporting on itself."""
        by_state: dict[str, int] = {}
        by_profile: dict[str, int] = {}
        by_class: dict[str, int] = {}
        by_domain: dict[str, int] = {}
        for item in self.all():
            by_state[item.state] = by_state.get(item.state, 0) + 1
            by_profile[item.classification] = by_profile.get(item.classification, 0) + 1
            by_class[item.entity_class] = by_class.get(item.entity_class, 0) + 1
            domain = str(item.payload.get("domain") or "")
            by_domain[domain] = by_domain.get(domain, 0) + 1
        return {
            "admitted": self._admitted,
            "by_class": dict(sorted(by_class.items())),
            "by_domain": dict(sorted(by_domain.items())),
            "by_profile": dict(sorted(by_profile.items())),
            "by_state": dict(sorted(by_state.items())),
            "chain_head": self._journal[-1].entry_hash if self._journal else GENESIS,
            "journal_entries": len(self._journal),
            "root_context": self._root,
            "subjects": len(self._subjects),
            "superseded_count": self._superseded,
        }

    def review_clock(self) -> int:
        """The sequence review dueness is measured against: subjects discovery does not produce.

        Measured defect this repairs: with the journal length as the clock, a discovery pass
        advanced it by hundreds and made reviews fall due that nothing had actually neglected — so
        discovery moved the thing it was measuring and never converged. Counting only subjects
        outside discovery's own output leaves a sequence that grows when work happens and not when
        work is merely reported on.
        """
        excluded = self._declaration.profile_for(self._declaration.discovery_scope_excludes_role)
        return sum(1 for item in self._subjects.values() if item.classification != excluded)

    def digest(self) -> str:
        return content_hash([item.as_dict() for item in self.all()])

    # --- seeding ---------------------------------------------------------------------------

    def bootstrap(self) -> None:
        """Admit the declared vocabulary, the contexts and the disclosed gaps as governed subjects.

        The root context goes first and is its own context: the fixed point that lets the first
        admission happen without a context that does not yet exist. Everything after it travels the
        same ``admit`` as an unknown nobody anticipated.
        """
        declaration = self._declaration
        root_identity = knowledge_id(
            declaration.universal_entity_class,
            f"context:{declaration.context_root}",
            namespace=declaration.namespace,
            key_domain=declaration.key_domain,
        )
        self._root = root_identity
        root = self.subject(
            natural_key=declaration.context_root,
            profile=declaration.profile_for(SITUATION_ROLE),
            domain=declaration.residual_domain,
            owner=declaration.artifact_id,
            origin="declared root context",
            context=root_identity,
            payload=dict(situate(declaration, declaration.residual_context_kind)),
            evidence=(Evidence(source=declaration.artifact_id, statement="declared root context"),),
        )
        self.admit(root)
        for spec in declaration.context_kinds:
            self.admit(
                self.subject(
                    natural_key=spec.identifier,
                    profile=declaration.profile_for(SITUATION_ROLE),
                    domain=declaration.residual_domain,
                    owner=declaration.artifact_id,
                    origin="declared context kind",
                    payload=dict(situate(declaration, spec.identifier)),
                    evidence=(Evidence(source=declaration.artifact_id, statement=spec.definition),),
                )
            )
        for population in declaration.seeded_populations:
            reader = POPULATION_READERS.get(population.reader)
            if reader is None:
                raise LedgerError(
                    f"population {population.population!r} names reader {population.reader!r}, "
                    "which nothing implements"
                )
            for natural_key, payload in reader(declaration):
                body = dict(payload)
                body.setdefault("definition", population.population)
                self.admit(
                    self.subject(
                        natural_key=f"{population.population}/{natural_key}",
                        profile=declaration.profile_for(VOCABULARY_ROLE),
                        domain=declaration.residual_domain,
                        owner=declaration.artifact_id,
                        origin=population.population,
                        entity_class=population.entity_class,
                        title=natural_key,
                        payload=body,
                        evidence=(
                            Evidence(
                                source=declaration.artifact_id,
                                statement=f"declared in {population.population}",
                            ),
                        ),
                    )
                )
        from engine.recursive_knowledge.subjects import admit_disclosed_gap

        for gap in declaration.all_disclosed_gaps():
            admit_disclosed_gap(self, gap)


def relate(
    ledger: KnowledgeLedger,
    *,
    source: str,
    target: str,
    relation: str,
    basis: str,
    owner: str,
    origin: str,
    evidence: tuple[Evidence, ...] = (),
) -> GovernedEntity:
    """Admit a governed relationship. The second structural primitive, and the last one.

    Both endpoints must already be recorded. A link to something absent would be a claim about a
    subject nobody can inspect, which is the shape of a reference that quietly stops resolving.
    """
    declaration = ledger.declaration
    declaration.relation(relation)
    for label, identity in (("source", source), ("target", target)):
        if not ledger.has(identity):
            raise LedgerError(f"the relationship names {label} {identity!r}, which is not recorded")
    if not basis.strip():
        raise LedgerError("a relationship must name its basis")
    entity = ledger.subject(
        natural_key=f"{relation}:{source}->{target}",
        profile=declaration.default_profile,
        domain=declaration.residual_domain,
        owner=owner,
        origin=origin,
        entity_class=declaration.link_entity_class,
        title=f"{relation} {ledger.get(source).title} -> {ledger.get(target).title}",
        evidence=evidence or (Evidence(source=origin or declaration.artifact_id, statement=basis),),
        source=source,
        target=target,
        relation=relation,
        basis=basis,
    )
    return ledger.admit(entity)


__all__ = [
    "GENESIS",
    "VOCABULARY_ROLE",
    "POPULATION_READERS",
    "JournalEntry",
    "KnowledgeLedger",
    "LedgerError",
    "available_population_readers",
    "relate",
]
