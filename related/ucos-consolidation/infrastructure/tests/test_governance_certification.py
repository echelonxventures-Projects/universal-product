"""Tests for EC3-B13-U09 Infrastructure Governance certification (CCE + compliance)."""

from __future__ import annotations

import pytest

from engine.certification.ledger import CertificationLedger
from infrastructure.governance import GovernanceFacetKind, make_governance_facet
from infrastructure.governance_certification import cce_gates, certify_construct
from infrastructure.governance_meta import REALIZATION_UNIT
from infrastructure.governance_traceability import build_traceability
from infrastructure.governance_validation import validate_construct

_ALL_FACETS = (
    GovernanceFacetKind.CONFORMANCE,
    GovernanceFacetKind.LIFECYCLE,
    GovernanceFacetKind.POLICY,
    GovernanceFacetKind.GAP_REPORT,
    GovernanceFacetKind.CHANGE_RECORD,
)


def _certify(facet: GovernanceFacetKind, ledger=None):
    gf = make_governance_facet(f"t.{facet.value}", facet)
    trace = build_traceability(gf, unit=REALIZATION_UNIT, forward=(gf.construct_id, "EVID"))
    validation = validate_construct(gf, trace)
    return certify_construct(validation, ledger=ledger)


def test_cce_has_ten_gates() -> None:
    gates = cce_gates()
    assert len(gates) == 10
    ids = [g.criterion_id for g in gates]
    assert ids == [f"CC-{n}" for n in range(1, 11)]


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_certified(facet: GovernanceFacetKind) -> None:
    cert = _certify(facet)
    assert cert.certified
    assert cert.decision.certification_id.startswith("UCOS-CERT-Governance-")


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_compliant_c1_c7(facet: GovernanceFacetKind) -> None:
    cert = _certify(facet)
    assert cert.compliance.compliant
    ids = [c["id"] for c in cert.compliance.conditions]
    assert ids == ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    for cond in cert.compliance.conditions:
        assert cond["status"] == "pass", f"{cond['id']} not pass"


def test_ledger_hash_chained() -> None:
    ledger = CertificationLedger()
    for facet in _ALL_FACETS:
        _certify(facet, ledger=ledger)
    d = ledger.to_dict()
    assert d["count"] == 5
    entries = d["entries"]
    # first entry links to the zero hash; each subsequent prev_hash == prior entry_hash
    assert entries[0]["prev_hash"] == "0" * 64
    for i in range(1, len(entries)):
        assert entries[i]["prev_hash"] == entries[i - 1]["entry_hash"]
    assert d["head_hash"] == entries[-1]["entry_hash"]


def test_the_traceability_record_fingerprints_its_own_projection() -> None:
    """The fingerprint is how this band cites its lineage record without reserialising it.

    Two builds of one construct agree to the byte; a different forward chain does not.
    """
    construct = make_governance_facet("t.govfp", GovernanceFacetKind.CONFORMANCE)
    record_a = build_traceability(construct, unit="EC3-B13-U09", forward=("X",))
    record_b = build_traceability(construct, unit="EC3-B13-U09", forward=("X",))
    assert record_a.fingerprint() == record_b.fingerprint()
    other = build_traceability(construct, unit="EC3-B13-U09", forward=("Y",))
    assert record_a.fingerprint() != other.fingerprint()
