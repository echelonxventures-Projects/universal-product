"""EC3-B11-U13 — Band-11 freeze validation tests (each check pass + fail; acceptance)."""

from __future__ import annotations

from dataclasses import replace

from engine.runtime.disclosure import build_disclosure
from service.band11_freeze import make_band11_freeze
from service.band11_freeze_meta import (
    EXPECTED_FROZEN_UNITS,
    FREEZE_SUBSTRATE_REFS,
    TRACE_BACKWARD_FREEZE,
)
from service.band11_freeze_traceability import build_band11_freeze_traceability
from service.band11_freeze_validation import (
    Band11FreezeValidation,
    FreezeBandCompletionReferencedCheck,
    FreezeEffectsDeclaredCheck,
    FreezeFoundingAcyclicCheck,
    FreezeIdentifiedCheck,
    FreezeImmutableBaselineCheck,
    FreezeIndependenceCheck,
    FreezeInventoryCompleteCheck,
    FreezeMetaClassCoverageCheck,
    FreezeNonConstitutiveCheck,
    FreezeNonProjectionCheck,
    FreezeProvisionalDisclosureCheck,
    FreezeRelationshipClosureCheck,
    FreezeReuseIntegrityCheck,
    FreezeTraceabilityRootedCheck,
    FreezeTypedCheck,
    FreezeAllUnitsCertifiedCheck,
    FreezeAllUnitsFrozenCheck,
    FreezeBaselineFidelityCheck,
    FreezeValidationSubject,
    FreezeValidStateCheck,
    FreezeVersionedCheck,
    band11_freeze_checks,
    validate_band11_freeze,
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
_BAND_CERT = "UCOS-CERT-BAND-11-" + "a" * 16


def _freeze():
    return make_band11_freeze(
        "ucos.service.band11.freeze",
        "ucos.core.band-freeze",
        tuple((u, f"UCOS-CERT-{u}-{'a' * 16}", True) for u in EXPECTED_FROZEN_UNITS),
        band_completion_id="UCOS-BAND11-ucos.service.band11.completion-" + "b" * 16,
        band_completion_certification_id=_BAND_CERT,
        meta_model_id="UCOS-METAMODEL-ucos.service.metamodel.universal-" + "c" * 16,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )


def _trace(freeze):
    return build_band11_freeze_traceability(freeze, unit="EC3-B11-U13", forward=("a", "b"))


def _subject(**overrides) -> FreezeValidationSubject:
    base = FreezeValidationSubject(
        target_id="UCOS-FREEZE-BAND11-ucos.service.band11.freeze-" + "d" * 16,
        blueprint_id="BAND-11-FREEZE",
        meta_class="BAND-11-FREEZE",
        name="ucos.service.band11.freeze",
        type_tag="ucos.core.band-freeze",
        value_digest="e" * 64,
        unit_count=len(EXPECTED_FROZEN_UNITS),
        inventory_complete=True,
        all_units_certified=True,
        all_units_frozen=True,
        meta_class_coverage_complete=True,
        band_completion_referenced=True,
        dependency_acyclic=True,
        integration_closed=True,
        reuses_by_reference=True,
        effects_declared=True,
        immutable_baseline=True,
        non_projection=True,
        confers_authority=False,
        embeds_secret=False,
        names_technology=False,
        selects_technology=False,
        non_constitutive=True,
        version="1.0.0",
        freeze_state="DEFINED",
        substrate_refs=FREEZE_SUBSTRATE_REFS,
        provenance_chain=TRACE_BACKWARD_FREEZE,
        disclosure=build_disclosure(),
    )
    return replace(base, **overrides) if overrides else base


def _ok(check, subject):
    return check.evaluate(subject).passed


# ---------------------------------------------------------------------------
# Subject projection
# ---------------------------------------------------------------------------


def test_subject_from_freeze():
    f = _freeze()
    subj = FreezeValidationSubject.from_freeze(f, _trace(f))
    assert subj.target_id == f.freeze_id
    assert subj.unit_count == len(EXPECTED_FROZEN_UNITS)
    assert subj.inventory_complete is True
    assert subj.all_units_frozen is True
    assert subj.provenance_chain == TRACE_BACKWARD_FREEZE


# ---------------------------------------------------------------------------
# Per-check pass + fail branches
# ---------------------------------------------------------------------------


def test_typed_check():
    assert _ok(FreezeTypedCheck(), _subject()) is True
    assert _ok(FreezeTypedCheck(), _subject(type_tag="  ")) is False


def test_identified_check():
    assert _ok(FreezeIdentifiedCheck(), _subject()) is True
    assert _ok(FreezeIdentifiedCheck(), _subject(target_id="nope")) is False


def test_baseline_fidelity_check():
    assert _ok(FreezeBaselineFidelityCheck(), _subject()) is True
    assert _ok(FreezeBaselineFidelityCheck(), _subject(value_digest="zz")) is False
    assert _ok(FreezeBaselineFidelityCheck(), _subject(value_digest="g" * 64)) is False


def test_inventory_complete_check():
    assert _ok(FreezeInventoryCompleteCheck(), _subject()) is True
    assert _ok(FreezeInventoryCompleteCheck(), _subject(inventory_complete=False)) is False
    assert _ok(FreezeInventoryCompleteCheck(), _subject(unit_count=3)) is False


def test_all_units_certified_check():
    assert _ok(FreezeAllUnitsCertifiedCheck(), _subject()) is True
    assert _ok(FreezeAllUnitsCertifiedCheck(), _subject(all_units_certified=False)) is False


def test_all_units_frozen_check():
    assert _ok(FreezeAllUnitsFrozenCheck(), _subject()) is True
    assert _ok(FreezeAllUnitsFrozenCheck(), _subject(all_units_frozen=False)) is False


def test_meta_class_coverage_check():
    assert _ok(FreezeMetaClassCoverageCheck(), _subject()) is True
    assert _ok(FreezeMetaClassCoverageCheck(), _subject(meta_class_coverage_complete=False)) is False


def test_relationship_closure_check():
    assert _ok(FreezeRelationshipClosureCheck(), _subject()) is True
    assert _ok(FreezeRelationshipClosureCheck(), _subject(integration_closed=False)) is False


def test_band_completion_referenced_check():
    assert _ok(FreezeBandCompletionReferencedCheck(), _subject()) is True
    assert _ok(FreezeBandCompletionReferencedCheck(), _subject(band_completion_referenced=False)) is False


def test_founding_acyclic_check():
    assert _ok(FreezeFoundingAcyclicCheck(), _subject()) is True
    assert _ok(FreezeFoundingAcyclicCheck(), _subject(dependency_acyclic=False)) is False


def test_reuse_integrity_check_all_branches():
    assert _ok(FreezeReuseIntegrityCheck(), _subject()) is True
    assert _ok(FreezeReuseIntegrityCheck(), _subject(substrate_refs=())) is False
    assert _ok(FreezeReuseIntegrityCheck(), _subject(all_units_certified=False)) is False
    assert _ok(FreezeReuseIntegrityCheck(), _subject(reuses_by_reference=False)) is False


def test_effects_declared_check():
    assert _ok(FreezeEffectsDeclaredCheck(), _subject()) is True
    assert _ok(FreezeEffectsDeclaredCheck(), _subject(effects_declared=False)) is False


def test_immutable_baseline_check():
    assert _ok(FreezeImmutableBaselineCheck(), _subject()) is True
    assert _ok(FreezeImmutableBaselineCheck(), _subject(immutable_baseline=False)) is False


def test_versioned_check():
    assert _ok(FreezeVersionedCheck(), _subject()) is True
    assert _ok(FreezeVersionedCheck(), _subject(version="  ")) is False


def test_valid_state_check():
    assert _ok(FreezeValidStateCheck(), _subject()) is True
    assert _ok(FreezeValidStateCheck(), _subject(freeze_state="BOGUS")) is False


def test_independence_check():
    assert _ok(FreezeIndependenceCheck(), _subject()) is True
    assert _ok(FreezeIndependenceCheck(), _subject(names_technology=True)) is False
    assert _ok(FreezeIndependenceCheck(), _subject(selects_technology=True)) is False


def test_non_projection_check():
    assert _ok(FreezeNonProjectionCheck(), _subject()) is True
    assert _ok(FreezeNonProjectionCheck(), _subject(non_projection=False)) is False


def test_non_constitutive_check_all_branches():
    assert _ok(FreezeNonConstitutiveCheck(), _subject()) is True
    assert _ok(FreezeNonConstitutiveCheck(), _subject(confers_authority=True)) is False
    assert _ok(FreezeNonConstitutiveCheck(), _subject(embeds_secret=True)) is False
    assert _ok(FreezeNonConstitutiveCheck(), _subject(selects_technology=True)) is False
    assert _ok(FreezeNonConstitutiveCheck(), _subject(non_constitutive=False)) is False


def test_provisional_disclosure_check():
    assert _ok(FreezeProvisionalDisclosureCheck(), _subject()) is True
    assert _ok(FreezeProvisionalDisclosureCheck(), _subject(disclosure={})) is False


def test_traceability_rooted_check_all_branches():
    assert _ok(FreezeTraceabilityRootedCheck(), _subject()) is True
    assert _ok(FreezeTraceabilityRootedCheck(), _subject(provenance_chain=())) is False
    assert _ok(FreezeTraceabilityRootedCheck(), _subject(provenance_chain=("WRONG",))) is False
    assert _ok(
        FreezeTraceabilityRootedCheck(),
        _subject(provenance_chain=("BAND-11-FREEZE", "no-anchor")),
    ) is False


# ---------------------------------------------------------------------------
# End-to-end validation + acceptance
# ---------------------------------------------------------------------------


def test_suite_has_twenty_checks_with_unique_ids():
    checks = band11_freeze_checks()
    assert len(checks) == 20
    assert len({c.check_id for c in checks}) == 20


def test_validate_band11_freeze_accepted():
    f = _freeze()
    validation = validate_band11_freeze(f, _trace(f))
    assert isinstance(validation, Band11FreezeValidation)
    assert validation.accepted is True
    passed = {finding.check_id: finding.passed for finding in validation.report.findings}
    assert all(passed.values())
