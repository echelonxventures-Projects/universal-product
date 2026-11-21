"""Tests for engine.knowledge.integration.repository — EPIC-UKDA-004.

Exercise the live-repository probe (via an injected, deterministic git runner and a
real temp working tree), the pure analyzers, the assimilator driving the *existing*
ConstitutionalPipeline, the RepositorySubject, evidence emission, and the CLI + the
pipeline.assimilate entry point. Nothing touches the certified corpus (DP-03).
"""

from __future__ import annotations

import json

import pytest

from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.integration import cli as integration_cli
from engine.knowledge.integration.errors import RepositoryDiscoveryError
from engine.knowledge.integration.pipeline import ConstitutionalPipeline
from engine.knowledge.integration.repository import (
    CommitRef,
    DependencySignal,
    OwnershipSignal,
    RepositoryAssimilator,
    RepositoryProbe,
    RepositorySnapshot,
    RepositoryUnit,
    _default_git_runner,
    _first_line,
    _lines,
    _parse_commits,
    _parse_status,
    _pattern_matches,
    _resolve_owner,
    _slug,
    _split_requirement,
    discover_checkpoints,
    discover_drift,
    discover_frontier,
    discover_repository,
    discover_workstreams,
    emit_evidence,
)
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

# --------------------------------------------------------------------------- helpers


def make_runner(responses):
    """Build a deterministic fake git runner mapping commands to canned output."""

    def run(args):
        a = tuple(args)
        if a == ("rev-parse", "HEAD"):
            return responses.get("head")
        if a == ("rev-parse", "--abbrev-ref", "HEAD"):
            return responses.get("branch")
        if a == ("rev-parse", "--is-inside-work-tree"):
            return responses.get("inside")
        if a == ("tag", "--list"):
            return responses.get("tags")
        if a and a[0] == "for-each-ref":
            return responses.get("branches")
        if a and a[0] == "log":
            return responses.get("log")
        if a == ("status", "--porcelain"):
            return responses.get("status")
        if a and a[0] == "symbolic-ref":
            return responses.get("symref")
        return None

    return run


@pytest.fixture
def repo_tree(tmp_path):
    """A realistic temp working tree: realized/doc-only/empty units + manifests + CODEOWNERS."""
    # A realized python package (with a pruned hidden + ignored subdir).
    pkg = tmp_path / "pkg"
    (pkg / "sub").mkdir(parents=True)
    (pkg / "__init__.py").write_text("x = 1\n", encoding="utf-8")
    (pkg / "sub" / "core.py").write_text("y = 2\n", encoding="utf-8")
    (pkg / ".hidden").mkdir()
    (pkg / ".hidden" / "ignored.py").write_text("nope = 1\n", encoding="utf-8")
    (pkg / "__pycache__").mkdir()
    (pkg / "__pycache__" / "cached.py").write_text("cache = 1\n", encoding="utf-8")
    (pkg / ".dotfile").write_text("hidden\n", encoding="utf-8")
    # A documentation-only unit (files, but no source).
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# guide\n", encoding="utf-8")
    # An empty unit.
    (tmp_path / "empty").mkdir()
    # Ignored + hidden top-level directories, and a top-level file.
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "README.md").write_text("# repo\n", encoding="utf-8")
    # Manifests.
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["requests==2.0.0"]\n'
        '[project.optional-dependencies]\ndev = ["pytest==8.3.4"]\n',
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        '{"dependencies": {"left-pad": "^1.0.0"}, "devDependencies": {"jest": "^29"},'
        ' "peerDependencies": []}',
        encoding="utf-8",
    )
    (tmp_path / "requirements.txt").write_text(
        "# a comment\n-r other.txt\n\nflask==3.0\n", encoding="utf-8"
    )
    # CODEOWNERS with a comment, a blank, a too-short line, and real claims.
    (tmp_path / "CODEOWNERS").write_text(
        "# owners\n\npkg\n/pkg/ @team-pkg\n* @team-root\n", encoding="utf-8"
    )
    return tmp_path


def snapshot_of(repo_tree, **responses):
    return RepositoryProbe().capture(repo_tree, git=make_runner(responses))


# --------------------------------------------------------------------------- helpers/units


