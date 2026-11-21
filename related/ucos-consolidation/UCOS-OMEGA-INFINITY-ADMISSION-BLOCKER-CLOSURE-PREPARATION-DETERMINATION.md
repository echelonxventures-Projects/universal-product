# UCOS Ω∞ — ADMISSION BLOCKER CLOSURE PREPARATION DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-ADMISSION-BLOCKER-CLOSURE-PREPARATION-DETERMINATION.md` |
| KIND | `CMG-K-17` — Determination |
| STANDING | **DECLARATIVE** (`CMG-000001` XII.6) |
| AUTHORITY | **NONE — DERIVED TRUTH.** Prepares closure actions; performs none. Creates no requirement, ADR, identifier, or authority. Mutates no code, configuration, registry, or certification. Not registered in `CMG-REGISTRY.json`; **SHALL NOT be cited as constitutional authority** (`CMG-L-01`). |
| MODE | **OBSERVE.** Controlled preparation only. |
| MUTATION | **READ-ONLY OBSERVATION.** The single mutation is the creation of this file. |
| PREPARES CLOSURE FOR | `UCOS-OMEGA-INFINITY-IMPLEMENTATION-ADMISSION-READINESS-DETERMINATION.md` blockers `B-1`…`B-6` |
| BASELINE | HEAD `bae59755` · `integration/recovery-001` · 16 modified tracked · 59 untracked |
| EVIDENCE CLASS | Every closure action below was either **executed and reverted** in a controlled probe this session, or has a **named precedent** in the corpus. No action is proposed on reasoning alone. |
| SCOPE DISCIPLINE | No unrelated capability. No scope expansion. No duplicate system. Disposition vocabulary: **REUSE · EXTEND · COMPOSE · HOLD**. CREATE appears **zero times**. |

---

## SECTION 0 — PREPARATION BASIS AND WHAT CHANGED SINCE THE ADMISSION DETERMINATION

### 0.1 Three measurements have moved. All in the adverse direction.

| Measure | Admission determination | Now | Movement |
|---|---|---|---|
| Ownership subjects | 542 | **549** | +7 |
| Ownership declared | 151 | **151** | 0 |
| Ownership coverage | 27.86% | **27.5046%** | **regressing** |
| Ownership unresolved | 391 | **398** | +7 |
| `*-gate` targets | 46 | **49** | +3 |
| `verify.sh` stages failing | 2 of 10 (reported) | **4 of 15 (measured)** | measured, not comparable |

The ownership figure is the one that matters for sequencing: **subjects are entering faster than owners are declared**, so coverage falls without anything failing. A closure plan that does not account for inflow will not converge.

### 0.2 The canonical verification baseline, measured this session

`./verify.sh --full` — 15 stages, 4 failed, ~44 min, log at `/tmp/ucos-verify-full.log`:

| Stage | Root cause |
|---|---|
| `pytest + coverage gate` | `test_infinite_scope` (6) · `test_mutation_classification` (many) · `test_observation_universe` (1) · `test_uaue_controller` (1) |
| `universal object governance (UGA-INV-01..10)` | **43 anonymous objects** — indexed files carrying no universal identifier |
| `evolution surface replay` | UAUE drift — **1,316,175 bytes committed vs 1,316,175 projected**; equal length, unequal content |
| `universal infinite scope (UISD-000001)` | verdict **CLOSED** — `ISD-L-07` refuses on **2** permanence occurrences |

All four are **pre-existing**. None was introduced by this session.

### 0.3 Two controlled probes, both reverted — and what they establish

Recorded because a closure plan whose actions have been *executed once* is stronger evidence than one that has not.

**Probe 1 — the 43-object mint.** I invoked `uga_engine.py run` (the minting subcommand) while intending observation. It minted 43 permanent identifiers into `00-BOOK/DATA/id-ledger.json` (`EXDOC` 2621→2657, `ENGINE` 1265→1267, `TESTOBJ` 831→836) and rewrote 11 further canonical surfaces. **It also reported `invariants 29/29 passing`.** Reverted by `git checkout` of exactly the 12 session-caused paths; all counters verified pristine.

Establishes three things: the closure action for `UGA-INV-01/10` **works**; its blast radius is **exactly 12 files**; and it is **fully reversible while uncommitted**.

**Probe 2 — ISD-L-07 self-inflicted violation.** My own planning determination reproduced one of the nine literal permanence phrases inside a quotation. `ISD-L-07` counts those phrases as substrings and cannot distinguish a quotation from an assertion, so violations went 2→3. Repaired by paraphrase; back to 2. *This document hit the same trap while describing it* — an earlier draft enumerated the phrase vocabulary verbatim in §7.3 and became violation #3 itself; that enumeration was removed rather than the finding softened.

Establishes that `ISD-L-07` is a **substring ratchet, not a semantic check** — which determines the shape of its closure (§5.3) and is the same limitation `UNIVERSAL-LIFECYCLE-SEMANTIC-RESCAN-REGISTER.md` records about its own prior scan.

### 0.4 Blocker → priority mapping

| Directive priority | Blocker | This document |
|---|---|---|
| 1. Gate purity stabilization | `B-2` | §1 |
| 2. Universal identity representation alignment | §8 six-digit finding + 4 disjoint mints | §2 |
| 3. Ownership resolution mechanism | `B-1` | §3 |
| 4. Safety admission wiring | `B-3` | §4 |
| 5. Measurement operand establishment | `B-5` | §5 |
| 6. Authority-dependent blockers | `B-4` + residue | §6 |
| — precondition to validating any of the above — | `B-6` | §7 |

