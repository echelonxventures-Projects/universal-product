# Output 9 — Traceability Verification

> **STATUS DOMAIN:** GOVERNANCE (verification) · **STATUS BASIS:** mechanical checks executed against the repository at HEAD `9de85ad`; every figure below is a measured result, not an assertion

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000008` · OUTPUT 9 |
| OUTPUT | 9 — Traceability Verification |
| SUBJECT | Proof that (1) no DDI disappeared, (2) no decision lacks authority, (3) no decision lacks repository traceability, (4) the register is append-only and boundary-compliant, and (5) the mechanical Implementation Evidence Gate is unchanged. |
| AUTHORITY | None. This output verifies; it decides nothing and amends no decision. |
| METHOD | The four admissible methods `UCCEP-000007` Output 0 §2 declares, reproduced never coined: **M-1** direct git measurement · **M-2** direct file measurement · **M-3** located owner's own output · **M-4** independent recomputation. A statement with no method marker is not a finding of this output. |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12` (condition **C-3**, constraint **K-09**). |

---

## 1. No DDI disappeared — DDI → GD closure

The mission's binding validation requirement, and the constitutional obligation of `GD-13` clause 6 (*omission counts as deletion*; `CMG-000001` XV.7 / `CMG-P-06`, LII.6).

**Measured (M-2):** each `DDI-01` … `DDI-21` appears as a `Resolves` target **exactly once** across the six family outputs.

```
DDI-01=1 DDI-02=1 DDI-03=1 DDI-04=1 DDI-05=1 DDI-06=1 DDI-07=1
DDI-08=1 DDI-09=1 DDI-10=1 DDI-11=1 DDI-12=1 DDI-13=1 DDI-14=1
DDI-15=1 DDI-16=1 DDI-17=1 DDI-18=1 DDI-19=1 DDI-20=1 DDI-21=1
```

**Measured (M-2):** `GD-01` … `GD-21` each appear as a decision heading **exactly once**; total headings **21**; no duplicate, no gap, no reuse.

| Check | Required | Measured | Result |
|---|---|---|---|
| DDIs in the canonical backlog | 21 | 21 | ✔ |
| DDIs mapped to a `GD` | 21 | 21 | ✔ **PASS** |
| DDIs mapped more than once | 0 | 0 | ✔ |
| DDIs unmapped / dropped / merged / renamed | 0 | 0 | ✔ |
| `GD` decisions declared | 21 | 21 | ✔ |
| `GD` ids duplicated | 0 | 0 | ✔ |
| `GD` ids skipped in sequence `01…21` | 0 | 0 | ✔ |

**Verdict: no DDI disappeared.** The map is a bijection.

## 2. Numbering continuity and append-only evolution

| Check | Measured | Method | Result |
|---|---|---|---|
| `GD-nn` allocated forward-only, `01`→`21`, no reuse | 21 unique, contiguous | M-2 | ✔ |
| `DEF-nn` allocated forward-only | `DEF-01`, `DEF-02` | M-2 | ✔ |
| `WP-GDR-nnn` allocated forward-only | `WP-GDR-001`, `WP-GDR-002` | M-2 | ✔ |
| Identifier collision with any located set (`WP-UCCEP-*`, `WP-UCDA-*`, `OA-n`, `DEC-*`) | **0** — `grep` for `WP-GDR-` outside this programme returns nothing; `ucda-decisions.json` `work_packages` are `WP-UCDA-001…007` only; no `GD-`/`DEF-` id exists elsewhere | M-2 | ✔ |
| Any completed decision renumbered, rewritten, or deleted during recovery | **0** | M-1 | ✔ |
| Any decision's disposition changed after recording | **0** | M-2 | ✔ |

### 2.1 One append-only correction, recorded

`CEP-002` 28.15 and `GD-13-C2` require that a change be recorded rather than made silently. One correction was made after the family outputs were complete:

