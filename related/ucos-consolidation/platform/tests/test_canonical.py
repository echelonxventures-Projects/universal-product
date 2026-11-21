"""WP-06 — Canonical Content Form tests (PRJ-C2 · ACT-C2).

Covers the versioned, technology-independent normalization over which every P1
content digest computes: pinned canonical profiles (append-only), deterministic text
+ structural normalization, canonical byte encoding, the pinned-algorithm content
digest, digest verification, and canonical metadata (AIF-L05 · A/G4 · AIF-L24).
"""

from __future__ import annotations

import hashlib
from platform.foundation.canonical import (
    CCF_DEFAULT_PROFILE,
    CCF_DIGEST_ALGORITHM,
    DEFAULT_PROFILE,
    CanonicalDigest,
    CanonicalProfile,
    ProfileRegistry,
    canonical_bytes,
    canonical_string,
    content_digest,
    normalize_text,
)
from platform.foundation.contracts import canonical_json
from platform.foundation.errors import CanonicalFormError

import pytest

# --------------------------------------------------------------------------------
# CanonicalProfile — pinned, validated parameters
# --------------------------------------------------------------------------------


def test_default_profile_shape():
    assert DEFAULT_PROFILE.profile_id == CCF_DEFAULT_PROFILE
    assert DEFAULT_PROFILE.unicode_form == "NFC"
    assert DEFAULT_PROFILE.to_dict()["profile_id"] == CCF_DEFAULT_PROFILE


def test_profile_validation():
    with pytest.raises(CanonicalFormError):
        CanonicalProfile("")
    with pytest.raises(CanonicalFormError):
        CanonicalProfile("p", unicode_form="NFZ")
    with pytest.raises(CanonicalFormError):
        CanonicalProfile("p", newline="\r")


# --------------------------------------------------------------------------------
# ProfileRegistry — append-only versioned profiles (AIF-L24)
# --------------------------------------------------------------------------------


def test_registry_seeds_default_and_registers_new():
    reg = ProfileRegistry()
    assert CCF_DEFAULT_PROFILE in reg
    assert reg.get(CCF_DEFAULT_PROFILE) == DEFAULT_PROFILE
    v2 = CanonicalProfile("ucos-ccf/1.1.0", ensure_trailing_newline=True)
    reg.register(v2)
    assert reg.profile_ids == ("ucos-ccf/1.0.0", "ucos-ccf/1.1.0")
    # Idempotent re-registration of an identical profile is allowed.
    reg.register(v2)


def test_registry_rejects_conflicting_and_unknown():
    reg = ProfileRegistry()
    with pytest.raises(CanonicalFormError):
        reg.register("not-a-profile")  # type: ignore[arg-type]
    conflicting = CanonicalProfile(CCF_DEFAULT_PROFILE, strip_trailing_whitespace=False)
    with pytest.raises(CanonicalFormError):
        reg.register(conflicting)  # same id, different params
    with pytest.raises(CanonicalFormError):
        reg.get("ucos-ccf/9.9.9")


# --------------------------------------------------------------------------------
# Text normalization — deterministic
# --------------------------------------------------------------------------------


def test_normalize_text_line_endings_and_trailing_ws():
    text = "line one  \r\nline two\t\rline three   "
    result = normalize_text(text)
    assert result == "line one\nline two\nline three"


def test_normalize_text_unicode_form():
    # 'é' composed vs decomposed normalize to the same NFC form.
    composed = "e\u0301"  # e + combining acute
    assert normalize_text(composed) == "\u00e9"


def test_normalize_text_trailing_newline_and_custom_newline():
    prof = CanonicalProfile("ucos-ccf/crlf", newline="\r\n", ensure_trailing_newline=True)
    assert normalize_text("a\nb", prof) == "a\r\nb\r\n"
    # ensure_trailing_newline is a no-op for empty text.
    assert normalize_text("", prof) == ""


def test_normalize_text_rejects_non_str():
    with pytest.raises(CanonicalFormError):
        normalize_text(123)  # type: ignore[arg-type]


# --------------------------------------------------------------------------------
# Canonical string / bytes — structural determinism
# --------------------------------------------------------------------------------


def test_canonical_string_orders_mappings_and_sets():
    payload = {"b": 1, "a": {"z": [3, 2, 1], "y": {2, 1, 3}}}
    result = canonical_string(payload)
    # keys sorted; set canonicalized to a sorted list; list order preserved.
    assert result == canonical_json({"a": {"y": [1, 2, 3], "z": [3, 2, 1]}, "b": 1})


def test_canonical_string_normalizes_unicode_in_values():
    assert canonical_string({"k": "e\u0301"}) == canonical_json({"k": "\u00e9"})


def test_canonical_string_rejects_bytes_and_nonserializable():
    with pytest.raises(CanonicalFormError):
        canonical_string(b"bytes")
    with pytest.raises(CanonicalFormError):
        canonical_string({"k": object()})  # not JSON serializable


def test_canonical_bytes_variants():
    assert canonical_bytes(b"raw") == b"raw"
    assert canonical_bytes(bytearray(b"raw")) == b"raw"
    assert canonical_bytes("a  \r\nb") == b"a\nb"
    assert canonical_bytes({"a": 1}) == canonical_json({"a": 1}).encode("utf-8")


# --------------------------------------------------------------------------------
# Content digest + verification (AIF-L05)
# --------------------------------------------------------------------------------


def test_content_digest_is_deterministic_and_pinned():
    d1 = content_digest({"a": 1, "b": 2})
    d2 = content_digest({"b": 2, "a": 1})  # key order irrelevant
    assert d1 == d2
    assert d1.algorithm == CCF_DIGEST_ALGORITHM
    assert d1.profile_id == CCF_DEFAULT_PROFILE
    expected = hashlib.sha256(canonical_bytes({"a": 1, "b": 2})).hexdigest()
    assert d1.value == expected
    assert d1.byte_length == len(canonical_bytes({"a": 1, "b": 2}))


def test_digest_verifies_content():
    digest = content_digest("hello  \r\nworld")
    assert digest.verify("hello\nworld") is True  # canonical-equivalent content
    assert digest.verify("different") is False


def test_digest_verify_wrong_profile_returns_false():
    prof2 = CanonicalProfile("ucos-ccf/alt", strip_trailing_whitespace=False)
    digest = content_digest("x")  # default profile
    assert digest.verify("x", prof2) is False


def test_digest_roundtrip_and_errors():
    digest = content_digest({"k": "v"})
    assert CanonicalDigest.from_dict(digest.to_dict()) == digest
    with pytest.raises(CanonicalFormError):
        CanonicalDigest.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(CanonicalFormError):
        CanonicalDigest.from_dict({"profile_id": "p"})  # missing fields


def test_profile_none_and_invalid_resolution():
    # None resolves to the default profile.
    assert content_digest("a", None) == content_digest("a")
    with pytest.raises(CanonicalFormError):
        canonical_bytes("a", "not-a-profile")  # type: ignore[arg-type]


def test_different_profiles_yield_different_digests():
    keep_ws = CanonicalProfile("ucos-ccf/keep-ws", strip_trailing_whitespace=False)
    stripped = content_digest("trailing   ")
    kept = content_digest("trailing   ", keep_ws)
    assert stripped.value != kept.value
    assert stripped.profile_id != kept.profile_id
