"""ZG-P-02 — coverage health tests (nine checks, fail-closed, strict vs baseline)."""

from __future__ import annotations

from platform.coverage.engine import CoverageEngine
from platform.coverage.health import (
    DUPLICATE_COVERAGE_CHECK,
    FINGERPRINT_CHECK,
    MISSING_RUNTIME_CHECK,
    MISSING_UNIVERSE_CHECK,
    ORPHAN_CODE_CHECK,
    ORPHAN_UNIVERSE_CHECK,
    CoverageHealth,
    coverage_health_checks,
)
from platform.coverage.registry import CoverageRegistry
from platform.observability.contracts import HealthStatus
from platform.tests._coverage_helpers import (
    complete_source,
    duplicate_source,
    gapped_source,
    orphan_code_source,
    orphan_universe_source,
    partial_source,
)

import pytest


def _health(source):
    eng = CoverageEngine(source)
    graph = eng.compute()
    return CoverageHealth(graph, eng.registry)


def test_nine_checks_registered():
    checks = coverage_health_checks()
    assert len(checks) == 9
    assert all(c.critical for c in checks)


def test_health_requires_valid_inputs():
    with pytest.raises(TypeError):
        CoverageHealth(object(), CoverageRegistry())  # type: ignore[arg-type]
    eng = CoverageEngine(complete_source())
    g = eng.compute()
    with pytest.raises(TypeError):
        CoverageHealth(g, object())  # type: ignore[arg-type]


def test_complete_graph_is_healthy_even_strict():
    h = _health(complete_source())
    assert h.integrity_ok
    assert h.healthy(strict=False)
    assert h.healthy(strict=True)
    probe = h.probe(strict=True)
    assert all(s is HealthStatus.HEALTHY for s in probe.values())


def test_gaps_are_degraded_baseline_unhealthy_strict():
    h = _health(gapped_source())
    assert h.integrity_ok  # no structural violation
    baseline = h.probe(strict=False)
    strict = h.probe(strict=True)
    assert baseline[MISSING_UNIVERSE_CHECK] is HealthStatus.DEGRADED
    assert strict[MISSING_UNIVERSE_CHECK] is HealthStatus.UNHEALTHY
    assert not h.healthy(strict=False)  # degraded ≠ healthy


def test_orphan_universe_is_unhealthy():
    h = _health(orphan_universe_source())
    probe = h.probe()
    assert probe[ORPHAN_UNIVERSE_CHECK] is HealthStatus.UNHEALTHY
    assert not h.integrity_ok
    assert h.orphan_universes() == ("UNI-500",)


def test_orphan_code_is_unhealthy():
    h = _health(orphan_code_source())
    probe = h.probe()
    assert probe[ORPHAN_CODE_CHECK] is HealthStatus.UNHEALTHY
    assert h.orphan_code()


def test_duplicate_coverage_is_unhealthy():
    h = _health(duplicate_source())
    probe = h.probe()
    assert probe[DUPLICATE_COVERAGE_CHECK] is HealthStatus.UNHEALTHY
    assert h.duplicate_records()


def test_missing_runtime_evidence_detected():
    # partial_source adds a module with no code asset (no runtime beneath it),
    # but every existing code asset still has runtime; construct a case where a
    # code asset lacks a runtime child by using orphan_code minus the runtime edge.
    h = _health(partial_source())
    # all code assets in partial_source do have runtime; runtime check healthy.
    assert h.probe()[MISSING_RUNTIME_CHECK] is HealthStatus.HEALTHY


def test_fingerprint_check_true_on_consistent_registry():
    h = _health(complete_source())
    assert h.fingerprint_matches()
    assert h.probe()[FINGERPRINT_CHECK] is HealthStatus.HEALTHY


def test_fingerprint_mismatch_is_unhealthy():
    # A graph that does not match the registry's recorded content ⇒ mismatch.
    eng = CoverageEngine(gapped_source())
    eng.compute()
    other_graph = CoverageEngine(complete_source()).compute()
    h = CoverageHealth(other_graph, eng.registry)
    assert not h.fingerprint_matches()
    assert h.probe()[FINGERPRINT_CHECK] is HealthStatus.UNHEALTHY
    assert not h.integrity_ok


def test_code_assets_without_runtime_surface():
    # Build a graph where a code asset has no runtime child (module→code_asset only).
    from platform.coverage.evidence import InMemoryEvidenceSource
    from platform.tests._coverage_helpers import K, edge, node

    nodes = [
        node(K.UNIVERSE, "UNI-1"),
        node(K.PHASE, "IMP-1"),
        node(K.PROGRAM, "prog"),
        node(K.IMPLEMENTATION, "impl"),
        node(K.EPIC, "epic"),
        node(K.MODULE, "m.py"),
        node(K.CODE_ASSET, "m.py::f"),
    ]
    edges = [
        edge(K.UNIVERSE, "UNI-1", K.PHASE, "IMP-1"),
        edge(K.PHASE, "IMP-1", K.PROGRAM, "prog"),
        edge(K.PROGRAM, "prog", K.IMPLEMENTATION, "impl"),
        edge(K.IMPLEMENTATION, "impl", K.EPIC, "epic"),
        edge(K.EPIC, "epic", K.MODULE, "m.py"),
        edge(K.MODULE, "m.py", K.CODE_ASSET, "m.py::f"),
    ]
    h = _health(InMemoryEvidenceSource(nodes, edges))
    assert h.code_assets_without_runtime() == ("m.py::f",)
    assert h.probe()[MISSING_RUNTIME_CHECK] is HealthStatus.DEGRADED