`B-6` is not a seventh priority. It is the **precondition**: while four stages fail, no closure action can be distinguished from pre-existing failure, so no closure can produce admissible evidence. Its three sub-closures are the cheapest work in this document and are prepared in §7.

---

## SECTION 1 — PRIORITY 1: GATE PURITY STABILIZATION (`B-2`)

### 1.1 Existing mechanism — more than the admission determination credited

The finding "≥24 gate paths perform undeclared mutation" is correct but incomplete. **The mode distinction already exists in at least one engine, declared in its own interface:**

```
$ uga_engine.py --help
  {run,gate,stats}
    run     mint identities and emit all surfaces
    gate    verify invariants, mutate nothing
    stats   print measured state
```

`UGA-001` is therefore a **positive precedent, not a violator**: `gate` states "mutate nothing" and honours it; `run` states "mint" and honours that. Probe 1 was an *operator* error — I called `run` intending `gate` — not an engine defect.

Further existing mechanism:
- `00-MASTER/UCCEP-000000/uccep-bindings.json` already carries a **`write_scope`** field per check, across 48 checks / 26 gates.
- `--check-write-scope` forbidden-write guards exist on every programme engine and are CI-enforced.
- `engine/infinite_scope/gate.py:15-20` declares `OBSERVE MODE — READ ONLY. No clock, no network, no subprocess.`
- `engine/uaue/gate.py` separates `--gate` / `--replay` (observe) from `--render` (write) in one interface.
- `00-BOOK/tools/register.sh --observe` runs read-only **before** the lock; the transaction plane is separate.
- **Phase A precedent (`UEG-000001`)**: `ucos_env_gate` observes and refuses; repair lives in `bootstrap.sh` / `doctor.sh --fix`. The separation is enforced by a test that reads `verify.sh` source. I verified this guard **bites** by injecting `ucos_ensure_venv` into `verify.sh` and watching `test_verify_does_not_ensure_the_environment_it_is_verifying` fail, then restoring byte-identical.

So the pattern, the enforcement technique, and a working reference implementation all exist.

### 1.2 Required extension

**EXTEND, not CREATE.** Three components, in order:

1. **A declared `MODE` field** on each check in `uccep-bindings.json`, valued from a closed-at-declaration set (`OBSERVE` / `TRANSACT`), sitting beside the existing `write_scope`. This is the remediation `GATE-PURITY-DETERMINATION.md` already specifies.
2. **A conformance measurement** that a check declaring `OBSERVE` leaves the tracked tree unchanged — the technique already proven by `UEG-000001`'s source-reading test and by the `--check-write-scope` family.
3. **Interface-level mode separation** for engines that lack `UGA-001`'s subcommand split, so an observe-intending operator cannot reach a mutating path by default.

Explicitly **out of scope**: any new gate, engine, registry, or authority. This adds a field and a measurement to existing surfaces.

### 1.3 Authority requirement

| Item | Authority |
|---|---|
| `MODE` field on `uccep-bindings.json` | `UCCEP-000000` owner |
| Per-engine mode declarations | each programme's own declaration owner |
| Conformance measurement | the measuring programme's owner |
| Precedent already granted | `GATE-PURITY-DETERMINATION.md` §remediation specifies the `MODE` field; blocked on `H-06` / `CR-09` |

**This is the only priority-1 item whose remediation is already specified and merely unauthorized.** No new determination is needed — an authorization is.

### 1.4 Dependency

None upstream. **This is a root.** Three items depend on it: §4 (safety admission wiring), and both remaining §7 sub-closures that run mutating engines.

### 1.5 Validation evidence

| Evidence | How produced |
|---|---|
| Every check carries exactly one `MODE` | totality count over `uccep-bindings.json` |
| Every `OBSERVE` check leaves the tree unchanged | `git status --porcelain` digest before/after each check |
| No `OBSERVE` path reaches a minting call | static reachability, or the source-reading technique `UEG-000001` uses |
| Regression guard bites | inject a write into an `OBSERVE` path; the measurement must fail |
| Probe-1 class cannot recur | an observe-intending invocation cannot mint |

The fourth row is the one that matters. Probe 1 and the recorded 140-identifier incident are the same defect; a measurement that would not have caught either is not closure.

### 1.6 Closure criteria

1. Every check in `uccep-bindings.json` declares exactly one `MODE`.
2. Every `OBSERVE`-declared check demonstrably leaves the tracked tree byte-unchanged.
3. A deliberately injected violation fails the measurement (guard efficacy proven, not assumed).
4. `GATE-PURITY-DETERMINATION.md`'s ≥24 undeclared-mutation paths are each either re-declared `TRANSACT` or made non-mutating.
5. The count of `*-gate` targets declaring a mode equals the count of `*-gate` targets (currently few of **49**).

---

## SECTION 2 — PRIORITY 2: UNIVERSAL IDENTITY REPRESENTATION ALIGNMENT

### 2.1 Existing mechanism

Two independent defects share this priority. They must not be conflated.

**Defect A — the six-digit ceiling.** Measured this session:

| Surface | Behaviour |
|---|---|
| Mint — `00-BOOK/tools/ukb.py:903`, `:2228` | `f"UCOS-{category}-{seq:06d}"` — `:06d` pads to a **minimum** of six; **never caps** |
| Validator — `engine/uckp/alignment.py:89` | `^UCOS-[A-Z0-9]+-[0-9]{6}$` — **exactly six** |
| Consequence | the 10⁶-th identifier in any family mints, then fails validation with `AlignmentError` |
| Headroom | largest family `EXDOC` at 2,621 — **0.26% consumed** |

