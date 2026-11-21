# UICM — Phase 4 Readiness Determination

> **Artifact:** `UICM-PHASE-4-READINESS-DETERMINATION`
> **Programme:** UCOS-UICM-000001 — Phase 4 discovery
> **AUTHORITY = NONE — DERIVED TRUTH.**
> **Disposition:** DISCOVERY COMPLETE. IMPLEMENTATION NOT AUTHORIZED. NO GAP RESOLVED.

---

## 1. Determination

**RESOLUTION EXECUTION GOVERNANCE EXISTS. ONE BINDING IS MISSING. NO AUTHORITY MAY BE CREATED.**

| Discovery item | Finding | Gap? |
|---|---|---|
| 1. Resolution authorization path | 7-layer composite, all located; G-14 verified **OPEN** | no |
| 2. Canonical owner execution boundaries | 43 disjoint scopes, total over 158 gaps — **given file-level scoping** | no |
| 3. Evidence generation requirements | structurally mandatory; unevidenced `CLOSED` is unconstructable | no |
| 4. Certification handoff | exists as a projection; 10 BLOCKING metrics, verdicts computed | no |
| 5. Failed resolution handling | **no record of a failed attempt exists** — accepted as intended | accepted |
| 6. Rollback / rejection without mutation | `CLOSED → OPEN` declared; supersession is the only reversal vocabulary | no |
| — | **gap id → (owner, path, gate) binding** | **YES** |

## 2. Constraint compliance

| Constraint | Held | How |
|---|---|---|
| `ObservationRegistry` remains the immutable source of history | **yes** | no alternative history proposed; rollback is a new observation |
| No new remediation registry | **yes** | none designed; the one gap is a declarative binding, not a register |
| No mutable updates | **yes** | every outcome is an append; failure/rejection follow `ApprovalRecord`'s `from_state`/`to_state` pattern |
| No direct gap status editing | **yes** | gaps are derived per run by total function; no gap record is writable |
| Every closure is a new observation | **yes** | `OPEN → CLOSED` appended at revision r+1; prior record becomes `SUPERSEDED` by derivation |

## 3. Evidence register

Executed against the live repository. Nothing was written except the four Phase-4 documents.

| # | Claim | Result |
|---:|---|---|
| E1 | Successor work is authorized | `gate=OPEN`, `undispositioned=0`, `decisions=113`, `seal=6f4bd4230c7d8e75` |
| E2 | The UCDA verification changed nothing | `git status` clean for `00-MASTER/UCDA-000001/` — engine at fixed point |
| E3 | The mutation gateway cannot edit a source file | zero `open(`/`Path(`/`read_text`/`write_text`/`subprocess` in `gateway.py`; stages declared pure |
| E4 | The gateway requires a named authority | `_proposal`: "a mutation must name the authority it acts under" |
| E5 | AUE-P-05 authorizes without executing | `mutation_performed` always `False`; 8 named refusal conditions |
| E6 | `pyproject.toml` / `verify.sh` are unfrozen | `FROZEN_PREFIXES = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")` |
| E7 | Subtree write scopes are **not** disjoint | 38 nesting conflicts; `engine/**` swallows 14 gaps, `platform/**` swallows 25 |
| E8 | File-level write scopes are disjoint | 43 distinct target files, **0 collisions** |
| E9 | Central and capability-local scopes do not overlap | 0 overlaps |
| E10 | Regression is a declared transition | `CLOSED → {BLOCKED, CERTIFIED, OPEN, SUPERSEDED}`; `CERTIFIED → {BLOCKED, OPEN, SUPERSEDED}` |
| E11 | `SUPERSEDED` is terminal | `is_terminal == True` |
| E12 | `CERTIFIED` is population-wide | `uicm.closed_cell_ratio` threshold = `matrix.cell_count`, severity BLOCKING; one decision per programme |

## 4. Findings that change the plan

**1. The mutation gateway is narrower than its docstring suggests.** It governs mutation of a
`Population` of `ConstitutionalMetadata`, and its stages are pure — no filesystem. **156 of 158
gaps are source-file changes it cannot govern.** Reading it as a general repository-write authority
would have produced a design nothing could implement.

