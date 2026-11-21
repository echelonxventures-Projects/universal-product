# UNIVERSAL PRINCIPLE ASSIMILATION DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UNIVERSAL-PRINCIPLE-ASSIMILATION-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` |
| AUTHORITY | **NONE — DERIVED TRUTH.** Legislates nothing, ratifies nothing, certifies nothing, assigns no ownership, allocates no identity. Where this determination and a located instrument differ, the located instrument governs. |
| DISPOSITION | **DETERMINATION ONLY.** No production architecture modified. No engine edited. No declaration edited. |
| SUBJECT | The requested UPAE — Universal Principle Assimilation Engine — and the ten-step pipeline Discussion → Knowledge Extraction → Canonical Principle Object → Classification → Authority Resolution → Affected Surface Mapping → Validation Rule Generation → Continuous Enforcement → Evolution Tracking |
| BASELINE | HEAD `03179308f5cb` · branch `integration/recovery-001` · working tree as received at session open (120 staged/modified entries) and byte-identical at close |
| MODE | Read-only measurement. No registry mutation. No identity minting. No certification claim. |
| GOVERNING INSTRUMENTS | `00-CEP/CEP-002` Article 28 (decision assimilation) · `UCOS-UFC-001` UFC-16 (one population, one measurement) · `adr/0024` (append-only decision history) · `CMG-000001` LXXVI.6 (admission is visible, reinterpretation is not) |
| REFUSES | Minting a `UPAE-000001` identifier. Creating a second principle registry. Creating a second lifecycle. Claiming any principle is enforced without a named executable check. |

> **Headline.** No engine, directory, declaration or identifier named UPAE exists — a repository-wide search for the token `UPAE` returns **zero** occurrences. But the capability is **not absent; it is fragmented across four located owners and structurally incomplete in one specific place.** The Canonical Principle Object cannot currently be represented: the only principle registry in the repository closes its schema at four keys, so **nine of the fourteen attributes the directive requires have nowhere to live.** The correct disposition is to extend two existing owners, not to charter a new programme.

---

## 0. What was measured, and with what

| Question | Command / file | Result |
|---|---|---|
| Does any UPAE artifact exist? | `grep -rl 'UPAE' --include='*.md' --include='*.py' --include='*.json' --include='*.yml'` | **0 hits** |
| What is the principle registry schema? | `00-MASTER/UCCEP-000000/uccep_engine.py:69-72` | `principles: {id, name, owner, enforced_by}` — closed set |
| How many principles are registered? | `00-MASTER/UCCEP-000000/uccep-bindings.json` | `principles` **22** · `invariants` **17** |
| Is PRINCIPLE a first-class knowledge kind? | `engine/knowledge/model.py` `KnowledgeKind` | Yes — `principle`, `rule`, `constraint`, `policy`, `law`, `decision` are distinct members |
| How many principle objects exist on the CKO plane? | `knowledge/canonical-knowledge.json` (142 objects) | `principle` **5** (`UCKO-PRIN-0001..0005`) · `law` **0** |
| Is there a decision lifecycle to reuse? | `00-MASTER/UCDA-000001/ucda-decisions.json` | 9 stages, closed by CEP-002 Art 28.8; 5 dispositions; evidence gate Art 28.17–28.21 |
| Is there append-only history to reuse? | `00-MASTER/UCDA-000001/ucda_engine.py` `record_decision_update` / `verify_decision_history` | Hash-chained, genesis = 64 zeros, returns a new document and writes nothing |
| What is the identity-minting mechanism to avoid? | `00-BOOK/tools/ukb.py::allocate` | `seq = category_seq[cat]+1; uid = f"UCOS-{category}-{seq:06d}"` — `mint=False` allocates nothing |
| Was the ledger touched by this determination? | `git diff -- 00-BOOK/DATA/id-ledger.json` | **0 lines** |

---

## 1. Current state

### 1.1 The capability is fragmented across four located owners

