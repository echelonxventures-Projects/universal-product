# UCL GAP CLOSURE REPORT

**UCL-V-41 and UCL-V-42 — root-cause analysis and authorization determination**

| Field | Value |
|-------|-------|
| Report class | Gap closure analysis (Task 1) |
| Authority | NONE — DERIVED TRUTH. This report measures and determines authorization; it changes no artifact. |
| Temporal anchor | Logical: `git HEAD = 03179308` |
| Temporal reference system | `logical:git-commit-order@ucos-consolidation` |
| Location / reality context | Repository reality `UCOS-CONSOLIDATION`; no planetary, calendar or civilizational frame asserted |
| Method | Every number below is a command output. No certification artifact was modified to produce it. |

---

## 1. The two failures

```
BLOCKING UCL-V-41  relationships whose target carries no registered constitutional
                   identity stay within the disclosed bound: 274 <= 217  failed
BLOCKING UCL-V-42  the DISTINCT artifacts the Universal Registry does not admit stay
                   within the disclosed bound: 85 <= 84  failed

UCL-000001: UNIVERSAL-CONSTITUTIONAL-LIFECYCLE-NOT-ESTABLISHED | gate=CLOSED
```

These two are the **only** UCL failures. Everything else the programme measures passes.

---

## 2. Canonical source of truth

| Artifact | Class | Role |
|---|---|---|
| `00-MASTER/UCL-000001/ucl-declaration.json` | **GOVERNED_DECLARATION** — authored | **The source of truth.** Declares `UCL-V-41.expect = 217` and `UCL-V-42.expect = 84`. |
| `00-MASTER/UCL-000001/ucl.json` + 13 markdown registers | **GENERATED_ARTIFACT** — producer `ucl_engine.py` | Derived. Never hand-authored. |

Mutation class per `00-BOOK/DATA/mutation-governance-boundary.json`: `GOVERNED_DECLARATION`, whose `governed_by` is *"the owning programme authority declared by the artifact itself (owner-parameterised) → verify.sh (observation only) → Phase 8 → Phase 9"*. The owning authority is UCL-000001. Note the same class explicitly records that it **"grants no certification authority, no ratification authority and no freeze authority"** (CEP-009 I.1).

**The bounds are therefore changed in the declaration, and only in the declaration.** Editing `ucl.json` directly would be editing a derived artifact and is refused.

---

## 3. Is the failure caused by stale generated bounds?

**No — and this distinction is the core of the report.** The *bounds* are not stale; they are correctly recorded values of a past measurement. What is stale is the **committed generated reading**, and what has changed is the **repository**.

| Reading | `ckos` | `knowledge_objects` | `relations` | `rel_without_target_identity` | `unadmitted_target_artifacts` | `blocking_failures` |
|---|---|---|---|---|---|---|
| Committed `ucl.json` (at `de9b9f3e`) | 3403 | 130 | 474 | **217** | **84** | `[]` |
| Live measurement (at `03179308`) | 3483 | 142 | 531 | **274** | **85** | `[UCL-V-41, UCL-V-42]` |

At the moment the bounds were set, `217` and `84` **were** the measured values. The declaration says so in its own `detail` field: *"The bound is a RATCHET held at exactly the measured value."*

### 3.1 Evidence lineage of the drift

| Fact | Evidence |
|---|---|
| Bounds last set | commit `9a398edc` — *P0-ULTIMATE-CLOSURE-001: resolve UCL-V-41 at its root* |
| `ucl.json` last regenerated | commit `de9b9f3e` — *P0-FINAL-CLOSURE-002: fixed-point round 2* |
| Commits landed since without regenerating | **77** |
| The one new unadmitted artifact | `engine/constitution/stages.py` |
| Introduced by | commit `8bad683f` — *P0-LIFECYCLE-CLOSURE-001: realize all 45 lifecycle stages; close RIB orphan defect* |
| `8bad683f` is after `de9b9f3e` | `git merge-base --is-ancestor de9b9f3e 8bad683f` → **true** |

The drift is the accumulated consequence of 77 commits of lawful work during which the UCL registers were never re-derived. **It is not caused by Phase 4:** measured with every Phase 4 change stashed at clean `HEAD`, the counts are byte-identical at 274 and 85.

---

## 4. Delta measured BY IDENTITY, as the declared rule requires

The declaration's own procedure is to re-take the snapshot against the reading at which the ratchet was last set, and to measure the delta **by identity, not by count**. Applied:

