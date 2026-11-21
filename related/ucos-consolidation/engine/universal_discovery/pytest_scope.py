"""UCOS-OMEGA-001 Part 10 (Ω-1) — the coverage denominator, injected from discovery.

WHY A PLUGIN AND NOT A CONFIG BLOCK.

``pyproject.toml`` held the denominator twice: 78 ``--cov=`` flags in ``addopts`` and 78 paths in
``[tool.coverage.run] source``, two independent lists reconciled by nobody. They happened to agree.
Nothing required them to. And both were enumerations, so adding ``quantum/`` meant editing both,
which means the Ω-1 success criterion — a new tree governed with ZERO configuration changes — was
unreachable while the denominator lived in a static file.

So the denominator moved to where it can be computed. This plugin runs before pytest-cov starts
its collector and hands it the set ``engine/universal_discovery/discovery.py`` derives from
``git ls-files '*.py'``. The two lists are now ONE derivation, and drift between them is not a
thing that is checked for — it is a thing that cannot occur.

THE HOOK ORDERING IS LOAD-BEARING, so it is stated rather than assumed. ``pytest-cov`` declares
``pytest_load_initial_conftests`` with ``tryfirst=True``, and because it is registered from an
entry point it registers AFTER a ``-p`` plugin, which under pluggy's LIFO ordering would let it
run FIRST. A ``tryfirst`` implementation here would therefore lose the race. A HOOKWRAPPER cannot:
everything before the ``yield`` runs ahead of every non-wrapper implementation, ``tryfirst``
included. That is why this is a wrapper, and changing it to ``tryfirst`` would silently restore
the enumerated denominator by leaving ``cov_source`` empty.

FAIL CLOSED, LOUDLY. If discovery cannot run, this raises. A plugin that swallowed the error would
hand pytest-cov an empty source list, and an empty source list measures everything at 100%.
"""

from __future__ import annotations

import os
import subprocess

import coverage
import pytest

#: Set to a non-empty value to skip injection. Exists for ONE purpose — bisecting a suspected
#: defect in discovery itself — and is read here rather than passed as a flag so it cannot end up
#: in ``addopts`` and quietly become the default.
DISABLE = "UCOS_OMEGA_NO_INJECT"


# --- The denominator is a set of PACKAGES, and coverage must be told so ---------------
#
# WHY THIS EXISTS, STATED AS THE MEASUREMENT THAT PRODUCED IT. `coverage xml` was rendering 423
# of the 467 files the run had actually measured: the root element claimed 43,174 statements and
# the body carried 38,307, so 4,867 — 11.27% — were absent from the document while every summary
# percentage still agreed. Only a per-file consumer could see the loss, and absence renders as
# nothing rather than as zero.
#
# THE MECHANISM, which is coverage's own dispatch and not a bug in it. `inorout.py` sorts each
# declared `source` entry by asking `os.path.isdir(src)`: a directory becomes a SOURCE ROOT, and
# anything else is treated as an importable package. Every file is then named in coverage.xml
# RELATIVE TO ITS ROOT. Six of the derived packages — application, data, infrastructure,
# intelligence, scripts, service — are flat top-level layers whose package name IS a directory
# name, so each became its own root and every file under it was keyed by a bare basename.
# `service/model_meta.py`, `application/model_meta.py` and `data/model_meta.py` all reduced to
# `model_meta.py`, one `<class>` element survived, and 37 such keys were claimed by more than one
# file. The dotted packages were never affected: `engine.foundation` is not a directory, so it
# was already dispatched as a package and keyed from the repository root.
#
# THE CORRECTION, applied at the one boundary where the two kinds are still distinguishable.
# A `source` entry that names a directory is moved to `source_pkgs`, which is where the flat
# layers belonged all along. The DENOMINATOR IS UNCHANGED — the same packages are measured, and
# `platform/tests/test_coverage_scope.py` still holds — but no directory is promoted to a root,
# so there is exactly one implied root and every file is keyed by its full package path. A file
# can then collide with nothing, because a full path is unique by construction.
#
# WHY A WRAPPER RATHER THAN A CONFIG KEY. `[tool.coverage.run] source_pkgs` would be a static
# enumeration of the very list Ω-1 exists to derive, and it would drift from the derivation the
# first time a layer was added. pytest-cov builds its `Coverage` objects itself and exposes no
# hook between construction and `start()`, so the construction call is the only place the derived
# set can still be corrected. The wrapper is idempotent and applies only while this plugin is
# loaded.
_COVERAGE_INIT = coverage.Coverage.__init__


def _coverage_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
    """Route directory-named sources to ``source_pkgs`` so no layer becomes its own root."""
    declared = list(kwargs.get("source") or [])
    directories = [entry for entry in declared if os.path.isdir(entry)]
    if directories:
        remaining = [entry for entry in declared if entry not in directories]
        kwargs["source"] = remaining or None
        kwargs["source_pkgs"] = list(kwargs.get("source_pkgs") or []) + directories
    return _COVERAGE_INIT(self, *args, **kwargs)


if getattr(coverage.Coverage.__init__, "__module__", None) != __name__:
    _coverage_init.__module__ = __name__
    coverage.Coverage.__init__ = _coverage_init  # type: ignore[method-assign]


