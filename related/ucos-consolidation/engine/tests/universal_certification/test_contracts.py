"""UCOS-EPIC-006 — Universal Certification contract tests."""

from __future__ import annotations

import pytest

from engine.universal_certification import (
    Certificate,
    CertificationClass,
    CertificationStatus,
    Measurement,
    MeasurementComparator,
    MeasurementInput,
    RepositoryTruthInput,
    RuleSeverity,
    UniversalCertificationSubject,
    ValidationInput,
    canonical_json,
    content_hash,
)
from engine.universal_certification.contracts import RuleFinding, RuleStatus
from engine.universal_certification.errors import (
    CertificateIntegrityError,
    CertificationInputError,
    CertificationSubjectError,
)

from .conftest import mutate


def test_content_hash_is_deterministic_and_order_independent():
    a = content_hash({"b": 1, "a": 2})
    b = content_hash({"a": 2, "b": 1})
    assert a == b
    assert canonical_json({"a": 2, "b": 1}) == '{"a":2,"b":1}'


# --------------------------------------------------------------------------- #
# Measurement.                                                                #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("comparator", "value", "threshold", "expected"),
    [
        (MeasurementComparator.GE, 90.0, 90.0, True),
        (MeasurementComparator.GE, 89.9, 90.0, False),
        (MeasurementComparator.LE, 0, 0, True),
        (MeasurementComparator.LE, 1, 0, False),
        (MeasurementComparator.GT, 91, 90, True),
        (MeasurementComparator.GT, 90, 90, False),
        (MeasurementComparator.LT, 89, 90, True),
        (MeasurementComparator.LT, 90, 90, False),
        (MeasurementComparator.EQ, 5, 5, True),
        (MeasurementComparator.EQ, 5, 6, False),
    ],
)
def test_measurement_evaluate_computes_satisfaction(comparator, value, threshold, expected):
    m = Measurement.evaluate(metric_id="m", value=value, threshold=threshold, comparator=comparator)
    assert m.satisfied is expected


def test_measurement_blocking_shortfall_flag():
    m = Measurement.evaluate(
        metric_id="m", value=1, threshold=0, comparator=MeasurementComparator.LE
    )
    assert m.is_blocking_shortfall is True
    a = Measurement.evaluate(
        metric_id="m",
        value=1,
        threshold=0,
        comparator=MeasurementComparator.LE,
        severity=RuleSeverity.ADVISORY,
    )
    assert a.is_blocking_shortfall is False


def test_measurement_evaluate_rejects_bad_input():
    with pytest.raises(CertificationInputError):
        Measurement.evaluate(metric_id="", value=1, threshold=0)
    with pytest.raises(CertificationInputError):
        Measurement.evaluate(metric_id="m", value="x", threshold=0)  # type: ignore[arg-type]
    with pytest.raises(CertificationInputError):
        Measurement.evaluate(
            metric_id="m",
            value=1,
            threshold=0,
            comparator="ge",  # type: ignore[arg-type]
        )
    with pytest.raises(CertificationInputError):
        Measurement.evaluate(
            metric_id="m",
            value=1,
            threshold=0,
            severity="blocking",  # type: ignore[arg-type]
        )


# --------------------------------------------------------------------------- #
# MeasurementInput.                                                           #
# --------------------------------------------------------------------------- #


def test_measurement_input_orders_by_metric_id_and_counts():
    mi = MeasurementInput.create(
        (
            Measurement.evaluate(
                metric_id="z", value=1, threshold=0, comparator=MeasurementComparator.GE
            ),
            Measurement.evaluate(
                metric_id="a", value=1, threshold=0, comparator=MeasurementComparator.GE
            ),
        )
    )
    assert [m.metric_id for m in mi.measurements] == ["a", "z"]
    assert mi.present is True
    assert mi.all_blocking_satisfied is True
    assert mi.counts()["total"] == 2


