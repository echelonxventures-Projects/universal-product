"""UCOS-UFC-001 — constitutional convergence: exactly one live answer per model.

Every constitutional question is permitted exactly one implementation. What makes that
enforceable rather than aspirational is that a declared relation is *verified* and never
asserted: a SUPERSEDED surface must actually be gone, a DELEGATES surface must actually import
the canonical owner, a PROJECTION must actually hold no executable determination, and a
GOVERNED surface must actually restate none of the canonical law.

So the tests below build surfaces that really violate each relation. The repository's own
population satisfies all four, which is what the register is for and also why its violation
paths are the ones nothing has ever run. Duplication is measured the same way: by content, so a
copy is found because it *is* one, not because it is named like one.
"""

from __future__ import annotations

import json
from pathlib import Path
from platform.universal_foundation.conformance import SymbolRef, Verdict
from platform.universal_foundation.constitution import foundation_constitution
from platform.universal_foundation.convergence import (
    DEFAULT_CONVERGENCE_FILENAME,
    ConstitutionalModel,
    ConvergenceEngine,
    ConvergenceRegister,
    ConvergenceRelation,
    DuplicateGroup,
    DuplicationPolicy,
    SubordinateSurface,
    bootstrap_convergence,
    catalog_path,
    default_convergence_register,
    load_convergence_register,
)
from platform.universal_foundation.errors import FoundationConvergenceError

import pytest

#: A package that really exists and really publishes a contract tuple.
OWNER_PACKAGE = "platform.universal_generator"
OWNER_CONTRACTS = "platform.universal_generator.contracts:GENERATION_CONTRACTS"
OWNER_MEASUREMENT = "platform.universal_generator.registry:default_target_register"


def model(
    model_id: str = "MODEL-TEST",
    *,
    canonical_package: str = OWNER_PACKAGE,
    canonical_contracts: str = OWNER_CONTRACTS,
    subordinates: tuple[SubordinateSurface, ...] = (),
    measurement: str | None = None,
    **overrides,
) -> ConstitutionalModel:
    return ConstitutionalModel(
        model_id=model_id,
        name=overrides.pop("name", "A test model"),
        question=overrides.pop("question", "What answers this?"),
        canonical_package=canonical_package,
        canonical_contracts=SymbolRef.parse(canonical_contracts),
        subordinates=subordinates,
        measurement=SymbolRef.parse(measurement) if measurement else None,
        **overrides,
    )


def subordinate(
    locator: str,
    relation: ConvergenceRelation = ConvergenceRelation.DELEGATES,
    *,
    module: str = "",
    rationale: str = "",
) -> SubordinateSurface:
    return SubordinateSurface(
        locator=locator, relation=relation, module=module, rationale=rationale
    )


def engine(*models: ConstitutionalModel, root: Path | str = ".") -> ConvergenceEngine:
    return ConvergenceEngine(ConvergenceRegister(models or (model(),)), project_root=root)


# ---------------------------------------------------------------------------
# ConvergenceRelation
# ---------------------------------------------------------------------------


def test_a_declared_relation_is_returned_unchanged():
    assert (
        ConvergenceRelation.coerce(ConvergenceRelation.DELEGATES) is ConvergenceRelation.DELEGATES
    )


def test_a_declared_relation_coerces_from_its_value():
    assert ConvergenceRelation.coerce("superseded") is ConvergenceRelation.SUPERSEDED


def test_an_unknown_relation_is_refused_and_names_its_subject():
    with pytest.raises(FoundationConvergenceError) as exc:
        ConvergenceRelation.coerce("tolerates", subject="a/b.py")
    assert "a/b.py" in str(exc.value)


def test_a_non_string_relation_is_refused():
    with pytest.raises(FoundationConvergenceError):
        ConvergenceRelation.coerce(4)


# ---------------------------------------------------------------------------
# SubordinateSurface
# ---------------------------------------------------------------------------


def test_a_subordinate_round_trips_through_its_projection():
    original = subordinate("a/b.py", module="a.b", rationale="why")
    assert SubordinateSurface.from_document(original.to_dict()) == original


def test_a_subordinate_declaration_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConvergenceError) as exc:
        SubordinateSurface.from_document(["a/b.py"])
    assert "must be a mapping" in str(exc.value)


