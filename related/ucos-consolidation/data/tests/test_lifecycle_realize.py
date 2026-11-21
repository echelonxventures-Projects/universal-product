"""EC3-B10-U06 — Realization + determinism tests (VC-4, AC-1…8, VC-1…5, spine)."""

from __future__ import annotations

import json

from data.lifecycle_realize import (
    CANONICAL_LIFECYCLE_NAME,
    UNIT_VERSION,
    build_canonical_lifecycle,
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


def test_lifecycle_transitions_the_certified_entity_by_reference():
    result = realize()
    # the realized lifecycle transitions the CERTIFIED-surface Entity's identity by reference
    assert result.lifecycle.transitions_subject(result.transitioned_entity.entity_id)  # DMR-06
    assert result.lifecycle.absorbs_subject() is False  # DLA-07 / DMX-02 non-owning


def test_full_spine_lifecycle_transitions_entity():
    result = realize()
    sc = result.spine_closure()
    assert sc["transitions_entity"] is True  # DMR-06
    assert sc["forward_only"] is True  # DLA-01
    assert sc["transitions_recorded"] is True  # DLA-03 / DMR-11
    assert sc["binds_runtime_by_reference"] is True  # DMR-11 / DLA-07
    assert sc["technology_neutral"] is True  # UDL-12 / DLA-K5


def test_acceptance_criteria_ac1_ac8_all_hold():
    result = realize()
    ac = result.acceptance_criteria()
    assert set(ac) == {f"AC-{n}" for n in range(1, 9)}
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
    for law in ("UDL-01", "UDL-02", "UDL-03", "UDL-04", "UDL-12", "UDL-13", "UDL-15"):
        assert udl[law], law


def test_certification_gates_and_compliance_complete():
    result = realize()
    assert all(result.certification_gates().values())  # CC-1…CC-10
    assert all(result.data_compliance().values())  # C1…C7


def test_double_realization_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True  # VC-4
    assert digest_a == digest_b
    assert len(digest_a) == 64


def test_canonical_builder_is_consistent():
    lifecycle = build_canonical_lifecycle()
    assert lifecycle.name == CANONICAL_LIFECYCLE_NAME
    assert lifecycle.transitions  # declares the forward-only chain
    assert lifecycle.is_forward_only() is True
    assert lifecycle.names_technology() is False


def test_emit_evidence_writes_all_artifacts(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["byte_identical"] is True
    assert summary["spine_closed"] is True
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
    assert "[PASS] EC3-B10-U06 → COMPLETE" in out
    bundle = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert bundle["determination"] == "COMPLETE"
    assert bundle["meta_class"] == "DMC-07"


def test_determination_degrades_to_conditions_and_then_refuses():
    """The three determinations are a ladder, and only the top rung had ever been reached.
    A realization that is accepted, certified and traced but NOT byte-identical is
    COMPLETE WITH CONDITIONS — a real, reportable state — and one that fails validation is
    NOT COMPLETE. Collapsing either into the other would make the top rung meaningless."""
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
