"""UCOS-EPIC-014 — Certification Registry tests (Terminal T7).

The registry is the cluster's second dependency-independent module: it imports only the
error taxonomy and the reused hashing primitive, and it is the record that makes a
certification *discoverable*. Its constitutional promise is narrow and absolute — the
record is append-only, hash-chained, and never reports itself intact when it is not.

These tests prove four things:

* **Append-only.** There is no update and no delete. Re-registering a certification id
  is refused rather than overwriting the earlier determination, because a certification
  that could be silently replaced is not evidence of anything.
* **Chain integrity.** Each entry commits to its own canonical core *and* to its
  predecessor's hash, so the head hash is a commitment to the whole history. Tampering
  with any field of any entry, renumbering an entry, or re-parenting one is detectable.
* **Fail-closed integrity.** ``verify`` returns False and ``require_intact`` raises on a
  broken chain, and ``register`` refuses to extend a chain that does not verify — a
  registry that cannot prove its own integrity never appends onto the doubt.
* **Full provenance in one record.** Every entry carries the digests needed to locate and
  replay the run that produced it, so a registered certification is never a dead end.

Tampering is performed with :func:`dataclasses.replace`, which rebuilds the frozen entry
with the *original* ``entry_hash`` carried over — exactly the retroactive edit the chain
exists to detect, and the only honest way to test that detection.
"""

from __future__ import annotations

import dataclasses
from platform.foundation.contracts import content_hash
from platform.universal_assurance.errors import AssuranceRegistryError
from platform.universal_assurance.registry import (
    GENESIS_HASH,
    REGISTRY_FORMAT,
    STATUS_CERTIFIED,
    STATUS_NOT_CERTIFIED,
    CertificationRegistry,
    RegistryEntry,
    entry_provenance,
)
from typing import Any

import pytest

#: The provenance digests every entry must carry, discovered from the helper itself.
_PROVENANCE_KEYS = (
    "policy_digest",
    "validation_plan_sha256",
    "certification_plan_sha256",
    "validation_execution_sha256",
    "certification_execution_sha256",
    "certificate_sha256",
    "evidence_bundle_sha256",
)


def _registration(suffix: str = "1", *, certified: bool = True) -> dict[str, Any]:
    """A complete, well-formed registration payload for ``CertificationRegistry.register``."""
    return {
        "certification_id": f"CERT-{suffix}",
        "subject_id": f"SUBJ-{suffix}",
        "version": "1.0.0",
        "certified": certified,
        "certificate_sha256": content_hash({"certificate": suffix}),
        "certificate_intact": True,
        "validation_plan_sha256": content_hash({"validation-plan": suffix}),
        "certification_plan_sha256": content_hash({"certification-plan": suffix}),
        "validation_execution_sha256": content_hash({"validation-execution": suffix}),
        "certification_execution_sha256": content_hash({"certification-execution": suffix}),
        "evidence_id": f"EVID-{suffix}",
        "evidence_bundle_sha256": content_hash({"bundle": suffix}),
        "policy_id": "POLICY-1",
        "policy_digest": content_hash({"policy": "v1"}),
    }


def _entry_fields(
    suffix: str = "1",
    *,
    sequence: int = 1,
    previous: str = GENESIS_HASH,
    **over: Any,
) -> dict[str, Any]:
    """The eighteen core fields of a :class:`RegistryEntry`, ready for ``create``."""
    registration = _registration(suffix)
    certified = registration.pop("certified")
    fields: dict[str, Any] = {
        "sequence": sequence,
        "registry_id": "REG-1",
        "certified": certified,
        "status": STATUS_CERTIFIED if certified else STATUS_NOT_CERTIFIED,
        "previous_hash": previous,
        **registration,
    }
    fields.update(over)
    return fields


def _populated(count: int = 3) -> CertificationRegistry:
    registry = CertificationRegistry("REG-1")
    for index in range(1, count + 1):
        registry.register(**_registration(str(index), certified=index % 2 == 1))
    return registry


# --- module constants ------------------------------------------------------------


