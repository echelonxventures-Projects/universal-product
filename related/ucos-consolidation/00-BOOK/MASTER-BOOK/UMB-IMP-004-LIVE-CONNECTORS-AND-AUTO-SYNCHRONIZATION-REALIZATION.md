# UCOS Ω∞ — UMB-IMP-004 · LIVE CONNECTORS AND AUTO SYNCHRONIZATION REALIZATION

> **STATUS DOMAIN:** IMPLEMENTATION (DOMAIN-C — code that exists and runs)
> **STATUS BASIS:** The realized machinery in `00-BOOK/tools/{config.py,ukbx.py,connectors/*}` (dynamic connector discovery + `ukbx sync` synchronization runtime: schedule · execute · verify · audit · recover) and the append-only operational log `00-BOOK/DATA/sync-audit.json` + refreshed `signals.json`/`twin.json`/`control-tower.json` — plus live execution this session (dynamic discovery of 5 connectors with a newly-added connector picked up with zero core edit; a verified synchronization run appending 2 real signals to real subjects; idempotent re-run; cadence-driven `--due` scheduling; per-connector recovery isolation proof; and the full `register.sh` transaction `CERTIFIED (hard checks 7/7)` with State-Synchronization now Phase 2/9). Evidence only; no projection.

| Field | Value |
|-------|-------|
| ARTIFACT ID | UMB-IMP-004 |
| ARTIFACT | Live Connectors and Auto Synchronization Realization |
| PROGRAM | UCOS Ω∞ Universal Master Book Architecture Program (UMB) |
| CLASSIFICATION | Implementation Realization — the fourth operational capability of the UMB architecture and the first Runtime Realization (UMB-RTP-001 Phase A): the minimum runtime for live source discovery, monitoring, change detection, synchronization scheduling, execution, verification, audit, and recovery — metadata/configuration-driven and append-only |
| STATUS | ACTIVE · IMPLEMENTATION |
| PARENT | UMB-000 |
| DEPENDS-ON | UMB-IMP-001 (auto-registration); UMB-IMP-002 (typed graph + spine); UMB-IMP-003 (change/version/lineage); UMB-012 (read-only target); UKB-ADV-001 (connector architecture); STATUS-001; REG-AUTO-001; UCI-001; AUTH-INF-001; UMB-000 |
| IMPLEMENTS | UMB-012 |
| CONSUMES (read-only) | UMB-000…020; UMB-IMP-001; UMB-IMP-002; UMB-IMP-003; `connector.schema.json`; `signal.schema.json` |
| TRACES-TO | UMB-012 |
| RELATES Evolves-From | UMB-IMP-003 |
| PRODUCES (append-only, machinery — not registered artifacts) | `connectors/__init__.py` `discover()` (dynamic connector discovery); `config.py` UMB-IMP-004 block (sync audit/stages/cadence/verify gates); `ukbx.py` `cmd_sync()`/`_sync_audit_append()`/`_sync_last_runs()`/`_is_due()`/`_verify_sync()` + `sync` subcommand; new reference connector `connectors/sonarqube.py` (+ fixture); `register.sh` Phase 2/9 State-Synchronization; generated view `DATA/sync-audit.json` + refreshed `signals.json`/`twin.json`/`control-tower.json` |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| VOLUME | VOL-022 (MASTER BOOK ARCHITECTURE) |
| BASELINE DATE | 2026-07-16 |

*This is an implementation artifact. It realizes — in reusable, standard-library machinery — the minimum **runtime** required to turn the Master Book's connector layer and append-only Signal ledger into an operational **State-Synchronization runtime**: live source discovery, source monitoring, change detection, synchronization scheduling, execution, verification, audit, and recovery, with **no hard-coded connector list** and **infinite connector expansion**. It creates no new architecture family, no new registry, no new identifier namespace, and no new lifecycle; it reuses the existing engines (`ukb.py`, `ukbx.py`), the existing connector framework (`connectors/`), the existing append-only Signal ledger + per-connector cursors, the existing deterministic roll-up, and the existing Atomic Registration Transaction (`register.sh`) exclusively. It is append-only and authority-neutral, subordinate to the frozen constitutional corpus, STATUS-001, REG-AUTO-001, UCI-001, AUTH-INF-001, and UMB-000…020; where any statement conflicts with a higher instrument, the higher instrument governs and the statement is void to the extent of the conflict.*

