"""Tests for EC3-B13-U06 Topology & Distribution certification.

Covers:
- CCE ten gates (CC-1…CC-10)
- Infrastructure compliance (C1…C7)
- Certification ledger
"""

from __future__ import annotations

from engine.certification.ledger import CertificationLedger
from infrastructure.topology import (
    make_delivery_arrangement,
    make_distribution_arrangement,
    make_locality_map,
    make_placement_rule,
    make_topology,
)
from infrastructure.topology_certification import (
    ComplianceVerdict,
    cce_gates,
    certify_construct,
)
from infrastructure.topology_meta import REALIZATION_UNIT
from infrastructure.topology_traceability import build_traceability
from infrastructure.topology_validation import validate_construct


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

    def test_certification_certified(self):
        d = make_distribution_arrangement("test.dist", hosts=("ENG-005:AF-3:exp",))
        cert = _certify(d)
        assert cert.certified

    def test_topology_certified(self):
        t = make_topology("test.topology.foundation")
        cert = _certify(t)
        assert cert.certified

    def test_locality_map_certified(self):
        lm = make_locality_map("test.lm")
        cert = _certify(lm)
        assert cert.certified

    def test_placement_rule_certified(self):
        pr = make_placement_rule("test.pr")
        cert = _certify(pr)
        assert cert.certified

    def test_delivery_certified(self):
        dl = make_delivery_arrangement("test.del", hosts=("ENG-005:AF-3:exp",))
        cert = _certify(dl)
        assert cert.certified


class TestCompliance:
    def test_compliance_verdict_structure(self):
        d = make_distribution_arrangement("test.d", hosts=("ENG-005:AF-3:svc",))
        cert = _certify(d)
        comp = cert.compliance
        assert isinstance(comp, ComplianceVerdict)
        assert len(comp.conditions) == 7

    def test_all_compliance_passes(self):
        constructs = [
            make_topology("t"),
            make_locality_map("t"),
            make_placement_rule("t"),
            make_distribution_arrangement("t", hosts=("ENG-005:c",)),
            make_delivery_arrangement("t", hosts=("ENG-005:c",)),
        ]
        for c in constructs:
            cert = _certify(c)
            assert cert.compliance.compliant, f"{c.meta_class} not compliant"

    def test_c4_distribution_hosts(self):
        """C4: Distribution typed, hosts AF-3/SF-2 by reference."""
        d = make_distribution_arrangement("test.d", hosts=("ENG-005:AF-3:exp",))
        cert = _certify(d)
        c4 = cert.compliance.conditions[3]  # C4 is index 3
        assert c4["status"] == "pass"

    def test_c5_topology_acyclic(self):
        """C5: Topology uses ENG-005 references, founding acyclic."""
        t = make_topology("test.t")
        cert = _certify(t)
        c5 = cert.compliance.conditions[4]  # C5 is index 4
        assert c5["status"] == "pass"

    def test_c7_technology_independence(self):
        """C7: No technology selection."""
        t = make_topology("test.t")
        cert = _certify(t)
        c7 = cert.compliance.conditions[6]  # C7 is index 6
        assert c7["status"] == "pass"


class TestCertificationLedger:
    def test_ledger_append(self):
        ledger = CertificationLedger()
        d = make_distribution_arrangement("test.d", hosts=("ENG-005:cap",))
        trace = build_traceability(d, unit=REALIZATION_UNIT, forward=(d.construct_id, "test"))
        validation = validate_construct(d, trace)
        cert = certify_construct(validation, version="1.0.0", ledger=ledger)
        assert len(ledger.entries) == 1

    def test_ledger_head_hash(self):
        ledger = CertificationLedger()
        t = make_topology("test.topo")
        trace = build_traceability(t, unit=REALIZATION_UNIT, forward=(t.construct_id, "test"))
        validation = validate_construct(t, trace)
        certify_construct(validation, version="1.0.0", ledger=ledger)
        assert ledger.head_hash is not None
        assert len(ledger.head_hash) > 0

    def test_ledger_serialization(self):
        ledger = CertificationLedger()
        constructs = [
            make_topology("t1"),
            make_locality_map("t2"),
            make_placement_rule("t3"),
        ]
        for c in constructs:
            trace = build_traceability(c, unit=REALIZATION_UNIT, forward=(c.construct_id, "test"))
            validation = validate_construct(c, trace)
            certify_construct(validation, version="1.0.0", ledger=ledger)
        d = ledger.to_dict()
        assert d["count"] == 3


def test_the_traceability_record_fingerprints_its_own_projection() -> None:
    """The fingerprint is how this band cites its lineage record without reserialising it.

    Two builds of one construct agree to the byte; a different forward chain does not.
    """
    construct = make_topology("t.topo")
    record_a = build_traceability(construct, unit="EC3-B13-U06", forward=("X",))
    record_b = build_traceability(construct, unit="EC3-B13-U06", forward=("X",))
    assert record_a.fingerprint() == record_b.fingerprint()
    other = build_traceability(construct, unit="EC3-B13-U06", forward=("Y",))
    assert record_a.fingerprint() != other.fingerprint()
