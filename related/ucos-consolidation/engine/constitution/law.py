"""UCOS-CEL-0001 Part 01 — the Constitutional Execution Law (Requirement 010).

Repository truth before this module existed
-------------------------------------------
The repository *contained* constitutional rules: ``00-CEP`` declares the execution,
validation, certification and ratification constitutions; ``00-CMG`` declares the
meta-governance constitution; ``engine.nucleus.law`` enforces one of them (ownership).
What no module supplied was the clause set that makes **execution itself** unlawful when
its preconditions are unproven. Ownership was enforced; sequencing, dependency closure,
authority closure, mutation discipline and state cleanliness were *followed*.

That difference is the whole of this package. A rule a human follows is a rule that can
be skipped in a hurry; a rule the repository enforces cannot be. This module supplies the
missing clauses and the invariants that measure them, and nothing else: it creates no
second ordering mechanism (that remains
:mod:`engine.foundation.composition.ordering`), no second identifier scheme (that remains
:mod:`engine.registry.universal.identity`), no second hash primitive (that remains
:mod:`engine.uckp.canonical`) and no second lifecycle (that remains
:mod:`engine.nucleus.lifecycle`, ``UCL-000001``).

Openness
--------
Clauses, invariants and acceptance criteria are **tuples of data**. A new constitutional
rule is one appended entry, not an edit to a function: no function in this package
branches on a specific clause id, subject, capability, owner or domain. That is what lets
the law grow without any prior determination changing meaning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.uckp.canonical import content_hash

#: The immutable identity of the constitutional execution law.
LAW_ID = "UCOS-CEL-0001"

#: Versioned so the law can be *extended* without any prior determination changing.
LAW_VERSION = "1.0.0"

#: The supreme clause. Every clause below elaborates it.
SUPREMACY_CLAUSE = (
    "Execution is a privilege granted by proof, never a default granted by silence. "
    "No artifact executes, mutates, registers or certifies until the repository has "
    "derived — not been told — that every dependency, authority, governance, identity, "
    "registration, certification, verification, traceability and evidence obligation "
    "bearing on it is closed. Where the proof is absent, the act is refused."
)


@dataclass(frozen=True, slots=True)
class Clause:
    """One clause of the constitutional execution law."""

    clause_id: str
    title: str
    statement: str
    refuses: str = ""
    realized_by: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "title": self.title,
            "statement": self.statement,
            "refuses": self.refuses,
            "realized_by": self.realized_by,
        }


@dataclass(frozen=True, slots=True)
class Invariant:
    """A property an implementation must *prove* by measurement, not assert."""

    invariant_id: str
    name: str
    statement: str
    clause_id: str
    blocking: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "name": self.name,
            "statement": self.statement,
            "clause_id": self.clause_id,
            "blocking": self.blocking,
        }


@dataclass(frozen=True, slots=True)
class AcceptanceCriterion:
    """One statement that must measure true before the system is complete.

    Held as data beside the law rather than in a checklist, so the question "is the
    constitutional execution system finished?" is answered by running a gate over the
    repository instead of by reading a document and agreeing with it.
    """

    criterion_id: str
    statement: str
    invariant_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "statement": self.statement,
            "invariant_id": self.invariant_id,
        }


#: The clauses of the constitutional execution law (DATA — extend by appending).
EXECUTION_CLAUSES: tuple[Clause, ...] = (
    Clause(
        "CEL-01",
        "Dependencies are discovered, never declared as an order",
        "Every executable artifact, capability, engine, registry, authority, governance "
        "object, knowledge object and constitutional object SHALL declare what it "
        "requires, and the repository SHALL derive the dependency graph from those "
        "declarations. A declared execution sequence is not a dependency and confers no "
        "execution right.",
        refuses="an execution whose dependency graph names an unregistered referent",
        realized_by="UCOS-CDG-000001",
    ),
    Clause(
        "CEL-02",
        "Execution order is derived by topological ordering",
        "Execution SHALL occur only in an order derived from the dependency graph by the "
        "single ordering authority. A caller SHALL NOT supply, override, hint at or "
        "partially constrain the order.",
        refuses="any execution request carrying a caller-supplied order",
        realized_by="UCOS-CEP-EXEC-000001",
    ),
    Clause(
        "CEL-03",
        "Legality is proven before execution, or execution is refused",
        "Every execution request SHALL prove dependency, governance, authority, identity, "
        "registry, certification, verification, traceability and evidence closure. There "
        "is no partial legality, no assumed legality and no trust-based legality: an "
        "unproven obligation is a refused request.",
        refuses="an execution over a subject with any unclosed obligation",
        realized_by="UCOS-CLE-000001",
    ),
    Clause(
        "CEL-04",
        "Mutation occurs only through the gateway",
        "Every mutation of repository truth SHALL execute the sequence proposal, "
        "evidence, validation, verification, certification, registration, truth update. "
        "A mutation that skips a stage does not apply — not partially, not provisionally, "
        "not pending review.",
        refuses="a truth update that did not discharge every gateway stage",
        realized_by="UCOS-CMG-EXEC-000001",
    ),
    Clause(
        "CEL-05",
        "No subject is its own authority",
        "Authority, certification and ownership relations SHALL be acyclic, and no "
        "subject SHALL certify, validate, verify or ratify itself. A subject that "
        "derives its own permission to exist has proven nothing.",
        refuses="a cycle in the authority, certification or ownership relation, and any "
        "self-attestation",
        realized_by="UCOS-CAG-000001",
    ),
    Clause(
        "CEL-06",
        "Replay runs to a deterministic fixed point",
        "Every mutation SHALL trigger recompute, revalidate, reverify, recertify, "
        "reregister and replay until two consecutive rounds are byte-identical. "
        "Certification against a state that has not converged is void.",
        refuses="a certification taken before the fixed point, and a run that does not "
        "converge within its declared bound",
        realized_by="UCOS-ARE-000001",
    ),
    Clause(
        "CEL-07",
        "Dirty state is not measurable",
        "Verification, certification, registration, measurement and governance SHALL "
        "read only constitutionally committed state. A reading taken while a mutation is "
        "open describes a state that never existed and is therefore not evidence.",
        refuses="any measurement, certification or registration taken against an open "
        "mutation or an unsealed state",
        realized_by="UCOS-DPE-000001",
    ),
    Clause(
        "CEL-08",
        "Reuse precedes creation",
        "Creation SHALL be permitted only after discovery, assimilation, search, reuse "
        "analysis and gap analysis prove that no canonical capability, owner, artifact or "
        "knowledge already covers the goal. Duplication is not inefficiency; it is a "
        "second truth.",
        refuses="a creation where a canonical owner, capability, artifact or knowledge "
        "already exists",
        realized_by="UCOS-RTAG-000001",
    ),
    Clause(
        "CEL-09",
        "Metadata is the licence to exist",
        "Every executable artifact SHALL declare its canonical owner, authorities, "
        "dependencies, constraints, inputs, outputs, registrations, certifications, and "
        "its validation, verification, replay, governance, evolution, lineage and "
        "traceability rules. Without complete metadata an artifact is not executable, not "
        "governable, not certifiable and not registerable.",
        refuses="an artifact missing any mandated metadata facet",
        realized_by="UCOS-CMM-000001",
    ),
    Clause(
        "CEL-10",
        "The system enforces; people do not follow",
        "Execution, dependency, registration, certification, governance, replay and "
        "evolution order SHALL each be derived by the repository. A rule whose only "
        "enforcement is a person remembering it is not a constitutional rule.",
        refuses="any ordering, sequencing or gating decision taken outside the derived plan",
        realized_by="UCOS-CEP-EXEC-000001",
    ),
    Clause(
        "CEL-11",
        "Every cycle elevates",
        "A completed constitutional cycle SHALL produce new knowledge, new evidence and a "
        "capability reading that does not regress, and that output SHALL be the input of "
        "the next cycle. A cycle that leaves the repository exactly as it found it has "
        "not run.",
        refuses="a cycle whose capability reading regresses against its predecessor",
        realized_by="UCOS-UACE-000001",
    ),
)


#: The invariants the enforcement layer must *measure*. Zero-tolerance by construction.
EXECUTION_INVARIANTS: tuple[Invariant, ...] = (
    Invariant(
        "CEL-INV-01",
        "artifacts_without_complete_metadata",
        "The count of artifacts missing a mandated metadata facet is zero.",
        "CEL-09",
    ),
    Invariant(
        "CEL-INV-02",
        "unknown_referents",
        "The count of declared referents naming an unregistered subject is zero.",
        "CEL-01",
    ),
    Invariant(
        "CEL-INV-03",
        "dependency_cycles",
        "The count of subjects lying on a cycle in the dependency relation is zero.",
        "CEL-01",
    ),
    Invariant(
        "CEL-INV-04",
        "authority_cycles",
        "The count of subjects lying on a cycle in the authority relation is zero.",
        "CEL-05",
    ),
    Invariant(
        "CEL-INV-05",
        "certification_cycles",
        "The count of subjects lying on a cycle in the certification relation is zero.",
        "CEL-05",
    ),
    Invariant(
        "CEL-INV-06",
        "ownership_cycles",
        "The count of subjects lying on a cycle in the ownership relation is zero.",
        "CEL-05",
    ),
    Invariant(
        "CEL-INV-07",
        "self_attestations",
        "The count of subjects that certify, validate, verify or ratify themselves is zero.",
        "CEL-05",
    ),
    Invariant(
        "CEL-INV-08",
        "illegal_subjects",
        "The count of subjects that fail any legality proof is zero.",
        "CEL-03",
    ),
    Invariant(
        "CEL-INV-09",
        "unplaceable_subjects",
        "The count of subjects the derived execution order could not place is zero.",
        "CEL-02",
    ),
    Invariant(
        "CEL-INV-10",
        "duplicate_capabilities",
        "The count of capabilities declared as an output by more than one subject is zero.",
        "CEL-08",
    ),
    Invariant(
        "CEL-INV-11",
        "duplicate_owners",
        "The count of subjects resolving to more than one canonical owner is zero.",
        "CEL-08",
    ),
    Invariant(
        "CEL-INV-12",
        "subjects_without_identifier",
        "The count of subjects lacking a well-formed universal identifier is zero.",
        "CEL-03",
    ),
)


#: The acceptance criteria of Requirement 011, each bound to the invariant that measures
#: it. A criterion with no measuring invariant would be prose, so every entry names one.
ACCEPTANCE_CRITERIA: tuple[AcceptanceCriterion, ...] = (
    AcceptanceCriterion(
        "AC-CEL-01",
        "A capability cannot execute unless its dependencies are complete.",
        "CEL-INV-02",
    ),
    AcceptanceCriterion(
        "AC-CEL-02",
        "A registry cannot update unless governance is complete.",
        "CEL-INV-08",
    ),
    AcceptanceCriterion(
        "AC-CEL-03",
        "A certification cannot occur unless authority is complete.",
        "CEL-INV-08",
    ),
    AcceptanceCriterion(
        "AC-CEL-04",
        "A mutation cannot occur unless verification is complete.",
        "CEL-INV-08",
    ),
    AcceptanceCriterion(
        "AC-CEL-05",
        "A replay cannot stop until a deterministic fixed point is achieved.",
        "CEL-INV-08",
    ),
    AcceptanceCriterion(
        "AC-CEL-06",
        "An artifact cannot exist without canonical ownership.",
        "CEL-INV-01",
    ),
    AcceptanceCriterion(
        "AC-CEL-07",
        "An executable cannot run without constitutional metadata.",
        "CEL-INV-01",
    ),
    AcceptanceCriterion(
        "AC-CEL-08",
        "A capability cannot be created if a canonical capability already exists.",
        "CEL-INV-10",
    ),
    AcceptanceCriterion(
        "AC-CEL-09",
        "A governance action cannot execute without constitutional authority.",
        "CEL-INV-04",
    ),
    AcceptanceCriterion(
        "AC-CEL-10",
        "A constitutional violation cannot be hidden.",
        "CEL-INV-08",
    ),
    AcceptanceCriterion(
        "AC-CEL-11",
        "A dependency cannot be skipped.",
        "CEL-INV-03",
    ),
    AcceptanceCriterion(
        "AC-CEL-12",
        "An execution order cannot be manually overridden.",
        "CEL-INV-09",
    ),
    AcceptanceCriterion(
        "AC-CEL-13",
        "A circular authority cannot be certified.",
        "CEL-INV-05",
    ),
    AcceptanceCriterion(
        "AC-CEL-14",
        "A dirty state cannot be measured.",
        "CEL-INV-08",
    ),
    AcceptanceCriterion(
        "AC-CEL-15",
        "An unverifiable state cannot be certified.",
        "CEL-INV-12",
    ),
    AcceptanceCriterion(
        "AC-CEL-16",
        "A trust-based decision cannot be accepted.",
        "CEL-INV-07",
    ),
)


def clause(clause_id: str) -> Clause:
    """Return the clause with ``clause_id`` or fail closed."""
    for item in EXECUTION_CLAUSES:
        if item.clause_id == clause_id:
            return item
    from engine.constitution.errors import ConstitutionalError

    raise ConstitutionalError(
        "no such execution clause",
        clause_id=clause_id,
        allowed=[c.clause_id for c in EXECUTION_CLAUSES],
    )


def invariant(invariant_id: str) -> Invariant:
    """Return the invariant with ``invariant_id`` or fail closed."""
    for item in EXECUTION_INVARIANTS:
        if item.invariant_id == invariant_id:
            return item
    from engine.constitution.errors import ConstitutionalError

    raise ConstitutionalError(
        "no such execution invariant",
        invariant_id=invariant_id,
        allowed=[i.invariant_id for i in EXECUTION_INVARIANTS],
    )


def blocking_invariant_ids() -> tuple[str, ...]:
    """The identifiers of every invariant whose violation refuses the act, ordered."""
    return tuple(sorted(i.invariant_id for i in EXECUTION_INVARIANTS if i.blocking))


def to_document() -> dict[str, Any]:
    """The whole law as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-execution-law",
        "law_id": LAW_ID,
        "version": LAW_VERSION,
        "supremacy_clause": SUPREMACY_CLAUSE,
        "clauses": [c.to_dict() for c in EXECUTION_CLAUSES],
        "invariants": [i.to_dict() for i in EXECUTION_INVARIANTS],
        "acceptance_criteria": [a.to_dict() for a in ACCEPTANCE_CRITERIA],
        "closed_set": False,
    }


def digest() -> str:
    """The content digest of the law, computed with the one canonical primitive."""
    return content_hash(to_document())


__all__ = [
    "ACCEPTANCE_CRITERIA",
    "EXECUTION_CLAUSES",
    "EXECUTION_INVARIANTS",
    "LAW_ID",
    "LAW_VERSION",
    "SUPREMACY_CLAUSE",
    "AcceptanceCriterion",
    "Clause",
    "Invariant",
    "blocking_invariant_ids",
    "clause",
    "digest",
    "invariant",
    "to_document",
]
