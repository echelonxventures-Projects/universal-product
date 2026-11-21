"""Deliverable 2 — Git as ONE provider, and discovery that works with no version control at all.

THE CENTRAL TEST IN THIS FILE IS ``test_discovery_works_with_no_version_control_of_any_kind``. It
enumerates a tree that has never been a repository — no ``.git``, no index, no VCS binary consulted
— and gets a population. Until that passes, "Git is no longer a dependency" is a claim about
intentions.

THE SECOND CENTRAL TEST IS ``test_the_two_providers_differ_only_in_what_they_declare``. The value of
Deliverable 6 is that "what do I lose by discovering without version control" has a computable
answer rather than a prose one.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.omega_infinite import filesystem_provider, git_provider
from engine.omega_infinite.capability import (
    AUTHORITY_METADATA,
    CHANGE_SET,
    CONTENT_HASHING,
    LOCAL_STORAGE,
    REVISION_HISTORY,
    REVISION_IDENTITY,
    REVISION_METADATA,
    TRACKED_CONTENT,
    VERSIONED_CONTENT,
    CapabilityError,
    CapabilitySet,
)
from engine.omega_infinite.capability import LOCAL_STORAGE as LOCAL
from engine.omega_infinite.provider import ProviderError, Selector
from engine.tests.omega_infinite.conftest import git

PYTHON_ONLY = Selector(patterns=("*.py",))


# ------------------------------------------------------------------ Deliverable 2b: no VCS at all


def test_discovery_works_with_no_version_control_of_any_kind(untracked_tree: Path) -> None:
    """THE DELIVERABLE 2 SUCCESS CRITERION, discharged by execution.

    The tree has never been a repository. No git, hg, svn or p4 is consulted, and artifacts are
    discovered directly from storage.
    """
    assert not (untracked_tree / ".git").exists()
    assert not git_provider.available(str(untracked_tree))

    provider = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree))
    found = provider.enumerate()
    locators = [a.location.locator for a in found]

    assert "src/module.py" in locators
    assert "docs/guide.md" in locators
    assert "bin/ucos-report" in locators
    assert len(found) >= 7


def test_the_filesystem_provider_declares_no_guarantee_it_does_not_have(
    untracked_tree: Path,
) -> None:
    """It enumerates local debris, so TRACKED_CONTENT would be a lie — and a lie here makes the
    eligibility boundary unenforceable everywhere else."""
    declared = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree)).capabilities()
    assert declared.names() == ("CONTENT_HASHING", "LOCAL_STORAGE")
    assert not declared.supports(TRACKED_CONTENT)
    assert not declared.supports(VERSIONED_CONTENT)
    assert not declared.supports(AUTHORITY_METADATA)


def test_an_unversioned_provider_leaves_the_revision_empty_rather_than_faking_one(
    untracked_tree: Path,
) -> None:
    provider = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree))
    assert provider.metadata().revision == ""
    assert all(a.location.revision == "" for a in provider.enumerate())


def test_untracked_debris_is_visible_to_the_filesystem_provider(untracked_tree: Path) -> None:
    """The honest consequence of no eligibility boundary, asserted so it is not a surprise."""
    (untracked_tree / "scratch.py").write_text("debris = 1\n", encoding="utf-8")
    provider = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree))
    assert "scratch.py" in [a.location.locator for a in provider.enumerate(PYTHON_ONLY)]


def test_the_walk_prunes_noise_directories_and_reports_what_it_pruned(
    untracked_tree: Path,
) -> None:
    (untracked_tree / "__pycache__").mkdir()
    (untracked_tree / "__pycache__" / "cached.py").write_text("x = 1\n", encoding="utf-8")
    provider = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree))

    assert not any("__pycache__" in a.location.locator for a in provider.enumerate())
    assert "__pycache__" in provider.metadata().details["exclusions"]


def test_exclusions_are_injected_so_no_fixed_noise_list_governs(untracked_tree: Path) -> None:
    """A fixed list inside the module would be the SOURCE_TREES defect again."""
    (untracked_tree / "__pycache__").mkdir()
    (untracked_tree / "__pycache__" / "cached.py").write_text("x = 1\n", encoding="utf-8")

    permissive = filesystem_provider.FilesystemDiscoveryProvider(
        str(untracked_tree), exclusions=frozenset()
    )
    assert any("__pycache__" in a.location.locator for a in permissive.enumerate())

    strict = filesystem_provider.FilesystemDiscoveryProvider(
        str(untracked_tree), exclusions=frozenset({"docs"})
    )
    assert not any(a.location.locator.startswith("docs/") for a in strict.enumerate())


def test_the_filesystem_provider_reads_and_hashes_content(untracked_tree: Path) -> None:
    provider = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree))
    assert provider.read("src/module.py") == "VALUE = 1\n"
    assert len(provider.content_hash("src/module.py")) == 64


def test_reading_or_hashing_something_absent_is_a_named_refusal(untracked_tree: Path) -> None:
    provider = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree))
    with pytest.raises(ProviderError, match="could not be read"):
        provider.read("no/such/file.py")
    with pytest.raises(ProviderError, match="could not be hashed"):
        provider.content_hash("no/such/file.py")


def test_a_missing_directory_is_a_fault_not_an_empty_population(tmp_path: Path) -> None:
    """An empty population satisfies every invariant, so it is never reported as a clean one."""
    provider = filesystem_provider.FilesystemDiscoveryProvider(str(tmp_path / "absent"))
    with pytest.raises(ProviderError, match="not a readable directory"):
        provider.enumerate()


def test_filesystem_availability_needs_no_external_binary(untracked_tree: Path) -> None:
    assert filesystem_provider.available(str(untracked_tree))
    assert not filesystem_provider.available(str(untracked_tree / "src" / "module.py"))


# --------------------------------------------------------------- Deliverable 2a: git as a provider


def test_the_git_provider_enumerates_tracked_content(tracked_tree: Path) -> None:
    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    locators = [a.location.locator for a in provider.enumerate()]
    assert "src/module.py" in locators
    assert "docs/guide.md" in locators


def test_the_git_provider_applies_the_eligibility_boundary(tracked_tree: Path) -> None:
    """The property that makes version control worth preferring: untracked debris is NOT in the
    population, so a verdict cannot depend on a developer's working copy."""
    (tracked_tree / "debris.py").write_text("debris = 1\n", encoding="utf-8")
    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    assert "debris.py" not in [a.location.locator for a in provider.enumerate(PYTHON_ONLY)]


