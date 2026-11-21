# UCOS Ω∞ — UGA REALITY SYNCHRONIZATION DETERMINATION

**Is `UCOS-UGA-001` a complete and reliable canonical object authority? — the foundation dependency the CAAR Architecture Correction created**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-UGA-REALITY-SYNCHRONIZATION-DETERMINATION.md` |
| Authority | **NONE — DERIVED TRUTH.** Creates no identifier, class, owner, lifecycle, registry or certification. Synchronizes nothing. Authorizes nothing. A verdict below is a measurement, not a permission. |
| Mode | ANALYSIS ONLY · **NO CODE CHANGE · NO REGISTRY CHANGE · NO CERTIFICATION CHANGE · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subject | `UCOS-UGA-001` — `00-MASTER/UCOS-UGA-001/` (declaration, 95 KB engine, 10 emitted surfaces) and its ledger maps in `00-BOOK/DATA/id-ledger.json` |
| Why this determination exists | The CAAR Architecture Correction made CAAR a **projection over UGA** rather than a seventh register (`ACD-2`). That converts UGA from an unread sibling into a **load-bearing foundation**, and a foundation that has never been measured against reality cannot carry one. |
| Method | Direct measurement at one commit: set operations over the ledger's three planes, UGA's ten surfaces, `git ls-files -z`, `artifacts.json` and `generated-artifact-registry.json`, at **both HEAD and the working tree**; plus one read-only execution of the declared non-mutating gate (`uga_engine.py gate`) |
| Findings raised | **11** (`URS-1`…`URS-11`) · 3 CRITICAL · 3 HIGH · 4 MEDIUM · 1 LOW |
| Predecessor measurement corrected | **1** — `ACD-5`'s orphan/missing figures (§1.4) |
| Overall verdict | **NOT SYNCHRONIZED · CONDITIONALLY QUALIFIED.** UGA's identity discipline is sound and measurably exact; its population, its gate state, and its certification surface are not synchronized with the repository. It is the right foundation and it is not currently a reliable one. |

---

## 1. Objective, Method, Limitation, and One Correction

### 1.1 The question

The CAAR Architecture Correction found that five of CAAR's seven columns are already
produced by `UCOS-UGA-001` over 6,145 objects, gated blocking in `verify.sh`, and concluded
that CAAR should extend UGA rather than replace it. That conclusion is only as good as UGA
is. This determination asks the question the correction created and did not answer:

> **Is UGA complete (does it know about everything that exists) and reliable (is what it
> says true, and does it stay true)?**

Ten dimensions are measured. Each is graded and given a finding where one exists.

### 1.2 Method

Every quantity below is computed at this baseline. Two disciplines are applied that prior
artifacts in this chain did not:

1. **HEAD and working tree are measured separately.** Five determinations in this chain
   reported figures without stating which of the two they came from. `URS-11` (§20) shows that the
   single most-cited discrepancy in the entire BC-6 corpus is an artifact of that omission.
2. **`git ls-files -z` is used, never newline-split output.** §1.4 explains why this
   matters and corrects a predecessor.

The gate was executed once, in its declared read-only form (`cmd_gate` calls
`build(mint=False)`; `_dump` is reached only from `cmd_run`). Surface mtimes and
`git status` were compared before and after: unchanged (§21).

### 1.3 Standing limitation

`classify()` still returns `ERROR`; `R-09` remains unimplemented in the classifier. Nothing
below is a classification, ownership, or certification of record.

### 1.4 Correction to a predecessor measurement

**`ACD-5`, as raised in the CAAR Architecture Correction, reported wrong figures.** It
stated *"UGA is stale at HEAD: 117 registered paths untracked, 160 tracked paths
unregistered."* Both numbers are wrong. The cause was mine, not UGA's: `git ls-files`
without `-z` renders non-ASCII paths in C-quoted form, and this repository holds exactly
**117** such paths (every `UCOS-Ω∞-*` file under `00-BOOK/CONTROL-TOWER/` and elsewhere).
Comparing quoted strings against UGA's unquoted paths produced 117 false orphans and
inflated the missing count.

Measured correctly, with `-z`:

```
git ls-files -z                              6,188
UGA 02-UNIVERSAL-OBJECT-REGISTRY entries     6,145
tracked NOT in registry  (MISSING)              43
registry NOT tracked     (ORPHAN)                0      ← not 117
```

**UGA has zero orphans.** The engine itself uses `-z` correctly (`uga_engine.py:175`), so
the defect was in the measurement, not the measured. `ACD-5`'s substance — that UGA's
emitted surfaces are not synchronized with the repository — survives and is confirmed here
by different evidence (§3, §5, §11). Its numbers do not, and are superseded by this
determination's.

---

## 2. Current State

### 2.1 What UGA is

A programme at `00-MASTER/UCOS-UGA-001/` that brings every version-controlled object that
is *not* a corpus document under the same identity, ownership, lifecycle and evidence
control the corpus already has. It mints from the shared `id-ledger.json` `by_object` map
using the corpus's own `category_seq` counter, consumes no page range, and emits ten
surfaces. Its gate is `verify.sh` **Stage 6b**, and the stage's own comment states the
intent precisely: *"a new engine, test or config file can no longer enter the repository
unidentified, unowned, unregistered or unaudited."*

### 2.2 Emitted surfaces, as they stand

| Surface | Content | Count | Last written |
|---|---|---|---|
| `00-EXISTENCE-INVENTORY.json` | objects | 6,145 | 2026-08-23 16:54 |
| `01-EXECUTABLE-OBJECT-REGISTRY.json` | entries | 4,912 | 2026-08-23 16:54 |
| `02-UNIVERSAL-OBJECT-REGISTRY.json` | entries | **6,145** | 2026-08-23 16:54 |
| `03-AUDIT-UNIVERSE.json` | events | 4,914 | 2026-08-23 16:54 |
| `04-RELATIONSHIP-GRAPH.json` | relationships (6 kinds) | 34,872 | 2026-08-23 16:54 |
| `05-GOVERNANCE-INVARIANTS.json` | invariants, **29 of 29 PASS** | 29 | 2026-08-23 16:54 |
| `06-SELF-OBSERVATION.json` | observation + analysis + proposals | — | 2026-08-23 16:54 |
| `07-CERTIFICATION.json` | **`verdict: CERTIFIED`**, 5 digests | — | 2026-08-23 16:54 |
| `08-OBSERVATION-REGISTRY.json` | observations | 7 | 2026-08-12 13:54 |
| `uga-declaration.json` (input) | 7 object classes, 3 lifecycle states, 10+7 invariants | — | 2026-08-12 17:18 |

### 2.3 The registry record

```jsonc
{ "universal_id": "UCOS-CONFIG-000001", "path": ".github/workflows/acee-gate.yml",
  "object_class": "CONFIGURATION_OBJECT", "owner": ".github/workflows",
  "producer": "HUMAN_AUTHORED", "identity_authority": "UCOS-UGA-001",
  "lifecycle": "AUTHORED", "dependencies": [], "produces": [],
  "evidence_class": "VALIDATION", "evidence_boundary": "NON_CANONICAL",
  "validation_contract": "UCOS-UGA-001 §UGA-INV-01..10",
  "certification_status": "GOVERNED", "content_hash": "e6e97ec4…",
  "first_seen": "commit:e98f59cd22e9" }
