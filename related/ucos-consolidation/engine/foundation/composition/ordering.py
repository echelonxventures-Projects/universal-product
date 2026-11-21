"""WP-UCDA-018 — the single ordering authority of UCOS Ω∞.

An execution order is **derived** from declarations. Nothing in this module holds a
workflow, a pipeline, or a predefined sequence of steps: a caller declares what each
element requires, and the order is computed from those declarations by a named,
registered, replaceable *strategy*. Declaring one more element changes the derived
order with no change to this module — which is the property a fixed pipeline cannot
have, and the reason a fixed pipeline is not permitted anywhere above this layer.

Why this lives in the foundation layer
--------------------------------------
It is the **one** ordering mechanism, and it has more than one lawful consumer:

    * :mod:`engine.civilization.composition` derives the order in which the
      capabilities of a generated constitutional operating system compose;
    * :mod:`engine.factory.phases` derives the order in which the generation runtime
      executes the phases of one artefact generation.

Both consumers sit *above* the foundation layer, so both depend downward: there is no
layer inversion, no import cycle, and — decisively — no second ordering mechanism to
drift from this one. ``DEC-MCOS-14`` recorded the defect that two ordering mechanisms
coexisted (a derived plan beside a hard-coded six-step sequence); ``WP-UCDA-018``
required that a single composition path remain reachable. This module is that path,
and the strategy registry below is shared, so a strategy registered by either consumer
is available to both.

Determinism
-----------
Every function here is pure and total over its inputs, ties are broken by sorting on
the key, and no wall-clock, RNG, filesystem or network is touched. An identical graph
therefore yields an identical order in every environment and at every commit.

Cycles
------
A declared graph may contain a cycle: requirements are declared by key, so an element
may name one that is not declared yet, and declarations are deliberately order
independent. Layering therefore stops at the acyclic frontier rather than inventing an
order, and :func:`unresolved_keys` reports exactly which keys no order could place.
Each consumer raises its own domain error over that report, so no error hierarchy is
duplicated here.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

#: A resolved dependency graph: element key -> the keys that element requires.
DependencyGraph = Mapping[str, "tuple[str, ...]"]

#: An ordering rule: given a resolved graph, return ``(wave, key)`` pairs in order.
#: A strategy MUST be pure and deterministic. It MAY return fewer pairs than the graph
#: has keys, which is how a cycle is reported rather than hidden.
CompositionStrategy = Callable[[DependencyGraph], "list[tuple[int, str]]"]

_STRATEGIES: dict[str, CompositionStrategy] = {}


# --------------------------------------------------------------------------- layering


def dependency_layers(graph: DependencyGraph) -> list[list[str]]:
    """Group keys into dependency layers; a key appears after everything it requires.

    Returns the layers discovered before progress stops. A graph containing a cycle
    yields layers covering only its acyclic part, which is how a cycle is detected
    rather than silently ordered.
    """
    remaining = {key: set(reqs) for key, reqs in graph.items()}
    layers: list[list[str]] = []
    placed: set[str] = set()
    while remaining:
        ready = sorted(key for key, reqs in remaining.items() if not (reqs - placed))
        if not ready:
            break
        layers.append(ready)
        placed.update(ready)
        for key in ready:
            del remaining[key]
    return layers


# --------------------------------------------------------------------------- strategies


def dependency_order(graph: DependencyGraph) -> list[tuple[int, str]]:
    """Total order: every element follows everything it requires, ties broken by key.

    Each step occupies its own wave, so the derived order is a strict sequence.
    """
    ordered = [key for layer in dependency_layers(graph) for key in layer]
    return [(index, key) for index, key in enumerate(ordered)]


def parallel_waves(graph: DependencyGraph) -> list[tuple[int, str]]:
    """Wave order: everything with satisfied requirements shares a wave.

    The same set and the same partial order as :func:`dependency_order`, expressed with
    the concurrency the declarations permit rather than with an imposed sequence.
    """
    return [
        (wave, key) for wave, layer in enumerate(dependency_layers(graph)) for key in sorted(layer)
    ]


def register_strategy(name: str, strategy: CompositionStrategy) -> None:
    """Register a named ordering strategy (unbounded extension).

    Raises :class:`ValueError` if the name is already registered: a strategy is an
    ordering *authority*, and silently replacing one would reintroduce exactly the
    ambiguity this module exists to remove.
    """
    if name in _STRATEGIES:
        raise ValueError(f"composition strategy already registered: {name!r}")
    _STRATEGIES[name] = strategy


def get_strategy(name: str) -> CompositionStrategy:
    """Return a registered ordering strategy by name.

    Raises :class:`KeyError` naming ``name`` when it is not registered. Consumers
    translate this into their own domain error, so this module declares no error
    hierarchy of its own.
    """
    try:
        return _STRATEGIES[name]
    except KeyError:
        raise KeyError(name) from None


def strategy_names() -> list[str]:
    """The names of every registered ordering strategy, sorted."""
    return sorted(_STRATEGIES)


#: The strategy used when a caller names none. It is looked up through the same registry
#: as any other, so it holds no privileged position in any consumer.
DEFAULT_STRATEGY = "dependency-order"
register_strategy(DEFAULT_STRATEGY, dependency_order)
register_strategy("parallel-waves", parallel_waves)


# --------------------------------------------------------------------------- derivation


def unresolved_keys(graph: DependencyGraph, ordering: list[tuple[int, str]]) -> list[str]:
    """The keys of ``graph`` that ``ordering`` did not place, sorted.

    Non-empty exactly when the declared graph contains a cycle, so a consumer can
    report *which* declarations could not be ordered instead of only that some failed.
    """
    return sorted(set(graph) - {key for _wave, key in ordering})


def derive_order(
    graph: DependencyGraph, *, strategy: str = DEFAULT_STRATEGY
) -> list[tuple[int, str]]:
    """Derive ``(wave, key)`` pairs for ``graph`` using the named strategy.

    The single act of derivation shared by every consumer. Cycle *reporting* is left to
    :func:`unresolved_keys` so each consumer raises its own domain error.
    """
    return get_strategy(strategy)(graph)


__all__ = [
    "DEFAULT_STRATEGY",
    "CompositionStrategy",
    "DependencyGraph",
    "dependency_layers",
    "dependency_order",
    "derive_order",
    "get_strategy",
    "parallel_waves",
    "register_strategy",
    "strategy_names",
    "unresolved_keys",
]
