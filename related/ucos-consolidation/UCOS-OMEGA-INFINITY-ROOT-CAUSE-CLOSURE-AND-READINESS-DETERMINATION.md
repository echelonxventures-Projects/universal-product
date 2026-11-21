# UCOS Ω∞ — ROOT CAUSE CLOSURE AND READINESS DETERMINATION

**Ten root causes, collapsed from every registered finding. What closes by engineering, what closes only by authority, and what closes by neither.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-ROOT-CAUSE-CLOSURE-AND-READINESS-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Closes no root cause, discharges no blocker, ratifies no authority, arbitrates no subject, mints no identity, assigns no ownership, and authorizes no act. Every closure action in §5 is a proposal addressed to the authority named beside it. |
| Mode | ANALYSIS ONLY · **NO CODE · NO CONFIGURATION · NO REGISTRY · NO CERTIFICATION · NO IDENTITY · NO OWNERSHIP · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` — *"POST-CERTIFICATION: Code formatting cleanup (Phase 1B and Phase 2)"*, `Sat Aug 22 18:29:57 2026 +0530` |
| Baseline branch | `integration/recovery-001` |
| Baseline working tree | **351** `git status --porcelain` lines — **38** tracked-modified, **313** untracked. Pre-existing; not produced by this determination. |
| Method | No new discovery was performed. Every figure is carried from measurements taken earlier in this session and recorded in `UCOS-OMEGA-INFINITY-IDENTITY-ARBITRATION-PRECONDITION-CLOSURE-EVIDENCE-SNAPSHOT.md` §12, each with the command that produced it. |
| Collapse | **112 registered findings → 10 root causes.** §2 gives the finding → root-cause mapping. |
| Sources collapsed | `BC-1…BC-6` (43 acceptance criteria) · `B-1…B-6` · `RU-01…RU-20` · `UIA-1…UIA-10` · `UIAR-1…UIAR-13` · `URS-2/3/5/6` · `EB-1…EB-14` · `EC-1…EC-9` · `N-1…N-6` · `S-1…S-6` · `D-1`, `D-2` · `CH-4`, `M-C`, `MP2-C-04`, `VAC-01`, `UCCEP-F-004` |
| Root causes | **10** — `RC-1`…`RC-10` |
| Closure actions | **12** — `CA-1`…`CA-12` · 7 engineering-closable · 5 requiring an authority act |
| Authority blockers | **9** — `AG-1`…`AG-9` |
| **Verdict** | **NOT READY. `READY UNCONDITIONAL` is not reachable by repository work, and is not a member of the declared readiness vocabulary. The reachable terminal state is `READY WITH CONDITIONS` where every residual condition is external, enumerated and declared.** |

---

## 1. Executive Determination

### 1.1 The answer, first

Seven of the ten root causes close by engineering work under authority that the repository
records as **available today**. Two close only by an authority act that the repository records as
**not located**. One closes by neither, because the tier that would perform it is **declared
vacant in the repository's own registry**.

That last one is decisive, and it is not a judgement — it is a read of two files:

```
00-CMG/CMG-REGISTRY.json  tiers[]
  {"id":"T1","name":"Constitutional Authority","subordinate_to":["T0"],
   "occupancy":"VACANT","vacancy":"VAC-01"}

00-CMG/CMG-REGISTRY.json  vacancies[]
  VAC-01  located: false
          evidence: "The referent exists in the repository only as frozen non-normative
                     source material under 00-SOURCE/CONSTITUTIONS/ (.docx). No ratified
                     normative artifact occupies the tier."
          provisional_consequence: "Every determination depending on T1 — including the
                     standing of CMG-000001 itself — is PROVISIONAL under CMG-L-12."

00-MASTER/UCCEP-000005/06-EXECUTION-READINESS-ASSESSMENT.md:107
  UCCEP-F-004  "Maximum attainable verdict anywhere in this repository is
                CERTIFIED-PROVISIONAL"
