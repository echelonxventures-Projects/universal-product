"""
UCOS Ω∞ UKB Advancement — Connector base interface, append-only Signal ledger,
and deterministic dimension roll-up (UKB-001 / UKB-012).

Design (see 00-BOOK/ADVANCEMENT/UKB-ADV-001-REAL-TIME-CONNECTOR-ARCHITECTURE.md):

  * A Connector turns raw events from an authoritative source into append-only
    Signals keyed to a Universal Artifact ID. It is read-only against the source
    and write-only-append against the signal ledger. It never mutates canon.
  * The SignalLedger is append-only and idempotent: a replayed event with the
    same (connector, source_event_id) key is de-duplicated. A corrected upstream
    value arrives as a NEW signal with a later as_of; roll-up uses the latest.
  * roll-up is a pure function of the signal set + the artifact registry, so the
    twin state is deterministically reproducible (UKB-ADV-INV-07).

Standard library only. No secret is ever read, stored, or logged (RR-07).
"""

from __future__ import annotations

import datetime as _dt
import json
import os

SOURCES = {
    "MANUAL", "GITHUB", "GITHUB_ACTIONS", "JIRA", "SONARQUBE", "OWASP", "TRIVY",
    "PROMETHEUS", "GRAFANA", "OPENTELEMETRY", "KUBERNETES", "CLOUD",
    # UMB-REMED-002 (F-2 runtime authenticity): local Git working tree / commit
    # history is a LIVE, authoritative, credential-free source (no secret, RR-07).
    # Sources are pluggable (UMB-012 §4; AUTH-INF-001 CR-INF-003); this is an
    # append-only addition to the open source set — no existing source changed.
    "GIT",
    # EXEC-REG-001 (RUNTIME-006): the append-only execution register is a LIVE,
    # credential-free DOMAIN-C source. Append-only addition to the open source set.
    "EXECUTION",
}

DIMENSIONS = [
    "architecture", "implementation", "build", "unit_testing",
    "integration_testing", "functional_testing", "performance_testing",
    "security", "certification", "deployment", "production", "operational",
    # EXEC-REG-001 (RUNTIME-006) DOMAIN-C runtime dimension. Append-only; no
    # existing dimension is renamed or reordered.
    "release", "execution", "incident", "quality", "portfolio",
]