| Field | Record |
|---|---|
| **What** | `00-GOVERNANCE-DECISION-INDEX.md` §6 (Reference convention): four convention rows **added**, covering (i) programme-relative paths `<PROGRAMME-ID>/NN-NAME.md` resolving under `00-MASTER/`, (ii) bare filenames introduced earlier under another programme's path, (iii) `<zone>/<INSTRUMENT-ID>` shorthand, (iv) `<path> :: <SYMBOL>` / `<path> → <field>` forms and elision templates. |
| **Why** | §3 below measured that 15 cited paths used the programme-relative form, which the original two-row convention did not cover, and that other-programme bare filenames were likewise uncovered. Left uncorrected, those citations would be unresolvable under the register's own declared convention — a traceability defect. |
| **Basis** | Repository integrity: `CEP-002` 25.4 (every declaration provable by evidence and traceability); `CEP-008` (`CMG-DLG-08`, evidence and traceability operation). |
| **Scope** | A **convention table only**. No decision, no disposition, no authority citation, no acceptance criterion, no numbering, and no traceability record was altered. `GD-01` … `GD-21` are untouched. |
| **Append character** | Rows were **added**; the pre-existing rows were retained in substance (the root-relative rule survives as *"any other path containing `/`"*). No rule was deleted. |

## 3. Every decision has repository traceability — evidence resolution

**Method M-2**, executed by extracting every backtick-delimited citation from all outputs of this programme and testing resolution against the repository at HEAD `9de85ad`, classified by the declared reference convention.

| Class | Cited | Resolved | Unresolved | Result |
|---|---|---|---|---|
| **A** — fully-qualified repository paths (`00-BOOK/`, `00-CEP/`, `00-CMG/`, `00-MASTER/`, `00-SOURCE/`, `02-MASTER/`, root-level `NN-*.md`, `adr/`, `knowledge/`, `.gitignore`, `engine/`, `intelligence/`) | 68 | **63** | 2 declared-absent + 3 convention forms | ✔ |
| **B** — programme-relative paths (`<PROGRAMME-ID>/NN-NAME.md`, resolving under `00-MASTER/`) | 15 | **15** | 0 | ✔ |
| **C** — bare `NN-*.md` shorthand (sibling outputs, or artifacts introduced earlier under a fully-qualified path) | 26 | **24** | 2 (this output and Output 10, which resolve on writing) | ✔ |
| **Total literal paths** | 109 | **102** | see below | ✔ **PASS** |

### The unresolved citations, itemized — every one accounted for

| Citation | Why it does not resolve | Defect? |
|---|---|---|
| `00-BOOK/DATA/changes.json` | **Declared absent by decision.** Registers 8–11 do not exist at this HEAD; that absence is the subject of `GD-19` and gap `DG-1`. Citing it is citing the gap. (Same applies to `knowledge.json`, `regeneration.json`, `rollback.json` where cited as bare filenames.) | No |
| `00-MASTER/UCCEP-000001` | **Declared absent by decision.** Its absence is the subject of `GD-18` and observation `OBS-2`. | No |
| `00-CEP/CEP-002`, `00-CMG/CMG-000001` | `<zone>/<INSTRUMENT-ID>` shorthand — convention §6 row 4. Both instruments' full filenames are cited at first use and both resolve: `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md`, `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md`. | No |
| `00-MASTER/UCCEP-000008/NN-NAME.md` | A **template** in the convention table itself — convention §6 row 6. | No |
| `09-TRACEABILITY-VERIFICATION.md`, `10-REMAINING-GOVERNANCE-GAPS.md` | Forward references to siblings; both resolve once written. | No |

**Unresolved defects: 0.** Every citation either resolves, is a declared absence that a decision is *about*, or is a declared convention form.

### 3.1 Evidence sufficiency per disposition

`CEP-002` 28.14 makes a decision undispositioned if its required evidence does not resolve. Checked per disposition class:

| Disposition | Count | Required evidence | Measured | Result |
|---|---|---|---|---|
| **(b)** REPRESENTED BY AN EXISTING CANONICAL CAPABILITY | 13 | *"the single canonical owner and its located artefact"* (28.13(b)) | 13 decisions, each naming **exactly one** canonical owner whose artifact resolves: `GOV-INT-001` ×5, `REG-AUTO-001` ×3, `CMG-000001` ×2, `CEP-002` ×1, `CEP-003` ×1, `CEP-007` ×1 | ✔ 13/13 |
| **(c)** REGISTERED AS AN IMPLEMENTATION WORK PACKAGE | 3 | *"a located work package carrying an owner, a constitutional route, and an acceptance condition"* (28.13(c)) | 3 packages: `OA-2` (located externally, resolves), `WP-GDR-001`, `WP-GDR-002` (declared at Output 8 §5). Each carries all three elements | ✔ 3/3 |
| **(d)** REJECTED WITH CONSTITUTIONAL JUSTIFICATION | 3 | *"the constitutional basis of the rejection, cited to the governing clause"* (28.13(d)) | 3 decisions, each citing named clauses: `GD-02` (`CMG-000001` XVII.8/X.1/X.14, `CEP-002` 8.3); `GD-10` (`CEP-007` III.2/IV.1/IV.4/V.1/V.5/I.3/I.5/II.4); `GD-14` (`CEP-009` II.4/III.3/IV.6/XII, `CEP-007` XI.2/XI.3, `REG-AUTO-001` P4/L5, `CMG-L-14`) | ✔ 3/3 |
| **(a)** IMPLEMENTED | 0 | — | Not used: this programme realizes nothing | ✔ |
| **(e)** SUPERSEDED | 0 | — | Not used: this programme displaces nothing | ✔ |

**No decision carries zero dispositions; none carries more than one.** Census (M-2): **13 (b) + 3 (c) + 3 (d) = 19 dispositioned**, plus **2 held** = **21**.

## 4. Every decision has authority — authority continuity

| Check | Required | Measured | Method | Result |
|---|---|---|---|---|
| Decisions with a `Constitutional Authority` field | 21 | 21 | M-2 | ✔ |
| Decisions with all 15 required record fields | 21 | 21 (verified per file: 4+4+5+2+5+1) | M-2 | ✔ **PASS** |
| Resolved decisions naming a located Owner resolved by `CMG-000001` XVII.2 concern lookup | 19 | 19 | M-2 | ✔ |
| Held matters recording that **no** located authority is competent, with the reservation cited | 2 | 2 (`GD-08` → XX.7/LII.3; `GD-21` → XVII.4/LVII.3/`ED-1`) | M-2 | ✔ |
| Decisions citing an **unrecognized** artifact as constitutional authority | **0** | 0 — `UCCEP-000000` is cited only as custodian of its own declaration (`GD-16`, with the distinction stated at `GD-16-C5`); `UCIC-001` is **expressly refused** as authority at `GD-15` under `CMG-L-01` | M-2 | ✔ |
| Decisions asserting new law | **0** | 0 — every resolved decision is a recognition, a rejection on cited grounds, or a registration of work (Output 0 §2) | M-2 | ✔ |
| Decisions claiming a standing above PROVISIONAL | **0** | 0 — all 9 outputs carry the `CMG-L-12` / Tier T1 VACANT disclosure and the **C-3** / **K-09** citation | M-2 | ✔ |

### 4.1 Distinct owners exercised

Nine located instruments and one path-based concern were cited as governing authority; **none** was created, amended, or promoted:

`GOV-INT-001` (`CMG-DLG-16`) · `REG-AUTO-001` (`CMG-DLG-13`) · `CMG-000001` (Articles XV, XVII, XX, LII, LVII, LXXVI) · `CEP-002` (Articles 8, 10, 11, 18, 24, 25, 27, 28) · `CEP-003` (`CMG-DLG-03`) · `CEP-007` (`CMG-DLG-07`) · `CEP-009` (`CMG-DLG-09`) · `UCI-001` (`CMG-DLG-15`) · `CEP-001` XX / `CEP-008` (`CMG-DLG-08`) · `CMG-DLG-37` / `CMG-DLG-40` (path-based concerns, cited as loci).

## 5. Gate invariance — the Implementation Evidence Gate is unchanged

The most consequential verification: recording 21 matters must not close the Gate and halt the programme (`CEP-002` 28.18).

