"""Repository Provider tests (Terminal-04, the reference implementation).

The framework suite deliberately exercises an invented in-memory provider, because
the architecture's claim is that the framework is indifferent to which provider it is
handed (``universal_provider_helpers``). That is why nothing tested this module: the
one place the framework must *not* look is the only place the reference implementation
lives. So these tests attack the provider's own claims rather than the framework's —
that its declared surface matches the manifest the framework actually binds to, that
its substrate containment holds against a crafted resource id, and that its index is
bounded and deterministic.

The substrate is a ``tmp_path`` tree wherever the assertion is about behaviour, so no
test depends on what happens to be checked into the repository today. The two tests
that *are* about the repository — the entry point resolving and the manifest matching
the code — read the real files, because their whole subject is that those files agree.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
from platform.providers import CATALOG_DIR, TEMPLATE_MANIFEST
from platform.providers.repository.provider import (
    ARTIFACT_KIND,
    CAPABILITY_ARTIFACT,
    CAPABILITY_ARTIFACTS,
    CAPABILITY_ATTESTATION,
    DEFAULT_PATTERNS,
    MAX_INDEXED_ARTIFACTS,
    REPOSITORY_PROVIDER_ID,
    REPOSITORY_PROVIDER_KIND,
    REPOSITORY_PROVIDER_VERSION,
    RepositoryProvider,
    build,
    repository_capabilities,
    repository_descriptor,
    repository_root,
)
from platform.universal_provider.constitution import ProviderOperation
from platform.universal_provider.contracts import ProviderQuery
from platform.universal_provider.errors import (
    ProviderCapabilityError,
    ProviderExecutionError,
)

import pytest


@pytest.fixture
def substrate(tmp_path: Path) -> Path:
    """A small, deterministic working tree: three markdown files and one decoy."""
    (tmp_path / "alpha.md").write_text("# alpha\n")
    (tmp_path / "beta.md").write_text("# beta\n")
    (tmp_path / "gamma-note.md").write_text("# gamma\n")
    (tmp_path / "ignored.txt").write_text("not matched by the default pattern\n")
    return tmp_path


@pytest.fixture
def provider(substrate: Path) -> RepositoryProvider:
    return build(repository_descriptor(), {"root": str(substrate)})


def _query(capability: str = CAPABILITY_ARTIFACTS, **selector: object) -> ProviderQuery:
    return ProviderQuery(capability=capability, selector=dict(selector))


# --- the declared surface -------------------------------------------------------


def test_the_declared_capabilities_are_three_and_read_only():
    """PC-08: the provider's sole declared effect is fs:read; it never writes."""
    capabilities = repository_capabilities()
    assert len(capabilities) == 3
    assert {c.name for c in capabilities} == {
        CAPABILITY_ARTIFACTS,
        CAPABILITY_ARTIFACT,
        CAPABILITY_ATTESTATION,
    }
    for capability in capabilities:
        assert capability.resource_kind == ARTIFACT_KIND
        assert capability.deterministic
        assert tuple(capability.effects) == ("fs:read",)


def test_each_capability_is_bound_to_the_operation_its_name_promises():
    by_name = {c.name: c for c in repository_capabilities()}
    assert by_name[CAPABILITY_ARTIFACTS].operation is ProviderOperation.QUERY
    assert by_name[CAPABILITY_ARTIFACT].operation is ProviderOperation.FETCH
    assert by_name[CAPABILITY_ATTESTATION].operation is ProviderOperation.VERIFY


