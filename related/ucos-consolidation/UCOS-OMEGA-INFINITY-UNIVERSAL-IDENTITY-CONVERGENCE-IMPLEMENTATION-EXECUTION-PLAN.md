# UCOS Ω∞ · UNIVERSAL IDENTITY CONVERGENCE IMPLEMENTATION EXECUTION PLAN

| Field | Value |
|---|---|
| ARTIFACT | UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-CONVERGENCE-IMPLEMENTATION-EXECUTION-PLAN |
| CLASS | EXECUTION PLAN — plan of record |
| VERSION | 1.0 |
| SOLE INPUT | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-CONVERGENCE-CLOSURE-DETERMINATION.md` (resolved) |
| SCOPE | Execution of owner-action dependencies R1…R4; preservation of permanent residuals R5…R6 |
| DOWNSTREAM CONSUMER | **G-3 Relationship Deterministic Identity Closure** — consumes Wave W1, W3 and W5 outputs via the handoff contract in PART 6 |
| AUTHORITY | **NONE.** This plan mints no identity, allocates no identifier, declares no namespace, defines no grammar, opens no registry, legislates no lifecycle and certifies nothing. It sequences actions that only their located owners may perform. |
| LAW OWNERS | AIF (`02-MASTER/…ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md`) · AUTH-INF-001 (`00-BOOK/CONTROL-TOWER/…-CONSTITUTION.md`) |
| ARCHITECTURE OWNER | ENG-001 (`07-ENGINEERING/UCOS-Ω∞-UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE.md`) |
| CONFORMANCE OWNER | UIS-001 (`00-MASTER/UIS-001/`) |
| SEAL | NOT SEALED — hand-authored plan, not engine-generated. No digest is asserted. |
| IMPLEMENTATION | NONE. No code, data, schema, ledger, registry or relationship record was created or modified by this artifact. |

> **DISCLOSURE.** This plan introduces **no mechanism**. Every action it sequences uses a function that already exists at the path cited, and every action is performed by the instrument's own located owner. It opens no identity system, ledger, registry, namespace or resolver; it defines no migration table and no compatibility layer; it authorizes no shortcut. Its only inputs are the resolved Convergence Closure Determination and the mechanisms that determination located. Where this plan and a located instrument differ, **the located instrument governs**.

---

# PART 0 — EXECUTION MODEL

## 0.1 What is being executed

The Closure Determination resolved J1…J8 as **two dissolved, five converged, one closed, zero repaired**, leaving four owner-action dependencies and two permanent residuals. This plan executes exactly those four and protects the two.

| Item | Determination disposition | Execution status here |
|---|---|---|
| R1 | Declare four unlocated cells; register their code spaces | **Wave W1** |
| R2 | Admit a durable-identity map inside `00-BOOK/DATA/id-ledger.json` and chain it | **Wave W3** |
| R3 | Version the artifact-plane grammar by profile id, current pattern preserved verbatim | **Wave W2-A** |
| R4 | Register the three canonicalization epochs; tag forward digests as multihashes | **Wave W2-B** |
| R5 | `identities_unresolvable ≤ 6`, `namespace_partition_ambiguities ≤ 17` | **PROTECTED — no wave may reduce these** |
| R6 | Nine schema-declared prefixes with zero members | **PROTECTED — declared RESERVED, must fail non-vacuity** |
| J7 | Registration replay tier | **Wave W4** (consequence of R2) |
| J8 | UIL-11 `measurable: true` | **Wave W4** (consequence of R1) |

## 0.2 The one architectural rule that governs every wave

**Invariant CP-1 (from the Determination): no step of the Convergence Protocol has write access to an existing recorded identity value.**

Every wave in this plan is therefore constructed so that its write set is one of exactly three kinds:

```
KIND-D  DECLARATION WRITE   append to declaration data      fully reversible by revert
KIND-A  ADOPTION WRITE      a new record naming an existing  reversible ONLY before commit
                            value, frozen verbatim
KIND-M  MINT-FORWARD WRITE  a new member                     reversible ONLY before commit
```

There is no fourth kind. A proposed action whose write set is not KIND-D, KIND-A or KIND-M is **out of scope of this plan and prohibited by the Determination.**

## 0.3 The rollback boundary is the prepare/commit seam, and it is enforced by code

Rollback is not a process commitment in this plan; it is a property of the located mechanism.

- `IdentityRegistry.prepare()` produces a provisional mint. Provisional mints "are not Recorded Truth and never persist" (`export()` exports only sealed identities).
- `IdentityRegistry.abort()` discards a provisional mint, and "aborting an unknown/never-prepared mint is a harmless no-op (idempotent)".
- `IdentityRegistry.abort()` **refuses** a sealed identity: `"cannot abort an already-sealed identity (forward-only)"`.

Therefore:

```
        ┌──────────── REVERSIBLE ────────────┐┌──────── IRREVERSIBLE ────────┐
   DECLARE  →  PREPARE  →  VERIFY  →  GATE  →│  COMMIT  →  MEASURE  →  CERTIFY
        └── revert / abort ──────────────────┘└── forward-only compensation ──┘
                                             ▲
                                   THE ROLLBACK BOUNDARY
```

**Rule EX-1.** Every wave places all of its verification *before* its commit. A wave whose gates run after commit has no rollback and is malformed.

**Rule EX-2.** Post-boundary correction is a **new event** — never an edit, never a deletion, never a renumber (AIF-L17). The located forms are: a `history` append, a widened `DigestSet`, a new certification ledger entry, a `retire()` mark. Nothing else.

## 0.4 Wave dependency graph

Derived from Determination G-2 ("the sequencing is forced"). W2-A and W2-B depend on nothing and may run concurrently with W1.

```
        W0  BASELINE SEAL  (read-only; establishes the rollback anchor)
              │
       ┌──────┼───────────────┬───────────────┐
       │      │               │               │
      W1     W2-A            W2-B             │
   cells   grammar        canonicalization    │
   (R1)    profile (R3)   epochs (R4)         │
       │      │               │               │
       └──────┴───────┬───────┘               │
                      │                       │
                     W3  DURABLE MAP (R2)  ◄──┘   ← the only wave crossing the boundary
                      │
                     W4  REPLAY TIER + MEASUREMENT CLOSURE (J7, J8)
                      │
                     W5  CERTIFICATION (AIF-L21 duality)
                      │
                     G-3  RELATIONSHIP DETERMINISTIC IDENTITY CLOSURE  (consumes PART 6)
