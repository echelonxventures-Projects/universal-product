"""EC3-B11-U05 — Realization + determinism tests (VC-4, AC-1…7, VC-1…5, evidence, CLI)."""

from __future__ import annotations

import json
from dataclasses import replace

from service.operation import make_operation
from service.operation_certification import certify_operation
from service.operation_meta import EffectKind, OperationKind
from service.operation_realize import (
    CANONICAL_TYPE_TAG,
    UNIT_VERSION,
    RealizationResult,
    build_canonical_operation,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from service.operation_traceability import build_operation_traceability
from service.operation_validation import validate_operation
from service.service_certification import ServiceComplianceReport


def _rr(operation):
    trace = build_operation_traceability(
        operation, unit="EC3-B11-U05", forward=(operation.operation_id,)
    )
    validation = validate_operation(operation, trace)
    certification = certify_operation(validation, version=UNIT_VERSION)
    return RealizationResult(
        operation=operation, trace=trace, validation=validation, certification=certification
    )


def test_realization_determination_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True


def test_canonical_operation_shape():
    o = build_canonical_operation()
    assert o.type_tag == CANONICAL_TYPE_TAG
    assert o.kind is OperationKind.COMMAND
    assert o.meta_class == "SMC-05"
    assert o.service_ref and o.contract_ref and o.interface_ref
    assert o.input_refs and o.output_refs and o.effects and o.faults


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
    for law in ("USL-01", "USL-02", "USL-03", "USL-06", "USL-08", "USL-10", "USL-11", "USL-13", "USL-14", "USL-15"):
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
    assert bundle["unit"] == "EC3-B11-U05"
    assert bundle["meta_class"] == "SMC-05"
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
    assert "[PASS] EC3-B11-U05 → COMPLETE" in capsys.readouterr().out
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

    monkeypatch.setattr("service.operation_realize.emit_evidence", _failing_emit)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "[FAIL] EC3-B11-U05 → NOT COMPLETE" in capsys.readouterr().out


def test_determination_not_complete_for_rejected_operation():
    result = _rr(make_operation(
        "t", "ENG-005:SOE-01:svc", "ENG-005:SOE-03:contract", "ENG-005:SOE-04:iface",
        kind=OperationKind.COMMAND,
        input_refs=("ENG-005:DF-2:kafka.topic",),
        output_refs=("ENG-005:DF-2:resp",),
        effects=(EffectKind.WRITE,),
        faults=("ucos.fault.bad-input",),
    ))
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
    assert result.validation.accepted is False


def test_determination_complete_with_conditions_when_compliance_degraded():
    result = _rr(build_canonical_operation())
    degraded = ServiceComplianceReport(
        target_id=result.certification.compliance.target_id,
        conditions=({"id": "C1", "requirement": "x", "status": "fail", "backed_by": []},),
    )
    result = replace(result, certification=replace(result.certification, compliance=degraded))
    assert result.certification.decision.certified is True
    assert result.certification.certified is False
    assert result.determination(byte_identical=True) == "COMPLETE WITH CONDITIONS"


def test_traceability_record_fingerprint_and_flags():
    o = build_canonical_operation()
    trace = build_operation_traceability(o, unit="EC3-B11-U05", forward=(o.operation_id,))
    assert trace.rooted is True and trace.closed is True
    assert len(trace.fingerprint()) == 64
    broken = replace(trace, backward=())
    assert broken.rooted is False and broken.closed is False
