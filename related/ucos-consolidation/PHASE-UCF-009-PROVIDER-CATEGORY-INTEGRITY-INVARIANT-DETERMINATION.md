# PHASE-UCF-009 — PROVIDER CATEGORY INTEGRITY INVARIANT DETERMINATION

## Document Identity

| Field | Value |
|---|---|
| Determination | PHASE-UCF-009-PROVIDER-CATEGORY-INTEGRITY-INVARIANT-DETERMINATION |
| Mission | Determine the constitutional and technical boundary of `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` enforcement — ownership, semantics, evidence, timing, failure mode, and relationship to the seventeen existing invariants |
| Mode | Determination only. Zero code, zero test changes, zero registry mutation, zero invariant implementation, zero constitution changes. |
| Date | 2026-08-14 |
| HEAD | `1f869865`, working tree unchanged from `PHASE-UCF-008 § Current Repository Truth` |

## Purpose

`PHASE-UCF-007` selected the UCKP invariant layer as the correct constitutional owner of provider category exclusivity and conceptually sketched `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY`, leaving its blocking-vs-advisory question explicitly deferred. `PHASE-UCF-008` determined that category ownership should be represented as a `category_ownership_resolution` ledger entry — the proven `*_resolution` pattern — rather than a `Term` schema change or provider self-declaration, and left the invariant itself unbuilt. This document answers the four questions `PHASE-UCF-008` closed with unresolved: how the invariant should be validated, what evidence it requires, whether violations block or warn, and precisely where invariant ownership belongs — by examining, for the first time in this arc, the actual mechanics of `engine/uckp/validation.py`'s invariant machinery rather than its ownership in the abstract.

## Scope

In scope: invariant ownership mechanics, PASS/FAIL/UNKNOWN semantics, evidence boundary, validation timing, failure-mode selection, and relationship to `UCKP-INV-01..17`, `CAA-INV-01..08`, and `OBS-INV-*`. Out of scope, per explicit instruction: writing the invariant, editing `law.py` or `validation.py`, adding tests, or mutating `constitutional-authority-alignment.json`.

## Context

Thirteenth determination in the Universal Completeness Foundation arc, immediately following `PHASE-UCF-008`. `PHASE-UCF-005` through `008` are treated as settled and not reopened; this document analyzes forward from all four, and in particular reuses `PHASE-UCF-008`'s ownership-model selection (the `*_resolution` ledger) as a given input rather than re-litigating it.

---

## Current Repository Truth

Re-confirmed fresh in this pass:

| Check | Result |
|---|---|
| `verify_binding(constitutional-authority-alignment.json)` | `()` — PASS |
| `build_universe().registry.discover()` | `providers_found=('engine.uckp.alignment', 'engine.uckp.capabilities', 'engine.uckp.constitution', 'engine.uckp.uga_projection')`, `objects_admitted=5982`, `failures=()` |
| `validate_universe(build_universe())` (17 UCKP-INV) | `verdict='certified'`, `certified=True`, `blocking_failures=()`, `unmeasured=()` |
| `00-BOOK/tools/ukb.py enforce --pre` | PASS |
| `00-BOOK/tools/ukb.py validate` | PASS — 1233 artifacts, referential integrity OK |

Identical to `PHASE-UCF-007`/`008`'s baseline — no drift, no corruption.

Also confirmed by direct read, not assumed:

- `engine/uckp/law.py:203-395` — `UCKP_INVARIANTS` is a **closed, fixed 17-member tuple**, declared once. Nothing in `law.py`, `vocabulary.py`, or `validation.py` provides a registration path for an 18th member the way `Vocabulary.extended_with()` provides one for a new category. `UCKP_INVARIANTS` is not an open vocabulary; it is enumerated data, the same architectural class as `Facet` (closed by design — `facets.py:9-13`: *"Adding a thirty-fourth facet is a constitutional amendment... amendments belong in the law, not in a data file."*).
- `engine/uckp/law.py::Invariant.blocking` — every declared `Invariant` uses the dataclass default `blocking=True`; `grep -c "blocking=" engine/uckp/law.py` returns `0` (no invariant declaration overrides the default), and `validation.py`'s own module docstring states it directly: *"because every invariant in the root law is blocking, the report is refused"* on any unmeasured or violated result. **UCKP-INV has no advisory tier at all**, by design.
- `engine/uckp/validation.py:270-300` — `ConstitutionalValidator.probes()` is a hardcoded, 1:1 dict of exactly the 17 declared ids; `unprobed()` and `orphan_probes()` explicitly diff the probe-dict keys against `ROOT_LAW.invariant_ids()` and treat any mismatch as a defect. A probe bound to an id the law does not declare is itself flagged (`orphan_probes()`).
- `engine/uckp/registry.py:120-152` — `register()` runs `require_integrity()` and `require_lawful()` **per object**, checking identity and semantic-digest collision against objects admitted *so far*. It has no visibility into the full, final population — a category-exclusivity violation (two providers populating the same category) cannot be detected at this per-object admission moment, because the first of the two colliding objects admits cleanly; only a full-population pass, after every provider has run, can see the collision. Re-confirms and sharpens `PHASE-UCF-007`'s finding ("admission-time... governs identity collision, not facet content") with the specific mechanical reason why.
- `engine/uckp/intelligence.py:66-67, 71-85, 336-357` — a **second, structurally distinct severity model already exists** inside `engine/uckp/`: `Finding(reasoning, severity, subject, statement)` with `severity ∈ {VIOLATION, OBSERVATION}` (`intelligence.py:66-67`), used by `risk_reasoning()` to report non-blocking observations (e.g. `"carries constitutional authority with no certification"`) alongside a numeric `ownership_concentration` metric computed by tabulating `obj.ownership.owner` across the whole registry (`intelligence.py:336-351`) — the exact shape (tabulate a field across the whole population, report concentration/collision as a finding) a category-population check would need, already built and proven, just parameterized over a different field.
- `00-MASTER/UCOS-UGA-001/uga_engine.py:964, 1350-1493` — `CAA-INV-01..08`, a second invariant family, entirely separate from `UCKP-INV-01..17`, living at the UGA layer with its own namespace, home, and probes — direct precedent that this repository's answer to "a new bounded question needs an invariant" has twice been "start a new, separately-namespaced family," never "force it into the other family's fixed enumeration."
- `00-BOOK/DATA/observation-universe.json` — a **third** independent invariant family, `OBS-INV-01..06, 11-13`, confirming the sibling-family pattern is not a one-off (`CAA-INV` alone) but a repeated, three-times-proven repository practice (`UCKP-INV`, `CAA-INV`, `OBS-INV`, each independently namespaced, each bounded to a different question, none merged into another — the same `MULTIPLE_INDEPENDENT_AUTHORITIES` shape `existence_resolution` already declares generally).
- `00-MASTER/UCOS-UGA-001/uga_engine.py:1893-1899` — direct historical precedent for a **staged, sunset-conditioned advisory invariant**: *"UGA-INV-06 was carried as a non-blocking DECLARED-OPEN condition while `realization/` had a producer but no bootstrap path. That gap is discharged... so the exemption is removed with it. Keeping a carve-out for a condition that no longer exists would mean a future regression... could never fail this gate, which is the exemption outliving its reason — exactly how a gate quietly stops gating."* This is a real, executed precedent for exactly the lifecycle this document determines is correct for `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` (§ Failure Semantics), including the explicit warning against letting the advisory stage outlive its reason.
- `engine/uckp/validation.py:13-18` — the module's own stated caution, cited directly: *"This repository has already recorded the opposite defect once, as UCCEP-F-001 (a gate that could fail but never pass); the symmetric defect is a gate that can pass because it never looked."* A permanently-advisory check that never promotes is the mirror image of that recorded defect and is treated here as a real risk to design against, not a hypothetical one.

---

## Evidence Reviewed

