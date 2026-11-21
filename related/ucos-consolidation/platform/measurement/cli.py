"""UCOS-EPIC-004 — Universal Measurement Engine CLI (UCOS-UMA-001).

The one-command measurement surface over the real Registry Truth. It measures the
corpus and prints a deterministic report (and, with ``--json``, the machine-readable
body for TRACK-001 / certification):

    ucos-measure report        # headline enumeration/metrics/coverage/gap report
    ucos-measure enumerate     # the population enumeration
    ucos-measure metrics       # the quantitative metric series
    ucos-measure coverage      # the traceability-chain coverage measurement
    ucos-measure gaps          # the structural + completeness gap report
    ucos-measure evidence      # deterministic measurement evidence
    ucos-measure health        # the measurement health endpoint (--strict to certify)

Exit status is fail-closed: ``0`` on success, ``2`` on a Truth/measurement fault. The
``health`` command additionally returns ``1`` when the health verdict is not HEALTHY.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.measurement.bootstrap import bootstrap_measurement
from platform.measurement.service import MeasurementService
from platform.observability.contracts import HealthStatus

from engine.foundation.obs.errors import FoundationError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-measure",
        description="Universal Measurement Engine (UCOS-UMA-001) over Registry Truth.",
    )
    parser.add_argument(
        "command",
        choices=("report", "enumerate", "metrics", "coverage", "gaps", "evidence", "health"),
        help="the measurement to produce",
    )
    parser.add_argument(
        "--data-dir", default=None, help="registry data dir (default: 00-BOOK/DATA)"
    )
    parser.add_argument(
        "--strict", action="store_true", help="apply the strict (certification) health policy"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _payload(service: MeasurementService, command: str, *, strict: bool) -> dict:
    if command == "report":
        return service.report()
    if command == "enumerate":
        return service.enumerate().to_dict()
    if command == "metrics":
        return service.metrics().to_dict()
    if command == "coverage":
        return service.coverage().to_dict()
    if command == "gaps":
        return service.gaps().to_dict()
    if command == "evidence":
        return service.evidence(strict=strict).to_dict()
    return service.health_report(strict=strict)  # command == "health"


def _print_summary(command: str, payload: dict, stream) -> None:  # noqa: ANN001
    print("================ UCOS-UMA-001 MEASUREMENT ================", file=stream)
    print(f"  command: {command}", file=stream)
    if command == "report":
        counts = payload.get("counts", {})
        gaps = payload.get("gaps", {})
        trace = payload.get("traceability", {})
        print(f"  artifacts:      {counts.get('artifacts', 0)}", file=stream)
        print(f"  relationships:  {counts.get('relationships', 0)}", file=stream)
        print(f"  volumes:        {counts.get('volumes', 0)}", file=stream)
        print(f"  metric series:  {payload.get('metric_count', 0)}", file=stream)
        print(f"  traceability:   {trace.get('overall_percentage', 0.0)}% mean", file=stream)
        print(
            f"  gaps:           {gaps.get('total', 0)} ({gaps.get('structural', 0)} structural)",
            file=stream,
        )
        print(f"  run:            {payload.get('run_id', '')}", file=stream)
    elif command == "health":
        print(f"  status:  {payload.get('status', 'unknown')}", file=stream)
        for check in payload.get("checks", []):
            print(f"    {check['status']:9} {check['name']}", file=stream)
    else:
        for key in sorted(payload):
            if key.endswith(("_id", "count", "percentage", "total")) or "fingerprint" in key:
                print(f"  {key}: {payload[key]}", file=stream)
    print("=========================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 on unhealthy, 2 on a measurement fault."""
    args = _build_parser().parse_args(argv)
    try:
        service = bootstrap_measurement(args.data_dir)
        payload = _payload(service, args.command, strict=args.strict)
    except FoundationError as exc:
        print(f"measurement error: {exc}", file=sys.stderr)
        return 2

    _print_summary(args.command, payload, sys.stderr)
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.command == "health" and payload.get("status") != HealthStatus.HEALTHY.value:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
