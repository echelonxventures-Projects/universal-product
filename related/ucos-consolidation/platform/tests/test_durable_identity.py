"""WP-04 — P2 Durable Identity Minting tests (PRJ-C2 · ACT-C2).

Covers the opaque, minted-once, immutable, authority-namespaced P2 identity and its
append-only registry: deterministic allocation from the path-independent admission
key, prepare/commit/abort atomicity (provisional-until-seal, no orphan, idempotent
retry), collision prevention, fail-closed lookup, forward-only retirement,
deterministic export/import (replay), and one-time genesis adoption / migration
compatibility (AIF-L02 / L06 / L07 / L13 / L16 / L17 · A/G7).
"""

from __future__ import annotations

import dataclasses
from platform.foundation.durable_identity import (
    DURABLE_IDENTITY_PROFILE,
    IDENTITY_REGISTRY_FORMAT,
    P2_OPAQUE_HEX_LEN,
    P2_URN_PREFIX,
    AdmissionKey,
    DurableIdentity,
    IdentityMint,
    IdentityRegistry,
    MintState,
    build_identity_registry,
)
from platform.foundation.errors import (
    DurableIdentityError,
    IdentityCollisionError,
    IdentityMintError,
)

import pytest

from engine.foundation.obs.context import reset_correlation_id, set_correlation_id

_FAKE_OPAQUE = "deadbeefdeadbeefdeadbeefdeadbeef"  # 32 lowercase hex chars

# --------------------------------------------------------------------------------
# AdmissionKey — path-independent (AuthorityID, local-key)
# --------------------------------------------------------------------------------


def test_admission_key_render_and_roundtrip():
    key = AdmissionKey(authority_id="AUTH-1", local_key="artifact-42")
    assert key.render == "AUTH-1/artifact-42"
    assert key.to_dict() == {"authority_id": "AUTH-1", "local_key": "artifact-42"}
    assert AdmissionKey.from_dict(key.to_dict()) == key


def test_admission_key_validation():
    with pytest.raises(DurableIdentityError):
        AdmissionKey(authority_id="", local_key="k")
    with pytest.raises(DurableIdentityError):
        AdmissionKey(authority_id="A", local_key="   ")
    with pytest.raises(DurableIdentityError):
        AdmissionKey(authority_id=123, local_key="k")  # type: ignore[arg-type]
    # '/' is reserved as the render separator.
    with pytest.raises(DurableIdentityError):
        AdmissionKey(authority_id="a/b", local_key="k")
    with pytest.raises(DurableIdentityError):
        AdmissionKey(authority_id="A", local_key="a/b")


def test_admission_key_from_dict_errors():
    with pytest.raises(DurableIdentityError):
        AdmissionKey.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(DurableIdentityError):
        AdmissionKey.from_dict({"authority_id": "A"})  # missing local_key


# --------------------------------------------------------------------------------
# DurableIdentity — opaque, deterministic, immutable
# --------------------------------------------------------------------------------


def test_mint_is_deterministic_and_opaque():
    a = DurableIdentity.mint("AUTH-1", "k1")
    b = DurableIdentity.mint("AUTH-1", "k1")
    assert a == b
    assert a.opaque == b.opaque
    assert len(a.opaque) == P2_OPAQUE_HEX_LEN
    assert a.urn == f"{P2_URN_PREFIX}AUTH-1:{a.opaque}"
    assert a.profile == DURABLE_IDENTITY_PROFILE
    assert a.adopted is False
    assert a.verify() is True
    assert a.admission_key == AdmissionKey("AUTH-1", "k1")


def test_distinct_keys_are_unique_by_construction():
    a = DurableIdentity.mint("AUTH-1", "k1")
    b = DurableIdentity.mint("AUTH-1", "k2")
    c = DurableIdentity.mint("AUTH-2", "k1")
    assert len({a.opaque, b.opaque, c.opaque}) == 3


def test_identity_is_not_path_derived():
    # The opaque depends only on the admission key, never on any path/content.
    assert DurableIdentity.compute_opaque("A", "k") == DurableIdentity.mint("A", "k").opaque


def test_adopt_preserves_frozen_opaque():
    ident = DurableIdentity.adopt("AUTH-1", "legacy-1", _FAKE_OPAQUE)
    assert ident.adopted is True
    assert ident.opaque == _FAKE_OPAQUE
    assert ident.urn == f"{P2_URN_PREFIX}AUTH-1:{_FAKE_OPAQUE}"
    # Adopted identities carry a historical opaque and are trivially intact.
    assert ident.verify() is True


