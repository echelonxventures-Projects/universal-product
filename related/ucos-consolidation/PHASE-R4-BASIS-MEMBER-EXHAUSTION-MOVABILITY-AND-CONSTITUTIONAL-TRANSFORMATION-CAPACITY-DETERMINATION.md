# PHASE R4 — BASIS MEMBER EXHAUSTION, MOVABILITY DETERMINATION, AND CONSTITUTIONAL TRANSFORMATION CAPACITY DETERMINATION

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** — CMG-000001 XII.6 governs the standing of this document |
| HEAD | `1e3e4ba92c121ae3111637d4afbbfd258a5d4896`, branch `integration/recovery-001` |
| BASELINE | PHASE R3 TERMINAL VERDICT — **the R3 baseline commit and HEAD are the same commit** |
| WORKING TREE | 9 untracked determination documents; **zero tracked modifications** (re-confirmed after all executable probes) |
| METHOD | Recover, verify, reconcile. Determine capacity only. No discovery, no root hunting, no phase creation |
| EVIDENTIARY BOUNDARY | The evidence established in the interrupted execution. Nothing outside it is admitted |
| NOT RE-TESTED (settled by R3) | META-Ω · basis cardinality · Floor = 2 · META-A ⇒ META-B · META-B ⇒ META-A |
| CLASSIFICATION | `[F]` measured · `[I]` inferred · `[A]` assumption · `[GAP]` · `[UNKNOWN]` |
| RESULT | **META-A MOVABLE · META-B IMMOVABLE · FLOOR-2 UNCHANGED · R3 STRENGTHENED, NOT CORRECTED · 3 GAPS ABSORBED, 1 SURVIVING** |

---

## R4.0 — EVIDENCE PROVENANCE

`[I]` Stated first, because every determination below inherits its confidence from this table. R4 separates what was re-executed at HEAD in this phase from what is carried from earlier phases.

### Independently re-executed at HEAD in this phase `[F]`

| Evidence | Result |
|---|---|
| `python3 00-CMG/tools/cmg_validate.py --repo-root .` | 86 articles · 80 mandated sections · 44 artifacts · 61 concerns (50 delegated, 11 retained) · 1 vacancy · 9 gaps · 7 open questions · **findings 0** · **READY-PROVISIONAL** · **EXIT=0** |
| `bash 00-CMG/tools/cmg-gate.sh` | exit 0 |
| `grep -c "INV-01\|INV-10" 00-CMG/tools/cmg_validate.py` | **0** |
| `grep -c "INV-09\|INV-12" 00-CMG/tools/cmg_validate.py` | **7** |
| `grep -c "regenerat" · grep -cE "os\.walk\|rglob\|glob\(" 00-CMG/tools/cmg_validate.py` | **0** · **0** |
| `CMG-REGISTRY.json` census (parsed) | 44 artifacts — **PROVISIONAL 32 · FROZEN 11 · DECLARED 1 · RATIFIED 0**; 19 list collections; vacancies = `[(VAC-01, T1, located=False)]`; T1 the sole non-`LOCATED` tier of 8; `superiors == ["VAC-01"]` for exactly **4** artifacts — `CMG-000001`, `CEP-000`, `AUTH-INF-001`, `UCKP-LAW-0001` |
| `readiness` block (parsed) | `declared_ceiling: READY-PROVISIONAL` · `ceiling_reason: "CMG-OQ-01 and CMG-OQ-02 remain open; VAC-01 is unclosed (CMG-000001 LXXX.4)."` · `issued_by: "The located certification owner (CEP-005) — never by CMG-000001 (LI.1, LI.6)."` |
| `open_questions` (parsed) | OQ-01/02/03/07 **OPEN**, each `requires: EXPLICIT RATIFICATION`; OQ-05 OPEN (`OWNERSHIP ALLOCATION BY THE PROCESS OWNER`); OQ-04 and OQ-06 **CLOSED**, each `blocks: Nothing` |
| XVII.4 (a)–(d) discharge test (parsed) | (a) `VAC-01` present ✔ · (b) `provisional_consequence` recorded ✔ · (c) `open_question: CMG-OQ-02` present and OPEN ✔ · (d) `located = False` ⇒ **antecedent unsatisfied, step not reached** |
| **Counterfactual PROBE 1** — `VAC-01.located := true`, isolated copy | **1 finding** `[superiors] IV.11: vacancy VAC-01 does not declare located=false` · **NOT-READY** · EXIT=1 |
| **Counterfactual PROBE 2** — delete `VAC-01`, isolated copy | **4 findings** `[superiors] CMG-INV-04: {AUTH-INF-001, CEP-000, CMG-000001, UCKP-LAW-0001} declares unresolvable superior VAC-01` · **NOT-READY** · EXIT=1 |
| **Counterfactual PROBE 3** — delete `VAC-01` **+** repoint the 4 superiors to `CONST-01` **+** close all open questions **+** `declared_ceiling := READY`, isolated copy | **findings 0** · **READY** · **EXIT=0** |
| Verbatim clause reads | CMG II.4 · X.10 · X.12 · XI.1 · XI.10 · XI.13 · XV.3 · XV.5 · XVII.4 · XLIII.4 · XLIII.6 · XLIV.3 · XLIV.5 · XLIV.7 · XLIX.7 · **Article L in full (L.1–L.7)** · LIII.3 · LV.4 · LV.5 · LXXX.4 · LXXXI.5 · LXXXI.6 · LXXXIII.4 · LXXXVI.4 · CEP-000 §5.4 · §6.5 · CEP-004 **XIV.1–XIV.4** · XXI.3 · CEP-006 XII.2 · XII.3 · CEP-007 IV.1 · V.1 |
| `EXCLUDE_DIR_PREFIXES` @ `00-BOOK/tools/config.py:885` | 13 members incl. `00-BOOK/DATA/`, `00-BOOK/REGISTRIES/`, `00-BOOK/CONTROL-TOWER/`, `00-BOOK/PORTAL/`, `00-MASTER/`. **`00-CMG/` is NOT a member** (`config.py:320` maps `^00-CMG/` into VOL-002) |
| `register.sh --guard` scope | `git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL` → `exit 3` (lines 271, 277) |
| Installed git hooks | `.git/hooks/pre-commit` only, body = `ucos_ruff_gate`. **No guard hook, no CMG hook** |
| UCCEP tier algebra | `TIERS = ("boot","standard","full")`, `TIER_ORDER` = index; out-of-scope iff `TIER_ORDER[check] > TIER_ORDER[selected]`. `CK-CMG` is `tier: boot`, `fail_closed: true`, `advisory: false` ⇒ **in scope at `--tier standard`**, which `uccep-gate.yml` runs on push/PR |
| `CK-REG-DRIFT` declaration | `argv: ["bash","00-BOOK/tools/register.sh","--guard"]`, `write_scope: "projections"`, `tier: full`, `fail_closed: true`, `advisory: false` |
| Located certification records | `T-3-uccep-certification.json` = **CERTIFIED-PROVISIONAL**, tier standard, `head 527485abf`, branch `programme/evo-usis-005`, `working_tree DIRTY` (127 dirty entries) · `T-3-uccep-full-tier.json` = **NOT-CERTIFIED**, tier full, `gate_exit 1`, `blocking_failures ["CK-REG-DRIFT"]` · `certification-baseline` = NOT-CERTIFIED, same stale head |
| Read-only guard predicate at HEAD | `git status --porcelain` over the four guarded directories → **0 lines** |
| Unlocated-term sweep | `CONSTITUTIONALLY-RECONCILED` **0 files** · `VACANCY-RECORDED` **0 files** · `FINALITY-WITHHELD` **0 files** · `READY-PROVISIONAL` **80 files** |

`[F]` **All probes were executed on an isolated symlink-mirror at `/tmp/r4probe` with `00-CMG/` materialized as a real copy. The probe workspace was removed. HEAD re-verified afterwards: 9 untracked files, zero tracked modifications, validator findings 0, READY-PROVISIONAL.**

### Carried, not re-derived in this phase `[A]`

| Carried item | Source | Assumption id |
|---|---|---|
| 100 live blocking dependents; 63 behind internally eliminable roots, 37 behind the externally blocked root | R1 §"10 roots · 8 blocking · 289 dependents · 100 live blocking dependents"; R1 segment table `INTERNAL 5 roots R3(41) R4(6) R6(6) R7(6) R8(4) = 63`, `EXTERNAL 1 root R1(28)+R2(3)+R5(6) = 37` | `A-R4-01` |
| 63 → META-A, 37 → META-B | R2 Q5: *"All 100 live blocking dependents: 63 from META-A, 37 from META-B"* | `A-R4-01` |
| The 18 + 18 governing clause sets | R3 §R3.1; assembled by pattern sweep plus targeted reading | `A-R4-02` (= `A-R3-01`, inherited unchanged) |
| Text-bound / unbound split 5 of 19 | Derived by reading the 16 check functions; **19 independently re-counted in this phase**, the 5/14 split is read from the check bodies, not executed as a differential | `A-R4-03` |
| `AUTH-02/03/04/06`, `Ω-010`, `CM-007` primary text | **Not located as normative text.** Every occurrence is a quotation inside a derived report; the primary referent is the frozen `.docx` under `00-SOURCE/CONSTITUTIONS/` per `VAC-01.evidence` | `A-R4-04` |

