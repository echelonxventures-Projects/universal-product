"""UCOS-UFC-001 — the thirteen constitutional probes, and every way each of them refuses.

The repository's own population passes all thirteen, which is what the Constitution is for and
also why the passing paths are the only ones the repository itself exercises. A probe whose
failure branch has never run is a gate nobody has seen close, so what is proven here is the
*refusals*: for every article, a capability that really violates it, measured by the real probe.

The specimens are genuine importable packages built for one test (see
``universal_conformance_helpers``). Patching a probe would have proven only that the patch
works; handing it a capability whose contract surface really is unversioned, whose registry
really has no ``require()``, or whose source really writes to disk, proves the probe.
"""

from __future__ import annotations

from dataclasses import replace
from platform.tests.universal_conformance_helpers import (
    CONFORMANT_SOURCE,
    context_for,
    declaration_document,
    declaration_for,
    register_for,
    specimen_package,
)
from platform.universal_foundation.conformance import (
    ARTIFACT_WRITE_CALLS,
    SHIPPED_PROBES,
    CapabilityDeclaration,
    FoundationConformanceError,
    ReplayDeclaration,
    SymbolRef,
    Verdict,
    probe_certifiable,
    probe_compatibility_declared,
    probe_composable,
    probe_contract_published,
    probe_evolution_additive,
    probe_fail_closed,
    probe_lifecycle_bootstrapped,
    probe_policy_declared,
    probe_provider_pluggable,
    probe_registry_deterministic,
    probe_runtime_invocable,
    probe_service_registered,
    probe_specialized,
)

import pytest


@pytest.fixture
def specimen(tmp_path):
    """A conformant specimen capability, and the tools to make it non-conformant."""

    class Specimen:
        def __init__(self, root):
            self.root = root
            self._counter = 0

        def build(self, extra: str = "", *, modules=None):
            """Materialise a specimen package; returns a context manager yielding its name."""
            self._counter += 1
            name = f"spec_{id(self)}_{self._counter}"
            payload = (
                {"specimen.py": CONFORMANT_SOURCE + extra} if modules is None else dict(modules)
            )
            return specimen_package(self.root, name, payload)

    return Specimen(tmp_path)


def measure(probe, declaration: CapabilityDeclaration, **register_kwargs):
    """Run one probe against one declaration with a register built around it."""
    register = register_for(declaration, **register_kwargs)
    return probe(declaration, context_for(register))


# ---------------------------------------------------------------------------
# the whole population, as the repository reads it
# ---------------------------------------------------------------------------


def test_a_conformant_specimen_passes_every_shipped_probe(specimen):
    """The baseline: if this ever fails, every refusal test below is measuring the fixture."""
    with specimen.build() as package:
        declaration = declaration_for(package)
        register = register_for(declaration)
        context = context_for(register)
        for gate, probe in SHIPPED_PROBES:
            verdict, _, findings = probe(declaration, context)
            assert verdict is Verdict.PASS, f"{gate}: {findings}"


# ---------------------------------------------------------------------------
# UFC-01 — contract published
# ---------------------------------------------------------------------------


def test_a_contract_surface_that_is_not_a_tuple_of_contracts_fails(specimen):
    with specimen.build("\nBROKEN_CONTRACTS = 'not a tuple'\n") as package:
        declaration = declaration_for(package, contracts=f"{package}.specimen:BROKEN_CONTRACTS")
        verdict, summary, findings = measure(probe_contract_published, declaration)
    assert verdict is Verdict.FAIL
    assert "not published" in summary
    assert any("non-empty tuple" in item for item in findings)


def test_a_published_entry_that_is_not_a_contract_ref_fails(specimen):
    with specimen.build("\nBROKEN_CONTRACTS = ('specimen.determine',)\n") as package:
        declaration = declaration_for(package, contracts=f"{package}.specimen:BROKEN_CONTRACTS")
        verdict, _, findings = measure(probe_contract_published, declaration)
    assert verdict is Verdict.FAIL
    assert any("not a ContractRef" in item for item in findings)


