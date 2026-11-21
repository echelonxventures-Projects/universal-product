"""Tests for EC3-B13-U10 InfrastructureDependency construct (UIMM integration leaf)."""

from __future__ import annotations

import pytest
import pytest as _pytest

from infrastructure.capability import InfrastructureError
from infrastructure.integration import (
    DEPENDS_ON,
    InfrastructureDependency,
    make_dependency,
)
from infrastructure.integration_meta import InfrastructureState, ownership_is_disjoint


def _dep(**kw):
    base = dict(
        type_tag="ucos.infrastructure.dependency.compute-reuses-capability",
        source_ref="ENG-005:EC3-B13-U02:infrastructure.compute",
        target_ref="ENG-005:EC3-B13-U01:infrastructure.capability",
        source_index=2,
        target_index=1,
        basis="reuses",
    )
    base.update(kw)
    return make_dependency(
        base.pop("type_tag"),
        source_ref=base.pop("source_ref"),
        target_ref=base.pop("target_ref"),
        source_index=base.pop("source_index"),
        target_index=base.pop("target_index"),
        basis=base.pop("basis"),
        **base,
    )


class TestConstruction:
    def test_well_formed_dependency(self):
        d = _dep()
        assert d.meta_class == "InfrastructureDependency"
        assert d.relationship == DEPENDS_ON
        assert d.downward_only is True
        assert d.construct_id.startswith("UCOS-INFRA-DEPENDENCY-")
        assert len(d.value_digest) == 64

    def test_deterministic_identity(self):
        assert _dep().construct_id == _dep().construct_id
        assert _dep().value_digest == _dep().value_digest

    def test_untyped_rejected(self):
        with pytest.raises(InfrastructureError):
            _dep(type_tag="   ")

    def test_empty_reference_rejected(self):
        with pytest.raises(InfrastructureError):
            _dep(source_ref="")

    def test_upward_edge_rejected(self):
        # target index >= source index violates downward-only (WF-3).
        with pytest.raises(InfrastructureError):
            _dep(source_index=1, target_index=2)

    def test_self_edge_rejected(self):
        with pytest.raises(InfrastructureError):
            _dep(
                source_ref="ENG-005:EC3-B13-U02:infrastructure.compute",
                target_ref="ENG-005:EC3-B13-U02:infrastructure.compute",
                source_index=2,
                target_index=2,
            )

    def test_bad_basis_rejected(self):
        with pytest.raises(InfrastructureError):
            _dep(basis="mutates")

    def test_downward_only_invariant_enforced(self):
        with pytest.raises(InfrastructureError):
            InfrastructureDependency(
                type_tag="x",
                source_ref="ENG-005:a",
                target_ref="ENG-005:b",
                source_index=2,
                target_index=1,
                basis="reuses",
                downward_only=False,
            )

    def test_non_dependsOn_relationship_rejected(self):
        with pytest.raises(InfrastructureError):
            InfrastructureDependency(
                type_tag="x",
                source_ref="ENG-005:a",
                target_ref="ENG-005:b",
                source_index=2,
                target_index=1,
                basis="reuses",
                relationship="evaluates",
            )


class TestPredicates:
    def test_downward_and_acyclic(self):
        d = _dep()
        assert d.is_downward_only()
        assert d.is_founding_acyclic()
        assert d.is_dependency()

    def test_reference_only_and_non_mutating(self):
        d = _dep()
        assert d.is_reference_only()
        assert not d.mutates_endpoints()

    def test_non_constitutive(self):
        d = _dep()
        assert not d.confers_authority()
        assert not d.is_new_primitive()
        assert not d.redefines_foundation()
        assert not d.projects_completion()
        assert not d.selects_technology()
        assert not d.embeds_secret()

    def test_meta_relationships(self):
        assert _dep().meta_relationships() == ("dependsOn",)

    def test_declares_mandatory_attributes(self):
        assert _dep().declares_mandatory_attributes()

    def test_not_hosting_or_resource_or_facet(self):
        d = _dep()
        assert not d.is_hosting_structure()
        assert not d.is_resource()
        assert not d.is_evaluative_facet()


