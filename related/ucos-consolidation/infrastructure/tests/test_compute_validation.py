"""EC3-B13-U02 — Validation tests (EC-1 ValidationEngine PASS + WF + UIL + VC).

Fail-branch coverage is achieved by projecting a valid compute resource into a
:class:`ComputeValidationSubject` and flipping a single field (``dataclasses.replace``)
before running it through the CERTIFIED EC-1 ``ValidationEngine`` — every blocking
check's negative path is exercised deterministically.
"""

from __future__ import annotations

from dataclasses import replace

from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine
from infrastructure.compute import make_compute_resource
from infrastructure.compute_meta import InfrastructureState
from infrastructure.compute_traceability import build_traceability
from infrastructure.compute_validation import (
    ComputeValidationSubject,
    compute_checks,
    validate_compute,
)

LOCALITY = "ENG-005:INFRASTRUCTURE-011:locality.foundation"


def _resource(**overrides):
    kwargs = dict(type_tag="ucos.demo.compute", locality_ref=LOCALITY)
    kwargs.update(overrides)
    return make_compute_resource(kwargs.pop("type_tag"), kwargs.pop("locality_ref"), **kwargs)


def _trace(resource):
    return build_traceability(resource, unit="EC3-B13-U02", forward=(resource.resource_id,))


def _subject(**overrides):
    r = _resource()
    subject = ComputeValidationSubject.from_resource(r, _trace(r))
    return replace(subject, **overrides) if overrides else subject


def _fails(subject, check_id: str) -> bool:
    report = ValidationEngine(compute_checks()).validate(subject)
    return report.verdict is Verdict.FAIL and check_id in {
        f.check_id for f in report.blocking_failures
    }


# --- positive path ----------------------------------------------------------


