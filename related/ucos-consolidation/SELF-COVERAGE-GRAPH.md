# Self-Coverage Closure — Certification Graph

| Field | Value |
|---|---|
| MISSION | Measure self-coverage closure. Build the complete certification graph. |
| AUTHORITY | **NONE — DERIVED TRUTH.** This document certifies nothing, ratifies nothing, creates no authority and repairs nothing. Every value was produced by executing the repository's own engines and reading its own committed registers. |
| METHOD | Read-only measurement. The enforcement surface was located with the repository's own discovery rules (`engine/enforcement_closure/discovery.py`) rather than a second inventory, so this graph cannot disagree with `UEC-000001` about what exists. |
| BASELINE | HEAD `446f8a0f`, branch `integration/recovery-001` |
| TREE STATE | **DIRTY — 91 `git status --porcelain` entries when measurement began.** A concurrent mutation campaign was rewriting `engine/enforcement_closure/contract.py` during the window; it restored the file and every figure was re-measured on the restored tree (§3). |
| SCOPE | Requirement → Certifier → Certifier-of-Certifier → Closure Proof → Certification Gate |
| DISPOSITION | **MEASUREMENT ONLY.** No repair performed. Companion: `SELF-COVERAGE-GAPS.md`. |

---

## 1 · What "certifies" means here, as measured

The repository does not implement certification as attestation. No artifact anywhere names a
certifier distinct from its own author, and this is deliberate: `00-CMG/CMG-000001` **LI.6**
forbids self-issued certification, `T1` (the ratifying tier) is **VACANT** (`VAC-01`,
`DR-RAT-11`), and so every certificate leaves the certifier slot empty and substitutes a
*method* — an engine, a baseline commit and a `sha256` seal — for a signature.

The certification relation therefore had to be measured as five distinct, separately observable
edge types rather than one. Each is mechanically checkable:

| Edge type | Reads as | How measured |
|---|---|---|
| `derives-verdict` | X computes the certification status of Y | engine reads Y, writes the verdict register |
| `invokes` | X can actually cause Y to run | `discovery.invokers` over the workflow/Make/verify corpus |
| `proves-can-refuse` | a test demonstrates Y is able to fail | `discovery.test_bindings` over 604 collected tests |
| `governs-existence` | X fails closed if Y disappears | membership in `UEC-000001`'s governed inventory |
| `would-ratify` | X confers standing on Y | **no instance exists in-corpus** |

The fifth row is the finding that shapes everything below: the graph has four working edge types
and one that is empty everywhere.

---

## 2 · Node census

| Plane | Node kind | Count | Source of truth |
|---|---|---:|---|
| **1 · REQUIREMENT** | `RR-<CONCEPT-ID>` | **549** | `00-MASTER/UAKOS-CLOSURE-009/requirements.json` (seal `b9d62642…`) |
| | `REQ-nn` | **49** | `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md` |
| **2 · CERTIFIER** | `GATE_ENGINE` | **39** | `00-MASTER/*/*_engine.py` (UEC-R-01) |
| | `MODULE_GATE` | **9** | `engine/*/gate.py` (UEC-R-02) |
| **3 · CERTIFIER-OF-CERTIFIER** | meta-gate | **1** | `UEC-000001` |
| | trust anchor | **1** | `REG-AUTO-001` |
| | constitution | **1** | `CMG-000001` LI.6 |
| | root authority | **1 (VACANT)** | `T1` — `VAC-01` / `DR-RAT-11` |
| **4 · CLOSURE PROOF** | `DECLARATION` | **20** | `00-MASTER/*/*-declaration.json` (UEC-R-06) |
| | result register carrying a verdict field | **83** | `00-MASTER/*/*.json` |
| | programme certificate document | **77** | `00-MASTER/*/*CERTIFIC*.md` |
| | root certificate document | **26** | `*CERTIFICAT*.md` at repository root |
| **5 · CERTIFICATION GATE** | `WORKFLOW` | **32** | `.github/workflows/*.yml` (UEC-R-03) |
| | `MAKE_GATE_TARGET` | **54** | `Makefile` `.*-gate$` (UEC-R-04) |
| | `VERIFY_STAGE` | **18** | `verify.sh` `run_stage` (UEC-R-05) |

