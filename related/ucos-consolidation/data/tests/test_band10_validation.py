"""EC3-B10-U12 — Band-10 completion validation tests (all checks, pass + fail branches)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from data.band10 import make_band10_completion
from data.band10_meta import EXPECTED_UNITS
from data.band10_traceability import build_band10_traceability
from data.band10_validation import (
    Band10ValidationSubject,
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
    band10_checks,
    validate_band10,
)
from engine.tests import assert_every_check_can_refuse

_FULL_INTEGRATION = {
    "all_members_certified": True,
    "closure_DMI_01": True,
    "relationship_closure_DMI_02": True,
    "totality_DMI_03": True,
    "founding_acyclic_DMI_04": True,
    "reuse_by_reference_DMI_05": True,
    "non_constitutive_DMI_06": True,
    "non_projection_DMI_07": True,
    "map_resolves": True,
}


def _completion():
    return make_band10_completion(
        "ucos.data.band10.completion",
        "ucos.core.band-completion",
        tuple((u, f"UCOS-CERT-{u}-{'a' * 16}", True) for u in EXPECTED_UNITS),
        meta_model_id="UCOS-METAMODEL-ucos.data.metamodel.universal-" + "b" * 16,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )


def _subject() -> Band10ValidationSubject:
    c = _completion()
    trace = build_band10_traceability(c, unit="EC3-B10-U12", forward=("x", "y"))
    return Band10ValidationSubject.from_completion(c, trace)


def _passes(check, subject) -> bool:
    return check.evaluate(subject).passed


# ---------------------------------------------------------------------------
# Every check passes on a well-formed subject
# ---------------------------------------------------------------------------


def test_all_checks_pass_on_wellformed_subject():
    subject = _subject()
    for check in band10_checks():
        assert _passes(check, subject), check.check_id


def test_shared_and_band_check_ids_present():
    ids = {c.check_id for c in band10_checks()}
    shared = {
        "traceability-rooted",
        "meta-class-single",
        "foundation-reuse-integrity",
        "data-value-fidelity",
        "founding-acyclic",
        "meta-relationships-closed",
        "provisional-state-disclosure",
    }
    assert shared <= ids
    assert {"band10-inventory-complete", "band10-all-units-certified", "non-constitutive"} <= ids


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
    assert (
        _passes(BandInventoryCompleteCheck(), replace(_subject(), inventory_complete=False))
        is False
    )
    assert _passes(BandInventoryCompleteCheck(), replace(_subject(), unit_count=3)) is False


def test_all_units_certified_fails():
    assert (
        _passes(BandAllUnitsCertifiedCheck(), replace(_subject(), all_units_certified=False))
        is False
    )


def test_meta_class_coverage_fails():
    bad = replace(_subject(), meta_class_coverage_complete=False)
    assert _passes(BandMetaClassCoverageCheck(), bad) is False


def test_relationship_closure_fails():
    assert (
        _passes(BandRelationshipClosureCheck(), replace(_subject(), integration_closed=False))
        is False
    )


def test_metamodel_integration_fails():
    assert (
        _passes(BandMetaModelIntegrationCheck(), replace(_subject(), integration_closed=False))
        is False
    )


def test_founding_acyclic_fails():
    assert (
        _passes(BandFoundingAcyclicCheck(), replace(_subject(), dependency_acyclic=False)) is False
    )


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
    assert _passes(chk, replace(_subject(), provenance_chain=("WRONG", "10-DATA@x"))) is False
    assert _passes(chk, replace(_subject(), provenance_chain=("BAND-10", "nope"))) is False


# ---------------------------------------------------------------------------
# End-to-end validation through the EC-1 engine
# ---------------------------------------------------------------------------


def test_validate_band10_accepts_wellformed_completion():
    c = _completion()
    trace = build_band10_traceability(c, unit="EC3-B10-U12", forward=("a", "b"))
    validation = validate_band10(c, trace)
    assert validation.accepted is True
    assert all(f.passed for f in validation.report.findings)


def test_validate_band10_strict_raises_on_bad_completion():
    # An incomplete inventory produces blocking failures; strict enforcement raises.
    c = _completion()
    short = replace(c, units=c.units[:-1])
    trace = build_band10_traceability(short, unit="EC3-B10-U12", forward=("a", "b"))
    with pytest.raises(Exception):
        validate_band10(short, trace, strict=True)


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), band10_checks())