---

## SECTION 1 — IMPLEMENTATION SCOPE

**In scope (realized by this artifact).** The eight runtime capabilities of UMB-RTP-001 Phase A:

1. **Live Source Discovery.** `connectors.discover()` auto-imports every connector module in the `connectors` package (via `pkgutil`), running each `@register` decorator so `REGISTRY` populates dynamically — no compiled-in connector list.
2. **Source Monitoring.** Each connector reads its persisted per-connector cursor (`connector-cursors.json`) to know its last synchronized high-water mark.
3. **Change Detection.** `fetch(since)` returns only events strictly newer than the cursor (incremental), so unchanged sources yield nothing (no-op).
4. **Synchronization Scheduling.** `ukbx sync --due` runs only connectors whose cadence (`cadence_seconds` class override, else `SYNC_DEFAULT_CADENCE_SECONDS`) has elapsed since their last successful run in the audit log; `--schedule` prints the cadence-driven plan.
5. **Synchronization Execution.** Events are normalized to append-only Signals keyed to Universal IDs and appended idempotently; cursors advance forward-only.
6. **Synchronization Verification.** Five hard gates assert every appended signal resolves to a registered subject, carries provenance, is secret-free, that no cursor regressed, and that signal ids remain unique + gapless.
7. **Synchronization Audit.** Every run appends a record (per-connector counts, cursors before/after, verification result, recovery list) to the append-only `sync-audit.json`.
8. **Synchronization Recovery.** A connector that fails is isolated (try/except per connector); its cursor is preserved for resume; the run continues for all other connectors and still verifies.

**Out of scope (explicitly not built here; unchanged).** Live network transports (the connectors remain offline-replay reference implementations; a live impl swaps only `fetch`), AI reasoning (UMB-014/UMB-IMP-005), the 9-domain certification runtime (UMB-017/UMB-IMP-006), semantic search (UMB-013), and binary publication (UMB-011). These are neither claimed nor implied (STATUS-001 §2 non-projection).

**Governing constraint.** Exactly **one** registered artifact is created by this mission (this document). All executable changes are made to the machinery under `00-BOOK/tools/` (excluded from registration by `config.py::EXCLUDE_DIR_PREFIXES`). The derived view (`sync-audit.json`) and refreshed `signals.json`/`twin.json`/`control-tower.json` are generated outputs under already-excluded `DATA/` — no new registered artifact and no new authoritative store.

---

## SECTION 2 — CURRENT-STATE ANALYSIS

Direct inspection + live execution established the pre-implementation state:

| Capability | Pre-state | Evidence |
|-----------|-----------|----------|
| Connector framework | **REALIZED** — `Connector`/`SignalLedger`/`rollup_dimensions` + 4 reference connectors | `connectors/base.py`, `connectors/{github_actions,trivy,prometheus,kubernetes}.py` |
| Connector discovery | **HARD-CODED (gap)** — `ukbx.py` imported exactly 4 connectors by name (`from connectors import github_actions, trivy, prometheus, kubernetes`), pinning the set at four | `ukbx.py` line 46 (pre-state) — violated "No hard-coded connector lists / Infinite connector expansion" |
| Ingest | **REALIZED (partial)** — `ukbx ingest` fetched + appended signals, advanced cursors | `ukbx.py::cmd_ingest` |
| Scheduling | **ABSENT** — no cadence, no due-selection, no schedule view | — |
| Verification | **ABSENT** — ingest asserted no post-run gates over the appended signals/cursors | — |
| Audit | **ABSENT** — no synchronization-run log (only `signals.json` growth); no per-run provenance record | — |
| Recovery | **ABSENT** — a raising connector aborted the whole ingest (no isolation, no cursor preservation) | `ukbx.py::cmd_ingest` (no per-connector try/except) |

**Proof of the gap (observed live).** At session start `ukbx` imported a fixed four-connector list; there was no `sync` command, no `sync-audit.json`, no scheduling, no verification gates, and a single failing connector would raise out of `cmd_ingest`. The signal ledger held 12 signals.

