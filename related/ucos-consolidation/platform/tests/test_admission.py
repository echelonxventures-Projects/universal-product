"""WP-08 — Admission Key Binder tests (PRJ-C2 · ACT-C2).

Covers admission-authority namespace ownership, atomic admission (mint + projection
re-verify, no orphan on failure), authority-namespaced duplicate detection, rename
stability (path independence), partition/sub-namespace delegation, and witnessed
authority migration (AIF-L06 / L07 / L09 / L14 · A/G-AUTH).
"""

from __future__ import annotations

from platform.foundation.admission import (
    ADMISSION_LEDGER_FORMAT,
    AdmissionBinder,
    AuthorityMigration,
    AuthorityStatus,
)
from platform.foundation.durable_identity import IdentityRegistry
from platform.foundation.errors import (
    AdmissionError,
    AuthorityBindingError,
    DuplicateAdmissionError,
    DurableIdentityError,
    TrustError,
)
from platform.foundation.trust import bootstrap_trust

import pytest

_KEY = b"genesis-secret"


def _binder() -> AdmissionBinder:
    binder = AdmissionBinder()
    binder.register_authority("AUTH-1")
    return binder


# --------------------------------------------------------------------------------
# Namespace ownership (AIF-L07)
# --------------------------------------------------------------------------------


def test_register_authority_owns_namespace():
    binder = AdmissionBinder()
    authority = binder.register_authority("AUTH-1")
    assert authority.status is AuthorityStatus.ACTIVE
    assert binder.authority("AUTH-1") == authority
    assert binder.authorities == (authority,)


def test_register_authority_validation():
    binder = AdmissionBinder()
    with pytest.raises(AuthorityBindingError):
        binder.register_authority("  ")
    binder.register_authority("AUTH-1")
    with pytest.raises(AuthorityBindingError):
        binder.register_authority("AUTH-1")  # duplicate
    with pytest.raises(AuthorityBindingError):
        binder.authority("UNKNOWN")


# --------------------------------------------------------------------------------
# Atomic admission (AIF-L14)
# --------------------------------------------------------------------------------


def test_admit_mints_and_binds():
    binder = _binder()
    record = binder.admit("AUTH-1", "k1", "docs/readme.md")
    assert record.authority_id == "AUTH-1"
    assert record.local_key == "k1"
    assert record.urn.startswith("urn:ucos:p2:AUTH-1:")
    assert binder.resolve("docs/readme.md") == record
    assert binder.resolve_by_key("AUTH-1", "k1") == record
    assert binder.is_admitted("AUTH-1", "k1") is True
    assert len(binder) == 1
    # The identity was actually sealed in the underlying registry.
    assert binder.identities.lookup("AUTH-1", "k1").urn == record.urn


def test_admit_is_idempotent_for_same_triple():
    binder = _binder()
    first = binder.admit("AUTH-1", "k1", "same-name")
    second = binder.admit("AUTH-1", "k1", "same-name")
    assert first == second
    assert len(binder) == 1


def test_admit_projection_verifier_passes():
    binder = _binder()
    seen = {}

    def verifier(identity):
        seen["urn"] = identity.urn
        return True

    record = binder.admit("AUTH-1", "k1", "n", verify_projection=verifier)
    assert seen["urn"] == record.urn


def test_admit_aborts_on_failed_projection_no_orphan():
    binder = _binder()
    with pytest.raises(AdmissionError):
        binder.admit("AUTH-1", "k1", "n", verify_projection=lambda _identity: False)
    # No orphan identity and no binding remain.
    assert len(binder) == 0
    assert binder.is_admitted("AUTH-1", "k1") is False
    with pytest.raises(DurableIdentityError):
        binder.identities.lookup("AUTH-1", "k1")
    # The admission key is re-admittable afterwards (abort left no trace).
    binder.admit("AUTH-1", "k1", "n")
    assert len(binder) == 1


