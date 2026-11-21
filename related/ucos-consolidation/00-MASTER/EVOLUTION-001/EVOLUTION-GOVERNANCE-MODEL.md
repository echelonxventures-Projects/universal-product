# EVOLUTION-001 — EVOLUTION GOVERNANCE MODEL

| Field | Value |
|---|---|
| PROGRAMME | `EVOLUTION-001` — Post-Baseline Evolution |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| BASELINE | `UCOS-BASELINE-001` · SHA `df763bf917943321886c3fc973eac4a1569b6183` |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. EVOLUTION PRINCIPLES

1. **UCOS-BASELINE-001 is immutable.** No change may invalidate the baseline certification.
2. **Additive only.** All evolution adds to, extends, or enhances — never removes or contradicts.
3. **Governed.** Every change is classified, impact-analyzed, and traced.
4. **Reversible.** Append-only semantics; predecessors preserved via version chains.
5. **Deterministic.** Every evolution produces byte-identical results from identical inputs.
6. **verify.sh remains GREEN.** No evolution may break verification.
7. **Knowledge Once.** No evolution duplicates existing knowledge.
8. **Reuse First.** Extend existing capabilities before creating new ones.

---

## 2. EVOLUTION CLASSIFICATION REGISTER

Every change from UCOS-BASELINE-001 forward is classified as exactly one of:

| Classification | Definition | Examples |
|---|---|---|
| **New capability** | Genuinely new functionality with no prior existence | GAP-1 (Idea Box) |
| **Extension** | Expanding an existing capability's scope or reach | GAP-3, GAP-4, GAP-6, GAP-7 |
| **Enhancement** | Improving quality/completeness of existing capability | GAP-5, UCCEP-F-001, UCCEP-F-002 |
| **Infrastructure** | Operational/tooling improvement | GG-3 (registers), GG-4 (upstream) |
| **Documentation** | Consolidation/indexing of existing knowledge | GAP-2 |
| **Refactoring** | Internal restructuring preserving behavior | (none pending) |
| **Defect correction** | Fixing incorrect behavior | (none pending) |
| **Constitutional amendment** | Change to constitutional law (CEP-009 route) | (none pending) |

---

## 3. EVOLUTION ROADMAP

### Wave-002 (Next executable)

| # | Item | Classification | Priority | Dependencies |
|---|---|---|---|---|
| 1 | GAP-1: Universal Idea Box | New capability | MEDIUM | None |
| 2 | GAP-3: Analysis registry binding | Extension | MEDIUM | None |
| 3 | GAP-4: Metering/Billing realization | Extension | MEDIUM | None |
| 4 | GAP-6: Digital Twin subject expansion | Extension | MEDIUM | None |
| 5 | GAP-7: Operational ecosystem generation | Extension | MEDIUM | None |
| 6 | GAP-2: Constitutional Asset pointer-index | Documentation | LOW | None (CIOA/CCE now satisfied) |
| 7 | GAP-5: Validation evidence model extensions | Enhancement | LOW | CEP-009 amendment route |

### Infrastructure (parallel, non-blocking)

| # | Item | Classification | Owner |
|---|---|---|---|
| 8 | GG-3: Registers 8–11 | Infrastructure | UCI-001 |
| 9 | GG-4: Upstream configuration | Infrastructure | Operator |
| 10 | GG-6: UCIC-001 ownership | Infrastructure | Registration Authority |

### Enhancements (can be interleaved)

| # | Item | Classification | Owner |
|---|---|---|---|
| 11 | UCCEP-F-001: Measured phase3 verdict | Enhancement | UCCEP-000000 |
| 12 | UCCEP-F-002: Traceability fill | Enhancement | Measurement authority |

---

## 4. WAVE EXECUTION GOVERNANCE

Each wave follows this lifecycle:

```
PROPOSED → CLASSIFIED → IMPACT-ANALYZED → APPROVED → IMPLEMENTING → VALIDATED → CERTIFIED → CLOSED
```

**Entry criteria (per wave):**
- All items classified
- Impact analysis complete (no baseline destabilization)
- Dependencies satisfied
- verify.sh GREEN at entry

**Exit criteria (per wave):**
- All wave items implemented
- Registries updated
- Traceability updated
- Certification evidence updated
- verify.sh GREEN at exit
- Evolution version recorded

---

## 5. BASELINE PROTECTION

| Rule | Enforcement |
|---|---|
| Baseline SHA preserved | Git history is append-only; no force-push |
| Certification not invalidated | UCCEP gate must remain blocking=none after every wave |
| Knowledge closure preserved | UAKOS-CLOSURE-002 must remain CLOSED after every wave |
| Registry integrity preserved | `ukb validate` must PASS after every wave |
| Test coverage maintained | pytest ≥90% after every wave |

---

