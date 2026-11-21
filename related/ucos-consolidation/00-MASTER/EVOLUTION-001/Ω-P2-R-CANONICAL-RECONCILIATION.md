# Ω-P2-R — CANONICAL CONSTITUTIONAL RECONCILIATION

> **STANDING: ADMITTED TO REPOSITORY TRUTH.** Admitted under Ω-E06-B through the located
> registration transaction, in the canonical home `00-MASTER/EVOLUTION-001/` proven at Ω-P1 §0
> — **REUSE**, no new home, no new namespace, no new identifier. `00-MASTER/` is excluded from
> corpus registration (`00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md`;
> `00-BOOK/tools/config.py` `EXCLUDE_DIR_PREFIXES`), so admission consumes no corpus identity
> and introduces no registration drift. The disposition is recorded as `DEC-OMEGA-P-04` in
> `00-MASTER/UCDA-000001/ucda-decisions.json`; the fifteen proposition outcomes this document
> serializes are recorded as `DEC-OMEGA-P-05`, whose canonical owner is this document. Both are
> indexed at `00-MASTER/MCP-004-MASTER-DECISIONS.md` §05.
>
> **AUTHORITY IS UNCHANGED — NONE (DERIVED TRUTH).** Admission changes standing, never
> authority: where this document and a located instrument differ, **the located instrument
> governs**. Admission introduces no reasoning, no measurement and no interpretation, so the
> PURE SERIALIZATION property below is preserved.
>
> **PURE SERIALIZATION.** This document introduces no reasoning, no measurement, no
> interpretation, no constitutional claim, no finding, no disposition and no proof. Every
> statement resolves to a certified theorem or a Repository Truth measurement carried in
> the certified namespaces named in §2.

| Field | Value |
|---|---|
| Document | Ω-P2-R — canonical reconciliation, serialized |
| Class | Deterministic serialization of already-certified knowledge |
| AUTHORITY | **NONE — DERIVED TRUTH.** Where this document and a located instrument differ, **the located instrument governs**. |
| Serializer | `.runtime/omega-p2-r-serialize.py` — gitignored (`.gitignore:12`), therefore **CREATE = 0** |
| Certified producers | loaded by AST literal extraction; **neither executed, neither rerun** |
| Source A | `.runtime/omega-p2-phase4-replay.py` — digest `0aa3097589c7d85d` |
| Source B | `00-MASTER/EVOLUTION-001/Ω-P2-E1-CERTIFIED-EVOLUTION-EPOCH.md` — digest `c45e1a8a2034f4bc` |

---

## 1. Mission

Reconcile every Ω-P1 proposition against Repository Truth, and record the outcome so that
an independent verifier reaches the identical result or names the exact failed premise.

| Phase | Activity | State |
|---|---|---|
| Ω-P1 | determination — measurement only | closed, PROVISIONAL CANDIDATE |
| Ω-P2 | reconciliation | superseded by the phases below |
| Ω-P2-E1 | Certified Evolution Epoch — population model | certified |
| Phase-4 | constitutional replay from the certified epoch | certified |
| Phase-5 | this serialization | Ω-P2-R |

Provenance: §14 lineage. No mission statement beyond the above is asserted.

## 2. Repository Truth baseline

Carried by certified measurement `M-17`, quoted verbatim:

> present program state 879b1abd..., HEAD 43dec4a, 70 modified tracked + 3 untracked; CLO-01 precondition initial_dirty_entries=0 is UNMET

| Element | Value | Provenance |
|---|---|---|
| HEAD | `43dec4a5e201a93019aac150f768ab15ec1d5d08` | Ω-P2-E1 header |
| PROGRAM-STATE HASH | `879b1abdb2b0efeed4d8018f635761e3f5b7166d1e2b8d20ea1288d6be2476d0` | Ω-P2-E1 header |
| Working tree | 70 modified tracked · 3 untracked candidates | Ω-P2-E1 header |

No measurement is taken by this serialization. The baseline is read, not observed.

## 3. Certified Evolution Epoch summary

| Element | Value |
|---|---|
| Epoch | **Ω-P2-E1** |
| Class | Certified Evolution Epoch — immutable evidence snapshot · reproducible proof baseline · point-in-time certification · historical reference state · **one epoch among infinitely many future epochs** |
| Certification body digest | `21d48940ecaaeb1aa1830fea1b1dcf6753fcbe3845a2d5cf250165490e1c70b0` (421 lines, byte-identical across consecutive runs) |
| Lattice verifier | `.runtime/omega-p2-lattice.py` — output digest `94e0cfce5ab836f2d6c14a43dd5d3d530e35728366fe3c4ddae05bee16f7823b`, verdict `LATTICE VALID — EPOCH CERTIFIABLE` |
| Certificates | **40 issued · 0 refuted · 0 lattice failures** |
| Verdict | **CERTIFIED AS EVOLUTION EPOCH Ω-P2-E1** |

Epoch semantics, quoted verbatim from Ω-P2-E1 §0:

> **Certification SHALL NEVER restrict future evolution.**
>
> **EPOCH SCOPE.** This theorem certifies Evolution Epoch Ω-P2-E1 only. It does not
> prohibit future constitutional evolution, future registrations, future recognitions,
> future authorities, future populations, future ontologies, future capabilities, future
> proofs, or future certified epochs.

> 1. **A cardinality is an epoch measurement, never a ceiling.**
> 2. **A closed relation is an epoch relation, never a prohibition.**

## 4. Population Model summary

Serialized from the Ω-P2-E1 §1 population table, verbatim:

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

Lattice, serialized from Ω-P2-E1 §2:

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

| Lattice element | Value | Provenance |
|---|---|---|
| equivalence classes | `{P1,P8}` `{P2,P3,P6}` | Ω-P2-E1 §2 closure |
| strict containment edges | 7 | Ω-P2-E1 §2 acyclicity |
| disjoint pairs | `P1#P7` `P8#P7` `{P2,P3,P6}#P9` | Ω-P2-E1 §2 |
| derivable / not-derivable cells | 74 / 26 | Ω-P2-E1 §2 completeness |

## 5. Certified theorem inventory

Ω-P2-E1 issued **40 issued · 0 refuted · 0 lattice failures**. The 14 theorems load-bearing in Phase-4
are serialized here verbatim from the certified namespace; wording is preserved exactly.

