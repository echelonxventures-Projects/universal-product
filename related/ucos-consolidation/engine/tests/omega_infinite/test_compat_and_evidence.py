"""Deliverable 7 and the five success criteria — backwards compatibility, proved by equivalence.

THE CENTRAL TEST IS ``test_the_abstraction_reproduces_the_omega_1_population_exactly``. It runs over
the REAL repository, because that is the only population that matters for the compatibility claim: a
synthetic tree would prove the code composes, not that Phase 1 changed nothing.

TUPLE EQUALITY, NOT SET EQUALITY. Order is part of the claim. A set comparison would pass for a
population that happened to contain the same files in a different sequence, and every downstream
digest in UCOS-OMEGA-001 is computed over an ordered structure.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.omega_infinite import compat, evidence
from engine.omega_infinite.artifact import PYTHON, UNKNOWN
from engine.omega_infinite.provider import Selector
from engine.universal_discovery import discovery

REPO = str(Path(__file__).resolve().parents[3])


# ------------------------------------------------------------------- Deliverable 7: equivalence


def test_the_abstraction_reproduces_the_omega_1_population_exactly() -> None:
    """PHASE 1 REPLACES NOTHING, discharged over the real repository.

    If this ever fails, the abstraction is not a generalisation of Ω-1 — it is a SECOND population,
    and this repository has already paid for four of those.
    """
    measured = compat.equivalence(REPO)
    assert measured.identical
    assert measured.only_in_legacy == ()
    assert measured.only_in_abstraction == ()
    assert len(measured.legacy) > 2000


def test_the_two_mechanisms_agree_on_a_synthetic_tree_too(tracked_tree: Path) -> None:
    """The same property over a tree whose contents this suite controls."""
    measured = compat.equivalence(str(tracked_tree))
    assert measured.identical
    assert measured.legacy == ("src/module.py", "src/nested/deep.py")


def test_the_relocated_python_filter_is_data_rather_than_a_literal() -> None:
    """The Ω-1 assumption did not disappear; it became an argument with a name and a test."""
    assert compat.PYTHON_ONLY == Selector(patterns=("*.py",))
    assert compat.PYTHON_ONLY.patterns == ("*.py",)


def test_a_different_selector_changes_the_population_with_no_code_change(
    tracked_tree: Path,
) -> None:
    """THE WHOLE OF PHASE 1 IN ONE ASSERTION. In Ω-1 this required editing an argv list."""
    from engine.omega_infinite.knowledge_space import repository_space

    space = repository_space(str(tracked_tree))
    assert space.discover(Selector(patterns=("*.md",))).locators() == ("docs/guide.md",)
    assert space.discover(compat.PYTHON_ONLY).locators() == (
        "src/module.py",
        "src/nested/deep.py",
    )


def test_equivalence_reports_divergence_in_both_directions() -> None:
    """A one-directional check is satisfied by a subset, which would hide over-collection."""
    diverged = compat.Equivalence(("a.py", "b.py"), ("b.py", "c.py"))
    assert not diverged.identical
    assert diverged.only_in_legacy == ("a.py",)
    assert diverged.only_in_abstraction == ("c.py",)
    assert "DIVERGED" in diverged.summary()

    ordered_differently = compat.Equivalence(("a.py", "b.py"), ("b.py", "a.py"))
    assert not ordered_differently.identical
    assert ordered_differently.only_in_legacy == ()


def test_the_equivalence_record_names_both_mechanisms(tracked_tree: Path) -> None:
    record = compat.equivalence(str(tracked_tree)).as_record()
    assert record["legacy_mechanism"] == "engine.universal_discovery.discovery.tracked_python"
    assert "Selector" in str(record["abstracted_mechanism"])
    assert record["identical"] is True
    assert "IDENTICAL" in compat.equivalence(str(tracked_tree)).summary()


def test_the_existing_omega_1_entry_points_are_untouched() -> None:
    """Additive means additive: Ω-1's own primitives must still answer as they always did."""
    paths = discovery.tracked_python(REPO)
    assert all(p.endswith(".py") for p in paths)
    assert paths == tuple(sorted(paths))
    assert "engine/universal_discovery/discovery.py" in paths


