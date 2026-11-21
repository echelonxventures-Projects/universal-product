"""UCOS-EPIC-010 (Terminal T2) — Semantic Reachability.

Answers *"can I get from artifact A to artifact B, and if so how, following only a
given kind of meaning?"* over the certified Universal Knowledge Graph (read-only,
DP-03).

Unlike raw graph reachability, semantic reachability constrains traversal to a
named **relation family** — a curated set of edge types that share a meaning
(structural dependency, capability provision, traceability, requirement demand) —
so a "reachable" answer is semantically interpretable rather than an accident of
mixing unrelated edge kinds. Each family can be traversed forward or backward.

Every query is deterministic (sorted traversal, deterministic shortest path) and
never mutates the corpus.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.graph.architecture.errors import ReachabilityError
from engine.graph.engine import (
    AUTHORIZES,
    CHILD,
    CONSUMES,
    DEPENDS_ON,
    EVOLVES_FROM,
    IMPLEMENTS,
    PARENT,
    REQUIRED_BY,
    TRACES_TO,
)
from engine.graph.model import KnowledgeGraph
from engine.graph.queries import shortest_path, transitive_closure

#: Named semantic relation families → the edge types they traverse (forward sense).
RELATION_FAMILIES: dict[str, tuple[str, ...]] = {
    "dependency": (DEPENDS_ON,),
    "capability": (CONSUMES,),
    "structural": (PARENT, CHILD),
    "traceability": (IMPLEMENTS, TRACES_TO, EVOLVES_FROM, AUTHORIZES),
    "requirement": (REQUIRED_BY,),
}


@dataclass(frozen=True, slots=True)
class ReachabilityResult:
    """The deterministic outcome of a semantic reachability query."""

    source: str
    family: str
    inbound: bool
    reachable: tuple[str, ...]

    @property
    def count(self) -> int:
        return len(self.reachable)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "family": self.family,
            "inbound": self.inbound,
            "count": self.count,
            "reachable": list(self.reachable),
        }


class SemanticReachability:
    """Read-only semantic reachability over curated relation families."""

    __slots__ = ("_core",)

    def __init__(self, core: KnowledgeGraph) -> None:
        self._core = core

    @staticmethod
    def families() -> tuple[str, ...]:
        """The names of the supported semantic relation families (ordered)."""
        return tuple(sorted(RELATION_FAMILIES))

    def _types(self, family: str) -> tuple[str, ...]:
        try:
            return RELATION_FAMILIES[family]
        except KeyError as exc:
            raise ReachabilityError(
                "unknown semantic relation family",
                family=family,
                known=tuple(sorted(RELATION_FAMILIES)),
            ) from exc

    def _require_node(self, node_id: str) -> None:
        if not self._core.has_node(node_id):
            raise ReachabilityError("node not present in the graph", node_id=node_id)

    def reachable(self, source: str, family: str, *, inbound: bool = False) -> ReachabilityResult:
        """Everything semantically reachable from ``source`` within ``family``.

        With ``inbound=True`` the family is traversed in reverse (who can reach
        ``source``). The reachable set is sorted and excludes ``source`` itself.
        """
        self._require_node(source)
        types = self._types(family)
        closure = transitive_closure(self._core, source, inbound=inbound, types=types)
        return ReachabilityResult(
            source=source,
            family=family,
            inbound=inbound,
            reachable=tuple(sorted(closure)),
        )

    def can_reach(self, source: str, target: str, family: str, *, inbound: bool = False) -> bool:
        """True iff ``target`` is semantically reachable from ``source`` in ``family``."""
        return bool(self.path(source, target, family, inbound=inbound))

    def path(
        self, source: str, target: str, family: str, *, inbound: bool = False
    ) -> tuple[str, ...]:
        """A deterministic shortest semantic path ``source -> ... -> target``.

        Returns an empty tuple if ``target`` is unreachable from ``source`` within the
        family. Both endpoints must exist in the graph.
        """
        self._require_node(source)
        self._require_node(target)
        types = self._types(family)
        return shortest_path(self._core, source, target, inbound=inbound, types=types)

    def summary(self, source: str) -> dict[str, Any]:
        """Per-family forward reachability counts from ``source`` (deterministic)."""
        self._require_node(source)
        return {
            "source": source,
            "families": {
                family: self.reachable(source, family).count for family in self.families()
            },
        }


__all__ = ["RELATION_FAMILIES", "ReachabilityResult", "SemanticReachability"]