- `engine/uckp/law.py:95-100, 203-395` — `UCKP_INVARIANTS` declaration and its module-level docstring on unmeasured/blocking semantics, full read.
- `engine/uckp/validation.py:1-350` — module docstring, `InvariantResult`, `ValidationReport`, `ConstitutionalValidator.probes()/unprobed()/orphan_probes()/validate_invariant()/validate()` — full read.
- `engine/uckp/registry.py:99-230` — `UniversalKnowledgeRegistry.register()`/`register_all()`/`replace()` — full read, confirming per-object (not whole-population) admission-time scope.
- `engine/uckp/intelligence.py:60-90, 330-360` — `Finding`, `ReasoningResult`, `risk_reasoning()` — full read; the only place in `engine/uckp/` where a non-blocking severity tier already exists.
- `engine/uckp/governance.py:35-45, 300-330` — `VERDICTS = (ANSWERED, PERMITTED, REFUSED)`, `_who_owns()` — confirmed a third, question-answering (not population-sweeping) decision shape, distinct from both `validation.py` and `intelligence.py`.
- `00-MASTER/UCOS-UGA-001/uga_engine.py:960-1500, 1880-1915` — `CAA-INV-01..08` declarations and the `cmd_gate()` blocking philosophy, including the UGA-INV-06 historical carve-out and its removal — full read.
- `00-BOOK/DATA/observation-universe.json` — `invariants` array — read to confirm `OBS-INV-*` exists as a third independent family.
- `PHASE-UCF-007 § Enforcement Ownership Analysis, § Invariant Determination` — re-cited, not re-derived, as the settled starting point for Invariant Ownership Analysis below.
- `PHASE-UCF-008 § Binding Model Determination, § Final Determination` — re-cited as the settled representation (`category_ownership_resolution` ledger) this document's evidence boundary depends on.

---

## Invariant Ownership Analysis

`PHASE-UCF-007` already evaluated candidates A–E and selected the UCKP invariant layer, on the basis that category membership, semantic identity, and duplication are already that layer's domain. This document does not reopen that selection; it examines a question `PHASE-UCF-007` did not reach — *given* the UCKP invariant layer is the right owner, what inside it can actually hold this invariant, mechanically.

| Candidate | Authority correctness | Scope alignment | Duplication risk | Existing pattern compatibility |
|---|---|---|---|---|
| **A. UCKP invariant layer** | Re-confirmed correct per `PHASE-UCF-007` | High, but the layer is not monolithic — it contains **two structurally distinct sub-homes** (see below), and which one fits depends on lifecycle stage | Low if the correct sub-home is chosen; high if forced into the wrong one (see Failure Semantics) | Two live, proven precedents exist inside this one layer |
| **B. UGA governance layer** | Re-confirmed incorrect per `PHASE-UCF-007` — `existence_resolution`'s own bounded question excludes `taxonomy.category` | Unchanged | Unchanged | Unchanged |
| **C. Registry validation (admission-time)** | Newly sharpened: **structurally cannot work as the primary check** — `register()`'s per-object scope (§ Current Repository Truth) means a category collision is invisible until the second colliding object admits, and even then only if checked at that exact moment; a whole-population pass is required for a sound verdict | Low as primary; unchanged as a *complementary*, post-hoc refusal point once a whole-population verdict already exists | Low, if implemented as a call into the same whole-population logic | Viable complement only, not a mechanism on its own |
| **D. Provider certification** | Unchanged: no certification mechanism exists for providers at all (`PHASE-UCF-006`) | N/A | N/A | Not the correct primary owner |
| **E. Combined responsibility model** | Refined, not rejected: A (whole-population measurement) is primary; C (admission-time) is a legitimate future complementary refusal point once A exists; B and D remain unjustified | — | — | — |

**Sharpened finding — Candidate A is not one home, it is two:**

