"""Universal Provider Selection — an open registry of selection strategies.

Selection is the mechanism by which one provider is chosen among several candidates that
all satisfy a request. It is deliberately **open**: a strategy is a named, pure function,
and new strategies are registered — there is no closed set of selection policies.

A strategy takes the candidate providers (kernel meta-objects) and the caller's
requirements, and returns them in preference order (best first). It must be deterministic.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from engine.foundation.contracts.contract import Version
from engine.kernel.meta import MetaObject

#: A selection strategy: given candidates + requirements, return them best-first.
SelectionStrategy = Callable[[Sequence[MetaObject], Mapping[str, Any]], "list[MetaObject]"]

_STRATEGIES: dict[str, SelectionStrategy] = {}


def _contract_version(provider: MetaObject) -> Version:
    """The provider's declared contract version, or 0.0.0 when absent/malformed."""
    contract = provider.attributes.get("contract") or {}
    raw = contract.get("version") if isinstance(contract, Mapping) else None
    try:
        return Version.parse(str(raw)) if raw is not None else Version(0, 0, 0)
    except Exception:  # noqa: BLE001 — a malformed version sorts lowest, never crashes selection
        return Version(0, 0, 0)


def _is_serving(provider: MetaObject) -> bool:
    """True unless the provider's advertised health status is explicitly unavailable.

    Health status is an open string, so this asks only the one question selection needs —
    *may this provider serve?* — without enumerating a closed set of health states.
    """
    health = provider.attributes.get("health") or {}
    status = str(health.get("status", "")).lower() if isinstance(health, Mapping) else ""
    return status != "unavailable"


def highest_version(
    candidates: Sequence[MetaObject], requirements: Mapping[str, Any]
) -> list[MetaObject]:
    """Default strategy: serving providers first, then highest contract version, then id.

    Deterministic and total: every candidate is returned exactly once in a stable order.
    """
    return sorted(
        candidates,
        key=lambda p: (
            0 if _is_serving(p) else 1,
            _reverse_version_key(_contract_version(p)),
            p.identity,
        ),
    )


def _reverse_version_key(version: Version) -> tuple[int, int, int]:
    """A sort key that orders higher versions first while remaining totally ordered."""
    return (-version.major, -version.minor, -version.patch)


def register_strategy(name: str, strategy: SelectionStrategy) -> None:
    """Register a named selection strategy (unbounded extension)."""
    if name in _STRATEGIES:
        raise ValueError(f"selection strategy already registered: {name!r}")
    _STRATEGIES[name] = strategy


def get_strategy(name: str) -> SelectionStrategy:
    """Return a registered selection strategy by name."""
    return _STRATEGIES[name]


def strategy_names() -> list[str]:
    """The names of every registered selection strategy, sorted."""
    return sorted(_STRATEGIES)


#: The default strategy is registered under a stable name so callers may request it.
DEFAULT_STRATEGY = "highest-version"
register_strategy(DEFAULT_STRATEGY, highest_version)


__all__ = [
    "SelectionStrategy",
    "highest_version",
    "register_strategy",
    "get_strategy",
    "strategy_names",
    "DEFAULT_STRATEGY",
]
