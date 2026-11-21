# BASELINE-001 — CANONICAL BASELINE REGISTRY

| Field | Value |
|---|---|
| REGISTRY | `UCOS-BASELINE-REGISTRY` — the canonical register of certified constitutional baselines |
| OWNER | `BASELINE-001` — Certified Implementation Baseline (the already-located baseline authority) |
| AUTHORITY | `NONE — DERIVED TRUTH`. This registry certifies nothing of its own motion. Every value below is **measured** from the machine model of the programme that owns the condition, and each row names that model. An unreadable source is a failure, never an assumption. |
| CONSTITUTIONAL BASIS | `RELEASE-001` §3.1 (the `UCOS-BASELINE-NNN` scheme) · §3.3 (baseline advancement criteria) · `EVOLUTION-001` §1.1/§1.4 (baseline immutable, append-only) · `CMG-000001` LXXVI.3 (admission is append-only) |
| APPEND-ONLY | Records are **added**, never edited, renumbered, reclassified or withdrawn. `UCOS-BASELINE-001` below is reproduced by reference to its own record, which this registry does not modify. |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`) |

> **No new authority.** This registry introduces no authority, no namespace, no lifecycle and no
> mechanism (`CMG-000001` XLI.5). It is a record held by the baseline authority that already
> exists. A second baseline programme directory was **not** created: `CMG-INV-02` requires the
> concern→owner map be injective on concerns, and `BASELINE-001` already owns *certified
> baseline*. `RELEASE-001` §5.3's operational suggestion of a `BASELINE-NNN/` directory per
> baseline is an operational guide, not a law, and following it would have minted a duplicate
> canonical home — which `RIB` `GATE-08` and `CMG-INV-02` both forbid.

> **No commit self-reference.** Per `UCOS-RFP-001` **RFP-2** the commit that carries a record is
> owned by version control and is not restated inside the record. Each row therefore names the
> commit it was **measured against** — a commit that already existed when the row was written —
> and leaves its own containing commit to git. Restating the containing commit is the `CYC-COMMIT`
> self-reference class, and it is what makes a record stale the instant it is committed.

---

## 1. REGISTRY

| # | Baseline ID | Measured against | Branch | Date | State | Record |
|---|---|---|---|---|---|---|
| 1 | `UCOS-BASELINE-001` | `df763bf917943321886c3fc973eac4a1569b6183` | `integration/recovery-001` | 2026-07-30 | **CERTIFIED** · superseded as *current* by row 2, **not** invalidated | `00-MASTER/BASELINE-001/CERTIFIED-BASELINE-RECORD.md` (unmodified) |
| 2 | `UCOS-BASELINE-002` | `f25b4652274318744adcef66e19c2fab1c91fa7e` | `integration/recovery-001` | 2026-08-01 | **CERTIFIED — CURRENT CONSTITUTIONAL BASELINE** | §2 of this registry |

`df763bf9` is a verified **ancestor** of `f25b465` (`git merge-base --is-ancestor` exit 0), so
`EVOLUTION-001` §5 *"Baseline SHA preserved"* holds: no history was rewritten, squashed or
force-pushed between the two rows.

---

## 2. `UCOS-BASELINE-002` — CURRENT CERTIFIED CONSTITUTIONAL BASELINE

### 2.1 Identity

| Field | Value | Measured from |
|---|---|---|
| Baseline ID | `UCOS-BASELINE-002` | `RELEASE-001` §3.1 scheme |
| Commit | *the containing commit — owned by version control, never restated here* (`RFP-2`) | version control |
| Measured against | `f25b4652274318744adcef66e19c2fab1c91fa7e` (`f25b465`) | `git rev-parse HEAD` |
| Branch | `integration/recovery-001` | `git rev-parse --abbrev-ref HEAD` |
| Git clean at measurement | **0 entries** — verified before measurement, again after the full 13-stage pipeline ran three times, and again after `verify.sh` | `git status --porcelain` |
| Predecessor baseline | `UCOS-BASELINE-001` · `df763bf9` | row 1 |
| Timestamp | commit timestamp — owned by version control (`RFP-2`); authored date 2026-08-01 | version control |
| Constitutional version | `CMG-000001` **v1.1** · `CMG-REGISTRY.json` **1.1.0** · `CEP-009` **v1.1** (ADDENDUM B / `CEP-009-AMD-001`) | `00-CMG/CMG-REGISTRY.json` `version` / `canonical_source_version` |

### 2.2 Registered programmes — **19 / 19**

| Measure | Value | Measured from |
|---|---|---|
| Declared programmes | **19** (`PROGRAM-000001` … `PROGRAM-000019`) | `00-MASTER/UCCEP-000000/uccep.json` `programs` |
| PASS | **19 / 19** — 14 `PASS`, 5 `PASS-WITH-ADVISORY` (`PROGRAM-000007`, `-000012`, `-000014`, `-000015` carry `CK-HEALTH`; see §2.10) | same |
| Constitutional artifacts registered | **43** across 8 Kinds | `00-CMG/CMG-REGISTRY.json` `artifacts` |
| Concerns allocated | **60**, injective on concerns (`CMG-INV-02`), exactly one located owner each (`CMG-INV-03`) | `00-CMG/CMG-REGISTRY.json` `concerns` |

### 2.3 Registered capabilities — **71 declared · 235 discovered units**

| Measure | Value | Measured from |
|---|---|---|
| Capability records | **71** | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` `count` |
| `CERTIFIED` | **21** | same, `implementation_status` |
| `IMPLEMENTED` | **48** | same |
| `PLANNED` | **2** | same |
| `replacement_prohibited` | **50 / 71** | same |
| Discovered capability units | **235** | `00-MASTER/UCOS-RIB-001/rib.json` `units` |
| Capability coverage | `GATE-07` **PASS** — every capability record resolves to a discovered unit **and** every implementation unit is covered by a capability record (`unresolved_catalogue_records`=0, `uncatalogued_units`=0) | `rib.json` `gates` |
| Baseline-001 realization figure | **68/68** — the frozen count at row 1 (19 CERTIFIED + 47 IMPLEMENTED + 2 REALIZED-BY-COMPOSITION). The live catalogue has since grown to 71; the 68 is a historical snapshot, not a current enumeration | `CERTIFIED-BASELINE-RECORD.md` §2 |

