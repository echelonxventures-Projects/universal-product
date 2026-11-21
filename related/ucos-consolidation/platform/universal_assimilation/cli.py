"""UCOS-USAF-001 — Assimilation Framework CLI.

The one-command surface over source assimilation, for any project:

    ucos-assimilate kinds                       # the open source-kind taxonomy
    ucos-assimilate adapters                    # the registered source adapters
    ucos-assimilate run --manifest FILE         # assimilate a declared source manifest

The manifest is a declared JSON document — never a filesystem scan::

    {"sources": [{"kind": "document-docx", "locator": "...", "destination": "..."}],
     "destinations": {"<source locator>": "<canonical destination locator>"}}

Payloads are read from the declared locators relative to ``--root`` (default: the current
directory). A source whose payload cannot be read is reported, never invented.

Exit status is fail-closed: ``0`` on success, ``1`` when ``--gate`` is set and assimilation is
not closed, ``2`` on a fault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from platform.universal_assimilation.bootstrap import bootstrap_assimilation
from platform.universal_assimilation.errors import AssimilationPipelineError
from platform.universal_assimilation.pipeline import AssimilationPipeline, SourceInput
from platform.universal_truth.bootstrap import bootstrap_repository_truth

from engine.foundation.obs.errors import FoundationError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-assimilate",
        description="Universal Source Assimilation Framework (UCOS-USAF-001).",
    )
    parser.add_argument(
        "command", choices=("kinds", "adapters", "run"), help="the operation to perform"
    )
    parser.add_argument("--manifest", default=None, help="declared source manifest document")
    parser.add_argument(
        "--sources-file",
        default=None,
        help="declared newline-separated locator list (used with --kind)",
    )
    parser.add_argument(
        "--kind", default=None, help="the declared source kind for --sources-file entries"
    )
    parser.add_argument("--root", default=".", help="root against which locators are resolved")
    parser.add_argument("--policy", default=None, help="declared truth-policy document")
    parser.add_argument(
        "--gate", action="store_true", help="exit 1 when assimilation is not closed"
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _read_payload(root: Path, locator: str) -> bytes:
    try:
        return (root / locator).read_bytes()
    except OSError as exc:
        raise AssimilationPipelineError(
            "declared source payload could not be read", locator=locator, detail=str(exc)
        ) from exc


def _load_locator_list(path: str, kind: str, root: Path) -> tuple[SourceInput, ...]:
    """Load a declared newline-separated locator list (a hash-pinned source manifest)."""
    if not kind:
        raise AssimilationPipelineError("--sources-file requires --kind")
    text = Path(path).read_text("utf-8")
    return tuple(
        SourceInput.create(kind, locator, _read_payload(root, locator))
        for locator in (line.strip() for line in text.splitlines())
        if locator
    )


def _load_manifest(path: str, root: Path) -> tuple[tuple[SourceInput, ...], dict[str, str]]:
    document = json.loads(Path(path).read_text("utf-8"))
    if not isinstance(document, dict):
        raise AssimilationPipelineError("source manifest must be a mapping")
    declared = document.get("sources", ())
    if not isinstance(declared, list):
        raise AssimilationPipelineError("source manifest requires a 'sources' list")
    inputs: list[SourceInput] = []
    for entry in declared:
        if not isinstance(entry, dict):
            raise AssimilationPipelineError("each declared source must be a mapping")
        locator = str(entry.get("locator", ""))
        kind = str(entry.get("kind", ""))
        if not locator or not kind:
            raise AssimilationPipelineError(
                "declared source requires 'kind' and 'locator'", locator=locator
            )
        inputs.append(
            SourceInput.create(
                kind,
                locator,
                _read_payload(root, locator),
                revision=str(entry.get("revision", "")),
                destination=str(entry.get("destination", "")),
            )
        )
    destinations = document.get("destinations", {})
    if not isinstance(destinations, dict):
        raise AssimilationPipelineError("'destinations' must be a mapping")
    return tuple(inputs), {str(k): str(v) for k, v in destinations.items()}


def _payload(pipeline: AssimilationPipeline, args: argparse.Namespace) -> dict:
    if args.command == "kinds":
        return pipeline.kinds.to_dict()
    if args.command == "adapters":
        return pipeline.adapters.to_dict()
    if args.sources_file:
        sources = _load_locator_list(args.sources_file, args.kind or "", Path(args.root))
        return pipeline.assimilate(sources).to_dict()
    if not args.manifest:
        raise AssimilationPipelineError(
            "run requires --manifest <declared source manifest> or --sources-file with --kind"
        )
    sources, destinations = _load_manifest(args.manifest, Path(args.root))
    return pipeline.assimilate(sources, destinations=destinations).to_dict()


def _print_summary(command: str, payload: dict, stream) -> None:  # noqa: ANN001
    print("========= UCOS-USAF-001 SOURCE ASSIMILATION =========", file=stream)
    print(f"  command: {command}", file=stream)
    if command == "kinds":
        for declaration in payload.get("kinds", []):
            print(f"    {declaration['kind_id']:22} {declaration['description']}", file=stream)
    elif command == "adapters":
        for descriptor in payload.get("adapters", []):
            print(
                f"    {descriptor['precedence']:>5}  {descriptor['adapter_id']:34} "
                f"{','.join(descriptor['kinds'])}",
                file=stream,
            )
    else:
        print(f"  sources:      {payload.get('total', 0)}", file=stream)
        print(f"  units:        {payload.get('unit_total', 0)}", file=stream)
        print(f"  assimilated:  {payload.get('coverage_percentage', 0.0)}%", file=stream)
        for state, count in sorted(payload.get("counts_by_state", {}).items()):
            if count:
                print(f"    {count:>6}  {state}", file=stream)
        for reason, count in sorted(payload.get("by_reason", {}).items()):
            print(f"    {count:>6}  {reason}", file=stream)
    print("=====================================================", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns 0 on success, 1 when gated open, 2 on a fault."""
    args = _build_parser().parse_args(argv)
    try:
        policy = bootstrap_repository_truth(args.policy)
        pipeline = bootstrap_assimilation(policy=policy)
        payload = _payload(pipeline, args)
    except (FoundationError, OSError, json.JSONDecodeError) as exc:
        print(f"assimilation error: {exc}", file=sys.stderr)
        return 2

    _print_summary(args.command, payload, sys.stderr)
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.gate and args.command == "run" and not payload.get("closed", False):
        print("SOURCE ASSIMILATION NOT CLOSED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
