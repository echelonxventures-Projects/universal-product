"""UCOS-UFP-001 — Universal Foundation Platform CLI.

The one-command surface over the composed Foundation, for any project:

    ucos-foundation capabilities                 # the composed capabilities and their contracts
    ucos-foundation composition                  # the declared specialisation and its wiring
    ucos-foundation determine                    # Truth + ownership + measurement determination

``determine`` executes from the project's *declared* population document — it never scans a
repository. ``--specialization FILE`` points at another project's declaration.

Exit status is fail-closed: ``0`` on success, ``1`` when ``--gate`` is set and the determination
is NOT-CLOSED, ``2`` on a fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.universal_foundation.bootstrap import bootstrap_universal_foundation
from platform.universal_foundation.service import UniversalFoundation

from engine.foundation.obs.errors import FoundationError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-foundation",
        description="Universal Foundation Platform (UCOS-UFP-001).",
    )
    parser.add_argument(
        "command",
        choices=("capabilities", "composition", "determine"),
        help="the operation to perform",
    )
    parser.add_argument("--specialization", default=None, help="declared specialisation document")
    parser.add_argument("--root", default=".", help="root against which declarations resolve")
    parser.add_argument(
        "--detail", action="store_true", help="emit the full determination, not the summary"
    )
    parser.add_argument(
        "--gate", action="store_true", help="exit 1 when the determination is NOT-CLOSED"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _payload(foundation: UniversalFoundation, args: argparse.Namespace) -> dict:
    if args.command == "capabilities":
        return {
            "capabilities": list(foundation.capabilities()),
            "truth_zones": foundation.truth.zone_ids(),
            "ownership_requirements": list(foundation.ownership.contract.requirement_ids),
            "source_kinds": list(foundation.assimilation.kinds.ids()),
            "measurement_policies": list(foundation.policies.registry.ids()),
            "fingerprint": foundation.fingerprint(),
        }
    if args.command == "composition":
        return foundation.to_dict()
    subjects = foundation.project_population(root=args.root)
    locators = sorted({locator for subject in subjects for locator in subject.locators})
    determination = foundation.determine(subjects=subjects, locators=locators)
    return determination.to_dict() if args.detail else determination.summary()


def _print_summary(command: str, payload: dict, stream) -> None:  # noqa: ANN001
    print("======== UCOS-UFP-001 UNIVERSAL FOUNDATION ========", file=stream)
    print(f"  command: {command}", file=stream)
    if command == "capabilities":
        for capability in payload.get("capabilities", []):
            print(f"    {capability}", file=stream)
        print(f"  truth zones:  {len(payload.get('truth_zones', []))}", file=stream)
        print(f"  source kinds: {len(payload.get('source_kinds', []))}", file=stream)
        print(f"  policies:     {len(payload.get('measurement_policies', []))}", file=stream)
    elif command == "composition":
        specialization = payload.get("specialization", {})
        print(f"  project: {specialization.get('project_id', '')}", file=stream)
        print(f"  truth policy: {specialization.get('truth_policy', '')}", file=stream)
        print(f"  population:   {specialization.get('population_document', '')}", file=stream)
    else:
        print(f"  determination: {payload.get('determination', '')}", file=stream)
        ownership = payload.get("ownership") or {}
        counts = ownership.get("counts", {}) if isinstance(ownership, dict) else {}
        if counts:
            print(
                f"  ownership:     {counts.get('declared', 0)}/{counts.get('total', 0)} declared, "
                f"{counts.get('unresolved', 0)} unresolved, {counts.get('contested', 0)} contested",
                file=stream,
            )
        for blocker in payload.get("blockers", []):
            print(f"    BLOCKER  {blocker}", file=stream)
    print("===================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 when gated open, 2 on a fault."""
    args = _build_parser().parse_args(argv)
    try:
        foundation = bootstrap_universal_foundation(args.specialization, root=args.root)
        payload = _payload(foundation, args)
    except (FoundationError, OSError) as exc:
        print(f"foundation error: {exc}", file=sys.stderr)
        return 2

    _print_summary(args.command, payload, sys.stderr)
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.gate and args.command == "determine" and payload.get("determination") != "CLOSED":
        print("FOUNDATION DETERMINATION NOT CLOSED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