def _repository_root() -> str:
    """The repository root, from this file's own location. Three parents up from the package."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _child_environment() -> dict[str, str]:
    """The spawn environment with ambient measurement state removed.

    THE SCRUB CANNOT IMPORT WHAT IT SCRUBS OUT OF. The one authoring of the ambient set is
    ``engine.certification_integrity.immutable``; importing it from here would run that module's
    body before the collector starts — the exact defect ``derive`` exists to end, re-opened one
    file over. The filter is therefore by prefix, and the equivalence to the canonical list is
    not assumed: ``test_the_child_environment_drops_every_ambient_measurement_variable`` in
    ``engine/tests/universal_discovery/test_surface_and_gate.py`` checks every member of
    ``AMBIENT_MEASUREMENT_VARS`` against this output, so a fifth ambient name added upstream
    fails a test rather than silently leaking into a derivation child.
    """
    return {
        key: value
        for key, value in os.environ.items()
        if not (key.startswith("COV_CORE_") or key == "COVERAGE_FILE")
    }


def derive() -> tuple[list[str], list[str]]:
    """``(coverage sources, test roots)``, both derived. The single source of the denominator.

    THE DERIVATION RUNS IN A CHILD PROCESS, AND THE REASON IS A MEASUREMENT. This hook fires
    at `pytest_load_initial_conftests` — before pytest-cov starts the collector — so importing
    `engine.universal_discovery.discovery` here executed that package's import-time lines
    (class bodies, frozen dataclasses, the seeded constants) outside measurement, and coverage
    reported them as misses forever: 455 statements across `engine/universal_discovery` and the
    `engine/omega_infinite` cluster it pulls in, unfixable by any test, because the lines only
    ever run at import. Measured both ways at HEAD: a shard run carrying the derivation in-proc
    reports `line-rate 0.994`; the identical tests with an explicit `--cov` (which takes the
    early-return below and never imports anything here) report `1.0`. Same code, same tests —
    only the import order differed. A child computing the same derived answer over `git ls-files`
    costs one interpreter start, keeps the parent's first import of the package UNDER coverage,
    and preserves Ω-1 exactly: the list is still produced by `discovery.derived_scope`, never
    enumerated. A failure in the child is a FAULT raised here, not a fallback to a guess.
    """

    root = _repository_root()
    code = (
        "import sys;"
        f"sys.path.insert(0, {root!r});"
        "from engine.universal_discovery import discovery;"
        f"t, p, _, _ = discovery.derived_scope({root!r});"
        "print(','.join(t) + '\\x1f' + ','.join(p))"
    )
    result = subprocess.run(  # noqa: S603 — the executable is this interpreter, the code is ours
        [os.sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
        env=_child_environment(),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"the denominator could not be derived (exit {result.returncode}): "
            f"{result.stderr.strip() or 'the child produced no message'}"
        )
    test_roots, _, packages = result.stdout.strip().partition("\x1f")
    return ([p for p in packages.split(",") if p], [t for t in test_roots.split(",") if t])


@pytest.hookimpl(hookwrapper=True)
def pytest_load_initial_conftests(early_config, parser, args):  # type: ignore[no-untyped-def]
    """Hand pytest-cov a derived denominator, and pytest a derived collection set."""
    if os.environ.get(DISABLE):
        yield
        return

    namespace = early_config.known_args_namespace
    if getattr(namespace, "cov_source", None):
        # Someone passed --cov= explicitly on the command line. An explicit request wins: a
        # developer measuring one package must not be silently given all 79, and overriding it
        # here would make the narrow run report a meaningless percentage.
        yield
        return

    packages, test_roots = derive()
    namespace.cov_source = packages

    # Collection: only when the invocation named no path of its own. `testpaths` used to carry
    # this and was the third enumeration of the same fact — the one that left 3,995 passing tests
    # collected by nothing for the interval between two programmes.
    #
    # THE POSITIONAL TEST IS `file_or_dir`, NOT A SCAN OF `args`, and the difference was measured.
    # Scanning `args` for an entry that does not start with "-" counts the VALUE of an option as a
    # path: `-p engine.universal_discovery.pytest_scope` in `addopts` made this plugin believe the
    # user had named a target, so it skipped extending, pytest fell back to collecting the whole
    # rootdir, and 90 tests under the generated, gitignored `realization/tests` joined the run.
    # `file_or_dir` is pytest's own parsed positional list, so option values cannot appear in it.
    if not getattr(namespace, "file_or_dir", None):
        args.extend(test_roots)

    yield


def pytest_report_header(config) -> str:  # type: ignore[no-untyped-def]
    """State the derived denominator in the run's own header, so a reader can check it.

    A denominator computed silently is a denominator nobody audits, which is how the previous one
    stayed wrong for five trees.
    """
    if os.environ.get(DISABLE):
        return "UCOS-OMEGA-001: scope injection DISABLED by environment"
    source = getattr(config.option, "cov_source", None) or []
    return (
        f"UCOS-OMEGA-001: coverage denominator DERIVED from git ls-files — "
        f"{len(source)} packages, no enumeration"
    )
