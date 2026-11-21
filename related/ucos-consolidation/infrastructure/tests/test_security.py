"""Tests for EC3-B13-U08 Infrastructure Security constructs (SecurityFacet).

Covers:
- WF-1: single leaf meta-class (SecurityFacet); mandatory attributes
- WF-10 / ISEC-01/04: evaluative, non-enforcing (nonEnforcing=true fail-closed)
- ISEC-01: evaluates >=1 ENG-002 object by reference
- ISEC-02: reuse by reference (five facet reuse targets)
- ISEC-03 / RR-07: embeds no secret material
- ISEC-05 / UIL-15: selects no technology
- ISEC-06 / AUTH-06: confers no authority; grants no access
- UIL-03: typed; UIL-04/05: identified/object-bound
- Lifecycle: forward-only transition
"""

from __future__ import annotations

import pytest

from infrastructure.capability import InfrastructureError
from infrastructure.security import (
    INFRA_SECURITY_ID_FAMILY,
    SecurityFacet,
    SecurityFacetKind,
    make_security_facet,
)
from infrastructure.security_meta import InfrastructureState

_ALL_FACETS = (
    SecurityFacetKind.ISOLATION,
    SecurityFacetKind.AUTHENTICATION,
    SecurityFacetKind.AUTHORIZATION,
    SecurityFacetKind.CONFIDENTIALITY,
    SecurityFacetKind.INTEGRITY,
)


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_is_typed_identified_and_evaluative(facet: SecurityFacetKind) -> None:
    sf = make_security_facet(f"test.security.{facet.value}", facet)
    assert sf.construct_id.startswith(INFRA_SECURITY_ID_FAMILY)
    assert sf.type_tag == f"test.security.{facet.value}"
    assert sf.meta_class == "SecurityFacet"
    assert sf.facet_value == facet.value
    assert sf.value_digest
    assert sf.references_resolve()
    assert sf.is_evaluative_facet()
    assert not sf.is_resource()


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_evaluative_non_enforcing(facet: SecurityFacetKind) -> None:
    sf = make_security_facet(f"t.{facet.value}", facet)
    assert sf.non_enforcing is True
    assert not sf.enacts_enforcement()
    assert not sf.grants_access()
    assert sf.evaluates_object_bound()


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_reuses_by_reference(facet: SecurityFacetKind) -> None:
    sf = make_security_facet(f"t.{facet.value}", facet)
    # Every facet reuses >=1 frozen lower-security concern by reference (ISEC-02).
    assert len(sf.references) >= 1
    for ref in sf.references:
        assert isinstance(ref, str) and ref.strip()


def test_facet_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_security_facet("", SecurityFacetKind.ISOLATION)


def test_facet_rejects_bad_facet_kind() -> None:
    with pytest.raises(InfrastructureError):
        SecurityFacet(type_tag="t", facet="isolation")  # type: ignore[arg-type]


def test_facet_rejects_empty_evaluates() -> None:
    with pytest.raises(InfrastructureError):
        SecurityFacet(
            type_tag="t",
            facet=SecurityFacetKind.INTEGRITY,
            evaluates=(),
        )


def test_facet_rejects_enforcing() -> None:
    # WF-10 / ISEC-04 — non_enforcing must be True (fail-closed).
    with pytest.raises(InfrastructureError):
        SecurityFacet(
            type_tag="t",
            facet=SecurityFacetKind.AUTHORIZATION,
            non_enforcing=False,
        )


def test_facet_rejects_bad_verdict() -> None:
    with pytest.raises(InfrastructureError):
        SecurityFacet(
            type_tag="t",
            facet=SecurityFacetKind.ISOLATION,
            evaluative_verdict="ENFORCED",
        )


def test_facet_rejects_bad_state() -> None:
    with pytest.raises(InfrastructureError):
        SecurityFacet(type_tag="t", facet=SecurityFacetKind.ISOLATION, state="ACTIVE")  # type: ignore[arg-type]


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_to_dict(facet: SecurityFacetKind) -> None:
    sf = make_security_facet(f"t.{facet.value}", facet)
    d = sf.to_dict()
    assert d["meta_class"] == "SecurityFacet"
    assert d["facet"] == facet.value
    assert d["non_enforcing"] is True
    assert "evaluates" in d and "references" in d
    assert d["relationships"] == ["evaluates", "dependsOn"]


def test_forward_lifecycle_transition() -> None:
    sf = make_security_facet("t.iso", SecurityFacetKind.ISOLATION)
    assert sf.state == InfrastructureState.DEFINED
    sf2 = sf.transition(InfrastructureState.PROVISIONED)
    assert sf2.state == InfrastructureState.PROVISIONED
    assert sf.state == InfrastructureState.DEFINED  # frozen, unchanged


def test_lifecycle_rejects_backward_transition() -> None:
    sf = make_security_facet("t.int", SecurityFacetKind.INTEGRITY, state=InfrastructureState.ACTIVE)
    with pytest.raises(InfrastructureError):
        sf.transition(InfrastructureState.DEFINED)


def test_all_facets_technology_neutral_and_non_constitutive() -> None:
    for facet in _ALL_FACETS:
        sf = make_security_facet(f"t.{facet.value}", facet)
        assert not sf.selects_technology(), f"{facet.value} selects technology"
        assert not sf.embeds_secret(), f"{facet.value} embeds secret"
        assert not sf.confers_authority(), f"{facet.value} confers authority"
        assert not sf.grants_access(), f"{facet.value} grants access"
        assert not sf.redefines_foundation()
        assert not sf.is_new_primitive()
        assert not sf.projects_completion()


def test_secret_material_is_detected() -> None:
    # A facet whose evaluated ref embeds a secret marker must be flagged (ISEC-03/RR-07).
    sf = SecurityFacet(
        type_tag="t.leak",
        facet=SecurityFacetKind.CONFIDENTIALITY,
        evaluates=("ENG-005:ENG-002:password=hunter2",),
    )
    assert sf.embeds_secret()


def test_technology_selection_is_detected() -> None:
    sf = SecurityFacet(
        type_tag="t.tech",
        facet=SecurityFacetKind.AUTHENTICATION,
        evaluates=("ENG-005:ENG-002:kubernetes.hosting",),
    )
    assert sf.selects_technology()


def test_a_security_facet_refuses_a_blank_dependency_and_a_mistyped_transition() -> None:
    """The same two ladders, on the security construct class."""
    with pytest.raises(InfrastructureError, match="dependsOn"):
        make_security_facet("t.blank-dep", SecurityFacetKind.CONFIDENTIALITY, depends_on=("   ",))
    facet = make_security_facet(
        "t.trans", SecurityFacetKind.CONFIDENTIALITY, state=InfrastructureState.ACTIVE
    )
    with pytest.raises(InfrastructureError, match="INFRASTRUCTURE-003"):
        facet.transition("ACTIVE")  # type: ignore[arg-type]


def test_the_security_factory_accepts_explicit_references_over_the_defaults() -> None:
    """The other side of the ISEC-05 defaulting arm: a caller may supply references."""
    facet = make_security_facet(
        "t.explicit-refs", SecurityFacetKind.CONFIDENTIALITY, references=("ENG-005:custom",)
    )
    assert facet.references == ("ENG-005:custom",)
