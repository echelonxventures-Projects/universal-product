"""UCOS-UOF-001 — Ownership Framework CLI.

THE one-command surface over canonical ownership determination, for any project:

    ucos-ownership contract                    # the Ownership Declaration Contract
    ucos-ownership providers                   # the registered evidence providers
    ucos-ownership homing                      # the project's canonical-home determination
    ucos-ownership recommend                   # the governance workload, reduced to a minimum
    ucos-ownership determine --subjects FILE   # determine ownership over an ad-hoc population

``homing`` and ``recommend`` execute from the project's **declared specialisation**, so the
population, the registration ledger, the eligibility rules, the ownership grain and the
evidence roles all come from one document and none of them is written in code. This is the
only canonical-home determination in the platform: there is no second implementation to keep
in step with it (UCOS-UFC-001 UFC-14, UFC-16).

``determine`` remains the generic surface for any declared Truth document, so the framework is
still usable against a population that has no specialisation at all.

Exit status is fail-closed: ``0`` on success, ``1`` when ``--gate`` is set and ownership is
not closed, ``2`` on a determination fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from platform.universal_ownership.bootstrap import bootstrap_ownership
from platform.universal_ownership.contracts import default_ownership_contract
from platform.universal_ownership.recommendation import build_governance_reduction
from platform.universal_truth.bootstrap import bootstrap_repository_truth
from platform.universal_truth.projection import ProjectionSpec, SubjectProjection

from engine.foundation.obs.errors import FoundationError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-ownership",
        description="Universal Ownership Framework (UCOS-UOF-001).",
    )
    parser.add_argument(
        "command",
        choices=("contract", "providers", "homing", "recommend", "determine", "authority-key"),
        help="the operation to perform",
    )
    parser.add_argument("--policy", default=None, help="declared truth-policy document")
    parser.add_argument("--declarations", default=None, help="declared ownership assignments")
    parser.add_argument(
        "--specialization", default=None, help="declared Foundation specialisation document"
    )
    parser.add_argument("--root", default=".", help="root against which declarations resolve")
    parser.add_argument("--subjects", default=None, help="declared Truth document to project")
    parser.add_argument("--collection", default="concepts", help="pointer to the population")
    parser.add_argument("--identity-field", default="id", help="the identity field of a record")
    parser.add_argument(
        "--locator-field",
        action="append",
        default=None,
        help="a locator field of a record (repeatable)",
    )
    parser.add_argument(
        "--detail", action="store_true", help="emit the per-record detail, not the summary"
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="emit the non-binding draft assignment document a governing authority would review",
    )
    parser.add_argument("--gate", action="store_true", help="exit 1 when ownership is not closed")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _specialised(args: argparse.Namespace):  # noqa: ANN202 - local composition helper
    """Compose the Foundation from the declared specialisation and project its population."""
    from platform.universal_foundation.bootstrap import bootstrap_universal_foundation

    foundation = bootstrap_universal_foundation(args.specialization, root=args.root)
    subjects = foundation.project_population(root=args.root)
    if not subjects:
        raise FoundationError(
            "the declared specialisation projects no population; nothing can be determined"
        )
    return foundation, subjects


def _payload(args: argparse.Namespace) -> dict:
    if args.command == "contract":
        return default_ownership_contract().to_dict()

    if args.command == "authority-key":
        from platform.universal_ownership.authority_key import coverage

        return coverage(root=Path(args.root))

    if args.command in ("homing", "recommend"):
        foundation, subjects = _specialised(args)
        determination = foundation.determine_ownership(subjects)
        if args.command == "homing":
            payload = determination.to_dict()
            if not args.detail:
                payload.pop("records", None)
            payload["providers"] = foundation.ownership.providers.to_dict()
            payload["subjects"] = len(subjects)
            return payload
        workload = build_governance_reduction(
            foundation.ownership.home or foundation.truth,
            determination=determination,
            subjects=subjects,
            attribute=foundation.specialization.peer_attribute,
        ).reduce(determination, subjects)
        if args.draft:
            return workload.as_declaration_document()
        return workload.to_dict() if args.detail else workload.summary()

    policy = bootstrap_repository_truth(args.policy)
    engine = bootstrap_ownership(policy=policy, declarations=args.declarations)
    if args.command == "providers":
        return engine.providers.to_dict()
    if not args.subjects:
        raise FoundationError("determine requires --subjects <declared truth document>")
    spec = ProjectionSpec.create(
        args.collection,
        args.identity_field,
        locator_fields=tuple(args.locator_field or ("files",)),
    )
    subjects = SubjectProjection(spec).project_file(args.subjects)
    return engine.determine(subjects).to_dict()


def _print_summary(command: str, payload: dict, stream) -> None:  # noqa: ANN001
    print("============ UCOS-UOF-001 CANONICAL OWNERSHIP ============", file=stream)
    print(f"  command: {command}", file=stream)
    if command == "contract":
        for requirement in payload.get("requirements", []):
            print(f"    {requirement['requirement_id']}  {requirement['statement']}", file=stream)
    elif command == "authority-key":
        planes = " · ".join(payload.get("planes_composed", []))
        print(f"  planes composed:  {planes}", file=stream)
        print(f"  subjects:         {payload.get('subjects', 0)}", file=stream)
        print(f"  fully resolved:   {payload.get('fully_resolved', 0)}", file=stream)
        print(
            f"  stranded:         {payload.get('locator_not_in_ledger', 0)} locator "
            f"+ {payload.get('unresolved_owner', 0)} owner",
            file=stream,
        )
        print(f"  join fraction:    {payload.get('fraction_fully_resolved', 0.0)}", file=stream)
        print(f"  derivation:       {payload.get('derivation', '')}", file=stream)
    elif command == "providers":
        for provider in payload.get("providers", []):
            mark = "CONSTITUTIVE" if provider["constitutive"] else "corroborative"
            print(
                f"    {provider['precedence']:>5}  {mark:13} {provider['provider_id']}",
                file=stream,
            )
    elif command == "recommend":
        counts = payload.get("counts", {})
        if counts:
            print(f"  open subjects:  {counts.get('open', 0)}", file=stream)
            print(f"  ratifiable:     {counts.get('ratifiable', 0)}", file=stream)
            print(f"  remediable:     {counts.get('remediable', 0)}", file=stream)
            print(f"  irreducible:    {counts.get('irreducible', 0)}", file=stream)
            print(
                f"  governance min: {counts.get('governance_minimum', 0)}  "
                "(neither proposable nor remediable)",
                file=stream,
            )
            print(
                f"  reduction:      {payload.get('reduction_percentage', 0.0)}% of the open "
                "population is reduced to a decision over a stated proposal",
                file=stream,
            )
            print(
                f"  determinable:   {payload.get('determinable_percentage', 0.0)}% is "
                "dischargeable by a deterministic act or proposal, without an authority",
                file=stream,
            )
        for reason, count in payload.get("by_deficit", {}).items():
            print(f"    {count:>6}  refused by declared rule {reason}", file=stream)
        for owner, count in list(payload.get("by_proposed_owner", {}).items())[:10]:
            print(f"    {count:>6}  would be owned by {owner}", file=stream)
        if payload.get("governance_minimum"):
            print(
                f"  GOVERNANCE MINIMUM ({len(payload['governance_minimum'])}) — no provider can "
                "propose an owner and no declared rule named a deficit; these require an "
                "authority to decide from first principles",
                file=stream,
            )
    else:
        counts = payload.get("counts", {})
        print(f"  subjects:   {counts.get('total', 0)}", file=stream)
        print(f"  declared:   {counts.get('declared', 0)}", file=stream)
        print(f"  contested:  {counts.get('contested', 0)}", file=stream)
        print(f"  unresolved: {counts.get('unresolved', 0)}", file=stream)
        print(f"  remediable: {counts.get('remediable', 0)}", file=stream)
        print(f"  coverage:   {payload.get('coverage_percentage', 0.0)}%", file=stream)
        for reason, count in sorted(payload.get("by_reason", {}).items()):
            print(f"    {count:>6}  {reason}", file=stream)
        for reason, count in sorted(payload.get("by_refusal", {}).items()):
            print(f"    {count:>6}  DIAGNOSED  {reason}", file=stream)
    print("=========================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 when gated open, 2 on a fault."""
    args = _build_parser().parse_args(argv)
    try:
        payload = _payload(args)
    except (FoundationError, OSError) as exc:
        print(f"ownership error: {exc}", file=sys.stderr)
        return 2

    _print_summary(args.command, payload, sys.stderr)
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.command == "authority-key":
        # S-3: the join across the three disclaiming planes. The gate refuses a
        # join that leaves a subject stranded on one plane.
        if not payload.get("subjects"):
            print("AUTHORITY KEY: no subjects measured", file=sys.stderr)
            return 1
        unresolved = payload.get("locator_not_in_ledger", 0) + payload.get("unresolved_owner", 0)
        if unresolved:
            print(
                f"AUTHORITY KEY: {unresolved} subject(s) unresolved across planes",
                file=sys.stderr,
            )
            return 1
        return 0
    if args.gate and args.command in ("homing", "determine") and not payload.get("closed", False):
        print("CANONICAL OWNERSHIP NOT CLOSED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
