# Ω-P2-E1 — CERTIFIED EVOLUTION EPOCH · CONSTITUTIONAL POPULATION MODEL

> **STANDING: ADMITTED TO REPOSITORY TRUTH.**
> Admitted under Ω-E06-B through the located registration transaction, in the canonical home
> `00-MASTER/EVOLUTION-001/` proven at Ω-P1 §0 — **REUSE**, no new home, no new namespace, no
> new identifier. `00-MASTER/` is excluded from corpus registration
> (`00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md`; `00-BOOK/tools/config.py`
> `EXCLUDE_DIR_PREFIXES`), so admission consumes no corpus identity and introduces no
> registration drift. The disposition is recorded as `DEC-OMEGA-P-03` in
> `00-MASTER/UCDA-000001/ucda-decisions.json` and indexed at
> `00-MASTER/MCP-004-MASTER-DECISIONS.md` §05.
>
> **AUTHORITY IS UNCHANGED — NONE (DERIVED TRUTH).** Admission changes standing, never
> authority: where this certificate and a located instrument differ, **the located instrument
> governs**. Every certificate, cardinality and relation below remains the epoch measurement
> §0 declares it to be, taken at the program state named in the header; admission neither
> restates nor amends any of them, and closes no enumeration.
>
> The discharged candidate banner read: *"STANDING: PROVISIONAL CANDIDATE — NOT REPOSITORY
> TRUTH. Untracked … This certificate admits itself no more than Ω-P1 or Ω-P2 admit
> themselves."* It did not admit itself; a later act did.

| Field | Value |
|---|---|
| Epoch | **Ω-P2-E1** |
| Class | Certified Evolution Epoch — immutable evidence snapshot · reproducible proof baseline · point-in-time certification · historical reference state · **one epoch among infinitely many future epochs** |
| AUTHORITY | **NONE — DERIVED TRUTH.** Legislates nothing. Where this certificate and a located instrument differ, **the located instrument governs**. |
| HEAD | `43dec4a5e201a93019aac150f768ab15ec1d5d08`, branch `integration/recovery-001` |
| Working tree | 70 modified tracked · 3 untracked candidates |
| PROGRAM-STATE HASH | `879b1abdb2b0efeed4d8018f635761e3f5b7166d1e2b8d20ea1288d6be2476d0` |
| Certifier | `.runtime/omega-p2-e1-certify.py` — gitignored (`.gitignore:12`), therefore **CREATE = 0** |
| Certification body digest | `21d48940ecaaeb1aa1830fea1b1dcf6753fcbe3845a2d5cf250165490e1c70b0` (421 lines, byte-identical across consecutive runs) |
| Lattice verifier | `.runtime/omega-p2-lattice.py` — output digest `94e0cfce5ab836f2d6c14a43dd5d3d530e35728366fe3c4ddae05bee16f7823b`, verdict `LATTICE VALID — EPOCH CERTIFIABLE` |
| Certificates | **40 issued · 0 refuted · 0 lattice failures** |
| Verdict | **CERTIFIED AS EVOLUTION EPOCH Ω-P2-E1** |
| Lineage predecessor | `Ω-P2-FINAL-1-FROZEN-POPULATION-MODEL.md` — superseded and withdrawn; see §9 |

---

## 0. Epoch semantics — what certification does and does not do

**Certification SHALL NEVER restrict future evolution.**

Every theorem in this certificate carries the same scope clause, stated once here and binding
on all forty without exception:

> **EPOCH SCOPE.** This theorem certifies Evolution Epoch Ω-P2-E1 only. It does not prohibit
> future constitutional evolution, future registrations, future recognitions, future
> authorities, future populations, future ontologies, future capabilities, future proofs, or
> future certified epochs.

The certificate closes no enumeration. It is consistent with `CMG-000001` `XIII.2` (Kind set
OPEN), `LXXVI.5` (expansion unbounded in count; *"any apparent limit SHALL be read as a
defect"*), `XI.9` (`CMG-INV-09`: no enumeration closed except by an invariant naming the
closure), `XII.2` (*"The value set IS OPEN"*), `XIV.7` (ontology open to new entity types), and
`CEP-009` `B.3.3` (*"The enumeration of B.3.2 SHALL NEVER be assumed complete"*).

