"""Deliverable 3 — the universal Artifact, and the Python fields it must NOT have.

THE STRONGEST TEST HERE IS ``test_the_model_carries_no_language_specific_field``. Everything else
checks that the six-part shape works; that one checks the abstraction is real. Ω-1's model carries
``module``, ``statements``, ``callables`` and ``imports`` as structure, and those four fields are
the reason it can describe nothing but Python.
"""

from __future__ import annotations

import pytest

from engine.omega_infinite import artifact as artifact_module
from engine.omega_infinite.artifact import (
    AUTHORITY_UNRESOLVED,
    DEPENDS_ON,
    DESCRIBES,
    DOCUMENT,
    PYTHON,
    UNKNOWN,
    Artifact,
    ArtifactError,
    ArtifactType,
    ArtifactTypeRegistry,
    Authority,
    Location,
    Relationship,
)


def _artifact(**changes: object) -> Artifact:
    base: dict[str, object] = {
        "identifier": "git:src/module.py",
        "location": Location("git", "src/module.py"),
    }
    base.update(changes)
    return Artifact(**base)  # type: ignore[arg-type]


# -------------------------------------------------------------------------------- the shape


def test_the_model_carries_no_language_specific_field() -> None:
    """RULE Ω-1, ASSERTED STRUCTURALLY. No Python measurement may be a field of the universal model.

    If this test ever fails, the abstraction has been re-specialised and Phase 1 has been undone.
    """
    fields = set(Artifact.__dataclass_fields__)
    assert fields == {
        "identifier",
        "location",
        "artifact_type",
        "authority",
        "metadata",
        "relationships",
        "classification_rule",
    }
    assert not fields & {"module", "statements", "callables", "imports", "path", "root"}


def test_the_six_directive_parts_are_all_present() -> None:
    """identifier, location, type, authority, metadata, relationships — the Deliverable 3 list."""
    built = _artifact(
        artifact_type=DOCUMENT,
        classification_rule="Ω∞-T-04",
        authority=Authority("UCOS-OMEGA-001", "Ω-A-03"),
        metadata={"tracked": "true"},
        relationships=(Relationship(DESCRIBES, "git:docs/guide.md"),),
    )
    assert built.identifier == "git:src/module.py"
    assert built.location.provider == "git"
    assert built.artifact_type is DOCUMENT
    assert built.authority.owner == "UCOS-OMEGA-001"
    assert built.metadata["tracked"] == "true"
    assert built.relationships[0].kind == DESCRIBES


def test_an_artifact_with_no_identifier_is_a_fault() -> None:
    with pytest.raises(ArtifactError, match="no identifier"):
        _artifact(identifier="  ")


def test_an_unclassified_artifact_defaults_to_unknown_rather_than_to_python() -> None:
    """UNKNOWN is a NAMED population. Defaulting to PYTHON is the assumption Phase 1 removes."""
    built = _artifact()
    assert built.artifact_type is UNKNOWN
    assert not built.typed
    assert built.classification_rule == ""


# ------------------------------------------------------------------------------------ location


def test_a_location_must_name_its_provider_and_locator() -> None:
    with pytest.raises(ArtifactError, match="name the provider"):
        Location("", "src/module.py")
    with pytest.raises(ArtifactError, match="carry a locator"):
        Location("git", "  ")


def test_the_provider_is_part_of_the_location_identity() -> None:
    """Two providers may hand back the same locator and mean different bytes. A federation that
    keyed on the locator alone would silently merge them."""
    assert Location("git", "config.toml") != Location("filesystem", "config.toml")
    assert str(Location("git", "config.toml")) == "git:config.toml"


def test_an_absent_revision_is_omitted_rather_than_faked() -> None:
    assert "revision" not in Location("filesystem", "a").as_record()
    assert Location("git", "a", "abc123").as_record()["revision"] == "abc123"


# ----------------------------------------------------------------------------------- authority


def test_an_unresolved_authority_is_a_distinct_state_from_an_empty_one() -> None:
    assert not Authority().resolved
    assert Authority().owner == AUTHORITY_UNRESOLVED
    assert not Authority("").resolved
    assert Authority("UCOS-OMEGA-001", "Ω-A-03").resolved


# -------------------------------------------------------------------------------- relationships


def test_a_relationship_must_declare_a_kind_and_a_target() -> None:
    with pytest.raises(ArtifactError, match="declare its kind"):
        Relationship("", "git:a")
    with pytest.raises(ArtifactError, match="name the identifier"):
        Relationship(DEPENDS_ON, "")


def test_relationships_target_identifiers_so_edges_can_cross_providers() -> None:
    built = _artifact(
        relationships=(
            Relationship(DEPENDS_ON, "s3://evidence/report.json"),
            Relationship(DESCRIBES, "git:docs/guide.md"),
        )
    )
    assert built.related(DEPENDS_ON) == ("s3://evidence/report.json",)
    assert built.related("NO_SUCH_KIND") == ()


