"""UEG-000001 Part 01 — the Execution Environment entity, and the declaration that shapes it.

The entity is a VALUE. It is observed once, it is frozen, and every derived quantity on it
is a function of the attributes it already carries — there is no method here that reaches
the filesystem, the clock or the network. Observation lives in
:mod:`engine.execution_environment.discovery`; measurement lives in
:mod:`engine.execution_environment.contract`. Keeping the value inert is what makes an
environment recorded in evidence comparable to one observed live: they are the same type,
and neither can change under the other.

The declaration (``00-MASTER/UEG-000001/ueg-declaration.json``) is rehydrated here too,
because refusing an unusable declaration is a property of the model rather than of the gate
that consumes it. A declaration that cannot be read is a FAULT, and a fault is not a verdict.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

RESULT_VALID = "VALID"
RESULT_INVALID = "INVALID"

DECLARATION_RELATIVE_PATH = "00-MASTER/UEG-000001/ueg-declaration.json"


class ExecutionEnvironmentError(Exception):
    """The declaration or an observation is unusable. Raised as a FAULT, never as a verdict."""


def _digest(*parts: str) -> str:
    """Return the sha256 over *parts*, NUL-separated so no two part lists can collide.

    Joining on a printable separator would let ``("a", "b")`` and ``("a\\tb",)`` produce the
    same digest, and a fingerprint whose inputs are ambiguous is a fingerprint that can miss
    a change.
    """
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


# --- the six declared attribute groups -------------------------------------------


@dataclass(frozen=True)
class RuntimeIdentity:
    """What is executing: language, version and the interpreter's own view of itself."""

    language: str
    version: str
    series: str
    interpreter_path: str
    prefix: str
    base_prefix: str

    @property
    def in_virtual_environment(self) -> bool:
        """True iff the interpreter is running inside a virtual environment.

        ``prefix != base_prefix`` is the interpreter's own answer to that question, which is
        why it is asked of the interpreter rather than inferred from a path shape.
        """
        return self.prefix != self.base_prefix

    @property
    def fingerprint(self) -> str:
        return _digest(self.interpreter_path, self.version, self.prefix, self.base_prefix)

    def as_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "version": self.version,
            "series": self.series,
            "interpreter_path": self.interpreter_path,
            "prefix": self.prefix,
            "base_prefix": self.base_prefix,
            "in_virtual_environment": self.in_virtual_environment,
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True)
class ToolRecord:
    """One pinned tool, as expected and as found.

    ``declared_scripts`` comes from the distribution's own ``RECORD``, never from a list in
    this repository: a pin added to ``pyproject.toml`` must not require a second edit here,
    and a wheel that ships an executable with no console-script entry point (ruff does
    exactly this) would be invisible to an entry-points based view.
    """

    name: str
    distribution: str
    expected_version: str
    installed_version: str | None
    importable: bool
    declared_scripts: tuple[str, ...] = ()
    missing_scripts: tuple[str, ...] = ()
    non_executable_scripts: tuple[str, ...] = ()
    record_readable: bool = True

    @property
    def installed(self) -> bool:
        return self.installed_version is not None

    @property
    def version_matches(self) -> bool:
        return self.installed_version == self.expected_version

    @property
    def healthy(self) -> bool:
        return (
            self.installed
            and self.version_matches
            and self.record_readable
            and not self.missing_scripts
            and not self.non_executable_scripts
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "distribution": self.distribution,
            "expected_version": self.expected_version,
            "installed_version": self.installed_version,
            "importable": self.importable,
            "declared_scripts": list(self.declared_scripts),
            "missing_scripts": list(self.missing_scripts),
            "non_executable_scripts": list(self.non_executable_scripts),
            "record_readable": self.record_readable,
            "healthy": self.healthy,
        }


@dataclass(frozen=True)
class Toolchain:
    """The venv script directory and every pinned tool that should live under it."""

    scripts_directory: str
    tools: tuple[ToolRecord, ...]
    unexpected_executables: tuple[str, ...] = ()
    shadowing_executables: tuple[str, ...] = ()

    def tool(self, name: str) -> ToolRecord | None:
        for record in self.tools:
            if record.name == name or record.distribution == name:
                return record
        return None

    def as_dict(self) -> dict[str, Any]:
        return {
            "scripts_directory": self.scripts_directory,
            "tools": [tool.as_dict() for tool in self.tools],
            "unexpected_executables": list(self.unexpected_executables),
            "shadowing_executables": list(self.shadowing_executables),
        }


