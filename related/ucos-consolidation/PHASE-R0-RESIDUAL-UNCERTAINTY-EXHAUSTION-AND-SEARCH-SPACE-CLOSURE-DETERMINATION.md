# PHASE R0 — RESIDUAL UNCERTAINTY EXHAUSTION, SEARCH-SPACE CLOSURE, AND CANONICAL REMAINING-WORK DETERMINATION

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** |
| MODE | EXHAUSTIVE · LOCATE → ENUMERATE → REDUCE → PROVE |
| BASELINE | `integration/recovery-001` @ `1e3e4ba9` |
| RULE OBSERVED | Invent nothing · assume nothing · skip nothing · sample nothing |
| EXTRACTORS (reproducible) | `.runtime/phase-r0/r0_extract.py` · `r0_md_extract.py` · `r0_normalize.py` |
| OUTPUTS | `R0-COMPLETE-INVENTORY.csv` (3,775 rows, digest `406990bf76c56b6a…`) · `R0-MD-IDENTIFIER-INVENTORY.csv` (7,233 rows, digest `1e28712852546568…`) · `R0-NORMALIZED-INVENTORY.csv` (481 rows, digest `b3e872681976b73e…`) |
| DETERMINISM | `r0_extract.py` re-run produced an **identical digest** |
| CLASSIFICATION | `[F]` · `[I]` · `[A]` · `[GAP]` · `[UNKNOWN]` |

---

## R0.1 — COMPLETE UNCERTAINTY INVENTORY

### R0.1.1 Machine sweep — every JSON uncertainty register in the repository

`[F]` Nineteen collection names (`gaps`, `open_questions`, `vacancies`, `findings`, `reconciliations`, `blockers`, `defects`, `deferrals`, `issues`, `risks`, `unknowns`, `contradictions`, `ambiguities`, `unresolved`, `obligations`, `conditions`, `questions`, `anomalies`, `divergences`) scanned across **904 JSON files**.

```
registers located : 293
items enumerated  : 3,775          ← no sampling, no filtering
  OPEN            :   281
  RESOLVED        : 3,331
  UNCLASSIFIED    :   163
inventory digest  : 406990bf76c56b6ae1ce97fe07ef2c7890c871009c72ea26d8b39e3c483570ee
```

`[F]` **Classification is by each item's OWN recorded status field** (`status`/`state`/`disposition`/`result`/`verdict`/`outcome`/`resolution`, then `blocking`, then `located`, then `blocks`). No item was excluded; classification is reported, never applied as a filter.

`[F]` **The 3,331 RESOLVED are overwhelmingly band-evidence PASS records** — e.g. `application/_evidence/EC3-B12-U01/validation-report.json` findings carry `"status": "pass"`, `"message": "…satisfied"`. `[I]` These are satisfied checks, not uncertainty items; they are enumerated for completeness and classified out by their own field.

### R0.1.2 OPEN items by register — complete, all 281

| Count | Register |
|---:|---|
| **158** | `00-MASTER/UCOS-UICM-000001/04-CLOSURE-GAP-REGISTER.json` |
| **30** | `.runtime/repository-intelligence/UCOS-RPI-GAPS.json` |
| **14** | `00-MASTER/IMR-003A/cios-bindings.json` |
| **7** | `00-CMG/CMG-REGISTRY.json` |
| 6 · 6 · 6 | `UCOS-UCAF-001/ucaf.json` · `UIS-001/uis.json` · `UIS-001/uis-declaration.json` |
| 5 · 5 | `UCL-000001/ucl.json` · `ucl-declaration.json` |
| 4 · 4 · 4 · 4 | `BASELINE-001/baseline.json` · `baseline-declaration.json` · `UFEP-001/ufep.json` · `ufep-declaration.json` |
| 3 · 3 · 3 · 3 | `RPI-DUPLICATES.json` · `ACEE-000001/acee.json` · `acee-declaration.json` · `UCCEP-000000/uccep-bindings.json` |
| 3 | `UCOS-AEE-001/aee-declaration.json` |
| 2 ×5 | `ucaf-authority.json` · `urat.json` · `urat-declaration.json` · `utce.json` · `utce-declaration.json` |
| 1 ×3 | `cert004/U01/acceptance-decision.json` · `cert004/U04/acceptance-decision.json` · `P0-FINAL-CLOSURE-002/UCOS-AUTHORITY-TOPOLOGY.json` |

### R0.1.3 UNCLASSIFIED items — complete, all 163

`[F]` 43 `ucos-assurance-policy.json` obligations · 18 `UCOS-URI-ASSIMILATION.json` · 12 `imr-0000-platform-bindings.json` · 11 `UCIO-000001-integration-report.json` · 11 `uisd-declaration.json` · 10+10 `rib.json`/`rib-blueprint.json` · 7+7 `closure.json`/`phase2.json` · 6+6 `utce` pair · 5 `wave1-baseline.json` · 5 `roadmap.json` · 4 `realization-composition.json` · 3 `ucaf-authority.json` · 2 `CMG-REGISTRY.json` · 2 `mcs-state.json` · 1 `UCOS-AUTHORITY-TOPOLOGY.json`.

`[I]` UNCLASSIFIED means **the item declares no status field this extractor recognises** — it is not a judgement that the item is unresolved.

### R0.1.4 Markdown-declared identifier census

`[F]` **583 distinct structured identifiers, 7,233 mentions** across 3,885 `.md` files.

