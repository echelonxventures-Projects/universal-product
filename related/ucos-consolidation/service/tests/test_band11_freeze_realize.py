"""EC3-B11-U13 — Band-11 freeze realization tests (aggregation + determinism + evidence)."""

from __future__ import annotations

import json
from dataclasses import replace

from service import band11_freeze_realize
from service.band11_freeze_meta import EXPECTED_FROZEN_UNITS
from service.band11_freeze_realize import (
    build_band_freeze,
    determinism_check,
    emit_evidence,
    main,
    realize,
)


# ---------------------------------------------------------------------------
# Live aggregation of the twelve CERTIFIED units (U01…U12)
# ---------------------------------------------------------------------------


def test_build_band_freeze_inventories_twelve_certified_frozen_units():
    f = build_band_freeze()
    assert set(f.unit_ids()) == set(EXPECTED_FROZEN_UNITS)
    assert f.all_units_certified() is True
    assert f.all_units_frozen() is True
    assert f.inventory_complete() is True
    assert f.integration_closed() is True
    assert f.band_completion_referenced() is True
    assert f.band_completion_certification_id.startswith("UCOS-CERT-BAND-11-")
    assert f.meta_model_certification_id.startswith("UCOS-CERT-USM-")


def test_realization_is_frozen():
    result = realize()
    assert result.determination(byte_identical=True) == "FROZEN"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True
    assert result.all_units_certified() is True
    assert result.all_units_frozen() is True


def test_freeze_preconditions_and_effects_all_true():
    result = realize()
    fp = result.freeze_preconditions(byte_identical=True)
    assert set(fp) == {f"FP-{n}" for n in range(1, 7)}
    assert all(fp.values())
    fe = result.freeze_effects()
    assert set(fe) == {f"FE-{n}" for n in range(1, 6)}
    assert all(fe.values())


def test_precondition_fp6_reflects_determinism_flag():
    result = realize()
    assert result.freeze_preconditions(byte_identical=False)["FP-6"] is False
    assert result.freeze_preconditions(byte_identical=True)["FP-6"] is True


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


def test_frozen_inventory_lists_twelve_units():
    inv = realize().frozen_inventory()
    assert len(inv) == len(EXPECTED_FROZEN_UNITS)
    assert {u["unit"] for u in inv} == set(EXPECTED_FROZEN_UNITS)
    assert all(u["frozen"] for u in inv)


def test_bundle_shape():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == "EC3-B11-U13"
    assert bundle["freeze_class"] == "BAND-11-FREEZE"
    assert bundle["determination"] == "FROZEN"
    assert bundle["unit_count"] == len(EXPECTED_FROZEN_UNITS)
    assert bundle["all_units_certified"] is True
    assert bundle["all_units_frozen"] is True
    assert len(bundle["baseline_digest"]) == 64
    assert set(bundle["freeze_preconditions"]) == {f"FP-{n}" for n in range(1, 7)}
    assert set(bundle["freeze_effects"]) == {f"FE-{n}" for n in range(1, 6)}


# ---------------------------------------------------------------------------
# Alternate determination branches
# ---------------------------------------------------------------------------


def test_determination_frozen_with_conditions_when_not_byte_identical():
    result = realize()
    assert result.determination(byte_identical=False) == "FROZEN WITH CONDITIONS"


def test_determination_not_frozen_when_trace_not_closed():
    result = realize()
    degraded = replace(result, trace=replace(result.trace, forward=()))
    assert degraded.trace.closed is False
    assert degraded.determination(byte_identical=True) == "NOT FROZEN"


# ---------------------------------------------------------------------------
# Determinism (VC-4 / FP-6 — immutability guarantee)
# ---------------------------------------------------------------------------


def test_determinism_check_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True
    assert digest_a == digest_b
    assert len(digest_a) == 64


# ---------------------------------------------------------------------------
# Evidence emission + CLI
# ---------------------------------------------------------------------------


def test_emit_evidence_writes_deterministic_files(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "FROZEN"
    assert summary["all_units_certified"] is True
    assert summary["all_units_frozen"] is True
    assert summary["ready"] is True
    assert summary["effects_declared"] is True
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
        "freeze-baseline.json",
        "freeze-preconditions.json",
        "freeze-effects.json",
        "determinism.json",
    }
    written = {p.name for p in tmp_path.iterdir()}
    assert expected <= written
    first = (tmp_path / "realization-evidence.json").read_text(encoding="utf-8")
    emit_evidence(tmp_path)
    assert (tmp_path / "realization-evidence.json").read_text(encoding="utf-8") == first
    parsed = json.loads(first)
    assert parsed["determination"] == "FROZEN"
    baseline = json.loads((tmp_path / "freeze-baseline.json").read_text(encoding="utf-8"))
    assert baseline["unit_count"] == len(EXPECTED_FROZEN_UNITS)
    assert len(baseline["baseline_digest"]) == 64


def test_main_returns_zero_on_frozen(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    assert "EC3-B11-U13 → FROZEN" in capsys.readouterr().out


def test_main_returns_one_when_not_frozen(tmp_path, monkeypatch, capsys):
    def _degraded(evidence_dir):
        return {
            "unit": "EC3-B11-U13",
            "determination": "NOT FROZEN",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "byte_identical": False,
            "all_units_certified": False,
            "all_units_frozen": False,
            "ready": False,
            "effects_declared": False,
        }

    monkeypatch.setattr(band11_freeze_realize, "emit_evidence", _degraded)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "FAIL" in capsys.readouterr().out