**2. Execution is unmediated; closure is not.** No engine gates the file edit. The gates validate
after the fact (`verify.sh`, `ec1-ci.yml`, `register.sh --guard`). This is safe for one specific
reason: an owner cannot *claim* closure — closure is only ever a measurement, so a false closure
claim is not expressible. That property is doing more work than any authorization step.

**3. Subtree write scopes would have created duplicate authority.** `engine` and `platform` are
themselves depth-0 capabilities, so a subtree scope would authorize their owners to write inside
39 other capabilities' packages. Phase 2 established one owner per gap; that is necessary but not
sufficient, because overlapping scopes collide even when each gap has one owner. Scope by target
file.

**4. The Phase-2 hold on `pyproject.toml` and `verify.sh` is unenforced.** Both are outside every
frozen prefix and neither is a registered artifact, so nothing mechanically prevents an edit. The
hold is a discipline, not a guard — and 48 gaps sit behind those two files.

**5. `CERTIFIED` is unreachable for any subset of the population.** `uicm.closed_cell_ratio` is
BLOCKING with threshold equal to the total cell count, and there is one decision per programme. So
the 896 closed cells and 4 fully closed capabilities cannot be certified individually. Legal in the
algebra, unreachable in practice.

**6. `COMPOSE` is not a constitutional disposition.** Phase 2 named the set
"REUSE/EXTEND/COMPOSE/CREATE". CMG-000001 Art LXXVII.2 declares
**REUSE / EXTEND / CREATE / RECORD AS GAP / REJECT**, with EXTEND as the default and Art LXXVII.4
forbidding admission by default routing. Corrected in
`UICM-RESOLUTION-AUTHORITY-DETERMINATION.md` §6.

## 5. The one gap, and its disposition

**No instrument binds a `UICM-GAP-*` identifier to an authorization record.**

Consequences today: a resolution cannot be refused for lacking authorization; a closed gap carries
no record of who was authorized to close it; and two owners could act on one gap with nothing
detecting it. The last matters most — Phase 2's one-owner-per-gap determination is currently a
document, not an enforced property.

| Property | Verdict |
|---|---|
| Is a new **authority** required? | **no** — all seven layers exist |
| Is a new **registry** required? | **no** |
| Is a new **state** or **transition** required? | **no** |
| What is required? | one declarative binding: gap → (resolution owner, target file, validating gate) |
| Disposition under Art LXXVII.2 | **EXTEND** of UCOS-UICM-000001 — within its own scope, unaddressed |
| Precedent to follow | `uccep-bindings.json` `checks[]` — data, append-only, no engine change |
| Digest impact | expected neutral if declared additively; **must be verified before landing** |

Not CREATE, and explicitly not routed by default to UAUE or UCCEP (Art LXXVII.4).

## 6. Readiness gates

| Gate | Verdict | Basis |
|---|---|---|
| All six discovery items answered | **PASS** | §1 |
| Authorization path located, not invented | **PASS** | 7 layers, each with a located owner |
| Successor work authorized | **PASS** | E1 — G-14 OPEN, 0 undispositioned |
| Owner boundaries disjoint and total | **PASS** | E7, E8, E9 — with file-level scoping |
| Evidence requirements determined | **PASS** | per-dimension closure evidence + producer rules |
| Certification handoff determined | **PASS** | E12; per-cell certification deferred to Phase 5 |
| Failure and rollback modelled without mutation | **PASS** | E10, E11; `ApprovalRecord` pattern for rejection |
| No new authority / registry / state proposed | **PASS** | §5 |
| Frozen surface unmodified | **PASS** | `engine/uicm/` and `uicm.json` untouched; all committed registers untouched |
| Measurement unperturbed | **PASS** | matrix digest `8ce37cd19fe42adf26d8832d84bd7106d0c0ccac9e12637727c35f81446c87dc` |
| Blocking gaps | **NONE** | the one gap is a binding, and it blocks enforcement rather than discovery |

## 7. Reserved for approval — cumulative across phases

Nothing below has been executed. Phase 3 items are carried forward unchanged.

