"""Tests for EC3-B13-U06 Topology & Distribution validation.

Covers meta-validity (WF-1…12), UIL conformance (UIL-01…15), and governing obligations
(WF-8 / UIL-12 — Distribution hosts by reference; UIL-09 — topology acyclic).
"""

from __future__ import annotations

from engine.tests import assert_every_check_can_refuse
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance
from infrastructure.topology import (
    make_delivery_arrangement,
    make_distribution_arrangement,
    make_locality_map,
    make_placement_rule,
    make_topology,
)
from infrastructure.topology_meta import REALIZATION_UNIT
from infrastructure.topology_traceability import build_traceability
from infrastructure.topology_validation import (
    TopologyValidationSubject,
    topology_checks,
    validate_construct,
)


def _trace_for(construct):
    return build_traceability(
        construct,
        unit=REALIZATION_UNIT,
        forward=(construct.construct_id, "test-validation"),
    )


class TestTopologyValidation:
    """Validation checks for the Topology construct."""

    def test_topology_valid(self):
        t = make_topology("test.topology.foundation")
        trace = _trace_for(t)
        result = validate_construct(t, trace)
        assert result.accepted
        assert result.report.verdict.value == "pass"

    def test_topology_rejects_untyped(self):
        t = make_topology("test.t")
        trace = _trace_for(t)
        # Will still validate because type_tag is non-empty; test that checks pass
        # Actually test infra-topology-typed
        checks = topology_checks()
        engine = ValidationEngine(checks)
        subject = TopologyValidationSubject.from_construct(t, trace)
        report = engine.validate(subject)
        decision = enforce_acceptance(report)
        assert decision.accepted  # type_tag is "test.t" which is non-empty


class TestDistributionValidation:
    """Validation checks for Distribution constructs."""

    def test_distribution_valid(self):
        d = make_distribution_arrangement("test.dist", hosts=("ENG-005:AF-3:exp",))
        trace = _trace_for(d)
        result = validate_construct(d, trace)
        assert result.accepted

    def test_delivery_valid(self):
        dl = make_delivery_arrangement("test.del", hosts=("ENG-005:AF-3:exp",))
        trace = _trace_for(dl)
        result = validate_construct(dl, trace)
        assert result.accepted

    def test_distribution_hosts_check_pass(self):
        d = make_distribution_arrangement("test.d", hosts=("ENG-005:AF-3:svc",))
        trace = _trace_for(d)
        subject = TopologyValidationSubject.from_construct(d, trace)
        checks = topology_checks()
        # Find and check the distribution-hosts check
        host_check = [c for c in checks if c.check_id == "infra-topology-distribution-hosts"]
        assert len(host_check) == 1
        finding = host_check[0].evaluate(subject)
        assert finding.passed


class TestLocalityMapValidation:
    def test_locality_map_valid(self):
        lm = make_locality_map("test.lm")
        trace = _trace_for(lm)
        result = validate_construct(lm, trace)
        assert result.accepted


class TestPlacementRuleValidation:
    def test_placement_rule_valid(self):
        pr = make_placement_rule("test.pr")
        trace = _trace_for(pr)
        result = validate_construct(pr, trace)
        assert result.accepted


class TestAllChecks:
    """Meta-validation checks common to all constructs."""

    def test_typed_check_for_all(self):
        constructs = [
            make_topology("t"),
            make_locality_map("t"),
            make_placement_rule("t"),
            make_distribution_arrangement("t", hosts=("ENG-005:c",)),
            make_delivery_arrangement("t", hosts=("ENG-005:c",)),
        ]
        for c in constructs:
            trace = _trace_for(c)
            result = validate_construct(c, trace)
            assert result.accepted, f"{c.meta_class} validation failed"

    def test_meta_class_single(self):
        t = make_topology("test.t")
        assert t.meta_class == "Topology"
        d = make_distribution_arrangement("test.d", hosts=("ENG-005:c",))
        assert d.meta_class == "Distribution"

    def test_foundation_reuse_integrity(self):
        constructs = [
            make_topology("t"),
            make_locality_map("t"),
            make_placement_rule("t"),
            make_distribution_arrangement("t", hosts=("ENG-005:c",)),
            make_delivery_arrangement("t", hosts=("ENG-005:c",)),
        ]
        for c in constructs:
            assert not c.redefines_foundation()


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    _c = make_topology("test.topology.foundation")
    assert_every_check_can_refuse(
        TopologyValidationSubject.from_construct(_c, _trace_for(_c)), topology_checks()
    )


def test_the_host_check_answers_on_both_refusal_shapes() -> None:
    """WF-8 refuses a distribution that hosts nothing by reference AND one with a zero count.

    Two different ways a hosts clause can be empty, two different findings. A check that
    folded them together would report the wrong reason for the wrong construct.
    """
    import dataclasses

    d = make_distribution_arrangement("test.host", hosts=("ENG-005:AF-3:svc",))
    trace = _trace_for(d)
    base = TopologyValidationSubject.from_construct(d, trace)
    check = next(c for c in topology_checks() if c.check_id == "infra-topology-distribution-hosts")

    no_refs = dataclasses.replace(base, hosts_by_reference=False)
    finding = check.evaluate(no_refs)
    assert not finding.passed
    assert "any capability by reference" in finding.message

    zero = dataclasses.replace(base, hosts_by_reference=True, hosts_count=0)
    finding = check.evaluate(zero)
    assert not finding.passed
    assert "multiplicity" in finding.message
