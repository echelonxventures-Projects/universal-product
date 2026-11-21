"""The Constitutional Generation Model: an open OS catalogue rooted at the Meta-Kernel."""

from __future__ import annotations

import pytest

from engine.civilization.errors import (
    BlueprintUnknownError,
    DerivationError,
    StratumOrderError,
    StratumUnknownError,
)
from engine.civilization.generation import (
    GENERATION_STRATA,
    ConstitutionalGenerator,
    GenerationResult,
)
from engine.civilization.metatypes import (
    DERIVES_FROM,
    GENERATION_NS,
    STRATUM_META_NS,
    STRATUM_ROLE,
)
from engine.civilization.seeding import seed_facets
from engine.kernel.kernel import MetaKernel


def _generator_with(os_key="Zetharic-OS", blueprint="zetharic-bp", **blueprint_kwargs):
    generator = ConstitutionalGenerator()
    generator.register_operating_system(os_key)
    generator.register_blueprint(blueprint, operating_system=os_key, **blueprint_kwargs)
    return generator


def test_the_ratified_generation_chain_is_seeded_in_order():
    generator = ConstitutionalGenerator()
    assert generator.strata() == tuple(key for key, _n, _a, _d in GENERATION_STRATA)
    assert generator.strata()[0] == "MetaKernelStratum"
    assert generator.strata()[-1] == "SolutionStratum"


def test_a_previously_unknown_operating_system_is_generated_by_registration():
    generator = _generator_with()
    assert generator.operating_systems() == ("Zetharic-OS",)
    result = generator.generate("zetharic-bp")
    assert result.operating_system == "Zetharic-OS"
    assert len(result.lineage) == len(generator.strata())
    assert generator.verify_derivation(result) is True


def test_every_generated_record_roots_at_the_kernel_reflective_root():
    generator = _generator_with()
    result = generator.generate("zetharic-bp")
    first = generator.kernel.registry.get(result.lineage[0])
    assert first.related(DERIVES_FROM) == (generator.kernel_root(),)
    second = generator.kernel.registry.get(result.lineage[1])
    assert second.related(DERIVES_FROM) == (result.lineage[0],)
    assert result.root == generator.kernel_root()


def test_generation_is_idempotent():
    generator = _generator_with()
    first = generator.generate("zetharic-bp")
    second = generator.generate("zetharic-bp")
    assert first == second
    assert first.derivation_hash() == second.derivation_hash()
    assert len(generator.generated()) == len(generator.strata())


def test_the_generation_chain_extends_by_registration_alone():
    generator = ConstitutionalGenerator()
    depth = len(generator.strata())
    generator.register_stratum("DeployedInstanceStratum", after=generator.strata()[-1])
    assert len(generator.strata()) == depth + 1
    assert generator.strata()[-1] == "DeployedInstanceStratum"


def test_a_stratum_cannot_be_ordered_after_an_unregistered_stratum():
    with pytest.raises(StratumUnknownError):
        ConstitutionalGenerator().register_stratum("Floating", after="Ghost")


def test_no_stratum_registered_means_nothing_generates():
    generator = ConstitutionalGenerator(seed=False)
    assert generator.strata() == ()
    generator.register_operating_system("Bare-OS")
    generator.register_blueprint("bare-bp", operating_system="Bare-OS")
    with pytest.raises(StratumOrderError, match="no generation stratum"):
        generator.generate("bare-bp")


def test_an_ambiguous_stratum_order_is_refused():
    generator = ConstitutionalGenerator(seed=False)
    generator.register_stratum("First")
    generator.register_stratum("AlsoFirst")
    with pytest.raises(StratumOrderError, match="ambiguous"):
        generator.strata()


def test_an_unreachable_stratum_predecessor_is_refused():
    generator = ConstitutionalGenerator()
    generator.kernel.register_metatype(
        "Orphaned",
        namespace=STRATUM_META_NS,
        attributes={"role": STRATUM_ROLE, "after": "NeverRegistered"},
    )
    with pytest.raises(StratumOrderError, match="unreachable"):
        generator.strata()


def test_a_blueprint_naming_an_unregistered_operating_system_is_refused():
    with pytest.raises(BlueprintUnknownError, match="unregistered constitutional"):
        ConstitutionalGenerator().register_blueprint("bp", operating_system="Unknown-OS")


def test_an_unregistered_blueprint_is_refused():
    with pytest.raises(BlueprintUnknownError, match="not registered"):
        ConstitutionalGenerator().blueprint("absent")


