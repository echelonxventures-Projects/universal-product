"""UCOS-EPIC-014 — Repository Intelligence one-command CLI (Terminal T5).

    ucos-repo-intel scan                      # full cycle summary (all eight dimensions)
    ucos-repo-intel graph [--dot|--mermaid]   # the repository dependency graph
    ucos-repo-intel impact <capability>       # what breaks if a capability changes
    ucos-repo-intel gaps|conflicts|duplicates # one discovery register
    ucos-repo-intel reuse                     # capability reuse proof
    ucos-repo-intel ownership                 # derived ownership register
    ucos-repo-intel recommend                 # the ranked work list
    ucos-repo-intel advise <name> [--about T] # the never-duplicate guard
    ucos-repo-intel validate                  # composed acceptance gates + rules
    ucos-repo-intel certify                   # issue the sealed certificate
    ucos-repo-intel emit                      # persist every sealed artefact
    ucos-repo-intel verify                    # prove deterministic regeneration
    ucos-repo-intel hook                      # the one-line session-start summary

Exit status is fail-closed: ``0`` on success/PASS, ``1`` on FAIL, ``2`` on a configuration or
substrate fault. ``--repo`` targets any UCOS-shaped repository; ``--json`` emits the machine
form on stdout while the human summary always goes to stderr, so piping is safe.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from platform.repository_intelligence.config import (
    RepositoryIntelligenceConfig,
    load_config,
)
from platform.repository_intelligence.contracts import DiscoveryDimension, Finding
from platform.repository_intelligence.errors import RepositoryIntelligenceError
from platform.repository_intelligence.runtime import IntelligenceCycle
from platform.repository_intelligence.service import RepositoryIntelligenceService
from typing import TextIO


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-repo-intel",
        description="Repository Intelligence: continuous repository, capability, reuse, "
        "dependency, gap, conflict, duplicate and ownership discovery, with a repository "
        "dependency graph, recommendations, validation and sealed certification.",
    )
    parser.add_argument("--repo", help="repository root (default: auto-resolve)")
    parser.add_argument("--config", help="path to a JSON/TOML repository-intelligence config")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="emit the machine form on stdout"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("scan", "run a full intelligence cycle and summarize it"),
        ("reuse", "report capability reuse proof"),
        ("ownership", "report the derived ownership register"),
        ("recommend", "report the ranked recommendation work list"),
        ("validate", "run composed acceptance gates and intelligence rules"),
        ("certify", "issue the sealed repository intelligence certificate"),
        ("emit", "persist every sealed artefact"),
        ("verify", "prove deterministic regeneration"),
        ("hook", "print the one-line session-start summary"),
    ):
        sub.add_parser(name, help=help_text)
    for name in ("gaps", "conflicts", "duplicates"):
        sub.add_parser(name, help=f"report the {name[:-1]} register")
    graph_parser = sub.add_parser("graph", help="report the repository dependency graph")
    graph_parser.add_argument("--dot", action="store_true", help="render Graphviz DOT")
    graph_parser.add_argument("--mermaid", action="store_true", help="render a Mermaid flowchart")
    impact_parser = sub.add_parser("impact", help="report the change impact of a capability")
    impact_parser.add_argument("capability", help="capability name, e.g. platform.foundation")
    advise_parser = sub.add_parser("advise", help="ask whether a proposed capability may be built")
    advise_parser.add_argument("name", help="proposed capability name")
    advise_parser.add_argument("--about", default="", help="what the proposed capability would do")
    return parser


def _service(args: argparse.Namespace) -> RepositoryIntelligenceService:
    if args.config:
        config = load_config(args.config)
    else:
        config = RepositoryIntelligenceConfig.create(args.repo)
    return RepositoryIntelligenceService(config)


# ---------------------------------------------------------------------------
# human summaries (stderr)
# ---------------------------------------------------------------------------
def _print_cycle(cycle: IntelligenceCycle, stream: TextIO) -> None:
    report = cycle.report
    counts = report.counts()
    print("================ REPOSITORY INTELLIGENCE ================", file=stream)
    print(f"  repository: {report.repository_id}", file=stream)
    print(f"  substrate:  {report.substrate_digest[:16]}", file=stream)
    for result in report.dimension_results:
        c = result.counts()
        print(
            f"  {result.verdict.value.upper():4} {result.dimension.value:12}"
            f" {c['blocking_failed']} blocking, {c['advisory_failed']} advisory"
            f" of {c['total']} checks",
            file=stream,
        )
    print(
        f"  inventory:  {counts['capabilities']} capabilities, {counts['units']} units, "
        f"{counts['graph_nodes']} graph nodes, {counts['graph_edges']} graph edges",
        file=stream,
    )
    print(
        f"  validation: {cycle.validation.counts()['passed']}"
        f"/{cycle.validation.counts()['rules']} rules PASS"
        f" ({cycle.validation.counts()['composed_acceptance_gates']} composed acceptance gates)",
        file=stream,
    )
    for rule in cycle.validation.blocking_failures():
        print(f"        BLOCK {rule}", file=stream)
    if report.recommendations:
        top = report.recommendations[0]
        print(
            f"  next:       [P{top.priority}] {top.action.value.upper()} {top.subject}",
            file=stream,
        )
    print(
        f"  DETERMINATION: {cycle.certificate.determination.value}"
        f" | gate={cycle.certificate.gate}"
        f" | seal={cycle.certificate.seal_sha256[:16]}",
        file=stream,
    )
    print("=========================================================", file=stream)


def _print_findings(label: str, findings: tuple[Finding, ...], stream: TextIO) -> None:
    print(f"============ {label.upper()} ({len(findings)}) ============", file=stream)
    for finding in findings:
        marker = (
            "BLOCK"
            if finding.is_blocking_failure
            else ("ADVIS" if finding.is_advisory_failure else "PASS ")
        )
        print(f"  {marker} {finding.code:42} {finding.subject}", file=stream)
    print("=" * (28 + len(label)), file=stream)


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def _cmd_scan(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    cycle = service.scan()
    _print_cycle(cycle, sys.stderr)
    if args.as_json:
        _emit(cycle.report.to_dict())
    return 0 if cycle.certificate.certified else 1


def _cmd_graph(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    graph = service.graph()
    if args.dot:
        print(graph.to_dot(), end="")
        return 0
    if args.mermaid:
        print(graph.to_mermaid(), end="")
        return 0
    payload = graph.to_dict()
    counts = payload["counts"]
    print(
        f"repository graph: {counts['nodes']} nodes, {counts['edges']} edges "
        f"({counts['dependency_edges']} dependency), {counts['layers']} layers, "
        f"{counts['cycles']} cycle(s)",
        file=sys.stderr,
    )
    for index, layer in enumerate(payload["topological_layers"]):
        print(f"  layer {index}: {', '.join(layer)}", file=sys.stderr)
    for cycle in payload["cycles"]:
        print(f"  CYCLE: {' -> '.join(cycle)}", file=sys.stderr)
    if args.as_json:
        _emit(payload)
    return 0 if payload["acyclic"] else 1


def _cmd_impact(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    profile = service.graph().impact_of(args.capability)
    print(
        f"{profile['node']}: layer {profile['layer']}, blast radius {profile['blast_radius']}",
        file=sys.stderr,
    )
    for label in ("direct_dependents", "transitive_dependents", "direct_dependencies"):
        print(f"  {label}: {', '.join(profile[label]) or '-'}", file=sys.stderr)
    if args.as_json:
        _emit(profile)
    return 0


def _cmd_register(
    service: RepositoryIntelligenceService, args: argparse.Namespace, dimension: DiscoveryDimension
) -> int:
    findings = service.findings(dimension)
    _print_findings(dimension.value, findings, sys.stderr)
    if args.as_json:
        _emit({"dimension": dimension.value, "findings": [f.to_dict() for f in findings]})
    return 1 if any(f.is_blocking_failure for f in findings) else 0


def _cmd_reuse(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    report = service.report()
    print(f"============ CAPABILITY REUSE ({len(report.reuse)}) ============", file=sys.stderr)
    for assessment in report.reuse:
        print(
            f"  {assessment.proof.value:11} {assessment.capability:45}"
            f" {len(assessment.importers)} importer(s) {assessment.reuse_directive}",
            file=sys.stderr,
        )
    if args.as_json:
        _emit({"reuse": [r.to_dict() for r in report.reuse]})
    return 0


def _cmd_ownership(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    report = service.report()
    print(f"============ OWNERSHIP ({len(report.ownership)}) ============", file=sys.stderr)
    for record in report.ownership:
        print(f"  {record.confidence:9} {record.subject:45} {record.owner}", file=sys.stderr)
    if args.as_json:
        _emit({"ownership": [o.to_dict() for o in report.ownership]})
    return 1 if report.unowned_units() else 0


def _cmd_recommend(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    recommendations = service.recommendations()
    print(f"============ RECOMMENDATIONS ({len(recommendations)}) ============", file=sys.stderr)
    for recommendation in recommendations:
        print(
            f"  P{recommendation.priority} {recommendation.action.value.upper():9}"
            f" {recommendation.subject}",
            file=sys.stderr,
        )
        print(f"        {recommendation.rationale}", file=sys.stderr)
        if recommendation.target:
            print(f"        -> {recommendation.target}", file=sys.stderr)
    if args.as_json:
        _emit({"recommendations": [r.to_dict() for r in recommendations]})
    return 0


def _cmd_advise(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    recommendation = service.advise(args.name, args.about)
    print(f"proposal: {args.name}", file=sys.stderr)
    print(f"  ACTION: {recommendation.action.value.upper()}", file=sys.stderr)
    print(f"  {recommendation.rationale}", file=sys.stderr)
    if recommendation.target:
        print(f"  -> {recommendation.target}", file=sys.stderr)
    if args.as_json:
        _emit(recommendation.to_dict())
    # Fail-closed for a duplicate proposal: a caller scripting capability creation must be
    # stopped when an existing capability should be reused instead.
    return 0 if recommendation.action.value in ("create", "no_action") else 1


def _cmd_validate(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    validation = service.validation()
    counts = validation.counts()
    print(
        f"repository validation: {counts['passed']}/{counts['rules']} rules PASS "
        f"({counts['composed_acceptance_gates']} composed acceptance gates, "
        f"{counts['intelligence_rules']} intelligence rules)",
        file=sys.stderr,
    )
    for rule in validation.rules:
        marker = "PASS " if rule.passed else ("BLOCK" if rule.is_blocking_failure else "ADVIS")
        print(f"  {marker} {rule.rule_id:38} {rule.message[:80]}", file=sys.stderr)
    print(f"  VERDICT: {validation.verdict.value.upper()}", file=sys.stderr)
    if args.as_json:
        _emit(validation.to_dict())
    return 0 if validation.passed else 1


def _cmd_certify(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    certificate = service.certificate()
    certificate.require_integrity()
    print(certificate.hook_line(), file=sys.stderr)
    for rule in certificate.blocking_rules:
        print(f"  BLOCK {rule}", file=sys.stderr)
    if args.as_json:
        _emit(certificate.to_dict())
    return 0 if certificate.certified else 1


def _cmd_emit(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    written = service.emit()
    print(f"wrote {len(written)} artefacts:", file=sys.stderr)
    for path in written:
        print(f"  - {path}", file=sys.stderr)
    if args.as_json:
        _emit({"written": list(written)})
    return 0


def _cmd_verify(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    result = service.verify_determinism()
    if not result["conclusive"]:
        status = "INCONCLUSIVE"
    else:
        status = "DETERMINISTIC" if result["deterministic"] else "NON-DETERMINISTIC"
    print(
        f"{status}: {len(result['artifacts_compared'])} artefacts compared, "
        f"{len(result['mismatches'])} mismatch(es)",
        file=sys.stderr,
    )
    print(f"  {result['note']}", file=sys.stderr)
    for name in result["mismatches"]:
        print(f"  MISMATCH {name}", file=sys.stderr)
    if args.as_json:
        _emit(result)
    return 0 if result["deterministic"] else 1


def _cmd_hook(service: RepositoryIntelligenceService, args: argparse.Namespace) -> int:
    cycle = service.scan()
    print(cycle.certificate.hook_line())
    if args.as_json:
        _emit(cycle.summary())
    return 0


def _emit(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


_REGISTERS = {
    "gaps": DiscoveryDimension.GAP,
    "conflicts": DiscoveryDimension.CONFLICT,
    "duplicates": DiscoveryDimension.DUPLICATE,
}

_COMMANDS = {
    "scan": _cmd_scan,
    "graph": _cmd_graph,
    "impact": _cmd_impact,
    "reuse": _cmd_reuse,
    "ownership": _cmd_ownership,
    "recommend": _cmd_recommend,
    "advise": _cmd_advise,
    "validate": _cmd_validate,
    "certify": _cmd_certify,
    "emit": _cmd_emit,
    "verify": _cmd_verify,
    "hook": _cmd_hook,
}


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. 0 on success/PASS, 1 on FAIL, 2 on a configuration/substrate fault."""
    args = _build_parser().parse_args(argv)
    try:
        service = _service(args)
        if args.command in _REGISTERS:
            return _cmd_register(service, args, _REGISTERS[args.command])
        return int(_COMMANDS[args.command](service, args))
    except RepositoryIntelligenceError as exc:
        print(f"repository intelligence error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["main"]
