# UFI "no" CELL FAILURE ROOT CAUSE ANALYSIS

**Date**: 2026-09-01  
**Cell value**: `"no"`  
**Declared in manifest**: YES (context-template-manifest.json line 50)  
**Still failing after manifest fix**: YES

---

## CODE PATH TRACE

### 1. Entry Point: classify() function (ufi.py:209-228)

```python
def classify(line: str, manifest: dict, corpus: set) -> tuple:
    s = line.strip()
    if not s or STRUCTURAL.match(s):
        return "OK", "structural"
    allowed_lines = manifest["_allowed_lines"]
    allowed_cells = manifest["_allowed_cells"]
    if s in allowed_lines:
        return "OK", "declared template"
    if normalise(s, manifest["_corpus_sorted"]) in allowed_lines:
        return "OK", "declared template (normalised)"
    if s.startswith("|"):  # ← TABLE ROW PROCESSING
        bad = [c.strip() for c in s.strip("|").split("|")
               if not cell_is_derived(c, corpus, allowed_cells, manifest["_lengths"])]
        if bad:
            return "UNPROVENANCED", "table cell(s): " + " ; ".join(bad[:3])
        return "OK", "derived table row"
```

**Flow for table row**:
1. Line starts with `|` → table row detected
2. Extract cells: `s.strip("|").split("|")` 
3. For each cell: `c.strip()` then check `cell_is_derived()`
4. Collect failed cells into `bad` list
5. If `bad` not empty → return UNPROVENANCED with failing cells

---

### 2. Cell Validation: cell_is_derived() (ufi.py:184-190)

```python
def cell_is_derived(cell: str, corpus: set, allowed_cells: set, lengths: list) -> bool:
    c = CELL_CLEAN.sub("", cell).strip()
    if not c or c in allowed_cells or c in corpus:
        return True
    if len(c) >= MIN_SLOT and any(c in s for s in corpus):
        return True
    return len(c) > 40 and concatenation_of(c, corpus, lengths)
```

**Validation steps for "no"**:

1. **Clean cell**: `CELL_CLEAN.sub("", cell).strip()`
   - `CELL_CLEAN = re.compile(r"^[`*_\s]+|[`*_\s]+$")`
   - Removes leading/trailing: backticks, asterisks, underscores, whitespace
   - Input: `" no "`
   - After strip: `"no"`
   - After CELL_CLEAN: `"no"` (no markdown to remove)

2. **Check condition 2**: `c in allowed_cells`
   - `c = "no"`
   - `allowed_cells` is `manifest["_allowed_cells"]`
   - This is a **set** created at runtime

3. **Runtime set creation** (ufi.py:473):
   ```python
   manifest["_allowed_cells"] = set(manifest.get("allowed_cells", []))
   ```
   - Reads `allowed_cells` array from JSON
   - Converts to Python set

---

### 3. Manifest Loading (ufi.py:467-473)

```python
manifest = json.loads(read(man_path))
corpus = declared_corpus(authorities, repo)
colls = collections_of(authorities, repo)
manifest["_corpus_sorted"] = sorted(corpus, key=len, reverse=True)
manifest["_lengths"] = sorted({len(c) for c in corpus}, reverse=True)
manifest["_allowed_lines"] = set(manifest.get("allowed_lines", []))
manifest["_allowed_cells"] = set(manifest.get("allowed_cells", []))
```

**At line 473**: `manifest["_allowed_cells"]` becomes a set containing all strings from the JSON array.

---

### 4. Runtime Value Analysis

**Expected manifest["_allowed_cells"] contents after fix**:
```python
{
    "./verify.sh --fast",
    "./verify.sh --integration",
    "./verify.sh` (`--change`)",
    "Agent",
    "Authority home",
    "Bounded question",
    "Cardinality",
    "Claim",
    "Class",
    "Command",
    "Constitutional binding",
    "Consumed by",
    "Declared by",
    "Definition",
    "Domain",
    "Fails closed",
    "Home",
    "ID",
    "If you need…",
    "Instrument",
    "May hold authority",
    "Meaning",
    "Name",
    "Property",
    "Refusal",
    "Role",
    "Statement",
    "Surface",
    "Title",
    "Value",
    "YES",
    "commit validation: impact-selected tests + every governance gate",
    "developer feedback: lint + impact-selected tests",
    "merge validation: whole suite under the floor + every gate",
    "release certification; this is what CI runs"
}
```

**Expected**: `"no" in allowed_cells` → FALSE (not in set)

---

## ROOT CAUSE: "no" IS NOT IN MANIFEST

### Verification: Check manifest line 50

Reading context-template-manifest.json at the exact location where "no" was believed to exist:

**Lines 24-55 of manifest** (the `allowed_cells` array):
```json
"allowed_cells": [
  "./verify.sh --fast",                // line 25
  "./verify.sh --integration",         // line 26
  "./verify.sh` (`--change`)",         // line 27
  "Agent",                              // line 28
  "Authority home",                     // line 29
  "Bounded question",                   // line 30
  "Cardinality",                        // line 31
  "Claim",                              // line 32
  "Class",                              // line 33
  "Command",                            // line 34
  "Constitutional binding",             // line 35
  "Consumed by",                        // line 36
  "Declared by",                        // line 37
  "Definition",                         // line 38
  "Domain",                             // line 39
  "Fails closed",                       // line 40
  "Home",                               // line 41
  "ID",                                 // line 42
  "If you need…",                       // line 43
  "Instrument",                         // line 44
  "May hold authority",                 // line 45
  "Meaning",                            // line 46
  "Name",                               // line 47
  "Property",                           // line 48
  "Refusal",                            // line 49
  "Role",                               // line 50
  "Statement",                          // line 51
  "Surface",                            // line 52
  "Title",                              // line 53
  "Value",                              // line 54
  "YES",                                // line 55
  "commit validation: impact-selected tests + every governance gate",
  "developer feedback: lint + impact-selected tests",
  "merge validation: whole suite under the floor + every gate",
  "release certification; this is what CI runs"
],
```

**Line 50 contains**: `"Role"` (NOT `"no"`)

---

## CONCLUSION

**The original assumption was incorrect.**

**"no" was NEVER in the manifest `allowed_cells` array.**

The confusion arose from:
1. Manifest line 50 was assumed to contain `"no"`
2. Actually, after the W5 edit, line 50 contains `"Role"`
3. The pre-W5 manifest may have had different line numbering
4. `"no"` was never added to `allowed_cells`

**Why "no" fails**:

```python
c = "no"
c in allowed_cells  # → False (not in set)
c in corpus         # → False ("no" is a boolean display value, not authority data)
len(c) >= MIN_SLOT  # → False (len("no") = 2, MIN_SLOT = 6)
```

All conditions fail → returns False → cell flagged as UNPROVENANCED

---

## REQUIRED FIX

**Add to allowed_cells**:
```json
"no"
```

**Justification**: 
- "no" is the lowercase display value for `may_hold_authority: false`
- Appears in "Authority roles and their cardinality" table
- Counterpart to "YES" (which IS already in allowed_cells line 55)
- Generator uses lowercase "no" for false, uppercase "YES" for true (ukctx.py:210)

---

## VERIFICATION OF GENERATOR LOGIC

**ukctx.py lines 209-211**:
```python
md_table(["Role", "May hold authority", "Cardinality", "Definition"],
         [[r["role"], "YES" if r["may_hold_authority"] else "no",
           r["cardinality"], r["definition"]] for r in roles]),
```

**Confirmed**: Generator emits `"no"` (lowercase) when `may_hold_authority` is false.

---

**ROOT CAUSE**: `"no"` is missing from manifest `allowed_cells` array  
**FAILURE TYPE**: MISSING_MANIFEST_ENTRY  
**FIX REQUIRED**: Add `"no"` to allowed_cells  
**ANOMALY RESOLVED**: Not an anomaly—cell genuinely missing from manifest
