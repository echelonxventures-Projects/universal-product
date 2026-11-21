"""Deterministic canonical serialization + content hashing.

The determinism guarantee of the whole engine rests here: a canonical JSON
encoding (sorted keys, stable separators, UTF-8, trailing newline) plus a
content hash computed over that canonical form with the ``content_hash`` field
excluded. Identical inputs ⇒ identical bytes ⇒ identical hash.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

_HASH_FIELD = "content_hash"


def canonical_json(obj: Any) -> str:
    """Return the canonical, deterministic JSON text for *obj*."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Content hash of a file, or a stable sentinel when it is absent."""
    if not path.exists():
        return "absent"
    return sha256_bytes(path.read_bytes())


def content_hash(payload: dict[str, Any]) -> str:
    """Hash a payload with any pre-existing ``content_hash`` field removed.

    This lets an output embed its own hash without the hash depending on itself.
    """
    without = {k: v for k, v in payload.items() if k != _HASH_FIELD}
    return sha256_text(canonical_json(without))


def sealed(payload: dict[str, Any]) -> dict[str, Any]:
    """Return *payload* with a self-describing ``content_hash`` embedded."""
    out = dict(payload)
    out[_HASH_FIELD] = content_hash(out)
    return out
