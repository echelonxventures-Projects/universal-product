# BASELINE-001 — FINAL BASELINE CERTIFICATE

| Field | Value |
|---|---|
| CERTIFICATE | Final Baseline Certificate — `UCOS-BASELINE-002` |
| OWNER | `BASELINE-001` — Certified Implementation Baseline |
| AUTHORITY | `NONE — DERIVED TRUTH`. Nothing here is asserted. Every value is measured from the machine model of the programme that owns the condition, and each row names that model. Where a value could not be measured it is reported as unmeasured, never assumed. |
| SCOPE | Baseline protection (measured, not recreated) · evolution readiness (exposed, not invented) · the canonical baseline determination |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`) |
| REGISTRY | `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` §2 |
| CONTRACT | `00-MASTER/EVOLUTION-001/EVOLUTION-GOVERNANCE-MODEL.md` §7 |

---

## PART A — BASELINE PROTECTION (MEASURED)

Each of the nine protections was located in the mechanism that already enforces it and then
**measured**. Nothing was recreated. Where enforcement is partial or absent, that is stated as a
finding with a located owner rather than closed by minting a new mechanism — `CMG-INV-02` bars a
second owner for an owned concern, and `CEP-009` ADDENDUM B.7 bars redesign as an evolution route.

| # | Protection | Enforcement | Measured | Blocking |
|---|---|---|---|---|
| 1 | **Duplicate canonical authorities** | `rib` `GATE-08` *Knowledge Once* · `VER-05` *Ownership* · `VER-06` · `VER-07` *No duplicate truth* · `DUP-KNOWLEDGE` · `urrc` `G-03` *Non-proliferation* · `CMG-INV-02`/`-03`/`-08` · `CK-CLOSURE-P2` | `closure_duplicate_homes` **0** · `owner_collisions` **0** · `DUP-KNOWLEDGE` **0** · `closure_gaps` **0** · duplicate canonical homes **0** of 447 concepts | **BLOCKING · PASS** |
| 2 | **Parallel implementations** | `rib` `GATE-09` *Zero Duplicate Capability* over 6 blocking classes · `urrc` `G-02` *Reuse before create* · `--check-reuse-before-create` on every programme engine · `CMG-INV-02` | `duplicate_findings` **0** — `DUP-CAPABILITY` 0 · `DUP-INTERFACE` 0 · `DUP-RUNTIME` 0 · `DUP-REGISTRY` 0 · `DUP-CONSTITUTION` 0 · `DUP-KNOWLEDGE` 0 | **BLOCKING · PASS** — with advisory residue, see `RISK-02` |
| 3 | **Replacement of certified canonical objects** | Append-only identity ledger (`ukb.py allocate()`, path-keyed, returns existing UIDs verbatim) gated by `CK-REG-VALIDATE` · DP-03 frozen-path guard over `00-SOURCE/`, `99-FREEZE/`, authored `00-BOOK` canon · `CK-REG-DRIFT` · normative prohibitions `CMG-000001` LXXVI.3, `CEP-009` B.7.2, `CEP-007` supersession-with-lineage · `CMG-INV-11` lineage predecessors resolve · `G-20` `UTCE-OB-04` lineage acyclic | Ledger integrity **PASS** — duplicate-UID absence, page non-overlap, no inverted range, referential integrity OK, 1194 artifacts, **0 identities minted**, forward-only lifecycle intact. Frozen prefixes guarded in CI. | **PARTIAL** — see `GOV-01` |
| 4 | **Non-traceable evolution** | `G-20` *Constitutional Traceability Closure* (`CK-UTCE`, `UTCE-OB-01`…`OB-06`) · `G-14` *Implementation Evidence* (`CEP-002` Art 28, `CK-DECISION-EVIDENCE`) · `CMG-INV-11` · `assimilate-gate` | `UTCE` **CONSTITUTIONAL-TRACEABILITY-CLOSED** · rooted, closed, **zero orphans**, lineage acyclic · gate `OPEN` · `UCDA` **ASSIMILATED**, undispositioned **0** | **BLOCKING · PASS** for constitutional instruments and decisions; **PARTIAL** per code change — see `GOV-02` |
| 5 | **Unregistered implementation** | `CK-REG-ENFORCE` (`ukb.py enforce`, exit 1) → `G-06`, `G-07` · `register.sh` Phase 0 exit 4 / Phase 9 exit 4 · `--guard` exit 3 + pre-commit hook · `rib` `VAL-07` *Registries* · `VER-10` *No dead registry* | unregistered eligible **0** · unclassified **0** · invalid **0** · `registration_drift` **0** · `GAP-REGISTRY` **0** · `dead_registry_entries` **0** · 1194 ≡ 1194 | **BLOCKING · PASS** |
| 6 | **Uncertified implementation** | `rib` `GATE-05` *Repository Certification* (corpus scope) · `CK-MCOS-CERTIFICATION` · `umk`/`uprf`/`mcos` 20-dimension matrices · `CK-HEALTH` (advisory) | `certification_verdict_absent` **0** · `certification_domains_failed` **0** · corpus verdict **CERTIFIED**, 10/10 domains · UMK/UPF/MCOS matrices **100.00%** each | **PARTIAL** — corpus scope only; per-unit `GAP-CERTIFICATION` **164** is measured and gates nothing, see `EB-01` |
| 7 | **Orphan artefacts** | `rib` `GATE-11` *Zero Orphan Capability* · `VER-09` · `CK-CLOSURE-P1` · `CK-CLOSURE-P2` · `CK-UTCE` · `CMG-INV-03` | `orphan_units` **0**, `orphan_members` **[]** · `orphan_concepts` **0** · UTCE orphans **0** · orphan governance **0** | **BLOCKING · PASS** |
| 8 | **Dead capabilities** | `rib` `VER-11` *No dead engine* (`GAP-DEAD-ENGINE`) · `VER-12` *No dead runtime* · `VER-10` · `GATE-07` *Capability Coverage* · `VAL-08` *Implementations* · `aee --check-mandate-coverage` | `GAP-DEAD-ENGINE` **0** · `dead_interfaces` **0**, `dead_interface_members` **[]** · `dead_registry_entries` **0** · `GAP-CAPABILITY` **0** · `GAP-RUNTIME` **0** · AEE mandate universe **57**, converged | **BLOCKING · PASS** |
| 9 | **Circular ownership** | `CMG-INV-05` (dependency graph + precedence lattice acyclic, deterministic Kahn sort) · `CMG-INV-04` · `rib` `GATE-10` *Zero Circular Dependency* · `VER-08` · `CK-GRAPH`/`G-08` · `G-20` `UTCE-OB-04` · `rfp` `CLO-07` | `architectural_cycles` **0** · `benign_cycles` **2** (declared `CYC-INIT-REEXPORT`, package `__init__` re-export) · `cycles_detected` **0** live · CMG lattice acyclic · graph `dangling_edge_endpoints` 0 | **BLOCKING · PASS** |

**Protection determination: 7 of 9 fully enforced blocking with zero findings; 2 partially
enforced with the shortfall recorded, owned and disclosed.** No protection was recreated. No
duplicate enforcement mechanism was introduced.

---

## PART B — EVOLUTION READINESS (EXPOSED, NOT INVENTED)

Only surfaces Repository Truth already supports. No new architecture.

### B.1 Reusable capability map

| Surface | Location | Measure |
|---|---|---|
| Capability catalogue (live) | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | **71** records `RC-01`…; 21 CERTIFIED · 48 IMPLEMENTED · 2 PLANNED; **50** carry `replacement_prohibited: true` — the reuse-before-create key |
| Discovered capability units | `00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md` · `rib.json` `units` | **235** units, each with class, location, disposition and the **rule id** (`RUL-01`…`RUL-11`) that produced it — computed, never asserted |
| Typed capability model | `platform/foundation/capabilities.py` | `CapabilityKind` (ENGINE / PLATFORM), frozen `Capability`, `CapabilityCatalog`; invariant: an ENGINE capability MUST bind an engine `ContractRef`, a PLATFORM capability MUST NOT — the EC-1 ↔ EC-2 boundary |
| Named capability bindings | `00-MASTER/UAEP-000001/uaep-platform.json` + `01-CAPABILITY-BINDING-REGISTER.md` | **16** capabilities `UAEP-CAP-01`…`-16`, each with disposition REUSE / EXTEND / COMPOSE **and** the `RC-nn` record it binds to |
| Layer packages | `engine/` `platform/` `intelligence/` `application/` `service/` `infrastructure/` `data/` | the physical capability surface; `GATE-07` proves the catalogue and the surface are mutually total |

### B.2 Extension points — append to a declaration, change no engine

Every programme engine is proven literal-free by `--check-no-enumeration`, which is the mechanical
guarantee that appending to its declaration extends behaviour with **zero** engine change.

| Declaration | Appending admits |
|---|---|
| `00-MASTER/UCOS-RFP-001/rfp-declaration.json` | a producer (pipeline stage), cycle class, artifact class, lifecycle step or closure criterion |
| `00-MASTER/UCCEP-000000/uccep-bindings.json` | a programme, gate, check, principle, invariant, finding or work package (currently 19 / 21 / 37 / 22 / 17 / 8 / 5) |
| `00-MASTER/UMK-000001/umk-kernel.json` | a metatype (**open metatype system**, ADR-0003), substrate, quality gate, proof category, certification dimension |
| `00-MASTER/UPF-000001/upf-provider.json` | a provider responsibility, substrate, gate, proof category, certification dimension (ADR-0004) |
| `00-MASTER/UCEF-000001/ucef-framework.json` | a law, lifecycle stage, **construct class** (33), expansion axis, criterion, governance obligation, validation |
| `00-MASTER/UEI-000001/uei-evolution.json` · `UER-000001/uer-resilience.json` | a newly proven capability / gap binding |
| `00-MASTER/URRC-000001/urrc-bindings.json` · `UCOS-RIB-001/rib-blueprint.json` | a deliverable, matrix, gate, substrate, derivation, binding mode / a discovery selector, measure, plane, disposition rule, **reachability dimension**, entry point |
| `00-CMG/CMG-REGISTRY.json` | a kind, standing, reach, tier, namespace, state, transition, relationship type, artifact, concern |
| `00-BOOK/tools/config.py` | a volume, classify rule, program root, relationship type, change event type, sync stage |
| `engine/kernel/registry.py` · `engine/provider/framework.py` | runtime: `UniversalRegistry.register()` over **open** metatype keys · `register_category()` / `register_provider()` |
| `00-BOOK/DATA/id-ledger.json` | a metadata-declared volume auto-registers append-only under `discovered_volumes` — unlimited future volumes with no config edit |

### B.3 Constitutional admission points

| Point | Location | Procedure |
|---|---|---|
| Concept admission | `CMG-000001` **Art LXXVI** | 8 steps: Discover → Classify → Dispose {**EXTEND default** / CREATE / REJECT} → Allocate (one owner) → Relate (acyclicity) → Register → Verify (all twelve invariants) → Certify. LXXVI.3 **append-only**; LXXVI.5 **unbounded in count**; LXXVI.6 no admission by reinterpretation |
| Unknown future concepts | `CMG-000001` **Art LXXVII** | totality rule — exactly one of five outcomes: REUSE / EXTEND / CREATE (meta only) / RECORD-AS-GAP / REJECT-with-reason. Default routing prohibited |
| Construct lifecycle | `00-CEP/CEP-009` **ADDENDUM B.4** | 15 stages, each bound to a located owner; B.6 twelve architectural acceptance criteria; B.7 redesign refused as an evolution route |
| Amendment | `00-CEP/CEP-009` Art I–XXV | the artifact-scoped change lifecycle |
| Registry admission | `00-CMG/CMG-REGISTRY.json` + `00-CMG/tools/cmg_validate.py` | 43 artifacts, 60 concerns, twelve invariants re-run on every admission |

### B.4 Evolution interfaces

| Interface | Location |
|---|---|
| Baseline registry (append-only) | `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` |
| Evolution contract (10 obligations, owners, gates) | `00-MASTER/EVOLUTION-001/EVOLUTION-GOVERNANCE-MODEL.md` §7 |
| Evolution classification register (closed 8-member set) | same, §2 |
| Evolution version history | same, §6 |
| Release lifecycle (8 states, per-state evidence) | `00-MASTER/RELEASE-001/RELEASE-LIFECYCLE.md` §1 |
| Baseline advancement criteria | same, §3.3 |
| Evolution intelligence (observe → learn → optimize → recommend → plan → execute) | `00-MASTER/UEI-000001/` — 15 capabilities, 23 outputs, creates no mechanism, binds 11 existing owners |
| Autonomous evolution loop | `00-MASTER/UCOS-AEE-001/aee-declaration.json` — `make aee` runs to convergence, `aee-gate` is the fail-closed convergence gate |
| Roadmap compiler | `00-MASTER/UCOS-MXR-001/roadmap_engine.py` — compiles current state into backlog / graph / waves / critical path |

### B.5 Automatic discovery points

| Mechanism | Location | Property |
|---|---|---|
| Eligibility universe | `ukb.py eligibility_universe()` | scans the tree, publishes a sha256 of the sorted path list so a local tree and a CI checkout can prove they computed the identical universe |
| Identity allocation | `ukb.py allocate()` | path-keyed, idempotent, append-only; an existing UID is returned verbatim |
| Volume discovery | `ukb.py cmd_build()` | a metadata-declared volume not in config auto-registers append-only |
| Connector discovery | `ukbx.py sync --due` | discovers connectors under `00-BOOK/tools/connectors/`, runs only those past their cadence cursor |
| Reachability | `rib_engine.py` (lines ~1039–1046) | dimensions read **entirely** from `rib-blueprint.json` `reachability` (7); adding a dimension is a declaration edit |
| Repository discovery | `rib-blueprint.json` `discovery` (8 selectors) + `entrypoints` (5) | 235 units discovered by selector, not enumeration |
| Knowledge discovery | `closure_engine.py` · `phase2_engine.py` · `UKAP-001/corpus_engine.py` | corpus currency decided by content / git commit order, **never** by filename or mtime; fails closed if a newer export is ignored |
| Capability discovery | `engine/discovery/` (`CK-DISCOVERY`) | `engine.discovery.cli coverage` |

### B.6 Registration flow

`bash 00-BOOK/tools/register.sh` — the `REG-AUTO-001` Atomic Registration Transaction. Re-entrancy
locked; `trap cleanup EXIT`; fails with `TRANSACTION INCOMPLETE`.

| Phase | Command | Exit on failure |
|---|---|---|
| 0 | `ukb.py enforce --pre` | 4 |
| 1 | `ukb.py build` | 1 |
| 2–4 | `ukbx.py sync --due` · `twin` · `portal` | 1 |
| 5–7 | `ukb.py validate` · `ukbx.py validate` · `ukbx.py twin --check` | 2 |
| 8 | `ukbx.py certify` (9 integrity domains) | 2 |
| 9 | `ukb.py enforce` (post: completeness + parity + append-only audit) | 4 |
| 10 | transaction sealed | — |

Write zone (identical to the `--guard` drift set): `00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}/`.
`--guard` exits **3** on drift and is installed as the `pre-commit` hook by `--install-hooks`.

### B.7 Certification flow

```
./verify.sh                      →  5 stages (ruff · pytest+cov≥90 · coverage · enforce --pre · validate)
make <programme>-gate            →  fail-closed programme determination
make <programme>-self            →  --check-declaration --check-no-enumeration --check-write-scope --check-determinism
make uccep-gate --tier full      →  37 checks → 21 gates G-01..G-21 → CERTIFIED-PROVISIONAL
make rfp-gate                    →  G-15: the 13-stage pipeline × 3 from the committed state → FIXED POINT
```

Exit semantics are uniform: **0** every blocking check in scope executed and passed · **1** a
blocking check failed **or produced no evidence** (`UNAVAILABLE` / `NOT-EXECUTED` — *absence of
evidence is never evidence*) · **2** fail-closed abort. 19 CI workflows in `.github/workflows/`
bind these gates to push and pull_request.

**Readiness determination: READY.** All seven surfaces exist, are measured, and are declaration-driven.

---

## PART C — FINAL BASELINE CERTIFICATE

| Field | Determination |
|---|---|
| **Repository Baseline ID** | **`UCOS-BASELINE-002`** |
| **HEAD** | measured against `f25b4652274318744adcef66e19c2fab1c91fa7e` (`f25b465`); this record's own commit is owned by version control and is not restated (`RFP-2`) |
| **Branch** | `integration/recovery-001` |
| **Repository Status** | **CLOSED — 100%** · 447 concepts · gaps 0/7 classes · seal `2fafb487f47fcff8` |
| **Git Clean** | **YES — 0 entries**, verified three times: before measurement, after the 13-stage pipeline ran three times, and after `verify.sh` |
| **Verification** | **PASS** — `rib` 12/12 gates, `BLUEPRINT CERTIFIED`, seal `5dd0c0e700a81f85` · determinism byte-identical · 5,997 tests passed, 1 skipped, 0 failed |
| **Validation** | **PASS** — `verify.sh` GREEN 5/5 · `urrc` 10/10, `REALITY-BOUND` · `utce` `CONSTITUTIONAL-TRACEABILITY-CLOSED` · `ufep` 14/14 dimensions |
| **Certification** | **`CERTIFIED-PROVISIONAL`** — `uccep` tier `full`, `gate_exit` 0, `gate_blocking` `[]`, 21/21 gates, 19/19 programmes, seal `d4484b9a355ef6a7` · corpus `CERTIFIED` 10/10 domains · UMK/UPF/MCOS 100% |
| **Coverage** | **PASS** — 94.57% aggregate (≥90% gate) · 95% statement (42,605/44,788) · 91.86% branch |
| **Fixed Point** | **YES — REPOSITORY IS A FIXED POINT** · 8/8 criteria · 3 passes × 13 stages · cycles 0 · findings 0 · gate `OPEN` |
| **Constitutional Completion** | **TRUE** — 11/11 criteria SATISFIED (`UCOS-UFEP-001`) |
| **Freeze Eligibility** | **TRUE** — 5/5 subjects `ELIGIBLE`, 25/25 `CEP-007` Art V preconditions SATISFIED; **freeze NOT performed** (reserved to Freeze Authority) |
| **Evolution Readiness** | **READY** — 7/7 surfaces measured (Part B) |
| **Engineering Backlog** | **6 items**, 0 blocking (§C.1) |
| **Governance Backlog** | **5 items**, 0 blocking to engineering (§C.2) |
| **Outstanding Risks** | **4**, 1 blocking to ABSOLUTE certification only (§C.3) |

### C.1 Engineering backlog — 6 items, none blocking

| ID | Item | Measured | Canonical owner | Repository location | Constitutional basis | Verdict |
|---|---|---|---|---|---|---|
| `EB-01` | Per-unit certification evidence absent | `GAP-CERTIFICATION` = **164** | family owners (APPLICATION / ARCH / CEP / …) named per member; aggregate `00-MASTER/UCCEP-000000` | `00-MASTER/UCOS-RIB-001/rib.json` `gaps`; items `MXR-EVID-001`… in `00-MASTER/UCOS-MXR-001/roadmap.json` (`EVID` class = 96) | `CEP-005` (certification) · `UCCEP-F-002` | **ADVISORY** — bound to no gate. Binding it blocking today would fail `G-11` on 164 open members; that is a certification-authority decision, not an engineering fix |
| `EB-02` | Implementation evidence lanes unpopulated | `GAP-EVIDENCE` = **227** | measurement authority; `WP-UCCEP-002` | same `rib.json`; `00-MASTER/UCCEP-000000/uccep-bindings.json` `findings` | `CEP-008` (evidence & traceability) · `UCCEP-F-002` (`GOVERNED`, `blocking: false`) | **ADVISORY** — data-volume task over 1,198 artifacts, not a model redesign (`FFI-K-02`) |
| `EB-03` | Verification records unpopulated | `GAP-VERIFICATION` = **204** | measurement authority | same `rib.json` | `CEP-004` · `UCCEP-F-002` | **ADVISORY** |
| `EB-04` | Coverage records absent for some units | `GAP-COVERAGE` = **26** | unit owners | same `rib.json` | `CEP-004` | **ADVISORY** — aggregate gate (≥90%) passes at 94.57% |
| `EB-05` | One unresolved dependency record | `GAP-DEPENDENCY` = **1** | `engine/graph` (`CK-GRAPH`) | same `rib.json` | `CEP-001` Art XV.2 acyclicity | **ADVISORY** — `GATE-06` *Dependency Closure* and `GATE-10` both PASS; `architectural_cycles` = 0 |
| `EB-06` | Roadmap projection lags HEAD | `roadmap.json` `head_commit` = `05342cb`, HEAD = `f25b465` | `00-MASTER/UCOS-MXR-001` | `00-MASTER/UCOS-MXR-001/roadmap.json` (tracked) | `UCOS-RFP-001` `CLO-08` | **ADVISORY** — `UCOS-MXR-001` is **not** a declared stage of the RFP pipeline, so it neither participates in nor threatens the fixed point; `CLO-08` `unattributed_paths` = 0. Re-rendering it is a routine act by its own owner |

Roadmap context (`00-MASTER/UCOS-MXR-001/roadmap.json`, verdict **CONDITIONAL GO**): 811 items ·
**180 READY** · 2 BLOCKED · 510 DEFERRED · 22 waiting-for-ratification · 1,358 effort points ·
`completion` = 71.6% disposition-implemented, 67.8% in-code, 53.9% certified. Declared next
executable capability: **EC-3 Band 10 (Data) realization**. The 2 BLOCKED are EC-3 Bands 11/12/13
(sequential band realization) and constitutional finality (`DR-RAT-11`, exogenous).

### C.2 Governance backlog — 5 items, none blocking to engineering

| ID | Item | Canonical owner | Repository location | Constitutional basis | Verdict |
|---|---|---|---|---|---|
| `GOV-01` | No check asserts that a **certified** canonical object cannot be replaced in place. Enforcement covers identity (append-only ledger) and the frozen prefixes (DP-03), not the general certified-object set. | Freeze Authority (`CEP-007`) with `00-MASTER/UCCEP-000000` as aggregate-gate owner | `00-CEP/CEP-007-…md`; `.github/workflows/ec1-ci.yml` DP-03; `00-BOOK/tools/ukb.py` | `CEP-007` (supersession-with-lineage, never replacement) · `CMG-000001` LXXVI.3 · `CEP-009` B.7.2 | **ADVISORY** — normatively prohibited, not measured. Adding measurement is a **new mechanism** and must traverse `CEP-009` ADDENDUM B.4 admission; it is not a baseline-establishment act |
| `GOV-02` | No gate requires a source change to name its authorizing requirement or decision. Traceability is enforced on constitutional instruments and decisions, not per code change. | measurement authority; `WP-UCCEP-002` | `00-MASTER/UCCEP-000000/uccep-bindings.json` (the 13-lane spine check is `advisory: true`) | `CEP-008` Art XI–XII · `UCCEP-F-002` | **ADVISORY** — same population task as `EB-02`/`EB-03` |
| `GOV-03` | Four declared `UCI-001` registers are absent (registers 8–11). | `UCI-001` (its located owner) | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-UCI-001-…md`; `GG-3` / `WP-GDR-001` | `CMG-INV-02` — authoring another owner's registers would breach it | **ADVISORY** (`FFI-K-03`) |
| `GOV-04` | Capability staging has no citable owner: `UCIC-001` is absent from `CMG-REGISTRY.json`, so `CMG-L-01` bars citing it. | Registration Authority (`CMG-000001` Art LXXVI) | `00-MASTER/UCIC-001-…md`; `00-CMG/CMG-REGISTRY.json` | `CMG-000001` Art LXXVI admission · `CMG-L-01` | **ADVISORY** — out of jurisdiction for this mission (`FFI-K-04`, `GG-6`) |
| `GOV-05` | **Registered universes = 0.** `CMG-K-12` *Universe* is an admitted constitutional Kind with no instantiated artifact. | owned elsewhere by reference | `00-CMG/CMG-REGISTRY.json` `kinds`; `CMG-000010` line 44 | `CMG-000001` **XIII.5** — Nucleus and Universe models are owned elsewhere and consumed by reference; this Article SHALL NOT restate them | **ADVISORY** — zero is correct and owned, not an unhomed gap |

