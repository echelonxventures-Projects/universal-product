"""EPIC-RTE-002 — Execution Federation (Runtime Execution Platform).

Realises **Execution Federation**: the execution-time view of the explicit,
cross-context ENG-005 Federation References that already authorise cross-boundary
dependencies in a :class:`~engine.runtime.composition.RuntimeComposition`
(RUNTIME-013 ORL-12; §D10 Federation).

This module **reuses the composition's already-validated federations and reference
frames verbatim** (:class:`~engine.runtime.context.Federation` /
:class:`~engine.runtime.context.ReferenceFrame`, EPIC-006) — it validates no new
federation and adds no federation logic. It projects them into an execution-time
federation view and, given an isolation view, re-affirms deterministically that
every cross-partition execution dependency is covered by exactly one federation. A
*structure only*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.errors import ExecutionFederationError

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition
    from engine.runtime.execution.isolation import IsolationView

_logger = get_logger("runtime.execution.federation")

#: The recorded federation format.
FEDERATION_FORMAT = "ucos-execution-federation/1.0.0"


@dataclass(frozen=True, slots=True)
class FederatedLink:
    """One execution-time cross-context federation link (``source → target``)."""

    source: str
    target: str

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "target": self.target}


@dataclass(frozen=True, slots=True)
class FederationView:
    """The full, deterministic federation view of a composition's execution."""

    composition_id: str
    links: tuple[FederatedLink, ...]

    def targets_of(self, source: str) -> tuple[str, ...]:
        """The federated targets reachable from ``source`` (sorted)."""
        return tuple(sorted(link.target for link in self.links if link.source == source))

    def is_federated(self, source: str, target: str) -> bool:
        """True iff an explicit federation authorises ``source → target``."""
        return any(link.source == source and link.target == target for link in self.links)

    def to_dict(self) -> dict[str, Any]:
        return {
            "federation_format": FEDERATION_FORMAT,
            "composition_id": self.composition_id,
            "link_count": len(self.links),
            "links": [link.to_dict() for link in self.links],
        }


def federate(composition: RuntimeComposition) -> FederationView:
    """Project the composition's resolved federations into an execution view.

    Reuses :attr:`RuntimeComposition.federations` verbatim (sorted deterministically
    at composition time). Adds no validation — the composition already refused
    dangling, same-context, and duplicate federations (ORL-12).
    """
    with trace("runtime.execution.federate", composition=composition.composition_id):
        links = tuple(
            FederatedLink(source=f.source, target=f.target) for f in composition.federations
        )
        view = FederationView(composition_id=composition.composition_id, links=links)
    _logger.info(
        "runtime.execution.federated",
        composition_id=composition.composition_id,
        links=len(links),
    )
    return view


def assert_federated(
    composition: RuntimeComposition,
    isolation: IsolationView,
    federation: FederationView,
) -> None:
    """Re-affirm that every cross-partition dependency is explicitly federated.

    Raises:
        ExecutionFederationError: if a dependency crosses partitions with no
            authorising federation link (a defensive re-check of ORL-12).
    """
    for universe in composition.universes:
        context_id = isolation.context_of(universe.universe_id)
        for dependency in universe.depends_on:
            if isolation.context_of(dependency) == context_id:
                continue
            if not federation.is_federated(universe.universe_id, dependency):
                raise ExecutionFederationError(
                    "cross-context execution dependency lacks a federation link",
                    universe_id=universe.universe_id,
                    dependency=dependency,
                )


__all__ = [
    "FEDERATION_FORMAT",
    "FederatedLink",
    "FederationView",
    "federate",
    "assert_federated",
]