---

## SECTION 3 — REUSE ANALYSIS

Per the mission's "reuse all existing UCOS machinery; do not replace existing capabilities; extend existing capabilities," every requirement maps to an existing mechanism; only thin, additive layers were written. No engine, registry, identifier namespace, lifecycle, or store was created.

| Requirement | Reused existing mechanism | Net-new (additive) |
|-------------|---------------------------|--------------------|
| Live source discovery | the `connectors` package + `@register`/`REGISTRY` (UKB-ADV-001) | `discover()` — dynamic `pkgutil` import (replaces the hard-coded import list) |
| Source monitoring / change detection | per-connector cursors `connector-cursors.json` + `Connector.fetch(since)`/`cursor()`/`high_water()` | none — reused verbatim |
| Execution / idempotent append | `SignalLedger.append(idempotency_key=…)` + `make_signal` (secret-guarded) | `cmd_sync` execution loop (reuses the ingest append path) |
| Scheduling | the append-only `sync-audit.json` last-run record | `_sync_last_runs`/`_is_due` cadence selection; per-connector `cadence_seconds` override |
| Verification | `SignalLedger` invariants + `base._secret_free` | `_verify_sync` (5 hard gates + 1 advisory) |
| Audit | the enforcement-audit dedup pattern (UMB-IMP-001) | `_sync_audit_append` (append-only, no-op-deduped) |
| Recovery | Python exception isolation | per-connector try/except; cursor preserved on failure |
| State roll-up → twin | `rollup_dimensions` + `_compute_twin`/`_refresh_control_tower` (UKB-012) | none — reused verbatim (sync calls them) |
| Registration / transaction | `register.sh` Atomic Transaction `T` | one added phase (2/9) `ukbx sync --due` |
| Certification | `ukbx twin --check` (C-04/05/07/08/…) | none — reused verbatim as the correctness gate |

---

## SECTION 4 — LIVE SOURCE DISCOVERY DESIGN (no hard-coded connector list)

Discovery is realized as UMB-012 §4/§6 specifies — **sources are pluggable; a new authoritative system is a new connector subclass, no core change** (AUTH-INF-001 CR-INF-003/010).

`connectors.discover()` enumerates the package's own modules with `pkgutil.iter_modules`, skipping the framework module `base` and any dunder/private (`_`-prefixed) module, and imports each so its `@register` decorator runs. The result is `REGISTRY` populated purely by the **presence of files**, not by any enumerated list. A module that fails to import is isolated (its error captured) and discovery continues — recovery at the discovery boundary. `ukbx.py` now performs `discover()` at import instead of the former fixed `from connectors import github_actions, trivy, prometheus, kubernetes`.

**Zero hard coding / infinite expansion (proven).** A brand-new connector `connectors/sonarqube.py` (dimension `quality`, `cadence_seconds=1800`) was added with **no edit to `ukbx.py`, `__init__.py`, or `config.py`** and was discovered automatically: `ukbx sync --schedule` reports **5** connectors (`github-actions, kubernetes, prometheus, sonarqube, trivy`). There is no ceiling on connector count (CR-INF-010).

---

## SECTION 5 — SYNCHRONIZATION RUNTIME DESIGN (schedule · execute · verify · audit · recover)

The runtime is `ukbx sync`, realizing the UMB-012 §3 pipeline for the **State-synchronization surface** (§2):

```
discover → monitor → detect → execute → verify → audit → (recover)  → roll-up (twin + control tower)
```

**5.1 Scheduling.** `--due` selects connectors whose cadence elapsed since their last OK run (from `sync-audit.json`); each connector may override `cadence_seconds` (SonarQube = 1800s vs default 900s). `--schedule` prints the plan and exits; `--connector <name>` runs one. No connector is named in `config.py` — scheduling is cadence-driven, so unlimited future connectors schedule with zero config edit.

**5.2 Execution.** For each selected connector: read cursor → `fetch(since)` → `normalize` → append idempotently (dedup by `connector|source_event_id#i`) → advance cursor **forward-only** (`hw >= cursor_before`, so a replay never rewinds).

