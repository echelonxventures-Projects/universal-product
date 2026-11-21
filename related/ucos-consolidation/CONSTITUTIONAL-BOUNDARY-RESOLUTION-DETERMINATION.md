# CONSTITUTIONAL BOUNDARY RESOLUTION DETERMINATION

| Field | Value |
|---|---|
| **ARTIFACT** | `CONSTITUTIONAL-BOUNDARY-RESOLUTION-DETERMINATION.md` |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** Resolves questions against *existing* declared authority. Creates no authority, no capability, no universe, no owner, no registry, no architecture. |
| **CLASSIFICATION** | `EVIDENCE` |
| **BOUNDARY** | `ASSESSMENT-BOUNDARY-DETERMINATION.md` |
| **BASELINE** | HEAD `1f869865` · branch `integration/recovery-001` · `./verify.sh` PASS · 11 302 tests · 97.59 % |
| **METHOD** | Every determination below is measured or read from the declaring artifact. Where the answer is "already determined", the declaring text is quoted. |

---

## 1. UCL Constitutional Artifact Boundary

### Question
Are executable constitutional artifacts (`.py`) canonical constitutional artifacts?

### Determination: **YES — and this was already determined. No change is required.**

Three independent declarations already answer it affirmatively:

| Evidence | Location | Content |
|---|---|---|
| The kind exists in the meta-constitution's own closed taxonomy | `00-CMG/CMG-000001-…-CONSTITUTION.md:396` | `\| CMG-K-14 \| **Engine** \| A realization that executes constitutional rule \| Executable \|` |
| An executable artifact is *recognized* | `00-CMG/CMG-REGISTRY.json` → `artifacts[UCKP-LAW-0001]` | `path: engine/uckp/law.py` · `kind: CMG-K-14` · `standing: FOUNDATIONAL` · `reach: CORPUS-WIDE` · `tier: T4` · `state: PROVISIONAL` |
| Recognition confers constitutional force | `CMG-L-01` | an artifact exercises constitutional force *only while recognized in this registry* — and it is recognized |
| The recognition was a formal amendment | `CMG-000001:2035` (AMD-002) | *"It adds one delegation (CMG-DLG-50) recognizing `engine/uckp/` (`UCKP-LAW-0001`) as the located, already-functioning owner … Version **1.1 → 1.2**"* |
| Its scope is supreme on its own axis | `CMG-000001:2039` | *"`engine/uckp/law.py` (`UCKP-LAW-0001`) governs on the canonical-object axis and this recognition IS void to that extent"* |

**No ownership-model update is performed, because the ownership model already contains the answer.** Performing one would create a second statement of an existing fact, violating the Knowledge Once Principle.

### 1.1 Include boundary: **NO CHANGE. Widening `INCLUDE_EXTENSIONS` is REFUSED.**

The instruction conditioned an include-boundary update on the answer being "yes". The answer is yes, and the boundary change is nevertheless **refused**, because the premise that constitutional recognition requires corpus admission is false. Measured evidence:

**The repository operates three distinct identity planes, by design:**

| Plane | Register | Admits `.py`? | Population | Governing invariant |
|---|---|---|---|---|
| Constitutional recognition | `00-CMG/CMG-REGISTRY.json` | **YES** (CMG-K-14) | 44 artifacts | `CMG-L-01` |
| Universal object identity | `00-BOOK/DATA/id-ledger.json` `by_object` | **YES** | **4611** objects | `CAA-INV-04 EXACTLY_ONE_IDENTITY_AUTHORITY` — **PASS**, measured 5874 |
| Corpus registration / pagination | `00-BOOK/DATA/artifacts.json` via `config.py:942 INCLUDE_EXTENSIONS = ('.md','.txt','.docx','.json')` | **NO** | 1233 artifacts | `ukb.py validate` — **PASS** |

`engine/uckp/law.py` holds universal identity **`UCOS-ENGINE-000496`** (`EXECUTABLE_OBJECT`). `engine/constitution/stages.py` likewise holds one. **`UGA-INV-03 EVERY_OBJECT_REGISTERED` passes with 0 violations over 5844 objects** — no `.py` file is unregistered. It is registered in the executable-object register, not the paginated corpus.

The design intent is stated by the minting authority itself, `00-MASTER/UCOS-UGA-001/uga_engine.py:210-215`: exclusion from corpus registration *"is a statement about which register lists them — never a licence to exist anonymously."*