```

A ceiling of `CERTIFIED-PROVISIONAL` and an unconditional readiness claim are incompatible by
construction. Nothing in the ten root causes changes that, and closing all ten would not change
it either.

### 1.2 The second finding, which is more actionable

`READY UNCONDITIONAL` **is not a value in the readiness vocabulary**, and the vocabulary has a
declared owner. `02-MASTER/UCOS-COMP-000000-IMPLEMENTATION-STATE-REGISTRY.md:25` — registry slot
`R-13`, the located owner of the readiness vocabulary — enumerates:

> `Readiness ∈ { READY · CONDITIONALLY READY · NOT READY }`

Three values. `READY UNCONDITIONAL` is not among them, and the same line declares the governing
evidence rule: `TRACK-001 fail-closed: absence of evidence = NOT-DONE`.

So the transition the directive names requires a **vocabulary amendment before it requires any
engineering**, and the amendment is a `T1`-dependent act. This was not previously recorded as a
blocker by any register, and it reframes the target: the reachable question is not *"can we reach
READY UNCONDITIONAL"* but *"can we reach `READY`, and what remains conditional when we do."*

### 1.3 The finding that changes the shape of the work

The 228 uncommitted corpus registrations — the transaction that creates 192 of the 217
dual-identity subjects, consumes 1,014 pages, and advances 88 namespace counters — are **not
pending work awaiting authorization. They are the residue of an act that already happened,
ungoverned, inside a read-only determination.**

The predecessor determination
(`UCOS-OMEGA-INFINITY-READY-UNCONDITIONAL-CLOSURE-DETERMINATION.md` §10.3) discloses the event:
`register.sh --guard`, invoked as a read-only measurement, executed its full registration
transaction — 238 page documents emitted, six ledgers rewritten, ~36 identifiers minted, working
tree 78 → 329 dirty paths, anonymous objects 43 → 7.

Six independent measurements taken this session match that disclosure exactly:

```
00-BOOK/PORTAL/            238 paths dirty   =  228 untracked  +  10 modified
id-ledger.json             +12,290 / −8,058
change-ledger.json         +22,898 / −13,068
relationships.json         +21,366 / −17,670
artifacts.json             +9,368 / −3
generated-artifact-registry.json    clean    (the possible-loss signature §10.3 flags)
anonymous objects                       7    (down from 43, as disclosed)
```

The linkage is therefore established at this baseline, not inferred. Its consequence for closure:
**`CA-3` is not "seal a pending transaction." It is "decide, after the fact, whether an
unauthorized mutation is ratified or reverted."** `ADR-0017` already refused a standing blanket
mint — *"A future anonymous object requires its own decision under this same Article, not a
standing blanket authorization"* — and no Article 28 decision exists for these registrations. That
makes `CA-3` an authority act, not engineering hygiene, and it sits on the critical path.

### 1.4 Answers to the eight closure questions

| # | Question | Answer |
|---|---|---|
| 1 | What blocks `READY UNCONDITIONAL`? | Ten root causes (§2), of which `RC-10` is unreachable by any repository act, and a target value that does not exist in the owning vocabulary (§1.2) |
| 2 | How many root causes actually exist? | **10**, collapsed from 112 registered findings — a 11.2 : 1 duplication ratio |
| 3 | What is the critical path? | `RC-4 → RC-3 → {RC-5, RC-7} → ARBITRABLE → READY` — depth 5, and `RC-3` is an authority act (§4) |
| 4 | What requires authority? | 5 of 12 closure actions: `CA-3`, `CA-4`, `CA-9`, `CA-11`, `CA-12`. Nine authority blockers `AG-1…AG-9` (§6) |
| 5 | What requires implementation? | 7 of 12: `CA-1`, `CA-2`, `CA-5`, `CA-6`, `CA-7`, `CA-8`, `CA-10` (§7) |
| 6 | What cannot currently be closed? | `RC-8` (ownership ratification), `RC-10` (constitutional authority). Both terminate in acts the repository records as unavailable (§8) |
| 7 | What is the minimum closure set? | 12 actions, no duplicates, no umbrella actions (§5) |
| 8 | Is `READY UNCONDITIONAL` achievable? | **No** — not by repository work, and not within the declared vocabulary. `READY WITH CONDITIONS` with all conditions external and enumerated **is** achievable (§9, §10) |

---

## 2. Root Cause Register

### 2.1 Collapse summary

| Root cause | Title | Findings collapsed | n |
|---|---|---|---|
| `RC-1` | Classification outage | `BC-1`, `M-C`, `UIAR-2`, `EB-1`, `EB-2`, `EB-3`, `EC-4`, `F-4`, `G-11`, `A1-1…A1-8` | 17 |
| `RC-2` | No authority-admission map | `UIAR-1`, `UIAR-3`, `UIA-5`, `EB-4`, `AV-7` | 5 |
| `RC-3` | Ungoverned registration transaction standing uncommitted | `RU-01`, `RU-07`, `RU-14`, `UIAR-4`, `UIAR-5`, `EB-5`, `EB-6`, `N-1`, `N-2`, `N-3`, `B-6`, `BC-6`, `A6-1…A6-8`, `G-1…G-11` | 32 |
| `RC-4` | Verification acts mutate — no declared gate mode | `B-2`, `S-1`, `RU-07`, `EB-8`, `H-06`/`CR-09` | 5 |
| `RC-5` | Identity measurement vacuous and stale | `UIA-2`, `UIAR-10`, `UIAR-11`, `EB-10`, `EB-11`, `EB-12`, `EC-2`, `EC-3`, `N-4`, `RU-11` | 10 |
| `RC-6` | Supersession is law with no implementation surface | `UIAR-7`, `EB-9`, `URS-5`, `G-11` (supersession vocabulary unused) | 4 |
| `RC-7` | No rollback boundary | `UIAR-12`, `EB-14`, `N-5`, `EC-6`, `AIF-L17` consequence | 5 |
| `RC-8` | Ownership unsatisfiable by construction | `BC-4`, `B-1`, `RU-06`, `CH-4`, `A4-1…A4-7`, `S-3`, `S-4`, `S-5` | 14 |
| `RC-9` | Certification asserts states its own gates contradict | `BC-3`, `UIA-9`, `UIAR-13`, `URS-3`, `EC-1`, `EC-5`, `EC-7`, `A3-1…A3-7` | 14 |
| `RC-10` | The ratifying authority does not exist | `BC-5`, `RU-19`, `RU-20`, `VAC-01`, `UCCEP-F-004`, `MP2-C-04`, `EB-13`, `EC-8`, `EC-9`, `D-1`, `D-2`, `A5-4` | 12 |
| | | **Total** | **112** |

**112 findings → 10 root causes.** No finding maps to two root causes; the mapping is a
partition, not a covering.

---

### `RC-1` — Classification outage

| Field | Content |
|---|---|
| **Root cause** | The mutation-governance register declares a **two-sided coverage contract** and nine rules, but only eight predicates exist. Because the contract declares *"Every mutation subject resolves… never to nothing, and never to a default,"* one missing predicate is a coverage failure for **every** subject, not for the subset the rule would have claimed. |
| **Evidence** | `RULE_PREDICATES` = `['R-01'…'R-08']` (8). Rules declared `R-01…R-09` (9). `validate_rule_coverage(boundary)` → `("rule 'R-09' is declared but no predicate implements it",)`. `classify()` → `ERROR` for **every** subject in the repository. `BC-1` = **0 / 8** acceptance criteria, `evidence: none` on all eight. `BC-1`'s own test `platform/tests/test_mutation_classification.py` is tracked-modified `+3/−3` and adds **no** `R-09` coverage. |
| **Impact** | No act in the repository can name its governing class, and therefore none can name its authority. Identity arbitration cannot begin for one subject. `R-09 GOVERNED_ANALYSIS` is precisely the class governing **127 of the 192** Group B subjects and the modified MIP plan (`G-11`). Every mutation-class statement in every determination in this corpus is a manual reading, not a machine verdict. |
| **Dependency** | None. `RC-1` is a graph root. |
| **Closure action** | `CA-1` |
| **Authority requirement** | **AVAILABLE — engineering.** `BC-1` records *"engineering execution; a declared rule is made to function"*, owner Repository Intelligence read from the register's `governed_by` chain, **not assigned**. |
| **Acceptance criteria** | `validate_rule_coverage()` returns `()`; `classify()` returns `CLASSIFIED` or `UNRESOLVED` — never `ERROR` — for a sample spanning all nine classes; deterministic on digest-compared repeat; zero mutations during classification, mutation-tested; unknown input → `UNRESOLVED`, never permissive; missing `Authority` falls through to `R-08`, no fabrication; a declared-but-unimplemented rule fails at test time; mutations certified while unclassified are disclosed. **Explicitly out of scope:** a tenth rule, any change to `R-01…R-08`, any change to precedence, any weakening of the coverage contract. |

---

### `RC-2` — No authority-admission map

| Field | Content |
|---|---|
| **Root cause** | Even with class resolution repaired, **class does not resolve to authority**. The mutation-class vocabulary — the only candidate carrier — cannot hold the mapping. |
| **Evidence** | Occurrences of `UCOS-UGA-001` in `00-BOOK/DATA/mutation-governance-boundary.json`: **0**. The identity-minting programme appears in none of the nine classes. **3 of 9** classes resolve to an owner-parameterised placeholder read off the subject rather than to a named authority (`GOVERNED_DECLARATION`, `AUTHORED_DOCUMENT`, `GOVERNED_ANALYSIS`). `REG-AUTO-001`'s own `does_not_govern` states `by_object` *"is not a declared mutation class."* `by_observation`'s authority is unmapped in every candidate. |
| **Impact** | The canonical-identity selection rule `CIS-2` — *"the authority whose declared admission predicate the subject's governing class satisfies"* — is unevaluable even after `RC-1` closes. Arbitration has no admission predicate to test. |
| **Dependency** | `RC-1` — a map keyed on class requires class resolution to exist. |
| **Closure action** | `CA-4` |
| **Authority requirement** | **NOT LOCATED.** The register names no owner competent to add a cross-authority mapping. Adopting `uga-declaration.json`'s `object_classes` instead would make one programme's classifier the cross-authority arbiter, which `UCKP-ART-18` refuses. |
| **Acceptance criteria** | A declared, ratified map that is **total** over the class vocabulary *and* over the three ledger maps `["by_path","by_object","by_observation"]`; **functional** — no owner-parameterised value; **fail-closed** on `UNRESOLVED`; naming `UCOS-UGA-001` and the observation authority explicitly; residing in an authority register, not in a programme's code. |

---

### `RC-3` — Ungoverned registration transaction standing uncommitted

| Field | Content |
|---|---|
| **Root cause** | A `register.sh --guard` run, invoked as a read-only measurement inside a read-only determination, executed its full registration transaction. Its output stands uncommitted in the working tree, and **no Article 28 decision authorizes it.** The repository therefore holds 228 permanent identifiers whose minting authority does not exist. |
| **Evidence** | Disclosed at `…READY-UNCONDITIONAL-CLOSURE-DETERMINATION.md` §10.3: 238 pages emitted, ~36 identifiers minted, six ledgers rewritten, tree 78 → 329, anonymous objects 43 → 7. Confirmed by six independent measurements this session: `00-BOOK/PORTAL/` **238** dirty (228 untracked + 10 modified); `id-ledger.json` **+12,290/−8,058**; `change-ledger.json` **+22,898/−13,068**; `relationships.json` **+21,366/−17,670**; `artifacts.json` **+9,368/−3**; `generated-artifact-registry.json` **clean**. Ledger deltas: `by_path` 1,264 → **1,492** (+228); `page_cursor` 9,826 → **10,840** (+1,014); `category_seq` 117 → **200** keys — **83 new namespaces, 5 pre-existing counters advanced** (`BOOK, CON, IMP, ENG, ADR`). All 83 new namespaces are exactly **6** characters; HEAD's 117 span 3–12 with 54 at twelve. `artifacts.json` count 1,233 → **1,461**. `ADR-0017`: *"A future anonymous object requires its own decision under this same Article, not a standing blanket authorization."* |
| **Impact** | Creates **192 of the 217** dual-identity subjects (Group B), each holding both a `by_path` corpus identity and a `by_object` UGA identity. Under `AIF-L14` their admission is **unsealed**, so any supersession record naming them is an irreversible reference to something Recorded Truth does not carry. Simultaneously destroys the rollback boundary (`RC-7`) and makes every downstream measurement a measurement over uncommitted state. Enlarges the ungoverned-namespace population by 83 against a declared vocabulary of 50. |
| **Dependency** | `RC-4` — the transaction was possible **because** the command declared no mutation mode. `RC-3` is `RC-4` realized. |
| **Closure action** | `CA-3` |
| **Authority requirement** | **NOT AVAILABLE.** Requires a `CEP-002` Article 28 decision enumerating the population, from the corpus authority (`REG-AUTO-001` / `UMB-003`). The instruments exist — `00-BOOK/tools/register.sh` (14,087 bytes, executable) and the `REG-AUTO-001` standard (43,326 bytes) — but `constitutional-authority-alignment.json` carries **0** matches for `ratif`, so no ratification state is recordable for any authority. |
| **Acceptance criteria** | A recorded Article 28 decision that either (a) **ratifies** the 228 registrations, enumerating them, disclosing the irreversibility of the 1,014 consumed pages and the 83 new namespaces, and stating whether the identifiers are reproducible under the 6-character derivation; or (b) **reverts** them, with the counter trace disclosed — `category_seq` does not roll back, so re-minting would issue different identifiers. Either way: `git status --porcelain 00-BOOK/DATA/` empty; `by_path` = 1,492 **at HEAD** or 1,264 **at HEAD**; a clean rollback boundary exists. |

---

### `RC-4` — Verification acts mutate; no declared gate mode

| Field | Content |
|---|---|
| **Root cause** | Gates do not declare whether they observe or transact, so a command invoked to measure can mint permanent identity. This is not a latent hazard; it is a realized one, twice. |
| **Evidence** | **0 of 29** `.github/workflows/*.yml` declare a mutation mode. **4 of 46** Makefile gate targets declare one (`B-2`). ≥24 gate paths mutate undeclared. `GATE-PURITY-DETERMINATION` records the first realization: *"A `register.sh --guard` run over a corpus with 140 unregistered artifacts **minted all 140 permanent identities inside a verification path**."* §10.3 records the second, which produced `RC-3`. `S-1` (gate mutation-mode field, `H-06`/`CR-09`) is **OPEN**. |
| **Impact** | Every measurement in this corpus is taken with a non-zero probability of mutating the thing measured. Concretely: a first-party execution of `./verify.sh --full` cannot be authorized under a read-only mode, so `BC-6` criterion `A6-4` (*"failing stages identified first-party"*) is unreachable **by the very discipline that BC-6 requires** — a circularity that `RC-4` alone breaks. |
| **Dependency** | None. `RC-4` is a graph root, and it is the **causal antecedent of `RC-3`**. |
| **Closure action** | `CA-2` |
| **Authority requirement** | **AVAILABLE for the field; DECISION REQUIRED for the semantics.** Populating a `MODE` field on existing declarations is engineering. Deciding what `OBSERVE` and `TRANSACT` bind is `S-1`, owned by the mutation governance owner. |
| **Acceptance criteria** | Every gate target and every workflow declares `OBSERVE` or `TRANSACT`; a declared-`OBSERVE` gate run leaves `git status --porcelain` byte-identical, demonstrated not asserted; `test_verification_purity` extended to cover the declaration, so an undeclared gate fails at test time. |

---

### `RC-5` — Identity measurement vacuous and stale

| Field | Content |
|---|---|
| **Root cause** | The blocking law for this exact condition is wired to a measure that quantifies over one register, and the measurement artifact of record was computed before the condition existed. |
| **Evidence** | `uis.json` `UIL-02` verbatim: `{"id":"UIL-02","law":"Singular Identity","invariant":"No object SHALL possess more than one permanent UID.","measure":"identities_multiple","expect":0,"value":0,"blocking":true,"satisfied":true,"state":"SATISFIED"}` — at a baseline where `by_path ∩ by_object` = **217**. `uis.json` is **clean**, last written `de9b9f3e` `2026-08-10 21:31`, **84 commits** before HEAD, reporting `recorded_identities: 1,264` against a ledger of **1,492**. `gate: OPEN`, `blocking_failures: []`. `counts`: declared namespaces **50**, live **109**, `ungoverned_namespaces` **74**, `ambiguous_namespaces` **9**, `namespace_width` **6**. `grep "uis_engine" verify.sh` → **0 matches** across **14** `run_stage` invocations; reachable only from `make`. |
| **Impact** | Six of ten arbitration validation gates are unevaluable, because they depend on an instrument that measures one canonical identity per subject across all maps and no such instrument exists. The `MIG-7` pre-arbitration measurement is impossible. And the identity gate reports green over a repository state that no longer exists — the most load-bearing false-negative in the corpus. |
| **Dependency** | `RC-3` — the measure cannot be refreshed to a meaningful value while the ledger it measures is uncommitted. |
| **Closure action** | `CA-5` |
| **Authority requirement** | **AVAILABLE — engineering**, under `UIS-001` for the measure and the verification owner for the stage wiring. |
| **Acceptance criteria** | `identities_multiple` (or a declared successor) quantifies over **subjects across all three maps** and returns **217** at the pre-arbitration baseline; `UIL-02` **fails**, and the failure is recorded as expected and time-boxed to the migration window rather than discovered; `verify.sh` names `uis_engine.py --gate` as an observing stage; `test_verification_purity` still passes. **The window in which `UIL-02` reads `217 → 0` must be declared, not discovered** — `UIS-001`'s gate will be `CLOSED` for its whole duration, and a plan that does not state this will read, correctly, as having broken the identity gate. |

---

### `RC-6` — Supersession is law with no implementation surface

| Field | Content |
|---|---|
| **Root cause** | `supersede` is a ratified declared-intent transition under `AIF-L15`, with zero implementation. |
| **Evidence** | `00-BOOK/DATA/id-ledger.json` top-level keys: `version · by_path · page_cursor · category_seq · discovered_volumes · volume_seq · history · by_object · by_observation` — **nine keys, no supersession map**. `grep "supersede" 00-BOOK/tools/ukb.py` → **0**. `00-BOOK/DATA/` holds **17** files; none is a supersession store. `constitutional-authority-alignment.json` `planes[REPOSITORY_OBJECT].maps` = `["by_path","by_object","by_observation"]`; `mint_markers` = `["category_seq"]`. The register's own note at `:654`: *"Real components exist (CMG amendments, Lifecycle.SUPERSEDED/HISTORICAL, supersedes/superseded_by, evolves-from relation types, engine.constitution.evolution) but **no single cross-domain read path was confirmed**… this binding does not guess at the answer."* |
| **Impact** | `MIG-2` has nothing to write into; validation criterion `VC-5` has nothing to check. The migration rule that records supersession cannot execute. |
| **Dependency** | None. `RC-6` is a graph root — the store can be specified and built before any of the others resolve. |
| **Closure action** | `CA-6` |
| **Authority requirement** | **NOT LOCATED for the carrier decision; AVAILABLE for the build.** If the store lives inside the ledger, `planes[REPOSITORY_OBJECT].maps` must be amended so `CAA-INV-04` remains total — a constitutional-alignment act. `CAA-INV-04 EXACTLY_ONE_IDENTITY_AUTHORITY` currently PASSES over **6,413** identities and must still pass over a population **≥** that. |
| **Acceptance criteria** | A declared carrier with a schema; the store readable and empty; `CAA-INV-04` PASSES over a population ≥ 6,413; `rival_mints` = `[]`; `unshaped_identities` = `[]`; **0** supersessions recordable as `RETIRED` (`URS-5` — the subject has not left version control); no supersession written into an existing identity's `history` (`AIF-L17`, `UIL-13`). |

---

### `RC-7` — No rollback boundary

| Field | Content |
|---|---|
| **Root cause** | The identity ledger has no declared producer, so `git` is the only restore path — and `git` cannot separate an arbitration failure from the uncommitted transaction the arbitration depends on, because both write the same file. |
| **Evidence** | `generated-artifact-registry.json` holds **345** entries / 345 `canonical_path` values. `00-BOOK/DATA/id-ledger.json` is **absent** from that set and has **no `producer` and no `regeneration_command`** — yet the ten UGA surface entries classify it as `GENERATED_DETERMINISTIC` **as an input**. It is consumed as regenerable and registered as not. The ten UGA surfaces themselves *are* declared generated, `registration_status: EXCLUDED_FROM_CORPUS_REGISTRATION`, `regeneration_command: python3 00-MASTER/UCOS-UGA-001/uga_engine.py run`. `AIF-L17`: *"No deletion or edit of Recorded Truth; correction is a new event."* |
| **Impact** | Today there is **no `git` operation that reverts an arbitration failure without also discarding the 192 canonical identities the arbitration was performed over**. After the first supersession record, no rollback exists in any form — only forward-only compensation under `AIF-L15`. The 1,519 references across three UGA surfaces are recoverable by regeneration; the ledger underneath them is not. |
| **Dependency** | `RC-3` — the boundary is created by the sealing or discarding decision and by nothing else. |
| **Closure action** | `CA-7` |
| **Authority requirement** | **AVAILABLE — engineering** for the producer declaration; the boundary itself is created by `CA-3`, which is an authority act. |
| **Acceptance criteria** | Either `id-ledger.json` is registered with a declared producer and a `regeneration_command` that reproduces it byte-identically from a sealed input closure, **or** the registry entries that classify it `GENERATED_DETERMINISTIC` are corrected to `RECORDED` and the absence of a regeneration path is declared. Plus: `git status --porcelain 00-BOOK/DATA/` empty at the boundary commit; the three regenerable surfaces demonstrably restorable from the sealed ledger. |

---

### `RC-8` — Ownership unsatisfiable by construction

| Field | Content |
|---|---|
| **Root cause** | An authority problem in the shape of a data problem. The governed ownership catalogue is empty, and the machinery refuses to populate it by design. |
| **Evidence** | `platform/universal_ownership/catalog/ucos-ownership-declarations.json` → `assignments` = `{}` (**dict, length 0**), authority `Governed Ownership Authority`. The file's own description: *"an empty catalogue is an honest statement that no assignment has been governed yet, **never a licence to guess**"*, and it requires *"the canonical owner (**an authority, not a path**)."* `OwnershipDeterminationEngine.require_owner` raises `OwnershipFabricationError` rather than infer. First-party measurement: `subjects: 549 · declared: 151 · contested: 0 · unresolved: 398 · remediable: 195 · coverage: 27.5046%`, diagnosed `186 EVIDENCE-NOT-IN-CANONICAL-HOME-ZONE`, `212 NO-OWNERSHIP-EVIDENCE`, `2 LOCATOR-FORM-NOT-ADMITTED`, `45 LOCATOR-NOT-REGISTERED`, `195 ZONE-NOT-CANONICAL-HOME-ELIGIBLE`. `UCOD-001:363` — *"Every constitutional object has ownership | **FAIL** | 391 of 542 UNRESOLVED."* Coverage is **falling**: subjects rose 542 → 549 while declared owners stayed at 151. `BC-4` = **0 / 7**, three criteria `UNATTAINABLE-IN-REPO`. |
| **Impact** | Ownership closure by the governed surface is **0 / 549 = 0.00%**. The apparently contradicting claim that all 549 concepts are owned rests on `00-MASTER/UAKOS-CLOSURE-002/31-CONCEPT-OWNERSHIP-REGISTER.md`, which is **untracked** (ignored by a committed `.gitignore:58` rule) and which defines ownership as *"the top-level Repository-Truth zone of the concept's canonical home"* — **a directory path, not an authority**. Under `TRACK-001` fail-closed an untracked artifact is not committed Repository Truth, and under the governed catalogue's own schema a path is not an owner. Three mutually inconsistent populations exist for one question: **398 / 506 / 549**. |
| **Dependency** | `RC-10` (ratification) and `RC-1` (a governed assignment must be classifiable). `S-3` authority key, `S-4` evidence-kind constitutive status, `S-5` Article 28 block existence — all **OPEN**. |
| **Closure action** | `CA-8` (partition, engineering) and `CA-11` (ratification, authority) |
| **Authority requirement** | **PARTIAL.** Operating Ownership Discovery to produce the `P-A`/`P-B`/`P-C` partition is engineering. Ratifying any assignment is not: no ratifier is located, and Article 28 is external. `R-54` records that automated population of the 391/398 assignments *"is exactly the fabrication the machinery is built to refuse."* |
| **Acceptance criteria** | Partition produced with every subject in exactly one of `P-A`/`P-B`/`P-C`, no count estimated; zero fabrication — no assignment without a declared source **and** owner acceptance; unknown stays unknown, no `UNASSIGNED` fallback; the three-population conflict (398/506/549) resolved by declaring which run mode is canonical. **Full closure additionally requires** `A4-5` authority key resolution, `A4-6` ratification, `A4-7` every admitted subject resolving to one ratified owner — all three `UNATTAINABLE-IN-REPO`. |

---

### `RC-9` — Certification asserts states its own gates contradict

| Field | Content |
|---|---|
| **Root cause** | Certification records that a claim was made, never that it was measured — and three standing green attestations each describe a repository state that has since moved. |
| **Evidence** | `00-MASTER/UCOS-UGA-001/07-CERTIFICATION.json`: `verdict: CERTIFIED`, `blocking_deviations: []`, `declared_open: []`, `objects_governed: 6,145`, `minted_by_this_programme: 4,912`, five proof digests — while `uga_engine.py gate` **FAILS** on `UGA-INV-01` (7 violations) and `UGA-INV-10` (7 violations, measured 4,727), `ANONYMOUS OBJECTS: 7`. `00-BOOK/DATA/certification.json`: `verdict: CERTIFIED`, `domains_passed: 10/10`, identity domain detail `"1233 unique"` and `"cursor=9826"` — against a working tree of **1,492** and **10,840**; last written `1f9041cd` `2026-08-10`. `UNAF-001`: *"This architecture is frozen at commit `00bd45f`"*, *"Freeze READY 13/13"*, *"1203/1203 artifacts registered"* — `00bd45f` is an ancestor of HEAD by **154 commits**; artifacts registered are 1,233 at HEAD and 1,461 in tree. `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` (`engine/universal_certification/contracts.py:54`). `BC-3` = **0 / 7**. |
| **Impact** | `MIG-6`'s recomputation cannot close: it returns FAILED for reasons that predate arbitration and that arbitration would be blamed for. Five digests are invalidated by any identity act. And the corpus's own recorded failure mode — `100-PERCENT-IMPLEMENTATION-READINESS-CERTIFICATION.md` §8.2, where `54.3% NOT READY` became `100% READY` on the basis of *"8 determination documents produced"* with **no blocker discharged** — is the pattern `RC-9` describes at scale. |
| **Dependency** | `RC-1` (a certification act must be classifiable) · `RC-4` (gate purity must replace single-process evidence) · `RC-10` (the ceiling) · `S-2` temporal qualification. |
| **Closure action** | `CA-9` |
| **Authority requirement** | **PARTIAL.** Engineering may build the probes. **Each axis's declaring owner must accept that a standing certification loses its basis** — that acceptance is the blocking act. |
| **Acceptance criteria** | 16 / 16 axes instrumented, none omitted; axes 13–14 recorded (expected failing); five fields per certified item or a named absence; cross-process reproducibility replacing single-process evidence; **zero prose-only certifications remain — instrumented or withdrawn**; no verdict exceeds `CERTIFIED-PROVISIONAL`; timestamps qualified or an exemption declared. Under `AIF-L21`, recomputation writes a **new current status into a distinct store** and the prior attestation is retained verbatim — **never amended**. A red current status beside a retained green attestation is the lawful outcome, not a failure. |

---

### `RC-10` — The ratifying authority does not exist

| Field | Content |
|---|---|
| **Root cause** | The tier that ratifies is declared vacant in the repository's own registry, and every instrument that legislates a ratification, freeze or amendment act therefore legislates an act nobody can perform. |
| **Evidence** | `00-CMG/CMG-REGISTRY.json` `tiers[]`: `T1 "Constitutional Authority" occupancy: VACANT, vacancy: VAC-01`. `T0` LOCATED; `T1M`, `T2`, `T2I`, `T3`, `T4`, `T5` all LOCATED — **T1 alone is vacant**. `VAC-01`: `located: false`; *"The referent exists in the repository only as frozen non-normative source material under `00-SOURCE/CONSTITUTIONS/` (.docx)"*; *"Every determination depending on T1 — including the standing of `CMG-000001` itself — is PROVISIONAL."* `UCCEP-F-004`: *"Maximum attainable verdict anywhere in this repository is `CERTIFIED-PROVISIONAL`."* `CEP-006` legislates Ratification Authority as *"the single constitutional act through which a validated and certified artifact becomes an officially accepted member of the constitutional corpus"* — and `constitutional-authority-alignment.json` carries **0** matches for `ratif`. `CEP-007` XVI.1 mandates *"The Freeze Registry SHALL be the single canonical record of all freeze baselines"* — **no artifact matching `*freeze*registry*` exists**; `CEP-007` I.5 forbids self-conferral by Execution Authority. `MP2-C-04`: no competent ratifier. `D-1` (`CH-6` facet frame) and `D-2` (protocol representation) are **OPEN — packages prepared, not decided**; `BC-5` = **3 / 4**, the fourth `UNATTAINABLE-IN-REPO`. **And `READY UNCONDITIONAL` is not a member of the declared readiness vocabulary** — `Readiness ∈ { READY · CONDITIONALLY READY · NOT READY }`. |
| **Impact** | Caps every verdict in the repository at `CERTIFIED-PROVISIONAL`, including any verdict this determination could reach. Makes `RC-8`'s ratification criteria unattainable. Makes `RC-3`'s Article 28 decision unattainable by any located party. And makes the directive's target state require a vocabulary amendment before it requires engineering. |
| **Dependency** | None **inside** the repository. `RC-10` is a graph root **and** a terminal blocker, which is the structural signature of an external dependency. |
| **Closure action** | `CA-12` — **not reachable by repository work** |
| **Authority requirement** | **EXTERNAL CONSTITUENT ACT.** `CMG-000001` XVII.4 prescribes the closure procedure: record the vacancy; record the determinations rendered provisional; refer identification of the occupying authority to explicit ratification; re-run authority resolution on closure. `CMG-000001` XVII.4 and LXXXI.5 **forbid promotion of a lower instrument** to occupy the tier, and void any reading that permits it. |
| **Acceptance criteria** | An external act that occupies `T1` without promoting a lower instrument; `VAC-01.located` becomes `true`; authority resolution re-run; `UCCEP-F-004`'s ceiling lifted by the authority that set it. **Falsification test:** exhibit an in-repository act that occupies `T1` without promoting a lower instrument, and `RC-10` moves from external to engineering. |

---

## 3. Dependency Graph

### 3.1 Edges, each forced by a measurement

```
E-01  RC-4 ──▶ RC-3     0 of 29 workflows declare a mode; the ungoverned run is RC-4 realized
E-02  RC-1 ──▶ RC-2     a map keyed on class requires class resolution
E-03  RC-1 ──▶ RC-8     BC-4 dependency: a governed assignment must be classifiable
E-04  RC-1 ──▶ RC-9     BC-3 dependency: a certification act must be classifiable
E-05  RC-4 ──▶ RC-9     BC-3 A3-4: CR-01 must REPLACE single-process evidence
E-06  RC-3 ──▶ RC-5     the measure cannot be refreshed over an uncommitted ledger
E-07  RC-3 ──▶ RC-7     the boundary is created by the seal/discard act and nothing else
E-08  RC-10 ─▶ RC-8     A4-6 ratification; no ratifier located
E-09  RC-10 ─▶ RC-9     UCCEP-F-004 caps every verdict at CERTIFIED-PROVISIONAL
E-10  RC-2 ──▶ ARB      CIS-2 needs an admission predicate
E-11  RC-3 ──▶ ARB      AIF-L14: a supersession may not name an unsealed canonical id
E-12  RC-5 ──▶ ARB      MIG-7 before-measurement is impossible after the first record
E-13  RC-6 ──▶ ARB      MIG-2 has nothing to write into
E-14  RC-7 ──▶ ARB      no lawful execution without a rollback boundary
E-15  ARB ───▶ READY    217 subjects arbitrated is a precondition of the identity property
E-16  RC-8 ──▶ READY    ownership property unsatisfied for 398 of 549 subjects
E-17  RC-9 ──▶ READY    no certification evidence while the canonical gate exits non-zero
E-18  RC-10 ─▶ READY    ceiling; and READY UNCONDITIONAL is not in the vocabulary
```

`ARB` = *identity arbitration may begin*. `READY` = *the readiness property holds*.
Both are derived nodes, not root causes.

### 3.2 Depth

```
depth 0   RC-1    RC-4    RC-6    RC-10          ← four roots, no in-edges
depth 1   RC-2 ◀RC-1   RC-3 ◀RC-4   RC-8 ◀RC-10,RC-1   RC-9 ◀RC-1,RC-4,RC-10
depth 2   RC-5 ◀RC-3        RC-7 ◀RC-3
depth 3   ARB  ◀RC-2, RC-3, RC-5, RC-6, RC-7
depth 4   READY ◀ARB, RC-8, RC-9, RC-10
```

### 3.3 Graph rendering

```
                              ┌──────────────────────────────────┐
   RC-4 ───────────▶ RC-3 ────┤                                  │
  (gate mode)      (seal /    │──▶ RC-5 (measure) ──┐            │
     │              discard)  └──▶ RC-7 (rollback) ─┤            │
     │                                              │            │
     │              RC-6 (supersession store) ──────┤──▶ ARB ────┤
     │                                              │            │
   RC-1 ─────────▶ RC-2 (A(C) map) ─────────────────┘            ├──▶ READY
  (R-09)   │                                                     │
     │     └──────▶ RC-8 (ownership) ────────────────────────────▶│
     └────────────▶ RC-9 (certification) ───────────────────────▶ │
                       ▲                                          │
   RC-10 ──────────────┴──────────────────────────────────────────┘
  (T1 VACANT — external; a root AND a terminal blocker)
```

### 3.4 Graph metrics

| Metric | Value | Detail |
|---|---|---|
| Root causes | **10** | `RC-1`…`RC-10` |
| Derived nodes | **2** | `ARB`, `READY` |
| Edges | **18** | `E-01`…`E-18` |
| Roots (no in-edges) | **4** | `RC-1`, `RC-4`, `RC-6`, `RC-10` |
| Maximum depth | **4** | `READY` |
| Highest fan-in (root causes) | **`RC-9` = 3** | `RC-1`, `RC-4`, `RC-10` |
| Highest fan-in (all nodes) | **`ARB` = 5** | `RC-2`, `RC-3`, `RC-5`, `RC-6`, `RC-7` |
| Highest fan-out | **`RC-10` = 3** and **`RC-1` = 3** and **`RC-3` = 3** | `RC-10` → `RC-8`, `RC-9`, `READY` · `RC-1` → `RC-2`, `RC-8`, `RC-9` · `RC-3` → `RC-5`, `RC-7`, `ARB` |
| Transitive fan-out leader | **`RC-1`** | reaches `RC-2`, `RC-8`, `RC-9`, `ARB`, `READY` = 5 of 12 nodes |
| Parallelizable at depth 0 | **4** | but only `RC-1`, `RC-4`, `RC-6` are workable; `RC-10` is external |
| Cycles | **0** | the graph is acyclic |

---

## 4. Critical Path

### 4.1 The path

```
RC-4 ──▶ RC-3 ──▶ RC-5 ──▶ ARB ──▶ READY
 │        │        └─ RC-7 ──┘
 │        └─ authority act (Article 28) ── THE PATH CROSSES AN AUTHORITY BOUNDARY HERE
 └─ engineering + S-1 decision
```

**Length 5 nodes / 4 edges.** This is the longest chain in the graph and the binding constraint
on total depth.

### 4.2 Why this path and not another

`RC-1 → RC-2 → ARB → READY` is length 4 and entirely blocked on one unlocated authority
(`RC-2`). `RC-10 → RC-9 → READY` is length 3. `RC-6 → ARB → READY` is length 3.
`RC-4 → RC-3 → {RC-5 | RC-7} → ARB → READY` is length **5**, and it is the only chain in which
each link is forced by a *measured mechanism* rather than by an authority gap:

| Link | Forced by |
|---|---|
| `RC-4 → RC-3` | 0 of 29 workflows declare a mode; the ungoverned run is that absence realized |
| `RC-3 → RC-5` | `uis.json` reports 1,264 against a ledger of 1,492 — refreshing it over an uncommitted ledger measures nothing |
| `RC-3 → RC-7` | `id-ledger.json` and `artifacts.json` carry both the transaction and any arbitration write; `git` cannot discriminate |
| `RC-5 → ARB` | `MIG-7`'s before-measurement is impossible after the first supersession record |
| `RC-7 → ARB` | after the first record, `AIF-L17` forbids deletion or edit; there is no rollback in any form |
| `ARB → READY` | 217 of 217 subjects arbitrated is a precondition of the identity property |

### 4.3 The property that makes this path decisive

**`RC-3` sits at position 2 of 5 and is an authority act.** Every engineering action downstream of
it — the measurement repair, the rollback boundary, the whole arbitration sequence — is gated on a
`CEP-002` Article 28 decision that no located party can take, about a mutation that has already
occurred.

That is the single most consequential structural fact in this determination: **the critical path
crosses the authority boundary at its second node, not at its last.** A plan that treats the
authority gaps as a tail-end concern has the sequence backwards.

### 4.4 What is genuinely parallel

Three actions have no in-edges among the root causes and may proceed concurrently today:

| Action | Root cause | Why it is unblocked |
|---|---|---|
| `CA-1` | `RC-1` | Repairs a defect that predates and is independent of every other; authority available |
| `CA-2` | `RC-4` | Declaration of an existing field's semantics; must precede `CA-3` |
| `CA-6` | `RC-6` | Specification and construction of an empty store touches no identity |

`CA-10` (mint the 7 anonymous objects) **appears** parallel and is not — see §5, `CA-10`.

---

## 5. Minimum Closure Actions

Twelve. No duplicates, no derived actions, no umbrella actions. Each closes at least one root
cause that no other action closes.

| ID | Action | Closes | Depends on | Authority | Class |
|---|---|---|---|---|---|
| **`CA-1`** | Implement the `R-09 GOVERNED_ANALYSIS` predicate in `RULE_PREDICATES` per its six declared membership criteria; add the regression guard that fails at test time on any declared-but-unimplemented rule | `RC-1` | — | Repository Intelligence — **AVAILABLE** | ENGINEERING |
| **`CA-2`** | Populate a mutation-mode field on all 46 gate targets and 29 workflows; resolve `S-1`'s semantics for `OBSERVE`/`TRANSACT`; extend `test_verification_purity` to fail on an undeclared gate | `RC-4` | — | Mutation governance owner — **DECISION (`S-1`)** | ENGINEERING + DECISION |
| **`CA-3`** | Record a `CEP-002` Article 28 decision that ratifies or reverts the 228 registrations / 238 pages / 1,014 consumed pages / 83 new namespaces, enumerating the population and disclosing irreversibility | `RC-3` | `CA-2` | Corpus authority (`REG-AUTO-001` / `UMB-003`) — **NOT LOCATED** | **AUTHORITY** |
| **`CA-4`** | Declare and ratify `A(C)`: total over the nine-class vocabulary and the three ledger maps, functional, fail-closed on `UNRESOLVED`, naming `UCOS-UGA-001` and the observation authority | `RC-2` | `CA-1` | Mutation governance owner, ratified — **NOT LOCATED** | **AUTHORITY** |
| **`CA-5`** | Re-scope `identities_multiple` to quantify over subjects across all three maps; refresh `uis.json`; register `uis_engine.py --gate` as an observing stage in `verify.sh`; declare and time-box the non-conformance window | `RC-5` | `CA-3` | `UIS-001` + verification owner — **AVAILABLE** | ENGINEERING |
| **`CA-6`** | Declare a supersession carrier, specify its schema, build it empty, and — if inside the ledger — amend `planes[REPOSITORY_OBJECT].maps` so `CAA-INV-04` remains total | `RC-6` | — | Identity authority + constitutional alignment owner — **PARTIAL** | ENGINEERING + DECISION |
| **`CA-7`** | Declare `id-ledger.json`'s producer and `regeneration_command`, or correct the registry entries that classify it `GENERATED_DETERMINISTIC` to `RECORDED` and declare the absence of a regeneration path | `RC-7` | `CA-3` | Generated-artifact registry owner — **AVAILABLE** | ENGINEERING |
| **`CA-8`** | Operate Ownership Discovery to produce the `P-A`/`P-B`/`P-C` partition with every one of the 549 subjects in exactly one class, no count estimated; declare which run mode is canonical, resolving the 398/506/549 conflict | `RC-8` *(partial)* | `CA-1` | Universal Ownership programme — **AVAILABLE for the partition** | ENGINEERING |
| **`CA-9`** | Instrument all 16 certification axes; record axes 13–14 as failing; withdraw every prose-only certification; recompute current status into a store distinct from the retained attestation under `AIF-L21` | `RC-9` *(partial)* | `CA-1`, `CA-2` | Certification owner **+ each axis's declaring owner must accept invalidation** — **PARTIAL** | ENGINEERING + AUTHORITY |
| **`CA-10`** | Mint identities and record audit events for the 7 anonymous objects, in a commit that carries no arbitration | contributes to `RC-9` (`uga_engine.py gate` PASS) | **`CA-3`** | `UCOS-UGA-001` — **AVAILABLE for the mint** | ENGINEERING |
| **`CA-11`** | Ratify ownership assignments; resolve `S-3` authority key, `S-4` evidence-kind constitutive status, `S-5` Article 28 block existence | `RC-8` *(closure)* | `CA-8`, `CA-12` | **NOT AVAILABLE** — no ratifier located; Article 28 external | **EXTERNAL** |
| **`CA-12`** | Occupy Tier `T1` per `CMG-000001` XVII.4 without promoting a lower instrument; re-run authority resolution; decide `D-1` and `D-2`; establish the `CEP-007` Article XVI Freeze Registry; amend the readiness vocabulary if `READY UNCONDITIONAL` is to be a reachable value | `RC-10` | — | **EXTERNAL CONSTITUENT ACT** | **EXTERNAL** |

### 5.1 The one action whose independence is measured false

`CA-10` is recorded in the predecessor register as dependency-free and *"dischargeable in parallel
today,"* while its own discharge test requires that *"the run is committed separately and named as
unrelated to arbitration."*

Measured, that test is not satisfiable at this baseline. `uga_engine.py` at lines 261–295:

```
"Shares the corpus `category_seq` counter. Consumes NO page range. Append-only:"
seq = ledger.setdefault("category_seq", {})
by_object[rel] = { … }
```

A `by_object` mint advances `category_seq` **inside `00-BOOK/DATA/id-ledger.json`** — the same file
and the same JSON object that already carries the transaction's 88 counter changes and 228
`by_path` registrations. A commit of the 7 mints therefore either carries the 228 registrations
with it, or requires partial staging of a single JSON object whose `by_path`, `page_cursor` and
`category_seq` values would be mutually inconsistent in the staged version.

The 7 are *substantively* independent — all tracked, all **clean at HEAD**, all disjoint from the
217:

```
engine/ceu/context_binding.py
engine/tests/ceu/test_context_binding.py
engine/tests/context/test_req_28_extensibility.py
engine/tests/lineage/test_req_43_upeg_certification.py
engine/tests/uckp/test_phase_2_requirement_evolution.py
platform/repository_intelligence/mutation_class_extension.py
platform/tests/test_violation_4_mutation_extension.py
```

They are *transactionally* entangled with `CA-3`. Both halves are measured; the dependency
`CA-10 → CA-3` follows from the second.

### 5.2 Minimality

| Test | Result |
|---|---|
| No duplicates | Each `CA` closes at least one root cause no other `CA` closes |
| No derived actions | No `CA` is the consequence of another; `CA-10` is retained because `RC-9`'s gate criterion cannot be met without it |
| No umbrella actions | No `CA` names a programme, phase, wave or effort — each names one act with one acceptance test |
| Sufficiency | `CA-1`…`CA-12` cover `RC-1`…`RC-10` with two partial closures (`RC-8` via `CA-8`+`CA-11`, `RC-9` via `CA-9`+`CA-10`) |
| Necessity | Removing any `CA` leaves at least one root cause with no closure path |

---

## 6. Authority Blockers

Nine. Each names the act, the authority the repository says must perform it, and what was
measured about that authority's availability.

| ID | Act requiring authority | Authority named by the repository | Measured availability | Blocks |
|---|---|---|---|---|
| **`AG-1`** | Implement `R-09`'s predicate | Repository Intelligence, *read from the register's `governed_by` chain, not assigned* | **AVAILABLE** — *"engineering execution; a declared rule is made to function"* | `CA-1` |
| **`AG-2`** | Declare gate mutation-mode semantics (`S-1`, `H-06`/`CR-09`) | Mutation governance owner | **DECISION OPEN** — 4 of 46 gate targets declare a mode; 0 of 29 workflows | `CA-2` |
| **`AG-3`** | Ratify or revert the 228 registrations under `CEP-002` Article 28 | Corpus authority — `REG-AUTO-001` / `UMB-003`; artifact lifecycle `ENG-001 D30` / `UMB-003 §3` | **INSTRUMENT PRESENT, RATIFICATION UNRECORDABLE** — `register.sh` and the `REG-AUTO-001` standard both exist; `constitutional-authority-alignment.json` has **0** `ratif` matches. `ADR-0017` refused a standing blanket mint | `CA-3` |
| **`AG-4`** | Declare `A(C)` over the class vocabulary | Mutation governance owner, ratified | **NOT LOCATED** — `UCOS-UGA-001` in 0 of 9 classes; 3 of 9 owner-parameterised; adopting a programme's classifier is refused by `UCKP-ART-18` | `CA-4` |
| **`AG-5`** | Decide the supersession carrier and amend `planes[REPOSITORY_OBJECT].maps` | Identity authority + constitutional alignment owner | **NOT LOCATED** — `CAA-INV-04` asserts exactly one identity authority over 6,413 identities; the register itself declines to assert a cross-domain supersession read path | `CA-6` |
| **`AG-6`** | Decide whether 85 pages remain bound to 25 superseded Group A corpus identities | Corpus authority via `UMB-003` | **REFERRED, UNRESOLVED** — Group A holds 0 of 25 `artifacts.json` records, narrowing the question to 85 pages; no decision record located | `CA-3` (Group A scope) |
| **`AG-7`** | Accept that a standing certification loses its basis | Certification owner **+ each axis's declaring owner** | **PARTIAL** — engineering may build probes; the acceptance is the blocking act. `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` | `CA-9` |
| **`AG-8`** | Ratify ownership; resolve `S-3`, `S-4`, `S-5` | Universal Ownership programme + each subject's owner | **NOT AVAILABLE** — `assignments = {}`; `require_owner` raises rather than infers; `R-54` forbids automated substitution; Article 28 external | `CA-11` |
| **`AG-9`** | Occupy Tier `T1`; decide `D-1`/`D-2`; establish the Freeze Registry; amend the readiness vocabulary | Constitutional Authority (`T1`) | **VACANT** — `VAC-01 located: false`; `CEP-007` I.5 forbids self-conferral by Execution Authority; `CMG-000001` XVII.4 / LXXXI.5 forbid promoting a lower instrument | `CA-12` |

### 6.1 Authority classification of the twelve actions

| Class | Count | Actions |
|---|---|---|
| **IMPLEMENTATION CLOSABLE** — authority available, engineering only | **5** | `CA-1`, `CA-5`, `CA-7`, `CA-8`, `CA-10` |
| **AUTHORITY DECISION REQUIRED** — a located party must decide | **3** | `CA-2` (`S-1`), `CA-6` (carrier), `CA-9` (axis owners) |
| **AUTHORITY NOT LOCATED** — the deciding party does not exist in-repo | **2** | `CA-3`, `CA-4` |
| **CONSTITUTIONAL AMENDMENT REQUIRED** | **1** | `CA-12` (vocabulary amendment; `D-2` Option B) |
| **EXTERNAL ACT REQUIRED** | **2** | `CA-11`, `CA-12` |

`CA-12` appears in three classes because it is a compound external act; it is counted once in the
twelve.

### 6.2 Ownership closure

| Measure | Value |
|---|---|
| Subjects | **549** |
| Declared owners | **151** |
| **Governed assignments in the catalogue** | **0** (`assignments = {}`) |
| Unresolved | **398** |
| Contested | **0** |
| Coverage, as the tool reports it | **27.5046%** |
| **Ownership closure by the governed surface** | **0 / 549 = 0.00%** |
| Trend | **FALLING** — subjects 542 → 549 while declared owners held at 151 |
| Populations in conflict for one question | **3** — 398 / 506 / 549 |
| Ratified assignments | **0** |

**Is ownership itself a blocker?** Yes, and at two distinct levels. The *partition* is engineering
(`CA-8`, authority available). The *assignment* is not: the catalogue is empty by design, and the
machinery raises `OwnershipFabricationError` rather than infer. `R-54` records that automated
population *"is exactly the fabrication the machinery is built to refuse."* So ownership blocks
`READY` and cannot be unblocked by work — only by `AG-8`, which depends on `AG-9`.

---

## 7. Engineering Closure Boundary

### 7.1 What engineering can close, completely

| Root cause | Action | Closure |
|---|---|---|
| `RC-1` | `CA-1` | **FULL** — a declared rule is made to function; authority available and recorded as such |
| `RC-5` | `CA-5` | **FULL**, once `CA-3` lands — the measure, the refresh and the stage wiring are all engineering |
| `RC-7` | `CA-7` | **FULL**, once `CA-3` lands — the producer declaration is a registry entry the registry owner may make |

### 7.2 What engineering can close partially, with the residue named

| Root cause | Engineering part | Residue | Residue owner |
|---|---|---|---|
| `RC-4` | Populate the mode field on 46 targets and 29 workflows; extend the purity test | The **semantics** of `OBSERVE`/`TRANSACT` — `S-1` | Mutation governance owner |
| `RC-6` | Specify the schema; build the store empty; validate `CAA-INV-04` totality | The **carrier decision** and the alignment amendment | Identity authority + alignment owner |
| `RC-8` | Produce the `P-A`/`P-B`/`P-C` partition; resolve the 398/506/549 mode conflict | **Every assignment and its ratification** — `A4-5`, `A4-6`, `A4-7` | `AG-8` → `AG-9` |
| `RC-9` | Instrument 16 axes; withdraw prose-only certifications; recompute into a distinct store | **Acceptance that a standing certification loses its basis** | Each axis's declaring owner |

### 7.3 What engineering cannot touch

| Root cause | Why |
|---|---|
| `RC-2` | A map declaring which authority admits which class **is** an authority act. Deriving it from a programme's code makes that programme the cross-authority arbiter — refused by `UCKP-ART-18` |
| `RC-3` | The mutation already occurred. Ratifying it after the fact is an Article 28 decision; reverting it destroys 228 identifiers and 1,014 page allocations. Engineering can do neither lawfully |
| `RC-10` | `CEP-007` I.5 forbids self-conferral by Execution Authority; `CMG-000001` XVII.4 and LXXXI.5 forbid promoting a lower instrument. There is no in-repository act |

### 7.4 The engineering-achievable terminal state

Closing `CA-1`, `CA-2`, `CA-5`, `CA-6`, `CA-7`, `CA-8`, `CA-10` — every action whose authority is
available or whose decider is located — reaches:

```
RC-1   CLOSED
RC-4   CLOSED (pending S-1)
RC-5   CLOSED (pending CA-3)
RC-6   CLOSED (pending carrier decision)
RC-7   CLOSED (pending CA-3)
RC-8   PARTITIONED, NOT ASSIGNED
RC-9   INSTRUMENTED, NOT ACCEPTED
RC-2   OPEN — no located authority
RC-3   OPEN — no located authority
RC-10  OPEN — external
```

**Three root causes remain open after every available engineering act, and all three are
authority, not work.** That is the engineering closure boundary.

---

## 8. Constitutional Closure Boundary

### 8.1 The three instruments that set the boundary

| Instrument | Verbatim | Consequence |
|---|---|---|
| `VAC-01` | `located: false` · *"No ratified normative artifact occupies the tier"* · *"Every determination depending on T1 — including the standing of `CMG-000001` itself — is PROVISIONAL"* | No verdict in this repository is final, including this one |
| `UCCEP-F-004` | *"Maximum attainable verdict anywhere in this repository is `CERTIFIED-PROVISIONAL`"* | An unconditional claim exceeds the declared ceiling and is unsatisfiable by construction |
| `CMG-000001` XVII.4 / LXXXI.5 | Promotion of a lower instrument to occupy `T1` is forbidden, and any reading that permits it is void | The vacancy cannot be closed from inside, by any act, at any tier |

### 8.2 What the constitution requires and the repository does not have

| Requirement | Instrument | Repository state |
|---|---|---|
| A Freeze Registry — *"the single canonical record of all freeze baselines"*, append-only, content-addressed, reconciled at boot | `CEP-007` XVI.1–XVI.3 | **No artifact matching `*freeze*registry*` exists.** The mechanism exists (`freeze.py`, `FZ-01…FZ-13`, a worked band-11 record with `FP-1…FP-6` all true) and is scoped to the Universal Foundation, not to identity |
| A freeze record naming *"the artifact, the Freeze Authority, the preconditions satisfied, the baseline digest, the version, the lineage, the state, and the program-state hash"* | `CEP-007` XVII.1 | The declared architecture freeze names `00bd45f` — **154 commits** behind HEAD — and cites 1,203 registered artifacts against 1,461 in tree |
| A ratification act recorded per authority | `CEP-006` P.2, I.1 | `constitutional-authority-alignment.json` carries **0** matches for `ratif` |
| `READY UNCONDITIONAL` as a readiness value | — | **Not in the vocabulary.** `Readiness ∈ { READY · CONDITIONALLY READY · NOT READY }`, owned by registry slot `R-13` |
| Two constitutional decisions | `D-1` (`CH-6` facet frame: invariant or limitation) · `D-2` (protocol representation: extension or amendment) | **Both OPEN — packages prepared, neither decided.** `CR-15` records explicitly that `D-2` *cannot be an engineering act* |

### 8.3 The constitutional closure set

```
CA-12  requires, as one external constituent act:
       (a) occupy T1 without promoting a lower instrument     CMG-000001 XVII.4
       (b) record the determinations rendered provisional      CMG-000001 XVII.4(b)
       (c) refer the occupying authority to explicit ratification   XVII.4(c)
       (d) re-run authority resolution on closure              XVII.4(d)
       (e) decide D-1 and D-2
       (f) establish the CEP-007 Article XVI Freeze Registry
       (g) amend the readiness vocabulary, if READY UNCONDITIONAL is to be reachable

CA-11  requires (a)–(d) of CA-12, plus:
       ratify ownership assignments · resolve S-3, S-4, S-5
```

**Nothing in (a)–(g) is reachable by repository work, by any tier, in any order.** `T1` is the
only vacant tier of eight; `T0`, `T1M`, `T2`, `T2I`, `T3`, `T4` and `T5` are all LOCATED. The
repository is structurally complete except at the one position that ratifies.

---

## 9. Readiness Transition Model

### 9.1 The declared vocabulary, and where the target is not

```
Readiness ∈ { READY · CONDITIONALLY READY · NOT READY }
             ▲          ▲                    ▲
             │          │                    └── current state
             │          └── reachable after the engineering set + the located decisions
             └── requires CA-3, CA-4 (authority not located) and CA-9 acceptance

READY UNCONDITIONAL  ─── NOT A MEMBER OF THE VOCABULARY.
                         Requires CA-12(g), a T1-dependent amendment.
```

### 9.2 The state machine, with each transition's gate

```
  S0  NOT READY  ◀── current state at HEAD bae59755
   │
   │  T1: close the three depth-0 workable root causes
   │      CA-1 (RC-1) · CA-2 (RC-4) · CA-6 (RC-6)
   │      gate: validate_rule_coverage() == () ; every gate declares a mode ;
   │            supersession store readable and empty, CAA-INV-04 ≥ 6,413 PASS
   ▼
  S1  NOT READY — CLASSIFIABLE
   │      classify() no longer errors; measurement becomes attributable
   │
   │  T2: THE AUTHORITY BOUNDARY — CA-3 (RC-3)
   │      gate: a recorded CEP-002 Article 28 decision ; git status 00-BOOK/DATA/ empty
   │      ▓▓▓ BLOCKED — AG-3, no located ratifier ▓▓▓
   ▼
  S2  NOT READY — BASELINE SEALED
   │      the rollback boundary exists for the first time
   │
   │  T3: CA-5 (RC-5) · CA-7 (RC-7) · CA-10 · CA-8 (RC-8 partition)
   │      gate: identities_multiple == 217 over three maps ; ledger producer declared ;
   │            uga_engine.py gate exits 0 ; P-A/P-B/P-C partition total over 549
   ▼
  S3  CONDITIONALLY READY — ARBITRABLE
   │      0 of 217 → 217 of 217 arbitrable, IF CA-4 has landed
   │      ▓▓▓ CA-4 BLOCKED — AG-4, no located authority ▓▓▓
   │
   │  T4: CA-9 (RC-9) — instrument 16 axes, accept invalidation
   │      gate: zero prose-only certifications ; current status recomputed into a
   │            distinct store ; prior attestation retained verbatim (AIF-L21)
   │      ▓▓▓ PARTIAL — AG-7, each axis's declaring owner must accept ▓▓▓
   ▼
  S4  READY WITH CONDITIONS — every residual condition external and enumerated
   │      ◀── THE REACHABLE TERMINAL STATE
   │
   │  T5: CA-11 (RC-8 closure) · CA-12 (RC-10)
   │      gate: T1 occupied ; ownership ratified ; Freeze Registry established ;
   │            vocabulary amended
   │      ▓▓▓ NOT REACHABLE BY REPOSITORY WORK — AG-8, AG-9 ▓▓▓
   ▼
  S5  READY UNCONDITIONAL  ── unreachable, and not a vocabulary member
```

### 9.3 The transition table

| From | To | Actions | Blocked by | Reachable |
|---|---|---|---|---|
| `S0` | `S1` | `CA-1`, `CA-2`, `CA-6` | `S-1`, carrier decision — **located deciders** | **YES** |
| `S1` | `S2` | `CA-3` | `AG-3` — **not located** | **NO** |
| `S2` | `S3` | `CA-5`, `CA-7`, `CA-8`, `CA-10` | `CA-4` / `AG-4` — **not located** | conditional on `S2` |
| `S3` | `S4` | `CA-9` | `AG-7` — **located but must accept** | conditional on `S3` |
| `S4` | `S5` | `CA-11`, `CA-12` | `AG-8`, `AG-9` — **external** | **NO** |

### 9.4 The unconditional readiness test

> *"If all minimum closure actions were completed exactly as defined, would `READY UNCONDITIONAL`
> be justified?"*

**Verdict: DISPROVEN.**

The test fails on three independent grounds, each measured:

1. **The ceiling.** `UCCEP-F-004` caps every verdict at `CERTIFIED-PROVISIONAL`. `CA-12` is the
   only action that could lift it, and lifting it is the external act, not a consequence of
   completing the set. Completing all twelve actions leaves the ceiling exactly where it was
   unless `CA-12` is among the completed — and `CA-12` is by definition not repository work.
2. **The vocabulary.** `READY UNCONDITIONAL` is not one of the three declared values. Completing
   twelve actions cannot make a verdict out of a value that the owning registry does not
   enumerate. The amendment is `CA-12(g)`.
3. **The provisionality cascade.** `VAC-01.provisional_consequence` states that every
   determination depending on `T1` — *"including the standing of `CMG-000001` itself"* — is
   `PROVISIONAL`. An unconditional readiness verdict issued under a provisional constitution is
   itself provisional, which is a contradiction in terms.

**What *is* proven:** completing `CA-1`, `CA-2`, `CA-5`, `CA-6`, `CA-7`, `CA-8`, `CA-9`, `CA-10`
and `CA-3` reaches `S4` — `READY WITH CONDITIONS` where the residual conditions are exactly
`CA-11` and `CA-12`, both external, both enumerated, both declared. That is the shape `TC-4`
already used for this exact dependency (*"Constitutional finality remains external and
non-blocking"*) and the shape `EC-1…EC-6` uses at constitutional scale.

### 9.5 Irreducible blockers after the minimum closure set

| Blocker | Classification | Why it survives |
|---|---|---|
| `RC-10` | **CONSTITUTION** | `T1` VACANT; promotion of a lower instrument is forbidden and any reading permitting it is void. No in-repository act exists |
| `RC-8` *(assignment layer)* | **OWNERSHIP** + **EXTERNAL** | `assignments = {}` by design; `require_owner` raises rather than infers; `R-54` forbids automated substitution; Article 28 is external |
| `RC-3` | **AUTHORITY** | The deciding party is not located. Note this is *reducible in principle* — vesting the corpus authority is a smaller act than occupying `T1` — but not by work |
| `RC-2` | **AUTHORITY** | Same shape as `RC-3`: the act is small, the authority is absent |
| `RC-9` *(acceptance layer)* | **CERTIFICATION** | Instrumentation is engineering; accepting that a standing certification loses its basis is the declaring owner's act |

**Five irreducible residues across four classifications.** Two of the five (`RC-2`, `RC-3`) would
be discharged by vesting authorities that the repository names but does not staff — which is a
materially smaller ask than `RC-10`, and worth separating in any plan.

---

## 10. Final Determination

### 10.1 The verdict

> # NOT READY
>
> **10 root causes. 5 of 12 closure actions require an authority act. 3 root causes remain open
> after every available engineering act. `READY UNCONDITIONAL` is not reachable by repository
> work and is not a member of the declared readiness vocabulary. The reachable terminal state is
> `READY WITH CONDITIONS`, with `CA-11` and `CA-12` as the enumerated external residue.**

### 10.2 Reasoning, in the order the evidence forces

1. **The current state is `NOT READY`, and the verdict landscape is unreconciled.** Eight
   readiness verdicts coexist across the corpus, none declaring itself superseded or superseding.
   The one at the live baseline `bae59755` reads `# NOT READY` with six blockers *"each
   independently sufficient."* The one asserting `READY WITH CONDITIONS` is at `5874ede`, over the
   FOUNDATION → SYSTEMATIC IMPLEMENTATION scope, and `CEP-000` `30.2 CM-2` forbids reading stage
   completion as successor authorization. Applying it to the current state is a scope error.
2. **112 registered findings collapse to 10 root causes** — an 11.2 : 1 ratio. The corpus's
   apparent breadth of problems is a reporting artifact, not a structural one. This is the
   encouraging half of the determination.
3. **Four root causes are graph roots and three of the four are workable today** (`RC-1`, `RC-4`,
   `RC-6`). The fourth (`RC-10`) is a root *and* a terminal blocker, which is the structural
   signature of an external dependency.
4. **The critical path crosses the authority boundary at its second node.** `RC-4 → RC-3 → {RC-5,
   RC-7} → ARB → READY`, and `RC-3` is a `CEP-002` Article 28 decision about a mutation that has
   already occurred, ungoverned, inside a read-only determination. Every engineering action
   downstream of it is gated on an authority that is not located.
5. **The one measurement that reframes the work:** the 228 registrations are not pending work.
   They are the residue of `register.sh --guard` executing its full transaction when invoked to
   measure — confirmed at this baseline by six independent numstat matches against the
   predecessor's disclosure. `RC-4` is therefore not a hypothetical purity concern; it is the
   mechanism that produced `RC-3`, which produced 192 of the 217 dual-identity subjects.
6. **Ownership closure by the governed surface is 0.00%**, is falling, and is unsatisfiable by
   construction — the catalogue is empty by design and the engine raises rather than infers. The
   only register reporting complete ownership is untracked and measures a directory path, not an
   authority.
7. **Three standing certifications each report green over a repository state that has moved.**
   None is wrong about what it measured; all three are being read as statements about now.
8. **The ceiling is declared, not inferred.** `UCCEP-F-004` caps every verdict at
   `CERTIFIED-PROVISIONAL`; `VAC-01` makes every `T1`-dependent determination provisional,
   *including the standing of `CMG-000001` itself*. An unconditional verdict under a provisional
   constitution is a contradiction the repository has already legislated against.
9. **And the target does not exist.** `Readiness ∈ { READY · CONDITIONALLY READY · NOT READY }`.
   Reaching `READY UNCONDITIONAL` requires amending the vocabulary before writing a line of code,
   and the amendment is `T1`-dependent.

### 10.3 What follows, stated as a recommendation and not a verdict

The productive reading of this determination is not that the programme is stalled. It is that the
programme has been measuring twelve actions as though they were 112 problems, and has been
sequencing its authority gaps last when the critical path crosses them second.

Three actions are unblocked today (`CA-1`, `CA-2`, `CA-6`), all three are engineering, and all
three are prerequisites of everything else. `CA-2` in particular closes the mechanism that
produced the largest single blocker in the graph, and it is a field declaration plus a test.

The two authority gaps on the critical path (`AG-3`, `AG-4`) are **vesting problems, not
ratification problems** — they need a located corpus authority and a located mutation-governance
owner, both of which the register already names. They are materially smaller than `AG-9`, and
separating them from it is the single highest-leverage change available to any plan built on this
determination.

`AG-9` — Tier `T1` — is the one thing that must be awaited rather than worked. The corpus's own
instruction on this distinction is worth restating: *"Reserved decisions are … owner decisions
awaiting a person, not repository work awaiting a process. Sequencing them as backlog would
misrepresent them."*

---

## 11. Verification Record

| Check | Result |
|---|---|
| File exists | ✅ `UCOS-OMEGA-INFINITY-ROOT-CAUSE-CLOSURE-AND-READINESS-DETERMINATION.md` |
| Line count | ✅ measured after write — see §11.1 |
| Section count | ✅ **11** — §1 Executive Determination · §2 Root Cause Register (`RC-1`…`RC-10`) · §3 Dependency Graph · §4 Critical Path · §5 Minimum Closure Actions (`CA-1`…`CA-12`) · §6 Authority Blockers (`AG-1`…`AG-9`) · §7 Engineering Closure Boundary · §8 Constitutional Closure Boundary · §9 Readiness Transition Model · §10 Final Determination · §11 Verification Record |
| Required per-root-cause fields | ✅ all seven present for each of `RC-1`…`RC-10` — Root cause · Evidence · Impact · Dependency · Closure action · Authority requirement · Acceptance criteria |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Tracked modifications unchanged | ✅ **38** — identical set to session start |
| Working tree | ✅ 351 → 352 porcelain lines; untracked 313 → 314; the single delta is this file |
| Only one new artifact | ✅ the single repository delta is this file |
| Code changes | ✅ **0** |
| Configuration changes | ✅ **0** |
| Registry changes | ✅ **0** |
| Certification changes | ✅ **0** |
| Identity changes | ✅ **0** — `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · `category_seq` 200 keys |
| Ownership changes | ✅ **0** — `assignments` remains `{}` |
| Commits | ✅ **0** |
| Additional discovery performed | ✅ **NONE** — every figure is carried from measurements recorded earlier in this session |
| Root causes closed | ✅ **0** |
| Blockers discharged | ✅ **0** |
| Authorities ratified | ✅ **0** |
| Verdict issued | **NOT READY** — a determination, carrying no authority, capped at `CERTIFIED-PROVISIONAL` by `UCCEP-F-004` and rendered `PROVISIONAL` by `VAC-01` like every other determination in this corpus |

### 11.1 Measurement note

The line count and the post-write porcelain count are asserted by commands run against this file
after it was written, and their results are recorded in the session transcript rather than
hard-coded here. A self-reported line count inside the file it counts is the one figure in this
determination that cannot be verified from the artifact alone.

---

*This determination closed no root cause, discharged no blocker, ratified no authority, arbitrated
no subject, minted no identity and assigned no ownership. `by_path` stands at 1,492, `by_object` at
4,914 and `by_observation` at 7, before and after; the ownership catalogue holds zero assignments,
before and after; the working tree carries the same 38 tracked modifications it carried at session
start. It collapses 112 registered findings into ten root causes, twelve minimum closure actions
and nine authority blockers, and returns **NOT READY**. Three findings carry the weight. The 228
uncommitted corpus registrations that create 192 of the 217 dual-identity subjects are not pending
work — they are the residue of `register.sh --guard` executing its full registration transaction
when it was invoked to measure, confirmed here by six independent numstat matches, and no Article
28 decision authorizes them; which places an unlocated authority at the second node of the
critical path rather than the last. Ownership closure by the governed surface is zero of 549 and
falling, and the only register reporting otherwise is untracked and measures a directory rather
than an authority. And the target state does not exist: `READY UNCONDITIONAL` is absent from the
three-value readiness vocabulary its owning registry declares, so reaching it requires a
constitutional amendment before it requires a line of code — while `UCCEP-F-004` caps every
verdict at `CERTIFIED-PROVISIONAL` and `VAC-01` records that Tier T1, alone among eight tiers, is
vacant. Seven of twelve closure actions are engineering. Three are unblocked today. Two of the
authority gaps on the critical path are vesting problems the register already names owners for,
and separating those from the constitutional vacancy is the highest-leverage correction available
to any plan built on this document. The single repository mutation is the creation of this file.*

**END DETERMINATION — 10 ROOT CAUSES · 12 CLOSURE ACTIONS · 9 AUTHORITY BLOCKERS · 5 IRREDUCIBLE RESIDUES · READY UNCONDITIONAL DISPROVEN · VERDICT NOT READY · ZERO CLOSURES PERFORMED · STOPPED AFTER ARTIFACT CREATION.**