| ID | Certified statement |
|---|---|
| `E1-C-1.1-P1` | mu1 extension EQUALS its representation; both set differences 0 |
| `E1-P1` | P1 Registration Population, |P1| = 1194; .py NOT-IN P1 is a THEOREM of the rule (.py not in INCLUDE_EXTENSIONS) |
| `E1-P5` | P5 Located Owner Population, |P5| = 58 |
| `E1-T-L1` | Registration does NOT imply Recognition; |P1 \ P3| = 1171 |
| `E1-T-L10` | Located ownership does NOT imply constitutional artifacthood; |P5 \ P3| = 15 |
| `E1-T-L5` | Operational realization does NOT imply Authority; |P7 \ P6| = 2856 |
| `E1-T-L7` | Authority IMPLIES Recognition; forced by X.1 |
| `E1-T-M2` | rho : P2 -> XII.2 standings TOTAL, image 4 of 6; DECLARATIVE and LATENT declared but unused |
| `E1-T-M3` | omega : concerns -> owner ids is PARTIAL 55/60, NON-INJECTIVE (image 43); partiality is exactly CMG-DLG-36..40 |
| `E1-T-M4` | iota : P6 -> P3 is BIJECTIVE and LAW-BACKED (X.1 forces P6 subset P3; XI.3 forces P3 subset P6); hence P6 = P3 |
| `E1-T-M5` | kappa : P3 -> P5 TOTAL INJECTIVE NON-SURJECTIVE by 15 |
| `E1-T-ND1` | |P9| NOT DERIVABLE - NOT REPRESENTED (primary) + NOT MEASURED. 0 latency checks among the 16 declared; XII.5 asserts detectability so the class is NOT constitutionally unknowable |
| `E1-T-ND3` | exact |P4| NOT DERIVABLE - NOT DECLARED (XII.6 supplies no decidable form) + NOT REPRESENTED |
| `E1-T-ND4` | correctness of P3 membership is CONSTITUTIONALLY UNKNOWABLE - VAC-01, CMG-OQ-01/02 open, LXXX.4 ceiling |

## 6. Replay theorem inventory

15 propositions, 6-value outcome vocabulary `FALSIFIED | GAP | PROVEN | REUSE | UNKNOWN | WITHDRAWN`.

| Outcome | Count | Replays |
|---|---|---|
| **FALSIFIED** | 7 | `R-D-01` `R-F-01` `R-D-03` `R-D-04` `R-D-07` `R-D-08` `R-B-14` |
| **GAP** | 0 | — |
| **PROVEN** | 5 | `R-D-02` `R-D-06` `R-T-01` `R-T-04` `R-T-05` |
| **REUSE** | 1 | `R-T-02` |
| **UNKNOWN** | 1 | `R-D-05` |
| **WITHDRAWN** | 1 | `R-T-03` |
| | **15** | |

### 6.1 Propositions, verbatim

**`R-D-01` → FALSIFIED**
**`R-D-02` → PROVEN**
**`R-F-01` → FALSIFIED**
**`R-D-03` → FALSIFIED**
**`R-D-04` → FALSIFIED**
**`R-D-05` → UNKNOWN**
**`R-D-06` → PROVEN**
**`R-D-07` → FALSIFIED**
**`R-D-08` → FALSIFIED**
**`R-B-14` → FALSIFIED**
**`R-T-01` → PROVEN**
**`R-T-02` → REUSE**
**`R-T-03` → WITHDRAWN**
**`R-T-04` → PROVEN**
**`R-T-05` → PROVEN**


## 7. Disposition transition matrix

For every Ω-P1 proposition: original disposition → replay outcome → reason →
load-bearing theorem(s) → Repository Truth evidence. Wording, disposition, theorem
identity, dependency and provenance are preserved exactly.

### R-D-01 — FALSIFIED

**Proposition** (verbatim) — OMEGA-P1-D-01: the 22 universal abstractions of umk-kernel.json are a closed enumeration, so the mechanism plane is not open.

| Element | Value |
|---|---|
| Original disposition | WITHDRAWN (disposition PASS) |
| ↓ provenance | Ω-P1 §5 Ω-P1-D-01 |
| Replay outcome | **FALSIFIED** |
| Reason | CONCLUSION Both the vehicle (P3) and the content (P4) of the proposition fail. FALSIFIED on two independent grounds. |
| Load-bearing theorem(s) | `LM-03` |
| Repository Truth evidence | `M-04`, `M-18` |
| Governing clauses | `CL-X.1`, `CL-XI.9`, `CL-XIII.2` |

Derivation, verbatim:

- P1 The proposition requires umk-kernel.json to close a constitutional enumeration.
- P2 To close a constitutional enumeration an artifact must exercise constitutional force. CL-X.1.
- P3 M-18 measures umk-kernel.json NOT-IN P3. By CL-X.1 it exercises no force and SHALL NOT be cited as constitutional authority. P2 fails.
- P4 Independently: LM-03 with M-04 shows the constitutional Kind set is not among the four closed enumerations, and CL-XIII.2 declares it OPEN.
- CONCLUSION Both the vehicle (P3) and the content (P4) of the proposition fail. FALSIFIED on two independent grounds.

Adversarial replay, verbatim:

> Counterexample sought: an unregistered manifest that nonetheless closes an enumeration. None can exist - CL-X.1 is unconditional and admits no exception for manifests. Attempt to invalidate M-04 by finding a fifth closed enumeration: the registry's closed_enumerations list is the located representation and carries exactly 4, each citing CMG-INV-09 as required by CL-XI.9. No counterexample.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-D-02 — PROVEN

**Proposition** (verbatim) — OMEGA-P1-D-02: XVIII.2 mandates six elements including revocation condition; it is absent from all 60 delegation records; therefore every delegation record is void, and the remedy is to append revocation_condition to the 60 records.

| Element | Value |
|---|---|
| Original disposition | EXTEND |
| ↓ provenance | Ω-P1 §5 Ω-P1-D-02; census B-03 |
| Replay outcome | **PROVEN** |
| Reason | CONCLUSION The proposition's assertion of voidness is PROVEN on the literal terms of the located clause. |
| Load-bearing theorem(s) | `E1-T-M3`, `LM-02`, `LM-10` |
| Repository Truth evidence | `M-01`, `M-02`, `M-05`, `M-06` |
| Governing clauses | `CL-XVIII.2`, `CL-XVIII.5`, `CL-XV.3`, `CL-X.7`, `CL-XI.3`, `CL-L.6`, `CL-XII.7` |

Derivation, verbatim:

- P1 CL-XVIII.2 requires a delegation record to carry EXACTLY six named elements and states the consequence of omission explicitly: the record IS void.
- P2 M-01 measures revocation_condition in 0 of 60; E1-T-M3 certifies the record set is 60 with the represented field union. The element is absent from every record.
- P3 The word 'exactly' in CL-XVIII.2 governs the ELEMENT LIST. An absent element is therefore a missing element, and the void consequence is triggered on its own terms.
- CONCLUSION The proposition's assertion of voidness is PROVEN on the literal terms of the located clause.
- SCOPE-1 The REMEDY is separately FALSIFIED: LM-02 with CL-XV.3 establishes that LXXXII.2 is the canonical representation and the JSON a projection, so appending the field to the projection makes it carry what its input does not declare, and CL-XV.3 directs that the input governs.
- SCOPE-2 The CASCADE is UNKNOWN and is expressly not asserted. If every delegation were void then by CL-X.7 no concern would be owned and CL-XI.3 would fail, yet M-06 records findings 0 and READY-PROVISIONAL. LM-10 resolves the conflict of clauses to a defect of the instrument under CL-L.6 and refers the reading to AUTH-INF-001 under CL-XII.7. Whether CL-XVIII.5's universal declaration satisfies 'carry' by incorporation is an act of interpretation this replay does not perform.

