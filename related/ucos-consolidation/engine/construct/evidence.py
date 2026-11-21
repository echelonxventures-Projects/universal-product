"""UCON-000001 Part 10 — evidence. A record of a measurement, and never Repository Truth.

Everything written here goes under the declared evidence home, which is untracked by design.
Deleting the whole directory changes no verdict — it only means the next run has to measure
again. That is the distinction between evidence and truth in this repository, and it is the
reason this module can write at all while every other part of the capability writes nothing.

The timestamp appears in the evidence payload and **nowhere else**. It is not an input to any
identity, not an input to any digest that participates in a verdict, and not an input to the
inventory. That is what lets law UCON-L-16 measure determinism at all: the measurement is a pure
function of the repository's committed bytes, and the only clock reading in the capability sits in
a field the verdict does not depend on.

:func:`assert_complete` refuses a payload that omits a declared record. A declared record with no
producer is a fault rather than a gap, because the declaration would then be describing an
artifact nobody writes — and an evidence manifest that lists artifacts which do not exist is
worse than no manifest, since it reads as coverage.
"""

from __future__ import annotations

import datetime as _datetime
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.construct.declaration import Declaration
from engine.construct.model import ConstructError

#: The declared record names this module produces, mapped to the key each occupies in the payload.
_PRODUCED = {
    "construct-foundation-report.json": "report",
    "closure-inventory.json": "inventory",
}


class EvidenceError(ConstructError):
    """The evidence payload is incomplete, or the declared home is unusable."""


def _observed_at() -> str:
    """The one clock reading in this capability, and it enters evidence only.

    Deliberately in its own function so that a search for the clock finds exactly one call site,
    and so that the docstring explaining why it is permissible sits next to it rather than in a
    design document nobody re-reads.
    """
    return _datetime.datetime.now(_datetime.UTC).replace(microsecond=0).isoformat()


def build(
    declaration: Declaration,
    report: Mapping[str, Any],
    inventory: Mapping[str, Any],
    *,
    command: str = "",
) -> dict[str, Any]:
    """The evidence payload: the law report, the closure inventory, and what produced them."""
    return {
        "schema": "ucos-construct-evidence",
        "version": "1.0.0",
        "authority": "NONE — DERIVED TRUTH. A record of a measurement, not a certification.",
        "declaration": declaration.artifact_id,
        "declaration_version": declaration.version,
        "command": command,
        "observed_at": _observed_at(),
        "$observed_at": "Present in evidence only. Not an input to any identity, digest "
        "or verdict.",
        "records": sorted(_PRODUCED),
        "report": dict(report),
        "inventory": dict(inventory),
    }


def assert_complete(declaration: Declaration, payload: Mapping[str, Any]) -> None:
    """Raise unless every declared evidence record is actually produced by this module."""
    declared = {str(row.get("record")) for row in declaration.evidence_records}
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


def _write_atomic(path: Path, payload: Mapping[str, Any]) -> Path:
    """Write ``payload`` atomically, sorted and newline-terminated.

    Atomically because a reader that observed a half-written evidence file would read a truncated
    JSON document as a corrupt one, and "the evidence is corrupt" and "the evidence says the gate
    closed" must never be confusable.
    """
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return path


def write(
    declaration: Declaration,
    report: Mapping[str, Any],
    inventory: Mapping[str, Any],
    *,
    repository: str,
    command: str = "",
) -> tuple[Path, ...]:
    """Write both declared records and return their paths. The only writer in this capability."""
    payload = build(declaration, report, inventory, command=command)
    assert_complete(declaration, payload)
    base = home(declaration, repository)
    written = [
        _write_atomic(base / "construct-foundation-report.json", payload),
        _write_atomic(base / "closure-inventory.json", dict(inventory)),
    ]
    return tuple(written)


def write_inventory(declaration: Declaration, inventory: Mapping[str, Any], *, path: str) -> Path:
    """Write the closure inventory to an explicit path, for a caller that wants it elsewhere.

    Used to materialise the audit deliverable outside the untracked evidence home. The caller
    names the path, because where an inventory belongs is a decision this module does not own.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    return _write_atomic(target, dict(inventory))


__all__ = [
    "EvidenceError",
    "assert_complete",
    "build",
    "home",
    "write",
    "write_inventory",
]