**Defect B — four disjoint mints.** Confirmed unchanged:

| Mint | Shape | Philosophy |
|---|---|---|
| `00-BOOK/tools/ukb.py build --mint` | `UCOS-<CODE>-<6d>` | **allocating** counter |
| `engine/registry/universal/identity.py` | `UCOS-<CODE>-<12hex>` | derived |
| `engine/uckp/identity.py` | `urn:ucos:ucko:<ns>:<local>` | derived (UUID5) |
| `platform/universal_assimilation/contracts.py:245,319,442,489` | `UCOS-USA{S,U,R,P}-<16hex>` | derived, `content_hash(core)[:16]` |

### 2.2 Required extension

**Defect A — EXTEND. Empirically validated against all 6,187 ledger identifiers this session:**

| Candidate | Matches | Verdict |
|---|---|---|
| `[0-9]{6}` (current) | 6,185 / 6,187 | ceiling at 10⁶ |
| **`[0-9]{6,}`** | **6,185 / 6,187** | **zero behavioural change; admits 10⁶** ✅ |
| `[0-9]+` (fully open) | 6,187 / 6,187 | **REGRESSION** ✗ |

`[0-9]+` must be rejected: it newly admits `UCOS-AEE-001` and `UCOS-RIB-001` — **programme identifiers, not minted object identifiers** — into `repository_local_urn`, collapsing the namespace separation between programmes and objects. The floor is load-bearing; only the ceiling is the defect.

Two coordinated sites, and they are cross-checked for **exact string equality**:

1. `engine/uckp/alignment.py:89` — the pattern
2. `00-BOOK/DATA/constitutional-authority-alignment.json` → `identity_authority_resolution.derivation.id_shape`, currently `'^UCOS-[A-Z0-9]+-[0-9]{6}$'`, compared at `alignment.py:671`

Unaffected by the widening, verified: `derivation.shape`, and `derivation.example` (`UCOS-ENGINE-000496` still matches).

**Defect B — HOLD.** The four mints differ not in *format* but in *whether identity is allocated or derived*. Reconciling them is an authority decision, not a code change. Recorded in §6.

### 2.3 Authority requirement

| Item | Authority |
|---|---|
| `alignment.py:89` pattern | `UCKP` / `engine/uckp/alignment.py` owner |
| `constitutional-authority-alignment.json` | **AUTHORED REPOSITORY TRUTH** — `00-BOOK/DATA/` owner |
| `CAA-INV-04` re-measurement | `UCOS-UGA-001` (currently PASS at 5,874) |
| Defect B | **no owner exists** — see §6 |

### 2.4 Dependency

`id_shape` is embedded in UCKO object metadata at `alignment.py:514`, which flows into the **universe digest**. The `evolution surface replay` stage **already fails on drift**. Therefore:

**Defect A closure depends on `B-6` (§7).** Applied on the current red baseline, the resulting drift would be indistinguishable from the pre-existing drift, and the change would be unverifiable. This is why it was analysed and deliberately **not applied** under the prior implementation authorization.

### 2.5 Validation evidence

| Evidence | How produced |
|---|---|
| Zero regression on the live population | all 6,187 identifiers match `{6,}` iff they matched `{6}` — **already produced** |
| Forward admission | `UCOS-ENGINE-1000000` and `UCOS-ENGINE-12345678` validate — **already produced** |
| Namespace separation preserved | `UCOS-AEE-001` / `UCOS-RIB-001` still refused — **already produced** |
| Code/declaration equality | `alignment.py:671` cross-check returns no findings |
| Digest delta bounded | universe-digest diff attributable to `id_shape` alone |
| No replay regression | `uaue.gate --replay` no worse than baseline |

### 2.6 Closure criteria

1. No numeric width is enforced as a ceiling anywhere in the identity plane.
2. Six digits remains the **current mint manifestation** — zero existing identifiers change.
3. Code and declaration agree by exact string equality.
4. The 10⁶ boundary is demonstrably admissible.
5. Programme-identifier / object-identifier separation is preserved.
6. The four-mint reconciliation is **recorded as open with a named owner requirement**, not silently folded in.
7. The residual disclosed closures — `_ID_DIGEST_LEN = 12`, the three-part parse at `identity.py:281,293`, ASCII-only namespaces, UCKP's 63/191-character caps — are **entered in the assumption register**. Per `engine/infinite_scope/contract.py:16-20`, *closure is not a defect; undisclosed closure is.* These are currently undisclosed; disclosure is the closure.

---

## SECTION 3 — PRIORITY 3: OWNERSHIP RESOLUTION MECHANISM (`B-1`)

### 3.1 Existing mechanism

`platform/universal_ownership/` — `OwnershipDeterminationEngine` (`determination.py:73`), seven legislated requirements (`contracts.py:257-291`), CLI `homing`. Measured now:

```
subjects: 549 · declared: 151 · contested: 0 · unresolved: 398 · remediable: 195 · coverage: 27.5046%
  186 EVIDENCE-NOT-IN-CANONICAL-HOME-ZONE
  212 NO-OWNERSHIP-EVIDENCE
    2 DIAGNOSED LOCATOR-FORM-NOT-ADMITTED
   45 DIAGNOSED LOCATOR-NOT-REGISTERED
  195 DIAGNOSED ZONE-NOT-CANONICAL-HOME-ELIGIBLE
```