| Check | Measured | Method | Result |
|---|---|---|---|
| Is the gate **input** `00-MASTER/UCDA-000001/ucda-decisions.json` modified by this programme? | **NO** — `git status --porcelain` on that path returns empty | M-1 | ✔ |
| Decision population in that input | **64** decisions | M-2 | unchanged |
| Disposition set in that input | `DP-1 … DP-5` (closed by `CEP-002` 28.13) | M-2 | unchanged |
| Work packages in that input | `WP-UCDA-001 … WP-UCDA-007` | M-2 | unchanged |
| Any `GD-`/`DDI-`/`WP-GDR-` entry written into that input | **0** | M-2 | ✔ none |
| Recorded gate verdict of the located check `CK-DECISION-EVIDENCE` | `UCDA-000001: ASSIMILATED \| decisions=64 \| undispositioned=0 \| conversation_only=0 \| evidence=205 \| gate=OPEN \| seal=8d34d196a80a05b8` | M-3 | **OPEN** |
| Was `ucda_engine.py` or `uccep_engine.py` run by this programme? | **NO** | M-1 | ✔ |
| Was any seal recomputed by this programme? | **NO** | M-1 | ✔ |

**Why the Gate cannot be closed by this register**, restated compactly with its chain:

1. The Gate is computed mechanically from `ucda-decisions.json` (`CEP-002` 28.19: *"the Gate's executable expression IS a check bound in the located aggregate gate declaration"*). That input is unmodified, so the computed verdict is unchanged.
2. The 19 resolved decisions are **recorded determinations awaiting registration**, and each is constructed so that when registered it carries exactly one disposition with resolving evidence — so registration cannot introduce an undispositioned decision either (Output 8 §4).
3. The 2 held matters carry **no** 28.13 disposition and are excluded from registration by `GD-08-C4` / `GD-21-C4`. Per 28.16 a matter in the Deferral Register is not a disposition — and, not having reached 28.8's CONSTITUTIONAL AGREEMENT stage, is not a *decision* and so cannot be an undispositioned one (Output 7 §4).

**Verdict: Gate remains OPEN. `M-1A` is not barred by this programme.**

### 5.1 What the held matters *do* constrain, recorded honestly

`CMG-000001` LII.6 — an undispositioned **finding** blocks certification under Article LXXX. `DG-6` (via `DEF-01`) and `UCCEP-F-004` (via `DEF-02`) are such findings, so both constrain any certification claim above `CERTIFIED-PROVISIONAL` — already the corpus's recorded ceiling. Separately, **C-2** bars any certification claim until `OA-2` is discharged (`GD-16`). None of these blocks a consolidation step.

## 6. Boundary and append-only compliance

| Boundary | Requirement | Measured | Method | Result |
|---|---|---|---|---|
| **X-1** | `00-SOURCE/`, `00-SOURCE-MANIFEST/`, `99-FREEZE/` FROZEN | untouched | M-1 | ✔ |
| **X-2** | `00-CEP/` protected | untouched | M-1 | ✔ |
| **X-3** | `00-CMG/` protected | untouched | M-1 | ✔ |
| **X-4** | `id-ledger.json` protected | untouched; no identity allocated | M-1 | ✔ |
| **X-5** | `00-BOOK/DATA/*` append-only | untouched | M-1 | ✔ |
| **X-6/X-7/X-8** | FROZEN and certified code baselines, `engine/**`, `platform/**` | untouched | M-1 | ✔ |
| **X-9** | **No cross-programme edits** | **No file under any other programme's directory was written by this programme.** See §6.1 for a measured condition that must not be mistaken for a breach | M-1 | ✔ |
| **X-10** | the certified execution model | untouched | M-1 | ✔ |
| **P-5** | programme-owned outputs under `00-MASTER/<PROGRAMME-ID>/` | all 11 outputs under `00-MASTER/UCCEP-000008/` | M-1 | ✔ |
| **K-07** | `WP-UCCEP-001…005` closed to addition | no addition; `WP-GDR-*` is prefix-distinct | M-2 | ✔ |
| **K-09 / C-3** | provisional disclosure on every artifact | present in all outputs | M-2 | ✔ |
| `GD-13` | no deletion, no overwrite, no renumbering, no history rewrite | 0 files deleted; 0 renamed; HEAD unchanged at `9de85ad`; OA-1 anchor `1c6e750e…` **IS an ancestor of HEAD** | M-1 | ✔ |

### 6.1 Measured condition: generated-artifact churn not attributable to this programme

