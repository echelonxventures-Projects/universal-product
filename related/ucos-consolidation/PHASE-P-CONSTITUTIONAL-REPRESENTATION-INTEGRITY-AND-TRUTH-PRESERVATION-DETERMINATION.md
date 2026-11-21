# PHASE P — CONSTITUTIONAL REPRESENTATION INTEGRITY & TRUTH-PRESERVATION

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** |
| OBJECTIVE | Determine whether constitutional truth, machine truth, validator truth and determination truth are provably equivalent at HEAD |
| METHOD | Exhaustive enumeration + **executed** gates. Every quantitative claim below was run, not read. |
| BASELINE | `integration/recovery-001` @ `1e3e4ba9` |
| GATES EXECUTED | `cmg-gate.sh` → **exit 0**, `READY-PROVISIONAL`, 0 findings · `ukb.py validate` → **PASSED**, 1579 artifacts · `uga_engine.py gate` → **PASSED**, 30 invariants · `ukb.py eligibility` → 1579 eligible, digest `ce71479a…` |
| CLASSIFICATION | `[F]` · `[I]` · `[A]` · `[GAP]` · `[UNKNOWN]` |
| WHAT THIS DOES | Derives. Proposes no fix, no implementation, no architecture. |

---

## P0 — CORRECTION TO PHASE O (issued first, because it changes the trust answer)

**`[F]` Phase O's `GAP-O-05` — *"No content-hash binding between constitutional text and any projection"* — is WRONG as stated, and the correction is material.**

A SHA-256 content hash of the constitutional texts **does exist at HEAD**, maintained by the registration authority in `00-BOOK/DATA/artifacts.json`, and **every one verified this session is current**:

| Artifact | Registered `content_hash` | Recomputed at HEAD | Match |
|---|---|---|---|
| `CMG-000001` (`.md`) | `9b33335fee3135b2…` | `9b33335fee3135b2…` | **✔** |
| `CMG-REGISTRY.json` | `83fe5ce03b42b874…` | `83fe5ce03b42b874…` | **✔** |
| `CEP-000` | `c1b598b897f22455…` | `c1b598b897f22455…` | **✔** |
| `CEP-002` | `f7ae8766f1fda329…` | `f7ae8766f1fda329…` | **✔** |
| `CEP-006` | `48524217103d2589…` | `48524217103d2589…` | **✔** |

`[F]` Across **all 23** CMG-recognized artifacts that are registered: **0 hash drift**.

`[I]` **The correct statement of the defect is narrower and sharper than Phase O's:** a trust anchor exists, is current, and is gate-enforced — but it is held by a **different authority**, in a **different register**, over a **different universe**, and `cmg_validate.py` never consults it. `GAP-O-05` is restated at P8 as `GAP-P-05`.

`[I]` This correction *raises* the trust boundary Phase O would have reported. It also makes the remaining defects harder to dismiss, because they are no longer "nothing is verified" but "**this** is verified and **that** is not, and nothing reconciles the two."

---

## P1 — TRUTH CHAIN ENUMERATION

### The four truths, as the corpus itself names them

`[F]` `CAA-INV-06` (`engine/uckp/alignment.py`, **PASSING**) declares *"the four truths"* and requires them to *"remain separate truths."* The corpus therefore already asserts non-equivalence as a design property. Phase P measures whether the **mappings between** them preserve content.

### SOURCE → PROJECTION → VALIDATOR → DETERMINATION

```
┌─ CHAIN 1 — META-CONSTITUTIONAL ─────────────────────────────────── COMPLETE ──┐
│ SOURCE      00-CMG/CMG-000001-…md  (2,000+ lines, 86 Articles, v1.2)          │
│ PROJECTION  00-CMG/CMG-REGISTRY.json  (19 collections, AUTHORITY = NONE)      │
│ VALIDATOR   00-CMG/tools/cmg_validate.py  (15 checks, 733 lines)              │
│ GATE        00-CMG/tools/cmg-gate.sh  → verify.sh stage 7                     │
│ CONSUMER    every determination citing READY-PROVISIONAL                      │
│ ⚠ SOURCE→PROJECTION edge is UNVERIFIED on 14 of 19 collections (P2)           │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ CHAIN 2 — REGISTRATION / REPOSITORY TRUTH ─────────────────────── COMPLETE ──┐
│ SOURCE      00-BOOK/CONTROL-TOWER/…REG-AUTO-001-…md                           │
│ PROJECTION  00-BOOK/DATA/artifacts.json (1579) + 6 REGISTRIES/*.md            │
│ VALIDATOR   00-BOOK/tools/ukb.py validate  +  register.sh --guard (drift)     │
│ GATE        .github/workflows/ucos-registration-gate.yml (every push/PR)      │
│ CONSUMER    UGA, UCCEP, URRC, UCAF, verify.sh                                 │
│ ✔ carries sha256 content_hash — the ONLY text-binding anchor in the repo      │
│ ⚠ its own SOURCE is excluded from its own universe (P2 · DIV-P-11)            │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ CHAIN 3 — MACHINE ROOT LAW ────────────────────────────── CIRCULAR (P1.D) ───┐
│ SOURCE      engine/uckp/law.py  ← IS ITSELF CODE; declares UCKP-LAW-0001      │
│ PROJECTION  00-BOOK/DATA/constitutional-authority-alignment.json              │
│ VALIDATOR   engine/uckp/alignment.py (CAA-INV-01…08)                          │
│ GATE        uga_engine.py gate → verify.sh stage 8                            │
│ CONSUMER    every engine that resolves authority                              │
│ ⛔ SOURCE = VALIDATOR's own premise. "Authority derives from itself" (P7)      │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ CHAIN 4 — RATIFICATION ────────────────────────────────────────── PARTIAL ───┐
│ SOURCE      00-CEP/CEP-006-…md                                                │
│ PROJECTION  00-MASTER/UCOS-URAT-001/urat.json (5 records + act digests)       │
│ VALIDATOR   urat_engine.py                                                    │
│ GATE        ✔ has digests · ⚠ NOT in verify.sh stage list                     │
│ CONSUMER    UCCEP-F-004 ceiling                                               │
│ ⚠ CEP-006 states ACCEPTED / FINALIZED have no CMG image (Phase O, DIV-03)     │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ CHAIN 5 — AUTHORITY RECONCILIATION ─────────────────────────────── ORPHAN ───┐
│ SOURCE      01-WORKING/AUTHORITY-REGISTER.md (AUTH-13/14) — UNREGISTERED      │
│ PROJECTION  00-MASTER/UCOS-UCAF-001/ucaf.json                                 │
│ VALIDATOR   ucaf_engine.py                                                    │
│ GATE        ⛔ NONE in verify.sh                                               │
│ CONSUMER    UCAF-RC-01/02/03 → referred, undisposed (Phase O)                 │
└───────────────────────────────────────────────────────────────────────────────┘
```