@pytest.mark.parametrize("bad", ("'1.0'", "'v1.0.0'", "'01.0.0'", "1.0"))
def test_a_version_that_is_not_semantic_fails(specimen, bad):
    with specimen.build(f"\nBROKEN_VERSION = {bad}\n") as package:
        declaration = declaration_for(package, version=f"{package}.specimen:BROKEN_VERSION")
        verdict, _, findings = measure(probe_contract_published, declaration)
    assert verdict is Verdict.FAIL
    assert any("semantic version" in item for item in findings)


# ---------------------------------------------------------------------------
# UFC-02 — service registered
# ---------------------------------------------------------------------------


def test_a_descriptor_that_is_not_a_service_descriptor_fails(specimen):
    with specimen.build("\ndef bad_descriptor():\n    return {'name': 'x'}\n") as package:
        declaration = declaration_for(
            package, service_descriptor=f"{package}.specimen:bad_descriptor"
        )
        verdict, summary, _ = measure(probe_service_registered, declaration)
    assert verdict is Verdict.FAIL
    assert "not a ServiceDescriptor" in summary


def test_a_published_service_name_that_contradicts_the_declaration_fails(specimen):
    """A descriptor naming a different service means callers bind to something else."""
    with specimen.build() as package:
        declaration = declaration_for(package, service_name="specimen.other")
        verdict, summary, findings = measure(probe_service_registered, declaration)
    assert verdict is Verdict.FAIL
    assert "does not match" in summary
    assert "specimen.other" in findings[0]


def test_a_registration_that_publishes_nothing_fails(specimen):
    with specimen.build("\ndef register_nothing(registry):\n    return None\n") as package:
        declaration = declaration_for(
            package, service_register=f"{package}.specimen:register_nothing"
        )
        verdict, summary, findings = measure(probe_service_registered, declaration)
    assert verdict is Verdict.FAIL
    assert "did not publish" in summary
    assert findings == ("specimen.service",)


def test_a_service_that_resolves_to_nothing_fails(specimen):
    extra = (
        "\n\ndef register_null(registry):\n"
        "    return registry.register(specimen_descriptor(), lambda: None)\n"
    )
    with specimen.build(extra) as package:
        declaration = declaration_for(package, service_register=f"{package}.specimen:register_null")
        verdict, summary, _ = measure(probe_service_registered, declaration)
    assert verdict is Verdict.FAIL
    assert "resolved to nothing" in summary


# ---------------------------------------------------------------------------
# UFC-03 — provider pluggable
# ---------------------------------------------------------------------------


def test_a_capability_declaring_no_extension_point_fails(specimen):
    with specimen.build() as package:
        declaration = declaration_for(package, extension_points=[])
        verdict, summary, findings = measure(probe_provider_pluggable, declaration)
    assert verdict is Verdict.FAIL
    assert "no extension point" in summary
    assert findings == ("UCOS-SPEC-001",)


def test_an_extension_point_that_is_not_a_class_fails(specimen):
    with specimen.build("\nNOT_A_CLASS = 42\n") as package:
        declaration = declaration_for(
            package, extension_points=[{"symbol": f"{package}.specimen:NOT_A_CLASS"}]
        )
        verdict, _, findings = measure(probe_provider_pluggable, declaration)
    assert verdict is Verdict.FAIL
    assert any("is not a class" in item for item in findings)


def test_an_extension_point_declared_abstract_with_no_abstract_method_fails(specimen):
    """A concrete class admits no new authority; it only offers itself."""
    with specimen.build("\n\nclass Concrete:\n    def provide(self):\n        return ''\n") as pkg:
        declaration = declaration_for(
            pkg,
            extension_points=[{"symbol": f"{pkg}.specimen:Concrete", "abstract": True}],
        )
        verdict, _, findings = measure(probe_provider_pluggable, declaration)
    assert verdict is Verdict.FAIL
    assert any("no abstract method" in item for item in findings)