def test_a_subordinate_declaration_missing_a_required_key_names_what_is_missing():
    with pytest.raises(FoundationConvergenceError) as exc:
        SubordinateSurface.from_document({"locator": "a/b.py"})
    assert "relation" in str(exc.value)


def test_a_subordinate_declaration_with_no_locator_is_refused():
    with pytest.raises(FoundationConvergenceError) as exc:
        SubordinateSurface.from_document({"locator": "   ", "relation": "delegates"})
    assert "requires a locator" in str(exc.value)


# ---------------------------------------------------------------------------
# ConstitutionalModel
# ---------------------------------------------------------------------------


def test_a_model_round_trips_through_its_projection():
    original = model(
        "MODEL-A", subordinates=(subordinate("a/b.py"),), measurement=OWNER_MEASUREMENT
    )
    rebuilt = ConstitutionalModel.from_document(original.to_dict())
    assert rebuilt.to_dict() == original.to_dict()
    assert rebuilt.fingerprint() == original.fingerprint()


def test_a_model_declaration_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConvergenceError) as exc:
        ConstitutionalModel.from_document(["MODEL-A"])
    assert "must be a mapping" in str(exc.value)


def test_a_model_declaration_missing_required_keys_names_every_one_of_them():
    with pytest.raises(FoundationConvergenceError) as exc:
        ConstitutionalModel.from_document({"model_id": "MODEL-A"})
    message = str(exc.value)
    assert "question" in message and "canonical_package" in message


def test_two_models_differing_anywhere_fingerprint_differently():
    assert model("MODEL-A").fingerprint() != model("MODEL-B").fingerprint()


# ---------------------------------------------------------------------------
# DuplicationPolicy
# ---------------------------------------------------------------------------


def test_an_absent_duplication_declaration_excludes_nothing():
    policy = DuplicationPolicy.from_document(None)
    assert policy.excluded_segments == ()
    assert policy.exclude_empty_artifacts is False


def test_a_duplication_declaration_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConvergenceError) as exc:
        DuplicationPolicy.from_document(["__pycache__"])
    assert "must be a mapping" in str(exc.value)


@pytest.mark.parametrize("segments", ("__pycache__", b"x", 7))
def test_excluded_segments_that_are_not_a_sequence_are_refused(segments):
    """A bare string would silently exclude every path containing any of its characters."""
    with pytest.raises(FoundationConvergenceError) as exc:
        DuplicationPolicy.from_document({"excluded_segments": segments})
    assert "must be a sequence" in str(exc.value)


def test_a_declared_segment_excludes_the_paths_that_carry_it(tmp_path):
    policy = DuplicationPolicy.from_document({"excluded_segments": ["__pycache__"]})
    cached = tmp_path / "__pycache__" / "a.pyc"
    cached.parent.mkdir()
    cached.write_bytes(b"compiled")
    ordinary = tmp_path / "a.py"
    ordinary.write_bytes(b"source")
    assert not policy.admits(cached)
    assert policy.admits(ordinary)


def test_an_empty_artifact_declares_nothing_and_is_excluded(tmp_path):
    """Two zero-byte files are not two implementations of one model."""
    policy = DuplicationPolicy.from_document({"exclude_empty_artifacts": True})
    blank = tmp_path / "empty.py"
    blank.write_bytes(b"   \n\t ")
    assert not policy.admits(blank)


def test_a_file_that_cannot_be_read_is_not_counted_as_a_duplicate(tmp_path):
    """An unreadable path is not evidence of a copy; it is an absence of evidence."""
    policy = DuplicationPolicy.from_document({"exclude_empty_artifacts": True})
    assert not policy.admits(tmp_path / "does-not-exist.py")


def test_a_policy_that_excludes_no_empty_artifact_admits_one(tmp_path):
    """Exclusion narrows a constitutional measurement, so it applies only when declared."""
    policy = DuplicationPolicy.from_document({"exclude_empty_artifacts": False})
    blank = tmp_path / "empty.py"
    blank.write_bytes(b"")
    assert policy.admits(blank)


def test_the_duplication_policy_projects_what_it_declares():
    payload = DuplicationPolicy.from_document({"excluded_segments": ["b", "a"]}).to_dict()
    assert payload["excluded_segments"] == ["a", "b"]


# ---------------------------------------------------------------------------
# ConvergenceRegister
# ---------------------------------------------------------------------------