Adversarial replay, verbatim:

> Counterexample sought: a record carrying the element. M-01 measures 0 of 60; the field does not appear in the key union. Attempt to invalidate via CL-XVIII.5 - a universal revocation condition might satisfy 'carry' by incorporation. That is an interpretive move reserved to AUTH-INF-001 by CL-XII.7, so it cannot be used here to defeat the literal reading; it is recorded as SCOPE-2 and downgrades only the cascade, not the proposition. Attempt to invalidate M-05: the validator has no revocation check, so its silence corroborates rather than contradicts. Proposition survives.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-F-01 — FALSIFIED

**Proposition** (verbatim) — OMEGA-P1-F-01: XVIII.2 names the disposition set as (EXTEND or REUSE); 11 records carry RETAIN; RETAIN is therefore constitutionally intended by LXXXII.3 but NOT ADMITTED by XVIII.2's enumeration.

| Element | Value |
|---|---|
| Original disposition | RECORDED, referred |
| ↓ provenance | Ω-P1 §5 Ω-P1-F-01 |
| Replay outcome | **FALSIFIED** |
| Reason | CONCLUSION P1 fails. RETAIN IS admitted. FALSIFIED. |
| Load-bearing theorem(s) | `LM-03` |
| Repository Truth evidence | `M-03`, `M-04` |
| Governing clauses | `CL-XI.9`, `CL-XVIII.2`, `CL-LXXXII.3`, `CL-LXXVI.3` |

Derivation, verbatim:

- P1 CL-XVIII.2 names the disposition element with a parenthetical value list '(EXTEND or REUSE)'. The proposition requires that parenthetical to have exclusionary force over values outside it.
- P2 CL-XI.9 states that NO enumeration in the instrument is closed except by an invariant naming the closure, and requires every CLOSED enumeration to cite its closing invariant.
- P3 M-04 measures the closed enumerations as exactly four. The XVIII.2 disposition value set is not among them. LM-03.
- P4 Therefore the parenthetical is an OPEN enumeration and its members are not exhaustive. It has no exclusionary force.
- P5 CL-LXXXII.3 positively establishes the RETAIN residue, and CL-LXXVI.3 makes admission append-only and non-invalidating of existing members, so RETAIN is admitted by append without amendment of XVIII.2.
- CONCLUSION P1 fails. RETAIN IS admitted. FALSIFIED.
- NOTE This diverges from R-D-02 on the same clause, and the divergence is exactly why the two must not be merged: 'exactly' governs the ELEMENT list, which is therefore closed by the clause's own words, while the VALUE list is left open by CL-XI.9.

Adversarial replay, verbatim:

> Counterexample sought: an invariant naming the closure of the XVIII.2 disposition set. M-04 enumerates all four closures; unknown_concept_dispositions closes LXXVII.3's five outcomes, a different set over a different subject. Attempt to read 'SHALL carry exactly' as closing the value list too: the adverb attaches to the enumeration of elements that follows it, and the value list appears parenthetically inside one element, so extending 'exactly' to it would require an interpretive step reserved to AUTH-INF-001 - and would additionally contradict CL-XI.9, which is an invariant and therefore superior ground. No counterexample.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-D-03 — FALSIFIED

**Proposition** (verbatim) — OMEGA-P1-D-03: three implementations each self-describe as the single admission authority; this is the one measured CMG-L-14 FAIL and a CMG-L-02 duplicate authority.

| Element | Value |
|---|---|
| Original disposition | EXTEND |
| ↓ provenance | Ω-P1 §5 Ω-P1-D-03; census E-06 |
| Replay outcome | **FALSIFIED** |
| Reason | CONCLUSION Both limbs fail. No located clause is violated. FALSIFIED. |
| Load-bearing theorem(s) | `E1-T-L5`, `LM-01`, `LM-04`, `LM-09` |
| Repository Truth evidence | `M-07` |
| Governing clauses | `CL-IV.2`, `CL-X.1`, `CL-X.2`, `CL-X.14`, `CL-XX.2`, `CL-XX.8` |

Derivation, verbatim:

- P1 The CMG-L-14 limb requires CL-X.14 to reach the three files.
- P2 LM-09 establishes CL-X.14's grammatical subject is 'This instrument'. The three files are not CMG-000001. P1 fails.
- P3 The CMG-L-02 limb requires the three to be CONSTITUTIONAL ARTIFACTS holding authority over one concern. CL-IV.2 supplies the test: a Constitution, or normatively derived from one AND CARRYING BINDING FORCE by that derivation.
- P4 LM-01 places every .py outside P1 and P3. E1-T-L5 certifies |P7 \ P6| = 2856 with engine/kernel/registry.py as its witness. LM-04 confines force and ownership to P3.
- P5 By CL-XX.2 an Owner must be a constitutional artifact and by CL-XX.8 a derived-truth artifact owns no concern. None of the three qualifies. P3 fails.
- CONCLUSION Both limbs fail. No located clause is violated. FALSIFIED.
- PRESERVED M-07 remains a true measurement - three registries, zero import edges. It is an engineering fact about P7 and not a constitutional violation. No clause is cited for it, and none is available.

Adversarial replay, verbatim:

> Counterexample sought: a clause making a plurality of implementation registries unlawful. CL-X.14 is subject-bound (LM-09); CL-X.2 is artifact-bound (P4-P5). DELIBERATE EXCLUSION: recorded decisions in 00-MASTER/UCDA-000001/ucda-decisions.json were NOT used to defeat this proposition. M-18 places that file outside P1 and P3, so citing it as authority would violate CL-X.1 - the very clause this replay relies on against the proposition. Using it would be an asymmetric application of CL-X.1 and is refused. The falsification stands on subject and sort alone.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-D-04 — FALSIFIED

**Proposition** (verbatim) — OMEGA-P1-D-04 (PRIMARY): CEP-009 B.6.1 obliges sixteen participation properties; no check asserts programme-home coverage, four engines are gated by nothing and eighteen sit outside the aggregate determination; therefore a constitutional obligation over the population is unmeasured.

| Element | Value |
|---|---|
| Original disposition | EXTEND (PRIMARY) |
| ↓ provenance | Ω-P1 §5 Ω-P1-D-04; census F-04, D-10 |
| Replay outcome | **FALSIFIED** |
| Reason | CONCLUSION The obligation attributed to CL-B.6.1 is not the obligation it states, and the population attributed to it is not its subject. FALSIFIED as stated. |
| Load-bearing theorem(s) | `E1-T-L5`, `LM-01`, `LM-05`, `LM-06` |
| Repository Truth evidence | `M-08`, `M-09` |
| Governing clauses | `CL-B.6.1`, `CL-B.6.2`, `CL-B.3.2`, `CL-B.4.1`, `CL-B.11.3` |

