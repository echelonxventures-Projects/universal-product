"""UCXI-000001 Part 10 — Context Runtime: binding, activating and propagating context.

The runtime is where a composed context becomes the *ambient* context of executing
work. It is deliberately thin and deliberately strict:

    * **Activation is scoped.** :meth:`ContextRuntime.activate` is a context manager;
      the activation is popped on exit even when the body raises, so context never
      leaks past the work it bounds.
    * **Nesting cannot widen scope** (CXL-04). A nested activation may narrow the
      active frames or stay within them, and may cross into a frame only when the
      outer composition federates into it. Widening — activating an unrelated frame
      inside an active one — is refused.
    * **Activation identity is deterministic** (CXL-05). An activation id is a digest
      of the composition, the depth and the parent activation: no clock, no counter,
      no randomness. The same nesting always yields the same ids, which is what lets a
      runtime trace be compared byte-for-byte across runs.
    * **Propagation is explicit.** :meth:`ContextRuntime.snapshot` and
      :meth:`ContextRuntime.restore` move the active stack into another execution unit
      (a task, a thread) rather than relying on ambient inheritance.

The ambient stack lives on a :class:`contextvars.ContextVar`, so activation is
async-safe and per-task, and the correlation identity already used by logging and
telemetry (:mod:`engine.foundation.obs.context`) is bound alongside it so context
activations and log lines share one id.
"""

from __future__ import annotations

import contextvars
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from engine.context.composition import ComposedContext
from engine.context.errors import ContextRuntimeError
from engine.context.model import content_digest
from engine.foundation.obs.context import (
    correlation_id,
    reset_correlation_id,
    set_correlation_id,
)
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("context.runtime")


@dataclass(frozen=True, slots=True)
class ContextActivation:
    """One entry of the ambient activation stack."""

    activation_id: str
    composition_id: str
    frames: tuple[str, ...]
    depth: int
    parent: str | None
    correlation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "activation_id": self.activation_id,
            "composition_id": self.composition_id,
            "frames": list(self.frames),
            "depth": self.depth,
            "parent": self.parent,
            "correlation": self.correlation,
        }


@dataclass(frozen=True, slots=True)
class _Frame:
    """The internal stack frame: an activation plus the composition it activated."""

    activation: ContextActivation
    composed: ComposedContext


_stack: contextvars.ContextVar[tuple[_Frame, ...]] = contextvars.ContextVar(
    "ucxi_context_stack", default=()
)


def _activation_id(composition_id: str, depth: int, parent: str | None) -> str:
    return "CTXA-" + content_digest([composition_id, depth, parent or ""])[:12]


def _frames_of(composed: ComposedContext) -> tuple[str, ...]:
    return tuple(frame.context_id for frame in composed.frames)


def _reachable_frames(composed: ComposedContext) -> frozenset[str]:
    """The frames an active composition may legitimately narrow or federate into."""
    reachable = set(_frames_of(composed))
    for reference_frame in composed.reference_frames:
        for target in reference_frame.federated:
            frame = composed.frame_of(target)
            if frame is not None:
                reachable.add(frame)
    return frozenset(reachable)