```
committed unadmitted targets : 84
current   unadmitted targets : 85

ADDED   (1):  + engine/constitution/stages.py
REMOVED (0):
```

**Exactly one artifact added. None removed.** This reproduces the precedent recorded in the declaration verbatim — `83 → 84, exactly one added, and none removed`.

### 4.1 The added artifact is the disclosed condition, not a new one

The disclosed condition is *"a located artifact that the Universal Registry does not admit"*. Measured against the registration authority `00-BOOK/tools/ukb.py::eligibility_universe()`:

| Test | Result |
|---|---|
| `engine/constitution/stages.py` in eligibility universe | **False** |
| `engine/constitution/stages.py` registered | False |
| Any `engine/**/*.py` in the eligibility universe | **0** |

Engine source is categorically outside the corpus eligibility universe, so `engine/constitution/stages.py` **cannot** carry a corpus identity. Its registration is not merely declined — it is unavailable. This is the disclosed condition exactly.

### 4.2 The decisive authorization test passes

The declaration conditions the ratchet on: *"No target that COULD carry an identity is in this population."* Measured:

```
unadmitted targets                                    : 85
eligible-but-unregistered                             : 192
targets that COULD carry an identity but do not       : 0     <-- decisive
unadmitted targets that are INELIGIBLE                : 85 / 85
```

**Zero.** Every one of the 85 unadmitted targets is ineligible for registration. No relationship in this population points at something that could have been registered and was not. The condition holds.

### 4.3 Why edges moved by 57 while the disclosed condition moved by 1

This is the exact phenomenon the engine's own source comments on (`ucl_engine.py:1068-1077`):

> *"A relationship count conflates 'the graph reaches a new corner of the corpus the registry cannot name' with 'more edges point at a corner already disclosed'. The second grows with legitimate knowledge-base growth for no constitutional reason … Only the target measure detects a genuinely new unadmitted corner at +1."*

`unadmitted_target_artifacts` is constructed as the **set of targets of exactly those relationships counted by `UCL-V-41`** (`ucl_engine.py:1078-1080`). The 274 relationships therefore reach the 85 targets by construction, and all 85 are ineligible (§4.2). The +57 edges are knowledge-base growth (knowledge objects 130 → 142) reaching already-disclosed and one newly-disclosed ineligible corner. No edge reaches a registrable target.

---

## 5. A discrepancy in the declaration's rationale, disclosed

The declaration's `detail` asserts, as supporting rationale: *"measured at this commit, the eligibility universe (`ukb.eligibility_universe()`, 1232 paths) and the registered artifact set (`00-BOOK/DATA/artifacts.json`, 1232 paths) are identical in both directions, so eligible-but-unregistered is 0."*

Measured now: eligibility universe **1425**, registered **1233**, eligible-but-unregistered **192**.

That sentence is no longer true. It matters that this is stated plainly, because it was part of the argument the bound rests on. Two things follow:

1. The **operative** condition of the ratchet is unaffected. That condition is about the unadmitted **target** population, and it still holds exactly (§4.2: zero targets could carry an identity). The rationale sentence was a stronger, repository-wide claim that happened to be true at the time; its failure does not admit a registrable target into the population.
2. The 192 eligible-but-unregistered documents are a **separate, larger finding** — corpus-registration drift — recorded below as `UCL-F-006` and **not** resolved by this report. It is the same drift the UGA gate reports as `UGA-INV-01` / `UGA-INV-10` (24 violations in its own universe). Resolving it is a `CORPUS_REGISTRATION` mutation, governed by `REG-AUTO-001 → 00-BOOK/tools/register.sh (ukb.py build --mint)`, which mints **permanent, append-only, never-renumberable** identities. That is out of scope for a bound re-tightening and must not be bundled into it.

---

## 6. Everything else UCL measures passes

All thirteen self-checks, run at `03179308`:

| Check | Result | Check | Result |
|---|---|---|---|
| `check-declaration` | **PASS** | `check-open-world` | **PASS** |
| `check-no-enumeration` | **PASS** | `check-no-parallel-authority` | **PASS** |
| `check-write-scope` | **PASS** | `check-lifecycle-executable` | **PASS** |
| `check-determinism` | **PASS** | `check-cko-identity` | **PASS** |
| `check-implementation-independence` | **PASS** | `check-semantic-identity` | **PASS** |
| `check-bounds-tight` | **PASS** | `check-knowledge-once` | **PASS** |
| | | `check-record-immutability` | **PASS** |