Two things follow, and both are asserted here so no later reader can mistake them:

1. **A cardinality is an epoch measurement, never a ceiling.** `|P1| = 1194` records what the
   located derivation rule yields at this program state. It states nothing about any future
   state and imposes no bound.
2. **A closed relation is an epoch relation, never a prohibition.** `P1 ∩ P7 = ∅` records that
   the two membership predicates presently have no common satisfier. It does not forbid a
   future instrument from making them overlap.

---

## 1. Certified populations — all nine attributes, each proven

Certificates `C-1.1` … `C-1.9`. Every proof is a recomputation, not a citation of a prior
claim.

| Population | Predicate | Owner | Representation | Cardinality |
|---|---|---|---|---|
| **P1** Registration | `μ₁(p) ≡ p ∈ A ∧ ext(p) ∈ INCLUDE_EXTENSIONS ∧ ¬∃e ∈ EXCLUDE_DIR_PREFIXES : p.startswith(e)` | `REG-AUTO-001` (`CMG-DLG-13`) + UKB | `00-BOOK/DATA/artifacts.json` | **1194** |
| **P2** Constitution Registry | `μ₂(r) ≡ r ∈ CMG-REGISTRY.json:artifacts` | `CMG-000001` Art XV (`CMG-RET-02`) | `00-CMG/CMG-REGISTRY.json:artifacts` | **43** |
| **P3** Recognition | `μ₃(p) ≡ p satisfies IV.1(f)` | `CMG-000001` Art XII/XV | `π(P2)` | **43** |
| **P4** Standing | `μ₄(p) ≡ a located rule assigns p exactly one XII.2 value` | `CMG-000001` Art XII (`CMG-RET-03`) | `artifacts[].standing` (verified limb only) | **> 43, exact ND** |
| **P5** Located Owner | `μ₅(p) ≡ p named as owner in a delegation record ∧ p resolves` | `CMG-000001` Art XVIII/LXXXII (`CMG-RET-05`) | `LXXXII.2` table; `concerns` projection | **58** |
| **P6** Located Authority | `μ₆(p) ≡ μ₅(p) ∧ μ₃(p)` | `CMG-000001` Art XVIII/LXXXII | `concerns[].owner` via `artifacts[].id` | **43** |
| **P7** Operational Realization | `μ₇(p) ≡ p ∈ A ∧ (p.startswith("00-MASTER/") ∨ ext(p) = ".py")` | `MCS-000`; per-programme homes | `config.py:809` excluded prefixes | **2871** |
| **P8** Constitutional Corpus | `μ₈ ≡ μ₁` | as P1 | as P1 | **1194** |
| **P9** Latent Constitution | `μ₉(p) ≡ IV.1(a)∧(b)∧(c)∧(d)∧(e) ∧ ¬IV.1(f)` | `CMG-000001` Art XII; detection → Art LII | **none located** | **ND — T-ND1** |
| **P10** Audit Subject | `μ₁₀(x) ≡ x is the audited subject of a record present in the Audit Registry` | `CEP-010` (`CMG-DLG-10`, `-11`) | distributed `findings` arrays | **53 records; subjects ND — T-ND2** |

### 1.1 The nine attribute certificates

