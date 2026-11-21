# Output 13 — Known Gaps

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** gap records read from their located owners — `00-CMG/CMG-REGISTRY.json → gaps[]`, `00-MASTER/UCCEP-000000/uccep-bindings.json → findings[]`, `intelligence/UCOS-RIE-AEOS-READINESS.json`, and `GOV-INT-001` §11 — at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 13 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | Gaps **recorded by located owners**, reproduced. This programme declares no gap of its own and closes none. Risks → Output 14. Open questions → Output 15. |

---

## 1. Meta-constitutional gaps (`CMG-000001` Article LXXVIII, 9 recorded)

| Id | Gap | Severity | Disposition | Closed by |
|---|---|---|---|---|
| CMG-GAP-01 | No instrument defined what a Constitution is, or which artifacts are constitutions | STRUCTURAL | **CLOSED** | Articles IV, XII–XV |
| CMG-GAP-02 | The Deferral Register is referenced across located instruments with no owner for its lifecycle | MINOR | **CLOSED** | Kind CMG-K-24 (XIII.6), LV.8, `CEP-002` Art 27 (AMD-001), `CEP-001` VIII.2/VIII.7 (AMD-001), CMG-DLG-49, LXXVIII.8 |
| CMG-GAP-03 | Multiple disjoint precedence statements with no single lattice; some pairs unrankable | STRUCTURAL | **CLOSED** | Articles XVI, XVII, LIV |
| CMG-GAP-04 | The Tier-1 superior authority presupposed by the located charter is not a located ratified artifact | **STRUCTURAL-EXTERNAL** | **RECORDED-AS-VACANCY** | `VAC-01` · open question `CMG-OQ-02` |
| CMG-GAP-05 | No located owner governs the identifier namespace of top-level meta instruments | MINOR | **CLOSED-FOR-CMG-NAMESPACE** | Article XXXIII |
| CMG-GAP-06 | No located instrument governs a program-completion ceremony | MINOR | **NOT-CLOSED** | — · reason recorded: *substantive process concern outside meta jurisdiction (XIX.2)* · open question `CMG-OQ-05` |
| CMG-GAP-07 | Latent constitutions may exist: artifacts functioning as law without recognition | STRUCTURAL | **CLOSED** | XII.5 and LII.2 |
| CMG-GAP-08 | Concern was not a first-class entity, so duplicate authority was structurally undetectable | STRUCTURAL | **CLOSED** | XIV.3–XIV.4 and `CMG-INV-02` |
| CMG-GAP-09 | No mechanism existed to admit a concept that does not yet exist without amendment | STRUCTURAL | **CLOSED** | Articles LXXVI and LXXVII |

**6 CLOSED · 1 CLOSED-FOR-CMG-NAMESPACE · 1 RECORDED-AS-VACANCY · 1 NOT-CLOSED.**

## 2. Gaps measured by this programme against located declarations

Each is a measured difference between what a located owner declares and what exists. No cause is asserted and nothing is repaired.

| Id | Gap | Declared by | Measured state | Owning authority | Method |
|---|---|---|---|---|---|
| **DG-1** | Four of the eleven declared registers do not exist: `changes.json`, `knowledge.json`, `regeneration.json`, `rollback.json` | `GOV-INT-001` §6.2 (state "READY TO ADD" at §11) | absent from `00-BOOK/DATA/` | `UCI-001` (CMG-DLG-15) | M-2 |
| **DG-2** | `UCCEP-F-003` remains recorded `GOVERNED / blocking: true` and is still named in the live `certification_ceiling`, while its substance is discharged in committed code (`engine/graph/validation.py` now includes `dependency_cycle` in `is_valid`) | `uccep-bindings.json → findings[]`; ceiling entry 3 | record open, substance closed | `UCCEP-000000` / `engine/graph` — the binding is another programme's declaration (**X-9**) | M-2 + M-3 |
| **DG-3** | Schema validation is not exercised: `ukb validate` reports *"jsonschema not installed — ran structural checks only"* | `UCCEP-F-006` / `WP-UCCEP-004` | structural checks only, PASS | `ukb.py` · CI | M-3 |
| **DG-4** | 12 `known_spine_gaps` are recorded by the intelligence engine | `intelligence/UCOS-RIE-AEOS-READINESS.json` (also `UCOS-IMP-BASELINE-001.rib.json`) | 12 entries, plus 14 `not_ready_because` and 4 `ready_because` | `intelligence/rie` producer | M-3 |
| **DG-5** | Traceability semantic completeness is RED: **1,198 of 1,198** registered artifacts carry incomplete traceability (≈22.7%), while the `traceability` **field** is non-empty on 1,199 of 1,199 | `UCCEP-F-002` / `WP-UCCEP-002`; `CK-HEALTH` advisory FAIL | field present ≠ semantically complete | `CEP-008` · `platform/measurement` · `engine/graph` | M-3 + M-4 |
| **DG-6** | Four Registry Owners declare `AUTHORITY = NONE`, which `CMG-000001` XX.8 states may not appear as an Owner: `STATUS-001`, `REG-AUTO-001`, `UCI-001`, `GOV-INT-001` | `CMG-000001` XX.8 vs `CMG-REGISTRY.json → concerns[]` | disagreement among located records | per XX.7 / Article LII: **the owner of the affected concern**, never `CMG-000001` and never this programme | M-2 |
| **DG-7** | The repository-closure verdict is not measured: the phase-3 engine returns a constant NOT-CLOSED verdict independent of state | `UCCEP-F-001` / `WP-UCCEP-001`; `CK-CLOSURE-P3` advisory FAIL | advisory failure, disclosed | UAKOS-CLOSURE successor programmes | M-3 |
| **DG-8** | 60 programme evidence files are excluded from version control by the ignore authority, including the nine seal inputs of the `UCCEP-000006` authorization | `.gitignore:72`; `UCCEP-000006` §9 reproduction instruction | evidence exists on disk, not in history | the ignore authority's owner — `REG-AUTO-001` / repository operator | M-1 |

## 3. Gaps explicitly **not** recorded here

| Not recorded | Where it belongs |
|---|---|
| The Tier T1 vacancy itself | `15-OPEN-CONSTITUTIONAL-QUESTIONS.md` (`VAC-01`, `CMG-OQ-02`) — it is a vacancy, not a gap, per `CMG-000001` XV.7 |
| Risk classification of any gap above | `14-KNOWN-RISKS.md` |
| Anything requiring a decision to resolve | `16-DECISION-DERIVED-INPUTS.md` |
| Treatment, remediation or sequencing of any gap | **nowhere in this programme** — out of scope |

---

*`UCCEP-000007` Output 13. AUTHORITY = NONE (DERIVED TRUTH). Reproduces located gap records and measured differences; closes nothing. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
