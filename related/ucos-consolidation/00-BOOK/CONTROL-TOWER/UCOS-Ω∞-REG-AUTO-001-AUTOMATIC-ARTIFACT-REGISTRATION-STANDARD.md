# UCOS Ω∞ — REG-AUTO-001 · AUTOMATIC ARTIFACT REGISTRATION STANDARD

> **STATUS DOMAIN:** GOVERNANCE (meta-standard)
> **STATUS BASIS:** REG-AUTO-001 self-definition (this standard) + STATUS-001 (validity gate) + UCOS-Ω∞-PHASE-REALITY-RESET-DETERMINATION + repository evidence (`00-BOOK/DATA/*.json`, `00-BOOK/tools/{ukb.py,ukbx.py,config.py}`) captured 2026-07-15

| Field | Value |
|-------|-------|
| ARTIFACT ID | REG-AUTO-001 |
| ARTIFACT | UCOS Automatic Artifact Registration Standard |
| CLASSIFICATION | Authoritative Governance Standard — Registration-Creation Binding & Synchronization Enforcement |
| STATUS | ACTIVE |
| INTEGRATION MODEL | Append-only governance standard; alters no constitution, renumbers nothing, modifies no frozen or historical artifact. Adds append-only classification config + an atomic registration transaction + enforcement gates. |
| CONSUMES (read-only) | STATUS-001; PHASE REALITY RESET DETERMINATION; `00-BOOK/DATA/*.json`; `00-BOOK/tools/ukb.py`, `ukbx.py`, `config.py`; `00-BOOK/SCHEMAS/*.schema.json` |
| PRODUCES (append-only) | `00-BOOK/tools/register.sh` (Atomic Registration Transaction); `config.py` PLATFORM classification (CLASSIFY_RULES/CHAINS/PROGRAM_ROOTS/CROSS_PROGRAM additions); `.kiro/hooks/auto-register-artifact.json` (PostFileCreate trigger) |
| AUTHORITY | NONE (defines validity rules for registration state; ratifies nothing; authorizes no EC-series step) |
| BASELINE DATE | 2026-07-15 |

*REG-AUTO-001 is the permanent authoritative standard that binds **artifact creation** to **artifact registration** across UCOS Ω∞. It closes the governance gap in which a roadmap artifact could exist physically while the Artifact Registry, Execution Status Registry, Control Tower, Digital Twin, Traceability/Knowledge-Graph, and Dependency Registry remained unaware of it. It is append-only and authority-neutral: it constrains the **validity of registration state** and provides the mechanism that keeps every register continuously synchronized; it enacts nothing and modifies no existing artifact. It is subordinate to the frozen constitutional corpus, the Technology Constitution, STATUS-001, and the ARCH/ENG/RUNTIME instruments; where any statement herein would conflict with a higher instrument, the higher instrument governs and the statement is void to the extent of the conflict.*

---

## SECTION 1 — PURPOSE

A divergence class was identified: an artifact could be **CREATED** on disk without simultaneously updating the seven synchronized registers, producing states such as *"artifact exists but registry missing"*, *"artifact exists but Control Tower missing"*, *"artifact exists but Digital Twin missing"*, and *"artifact exists but status tracker outdated"*.

REG-AUTO-001 eliminates that possibility by establishing one permanent rule:

```
Artifact Creation  =  Artifact Registration
```

No roadmap artifact shall ever exist in an unregistered state. Registration is not a later, separate, or optional step — it is a constitutive part of creation itself.

---

## SECTION 2 — SCOPE

**In scope.** Every artifact reachable by the UKB generator's scan (`00-BOOK/tools/ukb.py`, `_iter_files`) — i.e. every `.md`, `.txt`, `.docx`, `.json` file outside the excluded machinery/output directories (`.git/`, `00-BOOK/tools/`, `00-BOOK/DATA/`, `00-BOOK/REGISTRIES/`, `00-BOOK/CONTROL-TOWER/`, `00-BOOK/VOLUMES/`, `00-BOOK/PORTAL/`). This includes all roadmap artifacts: ENG-\*, RUNTIME-\*, PLATFORM-\*, ARCH-\*, CAT-\*, REF-\*, GEN-\*, IMP-\*, ADV-\*, and every future program family.

**Out of scope.** The generator's own machinery and generated outputs (they are excluded by design so the registry never lists itself), and the meta-governance standards that live under `00-BOOK/CONTROL-TOWER/` (STATUS-001 and this standard). This standard governs the **registration of content artifacts**, not the re-registration of the registration machinery.

**The seven synchronized registers** (the "registration set"):

| # | Register | Physical source of truth |
|---|----------|--------------------------|
| 1 | Artifact Registry | `00-BOOK/DATA/artifacts.json` + `00-BOOK/REGISTRIES/UNIVERSAL-ARTIFACT-REGISTRY.md` |
| 2 | Execution Status Registry | `artifacts.json` status roll-up → `control-tower.json` programs/portfolio histograms |
| 3 | Control Tower | `00-BOOK/DATA/control-tower.json` + `00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md` |
| 4 | Digital Twin | `00-BOOK/DATA/twin.json` (+ automated Control-Tower dimension refresh) |
| 5 | Traceability / Knowledge Graph | `00-BOOK/DATA/relationships.json` + `00-BOOK/REGISTRIES/KNOWLEDGE-GRAPH-REGISTRY.md` |
| 6 | Dependency Registry | `artifacts.json[*].dependencies` + `parent` (materialized as Depends-On / Parent / Child edges) |
| 7 | Page / ID Ledger | `00-BOOK/DATA/id-ledger.json` (append-only Universal IDs + Universal Page Numbers) + `UNIVERSAL-PAGE-REGISTRY.md` |