### P1.A — Complete paths — **2 of 5**

`[F]` Chains 1 and 2 have every link present and a gate in `verify.sh`.

### P1.B — Partial paths — **1**

`[F]` **Chain 4.** Digest-bound and validated, but `urat_engine.py` appears in **no** `verify.sh` stage. `[F]` The **15** `run_stage` invocations are: ruff · prerequisite generation · pytest+coverage · `ukb enforce --pre` · `ukb validate` · **cmg-gate** · **uga** · uaue · evolution-replay · uobc · uisd · ucpa · uvi · coverage report · registration observation. `[I]` Ratification truth is validated on demand, never on the merge path.

### P1.C — Orphan paths — **1, plus 28 gate workflows**

`[F]` **Chain 5** — no gate at any level. `[F]` Additionally, **28** `.github/workflows/*-gate.yml` exist while `verify.sh` runs **15** stages; `[I]` the CI gate set and the local gate set are not the same set, and nothing reconciles them. `[UNKNOWN] UNK-P-01` — whether all 28 CI gates currently pass was not measured (they require CI).

### P1.D — Circular paths — **1, and it is load-bearing**

**`[F]` Chain 3 is a proper circle.** `engine/uckp/law.py` declares `LAW_ID = "UCKP-LAW-0001"` and `SUPREMACY_CLAUSE`. `engine/uckp/alignment.py` then defines role `SUPREME` as *"the root constitutional law; **its authority derives from itself** and every other chain terminates at it"*, and `CAA-INV-01` checks *"Exactly one instrument holds role SUPREME, **it is UCKP-LAW-0001**"* — against `constitutional-authority-alignment.json`, which is generated from the same law module.

`[I]` The validator's premise, subject and standard are one artifact. **No external input can falsify `CAA-INV-01`.** It measured 13 and passed; it would pass over an empty repository.

---

## P2 — CONSTITUTION → PROJECTION FIDELITY

### Exact loss matrix — `CMG-000001` → `CMG-REGISTRY.json`

`[F]` Machine-verified, collection by collection.

| # | Collection | n | Source authority | Derivation mechanism | Lossless? | Information LOST | ADDED | TRANSFORMED |
|---|---|---|---|---|---|---|---|---|
| 1 | `identifier_families` | 11 | `CMG-000001` V.3 | hand-maintained; **verified** vs text (`CMG_MEMBER_RE`) | **YES** | — | — | — |
| 2 | `conformance_map` | 80 | LXXIX.7 | **verified** vs `ARTICLE_RE` + roman ordinal | **YES** | — | — | — |
| 3 | `closing_articles` | 6 | LXXXI–LXXXVI | **verified** | **YES** | — | — | — |
| 4 | `closed_enumerations` | 4 | CMG-INV-09 | invariant **name** checked in text; **members never checked** | **PARTIAL** | member sets | — | — |
| 5 | `namespaces` | 17 | XXXIII | unverified | **NO** | width/status rationale | — | — |
| 6 | `kinds` | 24 | XIII | unverified | **NO** | Kind **definitions** (prose) | — | prose → id |
| 7 | `standings` | 6 | XII | unverified | **NO** | meaning | — | — |
| 8 | `reaches` · `phases` | 5 · 3 | XXIV | unverified | **NO** | XXIV.4's force rule | — | — |
| 9 | **`states`** | 14 | XXV.1 | unverified | **NO** | **the entire "Meaning" column; ALL of XXV.3's located-model mapping** | — | 4-col table → 3-key object |
| 10 | **`transitions`** | 22 | XXVI.1 | unverified | **NO** | **every transition CONDITION** — incl. `CMG-T-07` *"the vacant authority closes and accepts"* | — | 3-col → `{id,from,to}` |
| 11 | `relationship_types` | 16 | XXXIV | unverified | **NO** | semantics | `must_not_persist` flag | — |
| 12 | `tiers` | 8 | XVI.2 | unverified | **NO** (structurally faithful) | Located-status prose; **T0's "non-normative-as-law"** | `subordinate_to` edges | full order → **transitive reduction** |
| 13 | `orthogonal_tier_pairs` | 3 | XVI.4 | unverified | **NO** | XVI.4's jurisdictional rationale | — | — |
| 14 | **`vacancies`** | 1 | XVII.4 | unverified | **NO** | — | **`located: false` as a machine switch** | prose → boolean |
| 15 | `artifacts` | 44 | LXXXII | path existence only | **NO** | — | `tier`, `state`, `standing`, `reach` | — |
| 16 | `concerns` | 61 | LXXXII.2/3 | owner resolution only | **NO** | basis prose | — | — |
| 17 | `gaps` | 9 | LXXVIII.2 | disposition presence only | **NO** | reasons | — | — |
| 18 | **`open_questions`** | 7 | LXXVIII.3 | unverified | **NO** | *"Why this instrument declines to decide"* | **`blocks` string** | prose → **prefix-matched switch** |
| 19 | **`readiness`** | 1 | LXXX.3/LXXX.4 | unverified | **NO** | — | **`declared_ceiling`** | normative clause → **editable field** |

**`[F]` 3 of 19 lossless · 1 partial · 15 lossy. 14 of 19 unverified against text.**

### `[F]` Three additions are not projections of anything — they are new governance primitives

`vacancies[].located`, `open_questions[].blocks`, `readiness.declared_ceiling`. `[I]` No clause of `CMG-000001` mandates any of them; each is a machine construct on which the corpus's headline verdict depends (P4).

### Other projections

| Projection | Source authority | Mechanism | Lossless? | Note |
|---|---|---|---|---|
| `00-BOOK/DATA/artifacts.json` | `REG-AUTO-001` | walk + `sha256()` | **YES** for bytes | ✔ the anchor |
| `00-BOOK/DATA/*.json` (16) | `REG-AUTO-001` | generated | derived | append-only ledger |
| `00-BOOK/REGISTRIES/*.md` (6) | idem | emitted from JSON | derived | `.md` **from** JSON — reverse direction |
| `constitutional-authority-alignment.json` | `engine/uckp/law.py` | generated from code | **circular** | P1.D |
| `urat.json` | `CEP-006` | act digests | digest-bound | not on merge path |
| `ucaf.json`, `uccep-bindings.json`, `urrc.json`, `uga` surfaces | various | generated | derived | |
| `.ucos-verification-evidence/**` | verify.sh | **content-addressed filenames** | ✔ | strong form |

### `[F]` The registration universe and the constitutional corpus are DIFFERENT SETS