## 6. EVOLUTION VERSION HISTORY

| Version | SHA | Date | Wave | Changes | Status |
|---|---|---|---|---|---|
| BASELINE-001 | `df763bf9` | 2026-07-30 | — | Initial certified baseline (68/68) | **CERTIFIED** |
| `UCOS-EVO-001-W01` | `91a8b1d`…`2a031b8` | 2026-07-30 | Wave-001 (`IMPLEMENT-001` programme) | 131 paths in 5 commits — see §6.1 | **RELEASED** |
| `UCOS-EVO-001-UCEF` | *(uncommitted at time of record)* | 2026-07-31 | Constitutional capability (out-of-wave, additive) | `CEP-009-AMD-001` — Universal Constitutional Evolution Framework — see §6.3 | **IMPLEMENTED · CERTIFIED-PROVISIONAL** |
| `UCOS-EVO-001-FFI` | *(the commit carrying this record — RFP-2)* | 2026-07-31 | Final Foundation Implementation (out-of-wave, foundational closure) | `DEC-MCOS-14`/`WP-UCDA-018` · `UCCEP-F-001`/`OA-5` · `UCEF-K-01` · `OA-2`/`GG-1` · `OA-3` — see §6.4 | **IMPLEMENTED · CERTIFIED-PROVISIONAL** |
| *(future)* | *(tbd)* | *(tbd)* | Wave-002 | *(tbd)* | *(pending)* |

### 6.1 `UCOS-EVO-001-W01` — Wave-001 evolution release

| Field | Value |
|---|---|
| PREDECESSOR | `UCOS-BASELINE-001` · `df763bf917943321886c3fc973eac4a1569b6183` |
| COMMIT RANGE | `91a8b1d`…`2a031b8` — five commits, `df763bf`(exclusive)..`2a031b8` |
| REGISTERED BY | `IMPLEMENT-001D` Phase 5, per `RELEASE-001` §5.1 step 5 |
| SCOPE | Programme `IMPLEMENT-001` → `IMPLEMENT-001A` (audit) → `IMPLEMENT-001B` (disposition) → `IMPLEMENT-001C` (execution) → `IMPLEMENT-001D` (finalization) |
| PATHS | 89 modified · 45 added · **0 removed** · 0 renames |
| LIFECYCLE STATE | **`RELEASED`** (`RELEASE-001` §1) |

> **No commit self-reference.** Per `UCOS-RFP-001` RFP-2, the commit that carries this record is
> owned by version control and is not restated here. The range above names only commits that
> already existed when the record was written.

**The five commits — the canonical sequence of `IMPLEMENT-001C` Deliverable 06 §4:**

| # | SHA | Concern | Paths | Classification (§2) |
|---|---|---|---|---|
| 1 | `91a8b1d` | `RG-09-A` — identifier-namespace widening, provably admits-only | 14 | **Enhancement** |
| 2 | `3ec932b` | `WP-RO-001` — verification, CI and repository-operations gates made fail-closed | 14 | **Defect correction** + **Infrastructure** |
| 3 | `d208272` | `UCCEP-000000` · `UCDA-000001` · `UCOS-RIB-001` — engines, declarations and their deterministic projections, atomically | 62 | **Enhancement** + **Defect correction** |
| 4 | `f201bab` | Authority witness — `BASELINE-001` · `EVOLUTION-001` · `RELEASE-001` · `CAEM-001` · `OAA-001` | 12 | **Documentation** |
| 5 | `2a031b8` | Mission record — `IMPLEMENT-001{,A,B,C}` · `UCOS-{CIOA,CCE,UAR}-001` | 32 | **Documentation** |

**Conditions discharged:** `OA-1` / `O-01` / `UCCEP-F-007` / `WP-UCCEP-005` (the registered **P0
suspensive** action) · `CK-REG-DRIFT` / `G-07` · 15 stale registered `content_hash` values ·
`C-1b` · `B-1` · `UCOS-RIB-001` `GATE-12` and `GATE-04`/`VAL-02` · `UCOS-RFP-001` `CLO-01`
(ABORT → evaluable) · `RB-01`…`RB-05`.

**§5 baseline-protection compliance at this release:**

| Rule | Evidence |
|---|---|
| Baseline SHA preserved | `df763bf9` is an ancestor of every commit; no force-push, no rewrite, no squash |
| Certification not invalidated | `uccep-gate` `blocking=none`, seal `68e8d9a2d396f3dc` **unchanged** from the pre-wave value |
| Knowledge closure preserved | `closure-gate` `CLOSED`, 440 concepts, `gaps=0` across all 7 classes |
| Registry integrity preserved | `ukb validate` PASS — 1193 artifacts, referential integrity OK |
| Test coverage maintained | pytest **94.28%** ≥ 90% |