**Measured blast radius of widening the boundary:**

| Consequence | Measurement |
|---|---|
| Artifacts entering the paginated corpus | **+2027 tracked `.py`** → `artifacts.json` 1233 → ~3260 |
| Page ledger | `page_cursor` 9826 must allocate ranges for 2027 new artifacts; `id-ledger.by_path` 1264 → ~3291 |
| Digital-twin certification | `certification.json` scope (1233 artifacts / 12 899 edges / 1233 lineage nodes) invalidated wholesale |
| Append-only page ledger invariant | `ukb.py validate` currently PASSES on "append-only page ledger intact" — mass repagination is the highest-risk operation available |
| `CK-UCL` | `engine/constitution/stages.py` becomes admissible, so `UCL-V-42` would move 85 → 84 by admission rather than by ratchet |
| Every `.md` classification | `CLASSIFY_RULES` (84 rules) would need `.py` rules; misclassification lands in `OTHER/MISC/VOL-000` per `UMB-004 §6` |

This is **architecture expansion of the corpus boundary**, which the governing instruction forbids. It is also unnecessary: the constitutional question it would answer is already answered on the recognition plane.

### 1.2 UCL regeneration: **NOT REQUIRED on boundary grounds**

`UCL-V-41` / `UCL-V-42` are **ratchets**, not boundary tests. `UCL-F-004` states the mechanism verbatim: *"The bound is a RATCHET held at exactly the measured value, so it is re-tightened whenever governed records are lawfully admitted."*

Delta measured **by identity**, as `UCL-F-004` itself requires:

| Measure | HEAD committed | Measured at pristine HEAD | Working tree | Added | Removed |
|---|---|---|---|---|---|
| `unadmitted_target_artifacts` (`UCL-V-42`) | 84 | **85** | 85 | **1** — `engine/constitution/stages.py` | **0** |
| `relationships_without_target_identity` (`UCL-V-41`) | 217 | **264** | 265 | +47 / +48 | 0 |

Edge decomposition: **45** `evidenced-by` edges from `SRC-MANIFEST::UCL-S-0010…0450` to `engine/constitution/stages.py`, plus 2–3 to `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` (119 → 122 capability facts).

**Cause:** commit `8bad683f "P0-LIFECYCLE-CLOSURE-001: realize all 45 lifecycle stages; close RIB orphan defect"` made that file the evidence target of all 45 stages. `00-MASTER/UCL-000001/ucl-stage-manifest.json` is **unmodified** and already names it 45 times. The ratchet was not re-tightened for the change.

**The added member is the same disclosed condition, not a new one** — verified structurally: it is a `.py` file, `artifacts.json` holds 0 `.py`, and it *does* carry universal identity. It is identical in kind to the 84 already-disclosed members (`engine/certification`, `engine/civilization`, `00-BOOK/tools/ukb.py`, `00-MASTER/UCCEP-000000/uccep_engine.py`, …).

### 1.3 Ratchet validation

| Ratchet | Current `expect` | Correct value | Basis |
|---|---|---|---|
| `UCL-V-41` | 217 | **264** at HEAD · **265** if the staged set is committed | measured; +45 stages, +2–3 catalog |
| `UCL-V-42` | 84 | **85** | measured; exactly 1 added, 0 removed |

**Action: SPECIFIED, NOT APPLIED.** Re-tightening edits `00-MASTER/UCL-000001/ucl-declaration.json` — an authored constitutional declaration — and *widens* a disclosed bound. Two reasons to hold:

1. **The value depends on an undecided input.** 264 vs 265 depends on whether the staged working-tree set is committed (`FINAL-FREEZE-ELIGIBILITY-DETERMINATION.md` §3). Setting the ratchet before that decision would set it wrong.
2. `UCL-F-004`'s precedent (92 → 98 → 217, and 83 → 84) shows each move was recorded as a governed act with the delta measured and the reasoning entered into the finding. This determination supplies the measurement; the act belongs to the owner.

### 1.4 Additional finding — committed derived artifacts that do not reproduce

Discovered by running each engine against a detached `git worktree` of HEAD:

| Artifact | Committed value | Value its own producer reads at the same commit |
|---|---|---|
| `00-MASTER/UCL-000001/ucl.json` | `UCL-V-41: 217`, `UCL-V-42: 84`, **satisfied** | **264 / 85, unsatisfied** |
| `00-MASTER/UIS-001/uis.json` | `UIS-V-14: 74`, **satisfied** | **81, unsatisfied** |

Both record a satisfied state their producer contradicts from identical inputs. Under `ASSESSMENT-BOUNDARY-DETERMINATION.md` §5.1 a generated artifact is current only if regenerated on the snapshot; these are **stale observations recording a passing verdict that no longer holds**. Regenerating them (`make ucl`, `make uis`) would make the failure visible in the committed tree, which is the honest state.

---

## 2. UIS Namespace Ownership Resolution

### Question
Determine the canonical owner of namespaces `CONFIG`, `DATAOBJ`, `ENGINE`, `EXDOC`, `OBS`, `TESTOBJ`, `TOOLING`. Do not assign without authority.

### 2.1 Provenance — measured

All seven are minted by `00-MASTER/UCOS-UGA-001/uga_engine.py`:

```
uga_engine.py:248  ID_CATEGORY = {
                     "EXECUTABLE_OBJECT":    "ENGINE",
                     "TEST_OBJECT":          "TESTOBJ",
                     "CONFIGURATION_OBJECT": "CONFIG",
                     "TOOLING_OBJECT":       "TOOLING",
                     "DATA_OBJECT":          "DATAOBJ",
                     "EXCLUDED_DOCUMENT":    "EXDOC",
                   }
uga_engine.py:484  n = seq.get("OBS", 0) + 1      # observation identities
uga_engine.py:294  uid = f"UCOS-{cat}-{n:06d}"
```

They became **live** (`category_seq[cat] > 0`) when the executable-object universe was identified — 4611 objects, including the 8 minted in the preceding stabilization step (`UCOS-ENGINE-001207/8`, `UCOS-TESTOBJ-000809…814`).

### 2.2 Ownership chain — determined from existing declarations

