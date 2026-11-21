"""UCXI-000001 Part 07 — Context Resolution: determining what the context *is*.

Resolution answers a request — *"what is the temporal context here?"* — from the
registry, and returns a value per dimension **with the provenance of the value that
won**. Three rules make the answer defensible rather than convenient:

    * **Explicit precedence** (CXL-07). Candidates are ordered by authority
      (constitutional ▸ architectural ▸ operational ▸ observed ▸ inferred) and then by
      *specificity* — a context declared at ``ucos.engine.runtime`` beats one declared
      at ``ucos`` for a request scoped to the former, because the narrower declaration
      is closer to the subject.
    * **Ambiguity is refused, not averaged** (CXL-11). Two candidates of equal
      authority and equal specificity that assert *different* values for the same
      dimension raise :class:`~engine.context.errors.ContextAmbiguityError`. Equal
      authority asserting the *same* value is not a conflict.
    * **Provenance survives** (CXL-08). Each resolved value keeps the authority and
      source that produced it, and the result records both the contexts that won and
      every context considered, so a resolution can be replayed and audited.

Resolution is pure and deterministic: same registry, same request, same bytes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.context.errors import ContextAmbiguityError, ContextResolutionFailure
from engine.context.model import ContextRecord, ContextValue, Observer, ResolvedContext
from engine.context.registry import ContextRegistry
from engine.context.taxonomy import ContextKind
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("context.resolution")


@dataclass(frozen=True, slots=True)
class ContextRequest:
    """A request to resolve one context kind within a scope.

    ``namespace`` scopes the request: a context applies if it is declared *at or above*
    that namespace (``ucos`` applies to ``ucos.engine.runtime``), which is what makes
    a broad platform context inheritable while a narrow one still wins. ``boundary``
    restricts candidates to one bounding frame. ``dimensions`` overrides the required
    set (defaulting to the ontology's required dimensions for the kind).
    """

    kind: str
    namespace: str | None = None
    boundary: str | None = None
    dimensions: tuple[str, ...] = ()
    observer: Observer | None = None
    include_inactive: bool = False
    members: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        kind = getattr(self.kind, "value", self.kind)
        object.__setattr__(self, "kind", str(kind))
        if self.namespace is not None:
            object.__setattr__(self, "namespace", str(self.namespace).strip().lower())
        object.__setattr__(self, "dimensions", tuple(sorted(self.dimensions)))
        object.__setattr__(self, "members", tuple(sorted(self.members)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "namespace": self.namespace,
            "boundary": self.boundary,
            "dimensions": list(self.dimensions),
            "observer": self.observer.to_dict() if self.observer else None,
            "include_inactive": self.include_inactive,
            "members": list(self.members),
        }


@dataclass(frozen=True, slots=True)
class Candidate:
    """One record considered for a request, with its computed precedence key."""

    record: ContextRecord
    specificity: int
    key: tuple[int, int, str] = field(default=(0, 0, ""), compare=False)

    @classmethod
    def of(cls, record: ContextRecord, specificity: int) -> Candidate:
        return cls(
            record=record,
            specificity=specificity,
            # Lower authority rank wins; then greater specificity; then stable id order.
            key=(record.authority.rank, -specificity, record.context_id),
        )


def _applies(record: ContextRecord, request: ContextRequest) -> bool:
    if record.kind != request.kind:
        return False
    if request.members and record.context_id not in request.members:
        return False
    if not request.include_inactive and not record.lifecycle.is_active:
        return False
    if request.boundary is not None and record.boundary != request.boundary:
        return False
    if request.namespace is None:
        return True
    return request.namespace == record.namespace or request.namespace.startswith(
        record.namespace + "."
    )


def candidates(registry: ContextRegistry, request: ContextRequest) -> tuple[Candidate, ...]:
    """Every applicable record for ``request``, ordered by precedence (best first)."""
    found = [
        Candidate.of(record, len(record.namespace.split(".")))
        for record in registry.records()
        if _applies(record, request)
    ]
    return tuple(sorted(found, key=lambda c: c.key))


def _merge(applicable: tuple[Candidate, ...], request: ContextRequest) -> dict[str, ContextValue]:
    """Merge candidate values by precedence, refusing genuine ambiguity."""
    winners: dict[str, ContextValue] = {}
    winner_keys: dict[str, tuple[int, int, str]] = {}
    for candidate in applicable:
        for value in candidate.record.values:
            current = winners.get(value.dimension)
            if current is None:
                winners[value.dimension] = value
                winner_keys[value.dimension] = candidate.key
                continue
            incumbent = winner_keys[value.dimension]
            # Candidates are pre-sorted, so an incumbent is never weaker. A challenger
            # only matters when it ties on authority *and* specificity.
            if incumbent[:2] != candidate.key[:2]:
                continue
            if current.value != value.value:
                raise ContextAmbiguityError(
                    "two equally authoritative contexts disagree on a dimension",
                    kind=request.kind,
                    dimension=value.dimension,
                    authority=value.authority.value,
                    sources=sorted({current.source, value.source}),
                )
    return winners


def resolve(registry: ContextRegistry, request: ContextRequest) -> ResolvedContext:
    """Resolve one context kind, or fail closed.

    Raises:
        ContextResolutionFailure: no applicable context, or a required dimension is
            unresolved.
        ContextAmbiguityError: equally authoritative contexts disagree.
    """
    with trace("context.resolution.resolve", kind=request.kind):
        applicable = candidates(registry, request)
        if not applicable:
            raise ContextResolutionFailure(
                "no registered context satisfies the request",
                kind=request.kind,
                namespace=request.namespace,
                boundary=request.boundary,
            )
        winners = _merge(applicable, request)
        if request.dimensions:
            required: tuple[str, ...] = request.dimensions
        elif registry.ontology.specifies(request.kind):
            required = registry.ontology.required_for(request.kind)
        else:
            raise ContextResolutionFailure(
                "context kind has no declared ontological shape, so nothing is required "
                "of a resolution (declare the kind before resolving it)",
                kind=request.kind,
            )
        missing = [name for name in required if name not in winners]
        if missing:
            raise ContextResolutionFailure(
                "required context dimension(s) are unresolved",
                kind=request.kind,
                missing=missing,
                considered=[c.record.context_id for c in applicable],
            )
        values = tuple(winners[name] for name in sorted(winners))
        resolved = ResolvedContext(
            kind=request.kind,
            values=values,
            sources=tuple(sorted({value.source for value in values})),
            considered=tuple(c.record.context_id for c in applicable),
            observer=request.observer,
        )
    _logger.info(
        "context.resolution.resolved",
        kind=request.kind,
        dimensions=len(resolved.values),
        considered=len(resolved.considered),
    )
    return resolved


def resolve_kind(
    registry: ContextRegistry,
    kind: ContextKind | str,
    *,
    namespace: str | None = None,
    boundary: str | None = None,
    observer: Observer | None = None,
) -> ResolvedContext:
    """Convenience form of :func:`resolve` for one kind."""
    return resolve(
        registry,
        ContextRequest(
            kind=kind if isinstance(kind, str) else kind.value,
            namespace=namespace,
            boundary=boundary,
            observer=observer,
        ),
    )


def resolve_many(
    registry: ContextRegistry,
    kinds: Iterable[ContextKind | str] | None = None,
    *,
    namespace: str | None = None,
    boundary: str | None = None,
    observer: Observer | None = None,
) -> dict[str, ResolvedContext]:
    """Resolve several kinds (default: every registered kind), keyed by kind."""
    wanted = (
        tuple(registry.kinds())
        if kinds is None
        else tuple(k if isinstance(k, str) else k.value for k in kinds)
    )
    return {
        kind: resolve_kind(
            registry, kind, namespace=namespace, boundary=boundary, observer=observer
        )
        for kind in sorted(wanted)
    }


def resolve_universal(
    registry: ContextRegistry,
    *,
    namespace: str | None = None,
    boundary: str | None = None,
    observer: Observer | None = None,
) -> dict[str, ResolvedContext]:
    """Resolve every *universal* kind, failing closed on the first unresolvable one."""
    return resolve_many(
        registry,
        registry.taxonomy.universal_kinds(),
        namespace=namespace,
        boundary=boundary,
        observer=observer,
    )


def try_resolve(
    registry: ContextRegistry, request: ContextRequest
) -> tuple[ResolvedContext | None, str]:
    """Resolve without raising: returns ``(resolved, "")`` or ``(None, reason)``.

    For reporting surfaces (validation, dashboards) that must survey every kind
    rather than stop at the first refusal.
    """
    try:
        return resolve(registry, request), ""
    except ContextResolutionFailure as exc:
        return None, str(exc)


def resolution_report(registry: ContextRegistry) -> dict[str, Any]:
    """A deterministic survey of the resolvability of every universal kind."""
    rows: list[dict[str, Any]] = []
    for kind in registry.taxonomy.universal_kinds():
        resolved, reason = try_resolve(registry, ContextRequest(kind=kind))
        rows.append(
            {
                "kind": kind,
                "resolvable": resolved is not None,
                "dimensions": len(resolved.values) if resolved else 0,
                "sources": list(resolved.sources) if resolved else [],
                "reason": reason,
            }
        )
    return {
        "kinds": rows,
        "resolvable": sum(1 for row in rows if row["resolvable"]),
        "total": len(rows),
        "all_resolvable": all(row["resolvable"] for row in rows),
    }


def values_of(resolved: Mapping[str, ResolvedContext]) -> dict[str, dict[str, Any]]:
    """Flatten resolved contexts to ``{kind: {dimension: value}}``."""
    return {kind: resolved[kind].value_mapping() for kind in sorted(resolved)}


__all__ = [
    "ContextRequest",
    "Candidate",
    "candidates",
    "resolve",
    "resolve_kind",
    "resolve_many",
    "resolve_universal",
    "try_resolve",
    "resolution_report",
    "values_of",
]