**Known-open at this release** (carried to Wave-002, none blocking): traceability fill at 2.2%
(`EB-08`) · `UCOS-UAR-001` partial with 5 `EB-01` defects · `repo-ops.sh` `architecture-freeze`
14-path report (disclosed, `RB-04`) · `repository-acceptance` expected-FAIL (disclosed) · one
unreproduced `uccep-gate` exit 2 under concurrency (`IMPLEMENT-001C` D04 §6).

### 6.2 Three findings measured AFTER the §6.1 record was written

`IMPLEMENT-001D` Phase 4 re-ran the gates on the committed tree, which is the first time several
of them could be evaluated at all. Three states became visible. All three are **pre-existing** —
made *measurable* by the release, not caused by it — and none blocks `verify.sh`, so `RELEASED`
stands. Recorded here because §6.1 was written before they were known.

| # | Finding | Evidence | Owner |
|---|---|---|---|
| **W01-F-01** | **`rib-gate` does not pass.** `IMPLEMENT-001C` D06 §4.3 predicted it would. Its two named gates **are** discharged (`GATE-12` `dirty_entries_outside_generated` 86 → **0**; `GATE-04`/`VAL-02` FAIL → PASS), but `VER-09`/`GATE-11` *No orphan capability* (`orphan_units=1`) and `VER-11`/`GATE-03` *No dead engine* (`GAP-DEAD-ENGINE=1`) now fail. **Single cause:** the newly-tracked `00-MASTER.UCOS-UAR-001` is unreachable in every declared reachability dimension and no entry point names it. | `rib-gate` exit 1 · gates **10/12** · units 240 → 241 · seal `82efa15805178be8` · `orphan_members: ["00-MASTER.UCOS-UAR-001"]`. Independently confirmed by `URRC-000001`: tracked engines 20 → 21, unbound engines 4 → **5**, `uar_engine.py` bindings `**none**`. | `EB-01`, Wave-002 order 2 — this **is** `EB-01` defect #3 ("zero enforcement wiring"), now measured rather than asserted |
| **W01-F-02** | **`rfp-gate` is now EVALUABLE and reports NOT A FIXED POINT.** `CLO-01` **PASSES** — the dirty-tree abort is gone, exactly as `IMPLEMENT-001C` D06 §4.3 predicted. The gate then measures **5/8** criteria: `CLO-03` `tracked_modifications=2359`, `CLO-06` `non_fixed_point_passes=3`, `CLO-07` `cycles_detected=2`. **22 × `CYC-OBSERVE`** — `UCOS-RIB-001` and `URRC-000001` persist observations of the tree, so running them is itself a mutation — and **2 × `CYC-REGISTER`** (`00-BOOK/DATA/change-ledger.json` lies in the registration projection zone but is written by `STAGE-UCCEP`). | `rfp-gate` exit 1 · `CLO-01`/`02`/`04`/`05`/`08` PASS · `unattributed_paths=0` · `untracked_outside_excluded=0` | Wave-002. `RB-05` removed the *worst* persisted observation (the per-path dirty list); the remaining `CYC-OBSERVE` set requires ceasing to persist the observation entirely — an **architecture change**, outside a finalization mission's mandate |
| **W01-F-03** | **The registration projection zone is stale by 731 files.** Running `00-BOOK/tools/register.sh` (pipeline `STAGE-REGISTER`) rewrites **731** tracked files: `+7,995 / −7,767`. Two distinct causes. **(a)** `content_hash` values legitimately move because the release changed the artifacts they hash. **(b)** commit `91a8b1d` set `DERIVED_CATEGORY_MAXLEN` 12 → 6, so every derived category code would **migrate** — e.g. `ARCHITECTURA` → `ARCHIT`, `CANONICALOWN` → … — collapsing distinct 12-char codes into shared 6-char ones. Also `Total relationships` 12829 → 12817. | Measured, then **restored**: `artifacts.json` `generated_at` remains `2026-07-28T05:52:19+00:00` as committed. `git status` → 0 entries. | **`REG-AUTO-001`**, not `IMPLEMENT-001D`. Re-deriving 1193 artifacts' category codes is a registration-authority migration with its own admission route. **Not** blocked: `verify.sh` Stage 4 (`enforce --pre`, 1193 ≡ 1193, 0 unregistered, 0 drift) and Stage 5 (`validate`, schema + referential integrity PASS) both pass on the committed state, and the widened patterns keep the existing 12-char codes valid — which is why the widening was required. `CK-REG-DRIFT` is `NOT-EXECUTED, in_scope=false` at the standard tier and says so, per `RO-F-06`, committed in `d208272`. |