def test_measurement_input_shortfalls():
    mi = MeasurementInput.create(
        (
            Measurement.evaluate(
                metric_id="b", value=1, threshold=0, comparator=MeasurementComparator.LE
            ),
            Measurement.evaluate(
                metric_id="a",
                value=1,
                threshold=0,
                comparator=MeasurementComparator.LE,
                severity=RuleSeverity.ADVISORY,
            ),
        )
    )
    assert mi.blocking_shortfalls == ("b",)
    assert mi.advisory_shortfalls == ("a",)
    assert mi.all_blocking_satisfied is False


def test_measurement_input_rejects_non_measurement():
    with pytest.raises(CertificationInputError):
        MeasurementInput.create((object(),))  # type: ignore[arg-type]


def test_measurement_input_digest_is_stable(measurement_input):
    assert measurement_input.digest() == measurement_input.digest()


# --------------------------------------------------------------------------- #
# RepositoryTruthInput.                                                       #
# --------------------------------------------------------------------------- #


def test_repository_truth_consistent(repository_truth_input):
    rt = repository_truth_input
    assert rt.consistent is True
    assert rt.gap_total == 0
    assert rt.fully_homed is True
    assert rt.open_gap_categories == ()


def test_repository_truth_inconsistent_variants():
    base = dict(
        snapshot_id="s", content_sha256="h", total_concepts=10, homed_concepts=10, closed=True
    )
    assert RepositoryTruthInput.create(**base, gaps={"x": 1}).consistent is False
    assert RepositoryTruthInput.create(**{**base, "closed": False}, gaps={}).consistent is False
    assert RepositoryTruthInput.create(**{**base, "homed_concepts": 9}, gaps={}).consistent is False
    empty = RepositoryTruthInput.create(
        snapshot_id="s", content_sha256="h", total_concepts=0, homed_concepts=0, closed=True
    )
    assert empty.fully_homed is False and empty.consistent is False


def test_repository_truth_open_gap_categories():
    rt = RepositoryTruthInput.create(
        snapshot_id="s",
        content_sha256="h",
        total_concepts=10,
        homed_concepts=10,
        gaps={"a": 2, "b": 0, "c": 3},
        closed=True,
    )
    assert rt.open_gap_categories == ("a", "c")
    assert rt.gap_total == 5


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(snapshot_id="", content_sha256="h", total_concepts=1, homed_concepts=1, closed=True),
        dict(snapshot_id="s", content_sha256="", total_concepts=1, homed_concepts=1, closed=True),
        dict(snapshot_id="s", content_sha256="h", total_concepts=-1, homed_concepts=0, closed=True),
        dict(snapshot_id="s", content_sha256="h", total_concepts=1, homed_concepts=-1, closed=True),
        dict(snapshot_id="s", content_sha256="h", total_concepts=1, homed_concepts=2, closed=True),
    ],
)
def test_repository_truth_create_rejects_bad_input(kwargs):
    with pytest.raises(CertificationInputError):
        RepositoryTruthInput.create(**kwargs)


def test_repository_truth_rejects_bad_gap_entries():
    base = dict(
        snapshot_id="s", content_sha256="h", total_concepts=1, homed_concepts=1, closed=True
    )
    with pytest.raises(CertificationInputError):
        RepositoryTruthInput.create(**base, gaps={"": 0})
    with pytest.raises(CertificationInputError):
        RepositoryTruthInput.create(**base, gaps={"a": -1})


# --------------------------------------------------------------------------- #
# ValidationInput.                                                            #
# --------------------------------------------------------------------------- #


def test_validation_input_from_real_validation(validation_input):
    assert validation_input.accepted is True
    assert validation_input.verdict == "pass"
    assert validation_input.evidence_present is True
    assert validation_input.evidence_sha256
    assert validation_input.disclosure_validated is True


def test_validation_input_missing_evidence(valid_report):
    vi = ValidationInput.from_validation(valid_report, None)
    assert vi.evidence_present is False
    assert vi.evidence_sha256 == ""


