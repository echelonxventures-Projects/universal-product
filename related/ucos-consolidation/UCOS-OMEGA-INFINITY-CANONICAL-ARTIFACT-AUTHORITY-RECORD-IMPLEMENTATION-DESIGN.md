# UCOS Ω∞ — CANONICAL ARTIFACT AUTHORITY RECORD IMPLEMENTATION DESIGN

**BC-6 · Implementation Preparation — Converting six determinations of evidence into an implementation-ready design**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-CANONICAL-ARTIFACT-AUTHORITY-RECORD-IMPLEMENTATION-DESIGN.md` |
| Authority | **NONE — DESIGN PROPOSAL.** Creates no identifier, schema, registry, or certification of record. Every design decision below requires the authority named in §10's sequence before it may be built. This artifact authorizes nothing. |
| Mode | **DESIGN ONLY** · **NO IMPLEMENTATION · NO CODE CHANGE · NO REGISTRY WRITE · NO CERTIFICATION CHANGE · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Relationship to BC-6 | BC-6 Steps 1–6 are **analysis**, complete, 26 findings raised, 0 resolved. This artifact is the first **design** artifact in the chain — it proposes closure for the findings, it does not close them |
| Inputs | Step 3 (`AV-1`…`AV-9`) · Step 4 (`AAT-1`…`AAT-5`) · Step 5 (`AAR-1`…`AAR-5`) · Step 6 (`CAAR-1`…`CAAR-5`) — every design decision below cites the specific finding it addresses; no requirement is introduced that does not trace to a numbered finding |
| Findings addressed | 26 of 26 (traceability matrix, §11) |
| Findings closed by this artifact | **ZERO** — a design closes nothing; only its implementation, validated against §8's gates, can |

---

## 0. Design Constraints, Carried Forward As Non-Negotiable

Every section below is bound by four conclusions Steps 1–6 already established as
measured fact, not preference. A design that violates any of these does not qualify as a
response to BC-6's evidence:

1. **Visibility must never determine classification** (Step 3 §3.1, `AV-6`). No field in
   CAAR may be derived from `tracked`/`ignored`/`untracked` state before class is resolved.
2. **The terminal at every node is fail-closed, never a default** (Step 3 §7.2 Rule 2).
   CAAR must refuse an unresolved artifact, never silently absorb it.
3. **Ownership is never fabricated to close a metric** (`OwnershipFabricationError`, cited
   Step 3 §3.5). CAAR's owner-resolution algorithm (§5) must be able to return
   `UNRESOLVED` and must never infer.
4. **Certification must never feed back into an upstream node** (Step 3 §7.2 Rule 1,
   `AV-8`). CAAR is read by certification; certification state is never read back into
   CAAR's class, owner, or visibility fields.

---

## 1. CAAR Schema Design

### 1.1 Record shape

One record per **Artifact Identity** (§2), carrying exactly the seven fields Step 6 §2.1
defined, plus provenance metadata making the record's own derivation auditable — CAAR is
itself a GENERATED artifact (§3.2) and must satisfy the same standard it would enforce on
others.

```jsonc
{
  "schema": "ucos-canonical-artifact-authority-record",
  "version": "0.1.0-design",          // no version is minted until implementation authority approves §10 Stage 0

  "identity": {
    "caar_id": "CAAR-<16 hex>",        // minted once, §2 — never derived from path
    "current_path": "engine/execution_environment/gate.py",
    "path_history": ["..."],           // append-only, survives rename/move
    "origin": "AUTHORED | PRODUCED | OBSERVED",   // closes Step 3 §7.3's "ORIGIN not represented" gap
    "minted_at_commit": "<sha>",
    "minted_by": "<registry that first admitted this artifact>"
  },

  "class": {
    "value": "AUTHORED | GENERATED | DERIVED | EVIDENCE | CACHE | TEMPORARY",
    "resolved_by": "R-01..R-09 rule id, evaluated per §6's decoupled order",
    "resolution_confidence": "CLASSIFIED | UNRESOLVED",   // never a silent default — Constraint 2
    "classified_at_commit": "<sha>"
  },

  "authority": {
    "canonical_register": "<one of the 6, or 'CAAR-NATIVE' for classes with none — CAAR-1/CAAR-5>",
    "record_ref": "<key into that register>",
    "authority_confidence": "SINGLE | CONTESTED | NONE"    // CONTESTED is the AAR-1 case; must be representable, not silently picked
  },

  "owner": {
    "value": "<owning authority id, or 'UNRESOLVED'>",
    "resolution_method": "SELF_DECLARED | REGISTRY_FIELD | RATIFIED | NON_UCOS | UNRESOLVED",
    "ratified": false
  },

  "lifecycle": {
    "state": "<per-class enum, §1.2>",
    "legal_transitions": ["..."],
    "entered_at_commit": "<sha>"
  },

  "visibility": {
    "expected": "TRACKED | IGNORED | PER_SURFACE_DECLARATION",   // a property of class, never an input to it — Constraint 1
    "actual": "TRACKED | UNTRACKED | IGNORED",
    "reconciled": true                                            // false = actual != expected, §6
  },

  "certification": {
    "may_affect_certification": true,
    "state": "<CEP-005 Art VI state, once implemented — §7>",
    "proof_ref": "<evidence pointer>",
    "proof_population_scope": "<which of CAAR-3's three totals this claim is scoped to>"
  }
}
```

### 1.2 Per-class lifecycle enums

Directly closes `AV-3` (GENERATED's `lifecycle` field has exactly one observed value
across 345/345 entries — not yet a lifecycle):

| Class | Minimum legal states | Source |
|---|---|---|
| AUTHORED | `DRAFTED → REVIEWED → COMMITTED → SUPERSEDED \| DEPRECATED` | New — no register declares an AUTHORED lifecycle today |
| GENERATED | `REGENERATED → STALE → REGENERATED` (cyclic) `→ PRODUCER_REMOVED → ORPHANED` | Extends the single existing value (`AV-3`) |
| DERIVED | `DERIVED → INPUT_MISSING → BOOTSTRAP_REQUIRED → DERIVED` | New, modeled on `generated_inputs.bootstrap_gaps` (Step 4 §4) |
| EVIDENCE | `CAPTURED → RETAINED → EXPIRED` (never `REVISED` — evidence is historical, Step 3 §2.3) | New |
| CACHE | `WARM → STALE → EVICTED` | New — informational only, never gates anything (Step 4 §4) |
| TEMPORARY | `CREATED → CONSUMED \| ORPHANED` | New — `ORPHANED` is the case a crashed process leaves behind |

### 1.3 Schema validation rule

A CAAR record with `class.resolution_confidence != CLASSIFIED` **must** have every
downstream field (`authority`, `owner`, `lifecycle`, `certification`) set to its own
`UNRESOLVED`/`NONE` equivalent — never populated speculatively. This is Constraint 2
applied at the schema level: an unresolved upstream field cannot coexist with a resolved
downstream one, which is precisely the defect `AAR-1` found in the *opposite* direction
(agreement assumed where none was declared).

---

## 2. Identity Strategy

### 2.1 Why path cannot be the key

`CAAR-1` measured zero overlap between the two candidate identity schemes already in use
(`artifacts.json` `universal_id`+`path`, `generated-artifact-registry.json`
`artifact_id`+`canonical_path`) because they partition the repository by directory, not by
a shared minting rule. Path is additionally unstable under rename, and Step 3 §7.3
measured that no register treats `ORIGIN` as independent of registry membership. A path-
keyed CAAR would inherit both defects.

### 2.2 The minting rule

`caar_id` is minted **once**, at first observation, and never recomputed from content or
path:

```
caar_id = "CAAR-" + first16hex( sha256(
              class_at_mint_time + ":" + canonical_path_at_mint_time + ":" +
              minted_at_commit_sha ) )
