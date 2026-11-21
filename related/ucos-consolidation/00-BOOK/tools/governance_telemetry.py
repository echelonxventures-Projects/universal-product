"""
UCOS Ω∞ — Governance Runtime Telemetry (EC3 Phase-3 · Runtime Telemetry Finalization).

THE single append-only writer, THE single location, and THE single sequence
authority for ALL runtime governance telemetry (the enforcement / synchronization
/ certification audit logs). This module is the root-cause remediation for the
last sources of telemetry non-determinism.

WHY THIS MODULE EXISTS
----------------------
Before Phase-3 each engine re-implemented its own audit appender and its own JSON
writer, and every audit log was written into the *version-tracked* ``00-BOOK/DATA``
tree:

    ukb.py ::  _enforcement_audit()  +  _dump_json()   -> DATA/enforcement-audit.json
    ukbx.py::  _sync_audit_append()  +  _dump()         -> DATA/sync-audit.json
    ukbx.py::  _cert_audit_append()  +  _dump()         -> DATA/certification-audit.json

That produced two anomalies:

  * ANOMALY A — a deleted audit log silently *reappeared* at the canonical
    ``00-BOOK/DATA`` location on the next gate run, because the writer targeted
    the tracked tree unconditionally. Telemetry became a source of git drift.
  * ANOMALY B — the audit **sequence** was derived from the log file itself
    (``seq = runs[-1].seq + 1``). Removing the file reset the sequence to 1
    (e.g. 346 → 1), because a missing file was treated as a fresh sequence.

FINALIZED ARCHITECTURE (one of everything; zero legacy)
-------------------------------------------------------
  * ONE location   — ``<repo>/.runtime/governance/``. Runtime telemetry is
                     per-clone *operational* state, git-ignored, and is NEVER a
                     repository artifact. It can never live under 00-BOOK/DATA.
  * ONE writer     — :func:`append_audit` is the only function that persists an
                     audit run. It owns path resolution, sequence assignment, and
                     the atomic write. There is no second implementation.
  * ONE sequence   — the monotonic ``seq`` is assigned here and only here.
  * ONE history    — the runtime log under the governance dir is the single
                     history authority. A fresh runtime has no history and each
                     sequence begins at 1 (the documented, intentional lifecycle).
  * FROZEN path    — :func:`_resolve` and :func:`forbid_data_telemetry` make the
                     repository structurally incapable of writing an audit log
                     into 00-BOOK/DATA. An attempt raises :class:`TelemetryPathError`.

RUNTIME LIFECYCLE (explicit — Task 7)
-------------------------------------
    fresh clone / fresh runtime            no .runtime/governance/<log>
        │                                  │
        ▼                                  ▼
    first gate run  ───────────────►  append_audit() creates the log, seq = 1
        │
        ▼
    subsequent runs  ──────────────►  seq increments monotonically, forever
                                       (idempotent no-op runs never grow the log)

The sequence is therefore *runtime* state, not repository history. The historical
tracked logs (which reached enforcement seq 345 / sync 22 / cert 4) were removed
from version control as part of the telemetry↔canonical separation; they are no
longer repository history, so a per-clone runtime that starts at seq 1 is CORRECT
and EXPECTED — not a regression.

Standard library only. Imported by ukb.py and ukbx.py as ``governance_telemetry``.
"""

from __future__ import annotations

import datetime as _dt
import json
import os

# --- Canonical location -----------------------------------------------------
# Resolved relative to this file so it is invariant to the caller's CWD:
#   00-BOOK/tools/governance_telemetry.py  ->  BOOK_DIR=00-BOOK  ->  REPO=repo root
_HERE = os.path.dirname(os.path.abspath(__file__))
_BOOK_DIR = os.path.dirname(_HERE)
REPO = os.path.dirname(_BOOK_DIR)

# THE one runtime telemetry location. Git-ignored (.gitignore: `.runtime/`),
# per-clone, never tracked, never under 00-BOOK/DATA.
GOVERNANCE_DIR = os.path.join(REPO, ".runtime", "governance")

# The ONLY telemetry logs. Filenames are kept identical to their historical names
# so operators recognize them; only the LOCATION changed (DATA/ -> .runtime/).
ENFORCEMENT_AUDIT = "enforcement-audit.json"
SYNC_AUDIT = "sync-audit.json"
CERT_AUDIT = "certification-audit.json"
AUDIT_LOGS = frozenset({ENFORCEMENT_AUDIT, SYNC_AUDIT, CERT_AUDIT})


