"""URKE-000001 Part 03 — the state lattice and the seven independent axes.

Two separate things live here, and keeping them separate is the point.

The **lattice** is the declared knowledge states and the moves between them. It has no terminal
member and every declared state is reachable from the initial one, which the declaration enforces
structurally and law URKE-L-09 measures. A transition appends to the entity's state history; it
never rewrites it, so a subject that went from unknown to verified to refuted still says so.

The **axes** are the seven independent statuses every entity carries at once: whether it is held to
be, whether the repository can express it, whether it has been dispositioned, what measurement
says, whether it is fit for purpose, whether an authority attested to it, and whether it is relied
on. These are not seven points on one scale. Collapsing them into a single status would make "we can
write this down" and "we believe this" the same observable, and representation before understanding
would stop being expressible — which is the one thing this capability exists to make possible.

:data:`OWNER_READERS` reads the vocabularies this capability binds to *from their owners*, live. A
copy of somebody else's vocabulary would be a second authority over it and would drift silently the
first time the owner changed; reading it means a binding that has gone stale is a measured refusal.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from engine.recursive_knowledge.declaration import Declaration
from engine.recursive_knowledge.model import (
    GovernedEntity,
    RecursiveKnowledgeError,
    StateTransition,
)

#: The population name the declared UKDA binding uses. Read from the declaration by the law that
#: checks the binding; named here because a reader must return the key its binding names.
UKDA_POPULATION = "lifecycle"


class StateError(RecursiveKnowledgeError):
    """The state, transition or axis value is not one the declaration allows. A fault."""


# --- reading other people's vocabularies, live --------------------------------------------


def ceu_populations() -> Mapping[str, frozenset[str]]:
    """The existence-universe populations, read from their owner rather than copied."""
    try:
        from engine.ceu.catalog import SEED_POPULATIONS
    except ImportError as exc:  # pragma: no cover - a missing owner is a fault, not a verdict
        raise StateError(f"the existence vocabulary owner cannot be read: {exc}") from exc
    return MappingProxyType(
        {str(name): frozenset(str(row[0]) for row in rows) for name, rows in SEED_POPULATIONS}
    )


def ukda_lifecycle() -> Mapping[str, frozenset[str]]:
    """The knowledge-object lifecycle stages, read from their owner rather than copied."""
    try:
        from engine.knowledge.model import Lifecycle
    except ImportError as exc:  # pragma: no cover - a missing owner is a fault, not a verdict
        raise StateError(f"the lifecycle vocabulary owner cannot be read: {exc}") from exc
    return MappingProxyType({UKDA_POPULATION: frozenset(member.value for member in Lifecycle)})


#: Each declared binding owner, mapped to the function that reads its live vocabulary. Bound in both
#: directions at load time, so an owner nothing can read is refused rather than silently unchecked.
OWNER_READERS: Mapping[str, Callable[[], Mapping[str, frozenset[str]]]] = MappingProxyType(
    {"ceu_populations": ceu_populations, "ukda_lifecycle": ukda_lifecycle}
)


def available_owner_readers() -> frozenset[str]:
    """The owner readers this module implements."""
    return frozenset(OWNER_READERS)


def live_vocabulary(declaration: Declaration) -> Mapping[str, Mapping[str, frozenset[str]]]:
    """Every bound owner's live vocabulary, keyed by owner then population."""
    live: dict[str, Mapping[str, frozenset[str]]] = {}
    for owner in declaration.binding_owners:
        reader = OWNER_READERS.get(owner.reader)
        if reader is None:
            raise StateError(
                f"binding owner {owner.owner!r} names reader {owner.reader!r}, which nothing "
                "implements"
            )
        live[owner.owner] = reader()
    return MappingProxyType(live)


def binding_problems(declaration: Declaration) -> list[str]:
    """Every binding that names a row its owner does not carry, or discloses no gap in its place.

    Returned rather than raised: a stale binding is a finding a law reports, not a fault that stops
    the measurement. The two directions of the check are different failures — a binding to a row
    that has gone away is drift, and a state that binds to nothing and discloses nothing is a
    vocabulary held in secret.
    """
    problems: list[str] = []
    live = live_vocabulary(declaration)
    required_classes = {
        spec.state_class for spec in declaration.state_classes if spec.binding_required
    }
    for spec in declaration.states:
        if spec.binding is None:
            gap = spec.binding_gap or {}
            for field_name in ("gap_id", "finding", "referred_to", "remediation"):
                if not str(gap.get(field_name) or "").strip():
                    problems.append(
                        f"state {spec.identifier!r} binds to no vocabulary owner and its gap "
                        f"discloses no {field_name}"
                    )
            if spec.state_class in required_classes and not gap:
                problems.append(
                    f"state {spec.identifier!r} is of a class whose members must bind, and it "
                    "neither binds nor discloses"
                )
            continue
        owner = str(spec.binding.get("owner") or "")
        population = str(spec.binding.get("population") or "")
        member = str(spec.binding.get("member") or "")
        carried = live.get(owner)
        if carried is None:
            problems.append(
                f"state {spec.identifier!r} binds to owner {owner!r}, which nothing reads"
            )
        elif population not in carried:
            problems.append(
                f"state {spec.identifier!r} binds to {owner}/{population}, which {owner} does not "
                "declare"
            )
        elif member not in carried[population]:
            problems.append(
                f"state {spec.identifier!r} binds to {owner}/{population}/{member}, which {owner} "
                "does not carry"
            )
    ours = {identifier.lower().replace("_", "-") for identifier in declaration.state_ids}
    for owner, populations in sorted(live.items()):
        for population, members in sorted(populations.items()):
            if members and members <= ours:
                problems.append(
                    f"the state vocabulary contains the whole of {owner}/{population}, so it is a "
                    "copy rather than a binding"
                )
    return problems


