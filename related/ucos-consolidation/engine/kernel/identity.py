"""Universal Identity — deterministic, universal, open.

Engineering Rule 3: *everything shall possess identity*. The kernel mints identity as a
pure function of an identity tuple ``(metatype, namespace, natural_key)`` so the same
logical thing always resolves to the same identifier regardless of version, wall-clock,
machine, or registration order (determinism), and so two independent registrations of the
same thing collapse onto one identity.

Crucially, ``metatype`` is an **open** reference — an arbitrary registered meta-type — not
a member of any closed enumeration. The identifier remains self-describing (it carries a
short, data-derived slug of the classifying meta-type) without the identity scheme ever
constraining which concept-categories may exist. Registering a previously unknown
concept-category therefore needs no change here.

Stdlib-only; no wall-clock, RNG, or network (Universal Time/Technology independence).
"""

from __future__ import annotations

import re
from typing import Any

from engine.kernel.errors import IdentityError

# The canonical serialization primitive has exactly one definition, in UCKP Layer Zero
# (UCKP-LAW-0001 Art-13, UCKP-INV-03). ``content_digest`` is this layer's historical
# name for the digest and is kept as an alias, so no caller has to move.
from engine.uckp.canonical import canonical_json, content_hash

#: The identifier authority prefix for every kernel-minted identity.
ID_PREFIX = "UMK"

#: Length (hex chars) of the deterministic identity digest embedded in an identifier.
_DIGEST_LEN = 12

#: Maximum length of the self-describing, data-derived meta-type slug in an identifier.
_SLUG_LEN = 12

#: A segment (namespace / natural key / metatype ref) is a non-empty token free of control
#: characters and surrounding whitespace. The kernel deliberately does NOT constrain the
#: alphabet to a finite script or language (Universal Language independence): any Unicode
#: token is a valid identity segment. The only invariants are non-emptiness and the absence
#: of whitespace/control characters, which are structural, not linguistic.
_WHITESPACE_RE = re.compile(r"\s")


#: This layer's historical name for the canonical digest. An alias, not a second
#: implementation: one primitive, two names, so the rename never became a fork.
content_digest = content_hash


def normalize_segment(value: Any, *, field: str) -> str:
    """Validate and normalise an identity segment (trimmed, non-empty, whitespace-free)."""
    if not isinstance(value, str):
        raise IdentityError("identity segment must be a string", field=field, value=value)
    trimmed = value.strip()
    if not trimmed:
        raise IdentityError("identity segment must be non-empty", field=field)
    if _WHITESPACE_RE.search(trimmed):
        raise IdentityError(
            "identity segment must not contain whitespace", field=field, value=value
        )
    return trimmed


def _slug(metatype: str) -> str:
    """Derive a stable, self-describing slug from an (open) meta-type reference.

    The slug is purely cosmetic — uniqueness is guaranteed by the digest — so it may be
    any data-derived rendering. Non-alphanumeric characters collapse to nothing and the
    result is upper-cased and truncated; a meta-type that renders empty (e.g. a purely
    symbolic script) falls back to ``X`` so the identifier shape stays uniform.
    """
    folded = "".join(ch for ch in metatype.upper() if ch.isalnum() and ch.isascii())
    return (folded or "X")[:_SLUG_LEN]


def identity_tuple(metatype: Any, namespace: Any, natural_key: Any) -> tuple[str, str, str]:
    """Return the normalised identity tuple ``(metatype, namespace, natural_key)``."""
    return (
        normalize_segment(metatype, field="metatype"),
        normalize_segment(namespace, field="namespace"),
        normalize_segment(natural_key, field="natural_key"),
    )


def mint(metatype: Any, namespace: Any, natural_key: Any) -> str:
    """Compute the deterministic universal identifier for an identity tuple.

    Shape: ``UMK-<SLUG>-<12 hex>`` where the digest is the leading 12 hex chars of the
    SHA-256 over the canonical identity tuple. Version-independent: every version of the
    same thing shares one identifier.
    """
    mt, ns, key = identity_tuple(metatype, namespace, natural_key)
    digest = content_hash([mt, ns, key])
    return f"{ID_PREFIX}-{_slug(mt)}-{digest[:_DIGEST_LEN]}"


class UniversalIdentity:
    """Convenience façade over the deterministic identity functions."""

    __slots__ = ()

    prefix = ID_PREFIX

    @staticmethod
    def mint(metatype: Any, namespace: Any, natural_key: Any) -> str:
        """Return the deterministic identifier for an identity tuple."""
        return mint(metatype, namespace, natural_key)

    @staticmethod
    def tuple(metatype: Any, namespace: Any, natural_key: Any) -> tuple[str, str, str]:
        """Return the normalised identity tuple."""
        return identity_tuple(metatype, namespace, natural_key)

    @staticmethod
    def is_well_formed(identifier: Any) -> bool:
        """True iff ``identifier`` has the kernel identifier shape."""
        if not isinstance(identifier, str):
            return False
        parts = identifier.split("-")
        return (
            len(parts) == 3
            and parts[0] == ID_PREFIX
            and bool(parts[1])
            and len(parts[2]) == _DIGEST_LEN
            and all(ch in "0123456789abcdef" for ch in parts[2])
        )


__all__ = [
    "ID_PREFIX",
    "UniversalIdentity",
    "mint",
    "identity_tuple",
    "normalize_segment",
    "canonical_json",
    "content_digest",
]
