"""The Meta-Civilization Operating System facade: one kernel, no authority of its own."""

from __future__ import annotations

import pytest

from engine.civilization.errors import CompositionUnsatisfiedError
from engine.civilization.mcos import MetaCivilizationPlatform
from engine.kernel.kernel import MetaKernel


def _realizable() -> MetaCivilizationPlatform:
    platform = MetaCivilizationPlatform()
    platform.dimensions.register_dimension("Language-Axis")
    platform.dimensions.register_dimension("Currency-Axis")
    platform.composition.register_capability("ledger", dimensions=("Currency-Axis",))
    platform.composition.register_capability(
        "invoice", requires=("ledger",), dimensions=("Language-Axis", "Currency-Axis")
    )
    platform.generation.register_operating_system("GCOS")
    platform.generation.register_blueprint(
        "gcos-blueprint",
        operating_system="GCOS",
        dimensions=("Language-Axis", "Currency-Axis"),
        capabilities=("invoice",),
    )
    return platform


def test_all_three_components_share_one_kernel():
    platform = MetaCivilizationPlatform()
    assert platform.dimensions.kernel is platform.kernel
    assert platform.composition.kernel is platform.kernel
    assert platform.generation.kernel is platform.kernel


def test_the_platform_claims_no_authority():
    assert MetaCivilizationPlatform.authority == "NONE"
    assert MetaCivilizationPlatform().describe()["authority"] == "NONE"


def test_realize_generates_a_system_and_derives_its_plan():
    platform = _realizable()
    result, plan = platform.realize("gcos-blueprint")
    assert result.operating_system == "GCOS"
    assert [step.capability for step in plan.steps] == ["ledger", "invoice"]
    assert plan.context == ("Currency-Axis", "Language-Axis")
    assert platform.generation.verify_derivation(result) is True


def test_realize_honours_an_explicit_strategy():
    platform = _realizable()
    _result, plan = platform.realize("gcos-blueprint", strategy="parallel-waves")
    assert plan.strategy == "parallel-waves"
    assert {step.capability for step in plan.steps} == {"ledger", "invoice"}


def test_realize_carries_declared_policies_into_the_plan():
    platform = MetaCivilizationPlatform()
    platform.dimensions.register_dimension("Axis")
    platform.composition.register_capability("guarded", policies=("retention",))
    platform.generation.register_operating_system("HCOS")
    platform.generation.register_blueprint(
        "hcos-bp", operating_system="HCOS", capabilities=("guarded",)
    )
    _result, plan = platform.realize("hcos-bp")
    assert plan.policies == ("retention",)


def test_realize_refuses_a_blueprint_with_nothing_to_compose():
    platform = MetaCivilizationPlatform()
    platform.generation.register_operating_system("ECOS")
    platform.generation.register_blueprint("ecos-bp", operating_system="ECOS")
    with pytest.raises(CompositionUnsatisfiedError, match="no composition target"):
        platform.realize("ecos-bp")


def test_certification_is_derived_and_deterministic():
    platform = _realizable()
    platform.realize("gcos-blueprint")
    first = platform.certify()
    assert first["determination"] == "CERTIFIED"
    assert first["kernel_determination"] == "CERTIFIED"
    assert first["authority"] == "NONE"
    assert first["operating_systems"] == 1
    assert first == platform.certify()


def test_two_independent_platforms_are_byte_identical():
    assert MetaCivilizationPlatform().snapshot_hash() == MetaCivilizationPlatform().snapshot_hash()


def test_certification_reports_rejection_when_validation_fails(monkeypatch):
    platform = MetaCivilizationPlatform()
    monkeypatch.setattr(MetaKernel, "validate", lambda self: False)
    assert platform.validate() is False
    assert platform.certify()["determination"] == "REJECTED"


def test_describe_exposes_the_kernel_it_derives_from():
    described = MetaCivilizationPlatform().describe()
    assert described["derives_from"]["kernel_version"] == MetaKernel.version
    assert described["open_world"] is True
    assert described["upper_limit"] is None
    assert described["generation"]["finite_catalogue"] is False
    assert described["dimensions"]["closed_set"] is False
    assert described["composition"]["fixed_pipeline"] is False


def test_trace_resolves_anything_the_platform_registered():
    platform = _realizable()
    result, _plan = platform.realize("gcos-blueprint")
    trace = platform.trace(result.lineage[0])
    assert trace["identity"] == result.lineage[0]


def test_the_platform_accepts_an_existing_kernel():
    kernel = MetaKernel()
    platform = MetaCivilizationPlatform(kernel=kernel)
    assert platform.kernel is kernel
    assert platform.validate() is True
