"""EC3-B11-U11 — Meta-model realization tests (integration + determinism + evidence)."""

from __future__ import annotations

import json
from dataclasses import replace

from service import model_realize
from service.model_meta import META_CLASSES, META_INVARIANTS
from service.model_realize import (
    MemberCertification,
    build_canonical_metamodel,
    determinism_check,
    emit_evidence,
    main,
    realize,
    realize_members,
)


# ---------------------------------------------------------------------------
# Live integration of the ten CERTIFIED members
# ---------------------------------------------------------------------------


def test_realize_members_are_all_ten_and_certified():
    members = realize_members()
    assert len(members) == len(META_CLASSES)
    assert {m.meta_class for m in members} == set(META_CLASSES)
    assert all(m.certified for m in members)
    for m in members:
        assert m.certification_id.startswith(f"UCOS-CERT-{m.meta_class}-")
    # member certifications match the CERTIFIED ledger of U01…U10 by construction
    by_class = {m.meta_class: m.certification_id for m in members}
    assert by_class["SMC-01"] == "UCOS-CERT-SMC-01-6d805a1308da2f66"
    assert by_class["SMC-05"] == "UCOS-CERT-SMC-05-5a06bcad4a3086c8"
    assert by_class["SMC-10"] == "UCOS-CERT-SMC-10-fb17b391ed14db5d"


def test_member_certification_to_dict():
    d = realize_members()[0].to_dict()
    assert set(d) == {"meta_class", "unit", "certified", "certification_id"}


def test_build_canonical_metamodel_from_members():
    model = build_canonical_metamodel(realize_members())
    assert model.declares_closure() is True
    assert model.members_certified() is True


# ---------------------------------------------------------------------------
# Realization determination + roll-ups
# ---------------------------------------------------------------------------


def test_realization_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True
    assert result.members_all_certified() is True


def test_meta_invariants_all_satisfied():
    mi = realize().meta_invariants()
    assert set(mi) == set(META_INVARIANTS)
    assert all(mi.values())


def test_usl_conformance_all_satisfied():
    usl = realize().usl_conformance()
    assert usl["USL-01"] is True
    assert usl["USL-02"] is True  # materially exercised (reuse over ten CERTIFIED units)
    assert all(usl.values())


def test_acceptance_and_validation_criteria():
    result = realize()
    ac = result.acceptance_criteria()
    assert set(ac) == {f"AC-{n}" for n in range(1, 9)}
    assert all(ac.values())
    vc = result.validation_criteria(byte_identical=True)
    assert set(vc) == {f"VC-{n}" for n in range(1, 6)}
    assert all(vc.values())


def test_certification_gates_and_service_compliance_rollups():
    result = realize()
    assert result.certification_gates() == {f"CC-{n}": True for n in range(1, 11)}
    assert result.service_compliance() == {f"C{n}": True for n in range(1, 8)}


def test_integration_closure_all_true():
    closure = realize().integration_closure()
    assert all(closure.values())
    assert closure["all_members_certified"] is True
    assert closure["closure_SMI_01"] is True
    assert closure["non_projection_SMI_07"] is True


def test_bundle_shape_and_spine():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == "EC3-B11-U11"
    assert bundle["determination"] == "COMPLETE"
    assert "Meta-Model fixes" in bundle["spine"]
    assert len(bundle["member_certifications"]) == 10
    assert bundle["meta_invariant_definitions"] == dict(META_INVARIANTS)


# ---------------------------------------------------------------------------
# Alternate determination branches
# ---------------------------------------------------------------------------


def test_determination_complete_with_conditions_when_not_byte_identical():
    # A valid, accepted, certified, traced result that fails only the determinism gate
    # degrades to COMPLETE WITH CONDITIONS (not NOT COMPLETE).
    result = realize()
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"


def test_determination_not_complete_when_trace_not_closed():
    result = realize()
    broken = replace(result.trace, forward=())  # trace no longer closed
    degraded = replace(result, trace=broken)
    assert degraded.trace.closed is False
    assert degraded.determination(byte_identical=True) == "NOT COMPLETE"


# ---------------------------------------------------------------------------
# Determinism (VC-4)
# ---------------------------------------------------------------------------


def test_determinism_check_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True
    assert digest_a == digest_b
    assert len(digest_a) == 64


# ---------------------------------------------------------------------------
# Evidence emission + CLI
# ---------------------------------------------------------------------------


def test_emit_evidence_writes_ten_deterministic_files(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["members_all_certified"] is True
    assert summary["integration_closed"] is True
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
    written = {p.name for p in tmp_path.iterdir()}
    assert expected <= written
    # re-emission is byte-identical (deterministic outputs)
    first = (tmp_path / "realization-evidence.json").read_text(encoding="utf-8")
    emit_evidence(tmp_path)
    assert (tmp_path / "realization-evidence.json").read_text(encoding="utf-8") == first
    # the emitted bundle parses and carries the certified determination
    parsed = json.loads(first)
    assert parsed["determination"] == "COMPLETE"


def test_main_returns_zero_on_complete(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "EC3-B11-U11 → COMPLETE" in out


def test_main_returns_one_when_not_complete(tmp_path, monkeypatch, capsys):
    def _degraded(evidence_dir):
        return {
            "unit": "EC3-B11-U11",
            "determination": "NOT COMPLETE",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "byte_identical": False,
            "integration_closed": False,
            "members_all_certified": False,
        }

    monkeypatch.setattr(model_realize, "emit_evidence", _degraded)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "FAIL" in capsys.readouterr().out


def test_member_certification_dataclass_roundtrip():
    m = MemberCertification("SMC-02", "EC3-B11-U02", True, "UCOS-CERT-SMC-02-" + "a" * 16)
    assert m.to_dict()["certified"] is True
