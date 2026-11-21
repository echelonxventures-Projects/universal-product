# 13 — Final Verification & Completion Report

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000005` — Repository Dependency Remediation Execution Programme |
| STAGE | Final verification sweep (independent re-execution of every gate) |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| HEAD | `527485abf00f241a035dbd06062b78c1d9dcde31` (unchanged) |
| BRANCH | `programme/evo-usis-005` |
| WORKING TREE | DIRTY · 127 entries |
| EVIDENCE | `evidence/final-verification/` |
| **EXIT VERDICT** | **DEPENDENCY REMEDIATION COMPLETE** |

> This sweep re-executed every gate from scratch after all remediation and reporting
> work was finished. It re-derived nothing from memory: each verdict below is a fresh
> process exit code, captured to file.

---

## 1. Gate re-execution — exit codes

| # | Command | Owner | Expected | Actual | Verdict |
|---|---|---|---|---|---|
| 1 | `./verify.sh` (EC-1) | EC-1 | 0 | **0** | **PASS** |
| 2 | `python3 -m engine.graph.cli validate` | `engine/graph` | 0 | **0** | **PASS** |
| 3 | `python3 00-BOOK/tools/ukb.py enforce --pre` | `ukb.py` | 0 | **0** | **PASS** |
| 4 | `python3 00-BOOK/tools/ukb.py validate` | `ukb.py` | 0 | **0** | **PASS** |
| 5 | `python3 -m intelligence.rie verify` | `intelligence/rie` | 0 | **0** | **PASS** |
| 6 | `python3 -m engine.determinism.reproduce` | `engine/determinism` | 0 | **0** | **PASS** |
| 7 | `uccep_engine.py --tier standard --gate` | UCCEP-000000 | 0 | **0** | **PASS** |
| 8 | `uccep_engine.py --tier full --gate` | UCCEP-000000 | 1 | **1** | **EXPECTED FAIL** — `CK-REG-DRIFT` only (§5) |

Captured: `evidence/final-verification/exit-codes.txt`.

## 2. EC-1 validation

```
================ VERIFICATION SUMMARY ================
  PASS  ruff lint + format-check (engine + platform)
  PASS  pytest + coverage gate (--cov-fail-under=90)
  PASS  coverage report
  PASS  governance enforce --pre