```

Measured field cardinality across all 6,145 entries:

| Field | Distinct | Field | Distinct |
|---|---|---|---|
| `universal_id` | 6,145 | `owner` | **276** |
| `object_class` | 7 | `producer` | 33 |
| `lifecycle` | **2** (of 3 declared) | `identity_authority` | 2 |
| `evidence_class` | **1** | `evidence_boundary` | **1** |
| `certification_status` | **1** | `content_hash` | 6,145 |

### 2.4 The three populations, at HEAD and in the working tree

This table is the key to §3.1 and to `URS-11`. It is the first time in this chain that the
figures are separated by where they were read.

| Register | At HEAD | Working tree | Delta |
|---|---|---|---|
| `git ls-files -z` | 6,188 | 6,188 | 0 |
| `artifacts.json` artifacts | **1,233** | **1,461** | **+228 (uncommitted)** |
| `id-ledger by_path` | 1,264 | 1,492 | +228 (uncommitted) |
| `id-ledger by_object` | 4,914 | 4,914 | **0** |
| `id-ledger by_observation` | 7 | 7 | 0 |
| UGA registry entries | 6,145 | 6,145 | 0 (surface is committed) |
| UGA `DOCUMENT_ARTIFACT` | 1,233 | 1,233 | 0 |

`00-BOOK/DATA/artifacts.json` and `00-BOOK/DATA/id-ledger.json` are **two of the 38 tracked
modifications** standing in the working tree at this baseline.

---

## 3. Dimension 1 — UGA Registry Completeness

**Verdict: NOT COMPLETE.**

### 3.1 Against the tracked population

```
tracked at HEAD                   6,188
UGA registry                      6,145
unregistered                         43   (0.69%)
```

All 43 entered version control on 2026-08-22, in five commits at or before HEAD
(`8dc9a812` ×32, `fb43383e` ×6, `299d48a9` ×3, `341bc907` ×1, `163e6f95` ×1). **UGA has not
been run since those commits landed.** The registry is not corrupt and is not internally
inconsistent — it is a correct snapshot of a population five commits old.

The 43 split cleanly by identity status, and the split is the whole diagnosis:

| Group | Count | Identity at HEAD | Identity in working tree | Why absent from UGA |
|---|---|---|---|---|
| Corpus documents | **36** | none | `by_path` (worktree-only registration) | Corpus registration ran *after* UGA's last run and is still uncommitted |
| Code objects | **7** | **none** | **none** | Never minted — UGA `run` not executed since they were committed |

The 7:

```
engine/ceu/context_binding.py
engine/tests/ceu/test_context_binding.py
engine/tests/context/test_req_28_extensibility.py
engine/tests/lineage/test_req_43_upeg_certification.py
engine/tests/uckp/test_phase_2_requirement_evolution.py
platform/repository_intelligence/mutation_class_extension.py
platform/tests/test_violation_4_mutation_extension.py
```

These are precisely the objects Stage 6b exists to catch — *"a new engine, test or config
file can no longer enter the repository unidentified"* — and they entered unidentified.

### 3.2 Against the untracked and ignored population

UGA's population is `git ls-files --cached`. It therefore does not reach, and makes no claim
about, the ignored and untracked population where `AV-6`, `AAR-1`, `AAR-2`, `AAT-3` and
`AAR-4` live — 308 untracked-and-un-ignored paths at this baseline, plus the ignored
population the exclusion register governs. **This is a declared scope boundary, not a
defect**, but it bounds what CAAR may claim from UGA: five of seven columns for the
*tracked* population only.

**`URS-4` (HIGH):** 43 tracked paths carry no UGA registry record at HEAD; 7 of them carry
no Universal ID in any ledger plane at HEAD or in the working tree. UGA's completeness claim
is true of the commit it last ran against, not of HEAD.

---

## 4. Dimension 2 — Filesystem-to-Object Alignment

**Verdict: ALIGNED IN DIRECTION, INCOMPLETE IN COVERAGE.**

```
tracked ∖ registry   (missing)      43
registry ∖ tracked   (orphan)        0
00-EXISTENCE-INVENTORY paths == 02-UNIVERSAL-OBJECT-REGISTRY paths   True
```

Zero orphans is a strong result and it is structural, not lucky: the registry is rebuilt
from the live `git ls-files` population on every run, so a path that leaves version control
cannot persist as a registry row. The inventory and the registry agree exactly on their path
sets, so UGA's own surfaces do not disagree with each other about what exists.

The alignment is therefore **one-directional**: everything UGA lists exists; not everything
that exists is listed. For a foundation that CAAR would query, that is the safer of the two
failure modes — a lookup never returns a phantom — but a coverage question (*"how many
objects are governed?"*) returns a number that is 43 short and does not say so.

---

## 5. Dimension 3 — Identity Alignment

**Verdict: EXACT — the strongest result in this determination.**

Every check run against the 6,145-entry registry and the ledger's three planes:

| Check | Result |
|---|---|
| Registry entries with a null `universal_id` | **0** of 6,145 |
| Duplicate `universal_id` within the registry | **0** |
| Duplicate identifiers across `by_path` ∪ `by_object` ∪ `by_observation` | **0** |
| Registry paths with no ledger entry | **0** |
| Registry `universal_id` ≠ ledger `universal_id` for the same path | **0** |
| `CAA-INV-04` `EXACTLY_ONE_IDENTITY_AUTHORITY` (live) | **PASS**, measured 6,413 |
| UGA `DOCUMENT_ARTIFACT` path set == HEAD `artifacts.json` path set | **True** (1,233 = 1,233) |

Identity minting, persistence, and non-reissue are working exactly as declared. The
`id_preservation` rule (*"Every identifier that existed before this binding exists after it,
unchanged"*) holds under measurement, and the last row is a notable positive: UGA's
document-class population is not approximately the corpus, it **is** the corpus, path for
path, at HEAD.

This result is what makes the CAAR Architecture Correction's §5 model viable. It is also
what makes §8's finding serious, because that finding is not about identifier integrity — it
is about how many identifiers one subject is entitled to.

---

## 6. Dimension 4 — Missing Objects

**Verdict: 43 MISSING · 7 STRUCTURALLY ANONYMOUS.**

Resolved against both ledger states (§3.1). The two groups need different acts:

| Group | Count | Act required | Authority |
|---|---|---|---|
| Corpus documents pending | 36 | Commit the standing `artifacts.json` / `id-ledger` modification, then re-run UGA | `REG-AUTO-001` (registration already performed, uncommitted) + implementation |
| Anonymous code objects | 7 | `uga_engine.py run` (mints into `by_object`) | Implementation authority |

The 7 are the only objects in the repository that are **tracked and have no Universal ID in
any plane, at HEAD or in the working tree**. They are the live violation set of `UGA-INV-01`.

**`URS-4`** (§3) covers this dimension; no separate finding is raised.

---

## 7. Dimension 5 — Orphan Objects

**Verdict: ZERO ORPHANS IN THE REGISTRY · TWO RETAINED-BUT-UNRECORDED IN THE LEDGER.**

The registry holds no path that version control does not carry (§4). The ledger, being
append-only, holds two `by_object` entries whose paths are no longer in the registry:

```
CURRENT-REPOSITORY-STATE.txt                                          UCOS-EXDOC-002463  EXCLUDED_DOCUMENT
.ucos-verification-evidence/ruff/9b37e2241144e4af…d201b1d.json        UCOS-DATAOBJ-000122  DATA_OBJECT
```

`06-SELF-OBSERVATION.json` records `retired_identities: 2`, so the engine measures them
correctly. They are **not** orphans in the defect sense — retention is required by
`id_preservation` and `IL-INF-07`, and the correct disposition of an identity whose path is
gone is exactly this: keep it, never reissue it.

The defect is that they have **no record anywhere in the registry**. The declaration
defines a `RETIRED` lifecycle state for precisely this condition, and no surface carries it
(§10). A consumer resolving `UCOS-EXDOC-002463` through the registry gets nothing; through
the ledger, an entry with no lifecycle.

The second row is independently notable: `.ucos-verification-evidence/` is one of `AAR-2`'s
48 unregistered *ignored* paths, and it holds a UGA-minted Universal ID. An identity was
minted for a path that has since left the version-controlled boundary UGA declares as its
scope — evidence that the boundary has been crossed at least once historically, and an
argument for `URS-5`'s remedy rather than against it.

---

## 8. Dimension 6 — Duplicate Identities

**Verdict: NO DUPLICATE IDENTIFIERS · 217 DUPLICATE IDENTITIES. The distinction is the finding.**

No identifier is issued twice (§5). But **217 paths hold two Universal IDs at once** — one
from the corpus plane, one from the object plane:

```
worktree  by_path ∩ by_object   217
HEAD      by_path ∩ by_object    25
```

Six of the 217, as they stand:

| Path | Corpus id (`by_path`) | UGA id (`by_object`) | Registry publishes |
|---|---|---|---|
| `00-MASTER/MCP-001-MASTER-CONTEXT.md` | `UCOS-MASTER-000015` | `UCOS-EXDOC-001457` | **`UCOS-EXDOC-001457`** |
| `00-MASTER/MCP-002-MASTER-STATE.md` | `UCOS-MASTER-000016` | `UCOS-EXDOC-001458` | **`UCOS-EXDOC-001458`** |
| `00-MASTER/MCP-003-MASTER-EXECUTION.md` | `UCOS-MASTER-000017` | `UCOS-EXDOC-001459` | **`UCOS-EXDOC-001459`** |
| `00-MASTER/MCP-004-MASTER-DECISIONS.md` | `UCOS-MASTER-000018` | `UCOS-EXDOC-001460` | **`UCOS-EXDOC-001460`** |
| `00-MASTER/MCP-005-MASTER-DASHBOARD.md` | `UCOS-MASTER-000019` | `UCOS-EXDOC-001461` | **`UCOS-EXDOC-001461`** |
| `00-MASTER/CHECKPOINTS/CKPT-2026-07-18-5874ede.md` | `UCOS-MASTER-000023` | `UCOS-EXDOC-001295` | **`UCOS-EXDOC-001295`** |

For all 217, the registry publishes the `by_object` identifier (217 of 217; the `by_path`
identifier is published for none). **Two consumers asking "what is this artifact's Universal
ID" get two different answers depending on which register they ask.** Their classes are
`EXCLUDED_DOCUMENT` (201) and `DATA_OBJECT` (16).

### 8.1 Mechanism

`classify_object` opens with `if rel in registered_docs: return "DOCUMENT_ARTIFACT"`, where
`registered_docs` is read from `artifacts.json`. A document not yet corpus-registered falls
through the rule chain to the unconditional terminal and becomes `EXCLUDED_DOCUMENT`, which
mints an `EXDOC` identity into `by_object`. When corpus registration later admits that same
document, `REG-AUTO-001` mints a **second**, `by_path` identity. UGA's `by_object` entry is
append-only and is retired only when the path leaves version control — which it has not — so
the first identity persists indefinitely, unreferenced and unretired.

### 8.2 The condition is growing, monotonically

`25 → 217` is not a static defect; it is the count as corpus registration proceeds. Every
document the corpus admits that UGA had previously absorbed as `EXCLUDED_DOCUMENT` adds one.
Projected against the working tree's inputs, the next `uga_engine.py run` would reclassify
**192** of the 217 from `EXCLUDED_DOCUMENT` to `DOCUMENT_ARTIFACT`, switching the published
identifier from the `EXDOC` id to the corpus id and **orphaning 192 `EXDOC` identities
in place** — retained by `id_preservation`, referenced by nothing, retired by nothing.

### 8.3 Why no invariant catches it

`CAA-INV-04` passes because it measures what it was written to measure: that the
ledger→URN derivation is total and collision-free over every recorded id. It does not ask
whether one *subject* holds two ids. `UGA-INV-01` asks whether every object has *an*
identity, not whether it has *one*. **The condition falls in the gap between "every object
has an id" and "every id is unique" — neither of which is "every object has exactly one
id."**

**`URS-2` (CRITICAL):** 217 paths hold two Universal IDs from two authorities, the registry
publishes the UGA-minted one for all 217, no invariant measures the condition, and the count
grows by one for every corpus registration of a previously-absorbed document. For a
foundation whose value to CAAR is *"the one identity a subject already holds"* (Architecture
Correction §5.1, rule I-2), this is the defect that most directly undermines the dependency.

---

## 9. Dimension 7 — Ownership Alignment

**Verdict: PARTIALLY ALIGNED — one strong owner function, three incompatible value spaces, zero ratified assignments.**

### 9.1 UGA's owner field is the best in the repository

| Register | Populated | Distinct | Usable |
|---|---|---|---|
| `ucos-ownership-declarations.json` `assignments` | 0 | 0 | No — empty (re-verified, fifth independent read) |
| `artifacts.json` `owner` | 1,461 / 1,461 | **1** (`UCOS-PROGRAM-CUSTODIAN`) | No — degenerate (`CAAR-2`) |
| `generated-artifact-registry.json` `owner` | 345 / 345 | 32 | Yes, 345 paths |
| **UGA `owner`** | **6,145 / 6,145** | **276** | **Yes, 6,145 paths** |

`derive_owner` is a declared TOTAL function whose last rule is unconditional, so it cannot
return null — which is why `UGA-INV-02` passes at 6,188 even where 7 objects have no
identity. Ownership is derived from path shape, and the declaration says so plainly:
*"Operational Memory is organised by programme; the programme directory IS the owner."*

### 9.2 Agreement where the populations overlap

Over the 345 paths UGA and the generated-artifact registry both carry:

```
owner AGREES     334   (96.8%)
owner DISAGREES   11
```

All 11 disagreements are the same shape — UGA derives the directory, the register declares
the programme:

| Path | UGA | GAR |
|---|---|---|
| `intelligence/UCOS-IMP-BASELINE-001.evidence.json` | `intelligence` | `UCOS-RIE-001` |
| `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | `intelligence` | `UCOS-RIE-001` |
| *(9 more, all `intelligence/*`)* | `intelligence` | `UCOS-RIE-001` |