Recorded because it would otherwise appear to contradict §6's **X-9** row, and because the mission preamble described the repository as CLEAN.

**Measured (M-1):** the working tree is **not** clean. 28 tracked files are modified:

| Zone | Files | Character |
|---|---|---|
| `00-MASTER/UCCEP-000000/` | 20 — outputs `00`…`18` plus `uccep.json` | all **generated** artifacts of `uccep_engine.py` |
| `00-MASTER/UCDA-000001/` | 8 — outputs `00`…`06` plus `ucda.json` | all **generated** artifacts of `ucda_engine.py` |

**Attribution.** These are not edits by this programme. They are re-derivations produced when the session-start hooks executed the two engines' own `--gate` entry points. The diffs are consistent with that and with nothing else:

- `uccep.json`: standard-tier checks flipped `PASS → NOT-EXECUTED` with reason *"tier standard above the selected tier boot"*, and `CK-CLOSURE-P3` dropped from `advisory_failures` — i.e. a **boot-tier** run replacing a full-tier run's record.
- `ucda.json`: `repository.head` re-recorded `1c6e750e… → 9de85ad…`, `working_tree` `CLEAN → DIRTY`, `dirty_entries` `0 → 29` — the engine recording the tree state it observed, which by then included its own siblings' churn.
- `ucda.json` `seal_sha256` is **unchanged** (`8d34d196a80a05b8…`) and `undispositioned` remains `[]` — the substantive verdict did not move.

**Disposition of this condition:** none by this programme. Each file belongs to another programme and is regenerated by that programme's own generator under `GD-03`; **X-9** forbids this programme from editing or reverting them, and `GD-04`/`GD-03-C1` forbid hand-editing generated artifacts in any case. The condition is recorded here and carried to `10-REMAINING-GOVERNANCE-GAPS.md` for its owners.

**Also recorded (M-1):** `00-MASTER/UCCEP-000007/` (18 outputs) is **untracked** — the prior mission's outputs were never committed. That is `UCCEP-000007`'s matter, not this programme's, and is likewise carried forward.

### 6.2 Files written by this programme — the complete set

**Measured (M-1):** 11 files, all untracked additions under one directory, zero modifications to any pre-existing file.

| # | File | Content |
|---|---|---|
| 0 | `00-GOVERNANCE-DECISION-INDEX.md` | index, authority model, family map |
| 1 | `01-GDR-A-EXECUTION-OWNERSHIP-AND-GENERATOR-ARCHITECTURE.md` | `GD-01` … `GD-04` |
| 2 | `02-GDR-B-OWNERSHIP-ALLOCATION-AND-CONSOLIDATION-MAPPING.md` | `GD-05` … `GD-08` |
| 3 | `03-GDR-C-PRESERVATION-AND-NON-PROLIFERATION-POLICY.md` | `GD-09` … `GD-13` |
| 4 | `04-GDR-D-SEQUENCING-AND-ORDERING.md` | `GD-14`, `GD-15` |
| 5 | `05-GDR-E-REGISTER-EVIDENCE-AND-LINEAGE-REALIZATION.md` | `GD-16` … `GD-20` |
| 6 | `06-GDR-F-CONSTITUTIONAL-VACANCY.md` | `GD-21` |
| 7 | `07-DEFERRAL-ENTRIES.md` | `DEF-01`, `DEF-02` |
| 8 | `08-DISPOSITION-ROUTING-TABLE.md` | routing, `WP-GDR-001`, `WP-GDR-002` |
| 9 | `09-TRACEABILITY-VERIFICATION.md` | this output |
| 10 | `10-REMAINING-GOVERNANCE-GAPS.md` | remaining governance work |

## 7. Cross-reference integrity