**What IS proven deterministic at this release.** All eleven non-registration producer engines
reach a **byte-identical fixed point** on the committed tree: two consecutive full passes in
declared pipeline order (`closure` → `ucda` → `uei` → `uer` → `urrc` → `umk` → `upf` → `rib` →
`uccep`) emit sha256-identical bytes for every path, and `git status` reports **0** entries
afterwards. Commits `0a5f1ba` (URRC) and `ac44985` (RIB) are that convergence: RIB is regenerated
**last**, from a clean tree, because it measures the tree's own dirtiness — the same reason
`df763bf` exists.

> **The prediction that `rib-gate` would pass was wrong, and is recorded as wrong.** A finalization
> mission may not fix what it finds; it must leave the finding where the next mission will trip
> over it.

**`IMPLEMENT-001` remains INTERRUPTED.** D02, D03 and D04 do not exist, and D04 defines the
`B-1`/`B-2` gate prerequisites all nine `EB-*` items cite. Per §4 wave-entry criteria, **no
`EB-*` item is orderable until those deliverables exist** — this release does not open Wave-002
execution, it only makes it reachable.

---

## 6.3 `UCOS-EVO-001-UCEF` — the Universal Constitutional Evolution Framework

| Field | Value |
|---|---|
| DIRECTIVE | `CEP-009-AMD-001` · programme `UCEF-000001` |
| CLASSIFICATION (§2) | **Constitutional amendment** — the `CEP-009` route, executed as an **extension** |
| PREDECESSOR | `CEP-009` version 1.0 |
| NORMATIVE HOME | `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` **ADDENDUM B** |
| OPERATIONAL HOME | `00-MASTER/UCEF-000001/` — `AUTHORITY = NONE — DERIVED TRUTH` |
| GATE | `make ucef-gate` · `.github/workflows/ucef-gate.yml` |
| LIFECYCLE STATE (§4) | **CERTIFIED** — `CERTIFIED-PROVISIONAL`, Tier T1 VACANT |

**What this closes.** §1.8 of this model already mandates *Reuse First* and §2 already routes a
constitutional amendment through `CEP-009`. What did not exist was a **normative statement, in
the instrument that owns evolution, of the lifecycle a *construct* traverses** — §4 above
governs a *wave*, `CEP-009` Art III governs an *artifact*, and `00-CMG/CMG-000001` LXXVI.2
governs *admission* and stops at certification. The three were never composed, so a construct
could be introduced along a path no instrument owned, and the no-redesign property was
certified analytically (`02-ARCHITECTURAL-STABILITY-CERTIFICATION.md`,
`05-CONSTITUTIONAL-CLOSURE-CERTIFICATION.md`) but never measured.

**Disposition.** **EXTEND**, under `CMG-000001` LXXVII.2(b). CREATE was rejected: LXXVI and
LXXVII already own construct admission and `CMG-GAP-09` is recorded **CLOSED** by them, so a
second mechanism would breach `CMG-INV-02` and `CMG-L-14`. ADDENDUM B creates **no authority,
no registry, no lifecycle and no namespace** (`CMG-000001` XLI.5): all fifteen lifecycle stages
and sixteen acceptance properties bind to owners that already exist, and a self-guard measures
that none of them lies inside `00-MASTER/UCEF-000001/`.

**§5 baseline-protection compliance:**

| Rule | Evidence at this evolution |
|---|---|
| Baseline SHA preserved | No history rewritten; the change is additive to the working tree only |
| Certification not invalidated | `00-MASTER/UCCEP-000000/uccep-bindings.json` **untouched** — the aggregate seal is unchanged by construction, because aggregation of `ucef-gate` is deliberately deferred to the aggregate-gate owner (see §6.3 *Known-open*) |
| Knowledge closure preserved | `closure-gate` **CLOSED**, 447 concepts, `gaps=0` across all 7 classes |
| Registry integrity preserved | `ukb validate` **PASS** — 1193 artifacts, append-only page ledger intact, referential integrity OK; `register.sh` **10/10 integrity domains CERTIFIED**, 1193 ≡ 1193, **0 identities minted**, `page_cursor` unchanged at 9618 |
| Test coverage maintained | pytest **≥ 90%** (`verify.sh` Stage 2 PASS) |
| Meta-constitutional integrity | `make cmg-gate` **0 findings**, 43 artifacts, 60 concerns, `READY-PROVISIONAL` |
| `verify.sh` GREEN | **PASS** — all five mandatory stages |

**Additive-only proof (§1.2).** Paths added: `00-MASTER/UCEF-000001/**`,
`.github/workflows/ucef-gate.yml`, `00-MASTER/CHECKPOINTS/CKPT-2026-07-31-UCEF-000001.md`. Paths
modified, all strictly by append or by a version statement: `00-CEP/CEP-009-…md` (ADDENDUM B +
AMENDMENT RECORD appended; metadata, Art XXIV.1 and footer version 1.0 → 1.1),
`00-CMG/CMG-REGISTRY.json` (the `CEP-009` `version` field), `02-CANONICAL-OWNERSHIP-MATRIX.md`
(addendum + one status annotation), `Makefile` (additive `ucef` block + three help lines), and
this file plus `MCP-002` / `MCP-004` / `MCP-006`. Regenerated by the registration authority's own
transaction, not hand-edited: `00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}/**`. **Paths
removed: 0.** No `CEP-009` Article, clause, law, invariant, state or transition identifier is
renumbered, reused, repurposed or withdrawn (`CMG-000001` XLII.4).

