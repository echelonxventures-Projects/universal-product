"""EC3-B10-U02 — Realization + determinism tests (VC-4, AC-1…8, VC-1…5, evidence)."""

from __future__ import annotations

import json
from dataclasses import replace

from data.attribute_realize import (
    CANONICAL_ATTRIBUTE_NAME,
    CANONICAL_ATTRIBUTE_TYPE_TAG,
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


def test_attribute_values_the_certified_datum_by_reference():
    result = realize()
    # the realized attribute's value reference is the CERTIFIED-surface Datum's identity
    assert result.attribute.value_ref.datum_id == result.value_datum.datum_id  # DMR-02
    assert result.attribute.absorbs_value() is False  # DMX-02 non-absorbing


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
    for law in ("UDL-01", "UDL-02", "UDL-03", "UDL-06", "UDL-08", "UDL-11", "UDL-15"):
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
    assert "[PASS] EC3-B10-U02 → COMPLETE" in out
    bundle = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert bundle["determination"] == "COMPLETE"
    assert bundle["meta_class"] == "DMC-03"


def test_determination_falls_to_conditions_when_determinism_is_not_claimed() -> None:
    """VC-4 is byte-identity, and the ladder below COMPLETE exists — both rungs must answer.

    A determination that could only say COMPLETE or NOT COMPLETE would be a bool wearing a
    name: `COMPLETE WITH CONDITIONS` is the honest middle state (accepted, certified and
    traceable, determinism not re-proved in this call), and it had no case.
    """
    result = realize()
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"


def test_determination_refuses_a_result_that_was_never_accepted() -> None:
    """NOT COMPLETE: the roll-up must disagree loudly when the validation did not accept.

    The real bundle is always accepted, so the arm is forced by a result whose validation
    says otherwise — the same code path a future broken realization would take.
    """

    result = realize()

    class _Hollow:
        accepted = False

        class report:
            findings = ()

    hollow = _Hollow()
    weakened = replace(result, validation=hollow)
    assert weakened.determination(byte_identical=True) == "NOT COMPLETE"


def test_the_canonical_attribute_is_constructible_directly_and_carries_its_own_anchors() -> None:
    """The exemplar the band documents is built by a function nobody called directly."""
    from data.attribute_realize import build_canonical_attribute

    attribute = build_canonical_attribute()
    assert attribute.name == CANONICAL_ATTRIBUTE_NAME
    assert attribute.type_tag == CANONICAL_ATTRIBUTE_TYPE_TAG