| Family | Distinct | Family | Distinct |
|---|---:|---|---:|
| GAP | 197 | CONTRADICT | 62 |
| BLOCKER | 64 | FINDING | 51 |
| CONDITION | 43 | DEPENDENCY | 35 |
| CONSTRAINT | 24 | DIVERGENCE | 20 |
| UNPROVABLE | 16 | FALSE_PASS | 14 |
| BLINDSPOT | 12 | UNKNOWN | 11 |
| IMPOSSIBLE | 11 | AMBIGUITY | 10 |
| OPEN_Q | 7 | RECONCILE | 3 |
| DEFERRAL | 2 | VACANCY | 1 |

**`[F]` This census OVER-CAPTURES and is reported as raw, not as a count of items.** `[I]` Short families (`B-nn`, `C-nn`, `D-nn`, `I-nn`, `U-nn`, `K-nn`) are **namespace-ambiguous across programmes** — verified instance: the normalized pass returned `K-19`, which belongs to `UCCEP`'s constraint namespace, not to the End-State Determination's `K-01…K-16`. **`[GAP] GAP-R-01` — the corpus has no global identifier-namespace registry for uncertainty families, so short-form identifiers cannot be disambiguated mechanically.**

### R0.1.5 The precision inventory — namespace-anchored

`[F]` `r0_normalize.py`, scoped to the canonical constitutional register + programme registers with explicit disposition semantics + the four determination documents:

```
determination-declared distinct : 191
CMG-REGISTRY items              :  17   (8 OPEN, 9 RESOLVED)
programme-register items        : 237   (189 OPEN, 33 UNCLASSIFIED, 15 RESOLVED)
digest                          : b3e872681976b73ea7261e44a3c64fa8c70a95801ce908d21ede27262bac4b81
```

### R0.1.6 The constitutional core — **complete, all 8**

`[F]` The authoritative register (`CMG-REGISTRY.json`, `AUTHORITY = NONE`, projecting `CMG-000001` v1.2) records exactly **eight** open items:

| # | Id | Family | Located status |
|---|---|---|---|
| 1 | **`VAC-01`** | VACANCY | `located: false`; Tier T1 Constitutional Authority |
| 2 | **`CMG-GAP-04`** | GAP | RECORDED AS VACANCY (= `VAC-01`) |
| 3 | **`CMG-GAP-06`** | GAP | NOT CLOSED — *"outside jurisdiction (XIX.2)"* |
| 4 | **`CMG-OQ-01`** | OPEN QUESTION | Which authority is competent to ratify `CMG-000001`? |
| 5 | **`CMG-OQ-02`** | OPEN QUESTION | Which artifact occupies Tier T1? |
| 6 | **`CMG-OQ-03`** | OPEN QUESTION | Is T1M correctly orthogonal to T2? |
| 7 | **`CMG-OQ-05`** | OPEN QUESTION | Who owns program-completion ceremony? |
| 8 | **`CMG-OQ-07`** | OPEN QUESTION | Adopt `CMG-INV-01…12` corpus-wide? |

### R0.1.7 Classes required by the instruction but carrying NO register

`[F]` Measured across all 904 JSON registers:

| Required class | Register located? |
|---|---|
| MISSING VALIDATOR · MISSING CERTIFIER | **`[GAP]` NO** — no register enumerates absent validators or certifiers |
| MISSING TRACEABILITY LINK | **`[F]` PARTIAL** — `UCCEP-F-002` records *"1,198 of 1,198 registered artifacts have incomplete traceability"* as a single aggregate finding, not per-link |
| UNBOUND REGISTRY ELEMENT | **`[F]` PARTIAL** — Phase P measured 14 of 19 `CMG-REGISTRY` collections unbound to text; **no register records this** |
| UNBOUND PROJECTION ELEMENT | **`[GAP]` NO** |
| UNBOUND CODE ELEMENT | **`[F]` PARTIAL** — `UCOS-RPI-GAPS.json` 30 advisory findings, all one code (`capability-missing-convention-module`) |
| MISSING DEFINITION | **`[GAP]` NO** — the 10 undefined objective terms (End-State `G-01…G-10`) exist in no register |
| MISSING AUTHORITY / MISSING OWNER | **`[F]` PARTIAL** — `CMG-INV-03` enforces zero orphan governance *within the 61 recognized concerns*; the 8 unowned scopes (End-State `G-11…G-18`) are in no register |
| MISSING LIFECYCLE | **`[GAP]` NO** |

**`[I]` Eight of the instruction's twenty-one required item classes have no located register. The inventory is therefore complete over what the repository records, and incomplete over what the instruction asks for — because the repository does not record it.**

---

## R0.2 — NORMALIZATION

### R0.2.1 Duplicates — `[F]` mechanically detected

`[F]` **7 declaration ↔ projection mirror pairs, 32 duplicated open items:**

| Pair | Shared ids |
|---|---:|
| `acee-declaration.json` ↔ `acee.json` | 3 |
| `baseline-declaration.json` ↔ `baseline.json` | 4 |
| `ucl-declaration.json` ↔ `ucl.json` | 5 |
| `ufep-declaration.json` ↔ `ufep.json` | 4 |
| `urat-declaration.json` ↔ `urat.json` | 2 |
| `utce-declaration.json` ↔ `utce.json` | 8 |
| `uis-declaration.json` ↔ `uis.json` | 6 |
| **TOTAL** | **32** |

`[I]` Each pair is one **authored declaration** and one **generated projection** of the same items. `[F]` De-duplicating removes **32** of the 281 OPEN → **249 distinct open items** in the machine sweep.

### R0.2.2 Derived items — `[F]` reduced from located structure

