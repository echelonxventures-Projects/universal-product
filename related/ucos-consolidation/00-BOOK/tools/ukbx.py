#!/usr/bin/env python3
"""
UCOS Ω∞ — UKB Advancement Engine (Digital Twin).

Sibling of the foundation engine (00-BOOK/tools/ukb.py). It DOES NOT modify or
import ukb.py's write paths; it only READS the foundation DATA (artifacts,
volumes, relationships, control-tower) and WRITES new append-only overlay data
(signals, cursors, twin) plus generated views (portal, exports). It creates no
authority (UKB-ADV-INV-08) and preserves foundation integrity (UKB-ADV-INV-01).

Commands:
    ingest    Run connectors (offline replay by default), append Signals.
    twin      Recompute the Digital Twin roll-up; refresh control tower;
              `--check` runs Digital-Twin Certification (UKB-014).
    export    Dynamic publication: /export <scope> <selector> <format>.
    portal    Generate the navigation portal under 00-BOOK/PORTAL/.
    search    Faceted + graph-aware + status-aware search.
    ai        Grounded, cited retrieval (explain/trace/impact/change).
    validate  Twin-specific validation (signals, provenance, secrets).

Standard library only. See 00-BOOK/ADVANCEMENT/UKB-ADV-000…019.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(BOOK_DIR)
DATA_DIR = os.path.join(BOOK_DIR, "DATA")
REG_DIR = os.path.join(BOOK_DIR, "REGISTRIES")
CT_DIR = os.path.join(BOOK_DIR, "CONTROL-TOWER")
PORTAL_DIR = os.path.join(BOOK_DIR, "PORTAL")

sys.path.insert(0, HERE)
import config as C  # noqa: E402
import governance_telemetry as T  # noqa: E402  (the one runtime-telemetry authority)
from connectors import base as B  # noqa: E402
from connectors import REGISTRY, discover  # noqa: E402
# UMB-IMP-004: Live Source Discovery. Dynamically discover every connector in the
# connectors package (their @register decorators run on import), instead of a
# hard-coded import list — so a new connector is a new file, not a core edit
# (AUTH-INF-001 CR-INF-003/010; no hard-coded connector list, infinite expansion).
_CONNECTOR_NAMES, _CONNECTOR_FAILURES = discover()

GEN_VERSION = "1.0.0-adv"


def _now():
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _load(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return default


def _dump(path, obj):
    # Frozen-path invariant (EC3 Phase-3): audit telemetry may never be written
    # under 00-BOOK/DATA — it belongs only in .runtime/governance/ via
    # governance_telemetry.append_audit.
    T.forbid_data_telemetry(path, DATA_DIR)
    if _stamp_eq_json(path, obj):
        return                                    # idempotent: only the stamp would change
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _stamp_eq_json(path, obj, stamp_keys=("generated_at",)):
    """True if `path` already holds JSON equal to `obj` once each document's own
    generation stamp (and any nested value equal to it) is neutralized — lets
    writers skip no-op rewrites so regeneration is byte-stable (register.sh
    --guard drift gate, F-1; UKB-ADV-INV-07 reproducibility)."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as fh:
            old = json.load(fh)
    except Exception:
        return False
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


def _artifacts():
    d = _load(os.path.join(DATA_DIR, "artifacts.json"), None)
    if not d:
        sys.exit("No artifacts.json — run `python3 00-BOOK/tools/ukb.py build` first.")
    return d["artifacts"]


def _relationships():
    return _load(os.path.join(DATA_DIR, "relationships.json"), {"relationships": []})["relationships"]


def _resolution_ctx(arts):
    by_uid = {a["universal_id"] for a in arts}
    by_native = {a["native_id"]: a["universal_id"] for a in arts if a.get("native_id")}
    paths = [(a["path"], a["universal_id"]) for a in arts]
    fallback = by_native.get("UKB-ADV-000") or "UCOS-BOOK-000000"
    return {"by_uid": by_uid, "by_native": by_native, "paths": paths,
            "fallback_uid": fallback}


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------
def cmd_ingest(args):
    arts = _artifacts()
    ctx = _resolution_ctx(arts)
    ledger = B.SignalLedger(DATA_DIR)

    names = [args.connector] if args.connector else sorted(REGISTRY.keys())
    total_new, total_dup, unresolved = 0, 0, 0
    for name in names:
        conn = REGISTRY[name]()
        run_id = ledger.next_run_id()
        since = conn.cursor(ledger)
        events = list(conn.fetch(since))
        nctx = {"next_signal_id": ledger.next_signal_id, "ingest_run": run_id,
                **ctx}
        consumed = []
        conn_new = 0
        for ev in events:
            key = f"{name}|{ev.get('source_event_id')}"
            sigs = list(conn.normalize(ev, nctx))
            appended_any = False
            for i, sig in enumerate(sigs):
                if sig["subject_universal_id"] == ctx["fallback_uid"] and \
                        not ev.get("subject_universal_id") and not ev.get("native_id") \
                        and not any(ev.get("path_hint", "") in p for p, _ in ctx["paths"]):
                    unresolved += 1
                ok = ledger.append(sig, idempotency_key=f"{key}#{i}")
                if ok:
                    total_new += 1
                    conn_new += 1
                    appended_any = True
                else:
                    total_dup += 1
            if appended_any:
                consumed.append(ev)
        # Commit-time URUN allocation (UMB-REMED-001 F-4 / F-1 drift gate): advance
        # run_seq only when this connector actually appended a new signal, so a
        # no-op ingest leaves signals.json byte-identical. Committed id equals the
        # run_id preview taken above (no intervening commit) — URUN stays gapless.
        if conn_new:
            ledger.commit_run()
        hw = conn.high_water(events)
        if hw:
            ledger.set_cursor(name, hw)
        print(f"  {name:16s} events={len(events):3d} new_signals={total_new:3d} "
              f"cursor={hw}")
    ledger.flush()
    print(f"ingest complete: +{total_new} signals, {total_dup} de-duplicated, "
          f"{unresolved} unresolved-subject. Ledger: {B.SignalLedger(DATA_DIR).doc['signal_seq']} total.")


# ---------------------------------------------------------------------------
# UMB-IMP-004 — SYNCHRONIZATION RUNTIME (schedule · execute · verify · audit ·
# recover). Wraps the existing connector layer + append-only Signal ledger into
# an audited, verifiable, recoverable, schedulable State-Synchronization run
# (UMB-012 §2 State surface, §3 pipeline). Reuses cmd_ingest's proven append
# path; adds per-connector RECOVERY isolation, VERIFICATION gates, cadence
# SCHEDULING, and an append-only sync AUDIT log. Creates no new store or engine.
# ---------------------------------------------------------------------------
def _sync_audit_append(record):
    """Record a sync-run outcome in the append-only runtime audit log via the
    single telemetry authority (``.runtime/governance/sync-audit.json``).

    A consecutive run with an identical fingerprint that added no new signals is a
    no-op; a zero-work run (no connector due, nothing changed, PASS, nothing
    recovered) is also a no-op — so idempotent CI/steady-state re-runs never grow
    the log (drift-free under register.sh --guard). Operational telemetry."""
    fp_keys = ("result", "connectors_run", "new_signals", "recovered", "verify")

    def dedup(runs, rec):
        if runs:
            last = runs[-1]
            if ({k: last.get(k) for k in fp_keys} == {k: rec.get(k) for k in fp_keys}
                    and rec.get("new_signals") == 0):
                return last["seq"]                # unchanged no-op — no append
        # A run in which no connector was due and nothing changed is a pure no-op
        # (steady-state / CI re-run); do not grow the append-only log with empty
        # runs, so a no-op transaction is byte-stable under the drift gate (F-1).
        if (rec.get("connectors_run") == 0 and rec.get("new_signals") == 0
                and rec.get("result") == "PASS" and not rec.get("recovered")):
            return runs[-1]["seq"] if runs else 0
        return None

    return T.append_audit(T.SYNC_AUDIT, record, dedup)


def _sync_last_runs():
    """Return {connector_name: last_success_iso} from the sync-audit log, for
    cadence scheduling (`--due`). Empty if never run."""
    doc = T.load_audit(T.SYNC_AUDIT)
    last = {}
    for run in doc.get("runs", []):
        for c in run.get("per_connector", []):
            if c.get("status") == "OK":
                last[c["connector"]] = max(last.get(c["connector"], ""), run.get("at", ""))
    return last