**5.3 Verification (fail-closed).** `_verify_sync` asserts the five `SYNC_VERIFY_HARD_GATES` over the signals appended this run + cursor movement: `subject_resolves`, `provenance_present`, `secret_free`, `cursor_monotonic`, `signal_ids_unique` (unique + gapless across the whole ledger). A hard-gate failure exits non-zero (state not certified); the advisory `subject_resolved_nonfallback` gate is reported but non-blocking.

**5.4 Audit.** `_sync_audit_append` writes an append-only run record — `at`, stages, discovered connectors + import failures, per-connector `{status, events, new/dup signals, cursor_before, cursor_after, error?}`, verification map, result, and ledger total — into `sync-audit.json`, de-duping a consecutive no-op run so idempotent re-runs never grow the log (drift-free under `register.sh --guard`).

**5.5 Recovery.** Each connector runs inside its own try/except: on failure it is isolated, its cursor **preserved** (`cursor_after == cursor_before`) so the next run resumes exactly where it stopped, it is added to the run's `recovered` list, and every other connector's synchronization proceeds and still verifies.

**5.6 Roll-up.** After execution the runtime recomputes the twin (`_compute_twin`) and refreshes the control-tower dimensions (`_refresh_control_tower`) — so a new signal propagates to the Digital Twin and the Control Tower automatically (UKB-012).

---

## SECTION 6 — TWO-SURFACE CONVERGENCE (UMB-012 §2)

The Master Book has two synchronization surfaces, now both runtime-realized and converging on the same registers with **no competing store**:

| Surface | Runtime | Integration |
|---------|---------|-------------|
| **Artifact synchronization** | `register.sh` Atomic Transaction `T` (build → … → certify) | Phases 1,3–9 |
| **State synchronization** | `ukbx sync` (this artifact) | Phase **2/9** `ukbx sync --due` |

State synchronization is now a phase of the atomic transaction, so authoring OR external state changes both flow through one idempotent, gated, certified transaction (UMB-012 §5; REG-AUTO-001 §7).

---

## SECTION 7 — AUTOMATION DESIGN

`ukbx sync --due` is Phase 2/9 of `register.sh`, itself made unskippable by the UMB-IMP-001 authoring/commit/CI gates:

```
register.sh (Atomic Transaction T):
  Phase 0  ukb enforce --pre    ← UMB-IMP-001 pre-registration gate
  Phase 1  ukb build            ← identity, registry, typed edges, spine, change/version/lineage
  Phase 2  ukbx sync --due      ← LIVE CONNECTORS + AUTO SYNCHRONIZATION  ← UMB-IMP-004
  Phase 3  ukbx twin            ← digital twin + control tower
  Phase 4  ukbx portal          ← navigation portal
  Phase 5  ukb validate         ← structural + referential integrity
  Phase 6  ukbx validate        ← twin/signal integrity
  Phase 7  ukbx twin --check    ← certification = CERTIFIED 7/7
  Phase 8  ukb enforce          ← post-registration parity gate + audit
  Phase 9  seal
```

Because `--due` respects cadence and sync is idempotent, a steady-state transaction appends no signal, grows no audit log, and stays drift-free — while a real upstream change is detected, executed, verified, audited, and rolled into the twin with no manual step.

---

## SECTION 8 — TESTING / VERIFICATION DESIGN

| Test | Type | Result |
|------|------|--------|
| `ukbx sync --schedule` after adding `sonarqube.py` | discovery (infinite expansion) | **5 connectors discovered** with zero core edit; sonarqube cadence=1800s (PASS) |
| `ukbx sync` (first run) | integration (real corpus) | 5 connectors run; **+2 signals** from sonarqube; all 5 hard verify gates PASS |
| signal binding | positive | `USIG-000000013 → UCOS-IMP-000011` quality APPROVED; `USIG-000000014 → UCOS-IMP-000010` quality BLOCKED (real subjects) |
| twin propagation | positive | twin `quality` dimension = BLOCKED, `signal_source=SONARQUBE` (automated) |
| `ukbx sync` (re-run) | idempotency | **+0 new signals**, dedup; audit no-op (log unchanged) |
| `ukbx sync --due` post-run | scheduling | **0 connectors run** (cadence not elapsed) |
| recovery probe (raising `fetch`) | negative / recovery | failing connector **isolated**, cursor preserved, other connectors OK, run still VERIFIED |
| `cursor_monotonic` | invariant | no cursor regressed across runs (PASS) |
| `signal_ids_unique` | invariant | ledger ids unique + gapless `USIG-000000001..014` (PASS) |
| full `register.sh` (sync as Phase 2/9) | end-to-end | **CERTIFIED (hard checks 7/7)**; TRANSACTION COMPLETE |