**Not this evolution's act, present in the working tree, disclosed rather than absorbed.** The
tree was already dirty at session start (32 entries) with uncommitted work of other programmes —
`MCOS-000001`, the `UAKOS-CLOSURE-008` decision/superiority engines, `UKAP-001` registers,
`engine/civilization`, `pyproject.toml`. During this session the pre-existing `SessionStart` hooks
in `.kiro/hooks/` and that WIP additionally rewrote `00-MASTER/UCCEP-000000/**` (including a
995-insertion reformat of `uccep-bindings.json`), `00-MASTER/UCDA-000001/**`,
`00-MASTER/UCOS-RFP-001/rfp-declaration.json`, `Makefile`'s `mcos` block,
`.github/workflows/mcos-gate.yml` and `00-MASTER/UCCEP-000000/20-META-CIVILIZATION-OPEN-WORLD-CLOSURE.md`.
**None of it was authored, requested or reverted by this evolution** — reverting another
programme's uncommitted work would destroy it. This is the already-disclosed `W01-F-02`
`CYC-OBSERVE` / `CYC-REGISTER` residue: running the gates on this tree is itself a mutation of it.

**Known-open at this evolution (none blocking):**

| # | Item | Disposition |
|---|---|---|
| `UCEF-K-01` | `ucef-gate` is **not** aggregated into `00-MASTER/UCCEP-000000/uccep-bindings.json`. | **DISCHARGED by §6.4.** It was deliberate at the time of this record: adding a binding changes the UCCEP rendered fixed point and its seal, which §5 of this model protects, so it was routed to the aggregate-gate owner as a governed follow-up. That follow-up has since been performed **by** the aggregate-gate owner, under §4 wave governance and with the §5 evidence set recorded at §6.4. Six `CK-UCEF-*` checks, gate `G-17` and `PROGRAM-000019` are now declared; `G-17` reports **PASS** (6/6). |
| `UCEF-K-02` | Traceability lane population remains at the corpus baseline (`EB-08`, 2.2%). | Pre-existing and **advisory**, not blocking. ADDENDUM B closes its own traceability (B.12) and the framework's own traceability register measures **zero orphans**. |
| `UCEF-K-03` | The registration projection zone was regenerated during this evolution. | **DISCHARGED for this evolution, and it changed what `W01-F-03` says.** `00-BOOK/tools/register.sh` — Stage 9 of the lifecycle B.4.1 legislates, and this programme's declared `registration_owner` — was executed, so `00-CEP/CEP-009` and `00-CMG/CMG-REGISTRY.json` now carry correct `content_hash` values: source and projection moved in **one** change, as `REG-AUTO-001` §7 Atomic Creation Law requires. Measured: **0 identities changed · 0 identities minted · 0 paths added · 0 paths removed · `page_cursor` 9618 → 9618 · 1193 ≡ 1193**, so the append-only identity ledger is provably intact. The transaction is now a **fixed point**: four consecutive `register.sh` runs leave all **1227** projection paths byte-identical, `change-ledger.json` included (it converged after the single stale-state transition). Integrity domains **10/10 CERTIFIED**. **What this newly measures and hands to `REG-AUTO-001`:** the pre-existing staleness of `W01-F-03` is **645 `volume` reprojections** (e.g. `VOL-000` → `VOL-002` across `00-CEP/`) plus **13 `00-BOOK/SCHEMAS/*` `content_hash` moves**, **not** the 731-file *category-code* migration that `W01-F-03` predicted — `DERIVED_CATEGORY_MAXLEN` 12 → 6 did **not** re-derive any identifier, because `allocate()` is path-keyed and returned every existing UID verbatim. The 12-char codes (`UCOS-ARCHITECTURA-…`, `UCOS-INFRASTRUCTU-…`) are unchanged and still valid. `W01-F-03` cause (b) is therefore **not realized**; only cause (a) was, and it is now discharged. |

---

## 6.4 `UCOS-EVO-001-FFI` — Final Foundation Implementation

