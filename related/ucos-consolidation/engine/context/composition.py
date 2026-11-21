"""UCXI-000001 Part 08 — Context Composition: assembling a bounded, isolated whole.

Composition takes a set of registered contexts and produces one
:class:`ComposedContext`: the resolved value of every kind present, bound into
explicit frames, with every cross-frame reference authorised by an explicit
federation. It is where the layer's two hardest guarantees are enforced:

    * **Boundedness** (CXL-03) — every member is bound to exactly one frame. An
      unbounded member is refused.
    * **Isolation** (CXL-04) — a dependency that crosses a frame boundary is refused
      unless an explicit ``federates`` relation authorises it. Frames do not leak into
      each other by accident.

Neither guarantee is reimplemented here. Both are **delegated** to the already
certified runtime composition primitives —
:func:`engine.runtime.context.resolve_contexts` and
:func:`engine.runtime.context.resolve_reference_frames` over an
:class:`engine.runtime.graph.RuntimeGraph` — which already fail closed on unbounded
scope, cross-context leaks, and dangling, duplicate or same-frame federations. This
module supplies the context-layer semantics (which edges are dependencies, which
relation authorises federation) and translates the runtime's refusals into the context
error taxonomy.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from engine.compiler.cycles import assert_acyclic
from engine.compiler.partition import (
    Federation,
    Frame,
    IsolationError,
    Partition,
    UnboundedMemberError,
    resolve_frames,
    resolve_partitions,
)
from engine.context.errors import (
    ContextCompositionError,
    ContextIsolationError,
)
from engine.context.model import Observer, ResolvedContext, content_digest, seal
from engine.context.registry import ContextRegistry
from engine.context.resolution import ContextRequest, resolve
from engine.context.taxonomy import ContextRelation
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("context.composition")


# --------------------------------------------------------------------------- #
# Boundedness (CXL-03) and isolation (CXL-04) — the rules this layer DECLARES   #
# --------------------------------------------------------------------------- #
#
# UCXI-000001 declares both guarantees, and this module enforces them. The RULES
# themselves are general — partition members, then refuse an unauthorised crossing —
# and general rules belong in the shared substrate, not in one of their consumers.
# engine.compiler already hosts the graph primitives engine/runtime/graph.py reuses
# "verbatim (Mandatory Rule 4)", so engine.compiler.partition is where these live and
# both this layer and engine.runtime depend DOWNWARD on it.
#
# An earlier correction of the same cycle put these definitions HERE. That broke the
# ring but left a general primitive inside a consumer, so a third layer wanting
# partitions would have had to depend on the context layer — the same inversion, one
# step over. The names below are this layer's vocabulary for the shared rules.

CompositionPartition = Partition
CompositionFederation = Federation
CompositionFrame = Frame
RuntimeContext = Partition
ReferenceFrame = Frame
resolve_contexts = resolve_partitions

#: The relations that make one context depend on another for its own resolution.
DEPENDENCY_RELATIONS: tuple[ContextRelation, ...] = (
    ContextRelation.DEPENDS_ON,
    ContextRelation.DERIVES_FROM,
    ContextRelation.REFINES,
)


@dataclass(frozen=True, slots=True)
class ComposedContext:
    """A bounded, isolated, fully resolved context assembly.

    ``composition_id`` is deterministic: it is a digest of the members, their frame
    bindings and the authorising federations, so the same assembly always carries the
    same identity and the same seal.
    """

    composition_id: str
    members: tuple[str, ...]
    frames: tuple[RuntimeContext, ...]
    federations: tuple[Federation, ...]
    reference_frames: tuple[ReferenceFrame, ...]
    resolved: tuple[ResolvedContext, ...]
    universal_expected: tuple[str, ...]
    observer: Observer | None = None
    content_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "resolved", tuple(sorted(self.resolved, key=lambda r: r.kind)))
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    def _payload(self) -> dict[str, Any]:
        return {
            "composition_id": self.composition_id,
            "members": list(self.members),
            "frames": [frame.to_dict() for frame in self.frames],
            "federations": [federation.to_dict() for federation in self.federations],
            "reference_frames": [frame.to_dict() for frame in self.reference_frames],
            "resolved": [resolved.to_dict() for resolved in self.resolved],
            "universal_expected": list(self.universal_expected),
            "observer": self.observer.to_dict() if self.observer else None,
        }

    # -- reads -------------------------------------------------------------- #

    def kinds(self) -> tuple[str, ...]:
        """Every kind present in the composition, ordered."""
        return tuple(resolved.kind for resolved in self.resolved)

    def get(self, kind: str) -> ResolvedContext | None:
        """The resolved context for ``kind``, or ``None``."""
        for resolved in self.resolved:
            if resolved.kind == kind:
                return resolved
        return None

    def value(self, kind: str, dimension: str) -> Any:
        """One resolved dimension value, or ``None`` if absent."""
        resolved = self.get(kind)
        return None if resolved is None else resolved.get(dimension)

    def frame_of(self, context_id: str) -> str | None:
        """The frame that bounds ``context_id``, or ``None`` if not a member."""
        for frame in self.frames:
            if frame.contains(context_id):
                return frame.context_id
        return None

    def reference_frame_of(self, context_id: str) -> ReferenceFrame | None:
        for frame in self.reference_frames:
            if frame.universe_id == context_id:
                return frame
        return None

    def can_reference(self, source: str, target: str) -> bool:
        """True iff ``source`` may reference ``target`` within this composition."""
        frame = self.reference_frame_of(source)
        return frame is not None and frame.can_reference(target)

    def missing_universal(self) -> tuple[str, ...]:
        """Universal kinds expected but absent from the composition, ordered."""
        present = set(self.kinds())
        return tuple(kind for kind in self.universal_expected if kind not in present)

    @property
    def is_universally_complete(self) -> bool:
        """True iff every universal kind is resolved in this composition."""
        return not self.missing_universal()

    def summary(self) -> dict[str, Any]:
        return {
            "composition_id": self.composition_id,
            "members": len(self.members),
            "frames": len(self.frames),
            "federations": len(self.federations),
            "kinds": list(self.kinds()),
            "universal_expected": len(self.universal_expected),
            "missing_universal": list(self.missing_universal()),
            "universally_complete": self.is_universally_complete,
            "content_hash": self.content_hash,
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["universally_complete"] = self.is_universally_complete
        payload["missing_universal"] = list(self.missing_universal())
        payload["content_hash"] = self.content_hash
        return payload


def _dependency_edges(
    registry: ContextRegistry, members: tuple[str, ...]
) -> dict[str, tuple[str, ...]]:
    """The dependency graph induced on ``members`` (closure enforced)."""
    member_set = set(members)
    edges: dict[str, list[str]] = {member: [] for member in members}
    for relation in DEPENDENCY_RELATIONS:
        for edge in registry.relations(relation=relation):
            if edge.source not in member_set:
                continue
            if edge.target not in member_set:
                raise ContextCompositionError(
                    "a member depends on a context outside the composition (open graph)",
                    context_id=edge.source,
                    dependency=edge.target,
                    relation=edge.relation.value,
                )
            edges[edge.source].append(edge.target)
    return {node: tuple(sorted(set(targets))) for node, targets in edges.items()}


def _declared_federations(
    registry: ContextRegistry, members: tuple[str, ...]
) -> tuple[Federation, ...]:
    """Federations declared in the registry between members, ordered."""
    member_set = set(members)
    found = {
        (edge.source, edge.target)
        for edge in registry.relations(relation=ContextRelation.FEDERATES)
        if edge.source in member_set and edge.target in member_set
    }
    return tuple(Federation(source=s, target=t) for s, t in sorted(found))


def compose(
    registry: ContextRegistry,
    *,
    context_ids: Iterable[str] | None = None,
    federations: Iterable[Federation] = (),
    observer: Observer | None = None,
    require_universal: bool = False,
) -> ComposedContext:
    """Compose the given contexts (default: every active context) into one whole.

    Args:
        registry: the registration authority holding the members.
        context_ids: the members; defaults to every context in an active lifecycle.
        federations: additional federations beyond those declared in the registry.
        observer: the vantage recorded on every resolved context.
        require_universal: when true, an incomplete universal set is refused rather
            than merely reported.

    Raises:
        ContextCompositionError: an unknown member, an open dependency graph, an
            unbounded member, or (when required) an incomplete universal set.
        ContextIsolationError: a cross-frame dependency without an authorising
            federation, or a malformed federation.
    """
    with trace("context.composition.compose"):
        if context_ids is None:
            members = tuple(
                record.context_id for record in registry.records() if record.lifecycle.is_active
            )
        else:
            members = tuple(sorted(set(context_ids)))
            unknown = [cid for cid in members if not registry.has(cid)]
            if unknown:
                raise ContextCompositionError(
                    "composition member is not registered", members=unknown
                )
        if not members:
            raise ContextCompositionError("a composition must have at least one member")

        bindings = {cid: registry.get(cid).boundary for cid in members}
        try:
            frames = resolve_partitions(bindings)
        except UnboundedMemberError as exc:
            raise ContextCompositionError(
                "composition member is not bound to a frame", detail=str(exc)
            ) from exc

        edges = _dependency_edges(registry, members)
        assert_acyclic(edges)
        all_federations = tuple(
            sorted(
                set(_declared_federations(registry, members)) | set(federations),
                key=lambda f: (f.source, f.target),
            )
        )
        try:
            reference_frames = resolve_frames(
                bindings,
                sorted(edges),
                lambda member: edges.get(member, ()),
                all_federations,
            )
        except IsolationError as exc:
            raise ContextIsolationError(
                "context isolation is not satisfied by the composition", detail=str(exc)
            ) from exc
        except UnboundedMemberError as exc:
            raise ContextCompositionError(
                "composition member is not bound to a frame", detail=str(exc)
            ) from exc

        kinds = sorted({registry.get(cid).kind for cid in members})
        resolved = tuple(
            resolve(
                registry,
                ContextRequest(kind=kind, members=members, observer=observer),
            )
            for kind in kinds
        )

        composition_id = (
            "CTXC-"
            + content_digest(
                {
                    "members": list(members),
                    "bindings": bindings,
                    "federations": [f.to_dict() for f in all_federations],
                }
            )[:12]
        )

        composed = ComposedContext(
            composition_id=composition_id,
            members=members,
            frames=frames,
            federations=all_federations,
            reference_frames=reference_frames,
            resolved=resolved,
            universal_expected=registry.taxonomy.universal_kinds(),
            observer=observer,
        )

        if require_universal and not composed.is_universally_complete:
            raise ContextCompositionError(
                "the composition does not cover every universal context kind",
                missing=list(composed.missing_universal()),
            )
    _logger.info(
        "context.composition.composed",
        composition_id=composed.composition_id,
        members=len(members),
        frames=len(frames),
        kinds=len(resolved),
    )
    return composed


def compose_universal(
    registry: ContextRegistry, *, observer: Observer | None = None
) -> ComposedContext:
    """Compose every active context and require the universal set to be complete."""
    return compose(registry, observer=observer, require_universal=True)


def merge(
    primary: ComposedContext, secondary: ComposedContext, registry: ContextRegistry
) -> ComposedContext:
    """Recompose the union of two compositions from the registry.

    Merging is *recomposition*, not value surgery: the union of the members is
    composed again from the registration authority, so boundedness, isolation and
    precedence are re-established rather than assumed to survive the merge.
    """
    return compose(
        registry,
        context_ids=set(primary.members) | set(secondary.members),
        federations=tuple(primary.federations) + tuple(secondary.federations),
        observer=primary.observer or secondary.observer,
    )


def projection(composed: ComposedContext) -> dict[str, dict[str, Any]]:
    """Flatten a composition to ``{kind: {dimension: value}}`` (for consumers)."""
    return {resolved.kind: resolved.value_mapping() for resolved in composed.resolved}


def frames_of(bindings: Mapping[str, str]) -> tuple[RuntimeContext, ...]:
    """Group a ``context_id -> frame`` binding into frames (thin reuse wrapper)."""
    try:
        return resolve_partitions(bindings)
    except UnboundedMemberError as exc:
        raise ContextCompositionError("unbounded context binding", detail=str(exc)) from exc


__all__ = [
    "DEPENDENCY_RELATIONS",
    "ComposedContext",
    "compose",
    "compose_universal",
    "merge",
    "projection",
    "frames_of",
    "Federation",
]
