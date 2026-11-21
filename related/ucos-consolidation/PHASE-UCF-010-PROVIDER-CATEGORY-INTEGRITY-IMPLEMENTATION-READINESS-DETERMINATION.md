# PHASE-UCF-010 — PROVIDER CATEGORY INTEGRITY IMPLEMENTATION READINESS DETERMINATION

## 1. Document Identity

| Field | Value |
|---|---|
| Determination | PHASE-UCF-010-PROVIDER-CATEGORY-INTEGRITY-IMPLEMENTATION-READINESS-DETERMINATION |
| Mission | Determine whether the repository is ready to implement the provider category integrity capability specified across `PHASE-UCF-007` (owner), `PHASE-UCF-008` (representation), and `PHASE-UCF-009` (enforcement stage) |
| Mode | Determination only. Zero code, zero test changes, zero registry mutation, zero constitution changes, zero invariants, zero schemas, zero ownership records. |
| Date | 2026-08-14 |
| HEAD | `1f869865`, working tree unchanged from `PHASE-UCF-009 § Current Repository Truth` |

## 2. Purpose

`PHASE-UCF-009` determined *what* to build (an Observational, advisory category-integrity check inside `engine/uckp/`'s reasoning family) and *when it may promote* to blocking (once a `category_ownership_resolution` ledger is populated). It did not establish whether the repository can actually carry that implementation today. This document answers only that: which dependencies exist, which do not, what the smallest defect-detecting implementation is, exactly where it goes, and what must become true before enforcement can harden.

This is a readiness determination. Nothing is built.

## 3. Scope

In scope: dependency discovery and classification, the minimum implementation package for the `PHASE-UCF-005` contamination class, implementation-location selection among the five named options, Observational-stage prerequisites, Blocking-stage prerequisites and promotion criteria, testing readiness, governance impact, and gap reassessment.

Out of scope, per explicit instruction: implementing code, modifying tests, modifying registries, modifying the constitution, adding invariants, changing governance structures, introducing schemas, creating ownership records, running `./verify.sh`, and continuing to `PHASE-UCF-011`.

`PHASE-UCF-005` through `009` are treated as settled inputs and are not re-litigated. Where this document's direct measurement refines a figure those documents carried, the refinement is stated explicitly (§ 5) rather than silently absorbed.

---

## 4. Current Repository Truth

Measured fresh in this pass, not cited from prior turns:

| Check | Result |
|---|---|
| `verify_binding(constitutional-authority-alignment.json)` | `()` — **PASS** |
| `build_universe().registry.discover()` | `providers_found=('engine.uckp.alignment', 'engine.uckp.capabilities', 'engine.uckp.constitution', 'engine.uckp.uga_projection')`, `objects_admitted=5982`, `failures=()` |
| `validate_universe(build_universe())` (17 UCKP-INV) | `verdict='certified'`, `certified=True` |
| `00-BOOK/tools/ukb.py enforce --pre` | **PASS** — no unregistered or invalid artifact can silently enter the corpus |
| `00-BOOK/tools/ukb.py validate` | **PASS** — 1233 artifacts, append-only page ledger intact, referential integrity OK, 0 executions |

No drift from the `PHASE-UCF-007`/`008`/`009` baseline. No constitutional corruption.

**Newly measured in this pass** — the facts the readiness question actually turns on, none of which were measured directly in any prior determination:

| Measurement | Value |
|---|---|
| Objects carrying a non-empty `discovery.provider` | **5982 / 5982 (zero empty)** |
| Categories actually populated across the live universe | **21** |
| Categories populated by **more than one** provider | **0** |
| `GOVERNED_CATEGORIES` declared in `law.py` | 35 (14 declared-but-unpopulated) |
| `category_ownership_resolution` present in the alignment binding | **False** |
| `*_resolution` sections present in the alignment binding | 6 — `identity_authority`, `relationship_graph`, `certification_authority`, `identity_namespace`, `existence`, `lifecycle` |
| `*_resolution` sections with a **machine reader** anywhere in the repository | **2 of 6** — `relationship_graph_resolution`, `identity_authority_resolution` |

The live provider × category population map, measured directly:

| Category | Providers | Objects | Category | Providers | Objects |
|---|---|---|---|---|---|
| artifact | `capabilities` | 10 | observation | `capabilities` | 13 |
| authority | `alignment` | 17 | policy | `uga_projection` | 29 |
| capability | `capabilities` | 10 | principle | `constitution` | 20 |
| concept | `uga_projection` | 2394 | runtime | `capabilities` | 10 |
| constraint | `constitution` | 17 | state | `uga_projection` | 109 |
| engine | `uga_projection` | 1187 | taxonomy | `constitution` | 13 |
| governance | `capabilities` | 20 | transition | `capabilities` | 15 |
| identity | `alignment` | 1 | validation | `constitution` | 13 |
| knowledge | `uga_projection` | 1233 | verification | `uga_projection` | 801 |
| law | `constitution` | 1 | workflow | `uga_projection` | 36 |
| metadata | `constitution` | 33 | | | |

**Every one of the 21 populated categories has exactly one provider.** No category is contested today.

---

## 5. Evidence Reviewed

- `engine/uckp/intelligence.py` — **full read (604 lines).** `ReasoningKind` enum, `Finding`, `ReasoningResult`, all thirteen reasoners, `reasoners()`, `reason_all()`, `report()`.
- `engine/uckp/registry.py:80-97, 194-240, 301-330` — `DiscoveryReport`, `by_category()`/`by_owner()`/`by_kind()`, `providers()`, `discover()`.
- `engine/uckp/alignment.py:615-775` — `_relationship_findings()`, `_derivation_findings()`, `verify_binding()`, `require_aligned()`; and `ALIGNMENT_BINDING_PATH` (line 76) with every one of its references traced.
- `engine/uckp/universe.py:195-220` — `to_document()`, confirming where `intelligence().report()` surfaces.
- `engine/uckp/validation.py` — searched for any consumption of `intelligence`/`Finding`/`reason`; **zero hits** outside an unrelated projection-engine message at line 787.
- `engine/uckp/cli.py:250-260` — the `reason` and `certify` command paths.
- `00-MASTER/UCOS-UGA-001/uga_engine.py:64-79, 920-1010, 1155-1165, 1320-1480, 1593, 1735-1750` — every read the stdlib-only enforcing engine performs against the alignment binding, enumerated by key.
- `engine/tests/uckp/doubles.py` — **full read.** `RegistryView`'s complete surface and `registry_of()`.
- `engine/tests/uckp/conftest.py:88-135` — `mint_object`, `universe`, `assimilated` fixtures.
- `engine/tests/uckp/test_state_evolution_intelligence_governance.py:316-400, 750-980` — every intelligence-layer assertion, read individually.
- `engine/tests/uckp/test_cli_and_package.py:100-125` — the `reason` CLI assertions.
- `inspect.signature(UCKO.mint)` — evaluated live to confirm the parameter set available to test fixtures.
- `PHASE-UCF-005 §§ 2.2, 4`, `PHASE-UCF-007 § Enforcement Ownership`, `PHASE-UCF-008 § Binding Model Determination`, `PHASE-UCF-009 §§ Invariant Ownership Analysis, Invariant Semantic Model, Failure Semantics` — cited as settled inputs.

### Two figures carried by prior determinations, corrected by direct measurement

1. **"14 actively-populated categories"** (`PHASE-UCF-007`, repeated by `008` and `009`, and used by `009` to define the promotion trigger) is the **native-provider-only** histogram — `alignment`, `capabilities`, `constitution`. It predates counting `uga_projection`, which populates seven further categories (`concept`, `engine`, `knowledge`, `policy`, `state`, `verification`, `workflow`). The live figure is **21**. The native fourteen are reproduced exactly by this pass's measurement (`metadata=33`, `authority=17`, `constraint=17`, `governance=20`, `principle=20`, `transition=15`, `observation=13`, `taxonomy=13`, `validation=13`, `artifact=10`, `capability=10`, `runtime=10`, `identity=1`, `law=1`), so the two figures agree on their overlap; the difference is scope, not conflict. **Consequence: the backfill named in `PHASE-UCF-009`'s promotion trigger covers 21 categories, not 14.**

2. **"the ledger is already read by governance tooling and `verify_binding()`"** (`PHASE-UCF-008 § Binding Model Determination`, Option 4's auditability column) is true of the `*_resolution` pattern in general but **not of the three sections that determination cited as its precedent.** Traced by key: `verify_binding()` reads `relationship_graph_resolution` and `identity_authority_resolution` only; `uga_engine.py` reads those same two plus `authority_claim_scan`, `subordinate_instruments`, `authority_roles`, `supreme_authority`, `evidence_observation_separation`, and `object_model`. `existence_resolution`, `lifecycle_resolution`, `certification_authority_resolution`, and `identity_namespace_resolution` have **no machine reader anywhere in the repository** — `existence_resolution`'s only appearances outside the JSON are prose citations in `uga_projection.py`'s docstring. **Consequence: writing a `category_ownership_resolution` section does not, by itself, make its content available to any check. A reader is a separate, currently-nonexistent piece of work (§ 6, Dependency D3).**

Neither correction changes any prior *determination*; both change the size and shape of the work those determinations left open, which is precisely what this document exists to establish.

---

## 6. Dependency Discovery

Every dependency an implementation would need, classified against direct evidence.

### 6.1 Evidence and input dependencies

| # | Dependency | Status | Evidence |
|---|---|---|---|
| D1 | **Provider identity per object** (`discovery.provider`, Facet 21) | **Already Present** | Measured: 5982/5982 objects carry a non-empty value; zero empty. No new field, no provider change. |
| D2 | **Category assignment per object** (`taxonomy.category`) | **Already Present** | Mandatory on `UCKO.mint()`; enforced lawful at admission by `registry.register()`'s `require_lawful()`. 21 distinct values live. |
| D3 | **Category ownership evidence** (`category_ownership_resolution` ledger) | **Missing** | Confirmed absent from the binding by direct key check. `PHASE-UCF-008` determined its shape; no content exists. |
| D4 | **A reader that makes the ledger available to engine code** | **Missing** | No production code path in `engine/` opens `00-BOOK/DATA/constitutional-authority-alignment.json`. `alignment.py` declares `ALIGNMENT_BINDING_PATH` as a string constant and embeds it as metadata (line 405) but never opens it; `verify_binding()` is a pure function over a caller-supplied mapping. The only in-repo loads are `engine/tests/uckp/test_alignment.py:49` (test scope) and `uga_engine.py:1593` (a separate, stdlib-only process). **This is the single genuinely new piece of infrastructure the capability needs, and no prior determination named it.** |
| D5 | **Vocabulary relationship** (category name is a lawful `GOVERNED_CATEGORY`) | **Already Present** | `ROOT_LAW.governs()` / `is_non_authoritative()`, already exercised by `constitutional_reasoning()` (`intelligence.py:216-246`). |
| D6 | **Provider registry** (which providers were actually discovered) | **Already Present** | `DiscoveryReport.providers_found` and `registry.providers()`. Measured live: four providers. |

### 6.2 Infrastructure dependencies

| # | Dependency | Status | Evidence |
|---|---|---|---|
| D7 | **A whole-population measurement moment** | **Already Present** | Every one of the thirteen reasoners already iterates `self._registry.objects()` at whole-registry scope. `gap_reasoning()` (`intelligence.py:412-444`) already builds `{obj.taxonomy.category for obj in objects}` — the exact sweep required. |
| D8 | **An advisory (non-gating) severity tier** | **Already Present** | `Finding(severity=OBSERVATION)`, `intelligence.py:66-67`. `ReasoningResult.clean` is defined as `not violations` (line 101-102), so an OBSERVATION provably cannot flip a clean verdict. |
| D9 | **A category-grain finding subject convention** | **Already Present** | `gap_reasoning()` already emits `subject=f"category:{category}"` for category-level OBSERVATIONs (`intelligence.py:423`). No addressing scheme needs inventing. |
| D10 | **A reporting/visibility path** | **Already Present** | `ReasoningResult.findings` → `UniversalIntelligence.report()` → `ucos-uckp reason --json` (`cli.py:253`) and `universe.to_document()["intelligence"]` (`universe.py:215`). Zero new surface. |
| D11 | **An open extension point for a 14th *reasoning kind*** | **Missing** | `ReasoningKind` is a **closed 13-member enum**; `reasoners()` is a fixed 13-entry dict. Four assertions pin the count: `test_state_evolution_intelligence_governance.py:320, 322, 353` and `test_cli_and_package.py:116`. This is the same closed-enumeration class `PHASE-UCF-009` identified for `UCKP_INVARIANTS`. **Refinement of `PHASE-UCF-009`:** that determination characterised `intelligence.py` as "Open — any reasoner may emit any number of `Finding`s." That is exactly true at the *Finding* grain and exactly false at the *ReasoningKind* grain. The capability must therefore extend an **existing** reasoner, not add a fourteenth. This is not a blocker — it is a constraint that changes the implementation's shape (§ 7, § 8). |
| D12 | **An extension point for a new blocking invariant** | **Missing (Blocking stage only)** | `UCKP_INVARIANTS` is a closed 17-member tuple with a 1:1 hardcoded probe dict and `orphan_probes()` guarding both directions (`PHASE-UCF-009`, re-confirmed). A sibling family is the determined path; no such family exists inside `engine/uckp/`. Not required for the Observational stage. |

### 6.3 Certification and test-harness dependencies

| # | Dependency | Status | Evidence |
|---|---|---|---|
| D13 | **Certification isolation** (an advisory finding must not alter the certification verdict) | **Already Present** | `validation.py` contains zero references to `intelligence`, `Finding`, or any reasoner. Certification is computed solely from the 17 probes. An OBSERVATION cannot reach it. |
| D14 | **A synthetic multi-provider fixture path** | **Already Present** | `UCKO.mint()` accepts `provider=` (confirmed by live signature inspection), `mint_object` forwards arbitrary `**overrides`, `RegistryView` accepts any object tuple and exposes `objects()`, and `_reason(kind, *objects, vocabularies=...)` already wires the two together. Contamination fixtures are constructible today with no new harness. |
| D15 | **Test-assertion headroom** (extending a reasoner must not break pinned expectations) | **Already Present** | Every observation assertion is a keyed lookup (`result.observations["roots"] == 2.0`), never set-equality; every finding assertion is a substring match against joined statements. Neither form breaks on an added key or an added OBSERVATION. |
| D16 | **`RegistryView` parity with the methods a new check would call** | **Partially Present** | `RegistryView` exposes `objects()`, `ids()`, `get()`, `root_ids()`, `duplicate_semantics()`, `vocabularies()`, `graph()` — but **not** `by_category()`. An implementation that iterates `objects()` (as all thirteen existing reasoners do) works against the double unchanged; one that calls `registry.by_category()` would require extending the double. **This is an implementation constraint, not a missing dependency** — the conforming path is the one every existing reasoner already takes. |

### 6.4 Summary

| Status | Count | Dependencies |
|---|---|---|
| **Already Present** | 12 | D1, D2, D5, D6, D7, D8, D9, D10, D13, D14, D15 (and D16 on the conforming path) |
| **Partially Present** | 1 | D16 (`RegistryView` lacks `by_category()`; avoidable by construction) |
| **Missing** | 3 | D3 (ledger content), D4 (ledger reader), D11 (14th-kind extension point — sidestepped, not required), plus D12 for the Blocking stage only |

**Every dependency required to detect the `PHASE-UCF-005` contamination class is Already Present.** The three Missing dependencies (D3, D4, D12) are required only to distinguish a *declared-legitimate* plurality (PASS) from an *undeclared* one, and to promote to blocking — not to detect contamination itself.

---

## 7. Minimum Implementation Package

The smallest future implementation capable of detecting the `PHASE-UCF-005` contamination class. `PHASE-UCF-005 § 2.2` is the concrete referent: a newly added provider populated `metadata`, `runtime`, and `artifact` — categories already exclusively populated by native providers — and was caught only because one unrelated test happened to assert `by_category("metadata") == 33`. The defect class is therefore precisely: **a category acquiring a second distinct populating provider, with nothing declaring that plurality legitimate.**

### 7.1 Required inputs

| Input | Source | Availability |
|---|---|---|
| Provider identity | `obj.discovery.provider` | Present (5982/5982) |
| Category assignment | `obj.taxonomy.category` | Present |
| Vocabulary relationship | `ROOT_LAW.governs(category)` | Present |
| Authorized ownership evidence | `category_ownership_resolution` | **Absent — and not required for detection** (§ 7.2) |

### 7.2 Required processing

**Comparison model.** One pass over `registry.objects()`, accumulating `category → set(provider)`. A category whose provider set has cardinality > 1 is a *plurality*. This is the same tabulate-a-field-across-the-population shape `risk_reasoning()` already proves with `ownership_concentration` (`intelligence.py:336-351`) — reused, parameterised over `taxonomy.category` instead of `ownership.owner`, exactly as `PHASE-UCF-009` determined.

**Reasoning requirement.** Three-way, per `PHASE-UCF-009 § Invariant Semantic Model`:

| Condition | Rule | Live count today |
|---|---|---|
| **CONTAMINATION** | \|providers\| > 1 **and** no ledger entry reconciles them | **0** |
| **UNKNOWN** | \|providers\| == 1 **and** no ledger entry declares an owner | **21** |
| **PASS** | a ledger entry names sole authority or declares reconciled plurality | **0** (not computable — D3/D4 absent) |

**Evidence requirement.** Detection of CONTAMINATION requires **only D1 and D2**, both present. The ledger (D3/D4) is required solely to move categories out of UNKNOWN into PASS. A ledger-absent implementation is therefore not a degraded version of the check — it is the complete check for the demonstrated defect class, with PASS collapsed into UNKNOWN.

This is the load-bearing readiness finding: **the capability's detection power does not depend on the missing dependency.**

### 7.3 Required outputs

| Output | Realisation | New machinery? |
|---|---|---|
| Integrity finding | `Finding(reasoning=<existing kind>, severity, subject, statement)` | None — existing dataclass |
| Evidence reference | The populating provider names, stated in `statement`; the category in `subject`, using the established `category:{name}` convention (D9) | None |
| Confidence | Carried structurally, not numerically: CONTAMINATION is a measured fact over the full population; UNKNOWN is an explicitly named absence of declaration. The repository has no numeric-confidence primitive and inventing one is unjustified by any evidenced need. | None |
| Severity | `OBSERVATION` at this stage — for both CONTAMINATION and UNKNOWN, per `PHASE-UCF-009 § Failure Semantics` | None |
| Recommendation | Prose in `statement`, matching every existing reasoner's convention (e.g. `gap_reasoning`'s *"a governed category with no canonical object yet"*) | None |
| Population metrics | Additional keys in `ReasoningResult.observations` — e.g. `categories_populated`, `categories_multi_provider`, `categories_without_declared_owner` | None — additive, and D15 confirms no test pins the key set |

**Nothing beyond the demonstrated problem is designed here.** No delegation model, no numeric confidence scale, no per-provider certification, no transfer or retirement mechanism.

---

## 8. Implementation Location Analysis

| Option | Architectural authority | Separation of responsibility | Reuse alignment | Duplication risk | Dependency impact |
|---|---|---|---|---|---|
| **A. `engine/uckp/intelligence.py`** | Correct — Article 15 ("knowledge reasons about itself"); the only home in `engine/uckp/` with a non-gating severity tier (D8) | Clean — reports, never mutates, never gates (D13) | Highest — D7, D8, D9, D10 all already exist here; the concentration-measurement shape is proven | Low — reuses `Finding`/`ReasoningResult` verbatim | **Zero new dependencies.** Constrained by D11 (extend an existing reasoner) and D16 (iterate `objects()`, do not call `by_category()`) |
| **B. `engine/uckp/validation.py`** | Wrong for this stage — every probe is bound 1:1 to a declared `UCKP_INVARIANTS` member, all blocking, with `orphan_probes()` refusing an unbound probe. There is no advisory tier here at all. | Would require either a law amendment (18th invariant) or a probe measuring something no statement declares — forbidden by the module's own binding discipline | Low | High — would force UNKNOWN into PASS or FAIL, the exact collapse `PHASE-UCF-009` ruled out | Requires D12 and a constitutional amendment |
| **C. Provider layer** | Wrong — `PHASE-UCF-008 § Category Ownership Model Analysis, Option B`: self-declaration cannot arbitrate a collision between two self-declarers. Structurally incapable of preventing the defect it targets. | Inverted — the party whose interest is at stake would adjudicate | None | High | Would require a federation contract nothing yet consumes |
| **D. Registry layer** | Mechanically impossible as primary — `register()` is per-object and admits the first of two colliding objects cleanly; the collision is invisible until the whole population exists (`PHASE-UCF-009`, re-confirmed) | N/A | N/A | N/A | N/A |
| **E. Mixed** | Premature — a mixed model presupposes a blocking half that cannot be built until D3/D4/D12 exist | Adds coordination cost with no present benefit | N/A | Two homes for one rule | Inherits every missing dependency |

### Selected location: **Option A — `engine/uckp/intelligence.py`**

This confirms `PHASE-UCF-009`'s selection and adds the mechanical constraints that determination did not reach:

1. **Extend an existing reasoner; do not add a fourteenth `ReasoningKind`** (D11). Adding a kind breaks four pinned assertions across two test files and edits a closed enumeration — the same architectural class as `UCKP_INVARIANTS`, which this arc has consistently declined to open.

2. **Host reasoner — `gap_reasoning()`, refining `PHASE-UCF-009`'s reference to `risk_reasoning()`.** `PHASE-UCF-009` cited `risk_reasoning()` for its *measurement shape* (tabulate a field across the whole population), and that citation stands — the shape is what is reused. But the *host* is better placed in `gap_reasoning()`, on three pieces of evidence unavailable to that determination:
   - `gap_reasoning()` already addresses category-grain subjects as `category:{name}` (`intelligence.py:423`); `risk_reasoning()`'s subjects are uniformly `obj.ucko_id`, so hosting a category-grain finding there would break its own subject convention.
   - `gap_reasoning()` already emits `OBSERVATION` for category-level conditions; `risk_reasoning()`'s OBSERVATIONs are per-object certification observations.
   - The UNKNOWN condition — *a category is populated but no authority was ever declared for it* — is semantically a gap, matching `gap_reasoning()`'s existing statement form *"a governed category with no canonical object yet"* almost exactly.

   `constitutional_reasoning()` is the natural host if a VIOLATION-severity in-engine variant is ever wanted before the sibling family exists, since it is already the reasoner that adjudicates `taxonomy.category` against `ROOT_LAW`. This document does not recommend that; it names it so a future phase does not have to rediscover it.

3. **Iterate `registry.objects()`; do not call `registry.by_category()`** (D16), so the existing `RegistryView` double keeps working unmodified.

---

## 9. Observational Readiness

### Trigger

**Determination: the existing reasoning pass — no new trigger.** `UniversalIntelligence.reason_all()`/`report()`, reached today by `ucos-uckp reason`, `ucos-uckp describe`, and `universe.to_document()`.

| Candidate | Assessment |
|---|---|
| Discovery | Mechanically excluded — per-object admission cannot see the population (D-layer analysis, § 8 Option D) |
| Validation | Wrong tier — no advisory severity exists there (§ 8 Option B) |
| Certification | Nothing to attach to — `validation.py` does not consume intelligence findings (D13), and `PHASE-UCF-006` established no certification surface consumes the UCKP population |
| **Explicit reasoning pass** | **Selected** — already whole-population, already advisory, already invoked by CLI and tests |

### Evidence collection

| Evidence | Source | Status |
|---|---|---|
| Source data | `registry.objects()` | Present |
| Provider evidence | `obj.discovery.provider` | Present — 5982/5982 |
| Category evidence | `obj.taxonomy.category` | Present — 21 populated |
| Ownership evidence | `category_ownership_resolution` | **Absent — and not required at this stage** (§ 7.2) |

### Finding generation

- **Structure:** `Finding(reasoning="gap", severity=OBSERVATION, subject=f"category:{name}", statement=<prose naming the populating providers>)`. Existing dataclass, existing conventions.
- **Reporting path:** `ReasoningResult.findings` → `report()` → `ucos-uckp reason --json` and `describe --json` → `to_document()["intelligence"]`. No new surface.
- **Visibility:** advisory and non-gating by construction. `clean` is `not violations`, so 21 OBSERVATIONs cannot flip `payload["clean"] is True` (`test_cli_and_package.py:117`), and certification is computed without reference to intelligence at all (D13).

### Are prerequisites already available?

**Yes — all of them.** Every dependency the Observational stage requires (D1, D2, D5, D6, D7, D8, D9, D10, D13, D14, D15) is Already Present and directly measured. The two Missing evidence dependencies (D3, D4) bear on PASS/UNKNOWN discrimination, not on detection. The one closed extension point (D11) is a shape constraint that § 8 resolves without opening anything.

**The Observational stage has zero blocking dependencies.**

---

## 10. Blocking Readiness

### Ownership evidence requirements

| Requirement | Status |
|---|---|
| `category_ownership_resolution` section exists in the alignment binding | **Missing** (D3) |
| The section is populated for all **21** populated categories — not the 14 named in `PHASE-UCF-009`'s trigger (§ 5, correction 1) | **Missing** |
| A production reader makes the section available to engine code | **Missing** (D4) — no `engine/` code path opens the binding today |
| Authority resolution for legitimate plurality (`MULTIPLE_INDEPENDENT_AUTHORITIES` shape) | Shape determined (`PHASE-UCF-008`); no content |
| Stewardship / delegation model | Not required; explicitly deferred (`PHASE-UCF-008` open question 2, `PHASE-UCF-009` open question 3) |

### Governance requirements

| Requirement | Status |
|---|---|
| Approved ownership model | **Present** — `PHASE-UCF-008 § Binding Model Determination` selected Option 4 |
| Conflict resolution mechanism (what happens when two providers legitimately contest a category) | **Missing** — no determination has specified adjudication, only representation |
| A sibling invariant family home inside `engine/uckp/` | **Missing** (D12) — precedent exists (`CAA-INV`, `OBS-INV`) but no such family exists in this package |
| Non-breakage of the binding's existing verifiers | **Confirmed available** — `verify_binding()` applies no section whitelist (unknown keys are ignored), and `uga_engine.py`'s structural fingerprint (line 1160-1161) draws only from `authority_roles` and `relationship_kind_bindings`, so an added top-level section perturbs neither |

### Migration requirements

| Requirement | Status |
|---|---|
| Existing categories classified | **Done, by this document** — the 21-row population map in § 4 is the complete input the backfill needs |
| Ownership populated | **Missing** — 0 of 21 declared |
| Ambiguity removed | **Already true** — zero categories are contested today (§ 4), so the backfill is a mechanical restatement of an uncontested measurement, not an adjudication. This is the least risky moment this migration will ever have. |

### Promotion criteria

| Stage | Entry criteria | Met? |
|---|---|---|
| **Observational** | D1, D2, D5, D6, D7, D8, D9, D10 present; host reasoner selected; detection reachable without ownership evidence | **Met in full — today** |
| **↓ Observational → Advisory** | (a) `category_ownership_resolution` exists and is populated for all 21 populated categories (D3); (b) a production reader exposes it to engine code (D4); (c) the check distinguishes PASS from UNKNOWN, so UNKNOWN's population falls from 21 toward 0; (d) a regression fixture pins the real 21-category / 4-provider population so a new provider cannot silently re-create `PHASE-UCF-005`'s defect | **Not met** — (a), (b), (d) outstanding |
| **↓ Advisory → Blocking** | (e) UNKNOWN is empty — every populated category carries a declared owner or a declared reconciled plurality; (f) a conflict-resolution rule exists for contested categories; (g) a sibling invariant family home exists inside `engine/uckp/` with its own namespace and probe binding (D12); (h) the ledger is covered by `verify_binding()` or an equivalent verifier, so the evidence the gate depends on cannot itself drift unchecked | **Not met** — all five outstanding |

Criterion (h) is added by this document and follows directly from § 5, correction 2: promoting to blocking against an unverified ledger would gate certification on a data file that nothing checks for internal consistency — a gate resting on unverified evidence, which is the same failure family as `validation.py`'s own recorded caution about a check that "can pass because it never looked."

---

## 11. Testing Readiness

No tests are implemented, designed in code, or modified here.

| Scenario | Fixture need | Reusable today? |
|---|---|---|
| **Positive case** — valid provider-category relationship | Two objects, same `provider`, same `category` | **Yes** — `mint_object(..., category=X, provider=P)` + `RegistryView` + `_reason(...)`; all exist |
| **Contamination case** — two providers, one category | Two objects, differing `provider`, same `category` | **Yes** — same toolchain. `UCKO.mint()` accepts `provider=` (verified live); `mint_object` forwards it through `**overrides` |
| **Unknown state case** — category populated, no ownership evidence | Any object, ledger absent or silent | **Yes** — this is the live repository state; also reproducible synthetically |
| **Ownership conflict case** — two authorities claim one category | A ledger document declaring two competing owners | **No** — requires D3/D4 first. This is the **only** scenario of the four not constructible today, and it is a Blocking-stage scenario, not an Observational one |

**Reusable fixtures:** `mint_object` (conftest), `vocabularies` (conftest), `RegistryView` and `registry_of` (doubles), `_reason()` and `_statements()` helpers (`test_state_evolution_intelligence_governance.py:765-775`), and the `universe` session fixture for real-population regression.

**Required new fixtures:** none for the three Observational scenarios. A ledger-document fixture is required for the conflict case, at the Advisory/Blocking stage.

**Certification impact: none.** Adding OBSERVATION findings and observation keys to an existing reasoner cannot break the suite, on three independently confirmed grounds (D15, D13, D8): observation assertions are keyed lookups rather than set equality; finding assertions are substring matches; and `clean`/`certified` are computed from violations and the 17 probes respectively, neither of which an OBSERVATION reaches. The four count-pinning assertions (`== 13`) are triggered only by adding a `ReasoningKind`, which § 8 determines against.

One residual test-design caution, named so it is not discovered late: a regression fixture pinning "21 categories, each with exactly one provider" is the mechanism that would actually have caught `PHASE-UCF-005`'s defect at the right moment. `PHASE-UCF-005` was caught by an unrelated assertion (`by_category("metadata") == 33`) — an accident, not a designed gate. That fixture is listed as promotion criterion (d).

---

## 12. Governance Impact

| Requirement | Observational stage | Blocking stage |
|---|---|---|
| **Constitutional amendment** | **Not required.** `intelligence.py` is Layer Zero, but extending a reasoner changes no Article, no invariant, and no stop condition. `verify_binding()` checks `articles=20`, `invariants=17`, `stop_conditions=13` against `ROOT_LAW`; none moves. | **Not required** if the sibling-family path is taken (`PHASE-UCF-009`); required only if a true `UCKP-INV-18` is preferred, which `PHASE-UCF-009` recommends against |
| **New invariant family** | **Not required** | **Required** (D12) — separately namespaced, sibling to `UCKP-INV`, matching `CAA-INV`/`OBS-INV` precedent |
| **Governance registration** | **Not required** — no ledger write occurs at this stage | **Required** — the `category_ownership_resolution` section plus its 21-row backfill |
| **Authority update** | **Not required** — ownership of this question was settled by `PHASE-UCF-007` (UCKP invariant layer) and unchanged by `008`/`009`/this document | **Not required** |
| **None** | — | — |

**Conclusion: the Observational stage requires no governance action of any kind.** Supporting evidence: `validate_universe()` does not consume intelligence findings (D13); `verify_binding()`'s counts derive from `ROOT_LAW`, which is untouched; `ukb.py enforce/validate` govern artifact registration, not engine internals; and no registry file is written. The Blocking stage requires governance registration (the ledger) and a new invariant family, both already determined in kind by `PHASE-UCF-008`/`009`.

---

## 13. Gap Reassessment

| Gap | Prior classification | This determination | Basis |
|---|---|---|---|
| Provider category exclusivity has no general invariant | Required (`007`–`009`) | **Required — Observational implementation fully unblocked.** Location, host reasoner, inputs, processing, outputs, trigger, and finding structure are all now determined with zero missing dependencies | § 6–§ 9 |
| `category_ownership_resolution` not populated | Required (`009`) | **Required — for Advisory/Blocking only, not for detection.** Scope corrected: 21 categories, not 14 | § 5.1, § 7.2, § 10 |
| **New: the ledger has no production reader** | *(not previously named)* | **Required — for Advisory/Blocking only.** The single genuinely new piece of infrastructure the capability needs; 4 of 6 `*_resolution` sections, including all three cited as the pattern's precedent, have no machine reader | § 5.2, D4 |
| **New: `ReasoningKind` is a closed 13-member enum, pinned by 4 assertions** | *(not previously named)* | **Observational.** A structural fact, not a defect — the same closed-enumeration class as `UCKP_INVARIANTS` and `Facet`. Load-bearing: it determines the implementation's shape (extend, don't add) | D11 |
| **New: `RegistryView` lacks `by_category()`** | *(not previously named)* | **Observational.** Avoidable by construction — iterate `objects()`, as all thirteen reasoners already do | D16 |
| **New: no conflict-resolution rule for contested categories** | *(not previously named)* | **Deferred.** Zero categories are contested today; specifying adjudication ahead of any evidenced conflict is exactly the speculative-infrastructure pattern `PHASE-UCF-006` cautioned against. Named as Blocking criterion (f) | § 10, § 4 |
| **New: "14 active categories" is a native-only figure; the live count is 21** | *(not previously named)* | **Closed** — measured, corrected, and the complete 21-row map recorded in § 4 as the backfill's input | § 4, § 5.1 |
| **New: contamination-case fixtures are constructible today** | *(not previously named)* | **Closed** — `UCKO.mint(provider=...)` + `mint_object` + `RegistryView` + `_reason()` verified sufficient for three of four scenarios | § 11, D14 |
| **New: certification is provably isolated from advisory findings** | *(not previously named)* | **Closed** — `validation.py` has zero references to intelligence; `clean` is `not violations` | § 12, D13 |
| Semantic-duplicate category registration (Case 2) | Deferred | **Deferred — unchanged** | `007`–`009` |
| Provider certification / pre-flight checklist | Deferred | **Deferred — unchanged.** § 8 Option C reconfirms provider self-declaration is the wrong mechanism | § 8 |
| Onboarding documentation | Deferred | **Deferred — unchanged** | `007`–`009` |
| Evolution History cross-domain view | Deferred | **Deferred — unchanged** | `007`–`009` |
| Vocabulary-term registration has no registrar capture | Observational | **Observational — unchanged** | `008` |
| `"relationship"` category is the future home for an ownership-binding UCKO | Observational | **Observational — unchanged.** Re-measured: still zero population | § 4 |
| No consumers of the expanded UCKP population | Observational | **Observational — unchanged** | `006` |
| No performance data past current scale | Observational | **Observational — unchanged.** The check is a single O(n) pass over 5,982 objects, alongside thirteen existing passes of the same order | § 7.2 |
| `UCKP_INVARIANTS` is a closed, non-registrable tuple | Observational (`009`) | **Observational — confirmed, and now shown to generalise:** `ReasoningKind` is closed in the same way. The pattern is architectural, not incidental | D11, D12 |
| Staged advisory→blocking promotion precedent (`UGA-INV-06`) | Observational (`009`) | **Observational — confirmed; promotion criteria now made concrete** in § 10 | § 10 |