| Pipeline step the directive requires | Located owner | State |
|---|---|---|
| Discussion → captured | — | **ABSENT.** No mechanism admits a conversation-born principle. |
| Knowledge Extraction | `00-MASTER/ACEE-000001` admission path `AP-PRINCIPLE` (adapter `SRC-GOVERNANCE-PRINCIPLE`, `pointer: principles`, axis "Constitutional principles") | **EXISTS** — lifts the 22 UCCEP principles into the CKO plane as `governance-principle` objects |
| Canonical Principle Object | `engine/knowledge/cko.py` `CanonicalKnowledgeObject` (content-addressed, `content_sha256` over every other field) | **EXISTS as a carrier**, unused for principles — 5 instances |
| Classification | `engine/knowledge/model.py` `KnowledgeKind` | **EXISTS** — the directive's seven principle types map onto existing members (§2.2) |
| Authority Resolution | `UCCEP.principles[].owner` · CKO `authority` / `owner` | **EXISTS**, two representations, unjoined |
| Affected Surface Mapping | CKO `dependencies[]`, `consumers[]`, `knowledge_links[]` | **EXISTS as a carrier**, unpopulated for principles |
| Validation Rule Generation | — | **ABSENT.** `enforced_by` is hand-authored prose. |
| Continuous Enforcement | `UCCEP.principles[].enforced_by → checks[]` executed by `uccep_engine.py` | **EXISTS** for the 22 |
| Evolution Tracking | `ucda_engine.py` hash chain · `knowledge/canonical-knowledge-history.json` | **EXISTS**, not wired to principles |

### 1.2 The decision plane is complete and is the reuse precedent

`UCDA-000001` already does for *decisions* what the directive asks for *principles*: a closed 9-stage lifecycle (`DISCUSSION → CONSTITUTIONAL-AGREEMENT → DECISION-REGISTRATION → REPOSITORY-MAPPING → {IMPLEMENTATION | REPOSITORY-TRUTH-UPDATE} → VALIDATION → CERTIFICATION → REPOSITORY-TRUTH-UPDATE → CLOSURE`), a closed disposition set, a per-disposition required-evidence gate, and a hash-chained append-only history.

It also states its own limits, which bind any successor: it is *"NOT a registry. It allocates no identity."* `adr/0024` records the governing precedent verbatim — *"we refuse to build a second decision-mutation authority, a second registry, or a policy substitute."* That ADR added **two functions and one dispatch-table entry** rather than a programme. That is the shape this work should take.

---

## 2. Discovered gaps

| ID | Finding | Grade |
|---|---|---|
| **PA-G-01** | **No assimilation path exists from a received principle statement to a governed object.** Every principle currently in the repository was placed by hand. `UCOS-CEA-000001` classified ten amendment principles manually. This is the directive's core complaint and it is real. | **CONFIRMED** |
| **PA-G-02** | **The Canonical Principle Object cannot be represented.** `uccep_engine.py:69-72` closes `principles` at `{id, name, owner, enforced_by}`. Of the fourteen attributes the directive requires, **nine have no field**: Intent, Scope, Applicability, Affected Architecture Surfaces, Dependencies, Validation Obligations, Evidence Requirements, Lifecycle State, Evolution History. The closure is deliberate — the comment above it says the closed key set is *"what prevents a finite domain, industry, science, technology, platform, language, database, infrastructure or reality from ever being smuggled into the declaration as a new field"* — so widening it is a governed act, not an edit. | **CONFIRMED** |
| **PA-G-03** | **`KnowledgeKind.LAW` is declared and has zero instances.** Constitutional laws exist only as markdown rows (e.g. `UCEF-LAW-*`). The directive's "Constitutional Law" principle type therefore has a declared kind and no population. | **CONFIRMED** |
| **PA-G-04** | **Two principle populations, no join key.** 22 in `uccep-bindings.json`; 5 on the CKO plane. Nothing states whether these are the same population. Under `UFC-16` — *"One subject population SHALL yield one measurement"* — an undisclosed two-plane count is the precise condition that refused `UCOS-URR-001`. | **CONFIRMED** |
| **PA-G-05** | **No validation-rule generation exists anywhere.** `enforced_by` names checks that a human already wrote. Nothing derives a check from a principle statement, and nothing detects a principle whose `enforced_by` is empty. | **CONFIRMED** |
| **PA-G-06** | **Principles that declare no enforcement are structurally permitted.** `adr/0021` (UAP-001) and `adr/0022` (UIEP-001) both explicitly disclaim enforcement, on the sound ground that *"a principle about future, unbuilt structures cannot have executable evidence by definition."* There is no intermediate tier between "unenforced direction" and "gated law", so a principle cannot be admitted as *partially* enforceable. | **CONFIRMED** |

---

## 3. Canonical Principle Object — attribute-to-field mapping

The directive's fourteen attributes do **not** require a new object type. Twelve map onto `CanonicalKnowledgeObject` fields that already exist and are already content-hashed.

