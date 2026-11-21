# UCOS Ω∞ — R-09 PREDICATE DECISION AUTHORIZATION DETERMINATION

**Whether Option A has valid authorization. The measured answer is that `AG-2b` was mis-specified: the party it names does not exist, and the authority it needs is vested in two surfaces that do.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-R09-PREDICATE-DECISION-AUTHORIZATION-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Vests no authority, ratifies nothing, discharges no blocker by its own force, implements nothing. It reports what the repository's own authority records say, and where they are silent it says so. |
| Mode | ANALYSIS ONLY · **NO `mutation_classification.py` · NO `RULE_PREDICATES` · NO `mutation-governance-boundary.json` · NO OPTION A IMPLEMENTATION · NO `classify()` · NO STATE-MUTATING TESTS · NO REGISTRY · NO CERTIFICATION · NO IDENTITY · NO OWNERSHIP · NO COMMIT** |
| Gap addressed | `AG-2b` located but not discharged — raised by `…WAVE-0-EXECUTION-IMPLEMENTATION-DETERMINATION.md` §3.2, carried by `…R09-PREDICATE-ARCHITECTURE-RESOLUTION-DETERMINATION.md` and `…R09-PREDICATE-IMPLEMENTATION-READINESS-DETERMINATION.md` |
| Method | Read-only search and measurement at HEAD `bae59755`: parsed `mutation-governance-boundary.json` `authorities` and every class `governed_by` chain; parsed `constitutional-authority-alignment.json` `subordinate_instruments`, `authority_roles`, `extension_rule`, `non_goals`, `invariants`; read `UCKP-ART-10`/`ART-16` verbatim from `engine/uckp/law.py`; read `REPOSITORY_INTELLIGENCE_AUTHORITY` at `contracts.py:64`. Term-frequency counts run against both registers. |
| **Central finding** | **`"mutation governance owner"` occurs 0 times in the mutation governance register and 0 times in the constitutional authority alignment register.** It is a designation this determination chain introduced, not one the repository declares. `AG-2b` was recorded `LOCATED` against a party that does not exist under that name — §3.2 |
| Countervailing finding | **The authority Option A actually needs is vested, in two places, and neither requires a constitutional act** — §3.3, §3.4 |
| Preserved | No invented authority · no inference presented as evidence · no implementation · no closure claimed |

---

## 1. Current Baseline

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **357** lines |
| Tracked modifications | **38** |
| Staged | **0** |

### 1.1 Current R-09 state

```
declared      mutation_classes[8] GOVERNED_ANALYSIS · rule R-09 · precedence 9 · six criteria
implemented   NONE — RULE_PREDICATES = R-01…R-08 (8 entries, verified at this baseline)
coverage      validate_rule_coverage() → ("rule 'R-09' is declared but no predicate ...",)
classify()    ERROR for every subject, repository-wide
relation      R-09 ⊂ R-08 strictly; | R-09 \ R-08 | = 0 measured over 6,188 tracked paths
population    92 case-insensitive · 1 case-sensitive — undeclared (Q-1)
```

### 1.2 `AG-2b` status as carried into this determination

| Field | As recorded by the prior two determinations |
|---|---|
| Authority | "Mutation governance owner — the same party holding `AG-2` and `AG-4`" |
| Availability | **LOCATED, OPEN** |
| Constitutional dependency | NONE for Option A |
| Open sub-decisions | 5 — option confirmation · `Q-1` · `Q-2` · `Q-3` · `Q-4`; `Q-5` referred separately |
| Decision record | **NONE LOCATED** |

**§3.2 establishes that the `LOCATED` attribution cannot be sustained as written.**

### 1.3 Option A readiness status

| Field | Value |
|---|---|
| Verdict carried in | **`CONDITIONALLY READY`** |
| Design | Complete — shared `_analysis_artifact` helper, sixth `not-analysis-artifact` criterion on R-08, R-09 declaration unchanged, precedence unchanged |
| Arithmetic | **439 = 347 + 92**, conserved exactly; zero new `UNRESOLVED` under symmetric implementation |
| Sole material risk | Asymmetric token test → **91** artifacts with no class; mitigated by the shared helper |
| Blast radius | **4 files**; no gate, engine, workflow or `verify.sh` stage consumes mutation class |
| Certification / identity / ownership coupling | **Zero, measured** |
| Conditions outstanding | **7**, six attributed to one owner |

---

## 2. Decision Authority Identification

### 2.1 Mutation governance owner

| Field | Measured |
|---|---|
| **Authority source** | **NONE FOUND.** `"mutation governance owner"` → **0 occurrences** in `mutation-governance-boundary.json`; **0** in `constitutional-authority-alignment.json` |
| What the register declares instead | An `authorities` array of **8 entries, every one a mechanism**: `UCOS-CMG-EXEC-000001` (`engine/constitution/gateway.py`) · pre-commit hook (`scripts/ucos-env.sh::ucos_ruff_gate`) · `verify.sh` · `UCOS-RIB-001` · `UCOS-AEE-001` · Phase 8 · Phase 9 · `REG-AUTO-001` (`00-BOOK/tools/register.sh`) |
| Responsibility | Not assignable — the role is not declared |
| Decision boundary | **Undefined, because the role is undefined** |

**No party in this repository is declared as the owner of the mutation governance register's content.** The eight declared authorities govern *mutations of classes of thing*; none governs *the definition of the classes themselves*.

### 2.2 The mutation governance boundary instrument

