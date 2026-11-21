"""UCOS-UNG-001 — the artifact templates: the pluggable rendering authority.

The templates carry the generator's strongest claim: that what they render is *complete and
conformant* rather than a stub with holes. So the assertions here are structural rather than
textual — every rendered Python module must parse, every rendered JSON document must load, and
every symbol a template promises must actually appear in what it rendered. A test that only
checked for a substring would pass on a file that no interpreter could read.

The second claim is that a template renders **from the declaration alone**. That is proven by
rendering a declaration stripped of every optional part: no CLI, no registries, no extension
points, no catalogue, no entry point. A template that only worked for a fully-grown nucleus
could not generate a new one, which is the job.
"""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from platform.tests.universal_generator_helpers import (
    NonStringTemplate,
    RaisingTemplate,
    StubTemplate,
    declaration,
    minimal_declaration,
    target,
)
from platform.universal_foundation.conformance import ReplayDeclaration, SymbolRef
from platform.universal_generator.contracts import ArtifactKind
from platform.universal_generator.errors import GenerationTemplateError
from platform.universal_generator.templates import (
    GENERATED_BANNER,
    SHIPPED_TEMPLATES,
    BootstrapTemplate,
    BuildTemplate,
    ContractTemplate,
    DeclarationTemplate,
    DocumentationTemplate,
    ErrorsTemplate,
    PolicyTemplate,
    RegistryTemplate,
    RuntimeTemplate,
    TemplateDescriptor,
    TestTemplate,
    shipped_templates,
    template_fingerprint,
)

import pytest

#: The templates whose output is a Python module and must therefore parse.
PYTHON_TEMPLATES = (
    ContractTemplate,
    ErrorsTemplate,
    RegistryTemplate,
    BootstrapTemplate,
    RuntimeTemplate,
    TestTemplate,
)

#: The templates whose output is a JSON document and must therefore load.
JSON_TEMPLATES = (DeclarationTemplate, PolicyTemplate)

DECLARATIONS = {
    "complete": declaration,
    "minimal": minimal_declaration,
}


def render(template_class, which: str = "complete") -> str:
    """Render one template against a named declaration shape."""
    return template_class().apply(DECLARATIONS[which](), target())


# ---------------------------------------------------------------------------
# the template contract
# ---------------------------------------------------------------------------


def test_every_shipped_template_declares_a_distinct_name_and_a_kind():
    templates = shipped_templates()
    assert len(templates) == len(SHIPPED_TEMPLATES)
    names = [item.name for item in templates]
    assert len(set(names)) == len(names)
    for item in templates:
        descriptor = item.descriptor()
        assert isinstance(descriptor, TemplateDescriptor)
        assert descriptor.kind in ArtifactKind
        assert descriptor.description


def test_the_shipped_templates_cover_every_declared_artifact_kind():
    """Ten kinds, ten shipped renderers: no obligation ships without an authority."""
    assert {item.descriptor().kind for item in shipped_templates()} == set(ArtifactKind)


def test_the_descriptor_projection_carries_the_name_kind_and_description():
    payload = ContractTemplate().descriptor().to_dict()
    assert payload["name"] == "contract-surface"
    assert payload["kind"] == "contract"
    assert payload["description"]


def test_the_population_fingerprint_ignores_the_order_it_is_given():
    forward = template_fingerprint(shipped_templates())
    backward = template_fingerprint(tuple(reversed(shipped_templates())))
    assert forward == backward


def test_a_different_population_fingerprints_differently():
    assert template_fingerprint(shipped_templates()) != template_fingerprint(
        shipped_templates()[:-1]
    )


# ---------------------------------------------------------------------------
# apply: fault containment
# ---------------------------------------------------------------------------


def test_apply_terminates_the_rendered_artifact_with_a_newline():
    assert StubTemplate(content="no trailing newline").apply(declaration(), target()).endswith("\n")


def test_apply_does_not_double_terminate_an_artifact_that_already_ends_cleanly():
    assert StubTemplate(content="ends cleanly\n").apply(declaration(), target()) == (
        "ends cleanly\n"
    )


def test_a_renderer_that_raises_is_contained_as_a_typed_refusal():
    """A partial artifact would carry the authority of the declaration it half-derives from."""
    with pytest.raises(GenerationTemplateError) as exc:
        RaisingTemplate(RuntimeError("upstream exploded")).apply(declaration(), target("GT-07"))
    message = str(exc.value)
    assert "upstream exploded" in message
    assert "GT-07" in message
    assert "UCOS-UNG-001" in message