The engine is sound and issued **CREATE ×0**. Ownership resolution is a **discovery** operation, not a construction one — which is what makes it the highest-leverage closure in the programme and why it needs no new machinery.

### 3.2 Required extension

**REUSE the engine; EXTEND its reach.** The mechanism is not the gap; **throughput and inflow control** are.

Three components:

1. **Work the 195 remediable subjects** — the engine already diagnoses each with a reason code, so each carries its own next action. This is the actionable population; the other 203 need evidence that does not yet exist.
2. **Close the inflow.** Coverage fell 27.86% → 27.5046% with declared unchanged at 151. Any convergence plan must make owner declaration a condition of subject entry, or the denominator outruns the numerator indefinitely.
3. **Reconcile the declaration plane with the enforcement plane.** `02-CANONICAL-OWNERSHIP-MATRIX.md` is human-authored and machine-unreadable; `CANONICAL-AUTHORITY-DETERMINATION.md` `D-2.1` records that the two planes **do not share a key**. `contested: 0` means no two owners claim one subject *within* the ownership plane — it does **not** mean the planes agree, and the 10 registered `CONFLICT-01`…`CONFLICT-10` are invisible to this engine because they are cross-plane.

### 3.3 Authority requirement

| Item | Authority |
|---|---|
| Each of the 195 remediable declarations | the prospective owner of that subject |
| Inflow condition | `CMG-000001` — this is a governance rule, not a code change |
| Cross-plane key reconciliation | `CANONICAL-AUTHORITY-DETERMINATION.md` `D-2.1` owner |
| Accepted-threshold alternative | if 100% is not the bar, the bar must be **declared** |

### 3.4 Dependency

None upstream — **a root, and the highest-leverage one.** Admission condition `A-3` gates every other admission condition, so every downstream closure inherits this.

### 3.5 Validation evidence

`homing` reports `closed: True`, or coverage at or above a **declared and accepted** threshold; `contested` remains 0; the 10 cross-plane conflicts each carry a disposition; coverage is **non-decreasing across two consecutive measurements** (the inflow test).

### 3.6 Closure criteria

1. Every subject an admitted change touches has a declared owner (`A-3` evaluable true for the change set).
2. Coverage is non-decreasing — inflow no longer outruns declaration.
3. The declaration and enforcement planes share a key, or their divergence is declared and bounded.
4. No owner is invented to satisfy a count: an unknown owner is recorded **unknown**, never guessed.

---

## SECTION 4 — PRIORITY 4: SAFETY ADMISSION WIRING (`B-3`)

### 4.1 Existing mechanism — all three components are built

| Component | Location | State |
|---|---|---|
| Security intelligence | `platform/security/` — 13 modules / 6,512 LOC; `scan_for_secret` + 7 `_SECRET_PATTERNS`; `FindingLedger`; `compute_rollup` (open CRITICAL/HIGH without valid exception ⇒ `BLOCKED`) | **non-enforcing by architecture**; referenced by **zero** CI workflows (re-verified) |
| Trust / provenance | `platform/foundation/trust.py::TrustEngine` — genesis anchor, signed hierarchy, HMAC-SHA256, revocation, rotation, notary on authority-local monotonic ordinals (never wall-clock, so byte-reproducible); keys by `SecretRef` only | wired to **authority succession**, not candidate content |
| Impact | `engine/graph/architecture/impact.py` — blast radius, certified-surface disturbance, 0–100 risk, severity band; `engine/verification_impact/` **fails wide** | CI-run; **unreachable from any admission path** (`MI-5`) |
| Admission pipeline to wire into | `engine/uaue/` 10 phases + `gate.py` 10 obligations | enforced |

Nothing needs building. Three edges need connecting.

### 4.2 Required extension

**COMPOSE ×3.** Wire each existing component into the `engine/uaue/` admission path at its corresponding declared phase, and add the corresponding gate obligation so the wiring is measured rather than assumed.

Genuinely missing, and to be recorded rather than quietly bundled: **cyber risk detection** (`T-4`). Only ruff's bandit `S` ruleset exists (`pyproject.toml:361`); there is no dependency scanning, no CI secret scanning, no SAST, no Dependabot; `14-SECURITY/` is **5 markdown files, 0 code** (re-verified). `scan_for_secret` is a reusable seed for exactly one of those three needs — it is not a substitute for the other two.

### 4.3 Authority requirement

**This is the decisive item, and it is not primarily technical.** `platform/security/intelligence.py` is non-enforcing *by declared architecture* (`ARCH-SECURITY-001` §11/§21, RG-02/AR-04). Making it enforce at admission contradicts its own declaration.

Required first: a determination by the `ARCH-SECURITY-001` owner on whether composition is **a binding** (permitted) or **a constitutional amendment** (requiring `CEP` process). Until that is answered, the wiring cannot be lawfully performed regardless of technical readiness.

### 4.4 Dependency

**Depends on §1 (gate purity), by construction.** Composing machinery into the admission path means running more machinery during admission. While ≥24 gate paths mutate undeclared, adding machinery to admission adds mutation to admission. Probe 1 is the demonstration: a diagnostic invocation minted 43 permanent identifiers.

Also depends on §3 for `A-3`.

### 4.5 Validation evidence

