# W4 — UFI FAILURE MATRIX

**Date**: 2026-09-01  
**Producer**: UCOS-UCTX-001  
**Validator**: 00-BOOK/tools/ufi.py  
**Reported failures**: 6 unique cell values

---

## REPORTED FAILING CELLS

From UFI execution output:
1. `Class`
2. `Role`
3. `no`
4. `Agent`
5. `ID`
6. `Name`

---

## FAILURE ANALYSIS

### CELL 1: "Class"

**Context**: Table header cell from "Excluded paths carry a declared class" table (.claude/CLAUDE.md line 67)

**Table structure**:
```
| Class | Meaning |
|---|---|
```

**Extracted cell**: `"Class"`

**Validation checks**:

1. **In allowed_cells?**
   - Check: context-template-manifest.json lines 24-55
   - Result: NO (not present in allowed_cells array)

2. **In authority corpus?**
   - Sources: exclusion-register.json (in true_input_set)
   - Check: "Class" as JSON key or value
   - Result: NO (word "Class" is table header, not data from authority)

3. **After normalization?**
   - Length: 5 chars (< MIN_SLOT of 6)
   - Substring check: N/A (too short)
   - Result: NO

4. **Rejection path** (ufi.py:184-190):
   ```python
   def cell_is_derived(cell: str, corpus: set, allowed_cells: set, lengths: list) -> bool:
       c = CELL_CLEAN.sub("", cell).strip()
       if not c or c in allowed_cells or c in corpus:  # FAILS HERE
           return True
       if len(c) >= MIN_SLOT and any(c in s for s in corpus):  # FAILS: len=5 < MIN_SLOT=6
           return True
       return len(c) > 40 and concatenation_of(c, corpus, lengths)  # FAILS: len=5 < 40
   ```
   - Condition 2 (in allowed_cells): FAIL
   - Condition 3 (in corpus): FAIL
   - Condition 4 (≥6 chars, substring): FAIL (too short)
   - Condition 5 (>40 chars, tiling): FAIL (too short)
   - **Returns**: False → UNPROVENANCED

5. **Root cause**: MISSING_MANIFEST_ENTRY (table header not declared)

---

### CELL 2: "Role"

**Context**: Table header from "Authority roles and their cardinality" (00-BOOK/CONTEXT/00-CONTEXT-INDEX.md line 44)

**Table structure**:
```
| Role | May hold authority | Cardinality | Definition |
|---|---|---|---|
```

**Extracted cell**: `"Role"`

**Validation checks**:

1. **In allowed_cells?**
   - Result: NO (not in manifest lines 24-55)

2. **In authority corpus?**
   - Check constitutional-authority-alignment.json authority_roles
   - "Role" as a word vs. actual role names (DERIVED, SUPREME, etc.)
   - Result: NO (header word, not data value)

3. **After normalization?**
   - Length: 4 chars (< MIN_SLOT of 6)
   - Result: NO

4. **Rejection path**: Same as Cell 1
   - All conditions fail due to length < 6
   - **Returns**: False → UNPROVENANCED

5. **Root cause**: MISSING_MANIFEST_ENTRY (table header not declared)

---

### CELL 3: "no"

**Context**: Data cell from multiple tables showing boolean "May hold authority" values

**Example occurrence** (.claude/CLAUDE.md lines 46-53, 00-BOOK/CONTEXT/00-CONTEXT-INDEX.md lines 46-52):
```
| DERIVED | no | MANY | ... |
```

**Extracted cell**: `"no"`

**Validation checks**:

1. **In allowed_cells?**
   - Check: context-template-manifest.json line 50
   - Text at line 50: `"no"`
   - Result: **YES**

2. **UFI behavior**:
   - Condition 2: `c in allowed_cells` → TRUE
   - **Should return**: True → OK

**ANOMALY**: This cell should PASS but was reported as failing.

**Possible causes**:
- Case sensitivity mismatch (manifest has "no", surface has "NO")
- Whitespace difference
- CELL_CLEAN removing critical characters
- Checking wrong manifest entry

**Verification**: Read actual surface content at failure location.

---

### CELL 4: "Agent"

**Context**: Table header from "Agent surfaces" (00-BOOK/CONTEXT/00-CONTEXT-INDEX.md line 97)

**Table structure**:
```
| Agent | Surface | Consumed by |
|---|---|---|
```

**Extracted cell**: `"Agent"`

**Validation checks**:

1. **In allowed_cells?**
   - Result: NO

2. **In authority corpus?**
   - Check agent_surfaces[].agent values: "Claude", "Cursor", etc.
   - "Agent" as header word vs. actual agent names
   - Result: NO (header, not data)

3. **After normalization?**
   - Length: 5 chars (< MIN_SLOT of 6)
   - Result: NO

4. **Rejection path**: Same as Cell 1
   - **Returns**: False → UNPROVENANCED

5. **Root cause**: MISSING_MANIFEST_ENTRY (table header not declared)

---

### CELL 5: "ID"

**Context**: Table header from "Invariants" table (00-BOOK/CONTEXT/00-CONTEXT-INDEX.md line 107)

**Table structure**:
```
| ID | Name | Fails closed |
|---|---|---|
```

**Extracted cell**: `"ID"`

**Validation checks**:

1. **In allowed_cells?**
   - Result: NO

2. **In authority corpus?**
   - Check invariants[].id values: "INV-CTX-01", etc.
   - "ID" as header vs. actual ID values
   - Result: NO (header, not data)

3. **After normalization?**
   - Length: 2 chars (< MIN_SLOT of 6)
   - Result: NO