def test_an_extension_point_missing_a_declared_method_fails(specimen):
    with specimen.build() as package:
        declaration = declaration_for(
            package,
            extension_points=[
                {
                    "symbol": f"{package}.specimen:SpecimenProvider",
                    "methods": ["provide", "withdraw"],
                }
            ],
        )
        verdict, _, findings = measure(probe_provider_pluggable, declaration)
    assert verdict is Verdict.FAIL
    assert any("withdraw()" in item for item in findings)


def test_a_non_abstract_extension_point_may_still_expose_its_methods(specimen):
    with specimen.build("\n\nclass Concrete:\n    def provide(self):\n        return ''\n") as pkg:
        declaration = declaration_for(
            pkg,
            extension_points=[
                {
                    "symbol": f"{pkg}.specimen:Concrete",
                    "abstract": False,
                    "methods": ["provide"],
                }
            ],
        )
        verdict, _, _ = measure(probe_provider_pluggable, declaration)
    assert verdict is Verdict.PASS


# ---------------------------------------------------------------------------
# UFC-04 — policy declared
# ---------------------------------------------------------------------------


def test_a_declared_catalogue_that_is_absent_fails(specimen):
    with specimen.build() as package:
        declaration = declaration_for(package, catalogs=["catalog/absent.json"], policy_free=False)
        verdict, summary, findings = measure(probe_policy_declared, declaration)
    assert verdict is Verdict.FAIL
    assert "not resolvable" in summary
    assert any("is absent" in item for item in findings)


def test_a_declared_catalogue_that_does_not_parse_fails(specimen, tmp_path):
    with specimen.build() as package:
        (tmp_path / package / "broken.json").write_text("{ not json", encoding="utf-8")
        declaration = declaration_for(package, catalogs=["broken.json"], policy_free=False)
        verdict, _, findings = measure(probe_policy_declared, declaration)
    assert verdict is Verdict.FAIL
    assert any("unreadable" in item for item in findings)


@pytest.mark.parametrize("payload", ("{}", "[]", '"a string"'))
def test_a_declared_catalogue_that_declares_nothing_fails(specimen, tmp_path, payload):
    """An empty policy document is configuration that configures nothing."""
    with specimen.build() as package:
        (tmp_path / package / "empty.json").write_text(payload, encoding="utf-8")
        declaration = declaration_for(package, catalogs=["empty.json"], policy_free=False)
        verdict, _, findings = measure(probe_policy_declared, declaration)
    assert verdict is Verdict.FAIL
    assert any("non-empty object" in item for item in findings)


def test_a_resolvable_catalogue_passes(specimen, tmp_path):
    with specimen.build() as package:
        (tmp_path / package / "policy.json").write_text('{"members": []}', encoding="utf-8")
        declaration = declaration_for(package, catalogs=["policy.json"], policy_free=False)
        verdict, summary, _ = measure(probe_policy_declared, declaration)
    assert verdict is Verdict.PASS
    assert "1 declared policy documents" in summary


# ---------------------------------------------------------------------------
# UFC-05 — registry deterministic
# ---------------------------------------------------------------------------


def test_a_capability_declaring_no_registry_fails(specimen):
    with specimen.build() as package:
        declaration = declaration_for(package, registries=[])
        verdict, summary, _ = measure(probe_registry_deterministic, declaration)
    assert verdict is Verdict.FAIL
    assert "no registry" in summary


def test_a_declared_registry_that_is_not_a_class_fails(specimen):
    with specimen.build("\nNOT_A_REGISTRY = []\n") as package:
        declaration = declaration_for(
            package,
            registries=[
                {
                    "symbol": f"{package}.specimen:NOT_A_REGISTRY",
                    "ordered": "ordered",
                    "require": "require",
                }
            ],
        )
        verdict, _, findings = measure(probe_registry_deterministic, declaration)
    assert verdict is Verdict.FAIL
    assert any("is not a class" in item for item in findings)