def test_the_registry_declares_its_snapshot_format_and_genesis() -> None:
    """A snapshot names its own format; the chain starts from a declared genesis."""
    assert REGISTRY_FORMAT == "ucos-assurance-certification-registry/1.0.0"
    assert GENESIS_HASH == "0" * 64
    assert len(GENESIS_HASH) == 64


def test_status_values_are_the_two_derived_outcomes() -> None:
    """Status is derived from the verdict, never hand-set, so there are exactly two."""
    assert STATUS_CERTIFIED == "certified"
    assert STATUS_NOT_CERTIFIED == "not-certified"
    assert STATUS_CERTIFIED != STATUS_NOT_CERTIFIED


# --- RegistryEntry ---------------------------------------------------------------


def test_an_entry_hashes_its_own_canonical_core() -> None:
    """The entry hash is a commitment to every field the entry declares."""
    entry = RegistryEntry.create(**_entry_fields())
    assert entry.entry_hash == entry.recompute_hash()
    assert entry.intact is True


def test_an_entry_is_immutable() -> None:
    entry = RegistryEntry.create(**_entry_fields())
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.status = STATUS_NOT_CERTIFIED  # type: ignore[misc]


def test_entry_identity_is_reproducible_from_identical_content() -> None:
    """Determinism: no wall-clock or ambient state leaks into a registration's identity."""
    assert RegistryEntry.create(**_entry_fields()).entry_hash == (
        RegistryEntry.create(**_entry_fields()).entry_hash
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "sequence",
        "registry_id",
        "certification_id",
        "subject_id",
        "version",
        "status",
        "certified",
        "certificate_sha256",
        "certificate_intact",
        "validation_plan_sha256",
        "certification_plan_sha256",
        "validation_execution_sha256",
        "certification_execution_sha256",
        "evidence_id",
        "evidence_bundle_sha256",
        "policy_id",
        "policy_digest",
        "previous_hash",
    ],
)
def test_every_core_field_participates_in_the_entry_hash(field_name: str) -> None:
    """A field outside the hash would be an editable region of an immutable record."""
    baseline = RegistryEntry.create(**_entry_fields())
    original = getattr(baseline, field_name)
    altered_value: Any = (
        original + 1
        if isinstance(original, int) and not isinstance(original, bool)
        else (not original if isinstance(original, bool) else f"{original}-altered")
    )
    altered = RegistryEntry.create(**_entry_fields(**{field_name: altered_value}))
    assert altered.entry_hash != baseline.entry_hash, field_name


def test_a_retroactive_edit_is_detected_by_the_entry_itself() -> None:
    """The core promise: an edited entry cannot recompute its way back to intact."""
    entry = RegistryEntry.create(**_entry_fields())
    tampered = dataclasses.replace(entry, subject_id="SUBJ-IMPOSTOR")
    assert tampered.entry_hash == entry.entry_hash
    assert tampered.recompute_hash() != tampered.entry_hash
    assert tampered.intact is False


def test_entry_to_dict_carries_the_full_core_plus_its_hash() -> None:
    """The wire form is self-verifying: the core and the hash over it travel together."""
    entry = RegistryEntry.create(**_entry_fields())
    payload = entry.to_dict()
    assert payload["entry_hash"] == entry.entry_hash
    assert payload["certification_id"] == "CERT-1"
    assert payload["previous_hash"] == GENESIS_HASH
    assert payload["status"] == STATUS_CERTIFIED
    assert content_hash({k: v for k, v in payload.items() if k != "entry_hash"}) == entry.entry_hash


def test_entry_provenance_exposes_the_full_replay_chain() -> None:
    """Given any entry, the run that produced it can be located and replayed."""
    entry = RegistryEntry.create(**_entry_fields())
    provenance = entry_provenance(entry)
    assert set(provenance) == set(_PROVENANCE_KEYS)
    for key in _PROVENANCE_KEYS:
        assert provenance[key] == getattr(entry, key)
        assert provenance[key], f"{key} is empty, so the chain is not replayable"


