"""WP-06 — Canonical Content Form (PRJ-C2 / ACT-C2).

The versioned, technology-independent normalization over which **every** content
digest computes. It realizes **AIF-L05** ("P1 is a multihash over the versioned
Canonical Content Form; it verifies, never identifies") and gap-resolution **A/G4**
("versioned canonical form over which all hashing computes"), and supplies the
canonical bytes that WP-07 (crypto-agility) hashes with an agile algorithm set.

Design (IMP-007 §5 determinism; AX-02 derived truth is recomputed, never authored):
    * A :class:`CanonicalProfile` pins the normalization parameters (Unicode form,
      line ending, trailing-whitespace policy, key ordering). Profiles are
      **versioned** and widen **append-only** (AIF-L24 pinned parameters) — an
      existing profile is never mutated; a new profile is a new id.
    * :func:`canonical_bytes` is a **pure function** of (content, profile): identical
      content under the same profile always yields identical bytes, so the resulting
      :class:`CanonicalDigest` is stable across processes and runs.
    * The digest **verifies** content (P1) — it is never an identity (P2 is minted,
      WP-04). :meth:`CanonicalDigest.verify` recomputes and compares, so any drift in
      content or profile is detected.

This module performs no I/O and **never writes to the certified corpus** (DP-03).
"""

from __future__ import annotations

import hashlib
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from platform.foundation.contracts import canonical_json
from platform.foundation.errors import CanonicalFormError
from typing import Any

#: The default, canonical CCF profile id (pinned parameter; widens append-only).
CCF_DEFAULT_PROFILE = "ucos-ccf/1.0.0"

#: The pinned default content-digest algorithm for the CCF (WP-07 makes it agile).
CCF_DIGEST_ALGORITHM = "sha256"

_ALLOWED_UNICODE_FORMS = frozenset({"NFC", "NFD", "NFKC", "NFKD"})
_ALLOWED_NEWLINES = frozenset({"\n", "\r\n"})


@dataclass(frozen=True, slots=True)
class CanonicalProfile:
    """The pinned normalization parameters of a Canonical Content Form (A/G4).

    Immutable and versioned: two artifacts hashed under the same profile compare
    meaningfully, and a profile is never mutated in place — a change is a new
    ``profile_id`` (AIF-L24 pinned parameters widen append-only).
    """

    profile_id: str
    unicode_form: str = "NFC"
    newline: str = "\n"
    strip_trailing_whitespace: bool = True
    ensure_trailing_newline: bool = False
    sort_keys: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not self.profile_id:
            raise CanonicalFormError("canonical profile id is required")
        if self.unicode_form not in _ALLOWED_UNICODE_FORMS:
            raise CanonicalFormError(
                "unsupported unicode normalization form",
                unicode_form=self.unicode_form,
            )
        if self.newline not in _ALLOWED_NEWLINES:
            raise CanonicalFormError("unsupported newline", newline=repr(self.newline))

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "unicode_form": self.unicode_form,
            "newline": self.newline,
            "strip_trailing_whitespace": self.strip_trailing_whitespace,
            "ensure_trailing_newline": self.ensure_trailing_newline,
            "sort_keys": self.sort_keys,
        }


#: The canonical default profile instance.
DEFAULT_PROFILE = CanonicalProfile(CCF_DEFAULT_PROFILE)


class ProfileRegistry:
    """An append-only registry of versioned canonical profiles (AIF-L24)."""

    __slots__ = ("_profiles",)

    def __init__(self) -> None:
        self._profiles: dict[str, CanonicalProfile] = {}
        self.register(DEFAULT_PROFILE)

    def register(self, profile: CanonicalProfile) -> CanonicalProfile:
        """Register a profile; an existing id is never overwritten (append-only)."""
        if not isinstance(profile, CanonicalProfile):
            raise CanonicalFormError("register expects a CanonicalProfile")
        existing = self._profiles.get(profile.profile_id)
        if existing is not None and existing != profile:
            raise CanonicalFormError(
                "canonical profile id already registered with different parameters",
                profile_id=profile.profile_id,
            )
        self._profiles[profile.profile_id] = profile
        return profile

    def get(self, profile_id: str) -> CanonicalProfile:
        profile = self._profiles.get(profile_id)
        if profile is None:
            raise CanonicalFormError("no such canonical profile", profile_id=profile_id)
        return profile

    def __contains__(self, profile_id: str) -> bool:
        return profile_id in self._profiles

    @property
    def profile_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._profiles))


def _resolve_profile(profile: CanonicalProfile | None) -> CanonicalProfile:
    if profile is None:
        return DEFAULT_PROFILE
    if not isinstance(profile, CanonicalProfile):
        raise CanonicalFormError("profile must be a CanonicalProfile")
    return profile