| Check | Measured | Method | Result |
|---|---|---|---|
| Every `GD` referenced in Output 0 §4's map exists as a decision | 21/21 | M-2 | ✔ |
| Every `GD` in Output 8's routing table exists, and the two held matters are **absent** from it | 19 routed, `GD-08`/`GD-21` absent | M-2 | ✔ |
| Every `DEF-nn` referenced by a decision exists in Output 7 | `DEF-01`, `DEF-02` | M-2 | ✔ |
| Every `WP-GDR-nnn` referenced by a decision is declared in Output 8 §5 | 2/2 | M-2 | ✔ |
| Every located identifier used is reproduced, never coined (`DDI-n`, `OBS-n`, `DG-n`, `DR-n`, `CMG-*`, `CEP-*`, `UCCEP-F-*`, `WP-UCCEP-*`, `OA-n`, `C-n`, `K-n`, `X-n`, `P-n`, `VAC-01`) | verified against `UCCEP-000007` Outputs 12–16 and the located instruments | M-2/M-3 | ✔ |
| Identifiers coined here are prefix-distinct from every located set | `GD-`, `GDR-`, `DEF-`, `WP-GDR-`, `GG-` | M-2 | ✔ |
| Forward references resolve | Outputs 9 and 10 exist | M-2 | ✔ |

## 8. Constitutional consistency

| Assertion the register makes about itself | Verification | Result |
|---|---|---|
| It is not a second decision register (`CEP-002` 28.3) | No decision originates here: all 19 route to located register 2 with a `source_register`, per Output 8 §2. `DEC-CDAF-06`'s registered rejection of a second register is undisturbed | ✔ |
| It is not a registry; it allocates no identity | `id-ledger.json` untouched; `00-MASTER/` outside registration scope | ✔ |
| It creates no new generator, gate, pipeline or store | 0 files written outside `00-MASTER/UCCEP-000008/`; no executable, schema, or `config.py` change | ✔ |
| It amends no constitution | `00-CEP/**`, `00-CMG/**`, `00-BOOK/CONTROL-TOWER/**` untouched | ✔ |
| It declares no freeze and exercises no supersession | 0 freeze declarations; FROZEN population unchanged; 0 `SUPERSEDED` transitions | ✔ |
| It deletes nothing | 0 deletions; anchor is an ancestor of HEAD | ✔ |
| It occupies no tier and claims no standing above PROVISIONAL | disclosure present in all 11 outputs | ✔ |
| It satisfies the `CMG-000001` LXXVI.2(a) discovery condition it adopts at `GD-11` | Discovery is `UCCEP-000007` Output 16 §1 (exhaustive search, 0 hits), cited at Output 0 §7 and `GD-11` | ✔ |
| Its own identifier is grounded, not assumed | `GD-18` (forward-only from `UCCEP-000007`) | ✔ |

## 9. Verification summary

| # | Validation required by the mission | Result |
|---|---|---|
| 1 | Every DDI is RESOLVED or explicitly deferred with constitutional justification | **PASS** — 19 resolved, 2 deferred with cited justification |
| 2 | No DDI disappears | **PASS** — bijection, 21 ↔ 21 |
| 3 | No decision lacks authority | **PASS** — 19 name a located Owner; 2 record the absence of one, with the reservation cited |
| 4 | No decision lacks repository traceability | **PASS** — 102 literal citations resolve; 0 unresolved defects; 2 declared-absent citations are the subjects of `GD-18`/`GD-19` |
| 5 | Append-only evolution | **PASS** — 0 deletions, 0 renames, 0 renumbering; one correction recorded at §2.1 |
| 6 | No duplicated governance | **PASS** — 0 restated Owner clauses as operative text; 0 second registers; 0 second orderings; 0 second owners |
| 7 | No changed completed decisions | **PASS** — `GD-01` … `GD-21` unchanged since recording |
| 8 | Numbering continuity | **PASS** — contiguous, unique, forward-only |
| 9 | Cross-reference integrity | **PASS** — §7 |
| 10 | Constitutional consistency | **PASS** — §8 |
| 11 | Gate invariance | **PASS** — input unmodified; verdict OPEN; `M-1A` not barred |

**Two conditions recorded, neither a defect of this programme:** the generated-artifact churn of §6.1 (owners: `UCCEP-000000`, `UCDA-000001`) and the uncommitted state of `00-MASTER/UCCEP-000007/` (owner: `UCCEP-000007`). Both carried to Output 10.

---

*`UCCEP-000008` Output 9. Verifies; decides nothing, amends no decision, and repairs nothing. Every figure is a measured result at HEAD `9de85ad` under the four admissible methods. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12`.*
