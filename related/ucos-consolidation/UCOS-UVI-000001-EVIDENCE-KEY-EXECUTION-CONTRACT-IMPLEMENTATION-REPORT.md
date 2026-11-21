# UCOS-UVI-000001 — Evidence Key Execution Contract Implementation Report

**Artifact ID:** UCOS-UVI-000001-EVIDENCE-KEY-EXEC-CONTRACT-IMPL
**Programme:** UVI-000001 — Universal Verification Intelligence
**Step:** Implementation Sequence — **Step 1 of 8**
**Standing:** IMPLEMENTATION REPORT — records what was changed and what was measured. Legislates nothing.
**Baseline:** branch `integration/recovery-001` at `bd3f71ff`
**Date:** 2026-08-19
**Predecessor:** UCOS-UVI-000001 Verification Intelligence Evolution Architecture Determination (ARCHITECTURE READY)
**Scope executed:** Step 1 only. No dependency-graph, impact-model, artifact-integration or scheduler work.

**Result:** **STEP 1 COMPLETE** — `./verify.sh --fast` PASSED, all ten UVI laws HOLD, 202 targeted tests green.

---

## 1. Problem

The evidence cache key bound what a stage **reads**, but not what it **runs**.

Under `EVIDENCE_VERSION 1.0` the key composed:

```
sha256( engine_version ‖ stage_id ‖ stage_label ‖ Σ sorted(prefix, path:content_hash) )
```

`./verify.sh` invokes each stage as `run_stage "<label>" <argv…>`. The label entered the key; **the argv did not.** A stage's identity was therefore its name and its inputs, but not its command.

The consequence is a false cache hit. Editing a stage's command while leaving its label unchanged — removing a flag, reordering flags, repointing the stage at a different module — produced a key **identical** to the one recorded before the edit. `decide()` would return `REUSE`, and `verify.sh` would report the stage green **on the strength of a result the edited command had never produced**.

This is the most dangerous failure mode available to a verification selector, because its symptom is a faster green run.

### 1.1 The defect was live, not theoretical

The declaration's own `$standing` asserted the key covered *"the stage's own command."* It did not. The gap was between a declared property and its realisation, which is exactly the class of defect the UVI laws exist to prevent — and no law measured this one.

A stored entry demonstrating the exposure was present in the working store at the time of implementation:

```json
{ "schema": "ucos-verification-evidence", "engine_version": "1.0",
  "stage_id": "object-birth",
  "input_digest": "94f3af99af7e0bb419eba2de421baed600ffbf5eb941e6c7ebf24f956d2fed05",
  "result": "PASS" }
```

That single `PASS` was reachable by **every** command variant of the `object-birth` stage — see §7.

---

## 2. Existing Architecture

Nothing in this step is new architecture. Every element it uses was already present.

| Element | Location | Pre-existing state |
|---|---|---|
| Evidence engine | `engine/verification_intelligence/evidence.py` | content-addressed, atomic, live |
| Hashing primitive | `hashlib.sha256` | already the only hash in the module |
| Key-extension seam | `input_digest(..., extra=())` | present, **no production caller** |
| Version invalidation | `EVIDENCE_VERSION` in every key | present, documented as the migration lever |
| `verify.sh` as contract | UVI-L-03 reconciles labels to `run_stage` literals | present |
| Script parsing | `gate.py::_verify_source`, `_declared_stage_labels` | present, label-only |
| Store | `.ucos-verification-evidence/`, gitignored | present |

The architecture determination identified the `extra` seam as the intended attachment point. **It was used, but not as an optional parameter** — see §3.2.

---

## 3. Change Implemented

Four production modules, one test module. **366 insertions, 23 deletions.** Four further tracked files are regenerated derived truth, disclosed in §6.3.1.

```
 engine/verification_intelligence/constitution.py   +79  -0
 engine/verification_intelligence/evidence.py       +69  -15
 engine/verification_intelligence/plan.py           +10  -2
 engine/verification_intelligence/gate.py           +3   -1
 engine/tests/unit/test_verification_intelligence.py  +198 -12
```

### 3.1 Contract derivation — `constitution.py`

Added `verify_source()` and `execution_contract(label, *, root=None, source=None)`.

`execution_contract` folds backslash-continuations, locates the single `run_stage "<label>"` invocation, and tokenises the remainder with `shlex`.