@dataclass(frozen=True)
class Dependencies:
    """The pinned set, the resolved set, and the fingerprint over what was actually found."""

    expected: tuple[tuple[str, str], ...]
    installed: tuple[tuple[str, str | None], ...]
    fingerprint: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "expected": [list(pair) for pair in self.expected],
            "installed": [list(pair) for pair in self.installed],
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True)
class RepositoryIdentity:
    """Where the environment belongs, resolved by git rather than by file layout.

    Finding F-2 is the whole reason ``root`` is a git answer: deriving it from the location
    of a shell library resolved it to the parent directory under zsh and built a virtual
    environment outside the repository.
    """

    root: str
    branch: str
    commit: str
    configuration_fingerprint: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "branch": self.branch,
            "commit": self.commit,
            "configuration_fingerprint": self.configuration_fingerprint,
        }


@dataclass(frozen=True)
class CheckResult:
    """One declared integrity condition, computed.

    ``blocking`` is carried from the declaration rather than decided here, so the answer to
    "does this refuse execution?" has exactly one home.
    """

    check_id: str
    title: str
    blocking: bool
    holds: bool
    findings: tuple[str, ...] = ()
    expected: str | None = None
    detected: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "check_id": self.check_id,
            "title": self.title,
            "blocking": self.blocking,
            "holds": self.holds,
            "findings": list(self.findings),
        }
        if self.expected is not None:
            payload["expected"] = self.expected
        if self.detected is not None:
            payload["detected"] = self.detected
        return payload


@dataclass(frozen=True)
class MachineIdentity:
    """Platform and architecture — deliberately never a hostname or a user name.

    A hostname identifies a person's machine and would make evidence both non-portable and
    personally identifying. Platform, architecture and interpreter implementation are what
    actually change behaviour, and two machines that agree on all three are interchangeable
    for the purposes of a certified run.
    """

    platform: str
    machine: str
    implementation: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "machine": self.machine,
            "implementation": self.implementation,
        }


@dataclass(frozen=True)
class ExecutionEnvironment:
    """The governed artifact: one observation of one environment, frozen.

    ``environment_id`` is CONTENT identity — derived from the runtime, dependency and
    repository-configuration fingerprints. It deliberately excludes the commit and the
    timestamp: the environment did not change because a source file did, and an identity
    carrying a clock makes two identical environments look different.
    """

    runtime: RuntimeIdentity
    toolchain: Toolchain
    dependencies: Dependencies
    repository: RepositoryIdentity
    machine: MachineIdentity
    venv_directory: str
    checks: tuple[CheckResult, ...] = ()
    command: str | None = None
    observed_at: str | None = None
    cache_state: str = "MISS"

    @property
    def environment_id(self) -> str:
        return _digest(
            self.runtime.fingerprint,
            self.dependencies.fingerprint,
            self.repository.configuration_fingerprint,
            self.machine.platform,
            self.machine.machine,
        )

    @property
    def blocking_failures(self) -> tuple[CheckResult, ...]:
        return tuple(check for check in self.checks if check.blocking and not check.holds)

    @property
    def advisories(self) -> tuple[CheckResult, ...]:
        return tuple(check for check in self.checks if not check.blocking and not check.holds)

    @property
    def result(self) -> str:
        return RESULT_INVALID if self.blocking_failures else RESULT_VALID

    @property
    def valid(self) -> bool:
        return self.result == RESULT_VALID

    def with_checks(self, checks: tuple[CheckResult, ...]) -> ExecutionEnvironment:
        """Return a copy carrying *checks*. The original is never mutated."""
        return ExecutionEnvironment(
            runtime=self.runtime,
            toolchain=self.toolchain,
            dependencies=self.dependencies,
            repository=self.repository,
            machine=self.machine,
            venv_directory=self.venv_directory,
            checks=checks,
            command=self.command,
            observed_at=self.observed_at,
            cache_state=self.cache_state,
        )

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "environment_id": self.environment_id,
            "venv_directory": self.venv_directory,
            "cache_state": self.cache_state,
            "runtime": self.runtime.as_dict(),
            "toolchain": self.toolchain.as_dict(),
            "dependencies": self.dependencies.as_dict(),
            "repository": self.repository.as_dict(),
            "machine": self.machine.as_dict(),
            "checks": [check.as_dict() for check in self.checks],
            "result": self.result,
        }
        if self.command is not None:
            payload["command"] = self.command
        if self.observed_at is not None:
            payload["observed_at"] = self.observed_at
        return payload


# --- the declaration ---------------------------------------------------------------


@dataclass(frozen=True)
class RequiredPlugin:
    """A module whose IMPORTABILITY is required, not merely its recorded version."""

    module: str
    distribution: str