```

**Hard ordering constraints (each with its reason):**

| Constraint | Reason |
|---|---|
| W1 ≺ W3 | A ledger map cannot be admitted for cells that are not declared. Declaring the cell is what names the authority the map records. |
| W3 ≺ W4 | There is nothing to replay until durable identity is recorded. A replay gate over an empty population must **FAIL** (non-vacuity), so gating before W3 would be a false red. |
| W1 ≺ W4 | UIL-11 `measurable: true` is valid only once authorities exist as a declared population. |
| W3 ≺ W5 | Historical attestation attests an adoption event; the event must exist. |
| W2-A ⊥ W2-B ⊥ W1 | Independent. Grammar profiles, canonicalization epochs and cell declarations touch disjoint declaration registers. |
| W5 ≺ G-3 | G-3 consumes a certified cell, not a proposed one. |

---

# PART 1 — WAVE W0 · BASELINE SEAL

**Purpose.** Establish the rollback anchor and prove the gate matrix is green *before* any convergence write, so that any later red is attributable.

**Write set.** KIND-D only, and only inside the plan's own operational home. **No identity file, ledger, schema or relationship record is read-write in this wave.**

| Field | Value |
|---|---|
| Authority | none required — read-only observation |
| Owner | executor |
| Depends on | — |
| Rollback | trivial: nothing is written outside the operational home |

## W0.1 Files

| File | Access | Note |
|---|---|---|
| `00-BOOK/DATA/id-ledger.json` | **READ ONLY** | digest recorded as the anchor |
| `00-BOOK/DATA/relationships.json` | **READ ONLY** | digest recorded; 13 361 edges is the adoption inventory G-3 will consume |
| `00-BOOK/DATA/artifacts.json` · `change-ledger.json` | **READ ONLY** | digests recorded |
| `00-BOOK/SCHEMAS/artifact.schema.json` · `relationship.schema.json` | **READ ONLY** | digests recorded |
| `00-MASTER/UIS-001/uis-declaration.json` | **READ ONLY** | digest recorded |

## W0.2 Verification gates (all must pass before any wave proceeds)

| Gate | Exact command | Expected |
|---|---|---|
| G0-1 identity self-guards (nine, each fail-closed) | `make uis-self` | exit 0 |
| G0-2 identity conformance | `make uis-gate` | exit 0 (gate OPEN) |
| G0-3 identity register replay | `make uis-replay` | exit 0, "no drift" |
| G0-4 registry structural + schema | `python3 00-BOOK/tools/ukb.py validate` | exit 0 |
| G0-5 registration parity (read-only) | `bash 00-BOOK/tools/register.sh --observe` | exit 0 |
| G0-6 canonical-primitive non-duplication | `python3 -m engine.uckp.cli validate` | exit 0 |
| G0-7 test suite | `pytest engine/tests platform/tests intelligence/tests -q` | exit 0 |
| G0-8 build determinism | `python3 -m engine.determinism.reproduce BP-DATA-0001 --evidence-dir determinism-evidence` | exit 0 |
| G0-9 evolution-surface replay | `python3 -m engine.uaue.gate --replay --quiet` | exit 0 |

## W0.3 Exit criteria

- All nine gates exit 0.
- The seven protected digests are recorded as the anchor set.
- **R5 baseline recorded**: `identities_unresolvable = 6`, `namespace_partition_ambiguities = 17`. These are the values every later wave must reproduce **exactly** — not improve.

**W0 FAIL disposition.** A red gate at W0 is a pre-existing condition, not a convergence defect. Convergence does not start until W0 is green, and W0 may not be made green by touching identity data.

---

# PART 2 — WAVE W1 · CELL DECLARATION (R1)

**Purpose.** Close J4 (duplicate/hidden authorities) and unblock J8. Four minting sites become located cells; three code spaces are registered. **No identifier changes value. No module is removed.**

| Field | Value |
|---|---|
| Closes | R1 → J4; enables J8 (W4) |
| Write kinds | KIND-D only |
| Rollback | **fully reversible** — revert the declaration append and the `register_kind` calls; nothing is minted, nothing is sealed |
| Boundary | entirely **pre**-boundary |

## W1.1 The four cells to declare

Each is an append to `identity_mechanisms[]` in the UIS-001 declaration, in the located record shape (`id`, `name`, `plane`, `owner`, `module`, `symbol`, `grammar_owner`, `grammar_symbol`, `keyed_by`, `note`).

| Cell | Plane | Module (unchanged) | Render (unchanged) | Code space to register |
|---|---|---|---|---|
| UMK kernel identity | P4 | `engine/kernel/identity.py` | `UMK-<SLUG>-<12h>` | none — own prefix |
| UAPF pipeline identity | P4 | `platform/universal_pipeline/identity.py` | `UAPF-<KIND>-<20h>` | none — own prefix |
| Intelligence artifact identity | P4 | `intelligence/kernel/ids.py` | `UCOS-<CODE>-<12h>` | **`RSRC RCLM RFND RCTR RSCH RSTD PUB PFMT PSEC CITE`** |
| Platform principal identity | P4 | `platform/foundation/identity.py` | `UCOS-PRIN-<16h>` | **`PRIN`** |
| Control-plane derived identity | P4 | `platform/universal_control_plane/{intelligence,prompt,ontology}.py` | `MET-`/`PRG-`/`PRM-<12h>` | **`MET PRG PRM`** |

## W1.2 Files and authorities

| File | Change | Kind | Authority that must act |
|---|---|---|---|
| `00-MASTER/UIS-001/uis-declaration.json` | append 5 entries to `identity_mechanisms[]` | KIND-D | UIS-001 (its own operational home; permitted) |
| `engine/registry/universal/identity.py` | **no edit.** `register_kind()` is *called* by each owner at import; the code-space table is `_EXTENSION_KIND_CODES`, which is data | KIND-D | registry owner (UMB-005) |
| `intelligence/kernel/ids.py` | delegate line 119 `hashlib.sha256(canonical_json(...))` → `content_hash(...)`; register 10 codes | KIND-D | `intelligence/` owner |
| `platform/foundation/identity.py` | register `PRIN` | KIND-D | `platform/foundation/` owner |
| `platform/universal_control_plane/{intelligence,prompt,ontology}.py` | register `MET`, `PRG`, `PRM` | KIND-D | control-plane owner |
| `engine/kernel/identity.py` · `platform/universal_pipeline/identity.py` | **no edit** — declaration only | KIND-D | UIS-001 |
| `engine/uicm/validation.py` `_FORBIDDEN_MINTS` | widen probe scope repository-wide with a **measured** exemption list | KIND-D | UICM owner |

**Write-scope note.** `engine/` and `intelligence/` are inside UIS-001's `forbidden_write_prefixes`, which is why the third, sixth and seventh rows are the package owners' actions and not UIS-001's. This separation is the reason R1 is an owner-action dependency rather than a task.

## W1.3 Constraints

| Constraint | Enforcement |
|---|---|
| No code is renamed | `register_kind` refuses to re-code an existing kind and refuses code reuse |
| No identifier changes value | The wave writes no identifier at all |
| No new authority | The five cells are *located*, not created; each already mints today |
| No sixth plane | All five are P4; AIF-L03 closes the plane set at five |
| `PRIN` and the 10 intelligence codes become parseable | `parse_kind_name` becomes total over them once registered — the defect closes without touching a stored value |

## W1.4 Verification gates

| Gate | Exact command | Proves |
|---|---|---|
| G1-1 | `make uis-self` | nine self-guards still fail-closed, incl. `--check-no-enumeration` (the engine still names no population) |
| G1-2 | `make uis-gate` | `UIS-V-05` exactly one plane per mechanism · `UIS-V-06` module + grammar symbol resolve · `UIS-V-07` no unrealized plane |
| G1-3 | `make uis-replay` | committed registers are the product of the declaration; zero drift |
| G1-4 | `python3 -m engine.uckp.cli validate` | `UCKP-INV-03` zero duplication — the `intelligence` inline digest fork is gone |
| G1-5 | `pytest engine/tests platform/tests intelligence/tests -q` | no regression in any located identity module |
| G1-6 | `python3 00-BOOK/tools/ukb.py validate` | artifact plane untouched |
| G1-7 | digest diff vs W0 anchor for all seven protected files | **byte-identical** — W1 touches no recorded truth |
| G1-8 | `make uis-gate` R5 readings | `identities_unresolvable == 6` **and** `namespace_partition_ambiguities == 17`, unchanged |

## W1.5 Rollback

Revert the declaration append and the owner-side `register_kind` calls. Nothing was prepared, nothing was sealed, no identifier existed before that does not exist after. **W1 is idempotent and fully reversible.**

---

# PART 3 — WAVE W2 · PARAMETER EPOCH DECLARATION (R3, R4)

Two independent tracks. Both are entirely pre-boundary, both KIND-D, both fully reversible.

## W2-A · Artifact-plane grammar profile (R3)

**Purpose.** Dissolve J5. The grammar governs a P3 **render**, and CR-INF-002.4 already declares its padding width "a formatting convenience for sort-stability, **not** a ceiling… extended append-only… **without renumbering prior members**." This wave makes "the pattern in force when this identifier was minted" answerable.

| Field | Value |
|---|---|
| Authority | `00-BOOK/SCHEMAS/` schema owner + UMB-004 nomenclature owner |
| Depends on | — |
| Rollback | fully reversible |

**Files**

| File | Change | Kind |
|---|---|---|
| `00-BOOK/SCHEMAS/artifact.schema.json` | the current pattern `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` is **preserved verbatim** and bound to a Genesis-epoch `profile_id` | KIND-D |
| `00-BOOK/MASTER-BOOK/UMB-004-NOMENCLATURE-ARCHITECTURE.md` | append-only amendment recording that width is a pinned parameter with a measured trigger | KIND-D |
| `00-MASTER/UIS-001/uis-declaration.json` | `grammar_source` gains the profile id alongside the existing `pointer` | KIND-D |

**Prohibitions specific to W2-A**

- The pattern **must not be loosened**. Loosening admits identifiers the Genesis epoch never allowed and makes `UIL-19` (`identities_failing_declared_grammar == 0`) meaningless retroactively.
- The pattern **must not be replaced**. It is dated, not superseded in place.
- No identifier is re-rendered. Width extension, if ever triggered, mints wider values forward only.

**Gates**

| Gate | Command | Proves |
|---|---|---|
| G2A-1 | `make uis-gate` | grammar still resolves **by pointer** (`uis_engine.py:256-262`); `FailClosed` not raised |
| G2A-2 | `make uis-self` | `uis_engine.py` still contains no grammar literal (its own self-check at ~line 1621) |
| G2A-3 | `python3 00-BOOK/tools/ukb.py validate` | every one of the recorded artifacts still validates against the schema |
| G2A-4 | `make uis-gate` UIL-19 | `identities_failing_declared_grammar == 0` |
| G2A-5 | `make uis-gate` capacity dimension | headroom reported against `capacity_threshold_fraction = 0.5`; a namespace crossing it is a **declared trigger**, not a failure |
| G2A-6 | digest diff vs W0 anchor | `id-ledger.json`, `relationships.json`, `artifacts.json`, `change-ledger.json` **byte-identical** |

## W2-B · Canonicalization epochs (R4)

**Purpose.** Close J2/J3. The three located canonicalization profiles are **registered, not unified** — unifying them would change historical digests, i.e. rewrite Recorded Truth.

| Field | Value |
|---|---|
| Authority | Layer Zero owner (`engine/uckp/`) + each `00-MASTER` engine owner + `platform/foundation/` owner |
| Depends on | — |
| Rollback | fully reversible |

**The three epochs to register** (as `CanonicalProfile` entries; `ProfileRegistry.register` already refuses to overwrite an existing `profile_id` with different parameters)

| Epoch | Parameters as they exist today | Producing sites |
|---|---|---|
| Genesis-compact | `sort_keys=True`, `separators=(",",":")`, `ensure_ascii=False` | `engine/uckp/canonical.py` (`ucos-uckp-canonical-json/1.0.0`) — the pinned default |
| Genesis-pretty | `indent=2`, `sort_keys=True`, `ensure_ascii=False`, trailing `"\n"` | ~9 `00-MASTER` engines (`rib_engine.py:264`, `uccep_engine.py:176`, `ucda_engine.py:164`, `ucef_engine.py:253`, `aee_engine.py:143`, `uei_engine.py:165`, `uer_engine.py:145`, `urrc_engine.py:192`, `rfp_engine.py:88`) |
| Genesis-loose | `sort_keys=True` only; default separators; `ensure_ascii=True` | ~13 UAKOS phase engines (`phase2_recon.py:465`, `phase3_engine.py:570`, `phase4_plan.py:608`, `phase5_gov.py:502`, `cert_engine.py:448`, `final_closure_engine.py:465`, …) |

**Forward digest tagging.** New digests are emitted as `DigestSet{profile_id, [Multihash{algorithm, value}]}` / `CanonicalDigest{profile_id, algorithm, value, byte_length}`. Algorithm additions go through `AlgorithmRegistry.rollover(name, strength, witness=…)`, which refuses an unnamed witness; `deprecate()` refuses to leave zero active.

**Prohibitions specific to W2-B**

- **No bulk re-hash.** The ~5 900 existing bare-hex values are read under their registered epoch. Re-hashing is rewriting Recorded Truth.
- **No field renaming.** Renaming `content_hash` → a profile-specific name across ~3 905 occurrences is a compatibility layer. The *record* carries `profile_id`; the field name does not need to.
- **No profile mutation.** An epoch is succeeded, never edited — guaranteed by `ProfileRegistry.register`.

**Gates**

| Gate | Command | Proves |
|---|---|---|
| G2B-1 | `python3 -m engine.uckp.cli validate` | `UCKP-INV-03` — exactly one canonical primitive; every module forwards rather than implements |
| G2B-2 | `pytest platform/tests/test_crypto_agility.py engine/tests -q` | multihash tag round-trip; witnessed rollover; deprecate refuses last-active |
| G2B-3 | `python3 -m engine.determinism.reproduce BP-DATA-0001 --evidence-dir determinism-evidence` | byte-identical double build; a file-less category still forced to non-identical |
| G2B-4 | `python3 -m engine.uaue.gate --replay --quiet` | `replay_drift` byte comparison unchanged |
| G2B-5 | digest diff vs W0 anchor | all seven protected files **byte-identical** — no historical digest moved |

---

# PART 4 — WAVE W3 · DURABLE-IDENTITY MAP ADMISSION (R2)

**This is the only wave that crosses the rollback boundary.** It is also the only wave that writes Recorded Truth. It is designed so that everything reversible happens first and the commit is the last action.

| Field | Value |
|---|---|
| Closes | R2 → J6; supplies the substrate for J1/G-3 and J7 |
| Authority | **UMB-003 identity-architecture owner** (`00-BOOK/MASTER-BOOK/UMB-003-IDENTITY-ARCHITECTURE.md`) |
| Depends on | W0 green · W1 complete (cells declared) |
| Write kinds | KIND-D (schema/defaults), then KIND-A (adoption), then KIND-M (mint-forward) |
| Rollback | **pre-commit: `abort()`, idempotent. post-commit: forward-only compensation only.** |

## W4.0 Why this is not a new ledger

The located precedent is explicit. `load_ledger()` (`00-BOOK/tools/ukb.py:867-873`) documents `by_execution` as:

> "an append-only map of execution KEY → {execution_id, first_seen} **sharing the ONE identity authority (`category_seq`)**. Additive to the ledger; **a legacy ledger lacking it gets it on next load**."

A new map inside the existing ledger, sharing the one authority, is the **established** way to admit a population. It is the opposite of a parallel ledger.

## W3.1 Files and authorities

| File | Change | Kind | Authority |
|---|---|---|---|
| `00-BOOK/tools/ukb.py` `load_ledger()` | additive default for the durable map, exactly as `by_execution` | KIND-D | UMB-003 owner |
| `00-BOOK/DATA/id-ledger.json` | **the map appears; no existing map, key or value is touched** | KIND-A + KIND-M | written **only** by `ukb.py::_dump_json` — the located writer |
| `00-BOOK/MASTER-BOOK/UMB-003-IDENTITY-ARCHITECTURE.md` | append-only amendment admitting the map and declaring `REALIZES AIF` for it | KIND-D | UMB-003 owner |
| `00-MASTER/UIS-001/uis-declaration.json` | `ledger_source` gains the map name | KIND-D | UIS-001 |
| `platform/foundation/durable_identity.py` | **no edit.** In-memory by DP-03; it produces the records, `ukb.py` persists them | — | — |
| `engine/certification/ledger.py` | **no edit.** Its `GENESIS_HASH` / `entry_hash` / `verify()` chain shape is the *pattern*, not a dependency | — | — |

## W3.2 Execution order inside W3 (Rule EX-1)

```
1  DECLARE   additive default in load_ledger(); map name in the declaration      KIND-D  reversible
2  PREPARE   IdentityRegistry.prepare(...) for every member of every declared    ——      reversible
             cell — provisional, non-persisting