`A-6`/`A-7`/`A-8` evaluable at admission time; a candidate with an open CRITICAL finding is **refused** (not warned); an unsigned candidate is refused or its acceptance is declared; the impact engine is reachable from the admission path with the reachability measured; each new obligation has a proven-biting guard; and the composed path **still leaves the tree unchanged in OBSERVE mode**.

### 4.6 Closure criteria

1. Security, trust, and impact are each reachable from admission, and reachability is measured.
2. The enforce-versus-record question is answered by the owning authority and the answer is declared.
3. A finding that should block does block — proven by a deliberate negative test.
4. Cyber risk detection is recorded as an open gap with a named owner; it is **not** claimed closed by the presence of `scan_for_secret`.
5. Composition adds no undeclared mutation.

---

## SECTION 5 — PRIORITY 5: MEASUREMENT OPERAND ESTABLISHMENT (`B-5`)

### 5.1 Existing mechanism

Eight of nine capabilities a self-evolving plan needs exist and are CI-enforced. Re-verified: `find . -name "mip.json"` returns **nothing**.

`00-MASTER/UCOS-MXR-001/roadmap_engine.py` (1,542 lines, stdlib only) computes topological order, transitive readiness closure, effort-weighted critical path (twice — in-corpus and ratification chain), parallel groups, union-find workstreams, and **12 blocking gates**; CI-enforced by `roadmap-gate.yml` via drift/replay plus derivability. Its `SRC` names eight input registers. **The MIP is not among them.**

`LAW P50-002` — *completion is measured, not asserted* — therefore **has no operand** (`MP2-C-01`).

### 5.2 Required extension

**EXTEND by derivation and registration — never by amendment.** This is the repository's own verdict (`MASTER-IMPLEMENTATION-PLAN-EVOLUTION-DETERMINATION.md:212-222`), and the reason is recorded: `UCOS-MIP-000002` is registered under `UCOS-UCOSOMEGAINF-000001` by a **digest over its bytes**, so editing it breaks that registration. v3 is the amendment surface and admits parts by delta — which is exactly how `UEG-000001` registered as Part 52.

Two components: derive a machine-readable plan state (proposal `P-1`, **not built**), and add it to `roadmap_engine.py`'s `SRC` so the existing sequencing machinery can consume it. No new engine.

### 5.3 Authority requirement

| Item | Authority |
|---|---|
| Plan-state schema and location | MIP owner |
| Adding an input to `SRC` | `UCOS-MXR-001` owner |
| Ratifying MIP v3 | **NO COMPETENT RATIFIER IDENTIFIED** — three located instruments so state (`MP2-C-04`) |

The second row is a technical decision. The third is a vacancy: v3 is `PROPOSED · UNRATIFIED` and declares `AUTHORITY | NONE — DERIVED. This document proposes; it does not legislate.` A correct `mip.json` would still be unratifiable.

### 5.4 Dependency

Independent of §1–§4. Blocked only on the ratifier vacancy for its *governance* half; its *derivation* half can proceed once `B-6` permits verification.

### 5.5 Validation evidence

`LAW P50-002` evaluates against a real operand; plan state is derived (regenerable, drift-gated) rather than authored; requirement→plan edges resolve in both directions; `roadmap_engine.py --gate` consumes it without new gate failures; and completion is **computed**, never asserted in prose.

### 5.6 Closure criteria

1. A machine-readable plan state exists and is **derived**, not authored.
2. It is an input to the existing sequencing engine.
3. `LAW P50-002` has an operand and returns a measured value.
4. The plan carries no fixed phase or date assumption — sequencing remains computed from readiness, dependency, authority, evidence, risk, and impact.
5. The ratifier vacancy is **recorded as an open authority requirement**, not worked around.

---

## SECTION 6 — PRIORITY 6: AUTHORITY-DEPENDENT BLOCKERS (`B-4` AND RESIDUE)

These cannot be closed by work. They require an authority to be **vested**. Preparation consists of stating precisely what must be vested and what each unblocks.

### 6.1 `B-4` — cross-class atomic evolution transaction

| Field | Content |
|---|---|
| Existing mechanism | `platform/foundation/admission.py` AIF-L14 atomic mint — **single-class only**. `engine/runtime/execution/rollback.py` reverses in reverse dependency order but **reverses records, not live effects** (ORL-15) |
| Formal position | `H-06-…AUTHORITY-DETERMINATION.md:12` **"AUTHORITY GAP REMAINS"**; `H-06-…OBJECT-DETERMINATION.md:11` **"NEW CANONICAL OBJECT REQUIRED"** — four candidates evaluated and rejected, including UAUE itself: *"UAUE is a measurement plane over the cycle"* |
| Required extension | The canonical object, owned. **This is the one place in this document where CREATE may be unavoidable** — and the repository, not this determination, reached that conclusion |
| Authority requirement | An authority vested across `UAUE-000001` · `UAIE-000001` · `UCOS-RIB-001` · `UCOS-UGA-001` · `UCKP` · `UCF` · ledger/registry producers. **None exists.** Open item `AT-1` |
| Dependency | Independent |
| Validation evidence | `A-13` satisfiable; the object instantiated ≥1 time; a partial failure across two classes leaves no half-applied state |
| Closure criteria | A single named owner for the cross-class transaction; the object specified **and** instantiated; atomicity demonstrated by a deliberate mid-transaction failure |
| Unblocks | `R-19` (Assimilation→Entity edge), `R-20` (Evolution→Assimilation re-entry) |

