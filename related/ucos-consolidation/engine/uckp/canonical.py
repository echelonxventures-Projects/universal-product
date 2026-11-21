"""UCKP Layer Zero — the single canonical serialization primitive (UCKP-LAW-0001 §Art-13).

Every content digest anywhere in UCOS Ω∞ is derived through exactly these two
functions. Before Layer Zero existed the primitive was reimplemented, byte for byte,
in nine modules:

    ``engine.acceptance.contracts``, ``engine.certification.contracts``,
    ``engine.discovery.contracts``, ``engine.kernel.identity``,
    ``engine.knowledge.model``, ``engine.registry.universal.identity``,
    ``engine.universal_certification.contracts``, ``platform.foundation.contracts``
    and ``platform.universal_provider.contracts``.

Nine byte-identical definitions are nine competing authorities over the same knowledge,
which UCKP Article 3 (Zero Duplication) forbids. Each of those modules now re-exports
from here and their public names are unchanged, so no consumer had to move. Two of them
— the ``kernel`` and ``registry.universal`` identity modules — historically called the
digest ``content_digest``; that name survives as an alias, because renaming a primitive
is not a reason to fork it.

The claim that the primitive exists exactly once is not left to this docstring.
:meth:`engine.uckp.validation.ConstitutionalValidator._probe_zero_duplication` parses
every module in ``engine`` and ``platform`` and reports any module-level
``canonical_json``, ``canonical_bytes`` or ``content_hash`` that implements the digest
itself rather than forwarding to this module. A prose assertion of non-duplication is
exactly the kind of claim that quietly stops being true.

This module is the *bottom* of the dependency order: it imports the standard
library only — not even the Layer Zero error taxonomy — so that any module in the
repository, at any layer, can depend on it without creating a cycle. That property
is what makes "everything depends on Layer Zero, nothing bypasses it" mechanically
true rather than aspirational.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

#: The digest algorithm every UCKO identity, seal and proof is computed with.
DIGEST_ALGORITHM = "sha256"

#: The canonical JSON profile identifier, so a digest is always attributable to
#: the normalization that produced it (a digest that cannot name its profile is
#: not replayable across future serializers).
CANONICAL_PROFILE = "ucos-uckp-canonical-json/1.0.0"


def canonical_json(payload: Any) -> str:
    """Return a deterministic canonical JSON encoding (sorted keys, compact).

    The single serialization used for every content hash in UCOS Ω∞, so hashing is
    stable across processes, machines, storage media and runs (IMP-007 §5):
    identical structures always encode to identical bytes.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_bytes(payload: Any) -> bytes:
    """Return the UTF-8 encoding of :func:`canonical_json` — the bytes that are hashed."""
    return canonical_json(payload).encode("utf-8")


def content_hash(payload: Any) -> str:
    """Return the SHA-256 hex digest of the canonical encoding of ``payload``."""
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def digests_match(left: Any, right: Any) -> bool:
    """True iff two payloads are canonically identical (the replay equality test)."""
    return content_hash(left) == content_hash(right)


__all__ = [
    "CANONICAL_PROFILE",
    "DIGEST_ALGORITHM",
    "canonical_bytes",
    "canonical_json",
    "content_hash",
    "digests_match",
]
