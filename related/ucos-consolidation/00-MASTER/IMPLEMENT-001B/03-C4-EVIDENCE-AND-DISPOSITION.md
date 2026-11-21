# IMPLEMENT-001B · DELIVERABLE 03 — C-4 EVIDENCE & DISPOSITION

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001B` |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| FINDING | **C-4** — *"five unresolvable identifiers under a colliding programme label"* (`IMPLEMENT-001A` D00 §5.4), classified **HIGH** |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DETERMINATION

> ### C-4 is **substantially INVALID**. Its counts are wrong, its cited authority does not
> ### reach the subject matter, and the practice it condemns is **already committed at HEAD**.
>
> A narrower residue survives — but it is **not** the finding C-4 describes, and it merges into
> **C-1d** (the missing P-7 work package).

---

## 2. PHASE 1 — EVIDENCE RECONSTRUCTION

### 2.1 ⛔ The counts in C-4 are wrong

C-4 reported *"Eight added lines … five unresolvable identifiers"* and tabulated 5 ids. Measured:

```
grep -rn "EIP-018" --include=*.py --include=*.sh --include=*.yml --include=*.toml .
```

| # | Location | Id | Context | New? |
|---|---|---|---|---|
| 1 | `.github/workflows/uccep-gate.yml:84` | **FP-2** | `#` comment | added |
| 2 | `.github/workflows/uccep-gate.yml:105` | **FP-3** | `#` comment (`EIP-018 / FP-3` — different separator) | added |
| 3 | `.github/workflows/ec1-ci.yml:56` | **FP-7** | `#` comment | added |
| 4 | `.github/workflows/ec1-ci.yml:102` | **FP-8** | `#` comment | added |
| 5 | `platform/repository_operations/stages.py:124` | **FP-13** | `#` comment | added |
| 6 | `platform/repository_operations/stages.py:250` | **FP-14** | `#` comment | added |
| 7 | `platform/tests/test_repository_operations_stages.py:81` | **FP-13** | docstring | added |
| 8 | `platform/tests/test_repository_operations_stages.py:167` | **FP-14** | docstring | added |

**8 lines, 6 distinct ids** — `FP-2, FP-3, FP-7, FP-8, FP-13, FP-14`.

C-4's table lists 5 and omits **FP-3**, because its grep pattern `EIP-018 \(FP-` does not match
the `EIP-018 / FP-3` form at `uccep-gate.yml:105`. C-4 is therefore **internally inconsistent**:
it asserts 8 lines while enumerating 5 ids that account for only 7 of them.

### 2.2 ⛔ `EIP-018` is not unresolvable — it resolves to a live mission

C-4 stated the ids *"resolve to nothing"* and that `EIP-018` *"already denotes a different,
unrelated mission … `00-MASTER/EIP-018D/`"*. Both halves are inaccurate.

| Location | Fact |
|---|---|
| `00-MASTER/UCOS-USIS-001/00-USIS-PROGRAM-ESTABLISHMENT-DETERMINATION.md:7` | `MISSION \| EIP-018 — establish USIS as the constitutional substrate for all science and intelligence` |
| `00-MASTER/UCOS-USIS-001/13-…-COMPLETION-AND-REFINEMENT-REPORT.md:7` | `MISSION \| EIP-018 — Pre-Wave-0 Constitutional Refinement` |
| `00-MASTER/EIP-018D/` | A **third**, distinct derived-determination set (Wave-0 preconditions), `AUTHORITY = NONE` |

`EIP-018` **does** resolve — to the USIS establishment mission. And the collision C-4 names
(`EIP-018` vs `EIP-018D`) is not the collision that exists; `EIP-018D` is a legitimately distinct
suffixed id.

Further, **`00-BOOK/tools/config.py` already cites `EIP-018` for USIS in committed code**:

```
config.py:69   # --- Appended by Wave 0 (UCOS-USIS-001 / EIP-018 — authorized; Phase 0.3).
config.py:265  # --- Universal Science & Intelligence Substrate (USIS / PHASE-EIP-018) —
config.py:787  # Universal Science & Intelligence Substrate (USIS / EIP-018) is founded
```

