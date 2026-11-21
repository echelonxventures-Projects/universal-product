# PHASE — P0 CLOSURE REMEDIATION DETERMINATION

> **Mission:** Resolve the two remaining P0 closure concerns to a true constitutional fixed point — not a relabeled exception.
> **Mode:** Discovery only. No implementation. No code changes.
> **Date:** 2026-08-13
> **HEAD:** `ec8b8d5b`, confirmed via fresh `git log`/`git status`.

---

## 1. UGA Anonymous-Object Backlog

### 1.1 Complete enumeration

The gate's own printer truncates violation lists to 10 entries per invariant (`00-MASTER/UCOS-UGA-001/uga_engine.py:1912`, `for v in i["violations"][:10]`), so the CLI output alone under-reports. Calling `build(mint=False)` directly (read-only) returns the untruncated set: **19 anonymous objects, all 19 identical between `UGA-INV-01` and `UGA-INV-10`**:

```
CERTIFICATION-ARCHITECTURE-DETERMINATION-DRAFT.md
CERTIFICATION-OWNERSHIP-RECONCILIATION-DETERMINATION.md
CERTIFICATION-OWNERSHIP-RECONCILIATION-FINDING.md
PHASE-0.7-DEPENDENCY-GRAPH-CONSOLIDATION-READINESS-DETERMINATION.md
PHASE-0.7-DEPENDENCY-GRAPH-GOVERNANCE-BINDING-DETERMINATION.md
PHASE-CAA-INV-08-ENFORCEMENT-COMPLETENESS-DETERMINATION.md
PHASE-CERTIFICATION-GOVERNANCE-BINDING-DETERMINATION.md
PHASE-CERTIFICATION-GOVERNANCE-RELATIONSHIP-DETERMINATION.md
PHASE-CERTIFICATION-TAXONOMY-READINESS-DETERMINATION.md
PHASE-GOVERNANCE-FREEZE-DETERMINATION.md
PHASE-GOVERNANCE-RECONCILIATION-FREEZE-READINESS-DETERMINATION.md
PHASE-IDENTITY-NAMESPACE-GOVERNANCE-BINDING-DETERMINATION.md
PHASE-IDENTITY-NAMESPACE-OWNERSHIP-DETERMINATION.md
PHASE-KNOWLEDGE-IDENTITY-RELATIONSHIP-DETERMINATION.md
PHASE-KNOWLEDGE-REGISTRY-OWNERSHIP-RECONCILIATION-DETERMINATION.md
PHASE-UNIVERSAL-ASSURANCE-RELATIONSHIP-DETERMINATION.md
PHASE-VERDICT-VOCABULARY-TAXONOMY-DETERMINATION.md
POST-STABILIZATION-DETERMINATION-LIFECYCLE-DECISION.md
UCOS-POST-STABILIZATION-READINESS-DETERMINATION.md
```

All 19 are root-level, tracked, committed `*.md` files produced by this P0 arc's own discovery and binding work — every one already following the house `*-DETERMINATION.md`/`*-DECISION.md`/`*-FINDING.md`/`*-DRAFT.md` convention. No object outside this exact set is anonymous.

### 1.2 What each object already is, per the engine's own deterministic classification

Calling the classifier directly (`u.build(mint=False)`, reading each entry rather than assuming) shows every one of the 19 already carries a full, deterministically-derived record:

```
object_class: EXCLUDED_DOCUMENT
owner: UCOS-REPOSITORY-ROOT
producer: HUMAN_AUTHORED
lifecycle: AUTHORED
identity_authority: UCOS-UGA-001
evidence_boundary: NON_CANONICAL
certification_status: GOVERNED
content_hash: <computed>
universal_id: None      <- the only field actually missing
first_seen: None        <- the only field actually missing
```

Ownership, lifecycle stage, and evidence classification are **already resolved** by `classify_object()`/`derive_owner()` (`uga_engine.py:187-229`) — deterministic, total functions with an unconditional terminal branch. What is missing is exactly one thing: the `universal_id`/`first_seen` pair that only `epoch1_identity()`'s mint step assigns.

### 1.3 What `object_class: EXCLUDED_DOCUMENT` actually means — checked, not assumed

The classifier's own comment (`uga_engine.py:210-215`) is explicit and directly answers whether this class is eligible for an exclusion boundary:

> *"Unconditional terminal branch: a readable document that the corpus registry does NOT carry — Operational Memory under `00-MASTER/` and the generated projections under `00-BOOK/CONTROL-TOWER, REGISTRIES, VOLUMES and PORTAL`. **Excluded from CORPUS REGISTRATION by declared authority, which is a statement about which register lists them — never a licence to exist anonymously.**"*