# --- CertificationRegistry: construction -----------------------------------------


def test_a_registry_requires_a_non_empty_identity() -> None:
    """An anonymous registry cannot be attributed, so it is refused at construction."""
    for bad_id in ("", None, 7):
        with pytest.raises(AssuranceRegistryError):
            CertificationRegistry(bad_id)  # type: ignore[arg-type]


def test_an_empty_registry_starts_at_genesis() -> None:
    registry = CertificationRegistry("REG-1")
    assert registry.registry_id == "REG-1"
    assert registry.entries == ()
    assert len(registry) == 0
    assert registry.head_hash == GENESIS_HASH
    assert registry.verify() is True


def test_a_registry_can_be_rehydrated_from_existing_entries() -> None:
    """A snapshot round-trips: rehydrated entries keep their chain and verify."""
    source = _populated(2)
    rehydrated = CertificationRegistry("REG-1", source.entries)
    assert rehydrated.verify() is True
    assert rehydrated.head_hash == source.head_hash
    assert rehydrated.certification_ids() == source.certification_ids()


def test_the_entries_view_cannot_mutate_the_registry() -> None:
    """``entries`` hands out a tuple snapshot, not the append-only list itself."""
    registry = _populated(1)
    assert isinstance(registry.entries, tuple)
    assert len(registry.entries) == 1
    assert len(registry) == 1


# --- CertificationRegistry: registration -----------------------------------------


def test_registering_a_certification_appends_a_chained_entry() -> None:
    registry = CertificationRegistry("REG-1")
    entry = registry.register(**_registration("1"))
    assert entry.sequence == 1
    assert entry.registry_id == "REG-1"
    assert entry.previous_hash == GENESIS_HASH
    assert registry.head_hash == entry.entry_hash
    assert len(registry) == 1


def test_each_registration_chains_onto_its_predecessor() -> None:
    """The head hash is a commitment to the whole history, entry by entry."""
    registry = CertificationRegistry("REG-1")
    first = registry.register(**_registration("1"))
    second = registry.register(**_registration("2"))
    third = registry.register(**_registration("3"))
    assert (first.sequence, second.sequence, third.sequence) == (1, 2, 3)
    assert second.previous_hash == first.entry_hash
    assert third.previous_hash == second.entry_hash
    assert registry.head_hash == third.entry_hash
    assert registry.verify() is True


def test_status_is_derived_from_the_certification_verdict() -> None:
    """Status is never hand-set: it follows the verdict the run actually reached."""
    registry = CertificationRegistry("REG-1")
    certified = registry.register(**_registration("1", certified=True))
    refused = registry.register(**_registration("2", certified=False))
    assert (certified.certified, certified.status) == (True, STATUS_CERTIFIED)
    assert (refused.certified, refused.status) == (False, STATUS_NOT_CERTIFIED)


def test_re_registering_a_certification_id_is_refused() -> None:
    """Append-only: an earlier determination is never silently replaced."""
    registry = CertificationRegistry("REG-1")
    registry.register(**_registration("1"))
    with pytest.raises(AssuranceRegistryError) as caught:
        registry.register(**_registration("1"))
    assert caught.value.context["certification_id"] == "CERT-1"
    assert caught.value.context["registry"] == "REG-1"
    assert len(registry) == 1, "the refused registration must not have been appended"


def test_a_registration_requires_a_non_empty_certification_id() -> None:
    """An unidentifiable registration is undiscoverable, which defeats the registry."""
    registry = CertificationRegistry("REG-1")
    for bad_id in ("", None, 12):
        payload = _registration("1")
        payload["certification_id"] = bad_id
        with pytest.raises(AssuranceRegistryError):
            registry.register(**payload)
    assert len(registry) == 0


def test_registering_onto_a_broken_chain_is_refused() -> None:
    """A registry that cannot prove its integrity never appends onto the doubt."""
    registry = _populated(2)
    tampered = list(registry.entries)
    tampered[0] = dataclasses.replace(tampered[0], subject_id="SUBJ-IMPOSTOR")
    broken = CertificationRegistry("REG-1", tampered)
    with pytest.raises(AssuranceRegistryError) as caught:
        broken.register(**_registration("9"))
    assert caught.value.context["entries"] == 2
    assert len(broken) == 2, "a refused registration must not extend a broken chain"


