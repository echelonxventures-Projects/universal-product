"""EC3-B11-U01 — Validation tests (EC-1 ValidationEngine PASS + V1…V5 + USL + VC).

Fail-branch coverage is achieved by projecting a valid service into a
:class:`ServiceValidationSubject` and flipping a single field (``dataclasses.replace``)
before running it through the CERTIFIED EC-1 ``ValidationEngine`` — every blocking
check's negative path is exercised deterministically.
"""

from __future__ import annotations

from dataclasses import replace

from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine
from service.service import make_service
from service.service_meta import ServiceKind, ServiceState
from service.service_traceability import build_traceability
from service.service_validation import (
    ServiceValidationSubject,
    service_checks,
    validate_service,
)

CAP_REF = "ENG-005:CAPABILITY:ucos.demo.capability"


def _service(**overrides):
    kwargs = dict(type_tag="ucos.demo.service", capability_ref=CAP_REF)
    kwargs.update(overrides)
    return make_service(kwargs.pop("type_tag"), kwargs.pop("capability_ref"), **kwargs)


def _trace(service):
    return build_traceability(service, unit="EC3-B11-U01", forward=(service.service_id,))


def _subject(**overrides):
    s = _service()
    subject = ServiceValidationSubject.from_service(s, _trace(s))
    return replace(subject, **overrides) if overrides else subject


def _fails(subject, check_id: str) -> bool:
    report = ValidationEngine(service_checks()).validate(subject)
    return report.verdict is Verdict.FAIL and check_id in {
        f.check_id for f in report.blocking_failures
    }


# --- positive path ----------------------------------------------------------


def test_validation_passes_and_is_accepted():
    s = _service()
    result = validate_service(s, _trace(s))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.decision.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    s = _service()
    result = validate_service(s, _trace(s))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(service_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_v1_v5_all_hold():
    s = _service()
    passed = {f.check_id: f.passed for f in validate_service(s, _trace(s)).report.findings}
    assert passed["meta-class-single"]  # V1
    assert passed["meta-relationships-closed"]  # V2
    assert passed["meta-constraints"]  # V3
    assert passed["founding-acyclic"]  # V4
    assert passed["lifecycle-valid"]  # V5


def test_usl_conformance_checks_present_and_pass():
    s = _service()
    passed = {f.check_id: f.passed for f in validate_service(s, _trace(s)).report.findings}
    for cid in (
        "service-typed",  # USL-03
        "service-identified-objectbound",  # USL-04/05
        "service-value-fidelity",  # ENG-003
        "service-classified",  # SXH-01
        "service-realizes-capability",  # SMR-01
        "foundation-reuse-integrity",  # USL-02 / VC-5
        "composition-by-reference",  # USL-09
        "execution-by-reference",  # USL-10
        "technology-independence",  # USL-15
        "non-constitutive",  # USL-15
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_subject_projection_is_deterministic():
    s = _service()
    assert ServiceValidationSubject.from_service(s, _trace(s)) == ServiceValidationSubject.from_service(
        s, _trace(s)
    )


def test_active_service_still_validates():
    s = _service(state=ServiceState.EXECUTABLE)
    assert validate_service(s, _trace(s)).accepted


def test_composite_and_orchestrated_services_validate():
    assert validate_service(_service(kind=ServiceKind.COMPOSITE), _trace(_service())).accepted
    assert validate_service(_service(kind=ServiceKind.ORCHESTRATED), _trace(_service())).accepted


# --- negative paths (one per blocking check) --------------------------------


def test_untyped_service_fails_typed_gate():
    assert _fails(_subject(type_tag=""), "service-typed")


def test_bad_identity_fails_identified_gate():
    assert _fails(_subject(target_id="NOT-A-SERVICE-id"), "service-identified-objectbound")


def test_missing_digest_fails_identified_gate():
    assert _fails(_subject(value_digest=""), "service-identified-objectbound")


def test_bad_digest_fails_value_fidelity_gate():
    assert _fails(_subject(value_digest="xyz"), "service-value-fidelity")


def test_bad_kind_fails_classified_gate():
    assert _fails(_subject(kind="Weird-Service"), "service-classified")


def test_missing_capability_fails_realizes_capability_gate():
    assert _fails(_subject(capability_ref="   "), "service-realizes-capability")


def test_wrong_meta_class_fails_meta_class_gate():
    assert _fails(_subject(meta_class="SMC-02"), "meta-class-single")


def test_relationship_outside_closure_fails_meta_relationships_gate():
    assert _fails(_subject(relationships=("SMR-99",)), "meta-relationships-closed")


def test_unresolved_reference_fails_meta_constraints_gate():
    assert _fails(_subject(references_resolve=False), "meta-constraints")


def test_empty_type_fails_meta_constraints_gate():
    assert _fails(_subject(type_tag=""), "meta-constraints")


def test_cyclic_founding_fails_founding_acyclic_gate():
    assert _fails(_subject(founding_acyclic=False), "founding-acyclic")


def test_bad_lifecycle_fails_lifecycle_gate():
    assert _fails(_subject(lifecycle_state="LIMBO"), "lifecycle-valid")


def test_redefining_foundation_fails_reuse_integrity_gate():
    assert _fails(_subject(redefines_foundation=True), "foundation-reuse-integrity")


def test_missing_substrate_fails_reuse_integrity_gate():
    assert _fails(_subject(substrate_refs=()), "foundation-reuse-integrity")


def test_missing_composition_reference_fails_composition_gate():
    assert _fails(_subject(composition_ref=""), "composition-by-reference")


def test_missing_behavior_reference_fails_execution_gate():
    assert _fails(_subject(behavior_ref=""), "execution-by-reference")


def test_technology_selection_fails_technology_independence_gate():
    assert _fails(_subject(selects_technology=True), "technology-independence")


def test_authority_conferral_fails_non_constitutive_gate():
    assert _fails(_subject(confers_authority=True), "non-constitutive")


def test_secret_embedding_fails_non_constitutive_gate():
    assert _fails(_subject(embeds_secret=True), "non-constitutive")


def test_absent_disclosure_fails_provisional_state_gate():
    assert _fails(_subject(disclosure={}), "provisional-state-disclosure")


def test_empty_lineage_fails_traceability_gate():
    assert _fails(_subject(provenance_chain=()), "traceability-rooted")


def test_unrooted_lineage_fails_traceability_gate():
    assert _fails(_subject(provenance_chain=("SERVICE-005", "SMC-01")), "traceability-rooted")


def test_lineage_without_anchor_fails_traceability_gate():
    assert _fails(_subject(provenance_chain=("SMC-01", "SERVICE-001")), "traceability-rooted")


def test_real_technology_bearing_service_is_rejected():
    s = _service(capability_ref="ENG-005:CAPABILITY:postgres.writer")
    result = validate_service(s, _trace(s))
    assert result.accepted is False
    assert "technology-independence" in {f.check_id for f in result.report.blocking_failures}
