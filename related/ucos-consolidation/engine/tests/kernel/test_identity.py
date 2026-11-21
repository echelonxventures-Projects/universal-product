"""Tests for Universal Identity (deterministic, open, language-independent)."""

from __future__ import annotations

import pytest

from engine.kernel.errors import IdentityError
from engine.kernel.identity import (
    UniversalIdentity,
    canonical_json,
    content_digest,
    identity_tuple,
    mint,
    normalize_segment,
)


def test_mint_is_deterministic_and_version_independent():
    a = mint("Capability", "umk.demo", "alpha")
    b = mint("Capability", "umk.demo", "alpha")
    assert a == b
    assert a.startswith("UMK-CAPABILITY-")
    assert UniversalIdentity.is_well_formed(a)


def test_mint_differs_by_any_segment():
    base = mint("Capability", "umk.demo", "alpha")
    assert base != mint("Contract", "umk.demo", "alpha")
    assert base != mint("Capability", "umk.other", "alpha")
    assert base != mint("Capability", "umk.demo", "beta")


def test_identity_is_language_independent():
    # A non-Latin / symbolic natural key is a valid identity segment; the slug falls back
    # to a uniform shape while the digest guarantees uniqueness.
    ident = mint("语言族", "umk.demo", "字符")
    assert UniversalIdentity.is_well_formed(ident)
    assert ident.startswith("UMK-X-")  # slug folds to the fallback for a non-ASCII metatype


def test_normalize_segment_rejects_empty_and_whitespace():
    with pytest.raises(IdentityError):
        normalize_segment("   ", field="x")
    with pytest.raises(IdentityError):
        normalize_segment("has space", field="x")
    with pytest.raises(IdentityError):
        normalize_segment(123, field="x")
    assert normalize_segment("  ok  ", field="x") == "ok"


def test_identity_tuple_normalises():
    assert identity_tuple("  A ", " ns ", " k ") == ("A", "ns", "k")


def test_canonical_json_is_stable_and_digest_matches():
    payload = {"b": 2, "a": 1}
    assert canonical_json(payload) == '{"a":1,"b":2}'
    assert content_digest(payload) == content_digest({"a": 1, "b": 2})


def test_is_well_formed_negative_cases():
    assert not UniversalIdentity.is_well_formed(123)
    assert not UniversalIdentity.is_well_formed("nope")
    assert not UniversalIdentity.is_well_formed("UMK-SLUG-zzzz")  # non-hex / wrong length


def test_facade_tuple_and_mint_agree():
    assert UniversalIdentity.mint("A", "ns", "k") == mint("A", "ns", "k")
    assert UniversalIdentity.tuple("A", "ns", "k") == ("A", "ns", "k")
    assert UniversalIdentity.prefix == "UMK"