# ---------------------------------------------------------------------------------- the adapter


def test_a_legacy_artifact_lifts_into_the_universal_model_losing_nothing() -> None:
    """DELIVERABLE 3: PYTHON becomes a TYPE and the four Python fields become metadata."""
    from engine.universal_discovery.model import Artifact as LegacyArtifact

    legacy = LegacyArtifact(
        path="engine/foundation/identity.py",
        root="engine",
        module="engine.foundation.identity",
        disposition="MEASURED",
        disposition_rule="Ω-C-04",
        disposition_reason="the derived coverage denominator names its package",
        authority="engine.foundation",
        authority_rule="Ω-A-06",
        reachable=True,
        reached_by=("import", "test"),
        statements=42,
        callables=7,
        imports=3,
    )
    lifted = compat.as_universal(legacy)

    assert lifted.artifact_type is PYTHON
    assert lifted.identifier == "git:engine/foundation/identity.py"
    assert lifted.location.provider == "git"
    assert lifted.authority.owner == "engine.foundation"
    assert lifted.authority.rule == "Ω-A-06"
    # every Python-specific measurement survived as metadata, not as structure
    assert lifted.metadata["python_statements"] == "42"
    assert lifted.metadata["python_callables"] == "7"
    assert lifted.metadata["python_imports"] == "3"
    assert lifted.metadata["python_module"] == "engine.foundation.identity"
    assert lifted.metadata["omega_disposition"] == "MEASURED"
    assert lifted.metadata["omega_reachable"] == "true"


def test_lifting_something_with_no_path_is_a_fault() -> None:
    with pytest.raises(ValueError, match="no path"):
        compat.as_universal(object())


# --------------------------------------------------------------------------- the five criteria


@pytest.fixture(scope="module")
def built() -> evidence.Evidence:
    """Built once: the real-repository evidence run costs a full `git ls-files` and a comparison."""
    return evidence.build(REPO)


def test_all_five_phase_1_criteria_hold(built: evidence.Evidence) -> None:
    assert built.passed, [c.as_record() for c in built.failures()]
    assert [c.identifier for c in built.criteria] == ["Ω∞-1", "Ω∞-2", "Ω∞-3", "Ω∞-4", "Ω∞-5"]


def test_every_criterion_carries_an_observation_a_reader_can_check(
    built: evidence.Evidence,
) -> None:
    """A criterion whose verdict is not accompanied by what was measured is an assertion."""
    for criterion in built.criteria:
        assert criterion.claim
        assert len(criterion.observation) > 60


def test_the_evidence_is_deterministic_and_machine_independent(built: evidence.Evidence) -> None:
    """No wall clock, no working-tree status, and NO ABSOLUTE PATHS.

    The last one is the property that makes the document comparable at all: an evidence document
    carrying ``/Users/<somebody>/...`` differs between two machines measuring the same tree, and a
    document that cannot be compared is not evidence. The binding is redacted to ``<root>`` rather
    than stripped, so a reader can see that a redaction happened.
    """
    again = evidence.build(REPO)
    assert built.digest() == again.digest()

    document = json.dumps(built.as_document(), sort_keys=True)
    assert REPO not in document
    assert evidence.SPACE_PLACEHOLDER in document
    assert built.space.space == evidence.SPACE_PLACEHOLDER

    binding = built.registry["providers"][0]["metadata"]["binding"]  # type: ignore[index]
    assert binding == evidence.SPACE_PLACEHOLDER


def test_the_provider_itself_still_reports_its_real_binding(tracked_tree: Path) -> None:
    """Redaction is a property of the DOCUMENT, not of the provider. A provider that misreported
    where it is pointed would be useless to an operator debugging a resolution."""
    from engine.omega_infinite.git_provider import GitDiscoveryProvider

    assert GitDiscoveryProvider(str(tracked_tree)).metadata().binding == str(tracked_tree)


