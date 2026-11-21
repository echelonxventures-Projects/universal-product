# UCTX-001 UFI PROVENANCE FAILURE ROOT CAUSE ANALYSIS

**Date**: 2026-09-01  
**Producer**: UCOS-UCTX-001  
**Validator**: 00-BOOK/tools/ufi.py  
**Method**: Manual trace of UFI validation logic against generated surfaces

---

## METHODOLOGY

1. Read generated surfaces (.claude/CLAUDE.md, 00-BOOK/CONTEXT/00-CONTEXT-INDEX.md)
2. Identify table rows (lines starting with `|`)
3. Extract cells per UFI logic (split on `|`, strip, clean markdown)
4. Check each cell against:
   - `allowed_cells` in context-template-manifest.json
   - Declared authority corpus (context-authority.json, law.py, etc.)
5. Trace UFI rejection path in ufi.py lines 219-223

---

## UFI TABLE VALIDATION LOGIC (ufi.py:219-223)

```python
if s.startswith("|"):
    bad = [c.strip() for c in s.strip("|").split("|")
           if not cell_is_derived(c, corpus, allowed_cells, manifest["_lengths"])]
    if bad:
        return "UNPROVENANCED", "table cell(s): " + " ; ".join(bad[:3])
    return "OK", "derived table row"
```

**Cell validation** (ufi.py:184-190):
```python
def cell_is_derived(cell: str, corpus: set, allowed_cells: set, lengths: list) -> bool:
    c = CELL_CLEAN.sub("", cell).strip()
    if not c or c in allowed_cells or c in corpus:
        return True
    if len(c) >= MIN_SLOT and any(c in s for s in corpus):
        return True
    return len(c) > 40 and concatenation_of(c, corpus, lengths)
```

**Requirements for cell to pass**:
1. Empty after cleaning → PASS
2. Exact match in `allowed_cells` → PASS
3. Exact match in authority corpus → PASS
4. ≥6 chars AND substring of corpus entry → PASS
5. >40 chars AND tiles from corpus pieces → PASS

---

## SURFACE 1: .claude/CLAUDE.md

### TABLE 1: "Where each answer lives" (lines 20-37)

**Row example** (line 22):
```
| May an agent hold context of its own | UCOS-UCTX-001 | `00-BOOK/DATA/context-authority.json` |
```

**Cells extracted**:
1. `"May an agent hold context of its own"`
2. `"UCOS-UCTX-001"`
3. `"\`00-BOOK/DATA/context-authority.json\`"`

**Cell 1 validation**:
- In `allowed_cells`? NO
- In authority corpus? YES (from context-authority.json domains[].answers)
- Length ≥ MIN_SLOT (6)? YES (38 chars)
- Substring of corpus entry? YES (exact match in domains[].answers)
- **Result**: PASS (condition 4: substring match)

**Cell 2 validation**:
- In `allowed_cells`? NO
- In authority corpus? YES (from context-authority.json domains[].authority)
- Length ≥ MIN_SLOT? YES (14 chars)
- Substring of corpus entry? YES (exact match)
- **Result**: PASS (condition 4: substring match)

**Cell 3 validation**:
- In `allowed_cells`? NO
- Exact match in corpus? NO (corpus has `"00-BOOK/DATA/context-authority.json"` WITHOUT backticks)
- After CELL_CLEAN (removes backticks): `"00-BOOK/DATA/context-authority.json"`
- Now in corpus? YES
- **Result**: PASS (condition 3: exact match after cleaning)

**Conclusion**: This row should PASS. If it's failing, need actual UFI output to identify which cell.

---

### TABLE 2: "Mutation authorities" (lines 52-61)

**Row example** (line 54):
```
| Phase 8 — fixed-point verification | `00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py` | fixed point not proven |
```

**Cells extracted**:
1. `"Phase 8 — fixed-point verification"`
2. `"\`00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py\`"`
3. `"fixed point not proven"`

**Cell 1 validation**:
- In `allowed_cells`? NO
- In corpus? Check mutation-governance-boundary.json authorities[].authority
- Length ≥ 6? YES (36 chars)
- Substring of corpus? DEPENDS on whether mutation-governance-boundary.json is in true_input_set

**Reading context-authority.json true_input_set.inputs**:
```json
"inputs": [
  "00-BOOK/DATA/constitutional-authority-alignment.json",
  "00-BOOK/DATA/context-authority.json",
  "00-BOOK/DATA/exclusion-register.json",
  "00-BOOK/DATA/mutation-governance-boundary.json",
  "engine/uckp/law.py"
]
```

**Cell 1 check**: mutation-governance-boundary.json IS in input set, so its authority names are in corpus.

