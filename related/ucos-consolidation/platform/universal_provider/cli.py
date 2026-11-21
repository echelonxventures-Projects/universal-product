"""UPA-000013 — Universal Provider Architecture CLI (Terminal-04).

The one-command entry point over the Provider Framework::

    ucos-provider constitution            # print the executable Provider Constitution
    ucos-provider discover                # what providers are declared?
    ucos-provider onboard                  # discover -> register -> validate -> certify -> activate
    ucos-provider validate <id@version>    # gate-by-gate conformance for one provider
    ucos-provider state                    # framework state, content-addressed
    ucos-provider verify-evidence <dir>    # re-hash a materialized evidence bundle

Every command reads a **catalog directory of JSON manifests** and nothing else. The
CLI names no provider, imports no provider, and branches on no provider kind: change
the catalog and the CLI's behaviour changes with it (PC-02 / PC-14).

Exit codes: ``0`` success, ``1`` a constitutional failure was found, ``2`` the command
could not be executed (unreadable catalog, unknown provider, malformed manifest).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from platform.universal_provider.certification import CertificationTier
from platform.universal_provider.constitution import provider_constitution
from platform.universal_provider.errors import ProviderFrameworkError
from platform.universal_provider.evidence import (
    build_evidence,
    verify_evidence,
    write_evidence,
)
from platform.universal_provider.framework import ProviderFramework

#: Default catalog directory, relative to the repository root. It is a *path*, not a
#: provider list: the framework learns which providers exist by reading it.
DEFAULT_CATALOG = Path("platform") / "providers" / "catalog"

EXIT_OK = 0
EXIT_FINDING = 1
EXIT_ERROR = 2


def _repository_root() -> Path:
    """Return the repository root inferred from this module's location."""
    return Path(__file__).resolve().parents[2]


def _resolve_catalog(raw: str | None) -> Path:
    if raw:
        return Path(raw)
    return _repository_root() / DEFAULT_CATALOG


def _emit(payload: object) -> None:
    """Print a deterministic JSON document."""
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def _build_framework(catalog: Path) -> ProviderFramework:
    framework = ProviderFramework()
    framework.add_catalog(catalog)
    return framework


def _cmd_constitution(_: argparse.Namespace) -> int:
    _emit(provider_constitution().to_dict())
    return EXIT_OK


def _cmd_discover(args: argparse.Namespace) -> int:
    framework = _build_framework(_resolve_catalog(args.catalog))
    result = framework.discover()
    _emit(
        {
            "count": len(result),
            "kinds": list(result.kinds()),
            "discovery_hash": result.discovery_hash(),
            "realizable": [item.qualified_id for item in result.resolvable()],
            "declared_only": [item.qualified_id for item in result.declared_only()],
            "conflicts": [dict(conflict) for conflict in result.conflicts],
        }
    )
    return EXIT_FINDING if result.conflicts else EXIT_OK


def _cmd_onboard(args: argparse.Namespace) -> int:
    framework = _build_framework(_resolve_catalog(args.catalog))
    discovery = framework.discover()
    results = framework.onboard_discovered(discovery)
    summary = {
        "providers": len(results),
        "active": sorted(item.qualified_id for item in results if item.active),
        "tiers": {item.qualified_id: item.tier for item in results},
        "phases": framework.lifecycle.phases(),
        "state_hash": framework.state_hash(),
        "lifecycle_intact": framework.lifecycle.verify(),
        "certification_intact": framework.certifier.ledger.verify(),
    }
    if args.evidence:
        bundle = build_evidence(framework, discovery=discovery, onboarding=results)
        written = write_evidence(bundle, args.evidence)
        summary["evidence"] = {
            "directory": str(Path(args.evidence)),
            "bundle_hash": bundle.bundle_hash(),
            "artifacts": [path.name for path in written],
        }
    _emit(summary)
    refused = [
        item.qualified_id
        for item in results
        if item.certificate is not None and item.certificate.tier is CertificationTier.REFUSED
    ]
    return EXIT_FINDING if refused else EXIT_OK


def _cmd_validate(args: argparse.Namespace) -> int:
    framework = _build_framework(_resolve_catalog(args.catalog))
    discovery = framework.discover()
    for descriptor in discovery.descriptors():
        framework.admit(descriptor)
    target = args.provider
    if "@" not in target:
        record = framework.registry.resolve(target)
        target = record.qualified_id
    report = framework.validate(target)
    _emit(
        {
            "qualified_id": report.qualified_id,
            "status": report.status.value,
            "counts": report.counts(),
            "report_hash": report.report_hash(),
            "gates": [
                {
                    "gate_id": result.gate_id,
                    "article_id": result.article_id,
                    "status": result.status.value,
                    "summary": result.summary,
                    "findings": list(result.findings),
                }
                for result in report.results
            ],
        }
    )
    return EXIT_OK if not report.failures() else EXIT_FINDING


def _cmd_state(args: argparse.Namespace) -> int:
    framework = _build_framework(_resolve_catalog(args.catalog))
    framework.onboard_discovered()
    _emit(framework.state())
    return EXIT_OK


def _cmd_verify_evidence(args: argparse.Namespace) -> int:
    intact = verify_evidence(args.directory)
    _emit({"directory": str(Path(args.directory)), "intact": intact})
    return EXIT_OK if intact else EXIT_FINDING


def build_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="ucos-provider",
        description="UCOS Universal Provider Architecture — provider-agnostic framework CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    constitution = subparsers.add_parser(
        "constitution", help="print the executable Provider Constitution"
    )
    constitution.set_defaults(handler=_cmd_constitution)

    for name, handler, help_text in (
        ("discover", _cmd_discover, "discover declared providers from the catalog"),
        ("onboard", _cmd_onboard, "run the full onboarding pipeline over the catalog"),
        ("state", _cmd_state, "print the content-addressed framework state"),
    ):
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("--catalog", default="", help="provider catalog directory")
        if name == "onboard":
            sub.add_argument("--evidence", default="", help="write an evidence bundle here")
        sub.set_defaults(handler=handler)

    validate = subparsers.add_parser(
        "validate", help="run every constitutional gate against one provider"
    )
    validate.add_argument("provider", help="provider id, optionally version-pinned as id@version")
    validate.add_argument("--catalog", default="", help="provider catalog directory")
    validate.set_defaults(handler=_cmd_validate)

    verify = subparsers.add_parser("verify-evidence", help="re-hash a materialized evidence bundle")
    verify.add_argument("directory", help="evidence bundle directory")
    verify.set_defaults(handler=_cmd_verify_evidence)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        return int(args.handler(args))
    except ProviderFrameworkError as exc:
        print(json.dumps(exc.to_dict(), indent=2, sort_keys=True), file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())


__all__ = [
    "DEFAULT_CATALOG",
    "EXIT_ERROR",
    "EXIT_FINDING",
    "EXIT_OK",
    "build_parser",
    "main",
]
