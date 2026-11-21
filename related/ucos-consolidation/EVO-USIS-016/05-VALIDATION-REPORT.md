# EVO-USIS-016 · 05 — Validation Report

| Field | Value |
|-------|-------|
| PROGRAMME | EVO-USIS-016 — Evidence Architecture Implementation |
| PHASE | 4 — Validation |
| RESULT | PASS on all integrity validators; commit-time drift gate reported (see §Guard) |

## Executed commands & results

| Command | Result (Repository Truth) |
|---------|---------------------------|
| `./doctor.sh` | ENVIRONMENT READY — python 3.12, pytest 8.3.4, pytest-cov 6.0.0, coverage 7.15.2, ruff 0.8.4 (exit 0) |
| `./verify.sh` | VERIFICATION PASSED — ruff lint+format (engine+platform), pytest+coverage gate `--cov-fail-under=90` (TOTAL 97%), coverage report, governance `enforce --pre` (run #465); 30s wall (exit 0) |
| `./00-BOOK/tools/register.sh` | TRANSACTION COMPLETE — 1155 artifacts (exit 0) |
| `ukb.py validate` | VALIDATION PASSED — 1155 artifacts, append-only intact, referential integrity OK |
| `ukb.py enforce` | ENFORCEMENT PASSED — 1155 = 1155; unregistered 0; unclassified 0; invalid 0 (audit run #464) |
| `ukbx.py validate` | TWIN VALIDATION PASSED — 15 signals, provenance present, secret-free |
| `ukbx.py twin --check` | CERTIFIED — hard checks 7/7 |
| `./00-BOOK/tools/register.sh --guard` | Transaction COMPLETE; drift gate = uncommitted synchronized register set (exit 3) — see §Guard |

## Verified integrity properties

| Property | Verified by | Result |
|----------|-------------|--------|
| Repository integrity | `ukb validate` + `ukbx certify` domain 2 | PASS |
| Registry integrity | append-only; count parity 1155=1155 | PASS |
| Knowledge Once | No-Orphan + referential integrity; unclassified 0 | PASS |
| Dependency closure | every Depends-On endpoint resolves (C-05); 42 edges / 0 unresolved | PASS |
| Evidence integrity | content-addressed identity + no-drift guard (CEP-008 IX); `ukbx certify` Identity/Registry/Change domains | PASS |
| No duplicate knowledge | Zero-Duplication (LAW USIS-02; CEP-008 XVI.2); references only | PASS |
| No orphan artifacts | navigability + return path (C-08) | PASS |
| No broken lineage | parent/child edges resolve; portal reachable; lineage acyclic (CEP-008 XII) | PASS |

## Guard (commit-time drift gate)

`register.sh --guard` completed the transaction, then reported drift (exit 3): the regenerated synchronized register set is not yet committed to git (REG-AUTO-001 §16 gate-2 — an *uncommitted-state* signal, **not** an integrity defect; every integrity validator PASSED). The delta comprises USIS-016 plus the still-uncommitted USIS-014/USIS-015 and prior Wave-2 batch (untracked portal pages `UCOS-USIS-000014…000019` observed). Remediation = stage + commit the synchronized set (a git action pending explicit authorization per repository git-safety policy); post-commit `--guard` returns exit 0.

## Determination

**PHASE 4 PASS (integrity).** Repository, registry, Knowledge-Once, dependency-closure, evidence-integrity, zero-duplication, zero-orphan, and lineage are proven. The sole open item is the commit-time drift gate (human-gated git commit).
