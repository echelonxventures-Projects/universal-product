"""Tests for TASK-000003 frozen-path guard."""

from __future__ import annotations

import io

import pytest

from engine.foundation.guards import frozen_paths
from engine.foundation.obs.errors import SecurityViolation


def test_detects_frozen_prefixes():
    paths = [
        "00-BOOK/DATA/artifacts.json",
        "00-SOURCE/CONSTITUTIONS/x.docx",
        "99-FREEZE/SOURCE-FILES.txt",
        "engine/foundation/config/config.py",
        "adr/0001.md",
    ]
    violations = frozen_paths.find_frozen_writes(paths)
    assert violations == [
        "00-BOOK/DATA/artifacts.json",
        "00-SOURCE/CONSTITUTIONS/x.docx",
        "99-FREEZE/SOURCE-FILES.txt",
    ]


def test_allows_engine_and_adr_paths():
    assert frozen_paths.find_frozen_writes(["engine/x.py", "adr/1.md", "pyproject.toml"]) == []


def test_path_normalization():
    assert frozen_paths.find_frozen_writes(["./00-BOOK/x"]) == ["00-BOOK/x"]
    assert frozen_paths.find_frozen_writes(["/00-SOURCE/y"]) == ["00-SOURCE/y"]
    assert frozen_paths.find_frozen_writes(["00-BOOK\\z"]) == ["00-BOOK/z"]
    assert frozen_paths.find_frozen_writes(["", "  "]) == []


def test_assert_raises_on_violation():
    with pytest.raises(SecurityViolation) as info:
        frozen_paths.assert_no_frozen_write(["00-BOOK/DATA/x.json"])
    assert info.value.context["paths"] == ["00-BOOK/DATA/x.json"]


def test_assert_passes_when_clean():
    frozen_paths.assert_no_frozen_write(["engine/x.py"])  # no raise


def test_main_returns_zero_when_clean():
    assert frozen_paths.main(["engine/x.py", "adr/1.md"]) == 0


def test_main_returns_one_on_violation(capsys):
    rc = frozen_paths.main(["00-BOOK/x"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "00-BOOK/x" in captured.err


def test_main_reads_stdin(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("engine/a.py\n00-SOURCE/b\n"))
    assert frozen_paths.main(["--stdin"]) == 1