| ID | Subject | Proof |
|---|---|---|
| `C-1.1-P1` | `μ₁`'s extension **equals** its representation | recomputed over `\|A\|=5354` → 1194; representation 1194; both set differences **0** |
| `C-1.1-P2` | path projection of P2 is injective | 43 records → 43 distinct paths |
| `C-1.1-P3` | `P3 = π(P2)` | identity by construction under `IV.1(f)` + `X.1` |
| `C-1.1-P5` | every `owner_paths` entry resolves (`LXXXII.4`) | 15 entries, **0** unresolved |
| `C-1.1-P6` | every delegation `owner` id resolves to a P2 record | 55 owner-bearing records, **0** unresolved |
| `C-1.1-P7` | `μ₇` is the positive reading of `μ₁`'s exclusion clause | `\|P1 ∩ P7\| = 0`; `μ₁` excludes `00-MASTER/` and every `.py`, which are exactly `μ₇`'s two disjuncts |
| `C-1.1-P8` | `P8 = P1` | `REGISTRATION_SCOPE`: *"eligible == this set"*; `UCOS-RECON-C1`: *"Only Repository Corpus is registered"* |
| `C-1.2` | every predicate is **decidable** over the carrier | `μ₁` evaluated on all 5354 elements; undecided **0** |
| `C-1.3` | every canonical owner **resolves** | 5/5 present |
| `C-1.4` | every located representation **parses** | `artifacts.json` `aca7de8b…`, `CMG-REGISTRY.json` `4d8242bb…` |
| `C-1.5` | derivation rules are **deterministic** | `μ₁` recomputed from an independent `git` invocation: 1194 = 1194 |
| `C-1.5-z` | the `-z` clause is **load-bearing** | without `-z` the identical predicate yields **1095**, a deficit of **99** |
| `C-1.6` | inclusion ∧ exclusion are **mutually exclusive** | elements satisfying both: **0** |
| `C-1.7` | inclusion ∧ exclusion are **jointly exhaustive** | elements matching inclusion yet excluded for no located reason: **0** |
| `C-1.8` | every derivable cardinality is **reproduced** | see the table above |
| `C-1.9` | every evidence source is present and digestible | `config.py` `bab1a8e4…`, `cmg_validate.py` `b98becc0…`, `id-ledger.json` `61bffc5f…` |

`C-1.6` and `C-1.7` together certify that the inclusion and exclusion rules **partition** the
carrier. That is what makes each membership predicate a function rather than a preference.

`C-1.5-z` is retained as a certificate rather than a footnote because an independent verifier
who omits `-z` will not reproduce `|P1| = 1194` and will conclude, wrongly, that the
representation is drifted by 99 records.

---

## 2. Certified lattice — with the justification, not the token

```
         P1   P2   P3   P4   P5   P6   P7   P8   P9  P10
P1        =  OVL  OVL  OVL  OVL  OVL  DIS    =   ND   ND
P2      OVL    =    =  SUB  SUB    =  OVL  OVL  DIS   ND
P3      OVL    =    =  SUB  SUB    =  OVL  OVL  DIS   ND
P4      OVL  SUP  SUP    =  OVL  SUP  OVL  OVL  SUP   ND
P5      OVL  SUP  SUP  OVL    =  SUP  OVL  OVL   ND   ND
P6      OVL    =    =  SUB  SUB    =  OVL  OVL  DIS   ND
P7      DIS  OVL  OVL  OVL  OVL  OVL    =  DIS   ND   ND
P8        =  OVL  OVL  OVL  OVL  OVL  DIS    =   ND   ND
P9       ND  DIS  DIS  SUB   ND  DIS   ND   ND    =   ND
P10      ND   ND   ND   ND   ND   ND   ND   ND   ND    =
```

Histogram over 100 ordered pairs: `= 18 · SUB 7 · SUP 7 · OVL 32 · DIS 10 · ND 26`.

