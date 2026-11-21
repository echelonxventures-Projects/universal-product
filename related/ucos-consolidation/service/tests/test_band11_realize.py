"""EC3-B11-U12 — Band-11 completion realization tests (aggregation + determinism + evidence)."""

from __future__ import annotations

import json
from dataclasses import replace

from service import band11_realize
from service.band11_meta import EXPECTED_UNITS
from service.band11_realize import (
    build_band_completion,
    determinism_check,
    emit_evidence,
    main,
    realize,
)


# ---------------------------------------------------------------------------
# Live aggregation of the eleven CERTIFIED units (U01…U11)
# ---------------------------------------------------------------------------


def test_build_band_completion_inventories_eleven_certified_units():
    c = build_band_completion()
    assert set(c.unit_ids()) == set(EXPECTED_UNITS)
    assert c.all_units_certified() is True
    assert c.inventory_complete() is True
    assert c.integration_closed() is True
    # the meta-model unit carries the certified USM id
    assert c.meta_model_certification_id.startswith("UCOS-CERT-USM-")


def test_realization_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True
    assert result.all_units_certified() is True


def test_readiness_and_completion_criteria_all_true():
    result = realize()
    brc = result.readiness_criteria(byte_identical=True)
    assert set(brc) == {f"BRC-{n}" for n in range(1, 9)}
    assert all(brc.values())
    bcc = result.completion_criteria()
    assert set(bcc) == {f"BCC-{n}" for n in range(1, 9)}
    assert all(bcc.values())


def test_readiness_brc8_reflects_determinism_flag():
    result = realize()
    assert result.readiness_criteria(byte_identical=False)["BRC-8"] is False
    assert result.readiness_criteria(byte_identical=True)["BRC-8"] is True


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


def test_unit_inventory_lists_eleven_units():
    inv = realize().unit_inventory()
    assert len(inv) == len(EXPECTED_UNITS)
    assert {u["unit"] for u in inv} == set(EXPECTED_UNITS)


def test_bundle_shape():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == "EC3-B11-U12"
    assert bundle["band_class"] == "BAND-11"
    assert bundle["determination"] == "COMPLETE"
    assert bundle["unit_count"] == len(EXPECTED_UNITS)
    assert bundle["all_units_certified"] is True
    assert set(bundle["readiness_criteria"]) == {f"BRC-{n}" for n in range(1, 9)}
    assert set(bundle["completion_criteria"]) == {f"BCC-{n}" for n in range(1, 9)}


# ---------------------------------------------------------------------------
# Alternate determination branches
# ---------------------------------------------------------------------------


def test_determination_complete_with_conditions_when_not_byte_identical():
    result = realize()
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"


def test_determination_not_complete_when_trace_not_closed():
    result = realize()
    degraded = replace(result, trace=replace(result.trace, forward=()))
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


def test_emit_evidence_writes_deterministic_files(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["all_units_certified"] is True
    assert summary["ready"] is True
    assert summary["complete"] is True
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
        "capability-inventory.json",
        "readiness-determination.json",
        "completion-determination.json",
        "determinism.json",
    }
    written = {p.name for p in tmp_path.iterdir()}
    assert expected <= written
    first = (tmp_path / "realization-evidence.json").read_text(encoding="utf-8")
    emit_evidence(tmp_path)
    assert (tmp_path / "realization-evidence.json").read_text(encoding="utf-8") == first
    parsed = json.loads(first)
    assert parsed["determination"] == "COMPLETE"
    inv = json.loads((tmp_path / "capability-inventory.json").read_text(encoding="utf-8"))
    assert inv["unit_count"] == len(EXPECTED_UNITS)


def test_main_returns_zero_on_complete(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    assert "EC3-B11-U12 → COMPLETE" in capsys.readouterr().out


def test_main_returns_one_when_not_complete(tmp_path, monkeypatch, capsys):
    def _degraded(evidence_dir):
        return {
            "unit": "EC3-B11-U12",
            "determination": "NOT COMPLETE",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "byte_identical": False,
            "all_units_certified": False,
            "ready": False,
            "complete": False,
        }

    monkeypatch.setattr(band11_realize, "emit_evidence", _degraded)
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 1
    assert "FAIL" in capsys.readouterr().out
