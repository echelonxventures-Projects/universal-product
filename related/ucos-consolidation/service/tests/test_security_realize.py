"""EC3-B11-U10 — Realization + determinism tests (VC-4, AC-1…7, VC-1…5, evidence, CLI)."""

from __future__ import annotations

import json
from dataclasses import replace

from service.security import make_security
from service.security_certification import certify_security
from service.security_meta import SecurityKind
from service.security_realize import (
    CANONICAL_TYPE_TAG,
    UNIT_VERSION,
    RealizationResult,
    build_canonical_security,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from service.security_traceability import build_security_traceability
from service.security_validation import validate_security
from service.service_certification import ServiceComplianceReport


def _rr(security):
    trace = build_security_traceability(
        security, unit="EC3-B11-U10", forward=(security.security_id,)
    )
    validation = validate_security(security, trace)
    certification = certify_security(validation, version=UNIT_VERSION)
    return RealizationResult(
        security=security,
        trace=trace,
        validation=validation,
        certification=certification,
    )


def test_realization_determination_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True


def test_canonical_security_shape():
    s = build_canonical_security()
    assert s.type_tag == CANONICAL_TYPE_TAG
    assert s.kind is SecurityKind.CONFIDENTIALITY
    assert s.meta_class == "SMC-10"
    assert s.subject_refs and s.policy_refs and s.data_refs
    assert s.runtime_reuse_valid() is True
    assert s.is_founding_acyclic() is True
    assert s.bears_data is True


def test_acceptance_criteria_ac1_ac7_all_hold():
    ac = realize().acceptance_criteria()
    assert set(ac) == {f"AC-{n}" for n in range(1, 8)}
    assert all(ac.values()), ac


def test_validation_criteria_vc1_vc5_all_hold():
    vc = realize().validation_criteria(byte_identical=True)
    assert set(vc) == {f"VC-{n}" for n in range(1, 6)}
    assert all(vc.values()), vc


def test_meta_validity_and_usl_conformance_complete():
    result = realize()
    assert all(result.meta_validity().values())
    usl = result.usl_conformance()
    for law in ("USL-01", "USL-02", "USL-03", "USL-10", "USL-11",
                "USL-13", "USL-14", "USL-15"):
        assert usl[law], law


def test_certification_gates_and_compliance_roll_up():
    result = realize()
    assert all(result.certification_gates().values())
    assert all(result.service_compliance().values())


def test_double_realization_is_byte_identical():
    byte_identical, a, b = determinism_check()
    assert byte_identical is True
    assert a == b and len(a) == 64


def test_bundle_shape_is_deterministic_and_complete():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == "EC3-B11-U10"
    assert bundle["meta_class"] == "SMC-10"
    assert bundle["authority"] == "ENGINEERING-EXECUTION-ONLY"
    assert bundle["determination"] == "COMPLETE"
    assert set(bundle["criteria"]) == {
        "acceptance",
        "validation",
        "certification_gates",
        "service_compliance",
    }


def test_emit_evidence_writes_all_artifacts(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["byte_identical"] is True
    expected = {
        "realization-evidence.json",
        "validation-report.json",
        "validation-evidence.json",
        "acceptance-decision.json",
        "cce-certification.json",
        "certification-evidence.json",
        "certification-ledger.json",
        "service-compliance.json",
        "traceability.json",
        "determinism.json",
    }
    assert expected <= {p.name for p in tmp_path.iterdir()}


def test_emitted_evidence_is_stable_across_runs(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    emit_evidence(a)
    emit_evidence(b)
    for name in ("realization-evidence.json", "cce-certification.json", "traceability.json"):
        assert (a / name).read_text() == (b / name).read_text()


def test_version_is_pinned():
    assert UNIT_VERSION == "1.0.0"


def test_cli_main_returns_zero(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    assert "[PASS] EC3-B11-U10 → COMPLETE" in capsys.readouterr().out
    payload = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert payload["determination"] == "COMPLETE"


def test_cli_main_reports_failure_when_not_complete(tmp_path, capsys, monkeypatch):
    def _failing_emit(_evidence_dir):
        return {
            "determination": "NOT COMPLETE",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "byte_identical": False,
        }

    monkeypatch.setattr("service.security_realize.emit_evidence", _failing_emit)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "[FAIL] EC3-B11-U10 → NOT COMPLETE" in capsys.readouterr().out


def test_determination_not_complete_for_rejected_security():
    result = _rr(make_security("t", ("ENG-005:SOE-10:t",), kind=SecurityKind.CONFIDENTIALITY))
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
    assert result.validation.accepted is False


def test_determination_complete_with_conditions_when_compliance_degraded():
    result = _rr(build_canonical_security())
    degraded = ServiceComplianceReport(
        target_id=result.certification.compliance.target_id,
        conditions=({"id": "C1", "requirement": "x", "status": "fail", "backed_by": []},),
    )
    result = replace(result, certification=replace(result.certification, compliance=degraded))
    assert result.certification.decision.certified is True
    assert result.certification.certified is False
    assert result.determination(byte_identical=True) == "COMPLETE WITH CONDITIONS"


def test_traceability_record_fingerprint_and_flags():
    s = build_canonical_security()
    trace = build_security_traceability(s, unit="EC3-B11-U10", forward=(s.security_id,))
    assert trace.rooted is True and trace.closed is True
    assert len(trace.fingerprint()) == 64
    broken = replace(trace, backward=())
    assert broken.rooted is False and broken.closed is False