| Property | Certificate | Why PASS is justified |
|---|---|---|
| **uniqueness** | PASS | Branch attribution measured, not asserted: `reflexive 10 · extensional 42 · P4-table 18 · P9-table 16 · P10-sort 14 · fallthrough 0`, summing to **100**. The `AssertionError` fallthrough is **measured at zero**, not presumed unreachable. The six values are pairwise incompatible as set relations. |
| **antisymmetry** | PASS (90) | Converse closure verified elementwise on all 90 off-diagonal pairs: **0** violations, **0** mutual `SUB`. The inverse table is verified to be an **involution** (`INV[INV[r]] = r` for all six values). |
| **transitivity** | PASS (26) | All 26 instantiating triples enumerated **and printed** with their conclusions. Non-zero, so not vacuous. `transitivity-skipped-ND = 0` certifies that **no** transitivity obligation was discharged by appeal to non-derivability. |
| **acyclicity** | PASS | 7 strict edges `P2<P4, P2<P5, P3<P4, P3<P5, P6<P4, P6<P5, P9<P4`. Three-colour DFS over all 10 vertices, **10/10 closed**, back-edges **0**. Longest strict chain: **2 vertices**. |
| **closure** | PASS (80) | `=` proven a **congruence**: for both equivalence classes `{P1,P8}` and `{P2,P3,P6}`, equals are substituted against **every** column — 80 substitutions, **0** row divergences. This proves congruence rather than coincidence of cardinality. |
| **completeness** | PASS | 74/100 derived; 26/100 `ND`, **each** carrying a certificate, each promoted to a theorem in §3. |
| disjointness propagation | **VACUOUS** | **0** instantiating triples, and this is *proven* rather than observed: the only `DIS` pairs are `{P1#P7, P8#P7}` and `{P2,P3,P6}#P9`; the only strict superclasses are `P4` and `P5`; neither is disjoint from anything; therefore no triple can instantiate the antecedent. A vacuous property constrains nothing and is certified as constraining nothing — **not** reported as PASS. |

### 2.1 Decisive cells, with their arithmetic

| Cell | ∩ | left ∖ right | right ∖ left |
|---|---|---|---|
| `P1 OVL P3` | **23** | 1171 | **20** |
| `P1 OVL P5` | 27 | 1167 | 31 |
| `P3 OVL P7` | **15** | 28 | 2856 |
| `P5 OVL P7` | 16 | 42 | 2855 |
| `P1 DIS P7` | **0** | 1194 | 2871 |

### 2.2 Witnesses closing the six non-extensional cells

| ID | Path | closes |
|---|---|---|
| W1 | `00-MASTER/UCL-000001/09-VALIDATION-REPORT.md` | `P4 ∖ P3 ≠ ∅` (`XII.6`), `P4 ∖ P5 ≠ ∅` |
| W2 | `00-MASTER/UAKOS-CLOSURE-006/CONST-08-PIPELINE-CONSTITUTION.md` | `P4 ∖ P1 ≠ ∅` |
| W3 | `engine/determinism/blueprints/BP-DATA-0001.json` | `P1 ∖ P4 ≠ ∅` — 1195 bytes, **zero** matches for `authority`, `scope`, `conflict`, `amend`, `governs`, `binds`, so it fails `IV.1(a)(b)(c)(e)` and lies in no `XII.2` limb |
| W4 | `engine/kernel/registry.py` | `P7 ∖ P4 ≠ ∅` on the same lexical grounds |
| W5 | `00-CMG/CMG-000001-…md` | `P4 ∖ P7 ≠ ∅`; its `XII.6` lexical hit is a *mention* of its own clause and is not load-bearing |
| W6 | `05-GENERATION` | `P5 ∖ P4 ≠ ∅` — a **directory** named as located owner in `CMG-DLG-36` |

---

## 3. Certified NOT-DERIVABLE theorems — five distinct outcomes

Taxonomy declared before use, and every class exercised:

| Class | Meaning |
|---|---|
| NOT MEASURED | a derivation rule exists but no owner executes it |
| NOT REPRESENTED | no canonical representation exists to measure |
| NOT DECLARED | no located clause supplies a decidable membership test |
| CONSTITUTIONALLY UNKNOWABLE | the competent authority does not exist at this epoch |
| IMPLEMENTATION LIMITATION | the located instrument cannot express the value |

### T-ND1 — `|P9|` is NOT DERIVABLE · **NOT REPRESENTED** (primary) + **NOT MEASURED** (consequent)

`cmg_validate.py` declares exactly 16 checks — `check_conformance, check_identifier_families,
check_members_unique, check_homes, check_classification, check_concerns, check_superiors,
check_acyclicity, check_precedence, check_lifecycle, check_lineage, check_gaps,
check_closed_enumerations, check_namespaces, check_no_persisted_conflict, check_source_binding`
— and contains **0** lines matching `/latent/i`. Across all tracked `.py`, exactly **1** file
contains the token, `rfp_engine.py`, in a comment about producers.

