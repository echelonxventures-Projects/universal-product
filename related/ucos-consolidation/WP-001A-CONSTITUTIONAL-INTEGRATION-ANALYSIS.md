# CONSTITUTIONAL INTEGRATION ANALYSIS — MCRF / STREAM-00 / WP-001A

| Field | Value |
|---|---|
| WORK PACKAGE | `MCRF / STREAM-00 / WP-001A` — Discovery Reconciliation |
| AUTHORITY | **NONE (DERIVED ANALYSIS ONLY)** |
| TARGET INSTRUMENT | `UNIVERSAL-CONSTITUTIONAL-META-REQUIREMENTS-FOUNDATION.md` |
| COMPANIONS | `DISCOVERY-REGISTER.md` · `DISCOVERY-CONSOLIDATION-REPORT.md` |
| WHAT THIS DOCUMENT DOES | Nominates candidates and states the ground for each. It admits nothing, drafts no clause, allocates no ownership, and creates no instrument. |

---

## 0 — THE TARGET INSTRUMENT DOES NOT EXIST

**`[F]` `UNIVERSAL-CONSTITUTIONAL-META-REQUIREMENTS-FOUNDATION.md` is not present in the repository
at HEAD.** An exhaustive filename search across the working tree returns no match, and no artifact
among the fourteen cites it. Every entry below is therefore a **candidate for an instrument that
would have to be created**, not a proposed amendment to an existing one.

**`[F]` Three located clauses bound anything this analysis could recommend, and they are recorded
here before any candidate is named.**

| Bound | Clause | Consequence for this analysis |
|---|---|---|
| Jurisdiction containment | `CMG-INV-12` · `XIX.2` · `XLIII.4` — *"a jurisdiction-expanding amendment to the meta layer IS PROHIBITED"* | No candidate may claim reach over an out-of-corpus authority. Every candidate below is scoped in-corpus or is marked **NOT ADMISSIBLE** |
| Certification is never durable | `LXXX.6` · `LI.5` — any amendment to `CMG-000001` automatically revokes certification across all 44 artifacts | A candidate that requires amending `CMG-000001` carries a certification-revocation cost. `A01`:775 records this as the reason `GAP-O-03` survives: *recording is cheaper than fixing, and `VIII.5` permits recording* |
| Declining is correct | `XIX.5` — *"Where a question falls outside `XIX.1` and is not delegated, this instrument SHALL record it and SHALL decline to answer it. Declining IS the correct constitutional response"* | Where no located clause states a requirement either way, this analysis records the candidate and declines |

**`[I]` One further bound is structural rather than clause-based.** A new meta-requirements
instrument would itself be an artifact in the constitutional corpus, and therefore subject to every
defect the fourteen artifacts locate — `META-A` above all. **An instrument that states the
reconciliation requirement and is not itself reconciled would be the ninth name for the same
failure** (`DISCOVERY-CONSOLIDATION-REPORT.md` §3, class E-03). This is stated as an observation,
not as an objection.

---

## 1 — CANDIDATE INVARIANTS

Ten candidates. An invariant is admitted here only if the artifacts locate a **measurable
verification condition** for it.