def test_a_registry_that_cannot_refuse_an_unknown_member_fails(specimen):
    """Without require() the registry substitutes rather than refuses."""
    with specimen.build() as package:
        declaration = declaration_for(
            package,
            registries=[
                {
                    "symbol": f"{package}.specimen:SpecimenRegistry",
                    "ordered": "ordered",
                    "require": "fetch_or_default",
                }
            ],
        )
        verdict, summary, findings = measure(probe_registry_deterministic, declaration)
    assert verdict is Verdict.FAIL
    assert "not deterministic and fail-closed" in summary
    assert any("fetch_or_default()" in item for item in findings)


# ---------------------------------------------------------------------------
# UFC-06 — runtime invocable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "overrides", ({"cli": None}, {"entry_point": ""}, {"cli": None, "entry_point": ""})
)
def test_a_capability_with_no_one_command_surface_fails(specimen, overrides):
    with specimen.build() as package:
        document = declaration_document(package)
        document.update(overrides)
        if document["cli"] is None:
            document.pop("cli")
        declaration = CapabilityDeclaration.from_document(document)
        verdict, summary, _ = measure(probe_runtime_invocable, declaration)
    assert verdict is Verdict.FAIL
    assert "no one-command runtime surface" in summary


def test_a_declared_cli_that_is_not_callable_fails(specimen):
    with specimen.build("\nNOT_CALLABLE = 'main'\n") as package:
        declaration = declaration_for(package, cli=f"{package}.specimen:NOT_CALLABLE")
        register = register_for(declaration)
        verdict, _, findings = probe_runtime_invocable(declaration, context_for(register))
    assert verdict is Verdict.FAIL
    assert any("not callable" in item for item in findings)


def test_an_entry_point_the_build_does_not_declare_fails(specimen):
    """A runtime surface the build never publishes is one nobody can reach."""
    with specimen.build() as package:
        declaration = declaration_for(package)
        register = register_for(declaration)
        verdict, summary, findings = probe_runtime_invocable(
            declaration, context_for(register, console_scripts={})
        )
    assert verdict is Verdict.FAIL
    assert "not invocable" in summary
    assert any("is not declared in the build" in item for item in findings)


def test_an_entry_point_that_resolves_elsewhere_fails(specimen):
    with specimen.build() as package:
        declaration = declaration_for(package)
        register = register_for(declaration)
        verdict, _, findings = probe_runtime_invocable(
            declaration,
            context_for(register, console_scripts={"ucos-specimen": "somewhere.else:main"}),
        )
    assert verdict is Verdict.FAIL
    assert any("somewhere.else:main" in item for item in findings)


# ---------------------------------------------------------------------------
# UFC-07 — lifecycle bootstrapped
# ---------------------------------------------------------------------------


def test_a_bootstrap_that_is_not_callable_fails(specimen):
    with specimen.build("\nNOT_CALLABLE = 1\n") as package:
        declaration = declaration_for(package, bootstrap=f"{package}.specimen:NOT_CALLABLE")
        verdict, summary, findings = measure(probe_lifecycle_bootstrapped, declaration)
    assert verdict is Verdict.FAIL
    assert "not bootstrap-only" in summary
    assert any("not callable" in item for item in findings)


def test_a_module_acting_at_import_time_fails(specimen):
    """A module that acts on import can never be composed twice, so it cannot be replayed."""
    impure = CONFORMANT_SOURCE + "\nimport json\n\nLOADED = json.loads('{}')\n"
    with specimen.build(modules={"specimen.py": impure}) as package:
        declaration = declaration_for(package)
        verdict, _, findings = measure(probe_lifecycle_bootstrapped, declaration)
    assert verdict is Verdict.FAIL
    assert any("at import time" in item and "loads" in item for item in findings)