Each of the other four classes is **excluded by proof**:
- not *NOT DECLARED* — `IV.1` defines the predicate and `XII.5` names the standing;
- not *CONSTITUTIONALLY UNKNOWABLE* — `XII.5` states *"Latency IS a detectable defect"*, which
  asserts decidability, and the competent authority exists at `CMG-RET-02`;
- not *IMPLEMENTATION LIMITATION* — no instrument attempts the measurement, so none fails at it;
- *NOT MEASURED* is consequent rather than primary: with no representation there is nothing for
  a measurement to read.

`CMG-GAP-07` records the rule CLOSED and the enumeration as *"a detection outcome, not a gap"* —
so what is absent is a representation, not law.

### T-ND2 — P10's subject projection is NOT DERIVABLE · **NOT REPRESENTED**

53 distinct located audit records. Those carrying a `subject` field: **1**. Of `CEP-010`
`XIX.1`'s eight mandated elements, five — *audited subject*, *governing constitution*,
*criteria assessed*, *state*, *program-state hash* — have **no** located field in the record
schema; `evidence` is present in 33/53 and `disposition` in 45/53.

Not *NOT DECLARED*: `XIX.1` mandates the element explicitly, so the requirement is declared and
the representation is absent.

### T-ND3 — exact `|P4|` is NOT DERIVABLE · **NOT DECLARED** (`XII.6` limb) + **NOT REPRESENTED** (`XII.5` limb)

`XII.6` declares the *semantics* — the `AUTHORITY = NONE (DERIVED TRUTH)` convention **is**
DECLARATIVE standing — and declares **no** syntactic form, no field, no schema and no position.
A lexical sweep therefore cannot be the membership test, and is demonstrably unsound as one:
over 5354 tracked files it returns 725 matches, including `CMG-000001` itself, which merely
states `XII.6`, and `CEP-002`. The test is **NOT DECLARED**.

The `XII.5` limb reduces to T-ND1.

**The lower bound is derivable and is certified:** `XII.4` makes registry verification
constitutive and the registry verifies **43**; W1 proves the `XII.6` limb non-empty; therefore
`|P4| > 43` **strictly**, with no derivable upper bound. `T-M2` corroborates: of the six
declared standing values, **4** are used and `DECLARATIVE` and `LATENT` are declared-but-unused.

### T-ND4 — the **correctness** of P3's membership is **CONSTITUTIONALLY UNKNOWABLE**

P3 is constituted by `CMG-000001` Art XV. That instrument's own standing is PROVISIONAL under
`X.12` (`CMG-L-12`) because `CMG-OQ-01` — *"Which authority is competent to ratify this
instrument?"* — is open, and `LXXX.4` caps the outcome at `READY-PROVISIONAL` while `CMG-OQ-01`
and `CMG-OQ-02` remain open.

Measured: vacancies **1** (`VAC-01`); open-question status `CMG-OQ-01 OPEN · 02 OPEN · 03 OPEN ·
04 CLOSED · 05 OPEN · 06 CLOSED · 07 OPEN`; `cmg_validate.py` readiness `READY-PROVISIONAL`,
findings **0**.

This is unknowability of a different kind from T-ND1…3: the value is not missing from a store —
**the authority competent to settle it does not exist at this epoch.** Under the Universal
Evolution Principle that is an epoch property and nothing more: a future epoch in which the
ratification authority is constituted will settle it, and this certificate does not stand in
the way.

### T-ND5 — the **IMPLEMENTATION LIMITATION** class is **EMPTY** at this epoch

One candidate was found and **eliminated rather than recorded**: `git ls-files` without `-z`
applies `core.quotePath` escaping, yielding 1095 instead of 1194 — a deficit of 99 paths
containing non-ASCII bytes. That was a limitation of the **measurement method**, not of a
located instrument, and it was removed by correcting the method. No residual member remains.

The class is reported empty rather than omitted, so that the taxonomy is shown to be exercised
and not merely declared.

---

## 4. Certified mapping theorems

Each mapping is certified on domain, codomain, totality, injectivity, surjectivity,
bijectivity, composition and inverse.