def test_a_typed_template_refusal_passes_through_unwrapped():
    """A refusal the template already made is not re-wrapped into a vaguer one."""
    original = GenerationTemplateError("already typed", template="raising")
    with pytest.raises(GenerationTemplateError) as exc:
        RaisingTemplate(original).apply(declaration(), target())
    assert exc.value is original


@pytest.mark.parametrize("empty", ("", "   \n\t "))
def test_a_template_that_renders_nothing_is_refused(empty):
    with pytest.raises(GenerationTemplateError) as exc:
        StubTemplate(content=empty).apply(declaration(), target())
    assert "rendered nothing" in str(exc.value)


def test_a_template_that_renders_a_non_string_is_refused():
    with pytest.raises(GenerationTemplateError):
        NonStringTemplate().apply(declaration(), target())


# ---------------------------------------------------------------------------
# what the templates render
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("template_class", PYTHON_TEMPLATES)
@pytest.mark.parametrize("which", ("complete", "minimal"))
def test_every_rendered_python_artifact_parses(template_class, which):
    """A skeleton no interpreter can read would hand its author the job the generator removes."""
    source = render(template_class, which)
    ast.parse(source)  # raises SyntaxError if the render is not valid Python
    assert GENERATED_BANNER in source


@pytest.mark.parametrize("template_class", JSON_TEMPLATES)
@pytest.mark.parametrize("which", ("complete", "minimal"))
def test_every_rendered_json_artifact_loads(template_class, which):
    payload = json.loads(render(template_class, which))
    assert isinstance(payload, dict) and payload


@pytest.mark.parametrize("template_class", SHIPPED_TEMPLATES)
@pytest.mark.parametrize("which", ("complete", "minimal"))
def test_every_template_renders_the_same_bytes_for_the_same_declaration(template_class, which):
    assert render(template_class, which) == render(template_class, which)


def test_the_declaration_template_projects_the_register_entry_back_into_its_own_shape():
    payload = json.loads(render(DeclarationTemplate))
    assert payload["capability_id"] == "UCOS-UNG-001"
    assert payload["replay"]["writes_tracked_artifacts"] is False
    # The nucleus profile is re-nested, and each facet keeps the reason for its status.
    assert isinstance(payload["nucleus"], dict)
    flattened = json.dumps(payload["nucleus"])
    assert '"status": "present"' in flattened
    assert '"evidence"' in flattened
    assert '"rationale"' in flattened  # the not-applicable facets state why


def test_the_declaration_template_omits_a_cli_the_declaration_does_not_have():
    assert "cli" in json.loads(render(DeclarationTemplate, "complete"))
    assert "cli" not in json.loads(render(DeclarationTemplate, "minimal"))


def test_the_declaration_template_carries_a_declared_replay_target():
    """A nucleus that writes must name where its writes replay to (UFC-11).

    The registered population currently writes nothing, so the writing posture is supplied
    here. Rendering it is what proves the projection would carry the replay obligation
    forward rather than dropping it the first time a nucleus does write.
    """
    writer = replace(
        declaration(),
        replay=ReplayDeclaration(
            writes_tracked_artifacts=True,
            target=SymbolRef.parse("platform.universal_generator.registry:TargetRegister"),
        ),
    )
    payload = json.loads(DeclarationTemplate().apply(writer, target()))
    assert payload["replay"]["writes_tracked_artifacts"] is True
    assert payload["replay"]["target"] == str(writer.replay.target)


def test_the_contract_template_publishes_the_symbols_the_declaration_names():
    source = render(ContractTemplate)
    item = declaration()
    tree = ast.parse(source)
    assigned = {
        node.target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    } | {
        name.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for name in node.targets
        if isinstance(name, ast.Name)
    }
    assert {item.identity.attribute, item.version.attribute, item.contracts.attribute} <= assigned
    assert f'"{item.capability_id}"' in source


def test_the_errors_template_derives_a_distinct_stable_code_per_refusal():
    source = render(ErrorsTemplate)
    codes = [line.split('"')[1] for line in source.splitlines() if "    code = " in line]
    assert len(codes) == len(set(codes)) == 4
    assert all(code.startswith("EC2-UNG-") for code in codes)
    # Every class derives from the declared error base.
    base = declaration().errors_base.attribute
    classes = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.ClassDef)]
    assert classes[0].name == base
    assert all(any(b.id == base for b in c.bases) for c in classes[1:])


def test_the_errors_template_derives_its_prefix_from_an_identity_without_a_tail():
    """An identity that is not three dash-separated parts still yields a usable prefix."""
    source = ErrorsTemplate().apply(replace(declaration(), capability_id="NUCLEUS"), target())
    assert "EC2-NUCLEUS-000" in source
    ast.parse(source)