**Required: 3** (invariant unbuilt; ledger unpopulated; ledger reader absent — the latter two for Advisory/Blocking only).
**Deferred: 5.** **Observational: 8.** **Closed: 3.**

---

## 14. Final Readiness Determination

# CONDITIONALLY READY

The condition is **scope, not capability**: the repository is fully ready to implement the Observational stage and is not ready for Advisory or Blocking enforcement.

### READY — Observational stage, zero blocking dependencies

Every input the check needs is present and directly measured: `discovery.provider` on 5982/5982 objects, `taxonomy.category` on all of them, the whole-population sweep, the advisory severity tier, the category-grain subject convention, the reporting path, and the synthetic-fixture toolchain. Critically, **detecting the `PHASE-UCF-005` contamination class does not require the missing ownership ledger** — ownership evidence is needed only to excuse a legitimate plurality (PASS), never to detect an unexcused one.

**Exact implementation package:**

1. **Location:** `engine/uckp/intelligence.py`, extending `gap_reasoning()` — not a fourteenth `ReasoningKind` (closed enum, four pinned assertions), and not `validation.py` (no advisory tier, closed probe dict).
2. **Processing:** one pass over `registry.objects()` accumulating `category → set(provider)`; reuse `risk_reasoning()`'s tabulate-across-the-population shape, parameterised over `taxonomy.category`. Iterate `objects()`; do not call `by_category()` (keeps `RegistryView` working).
3. **Verdicts:** CONTAMINATION (\|providers\| > 1, unreconciled) and UNKNOWN (\|providers\| == 1, no declared owner). PASS is not computable until the ledger exists and collapses into UNKNOWN until then.
4. **Output:** `Finding(reasoning="gap", severity=OBSERVATION, subject=f"category:{name}", statement=<naming the populating providers>)`, plus additive `observations` keys.
5. **Tests:** positive, contamination, and unknown-state scenarios via `mint_object(provider=…)` + `RegistryView` + `_reason()`; plus a regression fixture pinning the live 21-category / 4-provider population.
6. **Expected effect on today's repository:** 21 UNKNOWN observations, 0 contamination findings, `clean` unchanged, `certified` unchanged.