Governed enforcement inventory: **172 artifacts**, matching `UEC-000001` exactly
(`DECLARATION` 20, `GATE_ENGINE` 39, `MAKE_GATE_TARGET` 54, `MODULE_GATE` 9, `VERIFY_STAGE` 18,
`WORKFLOW` 32). Tracked files scanned: **6,751**. Tests collected: **604**. Withdrawals: **0**.

Constructed graph size: **322 nodes, 371 edges, 40 self-loops, 0 multi-node strongly-connected
components.**

---

## 3 · The meta-gate verdict, executed at this baseline

```
$ python -m engine.enforcement_closure.gate --json      # exit 0
status: OPEN · laws 13 · holds 13 · refused 0 · blocking_refusals 0
declaration_digest: cffb41b32c9eba5bffe824e08c90c151d9a762168ea0bb6759eba74d0a390c6f
```

All thirteen `UEC` laws hold, including **UEC-L-09 `self_coverage_is_a_fixed_point`** — the
"GUARD OF GUARD" law. `UEC-000001` lists its own five artifacts inside its own inventory and
refuses if it does not.

> ### Condition of measurement: the tree was mutating while this graph was measured
>
> A concurrent per-law mutation campaign was running against
> `engine/enforcement_closure/contract.py` throughout the measurement window. It neutered one law
> body at a time (`return []  # MUTANT`), ran `engine/tests/unit/test_enforcement_closure.py`, and
> restored the file after each mutant. Transient mutants were observed in
> `certification_identity_is_complete` (UEC-L-13) at 14:38 and `every_declaration_is_consumed`
> (UEC-L-07) at 14:42. The campaign completed and verified its own restoration:
>
> ```
> total killed 13  SURVIVED 0
> contract restored: True
> $ git diff --stat engine/enforcement_closure/contract.py     # empty — restored
> ```
>
> **Every measurement in this document was re-executed on the restored tree and is byte-identical
> to the pre-campaign run** (48 certifiers, 18 unverified, 6 unreachable, 16 single-plane, 3 inert,
> 322 nodes, 371 edges, 40 self-loops, declaration digest `cffb41b32c9eba5b`). The ratcheted
> helpers this graph calls are distinct from the law functions the campaign neutered, so no figure
> here was taken through a mutant.
>
> **The campaign also settles a question this graph would otherwise have to leave open.** All 13
> `UEC` law mutants were **KILLED** by the test suite. That is the strongest falsifiability
> evidence available anywhere in this repository, and it holds for exactly one programme.
>
> One narrower observation, made directly while a mutant was live and reproducible by anyone
> repeating it: with `certification_identity_is_complete` neutered,
> `python -m engine.enforcement_closure.gate --law UEC-L-13 --gate` **exited 0 and reported
> HOLDS**. Running the gate does not detect a neutered law body; only the test suite does. For
> `UEC` that suite exists and kills all 13. For the 18 certifiers in `SC-G1` no such test exists,
> so the identical mutation would survive unobserved. That asymmetry is the substance of `SC-G1`,
> and it is now empirical rather than inferred.

The ratchet is the load-bearing detail. Four measurements sit **exactly at their declared
ceiling**, which is what "OPEN" means here:

| Ratcheted measurement | Declared ceiling | Measured | Law |
|---|---:|---:|---|
| `engines_without_a_test` | 18 | **18** | UEC-L-05 |
| `artifacts_with_one_invocation_plane` | 16 | **16** | UEC-L-06 |
| `engines_with_no_invoker` | 6 | **6** | UEC-L-04 |
| `declarations_no_code_consumes` | 3 | **3** | UEC-L-07 |
| `declarations_without_a_certification_identity` | 0 | **0** | UEC-L-08 |

The meta-gate is OPEN **and** 18 certifiers are unverified, 6 are unreachable. Those are not in
tension: the ratchet caps the debt so it cannot grow, and refuses if a repair fails to tighten
the ceiling. It does not assert the debt is absent. `SELF-COVERAGE-GAPS.md` enumerates it.