| Layer | Owner | Declaring text |
|---|---|---|
| **Governing identity authority** | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` (`UCOS-IMP-000024`, AIF) | `UMB-004` AIF conformance: *"exactly **one identity authority**. The AIF **governs**; this Nomenclature Architecture **realizes** it and asserts no parallel or duplicate naming/identity authority."* Realized laws AIF-L04, AIF-L07 |
| **Nomenclature realization / the obligation** | `00-BOOK/MASTER-BOOK/UMB-004-NOMENCLATURE-ARCHITECTURE.md` §5 | *"When a new entity class appears … it receives: a category namespace (append-only), **a classification rule**, an optional chain, a program root, and a volume"* |
| **Declared classification authority (the mechanism UIS measures)** | `00-BOOK/tools/config.py` | `uis-declaration.json.classification_authority.owner = "00-BOOK/tools/config.py"`, `rule_symbol: CLASSIFY_RULES`, anchor *"UMB-004 §3 THE CLASSIFICATION ENGINE (existing, reused)"* |
| **Minting mechanism** | `00-MASTER/UCOS-UGA-001/uga_engine.py` | mints identities; **does not own classification** — `CAA-INV-04` permits exactly one identity authority, which UGA realizes rather than holds |

**Determination: the canonical owner already exists and is not vacant.** Namespace governance is owned by the **AIF (`UCOS-IMP-000024`)**, realized in **`UMB-004` §5**, mechanised in **`00-BOOK/tools/config.py`**. `UCOS-UGA-001` is the minting realization, not the owner. **No assignment is made, because none is needed.**

### 2.3 Why the obligation cannot be discharged as the declaration is currently written

`uis_engine.py:384-407` computes `ungoverned = live_namespaces − declared_namespaces`, where `declared_namespaces` is the union of exactly six symbols in `config.py`:

| Symbol | Current content | Fits an executable-object identity namespace? |
|---|---|---|
| `CLASSIFY_RULES` (index 2) | 84 rules → 37 categories; shape `(path_regex, chain, category, volume)` | **No** — path→category rules for corpus pagination. A rule like `^engine/` would re-categorize the 13 registered `engine/**` `.md` artifacts from `ENG`, causing corpus drift |
| `ARTIFACT_FAMILIES` | 7 families (`APP GOV EXEC ADR ENG PLT DET`), each with `sources` path regexes | **No** — same path-classification semantics |
| `VOLUMES` (index 3) | volume codes | **No** — volumes are corpus pagination units |
| `DERIVED_DEFAULT_CATEGORY` | `"REPO"` | No — single scalar |
| `EXECUTION_CATEGORIES` | `('primitive-behavior','workflow-step','agent-driven','orchestrated')` | **No** — execution *kinds*, not identity namespaces |
| `EXECUTION_DEFAULT_CATEGORY` | `"primitive-behavior"` | No |

**There is no declaration surface in the declared classification authority whose semantics fit an executable-object identity namespace.** Discharging `UIS-V-14` therefore requires one of:

| Option | Action | Assessment |
|---|---|---|
| **(a)** | Add path-regex `CLASSIFY_RULES` / `ARTIFACT_FAMILIES` entries for the 7 | **Semantically wrong and risky** — misuses a corpus-pagination surface and can re-categorize registered `.md` artifacts |
| **(b)** | Add a new namespace-declaration surface to `config.py` and extend `uis-declaration.json.classification_authority` to read it | **Creates governance structure** — forbidden by the governing instruction ("no architecture expansion") |
| **(c)** | Raise `UIS-V-14` `expect` 74 → 81 | **Forbidden by the declaration itself.** `uis-declaration.json.namespace_governance.obligation`: *"A namespace minted without a declared rule is a namespace no authority governs."* Raising the bound would record 7 ungoverned namespaces as acceptable |

**Determination: `CK-UIS` is a genuine, correctly-detected governance gap that cannot be closed without an owner's decision.** All three available routes require an act this assessment is instructed not to take. The gap is recorded here with its owner named, its mechanism analysed, and its three options costed. **Option (c) is affirmatively recommended against**, on the declaration's own words.

**Recommended route for the owner: (b), scoped minimally** — one append-only namespace declaration in `config.py` (the declared authority) plus one pointer in `uis-declaration.json`. This is consistent with `UMB-004 §5`'s promise that the nomenclature *"self-expands without redesign"*, and with `UMB-004 §6`'s rule that an undeclared family is *"surfaced for an append-only declaration — never silently guessed"*. That is what `UIS-V-14` is doing right now: surfacing it.

---

## 3. CK-BASELINE Resolution

Two failures reported under `BLN-VAL-17 VERSION-SUCCEEDED`, plus `BLN-VAL-26 CAPABILITY-DISCHARGED` which is their **consequence** (`BLN-CAP-08 versions_succeeded`, `BLN-CAP-16 configuration_versions_read` are undischarged because their measure did not complete).

Declared sources — `baseline-declaration.json.version_sources`:
- `BLN-VER-01` constitutional register → `00-CMG/CMG-REGISTRY.json` `artifacts[].version`, **`base_version: "1.0"`**
- `BLN-VER-02` identity → `00-BOOK/DATA/artifacts.json` (`path` → `universal_id`)
- `BLN-VER-03` ledger → `00-BOOK/DATA/change-ledger.json`, token `Version-Incremented`

### 3.1 `UCKP-LAW-0001: no universal identity resolves for its path`

**The reported diagnosis is wrong. This is not an identity-source mismatch — it is a version-format comparison defect.** Measured evidence:

| Fact | Value |
|---|---|
| Version strings across the 44 recognized artifacts | `1.0` ×39 · `1.1` ×2 · `1.2` ×2 · **`1.0.0` ×1** |
| The sole 3-component value | `UCKP-LAW-0001` |
| Its canonical source | `engine/uckp/law.py:38` — `LAW_VERSION = "1.0.0"`. The projection is **correct**; `CMG-REGISTRY.json` states *"Where this file and the canonical source disagree, the canonical source governs"* |
| The comparison | `baseline_engine.py:668-670` — `if not version or version == base: continue`, with `base = "1.0"` |
| Consequence | `"1.0.0" != "1.0"` by string equality → `UCKP-LAW-0001` is wrongly treated as *above* base → identity resolution is attempted → `artifacts.json` holds 0 `.py` → failure |

**`UCKP-LAW-0001` is AT the base version.** It has no version progression to record, so no ledger event is missing and no identity lookup should occur.

**Verified by reversible probe.** A version-aware comparison was applied, the gate re-run, and the patch reverted:

| Measure | Before | With normalized comparison |
|---|---|---|
| `BLN-VAL-17` failures | **2** | **1** |
| Failure text | `CMG-000001: …` + `UCKP-LAW-0001: no universal identity resolves for its path` | `CMG-000001: no recorded increment reaches its version` only |
| `versions` counter | 3/5 | **3/4** — UCKP correctly leaves the progression population |
| `BLN-VAL-26` | 2 | 2 (unchanged — CMG still fails) |
| Gate | CLOSED | CLOSED |

The exact patch, at `00-MASTER/BASELINE-001/baseline_engine.py:668`:

```python
def _norm(v: str) -> tuple:
    parts = [int(x) for x in v.split(".") if x.isdigit()]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)
if not version or _norm(version) == _norm(base):
    continue
```

**Action: SPECIFIED AND VERIFIED, NOT APPLIED.** Grounds for holding: it edits a constitutional gate engine that has **zero tests** (`00-MASTER/**`: 48 modules, 0 test files), it changes what *"at base version"* means — a declaration-semantics question owned by `BASELINE-001` under `CEP-007 XXIV.2` / `CEP-009 XXIV.2` — and it **cannot open the gate alone** (§3.2 still fails). The repository's own precedent for applying an unverified change to a measure is the `ukb.py:1733-1735` incident, in which a swallowed `ImportError` let 539 schema violations pass.

### 3.2 `CMG-000001: no recorded increment reaches its version`

**A genuine missing ledger event. The engine is correct to fail.** Measured in `00-BOOK/DATA/change-ledger.json` (1353 events: 1233 `Created`, 115 `Modified`, **5** `Version-Incremented`):

| Subject | `Version-Incremented` events | Registry version |
|---|---|---|
| `UCOS-CON-000033` | 1.0 → 1.1 | 1.1 |
| `UCOS-CON-000034` | 1.0 → 1.1, **1.1 → 1.2** | 1.2 |
| `UCOS-CON-000041` | 1.0 → 1.1 | 1.1 |
| **`UCOS-CON-000050`** = `CMG-000001` | 1.0 → 1.1, then two `Modified` (content-hash) events, **no 1.1 → 1.2** | **1.2** |

`UCOS-CON-000034` proves the mechanism works. `CMG-000001` was amended to v1.2 by AMD-002 — the amendment record at `CMG-000001:2035` states *"Version **1.1 → 1.2**"* and `:2040` asserts *"Registry, delegation, traceability, dependency records updated in the same change"* — but the **change ledger was not updated**. `BLN-VAL-17` exists precisely to catch this, and it did.

**Action: REQUIRES AUTHORISATION.** `change-ledger.json` is generated output; the generated-artifact rule forbids hand edits. The increment must be recorded by the registration transaction — `bash 00-BOOK/tools/register.sh --guard`, i.e. `./verify.sh --full` Stage 7 — which **mutates** `00-BOOK/DATA`, `00-BOOK/REGISTRIES`, `00-BOOK/CONTROL-TOWER` and `00-BOOK/PORTAL`. That is a write-scope expansion beyond anything executed in this programme and needs explicit approval. It is also **unverified** whether `register.sh` emits a *retroactive* increment for a version bump committed earlier; if it does not, the event must be recorded by the ledger's owner through its declared append path.

### 3.3 CK-BASELINE determination

**NOT RESOLVED — one defect specified and verified, one blocked on authorisation.** `CK-BASELINE` remains CLOSED. Discharging it requires both §3.1 and §3.2; neither alone suffices.

---

## 4. Gate Purity Determination

Measured empirically: each gate was run with a clean baseline, tracked-file delta recorded, and the tree restored before the next probe. Harness `/tmp/ucos-verify/gate_purity.sh`; results `/tmp/ucos-verify/gate_purity.tsv`. Tree returned to baseline after all 28 probes.

### 4.1 READ_ONLY — 0 tracked writes measured (15 gates)

| Gate | Exit | Declared scope | Conformant |
|---|---|---|---|
| `ukb.py enforce --pre` | 0 | `read-only` (CK-REG-ENFORCE) | ✅ |
| `ukb.py validate` | 0 | `read-only` (CK-REG-VALIDATE) | ✅ |
| `cmg-gate.sh` | 0 | `read-only` (CK-CMG) | ✅ |
| `uga_engine.py gate` | 0 | `read-only` (`verify.sh` Stage 6b: *"`gate` mints nothing and writes nothing"*) | ✅ |
| `engine.uaue.gate --gate` | 0 | `read-only` (*"Read-only and hermetic"*) | ✅ |
| `engine.uaue.gate --replay` | 0 | `read-only` | ✅ |
| `urat_engine.py --gate` | 0 | `read-only` (CK-URAT) | ✅ |
| `utce_engine.py --gate` | 0 | `read-only` (CK-UTCE) | ✅ |
| `ucef_engine.py --gate` | 0 | `read-only` ×5 | ✅ |
| `uei_engine.py --gate` | 0 | — | ✅ |
| `uer_engine.py --gate` | 0 | — | ✅ |
| `uar_engine.py --gate` | 0 | — | ✅ |
| `rfp_engine.py --gate` | 1 | — | ✅ (fails without writing) |
| `umk_engine.py --gate` | 0 | `read-only` | ✅ |
| `upf_engine.py --gate` | 0 | — | ✅ |
| `mcos_engine.py --gate` | 0 | `read-only` ×3 | ✅ |
| `ucda_engine.py --gate` | 0 | `own-memory` | ✅ |

**All six `verify.sh` gate stages are measured READ_ONLY. The canonical verification path is pure.** This is the single most important result in this section: the pipeline that decides repository truth does not mutate the tree it measures.

### 4.2 MUTATING — tracked writes measured (11 gates)

| Gate | Exit | Files written | Declared scope | Verdict |
|---|---|---|---|---|
| `uccep_engine.py --gate` | 1 | **53** | `read-only` (CK-SELF-* ×5) | ❌ **VIOLATION (by delegation)** |
| `aee_engine.py --gate` | 0 | **21** | not bound in `uccep-bindings.json` | ⚠️ UNDECLARED |
| `acee_engine.py --gate` | 0 | **17** | **`read-only`** (CK-ACEE, CK-ACEE-SELF) | ❌ **VIOLATION** |
| `rib_engine.py --gate` | 1 | **16** | not bound | ⚠️ UNDECLARED |
| `ucl_engine.py --gate` | 1 | **15** | **`read-only`** (CK-UCL, CK-UCL-SELF) | ❌ **VIOLATION** |
| `assimilation_engine.py --gate` | 0 | **11** | not bound | ⚠️ UNDECLARED |
| `uis_engine.py --gate` | 1 | **10** | `00-MASTER/UIS-001/` | ✅ in scope |
| `ucaf_engine.py --gate` | 0 | **6** | **`read-only`** (CK-UCAF, CK-UCAF-SELF) | ❌ **VIOLATION** |
| `baseline_engine.py --gate` | 1 | **5** | `00-MASTER/BASELINE-001/` | ✅ in scope |
| `urrc_engine.py --gate` | 0 | **5** | not bound | ⚠️ UNDECLARED |
| `ufep_engine.py --gate` | 1 | **3** | `read-only` (CK-UFEP-SELF only; gate mode unbound) | ⚠️ UNDECLARED for gate mode |

### 4.3 Purity findings

| # | Finding | Evidence |
|---|---|---|
| **GP-01** | **Three engines declare `read-only` and write tracked files.** `ucl_engine.py` (15), `acee_engine.py` (17), `ucaf_engine.py` (6). Declared at `uccep-bindings.json` → `checks[CK-UCL].write_scope = "read-only"`, `[CK-ACEE]`, `[CK-UCAF]` | measured, restored |
| **GP-02** | **The aggregate certifier violates its own read-only claim by delegation.** All five `CK-SELF-*` checks declare `read-only`, yet `uccep_engine.py --gate` dirties **53** tracked files — the sum of the sub-engine cascade (`acee` 17 + `ucl` 15 + `uis` 10 + `ucaf` 6 + `baseline` 5). A gate that delegates to a mutating gate is mutating | measured |
| **GP-03** | **Five gate modes have no declared write scope at all**: `aee`, `rib`, `assimilation`, `urrc`, and `ufep` in `--gate` mode. Under the fail-closed principle an undeclared write scope is of UNKNOWN conformance, not permitted | `uccep-bindings.json` has no `checks` entry for them |
| **GP-04** | Two engines are **honestly declared as mutating and stay in scope**: `uis_engine.py` → `00-MASTER/UIS-001/` (10 files), `baseline_engine.py` → `00-MASTER/BASELINE-001/` (5 files). These are the correct pattern | measured |
| **GP-05** | Declared scope vocabulary is inconsistent: `read-only` (36), `own-memory` (6), an explicit home path (5), `projections` (1). `own-memory` and a home path mean the same thing stated two ways | `uccep-bindings.json` |
| **GP-06** | Consequence, measured earlier in this programme: running the aggregate certifier once moved working-tree porcelain 113 → 186. An operator who runs `make uccep-gate` to *check* the repository thereby **fails** `rib` GATE-12 (`dirty_entries_outside_generated`) | measured |

**Remediation required (GP-01, GP-02, GP-03) — specified, not applied:** for each of the three violating engines, either make `--gate` write-free (splitting rendering into the existing `--render` mode, which every one of them already has) or amend its declared `write_scope` to its actual home. The first is correct: `mutation-governance-boundary.json` names these engines as **gates**, and a gate that mutates the state it judges cannot be relied on to judge it. Applying this requires editing three untested engines and one binding declaration, and is deferred to the owner on the same grounds as §3.1.

---

## 5. Re-run of `./verify.sh`

Executed after all probes and reverts, with **no persisted engine or declaration edit** (`git diff --stat` over `baseline_engine.py`, `ucl_engine.py`, `config.py`, `CMG-REGISTRY.json` returned empty). Result recorded in `FINAL-FREEZE-ELIGIBILITY-DETERMINATION.md` §1.

---

## 6. Determination summary

| # | Boundary question | Determination | Action taken |
|---|---|---|---|
| 1 | Are `.py` artifacts canonical constitutional artifacts? | **YES — already determined** by `CMG-K-14` (form: Executable), `CMG-REGISTRY.json` recognition of `UCKP-LAW-0001`, and amendment AMD-002 | **None.** Restating it would duplicate existing knowledge |
| 1.1 | Widen `INCLUDE_EXTENSIONS` to admit `.py`? | **NO — REFUSED.** Constitutional recognition, universal identity and corpus pagination are three distinct planes; `.py` is already registered (`UGA-INV-03` PASS, 4611 objects). Widening would add 2027 artifacts, repaginate an append-only ledger and invalidate the certification scope | **None** — refused as architecture expansion |
| 1.2/1.3 | UCL ratchets | `UCL-V-41` → **264** (or 265 if the staged set is committed); `UCL-V-42` → **85**. Delta measured by identity: exactly 1 artifact added, 0 removed; cause is commit `8bad683f` | **Specified.** Value depends on the undecided HEAD-inclusion set |
| 2 | Canonical owner of the 7 namespaces | **Already exists and is not vacant:** AIF `UCOS-IMP-000024` governs, `UMB-004 §5` realizes, `00-BOOK/tools/config.py` mechanises. `UCOS-UGA-001` mints but does not own | **No assignment made.** No fitting declaration surface exists; all three closure routes need an owner's act. Option (c) — raising the bound — recommended **against** |
| 3.1 | UCKP identity mismatch | **Misdiagnosed upstream.** It is a **version-format comparison defect** (`"1.0.0"` vs base `"1.0"`); `UCKP-LAW-0001` is at base. Patch verified to drop `BLN-VAL-17` from 2 → 1 failures | **Specified and verified, reverted.** Engine has 0 tests; cannot open the gate alone |
| 3.2 | CMG missing increment | **Genuine.** `UCOS-CON-000050` has 1.0 → 1.1 but no 1.1 → 1.2, while the register says 1.2. AMD-002 claimed all records were updated; the ledger was not | **Requires authorisation** — `register.sh --guard` write scope |
| 4 | Gate purity | **15 READ_ONLY, 11 MUTATING.** All 6 `verify.sh` stages pure. **3 violations** (`ucl`, `acee`, `ucaf` declare read-only and write), 1 by delegation (`uccep`, 53 files), 5 undeclared | **Specified.** Fix is to route rendering through each engine's existing `--render` mode |

**Boundaries closed by determination: 2 of 4** (question 1 answered from existing authority; question 2's owner identified without assignment).
**Boundaries requiring an owner's act: 3** — UCL ratchet re-tightening, UIS namespace declaration surface, CMG increment ledgering.
**Defects specified and verified but not applied: 2** — the baseline version-comparison patch and the three gate-purity separations.

**No new architecture, capability, universe, owner or registry was created. No boundary was widened.**
