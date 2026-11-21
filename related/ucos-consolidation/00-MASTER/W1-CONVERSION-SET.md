# W1 — CONVERSION SET

**Artifact ID**: UCOS-W1-CONVERSION-SET-001  
**Date**: 2026-09-01  
**Authority**: PHASE W1 — MB7 REPOSITORY-WIDE BATCH CONVERSION  
**Source**: C13-MB7-REUSE-MATRIX.md CLASS 3 producers

---

## OBJECTIVE

Select every producer classified CLASS 3 (UFI + authority extraction) for batch conversion to independent validation.

---

## SELECTION CRITERIA

**From C13-MB7-REUSE-MATRIX.md**:

**CLASS 3**: UFI + authority extraction required
- Generator embeds authority (no separate authority file)
- Output is JSON or structured text
- UFI framework can validate once authority extracted
- Batch-convertible via tooling

**Selected**: All 31 CLASS 3 producers

**Excluded**: 
- UCOS-UCTX-001 (already closed, CLASS 1)
- No CLASS 2 or CLASS 4 producers exist

---

## CONVERSION SET (31 PRODUCERS)

### Batch A — JSON Generators (20 producers)

| Producer | Authority Source | Generated Artifacts | Output Format |
|----------|-----------------|---------------------|---------------|
| **ACEE-000001** | acee_engine.py | 00-AUTONOMOUS-CONSTITUTIONAL-ENGINEERING-DASHBOARD.md | Markdown (data-driven) |
| **BASELINE-001** | baseline_engine.py | BASELINE-REGISTER.md | Markdown (JSON-driven) |
| **MCOS-000001** | mcos_engine.py | mcos-dashboard.md | Markdown (JSON-driven) |
| **P0-LIFECYCLE-CLOSURE-001** | p0_lifecycle_closure_engine.py | lifecycle-closure-dashboard.md | Markdown (JSON-driven) |
| **UAIE-000001** | uaie_engine.py | 00-UAIE-DASHBOARD.md, 02-REGISTER-PLANE.md, 03-CROSS-REGISTER-CONSISTENCY.md, 05-VALIDATION-REPORT.md, 06-CERTIFICATION-REPORT.md | Markdown (JSON-driven) |
| **UAKOS-CLOSURE-008** | assimilation_engine.py | 01-REPOSITORY-RECONCILIATION-REGISTER.md through 11-IMPLEMENTATION-PLAN-REGISTER.md (11 files) | Markdown (JSON-driven) |
| **UAKOS-CLOSURE-009** | closure_009_engine.py | closure-dashboard.md | Markdown (JSON-driven) |
| **UAKOS-PHASE-001A-R1** | phase_001a_r1_engine.py | phase-dashboard.md | Markdown (JSON-driven) |
| **UAKOS-PHASE-003R** | phase_003r_engine.py | phase-dashboard.md | Markdown (JSON-driven) |
| **UAUE-000001** | uaue_engine.py | uaue-dashboard.md | Markdown (JSON-driven) |
| **UCDA-000001** | ucda_engine.py | ucda-dashboard.md | Markdown (JSON-driven) |
| **UCEF-000001** | ucef_engine.py | ucef-dashboard.md | Markdown (JSON-driven) |
| **UCL-000001** | ucl_engine.py | ucl-dashboard.md | Markdown (JSON-driven) |
| **UCOS-AEE-001** | aee_engine.py | aee-dashboard.md, aee-evolution-log.md | Markdown (JSON-driven) |
| **UCOS-MXR-001** | mxr_engine.py | mxr-dashboard.md | Markdown (JSON-driven) |
| **UCOS-NUCLEUS-001** | nucleus_engine.py | nucleus-dashboard.md | Markdown (JSON-driven) |
| **UEI-000001** | uei_engine.py | uei-dashboard.md | Markdown (JSON-driven) |
| **UER-000001** | uer_engine.py | uer-dashboard.md | Markdown (JSON-driven) |
| **UIS-001** | uis_engine.py | uis-dashboard.md | Markdown (JSON-driven) |
| **UKAP-001** | ukap_engine.py | ukap-dashboard.md | Markdown (JSON-driven) |

### Batch B — JSON Generators Continued (3 producers)

| Producer | Authority Source | Generated Artifacts | Output Format |
|----------|-----------------|---------------------|---------------|
| **UMK-000001** | umk_engine.py | umk-dashboard.md | Markdown (JSON-driven) |
| **UPF-000001** | upf_engine.py | upf-dashboard.md | Markdown (JSON-driven) |
| **URRC-000001** | urrc_engine.py | urrc-dashboard.md | Markdown (JSON-driven) |

### Batch C — Text Generators (8 producers)