def test_the_selector_replaces_the_hard_coded_python_query(tracked_tree: Path) -> None:
    """Ω-1 asks git for '*.py'. Here the filter is an ARGUMENT, and the default is everything."""
    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    everything = [a.location.locator for a in provider.enumerate()]
    python = [a.location.locator for a in provider.enumerate(PYTHON_ONLY)]

    assert "docs/guide.md" in everything
    assert "docs/guide.md" not in python
    assert set(python) == {"src/module.py", "src/nested/deep.py"}
    assert len(everything) > len(python)


def test_the_git_provider_declares_what_git_actually_offers(tracked_tree: Path) -> None:
    declared = git_provider.GitDiscoveryProvider(str(tracked_tree)).capabilities()
    assert declared.names() == (
        "AUTHORITY_METADATA",
        # Three questions the provider declared it could not answer until callers needed them:
        # what differs between two points, what the recorded sequence is, and what one revision
        # carries. Each is one question, keyed and delivered separately.
        "CHANGE_SET",
        "CONTENT_HASHING",
        "LOCAL_STORAGE",
        "REVISION_HISTORY",
        "REVISION_IDENTITY",
        "REVISION_METADATA",
        "TRACKED_CONTENT",
        "VERSIONED_CONTENT",
        # Added when every declared capability acquired a delivery method. It is a DIFFERENT
        # QUESTION from TRACKED_CONTENT, not a wider filter: four callers were reaching past the
        # provider for `--others` because no capability covered what the working copy holds and
        # the index does not.
        "WORKING_TREE_STATE",
    )


def test_a_committed_revision_is_named_and_attached_to_every_location(tracked_tree: Path) -> None:
    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    revision = provider.revision()
    assert len(revision) == 40
    assert all(a.location.revision == revision for a in provider.enumerate())