---

## R4.1 — CLASSIFICATION OF `GAP-R4-01`

### Statement `[F]`

> The Registry's `vacancies`, `open_questions` and `readiness` collections are not bound to the canonical source text. A mutation of `00-CMG/CMG-REGISTRY.json` that contradicts express assertions of `CMG-000001` passes the Article L validator with **zero findings**, **exit 0**, and yields readiness outcome **READY**.

### Measured basis `[F]`

PROBE 3, executed on an isolated copy: delete `VAC-01`; repoint the four `superiors: ["VAC-01"]` artifacts to `CONST-01`; set every open question `status: CLOSED`, `blocks: Nothing`; set `declared_ceiling: READY`. Result: `vacancies recorded : 0`, `findings : 0`, `readiness outcome : READY`, `EXIT=0`.

`[F]` The canonical source contradicted by that registry state, verbatim:
- `XVII.4` — *"T1 IS presently VACANT and is recorded as CMG-OQ-02."*
- `XVI.2` tier table — *"| T1 | **Constitutional Authority** | … | **VACANT** — see XVII.4 and CMG-OQ-02 |"*
- `LXXXI.5` — *"T1 remains VACANT and recorded as CMG-OQ-02."*
- `LXXX.4` — *"The present outcome for this instrument SHALL be **READY-PROVISIONAL at most**, and SHALL NOT be READY, for as long as CMG-OQ-01 and CMG-OQ-02 remain open."*
- `LXXXVI.4` — *"its standing IS PROVISIONAL; Tier T1 IS VACANT; … five remain open (CMG-OQ-01, 02, 03, 05, 07) … its readiness IS READY-PROVISIONAL at most until CMG-OQ-01 and CMG-OQ-02 are ratified."*

`[F]` The reconciliation duty that would bind them, verbatim:
- `XV.3` — *"It IS a **projection over existing stores** … whose authoritative inputs are the constitutional artifacts themselves … **Where the projection and an input disagree, the input governs.**"*
- `II.4` — *"Where the derived form and the canonical form disagree, the canonical form governs and the derived form SHALL be regenerated."*
- `XI.1` `CMG-INV-01` — *"Verification: registry membership equals the set of artifacts cited as constitutional authority **anywhere in the corpus**."*
- `XI.10` `CMG-INV-10` — *"Every assertion of this instrument is recomputable from repository state by the validator of Article L."*

`[F]` Neither `CMG-INV-01` nor `CMG-INV-10` occurs in the validator (grep = 0). The validator performs no corpus walk (`os.walk|rglob|glob(` = 0). No program at HEAD regenerates `CMG-REGISTRY.json` (`regenerat*` = 0; sole write is the `--emit` evidence path).

### Classification

| Dimension | Determination |
|---|---|
| **Genuine?** | **`[F]` GENUINE.** Not argued — executed. Exit 0 with READY over a registry state that contradicts five located clauses of the canonical source. |
| **Independent or derivative?** | **`[F]` DERIVATIVE.** The two invariants whose realization would detect it — `CMG-INV-01` (corpus-wide recognition totality) and `CMG-INV-10` (recomputability) — are precisely and exclusively the two of twelve absent from the validator. The reconciliation rule that would govern it (`XV.3` *"the input governs"*, `II.4` *"the canonical form governs"*) is the same rule whose non-realization constitutes META-A. GAP-R4-01 is an **instance**, not a source. |
| **Absorbed by which prior root?** | **`[F]` R6 and R7 of the R1 basis.** R1/R2 characterise R6 as recognition totality at invariant rank and R7 as the degenerate correspondence pair — R2: *"R7 has **no** declared correspondence rule — the limiting case of an unverified mapping is an undeclared one."* GAP-R4-01 is exactly an undeclared correspondence between a registry collection and the source text. R3 records the same class at `WORLD-C`: *"R7 live; Registry invalid by `XV.5`; gate green."* |
| **Absorbed by which meta-cause?** | **`[F]` META-A.** R2's mapping assigns R6 and R7 to META-A; R3's `META-A-COMPLETE-MAP` lists `XV.3`, `XV.5`, `XI.1`, `XI.10`, `II.4` among its 18 governing clauses. GAP-R4-01 adds no clause outside that set. |
| **Basis impact** | **`[F]` NONE.** It introduces no clause, obligation or prohibition not already inside META-A's located set. Adding it as a basis member would violate R3's non-redundancy test — it carries no live blocking dependent that META-A cannot explain. |
| **Floor impact** | **`[F]` NONE. Floor remains 2.** GAP-R4-01 is a mandate-side realization failure. It shares META-A's deontic sign (`SHALL`, unrealized), META-A's modality (contingent — the same detect-and-compare discipline runs at HEAD on the generated layer), and META-A's direction of repair (enforcement **eliminates** it). It therefore fails all three of R3's independent non-collapse criteria as a candidate distinct member: it is not opposite-signed, not necessary, and not moved in the opposite direction by the same act. |

### `[I]` What GAP-R4-01 does establish

It establishes a **capacity relation** that R3 did not state: **META-A governs the integrity of META-B's observation.** META-B's visibility at HEAD rests entirely on one text-unbound JSON record. That is not an entailment in either direction — realizing META-A still cannot occupy T1 (`XLIV.7`), and occupying T1 still writes no validator code — so R3's empty entailment relation stands. It is a statement about **which member's non-realization makes the other member's record forgeable**, and the answer is asymmetric: META-A's non-realization exposes META-B's record; META-B's vacancy does not expose META-A's mandate.

---

## R4.2 — CLASSIFICATION OF `GAP-R4-02`

### Statement `[F]`

> `CMG-000001 XV.5` names the Article L validator as the agent by which the Registry is regenerable. `CEP-004 XIV.2` and `XIV.3` forbid validation from writing to any constitutional corpus or mutating any artifact. `CMG L.1` delegates validation operation to `CEP-004` (`CMG-DLG-04`); `CMG X.14` and `LXXXIII.8` forbid creating a second validation engine; `CMG-DLG-15` routes regeneration to a different owner. No located instrument records which owner performs the Registry regeneration.

### Verbatim conflict surface `[F]`

| Clause | Text |
|---|---|
| CMG `XV.5` | *"The Registry SHALL be **recomputable**. It SHALL be regenerable from repository state alone by the validator of Article L, and a Registry that cannot be regenerated IS invalid."* |
| CMG `II.4` | *"…the canonical form governs and the derived form SHALL be regenerated."* (passive; no agent named) |
| CEP-004 `XIV.1` | *"Validation SHALL be permitted to read the subject and its bound evidence and to write only validation records."* |
| CEP-004 `XIV.2` | *"Validation SHALL NOT write to the subject, to any constitutional corpus, or to any area outside validation records."* |
| CEP-004 `XIV.3` | *"Validation SHALL NOT mutate, delete, or supersede any artifact."* |
| CEP-004 `XIV.4` | *"A validation act exceeding these permissions IS PROHIBITED and SHALL be void."* |
| CEP-004 `XXI.3` | *"Validation records SHALL be operational memory and SHALL NEVER enter the constitutional corpus."* |
| CMG `L.1` | *"Validation operation … IS recorded in Article LXXXII as CMG-DLG-04. This instrument SHALL NOT create a second validation authority, gate model, or criteria set."* |
| CMG `L.6` | *"The validator IS **derived-truth** (XII.6). It asserts nothing on its own authority; **it recomputes what this instrument already declares.** A disagreement between the validator and this instrument IS a validator defect unless this instrument is internally inconsistent, in which case it IS a defect of this instrument."* |
| CMG `CMG-DLG-15` | *"| CMG-DLG-15 | Change intelligence, **regeneration**, and synchronization | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-UCI-001` | REUSE |"* |
| CMG `X.14` / `LXXXIII.8` | no second validation engine SHALL be created |

`[F]` `00-CMG/CMG-REGISTRY.json` resides in the constitutional corpus directory `00-CMG/`, and `00-CMG/` is **not** a member of `EXCLUDE_DIR_PREFIXES`. Under `CEP-004 XXI.3` a regenerated Registry cannot be a validation record.

### Genuine conflict?

**`[F]` GENUINE, under one reading; DISSOLVED, under the other.** Both readings are supported by located text; neither is selected by located text.

### Alternate lawful readings