| Field | Measured |
|---|---|
| **Authority source** | `constitutional-authority-alignment.json` `subordinate_instruments[8]` — `id: UCOS-MUTATION-GOVERNANCE-BOUNDARY-001` |
| Declared record, verbatim | `role: "EXECUTION"` · `relation: "PROJECTION"` · `derives_under: ["UCKP-ART-10","UCKP-ART-16"]` · **`owns: "Which mutation classes exist and which authority disposes of each."`** · `may_never_own: "Knowledge."` |
| **Responsibility** | **It owns exactly the question Option A answers.** Option A changes which class exists over which subject |
| **Decision boundary** | `authority_roles.EXECUTION` — *"a technology that acts on objects; execution never owns knowledge"*, `may_hold_authority: **false**`. `authority_roles.PROJECTION` — *"may state repository reality and may never state law"*, `may_hold_authority: **false**` |

**The instrument owns the content and may hold no authority. It records; it cannot decide.** That is not a defect — it is `UCKP-ART-10` operating as designed, and it is why the question "who decides" does not resolve to the register itself.

### 2.3 Repository Intelligence owner

| Field | Measured |
|---|---|
| **Authority source** | `constitutional-authority-alignment.json:610` — `{"id": "REPOSITORY-INTELLIGENCE", "home": "platform/repository_intelligence/", "role": "AUTHORITY", "bounded_question": "What exists, what can be reused, what is missing, **what conflicts**, what is duplicated, and who owns it — across the whole repository substrate?"}` |
| Second record | `:510` — `REPOSITORY-INTELLIGENCE-CERTIFICATION`, `role: "AUTHORITY"`, `authority_claim: "ENGINEERING-EXECUTION-ONLY (REPOSITORY_INTELLIGENCE_AUTHORITY constant, platform/repository_intelligence/contracts.py:64)"`, and its own docstring: the certificate *"confers no constitutional authority (DE-05/IP-01): it records derived engineering truth about the repository"* |
| Code confirmation | `contracts.py:64` — `REPOSITORY_INTELLIGENCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"`, comment: *"Repository Intelligence confers no constitutional authority (DE-05 / IP-01)"* |
| Register mention | `"Repository Intelligence"` appears **once** in `mutation-governance-boundary.json` — in `GOVERNED_ANALYSIS`'s `governed_by` chain: *"the authority the analysis declares of itself (owner-parameterised, read from Authority field) → **Repository Intelligence** → verify.sh (observation only)"* |
| **Responsibility** | **Vested, with role AUTHORITY, and its bounded question explicitly includes *"what conflicts"*** — which is precisely the R-08/R-09 overlap |
| **Decision boundary** | **ENGINEERING-EXECUTION-ONLY.** It may *detect*, *measure* and *implement*. It confers no constitutional authority and may not *define* what a declared criterion is |

**This corrects the root determination.** `AG-1` was recorded as *"Repository Intelligence, read from the register's `governed_by` chain, **not assigned**."* Measured: it **is** assigned — `role: AUTHORITY`, declared home, bounded question naming conflict detection. It was assigned in the constitutional authority alignment register rather than in the mutation register, which is why a search of the latter alone found only a chain mention.

### 2.4 Engineering owner

| Field | Measured |
|---|---|
| **Authority source** | Same as §2.3 — engineering execution *is* Repository Intelligence's declared standing |
| Responsibility | Write the shared helper, both checks dicts, the R-09 predicate, the `RULE_PREDICATES` entry, the tests |
| **Decision boundary** | May implement **only criteria the register already declares**. `Q-1` and `Q-2` define *what the criterion is* and therefore fall outside engineering execution |
| Caveat | `P0-DECLARATION-001`: `platform/repository_intelligence` *"is not a governed package… falls outside the scope of UFC-14, UFC-15 and UFC-16 entirely."* The **package** is ungoverned even though the **authority** is vested — two different statements, both true |

### 2.5 Constitutional authority

| Field | Measured |
|---|---|
| **Authority source** | `UCKP-LAW-0001`, `engine/uckp/law.py`, `role: SUPREME`, `may_hold_authority: true`, `cardinality: EXACTLY_ONE`. Separately, `00-CMG/CMG-REGISTRY.json` tier `T1 "Constitutional Authority" occupancy: VACANT, vacancy: VAC-01` |
| Responsibility | The root law and its articles. Amendment of articles, invariants or stop conditions |
| **Decision boundary** | `extension_rule.how_to_extend`: *"A new vocabulary member, relationship class, adapter or authority role is one appended entry in DATA. **`engine/uckp/law.py` is never amended to fit the data (UCKP-ART-17)**"* |
| **Engaged by Option A?** | **NO** — §4.5 |

---

## 3. Existing Authority Evidence

**Every statement in this section is a measurement or a verbatim quotation. Where the record is silent, that silence is reported as silence.**

### 3.1 What was searched

| Surface | Result |
|---|---|
| `mutation-governance-boundary.json` `authorities` | **8 entries, all mechanisms.** No party. No "owner" role |
| `mutation-governance-boundary.json` `mutation_classes[*].governed_by` | 9 chains. **3 resolve to an owner-parameterised placeholder** read off the subject (`GOVERNED_DECLARATION`, `AUTHORED_DOCUMENT`, `GOVERNED_ANALYSIS`) |
| `constitutional-authority-alignment.json` `subordinate_instruments` | `[8]` = `UCOS-MUTATION-GOVERNANCE-BOUNDARY-001`, role EXECUTION, relation PROJECTION, **owns "which mutation classes exist"** |
| `constitutional-authority-alignment.json` `authority_roles` | 8 roles. **`may_hold_authority` appears 8 times; `true` exactly once — SUPREME** |
| `constitutional-authority-alignment.json` `extension_rule` | `how_to_extend` — four numbered mechanisms; item 2 governs DATA appends |
| `constitutional-authority-alignment.json` `non_goals` | *"Creating an authority. This binding confers none, ratifies nothing and occupies no tier."* · *"**Deciding a conflict between two located instruments.** Where one is found, it is measured and reported, **never disposed of here**"* |
| `constitutional-authority-alignment.json` `invariants` | `CAA-INV-01`…`CAA-INV-08` |
| `engine/uckp/law.py` `UCKP-ART-10` | *"Every execution technology satisfies one identical constitutional contract. **Execution never owns knowledge.**"* |
| `engine/uckp/law.py` `UCKP-ART-16` | *"Every governance decision is discoverable, replayable, deterministic, auditable, traceable, machine-verifiable and human-understandable."* |
| `platform/repository_intelligence/contracts.py:64` | `REPOSITORY_INTELLIGENCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` |
| `00-CMG/CMG-REGISTRY.json` | `T1` VACANT, `VAC-01 located: false`; `T0`, `T1M`, `T2`, `T2I`, `T3`, `T4`, `T5` all LOCATED |
| Term frequency, both registers | `"mutation governance owner"` → **0** · **0** |
| Decision packages for `AG-2b` | **NONE FOUND** |
| Ratification records | `constitutional-authority-alignment.json` carries **0** matches for `ratif` |

