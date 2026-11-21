"""Ω-E06 M-04 / W1-4 — the reachability legs of the Repository Intelligence producer.

The Ω-E06 Stage-1 determination measured this producer as **142 commits and 500 files
stale while self-reporting NOT-CERTIFIED**, and named the cause exactly: *"Nothing re-runs
it. There is no ``make rpi`` target."* The certificate was not wrong because the engine was
wrong — it was wrong because no declared entry point named the engine, so nobody ran it,
so a certificate rendered against ``df763bf`` was still being read as current at HEAD.

REG-AUTO-001 P7 requires that discharge be enforced by *tooling gates* rather than author
discipline: at least one Makefile target, at least one workflow and at least one test. This
file is the test leg. It is deliberately a contract test over the Makefile rather than a
smoke test of the engine, because the defect was never in the engine — it was in the absence
of anything that named it. Deleting ``rpi`` or ``rpi-gate`` must break a test, not quietly
re-create a producer nobody re-runs.

The workflow leg is deliberately NOT yet declared. ``rpi-gate`` is fail-closed and the
repository is currently NOT-CERTIFIED on four blocking rules, so wiring CI now would pin
every build red on findings that Wave 3 owns. That leg lands when certification is
reachable; until then this suite and the Makefile targets are the discharge.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CLI = "platform.repository_intelligence.cli"


@pytest.fixture(scope="module")
def makefile() -> str:
    return (REPO / "Makefile").read_text(encoding="utf-8")


# --------------------------------------------------------------- the producer is named
def test_a_makefile_target_names_the_producer(makefile: str) -> None:
    """The whole of M-04: an engine no target names is an engine nobody re-runs."""
    for target in ("rpi", "rpi-report", "rpi-gate"):
        assert f"\n{target}: bootstrap-quiet\n" in makefile, f"{target} is not declared"
    assert CLI in makefile, "no target names the repository-intelligence CLI"


def test_the_rerun_target_persists_the_sealed_artefacts(makefile: str) -> None:
    """``rpi`` must EMIT. A target that only scans refreshes nothing and closes nothing."""
    assert f"$(PY) -m {CLI} emit" in makefile


def test_the_report_target_is_read_only(makefile: str) -> None:
    """``rpi-report`` must scan and never emit, so reading the state cannot mutate it."""
    body = makefile.split("\nrpi-report: bootstrap-quiet\n", 1)[1].split("\n\n", 1)[0]
    assert f"$(PY) -m {CLI} scan" in body
    assert "emit" not in body


# ------------------------------------------------------------------ the gate is closed
def test_the_gate_checks_certification_and_determinism(makefile: str) -> None:
    """Both halves of M-04. Certification alone would pass a producer that cannot
    reproduce itself; determinism alone would pass a NOT-CERTIFIED repository."""
    body = makefile.split("\nrpi-gate: bootstrap-quiet\n", 1)[1].split("\n\n", 1)[0]
    assert f"$(PY) -m {CLI} certify" in body
    assert f"$(PY) -m {CLI} verify" in body


def test_the_gate_fails_closed_on_each_check(makefile: str) -> None:
    """Every check must exit non-zero on failure. A gate that reports and returns 0 is a
    report, and reporting is what let the certificate go 142 commits stale."""
    body = makefile.split("\nrpi-gate: bootstrap-quiet\n", 1)[1].split("\n\n", 1)[0]
    assert body.count("exit 1") == 2, "a check in rpi-gate does not fail closed"
    assert body.count("||") == 2


def test_the_gate_names_its_remediation(makefile: str) -> None:
    """A gate that fails without naming the next command is a gate people learn to skip."""
    body = makefile.split("\nrpi-gate: bootstrap-quiet\n", 1)[1].split("\n\n", 1)[0]
    assert body.count("make rpi-report") == 2


# ------------------------------------------------------------------- the targets are reachable
def test_the_targets_are_declared_phony(makefile: str) -> None:
    assert "\n.PHONY: rpi rpi-report rpi-gate\n" in makefile


def test_help_documents_every_target(makefile: str) -> None:
    """``make help`` is the discovery surface. An undocumented target is one nobody finds,
    which is the same defect as one that does not exist."""
    help_body = makefile.split("\nhelp:\n", 1)[1].split("\n\n", 1)[0]
    for target in ("make rpi", "make rpi-report", "make rpi-gate"):
        assert target in help_body, f"{target} is undocumented in `make help`"


def test_the_targets_bootstrap_rather_than_assume_a_venv(makefile: str) -> None:
    """The producer must run from a fresh shell with no activated venv — the same
    invariant scripts/ucos-env.sh exists to hold."""
    for target in ("rpi", "rpi-report", "rpi-gate"):
        assert f"\n{target}: bootstrap-quiet\n" in makefile
    assert "\nbootstrap-quiet:\n" in makefile