# ---------------------------------------------------------------------------
# UFC-08 — compatibility declared
# ---------------------------------------------------------------------------


def test_a_non_semantic_declared_version_is_incompatible(specimen):
    with specimen.build("\nBROKEN_VERSION = 'one'\n") as package:
        declaration = declaration_for(package, version=f"{package}.specimen:BROKEN_VERSION")
        verdict, summary, findings = measure(probe_compatibility_declared, declaration)
    assert verdict is Verdict.FAIL
    assert "inconsistent" in summary
    assert any("not semantic" in item for item in findings)


def test_a_contract_carrying_a_second_version_is_incompatible(specimen):
    """One declared version governs the whole surface, or a consumer cannot bind to it."""
    extra = (
        "\nSPLIT_CONTRACTS: tuple[ContractRef, ...] = (\n"
        "    ContractRef('specimen.determine', '1.0.0'),\n"
        "    ContractRef('specimen.describe', '2.0.0'),\n"
        ")\n"
    )
    with specimen.build(extra) as package:
        declaration = declaration_for(package, contracts=f"{package}.specimen:SPLIT_CONTRACTS")
        verdict, _, findings = measure(probe_compatibility_declared, declaration)
    assert verdict is Verdict.FAIL
    assert any("carries 2.0.0" in item for item in findings)


def test_a_service_contract_at_a_different_version_is_incompatible(specimen):
    extra = (
        "\n\ndef drifted_descriptor():\n"
        "    return ServiceDescriptor(\n"
        "        name=SERVICE_NAME,\n"
        "        contract=platform_contract('specimen.determine', '9.9.9', 'Drifted.'),\n"
        "        capabilities=(SPECIMEN_ID,),\n"
        "        description='Specimen',\n"
        "    )\n"
    )
    with specimen.build(extra) as package:
        declaration = declaration_for(
            package, service_descriptor=f"{package}.specimen:drifted_descriptor"
        )
        verdict, _, findings = measure(probe_compatibility_declared, declaration)
    assert verdict is Verdict.FAIL
    assert any("service contract carries 9.9.9" in item for item in findings)


# ---------------------------------------------------------------------------
# UFC-09 — evolution additive
# ---------------------------------------------------------------------------


def test_an_identity_that_contradicts_the_declaration_fails(specimen):
    with specimen.build() as package:
        declaration = declaration_for(package, capability_id="UCOS-SPEC-999")
        verdict, summary, findings = measure(probe_evolution_additive, declaration)
    assert verdict is Verdict.FAIL
    assert "not evolution-additive" in summary
    assert any("UCOS-SPEC-999" in item for item in findings)


def test_a_governing_module_that_enumerates_the_capability_fails(specimen, tmp_path):
    """Enumeration is what makes adding a capability require editing its governor."""
    governor = tmp_path / "specimen_governor.py"
    governor.write_text('"""A governor."""\n\nKNOWN = ("UCOS-SPEC-001",)\n', encoding="utf-8")
    with specimen.build() as package:
        declaration = declaration_for(package)
        verdict, _, findings = measure(
            probe_evolution_additive,
            declaration,
            governing_modules=("specimen_governor",),
        )
    assert verdict is Verdict.FAIL
    assert any("enumerates this capability" in item for item in findings)


def test_a_register_declaring_no_governing_module_cannot_measure_ufc_09(specimen):
    """Unmeasurable is a refusal, not a pass: UFC-09 has nothing to look at."""
    with specimen.build() as package:
        declaration = declaration_for(package)
        with pytest.raises(FoundationConformanceError) as exc:
            measure(probe_evolution_additive, declaration, governing_modules=())
    assert "cannot be measured" in str(exc.value)


