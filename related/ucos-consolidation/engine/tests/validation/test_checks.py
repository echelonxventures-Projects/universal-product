"""TASK-000049 — Validation check tests (TASK-000046 architecture)."""

from __future__ import annotations

from engine.validation.checks import (
    DependencyClosureCheck,
    DisclosureCheck,
    IdentityCheck,
    ImageDigestCheck,
    ProvenanceCheck,
    SbomCheck,
    SignatureCheck,
    default_checks,
)
from engine.validation.contracts import CheckStatus, Severity

from .conftest import mutate

# -- suite --------------------------------------------------------------------


def test_default_checks_are_sorted_and_unique():
    checks = default_checks()
    ids = [c.check_id for c in checks]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids)) == 7


def test_all_checks_pass_on_valid_subject(valid_subject):
    for check in default_checks():
        finding = check.evaluate(valid_subject)
        assert finding.status is CheckStatus.PASS, check.check_id
        assert finding.check_id == check.check_id


# -- provenance ---------------------------------------------------------------


def test_provenance_empty_fails(valid_subject):
    finding = ProvenanceCheck().evaluate(mutate(valid_subject, provenance_chain=()))
    assert finding.status is CheckStatus.FAIL


def test_provenance_nonstring_link_fails(valid_subject):
    finding = ProvenanceCheck().evaluate(
        mutate(valid_subject, provenance_chain=("BP-DATA-0001", ""))
    )
    assert finding.status is CheckStatus.FAIL


def test_provenance_wrong_head_fails(valid_subject):
    finding = ProvenanceCheck().evaluate(mutate(valid_subject, provenance_chain=("WRONG", "x")))
    assert finding.status is CheckStatus.FAIL
    assert finding.details["head"] == "WRONG"


# -- signature ----------------------------------------------------------------


def test_signature_incomplete_fails(valid_subject):
    broken = dict(valid_subject.signature)
    broken.pop("payload_sha256")
    finding = SignatureCheck().evaluate(mutate(valid_subject, signature=broken))
    assert finding.status is CheckStatus.FAIL
    assert "payload_sha256" in finding.details["missing"]


# -- sbom ---------------------------------------------------------------------


def test_sbom_absent_fails(valid_subject):
    finding = SbomCheck().evaluate(mutate(valid_subject, sbom={}))
    assert finding.status is CheckStatus.FAIL


def test_sbom_no_components_fails(valid_subject):
    finding = SbomCheck().evaluate(
        mutate(valid_subject, sbom={"sbom_format": "ucos-sbom/1.0.0", "components": []})
    )
    assert finding.status is CheckStatus.FAIL


# -- disclosure ---------------------------------------------------------------


def test_disclosure_absent_fails(valid_subject):
    finding = DisclosureCheck().evaluate(mutate(valid_subject, disclosure=None))
    assert finding.status is CheckStatus.FAIL


# -- dependency closure -------------------------------------------------------


def test_closure_empty_fails(valid_subject):
    finding = DependencyClosureCheck().evaluate(mutate(valid_subject, dependency_closure=()))
    assert finding.status is CheckStatus.FAIL


def test_closure_multiple_roots_fails(valid_subject):
    closure = (
        {"blueprint_id": "A", "role": "root", "package_sha256": "x"},
        {"blueprint_id": "B", "role": "root", "package_sha256": "y"},
    )
    finding = DependencyClosureCheck().evaluate(mutate(valid_subject, dependency_closure=closure))
    assert finding.status is CheckStatus.FAIL
    assert finding.details["roots"] == 2


def test_closure_unpinned_member_fails(valid_subject):
    closure = ({"blueprint_id": "A", "role": "root", "package_sha256": ""},)
    finding = DependencyClosureCheck().evaluate(mutate(valid_subject, dependency_closure=closure))
    assert finding.status is CheckStatus.FAIL
    assert "A" in finding.details["unpinned"]


def test_closure_root_hash_mismatch_fails(valid_subject):
    closure = ({"blueprint_id": "A", "role": "root", "package_sha256": "deadbeef"},)
    finding = DependencyClosureCheck().evaluate(
        mutate(valid_subject, dependency_closure=closure, package_sha256="not-deadbeef")
    )
    assert finding.status is CheckStatus.FAIL


# -- image digest -------------------------------------------------------------


def test_image_not_digest_pinned_fails(valid_subject):
    finding = ImageDigestCheck().evaluate(
        mutate(valid_subject, image_reference="ucos-runtime/bp-data-0001:latest")
    )
    assert finding.status is CheckStatus.FAIL


# -- identity (advisory) ------------------------------------------------------


def test_identity_malformed_is_advisory_failure(valid_subject):
    finding = IdentityCheck().evaluate(mutate(valid_subject, runtime_id="not-an-id"))
    assert finding.status is CheckStatus.FAIL
    assert finding.severity is Severity.ADVISORY


def test_identity_none_fails(valid_subject):
    finding = IdentityCheck().evaluate(mutate(valid_subject, runtime_id=None))
    assert finding.status is CheckStatus.FAIL