---

## 4 · Plane 1 → Plane 2: who certifies a requirement

### 4.1 The `RR-*` population (549)

Every requirement's certification status is derived by one engine:

```
RR-<CONCEPT-ID> ×549
  ← derives-verdict ← 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py
      ← invokes ← .github/workflows/closure009-gate.yml   (2 steps continue-on-error: true)
      ← invokes ← Makefile :: closure009-gate
      ← proves-can-refuse ← engine/tests/unit/test_closure009_requirement_engine.py
      ← governs-existence ← UEC-000001
          ← self-coverage ← UEC-000001            (self-loop, UEC-L-09, mutation-tested)
              ← REG-AUTO-001                       (unregistered under itself)
                  ← CMG-000001 LI.6
                      ← T1                         (VACANT — chain ends)
```

The certifier is governed, invoked from two planes and covered by a test. Its **gate** is not
blocking: `closure009-gate.yml` carries the repository's only two `continue-on-error: true`
steps, and both sit on the `--gate` and `--baseline-gate` invocations. The 549 requirement
verdicts are therefore *measured* in CI and *not enforced* by it.

Measured status of the 549:

| Field | Distribution |
|---|---|
| `certification_status` | `UNCERTIFIED` **308** · `CERTIFIED-PROVISIONAL` **241** |
| `verification_status` | `NOT-EVIDENCED` **294** · `EVIDENCED` **255** |
| `validation_status` | `NOT-EVIDENCED` **327** · `TEST-ONLY` **133** · `EVIDENCED` **89** |
| `runtime_status` | `NO-RUNTIME-EVIDENCE` **549 / 549** |
| `maturity_level` | M1 177 · M6 161 · M3 98 · M2 42 · M4 40 · M0 16 · M5 15 |
| full `constitution→requirement→implementation→test→evidence→certification` chain | **70 / 549** |
| register determination | `ASSIMILATION-INCOMPLETE` · `baseline_permitted: false` · BC-01…BC-08 all **FAIL** |

**No requirement identifier reaches the enforcement surface.** Grepping all 32 workflows, the
`Makefile`, `verify.sh` and every collected test for all 549 `RR-*` identifiers returns
**0 matches**. The requirement plane and the gate plane share no vocabulary.

### 4.2 The `REQ-nn` population (49)

Nine `REQ-nn` tokens appear in test sources. Five (`REQ-00`, `REQ-50`…`REQ-53`) are synthetic
fixtures in `engine/tests/uckp/test_phase_2_requirement_evolution.py`. Of the four remaining,
two bind a **different subject** than the register assigns to that ID:

| ID | Master index subject | Subject in the test that names it | Match |
|---|---|---|:-:|
| `REQ-23` | Space not conflated with path string (`engine/context/location.py`) | "extend evolution ledger to support requirement evolution" | **no** |
| `REQ-28` | 192-document corpus-registration population (**OPEN GAP**) | context-kind extensibility (`test_req_28_extensibility.py`) | **no** |
| `REQ-37` | impact-selector tracks real coupling | named in a comment only | comment |
| `REQ-43` | storage neutrality for `KnowledgeStore` (**OPEN GAP**) | named in a comment only | comment |

The `REQ-nn` namespace is **not injective**: the same identifier denotes different requirements
in the register and in the test corpus. No `REQ-nn` has a machine-checkable binding to a gate.

---

## 5 · Plane 2 → Plane 4: certifier and the proof it writes

**37 of 39 `GATE_ENGINE` certifiers write their verdict register into their own home directory.
31 have an artifact whose filename contains `CERTIFIC` in that same directory.** By contrast
only **1 of 9 `MODULE_GATE` certifiers** does — `engine/*/gate.py` renders nothing beside
itself, and `UEC-000001`'s gate declares `plane: READ_ONLY` with no `--render` and no `--write`
on the stated ground that "a gate that emits no artifact cannot drift from it, and cannot be
satisfied by regenerating its own expectation."