# --- CertificationRegistry: queries ----------------------------------------------


def test_get_returns_the_registered_entry_or_none() -> None:
    """A miss is reported as absence, never as a fabricated entry."""
    registry = _populated(2)
    found = registry.get("CERT-2")
    assert found is not None
    assert found.certification_id == "CERT-2"
    assert registry.get("CERT-UNKNOWN") is None


def test_entries_can_be_located_by_subject() -> None:
    registry = CertificationRegistry("REG-1")
    registry.register(**_registration("1"))
    second = _registration("2")
    second["subject_id"] = "SUBJ-1"
    registry.register(**second)
    assert {entry.certification_id for entry in registry.by_subject("SUBJ-1")} == {
        "CERT-1",
        "CERT-2",
    }
    assert registry.by_subject("SUBJ-ABSENT") == ()


def test_entries_can_be_located_by_authorizing_policy() -> None:
    registry = _populated(2)
    digest = content_hash({"policy": "v1"})
    assert len(registry.by_policy(digest)) == 2
    assert registry.by_policy("some-other-digest") == ()


def test_certification_ids_are_reported_in_registration_order() -> None:
    """Sequence order is the record's order; it is never re-sorted for presentation."""
    assert _populated(3).certification_ids() == ("CERT-1", "CERT-2", "CERT-3")


def test_counts_by_status_separate_certified_from_refused() -> None:
    registry = _populated(3)
    assert registry.count_by_status() == {STATUS_CERTIFIED: 2, STATUS_NOT_CERTIFIED: 1}
    assert registry.counts() == {"entries": 3, "certified": 2, "not_certified": 1}


def test_an_unrecognized_status_is_counted_honestly_rather_than_dropped() -> None:
    """A rehydrated entry with a status this version does not know is still reported."""
    rehydrated = RegistryEntry.create(**_entry_fields(status="revoked"))
    registry = CertificationRegistry("REG-1", [rehydrated])
    assert registry.count_by_status() == {
        STATUS_CERTIFIED: 0,
        STATUS_NOT_CERTIFIED: 0,
        "revoked": 1,
    }
    assert registry.counts() == {"entries": 1, "certified": 0, "not_certified": 0}


def test_policy_drift_names_certifications_authorized_by_a_different_policy() -> None:
    """Drift is an honest record, not an error — intelligence must be able to see it."""
    registry = _populated(2)
    current = content_hash({"policy": "v1"})
    assert registry.policy_drift(current) == ()
    assert registry.policy_drift(content_hash({"policy": "v2"})) == ("CERT-1", "CERT-2")


# --- CertificationRegistry: integrity --------------------------------------------


def test_a_registry_of_untouched_entries_verifies() -> None:
    registry = _populated(3)
    assert registry.verify() is True
    registry.require_intact()


def test_a_tampered_entry_breaks_verification() -> None:
    """Detection condition 1: the entry no longer hashes to its recorded hash."""
    registry = _populated(3)
    entries = list(registry.entries)
    entries[1] = dataclasses.replace(entries[1], certified=not entries[1].certified)
    assert CertificationRegistry("REG-1", entries).verify() is False


def test_a_renumbered_entry_breaks_verification() -> None:
    """Detection condition 2: sequence must equal the entry's position in the chain."""
    registry = _populated(2)
    entries = list(registry.entries)
    entries[1] = RegistryEntry.create(
        **_entry_fields("2", sequence=99, previous=entries[0].entry_hash)
    )
    assert CertificationRegistry("REG-1", entries).verify() is False


def test_a_re_parented_entry_breaks_verification() -> None:
    """Detection condition 3: an entry must chain onto its actual predecessor."""
    registry = _populated(2)
    entries = list(registry.entries)
    entries[1] = RegistryEntry.create(**_entry_fields("2", sequence=2, previous="f" * 64))
    assert CertificationRegistry("REG-1", entries).verify() is False


