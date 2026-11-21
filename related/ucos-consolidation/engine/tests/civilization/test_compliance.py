"""The executed constitutional proof of the Meta-Civilization layer."""

from __future__ import annotations

import json

from engine.civilization.compliance import (
    PROHIBITED_TOKENS,
    PROOF_CATEGORIES,
    UNKNOWN_OPERATING_SYSTEMS,
    _closed_enum_offenders,
    _layer_has_no_closed_enum,
    architectural_proof,
    constitutional_report,
    layer_source_fingerprint,
    quality_gates,
)
from engine.civilization.metatypes import dimension_facet_keys


def test_every_quality_gate_passes():
    gates = quality_gates()
    failed = [gate["id"] for gate in gates["gates"] if not gate["passed"]]
    assert failed == []
    assert gates["passed"] is True
    # Every gate carries executed evidence, never a bare assertion.
    assert all(gate["evidence"] for gate in gates["gates"])


def test_the_architectural_proof_admits_every_mandated_category():
    proof = architectural_proof()
    assert proof["categories_proven"] == len(PROOF_CATEGORIES)
    assert proof["operating_systems_proven"] == len(UNKNOWN_OPERATING_SYSTEMS)
    assert proof["passed"] is True


def test_the_proof_changes_no_source_byte():
    proof = architectural_proof()
    assert proof["layer_unchanged"] is True
    assert proof["kernel_unchanged"] is True
    assert proof["layer_source_fingerprint_before"] == proof["layer_source_fingerprint_after"]
    assert proof["kernel_source_fingerprint_before"] == proof["kernel_source_fingerprint_after"]


def test_every_proof_record_is_discoverable_and_traceable():
    proof = architectural_proof()
    for record in proof["category_records"]:
        assert record["discoverable"] is True
        assert record["traceable"] is True
        assert record["governed"] is True
    for record in proof["operating_system_records"]:
        assert record["rooted_in_meta_kernel"] is True


def test_the_layer_declares_no_closed_enumeration():
    ok, offenders = _layer_has_no_closed_enum()
    assert ok is True
    assert offenders == []


def test_the_enum_scanner_flags_a_control_sample(tmp_path):
    (tmp_path / "closed.py").write_text(
        "import enum\n"
        "from enum import Enum\n"
        "class ByName(Enum):\n    A = 1\n"
        "class ByAttribute(enum.IntEnum):\n    B = 2\n"
        "class NotAnEnum:\n    pass\n",
        encoding="utf-8",
    )
    offenders = _closed_enum_offenders(tmp_path)
    assert "closed.py::ByName" in offenders
    assert "closed.py::ByAttribute" in offenders
    assert "closed.py::NotAnEnum" not in offenders


def test_no_prohibited_token_is_built_into_the_vocabulary():
    from engine.civilization.compliance import _vocabulary_keys

    assert _vocabulary_keys() & set(PROHIBITED_TOKENS) == set()


def test_the_constitutional_report_is_reproducible():
    first = constitutional_report()
    second = constitutional_report()
    assert first["verdict"] == "CONSTITUTIONALLY-COMPLIANT"
    assert first["passed"] is True
    assert first["report_hash"] == second["report_hash"]
    assert first["authority"] == "NONE"
    assert first["mandatory_dimension_facets"] == list(dimension_facet_keys())


def test_the_report_is_json_serialisable():
    payload = json.dumps(constitutional_report(), sort_keys=True)
    assert "CONSTITUTIONALLY-COMPLIANT" in payload


def test_the_fingerprint_is_stable_across_calls():
    assert layer_source_fingerprint() == layer_source_fingerprint()