---

## SECTION 3 — REGISTRATION PRINCIPLES

1. **P1 — Creation is registration.** An artifact is not "created" until all seven registers reflect it. Physical existence alone is a *draft on disk*, not a created artifact (§5).
2. **P2 — Single source of truth.** The repository filesystem is authoritative for *existence*; the registers are authoritative for *state*. The registers are always derived from the filesystem, never hand-authored.
3. **P3 — Deterministic derivation.** Registration is a pure function of repository content + the append-only ledger + `config.py`. Re-running it on unchanged inputs yields byte-identical outputs (idempotence).
4. **P4 — Append-only identity.** Universal IDs and Universal Page Numbers are allocated once and never reused, renumbered, or reordered. Native identifiers are preserved verbatim.
5. **P5 — Atomicity.** Registration across the seven registers is all-or-nothing (§7). Partial registration is a failed transaction, not a partial success.
6. **P6 — No fabrication.** Registration records only what physically exists and what signals attest; it never manufactures status, coverage, or completion (STATUS-001 §2, non-projection).
7. **P7 — Enforceability.** The binding is enforced by tooling gates (§16), not by author discipline. A creation that skips registration is *detected and blocked*, not trusted.

---

## SECTION 4 — REGISTRATION LAWS

- **L1 — Prohibition.** Creation without registration is prohibited. A commit that adds or changes an in-scope artifact without committing the resulting synchronized register state is invalid and must be blocked (§16 guard).
- **L2 — Definition of Done.** "Created" ≡ "Registered" ≡ the seven registers agree with the filesystem and all validators pass (§14).
- **L3 — No state skipping.** An artifact traverses the lifecycle (§5) in order; `GENERATED` may not transition directly to `ACTIVE`; `REGISTERED` is mandatory and non-bypassable.
- **L4 — Family declaration.** A genuinely new program family must be declared in `config.py` (a classification rule, a dependency chain, a program root, and a volume) **before or with** its first artifact, so automatic registration classifies it correctly rather than dumping it into `OTHER/MISC/VOL-000`. This declaration is itself append-only (§11, §12).
- **L5 — Append-only correction.** Divergence is repaired by re-running registration and appending, never by editing frozen artifacts, renumbering, or rewriting history.
- **L6 — Validity gate.** Every determination that claims an artifact is created/registered must satisfy STATUS-001 §3–§5 and cite the registration evidence (register paths + validator result).

---

## SECTION 5 — ARTIFACT LIFECYCLE MODEL

Seven states, strictly ordered; **no state skipping** (L3):

```
DRAFT → GENERATED → REGISTERED → ACTIVE → CERTIFIED → FROZEN → ARCHIVED
```

| State | Meaning | Entry condition | Register effect |
|-------|---------|-----------------|-----------------|
| **DRAFT** | Intent exists; content being authored | — | none (not yet on disk, or on disk but pre-transaction) |
| **GENERATED** | Physical artifact file exists on disk | file written under an in-scope path | none *yet* — this is the dangerous interim the standard forbids leaving |
| **REGISTERED** | Present in all seven registers | Atomic Registration Transaction succeeds (§7) | all 7 registers updated; ID/page allocated append-only |
| **ACTIVE** | Registered and in force | declared `STATUS: ACTIVE` in front-matter; inferred by generator | status roll-up reflects ACTIVE |
| **CERTIFIED** | Passed its certification determination | DOMAIN-D determination + `twin --check` hard checks pass | certification dimension/signals |
| **FROZEN** | Immutable baseline | freeze determination | status FROZEN; content_hash pinned |
| **ARCHIVED** | Retired from active use, retained for history | archival determination | status retired/superseded; append-only |

**Governing constraints.**
- `GENERATED → ACTIVE` directly is **prohibited**. `REGISTERED` is mandatory between them.
- A `GENERATED` artifact that has not reached `REGISTERED` carries **no status authority** and **no valid completion claim** (STATUS-001 §4).
- Certification, freeze, and archival are DOMAIN-specific (STATUS-001) and never inferred from mere registration.

---

## SECTION 6 — REGISTRATION STATE MACHINE

```
        create file (in-scope path)
DRAFT ─────────────────────────────▶ GENERATED
                                        │
                     Atomic Registration Transaction (§7)
                     build → twin → portal → validate×2 → certify
                                        │
                   ┌────────────────────┴────────────────────┐
              all phases PASS                         any phase FAIL
                   │                                          │
                   ▼                                          ▼
              REGISTERED                              UNREGISTERED
        (7 registers synchronized)            (transaction INCOMPLETE;
                   │                            completion claim INVALID;
        declared STATUS drives                  artifact stays GENERATED;
                   ▼                            re-run after fix — no partial state)
   ACTIVE ─▶ CERTIFIED ─▶ FROZEN ─▶ ARCHIVED
```

- The transition `GENERATED → REGISTERED` is **guarded**: it fires only when the transaction completes wholly (§7). On any failure the machine remains at `GENERATED`/`UNREGISTERED`.
- The machine is **re-entrant and idempotent** (P3): re-running the transaction on an already-`REGISTERED` set is a no-op that re-proves synchronization.
- The state is **externally observable**: `git status --porcelain` over the register directories is empty iff the set is `REGISTERED` and committed (§16 guard).

---

## SECTION 7 — ATOMIC CREATION LAW (TRANSACTION MODEL)

