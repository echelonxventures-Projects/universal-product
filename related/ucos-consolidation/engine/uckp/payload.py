"""UCKP Layer Zero+1 — the structural normalizer that lets a declaration take its
certification identity over the WHOLE of itself.

WHY THIS IS NOT IN ``canonical.py``. Layer Zero declares, and
``engine/tests/uckp/test_layer_zero.py`` measures, that it imports ``hashlib``, ``json``,
``typing`` and ``__future__`` and nothing else — the property that makes it safe for any module
at any layer to depend on. This normalizer needs ``dataclasses`` and ``collections.abc``. Both
are standard library and neither creates a cycle, but the allowlist is a deliberate ratchet
rather than an accident, and widening an invariant to admit one's own code is how ratchets stop
being ratchets. So the digest primitive stays exactly where it is and this sits one layer above
it, importing it rather than reimplementing it — which is also what keeps UCKP Article 3 (Zero
Duplication) satisfied: there is still exactly one ``canonical_json``, one ``canonical_bytes``
and one ``content_hash`` in the repository.

WHAT IT IS FOR. A declaration's certification identity must cover every value that can change a
verdict. The obvious way to build one — write down the keys to include — fails silently: a field
is added to the parsed structure, nobody adds it to the list, and from that moment a value that
decides PASS or FAIL sits outside the identity that is supposed to certify it. That was not
hypothesised. It was measured, twice. ``engine/construct`` projected eleven keys to bare
identifier lists, and flipping ``blocking`` on ``UCON-L-01`` — the flag its own contract reads to
choose OPEN or CLOSED — left the declaration digest byte-identical at ``192c63af…``;
``engine/recursive_knowledge`` left 101 of its 115 parsed fields outside the identity entirely.

Inversion is the remedy, and this function is how it is spelled: a dataclass field reaches the
payload unless it is explicitly excluded, so the maintenance burden falls on OMISSION rather than
on inclusion, and a new field is covered on the day it is written rather than on the day somebody
remembers it. ``UEC-L-13`` then proves by mutation, over every declaration that uses this, that
the resulting identity actually moves when the declaration's meaning moves.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping, Sequence
from typing import Any

from engine.uckp.canonical import canonical_json

#: Types :func:`canonical_payload` renders without needing to look inside them.
_SCALARS = (str, int, float, bool, type(None))


def canonical_payload(value: Any, *, exclude: Sequence[str] = ()) -> Any:
    """Render a parsed structure into a JSON-safe value, INCLUDING EVERYTHING BY DEFAULT.

    Written for one job: letting a declaration take its certification identity over its whole
    parsed self rather than over a hand-written projection of it. The distinction is not
    cosmetic. A projection is a list somebody maintains, and the failure mode is silence — a
    field is added to the parsed structure, nobody adds it to the list, and from that moment a
    value that decides PASS or FAIL sits outside the identity that is supposed to certify it.
    That defect was not hypothesised; it was measured. ``engine/construct`` projected eleven
    keys to bare identifier lists, and flipping ``blocking`` on ``UCON-L-01`` — the flag
    ``engine/construct/contract.py`` reads to choose OPEN or CLOSED — left the declaration
    digest byte-identical at ``192c63af…``.

    Inversion is the remedy: a dataclass field reaches the payload unless ``exclude`` names it,
    so the maintenance burden falls on omission rather than on inclusion, and a new field is
    covered on the day it is written rather than on the day somebody remembers it.

    ``exclude`` applies to the dataclass fields of the TOP-LEVEL value only. Excluding a name
    everywhere it occurs at any depth would make the exclusion list a wildcard whose reach
    nobody could state, and an exclusion nobody can state the reach of is not a disclosure.

    An unrenderable type raises rather than degrading to ``repr``. A ``repr`` fallback would
    encode the object's memory address into the digest on some types and its class name on
    others, so the identity would either be unstable across processes or silently collapse
    distinct values together — both worse than a fault that names the type.
    """
    excluded = frozenset(exclude)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: canonical_payload(getattr(value, field.name))
            for field in dataclasses.fields(value)
            if field.name not in excluded
        }
    return _render(value)


def _render(value: Any) -> Any:
    if isinstance(value, _SCALARS):
        return value
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return canonical_payload(value)
    if isinstance(value, Mapping):
        return {str(key): _render(item) for key, item in value.items()}
    if isinstance(value, frozenset | set):
        # Sorted on the RENDERED form: a set has no order, so an unsorted rendering would
        # give one value two digests depending on iteration order.
        return sorted((_render(item) for item in value), key=canonical_json)
    if isinstance(value, tuple | list):
        return [_render(item) for item in value]
    raise TypeError(
        f"canonical_payload cannot render {type(value).__name__!r} without guessing. Add an "
        "explicit rule rather than letting an unrenderable value reach a certification identity."
    )


__all__ = ["canonical_payload"]
