"""Fixtures for the UCOS-OMEGA-001 suite: real git repositories, because git is the boundary.

WHY EVERY FIXTURE RUNS ``git init``. Ω-1's population is ``git ls-files``, chosen so a control
decides the same way on a developer's machine and on a clean checkout. A fixture that wrote files
and skipped git would exercise a code path the gate never takes, and the one defect that boundary
exists to prevent — a verdict that depends on untracked local debris — would be untestable.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest


def git(repository: Path, *arguments: str) -> None:
    subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", *arguments],  # noqa: S607 - git from PATH by design
        cwd=repository,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def make_repo(tmp_path: Path) -> Callable[..., Path]:
    """Build a tracked repository from a ``{relative path: contents}`` mapping."""

    counter = {"n": 0}

    def build(files: dict[str, str], *, pyproject: str = "[tool.ucos]\n") -> Path:
        counter["n"] += 1
        repository = tmp_path / f"repo{counter['n']}"
        repository.mkdir()
        for relative, contents in files.items():
            target = repository / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents, encoding="utf-8")
        (repository / "pyproject.toml").write_text(pyproject, encoding="utf-8")
        git(repository, "init", "-q")
        git(repository, "add", "-A")
        return repository

    return build


@pytest.fixture
def layered_repo(make_repo: Callable[..., Path]) -> Path:
    """One repository exercising every shape the derivation distinguishes.

    ``alpha`` holds sub-packages only, so it is measured per sub-package. ``beta`` holds modules
    directly, so it is measured whole. ``alpha/tests`` carries a helper with no ``test_`` prefix,
    which is the shape that defeated the naming-keyed predicate. ``00-GOV`` is a governance home
    whose name is not a Python identifier.
    """
    return make_repo(
        {
            "alpha/__init__.py": "",
            "alpha/core/service.py": "def run():\n    return 1\n",
            "alpha/core/helper.py": (
                "import json\n\n\ndef load(text):\n    return json.loads(text)\n"
            ),
            "alpha/namespaced/deep.py": "VALUE = 1\n",
            "alpha/tests/__init__.py": "",
            "alpha/tests/conftest.py": "import pytest\n",
            "alpha/tests/support.py": "def double(n):\n    return n * 2\n",
            "alpha/tests/test_service.py": (
                "from alpha.core.service import run\n"
                "from alpha.tests.support import double\n\n\n"
                "def test_run():\n    assert double(run()) == 2\n"
            ),
            "beta/__init__.py": "",
            "beta/module.py": "NAME = 'beta'\n",
            "beta/tests/test_module.py": "def test_name():\n    pass\n",
            "00-GOV/PROG-001/prog_engine.py": "def main():\n    return 0\n",
            "Makefile": "prog:\n\t@python3 -m alpha.core.service\n",
        }
    )