def test_the_code_descriptor_and_the_catalog_manifest_do_not_diverge():
    """The docstring says the two are kept apart so they can be diffed. Diff them.

    The framework binds to the manifest and gate PV-11-CERTIFIABLE refuses a
    divergence, so a drift between these two files is a certification failure that
    would otherwise only surface at validation time.
    """
    manifest = json.loads((CATALOG_DIR / "repository.json").read_text())
    descriptor = repository_descriptor()

    assert manifest["identity"] == {
        "provider_id": descriptor.identity.provider_id,
        "kind": descriptor.identity.kind,
        "version": descriptor.identity.version,
        "name": descriptor.identity.name,
        "authority": descriptor.identity.authority,
    }
    assert manifest["interface"] == descriptor.interface
    assert manifest["interface_version"] == descriptor.interface_version
    assert manifest["entry_point"] == descriptor.entry_point
    assert manifest["source_of_record"] == descriptor.source_of_record
    assert manifest["description"] == descriptor.description
    assert manifest["config_schema"] == dict(descriptor.config_schema)

    declared = {c["name"]: c for c in manifest["capabilities"]}
    assert set(declared) == {c.name for c in descriptor.capabilities}
    for capability in descriptor.capabilities:
        entry = declared[capability.name]
        assert entry["operation"] == capability.operation.value
        assert entry["resource_kind"] == capability.resource_kind
        assert entry["description"] == capability.description
        assert tuple(entry["selector_keys"]) == tuple(capability.selector_keys)
        assert tuple(entry["effects"]) == tuple(capability.effects)
        assert entry["deterministic"] is capability.deterministic


def test_the_declared_entry_point_actually_resolves_to_a_builder():
    """A manifest naming an unimportable entry point is a manifest that lies."""
    module_name, _, attribute = repository_descriptor().entry_point.partition(":")
    resolved = getattr(importlib.import_module(module_name), attribute)
    assert resolved is build


def test_the_identity_constants_are_what_the_descriptor_declares():
    descriptor = repository_descriptor()
    assert descriptor.provider_id == REPOSITORY_PROVIDER_ID == "ucos.repository"
    assert descriptor.kind == REPOSITORY_PROVIDER_KIND == "repository"
    assert descriptor.version == REPOSITORY_PROVIDER_VERSION == "1.0.0"


def test_an_author_may_point_the_descriptor_at_a_different_entry_point():
    assert repository_descriptor(entry_point="x.y:z").entry_point == "x.y:z"


# --- the package's own declarations ----------------------------------------------


def test_the_catalog_holds_the_repository_manifest():
    assert CATALOG_DIR.is_dir()
    assert (CATALOG_DIR / "repository.json").is_file()


def test_the_template_manifest_is_outside_the_catalog_so_it_is_never_discovered():
    """The package docstring makes this claim explicitly; discovery reads CATALOG_DIR."""
    assert TEMPLATE_MANIFEST.is_file()
    assert TEMPLATE_MANIFEST.parent != CATALOG_DIR
    assert TEMPLATE_MANIFEST not in set(CATALOG_DIR.iterdir())


def test_the_inferred_repository_root_is_the_working_tree():
    root = repository_root()
    assert (root / "pyproject.toml").is_file()
    assert (root / "platform" / "providers").is_dir()


# --- configuration ----------------------------------------------------------------


def test_an_absent_root_falls_back_to_the_inferred_repository_root():
    assert build(repository_descriptor(), None).root == repository_root()
    assert build(repository_descriptor(), {}).root == repository_root()


def test_patterns_accept_a_single_string_a_sequence_or_neither(substrate: Path):
    descriptor = repository_descriptor()
    assert build(descriptor, {"root": str(substrate)}).patterns == DEFAULT_PATTERNS
    assert build(descriptor, {"root": str(substrate), "patterns": "*.txt"}).patterns == ("*.txt",)
    listed = build(descriptor, {"root": str(substrate), "patterns": ["*.md", "*.txt"]})
    assert listed.patterns == ("*.md", "*.txt")


def test_an_empty_pattern_list_falls_back_to_the_default(substrate: Path):
    """An empty declaration is an unmade choice, not a declaration of nothing."""
    provider = build(repository_descriptor(), {"root": str(substrate), "patterns": []})
    assert provider.patterns == DEFAULT_PATTERNS


# --- probing ----------------------------------------------------------------------


def test_probe_reports_a_readable_substrate(provider: RepositoryProvider):
    assert provider.probe() == {"root_exists": True, "root_readable": True}


def test_probe_reports_an_absent_substrate(tmp_path: Path):
    provider = build(repository_descriptor(), {"root": str(tmp_path / "nowhere")})
    assert provider.probe() == {"root_exists": False, "root_readable": False}


