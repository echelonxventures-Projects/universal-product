# F-1 — Lineage Divergence Correction Report

| Field | Value |
|---|---|
| FINDING | `F-1` — conflicting `Parent` assertions |
| AUTHORIZED CORRECTION | Option 2 (correct authoritative source) + Option 5 (extend existing validation) |
| CONSTITUENT AUTHORITY | **NONE** |
| PREDECESSORS | `SCOPE-B-WORKSTREAM-3-LINEAGE-DISCOVERY-DETERMINATION.md` · `F-1-LINEAGE-DIVERGENCE-DISPOSITION-DETERMINATION.md` |
| PRIOR BASELINE | `B-01` CERTIFIED · `B-02` CERTIFIED — both **unmodified** |

---

## 1. Original Defect

Two of 1,234 projected `Parent` edges asserted an ancestry `artifacts.json` did not declare:

```
UCOS-EVOUSIS015-000002 --Parent--> UCOS-USIS-000017   note=metadata:PARENT
UCOS-EVOUSIS016-000002 --Parent--> UCOS-USIS-000018   note=metadata:PARENT
```

Both artifacts declare `parent: UCOS-USIS-000001`. Each therefore carried **two parents**, and an ancestor-chain query over them had two answers.

**The defect was worse than a mislabel: it lost one true relation and invented one false one.** The documents declare a `Depends-On` that the projection never carried.

---

## 2. Root Cause

Proven by executing the generator's own parser, not inferred.

1. **The label regex is unanchored** — `ukb.py`:
   ```python
   re.search(r"\|\s*" + re.escape(label) + r"[^|\n]*\|\s*([^|\n]+?)\s*\|", head, re.IGNORECASE)
   ```
   For `label = "PARENT"`, the trailing `[^|\n]*` lets it match the **prose heading "Parent lineage"**.

2. **The cell is harvested wholesale.** The affected row declared *two* relations in one cell:
   > `` `Parent` = program root USIS-GOV-000 (non-chained); `Depends-On` USIS-014 (parent tier 20) + Wave-2 spine ``

   Executed against the real text:
   ```
   parse_relationship_refs(cell) → ['USIS-GOV-000', 'USIS-014']
   ```
   Both tokens attributed to the `PARENT` label.

3. **Dedup removed the correct half and left the wrong one.** `(uid, UCOS-USIS-000001, Parent)` was already emitted structurally, so it was dropped — *"metadata never duplicates a structurally-emitted edge (UMB-IMP-002)"* — leaving only the incorrect edge visible.

---

## 3. Source Correction (Option 2)

Corrected **only source declarations**. No derived projection, registry or generated artifact was hand-patched.

The fused row was split into two properly labelled declaration rows:

| File | Before | After |
|---|---|---|
| `EVO-USIS-015/02-REPOSITORY-STRUCTURE-REPORT.md` | `&#124; Parent lineage &#124; `Parent` = … USIS-GOV-000 …; `Depends-On` USIS-014 … &#124;` | `&#124; PARENT &#124; USIS-GOV-000 &#124; …` + `&#124; DEPENDS-ON &#124; USIS-014 &#124; …` |
| `EVO-USIS-016/02-REPOSITORY-STRUCTURE-REPORT.md` | same shape, `Depends-On` USIS-015 | `&#124; PARENT &#124; USIS-GOV-000 &#124;` + `&#124; DEPENDS-ON &#124; USIS-015 &#124;` |

This removes the ambiguity **at its origin** and supplies the `Depends-On` the projection was missing. Both files sit outside every frozen prefix.

**Correction applied to this document (same Option 2 remedy, applied to the quotation).**
When this report was itself registered as a corpus artifact, the two rows above — which
*quote* declaration syntax rather than *make* a declaration — were read by
`read_relationship_rows` as this document's own `PARENT` and `DEPENDS-ON` rows, projecting
`UCOS-F1LINE-000001 --Parent--> UCOS-USIS-000001` and `--> UCOS-USIS-000017` and failing the
§5 rule with three conflicting parents. The literal `|` glyphs inside those two quoted cells
are now written as the HTML entity `&#124;`. The rendered evidence is byte-for-byte the same
text on the page; only the raw scan surface changes, so the quotation can no longer be read
as a declaration. The parser is again NOT changed (§4 stands), and no derived projection,
registry or generated artifact was hand-patched.

