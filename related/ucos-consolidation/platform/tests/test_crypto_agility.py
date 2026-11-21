"""WP-07 — Crypto Agility tests (PRJ-C2 · ACT-C2).

Covers algorithm-tagged multihashes, the append-only algorithm registry, crypto
version negotiation, the agile digest-set abstraction over the Canonical Content
Form (WP-06), witnessed rollover, post-rollover deprecation, and forward
compatibility with algorithms this runtime cannot compute (AIF-L22 · A/G5).
"""

from __future__ import annotations

import hashlib
from platform.foundation.canonical import CanonicalProfile, canonical_bytes
from platform.foundation.crypto_agility import (
    CRYPTO_REGISTRY_FORMAT,
    DEFAULT_ALGORITHMS,
    AlgorithmRegistry,
    AlgorithmStatus,
    DigestSet,
    HashAlgorithm,
    Multihash,
    compute_multihash,
    default_algorithm_registry,
)
from platform.foundation.errors import AlgorithmNegotiationError, CryptoAgilityError

import pytest

# --------------------------------------------------------------------------------
# HashAlgorithm
# --------------------------------------------------------------------------------


def test_hash_algorithm_create_resolves_size():
    algo = HashAlgorithm.create("sha256", 10)
    assert algo.digest_size == 32
    assert algo.to_dict() == {"name": "sha256", "strength": 10, "digest_size": 32}


def test_hash_algorithm_validation():
    with pytest.raises(CryptoAgilityError):
        HashAlgorithm.create("", 10)
    with pytest.raises(CryptoAgilityError):
        HashAlgorithm.create("sha256", 0)
    with pytest.raises(CryptoAgilityError):
        HashAlgorithm.create("no-such-algo", 10)


# --------------------------------------------------------------------------------
# Multihash — self-describing, future-compatible
# --------------------------------------------------------------------------------


def test_multihash_tag_parse_roundtrip():
    mh = Multihash("sha256", "abcd")
    assert mh.tag == "sha256:abcd"
    assert Multihash.parse(mh.tag) == mh
    assert Multihash.from_dict(mh.to_dict()) == mh


def test_multihash_validation():
    with pytest.raises(CryptoAgilityError):
        Multihash("", "v")
    with pytest.raises(CryptoAgilityError):
        Multihash("sha:256", "v")  # separator in algorithm
    with pytest.raises(CryptoAgilityError):
        Multihash("sha256", "")
    with pytest.raises(CryptoAgilityError):
        Multihash.parse("no-separator")
    with pytest.raises(CryptoAgilityError):
        Multihash.parse(123)  # type: ignore[arg-type]
    with pytest.raises(CryptoAgilityError):
        Multihash.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(CryptoAgilityError):
        Multihash.from_dict({"algorithm": "sha256"})  # missing value


def test_multihash_verify_and_future_algorithm():
    mh = compute_multihash({"a": 1}, "sha256")
    data = canonical_bytes({"a": 1})
    assert mh.verify_bytes(data) is True
    assert mh.value == hashlib.sha256(data).hexdigest()
    # A digest for an algorithm this runtime cannot compute is still representable,
    # but verification fails closed (future compatibility, AIF-L22).
    future = Multihash("sha4-future", "deadbeef")
    assert future.tag == "sha4-future:deadbeef"
    with pytest.raises(CryptoAgilityError):
        future.verify_bytes(data)


def test_compute_multihash_uses_canonical_form():
    # Key order is irrelevant because hashing is over the CCF (WP-06).
    assert compute_multihash({"a": 1, "b": 2}, "sha256") == compute_multihash(
        {"b": 2, "a": 1}, "sha256"
    )


# --------------------------------------------------------------------------------
# AlgorithmRegistry — append-only + agile lifecycle
# --------------------------------------------------------------------------------


def test_default_registry_seeds_algorithms():
    reg = default_algorithm_registry()
    assert len(reg) == len(DEFAULT_ALGORITHMS)
    for name, _ in DEFAULT_ALGORITHMS:
        assert name in reg
        assert reg.status(name) is AlgorithmStatus.ACTIVE
    # strongest active is sha512 (highest strength).
    assert reg.preferred().name == "sha512"
    assert reg.export()["registry_format"] == CRYPTO_REGISTRY_FORMAT


def test_registry_register_idempotent_and_conflict():
    reg = AlgorithmRegistry(seed_defaults=False)
    algo = HashAlgorithm.create("sha256", 10)
    reg.register(algo)
    reg.register(algo)  # idempotent
    assert len(reg) == 1
    with pytest.raises(CryptoAgilityError):
        reg.register("not-an-algo")  # type: ignore[arg-type]
    with pytest.raises(CryptoAgilityError):
        reg.register(HashAlgorithm.create("sha256", 99))  # same name, diff params


def test_registry_get_and_status_errors():
    reg = default_algorithm_registry()
    with pytest.raises(CryptoAgilityError):
        reg.get("missing")
    with pytest.raises(CryptoAgilityError):
        reg.status("missing")


def test_empty_registry_preferred_fails_closed():
    reg = AlgorithmRegistry(seed_defaults=False)
    with pytest.raises(AlgorithmNegotiationError):
        reg.preferred()