This forecloses an exclusion-declaration resolution for this class: `EXCLUDED_DOCUMENT` means "not carried by `ukb.py`'s corpus register" (confirmed separately: `ukb.py enforce --pre` lists these same files as `UNREGISTERED`, `REPORTED` not `GATED` — a different, non-blocking, doc-corpus-specific concern). It does **not** mean "exempt from universal identity." Confirming this structurally: `ID_CATEGORY` (`uga_engine.py:248-255`) maps `"EXCLUDED_DOCUMENT": "EXDOC"` — this class has a governed category prefix and is minted exactly like every other governed class; nothing in `epoch1_identity()` special-cases or skips it.

### 1.4 Classifying the correct resolution, per the four options given

- **Canonical identity assignment** — Correct and required, per §1.3.
- **Exclusion declaration** — Not available for this class; the code's own comment explicitly rules this out ("never a licence to exist anonymously").
- **Lifecycle closure** — Not applicable as a *separate* action: `lifecycle: AUTHORED` is already correctly assigned by the same deterministic rule every other authored document in the repository receives. There is no lifecycle transition pending; the gap is identity, not lifecycle state.
- **Other legitimate resolution** — None found. No third path exists in the engine's own architecture between "minted" and "anonymous" for a governed class.

**Determination: canonical identity assignment via `uga_engine.py run` is the sole correct resolution.**

### 1.5 Confirming this is not "blind minting"

`epoch1_identity()` (`uga_engine.py:258-302`) is a pure, total, append-only function: an existing ledger entry is returned untouched (never reissued); a new entry draws the next sequence number from the **same shared `category_seq` counter** `identity_authority_resolution`'s `derivation` block already governs and `CAA-INV-04` already measures (5,804 identifiers at last count); the minted shape (`UCOS-EXDOC-NNNNNN`) is the same `UCOS-<CATEGORY>-<NNNNNN>` form every other repository-object identity already takes — no new category, no new mechanism, no per-file judgment call. This satisfies every principle named in the mission:

- **Canonical Ownership** — owner (`UCOS-REPOSITORY-ROOT`) is already deterministically resolved, not invented here.
- **Knowledge Once Principle** — each file's `content_hash` is computed once, deterministically; minting does not duplicate or reinterpret it.
- **Artifact Lifecycle Governance** — `lifecycle: AUTHORED` is already correctly assigned; minting does not alter it.
- **Reuse Before Create** — this is the *existing*, already-used-many-times-this-session mint mechanism (the same one that registered every other artifact in the repository); nothing new is created.

### 1.6 What this determination does *not* do

Per explicit instruction ("No implementation... Stop after analysis and recommendation"), `uga_engine.py run` was **not executed** in this phase. The backlog remains at 19 as of this writing — re-confirmed immediately before this document was written. The correct remediation is fully specified and zero-discretion, but it is a recommendation, not an action taken.

---

## 2. CMG Tier T1 Vacancy

### 2.1 The constitution's own jurisdictional text

`CMG-000001` does not merely note the T1 vacancy in passing — it defines, in its own binding articles, exactly why CMG cannot close it:

- **Article P.2**: *"No instrument in the corpus defines the class of object that Tier 1 consists of, enumerates its members, or governs the admission of a new member. That vacancy IS the jurisdiction of this instrument, and it is the **only** jurisdiction of this instrument."* — CMG's jurisdiction is to *record* the vacancy; the article states this is the *only* thing it has jurisdiction to do about T1.
- **CMG-OQ-02** (open question, `CMG-REGISTRY.json`): *"T1 governs substance; this instrument has no substantive jurisdiction (XIX.2). Promoting any located artifact into T1 would be an allocation of substantive authority beyond jurisdiction."*
- **Article XVI.3**: *"T1 binds substance and is presently vacant"* — stated as a structural fact of the tier lattice, not a defect.
- **Article XVII.4** (the vacancy closure procedure, defined by the constitution itself): record the vacancy (done); record dependent determinations as provisional (done); *"refer the identification of the occupying authority to explicit ratification as an open question"* (external — ratification is not a repository engineering act); re-run resolution when the vacancy closes (conditional on that external act).
- **Article IV.11**: *"A vacancy IS a recorded fact, not a defect to be hidden, and carries a mandatory closure procedure."* — a correctly-recorded vacancy is, by the constitution's own design, a valid, permanent-until-externally-resolved state, not a temporary flaw awaiting an internal fix.

### 2.2 The vacancy record itself

`00-CMG/CMG-REGISTRY.json` — `VAC-01`, tier `T1`: `"located": false`, evidence: *"The referent exists in the repository only as frozen non-normative source material under `00-SOURCE/CONSTITUTIONS/` (.docx). No ratified normative artifact occupies the tier."* Closing this requires **ratification** of that source material into a normative instrument — an act no code change, discovery pass, or governance binding performed by this repository's own tooling can perform. Ratification is, by definition, an act of an authority external to the artifact being ratified.

### 2.3 Boundary determination

Applying the mission's own A/B test directly:

