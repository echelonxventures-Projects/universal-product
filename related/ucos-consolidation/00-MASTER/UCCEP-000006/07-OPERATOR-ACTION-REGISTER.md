# Output 7 — Operator Action Register

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000006` |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| PURPOSE | The complete set of acts this programme may **not** perform, with owner, exact steps, and acceptance criteria |
| REPOSITORY | HEAD `527485abf00f241a035dbd06062b78c1d9dcde31` · branch `programme/evo-usis-005` · tree DIRTY 127 |

> Every action below is owned by a party other than this programme. None was performed here.
> `OA-1` in particular is an irreversible act on shared history over an uncommitted
> meta-constitutional zone — an operator decision, not an agent decision.

---

## 1. Register

| # | Action | Owner | Discharges | Priority | Blocking | Status |
|---|---|---|---|---|---|---|
| **OA-1** | Atomic registration commit + `MCP-002` reconciliation | repository operator | O-01 · `UCCEP-F-007` · `WP-UCCEP-005` · **C-1** | **P0** | **YES — suspensive** | **OPEN** |
| **OA-2** | Record `UCCEP-F-003` as discharged in the bindings and regenerate the findings register | UCCEP-000000 / `engine/graph` | O-02 · `UCCEP-F-003` · **C-2** | **P1** | No (bars certification claims) | **OPEN** |
| **OA-3** | Install `jsonschema` so `ukb validate` runs full schema validation | `00-BOOK/tools/ukb.py` · CI workflow | `UCCEP-F-006` · `WP-UCCEP-004` | P2 | No | **OPEN** |
| **OA-4** | Close the traceability completeness gap (≈22.7% → target) | CEP-008 · `platform/measurement` · `engine/graph` | `UCCEP-F-002` · `WP-UCCEP-002` | P2 | No (advisory `CK-HEALTH`) | **OPEN** |
| **OA-5** | Make the phase-3 closure verdict measured rather than constant | UAKOS-CLOSURE successor programmes | `UCCEP-F-001` · `WP-UCCEP-001` | P3 | No (advisory `CK-CLOSURE-P3`) | **OPEN** |
| **OA-6** | Constitute a Tier T1 authority competent to ratify | **external constituent act** | O-04 · `UCCEP-F-004` | — | No (standing ceiling) | **NOT ACTIONABLE IN-REPOSITORY** |
| **OA-7** | Refresh stale CI signals (dated 2026-07-15, predating HEAD) | MEP-08 CI signal refresh | `R-CI-STALE` (MCP-002 §risk) | P3 | No | **OPEN** |

---

## 2. OA-1 — Atomic registration commit (P0 · BLOCKING)

**Why it is P0.** Until this is done, Repository Truth is split from committed history: the
meta-constitutional zone, the constitutional register, and the evidence package that justifies
the authorization all exist only in the working tree. There is no committed baseline to roll
back to, so no implementation mutation is permitted (Output 6 RB-1).

### 2.1 Scope to review — 127 entries

| Class | Count | Notable content |
|---|---|---|
| Modified | 75 | `00-BOOK/tools/config.py` (`RECONCILED_SETS`) · `00-BOOK/tools/ukb.py` · `engine/graph/validation.py` · `engine/tests/graph/test_validation.py` · `00-CEP/CEP-001`, `CEP-002` · `Makefile` · `00-BOOK/DATA/*` · registry projections · intelligence outputs |
| Untracked | 52 | **`00-CMG/`** (entire meta-constitutional zone) · **`00-MASTER/UCCEP-000000/`** (constitutional register) · **`00-MASTER/UCCEP-000005/`** (the handover package) · 37 `00-BOOK/PORTAL/*` projections · `00-MASTER/UCOS-{ACE,CCD,NUCLEUS}-001/` · USIS-WAVE3 determinations · `.github/workflows/uccep-gate.yml` · `.kiro/hooks/uccep-000000.json` |

Full listing: `evidence/worktree.txt`.

### 2.2 Steps

1. **Review** all 127 entries. Two require deliberate judgement:
   - `00-CMG/` — committing it makes the meta-constitutional zone Repository Truth. That is a constitutional act with standing consequences, not a housekeeping commit.
   - `config.py` / `ukb.py` `RECONCILED_SETS` — changes registration recognition behaviour (zone `^00-CMG/`, namespace `CMG`, owner `CMG-000001`).
2. **Regenerate projections** so source and projections agree at the moment of commit.
3. **Commit atomically** — source **and** projections in one commit (REG-AUTO-001: source is never split from projections). Name specific paths; do not blanket-stage.
4. **Reconcile `MCP-002` §01** to the new HEAD per MCP-007 §04.B. It currently records the pre-programme `EC3-B13-U11` lineage (boot HEAD `b921376`), not `527485a` — see OBS-3.
5. **Verify** (acceptance criteria below).
6. **Record** the resulting commit SHA as the UCCEP-000007 rollback anchor (Output 6 RB-1).

### 2.3 Verification commands

```
git status --porcelain | wc -l                        # expect 0 (or only intentional residue)
python3 00-BOOK/tools/ukb.py enforce --pre            # expect exit 0
python3 00-BOOK/tools/ukb.py validate                 # expect exit 0
./register.sh --guard                                 # expect 10/10 CERTIFIED, zero drift
./verify.sh                                           # expect exit 0
python3 -m engine.graph.cli validate                  # expect exit 0, dependency_cycle = []
python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier full --gate   # expect exit 0
```

### 2.4 Acceptance criteria

| # | Criterion |
|---|---|
| A-1 | `CK-REG-DRIFT` → **PASS** (no longer exit 3) |
| A-2 | `G-07` Registry → **PASS** |
| A-3 | Full-tier aggregate gate → exit **0**, blocking failures **none**, 13/13 gates PASS |
| A-4 | `G-08` still **PASS**; `dependency_cycle` still `[]`; `scc_gt1_count` still **0** |
| A-5 | Registration parity preserved — 1199 = 1199, 0 unregistered / unclassified / invalid |
| A-6 | `id-ledger.json` digest unchanged (`be97eb9f…`) unless identifiers were legitimately allocated through the governed path |
| A-7 | `MCP-002` §01 HEAD equals the new HEAD |
| A-8 | Source and projections in the **same** commit — verifiable from the commit contents |

### 2.5 Cautions

- **Irreversible on shared history.** Prefer a normal commit; no `--amend`, no history rewriting.
- **No `git add -A`.** Stage named paths so nothing unintended enters the constitutional record.
- **Secrets check.** 52 untracked entries were not individually screened by this programme for credential material; screen before committing.
- **Do not skip hooks.** The registration gate exists to catch exactly this class of drift.

---

## 3. OA-2 — Record `UCCEP-F-003` as discharged (P1)

| Item | Detail |
|---|---|
| File | `00-MASTER/UCCEP-000000/uccep-bindings.json` |
| Current | `UCCEP-F-003` → `disposition: "GOVERNED"`, `blocking: true`, `work_package: "WP-UCCEP-003"` |
| Required | disposition recorded as discharged/remediated, `blocking: false`, with the discharging evidence referenced |
| Evidence available | `dependency_cycle = []` · `CK-GRAPH` PASS · `G-08` PASS · fail-closed negative path exit 1 demonstrated · UCCEP-000005 `evidence/post/T-1-eng-chain-edges.json`, `T-2-validation-gate.diff` |
| Then | regenerate `17-ASSIMILATION-FINDINGS-REGISTER.md` and the `certification_ceiling` in `uccep.json` |
| Acceptance | the live ceiling no longer names `UCCEP-F-003`; aggregate verdict unchanged or improved |
| Note | UCCEP-000005 declined this act because it is another programme's declaration. This programme declines it for the same reason (Output 6 X-9) |

---

## 4. OA-6 — Tier T1 authority (NOT ACTIONABLE IN-REPOSITORY)

| Item | Detail |
|---|---|
| Facts | `CMG-000001` PROVISIONAL · constitutional Tier T1 **VACANT** · CEP-006 names no existing competent authority |
| Consequence | every verdict in this corpus — including this authorization — is capped at `CERTIFIED-PROVISIONAL` |
| Correct handling | **disclosure**, per condition C-3. It cannot be manufactured, and no in-repository act can substitute for it |
| What must not happen | no programme may self-ratify, and no artifact may present a provisional verdict as ratified |

---

## 5. Register summary

| Measure | Value |
|---|---|
| Actions registered | **7** |
| Blocking | **1** — OA-1 |
| Performed by this programme | **0** |
| Not actionable in-repository | **1** — OA-6 |
| New work packages created | **0** — every action maps to an existing `WP-UCCEP-00x` or an existing finding |

**Next act in the programme sequence: OA-1.** It is one operator act, it is the sole
suspensive condition, and every dependency precondition behind it is already satisfied and
evidenced.
