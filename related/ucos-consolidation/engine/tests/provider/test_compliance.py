"""Tests for the provider constitutional compliance + mandatory architectural proof."""

from __future__ import annotations

from engine.provider.compliance import (
    PROOF_CATEGORIES,
    _framework_has_no_closed_enum,
    _mechanism_vendor_tokens,
    architectural_proof,
    constitutional_report,
    framework_source_fingerprint,
    quality_gates,
)


def test_architectural_proof_all_categories():
    proof = architectural_proof()
    assert proof["passed"] is True
    assert proof["categories_proven"] == len(PROOF_CATEGORIES)
    assert proof["kernel_unchanged"] is True
    assert proof["framework_unchanged"] is True
    for r in proof["records"]:
        assert r["ok"] and r["discoverable"] and r["resolvable"] and r["traceable"]


def test_quality_gates_all_pass():
    gates = quality_gates()
    assert gates["passed"] is True
    ids = {g["id"] for g in gates["gates"]}
    assert ids == {
        "no-closed-provider-categories",
        "no-finite-enumeration",
        "no-vendor-technology-coupling",
        "kernel-immutable",
        "open-world",
        "knowledge-once",
        "unknown-future-compatibility",
    }
    for g in gates["gates"]:
        assert g["passed"] is True, g


def test_constitutional_report_compliant_and_deterministic():
    a = constitutional_report()
    b = constitutional_report()
    assert a["passed"] is True
    assert a["verdict"] == "CONSTITUTIONALLY-COMPLIANT"
    assert a["report_hash"] == b["report_hash"]


def test_no_vendor_tokens_in_mechanism():
    assert _mechanism_vendor_tokens() == []


def test_framework_has_no_closed_enum():
    ok, offenders = _framework_has_no_closed_enum()
    assert ok is True
    assert offenders == []


def test_enum_detector_flags_control_sample(tmp_path):
    (tmp_path / "closed.py").write_text(
        "from enum import Enum\n\nclass Kind(Enum):\n    A = 1\n", encoding="utf-8"
    )
    ok, offenders = _framework_has_no_closed_enum(tmp_path)
    assert ok is False and any("closed.py:Kind" in o for o in offenders)


def test_fingerprint_stable():
    assert framework_source_fingerprint() == framework_source_fingerprint()