| Required attribute | Existing CKO field | Status |
|---|---|---|
| Principle Identity | `cko_id` | present |
| Principle Type | `kind` (`principle`/`law`/`rule`/`policy`/`constraint`/`decision`) | present — six of the seven types are existing members |
| Source Origin | `rationale`, `documentation_links[]` | present |
| Intent | `statement` | present |
| Scope | `universe` | present |
| Applicability | `tags[]` | present, weakly typed |
| Affected Architecture Surfaces | `consumers[]` | present, unpopulated |
| Dependencies | `dependencies[]` | present |
| Authority | `authority` | present |
| Owner | `owner` | present |
| Validation Obligations | `validation` | present |
| Evidence Requirements | `evidence[]` | present |
| Lifecycle State | `lifecycle` | present |
| Evolution History | `knowledge/canonical-knowledge-history.json` + `content_sha256` | present |

**The directive's four rules are already enforced on this plane.** Append-only history: the history file plus `adr/0025`. No silent modification: `content_sha256` is computed over every field but itself, so *"any post-authoring mutation is detectable."* No duplicate authority: hash equality detects duplicates (the Knowledge Once Principle, `PR-02`). No conflicting principles without resolution: `conflicts_with[]` exists as a field.

The seventh principle type, **Exception**, has no `KnowledgeKind` member. That is a one-row admission, not a redesign.

---

## 4. Affected artifacts

**Would be extended (governed acts, not edits):**
- `00-MASTER/UCCEP-000000/uccep-bindings.json` — `principles[]` entries
- `00-MASTER/UCCEP-000000/uccep_engine.py:69-72` — `ALLOWED_KEYS["principles"]`
- `engine/knowledge/model.py` — `KnowledgeKind` (one member: `exception`)
- `knowledge/canonical-knowledge.json` — principle population

**Would be read, not written:** `00-MASTER/UCDA-000001/ucda-decisions.json`, `ucda_engine.py`, `00-MASTER/ACEE-000001/acee-declaration.json`, `adr/0021`, `adr/0022`, `adr/0024`.

**Must not be touched:** `00-BOOK/DATA/id-ledger.json`, `00-BOOK/DATA/artifacts.json`, `00-BOOK/REGISTRIES/**`, any `canonical_path` in `00-BOOK/DATA/generated-artifact-registry.json`. Corpus registration is `REG-AUTO-001`'s alone and runs only under an explicit `--mint`.

---

## 5. Implementation impact

**No new programme.** Charter no `UPAE-000001`. `UNIVERSAL-EVOLUTION-MODEL-DETERMINATION.md` refused an Evolution Registry on exactly this ground — *"Nothing is minted, no corpus serial is consumed and no registry is written, so this register cannot become a second identity authority"* — and adding one would breach `CAA-INV-04`.

The residual work is narrow and has three parts:

1. **Widen the principle schema** (PA-G-02). Add the nine missing keys to `ALLOWED_KEYS["principles"]` and to the 22 existing entries. This is a fail-closed schema change: every existing entry must be brought to the new shape in the same act, or the engine refuses. Blast radius is one engine and one declaration.
2. **Join the two principle planes** (PA-G-04). Decide whether `UCCEP.principles[]` or the CKO plane is the single population, and make the other a declared projection of it. This is the `UFC-16` obligation. **This determination does not choose** — the `UCOS-URR-001` disposition reserves population-authority choices to a governing authority under `CEP-002 14.2`.
3. **Add a coverage measurement, not a generator** (PA-G-05). Deriving a check from prose is not achievable deterministically. What *is* achievable, and matches house technique, is a check that measures whether every registered principle names at least one `enforced_by` check that exists and executes — and discloses the ones that do not, in the `ISD-CE-*`/`ISD-G-*` disclosure form. Enforcement coverage becomes measured rather than assumed.

**Order matters:** step 1 before step 3, because a principle cannot carry a validation obligation until the schema has a field for one.

---

## 6. Validation approach

| Obligation | How it would be measured | Precedent |
|---|---|---|
| Schema widening is total | `uccep_engine.py` already fails closed on any key outside the allowed set; the same mechanism proves all 22 entries conform | existing |
| History is append-only | `verify_decision_history` recomputes the chain and reports "previous-hash link broken" / "entry hash does not reproduce" | `adr/0024` |
| No silent modification | recompute `content_sha256` and compare | `engine/knowledge/cko.py` |
| No duplicate authority | hash equality across the population; `enforced_by` owners resolve to exactly one located owner | `PR-02` |
| Principle plane is open | admit a synthetic principle into a **deep copy** of the declaration each run and prove the original did not move | `check_relationship_model_expands`, `check_admission_path_exercisability` |
| Enforcement coverage | count principles whose `enforced_by` names a check that exists; disclose the remainder as gaps | `ISD-L-01` disclosure form |

