"""EC3-B10-U01 — Realization + determinism tests (VC-4, AC-1…7, VC-1…5, evidence)."""

from __future__ import annotations

import json

from data.realize import (
    UNIT_VERSION,
    determinism_check,
    emit_evidence,
    main,
    realize,
)


def test_realization_determination_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True


def test_acceptance_criteria_ac1_ac7_all_hold():
    result = realize()
    ac = result.acceptance_criteria()
    assert set(ac) == {f"AC-{n}" for n in range(1, 8)}
    assert all(ac.values()), ac


def test_validation_criteria_vc1_vc5_all_hold():
    result = realize()
    vc = result.validation_criteria(byte_identical=True)
    assert set(vc) == {f"VC-{n}" for n in range(1, 6)}
    assert all(vc.values()), vc


def test_meta_validity_and_udl_conformance_complete():
    result = realize()
    assert all(result.meta_validity().values())  # V1…V5
    udl = result.udl_conformance()
    for law in ("UDL-01", "UDL-02", "UDL-03", "UDL-06", "UDL-11", "UDL-15"):
        assert udl[law], law


def test_double_realization_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True  # VC-4
    assert digest_a == digest_b
    assert len(digest_a) == 64


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
        "data-compliance.json",
        "traceability.json",
        "determinism.json",
    }
    written = {p.name for p in tmp_path.iterdir()}
    assert expected <= written


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
    out = capsys.readouterr().out
    assert "[PASS] EC3-B10-U01 → COMPLETE" in out
    # the emitted bundle on disk is the authoritative machine-readable summary
    bundle = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert bundle["determination"] == "COMPLETE"


def test_determination_degrades_to_conditions_and_then_refuses():
    """The three determinations are a ladder, and only the top rung had ever been reached.
    A realization that is accepted, certified and traced but NOT byte-identical is
    COMPLETE WITH CONDITIONS — a real, reportable state — and one whose acceptance was
    withheld is NOT COMPLETE. Collapsing either into the other makes the top rung
    meaningless."""
    from dataclasses import replace as _replace

    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"

    validation = result.validation
    rejected = _replace(
        result,
        validation=_replace(validation, decision=_replace(validation.decision, accepted=False)),
    )
    assert rejected.validation.accepted is False
    assert rejected.determination(byte_identical=True) == "NOT COMPLETE"


def test_the_cli_refuses_a_determination_short_of_complete(tmp_path, capsys, monkeypatch):
    """The exit code is the whole point of the entry point: a run that emits evidence and
    exits zero regardless of what the evidence says is a reporter, not a gate."""
    from data import realize as module

    monkeypatch.setattr(
        module,
        "emit_evidence",
        lambda _dir: {
            "determination": "NOT COMPLETE",
            "validation_accepted": False,
            "certified": False,
            "traceability_closed": False,
            "byte_identical": False,
        },
    )
    assert main(["--evidence-dir", str(tmp_path)]) == 1
    assert "[FAIL]" in capsys.readouterr().out
