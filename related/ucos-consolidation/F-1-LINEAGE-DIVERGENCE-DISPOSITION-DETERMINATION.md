# F-1 — Lineage Divergence Disposition Determination

| Field | Value |
|---|---|
| FINDING | `F-1` — conflicting `Parent` assertions (`SCOPE-B-WORKSTREAM-3-LINEAGE-DISCOVERY-DETERMINATION.md` §7) |
| MODE | **DISCOVERY AND DETERMINATION ONLY.** No implementation, no artifact mutation, no registry modification, no lineage projection created. |
| CONSTITUENT AUTHORITY | **NONE** |
| PRIOR BASELINE | `B-01` CERTIFIED · `B-02` CERTIFIED — both **unmodified** |

---

## 1. Finding Summary

Two of 1,234 `Parent` edges in `00-BOOK/DATA/relationships.json` assert an ancestry that
`00-BOOK/DATA/artifacts.json` does not declare. 1,232 agree.

**The divergence is real, and it is not residue.** It is produced by a **live rule** in the
current generator, reproduced here by executing that generator's own parser.

---

## 2. Affected Artifacts

| | Artifact A | Artifact B |
|---|---|---|
| Universal ID | `UCOS-EVOUSIS015-000002` | `UCOS-EVOUSIS016-000002` |
| Path | `EVO-USIS-015/02-REPOSITORY-STRUCTURE-REPORT.md` | `EVO-USIS-016/02-REPOSITORY-STRUCTURE-REPORT.md` |
| Type | `DOCUMENT_ARTIFACT` | `DOCUMENT_ARTIFACT` |
| UGA owner | `EVO-USIS-015` | `EVO-USIS-016` |
| Registry owner | `UCOS-PROGRAM-CUSTODIAN` | `UCOS-PROGRAM-CUSTODIAN` |
| Birth record | **none** — `EXCLUDED_DOCUMENT` class; holds repository-plane identity only | **none** — same |
| **Declared structural parent** | `UCOS-USIS-000001` | `UCOS-USIS-000001` |
| **Conflicting metadata parent** | `UCOS-USIS-000017` (*USIS-014 — Validation Architecture*) | `UCOS-USIS-000018` (*USIS-015 — Certification Architecture*) |
| Declared `dependencies` | `[]` | `[]` |
| Creation | `Created`, snapshot in `change-ledger.change_events`; version `1.0.0`, depth 1 | same |
| Producing instrument | `00-BOOK/tools/ukb.py` (`ukb build`) | same |
| Producing workflow | `register.sh` Phase 1 / `ukb build` → `00-BOOK/DATA/relationships.json` | same |
| Evidence references | `artifacts.json` record · `relationships.json` edges · `change-ledger` version record · `id-ledger` history | same |

**Exact edge comparison:**

```
UCOS-EVOUSIS015-000002 --Parent--> UCOS-USIS-000001   note=structural:program-root   [agrees with source]
UCOS-EVOUSIS015-000002 --Parent--> UCOS-USIS-000017   note=metadata:PARENT           [NOT declared by source]
UCOS-EVOUSIS016-000002 --Parent--> UCOS-USIS-000001   note=structural:program-root   [agrees with source]
UCOS-EVOUSIS016-000002 --Parent--> UCOS-USIS-000018   note=metadata:PARENT           [NOT declared by source]
```

Measured: `metadata:PARENT` occurs **exactly twice in 12,899 edges**. No `Depends-On` edge
exists from either artifact to its metadata target. `Parent`/`Child` remain exact inverses
across all 2,468 edges.

---

## 3. Relationship Analysis

**Determined from the source documents, not assumed.** Both artifacts declare, in a single
front-matter row headed **"Parent lineage"**:

> *EVO-USIS-015:* `` `Parent` = program root USIS-GOV-000 (non-chained); `Depends-On` USIS-014 (parent tier 20) + Wave-2 spine ``
> *EVO-USIS-016:* `` `Parent` = program root USIS-GOV-000 (non-chained, materialized to `UCOS-USIS-000001`); `Depends-On` USIS-015 (parent tier 21) + spine ``

The documents themselves say the target is **`Depends-On`**, and that `Parent` is the
program root — which is exactly what `artifacts.json` records.

### Verdict: **B — a different relationship type incorrectly labelled `Parent`.**

The true relation is `Depends-On`. Options A, C, D and E are refuted by evidence:

| Option | Refutation |
|---|---|
| A — a true structural parent | The document states the opposite: `Parent` = program root. |
| C — historical migration artifact | The rule is live in the current generator (§6), not inherited data. |
| D — obsolete projection residue | `ukb build` rebuilds `edges = []` from scratch — a **replace**, not a merge. Regeneration reproduces the edge. |
| E — intentional exception | No exception is declared anywhere; the emitting rule is generic and fires wherever the pattern occurs. |

---

## 4. Authority Determination

| Layer | Instrument | Standing |
|---|---|---|
| Ancestry source | `artifacts.json` `parent` | **SOURCE AUTHORITY** — declares `UCOS-USIS-000001`, and is correct |
| Ancestry projection | `relationships.json` | **DERIVED PROJECTION** — cannot override the source |
| Lineage law | `UCI-001 Part XVI.5` via `UCL-S-0350` | *"lineage and evolution are DERIVED projections over recorded history; no new store is created"* |

**DETERMINED: the authoritative interpretation is the source.** The parent of both artifacts
is `UCOS-USIS-000001`. The `metadata:PARENT` edges are **incorrect projections**, not a
competing ancestry claim, and they carry no authority to alter the source.

**No lineage authority duplication exists.** This is one authority with a defective
projection — not two authorities in conflict.

---

## 5. Ownership Determination

| Responsibility | Owner | Basis |
|---|---|---|
| **Source owner** | `UCOS-PROGRAM-CUSTODIAN` (registry record) · `EVO-USIS-015` / `EVO-USIS-016` (UGA object owner) | UGA `ownership_rules`; `artifacts.json.owner` |
| **Projection owner** | **`UCOS-UKB-TOOLING`** — `00-BOOK/tools/ukb.py`, `config.py`, both `TOOLING_OBJECT` | UGA ownership rule: *"the registration engine and its data home are one custodial unit"* |
| **Verification owner** | `UMB-IMP-001` / `ukb validate`; repository-scale gating by `./verify.sh` | `ukb.py:1832` parent referential-integrity check |
| Governing standard | `UMB-006` (knowledge graph) · `UMB-IMP-002` (cited in the dedup comment) | in-code citation |

**The correction belongs to `UCOS-UKB-TOOLING` and/or the two document owners — not to this
workstream, and not to Scope B.**

---

## 6. Root Cause Determination

Proven by executing the generator's own parser against the real cell.

**Two rules compose into the defect:**

1. **The label regex is unanchored.** `ukb.py:255`
   ```python
   re.search(r"\|\s*" + re.escape(label) + r"[^|\n]*\|\s*([^|\n]+?)\s*\|", head, re.IGNORECASE)
   ```
   For `label = "PARENT"`, the trailing `[^|\n]*` lets it match the **prose heading
   "Parent lineage"** — a narrative row, not a relationship-declaration row.

2. **The cell is harvested wholesale.** `parse_relationship_refs` returns every resolvable
   token in the captured cell. Executed on the actual text:
   ```
   parse_relationship_refs(cell) → ['USIS-GOV-000', 'USIS-014']
   ```
   Both are attributed to the `PARENT` label, because the row declares **two relations in
   one cell**.

3. **Dedup hides the correct half and leaves the wrong one.** `ukb.py:1027` drops
   `(uid, UCOS-USIS-000001, Parent)` as already structurally emitted — *"metadata never
   duplicates a structurally-emitted edge (UMB-IMP-002)"* — so the only surviving metadata
   edge is the incorrect one.

**ROOT CAUSE: a relationship-label regex that matches a prose heading, combined with a cell
that declares two relations, causes a `Depends-On` target to be emitted as a `Parent` edge.**

**Secondary finding (source incompleteness):** both artifacts declare `dependencies: []`
while their documents declare a `Depends-On`. The correct edge is therefore **missing**, not
merely mislabelled — the defect loses one true relation and invents one false one.

---

## 7. Correction Path Determination

Each option assessed against evidence; none is executed.