| ID | Mapping | dom → cod | Totality | Inj. | Surj. | Bij. | Inverse |
|---|---|---|---|---|---|---|---|
| **T-M1** | `π : P2 → A`, `a[path]` | 43 → 5354 | TOTAL | **INJ** | non-surj | no | exists on image; **bijective onto P3** |
| **T-M2** | `ρ : P2 → XII.2 standings` | 43 → 6 | TOTAL | non-inj (img 4) | non-surj | no | none |
| **T-M3** | `ω : concerns → owner ids` | 60 → — | **PARTIAL 55/60** | non-inj (img 43) | n/a | no | none |
| **T-M4** | `ι : P6 → P3` | 43 → 43 | TOTAL | **INJ** | **SURJ** | **BIJECTIVE** | `ι` itself |
| **T-M5** | `κ : P3 → P5` | 43 → 58 | TOTAL | **INJ** | non-surj (by 15) | no | exists on image |
| **T-M6** | `δ : A → {0,1}` (`μ₁`) | 5354 → 2 | TOTAL | non-inj | **SURJ** | no | none; `P1 = δ⁻¹(1)`, `\|δ⁻¹(0)\| = 4160` |
| **T-M7** | `id : P1 → universal_id` | 1194 → — | TOTAL | **INJ** | n/a | no | exists on image |
| **T-M8** | `hash : P1 → content_hash` | 1194 → — | TOTAL | non-inj (img 1192) | n/a | no | none |
| **T-M9** | `λ : P1 → id-ledger.by_path` | 1194 → 1225 | TOTAL | **INJ** | non-surj (by 31) | no | exists on image |

Four of these carry constitutional weight beyond their arithmetic:

- **T-M4 is bijective and the bijection is law-backed, not accidental.** `X.1` (`CMG-L-01`)
  forces `P6 ⊆ P3`; `XI.3` (`CMG-INV-03`, *"no owner lacks a concern"*) forces `P3 ⊆ P6`.
  Therefore `P6 = P3` by law and not by coincidence of cardinality.
- **T-M7 certifies `XI.8`** (`CMG-INV-08`, identity uniqueness and permanence) over P1: total
  and injective, 1194 → 1194 distinct `universal_id`.
- **T-M8 is non-injective by 2 collision classes, and this is a property, not a defect.** No
  located clause requires content injectivity — `XI.8` constrains *identifiers*, not content.
- **T-M9's non-surjectivity is by design.** The 31 surplus ledger entries are
  RETAINED-BUT-RETIRED identities under `config.py:800-808` and `UMB-017 C-05`: never
  renumbered, never reused, never emitted.

**T-M3's partiality and non-injectivity are both licensed.** Partial by the 5 records
`CMG-DLG-36…40` that carry `owner_paths` only. Non-injective because `XIV.2` declares
`Concern → Owner` as **N:1**, and `XI.2`'s verification text *"injective on concerns"* is the
functionality condition — every concern has exactly one owner — which holds.

### 4.1 Certified compositions

| Composition | Result |
|---|---|
| `T-M4 ; T-M5` : `P6 → P3 → P5` | TOTAL, INJECTIVE, NON-SURJECTIVE; verified `43 → 43 → 58` |
| `T-M6 ; T-M7` : `A → {0,1} → id` | defined exactly on `δ⁻¹(1) = P1`; 1194 artifacts, 1194 distinct ids |
| `ρ ∘ π⁻¹` : `A ⇀ standings` | **defined exactly on P3 and nowhere else.** This is the formal statement that **standing attaches to recognition and not to paths** — no standing map exists on the carrier |

---

## 5. Certified layer-independence theorems

