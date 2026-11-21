"""EC3-B13-U01 — Realization + determinism tests (VC-4, AC-1…7, VC-1…5, evidence, CLI)."""

from __future__ import annotations

import json
from dataclasses import replace

from infrastructure.capability import make_infrastructure_capability
from infrastructure.capability_certification import (
    CapabilityComplianceReport,
    certify_capability,
)
from infrastructure.capability_realize import (
    CANONICAL_ENABLES_REF,
    CANONICAL_TYPE_TAG,
    UNIT_VERSION,
    RealizationResult,
    build_canonical_capability,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from infrastructure.capability_traceability import build_traceability
from infrastructure.capability_validation import validate_capability


def test_realization_determination_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True


def test_canonical_capability_is_the_hosting_foundation():
    c = build_canonical_capability()
    assert c.type_tag == CANONICAL_TYPE_TAG
    assert c.enables_ref == CANONICAL_ENABLES_REF
    assert c.meta_class == "InfrastructureCapability"


def test_acceptance_criteria_ac1_ac7_all_hold():
    ac = realize().acceptance_criteria()
    assert set(ac) == {f"AC-{n}" for n in range(1, 8)}
    assert all(ac.values()), ac


def test_validation_criteria_vc1_vc5_all_hold():
    vc = realize().validation_criteria(byte_identical=True)
    assert set(vc) == {f"VC-{n}" for n in range(1, 6)}
    assert all(vc.values()), vc


def test_meta_validity_and_uil_conformance_complete():
    result = realize()
    assert all(result.meta_validity().values())  # WF-1/2/3/11/12
    uil = result.uil_conformance()
    for law in ("UIL-01", "UIL-02", "UIL-03", "UIL-06", "UIL-10", "UIL-13", "UIL-14", "UIL-15"):
        assert uil[law], law


def test_certification_gates_and_compliance_roll_up():
    result = realize()
    assert all(result.certification_gates().values())  # CC-1…CC-10
    assert all(result.capability_compliance().values())  # C1…C7


def test_double_realization_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True  # VC-4
    assert digest_a == digest_b
    assert len(digest_a) == 64


def test_bundle_shape_is_deterministic_and_complete():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == "EC3-B13-U01"
    assert bundle["meta_class"] == "InfrastructureCapability"
    assert bundle["authority"] == "ENGINEERING-EXECUTION-ONLY"
    assert bundle["determination"] == "COMPLETE"
    assert set(bundle["criteria"]) == {
        "acceptance",
        "validation",
        "certification_gates",
        "infrastructure_compliance",
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
        "infrastructure-compliance.json",
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
    assert "[PASS] EC3-B13-U01 → COMPLETE" in capsys.readouterr().out
    bundle = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert bundle["determination"] == "COMPLETE"


def test_cli_main_reports_failure_when_not_complete(tmp_path, capsys, monkeypatch):
    # Force a non-complete summary to exercise the fail-closed CLI branch (return 1).
    def _failing_emit(_evidence_dir):
        return {
            "determination": "NOT COMPLETE",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "byte_identical": False,
        }

    monkeypatch.setattr("infrastructure.capability_realize.emit_evidence", _failing_emit)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "[FAIL] EC3-B13-U01 → NOT COMPLETE" in capsys.readouterr().out


def test_determination_not_complete_for_rejected_capability():
    # A technology-selecting capability is rejected → determination NOT COMPLETE.
    bad = make_infrastructure_capability("t", "ENG-005:RL-F2:kubernetes")
    trace = build_traceability(bad, unit="EC3-B13-U01", forward=(bad.capability_id,))
    validation = validate_capability(bad, trace)
    certification = certify_capability(validation, version=UNIT_VERSION)
    result = RealizationResult(
        capability=bad, trace=trace, validation=validation, certification=certification
    )
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
    assert result.validation.accepted is False


def test_traceability_record_fingerprint_and_flags():
    c = make_infrastructure_capability("t", CANONICAL_ENABLES_REF)
    trace = build_traceability(c, unit="EC3-B13-U01", forward=(c.capability_id,))
    assert trace.rooted is True
    assert trace.closed is True
    assert len(trace.fingerprint()) == 64  # deterministic content hash
    broken = replace(trace, backward=())
    assert broken.rooted is False
    assert broken.closed is False


def test_determination_complete_with_conditions_when_certification_degraded():
    # A validly-certified decision whose compliance roll-up is degraded lands in the
    # bounded "COMPLETE WITH CONDITIONS" state (accepted + decision.certified + closed).
    c = build_canonical_capability()
    trace = build_traceability(c, unit="EC3-B13-U01", forward=(c.capability_id,))
    validation = validate_capability(c, trace)
    certification = certify_capability(validation, version=UNIT_VERSION)
    degraded_compliance = CapabilityComplianceReport(
        target_id=certification.compliance.target_id,
        conditions=({"id": "C1", "requirement": "x", "status": "fail", "backed_by": []},),
    )
    certification = replace(certification, compliance=degraded_compliance)
    result = RealizationResult(
        capability=c, trace=trace, validation=validation, certification=certification
    )
    assert result.certification.decision.certified is True
    assert result.certification.certified is False  # compliance degraded
    assert result.determination(byte_identical=True) == "COMPLETE WITH CONDITIONS"
