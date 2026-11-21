# MCP-007 — MASTER RECOVERY (UCOS Ω∞)

| Field | Value |
|-------|-------|
| ARTIFACT ID | MCP-007 |
| ARTIFACT | Master Recovery — Session, Crash & Repository Recovery of UCOS Ω∞ |
| CLASSIFICATION | MCS COMPONENT 7 — recovery & continuity |
| STATUS | ACTIVE · LIVING |
| AUTHORITY | **NONE — DERIVED TRUTH.** Restores continuity from persisted state; asserts no authority. |
| ANSWERS | *How do we resume — after a stop, a crash, or a repository divergence?* |
| PART OF | Master Context System (`00-MASTER/`), governed by `MCS-000` |
| CHECKPOINT STORE | `00-MASTER/CHECKPOINTS/` (append-only) |
| BASELINE | 2026-07-18 · branch `governance-reconciliation` · HEAD `5874ede` |
| CONFLICT RULE | Where any statement conflicts with a higher frozen or governing instrument, the higher instrument governs. |

> **Scope.** MCP-007 makes continuity deterministic: any session — normal, interrupted, or crashed — resumes from persisted state (MCP-002) + the last checkpoint, without rediscovering context. It writes checkpoints only; it authors no state (that is MCP-002's).

---

## SECTION 01 — SESSION CONTINUATION CONTRACT (boot)

Every AI/engineering session **SHALL**, in order:

1. **Load MCP-001** (Master Context) — identity + rules.
2. **Load MCP-002** (Master State) — current state + Next Authorized Capability.
3. **Verify Git branch** — expect `governance-reconciliation` (`git branch --show-current`).
4. **Verify Git HEAD** — `git rev-parse HEAD`; compare to MCP-002 §01.
5. **Verify Working Tree** — `git status --porcelain`; reconcile against MCP-002 §01.
6. **Verify Repository Synchronization** — `git fetch` + ahead/behind vs `origin`.
7. **Verify Current Execution State** — read MCP-002 §01/§05.
8. **Load the execution ticket** — the Next Authorized Capability from MCP-003.
9. **Continue ONLY the authorized capability** — one logical capability at a time (`MCS-000 §05/§06`).
10. **Update state** — MCP-002 (§01/§05); MCP-003 transition; MCP-005 metrics; MCP-006 edges; MCP-004 if a decision was made.
11. **Checkpoint** — write `CHECKPOINTS/CKPT-<UTC>-<HEAD>.md` (§03).
12. **Commit** — one commit per logical capability, referencing its governing determination.
13. **End Session** — leave MCP-002 accurate so the next session continues without rediscovery.

> **Session start command block:**
> ```bash
> git branch --show-current && git rev-parse HEAD && git status --porcelain && git fetch --quiet && git rev-list --left-right --count origin/governance-reconciliation...HEAD
> ```

---

## SECTION 02 — RECOVERY DECISION TREE

Run at boot (steps 3–6) and whenever verification fails.

```
Is repository reachable?
 ├─ NO  → REPOSITORY RECOVERY (§05)
 └─ YES → Does branch == MCP-002 §01 branch?
     ├─ NO  → BRANCH DIVERGENCE (§04.A)
     └─ YES → Does HEAD == MCP-002 §01 HEAD (or a known descendant)?
         ├─ NO, ahead  → HEAD ADVANCED (§04.B): rebuild MCP-002 from git log since recorded HEAD
         ├─ NO, behind → HEAD BEHIND (§04.C): fast-forward or investigate reset
         └─ YES → Is working tree as MCP-002 §01 describes?
             ├─ NO  → WORKING-TREE DRIFT (§04.D): reconcile; uncommitted work = interrupted session
             └─ YES → BOOT CLEAN: continue Next Authorized Capability
```

---

## SECTION 03 — CHECKPOINT FORMAT

One checkpoint per completed (or interrupted) session, append-only, at `00-MASTER/CHECKPOINTS/CKPT-<UTC-timestamp>-<short-HEAD>.md`:

```
CHECKPOINT: CKPT-<UTC>-<HEAD>
SESSION OUTCOME: COMPLETED | INTERRUPTED | ABORTED
BRANCH / HEAD / SYNC: <verified values>
WORKING TREE: <git status --porcelain summary>
CAPABILITY WORKED: <MEP-NN>  STATE BEFORE→AFTER: <e.g. ACTIVE→IMPLEMENTED>
GOVERNING DETERMINATION: <ID>
ARTIFACTS TOUCHED: <paths>
VALIDATION: <tests/evidence run; pass/fail>
NEXT AUTHORIZED CAPABILITY (as left in MCP-002 §05): <text>
NOTES / RESUME HINTS: <anything the next session needs>
```

A checkpoint is a redundant, self-contained resume anchor: if MCP-002 were ever lost, the latest checkpoint + git log fully reconstruct state.

---

## SECTION 04 — RECOVERY PROCEDURES

**A. Branch divergence (on wrong branch).**
1. Do not commit. 2. `git stash` any accidental edits. 3. `git checkout governance-reconciliation`. 4. Re-run boot verification. 5. If work belongs on another branch, record the decision in MCP-004 before switching context.

**B. HEAD advanced (repo ahead of MCP-002).**
Another session committed and did not update MCP-002 (contract violation). 1. `git log <recorded-HEAD>..HEAD` to enumerate new commits. 2. Rebuild MCP-002 §01 (HEAD/tree/sync) + MCP-003 states from those commits + latest checkpoint. 3. Record the reconciliation in MCP-002 §06. 4. Continue.

**C. HEAD behind (repo behind MCP-002).**
Likely a reset/rollback. 1. `git reflog` to locate the recorded HEAD. 2. If intentional rollback, treat superseded capabilities per REOPEN (`MCS-000 §05`) and update MCP-003. 3. If accidental, restore via reflog. 4. Reconcile MCP-002; record in §06.

**D. Working-tree drift (uncommitted work present).**
Indicates an INTERRUPTED session. 1. Read the latest checkpoint (§03) for the capability in flight. 2. Diff uncommitted changes against the checkpoint's ARTIFACTS TOUCHED. 3. Either complete the capability (validate → update → checkpoint → commit) or `git stash`/discard if unrecoverable, recording the decision. 4. Never mix two capabilities in one commit.

---

## SECTION 05 — CRASH & REPOSITORY RECOVERY

**Crash recovery (session died mid-capability).**
- Truth survives in git + MCP-002 + checkpoints; nothing is held only in session memory (state-driven, not conversation-driven).
- Resume: boot (§01) → recovery tree (§02) → working-tree drift path (§04.D) using the last checkpoint.

**Repository recovery (local clone lost/corrupt).**
1. Re-clone `ABSOLUTE-FOUNDATION`. 2. `git checkout governance-reconciliation`. 3. Boot (§01). 4. MCP-002 + latest checkpoint restore full operational context — no rediscovery, no re-audit.

**Origin loss (remote unavailable).**
- Local clone + committed MCS state remain authoritative for continuity; defer `git fetch`/sync verification, record R-SYNC-UNAVAILABLE risk in MCP-002 §03, and continue local-only additive work.

**Guarantee.** Because state is persisted (MCP-002), append-only (checkpoints), and git-versioned, recovery is deterministic: the same repository + checkpoints always reconstruct the same operational context and the same Next Authorized Capability.

---

## SECTION 06 — CHANGE LOG (MCP-007 only)

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-18 | MCP-007 established as MCS component 7 (continuation contract + recovery decision tree + checkpoint format + crash/repository recovery) | Mission MCP-002 decomposition (migrated from root §11; recovery model added) |

*Append on any change to recovery procedure or checkpoint format.*

---

*END OF ARTIFACT — MCP-007 · MASTER RECOVERY · ACTIVE · LIVING · AUTHORITY = NONE (DERIVED TRUTH)*