# Blocking-view order: least-advanced state with members wins (risk never hidden).
# Mirrors the foundation control-tower roll-up ordering.
STATE_ORDER = [
    "BLOCKED", "STALE", "NOT_STARTED", "PLANNED", "IN_PROGRESS", "UNDER_REVIEW",
    "APPROVED", "ACTIVE", "IMPLEMENTED", "COMPLETE", "TESTED", "CERTIFIED",
    "DEPLOYED", "PRODUCTION", "FROZEN", "FINAL",
]


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _load(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return default


def _dump(path, obj):
    if isinstance(obj, dict) and _stamp_eq_json(path, obj):
        return                                    # idempotent: only the stamp would change
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _stamp_eq_json(path, obj, stamp_keys=("generated_at",)):
    """True if `path` already holds JSON equal to `obj` once each document's own
    generation stamp (and any nested value equal to it) is neutralized, so a no-op
    flush does not rewrite the signal ledger with a fresh wall-clock stamp (F-1
    drift gate; UKB-ADV-INV-07 reproducibility)."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as fh:
            old = json.load(fh)
    except Exception:
        return False
    if not isinstance(old, dict):
        return old == obj
    # P0-BLOCKER-ERADICATION-001: neutralize against the UNION of both documents' stamps
    # (see the identical correction in ukb.py). Per-document neutralization erased a
    # content-derived timestamp on the OLD side whenever it equalled that document's own
    # generation stamp while preserving it on the NEW side, so substantively identical
    # registers compared unequal and were rewritten with only their stamp changed.
    stamps = _stamps_of(old, stamp_keys) | _stamps_of(obj, stamp_keys)
    return _neutralize_stamps(old, stamp_keys, stamps) == _neutralize_stamps(
        obj, stamp_keys, stamps
    )


def _stamps_of(doc, stamp_keys):
    stamps = set()
    if isinstance(doc, dict):
        for k in stamp_keys:
            v = doc.get(k)
            if v is not None:
                stamps.add(v)
    return stamps


def _neutralize_stamps(doc, stamp_keys, stamps=None):
    if stamps is None:
        stamps = _stamps_of(doc, stamp_keys)

    def walk(x):
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [walk(v) for v in x]
        if isinstance(x, str) and x in stamps:
            return "<STAMP>"
        return x

    return walk(doc)


# Trivial secret-pattern guard (SRC-08 / RR-07 defense). Rejects obvious secrets
# from ever entering a signal's evidence/metrics.
_SECRET_HINTS = ("password=", "secret=", "api_key=", "apikey=", "token=ghp_",
                 "-----BEGIN", "aws_secret_access_key")


def _secret_free(text: str) -> bool:
    low = str(text).lower()
    return not any(h in low for h in _SECRET_HINTS)


def make_signal(signal_id, subject_universal_id, dimension, state, source,
                *, subject_native_id=None, evidence=None, metrics=None,
                connector=None, ingest_run=None, as_of=None, **extra):
    """Build a schema-shaped Signal dict. Rejects secret-bearing evidence."""
    if dimension not in DIMENSIONS:
        raise ValueError(f"unknown dimension: {dimension}")
    if source not in SOURCES:
        raise ValueError(f"unknown source: {source}")
    if evidence is not None and not _secret_free(evidence):
        raise ValueError("evidence appears to contain a secret; rejected (RR-07)")
    sig = {
        "signal_id": signal_id,
        "subject_universal_id": subject_universal_id,
        "subject_native_id": subject_native_id,
        "dimension": dimension,
        "state": state,
        "source": source,
        "as_of": as_of or now_iso(),
        "evidence": evidence,
        "metrics": metrics or {},
        "connector": connector,
        "ingest_run": ingest_run,
    }
    sig.update(extra)
    return sig


class SignalLedger:
    """Append-only, idempotent signal store + per-connector cursor store."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.signals_path = os.path.join(data_dir, "signals.json")
        self.cursors_path = os.path.join(data_dir, "connector-cursors.json")
        self.doc = _load(self.signals_path, {
            "generated_at": None, "signal_seq": 0, "run_seq": 0,
            "seen_keys": [], "signals": [],
        })
        self.cursors = _load(self.cursors_path, {})
        self._seen = set(self.doc.get("seen_keys", []))

    # -- ids ---------------------------------------------------------------
    def next_signal_id(self) -> str:
        """Non-committing PREVIEW of the id a signal would receive.

        UMB-REMED-001 (F-4): the durable, gapless USIG id is allocated ONLY on a
        successful append() (commit-time allocation), never here. This preview
        does NOT advance ``signal_seq``, so a candidate signal that is later
        de-duplicated cannot inflate the counter and cannot open a gap in the
        append-only, gapless signal-id sequence. Multiple candidates in one run
        legitimately share this preview value; append() assigns each a distinct
        sequential id at commit. Kept for connector-interface compatibility."""
        return f"USIG-{self.doc['signal_seq'] + 1:09d}"

    def next_run_id(self) -> str:
        """Non-committing PREVIEW of the run id a connector run would receive.

        UMB-REMED-001 (F-4 / F-1 drift gate): mirrors ``next_signal_id``. The
        durable, gapless URUN run id is allocated ONLY by ``commit_run()`` after
        the run actually appends >=1 new signal (commit-time allocation), never
        here. This preview does NOT advance ``run_seq``, so a zero-new-signal
        (steady-state / CI) run consumes no run id and cannot mutate the guarded
        signals.json: with ``run_seq`` unchanged and no new signals, the flushed
        document neutralizes to the on-disk document (only the generation stamp
        differs) and ``_dump`` skips the rewrite, keeping the append-only signal
        ledger byte-identical under ``register.sh --guard`` and the determinism
        gate (IMP-007 §5 / UKB-ADV-INV-07). A run that stamps signals with this
        preview id then calls ``commit_run()`` before the next connector previews,
        so the committed id equals the preview and the URUN sequence stays gapless."""
        return f"URUN-{self.doc['run_seq'] + 1:09d}"

    def commit_run(self) -> str:
        """Commit-time allocation of a durable, gapless URUN run id.

        Called only when a connector run has appended >=1 new signal, so
        ``run_seq`` advances exactly once per signal-producing run and never on a
        no-op. Returns the id, which equals the ``next_run_id()`` preview taken
        at the start of that connector's pass (no intervening commit)."""
        self.doc["run_seq"] += 1
        return f"URUN-{self.doc['run_seq']:09d}"

    # -- append ------------------------------------------------------------
    def append(self, signal: dict, idempotency_key: str | None = None) -> bool:
        """Append a signal unless its idempotency key was already seen.
        Returns True if appended, False if de-duplicated.

        UMB-REMED-001 (F-4): the durable, gapless USIG signal id is allocated
        HERE — only after the dedup check passes and the signal is committed to
        the ledger. This makes id allocation idempotent under connector replay:
        a de-duplicated candidate returns before any counter movement, so
        ``signal_seq`` stays exactly equal to the number of stored signals and
        the ``signal_ids_unique`` (unique + gapless) invariant holds by
        construction. Any preview id set by ``next_signal_id()`` is overwritten."""
        if idempotency_key is not None:
            if idempotency_key in self._seen:
                return False
            self._seen.add(idempotency_key)
            self.doc["seen_keys"].append(idempotency_key)
        self.doc["signal_seq"] += 1
        signal["signal_id"] = f"USIG-{self.doc['signal_seq']:09d}"
        self.doc["signals"].append(signal)
        return True

    def set_cursor(self, connector_name: str, high_water) -> None:
        self.cursors[connector_name] = high_water

    def get_cursor(self, connector_name: str):
        return self.cursors.get(connector_name)

    def flush(self) -> None:
        self.doc["generated_at"] = now_iso()
        _dump(self.signals_path, self.doc)
        _dump(self.cursors_path, self.cursors)

    @property
    def signals(self):
        return self.doc["signals"]


class Connector:
    """Base connector interface. Subclasses implement fetch/normalize/resolve.

    Contract:
      name        stable id
      sources     [SOURCE]
      dimensions  [dimension]
      mode        'EVENT' | 'POLL_INCREMENTAL'
      fetch(since)      -> iterable of raw events strictly newer than `since`
      normalize(ev, ctx)-> iterable of Signal dicts (pure/deterministic)
      resolve(ev, ctx)  -> subject_universal_id (never guesses identity)
    """

    name = "abstract"
    sources: list[str] = []
    dimensions: list[str] = []
    mode = "POLL_INCREMENTAL"

    def cursor(self, ledger: SignalLedger):
        return ledger.get_cursor(self.name)

    def fetch(self, since):
        raise NotImplementedError

    def resolve(self, ev, ctx) -> str | None:
        """Default subject resolution: explicit id -> native id -> path hint.
        ctx must provide by_uid (set), by_native (dict), paths (list of (path,uid)),
        and fallback_uid. Never fabricates identity (UKB-ADV-INV-05)."""
        uid = ev.get("subject_universal_id")
        if uid and uid in ctx["by_uid"]:
            return uid
        nat = ev.get("native_id")
        if nat and nat in ctx["by_native"]:
            return ctx["by_native"][nat]
        hint = ev.get("path_hint")
        if hint:
            for path, puid in ctx["paths"]:
                if hint in path:
                    return puid
        return ctx.get("fallback_uid")

    def normalize(self, ev, ctx):
        raise NotImplementedError

    def high_water(self, events):
        """Compute the new cursor from consumed events (max as_of/seq)."""
        vals = [e.get("as_of") or e.get("seq") for e in events if e.get("as_of") or e.get("seq")]
        return max(vals) if vals else None



# ---------------------------------------------------------------------------
# deterministic roll-up (UKB-012): signals -> per-subject + per-dimension state
# ---------------------------------------------------------------------------
def _latest_per(signals, keyfn):
    """Return the latest signal per key (by as_of, then signal_id)."""
    latest = {}
    for s in signals:
        k = keyfn(s)
        cur = latest.get(k)
        if cur is None or (s.get("as_of", ""), s.get("signal_id", "")) >= (
                cur.get("as_of", ""), cur.get("signal_id", "")):
            latest[k] = s
    return latest


def _blocking(states):
    """Blocking-view reduction: least-advanced present state wins."""
    present = [s for s in STATE_ORDER if s in states]
    return present[0] if present else "NOT_STARTED"


def _active_overrides(signals):
    """Return signal_ids that are superseded by a still-valid governed override."""
    superseded = set()
    for s in signals:
        if s.get("override") and s.get("supersedes_signal"):
            exp = s.get("expires")
            if not exp or exp >= now_iso():
                superseded.add(s["supersedes_signal"])
    return superseded


def rollup_dimensions(signals):
    """Pure function: signal list -> {subjects, dimensions}.

    subjects[subject][dimension] = latest {state, source, as_of, evidence, signal_id}
    dimensions[dimension]        = {status, sources, as_of} (blocking-view roll-up)
    Governed overrides (UKB-ADV-OVR) that are unexpired supersede their target.
    """
    superseded = _active_overrides(signals)
    live = [s for s in signals if s.get("signal_id") not in superseded]

    # latest per (subject, dimension, source) then per (subject, dimension)
    per_sds = _latest_per(
        live, lambda s: (s["subject_universal_id"], s["dimension"], s["source"]))
    subjects = {}
    dim_states = {}
    dim_sources = {}
    dim_asof = {}
    for (subj, dim, _src), s in per_sds.items():
        subjects.setdefault(subj, {})
        cur = subjects[subj].get(dim)
        if cur is None or (s["as_of"], s["signal_id"]) >= (cur["as_of"], cur["signal_id"]):
            subjects[subj][dim] = {
                "state": s["state"], "source": s["source"], "as_of": s["as_of"],
                "evidence": s.get("evidence"), "signal_id": s["signal_id"],
            }
        dim_states.setdefault(dim, []).append(s["state"])
        dim_sources.setdefault(dim, set()).add(s["source"])
        dim_asof[dim] = max(dim_asof.get(dim, ""), s["as_of"])

    dimensions = {}
    for dim, states in dim_states.items():
        dimensions[dim] = {
            "status": _blocking(states),
            "signal_source": sorted(dim_sources[dim])[0] if len(dim_sources[dim]) == 1
            else "+".join(sorted(dim_sources[dim])),
            "as_of": dim_asof[dim],
        }
    return {"subjects": subjects, "dimensions": dimensions}
