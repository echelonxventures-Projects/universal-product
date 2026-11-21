"""EPIC-RTE-003 — Runtime Integration & Repository Execution Bridge error taxonomy.

The Runtime Bridge connects the repository lifecycle to the existing runtime
capabilities — Runtime Composition (EPIC-006), the Runtime Execution Platform
(EPIC-RTE-002), Validation (EPIC-007), Certification (EPIC-008), Repository
Acceptance (EPIC-VAL-002), and the Universal Knowledge & Decision Architecture
(EPIC-UKDA). It **implements only integration**: it reuses every one of those
engines verbatim and adds no duplicate composition, execution, validation,
certification, acceptance, or knowledge logic.

Like every other EC-1 capability the bridge reuses the Foundation error discipline
(TASK-000006): every error is rooted in :class:`FoundationError`, carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so failures are
auditable (PL-02, IP-12) and machine-consumable. Bridge errors form a distinct
root, because integration is a separate concern from the capabilities it binds (no
duplicate capability ownership) — a failure inside a reused engine propagates as
that engine's own error, unwrapped, so the failing capability is never masked.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class RuntimeBridgeError(FoundationError):
    """Base class for all Runtime Bridge errors (EPIC-RTE-003)."""

    code = "RT-BRIDGE-000"


class BridgeInputError(RuntimeBridgeError):
    """The inputs to a bridge stage were absent, malformed, or inconsistent.

    Raised, for example, when a repository is composed with no runtime universes,
    when a composition member is neither a :class:`~engine.runtime.composition.Universe`
    nor an assembled :class:`~engine.runtime.assembly.RuntimeUnit`, or when the
    assimilated repository subject cannot be normalised.
    """

    code = "RT-BRIDGE-INPUT-001"


__all__ = [
    "RuntimeBridgeError",
    "BridgeInputError",
]
