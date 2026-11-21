"""UCOS-UNG-001 — the generation registries and the bootstrap that composes them.

Two populations, one discipline: order by declared identity rather than insertion, refuse a
redefinition that conflicts with itself, and report an unknown member rather than substituting
a default. The last of those is the one that matters most here — a generator that quietly
substituted a default template for a missing one would emit an artifact nobody declared, and
that artifact would then carry the authority of the declaration it claims to derive from.
"""

from __future__ import annotations

import json
from platform.foundation.services import ServiceRegistry
from platform.tests.universal_generator_helpers import StubTemplate, target
from platform.universal_generator.bootstrap import (
    GENERATION_SERVICE_NAME,
    bootstrap_nucleus_generator,
    generator_service_descriptor,
    register_nucleus_generator,
)
from platform.universal_generator.contracts import UNG_ID, ArtifactKind, GenerationTarget
from platform.universal_generator.errors import GenerationTargetError, GenerationTemplateError
from platform.universal_generator.generator import NucleusGenerator
from platform.universal_generator.registry import (
    DEFAULT_TARGETS_FILENAME,
    TargetRegister,
    TemplateRegistry,
    catalog_path,
    default_target_register,
    load_target_register,
)
from platform.universal_generator.templates import ContractTemplate, shipped_templates

import pytest


def target_document(*targets: GenerationTarget, register_id: str = "test.targets") -> dict:
    return {
        "register_id": register_id,
        "version": "1.0.0",
        "targets": [item.to_dict() for item in targets],
    }


# ---------------------------------------------------------------------------
# TemplateRegistry
# ---------------------------------------------------------------------------


def test_templates_are_ordered_by_declared_name_never_by_insertion():
    registry = TemplateRegistry([StubTemplate("zulu"), StubTemplate("alpha")])
    assert registry.names() == ("alpha", "zulu")
    assert [item.name for item in registry.ordered()] == ["alpha", "zulu"]


def test_registering_the_same_renderer_twice_is_idempotent():
    """Re-registering the same authority is not a conflict; it is the same answer twice."""
    registry = TemplateRegistry([StubTemplate("alpha", "first")])
    registry.add(StubTemplate("alpha", "second"))
    assert registry.count == 1
    assert registry.require("alpha").name == "alpha"


def test_a_second_renderer_claiming_a_registered_name_is_refused():
    """Two authorities for one obligation means the rendered artifact has no single author."""
    registry = TemplateRegistry([StubTemplate("contract-surface")])
    with pytest.raises(GenerationTemplateError) as exc:
        registry.add(ContractTemplate())
    message = str(exc.value)
    assert "contract-surface" in message
    assert "StubTemplate" in message and "ContractTemplate" in message


def test_only_an_artifact_template_may_be_registered():
    with pytest.raises(GenerationTemplateError):
        TemplateRegistry().add("contract-surface")  # type: ignore[arg-type]


def test_get_reports_an_unregistered_template_as_absent():
    assert TemplateRegistry().get("nobody") is None


def test_require_refuses_an_unknown_template_and_names_what_is_registered():
    registry = TemplateRegistry([StubTemplate("alpha")])
    with pytest.raises(GenerationTemplateError) as exc:
        registry.require("omega")
    message = str(exc.value)
    assert "omega" in message
    assert "alpha" in message


def test_extend_registers_every_template_supplied():
    registry = TemplateRegistry()
    registered = registry.extend([StubTemplate("a"), StubTemplate("b")])
    assert len(registered) == 2
    assert registry.count == 2


def test_the_registry_projection_describes_each_template_and_fingerprints_the_population():
    registry = TemplateRegistry([StubTemplate("alpha", kind=ArtifactKind.TESTS)])
    payload = registry.to_dict()
    assert payload["count"] == 1
    assert payload["templates"][0]["name"] == "alpha"
    assert payload["templates"][0]["kind"] == "tests"
    # The fingerprint is over the declared population, so insertion order cannot change it.
    forward = TemplateRegistry([StubTemplate("a"), StubTemplate("b")]).fingerprint()
    backward = TemplateRegistry([StubTemplate("b"), StubTemplate("a")]).fingerprint()
    assert forward == backward


# ---------------------------------------------------------------------------
# TargetRegister
# ---------------------------------------------------------------------------


def test_targets_are_ordered_by_identity_never_by_insertion():
    register = TargetRegister(targets=[target("GT-09"), target("GT-01")])
    assert register.ids() == ("GT-01", "GT-09")
    assert [item.target_id for item in register.ordered()] == ["GT-01", "GT-09"]


def test_declaring_the_same_target_twice_identically_is_idempotent():
    register = TargetRegister(targets=[target("GT-01")])
    register.add(target("GT-01"))
    assert register.count == 1


def test_a_target_redeclared_with_a_different_body_is_refused():
    register = TargetRegister(targets=[target("GT-01", destination="pkg/a.py")])
    with pytest.raises(GenerationTargetError) as exc:
        register.add(target("GT-01", destination="pkg/b.py"))
    assert "GT-01" in str(exc.value)


def test_only_a_generation_target_may_be_declared():
    with pytest.raises(GenerationTargetError):
        TargetRegister().add({"target_id": "GT-01"})  # type: ignore[arg-type]