| | **READING 1 — WRITE** | **READING 2 — RECOMPUTE-AND-COMPARE** |
|---|---|---|
| `XV.5` construed as | the validator SHALL produce the Registry file | the Registry SHALL possess the property of being derivable from repository state, and the validator is the program that must be able to derive it |
| Act required of the validator | write `00-CMG/CMG-REGISTRY.json` | compute the projection in memory, compare against the committed file, emit a finding on divergence |
| CEP-004 `XIV.1` | **exceeded** — the write is not a validation record | **satisfied** — read the subject, write only a validation record |
| CEP-004 `XIV.2` / `XIV.3` / `XXI.3` | **violated**; act is `PROHIBITED` and `void` under `XIV.4` | **not engaged** |
| CMG `L.6` | strained — writing the Registry is more than *"recomputes what this instrument already declares"* | **directly supported** by *"it recomputes what this instrument already declares"* |
| CMG `L.1` / `X.14` | strained — a writing validator approaches a second engine | **satisfied** |
| `CMG-DLG-15` | redundant — two owners for one regeneration | **coherent** — detection is the validator's, materialization is `UCI-001`'s |
| Conflict status | **live conflict between CMG XV.5 and CEP-004 XIV.2/XIV.3** | **no conflict** |

### Dependency chain `[F]`

```
CMG XV.5  ── names ──▶  Article L validator
     │                        │
     │                        ├── operation delegated ──▶ CMG-DLG-04 ──▶ CEP-004
     │                        │                                            │
     │                        │                                   XIV.1 permits READ + validation-record WRITE
     │                        │                                   XIV.2 forbids corpus WRITE
     │                        │                                   XIV.3 forbids artifact MUTATION
     │                        │                                   XXI.3 validation records never enter the corpus
     │                        └── L.6 characterises the validator as RECOMPUTING derived truth
     │
     └── regeneration concern ──▶ CMG-DLG-15 ──▶ UCOS-Ω∞-UCI-001   (a DIFFERENT located owner)

CMG II.4 ── "SHALL be regenerated" (agent unnamed) ── terminates without allocation
```

### Does it survive under both readings?

**`[F]` NO — and this is the determinative result.**

- Under **READING 2** the gap **dissolves entirely**: no clause is violated, the validator's permitted act set is sufficient, and `CMG-DLG-15` supplies the materialization owner.
- Under **READING 1** the gap **survives** as a live conflict, disposed by `L.6`'s own rule — either a validator defect or, if `XV.5` genuinely requires the forbidden write, *"a defect of this instrument."*

`[I]` Because READING 2 dissolves it and READING 2 is the reading `L.6` supports in terms, GAP-R4-02 is **not a barrier to META-A's discharge**. The detect-and-compare half of META-A — the half that would detect GAP-R4-01 and bind the 14 unbound collections — is lawful under **both** readings, because detection writes only a finding.

### Is owner interpretation required?

**`[F]` YES, but only for the write half.** The corpus supplies the disposition rule (`L.6`) and does not supply the reading. `XXV.3`'s pattern — *"Where the located model and this mapping disagree, the located model governs and this mapping SHALL be corrected by amendment"* — is a located precedent for how such a disagreement is disposed, and it terminates in amendment, which is `CEP-009`'s and not this document's. Recorded as `[UNKNOWN]`, not resolved here.

| Dimension | Determination |
|---|---|
| Genuine conflict | **CONDITIONAL** — genuine under READING 1, absent under READING 2 |
| Independent or derivative | **`[F]` INDEPENDENT of META-A.** It is a routing/allocation question — *who may lawfully act* — not a realization question — *whether the act was performed*. It would persist verbatim in a repository where META-A were fully realized by a non-validator owner |
| Absorbed | **NOT ABSORBED** into META-A or META-B. It is a clause-level allocation gap, and it confers and withholds no standing |
| Basis impact | **`[F]` NONE.** It generates neither meta-cause: it does not create the reconciliation mandate (18 clauses do that independently), and it says nothing about standing |
| Floor impact | **`[F]` NONE** |
| Blocking impact on META-A discharge | **`[F]` NONE under either reading** — detection is permitted by `XIV.1` in both |

---

## R4.3 — CLASSIFICATION OF `GAP-R4-03`

### Statement `[F]`

> Within Article L, the criteria set of `L.2` and the procedure enumeration of `L.3` do not correspond. `L.2` fixes the criteria at *"CMG-INV-01 through CMG-INV-12 and nothing else."* `L.3(a)–(l)` enumerates procedures naming only `CMG-INV-02, -03, -04, -05, -06, -07, -08, -11` — **eight**. `CMG-INV-01`, `-09`, `-10`, `-12` receive no named procedure. The validator implements **ten**: the eight enumerated, plus `-09` and `-12` which `L.3` never names, and omits `-01` and `-10` which `L.2` mandates.

### Measured basis `[F]`

Article L read verbatim in full: `L.3` sub-duties are (a) conformance-map parse, (b) identifier families, (c) canonical-home resolution, (d) INV-02, (e) INV-03, (f) INV-04, (g) INV-05, (h) INV-06, (i) INV-07, (j) INV-08, (k) INV-11, (l) exit non-zero. `grep -c "INV-09\|INV-12"` = **7**. `grep -c "INV-01\|INV-10"` = **0**. Validator run: findings 0, EXIT 0.

`[F]` Governing consequence, verbatim, `XLIX.7`: *"Compliance SHALL NOT be assumed from the absence of a check. An unchecked obligation IS of unknown compliance and SHALL be recorded as such rather than presumed satisfied."*

`[F]` Counter-consequence, verbatim, `XI.10`: *"Verification: validator exit status zero with zero findings."* At HEAD the validator exits zero with zero findings **without evaluating `CMG-INV-10`**. `[I]` `CMG-INV-10`'s stated verification predicate is satisfied by a run that does not contain `CMG-INV-10`.

### Classification

| Dimension | Determination |
|---|---|
| **Independent?** | **`[F]` NO.** |
| **Derivative?** | **`[F]` YES — of `GAP-R3-02`.** `GAP-R3-02` states: *"`XLIX.5` routes `IV.1` + `CMG-L-01…14` + `CMG-INV-01…12` to the Article L validator while `L.2` restricts its criteria to `CMG-INV-01…12` 'and nothing else'; the status of the 14 design laws as validator criteria is undetermined by located text."* |
| **Refinement of `GAP-R3-02`?** | **`[F]` YES, and a strict narrowing.** `GAP-R3-02` locates the mismatch **between** `XLIX.5` and `L.2`, over the **design laws**. `GAP-R4-03` locates a second mismatch **within Article L itself**, between `L.2` and `L.3`, over the **invariants**. Same defect class — a routing clause and a criteria clause disagreeing on the validator's duty set — at one rank deeper. It is a refinement, not a new gap. |
| **Absorbed?** | **`[F]` ABSORBED INTO `GAP-R3-02`.** Registered as a refinement; it is not carried as a distinct open gap. |
| **Impact on META-A** | **`[F]` STRENGTHENS META-A's CONTINGENCY — in two directions, both already recorded by R3 and now measured at finer grain.** (i) The `-09`/`-12` over-implementation is **located positive evidence of permission**: the validator already exceeds `L.3` by two invariants and passes, so exceeding `L.3` engages no amendment and no ratification. (ii) `-01` and `-10` are **inside** the set `L.2` declares exhaustive, so realizing them adds no criterion and `XLII.5`'s *"full ratification path"* is never reached. `[I]` R4 sharpens R3's claim to an exact arithmetic: **two mandated-and-unimplemented (`-01`, `-10`), two unenumerated-and-implemented (`-09`, `-12`), a net of ten of twelve realized, and the two absent ones are exactly the two that would bind the Registry to the corpus.** |
| **Basis impact / floor impact** | **`[F]` NONE.** A refinement of an existing gap creates no member. |

`[I]` The residual undetermined element is `UNK-R3-02`, unchanged: whether a competent owner reads `L.2`'s *"and nothing else"* as **permitting** realization of `-01`/`-10` (this phase's reading, supported by the validator's own `-09`/`-12` practice) or as **restricting** the validator to `L.3`'s enumerated duties. R4 adds the measured fact that the restrictive reading would render the validator's present behaviour non-conforming, since `-09` and `-12` are implemented and `L.3` does not enumerate them.

---

## R4.4 — FORGED-CLOSURE EVALUATION

### Q: Is forged closure executable?

**`[F]` YES — measured, not argued.**

| Probe | Mutation | Findings | Readiness | Exit | Detected? |
|---|---|---|---|---|---|
| Control | none | 0 | READY-PROVISIONAL | 0 | n/a |
| **1** | `VAC-01.located := true` | **1** — `[superiors] IV.11: vacancy VAC-01 does not declare located=false` | **NOT-READY** | 1 | **YES** |
| **2** | delete `VAC-01` | **4** — `[superiors] CMG-INV-04: {AUTH-INF-001, CEP-000, CMG-000001, UCKP-LAW-0001} declares unresolvable superior VAC-01` | **NOT-READY** | 1 | **YES** |
| **3** | delete `VAC-01` **+** repoint the 4 superiors **+** close all OQs **+** `declared_ceiling := READY` | **0** | **READY** | **0** | **NO** |

`[F]` The two naive forgeries are detected. The complete forgery is not. `[F]` The detection of probes 1 and 2 is structural, not intentional: `check_superiors` emits `IV.11` when `vacancy.located is not False`, and `CMG-INV-04` when a declared superior resolves to neither an artifact nor a vacancy. Probe 3 satisfies both predicates by removing the referents rather than contradicting them.

