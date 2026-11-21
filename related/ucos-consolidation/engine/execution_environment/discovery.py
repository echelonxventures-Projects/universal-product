"""UEG-000001 Part 02 — observation. The only module here that touches the machine.

Everything this package knows about the live environment is read exactly once, here, and
handed to :mod:`engine.execution_environment.contract` as a frozen value. That separation is
not tidiness: it is what lets the same measurements run against an environment recorded in
evidence, and what keeps the checks free of any hidden second read that could disagree with
the first.

Reads performed: the running interpreter's own attributes, the installed distribution
metadata, the venv script directory, four configuration files, and ``git rev-parse``. No
network, no package installation, no writes.
"""

from __future__ import annotations

import csv
import io
import os
import platform
import re
import subprocess
import sys
import sysconfig
from importlib import metadata
from pathlib import Path

from engine.execution_environment.model import (
    Dependencies,
    ExecutionEnvironment,
    ExecutionEnvironmentError,
    MachineIdentity,
    RepositoryIdentity,
    RuntimeIdentity,
    Toolchain,
    ToolRecord,
    _digest,
)

# Names a virtual environment creates for itself. They are declared by no distribution, so
# without this set every healthy venv would report its own interpreter as an intruder.
_VENV_INTRINSIC_PREFIXES = ("python", "activate", "Activate")

# The tool names whose PATH resolution EEG-08 reports on. These are the words a developer
# actually types, which is the whole population at risk of resolving somewhere unintended.
_SHADOWABLE_TOOLS = ("python", "python3", "pytest", "ruff", "coverage")

_SERIES_PATTERN = re.compile(r'UCOS_PYTHON_SERIES="\$\{UCOS_PYTHON_SERIES:-([0-9]+\.[0-9]+)\}"')
_PIN_PATTERN = re.compile(r'^\s*"?([A-Za-z0-9_.\-]+)\s*==\s*([^\s";]+)')


def repo_root(start: str | Path | None = None) -> str:
    """Return the repository root, resolved by git.

    Resolved by git and NOT by the location of this file, because that is the exact
    substitution finding F-2 records: a root derived from file layout resolved to the parent
    directory under a shell that does not populate ``BASH_SOURCE`` and a virtual environment
    was built outside the repository.

    Falls back to walking upward for a ``.git`` entry when git is unavailable, and raises
    when neither answers — an unknown root is a fault, never a guess.
    """
    base = Path(start) if start is not None else Path(__file__).resolve().parent
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell, no user input
            ["git", "rev-parse", "--show-toplevel"],  # noqa: S607 - git is resolved from PATH by design
            cwd=str(base),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            return str(Path(completed.stdout.strip()).resolve())
    except (OSError, ValueError):  # pragma: no cover - git absent is covered by the walk below
        pass

    for candidate in [base, *base.parents]:
        if (candidate / ".git").exists():
            return str(candidate.resolve())
    raise ExecutionEnvironmentError(
        f"no repository root could be resolved from {base}; "
        "git did not answer and no .git was found"
    )


def git_identity(repository: str | Path) -> tuple[str, str]:
    """Return ``(branch, commit)`` for *repository*, or explicit UNKNOWN markers.

    An unavailable git is recorded as UNKNOWN rather than raising: the commit is evidence,
    not an integrity condition, and a repository that cannot report its branch is still an
    environment whose interpreter can be verified.
    """

    def _git(*args: str) -> str:
        try:
            completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["git", *args],  # noqa: S607 - git is resolved from PATH by design
                cwd=str(repository),
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:  # pragma: no cover - exercised only on a machine without git
            return "UNKNOWN"
        if completed.returncode != 0:
            return "UNKNOWN"
        return completed.stdout.strip() or "UNKNOWN"

    return _git("rev-parse", "--abbrev-ref", "HEAD"), _git("rev-parse", "HEAD")


