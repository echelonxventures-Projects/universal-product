"""EC3-B13-U05 — Certification tests (CCE CC-1…CC-10 + Infrastructure C1…C7 + shared ledger).

Per-gate negative coverage is achieved by constructing a crafted
:class:`engine.certification.contracts.CertificationSubject` and flipping the single signal
each gate aggregates, then calling the gate's ``evaluate`` directly.
"""

from __future__ import annotations

from engine.certification.contracts import (
    CertificationClass,
    CertificationStatus,
    CertificationSubject,
    CriterionStatus,
)
from engine.certification.ledger import CertificationLedger
from infrastructure.environment import (
    make_environment,
    make_locality,
    make_node,
    make_provisioning_process,
)
from infrastructure.environment_certification import (
    EnvComplianceReport,
    Gate1Architecture,
    Gate2Dependencies,
    Gate3Coverage,
    Gate4Validation,
    Gate5Traceability,
    Gate6Evidence,
    Gate7CertificationReady,
    Gate8Readiness,
    Gate9GapZero,
    Gate10Completeness,
    cce_gates,
    certify_construct,
    evaluate_environment_compliance,
)
from infrastructure.environment_meta import CCE_GATES
from infrastructure.environment_traceability import build_traceability
from infrastructure.environment_validation import environment_checks, validate_construct

LOC = "ENG-005:INFRASTRUCTURE-011:locality.foundation"
BOUND = "ENG-005:INFRASTRUCTURE-011:isolation.boundary.a"
RES = "ENG-005:INFRASTRUCTURE-007:compute.resource"

_ALL_CHECKS = tuple(c.check_id for c in environment_checks())


def _env():
    return make_environment("ucos.demo.env", BOUND, LOC, contains=(RES,))


def _validate(construct):
    trace = build_traceability(construct, unit="EC3-B13-U05", forward=(construct.construct_id,))
    return validate_construct(construct, trace)


def _good_subject(**overrides) -> CertificationSubject:
    """A crafted certification subject where every gate would otherwise close."""
    base = dict(
        target_id="UCOS-INFRA-ENVIRONMENT-ucos.demo.env-0000000000000000",
        blueprint_id="Environment",
        version="1.0.0",
        certification_class=CertificationClass.ENGINEERING_READINESS,
        validation_verdict="pass",
        validation_accepted=True,
        checks_run=_ALL_CHECKS,
        blocking_failures=(),
        counts={"failed": 0, "total": len(_ALL_CHECKS)},
        evidence_present=True,
        evidence_sha256="a" * 64,
    )
    base.update(overrides)
    return CertificationSubject(**base)