**Cell 2 validation**: Path with backticks, cleaned to bare path, should match corpus.

**Cell 3 validation**: "fixed point not proven" should be in mutation-governance-boundary.json authorities[].enforcement or similar field.

**Requires**: Read mutation-governance-boundary.json to verify corpus content.

---

### TABLE 3: "Excluded paths carry a declared class" (lines 67-75)

**Row example** (line 69):
```
| CACHE | Interpreter or tool cache. Reconstructible from source at any time; carries no information. |
```

**Cells extracted**:
1. `"CACHE"`
2. `"Interpreter or tool cache. Reconstructible from source at any time; carries no information."`

**Cell 1 validation**:
- In `allowed_cells`? NO
- In corpus? Check exclusion-register.json classes keys
- exclusion-register.json IS in true_input_set
- If "CACHE" is a key in classes object → in corpus
- **Result**: Should PASS (condition 3)

**Cell 2 validation**:
- In `allowed_cells`? NO
- In corpus? Should be value of classes["CACHE"]
- Length check: 96 chars
- **Result**: Should PASS (condition 3 or 4)

---

### TABLE 4: "Verification" (lines 81-86)

**Row example** (line 83):
```
| `./verify.sh --fast` | developer feedback: lint + impact-selected tests |
```

**Cells extracted**:
1. `"\`./verify.sh --fast\`"`
2. `"developer feedback: lint + impact-selected tests"`

**Cell 1 validation**:
- After cleaning: `"./verify.sh --fast"`
- In `allowed_cells`? YES (line 25 of manifest)
- **Result**: PASS (condition 2)

**Cell 2 validation**:
- In `allowed_cells`? YES (line 52 of manifest: "developer feedback: lint + impact-selected tests")
- **Result**: PASS (condition 2)

---

### TABLE 5: "Articles of the root law" (lines 92-113)

**Row example** (line 94):
```
| UCKP-ART-01 | Supremacy | Every constitutional entity shall exist exactly once as a canonical Universal Constitutional Knowledge Object. Every representation, execution environment and persistence mechanism of that entity is a view of it and holds no independent architectural authority. No architectural authority exists outside this principle. |
```

**Cells extracted**:
1. `"UCKP-ART-01"`
2. `"Supremacy"`
3. `"Every constitutional entity shall exist exactly once as a canonical Universal Constitutional Knowledge Object. Every representation, execution environment and persistence mechanism of that entity is a view of it and holds no independent architectural authority. No architectural authority exists outside this principle."`

**Cell 1 validation**:
- In `allowed_cells`? NO
- In corpus? Article IDs are extracted from engine/uckp/law.py via regex
- engine/uckp/law.py IS in true_input_set
- **Result**: Should PASS (condition 3)

**Cell 2 validation**:
- In `allowed_cells`? NO
- In corpus? Article titles from law.py
- **Result**: Should PASS (condition 3)

**Cell 3 validation**:
- In `allowed_cells`? NO
- In corpus? Article statements from law.py
- Length: 294 chars
- **Result**: Should PASS (condition 3 or 5: >40 chars tiling check)

---

## SURFACE 2: 00-BOOK/CONTEXT/00-CONTEXT-INDEX.md

### TABLE: "Authority roles and their cardinality" (lines 44-53)

**Row example** (line 46):
```
| DERIVED | no | MANY | an instrument that records or measures the standing of others and asserts nothing of its own |
```

**Cells extracted**:
1. `"DERIVED"`
2. `"no"`
3. `"MANY"`
4. `"an instrument that records or measures the standing of others and asserts nothing of its own"`

**Cell 1 validation**:
- In `allowed_cells`? NO
- In corpus? Role name from constitutional-authority-alignment.json authority_roles keys
- constitutional-authority-alignment.json IS in true_input_set
- **Result**: Should PASS (condition 3)

**Cell 2 validation**:
- In `allowed_cells`? YES (line 50: "no")
- **Result**: PASS (condition 2)

**Cell 3 validation**:
- In `allowed_cells`? NO
- In corpus? Cardinality value from authority_roles[].cardinality
- **Result**: Should PASS (condition 3)

**Cell 4 validation**:
- In `allowed_cells`? NO
- In corpus? Definition from authority_roles[].definition
- Length: 93 chars
- **Result**: Should PASS (condition 3 or 4)

---

### TABLE: "Context domains" (lines 59-76)

**Row example** (line 61):
```
| agent_policy | UCOS-UCTX-001 | `00-BOOK/DATA/context-authority.json` | SINGLE |
```