# --- the lattice --------------------------------------------------------------------------


def successors(declaration: Declaration, state: str) -> frozenset[str]:
    """The states reachable in one move from ``state``."""
    return frozenset(declaration.state(state).successors)


def reachable_from(declaration: Declaration, start: str) -> frozenset[str]:
    """Every state reachable from ``start`` in any number of moves."""
    declaration.state(start)
    seen: set[str] = set()
    frontier = [start]
    while frontier:
        for candidate in successors(declaration, frontier.pop()):
            if candidate not in seen:
                seen.add(candidate)
                frontier.append(candidate)
    return frozenset(seen)


def terminal_states(declaration: Declaration) -> tuple[str, ...]:
    """Declared states from which nothing is reachable. Expected to be empty, measured not "
    "assumed."""
    return tuple(
        spec.identifier for spec in declaration.states if not spec.successors or spec.terminal
    )


def settled(declaration: Declaration, state: str) -> bool:
    """True when no discovery workflow is owed for a subject in this state.

    Settled is not terminal. Both declared settled states name successors, so a settled subject can
    be reopened — which is why closure here never means "stopped being looked at".
    """
    document_settled = _settled_ids(declaration)
    return state in document_settled


def _settled_ids(declaration: Declaration) -> frozenset[str]:
    return frozenset(declaration.settled_states)


def eligible_for_discovery(declaration: Declaration, entity: GovernedEntity) -> bool:
    """True when the entity's state is unresolved, computed from the lattice rather than its class.

    Eligibility deliberately ignores the entity class. A rule that named the classes discovery
    applies to would be a list somebody forgets to extend, and the class left off the list would be
    the one nothing ever looked at again.
    """
    return not settled(declaration, entity.state)


def transition(
    declaration: Declaration,
    entity: GovernedEntity,
    to_state: str,
    *,
    basis: str,
    actor: str,
    sequence: int,
) -> GovernedEntity:
    """Move an entity to ``to_state``, appending to its history. Nothing earlier is altered.

    Refuses an undeclared state, and refuses a move the lattice does not permit. Both refusals are
    faults rather than silent no-ops: a transition that quietly did nothing would leave the caller
    believing a subject had advanced.
    """
    spec = declaration.state(to_state)
    current = entity.state
    if current and to_state not in successors(declaration, current):
        raise StateError(
            f"the lattice permits no move from {current!r} to {spec.identifier!r}; declared "
            f"successors are {', '.join(sorted(successors(declaration, current)))}"
        )
    history = entity.state_history + (
        StateTransition(
            from_state=current,
            to_state=spec.identifier,
            basis=basis,
            actor=actor,
            sequence=sequence,
        ),
    )
    return _replace(entity, state=spec.identifier, state_history=history)


def _replace(entity: GovernedEntity, **changes: Any) -> GovernedEntity:
    from dataclasses import replace

    return replace(entity, **changes)


# --- the seven axes -----------------------------------------------------------------------


def axis_initial(declaration: Declaration) -> Mapping[str, str]:
    """The declared starting value of every axis. Never a default invented here."""
    return MappingProxyType({spec.axis: spec.initial for spec in declaration.lifecycle_axes})


def axis_values(declaration: Declaration, axis: str) -> tuple[str, ...]:
    """The declared values an axis may take."""
    for spec in declaration.lifecycle_axes:
        if spec.axis == axis:
            return spec.values
    raise StateError(f"{axis!r} is not a declared lifecycle axis")


def with_axis(
    declaration: Declaration, entity: GovernedEntity, axis: str, value: str
) -> GovernedEntity:
    """Set one axis, leaving every other axis exactly as it was.

    The independence law measures precisely this: that moving one axis moves no other. It is easy to
    write a status setter that derives verification from admission for convenience, and that
    convenience is what makes "admitted" start meaning "true".
    """
    permitted = axis_values(declaration, axis)
    if value not in permitted:
        raise StateError(
            f"{value!r} is not a declared value of axis {axis!r}; declared values are "
            f"{', '.join(permitted)}"
        )
    axes = dict(entity.axes)
    axes[axis] = value
    return _replace(entity, axes=axes)


def axis_combinations(declaration: Declaration) -> tuple[Mapping[str, str], ...]:
    """The whole cross-product of declared axis values, in deterministic order.

    Realised in full by law URKE-L-33 rather than sampled, because independence is a claim about
    every combination and a sample would only show that the common ones work.
    """
    combinations: list[dict[str, str]] = [{}]
    for spec in sorted(declaration.lifecycle_axes, key=lambda item: item.axis):
        grown: list[dict[str, str]] = []
        for partial in combinations:
            for value in spec.values:
                extended = dict(partial)
                extended[spec.axis] = value
                grown.append(extended)
        combinations = grown
    return tuple(MappingProxyType(item) for item in combinations)


__all__ = [
    "OWNER_READERS",
    "StateError",
    "available_owner_readers",
    "axis_combinations",
    "axis_initial",
    "axis_values",
    "binding_problems",
    "ceu_populations",
    "eligible_for_discovery",
    "live_vocabulary",
    "reachable_from",
    "settled",
    "successors",
    "terminal_states",
    "transition",
    "ukda_lifecycle",
    "with_axis",
]