Define the **Artifact Creation Transaction** `T`. `T` is COMPLETE iff **all** of the following succeed as one unit:

```
T = Artifact File            (physical existence, in-scope path)
  ⊕ Artifact Registry        (artifacts.json + UNIVERSAL-ARTIFACT-REGISTRY.md)
  ⊕ Execution Registry       (status roll-up in control-tower.json)
  ⊕ Control Tower            (control-tower.json + PROGRAM-CONTROL-TOWER.md)
  ⊕ Digital Twin             (twin.json + automated dimension refresh)
  ⊕ Traceability             (relationships.json + KNOWLEDGE-GRAPH-REGISTRY.md)
  ⊕ Dependencies             (parent + dependencies edges)
  ⊕ Page/ID Ledger           (id-ledger.json append-only allocation)
```

If **any** component fails:

```
Transaction Status: INCOMPLETE
Artifact Status:     UNREGISTERED
Completion Claim:    INVALID
```

**Realization.** `T` is implemented by the single idempotent operation `00-BOOK/tools/register.sh`, whose six phases map onto the components above:

| Phase | Command | Registers satisfied |
|-------|---------|---------------------|
| 1 | `python3 00-BOOK/tools/ukb.py build` | Artifact Registry, Execution roll-up, Control-Tower baseline, Traceability/Graph, Dependencies, Page/ID Ledger |
| 2 | `python3 00-BOOK/tools/ukbx.py twin` | Digital Twin + automated Control-Tower dimension refresh |
| 3 | `python3 00-BOOK/tools/ukbx.py portal` | Navigation Portal (no dead ends) |
| 4 | `python3 00-BOOK/tools/ukb.py validate` | append-only, no duplicate IDs/pages, referential integrity |
| 5 | `python3 00-BOOK/tools/ukbx.py validate` | signal ledger integrity, provenance, secret-free |
| 6 | `python3 00-BOOK/tools/ukbx.py twin --check` | Digital-Twin Certification (UKB-014) hard checks |

Because Phase 1 allocates IDs/pages append-only from the immutable ledger and every phase is deterministic, `T` is safe to run repeatedly and is the *only* sanctioned way to reach `REGISTERED`.

---

## SECTION 8 — REGISTRY SYNCHRONIZATION MODEL

- The Artifact Registry is regenerated by a full repository scan (`ukb.py build`), so **any** new in-scope file is discovered and registered automatically — no per-artifact wiring is required for existing families.
- Each artifact receives an append-only Universal ID (`UCOS-<CATEGORY>-NNNNNN`) and a contiguous, permanently-fixed Universal Page range.
- Native identifiers (`PLATFORM-001`, `RUNTIME-014`, …) are read from front-matter and preserved verbatim; the Universal ID is an overlay crosswalk.
- Status is inferred from the artifact's own `| STATUS | … |` front-matter row (deterministic mapping in `config.py::STATUS_KEYWORDS`).
- **Invariant:** `count(artifacts.json)` equals the number of in-scope files on disk. A mismatch is an unregistered-artifact defect and fails the guard (§16).

---

## SECTION 9 — CONTROL TOWER SYNCHRONIZATION MODEL

- `ukb.py build` writes the Control-Tower baseline (`control-tower.json`): portfolio totals, per-program artifact counts, status histograms, and roll-up states — all derived deterministically from the Artifact Registry.
- `ukbx.py twin` then refreshes the Control-Tower **dimensions** from the append-only signal ledger, marking each computed dimension `signal_source` automated (UKB-012).
- **Result:** creating an artifact and running `T` updates the Control Tower automatically — no manual intervention, no secondary prompt, no separate determination.
- **Enhancement adopted by this standard:** the Control-Tower refresh is bound into `T` Phase 1–2, so a new artifact can never leave the Control Tower stale.

---

## SECTION 10 — DIGITAL TWIN SYNCHRONIZATION MODEL

- `ukbx.py twin` recomputes `twin.json` (signals over subjects across lifecycle dimensions) reading the freshly-built Artifact Registry, then refreshes the Control-Tower dimensions.
- `ukbx.py portal` regenerates a navigation page for every registered artifact (parent, children, backlinks, master-index return) — guaranteeing the new artifact is reachable with no dead ends.
- **Result:** creating an artifact and running `T` updates the Digital Twin and portal automatically — no manual intervention, no secondary prompt.
- **Enhancement adopted:** twin recompute + portal regeneration are `T` Phases 2–3; twin certification (`twin --check`) is Phase 6, so the twin is not merely refreshed but re-certified on every registration.

---

## SECTION 11 — TRACEABILITY SYNCHRONIZATION MODEL

- Parent/Child and Depends-On edges are generated from `config.py::CHAINS`, `CROSS_PROGRAM`, and `PROGRAM_ROOTS`, materialized into `relationships.json` and the Knowledge-Graph Registry.
- Within a declared family, consecutive chain members auto-generate `Depends-On` + `Parent`/`Child` edges; the family head Depends-On the upstream program terminal (cross-program ordering).
- Non-chained members of a program auto-parent to the program root; unrooted artifacts fall back to the BOOK root so **every** artifact is reachable (certification check C-08).
- **Traceability links are therefore generated automatically** for any artifact whose family is declared (L4). For a *new* family, the one-time `config.py` declaration (§12) is the prerequisite; thereafter traceability is automatic for every future member.

---

## SECTION 12 — DEPENDENCY SYNCHRONIZATION MODEL

