"""UOBC-000001 Part 03 — the append-only birth ledger, keyed by identity.

The one structural difference from ``00-BOOK/DATA/id-ledger.json`` is the key. That
ledger holds ``by_path`` and ``by_object``; this one holds ``births`` keyed by
``universal_id``. A path key is rewritten when a file moves, which is why the older
architecture had to treat a rename as retire-and-reissue. An identity key cannot be
rewritten by a move at all, so ``UOBC-L-07`` (evolution under one identity) holds
here by construction rather than by discipline.

This file deliberately holds **no** ``category_seq``. That token is the declared
``mint_marker`` in ``00-BOOK/DATA/constitutional-authority-alignment.json``, and
``CAA-INV-04`` recognises a second identity authority by exactly that: "a mint is
recognised by the counter it advances". Birth identity is derived rather than counted,
so there is no counter to hold, and this ledger is a *binding* of UCKP Article 5
rather than a rival to it.

Append-only means append-only: :func:`append` refuses to overwrite an existing
identity with different content, and :func:`supersede` records a new generation
alongside the old rather than in place of it.
"""

from __future__ import annotations

import json
import os
from typing import Any

from engine.object_birth.model import BirthError, BirthRecord

#: The declared ledger schema token. Bumping it is an amendment, not a migration.
LEDGER_SCHEMA = "ucos-object-birth-ledger"

#: Forbidden top-level key: holding it would make this file a second mint.
FORBIDDEN_MINT_MARKER = "category_seq"


def empty_ledger() -> dict[str, Any]:
    """Return a well-formed empty ledger."""
    return {
        "schema": LEDGER_SCHEMA,
        "version": "1.0",
        "authority": (
            "NONE — DERIVED TRUTH. A persistence binding of UCKP-ART-05 "
            "(engine/uckp/identity.py). Holds no counter and issues no repository serial."
        ),
        "keyed_by": "universal_id",
        "births": {},
        "supersessions": [],
    }


def load(path: str) -> dict[str, Any]:
    """Load the ledger at ``path``, returning an empty one when absent.

    Raises:
        BirthError: the file exists but is not a usable ledger, or it holds the
            forbidden mint marker.
    """
    if not os.path.isfile(path):
        return empty_ledger()
    try:
        with open(path, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise BirthError("birth ledger is unreadable", subject=path) from exc
    if not isinstance(doc, dict):
        raise BirthError("birth ledger is not a mapping", subject=path)
    if FORBIDDEN_MINT_MARKER in doc:
        raise BirthError(
            f"birth ledger holds {FORBIDDEN_MINT_MARKER!r}, which would make it a second mint",
            subject=path,
        )
    if doc.get("schema") != LEDGER_SCHEMA:
        raise BirthError(
            f"birth ledger schema is not {LEDGER_SCHEMA!r}", subject=str(doc.get("schema"))
        )
    if not isinstance(doc.get("births"), dict):
        raise BirthError("birth ledger holds no births mapping", subject=path)
    return doc


def records(ledger: dict[str, Any]) -> tuple[BirthRecord, ...]:
    """Return every birth record the ledger holds, in identity order."""
    out = []
    for universal_id, entry in sorted(ledger["births"].items()):
        if not isinstance(entry, dict):
            raise BirthError("birth entry is not a mapping", subject=universal_id)
        merged = {**entry, "universal_id": universal_id}
        out.append(BirthRecord.from_dict(merged))
    return tuple(out)


def append(ledger: dict[str, Any], record: BirthRecord) -> dict[str, Any]:
    """Return a new ledger with ``record`` appended.

    Idempotent for an identical re-append, which makes replay safe.

    Raises:
        BirthError: the identity is already present with different content. That is
            an overwrite, and the ledger is append-only.
    """
    body = record.to_dict()
    identity = body.pop("universal_id")
    existing = ledger["births"].get(identity)
    if existing is not None and existing != body:
        raise BirthError(
            "identity already born with different content; the ledger is append-only",
            subject=identity,
        )
    births = {**ledger["births"], identity: body}
    return {**ledger, "births": births}


def supersede(ledger: dict[str, Any], record: BirthRecord, *, reason: str) -> dict[str, Any]:
    """Record an evolution of an already-born identity, preserving the prior state.

    The prior body is appended to ``supersessions`` and the current body replaced, so
    history grows and nothing is lost. The identity itself is unchanged — that is the
    invariant this function exists to make observable.

    Raises:
        BirthError: the identity has not been born, or the supersession would change
            the identity.
    """
    body = record.to_dict()
    identity = body.pop("universal_id")
    prior = ledger["births"].get(identity)
    if prior is None:
        raise BirthError("cannot supersede an identity that was never born", subject=identity)
    history = list(ledger.get("supersessions", []))
    history.append({"universal_id": identity, "reason": reason, "superseded": prior})
    births = {**ledger["births"], identity: body}
    return {**ledger, "births": births, "supersessions": history}


def dumps(ledger: dict[str, Any]) -> str:
    """Return the canonical serialisation: sorted keys, fixed separators, trailing newline.

    Byte-stability is required, not cosmetic — the ledger is replay-compared.
    """
    return json.dumps(ledger, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def save(path: str, ledger: dict[str, Any]) -> None:
    """Write ``ledger`` to ``path`` in canonical form."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(dumps(ledger))