| Field | Value |
|---|---|
| PREDECESSOR | `UCOS-EVO-001-UCEF` |
| CLASSIFICATION (§2) | **Defect correction** + **Enhancement** + **Infrastructure**. Not a constitutional amendment: `uccep-bindings.json` and `ucda-decisions.json` both declare `authority: "NONE — DERIVED TRUTH"`, and no Article, law, invariant or clause of any `CEP`/`CMG` instrument is added, renumbered or withdrawn. |
| SCOPE | Closure of the last four in-jurisdiction **foundational** residues: the dual composition authority, the phase-3 constant verdict, the un-aggregated evolution gate, and three stale finding records. |
| LIFECYCLE STATE | `CERTIFIED` at §4 wave-exit, **`CERTIFIED-PROVISIONAL`** in standing (Tier T1 VACANT — `VAC-01` / `CMG-OQ-02`) |

> **No commit self-reference.** Per `UCOS-RFP-001` RFP-2 the commit carrying this record is owned
> by version control and is not restated here.

**What was closed, and by whose act:**

| Residue | Owner that discharged it | Evidence |
|---|---|---|
| `DEC-MCOS-14` / `WP-UCDA-018` — two ordering mechanisms coexisted | `engine/factory` + `engine/foundation` under a declared surface | Ordering authority relocated to `engine/foundation/composition/ordering.py`, **below** both consumers; `engine/factory/phases.py` declares the phase graph and the order is **derived**; the frozen `DEFAULT_STAGES` tuple (a *third* declaration) removed. `engine/tests/factory/test_phases.py` proves both acceptance clauses. |
| `UCCEP-F-001` / `DG-7` / `WP-UCCEP-001` / `OA-5` — a gate with no reachable PASS state | `00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py` | `repository_status` measured from the located PHASE-002 determination and cross-checked against its blocking-gap count; three literal-`True` criteria measured. Proven **both ways**: exit 0 at the located CLOSED state, exit 1 with the determination forced to NOT-CLOSED. `CK-CLOSURE-P3` is no longer advisory **and** is now bound to `G-02`, which it previously was not bound to at all. |
| `UCEF-K-01` — the evolution gate was not aggregated | `00-MASTER/UCCEP-000000` (the aggregate-gate owner) | Six `CK-UCEF-*` checks, `G-17`, `PROGRAM-000019`; `G-17` **PASS** 6/6. |
| `OA-2` / `GG-1` (`UCCEP-F-003`), `WP-UCCEP-004` / `OA-3` (`UCCEP-F-006`) — record lag | `00-MASTER/UCCEP-000000` | Both substances were **already** discharged in code and measured before the record was changed: `engine/graph/validation.py` includes `dependency_cycle` in `is_valid` and the located cycle is now `[]`; `jsonschema==4.26.0` is a pinned dev dependency and the CI `\|\| true` is gone. Records moved to `IMPLEMENTED`, `blocking: false`. |

**§5 baseline-protection compliance at this evolution:**

| Rule | Evidence |
|---|---|
| Baseline SHA preserved | `df763bf9` remains an ancestor; no force-push, no rewrite, no squash, **0 paths removed** |
| Certification not invalidated | Seal moved `f44d8b6e…` → **`a6ae6b49d4aa3703`**, which §5 requires be *recorded*, not held constant — a binding cannot be added without moving it. **No gate regressed:** `gate_blocking` is `['CK-REG-DRIFT']` alone, exactly as at the pre-wave tree, and that check is commit-gated by construction (`REG-AUTO-001` §16.3). Gates 15/17 and programmes 16/19 PASS; the only failures are `G-07`, `G-15`, `PROGRAM-000004/5/17`, all carrying `CK-REG-DRIFT` and nothing else. The certification **ceiling shrank** from five findings to two (`UCCEP-F-002` advisory, `UCCEP-F-004` external). |
| Knowledge closure preserved | `UAKOS-CLOSURE-002` **CLOSED**, concepts 447, gaps 0 |
| Registry integrity preserved | `ukb validate` **PASS** — 1193 artifacts, append-only page ledger intact, referential integrity OK |
| Test coverage maintained | pytest **5127 passed**, aggregate coverage ≥90%; `engine/civilization` held at **100%** statement *and* branch, so `MCOS-000001`'s certification is unweakened |

**Known-open at this evolution (none blocking, none in jurisdiction):**