Also open at the meta layer and recorded there, not here: `CMG-GAP-01`…`-09` (all recorded CLOSED
by the Articles that own them), `CMG-OQ-01`…`-07`, `UFEP-F-002` (a located determination records
**BAND-scope** freeze as NOT READY — a scope `UCOS-UFEP-001` explicitly does not close).

### C.3 Outstanding risks — 4

| ID | Risk | Canonical owner | Repository location | Constitutional basis | Verdict |
|---|---|---|---|---|---|
| `RISK-01` | **Tier T1 is VACANT.** No ratified normative artifact occupies Tier T1; the referent exists only as frozen non-normative `.docx` under `00-SOURCE/CONSTITUTIONS/`. Every determination depending on T1 — including the standing of `CMG-000001` itself — is PROVISIONAL. | an authority **outside the corpus**; self-ratification is prohibited | `00-CMG/CMG-REGISTRY.json` `vacancies[0]` (`VAC-01`); `09-DR-RAT-11-ASSESSMENT.md` | `CMG-000001` XVII.4 closure procedure · `CMG-L-12` · `CEP-006` I.4 · `CMG-000001` XLIV.5 (self-ratification prohibited) · `UCCEP-F-004` (`blocking: true`) · `CMG-OQ-02` | **BLOCKING to ABSOLUTE certification only.** Not blocking to any engineering act, any gate, or this baseline. It is the sole entry in `uccep.json` `certification_ceiling` and the reason every determination reads `CERTIFIED-PROVISIONAL`. **Not manufacturable in-repository.** |
| `RISK-02` | **9 advisory duplicate signals**, declared non-blocking: `DUP-RESPONSIBILITY` **5** (cross-layer name collisions — `engine.certification`/`platform.certification`, `engine.foundation`/`platform.foundation`, `engine.kernel`/`intelligence.kernel`, …), `DUP-ENGINE` **2** (multi-engine programme), `DUP-FREEZE` **2** (freeze-boundary copy). | `00-MASTER/UCOS-RIB-001` (declares the `blocking: false` flags) | `00-MASTER/UCOS-RIB-001/rib-blueprint.json` duplicate classes; `rib.json` `duplicates` | `CEP-001` Knowledge Once · `rib` `GATE-09` | **ADVISORY** — disclosed rather than prevented. The 6 blocking duplicate classes are all **0**. Several collisions are the intended EC-1/EC-2 boundary (`platform/foundation/capabilities.py` enforces that a PLATFORM capability must **not** re-bind an engine contract), so promoting the class to blocking would fail on correct architecture. Reclassifying it is `UCOS-RIB-001`'s act. |
| `RISK-03` | **`CK-HEALTH` advisory FAIL.** Repository health is RED: traceability metadata incomplete across 1,198 registered artifacts. Sole entry in `advisory_failures`; sole cause of all five `PASS-WITH-ADVISORY` verdicts (`G-11`, `PROGRAM-000007/12/14/15`). | measurement authority; `WP-UCCEP-002` | `00-MASTER/UCCEP-000000/uccep-bindings.json` `UCCEP-F-002` (`GOVERNED`, `blocking: false`) | `CEP-008` · `UCCEP-F-002` | **ADVISORY** — `gate_blocking` is `[]` and `blocking_failures` is `[]` with this finding standing. Same substance as `EB-02`/`EB-03`/`GOV-02`. |
| `RISK-04` | **Observation mutates the tree.** Running a producer engine regenerates its tracked projection, so an unguarded measurement dirties the repository. Observed during this mission: subagent measurement runs modified 22 tracked files under `00-MASTER/UCOS-AEE-001/` and `00-MASTER/UCOS-RIB-001/`, which were **restored to HEAD** before certification. `UCOS-RIB-001` reports `GATE-04` + `GATE-12` FAIL on a dirty tree by design, because it measures the tree's own cleanliness. | `00-MASTER/UCOS-RFP-001` (owns the self-reference classes) | `00-MASTER/UCOS-RFP-001/rfp-declaration.json` `cycle_classes` (`CYC-OBSERVE`, `CYC-COMMIT`, `CYC-REGISTER`, `CYC-UNDECLARED`, `CYC-RECURSE`) | `UCOS-RFP-001` RFP-2 (no commit self-reference) · RFP-3 (no working-tree self-observation) · `CLO-01` fail-closed | **ADVISORY, and now measured closed at this baseline.** `cycles_detected` = **0** and `unattributed_paths` = **0** on the committed tree — `EVOLUTION-001` §6.2 `W01-F-02` recorded 22 × `CYC-OBSERVE` + 2 × `CYC-REGISTER`; all are gone. The operational discipline remains: **measure from a clean tree, and restore it afterwards.** `CLO-01` enforces this by refusing to assert a fixed point on a dirty tree. |

