"""UISD-000001 Part 03 — the fail-closed infinite scope gate.

Exit codes follow the repository convention so a caller can distinguish the three
outcomes that matter:

    0  OPEN    every law holds
    1  CLOSED  a law was measured and refused
    2  FAULT   no verdict could be reached (the declaration is unusable)

The distinction between 1 and 2 is deliberate. "A scope is bounded" and "the declaration
could not be read" are different facts, and collapsing them would let an unreadable
declaration pass as whichever was more convenient.

OBSERVE MODE — READ ONLY. It loads the declaration, reads declared files, imports declared
modules in-process, computes, and writes nothing — including to gitignored paths. No
clock, no network, no subprocess. No ``--render`` and no ``--replay`` are declared, because
a gate that writes nothing has nothing to render and cannot drift; declaring an unread flag
is the ``GP-4`` defect recorded in ``GATE-PURITY-DETERMINATION.md``.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from engine.infinite_scope.contract import assess, load_contract, repo_root
from engine.infinite_scope.model import InfiniteScopeError
from engine.uckp.canonical import content_hash

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2


def measure(declaration: str | None = None, repository: str | None = None) -> dict[str, Any]:
    """Measure every law and return the report.

    Raises:
        InfiniteScopeError: the declaration is unusable, which is a FAULT rather than a
            verdict.
    """
    contract = load_contract(declaration)
    repository = repository or repo_root()
    assessments = assess(contract, repository)

    laws = [
        {"law_id": law_id, "title": title, "violations": list(violations), "holds": not violations}
        for law_id, title, violations in assessments
    ]
    refused = [entry for entry in laws if not entry["holds"]]
    unintentional = [
        disclosure.disclosure_id
        for disclosure in contract.closed_enumerations
        if not disclosure.intentional
    ]

    return {
        "artifact_id": contract.artifact_id,
        # THE REPORT NOW NAMES THE STATE IT IS A REPORT OF. Without this the eleven laws below
        # returned a verdict attributable to nothing: two different declarations reaching two
        # opposite verdicts produced reports that could not be told apart. UEC-L-13 measures by
        # mutation that this digest MOVES whenever the declaration's meaning does.
        "declaration_digest": content_hash(contract.digest_payload()),
        "version": contract.version,
        "authority": "NONE — DERIVED TRUTH",
        "plane": contract.gate.get("plane", "OBSERVE MODE — READ ONLY"),
        "expansion_axes": len(contract.axes),
        "closed_enumerations_disclosed": len(contract.closed_enumerations),
        "closed_enumerations_unintentional": unintentional,
        "preserved_freeze_sites": len(contract.freeze_scan.preserved_sites),
        "baseline_surfaces": len(contract.baseline_surfaces),
        "baseline_surfaces_qualified": sum(
            1 for surface in contract.baseline_surfaces if surface.qualified
        ),
        "declared_pins": len(contract.declared_pins),
        "capability_enumerations": len(contract.capability_enumerations),
        "capability_model_final": contract.capability_final,
        "self_applied": contract.artifact_id
        in list(contract.self_application.get("subject_of_own_laws") or []),
        "laws": laws,
        "laws_measured": len(laws),
        "laws_refused": len(refused),
        "verdict": "OPEN" if not refused else "CLOSED",
    }


def _render(report: dict[str, Any]) -> str:
    """Render the report for a terminal reader."""
    lines = [
        f"{report['artifact_id']} UNIVERSAL INFINITE SCOPE AND DIRECTION v{report['version']}",
        "-" * 74,
        f"  plane                      : {report['plane']}",
        f"  authority                  : {report['authority']}",
        f"  expansion axes             : {report['expansion_axes']}",
        f"  closed enumerations shown  : {report['closed_enumerations_disclosed']}"
        f" ({len(report['closed_enumerations_unintentional'])} unintentional)",
        f"  preserved freeze sites     : {report['preserved_freeze_sites']}",
        f"  baseline surfaces          : {report['baseline_surfaces']}"
        f" ({report['baseline_surfaces_qualified']} carry a qualified coordinate)",
        f"  disclosed toolchain pins   : {report['declared_pins']}",
        f"  capability enumerations    : {report['capability_enumerations']}"
        f" (seed model final: {report['capability_model_final']})",
        f"  principle self-applied     : {report['self_applied']}",
        f"  laws measured / refused    : {report['laws_measured']} / {report['laws_refused']}",
        "-" * 74,
    ]
    for entry in report["laws"]:
        mark = "PASS" if entry["holds"] else "FAIL"
        lines.append(f"  [{mark}] {entry['law_id']}  {entry['title']}")
        for violation in entry["violations"]:
            lines.append(f"         - {violation}")
    lines.append("-" * 74)
    if report["verdict"] == "OPEN":
        lines.append(
            "GATE PASSED — scope, direction, relationship and evolution capacity are "
            "unbounded, and no closure is undisclosed."
        )
    else:
        lines.append(f"GATE CLOSED — {report['laws_refused']} law(s) refused.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Entry point. See module docstring for exit semantics."""
    parser = argparse.ArgumentParser(
        prog="python -m engine.infinite_scope.gate",
        description="UISD-000001 infinite scope and direction gate (read-only, fail-closed).",
    )
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument("--quiet", action="store_true", help="suppress the rendered report")
    parser.add_argument("--declaration", default=None, help="declaration path override")
    parser.add_argument("--repository", default=None, help="repository root override")
    args = parser.parse_args(argv)

    try:
        report = measure(args.declaration, args.repository)
    except InfiniteScopeError as exc:
        print(f"INFINITE SCOPE FAULT: {exc}", file=sys.stderr)
        return EXIT_FAULT

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif not args.quiet:
        print(_render(report))

    if report["verdict"] == "CLOSED":
        if args.quiet and not args.json:
            print(_render(report), file=sys.stderr)
        return EXIT_CLOSED
    return EXIT_OPEN


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
