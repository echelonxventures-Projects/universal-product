"""UCON-000001 — the one-command surface, published as ``ucos-construct``.

Six subcommands, each one thing:

    laws        measure every declared law and report (the same measurement the gate makes)
    audit       the extensibility inventory — every closure, its tier, owner and migration path
    registry    the construct population: kinds, dispositions, reality states, facet violations
    dispose     present one construct from the command line and show the full rule trace
    discover    run recursive discovery over a seeded registry and report what it found
    permits     ask whether a disposition/reality pair permits an act, and why not if it does not

``dispose`` and ``permits`` exist because the two questions this capability most needs to answer
out loud are *why does this construct have this disposition* and *why may it not do that*. Both
are answered from the declaration rather than from prose, so the answer cannot drift from the
behaviour.

Nothing here writes. Evidence is written only by ``python -m engine.construct.gate --evidence``,
which is a separate, explicit act.

Exit codes match the gate: 0 succeeded, 1 a measurement refused, 2 the capability faulted.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from engine.construct import audit, extension, reality, views
from engine.construct.contract import REFUSED, load_contract, measure
from engine.construct.declaration import repo_root
from engine.construct.disposition import trace
from engine.construct.model import ConstructError, Evidence, Presentation
from engine.construct.registry import ConstructRegistry

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_FAULT = 2


def _emit(payload: Any, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))


def _laws(args: argparse.Namespace, root: str) -> int:
    report = measure(args.declaration, repository=root, laws=args.law)
    refused = [row for row in report["laws"] if row["verdict"] == REFUSED]
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for row in report["laws"]:
            mark = "ok" if row["verdict"] != REFUSED else "XX"
            print(f"{mark}  {row['law_id']}  {row['statement']}")
            for violation in row["violations"]:
                print(f"        - {violation}")
        print(
            f"\n{report['counts']['holds']}/{report['counts']['laws']} laws hold "
            f"— verdict {report['status']}"
        )
    return EXIT_FAILED if refused else EXIT_OK


def _audit(args: argparse.Namespace, root: str) -> int:
    declaration, probe = load_contract(args.declaration, repository=root)
    inventory = probe.inventory()
    problems = audit.validate(inventory)
    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True))
    else:
        counts = inventory["counts"]
        print("EXTENSIBILITY AUDIT — closure mechanism inventory")
        print("-" * 78)
        print(f"  total closures        : {counts['total']}")
        print(f"  modules with closures : {counts['modules_with_closures']}")
        print(f"  inside governed scope : {counts['governed_scope']} (all must be disclosed)")
        print("\n  by form:")
        for form, count in counts["by_form"].items():
            baseline = inventory["baseline"].get(form)
            outside = counts["outside_governed_scope"].get(form, 0)
            print(f"    {form:24s} {count:5d}   outside scope {outside:5d} / baseline {baseline}")
            print(f"      limitation: {inventory['limitations'][form]}")
            print(f"      migration : {inventory['migrations'][form]}")
        print("\n  by risk tier:")
        for tier, count in counts["by_tier"].items():
            print(f"    {tier:24s} {count:5d}")
        print("\n  heaviest modules:")
        for row in inventory["top_modules"][:15]:
            print(f"    {row['closures']:4d}  {row['module']}")
        print("-" * 78)
        if problems:
            print("  RATCHET VIOLATIONS:")
            for problem in problems:
                print(f"    - {problem}")
        else:
            print("  ratchet holds: nothing undisclosed in scope, nothing above baseline")
    if args.out:
        from engine.construct import evidence

        path = evidence.write_inventory(declaration, inventory, path=args.out)
        print(f"UCON: wrote {path}", file=sys.stderr)
    return EXIT_FAILED if problems else EXIT_OK


def _registry(args: argparse.Namespace, root: str) -> int:
    declaration, _ = load_contract(args.declaration, repository=root)
    registry = ConstructRegistry(declaration)
    payload = {
        "summary": registry.summary(),
        "verification": registry.verify(),
        "discovery": views.discovery_report(registry),
        "extension_points": [
            {
                "admission": point.admission,
                "kind": point.kind,
                "owner": point.owner,
                "point_id": point.point_id,
                "subject": point.subject,
            }
            for point in declaration.extension_points
        ],
    }
    _emit(payload, as_json=True)
    return EXIT_OK if registry.verify()["status"] == "PASS" else EXIT_FAILED


def _dispose(args: argparse.Namespace, root: str) -> int:
    declaration, _ = load_contract(args.declaration, repository=root)
    registry = ConstructRegistry(declaration)
    presentation = Presentation(
        kind=args.kind,
        natural_key=args.key,
        payload=json.loads(args.payload) if args.payload else {},
        evidence=tuple(
            Evidence(source=item, statement="supplied on the command line")
            for item in (args.evidence or ())
        ),
        dependencies=tuple(args.depends_on or ()),
        reality_status=args.reality or "",
        escalation_requested=args.escalate,
        declared_undecidable=args.undecidable,
    )
    construct = registry.present(presentation)
    payload = {
        "construct": construct.as_dict(),
        "permitted_acts": sorted(reality.permitted_acts(declaration, construct)),
        "refusals": {
            act: reality.refusal(declaration, construct, act)
            for act in declaration.operational_acts
            if not reality.permits(declaration, construct, act)
        },
        "trace": [
            row
            for row in trace(
                declaration,
                presentation,
                context=registry.context(reality_status=construct.reality.status),
            )
        ],
    }
    _emit(payload, as_json=True)
    return EXIT_OK


def _discover(args: argparse.Namespace, root: str) -> int:
    declaration, _ = load_contract(args.declaration, repository=root)
    registry = ConstructRegistry(declaration)
    for point in declaration.extension_points:
        extension.exercise(registry, point.point_id)
    first = views.discover(registry)
    second = views.discover(registry)
    _emit(
        {
            "fixed_point": not second,
            "minted": [construct.as_dict() for construct in first],
            "report": views.discovery_report(registry),
            "second_pass_minted": len(second),
        },
        as_json=True,
    )
    return EXIT_OK if not second else EXIT_FAILED


def _permits(args: argparse.Namespace, root: str) -> int:
    declaration, _ = load_contract(args.declaration, repository=root)
    disposition = declaration.disposition(args.disposition)
    state = declaration.reality(args.reality)
    both = sorted(disposition.permits & state.permits)
    _emit(
        {
            "disposition": disposition.identifier,
            "disposition_permits": sorted(disposition.permits),
            "permitted": both,
            "reality_permits": sorted(state.permits),
            "reality_state": state.identifier,
            "refused": {
                act: "; ".join(
                    part
                    for part in (
                        f"disposition {disposition.identifier} does not permit it"
                        if act not in disposition.permits
                        else "",
                        f"reality state {state.identifier} does not permit it"
                        if act not in state.permits
                        else "",
                    )
                    if part
                )
                for act in declaration.operational_acts
                if act not in both
            },
        },
        as_json=True,
    )
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ucos-construct",
        description=(
            "Universal Construct Foundation — governed representation, disposition and "
            "recursive discovery of any presented construct."
        ),
    )
    parser.add_argument("--repository", default=None, help="repository root")
    parser.add_argument("--declaration", default=None, help="path to ucon-declaration.json")
    sub = parser.add_subparsers(dest="command", required=True)

    node = sub.add_parser("laws", help="measure every declared law")
    node.add_argument("--law", action="append", default=None, help="measure only this law id")
    node.add_argument("--json", action="store_true", help="emit the report as JSON")

    node = sub.add_parser("audit", help="the extensibility closure inventory")
    node.add_argument("--json", action="store_true", help="emit the inventory as JSON")
    node.add_argument("--out", default=None, help="also write the inventory to this path")

    sub.add_parser("registry", help="the construct population and the extension points")

    node = sub.add_parser("dispose", help="present one construct and show its full rule trace")
    node.add_argument("--kind", required=True, help="the construct kind, registered or not")
    node.add_argument("--key", required=True, help="the natural key")
    node.add_argument("--payload", default=None, help="a JSON object of facet fields")
    node.add_argument("--evidence", action="append", default=None, help="an evidence source")
    node.add_argument("--depends-on", action="append", default=None, help="a dependency identity")
    node.add_argument("--reality", default=None, help="the claimed reality state")
    node.add_argument("--escalate", action="store_true", help="request an authority")
    node.add_argument("--undecidable", action="store_true", help="declare no procedure decides it")

    sub.add_parser("discover", help="run recursive discovery and report the fixed point")

    node = sub.add_parser("permits", help="ask what a disposition/reality pair permits")
    node.add_argument("--disposition", required=True)
    node.add_argument("--reality", required=True)

    args = parser.parse_args(argv)
    root = args.repository or repo_root()
    handlers = {
        "audit": _audit,
        "discover": _discover,
        "dispose": _dispose,
        "laws": _laws,
        "permits": _permits,
        "registry": _registry,
    }
    try:
        return handlers[args.command](args, root)
    except ConstructError as exc:
        print(f"UCON FAULT: {exc}", file=sys.stderr)
        return EXIT_FAULT
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"UCON FAULT: {exc}", file=sys.stderr)
        return EXIT_FAULT


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
