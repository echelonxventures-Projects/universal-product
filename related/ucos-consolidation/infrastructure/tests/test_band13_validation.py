"""EC3-B13-U11 — Band-13 completion validation tests (BRC/BCC checks, pass + fail branches)."""

from __future__ import annotations

from dataclasses import replace

from engine.tests import assert_every_check_can_refuse
from infrastructure.band13 import make_band13_completion
from infrastructure.band13_meta import EXPECTED_UNITS
from infrastructure.band13_traceability import build_band13_traceability
from infrastructure.band13_validation import (
    Band13ValidationSubject,
    BandAllUnitsCertifiedCheck,
    BandFoundingAcyclicCheck,
    BandIdentifiedCheck,
    BandIndependenceCheck,
    BandIntegrationClosedCheck,
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
    band13_checks,
    validate_band13,
)

_FULL_INTEGRATION = {
    "all_concerns_certified": True,
    "leaf_closure_complete": True,
    "graph_downward_only": True,
    "graph_acyclic": True,
    "all_nodes_present": True,
    "ownership_disjoint": True,
    "all_edges_certified": True,
    "uimm_determination_complete": True,
}


def _completion():
    return make_band13_completion(
        "ucos.infrastructure.band13.completion",
        "ucos.core.band-completion",
        tuple((u, "a" * 64, True) for u in EXPECTED_UNITS),
        meta_model_id="b" * 64,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )


def _subject() -> Band13ValidationSubject:
    completion = _completion()
    trace = build_band13_traceability(
        completion, unit="EC3-B13-U11", forward=(completion.band_id, "X", "Y", "Z")
    )
    return Band13ValidationSubject.from_completion(completion, trace)


# ---------------------------------------------------------------------------
# Happy path — the full suite accepts a well-formed completion
# ---------------------------------------------------------------------------


def test_validate_band13_accepts_wellformed_completion():
    completion = _completion()
    trace = build_band13_traceability(
        completion, unit="EC3-B13-U11", forward=(completion.band_id, "X", "Y", "Z")
    )
    result = validate_band13(completion, trace)
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert all(f.passed for f in result.report.findings)


def test_band13_checks_count_and_ids_unique():
    checks = band13_checks()
    ids = [c.check_id for c in checks]
    assert len(ids) == len(set(ids))
    # the shared CCE-required ids are emitted
    assert {
        "traceability-rooted",
        "meta-class-single",
        "foundation-reuse-integrity",
        "infra-capability-value-fidelity",
        "founding-acyclic",
        "meta-relationships-closed",
        "provisional-state-disclosure",
    } <= set(ids)


# ---------------------------------------------------------------------------
# Per-check pass + fail branches
# ---------------------------------------------------------------------------


def test_typed_check():
    s = _subject()
    assert BandTypedCheck().evaluate(s).passed is True
    assert BandTypedCheck().evaluate(replace(s, type_tag="  ")).passed is False


def test_identified_check():
    s = _subject()
    assert BandIdentifiedCheck().evaluate(s).passed is True
    assert BandIdentifiedCheck().evaluate(replace(s, target_id="X-1")).passed is False


def test_value_fidelity_check():
    s = _subject()
    assert BandValueFidelityCheck().evaluate(s).passed is True
    assert BandValueFidelityCheck().evaluate(replace(s, value_digest="zz")).passed is False


def test_inventory_complete_check():
    s = _subject()
    assert BandInventoryCompleteCheck().evaluate(s).passed is True
    assert (
        BandInventoryCompleteCheck().evaluate(replace(s, inventory_complete=False)).passed is False
    )
    assert BandInventoryCompleteCheck().evaluate(replace(s, unit_count=3)).passed is False


def test_all_units_certified_check():
    s = _subject()
    assert BandAllUnitsCertifiedCheck().evaluate(s).passed is True
    assert (
        BandAllUnitsCertifiedCheck().evaluate(replace(s, all_units_certified=False)).passed is False
    )


