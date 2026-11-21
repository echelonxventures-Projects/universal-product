"""TASK-000039 — Runtime Context + Reference Frame Resolution (EPIC-006).

Realises **context resolution** and **reference frame resolution** for the
Universal Runtime Composition Engine (RUNTIME-013 §D14 Orchestration↔Context; §D10
Federation). Every composed universe is **bounded** by exactly one runtime context
(ORL-05/ORL-14), and every cross-context reference is authorised **only** by an
explicit, collision-free **federation reference** (ORL-12; ENG-005 Federation
References). Context isolation is preserved: no dependency may cross a context
boundary implicitly (ORL-13).

Two resolutions are provided, both pure and deterministic:

    * :func:`resolve_contexts` — groups the bound universes into their
      :class:`RuntimeContext` partitions, refusing any unbounded universe (ORL-14).
    * :func:`resolve_reference_frames` — computes, per universe, the
      :class:`ReferenceFrame` of universes it may reference (same-context peers plus
      federated targets) and **fails closed** on any isolation leak: a dependency
      edge that crosses contexts without a matching federation reference is refused
      (ORL-13), a federation whose endpoints share a context is refused (a
      federation is cross-context by definition, ORL-12), a dangling federation
      endpoint is refused, and a duplicate federation is refused (collision-free).

This module consumes a :class:`~engine.runtime.graph.RuntimeGraph` and a
``universe_id -> context_id`` binding; it holds no ``RuntimeUnit`` and sits below
:mod:`engine.runtime.composition`. It resolves scope and references only — it
executes nothing and confers no authority (ORL-15/ORL-22).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from engine.compiler.partition import (
    Federation,
    IsolationError,
    UnboundedMemberError,
)
from engine.compiler.partition import (
    Frame as ReferenceFrame,
)
from engine.compiler.partition import (
    Partition as RuntimeContext,
)
from engine.compiler.partition import (
    resolve_frames as _resolve_frames,
)
from engine.compiler.partition import (
    resolve_partitions as _resolve_partitions,
)
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.errors import ContextResolutionError, ReferenceFrameError
from engine.runtime.graph import RuntimeGraph

_logger = get_logger("runtime.context")

#: The default bounding context bound when a universe declares none.
DEFAULT_CONTEXT = "runtime"


# --------------------------------------------------------------------------- #
# Value types                                                                  #
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# Bounded scope and reference frames — OWNED BY engine.context, imported here   #
# --------------------------------------------------------------------------- #
#
# These types and both resolutions used to be DEFINED here, and engine.context.
# composition imported them upward. That single import closed the CYC-ARCHITECTURAL
# cycle RIB GATE-10 refuses:
#
#   engine.runtime -> engine.knowledge -> engine.context -> engine.runtime
#
# Boundedness and isolation are UCXI-000001's declared guarantees (CXL-03, CXL-04), so
# the context layer owns the concept and this layer consumes it. The definitions moved
# to engine/context/composition.py unchanged in behaviour; they are re-exported here
# under their runtime names so every existing caller of engine.runtime.context is
# untouched. The runtime still owns its graph, its errors and its universe semantics.


def resolve_contexts(bindings: Mapping[str, str]) -> tuple[RuntimeContext, ...]:
    """Group bound universes into their context partitions (ORL-05/ORL-14).

    The rule is the context layer's; the ERROR TAXONOMY is this layer's. A caller of the
    runtime keeps catching runtime errors, so inverting the dependency changed no
    contract — only which layer states the rule.
    """
    with trace("runtime.context.resolve", universes=len(bindings)):
        try:
            contexts = _resolve_partitions(bindings)
        except UnboundedMemberError as exc:
            raise ContextResolutionError(
                "universe is not bound to a context (unbounded orchestration)",
                detail=str(exc),
            ) from exc
    _logger.info("runtime.context.resolved", contexts=len(contexts))
    return contexts


def resolve_reference_frames(
    bindings: Mapping[str, str],
    graph: RuntimeGraph,
    federations: Iterable[Federation] = (),
) -> tuple[ReferenceFrame, ...]:
    """Resolve each universe's reference frame and enforce isolation (ORL-12/13).

    The runtime supplies its graph; the rule itself belongs to the context layer.
    """
    with trace("runtime.context.frames", universes=graph.count()):
        try:
            frames = _resolve_frames(bindings, graph.nodes(), graph.dependencies_of, federations)
        except IsolationError as exc:
            # VOCABULARY TRANSLATION, not just a type change. The shared rule speaks of
            # partitions; this layer's declared contract speaks of contexts and reports an
            # "isolation leak", and callers assert on that wording. A boundary that keeps
            # the type and drops the vocabulary would still break the contract.
            raise ReferenceFrameError(
                str(exc)
                .replace(
                    "cross-partition dependency without a federation",
                    "cross-context dependency without a federation reference "
                    "(context isolation leak)",
                )
                .replace(
                    "federation endpoints share a partition",
                    "federation endpoints share a context (federation is cross-context)",
                )
                .replace("partition", "context")
            ) from exc
        except UnboundedMemberError as exc:
            raise ContextResolutionError(str(exc)) from exc
    _logger.info("runtime.context.frames.resolved", frames=len(frames))
    return frames


__all__ = [
    "DEFAULT_CONTEXT",
    "RuntimeContext",
    "Federation",
    "ReferenceFrame",
    "resolve_contexts",
    "resolve_reference_frames",
]