def test_validation_passes_and_is_accepted():
    r = _resource()
    result = validate_compute(r, _trace(r))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.decision.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    r = _resource()
    result = validate_compute(r, _trace(r))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(compute_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_wf_checks_hold():
    r = _resource()
    passed = {f.check_id: f.passed for f in validate_compute(r, _trace(r)).report.findings}
    assert passed["meta-class-single"]  # WF-1
    assert passed["infra-compute-hosts-execution-by-reference"]  # WF-2
    assert passed["founding-acyclic"]  # WF-3
    assert passed["infra-compute-declares-capacity-locality"]  # WF-5 — the governing rule
    assert passed["foundation-reuse-integrity"]  # WF-11
    assert passed["non-constitutive"]  # WF-12


def test_uil_conformance_checks_present_and_pass():
    r = _resource()
    passed = {f.check_id: f.passed for f in validate_compute(r, _trace(r)).report.findings}
    for cid in (
        "infra-compute-typed",  # UIL-03
        "infra-compute-identified-objectbound",  # UIL-04/05
        "infra-compute-value-fidelity",  # ENG-003
        "infra-compute-declares-capacity-locality",  # UIL-08 / WF-5
        "infra-compute-hosts-execution-by-reference",  # ICMP-01 / UIL-10
        "infra-compute-is-resource",  # WF-5
        "foundation-reuse-integrity",  # UIL-02 / VC-5
        "hosting-by-reference",  # UIL-10
        "scaling-unbounded",  # UIL-13
        "technology-independence",  # UIL-12 / UIL-15
        "non-constitutive",  # UIL-14/15
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_subject_projection_is_deterministic():
    r = _resource()
    assert ComputeValidationSubject.from_resource(
        r, _trace(r)
    ) == ComputeValidationSubject.from_resource(r, _trace(r))


def test_active_resource_still_validates():
    r = _resource(state=InfrastructureState.ACTIVE)
    assert validate_compute(r, _trace(r)).accepted


# --- negative paths (one per blocking check) --------------------------------


def test_untyped_resource_fails_typed_gate():
    assert _fails(_subject(type_tag=""), "infra-compute-typed")


def test_bad_identity_fails_identified_gate():
    assert _fails(_subject(target_id="NOT-A-COMPUTE-id"), "infra-compute-identified-objectbound")


def test_missing_digest_fails_identified_gate():
    assert _fails(_subject(value_digest=""), "infra-compute-identified-objectbound")


def test_missing_mandatory_attribute_fails_identified_gate():
    assert _fails(
        _subject(declares_mandatory_attributes=False),
        "infra-compute-identified-objectbound",
    )


def test_bad_digest_fails_value_fidelity_gate():
    assert _fails(_subject(value_digest="xyz"), "infra-compute-value-fidelity")


def test_negative_capacity_fails_capacity_locality_gate():
    assert _fails(_subject(capacity_amount=-1), "infra-compute-declares-capacity-locality")


def test_empty_capacity_unit_fails_capacity_locality_gate():
    assert _fails(_subject(capacity_unit="   "), "infra-compute-declares-capacity-locality")


def test_missing_locality_fails_capacity_locality_gate():
    assert _fails(
        _subject(located_by_reference=False, locality_ref="   "),
        "infra-compute-declares-capacity-locality",
    )


def test_undeclared_capacity_locality_fails_capacity_locality_gate():
    assert _fails(
        _subject(declares_capacity_and_locality=False),
        "infra-compute-declares-capacity-locality",
    )


def test_missing_execution_host_fails_hosts_execution_gate():
    assert _fails(
        _subject(hosts_execution_by_reference=False),
        "infra-compute-hosts-execution-by-reference",
    )
    assert _fails(_subject(execution_host_ref="   "), "infra-compute-hosts-execution-by-reference")


def test_wrong_meta_class_fails_meta_class_gate():
    assert _fails(_subject(meta_class="InfrastructureCapability"), "meta-class-single")


def test_relationship_outside_closure_fails_meta_relationships_gate():
    assert _fails(_subject(relationships=("teleports",)), "meta-relationships-closed")


def test_unresolved_reference_fails_meta_constraints_gate():
    assert _fails(_subject(references_resolve=False), "meta-constraints")


def test_empty_type_fails_meta_constraints_gate():
    assert _fails(_subject(type_tag=""), "meta-constraints")


def test_cyclic_founding_fails_founding_acyclic_gate():
    assert _fails(_subject(founding_acyclic=False), "founding-acyclic")


def test_non_resource_fails_resource_kind_gate():
    assert _fails(_subject(is_resource=False), "infra-compute-is-resource")


def test_evaluative_facet_fails_resource_kind_gate():
    assert _fails(_subject(is_evaluative_facet=True), "infra-compute-is-resource")


def test_bad_lifecycle_fails_lifecycle_gate():
    assert _fails(_subject(lifecycle_state="LIMBO"), "lifecycle-valid")


def test_redefining_foundation_fails_reuse_integrity_gate():
    assert _fails(_subject(redefines_foundation=True), "foundation-reuse-integrity")


def test_new_primitive_fails_reuse_integrity_gate():
    assert _fails(_subject(is_new_primitive=True), "foundation-reuse-integrity")


def test_missing_substrate_fails_reuse_integrity_gate():
    assert _fails(_subject(substrate_refs=()), "foundation-reuse-integrity")


def test_missing_hosting_reference_fails_hosting_gate():
    assert _fails(_subject(execution_host_ref=""), "hosting-by-reference")
    assert _fails(_subject(locality_ref=""), "hosting-by-reference")


def test_artificial_ceiling_fails_scaling_gate():
    assert _fails(_subject(declares_no_artificial_ceiling=False), "scaling-unbounded")


def test_technology_selection_fails_technology_independence_gate():
    assert _fails(_subject(selects_technology=True), "technology-independence")


def test_authority_conferral_fails_non_constitutive_gate():
    assert _fails(_subject(confers_authority=True), "non-constitutive")


def test_enforcement_fails_non_constitutive_gate():
    assert _fails(_subject(enacts_enforcement=True), "non-constitutive")


def test_secret_embedding_fails_non_constitutive_gate():
    assert _fails(_subject(embeds_secret=True), "non-constitutive")


def test_completion_projection_fails_non_constitutive_gate():
    assert _fails(_subject(projects_completion=True), "non-constitutive")


def test_absent_disclosure_fails_provisional_state_gate():
    assert _fails(_subject(disclosure={}), "provisional-state-disclosure")


def test_empty_lineage_fails_traceability_gate():
    assert _fails(_subject(provenance_chain=()), "traceability-rooted")


def test_unrooted_lineage_fails_traceability_gate():
    assert _fails(
        _subject(provenance_chain=("INFRASTRUCTURE-005", "ComputeResource")),
        "traceability-rooted",
    )


def test_lineage_without_anchor_fails_traceability_gate():
    assert _fails(
        _subject(provenance_chain=("ComputeResource", "INFRASTRUCTURE-001")),
        "traceability-rooted",
    )


def test_real_technology_bearing_resource_is_rejected():
    r = _resource(execution_host_ref="ENG-005:RL-F2:terraform.module")
    result = validate_compute(r, _trace(r))
    assert result.accepted is False
    assert "technology-independence" in {f.check_id for f in result.report.blocking_failures}


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), compute_checks())