def normalize_text(text: str, profile: CanonicalProfile | None = None) -> str:
    """Normalize free text to its canonical form under ``profile`` (deterministic).

    Applies Unicode normalization, line-ending normalization, optional
    trailing-whitespace stripping, and an optional trailing newline — so semantically
    identical text always canonicalizes identically.
    """
    prof = _resolve_profile(profile)
    if not isinstance(text, str):
        raise CanonicalFormError("normalize_text expects a str")
    result = unicodedata.normalize(prof.unicode_form, text)
    # Normalize all line endings to LF first, then to the profile's newline.
    result = result.replace("\r\n", "\n").replace("\r", "\n")
    if prof.strip_trailing_whitespace:
        result = "\n".join(line.rstrip() for line in result.split("\n"))
    if prof.ensure_trailing_newline and result and not result.endswith("\n"):
        result += "\n"
    if prof.newline != "\n":
        result = result.replace("\n", prof.newline)
    return result


def _canonical_structure(value: Any, profile: CanonicalProfile) -> Any:
    """Recursively reduce a structure to a deterministically-ordered JSON value."""
    if isinstance(value, str):
        return unicodedata.normalize(profile.unicode_form, value)
    if isinstance(value, Mapping):
        # json.dumps(sort_keys=True) provides the deterministic key ordering.
        return {str(k): _canonical_structure(v, profile) for k, v in value.items()}
    if isinstance(value, set | frozenset):
        # A set has no intrinsic order — sort by canonical encoding for determinism.
        items = [_canonical_structure(v, profile) for v in value]
        return sorted(items, key=lambda item: canonical_json(item))
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [_canonical_structure(v, profile) for v in value]
    return value


def canonical_string(content: Any, profile: CanonicalProfile | None = None) -> str:
    """Return the canonical textual form of ``content`` (text or structured)."""
    prof = _resolve_profile(profile)
    if isinstance(content, str):
        return normalize_text(content, prof)
    if isinstance(content, bytes | bytearray):
        raise CanonicalFormError("use canonical_bytes for raw byte content")
    try:
        return canonical_json(_canonical_structure(content, prof))
    except TypeError as exc:
        raise CanonicalFormError("content is not canonically serializable") from exc


def canonical_bytes(content: Any, profile: CanonicalProfile | None = None) -> bytes:
    """Return the canonical byte encoding of ``content`` under ``profile``.

    Raw ``bytes`` are already canonical and returned verbatim; text is normalized and
    UTF-8 encoded; structured content is deterministically ordered and JSON-encoded.
    """
    if isinstance(content, bytes | bytearray):
        return bytes(content)
    return canonical_string(content, profile).encode("utf-8")


@dataclass(frozen=True, slots=True)
class CanonicalDigest:
    """The canonical metadata + P1 content digest over a Canonical Content Form.

    Carries the profile it was computed under, the algorithm, the digest value, and
    the canonical byte length. It **verifies** content; it never identifies it
    (AIF-L05). :meth:`verify` recomputes over the same profile and compares.
    """

    profile_id: str
    algorithm: str
    value: str
    byte_length: int

    def verify(self, content: Any, profile: CanonicalProfile | None = None) -> bool:
        """Return True iff ``content`` recomputes to this digest under its profile."""
        prof = _resolve_profile(profile)
        if prof.profile_id != self.profile_id:
            return False
        recomputed = content_digest(content, prof)
        return (
            recomputed.value == self.value
            and recomputed.byte_length == self.byte_length
            and recomputed.algorithm == self.algorithm
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "algorithm": self.algorithm,
            "value": self.value,
            "byte_length": self.byte_length,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CanonicalDigest:
        if not isinstance(data, Mapping):
            raise CanonicalFormError("digest record must be a mapping")
        try:
            return cls(
                profile_id=data["profile_id"],
                algorithm=data["algorithm"],
                value=data["value"],
                byte_length=int(data["byte_length"]),
            )
        except (KeyError, TypeError) as exc:
            raise CanonicalFormError("digest record is missing required fields") from exc


def content_digest(content: Any, profile: CanonicalProfile | None = None) -> CanonicalDigest:
    """Compute the pinned-algorithm P1 content digest over the CCF of ``content``.

    Deterministic: identical content under the same profile yields an identical
    :class:`CanonicalDigest`. WP-07 wraps this with an agile multihash algorithm set;
    here the pinned default (:data:`CCF_DIGEST_ALGORITHM`) is used.
    """
    prof = _resolve_profile(profile)
    data = canonical_bytes(content, prof)
    value = hashlib.new(CCF_DIGEST_ALGORITHM, data).hexdigest()
    return CanonicalDigest(
        profile_id=prof.profile_id,
        algorithm=CCF_DIGEST_ALGORITHM,
        value=value,
        byte_length=len(data),
    )


__all__ = [
    "CCF_DEFAULT_PROFILE",
    "CCF_DIGEST_ALGORITHM",
    "DEFAULT_PROFILE",
    "CanonicalProfile",
    "ProfileRegistry",
    "CanonicalDigest",
    "normalize_text",
    "canonical_string",
    "canonical_bytes",
    "content_digest",
]
