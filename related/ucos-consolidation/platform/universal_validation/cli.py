"""UCOS-EPIC-005 — Universal Validation one-command CLI (Terminal T5).

The single command that performs universal validation across the seven domains from a
declarative configuration:

    ucos-validate --config validation.json           # run the configured validation
    ucos-validate --config validation.json --json     # also emit the report on stdout
    ucos-validate --config validation.json --evidence # also emit the evidence record

Exit status is fail-closed: ``0`` iff the run verdict is PASS, ``1`` on FAIL, and ``2``
on a malformed configuration or execution fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.universal_validation.config import load_config
from platform.universal_validation.contracts import ValidationReport
from platform.universal_validation.errors import UniversalValidationError
from platform.universal_validation.evidence import build_validation_evidence
from platform.universal_validation.service import build_universal_validation_service
from typing import TextIO


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-validate",
        description="Universal validation across architecture, implementation, dependency, "
        "registry, schema, runtime, and quality domains.",
    )
    parser.add_argument("--config", required=True, help="path to the JSON/TOML validation config")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="emit the report as JSON on stdout"
    )
    parser.add_argument(
        "--evidence",
        action="store_true",
        help="emit the evidence record as JSON on stdout",
    )
    return parser


def _print_summary(report: ValidationReport, stream: TextIO) -> None:
    counts = report.counts()
    print("================ UNIVERSAL VALIDATION SUMMARY ================", file=stream)
    print(f"  target: {report.target_id}", file=stream)
    for domain_report in report.domain_reports:
        dcounts = domain_report.counts()
        line = (
            f"  {domain_report.verdict.value.upper():4} {domain_report.domain.value:16} "
            f"{dcounts['passed']}/{dcounts['total']} rules passed"
        )
        print(line, file=stream)
        for result in domain_report.results:
            if result.failed:
                marker = "BLOCK" if result.is_blocking_failure else "ADVIS"
                print(f"        {marker} {result.rule_id}: {result.message}", file=stream)
    print(
        f"  totals: {counts['passed']} passed, {counts['failed']} failed "
        f"across {counts['domains']} domains ({counts['total']} rules)",
        file=stream,
    )
    print(f"  VERDICT: {report.verdict.value.upper()}", file=stream)
    print("=============================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on PASS, 1 on FAIL, 2 on a configuration/execution fault."""
    args = _build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        service = build_universal_validation_service(config)
        report = service.validate(config.build_target())
    except UniversalValidationError as exc:
        print(f"universal validation error: {exc}", file=sys.stderr)
        return 2

    _print_summary(report, sys.stderr)
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    if args.evidence:
        print(json.dumps(build_validation_evidence(report).to_dict(), indent=2, sort_keys=True))
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