**The source text is the contract.** Tokens are the ones the script *declares*, not the ones a process would receive after shell expansion. `"$PY"` returns as the literal `$PY`, never as this checkout's absolute venv path. This is the decision that keeps the key machine-independent and keeps UVI-L-10's prohibition on absolute paths intact — binding the expanded argv would have put `/Users/…/.ec1-venv/bin/python` into every key.

Derivation over the live script, all fifteen stages:

| Stage | Derived contract |
|---|---|
| `ruff` | `ucos_ruff_gate` |
| `prerequisites` | `env PYTHON=$PY bash scripts/generate-prerequisites.sh` |
| `pytest` | `$PY ${PYTEST_ARGV[@]}` |
| `object-birth` | `$PY -m engine.object_birth.gate --gate --quiet` |
| `meta-constitutional` | `bash 00-CMG/tools/cmg-gate.sh` |
| `registration-observation` | `env PYTHON=$PY bash 00-BOOK/tools/register.sh --observe` |

All fifteen resolve. No token is an absolute path.

### 3.2 Key composition — `evidence.py`

`input_digest` gained a **keyword-only, non-defaultable** `contract` parameter, replacing the optional `extra`.

The determination called for using the existing `extra` seam. Implementation departed from that in one respect, deliberately: **`extra` had a default of `()`.** An optional key component reintroduces exactly the defect being closed — a future caller who omits it computes a key that silently covers less than the stage runs, with no error. Making the parameter required means the unsafe call **cannot be written**. This was verified by construction: five pre-existing tests failed with `TypeError: missing 1 required keyword-only argument: 'contract'` and had to be updated explicitly.

`EVIDENCE_VERSION` bumped `1.0 → 2.0`. Key composition changed, so every stored 1.0 entry must become unreachable. This is the module's own declared migration mechanism, used as designed.

### 3.3 Callsites — `plan.py`, `gate.py`

`decide()` gained `root` and `verify` parameters and resolves the contract itself.

`plan.py::_resolve_stages` reads `verify.sh` **once per plan** and passes it to all fifteen decisions — a plan that read the script fifteen times could observe fifteen different versions of it if the file were edited mid-plan.

`gate.py`'s UVI-L-09 check passes the `ctx.verify` source it already holds, so the law measures the same contract the plan computes.

### 3.4 What was NOT changed

No change to: the declaration, the stage registry, the mode constitution, any law, the store layout, the entry schema, `record()`, `lookup()`, the reuse conditions, the certification refusal, `verify.sh`, or any scheduler, selector or dependency-graph code.

---

## 4. Deterministic Key Model

```
sha256(
    EVIDENCE_VERSION            "2.0"
  ‖ stage_id                    declared, from the stage registry
  ‖ stage_label                 declared, reconciled to verify.sh by UVI-L-03
  ‖ "argc:" len(contract)       length prefix — truncation cannot forge a key
  ‖ ∀ i, token in contract:     ORDERED — argv as the script writes it
       "argv:" i ":" token
  ‖ ∀ prefix in sorted(reuse_inputs):        SORTED — a declared input set has no order
       "prefix:" prefix
     ‖ ∀ path in sorted(matched):
          path ":" content_hash             from UCOS-UGA-001, not re-measured
)
```

### 4.1 Order semantics, stated because they differ by field

- **`contract` is ordered.** A shell passes argv in the order written; nothing here may assume the receiving parser is order-insensitive. `--gate --quiet` and `--quiet --gate` are different keys.
- **`reuse_inputs` is sorted.** A set of declared inputs has no order to preserve, and sorting makes the key independent of declaration order.

### 4.2 Normalised (does not change the key)

Line-wrapping, backslash-continuations, indentation, runs of whitespace, and quoting style (`"$PY"` ≡ `$PY`). A maintainer re-wrapping a long invocation must not invalidate its evidence.

### 4.3 Significant (changes the key)

Token addition, removal, substitution, reordering, and token-boundary changes (`"--gate --quiet"` as one token ≠ `--gate`, `--quiet` as two).

### 4.4 Refusals — all return `None`, never a placeholder

