"""Tests for EC3-B13-U10 Infrastructure Integration certification (CCE + C1…C7)."""

from __future__ import annotations

from engine.certification.ledger import CertificationLedger
from infrastructure.integration import make_dependency
from infrastructure.integration_certification import cce_gates, certify_dependency
from infrastructure.integration_meta import REALIZATION_UNIT
from infrastructure.integration_traceability import build_traceability
from infrastructure.integration_validation import validate_dependency


def _validated():
    edge = make_dependency(
        "ucos.infrastructure.dependency.compute-reuses-capability",
        source_ref="ENG-005:EC3-B13-U02:infrastructure.compute",
        target_ref="ENG-005:EC3-B13-U01:infrastructure.capability",
        source_index=2,
        target_index=1,
        basis="reuses",
    )
    trace = build_traceability(
        edge,
        unit=REALIZATION_UNIT,
        forward=(edge.construct_id, "V", "C", "EC3-B13-U10-COMPLETION-REPORT"),
    )
    return validate_dependency(edge, trace)


class TestCertification:
    def test_ten_cce_gates(self):
        assert len(cce_gates()) == 10

    def test_certifies_valid_edge(self):
        cert = certify_dependency(_validated())
        assert cert.certified
        assert cert.decision.certification_id

    def test_all_gates_pass(self):
        cert = certify_dependency(_validated())
        assert all(f.passed for f in cert.decision.findings)

    def test_compliance_all_pass(self):
        cert = certify_dependency(_validated())
        assert cert.compliance.compliant
        assert all(c["status"] == "pass" for c in cert.compliance.conditions)

    def test_ledger_append_and_head(self):
        ledger = CertificationLedger()
        certify_dependency(_validated(), ledger=ledger)
        assert ledger.head_hash
        assert ledger.to_dict()["count"] == 1
        assert len(ledger.to_dict()["entries"]) == 1


def test_the_traceability_record_fingerprints_its_own_projection() -> None:
    """The fingerprint is how this band cites its lineage record without reserialising it.

    Two builds of one construct agree to the byte; a different forward chain does not.
    """
    construct = make_dependency(
        "t.ifp",
        source_ref="ENG-005:EC3-B13-U02:infrastructure.compute",
        target_ref="ENG-005:EC3-B13-U01:infrastructure.capability",
        source_index=2,
        target_index=1,
        basis="reuses",
    )
    record_a = build_traceability(construct, unit="EC3-B13-U10", forward=("X",))
    record_b = build_traceability(construct, unit="EC3-B13-U10", forward=("X",))
    assert record_a.fingerprint() == record_b.fingerprint()
    other = build_traceability(construct, unit="EC3-B13-U10", forward=("Y",))
    assert record_a.fingerprint() != other.fingerprint()
