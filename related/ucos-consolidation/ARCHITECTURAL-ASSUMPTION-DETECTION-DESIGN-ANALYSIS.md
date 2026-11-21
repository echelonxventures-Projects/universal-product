# UNIVERSAL ARCHITECTURAL ASSUMPTION DETECTOR DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UNIVERSAL-ARCHITECTURAL-ASSUMPTION-DETECTOR-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` |
| AUTHORITY | **NONE — DERIVED TRUTH.** No law is legislated, no declaration edited, no gate modified, no axis ratified. Every classification below is read from executing code or from declared data, never from a comment. |
| DISPOSITION | **DETERMINATION ONLY.** No detector built. No check added. |
| SUBJECT | The requested Universal Architectural Assumption Detector: detection of fixed ontology, hierarchy, layers, domains, entities, artifact categories, technology and infrastructure assumptions, example-becoming-law, and implementation-becoming-constitutional-dependency |
| BASELINE | HEAD `03179308f5cb` · branch `integration/recovery-001` · working tree unchanged across this determination |
| MODE | Read-only measurement. The one gate executed (`engine.infinite_scope.gate --quiet --json`) was verified to leave the tree byte-identical. |
| GOVERNING INSTRUMENTS | `00-MASTER/UISD-000001/uisd-declaration.json` · `ISD-L-03` (the principle inherits its own laws) · `CEP-007 II.2, XXII.3` (technology outside constitutional jurisdiction) |
| REFUSES | Building a second detector. Adding a law that would fail a correctly-closed enumeration. Claiming any dimension is agnostic without an executable check. |

> **Headline.** The detector already exists and passes. `engine/infinite_scope/` (UISD-000001) is a declaration-driven engine with **11 laws, 11 computable checks in bijection, 11 expansion axes, 11 disclosed closures and 11 recorded gaps**; executed at this baseline it returns `verdict: OPEN`, `11/11` laws holding, `self_applied: true`, `plane: OBSERVE MODE — READ ONLY`. The gap is not mechanism — it is **reach**. Every law binds only to subjects the declaration already names, so **an undeclared closed enumeration is invisible to it**, and of the directive's seven technology categories only two have any executable coverage at all.

---

## 0. What was measured, and with what

| Question | Command / file | Result |
|---|---|---|
| Does a detector exist and pass? | `python3 -m engine.infinite_scope.gate --quiet --json` | `verdict: OPEN` · `laws_measured: 11` · `laws_refused: 0` · all 11 `holds: true` |
| Is the gate read-only? | `git status --porcelain` hashed before/after the run | **identical** — tree unchanged |
| Is it self-applied? | same run | `self_applied: true` |
| Law/check bijection? | `engine/infinite_scope/contract.py:4-6` | `validate` *"refuses to construct a contract whose law names a missing check — or whose check no law claims"* |
| Declared laws / axes | `00-MASTER/UISD-000001/uisd-declaration.json` | `ISD-L-01..11` · `ISD-AX-01..11` (scope, direction, relationship, evolution, lifecycle, capability, technology, temporal, self, lifecycle-vocabulary, population) |
| Disclosed closures / gaps | same | `ISD-CE-01..11` · `ISD-G-01..11` |
| Any closure with undisclosed intent? | gate output | `closed_enumerations_unintentional: ["ISD-CE-09"]` |
| Is it wired into local enforcement? | `verify.sh:505,539` | Stage 6f — `"universal infinite scope and direction (UISD-000001, unbounded and self-applied)"` |
| Baseline temporal coverage | gate output | `baseline_surfaces: 4` · `baseline_surfaces_qualified: 1` |
| Technology pins disclosed | gate output | `declared_pins: 5` |

---

## 1. Current state

### 1.1 The eleven laws and what each actually detects

| Law | Detects |
|---|---|
| ISD-L-01 Scope Expansion Capacity | Enumerations closed **silently**. Does *not* forbid closure — requires each closure to name a closing invariant, an admission path, and either intent or a gap id. |
| ISD-L-02 Direction Expansion Capacity | Relationship-type space closed by schema (`enum` on the type property is forbidden). |
| ISD-L-03 | The principle is subject to its own laws. |
| ISD-L-04 | Lifecycle applies to itself; stage graph admits a stage without an engine change. |
| ISD-L-05 | No terminal stage; the cycle wraps. |
| ISD-L-06 | Proves openness by **performing** an in-memory extension each run, then proving the original vocabulary did not move. |
| ISD-L-07 | Freeze/permanence ratchet over declared roots: 9 phrases, a `FROZEN` status regex, 5 site classes, **16 preserved sites**. Class A (active declaration forbidding future change) is inadmissible by construction. |
| ISD-L-08 | Baseline surfaces parse a temporal coordinate or disclose they cannot. |
| ISD-L-09 | Technology-as-evolutionary-state: `pyproject.toml` runtime deps empty, `requires-python` carries no `<`, `<=` or `==`, and every optional pin is reconciled against disclosure **in both directions**. |
| ISD-L-10 | Capability model non-final; every capability enumeration names its admission path. |
| ISD-L-11 | AST literal-population detector + live admission exercise with a two-way refusal ratchet. |