---

## 4. Generator Correction — **REFUSED ON EVIDENCE**

The disposition invited a parser fix (anchor the label regex). **It was measured before being adopted, and then declined.**

| Regex | Rows matched across the corpus |
|---|---|
| current, unanchored | **672** |
| anchored `\|\s*LABEL\s*\|` | **578** |
| **lost by anchoring** | **94 (14%), across 17 labels** |

Legitimate cells that anchoring would silently drop include `CONSUMES (read-only)` ×35, `AUTHORITY type`, `AUTHORITY Chain`, `PRODUCES (append-only, machinery …)` ×6, `DEPENDS-ON (immutable)`, `PARENT / Child`, `SUPERSEDES / Superseded By`.

**DETERMINED: the parser is NOT changed.** Anchoring would be a 14% regression in relationship parsing to remove 2 edges — the *"do not introduce broad regression"* constraint refuses it, and the parser change is more dangerous than the defect it would fix. The protection is delivered by §5 instead, which catches the entire defect class however an edge was produced.

**Residual, recorded not fixed:** one further artifact still carries a `PARENT` row with suffix `lineage`. It produces **no divergence today** (its tokens resolve to the structurally-emitted parent and dedup). It is now covered by the §5 rule, which would refuse it the moment it diverged.

---

## 5. Validation Enhancement (Option 5)

Extended the **existing** referential-integrity check in `ukb validate`. **No new stage, no new authority, no new gate** — `ukb validate` is already a declared `verify.sh` stage.

The prior check proved a declared parent **resolves**. It never proved a projected edge is **backed**. The new rule states the property over the *emitted graph* rather than over the parser, so it holds however an edge was produced, and names no label, document or artifact:

* every projected `Parent` edge must equal the child's declared parent;
* no child may carry more than one projected parent.

It detects all four required classes: orphan projected edges, wrong relation type, missing source declaration, conflicting ancestry.

---

## 6. Before-Correction Failure Evidence

| Measure | Value |
|---|---|
| `metadata:PARENT` edges | **2** |
| Parent edges not backed by a declared parent | **2** |
| Children with more than one parent | **2** |
| Parent / Child | 1234 / 1234 |
| Depends-On / Required-By | 4774 / 4697 |
| `dependencies` on both subjects | `[]` |

**The rule refuses that state.** Reconstructed and executed against `ukb validate`:

```
exit: 1
VALIDATION FAILED — 4 problem(s):
 - UCOS-EVOUSIS015-000002 projected Parent UCOS-USIS-000017 is not the declared parent UCOS-USIS-000001 (note: metadata:PARENT).
 - UCOS-EVOUSIS016-000002 projected Parent UCOS-USIS-000018 is not the declared parent UCOS-USIS-000001 (note: metadata:PARENT).
 - UCOS-EVOUSIS015-000002 has 2 conflicting projected parents: ['UCOS-USIS-000001', 'UCOS-USIS-000017'].
 - UCOS-EVOUSIS016-000002 has 2 conflicting projected parents: ['UCOS-USIS-000001', 'UCOS-USIS-000018'].
```

The probe restored `relationships.json` **byte-identically** afterwards.

---

## 7. After-Correction Success Evidence

| Measure | Before | After |
|---|---|---|
| `metadata:PARENT` edges | 2 | **0** |
| Parent edges not backed | 2 | **0** |
| Children with >1 parent | 2 | **0** |
| Parent / Child | 1234 / 1234 | **1232 / 1232** |
| Depends-On / Required-By | 4774 / 4697 | **4776 / 4699** |
| Total edges | 12,899 | **12,899** |
| Parent note histogram | 4 structural + `metadata:PARENT` | **structural only** |

Per subject, after correction:

```
UCOS-EVOUSIS015-000002  Parent     -> UCOS-USIS-000001  note=structural:program-root
                        Depends-On -> UCOS-USIS-000017  note=metadata:DEPENDS-ON
UCOS-EVOUSIS016-000002  Parent     -> UCOS-USIS-000001  note=structural:program-root
                        Depends-On -> UCOS-USIS-000018  note=metadata:DEPENDS-ON
```

