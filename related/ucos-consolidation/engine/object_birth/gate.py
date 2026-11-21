"""UOBC-000001 Part 05 — the fail-closed birth gate.

Exit codes follow the repository convention so a caller can distinguish the three
outcomes that matter:

    0  OPEN    every law holds
    1  CLOSED  a law was measured and refused
    2  FAULT   no verdict could be reached (the declaration or ledger is unusable)

The distinction between 1 and 2 is deliberate. "The contract is violated" and "the
contract could not be read" are different facts, and collapsing them would let an
unreadable declaration masquerade as a pass or a failure depending on which was more
convenient.

Read-only and hermetic: it loads the declaration and the ledger, computes, and writes
nothing. No clock, no network, no subprocess. That is what makes it safe to wire into
``./verify.sh`` without it being able to dirty the tree or flake.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from engine.object_birth.contract import assess, load_contract, repo_root
from engine.object_birth.ledger import load as load_ledger
from engine.object_birth.ledger import records as ledger_records
from engine.object_birth.model import BirthError
from engine.object_birth.scope import (
    assess_scope,
    load_context,
    load_policy,
    summarize,
)

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2


def measure(declaration: str | None = None, ledger_path: str | None = None) -> dict[str, Any]:
    """Measure every law and return the report.

    Raises:
        BirthError: the declaration or ledger is unusable, which is a FAULT rather
            than a verdict.
    """
    contract = load_contract(declaration)
    target = ledger_path or os.path.join(repo_root(), contract.ledger_home)
    ledger = load_ledger(target)
    records = ledger_records(ledger)
    assessments = assess(contract, ledger, records)

    laws = [
        {"law_id": law_id, "title": title, "violations": list(violations), "holds": not violations}
        for law_id, title, violations in assessments
    ]

    # UOBC-BSP-001 — birth SCOPE, measured in the same gate rather than a new one. Scope
    # is part of the birth contract: which objects must be born is the same subject as
    # whether the ones that are born are correct, and a second stage would be a second
    # place to look for one answer.
    policy = load_policy()
    context = load_context()
    laws.extend(
        {"law_id": law_id, "title": title, "violations": list(violations), "holds": not violations}
        for law_id, title, violations in assess_scope(policy, context)
    )
    scope = summarize(policy, context)

    refused = [entry for entry in laws if not entry["holds"]]

    return {
        "artifact_id": contract.artifact_id,
        "version": contract.version,
        "authority": "NONE — DERIVED TRUTH",
        "ledger": contract.ledger_home,
        "identity_plane": contract.identity_home,
        "identity_shape": contract.identity_shape,
        "stages": len(contract.stages),
        "identity_stage": contract.identity_stage.stage_id,
        "mandatory_fields": len(contract.fields),
        "declared_namespaces": [n.namespace for n in contract.namespaces],
        "births": len(records),
        "supersessions": len(ledger.get("supersessions", [])),
        "laws": laws,
        "laws_measured": len(laws),
        "laws_refused": len(refused),
        "scope": scope,
        "verdict": "OPEN" if not refused else "CLOSED",
    }


def _render(report: dict[str, Any]) -> str:
    """Render the report for a terminal reader."""
    lines = [
        f"{report['artifact_id']} UNIVERSAL OBJECT BIRTH CONTRACT v{report['version']}",
        "-" * 60,
        f"  identity plane        : {report['identity_plane']}",
        f"  identity shape        : {report['identity_shape']}",
        f"  identity comes into being at : {report['identity_stage']}",
        f"  declared stages       : {report['stages']}",
        f"  mandatory fields      : {report['mandatory_fields']}",
        f"  declared namespaces   : {len(report['declared_namespaces'])}",
        f"  births recorded       : {report['births']}",
        f"  supersessions         : {report['supersessions']}",
        f"  laws measured         : {report['laws_measured']}",
        f"  laws refused          : {report['laws_refused']}",
        "-" * 60,
        f"  birth scope policy    : {report['scope']['policy_id']}",
        f"  governed objects      : {report['scope']['objects']}",
        f"  scope verdicts        : "
        f"PASS {report['scope']['verdicts']['PASS']} · "
        f"FAIL {report['scope']['verdicts']['FAIL']} · "
        f"EXCEPTION {report['scope']['verdicts']['EXCEPTION']} (adoption deferred, disclosed)",
        "-" * 60,
    ]
    for entry in report["laws"]:
        mark = "PASS" if entry["holds"] else "FAIL"
        lines.append(f"  [{mark}] {entry['law_id']}  {entry['title']}")
        for violation in entry["violations"]:
            lines.append(f"         - {violation}")
    lines.append("-" * 60)
    if report["verdict"] == "OPEN":
        lines.append(
            "GATE PASSED — no object exists without identity, and no identity was replaced."
        )
    else:
        lines.append(f"GATE CLOSED — {report['laws_refused']} law(s) refused.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Entry point. See module docstring for exit semantics."""
    parser = argparse.ArgumentParser(
        prog="python -m engine.object_birth.gate",
        description="UOBC-000001 birth contract gate (read-only, fail-closed).",
    )
    parser.add_argument("--gate", action="store_true", help="fail closed on any refused law")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument("--quiet", action="store_true", help="suppress the rendered report")
    parser.add_argument("--declaration", default=None, help="declaration path override")
    parser.add_argument("--ledger", default=None, help="ledger path override")
    args = parser.parse_args(argv)

    try:
        report = measure(args.declaration, args.ledger)
    except BirthError as exc:
        print(f"BIRTH CONTRACT FAULT: {exc}", file=sys.stderr)
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