`[F]` `EXCLUDE_DIR_PREFIXES` (`00-BOOK/tools/config.py:885`) excludes **`00-MASTER/`** — commented *"the Master Context System is **execution state, not corpus**"* — and **`00-BOOK/CONTROL-TOWER/`**, classified in `NON_ARTIFACT_SCOPE` as *"generated: deterministically re-derivable outputs"*.
`[F]` `INCLUDE_EXTENSIONS = (".md", ".txt", ".docx", ".json")` — **`.py` is structurally ineligible.**

**`[F]` Measured consequence over the 44 artifacts `CMG-000001` recognizes:**

```
registered (sha256-covered) : 23   (52%)   drift: 0
UNREGISTERED (no hash)      : 21   (48%)
   FROZEN      : 11   CONST-01 … CONST-11
   PROVISIONAL : 10   AUTH-INF-001 (T2I), STATUS-001, REG-AUTO-001,
                      UCI-001, GOV-INT-001, AB-001-07, EG-001-01,
                      UMA-001-01, NUCLEUS-001-02, UCKP-LAW-0001
```

`[F]` All 21 exist on disk; all are **git-tracked and not `.gitignore`d** (`git check-ignore` → not ignored). `[F]` Unicode NFC/NFD mismatch excluded as a cause.

**`[I] DIV-P-11` — `REG-AUTO-001`, `AUTH-INF-001` (the T2I Interpretive Authority), `STATUS-001`, `UCI-001` and `GOV-INT-001` are classified by the registration authority as *generated, deterministically re-derivable non-artifacts*, while `CMG-000001` recognizes them as binding constitutional instruments. The registration authority's own governing standard is outside its own universe.**

**`[I] DIV-P-12` — the 11 FROZEN constitutions are classified as *execution state, not corpus*. `CEP-007` immutability over them is unverifiable by any gate, because no hash of them exists anywhere.**

---

## P3 — PROJECTION → VALIDATOR FIDELITY

### VALIDATOR BLIND-SPOT REGISTER — ranked by governance impact

| Rank | Id | Validator | Blind spot | Constitutional clause rendered unreachable | Impact |
|---|---|---|---|---|---|
| **1** | `BS-01` | `cmg_validate.py` | **`check_lifecycle` fires XXVII.3 on POST-EFFECT only.** Executed over all 14 states with `standing=META`: **PRE-EFFECT ×5 → 0 findings**; IN-EFFECT ×5 → 0; POST-EFFECT ×4 → 1 | **XXVII.3** (*"an artifact exercising force **outside the IN-EFFECT phase**"*) and **XXIV.4** (*"An artifact in PRE-EFFECT SHALL NOT be cited as authority"*) — **half of XXVII.3 is unimplemented** | **CRITICAL — live instance, P4** |
| **2** | `BS-02` | `cmg_validate.py` | **No comparison of projected enumeration members to canonical text** on 14 of 19 collections | XIII, XXV.1, **XXVI.1**, XVI.2, XVI.4, XXXIII, XXXIV, LXXVIII.2/3, LXXX.4 | **CRITICAL** |
| **3** | `BS-03` | `cmg_validate.py` | **Text binding is a VERSION string comparison**; zero `hashlib`/`sha256` in the module | XV.3, L.6 — recomputability is asserted, never proven | **CRITICAL** |
| **4** | `BS-04` | `cmg_validate.py` | **`readiness()` reads `declared_ceiling` from the projection**, not from LXXX.4 | **LXXX.4** — the anti-drift ceiling is stored in the drifting file | **CRITICAL** |
| **5** | `BS-05` | `ukb.py` | **`STATUS_KEYWORDS` infers lifecycle status from a status string near the top of a markdown file** (`config.py:944`) | **XXVII.5** — *"A lifecycle state SHALL NOT be inferred from a filename, a directory, a commit, or a **status string alone**"* | **CRITICAL — direct textual violation by the machinery** |
| **6** | `BS-06` | all | **No validator reconciles two registers' records of the same artifact.** XXVII.5 requires irreconcilable inputs to *"produce a finding rather than a guess"* | **XXVII.5** second limb | **CRITICAL — live instance, P4** |
| **7** | `BS-07` | `alignment.py` | **`CAA-INV-01` is unfalsifiable** — premise, subject and standard are one module (P1.D) | `UCKP-ART-01`; and **`CMG-000001` XVII.4 / LXXXI.5** are invisible to it | **CRITICAL** |
| **8** | `BS-08` | `cmg_validate.py` | `check_precedence` compares artifacts **by tier only**; never against a machine-declared authority role | XVI.6, CMG-INV-06 — cannot see the P6 inversion | **HIGH** |
| **9** | `BS-09` | `ukb.py` / `register.sh` | Drift gate covers **only the eligible universe**; 21 of 44 constitutional artifacts are outside it | `CEP-007` XI.2 immutability | **HIGH** |
| **10** | `BS-10` | `cmg_validate.py` | `check_homes` verifies **path existence only** — never that the file at the path is the artifact claimed | LVIII.3, XXXI.8 | **HIGH** |
| **11** | `BS-11` | `cmg_validate.py` | **Transition conditions are absent from the projection**, so no condition can be checked | XXVI.1, XXVI.5 | **MEDIUM** |
| **12** | `BS-12` | verify.sh | **No stage validates ratification (Chain 4) or authority reconciliation (Chain 5)** | `CEP-006` XVI; `CEP-002` Art 23 | **MEDIUM** |

### What each validator reads / ignores / assumes / cannot detect

| | `cmg_validate.py` | `ukb.py validate` | `uga_engine.py gate` | `alignment.py` |
|---|---|---|---|---|
| **Reads** | `CMG-REGISTRY.json`; the `.md` **only** for article headings, `CMG-*` identifiers, invariant-name substrings, `VERSION` | git-tracked `.md/.txt/.docx/.json` minus excludes; hashes bytes | 6,662 objects, 5,083 mutations, 2,470 ancestries | `constitutional-authority-alignment.json` |
| **Ignores** | all prose semantics; 14 of 19 collections' members | `00-MASTER/`, `00-BOOK/CONTROL-TOWER/`, all `.py` | constitutional tier order | everything outside its own binding |
| **Assumes** | the projection is a faithful projection | status strings are truthful (`BS-05`) | UGA's own declaration is the object model | `UCKP-LAW-0001` is supreme (its own premise) |
| **Cannot detect** | text↔projection divergence; PRE-EFFECT force; cross-register conflict | that an excluded file is constitutional law | a five-tier authority inversion | its own circularity |

---

## P4 — VALIDATOR → DETERMINATION FIDELITY

**Question: can a determination be reached while text / projection / registry disagree? `[F]` YES — and it is the state of HEAD.**

