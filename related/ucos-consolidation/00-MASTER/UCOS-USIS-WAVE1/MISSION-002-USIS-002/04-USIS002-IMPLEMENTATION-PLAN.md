# 04 — USIS-002 IMPLEMENTATION PLAN (constitutional)

**Scope:** USIS-002 = **Universe Catalog** (the 21 constitutional universes) —
Wave-1 · Mission 2 per roadmap `USIS-012`.
**Execution model:** one capability, one complete **UCIC-001** cycle (15 stages,
fail-closed) + the **SCIENCE_INTELLIGENCE lifecycle** (USIS-008).
**This document plans; it does not implement. No implementation begins without a
separate explicit authorization.**

---

## 1 — Implementation strategy (constitutional)

Realize the operational-memory blueprint `02-USIS-UNIVERSE-CATALOG.md` into a
single registered corpus capability under `15-…/`, using exclusively **reused**
engines and gates. The universe set is authored as an **open, append-only
registry** (LAW USIS-09), each universe a **single-canonical-owner** row that
**REFERENCES** its realizing MIP universe (LAW USIS-02) — never a competing
catalog. `USIS-U-FUT`/`USIS-U-UNK` are authored as permanent reserved slots so the
set is uncapped by construction (Part F invariant 4 = 0 closed registries).

## 2 — Phases (dependency order)

| Phase | Step | Corpus surface | Entry dep | Exit gate |
|---|---|---|---|---|
| **U2-0** | Governed pre-flight: confirm baseline `07e0de4`, guard clean; decide chain vs non-chained (`03` §5); optional append-only `config.py CHAINS["USIS"]` edit; optional local `pip install jsonschema` for parity | `config.py` (optional, append-only) | baseline `07e0de4` | `ukb validate` PASS; guard clean |
| **U2-1** | Author Universe-Catalog artifact(s) + USIS Universe Registry | `15-…/06-UNIVERSES/` (D-1) + `15-…/04-REGISTRIES/` | USIS-001 (`UCOS-USIS-000002`) | UCIC 15/15; obl. 2/3 (no dup universe) |
| **U2-2** | Register + synchronize + certify | projections (`00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}`) | U2-1 | certify 10/10; twin 7/7; enforce 0-orphan |
| **U2-3** | Convergence commit (separately authorized) + guard | corpus + regenerated projections (atomic) | U2-2 | `register.sh --guard` PASS; determinism re-proven |

Each step is a complete UCIC-001 cycle producing its own per-capability evidence
and certification. No batching, no forward references.

## 3 — Per-capability UCIC-001 cycle (repository realization — reused gate sequence)

```
Stage 1  Intent + USIS-001 Part D spec (Identifier·Objective·Dependencies·Governing
         Determination·Constitutional Anchor·Additive Surfaces·Acceptance·Evidence·
         Validation·Certification·Required Repo Updates·Completion) BEFORE Stage 4
Stage 2  Dependency satisfaction: USIS-001 registered + terminal-success ✓
Stage 3  Governing determination (USIS-001) + anchor (LAW USIS-01/02/09) bound
Stage 4  Author under 15-…/06-UNIVERSES/ (front-matter: VOL-024 · USIS · science-intelligence)
Stage 5–8  Model universe rows; bind each to its MIP anchor (REFERENCE, LAW USIS-02/04)
Stage 9  Evidence: provenance/explanation trace emitted (LAW USIS-07)
Stage 10 Certification: ukbx certify domains PASS for the new state
Stage 11–14 Registration + traceability + change/version/lineage
Stage 15 Completion definition satisfied; USIS-002 CERTIFIED (USIS-008 lifecycle)
```
Orchestrated by `register.sh` (its 10 phases):
```
ukb enforce --pre → ukb build → ukbx sync --due → ukbx twin → ukbx portal
→ ukb validate → ukbx validate → ukbx twin --check → ukbx certify → ukb enforce → [--guard]
```

## 4 — Validation gates (fail-closed)

- `ukb validate` — structural + schema (schema layer enforced in CI via `jsonschema`; local parity optional — R-4).
- `ukb enforce` — eligible == registered; 0 unregistered / 0 unclassified / 0 invalid.
- `ukbx validate` — twin signal-ledger integrity; provenance present; secret-free.
- `ukbx twin --check` — 7 hard checks incl. **C-07 acyclic**.
- **USIS-011 obligations gating USIS-002:** 2/3 (no duplicate universe/registry),
  4 (0 orphans), 5 (acyclic downward), 10 (registry closure), 14 (no forward ref),
  18 (byte-stable regeneration).

## 5 — Certification gates (fail-closed)

- `ukbx certify` — 10 integrity domains PASS over the new state (scope 1004).
- USIS-011 obligation 16 (validation evidence present) + 17 (certification recorded)
  discharged at UCIC Stage 9/10.