def test_adopt_rejects_malformed_opaque():
    with pytest.raises(DurableIdentityError):
        DurableIdentity.adopt("A", "k", "tooshort")
    with pytest.raises(DurableIdentityError):
        DurableIdentity.adopt("A", "k", "Z" * P2_OPAQUE_HEX_LEN)  # non-hex / uppercase


def test_verify_detects_tampered_native_identity():
    ident = DurableIdentity.mint("A", "k")
    forged = dataclasses.replace(ident, opaque=_FAKE_OPAQUE)
    assert forged.verify() is False


def test_identity_to_dict_from_dict_roundtrip():
    ident = DurableIdentity.mint("AUTH-9", "k9")
    restored = DurableIdentity.from_dict(ident.to_dict())
    assert restored == ident
    adopted = DurableIdentity.adopt("AUTH-9", "legacy", _FAKE_OPAQUE)
    assert DurableIdentity.from_dict(adopted.to_dict()) == adopted


def test_identity_from_dict_errors():
    with pytest.raises(DurableIdentityError):
        DurableIdentity.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(DurableIdentityError):
        DurableIdentity.from_dict({"authority_id": "A", "local_key": "k"})  # no opaque
    # A native record whose opaque disagrees with its key is tamper — fail closed.
    with pytest.raises(IdentityCollisionError):
        DurableIdentity.from_dict(
            {"authority_id": "A", "local_key": "k", "opaque": _FAKE_OPAQUE, "adopted": False}
        )


# --------------------------------------------------------------------------------
# IdentityMint — prepare/commit/abort value type
# --------------------------------------------------------------------------------


def test_identity_mint_shape():
    ident = DurableIdentity.mint("A", "k")
    mint = IdentityMint(ident, MintState.PREPARED)
    assert mint.admission_key == ident.admission_key
    assert mint.to_dict() == {"identity": ident.to_dict(), "state": "prepared"}
    assert MintState.PREPARED.value == "prepared"


# --------------------------------------------------------------------------------
# IdentityRegistry — atomicity (prepare / commit / abort)
# --------------------------------------------------------------------------------


def test_prepare_commit_seals_identity():
    reg = IdentityRegistry()
    mint = reg.prepare("A", "k1")
    assert mint.state is MintState.PREPARED
    assert len(reg) == 0  # provisional, not yet sealed
    assert reg.pending[0].identity == mint.identity
    sealed = reg.commit(mint)
    assert sealed == mint.identity
    assert len(reg) == 1
    assert reg.pending == ()
    assert reg.identities == (sealed,)
    assert sealed.admission_key.render in reg
    assert sealed.opaque in reg
    assert reg.verify() is True
    reg.require_intact()


def test_commit_is_idempotent_retry():
    reg = IdentityRegistry()
    mint = reg.prepare("A", "k1")
    reg.commit(mint)
    # Re-committing the same mint is an idempotent retry (AIF-L13).
    again = reg.commit(mint)
    assert again == mint.identity
    assert len(reg) == 1


def test_mint_convenience_is_idempotent():
    reg = IdentityRegistry()
    first = reg.mint("A", "k1")
    second = reg.mint("A", "k1")  # already sealed ⇒ returns existing
    assert first == second
    assert len(reg) == 1


def test_abort_discards_provisional_no_orphan():
    reg = IdentityRegistry()
    mint = reg.prepare("A", "k1")
    reg.abort(mint)
    assert reg.pending == ()
    assert len(reg) == 0
    # Aborting again (unknown/never-prepared) is a harmless no-op.
    reg.abort(mint)
    # The admission key can still be minted afterwards (abort left no trace).
    reg.mint("A", "k1")
    assert len(reg) == 1


def test_prepare_fails_closed_on_duplicate_and_retired():
    reg = IdentityRegistry()
    reg.mint("A", "k1")
    # already sealed
    with pytest.raises(IdentityCollisionError):
        reg.prepare("A", "k1")
    # already pending
    reg.prepare("A", "k2")
    with pytest.raises(IdentityMintError):
        reg.prepare("A", "k2")
    # retired
    reg.retire("A", "k1")
    with pytest.raises(IdentityMintError):
        reg.prepare("A", "k1")