All three pre-date the change set (outside its diff hunks).

> **The actual defect is token REUSE, not non-resolution:** one token now denotes two unrelated
> subject matters — the USIS establishment mission, and a set of stabilization findings. That is
> a real naming-hygiene problem. It is not what C-4 reported.

### 2.3 The `FP-N` register does not exist

`grep -rn "FP-13\|FP-14\|FP-2\b\|FP-3\b"` for a *definition*: the only `FP-N` register in the
corpus is `14-SECURITY/SECURITY-003-UNIVERSAL-SECURITY-ONTOLOGY.md:99-104` — unrelated
foundational properties (`FP-7` = *"Assurance, Not Enforcement"*, `FP-8` = *"Determinism"*).

**No `FP-1…FP-14` finding register exists.** This sub-claim of C-4 is **VALID**.

### 2.4 Nothing was minted

Every one of the 8 occurrences is a `#` comment or a test docstring. Checked each context.

| Registry | `EIP-018` present? |
|---|---|
| `00-BOOK/DATA/id-ledger.json` | **NO** |
| `00-BOOK/DATA/artifacts.json` | **NO** |
| any `.json` declaration, manifest, or register | **NO** |

**No identifier was allocated. No ledger entry was created. No registry field was written.**

---

## 3. PHASE 2 — CONSTITUTIONAL REVIEW

### 3.1 ⛔ `AC-4` does not reach code comments

`00-MASTER/IMR-001/01-OPERATOR-AUTHORIZATION-DECISION.md:55`, the **entire** text of AC-4:

```
- **AC-4** — No parallel identifier system.
```

One unelaborated clause in a bullet list. Its content comes from the instruments it inherits,
and every one of them makes the operative act **allocation**, not reference:

| Instrument | Verbatim |
|---|---|
| `00-MASTER/IMR-003A-R1/10-NAMESPACE-RECONCILIATION.md:37` (quoting `IMR-003A` AC-3) | *"No parallel identifier system. **All identity is minted by the located identity authority.**"* |
| `00-MASTER/IMR-0000/05-CIOS-IDENTITY-FRAMEWORK.md:25` | *"`GOV-001` Part 10 \| governance \| the prohibition on a parallel identifier system"* |
| `00-MASTER/IMR-003A-R1/07-REGISTRY-MATRIX.md:203` | frames the violation as *"**allocated** an `id-ledger` identifier \| parallel identifier system"* |

Decisively, `00-MASTER/IMR-0000/06-CIOS-NAMESPACE-FRAMEWORK.md` §1 establishes three namespace
tiers and rules `NF-1`…`NF-4`:

| Rule | Verbatim |
|---|---|
| **NF-1** | *"A T-P or T-M identifier is **a slot in a declaration, never an allocated identity**. It may **never** be presented to `REG-AUTO-001` or entered in `id-ledger.json`."* |
| **NF-3** | *"A T-M family is created by declaring it in a mission artifact and stating its cardinality. **It requires no admission, because it claims no identity.**"* |
| **NF-4** | *"No second subject token may be allocated for a subject matter that already has one."* |

Mission-local id families (`SS-*`, `UUP-*`, `RC-*`, `V-*`, `B-*`, `EB-*`, `C-*` …) are expressly
outside corpus identity and **require no admission**. A code comment is weaker still — it is not
even a declaration slot.

> **`AC-4` governs allocation into `id-ledger.json` / `REG-AUTO-001`. It does not govern
> comments.** C-4 applied it to a subject matter it does not reach.

The one clause with residual force is **NF-4** — and it bites in the *inverse* direction from
C-4's reading: not "a second token for one subject", but **one token for two subjects**.

### 3.2 No instrument requires code comments to cite registered identifiers

