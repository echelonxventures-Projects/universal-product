"""UCOS-UNG-001 — the Ω Nucleus generator: declarations in, artifact plans out.

Two claims are load-bearing and both are proven here.

*A declaration is the only input.* Destinations resolve from tokens the declaration already
answers, and a token it cannot answer is a refusal rather than a guess — because a plan with a
destination nobody declared is worse than no plan at all.

*The generator never writes.* A plan is a determination; materialising it is a separate
constituent act. That claim is checked against the package's own source rather than asserted,
since a claim about writing that nothing checks is exactly the kind of fact that rots.
"""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
from platform.tests.universal_generator_helpers import (
    CATALOG_FREE_CAPABILITY,
    StubTemplate,
    declaration,
    minimal_declaration,
    target,
)
from platform.universal_foundation.conformance import default_capability_register
from platform.universal_generator.contracts import GenerationPlan
from platform.universal_generator.errors import (
    GenerationDestinationError,
    GenerationTemplateError,
)
from platform.universal_generator.generator import (
    NucleusGenerator,
    build_generator,
    destination_tokens,
    resolve_destination,
)
from platform.universal_generator.registry import (
    TargetRegister,
    TemplateRegistry,
    default_target_register,
)
from platform.universal_generator.templates import shipped_templates

import pytest

WRITE_ATTRIBUTES = {"write_text", "write_bytes", "mkdir", "touch", "unlink", "rename"}
WRITE_CALLS = {"open"}


def stub_generator(*targets, templates=None) -> NucleusGenerator:
    """A generator over the supplied targets, rendered by a single stub template."""
    declared = targets or (target("GT-01", template="stub"),)
    return build_generator(
        TargetRegister(targets=declared),
        templates if templates is not None else [StubTemplate("stub")],
    )


# ---------------------------------------------------------------------------
# destination tokens
# ---------------------------------------------------------------------------


def test_every_token_is_derived_from_something_the_declaration_already_says():
    tokens = destination_tokens(declaration())
    assert tokens["capability_id"] == "UCOS-UNG-001"
    assert tokens["package"] == "platform.universal_generator"
    assert tokens["package_path"] == "platform/universal_generator"
    assert tokens["slug"] == "universal_generator"
    assert tokens["contracts_path"] == "platform/universal_generator/contracts.py"
    assert tokens["errors_path"] == "platform/universal_generator/errors.py"
    assert tokens["bootstrap_path"] == "platform/universal_generator/bootstrap.py"
    assert tokens["cli_path"] == "platform/universal_generator/cli.py"
    assert tokens["registry_path"].endswith(".py")
    assert tokens["catalog_path"].startswith("platform/universal_generator/catalog/")
    assert tokens["entry_point"] == "ucos-generate"


def test_a_declaration_that_declares_no_optional_surface_answers_no_optional_token():
    """The optional tokens are exactly the optional declarations — not defaults with a fallback."""
    tokens = destination_tokens(minimal_declaration())
    for optional in ("cli_path", "registry_path", "catalog_path", "entry_point"):
        assert optional not in tokens
    # The obligatory tokens are still answered: a nucleus always has these.
    assert {"capability_id", "package", "package_path", "contracts_path"} <= set(tokens)


def test_a_declaration_with_no_catalogue_cannot_answer_the_catalogue_token():
    tokens = destination_tokens(declaration(CATALOG_FREE_CAPABILITY))
    assert "catalog_path" not in tokens
    assert "cli_path" in tokens


def test_a_destination_pattern_resolves_every_token_it_names():
    resolved = resolve_destination("{package_path}/{slug}_notes.md", declaration())
    assert resolved == "platform/universal_generator/universal_generator_notes.md"


def test_a_pattern_with_no_token_is_returned_as_a_literal_path():
    assert resolve_destination("docs/GENERATION.md", declaration()) == "docs/GENERATION.md"


def test_an_unanswerable_token_is_refused_and_names_what_was_available():
    with pytest.raises(GenerationDestinationError) as exc:
        resolve_destination("{catalog_path}/x.json", declaration(CATALOG_FREE_CAPABILITY))
    message = str(exc.value)
    assert "catalog_path" in message
    assert CATALOG_FREE_CAPABILITY in message
    assert "package_path" in message  # the available set is reported, not just the failure


def test_every_unanswerable_token_in_one_pattern_is_reported_together():
    with pytest.raises(GenerationDestinationError) as exc:
        resolve_destination("{nowhere}/{alsonowhere}.py", declaration())
    assert "alsonowhere,nowhere" in str(exc.value)


# ---------------------------------------------------------------------------
# composition
# ---------------------------------------------------------------------------


def test_a_target_naming_an_unregistered_template_fails_at_composition_not_at_render():
    """A plan silently short by one artifact is the failure this refusal prevents."""
    with pytest.raises(GenerationTemplateError) as exc:
        NucleusGenerator(
            TargetRegister(targets=[target("GT-01", template="nobody")]), TemplateRegistry()
        )
    assert "nobody" in str(exc.value)


def test_composition_requires_a_target_register():
    with pytest.raises(GenerationDestinationError):
        NucleusGenerator({"GT-01": target()}, TemplateRegistry())  # type: ignore[arg-type]


def test_composition_requires_a_template_registry():
    with pytest.raises(GenerationDestinationError):
        NucleusGenerator(TargetRegister(), [StubTemplate("stub")])  # type: ignore[arg-type]


def test_a_composed_generator_reports_no_unbound_target():
    """Composition already refused an unbound target, so this is always empty afterwards."""
    assert stub_generator().unbound_targets() == ()