Derivation, verbatim:

- P1 M-09 measures the facts the proposition asserts: 35 engines across 31 programme homes, 18 present in the check register and 17 absent, and ZERO checks asserting programme-home coverage. Those measurements are accepted in full. What the proposition adds to them is the claim that CL-B.6.1's obligation is per-object coverage over a population that includes *_engine.py.
- P2 LM-05 derives the obligation's actual shape from the clause's own words: each property IS DISCHARGED BY A LOCATED MECHANISM, and CL-B.6.2 makes non-LOCATION the failure mode. M-08 measures the located owner discharging all sixteen by mechanism location. The obligation CL-B.6.1 states is met.
- P3 LM-06 shows the subject is a NEWLY INTRODUCED CONSTRUCT, while CL-B.4.1 places implementation at stage 12 of a construct's traversal. An engine is an output of a traversal, not a construct entering one.
- P4 Independently, LM-01 and E1-T-L5 place every engine outside P1, P3 and P6, and CL-B.11.3 declares the executable measurement void as constitutional authority.
- CONCLUSION The obligation attributed to CL-B.6.1 is not the obligation it states, and the population attributed to it is not its subject. FALSIFIED as stated.
- RESIDUE, ALREADY CERTIFIED, NOT A NEW FINDING The proposition's underlying concern - that some constitutional population's participation is unmeasured - is TRUE of P9 and is already carried by certificate E1-T-ND1, which proves the latency detector absent while CL-XII.5 requires latency to be recorded as a finding. That is a different population from the one D-04 names, and R-T-05 below is where it discharges.

Adversarial replay, verbatim:

> Counterexample sought: a located clause quantifying a participation obligation over implementation files. CL-B.6.1's subject is a construct; CL-B.3.2's construct classes name capabilities, components and registries but CL-B.4.1 separates registration (stage 6) from implementation (stage 12), so 'component' cannot be read as the implementation output without collapsing two declared stages. Attempt to invalidate M-08 by challenging UCEF-000001's standing: M-18-class reasoning would place it outside P3, but M-08 is used here as a MEASUREMENT of what the located owner does, not as an authority - CL-B.6.1 itself supplies the obligation. Sort is preserved. No counterexample.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-D-05 — UNKNOWN

**Proposition** (verbatim) — OMEGA-P1-D-05: UCL-V-24 measures stage_obligation_failures = 4; the Gap Discovery stage's owner lies in a zone constitutional checks cover, yet no declared gate validates, verifies or certifies it; therefore four applicable obligations are unbound.

| Element | Value |
|---|---|
| Original disposition | EXTEND (disclosed, ratcheted) |
| ↓ provenance | Ω-P1 §5 Ω-P1-D-05; census D-09 |
| Replay outcome | **UNKNOWN** |
| Reason | CONCLUSION UNKNOWN. Not FALSIFIED - the deficiency may well obtain, and calling it false would itself require the unstable measure. Not PROVEN - the premise does not reproduce from Repository Truth at a fixed baseline. |
| Load-bearing theorem(s) | `LM-07` |
| Repository Truth evidence | `M-10`, `M-16`, `M-18`, `M-20` |
| Governing clauses | `CL-X.10`, `CL-XI.10`, `CL-XV.5`, `CL-CONST08.5`, `CL-CLO-01`, `CL-X.1` |

Derivation, verbatim:

- P1 The proposition's load-bearing premise is the measured value 4.
- P2 M-16 places CONST-08 in P3, so CL-CONST08.5 is citable as authority: determinations must reproduce identically AT A FIXED BASELINE COMMIT. CL-X.10, CL-XI.10 and CL-XV.5 independently require recomputability from repository state alone.
- P3 M-10 measures the same declared measure as 9 at a clean checkout of 43dec4a, with 5 of the 9 traceable to three GITIGNORED inputs. The measure is therefore not a function of the committed repository state.
- P4 LM-07 makes such a measure incapable of grounding a constitutional assertion. P1 is unstable, so neither the proposition nor its negation is derivable.
- CONCLUSION UNKNOWN. Not FALSIFIED - the deficiency may well obtain, and calling it false would itself require the unstable measure. Not PROVEN - the premise does not reproduce from Repository Truth at a fixed baseline.
- SECOND GROUND, RECORDED, NOT DECISIVE The obligation rules OBL-VALIDATION, OBL-VERIFICATION and OBL-CERTIFICATION are declarations of ucl-declaration.json, which M-18 places outside P1 and P3, so by CL-X.1 they are not located constitutional law; and M-20 places the stage owner in P1 but outside P3, so it too carries no constitutional force. This ground would point to FALSIFIED on the constitutional limb, but the outcome rule requires exactly one verdict and the unstable premise dominates: a proposition whose measurement is not reproducible cannot be adjudicated either way.

Adversarial replay, verbatim:

> Counterexample sought: a repository state at which the measure is reproducibly 4. M-10 shows the clean committed baseline yields 9, so 4 is attainable only with untracked inputs present - which CL-CLO-01 and CL-CONST08.5 exclude as a certification basis. Attempt to rescue by declaring the gitignored files part of repository state: CL-CLO-01 states the fixed point is a property of a COMMITTED state, and the located recognition rule classes an uncommitted file as a CANDIDATE, never registered. The rescue fails and UNKNOWN stands.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-D-06 — PROVEN

**Proposition** (verbatim) — OMEGA-P1-D-06: 02-CANONICAL-OWNERSHIP-MATRIX.md cites 431 concepts while the machine-generated register measures 447; the document is narrative and drifting.

| Element | Value |
|---|---|
| Original disposition | EXTEND |
| ↓ provenance | Ω-P1 §5 Ω-P1-D-06; census B-15 |
| Replay outcome | **PROVEN** |
| Reason | CONCLUSION The proposition asserts a disagreement between two located ownership records. The disagreement is measured and the governing clause classifies it. PROVEN. |
| Load-bearing theorem(s) | `E1-T-L1` |
| Repository Truth evidence | `M-11`, `M-20` |
| Governing clauses | `CL-XX.7`, `CL-VIII.1` |

Derivation, verbatim:

- P1 CL-XX.7 names BOTH the canonical ownership matrix AND the concept-ownership register as located ownership FACTS of the corpus.
- P2 M-11 measures the matrix at 431 against the register's 447, at two different baselines. The two located records disagree.
- P3 CL-XX.7 states the consequence directly: where those records disagree with each other, the disagreement IS A FINDING under Article LII, to be disposed by the owner of the affected concern and never by CMG-000001.
- CONCLUSION The proposition asserts a disagreement between two located ownership records. The disagreement is measured and the governing clause classifies it. PROVEN.
- REMEDY ADMISSIBILITY CL-XX.7 also settles a question the proposition raises implicitly. E1-T-L1 and M-20 place the matrix in P1 and outside P3, and the register outside both; an objection that deriving the former from the latter inverts authority under CL-X.1 does NOT hold, because CL-XX.7 admits the register as a FACT source rather than an authority. Sort is preserved: facts ground measurements, authorities ground obligations.
- DISPOSITION OWNER Not determined here. CL-XX.7 assigns it to the owner of the affected concern, and this replay holds no such authority.

