"""Tests for EC3-B13-U07 Resilience & Availability certification.

Covers:
- CCE ten gates (CC-1…CC-10)
- Infrastructure compliance (C1…C7)
- Certification ledger
"""

from __future__ import annotations

from engine.certification.ledger import CertificationLedger
from infrastructure.resilience import (
    make_availability_topology,
    make_scaling_arrangement,
)
from infrastructure.resilience_certification import (
    ComplianceVerdict,
    cce_gates,
    certify_construct,
)
from infrastructure.resilience_meta import REALIZATION_UNIT
from infrastructure.resilience_traceability import build_traceability
from infrastructure.resilience_validation import validate_construct


def _certify(construct):
    trace = build_traceability(
        construct,
        unit=REALIZATION_UNIT,
        forward=(construct.construct_id, "test-cert"),
    )
    validation = validate_construct(construct, trace)
    return certify_construct(validation, version="1.0.0")


class TestCCEGates:
    def test_cce_gates_present(self):
        gates = cce_gates()
        assert len(gates) == 10
        for i, g in enumerate(gates, 1):
            assert g.criterion_id == f"CC-{i}"

    def test_availability_topology_certified(self):
        at = make_availability_topology("test.availability.foundation")
        cert = _certify(at)
        assert cert.certified

    def test_scaling_arrangement_certified(self):
        sa = make_scaling_arrangement("test.scaling.foundation")
        cert = _certify(sa)
        assert cert.certified


class TestCompliance:
    def test_compliance_verdict_structure(self):
        at = make_availability_topology("test.at")
        cert = _certify(at)
        comp = cert.compliance
        assert isinstance(comp, ComplianceVerdict)
        assert len(comp.conditions) == 7

    def test_all_compliance_passes(self):
        constructs = [
            make_availability_topology("t"),
            make_scaling_arrangement("t"),
        ]
        for c in constructs:
            cert = _certify(c)
            assert cert.compliance.compliant, f"{c.meta_class} not compliant"

    def test_c6_scaling_posture(self):
        """C6: Scaling posture unbounded, no artificial ceiling."""
        sa = make_scaling_arrangement("test.sa", scaling_posture="elastic")
        cert = _certify(sa)
        c6 = cert.compliance.conditions[5]  # C6 is index 5
        assert c6["status"] == "pass"

    def test_c7_technology_independence(self):
        """C7: No technology selection."""
        at = make_availability_topology("test.at")
        cert = _certify(at)
        c7 = cert.compliance.conditions[6]  # C7 is index 6
        assert c7["status"] == "pass"


class TestCertificationLedger:
    def test_ledger_append(self):
        ledger = CertificationLedger()
        at = make_availability_topology("test.at")
        trace = build_traceability(at, unit=REALIZATION_UNIT, forward=(at.construct_id, "test"))
        validation = validate_construct(at, trace)
        cert = certify_construct(validation, version="1.0.0", ledger=ledger)
        assert len(ledger.entries) == 1

    def test_ledger_head_hash(self):
        ledger = CertificationLedger()
        sa = make_scaling_arrangement("test.sa")
        trace = build_traceability(sa, unit=REALIZATION_UNIT, forward=(sa.construct_id, "test"))
        validation = validate_construct(sa, trace)
        certify_construct(validation, version="1.0.0", ledger=ledger)
        assert ledger.head_hash is not None
        assert len(ledger.head_hash) > 0

    def test_ledger_serialization(self):
        ledger = CertificationLedger()
        constructs = [
            make_availability_topology("t1"),
            make_scaling_arrangement("t2"),
        ]
        for c in constructs:
            trace = build_traceability(c, unit=REALIZATION_UNIT, forward=(c.construct_id, "test"))
            validation = validate_construct(c, trace)
            certify_construct(validation, version="1.0.0", ledger=ledger)
        d = ledger.to_dict()
        assert d["count"] == 2


def test_the_traceability_record_fingerprints_its_own_projection() -> None:
    """The fingerprint is how this band cites its lineage record without reserialising it.

    Two builds of one construct agree to the byte; a different forward chain does not.
    """
    construct = make_availability_topology("t.resfp")
    record_a = build_traceability(construct, unit="EC3-B13-U07", forward=("X",))
    record_b = build_traceability(construct, unit="EC3-B13-U07", forward=("X",))
    assert record_a.fingerprint() == record_b.fingerprint()
    other = build_traceability(construct, unit="EC3-B13-U07", forward=("Y",))
    assert record_a.fingerprint() != other.fingerprint()
