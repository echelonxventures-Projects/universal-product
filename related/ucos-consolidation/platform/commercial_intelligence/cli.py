"""UCOS-EPIC-014 — Commercial Intelligence one-command CLI (Terminal T5).

The single command that produces commercial intelligence across the fourteen mandated
domains from a declarative configuration:

    ucos-commercial --config commercial.json                 # run the assessment
    ucos-commercial --config commercial.json --json          # also emit the report
    ucos-commercial --config commercial.json --certificate   # also emit the certificate
    ucos-commercial --config commercial.json --evidence      # also emit the evidence record
    ucos-commercial --config commercial.json --dashboard     # also emit the dashboard

Exit status is fail-closed: ``0`` iff the run verdict is PASS (a certified or provisionally
certified commercial surface), ``1`` on FAIL, and ``2`` on a malformed configuration or
execution fault. The human summary goes to stderr and the machine artefacts to stdout, so
the command composes in a pipeline without the summary contaminating the JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.commercial_intelligence.config import load_config
from platform.commercial_intelligence.errors import CommercialIntelligenceError
from platform.commercial_intelligence.service import (
    CommercialAssessment,
    build_commercial_service,
)
from typing import TextIO


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-commercial",
        description="Commercial intelligence across marketplace, licensing, product, "
        "portfolio, business documentation, commercial packages, pricing, investment, "
        "customer, policy governance, approval, business evidence, commercial validation "
        "and commercial certification.",
    )
    parser.add_argument("--config", required=True, help="path to the JSON/TOML commercial config")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="emit the report as JSON on stdout"
    )
    parser.add_argument(
        "--dashboard", action="store_true", help="emit the commercial dashboard as JSON on stdout"
    )
    parser.add_argument(
        "--certificate",
        action="store_true",
        help="emit the commercial certificate as JSON on stdout",
    )
    parser.add_argument(
        "--evidence",
        action="store_true",
        help="emit the business-evidence record as JSON on stdout",
    )
    return parser


def _print_summary(assessment: CommercialAssessment, stream: TextIO) -> None:
    report = assessment.report
    certificate = assessment.certificate
    counts = report.counts()
    print("================ COMMERCIAL INTELLIGENCE SUMMARY ================", file=stream)
    print(f"  subject: {report.target_id}", file=stream)
    for domain_report in report.domain_reports:
        dcounts = domain_report.counts()
        print(
            f"  {domain_report.verdict.value.upper():4} "
            f"{domain_report.domain.value:28} "
            f"{dcounts['passed']}/{dcounts['total']} checks passed",
            file=stream,
        )
        for finding in domain_report.findings:
            if finding.failed:
                marker = "BLOCK" if finding.is_blocking_failure else "ADVIS"
                print(f"        {marker} {finding.check_id}: {finding.message}", file=stream)
    print(
        f"  totals: {counts['passed']} passed, {counts['failed']} failed "
        f"across {counts['domains']} domain(s) ({counts['total']} checks)",
        file=stream,
    )
    for kind, verdict in sorted(report.kind_verdicts().items()):
        print(f"  family {kind:11} {verdict.upper()}", file=stream)
    print(f"  DETERMINATION: {certificate.determination.value}", file=stream)
    print(f"  certificate:   {certificate.certificate_sha256}", file=stream)
    print(f"  evidence:      {assessment.evidence.evidence_sha256}", file=stream)
    print(f"  VERDICT: {report.verdict.value.upper()}", file=stream)
    print("================================================================", file=stream)


def _dump(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on PASS, 1 on FAIL, 2 on a configuration/execution fault."""
    args = _build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        service = build_commercial_service(config)
        assessment = service.assess(config.build_target())
    except CommercialIntelligenceError as exc:
        print(f"commercial intelligence error: {exc}", file=sys.stderr)
        return 2

    _print_summary(assessment, sys.stderr)
    if args.as_json:
        _dump(assessment.report.to_dict())
    if args.dashboard:
        _dump(assessment.dashboard.to_dict())
    if args.certificate:
        _dump(assessment.certificate.to_dict())
    if args.evidence:
        _dump(assessment.evidence.to_dict())
    return 0 if assessment.passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