def _is_due(name, cadence, last_runs, now_dt):
    """True if the connector has never run OK or its cadence has elapsed."""
    last = last_runs.get(name)
    if not last:
        return True
    try:
        prev = _dt.datetime.fromisoformat(last.replace("Z", "+00:00"))
        return (now_dt - prev).total_seconds() >= cadence
    except Exception:
        return True


def _verify_sync(new_signals, cursors_before, cursors_after, ctx, ledger):
    """Synchronization Verification (UMB-012 §3). Assert the hard gates over the
    signals appended THIS run + cursor movement. Returns (ok, {gate: detail})."""
    gates = {}
    by_uid = ctx["by_uid"]
    # subject_resolves + provenance + secret_free over new signals
    unresolved = [s["signal_id"] for s in new_signals if s["subject_universal_id"] not in by_uid]
    no_prov = [s["signal_id"] for s in new_signals if not s.get("source") or not s.get("as_of")]
    secretful = [s["signal_id"] for s in new_signals
                 if s.get("evidence") and not B._secret_free(s["evidence"])]
    gates["subject_resolves"] = {"pass": not unresolved, "detail": unresolved[:5] or "all resolve"}
    gates["provenance_present"] = {"pass": not no_prov, "detail": no_prov[:5] or "all carry source+as_of"}
    gates["secret_free"] = {"pass": not secretful, "detail": secretful[:5] or "no secrets in evidence"}
    # cursor_monotonic: no connector cursor regressed
    regressed = [n for n, after in cursors_after.items()
                 if cursors_before.get(n) is not None and after is not None
                 and str(after) < str(cursors_before.get(n))]
    gates["cursor_monotonic"] = {"pass": not regressed, "detail": regressed[:5] or "cursors non-decreasing"}
    # signal_ids_unique + gapless over the WHOLE ledger (append-only invariant)
    ids = [s["signal_id"] for s in ledger.signals]
    dup = len(ids) != len(set(ids))
    seqs = sorted(int(i.split("-")[1]) for i in ids) if ids else []
    gapless = seqs == list(range(1, len(seqs) + 1)) if seqs else True
    gates["signal_ids_unique"] = {"pass": (not dup) and gapless,
                                  "detail": "unique+gapless" if (not dup and gapless) else "dup/gap detected"}
    # advisory: non-fallback subject resolution
    fb = ctx.get("fallback_uid")
    fallback_bound = [s["signal_id"] for s in new_signals
                      if s["subject_universal_id"] == fb and s.get("connector")]
    gates["subject_resolved_nonfallback"] = {"pass": not fallback_bound,
                                             "detail": f"{len(fallback_bound)} fallback-bound (advisory)",
                                             "advisory": True}
    hard = [g for g in C.SYNC_VERIFY_HARD_GATES]
    ok = all(gates[g]["pass"] for g in hard)
    return ok, gates


def cmd_sync(args):
    """Auto-Synchronization run: discover → monitor → detect → execute → verify →
    audit → recover, then recompute the twin + control tower (UMB-012)."""
    arts = _artifacts()
    ctx = _resolution_ctx(arts)
    ledger = B.SignalLedger(DATA_DIR)

    # --- Stage 1: Live Source Discovery (dynamic; no hard-coded list) --------
    discovered = sorted(REGISTRY.keys())
    if _CONNECTOR_FAILURES:
        for name, err in _CONNECTOR_FAILURES:
            print(f"  discovery: connector '{name}' failed to import and was isolated ({err})")
    print(f"-- sync: discovered {len(discovered)} connector(s): {', '.join(discovered)}")

    if args.schedule:
        last_runs = _sync_last_runs()
        now_dt = _dt.datetime.now(_dt.timezone.utc)
        print("-- sync schedule (cadence-driven; no connector list is compiled in):")
        for name in discovered:
            conn = REGISTRY[name]()
            cad = getattr(conn, "cadence_seconds", C.SYNC_DEFAULT_CADENCE_SECONDS)
            due = _is_due(name, cad, last_runs, now_dt)
            print(f"    {name:16s} cadence={cad}s last={last_runs.get(name) or '—':25s} "
                  f"{'DUE' if due else 'not-due'}")
        return

    # --- Stage 4: which connectors to run (scheduling) -----------------------
    if args.connector:
        run_names = [args.connector] if args.connector in REGISTRY else []
        if not run_names:
            sys.exit(f"unknown connector: {args.connector} (discovered: {', '.join(discovered)})")
    elif args.due:
        last_runs = _sync_last_runs()
        now_dt = _dt.datetime.now(_dt.timezone.utc)
        run_names = [n for n in discovered
                     if _is_due(n, getattr(REGISTRY[n](), "cadence_seconds",
                                           C.SYNC_DEFAULT_CADENCE_SECONDS), last_runs, now_dt)]
    else:
        run_names = discovered

    cursors_before = dict(ledger.cursors)
    sig_before = len(ledger.signals)
    per_connector, recovered = [], []
    total_new = total_dup = 0

    for name in run_names:
        cb = ledger.get_cursor(name)
        try:                                     # --- per-connector RECOVERY isolation
            conn = REGISTRY[name]()
            run_id = ledger.next_run_id()
            since = conn.cursor(ledger)
            events = list(conn.fetch(since))
            nctx = {"next_signal_id": ledger.next_signal_id, "ingest_run": run_id, **ctx}
            cnew = cdup = 0
            for ev in events:                    # Stage 2/3: monitor + change detection
                key = f"{name}|{ev.get('source_event_id')}"
                for i, sig in enumerate(conn.normalize(ev, nctx)):   # Stage: execute
                    if ledger.append(sig, idempotency_key=f"{key}#{i}"):
                        cnew += 1; total_new += 1
                    else:
                        cdup += 1; total_dup += 1
            # Commit-time URUN allocation (UMB-REMED-001 F-4 / F-1 drift gate):
            # advance run_seq only when this pass actually produced a new signal,
            # so a zero-new-signal run leaves signals.json byte-identical. The
            # committed id equals the run_id preview taken above (no intervening
            # commit), keeping the URUN sequence gapless and the stamped
            # ingest_run values consistent.
            if cnew:
                ledger.commit_run()
            hw = conn.high_water(events)
            # cursor advances only forward (monotonic) — never regress on replay
            if hw and (cb is None or str(hw) >= str(cb)):
                ledger.set_cursor(name, hw)
            per_connector.append({"connector": name, "status": "OK", "events": len(events),
                                  "new_signals": cnew, "duplicates": cdup,
                                  "cursor_before": cb, "cursor_after": ledger.get_cursor(name)})
            print(f"  {name:16s} events={len(events):3d} new={cnew:3d} dup={cdup:3d} "
                  f"cursor={ledger.get_cursor(name)}  [OK]")
        except Exception as exc:                 # isolate + preserve cursor for resume
            per_connector.append({"connector": name, "status": "RECOVERED",
                                  "error": f"{type(exc).__name__}: {exc}",
                                  "cursor_before": cb, "cursor_after": cb})
            recovered.append(name)
            print(f"  {name:16s} FAILED, isolated — cursor preserved at {cb} for resume "
                  f"[RECOVERED] ({type(exc).__name__}: {exc})")

    ledger.flush()
    cursors_after = dict(ledger.cursors)
    new_signals = ledger.signals[sig_before:]

    # --- Stage 5: Synchronization Verification -------------------------------
    verify_ok, gates = _verify_sync(new_signals, cursors_before, cursors_after, ctx, ledger)

    # --- Propagate to the twin + control tower (state synchronization) -------
    twin, _ = _compute_twin()
    _dump(os.path.join(DATA_DIR, "twin.json"), twin)
    _refresh_control_tower(twin)

    # --- Stage 6: append-only AUDIT ------------------------------------------
    result = "PASS" if verify_ok else "FAIL"
    record = {
        "at": _now(), "generator_version": GEN_VERSION,
        "stages": list(C.SYNC_STAGES),
        "discovered": discovered, "discovery_failures": _CONNECTOR_FAILURES,
        "connectors_run": len(run_names), "per_connector": per_connector,
        "new_signals": total_new, "duplicates": total_dup,
        "recovered": recovered,
        "verify": {g: gates[g]["pass"] for g in gates},
        "result": result,
        "ledger_signal_total": ledger.doc["signal_seq"],
    }
    seq = _sync_audit_append(record)

    print("-" * 60)
    print(f"UMB-IMP-004 Synchronization Run  (audit run #{seq})")
    print(f"  connectors run   : {len(run_names)}   recovered/isolated: {len(recovered)}")
    print(f"  new signals      : +{total_new}   de-duplicated: {total_dup}")
    print(f"  ledger total     : {ledger.doc['signal_seq']} signals")
    print("  verification gates:")
    for g, v in gates.items():
        tag = "advisory" if v.get("advisory") else ("PASS" if v["pass"] else "FAIL")
        detail = v["detail"] if isinstance(v["detail"], str) else ", ".join(v["detail"])
        print(f"    [{tag:8s}] {g:26s} {detail}")
    print("-" * 60)
    if not verify_ok:
        print("SYNCHRONIZATION FAILED verification — run recorded; state not certified.")
        sys.exit(1)
    print(f"SYNCHRONIZATION VERIFIED — {total_new} new signals audited; "
          f"{len(recovered)} connector(s) recovered; twin + control tower refreshed.")