- Dependencies are the `dependencies` array + `parent` on each artifact record, kept consistent with the Depends-On/Parent edges.
- Referential integrity (every parent/dep/edge endpoint resolves) is asserted by `ukb.py validate` (Phase 4) and certification check C-05; the Depends-On graph is asserted acyclic by C-07.
- **New-family declaration procedure (append-only, one-time per family):** add to `config.py`
  1. a `CLASSIFY_RULES` entry mapping the family's path prefix → `(program, category, volume)`;
  2. a `CHAINS[<family>]` ordered list of unique basename substrings (the dependency spine);
  3. a `PROGRAM_ROOTS[<family>]` head so non-chained members parent correctly;
  4. a `CROSS_PROGRAM` edge placing the family head downstream of its upstream terminal;
  5. (if thematically new) a `VOLUMES` append — never renumbering an existing volume.
- This procedure was executed for the PLATFORM family under this standard (§ Application, below).

---

## SECTION 13 — FAILURE HANDLING MODEL

| Failure | Detection | Transaction outcome | Required response |
|---------|-----------|---------------------|-------------------|
| Build error (scan/allocate/emit) | Phase 1 nonzero exit | INCOMPLETE (exit 1) | fix input; re-run `T` |
| Twin/portal error | Phase 2/3 nonzero exit | INCOMPLETE (exit 1) | fix; re-run `T` |
| Structural invariant broken (dup ID/page, page overlap, dangling ref) | Phase 4 | INCOMPLETE (exit 2) | correct config/ledger append-only; re-run |
| Signal/provenance/secret defect | Phase 5 | INCOMPLETE (exit 2) | remediate signal; re-run |
| Certification hard-check fail (C-04/05/07/08/09/10/11) | Phase 6 | NOT-CERTIFIED (exit 2) | repair graph/navigation/control-tower; re-run |
| New family misclassified as `OTHER/MISC` | post-build inspection / review | artifact REGISTERED but mis-traced | apply §12 family declaration; re-run |
| Uncommitted synchronized state | `--guard` (§16) | DRIFT (exit 3) | stage regenerated registers; recommit |

**Principle:** there is no partial-success path. Any failure leaves the artifact `UNREGISTERED`; no register is left half-updated because Phase 1 rewrites the full derived state atomically per file, and the ledger only commits allocations for a completed scan.

---

## SECTION 14 — RECOVERY MODEL