| Condition | Rationale |
|---|---|
| stage not reusable, or declares no `reuse_inputs` | pre-existing |
| label appears **≠ 1** times in `verify.sh` | ambiguous contract; unknown widens |
| invocation has unbalanced quoting | unparseable is unknown |
| declared prefix matches no registered object | pre-existing — key would cover nothing |
| matched object carries no `content_hash` | pre-existing |

Every refusal causes the stage to **run**. The failure direction is unchanged and remains fail-wide (UVI-L-07).

---

## 5. Tests Added

Nine new tests. **193 → 202** in the targeted suite, all green.

| Req. | Test | Proves |
|---|---|---|
| — | `test_the_contract_of_every_declared_stage_resolves` | all 15 stages yield a non-empty contract |
| **A** | `test_A_same_inputs_same_command_is_one_key_and_a_hit` | identical inputs + command ⇒ identical key; recorded PASS is reused |
| **B** | `test_B_a_changed_command_is_a_different_key_and_a_miss` | flag added / flag removed / interpreter changed ⇒ distinct key, and `lookup` cannot reach the recorded PASS |
| **C** | `test_C_argument_order_is_significant` | reordering flags ⇒ different key |
| **C** | `test_C_token_boundaries_cannot_be_forged` | one joined token ≠ two split tokens |
| **D** | `test_D_equivalent_serialisations_of_one_command_are_one_key` | 4 written forms (inline, continued, extra whitespace, multi-continued) ⇒ **one** contract, **one** key |
| **E** | `test_E_no_clock_host_path_or_environment_reaches_the_key` | no token is absolute, contains the checkout path, or is home-relative; **and** a second OS process recomputes the identical digest |
| — | `test_a_certification_mode_never_resolves_a_contract_at_all` | UVI-L-09 evaluated *before* the contract — passing a deliberately broken script still refuses |
| — | `test_an_unresolvable_contract_refuses_the_key_rather_than_guessing` | absent / duplicated / unbalanced label ⇒ `None`, and `decide` reports it distinctly |

### 5.1 Mutation proof — the tests measure the defect, not themselves

The key composition was temporarily reverted to 1.0 semantics (contract dropped from the digest) and the suite re-run:

```
FAILED test_B_a_changed_command_is_a_different_key_and_a_miss
FAILED test_C_argument_order_is_significant
FAILED test_C_token_boundaries_cannot_be_forged
3 failed
AssertionError: assert 'cad6343c…' != 'cad6343c…'
```

Restored: `3 passed`. The proofs fail when the fix is absent, which is what makes them proofs.

No test asserts a hardcoded digest. Every key is computed from the real declaration, the real registry and the real script — a frozen digest would pin the composition rather than measure it.

---

## 6. Governance Validation

### 6.1 Prohibitions — all held

| Must not create | Status |
|---|---|
| new registry | **none** — no file added under any registry path |
| new authority | **none** — no declaration, no owner, no law |
| new lifecycle owner | **none** |
| new verification stage | **none** — stage count unchanged at 15 |
| new evidence store | **none** — same `.ucos-verification-evidence/`, same schema |

### 6.2 Reuse — all satisfied

| Must reuse | How |
|---|---|
| existing evidence engine | modified in place; no parallel module |
| existing canonical serialization | `json.dump(..., indent=2, sort_keys=True)` untouched |
| existing hashing primitive | `hashlib.sha256`, unchanged |

### 6.3 Identity ledger — byte-identical

```
before  sha256 1eea127811ef9ef813383e2f569463f1fcc4096c49a8856902c868ecc225bbf0
after   sha256 1eea127811ef9ef813383e2f569463f1fcc4096c49a8856902c868ecc225bbf0
page_cursor 9826 → 9826 · volume_seq 1 → 1 · by_path 1264 → 1264 · category_seq 117 → 117
```

No identity minted. CAA-INV-04 untouched.

### 6.3.1 Four derived-truth artifacts regenerated — disclosed

The `--fast` run also modified **four tracked files**:

```
 M intelligence/UCOS-RIE-CAPABILITY-CATALOG.json
 M intelligence/UCOS-RIE-HEALTH.json
 M intelligence/UCOS-RIE-MODEL.json
 M intelligence/UCOS-IMP-BASELINE-001.rib.json
```

These are UCOS-RIE-001 derived-truth projections of the repository's own test inventory.
They regenerated to record the nine tests added in §5 — `test_A_…` through `test_E_…`
appear as new capability members, and `test_functions` moved 4 614 → 4 623, `loc`
112 996 → 113 139.