# ---------------------------------------------------------------------------
# twin roll-up + control tower automation
# ---------------------------------------------------------------------------
def _compute_twin():
    ledger = B.SignalLedger(DATA_DIR)
    roll = B.rollup_dimensions(ledger.signals)
    twin = {
        "generated_at": _now(),
        "generator_version": GEN_VERSION,
        "signal_count": len(ledger.signals),
        "subject_count": len(roll["subjects"]),
        "dimensions": roll["dimensions"],
        "subjects": roll["subjects"],
    }
    return twin, ledger


def _refresh_control_tower(twin):
    ct_path = os.path.join(DATA_DIR, "control-tower.json")
    ct = _load(ct_path, None)
    if not ct:
        return None
    now = _now()
    for dim, comp in twin["dimensions"].items():
        if dim in ct["dimensions"]:
            ct["dimensions"][dim]["status"] = comp["status"]
            ct["dimensions"][dim]["signal_source"] = comp["signal_source"]
            ct["dimensions"][dim]["as_of"] = comp["as_of"]
            ct["dimensions"][dim]["note"] = "Automated: computed from the append-only signal ledger (UKB-012)."
    # Manual-baseline dimensions (no signal this run) carry only a generation
    # stamp, not real event time; align them to the single generation clock so a
    # no-op refresh neutralizes as one stamp and stays byte-stable (F-1 drift gate).
    for dim, comp in ct["dimensions"].items():
        if dim not in twin["dimensions"]:
            comp["as_of"] = now
    ct["generated_at"] = now
    _dump(ct_path, ct)
    return ct


def cmd_twin(args):
    if args.check is not None:
        return _cmd_certify(args)
    twin, _ = _compute_twin()
    _dump(os.path.join(DATA_DIR, "twin.json"), twin)
    ct = _refresh_control_tower(twin)
    print(f"twin recomputed: {twin['signal_count']} signals over "
          f"{twin['subject_count']} subjects, {len(twin['dimensions'])} dimensions.")
    for dim, d in sorted(twin["dimensions"].items()):
        print(f"  {dim:20s} {d['status']:12s} [{d['signal_source']}] {d['as_of']}")
    if ct:
        print(f"control tower refreshed (signal_source automated for "
              f"{len(twin['dimensions'])} dimensions).")


# ---------------------------------------------------------------------------
# certification (UKB-014)
# ---------------------------------------------------------------------------
def _cmd_certify(args):
    arts = _artifacts()
    by_uid = {a["universal_id"]: a for a in arts}
    rels = _relationships()
    twin, ledger = _compute_twin()
    results, evidence = {}, {}

    # C-04/C-12 signals + provenance + secret-free
    bad_sig = []
    for s in ledger.signals:
        if s["subject_universal_id"] not in by_uid:
            bad_sig.append(f"{s['signal_id']} unknown subject {s['subject_universal_id']}")
        if not s.get("source") or not s.get("as_of"):
            bad_sig.append(f"{s['signal_id']} missing provenance")
        if s.get("evidence") and not B._secret_free(s["evidence"]):
            bad_sig.append(f"{s['signal_id']} secret in evidence")
    results["C-04/12 signals+provenance"] = not bad_sig
    evidence["C-04/12 signals+provenance"] = bad_sig[:5] or f"{len(ledger.signals)} signals clean"

    # C-05 referential integrity (parents/deps/edges)
    ref = []
    for a in arts:
        if a["parent"] and a["parent"] not in by_uid:
            ref.append(f"{a['universal_id']} parent {a['parent']} unknown")
        for d in a["dependencies"]:
            if d not in by_uid:
                ref.append(f"{a['universal_id']} dep {d} unknown")
    for e in rels:
        if e["from"] not in by_uid or e["to"] not in by_uid:
            ref.append(f"{e['edge_id']} dangling endpoint")
    results["C-05 referential"] = not ref
    evidence["C-05 referential"] = ref[:5] or "all endpoints resolve"

    # C-07 graph: Depends-On acyclic
    dep = defaultdict(list)
    for a in arts:
        for d in a["dependencies"]:
            dep[a["universal_id"]].append(d)
    cyc = _has_cycle(dep)
    results["C-07 graph acyclic"] = not cyc
    evidence["C-07 graph acyclic"] = "acyclic" if not cyc else f"cycle via {cyc}"

    # C-08 navigation: every artifact reachable from BOOK root + has return path
    root = "UCOS-BOOK-000000"
    orphans = [a["universal_id"] for a in arts
               if a["universal_id"] != root and not a["parent"]]
    unreachable = _unreachable_from_root(arts, root)
    results["C-08 navigation"] = not orphans and not unreachable
    evidence["C-08 navigation"] = (orphans[:5] + unreachable[:5]) or "all reachable + return path"

    # C-06 coverage (advisory): report artifacts with any testing signal
    tested = {s["subject_universal_id"] for s in ledger.signals
              if s["dimension"].endswith("testing") or s["dimension"] == "unit_testing"}
    results["C-06 coverage (advisory)"] = True
    evidence["C-06 coverage (advisory)"] = f"{len(tested)} subjects carry testing signals"

    # C-09 control-tower integrity: no ungoverned MANUAL among computed dims
    ct = _load(os.path.join(DATA_DIR, "control-tower.json"), {"dimensions": {}})
    manual = [d for d, v in ct["dimensions"].items()
              if v.get("signal_source") == "MANUAL" and d in twin["dimensions"]]
    results["C-09 control-tower"] = not manual
    evidence["C-09 control-tower"] = manual[:5] or "computed dimensions automated"

    # C-10 export + C-11 search smoke
    exp_ok = bool(_resolve_scope(arts, "PROGRAM", "ADV"))
    results["C-10 export"] = exp_ok
    evidence["C-10 export"] = "PROGRAM/ADV export non-empty" if exp_ok else "export empty"
    srch = _search(arts, twin, keyword="architecture")
    results["C-11 search"] = bool(srch)
    evidence["C-11 search"] = f"{len(srch)} hits for 'architecture'"

    # C-02 completeness (advisory): unresolved-subject signals
    fallback = _resolution_ctx(arts)["fallback_uid"]
    unresolved = [s["signal_id"] for s in ledger.signals
                  if s["subject_universal_id"] == fallback and s.get("connector")]
    results["C-02 completeness (advisory)"] = True
    evidence["C-02 completeness (advisory)"] = f"{len(unresolved)} unresolved-subject signals"

    # C-03 trace (advisory): every subject with signals has a parent (in-graph)
    subj_no_parent = [s for s in twin["subjects"]
                      if s in by_uid and not by_uid[s]["parent"] and s != root]
    results["C-03 trace (advisory)"] = not subj_no_parent
    evidence["C-03 trace (advisory)"] = subj_no_parent[:5] or "all signal subjects in-graph"

    hard = [k for k in results if "advisory" not in k]
    passed = all(results[k] for k in hard)
    print("UCOS Ω∞ Digital-Twin Certification (UKB-014)\n" + "-" * 52)
    for k in sorted(results):
        mark = "PASS" if results[k] else "FAIL"
        print(f"  [{mark}] {k}")
        if isinstance(evidence[k], list) and evidence[k]:
            for line in evidence[k]:
                print(f"          - {line}")
        else:
            print(f"          {evidence[k]}")
    verdict = "CERTIFIED" if passed else "NOT-CERTIFIED"
    print("-" * 52 + f"\nRESULT: {verdict} "
          f"(hard checks {sum(results[k] for k in hard)}/{len(hard)})")
    if not passed:
        sys.exit(1)


