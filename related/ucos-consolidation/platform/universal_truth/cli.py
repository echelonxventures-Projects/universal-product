"""UCOS-URTF-001 — Repository Truth Framework CLI.

The one-command surface over declared Repository Truth, for any project:

    ucos-truth policy                        # the declared policy and its zones
    ucos-truth classify <locator> [...]      # classify locators by declared policy
    ucos-truth partition --locators FILE     # partition a declared locator population

``--policy FILE`` supplies another project's declaration; with no flag the packaged
catalogue specialisation is used. Exit status is fail-closed: ``0`` on success, ``1`` when
``--require-classified`` is set and the population contains unclassified locators, ``2`` on
a policy fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from platform.universal_truth.bootstrap import bootstrap_repository_truth
from platform.universal_truth.policy import TruthPolicy

from engine.foundation.obs.errors import FoundationError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-truth",
        description="Universal Repository Truth Framework (UCOS-URTF-001).",
    )
    parser.add_argument(
        "command", choices=("policy", "classify", "partition"), help="the operation to perform"
    )
    parser.add_argument("locators", nargs="*", help="locators to classify")
    parser.add_argument("--policy", default=None, help="declared truth-policy document")
    parser.add_argument("--locators-file", default=None, help="file of newline-separated locators")
    parser.add_argument(
        "--require-classified",
        action="store_true",
        help="exit 1 when any locator is unclassified",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _population(args: argparse.Namespace) -> tuple[str, ...]:
    locators: list[str] = list(args.locators)
    if args.locators_file:
        text = Path(args.locators_file).read_text("utf-8")
        locators.extend(line.strip() for line in text.splitlines() if line.strip())
    return tuple(locators)


def _payload(policy: TruthPolicy, args: argparse.Namespace) -> dict:
    if args.command == "policy":
        return policy.to_dict()
    population = _population(args)
    if not population:
        return {"total": 0, "counts": {}, "classifications": [], "unclassified": []}
    partition = policy.classify_all(population)
    if args.command == "classify":
        return {
            "total": partition.total,
            "classifications": [item.to_dict() for item in partition.classifications],
        }
    return partition.to_dict()


def _print_summary(command: str, payload: dict, stream) -> None:  # noqa: ANN001
    print("=========== UCOS-URTF-001 REPOSITORY TRUTH ===========", file=stream)
    print(f"  command: {command}", file=stream)
    if command == "policy":
        print(f"  policy:  {payload.get('policy_id', '')}", file=stream)
        print(f"  zones:   {payload.get('zone_count', 0)}", file=stream)
        for zone in payload.get("zones", []):
            home = "HOME" if zone["canonical_home_eligible"] else "    "
            print(f"    {home} {zone['truth_class']:20} {zone['zone_id']}", file=stream)
    else:
        for item in payload.get("classifications", []):
            home = "HOME" if item["canonical_home_eligible"] else "    "
            print(f"    {home} {item['truth_class']:20} {item['locator']}", file=stream)
        print(f"  total:   {payload.get('total', 0)}", file=stream)
    print("======================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 on unclassified residue, 2 on a fault."""
    args = _build_parser().parse_args(argv)
    try:
        policy = bootstrap_repository_truth(args.policy)
        payload = _payload(policy, args)
    except (FoundationError, OSError) as exc:
        print(f"repository truth error: {exc}", file=sys.stderr)
        return 2

    _print_summary(args.command, payload, sys.stderr)
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.require_classified:
        unclassified = payload.get("unclassified") or [
            item["locator"]
            for item in payload.get("classifications", [])
            if not item.get("classified", True)
        ]
        if unclassified:
            print(f"unclassified locators: {len(unclassified)}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
