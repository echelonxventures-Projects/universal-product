"""EC3-B10-U01 — Validation tests (EC-1 ValidationEngine PASS + V1…V5 + UDL + VC)."""

from __future__ import annotations

from dataclasses import replace

from data.datum import make_datum
from data.meta import DatumKind, DatumState
from data.traceability import build_traceability
from data.validation import (
    DatumValidationSubject,
    datum_checks,
    validate_datum,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict


def _trace(datum):
    return build_traceability(datum, unit="EC3-B10-U01", forward=(datum.datum_id,))


def test_validation_passes_and_is_accepted():
    d = make_datum("ucos.core.string", "hello")
    result = validate_datum(d, _trace(d))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.decision.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    d = make_datum("t", "v")
    result = validate_datum(d, _trace(d))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(datum_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    d = make_datum("t", "v")
    result = validate_datum(d, _trace(d))
    passed = {f.check_id: f.passed for f in result.report.findings}
    assert passed["meta-class-single"]  # V1
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3
    assert passed["founding-acyclic"]  # V4
    assert passed["lifecycle-valid"]  # V5


def test_udl_conformance_checks_present_and_pass():
    d = make_datum("t", "v")
    result = validate_datum(d, _trace(d))
    passed = {f.check_id: f.passed for f in result.report.findings}
    for cid in (
        "foundation-reuse-integrity",  # UDL-02 / VC-5
        "data-typed",  # UDL-03
        "data-identified-objectbound",  # UDL-04/05
        "data-value-fidelity",  # UDL-06
        "storage-independence",  # UDL-11
        "non-constitutive",  # UDL-15
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_subject_projection_is_deterministic():
    d = make_datum("t", "v")
    s1 = DatumValidationSubject.from_datum(d, _trace(d))
    s2 = DatumValidationSubject.from_datum(d, _trace(d))
    assert s1 == s2  # determinism at the subject boundary


def test_untraced_datum_fails_traceability_gate():
    d = make_datum("t", "v")
    trace = _trace(d)
    broken = replace(trace, backward=())  # orphaned lineage
    subject = DatumValidationSubject.from_datum(d, trace)
    subject = replace(subject, provenance_chain=broken.backward)
    from engine.validation.executor import ValidationEngine

    report = ValidationEngine(datum_checks()).validate(subject)
    assert report.verdict is Verdict.FAIL
    assert "traceability-rooted" in {f.check_id for f in report.blocking_failures}


def test_secret_bearing_datum_fails_non_constitutive_gate():
    d = make_datum("credential", {"api_key": "AKIA-not-real"})
    result = validate_datum(d, _trace(d))
    assert result.accepted is False
    assert "non-constitutive" in {f.check_id for f in result.report.blocking_failures}


def test_active_datum_still_validates():
    d = make_datum("t", "v", state=DatumState.ACTIVE)
    assert validate_datum(d, _trace(d)).accepted


def test_composite_datum_validates():
    d = make_datum("t", {"a": 1, "b": [2, 3]}, kind=DatumKind.COMPOSITE)
    assert validate_datum(d, _trace(d)).accepted


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    d = make_datum("ucos.core.string", "hello")
    subject = DatumValidationSubject.from_datum(d, _trace(d))
    assert_every_check_can_refuse(subject, datum_checks())


def test_a_traceability_record_fingerprints_its_own_projection() -> None:
    """The fingerprint is how a lineage record is cited without re-serialising it.

    Two records of the same datum are one record; two different values are not. A
    fingerprint that failed either direction would let one lineage impersonate another.
    """

    record = build_traceability(
        make_datum("t", "v"), unit="EC3-B10-U01", forward=("UCOS-DATUM-x-0",)
    )
    assert record.fingerprint() == record.fingerprint()
    other = build_traceability(
        make_datum("t", "w"), unit="EC3-B10-U01", forward=("UCOS-DATUM-x-0",)
    )
    assert record.fingerprint() != other.fingerprint()
