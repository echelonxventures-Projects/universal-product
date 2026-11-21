"""TASK-000036 — Provisional-State Disclosure (EPIC-005, DE-05 / C-05 / IP-01).

The EC-1 provisional-state disclosure **contract** — its identity, standard, gate,
statement, constructor and predicate — is defined once in
:mod:`engine.foundation.contracts.disclosure` and is re-exported here unchanged. Nothing is
restated or reimplemented: this module holds exactly the two behaviours whose subject matter
is the runtime itself.

:func:`inject_provisional_state` stamps the disclosure onto a
:class:`~engine.runtime.assembly.RuntimeUnit` and embeds the same disclosure into its runtime
descriptor, so the disclosure **survives packaging and deployment generation** (TASK-000035
copies ``unit.disclosure`` into every deployment and rollback descriptor and into the
generated Kubernetes annotations). :func:`require_disclosure` turns the predicate into a hard
gate by raising the runtime's own :class:`~engine.runtime.errors.DisclosureError`.

The public surface of this module is unchanged, so every existing import site continues to
resolve here. Consumers that must not depend on the runtime — acceptance, certification and
validation — import the contract from :mod:`engine.foundation.contracts.disclosure` directly;
homing the contract in this package is what previously closed a dependency cycle between the
runtime bridge and the three engines it orchestrates.

The disclosure is pure data — no secrets, no wall-clock state — so it does not disturb
determinism (IMP-007 §5): identical inputs yield an identical disclosure.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from engine.foundation.contracts.disclosure import (
    DISCLOSURE_GATE,
    DISCLOSURE_ID,
    DISCLOSURE_STANDARD,
    DISCLOSURE_STATEMENT,
    build_disclosure,
    disclosure_present,
)
from engine.runtime.errors import DisclosureError

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.assembly import RuntimeUnit


def inject_provisional_state(unit: RuntimeUnit) -> RuntimeUnit:
    """Return a copy of ``unit`` carrying the EC-1 provisional-state disclosure.

    The disclosure is attached to the unit *and* embedded in its runtime
    descriptor under ``provisional_state_disclosure`` so downstream deployment
    generation preserves it (DE-05). The operation is idempotent: re-injecting an
    already-disclosed unit reproduces the identical disclosure.
    """
    disclosure = build_disclosure()
    descriptor = dict(unit.descriptor)
    descriptor["provisional_state_disclosure"] = disclosure
    return replace(unit, disclosure=disclosure, descriptor=descriptor)


def require_disclosure(disclosure: dict[str, Any] | None) -> dict[str, Any]:
    """Return ``disclosure`` if present and well-formed, else raise (DE-05)."""
    if not disclosure_present(disclosure):
        raise DisclosureError(
            "EC-1 provisional-state disclosure is required while gates are open",
            standard=DISCLOSURE_STANDARD,
            gate=DISCLOSURE_GATE,
        )
    return dict(disclosure) if disclosure is not None else {}


__all__ = [
    "DISCLOSURE_ID",
    "DISCLOSURE_STANDARD",
    "DISCLOSURE_GATE",
    "DISCLOSURE_STATEMENT",
    "build_disclosure",
    "inject_provisional_state",
    "disclosure_present",
    "require_disclosure",
]