```

This mirrors `id-ledger.json`'s own precedent — `allocate()` derives sequence numbers from
arrival order and a monotone cursor, never from content (Step 3 §3.5's mutation-boundary
citation) — extended with class and commit so that two different classes observed at the
same path (a real, measured case: `verify.sh` is `SOURCE`, contamination absorbs
`gate.py` at the same directory level, Step 3 §4.1) never collide.

### 2.3 Rename survival

`identity.path_history` is append-only. A rename is detected as: same `caar_id`, new
`current_path`, old path appended to `path_history` — never a new mint. Detection method is
deliberately **not specified here** (git rename-similarity heuristics, content hashing, and
manual declaration are all viable) because choosing one is an implementation decision, not
a design constraint; whichever is chosen must satisfy: **a rename never produces two CAAR
records for one artifact, and never silently merges two artifacts into one.**

### 2.4 Origin as a first-class field

`identity.origin` (`AUTHORED | PRODUCED | OBSERVED`) closes the gap Step 3 §7.3 named
explicitly: *"ORIGIN is not represented at all… an AUTHORED artifact and a GENERATED one
are distinguished only by registry membership."* Origin is set once, at mint time, from
whichever registry first admits the artifact, and is never re-derived — it answers "who or
what produced these bytes," which by definition cannot change without the artifact itself
being replaced (a new mint).

---

## 3. Registry Migration Strategy

### 3.1 CAAR is generated, not migrated-into

`CAAR-5` concluded that building CAAR is a repair, not a composition, because no join
exists among the six named registries. The corollary: **CAAR is not a destination the six
registries migrate their data into.** It is a **seventh, GENERATED artifact** — a projection
computed by reading the six sources and resolving their declared authority per §1.1's
`authority.canonical_register` field — that becomes authoritative *for lookups*, while the
six sources remain authoritative *for their own domain* until each is individually
deprecated (§4). This keeps CAAR inside the class model it defines: it must itself satisfy
`GENERATED`'s row in Step 6 §4 (a declared producer, a `canonical_path`, an `owner`, a
`certification_role`) rather than becoming a seventh ungoverned vocabulary — the exact
failure mode `AV-1` measured for the six that came before it.

### 3.2 Build order, mapped to Step 4 §5's nine stages

CAAR's composition script cannot run correctly before its inputs are trustworthy. The
order below is Step 4 §5 restated as a build dependency graph rather than a general
migration plan:

```
Stage 0   CAAR schema frozen (§1), identity minting rule frozen (§2)         — this design
Stage 1   R-01 repository-state repair (AV-6)                                — floor for everything
Stage 2   Exclusion register reachable; ignored_unclassified measured live   — floor for CACHE/TEMPORARY rows
Stage 3   AAR-1's three dual-classified prefixes given one declared class    — floor for EVIDENCE row
Stage 4   AAR-2's 48 unregistered ignored paths registered                   — floor for CACHE row completeness
Stage 5   00-BOOK GENERATED coverage closed (AV-3, 1,468 paths)              — floor for GENERATED row
Stage 6   R-09 implemented (BC-1)                                            — classify() stops returning ERROR
Stage 7   First CAAR build — a read-only script, output is the CAAR store, no source registry is written
Stage 8   CAAR build validated against §8's gates; iterate Stages 1–7 until gates pass
Stage 9   CAAR promoted from experimental to authoritative-for-lookups (§4)
```

Stage 7 is deliberately placed after Stages 1–6, not interleaved — building CAAR from
unrepaired sources would encode `AV-6`, `AAR-1`, and `AAR-2`'s contradictions as CAAR's own
data, which is worse than not having CAAR, because it would present contradictions with
the appearance of resolution.

### 3.3 Conflict resolution rule for `AAR-1`'s dual-classified prefixes

Until Stage 3 lands, CAAR's build script must **not** guess between V2
(`exclusion-register.json`) and V4 (`evidence-universe.json`) for
`00-MASTER/**/evidence/`, `.runtime/`, and `coverage.xml`/`.coverage*`. Per Constraint 2,
these three prefixes' CAAR records carry `authority.authority_confidence: CONTESTED` and
`class.resolution_confidence: UNRESOLVED` until a declared precedence exists — visible and
queryable as contested, never silently resolved to whichever register the script happened
to read first.

---

## 4. Backward Compatibility Strategy

### 4.1 CAAR is additive, never a replacement, until Stage 9

`verify.sh`, `UCOS-RIB-001`, `UCOS-AEE-001`, Phase 8/9, `register.sh`, and the UGA all read
today's six registries directly. None of them are modified by CAAR's introduction. CAAR is
built alongside them, read-only, and nothing consumes it until it has passed §8's gates.
This is the same posture Step 4 §5 Stage 7 already stated for the six-class model generally
("adoption is a distinct owner act, not implied by any stage completing") — extended here
to the schema itself.

### 4.2 Dual-read period

Once Stage 9 is reached for a given class (§1.2's per-class enums, migrated one class at a
time — GENERATED first, since its source registry is most complete per Step 6 §3.6), a
consumer may read CAAR **in addition to** its existing registry read, compare the two, and
log — never act on — a mismatch. This period has no fixed duration; it ends per-class when
mismatch logging shows zero divergence over a declared observation window (an
implementation decision, not fixed here).

### 4.3 No existing register is deprecated by this design

Deprecating `exclusion-register.json`, `generated-artifact-registry.json`, etc. is
explicitly **out of scope**. §3.1 keeps them as CAAR's declared sources of truth per class
indefinitely; CAAR's own `authority.canonical_register` field exists specifically so that
provenance to the original register is never lost. A future decision to deprecate a source
register is a distinct owner act with its own migration design, not implied here.

---

## 5. Ownership Resolution Strategy

### 5.1 Resolution order, fail-closed at every step (Constraint 3)

```
1. RATIFIED     — ucos-ownership-declarations.json assignments[key] exists   → owner = that value
2. REGISTRY     — generated-artifact-registry.json owner/validation_owner,
                   populated and non-constant for this artifact              → owner = that value,
                                                                                 resolution_method = REGISTRY_FIELD
