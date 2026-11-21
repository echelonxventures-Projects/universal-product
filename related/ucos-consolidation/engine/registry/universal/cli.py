"""UCOS-EPIC-001 — Universal Registry Platform CLI (validation + evidence).

A thin, deterministic command-line surface over the platform, used by CI and
operators to *validate* a set of registration requests and emit reproducible
*evidence*. It builds an in-memory platform from a JSON manifest, applies every
registration through the single authority, verifies audit-chain + registry
integrity, and prints a canonical summary.

Manifest shape (``registrations`` is an array of request objects)::

    {
      "actor": "OPERATOR",              // optional; audit actor
      "registrations": [
        {
          "kind": "SERVICE",
          "namespace": "ucos.service",  // optional (kind default otherwise)
          "natural_key": "registry-discovery",
          "name": "Registry & Discovery",
          "version": "1.0.0",
          "attributes": {"domain": "DOM-027"},
          "dependencies": [], "tags": [], "provenance": [],
          "owner": "WP-PLT-06", "description": ""
        }
      ]
    }

Exit codes: ``0`` valid; ``1`` a registration or integrity check failed; ``2``
the manifest is malformed. Stdlib-only; deterministic (uses a sequence clock so
evidence is byte-stable). Never writes to the frozen corpus.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from engine.registry.universal.audit import SequenceClock
from engine.registry.universal.errors import RegistrationError
from engine.registry.universal.identity import canonical_json
from engine.registry.universal.records import RegistrationRequest
from engine.registry.universal.registries import UniversalRegistryPlatform


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(document, dict) or not isinstance(document.get("registrations"), list):
        raise ValueError("manifest must be an object with a 'registrations' array")
    return document


def build_platform(manifest: dict[str, Any]) -> UniversalRegistryPlatform:
    """Build and populate a platform from a manifest (deterministic clock)."""
    actor = str(manifest.get("actor") or "UCOS-REGISTRY-AUTHORITY")
    platform = UniversalRegistryPlatform(actor=actor, clock=SequenceClock())
    for entry in manifest["registrations"]:
        if not isinstance(entry, dict):
            raise ValueError("each registration must be an object")
        request = RegistrationRequest.build(
            kind=entry["kind"],
            namespace=entry.get("namespace") or _default_namespace(entry["kind"]),
            natural_key=entry["natural_key"],
            name=entry["name"],
            version=entry.get("version", "1.0.0"),
            attributes=entry.get("attributes") or {},
            description=entry.get("description", ""),
            owner=entry.get("owner", "UNASSIGNED"),
            dependencies=entry.get("dependencies"),
            tags=entry.get("tags"),
            provenance=entry.get("provenance"),
        )
        platform.core.register(request, actor=actor)
    return platform


def _default_namespace(kind: str) -> str:
    return f"ucos.{str(kind).strip().lower()}"


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(
        prog="ucos-registry",
        description="Validate registrations against the Universal Registry Platform.",
    )
    parser.add_argument("manifest", type=Path, help="path to a registrations manifest (JSON)")
    parser.add_argument(
        "--export",
        type=Path,
        default=None,
        metavar="DIR",
        help="write a deterministic snapshot + audit journal to DIR",
    )
    args = parser.parse_args(argv)

    try:
        manifest = _load_manifest(args.manifest)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2

    try:
        platform = build_platform(manifest)
        platform.validate()
    except RegistrationError as exc:
        print(canonical_json({"ok": False, **exc.to_dict()}), file=sys.stderr)
        return 1
    except (KeyError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": f"malformed registration: {exc}"}), file=sys.stderr)
        return 2

    if args.export is not None:
        platform.export(args.export)

    print(canonical_json({"ok": True, "summary": platform.summary()}))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