def test_get_reports_an_undeclared_target_as_absent():
    assert TargetRegister().get("GT-99") is None


def test_require_returns_a_declared_target():
    declared = target("GT-01")
    assert TargetRegister(targets=[declared]).require("GT-01") is declared


def test_require_refuses_an_undeclared_target():
    with pytest.raises(GenerationTargetError) as exc:
        TargetRegister().require("GT-99")
    assert "GT-99" in str(exc.value)


def test_the_register_reports_every_template_its_targets_require_once():
    register = TargetRegister(
        targets=[
            target("GT-01", template="alpha"),
            target("GT-02", template="alpha", destination="pkg/b.py"),
            target("GT-03", template="beta", destination="pkg/c.py"),
        ]
    )
    assert register.templates() == ("alpha", "beta")


def test_a_register_document_round_trips_through_its_projection():
    original = TargetRegister(
        "test.targets",
        version="1.0.0",
        targets=[target("GT-01"), target("GT-02", destination="pkg/b.py")],
    )
    rebuilt = TargetRegister.from_document(original.to_dict())
    assert rebuilt.to_dict() == original.to_dict()
    assert rebuilt.fingerprint() == original.fingerprint()
    assert rebuilt.register_id == "test.targets"
    assert rebuilt.version == "1.0.0"


def test_a_register_document_that_is_not_a_mapping_is_refused():
    with pytest.raises(GenerationTargetError):
        TargetRegister.from_document([])  # type: ignore[arg-type]


@pytest.mark.parametrize("targets", ([], "GT-01", None))
def test_a_register_document_declaring_no_target_is_refused(targets):
    """An empty generation register would silently generate nothing at all."""
    with pytest.raises(GenerationTargetError):
        TargetRegister.from_document({"register_id": "x", "targets": targets})


# ---------------------------------------------------------------------------
# loading the declared catalogue
# ---------------------------------------------------------------------------


def test_the_packaged_catalogue_declares_the_generation_targets():
    register = default_target_register()
    assert register.count > 0
    assert catalog_path().name == DEFAULT_TARGETS_FILENAME
    assert catalog_path().is_file()
    # Every declared target names a template one of the shipped renderers provides.
    shipped = {item.name for item in shipped_templates()}
    assert set(register.templates()) <= shipped


def test_a_register_loaded_from_a_document_matches_one_built_in_memory(tmp_path):
    path = tmp_path / "targets.json"
    original = TargetRegister("test.targets", version="1.0.0", targets=[target("GT-01")])
    path.write_text(json.dumps(target_document(target("GT-01"))), encoding="utf-8")
    assert load_target_register(path).to_dict() == original.to_dict()


def test_an_absent_register_document_is_a_refusal_naming_the_path(tmp_path):
    missing = tmp_path / "absent.json"
    with pytest.raises(GenerationTargetError) as exc:
        load_target_register(missing)
    assert str(missing) in str(exc.value)


def test_a_malformed_register_document_is_a_refusal(tmp_path):
    path = tmp_path / "targets.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(GenerationTargetError):
        load_target_register(path)


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------


def test_bootstrapping_with_nothing_composes_the_packaged_declaration():
    generator = bootstrap_nucleus_generator()
    assert isinstance(generator, NucleusGenerator)
    assert generator.targets.to_dict() == default_target_register().to_dict()
    assert generator.templates.count == len(shipped_templates())


def test_bootstrapping_accepts_an_already_built_register():
    register = TargetRegister(targets=[target("GT-01", template="stub")])
    generator = bootstrap_nucleus_generator(register, templates=[StubTemplate("stub")])
    assert generator.targets.ids() == ("GT-01",)


def test_bootstrapping_accepts_a_path_to_a_declared_register(tmp_path):
    path = tmp_path / "targets.json"
    path.write_text(json.dumps(target_document(target("GT-01", template="stub"))), encoding="utf-8")
    generator = bootstrap_nucleus_generator(path, templates=[StubTemplate("stub")])
    assert generator.targets.ids() == ("GT-01",)


def test_the_published_service_descriptor_names_the_generation_contract():
    descriptor = generator_service_descriptor()
    assert descriptor.name == GENERATION_SERVICE_NAME
    assert descriptor.capabilities == (UNG_ID,)
    assert descriptor.contract.name == "generation.nucleus.plan"


def test_registration_is_lazy_and_resolves_to_the_composed_generator():
    registry = ServiceRegistry()
    descriptor = register_nucleus_generator(registry)
    assert descriptor.name == GENERATION_SERVICE_NAME
    resolved = registry.resolve(GENERATION_SERVICE_NAME)
    assert isinstance(resolved, NucleusGenerator)
    # Memoised: resolving twice yields the same composed instance, not a second generator.
    assert registry.resolve(GENERATION_SERVICE_NAME) is resolved


def test_registration_carries_an_explicit_specialisation_through_to_resolution():
    registry = ServiceRegistry()
    register_nucleus_generator(
        registry,
        targets=TargetRegister(targets=[target("GT-01", template="stub")]),
        templates=[StubTemplate("stub")],
    )
    assert registry.resolve(GENERATION_SERVICE_NAME).targets.ids() == ("GT-01",)