---

## SECTION 9 — OPERATIONAL DESIGN

- **Normal operation:** `register.sh` (fired by the UMB-IMP-001 gates) runs `ukbx sync --due` as Phase 2; due connectors synchronize, verify, audit, and roll into the twin. Operators may also run `ukbx sync` (all), `ukbx sync --connector <name>` (one), or `ukbx sync --schedule` (plan).
- **Observability:** `DATA/sync-audit.json` (append-only run log), `signals.json` (append-only signals), `twin.json`/`control-tower.json` (refreshed dimensions).
- **Determinism & safety:** execution is idempotent (dedup by idempotency key); cursors advance forward-only; connectors are read-only against sources and append-only against the ledger; no secret is read, stored, or logged (RR-07 enforced by `make_signal`/`_secret_free` and the `secret_free` verify gate).
- **Extensibility operation:** to add a source, drop a `Connector` subclass file into `connectors/` (optionally declaring `cadence_seconds`); discovery + scheduling pick it up with no core edit. A live source swaps only `fetch` (and, for EVENT mode, a webhook entry point); `normalize`/`resolve`/verification/audit/recovery are unchanged.
- **Failure degradation:** a broken connector is isolated and reported; its cursor is preserved for the next run; the synchronization of all other connectors is unaffected — the twin is never left partially corrupted.

---

## SECTION 10 — ACCEPTANCE CRITERIA & SUCCESS GATE A

**Success Gate A (mission).**

| Gate A requirement | Status | Evidence |
|--------------------|--------|----------|
| Live source participation | MET | sonarqube connector emitted 2 signals bound to real subjects `UCOS-IMP-000010/011` |
| Automatic synchronization | MET | `ukbx sync` executes → verifies → rolls into twin (`quality` dimension automated) |
| Synchronization auditability | MET | append-only `sync-audit.json` run records (per-connector, cursors, verify map, result) |
| Synchronization recovery | MET | raising connector isolated, cursor preserved, others OK, run VERIFIED |
| No hard-coded connector limits | MET | `discover()` replaces the fixed 4-import list; nothing enumerates connectors |
| Infinite connector expansion | MET | new `sonarqube.py` discovered + scheduled with zero core edit; no ceiling (CR-INF-010) |

**Acceptance criteria.**

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| AC-1 | Discovery/monitor/detect/execute/verify/audit/recover realized | MET | Sections 4–5; live run |
| AC-2 | Scheduling is cadence-driven, list-free | MET | `--due`/`--schedule`; per-connector `cadence_seconds` |
| AC-3 | Verification fail-closed over signals + cursors | MET | 5 hard gates; exit non-zero on failure |
| AC-4 | Append-only audit, no-op-deduped | MET | `sync-audit.json`; drift-free under `--guard` |
| AC-5 | Recovery isolates failures, preserves cursors | MET | recovery-probe test |
| AC-6 | Zero hard coding / infinite expansion | MET | dynamic discovery; new connector zero-edit |
| AC-7 | No new registry/identifier/lifecycle/store | MET | reuse table (Section 3); audit is an operational log |
| AC-8 | Integrated into the atomic transaction, still certified | MET | Phase 2/9; `register.sh` CERTIFIED 7/7 |
| AC-9 | Compatible with STATUS-001/REG-AUTO-001/UCI-001/AUTH-INF-001/UMB-012/IMP-001..003 | MET | Section 11 |
| AC-10 | Exactly one artifact created | MET | only this `.md`; all logic is excluded machinery |

**Self-demonstration (populated by the registration run at the end of this mission).** Creating this file leaves it `GENERATED` (unregistered). Running the Atomic Registration Transaction registers it — allocating its append-only Universal ID, parenting it under `UMB-000`, recording its `Created` change event, its version record, and its `Evolves-From` lineage edge to `UMB-IMP-003` — while Phase 2 re-proves State-Synchronization and Phase 7 re-certifies `CERTIFIED (hard checks 7/7)`.