def test_the_registry_template_names_the_declared_registry_and_extension_point():
    item = declaration()
    source = render(RegistryTemplate)
    classes = {n.name for n in ast.walk(ast.parse(source)) if isinstance(n, ast.ClassDef)}
    assert item.registries[0].symbol.attribute in classes
    assert item.extension_points[0].symbol.attribute in classes


def test_the_registry_template_derives_symbols_when_the_declaration_names_none():
    """A nucleus that has not yet declared a registry still gets one derived from its package."""
    source = render(RegistryTemplate, "minimal")
    classes = {n.name for n in ast.walk(ast.parse(source)) if isinstance(n, ast.ClassDef)}
    assert "UniversalGeneratorRegistry" in classes
    assert "UniversalGeneratorProvider" in classes


def test_the_bootstrap_template_wires_the_declared_service_and_performs_no_import_side_effect():
    item = declaration()
    source = render(BootstrapTemplate)
    tree = ast.parse(source)
    functions = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert {
        item.bootstrap.attribute,
        item.service_descriptor.attribute,
        item.service_register.attribute,
    } <= functions
    assert f'"{item.service_name}"' in source
    # Nothing at module level does anything but define or assign (UFC-07).
    assert all(
        isinstance(node, ast.Import | ast.ImportFrom | ast.Assign | ast.FunctionDef | ast.Expr)
        for node in tree.body
    )


def test_the_bootstrap_template_falls_back_to_the_conventional_registry_module():
    source = render(BootstrapTemplate, "minimal")
    assert "from platform.universal_generator.registry import" in source


def test_the_runtime_template_renders_a_one_command_surface():
    source = render(RuntimeTemplate)
    item = declaration()
    assert f'prog="{item.entry_point}"' in source
    functions = {n.name for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
    assert item.cli.attribute in functions


def test_the_runtime_template_derives_an_entry_point_and_a_main_when_none_is_declared():
    source = render(RuntimeTemplate, "minimal")
    assert 'prog="ucos-universal-generator"' in source
    functions = {n.name for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
    assert "main" in functions


def test_the_policy_template_renders_a_well_formed_but_empty_catalogue():
    """Empty and well-formed: a nucleus is specialised by registration, not by editing code."""
    payload = json.loads(render(PolicyTemplate))
    assert payload["members"] == []
    assert payload["register_id"].startswith("ucos.")
    assert GENERATED_BANNER in payload["$comment"]


def test_the_documentation_template_derives_every_section_from_the_declaration():
    item = declaration()
    text = render(DocumentationTemplate)
    assert text.startswith(f"# {item.capability_id} — {item.name}")
    assert f"`{item.package}`" in text
    assert f"`{item.service_name}`" in text
    assert f"`{item.entry_point}`" in text
    # Every declared facet is tabulated with the reason for its status.
    for entry in item.nucleus.entries:
        assert f"`{entry.path}`" in text


def test_the_documentation_template_says_so_when_nothing_is_declared():
    text = render(DocumentationTemplate, "minimal")
    assert "* none declared" in text  # extension points
    assert "(none declared)" in text  # entry point


def test_the_documentation_template_lists_declared_dependencies():
    item = replace(declaration(), dependencies=("UCOS-UFC-001", "UCOS-URTF-001"))
    text = DocumentationTemplate().apply(item, target())
    assert "* depends on `UCOS-UFC-001`" in text
    assert "* depends on `UCOS-URTF-001`" in text


def test_the_documentation_template_says_so_when_nothing_is_depended_on():
    item = replace(declaration(), dependencies=())
    text = DocumentationTemplate().apply(item, target())
    assert "depends on nothing" in text


def test_the_test_template_renders_executable_obligations_that_bind_to_the_declaration():
    item = declaration()
    source = render(TestTemplate)
    tests = {n.name for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
    assert all(name.startswith("test_") for name in tests)
    assert len(tests) >= 5
    assert f'"{item.capability_id}"' in source
    assert f'"{item.service_name}"' in source


def test_the_test_template_binds_to_derived_symbols_when_none_are_declared():
    source = render(TestTemplate, "minimal")
    ast.parse(source)
    assert "UniversalGeneratorRegistry" in source
    assert "from platform.universal_generator.registry import" in source


def test_the_build_template_publishes_the_declared_entry_point_and_coverage_wiring():
    item = declaration()
    text = render(BuildTemplate)
    assert f'{item.entry_point} = "{item.cli}"' in text
    assert f"--cov={item.package}" in text


def test_the_build_template_derives_an_entry_point_and_a_cli_when_none_is_declared():
    text = render(BuildTemplate, "minimal")
    assert 'ucos-universal-generator = "platform.universal_generator.cli:main"' in text
