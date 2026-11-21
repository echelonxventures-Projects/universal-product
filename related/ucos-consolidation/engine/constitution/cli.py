"""UCOS-CEL-0001 — the one-command surface of the constitutional execution system.

Every subcommand emits canonical JSON on stdout and nothing else, so its output is
evidence: byte-identical across machines and runs, and directly diffable. Exit code 0
means the constitutional condition held; 1 means it did not. The CLI writes no file — a
determination is materialised by the authority that owns the truth it would enter.

The population it acts on
-------------------------
With ``--population <path>`` it reads declarations from a JSON document. With no path it
acts on :mod:`engine.constitution.catalog` — this package declaring itself — so
``ucos-cel acceptance`` in a bare checkout answers "does the constitutional
execution system satisfy its own constitution?" rather than "no input, nothing to say".
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from engine.constitution import (
    acceptance as enforcement_layer,
)
from engine.constitution import (
    assimilation as assimilation_gate,
)
from engine.constitution import (
    authority as authority_graph,
)
from engine.constitution import (
    catalog,
    law,
    metadata,
)
from engine.constitution import (
    dependency as dependency_graph,
)
from engine.constitution import (
    evolution as evolution_engine,
)
from engine.constitution import (
    gateway as mutation_gateway,
)
from engine.constitution import (
    legality as legality_engine,
)
from engine.constitution import (
    planner as execution_planner,
)
from engine.constitution import (
    replay as replay_engine,
)
from engine.constitution import (
    state as state_engine,
)
from engine.constitution.errors import ConstitutionalError


def _emit(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def _population(args: argparse.Namespace) -> metadata.Population:
    """The population under examination: a supplied document, or this package itself."""
    path = getattr(args, "population", "")
    if not path:
        return catalog.build_population()
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    records = document.get("records", document) if isinstance(document, dict) else document
    if not isinstance(records, list):
        raise ConstitutionalError(
            "a population document must carry a list of records",
            path=str(path),
        )
    return metadata.Population.of(
        metadata.ConstitutionalMetadata.declare(
            str(entry.get("subject", "")),
            universal_id=str(entry.get("universal_id", "")),
            **{
                facet_id: entry.get("facets", entry).get(facet_id, ())
                for facet_id in metadata.facet_ids()
            },
        )
        for entry in records
    )


def _with_digest(document: dict[str, Any], value: str) -> dict[str, Any]:
    document["digest"] = value
    return document


def _cmd_law(_args: argparse.Namespace) -> int:
    _emit(_with_digest(law.to_document(), law.digest()))
    return 0


def _cmd_mandate(_args: argparse.Namespace) -> int:
    _emit(_with_digest(metadata.to_document(), metadata.digest()))
    return 0


def _cmd_catalog(_args: argparse.Namespace) -> int:
    _emit(_with_digest(catalog.to_document(), catalog.digest()))
    return 0


def _cmd_population(args: argparse.Namespace) -> int:
    population = _population(args)
    _emit(_with_digest(population.to_dict(), population.digest()))
    return 0 if not population.incomplete() else 1


def _cmd_graph(args: argparse.Namespace) -> int:
    graph = dependency_graph.build(_population(args))
    _emit(_with_digest(graph.to_dict(), graph.digest()))
    return 0 if not graph.unknown_referents() else 1


def _cmd_authority(args: argparse.Namespace) -> int:
    population = _population(args)
    report = authority_graph.analyse(population, dependency_graph.build(population))
    _emit(_with_digest(report.to_dict(), report.digest()))
    return 0 if report.passed else 1


def _cmd_legality(args: argparse.Namespace) -> int:
    population = _population(args)
    report = legality_engine.assess(population, dependency_graph.build(population))
    _emit(_with_digest(report.to_dict(), report.digest()))
    return 0 if report.passed else 1


def _cmd_plan(args: argparse.Namespace) -> int:
    derived = execution_planner.plan(_population(args), strategy=args.strategy)
    _emit(_with_digest(derived.to_dict(), derived.digest()))
    return 0 if derived.executable else 1


def _cmd_replay(args: argparse.Namespace) -> int:
    record = replay_engine.converge(_population(args), max_rounds=args.max_rounds)
    _emit(_with_digest(record.to_dict(), record.digest()))
    return 0 if record.fixed_point else 1


def _cmd_seal(args: argparse.Namespace) -> int:
    population = _population(args)
    seal = state_engine.commit(population, source="cli")
    _emit(_with_digest(seal.to_dict(), seal.seal_digest()))
    return 0


def _cmd_assimilate(args: argparse.Namespace) -> int:
    verdict = assimilation_gate.assimilate(
        assimilation_gate.Proposal(
            subject=args.subject,
            owner=args.owner,
            outputs=tuple(args.outputs),
            inputs=tuple(args.inputs),
            intent=args.intent,
        ),
        _population(args),
    )
    _emit(_with_digest(verdict.to_dict(), verdict.digest()))
    return 0 if verdict.creatable else 1


def _cmd_gateway(_args: argparse.Namespace) -> int:
    _emit(_with_digest(mutation_gateway.to_document(), mutation_gateway.digest()))
    return 0


def _cmd_acceptance(args: argparse.Namespace) -> int:
    report = enforcement_layer.enforce(_population(args))
    _emit(_with_digest(report.to_dict(), report.digest()))
    return 0 if report.passed else 1


def _cmd_cycle(args: argparse.Namespace) -> int:
    record = evolution_engine.run(
        _population(args),
        evolution_engine.Goal(statement=args.goal, authority=args.authority),
    )
    _emit(_with_digest(record.to_dict(), record.digest()))
    return 0 if record.complete else 1


def _cmd_lifecycle(args: argparse.Namespace) -> int:
    """Run ``UCL-000001``'s 45 stages, discharged by this package's faculties."""
    from engine.nucleus import lifecycle as nucleus_lifecycle

    population = _population(args)
    execution = nucleus_lifecycle.execute(
        args.subject or "repository",
        stage_function=evolution_engine.lifecycle_stage_function(population),
        context={"frame": "constitutional-execution", "population": population.digest()},
    )
    _emit(_with_digest(execution.to_dict(), execution.digest()))
    return 0 if not execution.failures else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-cel",
        description=(
            "The Autonomous Constitutional Execution System: dependencies are discovered, "
            "order is derived, legality is proven, mutation passes the gateway, replay "
            "reaches a fixed point, and nothing certifies itself."
        ),
    )
    parser.add_argument(
        "--population",
        default="",
        help="path to a population document (default: this package, declared as itself)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("law", help="the constitutional execution law").set_defaults(func=_cmd_law)
    sub.add_parser("mandate", help="the constitutional metadata mandate").set_defaults(
        func=_cmd_mandate
    )
    sub.add_parser("catalog", help="the declared engines of this system").set_defaults(
        func=_cmd_catalog
    )
    sub.add_parser("population", help="the population under examination").set_defaults(
        func=_cmd_population
    )
    sub.add_parser("graph", help="the discovered constitutional dependency graph").set_defaults(
        func=_cmd_graph
    )
    sub.add_parser("authority", help="circularity and self-attestation").set_defaults(
        func=_cmd_authority
    )
    sub.add_parser("legality", help="the nine proofs, over every subject").set_defaults(
        func=_cmd_legality
    )
    sub.add_parser("seal", help="commit the state and emit its seal").set_defaults(func=_cmd_seal)
    sub.add_parser("gateway", help="the mutation pipeline and its derived order").set_defaults(
        func=_cmd_gateway
    )
    sub.add_parser(
        "acceptance", help="every invariant measured, every criterion resolved"
    ).set_defaults(func=_cmd_acceptance)

    plan = sub.add_parser("plan", help="the derived, legal execution order")
    plan.add_argument("--strategy", default="dependency-order", help="registered ordering rule")
    plan.set_defaults(func=_cmd_plan)

    replay = sub.add_parser("replay", help="converge to a deterministic fixed point")
    replay.add_argument("--max-rounds", type=int, default=replay_engine.DEFAULT_MAX_ROUNDS)
    replay.set_defaults(func=_cmd_replay)

    assimilate = sub.add_parser("assimilate", help="reuse-before-create analysis of a proposal")
    assimilate.add_argument("--subject", required=True)
    assimilate.add_argument("--owner", default="")
    assimilate.add_argument("--outputs", nargs="*", default=[])
    assimilate.add_argument("--inputs", nargs="*", default=[])
    assimilate.add_argument("--intent", default="")
    assimilate.set_defaults(func=_cmd_assimilate)

    cycle = sub.add_parser("cycle", help="run one autonomous constitutional evolution cycle")
    cycle.add_argument("--goal", default="verify the repository enforces its constitution")
    cycle.add_argument("--authority", default=catalog.DETERMINATION)
    cycle.set_defaults(func=_cmd_cycle)

    lifecycle = sub.add_parser(
        "lifecycle", help="run UCL-000001's 45 stages, discharged by these faculties"
    )
    lifecycle.add_argument("--subject", default="", help="subject to run the lifecycle over")
    lifecycle.set_defaults(func=_cmd_lifecycle)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ConstitutionalError as exc:
        _emit(exc.to_dict())
        return 1


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
