"""UCI-000001 Part 8 — reproducibility, shard equivalence and order independence.

THE THREE RULES THIS MODULE MEASURES, AND THE ONE THING THEY HAVE IN COMMON.

  Rule 8/11  run the suite N times over one frozen tree; require every run identical
  Rule 10    run it once whole and once as K shards; require combine(shards) == whole
  Rule 9     run it under N random permutations; require every run identical

All three compare covered-line SETS, never percentages, using the single ``coverage_data.compare``
primitive. That choice is what makes the claims provable rather than merely plausible: two runs
that executed different lines can report the same percentage, so a percentage comparison would
pass on exactly the divergence these rules exist to catch.

WHAT "IDENTICAL" MEANS HERE, PRECISELY.

Per file, the same set of line numbers hit and the same set missed. Not the same total, not the
same ratio, not the same digest of a summary — the sets. ``CoverageReport.digest`` covers both the
hit and missed sets for the same reason: a run that stopped measuring a file entirely and a run
that measured it and found it uncovered must not produce the same digest, because Rule 11 lists
"measured files change" and "coverage changes" as separate failures.

WHY THE SHARD PROOF IS AN INDEPENDENT IMPLEMENTATION.

``engine/verification_intelligence/execution.py`` already shards and combines, and the mandate
asks for that logic to be AUDITED. An audit that ran the audited code would be a tautology, so the
sharding here is deliberately its own: a simple deterministic partition of the collected test
files, combined with ``coverage combine`` directly. If the two disagree, the disagreement is the
finding. This module makes no claim about which one would be right.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field

from engine.certification_integrity import coverage_data, immutable, suite
from engine.certification_integrity.model import IntegrityError


@dataclass
class EquivalenceFinding:
    """The outcome of comparing a set of runs that were required to agree."""

    rule: str
    question: str
    runs: list[dict[str, object]] = field(default_factory=list)
    comparisons: list[dict[str, object]] = field(default_factory=list)
    identical: bool = False
    failures: list[str] = field(default_factory=list)

    @property
    def holds(self) -> bool:
        return self.identical and not self.failures

    def as_record(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "question": self.question,
            "holds": self.holds,
            "identical": self.identical,
            "failures": list(self.failures),
            "runs": list(self.runs),
            "comparisons": list(self.comparisons),
        }


def _compare_all(results: list[suite.SuiteResult]) -> tuple[bool, list[dict[str, object]]]:
    """Compare every run against the first. N-1 comparisons prove the N-way equality.

    Comparing against the first rather than pairwise is sufficient because set equality is
    transitive, and it keeps the evidence linear in N rather than quadratic — which matters when
    N is 100.
    """
    comparisons: list[dict[str, object]] = []
    identical = True
    baseline = results[0]
    for other in results[1:]:
        if baseline.report is None or other.report is None:
            identical = False
            comparisons.append(
                {
                    "first": baseline.label,
                    "second": other.label,
                    "identical": False,
                    "reason": "a run produced no coverage measurement",
                }
            )
            continue
        diff = coverage_data.compare(baseline.report, other.report)
        diff["first_label"] = baseline.label
        diff["second_label"] = other.label
        comparisons.append(diff)
        if not diff["identical"]:
            identical = False
    return identical, comparisons


def _collect_failures(results: list[suite.SuiteResult]) -> list[str]:
    failures = []
    for result in results:
        if not result.passed:
            failures.append(
                f"{result.label}: pytest exited {result.exit_code} "
                f"(counts={result.counts or 'unparsed'})"
            )
    return failures


def reproducibility(
    root: str,
    sha: str,
    *,
    runs: int = 3,
    workspace: str | None = None,
    targets: list[str] | None = None,
    evidence_dir: str | None = None,
    timeout: float | None = None,
) -> EquivalenceFinding:
    """Rules 8 and 11: run the suite ``runs`` times over one frozen tree; require A == B == C."""
    if runs < 2:
        raise IntegrityError(
            "reproducibility over a single run is not a measurement; at least two runs are "
            "required for the comparison to exist"
        )
    finding = EquivalenceFinding(
        rule="Rule 8/11",
        question=f"are {runs} independent runs over the frozen tree {sha[:12]} identical?",
    )
    results: list[suite.SuiteResult] = []
    for index in range(runs):
        label = f"repro-{index + 1}"
        target_xml = os.path.join(evidence_dir, f"coverage-{label}.xml") if evidence_dir else None
        result, _frozen = suite.run_in_extraction(
            root=root,
            sha=sha,
            label=label,
            workspace=workspace,
            targets=targets,
            collect_xml_to=target_xml,
            timeout=timeout,
        )
        results.append(result)
        finding.runs.append(result.as_record())
    finding.failures = _collect_failures(results)
    finding.identical, finding.comparisons = _compare_all(results)
    return finding


def order_independence(
    root: str,
    sha: str,
    *,
    seeds: list[int],
    workspace: str | None = None,
    targets: list[str] | None = None,
    evidence_dir: str | None = None,
    timeout: float | None = None,
) -> EquivalenceFinding:
    """Rule 9: the verdict and the coverage must not depend on the order tests ran in.

    The unseeded run is included as the first element, so the comparison answers the question that
    matters — "does a permutation change the result relative to the order the repository actually
    uses" — rather than only whether permutations agree with each other.
    """
    finding = EquivalenceFinding(
        rule="Rule 9",
        question=(
            f"do {len(seeds)} randomized permutations agree with the declared order over "
            f"{sha[:12]}?"
        ),
    )
    results: list[suite.SuiteResult] = []
    baseline, _ = suite.run_in_extraction(
        root=root,
        sha=sha,
        label="order-declared",
        workspace=workspace,
        targets=targets,
        collect_xml_to=(
            os.path.join(evidence_dir, "coverage-order-declared.xml") if evidence_dir else None
        ),
        timeout=timeout,
    )
    results.append(baseline)
    finding.runs.append(baseline.as_record())
    for seed in seeds:
        label = f"order-seed-{seed}"
        result, _ = suite.run_in_extraction(
            root=root,
            sha=sha,
            label=label,
            workspace=workspace,
            targets=targets,
            shuffle_seed=seed,
            collect_xml_to=(
                os.path.join(evidence_dir, f"coverage-{label}.xml") if evidence_dir else None
            ),
            timeout=timeout,
        )
        record = result.as_record()
        record["seed"] = seed
        results.append(result)
        finding.runs.append(record)
    finding.failures = _collect_failures(results)
    finding.identical, finding.comparisons = _compare_all(results)
    return finding


def partition(items: list[str], shards: int) -> list[list[str]]:
    """Deterministically split ``items`` into ``shards`` groups.

    Round-robin over the sorted list. Deliberately NOT the cost-model-weighted
    longest-processing-time assignment UVI uses: the point is to shard differently from the
    implementation under audit, so that an agreement between them is evidence rather than a shared
    assumption.
    """
    if shards < 2:
        raise IntegrityError("a shard equivalence proof needs at least two shards")
    ordered = sorted(items)
    groups: list[list[str]] = [[] for _ in range(shards)]
    for index, item in enumerate(ordered):
        groups[index % shards].append(item)
    empty = [i for i, group in enumerate(groups) if not group]
    if empty:
        raise IntegrityError(
            f"shards {empty} received no tests; an empty shard contributes no coverage data and "
            "would make the combined total silently smaller than the whole run"
        )
    return groups


def discover_test_modules(root: str, testpaths: list[str]) -> list[str]:
    """Every test module, from the filesystem rather than from pytest's collection.

    NOT named ``test_files``: pytest collects any module-level callable whose name begins with
    ``test_``, so the original name made this helper a collected test with an unsatisfiable
    ``root`` fixture, and the shard proof's own helper reported as a suite error.

    Reading the filesystem keeps the shard population independent of the plugin set: a collection
    hook that dropped items would otherwise shrink both the shards and the whole run together and
    the equality would still hold over a smaller suite.
    """
    found: list[str] = []
    for testpath in testpaths:
        base = os.path.join(root, testpath)
        for current, _dirs, files in os.walk(base):
            for name in sorted(files):
                if name.startswith("test_") and name.endswith(".py"):
                    found.append(
                        os.path.relpath(os.path.join(current, name), root).replace(os.sep, "/")
                    )
    if not found:
        raise IntegrityError(
            f"no test modules found under {testpaths} — a shard proof over an empty suite would "
            "compare nothing to nothing and report success"
        )
    return sorted(found)


def shard_equivalence(
    root: str,
    sha: str,
    *,
    shards: int = 4,
    workspace: str | None = None,
    evidence_dir: str | None = None,
    timeout: float | None = None,
) -> EquivalenceFinding:
    """Rule 10: prove ``combine(shards) == single full execution``, per line.

    Runs the whole suite once, then the same suite split ``shards`` ways with one coverage data
    file per shard, combines them with ``coverage combine`` and compares the two line sets.
    """
    from engine.certification_integrity import surface as surface_module

    finding = EquivalenceFinding(
        rule="Rule 10",
        question=f"does combining {shards} shards equal one full execution over {sha[:12]}?",
    )

    extraction = immutable.prepare(root, sha, workspace=workspace)
    scope = surface_module.read_scope(extraction.root)
    modules = discover_test_modules(extraction.root, list(scope.testpaths))
    groups = partition(modules, shards)

    whole, _ = suite.run_in_extraction(
        root=root,
        sha=sha,
        label="whole",
        workspace=workspace,
        collect_xml_to=(os.path.join(evidence_dir, "coverage-whole.xml") if evidence_dir else None),
        timeout=timeout,
    )
    finding.runs.append(whole.as_record())

    shard_results: list[suite.SuiteResult] = []
    shard_data: list[str] = []
    for index, group in enumerate(groups):
        label = f"shard-{index + 1}"
        data_file = f".uci-shard-{index + 1}.data"
        result, _ = suite.run_in_extraction(
            root=root,
            sha=sha,
            label=label,
            workspace=workspace,
            targets=group,
            coverage_file=data_file,
            timeout=timeout,
        )
        record = result.as_record()
        record["modules"] = len(group)
        finding.runs.append(record)
        shard_results.append(result)
        shard_data.append(data_file)

    combined_xml = _combine(extraction.root, extraction.python, shard_data)
    combined = coverage_data.parse(combined_xml, repository=extraction.root)
    if evidence_dir:
        os.makedirs(evidence_dir, exist_ok=True)
        import shutil

        shutil.copy2(combined_xml, os.path.join(evidence_dir, "coverage-combined.xml"))

    finding.failures = _collect_failures([whole, *shard_results])
    if whole.report is None:
        finding.failures.append("the whole run produced no coverage measurement")
        finding.identical = False
        return finding

    diff = coverage_data.compare(whole.report, combined)
    diff["first_label"] = "whole"
    diff["second_label"] = "combined-shards"
    finding.comparisons.append(diff)
    finding.identical = bool(diff["identical"])

    # Rule 10 names statements, branches, files and percentages explicitly, so each is asserted
    # separately rather than being taken as implied by the line-set equality.
    for name, left, right in (
        ("statements", whole.report.statements, combined.statements),
        ("covered", whole.report.covered, combined.covered),
        ("files", len(whole.report.files), len(combined.files)),
        ("branches_valid", whole.report.branches_valid, combined.branches_valid),
        ("branches_covered", whole.report.branches_covered, combined.branches_covered),
    ):
        if left != right:
            finding.failures.append(f"{name} differ: whole={left} combined={right}")
    return finding


def _combine(root: str, python: str, data_files: list[str]) -> str:
    """``coverage combine`` the shard data files and render XML, inside the extraction."""
    present = [name for name in data_files if os.path.exists(os.path.join(root, name))]
    if not present:
        raise IntegrityError(
            "no shard produced coverage data — refusing to claim a combined measurement over "
            "nothing, which is the failure engine/verification_intelligence/execution.py also "
            "refuses by name"
        )
    # No ambient measurement environment reaches these subprocesses: pytest-cov's bootstrap
    # would otherwise auto-start a second, unconfigured coverage inside `coverage combine`
    # itself and write statement-only data beside the caller's branch data. The set stripped
    # is named once, in immutable.AMBIENT_MEASUREMENT_VARS.
    env = immutable.clean_environment(COVERAGE_FILE=os.path.join(root, ".uci-combined.data"))
    env.pop("PYTHONHASHSEED", None)
    combine = subprocess.run(  # noqa: S603
        [python, "-m", "coverage", "combine", "--keep", *present],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if combine.returncode != 0:
        raise IntegrityError(f"coverage combine failed: {combine.stderr[-2000:]}")
    target = os.path.join(root, ".uci-combined.xml")
    render = subprocess.run(  # noqa: S603
        [python, "-m", "coverage", "xml", "--fail-under=0", "-o", target],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if render.returncode != 0:
        raise IntegrityError(f"rendering combined coverage failed: {render.stderr[-2000:]}")
    return target