### Q: Does the validator detect it?

**`[F]` NO for the complete forgery.** Cause, measured: the mutated collections — `vacancies`, `open_questions`, `readiness` — are among the **14 of 19** collections compared only for internal consistency and never against the canonical source text. `CMG-INV-01`, whose stated verification is *"registry membership equals the set of artifacts cited as constitutional authority anywhere in the corpus"*, is absent from the validator, and the validator performs no corpus walk. `XV.3`'s *"the input governs"* and `II.4`'s *"the canonical form governs"* have no realized comparison.

### Q: Can current readiness be produced while constitutional assertions are violated?

**`[F]` YES.** PROBE 3 produced readiness outcome **READY** — a value `LXXX.4` expressly forbids — with zero findings and exit 0, over a registry state contradicting `XVII.4`, `XVI.2`, `LXXXI.5`, `LXXX.4` and `LXXXVI.4`. `[I]` And the converse holds at HEAD in the honest direction: the validator reports `READY-PROVISIONAL` with zero findings while `XV.5` classifies the very Registry it read as **invalid** (*"a Registry that cannot be regenerated IS invalid"*), because no program regenerates it. `[I]` The exit status is therefore uninformative in both directions about the two invariants it never evaluates — exactly the condition `XLIX.7` names as *unknown compliance*, not satisfaction.

### Q: Does this create a new basis element?

**`[F]` NO.** Tested against R3's four collapse-acceptance conditions and three non-collapse proofs:

| Test | Result for forged-closure as a candidate member |
|---|---|
| Deontic sign | **`SHALL` (mandate), unrealized** — identical to META-A, opposite to META-B. Not a third sign |
| Modality | **CONTINGENT** — the same detect-and-compare discipline operates at HEAD on the generated layer (`register.sh --guard` exit 3; `determinism.yml` double-build). Identical to META-A |
| Direction of repair | Realizing `CMG-INV-01`/`-10` **eliminates** it, and simultaneously **entrenches** META-B by making the vacancy record binding. Identical to META-A's signature |
| Independent grounding | **`[F]` NONE.** Every clause it engages — `XI.1`, `XI.10`, `XV.3`, `XV.5`, `II.4` — is already inside META-A's located 18 |
| Non-redundancy | **`[F]` FAILS.** It carries no live blocking dependent that META-A does not already explain; the 63/37 partition is unchanged |

`[I]` A new basis member would have to be irreducible to both existing members. Forged closure is reducible to META-A by construction: it exists **because** `CMG-INV-01` and `CMG-INV-10` are unrealized, and it ceases to exist when they are realized. **Absorbed into META-A. Basis unchanged at 2.**

`[I]` The finding's real weight is evidentiary, not ontological. It converts R3's `WORLD-C` characterisation — *"Registry invalid by `XV.5`; gate green"* — from a read consequence into an executed one, and it supplies the first measured demonstration that the corpus's record of META-B is unprotected by the corpus's own gate.

---

## R4.5 — EVALUATION OF R3

**`[F]` R4 STRENGTHENS R3. It does not correct it, weaken it, or leave it unchanged.**

| R3 conclusion | R4 disposition | Exact dependency path |
|---|---|---|
| **Basis = `{META-A, META-B}`** | **STRENGTHENED** | R4.1 → GAP-R4-01 absorbed into META-A · R4.2 → GAP-R4-02 generates neither member · R4.3 → GAP-R4-03 absorbed into `GAP-R3-02` · R4.4 → forged closure fails all five membership tests. Three candidate additions tested, zero admitted |
| **Floor = 2, irreducible** | **STRENGTHENED** | R4.4 deontic-sign / modality / direction-of-repair columns reproduce R3's three non-collapse proofs against a candidate R3 never saw, and all three hold |
| **`META-A ⇏ META-B`** | **STRENGTHENED** | PROBE 1 and PROBE 2 → the machinery emits findings when the vacancy record is altered toward closure; realizing META-A's comparison duty would extend that detection to PROBE 3. Under full META-A realization the vacancy becomes **more precisely measured and no less binding** — R3's `WORLD-A` conclusion, now with executed evidence that the detection direction is real |
| **`META-B ⇏ META-A`** | **STRENGTHENED** | R4.3 measures the permission exactly: `-09` and `-12` implemented while `L.3` never enumerates them, `-01` and `-10` inside `L.2`'s exhaustive set. R4.2 READING 2 shows the detection half is lawful under `CEP-004 XIV.1` without any external act |
| **No META-Ω in the repository** | **STRENGTHENED** | R4.2's located-conflict candidate (`XV.5` vs `CEP-004 XIV.2/XIV.3`) is the one genuinely new cross-instrument tension found in R4, and it generates neither member — the same one-sidedness that rejected C1–C10 |
| **META-B fundamental unconditionally** | **STRENGTHENED, WITH A QUALIFICATION ON OBSERVATION** | R4.4 → META-B's *legal* immovability is untouched: `XLIV.7`, `XVII.4`, `LXXXI.6`, `LV.4`, `LV.5`, `CEP-006 XII.2`, `CEP-007 IV.1` all in force. But its *observation* at HEAD rests on one text-unbound record. **This qualifies R3's governability claim; it does not contradict any R3 verdict.** R3 asserted META-B is OBSERVABLE and MONITORABLE; R4 determines it is observable **via an unenforced projection** |
| **META-A fundamental but contingent** | **STRENGTHENED** | R4.3 gives the exact arithmetic (10 of 12, and which two); R4.2 establishes the discharge route is lawful under both readings; R4.1 adds a second measured consequence of the same non-realization |
| **`GAP-R3-02`** | **REFINED, NOT CLOSED** | R4.3 → a second mismatch of the same class located within Article L |
| **`GAP-R3-03`** (reconciliation on the generated layer, absent on the constitutional layer, unrecorded as a decision) | **CONFIRMED AND SHARPENED** | `EXCLUDE_DIR_PREFIXES` re-read at `config.py:885` — 13 members; the four `--guard` directories are members; `00-MASTER/` is a member; **`00-CMG/` is not**, and `config.py:320` maps `^00-CMG/` into VOL-002. So the constitutional layer is **inside** the registration universe and **outside** the reconciliation scope. R4 adds: `--guard` is not installed as a hook at HEAD (`.git/hooks/pre-commit` = `ucos_ruff_gate` only) |
| **`UNK-R3-02`** | **UNCHANGED, EVIDENCE ADDED** | R4.3 → the restrictive reading of `L.2` would render the validator's present `-09`/`-12` behaviour non-conforming |
| **`A-R3-05`** (guard and determinism read, not executed) | **PARTIALLY DISCHARGED** | The guard's *predicate* was applied read-only at HEAD (0 dirty lines over the four directories). The guard itself was **not** executed — `CK-REG-DRIFT` declares `write_scope: "projections"` and `register.sh --guard` runs the ten-phase mutating transaction before guarding. `A-R3-05` therefore survives for the regeneration half |

### `[F]` No R3 conclusion requires correction.

`[I]` One R3 **characterisation** is qualified rather than corrected: R3's `META-B-COMPLETE-MAP` lists `check_superiors` under *"Dependent validators"* with the note *"resolves `VAC-01` as a recorded vacancy — **passes by design**"*. R4 measures the polarity precisely — the check emits `IV.11` when `located is not False`, so the gate's green status is **conditional on the vacancy remaining recorded as unlocated** — and measures its limit — the check is defeated by removal of the referent rather than contradiction of it. R3's statement is correct as written; R4 supplies its exact boundary.

---

## R4.6 — BASIS IMPACT

