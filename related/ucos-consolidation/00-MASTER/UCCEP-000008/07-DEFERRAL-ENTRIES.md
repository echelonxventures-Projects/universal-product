# Output 7 — Deferral Entries under `CEP-002` Article 27

> **STATUS DOMAIN:** GOVERNANCE (determination) · **STATUS BASIS:** the entry-record requirements of `CEP-002` Article 27, discharged against located evidence at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000008` · OUTPUT 7 |
| ENTRIES | `DEF-01` (from `GD-08` / DDI-15) · `DEF-02` (from `GD-21` / DDI-21) |
| GOVERNING AUTHORITY | `00-CEP/CEP-002` **Article 27** — Deferral Register lifecycle (`CMG-DLG-49`, owner `CEP-002` by its Article 27, added by `CEP-002-AMD-001` under Article 21) |
| AUTHORITY | None of its own. This output creates no register and no lifecycle; it records two entries against the located Deferral Register lifecycle. |
| BINDING RULE | `CEP-002` 27.3 — *"This Article creates **no new register and no new storage** … A second deferral register, deferral store, deferral pipeline, or deferral gate IS PROHIBITED (8.3, `CEP-001` VII.2)."* This output is therefore **not** a deferral register. It is two entry records, held in this programme's own governance home, against the single located append-only Deferral Register established by `CEP-000` §7.4/§9.3/§9.5/§34.9/§35.4 and `CEP-001` VIII.2/XVII.1/XVIII.4/XXII.3, and operational memory under `CEP-002` 18.3. |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12` (condition **C-3**, constraint **K-09**). |

---

## 1. Why two matters are held and not decided

Of the 21 Decision-Derived Inputs, 19 were resolvable by a located authority and are dispositioned in outputs 1–6. Two were not:

| Entry | Matter | Reason no located authority can decide it |
|---|---|---|
| `DEF-01` | `GD-08` / DDI-15 — the `AUTHORITY = NONE` vs Registry-Owner tension (`DG-6`) | **Too many owners.** `CMG-000001` XX.7 provides that a disagreement among located ownership records *"IS a finding under Article LII and SHALL be disposed by the owner of the affected concern, never by this instrument"*. Four concerns are affected, so no single act disposes it. LII.3: audit *"SHALL emit findings and SHALL decide nothing."* |
| `DEF-02` | `GD-21` / DDI-21 — occupancy of constitutional Tier T1 | **No owner at all.** Tier T1 is recorded `located: false`; `CEP-006` names no competent authority; `UCCEP-000006` classifies the dependency as `ED-1`, an external constituent act, *"not manufacturable"*. `CMG-000001` XVII.4 forbids skipping the tier or promoting a lower instrument into it. |

`CMG-000001` LVII.3 makes holding the required response in both cases: a question undecidable by any located authority *"SHALL be recorded as an **open constitutional question** and SHALL be routed to explicit ratification. It SHALL NOT be decided by default, by the detector, by the most convenient authority, or by silence."* `XV.7` / `CMG-P-06` make recording mandatory, and IX.6 provides that *"A missing superior authority is recorded, not assumed."*

**Holding is a valid disposition of the matter. It is not a disposition under `CEP-002` 28.13** — see §4.

---

## 2. `DEF-01` — The `AUTHORITY = NONE` versus Registry-Owner tension

Recorded against the nine minimum elements of `CEP-002` **27.4**. An entry missing any element *"IS incomplete and SHALL be treated as undispositioned"*, so each is discharged explicitly.

