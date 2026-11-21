"""UCKP — the Universal Constitutional Knowledge Universe CLI.

One command surface over the assembled universe:

    ucos-uckp law           # the root law: articles, invariants, stop conditions
    ucos-uckp build         # assemble the universe and describe it
    ucos-uckp validate      # measure all seventeen invariants (fail-closed)
    ucos-uckp assimilate    # assimilate every existing UCOS artifact, prove invertibility
    ucos-uckp project       # generate every projection of the universe
    ucos-uckp persist       # prove every persistence technology interchangeable
    ucos-uckp execute       # prove every execution technology interchangeable
    ucos-uckp replay        # re-derive states, decisions and projections
    ucos-uckp govern        # every governance question, decided and replayed
    ucos-uckp reason        # what the universe concludes about itself
    ucos-uckp certify       # the whole judgement: validate + stop conditions
    ucos-uckp describe      # the machine-readable self-description

Exit status is fail-closed, matching the repository convention: ``0`` on success,
``1`` when the constitutional verdict is REFUSED, ``2`` on a fault that prevented any
verdict being reached. The distinction matters — "the universe is not lawful" and "I
could not tell whether the universe is lawful" are different answers, and collapsing
them into one exit code is how an unmeasured invariant comes to look like a passing one.

``--assimilate`` includes the 1201 existing UCOS artifacts. Without it the commands
operate on the constitutional core alone, which is the faster loop when the question is
about the law rather than about the corpus.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

from engine.uckp.assimilation import (
    AssimilationReport,
    assimilate,
    build_assimilated_universe,
)
from engine.uckp.canonical import canonical_json
from engine.uckp.errors import UCKPError
from engine.uckp.execution import verify_execution_interchangeable
from engine.uckp.law import ROOT_LAW
from engine.uckp.persistence import verify_interchangeable
from engine.uckp.projection import assert_no_projection_authority
from engine.uckp.universe import (
    ConstitutionalUniverse,
    build_universe,
    universe_execution_request,
)
from engine.uckp.validation import ConstitutionalValidator, ValidationReport

COMMANDS: tuple[str, ...] = (
    "law",
    "build",
    "validate",
    "assimilate",
    "project",
    "persist",
    "execute",
    "replay",
    "govern",
    "reason",
    "certify",
    "describe",
)

#: Returned when the constitution refuses the universe (a verdict was reached).
EXIT_REFUSED = 1

#: Returned when no verdict could be reached at all.
EXIT_FAULT = 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-uckp",
        description=(
            "Universal Constitutional Knowledge Universe (UCKP-LAW-0001) — "
            "assemble, validate, assimilate, project and certify."
        ),
    )
    parser.add_argument("command", choices=COMMANDS, help="the operation to perform")
    parser.add_argument(
        "--assimilate",
        action="store_true",
        dest="with_artifacts",
        help="include every existing UCOS artifact (reads the artifact registry)",
    )
    parser.add_argument(
        "--source-root",
        default=None,
        help="repository root used for source-level checks and assimilation",
    )
    parser.add_argument(
        "--persistence-base",
        default=None,
        help="directory the persistence adapters write to (default: a temporary directory)",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    return parser


def _assemble(
    *, with_artifacts: bool, source_root: str | None, persistence_base: str
) -> tuple[ConstitutionalUniverse, AssimilationReport | None]:
    if with_artifacts:
        universe, report = build_assimilated_universe(
            source_root=source_root, persistence_base=persistence_base
        )
        return universe, report
    return build_universe(persistence_base=persistence_base), None


def _law_payload() -> dict[str, object]:
    return {
        "law_id": ROOT_LAW.law_id,
        "version": ROOT_LAW.version,
        "digest": ROOT_LAW.digest(),
        "supremacy": ROOT_LAW.supremacy,
        "counts": {
            "articles": len(ROOT_LAW.articles),
            "invariants": len(ROOT_LAW.invariants),
            "stop_conditions": len(ROOT_LAW.stop_conditions),
            "governed_categories": len(ROOT_LAW.governed_categories),
            "non_authoritative_categories": len(ROOT_LAW.non_authoritative_categories),
        },
        "articles": [article.to_dict() for article in ROOT_LAW.articles],
        "invariants": [invariant.to_dict() for invariant in ROOT_LAW.invariants],
        "stop_conditions": [condition.to_dict() for condition in ROOT_LAW.stop_conditions],
    }


def _project_payload(universe: ConstitutionalUniverse) -> dict[str, object]:
    objects = universe.objects()
    artifacts = universe.projections.project_all(objects)
    return {
        "kinds": list(universe.projections.kinds()),
        "authority_claims": list(assert_no_projection_authority(artifacts)),
        "replays_identically": universe.projections.replays_identically(objects),
        "artifacts": [
            {**artifact.to_dict(), "payload_bytes": len(artifact.payload)} for artifact in artifacts
        ],
    }


def _persist_payload(universe: ConstitutionalUniverse) -> dict[str, object]:
    report = verify_interchangeable(universe.persistence, universe.objects())
    return {
        "adapters": len(universe.persistence),
        "base": universe.persistence_base,
        **report.to_dict(),
    }


def _execute_payload(universe: ConstitutionalUniverse) -> dict[str, object]:
    # Two universe-wide operations plus one that needs a subject, so interchangeability
    # is proven for both shapes of request rather than only the subject-free kind.
    root_id = universe.root_id()
    requests = (
        universe_execution_request("universe-seal"),
        universe_execution_request("graph-fingerprint"),
        universe_execution_request("describe", root_id),
        universe_execution_request("authority-chain", root_id),
    )
    reports = [
        verify_execution_interchangeable(universe.execution, request, universe.registry)
        for request in requests
    ]
    return {
        "adapters": len(universe.execution),
        "operations": [report.to_dict() for report in reports],
        "interchangeable": all(not report.failures for report in reports),
        "knowledge_owners": sorted({k for r in reports for k in r.knowledge_owners}),
    }


def _replay_payload(universe: ConstitutionalUniverse) -> dict[str, object]:
    timeline = universe.timeline
    return {
        "timeline": {
            "states": len(timeline.states()),
            "verified": timeline.verify(),
            "proofs_complete": timeline.proofs_complete(),
            "replays_identically": timeline.replays_identically(),
            "fingerprint": timeline.fingerprint(),
        },
        "governance": {
            "decisions": len(universe.governance.decisions()),
            "replays_identically": universe.governance.replays_identically(),
        },
        "projections": {
            "replays_identically": universe.projections.replays_identically(universe.objects())
        },
        "objects": {
            "without_holding_replay_proof": sorted(
                obj.ucko_id for obj in universe.objects() if not obj.verify_replay()
            )[:20]
        },
        "evolution": {
            "records": len(universe.evolution.records()),
            "cycles": universe.evolution.cycles(),
            "terminated": universe.evolution.is_terminated(),
            "fingerprint": universe.evolution.fingerprint(),
        },
    }


def _govern_payload(universe: ConstitutionalUniverse) -> dict[str, object]:
    governance = universe.governance
    return {
        "rules": len(governance.rules()),
        "questions": list(governance.questions()),
        "replays_identically": governance.replays_identically(),
        "decisions": [
            {**decision.to_dict(), "replayed": governance.replay(decision)}
            for decision in governance.decisions()
        ],
    }


def _payload(
    command: str,
    universe: ConstitutionalUniverse | None,
    report: AssimilationReport | None,
    validation: ValidationReport | None,
) -> dict[str, object]:
    if command == "law":
        return _law_payload()
    if universe is None:  # pragma: no cover - guarded by the caller
        raise UCKPError("this command requires an assembled universe", command=command)
    if command in {"build", "describe"}:
        return universe.describe() if command == "build" else universe.to_document()
    if command == "assimilate":
        if report is None:
            raise UCKPError("assimilate requires the artifact registry")
        return report.to_dict()
    if command == "project":
        return _project_payload(universe)
    if command == "persist":
        return _persist_payload(universe)
    if command == "execute":
        return _execute_payload(universe)
    if command == "replay":
        return _replay_payload(universe)
    if command == "govern":
        return _govern_payload(universe)
    if command == "reason":
        return universe.intelligence().report()
    if validation is None:  # pragma: no cover - validate/certify always measure first
        raise UCKPError("no validation report was produced", command=command)
    payload = validation.to_dict()
    if command == "certify":
        payload["assimilation"] = report.to_dict() if report is not None else None
        payload["universe"] = universe.describe()
    return payload


def _print_summary(
    command: str,
    universe: ConstitutionalUniverse | None,
    report: AssimilationReport | None,
    validation: ValidationReport | None,
    stream: object,
) -> None:
    def emit(line: str = "") -> None:
        print(line, file=stream)  # type: ignore[call-overload]

    emit("=========================================================")
    emit(f"UCKP {ROOT_LAW.law_id} v{ROOT_LAW.version} — {command}")
    emit("=========================================================")
    if universe is not None:
        counts = cast("Mapping[str, int]", universe.describe()["counts"])
        emit(f"  objects:        {counts['objects']}")
        emit(f"  edges:          {counts['edges']}")
        emit(f"  providers:      {counts['providers']}")
        emit(f"  root:           {universe.root_id()}")
        emit(f"  seal:           {universe.seal()[:32]}")
        emit(f"  fingerprint:    {universe.fingerprint()[:32]}")
    if command == "law":
        emit(f"  articles:       {len(ROOT_LAW.articles)}")
        emit(f"  invariants:     {len(ROOT_LAW.invariants)}")
        emit(f"  stop conditions:{len(ROOT_LAW.stop_conditions)}")
    if report is not None:
        emit()
        emit(f"  assimilation:   {report.summary()}")
    if validation is not None:
        emit()
        for line in validation.summary().splitlines():
            emit(f"  {line}")
    emit("=========================================================")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. 0 on success, 1 when refused, 2 on a fault."""
    args = _build_parser().parse_args(argv)
    universe: ConstitutionalUniverse | None = None
    report: AssimilationReport | None = None
    validation: ValidationReport | None = None

    with tempfile.TemporaryDirectory(prefix="uckp-cli-") as scratch:
        base = args.persistence_base or scratch
        try:
            if args.command == "assimilate" and not args.with_artifacts:
                # Asking to assimilate is asking for the artifacts, so do not require
                # the caller to say so twice.
                args.with_artifacts = True
            if args.command != "law":
                universe, report = _assemble(
                    with_artifacts=args.with_artifacts,
                    source_root=args.source_root,
                    persistence_base=base,
                )
            elif args.with_artifacts:
                _, report = assimilate()
            if args.command in {"validate", "certify"} and universe is not None:
                validation = ConstitutionalValidator(
                    universe, source_root=args.source_root
                ).validate()
            payload = _payload(args.command, universe, report, validation)
        except UCKPError as exc:
            print(f"uckp fault: {exc}", file=sys.stderr)
            return EXIT_FAULT
        except OSError as exc:
            print(f"uckp io fault: {exc}", file=sys.stderr)
            return EXIT_FAULT

        _print_summary(args.command, universe, report, validation, sys.stderr)
        if args.as_json:
            print(json.dumps(payload, indent=2, sort_keys=True))

        if validation is not None and not validation.certified:
            return EXIT_REFUSED
        if report is not None and not report.lossless:
            return EXIT_REFUSED
        if args.command == "project" and payload.get("authority_claims"):
            return EXIT_REFUSED
        if args.command == "persist" and payload.get("failures"):
            return EXIT_REFUSED
        if args.command == "execute" and not payload.get("interchangeable"):
            return EXIT_REFUSED
        return 0


def write_projections(
    universe: ConstitutionalUniverse, destination: str | Path
) -> tuple[Path, ...]:
    """Write every projection to ``destination``, returning the paths written.

    Offered as a function rather than a command because writing generated views into a
    working tree is a side effect on the repository, and Article 4 is easier to keep
    true when that step is explicit.
    """
    root = Path(destination)
    written: list[Path] = []
    for artifact in universe.projections.project_all(universe.objects()):
        target = root / Path(artifact.locator).name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(artifact.payload, encoding="utf-8")
        written.append(target)
    manifest = root / "projection-manifest.json"
    manifest.write_text(
        canonical_json(universe.projections.to_document(universe.objects())), encoding="utf-8"
    )
    written.append(manifest)
    return tuple(written)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["COMMANDS", "EXIT_FAULT", "EXIT_REFUSED", "main", "write_projections"]