Adversarial replay, verbatim:

> Counterexample sought: a reading under which 431 and 447 do not disagree. They are counts of the same population at two baselines, ab78f35 and 43dec4a, and CL-VIII.1 requires a constitutional truth to be stated in exactly one place, so two divergent statements of one count cannot both stand. Attempt to invalidate by arguing the matrix is out of scope: M-20 places it IN P1 and CL-XX.7 names it explicitly. No counterexample.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-D-07 — FALSIFIED

**Proposition** (verbatim) — OMEGA-P1-D-07: RegistryKind and KnowledgeKind are closed enumerations and therefore do not conform to XIII.2's open Kind set.

| Element | Value |
|---|---|
| Original disposition | EXTEND |
| ↓ provenance | Ω-P1 §5 Ω-P1-D-07 |
| Replay outcome | **FALSIFIED** |
| Reason | CONCLUSION CL-XIII.2 does not govern them. FALSIFIED. |
| Load-bearing theorem(s) | `LM-01` |
| Repository Truth evidence | `M-12` |
| Governing clauses | `CL-XIII.1`, `CL-XIII.2`, `CL-XIII.3`, `CL-X.9` |

Derivation, verbatim:

- P1 The proposition requires CL-XIII.2 to govern the two Python enumerations.
- P2 CL-XIII.1 fixes the domain: the recognized Kinds of CONSTITUTIONAL OBJECT, enumerated CMG-K-01..24. M-12 measures RegistryKind's and KnowledgeKind's members as a disjoint enumeration over a different subject.
- P3 CL-X.9 forbids a constitutional artifact from naming a PROGRAMMING LANGUAGE as a condition of its law, so CL-XIII.2 cannot be reaching into a Python enum without voiding itself.
- P4 CL-XIII.3 forbids Kind being defined by location, filename, program or technology, confirming the constitutional Kind set is not a code-level vocabulary.
- P5 LM-01 independently places both files outside P1 and P3.
- CONCLUSION CL-XIII.2 does not govern them. FALSIFIED.
- PRESERVED M-12's observation that admitting a member required editing the enum remains a true measurement about P7. No located clause makes it a violation.

Adversarial replay, verbatim:

> Counterexample sought: a clause extending the constitutional Kind set to implementation vocabularies. CL-XIII.3 excludes it explicitly and CL-X.9 makes the converse reading self-voiding. Attempt to rescue via CL-XIII.2's 'at minimum' in CL-XIII.1 - openness means the constitutional set may GROW, not that unrelated sets are members of it. No counterexample.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-D-08 — FALSIFIED

**Proposition** (verbatim) — OMEGA-P1-D-08: engine/identity/ contains only stale bytecode yet imports successfully, so a latent identity authority exists that is unowned and unmeasured; disposition RECORD AS GAP under LXXVII.2(d).

| Element | Value |
|---|---|
| Original disposition | RECORD AS GAP (LXXVII.2(d)) |
| ↓ provenance | Ω-P1 §5 Ω-P1-D-08; census E-10 |
| Replay outcome | **FALSIFIED** |
| Reason | CONCLUSION Neither limb of CL-LXXVII.2d is satisfied. FALSIFIED. |
| Load-bearing theorem(s) | `E1-T-L5`, `LM-01`, `LM-04`, `LM-08` |
| Repository Truth evidence | `M-13`, `M-19` |
| Governing clauses | `CL-IV.13`, `CL-LXXVII.2d`, `CL-LXXXII.6`, `CL-X.1`, `CL-XX.8` |

Derivation, verbatim:

- P1 CL-LXXVII.2d requires the subject to be a CONCERN that is both SUBSTANTIVE and UNOWNED, and LM-08 with CL-IV.13 establishes that a gap is a QUESTION, never an artifact or a directory.
- P2 M-19 measures the identity concern as delegated at CMG-DLG-13 to REG-AUTO-001. It is present in LXXXII.2, so by CL-LXXXII.6 it is not a gap. The 'unowned' condition fails.
- P3 The word 'authority' in the proposition is not the located sense. M-13 measures 0 tracked files, so LM-01 and LM-04 place the directory outside P1, P3 and P6; CL-X.1 denies it force and CL-XX.8 denies it ownership. E1-T-L5 certifies the general case.
- CONCLUSION Neither limb of CL-LXXVII.2d is satisfied. FALSIFIED.
- PRESERVED M-13 remains true: 20 stale modules importable with __file__ = None. That is an implementation-hygiene fact about P7, for which no clause is available and none is cited.

Adversarial replay, verbatim:

> Counterexample sought: a construal on which the directory is a constitutional gap. CL-IV.13 defines a gap as a question within jurisdiction, so no artifact can be one. Attempt to relocate the gap to the concern 'identity resolution' as distinct from 'identity allocation': that would require showing the narrower concern absent from both LXXXII.2 and LXXXII.3, which this replay cannot establish from the certified set and which would constitute a NEW FINDING - prohibited in this phase. Recorded as not attempted rather than silently resolved. The proposition as stated remains falsified.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-B-14 — FALSIFIED

**Proposition** (verbatim) — OMEGA-P1-B-14: UKI-LAW-005 requires semantic ownership overlap detection to fail closed; find_overlaps does not; therefore a constitutional obligation is unmet.

| Element | Value |
|---|---|
| Original disposition | EXTEND |
| ↓ provenance | Ω-P1 §4.B B-14 |
| Replay outcome | **FALSIFIED** |
| Reason | CONCLUSION The cited authority is not located constitutional law, so no constitutional obligation exists to be unmet. FALSIFIED. |
| Load-bearing theorem(s) | `LM-01` |
| Repository Truth evidence | `M-14` |
| Governing clauses | `CL-X.1` |

Derivation, verbatim:

- P1 The proposition's authority is UKI-LAW-005.
- P2 M-14 measures its only carriers as 6 tracked files, every one a .py.
- P3 LM-01 places every .py outside P1 and P3, and CL-X.1 states that an unrecognized artifact SHALL NOT be cited as constitutional authority.
- CONCLUSION The cited authority is not located constitutional law, so no constitutional obligation exists to be unmet. FALSIFIED.
- SORT NOTE This is CL-X.1 applied to the AUTHORITY a proposition invokes, which is exactly the clause's target. It is not the inverse move of using an unrecognized artifact to DEFEAT a proposition, which R-D-03 expressly refuses.

Adversarial replay, verbatim:

> Counterexample sought: a recognized artifact carrying UKI-LAW-005. M-14 enumerates all six carriers and none is in P1 or P3. Attempt to rescue by treating the docstring as evidence of an unwritten law: CL-X.1 admits no unwritten constitutional authority. No counterexample.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-T-01 — PROVEN

