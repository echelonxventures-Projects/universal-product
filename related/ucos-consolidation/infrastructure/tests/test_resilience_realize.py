"""Tests for EC3-B13-U07 Resilience & Availability realization.

Covers:
- Canonical composition construction
- Realization result structure
- Determinism check
- Evidence emission
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest as _pytest

from infrastructure.resilience_realize import (
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
        assert (
            comp.availability_topology.type_tag
            == "ucos.infrastructure.availabilitytopology.foundation"
        )
        assert (
            comp.scaling_arrangement.type_tag == "ucos.infrastructure.scalingarrangement.foundation"
        )

    def test_composition_ordered(self):
        comp = build_canonical_composition()
        ordered = comp.ordered()
        assert len(ordered) == 2
        assert ordered[0].meta_class == "AvailabilityTopology"
        assert ordered[1].meta_class == "ScalingArrangement"


class TestRealization:
    def test_realize_returns_result(self):
        result = realize()
        assert isinstance(result, RealizationResult)
        assert result.ledger is not None

    def test_all_constructs_realized(self):
        result = realize()
        assert len(result.realizations) == 2

    def test_all_constructs_accepted(self):
        result = realize()
        assert result.all_accepted()

    def test_all_constructs_certified(self):
        result = realize()
        assert result.all_certified()

    def test_all_constructs_traceable(self):
        result = realize()
        assert result.all_traceable()

    def test_meta_validity_passes(self):
        result = realize()
        mv = result.meta_validity()
        for wf, ok in mv.items():
            assert ok, f"WF {wf} failed"

    def test_uil_conformance_passes(self):
        result = realize()
        uc = result.uil_conformance()
        for law, ok in uc.items():
            assert ok, f"UIL {law} failed"

    def test_determination_complete(self):
        result = realize()
        det = result.determination(byte_identical=True)
        assert det == "COMPLETE", f"Determination: {det}"


class TestDeterminism:
    def test_determinism_check_passes(self):
        byte_identical, a, b = determinism_check()
        assert byte_identical, "determinism check failed"
        assert a == b

    def test_double_realize_identical(self):
        r1 = realize().to_bundle(byte_identical=True)
        r2 = realize().to_bundle(byte_identical=True)
        assert r1 == r2


class TestEvidence:
    def test_emit_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_dir = Path(tmp) / "_evidence" / REALIZATION_UNIT
            summary = emit_evidence(evidence_dir)
            assert summary["determination"] == "COMPLETE"
            assert summary["validation_accepted"]
            assert summary["certified"]
            assert summary["traceability_closed"]
            assert summary["byte_identical"]

    def test_evidence_files_written(self):
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
                assert (evidence_dir / name).exists(), f"Missing: {name}"

    def test_evidence_files_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_dir = Path(tmp) / "_evidence" / REALIZATION_UNIT
            emit_evidence(evidence_dir)
            for path in evidence_dir.iterdir():
                if path.suffix == ".json":
                    data = json.loads(path.read_text(encoding="utf-8"))
                    assert data is not None


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
        result.by_meta_class("NO-SUCH-CLASS")
