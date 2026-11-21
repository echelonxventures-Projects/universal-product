"""ZG-P-02 — coverage determinism tests (in-process + cross-process)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from platform.coverage.engine import CoverageEngine
from platform.tests._coverage_helpers import complete_source

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_in_process_fingerprint_is_stable():
    a = CoverageEngine(complete_source()).fingerprint()
    b = CoverageEngine(complete_source()).fingerprint()
    assert a == b


def test_report_and_evidence_are_stable_in_process():
    r1 = CoverageEngine(complete_source()).report()
    r2 = CoverageEngine(complete_source()).report()
    assert r1 == r2


def _subprocess_fingerprint() -> str:
    script = (
        "from platform.coverage.bootstrap import bootstrap_coverage;"
        "print(bootstrap_coverage().fingerprint())"
    )
    # Strip pytest-cov's subprocess-coverage startup hooks so the child is a clean,
    # independent interpreter (they otherwise error at child startup under coverage).
    env = {k: v for k, v in os.environ.items() if not k.startswith(("COV_CORE", "COVERAGE"))}
    env["PYTHONHASHSEED"] = "0"
    out = subprocess.run(  # noqa: S603 - constant script, trusted interpreter
        [sys.executable, "-c", script],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return out.stdout.strip()


def test_repository_fingerprint_is_reproducible_across_processes():
    """The decisive determinism check: two independent processes must agree."""
    first = _subprocess_fingerprint()
    second = _subprocess_fingerprint()
    assert first
    assert first == second


def test_repository_fingerprint_matches_in_process():
    from platform.coverage.bootstrap import bootstrap_coverage

    assert bootstrap_coverage().fingerprint() == _subprocess_fingerprint()