def test_only_a_constitutional_model_may_be_declared():
    with pytest.raises(FoundationConvergenceError) as exc:
        ConvergenceRegister().add({"model_id": "MODEL-A"})
    assert "only ConstitutionalModel" in str(exc.value)


def test_declaring_the_same_model_twice_identically_is_idempotent():
    register = ConvergenceRegister([model("MODEL-A")])
    assert register.add(model("MODEL-A")).model_id == "MODEL-A"
    assert register.count == 1


def test_a_model_redeclared_with_a_different_body_is_refused():
    """Two bodies for one model is the second answer the register exists to prevent."""
    register = ConvergenceRegister([model("MODEL-A", name="one")])
    with pytest.raises(FoundationConvergenceError) as exc:
        register.add(model("MODEL-A", name="another"))
    assert "different body" in str(exc.value)


def test_get_reports_an_undeclared_model_as_absent():
    assert ConvergenceRegister().get("MODEL-NOBODY") is None


def test_require_returns_a_declared_model_and_refuses_an_undeclared_one():
    register = ConvergenceRegister([model("MODEL-A")])
    assert register.require("MODEL-A").model_id == "MODEL-A"
    with pytest.raises(FoundationConvergenceError) as exc:
        register.require("MODEL-NOBODY")
    assert "unknown constitutional model" in str(exc.value)


def test_models_are_ordered_by_identity_never_by_insertion():
    register = ConvergenceRegister([model("MODEL-Z"), model("MODEL-A")])
    assert register.ids() == ("MODEL-A", "MODEL-Z")


def test_a_register_with_a_blank_identity_falls_back_to_the_declared_default():
    assert ConvergenceRegister(register_id="  ").register_id == "foundation.convergence"


def test_a_convergence_document_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationConvergenceError) as exc:
        ConvergenceRegister.from_document([])
    assert "must be a mapping" in str(exc.value)


@pytest.mark.parametrize("models", (None, "MODEL-A", 7))
def test_a_convergence_document_without_a_models_sequence_is_refused(models):
    with pytest.raises(FoundationConvergenceError) as exc:
        ConvergenceRegister.from_document({"models": models})
    assert "'models' sequence" in str(exc.value)


def test_a_convergence_document_declaring_no_model_is_refused():
    """An empty register would declare the platform converged by asking nothing of it."""
    with pytest.raises(FoundationConvergenceError) as exc:
        ConvergenceRegister.from_document({"models": []})
    assert "declares no model" in str(exc.value)


def test_a_register_round_trips_through_its_projection():
    original = ConvergenceRegister([model("MODEL-A")], register_id="test.convergence")
    rebuilt = ConvergenceRegister.from_document(original.to_dict())
    assert rebuilt.to_dict() == original.to_dict()
    assert rebuilt.fingerprint() == original.fingerprint()


# ---------------------------------------------------------------------------
# loading the declared register
# ---------------------------------------------------------------------------


def test_the_packaged_catalogue_declares_the_constitutional_models():
    register = default_convergence_register()
    assert catalog_path().name == DEFAULT_CONVERGENCE_FILENAME
    assert register.count > 0


def test_a_register_loaded_from_a_document_matches_one_built_in_memory(tmp_path):
    path = tmp_path / "convergence.json"
    original = ConvergenceRegister([model("MODEL-A")], register_id="test.convergence")
    path.write_text(json.dumps(original.to_dict()), encoding="utf-8")
    assert load_convergence_register(path).to_dict() == original.to_dict()


def test_an_absent_convergence_document_is_a_refusal_naming_the_path(tmp_path):
    missing = tmp_path / "absent.json"
    with pytest.raises(FoundationConvergenceError) as exc:
        load_convergence_register(missing)
    assert str(missing) in str(exc.value)


def test_a_malformed_convergence_document_is_a_refusal(tmp_path):
    path = tmp_path / "convergence.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(FoundationConvergenceError):
        load_convergence_register(path)


# ---------------------------------------------------------------------------
# the engine's composition
# ---------------------------------------------------------------------------


def test_the_engine_requires_a_declared_register():
    with pytest.raises(FoundationConvergenceError) as exc:
        ConvergenceEngine([model()])
    assert "requires a ConvergenceRegister" in str(exc.value)


def test_the_engine_exposes_the_law_and_the_population_it_measures():
    built = engine()
    assert built.register.count == 1
    assert built.constitution.constitution_id == foundation_constitution().constitution_id
    assert "register" in built.to_dict()
    assert built.fingerprint() == engine().fingerprint()


