"""TASK-000007 — Execution context (correlation identity).

A process-safe, async-safe correlation identifier carried on a :class:`contextvars.ContextVar`.
Logging (TASK-000006) and telemetry (TASK-000007) both read it so that every log
line, metric, and span produced while handling one unit of work shares one id
(PL-02 observability; end-to-end traceability, IP-03).
"""

from __future__ import annotations

import contextvars
import uuid

_correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "ec1_correlation_id", default=None
)


def correlation_id() -> str | None:
    """Return the current correlation id, or ``None`` if none is bound."""
    return _correlation_id.get()


def set_correlation_id(value: str) -> contextvars.Token[str | None]:
    """Bind ``value`` as the current correlation id and return a reset token."""
    if not isinstance(value, str) or not value:
        raise ValueError("correlation id must be a non-empty string")
    return _correlation_id.set(value)


def new_correlation_id() -> str:
    """Generate, bind, and return a fresh correlation id."""
    generated = uuid.uuid4().hex
    _correlation_id.set(generated)
    return generated


def reset_correlation_id(token: contextvars.Token[str | None]) -> None:
    """Restore the correlation id to the value captured by ``token``."""
    _correlation_id.reset(token)


__all__ = [
    "correlation_id",
    "set_correlation_id",
    "new_correlation_id",
    "reset_correlation_id",
]