**This is correct derived-truth behaviour, not drift.** Adding *any* test to this
repository moves these four surfaces; the change is the projection catching up with the
tree it projects. It is disclosed here rather than left for a reviewer to find because
it is a tracked-tree change this step caused, and the step's own report should not be
the last place it appears.

**Fixed point verified.** The producer was re-run after the `--fast` run and the four
artifacts are byte-identical:

| Artifact | sha256 (16) after `--fast` | after re-run |
|---|---|---|
| `UCOS-RIE-CAPABILITY-CATALOG.json` | `a3324f30464edb70` | `a3324f30464edb70` |
| `UCOS-RIE-HEALTH.json` | `a098422b24020c38` | `a098422b24020c38` |
| `UCOS-RIE-MODEL.json` | `fb0a5143f23ddbfd` | `fb0a5143f23ddbfd` |
| `UCOS-IMP-BASELINE-001.rib.json` | `ac5a07eee12f8fdf` | `ac5a07eee12f8fdf` |

They have converged and are stable. No further regeneration is pending.

### 6.4 The ten laws — all HOLD

```
HOLDS  UVI-L-01  Mode Constitution Completeness
HOLDS  UVI-L-02  Exactly One Default
HOLDS  UVI-L-03  Stage Registry Reconciliation
HOLDS  UVI-L-04  No Assurance Reduction
HOLDS  UVI-L-05  A Mode May Not Claim More Than It Measures
HOLDS  UVI-L-06  Selection Is Derived, Never Authored
HOLDS  UVI-L-07  Fail Wide
HOLDS  UVI-L-08  Execution Topology Neutrality
HOLDS  UVI-L-09  Evidence Reuse Integrity
HOLDS  UVI-L-10  Deterministic Planning
VERDICT: COHERENT (10/10 laws hold)
```

### 6.5 Certification prohibition — strengthened, never weakened

The change can only **reduce** reuse: it adds a component to the key and adds refusal conditions. No path was added by which anything becomes reusable that was not before.

`decide()` still evaluates `mode.evidence_reuse` **first** — before it reads the script, touches the store, or computes a digest. `test_a_certification_mode_never_resolves_a_contract_at_all` proves the ordering by passing a deliberately broken script and observing the refusal anyway.

### 6.6 Ruff

```
All checks passed!
1481 files already formatted
```

Two findings were raised during implementation and fixed at source (an unused import left by the final refactor; one over-length test line) — not suppressed.

---

## 7. Before/After Evidence

Stage `object-birth`, declared contract `$PY -m engine.object_birth.gate --gate --quiet`, measured against the live declaration and registry:

| Command mutation | v1.0 key | v2.0 key | v1.0 | v2.0 |
|---|---|---|---|---|
| declared command (unchanged) | `94f3af99af7e0bb4` | `1a55fd991be36da3` | HIT | HIT |
| `--quiet` removed | `94f3af99af7e0bb4` | `74c422d808300293` | **HIT** | miss |
| `--gate --quiet` reordered | `94f3af99af7e0bb4` | `10d0a0ac7b3e52d9` | **HIT** | miss |
| module repointed | `94f3af99af7e0bb4` | `b2b754aab5238a0d` | **HIT** | miss |

Under 1.0 all four collapse onto **one** key — and that key was a **real stored `PASS`** in the working store. Under 2.0 each is a distinct key, and the stored entry is unreachable:

```
lookup(home, "object-birth", "94f3af99…") → None
```

### 7.1 Store migration, observed

| | before | after `--fast` |
|---|---|---|
| total entries | 20 | 21 |
| reachable (v2.0) | 0 | 1 |
| unreachable (v1.0) | 20 | 20 |

The 20 pre-existing entries were neither mutated nor deleted — immutability preserved. They are simply unaddressable, which is the correct migration: they record what an unidentified command did.

### 7.2 Verification runs

**`./verify.sh --fast` — PASSED**

```
PASS  ruff lint + format-check (engine + platform)                    0s
PASS  prerequisite generation (knowledge · determinism · closure 1-3) 31s
PASS  pytest + coverage gate (--cov-fail-under=90)                   444s
PASS  coverage report                                                 3s
TOTAL (wall clock)                                                   479s
✓ VERIFICATION PASSED — every stage this mode admits is green.
```