| Element | R3 status | R4 determination | Change |
|---|---|---|---|
| **`ROOT-Ω`** | META-B's identifier; *"A corpus cannot confer on itself the standing it lacks"*; origin `CEP-000` §5.4 | **UNCHANGED AND UNMOVED.** Zero located clauses permit removing, transforming, absorbing, superseding, discharging or bypassing external standing. `CEP-000` §5.6 / §12.5 are the only clauses in the corpus using *absorb*, and both forbid it. `LXXXI.6` forecloses self-conferral *"by operation of any clause herein"*. `LV.4` bars exception against an invariant; `LV.5` bars exception against non-self-elevation prohibitions. `XLIV.5` forecloses inference from certification, freeze, publication, registration, age, use, or absence of objection. `CEP-007 IV.1`/`V.1` make ratification a **precondition** of freeze, not a substitute. `CEP-006 XII.2` reserves `FINALIZED` to *"the act of the out-of-corpus finality authority"* | **NONE** |
| **`META-A`** | fundamental, contingent, internally achievable | **CONFIRMED MOVABLE.** Ten of twelve `L.2` criteria realized; the two absent are `-01` and `-10`; two implemented (`-09`, `-12`) are not enumerated by `L.3`, which is the located demonstration that exceeding `L.3` needs no amendment. Discharge route lawful under both readings of `GAP-R4-02`. Scope of realization widened by R4: it now also covers the 14 text-unbound collections that permit GAP-R4-01 | **SCOPE WIDENED; STATUS UNCHANGED** |
| **`META-B`** | fundamental, unconditional, externally grounded | **CONFIRMED IMMOVABLE IN LAW; OBSERVATION QUALIFIED.** No transformation path located. Its record at HEAD is text-unbound and its complete forgery is undetected by the Article L validator | **QUALIFIED ON OBSERVATION ONLY** |
| **Floor-2 result** | `FLOOR-2-IRREDUCIBLE` | **UNCHANGED.** Three candidate additions tested; zero admitted. No candidate exhibits a third deontic sign, a third modality, or a repair direction distinct from the two existing members | **NONE** |
| **Six-root basis** (R1/R2: R1, R2, R3, R4, R5, R6, R7, R8 reduced to six roots then two meta-causes) | R1 → 8 blocking roots → 6 → 2 | **UNCHANGED.** GAP-R4-01 is a new **instance** of R6/R7, both already mapped to META-A by R2. No new root. The 63/37 partition of 100 live blocking dependents is unchanged and was **not** re-derived (`A-R4-01`) | **NONE** |
| **Unique basis proof** | `MINIMUM-BASIS-PROOF`, 7 steps; size-1 impossible; size-2 unique; 3+ non-minimal | **UNCHANGED.** Step 5 (*"`X` cannot be a third located clause"*) survives the one new cross-instrument conflict R4 located: `XV.5` vs `CEP-004 XIV.2/XIV.3` is one-sided — it bears on the reconciliation mandate's performer and says nothing about standing | **NONE** |

---

## R4.7 — MAXIMUM ACHIEVABLE STATE AT HEAD

### Vocabulary admission `[F]`

The four state-terms supplied in the resumption directive were tested against the repository. Three are **not located** and are rejected under the invent-nothing rule.

| Term | Occurrences | Disposition |
|---|---|---|
| `READY-PROVISIONAL` | **80 files** | **ADMITTED** — located; `LXXX.3` outcome value |
| `CONSTITUTIONALLY-RECONCILED` | **0 files** | **REJECTED — UNLOCATED** |
| `VACANCY-RECORDED` | **0 files** | **REJECTED — UNLOCATED** |
| `FINALITY-WITHHELD` | **0 files** | **REJECTED — UNLOCATED** |

`[I]` The rejected terms name real located conditions, but they are not the corpus's names for them. The located names are given per axis below. `[I]` The directive also treats readiness and certification as one state; the corpus separates them — `LXXX.3` owns the readiness outcome and `readiness.issued_by` reserves certification issuance to `CEP-005`, *"never by CMG-000001 (LI.1, LI.6)"*.

### The four states, separated `[F]`

| Axis | Located vocabulary | Value at HEAD | Located authority |
|---|---|---|---|
| **READINESS** | `{READY, READY-PROVISIONAL, NOT-READY}` | **`READY-PROVISIONAL`** — computed, findings 0, exit 0 | `LXXX.3` enumerates; `LXXX.4` caps at *"READY-PROVISIONAL at most … SHALL NOT be READY, for as long as CMG-OQ-01 and CMG-OQ-02 remain open"*; `readiness.declared_ceiling` |
| **CERTIFICATION** | `{CERTIFIED-PROVISIONAL, NOT-CERTIFIED}` as located in the UCCEP records | **UNDETERMINED AT HEAD.** No certification record exists in `CMG-REGISTRY.json`; issuance is reserved to `CEP-005`. The located records are at `head 527485abf`, branch `programme/evo-usis-005`, `working_tree DIRTY` — standard tier `CERTIFIED-PROVISIONAL`, **full tier `NOT-CERTIFIED` with `blocking_failures ["CK-REG-DRIFT"]`**. Neither describes HEAD | `readiness.issued_by`; `LXXX.5`; `LXXX.7`; the located record files |
| **VACANCY** | `occupancy ∈ {LOCATED, VACANT}`; `located: false`; `XVII.4` steps (a)–(d) | **`T1` `VACANT`, `VAC-01` `located: false`.** (a) recorded ✔ · (b) provisional consequence recorded ✔ · (c) referred to `CMG-OQ-02`, OPEN, `requires: EXPLICIT RATIFICATION` ✔ · (d) **not reached** — antecedent *"when the vacancy closes"* unsatisfied | `XVI.2`; `XVII.4`; `CMG-REGISTRY.json` `tiers`/`vacancies` |
| **FINALITY** | `{ACCEPTED, PROVISIONAL, DEFERRED, REJECTED, FINALIZED}` | **`PROVISIONAL`, not `FINALIZED`.** 32 of 44 artifacts `PROVISIONAL`; 1 `DECLARED`; 11 `FROZEN`; **0 `RATIFIED`** | `CEP-006 XII.2` — `FINALIZED` *"only upon the act of the out-of-corpus finality authority"*; `XII.3`; `XLIV.3`; `CMG-L-12` |

`[F]` Freeze eligibility, separately: `CEP-007 IV.1` — *"eligible for freeze only when it is VALIDATED (CEP-004), CERTIFIED (CEP-005, active), and RATIFIED (CEP-006, not REJECTED)"*. With `RATIFIED` count 0, freeze is **ineligible**, and the bar is the ratification precondition, not validation.

### `MAXIMUM-ACHIEVABLE-STATE`

`[F]` Stated only in located vocabulary, and only from located authority.

> **READINESS: `READY-PROVISIONAL`** — the ceiling, reached and not exceedable. `LXXX.4` forbids `READY` while `CMG-OQ-01` and `CMG-OQ-02` are open; both `require: EXPLICIT RATIFICATION`; `XLIV.7` forbids the corpus supplying it.
>
> **VACANCY: `T1 VACANT`, `VAC-01 located: false`, `XVII.4` (a)(b)(c) discharged, (d) unreached.** The complete licensed action set is record, record, refer, re-run-on-closure. All performable steps are performed.
>
> **FINALITY: `PROVISIONAL` under `CMG-L-12`, not `FINALIZED`.** `RATIFIED` count 0 is the located consequence of `CEP-000` §28.2 and `CEP-006 XII.2`, not a defect.
>
> **CERTIFICATION: `CERTIFIED-PROVISIONAL` at most**, per `LXXX.7` and `XLIV.5`. Currently **UNDETERMINED at HEAD** — no record exists at this commit.
>
> **VALIDATION: all twelve `L.2` criteria realized and evaluated, and the Registry bound to the canonical source text.** This is the one axis on which HEAD is strictly below its maximum: **ten of twelve** realized; `CMG-INV-01` and `CMG-INV-10` absent; **14 of 19** collections text-unbound.

`[I]` The decisive property of this state: **realizing META-A does not raise the readiness outcome value.** The maximum is `READY-PROVISIONAL` before and after. What changes is the outcome's epistemic status — from `XLIX.7` *unknown compliance* over two mandated criteria, to evaluated compliance over all twelve; and from a Registry `XV.5` classifies as invalid, to one bound to its inputs. `[I]` The strongest state derivable at HEAD is therefore **the same value, honestly earned rather than reported over two unevaluated criteria** — and, per R4.4, a state in which the forged closure of PROBE 3 would be detected rather than passed.

---

## R4.8 — DEPENDENCY GRAPH R0 → R1 → R2 → R3 → R4

