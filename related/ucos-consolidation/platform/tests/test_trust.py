"""WP-05 — Genesis Trust, Keys & Signing tests (PRJ-C2 · ACT-C2).

Covers the self-signed genesis anchor, the signed key hierarchy, deterministic
HMAC-SHA256 signing + verification, signed delegation, key rotation, notary-
timestamped revocation, fail-closed trust-chain verification, and the public
(secret-free) trust-state export (AIF-L10 / L11 · SEC-04 / RR-07).
"""

from __future__ import annotations

from platform.foundation.errors import (
    SignatureError,
    TrustChainError,
    TrustError,
)
from platform.foundation.trust import (
    TRUST_SIGNATURE_ALGORITHM,
    TRUST_STORE_FORMAT,
    Delegation,
    KeyStatus,
    NotaryRecord,
    Signature,
    TrustEngine,
    TrustKey,
    bootstrap_trust,
)

import pytest

from engine.foundation.config.config import SecretRef

_GEN = b"genesis-secret-key"
_CHILD = b"child-secret-key"
_NEW = b"rotated-secret-key"


def _engine_with_genesis() -> TrustEngine:
    engine = TrustEngine()
    engine.establish_genesis("genesis", key=_GEN)
    return engine


# --------------------------------------------------------------------------------
# Value types
# --------------------------------------------------------------------------------


def test_trust_key_roundtrip():
    key = TrustKey(key_id="k1", parent_key_id="g", is_genesis=False)
    assert TrustKey.from_dict(key.to_dict()) == key
    genesis = TrustKey(key_id="g", is_genesis=True)
    assert TrustKey.from_dict(genesis.to_dict()) == genesis


def test_trust_key_from_dict_errors():
    with pytest.raises(TrustError):
        TrustKey.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(TrustError):
        TrustKey.from_dict({"algorithm": "x"})  # missing key_id


def test_signature_roundtrip_and_errors():
    sig = Signature("k1", TRUST_SIGNATURE_ALGORITHM, "abc", "def")
    assert Signature.from_dict(sig.to_dict()) == sig
    with pytest.raises(SignatureError):
        Signature.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(SignatureError):
        Signature.from_dict({"key_id": "k1"})  # missing fields


# --------------------------------------------------------------------------------
# Genesis anchor (AIF-L10)
# --------------------------------------------------------------------------------


def test_establish_genesis_is_trusted_anchor():
    engine = _engine_with_genesis()
    anchor = engine.get("genesis")
    assert anchor.is_genesis is True
    assert anchor.parent_key_id is None
    assert engine.trust_anchors == (anchor,)
    assert engine.is_trusted("genesis") is True
    assert engine.verify_chain("genesis") == (anchor,)
    assert engine.status("genesis") is KeyStatus.ACTIVE
    assert len(engine) == 1
    assert "genesis" in engine


def test_establish_genesis_requires_key_and_unique_id():
    engine = TrustEngine()
    with pytest.raises(TrustError):
        engine.establish_genesis("", key=_GEN)
    with pytest.raises(SignatureError):
        engine.establish_genesis("g")  # no key material
    engine.establish_genesis("g", key=_GEN)
    with pytest.raises(TrustError):
        engine.establish_genesis("g", key=_GEN)  # duplicate id


def test_bootstrap_trust_helper():
    engine = bootstrap_trust("genesis", key=_GEN)
    assert engine.is_trusted("genesis")
    assert engine.trust_anchors[0].key_id == "genesis"


# --------------------------------------------------------------------------------
# Signing + verification (AIF-L11)
# --------------------------------------------------------------------------------


def test_sign_and_verify_is_deterministic():
    engine = _engine_with_genesis()
    statement = {"kind": "attestation", "subject": "artifact-1"}
    sig = engine.sign("genesis", statement)
    assert sig.algorithm == TRUST_SIGNATURE_ALGORITHM
    assert sig.key_id == "genesis"
    assert engine.verify(sig, statement) is True
    # Deterministic: a second engine with the same key produces the same signature.
    other = bootstrap_trust("genesis", key=_GEN)
    assert other.sign("genesis", statement) == sig


def test_verify_rejects_tampered_statement_and_wrong_algorithm():
    engine = _engine_with_genesis()
    statement = {"kind": "attestation", "subject": "artifact-1"}
    sig = engine.sign("genesis", statement)
    assert engine.verify(sig, {"kind": "attestation", "subject": "tampered"}) is False
    wrong_algo = Signature("genesis", " RSA", sig.value, sig.payload_hash)
    assert engine.verify(wrong_algo, statement) is False


def test_sign_and_verify_error_paths():
    engine = _engine_with_genesis()
    with pytest.raises(TrustError):
        engine.sign("", {})
    with pytest.raises(SignatureError):
        engine.sign("unregistered", {})
    with pytest.raises(SignatureError):
        engine.verify("not-a-signature", {})  # type: ignore[arg-type]
    stray = Signature("unregistered", TRUST_SIGNATURE_ALGORITHM, "x", "y")
    with pytest.raises(SignatureError):
        engine.verify(stray, {})


