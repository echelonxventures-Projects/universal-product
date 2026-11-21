"""UCOS-CTRL-000001 — Universal Control Plane CLI.

One command over the whole control plane. Every subcommand reads *discovered*
repository state — there is no demo mode and no sample data behind any of them:

    ucos-ctrl truth           Repository Truth: sources, counts, classification
    ucos-ctrl state           registered lifecycle states and transitions
    ucos-ctrl registries      the four registries after engine registration
    ucos-ctrl registration    every registered control-plane engine
    ucos-ctrl plan            the master plan derived from registered programmes
    ucos-ctrl roadmap         milestones derived from registry volumes
    ucos-ctrl backlog         work derived from governance violations
    ucos-ctrl schedule        the derived backlog scheduled across discovered agents
    ucos-ctrl governance      per-object governance state and violations
    ucos-ctrl certification   certification status, eligibility and criteria
    ucos-ctrl version         version lineages across all seven dimensions
    ucos-ctrl evolution       observed change, deltas and replay digest
    ucos-ctrl linkage         constitutional linkage and any orphans
    ucos-ctrl consumption     measured cross-system consumption
    ucos-ctrl replay          durable journal reconstruction
    ucos-ctrl dashboard       the unified snapshot
    ucos-ctrl completion      the ten-criterion completion gate

Exit codes: 0 success, 1 operational error, 2 fatal/argument error. ``completion``
additionally exits 1 when the gate does not pass, so it is usable in CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from platform.universal_control_plane.discovery import ControlPlane
from platform.universal_control_plane.errors import ControlPlaneError
from typing import Any

COMMANDS: tuple[str, ...] = (
    "truth",
    "state",
    "registries",
    "registration",
    "plan",
    "roadmap",
    "backlog",
    "schedule",
    "governance",
    "certification",
    "version",
    "evolution",
    "linkage",
    "consumption",
    "replay",
    "dashboard",
    "completion",
)

#: Commands that need a durable journal to answer at all.
JOURNAL_COMMANDS: frozenset[str] = frozenset({"replay", "completion"})


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-ctrl",
        description="UCOS-CTRL-000001 Universal Control Plane (UCOS Ω∞).",
    )
    parser.add_argument("command", choices=COMMANDS, help="the operation to perform")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON on stdout")
    parser.add_argument(
        "--data-dir",
        default=None,
        help="registry data directory to discover from (default: the packaged substrate)",
    )
    parser.add_argument(
        "--repository-root",
        default=None,
        help="repository root for declared derived-truth artifacts (default: resolved)",
    )
    parser.add_argument(
        "--journal-root",
        default=None,
        help="root beneath which the durable replay journal is opened",
    )
    parser.add_argument(
        "--tick", type=int, default=0, help="logical tick for this run (default: 0)"
    )
    parser.add_argument(
        "--subject", default=None, help="restrict the output to one subject id where supported"
    )
    return parser


def _emit(payload: Any, *, as_json: bool, stream=None) -> None:
    out = stream or sys.stdout
    if as_json:
        print(json.dumps(payload, indent=2, default=str), file=out)
    else:
        _pretty(payload, out)


def _pretty(data: Any, out, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict | list):
                print(f"{pad}{k}:", file=out)
                _pretty(v, out, indent + 1)
            else:
                print(f"{pad}{k}: {v}", file=out)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                _pretty(item, out, indent)
            else:
                print(f"{pad}- {item}", file=out)
    else:
        print(f"{pad}{data}", file=out)


def _default_journal_root(args: argparse.Namespace) -> Path | None:
    """Where the journal lives for this run, when the command needs one.

    A command that reads the journal gets a temporary one rather than failing:
    the reconstruction is still real, it simply starts from this run's own
    determinations. Pass ``--journal-root`` to read or extend a durable one.
    """
    if args.journal_root:
        return Path(args.journal_root)
    if args.command in JOURNAL_COMMANDS:
        import tempfile

        return Path(tempfile.mkdtemp(prefix="ucos-ctrl-journal-"))
    return None


def _payload(plane: ControlPlane, command: str, subject: str | None) -> Any:
    """Project the composed control plane for one command."""
    if command == "truth":
        return plane.truth.to_dict(tick=plane.tick)
    if command == "state":
        return plane.state.to_dict()
    if command == "registries":
        return {
            "registries": [
                plane.registration.capability_registry.to_dict(),
                plane.registration.ownership_registry.to_dict(),
                plane.registration.dependency_registry.to_dict(),
                plane.agents.to_dict(),
            ]
        }
    if command == "registration":
        return plane.registration.to_dict()
    if command == "plan":
        return plane.plan.to_dict()
    if command == "roadmap":
        return plane.roadmap.to_dict()
    if command == "backlog":
        return plane.backlog.to_dict()
    if command == "schedule":
        return plane.schedule().to_dict()
    if command == "governance":
        if subject:
            return plane.governance.state_of(subject).to_dict()
        return plane.governance.to_dict()
    if command == "certification":
        if subject:
            return plane.certification.state_of(subject).to_dict()
        return plane.certification.to_dict()
    if command == "version":
        if subject:
            return {
                "subject_id": subject,
                "kinds": list(plane.version.kinds_for(subject)),
                "lineages": {
                    kind: [r.to_dict() for r in plane.version.lineage(subject, kind=kind)]
                    for kind in plane.version.kinds_for(subject)
                },
            }
        return plane.version.to_dict()
    if command == "evolution":
        return plane.evolution.to_dict()
    if command == "linkage":
        return plane.linkage.to_dict()
    if command == "consumption":
        plane.consume()
        return plane.consumption.to_dict()
    if command == "replay":
        if plane.journal is None:  # pragma: no cover — guarded by _default_journal_root
            raise ControlPlaneError("no durable journal is open; pass --journal-root")
        return {"journal": plane.journal.to_dict(), "state": plane.journal.reconstruct().to_dict()}
    if command == "dashboard":
        return plane.dashboard()
    # completion
    plane.consume()
    return plane.completion().to_dict()


def run(argv: list[str] | None = None, *, out=None, err=None) -> int:
    out = out or sys.stdout
    err = err or sys.stderr
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        plane = ControlPlane.discover(
            data_dir=args.data_dir,
            repository_root=args.repository_root,
            journal_root=_default_journal_root(args),
            tick=args.tick,
        )
        payload = _payload(plane, args.command, args.subject)
        _emit(payload, as_json=args.as_json, stream=out)
        if args.command == "completion" and not payload["complete"]:
            print(
                f"gate not met: {', '.join(payload['failures'])}",
                file=err,
            )
            return 1
        return 0

    except ControlPlaneError as exc:
        print(f"error: {exc}", file=err)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"fatal: {exc}", file=err)
        return 2


def main(argv: list[str] | None = None) -> None:
    sys.exit(run(argv))


if __name__ == "__main__":
    main()