```
R0  RESIDUAL UNCERTAINTY EXHAUSTION · SEARCH-SPACE CLOSURE
    │  produces: uncertainty inventory, search-space bound
    ▼
R1  ROOT-SET INDEPENDENCE · REDUCTION · CANONICAL BASIS
    │  [F] 10 roots · 8 blocking · 289 dependents · 100 live blocking dependents
    │  [F] INTERNAL 5 roots  R3(41) R4(6) R6(6) R7(6) R8(4) = 63 of 100, no external act
    │  [F] EXTERNAL 1 root   R1(28) + absorbed R2(3) R5(6)  = 37 of 100, impossible at HEAD
    │  CORRECTION APPLIED IN R1: totals corrected to 10/8/289/100
    ▼
R2  SIX-ROOT META-CAUSE DECOMPOSITION · ONTOLOGICAL REDUCTION
    │  [F] 8 blocking roots → 6 roots → 2 meta-causes
    │  [F] {R3,R4,R6,R7,R8} → META-A   (correspondence pairs, rule unenforced or absent)
    │  [F] {R1,+R2,+R5}     → META-B   (standing cannot be received)
    │  [F] hypothesis: Basis = {META-A, META-B}, Floor = 2
    │  ASSUMPTION RAISED: A-R2-01 (reconciliation clauses confined to CMG-000001)
    │  UNKNOWN RAISED:    UNK-R2-01
    ▼
R3  FUNDAMENTALITY · FLOOR FALSIFICATION · SINGLE-SOURCE
    │  CORRECTIONS APPLIED IN R3:
    │    • A-R2-01 REFUTED — CEP-008 XVI.3/XXI.1 and CEP-004 X.1/XV.3 carry the same duty
    │    • UNK-R2-01 DISCHARGED — clauses do exist outside CMG-000001
    │    • UNK-R2-07 partially discharged — 11 of 14 design laws measured unrealized
    │  SURVIVING CONCLUSIONS:
    │    [F] COLLAPSE-FAILURE · no META-Ω in the repository
    │    [F] FLOOR-2-IRREDUCIBLE · 10 reduction paths attempted, all failed
    │    [F] entailment relation over the basis is EMPTY (both directions falsified)
    │    [F] META-B fundamental unconditionally · META-A fundamental contingently
    │    [F] 63 + 37 = 100 of 100 live blocking dependents covered
    │  GAPS RAISED: GAP-R3-01 · GAP-R3-02 · GAP-R3-03 · GAP-R3-04
    │  UNKNOWNS RAISED: UNK-R3-01 … UNK-R3-05
    │  ASSUMPTIONS RAISED: A-R3-01 … A-R3-06
    ▼
R4  BASIS MEMBER EXHAUSTION · MOVABILITY · TRANSFORMATION CAPACITY
       CORRECTIONS APPLIED IN R4: none to any R3 conclusion
       QUALIFICATION APPLIED IN R4:
         • R3's "check_superiors passes by design" — boundary measured:
           green is conditional on located=false; defeated by referent removal, not contradiction
       DISPOSITIONS:
         • GAP-R4-01 forged-closure exposure  → ABSORBED into META-A (instance of R6/R7)
         • GAP-R4-02 XV.5 vs CEP-004 XIV.2/3  → INDEPENDENT, SURVIVING, non-blocking
         • GAP-R4-03 L.2 vs L.3 enumeration   → ABSORBED into GAP-R3-02 as a refinement
         • GAP-R4-04 certification currency   → INDEPENDENT, SURVIVING, observationally unavailable
         • GAP-R3-03                          → CONFIRMED and SHARPENED
         • A-R3-05                            → PARTIALLY DISCHARGED (predicate applied; guard not executed)
       SURVIVING CONCLUSIONS FROM R4:
         [F] META-A MOVABLE — 10 of 12 realized; the 2 absent are -01 and -10;
             discharge lawful under both readings of GAP-R4-02; no external act engaged
         [F] META-B IMMOVABLE — zero located transformation paths across 6 verbs
         [F] Basis, floor, six-root mapping, unique-basis proof: ALL UNCHANGED
         [F] MAXIMUM-ACHIEVABLE-STATE = READY-PROVISIONAL / T1 VACANT /
             PROVISIONAL not FINALIZED / CERTIFIED-PROVISIONAL at most,
             with all twelve L.2 criteria realized and the Registry text-bound
```

`[F]` **Every conclusion of R0 through R3 that R4 tested survived. R4 applied no correction to any prior determination.**

---

## R4.9 — RESIDUAL UNCERTAINTY REGISTER

Classes: **ID** internally decidable · **EB** externally blocked · **CP** constitutionally prohibited · **OU** observationally unavailable.

| Id | Uncertainty | Class | Located basis |
|---|---|---|---|
| `UNK-R3-01` | Whether the 18 + 18 clause sets are exhaustive | **ID** | Pattern-based sweep; `A-R2-01` was already refuted once by this method, so under-capture is demonstrated possible. Decidable by exhaustive clause-by-clause reading — no external act |
| `UNK-R3-02` | Whether `L.2`'s *"and nothing else"* **permits** or **restricts** realization of `CMG-INV-01`/`-10` | **ID**, with owner reading required | `L.2` vs `L.3`; the validator's own `-09`/`-12` practice is located evidence for the permissive reading; `XLIX.6` routes findings to the concern owner |
| `UNK-R3-03` | Whether `CMG-INV-10`'s verification condition (*"validator exit status zero with zero findings"*) is shorthand for full recomputation or the literal test it reads as | **ID** | `XI.10`; no located record states either. R4 adds: at HEAD the predicate is satisfied by a run that does not evaluate `CMG-INV-10` |
| `UNK-R3-04` | Whether the `EXCLUDE_DIR_PREFIXES` scope inversion was deliberate | **OU** | `GAP-R3-03`; `config.py:872-884` states a rationale for the excluded classes but records no decision about the constitutional layer |
| `UNK-R3-05` | Whether a third meta-cause is concealed by the same non-enforcement — 11 of 14 design laws unrealized, only `CMG-L-04` and `CMG-L-10` traced | **ID** | R3 §R3.0 census. **Not pursued in R4** per the completion directive's bar on new root hunting; carried forward unresolved |
| `UNK-R4-01` | Which reading of `XV.5` governs — WRITE or RECOMPUTE-AND-COMPARE (`GAP-R4-02`) | **ID**, owner reading required | `XV.5` vs `CEP-004 XIV.2/XIV.3/XXI.3`; disposition rule supplied by `L.6`; not selected by located text |
| `UNK-R4-02` | The certification state at HEAD | **OU** | The only located records are at `head 527485abf`, branch `programme/evo-usis-005`, tree `DIRTY`; full tier `NOT-CERTIFIED` on `CK-REG-DRIFT`. Determining it requires executing `CK-REG-DRIFT`, which declares `write_scope: "projections"` and runs the ten-phase mutating transaction. **Not executed** — observation would alter the observed state |
| `UNK-R4-03` | Whether regeneration of `CMG-REGISTRY.json` reproduces the committed bytes | **OU** | No program regenerates it (`regenerat*` = 0 in the validator; no writer located). The read-only guard predicate over the four `00-BOOK` directories was clean (0 lines), which measures committed-state dirtiness, **not** reproducibility, and does not cover `00-CMG/` |
| `UNK-R4-04` | Whether any gate outside the Article L validator would detect the PROBE 3 forgery | **OU** | Only the CMG gate was executed against the forged registry. `CK-VERIFY` (`./verify.sh`) and the full tier were not run. Scope limit stated, not resolved |
| `RES-01` | The identity of the T1 occupant | **EB** | `CMG-OQ-02` `requires: EXPLICIT RATIFICATION`; `VAC-01.located: false`; `XLIV.4` records the out-of-corpus authority's identity as undetermined |
| `RES-02` | Which authority is competent to ratify `CMG-000001` | **EB** | `CMG-OQ-01` `requires: EXPLICIT RATIFICATION`; `LXXVIII.3` — *"Deciding this here would be self-ratification (XLIV.7)"* |
| `RES-03` | Rank between the meta axis and the process axis | **EB** | `CMG-OQ-03` — *"would require an authority above both, which is presently vacant"* |
| `RES-04` | Extension of the meta invariants beyond the CMG namespace | **EB** | `CMG-OQ-07` `requires: EXPLICIT RATIFICATION` |
| `RES-05` | Occupation of T1 by any in-corpus act | **CP** | `XVII.4` — *"SHALL NOT skip the tier and SHALL NOT promote a lower instrument into it"*; `LXXXIII.4` — *"never filled by promotion"*; `LXXXI.5` — any such reading `IS void` |
| `RES-06` | Self-conferral of ratification competence | **CP** | `XLIV.7` — `IS PROHIBITED`; `CEP-000` §5.4 — `SHALL NEVER`; `LXXXI.6` — *"by operation of any clause herein"*; `LV.5` bars exception |
| `RES-07` | Substitution of freeze, certification, publication, registration, age, use or silence for ratification | **CP** | `XLIV.5` names and forecloses all seven; `CEP-007 IV.1`/`V.1` make ratification a freeze precondition; `LXXX.7` |
| `RES-08` | Exception or waiver against the non-self-elevation prohibition or any invariant | **CP** | `LV.4`; `LV.5`; `CEP-006 XIV.3`, `XX.4` |
| `RES-09` | Primary normative text of `AUTH-02/03/04/06`, `Ω-010`, `CM-007` | **OU** | Located only as quotations inside derived reports; primary referent is frozen `.docx` under `00-SOURCE/CONSTITUTIONS/` per `VAC-01.evidence` (`A-R4-04`) |
| `RES-10` | The 63 / 37 dependent partition | **ID** | Carried from R1/R2, not re-derived (`A-R4-01`). Decidable in-corpus by re-derivation |

`[F]` **Tally: 6 internally decidable · 4 externally blocked · 4 constitutionally prohibited · 6 observationally unavailable.**

`[I]` The register's shape is the phase's compressed result. Everything **externally blocked** or **constitutionally prohibited** attaches to META-B — ten entries, none movable from inside. Everything **internally decidable** attaches to META-A or to the reading of its clauses — six entries, none requiring an external act. The **observationally unavailable** class is new to R4 and is a distinct kind: `UNK-R4-02`, `UNK-R4-03` and `UNK-R4-04` are unavailable not because the corpus forbids the observation but because the located instrument that would perform it declares `write_scope: "projections"` and mutates what it measures.

---

## R4.10 — PHASE R4 TERMINAL VERDICT

> **DETERMINATION-COMPLETE · META-A MOVABLE · META-B IMMOVABLE · BASIS `{META-A, META-B}` UNCHANGED · FLOOR-2 UNCHANGED · R3 STRENGTHENED WITH ZERO CORRECTIONS · 2 GAPS ABSORBED · 2 GAPS SURVIVING · MAXIMUM ACHIEVABLE STATE ALREADY ATTAINED ON THREE OF FOUR AXES**