def canonical_series(repository: str | Path, series_file: str) -> str:
    """Return the canonical ``major.minor`` declared by the series authority.

    Parsed out of the shell library rather than restated, so the series has one home. A
    declaration whose authority cannot be parsed is a fault: silently choosing a series
    would make every subsequent comparison meaningless.
    """
    path = Path(repository) / series_file
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ExecutionEnvironmentError(
            f"the series authority {path} is unreadable: {error}"
        ) from error
    match = _SERIES_PATTERN.search(source)
    if not match:
        raise ExecutionEnvironmentError(
            f"the series authority {path} declares no UCOS_PYTHON_SERIES this model can parse"
        )
    return match.group(1)


def expected_pins(repository: str | Path, pin_file: str) -> tuple[tuple[str, str], ...]:
    """Return the pinned ``(distribution, version)`` set from the pin authority.

    Parsed from ``pyproject.toml``'s dev extra with ``tomllib`` — the same list, read the
    same way, as ``ucos_expected_deps()`` in ``scripts/ucos-env.sh``. Nothing is restated,
    so adding a pin requires exactly one edit and this model follows it without a change.
    """
    import tomllib

    path = Path(repository) / pin_file
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ExecutionEnvironmentError(
            f"the pin authority {path} is unreadable: {error}"
        ) from error
    except tomllib.TOMLDecodeError as error:
        raise ExecutionEnvironmentError(
            f"the pin authority {path} is not valid TOML: {error}"
        ) from error

    specs = payload.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    pins: list[tuple[str, str]] = []
    for spec in specs:
        match = _PIN_PATTERN.match(str(spec))
        if match:
            pins.append((match.group(1), match.group(2)))
    return tuple(sorted(pins))


def _module_name(distribution: str) -> str:
    """Return the import name for *distribution* using the repository's one alias.

    Only ``pytest-cov`` differs from the mechanical transformation, and it is the alias
    ``scripts/ucos-env.sh`` already carries. A general distribution-to-module mapping does
    not exist in Python metadata; guessing more broadly would produce false negatives.
    """
    return {"pytest-cov": "pytest_cov"}.get(distribution, distribution.replace("-", "_"))


def _importable(module: str) -> bool:
    """Return whether *module* can actually be imported by this interpreter.

    ``find_spec`` rather than ``import``: it answers the question without executing the
    module, so a check cannot be made to do work by the thing it is checking.
    """
    from importlib.util import find_spec

    try:
        return find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def _scan_tool(distribution: str, expected_version: str, scripts_dir: Path) -> ToolRecord:
    """Observe one pinned distribution: version, importability and declared executables.

    ``RECORD`` is read DIRECTLY rather than through ``Distribution.files``. That choice is
    load-bearing and is recorded at length in ``scripts/ucos-env.sh``: ``files()`` applies
    ``skip_missing_files()`` and therefore OMITS any recorded file absent from disk — it
    hides precisely the condition being detected. Measured there: with ``bin/ruff`` deleted,
    ``files()`` yielded ten entries and none was the bin entry, while ``RECORD`` still
    declared it.
    """
    module = _module_name(distribution)
    try:
        dist = metadata.distribution(distribution)
    except metadata.PackageNotFoundError:
        return ToolRecord(
            name=module,
            distribution=distribution,
            expected_version=expected_version,
            installed_version=None,
            importable=False,
        )

    record = dist.read_text("RECORD")
    if record is None:
        return ToolRecord(
            name=module,
            distribution=distribution,
            expected_version=expected_version,
            installed_version=dist.version,
            importable=_importable(module),
            record_readable=False,
        )

    base = Path(dist.locate_file("")).resolve()
    declared: list[str] = []
    missing: list[str] = []
    non_executable: list[str] = []
    for row in csv.reader(io.StringIO(record)):
        if not row or not row[0]:
            continue
        try:
            located = (base / row[0]).resolve()
        except (OSError, ValueError):  # pragma: no cover - malformed RECORD rows are rare
            continue
        if located.parent != scripts_dir:
            continue
        declared.append(str(located))
        if not located.is_file():
            missing.append(str(located))
        elif not os.access(located, os.X_OK):
            non_executable.append(str(located))

    return ToolRecord(
        name=module,
        distribution=distribution,
        expected_version=expected_version,
        installed_version=dist.version,
        importable=_importable(module),
        declared_scripts=tuple(sorted(declared)),
        missing_scripts=tuple(sorted(missing)),
        non_executable_scripts=tuple(sorted(non_executable)),
    )


