# IMR-0000/15 — GOVERNANCE FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `15` — Governance Framework (**deliverable 25**) · directive capability 19 |
| ARTIFACT KIND | Framework (`CMG-K-05`) — binding declaration · **zero net-new governance rules** |
| SUBSYSTEM | `SS-14` `CIOS-GI` (engines `E-09` impact/classification/admission, `E-18` override adjudication; public port **`CIOS-P-35`**) |
| CENTRAL CLAIM | **The platform governs nothing.** It declares which located authority governs each platform question, and it is itself governed by all of them. |
| AUTHORITY OF ITS OWN | **NONE.** `CIOS-01` I.6 — no gate authority; `CIOS-INV-12` — no concern. |
| CONFLICT RULE | Located instrument governs (`CEP-001` supreme operational, then `CMG-000001` meta-governance, then `CEP-002`, then `GOV-INT-001`); then `IMR-003A` (`CIOS-14`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE AUTHORITY TIERS

`CMG-000001` declares eight tiers. Reproduced **by reference** because the platform's position within them is the whole point of this framework.

| Tier | Name | Occupancy at `b26c5bb` | Platform's relation |
|---|---|---|---|
| `T0` | Constitutional Source Corpus | LOCATED | consumed read-only |
| **`T1`** | **Constitutional Authority** | **VACANT — `VAC-01`** | **no authority competent to ratify anything, including this mission** |
| `T1M` | Meta-Constitutional Authority | LOCATED | consumed read-only |
| `T2` | Program Authority | LOCATED | the platform's own standing derives here, capped PROVISIONAL |
| `T2I` | Interpretive Authority | LOCATED | consumed read-only |
| `T3` | Domain Authority | LOCATED | consumed read-only |
| `T4` | Execution Authority | LOCATED | **holds dispatch**; the platform hands off to it and holds nothing |
| `T5` | Derived-Truth Authority | LOCATED | where every platform observation and derived view sits |

**`T1` vacancy is the single most consequential fact in this framework.** It caps every determination in this mission at PROVISIONAL (`CMG-L-12`), makes ratification unavailable (`CEP-006`), makes active certification unavailable, and makes freeze ineligible. Nothing the platform does can alter it; `CIOS-G-03` is its gate and `CEP-006`'s authority owns it.

---

## 2. THE GOVERNANCE BINDING MAP

Which located authority governs each platform question. **Every row points outward.**

| Platform question | Governing instrument | Delegation |
|---|---|---|
| Is this act lawful at all? | `CEP-001` (supreme operational) — LAW-1 supremacy, LAW-2 evidence, LAW-4 single canonicity, LAW-5 non-bypass, LAW-7 preservation, LAW-8 determinism | `CMG-DLG-48` |
| Who governs governance? | `CMG-000001` (meta-governance) — tiers, kinds, states, concerns, vacancies | retained `CMG-RET-01…11` |
| How is a decision governed and dispositioned? | `CEP-002` **Article 28**; machine overlay at `UCDA-000001` | `CMG-DLG-02`, `CMG-DLG-49` |
| How is execution governed? | `CEP-003`; `GOV-INT-001` SECTION 8; `IEC-001` `09` / C12 | `CMG-DLG-03` |
| How is validation governed? | `CEP-004` | `CMG-DLG-04` |
| How is certification governed? | `CEP-005` | `CMG-DLG-05` |
| How is anything ratified? | `CEP-006` — **unavailable**, `T1` VACANT | `CMG-DLG-06` |
| How is anything frozen? | `CEP-007` — **unavailable**, ineligible while `VAC-01` is open | `CMG-DLG-07` |
| What counts as evidence and traceability? | `CEP-008` | `CMG-DLG-08` |
| How does anything change or evolve? | `CEP-009` — the **sole** evolution authority | `CMG-DLG-09` |
| How is compliance audited? | `CEP-010` | `CMG-DLG-10`, `CMG-DLG-11` |
| How is registration governed? | `REG-AUTO-001` | `CMG-DLG-13` |
| How is status determined? | `STATUS-001` | `CMG-DLG-14` |
| How is change intelligence governed? | `UCI-001` (+ `UCI-OPT-001` optimization determination) | `CMG-DLG-15` |
| How do governance instruments integrate? | `GOV-INT-001` | `CMG-DLG-16` |
| How is knowledge governed? | `UCOS-BOOK-000000`; `UAKOS-CLOSURE-002` charter | `CMG-DLG-17` |

| Property | Value |
|---|---|
| Governance rules created by this framework | **0** |
| `CIOS-14`'s `GR-01 … GR-33` | **all 33 externally owned**; bound by pointer, restated **0** times |
| Concerns claimed in `CMG-REGISTRY.json` | **0** — `CIOS-G-02` **OPEN** |
| Delegations named | **16 of 60** located concerns, being those that govern a platform question |
| Tiers occupied by the platform | **0** — it holds no tier; its standing derives from `T2` |

---

## 3. WHAT `SS-14` ACTUALLY DOES

Governance *intelligence*, not governance. Two engines, four admission determinations, one override adjudication.

| Determination | Stage | Located gate | On failure |
|---|---|---|---|
| constitution conformance | `CIOS-S-09` | `G-04` Constitution Gate | non-admission |
| architecture admission | `CIOS-S-10` | `G-05` Architecture Admission Gate | non-admission |
| impact assessment (`CEP-009` III.1) | `CIOS-S-15` | `G-09` Governance Gate | non-admission |
| change classification — **exactly one** primary class (`CEP-009` IV.6) | `CIOS-S-16` | `G-09` | non-admission on ambiguity |
| governance admission by the located authority | `CIOS-S-17` | `G-09` | non-admission |
| evidence sufficiency + disposition obligation | `CIOS-S-18` | `G-12` + `CK-DECISION-EVIDENCE` | non-admission |
| override adjudication | post-dispatch | `CIOS-P-35`; `CIOS-OR-01`/`OR-02` only | reject; **an unrecorded override is void** |

`SS-14` does **not**: write a governance rule, add a concern, issue a gate verdict of its own, ratify, certify, freeze, or admit an override from any authority outside the located pair.

---

## 4. THE DECISION DISPOSITION OBLIGATION

The one governance mechanism a future platform mission is most likely to overlook, so it is stated rather than merely bound.

| Obligation | Source | Consequence of breach |
|---|---|---|
| Every architectural decision SHALL carry a constitutional disposition | `CEP-002` Article 28 (added by `CEP-002-AMD-002`) | an owned concept whose decision is undispositioned **closes the Implementation Evidence Gate** (Art 28.14, 28.18) |
| Dispositions are recorded machine-readably | `00-MASTER/UCDA-000001/ucda-decisions.json`, rendered at `01-CONSTITUTIONAL-DECISION-REGISTER.md` | — |
| A rejected alternative SHALL be recorded as REJECTED **with constitutional justification**, not silently dropped | located precedent `DEC-ADAM-10R` | an unrecorded rejection is an undispositioned decision |

**Observed state:** 64 decisions, **0 undispositioned**, 205 evidence items, gate OPEN, seal `8d34d196a80a05b8`.

**Applied to this mission.** `IMR-0000`'s own architectural decisions — the refusal of a new subject token, the five BINDING-ONLY subsystems, the two contract-only registries, the declaration-scoped freeze — are recorded as disclosed divergences `D-1 … D-7` (`00` §6) with their constitutional justification stated in each case. Whether they require entry in `ucda-decisions.json` is **`UCDA-000001`'s determination, not this mission's**; the platform adds no decision entry (`RC-07` prohibition). Recorded as `PF-04` in `23`.

---

## 5. HOW THE PLATFORM IS GOVERNED

The framework's reflexive test. A governance framework that did not state its own subjection would be asserting authority by omission.

| Question | Answer |
|---|---|
| What governs `IMR-0000`? | every instrument in §2, plus `IMR-003A` where it is more specific |
| What is `IMR-0000`'s standing? | **PROVISIONAL**, capped by `T1` vacancy (`CMG-L-12`) |
| Can `IMR-0000` be ratified? | **No** — no competent authority (`CEP-006`; `CIOS-G-03`) |
| Can `IMR-0000` be certified active? | **No** — ceiling `CERTIFIED-PROVISIONAL` |
| Can `IMR-0000` be frozen? | **No** — `CEP-007` ineligible; an attempt would be **void** |
| How does `IMR-0000` change? | `CEP-009` III.1 with an impact assessment; **never** by in-place edit of a `IMR-003A` artifact |
| What happens where `IMR-0000` conflicts with a located instrument? | the located instrument governs and `IMR-0000` **SHALL be corrected** |
| Does `IMR-0000` govern any future programme? | **No.** It offers a binding surface. Governing authority over future programmes would require `CIOS-G-01` (a `GOV-001` Part 11 migration determination) and `CIOS-G-02` — both **OPEN** |

**The last row is the honest limit of this mission.** The instruction asks for a platform that *"will govern every future engineering programme"*. What is delivered is a platform that every future programme may **bind by composition and reference**. Governing supremacy is not conferred, cannot be self-conferred (`CEP-009` I.5), and remains behind two open, owner-held gates. Recorded as divergence `D-6` (`00` §6) and finding `PF-05` (`23`).

---

## 6. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner |
|---|---|
| Create, amend or interpret a governance rule | `CEP-001…010`; `CMG-000001`; `CIOS-14`'s 33 `GR-*` are all located |
| Claim a concern, tier, kind, state or delegation | `CMG-000001`; `CIOS-G-02` OPEN |
| Issue a gate verdict, or re-implement a gate | `G-01 … G-14`; `IEC-001` `08` |
| Ratify, certify or freeze anything | `CEP-006`; `CEP-005`; `CEP-007` — all unavailable |
| Add a decision, or alter a disposition | `UCDA-000001`; `CEP-002` Art 28 |
| Own an evolution model or create an evolution entry | `CEP-009` |
| Confer governing supremacy on CIOS or on itself | `CIOS-G-01`, `CIOS-G-02` OPEN; `CEP-009` I.5 |
| Discharge `VAC-01` or any inherited finding | `CEP-006` authority; each finding's owner |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework binds platform questions to located governing authorities. **It creates no governance rule, claims no concern, issues no verdict, ratifies nothing, certifies nothing and freezes nothing.** All 33 located governance rules are bound by pointer and restated nowhere. The platform holds no tier and no gate; its own standing is PROVISIONAL and capped by `T1` vacancy, and governing supremacy over future programmes is expressly **not conferred**. Every authority named is located in an instrument existing independently at `b26c5bb`. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/15` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