### 6.2 Identity philosophy reconciliation (Defect B from §2)

The four mints split on **allocated versus derived** identity. `platform/universal_assimilation/contracts.py` derives from `content_hash(core)[:16]`; `ukb.py` allocates from a counter in `id-ledger.json`. No format change reconciles these — one of the two philosophies must govern, or their coexistence must be declared with a resolution rule.

Authority: `CAA-INV-04` currently reports PASS at 5,684–5,874 measured while four disjoint mints exist, so the invariant as written does not detect this. Resolving requires the `UCOS-UGA-001` owner **and** the assimilation plane owner. Unblocks `R-19`.

### 6.3 Assimilation plane reconciliation

Re-verified: `platform/universal_assimilation/` imports `engine/` **exactly once**, and only for an exception type (`cli.py:33`). No `engine/` module imports it. Terminus is `AssimilationReport` → coverage number → ∅. Two planes exist; only Plane B (`UAKOS-CLOSURE-008`) is in CI.

Also: `ucos-assimilate` has **no `uccep-bindings.json` entry and no `verify.sh` stage**, hence no evidence key, hence **no proof it ever ran** (`MI-10`). Confirmed directly: `.ucos-verification-evidence/` holds directories for `ruff`, `object-birth`, `meta-constitutional`, `evolution-replay`, `verification-intelligence`, `governance-pre`, `registry-validate`, `autonomous-evolution` — and nothing for assimilation. **The cheapest possible closure step here is an evidence key**, which is not blocked on authority.

### 6.4 Corrected carry-forward: `F-3`

My admission determination stated the `EvolutionLedger` is never persisted. **That is narrower than stated and the correction matters for planning.** `to_document` / `from_document` exist; `engine/uaue/history.py` rehydrates through them. What is absent is a **production writer** — only `engine/tests/unit/test_uaue_controller.py:1120` writes `UAUE-EVOLUTION-HISTORY.json`, and to `tmp_path`. Missing writer, not missing serialization. A writer is a smaller closure than a persistence layer.

---

## SECTION 7 — PRECONDITION: BASELINE RESTORATION (`B-6`)

Three sub-closures. Each has a located mechanism and a named precedent. Together they are the cheapest work prepared in this document, and **nothing else can be validated until they are done.**

### 7.1 `B-6a` — the 43 anonymous objects

| Field | Content |
|---|---|
| Existing mechanism | `uga_engine.py run` — "mint identities and emit all surfaces" |
| Enumeration | `uga_engine.build(mint=False)["anonymous"]` — the **same method ADR-0017 used**. Returns **43**: 36 `.md` + 7 `.py`; by directory: 21 root, 14 `adr/`, 5 `engine/`, 2 `platform/`, 1 `00-BOOK/` |
| Discovery basis | `git ls-files --cached` — the **git index**, not the working tree. Untracked files are invisible; a `git add` makes one visible and anonymous |
| Measured effect | Probe 1: `EXDOC` +36, `ENGINE` +2, `TESTOBJ` +5; 12 files written; then **`invariants 29/29 passing`** |
| Precedent | **`ADR-0017`** (24 objects) and **`ADR-0018`** (2 objects), both citing `UGA-001` · `REG-AUTO-001` · `CEP-002 Article 28`, deciders "Constitutional Authority · UCOS Ω∞" |
| Authority requirement | **A new decision under `CEP-002` Article 28.** `ADR-0017` explicitly declined a standing blanket mint: *"A future anonymous object requires its own decision under this same Article, not a standing blanket authorization."* The 43 are precisely such future objects. **This determination does not create that ADR** |
| Dependency | §1 is *desirable* first (the action mutates authored truth) but not strictly blocking, because the action is **declared** minting, not undeclared mutation |
| Validation evidence | `UGA-INV-01` and `UGA-INV-10` violations → 0; `anonymous` → 0; identifiers append-only and never renumbered; exactly 43 minted, enumerated before and after |
| Closure criteria | The 43 named objects carry identifiers; the enumerated set matches the authorized set exactly; no unnamed object is minted as a side effect |

**Forward condition worth recording:** my two prior determinations and this file are untracked and therefore invisible to `UGA-001`. Confirmed: 0 of them are in the index. Each will become an anonymous object requiring minting **if and when** it is `git add`ed.

### 7.2 `B-6b` — UAUE replay drift

| Field | Content |
|---|---|
| Existing mechanism | `engine.uaue.gate --render` — "write the declared history projection and every declared register" |
| Symptom | 1,316,175 bytes committed vs 1,316,175 projected — **equal length, unequal content.** A content drift, not a truncation |
| Interpretation | The 19 files in `00-MASTER/UAUE-000001/` are declared **DERIVED TRUTH**; `--replay` treats a hand edit as a failure rather than a fact. Equal-length inequality is consistent with a hand edit or a stale projection, not a partial write |
| Required extension | None. Re-render, then re-replay |
| Authority requirement | `UAUE-000001` owner — `--render` **writes 19 canonical surfaces** |
| Dependency | §1 desirable first; the write is declared, so not strictly blocking |
| Validation evidence | `--replay` exits 0; the re-rendered bytes equal the committed bytes; the content delta is inspected **before** overwriting, so the cause is known rather than erased |
| Closure criteria | Committed projection is the replay of the declaration; the drift **cause is recorded**, not merely eliminated |

**Explicit caution.** `--render` overwrites the committed projection. If the drift is an *unauthorized hand edit*, rendering **destroys the only evidence of it**. The content delta must be captured before rendering. This is the same failure mode Phase A was built to prevent: a command that repairs its subject cannot report on it.