def test_validation_input_target_mismatch(valid_report, valid_evidence):
    bad = mutate(valid_evidence, target_id="OTHER")
    with pytest.raises(CertificationInputError):
        ValidationInput.from_validation(valid_report, bad)


def test_validation_input_requires_target(valid_report):
    bad = mutate(valid_report, target_id="")
    with pytest.raises(CertificationInputError):
        ValidationInput.from_validation(bad, None)


# --------------------------------------------------------------------------- #
# Subject.                                                                    #
# --------------------------------------------------------------------------- #


def test_subject_projection_and_digests(subject):
    digests = subject.digests()
    assert set(digests) == {"validation", "measurement", "repository_truth"}
    assert subject.fingerprint() == subject.fingerprint()
    assert subject.certification_class is CertificationClass.UNIVERSAL_READINESS


def test_subject_create_rejects_bad_inputs(
    validation_input, measurement_input, repository_truth_input
):
    with pytest.raises(CertificationSubjectError):
        UniversalCertificationSubject.create(
            validation=object(),  # type: ignore[arg-type]
            measurement=measurement_input,
            repository_truth=repository_truth_input,
            version="1.0.0",
        )
    with pytest.raises(CertificationSubjectError):
        UniversalCertificationSubject.create(
            validation=validation_input,
            measurement=object(),  # type: ignore[arg-type]
            repository_truth=repository_truth_input,
            version="1.0.0",
        )
    with pytest.raises(CertificationSubjectError):
        UniversalCertificationSubject.create(
            validation=validation_input,
            measurement=measurement_input,
            repository_truth=object(),  # type: ignore[arg-type]
            version="1.0.0",
        )
    with pytest.raises(CertificationSubjectError):
        UniversalCertificationSubject.create(
            validation=validation_input,
            measurement=measurement_input,
            repository_truth=repository_truth_input,
            version="1.0.0",
            certification_class="x",  # type: ignore[arg-type]
        )


def test_subject_requires_ids(measurement_input, repository_truth_input, valid_report):
    vi = ValidationInput.from_validation(valid_report, None)
    vi_no_target = mutate(vi, target_id="")
    with pytest.raises(CertificationSubjectError):
        UniversalCertificationSubject.create(
            validation=vi_no_target,
            measurement=measurement_input,
            repository_truth=repository_truth_input,
            version="1.0.0",
        )
    vi_no_bp = mutate(vi, blueprint_id="")
    with pytest.raises(CertificationSubjectError):
        UniversalCertificationSubject.create(
            validation=vi_no_bp,
            measurement=measurement_input,
            repository_truth=repository_truth_input,
            version="1.0.0",
        )


# --------------------------------------------------------------------------- #
# Certificate.                                                                #
# --------------------------------------------------------------------------- #


def _certificate() -> Certificate:
    finding = RuleFinding("r", RuleSeverity.BLOCKING, RuleStatus.PASS, "ok")
    return Certificate.create(
        target_id="T",
        blueprint_id="BP-DATA-0001",
        version="1.0.0",
        status=CertificationStatus.CERTIFIED,
        certification_class=CertificationClass.UNIVERSAL_READINESS,
        validation_evidence_ref="v",
        measurement_digest="m",
        repository_truth_digest="rt",
        compliance_digest="c",
        rules=(finding,),
        disclosure={"disclosure_id": "EC-1-PROVISIONAL-STATE"},
    )


def test_certificate_is_content_addressed_and_verifies():
    cert = _certificate()
    assert cert.certified is True
    assert cert.certification_id == f"UCOS-UCERT-BP-DATA-0001-{cert.content_sha256[:16]}"
    assert cert.verify_integrity() is True
    cert.require_integrity()


def test_certificate_detects_mutation():
    cert = _certificate()
    tampered = mutate(cert, version="9.9.9")
    assert tampered.verify_integrity() is False
    with pytest.raises(CertificateIntegrityError):
        tampered.require_integrity()


def test_certificate_id_is_reproducible():
    assert _certificate().certification_id == _certificate().certification_id