# ---------------------------------------------------------------------------------- determinism


def test_metadata_and_relationships_are_normalised_for_deterministic_bytes() -> None:
    """Two artifacts built from the same facts in a different ORDER must be equal and serialise
    identically, or the evidence document's byte-comparison flaps for an ungoverned reason."""
    first = _artifact(
        metadata={"b": "2", "a": "1"},
        relationships=(Relationship(DESCRIBES, "z"), Relationship(DEPENDS_ON, "a")),
    )
    second = _artifact(
        metadata={"a": "1", "b": "2"},
        relationships=(Relationship(DEPENDS_ON, "a"), Relationship(DESCRIBES, "z")),
    )
    assert first == second
    assert first.as_record() == second.as_record()
    assert list(first.metadata) == ["a", "b"]


def test_the_record_is_fully_expanded_for_a_reader() -> None:
    record = _artifact(
        artifact_type=PYTHON,
        classification_rule="Ω∞-T-04",
        authority=Authority("UCOS-REPOSITORY-ROOT::python", "Ω-A-04"),
    ).as_record()
    assert record["type"] == "PYTHON"
    assert record["classification_rule"] == "Ω∞-T-04"
    assert record["authority"] == {"owner": "UCOS-REPOSITORY-ROOT::python", "rule": "Ω-A-04"}
    assert record["location"] == {"provider": "git", "locator": "src/module.py"}


# ------------------------------------------------------------------------- non-mutating copies


def test_with_type_requires_the_rule_that_produced_the_type() -> None:
    """A type with no rule cannot be argued with, which is the defect Ω-5 exists to end."""
    with pytest.raises(ArtifactError, match="without naming the rule"):
        _artifact().with_type(PYTHON, "  ")


def test_the_derived_copies_preserve_every_other_field() -> None:
    """``_replace`` is the single construction point so no field is dropped by omission."""
    original = _artifact(
        metadata={"tracked": "true"},
        relationships=(Relationship(DESCRIBES, "git:docs/guide.md"),),
        authority=Authority("OWNER", "Ω-A-01"),
    )
    typed = original.with_type(PYTHON, "Ω∞-T-04")
    assert typed.metadata == original.metadata
    assert typed.relationships == original.relationships
    assert typed.authority == original.authority
    assert typed.artifact_type is PYTHON
    # the original is untouched
    assert original.artifact_type is UNKNOWN


def test_with_metadata_merges_and_with_relationships_appends() -> None:
    built = (
        _artifact(metadata={"tracked": "true"})
        .with_metadata(extra="1")
        .with_relationships(Relationship(DEPENDS_ON, "git:src/other.py"))
        .with_authority(Authority("OWNER", "Ω-A-01"))
    )
    assert built.metadata == {"extra": "1", "tracked": "true"}
    assert built.related(DEPENDS_ON) == ("git:src/other.py",)
    assert built.authority.owner == "OWNER"


# --------------------------------------------------------------------------------- type registry


def test_an_artifact_type_must_be_named() -> None:
    with pytest.raises(ArtifactError, match="must have a name"):
        ArtifactType(" ")


def test_the_registry_seeds_the_six_initial_types() -> None:
    registry = ArtifactTypeRegistry()
    assert {t.name for t in registry.known()} == {
        "CONFIGURATION",
        "DATASET",
        "DOCUMENT",
        "PYTHON",
        "UNKNOWN",
        "WORKFLOW",
    }
    assert "PYTHON" in registry
    assert len(registry) == 6


def test_a_seventh_type_is_a_registration_and_not_a_code_change() -> None:
    """DELIVERABLE 3's 'unlimited future expansion', discharged."""
    registry = ArtifactTypeRegistry()
    added = registry.declare_name("SCHEMA", "A structural contract.")
    assert registry.resolve("SCHEMA") is added
    assert len(registry) == 7
    assert "SCHEMA" not in {t.name for t in artifact_module.INITIAL_TYPES}


def test_redeclaring_a_type_with_a_different_meaning_is_refused() -> None:
    registry = ArtifactTypeRegistry()
    assert registry.declare(ArtifactType("PYTHON", PYTHON.description)) == PYTHON
    with pytest.raises(ArtifactError, match="different meaning"):
        registry.declare(ArtifactType("PYTHON", "a snake"))


def test_an_unknown_type_name_raises_rather_than_becoming_a_new_type() -> None:
    with pytest.raises(ArtifactError, match="not a declared artifact type"):
        ArtifactTypeRegistry().resolve("PYTHN")


def test_a_type_renders_as_its_name() -> None:
    assert str(PYTHON) == "PYTHON"