def test_commit_error_paths():
    reg = IdentityRegistry()
    with pytest.raises(IdentityMintError):
        reg.commit("not-a-mint")  # type: ignore[arg-type]
    # commit without prepare
    stray = IdentityMint(DurableIdentity.mint("A", "k1"), MintState.PREPARED)
    with pytest.raises(IdentityMintError):
        reg.commit(stray)
    # committed mint disagrees with a sealed key on opaque
    reg.mint("A", "k2")
    conflicting = IdentityMint(DurableIdentity.adopt("A", "k2", _FAKE_OPAQUE), MintState.PREPARED)
    with pytest.raises(IdentityCollisionError):
        reg.commit(conflicting)


def test_commit_disagrees_with_pending_fails_closed():
    reg = IdentityRegistry()
    reg.prepare("A", "k1")  # pending opaque == compute("A","k1")
    # A mint for the same ref but a different opaque disagrees with the pending one.
    conflicting = IdentityMint(DurableIdentity.adopt("A", "k1", _FAKE_OPAQUE), MintState.PREPARED)
    with pytest.raises(IdentityCollisionError):
        reg.commit(conflicting)


def test_abort_error_paths():
    reg = IdentityRegistry()
    with pytest.raises(IdentityMintError):
        reg.abort("not-a-mint")  # type: ignore[arg-type]
    sealed = reg.mint("A", "k1")
    with pytest.raises(IdentityMintError):
        reg.abort(IdentityMint(sealed, MintState.COMMITTED))


# --------------------------------------------------------------------------------
# Lookup & durable references (fail closed — AIF-L16)
# --------------------------------------------------------------------------------


def test_lookup_resolve_and_durable_reference():
    reg = IdentityRegistry()
    ident = reg.mint("AUTH-1", "k1")
    assert reg.lookup("AUTH-1", "k1") == ident
    assert reg.resolve(ident.opaque) == ident
    assert reg.resolve(ident.urn) == ident
    assert reg.durable_reference("AUTH-1", "k1") == ident.urn


def test_lookup_and_resolve_fail_closed():
    reg = IdentityRegistry()
    with pytest.raises(DurableIdentityError):
        reg.lookup("AUTH-1", "missing")
    with pytest.raises(DurableIdentityError):
        reg.resolve("no-such-opaque")
    with pytest.raises(DurableIdentityError):
        reg.resolve(f"{P2_URN_PREFIX}AUTH-1:{_FAKE_OPAQUE}")


# --------------------------------------------------------------------------------
# Forward-only retirement (AIF-L17)
# --------------------------------------------------------------------------------


def test_retire_marks_key_and_blocks_reuse():
    reg = IdentityRegistry()
    reg.mint("A", "k1")
    reg.retire("A", "k1")
    assert "A/k1" in reg.retired
    with pytest.raises(IdentityMintError):
        reg.mint("A", "k1")


def test_retire_unsealed_fails_closed():
    reg = IdentityRegistry()
    with pytest.raises(DurableIdentityError):
        reg.retire("A", "never-minted")


# --------------------------------------------------------------------------------
# Migration / genesis adoption (A/G7)
# --------------------------------------------------------------------------------


def test_adopt_seals_frozen_opaque_and_is_idempotent():
    reg = IdentityRegistry()
    ident = reg.adopt("AUTH-1", "legacy-1", _FAKE_OPAQUE)
    assert ident.adopted is True
    assert reg.lookup("AUTH-1", "legacy-1") == ident
    # Idempotent: adopting the same key + opaque returns the sealed identity.
    assert reg.adopt("AUTH-1", "legacy-1", _FAKE_OPAQUE) == ident
    assert len(reg) == 1


def test_adopt_error_paths():
    reg = IdentityRegistry()
    reg.adopt("A", "legacy", _FAKE_OPAQUE)
    # same key, different opaque ⇒ collision
    other = "abcdef01" * 4
    with pytest.raises(IdentityCollisionError):
        reg.adopt("A", "legacy", other)
    # retired key can never be adopted
    reg.mint("A", "k1")
    reg.retire("A", "k1")
    with pytest.raises(IdentityMintError):
        reg.adopt("A", "k1", other)


# --------------------------------------------------------------------------------
# Collision prevention on the opaque index
# --------------------------------------------------------------------------------