Every check must be a pure function that reads no clock, opens no socket, spawns no subprocess and writes nothing — the constraint `engine/infinite_scope/contract.py` already documents and satisfies, so *"a gate built on them cannot dirty the tree."*

---

## 7. Risk assessment

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| PA-R-01 | Chartering UPAE creates a second principle authority, breaching Zero Parallel Authority and `CAA-INV-04` | **HIGH** | Do not charter. Extend UCCEP + CKO. |
| PA-R-02 | Widening `ALLOWED_KEYS` weakens the defence the closure exists to provide — the comment says the closed set is what stops a finite reality being smuggled in as a field | **MEDIUM** | Add *governance* fields only (intent, scope, obligations, evidence, lifecycle, history). Add no field whose value space is a finite domain, technology or industry. |
| PA-R-03 | Two principle populations get a note instead of a convergence, which `UFC-16` forbids ("SHALL be converged, never reconciled by note") | **HIGH** | Reserve to governing authority; do not paper over. |
| PA-R-04 | A generated "validation rule" becomes fabricated evidence | **HIGH** | Generate nothing. Measure coverage and disclose gaps. |
| PA-R-05 | Retrofitting history onto the 22 existing principles fabricates a past that was never captured — the defect `adr/0024` explicitly refused for `DEC-ADR-0015..0023` | **MEDIUM** | Start the chain at admission. Record the absence of prior history rather than inventing it. |
| PA-R-06 | Principles admitted with empty `enforced_by` create the appearance of governance without enforcement | **MEDIUM** | Empty enforcement is a *declared disclosure with a gap id*, never a silent default. |

---

## 8. Acceptance criteria

1. `grep -rl 'UPAE'` returns 0 — no programme identifier was minted. **Verifiable now.**
2. `git diff -- 00-BOOK/DATA/id-ledger.json` and `-- 00-BOOK/DATA/artifacts.json` are empty. **Verifiable now.**
3. `ALLOWED_KEYS["principles"]` carries a field for each of the fourteen required attributes, and all registered principle entries validate against it with zero findings.
4. Exactly one principle population is declared authoritative; any second surface declares itself a projection of it and its count is derived, not written.
5. Every registered principle either names an `enforced_by` check that exists and executes, or carries an explicit gap id. Zero principles are silently unenforced.
6. A synthetic principle can be admitted into a copy of the declaration without an engine edit, and the original population is proven unmoved in the same run.
7. Principle history verifies as a hash chain from genesis, with no fabricated pre-admission entries.
8. No certification of the phrase "all principles enforced" is made. Coverage is reported as a measured fraction with the remainder named.

---

## 9. Refusals

- Minting `UPAE-000001` or any identifier. Not performed; `mint=False` semantics respected by not invoking allocation at all.
- Choosing between the two principle populations. Reserved to a governing authority under `CEP-002 14.2`.
- Editing `ALLOWED_KEYS` or any declaration in this pass.
- Asserting that the 22 UCCEP principles are enforced. `enforced_by` was read as declared; the named checks were **not** executed in this pass. Enforcement is **APPARENT**, not confirmed.
- Reinterpreting any existing principle into the new shape by reading. `CMG-000001` LXXVI.6 — *"Reinterpretation is invisible to validation; admission is visible."*

---

## 10. Determination

**PARTIALLY EXISTS — EXTEND TWO OWNERS, CHARTER NOTHING.**

The directive's premise is correct: principles do currently live in human memory, and re-discovery is the observable consequence. The directive's proposed remedy — a new engine — is the wrong instrument. Decision assimilation, append-only history, content-addressed objects, an admission path, and continuous check execution all exist and pass today. The single structural blocker is that **the principle object has nine attributes with nowhere to live**, and the single governance blocker is that **two principle populations are counted separately without disclosure**.

Fix those two and the ten-step pipeline closes over existing owners.

**VERDICT: `DETERMINATION-COMPLETE · IMPLEMENTATION-NOT-AUTHORIZED`**

Nothing in this determination is authorized for implementation. No repository state was modified. `git status` at close is byte-identical to `git status` at open.