def test_probe_distinguishes_a_present_substrate_from_a_readable_one(tmp_path: Path):
    """A root that exists but cannot be listed is present and not readable."""
    root = tmp_path / "locked"
    root.mkdir()
    root.chmod(0o000)
    try:
        provider = build(repository_descriptor(), {"root": str(root)})
        assert provider.probe() == {"root_exists": True, "root_readable": False}
    finally:
        root.chmod(0o755)


# --- querying ---------------------------------------------------------------------


def test_an_unselected_query_returns_every_artifact_the_pattern_matches(
    provider: RepositoryProvider,
):
    response = provider.query(_query())
    ids = [resource.resource_id for resource in response.resources]
    assert ids == ["alpha.md", "beta.md", "gamma-note.md"]
    assert "ignored.txt" not in ids


def test_results_are_ordered_deterministically_and_repeat_byte_for_byte(
    provider: RepositoryProvider,
):
    first = provider.query(_query())
    second = provider.query(_query())
    assert [r.resource_id for r in first.resources] == [r.resource_id for r in second.resources]
    assert first.query_fingerprint == second.query_fingerprint


def test_each_selector_key_filters_on_its_own_terms(provider: RepositoryProvider):
    assert [r.resource_id for r in provider.query(_query(suffix=".md")).resources] == [
        "alpha.md",
        "beta.md",
        "gamma-note.md",
    ]
    assert [r.resource_id for r in provider.query(_query(path_prefix="beta")).resources] == [
        "beta.md"
    ]
    assert [r.resource_id for r in provider.query(_query(name_contains="note")).resources] == [
        "gamma-note.md"
    ]


def test_selectors_compose_and_an_unsatisfiable_pair_returns_nothing(
    provider: RepositoryProvider,
):
    assert provider.query(_query(path_prefix="alpha", suffix=".md")).resources
    assert not provider.query(_query(path_prefix="alpha", suffix=".txt")).resources


def test_a_selector_key_the_capability_never_declared_is_refused(
    provider: RepositoryProvider,
):
    """PC-04 — the framework refuses it, and the provider must not interpret it."""
    with pytest.raises(ProviderCapabilityError, match="did not declare"):
        provider.query(_query(undeclared_key="anything"))


def test_pagination_is_stable_across_the_cursor(provider: RepositoryProvider):
    page = provider.query(ProviderQuery(capability=CAPABILITY_ARTIFACTS, limit=2))
    assert [r.resource_id for r in page.resources] == ["alpha.md", "beta.md"]
    assert page.truncated
    rest = provider.query(
        ProviderQuery(capability=CAPABILITY_ARTIFACTS, limit=2, cursor=page.next_cursor)
    )
    assert [r.resource_id for r in rest.resources] == ["gamma-note.md"]
    assert not rest.truncated


def test_a_directory_matching_the_pattern_is_not_indexed_as_an_artifact(
    provider: RepositoryProvider, substrate: Path
):
    """The index holds files; a directory that happens to match the glob is not one."""
    (substrate / "directory.md").mkdir()
    assert [r.resource_id for r in provider.query(_query()).resources] == [
        "alpha.md",
        "beta.md",
        "gamma-note.md",
    ]


def test_an_unreadable_match_is_skipped_by_the_query_rather_than_failing_it(
    provider: RepositoryProvider, substrate: Path
):
    """One unreadable artifact must not deny the caller the rest of the substrate."""
    target = substrate / "beta.md"
    target.chmod(0o000)
    try:
        ids = [r.resource_id for r in provider.query(_query()).resources]
    finally:
        target.chmod(0o644)
    assert ids == ["alpha.md", "gamma-note.md"]


def test_a_query_over_an_absent_substrate_returns_nothing_rather_than_raising(
    tmp_path: Path,
):
    """Fail closed means empty, not exploded: an absent root is a substrate fact."""
    provider = build(repository_descriptor(), {"root": str(tmp_path / "nowhere")})
    assert provider.query(_query()).resources == ()


# --- resource projection ----------------------------------------------------------