class TelemetryPathError(RuntimeError):
    """Raised when telemetry is directed anywhere but the governance runtime dir.

    This is the enforcement mechanism of the frozen-path invariant: telemetry
    lives under :data:`GOVERNANCE_DIR` and nowhere else. It exists so a future
    contributor cannot accidentally reintroduce tracked, drift-producing
    telemetry under 00-BOOK/DATA.
    """


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _resolve(name: str) -> str:
    """Resolve an audit-log NAME to its one canonical runtime path, asserting the
    frozen-path invariant. ``name`` must be one of :data:`AUDIT_LOGS` (a bare log
    name, never a path); anything else — including a value that would escape the
    governance dir — is a hard :class:`TelemetryPathError`."""
    if name not in AUDIT_LOGS:
        raise TelemetryPathError(
            f"unknown telemetry log {name!r}; expected one of {sorted(AUDIT_LOGS)}"
        )
    path = os.path.join(GOVERNANCE_DIR, name)
    resolved = os.path.realpath(path)
    root = os.path.realpath(GOVERNANCE_DIR)
    if resolved != os.path.join(root, name):
        raise TelemetryPathError(
            f"telemetry path escapes the governance runtime dir: {resolved}"
        )
    return path


def load_audit(name: str) -> dict:
    """Read an audit log from the one location. Returns the empty append-only
    document ``{"version": 1, "runs": []}`` when the runtime has no history yet
    (a fresh runtime → the next appended run is seq 1)."""
    path = _resolve(name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"version": 1, "runs": []}


def append_audit(name: str, record: dict, dedup) -> int:
    """THE single append-only telemetry writer and sequence authority.

    Parameters
    ----------
    name    : one of :data:`AUDIT_LOGS` — the log to append to.
    record  : the run to record (WITHOUT ``seq``; the sequence is assigned here).
    dedup   : ``dedup(runs, record) -> int | None`` — the per-log no-op policy.
              It returns an existing ``seq`` to short-circuit (an idempotent
              re-run → no append, no write, so the log never grows and stays
              byte-stable under the drift gate), or ``None`` to append a new run.

    The monotonic ``seq`` is derived from the runtime log and assigned HERE and
    only here. A fresh runtime (empty log) starts at 1.
    """
    path = _resolve(name)
    doc = load_audit(name)
    runs = doc["runs"]
    short = dedup(runs, record)
    if short is not None:
        return short
    record["seq"] = (runs[-1]["seq"] + 1) if runs else 1
    runs.append(record)
    doc["generated_at"] = _now()
    _atomic_write(path, doc)
    return record["seq"]


def fingerprint_dedup(keys, *, mode_key: str | None = None):
    """Build the standard fingerprint no-op policy for :func:`append_audit`.

    A run whose ``keys`` fingerprint equals the most recent *comparable* run is a
    no-op (idempotent re-run → returns that run's ``seq``, no append). With
    ``mode_key`` set, "comparable" means the most recent run that shares the same
    ``record[mode_key]`` value (e.g. enforcement ``pre``/``post`` alternate every
    transaction and are de-duplicated per mode)."""
    keys = tuple(keys)

    def dedup(runs, record):
        prior = (
            [r for r in runs if r.get(mode_key) == record.get(mode_key)]
            if mode_key is not None
            else runs
        )
        if not prior:
            return None
        last = prior[-1]
        if {k: last.get(k) for k in keys} == {k: record.get(k) for k in keys}:
            return last["seq"]
        return None

    return dedup


def forbid_data_telemetry(path: str, data_dir: str) -> None:
    """Frozen-path guard invoked by every canonical-artifact JSON writer.

    Audit telemetry (``*-audit.json``) may NEVER be written under 00-BOOK/DATA.
    Any such target inside the tracked DATA tree is a hard :class:`TelemetryPathError`
    — so even a future edit that reconstructs an ``os.path.join(DATA_DIR, "…-audit.json")``
    write is rejected at runtime instead of silently reintroducing tracked,
    drift-producing telemetry. Canonical generated views (e.g. ``certification.json``)
    are unaffected because they are not ``*-audit.json`` logs."""
    base = os.path.basename(path)
    if not base.endswith("-audit.json"):
        return
    resolved = os.path.realpath(path)
    root = os.path.realpath(data_dir)
    if resolved == root or resolved.startswith(root + os.sep):
        raise TelemetryPathError(
            f"audit telemetry {base!r} may not be written under 00-BOOK/DATA "
            f"({resolved}); route it through governance_telemetry.append_audit "
            f"(→ {GOVERNANCE_DIR})"
        )


def _atomic_write(path: str, obj: dict) -> None:
    """Write ``obj`` as pretty JSON atomically (temp file + os.replace) so a
    concurrent reader never observes a half-written log."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)
