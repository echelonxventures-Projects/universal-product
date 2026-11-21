# Output 2 — Dependency Remediation Report

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000005` |
| PHASES | 2 (T-1) · 3 (Regeneration) · 4 (T-2) · 5 (T-3) |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| EXECUTION ORDER | `T-1 → T-2 → T-3` — strictly sequential, no parallel execution |
| APPROVED SCOPE | `WP-UCCEP-003` only. No redesign, no reinterpretation, no new work package. |

---

## 1. What was authorized, and what was executed

`WP-UCCEP-003` prescribes **two independent corrections**:

> **(1) DATA** — reconcile the declared dependency direction between ENG-004 and ENG-005
> so the Depends-On relation is acyclic … **the point of correction**.
> **(2) GATE** — `engine/graph/validation.py`: `is_valid` must consider
> `dependency_cycle`, and the CLI must exit non-zero when `is_valid` is false.

Both were executed, in the approved order, and nothing else.

| Task | Scope | Target | Status |
|---|---|---|---|
| **T-1** | DATA correction | `00-BOOK/tools/config.py` → `CHAINS["ENG"]` | **EXECUTED** |
| **T-2** | GATE correction | `engine/graph/validation.py` (+ its test) | **EXECUTED** |
| **T-3** | Repository re-derivation | derived views only (read-only over the corpus) | **EXECUTED** |

---

## 2. T-1 — Dependency Data Correction

### 2.1 The correction

`00-BOOK/tools/config.py`, `CHAINS["ENG"]`:

```diff
     "ENG": [
         "ENGINEERING-PROGRAM-MASTER-INDEX",
         "UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE",
         "UNIVERSAL-OBJECT-SYSTEM-MASTER-ARCHITECTURE",
-        "UNIVERSAL-RELATIONSHIP-REFERENCE-SYSTEM-MASTER-ARCHITECTURE",
-        "UNIVERSAL-TYPE-SYSTEM-MASTER-ARCHITECTURE",
         "UNIVERSAL-VALUE-SYSTEM-MASTER-ARCHITECTURE",
+        "UNIVERSAL-TYPE-SYSTEM-MASTER-ARCHITECTURE",
+        "UNIVERSAL-RELATIONSHIP-REFERENCE-SYSTEM-MASTER-ARCHITECTURE",
     ],
