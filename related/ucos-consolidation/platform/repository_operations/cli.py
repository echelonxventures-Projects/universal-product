"""EPIC-PLAT-003 — Repository Operations one-command CLI (Terminal T5).

The single command that performs complete repository operational verification using the
existing canonical engines. It is invoked by ``repo-ops.sh`` (which self-heals the
canonical venv first, exactly like ``verify.sh``) and by ``make repo-ops``:

    ./repo-ops.sh                 # run the configured pipeline
    ./repo-ops.sh --resume        # resume, skipping already-passed stages
    ./repo-ops.sh --json          # also emit the machine-readable report on stdout

Exit status is fail-closed: ``0`` iff the run verdict is PASS, ``1`` on FAIL, and ``2``
on a malformed configuration or execution fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.repository_operations.config import load_config
from platform.repository_operations.contracts import ExecutionReport
from platform.repository_operations.errors import RepositoryOperationsError
from platform.repository_operations.service import build_repository_operations_service
from typing import TextIO


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-repo-ops",
        description="Complete repository operational verification via the canonical engines.",
    )
    parser.add_argument("--config", required=True, help="path to the JSON/TOML pipeline config")
    parser.add_argument("--repo-root", default=".", help="repository root (default: cwd)")
    parser.add_argument("--checkpoint", default=None, help="path to a resumable checkpoint file")
    parser.add_argument(
        "--resume", action="store_true", help="skip stages already passed in the checkpoint"
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="emit the report as JSON on stdout"
    )
    return parser


def _print_summary(report: ExecutionReport, stream: TextIO) -> None:
    counts = report.counts()
    print("================ REPOSITORY OPERATIONS SUMMARY ================", file=stream)
    print(f"  repository: {report.repository_id}  epic: {report.epic_id}", file=stream)
    for result in report.stage_results:
        line = f"  {result.outcome.value.upper():8} {result.stage_id:32} {result.summary}"
        print(line, file=stream)
    if report.coverage is not None:
        print(f"  coverage:   line {report.coverage.line_percent}%", file=stream)
    print(
        f"  totals: {counts['passed']} passed, {counts['failed']} failed, "
        f"{counts['skipped']} skipped ({counts['total']} stages)",
        file=stream,
    )
    print(f"  VERDICT: {report.verdict.value.upper()}", file=stream)
    print("===============================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on PASS, 1 on FAIL, 2 on a configuration/execution fault."""
    args = _build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        service = build_repository_operations_service(
            config,
            repo_root=args.repo_root,
            checkpoint_path=args.checkpoint,
        )
        report = service.verify_repository(resume=args.resume)
    except RepositoryOperationsError as exc:
        print(f"repository operations error: {exc}", file=sys.stderr)
        return 2

    _print_summary(report, sys.stderr)
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
