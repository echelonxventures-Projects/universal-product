"""UEG-000001 Part 03 — the integrity conditions, computed.

One function per declared check, each taking the observed environment and returning a
:class:`CheckResult`. None of them reads the machine: every fact they need is already on the
value observation produced, which is what makes a check reproducible from evidence and what
guarantees two checks can never disagree about what they saw.

``assess`` iterates the DECLARATION rather than a list in this file, so a check declared and
not implemented is a fault at assessment time instead of a silent omission — the failure
mode where a condition exists in JSON, is believed to be enforced, and is enforced by
nothing.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from engine.execution_environment.discovery import canonical_series
from engine.execution_environment.model import (
    CheckDeclaration,
    CheckResult,
    Declaration,
    ExecutionEnvironment,
    ExecutionEnvironmentError,
)


def _result(
    declared: CheckDeclaration,
    findings: list[str],
    expected: str | None = None,
    detected: str | None = None,
) -> CheckResult:
    return CheckResult(
        check_id=declared.check_id,
        title=declared.title,
        blocking=declared.blocking,
        holds=not findings,
        findings=tuple(findings),
        expected=expected,
        detected=detected,
    )


def check_repository(
    environment: ExecutionEnvironment, declared: CheckDeclaration, declaration: Declaration
) -> CheckResult:
    """EEG-01 — the running interpreter and its venv belong to THIS repository.

    Finding F-2 is this check's whole reason for existing: a root resolved from file layout
    instead of from git built a virtual environment in the parent directory, and nothing
    noticed for sixteen days.
    """
    findings: list[str] = []
    root = Path(environment.repository.root)
    venv = Path(environment.venv_directory).resolve()
    prefix = Path(environment.runtime.prefix)

    if root not in venv.parents:
        findings.append(f"the virtual environment {venv} is not inside the repository root {root}")
    # sys.prefix, NOT the interpreter binary. A venv's bin/python is a symlink into the base
    # interpreter that built it, which lives in the system package manager's tree by design —
    # requiring the BINARY to sit under the repository would fail every correctly built venv
    # on this platform. The prefix is the environment's own location, and it is exactly the
    # attribute that was wrong in finding F-2.
    if root not in prefix.parents:
        findings.append(
            f"the active environment prefix {prefix} is not inside the repository root {root}"
        )
    return _result(
        declared,
        findings,
        expected=f"an environment prefix under {root}",
        detected=str(prefix),
    )


def check_virtual_environment(
    environment: ExecutionEnvironment, declared: CheckDeclaration, declaration: Declaration
) -> CheckResult:
    """EEG-02 — the interpreter IS the canonical venv, not merely near it.

    Assumption A3: a directory existing where a venv is expected proves nothing about what
    is running. ``sys.prefix`` is the interpreter's own answer, and it is the only one that
    cannot be faked by a path that happens to look right.
    """
    findings: list[str] = []
    expected_prefix = Path(environment.venv_directory).resolve()
    actual_prefix = Path(environment.runtime.prefix)

    if not environment.runtime.in_virtual_environment:
        findings.append(
            f"the interpreter is not running inside a virtual environment "
            f"(prefix == base_prefix == {environment.runtime.prefix})"
        )
    if actual_prefix != expected_prefix:
        findings.append(f"sys.prefix is {actual_prefix}, not the canonical {expected_prefix}")
    return _result(declared, findings, expected=str(expected_prefix), detected=str(actual_prefix))


def check_interpreter(
    environment: ExecutionEnvironment, declared: CheckDeclaration, declaration: Declaration
) -> CheckResult:
    """EEG-03 — the interpreter series is the canonical one.

    The series is READ from the authority that declares it, every time, rather than carried
    as a constant here. Two places holding a version is how the two drift.
    """
    series = canonical_series(environment.repository.root, declaration.series_file)
    findings: list[str] = []
    if environment.runtime.series != series:
        findings.append(
            f"interpreter series {environment.runtime.series} != canonical {series} "
            f"(declared by {declaration.series_file})"
        )
    return _result(
        declared,
        findings,
        expected=f"python {series}",
        detected=f"python {environment.runtime.version} at {environment.runtime.interpreter_path}",
    )


def check_pytest_ownership(
    environment: ExecutionEnvironment, declared: CheckDeclaration, declaration: Declaration
) -> CheckResult:
    """EEG-04 — the pytest this interpreter would import belongs to this environment.

    Finding F-3. The dangerous property of the global pytest is not that it exists but that
    it FINDS this repository's ``pyproject.toml``: it attempts the certified gate under an
    interpreter that cannot satisfy it, so the failure looks like a repository problem.
    """
    from importlib.util import find_spec

    findings: list[str] = []
    prefix = Path(environment.runtime.prefix)
    detected = "<not importable>"
    try:
        spec = find_spec("pytest")
    except (ImportError, ValueError):
        spec = None

    if spec is None or not spec.origin:
        findings.append("pytest is not importable by this interpreter")
    else:
        detected = spec.origin
        origin = Path(spec.origin).resolve()
        if prefix not in origin.parents:
            findings.append(f"pytest resolves to {origin}, which is outside {prefix}")
    return _result(declared, findings, expected=f"a pytest under {prefix}", detected=detected)


def check_required_plugins(
    environment: ExecutionEnvironment, declared: CheckDeclaration, declaration: Declaration
) -> CheckResult:
    """EEG-05 — every declared plugin IMPORTS, not merely records a version.

    Assumption A4. ``pytest-cov`` recorded at 6.0.0 with ``pytest_cov`` unimportable is a
    real state, and it is exactly the state that reports a healthy toolchain right up to the
    moment the certified command aborts on ``unrecognized arguments: --cov``.
    """
    from importlib.util import find_spec

    findings: list[str] = []
    for plugin in declared.required_plugins:
        try:
            spec = find_spec(plugin.module)
        except (ImportError, ValueError):
            spec = None
        if spec is None:
            findings.append(
                f"{plugin.module} (distribution {plugin.distribution}) is not importable"
            )
    modules = ", ".join(plugin.module for plugin in declared.required_plugins)
    return _result(
        declared,
        findings,
        expected=f"importable: {modules}",
        detected="all importable" if not findings else "; ".join(findings),
    )


def check_dependencies(
    environment: ExecutionEnvironment, declared: CheckDeclaration, declaration: Declaration
) -> CheckResult:
    """EEG-06 — every pin installed at its version, with every declared executable usable.

    The executable half is preserved from ``scripts/ucos-env.sh`` for the reason recorded
    there: pip treats a requirement as satisfied on version metadata alone, so a lost
    ``bin/<tool>`` survives an ordinary install and fails at the point of use instead of at
    the point of verification.
    """
    findings: list[str] = []
    for tool in environment.toolchain.tools:
        if not tool.installed:
            findings.append(f"{tool.distribution} is not installed")
            continue
        if not tool.version_matches:
            findings.append(
                f"{tool.distribution} {tool.installed_version} != pinned {tool.expected_version}"
            )
        if not tool.record_readable:
            findings.append(
                f"{tool.distribution}: installed-files manifest absent, executables unverifiable"
            )
        for script in tool.missing_scripts:
            findings.append(f"{tool.distribution}: {script} is declared but absent")
        for script in tool.non_executable_scripts:
            findings.append(f"{tool.distribution}: {script} is present but not executable")
    return _result(
        declared,
        findings,
        expected=f"{len(environment.dependencies.expected)} pinned distributions, healthy",
        detected=f"{sum(1 for tool in environment.toolchain.tools if tool.healthy)} healthy",
    )


def check_configuration(
    environment: ExecutionEnvironment, declared: CheckDeclaration, declaration: Declaration
) -> CheckResult:
    """EEG-07 — the configuration this environment is measured against is readable and real.

    Fail-closed in the direction that matters: an unparseable ``pyproject.toml`` yields an
    EMPTY expected set, under which EEG-06 passes vacuously over nothing. An empty
    expectation is therefore a failure, not a pass.
    """
    findings: list[str] = []
    root = Path(environment.repository.root)
    for relative in (declaration.pin_file, declaration.series_file):
        if not (root / relative).is_file():
            findings.append(f"{relative} is absent from {root}")
    if not environment.dependencies.expected:
        findings.append(
            f"{declaration.pin_file} declares no pinned dev dependencies this model can parse; "
            "an empty expectation would make every dependency check pass vacuously"
        )
    if not Path(environment.venv_directory).is_dir():
        findings.append(
            f"the declared virtual environment {environment.venv_directory} does not exist"
        )
    return _result(
        declared,
        findings,
        expected=f"{declaration.pin_file} + {declaration.series_file} readable, pins non-empty",
        detected=f"{len(environment.dependencies.expected)} pins parsed",
    )


def check_global_leakage(
    environment: ExecutionEnvironment, declared: CheckDeclaration, declaration: Declaration
) -> CheckResult:
    """EEG-08 — global shadowing and unexpected executables, reported and non-blocking.

    Finding F-4 and the PATH half of F-3. Non-blocking is a deliberate determination, not a
    softening: the present instances are inert Finder duplicates and a Homebrew pytest the
    pipeline never invokes, and a blocking check that must be suppressed to get work done is
    a check that gets deleted. Reported every run, so the class stays visible.
    """
    findings: list[str] = []
    for entry in environment.toolchain.shadowing_executables:
        findings.append(f"PATH resolves {entry}, outside {environment.toolchain.scripts_directory}")
    for name in environment.toolchain.unexpected_executables:
        findings.append(
            f"{name} is executable in {environment.toolchain.scripts_directory} "
            "but declared by no installed distribution"
        )
    return _result(
        declared,
        findings,
        expected="no shadowing tool on PATH, no undeclared executable in the venv",
        detected=f"{len(findings)} condition(s)",
    )


CHECKS: dict[str, Callable[[ExecutionEnvironment, CheckDeclaration, Declaration], CheckResult]] = {
    "EEG-01": check_repository,
    "EEG-02": check_virtual_environment,
    "EEG-03": check_interpreter,
    "EEG-04": check_pytest_ownership,
    "EEG-05": check_required_plugins,
    "EEG-06": check_dependencies,
    "EEG-07": check_configuration,
    "EEG-08": check_global_leakage,
}


def assess(environment: ExecutionEnvironment, declaration: Declaration) -> ExecutionEnvironment:
    """Compute every DECLARED check and return the environment carrying the results.

    Iterating the declaration is what makes "declared but unimplemented" a fault rather than
    a silent omission. The inverse — implemented but undeclared — is measured by the test
    suite over :data:`CHECKS` and the declaration's own id set, in both directions.
    """
    results: list[CheckResult] = []
    for declared in declaration.checks:
        implementation = CHECKS.get(declared.check_id)
        if implementation is None:
            raise ExecutionEnvironmentError(
                f"{declared.check_id} is declared but implemented by nothing; "
                "a declared check that nothing computes is enforced by nothing"
            )
        results.append(implementation(environment, declared, declaration))
    return environment.with_checks(tuple(results))


__all__ = [
    "CHECKS",
    "assess",
    "check_configuration",
    "check_dependencies",
    "check_global_leakage",
    "check_interpreter",
    "check_pytest_ownership",
    "check_repository",
    "check_required_plugins",
    "check_virtual_environment",
]
