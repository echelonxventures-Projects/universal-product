"""EC3-B13-U01 — Validation tests (EC-1 ValidationEngine PASS + WF + UIL + VC).

Fail-branch coverage is achieved by projecting a valid capability into a
:class:`CapabilityValidationSubject` and flipping a single field
(``dataclasses.replace``) before running it through the CERTIFIED EC-1
``ValidationEngine`` — every blocking check's negative path is exercised deterministically.
"""

from __future__ import annotations

from dataclasses import replace

from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine
from infrastructure.capability import make_infrastructure_capability
from infrastructure.capability_meta import InfrastructureCapabilityKind, InfrastructureState
from infrastructure.capability_traceability import build_traceability
from infrastructure.capability_validation import (
    CapabilityValidationSubject,
    capability_checks,
    validate_capability,
)

ENABLES = "ENG-005:RL-F2:runtime.execution"


def _capability(**overrides):
    kwargs = dict(type_tag="ucos.demo.capability", enables_ref=ENABLES)
    kwargs.update(overrides)
    return make_infrastructure_capability(
        kwargs.pop("type_tag"), kwargs.pop("enables_ref"), **kwargs
    )


def _trace(capability):
    return build_traceability(capability, unit="EC3-B13-U01", forward=(capability.capability_id,))


def _subject(**overrides):
    c = _capability()
    subject = CapabilityValidationSubject.from_capability(c, _trace(c))
    return replace(subject, **overrides) if overrides else subject


def _fails(subject, check_id: str) -> bool:
    report = ValidationEngine(capability_checks()).validate(subject)
    return report.verdict is Verdict.FAIL and check_id in {
        f.check_id for f in report.blocking_failures
    }


# --- positive path ----------------------------------------------------------


def test_validation_passes_and_is_accepted():
    c = _capability()
    result = validate_capability(c, _trace(c))
    assert result.report.verdict is Verdict.PASS  # VC-1
    assert result.accepted is True
    assert result.decision.accepted is True
    assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes():
    c = _capability()
    result = validate_capability(c, _trace(c))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(capability_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_wf_checks_hold():
    c = _capability()
    passed = {f.check_id: f.passed for f in validate_capability(c, _trace(c)).report.findings}
    assert passed["meta-class-single"]  # WF-1
    assert passed["hosting-by-reference"]  # WF-2
    assert passed["founding-acyclic"]  # WF-3
    assert passed["foundation-reuse-integrity"]  # WF-11
    assert passed["non-constitutive"]  # WF-12


def test_uil_conformance_checks_present_and_pass():
    c = _capability()
    passed = {f.check_id: f.passed for f in validate_capability(c, _trace(c)).report.findings}
    for cid in (
        "infra-capability-typed",  # UIL-03
        "infra-capability-identified-objectbound",  # UIL-04/05
        "infra-capability-value-fidelity",  # ENG-003
        "infra-capability-classified",  # INFRASTRUCTURE-006 §2
        "infra-capability-reuses-platform",  # ICAP-01 / UIL-06
        "infra-capability-enables-frozen-construct",  # ICAP-03
        "foundation-reuse-integrity",  # UIL-02 / VC-5
        "hosting-by-reference",  # UIL-06
        "behavior-by-reference",  # UIL-10
        "scaling-unbounded",  # UIL-13
        "technology-independence",  # UIL-12 / UIL-15
        "non-constitutive",  # UIL-14/15
        "provisional-state-disclosure",  # DE-05
        "traceability-rooted",  # No-Orphan
    ):
        assert passed[cid], cid


def test_subject_projection_is_deterministic():
    c = _capability()
    assert CapabilityValidationSubject.from_capability(
        c, _trace(c)
    ) == CapabilityValidationSubject.from_capability(c, _trace(c))


def test_active_capability_still_validates():
    c = _capability(state=InfrastructureState.ACTIVE)
    assert validate_capability(c, _trace(c)).accepted


def test_all_kinds_validate():
    for kind in InfrastructureCapabilityKind:
        c = _capability(kind=kind)
        assert validate_capability(c, _trace(c)).accepted, kind


# --- negative paths (one per blocking check) --------------------------------


def test_untyped_capability_fails_typed_gate():
    assert _fails(_subject(type_tag=""), "infra-capability-typed")


def test_bad_identity_fails_identified_gate():
    assert _fails(_subject(target_id="NOT-A-CAP-id"), "infra-capability-identified-objectbound")


def test_missing_digest_fails_identified_gate():
    assert _fails(_subject(value_digest=""), "infra-capability-identified-objectbound")


def test_missing_mandatory_attribute_fails_identified_gate():
    assert _fails(
        _subject(declares_mandatory_attributes=False),
        "infra-capability-identified-objectbound",
    )


def test_bad_digest_fails_value_fidelity_gate():
    assert _fails(_subject(value_digest="xyz"), "infra-capability-value-fidelity")


def test_bad_kind_fails_classified_gate():
    assert _fails(_subject(kind="Weird-Capability"), "infra-capability-classified")


def test_missing_platform_reuse_fails_reuses_platform_gate():
    assert _fails(_subject(reuses_platform_capability=False), "infra-capability-reuses-platform")
    assert _fails(_subject(capability_ref="   "), "infra-capability-reuses-platform")


def test_missing_enable_fails_enables_construct_gate():
    assert _fails(_subject(enables_by_reference=False), "infra-capability-enables-frozen-construct")
    assert _fails(_subject(enables_ref="   "), "infra-capability-enables-frozen-construct")


def test_wrong_meta_class_fails_meta_class_gate():
    assert _fails(_subject(meta_class="ComputeResource"), "meta-class-single")


def test_relationship_outside_closure_fails_meta_relationships_gate():
    assert _fails(_subject(relationships=("teleports",)), "meta-relationships-closed")


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


def test_new_primitive_fails_reuse_integrity_gate():
    assert _fails(_subject(is_new_primitive=True), "foundation-reuse-integrity")


def test_missing_substrate_fails_reuse_integrity_gate():
    assert _fails(_subject(substrate_refs=()), "foundation-reuse-integrity")


def test_missing_hosting_reference_fails_hosting_gate():
    assert _fails(_subject(enables_ref=""), "hosting-by-reference")
    assert _fails(_subject(capability_ref=""), "hosting-by-reference")


def test_missing_behavior_reference_fails_behavior_gate():
    assert _fails(_subject(behavior_ref=""), "behavior-by-reference")


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
        _subject(provenance_chain=("INFRASTRUCTURE-005", "InfrastructureCapability")),
        "traceability-rooted",
    )


def test_lineage_without_anchor_fails_traceability_gate():
    assert _fails(
        _subject(provenance_chain=("InfrastructureCapability", "INFRASTRUCTURE-001")),
        "traceability-rooted",
    )


def test_real_technology_bearing_capability_is_rejected():
    c = _capability(enables_ref="ENG-005:RL-F2:terraform.module")
    result = validate_capability(c, _trace(c))
    assert result.accepted is False
    assert "technology-independence" in {f.check_id for f in result.report.blocking_failures}


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), capability_checks())
