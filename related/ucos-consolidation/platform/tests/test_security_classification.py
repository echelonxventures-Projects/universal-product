"""EC2-CAP-SEC-001 / SEC-CLASS — classification model & ledger unit tests.

Covers :class:`SecurityClassification` (evaluative, non-enforcing, content-addressed;
classify / trace / validate) and the append-only, idempotent
:class:`ClassificationLedger` (record / query / fingerprint).
"""

from __future__ import annotations

from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.security.classification import ClassificationLedger, SecurityClassification
from platform.security.contracts import (
    ClassificationKind,
    EnforcementReference,
    SubjectLayer,
)
from platform.security.errors import (
    ClassificationValidationError,
    SecurityClassificationError,
)

import pytest


def _authz_ref() -> EnforcementReference:
    return EnforcementReference.create(CapabilityGroup.GENERATION_REQUESTS, Permission.EXECUTE)


def test_confidentiality_classification_is_content_addressed_and_deterministic():
    a = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000001", "restricted"
    )
    b = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000001", "restricted"
    )
    assert a.classification_id == b.classification_id
    assert a.classification_id.startswith("UCOS-SCLS-")
    assert a.fingerprint() == b.fingerprint()


def test_classification_defaults_constitution_ref_from_layer():
    c = SecurityClassification.create(
        ClassificationKind.INTEGRITY, SubjectLayer.DATA, "UCOS-DATA-000002", "tamper-evident"
    )
    assert "DATA-014" in c.constitution_ref


def test_classification_is_non_enforcing_and_evaluative():
    c = SecurityClassification.create(
        ClassificationKind.CLASSIFICATION_LABEL, SubjectLayer.DATA, "UCOS-DATA-000003", "public"
    )
    assert c.non_enforcing is True
    verdict = c.classify()
    assert verdict["decidable"] is True
    assert verdict["enforced"] is False
    assert verdict["non_enforcing"] is True


def test_l7_bound_kind_requires_enforcement_reference():
    with pytest.raises(SecurityClassificationError):
        SecurityClassification.create(
            ClassificationKind.AUTHORIZATION,
            SubjectLayer.SERVICE,
            "UCOS-SVC-000001",
            "required",
        )


def test_l7_bound_kind_with_reference_is_valid_and_is_l7_bound():
    c = SecurityClassification.create(
        ClassificationKind.AUTHORIZATION,
        SubjectLayer.SERVICE,
        "UCOS-SVC-000001",
        "required",
        enforcement_ref=_authz_ref(),
    )
    assert c.is_l7_bound is True
    assert c.enforcement_ref is not None


def test_non_l7_bound_kind_rejects_enforcement_reference():
    with pytest.raises(SecurityClassificationError):
        SecurityClassification.create(
            ClassificationKind.CONFIDENTIALITY,
            SubjectLayer.DATA,
            "UCOS-DATA-000004",
            "restricted",
            enforcement_ref=_authz_ref(),
        )


def test_layer_must_originate_the_kind():
    # DATA-014 does not originate an authentication record.
    with pytest.raises(SecurityClassificationError):
        SecurityClassification.create(
            ClassificationKind.AUTHENTICATION,
            SubjectLayer.DATA,
            "UCOS-DATA-000005",
            "required",
            enforcement_ref=EnforcementReference.create(
                CapabilityGroup.IDENTITY_SESSIONS_SELF, Permission.READ
            ),
        )


def test_create_rejects_bad_kind():
    with pytest.raises(SecurityClassificationError):
        SecurityClassification.create(
            "authorization-record",
            SubjectLayer.SERVICE,
            "x",
            "y",  # type: ignore[arg-type]
        )