---

## SECTION 11 — COMPATIBILITY WITH GOVERNING STANDARDS

- **STATUS-001.** Declares STATUS DOMAIN + BASIS; a DOMAIN-C claim evidenced by code + live execution; asserts nothing about AI reasoning (IMP-005) or the certification runtime (IMP-006) (§2 non-projection).
- **REG-AUTO-001.** State synchronization is now Phase 2 of the atomic transaction `T`; every signal references its ingest run + evidence for reverse traceability (§7/§16).
- **UCI-001.** Introduces no registry, engine, identifier namespace, lifecycle, or state store; `sync-audit.json` is an append-only operational log and the twin/control-tower remain derived views (RP-4 no second synchronization; IP-3/IP-6 derived-not-stored).
- **AUTH-INF-001.** Connectors are pluggable and unbounded (CR-INF-003); no ceiling on connector count, event volume, or signal count (CR-INF-010); a new source is an append-only new file.
- **UMB-012 / UMB-IMP-001 / UMB-IMP-002 / UMB-IMP-003.** Realizes UMB-012 (auto-synchronization principle, two surfaces, connector model, enforcement, infinite scale, traceability); runs inside the UMB-IMP-001 transaction, over the UMB-IMP-002 registry/graph, and refreshes alongside UMB-IMP-003 change/version/lineage — from which it evolves (its own lineage edge).

---

## AUTHORITY BOUNDARY (MANDATORY)

UMB-IMP-004 holds no constituent, governance, ratification, or EC-series authority and cannot authorize EC-1. It is an implementation realization only, append-only, subordinate to the frozen constitutional corpus, the Technology Constitution, STATUS-001, REG-AUTO-001, UCI-001, AUTH-INF-001, UMB-000…020, UMB-IMP-001, UMB-IMP-002, UMB-IMP-003, and all prior determinations. It owns no synchronization semantics (REG-AUTO-001 / UMB-012 do); it creates no new architecture family, registry, identifier namespace, lifecycle, or synchronization engine; connectors are read-only against sources and append-only against the ledger, reference secrets only by external handle (RR-07), and never mutate canon; it renumbers nothing; it modifies no frozen or historical artifact; and it treats `00-SOURCE/`/`99-FREEZE/` as read-only. Per STATUS-001 §2, realizing this implementation capability projects no completion of any other domain. Any conflicting statement is void to the extent of the conflict.

## CERTIFICATION

| Attribute | Value |
|-----------|-------|
| Artifact Status | ACTIVE · IMPLEMENTATION |
| Evidence basis | Realized machinery + live execution (dynamic discovery of 5 connectors incl. zero-edit new connector, verified sync run +2 signals, idempotent re-run, cadence `--due` scheduling, recovery isolation proof, `register.sh` CERTIFIED 7/7 with sync as Phase 2/9) 2026-07-16 |
| Method | Reuse-first realization; reality-as-it-exists; no fabrication |
| Scope verdict | Fourth operational capability (live connectors + auto synchronization runtime) — REALIZED; Success Gate A MET |
| Append-only verdict | PASS — dynamic discovery + append-only signals + append-only sync-audit; cursors forward-only; derived views regenerated |
| Zero-hard-coding / infinite-expansion verdict | PASS — connectors discovered not enumerated; new connector participates with zero core edit; no ceiling |
| Authority | IMPLEMENTATION ONLY — NONE |

*Return: [UMB-000 Master Index](UMB-000-MASTER-BOOK-ARCHITECTURE-MASTER-INDEX.md) · [UMB-IMP-003](UMB-IMP-003-CHANGE-VERSION-AND-LINEAGE-INTELLIGENCE-REALIZATION.md) · [UMB-012 Synchronization](UMB-012-SYNCHRONIZATION-ARCHITECTURE.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*

**END OF ARTIFACT — UMB-IMP-004 · ACTIVE · IMPLEMENTATION · APPEND-ONLY · AUTHORITY-NEUTRAL · LIVE CONNECTORS AND AUTO SYNCHRONIZATION REALIZATION**
