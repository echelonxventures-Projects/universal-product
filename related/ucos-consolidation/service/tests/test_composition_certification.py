"""EC3-B11-U06 — Composition certification tests (reused CCE CC-1…CC-10 + Service C1…C7)."""

from __future__ import annotations

from types import SimpleNamespace

from engine.certification.contracts import CertificationStatus
from engine.certification.ledger import CertificationLedger
from service.composition import make_composition
from service.composition_certification import (
    certify_composition,
    evaluate_composition_compliance,
)
from service.composition_meta import CompositionKind
from service.composition_traceability import build_composition_traceability
from service.composition_validation import validate_composition
from service.service_meta import CCE_GATES

_MEMBERS = ("ENG-005:SOE-05:op.a", "ENG-005:SOE-05:op.b")
_CON = "ENG-005:SOE-03:contract"


def _c(**kw):
    base = dict(kind=CompositionKind.AGGREGATION, data_refs=("ENG-005:DF-2:composite",))
    base.update(kw)
    type_tag = base.pop("type_tag", "t")
    members = base.pop("member_refs", _MEMBERS)
    return make_composition(type_tag, members, _CON, **base)


def _validate(composition):
    trace = build_composition_traceability(
        composition, unit="EC3-B11-U06", forward=(composition.composition_id,)
    )
    return validate_composition(composition, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_composition(_validate(_c()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    assert {f.criterion_id for f in cert.decision.findings} == set(CCE_GATES)
    assert all(f.passed for f in cert.decision.findings)


def test_overall_certification_is_sound():
    cert = certify_composition(_validate(_c()), version="1.0.0")
    assert cert.certified is True
    assert cert.ledger.verify() is True


def test_certification_record_authority_is_engineering_only():
    cert = certify_composition(_validate(_c()), version="1.0.0")
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_certification_id_is_deterministic():
    assert (
        certify_composition(_validate(_c()), version="1.0.0").decision.certification_id
        == certify_composition(_validate(_c()), version="1.0.0").decision.certification_id
    )


def test_composition_compliance_c1_c7_all_hold_with_notes():
    compliance = evaluate_composition_compliance(_validate(_c()))
    assert compliance.compliant is True
    by_id = {c["id"]: c for c in compliance.conditions}
    assert {c["id"] for c in compliance.conditions} == {f"C{n}" for n in range(1, 8)}
    for cid in ("C3", "C4", "C5", "C6"):
        assert "note" in by_id[cid], cid
    assert "MATERIALLY EXERCISED" in by_id["C5"]["note"]


def test_non_compliant_composition_is_not_certified():
    bad = _c(kind=CompositionKind.FEDERATION, member_refs=("ENG-005:SOE-01:grpc.peer", "ENG-005:SOE-01:s2"))
    cert = certify_composition(_validate(bad), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_supplied_ledger_is_reused():
    ledger = CertificationLedger()
    certify_composition(_validate(_c(type_tag="a")), version="1.0.0", ledger=ledger)
    certify_composition(_validate(_c(type_tag="b")), version="1.0.0", ledger=ledger)
    assert len(ledger) == 2


def test_compliance_fail_branch_when_backing_check_missing():
    fake = SimpleNamespace(
        report=SimpleNamespace(
            target_id="UCOS-COMPOSITION-x-0000000000000000",
            findings=[SimpleNamespace(check_id="non-constitutive", passed=True)],
        )
    )
    compliance = evaluate_composition_compliance(fake)  # type: ignore[arg-type]
    assert compliance.compliant is False
    assert {c["id"]: c["status"] for c in compliance.conditions}["C1"] == "fail"


def test_all_kinds_certify():
    for kind, members in (
        (CompositionKind.AGGREGATION, _MEMBERS),
        (CompositionKind.FEDERATION, ("ENG-005:SOE-01:s1", "ENG-005:SOE-01:s2")),
        (CompositionKind.DELEGATION, ("ENG-005:SOE-05:target",)),
    ):
        assert certify_composition(
            _validate(_c(kind=kind, member_refs=members)), version="1.0.0"
        ).certified is True, kind
