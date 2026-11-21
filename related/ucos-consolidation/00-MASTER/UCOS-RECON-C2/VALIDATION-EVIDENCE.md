# UCOS-RECON-C2 — VALIDATION EVIDENCE

| Field | Value |
|-------|-------|
| AUTHORITY | **NONE — DERIVED TRUTH** |
| ANCHOR | `4c6623f` on `integration/recovery-001`, working tree CLEAN (0 entries) |
| EVERY ROW BELOW | executed in this repository; exit codes and output lines quoted, not asserted |

---

## 1. The mission gate

```
$ bash 00-BOOK/tools/register.sh --guard ; echo $?
Guard PASSED — repository, registry, control tower, twin, and portal are in sync.
0
```

Exit semantics (`uccep-bindings.json`): `0` = registered and synchronized;
`3` = uncommitted-registration drift — source split from projections.

**CK-REG-DRIFT = PASS.**

## 2. Registration, registry, projection, traceability

| Validation | Command | Exit | Result |
|---|---|---:|---|
| Structural + schema invariants | `ukb.py validate` | 0 | `VALIDATION PASSED — 1193 artifacts, append-only page ledger intact, referential integrity OK; 0 execution(s)` |
| Signal ledger integrity | `ukbx.py validate` | 0 | `TWIN VALIDATION PASSED — 15 signals, append-only, every subject resolves, provenance present, no embedded secrets` |
| Registration completeness / parity | `ukb.py enforce` | 0 | `ENFORCEMENT PASSED` — 1193 eligible = 1193 registered; 0 unregistered, 0 unclassified, 0 invalid, 0 reconciled-set drift, 0 awaiting VCS binding |
| Digital-twin hard checks | `ukbx.py twin --check` | 0 | `CERTIFIED (hard checks 7/7)` — incl. C-07 graph acyclic, C-08 navigation all reachable + return path |
| Digital-twin certification runtime | `ukbx.py certify` | 0 | `CERTIFIED (integrity domains 10/10)` — Identity, Registry, Traceability, Knowledge Graph, Change Intelligence, Version, Lineage, Synchronization, Twin Intelligence, Execution |

## 3. Determinism

| Property | Command | Exit | Result |
|---|---|---:|---|
| Registration idempotence | `register.sh` twice, digest the 4 projection subtrees | 0 | **byte-identical**: `8b483a1340b2c2d25544528439a3396d8fd8b10e809c1795b61019304c09b78c` both runs |
| Intelligence determinism (CK-RIE-DETERMINISM) | `python -m intelligence.rie verify` | 0 | `"deterministic": true, "mismatches": []` |
| Compiler reproducibility (CK-DETERMINISM-BUILD) | `python -m engine.determinism.reproduce` | 0 | `[PASS] double_build('BP-DATA-0001') byte_identical=True` |
| RIB self-determinism | `rib_engine.py --check-determinism` | 0 | `PASS` |

Digest command:
```
find 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL \
  -type f | sort | xargs shasum -a256 | shasum -a256
```

## 4. Root cause eliminated — the decisive test

The test the previous classification could not pass:

```
$ python -m intelligence.rie build          # regenerates all 10 RIE outputs
$ bash 00-BOOK/tools/register.sh
$ git status --porcelain -- 00-BOOK | wc -l
0
```

Projection digest unchanged at `8b483a13…`. **A full regeneration of the
Repository Intelligence Engine now perturbs the registry by zero bytes.** Before
`214c1a9`, the same two commands produced 10 `Modified` change events, 10
`content_hash` rewrites and an `id-ledger` append.

Fixpoint probe from a clean tree, running every engine in sequence:

| Step | Exit | tree dirty | **00-BOOK dirty** |
|---|---:|---:|---:|
| `register.sh --guard` | 0 | 0 | **0** |
| `intelligence.rie build` | 0 | 10 | **0** |
| `rib_engine.py --gate` | 1 | 26 | **0** |
| `uccep_engine.py --tier full --gate` | 0 | 54 | **0** |

`00-BOOK` never moves. The `rib` exit 1 is GATE-12 reacting to the uncommitted RIE
regeneration from the previous step (anchor lag, declared in
REGISTRATION-GRAPH §6), not registration drift.

## 5. Canonical verification

```
$ ./verify.sh ; echo $?
  PASS  ruff lint + format-check (engine + platform)   0s
  PASS  pytest + coverage gate (--cov-fail-under=90)  34s
  PASS  coverage report                                2s
  PASS  governance enforce --pre                       1s
✓ VERIFICATION PASSED — all gates green
0
```

Coverage: **94%** line (37652 statements, 2155 missed; 7420 branches, 112 partial).

## 6. Governance

| Gate | Command | Exit | Result |
|---|---|---:|---|
| Constitutional meta-governance | `00-CMG/tools/cmg-gate.sh` | 0 | 60 concerns allocated (49 delegated / 11 retained), 0 findings, `READY-PROVISIONAL` |
| Repository Integration Blueprint, 8 self-guards | `rib_engine.py --check-{declaration,no-enumeration,write-scope,determinism,substrate,no-fabrication,reuse-before-create,totality}` | 0 ×8 | **all PASS** |
| Repository Integration Gate | `rib_engine.py --gate` | 0 | `BLUEPRINT CERTIFIED — REPOSITORY MAY PROCEED \| gates=12/12 \| dirty=0 \| gate=OPEN \| seal=65d0c8955c6c6cf5` |

