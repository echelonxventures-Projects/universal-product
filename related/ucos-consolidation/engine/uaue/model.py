"""UAUE — the authority model types (UAUE-000001).

Every type here is ``frozen=True, slots=True`` and every collection is a ``tuple``, so an
authority model cannot be edited after it is resolved and two models resolved from the same
declaration are equal by value. That is what makes :meth:`EvolutionAuthority.digest` a
replay test rather than a timestamp: if resolution were order-dependent or mutable, a digest
would prove nothing about the declaration it came from.

These types describe *shape*, never *content*. Not one of them names a phase, a register, a
stage or a classification rule; the names arrive from the declaration and, for the stage set,
from :mod:`engine.uckp.evolution`. A default here would be a declaration kept in two places.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.foundation.obs.errors import FoundationError

#: The three states a declared home or evidence path can reach. ``UNREADABLE`` is kept
#: distinct from ``ABSENT`` for the reason :mod:`engine.uckp.resolution` keeps them distinct:
#: a path that could not be read must never be able to pass as a path that declares nothing.
PRESENT = "present"
ABSENT = "absent"
UNREADABLE = "unreadable"


class EvolutionAuthorityError(FoundationError):
    """The evolution declaration or its substrate is unusable, so no authority may be built.

    Rooted in :class:`~engine.foundation.obs.errors.FoundationError` rather than in the UCKP
    taxonomy: UAUE holds no constitutional authority and adding a code to
    :mod:`engine.uckp.errors` would enlarge Layer Zero's contract for a programme that
    legislates nothing.
    """

    code = "UAUE-DECLARATION-001"


@dataclass(frozen=True, slots=True)
class Classification:
    """One classification a phase may be measured into, as the declaration defines it.

    ``rule`` is the falsifiable test, carried verbatim so a report can quote the declaration
    instead of paraphrasing it. ``rank`` orders severity for aggregation and is the
    declaration's, not this module's.
    """

    identifier: str
    rule: str
    meaning: str
    rank: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "rule": self.rule,
            "meaning": self.meaning,
            "rank": self.rank,
        }


@dataclass(frozen=True, slots=True)
class Owner:
    """One declared owner home of one phase, with the measurement of whether it resolves.

    ``missing_symbols`` is the shortfall of ``symbols`` against the names actually bound
    across *all* resolving homes of the owning phase — a symbol counts as bound if any of the
    phase's homes binds it, which is the union rule the existing programme engines apply.
    """

    home: str
    symbols: tuple[str, ...]
    state: str
    missing_symbols: tuple[str, ...]

    @property
    def resolves(self) -> bool:
        return self.state == PRESENT

    def to_dict(self) -> dict[str, Any]:
        return {
            "home": self.home,
            "symbols": list(self.symbols),
            "state": self.state,
            "missing_symbols": list(self.missing_symbols),
        }


@dataclass(frozen=True, slots=True)
class Gate:
    """The gate a phase declares, and whether that gate is actually wired.

    A declared gate that no Makefile target and no executable discharges is a phase that
    cannot be closed by anything, so ``wired`` is a measurement and never an assumption.
    """

    command: str
    wired: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"command": self.command, "wired": self.wired, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class Register:
    """One canonical register the declaration owns.

    ``ordinal`` is the register's position in declared order and is cross-checked against the
    numeric prefix of ``file``: that is what turns a missing or duplicated register into a
    refusal rather than a silently renumbered set. ``owner_phase`` is the phase whose objects
    the register renders, or empty when the register is owned by the programme as a whole.
    """

    ordinal: int
    file: str
    renderer: str
    title: str
    purpose: str
    owner_phase: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ordinal": self.ordinal,
            "file": self.file,
            "renderer": self.renderer,
            "title": self.title,
            "purpose": self.purpose,
            "owner_phase": self.owner_phase,
        }


@dataclass(frozen=True, slots=True)
class Phase:
    """One phase of the loop, its owners, its gate, its evidence and its classification."""

    identifier: str
    ordinal: int
    name: str
    duty: str
    canonical_stages: tuple[str, ...]
    produces: str
    owners: tuple[Owner, ...]
    gate: Gate
    declared_evidence: tuple[str, ...]
    resolving_evidence: tuple[str, ...]
    authority: str
    reuse: str
    classification: str

    @property
    def homes(self) -> tuple[str, ...]:
        """The declared owner homes, in declared order."""
        return tuple(owner.home for owner in self.owners)

    @property
    def home_set(self) -> frozenset[str]:
        """The declared owner homes as a set — the subject of the DUPLICATE rule."""
        return frozenset(self.homes)

    @property
    def resolving_homes(self) -> tuple[str, ...]:
        return tuple(owner.home for owner in self.owners if owner.resolves)

    @property
    def missing_symbols(self) -> tuple[str, ...]:
        return tuple(symbol for owner in self.owners for symbol in owner.missing_symbols)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "ordinal": self.ordinal,
            "name": self.name,
            "duty": self.duty,
            "canonical_stages": list(self.canonical_stages),
            "produces": self.produces,
            "owners": [owner.to_dict() for owner in self.owners],
            "gate": self.gate.to_dict(),
            "declared_evidence": list(self.declared_evidence),
            "resolving_evidence": list(self.resolving_evidence),
            "authority": self.authority,
            "reuse": self.reuse,
            "classification": self.classification,
        }


@dataclass(frozen=True, slots=True)
class LifecycleState:
    """One canonical stage of the perpetual evolution cycle.

    Read from :mod:`engine.uckp.evolution` — the Article 14 authority — and never declared
    here. ``claimed_by`` is the phases of this register that claim the stage; the declaration
    requires exactly one, so zero (an unowned stage, e.g. one appended under Article 17) and
    two (two authorities over one stage) are both visible rather than inferred.
    """

    name: str
    ordinal: int
    successor: str
    terminal: bool
    claimed_by: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ordinal": self.ordinal,
            "successor": self.successor,
            "terminal": self.terminal,
            "claimed_by": list(self.claimed_by),
        }


@dataclass(frozen=True, slots=True)
class Dependency:
    """One dependency edge of the loop.

    ``kind`` is ``"phase"`` for the preceding phase in the loop and ``"home"`` for an owner
    home the phase binds — the two sources the declaration's plan contract names. A phase
    edge always points at a lower ordinal, which is the property the dependency-integrity
    verification measures.
    """

    phase: str
    depends_on: str
    kind: str

    def to_dict(self) -> dict[str, Any]:
        return {"phase": self.phase, "depends_on": self.depends_on, "kind": self.kind}


@dataclass(frozen=True, slots=True)
class Ownership:
    """One owner home and every phase of this register that binds it.

    A home bound by more than one phase is lawful — owners are shared. What is not lawful is
    two phases declaring an *identical* home set, which is the DUPLICATE rule and is measured
    over :attr:`Phase.home_set`, not here.
    """

    home: str
    phases: tuple[str, ...]
    state: str

    @property
    def resolves(self) -> bool:
        return self.state == PRESENT

    def to_dict(self) -> dict[str, Any]:
        return {"home": self.home, "phases": list(self.phases), "state": self.state}


@dataclass(frozen=True, slots=True)
class ObjectKind:
    """One evolution object kind, and the phase that produces it."""

    identifier: str
    name: str
    phase: str
    mandated: bool
    purpose: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "name": self.name,
            "phase": self.phase,
            "mandated": self.mandated,
            "purpose": self.purpose,
        }


@dataclass(frozen=True, slots=True)
class RequiredField:
    """One field every evolution object must carry, and how it is derived."""

    identifier: str
    field_name: str
    name: str
    non_empty: bool
    derivation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "field": self.field_name,
            "name": self.name,
            "non_empty": self.non_empty,
            "derivation": self.derivation,
        }


@dataclass(frozen=True, slots=True)
class IdentityRule:
    """How an evolution object's identity is derived. Read, never restated.

    The prefix, the width and the input field names all come from the declaration, so this
    engine contains no identifier literal and cannot mint into a population it does not own.
    ``derivation_home`` and ``digest_home`` are the owners of the rule and of the digest; both
    are pointers, because an identity rule copied here would be a second identity authority.
    """

    prefix: str
    width: int
    inputs: tuple[str, ...]
    derivation_home: str
    derivation_symbol: str
    digest_home: str
    digest_symbol: str
    anonymity_rule: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "prefix": self.prefix,
            "width": self.width,
            "inputs": list(self.inputs),
            "derivation_home": self.derivation_home,
            "derivation_symbol": self.derivation_symbol,
            "digest_home": self.digest_home,
            "digest_symbol": self.digest_symbol,
            "anonymity_rule": self.anonymity_rule,
        }


@dataclass(frozen=True, slots=True)
class SourceCondition:
    """One ``include_when`` test a source entry must pass to become a candidate."""

    field_name: str
    op: str
    value: Any

    def to_dict(self) -> dict[str, Any]:
        return {"field": self.field_name, "op": self.op, "value": self.value}


@dataclass(frozen=True, slots=True)
class DiscoverySource:
    """One artifact another owner already publishes, and how candidates are read from it.

    Discovery never inspects the working tree: it reads sealed derived-truth artifacts, so a
    candidate is always attributable to an owner that measured it. ``path`` is empty for the
    two internal sources that select from the declaration itself.
    """

    identifier: str
    name: str
    owner: str
    path: str
    selector: tuple[str, ...]
    form: str
    candidate_class: str
    fields: tuple[tuple[str, str], ...]
    reason_template: str
    target_template: str
    include_when: tuple[SourceCondition, ...]

    @property
    def internal(self) -> bool:
        """True when the source selects from the declaration rather than from an artifact."""
        return not self.path

    def field_for(self, canonical: str) -> str:
        for name, source_field in self.fields:
            if name == canonical:
                return source_field
        return ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "name": self.name,
            "owner": self.owner,
            "path": self.path,
            "selector": list(self.selector),
            "form": self.form,
            "candidate_class": self.candidate_class,
            "fields": [list(pair) for pair in self.fields],
            "include_when": [entry.to_dict() for entry in self.include_when],
        }


@dataclass(frozen=True, slots=True)
class DiscoveryDuty:
    """One duty discovery must discharge, and the sources that may discharge it."""

    identifier: str
    duty: str
    satisfied_by: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "duty": self.duty,
            "satisfied_by": list(self.satisfied_by),
        }


@dataclass(frozen=True, slots=True)
class Criterion:
    """One declared validation dimension, verification dimension or certification proof.

    A single type for all three because all three have the same shape — an obligation that is
    either met or not, and a blocking flag. ``bound_gate`` is empty for validations and
    certifications, which the declaration does not bind to a gate.
    """

    identifier: str
    subject: str
    obligation: str
    blocking: bool
    bound_gate: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "subject": self.subject,
            "obligation": self.obligation,
            "blocking": self.blocking,
            "bound_gate": self.bound_gate,
        }


@dataclass(frozen=True, slots=True)
class Invariant:
    """One zero-tolerance invariant, its measure name and the value it must hold."""

    identifier: str
    invariant: str
    measure: str
    expect: int
    blocking: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "invariant": self.invariant,
            "measure": self.measure,
            "expect": self.expect,
            "blocking": self.blocking,
        }


@dataclass(frozen=True, slots=True)
class HistorySpec:
    """Where the history is projected, and which ledger owns its append rules."""

    file: str
    schema: str
    version: str
    append_only: bool
    ledger_home: str
    ledger_symbol: str
    document_symbol: str
    rehydration_symbol: str
    dimensions: tuple[str, ...]
    queryable_by: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "schema": self.schema,
            "version": self.version,
            "append_only": self.append_only,
            "ledger_home": self.ledger_home,
            "ledger_symbol": self.ledger_symbol,
            "document_symbol": self.document_symbol,
            "rehydration_symbol": self.rehydration_symbol,
            "dimensions": list(self.dimensions),
            "queryable_by": list(self.queryable_by),
        }


@dataclass(frozen=True, slots=True)
class PlanContract:
    """Where each part of a plan is composed from. The plan is derived, never authored."""

    identifier: str
    objectives_from: str
    steps_from: str
    dependencies_from: str
    risk_from: str
    validation_criteria_from: str
    verification_criteria_from: str
    certification_criteria_from: str
    rollback_strategy: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "objectives_from": self.objectives_from,
            "steps_from": self.steps_from,
            "dependencies_from": self.dependencies_from,
            "risk_from": self.risk_from,
            "validation_criteria_from": self.validation_criteria_from,
            "verification_criteria_from": self.verification_criteria_from,
            "certification_criteria_from": self.certification_criteria_from,
            "rollback_strategy": self.rollback_strategy,
        }


@dataclass(frozen=True, slots=True)
class UnknownProbe:
    """The declared unknown subject: an object of no known class, carried as a candidate.

    It is not a test fixture beside the code. It is discovered by a declared source and
    traverses the same controller as everything else, which is the only way the claim "the
    engine does not need to know what the subject is" can be measured rather than asserted.
    """

    identifier: str
    subject: str
    subject_class: str
    unknown_stage_term: str
    must_not_require: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "subject": self.subject,
            "subject_class": self.subject_class,
            "unknown_stage_term": self.unknown_stage_term,
            "must_not_require": list(self.must_not_require),
        }


@dataclass(frozen=True, slots=True)
class Boundary:
    """One declared non-duplication boundary against another located owner.

    The declaration carries these so the reuse-before-create question is answered in the
    register rather than re-litigated in review. ``other_subject`` and ``this_subject`` are
    kept as separate fields because the whole content of a boundary is that the two subjects
    differ; collapsing them into one "scope" string would make the distinction unstateable.
    """

    identifier: str
    other_owner: str
    other_subject: str
    this_subject: str
    why_not_duplicate: str
    other_owner_state: str

    @property
    def other_owner_resolves(self) -> bool:
        """True when the owner this boundary is drawn against actually exists.

        A boundary against a home that has vanished is not a satisfied boundary — it is a
        boundary nobody can check, which is why the state is measured rather than assumed.
        """
        return self.other_owner_state == PRESENT

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "other_owner": self.other_owner,
            "other_subject": self.other_subject,
            "this_subject": self.this_subject,
            "why_not_duplicate": self.why_not_duplicate,
            "other_owner_state": self.other_owner_state,
            "other_owner_resolves": self.other_owner_resolves,
        }


@dataclass(frozen=True, slots=True)
class ExitCriterion:
    """One declared exit criterion of one implementation phase of the programme.

    ``phase`` names an implementation phase (``AUE-001``…) and never a loop position
    (``AUE-P-01``…): the two sequences are different subjects and the declaration keeps them
    apart, so this model does too.

    ``measure`` names the violation count the engine computes for this criterion and ``expect``
    the value it must hold. The pair is what makes the criterion *measurable* rather than merely
    stated: for its first three epochs this block was declared, loaded and rendered while nothing
    evaluated it, so fifteen exit conditions were of unknown compliance and read as satisfied. The
    engine implements one function per measure name and refuses a name it cannot compute, exactly
    as it does for the mandatory invariants — a measure that defaulted to zero would report an
    unmet exit criterion as met.
    """

    identifier: str
    phase: str
    criterion: str
    measure: str
    expect: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "phase": self.phase,
            "criterion": self.criterion,
            "measure": self.measure,
            "expect": self.expect,
        }


@dataclass(frozen=True, slots=True)
class SelfEvolution:
    """The programme's own demonstration that it can close a gap in its own foundation.

    Every field except the two measured ones is declared. ``missing_symbols`` is the shortfall
    of ``required_symbols`` against the names actually bound in ``home``, so the closure is
    re-measured on every run: if the surface is removed the gap reopens by itself, which is the
    only version of this proof that cannot rot into a claim about the past.
    """

    identifier: str
    subject_identity: str
    detected_by: str
    gap: str
    previous_state: str
    target_state: str
    required_symbols: tuple[str, ...]
    home: str
    authority: str
    executed_through: str
    evidence: tuple[str, ...]
    home_state: str
    missing_symbols: tuple[str, ...]
    unresolved_evidence: tuple[str, ...]

    @property
    def home_resolves(self) -> bool:
        return self.home_state == PRESENT

    @property
    def closed(self) -> bool:
        """True when the home resolves, every required symbol binds, and evidence resolves."""
        return self.home_resolves and not self.missing_symbols and not self.unresolved_evidence

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "subject_identity": self.subject_identity,
            "detected_by": self.detected_by,
            "gap": self.gap,
            "previous_state": self.previous_state,
            "target_state": self.target_state,
            "required_symbols": list(self.required_symbols),
            "home": self.home,
            "authority": self.authority,
            "executed_through": self.executed_through,
            "evidence": list(self.evidence),
            "home_state": self.home_state,
            "missing_symbols": list(self.missing_symbols),
            "unresolved_evidence": list(self.unresolved_evidence),
            "closed": self.closed,
        }


@dataclass(frozen=True, slots=True)
class EvolutionAuthority:
    """The deterministic authority model resolved from the canonical evolution declaration.

    This is the whole interface the engine phases of Epoch 3 are built against. They read
    registers, phases, stages and rules from an instance of this class; none of them may hold
    a list of its own, which is how "no hard-coded register list in the engine" is enforced
    structurally rather than by review.
    """

    programme_id: str
    version: str
    source: str
    stage_authority_home: str
    identity: IdentityRule
    classifications: tuple[Classification, ...]
    registers: tuple[Register, ...]
    phases: tuple[Phase, ...]
    dependencies: tuple[Dependency, ...]
    ownership: tuple[Ownership, ...]
    lifecycle_states: tuple[LifecycleState, ...]
    object_kinds: tuple[ObjectKind, ...]
    required_fields: tuple[RequiredField, ...]
    discovery_sources: tuple[DiscoverySource, ...]
    discovery_duties: tuple[DiscoveryDuty, ...]
    validations: tuple[Criterion, ...]
    verifications: tuple[Criterion, ...]
    certifications: tuple[Criterion, ...]
    mandatory: tuple[Invariant, ...]
    history: HistorySpec
    plan_contract: PlanContract
    unknown_probe: UnknownProbe
    boundaries: tuple[Boundary, ...]
    exit_criteria: tuple[ExitCriterion, ...]
    self_evolution: SelfEvolution

    def classification(self, identifier: str) -> Classification:
        for entry in self.classifications:
            if entry.identifier == identifier:
                return entry
        raise EvolutionAuthorityError(
            "the declaration defines no such classification", classification=identifier
        )

    def phase(self, identifier: str) -> Phase:
        for entry in self.phases:
            if entry.identifier == identifier:
                return entry
        raise EvolutionAuthorityError("the declaration defines no such phase", phase=identifier)

    def register(self, file: str) -> Register:
        for entry in self.registers:
            if entry.file == file:
                return entry
        raise EvolutionAuthorityError("the declaration defines no such register", register=file)

    def phases_claiming(self, stage: str) -> tuple[str, ...]:
        """The phases claiming one canonical stage. Empty means the stage is unowned."""
        for state in self.lifecycle_states:
            if state.name == stage:
                return state.claimed_by
        raise EvolutionAuthorityError("not a canonical evolution stage", stage=stage)

    def registers_of(self, phase: str) -> tuple[Register, ...]:
        return tuple(entry for entry in self.registers if entry.owner_phase == phase)

    def object_kind_of(self, phase: str) -> ObjectKind:
        for entry in self.object_kinds:
            if entry.phase == phase:
                return entry
        raise EvolutionAuthorityError("no object kind is produced by that phase", phase=phase)

    def discovery_source(self, identifier: str) -> DiscoverySource:
        for entry in self.discovery_sources:
            if entry.identifier == identifier:
                return entry
        raise EvolutionAuthorityError("no such discovery source", source=identifier)

    def phase_claiming(self, stage: str) -> str:
        """The single phase claiming a canonical stage.

        Safe to return one value rather than a tuple because the loader has already refused
        any declaration in which a stage is claimed by zero or by more than one phase.
        """
        return self.phases_claiming(stage)[0]

    def stage_of(self, phase: str) -> str:
        """The canonical stage a phase's objects occupy, as its lifecycle state.

        A phase may claim several stages; the earliest in cycle order is the one its object
        enters the loop at, and the later ones are claimed by the same phase, so no other
        phase's object can occupy them.
        """
        for state in self.lifecycle_states:
            if phase in state.claimed_by:
                return state.name
        raise EvolutionAuthorityError("that phase claims no canonical stage", phase=phase)

    def mandated_kinds(self) -> tuple[ObjectKind, ...]:
        return tuple(entry for entry in self.object_kinds if entry.mandated)

    def phase_by_ordinal(self, ordinal: int) -> Phase:
        for entry in self.phases:
            if entry.ordinal == ordinal:
                return entry
        raise EvolutionAuthorityError(
            "the declaration declares no phase at that position", ordinal=ordinal
        )

    def dependencies_of(self, phase: str) -> tuple[str, ...]:
        """The declared dependencies of one phase, derived exactly as the field mandate says.

        AUE-FLD-07 defines them as "the owner homes this phase binds, plus the phases this phase
        depends on". Derived here, once, from the authority's own dependency edges — so eleven
        phase modules cannot each derive it slightly differently, and it can never disagree with
        the graph the dependency-integrity verification measures.
        """
        homes = tuple(
            edge.depends_on
            for edge in self.dependencies
            if edge.phase == phase and edge.kind == "home"
        )
        earlier = tuple(
            edge.depends_on
            for edge in self.dependencies
            if edge.phase == phase and edge.kind == "phase"
        )
        return homes + earlier

    def to_document(self) -> dict[str, Any]:
        """The authority as a canonical document — the input to :meth:`digest`."""
        return {
            "programme": self.programme_id,
            "version": self.version,
            "stage_authority_home": self.stage_authority_home,
            "identity": self.identity.to_dict(),
            "classifications": [entry.to_dict() for entry in self.classifications],
            "registers": [entry.to_dict() for entry in self.registers],
            "phases": [entry.to_dict() for entry in self.phases],
            "dependencies": [entry.to_dict() for entry in self.dependencies],
            "ownership": [entry.to_dict() for entry in self.ownership],
            "lifecycle_states": [entry.to_dict() for entry in self.lifecycle_states],
            "object_kinds": [entry.to_dict() for entry in self.object_kinds],
            "required_fields": [entry.to_dict() for entry in self.required_fields],
            "discovery_sources": [entry.to_dict() for entry in self.discovery_sources],
            "discovery_duties": [entry.to_dict() for entry in self.discovery_duties],
            "validations": [entry.to_dict() for entry in self.validations],
            "verifications": [entry.to_dict() for entry in self.verifications],
            "certifications": [entry.to_dict() for entry in self.certifications],
            "mandatory": [entry.to_dict() for entry in self.mandatory],
            "history": self.history.to_dict(),
            "plan_contract": self.plan_contract.to_dict(),
            "unknown_probe": self.unknown_probe.to_dict(),
            "boundaries": [entry.to_dict() for entry in self.boundaries],
            "exit_criteria": [entry.to_dict() for entry in self.exit_criteria],
            "self_evolution": self.self_evolution.to_dict(),
        }

    def digest(self) -> str:
        """The content-addressed digest of the authority.

        Deliberately excludes :attr:`source`: the same declaration read from a path and from
        an in-memory document must produce one digest, or a replay test would only be proving
        that the file was read from the same place twice.
        """
        from engine.uckp.canonical import content_hash

        return content_hash(self.to_document())


__all__ = [
    "ABSENT",
    "PRESENT",
    "UNREADABLE",
    "Boundary",
    "Classification",
    "Criterion",
    "Dependency",
    "DiscoveryDuty",
    "DiscoverySource",
    "EvolutionAuthority",
    "EvolutionAuthorityError",
    "ExitCriterion",
    "Gate",
    "HistorySpec",
    "IdentityRule",
    "Invariant",
    "LifecycleState",
    "ObjectKind",
    "Owner",
    "Ownership",
    "Phase",
    "PlanContract",
    "Register",
    "RequiredField",
    "SelfEvolution",
    "SourceCondition",
    "UnknownProbe",
]