The run **escalated to the whole suite under the coverage floor**, because the change touches `engine/verification_intelligence/` — a declared `SELF_PREFIX`. UVI-L-07 fail-wide applied to the selector's own modification, exactly as designed. The `coverage report` stage was consequently re-admitted to a `--fast` plan. Both behaviours are correct and neither was configured for this run.

**Targeted tests — 202 passed** (`test_verification_intelligence.py` + `test_verification_impact.py`).

Per instruction, full four-mode certification was **not** run.

---

## 8. Residual Risks

| # | Risk | Severity | Disposition |
|---|---|---|---|
| R1 | **The contract binds the script's source text, not the executed process argv.** A stage whose argv is assembled in a shell variable (`pytest`'s `${PYTEST_ARGV[@]}`) binds the *literal* token, so a change to how that array is built inside `verify.sh` does not change the key. | **Low** | `pytest` is declared `reusable: false` and can never be cached — the one stage with a computed argv is structurally exempt. No other stage assembles argv dynamically. Any future stage that did would need this reconsidered. |
| R2 | 20 unreachable v1.0 entries remain in the store. | Informational | Correct and intended. Deleting them is Step 7 (retention), out of scope here. |
| R3 | No law measures that the key covers the contract. UVI-L-09 measures reuse *integrity*, not key *totality*. A future edit could remove the contract from the key and all ten laws would still hold. | **Medium** | The nine tests are the current guard and they do fail on removal (§5.1). A law would be strictly stronger. Not in Step 1 scope — recorded for the sequence owner. |
| R4 | `execution_contract` refuses on a label appearing ≠ 1 times, duplicating part of what UVI-L-03 measures. | Low | Deliberate. The law refuses drift as a *verdict*; this refuses a *key*. Both must hold independently — a key that depended on a law having already passed would be a key computed on an assumption. |
| R5 | Three stages (`governance-pre`, `registry-validate`, `meta-constitutional`) still cannot compute a key. | Known | Unchanged by this step, and correctly so — the cause is empty-prefix and withheld-hash refusal, which is Step 1's *sibling* work item, not its scope. Sequence steps A5/A6. |
| R6 | The step made three previously-keyable stages' digests change, so the next `--full` run repays them once. | Negligible | One-time cost of the version bump; measured at ≤ 2 s across the affected stages. |

**No risk identified in this step reduces verification.** R1, R3 and R5 are all conditions under which a stage **runs** rather than being reused.

---

## 9. Readiness for Step 2

**READY.**

Step 2 of the determined sequence is *"Bind stage argv into the evidence key via the existing `extra` seam."*

**Step 2 is discharged by this step.** The sequence separated the withheld/missing distinction (Step 1) from the argv binding (Step 2) on the assumption they were independent. They are not: making `contract` a required parameter — the correct way to close the defect — forces every callsite to supply it in one change. Splitting them would have meant landing an optional parameter first and tightening it afterwards, leaving a window in which the unsafe call was still writable.

What Step 1 as originally scoped did **not** do, and what therefore remains:

- **Distinguishing `content_hash_withheld` from a missing hash** (sequence item A5), and
- **Failing loudly when a declared read-set prefix matches zero registered objects** (sequence item A6).

These are the two causes of R5 and together unblock the three permanently-keyless stages.

### 9.1 Preconditions for the next step, verified

| Precondition | State |
|---|---|
| working tree green under `--fast` | ✅ PASSED |
| all ten laws hold | ✅ 10/10 |
| ruff clean | ✅ |
| identity ledger unmoved | ✅ byte-identical |
| no new registry / authority / stage / store | ✅ |
| targeted tests green | ✅ 202 passed |
| full certification run | ⏸ **not run, per instruction** |

### 9.2 Recommended before any certification claim

`./verify.sh --full` has not been run since this change. It is the only mode that evaluates the coverage floor over the whole suite *without* evidence reuse, and no certification claim should rest on the `--fast` result above — which says so itself in its own summary.

---

**Scope honoured:** Step 1 only. No dependency-graph, impact-model, artifact-integration or scheduler changes. No new registry, authority, lifecycle owner, verification stage or evidence store. Existing evidence engine, canonical serialization and hashing primitive reused.

**STOP — STEP 1 COMPLETE. Step 2 not commenced.**