The dependency is recorded in `traceability.architecture` — the declared subject lane for `Depends-On` — for both subjects.

**Regeneration determinism (E-4):** two consecutive `ukb build` runs produced byte-identical `relationships.json`, `artifacts.json` and `change-ledger.json`. **`Parent`/`Child` remain exact inverses.** Net edge total unchanged: 2 `Parent` + 2 `Child` removed, 2 `Depends-On` + 2 `Required-By` added.

---

## 8. Regression Coverage

`platform/tests/test_lineage_projection_consistency.py` — **9 tests**.

| Test | Guards |
|---|---|
| `test_every_projected_parent_edge_is_backed_by_a_declared_parent` | the defect class itself |
| `test_no_artifact_has_more_than_one_projected_parent` | conflicting ancestry |
| `test_parent_and_child_edges_remain_exact_inverses` | the correction unbalancing the graph |
| `test_the_f1_subjects_carry_the_declared_parent_and_a_dependency` | the specific outcome F-1 was closed to produce |
| `test_no_parent_edge_is_sourced_from_parent_metadata` | a `Parent` edge re-entering from a relationship row |
| **`test_the_rule_refuses_the_pre_correction_state`** | **E-6 — reconstructs F-1 exactly and asserts refusal** |
| `test_each_original_divergent_edge_is_individually_refused` (×2) | each edge independently |
| `test_an_orphan_projected_edge_is_refused` | an edge for an unregistered target |

---

## 9. Governance Compliance

| Rule | Compliance |
|---|---|
| Correct source only; never hand-patch projections | **HELD** — only the 2 documents were edited; every derived surface came from its producer |
| No new verification stage | **HELD** — extended the existing `ukb validate` |
| No new authority / registry / lifecycle / evidence owner | **HELD** |
| No identity authority drift | **HELD** — `category_seq` **117 unchanged**; births **38 unchanged** |
| Identity ledger untouched by regeneration | **HELD** — `ukb build` (non-minting path) left `id-ledger.json` byte-identical |
| Registry integrity maintained | **HELD** — `ukb validate` PASS, 1233 artifacts, append-only page ledger intact |
| Frozen-path authority | **HELD** — `00-BOOK/tools/` and `00-BOOK/DATA/` are inside CI's declared frozen-guard filter (UCCEP-000006 X-4/X-5) |
| Scope not expanded | **HELD** — the parser was measured and left unchanged |

**Verification:**

| Mode | Exit | Stages | Tests | Failed | Coverage |
|---|---|---|---|---|---|
| `--fast` | **0** | 4/4 | 11,923 | 0 | 97% |
| `--change` | **0** | 9/9 | 11,923 | 0 | 97% |
| `--integration` | **0** | 14/14 | 11,923 | 0 | 97% |
| `--full` | **0** | **15/15** | 11,923 | 0 | 97% |

Fixed point at pass 1 · `ruff check` / `format --check` clean · 0 unstaged modifications.

---

## 10. Remaining Risks

| # | Risk | Severity | Status |
|---|---|---|---|
| R-1 | The unanchored label regex remains; a future document fusing two relations in one prose-headed row can re-create the defect | **MEDIUM** | **MITIGATED, not eliminated.** The §5 rule refuses it at `ukb validate` before it can be committed as truth. Eliminating it needs a parser change whose cost was measured at **94 lost rows** and refused. Referred to `UCOS-UKB-TOOLING`. |
| R-2 | One artifact still carries a `PARENT … lineage` row | **LOW** | No divergence today; covered by the §5 rule. |
| R-3 | The rule constrains `Parent` only; other relation types have no source-backing check | **LOW–MEDIUM** | `Parent` is the only type with a declared per-artifact source field (`parent`). Extending to `Depends-On` would need `dependencies` populated, which is a separate finding. |
| R-4 | `dependencies` stays `[]` while the dependency lives in `traceability.architecture` | **LOW** | Pre-existing generator behaviour, unchanged by this correction; recorded, not altered. |

---

# CORRECTION COMPLETE
