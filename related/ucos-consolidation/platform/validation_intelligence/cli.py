"""UCOS-EPIC-013 — Continuous Validation Intelligence one-command CLI (Terminal T5).

The single command that produces continuous validation intelligence across the seven
dimensions from a declarative configuration:

    ucos-validate-intel --config intel.json                 # run the analysis
    ucos-validate-intel --config intel.json --json          # also emit the report
    ucos-validate-intel --config intel.json --compatibility # also emit the compat report
    ucos-validate-intel --config intel.json --compliance    # also emit the compliance report
    ucos-validate-intel --config intel.json --evidence      # also emit the evidence record

Exit status is fail-closed: ``0`` iff the run verdict is PASS, ``1`` on FAIL, and ``2``
on a malformed configuration or execution fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.validation_intelligence.config import load_config
from platform.validation_intelligence.contracts import ValidationIntelligenceReport
from platform.validation_intelligence.errors import ValidationIntelligenceError
from platform.validation_intelligence.evidence import build_validation_intelligence_evidence
from platform.validation_intelligence.service import build_validation_intelligence_service
from typing import TextIO


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-validate-intel",
        description="Continuous validation intelligence across cross-capability consistency, "
        "repository completeness, contract/runtime/version compatibility, and "
        "architecture/governance compliance.",
    )
    parser.add_argument("--config", required=True, help="path to the JSON/TOML intelligence config")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="emit the report as JSON on stdout"
    )
    parser.add_argument(
        "--compatibility",
        action="store_true",
        help="emit the Compatibility Report as JSON on stdout",
    )
    parser.add_argument(
        "--compliance",
        action="store_true",
        help="emit the Compliance Report as JSON on stdout",
    )
    parser.add_argument(
        "--evidence",
        action="store_true",
        help="emit the evidence record as JSON on stdout",
    )
    return parser


def _print_summary(report: ValidationIntelligenceReport, stream: TextIO) -> None:
    counts = report.counts()
    print("============ CONTINUOUS VALIDATION INTELLIGENCE SUMMARY ============", file=stream)
    print(f"  target: {report.target_id}", file=stream)
    for dimension_report in report.dimension_reports:
        dcounts = dimension_report.counts()
        line = (
            f"  {dimension_report.verdict.value.upper():4} "
            f"{dimension_report.dimension.value:30} "
            f"{dcounts['passed']}/{dcounts['total']} checks passed"
        )
        print(line, file=stream)
        for finding in dimension_report.findings:
            if finding.failed:
                marker = "BLOCK" if finding.is_blocking_failure else "ADVIS"
                print(f"        {marker} {finding.check_id}: {finding.message}", file=stream)
    print(
        f"  totals: {counts['passed']} passed, {counts['failed']} failed "
        f"across {counts['dimensions']} dimensions ({counts['total']} checks)",
        file=stream,
    )
    print(f"  compatible: {report.compatibility_report().compatible}", file=stream)
    print(f"  compliant:  {report.compliance_report().compliant}", file=stream)
    print(f"  VERDICT: {report.verdict.value.upper()}", file=stream)
    print("====================================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on PASS, 1 on FAIL, 2 on a configuration/execution fault."""
    args = _build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        service = build_validation_intelligence_service(config)
        report = service.analyze(config.build_target())
    except ValidationIntelligenceError as exc:
        print(f"validation intelligence error: {exc}", file=sys.stderr)
        return 2

    _print_summary(report, sys.stderr)
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    if args.compatibility:
        print(json.dumps(report.compatibility_report().to_dict(), indent=2, sort_keys=True))
    if args.compliance:
        print(json.dumps(report.compliance_report().to_dict(), indent=2, sort_keys=True))
    if args.evidence:
        print(
            json.dumps(
                build_validation_intelligence_evidence(report).to_dict(), indent=2, sort_keys=True
            )
        )
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