# --- happy path -------------------------------------------------------------


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_construct(_validate(_env()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    assert {f.criterion_id for f in cert.decision.findings} == set(CCE_GATES)  # CC-1…CC-10
    assert all(f.passed for f in cert.decision.findings)
    assert len(cce_gates()) == 10


def test_certification_record_is_immutable_and_self_verifying():
    cert = certify_construct(_validate(_env()), version="1.0.0")
    assert cert.decision.record.verify_integrity() is True
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"  # DE-05
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_ledger_is_append_only_and_hash_chain_intact():
    cert = certify_construct(_validate(_env()), version="1.0.0")
    assert cert.ledger.verify() is True  # CC-10 chain intact
    assert len(cert.ledger) == 1
    assert cert.ledger_entry.sequence == 0
    assert cert.ledger_entry.prev_hash == "0" * 64


def test_infrastructure_compliance_c1_c7_all_hold():
    compliance = evaluate_environment_compliance(_validate(_env()))
    assert compliance.compliant is True
    assert {c["id"] for c in compliance.conditions} == {f"C{n}" for n in range(1, 8)}
    assert all(c["status"] == "pass" for c in compliance.conditions)
    payload = compliance.to_dict()
    assert payload["standard"] == "INFRASTRUCTURE-001 §12"
    assert payload["compliant"] is True
    c3 = next(c for c in compliance.conditions if c["id"] == "C3")
    assert "note" in c3  # C3 carries the by-reference scoping note


def test_governing_compliance_conditions_materially_hold():
    # C4 (bounded/isolated), C5 (containment acyclic), C6 (provisioning binds RL-F2) hold on
    # the constructs that materially exercise them.
    env_compliance = {
        c["id"]: c["status"] for c in evaluate_environment_compliance(_validate(_env())).conditions
    }
    assert env_compliance["C4"] == "pass"  # Environment bounded/isolated
    assert env_compliance["C5"] == "pass"  # containment acyclic
    prov = make_provisioning_process("ucos.demo.prov", provisions=(RES,))
    prov_compliance = {
        c["id"]: c["status"] for c in evaluate_environment_compliance(_validate(prov)).conditions
    }
    assert prov_compliance["C6"] == "pass"  # provisioning binds RL-F2 by reference


def test_overall_certification_is_sound():
    cert = certify_construct(_validate(_env()), version="1.0.0")
    assert cert.certified is True  # decision + ledger + compliance


def test_certification_id_is_deterministic():
    a = certify_construct(_validate(_env()), version="1.0.0")
    b = certify_construct(_validate(_env()), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


def test_compliance_report_is_directly_constructible():
    report = EnvComplianceReport(target_id="x", conditions=())
    assert report.compliant is True  # vacuously (no failing condition)
    assert report.to_dict()["target_id"] == "x"


def test_non_compliant_construct_is_not_certified():
    # A technology-selecting node fails validation → gates fail-closed → NOT-CERTIFIED.
    techy = make_node("t", LOC, contains=("ENG-005:kubernetes:pod",))
    cert = certify_construct(_validate(techy), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_shared_ledger_chains_multiple_constructs():
    ledger = CertificationLedger()
    certify_construct(_validate(make_locality("t")), version="1.0.0", ledger=ledger)
    certify_construct(_validate(_env()), version="1.0.0", ledger=ledger)
    certify_construct(
        _validate(make_provisioning_process("t", provisions=(RES,))), version="1.0.0", ledger=ledger
    )
    assert len(ledger) == 3
    assert ledger.verify() is True


# --- per-gate negative coverage --------------------------------------------


def test_gate1_fails_on_orphan():
    assert (
        Gate1Architecture()
        .evaluate(_good_subject(blocking_failures=("traceability-rooted",)))
        .status
        is CriterionStatus.FAIL
    )


def test_gate2_fails_on_broken_substrate():
    assert (
        Gate2Dependencies()
        .evaluate(_good_subject(blocking_failures=("foundation-reuse-integrity",)))
        .status
        is CriterionStatus.FAIL
    )


def test_gate3_fails_on_structural_violation():
    assert (
        Gate3Coverage()
        .evaluate(
            _good_subject(
                blocking_failures=("infra-env-containment-acyclic",), counts={"failed": 1}
            )
        )
        .status
        is CriterionStatus.FAIL
    )


def test_gate4_fails_when_validation_not_accepted():
    assert (
        Gate4Validation()
        .evaluate(_good_subject(validation_accepted=False, validation_verdict="fail"))
        .status
        is CriterionStatus.FAIL
    )


def test_gate5_fails_on_broken_lineage():
    assert (
        Gate5Traceability()
        .evaluate(_good_subject(blocking_failures=("traceability-rooted",)))
        .status
        is CriterionStatus.FAIL
    )


def test_gate6_fails_when_evidence_absent():
    assert (
        Gate6Evidence().evaluate(_good_subject(evidence_present=False, evidence_sha256="")).status
        is CriterionStatus.FAIL
    )


def test_gate7_fails_when_disclosure_absent():
    assert (
        Gate7CertificationReady()
        .evaluate(_good_subject(blocking_failures=("provisional-state-disclosure",)))
        .status
        is CriterionStatus.FAIL
    )


def test_gate8_fails_on_blockers():
    assert (
        Gate8Readiness().evaluate(_good_subject(blocking_failures=("some-check",))).status
        is CriterionStatus.FAIL
    )


def test_gate9_fails_on_open_gap():
    assert (
        Gate9GapZero().evaluate(_good_subject(counts={"failed": 2})).status is CriterionStatus.FAIL
    )


def test_gate10_fails_when_prerequisites_open():
    assert (
        Gate10Completeness().evaluate(_good_subject(validation_accepted=False)).status
        is CriterionStatus.FAIL
    )


def test_all_gates_pass_on_good_subject():
    subject = _good_subject()
    for gate in cce_gates():
        assert gate.evaluate(subject).status is CriterionStatus.PASS, gate.criterion_id


def test_gate_reports_a_required_check_that_did_not_run():
    assert Gate2Dependencies().evaluate(_good_subject(checks_run=())).status is CriterionStatus.FAIL