| Producer | Authority Source | Generated Artifacts | Output Format |
|----------|-----------------|---------------------|---------------|
| **UCOS-RIB-001** | rib_engine.py | RIB registers | Markdown (template-driven) |
| **UCOS-RIE-001** | rie_engine.py | RIE registers | Markdown (template-driven) |
| **UCOS-UAR-001** | uar_engine.py | UAR registers | Markdown (template-driven) |
| **UCOS-UCAF-001** | ucaf_engine.py | UCAF registers | Markdown (template-driven) |
| **UCOS-UFEP-001** | ufep_engine.py | UFEP registers | Markdown (template-driven) |
| **UCOS-UGA-001** | uga_engine.py | UGA registers | Markdown (template-driven) |
| **UCOS-USIS-WAVE0** | usis_wave0_engine.py | USIS registers | Markdown (template-driven) |
| **UCOS-UTCE-001** | utce_engine.py | UTCE registers | Markdown (template-driven) |

---

## UFI ADOPTION REQUIREMENTS

For each producer in the conversion set:

### Required Artifacts (per producer)

**1. Authority Extraction**
- **File**: `00-BOOK/DATA/{producer}-authority.json`
- **Content**: Extracted canonical authority from generator source
- **Format**:
```json
{
  "artifact_id": "{PRODUCER}-AUTHORITY-001",
  "title": "{Producer} Authority — canonical truth for {producer} surfaces",
  "authority": "AUTHORED REPOSITORY TRUTH...",
  "constitutional_superior": {...},
  "schema": "{producer}-authority",
  "version": "1.0.0",
  "{domain}_data": {...}
}
```

**2. Independence Declaration**
- **File**: `00-BOOK/DATA/independence/{producer}-independence.json`
- **Content**: UFI configuration binding authorities, surfaces, manifest
- **Format**:
```json
{
  "owner": "{PRODUCER}",
  "authorities": [
    "00-BOOK/DATA/{producer}-authority.json",
    {"from": "00-BOOK/DATA/generated-artifact-registry.json", 
     "json_path": "entries[?owner=='{PRODUCER}'].canonical_path"}
  ],
  "surfaces": {
    "from": "00-BOOK/DATA/generated-artifact-registry.json",
    "json_path": "entries[?owner=='{PRODUCER}'].canonical_path"
  },
  "manifest": "00-BOOK/DATA/independence/{producer}-template-manifest.json"
}
```

**3. Template Manifest**
- **File**: `00-BOOK/DATA/independence/{producer}-template-manifest.json`
- **Content**: Declared templates extracted from known-good output
- **Format**:
```json
{
  "allowed_lines": [
    "# {Producer} Dashboard",
    "**Status**: {}",
    "| Field | Value |",
    ...
  ],
  "allowed_cells": [
    "Status", "Field", "Value", ...
  ],
  "required_projections": [
    {
      "surfaces": ["ALL_SURFACES"],
      "source": "00-BOOK/DATA/{producer}-authority.json",
      "collection": "{domain}_data",
      "field": "id"
    }
  ]
}
```

**4. CI Integration**
- **File**: `verify.sh` (append stage)
- **Content**:
```bash
stage_{producer}_validation() {
    python3 00-BOOK/tools/ufi.py 00-BOOK/DATA/independence/{producer}-independence.json
}
```

---

## BATCH CONVERSION STRATEGY

### Phase 1: Tooling (14-24 hours)

**Authority Extraction Script** (4-8 hours):
- Parse Python generator source
- Extract embedded data structures (dicts, lists, string literals)
- Generate authority JSON with constitutional bindings
- Reuse UCOS-UCTX-001 pattern

**Template Extraction Tool** (8-12 hours):
- Read known-good generator output
- Normalize lines (replace declared values with `{}`)
- Extract unique templates
- Generate manifest JSON
- Reuse UCOS-UCTX-001 template-manifest.json structure

**CI Integration Template** (2-4 hours):
- Generate verify.sh stages from producer list
- Template: `stage_{producer}_validation() { python3 00-BOOK/tools/ufi.py ... }`
- Update UVI registry with new stages

### Phase 2: Batch Extraction (2-3 hours automated)

**For each producer**:
1. Run authority extraction → `{producer}-authority.json`
2. Run template extraction → `{producer}-template-manifest.json`
3. Generate independence declaration → `{producer}-independence.json`
4. Generate CI stage → append to `verify.sh`

### Phase 3: Human Review (17-24 hours)

**Per producer** (~30-45 min):
- Review extracted authority (completeness, accuracy)
- Review extracted templates (coverage, false positives)
- Review independence declaration (correct bindings)
- Approve for CI deployment

### Phase 4: CI Deployment (3-6 hours)

**For each approved producer**:
1. Commit authority, declaration, manifest
2. Deploy CI stage
3. Run verification
4. Measure attack detection

---

## VALIDATION CONFIGURATION

### UFI Check 1: Provenance

**Requirement**: Every emitted line traces to declared source (authority or template)

**Configuration**: 
- `authorities`: List of authority JSON files
- `manifest.allowed_lines`: Extracted templates
- `MIN_SLOT`: 6 (from ufi.py, prevents false matches on "the", "and")

**Detection**: Lines not in corpus or template → UNPROVENANCED

### UFI Check 2: Record Integrity

**Requirement**: Every table row reconciles to ONE declared record

**Configuration**:
- Automatic discovery from authorities (any `list[dict]` is a collection)
- No manual collection enumeration required