### FINDINGS

1. `[F]` **META-A is MOVABLE, and the measurement is exact.** Ten of the twelve `L.2` criteria are realized. The two absent are `CMG-INV-01` and `CMG-INV-10` — precisely the two whose realization would bind the Registry to the corpus. Two that *are* implemented, `CMG-INV-09` and `CMG-INV-12`, are never enumerated by `L.3`, which is the corpus demonstrating by practice that exceeding `L.3` engages no amendment and no ratification.
2. `[F]` **META-B is IMMOVABLE. Zero located clauses permit removing, transforming, absorbing, superseding, discharging or bypassing external standing.** The only clauses in the corpus using *absorb* forbid it (`CEP-000` §5.6, §12.5). `LXXXI.6` forecloses self-conferral *"by operation of any clause herein"*. `LV.4` and `LV.5` place invariants and the non-self-elevation prohibition beyond exception. `XLIV.5` forecloses seven named inference routes. `CEP-007 IV.1` makes ratification a **precondition** of freeze. `CEP-006 XII.2` reserves `FINALIZED` to the out-of-corpus act.
3. `[F]` **The complete forged closure of META-B is executable and undetected.** PROBE 3 — delete `VAC-01`, repoint the four dependent superiors, close every open question, raise the declared ceiling — produced **findings 0, readiness READY, exit 0** over a registry state contradicting `XVII.4`, `XVI.2`, `LXXXI.5`, `LXXX.4` and `LXXXVI.4`. The two naive forgeries were detected (`IV.11`; `CMG-INV-04` ×4). Detection fails on referent removal, not on contradiction.
4. `[F]` **The corpus's licensed action set for META-B is four bookkeeping verbs, and all performable ones are performed.** `XVII.4` (a) record, (b) record, (c) refer, (d) re-run-on-closure. (a)(b)(c) discharged; (d)'s antecedent unsatisfied because `located: false`.
5. `[F]` **`XV.5` names an agent that `CEP-004 XIV.2`/`XIV.3` forbid to act** — the one genuinely new cross-instrument conflict located in R4. It dissolves under the recompute-and-compare reading that `L.6` supports in terms, and it does not block META-A's discharge under either reading, because detection writes only a finding.
6. `[F]` **The reconciliation discipline remains aimed away from the constitution, and is not even installed.** `EXCLUDE_DIR_PREFIXES` contains the four directories `register.sh --guard` reconciles plus `00-MASTER/`; `00-CMG/` is not a member and is mapped into VOL-002. The installed `.git/hooks/pre-commit` runs `ucos_ruff_gate` only. `CK-REG-DRIFT` is full-tier; CI runs `--tier standard`.
7. `[F]` **`CMG-INV-10`'s verification predicate is satisfied at HEAD by a run that does not evaluate `CMG-INV-10`.** `XI.10` sets the predicate as *"validator exit status zero with zero findings"*; the validator exits zero; `grep` for `INV-10` returns 0. Under `XLIX.7` this is *unknown compliance*, not satisfaction.
8. `[F]` **Three of the four state-terms supplied for this phase are unlocated** — `CONSTITUTIONALLY-RECONCILED`, `VACANCY-RECORDED`, `FINALITY-WITHHELD` each occur in **0** files; `READY-PROVISIONAL` occurs in **80**. Readiness and certification are distinct instruments and were not conflated.

### CORRECTIONS

`[F]` **To prior determinations: NONE.** Every R0–R3 conclusion R4 tested survived unchanged.

`[F]` **To the phase input, two:**
- The consolidated-state vocabulary is rejected in three of four terms as unlocated (finding 8). The located state is reported per axis in R4.7.
- *"CEP-005 certification exists with cap"* is **not supported at HEAD**. `CMG-REGISTRY.json` carries no certification record and reserves issuance to `CEP-005`. The located records are at a foreign commit on a foreign branch against a dirty tree, and the **full-tier record reads `NOT-CERTIFIED`** with `blocking_failures ["CK-REG-DRIFT"]`. Certification at HEAD is **UNDETERMINED**.

`[I]` **One qualification, not a correction:** R3's *"`check_superiors` … passes by design"* is correct; R4 measures its boundary — the green status is conditional on `located: false`, and the check is defeated by removal of the referent rather than contradiction of it.

### ABSORBED GAPS

| Gap | Absorbed into | Basis / floor impact |
|---|---|---|
| `GAP-R4-01` — Registry collections text-unbound; forged closure passes with `READY` | **META-A**, as an instance of R1-basis roots **R6** and **R7** | NONE / NONE |
| `GAP-R4-03` — `L.2` criteria set and `L.3` procedure enumeration do not correspond | **`GAP-R3-02`**, as a strict refinement one rank deeper | NONE / NONE |

### SURVIVING GAPS

| Gap | Status | Blocking? |
|---|---|---|
| `GAP-R4-02` — `XV.5` names the validator as regenerating agent; `CEP-004 XIV.2`/`XIV.3` forbid it to write | **INDEPENDENT · CONDITIONAL** — live under the WRITE reading, absent under the RECOMPUTE-AND-COMPARE reading; owner reading required for the write half only | **NO** — detection is lawful under both readings |
| `GAP-R4-04` — no certification record exists at HEAD; the located records are stale, from a foreign branch and a dirty tree, and the full-tier record is `NOT-CERTIFIED` | **INDEPENDENT · OBSERVATIONALLY UNAVAILABLE** — resolving it requires executing a check that declares `write_scope: "projections"` | **NO** to determination; the certification **axis** is undetermined |
| `GAP-R3-01`, `GAP-R3-02`, `GAP-R3-03`, `GAP-R3-04` | **CARRIED.** `-02` refined by `GAP-R4-03`; `-03` confirmed and sharpened; `-01` and `-04` untouched | as recorded in R3 |

### BASIS IMPACTS

`[F]` `ROOT-Ω` — unchanged, unmoved. `META-A` — status unchanged, realization scope widened to the 14 text-unbound collections. `META-B` — legal immovability unchanged; **observation qualified**: its record is text-unbound and its complete forgery is undetected. `Floor = 2` — unchanged; three candidate additions tested against R3's deontic-sign, modality and direction-of-repair proofs, zero admitted. **Six-root basis** — unchanged; GAP-R4-01 is a new instance of R6/R7, not a new root. **Unique-basis proof** — unchanged; the one new conflict located is one-sided and touches standing nowhere.

### UNCERTAINTY IMPACTS

`[F]` 6 internally decidable · 4 externally blocked · 4 constitutionally prohibited · 6 observationally unavailable. `[F]` `A-R3-05` partially discharged — the guard's predicate was applied read-only at HEAD (0 dirty lines over four directories); the guard itself was not executed. `[F]` One new class enters the register at R4: **observationally unavailable**, populated by three uncertainties that are unresolved not because the corpus forbids the observation but because the located instrument that would perform it mutates what it measures.

### MAXIMUM ACHIEVABLE STATE

> **READINESS `READY-PROVISIONAL`** (`LXXX.3`, capped by `LXXX.4`) — **attained** · **VACANCY `T1 VACANT`, `VAC-01 located: false`, `XVII.4` (a)(b)(c) discharged, (d) unreached** — **attained** · **FINALITY `PROVISIONAL`, not `FINALIZED`** (`CEP-006 XII.2`, `CMG-L-12`) — **attained** · **CERTIFICATION `CERTIFIED-PROVISIONAL` at most** (`LXXX.7`, `XLIV.5`) — **undetermined at HEAD** · **VALIDATION: all twelve `L.2` criteria realized and the Registry bound to its inputs** — **not attained; ten of twelve realized, 14 of 19 collections unbound.**

`[F]` The readiness **value** is at its ceiling and cannot rise. `[I]` Realizing META-A does not raise it; it changes the value's status from reported-over-two-unevaluated-criteria to evaluated, and makes the PROBE 3 forgery detectable. **Three of four state axes are at maximum. The fourth is undetermined. The validation axis is the only one below maximum, and it is the only one movable from inside.**

### RESIDUAL IRREDUCIBLE SET

> `[F]` **`{ META-A , META-B }` — size 2, unchanged from R3.**
>
> **`META-A`** — the unrealized reconciliation mandate. Deepest locus `XI.10` (`CMG-INV-10`); design law `X.10` (`CMG-L-10`); 18 located clauses across 4 instruments. **IRREDUCIBLE AND MOVABLE.** 63 of 100 live blocking dependents. No external act engaged. Now carrying `GAP-R4-01` as an absorbed instance.
>
> **`META-B`** — `ROOT-Ω`. Deepest locus `XLIV.7`; origin `CEP-000` §5.4; 18 located clauses across ≥6 instruments. **IRREDUCIBLE AND IMMOVABLE.** 37 of 100 live blocking dependents. Zero located transformation paths across all six tested verbs. Its record is text-unbound at HEAD.
>
> **Entailment relation over the set: EMPTY** — unchanged from R3.
>
> **Newly determined relation, not an entailment:** META-A's non-realization governs the **integrity of META-B's observation**. Asymmetric — META-B's vacancy does not expose META-A's mandate. This is a capacity relation between the members, and it leaves both irreducible.

