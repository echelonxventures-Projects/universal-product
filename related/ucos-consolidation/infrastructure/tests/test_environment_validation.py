"""EC3-B13-U05 — Validation tests (EC-1 ValidationEngine PASS + WF + UIL + VC).

Fail-branch coverage is achieved by projecting a valid construct into an
:class:`EnvValidationSubject` and flipping a single field (``dataclasses.replace``) before
running it through the CERTIFIED EC-1 ``ValidationEngine`` — every blocking check's negative
path is exercised deterministically. A single suite validates all six concern-011
meta-classes via the per-construct ``applies_*`` flags.
"""

from __future__ import annotations

from dataclasses import replace

from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Verdict
from engine.validation.executor import ValidationEngine
from infrastructure.environment import (
    make_cluster,
    make_environment,
    make_isolation_boundary,
    make_locality,
    make_node,
    make_provisioning_process,
)
from infrastructure.environment_meta import InfrastructureState
from infrastructure.environment_traceability import build_traceability
from infrastructure.environment_validation import (
    EnvValidationSubject,
    environment_checks,
    validate_construct,
)

LOC = "ENG-005:INFRASTRUCTURE-011:locality.foundation"
BOUND = "ENG-005:INFRASTRUCTURE-011:isolation.boundary.a"
RES = "ENG-005:INFRASTRUCTURE-007:compute.resource"


def _trace(construct):
    return build_traceability(construct, unit="EC3-B13-U05", forward=(construct.construct_id,))


def _env():
    return make_environment("ucos.demo.env", BOUND, LOC, contains=(RES,))


def _subject(**overrides):
    e = _env()
    subject = EnvValidationSubject.from_construct(e, _trace(e), containment_acyclic=True)
    return replace(subject, **overrides) if overrides else subject


def _fails(subject, check_id: str) -> bool:
    report = ValidationEngine(environment_checks()).validate(subject)
    return report.verdict is Verdict.FAIL and check_id in {
        f.check_id for f in report.blocking_failures
    }


def _all_constructs():
    node = make_node("ucos.demo.node", LOC, contains=(RES,))
    cluster = make_cluster("ucos.demo.cluster", LOC, contains=(node.construct_id,))
    env = make_environment("ucos.demo.env", BOUND, LOC, contains=(cluster.construct_id,))
    return (
        make_locality("ucos.demo.locality"),
        make_isolation_boundary("ucos.demo.boundary"),
        node,
        cluster,
        env,
        make_provisioning_process("ucos.demo.prov", provisions=(RES,)),
    )


# --- positive path (all six constructs) -------------------------------------


def test_every_construct_validates_and_is_accepted():
    for construct in _all_constructs():
        result = validate_construct(construct, _trace(construct))
        assert result.report.verdict is Verdict.PASS, construct.meta_class  # VC-1
        assert result.accepted is True
        assert result.report.blocking_failures == ()


def test_every_check_is_blocking_and_passes_for_environment():
    e = _env()
    result = validate_construct(e, _trace(e))
    counts = result.report.counts()
    assert counts["failed"] == 0
    assert counts["total"] == len(environment_checks())
    assert counts["blocking_failed"] == 0


def test_meta_validity_wf_checks_hold_for_environment():
    e = _env()
    passed = {f.check_id: f.passed for f in validate_construct(e, _trace(e)).report.findings}
    assert passed["meta-class-single"]  # WF-1
    assert passed["meta-constraints"]  # WF-2
    assert passed["founding-acyclic"]  # WF-3
    assert passed["infra-env-containment-acyclic"]  # WF-3 / IENV-03 — governing
    assert passed["infra-env-bounded-isolated"]  # WF-4 / UIL-07 — governing
    assert passed["foundation-reuse-integrity"]  # WF-11
    assert passed["non-constitutive"]  # WF-12


def test_provisioning_process_binds_runtime_check_holds():
    p = make_provisioning_process("ucos.demo.prov", provisions=(RES,))
    passed = {f.check_id: f.passed for f in validate_construct(p, _trace(p)).report.findings}
    assert passed["infra-env-provisioning-binds-runtime"]  # WF-6 / UIL-10 — governing


def test_subject_projection_is_deterministic():
    e = _env()
    assert EnvValidationSubject.from_construct(e, _trace(e)) == EnvValidationSubject.from_construct(
        e, _trace(e)
    )


def test_active_construct_still_validates():
    e = make_environment("t", BOUND, LOC, contains=(RES,), state=InfrastructureState.ACTIVE)
    assert validate_construct(e, _trace(e)).accepted


# --- negative paths (one per blocking check) --------------------------------


def test_untyped_construct_fails_typed_gate():
    assert _fails(_subject(type_tag=""), "infra-env-typed")


