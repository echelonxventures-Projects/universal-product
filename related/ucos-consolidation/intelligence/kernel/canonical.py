"""Deterministic serialization + sealing — re-exported from the canonical owner.

``intelligence.rie.canonical`` already owns the repository's canonical JSON
encoding, SHA-256 helpers, ``content_hash`` (self-excluding) and ``sealed``.
Re-implementing them here would create a second source of truth for the
determinism guarantee — precisely the duplication anti-pattern (UCKO-ANTI-0001).
The kernel therefore re-exports the owner and adds only what does not yet exist:
a normalizer used by the zero-duplication detector.
"""

from __future__ import annotations

import re
import unicodedata

from intelligence.rie.canonical import (
    canonical_json,
    content_hash,
    sealed,
    sha256_bytes,
    sha256_file,
    sha256_text,
)

_WS = re.compile(r"\s+")
_NON_WORD = re.compile(r"[^a-z0-9]+")

#: The shortest normalized token run treated as a canonical-prose fingerprint.
#: Short enough to catch a copied clause, long enough that structural labels
#: ("Abstract", "Prior Art") can never collide with a canonical statement.
SHINGLE_WORDS = 8


def normalize_prose(text: str) -> str:
    """Fold prose to a comparison form: NFKC, lower-case, whitespace-collapsed."""
    folded = unicodedata.normalize("NFKC", text).strip().lower()
    return _WS.sub(" ", folded)


def slug(text: str) -> str:
    """Deterministic, whitespace-free slug suitable for a registry natural key."""
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return _NON_WORD.sub("-", folded.lower()).strip("-") or "unnamed"


def shingles(text: str, size: int = SHINGLE_WORDS) -> frozenset[str]:
    """Word shingles of the normalized prose — the duplication fingerprint set.

    Two texts sharing a shingle share a verbatim run of ``size`` words, which is
    the operational definition of *copied content* used by the publication
    validator (a reference-resolved block is exempt; an authored field is not).
    """
    words = normalize_prose(text).split()
    if len(words) < size:
        return frozenset()
    return frozenset(" ".join(words[i : i + size]) for i in range(len(words) - size + 1))


__all__ = [
    "SHINGLE_WORDS",
    "canonical_json",
    "content_hash",
    "normalize_prose",
    "sealed",
    "sha256_bytes",
    "sha256_file",
    "sha256_text",
    "shingles",
    "slug",
]