That 37/39 vs 1/9 split is the architectural fault line of the whole graph. It is the same
defect `GATE-PURITY-DETERMINATION.md` records as D-3.0: what these engines declare is a write
*scope*, not a write *mode*, so an engine passes `--check-write-scope` while rewriting the very
register its verdict compares against, because its home is inside its own permitted scope.

### Certifier slot on the proofs themselves

103 certificate documents were parsed (77 programme, 26 root). **101 declare `AUTHORITY = NONE`
or carry no authority line at all.** The 2 residual matches were inspected by hand and name no
certifier either (one is a plan, one asserts only "Repository Truth"). Measured result:

> **103 of 103 certificate documents have a vacant certifier slot.**

And the proofs are not re-verified by anything:

| Population | Total | Referenced by any workflow, Makefile target or verify stage |
|---|---:|---:|
| Programme certificates (`00-MASTER/*/*CERTIFIC*.md`) | 77 | **1** |
| Root certificates (`*CERTIFICAT*.md`) | 26 | **2** |

---

## 6 · Plane 5: the gate plane, and whether both planes are real

`UEC-L-06` requires every enforcement artifact to be reachable from two independent invocation
planes, so that deleting one leaves a signal. Measured plane multiplicity across the 48
certifiers:

| Planes reachable from | Certifiers |
|---:|---:|
| 3 (workflow + Make + verify.sh) | 5 |
| 2 | 27 |
| 1 | 10 |
| **0** | **6** |

The second plane is structurally present and **almost entirely unexercised by CI**. Of the 54
governed `MAKE_GATE_TARGET` nodes:

- **3** are invoked by a workflow — `constitution-gate`, `convergence-gate`, `freeze-gate`, all
  from `ufc-gate.yml`
- **0** are invoked by `verify.sh`
- **51** are reachable only by a human typing `make`

`verify.sh` registers 19 `run_stage` invocations over **18 distinct labels** (the label
`pytest + coverage gate (--cov-fail-under=90)` is registered twice); all 18 are governed.
`ec1-ci.yml` does invoke `./verify.sh --full`, so the verify plane is genuinely exercised.

Blocking posture across the 32 workflows: **1** workflow contains `continue-on-error: true`
(`closure009-gate.yml`, 2 steps); **11** contain a `|| true` construct.

---

## 7 · Recorded verdicts on disk at this baseline

83 registers under `00-MASTER/` carry a verdict field; 55 declare `authority` containing `NONE`.
Three record a closed gate right now:

| Register | Recorded state |
|---|---|
| `00-MASTER/UCCEP-000000/uccep.json` | `gate_exit: 1` · `certification: NOT-CERTIFIED` · `blocking_failures: ["CK-ACEE"]` |
| `00-MASTER/UCOS-RIB-001/rib.json` | `gate: CLOSED` · `gate_exit: 1` · `BLUEPRINT NOT CERTIFIED — REPOSITORY MUST STOP` |
| `00-MASTER/UCOS-UFEP-001/ufep.json` | `gate: CLOSED` · `gate_exit: 1` · `blocking_failures: ["UFEP-VAL-14"]` |

`UCCEP-000000` is the aggregate constitutional certification gate: 26 gates `G-01`…`G-26`,
verdicts **24 PASS · 1 PASS-WITH-ADVISORY · 1 FAIL**. Note the two most relevant rows:

- `G-11` **"Certification Gate"** (owner `00-CEP/CEP-005`) — `PASS-WITH-ADVISORY`, advisory
  failure `CK-HEALTH`. The gate that certifies certification passes with an advisory.
- `G-26` **"Autonomous Constitutional Engineering Gate"** (owner `00-MASTER/ACEE-000001`) —
  `FAIL` on `CK-ACEE`, and it is the sole blocking failure capping the whole cluster.

`uccep.json` carries an `independent_view` block keyed by 20+ constituent homes, added
specifically to break the ACEE↔UCCEP reading fixed point documented in
`P0-ULTIMATE-CLOSURE-CERTIFICATION.md` §1. Certification ceiling recorded in the register:
`UCCEP-F-004` — "constitutional finality is reserved to an out-of-corpus authority, so every
in-corpus determination is capped at provisional acceptance."

