"""UCOS-UFC-001 — the conformance vocabulary, register, probe registry and engine.

Everything a declaration is made of, and every way each part refuses. The refusals are the
subject: a register that accepted a malformed symbol reference, an unresolvable module, a
profile leaf stating a status with no reason, or a dependency graph with a cycle would be a
register whose contents nobody could measure — and an unmeasurable declaration is worse than
an absent one, because it looks like evidence.

The engine's own containment is proven the same way: a probe that raises, in either the typed
or the untyped direction, must land as a FAULT carrying what raised, because a Constitution
that could be silenced by an exception is not fail-closed.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from platform.tests.universal_conformance_helpers import (
    context_for,
    declaration_document,
    declaration_for,
    register_for,
    specimen_package,
)
from platform.universal_foundation.conformance import (
    CallableProbe,
    CapabilityConformance,
    CapabilityDeclaration,
    CapabilityRegister,
    ConformanceDetermination,
    ConformanceEngine,
    ExtensionPointDeclaration,
    FacetDeclaration,
    FacetStatus,
    FoundationConformanceError,
    GateResult,
    NucleusProfile,
    ProbeRegistry,
    RegistryDeclaration,
    ReplayDeclaration,
    SymbolRef,
    Verdict,
    _module_level_calls,
    _parse,
    default_capability_register,
    default_probe_registry,
    load_capability_register,
)
from platform.universal_foundation.constitution import foundation_constitution

import pytest


@pytest.fixture(scope="module")
def register() -> CapabilityRegister:
    return default_capability_register()


@pytest.fixture(scope="module")
def declaration(register) -> CapabilityDeclaration:
    return register.require("UCOS-UNG-001")


# ---------------------------------------------------------------------------
# SymbolRef
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ("no_colon", "too:many:colons", "", 42, None, ["a:b"]))
def test_a_symbol_reference_that_is_not_module_attribute_is_refused(value):
    with pytest.raises(FoundationConformanceError) as exc:
        SymbolRef.parse(value, context="UCOS-SPEC-001")
    assert "module:attribute" in str(exc.value)


@pytest.mark.parametrize("value", (":attribute", "module:", "  :  "))
def test_a_symbol_reference_missing_either_half_is_refused(value):
    with pytest.raises(FoundationConformanceError) as exc:
        SymbolRef.parse(value)
    assert "incomplete" in str(exc.value)


def test_a_symbol_reference_is_stripped_and_renders_as_it_was_declared():
    parsed = SymbolRef.parse("  platform.foundation.contracts : ContractRef  ")
    assert parsed.module == "platform.foundation.contracts"
    assert parsed.attribute == "ContractRef"
    assert str(parsed) == "platform.foundation.contracts:ContractRef"


def test_a_symbol_resolves_on_demand_and_never_at_import():
    from platform.foundation.contracts import ContractRef

    assert SymbolRef.parse("platform.foundation.contracts:ContractRef").resolve() is ContractRef


def test_a_symbol_whose_module_cannot_be_imported_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        SymbolRef.parse("module.that.does.not.exist:thing").resolve()
    assert "could not be imported" in str(exc.value)


def test_a_symbol_whose_attribute_is_absent_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        SymbolRef.parse("platform.foundation.contracts:NoSuchAttribute").resolve()
    assert "attribute is absent" in str(exc.value)


# ---------------------------------------------------------------------------
# the declaration's parts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload", ({}, {"abstract": True}, "symbol", None))
def test_an_extension_point_declaration_without_a_symbol_is_refused(payload):
    with pytest.raises(FoundationConformanceError) as exc:
        ExtensionPointDeclaration.from_document(payload)
    assert "requires 'symbol'" in str(exc.value)


def test_an_extension_point_declaration_round_trips():
    original = ExtensionPointDeclaration.from_document(
        {"symbol": "platform.foundation.contracts:ContractRef", "methods": ["to_dict"]}
    )
    assert ExtensionPointDeclaration.from_document(original.to_dict()) == original


def test_a_registry_declaration_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        RegistryDeclaration.from_document(["symbol"])
    assert "must be a mapping" in str(exc.value)


def test_a_registry_declaration_missing_its_determinism_methods_is_refused():
    """A registry surface declared without ordered/require names no determinism to measure."""
    with pytest.raises(FoundationConformanceError) as exc:
        RegistryDeclaration.from_document({"symbol": "a:B"})
    message = str(exc.value)
    assert "ordered" in message and "require" in message


def test_a_registry_declaration_round_trips():
    original = RegistryDeclaration.from_document(
        {"symbol": "a.b:C", "ordered": "ordered", "require": "require"}
    )
    assert RegistryDeclaration.from_document(original.to_dict()) == original


def test_a_replay_declaration_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        ReplayDeclaration.from_document(True, capability_id="UCOS-SPEC-001")
    assert "must be a mapping" in str(exc.value)


def test_a_replay_declaration_that_states_no_posture_is_refused():
    """Silence about writing is not a declaration of not writing."""
    with pytest.raises(FoundationConformanceError) as exc:
        ReplayDeclaration.from_document({}, capability_id="UCOS-SPEC-001")
    assert "writes_tracked_artifacts" in str(exc.value)


def test_a_writer_that_names_no_replay_target_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        ReplayDeclaration.from_document(
            {"writes_tracked_artifacts": True}, capability_id="UCOS-SPEC-001"
        )
    assert "must declare a replay target" in str(exc.value)


def test_a_replay_target_declared_by_a_non_writer_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        ReplayDeclaration.from_document(
            {"writes_tracked_artifacts": False, "target": "a:b"},
            capability_id="UCOS-SPEC-001",
        )
    assert "declares no tracked output" in str(exc.value)


def test_a_replay_declaration_round_trips_in_both_postures():
    writer = ReplayDeclaration.from_document(
        {"writes_tracked_artifacts": True, "target": "a.b:c"}, capability_id="X"
    )
    assert writer.to_dict() == {"writes_tracked_artifacts": True, "target": "a.b:c"}
    quiet = ReplayDeclaration.from_document({"writes_tracked_artifacts": False}, capability_id="X")
    assert quiet.to_dict() == {"writes_tracked_artifacts": False, "target": ""}


# ---------------------------------------------------------------------------
# the nucleus profile
# ---------------------------------------------------------------------------


def test_a_facet_status_is_returned_unchanged():
    assert FacetStatus.coerce(FacetStatus.PRESENT, subject="x") is FacetStatus.PRESENT


def test_an_unknown_facet_status_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        FacetStatus.coerce("maybe", subject="X:facet")
    assert "X:facet" in str(exc.value)


def test_a_non_string_facet_status_is_refused():
    with pytest.raises(FoundationConformanceError):
        FacetStatus.coerce(1, subject="X:facet")


def test_a_facet_declaration_reports_whether_it_is_realised_or_inapplicable():
    present = FacetDeclaration("a.b", FacetStatus.PRESENT, "evidence here")
    absent = FacetDeclaration("a.c", FacetStatus.NOT_APPLICABLE, "reason here")
    assert present.present and not absent.present
    assert present.to_dict() == {"path": "a.b", "status": "present", "detail": "evidence here"}


def test_a_silent_profile_is_an_empty_profile():
    assert NucleusProfile.from_document(None, capability_id="X").entries == ()


def test_a_profile_that_is_neither_a_mapping_nor_a_projection_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        NucleusProfile.from_document(7, capability_id="X")
    assert "mapping or a projected sequence" in str(exc.value)


def test_a_nested_profile_flattens_to_dotted_paths_and_skips_comment_keys():
    profile = NucleusProfile.from_document(
        {
            "$comment": "ignored",
            "ownership": {"status": "present", "evidence": "declared here"},
            "truth": {"binding": {"status": "not-applicable", "rationale": "no truth to bind"}},
        },
        capability_id="X",
    )
    assert profile.paths() == ("ownership", "truth.binding")
    assert profile.get("truth.binding").status is FacetStatus.NOT_APPLICABLE
    assert profile.get("nothing.here") is None


def test_a_profile_round_trips_through_its_own_projection():
    """A register entry read, projected and read back must yield the same declaration."""
    original = NucleusProfile.from_document(
        {"ownership": {"status": "present", "evidence": "declared here"}}, capability_id="X"
    )
    assert NucleusProfile.from_document(original.to_dict(), capability_id="X") == original


def test_a_projected_facet_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        NucleusProfile.from_document(["ownership"], capability_id="X")
    assert "projected nucleus facet must be a mapping" in str(exc.value)


def test_a_projected_facet_missing_a_key_names_what_is_missing():
    with pytest.raises(FoundationConformanceError) as exc:
        NucleusProfile.from_document([{"path": "a"}], capability_id="X")
    message = str(exc.value)
    assert "status" in message and "detail" in message


@pytest.mark.parametrize("blank", ("path", "detail"))
def test_a_projected_facet_stating_no_path_or_no_reason_is_refused(blank):
    payload = {"path": "a.b", "status": "present", "detail": "evidence"}
    payload[blank] = "  "
    with pytest.raises(FoundationConformanceError) as exc:
        NucleusProfile.from_document([payload], capability_id="X")
    assert "no path or no reason" in str(exc.value)


def test_a_profile_entry_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        NucleusProfile.from_document({"ownership": "yes"}, capability_id="X")
    assert "must be a mapping" in str(exc.value)


@pytest.mark.parametrize(
    ("status", "key"), (("present", "evidence"), ("not-applicable", "rationale"))
)
def test_a_facet_stating_a_status_with_no_reason_is_refused(status, key):
    """ "Somebody wrote a key" is not a determination."""
    with pytest.raises(FoundationConformanceError) as exc:
        NucleusProfile.from_document({"ownership": {"status": status}}, capability_id="X")
    message = str(exc.value)
    assert status in message and key in message


# ---------------------------------------------------------------------------
# CapabilityDeclaration
# ---------------------------------------------------------------------------


def test_a_declaration_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityDeclaration.from_document(["capability_id"])
    assert "must be a mapping" in str(exc.value)


def test_a_declaration_missing_required_keys_names_every_one_of_them():
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityDeclaration.from_document({"capability_id": "UCOS-SPEC-001"})
    message = str(exc.value)
    assert "identity" in message and "replay" in message


def test_a_declaration_with_a_blank_identity_is_refused():
    document = declaration_document("platform.universal_generator")
    document["capability_id"] = "   "
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityDeclaration.from_document(document)
    assert "must be non-empty" in str(exc.value)


def test_a_declaration_with_no_catalogue_must_declare_itself_policy_free():
    """Silence about configuration is not a declaration of having none."""
    document = declaration_document("platform.universal_generator")
    document["catalogs"] = []
    document["policy_free"] = False
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityDeclaration.from_document(document)
    assert "not declared policy_free" in str(exc.value)


def test_a_declaration_whose_package_cannot_be_imported_refuses_to_locate_itself():
    document = declaration_document("platform.universal_generator")
    document["package"] = "package.that.does.not.exist"
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityDeclaration.from_document(document).package_path()
    assert "could not be imported" in str(exc.value)


def test_a_declaration_whose_package_has_no_filesystem_location_is_refused(tmp_path):
    """A namespace package has no source to measure, so no article can be proven over it."""
    namespace = tmp_path / "specimen_namespace"
    namespace.mkdir()
    sys.path.insert(0, str(tmp_path))
    try:
        document = declaration_document("specimen_namespace")
        document["package"] = "specimen_namespace"
        with pytest.raises(FoundationConformanceError) as exc:
            CapabilityDeclaration.from_document(document).package_path()
        assert "no filesystem location" in str(exc.value)
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("specimen_namespace", None)


def test_source_files_exclude_compiled_residue(declaration):
    sources = declaration.source_files()
    assert sources
    assert all(path.suffix == ".py" for path in sources)
    assert not any("__pycache__" in path.parts for path in sources)


# ---------------------------------------------------------------------------
# determinations over an empty population
# ---------------------------------------------------------------------------


def test_a_determination_over_no_capability_reports_no_maturity():
    """Nothing measured is 0%, never 100%: an unasked question is not a satisfied one."""
    determination = ConformanceDetermination.create(foundation_constitution(), [])
    assert determination.maturity_percentage == 0.0
    assert set(determination.maturity_by_axis().values()) == {0.0}
    assert determination.total == 0
    assert determination.fingerprint()


def test_platform_results_participate_in_maturity_as_a_capability_equivalent_term(declaration):
    """An unconverged platform cannot report full maturity however mature its parts are."""
    passing = [
        GateResult.create(article.gate, article.article_id, declaration.capability_id, Verdict.PASS)
        for article in foundation_constitution().capability_articles()
    ]
    capability = CapabilityConformance.create(declaration, passing)
    without = ConformanceDetermination.create(foundation_constitution(), [capability])
    with_failure = ConformanceDetermination.create(
        foundation_constitution(),
        [capability],
        [GateResult.create("FG-99-PLATFORM", "UFC-99", "PLATFORM", Verdict.FAIL)],
    )
    assert without.maturity_percentage == 100.0
    assert with_failure.maturity_percentage < without.maturity_percentage


def test_an_axis_no_capability_reaches_is_reported_as_zero(declaration):
    """The by-axis reading distinguishes an axis nobody reached from one nobody declared."""
    capability = CapabilityConformance.create(declaration, [])
    determination = ConformanceDetermination.create(foundation_constitution(), [capability])
    by_axis = determination.maturity_by_axis()
    assert by_axis
    assert set(by_axis.values()) == {0.0}
    assert capability.maturity_percentage == 0.0


# ---------------------------------------------------------------------------
# CapabilityRegister
# ---------------------------------------------------------------------------


def test_the_register_reports_what_it_was_declared_as(register):
    assert register.register_id
    assert register.locator_pattern
    assert register.governing_modules
    assert register.count == len(register.ordered())
    assert register.ids() == tuple(item.capability_id for item in register.ordered())


def test_only_a_capability_declaration_may_be_registered():
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityRegister().add({"capability_id": "UCOS-SPEC-001"})
    assert "only CapabilityDeclaration" in str(exc.value)


def test_registering_the_same_declaration_twice_identically_is_idempotent(declaration):
    built = CapabilityRegister([declaration])
    assert built.add(declaration) is declaration
    assert built.count == 1


def test_a_capability_redeclared_with_a_different_body_is_refused(declaration):
    built = CapabilityRegister([declaration])
    with pytest.raises(FoundationConformanceError) as exc:
        built.add(replace(declaration, name="A different name"))
    assert "different body" in str(exc.value)


def test_get_reports_an_undeclared_capability_as_absent(register):
    assert register.get("UCOS-NOBODY-001") is None


def test_require_refuses_an_undeclared_capability(register):
    with pytest.raises(FoundationConformanceError) as exc:
        register.require("UCOS-NOBODY-001")
    assert "UCOS-NOBODY-001" in str(exc.value)


def test_of_domain_selects_only_that_domain(register, declaration):
    selected = register.of_domain(declaration.domain)
    assert declaration in selected
    assert all(item.domain is declaration.domain for item in selected)
    assert register.of_domain(declaration.domain.value) == selected


def test_a_dependency_on_a_capability_nobody_registered_is_refused(declaration):
    built = CapabilityRegister([replace(declaration, dependencies=("UCOS-NOBODY-001",))])
    with pytest.raises(FoundationConformanceError) as exc:
        built.dependency_order()
    assert "unregistered dependency" in str(exc.value)


def test_a_dependency_cycle_is_refused_rather_than_broken_arbitrarily(declaration):
    first = replace(declaration, capability_id="UCOS-A-001", dependencies=("UCOS-B-001",))
    second = replace(declaration, capability_id="UCOS-B-001", dependencies=("UCOS-A-001",))
    built = CapabilityRegister([first, second])
    with pytest.raises(FoundationConformanceError) as exc:
        built.dependency_order()
    message = str(exc.value)
    assert "cycle" in message
    assert "UCOS-A-001" in message and "UCOS-B-001" in message


def test_the_dependency_order_is_total_and_dependency_honest(register):
    order = register.dependency_order()
    assert set(order) == set(register.ids())
    positions = {name: index for index, name in enumerate(order)}
    for item in register.ordered():
        for dependency in item.dependencies:
            assert positions[dependency] < positions[item.capability_id]


def test_a_register_document_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityRegister.from_document([])
    assert "must be a mapping" in str(exc.value)


@pytest.mark.parametrize("capabilities", (None, "UCOS-SPEC-001", 7))
def test_a_register_document_without_a_capabilities_sequence_is_refused(capabilities):
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityRegister.from_document({"capabilities": capabilities})
    assert "'capabilities' sequence" in str(exc.value)


def test_a_register_document_declaring_no_capability_is_refused():
    with pytest.raises(FoundationConformanceError) as exc:
        CapabilityRegister.from_document({"capabilities": []})
    assert "declares no capability" in str(exc.value)


def test_a_register_document_round_trips(register, tmp_path):
    path = tmp_path / "register.json"
    import json

    path.write_text(json.dumps(register.to_dict()), encoding="utf-8")
    assert load_capability_register(path).to_dict() == register.to_dict()


def test_an_unreadable_register_document_is_refused(tmp_path):
    with pytest.raises(FoundationConformanceError):
        load_capability_register(tmp_path / "absent.json")


# ---------------------------------------------------------------------------
# source inspection
# ---------------------------------------------------------------------------


def test_source_that_cannot_be_parsed_is_refused(tmp_path):
    broken = tmp_path / "broken.py"
    broken.write_text("def (:\n", encoding="utf-8")
    with pytest.raises(FoundationConformanceError) as exc:
        _parse(broken)
    assert "could not be parsed" in str(exc.value)


def test_absent_source_is_refused(tmp_path):
    with pytest.raises(FoundationConformanceError):
        _parse(tmp_path / "absent.py")


def test_a_module_level_call_on_something_that_is_neither_a_name_nor_an_attribute(tmp_path):
    """An immediately-invoked expression names no callable, so it contributes none."""
    source = tmp_path / "iife.py"
    source.write_text("VALUE = (lambda: 1)()\nimport json\nOTHER = json.loads('{}')\n", "utf-8")
    calls = _module_level_calls(_parse(source))
    assert "loads" in calls
    assert all(name.isidentifier() for name in calls)


# ---------------------------------------------------------------------------
# ProbeRegistry
# ---------------------------------------------------------------------------


def _outcome(declaration, context):
    del declaration, context
    return Verdict.PASS, "ok", ()


@pytest.mark.parametrize("gate", ("", "   ", 7, None))
def test_a_probe_that_declares_no_gate_is_refused(gate):
    with pytest.raises(FoundationConformanceError) as exc:
        CallableProbe(gate, _outcome)
    assert "must declare its gate" in str(exc.value)


def test_a_callable_probe_requires_something_callable():
    with pytest.raises(FoundationConformanceError) as exc:
        CallableProbe("FG-01-CONTRACT-PUBLISHED", "not callable")
    assert "requires a callable" in str(exc.value)


def test_only_a_conformance_probe_may_be_registered():
    with pytest.raises(FoundationConformanceError) as exc:
        ProbeRegistry().add(_outcome)
    assert "only ConformanceProbe" in str(exc.value)


def test_registering_the_same_probe_object_twice_is_idempotent():
    probe = CallableProbe("FG-X", _outcome)
    registry = ProbeRegistry([probe])
    assert registry.add(probe) is probe
    assert registry.count == 1


def test_a_second_probe_claiming_a_bound_gate_is_refused():
    """Two probes for one gate means the article has no single answer."""
    registry = ProbeRegistry([CallableProbe("FG-X", _outcome)])
    with pytest.raises(FoundationConformanceError) as exc:
        registry.add(CallableProbe("FG-X", _outcome))
    assert "already has a bound probe" in str(exc.value)


def test_extend_registers_every_probe_and_returns_them_in_gate_order():
    registry = ProbeRegistry()
    returned = registry.extend([CallableProbe("FG-Z", _outcome), CallableProbe("FG-A", _outcome)])
    assert [probe.gate() for probe in returned] == ["FG-A", "FG-Z"]
    assert registry.gates() == ("FG-A", "FG-Z")
    assert [probe.gate() for probe in registry.ordered()] == ["FG-A", "FG-Z"]


def test_get_reports_an_unbound_gate_as_absent():
    assert ProbeRegistry().get("FG-X") is None


def test_require_refuses_an_unbound_gate():
    with pytest.raises(FoundationConformanceError) as exc:
        ProbeRegistry().require("FG-X")
    assert "no probe is bound" in str(exc.value)


def test_the_probe_registry_projection_and_fingerprint_are_deterministic():
    forward = ProbeRegistry([CallableProbe("FG-A", _outcome), CallableProbe("FG-Z", _outcome)])
    backward = ProbeRegistry([CallableProbe("FG-Z", _outcome), CallableProbe("FG-A", _outcome)])
    assert forward.to_dict() == backward.to_dict() == {"probe_count": 2, "gates": ["FG-A", "FG-Z"]}
    assert forward.fingerprint() == backward.fingerprint()


def test_a_callable_probe_delegates_to_what_it_wraps(register, declaration):
    probe = CallableProbe("FG-X", _outcome)
    assert probe.measure(declaration, context_for(register_for(declaration))) == (
        Verdict.PASS,
        "ok",
        (),
    )


def test_the_shipped_registry_binds_every_capability_scoped_gate():
    registry = default_probe_registry()
    declared = {article.gate for article in foundation_constitution().capability_articles()}
    assert declared <= set(registry.gates())


# ---------------------------------------------------------------------------
# ConformanceEngine
# ---------------------------------------------------------------------------


def test_the_engine_requires_a_capability_register():
    with pytest.raises(FoundationConformanceError) as exc:
        ConformanceEngine([1, 2])
    assert "requires a CapabilityRegister" in str(exc.value)


def test_the_engine_exposes_the_law_the_population_and_the_probes(register):
    engine = ConformanceEngine(register)
    assert engine.constitution.constitution_id == foundation_constitution().constitution_id
    assert engine.register is register
    assert engine.probes.count > 0
    assert engine.unbound_gates() == ()
    assert engine.fingerprint() == ConformanceEngine(register).fingerprint()


def test_a_build_manifest_that_cannot_be_read_is_refused(register, tmp_path):
    engine = ConformanceEngine(register, project_root=tmp_path)
    with pytest.raises(FoundationConformanceError) as exc:
        engine.context()
    assert "could not be read" in str(exc.value)


def test_a_build_manifest_that_is_not_valid_toml_is_refused(register, tmp_path):
    (tmp_path / "pyproject.toml").write_text("not = = toml", encoding="utf-8")
    with pytest.raises(FoundationConformanceError) as exc:
        ConformanceEngine(register, project_root=tmp_path).context()
    assert "not valid TOML" in str(exc.value)


@pytest.mark.parametrize(
    "manifest", ('[project]\nname = "x"\n', "[project]\n[project.scripts]\n", "")
)
def test_a_build_manifest_declaring_no_console_scripts_is_refused(register, tmp_path, manifest):
    """UFC-06 cannot be measured against a build that publishes nothing."""
    (tmp_path / "pyproject.toml").write_text(manifest, encoding="utf-8")
    with pytest.raises(FoundationConformanceError) as exc:
        ConformanceEngine(register, project_root=tmp_path).context()
    assert "no console scripts table" in str(exc.value)


def test_an_unmeasurable_gate_is_a_fault_rather_than_a_silent_skip(register, declaration):
    """An article whose gate no probe proves is UNKNOWN, and UNKNOWN is never a pass."""
    engine = ConformanceEngine(register, probes=ProbeRegistry())
    article = foundation_constitution().capability_articles()[0]
    result = engine.measure_gate(declaration, article)
    assert result.verdict is Verdict.FAULT
    assert result.summary == "probe could not execute"
    assert "no probe is bound" in result.findings[0]
    assert engine.unbound_gates() == tuple(
        item.gate for item in foundation_constitution().capability_articles()
    )


def test_a_probe_raising_an_uncontained_fault_is_contained_as_one(register, declaration):
    """A Constitution an exception could silence would not be fail-closed."""

    def _explodes(item, context):
        del item, context
        raise ZeroDivisionError("probe exploded")

    article = foundation_constitution().capability_articles()[0]
    engine = ConformanceEngine(
        register, probes=ProbeRegistry([CallableProbe(article.gate, _explodes)])
    )
    result = engine.measure_gate(declaration, article)
    assert result.verdict is Verdict.FAULT
    assert result.summary == "probe raised an uncontained fault"
    assert "ZeroDivisionError: probe exploded" in result.findings[0]


def test_a_governing_module_with_no_filesystem_location_is_skipped(tmp_path):
    """A namespace package carries no source, so it can enumerate nothing."""
    from platform.universal_foundation.conformance import probe_evolution_additive

    namespace = tmp_path / "specimen_governing_namespace"
    namespace.mkdir()
    sys.path.insert(0, str(tmp_path))
    try:
        with specimen_package(tmp_path, "spec_ns_probe") as package:
            item = declaration_for(package)
            built = register_for(item, governing_modules=("specimen_governing_namespace",))
            verdict, summary, _ = probe_evolution_additive(item, context_for(built))
        assert verdict is Verdict.PASS
        assert "1 governing modules" in summary
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("specimen_governing_namespace", None)


def test_measuring_one_capability_covers_every_capability_scoped_article(register, declaration):
    engine = ConformanceEngine(register)
    conformance = engine.measure_capability(declaration)
    assert {item.gate for item in conformance.results} == {
        article.gate for article in foundation_constitution().capability_articles()
    }
    assert conformance.failures() == ()
    assert Path(".").exists()  # the engine read the real build manifest to get here