### 7.3 `B-6c` — `ISD-L-07`, two permanence occurrences

| Field | Content |
|---|---|
| Existing mechanism | `freeze_scan.preserved_sites` in `00-MASTER/UISD-000001/uisd-declaration.json` — **16 existing entries** (`R-01`…`R-16`) with classes B/C/D/E, each carrying `path`, `class`, `occurrences`, `reason` |
| Current violations | 2 — `UCOS-OMEGA-INFINITY-ASSIMILATION-INFINITE-INTELLIGENCE-INTEGRATION-DETERMINATION.md` (2 occurrences) and `UCOS-OMEGA-INFINITY-UNIVERSAL-EVOLUTIONARY-ENTITY-FABRIC-DETERMINATION.md` (1) |
| Nature of the check | A **substring ratchet, not a semantic check** — nine literal permanence phrases plus a status-field pattern. The vocabulary is declared at `freeze_scan.phrases` in `00-MASTER/UISD-000001/uisd-declaration.json` and is **deliberately not reproduced here**: this document would then count as a permanence site itself. It cannot distinguish a quotation from a declaration |
| Precedent | Directly on point: `R-10` `SEMANTIC-LIFECYCLE-RECONCILIATION-REGISTER.md` at **25 occurrences** and `R-12` `UNIVERSAL-LIFECYCLE-SEMANTIC-RESCAN-REGISTER.md` at **22** are both registered class E. Quotation-heavy registers are *expected* to be preserved sites |
| Two lawful closures | (a) register each as a preserved site with class and reason; (b) paraphrase so the literal phrase is not emitted. **I used (b) on my own document** when my quotation took violations 2→3 |
| Authority requirement | `UISD-000001` owner for (a). For (b), the authority is whoever owns the document — no external authority needed |
| Dependency | None. **Cheapest closure in this document** |
| Validation evidence | `engine.infinite_scope.gate` verdict → `OPEN`; `ISD-L-07` violations → 0; every remaining occurrence is a declared, classified, non-active site |
| Closure criteria | Gate verdict `OPEN`; no permanence occurrence is undisclosed; no *active* permanence declaration is introduced — a preserved site records history, it does not freeze forward capability |

### 7.4 `B-6d` — residual test failures

`test_mutation_classification`, `engine/verification_intelligence/*`, and `engine/verification_impact/*` are among the **16 pre-existing modified tracked files**. These represent work-in-progress by a prior session, not defects introduced by closure. The `pytest` stage cannot pass until that work is either completed or reverted.

**Authority requirement: the owner of the uncommitted work.** This determination will not complete or revert another party's in-flight changes.

### 7.5 Sequencing within `B-6`

```
B-6c (ISD-L-07)        — no authority beyond document owners; cheapest; do first
B-6a (43 mints)        — needs a new CEP-002 Art 28 decision; effect measured; reversible while uncommitted
B-6b (UAUE render)     — needs UAUE owner; CAPTURE THE DELTA BEFORE RENDERING
B-6d (WIP tests)       — needs the owner of the 16 modified files
```

---

## SECTION 8 — CONSOLIDATED DEPENDENCY GRAPH

```
B-6c ─┐
B-6a ─┼─→ GREEN BASELINE ─┬─→ §2 Defect A (six-digit)   [needs clean drift signal]
B-6b ─┤                    └─→ any closure requiring evidence
B-6d ─┘

§1 gate purity ─────→ §4 safety wiring        [must precede, by construction]
§3 ownership ───────→ §4 safety wiring        [A-3 gates every condition]
§5 plan operand ────  independent
§6 authority vesting ─→ §6.1 unblocks R-19, R-20
```

**Four independent roots:** `B-6` (as a bundle), §1, §3, §5. **One derived:** §4. **One unvestable by work:** §6.

No single action unblocks more than one root. §6 cannot be worked at all — only vested.

---

## SECTION 9 — REPRESENTATION NEUTRALITY COMPLIANCE

The directive fixes four constraints on this preparation. Each is checked against what is prepared above.

| Constraint | Compliance in this preparation |
|---|---|
| **Identity: not six digits** | §2 removes the ceiling and **retains six as the current mint manifestation**. `{6,}` is chosen over `[0-9]+` on measured grounds — the floor preserves programme/object namespace separation. §2.6(7) requires the residual closures (`_ID_DIGEST_LEN = 12`, 3-part parse, ASCII-only, 63/191 caps) to be **disclosed**, since undisclosed closure is the defect |
| **Runtime: not Python** | §1's Phase A precedent reads its canonical series from a **single declared authority** rather than hardcoding it, and no closure above introduces a runtime assumption. The honest residue, restated not hidden: the substrate is Python-shaped, single-process, has no durable runtime sink, and hardcodes `utf-8`. `PersistenceAdapter` proves storage neutrality **once**, not repo-wide |
| **Location: not Earth** | Untouched by every closure above, and already sound: no lat/long, no ISO-3166, `"country"` in `PROHIBITED_TOKENS`, frames explicitly off-world and non-planetary |
| **Time: not one calendar** | Untouched and already sound: `TemporalCoordinate` carries value + required `ReferenceSystem`, never normalises, returns `INCOMPARABLE` across systems. §7.2's notary ordinals are **authority-local monotonic, never wall-clock** — the property that keeps trust state byte-reproducible. The two unqualified UTC/ISO-8601 emissions (`engine/foundation/obs/logging.py:59`, `engine/registry/universal/audit.py:51`) remain open and **are not closed by anything above** |
| **Everything remains an evolving entity** | No closure introduces a terminal state. §6.4's correction (writer missing, not serialization) preserves the append-only non-terminating ledger. §7.3 explicitly requires that a preserved site record history **without** freezing forward capability |