### NOT READY — Advisory and Blocking stages

**Exact blocking dependencies:**

| # | Dependency | Stage gated |
|---|---|---|
| B1 | `category_ownership_resolution` section added to `00-BOOK/DATA/constitutional-authority-alignment.json` | Advisory |
| B2 | That section populated for all **21** populated categories (not 14) | Advisory |
| B3 | A production reader exposing the ledger to engine code — **no `engine/` path opens the binding today**; this is the one piece of genuinely new infrastructure | Advisory |
| B4 | A regression fixture pinning the real population so a new provider cannot silently repeat `PHASE-UCF-005` | Advisory |
| B5 | UNKNOWN reduced to empty — every populated category carries a declared owner or declared reconciled plurality | Blocking |
| B6 | A conflict-resolution rule for contested categories | Blocking |
| B7 | A sibling invariant family home inside `engine/uckp/`, separately namespaced (not an 18th member of the closed `UCKP_INVARIANTS` tuple) | Blocking |
| B8 | The ledger itself covered by `verify_binding()` or an equivalent verifier, so a gate does not come to depend on unverified evidence | Blocking |

No code, test, registry, schema, invariant, governance structure, or ownership record was created or modified by this document.

### Unresolved questions, carried forward explicitly

1. Should the ledger reader (B3) live in `alignment.py` (which already owns the binding's contract and declares its path) or in a new module? `alignment.py` is stdlib-discipline-sensitive and currently pure-functional over a caller-supplied mapping — adding file I/O there changes its character. Not settled here.
2. Should the backfill (B1/B2) be its own narrowly-scoped phase, or land with the Advisory implementation? `PHASE-UCF-008`'s open question 1 and `PHASE-UCF-009`'s open question 1, both still open. This document adds one input to the decision: the backfill is at its lowest-risk moment right now, because zero categories are contested.
3. Should the four `*_resolution` sections that have no machine reader (`existence`, `lifecycle`, `certification_authority`, `identity_namespace`) be brought under a verifier as a general repository concern, rather than solving reader-coverage once for `category_ownership_resolution` alone? Newly raised by § 5.2; outside this arc's scope and not answered here.
4. `PHASE-UCF-008`'s open question 2 — whether `Ownership.stewards` generalises to delegated category producers — remains unresolved and is not needed by the Observational stage.

---

Stopping after PHASE-UCF-010, as instructed. Minimum validation (`verify_binding()`, `discover()`, `validate_universe()`, `ukb.py enforce --pre`, `ukb.py validate`) run fresh and reported under § 4. `./verify.sh` was not run, no repository content was modified, and PHASE-UCF-011 was not started.
