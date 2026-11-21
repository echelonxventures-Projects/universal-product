"""Fixtures for the UCOS Ω∞ Phase 1 suite.

TWO KINDS OF TREE, AND THE SECOND ONE IS THE DELIVERABLE. ``tracked_tree`` runs ``git init`` because
the git provider's whole claim is an eligibility boundary that only an index can supply.
``untracked_tree`` deliberately does NOT, and never will: Deliverable 2 requires discovery to work
with no git, hg, svn or p4, and a fixture that quietly initialised a repository would make that
requirement untestable while appearing to test it.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

#: A tree carrying one artifact of each initial type, plus two artifacts whose type cannot be
#: decided from a suffix — which is the pair the classification pipeline exists to separate.
SAMPLE: dict[str, str] = {
    "src/module.py": "VALUE = 1\n",
    "src/nested/deep.py": "def run():\n    return 2\n",
    "docs/guide.md": "# Guide\n\nProse.\n",
    "config/settings.toml": "[table]\nkey = 'value'\n",
    "data/records.json": '{"rows": []}\n',
    "bin/ucos-report": "#!/usr/bin/env python3\nPORT = 1\n",
    "bin/opaque-blob": "\x00binary-ish payload with no marker\n",
}


def git(repository: Path, *arguments: str) -> None:
    subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", *arguments],  # noqa: S607 - git from PATH by design
        cwd=repository,
        check=True,
        capture_output=True,
    )


def _write(root: Path, files: dict[str, str]) -> None:
    for relative, contents in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")


@pytest.fixture
def make_tracked(tmp_path: Path) -> Callable[..., Path]:
    """Build a committed git repository from a ``{locator: contents}`` mapping."""
    counter = {"n": 0}

    def build(files: dict[str, str] | None = None) -> Path:
        counter["n"] += 1
        root = tmp_path / f"tracked{counter['n']}"
        root.mkdir()
        _write(root, files if files is not None else SAMPLE)
        git(root, "init", "-q")
        git(root, "-c", "user.email=t@ucos", "-c", "user.name=Test", "add", "-A")
        git(
            root,
            "-c",
            "user.email=t@ucos",
            "-c",
            "user.name=Test",
            "commit",
            "-q",
            "-m",
            "seed",
        )
        return root

    return build


@pytest.fixture
def tracked_tree(make_tracked: Callable[..., Path]) -> Path:
    return make_tracked()


@pytest.fixture
def untracked_tree(tmp_path: Path) -> Path:
    """A tree that has NEVER been a repository. No .git, no index, no VCS binary consulted."""
    root = tmp_path / "untracked"
    root.mkdir()
    _write(root, SAMPLE)
    return root