### 3.2 Is the authority already vested? — the three-part answer

**The question decomposes, and the parts have different answers. Conflating them is what produced the `LOCATED` mis-attribution.**

| Act | Vested? | Evidence |
|---|---|---|
| **(a) Own the content** — hold "which mutation classes exist and which authority disposes of each" | **YES, in the instrument** | `subordinate_instruments[8].owns`, verbatim |
| **(b) Decide** — exercise judgement over what a class's criteria are | **NO PARTY DECLARED** | `"mutation governance owner"` → 0 occurrences. The instrument's roles EXECUTION and PROJECTION both carry `may_hold_authority: false` |
| **(c) Implement** — write a predicate evaluating declared criteria | **YES, in Repository Intelligence** | `role: AUTHORITY`, home declared, bounded question includes *"what conflicts"*, `authority_claim: ENGINEERING-EXECUTION-ONLY` |

**So `AG-2b` was mis-specified.** It was recorded as one decision by one located party. Measured, it is:

```
(a) OWNED      by an instrument that may hold no authority     ← records, cannot decide
(b) UNDECLARED no party holds the deciding role                ← the actual gap
(c) VESTED     in Repository Intelligence, engineering-only    ← can implement, not define
```

### 3.3 Is only execution ownership missing?

**No — the inverse. Execution ownership is the part that is present.**

| | Status |
|---|---|
| Execution ownership | **PRESENT** — Repository Intelligence, `role: AUTHORITY`, `ENGINEERING-EXECUTION-ONLY` |
| Content ownership | **PRESENT** — the instrument, per `subordinate_instruments[8].owns` |
| **Deciding party** | **ABSENT** — no declared role, no named party, no decision record |

**The gap is narrower than "no authority" and different from "no engineer".** What is missing is a declared party competent to answer `Q-1` and `Q-2` — to say what the `analysis-artifact` criterion *means*. Everything needed to record and implement that answer exists.

### 3.4 Is ratification required?

**NO. Measured on four independent grounds.**

| # | Ground | Evidence |
|---|---|---|
| 1 | The instrument's roles cannot hold authority, so there is no authority to ratify | `authority_roles.EXECUTION.may_hold_authority: false`; `.PROJECTION.may_hold_authority: false` |
| 2 | The alignment binding *"confers none, ratifies nothing and occupies no tier"* | `non_goals[0]`, verbatim |
| 3 | Extension is **by registration in DATA**, explicitly not by amendment of law | `extension_rule.how_to_extend[1]`: *"A new vocabulary member … is one appended entry in DATA. `engine/uckp/law.py` is never amended to fit the data (`UCKP-ART-17`)"* |
| 4 | The register declares of itself that it *"does not create a new authority and governs nothing itself"* | `mutation-governance-boundary.json` `authority` field |

**And a consequence that matters for the vacant tier:** because no ratification is required, Option A does **not** route through `T1`. The `VAC-01` vacancy — which caps every verdict in this repository at `CERTIFIED-PROVISIONAL` and blocks `CA-11` and `CA-12` outright — **is not in Option A's path.**

### 3.5 One inconsistency found while searching

`mutation-governance-boundary.json` `invariants[3]`: *"Every named authority resolves to an implementation that exists in the tree."*

Repository Intelligence is **named** in `GOVERNED_ANALYSIS`'s `governed_by` chain and is **absent from the register's own `authorities` array** — so within that register it resolves to no `implementation`, no `governs`, no `does_not_govern`, no `enforcement`.

It **does** resolve, in a different register (`constitutional-authority-alignment.json:610`, home `platform/repository_intelligence/`, which exists). So the invariant is **satisfiable but not satisfied locally** — the register names an authority it does not bind. Recorded as a finding; its disposition is not this determination's to make.

---

## 4. Decision Questions

### 4.1 Q1 — Is narrowing R-08 within existing mutation governance authority?

> **PARTIALLY — and the boundary falls precisely between two acts.**

| Act | Within existing authority? | Evidence |
|---|---|---|
| **Recording** a sixth criterion on `mutation_classes[7]` | **YES** | `subordinate_instruments[8].owns` — the instrument owns "which mutation classes exist and which authority disposes of each". A criterion list is that content |
| **Implementing** the predicate from declared criteria | **YES** | Repository Intelligence, `role: AUTHORITY`, `ENGINEERING-EXECUTION-ONLY` |
| **Deciding what `analysis-artifact` means** (`Q-1` case, `Q-2` scope) | **NO** | No declared party. An engineering-execution-only authority may implement a declared criterion; defining one is not execution |

**One textual gap, disclosed rather than resolved.** `extension_rule.how_to_extend[1]` authorises *"a **new** vocabulary member, relationship class, adapter or authority role"* as one appended DATA entry. Option A **narrows an existing** class rather than appending a new one. Whether narrowing is "extension by registration" or "amendment of a declared member" is **not settled by the text**, and this determination does not settle it by reading. It is recorded as condition 3 in §9.2.