### C.4 What was implemented by this mission

Per the FINAL RULE, one engineering-implementable gap was found and closed. Everything else was
measured and left with its located owner.

| Gap | Disposition | Authority used |
|---|---|---|
| **No canonical Baseline Registry existed.** `BASELINE-001/CERTIFIED-BASELINE-RECORD.md` was a single record pinned at `df763bf9`, an obsolete SHA, with no register of baselines and no record of the current state. | **CREATED** `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` — append-only, two rows, every field measured and each citing its source model. `CERTIFIED-BASELINE-RECORD.md` was **not modified**. | `BASELINE-001` — the **already-located** baseline owner. No new authority, namespace, lifecycle or mechanism (`CMG-000001` XLI.5). A `BASELINE-002/` directory was deliberately **not** created: that would mint a duplicate canonical home and fail `CMG-INV-02` and `rib` `GATE-08`. |
| **The evolution contract was implemented but never composed.** All ten obligations existed with owners and gates across four instruments; no instrument stated them as one contract. | **APPENDED** §7 to `00-MASTER/EVOLUTION-001/EVOLUTION-GOVERNANCE-MODEL.md` — the ten obligations, their owners, their gates, their lifecycle steps, and the two absolute rules (R-1 baseline never modified directly, R-2 append-only), each bound to enforcement that already exists. | `EVOLUTION-001` — the located evolution owner. Composition only: no stage, gate, mechanism or authority created. A second evolution model is prohibited by `CEP-009` ADDENDUM B.11 and would fail `CMG-INV-02`. |
| Baseline protection | **MEASURED, not recreated** (Part A). | the nine mechanisms that already enforce it |
| Evolution readiness | **EXPOSED, not invented** (Part B). | Repository Truth only |

