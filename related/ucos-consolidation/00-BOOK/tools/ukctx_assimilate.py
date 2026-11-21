#!/usr/bin/env python3
"""UCOS-UCTX-001 — the context assimilation pipeline.

AUTHORITY = NONE (DERIVED TRUTH). This tool legislates nothing and decides nothing on its
own. It runs the four gates `context-authority.json :: assimilation_pipeline` declares, in
the order that instrument declares them, and refuses anything that does not pass all four.

WHAT IT IS FOR. Discussion routes IN to the proposer's own folder; implementation routes OUT
from one authority. This is the road between them, and until it existed there was no lawful
way to add context at all: hand-editing a projection is a drift failure, editing the
authority directly is an ungated mutation, and writing context somewhere unregistered is the
rival authority UCKP-ART-03 voids. A proposal is free to write and costs nothing; it simply
is not context until it has passed here.

ORDER IS THE POINT. Every check below already existed somewhere in the repository. What did
not exist was their running BEFORE the write. The generator emitted first and the gate
measured afterwards, which detects drift but cannot stop the authority absorbing a duplicate.
These four run against the MERGED result, before a byte is written.

IT CANNOT MINT ON ITS OWN. Identity allocation is irreversible and governed by REG-AUTO-001.
Without an operator permit this tool PLANS and refuses to write, which is why --plan is the
default and --assimilate must be asked for explicitly.

    python3 00-BOOK/tools/ukctx_assimilate.py              plan every discovered proposal
    python3 00-BOOK/tools/ukctx_assimilate.py --json       the plan as a record
    python3 00-BOOK/tools/ukctx_assimilate.py --assimilate merge (needs a permit)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DECLARATION = os.path.join(REPO, "00-BOOK", "DATA", "context-authority.json")
PERMITS = os.path.join(REPO, "00-BOOK", "DATA", "allocation-permits.json")

#: A proposal is front-matter plus prose. The keys are the minimum a gate can act on:
#: which declared domain it belongs to, and what it actually asserts.
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def declaration() -> dict:
    return json.loads(_read(DECLARATION))


# ------------------------------------------------------------------------------ discovery


def proposal_paths(decl: dict) -> list[str]:
    """Every declared proposal location, resolved. Discovered, never enumerated.

    The agent lane is derived from `agent_directories`, so a new agent directory brings its
    proposal path with it and this function does not change (UCKP-ART-08).
    """
    lane = decl["proposal_lane"]
    suffixes = tuple(lane["suffixes"])
    roots: list[str] = []
    for directory in decl["agent_directories"]:
        for pattern in lane["agent_paths"]:
            roots.append(pattern.replace("{agent_directory}", directory))
    roots.append(lane["developer_path"].split("{")[0])

    found: list[str] = []
    for root in roots:
        base = os.path.join(REPO, root)
        for dirpath, _dirs, files in os.walk(base):
            for name in sorted(files):
                if name.endswith(suffixes):
                    found.append(os.path.relpath(os.path.join(dirpath, name), REPO))
    return sorted(found)


def parse(relpath: str) -> tuple[dict, str, list[str]]:
    """(front matter, body, faults). A malformed proposal is a fault, never an exception."""
    text = _read(os.path.join(REPO, relpath))
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text, ["no front matter — a proposal must open with a --- block"]
    head, body = match.group(1), match.group(2)
    fields: dict[str, str] = {}
    for line in head.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields, body, []


# ---------------------------------------------------------------------------- the four gates


def gate_validate(decl: dict, fields: dict, body: str, faults: list[str]) -> list[str]:
    """Well formed, and names a domain this instrument actually declares."""
    findings = list(faults)
    domains = {d["domain"] for d in decl["domains"]}
    domain = fields.get("domain", "")
    if not domain:
        findings.append("declares no `domain`")
    elif domain not in domains:
        findings.append(
            f"domain {domain!r} is not declared by the authority; declared are: "
            + ", ".join(sorted(domains))
        )
    if not fields.get("author"):
        findings.append("declares no `author` — an unattributed contribution cannot be traced")
    if not body.strip():
        findings.append("states nothing")
    return findings


def gate_duplication(decl: dict, _fields: dict, body: str) -> list[str]:
    """Does the authority already say it? A second authoring is void (UCKP-ART-03).

    Compared on NORMALISED SENTENCES rather than whole documents, because the duplication
    that matters is a restated rule, not a byte-identical file — nobody ever re-authors a
    file verbatim, they re-author its content in different words around the same claim.
    """
    existing = " ".join(str(value) for value in _strings(decl)).lower()
    findings = []
    for sentence in _sentences(body):
        if len(sentence) >= 40 and sentence.lower() in existing:
            findings.append(f"already stated by the authority: {sentence[:90]!r}")
    return findings


def gate_overlap(decl: dict, fields: dict, body: str) -> list[str]:
    """Would it give one bounded question two answers?

    The authority already resolves each bounded question to exactly one owner; INV-CTX-14
    and INV-CTX-15 measure that. This gate refuses a proposal that asserts an answer in a
    domain other than the one it declares, which is how a second answer gets in.
    """
    findings = []
    mine = fields.get("domain", "")
    for other in decl["domains"]:
        name = other["domain"]
        if name == mine:
            continue
        claim = f"authority for {name}"
        if claim in body.lower():
            findings.append(
                f"claims authority for {name!r} while declaring domain {mine!r} — "
                "one bounded question, one owner"
            )
    return findings


def gate_verification() -> list[str]:
    """Does the merged authority still project faithfully?

    Delegated to the independent verifier, which does not import the producer. This tool
    deliberately owns no verification logic of its own: a second implementation could agree
    with a wrong generator, which is the whole failure MB7 describes.
    """
    run = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, os.path.join(HERE, "ukctx_verify.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if run.returncode != 0:
        tail = (run.stdout + run.stderr).strip().splitlines()[-3:]
        return ["the independent verifier refused: " + " / ".join(tail)]
    return []


def _strings(node) -> list:
    out: list = []
    if isinstance(node, dict):
        for value in node.values():
            out += _strings(value)
    elif isinstance(node, list):
        for value in node:
            out += _strings(value)
    elif isinstance(node, str):
        out.append(node)
    return out


def _sentences(body: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", body) if s.strip()]


# -------------------------------------------------------------------------------- the plan


#: What this tool needs the authority to declare before it can do anything. Named rather
#: than assumed: without the lane there is nowhere for a proposal to live, and without the
#: pipeline there is no declared order to run the gates in. Either absence is reported as a
#: refusal naming what is missing — never a KeyError, and never a silent empty plan, which
#: would report "nothing to assimilate" for a repository that has not adopted the lane at all.
REQUIRED_DECLARATIONS = ("proposal_lane", "assimilation_pipeline")


def plan() -> dict:
    decl = declaration()

    absent = [key for key in REQUIRED_DECLARATIONS if key not in decl]
    if absent:
        return {
            "artifact_id": "UCOS-UCTX-001.ASSIMILATION-PLAN",
            "authority": "NONE — DERIVED TRUTH. A plan, not an act.",
            "lane_declared": False,
            "undeclared": absent,
            "gates": [],
            "proposals": [],
            "admitted": 0,
            "refused": 0,
            "permit_present": False,
            "may_mint": False,
        }

    order = decl["assimilation_pipeline"]["order"]
    records = []

    for relpath in proposal_paths(decl):
        fields, body, faults = parse(relpath)
        results = {
            "validate": gate_validate(decl, fields, body, faults),
            "duplication": gate_duplication(decl, fields, body),
            "overlap": gate_overlap(decl, fields, body),
        }
        # Verification runs only if the cheaper gates pass — it executes another process,
        # and a proposal already refused does not earn one.
        results["verification"] = (
            gate_verification()
            if not any(results[g] for g in order[:-1])
            else ["not reached — an earlier gate refused"]
        )
        admitted = not any(results[g] for g in order)
        records.append(
            {
                "proposal": relpath,
                "author": fields.get("author", ""),
                "domain": fields.get("domain", ""),
                "sha256": _digest(_read(os.path.join(REPO, relpath))),
                "gates": {g: results[g] for g in order},
                "gates_passed": [g for g in order if not results[g]],
                "admitted": admitted,
            }
        )

    permit = os.path.isfile(PERMITS) and bool(json.loads(_read(PERMITS)).get("permits"))
    return {
        "artifact_id": "UCOS-UCTX-001.ASSIMILATION-PLAN",
        "authority": "NONE — DERIVED TRUTH. A plan, not an act.",
        "gates": order,
        "proposals": records,
        "admitted": sum(1 for r in records if r["admitted"]),
        "refused": sum(1 for r in records if not r["admitted"]),
        "permit_present": permit,
        "may_mint": permit,
    }


def render(record: dict) -> str:
    lines = ["UCOS-UCTX-001 Context Assimilation — PLAN", "-" * 60]
    if not record.get("lane_declared", True):
        lines.append("  REFUSED — the authority declares no proposal lane.")
        for key in record["undeclared"]:
            lines.append(f"           `{key}` is absent from context-authority.json")
        lines.append("  Nothing can be assimilated until the lane is declared. This is a")
        lines.append("  refusal, not an empty plan: the two read identically in a CI log.")
        return "\n".join(lines) + "\n"
    if not record["proposals"]:
        lines.append("  no proposals discovered under any declared proposal path.")
    for r in record["proposals"]:
        mark = "ADMIT " if r["admitted"] else "REFUSE"
        lines.append(
            f"  [{mark}] {r['proposal']}  (domain={r['domain'] or '—'}, "
            f"author={r['author'] or '—'})"
        )
        for gate, findings in r["gates"].items():
            for finding in findings:
                lines.append(f"           {gate}: {finding}")
    lines.append("-" * 60)
    lines.append(f"  admitted {record['admitted']} · refused {record['refused']}")
    if not record["permit_present"]:
        lines.append("  NO ALLOCATION PERMIT — identity is irreversible, so this run may plan")
        lines.append("  but may not mint. Obtain REG-AUTO-001 authorization to assimilate.")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="ukctx_assimilate.py",
        description="Run the four declared gates over every discovered context proposal.",
    )
    ap.add_argument("--json", action="store_true", help="emit the plan record")
    ap.add_argument(
        "--assimilate",
        action="store_true",
        help="merge admitted proposals (requires an allocation permit)",
    )
    ap.add_argument(
        "--gate",
        action="store_true",
        help=(
            "CI mode: refuse only when a discovered proposal is refused. An undeclared "
            "lane is the committed state, not a fault, so it passes here while the bare "
            "CLI still reports it as a refusal."
        ),
    )
    args = ap.parse_args(argv)

    record = plan()

    if args.assimilate and not record["may_mint"]:
        print(
            "REFUSED — assimilation mints a Universal ID, which is IRREVERSIBLE and "
            "governed by REG-AUTO-001.\n"
            "         No permit is present in 00-BOOK/DATA/allocation-permits.json.\n"
            "         This tool may not self-authorize an allocation. Run without "
            "--assimilate to plan.",
            file=sys.stderr,
        )
        return 2

    if args.json:
        print(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render(record), end="")
    if not record.get("lane_declared", True):
        # A GATE AND A CLI ASK DIFFERENT QUESTIONS. The gate asks "is any proposal in a
        # bad state?" — with no lane there are no proposals, so nothing is wrong, and a
        # stage that failed for a subsystem the repository has not adopted would be
        # refusing its own roadmap. The bare CLI asks "can you assimilate?", and there
        # the honest answer is no.
        return 0 if args.gate else 2
    return 0 if record["refused"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