**Cells extracted**:
1. `"agent_policy"`
2. `"UCOS-UCTX-001"`
3. `"\`00-BOOK/DATA/context-authority.json\`"`
4. `"SINGLE"`

**Cell 1 validation**:
- In `allowed_cells`? NO
- In corpus? Domain name from context-authority.json domains[].domain
- **Result**: Should PASS (condition 3)

**Cell 2 validation**:
- In `allowed_cells`? NO
- In corpus? Authority name from domains[].authority
- **Result**: Should PASS (condition 3)

**Cell 3 validation**:
- After cleaning: `"00-BOOK/DATA/context-authority.json"`
- In corpus? From domains[].authority_home
- **Result**: Should PASS (condition 3)

**Cell 4 validation**:
- In `allowed_cells`? NO
- In corpus? Cardinality value from domains[].cardinality
- **Result**: Should PASS (condition 3)

---

### TABLE: "Relationship to UCXI" (lines 86-89)

**Row example** (line 88):
```
| UCXI-000001 | In which reference frame does a context resolve, what kind of context is it, and how is a kind nobody has declared yet admitted? Its values are dimension VALUES describing the frame that surrounds an entity. |
```

**Cells extracted**:
1. `"UCXI-000001"`
2. Long text (206 chars)

**Cell 1 validation**:
- In `allowed_cells`? NO
- In corpus? From ucxi_relationship.sibling
- **Result**: Should PASS (condition 3)

**Cell 2 validation**:
- In `allowed_cells`? NO
- In corpus? From ucxi_relationship.QUESTION_ANSWERED_BY_UCXI
- Length: 206 chars
- **Result**: Should PASS (condition 3 or 5)

---

### TABLE: "Agent surfaces" (lines 97-103)

**Row example** (line 100):
```
| Claude | `.claude/CLAUDE.md` | Claude Code, claude.ai/code, Claude Agent SDK |
```

**Cells extracted**:
1. `"Claude"`
2. `"\`.claude/CLAUDE.md\`"`
3. `"Claude Code, claude.ai/code, Claude Agent SDK"`

**Cell 1 validation**:
- In `allowed_cells`? NO
- In corpus? From agent_surfaces[].agent
- **Result**: Should PASS (condition 3)

**Cell 2 validation**:
- After cleaning: `".claude/CLAUDE.md"`
- In corpus? From agent_surfaces[].surface
- **Result**: Should PASS (condition 3)

**Cell 3 validation**:
- In `allowed_cells`? NO
- In corpus? From agent_surfaces[].consumed_by
- **Result**: Should PASS (condition 3)

---

### TABLE: "Invariants" (lines 107-123)

**Row example** (line 109):
```
| INV-CTX-01 | EXACTLY_ONE_CANONICAL_CONTEXT_AUTHORITY | YES |
```

**Cells extracted**:
1. `"INV-CTX-01"`
2. `"EXACTLY_ONE_CANONICAL_CONTEXT_AUTHORITY"`
3. `"YES"`

**Cell 1 validation**:
- In `allowed_cells`? NO
- In corpus? From invariants[].id
- **Result**: Should PASS (condition 3)

**Cell 2 validation**:
- In `allowed_cells`? NO
- In corpus? From invariants[].name
- **Result**: Should PASS (condition 3)

**Cell 3 validation**:
- In `allowed_cells`? YES (line 50: "YES")
- **Result**: PASS (condition 2)

---

## HYPOTHESIS: NO ACTUAL FAILURES

Based on tracing UFI logic against generated content:

**Every table cell should PASS** because:
1. Header cells are in `allowed_cells` or short/structural
2. Data cells come from declared authorities in true_input_set
3. UFI corpus includes all strings from those authorities
4. Substring matching (condition 4) catches partial matches
5. Markdown cleaning removes backticks before checking

**If UFI is reporting 15 failures**, the cause must be:

1. **Corpus extraction incomplete**: UFI may not be extracting nested JSON values correctly
2. **Path mismatch**: Backtick cleaning may not work as expected
3. **Substring logic failure**: MIN_SLOT or substring check may reject valid cells
4. **Non-table failures**: The 15 failures may be prose lines, not table cells
5. **Corpus source mismatch**: Generator reads files not in true_input_set

---

## REQUIRED: ACTUAL UFI OUTPUT

**Cannot complete root cause analysis without seeing**:
- Which exact lines UFI flags as UNPROVENANCED
- Which exact cells within those lines fail
- The actual error messages UFI produces

**Next step**: Execute UFI and capture output, or provide existing execution log showing the 15 failures.

---

**Status**: INCOMPLETE  
**Blocker**: No UFI execution output available  
**Confidence**: MEDIUM (logic trace suggests no failures, contradicting stated 15 failures)
