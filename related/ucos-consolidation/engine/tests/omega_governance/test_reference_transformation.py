"""Ω∞ reference layer — declared relationships between domains, and the absent arithmetic.

THE DESIGN DECISION UNDER TEST. A transformation between two domains is DECLARED first and computed
only if somebody supplied a computation. That separation is what lets the registry name the gap: a
relationship everyone agrees exists, which this repository cannot evaluate, appears in
``uncomputable()`` rather than as a missing edge or a silent identity.

REFUSALS ARE RESULTS HERE, not exceptions. ``apply`` returns a ``TransformationOutcome`` carrying a
rule id in every case, because a caller deciding what to do about an untransformable value needs to
know WHICH of the five ways it failed, and an exception collapses them into one.
"""

from __future__ import annotations

import pytest

from engine.omega_governance.reference.domain import Value
from engine.omega_governance.reference.transformation import (
    RULE_APPLIED,
    RULE_IDENTITY,
    RULE_NO_PATH,
    RULE_NOT_COMPUTABLE,
    RULE_WRONG_DOMAIN,
    Transformation,
    TransformationError,
    TransformationRegistry,
    default_transformations,
)


def _celsius_to_kelvin(value: Value) -> Value:
    return Value(
        domain="KELVIN", components=(value.components[0] + 273,), attributes=dict(value.attributes)
    )


def test_a_transformation_must_name_itself_its_endpoints_and_an_authority() -> None:
    for bad in (
        {"identifier": "  ", "source": "A", "target": "B", "authority": "X"},
        {"identifier": "T", "source": "  ", "target": "B", "authority": "X"},
        {"identifier": "T", "source": "A", "target": "  ", "authority": "X"},
        {"identifier": "T", "source": "A", "target": "B", "authority": "  "},
    ):
        with pytest.raises(TransformationError):
            Transformation(**bad)


def test_the_shipped_registry_declares_more_than_it_can_compute() -> None:
    """The countable gap. Two of the three declared relationships have no computation here, and the
    registry says so by name rather than by omitting the edge."""
    registry = default_transformations()
    declared = {transformation.identifier for transformation in registry.declared()}
    assert declared == {"Ω∞-X-ID-01", "Ω∞-X-TEMP-01", "Ω∞-X-TIME-01"}
    assert set(registry.uncomputable()) == {"Ω∞-X-TEMP-01", "Ω∞-X-TIME-01"}
    assert registry.computable("Ω∞-X-ID-01")
    assert not registry.computable("Ω∞-X-TIME-01")


def test_an_unknown_transformation_identifier_is_refused() -> None:
    with pytest.raises(TransformationError):
        default_transformations().resolve("Ω∞-X-NOWHERE")


def test_a_relationship_is_declared_from_primitives_with_no_edit_to_any_module() -> None:
    registry = TransformationRegistry()
    registry.declare(
        "T-C-K",
        "CELSIUS",
        "KELVIN",
        "TEST-AUTHORITY",
        description="An additive offset.",
        invertible=True,
        lossy=False,
        computation=_celsius_to_kelvin,
    )
    assert registry.computable("T-C-K")
    assert registry.between("CELSIUS", "KELVIN")


def test_applying_a_declared_and_computable_transformation_succeeds_and_says_why() -> None:
    registry = TransformationRegistry()
    registry.declare("T-C-K", "CELSIUS", "KELVIN", "TEST-AUTHORITY", computation=_celsius_to_kelvin)
    outcome = registry.apply(Value(domain="CELSIUS", components=(27,)), "KELVIN")
    assert outcome.applied
    assert outcome.rule == RULE_APPLIED
    assert outcome.value is not None
    assert outcome.value.components == (300,)
    assert outcome.path == ("T-C-K",)
    assert outcome.authorities == ("TEST-AUTHORITY",)


def test_transforming_a_value_into_its_own_domain_is_the_identity_and_is_named() -> None:
    """Not a no-op that silently returns the input: it carries its own rule id, so a caller reading
    an audit trail can tell an identity from a computation that happened to change nothing."""
    registry = default_transformations()
    value = Value(domain="TIME", components=(1,))
    outcome = registry.apply(value, "TIME")
    assert outcome.applied
    assert outcome.rule == RULE_IDENTITY
    assert outcome.value == value


def test_a_declared_but_uncomputable_transformation_refuses_with_its_own_rule() -> None:
    """This is the distinction the design exists for: NOT_COMPUTABLE means the relationship is real
    and this deployment cannot evaluate it. NO_PATH means nobody ever claimed it existed."""
    registry = TransformationRegistry()
    registry.declare("T-NO-CODE", "A", "B", "TEST-AUTHORITY")
    outcome = registry.apply(Value(domain="A", components=(1,)), "B")
    assert not outcome.applied
    assert outcome.rule == RULE_NOT_COMPUTABLE
    assert outcome.value is None