# --------------------------------------------------------------------------------
# Crypto version negotiation
# --------------------------------------------------------------------------------


def test_negotiate_picks_strongest_common():
    reg = default_algorithm_registry()
    # peer supports sha256 + sha3_256 ⇒ strongest common is sha3_256.
    assert reg.negotiate(["sha256", "sha3_256"]).name == "sha3_256"
    assert reg.negotiate(["sha256"]).name == "sha256"


def test_negotiate_fails_closed_without_common():
    reg = default_algorithm_registry()
    with pytest.raises(AlgorithmNegotiationError):
        reg.negotiate(["md5", "blake2b"])


# --------------------------------------------------------------------------------
# Witnessed rollover + post-rollover deprecation (AIF-L22)
# --------------------------------------------------------------------------------


def test_rollover_introduces_active_algorithm():
    reg = AlgorithmRegistry(seed_defaults=False)
    reg.register(HashAlgorithm.create("sha256", 10))
    record = reg.rollover("sha512", 30, witness="crypto-board")
    assert record.witness == "crypto-board"
    assert reg.status("sha512") is AlgorithmStatus.ACTIVE
    assert reg.rollovers == (record,)
    assert reg.preferred().name == "sha512"
    # The rollover is captured in the (secret-free) registry export.
    exported = reg.export()
    assert exported["rollovers"] == [
        {"algorithm": "sha512", "strength": 30, "witness": "crypto-board"}
    ]
    assert {a["name"]: a["status"] for a in exported["algorithms"]} == {
        "sha256": "active",
        "sha512": "active",
    }


def test_rollover_error_paths():
    reg = default_algorithm_registry()
    with pytest.raises(CryptoAgilityError):
        reg.rollover("sha512-new", 40, witness="  ")  # empty witness
    with pytest.raises(CryptoAgilityError):
        reg.rollover("sha256", 10, witness="w")  # already registered


def test_deprecate_requires_prior_rollover():
    reg = AlgorithmRegistry(seed_defaults=False)
    reg.register(HashAlgorithm.create("sha256", 10))
    # Only one active algorithm ⇒ cannot deprecate (must rollover first).
    with pytest.raises(AlgorithmNegotiationError):
        reg.deprecate("sha256")
    reg.rollover("sha512", 30, witness="crypto-board")
    reg.deprecate("sha256")  # now allowed — a successor is active
    assert reg.status("sha256") is AlgorithmStatus.DEPRECATED
    reg.deprecate("sha256")  # idempotent
    assert reg.preferred().name == "sha512"
    with pytest.raises(CryptoAgilityError):
        reg.deprecate("missing")


# --------------------------------------------------------------------------------
# DigestSet — agile digests over the same canonical bytes
# --------------------------------------------------------------------------------


def test_digest_set_compute_and_verify():
    content = {"artifact": "x", "n": 1}
    ds = DigestSet.compute(content, ["sha256", "sha512"])
    assert ds.algorithms == ("sha256", "sha512")  # sorted by algorithm
    assert ds.verify(content) is True
    assert ds.verify({"artifact": "tampered", "n": 1}) is False
    assert ds.verify_with(content, "sha256") is True
    assert ds.by_algorithm("sha512").algorithm == "sha512"
    with pytest.raises(CryptoAgilityError):
        ds.by_algorithm("sha3_256")


def test_digest_set_dedups_and_requires_algorithm():
    ds = DigestSet.compute("data", ["sha256", "sha256"])  # dedup
    assert ds.algorithms == ("sha256",)
    with pytest.raises(CryptoAgilityError):
        DigestSet.compute("data", [])


def test_digest_set_rollover_widens_append_only():
    content = {"a": 1}
    ds = DigestSet.compute(content, ["sha256"])
    widened = ds.rolled_over(content, "sha512")
    assert widened.algorithms == ("sha256", "sha512")
    assert widened.verify(content) is True
    # original is unchanged (append-only)
    assert ds.algorithms == ("sha256",)
    with pytest.raises(CryptoAgilityError):
        widened.rolled_over(content, "sha256")  # already present


def test_digest_set_respects_profile():
    profile = CanonicalProfile("ucos-ccf/keep-ws", strip_trailing_whitespace=False)
    ds = DigestSet.compute("trailing   ", ["sha256"], profile=profile)
    assert ds.profile_id == "ucos-ccf/keep-ws"
    assert ds.verify("trailing   ", profile=profile) is True
    # Default profile strips trailing whitespace ⇒ different canonical bytes.
    assert ds.verify("trailing   ") is False


def test_digest_set_roundtrip_and_errors():
    ds = DigestSet.compute({"a": 1}, ["sha256", "sha512"])
    assert DigestSet.from_dict(ds.to_dict()) == ds
    with pytest.raises(CryptoAgilityError):
        DigestSet.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(CryptoAgilityError):
        DigestSet.from_dict({"profile_id": "p"})  # missing digests
    with pytest.raises(CryptoAgilityError):
        DigestSet.from_dict({"profile_id": "p", "digests": []})  # empty
