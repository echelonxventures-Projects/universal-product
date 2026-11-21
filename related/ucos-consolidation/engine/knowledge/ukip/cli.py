"""UKIP Part 14 — the Knowledge Intelligence command line (EPIC-UKDA-003).

The operational surface: ``ucos-knowledge-intelligence``. Every subcommand is a thin
projection of a library call — the CLI holds no knowledge logic of its own, so what an
operator sees is exactly what a caller of the library gets.

    constitution   the Knowledge Constitution: capabilities, laws, capability matrix
    providers      the registered providers and what each contributes
    assimilate     run the pipeline and print the ledger
    registry       the canonical registry (records, homes, corroborations)
    record         one record in full, including its provenance chain
    classify       classify arbitrary text without registering it
    relate         resolved relationships, optionally composed
    graph          graph counts, projections, provider contribution
    impact         blast radius of a change to one record
    discover       ranked search across every registered record
    screen         discover-before-create determination for proposed knowledge
    provenance     the provenance ledger and its integrity
    validate       the fail-closed validation suite
    certify        the certification verdict per capability
    evidence       build, write, or verify the sealed evidence bundle
    stats          a one-line summary

Exit codes follow the repository convention: ``0`` pass, ``1`` gate failed
(not-valid / not-certified / verification failed), ``2`` operational error.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from typing import Any

from engine.knowledge.errors import KnowledgeError
from engine.knowledge.model import KnowledgeKind
from engine.knowledge.store import KnowledgeStore
from engine.knowledge.ukip.assimilation import (
    AssimilationReport,
    KnowledgeAssimilator,
)
from engine.knowledge.ukip.certification import certify_assimilation
from engine.knowledge.ukip.classification import KnowledgeClassifier
from engine.knowledge.ukip.constitution import knowledge_constitution
from engine.knowledge.ukip.contracts import (
    KnowledgeUnit,
    ProviderKind,
    SourceRef,
)
from engine.knowledge.ukip.discovery import KnowledgeDiscovery
from engine.knowledge.ukip.evidence import (
    build_evidence_from_assimilation,
    read_evidence,
    verify_evidence,
    write_evidence,
)
from engine.knowledge.ukip.graph import KnowledgeIntelligenceGraph
from engine.knowledge.ukip.providers import (
    DocumentProvider,
    MappingProvider,
    ProviderDescriptor,
    ProviderRegistry,
    default_registry,
)
from engine.knowledge.ukip.validation import validate_assimilation

EXIT_OK = 0
EXIT_GATE = 1
EXIT_ERROR = 2


def _emit(payload: Any) -> None:
    """Print canonical JSON so output is diffable and machine-consumable."""
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))


def _providers(args: argparse.Namespace) -> ProviderRegistry:
    """Assemble the provider set: the canonical store plus any operator additions.

    This is where "unlimited providers" is visible operationally: each ``--documents``
    or ``--units`` flag adds another provider and nothing else in the pipeline changes.
    """
    base = KnowledgeStore(getattr(args, "store", None)).load()
    registry = default_registry(base)
    for index, root in enumerate(getattr(args, "documents", None) or []):
        registry.add(
            DocumentProvider(
                root,
                provider_id=f"documents-{index + 1}",
                title=f"Markdown documents under {root}",
                priority=200 + index,
            )
        )
    for index, payload in enumerate(getattr(args, "units", None) or []):
        registry.add(
            MappingProvider.from_json_file(
                ProviderDescriptor(
                    provider_id=f"units-{index + 1}",
                    kind=ProviderKind.EXTERNAL,
                    title=f"External units from {payload}",
                    priority=300 + index,
                ),
                payload,
            )
        )
    return registry


def _assimilate(args: argparse.Namespace) -> tuple[AssimilationReport, ProviderRegistry]:
    base = KnowledgeStore(getattr(args, "store", None)).load()
    providers = _providers(args)
    assimilator = KnowledgeAssimilator(
        screen=getattr(args, "screen", False), strict=getattr(args, "strict", False)
    )
    return assimilator.assimilate(providers, decisions=base.decisions()), providers


# ---------------------------------------------------------------------------
# subcommands
# ---------------------------------------------------------------------------


def cmd_constitution(args: argparse.Namespace) -> int:
    constitution = knowledge_constitution()
    if args.capability:
        laws = [
            law.to_dict()
            for law in constitution.laws
            if args.capability in [c.value for c in law.capabilities]
        ]
        _emit({"capability": args.capability, "laws": laws})
        return EXIT_OK
    _emit(constitution.to_dict())
    return EXIT_OK if constitution.is_complete else EXIT_GATE


def cmd_providers(args: argparse.Namespace) -> int:
    providers = _providers(args)
    payload = providers.to_dict()
    payload["units"] = {
        descriptor.provider_id: len(providers.require(descriptor.provider_id).units())
        for descriptor in providers.descriptors()
    }
    _emit(payload)
    return EXIT_OK


def cmd_assimilate(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    _emit(report.to_document())
    return EXIT_OK if report.accepted else EXIT_GATE


def cmd_registry(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    document = report.registry.to_document()
    if not args.full:
        document["records"] = [
            {
                "knowledge_id": record.knowledge_id,
                "title": record.title,
                "kind": record.kind.value,
                "authority": record.authority.value,
                "universe": record.universe,
                "providers": list(record.provider_ids),
                "corroborations": record.corroboration_count,
            }
            for record in report.registry.records()
        ]
    _emit(document)
    return EXIT_OK


def cmd_record(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    record = report.registry.resolve(args.reference)
    if record is None:
        _emit({"error": "not found", "reference": args.reference})
        return EXIT_ERROR
    _emit(record.to_dict())
    return EXIT_OK


def cmd_classify(args: argparse.Namespace) -> int:
    unit = KnowledgeUnit(
        key="cli-probe",
        title=args.title or args.statement[:60],
        statement=args.statement,
        rationale=args.rationale or "",
        source=SourceRef(
            provider_id="cli",
            kind=ProviderKind.HUMAN,
            locator="cli:classify",
        ),
    )
    classification = KnowledgeClassifier().classify(unit)
    _emit(
        {
            "knowledge_id": classification.apply(unit).knowledge_id(),
            "classification": classification.to_dict(),
        }
    )
    return EXIT_OK


def cmd_relate(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    relationships = report.relationships
    if args.compose:
        relationships = relationships.compose(max_depth=args.depth)
    _emit(relationships.to_dict())
    return EXIT_OK if not relationships.dangling() else EXIT_GATE


def cmd_graph(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    graph = KnowledgeIntelligenceGraph(report.registry, report.relationships)
    if args.projection:
        _emit(
            {
                "projection": args.projection,
                "relationships": [r.to_dict() for r in graph.projection(args.projection)],
            }
        )
        return EXIT_OK
    document = graph.to_dict()
    if not args.full:
        document.pop("edges", None)
        document.pop("nodes", None)
    _emit(document)
    return EXIT_OK


def cmd_impact(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    record = report.registry.resolve(args.reference)
    if record is None:
        _emit({"error": "not found", "reference": args.reference})
        return EXIT_ERROR
    graph = KnowledgeIntelligenceGraph(report.registry, report.relationships)
    _emit(graph.blast_radius(record.knowledge_id))
    return EXIT_OK


def cmd_discover(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    discovery = KnowledgeDiscovery(report.registry)
    if args.coverage:
        coverage = discovery.coverage()
        _emit(coverage.to_dict())
        return EXIT_OK if coverage.is_fully_discoverable else EXIT_GATE
    hits = discovery.search(args.query or "", limit=args.limit)
    _emit({"query": args.query, "count": len(hits), "hits": [h.to_dict() for h in hits]})
    return EXIT_OK


def cmd_screen(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    discovery = KnowledgeDiscovery(report.registry)
    answer = discovery.discover_before_create(
        args.statement,
        title=args.title or "",
        rationale=args.rationale or "",
        kind=KnowledgeKind.coerce(args.kind) if args.kind else None,
    )
    _emit(answer.to_dict())
    return EXIT_GATE if answer.must_reuse else EXIT_OK


def cmd_provenance(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    if args.reference:
        record = report.registry.resolve(args.reference)
        if record is None:
            _emit({"error": "not found", "reference": args.reference})
            return EXIT_ERROR
        _emit(record.provenance.to_dict())
        return EXIT_OK if record.provenance.verify() else EXIT_GATE
    document = report.provenance.to_dict()
    if not args.full:
        document.pop("chains", None)
    _emit(document)
    intact = not (
        report.provenance.broken()
        or report.provenance.incomplete()
        or report.provenance.ungrounded()
    )
    return EXIT_OK if intact else EXIT_GATE


def cmd_validate(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    result = validate_assimilation(report)
    _emit(result.to_dict())
    return EXIT_OK if result.accepted else EXIT_GATE


def cmd_certify(args: argparse.Namespace) -> int:
    report, _ = _assimilate(args)
    certificate = certify_assimilation(report)
    _emit(certificate.to_dict())
    return EXIT_OK if certificate.certified else EXIT_GATE


def cmd_evidence(args: argparse.Namespace) -> int:
    if args.verify:
        document = read_evidence(args.verify)
        ok, defects = verify_evidence(document)
        _emit({"path": str(args.verify), "verified": ok, "defects": list(defects)})
        return EXIT_OK if ok else EXIT_GATE
    report, providers = _assimilate(args)
    evidence = build_evidence_from_assimilation(report, providers=providers)
    if args.out:
        path = write_evidence(evidence, args.out)
        _emit(
            {
                "path": str(path),
                "seal": evidence.seal,
                "accepted": evidence.accepted,
                "component_seals": dict(sorted(evidence.component_seals.items())),
            }
        )
    else:
        _emit(evidence.to_dict())
    return EXIT_OK if evidence.accepted else EXIT_GATE


def cmd_stats(args: argparse.Namespace) -> int:
    report, providers = _assimilate(args)
    validation = validate_assimilation(report)
    certificate = certify_assimilation(report)
    _emit(
        {
            "providers": len(providers),
            "contributions": len(report.ledger),
            "records": len(report.registry),
            "corroborated": len(report.corroborated()),
            "duplicates_created": report.duplicates_created,
            "relationships": len(report.relationships),
            "verdict": validation.verdict.value,
            "certification": certificate.status.value,
            "capabilities_certified": len(certificate.certified_capabilities()),
            "seal": report.seal(),
        }
    )
    if not validation.accepted or not certificate.certified:
        return EXIT_GATE
    return EXIT_OK


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------


def _add_source_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--store", help="canonical knowledge store directory")
    parser.add_argument(
        "--documents",
        action="append",
        metavar="DIR",
        help="add a Markdown document provider rooted at DIR (repeatable)",
    )
    parser.add_argument(
        "--units",
        action="append",
        metavar="FILE",
        help="add an external unit provider from a JSON file (repeatable)",
    )
    parser.add_argument(
        "--screen",
        action="store_true",
        help="apply discover-before-create screening to non-authoritative providers",
    )
    parser.add_argument("--strict", action="store_true", help="fail closed on any provider error")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-knowledge-intelligence",
        description=(
            "UCOS Ω∞ Universal Knowledge Intelligence Platform (UKIP, EPIC-UKDA-003): "
            "unlimited providers, canonical knowledge only, knowledge authored once."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("constitution", help="show the Knowledge Constitution")
    p.add_argument("--capability", help="show only the laws governing this capability")
    p.set_defaults(func=cmd_constitution)

    p = sub.add_parser("providers", help="list registered providers and their units")
    _add_source_flags(p)
    p.set_defaults(func=cmd_providers)

    p = sub.add_parser("assimilate", help="run the assimilation pipeline")
    _add_source_flags(p)
    p.set_defaults(func=cmd_assimilate)

    p = sub.add_parser("registry", help="show the canonical knowledge registry")
    _add_source_flags(p)
    p.add_argument("--full", action="store_true", help="include every record in full")
    p.set_defaults(func=cmd_registry)

    p = sub.add_parser("record", help="show one record, including its provenance")
    _add_source_flags(p)
    p.add_argument("reference", help="knowledge id, provider:key, bare key, or digest")
    p.set_defaults(func=cmd_record)

    p = sub.add_parser("classify", help="classify arbitrary text without registering it")
    p.add_argument("statement", help="the knowledge statement to classify")
    p.add_argument("--title")
    p.add_argument("--rationale")
    p.set_defaults(func=cmd_classify)

    p = sub.add_parser("relate", help="show resolved relationships")
    _add_source_flags(p)
    p.add_argument("--compose", action="store_true", help="include derived relationships")
    p.add_argument("--depth", type=int, default=3, help="composition depth (default 3)")
    p.set_defaults(func=cmd_relate)

    p = sub.add_parser("graph", help="show the knowledge graph")
    _add_source_flags(p)
    p.add_argument("--projection", help="show a single named projection")
    p.add_argument("--full", action="store_true", help="include nodes and edges")
    p.set_defaults(func=cmd_graph)

    p = sub.add_parser("impact", help="blast radius of a change to one record")
    _add_source_flags(p)
    p.add_argument("reference")
    p.set_defaults(func=cmd_impact)

    p = sub.add_parser("discover", help="search registered knowledge")
    _add_source_flags(p)
    p.add_argument("query", nargs="?", help="search terms")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--coverage", action="store_true", help="show discoverability coverage")
    p.set_defaults(func=cmd_discover)

    p = sub.add_parser("screen", help="discover-before-create determination")
    _add_source_flags(p)
    p.add_argument("statement", help="the knowledge you propose to author")
    p.add_argument("--title")
    p.add_argument("--rationale")
    p.add_argument("--kind", help="knowledge kind, enabling exact-duplicate detection")
    p.set_defaults(func=cmd_screen)

    p = sub.add_parser("provenance", help="show the provenance ledger")
    _add_source_flags(p)
    p.add_argument("reference", nargs="?", help="show one subject's chain")
    p.add_argument("--full", action="store_true", help="include every chain")
    p.set_defaults(func=cmd_provenance)

    p = sub.add_parser("validate", help="run the fail-closed validation suite")
    _add_source_flags(p)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("certify", help="certify knowledge intelligence per capability")
    _add_source_flags(p)
    p.set_defaults(func=cmd_certify)

    p = sub.add_parser("evidence", help="build, write, or verify the evidence bundle")
    _add_source_flags(p)
    p.add_argument("--out", metavar="DIR", help="write the bundle into DIR")
    p.add_argument("--verify", metavar="FILE", help="verify a stored bundle instead")
    p.set_defaults(func=cmd_evidence)

    p = sub.add_parser("stats", help="one-line knowledge intelligence summary")
    _add_source_flags(p)
    p.set_defaults(func=cmd_stats)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KnowledgeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["build_parser", "main", "EXIT_OK", "EXIT_GATE", "EXIT_ERROR"]