**Paths added: 2. Paths modified: 1 (by append). Paths removed: 0.** No declaration, engine, gate,
CI workflow, `Makefile` target, registry, ontology or enumeration member was altered, renumbered,
reclassified or withdrawn. No aggregate seal moved, because no check or gate binding was added.

### C.5 Determination

> ## THIS REPOSITORY IS THE CERTIFIED CONSTITUTIONAL BASELINE FOR ALL FUTURE UCOS Ω∞ EVOLUTION.
>
> Baseline ID **`UCOS-BASELINE-002`**, measured against `f25b465` on `integration/recovery-001`.
>
> The repository is **CLOSED at 100%**, is a proven **FIXED POINT** (8/8 criteria, three
> byte-identical passes of the full 13-stage pipeline from its committed state),
> **CONSTITUTIONALLY COMPLETE** (11/11), **FREEZE ELIGIBLE** (5/5 subjects, 25/25 preconditions),
> and **CERTIFIED-PROVISIONAL** with `blocking=none` across 21/21 constitutional gates and 19/19
> programmes.
>
> Zero blocking failures stand. Zero orphans, zero duplicate canonical homes, zero owner
> collisions, zero architectural cycles, zero dead engines, zero registration drift, zero
> unregistered artifacts, zero self-reference cycles.
>
> The single ceiling is `UCCEP-F-004`: constitutional finality is reserved to an authority outside
> this corpus. `VAC-01` cannot be closed by any act inside the repository, and self-ratification is
> prohibited. Every determination above is therefore **PROVISIONAL** — and that is the highest
> standing the corpus is competent to issue.
>
> All future evolution proceeds from this baseline under the contract at `EVOLUTION-001` §7. The
> baseline is immutable. Evolution is append-only. Nothing may modify the baseline directly.

---

*END — `BASELINE-001` Final Baseline Certificate · `UCOS-BASELINE-002` · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
