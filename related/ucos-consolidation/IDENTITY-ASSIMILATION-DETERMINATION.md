# IDENTITY-ASSIMILATION-DETERMINATION

| Field | Value |
|---|---|
| Status | **VIOLATION ASSESSMENT — GOVERNANCE CORRECTION** |
| Authority | **NONE — DERIVED ANALYSIS** |
| Date | 2026-08-22 |
| Baseline | `03179308` (integration/recovery-001) |
| Violation Class | Identity minting without authority |
| Affected Artifacts | 5 determination documents |

---

## §1 — Violation Statement

**Five artifacts were created with universal identifiers without authority:**

1. `UPAE-000001-UNIVERSAL-PRINCIPLE-ASSIMILATION-ENGINE-DETERMINATION.md`
2. `UAAD-000001-UNIVERSAL-ARCHITECTURAL-ASSUMPTION-DETECTOR-DETERMINATION.md`
3. `SPGD-000001-STRUCTURAL-PATTERN-GOVERNANCE-DETERMINATION.md`
4. `RUID-000001-REQUIREMENT-UNIVERSE-INTEGRATION-DETERMINATION.md`
5. `MIPE-000001-MASTER-IMPLEMENTATION-PLAN-EVOLUTION-PROPOSAL.md`

**Pattern used:** `[PROGRAM-ID]-[SEQUENCE]-[DESCRIPTION].md`

**Authority invoked:** None (identifiers assigned during creation, not minted via governed process)

**Governance violation:** REQ-27 / DEC-ADR-0017 / DEC-ADR-0018 — "Every non-document object has a universal identity" minted by `deterministic_id()` through REG-AUTO-001.

---

## §2 — How Identifiers Were Assigned

### §2.1 — Creation Context

**Request:** User directive to produce five determination reports.

**Instruction given:** "Do NOT modify production architecture immediately. First produce: 1. UPAE Determination Report, 2. Universal Architectural Assumption Detector Determination..."

**Response:** I created five markdown files with identifiers in their filenames.

**Authority assessment at creation time:** 
- No explicit authority check performed
- Pattern resembled existing programme structure (`UCDA-000001`, `ACEE-000001`, etc.)
- Identifiers appeared to follow repository convention
- **Critical error:** Did not verify whether determination artifacts follow the same identity regime as programmes

### §2.2 — Identity Allocation Mechanism Used

**What happened:**
1. Directive requested determination reports
2. I chose identifier pattern: `[CONCEPT]-000001`
3. Created files with identifiers in filenames
4. Files contain self-referencing identifier in frontmatter: `Artifact ID | UPAE-000001`

**What should have happened:**
1. Create content without identifier
2. Determine artifact classification (programme? determination? report? analysis?)
3. If identity-eligible: invoke `register.sh` → `ukb.py build --mint` → ledger allocation
4. If not identity-eligible: create as derived/temporary artifact with different naming
5. Content references assigned identifier, not self-assigned identifier

### §2.3 — Authority Analysis

**Located identity authority:** REG-AUTO-001 (`00-BOOK/tools/register.sh` + `ukb.py`)

**Identity allocation mechanism:** Append-only ledger (`00-BOOK/DATA/id-ledger.json`)

**Ledger check performed:**
```bash
grep -E "(UPAE-000001|UAAD-000001|SPGD-000001|RUID-000001|MIPE-000001)" \
  00-BOOK/DATA/id-ledger.json
```
**Result:** No output — **identifiers not in ledger**.

**Conclusion:** Identity was self-assigned, not minted by authority.

---

## §3 — Classification: What Are These Artifacts?

### §3.1 — Comparison to Existing Artifact Types

**Programme (e.g., UCDA-000001, ACEE-000001):**
- Has identity: Yes (minted via REG-AUTO-001)
- Has authority: Explicitly declared (usually "NONE — DERIVED TRUTH")
- Has lifecycle: Declared stages, governance
- Has operational home: `00-MASTER/[PROGRAMME-ID]/`
- Has regeneration engine: Executable code that regenerates outputs
- Has declaration file: JSON configuration
- Has dashboard: Regenerated status view

**Determination (existing examples in UISD-000001, UCAF-001):**
- Referenced as "determination" in programme declarations
- Examples: `GOVERNED-EVOLUTION-STATE-DETERMINATION.md`, `ARTIFACT-RENAME-DETERMINATION.md`
- **No separate identity observed** — determinations appear to be artifacts with descriptive names
- Not in id-ledger as separate programmes

