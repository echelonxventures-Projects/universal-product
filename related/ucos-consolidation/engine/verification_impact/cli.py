"""The impact CLI that ``./verify.sh --change`` consumes.

Exit codes are chosen so a shell can branch on them without parsing:

    0  a bounded plan was produced (``--print-tests`` lists what to run)
    2  the scope escalated to the whole suite, or no plan could be reached

Escalation is exit 2 rather than exit 0-with-empty-output for the same reason
``changed_paths`` refuses an empty set: the caller must be unable to mistake "verify
everything" for "verify nothing".
"""

from __future__ import annotations

import argparse
import json
import sys

from engine.verification_impact.changes import changed_paths
from engine.verification_impact.graph import ImpactError, load_graph
from engine.verification_impact.impact import Scope, analyse, plan

EXIT_BOUNDED = 0
EXIT_ESCALATED = 2


def _render(report_dict: dict, plan_dict: dict) -> str:
    lines = [
        "VERIFICATION IMPACT",
        "-" * 60,
        f"  changed files         : {report_dict['counts']['changed']}",
        f"  affected objects      : {report_dict['counts']['affected_objects']}",
        f"  affected tests        : {report_dict['counts']['affected_tests']}",
        f"  affected owners       : {report_dict['counts']['affected_owners']}",
        f"  affected evidence     : {', '.join(report_dict['affected_evidence']) or '-'}",
        f"  affected certification: {', '.join(report_dict['affected_certification']) or '-'}",
        f"  scope                 : {report_dict['scope'].upper()}",
        f"  plan                  : {'WHOLE SUITE' if plan_dict['run_everything'] else 'SELECTED'}",
        f"  reason                : {plan_dict['reason']}",
    ]
    if report_dict["escalations"]:
        lines.append("-" * 60)
        lines.append("  escalations:")
        for reason in report_dict["escalations"][:12]:
            lines.append(f"    - {reason}")
        remaining = len(report_dict["escalations"]) - 12
        if remaining > 0:
            lines.append(f"    ... +{remaining} more")
    lines.append("-" * 60)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine.verification_impact",
        description="Compute the minimal verification a change requires (read-only).",
    )
    parser.add_argument("--base", default=None, help="explicit diff base")
    parser.add_argument("--path", action="append", default=None, help="treat PATH as changed")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument(
        "--print-tests",
        action="store_true",
        help="print one affected test path per line (empty when the scope escalates)",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress the rendered report")
    args = parser.parse_args(argv)

    try:
        graph = load_graph()
        changed = tuple(args.path) if args.path else changed_paths(args.base)
    except ImpactError as exc:
        print(f"IMPACT FAULT: {exc}", file=sys.stderr)
        return EXIT_ESCALATED

    report = analyse(graph, changed)
    verification = plan(report)
    report_dict, plan_dict = report.to_dict(), verification.to_dict()

    if args.json:
        print(json.dumps({"impact": report_dict, "plan": plan_dict}, indent=2, sort_keys=True))
    elif args.print_tests:
        if not verification.run_everything:
            for path in verification.test_paths:
                print(path)
    elif not args.quiet:
        print(_render(report_dict, plan_dict))

    if verification.run_everything or report.scope is Scope.NONE:
        return EXIT_ESCALATED
    return EXIT_BOUNDED


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