def _has_cycle(dep):
    WHITE, GREY, BLACK = 0, 1, 2
    color = defaultdict(int)

    def dfs(u):
        color[u] = GREY
        for v in dep.get(u, []):
            if color[v] == GREY:
                return u
            if color[v] == WHITE:
                r = dfs(v)
                if r:
                    return r
        color[u] = BLACK
        return None

    for n in list(dep.keys()):
        if color[n] == WHITE:
            r = dfs(n)
            if r:
                return r
    return None


def _unreachable_from_root(arts, root):
    children = defaultdict(list)
    for a in arts:
        if a["parent"]:
            children[a["parent"]].append(a["universal_id"])
    seen = set()
    stack = [root]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(children.get(n, []))
    return [a["universal_id"] for a in arts if a["universal_id"] not in seen]


# ---------------------------------------------------------------------------
# export (UKB-009)
# ---------------------------------------------------------------------------
def _resolve_scope(arts, scope, selector):
    scope = scope.upper()
    sel = (selector or "").lower()
    if scope == "ARTIFACT":
        return [a for a in arts if selector in (a["universal_id"], a.get("native_id"))]
    if scope == "VOLUME":
        return [a for a in arts if a["volume"].lower() == sel or sel in a["volume"].lower()]
    if scope == "PROGRAM":
        return [a for a in arts if a["program"].upper() == selector.upper()]
    # FEATURE / MODULE / *_PACKAGE / USER_GUIDE / TRACEABILITY_CHAIN → keyword match
    return [a for a in arts if sel in " ".join(
        [a["universal_id"], a["name"], a.get("native_id") or "", a["program"],
         " ".join(a["tags"]), a["path"]]).lower()]


def _twin_status(twin, uid):
    dims = twin.get("subjects", {}).get(uid, {})
    return {d: v["state"] for d, v in dims.items()}


def cmd_export(args):
    arts = _artifacts()
    twin = _load(os.path.join(DATA_DIR, "twin.json"), {"subjects": {}})
    hits = _resolve_scope(arts, args.scope, args.selector)
    fmt = args.format.upper()
    as_of = _now()
    if not hits:
        print(f"(no artifacts for scope {args.scope}='{args.selector}')")
        return
    if fmt == "JSON":
        out = {"export": {"scope": args.scope, "selector": args.selector,
                          "format": "JSON", "as_of": as_of,
                          "included_ids": [a["universal_id"] for a in hits]},
               "artifacts": [{**a, "twin_status": _twin_status(twin, a["universal_id"])}
                             for a in hits]}
        text = json.dumps(out, ensure_ascii=False, indent=2)
    else:  # MARKDOWN (and the intermediate model for HTML/PDF/DOCX adapters)
        lines = [f"# UCOS Ω∞ Export — {args.scope}: {args.selector}", "",
                 f"*Generated dynamically {as_of} from authoritative data "
                 f"(UKB-ADV-INV-06). {len(hits)} artifact(s).*", "",
                 "| Universal ID | Name | Native | Volume | Status | Twin status |",
                 "|--------------|------|--------|--------|--------|-------------|"]
        for a in sorted(hits, key=lambda x: x["page_start"]):
            ts = ", ".join(f"{k}={v}" for k, v in _twin_status(twin, a["universal_id"]).items()) or "—"
            nm = a["name"].replace("|", "/")[:60]
            lines.append(f"| `{a['universal_id']}` | {nm} | {a.get('native_id') or '—'} "
                         f"| {a['volume']} | {a['status']} | {ts} |")
        lines += ["", f"*Provenance: {len(hits)} ids; twin as_of {twin.get('generated_at','—')}.*"]
        text = "\n".join(lines)
        if fmt not in ("MARKDOWN", "HTML", "PDF", "DOCX"):
            pass
        if fmt in ("HTML", "PDF", "DOCX"):
            text = (f"<!-- {fmt} adapter renders this intermediate Markdown model; "
                    f"install the {fmt} renderer to emit binary output. -->\n\n" + text)
    if args.out:
        _dump_text(args.out, text)
        print(f"export written: {args.out} ({len(hits)} artifacts, {fmt})")
    else:
        print(text)


def _dump_text(path, text):
    if _stamp_eq_text(path, text):
        return                                    # idempotent: only the stamp would change
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")