| Sub-home | Shape | Severity model | Population scope | Precedent |
|---|---|---|---|---|
| `engine/uckp/validation.py` (`ConstitutionalValidator`) | Fixed, closed 17-probe dict, 1:1 with a closed `UCKP_INVARIANTS` tuple | **Blocking only** — no advisory tier exists here at all | Whole-registry, run once per `validate_universe()` call | `UCKP-INV-01..17`, and — outside this fixed tuple entirely — the proven sibling-family pattern `CAA-INV-01..08` / `OBS-INV-*` |
| `engine/uckp/intelligence.py` (`ReasoningResult`/`Finding`) | Open — any reasoner may emit any number of `Finding`s | **Advisory-capable** — `severity ∈ {VIOLATION, OBSERVATION}`, non-gating by construction | Whole-registry, e.g. `risk_reasoning()`'s existing `ownership_concentration` metric | The only place in `engine/uckp/` that already computes "concentration of a field's values across the whole population" — the exact shape category-population needs |

Adding a genuinely new, 18th member to `UCKP_INVARIANTS` is not a registration (the way a new `GOVERNED_CATEGORY` term is); `UCKP_INVARIANTS` is a closed, enumerated tuple the same architectural class as `Facet` — editing it is editing Layer Zero law directly, which this document is explicitly forbidden from doing and which, per this repository's own three-times-proven practice (`CAA-INV`, `OBS-INV` as siblings rather than merges), is not even the pattern this repository actually follows when a genuinely new bounded question arises.

**Selected ownership determination:** the UCKP invariant layer remains the correct owner (`PHASE-UCF-007`, unchanged), but concretely: (1) **today**, with no populated `category_ownership_resolution` ledger, the correct sub-home is `engine/uckp/intelligence.py`'s advisory-capable reasoning family, structurally extending `risk_reasoning()`'s existing concentration-measurement shape rather than inventing a new one; (2) **once the ledger is populated**, the correct future sub-home is a new, separately-namespaced invariant family living inside `engine/uckp/` — sibling to, not merged into, `UCKP-INV-01..17` — mirroring the `CAA-INV`/`OBS-INV` precedent, since a true `UCKP-INV-18` would require a law amendment this arc has consistently avoided when a sibling family serves the same purpose without one.

---

## Invariant Semantic Model

Building on `PHASE-UCF-007`'s conceptual sketch (unchanged, not re-derived) and `PHASE-UCF-008`'s chosen representation (the `category_ownership_resolution` ledger), a valid provider-category relationship requires, precisely:

1. **Provider identity exists** — the provider's dotted-module name appears in `discovery.provider` on at least one admitted object, or is a declared entry in `discover()`'s `providers_found`. Already available; no change required.
2. **Category exists** — the value appears in `GOVERNED_CATEGORY_VOCABULARY` (`taxonomy.category` passes `require_lawful()`). Already enforced today, at admission time, per object.
3. **Ownership authority exists** — a `category_ownership_resolution` entry names a bounded authority for that category. **Does not exist today** — `PHASE-UCF-008` determined the shape, not the content; the ledger has zero entries.
4. **Ownership resolution exists** — for a category populated by more than one provider, either exactly one is named authoritative, or plurality is explicitly declared and reconciled (the same `MULTIPLE_INDEPENDENT_AUTHORITIES` shape `existence_resolution` already uses). **Not yet possible to evaluate** — depends on (3).
5. **Provider relationship is permitted** — the specific `(provider, category)` pair being checked matches what (3)/(4) declare.

**PASS condition:** every category actually populated by more than one distinct `discovery.provider` value has a `category_ownership_resolution` entry that either names exactly one of them as sole authority, or explicitly lists all populating providers as a declared, reconciled plurality.

**FAIL condition:** a category is populated by more than one distinct `discovery.provider` value, and no `category_ownership_resolution` entry accounts for that plurality — the exact shape of the defect `PHASE-UCF-005` produced and self-corrected before commit.

**UNKNOWN condition — newly named, not present in `PHASE-UCF-007`'s sketch:** a category is populated by exactly one provider (no collision possible to detect), *and* no `category_ownership_resolution` entry exists for it either. This is not a violation (nothing collided) and not a clean pass (no authority was ever declared) — it is the state every one of the 14 actively-populated categories is in **today**, confirmed directly (`PHASE-UCF-008`'s ledger was determined, not populated). Naming this condition explicitly matters because collapsing it into PASS would silently certify an undeclared default as if it were a decision, and collapsing it into FAIL would make every provider newly non-certifiable the moment this invariant is switched on, for a condition that has never actually produced a defect. This three-way split is the direct, evidenced reason the current correct answer is advisory (§ Failure Semantics), not blocking.