class ContextRuntime:
    """The ambient context runtime: bind, activate, read, propagate, release.

    The runtime holds no state of its own — the active stack is the context variable —
    so two runtime instances in the same task observe the same activation, and an
    activation made in one is visible to the other. That is intentional: the ambient
    context is a property of the execution, not of the object that asked about it.
    """

    __slots__ = ()

    # -- binding ------------------------------------------------------------ #

    def bind(
        self, composed: ComposedContext, *, require_universal: bool = False
    ) -> ContextActivation:
        """Validate a composition for activation and return the activation it would get.

        Binding performs the checks activation would perform, without mutating the
        stack, so a caller can verify admissibility before committing to it.

        Raises:
            ContextRuntimeError: the composition is not admissible here.
        """
        self._require_admissible(composed, require_universal=require_universal)
        parent = self.current()
        depth = 0 if parent is None else parent.depth + 1
        return ContextActivation(
            activation_id=_activation_id(
                composed.composition_id, depth, parent.activation_id if parent else None
            ),
            composition_id=composed.composition_id,
            frames=_frames_of(composed),
            depth=depth,
            parent=parent.activation_id if parent else None,
            correlation=correlation_id() or _activation_id(composed.composition_id, depth, None),
        )

    def _require_admissible(self, composed: ComposedContext, *, require_universal: bool) -> None:
        if not composed.members:
            raise ContextRuntimeError("cannot activate an empty composition")
        if require_universal and not composed.is_universally_complete:
            raise ContextRuntimeError(
                "composition does not cover every universal context kind",
                missing=list(composed.missing_universal()),
            )
        stack = _stack.get()
        if not stack:
            return
        outer = stack[-1].composed
        permitted = _reachable_frames(outer)
        widening = sorted(set(_frames_of(composed)) - permitted)
        if widening:
            raise ContextRuntimeError(
                "nested activation would widen the active context boundary",
                active_frames=sorted(permitted),
                requested_frames=widening,
            )

    # -- activation --------------------------------------------------------- #

    @contextmanager
    def activate(
        self, composed: ComposedContext, *, require_universal: bool = False
    ) -> Iterator[ContextActivation]:
        """Activate ``composed`` for the duration of the block."""
        activation = self.bind(composed, require_universal=require_universal)
        correlation_token = None
        if correlation_id() is None:
            correlation_token = set_correlation_id(activation.correlation)
        stack_token = _stack.set(_stack.get() + (_Frame(activation=activation, composed=composed),))
        with trace("context.runtime.activate", composition=composed.composition_id):
            _logger.info(
                "context.runtime.activated",
                activation_id=activation.activation_id,
                composition_id=activation.composition_id,
                depth=activation.depth,
            )
            try:
                yield activation
            finally:
                _stack.reset(stack_token)
                if correlation_token is not None:
                    reset_correlation_id(correlation_token)
                _logger.info("context.runtime.released", activation_id=activation.activation_id)

    # -- reads -------------------------------------------------------------- #

    def current(self) -> ContextActivation | None:
        """The innermost activation, or ``None`` if no context is active."""
        stack = _stack.get()
        return stack[-1].activation if stack else None

    def current_context(self) -> ComposedContext | None:
        """The innermost active composition, or ``None``."""
        stack = _stack.get()
        return stack[-1].composed if stack else None

    def stack(self) -> tuple[ContextActivation, ...]:
        """The whole activation stack, outermost first."""
        return tuple(frame.activation for frame in _stack.get())

    def depth(self) -> int:
        """The current nesting depth (0 when nothing is active)."""
        return len(_stack.get())

    def is_active(self) -> bool:
        return bool(_stack.get())

    def require_active(self) -> ComposedContext:
        """The active composition, or fail closed."""
        composed = self.current_context()
        if composed is None:
            raise ContextRuntimeError("no context is active")
        return composed

    def value(self, kind: str, dimension: str) -> Any:
        """Read one dimension from the active composition, or ``None``.

        Inner activations shadow outer ones: the innermost frame that resolves the
        dimension wins, which is what makes narrowing meaningful.
        """
        for frame in reversed(_stack.get()):
            found = frame.composed.value(kind, dimension)
            if found is not None:
                return found
        return None

    def require(self, kind: str, dimension: str) -> Any:
        """Fail-closed form of :meth:`value`."""
        found = self.value(kind, dimension)
        if found is None:
            raise ContextRuntimeError(
                "required context dimension is not active", kind=kind, dimension=dimension
            )
        return found

    def provenance(self, kind: str, dimension: str) -> str | None:
        """The source of the value :meth:`value` would return."""
        for frame in reversed(_stack.get()):
            resolved = frame.composed.get(kind)
            if resolved is not None and resolved.get(dimension) is not None:
                return resolved.provenance_of(dimension)
        return None

    def frames(self) -> tuple[str, ...]:
        """The frames bounding the innermost activation."""
        activation = self.current()
        return activation.frames if activation else ()

    def can_reference(self, source: str, target: str) -> bool:
        """True iff the active composition authorises ``source`` to see ``target``."""
        composed = self.current_context()
        return composed is not None and composed.can_reference(source, target)

    # -- propagation -------------------------------------------------------- #

    def snapshot(self) -> tuple[ComposedContext, ...]:
        """The active compositions, outermost first, for explicit propagation."""
        return tuple(frame.composed for frame in _stack.get())

    @contextmanager
    def restore(
        self, snapshot: tuple[ComposedContext, ...]
    ) -> Iterator[tuple[ContextActivation, ...]]:
        """Re-establish a snapshot in this execution unit for the duration of the block.

        The stack is rebuilt by activating each composition in order, so every
        admissibility rule is re-checked rather than trusted: a snapshot cannot be used
        to smuggle a widening activation into a narrower execution unit.
        """
        if not snapshot:
            yield ()
            return
        head, *tail = snapshot
        with self.activate(head) as activation:
            if not tail:
                yield (activation,)
            else:
                with self.restore(tuple(tail)) as rest:
                    yield (activation, *rest)

    def trace(self) -> dict[str, Any]:
        """A deterministic description of the active stack (for evidence)."""
        return {
            "depth": self.depth(),
            "activations": [activation.to_dict() for activation in self.stack()],
            "frames": list(self.frames()),
        }


#: The process-wide runtime handle (the ambient stack lives in a context variable).
RUNTIME = ContextRuntime()


@contextmanager
def activate(
    composed: ComposedContext, *, require_universal: bool = False
) -> Iterator[ContextActivation]:
    """Module-level convenience wrapper over :meth:`ContextRuntime.activate`."""
    with RUNTIME.activate(composed, require_universal=require_universal) as activation:
        yield activation


def current() -> ContextActivation | None:
    """The innermost activation, or ``None``."""
    return RUNTIME.current()


def current_context() -> ComposedContext | None:
    """The innermost active composition, or ``None``."""
    return RUNTIME.current_context()


def value(kind: str, dimension: str) -> Any:
    """Read one dimension from the ambient context."""
    return RUNTIME.value(kind, dimension)


def require(kind: str, dimension: str) -> Any:
    """Read one dimension from the ambient context, failing closed."""
    return RUNTIME.require(kind, dimension)


__all__ = [
    "ContextActivation",
    "ContextRuntime",
    "RUNTIME",
    "activate",
    "current",
    "current_context",
    "value",
    "require",
]