| # | Element required by 27.4 | Record |
|---|---|---|
| 1 | **Identity** | `DEF-01` · scope `UCCEP-000008` · raised by `GD-08` · resolves `DDI-15` · finding of record `DG-6` |
| 2 | **The matter deferred** | Whether the four Registry Owners that declare `AUTHORITY = NONE` — `STATUS-001` (`CMG-DLG-14`), `REG-AUTO-001` (`CMG-DLG-13`), `UCI-001` (`CMG-DLG-15`), `GOV-INT-001` (`CMG-DLG-16`) — may lawfully appear as Owners in `CMG-REGISTRY.json → concerns[]`, given `CMG-000001` XX.8: *"A derived-truth artifact owns no concern and SHALL NOT appear as an Owner in the Registry."* Both records are located and both stand. |
| 3 | **Deferring authority and the jurisdiction under which it acted** | `UCCEP-000008` (this programme), acting **not** as a jurisdiction over the matter but under the express reservation of `CMG-000001` XX.7 (*"never by this instrument"*, extended by `UCCEP-000007` Output 16 to *"never by a measuring programme"*, and by `GD-08` on the same reasoning to a determining programme that does not own the concern) and Article LII.3 (audit decides nothing). The programme's own jurisdiction here is limited to **recording and routing**. |
| 4 | **Basis for deferral** | `CMG-000001` XX.7 (disagreement is a finding, disposed by the affected concern's owner); LII.3 (read-only detection, disposition rests with the concern owner); LVII.3 (a genuine contradiction is held, never decided by default or by the most convenient authority); XVII.8 (no instrument determines jurisdiction it does not own); XV.7 / `CMG-P-06` (concealment prohibited). |
| 5 | **Deferring condition whose persistence justifies continued deferral** | **Both located records stand unamended and no affected concern owner has disposed the finding.** Specifically: `CMG-000001` XX.8 remains in force, and `CMG-REGISTRY.json → concerns[]` continues to record `CMG-DLG-13/14/15/16` with those four Owners. While both hold simultaneously and no owner has acted, the deferral is upheld. |
| 6 | **Owner to whom the matter returns on resolution** | **Four owners, individually** — `REG-AUTO-001` for `CMG-DLG-13`; `STATUS-001` for `CMG-DLG-14`; `UCI-001` for `CMG-DLG-15`; `GOV-INT-001` for `CMG-DLG-16`. Per XX.7 the finding is disposed **by the owner of the affected concern**; no single act resolves all four. Expressly **not** `CMG-000001` (*"never by this instrument"*) and **not** this programme. |
| 7 | **Declared review point** | The **earliest** of: (i) the next governance gate under `CEP-002` 24.1 / `CEP-001` XXIII — operationally, the next full-tier run of the located aggregate gate; (ii) the next stage boundary; (iii) the next readiness assessment (`CEP-002` 12.5); and (iv) **any certification claim above `CERTIFIED-PROVISIONAL`**, which `CMG-000001` LII.6 makes contingent on this finding's disposition. `CEP-002` 27.13 requires review no later than the earliest of these. |
| 8 | **Current entry state** | **`RECORDED`** — the initial state required by `CEP-002` 27.9. |
| 9 | **Reference to bound evidence** | `00-MASTER/UCCEP-000007/13-KNOWN-GAPS.md` §2 (`DG-6`) · `00-MASTER/UCCEP-000007/09-OWNERSHIP-INVENTORY.md` §5 · `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` XX.7 / XX.8 / LII.3 / LII.6 / LVII.3 / XV.7 · `00-CMG/CMG-REGISTRY.json → concerns[]` (`CMG-DLG-13`, `CMG-DLG-14`, `CMG-DLG-15`, `CMG-DLG-16`) · the four instruments' own front matter in `00-BOOK/CONTROL-TOWER/` · `02-GDR-B-OWNERSHIP-ALLOCATION-AND-CONSOLIDATION-MAPPING.md` `GD-08` |

### Entry conditions satisfied (`CEP-002` 27.6)

Qualifies under **27.6(d)** — *"it IS a review or dispute finding dispositioned as deferred rather than accepted or rejected"* — the disagreement being a finding under Article LII whose disposition is reserved. Also within **27.6(c)**, *"a matter knowingly not decided"*. Not 27.6(f): no artifact transitions `DRAFTED → DEFERRED`, so the one-to-one correspondence duty of 27.7 is not engaged.

### Deferral, not exception (`CEP-002` 27.8)

Recorded as a **deferral**: a matter knowingly not decided. It is **not** an exception — no rule is departed from, no enforcement is waived, and nothing here permits governance to waive, defer or override enforcement (27.8, 8.5, 24.4). The finding's certification-blocking effect under `CMG-000001` LII.6 remains fully in force.

### Exit conditions (`CEP-002` 27.10 — the only lawful transitions)

| Transition | Trigger for `DEF-01` |
|---|---|
| `RECORDED → UNDER-REVIEW` | The declared review point is reached, or a governance gate, stage boundary or readiness assessment triggers review (27.13). |
| `UNDER-REVIEW → RECORDED` | Review upholds the deferral because the deferring condition still holds. A **new** declared review point is recorded in the same act and the prior review is retained (27.10). |
| `UNDER-REVIEW → RESOLVED` | Review determines the deferring condition no longer holds — i.e. the affected concern owners have disposed the finding, or the underlying records no longer disagree. The matter returns to its recorded owners. |
| `UNDER-REVIEW → WITHDRAWN` | Review determines the matter is no longer required, or is displaced by a later canonical definition. |

**Prohibited:** any transition not enumerated above (27.11). In particular `RECORDED → RESOLVED` directly is prohibited — *"every exit IS reviewed"*. No exit by silence, lapse of time, unilateral action of the deferring party, or absence of objection (27.12). Review must be performed by an entity other than the deferring party, escalating one level under Article 12 where they coincide (27.15) — which here they do not, since the reviewers are the four concern owners and the deferring party is this programme.

---

## 3. `DEF-02` — Occupancy of constitutional Tier T1

| # | Element required by 27.4 | Record |
|---|---|---|
| 1 | **Identity** | `DEF-02` · scope `UCCEP-000008` · raised by `GD-21` · resolves `DDI-21` · located records `VAC-01`, `CMG-OQ-02`, `CMG-GAP-04`, `UCCEP-F-004` |
| 2 | **The matter deferred** | Which authority, if any, occupies constitutional **Tier T1** (Constitutional Authority over substance). The declared superior is the ratified UCOS Ω∞ Constitution presupposed at `CEP-000` §5.5 Tier 1 and §6.4; `VAC-01` records `located: false`, the referent existing only as frozen non-normative `.docx` source material under `00-SOURCE/CONSTITUTIONS/`. |
| 3 | **Deferring authority and the jurisdiction under which it acted** | `UCCEP-000008`, acting under the **procedural** authority of `CMG-000001` XVII.4 (the four-step vacancy closure procedure) and `CEP-002` Article 27. It claims **no** jurisdiction over the matter: `CMG-000001` XVII.2 resolution reaches a tier recorded `located: false`, so no Owner resolves, and XVII.8 bars any instrument from determining jurisdiction it does not own. |
| 4 | **Basis for deferral** | `CMG-000001` XVII.4 (*"SHALL NOT skip the tier and SHALL NOT promote a lower instrument into it"*; treat dependent determinations as PROVISIONAL under `CMG-L-12`); LVII.3 (undecidable through vacancy → open constitutional question, routed to explicit ratification); XV.7 / `CMG-P-06` and IX.6 (recorded, not assumed; concealment prohibited); `CEP-006` names no existing competent authority; `UCCEP-000006` **`ED-1`** — *"external constituent act … No programme may self-ratify."* |
| 5 | **Deferring condition whose persistence justifies continued deferral** | **No external constituent act has occurred, and no ratified normative artifact occupies Tier T1.** While `VAC-01` records `located: false` and `CMG-OQ-02` remains OPEN, the deferral is upheld. No in-repository act can alter this condition. |
| 6 | **Owner to whom the matter returns on resolution** | **An external constituent authority, by explicit ratification** — identified through open question `CMG-OQ-02`, whose requirement is recorded as EXPLICIT RATIFICATION. Expressly **not** any located instrument, **not** `CMG-000001`, **not** `CEP-006`, **not** `GOV-INT-001`, and **not** any programme (`ED-1`: no programme may self-ratify). On closure, authority resolution is re-run per XVII.4(d). |
| 7 | **Declared review point** | The **earliest** of: (i) the next governance gate under `CEP-002` 24.1 / `CEP-001` XXIII; (ii) the next stage boundary; (iii) the next readiness assessment (`CEP-002` 12.5); (iv) any attempt to declare standing above PROVISIONAL, any certification claim above `CERTIFIED-PROVISIONAL`, or any freeze eligibility assessment under `CEP-007` IV.1 — each of which depends on this matter (see `GD-10`). Per 27.13, review occurs no later than the earliest. |
| 8 | **Current entry state** | **`RECORDED`** — the initial state required by `CEP-002` 27.9. |
| 9 | **Reference to bound evidence** | `00-CMG/CMG-REGISTRY.json → vacancies[]` (`VAC-01`) and `→ open_questions[]` (`CMG-OQ-02`) · `00-MASTER/UCCEP-000007/15-OPEN-CONSTITUTIONAL-QUESTIONS.md` §1–§4 · `00-MASTER/UCCEP-000007/11-CERTIFICATION-INVENTORY.md` §4/§6/§8 (`UCCEP-F-004`, ceiling, **C-3**/**K-09**) · `00-CMG/CMG-000001-…md` XVII.2 / XVII.4 / XVII.8 / XV.7 / IX.6 / LVII.3 / `CMG-L-12` · `00-CEP/CEP-000-CONSTITUTIONAL-ENGINEERING-CHARTER.md` §5.5 / §6.4 · `00-CEP/CEP-006-CONSTITUTIONAL-RATIFICATION-CONSTITUTION.md` · `00-MASTER/UCCEP-000006/` (`ED-1`) · `06-GDR-F-CONSTITUTIONAL-VACANCY.md` `GD-21` |

### Entry conditions satisfied (`CEP-002` 27.6)

Qualifies under **27.6(c)** — *"a matter knowingly not decided, or a decision raised and not resolved"* — and under **27.6(b)**, since the matter *"falls within no registered governance domain"*: `CMG-REGISTRY.json` records no Owner for Tier T1, only a vacancy. Not 27.6(f); the 27.7 correspondence duty is not engaged.

### Deferral, not exception (`CEP-002` 27.8)

Recorded as a **deferral**. No rule is departed from and no enforcement waived. The vacancy's blocking effects stand in full: `UCCEP-F-004` remains blocking, the certification ceiling remains `CERTIFIED-PROVISIONAL`, 31 of 43 recognized artifacts remain PROVISIONAL, and `CMG-000001`'s own registry state remains PROVISIONAL.

### Exit conditions (`CEP-002` 27.10)

| Transition | Trigger for `DEF-02` |
|---|---|
| `RECORDED → UNDER-REVIEW` | The declared review point is reached, or a governance gate, stage boundary or readiness assessment triggers review (27.13). |
| `UNDER-REVIEW → RECORDED` | Review upholds the deferral because no external constituent act has occurred. A **new** declared review point is recorded and the prior review retained. |
| `UNDER-REVIEW → RESOLVED` | An external constituent act occurs: an authority is identified by explicit ratification and `VAC-01` closes. Authority resolution is then re-run (`CMG-000001` XVII.4(d)) and every determination in this register becomes re-assessable by its own cited Owner. |
| `UNDER-REVIEW → WITHDRAWN` | Review determines the matter is displaced by a later canonical definition of the tier model — a determination for the owner of the precedence lattice, not for this programme, and adjacent to open question `CMG-OQ-03`. |

**Prohibited:** any transition not enumerated (27.11); direct `RECORDED → RESOLVED` (every exit is reviewed); exit by silence, lapse of time, unilateral action, or absence of objection (27.12). Note the standing constraint of `GD-21-C4`: no consolidation act may purport to close `VAC-01`, `CMG-GAP-04`, `CMG-OQ-02` or `UCCEP-F-004`.

---

## 4. Why a held matter is not an undispositioned decision

This section is load-bearing: if either entry were an undispositioned decision, `CEP-002` 28.18 would close the Implementation Evidence Gate and halt the programme. Neither is.

| Step | Provision | Consequence |
|---|---|---|
| 1 | `CEP-002` **28.16** — *"Recording a matter in the Deferral Register under Article 27 IS **not** a disposition under 28.13, and SHALL NOT satisfy any obligation of this Article."* | A held matter carries no 28.13 disposition. This is stated, not evaded. |
| 2 | `CEP-002` **28.4 / 28.8** — Article 28 binds *"every **constitutionally agreed** decision"*, and the lifecycle's second stage is CONSTITUTIONAL AGREEMENT, at which *"the competent authority of 11.2 agrees the decision."* | Neither matter has been agreed by a competent authority. For `DEF-01` the competent authorities are four concern owners, none of which has acted; for `DEF-02` no competent authority exists. Neither matter has entered the lifecycle. |
| 3 | `CEP-002` **28.14** — undispositioned means a **decision** with no disposition, more than one, or unresolving evidence. | A matter that is not a decision cannot be an undispositioned decision. `DEF-01` and `DEF-02` are matters, not decisions. |
| 4 | `CEP-002` **28.18** — the Gate is CLOSED while any *"previously ratified or recorded decision IS undispositioned."* | Neither matter is ratified, and neither is **registered as a decision** in any located register. Both are therefore outside the population the Gate governs. |
| 5 | Constraints `GD-08-C4` and `GD-21-C4` | Forbid registering either matter as a decision, so step 4 remains true by construction rather than by accident. |
| 6 | `CMG-000001` **LVII.3**, **XV.7** / `CMG-P-06` | Holding is the required response, and recording the hold is mandatory — so the entries must exist. |

**Verified consequence:** the mechanical Gate value is unchanged by this programme. `00-MASTER/UCDA-000001/ucda-decisions.json` is not modified, so the located check `CK-DECISION-EVIDENCE` continues to compute over the same 64 decisions with 0 undispositioned and gate `OPEN`. Verification is recorded in `09-TRACEABILITY-VERIFICATION.md` §5.

**What the holds *do* block**, recorded honestly: `CMG-000001` **LII.6** provides that an undispositioned **finding** blocks certification under Article LXXX. `DG-6` (via `DEF-01`) and `UCCEP-F-004` (via `DEF-02`) are such findings. Both therefore constrain any certification claim above `CERTIFIED-PROVISIONAL` — which is already the corpus's recorded ceiling. They do not block `M-1A` or any consolidation step.

---

## 5. Entry summary

| Entry | Matter | State | Owner on return | Deferring condition | Blocks |
|---|---|---|---|---|---|
| `DEF-01` | `AUTHORITY = NONE` vs Registry-Owner (`DG-6`) | **RECORDED** | four concern owners: `REG-AUTO-001`, `STATUS-001`, `UCI-001`, `GOV-INT-001` | both located records stand; no owner has disposed the finding | certification above `CERTIFIED-PROVISIONAL` (`CMG-000001` LII.6) |
| `DEF-02` | Tier T1 occupancy (`VAC-01`, `CMG-OQ-02`) | **RECORDED** | an external constituent authority, by explicit ratification | no external constituent act; no ratified artifact occupies T1 | non-provisional standing corpus-wide; freeze eligibility (`GD-10`); closure of `CMG-GAP-04` / `UCCEP-F-004` |

**Neither entry blocks `M-1A` or any consolidation step.** Both are Gate-neutral by §4.

## 6. What this output does not do

- It creates **no** deferral register, store, pipeline or gate (`CEP-002` 27.3).
- It **decides** neither matter, and adopts no default reading of either.
- It does **not** narrow, re-scope, or answer `CMG-OQ-01`, `CMG-OQ-02`, `CMG-OQ-03`, `CMG-OQ-05` or `CMG-OQ-07`, nor close `VAC-01`, `CMG-GAP-04`, `DG-6` or `UCCEP-F-004`.
- It writes **nothing** outside `00-MASTER/UCCEP-000008/`; `00-CMG/` (**X-3**) and every other programme's outputs (**X-9**) are untouched.
- It assigns **no** severity to either matter — severity is its owner's to assign, as `UCCEP-000007` Output 14 also records of itself.

---

*`UCCEP-000008` Output 7. Two entry records against the located Deferral Register lifecycle of `CEP-002` Article 27. No register created, no matter decided, no question answered, no vacancy concealed, no enforcement waived. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12`.*