**One genuinely missing representation, carried forward unclosed:** no entity anywhere carries **possible futures**. Re-verified — `possible_futures | projected_future | candidate_future | future_states | alternative_path | parallel_evolution` return **zero matches** across all `.py` and `.json`; the sole adjacent surface is one content hash at `engine/uaue/simulation.py:65`. Nothing in this preparation closes it, and nothing above should be read as doing so.

---

## SECTION 10 — REUSE DETERMINATION

| § | Closure | Disposition | Target |
|---|---|---|---|
| 1 | Gate purity | **EXTEND** | `uccep-bindings.json` `MODE` beside existing `write_scope`; `UGA-001` run/gate split as the pattern; `UEG-000001` source-reading test as the enforcement technique |
| 2A | Six-digit ceiling | **EXTEND** | `alignment.py:89` + `constitutional-authority-alignment.json` |
| 2B | Four disjoint mints | **HOLD** | authority decision (§6.2) |
| 3 | Ownership | **REUSE** engine, **EXTEND** reach | `platform/universal_ownership/` |
| 4 | Safety wiring | **COMPOSE ×3** | `platform/security/`, `platform/foundation/trust.py`, `engine/graph/architecture/impact.py` → `engine/uaue/` |
| 4 | Cyber risk detection | **TRUE MISSING** | `scan_for_secret` seeds 1 of 3 needs |
| 5 | Plan operand | **EXTEND** | derive-and-register; add to `roadmap_engine.py` `SRC` |
| 6.1 | Cross-class transaction | **CREATE (repository-determined)** | `H-06` `AT-1` |
| 6.3 | Assimilation evidence key | **EXTEND** | `engine/verification_intelligence/evidence.py` |
| 6.4 | Evolution ledger writer | **EXTEND** | `to_document` already exists |
| 7a | 43 mints | **REUSE** | `uga_engine.py run` |
| 7b | UAUE drift | **REUSE** | `uaue.gate --render` |
| 7c | ISD-L-07 | **REUSE** | `preserved_sites`, 16 precedents |

**Totals: 8 REUSE · 7 EXTEND · 3 COMPOSE · 1 HOLD · 1 TRUE MISSING · 1 CREATE (repository-determined, not by this document).**

No duplicate engine, registry, or authority is proposed anywhere above.

---

## SECTION 11 — WHAT THIS PREPARATION DOES NOT RESOLVE

Recorded so nothing above reads as broader than it is.

1. **The 15 contradictions** in the planning determination remain unresolved; this document adds no authority to resolve them.
2. **`B-4` and the MIP ratifier vacancy** cannot be closed by work of any kind.
3. **Possible futures** (`T-1`) — no entity carries them; nothing above changes that.
4. **Semantic conflict detection** (`T-5`) — conflict remains ownership/name collision only.
5. **The two unqualified UTC/ISO-8601 timestamp emissions** remain open.
6. **`ISD-L-07`'s substring nature** is worked *around* by both lawful closures, not fixed. A ratchet that cannot distinguish quotation from declaration will keep flagging faithful quotation. `AD-G-01` (detection is declaration-bound) is untouched: an undeclared closure remains invisible.
7. **`B-6d`** depends on another party completing or reverting in-flight work.
8. **Ownership inflow** — even a fully worked 195-subject remediation does not converge if subjects keep entering unowned. §3.2(2) names the condition; it does not impose it.

---

## STOP

Preparation complete. No implementation performed. No code, configuration, registry, or certification modified. No requirement, ADR, identifier, or authority created. No phase or roadmap created. The single mutation is the creation of this file.

**Awaiting explicit approval.**

| Field | Value |
|---|---|
| BLOCKERS PREPARED | 6 priorities + `B-6` precondition (4 sub-closures) |
| DISPOSITIONS | 8 REUSE · 7 EXTEND · 3 COMPOSE · 1 HOLD · 1 TRUE MISSING · 1 CREATE (repository-determined) |
| INDEPENDENT ROOTS | 4 — `B-6` bundle · gate purity · ownership · plan operand |
| DERIVED | 1 — safety wiring (depends on gate purity **and** ownership) |
| UNVESTABLE BY WORK | `B-4` cross-class transaction · MIP ratifier vacancy |
| CHEAPEST FIRST ACTION | `B-6c` — `ISD-L-07` preserved-site registration or paraphrase; no external authority required |
| HIGHEST LEVERAGE | §3 ownership — `A-3` gates every other admission condition |
| NEW AUTHORITY DECISIONS REQUIRED | `CEP-002` Art 28 decision for the 43 mints · `ARCH-SECURITY-001` enforce-vs-record · `UAUE-000001` render · cross-class transaction vesting · MIP ratifier |
| MEASUREMENTS THAT MOVED ADVERSELY | ownership coverage 27.86% → **27.5046%** · gate targets 46 → **49** |
| CRITICAL CAUTION | `uaue.gate --render` **overwrites the drift evidence**; capture the content delta first |
| VERDICT | `PREPARATION-COMPLETE · IMPLEMENTATION-NOT-AUTHORIZED` |