def test_a_projected_artifact_carries_its_content_hash_and_provenance(
    provider: RepositoryProvider, substrate: Path
):
    (resource,) = provider.query(_query(path_prefix="alpha")).resources
    expected = hashlib.sha256((substrate / "alpha.md").read_bytes()).hexdigest()
    assert resource.kind == ARTIFACT_KIND
    assert resource.provider_id == REPOSITORY_PROVIDER_ID
    assert resource.payload["sha256"] == expected
    assert resource.payload["name"] == "alpha.md"
    assert resource.payload["suffix"] == ".md"
    assert resource.payload["size_bytes"] == len((substrate / "alpha.md").read_bytes())
    assert resource.provenance["root"] == substrate.resolve().as_posix()
    assert resource.provenance["sha256"] == expected


def test_the_provenance_chain_is_extended_with_the_artifact_path(
    provider: RepositoryProvider,
):
    """PC-06 — the default chain names origin and conveyor; this adds the location."""
    (resource,) = provider.query(_query(path_prefix="alpha")).resources
    chain = provider.provenance_chain(resource)
    assert chain[-1] == "path:alpha.md"
    assert "UCOS repository working tree" in chain


# --- fetching and containment -----------------------------------------------------


def test_one_artifact_resolves_by_its_repository_relative_path(
    provider: RepositoryProvider,
):
    assert provider.fetch("beta.md").payload["name"] == "beta.md"


def test_an_absent_artifact_fails_closed(provider: RepositoryProvider):
    with pytest.raises(ProviderExecutionError, match="resource not found"):
        provider.fetch("no-such-file.md")


def test_a_directory_is_not_an_artifact(provider: RepositoryProvider, substrate: Path):
    (substrate / "subdir").mkdir()
    with pytest.raises(ProviderExecutionError, match="resource not found"):
        provider.fetch("subdir")


def test_a_crafted_resource_id_cannot_read_outside_the_declared_substrate(
    provider: RepositoryProvider, substrate: Path
):
    """Containment is the module's stated security claim; prove the escape is refused."""
    outside = substrate.parent / "outside.md"
    outside.write_text("# not part of the declared substrate\n")
    assert provider.resolve_resource("../outside.md") is None
    with pytest.raises(ProviderExecutionError, match="resource not found"):
        provider.fetch("../outside.md")


def test_an_absolute_path_outside_the_root_is_refused(
    provider: RepositoryProvider, substrate: Path
):
    outside = substrate.parent / "absolute.md"
    outside.write_text("# elsewhere\n")
    assert provider.resolve_resource(str(outside)) is None


def test_an_unreadable_artifact_projects_to_nothing_rather_than_raising(
    provider: RepositoryProvider, substrate: Path
):
    """An OSError on read is a substrate fault, and a fault is not a resource."""
    target = substrate / "alpha.md"
    target.chmod(0o000)
    try:
        assert provider.resolve_resource("alpha.md") is None
    finally:
        target.chmod(0o644)


# --- attestation ------------------------------------------------------------------


def test_an_artifact_attests_with_a_hash_and_a_non_empty_chain(
    provider: RepositoryProvider,
):
    attestation = provider.verify("alpha.md")
    assert attestation.verified
    assert attestation.resource_id == "alpha.md"
    assert attestation.resource_hash
    assert attestation.provenance_chain[-1] == "path:alpha.md"


def test_an_absent_artifact_attests_as_unverified_rather_than_raising(
    provider: RepositoryProvider,
):
    """A consumer must be able to tell 'absent' from 'tampered' (PC-06)."""
    attestation = provider.verify("no-such-file.md")
    assert not attestation.verified
    assert attestation.reasons


# --- bounds -----------------------------------------------------------------------


def test_the_index_is_bounded_so_an_unexpected_substrate_cannot_run_away(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """The ceiling truncates deterministically; the lowest ids survive."""
    for index in range(12):
        (tmp_path / f"artifact-{index:03d}.md").write_text(f"# {index}\n")
    monkeypatch.setattr(
        "platform.providers.repository.provider.MAX_INDEXED_ARTIFACTS", 5, raising=True
    )
    provider = build(repository_descriptor(), {"root": str(tmp_path)})
    ids = [
        r.resource_id
        for r in provider.query(ProviderQuery(capability=CAPABILITY_ARTIFACTS)).resources
    ]
    assert ids == [f"artifact-{index:03d}.md" for index in range(5)]


def test_the_declared_ceiling_is_a_real_bound():
    assert MAX_INDEXED_ARTIFACTS == 5_000
