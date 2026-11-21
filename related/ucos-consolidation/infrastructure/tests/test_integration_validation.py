"""Tests for EC3-B13-U10 Infrastructure Integration validation."""

from __future__ import annotations

from engine.tests import assert_every_check_can_refuse
from infrastructure.integration import make_dependency
from infrastructure.integration_meta import REALIZATION_UNIT
from infrastructure.integration_traceability import build_traceability
from infrastructure.integration_validation import (
    IntegrationValidationSubject,
    integration_checks,
    validate_dependency,
)


def _edge():
    return make_dependency(
        "ucos.infrastructure.dependency.compute-reuses-capability",
        source_ref="ENG-005:EC3-B13-U02:infrastructure.compute",
        target_ref="ENG-005:EC3-B13-U01:infrastructure.capability",
        source_index=2,
        target_index=1,
        basis="reuses",
    )


def _trace(edge):
    return build_traceability(
        edge,
        unit=REALIZATION_UNIT,
        forward=(edge.construct_id, "V", "C", "EC3-B13-U10-COMPLETION-REPORT"),
    )


class TestValidationSuite:
    def test_suite_has_eighteen_checks(self):
        assert len(integration_checks()) == 18

    def test_all_check_ids_unique(self):
        ids = [c.check_id for c in integration_checks()]
        assert len(ids) == len(set(ids))

    def test_valid_edge_accepted(self):
        edge = _edge()
        result = validate_dependency(edge, _trace(edge))
        assert result.accepted
        assert result.report.verdict.value == "pass"

    def test_all_findings_pass_for_valid_edge(self):
        edge = _edge()
        result = validate_dependency(edge, _trace(edge))
        assert all(f.passed for f in result.report.findings)

    def test_endpoints_resolve_to_known_concerns(self):
        edge = _edge()
        result = validate_dependency(edge, _trace(edge))
        passed = {f.check_id: f.passed for f in result.report.findings}
        assert passed["dependency-endpoints-resolve"]

    def test_unknown_endpoint_fails_resolution(self):
        # A syntactically valid but unregistered endpoint fails the endpoints-resolve check.
        edge = make_dependency(
            "ucos.infrastructure.dependency.unknown-reuses-capability",
            source_ref="ENG-005:EC3-B13-U99:infrastructure.unknown",
            target_ref="ENG-005:EC3-B13-U01:infrastructure.capability",
            source_index=99,
            target_index=1,
            basis="reuses",
        )
        result = validate_dependency(edge, _trace(edge))
        passed = {f.check_id: f.passed for f in result.report.findings}
        assert not passed["dependency-endpoints-resolve"]
        assert not result.accepted


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    _e = _edge()
    assert_every_check_can_refuse(
        IntegrationValidationSubject.from_construct(_e, _trace(_e)), integration_checks()
    )