def test_signing_key_by_secret_ref(monkeypatch):
    monkeypatch.setenv("UCOS_TRUST_KEY", "env-provided-secret")
    engine = TrustEngine()
    engine.establish_genesis("genesis", key_ref=SecretRef("env://UCOS_TRUST_KEY"))
    statement = {"kind": "attestation", "subject": "s"}
    sig = engine.sign("genesis", statement)
    assert engine.verify(sig, statement) is True


def test_secret_ref_empty_resolution_fails(monkeypatch):
    monkeypatch.setenv("UCOS_EMPTY", "")
    engine = TrustEngine()
    engine.establish_genesis("g", key_ref="env://UCOS_EMPTY")
    with pytest.raises(SignatureError):
        engine.sign("g", {"k": 1})


def test_register_key_validation():
    engine = _engine_with_genesis()
    with pytest.raises(TrustError):
        engine.register_key("", key=_CHILD)
    engine.register_key("child", key=_CHILD)
    with pytest.raises(TrustError):
        engine.register_key("child", key=_CHILD)  # already registered
    with pytest.raises(SignatureError):
        engine.register_key("bad")  # no material
    with pytest.raises(SignatureError):
        engine.register_key("bad2", key="not-bytes")  # type: ignore[arg-type]


# --------------------------------------------------------------------------------
# Delegation & key hierarchy (AIF-L10)
# --------------------------------------------------------------------------------


def test_delegate_extends_trust_chain():
    engine = _engine_with_genesis()
    engine.register_key("child", key=_CHILD)
    delegation = engine.delegate("genesis", "child")
    assert isinstance(delegation, Delegation)
    assert engine.is_trusted("child") is True
    chain = engine.verify_chain("child")
    assert [k.key_id for k in chain] == ["child", "genesis"]
    # The delegation signature verifies against the parent key.
    assert engine.verify(delegation.signature, Delegation.statement("genesis", "child"))


def test_delegate_error_paths():
    engine = _engine_with_genesis()
    with pytest.raises(TrustChainError):
        engine.delegate("genesis", "genesis")  # self-delegation
    with pytest.raises(TrustError):
        engine.delegate("genesis", "unregistered-child")  # child not registered
    # parent not trusted (registered key material but never delegated ⇒ not a trust key)
    engine.register_key("floating", key=_CHILD)
    engine.register_key("orphan-child", key=_NEW)
    with pytest.raises(TrustError):
        engine.delegate("floating", "orphan-child")
    # child already trusted ⇒ fail closed
    engine.register_key("child", key=_CHILD)
    engine.delegate("genesis", "child")
    with pytest.raises(TrustError):
        engine.delegate("genesis", "child")


def test_multi_level_delegation_chain():
    engine = _engine_with_genesis()
    engine.register_key("mid", key=_CHILD)
    engine.delegate("genesis", "mid")
    engine.register_key("leaf", key=_NEW)
    engine.delegate("mid", "leaf")
    assert [k.key_id for k in engine.verify_chain("leaf")] == ["leaf", "mid", "genesis"]


# --------------------------------------------------------------------------------
# Key rotation (AIF-L10 successor recognition)
# --------------------------------------------------------------------------------


def test_rotate_recognizes_successor_by_delegation():
    engine = _engine_with_genesis()
    engine.rotate("genesis", "genesis-2", key=_NEW)
    assert engine.is_trusted("genesis-2") is True
    assert engine.status("genesis") is KeyStatus.ROTATED
    assert engine.status("genesis-2") is KeyStatus.ACTIVE
    # The successor traces back to the original anchor.
    assert [k.key_id for k in engine.verify_chain("genesis-2")] == ["genesis-2", "genesis"]


# --------------------------------------------------------------------------------
# Notary + revocation (AIF-L11 / AIF-L17)
# --------------------------------------------------------------------------------


def test_notarize_is_monotonic_and_signed():
    engine = _engine_with_genesis()
    r1 = engine.notarize("digest-a", "genesis")
    r2 = engine.notarize("digest-b", "genesis")
    assert (r1.sequence, r2.sequence) == (1, 2)
    assert isinstance(r1, NotaryRecord)
    assert engine.verify(r1.signature, NotaryRecord.statement(1, "genesis", "digest-a"))


def test_notarize_error_paths():
    engine = _engine_with_genesis()
    with pytest.raises(TrustError):
        engine.notarize("", "genesis")
    with pytest.raises(TrustError):
        engine.notarize("d", "unknown-witness")


def test_revoke_marks_key_and_breaks_trust():
    engine = _engine_with_genesis()
    engine.register_key("child", key=_CHILD)
    engine.delegate("genesis", "child")
    revocation = engine.revoke("child", "compromised", witness_key_id="genesis")
    assert engine.status("child") is KeyStatus.REVOKED
    assert engine.is_trusted("child") is False
    assert revocation.notary.sequence == 1
    assert engine.revocations == (revocation,)
    # The revocation event is signed and verifiable.
    assert engine.verify(
        revocation.signature,
        type(revocation).statement("child", "compromised", 1),
    )