def test_a_relative_root_is_redacted_too(
    tracked_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tracked_tree)
    built = evidence.build(".", compare=False)
    binding = built.registry["providers"][0]["metadata"]["binding"]  # type: ignore[index]
    assert binding == evidence.SPACE_PLACEHOLDER
    assert str(tracked_tree) not in json.dumps(built.as_document())


def test_the_evidence_document_carries_the_capability_matrix(built: evidence.Evidence) -> None:
    matrix = built.registry["capability_matrix"]
    assert matrix == {
        "git": [
            "AUTHORITY_METADATA",
            "CHANGE_SET",
            "CONTENT_HASHING",
            "LOCAL_STORAGE",
            "REVISION_HISTORY",
            "REVISION_IDENTITY",
            "REVISION_METADATA",
            "TRACKED_CONTENT",
            "VERSIONED_CONTENT",
            "WORKING_TREE_STATE",
        ]
    }


def test_the_document_reports_the_open_vocabulary(built: evidence.Evidence) -> None:
    vocabulary = built.vocabulary
    assert "PYTHON" in vocabulary["artifact_types"]  # type: ignore[operator]
    assert "TRACKED_CONTENT" in vocabulary["capabilities"]  # type: ignore[operator]
    assert vocabulary["classifiers"] == [
        "provider-declared",
        "content-interpreter",
        "content-structure",
        "suffix",
    ]


def test_the_expansion_probe_registers_things_this_package_never_named() -> None:
    """Ω∞-5 IS THE LOAD-BEARING CRITERION. The first four could be satisfied by a well-factored
    special case; this one registers a capability, a type, a kind and a provider at runtime."""
    from engine.omega_infinite import capability as capability_module
    from engine.omega_infinite import knowledge_space as space_module

    criterion = evidence.expansion_probe()
    assert criterion.holds
    assert "STREAMING_CONTENT" not in capability_module.REGISTRY
    assert "STREAM" not in {k.name for k in space_module.KINDS}


def test_the_expansion_probe_is_idempotent_across_runs() -> None:
    """It declares a type into the process-wide registry, so repeated runs must not conflict."""
    assert evidence.expansion_probe().holds
    assert evidence.expansion_probe().holds


def test_the_git_optional_criterion_runs_without_version_control(untracked_tree: Path) -> None:
    """Ω∞-2 over a tree that has never been a repository."""
    criterion = evidence.git_optional_probe(str(untracked_tree))
    assert criterion.holds
    assert "no git, hg, svn or p4" in criterion.observation


def test_a_criterion_can_fail_and_the_document_says_so() -> None:
    """A criterion set that could not report a failure would be decorative."""
    failing = evidence.Criterion("Ω∞-X", "a claim", False, "an observation that did not hold")
    document = evidence.Evidence(
        space=evidence.knowledge_space.filesystem_space(REPO, "<root>").discover(
            Selector(patterns=("pyproject.toml",))
        ),
        criteria=(failing,),
        registry={"capability_matrix": {}},
        equivalence=None,
        vocabulary=evidence.vocabulary_report(),
    )
    assert not document.passed
    assert document.failures() == (failing,)
    assert "REFUSED" in evidence.render(document)
    assert "not measured" in evidence.render(document)


def test_the_report_renders_every_section(built: evidence.Evidence) -> None:
    rendered = evidence.render(built)
    for heading in (
        "SUCCESS CRITERIA",
        "KNOWLEDGE SPACE",
        "PROVIDER CAPABILITY MATRIX",
        "BACKWARDS COMPATIBILITY",
        "VOCABULARY",
    ):
        assert heading in rendered
    assert "PASS — all five Phase 1 criteria hold" in rendered
    assert "No certification issued" in rendered


def test_evidence_can_skip_the_comparison(tracked_tree: Path) -> None:
    built = evidence.build(str(tracked_tree), compare=False)
    assert built.equivalence is None
    assert built.as_document()["backwards_compatibility"] is None


