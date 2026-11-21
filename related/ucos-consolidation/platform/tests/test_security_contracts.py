"""EC2-CAP-SEC-001 / SEC-CLASS — contract tests.

Covers the classification vocabulary (kinds, subject layers, layer→kind membership),
the :class:`EnforcementReference` (content-addressed reference to the L7 seam, enacts
nothing), and the published SEC-CLASS contract surface (versioned refs).
"""

from __future__ import annotations

from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.security.contracts import (
    L7_BOUND_KINDS,
    SECURITY_CLASSIFICATION_CONTRACT_VERSION,
    SECURITY_CLASSIFICATION_CONTRACTS,
    SUBJECT_LAYER_KINDS,
    SUBJECT_LAYER_SOURCE,
    ClassificationKind,
    EnforcementReference,
    SubjectLayer,
    all_classification_kinds,
    all_subject_layers,
    default_security_classification_contracts,
    security_classification_contract,
)
from platform.security.errors import EnforcementReferenceError, SecurityContractError

import pytest


def test_classification_kinds_are_the_six_subject_layer_records():
    assert all_classification_kinds() == tuple(ClassificationKind)
    assert {k.value for k in ClassificationKind} == {
        "authentication-record",
        "authorization-record",
        "confidentiality-record",
        "integrity-record",
        "isolation-facet",
        "classification-label",
    }


def test_subject_layers_are_the_four_architectures():
    assert all_subject_layers() == tuple(SubjectLayer)
    assert {layer.value for layer in SubjectLayer} == {
        "DATA-014",
        "SERVICE-014",
        "APPLICATION-013",
        "INFRASTRUCTURE-013",
    }


def test_l7_bound_kinds_are_exactly_authentication_and_authorization():
    assert L7_BOUND_KINDS == frozenset(
        {ClassificationKind.AUTHENTICATION, ClassificationKind.AUTHORIZATION}
    )


def test_every_subject_layer_has_a_source_reference():
    for layer in SubjectLayer:
        assert layer in SUBJECT_LAYER_SOURCE
        assert SUBJECT_LAYER_SOURCE[layer]


def test_every_subject_layer_declares_originatable_kinds():
    for layer in SubjectLayer:
        assert layer in SUBJECT_LAYER_KINDS
        assert SUBJECT_LAYER_KINDS[layer]
        assert SUBJECT_LAYER_KINDS[layer].issubset(set(ClassificationKind))


def test_data_layer_does_not_originate_authentication():
    # DATA-014 is classification/confidentiality/integrity only (no authn/authz record).
    assert ClassificationKind.AUTHENTICATION not in SUBJECT_LAYER_KINDS[SubjectLayer.DATA]
    assert ClassificationKind.AUTHORIZATION not in SUBJECT_LAYER_KINDS[SubjectLayer.DATA]


def test_data_layer_owns_the_classification_label():
    assert ClassificationKind.CLASSIFICATION_LABEL in SUBJECT_LAYER_KINDS[SubjectLayer.DATA]


def test_infrastructure_layer_owns_isolation():
    assert ClassificationKind.ISOLATION in SUBJECT_LAYER_KINDS[SubjectLayer.INFRASTRUCTURE]


def test_enforcement_reference_is_content_addressed_and_deterministic():
    a = EnforcementReference.create(CapabilityGroup.GENERATION_REQUESTS, Permission.EXECUTE)
    b = EnforcementReference.create(CapabilityGroup.GENERATION_REQUESTS, Permission.EXECUTE)
    assert a.reference_id == b.reference_id
    assert a.reference_id.startswith("UCOS-SREF-")


def test_enforcement_reference_records_the_seam_and_enacts_nothing():
    ref = EnforcementReference.create(CapabilityGroup.ADMINISTRATION_POLICY, Permission.ADMINISTER)
    d = ref.to_dict()
    assert d["seam"] == "platform.identity.AuthorizationService"
    assert d["enacts"] is False
    assert d["group"] == "administration-policy"
    assert d["permission"] == "administer"


def test_enforcement_reference_rejects_bad_group():
    with pytest.raises(EnforcementReferenceError):
        EnforcementReference.create("generation-requests", Permission.READ)  # type: ignore[arg-type]


def test_enforcement_reference_rejects_bad_permission():
    with pytest.raises(EnforcementReferenceError):
        EnforcementReference.create(CapabilityGroup.API_ACCESS, "execute")  # type: ignore[arg-type]


def test_published_contracts_are_versioned_refs():
    assert len(SECURITY_CLASSIFICATION_CONTRACTS) == 3
    for ref in SECURITY_CLASSIFICATION_CONTRACTS:
        assert ref.version == SECURITY_CLASSIFICATION_CONTRACT_VERSION
        assert ref.name.startswith("security.classification.")


def test_default_contracts_materialize_every_ref():
    contracts = default_security_classification_contracts()
    assert {c.name for c in contracts} == {r.name for r in SECURITY_CLASSIFICATION_CONTRACTS}


def test_security_classification_contract_requires_a_name():
    with pytest.raises(SecurityContractError):
        security_classification_contract("")


def test_security_classification_contract_builds_a_versioned_contract():
    contract = security_classification_contract("security.classification.record", "desc")
    assert contract.name == "security.classification.record"
    assert str(contract.version) == SECURITY_CLASSIFICATION_CONTRACT_VERSION