| ID | Theorem | Proof |
|---|---|---|
| **T-L1** | Registration does **not** imply Recognition | `\|P1 ∖ P3\| = 1171` |
| **T-L2** | Recognition does **not** imply Registration | `\|P3 ∖ P1\| = 20`, including **`REG-AUTO-001`**, the canonical owner of P1 under `CMG-DLG-13` |
| **T-L3** | Registration and Recognition are **independent** predicates | all three regions inhabited: `1171 / 20 / 23` |
| **T-L4** | Operational realization does **not** preclude Recognition | `\|P3 ∩ P7\| = 15`, every member `standing = FOUNDATIONAL` |
| **T-L5** | Operational realization does **not** imply Authority | `\|P7 ∖ P6\| = 2856`; witness W4 |
| **T-L6** | Registration does **not** imply Authority | `\|P1 ∖ P6\| = 1171` |
| **T-L7** | Authority **implies** Recognition | `P6 ⊆ P3`; forced by `X.1` |
| **T-L8** | Recognition **implies** Authority at this epoch | `P3 ⊆ P6`; forced by `XI.3`; hence `P6 = P3` |
| **T-L9** | Registration and Operational realization are **disjoint** | `\|P1 ∩ P7\| = 0`; forced by `μ₁`'s exclusion of `00-MASTER/` and of every `.py` |
| **T-L10** | Located ownership does **not** imply constitutional artifacthood | `\|P5 ∖ P3\| = 15`; W6 is a directory, which no `XII.2` rule reaches, while `XX.2` requires an Owner to be a constitutional artifact |

T-L1 through T-L3 jointly certify that **registration and recognition are two independent
predicates over one carrier.** T-L4 and T-L5 jointly certify that **residence in operational
memory is orthogonal to both recognition and authority** — it neither confers nor precludes
either. T-L7 and T-L8 are the two positive implications, and both are law-backed rather than
extensional accidents.

Every one of the ten carries the **EPOCH SCOPE** clause of §0.

---

## 6. Certification verdict

| Measure | Value |
|---|---|
| Certificates issued | **40** |
| Certificates refuted | **0** |
| Lattice failures | **0** |
| Non-vacuity | `antisymmetry 90 · transitivity 26 · closure 80 · transitivity-skipped-ND 0 · disjointness-propagation 0 (certified vacuous)` |
| Determinism | two consecutive certifier runs byte-identical; body digest `21d48940…` |
| Tree effect | none — both verifiers live in gitignored `.runtime/`; `CREATE = 0` |

**The Population Model has been Certified as Evolution Epoch Ω-P2-E1.**

The certified epoch becomes immutable evidence. The living constitutional universe remains
infinitely evolvable.

---

## 7. Replay instructions for an independent verifier

```
git rev-parse HEAD                      # expect 43dec4a5e201a93019aac150f768ab15ec1d5d08
python3 .runtime/omega-p2-lattice.py    # expect LATTICE VALID - EPOCH CERTIFIABLE; digest 94e0cfce…
python3 .runtime/omega-p2-e1-certify.py # expect 40 certificates, 0 refuted; digest 21d48940…
```

Two replay preconditions, both constitutional rather than incidental:

1. **`git ls-files` MUST be invoked with `-z`.** Certificate `C-1.5-z` proves the deficit is 99
   records. A verifier omitting it will mis-derive P1 and wrongly report registry drift.
2. **The program state is `879b1abd…`, not the commit.** `HEAD` is `43dec4a` but the tree
   carries 70 modified tracked files and 3 untracked candidates. A verifier who checks out
   `43dec4a` cleanly reproduces §1 and §2 in full — those depend only on tracked content — but
   is measuring a **different program state** from the one certified here.

---

## 8. What this certificate does NOT do

8.1 **Freezes nothing.** No architecture, constitutional universe, knowledge, ontology,
taxonomy, capability space or evolution mechanism is frozen, closed, finalized or made
permanent. Every enumeration it touches remains open, and every cardinality is an epoch
measurement.

8.2 **Replays no Ω-P1 disposition.** Not begun.

8.3 **Generates no Ω-P2-R.** Not begun.

