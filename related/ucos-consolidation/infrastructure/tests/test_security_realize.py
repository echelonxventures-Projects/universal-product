"""Tests for EC3-B13-U08 Infrastructure Security realization + evidence emission."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest as _pytest

from infrastructure.security_realize import (
    NAMESAKE_FACET,
    REALIZATION_UNIT,
    Composition,
    RealizationResult,
    build_canonical_composition,
    determinism_check,
    emit_evidence,
    realize,
)


class TestComposition:
    def test_build_canonical_composition(self):
        comp = build_canonical_composition()
        assert isinstance(comp, Composition)
        assert comp.isolation.facet_value == "isolation"
        assert comp.integrity.facet_value == "integrity"

    def test_composition_ordered_five_facets(self):
        ordered = build_canonical_composition().ordered()
        assert len(ordered) == 5
        assert [c.facet_value for c in ordered] == [
            "isolation",
            "authentication",
            "authorization",
            "confidentiality",
            "integrity",
        ]
        # all instantiate the single SecurityFacet meta-class (WF-1)
        assert {c.meta_class for c in ordered} == {"SecurityFacet"}


class TestRealization:
    def test_realize_returns_result(self):
        result = realize()
        assert isinstance(result, RealizationResult)
        assert len(result.realizations) == 5

    def test_all_accepted_certified_traceable(self):
        result = realize()
        assert result.all_accepted()
        assert result.all_certified()
        assert result.all_traceable()

    def test_meta_validity_passes(self):
        for wf, ok in realize().meta_validity().items():
            assert ok, f"WF {wf} failed"

    def test_uil_conformance_passes(self):
        for law, ok in realize().uil_conformance().items():
            assert ok, f"UIL {law} failed"

    def test_compliance_passes(self):
        for cid, ok in realize().security_compliance().items():
            assert ok, f"compliance {cid} failed"

    def test_determination_complete(self):
        assert realize().determination(byte_identical=True) == "COMPLETE"

    def test_five_distinct_certification_ids(self):
        result = realize()
        cids = result.certification_ids()
        assert len(cids) == 5
        assert len(set(cids.values())) == 5

    def test_namesake_is_integrity(self):
        result = realize()
        assert result.namesake.construct.facet_value == NAMESAKE_FACET


class TestDeterminism:
    def test_determinism_check_passes(self):
        byte_identical, a, b = determinism_check()
        assert byte_identical
        assert a == b

    def test_double_realize_identical(self):
        assert realize().to_bundle(byte_identical=True) == realize().to_bundle(byte_identical=True)


class TestEvidence:
    def test_emit_evidence_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = emit_evidence(Path(tmp) / "_evidence" / REALIZATION_UNIT)
            assert summary["determination"] == "COMPLETE"
            assert summary["validation_accepted"]
            assert summary["certified"]
            assert summary["traceability_closed"]
            assert summary["byte_identical"]

    def test_evidence_files_written_and_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_dir = Path(tmp) / "_evidence" / REALIZATION_UNIT
            emit_evidence(evidence_dir)
            expected = [
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
            ]
            for name in expected:
                p = evidence_dir / name
                assert p.exists(), f"Missing: {name}"
                assert json.loads(p.read_text(encoding="utf-8")) is not None


def test_determination_ladder_answers_below_complete() -> None:
    """The ladder below COMPLETE — conditions and refusal — had no case on this band.

    The real bundle always realizes to COMPLETE, so the two lower rungs were never observed.
    A determination with three outcomes and one measured path is two outcomes pretending.
    The conditions rung is reached by withholding the determinism claim; the refusal rung by
    a result whose acceptance roll-up says otherwise — the shape a broken future realization
    would take, forced here rather than assumed.
    """

    result = realize()
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"

    class _NeverAccepted(RealizationResult):
        def all_accepted(self) -> bool:
            return False

    weakened = _NeverAccepted(result.composition, result.realizations, result.ledger)
    assert weakened.determination(byte_identical=True) == "NOT COMPLETE"


def test_unknown_lookup_raises_instead_of_returning_a_default() -> None:
    """A lookup that answered None would turn a miss into a silent pass downstream."""

    result = realize()
    with _pytest.raises(KeyError):
        result.by_facet("no-such-facet")
