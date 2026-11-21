# 17 — Repository Baseline Record

> PROGRAM **UCOS-AB-001** · PHASE-001 · ARCHITECTURE BASELINE v1.0
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Record the immutable, reproducible repository facts that anchor baseline v1.0, so the baseline can be verified and reproduced at any future time. This is the physical seal record for doc 08 v1.0.

## 1. Repository Anchor

| Field | Value | Source |
|---|---|---|
| Git HEAD (verifiable) | `b67a720` | `git rev-parse HEAD` |
| Branch | `governance-reconciliation` | `git rev-parse --abbrev-ref HEAD` |
| Origin | `ABSOLUTE-FOUNDATION` | MCP-002 §01 |
| Foundational corpus | `00-SOURCE/` (13 FROZEN + 2 FINAL) | `99-FREEZE/FREEZE-NOTICE.md` |
| Corpus hash set | `99-FREEZE/SOURCE-HASHES.txt` | 99-FREEZE |
| Guard integrity | 10/10 domains CERTIFIED (at frontier) | `register.sh --guard` (MCP-002) |

## 2. Derived-State Snapshot (AUTHORITY=NONE, evidence: MCP-002/005)

| Metric | Value (captured) | Source | Caveat |
|---|---|---|---|
| Registered artifacts | 990 (realization frontier) / baseline anchor at `b67a720` | Control Tower | regenerate before authoritative quoting |
| Pages | 8,988 | Control Tower | as captured |
| Volumes | 24 | Control Tower | as captured |
| Relationships | 10,732 | Control Tower | 2026-07-18 |
| EC-2 test suite | 2,677 pass / 0 fail (local) | EC-2 | post-dates stale CI |
| Freeze gate | 2,847 pass / 100% cov | band evidence | preserved across bands |

> These figures are **derived** and time-stamped; per repository discipline they must be regenerated (`ukb build` / Control Tower) before being quoted as current. The baseline anchors to the git HEAD, not to any single captured figure.

## 3. Reproducibility Method

Baseline v1.0 is reproducible by:
1. checkout `b67a720` on `governance-reconciliation`;
2. verify `00-SOURCE` against `99-FREEZE/SOURCE-HASHES.txt`;
3. run `register.sh --guard` → expect 10/10 CERTIFIED, zero drift;
4. re-derive the inventory (docs 02/03) → expect identical lifecycle states;
5. confirm frozen band baselines (`deb2694f…`, `beff9ed3…`) intact.
A matching result reproduces the baseline; a mismatch is drift (Change Control / reconciliation).

## 4. HEAD vs Operational-Memory Divergence (recorded)

`git HEAD = b67a720`; operational memory (MCP-002/005) narrates realization commits through EC3-B13-U11. Per MCP-007 boot contract, such divergence is reconciled at next boot by enumerating descendant commits. This record anchors to the **verifiable HEAD** and flags the operational-memory frontier as derived; it fabricates no merged anchor (fail-closed).

## 5. Read-Only Attestation

This program created only new files under `00-MASTER/UCOS-AB-001/`. It modified no `00-SOURCE`, `99-FREEZE`, `engine`, `platform`, `data`, `service`, `application`, `infrastructure`, `00-CEP`, `02-MASTER`, or prior `00-MASTER` artifact. Verification: `git status` shows only the new `UCOS-AB-001/` directory (doc 20 §repository modification).

## 6. Determination

**REPOSITORY BASELINE RECORD IS SEALED (read-only).** The verifiable anchor, derived snapshot (with caveats), reproducibility method, and divergence note are recorded. Baseline v1.0 is reproducible from `b67a720` + `99-FREEZE` hashes. No repository artifact was modified.

*END — 17 · UCOS-AB-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
