"""UCOS Ω∞ Phase 2 — TIME, as one registered reference domain among fourteen.

AUTHORITY = NONE (DERIVED TRUTH).

THIS SUBPACKAGE IS NOT THE ROOT OF THE ARCHITECTURE, and the import graph is how that is checkable
rather than asserted: ``temporal`` imports ``reference``, and ``reference`` imports nothing from
``temporal``. A deployment that registers no clock, no calendar and no frame still has a complete
governance architecture — it simply records no temporal coordinates, and
``registry.GovernanceRegistry`` accepts an absent coordinate for exactly that reason.

    frames.py       WHERE an observation was made, and WHAT its components count
    ordering.py     HOW two positions compare, as a provider, with relations in a registry
    coordinate.py   the universal temporal coordinate, and comparison that refuses before it guesses
    clocks.py       clocks as providers. No ``datetime``, no ``time``, no ``calendar`` module
    calendars.py    calendars as providers. Gregorian exists in exactly one deletable class

WHAT WAS FOUND HERE BY ASSUMING FAILURE. The first draft of this subpackage replaced
``datetime.now()`` with a ``Clock`` protocol returning ``str``, and called the assumption removed.
It had four left: a total ordering implied by a sortable string, an unstated Earth frame, ``json``
and ``sha256`` hardcoded in the coordinate's identity, and ``tuple[int, ...]`` asserting that
measurement is numeric. Relocating ``datetime.now()`` behind an interface removed none of them.
"""

from __future__ import annotations

#: The standing this package holds, as a VALUE rather than only as a sentence in the docstring
#: above. The literal is the token UCOS-UCAF-001 classifies (UCAF-TC-02, "the derived-truth tier
#: records and asserts nothing"): it was `"NONE"`, which said the same thing in a spelling no
#: classification carried, so the authority-realization gate reported a token minted in the
#: executable plane and classified nowhere. Two spellings of one standing is how a vocabulary
#: acquires an unclassifiable member.
AUTHORITY = "NONE (DERIVED TRUTH)"
