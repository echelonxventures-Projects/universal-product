"""UCOS-CEL-0001 Part 02 — the Constitutional Enforcement Layer (Requirement 010).

The law declares twelve invariants and sixteen acceptance criteria. This module measures
them. That distinction is the difference between a repository that *contains* rules and
one that *enforces* them: a clause nobody counts is a preference, and a criterion whose
only evidence is a person agreeing with it is a trust-based decision, which CEL forbids.

Every invariant in :data:`~engine.constitution.law.EXECUTION_INVARIANTS` has exactly one
measurement here, keyed by its identifier. The measurement functions are held in a
mapping rather than a chain of conditionals, so an invariant appended to the law without a
measurement is reported as **unmeasured and blocking** — the enforcement layer fails
closed on its own incompleteness rather than silently passing a rule it cannot count.

Each acceptance criterion resolves to the invariant that measures it, so
"is the constitutional execution system complete?" is answered by running this gate over
the repository and reading the number, not by reading a certificate and believing it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from engine.constitution import assimilation as assimilation_gate
from engine.constitution import authority as authority_graph
from engine.constitution import dependency as dependency_graph
from engine.constitution import legality as legality_engine
from engine.constitution import planner as execution_planner
from engine.constitution.errors import AcceptanceFailure
from engine.constitution.law import (
    ACCEPTANCE_CRITERIA,
    EXECUTION_INVARIANTS,
    LAW_ID,
)
from engine.constitution.metadata import Population
from engine.uckp.canonical import content_hash

#: The identity of the enforcement layer this module realises.
ENFORCEMENT_ID = "UCOS-CEL-ENFORCE-0001"

#: Versioned so measurements can be *added* without prior reports changing meaning.
ENFORCEMENT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class Measured:
    """One invariant, counted over one population, with the subjects that violated it."""

    invariant_id: str
    name: str
    count: int
    subjects: tuple[str, ...]
    measured: bool = True

    @property
    def satisfied(self) -> bool:
        """True iff the invariant was measurable and measured zero."""
        return self.measured and self.count == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "name": self.name,
            "count": self.count,
            "subjects": list(self.subjects),
            "measured": self.measured,
            "satisfied": self.satisfied,
        }


#: A measurement: given the whole derived view of a population, name the violators.
Measurement = Callable[["View"], "tuple[str, ...]"]


@dataclass(frozen=True, slots=True)
class View:
    """Everything derived from one population, computed once and shared by every measurement.

    Without this, twelve measurements would each rebuild the graph and re-derive the plan.
    That would be slow, but far worse: twelve independently derived views could disagree,
    and a report whose invariants were measured against different states is not a report.
    """

    population: Population
    graph: dependency_graph.DependencyGraph
    authority: authority_graph.AuthorityReport
    legality: legality_engine.LegalityReport
    plan: execution_planner.ExecutionPlan

    @classmethod
    def of(cls, population: Population) -> View:
        graph = dependency_graph.build(population)
        return cls(
            population=population,
            graph=graph,
            authority=authority_graph.analyse(population, graph),
            legality=legality_engine.assess(population, graph),
            plan=execution_planner.plan(population),
        )


def _incomplete_metadata(view: View) -> tuple[str, ...]:
    return tuple(record.subject for record in view.population.incomplete())


def _unknown_referents(view: View) -> tuple[str, ...]:
    return tuple(sorted({edge.source for edge in view.graph.unknown_referents()}))


def _cycles_in(relation: str) -> Measurement:
    """Build the measurement for one relation's cycles — four invariants, one shape."""

    def measure(view: View) -> tuple[str, ...]:
        return view.graph.cycles(relation) if relation in view.graph.relations else ()

    return measure


def _self_attestations(view: View) -> tuple[str, ...]:
    return tuple(sorted({f.subject for f in view.authority.self_attestations}))


def _illegal_subjects(view: View) -> tuple[str, ...]:
    return tuple(verdict.subject for verdict in view.legality.illegal)


def _unplaceable(view: View) -> tuple[str, ...]:
    return view.plan.unplaceable


def _duplicate_capabilities(view: View) -> tuple[str, ...]:
    duplicates = assimilation_gate.duplicate_capabilities(view.population)
    return tuple(sorted({subject for subjects in duplicates.values() for subject in subjects}))


def _duplicate_owners(view: View) -> tuple[str, ...]:
    # CEL-INV-11 counts subjects whose ownership does not resolve to exactly one owner.
    # Zero owners and two owners are the same defect at different ends: in both cases the
    # question "who owns this?" has no single answer.
    return tuple(
        record.subject for record in view.population if len(record.entries("canonical_owner")) != 1
    )


def _without_identifier(view: View) -> tuple[str, ...]:
    return tuple(record.subject for record in view.population if not record.identity_well_formed)


#: Invariant id → the measurement that counts it. An invariant declared in the law with
#: no entry here is reported unmeasured and blocking; it is never silently satisfied.
MEASUREMENTS: Mapping[str, Measurement] = {
    "CEL-INV-01": _incomplete_metadata,
    "CEL-INV-02": _unknown_referents,
    "CEL-INV-03": _cycles_in("dependencies"),
    "CEL-INV-04": _cycles_in("authorities"),
    "CEL-INV-05": _cycles_in("certifications"),
    "CEL-INV-06": _cycles_in("canonical_owner"),
    "CEL-INV-07": _self_attestations,
    "CEL-INV-08": _illegal_subjects,
    "CEL-INV-09": _unplaceable,
    "CEL-INV-10": _duplicate_capabilities,
    "CEL-INV-11": _duplicate_owners,
    "CEL-INV-12": _without_identifier,
}