- FREEZE C2/C3/C4 remain **immutable**; no new freeze (FREEZE C5 is Wave 6).

## 6 — Constitutional checkpoints (Part F, every phase; any nonzero ⇒ STOP)

| CC | Predicate | Mechanism |
|---|---|---|
| CC-1 No redesign | append-only; nothing renumbered | id-ledger append check; obl. 7 |
| CC-2 No duplication | no competing universe/catalog/registry | Reuse-First diff; obl. 2/3; `02` §6 register |
| CC-3 Tech neutrality | no vendor/model/framework named | grep audit; obl. 1 |
| CC-4 No-Orphan | classified + homed + parented + registered | `ukb enforce`; obl. 4 |
| CC-5 Acyclic downward | Depends-On acyclic, downward-only | `ukbx twin --check` C-07; obl. 5 |
| CC-6 Freeze integrity | 0 edits to freezes/frozen paths | `git status` of freezes; obl. 19 |
| CC-7 Provenance | 7 integration facets present | USIS-001 Part D; obl. 15 |
| CC-8 Open registry | universe set uncapped (`U-FUT`/`U-UNK` reserved) | Part F inv. 4; obl. 20/21 |

## 7 — Determinism & convergence gate

After authoring: `register.sh` TRANSACTION COMPLETE → atomic commit of USIS-002 +
regenerated projections → `register.sh --guard` PASS (0 drift) → byte-stable
re-run (idempotent → zero diff). Baseline determinism hash to preserve:
guard-scope SHA-256 `b53f7fcb…` (will change deterministically to a new stable
value once USIS-002 is registered; the invariant is *byte-stability across
re-runs*, not the specific digest). CI `ucos-registration-gate.yml` re-verifies.

## 8 — Expected repository impact assessment

| Impact | Detail |
|---|---|
| New corpus files | `15-…/06-UNIVERSES/` (Universe Catalog) + `15-…/04-REGISTRIES/` (USIS Universe Registry) |
| New registrations | USIS-002 + universe registry rows; `id-ledger` page cursor advances from **9136** (append-only) |
| Registered-artifact count | 1003 → 1004+ (per artifact authored) |
| Projections regenerated | `00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}` + new portal page(s) |
| Governed source (optional) | single append-only `config.py CHAINS["USIS"]` edit if chained (R-2) |
| Volumes | **no change** — VOL-024 reused |
| Upstream programs / freezes / engines | **no change** — additive-only, no frozen-path touch |
| Working-tree cleanliness | guard-scope clean after the convergence commit |

## 9 — Risk register

| # | Risk | Evidence | Impact | Mitigation |
|---|---|---|---|---|
| **D-1** | **Universe-home naming discrepancy** — roadmap/plan + Wave-1 dependency graph use `15-…/06-UNIVERSES/`; blueprint `02-USIS-UNIVERSE-CATALOG.md §2` registry-row model says `home: 06-DOMAINS/<UNIVERSE>/` | both in repo | Wrong directory = split-home / re-work | **Authorizer confirms canonical universe directory before U2-1.** Recommend `06-UNIVERSES/` (roadmap/plan/`03` consistent); treat blueprint `06-DOMAINS` as superseded shorthand. Non-blocking to the gate. |
| **R-1** | **Stale VOL-023 in blueprints** — some establishment-package front-matter still says VOL-023; ratified baseline is VOL-024 | `config.py:73/275` | Front-matter VOL-023 would misclassify | Author USIS-002 front-matter with **VOL-024** (B1 correction) |
| **R-2** | Chain vs non-chained ordering | `CHAINS["USIS"]` head-only | Governance choice on Parent/Child edges | Decide at U2-0; both acyclic; recommend append-only chain |
| **R-3** | Reuse-First duplication | LAW USIS-02 | Duplicate universe/registry = constitutional fail | `02` §6 register; obl. 2/3 each phase; REFERENCE MIP anchors |
| **R-4** | `jsonschema` absent locally | `04` acceptance note | Local schema layer skipped | Install locally; CI already enforces |
| **R-5** | Frozen-path edit | Part F inv. 5 | Any freeze/engine edit voids conformance | Author only under `15-…/`; only governed `config.py` append allowed |
| **R-6** | Drift / non-determinism | guard model | Uncommitted regen = drift | Convergence commit + guard after authoring |
| **R-7** | DR-RAT-11 external finality PENDING | establishment determination | none — **non-blocking** | Proceed at PROVISIONAL/engineering-authority tier |

## 10 — Explicit non-goals (this plan)

No implementation, no `15-…/` files, no `config.py` edit, no registration
transaction, no commit, no tag, no push, no USIS-003+. This is the authoritative
sequence USIS-002 will follow **after explicit implementation authorization**.
