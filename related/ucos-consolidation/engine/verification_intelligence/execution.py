"""UVI-000001 Part 06 — deterministic sharding and parallel execution.

Scheduling changes WHEN a stage runs. It never changes WHAT is measured, and that is a
computed property here rather than an intention: :func:`plan_shards` refuses to return a
partition whose union is not exactly the selection, and :func:`run_tests` re-asserts it
before spawning anything. ``UVI-L-08`` measures the same property from outside.

Sharding is by process, with no test-distribution plugin. Two reasons, in order:

* The assignment stays DECLARED and deterministic. Longest-processing-time over a
  measured cost table, ties broken by path, is a pure function of (selection, costs,
  worker count) — two planners on two machines produce identical shards, which is what
  makes a plan digest meaningful.
* It adds no dependency. ``pyproject.toml`` pins its verification toolchain on purpose
  (DE-04), and a distributed-execution plugin would put shard assignment inside a
  scheduler this repository does not own and cannot reproduce.

Coverage under sharding is combined, never summed. Each shard writes its own
``COVERAGE_FILE``; the run then combines them with the coverage tool itself and
evaluates the floor exactly once, over the union. The denominator is identical to the
one a single process would have produced, because every shard measures the same declared
source set — the ``--cov`` arguments in ``pyproject.toml`` addopts, which no shard
overrides.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass

from engine.verification_intelligence.constitution import (
    DECLARATION,
    load_declaration,
    repo_root,
)
from engine.verification_intelligence.model import (
    Coverage,
    Shard,
    VerificationIntelligenceError,
)
from engine.verification_intelligence.registry import TestObjectRegistry

#: Used when the declaration names no ceiling. Not a policy — a fallback for a
#: declaration that has not yet been read.
FALLBACK_MAX_WORKERS = 8

#: Used when the declaration names no per-shard budget, for the same reason as above.
FALLBACK_SHARD_MEMORY_BUDGET_MB = 1536


def shard_memory_budget_bytes(root: str | None = None) -> int:
    """The declared per-shard memory assumption, in bytes.

    Read rather than assumed, because it IS an assumption: a number that decides how many
    interpreters may run at once does not belong hidden in code. A declaration that cannot
    be read falls back, exactly as the worker ceiling does — a bound nobody can read is
    still better than no bound at all. The reading itself is the constitution's own
    (UCKP-ART-18): a second parser here would be a second opinion about what the
    declaration says, and the two could disagree.
    """
    try:
        sharding = load_declaration(os.path.join(root, DECLARATION) if root else None)["execution"][
            "test_sharding"
        ]
        budget = sharding["shard_memory_budget_mb"]
    except (VerificationIntelligenceError, KeyError, TypeError):
        budget = FALLBACK_SHARD_MEMORY_BUDGET_MB
    if not isinstance(budget, int | float) or isinstance(budget, bool) or budget <= 0:
        budget = FALLBACK_SHARD_MEMORY_BUDGET_MB
    return int(budget) * 1024 * 1024


def memory_headroom_bytes() -> int | None:
    """Memory the host can hand a new process right now, or None where it cannot be read.

    NOT USABLE BY THE PLANNER, AND THE DISTINCTION IS THE POINT. UVI-L-10 requires that
    planning twice over one repository state produce byte-identical bytes, and this value
    moves between two reads, so a plan derived from it would not be reproducible. Execution
    is under no such obligation: how fast a host is willing to run the partition changes no
    measured obligation (UVI-L-08), so the schedule may observe what the plan may not.

    None means "unknown", never "none available", and every caller must read it that way —
    an unreadable host gets the previous unbounded behaviour rather than a guess that
    serialises a healthy machine.
    """
    if sys.platform == "linux":
        try:
            with open("/proc/meminfo", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) * 1024
        except (OSError, IndexError, ValueError):
            return None
        return None
    if sys.platform == "darwin":
        try:
            result = subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
                ["/usr/bin/vm_stat"], capture_output=True, text=True, check=False, timeout=10
            )
            if result.returncode != 0:
                return None
            page = 4096
            free = 0
            for line in result.stdout.splitlines():
                if "page size of" in line:
                    page = int(re.search(r"page size of (\d+) bytes", line).group(1))
                # Inactive and speculative pages are reclaimable on demand, so counting
                # only the free list understates headroom badly on a warm machine and
                # would serialise a host with gigabytes genuinely available.
                elif line.startswith(("Pages free:", "Pages inactive:", "Pages speculative:")):
                    free += int(line.split(":")[1].strip().rstrip("."))
            return free * page
        except (OSError, subprocess.SubprocessError, AttributeError, IndexError, ValueError):
            return None
    return None


def concurrency_limit(wave_size: int, *, root: str | None = None) -> int:
    """How many shard processes this host may run at once, never fewer than one.

    ``UVI_CONCURRENCY`` pins it. Otherwise it is the host's readable headroom divided by
    the declared per-shard budget. The floor of one is what makes this a throttle and not
    a refusal: a host too small for two shards still runs every one of them, in turn.
    """
    override = os.environ.get("UVI_CONCURRENCY")
    if override:
        try:
            pinned = int(override)
        except ValueError as exc:
            raise VerificationIntelligenceError(
                f"UVI_CONCURRENCY is not a number: {override}"
            ) from exc
        if pinned < 1:
            raise VerificationIntelligenceError("UVI_CONCURRENCY must be at least 1")
        return max(1, min(pinned, wave_size)) if wave_size else 1
    headroom = memory_headroom_bytes()
    if headroom is None:
        return max(1, wave_size)
    admits = headroom // shard_memory_budget_bytes(root)
    return max(1, min(wave_size, admits))


def resolve_workers(count: int, *, max_workers: int, override: str | None = None) -> int:
    """How many shards to plan for ``count`` test objects.

    The smaller of the declared ceiling and the machine's own CPU count, never more than
    there are test objects to place, and never fewer than one. ``UVI_WORKERS`` overrides
    both so a measurement can pin the topology.
    """
    if override:
        try:
            pinned = int(override)
        except ValueError as exc:
            raise VerificationIntelligenceError(f"UVI_WORKERS is not a number: {override}") from exc
        if pinned < 1:
            raise VerificationIntelligenceError("UVI_WORKERS must be at least 1")
        return max(1, min(pinned, count)) if count else 1
    cpus = os.cpu_count() or 1
    return max(1, min(max_workers, cpus, count or 1))


def split_currency(registry: TestObjectRegistry) -> str:
    """One line saying how much of the split table the planner could actually use.

    Emitted beside the wave header because the alternative — what happened before this
    existed — is that a stale entry silently costs the run its largest object's
    divisibility and the run looks exactly the same. Not a gate: a stale entry makes a
    plan slower and never wrong, and this reports it rather than refusing it.
    """
    usable, stale = len(registry.splittable), len(registry.stale_splits)
    if not usable and not stale:
        return ""
    line = f"UVI: split table {usable}/{usable + stale} current"
    if stale:
        line += " — stale, placed whole: " + ", ".join(registry.stale_splits)
    return line


def plan_shards(
    test_paths: tuple[str, ...],
    registry: TestObjectRegistry,
    workers: int,
    *,
    isolated: tuple[str, ...] = (),
) -> tuple[Shard, ...]:
    """Partition ``test_paths`` across ``workers`` shards, deterministically.

    Longest-processing-time: place the most expensive object first, always into the
    least-loaded shard, ties broken by shard index and then by path.

    Anything under a declared ``isolated`` prefix is placed instead into a single shard
    in wave 0, which runs alone and BEFORE the concurrent body in wave 1. Pinning such an
    object to one shard of the concurrent body would not have helped: the objects that
    need isolation are the ones that assert a property of the whole working tree, and what
    perturbs them is the OTHER shards, not their neighbours.

    First rather than last, and the order is the point. Such an object must observe the
    tree **as verification found it** — the fixed point the preflight phase just
    established — not the tree eleven thousand tests happened to leave behind. Running it
    last was measured and rejected: the suite regenerates derived views, so the object saw
    a different tree depending on what ran before it, and reached a different verdict for
    reasons that had nothing to do with what it measures.

    This is scheduling isolation and never selection — an isolated object still runs, in
    exactly one shard.

    Raises:
        VerificationIntelligenceError: the partition is not exactly the selection. A
            shard plan that loses or duplicates a test is the one failure mode that
            could turn a green run into a false one.
    """
    if workers < 1:
        raise VerificationIntelligenceError("a shard plan needs at least one worker")
    unique = tuple(sorted(set(test_paths)))
    if not unique:
        return ()
    selection = tuple(sorted({unit_file(unit) for unit in unique}))

    exclusive = tuple(unit for unit in unique if unit_file(unit).startswith(isolated))
    free = tuple(unit for unit in unique if unit not in set(exclusive))

    loads = [0.0] * workers
    buckets: list[list[str]] = [[] for _ in range(workers)]
    for unit in sorted(free, key=lambda u: (-registry.cost_of(u), u)):
        index = min(range(workers), key=lambda i: (loads[i], i))
        buckets[index].append(unit)
        loads[index] += registry.cost_of(unit)

    ordered: list[tuple[int, list[str], float]] = []
    if exclusive:
        ordered.append((0, sorted(exclusive), sum(registry.cost_of(unit) for unit in exclusive)))
    body_wave = 1 if exclusive else 0
    ordered.extend(
        (body_wave, sorted(units), loads[index]) for index, units in enumerate(buckets) if units
    )
    deselects = _assign_remainders(ordered)
    shards = tuple(
        Shard(
            index=index,
            test_paths=tuple(units),
            cost_seconds=cost,
            deselect=tuple(deselects.get(index, ())),
            wave=wave,
        )
        for index, (wave, units, cost) in enumerate(ordered)
    )
    assert_topology_neutral(shards, selection)
    return shards


def _assign_remainders(ordered: list[tuple[int, list[str], float]]) -> dict[int, list[str]]:
    """Give every split file exactly one REMAINDER shard, and return the deselect sets.

    A file split into nodes is covered by the union of those nodes only if the cost model
    knows every node it has. It does not: ``--durations`` hides anything under 0.005s, so
    a fast test in a slow file appears in no shard at all. Rather than trust the model to
    be complete — which cannot be established without collecting — the lowest-indexed
    shard holding any part of the file is given the FILE, and told to deselect exactly the
    nodes its neighbours hold. Coverage of the file is then true by construction: the
    remainder shard runs everything nobody else took, including nodes nothing measured.
    """
    holders: dict[str, list[int]] = {}
    for index, (_wave, units, _cost) in enumerate(ordered):
        for unit in units:
            if "::" in unit:
                holders.setdefault(unit_file(unit), []).append(index)

    deselects: dict[int, list[str]] = {}
    for path, indices in holders.items():
        remainder = min(indices)
        elsewhere = sorted(
            unit
            for index, (_wave, units, _cost) in enumerate(ordered)
            if index != remainder
            for unit in units
            if unit_file(unit) == path and "::" in unit
        )
        ordered[remainder][1][:] = sorted(
            [unit for unit in ordered[remainder][1] if unit_file(unit) != path or "::" not in unit]
            + [path]
        )
        deselects.setdefault(remainder, []).extend(elsewhere)
    for index in deselects:
        deselects[index] = sorted(set(deselects[index]))
    return deselects


def unit_file(unit: str) -> str:
    """The test object a schedulable unit belongs to.

    A unit is either a test file or one ``file::node`` inside it. Both answer to the same
    question — which test object does this cover — and the neutrality check is stated in
    terms of test objects, because that is the granularity the selection is expressed in.
    """
    return unit.split("::", 1)[0]


def assert_topology_neutral(shards: tuple[Shard, ...], selection: tuple[str, ...]) -> None:
    """Refuse any partition that is not exactly the selection.

    Three distinct failures, kept distinct because they mean different things: a unit
    placed twice would run one test in two shards, a test object present in the selection
    and absent from the partition would be a SKIPPED test reported as a pass, and an
    object in the partition that nothing selected would be a plan that invented work. The
    second is the one that could turn a green run into a false one.

    Raises:
        VerificationIntelligenceError: the partition is not exactly the selection.
    """
    placed: list[str] = [unit for shard in shards for unit in shard.test_paths]
    if len(placed) != len(set(placed)):
        duplicated = sorted({unit for unit in placed if placed.count(unit) > 1})
        raise VerificationIntelligenceError(
            f"the shard plan places {len(duplicated)} unit(s) more than once: {duplicated[:5]}"
        )
    covered = {unit_file(unit) for unit in placed}
    # A split file legitimately appears BOTH as a whole unit and as node units: the whole
    # one is the remainder shard, and it must deselect exactly the nodes the others hold.
    # Anything else — a file whole in two shards, or whole with no deselects while its
    # nodes run elsewhere — would run some test twice or lose the file's fast tests.
    whole_counts: dict[str, int] = {}
    for unit in placed:
        if "::" not in unit:
            whole_counts[unit] = whole_counts.get(unit, 0) + 1
    duplicated_files = sorted(path for path, count in whole_counts.items() if count > 1)
    if duplicated_files:
        raise VerificationIntelligenceError(
            f"the shard plan places {len(duplicated_files)} test object(s) whole in more than "
            f"one shard: {duplicated_files[:5]}"
        )
    node_units = {unit for unit in placed if "::" in unit}
    declared_deselects = {unit for shard in shards for unit in shard.deselect}
    if node_units != declared_deselects:
        unguarded = sorted(node_units - declared_deselects)
        phantom = sorted(declared_deselects - node_units)
        raise VerificationIntelligenceError(
            "the shard plan's deselects do not match its node placements: "
            f"{len(unguarded)} node(s) would run twice {unguarded[:3]}, "
            f"{len(phantom)} deselected node(s) run nowhere {phantom[:3]}"
        )
    for path in {unit_file(unit) for unit in node_units}:
        if whole_counts.get(path, 0) != 1:
            raise VerificationIntelligenceError(
                f"{path} is split into nodes but has no remainder shard, so any test in it "
                "that the cost model does not know about would run nowhere"
            )
    missing = sorted(set(selection) - covered)
    extra = sorted(covered - set(selection))
    if missing or extra:
        raise VerificationIntelligenceError(
            "the shard plan is not the selection: "
            f"{len(missing)} missing {missing[:5]}, {len(extra)} unselected {extra[:5]}"
        )


@dataclass(frozen=True, slots=True)
class ShardOutcome:
    """What one shard process did."""

    index: int
    returncode: int
    log_path: str
    tests: int


def _shard_argv(
    python: str, shard: Shard, coverage: Coverage, *, report_path: str | None = None
) -> list[str]:
    """The pytest invocation for one shard.

    Under the floor, ``addopts`` is left INTACT so the derived ``--cov`` set in
    ``pyproject.toml`` still applies — the denominator must not depend on how the run was
    scheduled. Only two things are overridden: the per-shard floor (evaluated once, later,
    over combined data) and the per-shard XML report.

    THE REPORT IS REDIRECTED, NOT CLEARED, AND THE DIFFERENCE WAS MEASURED. This built
    ``--cov-report=`` and its docstring claimed that suppressed the report. It does not.
    ``pytest_cov/plugin.py`` stores reports in a DICT keyed by type (``StoreReport``,
    line 76) and only collapses to "no reports" when the empty entry is the ONLY one
    (line 228). Arriving after ``--cov-report=term-missing --cov-report=xml`` from
    ``addopts`` it is the third key, so both earlier reports stayed in force: every shard
    rendered a full term-missing table, and every shard wrote ``coverage.xml`` to the
    REPOSITORY ROOT — twelve concurrent writers on one path, on the very file the UCI gate
    reads as its coverage evidence. ``test_the_inventory_document_is_deterministic`` failed
    under sharding while passing in isolation for exactly this reason.

    Because the store is keyed by type, naming the type again REPLACES it. Redirecting
    ``xml`` to a shard-private path is therefore a real override, and it needs no change to
    ``addopts`` — so the plugin that derives the denominator is still loaded, which matters:
    clearing ``addopts`` would require re-adding ``-p engine.universal_discovery.pytest_scope``
    by module path, and a shard executing against a tree where that package is not importable
    would die on plugin import rather than run.

    Without the floor, ``addopts`` is cleared and coverage is off, which is what makes a
    developer mode fast and is exactly why a developer mode may not claim the floor.
    """
    deselect: list[str] = []
    for node in shard.deselect:
        deselect += ["--deselect", node]
    if coverage is Coverage.FLOOR_90:
        return [
            python,
            "-m",
            "pytest",
            "--cov-fail-under=0",
            f"--cov-report=xml:{report_path}" if report_path else "--cov-report=",
            "-q",
            *deselect,
            *shard.test_paths,
        ]
    return [
        python,
        "-m",
        "pytest",
        "-o",
        "addopts=",
        "--no-cov",
        "-q",
        *deselect,
        *shard.test_paths,
    ]


def run_tests(
    shards: tuple[Shard, ...],
    coverage: Coverage,
    *,
    root: str | None = None,
    python: str | None = None,
    selection: tuple[str, ...] | None = None,
    stream: object = None,
    only: int | None = None,
    coverage_out: str | None = None,
) -> int:
    """Execute every shard concurrently and return a single exit status.

    Under the coverage floor the shard data files are combined and the floor is
    evaluated once, by the coverage tool, over the union. Any shard failure fails the
    run; the floor is still evaluated so a run reports both facts rather than the first.

    ``only`` executes exactly ONE shard of the plan and is what makes a shard a CI job
    rather than a process. Three properties make that safe, and each is enforced here
    rather than assumed:

    * **The plan is still proved whole.** ``assert_topology_neutral`` runs over the FULL
      plan before ``only`` narrows anything, so every job independently re-derives the
      same partition and re-proves that it unions to exactly the selection. A job that
      cannot prove the whole plan does not run its part of it.
    * **The index is addressed, never counted.** ``only`` must name a shard the plan
      actually contains. This is the failure that motivated the check: ``plan_shards``
      returns ``workers + 1`` shards whenever an isolated object is declared — the
      isolated shard is additional to the concurrent body — so a matrix built from the
      worker count addresses ``0..workers-1`` and never runs the last shard, while every
      job's topology proof still passes, because that proof measures the PLAN and not
      which shards were executed. Refusing an unaddressable index converts that silent
      loss into a fault; ``UVI-L-08`` measures the same property from outside.
    * **The floor is never claimed by a part.** Under the floor a single shard produces
      partial data and no verdict. It must therefore be given ``coverage_out`` to leave
      that data in, and it evaluates nothing; :func:`combine_shards` evaluates the floor
      once, over data from every shard, after all of them have landed.

    Wave ordering needs no cross-job equivalent. A wave exists because an isolated object
    must observe the tree as verification found it rather than the tree eleven thousand
    tests left behind, and a job that runs one shard alone in a fresh checkout satisfies
    that more strongly than ordering within a shared runner ever did.
    """
    out = stream or sys.stderr
    base = root or repo_root()
    interpreter = python or sys.executable
    if selection is not None:
        assert_topology_neutral(shards, tuple(sorted(set(selection))))

    if not shards:
        print(
            "UVI: no test object selected and none escalated — refusing to report a pass",
            file=out,
        )
        return 1

    if only is not None:
        addressable = sorted(shard.index for shard in shards)
        if only not in addressable:
            print(
                f"UVI FAULT: shard {only} is not in this plan, which holds shard(s) "
                f"{addressable}. A matrix addressed by worker count rather than by the "
                f"plan's own indices would lose the shard(s) it never names, and every "
                f"job's topology proof would still pass. Refusing.",
                file=out,
            )
            return 2
        if coverage is Coverage.FLOOR_90 and not coverage_out:
            print(
                "UVI FAULT: one shard under the coverage floor produces partial data and "
                "no verdict. Give it --coverage-out to leave that data in, and evaluate "
                "the floor once with `combine` over every shard.",
                file=out,
            )
            return 2
        shards = tuple(shard for shard in shards if shard.index == only)

    # --- the interpreter must be able to evaluate the floor it is about to claim -----------
    #
    # Every shard inherits THIS process's interpreter (`sys.executable`, threaded through as
    # `python`), and every floor-mode shard argv carries `--cov-fail-under` and `--cov-report`.
    # Those are pytest-cov's options. Run under an interpreter without pytest-cov installed and
    # all thirteen shards die identically before collecting anything:
    #
    #     pytest: error: unrecognized arguments: --cov-report=term-missing --cov-report=xml
    #                                            --cov-fail-under=90 --cov-fail-under=0 …
    #     exit 4
    #
    # Thirteen usage errors are a legible symptom of an illegible cause, and the run reports
    # "shard(s) FAILED" — which reads as a test failure rather than as a toolchain that cannot
    # measure. The canonical planes all pass the repository venv (`verify.sh` and every Makefile
    # target use `$(VENV)/bin/python`), so this is reachable by invoking the CLI with a bare
    # `python3`; on a machine whose `python3` is a different series from the pinned toolchain
    # that is one keystroke away. Refusing HERE costs one import check and converts an
    # unreadable failure into a named one, before any subprocess is spawned.
    #
    # Checked only under the floor: the developer modes pass `--no-cov` and are correct without
    # the plugin, so requiring it there would refuse runs that would have worked.
    if coverage is Coverage.FLOOR_90:
        probe = subprocess.run(  # noqa: S603
            [interpreter, "-c", "import pytest_cov"],
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode != 0:
            print(
                f"UVI FAULT: {interpreter} cannot import pytest_cov, so the coverage floor "
                f"cannot be evaluated and every shard would exit 4 on unrecognized arguments. "
                f"Run through the repository venv (./verify.sh, or make uvi) rather than a "
                f"bare interpreter.",
                file=out,
            )
            return 2

    # Deliberately NOT inside the repository. The first implementation passed `dir=base`
    # for no better reason than filesystem locality, and an interrupted run left
    # `uvi-logs-*` and `uvi-coverage-*` directories in the tree — which UCOS-UGA-001 then
    # measured as unidentified objects, because to a governance gate a directory in the
    # working tree is an object whether or not the process that made it is still alive.
    # A verification run must not be able to dirty the thing it is verifying, even when it
    # dies. Coverage data files are referenced by absolute path, so location is free.
    data_dir = tempfile.mkdtemp(prefix="uvi-coverage-")
    log_dir = tempfile.mkdtemp(prefix="uvi-logs-")
    try:
        failed: list[int] = []
        # Waves run in order; shards within a wave run together. Wave 0 is the ordinary
        # concurrent body, and a later wave is the exclusive one — declared for objects
        # measured to be unsafe beside anything else, and therefore only meaningful if
        # nothing from an earlier wave is still running when it starts.
        for wave in sorted({shard.wave for shard in shards}):
            in_wave = [shard for shard in shards if shard.wave == wave]
            processes: list[tuple[Shard, subprocess.Popen, str] | None] = [None] * len(in_wave)

            def _start(
                position: int,
                _in_wave: list[Shard] = in_wave,
                _processes: list[tuple[Shard, subprocess.Popen, str] | None] = processes,
            ) -> None:
                shard = _in_wave[position]
                env = dict(os.environ)
                if coverage is Coverage.FLOOR_90:
                    env["COVERAGE_FILE"] = os.path.join(data_dir, f".coverage.{shard.index}")
                log_path = os.path.join(log_dir, f"shard-{shard.index}.log")
                handle = open(log_path, "wb")  # noqa: SIM115 - closed in the wait loop below
                process = subprocess.Popen(  # noqa: S603
                    _shard_argv(
                        interpreter,
                        shard,
                        coverage,
                        # Shard-private, outside the repository, and discarded with the
                        # rest of `data_dir`. The combined document is written once, later,
                        # by `_combine_and_evaluate`; a shard's partial XML is not evidence
                        # and must not land where anything reads it.
                        report_path=os.path.join(data_dir, f"shard-{shard.index}.xml"),
                    ),
                    cwd=base,
                    env=env,
                    stdout=handle,
                    stderr=subprocess.STDOUT,
                )
                process.stdout = handle  # type: ignore[assignment] - kept alive for closing
                _processes[position] = (shard, process, log_path)

            # BOUNDED, BECAUSE THE PLAN IS A PARTITION AND NOT A PERMISSION TO OVERSUBSCRIBE.
            # Every shard in the wave used to start at once, so on one host the shard count
            # WAS the concurrency — and a fourteen-core workstation planning twelve
            # coverage-instrumented interpreters is killed by the operating system rather
            # than refused by a gate. CI never saw it: there each shard is its own job on its
            # own runner. The partition is untouched, so the plan digest and UVI-L-08 are
            # untouched; only the rate of starting changes, which UVI-L-08 says changes no
            # obligation. A shard starts as its predecessor finishes, so the wave costs more
            # wall clock and still measures exactly the same units.
            limit = concurrency_limit(len(in_wave), root=base)
            for position in range(min(limit, len(in_wave))):
                _start(position)
            unstarted = min(limit, len(in_wave))
            print(
                f"UVI: wave {wave} — {len(in_wave)} shard(s) running concurrently over "
                f"{sum(len(s.test_paths) for s in in_wave)} unit(s)"
                + (" (exclusive)" if len(in_wave) == 1 and len(shards) > 1 and wave == 0 else "")
                + (f" [throttled to {limit} at once]" if limit < len(in_wave) else ""),
                file=out,
            )
            for position in range(len(in_wave)):
                entry = processes[position]
                assert entry is not None  # noqa: S101 - every position is started before its wait
                shard, process, log_path = entry
                code = process.wait()
                if process.stdout is not None:
                    process.stdout.close()
                # A seat came free, so the next shard takes it before this one's log is
                # rendered. Waiting in index order keeps the transcript deterministic
                # whatever order the shards actually finish in, which is why the output of
                # a throttled wave is byte-identical to the output of an unthrottled one.
                if unstarted < len(in_wave):
                    _start(unstarted)
                    unstarted += 1
                print(
                    f"\n----- shard {shard.index} ({len(shard.test_paths)} unit(s), "
                    f"wave {shard.wave}) -----",
                    file=out,
                )
                with open(log_path, encoding="utf-8", errors="replace") as handle:
                    print(handle.read().rstrip(), file=out)
                if code != 0:
                    failed.append(shard.index)

        status = 1 if failed else 0
        if failed:
            print(f"\nUVI: shard(s) FAILED: {sorted(failed)}", file=out)

        if coverage is Coverage.FLOOR_90:
            if only is None:
                status = _combine_and_evaluate(interpreter, base, data_dir, out) or status
            else:
                status = _export_shard_data(data_dir, only, str(coverage_out), out) or status
        return status
    finally:
        _remove_tree(data_dir)
        _remove_tree(log_dir)


def _combine_and_evaluate(python: str, base: str, data_dir: str, out: object) -> int:
    """Combine the shard data, evaluate the floor once, and emit coverage.xml.

    Every subprocess here is given an EXPLICIT ``COVERAGE_FILE`` pointing at the
    canonical ``.coverage`` beside the repository root. Inheriting the ambient value
    instead was a real defect and not a hypothetical one: run under a parent that had
    already set ``COVERAGE_FILE`` — a nested measurement, or a developer measuring one
    package — the combine wrote its result into the PARENT's data file and corrupted it.
    The canonical location is also the one the declared ``coverage report`` stage reads
    afterwards, so naming it here is what makes that stage read this run's data.
    """
    files = sorted(
        os.path.join(data_dir, name)
        for name in os.listdir(data_dir)
        if name.startswith(".coverage")
    )
    if not files:
        print(
            "UVI: no coverage data was produced by any shard — refusing to claim the floor",
            file=out,
        )
        return 1
    env = dict(os.environ)
    env["COVERAGE_FILE"] = os.path.join(base, ".coverage")

    def _coverage(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(  # noqa: S603
            [python, "-m", "coverage", *args],
            cwd=base,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    combine = _coverage("combine", "--keep", *files)
    if combine.returncode != 0:
        print(f"UVI: coverage combine failed\n{combine.stdout}{combine.stderr}", file=out)
        return 1
    # `coverage xml` applies the configured fail_under too, so a run below the floor would
    # exit non-zero HERE and be reported as "coverage xml failed" — a true verdict behind a
    # false explanation, and the artifact would still have been written. The floor is
    # evaluated by exactly one command, so the xml step is told not to evaluate it.
    xml = _coverage("xml", "--fail-under=0")
    if xml.returncode != 0:
        print(f"UVI: coverage xml failed\n{xml.stdout}{xml.stderr}", file=out)
        return 1
    report = _coverage("report", "--fail-under=90")
    print(report.stdout.rstrip(), file=out)
    if report.stderr.strip():
        print(report.stderr.rstrip(), file=out)
    if report.returncode != 0:
        print("UVI: the combined coverage total is below the declared floor", file=out)
        return 1
    return 0


def _export_shard_data(data_dir: str, index: int, out_dir: str, out: object) -> int:
    """Leave one shard's coverage data where the combine step can collect it.

    Named by SHARD INDEX rather than by pid or hostname, because the combine step's
    fails-closed check is `which shards arrived`, and it can only ask that of a name that
    carries the shard's identity. The exported names still begin with ``.coverage`` so the
    coverage tool's own combine treats them as data files.
    """
    produced = sorted(name for name in os.listdir(data_dir) if name.startswith(".coverage"))
    if not produced:
        print(
            f"UVI: shard {index} produced no coverage data — refusing to export a shard "
            f"that measured nothing, because the combine step would then evaluate the "
            f"floor over a denominator this shard never contributed to",
            file=out,
        )
        return 1
    os.makedirs(out_dir, exist_ok=True)
    # The ordinal is unconditional. Naming the single-file case differently would make the
    # exported name depend on HOW MANY files a shard produced — a population the exporter
    # would then be asserting rather than reporting, which is the closure form UCON-L-15
    # refuses. The combine reads the shard index out of the name either way.
    for ordinal, name in enumerate(produced):
        shutil.copyfile(
            os.path.join(data_dir, name),
            os.path.join(out_dir, f".coverage.shard-{index}.{ordinal}"),
        )
    print(
        f"UVI: shard {index} exported {len(produced)} coverage data file(s) to {out_dir}; "
        f"the floor is not evaluated by a shard",
        file=out,
    )
    return 0


def shard_indices_present(data_dir: str) -> tuple[int, ...]:
    """Which shards left data in ``data_dir``, by the index in their exported names."""
    seen: set[int] = set()
    for name in os.listdir(data_dir):
        match = re.match(r"^\.coverage\.shard-(\d+)(?:\.\d+)?$", name)
        if match:
            seen.add(int(match.group(1)))
    return tuple(sorted(seen))


def combine_shards(
    expected: tuple[int, ...],
    data_dir: str,
    *,
    root: str | None = None,
    python: str | None = None,
    stream: object = None,
) -> int:
    """Combine cross-job shard data and evaluate the coverage floor exactly once.

    THIS FAILS CLOSED ON A MISSING SHARD, and that is the whole reason it exists rather
    than the in-process path being pointed at a download directory. In one process a shard
    that dies before writing data also exits non-zero, so the run is already failing and
    the missing file cannot mint a false pass. A combine job has no such backstop: it sees
    artifacts, not exit codes. A job that was cancelled, skipped, or whose upload failed
    contributes nothing, and the coverage tool would happily combine what did arrive and
    report a floor over a suite fragment — a green verdict for a run that never measured
    the missing shard's code. So the expected indices are named by the plan, and every one
    of them must have arrived before any verdict is computed.

    ``expected`` comes from the plan's own shard indices, never from a worker count; see
    :func:`run_tests` for why those two numbers differ.
    """
    out = stream or sys.stderr
    base = root or repo_root()
    interpreter = python or sys.executable
    if not expected:
        print("UVI: no shard was expected — refusing to claim the floor", file=out)
        return 1
    if not os.path.isdir(data_dir):
        print(f"UVI: no coverage data directory at {data_dir}", file=out)
        return 1
    arrived = shard_indices_present(data_dir)
    missing = sorted(set(expected) - set(arrived))
    unexpected = sorted(set(arrived) - set(expected))
    if missing:
        print(
            f"UVI: {len(missing)} of {len(expected)} shard(s) left no coverage data: "
            f"{missing}. The floor is a property of the whole suite and cannot be "
            f"evaluated over the part that arrived. Refusing.",
            file=out,
        )
        return 1
    if unexpected:
        print(
            f"UVI: coverage data arrived from shard(s) {unexpected} that this plan does "
            f"not contain, so the data and the plan disagree about what ran. Refusing.",
            file=out,
        )
        return 1
    print(
        f"UVI: all {len(expected)} shard(s) reported; combining and evaluating the floor "
        f"once over the union",
        file=out,
    )
    return _combine_and_evaluate(interpreter, base, data_dir, out)


def _remove_tree(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)
