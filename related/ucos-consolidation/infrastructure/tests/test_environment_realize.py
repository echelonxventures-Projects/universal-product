"""EC3-B13-U05 — Realization + determinism tests (VC-4, AC-1…7, VC-1…5, evidence, CLI)."""

from __future__ import annotations

import json
from dataclasses import replace

from infrastructure.environment import make_node
from infrastructure.environment_certification import (
    EnvComplianceReport,
    certify_construct,
)
from infrastructure.environment_realize import (
    CANONICAL_BOUNDARY_TYPE,
    CANONICAL_ENVIRONMENT_TYPE,
    CANONICAL_LOCALITY_TYPE,
    CANONICAL_RESOURCE_REF,
    NAMESAKE_META_CLASS,
    UNIT_VERSION,
    ConstructRealization,
    RealizationResult,
    build_canonical_composition,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from infrastructure.environment_traceability import build_traceability
from infrastructure.environment_validation import validate_construct

LOC = "ENG-005:INFRASTRUCTURE-011:locality.foundation"


def test_realization_determination_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.all_accepted() is True
    assert result.all_certified() is True
    assert result.all_traceable() is True
    assert result.containment_acyclic is True
    assert len(result.realizations) == 6  # all six concern-011 constructs


def test_canonical_composition_is_the_environment_foundation():
    comp = build_canonical_composition()
    assert comp.locality.type_tag == CANONICAL_LOCALITY_TYPE
    assert comp.boundary.type_tag == CANONICAL_BOUNDARY_TYPE
    assert comp.environment.type_tag == CANONICAL_ENVIRONMENT_TYPE
    # The composition is downward-only: env → cluster → node → resource; env declares boundary.
    assert comp.environment.boundary_ref == comp.boundary.construct_id
    assert comp.environment.contains == (comp.cluster.construct_id,)
    assert comp.cluster.contains == (comp.node.construct_id,)
    assert comp.node.contains == (CANONICAL_RESOURCE_REF,)
    assert comp.provisioning.provisions == (CANONICAL_RESOURCE_REF,)
    assert len(comp.ordered()) == 6


def test_namesake_and_lookups():
    result = realize()
    assert result.namesake.construct.meta_class == NAMESAKE_META_CLASS
    assert result.by_meta_class("Locality").construct.meta_class == "Locality"
    ids = result.construct_ids()
    assert set(ids) == {
        "Locality",
        "IsolationBoundary",
        "Node",
        "Cluster",
        "Environment",
        "ProvisioningProcess",
    }
    cert_ids = result.certification_ids()
    assert cert_ids["Environment"].startswith("UCOS-CERT-Environment-")


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
    mv = result.meta_validity()
    assert set(mv) == {"WF-1", "WF-2", "WF-3", "WF-4", "WF-6", "WF-11", "WF-12"}
    assert all(mv.values())
    uil = result.uil_conformance()
    for law in (
        "UIL-01",
        "UIL-02",
        "UIL-03",
        "UIL-04",
        "UIL-05",
        "UIL-07",
        "UIL-09",
        "UIL-10",
        "UIL-15",
    ):
        assert uil[law], law


def test_certification_gates_and_compliance_roll_up():
    result = realize()
    assert all(result.certification_gates().values())  # CC-1…CC-10 across all six
    assert all(result.environment_compliance().values())  # C1…C7 across all six


def test_shared_ledger_carries_six_entries():
    result = realize()
    assert len(result.ledger) == 6
    assert result.ledger.verify() is True
    assert result.ledger.head_hash == result.ledger.to_dict()["entries"][-1]["entry_hash"]


def test_double_realization_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True  # VC-4
    assert digest_a == digest_b
    assert len(digest_a) == 64


def test_bundle_shape_is_deterministic_and_complete():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == "EC3-B13-U05"
    assert bundle["meta_classes"] == [
        "Locality",
        "IsolationBoundary",
        "Node",
        "Cluster",
        "Environment",
        "ProvisioningProcess",
    ]
    assert bundle["authority"] == "ENGINEERING-EXECUTION-ONLY"
    assert bundle["determination"] == "COMPLETE"
    assert bundle["containment_acyclic"] is True
    assert len(bundle["constructs"]) == 6
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
    assert summary["containment_acyclic"] is True
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
    # The shared ledger file carries all six certifications.
    ledger = json.loads((tmp_path / "certification-ledger.json").read_text())
    assert len(ledger["entries"]) == 6


def test_emitted_evidence_is_stable_across_runs(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    emit_evidence(a)
    emit_evidence(b)
    for name in ("realization-evidence.json", "certification-ledger.json", "traceability.json"):
        assert (a / name).read_text() == (b / name).read_text()  # no drift


def test_version_is_pinned():
    assert UNIT_VERSION == "1.0.0"


def test_cli_main_returns_zero(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    assert "[PASS] EC3-B13-U05 → COMPLETE" in capsys.readouterr().out
    bundle = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert bundle["determination"] == "COMPLETE"


def test_cli_main_reports_failure_when_not_complete(tmp_path, capsys, monkeypatch):
    def _failing_emit(_evidence_dir):
        return {
            "determination": "NOT COMPLETE",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "containment_acyclic": False,
            "byte_identical": False,
        }

    monkeypatch.setattr("infrastructure.environment_realize.emit_evidence", _failing_emit)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "[FAIL] EC3-B13-U05 → NOT COMPLETE" in capsys.readouterr().out


def _rejected_realization():
    techy = make_node("t", LOC, contains=("ENG-005:terraform:module",))
    trace = build_traceability(techy, unit="EC3-B13-U05", forward=(techy.construct_id,))
    validation = validate_construct(techy, trace)
    certification = certify_construct(validation, version=UNIT_VERSION)
    return ConstructRealization(
        construct=techy, trace=trace, validation=validation, certification=certification
    )


def test_determination_not_complete_for_rejected_construct():
    rejected = _rejected_realization()
    result = RealizationResult(
        composition=build_canonical_composition(),
        realizations=(rejected,),
        ledger=rejected.certification.ledger,
        containment_acyclic=True,
    )
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
    assert result.all_accepted() is False


def test_determination_complete_with_conditions_when_compliance_degraded():
    result = realize()
    namesake = result.namesake
    degraded_compliance = EnvComplianceReport(
        target_id=namesake.certification.compliance.target_id,
        conditions=({"id": "C1", "requirement": "x", "status": "fail", "backed_by": []},),
    )
    degraded_cert = replace(namesake.certification, compliance=degraded_compliance)
    degraded_realization = replace(namesake, certification=degraded_cert)
    new_realizations = tuple(
        degraded_realization if r.construct.meta_class == NAMESAKE_META_CLASS else r
        for r in result.realizations
    )
    degraded_result = replace(result, realizations=new_realizations)
    assert degraded_result.all_certified() is False  # compliance degraded
    assert all(r.certification.decision.certified for r in degraded_result.realizations) is True
    assert degraded_result.determination(byte_identical=True) == "COMPLETE WITH CONDITIONS"


def test_traceability_record_fingerprint_and_flags():
    comp = build_canonical_composition()
    trace = build_traceability(
        comp.environment, unit="EC3-B13-U05", forward=(comp.environment.construct_id,)
    )
    assert trace.rooted is True
    assert trace.closed is True
    assert trace.meta_class == "Environment"
    assert len(trace.fingerprint()) == 64  # deterministic content hash
    broken = replace(trace, backward=())
    assert broken.rooted is False
    assert broken.closed is False


def test_construct_realization_to_dict_shape():
    result = realize()
    payload = result.namesake.to_dict()
    assert set(payload) >= {
        "construct",
        "traceability",
        "validation",
        "certification",
        "infrastructure_compliance_C1_C7",
        "certification_id",
    }