`[I]` The phase's compressed result is a separation the earlier phases had not needed. R3 established that both members are irreducible and that only one is immovable. **R4 establishes that the movable one governs whether the immovable one can be seen.** META-B cannot be removed, transformed, absorbed, superseded, discharged or bypassed by any located clause — and at HEAD its entire visibility rests on one JSON record that no program compares against the constitution that asserts it. The corpus's honesty about the vacancy is real, complete under `XVII.4`, and unenforced. **The one thing the corpus can lawfully do about ROOT-Ω is record it. Nothing at HEAD checks that the record is true.**

**This determination falsifies, exhausts and concedes. It recommends nothing, designs nothing, amends nothing, and eliminates nothing.**

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. HEAD = `1e3e4ba92c121ae3111637d4afbbfd258a5d4896` = the R3 baseline commit; 9 untracked determinations; zero tracked modifications before and after all probes.
2. Validator at HEAD: 86 articles, 80 mandated sections, 44 artifacts, 61 concerns, 1 vacancy, 9 gaps, 7 open questions, **findings 0**, **READY-PROVISIONAL**, **EXIT 0**.
3. `CMG-INV-01` and `CMG-INV-10` have **zero** occurrences in `cmg_validate.py`; `CMG-INV-09` and `CMG-INV-12` have seven; `regenerat*`, `os.walk`, `rglob`, `glob(` all zero.
4. `L.3(a)–(l)` enumerates procedures for eight invariants; `L.2` mandates twelve *"and nothing else"*; the validator implements ten.
5. Registry: 44 artifacts — **32 PROVISIONAL, 11 FROZEN, 1 DECLARED, 0 RATIFIED**; 19 list collections; T1 the sole non-`LOCATED` tier of 8; `VAC-01 located: false`; exactly 4 artifacts declare `superiors: ["VAC-01"]`.
6. PROBE 1 → 1 finding (`IV.11`), NOT-READY, exit 1. PROBE 2 → 4 findings (`CMG-INV-04`), NOT-READY, exit 1. **PROBE 3 → 0 findings, READY, exit 0.**
7. `CEP-004 XIV.2` — *"Validation SHALL NOT write to the subject, to any constitutional corpus, or to any area outside validation records."* `XIV.3` — *"SHALL NOT mutate, delete, or supersede any artifact."* `XXI.3` — validation records *"SHALL NEVER enter the constitutional corpus."*
8. `CMG XV.5` — the Registry *"SHALL be regenerable from repository state alone by the validator of Article L, and a Registry that cannot be regenerated IS invalid."* No program at HEAD regenerates it.
9. `CMG-DLG-15` routes *"Change intelligence, regeneration, and synchronization"* to `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-UCI-001` — an owner distinct from the validator.
10. `EXCLUDE_DIR_PREFIXES` has 13 members including the four `--guard` directories and `00-MASTER/`; `00-CMG/` is not a member and `config.py:320` maps `^00-CMG/` into VOL-002.
11. Installed hooks: `.git/hooks/pre-commit` only, body `ucos_ruff_gate`. `register.sh --guard` is not installed.
12. `CK-CMG` is `tier: boot`, `fail_closed: true`, `advisory: false`; `TIER_ORDER` places boot ≤ standard, so it is in scope for `uccep-gate.yml`'s `--tier standard` on push and PR. `CK-REG-DRIFT` is `tier: full`, `write_scope: "projections"`.
13. Located certification records: standard tier `CERTIFIED-PROVISIONAL` at `head 527485abf`, branch `programme/evo-usis-005`, tree `DIRTY`; **full tier `NOT-CERTIFIED`, `gate_exit 1`, `blocking_failures ["CK-REG-DRIFT"]`**. None at HEAD.
14. `CEP-007 IV.1` conditions freeze eligibility on `RATIFIED`; the `RATIFIED` count is 0.
15. `CONSTITUTIONALLY-RECONCILED`, `VACANCY-RECORDED`, `FINALITY-WITHHELD`: **0 files each**. `READY-PROVISIONAL`: 80 files.
16. `XVII.4` (a)(b)(c) discharged in the Registry; (d) unreached because `located: false`.

### INFERENCES `[I]`
1. **A shared record is not a checked record.** The corpus's compliance with `XVII.4` is complete and its verification is absent. Recording and reconciling are different acts, and only the first is realized.
2. **META-A governs the integrity of META-B's observation, asymmetrically.** This is a capacity relation, not an entailment; R3's empty entailment relation stands.
3. **Forged closure is an instance, not a cause.** It shares META-A's deontic sign, modality and repair direction, is grounded in no clause outside META-A's 18, and carries no dependent META-A cannot explain.
4. **`GAP-R4-02` dissolves under the reading `L.6` supports**, and the detection half of META-A is lawful under both readings, so no located clause blocks META-A's discharge.
5. **The readiness ceiling is not the constraint on META-A.** Realizing META-A leaves the outcome value at `READY-PROVISIONAL` and changes only its epistemic status.
6. **The exit status is uninformative in both directions** about the two invariants it never evaluates — it passed the honest state at HEAD and would equally have passed PROBE 3.
7. **A new uncertainty class appears at R4: observationally unavailable** — the instrument that would resolve it mutates what it measures.
8. **R4 found nothing that changes the basis.** Three candidates tested, zero admitted; the floor holds for the same reason R3 gave — the corpus contains two categorially different kinds of law, and the basis holds one of each.

### ASSUMPTIONS `[A]`
`A-R4-01` The 63 / 37 partition of 100 live blocking dependents is carried from R1 and R2 and was not re-derived in this phase.
`A-R4-02` The 18 + 18 governing clause sets are carried from R3, assembled by pattern sweep plus targeted reading (`= A-R3-01`, inherited unchanged).
`A-R4-03` The 5 text-bound / 14 unbound split is read from the sixteen check-function bodies; the collection count 19 was independently re-derived, the split was not executed as a differential.
`A-R4-04` `AUTH-02/03/04/06`, `Ω-010` and `CM-007` are quoted from derived reports; no primary normative text was located, consistent with `VAC-01.evidence` placing the referent in frozen `.docx` source.
`A-R4-05` PROBE results establish the behaviour of the Article L validator only. No other gate was executed against the forged registry.
`A-R4-06` Measured at `1e3e4ba9` in this environment.

### GAPS `[GAP]`
| Id | Gap | Disposition |
|---|---|---|
| `GAP-R4-01` | Registry `vacancies`, `open_questions` and `readiness` collections are text-unbound; complete forged closure passes with `READY` | **ABSORBED into META-A** (instance of R6/R7) |
| `GAP-R4-02` | `XV.5` names the Article L validator as regenerating agent; `CEP-004 XIV.2`/`XIV.3`/`XXI.3` forbid that write; `CMG-DLG-15` names a different regeneration owner; no located instrument allocates the duty | **SURVIVING · INDEPENDENT · CONDITIONAL · NON-BLOCKING** |
| `GAP-R4-03` | `L.2`'s criteria set and `L.3`'s procedure enumeration do not correspond: 2 mandated-unimplemented, 2 unenumerated-implemented | **ABSORBED into `GAP-R3-02`** as a refinement |
| `GAP-R4-04` | No certification record exists at HEAD; located records are stale, foreign-branch, dirty-tree; full-tier record is `NOT-CERTIFIED` | **SURVIVING · INDEPENDENT · OBSERVATIONALLY UNAVAILABLE** |
| `GAP-R3-01` … `GAP-R3-04` | carried from R3 | `-02` refined · `-03` confirmed and sharpened · `-01`, `-04` untouched |

### UNKNOWNS `[UNKNOWN]`
`UNK-R4-01` Which reading of `XV.5` governs — WRITE or RECOMPUTE-AND-COMPARE. Internally decidable; owner reading required; `L.6` supplies the disposition rule but not the reading.
`UNK-R4-02` The certification state at HEAD. Observationally unavailable — `CK-REG-DRIFT` declares `write_scope: "projections"`.
`UNK-R4-03` Whether regeneration of `CMG-REGISTRY.json` reproduces the committed bytes. No regenerator exists; unmeasurable at HEAD without writing.
`UNK-R4-04` Whether any gate outside the Article L validator would detect the PROBE 3 forgery. Only the CMG gate was executed against it.
`UNK-R3-01` … `UNK-R3-05` carried unchanged; `UNK-R3-02` and `UNK-R3-03` gained located evidence in R4; `UNK-R3-05` deliberately not pursued under the bar on new root hunting.

---

*PHASE R4 · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`READY-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Reproduce: `python3 00-CMG/tools/cmg_validate.py --repo-root .` · `bash 00-CMG/tools/cmg-gate.sh` · counterfactual probes on an isolated copy of `00-CMG/` only.*