---

## 8 · Termination and cycle analysis

### 8.1 Does the chain terminate?

Every chain terminates. None terminates in a certified authority.

| Terminus | Kind | Measured evidence |
|---|---|---|
| `UEC-000001` | **self-loop** | `self_coverage.artifacts` lists UEC's own gate, declaration, workflow, Make target and verify stage; UEC-L-09 refuses if it does not |
| `REG-AUTO-001` | **uncertified root** | 0 of 1,597 registered artifacts lie under `00-BOOK/tools/`; the registration mechanism is not registered under itself (discovery `D-09`) |
| `T1` ratification authority | **vacant root** | `VAC-01` / `DR-RAT-11`; `00-MASTER/P0-FINAL-CLOSURE-002/UCOS-UNCONDITIONAL-CERTIFICATION.json` records `outcome_from_inside_the_corpus: "PROHIBITED"`, ceiling `CERTIFIED-PROVISIONAL` |
| 6 engines | **unreachable** | no plane invokes them; the chain has no downward edge to enter from |

### 8.2 Do cycles exist?

| Cycle class | Count | Detail |
|---|---:|---|
| Self-loops (certifier certifies its own home) | **40** | 39 `GATE_ENGINE` + `UEC-000001` |
| Multi-node cycles in the governance graph | **0** | Tarjan SCC over 322 nodes / 371 edges: every SCC is a singleton |
| Engine → engine invocation cycles | **0** | 17 naming edges between engines, acyclic |
| Data-dependency cycles (engine reads a register another engine writes) | **1** | `00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py` ⇄ `00-MASTER/UKAP-001/corpus_engine.py` (via `EVIDENCE-MANIFEST.json` / `assimilation.json`) |

52 cross-programme data-dependency edges were measured. The dependency plane is a DAG rooted at
`closure.json` with exactly one two-node cycle. The classic ACEE↔UCCEP circularity does **not**
appear as a code cycle at this baseline: `acee_engine.py` does not read `uccep.json` and
`uccep_engine.py` does not name ACEE; the coupling now runs through `uccep-bindings.json`
(which does name ACEE) and is mediated by the `independent_view` repair.

### 8.3 The two planes do not overlap

`UEC-L-10 planes_are_disjoint` holds, and the measurement is stark. Of 1,597 artifacts
registered under `REG-AUTO-001`:

| Under the registration boundary | Count |
|---|---:|
| `.py` files | **0** |
| `.yml` files | **0** |
| paths under `.github/` | **0** |
| paths under `00-MASTER/` | **0** |
| paths under `00-BOOK/tools/` | **0** |
| root-level `.md` files | 434 |

Neither `00-BOOK/DATA/artifacts.json` nor `00-BOOK/DATA/certification.json` is registered in
`artifacts.json`. And `00-BOOK/DATA/certification.json` — which records
`verdict: "CERTIFIED"`, `domains_passed: 10/10` under standard `UMB-017` — is in **neither**
closure plane: not registered by `REG-AUTO-001`, not present in `UEC-000001`'s governed
inventory. The repository's most affirmative certification verdict is the one object no closure
mechanism covers.

---

## 9 · Full certifier table

Planes: `WORKFLOW` / `MAKE` / `VERIFY`. "Self-certifies own home" = the engine writes its verdict
register or a `CERTIFIC*` artifact into the directory it lives in.