8.4 **Records no finding.** Five clause-level tensions were encountered while proving the
mapping and standing theorems — `XVIII.2` versus `LXXXII.2`'s five columns; `XVIII.2`'s
*(EXTEND or REUSE)* versus `RETAIN`; `XX.2` versus the five path-only owners including three
directories; `XII.2`/`XII.6` DECLARATIVE versus `IV.2`'s binding-force requirement; `XIX.1`'s
five unrepresented record elements. All are **held** under `LXXVII.5`, none raised. Where a
measured property could be mistaken for a defect it is certified explicitly as a property —
T-M3's non-injectivity (licensed by `XIV.2`) and T-M8's collisions (outside `XI.8`'s scope).

8.5 **Creates no authority, registry, lifecycle, namespace, identifier or engine.** `CREATE = 0`.
Both verifiers are inside the gitignored `.runtime/` zone, so they consume no corpus identity
and add no candidate.

8.6 **Amends nothing.** No clause, column, enumeration or identifier of any instrument is
altered.

8.7 **Admits itself no more than Ω-P1 or Ω-P2 do.** By `CEP-010` `XVIII.4` — *"An assessment
absent from the Registry SHALL be deemed non-existent, and reliance upon it IS PROHIBITED"* —
this certificate holds no standing as an assessment until admitted. Its presence as a third
untracked entry under `00-MASTER/EVOLUTION-001/` blocks re-assertion of the `UCOS-RFP-001`
fixed point by `CLO-01` and `CLO-05`, exactly as Ω-P1 §6 already recorded for itself.

> **Discharged under Ω-E06-B.** The blocking condition stated here was measured again and
> confirmed by `rfp_engine.py --gate`, which named this certificate among four
> `pre-existing untracked` entries. Admission through the located registration transaction
> discharged it. No certificate, cardinality, relation or verdict recorded above was altered
> to reach the fixed point.

---

## 9. Lineage — supersession of the freeze-titled predecessor

`Ω-P2-FINAL-1-FROZEN-POPULATION-MODEL.md` was issued as the Candidate Evolution Epoch. It is
**superseded and withdrawn** by this certificate, on two grounds:

1. Its title and §6 used the vocabulary *freeze / frozen / permanently*, which the Universal
   Evolution Principle prohibits. `CMG-000001` `V.4` requires terminology to be
   single-canonical, and `V.5` forbids introducing a term where a located one exists — the
   located term is **Certified Evolution Epoch**.
2. Its entire content is carried forward here without loss and with the certification added.

Withdrawal destroys no constitutional history. The predecessor was an untracked CANDIDATE that
was never registered and never recognized, so it was never part of Repository Truth and
`X.11` (Preservation) does not reach it. Its substance survives in §§1–5 above; the
recomputation that produced it survives in `.runtime/omega-p2-lattice.py`, which still runs
and still reports `LATTICE VALID`.

**One vocabulary distinction is preserved deliberately.** *Freeze* remains a **located
constitutional term**: `CMG-DLG-07` delegates *"Freeze operation: baselines, immutability, drift
protection, supersession mechanics, version lineage, historical preservation, freeze registry"*
to `CEP-007`. The Universal Evolution Principle prohibits freezing the architecture, the
constitutional universe, knowledge, ontology, taxonomy, capability space and the evolution
mechanism — it does not repeal `CEP-007`, and this certificate does not purge the located term
where it names that owner's concern. Every occurrence of the word in this certificate is either
a negation (§8.1 and the closing line) or a citation of the withdrawn predecessor's own
vocabulary (§9); none asserts a freeze. The verifier output was corrected from
`FREEZE ADMISSIBLE` to `EPOCH CERTIFIABLE` for the same reason, which is why its digest is
`94e0cfce…` and not the predecessor's.

---

*END OF CERTIFICATE — Ω-P2-E1 · AUTHORITY NONE (DERIVED TRUTH) ·
STANDING ADMITTED (Ω-E06-B; issued as PROVISIONAL CANDIDATE) ·
HEAD `43dec4a` · PROGRAM-STATE `879b1abd…` · 40 CERTIFICATES · 0 REFUTED · 0 LATTICE FAILURES ·
CERTIFIED AS EVOLUTION EPOCH Ω-P2-E1 · NOTHING FROZEN · NO DISPOSITION TAKEN · NO FINDING RAISED ·
Ω-P1 REPLAY NOT BEGUN · Ω-P2-R NOT BEGUN*
