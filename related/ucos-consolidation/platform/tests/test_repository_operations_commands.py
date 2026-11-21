"""EPIC-PLAT-003 — Canonical command reuse tests (Terminal T5)."""

from __future__ import annotations

import os
import sys
from platform.repository_operations.commands import (
    CANONICAL_COMMANDS,
    resolve_command,
    subprocess_command_runner,
)
from platform.repository_operations.errors import StageDefinitionError

import pytest


def test_resolve_command_returns_canonical_argv():
    assert resolve_command("verify") == ("./verify.sh",)
    assert resolve_command("verify-full") == ("./verify.sh", "--full")
    assert "doctor" in CANONICAL_COMMANDS


def test_resolve_command_rejects_non_canonical():
    with pytest.raises(StageDefinitionError):
        resolve_command("rm -rf /")


def test_subprocess_runner_success_and_failure(tmp_path, monkeypatch):
    # Strip pytest-cov's subprocess-coverage startup hooks so the spawned child does
    # not emit statement-only parallel coverage data (which cannot combine with the
    # parent's branch data) — the same discipline the determinism tests use.
    for key in list(os.environ):
        if key.startswith(("COV_CORE", "COVERAGE")):
            monkeypatch.delenv(key, raising=False)
    runner = subprocess_command_runner(tmp_path)
    assert runner([sys.executable, "-c", "raise SystemExit(0)"]) == 0
    assert runner([sys.executable, "-c", "raise SystemExit(3)"]) == 3
