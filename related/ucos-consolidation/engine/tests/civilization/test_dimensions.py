"""The Universal Dimension Model: open by registration, and refusing its own bounds."""

from __future__ import annotations

import pytest

from engine.civilization.dimensions import DimensionRegistry
from engine.civilization.errors import DimensionClosedError, DimensionUnknownError
from engine.civilization.metatypes import (
    DIMENSION_META_NS,
    DIMENSION_NS,
    FORBIDDEN_DIMENSION_KEYS,
    SPECIALIZES,
    dimension_facet_keys,
)
from engine.civilization.seeding import seed_facets
from engine.kernel.kernel import MetaKernel


def test_a_previously_unknown_dimension_is_admitted_by_registration():
    registry = DimensionRegistry()
    assert registry.dimensions() == ()
    declared = registry.register_dimension(
        "Glyphic-Resonance", description="An axis nobody has named."
    )
    assert registry.is_registered("Glyphic-Resonance") is True
    assert registry.dimension_keys() == ("Glyphic-Resonance",)
    assert declared.namespace == DIMENSION_NS
    # Every mandatory facet is attached by the registry itself, so no caller can omit one.
    assert declared.attributes["facets"] == list(dimension_facet_keys())


def test_no_dimension_may_declare_a_closed_value_set_or_any_bound():
    registry = DimensionRegistry()
    # Derived from the declared set, so a newly forbidden key is covered without a test edit.
    for key in FORBIDDEN_DIMENSION_KEYS:
        with pytest.raises(DimensionClosedError):
            registry.register_dimension(f"Bounded-{key}", attributes={key: [1, 2]})
    assert registry.dimensions() == ()


def test_the_bound_prohibition_is_directional_symmetric():
    """A floor is refused on the same ground as a ceiling (DEC-MCOS-07: any direction)."""
    registry = DimensionRegistry()
    for ceiling, floor in (("max_cardinality", "min_cardinality"), ("upper_bound", "lower_bound")):
        assert ceiling in FORBIDDEN_DIMENSION_KEYS
        assert floor in FORBIDDEN_DIMENSION_KEYS
        with pytest.raises(DimensionClosedError):
            registry.register_dimension(f"Floor-{floor}", attributes={floor: 3})
    assert registry.dimensions() == ()


def test_unlimited_specialization_and_generalization():
    registry = DimensionRegistry()
    registry.register_dimension("Axis")
    registry.register_dimension("Sub-Axis", specializes="Axis")
    registry.register_dimension("Sub-Sub-Axis", specializes="Sub-Axis")
    parent = registry.declaration("Axis")
    child = registry.declaration("Sub-Axis")
    assert child.related(SPECIALIZES) == (parent.identity,)
    assert registry.discover(specializes="Axis") == (child,)
    assert registry.discover(specializes="Sub-Axis")[0].natural_key == "Sub-Sub-Axis"


def test_specializing_an_unregistered_dimension_is_refused():
    registry = DimensionRegistry()
    with pytest.raises(DimensionUnknownError):
        registry.register_dimension("Orphan", specializes="Nonexistent")


def test_unknown_dimension_lookup_is_refused():
    registry = DimensionRegistry()
    with pytest.raises(DimensionUnknownError):
        registry.declaration("Nope")
    assert registry.is_registered("Nope") is False


def test_dimensions_compose_without_arity_limit():
    registry = DimensionRegistry()
    registry.register_dimension("Composite")
    registry.register_dimension("Part-A")
    registry.register_dimension("Part-B")
    registry.compose("Part-A", into="Composite")
    composed = registry.compose("Part-B", into="Composite")
    targets = composed.related("composes")
    assert len(targets) == 2
    assert registry.declaration("Part-A").identity in targets