def test_a_first_entry_that_skips_genesis_breaks_verification() -> None:
    """The chain must be anchored: entry one parents onto genesis and nothing else."""
    orphan = RegistryEntry.create(**_entry_fields("1", sequence=1, previous="a" * 64))
    assert CertificationRegistry("REG-1", [orphan]).verify() is False


def test_a_dropped_entry_breaks_verification() -> None:
    """Removal is detectable too: the survivors no longer form a contiguous chain."""
    registry = _populated(3)
    entries = list(registry.entries)
    del entries[1]
    assert CertificationRegistry("REG-1", entries).verify() is False


def test_require_intact_raises_on_a_broken_chain() -> None:
    """Fail-closed: the integrity failure is auditable, naming the registry and size."""
    registry = _populated(2)
    entries = list(registry.entries)
    entries[0] = dataclasses.replace(entries[0], version="9.9.9")
    with pytest.raises(AssuranceRegistryError) as caught:
        CertificationRegistry("REG-1", entries).require_intact()
    assert caught.value.context["registry"] == "REG-1"
    assert caught.value.context["entries"] == 2


# --- CertificationRegistry: projections ------------------------------------------


def test_observations_expose_the_numeric_facts_policy_metrics_measure() -> None:
    """The registry's own metrics are derived facts, never separately maintained state."""
    registry = _populated(3)
    assert registry.observations() == {
        "registry.entries": 3.0,
        "registry.certified": 2.0,
        "registry.not_certified": 1.0,
        "registry.chain_intact": 1.0,
    }


def test_a_broken_chain_is_reported_as_a_zero_observation() -> None:
    """The integrity fact is measured, so a policy metric can gate on it."""
    registry = _populated(2)
    entries = list(registry.entries)
    entries[0] = dataclasses.replace(entries[0], policy_id="POLICY-IMPOSTOR")
    broken = CertificationRegistry("REG-1", entries)
    assert broken.observations()["registry.chain_intact"] == 0.0


def test_the_snapshot_is_complete_and_self_describing() -> None:
    registry = _populated(2)
    snapshot = registry.snapshot()
    assert snapshot["registry_format"] == REGISTRY_FORMAT
    assert snapshot["registry_id"] == "REG-1"
    assert snapshot["head_hash"] == registry.head_hash
    assert snapshot["chain_intact"] is True
    assert snapshot["counts"] == {"entries": 2, "certified": 1, "not_certified": 1}
    assert snapshot["certification_ids"] == ["CERT-1", "CERT-2"]
    assert [entry["entry_hash"] for entry in snapshot["entries"]] == [
        entry.entry_hash for entry in registry.entries
    ]


def test_the_snapshot_reports_a_broken_chain_rather_than_concealing_it() -> None:
    """A registry never reports itself intact when it is not."""
    registry = _populated(2)
    entries = list(registry.entries)
    entries[1] = dataclasses.replace(entries[1], evidence_id="EVID-IMPOSTOR")
    assert CertificationRegistry("REG-1", entries).snapshot()["chain_intact"] is False


def test_to_dict_is_the_snapshot() -> None:
    registry = _populated(2)
    assert registry.to_dict() == registry.snapshot()


def test_the_fingerprint_is_deterministic_and_content_derived() -> None:
    """Two registries built from identical registrations fingerprint identically."""
    first = _populated(2)
    second = _populated(2)
    assert first.fingerprint() == second.fingerprint()
    assert first.fingerprint() == content_hash(first.snapshot())

    third = _populated(3)
    assert third.fingerprint() != first.fingerprint()


def test_the_fingerprint_changes_when_the_chain_is_tampered_with() -> None:
    registry = _populated(2)
    entries = list(registry.entries)
    entries[0] = dataclasses.replace(entries[0], subject_id="SUBJ-IMPOSTOR")
    assert CertificationRegistry("REG-1", entries).fingerprint() != registry.fingerprint()