| Instrument | Result |
|---|---|
| `REG-AUTO-001` `L6` (`:75`) | requires **determinations** to cite registration evidence. Silent on code. |
| `UCIC-001` | `grep -icE "comment\|citation\|cite\|attribut"` → **0** |
| `02-MASTER/UCOS-GOV-002-…-TRACEABILITY-DETERMINATION.md:64` | treats comment-borne ids as **evidence to harvest**: *"`git grep -oE` over `engine/`, `platform/` … located explicit cross-references (constitutional IDs, EPIC IDs, program IDs, and file-path citations) **as evidence of trace links**"* — and `RA5` (`:245`) makes **preserving** them a standing obligation |

> The corpus treats comment-borne identifiers as a traceability **asset**, not a regulated
> namespace. `GOV-002` would have the change set's citations *harvested*, not deleted.

### 3.3 ⛔ The practice is already committed at HEAD — precedent is dispositive

Comment-cited identifiers in **already-committed** files:

| File:line | Cited id | Resolves? |
|---|---|---|
| `verify.sh:87` | `CD-01` / `CD-04` | ✓ `02-MASTER/UCOS-Ω∞-TECHNOLOGY-CONSTITUTION.md:272` |
| `verify.sh:93` | `CD-02` | ✓ `…TECHNOLOGY-CONSTITUTION.md:277` — *"CD-02 — Tested Before Merge"* |
| **`verify.sh:109`** | **`CRAP-001`** | ⛔ **NO.** Its only other occurrence in the repository is a *citation* at `OAA-001:44`. No programme directory, no declaration, no register. |
| `.github/workflows/ec1-ci.yml:2` | `DP-03`, `CD-01/CD-04`, `CD-02`, `DE-01` | mixed |
| `.github/workflows/ucos-registration-gate.yml:42,:47` | `B-01c` | comment-only |
| `pyproject.toml:2,:3,:153` | `DE-04`, `TP-04`, `TP-05`, `CD-01`, `CD-04` | mixed |
| `engine/acceptance/gates.py:124`, `engine/context/catalog.py:138`, `engine/determinism/hermetic.py:29` | `DE-04`, `TP-04/TP-05` | comment-only |

> **`verify.sh:109` — the repository's own canonical verification entry point, committed at
> `df763bf9` — cites `CRAP-001`, which resolves to nothing.**
>
> If C-4 were a valid blocking breach of `AC-4`, then `UCOS-BASELINE-001` was already in breach
> when it was certified. A rule that convicts the certified baseline is not the rule.

*(Correction of record: an intermediate analysis in this mission reported `CD-02` as
unresolvable. It resolves — `TECHNOLOGY-CONSTITUTION.md:277`. Only `CRAP-001` does not.)*

---

## 4. PHASE 3 — CLASSIFICATION

| Sub-claim | Classification |
|---|---|
| *"8 lines / 5 unresolvable ids"* | **FALSE POSITIVE** — 8 lines / 6 ids; `FP-3` missed |
| *"`EIP-018` resolves to nothing"* | **FALSE POSITIVE** — resolves to the USIS establishment mission |
| *"colliding with `EIP-018D`"* | **FALSE POSITIVE** — `EIP-018D` is a validly distinct id |
| *"breaches `OAA-001` AC-4"* | **FALSE POSITIVE** — AC-4 governs allocation; `NF-1`/`NF-3` exempt non-identity slots; nothing minted |
| *"breaches `RELEASE-001` §2.1 traceability"* | **FALSE POSITIVE** — `GOV-002` §6/`RA5` treat code citations as traceability evidence to preserve |
| *the `FP-N` register does not exist* | **VALID** — **INCOMPLETE IMPLEMENTATION** |
| *one token, two subject matters* | **VALID (recast)** — **REPOSITORY DEFECT**, `NF-4` in spirit |

> ## Overall: **INVALID as reported** · a narrow **VALID** residue

---

## 5. PHASE 4 — DISPOSITION

> # **REJECT** as reported (HIGH / traceability breach / AC-4 violation)
> # **ACCEPT** a narrowed residue, **MERGED into C-1d**

