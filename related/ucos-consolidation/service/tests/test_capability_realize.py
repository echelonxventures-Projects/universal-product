"""EC3-B11-U02 — Realization + determinism tests (VC-4, AC-1…7, VC-1…5, evidence, CLI)."""

from __future__ import annotations

import json
from dataclasses import replace

from service.capability import make_capability
from service.capability_certification import certify_capability
from service.capability_realize import (
    CANONICAL_SERVICE_REF,
    CANONICAL_TYPE_TAG,
    UNIT_VERSION,
    RealizationResult,
    build_canonical_capability,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from service.capability_traceability import build_capability_traceability
from service.capability_validation import validate_capability
from service.service_certification import ServiceComplianceReport


def _rr(capability):
    trace = build_capability_traceability(
        capability, unit="EC3-B11-U02", forward=(capability.capability_id,)
    )
    validation = validate_capability(capability, trace)
    certification = certify_capability(validation, version=UNIT_VERSION)
    return RealizationResult(
        capability=capability, trace=trace, validation=validation, certification=certification
    )


def test_realization_determination_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True


def test_canonical_capability_shape():
    c = build_canonical_capability()
    assert c.type_tag == CANONICAL_TYPE_TAG
    assert c.service_ref == CANONICAL_SERVICE_REF
    assert c.meta_class == "SMC-02"


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
    assert all(result.meta_validity().values())  # V1…V5
    usl = result.usl_conformance()
    for law in ("USL-01", "USL-02", "USL-03", "USL-09", "USL-10", "USL-13", "USL-14", "USL-15"):
        assert usl[law], law


def test_certification_gates_and_compliance_roll_up():
    result = realize()
    assert all(result.certification_gates().values())  # CC-1…CC-10
    assert all(result.service_compliance().values())  # C1…C7


def test_double_realization_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True  # VC-4
    assert digest_a == digest_b
    assert len(digest_a) == 64


def test_bundle_shape_is_deterministic_and_complete():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == "EC3-B11-U02"
    assert bundle["meta_class"] == "SMC-02"
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
    a = tmp_path / "a"
    b = tmp_path / "b"
    emit_evidence(a)
    emit_evidence(b)
    for name in ("realization-evidence.json", "cce-certification.json", "traceability.json"):
        assert (a / name).read_text() == (b / name).read_text()  # no drift


def test_version_is_pinned():
    assert UNIT_VERSION == "1.0.0"


def test_cli_main_returns_zero(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    assert "[PASS] EC3-B11-U02 → COMPLETE" in capsys.readouterr().out
    bundle = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert bundle["determination"] == "COMPLETE"


def test_cli_main_reports_failure_when_not_complete(tmp_path, capsys, monkeypatch):
    def _failing_emit(_evidence_dir):
        return {
            "determination": "NOT COMPLETE",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "byte_identical": False,
        }

    monkeypatch.setattr("service.capability_realize.emit_evidence", _failing_emit)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "[FAIL] EC3-B11-U02 → NOT COMPLETE" in capsys.readouterr().out


def test_determination_not_complete_for_rejected_capability():
    result = _rr(make_capability("t", behavior_ref="ENG-005:RL-F2:kafka"))
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
    assert result.validation.accepted is False


def test_determination_complete_with_conditions_when_compliance_degraded():
    result = _rr(build_canonical_capability())
    degraded = ServiceComplianceReport(
        target_id=result.certification.compliance.target_id,
        conditions=({"id": "C1", "requirement": "x", "status": "fail", "backed_by": []},),
    )
    certification = replace(result.certification, compliance=degraded)
    result = replace(result, certification=certification)
    assert result.certification.decision.certified is True
    assert result.certification.certified is False  # compliance degraded
    assert result.determination(byte_identical=True) == "COMPLETE WITH CONDITIONS"


def test_traceability_record_fingerprint_and_flags():
    c = make_capability("t")
    trace = build_capability_traceability(c, unit="EC3-B11-U02", forward=(c.capability_id,))
    assert trace.rooted is True
    assert trace.closed is True
    assert len(trace.fingerprint()) == 64
    broken = replace(trace, backward=())
    assert broken.rooted is False
    assert broken.closed is False