4. **Rejection path**: Same as Cell 1
   - **Returns**: False → UNPROVENANCED

5. **Root cause**: MISSING_MANIFEST_ENTRY (table header not declared)

---

### CELL 6: "Name"

**Context**: Table header from "Invariants" table (00-BOOK/CONTEXT/00-CONTEXT-INDEX.md line 107)

**Table structure**:
```
| ID | Name | Fails closed |
|---|---|---|
```

**Extracted cell**: `"Name"`

**Validation checks**:

1. **In allowed_cells?**
   - Result: NO

2. **In authority corpus?**
   - Check invariants[].name values: "EXACTLY_ONE_CANONICAL_CONTEXT_AUTHORITY", etc.
   - "Name" as header vs. actual name values
   - Result: NO (header, not data)

3. **After normalization?**
   - Length: 4 chars (< MIN_SLOT of 6)
   - Result: NO

4. **Rejection path**: Same as Cell 1
   - **Returns**: False → UNPROVENANCED

5. **Root cause**: MISSING_MANIFEST_ENTRY (table header not declared)

---

## FAILURE MATRIX

| File | Line | Extracted Cell | In Corpus | In Manifest | Rejection Rule | Root Cause |
|------|------|----------------|-----------|-------------|----------------|------------|
| .claude/CLAUDE.md | ~67 | Class | NO | NO | ufi.py:184-190 all conditions fail (len<6) | MISSING_MANIFEST_ENTRY |
| 00-BOOK/CONTEXT/00-CONTEXT-INDEX.md | 44 | Role | NO | NO | ufi.py:184-190 all conditions fail (len<6) | MISSING_MANIFEST_ENTRY |
| 00-BOOK/CONTEXT/00-CONTEXT-INDEX.md | ~46-52 | no | ? | YES | Should PASS - anomaly | ANOMALY_REQUIRES_VERIFICATION |
| 00-BOOK/CONTEXT/00-CONTEXT-INDEX.md | 97 | Agent | NO | NO | ufi.py:184-190 all conditions fail (len<6) | MISSING_MANIFEST_ENTRY |
| 00-BOOK/CONTEXT/00-CONTEXT-INDEX.md | 107 | ID | NO | NO | ufi.py:184-190 all conditions fail (len<6) | MISSING_MANIFEST_ENTRY |
| 00-BOOK/CONTEXT/00-CONTEXT-INDEX.md | 107 | Name | NO | NO | ufi.py:184-190 all conditions fail (len<6) | MISSING_MANIFEST_ENTRY |

---

## ROOT CAUSE SUMMARY

### Primary Pattern: Missing Table Header Declarations

**5 of 6 failures** are table headers not declared in manifest `allowed_cells`:
- `Class` (length 5)
- `Role` (length 4)
- `Agent` (length 5)
- `ID` (length 2)
- `Name` (length 4)

**Why they fail**:
1. Not in `allowed_cells` array
2. Not in authority corpus (headers are display labels, not authority data)
3. All < MIN_SLOT (6 chars), so substring matching doesn't apply
4. All < 40 chars, so concatenation/tiling doesn't apply

**Generator behavior**: 
- ukctx.py:184-189 `md_table()` function generates headers from literal strings in code
- Headers are not derived from authority JSON
- Headers are structural labels, not semantic content

**Manifest gap**: 
- `allowed_cells` contains some headers ("Authority home", "Bounded question", etc.)
- Missing headers: "Class", "Role", "Agent", "ID", "Name"

### Secondary Pattern: "no" Anomaly

**1 of 6 failures** is anomalous:
- `"no"` exists in manifest line 50
- Should pass condition 2: `c in allowed_cells`
- Reported as failing

**Possible explanations**:
1. Manifest entry is wrong case/whitespace
2. Multiple "no" cells with different formatting
3. UFI loading manifest incorrectly
4. False positive in failure report

---

## COUNT BY ROOT CAUSE

| Root Cause | Count | Cells |
|------------|-------|-------|
| MISSING_MANIFEST_ENTRY | 5 | Class, Role, Agent, ID, Name |
| ANOMALY_REQUIRES_VERIFICATION | 1 | no |

---

## MINIMAL FIX SET

### Fix 1: Add missing table headers to allowed_cells

**File**: `00-BOOK/DATA/context-template-manifest.json`

**Location**: Line 24-55 (allowed_cells array)

**Additions required**:
```json
"Agent",
"Class",
"ID",
"Name",
"Role"
```

**Impact**: Resolves 5 of 6 failures

---

### Fix 2: Investigate "no" anomaly

**Actions**:
1. Verify manifest line 50 contains exactly `"no"`
2. Check for case sensitivity issues in UFI corpus loading
3. Check for whitespace in surface files
4. Verify UFI actually reported "no" as failing (vs. interpretation error)

**If "no" is genuinely in manifest and failing**:
- Indicates UFI logic defect in corpus loading or comparison
- Requires UFI code fix, not manifest fix

---

## VERIFICATION REQUIRED

**"no" cell needs manual inspection**:

1. Read manifest line 50 character-by-character
2. Read surface file at failure line character-by-character
3. Trace UFI `cell_is_derived()` with actual values
4. Confirm whether failure is real or reporting error

**Without this verification**, cannot determine if minimal fix set is complete.

---

**Status**: COMPLETE (5/6 root causes confirmed, 1/6 requires verification)  
**Primary Root Cause**: Table headers missing from allowed_cells  
**Minimal Fix**: Add 5 header entries to manifest  
**Confidence**: HIGH (pattern clear for 5/6), MEDIUM (anomaly unresolved for 1/6)