def test_discovery_by_context_and_policy():
    registry = DimensionRegistry()
    registry.register_dimension("Bound", contexts=("frame-1",), policies=("policy-1",))
    registry.register_dimension("Free")
    assert [d.natural_key for d in registry.discover(context="frame-1")] == ["Bound"]
    assert [d.natural_key for d in registry.discover(policy="policy-1")] == ["Bound"]
    assert len(registry.discover()) == 2


def test_trace_and_describe_are_derived_from_the_kernel():
    registry = DimensionRegistry()
    registry.register_dimension("Traced")
    trace = registry.trace("Traced")
    assert trace["metatype"] == "Traced"
    described = registry.describe()
    assert described["closed_set"] is False
    assert described["upper_limit"] is None
    assert described["dimensions"] == ["Traced"]


def test_a_pre_existing_metatype_is_reused_not_redeclared():
    kernel = MetaKernel()
    kernel.register_metatype("Pre-Existing", namespace=DIMENSION_META_NS)
    registry = DimensionRegistry(kernel=kernel)
    declared = registry.register_dimension("Pre-Existing")
    assert declared.metatype == "Pre-Existing"
    assert registry.is_registered("Pre-Existing") is True


def test_a_second_registry_over_the_same_kernel_rebinds_nothing():
    first = DimensionRegistry()
    second = DimensionRegistry(kernel=first.kernel)
    assert second.kernel is first.kernel
    names = first.kernel.governance.admission.constraint_names()
    assert names.count("dimension-facets-complete") == 1
    assert second.validate() is True


def test_governance_ignores_objects_outside_the_dimension_namespace():
    registry = DimensionRegistry()
    kernel = registry.kernel
    kernel.register_metatype("Unrelated")
    obj = kernel.register_object(metatype="Unrelated", natural_key="x", namespace="umk.elsewhere")
    assert obj.namespace == "umk.elsewhere"
    assert registry.validate() is True


def _inject_incomplete_declaration(facets):
    """Admit a malformed declaration before the invariants are bound, then bind them."""
    kernel = MetaKernel()
    seed_facets(kernel)
    kernel.register_metatype("Malformed", namespace=DIMENSION_META_NS)
    kernel.register_object(
        metatype="Malformed",
        natural_key="Malformed",
        namespace=DIMENSION_NS,
        attributes={"facets": facets},
    )
    return DimensionRegistry(kernel=kernel)


def test_validate_rejects_a_declaration_missing_a_mandatory_facet():
    registry = _inject_incomplete_declaration(["discoverable"])
    assert registry.validate() is False


def test_validate_rejects_a_declaration_whose_facets_are_not_a_sequence():
    registry = _inject_incomplete_declaration("not-a-list")
    assert registry.validate() is False


def test_the_bound_invariants_refuse_a_malformed_declaration_at_admission():
    registry = DimensionRegistry()
    kernel = registry.kernel
    kernel.register_metatype("Late", namespace=DIMENSION_META_NS)
    with pytest.raises(Exception, match="admission denied"):
        kernel.register_object(
            metatype="Late",
            natural_key="Late",
            namespace=DIMENSION_NS,
            attributes={"facets": []},
        )


def test_the_bound_invariants_refuse_a_bound_at_admission():
    """The kernel-level constraint refuses a bound in either direction, not only a ceiling."""
    for label, attrs in (
        ("Ceiling", {"upper_bound": 3}),
        ("Floor", {"lower_bound": 3}),
    ):
        registry = DimensionRegistry()
        kernel = registry.kernel
        kernel.register_metatype(label, namespace=DIMENSION_META_NS)
        with pytest.raises(Exception, match="admission denied"):
            kernel.register_object(
                metatype=label,
                natural_key=label,
                namespace=DIMENSION_NS,
                attributes={"facets": list(dimension_facet_keys()), **attrs},
            )


def test_validate_defers_to_the_kernel_audit_chain(monkeypatch):
    registry = DimensionRegistry()
    registry.register_dimension("Fine")
    monkeypatch.setattr(MetaKernel, "validate", lambda self: False)
    assert registry.validate() is False
