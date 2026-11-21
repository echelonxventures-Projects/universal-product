# 53 — Operational Execution Model (Phase-004)

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-004 |
| STATUS | PLANNING / GOVERNANCE — no implementation artifact modified |
| AUTHORITY | NONE — DERIVED TRUTH |
| BASELINE | HEAD `b67a720` |

## 1. Execution order (deterministic DAG)

```
S1 ingest → S2 extract → S3 match → S4 graph(P2) → S6 gaps → S7 plan
                                         ↘ S5 traceability (MCP-006)
S8 validate (CEP-004 / ukb validate) → S9 certify (CEP-005 / CCE) → S10 closure determination
```
Phase-N never runs before its upstream JSON model exists; Phase-002 requires a present `closure.json` (interface contract §1).

## 2. Policies

| Policy | Rule |
|--------|------|
| **Retry** | Idempotent: re-running at the same HEAD is safe and produces identical bytes. No partial-write state (whole-file emit). |
| **Failure** | Fail-closed. A gate returns non-zero (`--gate`); the closure certificate is withheld. Upstream artifacts are never corrupted on failure. |
| **Evidence** | Append-only, cite-don't-copy. Authoritative evidence (`15`, `19`, ukb runs) preserved verbatim; derived reports reference it. |
| **Determinism** | `UCKO-PRIN-0005`: identical inputs at identical HEAD → byte-identical outputs. Git commit is the baseline stamp; no wall-clock in canonical content. Verified by `determinism.yml`. |
| **Idempotency** | Re-emit overwrites derived reports with identical content; no accumulation, no duplication. |
| **Compatibility** | `closure.json` = interface contract v1; additive fields only; renames/removals require version bump + Phase-002 sign-off. |
| **Versioning** | Recommend explicit `schema_version` + `scan_mode` on `closure.json` (contract §5); phase engines stamp `baseline_commit`. |
| **Rollback** | Tracked files → git. **Operational-memory tooling under `00-MASTER/` is git-untracked → no git rollback; a tar snapshot MUST precede any destructive change** (consolidation precondition). |
| **Recovery** | Follow `MCP-007` recovery pattern: reuse existing evidence, never duplicate; re-run deterministically from the last good HEAD. |

## 3. Scan-mode discipline (resolves the observed 398↔506 flux)

- **Canonical `closure.json` = full-corpus run** (includes external conversation/upload concepts).
- Fast repo-only pass (`CLOSURE_SKIP_CORPUS=1`) is for local iteration and SHOULD write a separate `closure.repo-only.json` (recommended; not yet implemented — interface change, requires sign-off).
- Until implemented: document which mode last wrote `closure.json`; Phase-002 figures inherit that mode.

## 4. Concurrency rule

The pipeline directory may have concurrent writers across phases. Therefore: **no phase renames/deletes/moves another phase's artifacts**; each phase owns its own numbered outputs + JSON model; cross-phase communication is via the read-only JSON contract only.

---

*END — 53 · Operational Execution Model · AUTHORITY = NONE.*