=====================================================
✓ VERIFICATION PASSED
```

Coverage 97% against a 90% gate. `verify.sh` was executed three times across this
session, exit 0 every time. Log: `evidence/final-verification/verify.log`.

## 3. Dependency gate

```json
{
  "dangling_edge_endpoints": [],
  "dependency_cycle": [],
  "duplicate_node_ids": [],
  "edge_count": 12841,
  "is_valid": true,
  "malformed_edge_ids": [],
  "malformed_node_ids": [],
  "node_count": 1224,
  "unversioned_artifacts": []
}
```
**Exit code 0.** Output sha256
`00ca33637606a4e8c5d194a38f944e25dbd5e2e8be063a73a70304427bd34897` — identical to the
positive-path digest recorded during T-2 verification, so the gate verdict is stable
across the whole session.

## 4. Registration and integrity

| Measure | Value |
|---|---|
| Eligible on-disk artifacts | 1199 |
| Registered | 1199 |
| Unregistered eligible | **0** |
| Unclassified (OTHER/MISC) | **0** (GATED) |
| Reconciled-set drift | **0** (GATED) |
| Invalid (unreadable/empty) | **0** |
| `ukb validate` | PASSED — 1199 artifacts, append-only page ledger intact, referential integrity OK |

`ukb validate` emits its standing self-report *"jsonschema not installed — ran structural
checks only"*. That reduced scope is the pre-existing finding `UCCEP-F-006`
(`WP-UCCEP-004`), unrelated to dependency remediation and outside this programme's scope.
It is recorded here rather than passed over silently.

## 5. Aggregate constitutional gate — reproduced byte-identically

| Tier | Certification | Exit | Gates PASS | Blocking | Seal | Log digest vs earlier evidence |
|---|---|---|---|---|---|---|
| `standard` | **CERTIFIED-PROVISIONAL** | **0** | **9/13** | **none** | `be797344405512e2…` | **byte-identical** |
| `full` | NOT-CERTIFIED | 1 | **12/13** | `CK-REG-DRIFT` | `45570ae083e34f5e…` | **byte-identical** |

Both logs hash to exactly the digests recorded in `evidence/post/`
(`b5c81423…`, `5c1cf975…`). The aggregate gate is therefore deterministic over an
unchanged repository — the strongest available evidence that the verdicts in Outputs 4, 6
and 11 were not incidental.

**`G-08` Dependency Gate: PASS at both tiers.** `CK-GRAPH`: all six assertions PASS,
including `dependency_cycle` under *CEP-009 Art XV.2*.

The single full-tier blocking failure is `CK-REG-DRIFT` (exit 3, *"uncommitted-registration
drift — source split from projections"*). It pre-dates this programme (`UCCEP-F-007`;
120 dirty entries at baseline), is a registration-commit act rather than a dependency
defect, and is owned by `WP-UCCEP-005` (repository operator). Unchanged by this sweep.

The register was returned to the canonical `standard` tier after the full-tier run, so
`00-MASTER/UCCEP-000000/` rests at `CERTIFIED-PROVISIONAL`, blocking none.

## 6. Artifact and state counts verified against implementation evidence

**40 of 40 count/state assertions verified · 0 mismatches.** Every number asserted in
Outputs 1–12 was recomputed from the live registers and the graph, not read back from the
reports.

| Assertion | Claimed | Measured |
|---|---|---|
| Registered artifacts (`count` and list length) | 1199 | 1199 |
| Volumes | 25 | 25 |
| Graph nodes | 1224 | 1224 |
| Graph edges (`relationships.json` count and graph size) | 12841 | 12841 |
| `Depends-On` artifact edges | 4774 | 4774 |
| Strongly-connected components | 1199 | 1199 |
| **Components with >1 member** | **0** | **0** |
| Self-loops / duplicate edges / malformed edges | 0 / 0 / 0 | 0 / 0 / 0 |
| Acyclic | true | true |
| Topological ordering complete | true | true |
| Artifacts ordered | 1199 | 1199 |
| Parallel groups | 164 | 164 |
| Artifacts placed in groups | 1199 | 1199 |
| Widest group | 903 | 903 |
| Single-member groups | 96 | 96 |
| Critical-path length / nodes listed | 164 / 164 | 164 / 164 |
| Critical path cyclic | false | false |
| Declared dependency pairs | 190 | 190 |
| **Hidden dependencies (declared, unprojected)** | **0** | **0** |
| Projected `Depends-On` pairs | 4774 | 4774 |
| Projected-not-declared (metadata edges, by design) | 4584 | 4584 |
| Duplicate edge ids / unknown endpoints | 0 / 0 | 0 / 0 |
| Parent pairs | 1198 | 1198 |
| Artifacts under `07-ENGINEERING/` | 9 | 9 |
| ENG spine dependency levels | 31,32,33,34,35,36 | 31,32,33,34,35,36 |
| ENG spine strictly increasing | true | true |
| Baseline / post evidence files | 7 / 19 | 7 / 19 |
| Output documents `01`–`12` | 12 | 12 |
| Working-tree entries (baseline / now) | 120 / 127 | 120 / 127 |
| **New entries attributable to this programme** | **7** | **7** |
| `id-ledger.json` sha256 unchanged | `be97eb9f…` | `be97eb9f…` |

### 6.1 Mutation-hash verification

`shasum -c` against `evidence/post/post-hashes.txt`: **10 of 10 OK** —
`config.py`, `validation.py`, `test_validation.py`, and `DATA/{artifacts, relationships,
volumes, id-ledger, control-tower, change-ledger, certification}.json`. No file drifted
after the mutation register was written.

### 6.2 Evidence-register verification

**26 of 26 evidence digests verified**, section-aware (baseline vs post), against
`10-VALIDATION-EVIDENCE-REGISTER.md`. Every cited hash resolves to the file it names.

## 7. One issue found and corrected by this sweep

Verification is only worth the failures it surfaces. It surfaced one.

| Item | Detail |
|---|---|
| **Issue** | Output 5 §7 claimed the ten `intelligence/*.json` registers "reproduce byte-identically", and Outputs 2 and 5 cited `model_content_hash 6b2748c4…`. On re-run the hash was `ed5a8b67…`. |
| **Root cause** | `RepositoryIntelligenceEngine.verify_determinism()` (`intelligence/rie/engine.py`) derives the output set **twice in memory** and compares canonical JSON. It proves *identical repository state ⇒ identical outputs*; it does **not** compare against the committed files. `model_content_hash` is a fingerprint of the *current* repository model, so it legitimately moved when this programme wrote its own 13 documents and evidence under `00-MASTER/UCCEP-000005/`. |
| **Is it a defect?** | **No.** `deterministic: true`, `mismatches: []` on every run; two consecutive runs returned an identical hash, confirming within-state stability. `rie verify` exits 0. |
| **Was it a reporting error?** | **Yes** — the wording overstated what the check proves. |
| **Correction applied** | Output 5 §7 rewritten to state precisely what `verify_determinism` proves, to record that this programme never ran `rie build` (so those files are unchanged by it, and their working-tree modifications are pre-existing baseline drift), and to mark the hash as a content fingerprint rather than a stability claim. Output 2 §5 row amended to drop the stale hash and cross-reference Output 5 §7. |
| **Repository logic changed** | **None.** Two markdown sentences in this programme's own reports. No code, register, corpus artifact or gate was touched. |

No other discrepancy was found.

## 8. Success criteria — final adjudication

| # | Criterion | Verifying gate / measurement | Verdict |
|---|---|---|---|
| 1 | Approved remediation executed | T-1, T-2, T-3 in order; `WP-UCCEP-003` acceptance criterion demonstrated in both directions | **MET** |
| 2 | Repository Truth regenerated | `register.sh` 10/10 phases; `ukbx certify` 10/10 domains; second build byte-identical | **MET** |
| 3 | Dependency graph acyclic | `dependency_cycle = []`, `acyclic = true` | **MET** |
| 4 | SCC count >1 = 0 | measured 0 | **MET** |
| 5 | Deterministic ordering established | 1199/1199 ordered; identical digests across runs | **MET** |
| 6 | Critical Path generated | Output 8 — length 164, acyclic, deterministic | **MET** |
| 7 | Parallel Groups generated | Output 9 — 164 groups, 1199/1199 placed, 0 unorderable | **MET** |
| 8 | `G-08` PASS | PASS at `standard` and `full` tier | **MET** |
| 9 | Repository integrity preserved | 10/10 integrity domains; `id-ledger` untouched; 0 identifiers allocated | **MET** |
| 10 | Repository consistency preserved | 0 hidden, 0 duplicate, 0 malformed dependencies; declared/projected parity | **MET** |
| 11 | Repository ready for execution authorization | Every dependency precondition satisfied (I-01…I-11). One pre-existing, non-dependency operator act outstanding (O-01, `CK-REG-DRIFT`) | **MET, CONDITIONAL** |

**11 of 11 criteria met**; criterion 11 carries the pre-existing registration-commit
condition, stated explicitly rather than absorbed.

## 9. Exit verdict

**DEPENDENCY REMEDIATION COMPLETE.**

Basis: the prohibited lineage cycle is resolved at its source in generator data, not
masked; the gate that reported it while returning valid now fails closed and was
demonstrated failing closed; the repository re-derives a complete, deterministic, acyclic
execution model; `G-08` moved FAIL → PASS; the aggregate gate moved NOT-CERTIFIED
(blocking `CK-GRAPH`) → CERTIFIED-PROVISIONAL (blocking none) at standard tier and reaches
12/13 gates at full tier; every gate verdict reproduces byte-identically; identity was
preserved absolutely (zero identifiers allocated, renumbered or released); and no corpus
artifact was edited.

The verdicts `PARTIALLY COMPLETE`, `BLOCKED` and `FAILED` are each excluded: no approved
remediation task is outstanding, no gate blocked execution of the programme, and no
success criterion failed.

## 10. Completion statement

| Item | Result |
|---|---|
| Tasks executed | `T-1` → `T-2` → `T-3`, strictly sequential, no parallel execution |
| Scope | `WP-UCCEP-003` only — no redesign, no reinterpretation, no new work package |
| Hand-authored file mutations | 3 |
| Corpus artifacts edited | 0 |
| Identifiers allocated / renumbered / released | 0 / 0 / 0 |
| Blast radius | 4 portal projections of 1199 artifacts |
| Commits made | 0 — HEAD unchanged |
| Outputs delivered | 11 required (Outputs 1–11) + handover + this report = 13 documents |
| Evidence artifacts | 35 (7 baseline · 19 post · 9 final-verification) |
| Findings discharged in substance | `UCCEP-F-003` (declaration update remains its owner's act — risk R-01) |
| Handover | `12-HANDOVER-TO-UCCEP-000006.md` — package complete |
| Implementation authorization granted | **NONE** |

Outstanding, carried into UCCEP-000006 as execution-authorization inputs:

1. **O-01 (blocking)** — commit source and projections atomically; discharges
   `CK-REG-DRIFT` / `G-07` / `UCCEP-F-007` / `WP-UCCEP-005`. Operator act.
2. **O-02** — record `UCCEP-F-003` as discharged in
   `00-MASTER/UCCEP-000000/uccep-bindings.json`. UCCEP-000000's act.
3. **O-03** — explicit implementation authorization. UCCEP-000006's act.
4. **O-04** — ratified certification. Requires an authority that does not exist in the
   corpus (`UCCEP-F-004`); cannot be manufactured.

---

**FINAL VERIFICATION PASSED · 8 GATES RE-EXECUTED · 40/40 COUNTS VERIFIED · 36/36 DIGESTS
VERIFIED · 1 REPORTING IMPRECISION FOUND AND CORRECTED · VERDICT: DEPENDENCY REMEDIATION
COMPLETE**