`derive_owner`'s `<top>/<file>` rule yields a directory name where a declared owner exists.
This is a derivation losing to a declaration — exactly the precedence the CAAR Architecture
Correction's §9.1 six-tier order encodes (registry above derived), and evidence that the
tiering is necessary rather than theoretical.

### 9.3 Three incompatible owner value spaces

```
UGA owners ∩ GAR owners            31 of 32   (shared vocabulary)
UGA owners ∩ artifacts.json owners  0         (no shared token at all)
ratified assignments                0
```

UGA's 276 owners are a mix of programme identifiers (`UCOS-USIS-WAVE2`, `UCOS-UKB-TOOLING`)
and directory paths (`00-BOOK/PORTAL` with 1,240 objects, `platform/tests` with 345,
`service/_evidence` with 136). `artifacts.json`'s single constant belongs to neither space.
**No register declares the relationship between an owner-as-directory and an
owner-as-programme**, so ownership coverage cannot be computed across the three without a
declared mapping.

**`URS-9` (MEDIUM):** UGA's owner field is total, non-degenerate and 96.8%-consistent with
the one other populated register, but the three owner value spaces in use (directory path,
programme identifier, repository constant) are unreconciled, and 11 measured disagreements
resolve a declared owner to a derived directory.

---

## 10. Dimension 8 — Lifecycle Alignment

**Verdict: NOT ALIGNED — one declared state is structurally unemittable, and a downstream consumer would reject it if it were emitted.**

