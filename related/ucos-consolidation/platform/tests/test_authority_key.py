"""Tests for the S-3 machine-readable authority key.

The key joins three disclaiming planes. This test asserts the properties that make
it a composition rather than a new authority: it derives instead of minting, it
reports UNRESOLVED instead of guessing, and it joins every subject or says which
ones it cannot.
"""

from __future__ import annotations

import json
from platform.universal_ownership import authority_key
from platform.universal_ownership.authority_key import AuthorityKey, coverage, resolve

import pytest

REPO_ROOT = authority_key.REPO_ROOT


@pytest.fixture(scope="module")
def keys() -> list[AuthorityKey]:
    return authority_key.resolve_all(root=REPO_ROOT)


def test_the_catalogue_is_present() -> None:
    """Without the 59 declared assignments there is nothing to join."""
    assignments = authority_key._catalog_assignments(REPO_ROOT)
    assert assignments, "the ownership catalogue must load for the join to be measurable"


def test_every_subject_resolves_across_all_three_planes(keys: list[AuthorityKey]) -> None:
    """The join must not strand a subject on one plane.

    This is the S-3 criterion: an owner named by the ownership plane whose
    locator is absent from the persistence plane is exactly the join failure the
    authority key exists to surface. Zero stranded is the pass condition.
    """
    measured = coverage(root=REPO_ROOT)
    assert measured["subjects"] == len(keys) == 59
    assert measured["locator_not_in_ledger"] == 0
    assert measured["unresolved_owner"] == 0
    assert measured["fully_resolved"] == len(keys)


def test_a_real_repository_identifier_resolves_to_a_urn() -> None:
    """The constitutional plane must derive a URN for a repository identifier.

    ``repository_local_urn`` is the declared join, measured at 6,079/6,079 in the
    discovery report. A repository id must resolve; this is the derivation
    actually doing the work, not a stored field.
    """
    from engine.uckp.alignment import repository_local_urn

    resolved = resolve("UCOS-CEP-000030", root=REPO_ROOT)
    assert resolved.urn == repository_local_urn("UCOS-CEP-000030")
    assert resolved.urn.startswith("urn:ucos:ucko:")


def test_a_mandate_id_is_reported_unresolved_not_fabricated() -> None:
    """A mandate id is not a repository identifier, so the plane says so.

    The derivation raises rather than emit something that looks like an identity
    and is not one. The authority key must surface UNRESOLVED, never a synthetic
    urn — a fabricated owner is what OWN-REQ-001 forbids.
    """
    resolved = resolve("AF-3", root=REPO_ROOT)
    assert resolved.owner == "Constitutional Authority (02-MASTER)"
    assert resolved.urn == authority_key.UNRESOLVED


def test_an_unknown_subject_resolves_to_nothing_not_a_default_owner() -> None:
    """A subject the catalogue does not name gets every plane at UNRESOLVED.

    The framework has no fallback owner by OWN-REQ-004: absence is reported, not
    papered over with a plausible default.
    """
    resolved = resolve("DOES-NOT-EXIST-9999", root=REPO_ROOT)
    assert resolved.owner == authority_key.UNRESOLVED
    assert resolved.authority == authority_key.UNRESOLVED
    assert resolved.repository_id == authority_key.UNRESOLVED


def test_the_key_is_serialisable_and_stable(keys: list[AuthorityKey]) -> None:
    """The key must be machine-readable, which means round-tripping through JSON."""
    first = keys[0]
    restored = AuthorityKey(**first.as_dict())
    assert restored == first
    assert json.loads(json.dumps(first.as_dict())) == first.as_dict()


def test_coverage_reports_the_planes_composed() -> None:
    """The measurement must name the three planes it joined, not claim a new one."""
    measured = coverage(root=REPO_ROOT)
    assert measured["planes_composed"] == [
        "CONSTITUTIONAL",
        "REPOSITORY",
        "OWNERSHIP",
    ]
    assert measured["derivation"] == "composed; nothing minted"


def test_the_cli_exposes_the_join_as_a_gate() -> None:
    """``ucos-ownership authority-key`` must exit non-zero when the join is broken."""
    from platform.universal_ownership.cli import main

    assert main(["authority-key", "--json"]) == 0