---

## Evidence Boundary Determination

| Evidence source | Classification | Reasoning |
|---|---|---|
| **`discovery.provider` × `taxonomy.category` population map** | **Required** | Already available on every admitted object today; the exact shape `PHASE-UCF-007` computed by hand. No new field, no new source. |
| **`category_ownership_resolution` ledger** | **Required, once it exists** | `PHASE-UCF-008`'s determined representation; currently absent (§ Invariant Semantic Model, UNKNOWN condition). Its absence is precisely why the invariant cannot be blocking yet — not a defect of this document, a fact about present repository state. |
| **Category registry (`GOVERNED_CATEGORY_VOCABULARY`)** | **Required** | Already enforced at admission time (`require_lawful()`); needed here only to confirm a category name is itself lawful before asking who owns it — no new check. |
| **Provider registry (`discover()`'s `providers_found`)** | **Required** | Already available; confirms a `discovery.provider` value corresponds to an actually-discovered provider, not a stray string. |
| **Authority graph (`graph.py`'s edges)** | **Optional** | Useful only if the binding is ever promoted to a real UCKO (`PHASE-UCF-008`'s Option 3 future path) with its own `owns`-classified edges; not needed for the ledger-based (Option 4) representation this document evaluates. |
| **Provenance records** | **Optional** | Would let a future implementation explain *why* an ownership entry exists (which determination or actor declared it), matching how every other `*_resolution` section already carries an implicit provenance trail through git history; not required for a PASS/FAIL/UNKNOWN verdict itself. |
| **UCKO relationships (Facet 9)** | **Future** | Only becomes relevant if `PHASE-UCF-008`'s Option 3 (`ProviderCategoryOwnershipBinding` as a real UCKO, reusing the dormant `"relationship"` category and the registered `"ownership"` `RELATIONSHIP_CLASS` term) is ever built. Not applicable to the ledger-based representation. |

---

## Validation Boundary Determination

| Candidate | Tradeoff |
|---|---|
| **A. Provider discovery time** | Ruled out mechanically, not by preference: `register()`'s per-object admission scope (§ Current Repository Truth) cannot see the full population, so the earliest sound moment is *after* every provider's objects have admitted, not during any single provider's discovery |
| **B. Universe assembly time** | The moment `build_universe()` finishes combining `discover()`'s output with any assimilated objects — the full population exists, but this is a construction step, not itself a verification step, in the current architecture |
| **C. Certification time** | No certification surface currently consumes the UCKP population at all (`PHASE-UCF-006`: "nothing does yet, outside the `ucos-uckp` CLI itself") — correct in principle for a future certification-gating role, but nothing to hook into today |
| **D. Registry validation time** | The moment `validate_universe()`/`ConstitutionalValidator.validate()` runs — the full population is assembled, this is already the *existing* whole-population verification moment for all 17 UCKP-INV probes, and `risk_reasoning()` (the intelligence-layer precedent this document selects, § Invariant Ownership Analysis) already runs at this same whole-registry scope |
| **E. Continuous governance validation** | No precedent exists anywhere in this repository for a continuously-running (as opposed to on-demand, CLI/test-invoked) check — `validate_universe()`, `ukb.py enforce/validate`, and `verify_binding()` are all synchronous, invocation-triggered functions with zero scheduler, daemon, or watch-mode found in `engine/uckp/` or `00-BOOK/tools/`. Introducing one would be new infrastructure with no evidenced need, the exact caution `PHASE-UCF-006` already raised generally |

**Selected canonical boundary: the same moment the other whole-population UCKP measurements already run** — mechanically, whichever of `validate_universe()` (once/if promoted to blocking) or `risk_reasoning()` (today, advisory) is the invariant's chosen sub-home per Invariant Ownership Analysis. This is not a new timing concept; it reuses the timing both existing sub-homes already have. Option A is mechanically excluded; Option E has no infrastructure precedent to build on; Option C is correct in principle but has nothing to attach to yet; Option B is a necessary precondition (the population must be assembled) but not itself a verification moment.

---

## Failure Semantics

Five candidates were posed; this repository's own governance history resolves the choice directly rather than requiring a preference to be asserted.

- **A. Reject provider admission** — mechanically impossible today at the moment a violation becomes knowable (§ Invariant Ownership Analysis, Candidate C) — admission is per-object and happens before the whole-population collision is visible.
- **B. Reject universe certification** — the correct **target state**: this is exactly what a blocking `UCKP-INV`-shaped (or sibling-family) result already does for every one of the other 17/8/13 invariants in this repository, via `blocking_failures()` → `verdict = REFUSED`.
- **C. Mark provider uncertified** — not available as a distinct mechanism; no per-provider certification surface exists (`PHASE-UCF-006`), so this collapses into B or is not yet buildable.
- **D. Produce governance finding** — a real, available mechanism (`governance.py`'s `GovernanceDecision`/`VERDICTS`), but shaped for answering a specific asked question ("who owns X," "may X transition"), not for a whole-population sweep; less natural fit than the whole-registry-scoped alternatives.
- **E. Advisory observation only** — the correct **current state**, and only the current state: `engine/uckp/intelligence.py`'s `Finding(severity=OBSERVATION, ...)` is a real, already-proven, non-gating mechanism at exactly the right population scope (§ Invariant Ownership Analysis).

**Determination — staged, with a named promotion condition, directly modeled on the `UGA-INV-06` precedent (§ Current Repository Truth):**

1. **Now:** Observational only (E), via `intelligence.py`'s advisory `Finding` mechanism, extending `risk_reasoning()`'s existing concentration-measurement shape. This is not a weaker choice made for convenience — it is the only choice the Invariant Semantic Model's UNKNOWN condition permits without falsely certifying an undeclared default as a decision (collapsing UNKNOWN into PASS) or making every currently-uncontested category a certification failure for a condition that has never produced a defect (collapsing UNKNOWN into FAIL).
2. **Promotion trigger, named explicitly, per `validation.py`'s own stated caution against a check that "can pass because it never looked":** the day `category_ownership_resolution` is populated with real entries for the 14 actively-used categories (the concrete follow-on `PHASE-UCF-008` left open), the invariant should promote to blocking (B) — a sibling-family, whole-population probe, refusing certification exactly as `UCKP-INV-01..17` already do for their own domains.
3. **Explicit anti-pattern to avoid, cited directly from this repository's own recorded history:** letting the advisory stage persist past its reason, mirroring `uga_engine.py`'s own warning that an exemption outliving the condition that justified it is "exactly how a gate quietly stops gating." This document does not set the promotion trigger's date; it names its condition, so a future phase does not need to rediscover why the advisory stage was ever acceptable.

Option A is mechanically excluded; C collapses into B; D is available but not the best-fitting shape for a whole-population sweep.

---

## Existing Invariant Relationship

Re-examined directly against all three invariant families in this repository, not assumed:

- **`UCKP-INV-01` (knowledge-once)** — "No two canonical objects carry the same semantic identity." Does not cover category-population plurality: two objects sharing a `taxonomy.category` value have different `ucko_id`s and different semantic digests by construction; they are not claiming the same identity, only the same classification. **Not an extension candidate.**
- **`UCKP-INV-03` (zero-duplication)** — "No identity, content digest or canonical primitive is defined more than once." Concerns primitive/identity redefinition (e.g. `content_hash` implemented twice), a different failure class entirely from two providers legitimately minting distinct objects into the same category. **Not an extension candidate.**
- **`UCKP-INV-04` (zero-ambiguity)** — "Every facet is populated and every relationship target resolves." Structurally the closest by subject (taxonomy is a facet), but its actual probe, confirmed by direct read in `PHASE-UCF-007` and re-confirmed here, checks facet *presence*, never cross-provider *population exclusivity*. Extending its probe body would silently widen what `UCKP-INV-04`'s statement (unchanged in `law.py`) claims to measure — exactly the drift `validation.py`'s own docstring forbids ("each probe is bound to an invariant_id... a probe that carried its own copy of the statement could drift"). **Not a safe extension candidate**, for the same reason no probe may measure something its bound statement does not say.
- **`CAA-INV-01..08`** — bounded to authority-claim, identity-mint, and relationship-graph-ownership questions at the UGA/repository-artifact layer; none is bounded to `taxonomy.category`. **Not applicable**, confirming `PHASE-UCF-007`'s rejection of UGA as owner.
- **`OBS-INV-01..06, 11-13`** — bounded to observation/evidence-lineage separation at the platform layer; unrelated subject matter. **Not applicable.**

**Determination: none of the 17 existing UCKP invariants, nor either sibling family, already covers this question — re-confirming, not merely repeating, `PHASE-UCF-006`'s original finding.** `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` is neither an extension of an existing invariant (no existing statement covers it without drifting) nor collapsible into `CAA-INV`/`OBS-INV` (wrong subject domain). It is **derived validation** in its current, Observational stage — computed from already-collected `discovery.provider`/`taxonomy.category` evidence via the same code shape `risk_reasoning()`'s `ownership_concentration` metric already proves out, reusing an existing measurement pattern rather than inventing one (Article 18) — and would become a **new, independent, sibling-namespaced invariant family** (not a merge into the closed `UCKP-INV-01..17` tuple) only upon promotion to blocking.

---

## Future Implementation Boundary

Stated for planning; nothing here is built.

- **Files affected (advisory stage):** `engine/uckp/intelligence.py` (a new reasoning method or an extension of `risk_reasoning()`'s shape, parameterized over `taxonomy.category` instead of `ownership.owner`); no change to `law.py`, `validation.py`, or `vocabulary.py`.
- **Files affected (blocking-promotion stage, future):** a new sibling probe module/family (mirroring `uga_engine.py`'s `CAA-INV` or the `OBS-INV` home), plus whatever wiring exposes its verdict to `validate_universe()`'s callers or an equivalent gate command; `law.py` is touched only if the eventual design still prefers a true `UCKP-INV-18` over a sibling family, which this document does not recommend (§ Invariant Ownership Analysis).
- **Registries affected:** `00-BOOK/DATA/constitutional-authority-alignment.json` — first, adding the empty-shaped `category_ownership_resolution` section (`PHASE-UCF-008`'s determined representation); later, populating it with real entries for the 14 active categories (a one-time backfill, the same data `PHASE-UCF-007` already computed by hand).
- **Tests required:** a new test module (pattern: `test_uga_projection.py`/`test_assimilation.py`), covering the three named verdict conditions (PASS/FAIL/UNKNOWN) against synthetic multi-provider fixtures, plus a regression test pinning the real current 14-category/4-provider population so a future provider addition cannot silently reintroduce `PHASE-UCF-005`'s original defect.
- **Migration needs:** the `category_ownership_resolution` backfill above is the only migration-shaped step identified; no data format changes, no existing object mutation.

---

## Gap Reclassification

| Gap | Prior classification | This determination | Change |
|---|---|---|---|
| Provider category exclusivity has no general invariant | Required (`UCF-007`, confirmed `UCF-008`) | **Required — confirmed, now implementable in stages.** An Observational (advisory) implementation path is fully specified and unblocked by this document; the blocking path is specified but explicitly gated on the ledger backfill named in § Future Implementation Boundary | Refined — path now determined, still not built |
| Category ownership binding not yet populated (from `UCF-008`) | *(named, not separately classified)* | **Required, named explicitly as its own item now** — this document's entire Failure Semantics determination depends on it; leaving it unpopulated is the reason the invariant must start Observational rather than blocking | Elevated to its own explicit line |
| Semantic-duplicate category registration (Case 2) | Deferred | **Deferred — confirmed, unaffected** | Unchanged |
| Provider certification/pre-flight checklist | Deferred | **Deferred — confirmed, unaffected.** Failure Semantics' rejection of Option C (mark provider uncertified) reinforces rather than changes this — no such mechanism is being proposed here either | Unchanged |
| Onboarding documentation | Deferred | **Deferred — confirmed, unaffected** | Unchanged |
| Evolution History cross-domain view | Deferred | **Deferred — confirmed, unaffected** | Unchanged |
| No consumers of the expanded UCKP population | Observational | **Observational — confirmed, unaffected** | Unchanged |
| No performance data past current scale | Observational | **Observational — confirmed, unaffected** | Unchanged |
| **New: `UCKP_INVARIANTS` is a closed, non-registrable tuple, unlike `GOVERNED_CATEGORY`** | *(not previously named)* | **Observational.** A structural fact about Layer Zero, not a defect — consistent with `Facet`'s own closed-by-design pattern — but load-bearing for any future invariant-count growth, worth naming so a future phase does not assume category-style openness applies to invariants too | New finding |
| **New: a proven, executed precedent (`UGA-INV-06`) exists for staged advisory-to-blocking invariant promotion with an explicit sunset condition** | *(not previously named)* | **Observational.** Informs the recommended implementation approach; not itself a gap | New finding |

---

## Final Determination

`PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` remains correctly owned by the UCKP invariant layer (`PHASE-UCF-007`, unchanged), but that layer is not monolithic: it contains a closed, blocking-only measurement family (`validation.py`'s `ConstitutionalValidator`, fixed at exactly 17 probes) and a separate, open, advisory-capable reasoning family (`intelligence.py`'s `Finding`/`ReasoningResult`), and the correct sub-home depends on whether the invariant's evidentiary prerequisite — a populated `category_ownership_resolution` ledger (`PHASE-UCF-008`) — exists yet. It does not. Consequently, the correct implementation today is **Observational**: a derived-validation reasoner in `intelligence.py`, structurally extending the already-proven `risk_reasoning()` concentration-measurement shape over `taxonomy.category` instead of `ownership.owner`, running at the same whole-registry timing every other population-scoped UCKP measurement already uses. The correct future state, once the ledger is populated, is **blocking** — refusing certification exactly as `UCKP-INV-01..17` already do — realized as a new, separately-namespaced sibling invariant family (matching the twice-proven `CAA-INV`/`OBS-INV` precedent), not as an 18th member forced into `UCKP_INVARIANTS`'s closed tuple (which would be a law amendment) and not as a stretched reinterpretation of an existing invariant's statement (which every existing probe's own binding discipline forbids). None of the seventeen existing UCKP invariants, nor either sibling family, already covers this question — confirmed by direct re-examination, not assumed. The promotion condition from advisory to blocking is named explicitly, following this repository's own recorded caution against a check that can pass because it never looked, and its own recorded history of removing an advisory carve-out precisely when — and only when — the gap that justified it closes.

No code, test, registry, or constitutional change is made in this document.

### Unresolved questions, carried forward explicitly

1. Should the `category_ownership_resolution` backfill (populating real entries for the 14 active categories) happen as its own narrowly-scoped phase before the Observational reasoner is built, or alongside it? Not settled here.
2. Should the eventual blocking sibling family be scoped to category-ownership alone, or designed from the start to hold future UCKP-adjacent invariants that also don't fit the closed 17-tuple? This document determines that a sibling family is correct in kind; it does not scope its eventual breadth.
3. `PHASE-UCF-008`'s own open question — whether `Ownership.stewards` actually generalizes to "delegated category producers" — remains unresolved and is not touched by this document, since the Observational stage this document specifies needs no delegate concept to function.

---

Stopping after PHASE-UCF-009, as instructed. Minimum validation (`verify_binding()`, `discover()`, `validate_universe()`, `ukb.py enforce --pre`/`validate`) run fresh and reported under Current Repository Truth — no repository corruption found.