### 10.1 The declaration and the data disagree

`uga-declaration.json` declares three lifecycle states:

| State | Definition | Registry occurrences |
|---|---|---|
| `AUTHORED` | *"Hand-written source. Its bytes are a human decision."* | 5,800 |
| `GENERATED` | *"Emitted by a declared producer."* | 345 |
| **`RETIRED`** | *"Previously minted an identity, no longer carried by version control. Identity is retained (append-only) and never reissued."* | **0** |

`RETIRED` has zero occurrences and cannot acquire one. The registry is built from
`epoch0_discovery` over the **live** path list; `epoch1_identity` computes a `retired` list
by set difference and returns it as a *report* — surfaced as `retired_identities: 2` in
`06-SELF-OBSERVATION.json` — but no retired object is ever an entry. **The state is declared,
measured, reported, and unemittable.** This is `AV-3`'s pattern (a lifecycle field with one
observed value) in a sharper form: a lifecycle whose third state has no representation.

### 10.2 A downstream consumer would fail closed on it

`engine/uckp/uga_projection.py` projects UGA entries into UCKO objects and holds:

```python
_LIFECYCLE_MAP: dict[str, str] = { "AUTHORED": "draft", "GENERATED": "implemented" }
...
if lifecycle not in _LIFECYCLE_MAP:
    raise UnrecognisedUGAValueError(f"{entry['path']}: unmapped UGA lifecycle {lifecycle!r}")
```

`RETIRED` is unmapped. **If UGA emitted the state its own declaration defines, the UCKP
projection would raise.** The class `UnrecognisedUGAValueError` documents this as deliberate
(*"Fails closed rather than guessing"*), which is correct discipline — and which makes the
gap concrete: emitting `RETIRED` is not a one-file change, and the declaration promises a
state the system cannot currently carry.

### 10.3 Lifecycle is also a two-axis question UGA does not answer

`constitutional-authority-alignment.json` `lifecycle_resolution` declares the model
`ORTHOGONAL_AXES` with two owners — `UCL-000001` (PROCESS, 45 stages, artifacts in scope)
and `KNOWLEDGE-LIFECYCLE` (STATE, 10 stages, knowledge objects only) — and warns that
neither is a projection of the other. UGA's three states cite neither axis. Under
`UCKP-ART-03` this is a third vocabulary over a subject two owners already hold, and it is
the same defect the CAAR Architecture Correction raised against CAAR's own §1.2 (`CIR-5`) —
present in the foundation as well as in the design built on it.

**`URS-5` (HIGH):** `RETIRED` is declared, measured (2 identities) and structurally
unemittable; the registry carries 2 of 3 declared states; and `engine/uckp/uga_projection.py`
would raise `UnrecognisedUGAValueError` if the third were emitted. UGA's lifecycle
vocabulary additionally cites neither declared lifecycle axis owner.

---

## 11. Dimension 9 — Certification Alignment

**Verdict: NOT ALIGNED — the certification surface asserts a clean verdict that the live gate contradicts.**

### 11.1 The committed evidence and the live measurement disagree

`05-GOVERNANCE-INVARIANTS.json`, committed at HEAD, records **29 of 29 invariants PASS**,
measured over 6,145 objects. The gate, executed at this baseline over the live population,
reports:

```
[FAIL] UGA-INV-01  EVERY_OBJECT_HAS_UNIVERSAL_ID   (violations=7, measured=6188)
[FAIL] UGA-INV-10  EVERY_MUTATION_HAS_AUDIT_EVENT  (violations=7, measured=4727)
  ANONYMOUS OBJECTS: 7 — run `uga_engine.py run`
GATE FAILED — 2 blocking invariant(s).
```

The other 27 pass. The two failures are the same 7 objects, seen twice: unminted (`INV-01`)
and therefore unaudited (`INV-10`).

The measurement denominators explain the whole divergence and confirm both readings are
internally correct:

| | Committed surface | Live gate | Why |
|---|---|---|---|
| `UGA-INV-01` measured | 6,145 | **6,188** | Surface counts its own snapshot; gate counts `git ls-files` |
| `UGA-INV-10` measured | 4,912 | **4,727** | `6,145 − 1,233` (HEAD corpus) vs `6,188 − 1,461` (worktree corpus) |

**`URS-3` (CRITICAL):** `05-GOVERNANCE-INVARIANTS.json` asserts 29 of 29 PASS over a
population of 6,145 while the live gate over 6,188 reports 2 blocking failures. Both are
correct measurements of different populations, and nothing in the surface says which
population it measured or when it stops being true.

### 11.2 The certification surface

`07-CERTIFICATION.json` declares:

```jsonc
{ "verdict": "CERTIFIED", "blocking_deviations": [], "declared_open": [],
  "proof": { "existence_digest": "ea83747b…", "identity_digest": "14005b62…",
             "registry_digest": "5dda706a…", "graph_digest": "c34482f0…",
             "invariant_digest": "53a2be24…" },
  "scope": { "objects_governed": 6145, "minted_by_this_programme": 4912,
             "corpus_bytes_touched": 0 } }
```

The five digests make the claim reproducible, and `scope.objects_governed: 6145` is stated
honestly — the surface does not claim 6,188. What it does not carry is any statement that
6,145 **is no longer the population**, or any binding to the commit it was computed at.
A certification with a digest but no staleness bound is verifiable and not falsifiable:
re-running the digest confirms the surface, never the world.

This is exactly the condition the CAAR Architecture Correction §10.2 named for population
scope, arrived at independently: a certification claim must carry a bounded question, an
authority, and a **population digest measured at a named commit**. UGA carries four of the
five digests and no commit binding.

### 11.3 `verify.sh` Stage 6b

