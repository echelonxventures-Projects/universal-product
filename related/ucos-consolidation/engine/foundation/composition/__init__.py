"""Composition subpackage (WP-UCDA-018) — the single ordering authority.

Public API surface for deriving an execution order from declarations.
"""

from __future__ import annotations

from engine.foundation.composition.ordering import (
    DEFAULT_STRATEGY,
    CompositionStrategy,
    DependencyGraph,
    dependency_layers,
    dependency_order,
    derive_order,
    get_strategy,
    parallel_waves,
    register_strategy,
    strategy_names,
    unresolved_keys,
)

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