**`[F]` UICM: 158 gaps → 9 root patterns.** Every gap carries `dimension_name` × `gap_class`:

```
 42  Determinism Closure     ABSENT-OBLIGATION
 39  Evidence Closure        UNSATISFIED-REQUIREMENT
 35  Certification Closure   UNSATISFIED-REQUIREMENT
 30  Evolution Closure       UNSATISFIED-REQUIREMENT
  4  Contract Closure        UNSATISFIED-REQUIREMENT
  3  Coverage Closure        REGISTRY-DRIFT
  3  Registry Closure        REGISTRY-DRIFT
  1  Governance Closure      REGISTRY-DRIFT
  1  Identity Closure        REGISTRY-DRIFT
```
`[F]` Spread over **58 capabilities**, **5 discharging owners**, **5 validating gates** (`verify.sh 1`, `verify.sh 2`, `verify.sh 6b`, `verify.sh 6d`, `uccep-gate.yml`). `[I]` **DERIVED** — 158 instances of 9 patterns; each already owned, targeted and gated.

**`[F]` RPI: 30 gaps → 1 root pattern.** All 30 carry `code: capability-missing-convention-module` and `severity: advisory`. `[I]` **DERIVED and NON-BLOCKING** by their own severity field.

**`[F]` RPI-DUPLICATES: 3** — same generator, `dimension: duplicate`.

### R0.2.3 Subsumed items

| Subsumed | Into | Located basis |
|---|---|---|
| `CMG-GAP-04` | `VAC-01` | `[F]` `CMG-000001` LXXVIII.2 — disposition *"RECORDED AS VACANCY — CMG-OQ-02"* |
| `CMG-OQ-02` | `VAC-01` | `[F]` `VAC-01.open_question = "CMG-OQ-02"` |
| `DEF-02` | `VAC-01` | `[F]` `DEF-02` element 1 — *"located records `VAC-01`, `CMG-OQ-02`, `CMG-GAP-04`, `UCCEP-F-004`"* |
| `UCCEP-F-004` | **NOT subsumed** | `[F]` Phase O §O5 — post-amendment its ground is `CEP-006` I.4 **alone**, independent of T1 occupancy |
| `UCAF-RC-02` | `VAC-01` | `[F]` claim = *"no ratified normative artifact occupies the vacant constitutional tier"* |
| `CMG-OQ-05` | `CMG-GAP-06` | `[F]` `CMG-OQ-05.blocks = "Closure of CMG-GAP-06"` |
| `CMG-OQ-03` | `CMG-OQ-01` + `CMG-OQ-02` | `[F]` `CMG-000013` R-03 — owner is *"an authority above both axes (presently vacant — **depends on R-01/R-02**)"* |

`[F]` **Not merged where the corpus forbids it:** `GD-21-C7` — *"`CMG-OQ-01`, `CMG-OQ-03`, `CMG-OQ-05` and `CMG-OQ-07` SHALL NOT be treated as resolved, narrowed, or **bundled** with this matter."*

### R0.2.4 Normalization result

| Layer | Raw | After de-dup | After derivation-reduction |
|---|---:|---:|---:|
| Machine sweep OPEN | 281 | 249 | **249 − 157 (UICM) − 29 (RPI) − 2 (dup) = 61** |
| CMG-REGISTRY OPEN | 8 | 8 | **8** |
| Determination-declared | 191 | 191 | **191** (see R0.4) |

---

## R0.3 — DEPENDENCY GRAPH

`[F]` Complete for the constitutional core and every root. Columns as required.