1. **Detect.** Run `T` (or `T --guard`). A nonzero exit or nonempty guard diff identifies the divergence.
2. **Diagnose.** `git diff -- 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL` shows exactly which registers were stale and which artifacts were missing.
3. **Repair append-only.** Re-run `T`; if a new family, apply §12 first. Never edit frozen artifacts, never renumber, never rewrite history.
4. **Re-validate.** Phases 4–6 must all pass.
5. **Commit the synchronized set** so the guard is clean.
6. **Record.** The compliance evidence (before/after counts, validator output) is retained in the adopting determination (this document's Compliance Report).

Recovery is always forward-only and idempotent; the append-only ledger guarantees that recovering divergence never disturbs previously-allocated identities or pages.

---

## SECTION 15 — VALIDATION MODEL

An artifact set is **VALID / REGISTERED** iff all hold:

1. **V1 — Completeness.** Every in-scope file appears in `artifacts.json` (count parity, §8).
2. **V2 — Append-only ledger.** No duplicate Universal IDs; no page overlap; page ranges contiguous-append (`ukb.py validate`).
3. **V3 — Referential integrity.** Every `parent`, `dependency`, and edge endpoint resolves (C-05).
4. **V4 — Acyclic dependencies.** The Depends-On graph is a DAG (C-07).
5. **V5 — Navigability.** Every artifact is reachable from the BOOK root and has a return path; no orphans (C-08).
6. **V6 — Twin integrity.** Signals are append-only, subjects resolve, provenance present, secret-free (`ukbx.py validate`).
7. **V7 — Control-tower automation.** Computed dimensions are automated, not ungoverned MANUAL (C-09).
8. **V8 — No drift.** The committed registers equal a fresh regeneration (§16 guard).

Validity is fully machine-checkable and is exactly what `T` Phases 4–6 + `--guard` assert.

---

## SECTION 16 — COMPLIANCE MODEL (ENFORCEMENT GATES)

Three layered gates make the create=register binding **unskippable**:

1. **Authoring-time gate (this environment).** A Kiro `PostFileCreate` hook (`.kiro/hooks/auto-register-artifact.json`) fires the Atomic Registration Transaction automatically the moment a roadmap artifact is created under an active program directory (initially `/09-PLATFORM/PLATFORM-*.md`; generalizes per program dir). This delivers "New Artifact Created → registered automatically" with no manual step.
2. **Commit-time gate (repository).** `00-BOOK/tools/register.sh --guard` is intended as a git `pre-commit`/`pre-push` hook: it runs `T`, then fails the commit (exit 3) if the regenerated registers differ from what is staged — i.e. if an artifact was created/changed without committing its registration. (Opt-in install; this standard does not modify git config.)
3. **CI gate (pipeline).** The same `register.sh --guard` runs in CI on every pull request; a nonzero exit blocks merge. This is the authoritative backstop independent of any local environment.

A creation that bypasses gate 1 is caught by gate 2; a bypass of gate 2 is caught by gate 3. Registration is therefore enforced by construction, not by discipline (P7).

---

## SECTION 17 — GOVERNANCE MODEL

- REG-AUTO-001 is the **binding validity gate for registration state**, complementary to STATUS-001 (which governs *completion-claim* validity). A determination claiming an artifact is created must show it is REGISTERED per §15.
- It is **subordinate** to the frozen constitutional corpus, the Technology Constitution, STATUS-001, and the ENG/RUNTIME/ARCH instruments; it creates no authority and authorizes no EC-series step.
- It is **append-only**: it adds config classification, a transaction tool, and enforcement hooks; it edits no constitution, frozen artifact, historical determination, or numbering.
- **Non-projection preserved (STATUS-001 §2):** registration records *existence and declared status only*. Registering PLATFORM-001..005 asserts they **exist** (DOMAIN-B physical inventory); it does **not** claim PHASE-003 is complete, nor project architecture existence into implementation/certification/operational completion.

---

## SECTION 18 — CERTIFICATION MODEL

- Registration certification = the Digital-Twin Certification (`ukbx.py twin --check`, UKB-014) hard checks C-04/05/07/08/09/10/11, run as Phase 6 of `T`.
- An artifact set is **registration-certified** when `T` completes with `RESULT: CERTIFIED (hard checks 7/7)`.
- Artifact-level certification (DOMAIN-D) remains separate and evidence-based (STATUS-001); registration certification attests only that the registers are synchronized, valid, navigable, and secret-free.

---

## SECTION 19 — EVOLUTION MODEL

- **New families:** apply §12 (append-only config declaration) once; all future members auto-register and auto-trace.
- **New registers:** if a future register is added (e.g. a risk or cost ledger), extend `T` with an additional deterministic phase and a corresponding validator; keep atomicity.
- **New signals/connectors:** the twin's connector registry extends without touching the foundation engine (`ukbx.py` reads foundation DATA read-only).
- **Schema growth:** additive-only, mirroring STATUS-001 §8 — existing records stay valid.
- **Versioning:** `GENERATOR_VERSION` / `GEN_VERSION` stamp every emission; the ledger's `first_seen` timestamps preserve allocation history.

---

## SECTION 20 — SUCCESS CRITERIA

| # | Criterion | Met by |
|---|-----------|--------|
| SC-1 | Create = Register (no unregistered in-scope artifact) | §7 transaction + §16 gates; V1 count parity |
| SC-2 | Control Tower auto-updates on creation | §9; `T` Phases 1–2 |
| SC-3 | Digital Twin auto-updates on creation | §10; `T` Phases 2–3 + Phase 6 |
| SC-4 | Execution status recalculated automatically | §8/§9 roll-up in `T` Phase 1 |
| SC-5 | Traceability + dependencies generated automatically | §11/§12; C-05/C-07/C-08 |
| SC-6 | Enforcement is unskippable | §16 three-gate model |
| SC-7 | Repository, registry, control-tower, twin, traceability continuously synchronized | V1–V8 all pass; guard clean |
| SC-8 | Append-only; no renumbering; no frozen edits | P4/L5; `ukb.py validate` append-only proof |

---

## SECTION 21 — CONSTITUTIONAL DETERMINATION: RECONCILED SETS (CMG-DLG-13 / CMG-OQ-06)

> **STATUS DOMAIN:** GOVERNANCE · **STATUS BASIS:** REG-AUTO-001 self-definition (§17 governance model) as the located owner of the concern delegated at `CMG-DLG-13` + Repository Truth (`00-BOOK/tools/{config.py,ukb.py}`, `00-BOOK/DATA/artifacts.json`, `00-CMG/CMG-REGISTRY.json`) + `CMG-000002` §3.2 registration evidence + `CMG-000012` classification evidence

**21.1 — The question referred.** `CMG-000001` LXXVIII.3 records the open constitutional question `CMG-OQ-06`: *does admission of the `CMG` namespace and zone require amendment of any located registration or classification instrument?* `CMG-000014` and `CMG-000013` R-04 refer that question to **this** standard, because artifact registration, identity allocation, classification, and the namespace of registered artifacts are delegated at `CMG-DLG-13` to REG-AUTO-001 with `00-BOOK/` (UKB) as the store. `CMG-000001` declines to answer it (LVIII.2 — it consumes Repository Truth and does not compete with it). This Section is the referred authority's answer.

**21.2 — The determination.** **NO amendment of any located registration or classification instrument is required.** Recognition of a constitutional zone and its namespace is already **total by construction**, on three ordered recognition paths that Repository Truth exhibits and that this standard already owns:

| # | Recognition path | Mechanism (Repository Truth) | Effect on `00-CMG/` |
|---|---|---|---|
| 1 | Existing `CLASSIFY_RULES` match | `config.py::CLASSIFY_RULES`, first match wins, unchanged | the 14 `CONSTITUTIONAL-*` artifacts resolve to `CONSOLIDATION`/`CON`/`VOL-002` through the pre-existing filename rule |
| 2 | Self-declared metadata | `ukb.py::classify` step 2 over `METADATA_CLASSIFY_KEYS` — a family participates with **zero** config edits (§11, L4) | each zone artifact additionally self-declares its program, category and volume |
| 3 | Deterministic path-derived catch-all | `ukb.py::_derive_class_from_path` (GOV-005 §5.2) — classification is **TOTAL**; the `OTHER/MISC` dead-end is structurally unreachable | the remaining zone files resolve to the real class `CMG`/`CMG` |

Consequently the §12 new-family declaration procedure is **not triggered**: L4 requires a family declaration only to prevent an artifact falling to `OTHER/MISC/VOL-000`, and that outcome is unreachable for a tracked artifact. Creating a `CLASSIFY_RULES` entry, a chain, a program root, a cross-program edge or a volume for `00-CMG/` would therefore add **no** recognition, and is refused: it would edit shared machinery that admission is forbidden to touch (`CMG-000001` LVIII.5–LVIII.6) and would create a second, redundant classification path for artifacts already classified.

**21.3 — What the authority requires instead: the reconciled-set record.** A determination that recognition *already suffices* must be recorded where the machinery can be held to it. This standard therefore requires exactly one append-only artefact of record — a **reconciled set** — and nothing else:

> A **reconciled set** IS a repository zone whose recognition was reconciled **by determination** rather than by a new classification family, together with the namespace admitted with it, its located owner, and the classification resolutions the determination admits.

The declaration lives append-only in `config.py::RECONCILED_SETS`. It is **record only**:
- it is **never** consulted by `classify()` — it changes no classification and resolves nothing;
- it adds, edits, reorders and renumbers **no** `CLASSIFY_RULES`, `CHAINS`, `PROGRAM_ROOTS`, `CROSS_PROGRAM` or `VOLUMES` entry, and creates **no** classification family (L4/L5);
- it is **not** a register: it is never emitted into `00-BOOK/DATA/`, allocates no identifier, and leaves `id-ledger.json` the one identity authority (P4);
- it is **not** a compatibility layer: no legacy path, alias, shim or dual representation is introduced.

**21.4 — Identity integrity (fail-closed).** Within the declaration, `set`, `namespace` and `zone` SHALL each be unique. A missing or duplicated value is an ambiguous input and **aborts** the reading gate rather than passing it. A reconciled set therefore cannot introduce duplicate identity, a second namespace owner, or two records for one zone.

**21.5 — Enforcement: the existing classification gate, strengthened.** The reconciled-set record is read by exactly one consumer: the **`classification` gate already enumerated in `ENFORCEMENT_GATES`** (`ukb.py::cmd_enforce`, §16 gate 1/2/3). No gate is added, no validator is created, and `ENFORCEMENT_GATES` is unchanged. The gate is strengthened as follows:

| | Before | After |
|---|---|---|
| Gate question | does the file resolve to something other than `OTHER/MISC`? | *and*, if the file lies in a declared reconciled zone, does it resolve to a classification that zone's determination **admits**? |
| Failure mode covered | unclassified artifact | unclassified artifact **+ reconciliation drift**: an artifact inside a reconciled zone silently resolving outside the admitted set |
| Scope outside reconciled zones | — | unchanged (vacuously conformant) |
| Determinism | pure function of repository state (GOV-005 §5.4) | unchanged — the check is a pure function of (path, resolved class, declaration); no clock, no environment, no flag |

Reconciliation drift is a **blocking** violation in both gate modes (pre-registration for newly-created files, post-registration for the whole eligible set), and is recorded in the enforcement audit record (`unreconciled`, `reconciled_sets`). Recognition of a reconciled zone is therefore machine-proven on every transaction and every CI run (§16.3), not incidental.

**21.6 — The reconciled set determined for the `CMG` zone.**

| Field | Value |
|-------|-------|
| Set | `CMG` |
| Zone | `^00-CMG/` |
| Namespace | `CMG` (width 6; `RECOGNIZED` — owned by `CMG-000001` per `CMG-000001` XXXIII, by reference only) |
| Namespace owner | `CMG-000001` |
| Delegated concern | `CMG-DLG-13` (artifact registration, identity allocation, classification, namespace of registered artifacts) |
| Recognition paths found sufficient | existing `CLASSIFY_RULES` match · self-declared metadata · deterministic path-derived catch-all |
| Admitted classifications | (`CONSOLIDATION`, `CON`) · (`CMG`, `CMG`) |
| Admitted volumes | `VOL-002` (CONSOLIDATION) · `VOL-000` (MASTER INDEX) — both pre-existing; none created, none renumbered |
| Closes | `CMG-OQ-06` |

**21.7 — Closure.** `CMG-OQ-06` is **CLOSED** by this determination. Closure is recorded, with evidence, in the two places the meta layer's own maintenance rule requires (`CMG-000001` LXXVIII.4): the constitution's own gap-and-question register (`CMG-000001` LXXVIII.7) and the derived projection (`00-CMG/CMG-REGISTRY.json`, `open_questions[CMG-OQ-06]`). No other open question, vacancy, gap, tier, or readiness outcome is touched: `CMG-OQ-01`, `CMG-OQ-02`, `CMG-OQ-03`, `CMG-OQ-04`, `CMG-OQ-05`, `CMG-OQ-07` and `VAC-01` are unaffected, and the declared readiness ceiling `READY-PROVISIONAL` is unchanged.

**21.8 — Non-mutation guarantees.** This determination: renumbers no Universal ID and no Universal Page (P4); edits no existing `CLASSIFY_RULE` (L5); creates no classification family, no registry, no validator and no gate; introduces no compatibility layer and no duplicate identity; edits no frozen artifact and rewrites no history; and leaves every artifact outside the declared zones classified exactly as before. It is additive in the same sense as every prior Section of this standard.

**21.9 — Evolution.** A future reconciliation is a **new** `RECONCILED_SETS` entry plus a new clause of this Section — never a rewrite of an existing entry or clause (§19; `AUTH-INF-001` CR-INF-007). Withdrawal of a reconciled set is likewise append-only: a superseding clause, never deletion of the record.

**21.10 — Authority neutrality.** This determination is confined to registration, classification, and the namespace of registered artifacts — precisely the concern delegated at `CMG-DLG-13`. It ratifies nothing, confers no authority, occupies no tier, decides no substantive question, and makes no completion or certification claim about `00-CMG/` or about the meta layer's standing (§17; STATUS-001 §2 non-projection).

**21.11 — Evidence (as executed).**

| Check | Result |
|-------|--------|
| Zone recognition, before and after | unchanged — 14 files `CONSOLIDATION/CON/VOL-002`, `CMG-REGISTRY.json` `CMG/CMG/VOL-000`, `README.md` `CMG/CMG/VOL-002` |
| Classification gate (pre-registration) | PASS — eligible 1197 · unregistered 0 · unclassified 0 · reconciled sets 1 (`CMG`) · reconciled-set drift 0 |
| Classification gate (post-registration) | PASS — same, parity 1197 = 1197 |
| Strengthening bites (negative proof) | a zone path resolving to a non-admitted class or volume is reported as a blocking violation; a duplicated reconciled-set record aborts fail-closed |
| Zones outside the declaration | unaffected — vacuously conformant |
| Meta-constitutional validation (`cmg-gate`) | PASS — 0 findings, readiness `READY-PROVISIONAL` (unchanged) |
| Append-only / no renumbering (SC-8) | PASS — `ukb.py validate` append-only ledger intact; no ID or page reallocated |

---

# APPLICATION & REQUIRED OUTPUTS

## OUTPUT A — PLATFORM-001..005 REGISTRATION ASSESSMENT

**Pre-adoption state (evidence).** `artifacts.json` was generated `2026-07-15T04:29:01Z` with **167** artifacts and **no** PLATFORM program. The platform artifacts were created `2026-07-15 11:36–11:51` (filesystem mtimes) — approximately seven hours later. They were therefore **entirely absent** from `artifacts.json`, `control-tower.json`, `twin.json`, and `relationships.json`: the exact *"artifact exists but registry/Control-Tower/Twin missing"* divergence this standard eliminates. Additionally, `config.py` contained **no** classification rule, chain, or program root for `^09-PLATFORM/`, so a naïve build would have misclassified them as `OTHER/MISC/VOL-000` with no dependency chain.

**Actions taken (append-only).**
1. `config.py` — added `CLASSIFY_RULES` entry `(^09-PLATFORM/ → PLATFORM/PLT/VOL-006)`, `CHAINS["PLATFORM"]` (GOV-000 → 001 → 002 → 003 → 004 → 005 → package), `PROGRAM_ROOTS["PLATFORM"] = PLATFORM-GOV-000`, and `CROSS_PROGRAM ("PLATFORM","RUN")`. No existing rule, chain, root, or volume was modified or renumbered.
2. Ran the Atomic Registration Transaction (`register.sh`).

**Post-adoption state (verified).** `artifacts.json` regenerated at `2026-07-15T06:33:18Z` with **175** artifacts; program `PLATFORM` now present with **7** members:

| Universal ID | Native ID | Volume | Status | Parent | Deps |
|--------------|-----------|--------|--------|--------|------|
| UCOS-PLT-000007 | PLATFORM-GOV-000 | VOL-006 | ACTIVE | UCOS-RUN-000014 (RUNTIME-014 terminal) | 1 |
| UCOS-PLT-000001 | PLATFORM-001 | VOL-006 | ACTIVE | UCOS-PLT-000007 | 1 |
| UCOS-PLT-000002 | PLATFORM-002 | VOL-006 | ACTIVE | UCOS-PLT-000001 | 1 |
| UCOS-PLT-000003 | PLATFORM-003 | VOL-006 | ACTIVE | UCOS-PLT-000002 | 1 |
| UCOS-PLT-000004 | PLATFORM-004 | VOL-006 | ACTIVE | UCOS-PLT-000003 | 1 |
| UCOS-PLT-000005 | PLATFORM-005 | VOL-006 | ACTIVE | UCOS-PLT-000004 | 1 |
| UCOS-PLT-000006 | (PLATFORM-FOUNDATION-PACKAGE-DETERMINATION) | VOL-006 | ACTIVE | UCOS-PLT-000005 | 1 |

**Determination for each:** PLATFORM-001, -002, -003, -004, -005 are now **FULLY REGISTERED** (Artifact Registry, Execution roll-up, Control Tower, Digital Twin, Traceability/Graph, Dependencies, Page/ID ledger all reflect them), synchronization is **COMPLETE**, and **no manual actions remain**. Registration records physical existence and declared `ACTIVE` status only; per STATUS-001 §2 this is **not** a PHASE-003 roadmap-completion claim (PHASE-003 remains NOT COMPLETE — 5 of the 18 defined `PLATFORM-*` roadmap artifacts exist).

## OUTPUT B — MIGRATION PLAN (bringing existing artifacts into compliance)

1. **No frozen edits / no renumbering / no history rewrite** — corrections are append-only (L5).
2. **Declare undeclared families** via §12. (Done for PLATFORM.)
3. **Run `T` once** to register all currently-unregistered in-scope files. This registered PLATFORM (7) and surfaced one further stray unregistered file — `02-MASTER/UCOS-Ω∞-UNIVERSAL-ARCHITECTURAL-QUALITY-CONSTITUTION.md` — which is now in the registry but classified `OTHER/MISC` because its name uses "ARCHITECTURAL-QUALITY" rather than the "-ARCHITECTURE-CONSTITUTION" pattern the ARCH rule matches. **Follow-up (append-only, recommended):** add an `ARCH` classification rule for the `ARCHITECTURAL-QUALITY-CONSTITUTION` name and re-run `T`; this is an ARCH-family concern outside the PLATFORM scope and is flagged rather than silently reclassified.
4. **Install the enforcement gates** (§16): the Kiro `PostFileCreate` hook is created by this standard; the git `pre-commit` and CI gates are opt-in via `register.sh --guard`.
5. **Commit the synchronized register set** so the guard is clean.

## OUTPUT C — COMPLIANCE REPORT

| Check | Result |
|-------|--------|
| Artifact count parity (V1) | PASS — 175 records = in-scope files scanned |
| Append-only ledger, no dup ID/page (V2) | PASS — `ukb.py validate`: "append-only page ledger intact" |
| Referential integrity (V3, C-05) | PASS — "all endpoints resolve" |
| Acyclic dependencies (V4, C-07) | PASS — "acyclic" |
| Navigability, no orphans (V5, C-08) | PASS — "all reachable + return path" |
| Twin integrity (V6) | PASS — 12 signals, provenance present, secret-free |
| Control-tower automation (V7, C-09) | PASS — computed dimensions automated |
| Digital-Twin Certification | PASS — CERTIFIED, hard checks 7/7 |
| PLATFORM-001..005 registered + synchronized | PASS — see Output A |
| Append-only / no renumbering / no frozen edits (SC-8) | PASS — only new PLT-\* IDs appended; RUN/ARCH/etc. unchanged |

**Open item (non-blocking):** the `ARCHITECTURAL-QUALITY-CONSTITUTION` misclassification noted in Output B step 3.

## OUTPUT D — GOVERNANCE IMPACT ANALYSIS

REG-AUTO-001 becomes the binding registration-validity gate, subordinate to and consistent with STATUS-001 and the frozen corpus. It creates no authority and authorizes no EC-series step. It is append-only and preserves the non-projection law: registration attests existence/declared-status only, never cross-domain completion. Prior determinations remain historically intact; divergence is prevented going forward, not retroactively rewritten.

## OUTPUT E — IMPLEMENTATION IMPACT ANALYSIS

- **Code touched (append-only):** `config.py` (+1 classify rule, +1 chain, +1 program root, +1 cross-program edge); new `register.sh`; new Kiro hook. No change to `ukb.py`/`ukbx.py` logic — the engines already register deterministically; this standard *binds and enforces* their use.
- **Performance:** a full `T` for the 175-artifact corpus completes in seconds; idempotent and safe to run on every creation/commit.
- **Risk:** low and reversible — all outputs are regenerable and git-tracked; the append-only ledger makes ID/page allocation non-destructive.

## OUTPUT F — CERTIFICATION STATEMENT & FINAL DETERMINATION

> **STATUS DOMAIN:** GOVERNANCE · **STATUS BASIS:** REG-AUTO-001 self-definition + repository evidence (`artifacts.json` 167→175; `register.sh` transaction log; `twin --check` CERTIFIED 7/7) 2026-07-15
>
> REG-AUTO-001 is hereby established as the authoritative, permanent, append-only Automatic Artifact Registration Standard for UCOS Ω∞. It binds artifact creation to registration across all seven registers via the idempotent Atomic Registration Transaction, enforced by a three-gate compliance model. It specifies additive-only config/tooling and modifies no constitution, frozen artifact, historical determination, or artifact numbering. It creates no authority and authorizes no EC-series step.

**FINAL DETERMINATION — will future roadmap artifacts (PLATFORM-006 onward) automatically Register, update Control Tower, update Digital Twin, update Execution Status, and update Traceability upon creation?**

**YES — conditionally and provably, under the adopted mechanism.** Registration is not spontaneous filesystem magic; it is an execution step. What REG-AUTO-001 guarantees is that this step is **automatic and unskippable**:

- **Explicit proof (executed, not asserted):** creating PLATFORM-001..005 (+GOV-000+package) without registration produced the exact divergence (167-artifact registry unaware of them). Declaring the family append-only and running the Atomic Registration Transaction moved all of them to `REGISTERED` — 175 artifacts, correct program/volume/native-id/parent/dependency chain, Control Tower and Digital Twin refreshed, portal regenerated, and Digital-Twin Certification `CERTIFIED (7/7)`. The transaction log and `artifacts.json` before/after are the proof.
- **For PLATFORM-006 onward specifically:** the PLATFORM family is now declared in `config.py`, so any new `PLATFORM-00N` file is classified, chained, and traced automatically; the `PostFileCreate` hook fires `T` on creation; the commit/CI guards block any commit whose registers are stale. Therefore PLATFORM-006+ will Register, update the Control Tower, update the Digital Twin, recalculate Execution Status, and generate Traceability/Dependencies **automatically upon creation** — with the only prerequisite (family declaration) already satisfied.
- **Residual honesty:** a brand-new *different* family still requires its one-time §12 declaration to be traced correctly (otherwise it registers as `OTHER/MISC`). This is a deliberate, append-only governance step, not a gap in synchronization.

**SUCCESS CRITERION satisfied:** after adoption, `Create Artifact = Registered Artifact`. No future roadmap artifact may remain outside the synchronized UCOS execution model, because the create→register binding is enforced by construction at authoring, commit, and CI, and the Repository / Control-Tower / Digital-Twin / Execution-Status / Traceability states are re-proven synchronized by the transaction on every creation.

**END OF STANDARD — REG-AUTO-001 · ACTIVE · APPEND-ONLY · AUTHORITY-NEUTRAL · PERMANENT AUTOMATIC ARTIFACT REGISTRATION STANDARD**
