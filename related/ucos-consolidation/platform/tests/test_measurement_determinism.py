"""UCOS-EPIC-004 — measurement determinism tests (in-process + cross-process)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from platform.measurement.service import build_measurement_service
from platform.tests._measurement_helpers import complete_source, gapped_source

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_in_process_fingerprint_is_stable():
    assert build_measurement_service(complete_source()).fingerprint() == (
        build_measurement_service(complete_source()).fingerprint()
    )
    assert build_measurement_service(gapped_source()).fingerprint() == (
        build_measurement_service(gapped_source()).fingerprint()
    )


def test_report_is_stable_in_process():
    r1 = build_measurement_service(complete_source()).report()
    r2 = build_measurement_service(complete_source()).report()
    assert r1 == r2


def _subprocess_fingerprint() -> str:
    script = (
        "from platform.measurement.bootstrap import bootstrap_measurement;"
        "print(bootstrap_measurement().fingerprint())"
    )
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
    """The decisive determinism check: two independent processes must agree on Truth."""
    first = _subprocess_fingerprint()
    second = _subprocess_fingerprint()
    assert first
    assert first == second


def test_repository_fingerprint_matches_in_process():
    from platform.measurement.bootstrap import bootstrap_measurement

    assert bootstrap_measurement().fingerprint() == _subprocess_fingerprint()
