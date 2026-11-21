"""UCOS-UFC-001 — Universal Foundation Constitution CLI.

The one-command surface over the Foundation's own law (UFC-06):

    ucos-constitution articles      # the law: seventeen articles over thirteen governed domains
    ucos-constitution capabilities  # the declared population the law governs
    ucos-constitution conform       # execute every article against every capability
    ucos-constitution convergence   # prove each constitutional model has exactly one answer
    ucos-constitution nucleus        # prove every registered Ω Nucleus is constitutionally complete
    ucos-constitution maturity       # the measured maturity of the platform, axis by axis
    ucos-constitution freeze         # the freeze readiness determination

``conform`` and ``freeze`` are the gates. ``freeze --with-suites`` additionally executes the
declared verification commands; without it those criteria are reported UNMEASURED and readiness
is withheld rather than assumed.

``conform`` measures twice, and deliberately so. UFC-17 is a platform-scoped article whose
evidence is the per-capability gate results, so completeness cannot be known until conformance
has been measured — and conformance is not final until completeness has contributed its gate.
The second pass carries the first pass's verdict; because every probe is pure and reads only
its declared context, the two passes are identical inputs and the composition is a fixed point
rather than a feedback loop.

Nothing here performs a freeze. Freezing is a constituent act, not a side effect of measuring
eligibility for one.

Exit status is fail-closed: ``0`` on success, ``1`` when ``--gate`` is set and the measured
determination withholds it, ``2`` on a fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.universal_foundation.bootstrap import bootstrap_foundation_constitution
from platform.universal_foundation.constitution import MATURITY_GATES, foundation_constitution
from platform.universal_foundation.convergence import bootstrap_convergence
from platform.universal_foundation.freeze import bootstrap_freeze_readiness
from platform.universal_foundation.nucleus import bootstrap_nucleus_completeness

from engine.foundation.obs.errors import FoundationError

#: Commands whose measured verdict a ``--gate`` run is allowed to fail on.
GATED_COMMANDS: tuple[str, ...] = ("conform", "convergence", "nucleus", "freeze")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-constitution",
        description="Universal Foundation Constitution (UCOS-UFC-001).",
    )
    parser.add_argument(
        "command",
        choices=(
            "articles",
            "capabilities",
            "conform",
            "convergence",
            "nucleus",
            "maturity",
            "freeze",
        ),
        help="the operation to perform",
    )
    parser.add_argument("--register", default=None, help="declared capability register document")
    parser.add_argument(
        "--convergence-register", default=None, help="declared convergence register document"
    )
    parser.add_argument("--freeze-register", default=None, help="declared freeze criteria document")
    parser.add_argument(
        "--nucleus-contract", default=None, help="declared Ω Nucleus facet contract document"
    )
    parser.add_argument(
        "--root", default=".", help="project root against which declarations resolve"
    )
    parser.add_argument(
        "--with-suites",
        action="store_true",
        help="execute declared verification commands (freeze only); otherwise UNMEASURED",
    )
    parser.add_argument(
        "--detail", action="store_true", help="emit the full determination, not the summary"
    )
    parser.add_argument(
        "--gate", action="store_true", help="exit 1 when the measured determination withholds it"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _conformance(args: argparse.Namespace):  # noqa: ANN202 - local composition helper
    """Measure conformance, including every platform-scoped article.

    Two passes, because UFC-17 reads the per-capability gate results it then contributes a
    platform gate about. The first pass establishes those results; the second carries the
    completeness verdict alongside the convergence verdicts. Both passes measure identical
    inputs — every probe is pure and reads only its declared context — so this converges at the
    second pass by construction rather than by hoping it settles.
    """
    engine = bootstrap_foundation_constitution(args.register, project_root=args.root)
    convergence = bootstrap_convergence(args.convergence_register, project_root=args.root).measure()
    first = engine.measure(platform_results=convergence.gate_results)
    nucleus = bootstrap_nucleus_completeness(
        args.nucleus_contract, register=engine.register
    ).measure(conformance=first)
    platform_results = (*convergence.gate_results, *nucleus.gate_results)
    return engine, convergence, nucleus, engine.measure(platform_results=platform_results)


def _payload(args: argparse.Namespace) -> tuple[dict, bool]:
    """The command payload and whether a gated run should pass."""
    if args.command == "articles":
        return foundation_constitution().to_dict(), True

    if args.command == "capabilities":
        engine = bootstrap_foundation_constitution(args.register, project_root=args.root)
        payload = engine.register.to_dict()
        payload["unbound_gates"] = list(engine.unbound_gates())
        payload["probes"] = engine.probes.to_dict()
        return payload, not engine.unbound_gates()

    if args.command == "convergence":
        determination = bootstrap_convergence(
            args.convergence_register, project_root=args.root
        ).measure()
        return (
            determination.to_dict() if args.detail else determination.summary()
        ), determination.converged

    _, convergence, nucleus, conformance = _conformance(args)

    if args.command == "nucleus":
        return (nucleus.to_dict() if args.detail else nucleus.summary()), nucleus.complete

    if args.command == "conform":
        return (
            conformance.to_dict() if args.detail else conformance.summary()
        ), conformance.conformant

    if args.command == "maturity":
        return {
            "determination_id": conformance.determination_id,
            "maturity_percentage": conformance.maturity_percentage,
            "maturity_by_axis": conformance.maturity_by_axis(),
            "maturity_gates": {
                axis.value: list(gates) for axis, gates in sorted(MATURITY_GATES.items())
            },
            "capabilities": [
                {
                    "capability_id": item.capability_id,
                    "maturity_percentage": item.maturity_percentage,
                    "maturity": item.maturity(),
                }
                for item in conformance.capabilities
            ],
        }, conformance.conformant

    determination = bootstrap_freeze_readiness(
        args.freeze_register, project_root=args.root, run_commands=args.with_suites
    ).measure(conformance=conformance, convergence=convergence)
    return (
        determination.to_dict() if args.detail else determination.summary()
    ), determination.ready


def _print_summary(command: str, payload: dict, stream) -> None:  # noqa: ANN001
    print("======== UCOS-UFC-001 UNIVERSAL FOUNDATION CONSTITUTION ========", file=stream)
    print(f"  command: {command}", file=stream)
    if command == "articles":
        for article in payload.get("articles", []):
            print(
                f"    {article['article_id']}  {article['domain']:<15} {article['title']}",
                file=stream,
            )
        print(f"  domains: {len(payload.get('domains', []))}", file=stream)
    elif command == "capabilities":
        for capability in payload.get("capabilities", []):
            print(
                f"    {capability['capability_id']:<16} {capability['domain']:<15} "
                f"{capability['name']}",
                file=stream,
            )
        order = " -> ".join(payload.get("dependency_order", []))
        print(f"  composition order: {order}", file=stream)
        for gate in payload.get("unbound_gates", []):
            print(f"    UNBOUND GATE  {gate}", file=stream)
    elif command == "convergence":
        counts = payload.get("counts", {})
        print(f"  models:                {counts.get('models', 0)}", file=stream)
        print(f"  converged:             {counts.get('converged', 0)}", file=stream)
        print(f"  duplicate impls:       {counts.get('duplicate_implementations', 0)}", file=stream)
        print(f"  competing surfaces:    {counts.get('competing_surfaces', 0)}", file=stream)
        print(f"  duplicate artifacts:   {counts.get('surplus_artifacts', 0)}", file=stream)
        for group in payload.get("duplicate_groups", []):
            print(
                f"    DUPLICATE      {group['model_id']:<22} {group['governed_root']}",
                file=stream,
            )
            for locator in group["locators"]:
                print(f"                     {locator}", file=stream)
            print(f"                     -> {group['remediation']}", file=stream)
        for model in payload.get("models", []):
            mark = "CONVERGED" if model.get("converged") else "NOT-CONVERGED"
            print(
                f"    {mark:<14} {model['model_id']:<22} {model['canonical_package']}",
                file=stream,
            )
        for gate in payload.get("gate_results", []):
            print(f"    {gate['verdict']:<6} {gate['gate']}", file=stream)
    elif command == "nucleus":
        counts = payload.get("counts", {})
        print(f"  contract:              {payload.get('contract_id', '')}", file=stream)
        print(f"  nuclei:                {counts.get('nuclei', 0)}", file=stream)
        print(f"  complete:              {counts.get('complete', 0)}", file=stream)
        print(f"  declared facets:       {counts.get('facets', 0)}", file=stream)
        print(f"  missing facets:        {counts.get('missing', 0)}", file=stream)
        for nucleus in payload.get("nuclei", []):
            mark = "COMPLETE" if nucleus.get("complete") else "INCOMPLETE"
            resolved = nucleus.get("counts", {})
            print(
                f"    {mark:<11} {nucleus['capability_id']:<16} "
                f"{nucleus.get('completeness_percentage', 0.0):>6.2f}%  "
                f"resolved={resolved.get('RESOLVED', 0)} "
                f"declared-absent={resolved.get('DECLARED-ABSENT', 0)}",
                file=stream,
            )
        for blocker in payload.get("blockers", []):
            print(f"    MISSING  {blocker}", file=stream)
        for gate in payload.get("gate_results", []):
            print(f"    {gate['verdict']:<6} {gate['gate']}", file=stream)
    elif command == "maturity":
        print(f"  Foundation maturity: {payload.get('maturity_percentage', 0.0)}%", file=stream)
        for axis, value in sorted(payload.get("maturity_by_axis", {}).items()):
            print(f"    {value:>7.2f}%  {axis}", file=stream)
    elif command == "conform":
        counts = payload.get("counts", {})
        print(f"  capabilities: {counts.get('capabilities', 0)}", file=stream)
        print(
            f"  results:      {counts.get('passed', 0)} passed, {counts.get('failed', 0)} failed, "
            f"{counts.get('faulted', 0)} faulted",
            file=stream,
        )
        print(f"  maturity:     {payload.get('maturity_percentage', 0.0)}%", file=stream)
        for capability in payload.get("capabilities", []):
            mark = "CONFORMANT" if capability.get("conformant") else "NON-CONFORMANT"
            print(
                f"    {mark:<15} {capability['capability_id']:<16} "
                f"{capability.get('maturity_percentage', 0.0):>6.2f}%",
                file=stream,
            )
        for blocker in payload.get("blockers", []):
            print(f"    BLOCKER  {blocker}", file=stream)
    else:
        counts = payload.get("counts", {})
        print(f"  determination: {payload.get('determination', '')}", file=stream)
        print(
            f"  criteria:      {counts.get('ready', 0)} ready, {counts.get('not_ready', 0)} "
            f"not ready, {counts.get('unmeasured', 0)} unmeasured",
            file=stream,
        )
        print(f"  maturity:      {payload.get('maturity_percentage', 0.0)}%", file=stream)
        for result in payload.get("results", []):
            print(
                f"    {result['verdict']:<11} {result['criterion_id']}  {result['requirement']}",
                file=stream,
            )
        for blocker in payload.get("blockers", []):
            print(f"    BLOCKER  {blocker}", file=stream)
    print("================================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 when gated open, 2 on a fault."""
    args = _build_parser().parse_args(argv)
    try:
        payload, satisfied = _payload(args)
    except (FoundationError, OSError) as exc:
        print(f"constitution error: {exc}", file=sys.stderr)
        return 2

    _print_summary(args.command, payload, sys.stderr)
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.gate and args.command in GATED_COMMANDS and not satisfied:
        print(f"FOUNDATION {args.command.upper()} WITHHELD", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["GATED_COMMANDS", "main"]