def test_meta_class_coverage_check():
    s = _subject()
    assert BandMetaClassCoverageCheck().evaluate(s).passed is True
    assert (
        BandMetaClassCoverageCheck().evaluate(replace(s, meta_class_coverage_complete=False)).passed
        is False
    )
    assert (
        BandMetaClassCoverageCheck()
        .evaluate(replace(s, meta_class_ownership_disjoint=False))
        .passed
        is False
    )


def test_relationship_and_integration_and_metamodel_checks():
    s = _subject()
    assert BandRelationshipClosureCheck().evaluate(s).passed is True
    assert BandMetaModelIntegrationCheck().evaluate(s).passed is True
    assert BandIntegrationClosedCheck().evaluate(s).passed is True
    broken = replace(s, integration_closed=False)
    assert BandRelationshipClosureCheck().evaluate(broken).passed is False
    assert BandMetaModelIntegrationCheck().evaluate(broken).passed is False
    assert BandIntegrationClosedCheck().evaluate(broken).passed is False


def test_founding_acyclic_check():
    s = _subject()
    assert BandFoundingAcyclicCheck().evaluate(s).passed is True
    assert BandFoundingAcyclicCheck().evaluate(replace(s, dependency_acyclic=False)).passed is False


def test_reuse_integrity_check():
    s = _subject()
    assert BandReuseIntegrityCheck().evaluate(s).passed is True
    assert BandReuseIntegrityCheck().evaluate(replace(s, substrate_refs=())).passed is False
    assert BandReuseIntegrityCheck().evaluate(replace(s, all_units_certified=False)).passed is False
    assert BandReuseIntegrityCheck().evaluate(replace(s, reuses_by_reference=False)).passed is False


def test_versioned_and_state_checks():
    s = _subject()
    assert BandVersionedCheck().evaluate(s).passed is True
    assert BandVersionedCheck().evaluate(replace(s, version="  ")).passed is False
    assert BandValidStateCheck().evaluate(s).passed is True
    assert BandValidStateCheck().evaluate(replace(s, band_state="BOGUS")).passed is False


def test_independence_and_nonprojection_and_nonconstitutive_checks():
    s = _subject()
    assert BandIndependenceCheck().evaluate(s).passed is True
    assert BandIndependenceCheck().evaluate(replace(s, names_technology=True)).passed is False
    assert BandIndependenceCheck().evaluate(replace(s, selects_technology=True)).passed is False
    assert BandNonProjectionCheck().evaluate(s).passed is True
    assert BandNonProjectionCheck().evaluate(replace(s, non_projection=False)).passed is False
    assert BandNonConstitutiveCheck().evaluate(s).passed is True
    assert BandNonConstitutiveCheck().evaluate(replace(s, confers_authority=True)).passed is False
    assert BandNonConstitutiveCheck().evaluate(replace(s, embeds_secret=True)).passed is False
    assert BandNonConstitutiveCheck().evaluate(replace(s, selects_technology=True)).passed is False
    assert BandNonConstitutiveCheck().evaluate(replace(s, non_constitutive=False)).passed is False


def test_provisional_disclosure_check():
    s = _subject()
    assert BandProvisionalDisclosureCheck().evaluate(s).passed is True
    assert BandProvisionalDisclosureCheck().evaluate(replace(s, disclosure={})).passed is False


def test_traceability_rooted_check():
    s = _subject()
    assert BandTraceabilityRootedCheck().evaluate(s).passed is True
    assert BandTraceabilityRootedCheck().evaluate(replace(s, provenance_chain=())).passed is False
    assert (
        BandTraceabilityRootedCheck()
        .evaluate(replace(s, provenance_chain=("WRONG", "13-INFRASTRUCTURE@b7e7657")))
        .passed
        is False
    )
    assert (
        BandTraceabilityRootedCheck()
        .evaluate(replace(s, provenance_chain=("BAND-13", "no-anchor")))
        .passed
        is False
    )


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), band13_checks())