```

A 16-line citation block was added above the list recording the ordering authority
(`ENG-GOV-001` Output 11 Option B), why Type must precede Relationship & Reference, and
that the change is corrective under CEP-009 Article IV.3 and is DATA ONLY.

Full diff: `evidence/post/T-1-config-py.diff` (99 lines).

### 2.2 Constitutionally approved ordering applied

| Position | Native id | Instrument | Universal id |
|---|---|---|---|
| 1 | `ENG-000` | Engineering Program Master Index | `UCOS-ENG-000003` |
| 2 | `ENG-001` | Universal Identity System | `UCOS-ENG-000005` |
| 3 | `ENG-002` | Universal Object System | `UCOS-ENG-000006` |
| 4 | `ENG-003` | Universal Value System | `UCOS-ENG-000009` |
| 5 | `ENG-004` | Universal Type System | `UCOS-ENG-000008` |
| 6 | `ENG-005` | Universal Relationship & Reference System | `UCOS-ENG-000007` |

This is verbatim `ENG-GOV-001` Output 11 Option B. No ordering was invented.

### 2.3 Preservation

| Preserved item | Proof |
|---|---|
| **Universal IDs** | `UCOS-ENG-000001…000009` all unchanged and still bound to the same paths (`evidence/post/T-1-eng-chain-edges.json`) |
| **Sticky identifiers** | `00-BOOK/DATA/id-ledger.json` sha256 `be97eb9f0e7152578d85a29f433a2cc284b3d9217231085052ec7efc5c057590` — **byte-identical before and after**. Zero allocation, zero renumber, zero release. |
| **Native ids** | `ENG-000/001/002/003/004/005/GOV-001/GOV-002/GOV-003` unchanged |
| **Repository Truth** | No corpus artifact edited. `07-ENGINEERING/**` untouched (DP-03). |
| **Classification** | No `CLASSIFY_RULES`, `VOLUMES`, `PROGRAM_ROOTS`, `CROSS_PROGRAM` or `RECONCILED_SETS` entry added, edited or renumbered |
| **Cross-program wiring** | `CROSS_PROGRAM` declares `("ENG", "ARCH")` — ENG is upstream-dependent only; **no program depends on the ENG terminal**, so the terminal change is contained inside the ENG chain |

### 2.4 Resulting edges

| Edge | From → To | Type | Note |
|---|---|---|---|
| `UEDGE-000000199` | `UCOS-ENG-000008` (ENG-004 Type) → `UCOS-ENG-000009` (ENG-003 Value) | Depends-On | `structural:chain` |
| `UEDGE-000000202` | `UCOS-ENG-000007` (ENG-005 Rel) → `UCOS-ENG-000008` (ENG-004 Type) | Depends-On | `structural:chain` |
| `UEDGE-000003639` | `UCOS-ENG-000007` → `UCOS-ENG-000009` | Depends-On | `metadata:DEPENDS ON` |

The structural chain and the artifacts' self-declared metadata **now agree**. The
contradiction that produced the cycle is gone at its source.

---

## 3. Phase 3 — Repository Regeneration

Executed the located owner's own transaction: `00-BOOK/tools/register.sh`
(REG-AUTO-001 Atomic Artifact Registration Transaction, 10 phases). No parallel
regeneration path was created.

| Phase | Owner | Result |
|---|---|---|
| 0 · pre-registration enforcement | `ukb enforce --pre` | PASS |
| 1 · registry, pages, graph, control tower | `ukb build` | PASS |
| 2 · state synchronization | `ukbx sync --due` | PASS |
| 3 · digital twin + control-tower dimensions | `ukbx twin` | PASS |
| 4 · navigation portal | `ukbx portal` | PASS |
| 5 · foundation validation | `ukb validate` | PASS |
| 6 · signal-ledger integrity | `ukbx validate` | PASS |
| 7 · digital-twin certification | `ukbx twin --check` | **CERTIFIED** 7/7 hard checks |
| 8 · certification runtime, 10 integrity domains | `ukbx certify` | **CERTIFIED** 10/10 — scope 1199 artifacts, 15 signals, 1353 change events |
| 9 · post-registration completeness | `ukb enforce` | PASS — 1199/1199 registered, 0 unregistered, 0 unclassified, 0 reconciled-set drift |
| 10 | — | **TRANSACTION COMPLETE** |

Log: `evidence/post/register-transaction.log`.

Refreshed: Dependency Graph (`DATA/relationships.json`), Registries (artifact, page,
volume, knowledge-graph, certification, change/version/lineage), Indexes
(`PORTAL/index.md`, portal pages), Control Tower, Repository Truth (`DATA/*.json`).

---

## 4. T-2 — Dependency Gate Correction

### 4.1 The correction

`engine/graph/validation.py` — `GraphValidationReport.is_valid`:

```diff
         return not (
             self.duplicate_node_ids
             or self.malformed_node_ids
             or self.malformed_edge_ids
             or self.unversioned_artifacts
+            or self.dependency_cycle
         )
```

`dependency_cycle` moved from *informational finding* to *hard mission invariant*. The
module docstring and the property docstring now record the authority (CEP-009
Art XV.2 / Art XX.2) and the discharged finding (`UCCEP-F-003`). Callers that must
inspect a knowingly-cyclic substrate still pass `require_acyclic_dependencies=False`,
which leaves the invariant *unasserted* rather than silently passed.

**No CLI change was required**: `engine/graph/cli.py::_cmd_validate` already returned
`0 if report.is_valid else 1`. The fail-open was entirely in `is_valid`. Correcting one
predicate therefore closed the CLI exit code, `evidence["operational"]`, and `CK-GRAPH`
simultaneously — no second gate and no new validator was written.

Full diff: `evidence/post/T-2-validation-gate.diff`.

### 4.2 Test correction

`engine/tests/graph/test_validation.py` — the test that *asserted* the fail-open
(`test_dependency_cycle_is_finding_not_failure`) was replaced by four tests:

| Test | Proves |
|---|---|
| `test_dependency_cycle_fails_validity` | negative path — cycle reported **and** `is_valid False` |
| `test_dependency_cycle_verdict_is_deterministic` | repeated validation yields an identical verdict |
| `test_acyclic_dependency_chain_passes_validity` | positive path — single-direction edge stays valid |
| `test_cycle_unasserted_when_acyclicity_not_required` | opt-out leaves the invariant unasserted |

`engine/tests/graph/test_real_corpus.py::report.is_valid is True` now constitutes a
standing positive-path assertion over real Repository Truth.

### 4.3 Verification

| Path | Command | `is_valid` | `dependency_cycle` | Exit |
|---|---|---|---|---|
| **Positive** | `engine.graph.cli validate` (real corpus) | `true` | `[]` | **0** |
| **Negative** | same, over an isolated temp copy of `00-BOOK/DATA` with the reversed edge re-injected | `false` | `[ENG-000008, ENG-000007, ENG-000008]` | **1** |

Gate determinism — output sha256 across repeated runs:

| Path | Runs | Digest |
|---|---|---|
| Negative | 3 | `2542099a88722691e53483b24305ffe7f1ae0ad47664dc5b9c06812f3352e2ec` (×3) |
| Positive | 2 | `00ca33637606a4e8c5d194a38f944e25dbd5e2e8be063a73a70304427bd34897` (×2) |

The negative path was constructed in a `mktemp -d` copy and the copy was removed; the
corpus was never mutated to produce it (DP-03).

Evidence: `evidence/post/T-2-gate-paths.txt`.

**`WP-UCCEP-003` acceptance criterion** — *"`engine.graph.cli validate` exits non-zero
while any cycle is reported, and exits 0 once the cycle is resolved"* — **SATISFIED
VERBATIM, both directions demonstrated.**

### 4.4 Required EC-1 validation

`./verify.sh` — executed twice, exit 0 both times:

| Stage | Verdict |
|---|---|
| ruff lint + format-check (engine + platform) | **PASS** |
| pytest + coverage gate (`--cov-fail-under=90`) | **PASS** — 97% total |
| coverage report | **PASS** |
| governance `enforce --pre` | **PASS** — 1199/1199 |

Log: `evidence/post/T-2-ec1-verify.log`.

---

## 5. T-3 — Repository Re-Derivation

Executed against the corrected Repository Truth using only located owners.

| Re-derived | Located owner | Result |
|---|---|---|
| Dependency ordering | `engine.graph` + `engine.graph.architecture.algorithms` | 1199/1199 ordered · **complete** |
| Parallel execution groups | idem (Kahn levelisation, sorted frontier) | 164 groups |
| Critical path | `engine.graph.architecture.critical_path.CriticalPathEngine` | length 164 · `cyclic = false` |
| Global Implementation Graph / Implementation State Registry | `02-MASTER/UCOS-COMP-000000-{GIG,ISR}` | **unaffected** — both contain zero `ENG-00N` references; neither was modified (DP-03) |
| Repository intelligence (dependency graph, execution frontier, progress, twin) | `intelligence.rie verify` | `deterministic: true`, `mismatches: []`, 10 outputs (see Output 5 §7 on the model content hash) |
| Repository Truth | `register.sh` (Phase 3) | regenerated, certified 10/10 |

Evidence: `evidence/post/dependency-derivation.json`,
`evidence/post/T-3-rie-determinism.json`, `evidence/post/T-3-graph-evidence.json`.

---

## 6. Before / after

| Metric | Baseline | Post-remediation | Δ |
|---|---|---|---|
| `dependency_cycle` | `[ENG-000008, ENG-000007, ENG-000008]` | `[]` | **resolved** |
| `is_valid` | `true` (fail-open) | `true` (fail-closed capable) | **gate corrected** |
| CLI exit on a cycle | 0 | 1 | **fail-closed** |
| SCC with >1 member | 1 | **0** | −1 |
| Deterministic ordering | INCOMPLETE (3 unorderable) | **COMPLETE** (1199/1199) | closed |
| Parallel groups | 52 (truncated) | **164** (full) | +112 |
| Critical path | 164 · cyclic | 164 · **acyclic** | well-defined |
| `G-08` Dependency Gate | **FAIL** | **PASS** | discharged |
| Registered artifacts | 1199 | 1199 | 0 |
| Identifiers allocated | — | **0** | — |

---

**T-1 EXECUTED · T-2 EXECUTED · T-3 EXECUTED · ORDER PRESERVED · SCOPE NOT EXCEEDED**