**Detection**: Row cells from multiple records → MISBOUND

### UFI Check 3: Completeness

**Requirement**: Every declared obligation carried in surfaces

**Configuration**:
- `required_projections`: List of {source, collection, field, surfaces}
- Example: All producer IDs from authority must appear in ALL_SURFACES

**Detection**: Declared value absent from surface → MISSING

---

## REUSE FROM UCOS-UCTX-001

### Proven Patterns (Direct Reuse)

**1. Authority Structure**:
```json
{
  "artifact_id": "...",
  "authority": "AUTHORED REPOSITORY TRUTH, HELD AS A PROJECTION UNDER UCKP-LAW-0001...",
  "constitutional_superior": {
    "authority": "UCKP-LAW-0001",
    "home": "engine/uckp/law.py",
    "role": "PROJECTION",
    "articles": ["UCKP-ART-04", "UCKP-ART-11"],
    "binding": "00-BOOK/DATA/constitutional-authority-alignment.json"
  }
}
```

**2. Independence Declaration**:
```json
{
  "owner": "PRODUCER-ID",
  "authorities": [...],
  "surfaces": {...pointer...},
  "manifest": "path/to/manifest.json"
}
```

**3. Template Manifest**:
```json
{
  "allowed_lines": ["# Heading", "| col | col |", ...],
  "allowed_cells": ["Status", "ID", ...],
  "required_projections": [{...}]
}
```

**4. CI Stage**:
```bash
stage_uctx_validation() {
    python3 00-BOOK/tools/ufi.py 00-BOOK/DATA/independence/uctx-independence.json
}
```

### Extraction Complexity by Producer Type

**JSON Generators** (20 producers):
- Authority: Extract data dicts/lists from Python source
- Templates: Markdown tables + headers (standard structure)
- Complexity: LOW (uniform pattern)

**Text Generators** (8 producers):
- Authority: Extract string templates from Python source
- Templates: More variability (prose + tables)
- Complexity: MEDIUM (template extraction more complex)

**Makefile Generators** (3 producers):
- Authority: Parse make rules or referenced JSON
- Templates: Generated script output
- Complexity: LOW (usually simple structured output)

---

## ATTACK TEST CONFIGURATION

### Attack A7: Wrong Generator Output

**Setup**: Modify generator to emit incorrect data

**Test Cases** (per producer):
1. Invent new sentence not in authority
2. Swap two record fields
3. Drop required projection
4. Permute table rows
5. Truncate authority statement

**Expected**: UFI detects all 5 attacks (Check 1, 2, or 3 fails)

**Measurement**: `attack_detected / attack_executed`

### Attack A1: Artifact Corruption

**Setup**: Modify emitted artifact directly (bypass generator)

**Test Cases** (per producer):
1. Hand-edit surface to add undeclared line
2. Delete row from table
3. Swap header row with body row
4. Change declared value to undeclared value

**Expected**: UFI detects all 4 attacks (Check 1 or 2 fails)

**Measurement**: `attack_detected / attack_executed`

---

## SUCCESS CRITERIA (Per Producer)

**Authority Extraction**:
- ✓ All embedded data extracted to authority JSON
- ✓ No second authoring (UCKP-ART-03)
- ✓ Constitutional binding present

**Template Extraction**:
- ✓ All output lines covered by template or authority
- ✓ No false positives (structural lines not over-specified)
- ✓ Normalization preserves sentence structure

**Independence Declaration**:
- ✓ Authorities list complete
- ✓ Surfaces pointer resolves correctly
- ✓ Manifest path valid

**CI Integration**:
- ✓ Stage executes without error
- ✓ UFI verification passes on clean output
- ✓ UFI verification fails on attacked output

**Registry Update**:
- ✓ `independent_validation` field updated
- ✓ `validation_owner != owner`
- ✓ MB7 closure condition met

---

## CONVERSION SET SUMMARY

**Total Producers**: 31

**By Output Type**:
- JSON-driven Markdown: 23 (74%)
- Template-driven Markdown: 8 (26%)

**By Complexity**:
- Low (JSON batch): 23 (74%)
- Medium (text batch): 8 (26%)

**Batch Convertible**: 31 (100%)

**Requires Unique Work**: 0 (0%)

**Estimated Effort**:
- Tooling: 14-24 hours
- Extraction: 2-3 hours (automated)
- Review: 17-24 hours (human)
- Deployment: 3-6 hours
- **Total**: 36-57 hours (optimistic), 58-84 hours (full batch from C13)

**Critical Path**:
- Tooling development: Sequential (14-24 hours)
- Batch extraction: Parallel (2-3 hours)
- Review: Bottleneck (17-24 hours, can split 2 reviewers)
- Deployment: Parallel (3-6 hours)

**Next Batch (W2)**: None — this is the final batch (all CLASS 3 producers)

---

**Status**: W1-CONVERSION-SET COMPLETE ✓  
**Selected**: 31/32 open producers (97%)  
**Method**: UFI + authority extraction (CLASS 3)  
**Batch Strategy**: JSON batch (23) + Text batch (8)