### 4.2 Q2 — Does Option A modify constitutional semantics?

> **NO.**

| Constitutional surface | Touched? |
|---|---|
| `engine/uckp/law.py` — 20 articles, 17 invariants, 13 stop conditions | **NO** — `UCKP-ART-17` forbids amending law to fit data, and Option A does not |
| `authority_roles` — 8 roles | **NO** |
| `CAA-INV-01`…`CAA-INV-08` | **NO** — none quantifies over mutation classes |
| `subordinate_instruments` — the instrument's role, relation, `derives_under`, `owns` | **NO** — all four unchanged |
| The register's four declared `properties` | **NO** — and three of them (`unique`, `total`, `invariants[7]`) move from violated to satisfied |
| `mutation_classes[8]` `GOVERNED_ANALYSIS` | **NO** — R-09's declaration is untouched |
| Precedence `1…9` | **NO** |

**What changes is one criterion in one class's membership list, inside an `EXECUTION`/`PROJECTION` instrument that `may_hold_authority: false`.** That is repository reality, not law. `authority_roles.PROJECTION` states the distinction: such an instrument *"may state repository reality and may never state law."*

### 4.3 Q3 — Does Option A change identity authority?

> **NO. Structurally impossible.**

| Ground | Evidence |
|---|---|
| Mutation classification reads `repo.tracked`, `repo.generated`, `repo.producer_homes` and file text. It writes nothing | `mutation_classification.py:250-424` |
| No ledger file is read or written | `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · `category_seq` 200 keys — unchanged and unreachable |
| `CAA-INV-04` — *"One append-only mint holds every repository identity"* — does not quantify over mutation classes | `constitutional-authority-alignment.json` `invariants` |
| Class 8 states it explicitly | *"Class 8 defines WHO MAY MUTATE a governed analysis artifact and nothing else. It grants no certification authority, no ratification authority and no freeze authority"* |
| No coupling to `RC-3` | No `00-BOOK/DATA/` ledger is involved |

### 4.4 Q4 — Does Option A require certification owner approval?

> **NO for the change. The reclassification is a separate question.**

| Item | Assessment |
|---|---|
| Does any certification artifact reference mutation class? | **NO — measured.** `07-CERTIFICATION.json`, `00-BOOK/DATA/certification.json`, the `UNAF-001` freeze record: none references mutation class |
| Blast radius | **4 files** reference the classifier — two implementation modules, two test modules. **No gate, workflow, engine or `verify.sh` stage** |
| Does a standing certification lose its basis? | **NO** — so `AG-7` is not engaged |
| Effect on `CA-9`-E / `W1-5` | **Positive.** Edge `E-04` requires a certification act to be classifiable; Option A makes 92 analysis artifacts classifiable |
| Residual | The **92-subject reclassification** changes which authority may mutate 92 artifacts. That is `EX-017` migration, distinct from `EX-016` evaluation by the register's own statement, and it is `Q-5` |

### 4.5 Q5 — Does Option A require Article-level authority?

> **NO. Measured on five grounds, and this is the determination's most consequential finding after §3.2.**

| # | Ground | Evidence |
|---|---|---|
| 1 | No article, invariant or stop condition is added or amended | `engine/uckp/law.py` untouched |
| 2 | Extension is **by registration**, which is the declared alternative to article amendment | `UCKP-ART-17`; `extension_rule.how_to_extend[1]` |
| 3 | The instrument's roles cannot hold authority, so no authority is created or transferred | `may_hold_authority: false` for both EXECUTION and PROJECTION |
| 4 | The alignment binding *"ratifies nothing and occupies no tier"* | `non_goals[0]` |
| 5 | `UCKP-ART-18` is **satisfied, not strained** — Option A reuses the register's own twice-used negative-criterion pattern (`non-generated` excludes R-04; `non-executable` excludes R-07) rather than creating a competing mechanism | `extension_rule.how_to_extend[3]`: *"Before creating anything, its canonical object is located and reused, extended or referenced"* |

**Contrast, which is why Option A was recommended over D and E.** Option E would amend the declared `properties` and make `invariants[1]` ambiguous under layered authority chains — plausibly engaging `UCOS-CAA-001` and through it `T1`, which is **VACANT**. Option D changes `classify()`'s resolution algorithm, adding a second mechanism beside precedence, which is the shape `UCKP-ART-18` refuses.

**Option A is the only analysed resolution that does not risk routing a nine-rule predicate defect into the one vacant tier in an eight-tier structure.**

---

## 5. Option A Authorization Assessment

### 5.1 The assessment

> **REQUIRE ADDITIONAL AUTHORITY — narrowly, and not the authority previously supposed.**
>
> Option A is **not rejected**: no constitutional bar exists, the content owner is declared, the implementing authority is vested, no ratification is required, and the vacant tier is not in its path. Option A is **not approved**: two criterion-defining questions (`Q-1`, `Q-2`) sit outside every vested authority's boundary, and one textual question about whether narrowing counts as extension-by-registration is unsettled.

### 5.2 Evidence for each disposition

| Disposition | Evidence for | Evidence against |
|---|---|---|
| **Approve** | Content ownership declared (`subordinate_instruments[8].owns`) · implementing authority vested (`REPOSITORY-INTELLIGENCE`, role AUTHORITY) · no ratification required (4 grounds, §3.4) · no article amendment (5 grounds, §4.5) · satisfies `unique`, `total`, `invariants[6]`, `invariants[7]` — three for the first time · uses the register's own twice-demonstrated pattern · arithmetic conserved 439 = 347 + 92 · zero certification/identity/ownership coupling · rollback crosses no authority boundary | `Q-1` undeclared — R-09's population is 92 or 1, and an engineering-only authority may not choose · `Q-2` undeclared — edge case `E-12` unresolved · `how_to_extend[1]` names *appending new* members, not narrowing existing ones |
| **Reject** | — | Nothing found. **No constitutional bar, no invariant violated by Option A, no authority claim exceeded, no tier engaged.** The measured position is the opposite: three declared properties currently violated become satisfied |
| **Require additional authority** | `Q-1` and `Q-2` define what a criterion *is*; Repository Intelligence's `ENGINEERING-EXECUTION-ONLY` claim and its *"confers no constitutional authority"* docstring exclude that act · no party holds the deciding role (§3.2b) · the `how_to_extend` textual gap · `Q-5`'s 92-subject reclassification touches owner-parameterised `governed_by` values, which is the `RC-2` defect | The required authority is **small, non-constitutional, and needs no ratification** — it is a declaration act on an `EXECUTION`-role instrument |

### 5.3 What the required authority actually is

**Not a ratifier. Not a constitutional authority. Not `T1`.** What is required is a **declared party competent to state what the `analysis-artifact` criterion means** — one sentence fixing case handling and match scope — after which the instrument records it and Repository Intelligence implements it, both within vested authority.

**This is a vesting act, not a ratification act.** It is the same shape the root determination identified for `AG-3` and `AG-4`: *"vesting problems, not ratification problems — they need a located corpus authority and a located mutation-governance owner, both of which the register already names."* **Measured here, the register does *not* name a mutation-governance owner.** That correction makes `AG-2b` a *smaller* problem than `AG-3`/`AG-4` in substance — one criterion definition, not a cross-authority map — and a *differently-shaped* one: the role must be declared before it can be filled.

---

## 6. Governance Impact

| Domain | Impact | Evidence |
|---|---|---|
| **Mutation governance** | **Repairs it.** `classify()` returns `ERROR` for every subject today, so mutation governance is uniformly unavailable. Option A restores resolution for all nine classes and eliminates the sole predicate overlap in the rule set | `validate_rule_coverage()`; §2.5 of the readiness determination |
| **Classification authority** | Unchanged in structure; **corrected in effect.** Each class keeps its own `governed_by` chain. 92 subjects move from Class 7's chain to Class 8's — the correction, not a side effect | `mutation_classes[7]`, `[8]` `governed_by` |
| | **Residual:** both chains are **owner-parameterised** — *"the authority the artifact declares of itself"* — so the 92 subjects move from one placeholder to another. **`RC-2` is untouched and `CA-4` is unaffected** | §3.1 |
| **Ownership** | **NONE.** `assignments` remains `{}`. Mutation class is *who may mutate*; ownership is *who owns*. Class 8 disclaims ownership authority explicitly | Class 8 `grants_only_mutation_ownership` |
| **Identity** | **NONE.** Structurally unreachable — classification writes nothing and touches no ledger | §4.3 |
| **Certification** | **NONE direct; positive indirect.** No certification artifact references mutation class; `W1-5`'s basis improves via `E-04` | §4.4 |
| **Verification gates** | **Two effects.** (i) No existing gate consumes mutation class, so no gate changes behaviour. (ii) An `EX-018`-style gate running `classify_all` and failing on `UNRESOLVED`/`ERROR` **does not exist**, and creating one requires declaring `OBSERVE`/`TRANSACT` — the open `S-1` decision. **`RC-4` reaches into this scope** | `Makefile`, `verify.sh`, `.github/workflows/` all carry no classification consumer; `AG-2` |
| **The vacant tier** | **NOT ENGAGED.** No ratification, no article amendment, no tier occupancy. `VAC-01` is not in Option A's path | §3.4, §4.5 |

---

## 7. Implementation Authorization Boundary

**Stated conditionally. This determination authorizes nothing; §9 sets the conditions under which the boundary below would apply.**

### 7.1 Allowed — files

| File | Permitted change | Current git state |
|---|---|---|
| `platform/repository_intelligence/mutation_classification.py` | Add `_analysis_artifact`, add `governed_analysis_checks`, add `_r09_governed_analysis`, add one `RULE_PREDICATES` entry, add one key to `authored_document_checks` | tracked, **clean at HEAD** |
| `platform/tests/test_mutation_classification.py` | Add R-09 positive, negative, exclusivity, coverage-guard and permutation tests | tracked, **MODIFIED `+3/−3`** — pre-existing, not owned by this scope |
| `00-BOOK/DATA/mutation-governance-boundary.json` | `mutation_classes[7].membership_criteria` 5 → 6 entries **only** | tracked, **MODIFIED** — pre-existing |

### 7.2 Allowed — functions and predicates

| Item | Constraint |
|---|---|
| `_analysis_artifact(path) -> bool` | **ONE definition, TWO call sites.** The negation in R-08 and the assertion in R-09 must come from this single helper. **Mandatory** — the sole mitigation for the 91-orphan failure mode |
| `governed_analysis_checks(path, repo) -> dict[str, bool]` | Six keys, individually attributable, mirroring Classes 6 and 7 |
| `authored_document_checks` | 5 → **6** keys; `+ "not-analysis-artifact": not _analysis_artifact(path)`. No other key altered |
| `_r09_governed_analysis` | `if subject.kind != PATH: return False` then `all(...)` — mirrors `_r08` exactly |
| `RULE_PREDICATES` | **`+= {"R-09": _r09_governed_analysis}`.** Entries `R-01…R-08` unaltered |
| `R-01`…`R-07` | **Not one line touched** |
| `classify()` | **Not touched** — that is Option D |

### 7.3 Allowed — tests

26 tests as enumerated in the readiness determination §6: `T-1`…`T-7` predicate units · `T-8`…`T-11` overlap, including exhaustive pairwise disjointness and the anti-asymmetry guard · `T-12`…`T-17` regression, including permutation invariance · `T-18`…`T-21` coverage · `T-22`…`T-26` repository-wide. **Every test must be read-only; porcelain byte-compared, not asserted.**

### 7.4 Forbidden

| Surface | Prohibition | Governing rule |
|---|---|---|
| Precedence values | **No change.** `R-01…R-09` stay at `1…9` | `unique` — ordering is never the mechanism; `CA-1` scope |
| `mutation_classes[8]` | **No change.** R-09's declaration is untouched | §2.6 of the readiness determination |
| A tenth class or rule | **Forbidden** | `CA-1` scope |
| **Registry changes** | No write to `id-ledger.json`, `change-ledger.json`, `relationships.json`, `artifacts.json`, `volumes.json`, `control-tower.json`, `generated-artifact-registry.json` | `AG-3` NOT LOCATED |
| **Identity changes** | No `by_path`, `by_object`, `by_observation`, `page_cursor`, `category_seq`, `history` write. **No `register.sh`, in any mode** | *No identity mutation without arbitration*; `AIF-L14`, `AIF-L17` |
| **Ownership changes** | `assignments` stays `{}`. No `UNASSIGNED` fallback. `OwnershipFabricationError` recorded, never suppressed | `R-54`; *no fabricated ownership* |
| **Certification changes** | No write to any certification artifact, including amendment | `AIF-L21` — corrections are new events in a distinct store |
| `constitutional-authority-alignment.json` | **No change.** The instrument's `role`, `relation`, `derives_under`, `owns` all stay | `AG-5`; `non_goals` |
| `engine/uckp/law.py` | **No change** | `UCKP-ART-17` |
| The 92-subject reclassification (`EX-017`) | **Not performed.** `EX-016` evaluation only | `Q-5`; register's own `$conformance_is_not_claimed_here` |
| Commit | **Forbidden** in this scope | Directive; no clean baseline exists |

### 7.5 Rollback boundary

```
SCOPE — three files, no governed surface

