"""EC3-B10-U11 — Meta-model validation tests (DMI-01…07 checks + acceptance + negatives)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from data.model_meta import META_CLASSES, META_RELATIONSHIPS, ONTOLOGY_ENTITIES
from data.model_traceability import build_model_traceability
from data.model_validation import (
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    MetaClassClosureCheck,
    MetaConstraintsCheck,
    MetaModelTotalityCheck,
    MetaRelationshipClosureCheck,
    ModelIdentifiedCheck,
    ModelIndependenceCheck,
    ModelMapResolvesCheck,
    ModelMembersCertifiedCheck,
    ModelNamedCheck,
    ModelTypedCheck,
    ModelValidationSubject,
    ModelValidStateCheck,
    ModelValueFidelityCheck,
    ModelVersionedCheck,
    NonConstitutiveCheck,
    NonProjectionCheck,
    ProvisionalDisclosureCheck,
    TraceabilityRootedCheck,
    model_checks,
    validate_model,
)
from data.tests.test_model import a_model
from engine.tests import assert_every_check_can_refuse


def _trace(model):
    return build_model_traceability(model, unit="EC3-B10-U11", forward=("f",))


def _subject():
    model = a_model()
    return ModelValidationSubject.from_model(model, _trace(model))


# ---------------------------------------------------------------------------
# Happy path — the full suite accepts a well-formed meta-model
# ---------------------------------------------------------------------------


def test_valid_metamodel_passes_full_suite():
    model = a_model()
    result = validate_model(model, _trace(model))
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    passed = {f.check_id for f in result.report.findings if f.passed}
    # every CCE-shared id the DMC-01 gate suite requires is present and passing
    for shared in (
        "traceability-rooted",
        "meta-class-single",
        "data-value-fidelity",
        "founding-acyclic",
        "meta-relationships-closed",
        "foundation-reuse-integrity",
        "provisional-state-disclosure",
    ):
        assert shared in passed


def test_suite_has_nineteen_blocking_checks():
    checks = model_checks()
    assert len(checks) == 19
    assert all(c.severity.name == "BLOCKING" for c in checks)


def test_strict_validation_of_valid_model_does_not_raise():
    model = a_model()
    assert validate_model(model, _trace(model), strict=True).accepted is True


# ---------------------------------------------------------------------------
# Individual check pass + fail branches
# ---------------------------------------------------------------------------


def test_typed_check():
    assert ModelTypedCheck().evaluate(_subject()).passed is True
    assert ModelTypedCheck().evaluate(replace(_subject(), type_tag="  ")).passed is False


def test_named_check():
    assert ModelNamedCheck().evaluate(_subject()).passed is True
    assert ModelNamedCheck().evaluate(replace(_subject(), name=" ")).passed is False


def test_identified_check():
    assert ModelIdentifiedCheck().evaluate(_subject()).passed is True
    assert ModelIdentifiedCheck().evaluate(replace(_subject(), target_id="X")).passed is False


def test_value_fidelity_check():
    assert ModelValueFidelityCheck().evaluate(_subject()).passed is True
    assert ModelValueFidelityCheck().evaluate(replace(_subject(), value_digest="z")).passed is False


def test_meta_class_closure_check():
    assert MetaClassClosureCheck().evaluate(_subject()).passed is True
    assert (
        MetaClassClosureCheck().evaluate(replace(_subject(), meta_classes=("DMC-01",))).passed
        is False
    )
    # correct set but does not declare closure
    assert (
        MetaClassClosureCheck().evaluate(replace(_subject(), declares_closure=False)).passed
        is False
    )


def test_meta_relationship_closure_check():
    assert MetaRelationshipClosureCheck().evaluate(_subject()).passed is True
    # outside DMR-01…12
    assert (
        MetaRelationshipClosureCheck()
        .evaluate(replace(_subject(), meta_relationships=(*META_RELATIONSHIPS, "DMR-99")))
        .passed
        is False
    )
    # not exact (missing one, no outsider)
    assert (
        MetaRelationshipClosureCheck()
        .evaluate(replace(_subject(), meta_relationships=tuple(META_RELATIONSHIPS[:-1])))
        .passed
        is False
    )
    # correct set but does not declare closure
    assert (
        MetaRelationshipClosureCheck()
        .evaluate(replace(_subject(), declares_relationship_closure=False))
        .passed
        is False
    )


def test_totality_check():
    assert MetaModelTotalityCheck().evaluate(_subject()).passed is True
    assert (
        MetaModelTotalityCheck().evaluate(replace(_subject(), modelled_entities=("DOE-01",))).passed
        is False
    )
    assert (
        MetaModelTotalityCheck()
        .evaluate(replace(_subject(), modelled_relationships=("DOR-01",)))
        .passed
        is False
    )
    # entities + relationships total, but is_total flag false
    assert MetaModelTotalityCheck().evaluate(replace(_subject(), is_total=False)).passed is False


def test_founding_acyclic_check():
    assert FoundingAcyclicCheck().evaluate(_subject()).passed is True
    assert (
        FoundingAcyclicCheck().evaluate(replace(_subject(), founding_acyclic=False)).passed is False
    )


def test_members_certified_check():
    assert ModelMembersCertifiedCheck().evaluate(_subject()).passed is True
    assert (
        ModelMembersCertifiedCheck().evaluate(replace(_subject(), members_certified=False)).passed
        is False
    )


def test_map_resolves_check():
    assert ModelMapResolvesCheck().evaluate(_subject()).passed is True
    assert ModelMapResolvesCheck().evaluate(replace(_subject(), map_resolves=False)).passed is False


def test_meta_constraints_check():
    assert MetaConstraintsCheck().evaluate(_subject()).passed is True
    assert (
        MetaConstraintsCheck().evaluate(replace(_subject(), confers_authority=True)).passed is False
    )


def test_valid_state_check():
    assert ModelValidStateCheck().evaluate(_subject()).passed is True
    assert ModelValidStateCheck().evaluate(replace(_subject(), model_state="BOGUS")).passed is False


def test_versioned_check():
    assert ModelVersionedCheck().evaluate(_subject()).passed is True
    assert ModelVersionedCheck().evaluate(replace(_subject(), version=" ")).passed is False


def test_reuse_integrity_check():
    assert FoundationReuseIntegrityCheck().evaluate(_subject()).passed is True
    assert (
        FoundationReuseIntegrityCheck().evaluate(replace(_subject(), redefines_el1=True)).passed
        is False
    )
    assert (
        FoundationReuseIntegrityCheck().evaluate(replace(_subject(), substrate_refs=())).passed
        is False
    )
    assert (
        FoundationReuseIntegrityCheck()
        .evaluate(replace(_subject(), members_certified=False))
        .passed
        is False
    )
    assert (
        FoundationReuseIntegrityCheck()
        .evaluate(replace(_subject(), reuses_by_reference=False))
        .passed
        is False
    )


def test_independence_check():
    assert ModelIndependenceCheck().evaluate(_subject()).passed is True
    assert (
        ModelIndependenceCheck().evaluate(replace(_subject(), names_technology=True)).passed
        is False
    )


def test_non_projection_check():
    assert NonProjectionCheck().evaluate(_subject()).passed is True
    assert NonProjectionCheck().evaluate(replace(_subject(), non_projection=False)).passed is False


def test_non_constitutive_check():
    assert NonConstitutiveCheck().evaluate(_subject()).passed is True
    assert (
        NonConstitutiveCheck().evaluate(replace(_subject(), confers_authority=True)).passed is False
    )
    assert NonConstitutiveCheck().evaluate(replace(_subject(), embeds_secret=True)).passed is False
    assert (
        NonConstitutiveCheck().evaluate(replace(_subject(), selects_technology=True)).passed
        is False
    )
    # not authority/secret/tech, but the aggregate non_constitutive flag is false
    assert (
        NonConstitutiveCheck().evaluate(replace(_subject(), non_constitutive=False)).passed is False
    )


def test_provisional_disclosure_check():
    assert ProvisionalDisclosureCheck().evaluate(_subject()).passed is True
    assert ProvisionalDisclosureCheck().evaluate(replace(_subject(), disclosure={})).passed is False


def test_traceability_rooted_check():
    assert TraceabilityRootedCheck().evaluate(_subject()).passed is True
    assert (
        TraceabilityRootedCheck().evaluate(replace(_subject(), provenance_chain=())).passed is False
    )
    assert (
        TraceabilityRootedCheck()
        .evaluate(replace(_subject(), provenance_chain=("WRONG", "10-DATA@x")))
        .passed
        is False
    )
    assert (
        TraceabilityRootedCheck()
        .evaluate(replace(_subject(), provenance_chain=(_subject().meta_class, "DATA-005")))
        .passed
        is False
    )


@pytest.mark.parametrize("meta_class", list(META_CLASSES))
def test_subject_carries_all_ten_meta_classes(meta_class):
    assert meta_class in _subject().meta_classes


def test_subject_totality_covers_all_ontology_entities():
    assert set(_subject().modelled_entities) == set(ONTOLOGY_ENTITIES)


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), model_checks())