| # | Certifier (node) | Kind | Self-certifies own home | Planes | Invokers | Test binding | Status |
|---:|---|---|:-:|:-:|---|---|---|
| 1 | `00-MASTER/ACEE-000001/acee_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/acee-gate.yml`, `.github/workflows/uec-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 2 | `00-MASTER/BASELINE-001/baseline_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/baseline-gate.yml`, `Makefile` | `test_rie.py` | COVERED |
| 3 | `00-MASTER/MCOS-000001/mcos_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/mcos-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 4 | `00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | **none** | **UNVERIFIED** |
| 5 | `00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | **none** | **UNVERIFIED** |
| 6 | `00-MASTER/UAEP-000001/uaep_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/uaep-gate.yml`, `Makefile` | `test_uaep_platform_binding.py` | COVERED |
| 7 | `00-MASTER/UAIE-000001/uaie_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/uaie-gate.yml`, `Makefile` | `test_uaie_architectural_intelligence.py`, `test_generated_artifact_registry.py` | COVERED |
| 8 | `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/roadmap-gate.yml`, `Makefile` | `test_closure009_requirement_engine.py`, `conftest.py`, `test_research_intelligence.py` | COVERED |
| 9 | `00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | `test_closure009_requirement_engine.py`, `conftest.py`, `test_research_intelligence.py` | COVERED |
| 10 | `00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | `test_closure009_requirement_engine.py`, `conftest.py`, `test_research_intelligence.py` | COVERED |
| 11 | `00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/assimilation-gate.yml`, `Makefile` | `test_corpus_currency.py`, `test_repository_decision.py`, `test_superiority_evaluation.py`, `test_canonical_validation_evidence.py` | COVERED |
| 12 | `00-MASTER/UAKOS-CLOSURE-008/decision_engine.py` | GATE_ENGINE | YES | 0 | **none** | `test_corpus_currency.py`, `test_repository_decision.py`, `test_superiority_evaluation.py`, `test_canonical_validation_evidence.py` | **UNREACHABLE** |
| 13 | `00-MASTER/UAKOS-CLOSURE-008/superiority_engine.py` | GATE_ENGINE | YES | 0 | **none** | `test_corpus_currency.py`, `test_repository_decision.py`, `test_superiority_evaluation.py`, `test_canonical_validation_evidence.py` | **UNREACHABLE** |
| 14 | `00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/closure009-gate.yml`, `Makefile` | `test_closure009_requirement_engine.py` | COVERED |
| 15 | `00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py` | GATE_ENGINE | YES | 0 | **none** | **none** | **UNREACHABLE** |
| 16 | `00-MASTER/UAKOS-PHASE-001B/provenance_engine.py` | GATE_ENGINE | YES | 0 | **none** | `test_corpus_currency.py` | **UNREACHABLE** |
| 17 | `00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py` | GATE_ENGINE | no | 0 | **none** | **none** | **UNREACHABLE** |
| 18 | `00-MASTER/UCCEP-000000/uccep_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/uccep-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 19 | `00-MASTER/UCDA-000001/ucda_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | **none** | **UNVERIFIED** |
| 20 | `00-MASTER/UCEF-000001/ucef_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/ucef-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 21 | `00-MASTER/UCL-000001/ucl_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/ucl-gate.yml`, `Makefile` | `test_lifecycle_lineage_evolution.py`, `test_object_birth.py` | COVERED |
| 22 | `00-MASTER/UCOS-AEE-001/aee_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/aee-gate.yml`, `Makefile` | `test_generated_artifact_registry.py`, `test_mutation_governance_boundary.py`, `test_observation_universe.py` | COVERED |
| 23 | `00-MASTER/UCOS-MXR-001/roadmap_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/roadmap-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 24 | `00-MASTER/UCOS-RFP-001/rfp_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/rfp-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 25 | `00-MASTER/UCOS-RIB-001/rib_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/rib-gate.yml`, `Makefile` | `test_generated_artifact_registry.py`, `test_mutation_governance_boundary.py`, `test_observation_lineage_boundary.py`, `test_observation_universe.py`, `test_repository_contamination.py` | COVERED |
| 26 | `00-MASTER/UCOS-UAR-001/uar_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/uar-gate.yml`, `Makefile` | `test_uar_analysis_registry.py` | COVERED |
| 27 | `00-MASTER/UCOS-UCAF-001/ucaf_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | `test_constitutional_convergence.py` | COVERED |
| 28 | `00-MASTER/UCOS-UFEP-001/ufep_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | `test_constitutional_convergence.py` | COVERED |
| 29 | `00-MASTER/UCOS-UGA-001/uga_engine.py` | GATE_ENGINE | YES | 2 | `Makefile`, `verify.sh` | `test_birth_scope.py`, `test_infinite_scope.py`, `test_temporal_contract.py`, `test_verification_impact.py`, `test_verification_intelligence.py`, `test_constitutional_authority_alignment.py`, `test_observation_universe.py`, `test_verification_purity.py` | COVERED |
| 30 | `00-MASTER/UCOS-URAT-001/urat_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | `test_constitutional_convergence.py` | COVERED |
| 31 | `00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py` | GATE_ENGINE | no | 0 | **none** | **none** | **UNREACHABLE** |
| 32 | `00-MASTER/UCOS-UTCE-001/utce_engine.py` | GATE_ENGINE | YES | 1 | `Makefile` | `test_constitutional_convergence.py` | COVERED |
| 33 | `00-MASTER/UEI-000001/uei_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/uei-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 34 | `00-MASTER/UER-000001/uer_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/uer-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 35 | `00-MASTER/UIS-001/uis_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/uec-gate.yml`, `.github/workflows/uis-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 36 | `00-MASTER/UKAP-001/corpus_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/corpus-currency-gate.yml`, `Makefile` | `test_corpus_currency.py` | COVERED |
| 37 | `00-MASTER/UMK-000001/umk_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/umk-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 38 | `00-MASTER/UPF-000001/upf_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/uprf-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 39 | `00-MASTER/URRC-000001/urrc_engine.py` | GATE_ENGINE | YES | 2 | `.github/workflows/urrc-gate.yml`, `Makefile` | **none** | **UNVERIFIED** |
| 40 | `engine/construct/gate.py` | MODULE_GATE | no | 3 | `.github/workflows/ucon-gate.yml`, `Makefile`, `verify.sh` | `test_construct_foundation.py`, `test_enforcement_closure.py` | COVERED |
| 41 | `engine/enforcement_closure/gate.py` | MODULE_GATE | no | 3 | `.github/workflows/uec-gate.yml`, `Makefile`, `verify.sh` | `test_enforcement_closure.py` | COVERED |
| 42 | `engine/execution_environment/gate.py` | MODULE_GATE | no | 1 | `Makefile` | `test_execution_environment.py` | COVERED |
| 43 | `engine/infinite_scope/gate.py` | MODULE_GATE | no | 3 | `.github/workflows/uisd-gate.yml`, `Makefile`, `verify.sh` | `test_infinite_scope.py` | COVERED |
| 44 | `engine/object_birth/gate.py` | MODULE_GATE | no | 2 | `Makefile`, `verify.sh` | `test_identifier_dictionary_persistence.py`, `test_birth_scope.py`, `test_object_birth.py`, `test_verification_purity.py` | COVERED |
| 45 | `engine/recursive_knowledge/gate.py` | MODULE_GATE | no | 3 | `.github/workflows/urke-gate.yml`, `Makefile`, `verify.sh` | `test_enforcement_closure.py`, `test_recursive_knowledge.py` | COVERED |
| 46 | `engine/root_ontology/gate.py` | MODULE_GATE | no | 2 | `Makefile`, `verify.sh` | `test_birth_scope.py`, `test_root_ontology.py` | COVERED |
| 47 | `engine/uaue/gate.py` | MODULE_GATE | YES | 3 | `.github/workflows/uaue-gate.yml`, `Makefile`, `verify.sh` | `test_uaue_controller.py`, `test_uaue_engine_refusals.py`, `test_uaue_evolution_authority.py`, `test_uaue_evolution_engine.py`, `test_uaue_exit_criteria.py`, `test_uaue_register_surface.py`, `test_verification_intelligence.py`, `test_verification_purity.py` | COVERED |
| 48 | `engine/verification_intelligence/gate.py` | MODULE_GATE | no | 2 | `Makefile`, `verify.sh` | `test_verification_intelligence.py`, `test_canonical_validation_evidence.py` | COVERED |

---

## 10 · Reproduction, and the limits of this measurement

```bash
python -m engine.enforcement_closure.gate --json      # 13 laws, ratchet, 172 artifacts
python -m engine.enforcement_closure.gate --inventory  # discovered surface, writes nothing
git rev-parse --short HEAD                            # 446f8a0f
```

Node populations come from `00-MASTER/UEC-000001/uec-declaration.json`,
`00-MASTER/UAKOS-CLOSURE-009/requirements.json`, `00-MASTER/UCCEP-000000/uccep.json`,
`00-BOOK/DATA/artifacts.json`, `00-BOOK/DATA/certification.json` and the four discovery globs.

**Limits, recorded rather than papered over:**

1. **The tree was DIRTY (91 entries) when measurement began, 95 when it ended.** This graph
   describes the working tree, not commit `446f8a0f`. Of the 4 new untracked files, 2 are this
   document and its companion; `ENFORCEMENT-CLOSURE-MATRIX.md` and `ENFORCEMENT-CLOSURE-GAPS.md`
   appeared during the session and were **not written by this mission**. Several dirty entries are
   register files under `00-MASTER/UAIE-000001/`, `00-MASTER/UCOS-UGA-001/` and `00-BOOK/DATA/` —
   i.e. artifacts that prior gate runs mutated, which is the `GATE-PURITY` D-3.1 finding,
   reproduced.
2. **A concurrent mutation campaign ran during the measurement window** (§3). It restored
   `contract.py` with digest verification, and every figure in this document was re-executed on the
   restored tree and is byte-identical. The ratcheted helpers used here are distinct from the law
   functions the campaign neutered.
3. **"Self-certifies own home" is a structural test, not a semantic one.** It measures that the
   engine writes into the directory whose artifacts it judges. It does not prove any specific
   verdict was satisfied by that write.
4. **`proves-can-refuse` is a name-binding test.** It measures that a test file names the engine,
   which is what `UEC-L-05` measures. Mutation-kill evidence exists for exactly one programme:
   `UEC-000001`, 13 of 13 law mutants killed. For every other certifier, "a test names it" is
   weaker than "a test can make it fail," and §3 records the direct observation that running a
   gate over a neutered detector returns OPEN.
5. **The `REQ-nn` layer was read from prose.** Its internal counts are inconsistent — the
   traceability matrix declares 37 requirements and tallies 40 — and the master index supersedes
   it. Both are reported; neither is machine-readable.
6. **`gap_classes[*].members` in `requirements.json` is capped at 400 entries.** Counts are
   authoritative; member lists are truncated for `RG-B01` (406), `RG-E01` (549), `RG-E02` (471)
   and `RG-E03` (416).
7. **This document is itself outside the closure it measures.** It is a root-level `.md`, which
   falls inside the `REG-AUTO-001` registration boundary and is not registered. It therefore
   adds 2 (with its companion) to the unregistered-eligible population that `REQ-28` tracks.
   Registering it would be a mutation of Repository Truth, which this mission does not authorize.

### Independent corroboration

`ENFORCEMENT-CLOSURE-MATRIX.md`, an artifact present in the working tree measuring the same
enforcement planes at the same HEAD by the same in-process import method, agrees on every
overlapping figure: 172 governed artifacts, 6,751 tracked paths, declaration digest
`cffb41b32c9eba5b`, verdict OPEN, all five ratchet classes at ceiling, 39 gate engines of which 33
are reachable and 24 executed by a workflow, 9 module gates, 54 Make gate targets, 18 verify
stages, 32 workflows, 549 requirements with 0 executed and 241 certified, 49 `REQ-nn` with 0
declared.

That artifact also reports "a live mutant that disables UEC-L-08 is present in the working tree,
and it survives," attributing it to `UEC-L-08` and stating it is "absent from HEAD" and "not
introduced by this measurement." Both that reading and this measurement's first reading of the same
observation were **transient states of the concurrent mutation campaign described in §3**. The
campaign's own completed output is `total killed 13  SURVIVED 0 · contract restored: True`. No
persistent mutant exists in `contract.py`; `UEC-L-08`'s detector body is intact and measures 0
against a ceiling of 0. Recorded here because two independent measurements reached the same wrong
conclusion from the same transient artefact, which is itself a fact about measuring a live tree.

*END — SELF-COVERAGE-GRAPH · AUTHORITY = NONE (DERIVED TRUTH) · MEASUREMENT ONLY · REPAIRS NOTHING.*