def test_an_undeclared_route_refuses_with_no_path_rather_than_not_computable() -> None:
    registry = TransformationRegistry()
    registry.declare("T-C-K", "CELSIUS", "KELVIN", "TEST-AUTHORITY", computation=_celsius_to_kelvin)
    outcome = registry.apply(Value(domain="CELSIUS", components=(27,)), "MASS")
    assert not outcome.applied
    assert outcome.rule == RULE_NO_PATH


def test_a_value_from_an_unrelated_domain_never_reaches_the_computation() -> None:
    """Route search starts at the VALUE's domain, so a Fahrenheit reading finds no declared route to
    Kelvin and the Celsius computation is never handed a value it does not accept."""
    calls: list[Value] = []

    def recording(value: Value) -> Value:
        calls.append(value)
        return Value(domain="KELVIN", components=value.components)

    registry = TransformationRegistry()
    registry.declare("T-C-K", "CELSIUS", "KELVIN", "TEST-AUTHORITY", computation=recording)
    outcome = registry.apply(Value(domain="FAHRENHEIT", components=(80,)), "KELVIN")
    assert not outcome.applied
    assert outcome.rule == RULE_NO_PATH
    assert calls == [], "the computation ran on a value from a domain it does not accept"


def test_a_computation_that_returns_the_wrong_domain_is_refused_as_a_result() -> None:
    """RULE_WRONG_DOMAIN, which was declared and exported while no code path could cite it.

    The distinction it carries is the one a caller most needs: a computation that is BROKEN, as
    against a relationship for which none was ever supplied. Both used to be indistinguishable —
    one arrived as a ``DomainError`` shared with schema validation, the other as an outcome.
    """
    registry = TransformationRegistry()
    registry.declare(
        "T-LIAR",
        "CELSIUS",
        "KELVIN",
        "TEST-AUTHORITY",
        computation=lambda value: Value(domain="MASS", components=value.components),
    )
    outcome = registry.apply(Value(domain="CELSIUS", components=(27,)), "KELVIN")
    assert not outcome.applied
    assert outcome.rule == RULE_WRONG_DOMAIN
    assert outcome.value is None
    assert "MASS" in outcome.reason and "KELVIN" in outcome.reason


def test_a_broken_step_stops_the_route_rather_than_cascading_through_it() -> None:
    """The later steps must never be handed a value from a domain they never declared they take."""
    seen: list[str] = []

    def liar(value: Value) -> Value:
        seen.append("T-1")
        return Value(domain="MASS")

    def downstream(value: Value) -> Value:
        seen.append("T-2")
        return Value(domain="C")

    registry = TransformationRegistry()
    registry.declare("T-1", "A", "B", "X", computation=liar)
    registry.declare("T-2", "B", "C", "X", computation=downstream)
    outcome = registry.apply(Value(domain="A"), "C")
    assert outcome.rule == RULE_WRONG_DOMAIN
    assert seen == ["T-1"], "the route continued past a step that misreported its output domain"


def test_a_path_is_found_breadth_first_over_declared_edges_only() -> None:
    registry = TransformationRegistry()
    registry.declare("T-1", "A", "B", "TEST-AUTHORITY", computation=lambda v: Value(domain="B"))
    registry.declare("T-2", "B", "C", "TEST-AUTHORITY", computation=lambda v: Value(domain="C"))
    assert tuple(step.identifier for step in registry.path("A", "C")) == ("T-1", "T-2")
    assert registry.path("C", "A") == ()


def test_a_multi_step_route_reports_every_authority_it_relied_on() -> None:
    """A transformed value's trustworthiness is the weakest authority on its route, so the route
    must carry all of them rather than only the last."""
    registry = TransformationRegistry()
    registry.declare(
        "T-1",
        "A",
        "B",
        "AUTHORITY-ONE",
        computation=lambda v: Value(domain="B", components=v.components),
    )
    registry.declare(
        "T-2",
        "B",
        "C",
        "AUTHORITY-TWO",
        computation=lambda v: Value(domain="C", components=v.components),
    )
    outcome = registry.apply(Value(domain="A", components=(1,)), "C")
    assert outcome.applied
    assert outcome.path == ("T-1", "T-2")
    assert set(outcome.authorities) == {"AUTHORITY-ONE", "AUTHORITY-TWO"}