def test_blueprint_declarations_carry_dimensions_and_capabilities():
    generator = _generator_with(dimensions=("Axis-B", "Axis-A"), capabilities=("cap",))
    declared = generator.blueprint("zetharic-bp")
    assert declared.attributes["dimensions"] == ["Axis-A", "Axis-B"]
    assert declared.attributes["capabilities"] == ["cap"]
    assert [b.natural_key for b in generator.blueprints()] == ["zetharic-bp"]
    result = generator.generate("zetharic-bp")
    record = generator.kernel.registry.get(result.lineage[0])
    assert record.attributes["dimensions"] == ["Axis-A", "Axis-B"]


def test_generated_records_are_filterable_by_blueprint():
    generator = _generator_with()
    generator.register_operating_system("Other-OS")
    generator.register_blueprint("other-bp", operating_system="Other-OS")
    generator.generate("zetharic-bp")
    generator.generate("other-bp")
    assert len(generator.generated()) == 2 * len(generator.strata())
    assert len(generator.generated(blueprint="other-bp")) == len(generator.strata())


def test_a_broken_derivation_chain_is_refused():
    generator = _generator_with()
    result = generator.generate("zetharic-bp")
    tampered = GenerationResult(
        blueprint=result.blueprint,
        operating_system=result.operating_system,
        strata=result.strata,
        lineage=tuple(reversed(result.lineage)),
        root=result.root,
    )
    with pytest.raises(DerivationError, match="does not derive"):
        generator.verify_derivation(tampered)


def test_a_lineage_not_rooted_at_the_kernel_is_refused():
    generator = _generator_with()
    unrooted = GenerationResult(
        blueprint="zetharic-bp",
        operating_system="Zetharic-OS",
        strata=(),
        lineage=(),
        root="UMK-BOGUS-000000000000",
    )
    with pytest.raises(DerivationError, match="does not root"):
        generator.verify_derivation(unrooted)


def test_a_kernel_without_a_reflective_root_cannot_be_derived_from():
    kernel = MetaKernel(seed=False)
    seed_facets(kernel)
    generator = ConstitutionalGenerator(kernel=kernel, seed=False)
    with pytest.raises(DerivationError, match="no reflective root"):
        generator.kernel_root()


def test_a_generated_record_must_declare_exactly_one_derivation_edge():
    generator = ConstitutionalGenerator()
    with pytest.raises(Exception, match="admission denied"):
        generator.kernel.register_object(
            metatype="MetaKernelStratum",
            natural_key="bypass",
            namespace=GENERATION_NS,
        )


def test_validate_rejects_a_record_deriving_from_nothing_registered():
    generator = _generator_with()
    generator.generate("zetharic-bp")
    assert generator.validate() is True
    generator.kernel.register_object(
        metatype="MetaKernelStratum",
        natural_key="fabricated",
        namespace=GENERATION_NS,
        relationships=({"relation": DERIVES_FROM, "target": "UMK-NOWHERE-00000000"},),
    )
    assert generator.validate() is False


def test_validate_defers_to_the_kernel_audit_chain(monkeypatch):
    generator = _generator_with()
    generator.generate("zetharic-bp")
    monkeypatch.setattr(MetaKernel, "validate", lambda self: False)
    assert generator.validate() is False


def test_a_second_generator_over_the_same_kernel_rebinds_nothing():
    first = _generator_with()
    second = ConstitutionalGenerator(kernel=first.kernel)
    assert second.kernel is first.kernel
    names = first.kernel.governance.admission.constraint_names()
    assert names.count("generation-derivation-rooted") == 1
    assert second.strata() == first.strata()


def test_governance_ignores_objects_outside_the_generation_namespace():
    generator = ConstitutionalGenerator()
    generator.kernel.register_metatype("Elsewhere")
    obj = generator.kernel.register_object(
        metatype="Elsewhere", natural_key="e", namespace="umk.elsewhere"
    )
    assert obj.related(DERIVES_FROM) == ()


def test_describe_declares_an_open_catalogue():
    generator = _generator_with()
    described = generator.describe()
    assert described["finite_catalogue"] is False
    assert described["upper_limit"] is None
    assert described["operating_systems"] == ["Zetharic-OS"]
    assert described["depth"] == len(GENERATION_STRATA)


def test_result_serialisation_is_deterministic():
    generator = _generator_with()
    result = generator.generate("zetharic-bp")
    payload = result.to_dict()
    assert payload["depth"] == len(result.strata)
    assert payload["derivation_hash"] == result.derivation_hash()
    assert set(result.records()) == set(result.strata)
    assert result.to_dict() == result.to_dict()