def test_a_governing_module_that_cannot_be_imported_is_a_refusal(specimen):
    with specimen.build() as package:
        declaration = declaration_for(package)
        with pytest.raises(FoundationConformanceError) as exc:
            measure(
                probe_evolution_additive,
                declaration,
                governing_modules=("module.that.does.not.exist",),
            )
    assert "could not be imported" in str(exc.value)


def test_a_capability_may_declare_its_own_identity_in_its_own_module(specimen):
    """A self-declared identity lives somewhere; that somewhere is not enumeration."""
    with specimen.build() as package:
        declaration = declaration_for(package)
        verdict, summary, _ = measure(
            probe_evolution_additive,
            declaration,
            governing_modules=(f"{package}.specimen",),
        )
    assert verdict is Verdict.PASS
    assert "self-declared" in summary


# ---------------------------------------------------------------------------
# UFC-10 — fail closed
# ---------------------------------------------------------------------------


def test_an_error_base_that_is_not_a_platform_error_fails(specimen):
    with specimen.build("\n\nclass Rogue(Exception):\n    pass\n") as package:
        declaration = declaration_for(package, errors_base=f"{package}.specimen:Rogue")
        verdict, summary, findings = measure(probe_fail_closed, declaration)
    assert verdict is Verdict.FAIL
    assert "not fail-closed" in summary
    assert any("PlatformError subclass" in item for item in findings)


def test_a_typed_error_with_no_stable_code_fails(specimen):
    with specimen.build('\n\nclass Uncoded(SpecimenError):\n    code = "  "\n') as package:
        declaration = declaration_for(package)
        verdict, _, findings = measure(probe_fail_closed, declaration)
    assert verdict is Verdict.FAIL
    assert any("no stable error code" in item for item in findings)


def test_two_errors_sharing_one_code_fail(specimen):
    """A reused code means two different refusals are indistinguishable to a caller."""
    extra = '\n\nclass Twin(SpecimenError):\n    code = "EC2-SPEC-REGISTRY-001"\n'
    with specimen.build(extra) as package:
        declaration = declaration_for(package)
        verdict, _, findings = measure(probe_fail_closed, declaration)
    assert verdict is Verdict.FAIL
    assert any("reuses the code" in item for item in findings)


def test_a_module_declaring_no_typed_error_fails(specimen, tmp_path):
    empty = '"""No errors here."""\n\nfrom __future__ import annotations\n\nVALUE = 1\n'
    with specimen.build(
        modules={"specimen.py": CONFORMANT_SOURCE, "empty_errors.py": empty}
    ) as package:
        declaration = declaration_for(
            package,
            errors_module=f"{package}.empty_errors",
            errors_base=f"{package}.specimen:SpecimenError",
        )
        verdict, _, findings = measure(probe_fail_closed, declaration)
    assert verdict is Verdict.FAIL
    assert any("declares no typed error" in item for item in findings)


# ---------------------------------------------------------------------------
# UFC-11 — certifiable
# ---------------------------------------------------------------------------


def test_a_build_that_is_not_callable_fails(specimen):
    with specimen.build("\nNOT_CALLABLE = 2\n") as package:
        declaration = declaration_for(package, build=f"{package}.specimen:NOT_CALLABLE")
        verdict, summary, _ = measure(probe_certifiable, declaration)
    assert verdict is Verdict.FAIL
    assert "not callable" in summary


def test_a_build_whose_product_is_not_content_addressed_fails(specimen):
    with specimen.build("\n\ndef build_plain():\n    return object()\n") as package:
        declaration = declaration_for(package, build=f"{package}.specimen:build_plain")
        verdict, summary, findings = measure(probe_certifiable, declaration)
    assert verdict is Verdict.FAIL
    assert "not content-addressed" in summary
    assert len(findings) == 2  # both builds are reported, not just the first