def test_slug():
    assert _slug("UCOS Consolidation!!") == "UCOS-CONSOLIDATION"
    assert _slug("---") == "REPO"
    assert _slug("a1_b2") == "A1-B2"


def test_split_requirement():
    assert _split_requirement("pytest==8.3.4") == ("pytest", "==8.3.4")
    assert _split_requirement("requests") == ("requests", None)
    assert _split_requirement("@scope/pkg") == ("@scope/pkg", None)


def test_first_line_and_lines():
    assert _first_line(None) is None
    assert _first_line("   ") is None
    assert _first_line(" a \n b ") == "a"
    assert _lines(None) == ()
    assert _lines("b\n\na\n") == ("a", "b")


def test_parse_commits():
    assert _parse_commits(None) == ()
    parsed = _parse_commits("sha1\x1fsummary one\nno-delimiter-line\n\x1fempty sha")
    assert parsed == (CommitRef("sha1", "summary one"),)


def test_parse_status():
    staged, modified, untracked = _parse_status(
        "A  staged.py\n M modified.py\n?? untracked.py\nR  old.py -> new.py\nMM both.py\nXY\n"
    )
    assert staged == ("both.py", "new.py", "staged.py")
    assert modified == ("both.py", "modified.py")
    assert untracked == ("untracked.py",)
    assert _parse_status(None) == ((), (), ())


def test_pattern_matches():
    assert _pattern_matches("*", "anything/here")
    assert _pattern_matches("/", "anything")
    assert _pattern_matches("/pkg/", "pkg")
    assert _pattern_matches("pkg", "pkg/sub")
    assert _pattern_matches("pkg/*", "pkg/sub")
    assert not _pattern_matches("other", "pkg")


def test_resolve_owner_precedence():
    signals = (
        OwnershipSignal("*", ("@root",), "CODEOWNERS"),
        OwnershipSignal("/pkg/", ("@pkg",), "CODEOWNERS"),
        OwnershipSignal("noowner", (), "CODEOWNERS"),
    )
    assert _resolve_owner("pkg/thing", signals) == "@pkg"
    assert _resolve_owner("unclaimed", signals) == "@root"
    assert _resolve_owner("x", ()) == ""


# --------------------------------------------------------------------------- probe


