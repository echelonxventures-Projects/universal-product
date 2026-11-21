# Output 3 — Repository Integrity Report

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000006` |
| PHASE | 3 — Repository Integrity Assessment |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| BASIS | Digest identity with the state UCCEP-000005 certified · one read-only gate confirmation · live register state |
| HEAD | `527485abf00f241a035dbd06062b78c1d9dcde31` · branch `programme/evo-usis-005` · tree DIRTY 127 |

> Method note. Where UCCEP-000005 established a property by execution and this programme
> measured its inputs to be **byte-identical**, integrity is affirmed by digest identity plus
> the evidenced determinism of the derivation — not by re-running the accepted validation.
> Exactly one command was executed (`engine.graph.cli validate`, read-only) as an
> authorization-time confirmation.

---

## 1. Assessment

| # | Dimension | Measurement | Verdict |
|---|---|---|---|
| 1 | **Repository consistency** | 0 hidden dependencies (declared-but-unprojected) · 0 duplicate edge ids · 0 malformed nodes/edges · 0 self-loops · 0 dangling endpoints · declared 190 / projected 4774 with the 4584 metadata-only edges accounted for by design · parent pairs 1198 | **CONSISTENT** |
| 2 | **Repository integrity** | Repository Truth **CERTIFIED 10/10** integrity domains (UCCEP-000005, `ukbx certify`) over inputs whose 7 digests this programme re-computed and matched · `id-ledger.json` digest unchanged · 0 identifiers allocated, renumbered or released · append-only page ledger intact · referential integrity OK | **INTACT** |
| 3 | **Deterministic state** | Regeneration is a fixed point (second build byte-identical) · aggregate gate logs reproduced byte-identically at both tiers · `CK-DETERMINISM-BUILD` PASS · `CK-RIE-DETERMINISM` PASS · dependency-gate output digest `00ca33637606a4e8…` **reproduced identically by this programme**, a third independent run across the session | **DETERMINISTIC** |
| 4 | **Artifact consistency** | 1199 eligible on-disk artifacts = 1199 registered · 0 unregistered · 0 unclassified (GATED) · 0 invalid · 0 reconciled-set drift (GATED) · 25 volumes · graph 1224 nodes / 12841 edges, matching the registers | **CONSISTENT** |
| 5 | **Evidence completeness** | 35 / 35 evidence artifacts present · **35 / 35** register digests re-computed and matched · **10 / 10** mutation digests re-computed and matched · every claim in the handover traceable to a named evidence file | **COMPLETE** |
| 6 | **Traceability completeness** | Structural traceability **complete**: dependency ordering 1199/1199, 164/164 groups, 1199 artifacts placed, 0 unorderable, claim→evidence table complete. **Semantic** traceability completeness measures ≈ **22.7%** (`CK-HEALTH` advisory FAIL, `UCCEP-F-002`, `WP-UCCEP-002`) | **STRUCTURALLY COMPLETE · SEMANTICALLY INCOMPLETE (advisory)** |
| 7 | **Repository reproducibility** | Regeneration, dependency gate, intelligence derivation and compiler all reproduce · EC-1 `verify.sh` exit 0 (coverage 97% vs a 90% gate) · **but** the state is reproducible only from a **dirty working tree**: 52 untracked entries including `00-CMG/`, `00-MASTER/UCCEP-000000/` and the handover package itself are absent from committed history | **REPRODUCIBLE IN PLACE · NOT REPRODUCIBLE FROM COMMITTED HISTORY** |

## 2. Integrity domains of record

Established by UCCEP-000005 over inputs verified byte-identical by this programme.

| Domain | State |
|---|---|
| Digital-twin certification | **10 / 10 CERTIFIED** |
| Registration parity (1199 = 1199) | PASS |
| Classification (0 OTHER/MISC) | PASS — GATED |
| Reconciled-set drift | PASS — 0, GATED |
| Page ledger append-only | PASS |
| Referential integrity | PASS |
| Identity ledger immutability | PASS — digest unchanged, 0 movements |
| Dependency acyclicity | PASS — `scc_gt1_count = 0` |
| Regeneration fixed point | PASS — second build byte-identical |
| Schema validation scope | **DEGRADED** — structural-only (`jsonschema` absent; `UCCEP-F-006` / `WP-UCCEP-004`, pre-existing, non-blocking) |

## 3. Live register state at authorization time

Captured in `evidence/register-state.txt`.

| Item | Value |
|---|---|
| Tier | `boot` (session-start hook refresh — OBS-1) |
| Certification | **CERTIFIED-PROVISIONAL** |
| Gate exit | **0** |
| Blocking failures | **none** |
| Advisory failures | `CK-HEALTH` |
| Seal | `f638046250d4f88a…` |
| `G-08` Dependency | **PASS** |
| `G-07` Registry | **PARTIAL** (drift check not executed at boot tier) |
| `CK-GRAPH` | **PASS** |
| Verdicts of record for `G-13` / `CK-VERIFY` / `CK-DETERMINISM-BUILD` / `CK-REG-DRIFT` | the full-tier run of UCCEP-000005, produced under the same input digests verified here |

## 4. Integrity defects found by this assessment

**None.** Two integrity *limitations* are carried forward, both pre-existing, both already
registered, neither introduced by remediation:

| Limitation | Registered as | Effect on execution |
|---|---|---|
| Uncommitted state — Repository Truth split from committed history (52 untracked entries) | `UCCEP-F-007` · `WP-UCCEP-005` · **O-01** | **Condition C-1.** Removes the ability to establish and roll back to a committed pre-mutation baseline |
| Semantic traceability ≈22.7%; schema validation structural-only | `UCCEP-F-002` / `UCCEP-F-006` · `WP-UCCEP-002` / `WP-UCCEP-004` | Advisory. Caps certification, not execution |

## 5. Phase 3 determination

**REPOSITORY INTEGRITY CONFIRMED.**

Consistency, integrity, deterministic state, artifact consistency and evidence completeness
are all affirmed with zero defects. Two qualifications are stated rather than absorbed:
traceability is structurally complete but semantically ~22.7% (advisory), and the repository
is reproducible **in place** but not from committed history until O-01 is discharged. The
second is the whole reason the authorization in Output 5 carries conditions.
