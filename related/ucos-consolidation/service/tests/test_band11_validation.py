"""EC3-B11-U12 — Band-11 completion validation tests (all checks, pass + fail branches)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from service.band11 import make_band11_completion
from service.band11_meta import EXPECTED_UNITS
from service.band11_traceability import build_band11_traceability
from service.band11_validation import (
    Band11ValidationSubject,
    BandAllUnitsCertifiedCheck,
    BandFoundingAcyclicCheck,
    BandIdentifiedCheck,
    BandIndependenceCheck,
    BandInventoryCompleteCheck,
    BandMetaClassCoverageCheck,
    BandMetaModelIntegrationCheck,
    BandNonConstitutiveCheck,
    BandNonProjectionCheck,
    BandProvisionalDisclosureCheck,
    BandRelationshipClosureCheck,
    BandReuseIntegrityCheck,
    BandTraceabilityRootedCheck,
    BandTypedCheck,
    BandValidStateCheck,
    BandValueFidelityCheck,
    BandVersionedCheck,
    band11_checks,
    validate_band11,
)

_FULL_INTEGRATION = {
    "all_members_certified": True,
    "closure_SMI_01": True,
    "relationship_closure_SMI_02": True,
    "totality_SMI_03": True,
    "founding_acyclic_SMI_04": True,
    "reuse_by_reference_SMI_05": True,
    "non_constitutive_SMI_06": True,
    "non_projection_SMI_07": True,
    "map_resolves": True,
}


def _completion():
    return make_band11_completion(
        "ucos.service.band11.completion",
        "ucos.core.band-completion",
        tuple((u, f"UCOS-CERT-{u}-{'a' * 16}", True) for u in EXPECTED_UNITS),
        meta_model_id="UCOS-METAMODEL-ucos.service.metamodel.universal-" + "b" * 16,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )


def _subject() -> Band11ValidationSubject:
    c = _completion()
    trace = build_band11_traceability(c, unit="EC3-B11-U12", forward=("x", "y"))
    return Band11ValidationSubject.from_completion(c, trace)


def _passes(check, subject) -> bool:
    return check.evaluate(subject).passed


# ---------------------------------------------------------------------------
# Every check passes on a well-formed subject
# ---------------------------------------------------------------------------


def test_all_checks_pass_on_wellformed_subject():
    subject = _subject()
    for check in band11_checks():
        assert _passes(check, subject), check.check_id


def test_shared_and_band_check_ids_present():
    ids = {c.check_id for c in band11_checks()}
    shared = {
        "traceability-rooted",
        "meta-class-single",
        "foundation-reuse-integrity",
        "service-value-fidelity",
        "founding-acyclic",
        "meta-relationships-closed",
        "provisional-state-disclosure",
    }
    assert shared <= ids
    assert {"band11-inventory-complete", "band11-all-units-certified", "non-constitutive"} <= ids


# ---------------------------------------------------------------------------
# Single-condition fail branches
# ---------------------------------------------------------------------------


def test_typed_check_fails_when_untyped():
    assert _passes(BandTypedCheck(), replace(_subject(), type_tag="  ")) is False


def test_identified_check_fails_on_bad_id():
    assert _passes(BandIdentifiedCheck(), replace(_subject(), target_id="X-1")) is False


def test_value_fidelity_fails_on_bad_digest():
    assert _passes(BandValueFidelityCheck(), replace(_subject(), value_digest="zz")) is False


def test_inventory_complete_fails():
    assert _passes(BandInventoryCompleteCheck(), replace(_subject(), inventory_complete=False)) is False
    assert _passes(BandInventoryCompleteCheck(), replace(_subject(), unit_count=3)) is False


def test_all_units_certified_fails():
    assert _passes(BandAllUnitsCertifiedCheck(), replace(_subject(), all_units_certified=False)) is False


def test_meta_class_coverage_fails():
    bad = replace(_subject(), meta_class_coverage_complete=False)
    assert _passes(BandMetaClassCoverageCheck(), bad) is False


def test_relationship_closure_fails():
    assert _passes(BandRelationshipClosureCheck(), replace(_subject(), integration_closed=False)) is False


def test_metamodel_integration_fails():
    assert _passes(BandMetaModelIntegrationCheck(), replace(_subject(), integration_closed=False)) is False


def test_founding_acyclic_fails():
    assert _passes(BandFoundingAcyclicCheck(), replace(_subject(), dependency_acyclic=False)) is False


def test_versioned_fails():
    assert _passes(BandVersionedCheck(), replace(_subject(), version="")) is False


def test_valid_state_fails():
    assert _passes(BandValidStateCheck(), replace(_subject(), band_state="bogus")) is False


def test_independence_fails_on_named_and_selected_tech():
    assert _passes(BandIndependenceCheck(), replace(_subject(), names_technology=True)) is False
    assert _passes(BandIndependenceCheck(), replace(_subject(), selects_technology=True)) is False


def test_non_projection_fails():
    assert _passes(BandNonProjectionCheck(), replace(_subject(), non_projection=False)) is False


# ---------------------------------------------------------------------------
# Multi-branch fail paths
# ---------------------------------------------------------------------------


def test_reuse_integrity_all_fail_branches():
    chk = BandReuseIntegrityCheck()
    assert _passes(chk, replace(_subject(), substrate_refs=())) is False
    assert _passes(chk, replace(_subject(), all_units_certified=False)) is False
    assert _passes(chk, replace(_subject(), reuses_by_reference=False)) is False


def test_non_constitutive_all_fail_branches():
    chk = BandNonConstitutiveCheck()
    assert _passes(chk, replace(_subject(), confers_authority=True)) is False
    assert _passes(chk, replace(_subject(), embeds_secret=True)) is False
    assert _passes(chk, replace(_subject(), selects_technology=True)) is False
    assert _passes(chk, replace(_subject(), non_constitutive=False)) is False


def test_provisional_disclosure_fails_when_absent():
    assert _passes(BandProvisionalDisclosureCheck(), replace(_subject(), disclosure={})) is False


def test_traceability_rooted_all_fail_branches():
    chk = BandTraceabilityRootedCheck()
    assert _passes(chk, replace(_subject(), provenance_chain=())) is False
    assert _passes(chk, replace(_subject(), provenance_chain=("WRONG", "11-SERVICE@x"))) is False
    assert _passes(chk, replace(_subject(), provenance_chain=("BAND-11", "nope"))) is False


# ---------------------------------------------------------------------------
# End-to-end validation through the EC-1 engine
# ---------------------------------------------------------------------------


def test_validate_band11_accepts_wellformed_completion():
    c = _completion()
    trace = build_band11_traceability(c, unit="EC3-B11-U12", forward=("a", "b"))
    validation = validate_band11(c, trace)
    assert validation.accepted is True
    assert all(f.passed for f in validation.report.findings)


def test_validate_band11_strict_raises_on_bad_completion():
    # An incomplete inventory produces blocking failures; strict enforcement raises.
    c = _completion()
    short = replace(c, units=c.units[:-1])
    trace = build_band11_traceability(short, unit="EC3-B11-U12", forward=("a", "b"))
    with pytest.raises(Exception):
        validate_band11(short, trace, strict=True)