def test_capture_rejects_non_directory(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("hi\n", encoding="utf-8")
    with pytest.raises(RepositoryDiscoveryError):
        RepositoryProbe().capture(target)


def test_capture_with_git_runner(repo_tree):
    snap = snapshot_of(
        repo_tree,
        head="081ecb0\n",
        branch="main\n",
        inside="true\n",
        tags="v2\nv1\n",
        branches="feature\nmain\n",
        log="sha1\x1ffirst\nsha2\x1fsecond\n",
        status="?? new.txt\n M pkg/__init__.py\n",
        symref="refs/remotes/origin/main\n",
    )
    assert snap.head == "081ecb0"
    assert snap.branch == "main"
    assert snap.git_available is True
    assert snap.tags == ("v1", "v2")
    assert snap.branches == ("feature", "main")
    assert snap.commits == (CommitRef("sha1", "first"), CommitRef("sha2", "second"))
    assert snap.default_branch == "main"
    assert snap.untracked == ("new.txt",)
    assert snap.modified == ("pkg/__init__.py",)
    # units: docs, empty, pkg (sorted); __pycache__/.git excluded; README.md is not a unit.
    paths = [u.path for u in snap.units]
    assert paths == ["docs", "empty", "pkg"]
    pkg = next(u for u in snap.units if u.path == "pkg")
    assert pkg.realized is True
    assert pkg.source_files == 2  # __init__.py + sub/core.py; hidden/pycache pruned
    assert pkg.languages == ("py",)
    assert pkg.owner == "@team-pkg"
    docs = next(u for u in snap.units if u.path == "docs")
    assert docs.realized is False and docs.total_files == 1
    empty = next(u for u in snap.units if u.path == "empty")
    assert empty.total_files == 0
    # ownership: comment/blank/short line dropped, two real signals.
    assert [o.pattern for o in snap.ownership] == ["/pkg/", "*"]
    # dependencies from all three manifests, sorted by (manifest, kind, name).
    names = [(d.manifest, d.kind, d.name, d.version) for d in snap.dependencies]
    assert ("pyproject.toml", "optional:dev", "pytest", "==8.3.4") in names
    assert ("pyproject.toml", "runtime", "requests", "==2.0.0") in names
    assert ("package.json", "dev", "jest", "^29") in names
    assert ("package.json", "runtime", "left-pad", "^1.0.0") in names
    assert ("requirements.txt", "runtime", "flask", "==3.0") in names


def test_capture_git_absent_defaults(repo_tree):
    snap = snapshot_of(repo_tree)  # runner returns None for everything
    assert snap.head is None
    assert snap.branch is None
    assert snap.git_available is False
    assert snap.default_branch is None
    assert snap.commits == ()


def test_capture_inside_false_but_head_present(repo_tree):
    snap = snapshot_of(repo_tree, head="abc\n", inside="false\n")
    assert snap.git_available is True


def test_default_git_runner_on_non_git_dir(tmp_path):
    runner = _default_git_runner(tmp_path)
    # git runs but reports failure outside a work tree -> None (or None if git is absent).
    assert runner(["rev-parse", "HEAD"]) is None


def test_capture_defaults_to_real_git_runner(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "m.py").write_text("z = 1\n", encoding="utf-8")
    snap = RepositoryProbe().capture(tmp_path)  # git=None -> real runner, non-git dir
    assert snap.git_available is False
    assert [u.path for u in snap.units] == ["src"]


def test_malformed_manifests_are_ignored(tmp_path):
    (tmp_path / "pyproject.toml").write_text("=not valid toml", encoding="utf-8")
    (tmp_path / "package.json").write_text("{not json", encoding="utf-8")
    snap = RepositoryProbe().capture(tmp_path, git=make_runner({}))
    assert snap.dependencies == ()


# --------------------------------------------------------------------------- analyzers


def test_checkpoints_with_and_without_head():
    base = RepositorySnapshot(
        name="r",
        root="/r",
        universe="R",
        head="deadbeefcafe0000",
        branch="main",
        default_branch="main",
        git_available=True,
        units=(),
        ownership=(),
        dependencies=(),
        tags=("v1",),
        branches=(),
        commits=(CommitRef("deadbeefcafe0000", "tip"),),
        staged=(),
        modified=(),
        untracked=(),
    )
    cps = discover_checkpoints(base)
    assert cps[0].kind == "head" and cps[0].summary == "tip"
    assert cps[1].kind == "tag" and cps[1].ref == "v1"
    # no head, no commits
    none_head = RepositorySnapshot(
        name="r",
        root="/r",
        universe="R",
        head=None,
        branch=None,
        default_branch=None,
        git_available=False,
        units=(),
        ownership=(),
        dependencies=(),
        tags=(),
        branches=(),
        commits=(),
        staged=(),
        modified=(),
        untracked=(),
    )
    assert discover_checkpoints(none_head) == ()


def test_workstreams():
    snap = RepositorySnapshot(
        name="r",
        root="/r",
        universe="R",
        head="h",
        branch="main",
        default_branch="main",
        git_available=True,
        units=(),
        ownership=(),
        dependencies=(),
        tags=(),
        branches=("feature", "main"),
        commits=(),
        staged=("s",),
        modified=(),
        untracked=("u",),
    )
    ws = discover_workstreams(snap)
    kinds = {w.name: (w.kind, w.active) for w in ws}
    assert kinds["main"] == ("branch", True)
    assert kinds["feature"] == ("branch", False)
    assert kinds["working-tree"][0] == "working-tree" and kinds["working-tree"][1] is True
    # clean tree -> no working-tree workstream
    clean = RepositorySnapshot(
        name="r",
        root="/r",
        universe="R",
        head="h",
        branch="main",
        default_branch="main",
        git_available=True,
        units=(),
        ownership=(),
        dependencies=(),
        tags=(),
        branches=("main",),
        commits=(),
        staged=(),
        modified=(),
        untracked=(),
    )
    assert all(w.kind == "branch" for w in discover_workstreams(clean))


def _unit(path, realized, total):
    return RepositoryUnit(
        unit_id=f"REPO-R-UNIT-{path.upper()}",
        path=path,
        realized=realized,
        source_files=1 if realized else 0,
        total_files=total,
        owner="",
        languages=("py",) if realized else (),
    )


def test_frontier_and_drift():
    snap = RepositorySnapshot(
        name="r",
        root="/r",
        universe="R",
        head="h",
        branch="main",
        default_branch="main",
        git_available=True,
        units=(_unit("pkg", True, 3), _unit("docs", False, 2), _unit("empty", False, 0)),
        ownership=(),
        dependencies=(),
        tags=(),
        branches=(),
        commits=(),
        staged=("a",),
        modified=("b",),
        untracked=("c",),
    )
    frontier = discover_frontier(snap)
    assert frontier.realized == ("REPO-R-UNIT-PKG",)
    reasons = {f.path: f.reason for f in frontier.frontier}
    assert reasons == {"docs": "documentation-only", "empty": "empty-unit"}
    drift = discover_drift(snap)
    assert drift.clean is False
    assert {d.kind for d in drift.drift} == {"staged", "modified", "untracked"}
    assert discover_repository(snap).counts()["units"] == 3


# --------------------------------------------------------------------------- assimilation


def test_assimilate_live_repo(repo_tree):
    subject = ConstitutionalPipeline(KnowledgeBase([])).assimilate(
        snapshot_of(repo_tree, head="abc123def456", branch="main", inside="true")
    )
    assert subject.repository_id == f"REPO-{_slug(repo_tree.name)}"
    assert subject.assimilated is True
    assert subject.assimilation.validated is True
    assert subject.assimilation.certified is True
    # one realized unit (pkg) -> one accepted assimilation record
    assert subject.assimilation.counts() == {"units": 1, "accepted": 1, "blocked": 0}
    record = subject.assimilation.units[0]
    assert record.accepted and record.outcome == "created"
    # subject object is the canonical repo CKO, depending on the realized unit
    assert subject.subject_object["cko_id"] == subject.repository_id
    assert subject.subject_object["dependencies"] == [record.unit_id]
    # full serialization round-trips through json
    assert json.loads(json.dumps(subject.to_dict()))["repository_id"] == subject.repository_id


def test_assimilate_is_deterministic(repo_tree):
    snap = snapshot_of(repo_tree, head="abc", branch="main", inside="true")
    a = ConstitutionalPipeline(KnowledgeBase([])).assimilate(snap).to_dict()
    b = ConstitutionalPipeline(KnowledgeBase([])).assimilate(snap).to_dict()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_assimilate_empty_repository(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "x.md").write_text("# x\n", encoding="utf-8")
    subject = ConstitutionalPipeline(KnowledgeBase([])).assimilate(
        RepositoryProbe().capture(tmp_path, git=make_runner({}))
    )
    # no realized units, but the subject still validates and certifies
    assert subject.assimilation.units == ()
    assert subject.assimilated is True
    assert subject.frontier.counts()["frontier"] == 1


def test_assimilation_blocks_on_duplicate_unit_identity(repo_tree):
    snap = snapshot_of(repo_tree, head="abc", branch="main", inside="true")
    unit_id = snap.realized_units()[0].unit_id
    # Pre-seed the pipeline base with the unit's identity so the CREATE is blocked.
    seeded = KnowledgeBase(
        [
            CanonicalKnowledgeObject.create(
                cko_id=unit_id,
                kind=KnowledgeKind.PATTERN,
                title="pre-existing",
                statement="a distinct pre-existing occupant of the identity",
                universe=snap.universe,
                authority=KnowledgeAuthority.ENGINEERING,
                owner="OTHER-TEAM",
                lifecycle=Lifecycle.OPERATIONAL,
                version="1.0.0",
            )
        ]
    )
    subject = ConstitutionalPipeline(seeded).assimilate(snap)
    assert subject.assimilation.units_accepted is False
    assert subject.assimilation.accepted is False
    assert subject.assimilated is False


def test_assimilate_accepts_path_and_default_owner(tmp_path):
    (tmp_path / "svc").mkdir()
    (tmp_path / "svc" / "app.py").write_text("run = 1\n", encoding="utf-8")
    subject = ConstitutionalPipeline(KnowledgeBase([])).assimilate(
        tmp_path, default_owner="CUSTOM-OWNER"
    )
    assert subject.subject_object["owner"] == "CUSTOM-OWNER"
    unit_obj_owner = subject.assimilation.units[0]
    assert unit_obj_owner.accepted


def test_assimilator_default_owner_used_for_units(repo_tree):
    # Remove CODEOWNERS so the unit owner falls back to the assimilator default.
    (repo_tree / "CODEOWNERS").unlink()
    snap = snapshot_of(repo_tree, head="abc", branch="main", inside="true")
    subject = RepositoryAssimilator(
        ConstitutionalPipeline(KnowledgeBase([])), default_owner="FALLBACK"
    ).assimilate(snap)
    unit_ids = subject.subject_object["dependencies"]
    assert unit_ids  # the realized pkg unit is present
    assert subject.subject_object["owner"] == "FALLBACK"


# --------------------------------------------------------------------------- emission + CLI


def test_emit_evidence_writes_four_artifacts(repo_tree, tmp_path):
    subject = ConstitutionalPipeline(KnowledgeBase([])).assimilate(
        snapshot_of(repo_tree, head="abc", branch="main", inside="true")
    )
    out = tmp_path / "evidence"
    written = emit_evidence(subject, out)
    assert set(written) == {
        "repository-discovery-report.json",
        "repository-frontier-report.json",
        "repository-drift-report.json",
        "repository-assimilation-evidence.json",
    }
    for name in written:
        payload = json.loads((out / name).read_text(encoding="utf-8"))
        assert payload["repository"]["repository_id"] == subject.repository_id
        assert "report" in payload and "schema" in payload


def test_cli_assimilate(tmp_path, capsys):
    (tmp_path / "code").mkdir()
    (tmp_path / "code" / "m.py").write_text("v = 1\n", encoding="utf-8")
    evidence = tmp_path / "ev"
    rc = integration_cli.main(
        ["--no-constitution", "assimilate", str(tmp_path), "--evidence-dir", str(evidence)]
    )
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["subject"]["assimilated"] is True
    assert len(out["artifacts"]) == 4
    # without an evidence directory the subject is emitted directly
    rc2 = integration_cli.main(["--no-constitution", "assimilate", str(tmp_path)])
    assert rc2 == 0
    assert json.loads(capsys.readouterr().out)["repository_id"].startswith("REPO-")


def test_cli_assimilate_exit_one_when_not_assimilated(tmp_path, capsys, monkeypatch):
    class _NotAssimilated:
        assimilated = False

        def to_dict(self):
            return {"repository_id": "REPO-X", "assimilated": False}

    monkeypatch.setattr(ConstitutionalPipeline, "assimilate", lambda self, repo: _NotAssimilated())
    rc = integration_cli.main(["--no-constitution", "assimilate", str(tmp_path)])
    assert rc == 1
    assert json.loads(capsys.readouterr().out)["assimilated"] is False


def test_value_type_serialization():
    snap = RepositorySnapshot(
        name="r",
        root="/r",
        universe="R",
        head="h",
        branch="main",
        default_branch="main",
        git_available=True,
        units=(_unit("pkg", True, 2),),
        ownership=(OwnershipSignal("*", ("@team",), "CODEOWNERS"),),
        dependencies=(DependencySignal("dep", "1.0", "pyproject.toml", "runtime"),),
        tags=("v1",),
        branches=("main",),
        commits=(CommitRef("h", "tip"),),
        staged=("s",),
        modified=("m",),
        untracked=("u",),
    )
    doc = snap.to_dict()
    assert doc["commits"] == [{"sha": "h", "summary": "tip"}]
    assert doc["repository_id"] == "REPO-R"
    drift = discover_drift(snap).to_dict()
    assert {d["kind"] for d in drift["drift"]} == {"staged", "modified", "untracked"}
    assert any(w["kind"] == "working-tree" for w in drift["workstreams"])


def test_package_json_non_dict_block(tmp_path):
    (tmp_path / "package.json").write_text('{"dependencies": "oops"}', encoding="utf-8")
    snap = RepositoryProbe().capture(tmp_path, git=make_runner({}))
    assert snap.dependencies == ()


def test_default_git_runner_success(tmp_path):
    import shutil
    import subprocess

    git_bin = shutil.which("git")
    if git_bin is None:  # pragma: no cover - git always present in CI
        pytest.skip("git is not available")
    subprocess.run([git_bin, "init"], cwd=tmp_path, capture_output=True, check=True)  # noqa: S603
    out = _default_git_runner(tmp_path)(["rev-parse", "--is-inside-work-tree"])
    assert out is not None and out.strip() == "true"