def test_the_engine_reports_the_governed_roots_it_derived_from_the_models():
    """No root is enumerated: the population follows the models."""
    payload = engine().to_dict()
    assert payload["governed_roots"] == ["platform/universal_generator"]


def test_a_model_whose_owner_cannot_be_resolved_contributes_no_governed_root():
    """Reporting one defect twice would be the double-count UFC-16 forbids."""
    built = engine(model("MODEL-A", canonical_package="package.that.does.not.exist"))
    assert built.governed_roots() == ()


def test_two_models_sharing_one_governed_root_are_counted_once():
    built = engine(
        model("MODEL-A", canonical_package=OWNER_PACKAGE),
        model("MODEL-B", canonical_package=f"{OWNER_PACKAGE}.registry"),
    )
    roots = built.governed_roots()
    assert len(roots) == 1
    assert roots[0][1].model_id == "MODEL-A"  # the first model in identity order owns the root


# ---------------------------------------------------------------------------
# subordinate relations — each one really violated
# ---------------------------------------------------------------------------


def test_a_superseded_surface_that_is_gone_stands_in_its_relation(tmp_path):
    built = engine(
        model(subordinates=(subordinate("retired.py", ConvergenceRelation.SUPERSEDED),)),
        root=tmp_path,
    )
    finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
    assert finding.satisfied
    assert "absent" in finding.observed


def test_a_retired_implementation_that_still_exists_is_still_a_second_answer(tmp_path):
    (tmp_path / "retired.py").write_text("VALUE = 1\n", encoding="utf-8")
    built = engine(
        model(subordinates=(subordinate("retired.py", ConvergenceRelation.SUPERSEDED),)),
        root=tmp_path,
    )
    finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
    assert not finding.satisfied
    assert "PRESENT" in finding.observed


def test_a_projection_holding_no_executable_determination_stands_in_its_relation(tmp_path):
    (tmp_path / "derived.md").write_text("# derived\n", encoding="utf-8")
    built = engine(
        model(subordinates=(subordinate("derived.md", ConvergenceRelation.PROJECTION),)),
        root=tmp_path,
    )
    finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
    assert finding.satisfied


def test_a_projection_that_is_executable_may_not_hold_a_determination(tmp_path):
    (tmp_path / "derived.py").write_text("VALUE = 1\n", encoding="utf-8")
    built = engine(
        model(subordinates=(subordinate("derived.py", ConvergenceRelation.PROJECTION),)),
        root=tmp_path,
    )
    finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
    assert not finding.satisfied
    assert "EXECUTABLE" in finding.observed


def test_a_declared_projection_that_does_not_exist_is_reported(tmp_path):
    built = engine(
        model(subordinates=(subordinate("absent.md", ConvergenceRelation.PROJECTION),)),
        root=tmp_path,
    )
    finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
    assert not finding.satisfied
    assert "does not exist" in finding.observed


def test_a_delegating_surface_that_is_absent_cannot_be_verified(tmp_path):
    built = engine(
        model(subordinates=(subordinate("absent.py", ConvergenceRelation.DELEGATES),)),
        root=tmp_path,
    )
    finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
    assert not finding.satisfied
    assert "must exist to be verified" in finding.observed


def test_a_delegating_surface_declaring_no_module_cannot_be_verified(tmp_path):
    (tmp_path / "surface.py").write_text("VALUE = 1\n", encoding="utf-8")
    built = engine(
        model(subordinates=(subordinate("surface.py", ConvergenceRelation.DELEGATES),)),
        root=tmp_path,
    )
    finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
    assert not finding.satisfied
    assert "no module declared" in finding.observed


def test_a_declared_module_that_cannot_be_imported_is_contained_as_a_finding(tmp_path):
    (tmp_path / "surface.py").write_text("VALUE = 1\n", encoding="utf-8")
    built = engine(
        model(
            subordinates=(
                subordinate(
                    "surface.py",
                    ConvergenceRelation.DELEGATES,
                    module="module.that.does.not.exist",
                ),
            )
        ),
        root=tmp_path,
    )
    finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
    assert not finding.satisfied
    assert "could not be imported" in finding.observed