def test_untyped_artifacts_are_a_countable_population(untracked_tree: Path) -> None:
    """Phase 2's target has to be measurable in Phase 1."""
    from engine.omega_infinite.classification import default_pipeline, unknown_population
    from engine.omega_infinite.filesystem_provider import FilesystemDiscoveryProvider

    provider = FilesystemDiscoveryProvider(str(untracked_tree))
    typed = default_pipeline().apply_all(
        provider.enumerate(), lambda a: provider.read(a.location.locator)
    )
    unknown = unknown_population(typed)
    assert all(a.artifact_type is UNKNOWN for a in unknown)
    assert "bin/opaque-blob" in [a.location.locator for a in unknown]


# --------------------------------------------------------------------------------------- the CLI


def test_the_cli_reports_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    from engine.omega_infinite import __main__ as cli

    assert cli.main(["--root", REPO]) == 0
    assert "PHASE 1" in capsys.readouterr().out


def test_the_cli_emits_a_json_document(capsys: pytest.CaptureFixture[str]) -> None:
    from engine.omega_infinite import __main__ as cli

    assert cli.main(["--root", REPO, "--json", "--no-compare"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["schema"] == evidence.SCHEMA
    assert document["passed"] is True
    assert len(document["criteria"]) == 5


def test_the_cli_prints_the_provider_matrix(capsys: pytest.CaptureFixture[str]) -> None:
    from engine.omega_infinite import __main__ as cli

    assert cli.main(["--root", REPO, "--providers", "--no-compare"]) == 0
    assert "capability_matrix" in json.loads(capsys.readouterr().out)


def test_the_cli_separates_could_not_run_from_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exit 2 is distinct on purpose: collapsing it into 1 would let a broken layer read as a
    governance failure."""
    from engine.omega_infinite import __main__ as cli

    assert cli.main(["--root", str(tmp_path / "absent")]) == 2
    assert "could not run" in capsys.readouterr().err


def test_the_cli_writes_nothing_anywhere(tmp_path: Path) -> None:
    """The directive forbids sealing and certification, so the CLI has no writing mode at all."""
    from engine.omega_infinite import __main__ as cli

    before = sorted(p.name for p in tmp_path.iterdir())
    assert cli.main(["--root", REPO, "--no-compare", "--json"]) == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == before
    assert "--seal" not in cli.build_parser().format_help()


def test_a_binding_that_is_not_a_path_is_left_alone_by_redaction() -> None:
    """Redaction rewrites a PREFIX MATCH and nothing else. A provider bound to ``s3://bucket``
    must pass through untouched, or the document would misreport where it looked."""
    entry = {
        "identifier": "synthetic-stream",
        "metadata": {"binding": "synthetic://phase1-expansion-probe", "identifier": "x"},
    }
    redacted = evidence._redact_binding(dict(entry), (REPO, "."))
    assert redacted["metadata"]["binding"] == "synthetic://phase1-expansion-probe"  # type: ignore[index]

    missing = evidence._redact_binding({"identifier": "bare"}, (REPO,))
    assert missing["metadata"]["binding"] == ""  # type: ignore[index]


def test_the_synthetic_expansion_provider_self_describes_like_any_other() -> None:
    """The Ω∞-5 probe provider must satisfy the same contract as git and the filesystem — otherwise
    the expansion claim rests on a provider that is exempt from the rules it demonstrates."""
    from engine.omega_infinite.capability import CapabilitySet
    from engine.omega_infinite.provider import DiscoveryProvider, ProviderRegistry

    provider = evidence._SyntheticProvider("probe", CapabilitySet())
    assert isinstance(provider, DiscoveryProvider)

    metadata = provider.metadata()
    assert metadata.identifier == "probe"
    assert metadata.binding.startswith("synthetic://")
    assert metadata.revision == ""

    report = ProviderRegistry((provider,)).report()
    assert report["capability_matrix"] == {"probe": []}