def test_a_repository_with_no_commit_reports_an_empty_revision_honestly(tmp_path: Path) -> None:
    """Inventing an identifier for a tree with no HEAD would make an unreproducible enumeration
    look reproducible."""

    root = tmp_path / "fresh"
    root.mkdir()
    (root / "a.py").write_text("x = 1\n", encoding="utf-8")
    git(root, "init", "-q")
    assert git_provider.GitDiscoveryProvider(str(root)).revision() == ""


def test_the_git_provider_hashes_through_the_index(tracked_tree: Path) -> None:
    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    assert len(provider.content_hash("src/module.py")) == 40
    with pytest.raises(ProviderError):
        provider.content_hash("no/such/file.py")


def test_git_supplies_ownership_facts_on_demand_never_during_enumeration(
    tracked_tree: Path,
) -> None:
    """A capability promises what CAN be asked, not what has already been paid for. One `git log`
    per artifact would make enumerating a large repository cost thousands of subprocesses."""
    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    facts = provider.authority_metadata("src/module.py")
    assert facts["last_author_email"] == "t@ucos"
    assert provider.authority_metadata("no/such/file.py") == {}
    # enumeration carried no ownership fact
    assert "last_author_email" not in provider.enumerate()[0].metadata


def test_git_availability_answers_rather_than_raising(tracked_tree: Path, tmp_path: Path) -> None:
    """THE QUESTION Ω-1 CANNOT ASK. A registry choosing between providers needs a probe that
    returns False instead of raising, or there is no fallback path."""
    assert git_provider.available(str(tracked_tree))
    assert not git_provider.available(str(tmp_path / "does-not-exist"))


def test_a_git_failure_is_a_named_refusal(tmp_path: Path) -> None:
    provider = git_provider.GitDiscoveryProvider(str(tmp_path / "not-a-repo"))
    with pytest.raises(ProviderError, match="git failed"):
        provider.enumerate()


# ------------------------------------------------------------------------------ the comparison


def test_the_two_providers_differ_only_in_what_they_declare(tracked_tree: Path) -> None:
    """THE DELIVERABLE 6 PAYOFF: the cost of discovering without version control is COMPUTABLE."""
    tracked = git_provider.GitDiscoveryProvider(str(tracked_tree)).capabilities()
    plain = filesystem_provider.FilesystemDiscoveryProvider(str(tracked_tree)).capabilities()

    lost = tracked.missing(*plain.capabilities) or ()
    gap = tuple(sorted(c.name for c in tracked.capabilities - plain.capabilities))
    assert lost == ()
    assert gap == (
        "AUTHORITY_METADATA",
        "CHANGE_SET",
        "REVISION_HISTORY",
        "REVISION_IDENTITY",
        "REVISION_METADATA",
        "TRACKED_CONTENT",
        "VERSIONED_CONTENT",
        "WORKING_TREE_STATE",
    )
    assert plain.supports(LOCAL_STORAGE) and plain.supports(CONTENT_HASHING)


def test_git_outranks_the_filesystem_because_it_offers_more(tracked_tree: Path) -> None:
    """Priority is a NUMBER, not a branch in the registry, so a future provider with stronger
    guarantees outranks git without an edit anywhere."""
    assert git_provider.GitDiscoveryProvider(str(tracked_tree)).priority > (
        filesystem_provider.FilesystemDiscoveryProvider(str(tracked_tree)).priority
    )


def test_both_providers_report_their_binding_and_mechanism(tracked_tree: Path) -> None:
    tracked = git_provider.GitDiscoveryProvider(str(tracked_tree)).metadata()
    plain = filesystem_provider.FilesystemDiscoveryProvider(str(tracked_tree)).metadata()
    assert "ls-files" in tracked.mechanism
    assert "no version control" in plain.mechanism
    assert "eligibility_boundary" in tracked.details
    assert plain.details["eligibility_boundary"].startswith("NONE")


