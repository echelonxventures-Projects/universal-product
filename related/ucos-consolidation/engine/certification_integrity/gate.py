"""UCI-000001 Part 10 — the gate. Fail-closed, read-only, three-valued.

    exit 0  OPEN    every blocking law was measured and holds
    exit 1  CLOSED  a blocking law was measured and REFUSED
    exit 2  FAULT   no verdict could be reached — the declaration is absent or unparseable, the
                    tracked-path boundary could not be established, or a coverage measurement
                    named on the command line could not be read

The third code is load-bearing and is not a convenience. "The executable surface is fully
governed" and "the executable surface could not be enumerated" are different facts, and a gate
that collapsed them would let a broken enumerator certify an empty repository. A FAULT is never
"skip": the caller's fail-safe on 2 is to treat certification integrity as UNPROVEN.

WRITES NOTHING BY DEFAULT. ``--inventory`` prints the inventory to stdout. ``--write-inventory``
exists because the mandate names ``coverage_gap_inventory.json`` as a required artifact, and it
writes ONLY that file, which no law in this package reads back. The asymmetry is the mechanism:
nothing this gate emits can turn one of its own refusals into a pass, so regenerating an artifact
can never be a way to satisfy a law.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from engine.certification_integrity.contract import CLOSED, REFUSED, measure, seal_ratchet
from engine.certification_integrity.inventory import build as build_inventory
from engine.certification_integrity.inventory import write as write_inventory
from engine.certification_integrity.model import IntegrityError

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2


def _render(report: dict[str, Any]) -> str:
    counts = report["counts"]
    totals = report["totals"]
    drift = report["scope_drift"]
    lines = [
        "UNIVERSAL CERTIFICATION INTEGRITY — UCI-000001",
        "-" * 78,
        f"  declaration        : {report['declaration']} v{report['declaration_version']}",
        f"  laws measured      : {counts['laws']}"
        f"   holds {counts['holds']}   refused {counts['refused']}",
        f"  tracked non-test   : {counts['files']} files   {counts['objects']} objects",
        "-" * 78,
        "  THE DENOMINATOR VERSUS THE SURFACE",
        f"    executable statements   : {totals['executable_statements']:,}",
        f"    inside the denominator  : {totals['measured_statements']:,}"
        f"  ({totals['denominator_share_percent']}%)",
        f"    outside it              : {totals['unmeasured_statements']:,}",
        f"    coverage of denominator : {totals['measured_coverage_percent']}%",
        f"    coverage of surface     : {totals['executable_coverage_percent']}%",
        "-" * 78,
        "  SCOPE DRIFT (Rule 3)",
        f"    coverage scope    : {drift['coverage_scope']}",
        f"    executable surface: {drift['executable_surface']}",
        f"    governed surface  : {drift['governed_surface']}",
        f"    executable but not measured: {drift['executable_not_in_coverage_scope']}",
        "-" * 78,
        "  LAWS",
    ]
    for law in report["laws"]:
        mark = "  " if law["status"] != REFUSED else "!!"
        lines.append(
            f"  {mark} {law['law']}  {law['name']:44s} " f"{law['measured']:>6} / {law['ceiling']}"
        )
        if law["status"] == REFUSED:
            lines.append(f"       {law['detail']}")
            for offender in law["offenders"][:6]:
                lines.append(f"         - {offender}")
    lines += [
        "-" * 78,
        f"  inventory digest   : {report['inventory_digest'][:16]}",
        f"  STATUS             : {report['status']}",
    ]
    integrity = report.get("coverage_document")
    if isinstance(integrity, dict) and integrity.get("body_is_incomplete"):
        lines[-2:-2] = [
            "-" * 78,
            "  !! COVERAGE DOCUMENT IS INTERNALLY INCONSISTENT",
            f"     root element declares : {integrity['declared_statements']:,} statements",
            f"     body actually contains: {integrity['statements']:,} in "
            f"{integrity['files']} files",
            f"     absent from the body  : {integrity['missing_from_body']:,} "
            f"({integrity['missing_percent']}%)",
            "     coverage xml drops files whose relative names collide across source roots.",
            "     The percentage is unaffected, so every summary agrees; only a per-file",
            "     consumer sees the loss, and absence renders as nothing rather than as zero.",
        ]
    if report["status"] == CLOSED:
        lines.append("  a blocking law was measured and REFUSED — see the detail above")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="engine.certification_integrity.gate",
        description=__doc__.splitlines()[0] if __doc__ else None,
    )
    parser.add_argument("--gate", action="store_true", help="fail-closed integrity gate")
    parser.add_argument("--json", action="store_true", help="emit the report to stdout as JSON")
    parser.add_argument(
        "--inventory", action="store_true", help="print the executable inventory to stdout"
    )
    parser.add_argument(
        "--write-inventory",
        metavar="PATH",
        help="render coverage_gap_inventory.json to PATH (the only file this gate writes)",
    )
    parser.add_argument(
        "--coverage-xml",
        metavar="PATH",
        help="read coverage from PATH instead of ./coverage.xml",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress the human render")
    parser.add_argument(
        "--seal-ratchet",
        action="store_true",
        help=(
            "advance the Ω-4 best-ever values from this measurement. Moves each bound only "
            "DOWNWARD, so this cannot turn a refusal into a pass"
        ),
    )
    args = parser.parse_args(argv)

    root = "."
    try:
        if args.inventory or args.write_inventory:
            if args.write_inventory:
                inventory = write_inventory(
                    root, args.write_inventory, coverage_xml=args.coverage_xml
                )
                if not args.quiet:
                    print(
                        f"wrote {args.write_inventory} "
                        f"({len(inventory.files)} files, {len(inventory.objects)} objects, "
                        f"digest {inventory.digest()[:16]})",
                        file=sys.stderr,
                    )
            else:
                inventory = build_inventory(root, coverage_xml=args.coverage_xml)
                print(json.dumps(inventory.as_document(), indent=1, sort_keys=True))
            if not args.gate:
                return EXIT_OPEN

        if args.seal_ratchet:
            sealed = seal_ratchet(root, coverage_xml=args.coverage_xml)
            if not args.quiet:
                print(f"sealed {sealed}", file=sys.stderr)

        report = measure(root, coverage_xml=args.coverage_xml)
    except IntegrityError as exc:
        print(f"UCI-000001 FAULT: {exc}", file=sys.stderr)
        return EXIT_FAULT

    if args.json:
        print(json.dumps(report, indent=1, sort_keys=True))
    if not args.quiet:
        print(_render(report), file=sys.stderr)

    if args.gate and report["status"] == CLOSED:
        return EXIT_CLOSED
    return EXIT_OPEN


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
