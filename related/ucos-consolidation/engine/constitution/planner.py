"""UCOS-CEP-EXEC-000001 — the Constitutional Execution Planner (Requirement 002).

The planner turns a population into the one order it is lawful to execute in. It computes
the six closures Requirement 002 names — dependency, governance, authority, certification,
registration, evolution — proves legality over every subject, and derives the order from
the merged graph through the single ordering authority.

Why ``plan()`` has no ``order`` parameter
-----------------------------------------
CEL-02 is not enforceable by asking callers not to sequence. It is enforceable by there
being no argument through which a sequence could arrive. :func:`plan` therefore takes the
population and a *named strategy* — never an order, an order hint, a priority, a
"run this first", or a partial constraint. Any unexpected keyword is refused as
:class:`~engine.constitution.errors.ManualSequencing` rather than ignored, because a
silently-ignored ``order=`` reads to the caller as an honoured one.

A strategy is not a sequence: it is a registered, replaceable *rule* for deriving one from
the declarations, and it lives in :mod:`engine.foundation.composition.ordering` with every
other consumer's. Choosing ``parallel-waves`` over ``dependency-order`` changes how much
concurrency the derived order expresses; it cannot change what depends on what.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.constitution import authority as authority_graph
from engine.constitution import dependency as dependency_graph
from engine.constitution import legality as legality_engine
from engine.constitution.dependency import DependencyGraph
from engine.constitution.errors import IllegalExecution, ManualSequencing
from engine.constitution.metadata import Population
from engine.foundation.composition.ordering import (
    DEFAULT_STRATEGY,
    derive_order,
    unresolved_keys,
)
from engine.uckp.canonical import content_hash

#: The identity of the execution planner this module realises.
PLANNER_ID = "UCOS-CEP-EXEC-000001"

#: Versioned so closures can be *added* without any prior plan changing meaning.
PLANNER_VERSION = "1.0.0"

#: The relations that constrain *execution order*: a subject cannot run before what it
#: requires, nor before the owner that owns it.
#:
#: Certification, governance and validation relations are deliberately absent, and the
#: reason matters. A subject is certified *by* an independent authority, and that authority
#: routinely depends on the subject it certifies — the enforcement layer certifies the
#: metadata mandate and is built on it. Both directions are correct, and merging them into
#: one ordering would report a cycle that does not exist: certification is not a
#: prerequisite of execution, it is a judgement passed on it.
#:
#: Those relations are not unchecked. Each is required to be acyclic *in its own right* by
#: :meth:`~engine.constitution.dependency.DependencyGraph.require_acyclic` and by the
#: authority gate, and each closure below is still computed and reported. What they do not
#: do is dictate what runs first.
ORDERING_RELATIONS: tuple[str, ...] = ("dependencies", "canonical_owner")

#: The six closures Requirement 002 requires a plan to calculate, and the relations each
#: is computed over. DATA — a seventh closure is one appended entry.
CLOSURES: Mapping[str, tuple[str, ...]] = {
    "dependency": ("dependencies",),
    "governance": ("governance_rules",),
    "authority": ("authorities", "canonical_owner"),
    "certification": ("certifications",),
    "registration": ("registrations",),
    "evolution": ("dependencies", "authorities", "certifications", "registrations"),
}


@dataclass(frozen=True, slots=True)
class ExecutionStep:
    """One subject placed in the derived order, with the closure it waits on."""

    wave: int
    subject: str
    requires: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"wave": self.wave, "subject": self.subject, "requires": list(self.requires)}


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """A derived, legal, replayable execution order over one population."""

    planner_id: str
    strategy: str
    steps: tuple[ExecutionStep, ...]
    unplaceable: tuple[str, ...]
    legality: legality_engine.LegalityReport
    authority: authority_graph.AuthorityReport
    graph: DependencyGraph
    relations: tuple[str, ...]
    ordering_relations: tuple[str, ...] = ORDERING_RELATIONS

    @property
    def cyclic_relations(self) -> dict[str, tuple[str, ...]]:
        """Every relation that closes a loop, ordered — including ones not ordered on.

        A cycle in a relation the order ignores is still a constitutional defect: a
        governance rule set that governs itself in a ring answers to nobody. Ordering
        cannot detect it, so the plan measures it directly.
        """
        return {
            relation: found
            for relation in self.graph.relations
            if (found := self.graph.cycles(relation))
        }

    @property
    def order(self) -> tuple[str, ...]:
        """The derived execution order, as subject keys."""
        return tuple(step.subject for step in self.steps)

    @property
    def waves(self) -> tuple[tuple[str, ...], ...]:
        """The order grouped by wave — what may run concurrently, as declared."""
        grouped: dict[int, list[str]] = {}
        for step in self.steps:
            grouped.setdefault(step.wave, []).append(step.subject)
        return tuple(tuple(sorted(grouped[wave])) for wave in sorted(grouped))

    @property
    def executable(self) -> bool:
        """True iff every subject was placed, proved legal, and the authority gate passed."""
        return (
            not self.unplaceable
            and self.legality.passed
            and self.authority.passed
            and not self.cyclic_relations
            and not self.graph.unknown_referents()
        )

    @property
    def status(self) -> str:
        return "EXECUTABLE" if self.executable else "REFUSED"

    @property
    def refusals(self) -> tuple[str, ...]:
        """Why the plan is not executable, ordered — empty when it is."""
        reasons: list[str] = []
        if self.graph.unknown_referents():
            reasons.append("graph names unregistered subjects")
        if self.unplaceable:
            reasons.append(f"unplaceable subjects: {', '.join(self.unplaceable)}")
        for relation, subjects in sorted(self.cyclic_relations.items()):
            reasons.append(f"cycle in {relation}: {', '.join(subjects)}")
        if not self.authority.passed:
            reasons.append(f"authority breaches: {len(self.authority.findings)}")
        if not self.legality.passed:
            reasons.append(f"illegal subjects: {len(self.legality.illegal)}")
        return tuple(reasons)

    def closure(self, subject: str, name: str) -> tuple[str, ...]:
        """One named closure of one subject — e.g. ``closure("x", "governance")``."""
        relations = CLOSURES.get(name)
        if relations is None:
            raise ManualSequencing(
                "no such closure",
                closure=name,
                allowed=sorted(CLOSURES),
            )
        return self.graph.closure(
            subject, relations=[r for r in relations if r in self.graph.relations]
        )

    def closures(self, subject: str) -> dict[str, tuple[str, ...]]:
        """Every declared closure of one subject."""
        return {name: self.closure(subject, name) for name in sorted(CLOSURES)}

    def position(self, subject: str) -> int:
        """The subject's index in the derived order, or ``-1`` when it was not placed."""
        for index, step in enumerate(self.steps):
            if step.subject == subject:
                return index
        return -1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-execution-plan",
            "version": PLANNER_VERSION,
            "planner_id": self.planner_id,
            "status": self.status,
            "strategy": self.strategy,
            "relations": list(self.relations),
            "ordering_relations": list(self.ordering_relations),
            "cyclic_relations": {k: list(v) for k, v in sorted(self.cyclic_relations.items())},
            "refusals": list(self.refusals),
            "order": list(self.order),
            "waves": [list(wave) for wave in self.waves],
            "steps": [step.to_dict() for step in self.steps],
            "unplaceable": list(self.unplaceable),
            "closures": {
                subject: {
                    name: list(targets) for name, targets in sorted(self.closures(subject).items())
                }
                for subject in self.order
            },
            "legality": self.legality.to_dict(),
            "authority": self.authority.to_dict(),
            "graph_digest": self.graph.digest(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def plan(
    population: Population,
    *,
    strategy: str = DEFAULT_STRATEGY,
    relations: Sequence[str] | None = None,
    **forbidden: Any,
) -> ExecutionPlan:
    """Derive the legal execution order of ``population``.

    Args:
        population: the declared subjects. The only input to the derivation.
        strategy: the *name* of a registered ordering rule. Not an order.
        relations: which relations constrain the order — see :data:`ORDERING_RELATIONS`
            for why this is a subset rather than every relation. The *graph* is always
            built over every graph-bearing facet, so every closure remains computable
            whatever is ordered on.

    Raises:
        ManualSequencing: any other keyword was supplied. There is no argument by which a
            caller may sequence, hint at, prioritise or partially constrain the order.
    """
    if forbidden:
        raise ManualSequencing(
            "execution order is derived, never supplied; refused unexpected arguments",
            planner_id=PLANNER_ID,
            supplied=sorted(forbidden),
            clause="CEL-02",
        )
    graph = dependency_graph.build(population)
    authority_report = authority_graph.analyse(population, graph)
    legality_report = legality_engine.assess(population, graph)

    ordering_relations = tuple(relations) if relations is not None else ORDERING_RELATIONS
    merged = graph.merged_graph([r for r in ordering_relations if r in graph.relations])
    ordering = derive_order(merged, strategy=strategy)
    unplaceable = tuple(unresolved_keys(merged, ordering))

    steps = tuple(
        ExecutionStep(wave=wave, subject=subject, requires=merged.get(subject, ()))
        for wave, subject in ordering
    )
    return ExecutionPlan(
        planner_id=PLANNER_ID,
        strategy=strategy,
        steps=steps,
        unplaceable=unplaceable,
        legality=legality_report,
        authority=authority_report,
        graph=graph,
        relations=graph.relations,
        ordering_relations=ordering_relations,
    )


def require_executable(
    population: Population,
    *,
    strategy: str = DEFAULT_STRATEGY,
    relations: Sequence[str] | None = None,
) -> ExecutionPlan:
    """Derive the plan and refuse it unless every subject may lawfully execute.

    The fail-closed entry point. A plan that is merely *derivable* is a report; a plan
    that is executable has proven that nothing in it can execute out of order, skip a
    dependency, bypass governance or certify itself.

    Raises:
        IllegalExecution: the plan is not executable; the refusals are named.
    """
    derived = plan(population, strategy=strategy, relations=relations)
    if not derived.executable:
        raise IllegalExecution(
            "execution plan refused: the population has not proven it may execute",
            planner_id=PLANNER_ID,
            refusals=list(derived.refusals),
            unplaceable=list(derived.unplaceable),
            illegal=[v.subject for v in derived.legality.illegal],
            authority_findings=[f.to_dict() for f in derived.authority.findings],
        )
    return derived


def to_document() -> dict[str, Any]:
    """The planner's closure model as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-execution-planner",
        "version": PLANNER_VERSION,
        "planner_id": PLANNER_ID,
        "closures": {name: list(relations) for name, relations in sorted(CLOSURES.items())},
        "ordering_relations": list(ORDERING_RELATIONS),
        "manual_sequencing": "prohibited",
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "CLOSURES",
    "ORDERING_RELATIONS",
    "PLANNER_ID",
    "PLANNER_VERSION",
    "ExecutionPlan",
    "ExecutionStep",
    "digest",
    "plan",
    "require_executable",
    "to_document",
]