| # | Step | Phase | Reversible | Digest effect |
|---:|---|---|---|---|
| M1 | Observation loader + L5–L11 load-time checks | 3 | yes | none |
| M2 | Verify: `--matrix --replay`, expect 0 appends and digest `8ce37cd1…` | 3 | yes | none |
| M3 | Reconciliation cases 1–3 | 3 | yes | none while unchanged |
| M4 | Case 4 (retirement) + `SUPERSEDED` filter + LG-03 fail-closed detection | 3 | yes | none while population stable |
| M5 | Two-pass-before-render made explicit and tested | 3 | yes | none |
| **G1** | **Declare the gap → (owner, target file, gate) binding, additively** | **4** | yes | verify neutral first |
| **G2** | **Append `CK-UICM` + `G-27` to `uccep-bindings.json` in the G-22..G-26 form** | **4** | yes | none (data append) |
| M6 | Wave 1 — `uga_engine.py run`, closing 2 gaps | 3 | **no** | matrix digest moves |

## 8. Recommendation

**Approve M1 and M2 only. Hold everything else, including G1 and G2.**

The recommendation is unchanged from Phase 3, and Phase 4 strengthens the reason rather than
altering it. G1 is the natural next step and it is tempting to bundle it with M1 — but the binding
declares *who may close a gap*, and until M1/M2 prove that a closure is durably recorded, a binding
would authorize actions whose effects still vanish on the next run. Authorization without durable
history authorizes something unobservable.

Sequence G1 → G2 after M5, before M6. Then Wave 1 becomes the first resolution that is
simultaneously **authorized** (G1 names the owner), **executed** within a **disjoint boundary**
(governance matrix §3), **evidenced** (`identified:<n>` + `identity_sample:<UCOS-…>`),
**validated** (`verify.sh` 6b, UGA-INV-01..10), and **durably recorded** (M1–M5). That is the
proof-of-architecture the whole programme has been building toward, and it is two gaps wide.

**Do not execute resolution waves.** All 158 gaps remain open and unclosed.

## 9. Carried-forward requirements

Five requirements now stand across phases. Each is easy to lose in implementation and each has a
specific failure mode.

| ID | Requirement | Failure mode if dropped |
|---|---|---|
| LG-03 | A coordinate in the population whose current observation is `SUPERSEDED` must fail the run closed | a retired-then-returned capability is silently transitioned or silently dropped |
| LG-04 | Never sort, parse or range-scan observation identifiers lexicographically; order by `(coordinate, revision)` | ordering silently inverts past `r99` |
| LG-06 | Measure the measurement-report size at M2 and after Wave 1 | a second growth vector goes untracked |
| **EG-01** | Write scope is the **target file**, never the subtree | `engine` and `platform` owners gain write authority over 39 other capabilities' gaps |
| **EG-02** | The hold on `pyproject.toml` and `verify.sh` is unenforced by any guard | 48 gaps' worth of edits can land without any mechanism objecting |

## 10. Status

```
PHASE 4 DISCOVERY          COMPLETE
IMPLEMENTATION             NOT STARTED  (not authorized)
GAP RESOLUTIONS EXECUTED   0            (by design)
NEW AUTHORITY              NOT CREATED  (7-layer composite already exists)
NEW REGISTRY               NOT CREATED  (none required)
NEW STATE / TRANSITION     NOT CREATED  (regression already declared)
ENGINE CODE                NOT WRITTEN
FROZEN SURFACE             UNMODIFIED   (engine/uicm, uicm.json, all committed registers)
MATRIX DIGEST              8ce37cd19fe42adf26d8832d84bd7106d0c0ccac9e12637727c35f81446c87dc  (unmoved)
G-14 IMPLEMENTATION GATE   OPEN         (undispositioned=0 — successor work authorized)
AUTHORIZATION LAYERS       7 / 7 located
OWNER WRITE SCOPES         43, disjoint, total   (file-level scoping required)
CERTIFICATION HANDOFF      PROJECTION   (10 BLOCKING metrics; not-certified, correctly)
MISSING CAPABILITY         1            (gap -> authorization binding; disposition EXTEND)
BLOCKING GAPS              0
CARRIED REQUIREMENTS       5            (LG-03, LG-04, LG-06, EG-01, EG-02)

HALTED PENDING EXPLICIT APPROVAL OF M1 + M2.
```
