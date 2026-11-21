# IMPLEMENT-001B · DELIVERABLE 05 — REPOSITORY IMPACT ASSESSMENT

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001B` |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| SUBJECT | Impact of the disposition set on the repository, its registries, dependencies and certification |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DISPOSITION SUMMARY — one formal disposition per finding

| Finding | Validity | Classification | **Disposition** | Blocking? |
|---|---|---|---|---|
| **C-1a** `00-BOOK/tools/config.py` | **INVALID** | False positive · expected behaviour | **REJECT** | No |
| **C-1b** `00-BOOK/SCHEMAS/` ×13 | **PARTIALLY VALID** | Mixed — permitted write, uncommitted registration | **ACCEPT** (reclassified) → discharged by `OA-1` | No |
| **C-1c** `frozen_paths.py` over-breadth | **VALID (new)** | Implementation defect · constitutional conflict | **FIX** | No |
| **C-1d** `platform/**` ×7 | **VALID (new)** | Repository defect — P-7 work package absent | **FIX** | No |
| **C-2** `repo-ops.sh` acceptance | **PARTIALLY VALID** | Intentional behaviour · tooling limitation · incomplete implementation | **WAIVE** (+ disclosure) | No |
| **C-3** Stage 5 schema half | **VALID / ALREADY SATISFIED** | Tooling limitation — registered as `UCCEP-F-006` | **DEFER** to `WP-UCCEP-004` | No |
| **C-4** `EIP-018 (FP-N)` | **INVALID as reported** | False positive; narrow residue merged into C-1d | **REJECT** (residue → `RB-02`) | No |
| **C-5** `rib.json` non-convergence | **VALID (new)** | Implementation defect | **FIX** (deferred) | No |

**8 findings · 8 dispositions · 1 REJECT×2 · 1 ACCEPT · 3 FIX · 1 WAIVE · 1 DEFER · 0 blocking.**

> ### Of the four findings `IMPLEMENT-001A` declared BLOCKING, **zero survive as blocking.**
> Two were rejected outright (C-1a, C-4), one was reclassified and is discharged by the commit
> (C-1b), one was waived as correct behaviour (C-2), and one was already registered non-blocking
> by its owner (C-3). Three genuinely new findings were discovered (C-1c, C-1d, C-5) and none is
> blocking either.

---

## 2. IMPLEMENTATION IMPACT

| Item | Code change required | Lines | Surface |
|---|---|---|---|
| C-1a | **NONE** | 0 | — |
| C-1b | **NONE** | 0 | — |
| **C-1c** | Narrow `FROZEN_PREFIXES`, **or** extend the `ec1-ci.yml` exclusion to `SCHEMAS/` + `tools/` | ~2 | `engine/foundation/guards/frozen_paths.py:17` **or** `.github/workflows/ec1-ci.yml:96-97` |
| **C-1d** | **NONE to code** — record only | 0 | one work-package entry |
| C-2 | **NONE** — the code is correct as written | 0 | — |
| C-3 | Pin `jsonschema`; drop `\|\| true` | 2 | `pyproject.toml:27-32` · `ucos-registration-gate.yml:40` |
| C-4 | **NONE** — removal would regress `GOV-002` `RA5` traceability evidence | 0 | — |
| C-5 | Exclude `dirty_paths` from the persisted artifact, or compute over committed HEAD only | ~5 | `00-MASTER/UCOS-RIB-001/rib_engine.py` |

> **Total code change across all eight dispositions: ~9 lines**, in three files, none of which
> is in the current change set. **Zero lines of the 86 modified files require revision.**

`C-1c` is itself a **P-7** corrective mutation (`frozen_paths.py` is in `engine/**`) and must
carry its own work package and negative-path demonstration — the guard must be shown still
failing closed on `00-SOURCE/` and `99-FREEZE/`.

---

## 3. REPOSITORY IMPACT

### 3.1 Registry impact

| Registry | Impact | Discharged by |
|---|---|---|
| `artifacts.json` | **13 stale `content_hash`** — `UCOS-REG-0000{01,03,04,06,07,09,11,12,13,14,16,17,19}`. Verified by re-hashing each file on disk against the recorded hash. | `OA-1` atomic registration commit |
| `id-ledger.json` | **NONE.** 0 identifiers allocated by this mission or by the change set. Append-only identity intact. |
| `relationships.json` | **NONE.** 12,829 edges / 1,218 nodes unchanged; 0 cycles. |
| `twin.json` | **NONE.** 15 signals / 8 subjects unchanged. |
| `change-ledger.json` | Append-only; unaffected. |
| `control-tower.json` | Regenerated projection; unaffected until registration. |
| Eligible-vs-registered parity | **1,193 ≡ 1,193 · 0 unregistered · 0 unclassified · 0 invalid** — verified 3× this mission |

**Critical:** the 13 stale hashes mean the working tree currently holds the **source/projection
split that `REG-AUTO-001` forbids**. Withholding the commit *sustains* that violation. This
inverts `IMPLEMENT-001A`'s commit-readiness conclusion.

### 3.2 Corpus impact

| Property | Value | Change |
|---|---|---|
| Registered artifacts | 1,193 | unchanged |
| `00-SOURCE/` + `99-FREEZE/` | `git status` → **0 entries** | **UNTOUCHED — X-1 intact** |
| `00-CEP/` | `git status` → **0 entries** | **UNTOUCHED — X-2 intact** |
| `00-BOOK/DATA/id-ledger.json` | unmodified | **X-4 intact** |
| `00-BOOK/DATA/*` ledgers | unmodified | **X-5 intact** |
| Canonical concepts | 440, all homed, 0 gaps | unchanged |
| Tracked decisions | 89, 0 undispositioned | unchanged |
| Duplicate canonical objects | **0** | unchanged |

> **Every genuinely protected area (X-1, X-2, X-4, X-5) is untouched.** The writes that occurred
> fall in `00-BOOK/SCHEMAS/`, `00-BOOK/tools/` and `platform/**` — of which only `platform/**`
> (X-8) is a protected area, and it has a permitted route (P-7) whose substantive conditions are met.

### 3.3 Files added by this mission

6 files under `00-MASTER/IMPLEMENT-001B/`. Registration impact: **0** — `00-MASTER/` is a declared
corpus-internal exclude (`EXCLUDE_DIR_PREFIXES`, consumed at `ukb.py:820-824`), so 0 of 1,193
registered artifacts live there and `enforce --pre` reports `eligible = registered = 1193`
unchanged. Verified after writing.

**Disclosed side effect:** raises the untracked entry count and therefore `UCOS-RIB-001`'s
`dirty_entries` and `UCOS-RFP-001`'s `CLO-01` count. Both are discharged by the commit. This is
also a live instance of **C-5**.

---

## 4. DEPENDENCY IMPACT

| Dimension | Assessment |
|---|---|
| New dependencies introduced by the dispositions | **1** — `jsonschema` (pinned), under `C-3`/`WP-UCCEP-004`. Already a de-facto runtime dependency of Stage 5; declaring it removes an undeclared one. |
| Dependency cycles | **0** over 12,829 edges / 1,218 nodes (`engine.graph.cli validate`, `dependency_cycle: []`, exit 0) |
| Dangling `dependencies[]` / `parent` references | **0** (`ukb.py validate` referential integrity) |
| Inter-finding dependencies | `C-4` residue **depends on** `C-1d`'s work package (same artifact). `C-2.1` disclosure is independent. `C-1c` and `C-5` are independent. |
| Ordering constraint | `RB-01` (`C-1c`) must precede any push, or the CI DP-03 step rejects the branch. `RB-02` (`C-1d`) must precede or accompany the commit to satisfy P-7. |
| Consumers of changed surfaces | `ec1-frozen-guard` console script (`pyproject.toml:36`) and `repo-operations.json` freeze stage both consume `frozen_paths`. Both are covered by existing tests, so `RB-01` is test-protected. |
| Blast radius of `RB-01` | Contained: 1 constant, 2 consumers, existing test coverage. |

---

## 5. CERTIFICATION IMPACT

### 5.1 The arithmetic changes

| | `IMPLEMENT-001A` | `IMPLEMENT-001B` (verified) |
|---|---|---|
| Blocking findings | **4** (C-1…C-4) | **0** |
| Findings requiring code | 4 | **3**, totalling ~9 lines, **none in the change set** |
| Constitutional violations | 1 asserted (DP-03) | **0 substantiated** — the DP-03 claim rests on a guard broader than its own authority |
| Findings already registered elsewhere | 0 recognized | **1** (C-3 = `UCCEP-F-006`, non-blocking P2) |
| Findings that are correct behaviour | 0 recognized | **1** (C-2 — replaced two vacuous passes) |
| Genuinely new findings | — | **3** (C-1c, C-1d, C-5) |
| Commit readiness | **BLOCKED** | **AUTHORIZED** (Deliverable 07) |

### 5.2 Gate state — unchanged by this mission

| Gate | Exit | Verdict |
|---|---|---|
| `verify.sh` | **0** | 5/5 PASS · coverage 94.28% · run 3× this mission, identical |
| `make uccep-gate` | 0 | `CERTIFIED-PROVISIONAL` · blocking=none · unproven=none |
| `make closure-gate` | 0 | `CLOSED` · 440 concepts · gaps 0 |
| `make ucda-gate` | 0 | `ASSIMILATED` · 89 decisions · 0 undispositioned |
| `urrc` / `uer` / `uei` / `umk` / `uprf` | 0 | all PASS |
| `make rib-gate` | 1 | dirty tree only (`VAL-02`/`GATE-12`, both `dirty_entries_outside_generated`) → discharged by the commit |
| `make rfp-gate` | 1 | `CLO-01` fail-closed abort on a dirty tree → discharged by the commit |
| `repo-ops.sh` | 1 | `architecture-freeze` → `RB-01`; `repository-acceptance` → **WAIVED** |

### 5.3 Certification determination

`RELEASE-001` §4 requires seven gates. **All seven pass** (Stage 5 qualified by `CF-03`).
`RELEASE-001` §1 requires, for `CERTIFIED`: *"UCCEP blocking=none + evidence recorded."*

- UCCEP `blocking=none` ✓ (verified)
- Evidence recorded — **this deliverable set is that evidence**, plus `RB-02`'s work package

> **Certification is attainable.** It requires `RB-01` and `RB-02` — two acts, ~2 lines and one
> record — not a constitutional amendment. See Deliverable 08.

---

## 6. RISK OF THE DISPOSITIONS THEMSELVES

Dispositions can be wrong. Each is stress-tested against the cost of being wrong.

| Disposition | If this disposition is wrong… | Mitigation |
|---|---|---|
| **REJECT C-1a** | `config.py` would be an unauthorized corpus write | Low risk: `REG-AUTO-001` §2 names `00-BOOK/tools/` out of scope, §3 P3 names `config.py` a declared input, 0/1193 registered, ≥10 prior commits. Reversible by `git checkout`. |
| **ACCEPT C-1b** | The schemas would need reverting | Reverting restores **539 schema violations** and breaks `verify.sh` Stage 5 — a strictly worse state. The widening is provably admits-only (0 regressions). Reversible pre-commit. |
| **WAIVE C-2** | A real gate failure would go unaddressed | Bounded: bound to no gate anywhere; the alternative (restore `covered:1/total:1`) is a gate that cannot fail. `RB-04` records the expected-fail so it cannot be forgotten. |
| **DEFER C-3** | Schema validation stays optional | Already the owner's determination (`blocking: false`, P2). Locally jsonschema **is** installed and Stage 5 runs in full. `CF-03` bars release claims until closed. |
| **REJECT C-4** | Unattributable code would be committed | The genuine attribution gap is preserved as `C-1d`/`RB-02`, which is **blocking-for-P-7** and must be discharged. Nothing is lost by rejecting the identifier framing. |
| **FIX C-1c** | The guard would be loosened wrongly | `RB-01` requires demonstrating the guard still fails closed on `00-SOURCE/` and `99-FREEZE/` — X-1 protection is preserved by construction. |

**Highest-consequence disposition:** `FIX C-1c`, because it loosens a security guard. It is
therefore the one item with a mandatory negative-path proof obligation.

---

## 7. DETERMINATION

> **Repository impact: MINIMAL. Certification impact: DECISIVE.**
>
> ~9 lines of code across three files, none of them in the 86-file change set. One work-package
> record. One disclosure record. Every genuinely protected area (X-1, X-2, X-4, X-5) is
> untouched; `00-SOURCE/`, `99-FREEZE/` and `00-CEP/` show **0** `git status` entries.
>
> The 13 stale `content_hash` values are the one real repository defect, and the act that fixes
> them is the commit `IMPLEMENT-001A` withheld.

---

*END — `IMPLEMENT-001B` Deliverable 05 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