### 2.4 Registered CKOs (Canonical Knowledge Objects) — **447 / 447 homed**

| Measure | Value | Measured from |
|---|---|---|
| Concept total | **447** | `00-MASTER/UAKOS-CLOSURE-002/closure.json` `concept_total` |
| Homed | **447 / 447** | same, `homed` |
| Families | **26** | same, `families` |
| `IMPLEMENTED` | **322** | same, `dispositions` |
| `DEFERRED` | **89** | same |
| `SPECIFIED` | **20** | same |
| `REJECTED` | **16** | same |
| Certified | **241** · not certified **206** | same, `certified` |
| In code | **305** · not in code **142** | same, `in_code` |
| Gap classes | **7 / 7 at zero** — `conversation_only` 0 · `duplicate_canonical_homes` 0 · `in_repo_unhomed` 0 · `not_homed_concepts` 0 · `orphan_concepts` 0 · `ukda_content_hash_duplicates` 0 · `upload_only` 0 | same, `gaps` |
| Determination | **CLOSED — 100%** · seal `2fafb487f47fcff8a21d639fc7c960e5f29ef3b9f0cc8aaebef41733edb2cb6b` | `00-MASTER/UAKOS-CLOSURE-002/12-REPOSITORY-CLOSURE-CERTIFICATE.md` |
| Verified knowledge objects | **23,859**, `unclassified` **0** | `00-MASTER/UAKOS-CLOSURE-008/assimilation.json` |

> The closure determination and its certificate are **gitignored generated artifacts**
> (`.gitignore` — `00-MASTER/UAKOS-CLOSURE-002/[0-9][0-9]-*.md`, `closure.json`, `phase2.json`),
> regenerated deterministically from the committed tree by `closure_engine.py`. They are derived
> truth by construction and can never be stale. Their authored sources are tracked.

### 2.5 Registered universes — **0**

