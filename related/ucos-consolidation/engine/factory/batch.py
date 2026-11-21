"""TASK-000044 — Multi-Blueprint Execution (EPIC-006).

Generates many blueprints through the single orchestrator path with a **fixed,
deterministic ordering**: requests are processed sorted by blueprint id and the
results are returned in that same order. Because each generation is itself
deterministic (IMP-007 §5) and the ordering is fixed, **identical inputs produce
identical outputs** — the batch adds ordering, not new behaviour.

Duplicate blueprint ids in the input collapse to a single generation (the batch is
a set-like closure over ids), keeping the result one-per-blueprint and stable.
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.factory.contracts import FactoryRequest, FactoryResult
from engine.factory.orchestrator import GenerationOrchestrator
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("factory.batch")


def _dedupe_sorted(requests: Iterable[FactoryRequest]) -> tuple[FactoryRequest, ...]:
    """Collapse duplicate blueprint ids and order deterministically by id."""
    by_id: dict[str, FactoryRequest] = {}
    for request in requests:
        by_id.setdefault(request.blueprint_id, request)
    return tuple(by_id[bp] for bp in sorted(by_id))


def generate_many(
    orchestrator: GenerationOrchestrator,
    requests: Iterable[FactoryRequest],
) -> tuple[FactoryResult, ...]:
    """Generate multiple blueprints deterministically; one result per blueprint.

    The returned tuple is ordered by blueprint id. Identical inputs (any order)
    yield an identical result tuple.
    """
    ordered = _dedupe_sorted(requests)
    with trace("factory.batch", count=len(ordered)):
        results = tuple(orchestrator.generate(request) for request in ordered)
    _logger.info(
        "factory.batch.completed",
        requested=len(ordered),
        generated=sum(1 for r in results if r.success),
    )
    return results


__all__ = ["generate_many"]
