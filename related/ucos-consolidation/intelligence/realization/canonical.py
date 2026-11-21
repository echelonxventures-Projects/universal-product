"""URI-000001 — deterministic serialization + content addressing.

The determinism guarantee of the whole subsystem rests here. Rather than introduce a
second hashing discipline, this module **composes** the canonical encoding already used
by the UKDA canonical knowledge store (:mod:`engine.knowledge.model`) — the same
encoding that produced the ``content_sha256`` of every canonical object URI reads. One
repository, one hash discipline (UCKO-PRIN-0001 Knowledge Once Principle).

Two encodings exist, deliberately:

* :func:`canonical_json` — compact, sorted, separator-stable. The *hashing* encoding.
* :func:`document_json` — indented, sorted, newline-terminated. The *file* encoding,
  identical to the store's own on-disk form so a round-trip is byte-stable.

Nothing in this module reads a clock. Identity is content, never time.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from engine.knowledge.model import canonical_json, content_hash

#: The field a sealed payload carries its own hash in.
SEAL_FIELD = "content_sha256"


def document_json(payload: Any) -> str:
    """Return the deterministic on-disk JSON form (indented, sorted, newline-ended)."""
    return json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def sha256_text(text: str) -> str:
    """Return the SHA-256 hex digest of ``text`` encoded as UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def seal_of(payload: Mapping[str, Any]) -> str:
    """Return the content hash of ``payload`` with any pre-existing seal removed.

    Excluding the seal field lets a payload embed its own hash without the hash
    depending on itself.
    """
    return content_hash({k: v for k, v in payload.items() if k != SEAL_FIELD})


def sealed(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy of ``payload`` carrying its own :data:`SEAL_FIELD`."""
    out = dict(payload)
    out[SEAL_FIELD] = seal_of(out)
    return out


def verify_seal(payload: Mapping[str, Any]) -> bool:
    """Return True iff a sealed payload's embedded hash matches a recomputation."""
    stored = payload.get(SEAL_FIELD)
    return bool(stored) and stored == seal_of(payload)


def short_seal(seal: str, *, width: int = 12) -> str:
    """Return a stable short form of a seal, used to build deterministic identifiers."""
    return seal[:width]


__all__ = [
    "SEAL_FIELD",
    "canonical_json",
    "content_hash",
    "document_json",
    "sha256_text",
    "seal_of",
    "sealed",
    "verify_seal",
    "short_seal",
]
