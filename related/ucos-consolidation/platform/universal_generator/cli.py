"""UCOS-UNG-001 — Universal Ω Nucleus Generator CLI.

The one-command surface over generation (UFC-06):

    ucos-generate targets                  # the declared obligations every generation covers
    ucos-generate templates                # the registered authorities that render them
    ucos-generate plan --nucleus <ID>      # the complete artifact set for one nucleus
    ucos-generate readiness                # can the Foundation generate every registered nucleus?

``plan`` prints what *would* exist and where. It writes nothing, and neither does any other
command: a plan is a determination, and materialising it is a constituent act performed by
whatever authority governs the Truth it would enter. ``plan --content`` includes the rendered
bytes on stdout so a caller can materialise them under its own governance.

``readiness`` is the Phase 6 question asked without generating anything: it resolves every
declared destination for every registered nucleus and reports the ones no declaration can
answer. Zero findings means the Foundation can generate its whole population.

Exit status is fail-closed: ``0`` on success, ``1`` when ``--gate`` is set and the measured
determination withholds it, ``2`` on a fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.universal_foundation.conformance import (
    default_capability_register,
    load_capability_register,
)
from platform.universal_generator.bootstrap import bootstrap_nucleus_generator

from engine.foundation.obs.errors import FoundationError

#: Commands whose measured verdict a ``--gate`` run is allowed to fail on.
GATED_COMMANDS: tuple[str, ...] = ("readiness",)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-generate",
        description="Universal Ω Nucleus Generator (UCOS-UNG-001).",
    )
    parser.add_argument(
        "command",
        choices=("targets", "templates", "plan", "readiness"),
        help="the operation to perform",
    )
    parser.add_argument("--targets", default=None, help="declared generation target document")
    parser.add_argument("--register", default=None, help="declared nucleus register document")
    parser.add_argument("--nucleus", default=None, help="the nucleus identity to plan for")
    parser.add_argument(
        "--content", action="store_true", help="include rendered bytes in the JSON payload"
    )
    parser.add_argument(
        "--gate", action="store_true", help="exit 1 when the measured determination withholds it"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _register(args: argparse.Namespace):  # noqa: ANN202 - local composition helper
    """The declared nucleus register — the same register the Constitution governs."""
    if args.register is None:
        return default_capability_register()
    return load_capability_register(args.register)


def _payload(args: argparse.Namespace) -> tuple[dict, bool]:
    """The command payload and whether a gated run should pass."""
    generator = bootstrap_nucleus_generator(args.targets)

    if args.command == "targets":
        return generator.targets.to_dict(), not generator.unbound_targets()

    if args.command == "templates":
        return generator.templates.to_dict(), True

    register = _register(args)

    if args.command == "plan":
        if not args.nucleus:
            raise FoundationError("plan requires --nucleus <ID>")
        plan = generator.generate(register.require(args.nucleus))
        return (plan.to_dict() if args.content else plan.summary()), True

    findings = {
        declaration.capability_id: list(generator.can_generate(declaration))
        for declaration in register.ordered()
    }
    blocked = {key: value for key, value in findings.items() if value}
    return {
        "nuclei": len(findings),
        "generatable": len(findings) - len(blocked),
        "targets": generator.targets.count,
        "templates": generator.templates.count,
        "generator_fingerprint": generator.fingerprint(),
        "blocked": blocked,
    }, not blocked


def _print_summary(command: str, payload: dict, stream) -> None:  # noqa: ANN001
    print("======== UCOS-UNG-001 UNIVERSAL Ω NUCLEUS GENERATOR ========", file=stream)
    print(f"  command: {command}", file=stream)
    if command == "targets":
        print(f"  declared targets: {payload.get('count', 0)}", file=stream)
        for target in payload.get("targets", []):
            print(
                f"    {target['target_id']:<7} {target['kind']:<15} {target['template']:<22} "
                f"{target['destination']}",
                file=stream,
            )
    elif command == "templates":
        print(f"  registered templates: {payload.get('count', 0)}", file=stream)
        for template in payload.get("templates", []):
            print(f"    {template['name']:<22} {template['kind']}", file=stream)
    elif command == "plan":
        print(f"  nucleus:   {payload.get('nucleus_id', '')}", file=stream)
        print(f"  plan:      {payload.get('plan_id', '')}", file=stream)
        print(f"  artifacts: {payload.get('total', 0)}", file=stream)
        for artifact in payload.get("artifacts", []):
            print(
                f"    {artifact['kind']:<15} {artifact['line_count']:>5} lines  "
                f"{artifact['destination']}",
                file=stream,
            )
    else:
        print(f"  nuclei:       {payload.get('nuclei', 0)}", file=stream)
        print(f"  generatable:  {payload.get('generatable', 0)}", file=stream)
        print(f"  targets:      {payload.get('targets', 0)}", file=stream)
        print(f"  templates:    {payload.get('templates', 0)}", file=stream)
        for nucleus, findings in sorted(payload.get("blocked", {}).items()):
            for finding in findings:
                print(f"    BLOCKED  {nucleus}  {finding}", file=stream)
    print("============================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 when gated open, 2 on a fault."""
    args = _build_parser().parse_args(argv)
    try:
        payload, satisfied = _payload(args)
    except (FoundationError, OSError) as exc:
        print(f"generation error: {exc}", file=sys.stderr)
        return 2

    _print_summary(args.command, payload, sys.stderr)
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.gate and args.command in GATED_COMMANDS and not satisfied:
        print(f"GENERATION {args.command.upper()} WITHHELD", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["GATED_COMMANDS", "main"]