@dataclass(frozen=True)
class CheckDeclaration:
    """One declared check: what it is, and whether failing it refuses execution."""

    check_id: str
    title: str
    blocking: bool
    measures: str
    required_plugins: tuple[RequiredPlugin, ...] = ()


@dataclass(frozen=True)
class Declaration:
    """UEG-000001, rehydrated. Refuses rather than defaults when a field is unusable."""

    artifact_id: str
    version: str
    series_file: str
    series_symbol: str
    pin_file: str
    venv_relative_path: str
    cache_path: str
    evidence_path: str
    checks: tuple[CheckDeclaration, ...]
    invalidation_triggers: tuple[str, ...]
    evidence_records: tuple[str, ...]
    entry_points: tuple[dict[str, Any], ...]
    direct_resolution_files: tuple[str, ...]
    attribute_groups: tuple[str, ...] = ()
    source_path: str = ""
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def check(self, check_id: str) -> CheckDeclaration:
        for declared in self.checks:
            if declared.check_id == check_id:
                return declared
        raise ExecutionEnvironmentError(f"{check_id} is not a declared check")

    @property
    def check_ids(self) -> tuple[str, ...]:
        return tuple(declared.check_id for declared in self.checks)

    @property
    def required_plugins(self) -> tuple[RequiredPlugin, ...]:
        plugins: list[RequiredPlugin] = []
        for declared in self.checks:
            plugins.extend(declared.required_plugins)
        return tuple(plugins)


def _require(payload: dict[str, Any], *path: str) -> Any:
    """Read a nested key, raising rather than defaulting when it is absent.

    Defaulting is what turns an unreadable declaration into a vacuous pass; this is the one
    place that behaviour is refused, once, for every field.
    """
    node: Any = payload
    for key in path:
        if not isinstance(node, dict) or key not in node:
            raise ExecutionEnvironmentError(
                f"the declaration is missing the required key {'.'.join(path)}"
            )
        node = node[key]
    return node


def load_declaration(path: str | Path | None = None, repository: str | Path | None = None):
    """Rehydrate UEG-000001 from *path*, or from the declared location under *repository*."""
    if path is None:
        base = Path(repository) if repository is not None else Path.cwd()
        path = Path(base) / DECLARATION_RELATIVE_PATH
    path = Path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ExecutionEnvironmentError(f"declaration not found at {path}") from error
    except json.JSONDecodeError as error:
        raise ExecutionEnvironmentError(
            f"declaration at {path} is not valid JSON: {error}"
        ) from error

    checks: list[CheckDeclaration] = []
    for item in _require(payload, "checks", "items"):
        plugins = tuple(
            RequiredPlugin(module=plugin["module"], distribution=plugin["distribution"])
            for plugin in item.get("required_plugins", ())
        )
        checks.append(
            CheckDeclaration(
                check_id=item["id"],
                title=item["title"],
                blocking=bool(item["blocking"]),
                measures=item["measures"],
                required_plugins=plugins,
            )
        )
    if not checks:
        raise ExecutionEnvironmentError("the declaration declares no checks")

    return Declaration(
        artifact_id=_require(payload, "artifact_id"),
        version=_require(payload, "version"),
        series_file=_require(payload, "binding", "series_authority", "file"),
        series_symbol=_require(payload, "binding", "series_authority", "symbol"),
        pin_file=_require(payload, "binding", "pin_authority", "file"),
        venv_relative_path=_require(payload, "binding", "venv_directory", "relative_path"),
        cache_path=_require(payload, "binding", "cache_path"),
        evidence_path=_require(payload, "binding", "evidence_path"),
        checks=tuple(checks),
        invalidation_triggers=tuple(
            trigger["trigger"]
            for trigger in _require(payload, "fingerprint_cache", "invalidation_triggers")
        ),
        evidence_records=tuple(_require(payload, "evidence", "records")),
        entry_points=tuple(_require(payload, "separation_of_powers", "entry_points")),
        direct_resolution_files=tuple(_require(payload, "direct_tool_resolution", "measured_over")),
        attribute_groups=tuple(
            group["group"] for group in _require(payload, "model", "attribute_groups")
        ),
        source_path=str(path),
        raw=payload,
    )


__all__ = [
    "DECLARATION_RELATIVE_PATH",
    "RESULT_INVALID",
    "RESULT_VALID",
    "CheckDeclaration",
    "CheckResult",
    "Declaration",
    "Dependencies",
    "ExecutionEnvironment",
    "ExecutionEnvironmentError",
    "MachineIdentity",
    "RepositoryIdentity",
    "RequiredPlugin",
    "RuntimeIdentity",
    "ToolRecord",
    "Toolchain",
    "load_declaration",
]