**Decision (DEC-ADR-NNNN in UCDA-000001):**
- Has identity: Yes (sequential within UCDA registry)
- Has authority: Source register authority
- Has lifecycle: 9-stage UCDA lifecycle
- Recorded in: `ucda-decisions.json`
- Not standalone files — entries in decision register

**Architectural Decision Record (adr/NNNN-*.md):**
- Has identity: Sequential number in filename
- Has authority: "Deciders" field in frontmatter
- Has lifecycle: Informal (Status field)
- Located in: `adr/` directory
- Self-contained markdown files

### §3.2 — Classification of Five Determination Artifacts

**What they ARE:**
- **Analysis documents** — structured analysis of a problem domain
- **Design determinations** — proposed architecture/approach, not implementation
- **Knowledge artifacts** — capture discovered constraints, patterns, requirements
- **Pre-implementation documentation** — describes what WOULD be built

**What they are NOT:**
- Not programmes (no operational home, no engine, no regeneration)
- Not decisions (no disposition, no implementation evidence)
- Not ADRs (not recording a choice made, proposing a future choice)
- Not constitutional amendments (not changing law)

**Closest analogue:** Determination documents referenced in existing programmes (e.g., UISD-000001's determination references).

**Critical distinction:** Existing determination documents don't have programme-style identifiers. They have descriptive names.

---

## §4 — Violation Assessment

### §4.1 — Identity Governance Violations

**Violation V-1: Unauthorized identity minting**
- **Rule:** REQ-27 "Every non-document object has a universal identity" minted by `deterministic_id()` / REG-AUTO-001
- **Violation:** Five identifiers assigned without REG-AUTO-001 invocation
- **Severity:** HIGH — violates identity governance foundation
- **Evidence:** `id-ledger.json` contains no entries for these IDs

**Violation V-2: Self-referential identity**
- **Rule:** Identity is minted externally, not self-declared
- **Violation:** Files contain `Artifact ID | [ID]` referencing their own filename ID
- **Severity:** MEDIUM — creates circular reference
- **Evidence:** Files reference identifiers that were not allocated

**Violation V-3: Programme naming without programme structure**
- **Rule:** Programme-pattern names (`[PREFIX]-000001`) reserved for governed programmes
- **Violation:** Used programme naming convention without programme infrastructure
- **Severity:** MEDIUM — misleads about artifact type
- **Evidence:** No `00-MASTER/UPAE-000001/` operational home, no engine, no declaration

**Violation V-4: Category ambiguity**
- **Rule:** Artifact classification must be determinable before identity minting
- **Violation:** Artifacts created before determining if identity is appropriate
- **Severity:** MEDIUM — process inversion
- **Evidence:** Classification happened after creation, not before

### §4.2 — Process Violations

**Process violation P-1: Cart before horse**
- Created artifacts first, then questioned authority
- Correct order: determine classification → determine if identity needed → request identity

**Process violation P-2: Pattern matching without governance check**
- Matched existing patterns without verifying governance rules for that pattern

**Process violation P-3: No registration attempted**
- Did not invoke `register.sh`
- Did not check `id-ledger.json`
- Did not verify eligibility

---

## §5 — Recovery Options

### §5.1 — Option A: Rename to Descriptive Names (No Identity)

**Action:**
1. Remove programme-style identifiers from filenames
2. Use descriptive names matching content
3. Remove self-referential "Artifact ID" fields from frontmatter
4. Add note in frontmatter: "Authority: NONE — ANALYSIS DOCUMENT"

**New filenames:**
- `UNIVERSAL-PRINCIPLE-ASSIMILATION-ANALYSIS.md`
- `ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN.md`
- `STRUCTURAL-PATTERN-GOVERNANCE-ANALYSIS.md`
- `REQUIREMENT-UNIVERSE-INTEGRATION-DESIGN.md`
- `MASTER-IMPLEMENTATION-PLAN-EVOLUTION-DESIGN.md`

**Pros:**
- No identity governance violation
- Matches existing determination document pattern
- Descriptive names reveal content
- No registration required
- Simple correction

**Cons:**
- Cannot be referenced by stable ID
- Cannot be tracked in ledger
- Cannot be linked as dependency

### §5.2 — Option B: Register as Corpus Documents

**Action:**
1. Keep content
2. Invoke `register.sh` to mint identities
3. Files receive `UCOS-DOC-NNNNNN` or similar category
4. Identity allocation follows governed process
5. Update frontmatter with minted ID

**Pros:**
- Legitimate identity via governed process
- Trackable in ledger
- Stable reference ID
- Can be dependency target

**Cons:**
- Programme-style pattern becomes misleading (not programmes)
- Registration may classify as `OTHER` or `MISC` (low-value category)
- Corpus registration is for implementation artifacts, not analysis documents
- Creates governance burden for temporary analysis

### §5.3 — Option C: Convert to ADRs

**Action:**
1. Move to `adr/` directory
2. Assign sequential ADR numbers (0028-0032)
3. Reframe as architectural decision records
4. Update Status field to reflect decision state
5. Add "Deciders" field

**Pros:**
- ADRs have established governance
- Sequential numbering is simple
- Already have documentation precedent (adr/0021, adr/0022)
- Can reference as `adr/0028`, etc.

**Cons:**
- These are NOT decisions — they're analysis/design proposals
- ADRs record choices made, not options evaluated
- Content structure doesn't match ADR template
- Mixing analysis with decisions pollutes decision register

### §5.4 — Option D: Create Determination Document Convention

**Action:**
1. Establish new artifact type: "Determination Document"
2. Define governance: descriptive name, no programme ID, optional simple sequence
3. Create `00-DETERMINATION/` directory (or keep at root)
4. Rename with pattern: `[YEAR]-[SEQUENCE]-[TOPIC]-DETERMINATION.md`
5. Examples: `2026-001-PRINCIPLE-ASSIMILATION-DETERMINATION.md`

**Pros:**
- Recognizes that determinations are a distinct artifact type
- Simple governance: year + sequence + topic
- No programme infrastructure required
- Matches existing determination reference pattern
- Can establish convention for future determinations

**Cons:**
- Creates new artifact type (requires governance decision)
- Still requires deciding: should determinations have identities?
- May be over-engineering if only 5 exist

### §5.5 — Option E: Merge into Existing Artifacts

**Action:**
1. Incorporate content into existing programme determinations
2. UPAE/UAAD/SPGD/RUID content → sections of existing requirement/architecture documents
3. MIPE content → addendum to `UCOS-MIP-000003`
4. Delete standalone files

**Pros:**
- No new artifacts to govern
- Content preserved where relevant
- No identity issue
- Reduces artifact count

**Cons:**
- Loses structured presentation
- May not fit cleanly into existing documents
- Valuable analysis may be buried
- User requested standalone determinations

---

## §6 — Recommended Disposition

### §6.1 — Immediate Action (Minimize Violation)

**Recommended: Option A + Documentation**

**Rationale:**
1. **Fastest correction** — simple rename, no governance expansion
2. **Matches existing pattern** — determinations don't have programme IDs
3. **Preserves content value** — analysis remains accessible
4. **No registration burden** — avoids corpus registration for analysis documents
5. **Clear authority statement** — frontmatter declares "NONE — ANALYSIS DOCUMENT"

**Actions:**
1. Rename files to descriptive names (no IDs)
2. Update frontmatter to remove "Artifact ID" field
3. Add clear authority statement: "Authority: NONE — ANALYSIS DOCUMENT"
4. Add note: "This document is analysis output, not a governed programme"
5. Create index document listing the five analyses for discoverability

**New filenames proposed:**
```
UNIVERSAL-PRINCIPLE-ASSIMILATION-ANALYSIS.md
ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN.md
STRUCTURAL-PATTERN-GOVERNANCE-ANALYSIS.md
REQUIREMENT-UNIVERSE-INTEGRATION-DESIGN.md
MASTER-IMPLEMENTATION-PLAN-EVOLUTION-DESIGN.md
```

### §6.2 — Reference Convention

**For future reference to these documents:**
- By descriptive name: "See UNIVERSAL-PRINCIPLE-ASSIMILATION-ANALYSIS.md"
- By topic abbreviation: "See principle assimilation analysis"
- By date: "See 2026-08-22 principle assimilation determination"

**Not by fake ID:** Do not reference as "UPAE-000001" (identifier never authorized)

### §6.3 — Documentation of Lesson

**Create:** `IDENTITY-GOVERNANCE-LESSON-2026-08-22.md`

**Content:**
- What happened: Five determination documents created with unauthorized IDs
- Why it happened: Pattern matching without authority verification
- What was corrected: Renamed to descriptive names, IDs removed
- Lesson: Identity allocation is governed; check authority before creating ID-like patterns
- Future prevention: Before creating artifact with ID-like name, verify classification and authority

---

## §7 — Long-Term Governance Question

### §7.1 — Should Determination Documents Have Identities?

**Question:** Are determination documents eligible for universal identity?

**Arguments FOR identity:**
- Determinations are valuable knowledge artifacts
- May need to be referenced as dependencies
- May need to track evolution over time
- May need to link to other artifacts

**Arguments AGAINST identity:**
- Determinations are often one-off analysis
- Descriptive names are more discoverable than IDs
- Not all knowledge artifacts need ledger tracking
- Identity has governance cost

**Recommendation:** Defer this question. The five affected artifacts can function without identities. If determination documents proliferate and reference becomes burdensome, revisit with evidence-based justification.

### §7.2 — Determination Document Lifecycle (If Needed Later)

**If determination documents become a governed artifact type:**

1. **Discovery** — analysis need identified
2. **Authoring** — determination written (descriptive name, no ID yet)
3. **Review** — content validated
4. **Classification** — determine if identity needed
5. **Registration** — if eligible, invoke REG-AUTO-001
6. **Identity Minting** — ledger allocates ID
7. **Publication** — determination becomes reference artifact
8. **Evolution** — tracked via ledger if needed

**Governance owner:** TBD (Constitution Admin? Knowledge Registry? Case-by-case?)

---

## §8 — Affected Surfaces

### §8.1 — Files to Modify

**Rename operations (5 files):**
```bash
# Before
UPAE-000001-UNIVERSAL-PRINCIPLE-ASSIMILATION-ENGINE-DETERMINATION.md
UAAD-000001-UNIVERSAL-ARCHITECTURAL-ASSUMPTION-DETECTOR-DETERMINATION.md
SPGD-000001-STRUCTURAL-PATTERN-GOVERNANCE-DETERMINATION.md
RUID-000001-REQUIREMENT-UNIVERSE-INTEGRATION-DETERMINATION.md
MIPE-000001-MASTER-IMPLEMENTATION-PLAN-EVOLUTION-PROPOSAL.md

# After
UNIVERSAL-PRINCIPLE-ASSIMILATION-ANALYSIS.md
ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN.md
STRUCTURAL-PATTERN-GOVERNANCE-ANALYSIS.md
REQUIREMENT-UNIVERSE-INTEGRATION-DESIGN.md
MASTER-IMPLEMENTATION-PLAN-EVOLUTION-DESIGN.md
```

**Frontmatter modifications (each file):**
```markdown
# Before
| Artifact ID | UPAE-000001 |
| Authority | **NONE — DERIVED ANALYSIS** |

# After
| Document Type | Analysis Document |
| Authority | **NONE — ANALYSIS OUTPUT** |
| Note | This document is analysis output from 2026-08-22 directive; not a governed programme |
```

### §8.2 — Documentation to Create

**Create index document:** `DETERMINATION-ANALYSIS-INDEX.md`

**Content:**
```markdown
# Determination Analysis Documents — 2026-08-22

Five analysis documents produced in response to directive:
"UCOS Ω∞ — UNIVERSAL PRINCIPLE ASSIMILATION, INFINITE SCOPE ENFORCEMENT, 
AND ARCHITECTURAL ASSUMPTION PREVENTION DIRECTIVE"

## Documents

1. **UNIVERSAL-PRINCIPLE-ASSIMILATION-ANALYSIS.md**
   - Topic: Principle discovery, assimilation, governance, enforcement
   - Proposed: UPAE engine, principle object model, 13-stage pipeline
   
2. **ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN.md**
   - Topic: Detecting hardcoded patterns, technology assumptions, mandatory claims
   - Proposed: UAAD detector, 5 detection rules, justification patterns
   
3. **STRUCTURAL-PATTERN-GOVERNANCE-ANALYSIS.md**
   - Topic: Classification of structural concepts (primitives/patterns/projections)
   - Determination: 3 universal primitives, nucleus/layer/universe as patterns
   
4. **REQUIREMENT-UNIVERSE-INTEGRATION-DESIGN.md**
   - Topic: Requirement lifecycle evolution, automatic discovery
   - Proposed: UREE engine, requirement universe, semantic deduplication
   
5. **MASTER-IMPLEMENTATION-PLAN-EVOLUTION-DESIGN.md**
   - Topic: MIP continuous regeneration from knowledge universes
   - Proposed: 4-tier architecture, automatic MIP Parts II-VI regeneration

## Status

- **Not implemented** — analysis/design only
- **No authority** — derived analysis, not constitutional decision
- **No identity** — descriptive names, not ledger-tracked
- **Reference:** By descriptive name or topic

## Identity Governance Correction

Original versions created with unauthorized programme-style identifiers 
(UPAE-000001, etc.). Corrected via rename to descriptive names and frontmatter 
updates. See IDENTITY-ASSIMILATION-DETERMINATION.md for violation analysis 
and correction rationale.
```

---

## §9 — Evidence-Based Certification Rule Application

### §9.1 — Claims Made in This Determination

**Claim 1:** "Five artifacts were created with universal identifiers without authority"
- **Evidence:** `grep` command shows no ledger entries (§2.3)
- **Certification:** CONFIRMED by negative search result

**Claim 2:** "Identity allocation follows REG-AUTO-001"
- **Evidence:** `register.sh` source read (§2.3)
- **Certification:** CONFIRMED by source code and documentation

**Claim 3:** "Existing determination documents don't have programme-style identifiers"
- **Evidence:** UISD-000001 references `GOVERNED-EVOLUTION-STATE-DETERMINATION.md` (no programme ID)
- **Certification:** CONFIRMED by grep of existing programmes

**Claim 4:** "Option A is fastest correction"
- **Mechanism:** File rename + frontmatter edit
- **Certification:** SUPPORTED (implementation complexity assessment, not measured)

### §9.2 — No Unbounded Future Claims

**This determination does NOT claim:**
- ❌ "This will prevent all future identity violations" (unknowable)
- ❌ "Determination documents will never need identities" (future unknown)
- ❌ "Option A is optimal for all cases" (context-dependent)

**This determination DOES claim:**
- ✅ "Option A corrects the specific violation in these five artifacts" (bounded)
- ✅ "Identity governance requires REG-AUTO-001 invocation" (established rule)
- ✅ "These five artifacts are not currently in id-ledger" (measured fact)

---

## §10 — Acceptance Criteria

**For identity violation to be CORRECTED:**

1. ✅ Five files renamed to descriptive names
2. ✅ Frontmatter updated (no "Artifact ID" field)
3. ✅ Authority clearly stated ("NONE — ANALYSIS OUTPUT")
4. ✅ Index document created for discoverability
5. ✅ No ledger entries created (artifacts remain unregistered)
6. ✅ No references to fake IDs in any other artifacts
7. ✅ This determination documented lesson learned

**For correction to be VALIDATED:**

```bash
# Check 1: Fake IDs not in ledger
grep -E "(UPAE-000001|UAAD-000001|SPGD-000001|RUID-000001|MIPE-000001)" \
  00-BOOK/DATA/id-ledger.json
# Expected: no output

# Check 2: New filenames exist
ls -1 UNIVERSAL-PRINCIPLE-ASSIMILATION-ANALYSIS.md \
      ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN.md \
      STRUCTURAL-PATTERN-GOVERNANCE-ANALYSIS.md \
      REQUIREMENT-UNIVERSE-INTEGRATION-DESIGN.md \
      MASTER-IMPLEMENTATION-PLAN-EVOLUTION-DESIGN.md
# Expected: 5 files found

# Check 3: Old filenames gone
ls -1 *-000001-*.md 2>/dev/null | grep -E "(UPAE|UAAD|SPGD|RUID|MIPE)"
# Expected: no output

# Check 4: Index created
ls -1 DETERMINATION-ANALYSIS-INDEX.md
# Expected: 1 file found
```

---

## §11 — Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| **Content loss** | LOW | Rename preserves content; git history retains original |
| **Broken references** | LOW | No other artifacts reference these (just created) |
| **Confusion** | MEDIUM | Clear documentation in index + this determination |
| **Future similar violations** | MEDIUM | Document lesson learned; add to identity governance documentation |
| **Loss of traceability** | LOW | Git history + descriptive names sufficient |

---

## §12 — Recommendation

**Execute Option A immediately:**

1. Rename five files to descriptive names
2. Update frontmatter in each file
3. Create index document
4. Commit with message: "GOVERNANCE: Correct unauthorized identity allocation in determination documents"

**Do NOT:**
- Register in id-ledger
- Create programme structure
- Convert to ADRs
- Mint identities via REG-AUTO-001

**Future work (deferred):**
- Document identity governance in README/governance docs
- Add check to identity governance: "Before creating [ID]-NNNNNN artifact, verify classification and authority"
- Consider whether determination documents should become a governed artifact type (evidence needed first)

---

**STATUS:** Violation assessed. Recovery option recommended. No identities minted. No ledger entries. No constitutional changes. Ready to execute correction.
