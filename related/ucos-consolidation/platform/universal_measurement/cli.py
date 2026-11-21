"""UCOS-UMPF-001 — Universal Measurement Policy Framework CLI.

The one-command surface over policy-driven measurement (UFC-06):

    ucos-measurement policies      # the declared composition: identity, kind, blocking, precedence
    ucos-measurement contracts     # the published contract surface and its version

Both commands read the *declared* composition — they measure nothing on their own and reach
no repository, which is why this surface is safe to run anywhere. A determination is produced
by the composed Foundation (``ucos-foundation determine``), which is the single place a
population is measured (UFC-16).

Exit status is fail-closed: ``0`` on success, ``2`` on a fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.universal_measurement.bootstrap import (
    POLICY_SERVICE_NAME,
    bootstrap_measurement_policies,
)
from platform.universal_measurement.contracts import (
    POLICY_CONTRACT_VERSION,
    POLICY_CONTRACTS,
    UMPF_ID,
)

from engine.foundation.obs.errors import FoundationError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-measurement",
        description="Universal Measurement Policy Framework (UCOS-UMPF-001).",
    )
    parser.add_argument(
        "command",
        choices=("policies", "contracts"),
        help="the operation to perform",
    )
    parser.add_argument(
        "--document", default=None, help="declared policy composition document to use"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _payload(args: argparse.Namespace) -> dict:
    if args.command == "contracts":
        return {
            "capability_id": UMPF_ID,
            "version": POLICY_CONTRACT_VERSION,
            "service": POLICY_SERVICE_NAME,
            "contracts": [ref.to_dict() for ref in POLICY_CONTRACTS],
        }
    engine = bootstrap_measurement_policies(document=args.document)
    registry = engine.registry
    return {
        "capability_id": UMPF_ID,
        "policy_count": registry.count,
        "fingerprint": engine.fingerprint(),
        "policies": [descriptor.to_dict() for descriptor in registry.descriptors()],
    }


def _print_summary(command: str, payload: dict, stream) -> None:  # noqa: ANN001
    print("======== UCOS-UMPF-001 MEASUREMENT POLICIES ========", file=stream)
    print(f"  command: {command}", file=stream)
    if command == "contracts":
        print(f"  version: {payload.get('version', '')}", file=stream)
        for ref in payload.get("contracts", []):
            print(f"    {ref.get('name', '')} v{ref.get('version', '')}", file=stream)
    else:
        print(f"  declared policies: {payload.get('policy_count', 0)}", file=stream)
        for descriptor in payload.get("policies", []):
            mark = "BLOCKING" if descriptor.get("blocking") else "advisory"
            print(
                f"    {descriptor.get('precedence', 0):>4}  {mark:<8}  "
                f"{descriptor.get('policy_id', '')}",
                file=stream,
            )
    print("====================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 2 on a fault."""
    args = _build_parser().parse_args(argv)
    try:
        payload = _payload(args)
    except (FoundationError, OSError) as exc:
        print(f"measurement error: {exc}", file=sys.stderr)
        return 2

    _print_summary(args.command, payload, sys.stderr)
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