def test_a_lossy_step_makes_the_whole_route_lossy() -> None:
    registry = TransformationRegistry()
    registry.declare("T-1", "A", "B", "X", lossy=False, computation=lambda v: Value(domain="B"))
    registry.declare("T-2", "B", "C", "X", lossy=True, computation=lambda v: Value(domain="C"))
    assert registry.apply(Value(domain="A"), "C").lossy


def test_redeclaring_an_identifier_is_refused() -> None:
    registry = TransformationRegistry()
    registry.declare("T-1", "A", "B", "X")
    with pytest.raises(TransformationError):
        registry.declare("T-1", "A", "C", "X")


def test_every_refusal_carries_a_rule_a_reader_can_look_up() -> None:
    """A refusal whose reason is prose alone cannot be counted, and a population that cannot be
    counted cannot be driven to zero."""
    registry = TransformationRegistry()
    registry.declare("T-NO-CODE", "A", "B", "TEST-AUTHORITY")
    for outcome in (
        registry.apply(Value(domain="A"), "B"),
        registry.apply(Value(domain="A"), "NOWHERE"),
    ):
        assert not outcome.applied
        assert outcome.rule in {RULE_NO_PATH, RULE_NOT_COMPUTABLE, RULE_WRONG_DOMAIN}
        assert outcome.reason.strip()


def test_the_report_names_the_declared_and_the_uncomputable_populations() -> None:
    report = default_transformations().report()
    assert report["count"] == 3
    assert report["uncomputable"] == ["Ω∞-X-TEMP-01", "Ω∞-X-TIME-01"]
    assert {entry["transformation"] for entry in report["transformations"]} == {
        "Ω∞-X-ID-01",
        "Ω∞-X-TEMP-01",
        "Ω∞-X-TIME-01",
    }


# ------------------------------------------------ the refusals, and the paths nothing had walked


def test_a_transformation_that_maps_a_domain_to_itself_is_refused() -> None:
    """Identity needs no declaration, and declaring it would put a no-op on every search path —
    where it would lengthen every route it appears in without converting anything."""
    with pytest.raises(TransformationError, match="maps .* to itself"):
        Transformation(
            identifier="T-SELF", source="KELVIN", target="KELVIN", authority="TEST-AUTHORITY"
        )


def test_a_registry_can_be_seeded_with_its_transformations() -> None:
    """Seeding and registering are one door. A seed that bypassed `register` would admit a pair
    the registration guards refuse, which is the shape those guards exist to close."""
    transformation = Transformation(
        identifier="T-SEED", source="A", target="B", authority="TEST-AUTHORITY"
    )
    registry = TransformationRegistry(seed=((transformation, None),))
    assert registry.path("A", "B") == (transformation,)


def test_a_second_transformation_over_one_edge_is_refused() -> None:
    """A second declaration would make the applicable authority and loss statement depend on
    registration order — two runs converting one value could cite different authorities."""
    registry = TransformationRegistry()
    registry.declare("T-FIRST", "A", "B", "TEST-AUTHORITY")
    with pytest.raises(TransformationError, match="would make .* depend on registration order"):
        registry.declare("T-SECOND", "A", "B", "ANOTHER-AUTHORITY")


def test_a_route_from_a_domain_to_itself_is_empty_rather_than_a_no_op_step() -> None:
    """An empty route is what "already there" looks like. A one-step identity route would put a
    conversion in the provenance of a value nothing converted."""
    assert default_transformations().path("KELVIN", "KELVIN") == ()


def test_the_search_does_not_revisit_a_domain_it_has_already_reached() -> None:
    """Breadth-first over declared edges, expanded in sorted order so two runs return the same
    route. Without the seen-set a cycle would make the search run forever."""
    registry = TransformationRegistry()
    registry.declare("T-AB", "A", "B", "TEST-AUTHORITY")
    registry.declare("T-BA", "B", "A", "TEST-AUTHORITY")
    registry.declare("T-BC", "B", "C", "TEST-AUTHORITY")
    route = registry.path("A", "C")
    assert [step.identifier for step in route] == ["T-AB", "T-BC"]


def test_an_outcome_carries_its_value_only_when_one_was_produced() -> None:
    """A record that always carried the key would make a refused conversion and a successful one
    holding nothing the same document."""
    registry = default_transformations()
    refused = registry.apply(Value(domain="CELSIUS"), "NOWHERE")
    assert not refused.applied
    assert "value" not in refused.as_record()
    identity = registry.apply(Value(domain="KELVIN", components=(1,)), "KELVIN")
    assert identity.applied
    assert identity.as_record()["value"]["domain"] == "KELVIN"