| # | Item | Disposition |
|---|---|---|
| `FFI-K-01` | `CK-REG-DRIFT` (`G-07`, `G-15`) fails on the working tree. | **Not closable in a working tree.** It measures the difference between regenerated and *committed* projections, so its PASS state is unreachable until source and the four projection subtrees are committed together. Discharged by the commit that carries this record. |
| `FFI-K-02` | `UCCEP-F-002` / `OA-4` / `WP-UCCEP-002` — traceability completeness at the corpus baseline. | **Advisory** (`CK-HEALTH`), not blocking, and **not foundational**: it is lane *population*, a data-volume task over 1198 artifacts, not a redesign of the traceability model. Left as routine work. |
| `FFI-K-03` | `GG-3` / `WP-GDR-001` — four declared `UCI-001` registers are absent. | Verified genuinely absent. Left to its **located owner** (`UCI-001`); authoring another owner's registers would breach `CMG-INV-02`. |
| `FFI-K-04` | `GG-6` — capability staging has no citable owner (`UCIC-001` is absent from `CMG-REGISTRY.json`, so `CMG-L-01` bars citing it). | **Out of jurisdiction.** Admission to the Constitution Registry is the registration authority's act under `CMG-000001` Art LXXVI, not this evolution's. |
| `FFI-K-05` | `DEF-01`, `DEF-02` / `VAC-01`, `CMG-OQ-01`/`-02`/`-03`/`-05`/`-07`, `OA-6`, `UCCEP-F-004`. | **Not manufacturable in-repository.** Each requires an external constituent act; `CMG-000011` records them as not closable by the meta layer, and self-ratification is prohibited (`CMG-000001` XLIV.5). This is why every determination here is `CERTIFIED-PROVISIONAL`. |

---

## 7. THE CONSTITUTIONAL EVOLUTION CONTRACT

| Field | Value |
|---|---|
| BASELINE | `UCOS-BASELINE-002` — `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` §2 |
| STATUS | **BOUND — not created.** Every obligation below was already implemented, owned and gate-bound before this section was written. This section **composes and records** the binding; it introduces no stage, no mechanism, no authority and no gate. |
| CONSTITUTIONAL BASIS | `UCOS-RFP-001` `rfp-declaration.json` `lifecycle` (the canonical 14-step implementation lifecycle with its gate bindings) · `CEP-009` ADDENDUM B.4 (the 15-stage constitutional evolution lifecycle) · `CMG-000001` LXXVI.2 (the 8-step admission procedure) · `RELEASE-001` §1 (the 8-state release lifecycle) · §1 and §2 of this model |

> **Why composition and not creation.** §1 of this model already mandates *Reuse First* and
> *Additive only*; `RELEASE-001` §1 already governs a *release*; `CEP-009` ADDENDUM B.4 already
> governs a *construct*; `UCOS-RFP-001` already governs *closure*. What did not exist in one
> place was the statement that the ten obligations a change owes are **one contract**, each with a
> named owner and a reachable gate. Recording that is not a second evolution model — `CEP-009`
> ADDENDUM B.11 prohibits one, and `CMG-INV-02` would fail if a second owner of *evolution* were
> minted. Nothing below is novel; every cell cites an owner that already discharges it.

### 7.1 The contract

Every future change from `UCOS-BASELINE-002` forward SHALL discharge all ten obligations, in
order. Each is owned, each is measured, and each has a gate whose verdict is reachable in both
directions.

| # | Obligation | Canonical owner | Gate | Lifecycle step |
|---|---|---|---|---|
| 1 | **measure baseline** | `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` (registry) · `00-MASTER/UCOS-RIB-001/rib_engine.py` (repository truth) · `00-MASTER/URRC-000001/urrc_engine.py` (reality binding) | `rib-gate` 12/12 · `urrc-gate` 10/10 | `RFP` 1–2 *Repository Discovery · Context Assimilation*; `CEP-009` B.4 stages 1–3 |
| 2 | **derive delta** | §2 of this model — the closed 8-member classification register. A change is exactly one of: new capability · extension · enhancement · infrastructure · documentation · refactoring · defect correction · constitutional amendment | `RELEASE-001` §1 `CLASSIFIED` state | `RFP` 3 *Architecture Review*; `CMG-000001` LXXVI.2(a)–(b) |
| 3 | **reuse existing authority** | `CMG-000001` LXXVII.2 totality rule (**EXTEND is the default**, `CREATE` requires that no owner exists) · `02-CANONICAL-OWNERSHIP-MATRIX.md` · `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` (`replacement_prohibited` on 50 of 71) | `urrc-gate` `G-02` *Reuse before create* · `G-03` *Non-proliferation* · every programme's `--check-reuse-before-create` · `rib-gate` `GATE-09` *Zero Duplicate Capability* | `CEP-009` B.4 stage 4; `CMG-000001` LXXVI.2(c) |
| 4 | **implement** | `00-MASTER/UCIC-001-UNIVERSAL-CAPABILITY-IMPLEMENTATION-CONTRACT.md` · in the `00-MASTER/CAEM-001/` mandated form (**declaration + engine + gate + self-guards**) | `uccep` `G-13` *Implementation Authorization* | `RFP` 4; `CEP-009` B.4 stages 11–12 |
| 5 | **register** | `00-BOOK/tools/register.sh` (`REG-AUTO-001` Atomic Registration Transaction, 10 phases) · `00-BOOK/tools/ukb.py` (append-only identity ledger) | `uccep` `G-06` *Repository Truth* · `G-07` *Registry* · `CK-REG-ENFORCE` · `CK-REG-VALIDATE` · `CK-REG-DRIFT` | `RFP` 8 *Registry Regeneration*; `CEP-009` B.4 stages 6, 9 |
| 6 | **validate** | `00-CEP/CEP-004` · `./verify.sh` | `uccep` `G-10` *Validation* · `verify.sh` 5/5 stages | `RFP` 6; `CEP-009` B.4 stage 13 |
| 7 | **verify** | `00-CEP/CEP-001` · `00-MASTER/UCOS-RIB-001` · `engine/determinism` | `uccep` `G-10` · `rib-gate` · `CK-DETERMINISM-BUILD` | `RFP` 5 |
| 8 | **certify** | `00-CEP/CEP-005` · `00-MASTER/UCCEP-000000/uccep_engine.py --tier full --gate` | `uccep` `G-11` *Certification* — `blocking=none`, `gate_exit=0`. **Absence of evidence is never evidence**: `UNAVAILABLE` or `NOT-EXECUTED` exits 1 | `RFP` 9; `CEP-009` B.4 stage 14 |
| 9 | **update evidence** | `00-CEP/CEP-008` · `00-MASTER/UCOS-UTCE-001/utce_engine.py` · `00-MASTER/UCDA-000001/ucda_engine.py` | `uccep` `G-12` *Evidence* · `G-14` *Implementation Evidence* (`CEP-002` Art 28) · `G-20` *Constitutional Traceability Closure* | `RFP` 7 *Evidence Generation* |
| 10 | **re-measure** | `00-MASTER/UCOS-RFP-001/rfp_engine.py --gate` — the full declared 13-stage pipeline, three times, from the **committed** state | `uccep` `G-15` *Repository Fixed-Point* — 8/8 `CLO-*` criteria | `RFP` 11–14 *Fresh Repository Discovery · Pipeline Re-execution · Fixed-Point Verification · Programme Closure* |

