"""UEG-000001 — Universal Execution Governance: Execution Environment Intelligence.

The execution environment was the last unfenced input to certification. Every other subject
in this repository — objects, decisions, stages, primitives, lifecycles — has an identity, a
declared model, a fail-closed gate and evidence. The interpreter that ran all of those gates
had none of it, so a certified result could not say what produced it, and a verification
command was allowed to repair the very environment it was reporting on.

``UCOS-EXECUTION-ENVIRONMENT-ASSESSMENT.md`` measured the consequences. Two are worth
carrying here because they are why this package exists rather than a shell patch:

* a repository root derived from ``BASH_SOURCE`` resolved to the PARENT directory under
  zsh and built a virtual environment outside the repository, which sat unnoticed for
  sixteen days (F-2);
* ``./verify.sh`` could ``rm -rf`` a drifted virtual environment and reinstall it, so drift
  detected was drift erased and the run reported green having destroyed the evidence (F-1).

Six parts, in dependency order:

* :mod:`engine.execution_environment.model` — the ``ExecutionEnvironment`` entity and the
  declaration, rehydrated and refused when unusable.
* :mod:`engine.execution_environment.discovery` — the only module that touches the machine.
* :mod:`engine.execution_environment.contract` — the eight declared checks, computed.
* :mod:`engine.execution_environment.fingerprint` — the cache, which may skip one
  measurement and never a verdict.
* :mod:`engine.execution_environment.evidence` — what verified this run, not only what was
  verified.
* :mod:`engine.execution_environment.gate` — fail-closed, OBSERVE MODE.

It holds no authority over versions. ``pyproject.toml [dev]`` pins the toolchain and
``scripts/ucos-env.sh`` declares the canonical series; both are parsed, never restated.
"""

from __future__ import annotations

from engine.execution_environment.model import (
    DECLARATION_RELATIVE_PATH,
    RESULT_INVALID,
    RESULT_VALID,
    CheckDeclaration,
    CheckResult,
    Declaration,
    Dependencies,
    ExecutionEnvironment,
    ExecutionEnvironmentError,
    MachineIdentity,
    RepositoryIdentity,
    RequiredPlugin,
    RuntimeIdentity,
    Toolchain,
    ToolRecord,
    load_declaration,
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