def test_admit_aborts_on_raising_projection():
    binder = _binder()

    def boom(_identity):
        raise ValueError("projection blew up")

    with pytest.raises(ValueError):
        binder.admit("AUTH-1", "k1", "n", verify_projection=boom)
    assert binder.is_admitted("AUTH-1", "k1") is False


def test_admit_validation_and_duplicates():
    binder = _binder()
    with pytest.raises(AdmissionError):
        binder.admit("AUTH-1", "k1", "  ")  # blank name
    binder.admit("AUTH-1", "k1", "name-a")
    # Same key, different name ⇒ duplicate identity admission.
    with pytest.raises(DuplicateAdmissionError):
        binder.admit("AUTH-1", "k1", "name-b")
    # Different key, name already used ⇒ duplicate name.
    with pytest.raises(DuplicateAdmissionError):
        binder.admit("AUTH-1", "k2", "name-a")


# --------------------------------------------------------------------------------
# Rename stability (AIF-L06 path independence)
# --------------------------------------------------------------------------------


def test_rename_preserves_identity():
    binder = _binder()
    original = binder.admit("AUTH-1", "k1", "old/path.md")
    renamed = binder.rename("old/path.md", "new/path.md")
    assert renamed.logical_name == "new/path.md"
    # Identity (urn/opaque/key) is unchanged — path independence.
    assert renamed.urn == original.urn
    assert renamed.opaque == original.opaque
    assert renamed.admission_key == original.admission_key
    assert binder.resolve_by_key("AUTH-1", "k1").logical_name == "new/path.md"
    with pytest.raises(AdmissionError):
        binder.resolve("old/path.md")  # old name no longer resolves


def test_rename_noop_and_errors():
    binder = _binder()
    binder.admit("AUTH-1", "k1", "a")
    binder.admit("AUTH-1", "k2", "b")
    assert binder.rename("a", "a").logical_name == "a"  # no-op
    with pytest.raises(AdmissionError):
        binder.rename("a", "  ")  # blank target
    with pytest.raises(AdmissionError):
        binder.rename("missing", "x")  # unknown source
    with pytest.raises(DuplicateAdmissionError):
        binder.rename("a", "b")  # target already admitted


# --------------------------------------------------------------------------------
# Resolution fails closed
# --------------------------------------------------------------------------------


def test_resolution_fails_closed():
    binder = _binder()
    with pytest.raises(AdmissionError):
        binder.resolve("missing")
    with pytest.raises(AdmissionError):
        binder.resolve_by_key("AUTH-1", "missing")


# --------------------------------------------------------------------------------
# Partition + sub-namespace delegation (AIF-L09)
# --------------------------------------------------------------------------------


def test_partition_blocks_minting_and_resume_restores():
    binder = _binder()
    binder.partition("AUTH-1")
    assert binder.authority("AUTH-1").status is AuthorityStatus.PARTITIONED
    with pytest.raises(AuthorityBindingError):
        binder.admit("AUTH-1", "k1", "n")
    binder.resume("AUTH-1")
    assert binder.authority("AUTH-1").status is AuthorityStatus.ACTIVE
    binder.admit("AUTH-1", "k1", "n")  # minting works again
    assert len(binder) == 1


def test_resume_requires_partition():
    binder = _binder()
    with pytest.raises(AuthorityBindingError):
        binder.resume("AUTH-1")  # not partitioned


def test_delegate_subnamespace_relieves_partition():
    binder = _binder()
    binder.partition("AUTH-1")
    child = binder.delegate_subnamespace("AUTH-1", "AUTH-1-SUB")
    assert child.parent_id == "AUTH-1"
    assert child.status is AuthorityStatus.ACTIVE
    # New admissions proceed under the delegated sub-namespace.
    record = binder.admit("AUTH-1-SUB", "k1", "n")
    assert record.authority_id == "AUTH-1-SUB"
    with pytest.raises(AuthorityBindingError):
        binder.delegate_subnamespace("AUTH-1", "AUTH-1-SUB")  # duplicate child