| Measure | Value | Measured from |
|---|---|---|
| Universe Kind recognized | **YES** — `CMG-K-12` *Universe*, "a bounded composition of nuclei and domains", binding `Compositional` | `00-CMG/CMG-REGISTRY.json` `kinds`; `CMG-000001` Art XIII line 394 |
| Artifacts holding Kind `CMG-K-12` | **0** — registered artifact Kinds are `CMG-K-01/02/03/10/11/17/22/23` only | `00-CMG/CMG-REGISTRY.json` `artifacts` |
| Basis for zero | `CMG-000001` **XIII.5** recognizes `CMG-K-11` (Nucleus) and `CMG-K-12` (Universe) as constitutional Kinds whose **models are owned elsewhere and consumed by reference**, and expressly forbids this Article restating them. `CMG-000010` line 44 records *Universes — No · composition owned elsewhere*. | as cited |
| Determination | **ZERO IS CORRECT AND OWNED.** This is not an unhomed gap: the Kind is admitted, the composition model is out of jurisdiction, and admitting a Universe artifact is the `CMG-000001` LXXVI.2 procedure, not a defect of this baseline. Advisory. | — |

### 2.6 Registered corpus

| Measure | Value | Measured from |
|---|---|---|
| Registered artifacts | **1,194** (1194 ≡ 1194, 0 unregistered, 0 unclassified, 0 invalid, 0 drift) | `00-BOOK/DATA/artifacts.json` `count`; `verify.sh` Stage 4 |
| Volumes | **25** | `00-BOOK/DATA/volumes.json` |
| Relationships (graph edges) | **12,819** | `00-BOOK/DATA/relationships.json` |
| Identity ledger | append-only, page ledger intact, referential integrity OK, **0 executions** (forward-only lifecycle intact) | `verify.sh` Stage 5 (`ukb.py validate`) |

### 2.7 Validation state — **PASS**

| Measure | Value | Measured from |
|---|---|---|
| `verify.sh` | **GREEN — 5/5 stages PASS**, 154s wall clock | live run, `verify.sh` summary |
| ruff lint + format-check | PASS | Stage 1 |
| Registry validate (schema + integrity) | PASS — 1194 artifacts | Stage 5 |
| `URRC-000001` | **REALITY-BOUND** · gate `OPEN` · exit 0 · **10/10 gates PASS** (`G-01`…`G-10`) · seal `8432609e10e719c6` | `00-MASTER/URRC-000001/urrc.json` |
| `UCOS-UFEP-001` validation dimensions | **14/14 satisfied**, 0 failures, all blocking | `00-MASTER/UCOS-UFEP-001/03-CONSTITUTIONAL-COMPLETION-DETERMINATION.md` |
| `UCOS-UTCE-001` | **CONSTITUTIONAL-TRACEABILITY-CLOSED** · gate `OPEN` · exit 0 · seal `a75b6e69e221a244` | `00-MASTER/UCOS-UTCE-001/utce.json` |

### 2.8 Verification state — **PASS**

| Measure | Value | Measured from |
|---|---|---|
| `UCOS-RIB-001` | **BLUEPRINT CERTIFIED — REPOSITORY MAY PROCEED** · exit 0 · **12/12 gates PASS** · seal `5dd0c0e700a81f85` | `00-MASTER/UCOS-RIB-001/rib.json` |
| Zero-finding invariants | `orphan_units` 0 · `owner_collisions` 0 · `architectural_cycles` 0 · `dead_interfaces` 0 · `dead_registry_entries` 0 · `registration_drift` 0 · `dirty_entries` 0 · `closure_duplicate_homes` 0 · `closure_gaps` 0 · `duplicate_findings` 0 | `rib.json` `metrics` |
| Determinism | **byte-identical = True**, environment fingerprint `d52bb3e84695c1b3` | `determinism-evidence/determinism-evidence.json` |
| Tests | **5,997 passed · 1 skipped · 0 failed** (the skip is `UFEP-F-005`: the suite is downstream of the certifier that runs it) | `verify.sh` Stage 2 |
| `UCOS-AEE-001` | **CONVERGED-PROVISIONAL** · exit 0 · converged `true` · seal `efeba054528e04b8` | `00-MASTER/UCOS-AEE-001/aee.json` |

### 2.9 Certification state — **CERTIFIED-PROVISIONAL**