METHOD — pre-save and restore, NOT git checkout
  1  Copy all three working-tree files out of tree before the change; record sha256
  2  Rollback = restore the saved copies byte-for-byte; verify sha256
  3  ▓ NEVER `git checkout --` — two of three carry pre-existing uncommitted diffs
       this scope does not own ▓
  4  ▓ NEVER git stash · git clean · git reset · git restore --staged ▓
       git clean would delete the 228 untracked registrations irreversibly, and
       category_seq does not roll back, so re-minting issues DIFFERENT identifiers

PROPERTIES
  ✅ total and reversible — three source files
  ✅ crosses NO authority boundary — no ledger, certification, ownership or identity
  ✅ independent of AG-3 — no ledger file involved
  ✅ no transaction boundary needed — no shared JSON counter object is written
  ⚠️ mutation-governance-boundary.json is registry-ADJACENT: it lives in 00-BOOK/DATA/
      but is not one of the seven ledgers and is not a corpus register under R-03
      (R-03 covers id-ledger.json and artifacts.json only)

PRESERVED THROUGH ROLLBACK — AIF-L17: a correction is a new event, never a deletion
  the baseline record · the full reverted diff · every gate result including failures ·
  the trigger and detecting gate, timestamped · the post-rollback sha256 set

NO ROLLBACK EXISTS for an identity mutation — RC-7. That is why nothing here writes identity.
```

---

## 8. Wave Impact Update

### 8.1 Wave 0 — `CA-1` status

| Field | Before | After |
|---|---|---|
| `W0-1` / `CA-1` | IMPLEMENTABLE, NOT ACCEPTABLE | **IMPLEMENTABLE, NOT ACCEPTABLE — authority structure now measured** |
| Conditions | 7, six attributed to "the mutation governance owner" | **4** — see §9.2. Three discharged by measurement |
| Discharged | — | **Constitutional authority NOT required** (5 grounds) · **ratification NOT required** (4 grounds) · **`Q-3` reassigned to engineering** (a code-location question inside `ENGINEERING-EXECUTION-ONLY`) · **`Q-4` reassigned to the instrument** (correcting a false `$`-prefixed descriptive note is recording repository reality, which PROJECTION may do) |
| Newly precise | The gap is **not an absent owner of an existing role** — it is an **undeclared role**. `"mutation governance owner"` occurs 0 times in either register |
| Wave 0 total | 6 of 7 READY | **6 of 7 READY — unchanged** |

### 8.2 Wave 1 — `W1-1` status

| Field | Before | After |
|---|---|---|
| Status | CONDITIONALLY READY | **CONDITIONALLY READY** |
| Conditions | 7 | **4** |
| Nature of remaining conditions | "decisions by a located owner" | **2 criterion definitions (`Q-1`, `Q-2`) · 1 textual gap in `how_to_extend` · 1 deferrable migration (`Q-5`)** |
| Constitutional exposure | assessed NONE | **measured NONE** — 5 grounds |
| Blocking party | "mutation governance owner" | **A role that must be declared before it can be filled** |

**`W1-1` cannot advance past `CONDITIONALLY READY` by analysis.** Four determinations have now examined it; each narrowed the gap and none closed it, because the residue is a declaration act.

### 8.3 Wave 2 — dependency impact

| Edge | Impact |
|---|---|
| `E-02` `RC-1 → RC-2` | ✅ Nine resolvable classes let `W0-4` draft `A(C)` total over the vocabulary. **`AG-4` untouched** |
| `E-03` `RC-1 → RC-8` | ✅ 92 analysis subjects become classifiable for `CA-8`-E's partition. **No assignment authorised** |
| `E-04` `RC-1 → RC-9` | ✅ `W1-5`'s basis improves |
| `E-05` `RC-4 → RC-9` | ⬜ Unaffected — `AG-2` |
| `CA-3`, `CA-4` | ⬜ **Wave 2 remains BLOCKED on `AG-3` and `AG-4`.** Option A discharges neither |

**One negative finding worth stating:** the 92 subjects move from one owner-parameterised `governed_by` placeholder to another. Option A corrects *which class* governs them; it does not make either class resolve to a named authority. **`RC-2` is entirely untouched.**

### 8.4 Critical path impact

```
RC-4 ──▶ RC-3 ──▶ {RC-5, RC-7} ──▶ ARB ──▶ READY
          ▲
          └── AG-3 NOT LOCATED — still binding at node 2 of 5

