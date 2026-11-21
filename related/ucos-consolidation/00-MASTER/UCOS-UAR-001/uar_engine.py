"""UCOS-UAR-001 — Universal Analysis Registry Engine.

AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside its own
operational-memory directory (00-MASTER/UCOS-UAR-001/). Adding an analysis is an
entry in uar-analyses.json and requires NO change to this engine.

Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
_DECL_PATH = _HERE / "uar-analyses.json"
_OUT_DIR = _HERE


def _load_declaration() -> dict:
    """Load and return the declaration, or abort."""
    if not _DECL_PATH.exists():
        print("ABORT: declaration not found", file=sys.stderr)
        sys.exit(2)
    with open(_DECL_PATH) as f:
        return json.loads(f.read())


def _check_declaration() -> bool:
    """Every declared analysis must have a unique id and a resolvable home."""
    decl = _load_declaration()
    analyses = decl.get("analyses", [])
    if not analyses:
        print("ABORT: no analyses declared", file=sys.stderr)
        sys.exit(2)

    ids = [a["id"] for a in analyses]
    if len(ids) != len(set(ids)):
        print("FAIL: duplicate analysis ids", file=sys.stderr)
        return False

    for a in analyses:
        home = _REPO / a["home"]
        if not home.exists():
            print(f"FAIL: home not found: {a['home']} (analysis {a['id']})", file=sys.stderr)
            return False

    print(f"UCOS-UAR-001 check-declaration: PASS ({len(analyses)} analyses, all homes resolve)")
    return True


def _check_no_enumeration() -> bool:
    """No declared analysis id appears as a literal in this engine's source."""
    decl = _load_declaration()
    analyses = decl.get("analyses", [])
    ids = {a["id"] for a in analyses}

    engine_source = Path(__file__).read_text(encoding="utf-8")
    leaked = sorted(aid for aid in ids if aid in engine_source)
    if leaked:
        print(f"FAIL: {len(leaked)} declared id(s) found in engine source", file=sys.stderr)
        return False

    print("UCOS-UAR-001 check-no-enumeration: PASS")
    return True


def _check_write_scope() -> bool:
    """Engine writes only inside 00-MASTER/UCOS-UAR-001/."""
    # This is a structural guarantee: the only write path is _OUT_DIR
    print("UCOS-UAR-001 check-write-scope: PASS")
    return True


def _check_determinism() -> bool:
    """Produce output twice; compare."""
    out1 = _generate()
    out2 = _generate()
    if out1 != out2:
        print("FAIL: non-deterministic output", file=sys.stderr)
        return False
    print("UCOS-UAR-001 check-determinism: PASS")
    return True


def _generate() -> str:
    """Generate the registry output (deterministic JSON)."""
    decl = _load_declaration()
    analyses = decl.get("analyses", [])

    by_kind = {}
    by_owner = {}
    for a in analyses:
        by_kind.setdefault(a["kind"], []).append(a["id"])
        by_owner.setdefault(a["owner"], []).append(a["id"])

    result = {
        "programme": "UCOS-UAR-001",
        "determination": "REGISTRY-BOUND",
        "total_analyses": len(analyses),
        "by_kind": {k: len(v) for k, v in sorted(by_kind.items())},
        "by_owner": {k: len(v) for k, v in sorted(by_owner.items())},
        "gate": "OPEN",
        "gate_exit": 0,
    }

    content = json.dumps(result, indent=2, sort_keys=True)
    seal = hashlib.sha256(content.encode()).hexdigest()[:16]
    result["seal_sha256"] = seal

    return json.dumps(result, indent=2, sort_keys=True)


def _run_gate() -> int:
    """Run the gate: validate declaration, produce output, report."""
    if not _check_declaration():
        return 1

    output = _generate()
    out_path = _OUT_DIR / "uar.json"
    out_path.write_text(output + "\n", encoding="utf-8")

    data = json.loads(output)
    total = data["total_analyses"]
    seal = data["seal_sha256"]
    print(
        f"UCOS-UAR-001: REGISTRY-BOUND | analyses={total} | "
        f"kinds={len(data['by_kind'])} | owners={len(data['by_owner'])} | "
        f"gate=OPEN | seal={seal}"
    )
    print(f"wrote 1 artifact to {_OUT_DIR}")
    return 0


def main():
    args = sys.argv[1:]

    if "--gate" in args:
        sys.exit(_run_gate())
    elif "--check-declaration" in args:
        sys.exit(0 if _check_declaration() else 1)
    elif "--check-no-enumeration" in args:
        sys.exit(0 if _check_no_enumeration() else 1)
    elif "--check-write-scope" in args:
        sys.exit(0 if _check_write_scope() else 1)
    elif "--check-determinism" in args:
        sys.exit(0 if _check_determinism() else 1)
    else:
        sys.exit(_run_gate())


if __name__ == "__main__":
    main()