def test_opaque_bound_to_committed_key_collision():
    reg = IdentityRegistry()
    ident = reg.mint("A", "k1")
    # Adopt a *different* admission key with the *same* opaque ⇒ collision.
    with pytest.raises(IdentityCollisionError):
        reg.adopt("A", "k2", ident.opaque)


def test_opaque_pending_for_other_key_collision():
    reg = IdentityRegistry()
    prepared = reg.prepare("A", "k1")  # pending, not committed
    with pytest.raises(IdentityCollisionError):
        reg.adopt("A", "k2", prepared.identity.opaque)


# --------------------------------------------------------------------------------
# Integrity verification (tamper-evidence)
# --------------------------------------------------------------------------------


def test_verify_detects_index_size_mismatch():
    reg = IdentityRegistry()
    reg.mint("A", "k1")
    reg._by_opaque["extra"] = "A/k1"  # opaque index larger than committed set
    assert reg.verify() is False
    with pytest.raises(IdentityCollisionError):
        reg.require_intact()


def test_verify_detects_key_render_mismatch():
    reg = IdentityRegistry()
    ident = reg.mint("A", "k1")
    # Rebind the sealed identity under a wrong ref key.
    reg._committed.clear()
    reg._committed["A/wrong"] = ident
    reg._by_opaque = {ident.opaque: "A/wrong"}
    assert reg.verify() is False


def test_verify_detects_tampered_identity():
    reg = IdentityRegistry()
    ident = reg.mint("A", "k1")
    forged = dataclasses.replace(ident, opaque=_FAKE_OPAQUE)
    reg._committed["A/k1"] = forged
    assert reg.verify() is False


def test_verify_detects_broken_reverse_index():
    reg = IdentityRegistry()
    ident = reg.mint("A", "k1")
    reg._by_opaque[ident.opaque] = "A/other"  # points at the wrong ref
    assert reg.verify() is False


# --------------------------------------------------------------------------------
# Export / import — deterministic replay
# --------------------------------------------------------------------------------


def _sample_registry() -> IdentityRegistry:
    reg = IdentityRegistry()
    reg.mint("AUTH-1", "k1")
    reg.mint("AUTH-1", "k2")
    reg.adopt("AUTH-2", "legacy", _FAKE_OPAQUE)
    reg.mint("AUTH-1", "k3")
    reg.retire("AUTH-1", "k3")
    return reg


def test_export_shape_and_fingerprint_determinism():
    reg = _sample_registry()
    exported = reg.export()
    assert exported["registry_format"] == IDENTITY_REGISTRY_FORMAT
    assert exported["count"] == 4
    assert exported["retired"] == ["AUTH-1/k3"]
    assert len(exported["identities"]) == 4
    assert reg.to_dict() == exported
    assert reg.fingerprint() == _sample_registry().fingerprint()


def test_import_roundtrip_preserves_registry():
    reg = _sample_registry()
    restored = IdentityRegistry.from_dict(reg.export())
    assert restored.verify() is True
    assert len(restored) == len(reg)
    assert restored.fingerprint() == reg.fingerprint()
    assert restored.retired == reg.retired


def test_import_rejects_malformed_export():
    with pytest.raises(DurableIdentityError):
        IdentityRegistry.from_dict("nope")  # type: ignore[arg-type]
    with pytest.raises(DurableIdentityError):
        IdentityRegistry.from_dict({"registry_format": IDENTITY_REGISTRY_FORMAT})


def test_import_rejects_retired_key_not_sealed():
    reg = IdentityRegistry()
    reg.mint("A", "k1")
    exported = reg.export()
    exported["retired"] = ["A/never-sealed"]
    with pytest.raises(DurableIdentityError):
        IdentityRegistry.from_dict(exported)


# --------------------------------------------------------------------------------
# Builder + correlation binding
# --------------------------------------------------------------------------------


def test_build_identity_registry_seeded_and_empty():
    assert len(build_identity_registry()) == 0
    reg = build_identity_registry([("A", "k1"), ("A", "k2")])
    assert len(reg) == 2
    assert reg.lookup("A", "k1").opaque != reg.lookup("A", "k2").opaque


def test_prepare_logs_bind_correlation_id():
    reg = IdentityRegistry()
    token = set_correlation_id("corr-p2")
    try:
        mint = reg.prepare("A", "k1")
    finally:
        reset_correlation_id(token)
    # The identity itself carries no wall-clock/correlation state (Recorded Truth).
    assert mint.identity.verify() is True