def _stamp_eq_text(path, text, markers=("**Generated:**", "*Generated ")):
    """True if `path` already holds text equal to `text + \\n` ignoring only lines
    beginning with a volatile generation-stamp marker (F-1 drift gate)."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as fh:
            old = fh.read()
    except Exception:
        return False
    strip = lambda s: "\n".join(
        ln for ln in s.splitlines()
        if not any(ln.lstrip().startswith(m) for m in markers))
    return strip(old) == strip(text + "\n")


# ---------------------------------------------------------------------------
# search (UKB-011)
# ---------------------------------------------------------------------------
def _search(arts, twin, *, keyword=None, uid=None, volume=None, program=None,
            status=None, dependency=None, relationship=None, rels=None):
    out = []
    for a in arts:
        if uid and uid.lower() not in a["universal_id"].lower():
            continue
        if volume and volume.upper() not in a["volume"]:
            continue
        if program and program.upper() != a["program"].upper():
            continue
        if dependency and dependency not in a["dependencies"]:
            continue
        if status:
            tw = _twin_status(twin, a["universal_id"])
            if status.upper() not in [v.upper() for v in tw.values()] and status.upper() != a["status"].upper():
                continue
        if keyword:
            hay = " ".join([a["universal_id"], a["name"], a.get("native_id") or "",
                            a["program"], a["volume"], " ".join(a["tags"]), a["path"]]).lower()
            if keyword.lower() not in hay:
                continue
        out.append(a)
    if relationship and rels is not None:
        keep = {e["from"] for e in rels if e["type"].lower() == relationship.lower()}
        keep |= {e["to"] for e in rels if e["type"].lower() == relationship.lower()}
        out = [a for a in out if a["universal_id"] in keep]
    return out


def cmd_search(args):
    arts = _artifacts()
    twin = _load(os.path.join(DATA_DIR, "twin.json"), {"subjects": {}})
    rels = _relationships()
    hits = _search(arts, twin, keyword=args.query, uid=args.id, volume=args.volume,
                   program=args.program, status=args.status, dependency=args.dependency,
                   relationship=args.relationship, rels=rels)
    for a in hits[: args.limit]:
        tw = ", ".join(f"{k}={v}" for k, v in _twin_status(twin, a["universal_id"]).items())
        print(f"{a['universal_id']}  [{a['volume']}]  {a['name']}")
        print(f"    native={a.get('native_id') or '—'} program={a['program']} "
              f"status={a['status']} twin=[{tw or '—'}]")
    print(f"\n{len(hits)} match(es).")


# ---------------------------------------------------------------------------
# ai (UKB-013) — grounded, cited retrieval
# ---------------------------------------------------------------------------
def cmd_ai(args):
    arts = _artifacts()
    by_uid = {a["universal_id"]: a for a in arts}
    by_native = {a["native_id"]: a for a in arts if a.get("native_id")}
    rels = _relationships()
    twin = _load(os.path.join(DATA_DIR, "twin.json"), {"subjects": {}})
    target = by_uid.get(args.subject) or by_native.get(args.subject)
    if not target:
        cand = [a for a in arts if args.subject.lower() in a["name"].lower()]
        target = cand[0] if cand else None
    if not target:
        sys.exit(f"not represented in the UKB: {args.subject} (gap, no fabrication)")
    uid = target["universal_id"]
    out_edges = [e for e in rels if e["from"] == uid]
    in_edges = [e for e in rels if e["to"] == uid]
    bundle = {
        "capability": args.capability,
        "subject": uid,
        "grounding": {
            "artifact": {k: target[k] for k in ("universal_id", "native_id", "name",
                                                 "volume", "status", "program", "path")},
            "twin_status": _twin_status(twin, uid),
            "parent": target["parent"],
            "dependencies": target["dependencies"],
            "outbound_edges": [(e["type"], e["to"]) for e in out_edges],
            "inbound_edges": [(e["from"], e["type"]) for e in in_edges],
        },
        "citations": sorted({uid, target["parent"] or uid,
                             *target["dependencies"],
                             *[e["to"] for e in out_edges],
                             *[e["from"] for e in in_edges]}),
        "note": "All facts are drawn from UKB authoritative sources; no content is fabricated (UKB-013).",
    }
    if args.capability == "impact":
        bundle["impact"] = {
            "dependents": [a["universal_id"] for a in arts if uid in a["dependencies"]],
            "children": [a["universal_id"] for a in arts if a["parent"] == uid],
        }
    print(json.dumps(bundle, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# UMB-IMP-005 — AI KNOWLEDGE & DIGITAL-TWIN INTELLIGENCE (grounded, cited).
# A unified reasoning surface that answers the seven canonical questions of
# Success Gate B entirely from the authoritative evidence base (artifacts, ID
# ledger, knowledge graph, change ledger, signal ledger, twin, certification
# evidence) and CITES its provenance — never fabricating (UMB-014 §2/§3;
# UCI-001 IP-3/IP-4; no AI store). Each capability is a pure query; `answer`
# composes all seven (Digital-Twin Intelligence Services).
# ---------------------------------------------------------------------------
def _intel_load():
    arts = _artifacts()
    return {
        "arts": arts,
        "by_uid": {a["universal_id"]: a for a in arts},
        "by_native": {a["native_id"]: a for a in arts if a.get("native_id")},
        "rels": _relationships(),
        "cl": _load(os.path.join(DATA_DIR, C.CHANGE_LEDGER_FILE),
                    {"change_events": [], "version_records": {}, "lineage": {}}),
        "signals": B.SignalLedger(DATA_DIR).signals,
        "twin": _load(os.path.join(DATA_DIR, "twin.json"), {"subjects": {}, "dimensions": {}}),
        "cert": _load(os.path.join(DATA_DIR, C.CERT_EVIDENCE_FILE), None),
        "sync_audit": T.load_audit(T.SYNC_AUDIT),
    }


def _intel_resolve(ev, subject):
    t = ev["by_uid"].get(subject) or ev["by_native"].get(subject)
    if not t:
        cand = [a for a in ev["arts"] if subject.lower() in a["name"].lower()]
        t = cand[0] if cand else None
    return t


def _intel_exists(ev, uid):
    """Knowledge Query Engine — what exists (grounded artifact facts)."""
    a = ev["by_uid"][uid]
    return {"answer": "exists", "engine": C.INTEL_QUESTIONS["exists"]["engine"],
            "facts": {k: a[k] for k in ("universal_id", "native_id", "name", "volume",
                                        "status", "program", "path", "parent")},
            "dependencies": a["dependencies"],
            "twin_status": _twin_status(ev["twin"], uid),
            "citations": [uid] + ([a["parent"]] if a["parent"] else [])}


def _intel_changed(ev, uid):
    """Change Reasoning Engine — what changed."""
    evs = [e for e in ev["cl"]["change_events"] if e["subject"] == uid]
    return {"answer": "changed", "engine": C.INTEL_QUESTIONS["changed"]["engine"],
            "events": [{"change_id": e["change_id"], "kind": e["kind"], "at": e["at"],
                        "from": e.get("from"), "to": e.get("to")} for e in evs],
            "count": len(evs),
            "citations": [e["change_id"] for e in evs]}


def _intel_why(ev, uid):
    """Change Reasoning Engine (causation) — why it changed (git evidence)."""
    evs = [e for e in ev["cl"]["change_events"] if e["subject"] == uid and e.get("commit")]
    return {"answer": "why", "engine": C.INTEL_QUESTIONS["why"]["engine"],
            "causation": [{"change_id": e["change_id"], "kind": e["kind"],
                           "commit": e["commit"].get("commit"),
                           "subject": e["commit"].get("subject"),
                           "author": e["commit"].get("author")} for e in evs],
            "note": "Causation is evidence-bound to git; absent for untracked/uncommitted state (never fabricated).",
            "citations": [e["change_id"] for e in evs]}


def _intel_impact(ev, uid):
    """Impact Reasoning Engine — what is impacted if this changes."""
    inbound = defaultdict(list)
    for e in ev["rels"]:
        if e["to"] == uid and e["type"] in C.INTEL_IMPACT_INBOUND_EDGE_TYPES:
            inbound[e["type"]].append(e["from"])
    dependents = [a["universal_id"] for a in ev["arts"] if uid in a["dependencies"]]
    cited = sorted({x for v in inbound.values() for x in v} | set(dependents))
    return {"answer": "impact", "engine": C.INTEL_QUESTIONS["impact"]["engine"],
            "impacted_by_edge": {t: sorted(set(v)) for t, v in inbound.items()},
            "dependents": dependents, "impacted_count": len(cited),
            "citations": cited}


def _intel_depends(ev, uid):
    """Dependency Reasoning Engine — what this depends on (transitive)."""
    by_uid = ev["by_uid"]
    seen, order, stack = set(), [], list(by_uid[uid]["dependencies"])
    while stack:
        d = stack.pop(0)
        if d in seen or d not in by_uid:
            continue
        seen.add(d); order.append(d)
        stack.extend(by_uid[d]["dependencies"])
    outbound = [(e["type"], e["to"]) for e in ev["rels"]
                if e["from"] == uid and e["type"] in ("Depends-On", "Consumes", "Implements", "Authorized-By")]
    return {"answer": "depends", "engine": C.INTEL_QUESTIONS["depends"]["engine"],
            "direct_dependencies": by_uid[uid]["dependencies"],
            "transitive_dependencies": order,
            "typed_outbound": outbound,
            "citations": order or by_uid[uid]["dependencies"]}


def _intel_certifications(ev, uid):
    """Certification Reasoning Engine — what certifications are affected."""
    a = ev["by_uid"][uid]
    cert_lane = a.get("traceability", {}).get("certification", [])
    cert_edges = [(e["type"], e["to"] if e["from"] == uid else e["from"])
                  for e in ev["rels"]
                  if (e["from"] == uid or e["to"] == uid)
                  and e["type"] in ("Certifies", "Certified-By")]
    twin_cert = _twin_status(ev["twin"], uid).get("certification")
    # If a certification evidence view exists (UMB-IMP-006), surface any domain
    # whose evidence references this subject.
    affected_domains = []
    if ev["cert"]:
        for dom, res in ev["cert"].get("domains", {}).items():
            eviden = json.dumps(res.get("evidence", ""))
            if uid in eviden or (a.get("native_id") and a["native_id"] in eviden):
                affected_domains.append(dom)
    return {"answer": "certifications", "engine": C.INTEL_QUESTIONS["certifications"]["engine"],
            "certification_spine_lane": cert_lane,
            "certification_edges": cert_edges,
            "twin_certification_state": twin_cert,
            "affected_certification_domains": affected_domains,
            "runtime_verdict": (ev["cert"] or {}).get("verdict"),
            "citations": cert_lane + [x for _, x in cert_edges]}


def _intel_sync(ev, uid):
    """Synchronization Intelligence Engine — what sync events are affected."""
    sigs = [s for s in ev["signals"] if s["subject_universal_id"] == uid]
    runs = set(s.get("ingest_run") for s in sigs if s.get("ingest_run"))
    return {"answer": "sync", "engine": C.INTEL_QUESTIONS["sync"]["engine"],
            "signals": [{"signal_id": s["signal_id"], "dimension": s["dimension"],
                         "state": s["state"], "source": s["source"], "as_of": s["as_of"],
                         "connector": s.get("connector"), "ingest_run": s.get("ingest_run"),
                         "evidence": s.get("evidence")} for s in sigs],
            "ingest_runs": sorted(r for r in runs if r),
            "signal_count": len(sigs),
            "citations": [s["signal_id"] for s in sigs] + sorted(r for r in runs if r)}


_INTEL_ENGINES = {
    "exists": _intel_exists, "changed": _intel_changed, "why": _intel_why,
    "impact": _intel_impact, "depends": _intel_depends,
    "certifications": _intel_certifications, "sync": _intel_sync,
}


def cmd_intel(args):
    ev = _intel_load()
    # Knowledge Query Engine corpus mode: `intel exists` with no/za partial subject
    # lists what exists matching a keyword (grounded, cited) — "What exists".
    if args.capability == "exists" and args.subject:
        t = _intel_resolve(ev, args.subject)
        if not t:
            hits = _search(ev["arts"], ev["twin"], keyword=args.subject)
            print(json.dumps({"answer": "exists", "engine": C.INTEL_QUESTIONS["exists"]["engine"],
                              "query": args.subject, "match_count": len(hits),
                              "matches": [{"universal_id": h["universal_id"], "name": h["name"],
                                           "volume": h["volume"], "status": h["status"]}
                                          for h in hits[:25]],
                              "citations": [h["universal_id"] for h in hits[:25]],
                              "note": "Grounded in the artifact registry; no fabrication (UMB-014)."},
                             ensure_ascii=False, indent=2))
            return
    else:
        t = _intel_resolve(ev, args.subject)
    if not t:
        sys.exit(f"not represented in the UKB: {args.subject} (gap, no fabrication)")
    uid = t["universal_id"]

    caps = list(_INTEL_ENGINES) if args.capability == "answer" else [args.capability]
    answers = {cap: _INTEL_ENGINES[cap](ev, uid) for cap in caps}
    citations = sorted({c for a in answers.values() for c in a.get("citations", [])})
    bundle = {
        "subject": uid,
        "subject_name": t["name"],
        "native_id": t.get("native_id"),
        "capability": args.capability,
        "digital_twin_intelligence": answers,
        "citations": citations,
        "provenance": {q: C.INTEL_QUESTIONS[q]["evidence"] for q in caps if q in C.INTEL_QUESTIONS},
        "note": "All answers are DERIVED on demand from authoritative evidence and are "
                "reproducible from the same stores; nothing is fabricated (UMB-014 §2/§3; "
                "UCI-001 IP-3/IP-4; no AI store).",
    }
    print(json.dumps(bundle, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# UMB-IMP-006 — DIGITAL-TWIN CERTIFICATION RUNTIME (9 integrity domains ·
# evidence generation · append-only audit trail · recovery · reporting).
# Extends the `twin --check` hard-check suite into a domain-organized runtime
# that attests Identity / Registry / Traceability / Knowledge-Graph / Change /
# Version / Lineage / Synchronization / Twin-Intelligence integrity over the REAL
# authoritative state, persists machine-readable evidence, appends an attributed
# audit trail, names exact defects for append-only repair (recovery), and emits a
# human-navigable report. Reuses the existing validators; creates no new store
# (evidence/report are regenerated derived views; UMB-017; non-terminal CR-INF-011).
# ---------------------------------------------------------------------------
def _certify_domains():
    arts = _artifacts()
    by_uid = {a["universal_id"]: a for a in arts}
    rels = _relationships()
    ledger = _load(os.path.join(DATA_DIR, "id-ledger.json"), {"by_path": {}, "history": {}})
    cl = _load(os.path.join(DATA_DIR, C.CHANGE_LEDGER_FILE),
               {"change_events": [], "version_records": {}, "lineage": {}})
    sledger = B.SignalLedger(DATA_DIR)
    twin, _ = _compute_twin()
    sync_audit = T.load_audit(T.SYNC_AUDIT)
    root = "UCOS-BOOK-000000"
    D = {}

    def dom(name, checks):
        D[name] = {"pass": all(c["pass"] for c in checks), "checks": checks}

    # 1) IDENTITY INTEGRITY — no dup/reused IDs or pages; append-only ledger.
    uids = [a["universal_id"] for a in arts]
    dup_ids = sorted({u for u in uids if uids.count(u) > 1})
    spans = sorted((a["page_start"], a["page_end"], a["universal_id"]) for a in arts)
    overlaps, last_end = [], 0
    for s, e, uid in spans:
        if s <= last_end:
            overlaps.append(uid)
        last_end = max(last_end, e)
    dom("identity", [
        {"name": "no duplicate Universal IDs", "pass": not dup_ids, "detail": dup_ids[:5] or f"{len(uids)} unique"},
        {"name": "no overlapping page ranges", "pass": not overlaps, "detail": overlaps[:5] or "append-only pages intact"},
        {"name": "ledger page cursor >= max page", "pass": ledger.get("page_cursor", 0) >= (last_end or 0),
         "detail": f"cursor={ledger.get('page_cursor', 0)} max_end={last_end}"},
    ])

    # 2) REGISTRY INTEGRITY — parity + every registered path in ledger + fields.
    missing_ledger = [a["universal_id"] for a in arts if a["path"] not in ledger.get("by_path", {})]
    missing_fields = [a["universal_id"] for a in arts
                      if not a.get("name") or not a.get("volume") or not a.get("program")]
    dom("registry", [
        {"name": "every artifact present in id-ledger", "pass": not missing_ledger,
         "detail": missing_ledger[:5] or f"{len(arts)} artifacts ledgered"},
        {"name": "every artifact carries name+volume+program", "pass": not missing_fields,
         "detail": missing_fields[:5] or "all classified"},
    ])

    # 3) TRACEABILITY INTEGRITY — reachable from root; no orphan (UMB-017 C-08).
    # NOTE: unresolved UCOS-shaped spine values are INTENTIONAL evidence-bound
    # external markers (UMB-007 §5; UMB-IMP-002), NOT dangling references — edge
    # referential integrity is asserted separately in the knowledge_graph domain.
    orphans = [a["universal_id"] for a in arts if a["universal_id"] != root and not a["parent"]]
    unreachable = _unreachable_from_root(arts, root)
    ext_markers = sum(1 for a in arts for lane, vals in a.get("traceability", {}).items()
                      for v in vals if v.startswith("UCOS-") and v not in by_uid)
    dom("traceability", [
        {"name": "no orphan (every non-root has a parent)", "pass": not orphans, "detail": orphans[:5] or "all parented"},
        {"name": "all reachable from BOOK root", "pass": not unreachable, "detail": unreachable[:5] or "fully reachable"},
        {"name": "spine external markers recorded (not dangling edges)", "pass": True,
         "detail": f"{ext_markers} evidence-bound external markers (by design, UMB-007 §5)"},
    ])

    # 4) KNOWLEDGE-GRAPH INTEGRITY — no dangling edges; Depends-On acyclic.
    dangling = [e["edge_id"] for e in rels if e["from"] not in by_uid or e["to"] not in by_uid]
    dep = defaultdict(list)
    for a in arts:
        for d in a["dependencies"]:
            dep[a["universal_id"]].append(d)
    cyc = _has_cycle(dep)
    dom("knowledge_graph", [
        {"name": "no dangling edge endpoints", "pass": not dangling, "detail": dangling[:5] or f"{len(rels)} edges resolve"},
        {"name": "Depends-On graph acyclic", "pass": not cyc, "detail": "acyclic" if not cyc else f"cycle via {cyc}"},
    ])

    # 5) CHANGE-INTELLIGENCE INTEGRITY — events node-bound + unique + append-only.
    ce = cl.get("change_events", [])
    bad_subj = [e["change_id"] for e in ce if e["subject"] not in by_uid]
    cids = [e["change_id"] for e in ce]
    dup_ce = sorted({c for c in cids if cids.count(c) > 1})
    hist = ledger.get("history", {})
    nonmono = [uid for uid, snaps in hist.items()
               if [s["seq"] for s in snaps] != list(range(1, len(snaps) + 1))]
    dom("change_intelligence", [
        {"name": "every change event bound to a real subject", "pass": not bad_subj,
         "detail": bad_subj[:5] or f"{len(ce)} events node-bound"},
        {"name": "change ids unique", "pass": not dup_ce, "detail": dup_ce[:5] or "unique"},
        {"name": "snapshot history seq monotonic (append-only)", "pass": not nonmono,
         "detail": nonmono[:5] or f"{len(hist)} histories append-only"},
    ])

    # 6) VERSION INTEGRITY — records consistent with append-only history.
    vr = cl.get("version_records", {})
    bad_ver = []
    for uid, rec in vr.items():
        snaps = hist.get(uid, [])
        if snaps and rec.get("current_version") != snaps[-1].get("version"):
            bad_ver.append(uid)
        if rec.get("version_depth", 0) < 1:
            bad_ver.append(f"{uid}(depth<1)")
    dom("version", [
        {"name": "current_version matches latest snapshot", "pass": not bad_ver,
         "detail": bad_ver[:5] or f"{len(vr)} version records consistent"},
    ])

    # 7) LINEAGE INTEGRITY — endpoints resolve; ancestry acyclic; bidirectional.
    ln = cl.get("lineage", {})
    bad_ln = []
    for uid, v in ln.items():
        for p in v.get("predecessors", []) + v.get("successors", []):
            if p not in by_uid:
                bad_ln.append(f"{uid}->{p}")
        if uid in v.get("ancestor_chain", []):
            bad_ln.append(f"{uid} in own ancestry")
    dom("lineage", [
        {"name": "lineage endpoints resolve + ancestry acyclic", "pass": not bad_ln,
         "detail": bad_ln[:5] or f"{len(ln)} lineage nodes intact"},
    ])

    # 8) SYNCHRONIZATION INTEGRITY — signals resolve/provenance/secret-free; audit.
    sigs = sledger.signals
    unresolved = [s["signal_id"] for s in sigs if s["subject_universal_id"] not in by_uid]
    no_prov = [s["signal_id"] for s in sigs if not s.get("source") or not s.get("as_of")]
    secretful = [s["signal_id"] for s in sigs if s.get("evidence") and not B._secret_free(s["evidence"])]
    last_sync = sync_audit["runs"][-1] if sync_audit.get("runs") else None
    dom("synchronization", [
        {"name": "every signal resolves to a subject", "pass": not unresolved,
         "detail": unresolved[:5] or f"{len(sigs)} signals resolve"},
        {"name": "every signal carries provenance", "pass": not no_prov, "detail": no_prov[:5] or "source+as_of present"},
        {"name": "no secret in signal evidence (RR-07)", "pass": not secretful, "detail": secretful[:5] or "secret-free"},
        {"name": "synchronization audit present + last run PASS", "pass": bool(last_sync) and last_sync.get("result") == "PASS",
         "detail": (f"last sync run {last_sync['result']}" if last_sync else "no sync audit yet")},
    ])

    # 9) TWIN-INTELLIGENCE INTEGRITY — dimensions computed; intel answerable+cited.
    ct = _load(os.path.join(DATA_DIR, "control-tower.json"), {"dimensions": {}})
    manual = [d for d, v in ct["dimensions"].items()
              if v.get("signal_source") == "MANUAL" and d in twin["dimensions"]]
    # intel smoke: answer for the BOOK root must produce a grounded, cited bundle
    ev = _intel_load()
    smoke = _intel_exists(ev, root)
    dom("twin_intelligence", [
        {"name": "no MANUAL source among computed dimensions", "pass": not manual,
         "detail": manual[:5] or f"{len(twin['dimensions'])} dimensions computed"},
        {"name": "intelligence surface answerable + cited", "pass": bool(smoke.get("citations")),
         "detail": f"exists({root}) cited {len(smoke.get('citations', []))} ids"},
    ])

    # 10) EXECUTION-REGISTER INTEGRITY (EXEC-REG-001 / RUNTIME-006) — execution
    #     instances minted from the ONE identity authority (EXL-02); forward-only
    #     append-only lifecycle (EXL-07/10); subjects + dependencies resolve
    #     (referential integrity); dependency graph acyclic (EXL-17). DOMAIN-C
    #     record-only; never a DOMAIN-B/roadmap projection (STATUS-001 §2). An
    #     empty/absent register passes vacuously.
    execs = _load(os.path.join(DATA_DIR, C.EXECUTION_STORE_FILE),
                  {"executions": {}}).get("executions", {})
    minted = {v["execution_id"] for v in ledger.get("by_execution", {}).values()}
    unminted = sorted(e for e in execs if e not in minted)
    bad_lifecycle = []
    bad_ref = []
    edep = {}
    for e, r in execs.items():
        if r.get("lifecycle_state") not in C.EXECUTION_LIFECYCLE:
            bad_lifecycle.append(e)
            continue
        trs = r.get("transitions", [])
        if [t.get("seq") for t in trs] != list(range(1, len(trs) + 1)):
            bad_lifecycle.append(e)
        else:
            for a, b in zip(trs, trs[1:]):
                if b.get("to") not in C.EXECUTION_TRANSITIONS.get(a.get("to"), ()):
                    bad_lifecycle.append(e)
                    break
            if trs and trs[-1].get("to") != r.get("lifecycle_state"):
                bad_lifecycle.append(e)
        subj = r.get("subject_universal_id")
        if subj and subj not in by_uid:
            bad_ref.append(f"{e}:subject")
        for d in r.get("dependencies", []):
            if d not in execs:
                bad_ref.append(f"{e}->{d}")
        edep[e] = [d for d in r.get("dependencies", []) if d in execs]
    ecyc = _has_cycle(edep)
    dom("execution", [
        {"name": "every execution minted from the id-ledger identity authority (EXL-02)",
         "pass": not unminted, "detail": unminted[:5] or f"{len(execs)} executions ledgered"},
        {"name": "forward-only append-only lifecycle (RUNTIME-006 EXL-07/10)",
         "pass": not bad_lifecycle, "detail": sorted(set(bad_lifecycle))[:5] or "forward-only, append-only"},
        {"name": "subjects + dependencies resolve (referential integrity)",
         "pass": not bad_ref, "detail": bad_ref[:5] or "all resolve"},
        {"name": "execution dependency graph acyclic (EXL-17)",
         "pass": not ecyc, "detail": "acyclic" if not ecyc else f"cycle via {ecyc}"},
    ])

    return D, {"artifacts": len(arts), "edges": len(rels), "change_events": len(ce),
               "signals": len(sigs), "lineage_nodes": len(ln), "executions": len(execs)}


def _write_cert_report(cert):
    lines = ["# UCOS Ω∞ — DIGITAL TWIN CERTIFICATION REGISTRY", "",
             "<!-- AUTO-GENERATED by 00-BOOK/tools/ukbx.py certify — do not edit by hand. -->", "",
             f"**Generated:** {cert['generated_at']}  ·  **Generator:** v{cert['generator_version']}", "",
             f"**VERDICT: {cert['verdict']}**  ·  domains {cert['domains_passed']}/{cert['domains_total']}  "
             f"·  scope: {cert['scope']['artifacts']} artifacts, {cert['scope']['edges']} edges, "
             f"{cert['scope']['change_events']} change events, {cert['scope']['signals']} signals", "",
             "Runtime certification over the real repository, synchronization, intelligence, "
             "traceability, and graph state (UMB-017). Non-terminal (AUTH-INF-001 CR-INF-011): "
             "certification closes scope, never evolution. A failed check names the exact defect "
             "for append-only repair and re-run.", "",
             "| # | Integrity Domain | Result | Checks | Defects |",
             "|---|------------------|--------|--------|---------|"]
    for i, (name, d) in enumerate(cert["domains"].items(), 1):
        npass = sum(1 for c in d["checks"] if c["pass"])
        defects = "; ".join(c["name"] for c in d["checks"] if not c["pass"]) or "—"
        lines.append(f"| {i} | {name.replace('_', ' ').title()} | {'PASS' if d['pass'] else 'FAIL'} "
                     f"| {npass}/{len(d['checks'])} | {defects} |")
    lines += ["", "## Domain evidence", ""]
    for name, d in cert["domains"].items():
        lines += [f"### {name.replace('_', ' ').title()} — {'PASS' if d['pass'] else 'FAIL'}", "",
                  "| Check | Result | Evidence |", "|-------|--------|----------|"]
        for c in d["checks"]:
            det = c["detail"] if isinstance(c["detail"], str) else ", ".join(c["detail"])
            lines.append(f"| {c['name']} | {'PASS' if c['pass'] else 'FAIL'} | {det} |")
        lines.append("")
    lines += ["*Return: [UCOS-BOOK-000000 Master Index](../../" +
              "00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*", ""]
    _dump_text(os.path.join(REG_DIR, C.CERT_REPORT_FILE), "\n".join(lines))


def _cert_audit_append(cert):
    """Record a certification verdict in the append-only runtime audit log via the
    single telemetry authority (``.runtime/governance/certification-audit.json``).
    A consecutive run with an identical {verdict, per-domain pass} fingerprint is a
    no-op so idempotent re-runs never grow the log. Operational telemetry."""
    run = {"at": cert["generated_at"],
           "generator_version": cert["generator_version"],
           "verdict": cert["verdict"],
           "domains_passed": cert["domains_passed"],
           "domains_total": cert["domains_total"],
           "domains": {n: d["pass"] for n, d in cert["domains"].items()},
           "scope": cert["scope"]}

    def dedup(runs, rec):
        if runs:
            last = runs[-1]
            if last.get("verdict") == rec["verdict"] and last.get("domains") == rec["domains"]:
                return last["seq"]
        return None

    return T.append_audit(T.CERT_AUDIT, run, dedup)


def cmd_certify(args):
    """UMB-IMP-006 Digital-Twin Certification Runtime."""
    domains, scope = _certify_domains()
    passed = sum(1 for d in domains.values() if d["pass"])
    verdict = "CERTIFIED" if passed == len(domains) else "NOT-CERTIFIED"
    cert = {
        "generated_at": _now(), "generator_version": GEN_VERSION,
        "standard": "UMB-017 Digital Twin Certification (non-terminal; AUTH-INF-001 CR-INF-011)",
        "verdict": verdict, "domains_total": len(domains), "domains_passed": passed,
        "domains": domains, "scope": scope,
    }
    # Evidence generation (derived view) + append-only audit trail + report.
    _dump(os.path.join(DATA_DIR, C.CERT_EVIDENCE_FILE), cert)
    seq = _cert_audit_append(cert)
    _write_cert_report(cert)

    print("UCOS Ω∞ Digital-Twin Certification Runtime (UMB-IMP-006 / UMB-017)")
    print("-" * 64)
    for i, (name, d) in enumerate(domains.items(), 1):
        print(f"  [{'PASS' if d['pass'] else 'FAIL'}] {i}. {name.replace('_', ' ').title()}")
        for c in d["checks"]:
            if not c["pass"]:                    # Recovery: name the exact defect
                det = c["detail"] if isinstance(c["detail"], str) else ", ".join(c["detail"])
                print(f"          DEFECT: {c['name']} — {det}")
    print("-" * 64)
    print(f"  evidence : {os.path.relpath(os.path.join(DATA_DIR, C.CERT_EVIDENCE_FILE), REPO)}")
    print(f"  audit    : {os.path.relpath(os.path.join(T.GOVERNANCE_DIR, T.CERT_AUDIT), REPO)} (run #{seq})")
    print(f"  report   : {os.path.relpath(os.path.join(REG_DIR, C.CERT_REPORT_FILE), REPO)}")
    print(f"RESULT: {verdict} (integrity domains {passed}/{len(domains)}) — "
          f"scope {scope['artifacts']} artifacts, {scope['signals']} signals, "
          f"{scope['change_events']} change events")
    if verdict != "CERTIFIED":
        print("CERTIFICATION FAILED — defects named above for append-only repair + re-run.")
        sys.exit(1)



def cmd_portal(args):
    arts = _artifacts()
    by_uid = {a["universal_id"]: a for a in arts}
    rels = _relationships()
    twin = _load(os.path.join(DATA_DIR, "twin.json"), {"subjects": {}})
    children = defaultdict(list)
    inbound = defaultdict(list)
    for a in arts:
        if a["parent"]:
            children[a["parent"]].append(a["universal_id"])
    for e in rels:
        inbound[e["to"]].append((e["from"], e["type"]))

    os.makedirs(PORTAL_DIR, exist_ok=True)
    # index
    idx = ["# UCOS Ω∞ — Navigation Portal (generated)", "",
           f"*Generated {_now()} by ukbx portal. {len(arts)} artifacts. "
           f"No dead ends: every page links parent, children, backlinks, and master index.*", "",
           "| Universal ID | Name | Volume | Status |",
           "|--------------|------|--------|--------|"]
    for a in sorted(arts, key=lambda x: x["page_start"]):
        idx.append(f"| [{a['universal_id']}]({a['universal_id']}.md) | "
                   f"{a['name'][:60].replace('|','/')} | {a['volume']} | {a['status']} |")
    _dump_text(os.path.join(PORTAL_DIR, "index.md"), "\n".join(idx))

    for a in arts:
        uid = a["universal_id"]
        crumbs = _breadcrumbs(uid, by_uid)
        tw = ", ".join(f"{k}={v}" for k, v in _twin_status(twin, uid).items()) or "—"
        page = [f"# {uid} — {a['name']}", "",
                "Breadcrumbs: " + " › ".join(f"[{c}]({c}.md)" if c in by_uid else c for c in crumbs), "",
                f"- Volume: {a['volume']}  ·  Status: {a['status']}  ·  Twin: [{tw}]",
                f"- Native: {a.get('native_id') or '—'}  ·  Program: {a['program']}",
                f"- Parent: " + (f"[{a['parent']}]({a['parent']}.md)" if a['parent'] else "— (root)"),
                f"- Source: [{a['path']}](../../{a['path']})", "",
                "## Children (forward)"]
        page += [f"- [{c}]({c}.md) {by_uid[c]['name'][:50]}" for c in children.get(uid, [])] or ["- (none)"]
        page += ["", "## Backlinks (reverse)"]
        page += [f"- [{f}]({f}.md) —{t}→" for f, t in inbound.get(uid, [])] or ["- (none)"]
        page += ["", f"Return: [Portal Index](index.md) · "
                 f"[Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)"]
        _dump_text(os.path.join(PORTAL_DIR, f"{uid}.md"), "\n".join(page))
    print(f"portal generated: {len(arts)} pages + index at 00-BOOK/PORTAL/")


def _breadcrumbs(uid, by_uid):
    chain = []
    cur = uid
    seen = set()
    while cur and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        cur = by_uid.get(cur, {}).get("parent")
    return list(reversed(chain))


# ---------------------------------------------------------------------------
# validate (twin-specific; complements ukb.py validate)
# ---------------------------------------------------------------------------
def cmd_validate(args):
    arts = _artifacts()
    by_uid = {a["universal_id"] for a in arts}
    ledger = B.SignalLedger(DATA_DIR)
    problems = []
    seq_seen = set()
    for s in ledger.signals:
        if s["signal_id"] in seq_seen:
            problems.append(f"duplicate signal id {s['signal_id']}")
        seq_seen.add(s["signal_id"])
        if s["subject_universal_id"] not in by_uid:
            problems.append(f"{s['signal_id']} unknown subject {s['subject_universal_id']}")
        for f in ("dimension", "state", "source", "as_of"):
            if not s.get(f):
                problems.append(f"{s['signal_id']} missing {f}")
        if s.get("evidence") and not B._secret_free(s["evidence"]):
            problems.append(f"{s['signal_id']} secret in evidence (RR-07)")
    if problems:
        print(f"TWIN VALIDATION FAILED — {len(problems)} problem(s):")
        for p in problems[:50]:
            print("  -", p)
        sys.exit(1)
    print(f"TWIN VALIDATION PASSED — {len(ledger.signals)} signals, append-only, "
          f"every subject resolves, provenance present, no embedded secrets.")


def main():
    ap = argparse.ArgumentParser(prog="ukbx", description="UCOS Ω∞ UKB Advancement Engine (Digital Twin).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ip = sub.add_parser("ingest", help="Run connectors, append signals.")
    ip.add_argument("--connector", help="Only run this connector (default: all).")

    syp = sub.add_parser("sync", help="UMB-IMP-004 synchronization runtime "
                         "(discover/monitor/detect/execute/verify/audit/recover).")
    syp.add_argument("--connector", help="Only synchronize this connector.")
    syp.add_argument("--due", action="store_true",
                     help="Only run connectors whose cadence has elapsed (scheduling).")
    syp.add_argument("--schedule", action="store_true",
                     help="Print the cadence-driven schedule and exit (no run).")

    tp = sub.add_parser("twin", help="Recompute the twin; --check runs certification.")
    tp.add_argument("--check", nargs="?", const="all", default=None,
                    help="Run Digital-Twin Certification (UKB-014).")

    ep = sub.add_parser("export", help="Dynamic export: scope selector format.")
    ep.add_argument("scope"); ep.add_argument("selector"); ep.add_argument("format")
    ep.add_argument("--out")

    spp = sub.add_parser("search", help="Faceted + graph-aware search.")
    spp.add_argument("query", nargs="?", default="")
    spp.add_argument("--id"); spp.add_argument("--volume"); spp.add_argument("--program")
    spp.add_argument("--status"); spp.add_argument("--dependency"); spp.add_argument("--relationship")
    spp.add_argument("--limit", type=int, default=25)

    aip = sub.add_parser("ai", help="Grounded, cited retrieval.")
    aip.add_argument("capability", choices=["explain", "trace", "impact", "change"])
    aip.add_argument("subject")

    inp = sub.add_parser("intel", help="UMB-IMP-005 Digital-Twin Intelligence: "
                         "grounded, cited answers to the seven canonical questions.")
    inp.add_argument("capability", choices=["exists", "changed", "why", "impact",
                                            "depends", "certifications", "sync", "answer"])
    inp.add_argument("subject")

    sub.add_parser("portal", help="Generate the navigation portal.")
    sub.add_parser("validate", help="Twin-specific validation.")

    sub.add_parser("certify", help="UMB-IMP-006 Digital-Twin Certification Runtime "
                   "(9 integrity domains, evidence, audit trail, recovery, report).")

    args = ap.parse_args()
    {"ingest": cmd_ingest, "sync": cmd_sync, "twin": cmd_twin, "export": cmd_export,
     "search": cmd_search, "ai": cmd_ai, "intel": cmd_intel, "portal": cmd_portal,
     "validate": cmd_validate, "certify": cmd_certify}[args.cmd](args)


if __name__ == "__main__":
    main()