| Measure | Value | Measured from |
|---|---|---|
| Aggregate certifier | `UCCEP-000000` · tier **full** · `gate_exit` **0** · `gate_blocking` **[]** · `blocking_failures` **[]** · `unavailable` **[]** · `unproven` **[]** · seal `d4484b9a355ef6a7` | `00-MASTER/UCCEP-000000/uccep.json` |
| Constitutional gates | **21 / 21 PASS** (`G-01`…`G-21`); `G-11` `PASS-WITH-ADVISORY` | same, `gates` |
| Certification standing | **`CERTIFIED-PROVISIONAL`** | same, `certification` |
| Certification ceiling | **one item only** — `UCCEP-F-004`: constitutional finality is reserved to an out-of-corpus authority | same, `certification_ceiling` |
| Corpus certification | **CERTIFIED** · **10/10 integrity domains passed** | `00-BOOK/DATA/certification.json` |
| `UMK-000001` · `UPF-000001` · `MCOS-000001` | certification matrices **100.00% PASS** each (20 dimensions) | each `08-FINAL-CERTIFICATION-REPORT.md` |
| `UCEF-000001` | `CERTIFIED-PROVISIONAL` · `GATE-OPEN` | `00-MASTER/UCEF-000001/ucef.json` |
| `UEI-000001` · `UER-000001` · `UCDA-000001` | `CERTIFIED-EVOLVING` · `CERTIFIED-RESILIENT` · `ASSIMILATED` — all gate `OPEN`, exit 0 | respective `*.json` |
| `UCOS-UCAF-001` · `UCOS-URAT-001` | `AUTHORITY-MODEL-BOUND` · `RATIFICATION-REGISTRY-BOUND` — both gate `OPEN`, exit 0 | respective `*.json` |
| `UAEP-000001` | `PLATFORM BOUND — EVERY NAMED CAPABILITY RESOLVES IN REPOSITORY TRUTH` · gate `OPEN` | `00-MASTER/UAEP-000001/uaep.json` |

### 2.10 Coverage state — **PASS (≥90% gate)**

| Measure | Value | Measured from |
|---|---|---|
| Aggregate coverage (gate metric) | **94.57%** ≥ 90% required | `verify.sh` Stage 2 (`--cov-fail-under=90`) |
| Statement coverage | **95%** — 42,605 / 44,788 covered, 2,183 missed | `coverage.xml` / Stage 3 |
| Branch coverage | **91.86%** — 9,116 branches, 134 partial | `coverage.xml` |
| `GAP-COVERAGE` | **26** — advisory, bound to no gate | `rib.json` `gaps` |
| `CK-HEALTH` | **advisory FAIL**, governed by `UCCEP-F-002`; the sole entry in `advisory_failures` and the sole cause of all five `PASS-WITH-ADVISORY` verdicts | `uccep.json` |

### 2.11 Fixed-point state — **REPOSITORY IS A FIXED POINT**

| Measure | Value | Measured from |
|---|---|---|
| Determination | **REPOSITORY IS A FIXED POINT** · gate `OPEN` · exit **0** | live `make rfp-gate` on the clean committed tree |
| Closure criteria | **8 / 8 PASS** | same |
| `CLO-01` tree clean before assertion | `initial_dirty_entries` = **0** | same |
| `CLO-02` every required stage succeeds | `stage_failures` = **0** | same |
| `CLO-03` no tracked file modified by any pass | `tracked_modifications` = **0** | same |
| `CLO-04` nothing staged | `staged_entries` = **0** | same |
| `CLO-05` no untracked entry outside an excluded location | `untracked_outside_excluded` = **0** | same |
| `CLO-06` byte-identical after every pass | `non_fixed_point_passes` = **0** | same |
| `CLO-07` no self-reference cycle | `cycles_detected` = **0** | same |
| `CLO-08` all residue attributable to a declared producer | `unattributed_paths` = **0** | same |
| Passes × stages | **3 passes × 13 stages**, including `STAGE-VERIFY` (`verify.sh`) and `STAGE-UCCEP` — both heavy, both required, both run three times | `rfp-declaration.json` `pipeline` |
| Findings | **0** (`findings: []`) | `00-MASTER/UCOS-RFP-001/rfp.json` |
| Declaration seal | `40fddf13156871af2bddef54506fa4d54a4ed0b86941a1aede39e88fc9bd0b33` | same |
| Tree after the run | **0 entries** | `git status --porcelain` |