def test_a_capability_gated_method_asks_before_acting(tracked_tree: Path) -> None:
    """Every provider method depending on a capability must call require(), or it becomes the
    template someone copies without the check."""

    class Stripped(git_provider.GitDiscoveryProvider):
        def capabilities(self):  # type: ignore[no-untyped-def]
            return CapabilitySet.of(LOCAL_STORAGE)

    with pytest.raises(CapabilityError, match="CONTENT_HASHING"):
        Stripped(str(tracked_tree)).content_hash("src/module.py")
    with pytest.raises(CapabilityError, match="AUTHORITY_METADATA"):
        Stripped(str(tracked_tree)).authority_metadata("src/module.py")


def test_the_walk_is_depth_bounded_so_a_pathological_tree_terminates(
    untracked_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A BOUND, not an optimisation. A symlink cycle or an absurd tree must not hang a gate, and a
    walk with no depth limit is a walk that can. Monkeypatched rather than built 64 levels deep,
    because the property under test is that the limit is ENFORCED, not what its value is."""
    deep = untracked_tree / "a" / "b" / "c" / "d"
    deep.mkdir(parents=True)
    (deep / "buried.py").write_text("x = 1\n", encoding="utf-8")

    monkeypatch.setattr(filesystem_provider, "MAX_DEPTH", 2)
    provider = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree))
    locators = [a.location.locator for a in provider.enumerate()]

    assert "a/b/c/d/buried.py" not in locators
    assert "src/module.py" in locators
    assert provider.metadata().details["max_depth"] == "2"


def test_symlinks_are_not_followed_by_default(untracked_tree: Path) -> None:
    """A followed symlink can leave the knowledge space entirely, which would make the population
    depend on filesystem topology outside the space being measured."""
    target = untracked_tree / "src"
    (untracked_tree / "link").symlink_to(target, target_is_directory=True)

    provider = filesystem_provider.FilesystemDiscoveryProvider(str(untracked_tree))
    assert provider.metadata().details["follow_symlinks"] == "false"
    assert not any(a.location.locator.startswith("link/") for a in provider.enumerate())

    following = filesystem_provider.FilesystemDiscoveryProvider(
        str(untracked_tree), follow_symlinks=True
    )
    assert following.metadata().details["follow_symlinks"] == "true"


def test_an_empty_hash_answer_is_a_fault_rather_than_an_empty_digest(
    tracked_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A defensive guard, and it is tested rather than trusted. If git ever answered successfully
    with nothing, returning "" would hand a caller an empty digest that compares equal to another
    empty digest — two unrelated artifacts would read as identical content."""
    monkeypatch.setattr(git_provider, "_run", lambda *arguments: "\n")
    with pytest.raises(ProviderError, match="resolved no object"):
        git_provider.GitDiscoveryProvider(str(tracked_tree)).content_hash("src/module.py")


# --------------------------------------------- the capabilities that had a declaration and no call


def test_a_named_reference_is_reported_as_resolving_or_not(tracked_tree: Path) -> None:
    """A caller binding work to a reference needs to know whether it exists, and "it does not"
    must be an answer rather than an exception — the same reason `revision()` returns ""."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    assert provider.supply(REVISION_IDENTITY, ref="HEAD") == {"ref": "HEAD", "resolves": True}
    assert provider.supply(REVISION_IDENTITY, ref="refs/heads/never-created") == {
        "ref": "refs/heads/never-created",
        "resolves": False,
    }


def test_where_two_references_parted_is_reported_or_left_empty(tracked_tree: Path) -> None:
    """A merge base that cannot be computed is empty rather than absent: a caller must be able to
    tell "they never met" from "the provider declined to say"."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    same = provider.supply(REVISION_IDENTITY, diverged_from="HEAD")
    assert same["diverged_from"] == "HEAD"
    assert len(str(same["merge_base"])) == 40
    unrelated = provider.supply(REVISION_IDENTITY, diverged_from="refs/heads/never-created")
    assert unrelated == {"diverged_from": "refs/heads/never-created", "merge_base": ""}


def test_the_change_set_can_be_asked_of_the_index_rather_than_the_working_copy(
    tracked_tree: Path,
) -> None:
    """`--cached` is a different question, not a filter: a verdict about what has been RECORDED
    must not move when an operator saves a file."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    (tracked_tree / "src" / "module.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert "src/module.py" in provider.supply(CHANGE_SET, PYTHON_ONLY)
    assert provider.supply(CHANGE_SET, PYTHON_ONLY, staged=True) == ()
    git(tracked_tree, "add", "src/module.py")
    assert provider.supply(CHANGE_SET, PYTHON_ONLY, staged=True) == ("src/module.py",)


def test_the_recorded_revisions_are_returned_as_pairs_the_caller_never_parses(
    tracked_tree: Path,
) -> None:
    """The separator stays inside the provider. A caller given a format string would be parsing
    git's output, which is the whole thing asking a provider is for."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    history = provider.supply(REVISION_HISTORY)
    assert len(history) == 1
    identifier, subject = history[0]
    assert len(identifier) == 40
    assert subject
    assert provider.supply(REVISION_HISTORY, limit=1) == history


def test_the_named_lines_of_development_are_a_different_question_from_the_revisions(
    tracked_tree: Path,
) -> None:
    """A ref carries no subject, and pairing it with an empty one keeps the shape the caller
    unpacks identical whichever question it asked."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    refs = provider.supply(REVISION_HISTORY, refs=True)
    assert refs
    assert all(subject == "" for _, subject in refs)


def test_a_revisions_metadata_is_supplied_and_an_unknown_revision_answers_empty(
    tracked_tree: Path,
) -> None:
    """An unknown revision has no metadata, and inventing a committed_at for it would put a
    fabricated instant into whatever the caller records."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    metadata = provider.supply(REVISION_METADATA)
    assert metadata["revision"] == "HEAD"
    assert metadata["committed_at"]
    assert metadata["subject"]
    assert provider.supply(REVISION_METADATA, revision="0" * 40) == {}


def test_an_index_row_this_provider_cannot_read_contributes_no_hash(
    tracked_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The index's answer is the one every other git-derived verdict rests on. A row this parser
    cannot read must contribute nothing rather than a partial entry, because a path mapped to the
    wrong blob is worse than a path with no hash at all."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    monkeypatch.setattr(git_provider, "_run", lambda *arguments: "100644\tsrc/module.py\0")
    assert provider.supply(CONTENT_HASHING, PYTHON_ONLY) == {}


def test_where_the_bytes_are_is_answered_without_a_network_call(tracked_tree: Path) -> None:
    """LOCAL_STORAGE was declared and had no delivery. A declaration with no call is the
    ENVELOPE_ONLY shape this package exists to measure."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    assert provider.supply(LOCAL) == str(tracked_tree)


def test_the_default_position_answer_carries_every_field_or_leaves_it_empty(
    tracked_tree: Path,
) -> None:
    """Four modules used to pay a separate process for two or three of these each. Asked together,
    a field git cannot answer here — an upstream a local branch does not have — is EMPTY rather
    than absent, so a caller can tell "no upstream" from "the provider declined to say"."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    position = provider.supply(REVISION_IDENTITY)
    assert set(position) == {"revision", "short", "branch", "upstream", "is_work_tree"}
    assert len(str(position["revision"])) == 40
    assert position["is_work_tree"] is True
    assert position["upstream"] == "", "a local branch with no upstream must answer empty"


def test_a_history_line_carrying_no_identifier_is_dropped(
    tracked_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank line in the log output is not a revision, and a pair whose identifier is "" would
    compare equal to every other such pair — two unrelated blanks reading as one revision."""

    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    monkeypatch.setattr(git_provider, "_run", lambda *arguments: "\n\nabc\x1fa subject\n")
    assert provider.supply(REVISION_HISTORY) == (("abc", "a subject"),)


def test_the_revision_the_enumeration_reproduces_against_is_supplied(tracked_tree: Path) -> None:
    """VERSIONED_CONTENT is what every allocation permit is bound to. Declaring it and offering no
    call is the shape that sent four callers to the tool directly."""
    provider = git_provider.GitDiscoveryProvider(str(tracked_tree))
    assert provider.supply(VERSIONED_CONTENT) == provider.revision()