def _declared_script_names(scripts_dir: Path) -> set[str]:
    """Return every script basename any installed distribution declares in *scripts_dir*.

    Every installed distribution, not only the pinned ones: an executable belonging to a
    transitive dependency is legitimately present, and reporting it would make EEG-08 noise
    that people learn to ignore.
    """
    names: set[str] = set()
    for dist in metadata.distributions():
        record = None
        try:
            record = dist.read_text("RECORD")
        except OSError:  # pragma: no cover - unreadable metadata is rare and non-fatal here
            continue
        if record is None:
            continue
        try:
            base = Path(dist.locate_file("")).resolve()
        except (OSError, ValueError):  # pragma: no cover
            continue
        for row in csv.reader(io.StringIO(record)):
            if not row or not row[0]:
                continue
            try:
                located = (base / row[0]).resolve()
            except (OSError, ValueError):  # pragma: no cover
                continue
            if located.parent == scripts_dir:
                names.add(located.name)
    return names


def unexpected_executables(scripts_dir: Path) -> tuple[str, ...]:
    """Return executables in *scripts_dir* that no installed distribution declares.

    Finding F-4: this venv holds ``pip 2``, ``coverage3 2`` and five more Finder-style
    duplicates. Those particular copies are inert, which is why EEG-08 does not block — but
    a stale duplicate earlier in resolution order is a silently different toolchain, so the
    condition is reported on every run rather than ignored.
    """
    if not scripts_dir.is_dir():
        return ()
    declared = _declared_script_names(scripts_dir)
    found: list[str] = []
    for entry in sorted(scripts_dir.iterdir()):
        if not entry.is_file() or not os.access(entry, os.X_OK):
            continue
        if entry.name in declared:
            continue
        if entry.name.startswith(_VENV_INTRINSIC_PREFIXES):
            continue
        found.append(entry.name)
    return tuple(found)


def shadowing_executables(scripts_dir: Path) -> tuple[str, ...]:
    """Return canonical tool names whose PATH resolution lands outside *scripts_dir*.

    Finding F-3 in one line: on the assessed machine ``pytest`` resolves to
    ``/opt/homebrew/bin/pytest``, which loads THIS repository's ``pyproject.toml`` and then
    fails on ``--cov`` because it has no ``pytest_cov``. The pipeline never invokes a bare
    tool name, so this is reported rather than blocking — but anyone who types ``pytest``
    here meets it.
    """
    import shutil

    shadowed: list[str] = []
    for tool in _SHADOWABLE_TOOLS:
        resolved = shutil.which(tool)
        if resolved is None:
            continue
        if Path(resolved).resolve().parent != scripts_dir:
            shadowed.append(f"{tool} -> {resolved}")
    return tuple(shadowed)


