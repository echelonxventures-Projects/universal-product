"""UEG-000001 Part 06 — the fail-closed environment integrity gate.

Exit codes follow the repository convention, and the three answers are kept distinct:

    0  OPEN    every blocking check holds
    1  CLOSED  a blocking check was computed and refused
    2  FAULT   no verdict could be reached (the declaration or the observation is unusable)

Collapsing 1 and 2 would let an unreadable declaration pass as whichever was more
convenient, which is the failure this repository has spent a lot of effort refusing
elsewhere.

WHAT THIS GATE MAY DO. It observes, computes, and writes exactly two gitignored files: the
fingerprint cache and the execution evidence. It creates no virtual environment, installs
no package, and makes no network call — the separation of powers UEG-000001 declares, of
which this gate is the verification half. ``bootstrap.sh`` is the repair half.

THE FAILURE MESSAGE IS PART OF THE CONTRACT. A gate that refuses without naming what it
expected and what it found sends the reader back to manual troubleshooting, which is the
condition this capability exists to eliminate. Every refusal prints expected, detected, and
the one command that repairs it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from engine.execution_environment import evidence as evidence_module
from engine.execution_environment import fingerprint as fingerprint_module
from engine.execution_environment.contract import assess
from engine.execution_environment.discovery import observe, repo_root
from engine.execution_environment.model import (
    ExecutionEnvironment,
    ExecutionEnvironmentError,
    load_declaration,
)

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2

REPAIR_COMMAND = "./bootstrap.sh"

# How many advisory findings the stderr summary prints before eliding the rest.
_ADVISORY_LINES = 5


def measure(
    repository: str | None = None,
    declaration_path: str | None = None,
    command: str | None = None,
    use_cache: bool = True,
    refresh: bool = False,
) -> ExecutionEnvironment:
    """Observe and assess the environment, reusing the cached scan when it is proven valid.

    Raises:
        ExecutionEnvironmentError: the declaration or the observation is unusable — a FAULT,
            which is deliberately not the same answer as a refused check.
    """
    repository = repository or repo_root()
    declaration = load_declaration(declaration_path, repository)

    venv_directory = str(Path(repository) / declaration.venv_relative_path)
    cache_file = fingerprint_module.cache_path(repository, declaration)

    tool_records = None
    state = fingerprint_module.STATE_DISABLED
    key = ""
    if use_cache:
        key = fingerprint_module.trigger_key(repository, declaration, venv_directory)
        if refresh:
            fingerprint_module.invalidate(cache_file)
            state = fingerprint_module.STATE_MISS
        else:
            payload = fingerprint_module.load(cache_file)
            tool_records = fingerprint_module.reusable_tool_records(payload, key)
            if tool_records is not None:
                state = fingerprint_module.STATE_HIT
            elif payload is None:
                state = fingerprint_module.STATE_MISS
            else:
                state = fingerprint_module.STATE_STALE

    environment = observe(declaration, repository, command=command, tool_records=tool_records)
    environment = assess(environment, declaration)
    environment = ExecutionEnvironment(
        runtime=environment.runtime,
        toolchain=environment.toolchain,
        dependencies=environment.dependencies,
        repository=environment.repository,
        machine=environment.machine,
        venv_directory=environment.venv_directory,
        checks=environment.checks,
        command=environment.command,
        observed_at=environment.observed_at,
        cache_state=state,
    )

    # The cache is refreshed only from a VALID environment. Storing an invalid one would let
    # the next run reuse the tool records of a toolchain already known to be broken.
    if use_cache and environment.valid and state != fingerprint_module.STATE_HIT:
        fingerprint_module.store(cache_file, environment, key)

    return environment


def _render(environment: ExecutionEnvironment) -> str:
    """Return the human-readable summary written to stderr."""
    lines = [
        f"UEG-000001 execution environment — {environment.result}",
        f"  environment id  : {environment.environment_id[:16]}",
        f"  interpreter     : {environment.runtime.interpreter_path}"
        f" ({environment.runtime.version})",
        f"  virtualenv      : {environment.runtime.prefix}",
        f"  repository      : {environment.repository.root} @ {environment.repository.commit[:12]}",
        f"  dependency print: {environment.dependencies.fingerprint[:16]}",
        f"  cache           : {environment.cache_state}",
    ]
    for check in environment.checks:
        mark = "OK  " if check.holds else ("FAIL" if check.blocking else "WARN")
        lines.append(f"  {mark} {check.check_id}  {check.title}")
        # Advisories are truncated in the summary and never in the JSON. EEG-08 legitimately
        # reports dozens of Finder duplicates on a contaminated venv, and forty lines of
        # advisory above a passing gate is how a report becomes something people scroll past.
        # --json carries every finding for anything that needs the whole set.
        shown = check.findings if check.blocking else check.findings[:_ADVISORY_LINES]
        for finding in shown:
            lines.append(f"         - {finding}")
        elided = len(check.findings) - len(shown)
        if elided > 0:
            lines.append(f"         ... +{elided} more (--json for the full set)")
    return "\n".join(lines)


def _render_failure(environment: ExecutionEnvironment) -> str:
    """Return the deterministic block printed when execution is blocked.

    The shape is fixed on purpose — expected, detected, blocked, repair — so that the answer
    to "what do I do now" is in the output rather than in someone's memory.
    """
    lines = ["", "UCOS EXECUTION ENVIRONMENT FAILURE", ""]
    for check in environment.blocking_failures:
        lines.append(f"{check.check_id} — {check.title}")
        if check.expected is not None:
            lines.append("")
            lines.append("Expected:")
            lines.append("")
            lines.append(f"    {check.expected}")
        if check.detected is not None:
            lines.append("")
            lines.append("Detected:")
            lines.append("")
            lines.append(f"    {check.detected}")
        for finding in check.findings:
            lines.append(f"      - {finding}")
        lines.append("")
    lines.append("Execution blocked.")
    lines.append("")
    lines.append(f"Repair with: {REPAIR_COMMAND}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns OPEN, CLOSED or FAULT."""
    parser = argparse.ArgumentParser(
        prog="python -m engine.execution_environment.gate",
        description=(
            "Measure UEG-000001: that this interpreter, this virtual environment and this "
            "toolchain are the ones the repository declares. Observes and refuses; never "
            "creates, installs or reaches the network."
        ),
    )
    parser.add_argument(
        "--gate", action="store_true", help="refuse execution when a blocking check fails"
    )
    parser.add_argument("--repository", default=None, help="repository root to measure")
    parser.add_argument("--declaration", default=None, help="path to ueg-declaration.json")
    parser.add_argument("--command", default=None, help="the command this environment is serving")
    parser.add_argument("--evidence", action="store_true", help="write execution evidence")
    parser.add_argument("--refresh", action="store_true", help="ignore the cache and rescan")
    parser.add_argument("--no-cache", action="store_true", help="neither read nor write the cache")
    parser.add_argument(
        "--json", action="store_true", help="write the full observation to stdout as JSON"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="suppress the summary on stderr when valid"
    )
    args = parser.parse_args(argv)

    try:
        environment = measure(
            repository=args.repository,
            declaration_path=args.declaration,
            command=args.command,
            use_cache=not args.no_cache,
            refresh=args.refresh,
        )
    except ExecutionEnvironmentError as error:
        print(f"UEG gate FAULT: {error}", file=sys.stderr)
        return EXIT_FAULT

    if args.evidence:
        try:
            declaration = load_declaration(args.declaration, environment.repository.root)
            evidence_module.write(
                environment, declaration, environment.repository.root, args.command
            )
        except (ExecutionEnvironmentError, OSError) as error:
            print(f"UEG gate FAULT: evidence could not be written: {error}", file=sys.stderr)
            return EXIT_FAULT

    if args.json:
        payload: dict[str, Any] = environment.as_dict()
        print(json.dumps(payload, indent=2, sort_keys=True))

    if not environment.valid:
        print(_render_failure(environment), file=sys.stderr)
        return EXIT_CLOSED if args.gate else EXIT_OPEN

    if not args.quiet:
        print(_render(environment), file=sys.stderr)
    else:
        # Even a quiet run reports advisories. EEG-08 is non-blocking precisely so it can be
        # reported every time; suppressing it under --quiet would make it non-existent.
        for check in environment.advisories:
            print(
                f"! {check.check_id} {check.title}: {len(check.findings)} condition(s)",
                file=sys.stderr,
            )
    return EXIT_OPEN


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["EXIT_CLOSED", "EXIT_FAULT", "EXIT_OPEN", "REPAIR_COMMAND", "main", "measure"]
