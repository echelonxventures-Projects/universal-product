"""URKE-000001 Part 14 — evidence. A record of a measurement, never Repository Truth.

Everything written here goes under the declared evidence home, which is untracked by design.
Deleting the whole directory changes no verdict; it only means the next run has to measure again.

The timestamp appears in the evidence payload and nowhere else. It is not an input to any identity,
any digest that participates in a verdict, or the ledger. That is what lets the determinism law
measure anything at all: the report is a function of the repository's committed bytes, and the only
clock reading in the capability sits in a field no verdict depends on. This module is the one the
temporal scan exempts, for exactly that reason and for nothing else.
"""

from __future__ import annotations

import datetime as _datetime
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.recursive_knowledge.declaration import Declaration
from engine.recursive_knowledge.ledger import KnowledgeLedger
from engine.recursive_knowledge.model import RecursiveKnowledgeError

#: The declared record names this module produces, mapped to the payload key each occupies.
_PRODUCED = {
    "recursive-knowledge-report.json": "report",
    "knowledge-ledger.json": "ledger",
}


class EvidenceError(RecursiveKnowledgeError):
    """The evidence payload is incomplete, or the declared home is unusable. A fault."""


def _observed_at() -> str:
    """The one clock reading in this capability, and it enters evidence only.

    Deliberately in its own function so a search for the clock finds exactly one call site, with the
    reason it is permissible sitting beside it rather than in a document nobody re-reads.
    """
    return _datetime.datetime.now(_datetime.UTC).replace(microsecond=0).isoformat()


def build(
    declaration: Declaration,
    report: Mapping[str, Any],
    ledger: Mapping[str, Any],
    *,
    command: str = "",
) -> dict[str, Any]:
    """The evidence payload: the law report, the rendered ledger, and what produced them."""
    return {
        "schema": "ucos-recursive-knowledge-evidence",
        "version": "1.0.0",
        "record_authority": "NONE — DERIVED TRUTH. A record of a measurement, not a certification.",
        "declaration": declaration.artifact_id,
        "declaration_version": declaration.version,
        "command": command,
        "observed_at": _observed_at(),
        "$observed_at": (
            "Present in evidence only. Not an input to any identity, digest or verdict."
        ),
        "records": sorted(_PRODUCED),
        "report": dict(report),
        "ledger": dict(ledger),
    }


def assert_complete(declaration: Declaration, payload: Mapping[str, Any]) -> None:
    """Raise unless every declared evidence record is actually produced by this module."""
    declared = {str(row.get("record_name")) for row in declaration.evidence_records}
    missing = sorted(declared - set(_PRODUCED))
    if missing:
        raise EvidenceError(
            "the declaration names evidence records nothing produces: " + ", ".join(missing)
        )
    orphans = sorted(set(_PRODUCED) - declared)
    if orphans:
        raise EvidenceError(
            "this module produces records the declaration does not name: " + ", ".join(orphans)
        )
    for record, key in sorted(_PRODUCED.items()):
        if key not in payload:
            raise EvidenceError(f"the payload carries no {key!r} for declared record {record!r}")


def home(declaration: Declaration, repository: str) -> Path:
    """The declared evidence directory, created on demand."""
    if not declaration.evidence_home:
        raise EvidenceError("the declaration names no evidence home")
    path = Path(repository) / declaration.evidence_home
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_ledger(store: KnowledgeLedger) -> dict[str, Any]:
    """The whole ledger as a document: every subject, its histories, and the journal chain."""
    return {
        "journal": [entry.as_dict() for entry in store.journal],
        "subjects": [entity.as_dict() for entity in store.all()],
        "summary": store.summary(),
        "verification": store.verify(),
    }


def _write_atomic(path: Path, payload: Mapping[str, Any]) -> Path:
    """Write atomically, sorted and newline-terminated.

    Atomically because a reader that saw a half-written file would read truncated JSON as corrupt,
    and "the evidence is corrupt" must never be confusable with "the evidence says the gate closed".
    """
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return path


def write(
    declaration: Declaration,
    report: Mapping[str, Any],
    store: KnowledgeLedger,
    *,
    repository: str,
    command: str = "",
) -> tuple[Path, ...]:
    """Write both declared records and return their paths. The only writer in this capability."""
    rendered = render_ledger(store)
    payload = build(declaration, report, rendered, command=command)
    assert_complete(declaration, payload)
    base = home(declaration, repository)
    return (
        _write_atomic(base / "recursive-knowledge-report.json", payload),
        _write_atomic(base / "knowledge-ledger.json", rendered),
    )


def write_ledger(declaration: Declaration, store: KnowledgeLedger, *, path: str) -> Path:
    """Write the rendered ledger to an explicit path, for a caller that wants it elsewhere."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    return _write_atomic(target, render_ledger(store))


__all__ = [
    "EvidenceError",
    "assert_complete",
    "build",
    "home",
    "render_ledger",
    "write",
    "write_ledger",
]