def test_an_empty_fingerprint_fails(specimen):
    extra = (
        "\n\nclass Blank:\n    def fingerprint(self):\n        return ''\n"
        "\n\ndef build_blank():\n    return Blank()\n"
    )
    with specimen.build(extra) as package:
        declaration = declaration_for(package, build=f"{package}.specimen:build_blank")
        verdict, summary, _ = measure(probe_certifiable, declaration)
    assert verdict is Verdict.FAIL
    assert "fingerprint is empty" in summary


def test_two_builds_that_disagree_fail(specimen):
    """Two independent builds must agree, or nothing built is certifiable."""
    extra = (
        "\n\n_COUNTER = [0]\n"
        "\n\nclass Drifting:\n"
        "    def __init__(self, value):\n        self._value = value\n"
        "    def fingerprint(self):\n        return f'fp-{self._value}'\n"
        "\n\ndef build_drifting():\n"
        "    _COUNTER[0] += 1\n    return Drifting(_COUNTER[0])\n"
    )
    with specimen.build(extra) as package:
        declaration = declaration_for(package, build=f"{package}.specimen:build_drifting")
        verdict, summary, findings = measure(probe_certifiable, declaration)
    assert verdict is Verdict.FAIL
    assert "different fingerprints" in summary
    assert "fp-1 != fp-2" in findings[0]


def test_a_capability_that_writes_but_declares_no_replay_obligation_fails(specimen):
    """An undeclared writer is a register nobody gates."""
    writer = CONFORMANT_SOURCE + (
        "\n\ndef emit(path):\n    return path.write_text('artifact', encoding='utf-8')\n"
    )
    with specimen.build(modules={"specimen.py": writer}) as package:
        declaration = declaration_for(package)
        verdict, summary, findings = measure(probe_certifiable, declaration)
    assert verdict is Verdict.FAIL
    assert "declares no replay obligation" in summary
    assert any("write_text()" in item for item in findings)


def test_a_capability_declaring_a_replay_obligation_its_source_cannot_discharge_fails(specimen):
    """A phantom writer is a replay obligation nobody can discharge."""
    with specimen.build() as package:
        declaration = replace(
            declaration_for(package),
            replay=ReplayDeclaration(
                writes_tracked_artifacts=True,
                target=SymbolRef.parse(f"{package}.specimen:bootstrap_specimen"),
            ),
        )
        verdict, summary, findings = measure(probe_certifiable, declaration)
    assert verdict is Verdict.FAIL
    assert "cannot discharge" in summary
    assert ARTIFACT_WRITE_CALLS[0] in findings[0]


def test_a_declared_writer_whose_replay_target_does_not_resolve_fails(specimen):
    writer = CONFORMANT_SOURCE + (
        "\n\ndef emit(path):\n    return path.write_text('artifact', encoding='utf-8')\n"
    )
    with specimen.build(modules={"specimen.py": writer}) as package:
        declaration = replace(
            declaration_for(package),
            replay=ReplayDeclaration(
                writes_tracked_artifacts=True,
                target=SymbolRef.parse(f"{package}.specimen:absent_symbol"),
            ),
        )
        verdict, summary, _ = measure(probe_certifiable, declaration)
    assert verdict is Verdict.FAIL
    assert "does not resolve" in summary


def test_a_declared_writer_whose_replay_target_is_not_callable_fails(specimen):
    writer = CONFORMANT_SOURCE + (
        "\n\nREPLAY_TARGET = 'not callable'\n"
        "\n\ndef emit(path):\n    return path.write_text('artifact', encoding='utf-8')\n"
    )
    with specimen.build(modules={"specimen.py": writer}) as package:
        declaration = replace(
            declaration_for(package),
            replay=ReplayDeclaration(
                writes_tracked_artifacts=True,
                target=SymbolRef.parse(f"{package}.specimen:REPLAY_TARGET"),
            ),
        )
        verdict, summary, _ = measure(probe_certifiable, declaration)
    assert verdict is Verdict.FAIL
    assert "not callable" in summary