Also measured: `stages=45`, `order=45 cycles=0`, `adapters=10/10`, `graphs=13/13`, `axes=32/32`, `properties=0unmet`, `runs=3/3det`, `criteria=40/42`. The two failing criteria are exactly `UCL-V-41` and `UCL-V-42`.

### 6.1 The two guards force the bound to equal the measurement

`check_bounds_tight` (`ucl_engine.py:2894-2900`) reports every bound where `bound > measured` — i.e. **slack**. It currently PASSES because `217 < 274` is a *breach*, not slack.

Composing the two guards:

- `UCL-V-41/42` fail if **measured > bound**
- `check-bounds-tight` fails if **bound > measured**

Therefore the only state satisfying both is **bound == measured, exactly**. This is what makes it a ratchet rather than a budget, and it is also the guard that makes inflating the bound to hide a future regression impossible: setting `expect` to anything above 274 or 85 would immediately fail `check-bounds-tight`.

**Consequence: the only lawful values are exactly 274 and 85.** There is no discretion.

---

## 7. Determination

### Is the failure caused by stale generated bounds?

**No.** The bounds are accurate records of a past measurement. The committed *generated reading* is stale by 77 commits, and the *repository* has lawfully grown. The failure is a ratchet that has not been re-tightened.

### Is regeneration authorized?

**Yes, for the generated artifacts** — `ucl.json` and the 13 registers are declared GENERATED_ARTIFACTs whose declared producer is `ucl_engine.py`. Re-deriving them is a producer action, not an evolution.

**Yes, for the bound re-tightening** — the declared ratchet rule authorizes it: *"re-tightened whenever governed records are lawfully admitted."* Every condition the rule attaches is measured and satisfied:

| Condition | Status |
|---|---|
| Delta measured by identity, not count | ✓ +1 / −0 |
| Each added target is the same disclosed condition | ✓ ineligible; no `engine/**/*.py` is registrable |
| No target that could carry an identity is in the population | ✓ 0 of 85 |
| Introduced by lawful admission of governed records | ✓ `8bad683f` P0-LIFECYCLE-CLOSURE-001 |
| Bound set to exactly the measured value | ✓ 274 and 85 are the only values passing both guards |
| Not caused by the change being certified | ✓ identical counts with Phase 4 stashed |

### Does governance approval exist?

**The rule exists; the instance requires registration.** The ratchet rule is declared in the governed declaration, and precedent moves (`92→98` under Ω-E05, `98→217` under P0-ULTIMATE-CLOSURE-001) were each carried by a governance commit that also amended the declaration's `detail` with its delta-by-identity evidence.

Under CEP-002 Article 28, amending a declared bound is a decision that must be registered in a located register before implementation. **No registered decision authorizing this specific move exists yet.** It must be created — `adr/0014` plus a UCDA entry — before the declaration is touched.

### What is the canonical source of truth?

`00-MASTER/UCL-000001/ucl-declaration.json`. The bounds live there and nowhere else. `ucl.json` and the 13 registers are projections of it and of the repository.

---

## 8. Authorized closure path

1. Register `adr/0014` + `DEC-ADR-0014` under CEP-002 Art 28, carrying the §4 delta-by-identity evidence.
2. Amend `ucl-declaration.json`: `UCL-V-41.expect 217 → 274`, `UCL-V-42.expect 84 → 85`, appending the delta evidence to each `detail` in the style the prior two moves used.
3. Re-derive via the declared producer: `python3 00-MASTER/UCL-000001/ucl_engine.py --render`.
4. Verify `--gate` exits 0, `--check-bounds-tight` PASSES (proving no slack was introduced), and all thirteen self-checks still PASS.
5. Commit declaration and regenerated artifacts together, so no derived artifact is ever committed out of step with its source again.

## 9. Findings recorded

| Finding | Owner | Detail |
|---|---|---|
| `UCL-F-006` | REG-AUTO-001 / UGA-000001 | 192 eligible-but-unregistered corpus documents (UGA measures 24 in its own universe as `UGA-INV-01`/`UGA-INV-10`). The declaration's rationale sentence asserting this is 0 is no longer true. Not resolved here: it is a `CORPUS_REGISTRATION` mutation minting permanent, never-renumberable identities. |
| `UCL-F-007` | UCL-000001 | The committed generated reading drifted 77 commits from its declaration. Recommend binding UCL re-derivation into the routine gate sequence so a derived artifact cannot be committed out of step with its source. |

**This report modifies no artifact.** Steps 1–5 are the authorized path and are executed separately.
