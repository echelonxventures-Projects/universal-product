"""EC3-B11-U03 — Realization + determinism tests (VC-4, AC-1…7, VC-1…5, evidence, CLI)."""

from __future__ import annotations

import json
from dataclasses import replace

from service.contract import make_contract
from service.contract_certification import certify_contract
from service.contract_meta import ContractKind
from service.contract_realize import (
    CANONICAL_TYPE_TAG,
    UNIT_VERSION,
    RealizationResult,
    build_canonical_contract,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from service.contract_traceability import build_contract_traceability
from service.contract_validation import validate_contract
from service.service_certification import ServiceComplianceReport


def _rr(contract):
    trace = build_contract_traceability(contract, unit="EC3-B11-U03", forward=(contract.contract_id,))
    validation = validate_contract(contract, trace)
    certification = certify_contract(validation, version=UNIT_VERSION)
    return RealizationResult(
        contract=contract, trace=trace, validation=validation, certification=certification
    )


def test_realization_determination_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True


def test_canonical_contract_shape():
    c = build_canonical_contract()
    assert c.type_tag == CANONICAL_TYPE_TAG
    assert c.kind is ContractKind.OPERATION
    assert c.meta_class == "SMC-03"
    assert c.inputs and c.outputs and c.effects and c.faults


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
    for law in ("USL-01", "USL-02", "USL-03", "USL-06", "USL-11", "USL-13", "USL-14", "USL-15"):
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
    assert bundle["unit"] == "EC3-B11-U03"
    assert bundle["meta_class"] == "SMC-03"
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
    assert "[PASS] EC3-B11-U03 → COMPLETE" in capsys.readouterr().out
    assert json.loads((tmp_path / "realization-evidence.json").read_text())["determination"] == "COMPLETE"


def test_cli_main_reports_failure_when_not_complete(tmp_path, capsys, monkeypatch):
    def _failing_emit(_evidence_dir):
        return {
            "determination": "NOT COMPLETE",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "byte_identical": False,
        }

    monkeypatch.setattr("service.contract_realize.emit_evidence", _failing_emit)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "[FAIL] EC3-B11-U03 → NOT COMPLETE" in capsys.readouterr().out


def test_determination_not_complete_for_rejected_contract():
    result = _rr(make_contract("t", inputs=("ENG-005:DF-2:kafka",), outputs=("ENG-005:DF-2:o",),
                               effects=("ENG-005:e",), faults=("ENG-005:f",)))
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
    assert result.validation.accepted is False


def test_determination_complete_with_conditions_when_compliance_degraded():
    result = _rr(build_canonical_contract())
    degraded = ServiceComplianceReport(
        target_id=result.certification.compliance.target_id,
        conditions=({"id": "C1", "requirement": "x", "status": "fail", "backed_by": []},),
    )
    result = replace(result, certification=replace(result.certification, compliance=degraded))
    assert result.certification.decision.certified is True
    assert result.certification.certified is False
    assert result.determination(byte_identical=True) == "COMPLETE WITH CONDITIONS"


def test_traceability_record_fingerprint_and_flags():
    c = build_canonical_contract()
    trace = build_contract_traceability(c, unit="EC3-B11-U03", forward=(c.contract_id,))
    assert trace.rooted is True and trace.closed is True
    assert len(trace.fingerprint()) == 64
    broken = replace(trace, backward=())
    assert broken.rooted is False and broken.closed is False