class TestLifecycle:
    def test_forward_transition(self):
        d = _dep()
        moved = d.transition(InfrastructureState.PROVISIONED)
        assert moved.state == InfrastructureState.PROVISIONED

    def test_backward_transition_rejected(self):
        d = _dep().transition(InfrastructureState.ACTIVE)
        with pytest.raises(InfrastructureError):
            d.transition(InfrastructureState.DEFINED)


class TestSerialization:
    def test_to_dict_shape(self):
        data = _dep().to_dict()
        for key in (
            "construct_id",
            "meta_class",
            "type_tag",
            "value_digest",
            "state",
            "source_ref",
            "target_ref",
            "relationship",
            "basis",
            "downward_only",
            "substrate_refs",
        ):
            assert key in data
        assert data["meta_class"] == "InfrastructureDependency"
        assert data["relationship"] == "dependsOn"


def test_the_dependency_guard_refuses_a_misdirected_or_mistyped_edge() -> None:
    """Every refusal in the dependency's post-init ladder, in order (WF-3, INFRASTRUCTURE-003).

    Downward-only is the acyclicity invariant; each of its three shapes — a missing index, an
    upward edge, a self-edge — was a branch nothing reached, and each is exactly the mistake a
    composition author would otherwise make in good faith.
    """

    with _pytest.raises(InfrastructureError, match="integer founding indices"):
        InfrastructureDependency(
            type_tag="IINT-BAD-01",
            source_ref="cluster-a",
            target_ref="cluster-b",
            relationship="dependsOn",
            basis="reuses",
            downward_only=True,
            source_index=None,
            target_index=None,
            state=InfrastructureState.DEFINED,
        )
    with _pytest.raises(InfrastructureError, match="not strictly downward"):
        InfrastructureDependency(
            type_tag="IINT-BAD-02",
            source_ref="cluster-a",
            target_ref="cluster-b",
            relationship="dependsOn",
            basis="reuses",
            downward_only=True,
            source_index=1,
            target_index=2,
            state=InfrastructureState.DEFINED,
        )
    with _pytest.raises(InfrastructureError, match="self-edge"):
        InfrastructureDependency(
            type_tag="IINT-BAD-03",
            source_ref="cluster-a",
            target_ref="cluster-a",
            relationship="dependsOn",
            basis="reuses",
            downward_only=True,
            source_index=2,
            target_index=1,
            state=InfrastructureState.DEFINED,
        )
    with _pytest.raises(InfrastructureError, match="InfrastructureState"):
        InfrastructureDependency(
            type_tag="IINT-BAD-04",
            source_ref="cluster-a",
            target_ref="cluster-b",
            relationship="dependsOn",
            basis="reuses",
            downward_only=True,
            source_index=2,
            target_index=1,
            state="DEFINED",  # type: ignore[arg-type]
        )


def test_transition_refuses_a_target_that_is_not_a_lifecycle_state() -> None:
    """Forward-only lifecycle is a type fact before it is an order fact (INFRASTRUCTURE-003 §3)."""

    edge = InfrastructureDependency(
        type_tag="IINT-T-01",
        source_ref="ENG-005:a",
        target_ref="ENG-005:b",
        source_index=2,
        target_index=1,
        basis="reuses",
    )
    with _pytest.raises(InfrastructureError, match="InfrastructureState"):
        edge.transition("ACTIVE")  # type: ignore[arg-type]


def test_duplicated_meta_class_ownership_is_reported_by_the_disjointness_check() -> None:
    """Two concerns claiming one meta-class: `ownership_is_disjoint` answers False.

    The shipped registry is disjoint, so the refusal arm is forced — a check that only
    ever answers True has not been shown to see a collision.
    """

    from infrastructure import integration_meta as meta

    concerns = list(meta.CONCERN_REGISTRY)
    twin = meta.ConcernUnit(
        concerns[1].unit,
        concerns[1].index,
        concerns[1].module,
        concerns[1].title,
        (concerns[0].meta_classes[0],),
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(meta, "CONCERN_REGISTRY", tuple([concerns[0], twin, *concerns[2:]]))
        assert ownership_is_disjoint() is False