def test_the_composition_exposes_the_declarations_it_was_built_from():
    generator = stub_generator()
    assert generator.targets.ids() == ("GT-01",)
    assert generator.templates.names() == ("stub",)


def test_build_generator_seeds_the_shipped_templates_by_default():
    generator = build_generator(default_target_register())
    assert generator.templates.names() == tuple(sorted(t.name for t in shipped_templates()))


def test_the_composition_projection_and_fingerprint_are_deterministic():
    first, second = stub_generator(), stub_generator()
    assert first.to_dict() == second.to_dict()
    assert first.fingerprint() == second.fingerprint()
    assert first.to_dict()["unbound_targets"] == []


def test_a_different_composition_fingerprints_differently():
    one = stub_generator(target("GT-01", template="stub"))
    two = stub_generator(target("GT-02", template="stub", destination="pkg/other.py"))
    assert one.fingerprint() != two.fingerprint()


# ---------------------------------------------------------------------------
# rendering and planning
# ---------------------------------------------------------------------------


def test_rendering_one_obligation_lands_the_rendered_bytes_at_the_resolved_destination():
    generator = stub_generator(target("GT-01", template="stub", destination="{package_path}/x.py"))
    artifact = generator.render(declaration(), generator.targets.require("GT-01"))
    assert artifact.destination == "platform/universal_generator/x.py"
    assert artifact.content == "stub content\n"
    assert artifact.target_id == "GT-01"


def test_generating_covers_every_declared_target_exactly_once():
    generator = stub_generator(
        target("GT-01", template="stub", destination="{package_path}/a.py"),
        target("GT-02", template="stub", destination="{package_path}/b.py"),
    )
    plan = generator.generate(declaration())
    assert isinstance(plan, GenerationPlan)
    assert plan.total == 2
    assert {item.target_id for item in plan.artifacts} == {"GT-01", "GT-02"}
    assert plan.nucleus_id == "UCOS-UNG-001"


def test_generating_the_same_declaration_twice_yields_one_identity():
    """Byte-identical artifacts with the same identities: re-derivable, not merely repeatable."""
    generator = stub_generator()
    assert generator.generate(declaration()).plan_id == generator.generate(declaration()).plan_id


def test_generation_requires_the_nucleus_own_declaration():
    with pytest.raises(GenerationDestinationError):
        stub_generator().generate({"capability_id": "UCOS-X-001"})  # type: ignore[arg-type]


def test_generating_over_a_population_requires_a_register():
    with pytest.raises(GenerationDestinationError):
        stub_generator().generate_all([declaration()])  # type: ignore[arg-type]


def test_generating_over_a_population_covers_every_nucleus_in_declared_order():
    generator = stub_generator(
        target("GT-01", template="stub", destination="{package_path}/{slug}_a.py")
    )
    register = default_capability_register()
    plans = generator.generate_all(register)
    assert len(plans) == len(register.ordered())
    assert [plan.nucleus_id for plan in plans] == [d.capability_id for d in register.ordered()]


def test_a_declaration_that_answers_every_destination_reports_no_finding():
    generator = stub_generator(target("GT-01", template="stub", destination="{package_path}/a.py"))
    assert generator.can_generate(declaration()) == ()


def test_can_generate_names_each_target_a_declaration_cannot_answer_without_generating():
    """The Phase 6 question — *can* the Foundation generate — asked without generating."""
    generator = stub_generator(
        target("GT-01", template="stub", destination="{catalog_path}/policy.json"),
        target("GT-02", template="stub", destination="{package_path}/ok.py"),
    )
    findings = generator.can_generate(declaration(CATALOG_FREE_CAPABILITY))
    assert len(findings) == 1
    assert findings[0].startswith("GT-01: ")
    assert "catalog_path" in findings[0]


def test_the_packaged_composition_can_generate_every_nucleus_that_declares_a_catalogue():
    """The one blocked nucleus is blocked for a declared reason, not an accidental one."""
    generator = build_generator(default_target_register())
    for item in default_capability_register().ordered():
        findings = generator.can_generate(item)
        if item.catalogs:
            assert findings == (), f"{item.capability_id} should be generatable"
        else:
            assert findings, f"{item.capability_id} declares no catalogue and must be blocked"


# ---------------------------------------------------------------------------
# the generator writes nothing
# ---------------------------------------------------------------------------


def test_no_module_in_the_generator_package_performs_a_filesystem_write():
    """The 'emits no tracked artifact' claim, checked against the source that must honour it."""
    package = Path(__file__).resolve().parents[2] / "platform" / "universal_generator"
    offenders: list[str] = []
    for source in sorted(package.glob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in WRITE_ATTRIBUTES:
                offenders.append(f"{source.name}:{node.lineno} {func.attr}")
            elif isinstance(func, ast.Name) and func.id in WRITE_CALLS:
                offenders.append(f"{source.name}:{node.lineno} {func.id}")
    assert offenders == []


def test_generating_a_full_plan_creates_nothing_on_disk(tmp_path, monkeypatch):
    """A plan states what would exist; nothing appears anywhere as a result of stating it."""
    monkeypatch.chdir(tmp_path)
    generator = build_generator(default_target_register())
    plan = generator.generate(declaration())
    assert plan.total > 0
    assert list(tmp_path.iterdir()) == []


def test_a_declaration_with_no_package_dependencies_still_plans():
    """Dependencies govern composition order, not what a nucleus is made of."""
    generator = stub_generator(target("GT-01", template="stub", destination="{package_path}/a.py"))
    plan = generator.generate(replace(declaration(), dependencies=()))
    assert plan.total == 1