RC-1 ──▶ {RC-2, RC-8, RC-9} ──▶ …        ← parallel branch; AG-2b sits here
```

**Unchanged.** `AG-2b` gates three downstream actions (`CA-4`, `CA-8`, `CA-9`) via `RC-1`'s fan-out — the highest in the graph, 5 of 12 nodes — and gates **nothing** on the critical path.

**High-leverage and non-urgent.** One further property, newly measured: `AG-2b` is the only substantive blocker in the programme whose resolution requires **no ratification, no article amendment, and no engagement with the vacant `T1`**. Every other authority gap in the register either terminates in `T1` or in an unlocated ratifier.

---

## 9. Final Determination

> # CONDITIONALLY AUTHORIZED
>
> **Option A has valid authority for both of its constituent acts. Recording a sixth criterion on `mutation_classes[7]` falls inside `UCOS-MUTATION-GOVERNANCE-BOUNDARY-001`'s declared ownership of *"which mutation classes exist and which authority disposes of each"*. Implementing the predicate falls inside `REPOSITORY-INTELLIGENCE`'s vested `role: AUTHORITY` with its `ENGINEERING-EXECUTION-ONLY` claim. No ratification is required on four measured grounds, no Article-level authority on five, and the vacant `T1` tier is not in Option A's path. What is missing is narrower than previously recorded and differently shaped: `AG-2b` names a "mutation governance owner" that occurs zero times in either governance register, so the gap is an undeclared role rather than an unfilled one. Two questions — case handling and match scope for the `analysis-artifact` criterion — define what the criterion *is*, and an engineering-execution-only authority that "confers no constitutional authority" may implement a declared criterion but not define one. Four conditions remain. Implementation is not performed and no execution is claimed.**

### 9.1 Why `CONDITIONALLY AUTHORIZED`

| Verdict | Assessment |
|---|---|
| `AUTHORIZED FOR IMPLEMENTATION` | **Rejected.** `Q-1` leaves R-09's population undetermined between 92 and 1; `Q-2` leaves edge case `E-12` open. Both define the criterion, and no vested authority may define it. Implementing would repeat the defect's own cause — a declaration extended by a party competent only to implement it |
| **`CONDITIONALLY AUTHORIZED`** | **Adopted.** Both required authorities are **vested and measured**, not inferred. No constitutional bar exists, and none was found on any of five grounds. Three of the seven prior conditions are discharged by measurement. The four residual conditions are finite, non-constitutional, and do not touch the vacant tier |
| `NOT AUTHORIZED` | **Rejected as unsupported.** It would require a constitutional bar, an exceeded authority claim, or a violated invariant. **None was found.** The measured position is the reverse: Option A moves three currently-violated declared properties into satisfaction |

### 9.2 The four remaining conditions

| # | Condition | Authority needed | Status |
|---|---|---|---|
| 1 | **`Q-1`** — case handling for the nine tokens declared. Decides 92 subjects or 1 | A party competent to define a criterion. **ROLE UNDECLARED** | **OPEN** |
| 2 | **`Q-2`** — match scope: filename only, or full path. Edge case `E-12` | Same | **OPEN** |
| 3 | **`how_to_extend` scope** — whether narrowing an existing class is "extension by registration" under `UCKP-ART-17`, or amendment of a declared member. The text authorises *appending new* members and is silent on narrowing existing ones | Same, or the alignment binding's maintainer. Note `non_goals`: the binding *"never disposes of"* a conflict | **OPEN — textual gap, disclosed not resolved** |
| 4 | **`Q-5`** — the 92-subject `EX-017` reclassification | Class 7 and Class 8 chains, both **owner-parameterised** — the `RC-2` defect; may reach `AG-4` | **DEFERRABLE** — `EX-016` and `EX-017` are distinct acts by the register's own statement |

**Condition 4 is separable: the predicate may be corrected, clearing the repository-wide `ERROR` outage, with the reclassification explicitly deferred.**

### 9.3 Discharged by measurement in this determination

| Previously | Now |
|---|---|
| "Constitutional authority may be required" | **NOT REQUIRED — 5 grounds** (§4.5) |
| "Ratification status unknown" | **NOT REQUIRED — 4 grounds** (§3.4) |
| `AG-1` "Repository Intelligence … **not assigned**" | **ASSIGNED** — `constitutional-authority-alignment.json:610`, `role: AUTHORITY`, home declared, bounded question includes *"what conflicts"* |
| `Q-3` extension-module registration path | **ENGINEERING** — where an implementation lives is inside `ENGINEERING-EXECUTION-ONLY` |
| `Q-4` Class 8's false ordering note | **RECORDABLE BY THE INSTRUMENT** — correcting a false `$`-prefixed descriptive note is stating repository reality, which `PROJECTION` may do; it *"may never state law"*, and this is not law |
| `AG-2b` "LOCATED, OPEN" | **MIS-SPECIFIED.** Content ownership vested in the instrument; implementation vested in Repository Intelligence; **the deciding role is undeclared** — 0 occurrences in either register |

### 9.4 What is claimed, and what is not

| Claimed | Not claimed |
|---|---|
| Both required authorities are vested, with citations | That either has been exercised |
| No ratification and no Article-level act is required | That the `how_to_extend` textual gap is resolved |
| The vacant `T1` is not in Option A's path | That `T1`'s vacancy is closed or closeable |
| `"mutation governance owner"` occurs 0 times in either register | That no such party exists outside the repository's records |
| Repository Intelligence is assigned, correcting `AG-1`'s note | That its `ENGINEERING-EXECUTION-ONLY` claim extends to defining a criterion — **it does not** |
| Three prior conditions discharged | That `AG-2b` is discharged. **It is not** |
| `RC-2` is untouched by Option A | A remedy for `RC-2` |
| The register names an authority it does not bind (§3.5) | A disposition for that inconsistency |

**No execution is claimed.** No predicate written, no criterion recorded, no precedence changed, no test run, no artifact reclassified, no root cause closed, no blocker discharged, no authority vested by this artifact. `RC-1` remains OPEN. `AG-2b` remains OPEN. `UCCEP-F-004` caps this determination at `CERTIFIED-PROVISIONAL` and `VAC-01` renders it `PROVISIONAL`.

---

## 10. Verification Record

| Check | Result |
|---|---|
| File exists | ✅ `UCOS-OMEGA-INFINITY-R09-PREDICATE-DECISION-AUTHORIZATION-DETERMINATION.md` |
| Line count | ✅ **525** — measured post-write against the final file; recorded in the session transcript |
| Section count | ✅ **10** `## ` headings — §1 Current Baseline · §2 Decision Authority Identification · §3 Existing Authority Evidence · §4 Decision Questions · §5 Option A Authorization Assessment · §6 Governance Impact · §7 Implementation Authorization Boundary · §8 Wave Impact Update · §9 Final Determination · §10 Verification Record |
| Q1–Q5 resolved explicitly | ✅ all five, each with cited evidence |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Staged changes | ✅ **0** |
| Tracked modifications unchanged | ✅ **38** — identical set to plan start |
| Exactly one new artifact | ✅ porcelain 357 → 358; the single delta is this file |
| Code mutations | ✅ **0** — `mutation_classification.py` read only, byte-identical to HEAD |
| `RULE_PREDICATES` | ✅ **UNCHANGED** — 8 entries, `R-01…R-08` |
| Precedence values | ✅ **UNCHANGED** — `R-01…R-09` at `1…9` |
| Option A implemented | ✅ **NO** |
| `classify()` executed | ✅ **NO** — the engine was not imported |
| State-mutating tests executed | ✅ **NO** — no test executed at all |
| Configuration mutations | ✅ **0** |
| Registry mutations | ✅ **0** — `mutation-governance-boundary.json` and `constitutional-authority-alignment.json` parsed read-only, byte-identical |
| Certification mutations | ✅ **0** |
| Identity mutations | ✅ **0** — `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `page_cursor` 10,840 · `category_seq` 200 keys |
| Ownership mutations | ✅ **0** — `assignments` remains `{}` |
| `register.sh` invocations | ✅ **0** |
| Commits | ✅ **0** |
| Root causes closed | ✅ **0** — `RC-1` OPEN |
| Blockers discharged | ✅ **0** — `AG-2b` OPEN; **3 of its 7 conditions discharged by measurement** |
| Authorities vested | ✅ **0** — two were found **already** vested; this artifact vested none |
| Execution claimed | ✅ **NONE** |

---

*This determination vested no authority and implemented nothing. Asked whether Option A has valid authorization, it searched the repository's authority records rather than reasoning from the prior determinations, and found that the question had been posed against a party that does not exist: `"mutation governance owner"` occurs zero times in the mutation governance register and zero times in the constitutional authority alignment register, and the eight authorities the mutation register does declare are all mechanisms — a gateway, a hook, a script, four engines and `register.sh`. What the records do show is better than the designation they lack. `UCOS-MUTATION-GOVERNANCE-BOUNDARY-001` is bound as a subordinate instrument with `role: EXECUTION`, `relation: PROJECTION`, and it owns, verbatim, "which mutation classes exist and which authority disposes of each" — exactly what Option A changes. `REPOSITORY-INTELLIGENCE` is bound with `role: AUTHORITY` and a bounded question that explicitly includes "what conflicts", which corrects the root determination's note that it was "not assigned". Neither surface requires ratification, because both of the instrument's roles carry `may_hold_authority: false` and the alignment binding "confers none, ratifies nothing and occupies no tier"; and extension is by registration in DATA under `UCKP-ART-17`, never by amending `engine/uckp/law.py`. So the vacant `T1` tier — which caps every verdict in this repository and blocks two closure actions outright — is not in Option A's path, and that property distinguishes A from Options D and E, which would risk routing a nine-rule predicate defect into it. Four conditions remain. Two are criterion definitions that an engineering-execution-only authority conferring no constitutional authority may implement but may not decide. One is a genuine gap in the register's own extension text, which authorises appending new vocabulary members and is silent on narrowing existing ones — disclosed rather than read into. One is a deferrable migration. `AG-2b` is not discharged; it is re-specified, and three of its seven conditions are discharged by measurement. The single repository mutation is the creation of this file.*

**END DETERMINATION — AG-2b RE-SPECIFIED, NOT DISCHARGED · "MUTATION GOVERNANCE OWNER" = 0 OCCURRENCES IN BOTH REGISTERS · CONTENT OWNERSHIP VESTED IN THE INSTRUMENT · IMPLEMENTATION VESTED IN REPOSITORY-INTELLIGENCE · NO RATIFICATION REQUIRED (4 GROUNDS) · NO ARTICLE-LEVEL AUTHORITY REQUIRED (5 GROUNDS) · VACANT T1 NOT IN PATH · 3 OF 7 CONDITIONS DISCHARGED · 4 REMAIN · VERDICT CONDITIONALLY AUTHORIZED · ZERO MUTATIONS PERFORMED · NO EXECUTION CLAIMED · STOPPED AFTER ARTIFACT CREATION.**