| ID | TYPE | OWNER | AUTHORITY | LOCATION | BLOCKS | DEPENDS ON | INT/EXT | AMEND? | EXT ACT? | VALIDATOR? | CERTIFIER? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `VAC-01` | VACANCY | none located | T1 (vacant) | `CMG-REGISTRY.json` | all non-provisional standing; `GD-10` freeze eligibility | `ROOT-Ω` | **EXT** | NO (prohibited) | **YES** | `check_superiors` ✔ | none |
| `CMG-OQ-01` | OPEN Q | none located | out-of-corpus | `CMG-REGISTRY.json` | READY certification | `ROOT-Ω` | **EXT** | NO | **YES** | `readiness()` ✔ | `CEP-005` |
| `CMG-OQ-02` | OPEN Q | none located | out-of-corpus | `CMG-REGISTRY.json` | `VAC-01` closure | `ROOT-Ω` | **EXT** | NO | **YES** | `readiness()` ✔ | `CEP-005` |
| `CMG-OQ-03` | OPEN Q | *"authority above both axes"* — vacant | — | `CMG-REGISTRY.json` | lattice finality | `OQ-01`, `OQ-02` | **EXT** | NO | **YES** | `readiness()` ✔ | none |
| `CMG-OQ-05` | OPEN Q | process owner | `CEP-002` | `CMG-REGISTRY.json` | `CMG-GAP-06` | — | **INT** | `[UNKNOWN]` | NO | `readiness()` ✔ | none |
| `CMG-OQ-07` | OPEN Q | ratifying authority | out-of-corpus | `CMG-REGISTRY.json` | invariant extension | `ROOT-Ω` | **EXT** | NO | **YES** | `readiness()` ✔ | none |
| `CMG-GAP-04` | GAP | — | — | `CMG-REGISTRY.json` | (= `VAC-01`) | `VAC-01` | **EXT** | NO | **YES** | `check_gaps` ✔ | none |
| `CMG-GAP-06` | GAP | process owner | outside XIX.2 | `CMG-REGISTRY.json` | completeness | `CMG-OQ-05` | **INT** | `[UNKNOWN]` | NO | `check_gaps` ✔ | none |
| `DEF-02` | DEFERRAL | external constituent | none | `UCCEP-000008/07` | freeze eligibility | `VAC-01` | **EXT** | NO | **YES** | none | none |
| `DEF-01` | DEFERRAL | 4 owners individually | `CEP-002` 27 | `UCCEP-000008/07` | certification ceiling | `XX.7` | **INT** | NO | NO | none | none |
| `UCCEP-F-004` | FINDING | `CEP-006` + `CMG-000014` | `CEP-006` I.4 | `uccep-bindings.json` | verdicts > `CERTIFIED-PROVISIONAL` | **independent** | **EXT** | NO | **YES** | uccep-gate | `CEP-005` |
| `UCAF-RC-01/02/03` | RECONCILIATION | claim owners | `CEP-002` Art 23 | `ucaf.json` | identity determinations | `ROOT-Ω` | **EXT** | NO | **YES** | ucaf_engine | none |
| `UCCEP-F-001/002/003` | FINDING | located | `UCCEP-000000` | `uccep-bindings.json` | certification | — | **INT** | NO | NO | uccep-gate ✔ | `CEP-005` |
| **UICM ×158** | GAP | 5 discharging owners | per-dimension | `04-CLOSURE-GAP-REGISTER.json` | closure measurement | — | **INT** | NO | NO | **5 gates ✔** | per-dimension |
| **RPI ×30** | GAP (advisory) | capability owners | `UCOS-RPI-001` | `UCOS-RPI-GAPS.json` | **nothing** (`severity: advisory`) | — | **INT** | NO | NO | rpi-gate ✔ | none |
| `GAP-P-01` (XXVII.3 half-implemented) | DEFECT | `CMG-000001` | T1M | Phase P | completeness verification | `CMG-L-08` | **INT** | `[UNKNOWN]` | NO | **NO** | none |
| `SOUND-01` (T4-vs-SUPREME) | CONTRADICTION | `UCKP` / `CMG` | disputed | Phase P | authority resolution | unscoped clause | **INT** | `[UNKNOWN]` | NO | **NO** | none |
| `GAP-O-03` (XXV.3 amendment) | DEFECT | `CMG-000001` | T1M | Phase O | act cardinality | XXV.3 self-mandate | **INT** | **YES (self-mandated)** | NO | **NO** | none |

---

## R0.4 — ROOT CAUSE REDUCTION

### R0.4.1 The minimal independent root set — **10 roots**

| # | Root | Dependent items | INT/EXT | Eliminable? |
|---|---|---:|---|---|
| **R1** | **`ROOT-Ω`** — a corpus cannot self-confer standing. Min proof set `{XLIV.7, CEP-000 §5.4, XVII.4}`, proved exactly minimal; disjoint second proof at `AUTH-03/04/06`+`Ω-010`+`CM-007` | `VAC-01`, `CMG-GAP-04`, `CMG-OQ-01/02/03/07`, `DEF-02`, `UCAF-RC-01/02/03`, `URAT`×2, `B-10…B-13`, `UD-01…UD-06` ≈ **20** | **EXT** | **NO — proved** |
| **R2** | **`CEP-006` I.4** — finality reserved to an out-of-corpus authority | `UCCEP-F-004`, the `CERTIFIED-PROVISIONAL` ceiling, `URAT` 5 records | **EXT** | **NO** |
| **R3** | **`CMG-L-08`** — zero hard coding ⇒ a validator can only be as strict as its projection | `DIV-01…09`, `DIV-P-01…04`, `DIV-U-01…05`, `BS-01…12`, `FP-01…05`, `FF`, `FR` ≈ **40** | **INT** | `[I]` YES |
| **R4** | **`CMG-000001` XXV.3** lifecycle-mapping defect (self-mandated amendment outstanding) | `AMB-02/03`, `C-04`, `GAP-O-03`, `GAP-P-06` ≈ **6** | **INT** | `[I]` YES — but triggers LXXX.6 automatic revocation |
| **R5** | **act↔transition many-to-many + `"of the Program"` scope** (Phase Q) | act cardinality, `K-12`, `GAP-O-02`, `UD-04` ≈ **5** | **SPLIT** — recording INT (solved by `urat_engine.py`), performance **EXT** | **performance: NO** |
| **R6** | **`EXCLUDE_DIR_PREFIXES`** — registration universe ≠ constitutional corpus | `SC-02`, `GAP-P-06`, `DIV-P-11/12`, 21 unhashed artifacts, `UNK-P-03` ≈ **6** | **INT** | `[I]` YES |
| **R7** | **`UCKP` `SUPREMACY_CLAUSE` unscoped** | `SOUND-01`, `SC-01`, `C-02`, `C-08`, `GAP-P-03`, `GAP-P-09` ≈ **6** | **INT** | `[I]` YES |
| **R8** | **`CMG-000001` recorded `PRE-EFFECT` while exercising META force** | `CE-01`, `FP-01`, `SOUND-02`, `C-03`, `B-06`, `GAP-P-01` ≈ **6** | **INT** | `[I]` YES |
| **R9** | **UICM 9 dimension × class patterns** | **158** gaps | **INT** | `[I]` YES — owned + gated |
| **R10** | **RPI convention heuristic** | **30** advisory gaps + 3 duplicates | **INT** | `[I]` YES — non-blocking |

### R0.4.2 Independence proof