`--check-substrate` PASS confirms the four `intelligence/UCOS-RIE-*` substrate
pointers still resolve — the files remained tracked, so no consumer was disturbed.

## 7. Complete certification pipeline

```
$ python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier full --gate ; echo $?
UCCEP-000000: CERTIFIED-PROVISIONAL | tier=full | gates=14/14 PASS |
              programmes=16/16 PASS | blocking=none | seal=a6082ab6c6a61b86
0
```

Seal `a6082ab6c6a61b86` reproduced identically across two independent full-tier
runs.

### All 18 checks

| Verdict | Check | Tier |
|---|---|---|
| PASS | CK-CMG | boot |
| PASS | CK-REG-ENFORCE | boot |
| PASS | CK-REG-VALIDATE | boot |
| PASS | CK-CLOSURE-P1 | standard |
| PASS | CK-CLOSURE-P2 | standard |
| FAIL *(advisory — standing finding UCCEP-F-001)* | CK-CLOSURE-P3 | standard |
| FAIL *(advisory — standing finding UCCEP-F-002)* | CK-HEALTH | boot |
| PASS | CK-GRAPH | boot |
| PASS | CK-DISCOVERY | boot |
| PASS | CK-RIE-DETERMINISM | standard |
| PASS | CK-VERIFY | full |
| PASS | CK-DETERMINISM-BUILD | full |
| **PASS** | **CK-REG-DRIFT** | **full** |
| PASS | CK-DECISION-EVIDENCE | boot |
| PASS | CK-SELF-DECLARATION | boot |
| PASS | CK-SELF-NO-ENUMERATION | boot |
| PASS | CK-SELF-WRITE-SCOPE | boot |
| PASS | CK-SELF-DETERMINISM | standard |

`blocking_failures = []` · `advisory_failures = [CK-CLOSURE-P3, CK-HEALTH]` ·
`unavailable = []`

### All 14 gates

| Verdict | Gate |
|---|---|
| PASS | G-01 Context Assimilation · G-02 Knowledge Assimilation · G-03 Reuse · G-04 Constitution · G-05 Architecture Admission · G-06 Repository Truth |
| **PASS** | **G-07 Registry Gate** |
| PASS | G-08 Dependency · G-09 Governance · G-10 Validation |
| PASS-WITH-ADVISORY | G-11 Certification *(CK-HEALTH advisory, pre-existing)* |
| PASS | G-12 Evidence · G-13 Implementation Authorization · G-14 Implementation Evidence |

## 8. No new failure introduced

| Surface | Baseline `a6ccdc0` | After `4c6623f` | Direction |
|---|---|---|---|
| CK-REG-DRIFT | NOT-EXECUTED → FAIL on full tier | **PASS** | fixed |
| G-07 Registry Gate | PARTIAL | **PASS** | fixed |
| UCCEP blocking failures | `[]` (drift never ran) | `[]` (drift ran, passed) | strictly stronger |
| UCCEP certification | CERTIFIED-PROVISIONAL | CERTIFIED-PROVISIONAL | unchanged |
| UCCEP ceiling F-001..F-004 | 4 standing findings | **byte-identical** | unchanged |
| Advisory failures | CK-CLOSURE-P3, CK-HEALTH | identical | unchanged |
| RIB gate | 9/12 CLOSED | **12/12 OPEN** | improved |
| RIB GATE-07 `uncatalogued_units` | 2 | **0** | improved |
| `verify.sh` | PASS | PASS | unchanged |
| Determinism double-build | PASS | PASS | unchanged |
| CMG gate | READY-PROVISIONAL | READY-PROVISIONAL | unchanged |
| Frozen zones written | 0 | **0** | unchanged |

**No gate, check or invariant moved from passing to failing at any step of this
recovery.** Two pre-existing RIB failures were cleared as a consequence of the
repair; the third (`uncatalogued_units=2`) was closed by its declared owner in
`4141647`.

## 9. Honest limits of this evidence

- `CERTIFIED-PROVISIONAL`, not `CERTIFIED`, is the ceiling — imposed by the four
  standing findings UCCEP-F-001..F-004, which are unrelated to registration,
  unchanged by this mission, and were equally in force at `a6ccdc0`. Reaching
  `CERTIFIED` requires ratification authority that `UCCEP-F-004` records as
  VACANT; no engine change can assert it.
- CI was not executed — only local gates. One pre-existing CI fragility was
  measured and is reported: a clean detached worktree at `a6ccdc0` fail-closes
  (`exit 2`) in `rib_engine --gate` because the gitignored substrates
  `00-MASTER/UAKOS-CLOSURE-002/{closure,phase3}.json` are absent from a fresh
  checkout. This mission neither caused nor widened it — Option C was rejected
  specifically to avoid widening it from two substrates to six
  (REPAIR-JUSTIFICATION §4).
- RIE outputs remain one commit stale after any commit containing them (anchor
  lag). Measured as costing the registry zero bytes; it does trip RIB GATE-12
  until a regeneration is committed.

---

*END — UCOS-RECON-C2 VALIDATION EVIDENCE · AUTHORITY = NONE (DERIVED TRUTH)*