**Proposition** (verbatim) — OMEGA-P1 headline: for every mechanism dispositioned a canonical owner was located, therefore no constitutional CREATE is required and CREATE = 0.

| Element | Value |
|---|---|
| Original disposition | 0 CREATE asserted |
| ↓ provenance | Ω-P1 §4.F, §7 |
| Replay outcome | **PROVEN** |
| Reason | CONCLUSION PROVEN, with scope stated: the claim holds over the LOCATED concern set of 60. Omega-P1's '84 mechanisms' is its own construction and is not a certified population in Omega-P2-E1, so the claim over that framing is not derivable and is not asserted here. |
| Load-bearing theorem(s) | `E1-T-M3`, `E1-T-M4`, `E1-T-L10`, `E1-P5` |
| Repository Truth evidence | `M-06` |
| Governing clauses | `CL-XI.3`, `CL-LXXVI.2c`, `CL-XX.2` |

Derivation, verbatim:

- P1 CL-XI.3 requires both projections of the concern-owner relation to be total.
- P2 E1-T-M4 certifies iota : P6 -> P3 BIJECTIVE and LAW-BACKED, so every located authority owns a concern and every recognized artifact is an owner.
- P3 E1-T-M3 certifies omega total on 55 of 60 with the 5-record partiality being exactly CMG-DLG-36..40, whose owner_paths all resolve; E1-P5 certifies |P5| = 58.
- P4 M-06 records the located validator reporting 60 concerns and findings 0.
- P5 By CL-LXXVI.2c CREATE requires a recorded discovery that no owner exists. No concern in the located set lacks an owner.
- CONCLUSION PROVEN, with scope stated: the claim holds over the LOCATED concern set of 60. Omega-P1's '84 mechanisms' is its own construction and is not a certified population in Omega-P2-E1, so the claim over that framing is not derivable and is not asserted here.

Adversarial replay, verbatim:

> Counterexample sought: a concern in the located set without an owner. E1-T-M4's surjectivity and CL-XI.3 exclude it, and M-06 corroborates at 0 findings. Attempt to invalidate via E1-T-L10 - 15 members of P5 are not constitutional artifacts, so CL-XX.2 is strained. That bears on the QUALITY of five owners, not on the EXISTENCE of an owner for each concern, so it does not reach CREATE. Recorded, not decisive.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-T-02 — REUSE

**Proposition** (verbatim) — OMEGA-P1 headline: the Universal Constitutional Admission Contract already exists normatively, so producing a second one is refused and the disposition is REUSE of CEP-009 ADDENDUM B.

| Element | Value |
|---|---|
| Original disposition | REUSE |
| ↓ provenance | Ω-P1 §4.D D-01, §7 |
| Replay outcome | **REUSE** |
| Reason | CONCLUSION REUSE. The outcome is the located disposition itself, not a judgement about it. |
| Load-bearing theorem(s) | — clause-only derivation |
| Repository Truth evidence | `M-15` |
| Governing clauses | `CL-LXXVII.2a`, `CL-B.11.1`, `CL-X.1`, `CL-IX.4` |

Derivation, verbatim:

- P1 M-15 places CEP-009 in P3, so by CL-X.1 it may be cited as constitutional authority. This is the sort condition the proposition needs and it is satisfied.
- P2 CL-B.11.1 states categorically that there is NO SECOND admission procedure and that B.4 binds rather than authors.
- P3 CL-IX.4 requires an existing owner to be bound by reference and never re-legislated.
- P4 CL-LXXVII.2a assigns the disposition where the concept is already owned: REUSE.
- CONCLUSION REUSE. The outcome is the located disposition itself, not a judgement about it.

Adversarial replay, verbatim:

> Counterexample sought: a second located admission contract that would make the concern contested. CL-B.11.1 forecloses it by declaration. Attempt to invalidate M-15: CEP-009 is a P2 record with FOUNDATIONAL standing, inside the 43. No counterexample.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-T-03 — WITHDRAWN

**Proposition** (verbatim) — OMEGA-P1 headline: the deterministic fixed point IS CERTIFIED, measured at HEAD 43dec4a with a clean working tree.

| Element | Value |
|---|---|
| Original disposition | FIXED POINT CERTIFIED |
| ↓ provenance | Ω-P1 §6, header FIXED POINT |
| Replay outcome | **WITHDRAWN** |
| Reason | CONCLUSION The proposition was valid for the program state that produced it and is not valid for this one. By CL-LXXIX.5 that is not falsification of a past measurement but expiry of its validity. WITHDRAWN as a present assertion. |
| Load-bearing theorem(s) | — clause-only derivation |
| Repository Truth evidence | `M-16`, `M-17` |
| Governing clauses | `CL-LXXIX.5`, `CL-CLO-01`, `CL-CONST08.5` |

Derivation, verbatim:

- P1 CL-LXXIX.5 states that a completeness result IS VALID ONLY FOR THE REPOSITORY STATE THAT PRODUCED IT and SHALL record that state.
- P2 M-16 places CONST-08 in P3, so CL-CONST08.5 is citable: determinations must reproduce at a fixed baseline commit. CL-CLO-01 requires a clean committed tree.
- P3 M-17 measures the present program state as 879b1abd... with 70 modified tracked files and 3 untracked candidates. CLO-01's precondition is unmet here.
- CONCLUSION The proposition was valid for the program state that produced it and is not valid for this one. By CL-LXXIX.5 that is not falsification of a past measurement but expiry of its validity. WITHDRAWN as a present assertion.
- NOT FALSIFIED is deliberate: nothing measured here contradicts the earlier run. What changed is the state, and CL-LXXIX.5 makes state-relativity constitutional rather than incidental.

Adversarial replay, verbatim:

> Counterexample sought: a reading under which a certification survives a change of state. CL-LXXIX.5 excludes it in terms. Attempt to argue the 3 untracked candidates are outside the fixed point and therefore harmless: CLO-05 counts untracked entries outside excluded locations, and CLO-01 requires the tree clean BEFORE assertion, so their presence is dispositive regardless of their content. WITHDRAWN stands.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-T-04 — PROVEN

**Proposition** (verbatim) — OMEGA-P1 headline: Article LXXXII is the universal ownership pattern, and a central mechanism registry is not missing but constitutionally PROHIBITED.

| Element | Value |
|---|---|
| Original disposition | REUSE / PASS (was EXTEND, withdrawn) |
| ↓ provenance | Ω-P1 §2, §4.E H-07 |
| Replay outcome | **PROVEN** |
| Reason | CONCLUSION PROVEN, with scope stated by LM-09: the prohibition binds CMG-000001. Omega-P1's unrestricted reading - that such a registry is prohibited to ANY party - is not supported by CL-X.14's grammatical subject and is not asserted here. |
| Load-bearing theorem(s) | `E1-T-M3`, `E1-T-M4`, `E1-T-M5`, `LM-09` |
| Repository Truth evidence | — none required |
| Governing clauses | `CL-LXXXII.1`, `CL-X.14`, `CL-IX.4` |