def test_create_rejects_bad_layer():
    with pytest.raises(SecurityClassificationError):
        SecurityClassification.create(
            ClassificationKind.CONFIDENTIALITY,
            "DATA-014",
            "x",
            "y",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("subject_ref", ["", "   "])
def test_create_rejects_empty_subject_ref(subject_ref):
    with pytest.raises(SecurityClassificationError):
        SecurityClassification.create(
            ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, subject_ref, "restricted"
        )


@pytest.mark.parametrize("label", ["", "   "])
def test_create_rejects_empty_label(label):
    with pytest.raises(SecurityClassificationError):
        SecurityClassification.create(
            ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000006", label
        )


def test_create_rejects_blank_constitution_ref_override():
    with pytest.raises(SecurityClassificationError):
        SecurityClassification.create(
            ClassificationKind.CONFIDENTIALITY,
            SubjectLayer.DATA,
            "UCOS-DATA-000007",
            "restricted",
            constitution_ref="   ",
        )


def test_trace_returns_backward_subject_and_forward():
    c = SecurityClassification.create(
        ClassificationKind.AUTHORIZATION,
        SubjectLayer.APPLICATION,
        "UCOS-APP-000001",
        "required",
        enforcement_ref=_authz_ref(),
    )
    trace = c.trace()
    assert trace["backward"]["layer"] == "APPLICATION-013"
    assert "APPLICATION-013" in trace["backward"]["constitution_ref"]
    assert trace["subject"]["subject_ref"] == "UCOS-APP-000001"
    assert trace["forward"]["seam"] == "platform.identity.AuthorizationService"


def test_trace_forward_is_none_for_non_l7_bound():
    c = SecurityClassification.create(
        ClassificationKind.ISOLATION,
        SubjectLayer.INFRASTRUCTURE,
        "UCOS-INF-000001",
        "isolated",
    )
    assert c.trace()["forward"] is None


def test_validate_reports_meta_validity():
    c = SecurityClassification.create(
        ClassificationKind.INTEGRITY, SubjectLayer.SERVICE, "UCOS-SVC-000002", "signed"
    )
    result = c.validate()
    assert result["meta_valid"] is True
    assert all(result["checks"].values())


def test_validate_detects_tampered_non_enforcing_flag():
    c = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000008", "restricted"
    )
    # dataclass is frozen; construct an invalid twin via object.__new__ bypass is unsafe,
    # so simulate by building a subtype-free copy with non_enforcing False through replace.
    import dataclasses

    tampered = dataclasses.replace(c, non_enforcing=False)
    with pytest.raises(ClassificationValidationError):
        tampered.validate()


def test_to_dict_roundtrip_shape():
    c = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000009", "internal"
    )
    d = c.to_dict()
    assert d["kind"] == "confidentiality-record"
    assert d["layer"] == "DATA-014"
    assert d["non_enforcing"] is True
    assert d["enforcement_ref"] is None


# --- ClassificationLedger ---------------------------------------------------


def test_ledger_records_and_is_idempotent_by_id():
    ledger = ClassificationLedger()
    c = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000010", "restricted"
    )
    first = ledger.record(c)
    second = ledger.record(c)
    assert first is second
    assert len(ledger) == 1
    assert c.classification_id in ledger


def test_ledger_rejects_non_classification():
    ledger = ClassificationLedger()
    with pytest.raises(SecurityClassificationError):
        ledger.record("not-a-classification")  # type: ignore[arg-type]


def test_ledger_get_absent_raises():
    ledger = ClassificationLedger()
    with pytest.raises(SecurityClassificationError):
        ledger.get("UCOS-SCLS-does-not-exist")


def test_ledger_queries_by_kind_layer_subject():
    ledger = ClassificationLedger()
    conf = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000011", "restricted"
    )
    integ = SecurityClassification.create(
        ClassificationKind.INTEGRITY, SubjectLayer.DATA, "UCOS-DATA-000011", "signed"
    )
    ledger.record(conf)
    ledger.record(integ)
    assert ledger.by_kind(ClassificationKind.CONFIDENTIALITY) == (conf,)
    assert ledger.by_layer(SubjectLayer.DATA) == (conf, integ)
    assert set(ledger.by_subject("UCOS-DATA-000011")) == {conf, integ}


def test_ledger_snapshot_is_immutable_and_ordered():
    ledger = ClassificationLedger()
    a = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000012", "a"
    )
    b = SecurityClassification.create(
        ClassificationKind.INTEGRITY, SubjectLayer.DATA, "UCOS-DATA-000013", "b"
    )
    ledger.record(a)
    ledger.record(b)
    snap = ledger.classifications
    assert snap == (a, b)
    assert isinstance(snap, tuple)


def test_ledger_fingerprint_is_deterministic():
    def build() -> ClassificationLedger:
        ledger = ClassificationLedger()
        ledger.record(
            SecurityClassification.create(
                ClassificationKind.CONFIDENTIALITY,
                SubjectLayer.DATA,
                "UCOS-DATA-000014",
                "restricted",
            )
        )
        return ledger

    assert build().fingerprint() == build().fingerprint()