### 7.2 The two absolute rules

| Rule | Statement | Enforcement that already exists |
|---|---|---|
| **R-1 — No future implementation may modify the baseline directly.** | A certified baseline record is never edited. A new baseline is a **new row** in the registry; the predecessor record is preserved byte-identically. | §1.1 of this model (baseline immutable) · `RELEASE-001` §2.2 (force-push and artifact removal prohibited) · `CMG-000001` LXXVI.3 (admission is append-only; no renumber, rename, reclassify or invalidate) · `CEP-009` ADDENDUM B.7.2 (a proposal that would renumber, rename, reclassify or invalidate an existing enumeration member **is not an admission** and is refused) · `CEP-007` supersession-with-lineage, never replacement · git history append-only, verified by `git merge-base --is-ancestor` |
| **R-2 — All evolution is append-only.** | Paths are added; existing paths change only by append or by a version statement. **Removals: 0.** | `00-BOOK/tools/ukb.py` `allocate()` — path-keyed, append-only over `00-BOOK/DATA/id-ledger.json`; an existing UID is returned verbatim, never re-minted · `CK-REG-VALIDATE` (duplicate-UID absence, page non-overlap, no inverted range) · DP-03 frozen-path guard (`.github/workflows/ec1-ci.yml`) over `00-SOURCE/`, `99-FREEZE/` and the authored `00-BOOK` canon · `CMG-INV-11` (every lineage predecessor resolves) · `G-20` `UTCE-OB-04` (lineage acyclic) |

### 7.3 Why the contract is *reachable*, not merely declared

`UCOS-BASELINE-002` is the first baseline at which all ten obligations were discharged and
**measured** in one run: `make rfp-gate` executes obligations 5–10 as declared pipeline stages
(`STAGE-VERIFY`, `STAGE-REGISTER`, `STAGE-UCCEP` among them) three consecutive times from the
committed tree and reports `stage_failures=0`, `tracked_modifications=0`,
`non_fixed_point_passes=0`, `cycles_detected=0`. Before this baseline the contract was declared
and its final obligation was unreachable — `EVOLUTION-001` §6.2 `W01-F-02` records `rfp-gate`
reporting *NOT A FIXED POINT* with 2 detected cycles. A contract whose last step cannot pass is
not a contract. It can pass now, and it does.

---

> **Evolution governance model ESTABLISHED.**

All future development proceeds as governed evolution from `UCOS-BASELINE-002` (§7), whose
predecessor chain from `UCOS-BASELINE-001` is recorded at §6 and registered at
`00-MASTER/BASELINE-001/BASELINE-REGISTRY.md`. The baseline is immutable. Every change is
classified, traced, validated, and certified. verify.sh remains the permanent gate, and the
repository fixed point (`G-15`) is the permanent closure condition.

---

*END — `EVOLUTION-001` Evolution Governance Model · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