| # | Option | Verdict |
|---|---|---|
| 1 | Regenerate derived projection | **REJECTED — proven ineffective.** The rule is live and the build replaces wholesale; regeneration reproduces both edges. |
| 2 | Correct the source record | **PARTIALLY VALID.** `artifacts.json.parent` is already correct. What is incorrect is the *document cell*, which fuses two relations into one row. Splitting it into distinct `PARENT` and `DEPENDS-ON` rows fixes both instances **and** supplies the missing `Depends-On`. Both files are outside every frozen prefix. Scope: 2 documents. |
| 3 | Rename / reclassify the relationship type | **REJECTED.** The type vocabulary is correct; `Parent` and `Depends-On` both exist and are properly specified. |
| 4 | Add exception governance | **REJECTED.** Declaring an exception would ratify an edge the source contradicts, and would convert a defect into law. |
| 5 | Add a verification rule only | **INSUFFICIENT ALONE.** It would detect the divergence without removing it; the two false edges would persist as a governed known-bad. Necessary, but not sufficient. |
| 6 | Anchor the label regex in the generator | **VALID and SYSTEMIC.** Constraining the label match so a prose heading cannot satisfy a relationship label prevents recurrence for every future document. **Carries regression risk** across all 1,233 artifacts and 12,899 edges, and touches `00-BOOK/tools/` — CI-filtered from the frozen guard, but owned by `UCOS-UKB-TOOLING`. |

**RECOMMENDED DISPOSITION — not authorized here, and not selectable by this workstream:**

**Option 2 + Option 5 as the minimum correct pair, with Option 6 referred as the systemic
fix.** Option 2 removes both false edges and restores the missing true one at the source of
the ambiguity; Option 5 makes recurrence detectable; Option 6 makes recurrence impossible
but must be decided by the generator's owner because its blast radius is the whole graph.

---

## 8. Verification Gap

**Required protection: lineage projection consistency validation** — every `Parent` edge in
the projection must be backed by a declared `parent` in the source.

| Question | Determination |
|---|---|
| Where does it belong? | With the existing referential-integrity check at `ukb.py:1832`, which already validates that a parent **resolves**, but never that a projected edge is **backed**. |
| Who owns it? | `UCOS-UKB-TOOLING` (generator) with `UMB-IMP-001` as validation owner. |
| Does it extend existing verification? | **Yes — it is an extension, not a new mechanism.** The check sits beside an existing loop over the same data. |
| Does it require a new gate? | **No.** `ukb validate` is already a declared `verify.sh` stage. A new stage would be a second place to look for one subject. |
| New authority required? | **None.** |

**Why the gap existed:** `ukb validate` measures *existence* of the parent, never *agreement*
between source and projection. That is why F-1 survived 11,914 tests — the silence is the
proof of the gap, not an inference from it.

---

## 9. Evidence Requirements

Before F-1 may be closed, the following must exist:

| # | Evidence | Acceptance |
|---|---|---|
| E-1 | **Before state** | `metadata:PARENT` edge count = **2**; children with >1 parent edge = **2**; `dependencies` = `[]` on both |
| E-2 | **After state** | `metadata:PARENT` edges backed by a declared parent, or absent; children with >1 parent edge = **0** |
| E-3 | **Ownership proof** | The correction performed by, or authorized by, `UCOS-UKB-TOOLING` and/or the two document owners |
| E-4 | **Regeneration proof** | `ukb build` run twice ⇒ byte-identical `relationships.json`; the corrected state survives regeneration (this is what disproves Option 1) |
| E-5 | **Lineage consistency proof** | Every `Parent` edge backed by a declared `parent`: **1,234 / 1,234** |
| E-6 | **Verification proof** | The new consistency rule **fails on the pre-correction state** and passes after — a rule never shown to fail is not a rule |
| E-7 | **No-regression proof** | `./verify.sh --full` PASS; edge total and type histogram unchanged apart from the corrected edges |

---

## 10. Implementation Readiness

**READY FOR AUTHORIZATION — but not by Scope B, and not by this workstream.**

* **Interpretation is settled:** the authoritative parent of both artifacts is
  `UCOS-USIS-000001`. The two `metadata:PARENT` edges are defective projections.
* **Root cause is proven**, by executing the generator's own parser, not inferred.
* **Ownership is located:** `UCOS-UKB-TOOLING` (projection), the two programme owners
  (source documents), `UMB-IMP-001` (validation).
* **Correction requires no new authority, registry, lifecycle or evidence owner.**
* **Blocking condition:** the correction touches `00-BOOK/tools/` and/or two corpus
  documents, both outside Scope B's mandate. It must be authorized by their owners.

**Effect on Workstream 3:** the precondition recorded there stands. A Universal Lineage
Projection built before F-1 is corrected would inherit a two-answer ancestry for 2 of 1,233
artifacts and would either mask the conflict or propagate it.

---

# DISPOSITION COMPLETE
