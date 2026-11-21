"""EC-1 provisional-state disclosure contract (DE-05 / C-05 / IP-01).

This is the **canonical, single definition** of the EC-1 provisional-state disclosure:
because the external constitutional gates (EC-1…EC-6) remain open, any artifact produced
from a compiled blueprint runs on *provisional engineering determinations* and asserts
**no constitutional finality or authority** (IP-01, IP-02; Technology Constitution DE-05).

It lives in :mod:`engine.foundation` because it is a **contract**, not a runtime mechanism,
and because it is consumed by layers that must not depend on the runtime: acceptance
(EPIC-VAL-002), certification (EPIC-008) and validation (EPIC-007) each stamp or check the
disclosure, while :mod:`engine.runtime` orchestrates all three through its bridge. With the
contract homed in the runtime package those two directions closed a dependency cycle; homed
here, both sides depend downward on the one layer they already share, and no adapter,
inversion or indirection is required.

The disclosure is pure data — no secrets, no wall-clock state — so it does not disturb
determinism (IMP-007 §5): identical inputs yield an identical disclosure.

Runtime-specific behaviour is **not** here and is not duplicated here:
:func:`engine.runtime.disclosure.inject_provisional_state` stamps a
:class:`~engine.runtime.assembly.RuntimeUnit`, and
:func:`engine.runtime.disclosure.require_disclosure` raises the runtime's own
:class:`~engine.runtime.errors.DisclosureError`. Both remain in the runtime, which is where
their subject matter lives; both build on the predicate defined here.
"""

from __future__ import annotations

from typing import Any

#: Stable identity of the EC-1 provisional-state disclosure.
DISCLOSURE_ID = "EC-1-PROVISIONAL-STATE"

#: Constitution rule that mandates the disclosure and the gate it discloses.
DISCLOSURE_STANDARD = "DE-05"
DISCLOSURE_GATE = "EC-1"

#: The human-readable disclosure statement (IP-01 / DE-05 / C-05).
DISCLOSURE_STATEMENT = (
    "This runtime is generated engineering execution built on provisional "
    "constitutional determinations. The external gates (EC-1) remain open; this "
    "artifact asserts no constitutional finality, authority, or ratification and "
    "holds engineering-execution authority only."
)


def build_disclosure() -> dict[str, Any]:
    """Return the canonical, deterministic EC-1 provisional-state disclosure block."""
    return {
        "disclosure_id": DISCLOSURE_ID,
        "standard": DISCLOSURE_STANDARD,
        "gate": DISCLOSURE_GATE,
        "gate_open": True,
        "asserts_constitutional_finality": False,
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "statement": DISCLOSURE_STATEMENT,
    }


def disclosure_present(disclosure: dict[str, Any] | None) -> bool:
    """True iff ``disclosure`` is a well-formed EC-1 provisional-state disclosure."""
    if not isinstance(disclosure, dict):
        return False
    return (
        disclosure.get("disclosure_id") == DISCLOSURE_ID
        and disclosure.get("gate") == DISCLOSURE_GATE
        and disclosure.get("asserts_constitutional_finality") is False
        and bool(disclosure.get("statement"))
    )


__all__ = [
    "DISCLOSURE_GATE",
    "DISCLOSURE_ID",
    "DISCLOSURE_STANDARD",
    "DISCLOSURE_STATEMENT",
    "build_disclosure",
    "disclosure_present",
]