3. SELF_DECLARED — artifact's own Authority/Deciders field (AUTHORED classes) → owner = that value,
                                                                                 resolution_method = SELF_DECLARED,
                                                                                 UNVERIFIED flag set (AAT-2)
4. NON_UCOS      — exclusion-register.json owner field names a tool, not a
                    UCOS authority (CPython, pytest, ruff, mypy, ...)         → owner = that value,
                                                                                 resolution_method = NON_UCOS,
                                                                                 excluded from ownership-coverage metrics
5. UNRESOLVED    — none of the above                                         → owner = UNRESOLVED, never fabricated
```

Step 1 outranks Step 2 because ratification is a constitutional act (`CEP-009`); Step 2
outranks Step 3 because a registry field, even where unverified, is at least structured
data rather than free text. `CAAR-2`'s finding — that `artifacts.json`'s owner field is a
single constant across 1,461 entries — is handled by treating a field with exactly one
distinct value across N>1 records as **not populated** for resolution purposes (§8.4's
validation gate makes this detection automatic rather than requiring a human to notice it
the way Step 3 §3.6 did).

### 5.2 Closing the `AAT-2` self-declaration gap

`SELF_DECLARED` resolutions carry an `UNVERIFIED` flag permanently until either (a) a
ratifying authority confirms them via the `RATIFIED` path, promoting them to Step 1, or (b)
an owner-conflict check (§8.5) finds no register disputes them over N observation windows,
at which point they may be promoted to a new `RESOLUTION_METHOD: SELF_DECLARED_STABLE` —
never silently to `RATIFIED`, which remains exclusively a constitutional act.

### 5.3 Non-UCOS owners are a first-class outcome, not a gap

`AAT-3` measured that CACHE and TEMPORARY resolve to owners (CPython, pytest, ruff, mypy,
setuptools) outside UCOS's ownership universe **by design**. CAAR's ownership-coverage
metric (§8) must exclude `NON_UCOS`-resolved records from its denominator entirely, rather
than counting them as unresolved. This is the single largest correction available: Step 3
§3.5 measured 391/542 unresolved without this exclusion; a coverage metric that correctly
excludes non-UCOS owners changes the denominator, not by fabricating numerators.

---

## 6. Visibility Reconciliation Strategy

### 6.1 Visibility is computed after class, never before (Constraint 1)

CAAR's `visibility.expected` field is a **pure function of `class.value`**, declared once
per class (§1.2's table implies the same per-class declaration applies to visibility):

| Class | Expected visibility | Source |
|---|---|---|
| AUTHORED | TRACKED | "loss is permanent," Step 3 §2.3 |
| GENERATED | TRACKED, if the producer's output is required for reproducibility beyond bootstrap; else IGNORED per producer declaration | Resolves the PORTAL contradiction (`AV-1` §2.2 item 2) by making the choice a declared per-producer field instead of an implicit, disagreeing default |
| DERIVED | IGNORED (untracked by design, Step 4 §4) | `generated_inputs[].tracked: false`, measured explicit |
| EVIDENCE | Per-surface declaration in the (reconciled, post-`AAR-1`) authority record | `evidence-universe.json` retention field |
| CACHE | IGNORED, always | Step 3 §2.3 definition |
| TEMPORARY | IGNORED, always | Step 3 §2.3 definition |

### 6.2 Reconciliation, not silent absorption

`visibility.reconciled = (actual == expected)`. A mismatch is **recorded, not corrected and
not hidden** — this is the direct fix for `AV-6`'s mechanism: today, a mismatch (an
AUTHORED file that is untracked, a GENERATED PORTAL page that is untracked) is invisible
because `R-01` reclassifies the artifact rather than flagging the visibility gap. Under
CAAR, `gate.py` (AUTHORED, untracked) keeps `class.value = AUTHORED` and gets
`visibility.reconciled = false` — the defect becomes queryable instead of disappearing
into `REPOSITORY_STATE`.

### 6.3 Closing `AAR-2`'s 48 unregistered-ignored paths

An ignored path with no CAAR record at all (not merely `reconciled: false`, but absent
entirely) is a distinct, worse condition — `class.resolution_confidence: UNRESOLVED` with
no authority record candidate. `.ucos-verification-evidence/` (46 files) and `.ucos/*.json`
(2 files) fall here today. The reconciliation job's first pass must enumerate these
explicitly as a named backlog, not merge them into the general `AV-8`/`AV-6` mismatch
count, because closing them requires a new exclusion-register or evidence-universe entry
(§3.2 Stage 4), not a reclassification.

---

## 7. Certification Integration Strategy

### 7.1 One-directional read (Constraint 4)

`CEP-005`'s certification chain — once implemented or formally superseded (`AV-5`) — reads
`certification.state`, `certification.may_affect_certification`, and
`certification.proof_population_scope` from CAAR. **No certification computation writes
back into `class`, `authority`, `owner`, `lifecycle`, or `visibility`.** This closes `AV-8`
by construction: today, `may_affect_certification: true` can be declared on an untracked
surface with no visibility gate; under CAAR, `visibility.reconciled` is computed
independently of `certification`, so a certification decision can never retroactively
change what visibility state was expected.

### 7.2 Resolving `CAAR-3`'s three population totals

Certification integration cannot proceed while "the repository's artifacts" means three
different things (1,233 certified scope / 1,461 corpus-registered / 6,188 tracked).
`certification.proof_population_scope` makes the scope **explicit per claim** rather than
implicit per register: a certification statement names which of the three (or a fourth,
CAAR's own total, once Stage 9 is reached) it is scoped to. This does not reconcile the
three totals — that remains an owner act (Step 6 §7.2) — it makes every future
certification claim state its scope so the next determination does not have to
re-discover the ambiguity `CAAR-3` measured.

### 7.3 Vocabulary reconciliation is a precondition, not a CAAR feature

`AV-5`'s four disagreeing vocabularies (`CEP-005`'s declared 8 states, two code enums of 2
and 3 members, and `certification.json`'s domain-verdict field) must be reconciled to one
before `certification.state` can be populated meaningfully. CAAR's schema (§1.1) declares
the field as `"<CEP-005 Art VI state, once implemented>"` deliberately open — this design
does not pick a winning vocabulary, because that choice requires certification authority
(Step 4 §6), not implementation authority.

---

## 8. Validation Gates

Each gate below is new — none exists in the repository today — and each closes exactly one
measured finding by making the defect it names impossible to pass silently.

| # | Gate | Fails when | Closes |
|---|---|---|---|
| 8.1 | **No visibility-before-class** | Any rule resolving `class.value` reads `tracked`/`ignored` state before every non-visibility rule has been tried | `AV-6` |
| 8.2 | **No silent default** | Any CAAR record has a populated downstream field alongside an `UNRESOLVED`/`CONTESTED` upstream field (Constraint 2, §1.3) | Step 3 §7.2 Rule 2 |
| 8.3 | **Authority contest detection** | Two source registries declare different classes for the same path with no declared precedence between them | `AAR-1` |
| 8.4 | **Degenerate-field detection** | A registry field has exactly one distinct value across N>1 records and is being read as if it discriminates (e.g. a constant "owner") | `CAAR-2`, and generalizes `AV-3`'s "4 of 18 fields are constants" |
| 8.5 | **Owner-conflict check** | A `SELF_DECLARED` owner is disputed by any registry field for the same artifact | `AAT-2` |
| 8.6 | **Live ignored-coverage measurement** | `ignored_unclassified` computed against the actual `.gitignore`/working-tree population diverges from the exclusion register's self-reported value | `AAR-2`, re-confirms `OB-1`'s pattern |
| 8.7 | **Population-scope declaration** | A certification claim has no `proof_population_scope` set | `CAAR-3` |
| 8.8 | **Non-UCOS exclusion** | An ownership-coverage metric counts a `NON_UCOS`-resolved record in its denominator | `AAT-3` |
| 8.9 | **CAAR self-conformance** | CAAR's own store fails the same six-column check (source/owner/registry/visibility/certification/lifecycle) it would apply to any other GENERATED artifact | §3.1 — CAAR must not become a seventh ungoverned vocabulary |
| 8.10 | **Ephemeral-population exclusion** | Any readiness or coverage denominator includes CACHE/ENVIRONMENT-classed records without an explicit inclusion declaration | `AAR-4` |

All ten gates are **observational** at Stages 7–8 (§3.2) — they report, they do not block
any existing pipeline, because nothing existing yet depends on CAAR (§4.1). A gate is
promoted to blocking only as part of the per-class Stage 9 promotion for that class, and
only by owner authority for the consuming pipeline.

---

## 9. Rollback Strategy

### 9.1 Rollback is structurally cheap by design

Because CAAR is additive-only through Stage 8 and dual-read-only through early Stage 9
(§4.1–4.2), rollback at any point before a consumer is switched to CAAR-only reading is:
**delete the CAAR store; no source registry was ever written.** This is the direct benefit
of §3.1's decision to make CAAR a GENERATED projection rather than a migration target — a
GENERATED artifact's defining property (Step 3 §2.3) is that it is reproducible from
declared inputs, so deleting it loses nothing that was not already present in the six
source registries.

### 9.2 Per-class rollback after Stage 9

Once a class's consumers read CAAR as authoritative (post dual-read observation window,
§4.2), rollback for that class specifically is: revert the consumer's read path to the
original registry, which still exists and was never deprecated (§4.3). Rollback is
per-class, not global — a regression discovered in EVIDENCE's CAAR records (plausible,
given `AAR-1`'s unresolved contests) does not require rolling back GENERATED or AUTHORED,
which may have independently passed their own Stage 9 promotion.

### 9.3 Versioned snapshots

`caar.schema.version` (§1.1) is bumped on any schema change; a build failure at Stage 7/8
(any gate in §8 regresses after previously passing) halts promotion of the new build and
leaves the last-passing CAAR snapshot as the active one — the same fixed-point discipline
Step 8 (Phase 8, cited via `mutation-governance-boundary.json` in Step 5 §2.1's authority
table) already applies to canonical-chain idempotence, extended to CAAR specifically.

### 9.4 No rollback scenario touches certification

Because certification reads CAAR one-directionally (§7.1, Constraint 4), rolling CAAR back
never requires rolling back a certification decision — a certification computed while a
now-rolled-back CAAR build was active remains a historical fact about what CAAR said at
that time (`certification.proof_ref`, §1.1), consistent with `EV-EXECUTION`'s definition of
evidence as historical and non-revisable (Step 3 §3.7, evidence class `EXECUTION`).

---

## 10. Implementation Sequence

Synthesizes §3.2's build order with §8's gates and §4's compatibility posture into one
ordered sequence, each stage naming its authority requirement per Step 4 §6's matrix:

| Stage | Action | Authority required | Exit criterion |
|---|---|---|---|
| **0** | Freeze CAAR schema (§1) and identity minting rule (§2) as an owner-adopted design | Owner authority (mutation governance owner) | Design adopted — this artifact alone does not adopt it (header) |
| **1** | Repair `_r01_repository_state` to consult the exclusion register (`AV-6`) | Implementation authority | `R-01` no longer claims a declared-excluded or declared-authored path |
| **2** | Make `ignored_unclassified` a live measurement (`AAR-2`, gate 8.6) | Implementation authority | Metric diverges from 0 exactly when unregistered ignored paths exist |
| **3** | Declare precedence for `AAR-1`'s three dual-classified prefixes | Owner authority (exclusion-register owner + evidence-universe owner, jointly, per Step 5 §7) | Zero `CONTESTED` records remain for those three prefixes |
| **4** | Register `.ucos-verification-evidence/` and `.ucos/*.json` (`AAR-2`'s 48 paths) | Owner authority (exclusion-register owner) | Gate 8.6 shows 0 divergence |
| **5** | Register the 1,468 `00-BOOK` GENERATED paths (`AV-3`) | Owner authority (`00-BOOK` + generated-artifact-registry owner) | `generated-artifact-registry.json` coverage includes `00-BOOK` |
| **6** | Implement `R-09 GOVERNED_ANALYSIS` (BC-1) | Implementation authority | `classify()` stops returning `ERROR` |
| **7** | Build CAAR (read-only script; §3.1–3.2) | Implementation authority | CAAR store exists, sourced from Stages 1–6's repaired registries |
| **8** | Validate against all ten gates (§8), observational mode | Implementation authority | Gates 8.1–8.10 report; failures logged, not blocking |
| **9a** | Promote GENERATED class to CAAR-authoritative (most complete source register, Step 6 §3.6) | Owner authority (generated-artifact-registry owner) | Dual-read shows 0 divergence over the declared window |
| **9b–9f** | Repeat 9a per remaining class (AUTHORED, DERIVED, EVIDENCE, CACHE, TEMPORARY), independently ordered by owner readiness | Owner authority, per class | Same, per class |
| **10** | Implement or formally supersede `CEP-005` Art VI (`AV-5`); wire certification to read CAAR one-directionally (§7) | Certification authority + constitutional authority (if superseding) | One certification vocabulary; `certification.proof_population_scope` populated on every claim |
| **11** | Reconcile `CAAR-3`'s three population totals into one declared relationship | Owner authority + certification authority, jointly | A register states which of {1,233 / 1,461 / 6,188 / CAAR total} is canonical and how the others relate |

Stage 0 is this artifact's own exit condition — nothing after it may begin under this
design's authority, because this design has none (header). Stages 1–6 are Step 4 §5's
migration path, unchanged. Stages 7–11 are new, specific to building and adopting CAAR
itself.

---

## 11. Traceability Matrix — Every Finding, Where It Is Addressed

| Finding | Severity | Addressed in |
|---|---|---|
| `AV-1` | HIGH | §3.1 (CAAR as 7th vocabulary risk), §6.1 (PORTAL visibility contradiction) |
| `AV-2` | HIGH | §1.2 (lifecycle enums for all 6 classes, including the 3 V1 has none for) |
| `AV-3` | MEDIUM | §1.2, §3.2 Stage 5, §8.4 |
| `AV-4` | HIGH | §5.1, §5.2 |
| `AV-5` | CRITICAL | §7.3, §10 Stage 10 |
| `AV-6` | CRITICAL | Constraint 1, §6.1, §6.2, §10 Stage 1 |
| `AV-7` | MEDIUM | §3.2 Stage 6 (R-09), indirectly — not independently re-addressed |
| `AV-8` | MEDIUM | Constraint 4, §7.1 |
| `AV-9` | LOW/structural | §8 (all ten gates are the bidirectional checks `AV-9` found absent) |
| `AAT-1` | CRITICAL | §1.1 (schema unifies the 5 columns), §3.1 |
| `AAT-2` | HIGH | §5.1 Step 3, §5.2, §8.5 |
| `AAT-3` | HIGH | §5.1 Step 4, §5.3, §8.8 |
| `AAT-4` | MEDIUM | §8.10 |
| `AAT-5` | HIGH | §1.1 `authority.record_ref` (structured pointer replaces free text) |
| `AAR-1` | CRITICAL | §3.3, §6.3, §8.3, §10 Stage 3 |
| `AAR-2` | HIGH | §6.3, §8.6, §10 Stages 2 & 4 |
| `AAR-3` | HIGH | §1.1 `authority` object, §3.1 |
| `AAR-4` | MEDIUM | §8.10 |
| `AAR-5` | LOW/structural | §8.9 — the same self-limitation is made a permanent gate rather than a one-time caveat |
| `CAAR-1` | CRITICAL | §2 (entire identity strategy exists because of this finding) |
| `CAAR-2` | HIGH | §5.1 Step-1 exclusion rule, §8.4 |
| `CAAR-3` | HIGH | §7.2, §10 Stage 11 |
| `CAAR-4` | MEDIUM | §2.2 (minting rule requires no prior identity, closing the "unkeyed store" gap) |
| `CAAR-5` | LOW/structural | §3.1 (the composability verdict is this design's starting premise) |

**26 of 26 findings traced.** None is closed by this artifact (header) — traceability
means every design decision above answers a specific, numbered, previously measured
defect, not that the defect no longer exists.

---

## 12. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-CANONICAL-ARTIFACT-AUTHORITY-RECORD-IMPLEMENTATION-DESIGN.md` |
| Required sections present | ✅ all 10 directive sections (§1–§10), plus traceability (§11) and verification (§12) |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Design only — implementation performed | ✅ **0** |
| Code changes | ✅ **0** |
| Registry writes | ✅ **0** — 6 registries and 2 registry-adjacent stores referenced, none written |
| Certification changes | ✅ **0** |
| Commits | ✅ **0** |
| Tracked modifications unchanged | ✅ identical set to session start |
| Only new artifact added | ✅ the single delta is this file |
| Findings closed | ✅ **0** — traced, not resolved |

---

*This design proposal modified no file, changed no code or configuration, wrote to no
registry, altered no certification, committed nothing, and created no schema, identity,
class, owner, lifecycle, visibility state, or certification of record. Every design
decision in §1–§10 cites the specific BC-6 finding it addresses (§11); no requirement
above was introduced without a traceable source in Steps 1–6's 26 findings. This artifact
has no authority (header) — Stage 0 of §10 names the first act any part of this design
requires before implementation may begin, and that act belongs to the mutation governance
owner, not to this determination. The single repository mutation is the creation of this
file.*

**END DESIGN — BC-6 IMPLEMENTATION PREPARATION COMPLETE · NO STAGE OF §10 EXECUTED · STOPPED AFTER ARTIFACT CREATION.**