@dataclass(frozen=True, slots=True)
class CriterionOutcome:
    """One acceptance criterion, resolved through the invariant that measures it."""

    criterion_id: str
    statement: str
    invariant_id: str
    satisfied: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "statement": self.statement,
            "invariant_id": self.invariant_id,
            "satisfied": self.satisfied,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class AcceptanceReport:
    """The enforcement layer's verdict over one population."""

    enforcement_id: str
    law_id: str
    measured: tuple[Measured, ...]
    criteria: tuple[CriterionOutcome, ...]
    scope: Mapping[str, Any]

    @property
    def blocking_failures(self) -> tuple[str, ...]:
        """Blocking invariants that measured above zero, or could not be measured."""
        blocking = {i.invariant_id for i in EXECUTION_INVARIANTS if i.blocking}
        return tuple(
            sorted(
                m.invariant_id
                for m in self.measured
                if m.invariant_id in blocking and not m.satisfied
            )
        )

    @property
    def unsatisfied_criteria(self) -> tuple[str, ...]:
        return tuple(c.criterion_id for c in self.criteria if not c.satisfied)

    @property
    def passed(self) -> bool:
        """True iff every blocking invariant measured zero and every criterion holds."""
        return not self.blocking_failures and not self.unsatisfied_criteria

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def measurement(self, invariant_id: str) -> Measured:
        for item in self.measured:
            if item.invariant_id == invariant_id:
                return item
        raise AcceptanceFailure(
            "no such measured invariant",
            enforcement_id=self.enforcement_id,
            invariant_id=invariant_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-acceptance",
            "version": ENFORCEMENT_VERSION,
            "enforcement_id": self.enforcement_id,
            "law_id": self.law_id,
            "status": self.status,
            "blocking_failures": list(self.blocking_failures),
            "unsatisfied_criteria": list(self.unsatisfied_criteria),
            "measurements": [m.to_dict() for m in self.measured],
            "criteria": [c.to_dict() for c in self.criteria],
            "scope": {k: self.scope[k] for k in sorted(self.scope)},
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def enforce(population: Population) -> AcceptanceReport:
    """Measure every invariant and resolve every acceptance criterion over ``population``."""
    view = View.of(population)

    measured: list[Measured] = []
    for invariant in EXECUTION_INVARIANTS:
        measurement = MEASUREMENTS.get(invariant.invariant_id)
        if measurement is None:
            measured.append(
                Measured(
                    invariant_id=invariant.invariant_id,
                    name=invariant.name,
                    count=1,
                    subjects=(),
                    measured=False,
                )
            )
            continue
        subjects = tuple(measurement(view))
        measured.append(
            Measured(
                invariant_id=invariant.invariant_id,
                name=invariant.name,
                count=len(subjects),
                subjects=subjects,
            )
        )

    by_id = {m.invariant_id: m for m in measured}
    criteria = tuple(
        CriterionOutcome(
            criterion_id=criterion.criterion_id,
            statement=criterion.statement,
            invariant_id=criterion.invariant_id,
            satisfied=by_id[criterion.invariant_id].satisfied
            if criterion.invariant_id in by_id
            else False,
            detail=(
                f"{by_id[criterion.invariant_id].name} = {by_id[criterion.invariant_id].count}"
                if criterion.invariant_id in by_id
                else f"no measurement for {criterion.invariant_id}"
            ),
        )
        for criterion in ACCEPTANCE_CRITERIA
    )

    return AcceptanceReport(
        enforcement_id=ENFORCEMENT_ID,
        law_id=LAW_ID,
        measured=tuple(measured),
        criteria=criteria,
        scope={
            "subjects": len(population),
            "population_digest": population.digest(),
            "plan_status": view.plan.status,
        },
    )


def gate(population: Population) -> AcceptanceReport:
    """Enforce and raise if any invariant or criterion fails — the fail-closed CI entry point.

    Raises:
        AcceptanceFailure: a blocking invariant measured above zero, could not be
            measured, or an acceptance criterion did not hold.
    """
    report = enforce(population)
    if not report.passed:
        raise AcceptanceFailure(
            "the constitutional enforcement gate failed",
            enforcement_id=ENFORCEMENT_ID,
            law_id=LAW_ID,
            blocking_failures=list(report.blocking_failures),
            unsatisfied_criteria=list(report.unsatisfied_criteria),
            measurements=[m.to_dict() for m in report.measured if not m.satisfied],
        )
    return report


def unmeasured_invariants() -> tuple[str, ...]:
    """Invariants the law declares that this layer cannot yet count, ordered.

    A self-check on the enforcement layer itself: a non-empty result means the law has
    grown past its enforcement, which is precisely the condition — rules present,
    enforcement absent — that this package exists to remove.
    """
    return tuple(
        sorted(i.invariant_id for i in EXECUTION_INVARIANTS if i.invariant_id not in MEASUREMENTS)
    )


def to_document() -> dict[str, Any]:
    """The enforcement layer's coverage as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-enforcement-layer",
        "version": ENFORCEMENT_VERSION,
        "enforcement_id": ENFORCEMENT_ID,
        "law_id": LAW_ID,
        "invariant_count": len(EXECUTION_INVARIANTS),
        "criterion_count": len(ACCEPTANCE_CRITERIA),
        "measured_invariants": sorted(MEASUREMENTS),
        "unmeasured_invariants": list(unmeasured_invariants()),
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "ENFORCEMENT_ID",
    "ENFORCEMENT_VERSION",
    "MEASUREMENTS",
    "AcceptanceReport",
    "CriterionOutcome",
    "Measured",
    "Measurement",
    "View",
    "digest",
    "enforce",
    "gate",
    "to_document",
    "unmeasured_invariants",
]