3  ADOPT     DurableIdentity.adopt(authority, local_key, opaque) for every        KIND-A  reversible
             historical value: opaque frozen verbatim, adopted=True                       (pre-commit)
4  VERIFY    require_intact() · verify() · _guard_opaque over committed AND       ——      —
             pending · fingerprint() recorded
5  GATE      G3-1 … G3-9 below, all green                                        ——      —
─────────────────────────────────────────── ROLLBACK BOUNDARY ────────────────────────────────
6  COMMIT    IdentityRegistry.commit(...) then a single ukb.py transaction write  KIND-A/M  IRREVERSIBLE
```

**Step 3 detail — adoption is a record, not a mapping.** `DurableIdentity.adopt` validates the admission key, validates the opaque as exactly `P2_OPAQUE_HEX_LEN` lowercase hex, and preserves it verbatim with `adopted=True`. `verify()` then short-circuits `True` because "an adopted identity carries a frozen historical opaque that is preserved, not recomputed (AX-02)". No old→new table is produced anywhere, because none is needed.

**Step 4 detail — adoption cannot manufacture uniqueness.** `_guard_opaque` runs on the adoption path over **both** committed and pending sets. If two historical records share an opaque, adoption **fails closed** with `IdentityCollisionError` rather than silently coalescing them. The adopted count is therefore itself evidence.

## W3.3 Verification gates (all before step 6)

| Gate | Exact command / check | Proves |
|---|---|---|
| G3-1 | `python3 00-BOOK/tools/ukb.py validate` | no duplicate `universal_id`; page ranges non-overlapping; referential integrity; every artifact schema-valid |
| G3-2 | `bash 00-BOOK/tools/register.sh --observe` | registration parity, read-only |
| G3-3 | `make uis-self` | `--check-record-immutability` (write set ∩ located record set = ∅ for the measurement) and `--check-no-identity-minting` still hold |
| G3-4 | `make uis-gate` | all 20 laws within bounds |
| G3-5 | `make uis-replay` | registers replay from the declaration; zero drift |
| G3-6 | `IdentityRegistry.require_intact()` | `len(_by_opaque) == len(_committed)`; key ↔ opaque bijective; every record verifies |
| G3-7 | **existing-map digest invariance** | every pre-existing key/value in `by_path`, `by_object`, `by_observation`, `history`, `category_seq`, `page_cursor`, `discovered_volumes` is **byte-identical** to the W0 anchor. Only the new map is added. |
| G3-8 | `make uis-gate` R5 readings | `identities_unresolvable == 6` and `namespace_partition_ambiguities == 17` — **exactly**, not fewer |
| G3-9 | `pytest engine/tests platform/tests -q` + `python3 -m engine.uaue.gate --replay --quiet` | no regression; projection byte-comparison intact |

**G3-7 is the wave's defining gate.** It is the mechanical expression of "preserve historical identities": the ledger after W3 differs from the ledger before W3 by *addition of one key* and nothing else.

## W3.4 Rollback boundaries

| Phase | Rollback | Mechanism |
|---|---|---|
| Steps 1-2 | revert; discard provisionals | `abort()` — idempotent, a no-op for a never-prepared mint |
| Steps 3-5 | `abort()` every prepared/adopted-but-unsealed record; revert KIND-D writes | provisional mints "never persist" |
| **Step 6 onward** | **no revert exists** | `abort()` raises `IdentityMintError("cannot abort an already-sealed identity (forward-only)")` |

**Post-boundary correction is forward-only and takes exactly one of these located forms:** a `history` append; `retire()` (marks, never removes, and the key can never be re-minted); a new certification ledger entry; a widened `DigestSet`. **Deleting a map, editing a value or renumbering a render is not available and must not be attempted** — AIF-L17, UIL-05, UIL-06, UIL-13.

## W3.5 Abort criteria (stop the wave, do not commit)

- Any `IdentityCollisionError` from `_guard_opaque` during adoption.
- G3-7 shows any pre-existing key or value changed.
- G3-8 shows either R5 reading **moved in any direction**, including downward.
- Any gate G3-1…G3-9 non-zero.

---

# PART 5 — WAVES W4 AND W5

## W4 · Registration replay tier + measurement closure (J7, J8)

| Field | Value |
|---|---|
| Authority | UIS-001 (declaration only) |
| Depends on | W1 (for J8) · W3 committed (for J7) |
| Write kinds | KIND-D only |
| Rollback | fully reversible — revert the declaration append |

**Files**

| File | Change | Kind |
|---|---|---|
| `00-MASTER/UIS-001/uis-declaration.json` | append a `validations[]` dimension for registration replay (`measure`, `comparator`, `expect`, `blocking: true`) | KIND-D |
| `00-MASTER/UIS-001/uis-declaration.json` | `laws[]` UIL-11 `measurable: false → true` with its measure bound | KIND-D |
| `00-MASTER/UIS-001/uis-declaration.json` | declare the nine zero-member prefixes **RESERVED** (R6) | KIND-D |
| `00-MASTER/UIS-001/uis_engine.py` | **no edit** — PR-07 zero enumeration guarantees an engine change is not required | — |

**Why UIL-11 becomes measurable.** Its declared reason is contingent: "the internal constructs are code-plane objects… asserting reflexivity over them would require this measurement to mint or read an identity it has no authority over." After W1, authorities and mechanisms are a *declared population* with located authorities rooted at the AIF-L10 Genesis anchor — so UIS can **read** their identities, and reading is exactly what UIS is permitted to do.

**Replay is two-class and must remain so** (Determination D-4): adopted → preservation check (`verify()` short-circuit, AX-02); minted → re-derivation check (`compute_opaque(recorded key) == recorded opaque`). Collapsing the classes would either falsely fail history or disable tamper detection.

**Gates**

| Gate | Command | Proves |
|---|---|---|
| G4-1 | `make uis-self` | `--check-no-enumeration` still passes — the engine was **not** edited, proving PR-07 held |
| G4-2 | `make uis-gate` | the new dimension is measured and blocking; UIL-11 no longer DECLARED-NOT-MEASURABLE |
| G4-3 | `make uis-replay` | zero drift |
| G4-4 | non-vacuity probe | an empty cell, an empty population and an unmeasured law each **FAIL**; the nine RESERVED prefixes fail rather than pass silently |
| G4-5 | `make uis-gate` R5 | `6` and `17`, unchanged |

**G4-1 is the plan's structural proof.** If the engine had to change to measure a newly declared population, the zero-enumeration property would be false and the universality proof in the Determination would not hold. This gate is where that claim is tested rather than asserted.

## W5 · Certification (AIF-L21 duality)

| Field | Value |
|---|---|
| Authority | certification authority (`engine/certification/`) + corpus certification (`00-BOOK/tools/ukbx.py`) |
| Depends on | W3 committed · W4 green |
| Write kinds | KIND-A (attestation entry) + derived recomputation |
| Rollback | attestation entries are append-only and hash-chained — **no revert**; correction is a new entry |

**Two stores, two truth classes, no contradiction possible.**

| Store | Truth class | Content | Mechanism |
|---|---|---|---|
| Historical Attestation | RECORDED · immutable · hash-chained | what was adopted, under which epoch, with which frozen ordinals, witnessed by whom | `CertificationRecord.create()` (derives id and `content_sha256` from a core excluding both) → `engine/certification/ledger.py` append from `GENESIS_HASH` |
| Current Status | DERIVED · recomputed every run | do all 20 laws hold now, at declared bounds | `make uis-gate` · `ukbx.py::cmd_certify` → `00-BOOK/DATA/certification.json` |

**Gates**

| Gate | Command / check | Proves |
|---|---|---|
| G5-1 | `engine/certification` ledger `verify()` | chain intact from `GENESIS_HASH`; sequence contiguous; every `entry_hash` recomputes |
| G5-2 | `build_program_closure` | refuses a tampered ledger; framework status computed live; `closure_sha256` byte-identical for the same ledger (no wall clock in the core) |
| G5-3 | `make uis-gate` + `make uis-replay` | current status green and replayable |
| G5-4 | corpus certification | `certification.json` verdict `CERTIFIED` — 10 domains, all pass |
| G5-5 | non-terminality | the attestation records scope closure only; CR-INF-001.2 / CR-INF-011 / IL-INF-01 — **certification closes scope, never evolution** |
| G5-6 | `make verify` | full repository verification green |

**G5-5 is mandatory.** A certification that closed the identity architecture against future populations would invalidate the universality proof it is certifying.

---

# PART 6 — HANDOFF CONTRACT: G-3 RELATIONSHIP DETERMINISTIC IDENTITY CLOSURE

**G-3 consumes this plan. It does not re-derive it, extend it, or work around it.**

## 6.1 Preconditions G-3 must verify before starting

| # | Precondition | Verification |
|---|---|---|
| P-1 | W0 anchor recorded; all nine W0 gates green | re-run G0-1…G0-9 |
| P-2 | W1 complete — the `REL` cell is declared and located | `make uis-gate` (`UIS-V-05/06/07`) |
| P-3 | W2-B complete — the epoch under which edge admission keys canonicalize is registered | `python3 -m engine.uckp.cli validate` |
| P-4 | W3 committed — the durable map exists inside `id-ledger.json`, and G3-7 passed | existing-map digest invariance vs W0 anchor |
| P-5 | W4 green — registration replay is a blocking declared dimension | `make uis-gate` |
| P-6 | W5 green — the adoption event is attested and the chain verifies | ledger `verify()` |
| P-7 | R5 readings still exactly `6` and `17` | `make uis-gate` |

## 6.2 What G-3 receives

| Artifact of this plan | Content G-3 consumes |
|---|---|
| **Declared cell** | plane P4/P2 · population code `REL` (already a `RegistryKind`, `engine/registry/universal/identity.py:138`) · located authority · grammar owner |
| **Admission key rule** | `local_key` = canonical render of the ordered triple `(from, to, type)`. This is an *admission key* under AIF-L06, **not** a content digest under AIF-L05 — for a relationship the endpoints-and-type **are** the thing. `compute_opaque` hashes `{authority_id, local_key, plane:"P2"}` and never content, order or path. |
| **Adoption inventory** | **13 361** edges recorded in `00-BOOK/DATA/relationships.json`; **18 430** `UEDGE-` references across `00-BOOK/DATA/`; the W0 digest of `relationships.json` as the anchor |
| **Frozen-ordinal rule** | every existing `UEDGE-NNNNNNNNN` is adopted **frozen** and becomes recorded rather than recomputed. AIF-L04 · CR-INF-005.1 ("sequence numbers are aliases… not identity") · IL-INF-03. **The render's value never changes, so all 18 430 references keep resolving.** |
| **Reference rule** | `inverse_of` resolves through `durable_reference()`, not through a positional neighbour |
| **Existing key computation** | the admission key is *already computed today* — `_seen_edges.add((src, dst, etype))` at `00-BOOK/tools/ukb.py:1024`. Only the identifier fails to use it. |
| **Durable substrate** | the map admitted in W3, written only by `ukb.py::_dump_json` |
| **Gate battery** | G0-1…G0-9, G3-1…G3-9, G4-1…G4-5, G5-1…G5-6, reusable verbatim |
| **Rollback boundary** | the prepare/commit seam, code-enforced by `abort()` |

## 6.3 What G-3 must not do

| Prohibition | Reason |
|---|---|
| Re-derive `UEDGE-` values by any rule — sorted, hashed, canonical or otherwise | Any recomputation of the render is renumbering (UIL-06, UIL-18, AIF-L17), and a *deterministic* recomputation is still identity-derived-from-generation (AIF-L20). Determinism does not make renumbering lawful. |
| Create `by_edge.json` or any edge-identity file | Parallel ledger. The map lives inside `id-ledger.json`, sharing the one authority (`by_execution` precedent). |
| Emit an old→new edge-id mapping | Migration table. Adoption records "this value is the value"; it maps nothing. |
| Add an edge-only resolver, shim or alias table | Compatibility layer / temporary resolver. `resolve()` and `lookup()` are already total and fail closed. |
| Introduce a relationship-specific identity authority or rule | Special-case authority. Every clause here is the general model with `population = REL`. |
| Retire the per-build `edge_seq` counter by making it global/persistent | A persisted sequential counter is still sequential identity dependency. The counter's *output* becomes a recorded P3 render; the counter stops being an identity source. |
| Reduce `identities_unresolvable` below 6 or `namespace_partition_ambiguities` below 17 | R5. Reducing either requires deleting or renumbering recorded identity. **A closure that improved these would violate the laws it claims to close.** |
| Commit before its gates are green | Rule EX-1. Post-boundary there is no rollback. |

## 6.4 G-3 exit criteria

1. `edge_id` values in `relationships.json` are **byte-identical** to the W0 anchor. Not equivalent — identical.
2. Every edge resolves to a durable identity via its admission key, and re-minting is idempotent.
3. Inserting an edge anywhere in the traversal changes **no other edge's identity** — the mechanical death of J1.
4. `make uis-gate`, `make uis-replay`, `ukb.py validate`, `register.sh --observe` all green.
5. R5 readings exactly `6` and `17`.
6. AIF-L20 satisfied: identity determinism is recorded, no longer a side effect of generation determinism.

---

# PART 7 — ANTI-SHORTCUT REGISTER

Every entry is an implementation route that would appear to close a blocker faster and is **prohibited**, with the reason and the compliant alternative.

| Shortcut | Why prohibited | Compliant route |
|---|---|---|
| Recompute `UEDGE-` ids deterministically from a canonical sort | Still positional in substance and still identity-from-generation (AIF-L20); renumbers 13 361 renders and breaks 18 430 references | Adopt renders frozen; mint P2 from the admission key (W3, G-3) |
| Bulk re-hash the corpus to add `algorithm:` tags | Rewrites Recorded Truth | Register the three epochs; read history under its epoch; tag forward only (W2-B) |
| Rename `content_hash` → profile-specific field names | Compatibility layer across ~3 905 occurrences | The *record* carries `profile_id`; the field name does not change |
| Loosen the artifact grammar regex to remove the width limits | Makes UIL-19 retroactively meaningless; admits identifiers the Genesis epoch disallowed | Preserve the pattern verbatim as the Genesis profile; width extension is a triggered forward parameter (W2-A) |
| Delete or merge the nine zero-member prefixes | Deletes declared truth; and a vacuous pass is worse than a declared reserve | Declare them RESERVED so they fail non-vacuity (W4) |
| "Fix" the 6 unresolvable / 17 ambiguities | Requires deleting or renumbering recorded identity (R5) | Preserve, keep bounded, keep `--check-bounds-tight` |
| Unify the three canonicalization profiles into one | Changes historical digests | Register all three; pin one as the forward default |
| Delete `intelligence/kernel/ids.py` or `platform/foundation/identity.py` to remove duplicate authorities | Deletes a located mechanism and orphans its identifiers | Declare the cell; register the code space; delegate the digest (W1) |
| Edit `uis_engine.py` so it can measure the new populations | Destroys zero enumeration and voids the universality proof | Append to the declaration; G4-1 tests that no engine edit was needed |
| Commit W3 and then verify | No rollback exists post-boundary | Rule EX-1: all gates before commit |
| Add an eleventh certification domain for identity | Addition where declaration suffices | Declare the dimension in `validations[]` (W4) |

---

# PART 8 — CONSOLIDATED MATRICES

## 8.1 Wave summary

| Wave | Closes | Authority | Depends on | Write kinds | Boundary | Rollback |
|---|---|---|---|---|---|---|
| W0 | baseline anchor | executor (read-only) | — | none | pre | trivial |
| W1 | R1 → J4; enables J8 | package owners + UIS-001 | W0 | KIND-D | pre | full revert |
| W2-A | R3 → J5 | schema owner + UMB-004 | W0 | KIND-D | pre | full revert |
| W2-B | R4 → J2/J3 | Layer Zero + engine owners | W0 | KIND-D | pre | full revert |
| W3 | R2 → J6 | **UMB-003 owner** | W0, W1 | KIND-D → A → M | **crosses** | abort pre-commit; forward-only after |
| W4 | J7, J8, R6 | UIS-001 | W1, W3 | KIND-D | pre | full revert |
| W5 | AIF-L21 duality | certification authority | W3, W4 | KIND-A | append-only | new entry only |
| G-3 | J1 | relationship owner | W0…W5 | KIND-A + M | crosses | abort pre-commit |

## 8.2 Files touched, by wave (complete)

| File | W1 | W2-A | W2-B | W3 | W4 | W5 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| `00-MASTER/UIS-001/uis-declaration.json` | ✎ | ✎ | | ✎ | ✎ | |
| `00-MASTER/UIS-001/uis_engine.py` | — | — | — | — | **—** | — |
| `intelligence/kernel/ids.py` | ✎ | | ✎ | | | |
| `platform/foundation/identity.py` | ✎ | | | | | |
| `platform/universal_control_plane/{intelligence,prompt,ontology}.py` | ✎ | | | | | |
| `engine/uicm/validation.py` | ✎ | | | | | |
| `engine/kernel/identity.py` · `platform/universal_pipeline/identity.py` | — | — | — | — | — | — |
| `engine/registry/universal/identity.py` | — | — | — | — | — | — |
| `platform/foundation/{durable_identity,crypto_agility,canonical}.py` | — | — | — | — | — | — |
| `engine/uckp/canonical.py` | — | — | ✎ | | | |
| `00-BOOK/SCHEMAS/artifact.schema.json` | | ✎ | | | | |
| `00-BOOK/MASTER-BOOK/UMB-004-…md` | | ✎ | | | | |
| `00-MASTER/*/…_engine.py` (canonicalization sites) | | | ✎ | | | |
| `00-BOOK/tools/ukb.py` | | | | ✎ | | |
| `00-BOOK/MASTER-BOOK/UMB-003-…md` | | | | ✎ | | |
| `00-BOOK/DATA/id-ledger.json` | | | | **+map only** | | |
| `00-BOOK/DATA/relationships.json` | — | — | — | — | — | — |
| `00-BOOK/DATA/artifacts.json` · `change-ledger.json` | — | — | — | — | — | — |
| `engine/certification/*` | — | — | — | — | — | ✎ append |

Legend: ✎ append-only edit by the named owner · `—` **must not change** · `+map only` the sole Recorded-Truth write in the entire plan.

## 8.3 Gate matrix (every gate is an existing command)

| ID | Command | W0 | W1 | W2-A | W2-B | W3 | W4 | W5 |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| uis self-guards | `make uis-self` | ● | ● | ● | | ● | ● | |
| uis conformance | `make uis-gate` | ● | ● | ● | | ● | ● | ● |
| uis replay | `make uis-replay` | ● | ● | | | ● | ● | ● |
| registry validate | `python3 00-BOOK/tools/ukb.py validate` | ● | ● | ● | | ● | | |
| registration observe | `bash 00-BOOK/tools/register.sh --observe` | ● | | | | ● | | |
| canonical non-duplication | `python3 -m engine.uckp.cli validate` | ● | ● | | ● | | | |
| tests | `pytest engine/tests platform/tests intelligence/tests -q` | ● | ● | | ● | ● | | |
| build determinism | `python3 -m engine.determinism.reproduce BP-DATA-0001 --evidence-dir determinism-evidence` | ● | | | ● | | | |
| evolution replay | `python3 -m engine.uaue.gate --replay --quiet` | ● | | | ● | ● | | |
| full verify | `make verify` | | | | | | | ● |
| **anchor digest invariance** | protected-file digests vs W0 | | ● | ● | ● | ● | ● | ● |
| **R5 invariance** | `6` and `17`, exactly | ● | ● | | | ● | ● | ● |

The last two rows are unconditional: **every wave must reproduce the W0 anchor and the R5 readings.** A wave that changes either has left the plan.

## 8.4 Mandatory-principle conformance

| Principle | Enforced by |
|---|---|
| Preserve historical identities | G3-7 existing-map digest invariance · adoption freezes verbatim · anchor-invariance row in every wave |
| Never renumber | invariant CP-1 · no wave has an existing render as a write target · G-3 §6.3 row 1 |
| Never delete recorded truth | no wave has a delete step; post-boundary correction is forward-only (Rule EX-2) |
| No duplicate identity authorities | W1 declares cells; `UIS-V-04/05/06/07`; generalized `_FORBIDDEN_MINTS` probe |
| No parallel ledgers | W3 admits a **map inside** `id-ledger.json` on the `by_execution` precedent |
| No positional identity | identity is a digest of the admission key; `compute_opaque` never hashes content, order or path |
| No finite identity assumptions | planes closed at 5; every other register append-only; G4-1 proves no engine edit was needed to admit a new population |

---

# PART 9 — BOUNDARY, DETERMINATION, CERTIFICATION

## AUTHORITY BOUNDARY (MANDATORY)
This artifact holds no constituent, governance, ratification, certification or execution authority. It creates no engine, registry, ledger, identifier namespace, resolver, volume or lifecycle. It allocates no identifier and mints no identity. It amends no constitution, supersedes no determination and authorizes no EC-series step. Every action it sequences is performed by that instrument's own located owner; this plan performs none of them. It treats `00-SOURCE/`, `99-FREEZE/`, `01-WORKING/`, `02-MASTER/`, `07-ENGINEERING/`, `00-CEP/`, `00-CMG/`, `00-BOOK/`, `engine/`, `intelligence/` and all program registers as read-only. It embeds no secret, credential or key material. It is subordinate to the frozen constitutional corpus, to AIF, to AUTH-INF-001, to ENG-001, to the resolved Convergence Closure Determination and to every superior determination. Where it conflicts with a located instrument, it is void to the extent of the conflict.

## DETERMINATION

- **A. Are R1…R4 mapped into execution waves?** **YES.** R1 → W1 · R3 → W2-A · R4 → W2-B · R2 → W3, with J7 and J8 as declared consequences in W4 and certification in W5. Dependency ordering is forced and each constraint carries its reason (§0.4).
- **B. Are exact files, authorities, dependencies, gates and rollback boundaries defined?** **YES.** §8.2 lists every file with its per-wave disposition, including the files that **must not change**; §8.3 lists every gate as an existing command; §0.3 and §3/§4 define the rollback boundary as the prepare/commit seam, code-enforced by `abort()`.
- **C. Is any new mechanism introduced?** **NO.** Zero identity systems, ledgers, registries, namespaces, resolvers, migration tables, compatibility layers and shortcuts. §7 enumerates eleven plausible shortcuts and refuses each with its compliant alternative.
- **D. Are historical identities preserved?** **YES, mechanically.** Only one wave writes Recorded Truth, and its defining gate (G3-7) requires the ledger to differ from the anchor by the addition of one key and nothing else. Adoption freezes every historical value verbatim.
- **E. Does the plan protect the permanent residuals?** **YES.** R5 (`6`, `17`) is an unconditional invariance row in every wave, in both directions — a reduction is a failure. R6 is declared RESERVED so it fails non-vacuity rather than passing silently.
- **F. Does G-3 consume this plan?** **YES.** PART 6 is a contract: seven preconditions to verify, eight artifacts consumed, seven prohibitions, six exit criteria. G-3's first exit criterion is that `edge_id` values remain **byte-identical** to the W0 anchor.
- **G. Is the identity architecture closed by executing this plan?** **NO** — and it must not be. Certification closes scope, never evolution (CR-INF-001.2, CR-INF-011, IL-INF-01), which gate G5-5 tests explicitly.
- **H. Is there a wave without rollback?** **YES, by construction: W3 after step 6, and W5.** Both are stated as such, both place all verification before the boundary, and both restrict post-boundary correction to the four located forward-only forms.

## CERTIFICATION

| Attribute | Value |
|---|---|
| Artifact status | ACTIVE — execution plan of record |
| Verdict | **EXECUTION PLAN DETERMINED · 4 OWNER ACTIONS SEQUENCED · 2 RESIDUALS PROTECTED · 0 MECHANISMS CREATED** |
| Waves | 7 (W0, W1, W2-A, W2-B, W3, W4, W5) + G-3 handoff |
| Waves crossing the rollback boundary | 2 (W3 step 6, W5) — both stated, both gate-before-commit |
| Recorded-Truth writes in the whole plan | **1** — the additive map in `00-BOOK/DATA/id-ledger.json` (W3) |
| Files that must not change | 11 (§8.2, `—` rows), incl. `relationships.json`, `artifacts.json`, `change-ledger.json`, `uis_engine.py`, all six unedited identity modules |
| Gates defined | 40, every one an existing command |
| Mechanisms / ledgers / registries / namespaces / migration tables created | **0 / 0 / 0 / 0 / 0** |
| Identities altered | **0** |
| Shortcuts admitted | **0** (11 refused, §7) |
| Sole input | the resolved Convergence Closure Determination |
| Files created by this artifact | **1** (this artifact) |
| Files modified by this artifact | **0** |
| Authority | **NONE** |

*Return: [Convergence Closure Determination](UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-CONVERGENCE-CLOSURE-DETERMINATION.md) · [Identity Evolution Architecture Determination](UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-EVOLUTION-ARCHITECTURE-DETERMINATION.md) · [Absolute Identity, Federation & Continuity Constitution](02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md) · [Master Knowledge Book](00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*

**END OF ARTIFACT — UNIVERSAL IDENTITY CONVERGENCE IMPLEMENTATION EXECUTION PLAN · PLAN ONLY · NO IMPLEMENTATION · AUTHORITY-NEUTRAL**