# --------------------------------------------------------------------------------
# Witnessed authority migration (AIF-L09 / A/G-AUTH)
# --------------------------------------------------------------------------------


def test_migrate_authority_requires_trust_engine():
    binder = _binder()
    binder.register_authority("AUTH-2")
    with pytest.raises(AuthorityBindingError):
        binder.migrate_authority("AUTH-1", "AUTH-2", witness_key_id="genesis")


def test_migrate_authority_witnessed_and_reroutes_minting():
    trust = bootstrap_trust("genesis", key=_KEY)
    binder = AdmissionBinder(trust=trust)
    binder.register_authority("AUTH-1")
    binder.register_authority("AUTH-2")
    existing = binder.admit("AUTH-1", "k1", "kept.md")
    migration = binder.migrate_authority("AUTH-1", "AUTH-2", witness_key_id="genesis")
    assert isinstance(migration, AuthorityMigration)
    assert binder.authority("AUTH-1").status is AuthorityStatus.MIGRATED
    assert binder.authority("AUTH-1").successor_id == "AUTH-2"
    # Existing identity remains immutable and resolvable.
    assert binder.resolve("kept.md") == existing
    # Minting under the migrated authority is blocked; the successor accepts it.
    with pytest.raises(AuthorityBindingError):
        binder.admit("AUTH-1", "k2", "blocked.md")
    binder.admit("AUTH-2", "k2", "new.md")
    assert binder.is_admitted("AUTH-2", "k2") is True


def test_migrate_authority_error_paths():
    trust = bootstrap_trust("genesis", key=_KEY)
    binder = AdmissionBinder(trust=trust)
    binder.register_authority("AUTH-1")
    binder.register_authority("AUTH-2")
    # untrusted witness
    with pytest.raises(TrustError):
        binder.migrate_authority("AUTH-1", "AUTH-2", witness_key_id="stranger")
    migration = binder.migrate_authority("AUTH-1", "AUTH-2", witness_key_id="genesis")
    assert migration.to_dict()["old_authority_id"] == "AUTH-1"
    with pytest.raises(AuthorityBindingError):
        binder.migrate_authority("AUTH-1", "AUTH-2", witness_key_id="genesis")  # already migrated


def test_cannot_partition_migrated_authority():
    trust = bootstrap_trust("genesis", key=_KEY)
    binder = AdmissionBinder(trust=trust)
    binder.register_authority("AUTH-1")
    binder.register_authority("AUTH-2")
    binder.migrate_authority("AUTH-1", "AUTH-2", witness_key_id="genesis")
    with pytest.raises(AuthorityBindingError):
        binder.partition("AUTH-1")


# --------------------------------------------------------------------------------
# Export + shared registry composition
# --------------------------------------------------------------------------------


def test_export_shape():
    binder = _binder()
    binder.admit("AUTH-1", "k1", "a")
    binder.admit("AUTH-1", "k2", "b")
    exported = binder.export()
    assert exported["ledger_format"] == ADMISSION_LEDGER_FORMAT
    assert len(exported["records"]) == 2
    assert {a["authority_id"] for a in exported["authorities"]} == {"AUTH-1"}
    assert binder.to_dict() == exported
    # containment + ordered records snapshot
    assert "a" in binder
    assert "missing" not in binder
    assert [r.logical_name for r in binder.records] == ["a", "b"]


def test_binder_uses_supplied_identity_registry():
    registry = IdentityRegistry()
    binder = AdmissionBinder(registry)
    binder.register_authority("AUTH-1")
    record = binder.admit("AUTH-1", "k1", "n")
    # The identity is sealed in the *shared* registry instance.
    assert registry.lookup("AUTH-1", "k1").urn == record.urn
    assert len(registry) == 1
