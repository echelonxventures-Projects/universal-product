"""Tests for EC3-B13-U09 Infrastructure Governance constructs (GovernanceFacet).

Covers:
- WF-1: single leaf meta-class (GovernanceFacet); mandatory attributes
- WF-10 / IGOV-01: record-only, non-enforcing (nonEnforcing=true fail-closed)
- IGOV-02: evaluates >=1 ENG-002 object by reference
- IGOV-05: reuse by reference (five construct reuse targets)
- UIL-15 / IGOV-06: embeds no secret material; selects no technology
- IGOV-04 / AUTH-06: confers no authority; grants no access
- UIL-03: typed; UIL-04/05: identified/object-bound
- Lifecycle: forward-only transition
"""

from __future__ import annotations

import pytest

from infrastructure.capability import InfrastructureError
from infrastructure.governance import (
    INFRA_GOVERNANCE_ID_FAMILY,
    GovernanceFacet,
    GovernanceFacetKind,
    make_governance_facet,
)
from infrastructure.governance_meta import InfrastructureState

_ALL_FACETS = (
    GovernanceFacetKind.CONFORMANCE,
    GovernanceFacetKind.LIFECYCLE,
    GovernanceFacetKind.POLICY,
    GovernanceFacetKind.GAP_REPORT,
    GovernanceFacetKind.CHANGE_RECORD,
)


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_is_typed_identified_and_evaluative(facet: GovernanceFacetKind) -> None:
    gf = make_governance_facet(f"test.governance.{facet.value}", facet)
    assert gf.construct_id.startswith(INFRA_GOVERNANCE_ID_FAMILY)
    assert gf.type_tag == f"test.governance.{facet.value}"
    assert gf.meta_class == "GovernanceFacet"
    assert gf.facet_value == facet.value
    assert gf.value_digest
    assert gf.references_resolve()
    assert gf.is_evaluative_facet()
    assert not gf.is_resource()


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_record_only_non_enforcing(facet: GovernanceFacetKind) -> None:
    gf = make_governance_facet(f"t.{facet.value}", facet)
    assert gf.non_enforcing is True
    assert not gf.enacts_enforcement()
    assert not gf.grants_access()
    assert gf.evaluates_object_bound()


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_reuses_by_reference(facet: GovernanceFacetKind) -> None:
    gf = make_governance_facet(f"t.{facet.value}", facet)
    # Every construct reuses >=1 frozen lower concern by reference (IGOV-05).
    assert len(gf.references) >= 1
    for ref in gf.references:
        assert isinstance(ref, str) and ref.strip()


def test_facet_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_governance_facet("", GovernanceFacetKind.CONFORMANCE)


def test_facet_rejects_bad_facet_kind() -> None:
    with pytest.raises(InfrastructureError):
        GovernanceFacet(type_tag="t", facet="conformance")  # type: ignore[arg-type]


def test_facet_rejects_empty_evaluates() -> None:
    with pytest.raises(InfrastructureError):
        GovernanceFacet(
            type_tag="t",
            facet=GovernanceFacetKind.CONFORMANCE,
            evaluates=(),
        )


def test_facet_rejects_enforcing() -> None:
    # WF-10 / IGOV-01 — non_enforcing must be True (fail-closed).
    with pytest.raises(InfrastructureError):
        GovernanceFacet(
            type_tag="t",
            facet=GovernanceFacetKind.POLICY,
            non_enforcing=False,
        )


def test_facet_rejects_bad_verdict() -> None:
    with pytest.raises(InfrastructureError):
        GovernanceFacet(
            type_tag="t",
            facet=GovernanceFacetKind.CONFORMANCE,
            evaluative_verdict="ENFORCED",
        )


def test_facet_rejects_bad_state() -> None:
    with pytest.raises(InfrastructureError):
        GovernanceFacet(type_tag="t", facet=GovernanceFacetKind.CONFORMANCE, state="ACTIVE")  # type: ignore[arg-type]


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_to_dict(facet: GovernanceFacetKind) -> None:
    gf = make_governance_facet(f"t.{facet.value}", facet)
    d = gf.to_dict()
    assert d["meta_class"] == "GovernanceFacet"
    assert d["facet"] == facet.value
    assert d["non_enforcing"] is True
    assert "evaluates" in d and "references" in d
    assert d["relationships"] == ["evaluates", "dependsOn"]


def test_forward_lifecycle_transition() -> None:
    gf = make_governance_facet("t.conf", GovernanceFacetKind.CONFORMANCE)
    assert gf.state == InfrastructureState.DEFINED
    gf2 = gf.transition(InfrastructureState.PROVISIONED)
    assert gf2.state == InfrastructureState.PROVISIONED
    assert gf.state == InfrastructureState.DEFINED  # frozen, unchanged


def test_lifecycle_rejects_backward_transition() -> None:
    gf = make_governance_facet(
        "t.chg", GovernanceFacetKind.CHANGE_RECORD, state=InfrastructureState.ACTIVE
    )
    with pytest.raises(InfrastructureError):
        gf.transition(InfrastructureState.DEFINED)


def test_all_facets_technology_neutral_and_non_constitutive() -> None:
    for facet in _ALL_FACETS:
        gf = make_governance_facet(f"t.{facet.value}", facet)
        assert not gf.selects_technology(), f"{facet.value} selects technology"
        assert not gf.embeds_secret(), f"{facet.value} embeds secret"
        assert not gf.confers_authority(), f"{facet.value} confers authority"
        assert not gf.grants_access(), f"{facet.value} grants access"
        assert not gf.redefines_foundation()
        assert not gf.is_new_primitive()
        assert not gf.projects_completion()


def test_secret_material_is_detected() -> None:
    # A construct whose evaluated ref embeds a secret marker must be flagged (UIL-15/IGOV-06).
    gf = GovernanceFacet(
        type_tag="t.leak",
        facet=GovernanceFacetKind.POLICY,
        evaluates=("ENG-005:ENG-002:password=hunter2",),
    )
    assert gf.embeds_secret()


def test_technology_selection_is_detected() -> None:
    gf = GovernanceFacet(
        type_tag="t.tech",
        facet=GovernanceFacetKind.POLICY,
        evaluates=("ENG-005:ENG-002:kubernetes.hosting",),
    )
    assert gf.selects_technology()


def test_a_governance_facet_refuses_a_blank_dependency_and_a_mistyped_transition() -> None:
    """The dependsOn ladder and INFRASTRUCTURE-003 §3 both answer before any ordering."""
    with pytest.raises(InfrastructureError, match="dependsOn"):
        make_governance_facet("t.blank-dep", GovernanceFacetKind.CONFORMANCE, depends_on=("   ",))
    facet = make_governance_facet(
        "t.trans", GovernanceFacetKind.CONFORMANCE, state=InfrastructureState.ACTIVE
    )
    with pytest.raises(InfrastructureError, match="INFRASTRUCTURE-003"):
        facet.transition("ACTIVE")  # type: ignore[arg-type]


def test_the_governance_factory_accepts_explicit_references_over_the_defaults() -> None:
    """The other side of the IGOV-05 defaulting arm: a caller may supply references."""
    facet = make_governance_facet(
        "t.explicit-refs", GovernanceFacetKind.CONFORMANCE, references=("ENG-005:custom",)
    )
    assert facet.references == ("ENG-005:custom",)