Derivation, verbatim:

- P1 CL-LXXXII.1 declares Art LXXXII the mechanism by which Zero Parallel Authority is achieved and every listed concern ALREADY OWNED and bound by reference.
- P2 E1-T-M3, E1-T-M4 and E1-T-M5 certify the pattern's structure: a total-on-55 concern-to-owner map, a law-backed bijection between authority and recognition, and an injective non-surjective embedding of recognition into located ownership.
- P3 CL-IX.4 forbids re-legislating an existing owner; a central mechanism registry authored by CMG-000001 would do exactly that.
- P4 CL-X.14 prohibits this instrument from creating a second registry where one exists.
- CONCLUSION PROVEN, with scope stated by LM-09: the prohibition binds CMG-000001. Omega-P1's unrestricted reading - that such a registry is prohibited to ANY party - is not supported by CL-X.14's grammatical subject and is not asserted here.

Adversarial replay, verbatim:

> Counterexample sought: a clause prohibiting a central mechanism registry generally. CL-X.14 is subject-bound and CL-LXXXII.1 speaks to what THIS instrument achieves. The scoped form survives; the unrestricted form is withdrawn from the claim rather than defended. Note this is the same subject-boundedness that falsifies R-D-03, applied consistently in both directions.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

### R-T-05 — PROVEN

**Proposition** (verbatim) — OMEGA-P1 exit answer: Repository Truth does NOT yet prove that a future constitutional change cannot become constitutionally incomplete at admission.

| Element | Value |
|---|---|
| Original disposition | answered: does NOT yet prove |
| ↓ provenance | Ω-P1 §7 exit criterion |
| Replay outcome | **PROVEN** |
| Reason | CONCLUSION An artifact can function as law without recognition, and no located mechanism detects it. Completeness at admission is therefore not proven, and by CL-B.6.3 no verdict of completeness may be asserted. PROVEN. |
| Load-bearing theorem(s) | `E1-T-ND1`, `E1-T-ND3`, `E1-T-ND4`, `E1-T-M2` |
| Repository Truth evidence | `M-05` |
| Governing clauses | `CL-LXXIX.4`, `CL-XII.5`, `CL-IV.1`, `CL-B.6.2`, `CL-B.6.3` |

Derivation, verbatim:

- P1 CL-LXXIX.4 requires completeness verification to be MECHANICAL and realized by the Art L validator, and states that a claim not produced by the validator IS AN ASSERTION, NOT A VERIFICATION.
- P2 CL-IV.1 and CL-XII.5 define an artifact that satisfies (a)-(e) without (f) as a Latent Constitution, require it to be RECORDED AS A FINDING under Article LII, and declare latency a DETECTABLE defect.
- P3 E1-T-ND1 certifies that no located detector exists: 0 latency checks among the 16 the validator declares, corroborated by M-05. So the mechanism CL-LXXIX.4 designates cannot produce the verification CL-XII.5 requires.
- P4 CL-B.6.2 states that absence of evidence IS NOT evidence of satisfaction, and CL-B.6.3 that where measurement cannot be performed NO VERDICT SHALL BE ASSERTED.
- P5 E1-T-ND3 and E1-T-M2 add that two of the six declared standings, DECLARATIVE and LATENT, are declared but unused and carry no decidable membership test; E1-T-ND4 adds that the correctness of recognition is constitutionally unknowable at this epoch.
- CONCLUSION An artifact can function as law without recognition, and no located mechanism detects it. Completeness at admission is therefore not proven, and by CL-B.6.3 no verdict of completeness may be asserted. PROVEN.
- ABSORPTION This is where R-D-04's residue discharges. D-04 as stated is falsified because it named the wrong population; the concern it was reaching for is carried here over P9, on certified ground, with no new finding raised.

Adversarial replay, verbatim:

> Counterexample sought: a located mechanism that detects latency or otherwise closes completeness at admission. E1-T-ND1 enumerates the validator's 16 checks and finds none. Attempt to rescue via CMG-GAP-07, which records the latency rule CLOSED: it closes the RULE and expressly leaves the enumeration of actual latent artifacts as 'a detection outcome, not a gap', which is precisely the detection that E1-T-ND1 proves absent. The rescue confirms the proposition instead of defeating it. No counterexample.

EPOCH SCOPE — certifies Evolution Epoch Ω-P2-E1 only. Prohibits no future evolution,
registration, recognition, authority, population, ontology, capability, proof or
certified epoch.

## 8. Dependency DAG summary

Recomputed from the certified literals of Source A. Recomputation reproduces the
certified graph; it derives nothing.

| Measure | Value |
|---|---|
| nodes | **106** (CL 47 / E1 14 / M 20 / LM 10 / R 15) |
| edges | **148** |
| longest path | **3** nodes (R → LM → {CL, E1, M}) |
| acyclic proof | three-colour DFS over all 106 nodes; back-edges **0**; all nodes closed |
| minimal proof | duplicate dependencies **0**; dependencies not load-bearing in their own derivation **0** |
| completeness proof | declared nodes unreachable from a replay **0** |

Rank order along every edge is strictly increasing: `CL < E1 < M < LM < R`.

**Recomputation note, disclosed rather than reconciled silently.** Phase-4's DAG summary
displayed `longest path 4 layers (R -> LM -> {CL,E1,M})`. That figure was a display
label naming the rank strata, not a computed depth. Recomputing the longest path over the
certified literals yields **3 nodes** along the same route. The two describe the
same graph. No certified theorem is affected: `longest path` is not a theorem of Ω-P2-E1
or of Phase-4, and the three certified DAG properties — acyclic, complete, minimal —
reproduce exactly.

## 9. Consistency certification

| Property | Result | Evidence |
|---|---|---|
| contradictions | **0** | replay identifiers unique across 15 propositions |
| cycles | **0** | DFS back-edges |
| dependency inversion | **0** | rank strictly increasing along all 148 edges |
| duplicated authority | **0** | each clause cited in its own governing role only; `CL-X.14` cited subject-bound in both `R-D-03` and `R-T-04`, consistently |
| uncertified premises | **0** | unresolved dependencies 0; replay-to-replay edges 0 — no Ω-P1 conclusion reused as evidence |
| UNKNOWN dependencies | **0** | propositions depending on an UNKNOWN without explicit downgrade |
| outcome vocabulary | **0** outside the 6-value set | |

## 10. Remaining constitutional questions

Only those already certified UNKNOWN or certified NOT DERIVABLE. No question is added.