### 1.2 The three reusable mechanisms already implemented

1. **Declared-root text ratchet** — `scan_occurrences` / `candidate_files`. Any occurrence in a scanned root that is not a declared preserved site is a violation.
2. **Positional AST literal classification** — `_population_literals` / `_literal_count_subject` resolve a comparison subject through up to six levels of local aliasing. `ACEE-000001`'s `check_no_enumeration` complements this by classifying findings as **EXECUTABLE GOVERNANCE** (a literal that can steer a branch — reported), **DECLARATION** (vocabulary from Repository Truth — exempt, and the exemption derived from the declaration's own keys so it cannot be widened by hand), or **PRESENTATION** (headings and labels — not reported).
3. **Live admission exercise** — build a synthetic member on a deep copy, push it through each declared consumer, and reconcile measured refusal against declared refusal as a ratchet in **both** directions: an undeclared refusal fails, and a stale declared refusal that no longer occurs also fails.

### 1.3 The doctrine that constrains any new law

Closure is not a defect; **undisclosed** closure is. `contract.py:16-20` states it plainly: `check_scope_expansion_capacity` *"does not assert that no enumeration is closed. That would be false — `engine/uckp/facets.py` closes 33 facets on purpose so that every vocabulary inside them can stay open — and a false law gets disabled."*

Second, a detector must not match its own source. `check_no_active_permanence_declaration` is named so as to avoid containing the token it searches for, *"because a detector that matches its own source is its own first finding."*

---

## 2. Discovered gaps

| ID | Finding | Grade |
|---|---|---|
| **AD-G-01** | **Detection is declaration-bound, not discovery-bound.** `ISD-L-01` and `ISD-L-10` audit only the 11 closures the declaration already lists. Nothing sweeps the repository for an *undeclared* `Enum`, `frozenset` or literal tuple. A new closed enumeration added tomorrow is invisible until a human discloses it — which inverts the intended direction of a detector. This is the single largest gap. | **CONFIRMED** |
| **AD-G-02** | **`ISD-L-09` is a manifest check, not a coupling check.** It parses `pyproject.toml` and nothing else. It never reads an import statement and never names a language, framework, cloud or protocol. The repository-wide stdlib-only audit that underwrites the "Technology CERTIFIED" verdict was performed by hand with `grep` and recorded in prose; **no gate re-runs it**, so it decays silently. | **CONFIRMED** |
| **AD-G-03** | **Four of the directive's seven technology categories have no executable check at all.** Coverage: Engineering — partial (manifest only). Data — partial (proven for `engine/uckp` alone). Software, Infrastructure, Communication, Experience, Tools — **none**. Per `UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md`, API/Communication is `SUPPORTED` (no violation found, no proof built), UI is `UNKNOWN` (no layer exists), Infrastructure and Tools are `SUPPORTED`. `SUPPORTED` is explicitly *not* certification. | **CONFIRMED** |
| **AD-G-04** | **"Example becoming law" and "current implementation becoming constitutional dependency" have no detector.** These are the two most consequential items on the directive's list, because they are how a finite assumption enters without anyone deciding it. Neither is expressible under any current law, and neither is a declared axis. | **CONFIRMED** |
| **AD-G-05** | **A closure with undisclosed intent is live right now.** `ISD-CE-09` — `KnowledgeCapability` in `engine/knowledge/ukip/constitution.py`, population 11, `intentional: false`, gap `ISD-G-01`. Its own disclosure records `closing_invariant: "NONE DECLARED IN CODE"` and notes the enum *"has no coercer and is frozen into `KNOWLEDGE_CAPABILITIES = tuple(KnowledgeCapability)`"*. The declaration names the correct in-package fix (`ProviderKind`, which carries a fail-closed coercer). | **CONFIRMED** |
| **AD-G-06** | **Baseline temporal qualification is 1 of 4.** `baseline_surfaces: 4`, `baseline_surfaces_qualified: 1`. Three baseline surfaces do not parse a temporal coordinate. Law `ISD-L-08` holds because the shortfall is disclosed, not because it is absent. | **CONFIRMED** |
| **AD-G-07** | **`check_no_enumeration` is replicated across ~20 programme engines.** Each `00-MASTER/*/\*_engine.py` defines its own. The implementations are not identical — `ACEE-000001`'s positional classifier is materially more sophisticated than the others. A defect fixed in one is not fixed in the rest. | **APPARENT** — enumerated by name and count; the ~20 bodies were not diffed line by line. |