`verify.sh:435-436` runs `uga_engine.py gate` through `run_stage`, and the stage's own
comment states *"All ten invariants block."* The gate returns 1 at this baseline.
**Therefore `verify.sh` Stage 6b fails at HEAD** unless the stage is reached in a `SKIP` or
`REUSE` disposition (`run_stage` supports both; `REUSE` is granted when *"identical input
already passed"*). Whether a prior REUSE digest currently masks the failure is not
determined here — it was not measured, and this determination does not execute `verify.sh`.

**`URS-1` (CRITICAL):** The UGA gate fails at this baseline with 2 blocking invariant
violations over 7 objects, and it is wired as a blocking stage of the canonical verification
entry point. A foundation whose own gate is red cannot be depended upon by a new consumer
until it is green.

### 11.4 Three certification-relevant fields are constants by construction

`certification_status` = `GOVERNED` for all 6,145. `evidence_class` = `VALIDATION` for all
6,145. `evidence_boundary` = `NON_CANONICAL` for all 6,145. The first two are not accidents
of the data — `EVIDENCE_FOR_CLASS` in the engine maps **all seven object classes to
`VALIDATION`**:

```python
EVIDENCE_FOR_CLASS = { "EXECUTABLE_OBJECT": "VALIDATION", "TEST_OBJECT": "VALIDATION",
    "CONFIGURATION_OBJECT": "VALIDATION", "TOOLING_OBJECT": "VALIDATION",
    "DATA_OBJECT": "VALIDATION", "DOCUMENT_ARTIFACT": "VALIDATION",
    "EXCLUDED_DOCUMENT": "VALIDATION" }
```

A total map onto a single value is a field that cannot discriminate. This is precisely the
condition CAAR's proposed gate 8.4 (degenerate-field detection) was written to catch, and it
is present in the foundation CAAR would read.

**`URS-7` (MEDIUM):** `certification_status`, `evidence_class` and `evidence_boundary` each
hold exactly one distinct value across 6,145 entries, two of them by a hardcoded total map.
CAAR cannot source a meaningful certification column from UGA as it stands.

---

## 12. Dimension 10 — Infinite Object Compatibility

**Verdict: NOT COMPATIBLE — extension requires code amendment in four places.**

### 12.1 What an eighth object class costs

`AUTH-INF-001` `IL-INF-06` requires every construct to admit a next member *"without
rewrite, renumber, or migration"*; `UCKP-INV-14` requires every vocabulary to admit an
unknown future member; and `extension_rule.how_to_extend` states the price: *"A new
vocabulary member … is one appended entry in DATA. `engine/uckp/law.py` is never amended to
fit the data."*

Admitting an eighth UGA object class today requires:

| # | Site | Kind | Lawful under `extension_rule`? |
|---|---|---|---|
| 1 | `uga-declaration.json` `object_classes` | DATA append | **Yes** |
| 2 | `uga_engine.py::classify_object` rule chain | **Python** | No |
| 3 | `uga_engine.py::ID_CATEGORY` | **Python** | No |
| 4 | `uga_engine.py::EVIDENCE_FOR_CLASS` | **Python** | No |
| 5 | `engine/uckp/uga_projection.py::_CATEGORY_MAP` | **Python**, different module | No |

**One DATA append and four code edits, across two programmes.** A new lifecycle state costs
the same plus `_LIFECYCLE_MAP` (§10.2). The declaration's `object_classes` block is read by
the engine only for the finite-instance scan (`UGA-INV-09`, `decl["object_classes"]` at
`uga_engine.py:1154`); the classifier itself derives nothing from it. **The declaration
describes the vocabulary; it does not define it.**

### 12.2 The terminal fails open

`classify_object`'s final branch is unconditional and returns `EXCLUDED_DOCUMENT`. The
docstring states the consequence as a virtue: *"'UNKNOWN' is therefore structurally
unreachable, which is what makes the Epoch-0 success condition (`unknown_objects == 0`) a
property of the classifier rather than a lucky measurement."*

Measured, that terminal holds **2,620 objects — 42.6% of the entire registry**:

| Composition of `EXCLUDED_DOCUMENT` | |
|---|---|
| by extension | `.md` 2,619 · no extension 1 |
| by top-level | `00-BOOK` 1,258 · `00-MASTER` 1,171 · `adr` 11 · ~180 root-level `*.md` |

Compare the sibling register CAAR draws its classes from.
`mutation-governance-boundary.json` declares its terminal `UNRESOLVED`, `FAILS CLOSED`,
`is_diagnostic_only`, and explains exactly why:

> *"A default class would silently confer an authority no owner claimed, which is precisely
> how `CORPUS_REGISTRATION` and `GOVERNED_DECLARATION` each came to be missing."*

**Two sibling instruments over overlapping populations adopt opposite terminal
disciplines.** UGA's absorbs 42.6% into a catch-all; the mutation register's refuses. And
UGA's terminal is the direct cause of `URS-2`'s 217 dual identities (§8.1), because
absorption is what mints an `EXDOC` identity for a document the corpus had not yet admitted.
The `unknown_objects == 0` success condition is therefore satisfied the way `AV-6`'s
`R-01` satisfies its own — by absorbing, not by resolving.

**`URS-6` (HIGH):** `classify_object`'s unconditional terminal absorbs 2,620 objects (42.6%)
into `EXCLUDED_DOCUMENT`, failing open where the sibling mutation register fails closed, and
is the minting mechanism behind `URS-2`.

**`URS-8` (MEDIUM):** Extending UGA's object-class vocabulary requires four code edits
across two programmes against one lawful DATA append, contravening `extension_rule` and
`UCKP-INV-14`. `UGA-INV-09` passes (0 violations over 64 structural terms) but measures
finite-instance *tokens*, not extensibility.

---

## 13. Measured Discrepancies

Consolidated. Every row is a direct measurement at this baseline.

| # | Discrepancy | Measured | Dimension |
|---|---|---|---|
| D-01 | Tracked paths absent from the UGA registry | **43** of 6,188 | 1, 4 |
| D-02 | Of those, objects with no Universal ID in any plane | **7** | 1, 4 |
| D-03 | Of those, corpus documents identified only in the uncommitted working tree | **36** | 1 |
| D-04 | Registry paths not tracked (orphans) | **0** | 5 |
| D-05 | Ledger `by_object` entries retained with no registry record | **2** | 5 |
| D-06 | Paths holding two Universal IDs (worktree) | **217** | 6 |
| D-07 | Same, at HEAD | **25** | 6 |
| D-08 | `EXDOC` identities that the next run would orphan in place | **192** | 6 |
| D-09 | Duplicate identifiers anywhere in the ledger | **0** | 3, 6 |
| D-10 | Registry/ledger `universal_id` mismatches | **0** | 3 |
| D-11 | Owner disagreements, UGA vs generated-artifact registry (of 345 shared) | **11** | 7 |
| D-12 | Owner value-space overlap, UGA vs `artifacts.json` | **0** tokens | 7 |
| D-13 | Ratified ownership assignments | **0** | 7 |
| D-14 | Declared lifecycle states with zero registry occurrences | **1** (`RETIRED`) | 8 |
| D-15 | Live gate blocking failures | **2** (`UGA-INV-01`, `UGA-INV-10`) | 9 |
| D-16 | Committed invariant surface asserting PASS | **29 of 29**, over 6,145 | 9 |
| D-17 | Registry fields with exactly one distinct value across 6,145 | **3** | 9 |
| D-18 | Code edits required to admit an eighth object class | **4** (+1 DATA append) | 10 |
| D-19 | Objects absorbed by the unconditional terminal | **2,620** (42.6%) | 10 |
| D-20 | Alignment register's recorded UGA population vs live | **5,789** vs **6,145** | 1, 9 |
| D-21 | `artifacts.json` / `id-ledger` uncommitted delta | **+228** each | 2 |

---

## 14. Root Causes

Twenty-one discrepancies reduce to four causes.

### 14.1 `URC-1` — There is no trigger binding UGA's run to its inputs changing

UGA reads `git ls-files`, `artifacts.json` and `generated-artifact-registry.json`, and emits
ten surfaces. Nothing re-runs it when any of the three changes. `verify.sh` runs `gate`
(read-only, fails), never `run` (which would refresh). Consequently a commit that adds a
tracked file, or a corpus registration that admits a document, leaves UGA's surfaces correct
about the past and wrong about the present — and the gate red until a human runs `run`.

**Explains:** D-01, D-02, D-03, D-15, D-16, D-20.

Evidence for the ordering: UGA surfaces written 2026-08-23 16:54; `id-ledger.json` written
2026-08-23 19:02 — the corpus registration transaction ran **after** UGA's last run and UGA
has not run since.

### 14.2 `URC-2` — Two authorities mint over one population with no arbitration rule

`REG-AUTO-001` mints `by_path` identities for corpus-eligible documents.
`UCOS-UGA-001` mints `by_object` identities for everything else. "Everything else" is
computed as *"not currently in `artifacts.json`"* — a **time-dependent** predicate over a
population that is still being registered. A document that UGA sees before the corpus does
receives an `EXDOC` identity that is never withdrawn, because withdrawal is only triggered
by the path leaving version control.

Neither authority is at fault in isolation; both follow their declarations. What is missing
is a rule stating which authority is entitled to mint for a document that is corpus-eligible
but not yet corpus-registered.

**Explains:** D-06, D-07, D-08.

### 14.3 `URC-3` — The terminal absorbs instead of refusing

`classify_object`'s unconditional final branch converts "I have no rule for this" into
"`EXCLUDED_DOCUMENT`". Absorption produces a class, a class produces an id category, and an
id category produces a mint. Had the terminal failed closed — as its sibling register's does
— the 217 dual identities could not have been minted, because no identity would have been
minted at all for an unresolved document.

`URC-3` is `URC-2`'s enabling mechanism, and it is the same structural defect as `AV-6`'s
`R-01` absorption, in a different instrument.

**Explains:** D-19, and jointly with `URC-2`, D-06 – D-08.

### 14.4 `URC-4` — The declaration describes the implementation instead of driving it

`object_classes`, `lifecycle_states` and the evidence-class mapping exist in
`uga-declaration.json` and are duplicated as Python constants that the engine actually uses.
The declaration is read for the finite-instance scan and for schema presence, never as the
source of the vocabulary. So the two can drift (`RETIRED` declared, unemittable), and
extension costs a code edit per duplicated constant plus one in a downstream consumer.

**Explains:** D-14, D-17, D-18.

---

## 15. Target Architecture

Stated as the minimum change that makes UGA a foundation CAAR may depend on. It is a
correction to UGA's *wiring and terminal*, not a redesign: UGA's identity discipline (§5) is
already exact and is preserved unchanged.

### 15.1 Statement

> **UGA is the canonical object authority for the version-controlled boundary: it resolves
> exactly one Universal ID per subject, refuses rather than absorbs an unresolved one, emits
> surfaces bound to the commit they measured, and derives its vocabularies from its
> declaration.**

### 15.2 The four corrections, one per root cause

| # | Correction | Closes | Cost |
|---|---|---|---|
| **T-1** | **Bind the run to its inputs.** UGA re-runs whenever `git ls-files`, `artifacts.json` or the generated-artifact registry changes; the gate reports staleness as a distinct condition from violation (*"surfaces measured at commit X, HEAD is Y"*) rather than as an invariant failure | `URC-1`; D-01/02/03/15/16/20 | Wiring + one gate condition |
| **T-2** | **Declare a minting arbitration rule.** One rule stating which authority mints for a corpus-eligible-but-unregistered document, plus a **supersession** path so that when the corpus admits a document UGA had absorbed, the `EXDOC` identity is recorded as superseded rather than silently orphaned — retained per `id_preservation`, but marked | `URC-2`; D-06/07/08 | Owner act + ledger field |
| **T-3** | **Make the terminal fail closed.** Replace the unconditional `EXCLUDED_DOCUMENT` return with an `UNRESOLVED` terminal on the sibling register's model — diagnostic only, confers no class, mints no identity, fails the gate | `URC-3`; D-19 | Engine change + a reclassification pass over 2,620 objects |
| **T-4** | **Make the declaration authoritative.** `classify_object`'s rule chain, `ID_CATEGORY`, `EVIDENCE_FOR_CLASS` and the downstream `_CATEGORY_MAP`/`_LIFECYCLE_MAP` derive from `uga-declaration.json`, so an eighth class is one DATA append | `URC-4`; D-14/17/18 | Engine change + projection change |

### 15.3 What is preserved without exception

| Preserved | Why the target cannot disturb it |
|---|---|
| All 4,914 `by_object` + 1,492 `by_path` + 7 `by_observation` identities | `id_preservation`, `IL-INF-07`; T-2 marks, never withdraws |
| Zero duplicate identifiers, zero registry/ledger mismatches (§5) | No correction touches the minting or persistence path |
| `page_cursor`, corpus page layout, `artifacts.json` bytes | UGA's `non_goals` are unchanged |
| The 29 invariants and their fail-closed discipline | T-1 adds a staleness condition; T-3 adds violations it can now see |

### 15.4 Interaction with the CAAR Architecture Correction

`T-3` is the same correction CAAR's Constraint 2 already requires, applied one layer down.
`T-2` supplies what the Correction's rule **I-2** (*"a record's key is the Universal ID the
subject already holds"*) presumes and this determination found untrue for 217 subjects:
**one** id per subject. `T-4` is the Correction's §3.2 registered-vocabulary model applied
to UGA's own classes. **CAAR's corrected architecture and UGA's target architecture are the
same four ideas at two levels**, which is the expected result if the Correction's root-cause
analysis was right.

---

## 16. Synchronization Strategy

Ordered so that no step is taken against an input a later step invalidates. Steps 1–3 are
synchronization; 4–7 are correction.

```
S-1  Commit or revert the standing artifacts.json / id-ledger modification (+228 each).
     WHY FIRST: every population figure is ambiguous while two versions of the corpus
     registry exist. No later measurement is stable until this resolves.
     Owner: whoever holds the uncommitted registration.  Closes: D-21, and 36 of D-01.

S-2  Run `uga_engine.py run`.  Mints 7 anonymous objects, refreshes all ten surfaces.
     PROJECTED RESULT (worktree inputs): 6,188 objects · 1,461 DOCUMENT_ARTIFACT ·
     4,727 UGA-minted · 7 new mints · 192 EXDOC identities orphaned in place · 2 retired.
     Owner: implementation authority.  Closes: D-01, D-02, D-15, D-16.  WORSENS: D-08.

S-3  Re-run `uga_engine.py gate`.  Expect 29/29 PASS over 6,188.
     Owner: implementation authority.  Verifies S-1 and S-2 only — no defect below is closed.

──────── the three steps above synchronize; nothing above corrects ────────

S-4  Declare the minting arbitration rule and the supersession path (T-2).
     MUST PRECEDE any further corpus registration, because each one adds a dual identity.
     Owner: mutation governance owner + REG-AUTO-001.  Closes: D-06, D-07, D-08.

S-5  Reconcile the 217 existing dual identities under S-4's rule.
     Not a deletion — a supersession record per pair, retained under id_preservation.
     Owner: identity authority.  Closes the standing population of D-06.

S-6  Replace the absorbing terminal with a fail-closed UNRESOLVED (T-3), and reclassify
     the 2,620 currently-absorbed objects against the declared rules.
     MUST FOLLOW S-5, because a fail-closed terminal over unreconciled dual identities
     would fail the gate on 217 objects at once with no disposition available.
     Owner: implementation authority + mutation governance owner.  Closes: D-19.

S-7  Make the declaration authoritative (T-4); bind the run to its inputs (T-1); add the
     staleness condition and a commit binding to 07-CERTIFICATION.json.
     Owner: implementation authority.  Closes: D-14, D-17, D-18, D-20.
```

**S-2 makes the gate green and closes nothing structural.** That is the most important
property of this ordering to state plainly: a green gate after S-3 would mean UGA is
synchronized, not that it is sound. Six of the eleven findings survive S-3 untouched.

---

## 17. Dependencies

```
S-1 (commit/revert the +228)  ──┐
                                ├─→ S-2 (run) ──→ S-3 (gate green)
nothing else                  ──┘                      │
                                                       │  synchronization complete
                                                       ▼
S-4 (arbitration rule)  ──→ S-5 (reconcile 217) ──→ S-6 (fail-closed terminal)
        │                                                    │
        │                                                    ▼
        └────────────────────────────────────────────→ S-7 (declaration-driven,
                                                             input-bound, commit-bound)
```

### 17.1 Upstream — what UGA depends on

| Dependency | State at this baseline | Blocks |
|---|---|---|
| `artifacts.json` / `id-ledger.json` committed | **Uncommitted, +228** | S-1, and every figure |
| `REG-AUTO-001` corpus registration boundary | Live, still registering | S-4 (each registration adds a dual identity) |
| `UCOS-EVIDENCE-UNIVERSE-001`'s five closed classes | Live, closed by owner | T-4's evidence mapping |
| `UCL-000001` / state-axis owner | Live, uncited by UGA | §10.3's axis reconciliation |
| `engine/uckp/uga_projection.py` | Live, fails closed on unmapped values | T-3, T-4 |

### 17.2 Downstream — what depends on UGA

| Consumer | Dependency | Effect of the findings |
|---|---|---|
| `verify.sh` Stage 6b | Blocking gate | **Red at this baseline** (`URS-1`) |
| `engine/uckp/uga_projection.py` | Reads `02-UNIVERSAL-OBJECT-REGISTRY.json` entries | Projects a 43-short population; would raise on `RETIRED` |
| `constitutional-authority-alignment.json` `existence_resolution` | Names UGA an existence AUTHORITY, population 5,789 | Recorded figure stale by 356 |
| **CAAR (proposed)** | 5 of 7 columns, identity plane, owner tier 3 | **Cannot proceed past S-5** — see §17.3 |

### 17.3 The CAAR dependency, stated exactly

The CAAR Architecture Correction's prerequisite **P-1** (adopt the corrected architecture)
does not depend on UGA. Its identity model rule **I-2** does, and specifically on `URS-2`:
a projection keyed on *"the Universal ID the subject already holds"* is undefined for 217
subjects that hold two. **CAAR's Stage 7 (first build) is blocked on S-5, not on S-3.** A
CAAR built after synchronization but before reconciliation would key 217 records on the
`EXDOC` identity the registry publishes, and would encode `URC-2` as CAAR's own permanent
structure — the same failure the design's own §3.2 warned against for unrepaired sources.

---

## 18. Acceptance Criteria

UGA may be accepted as a complete and reliable canonical object authority when all fifteen
hold. **None holds at this baseline.**

**Synchronization (S-1 – S-3):**

- [ ] AC-1 · `artifacts.json` and `id-ledger.json` carry no uncommitted delta; one corpus population, not two
- [ ] AC-2 · Registry entries == `git ls-files -z` count, exactly; missing = 0, orphan = 0
- [ ] AC-3 · Zero objects tracked without a Universal ID in some ledger plane
- [ ] AC-4 · `uga_engine.py gate` returns 0 with 29 of 29 PASS
- [ ] AC-5 · `05-GOVERNANCE-INVARIANTS.json`'s asserted result matches a live gate run over the same population

**Identity (S-4 – S-5):**

- [ ] AC-6 · Every subject holds **exactly one** Universal ID; `by_path ∩ by_object` = ∅, or every element of it carries a supersession record naming the surviving id
- [ ] AC-7 · A declared arbitration rule states which authority mints for a corpus-eligible, unregistered document
- [ ] AC-8 · An invariant exists that measures "exactly one id per subject" — the condition `CAA-INV-04` and `UGA-INV-01` jointly do not cover
- [ ] AC-9 · Zero identifiers deleted, renumbered or reissued in reaching AC-6 (`id_preservation`)

**Classification and lifecycle (S-6):**

- [ ] AC-10 · The terminal fails closed; `UNRESOLVED` confers no class and mints no identity
- [ ] AC-11 · Every one of the 2,620 currently-absorbed objects resolves to a declared rule or to `UNRESOLVED` — not to a catch-all
- [ ] AC-12 · `RETIRED` is emittable and emitted for the 2 retained identities, and `_LIFECYCLE_MAP` carries it
- [ ] AC-13 · UGA's lifecycle vocabulary cites a declared axis owner or declares its own axis with a bounded question

**Extensibility and certification (S-7):**

- [ ] AC-14 · Admitting an eighth object class touches only `uga-declaration.json`; a synthetic N+1 member is exercised, not asserted
- [ ] AC-15 · `07-CERTIFICATION.json` carries the commit it measured and a staleness condition; `existence_resolution`'s recorded population matches the live one or declares its measurement date

---

## 19. Closure Conditions

The conditions under which this determination's question is answered `YES`, stated so that a
successor can evaluate them without re-deriving anything.

| # | Condition | Evidence required |
|---|---|---|
| **C-1** | **Complete** — UGA knows about everything in its declared scope | AC-2, AC-3 hold at a commit, re-measured at that commit and not carried forward |
| **C-2** | **Reliable** — what UGA says is true | AC-4, AC-5 hold; the gate and the committed surface agree over one stated population |
| **C-3** | **Stays true** — reliability survives the next commit | AC-15 holds: surfaces carry a commit binding, and staleness is a reported condition, not an invariant failure |
| **C-4** | **Singular** — one subject, one identity | AC-6 – AC-9 hold; `URS-2` closed with zero identifiers destroyed |
| **C-5** | **Refuses rather than absorbs** | AC-10, AC-11 hold; the terminal is diagnostic and fail-closed |
| **C-6** | **Extensible** — an eighth class costs one DATA append | AC-14 holds, exercised |

**Verdict on the directive's question, at this baseline:**

| Question | Answer |
|---|---|
| Is UGA **complete**? | **No.** 43 tracked objects unregistered at HEAD; 7 anonymous; scope excludes the ignored and untracked population by declaration |
| Is UGA **reliable**? | **No, currently.** Its gate is red; its committed invariant surface asserts a clean state that the live gate contradicts; 217 subjects have two identities and no invariant measures it |
| Is UGA the **right foundation** for CAAR? | **Yes — with conditions.** Its identity integrity is exact (0 duplicate identifiers, 0 mismatches, 0 orphans, document class == corpus path-for-path), it holds the only total non-degenerate owner function in the repository, and every defect found is a wiring, arbitration or terminal defect — not a modelling one |
| May CAAR proceed on it? | **Not past C-4.** CAAR's identity rule I-2 is undefined for 217 subjects |

**Closure is reached when C-1 through C-6 all hold at one commit, measured at that commit.**
None holds at this baseline.

---

## 20. Findings Register

| ID | Finding | Severity | Root cause | Status |
|---|---|---|---|---|
| `URS-1` | The UGA gate fails at this baseline (`UGA-INV-01`, `UGA-INV-10`, 7 objects) and is wired blocking as `verify.sh` Stage 6b | **CRITICAL** | `URC-1` | **OPEN** |
| `URS-2` | 217 paths hold two Universal IDs; the registry publishes the UGA-minted one for all 217; no invariant measures the condition; the count grows with every corpus registration | **CRITICAL** | `URC-2`, `URC-3` | **OPEN** |
| `URS-3` | `05-GOVERNANCE-INVARIANTS.json` asserts 29/29 PASS over 6,145 while the live gate reports 2 blocking failures over 6,188; `07-CERTIFICATION.json` declares `CERTIFIED` with no commit binding or staleness bound | **CRITICAL** | `URC-1` | **OPEN** |
| `URS-4` | 43 tracked paths carry no registry record at HEAD; 7 carry no Universal ID in any plane | **HIGH** | `URC-1` | **OPEN** |
| `URS-5` | `RETIRED` is declared, measured (2) and structurally unemittable; `_LIFECYCLE_MAP` would raise on it; UGA's lifecycle cites neither declared axis owner | **HIGH** | `URC-4` | **OPEN** |
| `URS-6` | The unconditional terminal absorbs 2,620 objects (42.6%) into `EXCLUDED_DOCUMENT`, failing open where the sibling mutation register fails closed | **HIGH** | `URC-3` | **OPEN** |
| `URS-7` | `certification_status`, `evidence_class`, `evidence_boundary` each hold one distinct value across 6,145; two by a hardcoded total map | **MEDIUM** | `URC-4` | **OPEN** |
| `URS-8` | An eighth object class costs four code edits across two programmes against one lawful DATA append — contra `extension_rule`, `UCKP-INV-14` | **MEDIUM** | `URC-4` | **OPEN** |
| `URS-9` | Three unreconciled owner value spaces; 11 measured disagreements resolve a declared owner to a derived directory; 0 ratified assignments | **MEDIUM** | — | **OPEN** |
| `URS-10` | `existence_resolution` records UGA's population as 5,789 against a live 6,145 — `AAT-4` drift, third measured occurrence | **MEDIUM** | `URC-1` | **OPEN** |
| `URS-11` | `CAAR-3`'s "1,233 certified / 1,461 corpus-registered" is not a registry disagreement: 1,233 **is** HEAD's corpus registry and equals UGA's `DOCUMENT_ARTIFACT` set exactly; 1,461 is the uncommitted working tree. The 228-artifact gap five determinations attributed to registry drift is one standing uncommitted mutation | **LOW / structural** | `URC-1` | **OPEN** |

**11 raised · 0 resolved.**

### 20.1 Disposition of prior findings

| Prior | Step 6 / CAAR disposition | This determination |
|---|---|---|
| `ACD-5` (UGA stale: 117 orphans / 160 missing) | Raised HIGH | **CORRECTED.** 0 orphans, 43 missing (§1.4). Substance confirmed by other evidence; figures superseded |
| `ACD-2` (5 of 7 columns already produced) | Raised HIGH | **CONFIRMED**, and qualified: the columns exist over a 43-short population, and 2 of the 5 are degenerate (`URS-7`) |
| `ACD-6` (degenerate UGA fields) | Raised MEDIUM | **CONFIRMED with mechanism** — `EVIDENCE_FOR_CLASS` is a total map to one value (`URS-7`) |
| `CAAR-2` (`artifacts.json` owner is one constant) | Raised HIGH | **UNCHANGED**, and now bounded: UGA supplies 276 distinct owners for 6,145 paths (`URS-9`) |
| `CAAR-3` (three disagreeing totals) | Raised HIGH | **RE-EXPLAINED** as `URS-11`: two of the three are the same register at two commits |
| `CIR-5` (unprecedented lifecycle enums) | Raised HIGH | **EXTENDED**: the same defect is present in the foundation (`URS-5` §10.3) |
| `AV-6` (`R-01` absorbs before resolving) | CRITICAL, open | **PATTERN REPEATED** in a second instrument (`URS-6`) — absorption as a success condition |

---

## 21. Verification

| Check | Result |
|---|---|
| Artifact exists | ✅ `UCOS-OMEGA-INFINITY-UGA-REALITY-SYNCHRONIZATION-DETERMINATION.md` |
| Line count | ✅ **1046** |
| Required sections — current state | ✅ §2 |
| Required sections — the ten analysis dimensions | ✅ §3 completeness · §4 filesystem alignment · §5 identity alignment · §6 missing · §7 orphan · §8 duplicate identities · §9 ownership · §10 lifecycle · §11 certification · §12 infinite object compatibility |
| Required sections — measured discrepancies | ✅ §13 (D-01…D-21) |
| Required sections — root causes | ✅ §14 (`URC-1`…`URC-4`) |
| Required sections — target architecture | ✅ §15 (T-1…T-4) |
| Required sections — synchronization strategy | ✅ §16 (S-1…S-7) |
| Required sections — dependencies | ✅ §17 (upstream, downstream, CAAR dependency stated exactly) |
| Required sections — acceptance criteria | ✅ §18 (AC-1…AC-15) |
| Required sections — closure conditions | ✅ §19 (C-1…C-6 + verdict table) |
| HEAD unchanged | ✅ `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | ✅ `integration/recovery-001` |
| Analysis only — synchronization performed | ✅ **0** — `uga_engine.py run` **not executed** |
| Code changes | ✅ **0** — engine, projection, `verify.sh` read, none written |
| Registry changes | ✅ **0** — ledger, `artifacts.json`, GAR, UGA surfaces read, none written |
| Identities minted | ✅ **0** — `by_object` unchanged at 4,914 before and after |
| Certification changes | ✅ **0** |
| Commits | ✅ **0** |
| Tracked modifications unchanged | ✅ **38** — identical set to session start |
| Only one new artifact | ✅ the single delta is this file |
| Gate execution was non-mutating | ✅ `cmd_gate` calls `build(mint=False)`; all ten UGA surface mtimes and `id-ledger.json` mtime identical before and after; `git status` count unchanged |
| Findings resolved | ✅ **0** — 11 raised, 1 predecessor measurement corrected |

### 21.1 Measurement provenance

```
git ls-files -z                                     6,188
UGA 02-UNIVERSAL-OBJECT-REGISTRY entries            6,145
  00-EXISTENCE-INVENTORY objects                    6,145   (path set == registry: True)
  01-EXECUTABLE-OBJECT-REGISTRY entries             4,912
  03-AUDIT-UNIVERSE events                          4,914
  04-RELATIONSHIP-GRAPH relationships               34,872  (6 kinds)
  05-GOVERNANCE-INVARIANTS                          29 of 29 PASS, measured 6,145
  07-CERTIFICATION verdict                          CERTIFIED, scope 6,145
  08-OBSERVATION-REGISTRY observations              7
missing / orphan                                    43 / 0
  anonymous at HEAD / at worktree                   43 / 7
id-ledger by_path   HEAD / worktree                 1,264 / 1,492
id-ledger by_object HEAD / worktree                 4,914 / 4,914
id-ledger by_observation                            7
artifacts.json      HEAD / worktree                 1,233 / 1,461
UGA DOCUMENT_ARTIFACT == HEAD artifacts path set    True (1,233)
by_path ∩ by_object   HEAD / worktree               25 / 217
  registry publishes by_object id for               217 of 217
  would flip to DOCUMENT_ARTIFACT on next run       192
retired identities (ledger, not in registry)        2
owner distinct: UGA / GAR / artifacts.json          276 / 32 / 1
  UGA vs GAR agreement over 345 shared              334 agree, 11 disagree
  UGA owners ∩ artifacts.json owners                0
ownership-declarations assignments                  0
EXCLUDED_DOCUMENT                                   2,620 (42.6%); .md 2,619
live gate                                           2 FAIL (INV-01 ×7, INV-10 ×7), 27 PASS
existence_resolution recorded UGA population        5,789
git status: modified / untracked / total            38 / 309 / 347
this artifact, lines                                1046
```

---

*This determination modified no file, changed no code or configuration, wrote to no registry,
minted no identifier, altered no certification, committed nothing, and synchronized nothing —
`uga_engine.py run` was deliberately not executed, and `by_object` stands at 4,914 before and
after. It answers the foundation question the CAAR Architecture Correction created: UGA's
identity discipline is exact — zero duplicate identifiers, zero registry/ledger mismatches,
zero orphans, and a document class that equals HEAD's corpus registry path for path — and its
population, gate state and certification surface are not synchronized with the repository. Its
gate fails at this baseline on 7 unidentified objects, while its committed invariant surface
asserts 29 of 29 passing over a population 43 objects short of the tracked one. Two hundred and
seventeen subjects hold two Universal IDs, a condition no invariant measures and which grows
with every corpus registration; that is the finding on which CAAR's own identity rule is
undefined, and CAAR's first build is blocked on it rather than on a green gate. Eleven findings
(`URS-1`…`URS-11`) are raised, four root causes named, and one predecessor measurement of my
own (`ACD-5`) corrected. None is resolved. The verdict is **NOT SYNCHRONIZED · CONDITIONALLY
QUALIFIED**: UGA is the right foundation and is not yet a reliable one. The single repository
mutation is the creation of this file.*

**END DETERMINATION — UGA ASSESSED AS NOT SYNCHRONIZED · CONDITIONALLY QUALIFIED · NO SYNCHRONIZATION PERFORMED · STOPPED AFTER ARTIFACT CREATION.**