def test_a_module_with_no_filesystem_location_cannot_have_its_delegation_verified(
    tmp_path, monkeypatch
):
    """A namespace package has no source, so nothing can prove it reaches the owner."""
    import sys

    namespace = tmp_path / "convergence_namespace"
    namespace.mkdir()
    (tmp_path / "surface.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    try:
        built = engine(
            model(
                subordinates=(
                    subordinate(
                        "surface.py",
                        ConvergenceRelation.DELEGATES,
                        module="convergence_namespace",
                    ),
                )
            ),
            root=tmp_path,
        )
        finding = built.measure_model(built.register.require("MODEL-TEST")).findings[0]
        assert not finding.satisfied
        assert "no filesystem location" in finding.observed
    finally:
        sys.modules.pop("convergence_namespace", None)


# ---------------------------------------------------------------------------
# model measurement
# ---------------------------------------------------------------------------


def test_a_model_whose_canonical_owner_does_not_resolve_is_not_converged():
    measured = engine().measure_model(model("MODEL-A", canonical_package="nowhere.at.all"))
    assert not measured.owner_resolved
    assert not measured.converged
    assert "does not resolve" in measured.detail


def test_a_model_whose_owner_publishes_no_contract_surface_is_not_converged():
    """An owner with no published contract is an owner nobody can bind to."""
    measured = engine().measure_model(
        model("MODEL-A", canonical_contracts=f"{OWNER_PACKAGE}.contracts:UNG_ID")
    )
    assert measured.owner_resolved
    assert measured.contract_count == 0
    assert not measured.converged
    assert measured.detail == "the canonical owner publishes no contract surface"


def test_a_model_with_a_reproducible_canonical_measurement_is_converged():
    measured = engine().measure_model(model("MODEL-A", measurement=OWNER_MEASUREMENT))
    assert measured.measurement_stable is True
    assert measured.measurement_fingerprint
    assert measured.converged


def test_a_canonical_measurement_that_does_not_reproduce_is_not_converged():
    """Two builds that disagree mean the model has no single answer to reproduce."""
    measured = engine().measure_model(
        model(
            "MODEL-A",
            measurement="platform.tests.test_universal_foundation_convergence:_drifting_build",
        )
    )
    assert measured.measurement_stable is False
    assert not measured.converged
    assert measured.detail == "the canonical measurement is not reproducible"


def test_a_canonical_measurement_that_cannot_be_taken_is_contained(monkeypatch):
    measured = engine().measure_model(
        model(
            "MODEL-A",
            measurement="platform.tests.test_universal_foundation_convergence:_raising_build",
        )
    )
    assert measured.measurement_stable is False
    assert not measured.converged
    assert "could not be taken" in measured.detail


class _Drifting:
    def __init__(self, value: int) -> None:
        self._value = value

    def fingerprint(self) -> str:
        return f"fp-{self._value}"


_DRIFT = [0]


def _drifting_build() -> _Drifting:
    """A canonical measurement that never reproduces — used as a declared measurement."""
    _DRIFT[0] += 1
    return _Drifting(_DRIFT[0])


def _raising_build() -> None:
    """A canonical measurement that cannot be taken at all."""
    raise RuntimeError("the measurement instrument is broken")


# ---------------------------------------------------------------------------
# duplication
# ---------------------------------------------------------------------------


def test_identical_content_is_found_because_it_is_a_copy_not_because_it_is_named_like_one(
    tmp_path,
):
    package = tmp_path / "dupe_specimen"
    package.mkdir()
    (package / "__init__.py").write_text('"""A specimen."""\n', encoding="utf-8")
    (package / "original.py").write_text("VALUE = 1\n", encoding="utf-8")
    (package / "moved_elsewhere.py").write_text("VALUE = 1\n", encoding="utf-8")
    (package / "different.py").write_text("VALUE = 2\n", encoding="utf-8")
    import sys

    sys.path.insert(0, str(tmp_path))
    try:
        built = ConvergenceEngine(
            ConvergenceRegister(
                [
                    model(
                        "MODEL-A",
                        canonical_package="dupe_specimen",
                        canonical_contracts=OWNER_CONTRACTS,
                    )
                ],
                duplication=DuplicationPolicy.from_document(
                    {"excluded_segments": ["__pycache__"], "exclude_empty_artifacts": True}
                ),
            ),
            project_root=tmp_path,
        )
        groups = built.measure_duplication()
        assert len(groups) == 1
        assert set(groups[0].locators) == {
            "dupe_specimen/moved_elsewhere.py",
            "dupe_specimen/original.py",
        }
        assert groups[0].surplus == 1
        assert groups[0].model_id == "MODEL-A"
    finally:
        sys.path.remove(str(tmp_path))
        sys.modules.pop("dupe_specimen", None)


# ---------------------------------------------------------------------------
# the whole determination
# ---------------------------------------------------------------------------


def test_the_repository_measures_its_own_models_as_converged():
    """The repository's real reading, asserted as one rather than assumed."""
    determination = bootstrap_convergence().measure()
    assert determination.converged
    assert determination.duplicates == 0
    assert determination.blockers() == ()
    assert all(item.verdict is Verdict.PASS for item in determination.gate_results)


def test_the_full_projection_carries_the_per_subordinate_detail_the_summary_drops():
    determination = bootstrap_convergence().measure()
    full = determination.to_dict()
    compact = determination.summary()
    assert "findings" in full["models"][0]
    assert "findings" not in compact["models"][0]
    assert full["determination_id"] == compact["determination_id"]
    assert full["counts"] == compact["counts"]


def test_a_determination_fingerprints_over_the_facts_it_asserts():
    """Two measurements of an unchanged repository must be comparable by one value."""
    first = bootstrap_convergence().measure()
    second = bootstrap_convergence().measure()
    assert first.fingerprint() == second.fingerprint()
    assert first.determination_id == second.determination_id
    assert first.fingerprint() != engine(model("MODEL-A")).measure().fingerprint()


def test_the_determination_resolves_a_model_by_identity_and_refuses_an_unknown_one():
    determination = bootstrap_convergence().measure()
    first = determination.models[0]
    assert determination.model(first.model_id) is first
    with pytest.raises(FoundationConvergenceError) as exc:
        determination.model("MODEL-NOBODY")
    assert "unknown constitutional model" in str(exc.value)


def test_a_duplicate_group_states_the_surplus_and_the_disposition_it_requires():
    group = DuplicateGroup(
        digest="a" * 64,
        locators=("pkg/one.py", "pkg/two.py", "pkg/three.py"),
        governed_root="pkg",
        model_id="MODEL-A",
        canonical_package="pkg",
    )
    assert group.surplus == 2
    assert "remove the 2 surplus artifact(s)" in group.remediation
    payload = group.to_dict()
    assert payload["surplus"] == 2
    assert payload["locators"] == list(group.locators)
    described = group.describe()
    assert "3 byte-identical" in described
    assert "pkg/one.py == pkg/two.py == pkg/three.py" in described


def test_a_locator_outside_the_project_root_is_reported_absolutely(tmp_path):
    """A governed root that is not under the project is still named, not silently dropped."""
    built = engine(root=tmp_path)
    outside = Path("/") / "somewhere" / "else.py"
    assert built._relative(outside) == outside.as_posix()


def test_a_governed_root_with_no_filesystem_location_is_omitted(tmp_path, monkeypatch):
    import sys

    namespace = tmp_path / "convergence_root_namespace"
    namespace.mkdir()
    monkeypatch.syspath_prepend(str(tmp_path))
    try:
        built = engine(
            model("MODEL-A", canonical_package="convergence_root_namespace"), root=tmp_path
        )
        assert built.governed_roots() == ()
    finally:
        sys.modules.pop("convergence_root_namespace", None)


def test_a_model_with_no_declared_measurement_withholds_the_one_measurement_gate():
    """A model nobody can measure reproducibly has no verified single answer."""
    determination = engine(model("MODEL-A")).measure()
    gate = next(item for item in determination.gate_results if "MEASUREMENT" in item.gate)
    assert gate.verdict is Verdict.FAIL
    assert any("declares no canonical measurement" in finding for finding in gate.findings)


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------


def test_bootstrapping_with_nothing_composes_the_packaged_declaration():
    assert bootstrap_convergence().register.to_dict() == default_convergence_register().to_dict()


def test_bootstrapping_accepts_an_already_built_register():
    register = ConvergenceRegister([model("MODEL-A")])
    assert bootstrap_convergence(register).register is register


def test_bootstrapping_accepts_a_path_to_a_declared_document(tmp_path):
    path = tmp_path / "convergence.json"
    path.write_text(json.dumps(ConvergenceRegister([model("MODEL-A")]).to_dict()), encoding="utf-8")
    assert bootstrap_convergence(path).register.ids() == ("MODEL-A",)