### FALSE PASS REGISTER

| Id | Determination reached | What disagrees | Proof |
|---|---|---|---|
| **`FP-01`** | `cmg-gate.sh` **exit 0**, findings **0** | **`CMG-000001` is recorded `state = DECLARED` → phase `PRE-EFFECT`, with `standing = META`, `reach = CORPUS-WIDE`, owning 11 retained concerns, and referenced by 401 files.** XXIV.4: *"An artifact in PRE-EFFECT SHALL NOT be cited as authority."* XXVII.3: a phase-force inconsistency *"**SHALL block certification under Article LXXX**."* | **`[F]` Executed.** `CMG-000001` is the **only** one of 44 artifacts outside IN-EFFECT (32 PROVISIONAL, 11 FROZEN, 1 DECLARED). Findings: **0**. `BS-01` proves the check fires only on POST-EFFECT. |
| **`FP-02`** | `ukb.py validate` **PASSED**, *"referential integrity OK"* | Three registers record three different states/versions for `CMG-000001`: `artifacts.json` → `UNDER_REVIEW` / `1.0.0` · `CMG-REGISTRY.json` → `DECLARED` / `1.2` · text → `VERSION 1.2`, P.6 *"status is PROPOSED"*, LXXXI.6 *"standing IS PROVISIONAL"*. **Four vocabularies, no reconciliation.** XXVII.5 requires a finding. | **`[F]` Executed.** No finding from any gate. |
| **`FP-03`** | `uga_engine.py gate` **PASSED** — `CAA-INV-01 EXACTLY_ONE_SUPREME_CONSTITUTIONAL_AUTHORITY`, violations 0 | The machine's supreme authority is `UCKP-LAW-0001` (`engine/uckp/law.py`), *"authority derives from itself"*. `CMG-REGISTRY.json` records the **same artifact** at **`tier: T4`** (Execution Authority — *"agents and engines acting within a gate"*), `state: PROVISIONAL`, `superiors: ["VAC-01"]`. **T1 is VACANT.** | **`[F]` Executed + proven** at P6. |
| **`FP-04`** | `ukb.py eligibility` — 1579 eligible = 1579 registered, digest `ce71479a…` | 21 of 44 constitutional artifacts — including all 11 FROZEN constitutions and `REG-AUTO-001` itself — are outside that universe by rule | **`[F]` Executed.** |
| **`FP-05`** | `readiness()` → `READY` reachable | Editing **only** `CMG-REGISTRY.json` (`blocks` → `"Nothing"`, `located` → `true`, `declared_ceiling` → `"READY"`) yields **`READY`, 0 findings**, constitutional text untouched | **`[F]` Simulated (Phase O `DIV-04`), re-confirmed.** |

### FALSE FAIL REGISTER

| Id | Determination | Analysis |
|---|---|---|
| **`FF-01`** | `READY-PROVISIONAL` instead of `READY` when `CMG-OQ-03/05/07` remain open | `[F]` `CMG-000007` §5 says two acts suffice; the validator counts five OQs blocking. `[I]` Whether this is a false FAIL or a true one is **undecidable**: `CMG-OQ-03`'s owner is *"an authority above both axes (presently vacant)"*, so no located authority can adjudicate. **`[UNKNOWN] UNK-P-02`.** |
| **`FF-02`** | — | `[F]` **No other false FAIL located.** Every executed gate that passed, passed; no gate blocked on a condition the constitution permits. `[I]` The failure mode of this repository is uniformly **over-permissive, never over-strict.** |

### FALSE READY REGISTER

| Id | Claim | Status |
|---|---|---|
| **`FR-01`** | `READY-PROVISIONAL` (`cmg-gate`) | **`[I]` FALSE-READY.** XXVII.3 requires `FP-01`'s phase-force inconsistency to **block certification under Article LXXX**. The correct outcome is `NOT-READY`. The verdict is reached only because `BS-01` implements half the clause. |
| **`FR-02`** | `CERTIFIED-PROVISIONAL` corpus ceiling | **`[I]` SOUND.** Independently grounded in `CEP-006` I.4 (Phase O, O5). It survives every defect here. |
| **`FR-03`** | `GATE PASSED — no anonymous, unowned, unregistered or unaudited object` (UGA) | **`[I]` FALSE-READY as worded.** True over UGA's universe; 21 constitutional artifacts are unregistered outside it. The sentence is unqualified. |

### Every reachable determination state

`[F]` `{NOT-READY, READY-PROVISIONAL, READY}` (cmg) · `{PASS, FAIL}` (ukb, uga, verify) · `{CERTIFIED-PROVISIONAL}` ceiling · `{PROVISIONAL}` (URAT, all 5 records) · `FINALIZED` — **unreachable**: `CMG-000001` has no such state (Phase O `GAP-O-06`) and `CEP-006` XII.2 gates it on an act not performed.

---

## P5 — CONSTITUTIONAL INFORMATION LOSS ANALYSIS