def test_a_declared_writer_with_a_resolvable_replay_target_passes(specimen):
    writer = CONFORMANT_SOURCE + (
        "\n\ndef emit(path):\n    return path.write_text('artifact', encoding='utf-8')\n"
    )
    with specimen.build(modules={"specimen.py": writer}) as package:
        declaration = replace(
            declaration_for(package),
            replay=ReplayDeclaration(
                writes_tracked_artifacts=True,
                target=SymbolRef.parse(f"{package}.specimen:bootstrap_specimen"),
            ),
        )
        verdict, summary, _ = measure(probe_certifiable, declaration)
    assert verdict is Verdict.PASS
    assert "re-measurable at its own commit" in summary


# ---------------------------------------------------------------------------
# UFC-12 — composable
# ---------------------------------------------------------------------------


def test_a_dependency_on_a_capability_nobody_declared_is_refused(specimen):
    """The graph refuses to order before a verdict exists — a stronger answer than FAIL.

    ``probe_composable`` notes the unknown dependency and then asks the register for its
    dependency order, which cannot be produced at all while a declared edge points outside the
    population. So this article is not merely unsatisfied; it is unmeasurable, and the probe
    surfaces that as a refusal rather than as a verdict it has no basis for.
    """
    with specimen.build() as package:
        declaration = declaration_for(package, dependencies=["UCOS-NOBODY-001"])
        register = register_for(declaration)
        with pytest.raises(FoundationConformanceError) as exc:
            probe_composable(declaration, context_for(register))
    assert "unregistered dependency" in str(exc.value)
    assert "UCOS-NOBODY-001" in str(exc.value)


def test_a_declared_dependency_that_is_never_imported_fails(specimen):
    """A dependency declared but not imported is a composition claim nothing discharges."""
    with specimen.build() as first_package:
        with specimen.build() as second_package:
            dependant = declaration_for(first_package, dependencies=["UCOS-SPEC-002"])
            dependency = declaration_for(second_package, capability_id="UCOS-SPEC-002")
            register = register_for(dependant, dependency)
            verdict, _, findings = probe_composable(dependant, context_for(register))
    assert verdict is Verdict.FAIL
    assert any("is never imported" in item for item in findings)


def test_a_dependency_that_is_really_imported_passes(specimen):
    with specimen.build() as dependency_package:
        importer = CONFORMANT_SOURCE + f"\n\nfrom {dependency_package} import specimen as _dep\n"
        with specimen.build(modules={"specimen.py": importer}) as dependant_package:
            dependant = declaration_for(dependant_package, dependencies=["UCOS-SPEC-002"])
            dependency = declaration_for(dependency_package, capability_id="UCOS-SPEC-002")
            register = register_for(dependant, dependency)
            verdict, summary, _ = probe_composable(dependant, context_for(register))
    assert verdict is Verdict.PASS
    assert "composes 1 capabilities" in summary


# ---------------------------------------------------------------------------
# UFC-13 — specialized by declaration
# ---------------------------------------------------------------------------


def test_a_module_carrying_a_repository_locator_fails(specimen):
    """A project literal in code is a capability that cannot be specialised by declaration."""
    localised = CONFORMANT_SOURCE + "\nROOT = '/Users/somebody/UCOS-CONSOLIDATION/engine'\n"
    with specimen.build(modules={"specimen.py": localised}) as package:
        declaration = declaration_for(package)
        verdict, summary, findings = measure(probe_specialized, declaration)
    assert verdict is Verdict.FAIL
    assert "project literals are present" in summary
    assert any("carries a repository locator" in item for item in findings)


def test_a_register_declaring_no_locator_pattern_cannot_measure_ufc_13(specimen):
    with specimen.build() as package:
        declaration = declaration_for(package)
        with pytest.raises(FoundationConformanceError) as exc:
            measure(probe_specialized, declaration, locator_pattern="")
    assert "cannot be measured" in str(exc.value)