def configuration_fingerprint(
    repository: str | Path, venv_dir: str | Path, extra: tuple[str, ...] = ()
) -> str:
    """Return the digest over every file whose change invalidates the environment.

    The declared triggers, made computable: ``pyproject.toml`` (the pins), the environment
    library (the series and the build procedure), the declaration itself, and the venv's own
    ``pyvenv.cfg`` (which interpreter built it). A file that is absent contributes the
    literal ``ABSENT`` rather than being skipped, so deleting a configuration file is itself
    a change the fingerprint sees.
    """
    repository = Path(repository)
    targets = [
        repository / "pyproject.toml",
        repository / "scripts" / "ucos-env.sh",
        repository / "00-MASTER" / "UEG-000001" / "ueg-declaration.json",
        Path(venv_dir) / "pyvenv.cfg",
        *(repository / item for item in extra),
    ]
    parts: list[str] = []
    for target in targets:
        parts.append(str(target.name))
        try:
            parts.append(_digest(target.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            parts.append("ABSENT")
    return _digest(*parts)


def observe(
    declaration,
    repository: str | Path | None = None,
    command: str | None = None,
    tool_records: tuple[ToolRecord, ...] | None = None,
) -> ExecutionEnvironment:
    """Observe the live environment as an :class:`ExecutionEnvironment`.

    *tool_records* exists for the fingerprint cache: EEG-06's ``RECORD`` scan is the one
    measurably expensive step, so a proven-unchanged environment supplies the previous
    scan's answer instead of repeating it. Every other attribute is re-read every time,
    because every other attribute is an in-process property costing microseconds — and they
    are the ones that catch a wrong interpreter.
    """
    repository = str(repository) if repository is not None else repo_root()
    venv_dir = os.environ.get("UCOS_VENV_DIR") or str(
        Path(repository) / declaration.venv_relative_path
    )
    venv_dir = str(Path(venv_dir))
    scripts_dir = Path(sysconfig.get_path("scripts")).resolve()

    pins = expected_pins(repository, declaration.pin_file)
    if tool_records is None:
        tool_records = tuple(_scan_tool(name, version, scripts_dir) for name, version in pins)

    # sys.executable is recorded AS GIVEN, deliberately unresolved. A virtual environment's
    # bin/python is a symlink into the interpreter that built it, so resolving it reports
    # /opt/homebrew/Cellar/python@3.12/.../bin/python3.12 for a perfectly correct venv — the
    # base interpreter, which is the one thing this path must not be confused with. What
    # "which python am I" means to every caller is the venv path, so that is what is kept.
    # sys.prefix is the attribute that answers whether the venv is the canonical one, and it
    # is resolved because it is compared against a resolved repository root.
    runtime = RuntimeIdentity(
        language="python",
        version=platform.python_version(),
        series=f"{sys.version_info[0]}.{sys.version_info[1]}",
        interpreter_path=str(Path(sys.executable)),
        prefix=str(Path(sys.prefix).resolve()),
        base_prefix=str(Path(sys.base_prefix).resolve()),
    )

    toolchain = Toolchain(
        scripts_directory=str(scripts_dir),
        tools=tool_records,
        unexpected_executables=unexpected_executables(scripts_dir),
        shadowing_executables=shadowing_executables(scripts_dir),
    )

    dependencies = Dependencies(
        expected=pins,
        installed=tuple((tool.distribution, tool.installed_version) for tool in tool_records),
        fingerprint=_digest(
            *[
                f"{tool.distribution}={tool.installed_version}:{','.join(tool.declared_scripts)}"
                for tool in tool_records
            ]
        ),
    )

    branch, commit = git_identity(repository)
    repository_identity = RepositoryIdentity(
        root=str(Path(repository).resolve()),
        branch=branch,
        commit=commit,
        configuration_fingerprint=configuration_fingerprint(repository, venv_dir),
    )

    machine = MachineIdentity(
        platform=platform.system(),
        machine=platform.machine(),
        implementation=platform.python_implementation(),
    )

    return ExecutionEnvironment(
        runtime=runtime,
        toolchain=toolchain,
        dependencies=dependencies,
        repository=repository_identity,
        machine=machine,
        venv_directory=venv_dir,
        command=command,
    )


__all__ = [
    "canonical_series",
    "configuration_fingerprint",
    "expected_pins",
    "git_identity",
    "observe",
    "repo_root",
    "shadowing_executables",
    "unexpected_executables",
]