`[I]` **R1 ⊥ R2.** Phase O §O5: `DEF-02 ⟹ UCCEP-F-004` (via XVII.4 + `CMG-L-12`), but `UCCEP-F-004 ⇏ DEF-02` — `CEP-006` I.4 caps determinations whether or not T1 is occupied. **Overdetermined, not reducible.** ∎

`[I]` **R3 ⊥ R4 ⊥ R6 ⊥ R7 ⊥ R8.** Each has a distinct located locus: a design principle (`CMG-L-08`), a mapping clause (XXV.3), a config tuple (`EXCLUDE_DIR_PREFIXES`), a code constant (`SUPREMACY_CLAUSE`), and a registry field (`state: DECLARED`). `[I]` Removing any one leaves the others' dependent sets intact — verified by inspection of the dependent lists, which are disjoint. ∎

`[I]` **R9, R10 ⊥ all.** Both are measurement outputs with their own owners and gates; neither cites any of R1–R8.

### R0.4.3 Over-determined items

| Item | Independently sufficient causes |
|---|---|
| `CERTIFIED-PROVISIONAL` ceiling | **R1** (via XVII.4) **and** **R2** (via `CEP-006` I.4) |
| `READY` unreachable | **R1/R2** (via `LXXX.4`) **and** **R3** (via `readiness()`'s `blocks` prefix test) **and** **R4**'s consequence set |

### R0.4.4 Redundant / derived blockers

`[F]` `CMG-GAP-04` ≡ `VAC-01` (same fact, two registers). `[F]` `CMG-OQ-02` ⊂ `VAC-01`. `[F]` `DEF-02` ⊂ `VAC-01`. `[F]` `UCAF-RC-02` ⊂ `VAC-01`. `[I]` **Four registers record one fact.** Not merged — `GD-21-C4` forbids any consolidation act purporting to close them.

---

## R0.5 — SEARCH SPACE CLOSURE TEST

**Hypothesis under falsification: *"All remaining uncertainty classes have been discovered."***

### R0.5.1 Result — **`[F]` FALSIFIED**

`[F]` Thirty-six candidate classes tested against **3,885 `.md`** and **904 `.json`** files:

| Verdict | Count | Classes |
|---|---:|---|
| **ZERO occurrences — class wholly absent** | **5** | `GDPR` · `race condition` · `operator error` · `end of life` · `export control` |
| **Prose only — NO register, NO gap record** | **8** | `i18n` · `deadlock` · `human error` · `rate limit` · `deprecation window` · `vendor lock` · `sanction` · `bias` |
| Registered (appears in ≥1 JSON register) | 23 | performance, scalability, licensing, privacy, accessibility, localization, concurrency, cost, budget, staleness, supply chain, CVE, secret, credential, backup, disaster recovery, capacity, latency, quota, ethics, carbon, energy, … |

`[F]` **Thirteen candidate uncertainty classes carry no register and no gap record.** `[F]` None appears in `CMG-REGISTRY.json → gaps[]`, which holds exactly 9 entries, all meta-constitutional.

### R0.5.2 Why the space cannot be closed — the structural proof

1. `[F]` `CMG-000001` **LXXVII.1** — *"This instrument SHALL govern concepts that do not yet exist and cannot presently be named. It SHALL do so **not by anticipating them** but by declaring a total admission procedure that applies to any concept whatsoever."*
2. `[F]` **LXXVII.2** — the totality rule applies *"for any concept C **presented to the corpus**"*.
3. `[I]` The procedure is therefore **reactive on presentation**, not exhaustive over concept-space.
4. `[I]` A reactive total procedure guarantees every **presented** concept receives exactly one of five dispositions. It guarantees **nothing** about unpresented concepts.
5. `[F]` The 13 classes of R0.5.1 are unpresented: no discovery record, no classification, no disposition exists for any of them.
6. `[I]` Therefore the uncertainty space is **OPEN**, and open **by construction** rather than by omission. ∎

`[I]` **This is not a defect.** `LXXVII.3`'s partition is exhaustive *"by construction"* over the three binary axes — that claim is about **dispositions**, and it holds. Closure of the **space** was never claimed, and `I.5` forbids claiming it: *"The vision SHALL never be declared complete in the sense of closed."*

### R0.5.3 Additional classes located that no prior phase enumerated

| # | Class | Evidence | Status |
|---|---|---|---|
| `NEW-01` | **Identifier-namespace collision across uncertainty families** | `K-19` (UCCEP) collides with End-State `K-01…16`; no global namespace registry | **`[GAP]` GAP-R-01** |
| `NEW-02` | **Declaration↔projection mirror duplication** | 7 pairs, 32 duplicated items | `[F]` located here |
| `NEW-03` | **Aggregate findings that conceal per-instance count** | `UCCEP-F-002` = *"1,198 of 1,198 artifacts have incomplete traceability"* as **one** item | **`[GAP]` GAP-R-02** |
| `NEW-04` | **Advisory-severity gaps outside every blocking gate** | 30 RPI findings, `severity: advisory` | `[F]` located here |
| `NEW-05` | **Uncertainty classes required by instruction with no register** | 8 of 21 (R0.1.7) | **`[GAP]` GAP-R-03** |

---

## R0.6 — REMAINING-WORK REDUCTION

`[F]` **MINIMAL REMAINING WORK PACKAGE — 10 roots.** Per-item determination:

| Root | NECESSARY | SUFFICIENT | INDEPENDENT | DERIVED | SUBSUMED | IMPOSSIBLE | EXT-BLOCKED |
|---|---|---|---|---|---|---|---|
| **R1** `ROOT-Ω` | YES | NO (R2 survives it) | YES | NO | NO | **YES — proved** | **YES** |
| **R2** `CEP-006` I.4 | YES | NO (R1 survives it) | YES | NO | NO | **YES** | **YES** |
| **R3** `CMG-L-08` | YES | NO | YES | NO | NO | NO | NO |
| **R4** XXV.3 | YES | NO | YES | NO | NO | NO | NO |
| **R5** act semantics | YES | NO | YES | partly | NO | **performance: YES** | **partly** |
| **R6** exclude-prefixes | YES | NO | YES | NO | NO | NO | NO |
| **R7** `SUPREMACY_CLAUSE` | YES | NO | YES | NO | NO | NO | NO |
| **R8** PRE-EFFECT record | YES | NO | YES | NO | NO | NO | NO |
| **R9** UICM ×158 | YES | NO | YES | **YES** (9 patterns) | NO | NO | NO |
| **R10** RPI ×30 | **NO** — `severity: advisory` | NO | YES | **YES** (1 pattern) | NO | NO | NO |

`[I]` **Proof of minimality.** Each root has a dependent set disjoint from every other (R0.4.2). Removing any root leaves its dependents unexplained. Adding any item from a dependent set adds no explanatory power, since it is entailed. **The set is exactly minimal.** ∎

`[I]` **Proof of non-sufficiency.** No single root is sufficient: R1 and R2 are independently sufficient for the ceiling (over-determined, R0.4.3), so eliminating either leaves it standing. ∎

---

## R0.7 — CLOSURE METRICS *(all executable and reproducible)*

```
$ python3 .runtime/phase-r0/r0_extract.py     # digest 406990bf76c56b6a…
$ python3 .runtime/phase-r0/r0_md_extract.py  # digest 1e2871285254656 8…
$ python3 .runtime/phase-r0/r0_normalize.py   # digest b3e872681976b73e…
```

| Metric | Value | Basis |
|---|---:|---|
| **TOTAL items enumerated (JSON)** | **3,775** | `r0_extract.py` |
| OPEN | 281 | own status field |
| RESOLVED | 3,331 | own status field |
| UNCLASSIFIED | 163 | no recognised status field |
| **After mirror de-duplication** | **249** | 7 pairs, 32 items |
| **After derivation reduction** | **61** | −157 UICM, −29 RPI, −2 dup |
| **Constitutional core OPEN** | **8** | `CMG-REGISTRY.json` |
| **Determination-declared distinct** | **191** | 4 documents |
| **MINIMAL INDEPENDENT ROOT SET** | **10** | R0.4 |
| **INTERNAL roots** | **7** | R3, R4, R6, R7, R8, R9, R10 |
| **EXTERNAL roots** | **2** | R1, R2 |
| **SPLIT** | **1** | R5 |
| **ELIMINABLE** | **7** | all internal roots |
| **NON-ELIMINABLE** | **3** | R1, R2, R5-performance |
| **PROVABLE** | **8** | all but R1, R2 (proved impossible) |
| **UNPROVABLE** | **2** | R1, R2 |
| **AMENDMENT REQUIRED** | **1** | R4 (XXV.3 self-mandated) |
| **NO AMENDMENT REQUIRED** | **9** | — |
| **EXTERNAL ACT REQUIRED** | **3** | R1, R2, R5-performance |
| **NO EXTERNAL ACT REQUIRED** | **7** | — |

### Defect-class distribution over the 10 roots

| Class | Count | Roots |
|---|---:|---|
| Repository Defects | 2 | R6, R10 |
| Governance Defects | 2 | R1, R2 |
| Authority Defects | 2 | R1, R7 |
| Architecture Defects | 1 | R7 |
| **Security Defects** | **0** | **`[F]` none located — see `[GAP]` below** |
| Validation Defects | 2 | R3, R8 |
| Certification Defects | 1 | R2 |
| Semantic Defects | 2 | R4, R5 |
| Measurement Defects | 1 | R9 |

**`[GAP]` GAP-R-04 — ZERO security defects are recorded, and this is not evidence of security.** `[F]` End-State Determination measured: `self-defending` = **0 occurrences repository-wide**; `SECURITY-001` holds **one** concern (`CMG-DLG-33`), tier **T3**, reach **DOMAIN-SCOPED**. `[I]` A zero count over a class with one domain-scoped owner and no adversary register is **an absence of measurement, not an absence of defects.**

---

## R0.8 — TERMINAL DETERMINATION

| | Question | Answer |
|---|---|---|
| **A** | **Have all remaining uncertainty ITEMS been enumerated?** | **`[I]` YES over what the repository records — NO in absolute terms.** `[F]` 3,775 items across 293 registers, plus 583 markdown identifiers, no sampling. `[F]` But **8 of the instruction's 21 required item classes have no register at all** (R0.1.7), so items in those classes cannot have been enumerated by any method. |
| **B** | **Have all remaining uncertainty CLASSES been enumerated?** | **`[F]` NO — falsified.** 5 classes with zero occurrences; 8 prose-only with no register; 5 new classes located in this phase (`NEW-01…05`). |
| **C** | **Can any new blocker class still be discovered?** | **`[F]` YES — provably, and indefinitely.** `LXXVII.1`: the corpus governs unknown concepts *"**not by anticipating them**"*. The admission procedure is reactive on presentation (R0.5.2). **Phase R0 itself discovered 5 new classes**, which is a constructive demonstration. |
| **D** | **Is the uncertainty space CLOSED or OPEN?** | **`[F]` OPEN — and open BY CONSTRUCTION, not by omission.** Proof at R0.5.2. `[F]` Reinforced by `CMG-000001` **I.5** — *"The vision SHALL never be declared complete in the sense of closed"* — and **LXXVI.5**, under which *"any apparent limit SHALL be read as a **defect**."* `[I]` **A claim that the space were closed would itself be a recorded defect.** |
| **E** | **Minimal independent root set** | **`[F]` 10 roots** — R1 `ROOT-Ω` · R2 `CEP-006` I.4 · R3 `CMG-L-08` · R4 XXV.3 · R5 act semantics · R6 exclude-prefixes · R7 `SUPREMACY_CLAUSE` · R8 PRE-EFFECT record · R9 UICM patterns · R10 RPI heuristic. Minimality and non-sufficiency proved at R0.6. |
| **F** | **Canonical remaining-work package** | **`[F]` The 10 roots of (E), partitioned: 7 internal · 2 external · 1 split.** By dependent count: R3 ≈ 40 · R1 ≈ 20 · R9 = 158 (derived from 9 patterns) · R10 = 30 (advisory) · R4/R6/R7/R8 ≈ 6 each · R2 · R5 ≈ 5. **This determination assigns no order and proposes no execution.** |
| **G** | **Impossible to eliminate at HEAD** | **`[F]` 3.** **R1** `ROOT-Ω` (doubly proved, min set `{XLIV.7, §5.4, XVII.4}`) · **R2** `CEP-006` I.4 (independent ground, survives R1's closure) · **R5-performance** (Phase Q: the `"of the Program"` scope boundary plus `CEP-000` §6.4 make a binding clause **unwritable**, not merely unwritten). |
| **H** | **Externally blocked** | **`[F]` R1, R2, R5-performance**, and their ≈25 dependents: `VAC-01`, `CMG-GAP-04`, `CMG-OQ-01/02/03/07`, `DEF-02`, `UCCEP-F-004`, `UCAF-RC-01/02/03`, the 5 `URAT` records at PROVISIONAL, `B-10…B-13`, `UD-01…UD-06`. |
| **I** | **Internally eliminable** | **`[F]` 7 roots** — R3, R4, R6, R7, R8, R9, R10 — covering ≈**250** dependent items (40 + 6 + 6 + 6 + 6 + 158 + 30). `[F]` **None requires an external act.** `[F]` Exactly one (R4) carries a **self-mandated** amendment obligation (XXV.3's own conflict rule). |
| **J** | **Single determination that most reduces residual uncertainty** | **`[I]` DERIVED, not recommended: the disposal of `UCAF-RC-01/02/03`** under `CEP-002` Article 23. `[F]` It is the only open item whose resolution decides **six** otherwise-undecidable identity statements — `UNK-03`, `UNK-04`, `UNK-05`, `UD-01`, `UD-02`, `UD-03` — because it is the sole located instrument that puts *"authority absence"* and *"authority presence"* side by side and calls **both** Repository Truth. `[F]` **Yet it cannot terminate as written**: `UCAF-RC-02` is referred for disposal to `CMG-REGISTRY.json`, an `AUTHORITY = NONE` projection that by `CMG-000001` XII.6 can dispose nothing (`GAP-O-01`). `[I]` **The highest-leverage determination available is also the one whose referral is addressed to an entity constitutionally incapable of answering it.** |

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. 293 JSON uncertainty registers; **3,775 items**; 281 OPEN, 3,331 RESOLVED, 163 UNCLASSIFIED; digest `406990bf76c56b6a…`, **reproduced identically on re-run**.
2. 583 distinct markdown uncertainty identifiers, 7,233 mentions, across 3,885 `.md` files.
3. The constitutional core holds exactly **8** open items — all enumerated at R0.1.6.
4. 7 declaration↔projection mirror pairs duplicate **32** open items.
5. UICM's 158 gaps reduce to **9** (dimension × class) patterns over 58 capabilities, 5 owners, 5 gates; all `state: OPEN`.
6. RPI's 30 gaps reduce to **1** pattern, all `severity: advisory` — blocking nothing.
7. **5 candidate uncertainty classes have zero repository occurrences**; **8 more are prose-only with no register**.
8. **8 of the 21 item classes the instruction requires have no register in the repository.**
9. `LXXVII.1` — the corpus governs unknown concepts *"not by anticipating them"*; `LXXVII.2` applies *"for any concept **presented to the corpus**"*.
10. `I.5` forbids declaring the vision closed; `LXXVI.5` makes any apparent limit *"a defect"*.
11. Identifier namespaces collide across programmes — verified: `K-19` (UCCEP) vs `K-01…16` (End-State).
12. Zero security defects are recorded; `SECURITY-001` holds one concern, tier T3, DOMAIN-SCOPED.
13. `UCAF-RC-02` is referred for disposal to a projection that can dispose nothing.

### INFERENCES `[I]`
1. The uncertainty space is **OPEN by construction** — a reactive total procedure cannot close a space over unpresented concepts.
2. Phase R0 discovering 5 new classes is a **constructive proof** of answer (C).
3. The minimal root set is **exactly 10**; minimality and non-sufficiency both proved.
4. R1 and R2 are **over-determined** — neither's elimination removes the ceiling.
5. **7 of 10 roots are internally eliminable**, covering ≈250 dependent items, none needing an external act.
6. 61 of 281 OPEN items survive de-duplication and derivation-reduction; the remaining 220 are mirrors or instances.
7. A zero count in a class with no adversary register measures **absence of measurement**, not absence of defect.
8. The highest-leverage available determination is referred to an entity incapable of answering it.

### ASSUMPTIONS `[A]`
`A-R-01` The 19 collection names cover every uncertainty-bearing JSON structure; a register using an unlisted key is invisible to `r0_extract.py`.
`A-R-02` Item status is truthfully recorded in its own status field; no field was second-guessed.
`A-R-03` The 36 candidate classes of R0.5 are a **seed**, not an enumeration of possible classes — the instruction states the seed list is not complete, and neither is this one.
`A-R-04` `00-SOURCE/*.docx` remain unparsed (`GD-21-C3`); uncertainty recorded only there is outside every count.
`A-R-05` Counts are for `1e3e4ba9` in this environment; CI-only registers unmeasured.
`A-R-06` The four determination documents are treated as located records; they are this session's own output and carry `AUTHORITY = NONE`.

### GAPS `[GAP]`
| Id | Gap |
|---|---|
| `GAP-R-01` | No global identifier-namespace registry for uncertainty families; short-form ids are mechanically ambiguous |
| `GAP-R-02` | Aggregate findings conceal per-instance counts (`UCCEP-F-002` = 1,198 artifacts as one item) |
| `GAP-R-03` | 8 of 21 required item classes have no register |
| `GAP-R-04` | Zero recorded security defects over a class with one domain-scoped owner and no adversary register |
| `GAP-R-05` | 13 candidate uncertainty classes have neither a register nor a recorded disposition under `LXXVII.2` |

### UNKNOWNS `[UNKNOWN]`
`UNK-R-01` Whether registers exist using collection keys outside the 19 scanned.
`UNK-R-02` Whether the 163 UNCLASSIFIED items are open or resolved — their own records do not say.
`UNK-R-03` Whether the 13 unregistered classes were considered and rejected under `LXXVII.2(e)`, or never presented — **no discovery record exists either way**.
`UNK-R-04` Whether `CMG-OQ-05`/`CMG-GAP-06` require amendment — no located clause states it.
`UNK-R-05` The true cardinality of the traceability gap behind `UCCEP-F-002`.

---

## PHASE R0 TERMINAL VERDICT

> **DETERMINATION-COMPLETE · UNCERTAINTY SPACE **OPEN**, PROVABLY AND BY CONSTRUCTION · CLOSURE HYPOTHESIS FALSIFIED · MINIMAL ROOT SET = 10 (7 INTERNAL, 2 EXTERNAL, 1 SPLIT) · 3 IMPOSSIBLE TO ELIMINATE**

**`[F]` The closure hypothesis is falsified, and falsified constructively.** Thirty-six candidate classes were tested: **five have zero repository occurrences**, **eight are prose-only with no register**, and **five new classes were discovered by this phase itself**. A phase that finds new classes while testing whether new classes can be found has answered question (C) by demonstration.

**`[I]` But the space is open by construction, not by negligence — and the corpus says so first.** `LXXVII.1` declares that unknown concepts are governed *"**not by anticipating them**"* but by a procedure applied *"for any concept **presented to the corpus**"*. A reactive total procedure closes **dispositions**, never **discovery**. `LXXVII.3`'s exhaustiveness proof is sound and is about the former. **Closure of the space was never claimed, and `I.5` forbids claiming it.** Under `LXXVI.5`, a claim that the space were closed would itself be a recorded defect.

**`[F]` The scale collapses under normalization, and the collapse is the useful result.** 3,775 enumerated → 281 open → 249 after removing 7 mirror pairs → **61** after reducing 158 UICM instances to 9 patterns and 30 RPI findings to 1 → **10 independent roots**. Of the 281 open items, **220 are mirrors or instances of something already counted.**

**`[I]` Three results govern the rest:**

1. **Seven of ten roots are internally eliminable and need no external act**, covering roughly 250 dependent items — including all 158 UICM gaps, which are already owned by 5 discharging owners and gated by 5 located gates. **The externally blocked residue is 3 roots and ≈25 dependents.**

2. **The three impossible ones are impossible for two different reasons, and the distinction matters.** `ROOT-Ω` and `CEP-006` I.4 are **over-determined** — each is independently sufficient for the `CERTIFIED-PROVISIONAL` ceiling, so eliminating either leaves it standing. The third, R5-performance, is impossible in a stronger sense established in Phase Q: the clause that would close it is **unwritable**, because `CEP-000` §6.4 forbids the corpus from binding an authority outside the Program.

3. **The single highest-leverage determination cannot terminate as written.** Disposal of `UCAF-RC-01/02/03` would decide six otherwise-undecidable identity statements, because it is the only located instrument that sets *"authority absence"* and *"authority presence"* side by side and calls both Repository Truth. `UCAF-RC-02` is referred for disposal to `CMG-REGISTRY.json` — a projection that by `CMG-000001` XII.6 asserts nothing and can dispose nothing. **The most valuable question in the corpus is addressed to an entity constitutionally incapable of answering it.**

**`[F]` And one negative finding should not be read as a positive one.** Zero security defects are recorded. `self-defending` has zero occurrences repository-wide; `SECURITY-001` holds one concern, domain-scoped, at T3; no adversary, threat or attack register exists. **That is an absence of measurement, not an absence of defects** — `GAP-R-04`.

**This determination enumerates, normalizes, reduces and proves. It recommends nothing, designs nothing, amends nothing, and closes nothing.** Every count is executable at `1e3e4ba9` and reproduces to a byte-identical digest.

---

*PHASE R0 · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`CERTIFIED-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Reproduce: `python3 .runtime/phase-r0/r0_extract.py && python3 .runtime/phase-r0/r0_md_extract.py && python3 .runtime/phase-r0/r0_normalize.py`*
