"""UEG-000001 Part 05 — execution evidence.

Finding F-5: certification recorded what was verified and never what verified it, so two
runs under different interpreters were indistinguishable in the evidence. This module emits
the eight records the declaration names, and the declaration is what it iterates — a record
declared and not produced is a fault here, not a gap discovered later.

The timestamp appears in evidence and NOWHERE else. It is not an input to the environment
identity, not an input to any fingerprint, and not an input to the cache key: a clock inside
an identity makes two identical environments look different, which is the defect
:mod:`engine.temporal` exists to prevent.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from engine.execution_environment.model import (
    Declaration,
    ExecutionEnvironment,
    ExecutionEnvironmentError,
)


def _pytest_executable(environment: ExecutionEnvironment) -> str | None:
    """Return the pytest executable this environment declares, if it declares one."""
    record = environment.toolchain.tool("pytest")
    if record is None:
        return None
    for script in record.declared_scripts:
        if Path(script).name == "pytest":
            return script
    return None


def build(
    environment: ExecutionEnvironment, declaration: Declaration, command: str | None = None
) -> dict[str, Any]:
    """Return the evidence payload for *environment*.

    Every key the declaration lists under ``evidence.records`` must be produced. The mapping
    from a declared record to the value that discharges it lives here and only here, and
    ``assert_complete`` measures that the mapping is total.
    """
    record = environment.toolchain.tool("pytest")
    payload = {
        "artifact_id": declaration.artifact_id,
        "python executable path": environment.runtime.interpreter_path,
        "python version": environment.runtime.version,
        "pytest executable path": _pytest_executable(environment),
        "pytest version": record.installed_version if record else None,
        "environment identity": environment.environment_id,
        "dependency fingerprint": environment.dependencies.fingerprint,
        "repository commit": environment.repository.commit,
        "validation timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "repository branch": environment.repository.branch,
        "repository root": environment.repository.root,
        "command": command or environment.command,
        "result": environment.result,
        "cache_state": environment.cache_state,
        "checks": [check.as_dict() for check in environment.checks],
    }
    assert_complete(payload, declaration)
    return payload


def assert_complete(payload: dict[str, Any], declaration: Declaration) -> None:
    """Raise unless every declared record is present in *payload*.

    A declared record with no producer is the same class of defect as a declared check with
    no implementation: the declaration asserts something the artifact does not contain, and
    a reader of the evidence has no way to know.
    """
    missing = [record for record in declaration.evidence_records if record not in payload]
    if missing:
        raise ExecutionEnvironmentError(
            "the evidence declares records that nothing produces: " + ", ".join(missing)
        )


def write(
    environment: ExecutionEnvironment,
    declaration: Declaration,
    repository: str | Path,
    command: str | None = None,
) -> Path:
    """Write the evidence for *environment* to the declared path, atomically."""
    payload = build(environment, declaration, command)
    path = Path(repository) / declaration.evidence_path
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return path


__all__ = ["assert_complete", "build", "write"]