---

## 3. Affected artifacts

**Would be extended:**
- `00-MASTER/UISD-000001/uisd-declaration.json` — `laws[]`, `expansion_axes[]`, `closed_enumeration_disclosures[]`, `gaps[]`
- `engine/infinite_scope/contract.py` — `LAW_CHECKS` (one pure function per new law)
- `verify.sh` — unchanged; stage 6f already invokes the gate, so a new law enforces automatically
- `.github/workflows/uisd-gate.yml` — **note**: it re-derives the 14 `verify.sh` stage labels and asserts a SHA-256 digest match, so any edit to a stage label breaks CI

**Would be read:** `engine/uckp/facets.py`, `engine/knowledge/model.py`, `engine/knowledge/ukip/constitution.py`, `engine/uckp/persistence.py`, `pyproject.toml`, `UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md`, `04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md`.

**Must not be touched:** all of `00-BOOK/DATA/`, `00-BOOK/REGISTRIES/`, and any `canonical_path` in `generated-artifact-registry.json`. Note also that ≥24 individual `*-gate` targets write tracked `00-MASTER/**` registers unconditionally, so they are not usable as read-only evidence sources.

---

## 4. Implementation impact

**Do not build a second detector.** `ISD-L-03` binds the principle to its own laws, and `--check-no-parallel-authority` across ACEE/UAIE/UCL makes a parallel detector a gate violation. New detection enters as **declaration entries plus checks in `LAW_CHECKS`**, held honest by the existing bijection.

The five proposed laws, in dependency order:

| Proposed | Closes | Mechanism to reuse | Blast radius |
|---|---|---|---|
| Undeclared-closure discovery | AD-G-01 | AST walk for `Enum` / `frozenset` / literal tuples across declared roots, reconciled **two-way** against `closed_enumeration_disclosures` | High — will find many; must land with disclosures, not with failures |
| Third-party import coupling | AD-G-02 | AST `Import`/`ImportFrom` walk over `engine/`, reconciled against a declared allow-list | Low — the audit already claims stdlib-only |
| Protocol / interface / infrastructure token coupling | AD-G-03 | `scan_occurrences` ratchet with declared preserved sites, exactly as `ISD-L-07` | Medium |
| Example-becoming-law | AD-G-04 | Detect a literal that appears in an illustrative artifact and is *also* an executable-governance operand elsewhere | Medium — needs a precise definition first |
| Implementation-as-constitutional-dependency | AD-G-04 | Detect a constitutional instrument naming a concrete module path as a normative dependency | Medium |

**Sequencing constraint.** The undeclared-closure law must be introduced in **observe-and-disclose** mode first. Introducing it as a blocking law immediately would fail the gate on legitimately-closed enumerations that have simply never been disclosed — converting a true finding into a false law, which the codebase's own doctrine says *"gets disabled."*

**Self-match hazard.** Every new scanner must exclude its own source and its own declaration, and must state the exclusion. Precedent: commit `1e2de714` recorded *"zero hardcoded planet literals outside anti-coupling gates"* — the exclusion clause is part of the finding, not a caveat on it.

---

## 5. Validation approach

Reuse the established six-step technique rather than inventing one. Distilled from commits `6785db4d`, `3e424148` and `1e2de714`:

1. **Locate** the literal, enumeration, pin or default; cite `file:line`.
2. **Separate references into plumbing vs. reading consumers.** Zero readers ⇒ defect class GP-4 "declared and never read" ⇒ delete. The rules explicitly forbid inventing a consumer to justify keeping it.
3. **Test the four authority axes by measurement, never assertion** — validation, ordering, serialization, discovery. Delete a listed member *and* an unlisted member and observe whether behaviour differs.
4. **Determine one of four dispositions**: remove (nothing reads it) · replace with a relational invariant (a test asserting cardinality) · replace with `None`-means-unspecified (a coupling default) · **disclose** (legitimately closed).
5. **Record governance lineage**: discovery id → ADR → work package → gate. New laws enter through the declaration, never through engine code.
6. **Validate and record numbers**: ruff clean, gate exit 0 with `N/N` laws/axes/disclosures, named test files with pass counts, and a repository scan with its exclusion clause stated.

