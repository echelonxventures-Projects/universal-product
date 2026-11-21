# PHASE R5 — META-A TRANSFORMATION CAPACITY EXHAUSTION AND STATE-SPACE DETERMINATION

| Field | Value |
|---|---|
| AUTHORITY | **NONE (DERIVED TRUTH)** — CMG-000001 XII.6 governs the standing of this document |
| HEAD | `1e3e4ba92c121ae3111637d4afbbfd258a5d4896`, branch `integration/recovery-001` |
| BASELINE | PHASE R3 (irreducibility, floor 2) · PHASE R4 (META-A movable, META-B immovable, META-A governs META-B's observability) |
| METHOD | Locate exhaustively · compute the counterfactual · assert nothing that requires implementation to know |
| MODALITY | **COUNTERFACTUAL.** Nothing was implemented. No clause was realized. The corpus is unchanged |
| CLASSIFICATION | `[F]` measured · `[I]` inferred · `[A]` assumption · `[GAP]` · `[UNKNOWN]` |
| RESULT | **META-A CORPUS UNDER-CAPTURED BY R3 · DISCHARGE CHANGES 11 STATE VARIABLES AND NO AXIS CEILING · META-B BECOMES RECOMPUTABLE AND NO LESS BINDING · ROOT-Ω UNCHANGED IN FORCE · FLOOR-2 NOT FALSIFIED BUT VACATED** |

---

## R5.0 — METHOD, AND THE ONE THING R5 CANNOT KNOW

`[I]` Stated first because it bounds every determination below.

**`[F]` R5 did not implement `CMG-INV-01` or `CMG-INV-10`.** Therefore R5 **cannot** determine whether full META-A discharge yields zero findings at HEAD. Realizing a corpus-wide recognition check and a recomputability check would either confirm the present Registry or contradict it, and which of those obtains is not derivable from located text — it is derivable only by running the check that does not exist.

`[F]` Consequently every statement below is of one of exactly two kinds, and they are marked throughout:
- **CEILING statements** — what the located clauses permit the state to become. Determinable now.
- **OCCUPANCY statements** — whether HEAD would actually reach that ceiling. **`[UNKNOWN]`** where it depends on an unrun check.

`[I]` R3's `WORLD-A` asserted occupancy — *"Registry regenerable and regenerated; 19 of 19 collections text-bound; 44 of 44 artifacts in the registration universe"*. **R5 downgrades that to a ceiling statement.** It is what discharge permits, not what discharge is measured to produce. This is recorded as a **correction of modality, not of content**, in R5.10.

---

## R5.1 — THE COMPLETE LOCATED META-A CORPUS

### `[F]` FINDING: R3's 18-clause set was under-capture. `UNK-R3-01` is answered in the negative.

`[F]` An exhaustive sweep of `CMG-000001` on the operative verbs (`reconcil*`, `recomput*`, `regenerat*`, `byte-identical`, `drift`) plus a full read of all 14 design laws (`X.1`–`X.14`) and all 12 invariants (`XI.1`–`XI.12`) located **42 clauses in `CMG-000001` alone**, against R3's 18 across four instruments. **Fourteen were not in R3's set.** R3's own `A-R3-01` admitted this was possible; R5 measures it.

`[A]` `A-R5-01` — the tiering below (CORE / CONSTITUTIVE / CONSEQUENTIAL) is **derived, not located.** `GAP-R3-01` stands: no located instrument classifies constitutional obligations by type, so the boundary of "META-A's corpus" is a judgment about scope, not a reading. The clause list is located; its partition is not.

### TIER 1 — CORE: the reconciliation and recomputability mandate itself

| # | Clause | Category | Located text (operative fragment) | In R3's 18? |
|---|---|---|---|---|
| 1 | `X.10` **CMG-L-10** | design law | *"Every meta-constitutional assertion SHALL be bound to evidence under CEP-008 and SHALL be recomputable from repository state alone."* | ✔ |
| 2 | `XI.10` **CMG-INV-10** | invariant · validator criterion | *"Every assertion of this instrument is recomputable from repository state by the validator of Article L. Verification: validator exit status zero with zero findings."* | ✔ |
| 3 | `X.1` **CMG-L-01** | design law | *"An artifact SHALL exercise constitutional force only while it is recognized in the Constitution Registry."* | ✔ |
| 4 | `XI.1` **CMG-INV-01** | invariant · validator criterion | *"Verification: registry membership equals the set of artifacts cited as constitutional authority **anywhere in the corpus**."* | ✔ |
| 5 | **`VII.7`** | authority-binding · reconciliation duty | *"Meta governance SHALL be **evidence-bound**. Every allocation, recognition, precedence rank, and **vacancy** SHALL be recorded as evidence under CEP-008 and SHALL be reproducible from the repository alone. **A meta-governance claim that cannot be recomputed from repository state IS not a claim but an opinion.**"* | **✘ NEW** |
| 6 | `II.4` | regeneration duty | *"Where the derived form and the canonical form disagree, the canonical form governs and the derived form SHALL be regenerated."* | ✔ |
| 7 | `XV.3` | projection requirement | *"It IS a **projection over existing stores** … Where the projection and an input disagree, the input governs."* | ✔ |
| 8 | `XV.5` | regeneration duty · registry rule | *"The Registry SHALL be **recomputable** … regenerable from repository state alone by the validator of Article L, and a Registry that cannot be regenerated IS invalid."* | ✔ |
| 9 | `XII.6` | reconciliation duty | *"Derived truth SHALL always be reconciled against repository reality…"* | ✔ |
| 10 | `LXXXIII.9` | reconciliation duty | *"Every assertion of this instrument SHALL be recomputable from repository state alone…"* | ✔ |
| 11 | `LIII.3` | traceability requirement | *"…recomputable from repository state rather than captured as a narrative. Where an assertion cannot be recomputed, it SHALL be recorded as a judgement with a named accountable authority, not as evidence."* | ✔ |
| 12 | `LX.2` | projection requirement | *"Generated output IS derived truth and SHALL be reconciled against its constitutional input; where they disagree, the input governs."* | ✔ |
| 13 | `LXXIV.6` | regeneration duty | *"Recovery of derived truth … SHALL be by regeneration from canonical sources, never by restoring a stale copy. A restored derived store that disagreeing with its sources IS a drift defect."* | ✔ |
| 14 | `XXVII.5` | reconciliation duty | *"…resolved from the artifact's declaration reconciled against the located registries, and irreconcilable inputs produce a finding rather than a guess."* | ✔ |
| 15 | `XXV.3` | reconciliation duty | *"Where the located model and this mapping disagree, the located model governs and this mapping SHALL be corrected by amendment."* | ✔ |

### TIER 2 — CONSTITUTIVE: the verification apparatus META-A is realized in

| # | Clause | Category | Operative fragment | In R3's 18? |
|---|---|---|---|---|
| 16 | `L.2` | validator criterion | *"The criteria SHALL be CMG-INV-01 through CMG-INV-12 and nothing else."* | ✘ (R4) |
| 17 | `L.3(a)–(l)` | validator criterion · routing | *"Its realization IS `00-CMG/tools/cmg_validate.py`, which SHALL: …"* — enumerates 8 invariants | ✘ (R4) |
| 18 | `L.4` | validator criterion | *"fail-closed: an unparseable input, a missing file, or an ambiguous record SHALL produce a finding, never a pass."* | ✘ (R4) |
| 19 | **`L.5`** | validator criterion | *"deterministic and hermetic: identical repository state SHALL produce **byte-identical output**…"* | **✘ NEW** |
| 20 | **`L.6`** | validator criterion | *"The validator IS derived-truth (XII.6) … **it recomputes what this instrument already declares.**"* | **✘ NEW** |
| 21 | `L.7` | validator criterion | *"SHALL NOT duplicate any check already performed by a located gate … SHALL bind to it."* | ✘ (R4) |
| 22 | `XLIX.7` | validator criterion | *"Compliance SHALL NOT be assumed from the absence of a check. An unchecked obligation IS of unknown compliance…"* | ✔ |
| 23 | **`LXXIX.1`** | validator criterion | *"**Completeness** … SHALL mean: no open gap within jurisdiction, no undelegated residue, **no unrecorded vacancy**, no unrecorded open question, and **all twelve invariants satisfied.**"* | **✘ NEW** |
| 24 | **`LXXIX.4`** | validator criterion · routing | *"Completeness verification SHALL be **mechanical** and SHALL be realized by the validator of Article L. A completeness claim not produced by the validator IS an assertion, not a verification."* | **✘ NEW** |
| 25 | **`LXXIX.5`** | validator criterion | *"…SHALL be **re-run on every change** … A completeness result IS valid only for the repository state that produced it."* | **✘ NEW** |
| 26 | **`LXXIX.2`** | validator criterion | four questions per artifact, *"each answerable deterministically from recorded fact"* | **✘ NEW** |
| 27 | `LXVI.1` | authority-binding | *"Every constitutional obligation that IS deterministically checkable SHALL be checked by automation, and the automated check SHALL be **unskippable**."* | ✘ (R4) |
| 28 | `LXVI.2` | authority-binding | *"fail-closed: a check that cannot run SHALL block, never pass."* | ✘ (R4) |
| 29 | `LXVI.5` | authority-binding | configuration-driven; no hard-coded enumeration | ✘ (R4) |
| 30 | `LXVI.7` | routing | *"exactly one gate — the validator of Article L…"* | ✘ (R4) |
| 31 | `XI.13` | **constraint** | *"The invariant set IS CLOSED for version 1.0 … extensible by amendment only."* | ✘ (R4) |
| 32 | `LII.1` | routing | *"**Audit operation** — drift detection, contradiction detection … IS located and owned"* → `CMG-DLG-11` → `CEP-010` | **✘ NEW** |
| 33 | **`LXXXIV.9`** | routing | the located enforcement chain, delegated at `CMG-DLG-40`, bound at `LXVI.4`/`LXVI.7` | **✘ NEW** |

### TIER 3 — CONSEQUENTIAL: drift, traceability, projection and generator duties that inherit from the mandate

| # | Clause | Category | Operative fragment | In R3's 18? |
|---|---|---|---|---|
| 34 | **`VII.3`** | reconciliation duty | *"The residue SHALL be **computed, not assumed** … Article LXXIX requires its recomputation on every change."* | **✘ NEW** |
| 35 | **`VIII.1`** | reconciliation duty | *"**Knowledge Once** … Restatement is duplication, duplication is drift, and drift is constitutional failure."* | **✘ NEW** |
| 36 | **`XXXVII.6`** | traceability requirement | *"Traceability SHALL be **reproducible**: recomputing the trace from repository state SHALL yield an identical result. A non-reproducible trace IS not evidence."* | **✘ NEW** |
| 37 | **`XLVIII.4`** | traceability requirement | *"Distribution SHALL be **drift-detectable**: every distributed copy SHALL be verifiable against its source **by content hash**, and a divergence SHALL be a finding under Article LII."* | **✘ NEW** |
| 38 | **`XXXVI.6`** | projection requirement | *"An impact analysis SHALL cover non-artifact impact …: registries, projections, validators, gates, generators … Omitting machinery from impact analysis is the most common cause of silent governance drift."* | **✘ NEW** |
| 39 | **`XXXIII.3`** | registry rule | *"An identifier issued in an unrecorded namespace IS provisional and SHALL be **reconciled or voided**."* | **✘ NEW** |
| 40 | **`LX.5`** | projection requirement | *"A generator SHALL NOT embed constitutional content in its own code … Embedded rules are copies and will drift."* | **✘ NEW** |
| 41 | **`LX.6`** | projection requirement | *"…affected generated output SHALL be **regenerated or explicitly classified UNAFFECTED**."* | **✘ NEW** |
| 42 | `III.6` / `XVI.1` | projection requirement | the single Precedence Lattice reconciling the corpus's disjoint precedence statements | **✘ NEW** |

### Cross-instrument members `[F]` — verified verbatim in this phase

| Instrument | Clause | Text | Prior status |
|---|---|---|---|
| `CEP-008` | `XVI.3` | *"The registries SHALL be append-only, content-addressed, and reconciled against repository truth at boot."* | cited by R3, **read here for the first time — accurate** |
| `CEP-008` | `XXI.1` | *"On every boot, evidence and traceability state SHALL be reconciled against repository truth through the general Recovery Model of CEP-001 Article XXI, and **repository truth SHALL prevail on divergence**."* | cited by R3, **read here — accurate** |
| `CEP-004` | `X.1` | *"Determinism validation SHALL verify that reproducible outputs of the subject **regenerate byte-identically**, referencing CEP-001 Article XX."* | cited by R3, **read here — accurate** |
| `CEP-004` | `XV.3` | *"Validation checkpoints SHALL be append-only and content-addressed and SHALL be reconciled against repository truth at boot."* | cited by R3, **read here — accurate** |
| `CEP-004` | `XIV.1`–`XIV.4`, `XXI.3` | the validation permission set — read-only plus validation records; corpus writes prohibited and void | located in R4 (`GAP-R4-02`) |
| `CEP-001` | `Art. XVIII`, `XX`, `XXI` | traceability closure · determinism · Recovery Model | consumed by reference; **not read** (`A-R5-02`) |

`[F]` **Located META-A corpus: 42 clauses in `CMG-000001` + 6 verified cross-instrument clauses + 3 consumed by reference = 51, against R3's 18.** `[I]` R3's set was correct in every member and incomplete in extent. No R3 citation failed verification.

`[I]` **The single most consequential new location is `VII.7`.** It places *vacancy* — VAC-01, which is META-B's entire footprint in the repository — expressly inside META-A's reproducibility mandate, and supplies the corpus's own word for a non-recomputable meta-governance claim: **"not a claim but an opinion."** R4 inferred that META-A governs META-B's observability. `VII.7` states it as located law.

---

## R5.2 — TRANSFORMATION GRAPH

`[F]` The graph below moves only variables for which a located clause fixes the value, and marks every variable whose post-state is not derivable without running the unrun check.

```
                         HEAD (measured)                    HEAD + META-A FULLY DISCHARGED
                                                            (ceiling permitted by located clauses)
────────────────────────────────────────────────────────────────────────────────────────────────────
VALIDATION APPARATUS
 v1  invariants evaluated by validator      10 of 12    ──▶  12 of 12                    [CEILING]
 v2  CMG-INV-01 in cmg_validate.py          absent (0)  ──▶  present                     [CEILING]
 v3  CMG-INV-10 in cmg_validate.py          absent (0)  ──▶  present                     [CEILING]
 v4  corpus walk (os.walk/rglob/glob)        0          ──▶  required by XI.1's own
                                                             verification ("anywhere in
                                                             the corpus")                [CEILING]
 v5  registry collections text-bound         5 of 19    ──▶  19 of 19                     [CEILING]
 v6  XLIX.7 status of INV-01 / INV-10        "unknown   ──▶  evaluated                    [CEILING]
                                             compliance"
REGISTRY TRUTH
 v7  Registry validity under XV.5            INVALID    ──▶  VALID                        [CEILING]
     ("a Registry that cannot be              (no regenerator exists at HEAD)
      regenerated IS invalid")
 v8  vacancy record status under VII.7        "opinion"  ──▶  "claim"                      [CEILING]
     (VII.7's own vocabulary)
 v9  PROBE-3 forged closure                  UNDETECTED ──▶  DETECTED                      [CEILING]
     (findings 0, READY, exit 0)                             (XV.3 "the input governs" +
                                                              XI.1 corpus-wide citation set)
COMPLETENESS
 v10 LXXIX.1 completeness                    NOT         ──▶  ESTABLISHABLE                [CEILING]
     ("all twelve invariants satisfied")      established        (LXXIX.1 requires the vacancy
                                                                  be RECORDED, not CLOSED)
 v11 LXXIX.4 completeness claim status        "assertion" ──▶  "verification"               [CEILING]

FINDINGS
 v12 validator findings                       0          ──▶  ***UNKNOWN***                [OCCUPANCY]
                                                              0 if the corpus confirms the
                                                              Registry; >0 if it contradicts it.
                                                              Not derivable without the check.
────────────────────────────────────────────────────────────────────────────────────────────────────
UNCHANGED BY DISCHARGE — every one fixed by a META-B clause, not a META-A clause
 u1  T1 occupancy                    VACANT              ──▶  VACANT          (XVII.4, XVI.2)
 u2  VAC-01.located                   false              ──▶  false           (XLIV.7, LXXXIII.4)
 u3  XVII.4 step (d)                  unreached          ──▶  unreached       (antecedent external)
 u4  artifacts RATIFIED               0 of 44            ──▶  0 of 44         (CEP-006 XII.2)
 u5  finality state                   PROVISIONAL        ──▶  PROVISIONAL     (CMG-L-12)
 u6  readiness outcome VALUE          READY-PROVISIONAL  ──▶  READY-PROVISIONAL (LXXX.4)
 u7  certification ceiling            CERTIFIED-PROV.    ──▶  CERTIFIED-PROV. (LXXX.7, XLIV.5)
 u8  freeze eligibility               INELIGIBLE         ──▶  INELIGIBLE      (CEP-007 IV.1: RATIFIED)
 u9  CMG-OQ-01/02/03/07               OPEN               ──▶  OPEN            (EXPLICIT RATIFICATION)
 u10 externality class of META-B      PROHIBITED         ──▶  PROHIBITED      (R4.4)
```

`[F]` **11 state variables change. 10 do not. No axis ceiling moves.**

`[I]` The graph's shape is the phase's central result: **every variable that discharge moves is epistemic — what is checked, what is bound, what is recomputable, what is detectable. Every variable it leaves fixed is deontic — what standing is held, what is ratified, what is final.** Discharge converts unverified assertions into verified ones. It confers nothing.

---

## R5.3 — DIRECT EFFECTS ON DEPENDENTS

`[A]` `A-R5-03` — the 63 / 37 partition of 100 live blocking dependents is carried from R1/R2 and was not re-derived (inherits `A-R4-01`).

| Dependent | Effect | Located basis |
|---|---|---|
| **META-A's 63 live blocking dependents** — R1-basis roots R3, R4, R6, R7, R8 and their dependents; `CE-01`, `SOUND-01/02`, `FP-01…05`, `DIV-*`, `BS-01…12` | **DISCHARGED — at ceiling; `[UNKNOWN]` in occupancy** | R2 maps all 63 to META-A. Discharge realizes the mandate they depend on. **Whether each individual dependent clears depends on what the check finds** (`v12`) |
| **META-B's 37 live blocking dependents** — `VAC-01`, `CMG-GAP-04`, `CMG-OQ-01/02/03/07`, `DEF-02`, `UCCEP-F-004`, `UCAF-RC-01/02/03`, 5 `URAT` records, `B-10…13`, `UD-01…06` | **UNCHANGED in force · REVEALED in evidence** | Each is fixed by a META-B clause. None is a reconciliation duty. `VII.7` makes their *records* recomputable without making any of them dischargeable |
| `GAP-R4-01` — Registry collections text-unbound; forged closure passes with `READY` | **REVEALED, then DISCHARGED** | `v5` + `v9`. `VII.7` and `XV.3` are the clauses that bind it; both are Tier-1 META-A |
| `GAP-R4-03` / `GAP-R3-02` — `L.2` vs `L.3` enumeration mismatch | **REDUCED, not discharged** | The *invariant* leg closes (`v1`: 12 of 12). The *design-law* leg survives: `XLIX.5` routes `CMG-L-01…14` to the validator while `L.2` restricts criteria to the invariants. 11 of 14 design laws remain unrealized |
| `GAP-R3-03` — reconciliation on the generated layer, absent on the constitutional layer, unrecorded as a decision | **REDUCED** | The substantive half closes: reconciliation would extend to `00-CMG/`. The recording half survives — no located instrument records the `EXCLUDE_DIR_PREFIXES` boundary as a decision |
| `GAP-R4-02` — `XV.5` names the validator; `CEP-004 XIV.2`/`XIV.3` forbid it to write | **UNCHANGED, and made operative** | Discharge is the moment the reading matters. Under RECOMPUTE-AND-COMPARE it stays dissolved; under WRITE it becomes a live conflict at the point of action |
| `GAP-R4-04` — no certification record at HEAD; full-tier record `NOT-CERTIFIED` on `CK-REG-DRIFT` | **UNCHANGED** | Discharging a validation duty issues no certification. `LXXX.5` reserves issuance to `CEP-005` |
| `GAP-R3-01` — no located taxonomy of obligations by deontic sign | **UNCHANGED** | No META-A clause creates a taxonomy |
| `GAP-R3-04` — no entailment register between meta-causes | **UNCHANGED** | Inherited from `GAP-R1-01`; no META-A clause creates one |
| `XI.10`'s circular verification predicate | **STRENGTHENED** | At HEAD *"validator exit status zero with zero findings"* is satisfied by a run that never evaluates `CMG-INV-10`. Post-discharge the predicate contains its own subject and becomes non-vacuous |
| `LXXIX.1` completeness | **DISCHARGED at ceiling** | Requires *"no **unrecorded** vacancy"* — not *no vacancy*. A recorded VAC-01 is compatible with completeness. The only unmet conjunct at HEAD is *"all twelve invariants satisfied"* |
| **Nothing is HIDDEN** | — | `[F]` No located META-A clause removes, suppresses or narrows an existing check. `L.7` binds rather than duplicates; `LXVI.1` makes checks *unskippable*; `XLIX.7` forbids presuming compliance from absence. The classification **HIDDEN is empty** |

---

## R5.4 — INDIRECT EFFECTS: OBSERVABILITY DELTA

| Object | Observability at HEAD | Under discharge | Located basis |
|---|---|---|---|
| `00-CMG/CMG-REGISTRY.json` | derived, unregenerated, **INVALID by `XV.5`'s own terms**, 14 of 19 collections compared to nothing outside themselves | bound to its declared inputs; divergence emits a finding | `XV.3`, `XV.5`, `II.4` |
| `vacancies[VAC-01]` | text-unbound; deletion + superior-repointing passes | reproducible from the corpus; contradiction with `XVII.4`/`XVI.2`/`LXXXI.5` detectable | **`VII.7`**, `XV.3`, `XI.1` |
| `open_questions[]` | text-unbound; mass closure passes | bound; `LXXXVI.4`'s enumeration of five open becomes a checkable assertion | `VII.7`, `XV.3` |
| `readiness.declared_ceiling` | text-unbound; `READY` accepted in PROBE 3 | bound to `LXXX.4` | `XV.3`, `LXXX.4` |
| `artifacts[]` — 44 entries | **no content-hash field exists on any entry** (`[F]` field census: 12 fields, zero hash-like) | content-addressed binding becomes checkable | `CEP-008 XVI.3` (*content-addressed*), `XLVIII.4` (*by content hash*), `CEP-008 IV.1` |
| `concerns[]` — 61 | `CMG-INV-03` total and passing over the recorded set | totality checkable against concerns cited corpus-wide | `XI.1`, `VII.3` |
| lifecycle states — 32 PROVISIONAL, 11 FROZEN, 1 DECLARED, **0 RATIFIED** | `CMG-INV-07` checks membership in the declared state set | membership plus reconciliation against the located registries | `XXVII.5`, `XI.7` |
| readiness state | computed by `readiness()`; value correct, inputs unverified | same value, verified inputs | `LXXIX.4`, `LXXX.3` |
| certification state | **UNDETERMINED at HEAD** — records at `head 527485abf`, foreign branch, DIRTY tree; full tier `NOT-CERTIFIED` | **still UNDETERMINED.** Discharge issues no certification | `LXXX.5`, `GAP-R4-04` |
| authority state — T1 | `VACANT`, recorded, unverified | `VACANT`, recorded, **verified** | `VII.7`, `XVII.4` |
| vacancy state | 1 recorded; `located: false` | 1 recorded, recomputable | `VII.7` |
| finality state | `PROVISIONAL`, not `FINALIZED` | unchanged | `CEP-006 XII.2` |
| traceability | `XXXVII.6` requires reproducible traces; no located recomputation for the meta layer | reproducible-trace duty realized | `XXXVII.6`, `CEP-008 XXI.1` |
| the four `superiors: ["VAC-01"]` artifacts — `CMG-000001`, `CEP-000`, `AUTH-INF-001`, `UCKP-LAW-0001` | resolve because a vacancy record exists | resolve, **and the record is verified** | `XI.4`, `LXXXIII.4` |
| `cmg_validate.py` output | `L.5` byte-identity asserted in docstring; **no double-build check for the meta layer** (`determinism.yml` subject is `BP-DATA-0001`) | `L.5` becomes checkable | `L.5`, `CEP-004 X.1` |

`[I]` The pattern across every row: **the value does not change; the warrant does.** Discharge alters no recorded state. It makes the record answerable to the corpus that the record purports to project.

---

## R5.5 — EFFECT ON META-B

`[F]` Determined without assuming elimination. META-B is not eliminated, reduced, or weakened by any row below.

| Property | Determination | Support |
|---|---|---|
| **MORE OBSERVABLE** | **`[F]` YES.** At HEAD META-B's entire footprint is one text-unbound JSON record whose complete forgery passes with `findings 0`, `READY`, `exit 0` (PROBE 3). Under discharge that forgery is detectable | `VII.7` (*vacancy … reproducible from the repository alone*); `XV.3` (*the input governs*); `XI.1` (*cited … anywhere in the corpus*); PROBE 1/2/3 |
| **LESS OBSERVABLE** | **`[F]` NO.** No located META-A clause narrows a check. `L.7` binds rather than duplicates; `LXVI.1` requires unskippability | `L.7`, `LXVI.1`, `XLIX.7` |
| **NEWLY MEASURABLE** | **`[F]` YES.** `VII.7` makes the vacancy record a reproducibility subject. `LXXIX.1`'s *"no unrecorded vacancy"* becomes a verified conjunct rather than an asserted one | `VII.7`, `LXXIX.1`, `LXXIX.4` |
| **NEWLY BOUNDED** | **`[F]` YES.** `LXXX.4`'s ceiling — *"READY-PROVISIONAL at most … SHALL NOT be READY"* — is a text assertion at HEAD and `declared_ceiling` is unbound (PROBE 3 raised it to `READY` undetected). Under discharge the ceiling becomes enforced against its own source | `LXXX.4`, `XV.3` |
| **NEWLY TRACEABLE** | **`[F]` YES.** `XXXVII.6` requires reproducible traces and `CEP-008 XVI.3`/`XXI.1` require registries content-addressed and reconciled at boot with *"repository truth SHALL prevail on divergence."* The 44 artifact entries carry **no content-hash field at all**; discharge brings the vacancy's evidence chain under a reproducible trace | `XXXVII.6`, `XLVIII.4`, `CEP-008 XVI.3`, `XXI.1` |
| **UNCHANGED — force** | **`[F]` YES, wholly.** `XLIV.7`, `CEP-000 §5.4`, `X.4`, `IX.16`, `VI.4`, `LXXXIII.3`, `LXXXI.6`, `XVII.4`, `LV.4`, `LV.5`, `CEP-006 XII.2`, `CEP-007 IV.1` — none is a reconciliation duty; none is touched | R4.4 verb table, zero permissive entries |
| **UNCHANGED — dependents** | **`[F]` YES.** All 37 remain live | R2 partition |
| **ENTRENCHED** | **`[F]` YES.** R3.0's direction-of-repair result is reconfirmed at finer grain: enforcement makes the prohibition *detectable*, hence harder to breach. `[I]` A vacancy that cannot be silently closed is more binding than one that can | R3.0; PROBE 3 |

`[I]` **The precise statement, in the corpus's own vocabulary.** `VII.7`: *"A meta-governance claim that cannot be recomputed from repository state IS not a claim but an opinion."* At HEAD the assertion *"Tier T1 is VACANT"* is recorded in a register that nothing recomputes — by `VII.7`'s own terms, an opinion. Under full META-A discharge it becomes a claim. **META-B's content does not change; its epistemic status does — from unverified record to verified claim — and its bindingness rises rather than falls.**

---

## R5.6 — EFFECT ON ROOT-Ω

`[F]` Determined without assuming elimination. Every consequence of ROOT-Ω was tested against the located META-A corpus.

| Consequence of ROOT-Ω | Changes under full META-A discharge? | Basis |
|---|---|---|
| A corpus cannot confer on itself the standing it lacks | **NO** | `CEP-000 §5.4`; no META-A clause confers standing |
| T1 remains VACANT | **NO** | `XVII.4`; `u1` |
| Self-ratification prohibited | **NO** | `XLIV.7` |
| Standing capped at PROVISIONAL | **NO** | `X.12` `CMG-L-12` |
| `FINALIZED` reserved to the out-of-corpus act | **NO** | `CEP-006 XII.2` |
| Freeze ineligible for want of `RATIFIED` | **NO** | `CEP-007 IV.1`; `u8` |
| Readiness capped at `READY-PROVISIONAL` | **NO** | `LXXX.4`; `u6` |
| `CMG-OQ-01/02/03/07` require `EXPLICIT RATIFICATION` | **NO** | registry `requires` field; `u9` |
| Licensed action set = record, record, refer, re-run | **NO** | `XVII.4` (a)–(d) |
| Externality class = PROHIBITED | **NO** | R4.4 |
| The 37 dependents | **NO** | R2 partition |
| **The evidentiary status of every one of the above** | **`[F]` YES** | `VII.7` — each is a meta-governance claim, and each becomes recomputable |
| **Detectability of a forged discharge of any of the above** | **`[F]` YES** | PROBE 3 → detected under `v9` |

`[F]` **No consequence of ROOT-Ω changes in force. Exactly two things change: whether its consequences are recomputable, and whether their forgery is detectable.**

`[I]` `LXXXI.6`'s self-referential foreclosure — *"it SHALL NOT confer standing on itself **by operation of any clause herein**"* — is dispositive here and needs no counterfactual reasoning. It forecloses conferral by **any** clause of the instrument, which necessarily includes the 42 META-A clauses located in R5.1. Discharging clauses that cannot confer standing cannot confer standing. **ROOT-Ω is unmoved by construction, not merely by measurement.**

---

## R5.7 — MAXIMUM ACHIEVABLE STATE-SPACE

`[F]` Located vocabulary only. Unlocated terms rejected in R4.7 (`CONSTITUTIONALLY-RECONCILED`, `VACANCY-RECORDED`, `FINALITY-WITHHELD` — 0 occurrences each) remain rejected and are not reintroduced.

| Axis | Located vocabulary | **HEAD** | **HEAD + META-A fully discharged** | Ceiling moves? |
|---|---|---|---|---|
| **VALIDATION** | `CMG-INV-01`…`12`; `L.2` *"and nothing else"* | 10 of 12 evaluated; `-01` and `-10` absent; `XLIX.7` *unknown compliance* | **12 of 12 evaluated** | **`[F]` YES — this is the only axis that moves** |
| **REGISTRY VALIDITY** | `XV.5` — *"a Registry that cannot be regenerated IS invalid"* | **INVALID** by its own terms | **VALID** | **`[F]` YES** |
| **COMPLETENESS** | `LXXIX.1` — *"no unrecorded vacancy … all twelve invariants satisfied"* | **NOT ESTABLISHED**; sole unmet conjunct is the twelve invariants | **ESTABLISHABLE** — a *recorded* vacancy is compatible | **`[F]` YES** |
| **COMPLETENESS CLAIM STATUS** | `LXXIX.4` — *"a completeness claim not produced by the validator IS an assertion, not a verification"* | **ASSERTION** | **VERIFICATION** | **`[F]` YES** |
| **READINESS** | `LXXX.3` `{READY, READY-PROVISIONAL, NOT-READY}` | `READY-PROVISIONAL` | `READY-PROVISIONAL` | **`[F]` NO — `LXXX.4` caps it while `CMG-OQ-01`/`-02` are open** |
| **VACANCY** | `occupancy ∈ {LOCATED, VACANT}`; `located: false` | `T1 VACANT`; `XVII.4` (a)(b)(c) discharged, (d) unreached | identical, **and recomputable** | **`[F]` NO** |
| **FINALITY** | `{ACCEPTED, PROVISIONAL, DEFERRED, REJECTED, FINALIZED}` | `PROVISIONAL`; `RATIFIED` count 0 | identical | **`[F]` NO — `CEP-006 XII.2`** |
| **CERTIFICATION** | `{CERTIFIED-PROVISIONAL, NOT-CERTIFIED}`; ceiling per `LXXX.7`, `XLIV.5` | **UNDETERMINED at HEAD** | **still UNDETERMINED** — discharge issues no certification | **`[F]` NO** |
| **FREEZE** | `CEP-007 IV.1` — `VALIDATED` ∧ `CERTIFIED` ∧ `RATIFIED` | **INELIGIBLE** — `RATIFIED` = 0 | **INELIGIBLE** | **`[F]` NO** |

### `MAXIMUM-ACHIEVABLE-STATE-SPACE`

> `[F]` **HEAD + META-A fully discharged** =
> **VALIDATION** all twelve `L.2` criteria evaluated · **REGISTRY** `VALID` under `XV.5` · **COMPLETENESS** established under `LXXIX.1` and holding the status `verification` under `LXXIX.4` · **READINESS** `READY-PROVISIONAL` · **VACANCY** `T1 VACANT`, `VAC-01 located: false`, `XVII.4` (a)(b)(c) discharged and recomputable, (d) unreached · **FINALITY** `PROVISIONAL`, not `FINALIZED` · **CERTIFICATION** `CERTIFIED-PROVISIONAL` at most, presently undetermined · **FREEZE** ineligible.

`[I]` **Four axes move; five do not, and the five that do not are the five that matter to standing.** The state-space delta is entirely confined to validation, registry validity, and completeness — the three axes whose values are facts about the corpus's knowledge of itself. Readiness, vacancy, finality, certification and freeze are unmoved, and each is held by a META-B clause.

`[I]` R4 determined that discharge does not raise the readiness value. R5 determines the stronger and more exact result: **discharge moves the corpus from `LXXIX.4`'s "assertion" to `LXXIX.4`'s "verification" without moving a single deontic state.** The corpus's own words for the two conditions are located, and the transition between them is the whole of META-A's transformation capacity.

---

## R5.8 — UNCERTAINTY DELTA

| Id | Uncertainty | Under full META-A discharge | Basis |
|---|---|---|---|
| `UNK-R3-01` | Whether the 18+18 clause sets are exhaustive | **`[F]` RESOLVED IN THIS PHASE, negatively — independent of discharge.** 42 clauses located in `CMG-000001` alone; 14 not in R3's set | R5.1 |
| `UNK-R3-03` | Whether `CMG-INV-10`'s verification predicate is shorthand or literal | **RESOLVED.** Post-discharge the predicate contains its own subject; exit-zero becomes non-vacuous for `-10` | `XI.10`; `v1`, `v3` |
| `UNK-R4-03` | Whether regeneration of `CMG-REGISTRY.json` reproduces the committed bytes | **RESOLVED.** This is precisely the comparison discharge performs | `XV.5`, `II.4`, `L.5` |
| `UNK-R4-04` | Whether any gate outside the Article L validator detects the PROBE 3 forgery | **REDUCED.** The Article L validator would. Other gates remain unmeasured | `v9`; `A-R4-05` |
| `UNK-R3-04` | Whether the `EXCLUDE_DIR_PREFIXES` scope inversion was deliberate | **NEWLY OBSERVABLE.** Extending reconciliation to `00-CMG/` forces the boundary to be stated as a rule; it does not retrieve the original intent | `GAP-R3-03`; `XXXVI.6` |
| `UNK-R3-05` | Whether a third meta-cause hides behind the 11 of 14 unrealized design laws | **NEWLY OBSERVABLE — and it is the live falsification risk to the floor.** Discharge realizes the two *invariants*; 9 design laws other than `CMG-L-04` and `CMG-L-10` remain unrealized and unsurfaced | R3.0 census; `XLIX.5` vs `L.2` |
| `UNK-R3-02` | Whether `L.2`'s *"and nothing else"* permits or restricts realizing `-01`/`-10` | **UNCHANGED — and presupposed.** Discharge assumes the permissive reading. `[I]` The restrictive reading would make discharge itself non-conforming, and would equally condemn the validator's present `-09`/`-12` behaviour | `L.2`, `L.3`; R4.3 |
| `UNK-R4-01` | Which reading of `XV.5` governs — WRITE or RECOMPUTE-AND-COMPARE | **UNCHANGED, and made operative.** Discharge is the point at which the reading has consequences | `GAP-R4-02` |
| `UNK-R4-02` | The certification state at HEAD | **UNCHANGED** | `LXXX.5`; `GAP-R4-04` |
| `RES-01` … `RES-04` | T1 occupant · ratifier of `CMG-000001` · axis rank · corpus-wide invariant extension | **UNCHANGED — externally blocked** | `requires: EXPLICIT RATIFICATION` |
| `RES-05` … `RES-08` | T1 occupation · self-conferral · substitution for ratification · exception against invariants | **UNCHANGED — constitutionally prohibited** | `XVII.4`, `XLIV.7`, `XLIV.5`, `LV.4`, `LV.5` |
| `RES-09` | Primary text of `AUTH-02/03/04/06`, `Ω-010`, `CM-007` | **UNCHANGED** — referent is frozen `.docx` outside the reconciled set | `A-R4-04` |
| `RES-10` | The 63 / 37 partition | **REDUCED** — recomputation of the residue is a located duty | `VII.3`, `LXXIX.5` |
| **`UNK-R5-01`** *(new)* | **Whether full META-A discharge yields zero findings at HEAD** | **`[UNKNOWN]` — and not resolvable by discharge, only by performing it.** The check either confirms the Registry or contradicts it | `v12`; R5.0 |

`[F]` **Delta: 3 resolved · 2 reduced · 2 newly observable · 12 unchanged · 1 new unknown.** `[F]` Every *unchanged* entry attaches to META-B or to an out-of-corpus referent. Every *resolved* or *reduced* entry attaches to META-A.

---

## R5.9 — FLOOR FALSIFICATION UNDER COMPLETE DISCHARGE

**Hypothesis under falsification: *"floor = 2"* survives complete META-A discharge.**

### Candidates tested

| # | Candidate new basis member | Deontic sign | Modality | Direction of repair | Verdict |
|---|---|---|---|---|---|
| 1 | The 9 design laws unrealized other than `CMG-L-04`/`CMG-L-10` (`L-01, 02, 03, 05, 09, 11, 13, 14` and the residue of the 11-of-14 census) | `SHALL` — mandate, unrealized | contingent | enforcement **eliminates** | **`[F]` ABSORBED into META-A.** Same sign, same modality, same repair direction. Fails all three of R3's non-collapse criteria as a distinct member |
| 2 | `GAP-R4-02` — `XV.5` names an agent `CEP-004 XIV.2`/`XIV.3` forbid to write | mixed — a mandate and a prohibition in different instruments | contingent | owner reading disposes it | **`[F]` REJECTED — one-sided.** It bears on *who may perform* the reconciliation duty and says nothing about standing. Generates neither member. Identical failure mode to R3's C1–C10 |
| 3 | `GAP-R4-04` — certification undetermined at HEAD | not an obligation; an observational deficit | contingent | re-running the gate disposes it | **`[F]` REJECTED.** Not a cause; a measurement gap |
| 4 | The absence of any content-hash field on all 44 artifact entries | `SHALL` — `CEP-008 XVI.3`, `XLVIII.4` mandate content-addressing | contingent | enforcement eliminates | **`[F]` ABSORBED into META-A.** Tier-3 member of the located corpus (R5.1 #37) |
| 5 | `GAP-R3-01` — no located deontic taxonomy | a recording absence | contingent | recording eliminates | **`[F]` REJECTED — generates neither** |

`[F]` **Five candidates, zero admitted. `floor = 2` is not falsified by complete META-A discharge.**

### `[F]` But the floor is **VACATED**, and the distinction is load-bearing

`[I]` `floor = 2` is a theorem about **the minimum basis of HEAD's blocker set** — the 100 live blocking dependents. Complete discharge does not falsify that theorem; it changes the set the theorem is indexed to.

```
AT HEAD          blocker set = 100 live blocking dependents
                 minimum basis = { META-A , META-B }        size 2   ← R3, unfalsified
                 entailment relation over the basis = EMPTY          ← R3, unfalsified

POST-DISCHARGE   blocker set = 37 live blocking dependents (META-B's)
                 minimum basis = { META-B }                 size 1
                 reason: META-A is DISCHARGED, not REDUCED
```

`[F]` **The post-discharge basis is size 1 by discharge, not by collapse.** R3's `MINIMUM-BASIS-PROOF` step 3 (`META-A ⇏ META-B`) and step 4 (`META-B ⇏ META-A`) are untouched — neither member was ever derivable from the other, and discharging one does not derive it from the other. `[I]` A basis shrinks when a member is *eliminated*; a floor falsifies when a member is shown *reducible*. R5 produces the first and not the second.

`[UNKNOWN]` `UNK-R3-05` is the one live falsification risk and it is not resolvable here. If enforcement of the remaining 9 unrealized design laws surfaced an obligation that is **opposite-signed** — an in-force prohibition rather than an unrealized mandate — it would be a candidate third member, and it would be surfaced *by* discharge rather than *before* it. R5 records this and, under the standing bar on new root hunting, does not pursue it.

---

## R5.10 — TERMINAL VERDICT

> **META-A TRANSFORMATION CAPACITY: THE CONVERSION OF ASSERTION INTO VERIFICATION, AND NOTHING ELSE.**
>
> **DETERMINATION-COMPLETE · 51 CLAUSES LOCATED AGAINST R3's 18 · 11 STATE VARIABLES MOVE · 10 DO NOT · NO AXIS CEILING MOVES EXCEPT VALIDATION, REGISTRY VALIDITY AND COMPLETENESS · META-B MORE OBSERVABLE AND NO LESS BINDING · ROOT-Ω UNCHANGED IN FORCE BY CONSTRUCTION · FLOOR-2 NOT FALSIFIED, VACATED**

### TRANSFORMATION GRAPH

`[F]` 11 variables change: invariants evaluated 10→12 · `CMG-INV-01` absent→present · `CMG-INV-10` absent→present · corpus walk 0→required · collections text-bound 5/19→19/19 · `XLIX.7` status unknown-compliance→evaluated · Registry validity under `XV.5` INVALID→VALID · vacancy record under `VII.7` "opinion"→"claim" · PROBE-3 forgery UNDETECTED→DETECTED · `LXXIX.1` completeness not-established→establishable · `LXXIX.4` claim status assertion→verification.

`[F]` 10 do not: T1 `VACANT` · `VAC-01.located false` · `XVII.4(d)` unreached · `RATIFIED` 0 of 44 · finality `PROVISIONAL` · readiness `READY-PROVISIONAL` · certification ceiling `CERTIFIED-PROVISIONAL` · freeze ineligible · `CMG-OQ-01/02/03/07` open · META-B's externality class `PROHIBITED`.

### STATE-SPACE DELTA

`[F]` Three axes move — **validation** (10→12 criteria), **registry validity** (`INVALID`→`VALID` by `XV.5`'s own terms), **completeness** (`LXXIX.1` establishable; `LXXIX.4` assertion→verification). Six do not — readiness, vacancy, finality, certification, freeze, and the licensed action set of `XVII.4`. `[I]` Every axis that moves is a fact about the corpus's knowledge of itself. Every axis that does not is a fact about standing.

### OBSERVABILITY DELTA

`[F]` The Registry and every collection within it become answerable to the corpus they project. `VII.7` — *"Every allocation, recognition, precedence rank, and **vacancy** SHALL be recorded as evidence under CEP-008 and SHALL be reproducible from the repository alone. A meta-governance claim that cannot be recomputed from repository state IS not a claim but an opinion."* `[F]` The 44 artifact entries carry **no content-hash field at all**, against `CEP-008 XVI.3`'s *content-addressed* and `XLVIII.4`'s *verifiable … by content hash*. `[I]` Nothing becomes less observable: `HIDDEN` is empty, and `L.7`, `LXVI.1` and `XLIX.7` forbid the narrowing that would populate it.

### UNCERTAINTY DELTA

`[F]` 3 resolved (`UNK-R3-01` in this phase, `UNK-R3-03`, `UNK-R4-03`) · 2 reduced (`UNK-R4-04`, `RES-10`) · 2 newly observable (`UNK-R3-04`, `UNK-R3-05`) · 12 unchanged, every one attaching to META-B or an out-of-corpus referent · 1 new (`UNK-R5-01` — whether discharge yields zero findings, **unknowable without performing it**).

### BASIS IMPACT

`[F]` **No new basis member emerges.** Five candidates tested against R3's deontic-sign, modality and direction-of-repair criteria; two absorbed into META-A, three rejected as one-sided or as non-obligations. **At HEAD the basis remains `{META-A, META-B}`, size 2, entailment relation empty.**

### FLOOR IMPACT

`[F]` **`floor = 2` is not falsified.** `[F]` It is **vacated** — post-discharge the blocker set is META-B's 37, whose minimum basis is `{META-B}`, size 1, **by discharge and not by collapse.** R3's `MINIMUM-BASIS-PROOF` steps 3 and 4 are untouched: neither member was ever derivable from the other, and eliminating one does not derive it from the other. `[UNKNOWN]` `UNK-R3-05` is the sole live falsification risk, and discharge would surface it rather than settle it.

### ROOT-Ω IMPACT

`[F]` **No consequence of ROOT-Ω changes in force** — 11 consequences tested, 11 unchanged. `[F]` Exactly two things change: their recomputability, and the detectability of their forgery. `[I]` `LXXXI.6` settles this by construction rather than by measurement: *"it SHALL NOT confer standing on itself **by operation of any clause herein**"* forecloses conferral by any clause of the instrument, which includes all 42 META-A clauses located here. **Discharging clauses that cannot confer standing cannot confer standing.**

### META-B IMPACT

`[F]` **MORE OBSERVABLE · NEWLY MEASURABLE · NEWLY BOUNDED · NEWLY TRACEABLE · UNCHANGED IN FORCE · ENTRENCHED.** Not less observable. Not reduced. Not eliminated. All 37 dependents remain live. `[I]` A vacancy that cannot be silently closed is more binding than one that can — R3.0's direction-of-repair result, now with executed evidence on both sides of it.

### CORRECTION ISSUED BY R5

`[F]` **One, and it is a correction of modality, not of content.** R3's `WORLD-A` column asserted the post-discharge state as occupancy — *"Registry regenerable and regenerated; 19 of 19 collections text-bound; 44 of 44 artifacts in the registration universe."* R5 downgrades this to a **ceiling** statement. Whether HEAD's Registry survives its own reconciliation is `UNK-R5-01` and is not derivable from located text. R3's substantive conclusions are unaffected; its counterfactual was stated with more confidence than the located evidence carries.

`[F]` **A second finding refines rather than corrects:** R3's 18-clause META-A set was accurate in every member and incomplete in extent. `UNK-R3-01` is answered — the sets were not exhaustive. `A-R3-01` and `A-R4-02` are superseded for META-A's side by the 51-clause located corpus of R5.1; they stand for META-B's side, untested here.

### RESIDUAL IRREDUCIBLE SET

> `[F]` **At HEAD: `{ META-A , META-B }`** — unchanged from R3 and R4.
>
> `[F]` **Under complete META-A discharge: `{ META-B }`** — `ROOT-Ω`, deepest locus `XLIV.7`, origin `CEP-000 §5.4`, 18 located clauses across ≥6 instruments, 37 live blocking dependents, zero located transformation paths across all six tested verbs, externality class **PROHIBITED**. Irreducible, immovable, and — post-discharge — **recomputable**.
>
> `[I]` The end state of META-A's transformation capacity, stated exactly: **a corpus that can prove it is telling the truth about the one thing it cannot fix.**

**This determination falsifies, exhausts and concedes. It recommends nothing, designs nothing, amends nothing, implements nothing, and eliminates nothing.**

---

## CLASSIFIED RESIDUE

### FACTS `[F]`
1. Exhaustive sweep located **42 META-A clauses in `CMG-000001`**; **14 were absent from R3's 18-clause set**. With 6 verified cross-instrument clauses and 3 consumed by reference, the located corpus is **51**.
2. **`VII.7`** — *"Every allocation, recognition, precedence rank, and **vacancy** SHALL be recorded as evidence under CEP-008 and SHALL be reproducible from the repository alone. A meta-governance claim that cannot be recomputed from repository state IS not a claim but an opinion."* Places META-B's entire footprint inside META-A's mandate as located law.
3. **`LXXIX.1`** — completeness means *"no open gap within jurisdiction, no undelegated residue, **no unrecorded vacancy**, no unrecorded open question, and **all twelve invariants satisfied**."* A *recorded* vacancy is compatible with completeness; the twelve invariants are the sole unmet conjunct at HEAD.
4. **`LXXIX.4`** — *"A completeness claim not produced by the validator IS an assertion, not a verification."*
5. `CEP-008 XVI.3`, `CEP-008 XXI.1`, `CEP-004 X.1`, `CEP-004 XV.3` read verbatim for the first time across R3–R5. **All four of R3's citations are accurate.**
6. All 14 design laws and all 12 invariants read in full. `CMG-INV-01`'s verification is *"registry membership equals the set of artifacts cited as constitutional authority **anywhere in the corpus**"* — the clause that requires the corpus walk the validator does not perform.
7. `CMG-REGISTRY.json` artifact entries carry **12 fields and zero hash-like fields**: no content hash on any of 44 entries, against `CEP-008 XVI.3` and `XLVIII.4`.
8. 11 state variables move under discharge; 10 do not; the 10 are each fixed by a META-B clause.
9. Three axes move — validation, registry validity, completeness. Six do not — readiness, vacancy, finality, certification, freeze, licensed action set.
10. Five candidate new basis members tested; two absorbed into META-A, three rejected; zero admitted.
11. `HIDDEN` is empty: no located META-A clause narrows an existing check.
12. R7's locus is the `UGA`/`UCKP` alignment family (`CAA-INV-01…08`, `CAA-INV-08` = `ORTHOGONAL_ROLE_IS_SCOPE_BOUNDED_AND_NON_SUPREME`), not `CMG-REGISTRY.json` — which carries no `role` field. R5 does not re-derive it.
13. HEAD unchanged throughout; nothing implemented; validator re-verified at findings 0 / `READY-PROVISIONAL` / exit 0.

### INFERENCES `[I]`
1. **Discharge changes the warrant, never the value.** Every moved variable is epistemic; every fixed variable is deontic.
2. **`VII.7` converts R4's inference into located law.** R4 inferred that META-A governs META-B's observability; `VII.7` states that vacancy records fall under the reproducibility mandate.
3. **The corpus supplies its own term for HEAD's condition:** the assertion *"T1 is VACANT"* sits in a register nothing recomputes, and `VII.7` calls such a claim an **opinion**.
4. **ROOT-Ω is unmoved by construction.** `LXXXI.6` forecloses conferral by any clause herein, which includes every META-A clause.
5. **Entrenchment is the correct direction.** A vacancy that cannot be silently closed binds harder than one that can.
6. **The floor is vacated, not falsified.** Elimination shrinks a basis; reducibility falsifies a floor. R5 produces the first.
7. **The strongest reachable state is completeness without finality** — `LXXIX.1` satisfied while `LXXX.4`, `CEP-006 XII.2` and `CEP-007 IV.1` all hold.
8. **R3's `WORLD-A` overstated its modality**, and R5's central methodological result is the separation of ceiling from occupancy.

### ASSUMPTIONS `[A]`
`A-R5-01` The CORE / CONSTITUTIVE / CONSEQUENTIAL tiering of the 42 clauses is derived, not located. `GAP-R3-01` stands: no located taxonomy of obligation types exists, so the boundary of META-A's corpus is a scope judgment.
`A-R5-02` `CEP-001` Articles XVIII, XX, XXI are consumed by reference and were **not read** in R3, R4 or R5.
`A-R5-03` The 63 / 37 partition is carried from R1/R2 and not re-derived (inherits `A-R4-01`).
`A-R5-04` "Full discharge" is construed as: `CMG-INV-01` and `CMG-INV-10` evaluated by the Article L validator, and the Registry bound to its declared inputs per `XV.3`/`XV.5`/`II.4`. **No located clause defines "full discharge"**; this construction is derived from the two unimplemented criteria and the reconciliation duties.
`A-R5-05` Discharge presupposes the permissive reading of `L.2`'s *"and nothing else"* (`UNK-R3-02`).
`A-R5-06` Measured at `1e3e4ba9` in this environment.

### GAPS `[GAP]`
| Id | Gap | Disposition |
|---|---|---|
| `GAP-R5-01` | R3's and R4's META-A clause set was under-capture by 14 clauses in the meta instrument alone; no located instrument enumerates the corpus of a meta-cause, so completeness of any such set is unverifiable by construction | **NEW · SURVIVING** — inherits `GAP-R3-01` (no obligation taxonomy) |
| `GAP-R4-02` | `XV.5` names the validator; `CEP-004 XIV.2`/`XIV.3` forbid it to write | **CARRIED · made operative by discharge** |
| `GAP-R4-04` | Certification undetermined at HEAD | **CARRIED · unchanged by discharge** |
| `GAP-R3-01` · `GAP-R3-04` | No deontic taxonomy · no entailment register | **CARRIED · unchanged by discharge** |
| `GAP-R3-02` · `GAP-R3-03` | `L.2`/`L.3`/`XLIX.5` routing · reconciliation scope boundary | **CARRIED · REDUCED by discharge, not closed** |

### UNKNOWNS `[UNKNOWN]`
`UNK-R5-01` **Whether full META-A discharge yields zero findings at HEAD.** Not resolvable by discharge — only by performing it. The check either confirms the Registry or contradicts it, and nothing located decides which.
`UNK-R3-02` Whether `L.2`'s *"and nothing else"* permits or restricts realizing `-01`/`-10`. Unchanged, and presupposed by discharge.
`UNK-R3-05` Whether a third meta-cause hides behind the 9 remaining unrealized design laws. **Newly observable under discharge; the sole live falsification risk to `floor = 2`.** Not pursued under the standing bar on root hunting.
`UNK-R4-01` Which reading of `XV.5` governs. Unchanged; made operative.
`UNK-R4-02` Certification state at HEAD. Unchanged.
`RES-01` … `RES-09` META-B's externally blocked, constitutionally prohibited and out-of-corpus residue. All unchanged.

---

*PHASE R5 · AUTHORITY = NONE (DERIVED TRUTH) · Reports; determines nothing.*
*`READY-PROVISIONAL`; Tier T1 VACANT; `CMG-L-12` applies to every statement herein.*
*Counterfactual: nothing was implemented, no clause was realized, the corpus is unchanged.*
*Reproduce the located corpus: exhaustive sweep of `00-CMG/CMG-000001-…md` on `reconcil|recomput|regenerat|byte-identical|drift`, plus full reads of `X.1`–`X.14` and `XI.1`–`XI.12`.*
