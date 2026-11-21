# EVO-USIS-014 · 05 — Validation Report

| Field | Value |
|-------|-------|
| PROGRAMME | EVO-USIS-014 — Validation Architecture Implementation |
| PHASE | 4 — Validation |
| RESULT | PASS on all integrity validators; commit-time drift gate reported (see §Guard) |

## Executed commands & results

| Command | Result (Repository Truth) |
|---------|---------------------------|
| `./doctor.sh` | ENVIRONMENT READY — python 3.12, pytest 8.3.4, pytest-cov 6.0.0, coverage 7.15.2, ruff 0.8.4 all OK (exit 0) |
| `./00-BOOK/tools/register.sh` | TRANSACTION COMPLETE — 1135 artifacts registered, classified, validated, synchronized (exit 0) |
| `ukb.py validate` | VALIDATION PASSED — 1135 artifacts, append-only page ledger intact, referential integrity OK |
| `ukb.py enforce` | ENFORCEMENT PASSED — 1135 eligible = 1135 registered; unregistered 0; unclassified 0 (GATED); invalid 0 |
| `ukbx.py validate` | TWIN VALIDATION PASSED — 15 signals, append-only, every subject resolves, provenance present, no embedded secrets |
| `ukbx.py twin --check` | CERTIFIED — hard checks 7/7 |
| `./00-BOOK/tools/register.sh --guard` | Transaction COMPLETE; drift gate = uncommitted synchronized register set (exit 3) — see §Guard |

> Note on `verify.sh`: `verify.sh` runs the Software-stream (`engine/`,`platform/`) pytest/coverage suite (EC-1/EC-2 verification), which is **referenced, frozen, and out of scope** for the intelligence-corpus USIS-014 artifact (LAW USIS-02; DP-03 — 0 writes to frozen streams). The authoritative validators for a `15-…/` corpus artifact are `ukb validate` / `ukbx validate` / `twin --check`, all PASS above. `doctor.sh` confirms the `verify.sh` toolchain is READY/reproducible.

## Verified integrity properties

| Property | Verified by | Result |
|----------|-------------|--------|
| Repository integrity | `ukb validate` structural + `ukbx certify` domain 2 | PASS |
| Registry integrity | append-only ledger; count parity 1135=1135 | PASS |
| Knowledge Once | No-Orphan + referential integrity; unclassified 0 | PASS |
| Dependency closure | every Depends-On endpoint resolves (C-05) | PASS |
| Cross-layer integrity | whole-corpus reference resolution + acyclic (C-07) | PASS |
| No duplicate knowledge | Zero-Duplication (LAW USIS-02); references only | PASS |
| No orphan artifacts | navigability + return path (C-08) | PASS |
| No broken lineage | parent/child edges resolve; portal reachable | PASS |
| No invalid registry entries | schema/structural checks; invalid 0 | PASS |

## Guard (commit-time drift gate)

`register.sh --guard` completed the transaction, then reported `REGISTRATION DRIFT DETECTED` (exit 3): the regenerated `00-BOOK/DATA|REGISTRIES|CONTROL-TOWER|PORTAL` synchronized set is **not yet committed** to git. This is the REG-AUTO-001 §16 gate-2 behavior — an *uncommitted-state* signal, **not** an integrity defect (every integrity validator above PASSED). The delta comprises the USIS-014 registration plus the pre-existing uncommitted Wave-2 batch (`UCOS-USIS-000007…000016`). Remediation = stage + commit the synchronized set (a git action pending explicit authorization, per repository git-safety policy). Post-commit, `--guard` returns exit 0 / "Guard PASSED".

## Determination

**PHASE 4 PASS (integrity).** Repository, registry, Knowledge-Once, dependency-closure, cross-layer integrity, zero-duplication, zero-orphan, lineage, and registry-validity are all proven. The sole open item is the commit-time drift gate, which is a workflow gate resolved by committing the synchronized register set.