| Construct | Representation | Where compressed | Evidence |
|---|---|---|---|
| **Authority** | **COLLAPSED** | Three incompatible models: `CMG` tiers T0–T5 · `CEP-000` §5.5 Tier 1–4 · `UCKP` roles SUPREME/PROJECTION/ORTHOGONAL/PERSISTENCE. No mapping exists between the third and the first two | `[F]` P6 |
| **Tier** | **COMPRESSED** (faithful) | Full order → transitive reduction; recoverable by `tier_reachable`. **T0's "non-normative-as-law" is LOST** — the projection makes T1 subordinate to a tier the text says *"does not bind as law"* | `[F]` machine-verified |
| **Concern** | **COMPLETE** | 61 projected with owner + basis + disposition; injectivity enforced (`CMG-INV-02`) | `[F]` |
| **Finding** | **UNREPRESENTABLE in CMG** | `CMG-REGISTRY.json` has **no `findings` collection**. Article LII findings live only in prose (`UCCEP-F-001…010`, `UCAF-F-002/003`) in a different programme's registers | `[F]` |
| **Deferral** | **UNREPRESENTABLE in CMG** | `DEF-01`/`DEF-02` exist only as `00-MASTER/UCCEP-000008/07-DEFERRAL-ENTRIES.md` — **inside the excluded tree**, unregistered, unhashed | `[F]` |
| **Lifecycle State** | **COLLAPSED** | 4-column table (ID/State/Phase/**Meaning**) → `{id,state,phase}`. **XXV.3's entire located-model mapping is absent from the projection** | `[F]` |
| **Governance State** | **AMBIGUOUS** | Four vocabularies for one artifact (`FP-02`) | `[F]` |
| **Ratification State** | **COLLAPSED** | `CEP-006` VI.1 declares **9** states; `XXV.3` maps **3** (PROVISIONAL, RATIFIED/FINALIZED, REJECTED). **6 have no image**: `NOT_ELIGIBLE`, `ELIGIBLE`, `DELIBERATING`, **`ACCEPTED`**, `DEFERRED`, `APPEALING` | `[F]` |
| **Finality State** | **UNREPRESENTABLE** | `FINALIZED` occurs **once** in 2,000+ lines of `CMG-000001` — inside XXV.3 itself. It is not a CMG state | `[F]` |
| **Ownership State** | **COMPLETE** | 50 delegated + 11 retained; `CMG-INV-03`/`INV-12` enforced | `[F]` |

### Special focus — `CMG-000001` XXV.3

**`[F]` The single most consequential compression in the corpus.**

```
XXV.3 :  CMG-S-07  ↔  RATIFIED / FINALIZED          ← 1 meta-state ↦ 2 located states
XXV.5 :  "An artifact SHALL hold exactly one state at any instant"
XXVI.5:  "A transition that leaves the artifact ... in two states, IS a defect"
CEP-006 VI.1: RATIFIED is not a state; FINALIZED is terminal (VI.2)
CEP-006 XII.2: PROVISIONAL → FINALIZED requires a SEPARATE out-of-corpus act
```

`[I]` **`ACCEPTED` is the load-bearing omission.** `XII.2`'s first limb turns on it: an `ACCEPTED` determination may finalize on **in-corpus** authority; a `PROVISIONAL` one may not. Without an image for `ACCEPTED`, the CMG lifecycle **cannot express the distinction that decides whether finality takes one act or two** — which is exactly why Phase O found act-cardinality underivable.

`[F]` XXV.3 carries its own conflict rule — *"Where the located model and this mapping disagree, **the located model governs** and this mapping **SHALL be corrected by amendment**"* — and `[F]` no such amendment exists at HEAD (Phase O `GAP-O-03`).
`[F]` **The projection does not carry XXV.3 at all**, so no validator can ever detect the disagreement.

---

## P6 — GOVERNANCE SOUNDNESS ANALYSIS

### Q1: Can a conclusion be machine-valid but constitutionally-invalid? **`[F]` YES. Three proven instances.**

#### **Proof 1 — `SOUND-01`: the five-tier authority inversion**

| Premise | Source | Status |
|---|---|---|
| P1 | `engine/uckp/law.py:35` — `LAW_ID = "UCKP-LAW-0001"` | `[F]` |
| P2 | `engine/uckp/alignment.py` `AUTHORITY_ROLES` — role `SUPREME` = *"the root constitutional law; **its authority derives from itself** and every other chain terminates at it"*, cardinality `EXACTLY_ONE` | `[F]` |
| P3 | `CAA-INV-01` — *"Exactly one instrument holds role SUPREME, **it is UCKP-LAW-0001**"* → **PASS**, violations 0, measured 13 | `[F]` executed |
| P4 | `CMG-REGISTRY.json` — `UCKP-LAW-0001`: `tier: "T4"`, `standing: FOUNDATIONAL`, `state: PROVISIONAL`, `superiors: ["VAC-01"]` | `[F]` |
| P5 | `CMG-000001` XVI.2 — T4 = **Execution Authority**, *"Agents and engines acting within a gate"*; T1 = **VACANT** | `[F]` |
| P6 | `tier_reachable(T4 → T1M)` = **True**; `tier_reachable(T1M → T4)` = **False** → CMG ranks it **4 hops below** T1 and **below** `CMG-000001` | `[F]` computed |
| P7 | `CMG-000001` XVII.4 — a vacant tier *"SHALL NOT [be skipped] and SHALL NOT promote a lower instrument into it"*; LXXXI.5 — any such reading *"IS erroneous and IS void under CMG-L-13"* | `[F]` |
| P8 | `CEP-000` §5.4 — *"Program Authority SHALL NEVER self-elevate"* | `[F]` |

**`[I]` Conclusion.** `CAA-INV-01` is machine-valid (green gate, zero violations) and constitutionally void: it seats a **T4 execution-tier artifact** as supreme over a tier the constitution records as **VACANT**, on the ground that *"its authority derives from itself"* — the exact act `ROOT-Ω`, `CEP-000` §5.4 and `CMG-000001` LXXXI.6 prohibit. ∎

`[F]` **The corpus already knows.** `UCKP-CMG-AUTHORITY-ALIGNMENT-DETERMINATION.md` records the `SUPREMACY_CLAUSE` as *"unconditional and unscoped, with no reference to CMG, no acknowledgment of Tier T1's vacancy, and no provisional framing"* and calls it *"**the finding future work must actually resolve**"* — **unresolved at HEAD.** `[I]` This is a located, recorded, open conflict, not a novel discovery.

#### **Proof 2 — `SOUND-02`: PRE-EFFECT force**
`[F]` `CMG-000001` is `PRE-EFFECT`, `standing = META`, owns 11 concerns, and is referenced by 401 files across the corpus. `[F]` XXIV.4 forbids citing it as authority; XXVII.3 makes this the *single lifecycle defect this instrument owns* and requires it to **block certification**. `[F]` `cmg-gate` exit 0. `[I]` Machine-valid, constitutionally-invalid. ∎
`[I]` **The dilemma is inescapable in both directions:** if `DECLARED` is correct (consistent with P.6 *"status is PROPOSED"*), then those citations violate XXIV.4; if the citations are correct, the registry state is wrong and XXVII.5 required a finding. **Either horn is a violation; the gate reports neither.**

#### **Proof 3 — `SOUND-03`: constitutional law classified as non-artifact**
`[F]` `NON_ARTIFACT_SCOPE["generated"]` classifies `00-BOOK/CONTROL-TOWER/` as *"deterministically re-derivable outputs"*; `EXCLUDE_DIR_PREFIXES` excludes `00-MASTER/` as *"execution state, not corpus"*. `[F]` These contain `REG-AUTO-001`, `AUTH-INF-001` (**tier T2I**), `STATUS-001`, `UCI-001`, `GOV-INT-001`, and **11 FROZEN constitutions**. `[F]` `ukb validate` PASSES; registration is complete over its universe. `[I]` Machine-valid; constitutionally-invalid, because `CMG-000001` XII.1–XII.4 recognizes all 16 as constitutional artifacts and `CEP-007` XI.2 binds the frozen 11 to immutability that nothing can verify. ∎

### Q2: Can a conclusion be constitutionally-valid but machine-invalid? **`[I]` NO located instance.**

`[F]` Search performed; `FF-02`. `[I]` **The asymmetry is itself the finding:** every located divergence runs in the permissive direction. `[I]` This is structural, not accidental — `CMG-L-08` (*"zero hard coding"*) requires validators to read enumerations **from projections**, so a validator can only ever be as strict as its projection. A projection cannot make a validator stricter than the constitution; it can only make it looser.

---

## P7 — `ROOT-Ω` ANALYSIS

**`ROOT-Ω`: "A corpus cannot self-confer standing."**

### Classification: **`[I]` (A) CONSTITUTIONAL THEOREM — with an independent (B) architectural proof, and one located (C) implementation artifact that CONTRADICTS it.**

**(A) Constitutional theorem — `[I]` YES.** Minimum proof set — **three clauses, irreducible**:

| # | Clause | Role in proof |
|---|---|---|
| 1 | `CMG-000001` **XLIV.7** — *"Self-ratification IS PROHIBITED. No artifact, agent, or program SHALL ratify itself, and **no authority SHALL grant itself ratification competence**."* | Blocks the direct route |
| 2 | `CEP-000` **§5.4** — *"Program Authority SHALL NEVER self-elevate … no CEP agent SHALL grant itself ratification authority."* | Blocks the program route |
| 3 | `CMG-000001` **XVII.4** — a vacant tier may not be skipped, nor a lower instrument promoted into it (voided by **LXXXI.5**) | Blocks the promotion route |

`[I]` **Minimality proof.** Drop 1 → an authority self-grants competence. Drop 2 → the Program elevates itself. Drop 3 → a located instrument is promoted into T1, conferring standing without conferral. Each removal admits a distinct self-conferral route; no two are substitutable. **The set is exactly minimal.** ∎

**(B) Architectural theorem — `[F]` an INDEPENDENT proof exists.**
`02-MASTER/UCOS-Ω∞-CONSTITUENT-AUTHORITY-DETERMINATION-REPORT.md`:
> *"Constituent power is by definition non-derived. Derivation would require: authorization (`AUTH-04`) → from sovereignty (`AUTH-03`) → which cannot be assumed/fabricated (`AUTH-06`) — a **closed circle with no internal seed**. INVARIANT `Ω-010` + `CM-007` make the founding act itself a ratification-requiring structural change… **Derivation is therefore logically foreclosed.**"*

`[I]` This proof uses `AUTH-03/04/06` + `Ω-010` + `CM-007` — **a disjoint clause set** from (A)'s XLIV.7/§5.4/XVII.4. **`ROOT-Ω` is therefore doubly grounded and survives the loss of either instrument.**

**(C) Implementation artifact — `[F]` one exists, and it VIOLATES `ROOT-Ω`.**
`engine/uckp/alignment.py` role `SUPREME`: *"**its authority derives from itself**"* — the literal negation of `ROOT-Ω` — enforced by a **passing** gate (`SOUND-01`).
`[I]` `ROOT-Ω` is not merely unimplemented in the machine layer; **the machine layer implements its contradiction.**

**(D) Current-state observation — `[I]` NO.** It is not contingent on T1 being vacant: XLIV.7 and §5.4 bind unconditionally. `[F]` Corroborated by the corpus's own bound: *"a **missing seed**, not a **contradiction**"* — a theorem about derivability, not a report on present occupancy.

---

## P8 — TRUST BOUNDARY DETERMINATION

| Layer | Trustworthy? | Basis |
|---|---|---|
| **L0 — constitutional text alone** | **`[I]` YES, conditionally** | `[F]` Self-consistent on everything Phase O and P examined **except** XXV.3, which is self-declared defective and carries its own correction mandate. `[I]` Trust is *conditional on reading XXV.3's conflict rule*, which resolves in favour of `CEP-006`. |
| **L0.5 — text + `artifacts.json` sha256** | **`[I]` YES — over 23 of 44 artifacts** | `[F]` 0 drift, verified this session; gate-enforced on every push/PR. `[F]` **Coverage 52%.** |
| **L1 — text + `CMG-REGISTRY.json`** | **`[I]` NO** | `[F]` 14 of 19 collections unverified; 3 invented governance primitives; XXV.3 absent |
| **L2 — text + registry + validator** | **`[I]` NO** | `[F]` `BS-01…04`; `FP-01`, `FP-05` |
| **L3 — full governance stack** | **`[I]` NO** | `[F]` `SOUND-01/02/03`; Chain 3 circular; Chains 4–5 ungated |

### **`[I]` EXACT TRUST BOUNDARY**

> **Constitutional text, plus the SHA-256 content anchor in `00-BOOK/DATA/artifacts.json`, over the 23 of 44 constitutional artifacts that anchor covers.**
>
> **Everything above that line — `CMG-REGISTRY.json`, `cmg_validate.py`, `readiness()`, `CAA-INV-01`, and every determination resting on them — is not provably trustworthy at HEAD.**

### `[I]` MINIMUM TRUST ANCHOR

**One artifact, one field, one gate:** `00-BOOK/DATA/artifacts.json` → `content_hash`, enforced by `register.sh --guard` in `ucos-registration-gate.yml`.

`[F]` It is the **only** mechanism in the repository that binds a constitutional byte-sequence to a verifiable digest on the merge path.
`[I]` It is **not self-anchoring**: its own governing standard (`REG-AUTO-001`) is in `00-BOOK/CONTROL-TOWER/`, which the anchor's own exclusion rule classifies as a *generated non-artifact*. **The anchor is trustworthy for what it covers and cannot vouch for itself.**

`[GAP] GAP-P-05` (restating Phase O `GAP-O-05` correctly): the anchor exists and is sound; **no clause of `CMG-000001` requires the meta-constitutional validator to consult it**, and it does not.

---

## P9 — COUNTEREXAMPLE SEARCH

**Goal: falsify equivalence. `[F]` FALSIFICATION SUCCEEDS — and no construction was required.**

### `[I]` The minimal counterexample is HEAD itself

**`CE-01` — minimal, found not constructed, zero edits:**

```
GIVEN   (all at 1e3e4ba9, all executed this session)
  T1.  CMG-000001 XXIV.4 : "An artifact in PRE-EFFECT SHALL NOT be cited as authority."
  T2.  CMG-000001 XXVII.3: a phase-force inconsistency "SHALL block certification
                           under Article LXXX."
  P1.  CMG-REGISTRY.json : CMG-000001 → state "DECLARED"
  P2.  CMG-REGISTRY.json : states[] → DECLARED has phase "PRE-EFFECT"
  P3.  CMG-REGISTRY.json : CMG-000001 → standing "META", reach "CORPUS-WIDE"
  M1.  401 files reference CMG-000001; 18 cite it in an explicit
       "Authority chain: `CMG-000001` ..." construction
  V1.  cmg_validate.py check_lifecycle tests phase == "POST-EFFECT" only
  D1.  cmg-gate.sh → exit 0 · findings 0 · readiness READY-PROVISIONAL

THEREFORE
  From P1+P2+P3+M1  : a PRE-EFFECT artifact exercises corpus-wide binding force.
  From T1+T2        : that is a phase-force inconsistency and SHALL block certification.
  From V1           : the validator cannot observe it.
  From D1           : certification is not blocked.

  CONSTITUTIONAL TRUTH  says  NOT-READY.
  VALIDATOR TRUTH       says  READY-PROVISIONAL.
                                                                              ∎
```

`[I]` **`CE-01` is minimal**: remove any one of the eight elements and it dissolves. It requires **no hypothetical edit** — it is the committed state.

### The four requested divergence classes

| Class | Constructed? | Instance |
|---|---|---|
| 1. **Constitutional divergence** | `[F]` **FOUND** | XXV.3 vs `CEP-006` VI.1/XII.2 — self-declared, uncorrected (Phase O `GAP-O-03`) |
| 2. **Projection divergence** | `[F]` **FOUND** | `CMG-000001`: `UNDER_REVIEW`/`1.0.0` (artifacts.json) vs `DECLARED`/`1.2` (CMG-REGISTRY) vs `PROPOSED`/`PROVISIONAL`/`1.2` (text) — **and `BS-05` shows the first is *inferred from a status string*, which XXVII.5 forbids** |
| 3. **Validator divergence** | `[F]` **FOUND** | `BS-01` — XXVII.3 implemented on 4 of 14 states |
| 4. **Governance divergence** | `[F]` **FOUND** | `SOUND-01` — `CAA-INV-01` PASSES while seating a T4 artifact above a VACANT T1 on self-derived authority |

`[I]` **All four classes are instantiated at HEAD by committed state. No adversarial construction was needed.**

`[F]` For completeness, the **constructive** counterexample also holds: editing only `CMG-REGISTRY.json` yields `READY` with 0 findings and no change to any constitutional byte (`FP-05`).

---

## P10 — TERMINAL DETERMINATION

| # | Question | Answer |
|---|---|---|
| 1 | **Is constitutional truth preserved?** | **`[I]` PARTIALLY.** The text is self-consistent except XXV.3, which is self-declared defective with an uncorrected mandatory amendment. **Byte-integrity is preserved and verified for 23 of 44 artifacts (52%), 0 drift; unverifiable for the other 21, including all 11 FROZEN constitutions.** |
| 2 | **Is machine truth preserved?** | **`[I]` NO.** 15 of 19 CMG collections are lossy; 14 unverified against text; XXV.3 and every transition condition are absent from the projection; three governance primitives exist only in the machine. |
| 3 | **Is validator truth preserved?** | **`[I]` NO.** 12 blind spots, 7 CRITICAL. `BS-01` implements 4 of 14 states of the one lifecycle clause `CMG-000001` says it owns. |
| 4 | **Is governance truth preserved?** | **`[I]` NO.** `SOUND-01/02/03` — three proven machine-valid / constitutionally-invalid conclusions, all currently green. |
| 5 | **Are all four equivalent?** | **`[F]` NO — disproved by `CE-01`, which needs zero edits.** `[I]` The corpus does not even claim equivalence: `CAA-INV-06` requires the four truths to *"remain separate truths."* What is missing is not equivalence but **a verified morphism** between them. |
| 6 | **Highest trustworthy layer?** | **`[I]` L0.5 — constitutional text + the `artifacts.json` sha256 anchor, over 52% of the constitutional corpus.** |
| 7 | **Minimum trust anchor?** | **`[I]` `00-BOOK/DATA/artifacts.json → content_hash`, enforced by `register.sh --guard`.** One field, one gate. Not self-anchoring. |
| 8 | **Can any prior phase result be accepted without independent constitutional verification?** | **`[I]` NO — and this determination is not exempt.** Every phase, including O and P, consumed `CMG-REGISTRY.json` and gate exit codes, both of which are proven non-equivalent to the text. `[F]` Phase P demonstrated this on itself by falsifying Phase O's `GAP-O-05`. `[I]` **Any prior result is accepted only where it cites constitutional text directly or a hash-covered artifact.** |

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. All five constitutional content hashes checked are **current**; across 23 registered CMG artifacts, **0 drift**.
2. **21 of 44** CMG-recognized artifacts are unregistered and unhashed — **11 FROZEN**, 10 PROVISIONAL.
3. `EXCLUDE_DIR_PREFIXES` excludes `00-MASTER/` (*"execution state, not corpus"*) and `00-BOOK/CONTROL-TOWER/` (*"generated … non-artifact"*); `INCLUDE_EXTENSIONS` excludes `.py`.
4. `REG-AUTO-001`, `AUTH-INF-001` (T2I), `STATUS-001`, `UCI-001`, `GOV-INT-001` are inside excluded trees.
5. All 21 unregistered files exist, are git-tracked, and are not `.gitignore`d; NFC/NFD mismatch excluded.
6. `CMG-000001`: `state=DECLARED` → `PRE-EFFECT`, `standing=META`, `reach=CORPUS-WIDE`, owns 11 concerns; **the only one of 44 outside IN-EFFECT**; referenced by 401 files (18 in explicit `Authority chain:` citations).
7. `check_lifecycle` executed over all 14 states: findings only for the 4 POST-EFFECT states.
8. Four vocabularies for one artifact's state; `ukb.py` **infers** status from a status string (`STATUS_KEYWORDS`), which XXVII.5 forbids.
9. `CAA-INV-01` **PASSES**, declaring `UCKP-LAW-0001` SUPREME, *"authority derives from itself"*.
10. `CMG-REGISTRY.json` records the same artifact at `tier T4`, `PROVISIONAL`, `superiors: ["VAC-01"]`; `tier_reachable(T4→T1M)=True`, reverse `False`.
11. `UCKP-CMG-AUTHORITY-ALIGNMENT-DETERMINATION.md` already records this as *"the finding future work must actually resolve"* — unresolved.
12. `CMG-REGISTRY.json` has **no** `findings` collection; `DEF-01/02` live only in the excluded tree.
13. `CEP-006` VI.1 declares 9 states; XXV.3 maps 3; **`ACCEPTED` unmapped**.
14. `FINALIZED` occurs once in `CMG-000001` — inside XXV.3.
15. `verify.sh` runs **15** stages; **28** `*-gate.yml` workflows exist; URAT and UCAF appear in no stage.
16. Executed: `cmg-gate` exit 0 / 0 findings · `ukb validate` PASSED / 1579 · `uga gate` PASSED / 30 invariants · eligibility 1579 = 1579, digest `ce71479a…`.
17. 3 of 19 CMG collections lossless, 1 partial, **15 lossy**; 14 unverified against text.

### INFERENCES `[I]`
1. Phase O's `GAP-O-05` was wrong; the anchor exists, is current, and is gate-enforced — but is held by another authority over another universe.
2. `CE-01` falsifies four-way equivalence with **zero edits**; the counterexample is the committed state.
3. Every located divergence is **permissive**; no over-strict instance exists. `CMG-L-08` makes this structural — a projection can only loosen a validator, never tighten it.
4. `SOUND-01` is a five-tier inversion effected in code, enforced by a green gate, invisible to `cmg_validate.py`.
5. `FP-01`'s dilemma is inescapable: either those 401 references violate XXIV.4, or the registry state is wrong and XXVII.5 required a finding.
6. `ROOT-Ω` is a constitutional theorem with a **disjoint independent architectural proof**; its minimum proof set is exactly {XLIV.7, §5.4, XVII.4}.
7. The machine layer implements `ROOT-Ω`'s **contradiction**, not merely its absence.
8. `ACCEPTED`'s absence from XXV.3 is why act-cardinality was underivable in Phase O — the same defect, reached from the representation side.
9. The trust anchor cannot vouch for itself: its governing standard is excluded by its own rule.
10. `FR-02` (`CERTIFIED-PROVISIONAL`) is the **one** verdict that survives every defect found, because it rests on `CEP-006` I.4 alone.

### ASSUMPTIONS `[A]`
`[A-P-01]` The 28 CI workflows were not executed; only the 4 local gates were. CI-only divergence unmeasured.
`[A-P-02]` `engine/uckp/law.py` was read as the operative machine law; no runtime import-order or monkey-patching analysis was performed.
`[A-P-03]` Hash verification covered the 44 CMG-recognized artifacts and 5 named constitutions, not all 1579 registered artifacts.
`[A-P-04]` `00-SOURCE/CONSTITUTIONS/*.docx` remain unparsed (`GD-21-C3`), so `SRC-02`'s content is outside every measurement here.
`[A-P-05]` Gate outcomes are taken as this environment's; determinism across environments untested (Phase O `[A-03]`).

### GAPS `[GAP]`
| Id | Gap |
|---|---|
| `GAP-P-01` | XXVII.3 is implemented for POST-EFFECT only; the PRE-EFFECT limb — which has a **live instance** — is unimplemented |
| `GAP-P-02` | No validator reconciles two registers' records of one artifact; XXVII.5's *"finding rather than a guess"* is unenforced |
| `GAP-P-03` | No mapping exists between UCKP authority **roles** and CMG authority **tiers** |
| `GAP-P-04` | `CMG-REGISTRY.json` cannot represent findings or deferrals |
| `GAP-P-05` | No clause requires the meta-constitutional validator to consult the one existing content anchor |
| `GAP-P-06` | 48% of the constitutional corpus is outside every hash-bearing register |
| `GAP-P-07` | `ukb.py` infers lifecycle status from status strings, contrary to XXVII.5 |
| `GAP-P-08` | Chains 4 (ratification) and 5 (authority reconciliation) have no merge-path gate |
| `GAP-P-09` | `CAA-INV-01` is structurally unfalsifiable |

### UNKNOWNS `[UNKNOWN]`
`UNK-P-01` — whether all 28 CI gate workflows pass at HEAD.
`UNK-P-02` — whether `FF-01` is a false FAIL or a true one (undecidable: `CMG-OQ-03`'s owner is vacant).
`UNK-P-03` — whether the 11 FROZEN constitutions have drifted since freeze (**unknowable**: no baseline hash was ever recorded).
`UNK-P-04` — whether `SOUND-01` is a drafting accident in `alignment.py` or a deliberate rival claim (`UCKP-CMG-AUTHORITY-ALIGNMENT` records *"nothing in UCKP's code references CMG, T1, or claims to bind other domains"*, but the clause is unscoped).

---

## PHASE P TERMINAL VERDICT

> **DETERMINATION-COMPLETE · EQUIVALENCE FALSIFIED · TRUST BOUNDARY LOCATED AT L0.5 · COVERAGE 52%**

**One-sentence requirement — does HEAD possess a provably trustworthy constitutional reasoning chain from source text to governance conclusion?**

> **`[I]` NO. HEAD possesses a *verified anchor* and an *unverified chain*. Constitutional bytes are provably intact for 23 of 44 artifacts (0 drift, gate-enforced on every push). Above that anchor, no link is verified: the projection loses 15 of 19 collections, the validator implements 4 of 14 states of the one lifecycle clause it owns, and the machine layer seats a Tier-4 execution artifact as self-deriving supreme authority over a tier the constitution records as vacant — with all four gates green.**

**`[F]` The falsification required no construction.** `CE-01` is the committed state: constitutional truth says `NOT-READY`, validator truth says `READY-PROVISIONAL`, and both are correct within their own layer.

**`[I]` The three results that matter most:**

1. **The defect is not absence of verification — it is a verified anchor wired to nothing.** A correct, current, gate-enforced SHA-256 anchor exists. `cmg_validate.py` has no clause requiring it to look, and does not. Phase O called this "no hash exists"; that was wrong, and the true shape is worse, because the remedy was already present and unused.

2. **Every divergence runs one way.** Not one constitutionally-valid / machine-invalid instance exists. `CMG-L-08` guarantees this: a validator forbidden to hard-code the constitution can only ever be as strict as its projection. **The corpus's central anti-drift principle is also its central drift vector.**

3. **`ROOT-Ω` survives Phase P doubly proved — and is contradicted in code.** Minimum proof set {`XLIV.7`, `CEP-000` §5.4, `XVII.4`}, with a disjoint independent proof at `AUTH-03/04/06` + `Ω-010`. Yet `engine/uckp/alignment.py` defines its supreme role as one whose *"authority derives from itself"*, and a passing gate enforces it. **The machine layer does not merely fail to implement `ROOT-Ω`; it implements its negation.**

**`[I]` And the answer to question 8, which governs everything before it:** no prior phase result — **this one included** — may be accepted without independent constitutional verification, because every phase consumed projections and exit codes now proven non-equivalent to the text. Phase P proved this on itself by falsifying Phase O's `GAP-O-05`. **The correct posture toward every determination in this corpus, including this determination, is: trace it to constitutional text or to a hash-covered artifact, or treat it as unverified.**

**This determination decides nothing.** It proposes no fix, no implementation, no architecture. It records what HEAD entails, what it verifies, and precisely where verification stops.

---

*PHASE P · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`CERTIFIED-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Every quantitative claim was executed at `1e3e4ba9`, not read.*