def test_bad_identity_fails_identified_gate():
    assert _fails(_subject(target_id="NOT-AN-INFRA-id"), "infra-env-identified-objectbound")


def test_missing_digest_fails_identified_gate():
    assert _fails(_subject(value_digest=""), "infra-env-identified-objectbound")


def test_missing_mandatory_attribute_fails_identified_gate():
    assert _fails(_subject(declares_mandatory_attributes=False), "infra-env-identified-objectbound")


def test_bad_digest_fails_value_fidelity_gate():
    assert _fails(_subject(value_digest="xyz"), "infra-env-value-fidelity")


def test_wrong_meta_class_fails_meta_class_gate():
    assert _fails(_subject(meta_class="ComputeResource"), "meta-class-single")


def test_relationship_outside_closure_fails_meta_relationships_gate():
    assert _fails(_subject(relationships=("teleports",)), "meta-relationships-closed")


def test_unresolved_reference_fails_meta_constraints_gate():
    assert _fails(_subject(references_resolve=False), "meta-constraints")


def test_empty_type_fails_meta_constraints_gate():
    assert _fails(_subject(type_tag=""), "meta-constraints")


def test_cyclic_own_founding_fails_founding_acyclic_gate():
    assert _fails(_subject(founding_acyclic=False), "founding-acyclic")


def test_cyclic_containment_fails_containment_acyclic_gate():
    assert _fails(_subject(containment_acyclic=False), "infra-env-containment-acyclic")


def test_environment_without_boundary_fails_bounded_isolated_gate():
    assert _fails(
        _subject(applies_boundary=True, declares_single_boundary=False),
        "infra-env-bounded-isolated",
    )


def test_hosting_structure_without_locality_fails_located_gate():
    assert _fails(_subject(applies_locality=True, located_by_reference=False), "infra-env-located")


def test_empty_containment_fails_containment_by_reference_gate():
    assert _fails(
        _subject(applies_contains=True, contains_count=0), "infra-env-containment-by-reference"
    )


def test_empty_provisioning_fails_containment_by_reference_gate():
    assert _fails(
        _subject(applies_provisions=True, provisions_count=0),
        "infra-env-containment-by-reference",
    )


def test_unresolved_containment_reference_fails_containment_by_reference_gate():
    assert _fails(
        _subject(applies_contains=True, contains_count=1, references_resolve=False),
        "infra-env-containment-by-reference",
    )


def test_provisioning_without_workflow_fails_binds_runtime_gate():
    assert _fails(
        _subject(applies_workflow=True, binds_runtime_workflow=False),
        "infra-env-provisioning-binds-runtime",
    )


def test_resource_kind_fails_construct_kind_gate():
    assert _fails(_subject(is_resource=True), "infra-env-construct-kind")


def test_evaluative_facet_fails_construct_kind_gate():
    assert _fails(_subject(is_evaluative_facet=True), "infra-env-construct-kind")


def test_bad_lifecycle_fails_lifecycle_gate():
    assert _fails(_subject(lifecycle_state="LIMBO"), "lifecycle-valid")


def test_redefining_foundation_fails_reuse_integrity_gate():
    assert _fails(_subject(redefines_foundation=True), "foundation-reuse-integrity")


def test_new_primitive_fails_reuse_integrity_gate():
    assert _fails(_subject(is_new_primitive=True), "foundation-reuse-integrity")


def test_missing_substrate_fails_reuse_integrity_gate():
    assert _fails(_subject(substrate_refs=()), "foundation-reuse-integrity")


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
        _subject(provenance_chain=("INFRASTRUCTURE-011", "Environment")), "traceability-rooted"
    )


def test_lineage_without_anchor_fails_traceability_gate():
    assert _fails(
        _subject(provenance_chain=("Environment", "INFRASTRUCTURE-001")), "traceability-rooted"
    )


def test_real_technology_bearing_construct_is_rejected():
    n = make_node("t", LOC, contains=("ENG-005:terraform:module",))
    result = validate_construct(n, _trace(n))
    assert result.accepted is False
    assert "technology-independence" in {f.check_id for f in result.report.blocking_failures}


def test_non_applicable_flags_pass_vacuously_for_foundational_constructs():
    # A Locality applies neither boundary, workflow, locality, nor contains — those checks
    # pass vacuously (the single suite validates every meta-class).
    loc = make_locality("t")
    passed = {f.check_id: f.passed for f in validate_construct(loc, _trace(loc)).report.findings}
    assert passed["infra-env-bounded-isolated"]
    assert passed["infra-env-located"]
    assert passed["infra-env-containment-by-reference"]
    assert passed["infra-env-provisioning-binds-runtime"]


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), environment_checks())
