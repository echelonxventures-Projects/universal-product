"""Tests for EC3-B13-U07 Resilience & Availability validation.

Covers meta-validity (WF-1…12), UIL conformance (UIL-01…15), and governing obligations
(WF-9 / UIL-13 — ScalingArrangement posture valid, no artificial ceiling; WF-10 —
evaluative non-enforcing; UIL-15 — technology independence).
"""

from __future__ import annotations

from engine.tests import assert_every_check_can_refuse
from infrastructure.resilience import (
    make_availability_topology,
    make_scaling_arrangement,
)
from infrastructure.resilience_meta import REALIZATION_UNIT
from infrastructure.resilience_traceability import build_traceability
from infrastructure.resilience_validation import (
    ResilienceValidationSubject,
    resilience_checks,
    validate_construct,
)


def _trace_for(construct):
    return build_traceability(
        construct,
        unit=REALIZATION_UNIT,
        forward=(construct.construct_id, "test-validation"),
    )


class TestAvailabilityTopologyValidation:
    """Validation checks for the AvailabilityTopology construct."""

    def test_availability_topology_valid(self):
        at = make_availability_topology("test.availability.foundation")
        trace = _trace_for(at)
        result = validate_construct(at, trace)
        assert result.accepted
        assert result.report.verdict.value == "pass"

    def test_availability_posture_valid(self):
        at = make_availability_topology("test.at", resilience_posture="fault-tolerant")
        trace = _trace_for(at)
        subject = ResilienceValidationSubject.from_construct(at, trace)
        checks = resilience_checks()
        posture_check = [c for c in checks if c.check_id == "posture-valid"]
        assert len(posture_check) == 1
        finding = posture_check[0].evaluate(subject)
        assert finding.passed


class TestScalingArrangementValidation:
    """Validation checks for the ScalingArrangement construct."""

    def test_scaling_arrangement_valid(self):
        sa = make_scaling_arrangement("test.scaling.foundation")
        trace = _trace_for(sa)
        result = validate_construct(sa, trace)
        assert result.accepted

    def test_scaling_posture_valid(self):
        sa = make_scaling_arrangement("test.sa", scaling_posture="unbounded")
        trace = _trace_for(sa)
        subject = ResilienceValidationSubject.from_construct(sa, trace)
        checks = resilience_checks()
        posture_check = [c for c in checks if c.check_id == "posture-valid"]
        assert len(posture_check) == 1
        finding = posture_check[0].evaluate(subject)
        assert finding.passed

    def test_no_artificial_ceiling_check(self):
        sa = make_scaling_arrangement("test.sa", scaling_posture="elastic")
        trace = _trace_for(sa)
        subject = ResilienceValidationSubject.from_construct(sa, trace)
        checks = resilience_checks()
        ceiling_check = [c for c in checks if c.check_id == "no-artificial-ceiling"]
        assert len(ceiling_check) == 1
        finding = ceiling_check[0].evaluate(subject)
        assert finding.passed


class TestAllChecks:
    """Meta-validation checks common to all constructs."""

    def test_typed_check_for_all(self):
        constructs = [
            make_availability_topology("t"),
            make_scaling_arrangement("t"),
        ]
        for c in constructs:
            trace = _trace_for(c)
            result = validate_construct(c, trace)
            assert result.accepted, f"{c.meta_class} validation failed"

    def test_meta_class_single(self):
        at = make_availability_topology("test.at")
        assert at.meta_class == "AvailabilityTopology"
        sa = make_scaling_arrangement("test.sa")
        assert sa.meta_class == "ScalingArrangement"

    def test_foundation_reuse_integrity(self):
        constructs = [
            make_availability_topology("t"),
            make_scaling_arrangement("t"),
        ]
        for c in constructs:
            assert not c.redefines_foundation()

    def test_non_enforcing_check(self):
        constructs = [
            make_availability_topology("t"),
            make_scaling_arrangement("t"),
        ]
        for c in constructs:
            assert c.is_evaluative_facet()
            assert not c.enacts_enforcement()


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    _c = make_availability_topology("test.availability.foundation")
    assert_every_check_can_refuse(
        ResilienceValidationSubject.from_construct(_c, _trace_for(_c)), resilience_checks()
    )
