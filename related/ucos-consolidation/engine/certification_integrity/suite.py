"""UCI-000001 Part 6 — running the test suite so that two runs are comparable.

ONE RUNNER, THREE RULES. Rules 8, 9, 10 and 11 all reduce to "run the suite under a stated
variation and compare the coverage line sets". They therefore share one runner, because four
runners would let four answers disagree about what "the suite" means — and the repository has
already been bitten by exactly that: ``addopts`` and ``[tool.coverage.run] source`` were two
declarations of one denominator, reconciled by nobody.

WHAT IS HELD FIXED, AND WHY EACH ONE MATTERS.

  * ``COVERAGE_FILE`` is set explicitly per run and never inherited. ``execution.py`` records
    that an ambient value once corrupted a parent's data file.
  * ``PYTHONHASHSEED`` is pinned. Unpinned, dict and set iteration order varies per process, so
    a run-to-run coverage difference could be caused by the harness rather than by the code, and
    Rule 11 would report drift that is really only hash randomisation.
  * ``--cov-fail-under=0`` on every measured run. The floor is a separate decision applied once
    over the combined data; a shard that failed the floor individually would abort before writing
    its data and the combine would then silently measure less.
  * ``-p no:cacheprovider`` so no run can be influenced by the previous run's cache. Without it,
    ``--lf``-style state and stored durations make run B a function of run A, which is precisely
    the independence Rule 11 requires.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass

from engine.certification_integrity import coverage_data
from engine.certification_integrity.model import IntegrityError

#: pytest's own summary line, which is the only place the collected/passed counts are stated in a
#: form that survives ``-q``. Parsed rather than recomputed because a second count of the tests
#: would be a second opinion about what ran.
SUMMARY = re.compile(
    r"^(?:=+ )?(?:(?P<passed>\d+) passed)?"
    r"(?:,? (?P<failed>\d+) failed)?"
    r"(?:,? (?P<skipped>\d+) skipped)?",
    re.M,
)
COUNT = re.compile(r"(\d+) (passed|failed|error|errors|skipped|xfailed|xpassed|deselected)")


@dataclass
class SuiteResult:
    """One measured execution of the suite."""

    label: str
    exit_code: int
    duration_seconds: float
    counts: dict[str, int]
    coverage_xml: str
    report: coverage_data.CoverageReport | None
    stdout_tail: str
    stderr_tail: str

    @property
    def test_count(self) -> int:
        """Tests that actually ran. Skipped and deselected tests did not execute."""
        return self.counts.get("passed", 0) + self.counts.get("failed", 0)

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    def as_record(self) -> dict[str, object]:
        return {
            "label": self.label,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 3),
            "counts": dict(self.counts),
            "test_count": self.test_count,
            "coverage": (
                {
                    "statements": self.report.statements,
                    "covered": self.report.covered,
                    "percent": self.report.percent,
                    "branches_valid": self.report.branches_valid,
                    "branches_covered": self.report.branches_covered,
                    "digest": self.report.digest(),
                    "files": len(self.report.files),
                }
                if self.report
                else None
            ),
        }


def parse_counts(text: str) -> dict[str, int]:
    """Read pytest's outcome counts from its summary output."""
    counts: dict[str, int] = {}
    for value, outcome in COUNT.findall(text):
        key = "error" if outcome.startswith("error") else outcome
        counts[key] = counts.get(key, 0) + int(value)
    return counts


def pytest_argv(
    *,
    targets: list[str] | None = None,
    coverage: bool = True,
    xml_path: str = "coverage.xml",
    shuffle_seed: int | None = None,
    extra: list[str] | None = None,
) -> list[str]:
    """Build the argv for one measured run.

    ``-o addopts=`` clears the project's own 69 ``--cov`` flags and they are re-added from the
    declared scope, so the runner cannot silently measure a different denominator from the one
    ``pyproject.toml`` declares while appearing to use the project default.
    """
    argv = ["{python}", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts="]
    if shuffle_seed is not None:
        argv += ["-p", "engine.certification_integrity.pytest_shuffle"]
    if coverage:
        argv += [f"--cov-report=xml:{xml_path}", "--cov-fail-under=0"]
    argv += extra or []
    argv += targets or []
    return argv


def cov_flags(scope_packages: list[str]) -> list[str]:
    return [f"--cov={package}" for package in sorted(scope_packages)]


def run_in_extraction(
    *,
    root: str,
    sha: str,
    label: str,
    workspace: str | None = None,
    targets: list[str] | None = None,
    coverage: bool = True,
    shuffle_seed: int | None = None,
    coverage_file: str | None = None,
    extra: list[str] | None = None,
    collect_xml_to: str | None = None,
    timeout: float | None = None,
    scope_packages: list[str] | None = None,
) -> tuple[SuiteResult, object]:
    """Run the suite inside a frozen extraction of ``sha`` and read its coverage back."""
    from engine.certification_integrity import immutable
    from engine.certification_integrity import surface as surface_module

    # Prepare first, so the denominator can be read from the FROZEN tree's own declaration. A
    # caller-supplied package list would let the measurement be taken over a scope the commit
    # under test never declared, which is the same defect as an unreconciled second copy of the
    # scope: the figure would be true of some denominator and attributable to no commit.
    extraction = immutable.prepare(root, sha, workspace=workspace)
    if scope_packages is None and coverage:
        scope_packages = sorted(surface_module.read_scope(extraction.root).flag_packages)

    xml_relative = f".uci-coverage-{label}.xml"
    argv = pytest_argv(
        targets=targets,
        coverage=coverage,
        xml_path=xml_relative,
        shuffle_seed=shuffle_seed,
        extra=(extra or []) + (cov_flags(scope_packages) if scope_packages else []),
    )
    env = {
        "PYTHONHASHSEED": "0",
        "COVERAGE_FILE": coverage_file or f".uci-coverage-{label}.data",
    }
    if shuffle_seed is not None:
        env["UCI_SHUFFLE_SEED"] = str(shuffle_seed)

    collect = {xml_relative: collect_xml_to} if collect_xml_to else {}
    started = time.monotonic()
    frozen = immutable.run(
        root,
        argv,
        sha=sha,
        workspace=workspace,
        env=env,
        collect=collect,
        timeout=timeout,
    )
    duration = time.monotonic() - started

    xml_in_extraction = os.path.join(frozen.extraction.root, xml_relative)
    report: coverage_data.CoverageReport | None = None
    if coverage and os.path.exists(xml_in_extraction):
        report = coverage_data.parse(xml_in_extraction, repository=frozen.extraction.root)
    elif coverage:
        raise IntegrityError(
            f"run {label} produced no coverage measurement at {xml_relative} — refusing to treat "
            "an absent measurement as a zero one"
        )

    text = frozen.stdout_tail + "\n" + frozen.stderr_tail
    result = SuiteResult(
        label=label,
        exit_code=frozen.exit_code,
        duration_seconds=duration,
        counts=parse_counts(text),
        coverage_xml=collect_xml_to or xml_in_extraction,
        report=report,
        stdout_tail=frozen.stdout_tail,
        stderr_tail=frozen.stderr_tail,
    )
    return result, frozen