> **What §2.11 discharges.** `EVOLUTION-001` §6.2 recorded `W01-F-01` (`rib-gate` fails,
> `orphan_units`=1, `GAP-DEAD-ENGINE`=1), `W01-F-02` (`rfp-gate` NOT A FIXED POINT —
> `tracked_modifications`=2359, `non_fixed_point_passes`=3, `cycles_detected`=2, 22 ×
> `CYC-OBSERVE`, 2 × `CYC-REGISTER`) and `W01-F-03` (registration projection stale by 731 files).
> All three are now **measured closed**: `rib-gate` 12/12 with `orphan_units`=0 and
> `GAP-DEAD-ENGINE`=0; `rfp-gate` 8/8 with every criterion at zero; and `registration_drift`=0
> with the register stage running three times inside the fixed point without moving a byte. This
> is the first baseline at which closure is **asserted after** the repository was proven to
> reproduce itself from its committed state, which is the property `UCOS-RFP-001` exists to
> establish.

### 2.12 Constitutional completion and freeze eligibility

| Measure | Value | Measured from |
|---|---|---|
| **CONSTITUTIONAL COMPLETION** | **TRUE** — 11/11 completion criteria SATISFIED, each measured against the sealed machine model of the programme that owns the condition | `00-MASTER/UCOS-UFEP-001/03-CONSTITUTIONAL-COMPLETION-DETERMINATION.md` |
| **FREEZE ELIGIBILITY** | **TRUE** — 5/5 subjects `ELIGIBLE`, 25/25 `CEP-007` Article V preconditions SATISFIED, 0 unsatisfied | `00-MASTER/UCOS-UFEP-001/01-FREEZE-ELIGIBILITY-REGISTER.md` |
| Sealed baseline | **13/13 verified · 0 drifted** | same, `00-UFEP-DASHBOARD.md` |
| Freeze performed | **NO** — reserved to Freeze Authority (`CEP-007` VII.1, I.5); `UFEP-VAL-09` fails closed if this programme ever reaches a post-eligibility state | same |
| Constitutional finality | **UNCHANGED** — reserved to an authority outside the corpus; no in-repository act can supply it (`CEP-006` I.4, `CMG-000001` XLIV.5) | same |
| Seal | `6549de91dc20f2228f8d50c468ed3556c34429bfc70e13992e2949c24f185600` | same |

### 2.13 Baseline advancement criteria — `RELEASE-001` §3.3

| Criterion | Satisfied | Evidence |
|---|---|---|
| A significant capability milestone is reached | **YES** | Constitutional completion `TRUE` and repository fixed point achieved — neither held at `UCOS-BASELINE-001`, where `rfp-gate` and `rib-gate` both failed (`W01-F-01`, `W01-F-02`) |
| All blocking gates pass | **YES** | `gate_blocking` `[]`, `blocking_failures` `[]`, 21/21 gates, 19/19 programmes, `rib` 12/12, `urrc` 10/10, `rfp` 8/8 |
| `verify.sh` GREEN | **YES** | 5/5 stages PASS, live |
| UCCEP `CERTIFIED-PROVISIONAL` with `blocking=none` | **YES** | tier `full`, `gate_exit` 0 |
| Evolution version history records the complete chain from prior baseline | **YES** | `EVOLUTION-001` §6 — `UCOS-BASELINE-001` → `UCOS-EVO-001-W01` → `UCOS-EVO-001-UCEF` → `UCOS-EVO-001-FFI` → this baseline |

> **`UCOS-BASELINE-002` CERTIFIED.** Every criterion `RELEASE-001` §3.3 states for baseline
> advancement is measured satisfied. This baseline is the **Certified Constitutional Baseline**
> for all future UCOS Ω∞ evolution, at the `CERTIFIED-PROVISIONAL` ceiling that `UCCEP-F-004`
> makes permanent until an out-of-corpus constituent act closes `VAC-01`.

---

*END — `BASELINE-001` Canonical Baseline Registry · append-only · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