- **(A) Required internal prerequisite for P0 closure — No.** The constitution's own text (§2.1) states CMG — the highest *located* authority in the tier lattice below T1 — has no jurisdiction to fill T1. If the one instrument whose entire purpose is meta-constitutional recognition explicitly disclaims jurisdiction over this tier, no lower-tier repository process (T2 and below, which is where every P0 determination this session operated) could have jurisdiction either.
- **(B) External constitutional dependency outside repository authority — Yes.** Confirmed by the constitution's own binding text, not asserted by this determination. This is a structural fact of the tier lattice (Article XVI.3), with its own defined, already-executed-as-far-as-possible closure procedure (Article XVII.4 steps a-b are done; steps c-d are inherently external and conditional).

**Determination: CMG Tier T1 is formally, constitutionally classified outside repository responsibility boundary — not merely outside P0's.** This is not a relabeled exception; it is a jurisdictional fact stated in the constitution's own binding articles, independently verifiable by any reader of `CMG-000001`. Confirmed further by `cmg-gate.sh`'s own live behavior: `vacancies recorded: 1`, `readiness outcome: READY-PROVISIONAL` — the gate itself treats a correctly-recorded vacancy as compatible with readiness, not as a failure condition, exactly matching Article IV.11's framing.

**This item is fully discharged from P0's closure concerns.** No further action, by this repository, can resolve it — and none is required for P0 to be sound.

---

## 3. Validation

Re-run fresh, in the order requested:

| Check | Result |
|---|---|
| `engine.uckp.alignment.verify_binding(document)` | **PASS** — `()`, zero findings |
| `uga_engine.py gate` — `CAA-INV-01` through `07` | **PASS**, 0 violations each, counts unchanged (10, 107, 9, 5804, 6, 5, 16) |
| `uga_engine.py gate` — `UGA-INV-01` / `UGA-INV-10` | **FAIL**, 19 violations each — the backlog analyzed in §1, not yet remediated (no implementation performed this phase) |
| `00-BOOK/tools/ukb.py enforce --pre` | **PASS** — `ENFORCEMENT PASSED` (unregistered-eligible count now 22, all `REPORTED` not `GATED` — a separate, non-blocking, doc-corpus concern distinct from UGA identity, already established in the freeze determination) |
| `00-BOOK/tools/ukb.py validate` | **PASS** — `VALIDATION PASSED`, 1,233 artifacts, referential integrity intact |
| `cmg-gate.sh` | `READY-PROVISIONAL`, 1 vacancy recorded (T1), 0 findings |
| Phase-8/9 | Not run — not required for this discovery, per instruction |

---

## 4. Classification

Weighing both items honestly against the mission's own stated bar — *"the objective is a true constitutional fixed point," "do not accept 'closed with exceptions' merely because it is convenient"*:

- **CMG Tier T1 is now genuinely resolved as a boundary**, not an exception: the constitution's own binding text proves no repository instrument has jurisdiction over it, and its closure procedure is already executed as far as any internal act can take it. This item no longer needs to be carried as an open concern — it is a permanent, correctly-recorded structural fact.
- **The UGA backlog is not eligible for the same treatment.** The engine's own code explicitly forecloses an exclusion-boundary reading for this class of object. There is exactly one correct, fully-specified, zero-discretion, previously-proven-safe remaining action (`uga_engine.py run`), and it has not been executed in this phase because the phase was scoped to discovery only.

Because 19 objects remain literally anonymous in the live gate output at this moment, declaring **(A) P0 CLOSED** would misstate the current, checked state — exactly the "convenient" mislabeling the mission warned against. Declaring **(B) P0 CLOSED WITH DOCUMENTED EXTERNAL BOUNDARY** would be accurate for CMG Tier T1 alone but would still be papering over the UGA item, which is not a boundary case at all — it is an outstanding, if trivial, action.

**Classification: (C) P0 REMEDIATION REQUIRED — narrowly and completely scoped to exactly one deterministic action.**

This is not the open-ended "remediation required" the classification label might suggest elsewhere. It is: run `uga_engine.py run` once (append-only, zero discretion, already proven safe by repeated use this session), then re-run `uga_engine.py gate` to confirm `UGA-INV-01`/`UGA-INV-10` both reach zero violations. Nothing else remains. Once that single action is taken and confirmed, P0 reaches a state with **zero exceptions and one permanently, correctly-recorded, jurisdictionally-proven external boundary (CMG Tier T1)** — which Article IV.11 itself defines as a valid closed state, not a lingering condition — at which point **(A) P0 CLOSED** becomes the accurate classification.

---

## 5. Non-Goals

- No file was modified. `uga_engine.py run` was not executed — its outcome is fully predicted (§1.6) but not performed.
- No claim is made that CMG Tier T1 will ever be filled; §2 establishes only that its non-filling is not a P0 or repository defect.
- No resolved P0 governance question was reopened.
- Phase-8/9 were not run, per instruction.

---

Stopping after analysis and recommendation, as instructed.