| # | Candidate invariant | SOURCE | RATIONALE | DEPENDENCIES | CONFLICTS | RECOMMENDED ACTION |
|---|---|---|---|---|---|---|
| `CI-01` | Every projected representation of a constitutional fact SHALL be recomputable from the canonical text, and the comparison SHALL be performed | `A06`:402 (`XI.10`/`CMG-INV-10`) · `A06`:210 (`XV.5`) · `A09`:R5.2 | `META-A` — the single largest blocker basis element, carrying 63 of 100 live blocking dependents. Declared eight times in `CMG-000001`, realized nowhere. Verification condition is executable: regenerate, compare bytes | `CI-02` (else the condition is self-certifying) · `CR-01` · `CR-03` | `GAP-R4-02` — `XV.5` names the Article L validator as regenerating agent while `CEP-004` `XIV.2`/`XIV.3` forbid it to write. Dissolves under the RECOMPUTE-AND-COMPARE reading | **RECORD AS CANDIDATE.** Route the `XV.5` reading (`UNK-R4-01`) to the owner before any drafting |
| `CI-02` | No verification condition SHALL be satisfiable by the exit status of the program that omits it | `A06`:446 (`GAP-R2-05`) · `A06`:365 | The deepest located cause of `META-A`. `CMG-INV-10` mandates recomputability and declares its own verification to be *"validator exit status zero with zero findings"* — a predicate the validator satisfies without recomputing anything. `[F]` No located clause detects a self-certifying verification condition | `CI-09` (deontic classification distinguishes a mandate from its own evidence) | none located | **RECORD AS CANDIDATE — HIGHEST LEVERAGE.** This is the one candidate whose absence conceals the others |
| `CI-03` | Every enumeration declared CLOSED SHALL itself be projected | `A06`:448 (`GAP-R2-07`) · `A06`:384 | Measured: `closed_enumerations` names four; **three** name collections absent from the Registry (`invariants`, `lifecycle_phases`, `unknown_concept_dispositions`). `check_closed_enumerations` passes. `XI.13` calls the invariant set *"the immutable ground against which every other part of this instrument is checked"* — and the ground is closed but unprojected | `CI-01` | `CMG-INV-09` (no finite ceiling) versus `XI.13` (set IS CLOSED) — `C-06`, confined by `XI.13` to the checking apparatus, **confined not resolved** | **RECORD AS CANDIDATE** |
| `CI-04` | Registry membership SHALL equal the set of artifacts cited as constitutional authority anywhere in the corpus | `A06`:334 (`CMG-INV-01`, `XI.1`) · `A06`:359 | The invariant exists and is inside a criteria set `L.2` declares exhaustive. Its converse direction is never evaluated: the validator performs **no** `os.walk`, `rglob`, or `glob(`. `A02`:440 measures the consequence — 21 of 44 recognized artifacts unregistered and unhashed, 11 of them FROZEN | `CI-01` · `CR-02` · `CR-06` | `SC-02`/`K-13` — the registration universe and the constitutional corpus are declared different sets by `EXCLUDE_DIR_PREFIXES` | **RECORD AS CANDIDATE.** The conflict is a scope decision no located instrument records (`GAP-R3-03`) and must be settled first |
| `CI-05` | Every declared design law SHALL name the criterion that verifies it | `A10`:322 (`GAP-R6-03`) · `A07`:388 (`GAP-R3-02`) | `XLIX.5` routes `CMG-L-01…14` to the Article L validator while `L.2` restricts criteria to `CMG-INV-01…12` *"and nothing else."* No instrument declares which invariant verifies which design law, so design-law realization is **unmeasurable except by derivation** | `CI-09` | `GAP-R2-06` — `L.2` declares 12 criteria exhaustive; `L.3` supplies realization sub-clauses for 8 | **RECORD AS CANDIDATE.** `UNK-R3-02` (whether `L.2`'s *"and nothing else"* permits or restricts) is a prerequisite owner reading |
| `CI-06` | Every discovery identifier SHALL be unique across the corpus | `A04`:415 (`GAP-R-01`) · `DISCOVERY-REGISTER.md` §4 | `[F]` 20 identifier namespace clashes measured across the fourteen artifacts alone: `A-01`…`A-08`, `UNK-01`…`UNK-06`, `K-1`…`K-5`, `G-11`. `[F]` 583 distinct markdown uncertainty identifiers over 7,233 mentions, with no global registry. `[I]` Building the register required exactly the disambiguation `GAP-R-01` says is unavailable | `CR-10` | none located | **RECORD AS CANDIDATE.** Encountered, not hypothetical |
| `CI-07` | A condition SHALL be retirable, and retirement SHALL be exercised rather than merely legislated | `A14`:197 (`G-11`) · `A14`:182 (`RU-18`) | Measured: **0** `SUPERSEDED` of 1,579 artifacts; **0** of 1,822 history events; the vocabulary exists at `ukb.py:344` and has never once been used. Consequence at HEAD: *"100% READY, blocking risks ZERO"* and *"# NOT READY"* are both committed truth, both `ACTIVE`, both citable | `CI-06` | none located; `K-05` (append-only) constrains the **form** of retirement, not its existence | **RECORD AS CANDIDATE.** `A14` classifies the remedy as convergence, not redesign |
| `CI-08` | Every vacancy, allocation, recognition and precedence rank SHALL be reproducible from repository state | `A09`:R5.4 (`VII.7`) | `VII.7` verbatim: *"A meta-governance claim that cannot be recomputed from repository state IS not a claim but an opinion."* At HEAD `META-B`'s entire visibility rests on one JSON record that no program compares against the constitution asserting it (`A08`:490) | `CI-01` · `CR-03` | none located | **RECORD AS CANDIDATE.** Note `A09`'s result: a vacancy that cannot be silently closed is **more** binding, not less |
| `CI-09` | Every constitutional obligation SHALL carry a recorded deontic sign | `A07`:387 (`GAP-R3-01`) | No located instrument classifies obligations as mandate or prohibition, so no register distinguishes an **unimplemented mandate** from an **in-force prohibition**. `[F]` The floor of 2 rests on exactly that distinction, and it had to be derived rather than read | `CI-05` · `CI-10` | none located | **RECORD AS CANDIDATE.** Prerequisite to `CI-05` and to any future basis proof |
| `CI-10` | Entailment between located defects SHALL be recorded, not re-derived per pair | `A05`:294 (`GAP-R1-01`) · `A07`:390 (`GAP-R3-04`) | No entailment register exists at defect rank or at meta rank. `A05`:320 records the consequence: minimality is proved *relative to the located entailment relation, which is itself not proved complete* — and `UNK-R1-01` leaves open whether the basis is smaller than six | `CI-09` | none located | **RECORD AS CANDIDATE** |

---

## 2 — CANDIDATE REQUIREMENTS

Twelve candidates. A requirement is admitted here only if the artifacts locate both the obligation
and a mechanism that would satisfy it.

| # | Candidate requirement | SOURCE | RATIONALE | DEPENDENCIES | CONFLICTS | RECOMMENDED ACTION |
|---|---|---|---|---|---|---|
| `CR-01` | The meta-constitutional validator SHALL evaluate `CMG-INV-01` and `CMG-INV-10` | `A08`:437 · `A06`:419 | `[F]` Both have **0** occurrences in `cmg_validate.py`; the other ten are present. They are the only two whose verification requires comparing corpus to projection. `[F]` The validator already implements `CMG-INV-09` and `-12`, which `L.3` never mandates — so exceeding `L.3` engages no amendment and no ratification | `CI-01` · `CI-04` | `UNK-R3-02` — the restrictive reading of `L.2` would make the extension non-conforming, and would equally condemn the validator's present `-09`/`-12` behaviour | **RECORD AS CANDIDATE.** No amendment required under the permissive reading; owner reading required to settle it |
| `CR-02` | The meta-constitutional validator SHALL perform a corpus walk | `A06`:359 · `A06`:422 | `CMG-INV-01`'s converse direction — *every artifact cited as authority is registered* — is never evaluated because no walk exists. `check_homes` verifies only the forward direction | `CR-01` · `CI-04` | `SC-02` scope boundary | **RECORD AS CANDIDATE** |
| `CR-03` | Every registered artifact entry SHALL carry a content-hash field | `A09`:R5.4 · `A02`:439 | `[F]` The 44 artifact entries carry **no content-hash field at all**, against `CEP-008` `XVI.3` (*content-addressed*) and `XLVIII.4` (*verifiable … by content hash*). `[F]` And the anchor that does exist is current and gate-enforced with **0 drift** across 23 artifacts — the remedy is present and unwired | `CI-01` · `CI-08` | `GAP-P-05` — no clause requires the meta validator to consult the one existing content anchor | **RECORD AS CANDIDATE.** `A02`:509 — *"a verified anchor wired to nothing"* |
| `CR-04` | The Registry SHALL project all 17 per-artifact fields `XV.2` mandates | `A10`:320 (`GAP-R6-01`) | Measured: 10 of 17 recorded; **7 absent across all 44 entries**, undetected. `A11`:458 records the compounding consequence — 11 artifacts occupy `FROZEN` while `RATIFIED` = 0, and the absent fields are exactly those that would establish whether the freeze satisfied `CEP-007` `IV.1` | `CI-01` | `GAP-R7-01` — `CMG-T-09` versus `CEP-007` `IV.1`/`V.1`; `UNK-R6-02` — whether the 7 fields are recoverable by projection or absent from the text too | **RECORD AS CANDIDATE** |
| `CR-05` | Closure state SHALL be detectable against referent removal, not only against contradiction | `A08`:434 (PROBE 3) | `[F]` Complete forged closure is executable and undetected: delete `VAC-01`, repoint the four dependent superiors, close every open question, raise the declared ceiling → **`findings 0`, `readiness READY`, `exit 0`** over a registry state contradicting `XVII.4`, `XVI.2`, `LXXXI.5`, `LXXX.4`, `LXXXVI.4`. The two naive forgeries **were** detected. Detection fails on referent removal | `CI-01` · `CR-01` | `UNK-R4-04` — only the CMG gate was executed against the forged registry; other gates unmeasured | **RECORD AS CANDIDATE.** `A09` measures this as DISCHARGED under full `META-A` realization |
| `CR-06` | The registration universe SHALL either equal the constitutional corpus or record the boundary as a governed decision | `A07`:389 (`GAP-R3-03`) · `A02`:484 (`GAP-P-06`) | `[F]` 48% of the constitutional corpus lies outside every hash-bearing register. `[F]` `EXCLUDE_DIR_PREFIXES` excludes exactly the directories `register.sh --guard` reconciles. `[I]` `A07`:415 — *"META-A is not a missing capability. It is a working capability aimed away from the constitution"* | `CI-04` | `K-13` classifies the mismatch as bypassable by rule change; `UNK-R3-04` — whether the inversion was deliberate is unrecoverable | **RECORD AS CANDIDATE.** The recording half is achievable without the substantive half |
| `CR-07` | A tier↔role correspondence rule SHALL be declared | `A02`:481 (`GAP-P-03`) · `A06`:214 | The absence is total — `A06` calls `R7` *"the degenerate case: no tier↔role correspondence rule is declared anywhere."* Live consequence: `UCKP-LAW-0001` holds `tier: T4`, `superiors: ["VAC-01"]`, and role `SUPREME`, with `CAA-INV-01` passing | `CI-05` | `SC-01` · `SOUND-01` — the contradiction persists under any T1 occupancy (`A05`:318) | **RECORD AS CANDIDATE.** `UNK-R2-04` — whether the absence is omission or deliberate refusal to rank two vocabularies |
| `CR-08` | `XXV.3`'s state mapping SHALL cover every `CEP-006` `VI.1` state | `A01`:756 (`GAP-O-03`, `GAP-O-06`) · `A02`:451 | `[F]` `CEP-006` `VI.1` declares 9 states; `XXV.3` maps 3; **`ACCEPTED` is unmapped**. `[F]` `XXV.3`'s own conflict rule mandates an amendment that does not exist. `[F]` `FINALIZED` occurs exactly once in `CMG-000001`, inside `XXV.3` itself | `CR-09` (`A02`:465 — the same defect is why act cardinality was underivable) | **`LXXX.6`** — correcting it revokes certification across all 44 artifacts. `A01`:775: *recording is cheaper than fixing, and `VIII.5` permits recording* | **RECORD AS CANDIDATE WITH COST DISCLOSED.** Do not recommend the amendment; record the cost and route to the owner |
| `CR-09` | A genus definition of *constitutional act* SHALL be recorded | `A03`:325 (`G-Q-02`) | `[F]` Eleven act-model components are located and one is executable and passing; **no genus definition (*"an act IS …"*) exists**; Article IV defines no term *act*. `[F]` `A03`:Q9.10 — an in-corpus genus definition is **not prohibited**: it falls inside `CMG-000001` `XIX.1` meta jurisdiction (Article IV, Definitions) | none | none located for the in-corpus half | **RECORD AS CANDIDATE — SMALLEST AND MOST LEVERAGED.** One definition, in jurisdiction, no external authority |
| `CR-10` | A global identifier-namespace registry SHALL exist | `A04`:415 (`GAP-R-01`) | 583 distinct markdown uncertainty identifiers, 7,233 mentions, 3,885 files, no registry; identifier namespaces collide across programmes — verified, `K-19` (UCCEP) versus `K-01…16` (End-State) | `CI-06` | none located | **RECORD AS CANDIDATE** |
| `CR-11` | Every required item class SHALL carry a register | `A04`:417 (`GAP-R-03`) | `[F]` **8 of 21** item classes the instruction requires have no register in the repository. `[I]` `A04`:401 — a zero count in a class with no adversary register measures **absence of measurement**, not absence of defect. Sharpest instance: `GAP-R-04`, zero recorded security defects over a class with one domain-scoped owner and no adversary register | `CR-12` | none located | **RECORD AS CANDIDATE** |
| `CR-12` | Every candidate uncertainty class SHALL carry a recorded disposition under `LXXVII.2` | `A04`:419 (`GAP-R-05`) | 13 candidate classes have neither a register nor a recorded disposition. `UNK-R-03` — whether they were considered and rejected under `LXXVII.2(e)` or never presented: **no discovery record exists either way** | `CR-11` | `LXXVII.1` — the procedure is reactive by design and applies *"for any concept presented to the corpus"*, so absence of a disposition is not by itself a defect | **RECORD AS CANDIDATE.** The requirement is the *record*, not the anticipation |

---

## 3 — CANDIDATE CONSTRAINTS

**`[F]` Sixteen constraints are already located and enumerated at `A13` Phase 4. Thirteen are
absolute and non-eliminable, two are eliminable in-corpus, one is an assumption rather than a
constraint.** A meta-requirements instrument would **inherit** these, not restate them.

| # | Constraint | Class | Absolute | Eliminable | RECOMMENDED ACTION |
|---|---|---|---|---|---|
| `K-01` | `ROOT-Ω` — a corpus cannot self-confer standing | Logical / governance | YES | NO | **INHERIT.** Minimum proof set `{XLIV.7, CEP-000 §5.4, XVII.4}`, proved exactly minimal, with a disjoint independent architectural proof |
| `K-02` | Self-verification cannot establish its own soundness | Logical | YES | NO | **INHERIT.** Bounds `CI-01` and `CI-02`: they improve recomputability, not soundness |
| `K-03` | No total order over constitutional systems | Information-theoretic | YES (relative to this corpus) | only by amending `LXXIX.6` | **INHERIT.** Forecloses any scoring or maturity metric in the instrument |
| `K-04` | No finite ceiling (`CMG-INV-09`, `LXXVI.5`) | Governance | YES | NO | **INHERIT.** Any apparent limit *"SHALL be read as a defect"* — this binds the instrument's own enumerations |
| `K-05` | Append-only (`LXXVI.3`, `XV.4`, `XXIV.5`, `CMG-L-11`) | Governance | YES | NO | **INHERIT.** Forbids renumber / rename / reclassify / invalidate — constrains the form of `CI-07` |
| `K-06` | Jurisdiction containment (`CMG-INV-12`, `XIX.2`, `XLIII.4`) | Governance | YES | NO | **INHERIT.** The binding constraint on this entire analysis |
| `K-07` | Decidability (`VI.5`) | Logical | YES as a standard | NO | **INHERIT.** `[F]` currently unmet — three located violations |
| `K-08` | Zero hard coding (`CMG-L-08`, `LXVI.5`) | Computational | YES | NO | **INHERIT WITH THE CORRECTION.** `A06`:258 exculpates `CMG-L-08`: regeneration is a third path that holds no enumeration member and satisfies both duties at once |
| `K-09` | Certification is never durable (`LXXX.6`, `LI.5`) | Governance | YES | NO | **INHERIT.** Governs the cost of `CR-08` and of the instrument's own future amendments |
| `K-10` | Self-ratification prohibited (`XLIV.7`) | Governance | YES | NO | **INHERIT.** Component of `K-01` |
| `K-11` | Vacancy non-promotion (`XVII.4`, `LXXXI.5`) | Governance | YES | NO | **INHERIT.** Any contrary reading *"IS void under `CMG-L-13`"* |
| `K-12` | Act atomicity undefined | Logical | YES at HEAD | **REVERSED by `A03`** | **DO NOT INHERIT AS STATED.** `A03` proves the residual gap externally blocked and unclosable by amendment; the in-corpus part is `CR-09` |
| `K-13` | Registration universe ≠ constitutional corpus | Computational | NO | YES | **ADDRESS via `CR-06`** |
| `K-14` | Human / external constituent act required for finality | Human | YES | NO | **INHERIT.** `ED-1` — *"not manufacturable"* |
| `K-15` | Substrate-neutrality is certified, not proved | Information-theoretic | `[A]` | — | **INHERIT AS ASSUMPTION, NOT CONSTRAINT.** The exhaustive proof *"was not performed"* |
| `K-16` | Evolution terminates at `PROVISIONAL` | Governance | YES | only by closing `VAC-01` | **INHERIT.** `LXXVI.2(h)` |

---

## 4 — CANDIDATE OBLIGATIONS

| # | Candidate obligation | SOURCE | RATIONALE | CONFLICTS | RECOMMENDED ACTION |
|---|---|---|---|---|---|
| `CO-01` | Record · record · refer · re-run-on-closure — the four bookkeeping verbs licensed over an unfillable vacancy | `A08`:437 (`XVII.4` (a)–(d)) | `[F]` The corpus's complete licensed action set for `META-B`. (a)(b)(c) discharged at HEAD; (d)'s antecedent unsatisfied because `located: false` | none | **INHERIT VERBATIM.** This is the whole of what may lawfully be done about `ROOT-Ω` |
| `CO-02` | An undecidable matter SHALL be recorded as an open constitutional question and routed to explicit ratification — never decided by default, by the detector, by the most convenient authority, or by silence | `A12`:651 (`LVII.3`, `LIV.3(d)`, `XVII.5`) | The corpus prescribes the outcome `A12` reaches. Two independent normative procedures converge on `CMG-OQ-01` | none | **INHERIT VERBATIM** |
| `CO-03` | An escalation that cannot terminate within the corpus SHALL be recorded as an open matter and surfaced at every readiness assessment | `A12`:652 (`CEP-002` 12.5) | Independent of CMG, from an IN-EFFECT `T2` instrument. `A12`:653 — this is why `CMG-OQ-01` is *"not CMG's self-serving invention but the convergent output of two independent normative procedures"* | none | **INHERIT VERBATIM** |
| `CO-04` | Recording a gap SHALL be superior to concealing one | `A13` (`VIII.5`, `LXXVIII.5`) | `VIII.5` makes the instrument that *records more gaps* the superior one — which `A13` shows inverts the term *"perfect"* | `SC-04` — percentage scoring runs the other way | **INHERIT.** It is the located ground for every *"decides nothing"* footer in the fourteen artifacts |
| `CO-05` | Where a question falls outside jurisdiction and is not delegated, the instrument SHALL record it and SHALL decline to answer it | `A03`:334 (`XIX.5`) | *"Declining IS the correct constitutional response."* `A03` uses it to refuse the amendment-justification question rather than answer it out of scope | none | **INHERIT VERBATIM** |
| `CO-06` | Discovery SHALL precede design: establish the concept is not already owned; record the discovery naming every existing owner examined and why each is insufficient | `A13`:723 (`LXXVI.2(a)`) | `[F]` `A13` determines architecture work **not permitted** and names `LXXVI.2(a)` as the next step in sequence. `[I]` `A13` states this as a reading of the ordering, not a recommendation | none | **INHERIT.** It is the located procedure that a WP-001A-class discovery register serves |
| `CO-07` | An assertion SHALL be recomputable from repository state or SHALL be recorded as an opinion | `A09`:R5.4 (`VII.7`) | `VII.7` supplies the sanction `CI-08` needs: the consequence of non-recomputability is loss of the status *claim* | none | **INHERIT VERBATIM** |
| `CO-08` | Irreconcilable inputs SHALL raise a finding rather than a guess | `A06`:215 (`XXVII.5`) | `[F]` Four vocabularies disagree about `CMG-000001`'s state and **no finding is raised**. `[F]` `ukb.py` infers status from a status string, which `XXVII.5` forbids | `GAP-P-02` — no validator reconciles two registers' records of one artifact; `GAP-P-04` — the Registry cannot represent findings at all | **INHERIT, AND NOTE `GAP-P-04`.** The obligation cannot be discharged in a projection that has no `findings` collection |

---

## 5 — CANDIDATE VALIDATIONS

| # | Candidate validation | SOURCE | Status at HEAD | CONFLICTS | RECOMMENDED ACTION |
|---|---|---|---|---|---|
| `CV-01` | Meta-constitutional conformance over the closed criteria set | `A06`:340 · `A13`:370 | `cmg_validate.py` exit 0, **findings 0**, `READY-PROVISIONAL`; **10 of 12** criteria realized; `verify.sh:410` labels the stage `CMG-INV-01..12` | `[F]` The gate's label claims 12; the realization covers 10 | **ADOPT WITH THE LABEL CORRECTED.** A label that overstates coverage is the mechanism by which `CI-02` hides |
| `CV-02` | Registration and eligibility enforcement | `A14`:178 | `enforce --pre` → eligible **1,579** = registered **1,579**, unregistered **0**, awaiting VCS binding **0** | `FB-2` — the act that closed this created the dual-registration defect (192 objects hold two universal identities each) | **ADOPT.** And record `FB-2` as its cost |
| `CV-03` | Regenerate-and-compare drift guard | `A07`:413 | **Implemented and running**: `register.sh --guard` exits 3 on divergence; `determinism.yml` double-builds; `ukbx twin --check` certifies the twin — **restricted to the directories the constitutional universe excludes** | `GAP-R3-03` — the scope boundary is not recorded as a decision | **ADOPT AND EXTEND SCOPE.** `A07`:413 — *"WORLD-B is not hypothetical. It exists in this repository"* |
| `CV-04` | Forged-closure probes | `A08`:434 | PROBE 1 and 2 **detected** (`IV.11`; `CMG-INV-04` ×4); PROBE 3 **undetected** | `UNK-R4-04` — other gates unmeasured against the forgery | **ADOPT AS A STANDING TEST.** A closure check that cannot be forged is the only evidence `CI-08` accepts |
| `CV-05` | Universal object governance · autonomous evolution · replay · birth contract · infinite scope · primitive alignment · verification intelligence | `A14`:8.1 | **All PASS** from a clean tree | none | **ADOPT AS THE LOCATED GATE SET** |
| `CV-06` | The 15-stage verification surface | `A14`:8.1 · executed in this work package | **14 of 15 PASS**; the failing stage is `pytest`, on **tests** and not on coverage (97% against a floor of 90) | `FB-1` (26 tests) · `FB-2` (3 tests) · signature drift (7) · corpus-sized constants (3) | **ADOPT.** And record that a green `verify.sh` is not currently attainable at HEAD |
| `CV-07` | Eligibility-universe digest, local versus CI | `A02`:454 | eligibility 1,579 = 1,579, digest `ce71479a…` | `UNK-P-01` — whether all 28 CI gate workflows pass at HEAD is unmeasured | **ADOPT.** `A-P-01` remains undischarged |

---

## 6 — CANDIDATE PROOF OBLIGATIONS

| # | Proof obligation | SOURCE | Status | RECOMMENDED ACTION |
|---|---|---|---|---|
| `CP-01` | `LXXVII.3`'s five-outcome partition is exhaustive over concept-space | `A13`:535 | **`[F]` DISCHARGED — exhaustive by construction over three binary axes, independent of domain cardinality.** `A13` calls it the corpus's single strongest formal result | **INHERIT AS THE ONE DISCHARGED PROOF** |
| `CP-02` | `ROOT-Ω` minimum proof set is exactly `{XLIV.7, CEP-000 §5.4, XVII.4}` | `A02`:463 | **DISCHARGED**, with a disjoint independent architectural proof at `AUTH-03/04/06` + `Ω-010` + `CM-007` | **INHERIT** |
| `CP-03` | The irreducible blocker basis is unique at size 6 | `A05`:310 | **DISCHARGED** relative to the located entailment relation — the unique size-6 generating set among all 256 subsets; no subset of size 1–5 generates | **INHERIT WITH `GAP-R1-01` DISCLOSED.** The entailment relation is not proved complete |
| `CP-04` | The ontological floor is 2 and the two cannot merge | `A06`:262 · `A07`:405 · `A10`:254 | **DISCHARGED** — both entailment directions falsified, ten candidate ancestors yield none, no size-1 basis exists, seven required proofs executed in `A10` | **INHERIT.** `UNK-R3-05` was the sole live falsification risk and `A10` discharged it |
| `CP-05` | No selector exists for the competence reading | `A12`:321 | **DISCHARGED** — formal non-existence proof in eight steps, step 6 derived entirely from IN-EFFECT `T2` instruments that make no reference to `CMG-000001`'s standing | **INHERIT.** The undecidability does not depend on `CMG-000001` being `PRE-EFFECT` |
| `CP-06` | `B_min = { CMG-OQ-01 }` — necessity and sufficiency | `A12`:603 | **DISCHARGED**, with corrected semantics: a **selector** vacancy over located text, not an authority vacancy | **INHERIT** |
| `CP-07` | Self-verification soundness (`U-02`, `UP-01`) | `A13`:411 | **`[UNPROVABLE]`** — `CMG-INV-10` puts the verifier inside the verified system; `CAA-INV-01` is a located unfalsifiable instance | **RECORD AS PERMANENTLY OPEN.** Do not state as a requirement |
| `CP-08` | Future-proofness (`U-03`, `UP-02`) | `A13`:437 | **`[UNPROVABLE]`** — `LXXVII.6`/`.7` refuse the premise | **RECORD AS PERMANENTLY OPEN** |
| `CP-09` | *"Strongest"* / absolute superiority (`U-01`, `UP-03`, `UP-04`) | `A13`:506 | **`[UNPROVABLE]`** — `LXXIX.6` forbids the scoring it presupposes | **RECORD AS PERMANENTLY OPEN** |
| `CP-10` | Universal completeness (`UP-05`) and infinite-domain coverage (`UP-06`) | `A13`:535 · `A13`:543 | **`[F]` NO for coverage; `[I]` YES for disposition** — and the corpus does not claim coverage | **RECORD THE PARTITION, NOT THE CLAIM** |
| `CP-11` | Substrate-neutrality as proof rather than certification (`UP-07`) | `A13` (`K-15`) | **NOT PERFORMED** — the source certification states the exhaustive proof *"was not performed"* | **RECORD AS ASSUMPTION `K-15`** |
| `CP-12` | Completeness of any meta-cause clause set | `A09`:441 (`GAP-R5-01`) | **UNVERIFIABLE BY CONSTRUCTION** — no instrument enumerates the corpus of a meta-cause, and under-capture was demonstrated (18 → 51 clauses) | **RECORD AS A STANDING LIMIT ON EVERY BASIS PROOF** |

---

## 7 — CANDIDATE REDESIGN-ELIMINATION REQUIREMENTS

**`[F]` `A14` §5.5 and §6.1 determine that none of the three surviving foundation blockers requires
redesign of any kind, and none requires a constitutional amendment.** The candidates below are
therefore *convergence and implementation* requirements whose purpose is to eliminate the need for
redesign, not to authorise one.

| # | Candidate | SOURCE | Why redesign is NOT required | DEPENDENCIES | CONFLICTS | RECOMMENDED ACTION |
|---|---|---|---|---|---|---|
| `CE-01` | A declared classification rule SHALL have an implementing predicate | `A14`:352 (`FB-1`) | `R-09` (`GOVERNED_ANALYSIS`) is declared in `mutation-governance-boundary.json` with no predicate, so `classify()` fails closed and returns `ERROR` for **every** subject; 26 tests red. `[F]` The remedy is **one predicate**, with Option A already specified across four determinations | none | none | **RECORD AS CANDIDATE.** Implementation, not redesign |
| `CE-02` | Every identity plane SHALL carry a lifecycle binding | `A14`:388 (`FB-2`) | `id-ledger.by_object` carries four fields and **0 history entries for 5,277 identities**, while the corpus plane is 1,579 of 1,579 historied. Live consequence: **192 objects hold two universal identities each**. `AIF-L15` legislates the transition; the plane has nowhere to write it | `CI-07` (supersession must be exercisable) | `AIF-L17` forbids deleting either identity, so the remedy is **forward compensation**, not deletion | **RECORD AS CANDIDATE.** Migration plus a schema binding |
| `CE-03` | No closed enumeration SHALL sit outside the extension mechanism | `A14`:467 (`FB-3`) | `KnowledgeCapability('future-unknown-capability')` → `ValueError`. The enum is not among the 13 vocabularies `UCKP-INV-14` proves extensible, so the invariant passes without reaching it. `[F]` `VocabularyRegistry.extend` already exists | `CI-03` | `ISD-G-09` makes disclosing a new closure an engine-plane change | **RECORD AS CANDIDATE.** Register the vocabulary and add a coercer |
| `CE-04` | Extending the validator beyond `L.3` SHALL require no amendment | `A08`:437 · `A07`:413 | `[F]` The validator already implements `CMG-INV-09` and `-12`, which `L.3` never enumerates — the corpus demonstrating **by practice** that exceeding `L.3` engages no amendment and no ratification. This is the located ground on which `CR-01` costs nothing constitutionally | `CR-01` · `UNK-R3-02` | The restrictive reading of `L.2` would condemn the present `-09`/`-12` behaviour as well | **RECORD AS CANDIDATE.** It is the argument that keeps `CI-01` out of amendment scope |
| `CE-05` | A vocabulary SHALL be extensible by registration rather than by editing a foundation source file | `A14`:623 · `A14`:584 | `[F]` Proved empirically: a reality with a novel calendar, a novel currency and a novel measurement system was admitted into the location model **by registering data, changing no source**. `[F]` 17 of 18 concerns measured demonstrably open to the future | `CE-03` | `ISD-G-07`/`-08` were **misclassified** as closures and are corrected by `A14`: they gate nothing, but `is_extensible()` does not reach them, so technology-openness is **unmeasured, not absent** | **RECORD AS CANDIDATE — THE STRONGEST POSITIVE RESULT IN THE SET** |
| `CE-06` | A category SHALL be admissible without a new supreme law | `A14`:180 (`RU-16`) · `A14`:173 (`RU-09`) | `GOVERNED_CATEGORIES` is open by Art. 17 via `VocabularyRegistry.extend`; `is_extensible() == True` is proved exercisable, so a category extension suffices and no *Universal Evolution Law* is needed. The terminal determination **rejects** creating a transaction authority and selects orchestration under an existing framework | `CE-05` | none | **RECORD AS CANDIDATE.** `A14` calls the scoping determination *"the cheapest high-leverage act in the register"* |

---

## 8 — CANDIDATE META-CONSTITUTIONAL REQUIREMENTS

Requirements about how a meta-requirements instrument must conduct itself. Every one is a
discipline the fourteen artifacts already keep, and each is stated here because keeping it was what
made the fourteen artifacts reconcilable at all.

| # | Candidate | SOURCE | RATIONALE | CONFLICTS | RECOMMENDED ACTION |
|---|---|---|---|---|---|
| `CM-01` | A derived instrument SHALL declare `AUTHORITY = NONE` and SHALL determine nothing | all fourteen artifacts (`CMG-L-12`) | Every one of the fourteen carries it in its front matter and in its footer, and `A01`:838 states the content: *"It closes no vacancy, disposes no reconciliation, nominates no T1 occupant, allocates no authority, and proposes no remediation"* | none | **INHERIT VERBATIM.** This document keeps it |
| `CM-02` | Every quantitative claim SHALL be executed, not read | `A02`:523 · `A01`:5 | *"Every quantitative claim was executed at `1e3e4ba9`, not estimated."* It is why `A02` could falsify `A01` and `A10` could correct `A07` | `A-03`, `A-P-05`, `A-R-05` and six more: execution is environment-local and hermeticity is untested | **INHERIT, WITH THE ASSUMPTION DISCLOSED** |
| `CM-03` | No prior result SHALL be accepted without independent verification — including this instrument's own | `A02`:515 | *"The correct posture toward every determination in this corpus, including this determination, is: trace it to constitutional text or to a hash-covered artifact, or treat it as unverified."* `A02` proved it on itself by falsifying `GAP-O-05` | none | **INHERIT VERBATIM — THE STRONGEST META-REQUIREMENT LOCATED** |
| `CM-04` | An observation SHALL NOT mutate what it measures; where it must, the state SHALL be recorded as observationally unavailable | `A08`:410 (`UNK-R4-02`) · `A14`:135 | `A08` declines to determine the certification state because `CK-REG-DRIFT` declares `write_scope: "projections"` — *"observation would alter the observed state."* `A08` introduces **observationally unavailable** as a residual class rather than guessing | none | **INHERIT.** It is the discipline that separates `register.sh --observe` from the transaction |
| `CM-05` | A determination SHALL record its own falsifiability and its own self-disclosure | `A14`:1090 · `A14`:1109 | `A14` carries explicit *Falsifiability* and *Self-disclosure* sections. `[I]` A meta-requirements instrument that cannot be falsified would be `CAA-INV-01` at instrument rank — structurally unfalsifiable, which `GAP-P-09` records as a defect | `K-02` bounds how far self-verification can reach | **INHERIT** |
| `CM-06` | No instrument SHALL declare the uncertainty space closed | `A04`:436 (`I.5`, `LXXVI.5`, `LXXVII.1`) | A reactive total procedure closes **dispositions**, never **discovery**. Under `LXXVI.5` a claim that the space were closed would itself be a recorded defect. `A04` proved the space open **constructively**, by discovering five new classes while testing whether new classes could be found | `LXXVII.3`'s exhaustiveness proof is sound and is about dispositions — the two must not be conflated | **INHERIT VERBATIM.** It bounds every count in the register |
| `CM-07` | An impossibility proof SHALL be stated at the strength the evidence carries, and SHALL be weakened when evidence requires | `A01`:831 | *"The impossibility proofs in this corpus have been getting weaker, and correctly so."* `EC-1` **was** performed; `UCCEP-F-004`'s competence limb was withdrawn as contradicted by committed Repository Truth. `A01` warns that restating the residue as categorical impossibility would be **regressing against located evidence** | none | **INHERIT.** It is the located ground for rejecting `K-12` as stated |
| `CM-08` | Scope SHALL NOT be transferred between planes: a certification result is not a readiness result and neither is an implementation-admission result | `A14`:1049 (`CM-2`) · `A08` corrections | `A14` refuses to read `P0-FINAL-CLOSURE-002`'s **certification** impossibility as a **readiness** determination, and separates implementation admission into its own section so the two are not conflated. `A11` Q28 and `A14` §2 together prove the planes disjoint | none | **INHERIT.** The disjointness is the most important structural fact in the consolidation |

---

## 9 — INTEGRATION SUMMARY

| Candidate class | Count | Requiring an amendment to `CMG-000001` | Requiring an external act | In-corpus and unblocked |
|---|---:|---:|---:|---:|
| Invariants (`CI-*`) | 10 | 0 | 0 | 10 |
| Requirements (`CR-*`) | 12 | 1 (`CR-08`, cost `LXXX.6`) | 0 | 11 |
| Constraints (`K-*`) | 16 | — inherited, not authored | — | 13 absolute · 2 eliminable · 1 assumption |
| Obligations (`CO-*`) | 8 | 0 | 0 | 8 |
| Validations (`CV-*`) | 7 | 0 | 0 | 7 |
| Proof obligations (`CP-*`) | 12 | 0 | 0 | 6 discharged · 5 permanently open · 1 unverifiable by construction |
| Redesign-elimination (`CE-*`) | 6 | 0 | 0 | 6 |
| Meta-constitutional (`CM-*`) | 8 | 0 | 0 | 8 |
| **TOTAL** | **79** | **1** | **0** | — |

**`[F]` No candidate in this analysis requires the external constituent act.** Every one is
in-corpus. That is a consequence of the plane disjointness `A14` and `A11` establish independently:
the whole of `META-B` — the T1 vacancy, `CMG-OQ-01`, `CMG-OQ-02`, `DEF-02`, `UCCEP-F-004` — bounds
*standing*, and none of the 79 candidates is a claim about standing.

**`[F]` One candidate carries a disclosed cost.** `CR-08` (`XXV.3` state mapping) would amend
`CMG-000001` and thereby revoke certification across all 44 artifacts under `LXXX.6`. This analysis
does not recommend it; it records the cost and routes the decision.

**`[I]` The three highest-leverage candidates, and the reason, stated once.** `CI-02`
(no self-certifying verification condition) because it is the mechanism by which every other
`META-A` defect stays invisible; `CR-09` (a genus definition of *act*) because it is one definition,
squarely in jurisdiction, needing no external authority, and it unblocks a question every phase in
the set had to defer; and `CE-04` (extension beyond `L.3` requires no amendment) because it is the
located argument that keeps `CI-01` and `CR-01` — the largest remediation in the set — outside
amendment scope entirely.

**`[F]` This analysis admits nothing.** It creates no instrument, drafts no clause, allocates no
ownership, and settles none of the seven owner readings it identifies as prerequisites
(`UNK-R3-02`, `UNK-R4-01`, `UNK-R6-01`, `UNK-R6-02`, `UNK-R7-01`, `UNK-R7B-01`, `UNK-R2-04`).
Whether to create the instrument at all is an owner's act under `LXXVI.2`, and `A13` determines that
architecture work is **not permitted** at HEAD.

---

*MCRF / STREAM-00 / WP-001A · CONSTITUTIONAL INTEGRATION ANALYSIS · AUTHORITY = NONE (DERIVED ANALYSIS ONLY).*
*Nominates; admits nothing. Valid for the fourteen artifacts as extracted, and for no later state.*
