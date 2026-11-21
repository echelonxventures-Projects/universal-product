"""UKDA Part 13 — Knowledge Layer CLI (EPIC-UKDA).

The single command-line surface over the Universal Knowledge & Decision
Architecture. It is the operational entry point for repository integration
(``make verify`` governance, CI, pre-commit, developer/agent onboarding):

    python -m engine.knowledge.cli init       # author the seed canonical store
    python -m engine.knowledge.cli validate    # Part 10 gate (exit 1 on invalid)
    python -m engine.knowledge.cli certify      # Part 11 gate (exit 1 on not-certified)
    python -m engine.knowledge.cli search TERMS  # Part 09 institutional-memory search
    python -m engine.knowledge.cli impact CKO    # Part 09 reverse-dependency impact
    python -m engine.knowledge.cli docs          # Part 07/08 generate handbooks
    python -m engine.knowledge.cli portal         # EPIC-DOC-002 generate the knowledge portal
    python -m engine.knowledge.cli bootstrap      # Part 06/14 agent/developer digest
    python -m engine.knowledge.cli stats           # Part 09 coverage/consistency
    python -m engine.knowledge.cli capabilities     # Part 04/09 Repository Self-Awareness

Canonical-home resolution is deliberately NOT here. Ownership determination has exactly one
implementation — the Universal Ownership Framework (``platform.universal_ownership``), invoked
as ``ucos-ownership`` / ``make homing`` — and this CLI holding a second one would be a parallel
constitutional authority (UCOS-UFC-001 UFC-15).

Every command loads the canonical store when present, else falls back to the seed
base, so the tool is useful on a fresh clone. Output is deterministic JSON/Markdown.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from engine.knowledge.bootstrap import build_digest
from engine.knowledge.capability import (
    DEFAULT_CATALOG_PATH,
    assimilate_capabilities,
    load_catalog,
)
from engine.knowledge.capability import coverage as capability_coverage
from engine.knowledge.certification import certify_base
from engine.knowledge.docs import DocumentationEngine
from engine.knowledge.errors import KnowledgeError
from engine.knowledge.intelligence import KnowledgeIntelligence
from engine.knowledge.portal import KnowledgePortal
from engine.knowledge.seed import build_seed_base
from engine.knowledge.store import KnowledgeBase, KnowledgeStore
from engine.knowledge.validation import validate_base


def _emit(payload: Any) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))


def _load_base(store_dir: str | None) -> KnowledgeBase:
    """Load the canonical store if present, else the authored-once seed base."""
    store = KnowledgeStore(store_dir)
    if store.exists():
        return store.load()
    return build_seed_base()


def _cmd_init(args: argparse.Namespace) -> int:
    store = KnowledgeStore(args.store)
    if store.exists() and not args.force:
        print(f"canonical store already exists at {store.directory} (use --force)")
        return 1
    canon, decisions = store.save(build_seed_base())
    print(f"wrote {canon}")
    print(f"wrote {decisions}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    report = validate_base(_load_base(args.store))
    _emit(report.to_dict())
    return 0 if report.accepted else 1


def _cmd_certify(args: argparse.Namespace) -> int:
    report = certify_base(_load_base(args.store))
    _emit(report.to_dict())
    return 0 if report.certified else 1


def _cmd_search(args: argparse.Namespace) -> int:
    intel = KnowledgeIntelligence(_load_base(args.store))
    hits = intel.search(" ".join(args.terms), limit=args.limit)
    _emit([h.to_dict() for h in hits])
    return 0


def _cmd_impact(args: argparse.Namespace) -> int:
    intel = KnowledgeIntelligence(_load_base(args.store))
    _emit(
        {
            "cko_id": args.cko_id,
            "direct_dependents": list(intel.dependents_of(args.cko_id)),
            "transitive_impact": list(intel.impact_analysis(args.cko_id)),
        }
    )
    return 0


def _cmd_docs(args: argparse.Namespace) -> int:
    base = _load_base(args.store)
    out_dir = Path(args.out) if args.out else (KnowledgeStore(args.store).directory / "handbooks")
    written = DocumentationEngine(base).write_all(out_dir)
    for path in written:
        print(f"wrote {path}")
    return 0


def _cmd_portal(args: argparse.Namespace) -> int:
    base = _load_base(args.store)
    out_dir = Path(args.out) if args.out else (KnowledgeStore(args.store).directory / "portal")
    written = KnowledgePortal(base).write_all(out_dir)
    for path in written:
        print(f"wrote {path}")
    return 0


def _cmd_bootstrap(args: argparse.Namespace) -> int:
    digest = build_digest(_load_base(args.store))
    if args.format == "md":
        print(digest.to_markdown(), end="")
    else:
        _emit(digest.to_dict())
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    intel = KnowledgeIntelligence(_load_base(args.store))
    _emit(intel.coverage().to_dict())
    return 0


def _cmd_capabilities(args: argparse.Namespace) -> int:
    """Project discovered capabilities into canonical knowledge (Repository Self-Awareness).

    Read-only by default: it reports what *would* change, so the projection can be run in
    a gate to detect that the canonical layer has fallen behind the repository. ``--write``
    persists. Exit 1 when ``--gate`` is set and the layer is stale, so a capability added
    without its canonical knowledge fails closed.
    """
    records = load_catalog(args.catalog)
    store = KnowledgeStore(args.store)
    base = _load_base(args.store)
    result = assimilate_capabilities(base, records)
    payload: dict[str, Any] = {
        "catalog": args.catalog,
        "discovered": len(records),
        "assimilation": result.to_dict(),
        "coverage_before": capability_coverage(records, base),
        "coverage_after": capability_coverage(records, result.base),
    }
    if args.write:
        canon, decisions = store.save(result.base)
        payload["wrote"] = [str(canon), str(decisions)]
    _emit(payload)
    if args.gate and result.changed:
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-knowledge",
        description="UCOS Ω∞ Universal Knowledge & Decision Architecture (UKDA) CLI.",
    )
    parser.add_argument(
        "--store",
        default=None,
        help="canonical knowledge store directory (default: <repo>/knowledge)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="author the seed canonical store")
    p_init.add_argument("--force", action="store_true", help="overwrite an existing store")
    p_init.set_defaults(func=_cmd_init)

    sub.add_parser("validate", help="validate the canonical base (Part 10)").set_defaults(
        func=_cmd_validate
    )
    sub.add_parser("certify", help="certify the canonical base (Part 11)").set_defaults(
        func=_cmd_certify
    )

    p_search = sub.add_parser("search", help="search canonical knowledge (Part 09)")
    p_search.add_argument("terms", nargs="+", help="search terms")
    p_search.add_argument("--limit", type=int, default=20)
    p_search.set_defaults(func=_cmd_search)

    p_impact = sub.add_parser("impact", help="reverse-dependency impact (Part 09)")
    p_impact.add_argument("cko_id", help="canonical object id")
    p_impact.set_defaults(func=_cmd_impact)

    p_docs = sub.add_parser("docs", help="generate handbooks (Part 07/08)")
    p_docs.add_argument("--out", default=None, help="output directory")
    p_docs.set_defaults(func=_cmd_docs)

    p_portal = sub.add_parser("portal", help="generate the knowledge portal (EPIC-DOC-002)")
    p_portal.add_argument("--out", default=None, help="output directory")
    p_portal.set_defaults(func=_cmd_portal)

    p_boot = sub.add_parser("bootstrap", help="agent/developer digest (Part 06/14)")
    p_boot.add_argument("--format", choices=("json", "md"), default="json")
    p_boot.set_defaults(func=_cmd_bootstrap)

    sub.add_parser("stats", help="coverage/consistency snapshot (Part 09)").set_defaults(
        func=_cmd_stats
    )

    p_caps = sub.add_parser(
        "capabilities",
        help="project discovered capabilities into canonical knowledge (self-awareness)",
    )
    p_caps.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG_PATH,
        help=f"capability catalogue to project (default: {DEFAULT_CATALOG_PATH})",
    )
    p_caps.add_argument("--write", action="store_true", help="persist the projection")
    p_caps.add_argument(
        "--gate", action="store_true", help="exit 1 when the canonical layer is stale"
    )
    p_caps.set_defaults(func=_cmd_capabilities)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m engine.knowledge.cli <command>``."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KnowledgeError as exc:
        print(json.dumps(exc.to_dict(), sort_keys=True, ensure_ascii=False))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["build_parser", "main"]
