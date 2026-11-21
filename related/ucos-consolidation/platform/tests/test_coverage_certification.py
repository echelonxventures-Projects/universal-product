"""ZG-P-02 — coverage certification API tests (G4 evidence, fail-closed)."""

from __future__ import annotations

import itertools
from platform.coverage.certification import (
    CERTIFIED,
    DETERMINISTIC,
    NON_DETERMINISTIC,
    NOT_CERTIFIED,
    CoverageCertification,
    assess,
)
from platform.coverage.engine import CoverageEngine
from platform.coverage.errors import CoverageCertificationError
from platform.coverage.evidence import EvidenceBundle, EvidenceSource
from platform.tests._coverage_helpers import (
    K,
    complete_source,
    duplicate_source,
    edge,
    gapped_source,
    node,
)

import pytest


class _NonDeterministicSource(EvidenceSource):
    def __init__(self):
        self._counter = itertools.count()

    def collect(self) -> EvidenceBundle:
        i = next(self._counter)
        return EvidenceBundle.create(
            [node(K.UNIVERSE, f"UNI-{i}"), node(K.PHASE, "IMP-1")],
            [edge(K.UNIVERSE, f"UNI-{i}", K.PHASE, "IMP-1")],
        )


def test_certified_on_complete_graph_strict():
    cert = assess(CoverageEngine(complete_source()), strict=True)
    assert cert.coverage_certification_status == CERTIFIED
    assert cert.certified
    assert cert.coverage_status == "COMPLETE"
    assert cert.coverage_percentage == 100.0
    assert cert.coverage_gaps == ()
    assert cert.coverage_orphans == ()
    assert cert.coverage_violations == ()
    assert cert.coverage_determinism_status == DETERMINISTIC
    assert cert.reasons == ()
    assert cert.certification_id.startswith("UCOS-COVC-")


def test_gaps_block_strict_but_pass_baseline():
    strict = assess(CoverageEngine(gapped_source()), strict=True)
    assert strict.coverage_certification_status == NOT_CERTIFIED
    assert any(r.startswith("coverage-gaps") for r in strict.reasons)
    baseline = assess(CoverageEngine(gapped_source()), strict=False)
    # structural integrity + determinism hold ⇒ baseline certifies.
    assert baseline.coverage_certification_status == CERTIFIED
    assert baseline.coverage_status == "PARTIAL"


def test_violations_block_certification():
    cert = assess(CoverageEngine(duplicate_source()), strict=False)
    assert cert.coverage_certification_status == NOT_CERTIFIED
    assert any(r.startswith("structural-violations") for r in cert.reasons)


def test_nondeterminism_blocks_certification():
    cert = assess(CoverageEngine(_NonDeterministicSource()), strict=False)
    assert cert.coverage_determinism_status == NON_DETERMINISTIC
    assert cert.coverage_certification_status == NOT_CERTIFIED
    assert "recompute-non-deterministic" in cert.reasons


def test_assess_requires_engine():
    with pytest.raises(CoverageCertificationError):
        assess(object())  # type: ignore[arg-type]


def test_certification_to_dict_and_fingerprint():
    cert = assess(CoverageEngine(complete_source()))
    d = cert.to_dict()
    for key in (
        "coverage_status",
        "coverage_percentage",
        "coverage_gaps",
        "coverage_orphans",
        "coverage_violations",
        "coverage_fingerprint",
        "coverage_determinism_status",
        "coverage_certification_status",
    ):
        assert key in d
    assert cert.fingerprint()
    assert isinstance(cert, CoverageCertification)
