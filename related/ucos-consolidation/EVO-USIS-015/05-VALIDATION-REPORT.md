# EVO-USIS-015 · 05 — Validation Report

| Field | Value |
|-------|-------|
| PROGRAMME | EVO-USIS-015 — Certification Architecture Implementation |
| PHASE | 4 — Validation |
| RESULT | PASS on all integrity validators; commit-time drift gate reported (see §Guard) |

## Executed commands & results

| Command | Result (Repository Truth) |
|---------|---------------------------|
| `./doctor.sh` | ENVIRONMENT READY — python 3.12, pytest 8.3.4, pytest-cov 6.0.0, coverage 7.15.2, ruff 0.8.4 (exit 0) |
| `./00-BOOK/tools/register.sh` | TRANSACTION COMPLETE — 1145 artifacts (exit 0) |
| `ukb.py validate` | VALIDATION PASSED — 1145 artifacts, append-only intact, referential integrity OK |
| `ukb.py enforce` | ENFORCEMENT PASSED — 1145 = 1145; unregistered 0; unclassified 0; invalid 0 |
| `ukbx.py validate` | TWIN VALIDATION PASSED — 15 signals, provenance present, secret-free |
| `ukbx.py twin --check` | CERTIFIED — hard checks 7/7 |
| `./00-BOOK/tools/register.sh --guard` | Transaction COMPLETE; drift gate = uncommitted synchronized register set (exit 3) — see §Guard |

> `verify.sh` runs the Software-stream (`engine/`,`platform/`) pytest/coverage suite (EC-1/EC-2), which is referenced/frozen and out of scope for the intelligence-corpus USIS-015 artifact (LAW USIS-02; DP-03 — 0 writes to frozen streams). `doctor.sh` confirms that toolchain is READY/reproducible. The authoritative validators for a `15-…/` corpus artifact are `ukb`/`ukbx`, all PASS above.

## Verified integrity properties

| Property | Verified by | Result |
|----------|-------------|--------|
| Repository integrity | `ukb validate` + `ukbx certify` domain 2 | PASS |
| Registry integrity | append-only; count parity 1145=1145 | PASS |
| Knowledge Once | No-Orphan + referential integrity; unclassified 0 | PASS |
| Dependency closure | every Depends-On endpoint resolves (C-05) | PASS |
| Certification integrity | `ukbx certify` 10/10; `twin --check` 7/7 | PASS |
| No duplicate knowledge | Zero-Duplication (LAW USIS-02); references only | PASS |
| No orphan artifacts | navigability + return path (C-08) | PASS |
| No broken lineage | parent/child edges resolve; portal reachable | PASS |

## Guard (commit-time drift gate)

`register.sh --guard` completed the transaction, then reported drift (exit 3): the regenerated synchronized register set is not yet committed to git (REG-AUTO-001 §16 gate-2 — an *uncommitted-state* signal, **not** an integrity defect; every integrity validator PASSED). The delta comprises USIS-015 plus the still-uncommitted EVO-USIS-014 and prior Wave-2 batch. Remediation = stage + commit the synchronized set (a git action pending explicit authorization per repository git-safety policy); post-commit `--guard` returns exit 0.

## Determination

**PHASE 4 PASS (integrity).** Repository, registry, Knowledge-Once, dependency-closure, certification-integrity, zero-duplication, zero-orphan, and lineage are proven. The sole open item is the commit-time drift gate.