| ID | Question | Certified class | Provenance |
|---|---|---|---|
| `R-D-05` | OMEGA-P1-D-05: UCL-V-24 measures stage_obligation_failures = 4; the Gap Discovery stage's owner lies in a zone constitutional checks cover, yet no declared gate validates, verifies or certifies it; therefore four applicable obligations are unbound. | UNKNOWN | Phase-4 replay |
| `R-D-02` SCOPE-2 | whether `CL-XVIII.5`'s universal declaration satisfies `CL-XVIII.2`'s "carry" by incorporation — the cascade is expressly not asserted | UNKNOWN, referred to AUTH-INF-001 under `CL-XII.7` | Phase-4 `R-D-02` SCOPE-2 |
| `E1-T-ND1` | |P9| NOT DERIVABLE - NOT REPRESENTED (primary) + NOT MEASURED. 0 latency checks among the 16 declared; XII.5 asserts detectability so the class is NOT constitutionally unknowable | NOT REPRESENTED + NOT MEASURED | Ω-P2-E1 §3 |
| `E1-T-ND3` | exact |P4| NOT DERIVABLE - NOT DECLARED (XII.6 supplies no decidable form) + NOT REPRESENTED | NOT DECLARED + NOT REPRESENTED | Ω-P2-E1 §3 |
| `E1-T-ND4` | correctness of P3 membership is CONSTITUTIONALLY UNKNOWABLE - VAC-01, CMG-OQ-01/02 open, LXXX.4 ceiling | CONSTITUTIONALLY UNKNOWABLE | Ω-P2-E1 §3 |

`T-ND2` and `T-ND5` are certified NOT DERIVABLE and EMPTY respectively; they raise no
question and are recorded in §13.

## 11. Residual GAP section

Constitutionally admitted GAPs in the certified replay set: **0**.

The `GAP` outcome class is empty. `R-D-08`, the only Ω-P1 proposition disposed
`RECORD AS GAP`, replayed **FALSIFIED**; its certified reason is serialized at §7.
No gap is manufactured here.

Gaps recorded by the located instrument itself are outside this serialization's scope and
are neither restated nor amended.

## 12. Proof obligations discharged

| Obligation | Discharge | Provenance |
|---|---|---|
| every population attribute proven | **40 issued · 0 refuted · 0 lattice failures** | Ω-P2-E1 §1 |
| lattice certified with justification | 6 properties PASS, 1 certified VACUOUS | Ω-P2-E1 §2 |
| every NOT DERIVABLE promoted to a theorem | 5 theorems across 5 distinct classes | Ω-P2-E1 §3 |
| every mapping certified | 9 mapping theorems | Ω-P2-E1 §4 |
| every layer relation certified | 10 layer theorems | Ω-P2-E1 §5 |
| every Ω-P1 proposition independently replayed | 15 | Phase-4 §6 |
| every replay adversarially challenged | 15 of 15 | Phase-4, per proposition |
| dependency DAG certified | acyclic, complete, minimal | §8 |
| consistency verified | 7 properties | §9 |
| byte determinism | serializer run twice, identical digest | §15 |

## 13. Proof obligations intentionally unresolved

| Obligation | Why unresolved | Provenance |
|---|---|---|
| exact `|P4|` | `CL-XII.6` supplies no decidable membership test | `E1-T-ND3` |
| `|P9|` | no located representation and no located detector | `E1-T-ND1` |
| P10 subject projection | `CEP-010 XIX.1` mandates the element; it is present in 1 of 53 records | `E1-T-ND2` |
| correctness of P3 membership | the competent ratifying authority does not exist at this epoch | `E1-T-ND4` |
| `R-D-05` truth-value | the premise is not a function of the committed repository state | Phase-4 `R-D-05` |
| `R-D-02` cascade | interpretation is reserved to AUTH-INF-001 under `CL-XII.7` | Phase-4 `R-D-02` SCOPE-2 |
| the five clause-level tensions | held under `LXXVII.5`; raising them would be a new finding | Ω-P2-E1 §8.4 |
| `R-D-08` narrower-concern relocation | would constitute a new finding; recorded as not attempted | Phase-4 `R-D-08` adversarial |

`IMPLEMENTATION LIMITATION` is certified an **empty** class at this epoch; its sole
candidate was eliminated by method correction rather than recorded. Provenance: `T-ND5`,
Ω-P2-E1 §3.

## 14. Evolution lineage

```
Ω-P1   determination, measurement only, 0 CREATE
  |     PROVISIONAL CANDIDATE, untracked
  v
Ω-P2   reconciliation
  |     superseded by the certified phases below
  v
Ω-P2-FINAL-1   candidate population model
  |     withdrawn; freeze vocabulary prohibited by the Universal Evolution Principle
  |     content carried forward without loss
  v
Ω-P2-E1   CERTIFIED EVOLUTION EPOCH
  |     40 certificates, 0 refuted, 0 lattice failures
  v
Phase-4 Replay   CERTIFIED REPLAY THEOREM SET
  |     15 propositions, 0 verification failures
  v
Ω-P2-R   this serialization
```

Provenance: Ω-P2-E1 §9 records the Ω-P2-FINAL-1 supersession and its two grounds.

## 15. Constitutional disclosures

Serialized verbatim from Ω-P2-E1 §8. Two are marked superseded by the certified phases
that followed the epoch; the wording is preserved and not edited.

- 8.1 **Freezes nothing.** No architecture, constitutional universe, knowledge, ontology,
- 8.2 **Replays no Ω-P1 disposition.** Not begun.  — **SUPERSEDED**: Phase-4 replayed all 15 propositions and was certified.
- 8.3 **Generates no Ω-P2-R.** Not begun.  — **SUPERSEDED**: Ω-P2-R is this document.
- 8.4 **Records no finding.** Five clause-level tensions were encountered while proving the
- 8.5 **Creates no authority, registry, lifecycle, namespace, identifier or engine.** `CREATE = 0`.
- 8.6 **Amends nothing.** No clause, column, enumeration or identifier of any instrument is
- 8.7 **Admits itself no more than Ω-P1 or Ω-P2 do.** By `CEP-010` `XVIII.4` — *"An assessment

Two disclosures are load-bearing for this document's own standing and are restated with
their certified provenance:

- **`CREATE = 0` holds.** The serializer resides in the gitignored `.runtime/` zone, so it
  consumes no corpus identity and adds no candidate. Provenance: Ω-P2-E1 §8.5.
- **No standing as an assessment.** By `CEP-010 XVIII.4` — *"An assessment absent from the
  Registry SHALL be deemed non-existent, and reliance upon it IS PROHIBITED"* — this
  document holds no standing until admitted, and its presence as an untracked entry under
  `00-MASTER/EVOLUTION-001/` blocks re-assertion of the `UCOS-RFP-001` fixed point by
  `CLO-01` and `CLO-05`. Provenance: Ω-P2-E1 §8.7. **Discharged under Ω-E06-B by admission
  through the located registration transaction**; the discharge is an act recorded elsewhere,
  and adds no reasoning, measurement or interpretation here.

---

*END OF SERIALIZATION — Ω-P2-R · AUTHORITY NONE (DERIVED TRUTH) ·
STANDING ADMITTED (Ω-E06-B; issued as PROVISIONAL CANDIDATE) · 15 PROPOSITIONS SERIALIZED ·
PURE SERIALIZATION · NO NEW REASONING · NOTHING FROZEN · CONSTITUTIONAL ADMISSION EXECUTED*