**The cardinality rule, verbatim from `3e424148`, governs every test written for a new law:**

> *A test may assert what the relationship between members IS. It may not assert how many members there are, unless the cardinality is itself the domain invariant.*

Success criterion for each new law: the invariant stays true when the population grows — by one, by four thousand, or into a domain nobody has declared yet.

---

## 6. Risk assessment

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| AD-R-01 | A new law fails a correctly-closed enumeration, becomes a false law, and is disabled — costing more credibility than it buys | **HIGH** | Land in observe-and-disclose mode. Require disclosure, never absence of closure. |
| AD-R-02 | A scanner matches its own source or declaration | **MEDIUM** | Name-avoidance discipline plus an explicit, stated exclusion. |
| AD-R-03 | Building a parallel detector violates `ISD-L-03` and the no-parallel-authority checks | **HIGH** | Extend the declaration and `LAW_CHECKS` only. |
| AD-R-04 | The undeclared-closure sweep returns an unmanageable population and stalls | **MEDIUM** | Scope by declared root, one root at a time, disclosures first. |
| AD-R-05 | Editing a `verify.sh` stage label breaks the `uisd-gate.yml` digest contract | **MEDIUM** | Add no stage. Stage 6f already runs the gate. |
| AD-R-06 | An import scan claims agnosticism that vendored or dynamic imports evade | **MEDIUM** | Report the scan's blind spots as part of the verdict; claim `SUPPORTED`, not `CERTIFIED`, until dynamic import paths are covered. |
| AD-R-07 | "Example becoming law" is defined loosely and generates noise | **MEDIUM** | Define it as a measurable predicate — a literal that is both illustrative and an executable-governance operand — before writing the check. |

---

## 7. Acceptance criteria

1. The gate remains a single authority: `laws == len(LAW_CHECKS)`, bijection intact, construction refused otherwise. **Holds now (11/11).**
2. The gate remains read-only: tree byte-identical before and after. **Verified now.**
3. Every new law is a declaration entry with a computable check; no detection logic is reachable that the declaration does not name.
4. Undeclared-closure detection reports a two-way reconciliation: an undisclosed closure fails, and a stale disclosure whose subject no longer exists also fails.
5. Import coupling over `engine/` is measured by an executing check, not by prose, and the check states its exclusions.
6. Each of the directive's seven technology categories carries either a passing executable check or an explicit `GAP`/`UNKNOWN` verdict with an owner. No category is left implicitly certified.
7. `ISD-CE-09` / `ISD-G-01` is either closed by an owner act under `CEP-009`, or re-disclosed unchanged with its gap id intact. It is not quietly reclassified as intentional.
8. No test asserts a population count unless cardinality is itself the invariant.
9. No claim of the form "no fixed boundary exists" is made for any dimension lacking a passing check. Permitted wording is `SUPPORTED`.

---

## 8. Refusals

- Building the detector. Not performed.
- Executing the ~20 programme `*-gate` targets to survey their `check_no_enumeration` behaviour. Refused: ≥24 gate paths write tracked registers, which would breach the no-registry-mutation constraint. AD-G-07 is therefore graded **APPARENT**.
- Reading `engine/infinite_scope/gate.py` and `model.py` line by line. The gate's behaviour was measured by executing it; its internals are cited only where quoted.
- Resolving `ISD-G-02..ISD-G-11` by assumption. Their `subject`/`owner`/`measured_by` fields were read; the underlying code was not audited in this pass.
- Claiming technology agnosticism. `ISD-L-09` proves the manifest carries no runtime dependency and no version ceiling. It proves nothing about imports.

---

## 9. Determination

**EXISTS AND PASSES — REACH IS THE GAP, NOT MECHANISM.**

A Universal Architectural Assumption Detector is already operating, self-applied, read-only, wired into `verify.sh` stage 6f, and holding 11/11 laws at this baseline. Its three mechanisms — declared-root ratchet, positional AST classification, and live admission exercise with two-way reconciliation — are sufficient to build everything the directive asks for.

What the directive asks for that does not yet exist is **discovery** rather than audit, and **coupling** rather than manifest. The honest current position is: openness is *proven* on the axes that have checks, *supported* on the axes that have only manual inspection, and *unknown* where no layer exists. That distinction must survive into any future certification language.

**VERDICT: `DETERMINATION-COMPLETE · IMPLEMENTATION-NOT-AUTHORIZED`**

No law added, no declaration edited, no gate modified. Working tree unchanged.