| Dimension | Determination |
|---|---|
| **Evidence** | 8 lines / **6** ids enumerated with file:line · all 8 are `#` comments or docstrings · `id-ledger.json` and `artifacts.json` contain **0** `EIP-018` entries · `EIP-018` resolves to `UCOS-USIS-001/00:7` · `config.py:69,265,787` already cite it (committed) · `AC-4` full text is one clause · `NF-1`/`NF-3`/`NF-4` at `IMR-0000/06` · `GOV-002:64`/`RA5:245` · **`verify.sh:109` cites the unresolvable `CRAP-001` at HEAD** |
| **Constitutional justification** | `AC-4`'s located basis (`IMR-003A` AC-3, `GOV-001` Part 10, `NF-1`/`NF-3`) makes the prohibited act **allocation into the identity authority**. `NF-1` expressly permits declaration slots that are never presented to `REG-AUTO-001` or `id-ledger.json`; `NF-3` states such families *"require no admission, because they claim no identity."* Comments are a fortiori exempt. `GOV-002` affirmatively values them. And HEAD already contains the same pattern in `verify.sh`. |
| **Implementation impact** | **None required.** No code deletion, no comment removal — `GOV-002` `RA5` would make removal a *regression* in traceability evidence. |
| **Repository impact** | Two record-only acts, both merged into `C-1d`: (1) rename the finding-set token so it does not shadow the USIS mission (`NF-4`); (2) declare the `FP-1…FP-14` register in the work package that `P-7` requires anyway. |
| **Dependency impact** | None. |
| **Certification impact** | **NONE.** C-4 is removed from the blocking set. Its valid residue is not independently blocking — it is a component of `C-1d`, which is one work-package registration. |

### 5.1 Why the residue merges into C-1d rather than standing alone

`C-1d` established that the 7 `platform/**` writes are an `X-8` freeze-gated mutation whose
`P-7` conditions are met **except** *"only under an existing work package."*

The `FP-N` register and the token rename are exactly the content that work package must carry:
it must name the defective gates (`FP-13` acceptance-by-fiat, `FP-14` empty freeze subject,
`FP-2`/`FP-3` uccep-gate environment and tier, `FP-7`/`FP-8` CI fail-open), their owner, and the
negative-path evidence. **Registering that one work package discharges C-1d and C-4's entire
valid residue simultaneously.**

Two findings, one act. Tracked as `RB-02` in Deliverable 06.

---

## 6. SUMMARY

| Claim in `IMPLEMENT-001A` C-4 | Verdict |
|---|---|
| 8 added lines cite `EIP-018 (FP-N)` | ✓ **REPRODUCED** (8 lines) |
| **5** distinct ids | ⛔ **WRONG** — **6** (`FP-3` missed; C-4 internally inconsistent) |
| Ids resolve to nothing | ⚠ **PARTLY** — the `FP-N` **register** does not exist ✓; but `EIP-018` **does** resolve |
| `EIP-018` collides with the unrelated `EIP-018D` | ⛔ **WRONG** — `EIP-018D` is a distinct valid id; the real reuse is against `UCOS-USIS-001` |
| Breaches `OAA-001` **AC-4** | ⛔ **DISPROVED** — AC-4 governs allocation; nothing minted; `NF-1`/`NF-3` exempt |
| Breaches `RELEASE-001` §2.1 traceability | ⛔ **DISPROVED** — `GOV-002` treats code citations as evidence to **preserve** |
| *"Every substantive code change is unattributable to a located authority"* | ⚠ **TRUE, but this is `P-7`'s work-package condition** — recast as `C-1d`, not an identifier issue |
| Severity **HIGH** | ⛔ **DISPROVED** — HEAD's own `verify.sh:109` cites the unresolvable `CRAP-001` |

> **What survives C-4:** the `FP-N` register must be declared and the token renamed — both as
> content of the single work package `C-1d` already requires. **Zero independent findings.**

---

*END — `IMPLEMENT-001B` Deliverable 03 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