def test_revoked_ancestor_breaks_descendant_trust():
    engine = _engine_with_genesis()
    engine.register_key("mid", key=_CHILD)
    engine.delegate("genesis", "mid")
    engine.register_key("leaf", key=_NEW)
    engine.delegate("mid", "leaf")
    engine.revoke("mid", "key-leak", witness_key_id="genesis")
    assert engine.is_trusted("leaf") is False
    with pytest.raises(TrustChainError):
        engine.verify_chain("leaf")


def test_self_revocation():
    engine = _engine_with_genesis()
    engine.register_key("child", key=_CHILD)
    engine.delegate("genesis", "child")
    engine.revoke("child", "self-retire", witness_key_id="child")
    assert engine.status("child") is KeyStatus.REVOKED


def test_revoke_error_paths():
    engine = _engine_with_genesis()
    with pytest.raises(TrustError):
        engine.revoke("unknown", "r", witness_key_id="genesis")
    engine.revoke("genesis", "root-retire", witness_key_id="genesis")
    with pytest.raises(TrustError):
        engine.revoke("genesis", "again", witness_key_id="genesis")  # already revoked


# --------------------------------------------------------------------------------
# Trust-chain verification — fail closed (AIF-L16)
# --------------------------------------------------------------------------------


def test_verify_chain_unknown_key_fails_closed():
    engine = _engine_with_genesis()
    with pytest.raises(TrustError):
        engine.verify_chain("nope")
    assert engine.is_trusted("nope") is False


def test_verify_chain_detects_invalid_delegation_signature():
    engine = _engine_with_genesis()
    engine.register_key("child", key=_CHILD)
    delegation = engine.delegate("genesis", "child")
    # Forge a delegation with a bad signature for the child.
    forged = Delegation(
        "genesis", "child", Signature("genesis", TRUST_SIGNATURE_ALGORITHM, "0" * 64, "x")
    )
    engine._delegations["child"] = forged
    assert engine.is_trusted("child") is False
    with pytest.raises(TrustChainError):
        engine.verify_chain("child")
    # sanity: the genuine delegation did verify
    assert engine.verify(delegation.signature, Delegation.statement("genesis", "child"))


def test_verify_chain_detects_orphan_and_cycle():
    engine = _engine_with_genesis()
    # Orphan: a key present in the graph with no delegation and not genesis.
    engine._keys["orphan"] = TrustKey(key_id="orphan", parent_key_id=None)
    engine._order.append("orphan")
    with pytest.raises(TrustChainError):
        engine.verify_chain("orphan")
    # Cycle: two keys delegating to each other (forged graph state).
    engine.register_key("a", key=_CHILD)
    engine.register_key("b", key=_NEW)
    engine._keys["a"] = TrustKey(key_id="a", parent_key_id="b")
    engine._keys["b"] = TrustKey(key_id="b", parent_key_id="a")
    engine._order.extend(["a", "b"])
    engine._delegations["a"] = Delegation(
        "b", "a", engine._sign_statement("b", Delegation.statement("b", "a"))
    )
    engine._delegations["b"] = Delegation(
        "a", "b", engine._sign_statement("a", Delegation.statement("a", "b"))
    )
    with pytest.raises(TrustChainError):
        engine.verify_chain("a")


# --------------------------------------------------------------------------------
# Export — public state only, never secrets (SEC-04 / RR-07)
# --------------------------------------------------------------------------------


def _rich_engine() -> TrustEngine:
    engine = _engine_with_genesis()
    engine.register_key("child", key=_CHILD)
    engine.delegate("genesis", "child")
    engine.rotate("genesis", "genesis-2", key=_NEW)
    engine.revoke("child", "compromised", witness_key_id="genesis")
    return engine


def test_export_shape_is_secret_free_and_deterministic():
    engine = _rich_engine()
    exported = engine.export()
    assert exported["store_format"] == TRUST_STORE_FORMAT
    assert exported["algorithm"] == TRUST_SIGNATURE_ALGORITHM
    assert {k["key_id"] for k in exported["keys"]} == {"genesis", "child", "genesis-2"}
    assert exported["rotated"] == ["genesis"]
    assert len(exported["revocations"]) == 1
    assert exported["notary_sequence"] == 1
    assert engine.to_dict() == exported
    # No secret material anywhere in the export.
    rendered = str(exported)
    assert "genesis-secret-key" not in rendered
    assert "child-secret-key" not in rendered
    # Deterministic fingerprint across identical construction.
    assert engine.fingerprint() == _rich_engine().fingerprint()


def test_keys_and_revocations_snapshots_are_ordered():
    engine = _rich_engine()
    assert [k.key_id for k in engine.keys] == ["genesis", "child", "genesis-2"]
    assert engine.revocations[0].key_id == "child"
