#!/usr/bin/env python3
"""UCOS-UCTX-001 — PHASE 10, the Context Closure Certification.

AUTHORITY = NONE (DERIVED TRUTH). This tool legislates nothing, mints nothing and confers
no standing. It answers the ten questions Phase 10 asks and records the measurement that
produced each answer. A certification that asserted rather than measured would be exactly
the "certified but unverified" contradiction the repository already refuses.

WHY THIS EXISTS, AND WHY IT IS SMALL. Phases 0 through 9 of the Context Authority
Consolidation are already built: one authority in 00-BOOK/DATA/context-authority.json, one
generated root in 00-BOOK/CONTEXT/, five agent projections that own nothing, a deterministic
generator at a proven fixed point, fifteen invariants, and an independent verifier that does
not import the generator. What was absent is the tenth phase — the certificate that states,
in one place, whether those ten claims hold today.

IT RE-IMPLEMENTS NOTHING (UCKP-ART-18). Every claim below is answered by CALLING the
instrument that already owns the question: `ukctx_gate.verify` for the invariants and
`ukctx_verify` for independent provenance. A second implementation of an invariant would be
a rival authority and void under UCKP-ART-03, and — worse in practice — it could disagree
with the gate while both reported success.

IT IS DETERMINISTIC AND CARRIES NO CLOCK. There is no timestamp anywhere in the output. A
certificate stamped with the hour it was produced differs on every run, could never reach a
fixed point, and would make INV-CTX-11 unprovable for its own artifact. What identifies this
certificate is the digest of the measurement it records, which is the only thing that should
change when the answer changes.

OUTPUT IS A GENERATED PROJECTION, NOT A TRACKED DOCUMENT. It is written under the same
Model B decision the projections use (context-authority.json :: projection_storage_model):
untracked, GENERATED_DETERMINISTIC, rebuilt by its declared command. That choice costs zero
identity allocations, which is the point — a certificate is product, not truth.

    python3 00-BOOK/tools/ukctx_certify.py            write the certificate
    python3 00-BOOK/tools/ukctx_certify.py --check    refuse if it is not at its fixed point
    python3 00-BOOK/tools/ukctx_certify.py --json     emit the record, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import ukctx_gate  # noqa: E402  — the gate owns the invariants; this tool owns none

#: Where the certificate lands. Under 00-BOOK/CONTEXT/ it would have to be produced by
#: ukctx.py or it would break that generator's fixed point, and it is not context — it is a
#: measurement ABOUT context. A sibling path keeps the two products separable.
CERTIFICATE = "00-BOOK/CONTEXT-CERTIFICATION/CONTEXT-CLOSURE-CERTIFICATION.md"

AUTHORITY = "00-BOOK/DATA/context-authority.json"

#: The five authored sources the storage model declares must carry permanent identity.
#: Named here because Phase 10 claim 10 is about what a FUTURE agent inherits, and an
#: authority with no identity cannot be cited by one.
AUTHORED_SOURCES = (
    "00-BOOK/DATA/context-authority.json",
    "00-BOOK/tools/ukctx.py",
    "00-BOOK/tools/ukctx_gate.py",
    "00-BOOK/tools/ukctx_verify.py",
    ".github/workflows/uctx-gate.yml",
)


def _read(relpath: str) -> str:
    with open(os.path.join(REPO, relpath), encoding="utf-8") as handle:
        return handle.read()


def _tracked() -> set[str]:
    out = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", "ls-files", "-z"],  # noqa: S607 - git from PATH by design
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return {p for p in out.split("\0") if p}


def _identities() -> dict:
    ledger = json.loads(_read("00-BOOK/DATA/id-ledger.json"))
    merged = dict(ledger.get("by_path", {}))
    merged.update(ledger.get("by_object", {}))
    return merged


# ---------------------------------------------------------------------------------- claims


def measure() -> dict:
    """Answer the ten Phase 10 questions by asking the instruments that own them."""
    decl = json.loads(_read(AUTHORITY))
    rows, summary = ukctx_gate.verify(strict_branch=False)
    by_id = {row["id"]: row for row in rows}

    def held(*invariants: str) -> tuple[bool, list[str]]:
        """A claim holds when every invariant that answers it reports no violation."""
        breaches: list[str] = []
        for iid in invariants:
            row = by_id.get(iid)
            if row is None:
                breaches.append(f"{iid} is not implemented by the gate")
            else:
                breaches.extend(f"{iid}: {v}" for v in row["violations"])
        return (not breaches), breaches

    verifier = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, os.path.join(HERE, "ukctx_verify.py")],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )

    identities = _identities()
    anonymous = [p for p in AUTHORED_SOURCES if p not in identities]

    tracked = _tracked()
    surfaces = [s["surface"] for s in decl["agent_surfaces"]]
    untracked_projections = [s for s in surfaces if s not in tracked]
    storage = decl["projection_storage_model"]
    bootstrapped = storage.get("tracked") is False and bool(storage.get("bootstrap_command"))

    claims = [
        (
            "C-01",
            "A single canonical context authority exists",
            *held("INV-CTX-01", "INV-CTX-04"),
            f"one authority declared at {AUTHORITY}",
        ),
        (
            "C-02",
            "Every context artifact is classified and resolves to that authority",
            *held("INV-CTX-02", "INV-CTX-03"),
            f"{len(decl['domains'])} domains declared, none orphaned",
        ),
        (
            "C-03",
            "Every projection is traceable to its canonical source",
            *held("INV-CTX-10"),
            f"{by_id['INV-CTX-10']['measured']} projections traced",
        ),
        (
            "C-04",
            "No duplicate authority remains",
            *held("INV-CTX-04", "INV-CTX-14", "INV-CTX-15"),
            "bounded-question uniqueness and kind-collision both measured",
        ),
        (
            "C-05",
            "No agent-exclusive truth remains",
            *held("INV-CTX-05", "INV-CTX-06", "INV-CTX-13"),
            f"{len(surfaces)} agent surfaces, all generated, none divergent",
        ),
        (
            "C-06",
            "No branch-exclusive truth remains",
            *held("INV-CTX-08"),
            f"{by_id['INV-CTX-08']['measured']} refs measured",
        ),
        (
            "C-07",
            "No worktree-exclusive truth remains",
            *held("INV-CTX-09"),
            f"{by_id['INV-CTX-09']['measured']} worktrees measured",
        ),
        (
            "C-08",
            "The generator reaches a fixed point",
            *held("INV-CTX-11", "INV-CTX-07"),
            f"{by_id['INV-CTX-11']['measured']} projections idempotent",
        ),
        (
            "C-09",
            "The repository reproduces context from a clean clone",
            bootstrapped and verifier.returncode == 0,
            ([] if bootstrapped else ["projection_storage_model declares no bootstrap command"])
            + ([] if verifier.returncode == 0 else ["the independent verifier refused"]),
            f"Model {storage.get('model')} — {len(untracked_projections)} projections rebuilt by "
            f"`{storage.get('bootstrap_command')}`; absence fails the gate rather than defaulting",
        ),
        (
            "C-10",
            "A future agent inherits context automatically",
            *held("INV-CTX-12"),
            f"{by_id['INV-CTX-12']['measured']} agent surfaces discovered by rule, none listed",
        ),
    ]

    records = [
        {"id": cid, "claim": text, "holds": ok, "breaches": breaches, "measurement": how}
        for cid, text, ok, breaches, how in claims
    ]

    # The certificate reports what it cannot prove as loudly as what it can. An authored
    # source with no identity is not an invariant breach — no INV-CTX rule asks — but a
    # certificate silent about it would be asserting more assurance than it measured.
    return {
        "artifact_id": "UCOS-UCTX-001.CONTEXT-CLOSURE-CERTIFICATION",
        "authority": "NONE — DERIVED TRUTH. Measurement only; this file certifies nothing "
        "of its own and creates no authority.",
        "constitutional_superior": decl["constitutional_superior"]["authority"],
        "subject": "UCOS-UCTX-001 Canonical Context Authority",
        "gate": {
            "invariants_implemented": len(rows),
            "invariants_failed": summary["failed"],
            "violations": summary["violations"],
        },
        "independent_verification": {
            "verifier": "00-BOOK/tools/ukctx_verify.py",
            "imports_the_generator": False,
            "passed": verifier.returncode == 0,
        },
        "claims": records,
        "claims_held": sum(1 for r in records if r["holds"]),
        "claims_total": len(records),
        "certifiable": all(r["holds"] for r in records),
        "unmeasured_obligations": [
            f"{p}: declared as an authored source that must carry permanent identity "
            f"(context-authority.json :: projection_storage_model.identity_cost), and holds none"
            for p in anonymous
        ],
    }


# ----------------------------------------------------------------------------------- render


def render(record: dict) -> str:
    out = io.StringIO()
    w = out.write
    w("# UCOS-UCTX-001 — CONTEXT CLOSURE CERTIFICATION\n\n")
    w(f"**Artifact ID**: {record['artifact_id']}  \n")
    w(f"**Authority**: {record['authority']}  \n")
    w(f"**Constitutional superior**: {record['constitutional_superior']}  \n")
    w(f"**Subject**: {record['subject']}\n\n")
    w(
        "> Generated by `00-BOOK/tools/ukctx_certify.py`. Never hand-authored. Carries no\n"
        "> timestamp, so it changes only when the measurement changes.\n\n"
    )

    verdict = "CERTIFIED" if record["certifiable"] else "REFUSED"
    w(f"## Determination — {verdict}\n\n")
    w(f"{record['claims_held']} of {record['claims_total']} Phase 10 claims hold. ")
    w(f"The gate implements {record['gate']['invariants_implemented']} invariants with ")
    w(f"{record['gate']['invariants_failed']} failing. ")
    w(
        "Independent verification "
        f"{'PASSED' if record['independent_verification']['passed'] else 'REFUSED'} — the "
        "verifier does not import the generator, so a uniformly wrong generator cannot make "
        "it agree.\n\n"
    )

    w("## The ten claims\n\n")
    w("| | Claim | Verdict | Measurement |\n|---|---|---|---|\n")
    for r in record["claims"]:
        mark = "**HOLDS**" if r["holds"] else "**REFUSED**"
        w(f"| `{r['id']}` | {r['claim']} | {mark} | {r['measurement']} |\n")

    breaches = [(r["id"], b) for r in record["claims"] for b in r["breaches"]]
    if breaches:
        w("\n## Breaches\n\n")
        for cid, b in breaches:
            w(f"- `{cid}` — {b}\n")

    if record["unmeasured_obligations"]:
        w("\n## Obligations no invariant measures\n\n")
        w("Declared by the authority itself and carried by no gate. Reported because a\n")
        w("certificate that named only what it measured would overstate its own reach.\n\n")
        for item in record["unmeasured_obligations"]:
            w(f"- {item}\n")

    w("\n---\n\n")
    w(f"**Measurement digest**: `{digest(record)}`\n")
    return out.getvalue()


def digest(record: dict) -> str:
    """Identity of the MEASUREMENT, not of the run. Two runs over one tree agree."""
    body = dict(record)
    body.pop("digest", None)
    canonical = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


# -------------------------------------------------------------------------------------- cli


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="ukctx_certify.py",
        description="UCOS-UCTX-001 Phase 10 — the Context Closure Certification.",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Refuse if the certificate on disk is not what this run derives.",
    )
    ap.add_argument(
        "--json", action="store_true", help="Emit the measurement record and write nothing."
    )
    args = ap.parse_args(argv)

    record = measure()
    if args.json:
        print(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if record["certifiable"] else 1

    text = render(record)
    path = os.path.join(REPO, CERTIFICATE)

    if args.check:
        if not os.path.isfile(path):
            print(f"REFUSED — {CERTIFICATE} is absent. Run this tool without --check.")
            return 1
        if _read(CERTIFICATE) != text:
            print(
                f"REFUSED — {CERTIFICATE} is not at its fixed point; it differs from "
                "what the current measurement derives."
            )
            return 1
        print(f"Certificate is at its fixed point ({digest(record)}).")
        return 0 if record["certifiable"] else 1

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(
        f"{'CERTIFIED' if record['certifiable'] else 'REFUSED'} — "
        f"{record['claims_held']}/{record['claims_total']} claims hold. "
        f"Written to {CERTIFICATE} ({digest(record)})."
    )
    return 0 if record["certifiable"] else 1


if __name__ == "__main__":
    sys.exit(main())
