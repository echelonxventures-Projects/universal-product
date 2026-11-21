# 04 — WAVE 1 IMPLEMENTATION PLAN (constitutional)

**Scope:** Wave 1 = Substrate Foundation (USIS-001…005) per roadmap `USIS-012`.
**Execution model:** one capability at a time under **UCIC-001** (15 stages,
fail-closed) + the **SCIENCE_INTELLIGENCE lifecycle**. Multi-session program.
**This document plans; it does not implement. No implementation begins without explicit authorization.**

---

## 1 — Implementation phases (dependency order)

| Phase | Capability | Corpus surface | Entry dep | Exit gate |
|---|---|---|---|---|
| **W1-0** | Governed pre-flight | (`config.py` append-only, optional per `03` §5b); local `pip install jsonschema` for parity | baseline `2bf5312` | `ukb validate` PASS; guard clean |
| **W1-1** | USIS-001 Constitution | `15-…/00-CONSTITUTION/` | USIS-GOV-000 | UCIC 15/15; certify 10/10; guard clean |
| **W1-2** | USIS-002 Universe Catalog (21) | `15-…/06-UNIVERSES/` (+ Universe Registry) | USIS-001 | as above + obl. 2/3 (no dup universe) |
| **W1-3** | USIS-003 Science Catalog (30 seed) | `15-…/07-SCIENCES/` (+ Science Registry) | USIS-002 | as above + open-registry proof (obl. 20/21) |
| **W1-4** | USIS-004 Capability Meta-Model (24-tier) | `15-…/05-META-MODEL/` (+ Capability Registry) | USIS-002, USIS-003 | as above + meta-model closure (obl. 13) |
| **W1-5** | USIS-005 Theory/Ontology/Taxonomy | `15-…/01-THEORY/ 02-ONTOLOGY/ 03-TAXONOMY/` | USIS-004 | as above + ontology/taxonomy closure (obl. 11/12) |
| **W1-6** | Wave-1 acceptance & baseline sync | projections + convergence commit + guard | W1-1…5 | guard PASS; determinism re-proven; wave determination |

Each of W1-1…W1-5 is a complete UCIC-001 cycle producing its own per-capability
evidence and certification before the next begins (no batching, no forward
references).

## 2 — Per-capability UCIC-001 cycle (repeated W1-1…W1-5)

```
Stage 1  Intent + Capability Identifier (USIS-001 Part D spec BEFORE Stage 4)
Stage 2  Dependency satisfaction (Depends-On targets registered + terminal-success)
Stage 3  Governing determination + constitutional anchor bound
Stage 4  Author artifact under 15-…/<area>/ (front-matter: VOL-024, USIS, science-intelligence)
Stage 5–8  Model / reason / compose within governed bounds (LAW USIS-04 tech-neutral)
Stage 9  Evidence emitted (provenance/explanation trace — LAW USIS-07)
Stage 10 Certification (ukbx certify domain pass for the new state)
Stage 11–14 Registration + traceability + change/version/lineage
Stage 15 Completion definition satisfied; artifact CERTIFIED (USIS-008 lifecycle)
```

Repository realization of each cycle (the reused gate sequence):

```
ukb enforce --pre   →  ukb build   →  ukb validate   →  ukbx sync --due
→ ukbx twin  →  ukbx portal  →  ukbx validate  →  ukbx twin --check
→ ukbx certify  →  ukb enforce   →  register.sh --guard
```

(identical to `register.sh`'s 10 phases; `register.sh` orchestrates it).

## 3 — Constitutional checkpoints (fail-closed, every phase)

| Checkpoint | Predicate | Mechanism |
|---|---|---|
| CC-1 No redesign | only append-only additions; nothing renumbered | id-ledger append check; USIS-011 obl. 7 |
| CC-2 No duplication | no competing universe/catalog/ontology/registry | Reuse-First diff; obl. 2/3 |
| CC-3 Tech neutrality | no vendor/framework named in architecture | grep audit; obl. 1 |
| CC-4 No-Orphan | classified + homed + parented + registered | `ukb enforce`; obl. 4 |
| CC-5 Acyclic downward | Depends-On graph acyclic, downward-only | `ukbx twin --check` C-07; obl. 5 |
| CC-6 Freeze integrity | 0 edits to C2/C3/C4 and frozen paths | `git status` of freezes; obl. 19 |
| CC-7 Provenance | every capability carries the 7 integration facets | USIS-001 Part D; obl. 15 |
| CC-8 Higher-instrument | no conflict with LAW Ω∞-000 / MIP / freezes | conflict-rule audit |

Any nonzero on a fail-closed invariant (USIS-001 Part F) ⇒ **STOP at that phase**
with evidence; do not proceed.

## 4 — Validation gates (per phase)

- `ukb validate` — structural + schema (schema layer exercised in CI via `jsonschema`; recommend local install for parity — R-4).
- `ukb enforce` — 0 unregistered / 0 unclassified / 0 invalid; eligible == registered.
- `ukbx validate` — twin signal-ledger integrity; provenance present; secret-free.
- `ukbx twin --check` — 7 hard checks (acyclic, navigation, control-tower, export, search).
- **USIS-011 obligations gating the build:** 4 (orphans), 10 (registry closure), 18 (repository consistency / byte-stable).

## 5 — Certification gates (per phase)

- `ukbx certify` — 10 integrity domains PASS over the new state.
- Per-capability: USIS-011 obligation 16 (validation evidence present) + 17 (certification recorded) discharged at UCIC Stage 9/10.
- FREEZE C2/C3/C4 remain **immutable**; no new freeze in Wave 1 (FREEZE C5 is Wave 6).

## 6 — Determinism & convergence gate (per commit)

- After each capability: `register.sh` TRANSACTION COMPLETE, then commit the
  capability + regenerated projections atomically, then `register.sh --guard`
  PASS (0 drift). Byte-stable regeneration re-proven (idempotent re-run → zero
  diff), exactly as in the published baseline.
- CI `ucos-registration-gate.yml` independently re-verifies on push/PR.

## 7 — Expected repository impacts (Wave 1)

| Impact | Detail |
|---|---|
| New corpus files | `15-…/00-CONSTITUTION/ 06-UNIVERSES/ 07-SCIENCES/ 05-META-MODEL/ 01-THEORY/ 02-ONTOLOGY/ 03-TAXONOMY/ 04-REGISTRIES/` — USIS-001…005 + Wave-1 USIS registries |
| New registrations | USIS-001…005 + Universe/Science/Capability registry structure; `id-ledger` page cursor advances from 9134 (append-only) |
| Projections regenerated | `00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}` each build; new portal page per artifact |
| Governed source (optional) | single append-only `config.py` edit if chaining USIS-001…005 (R-2) |
| Volumes | **no change** — VOL-024 reused; no new volume |
| Upstream programs / freezes | **no change** — additive-only |
| Working-tree cleanliness | guard-scope clean after each convergence commit |

## 8 — Risk register

| # | Risk | Evidence | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | **Stale VOL-023 in blueprints** — `USIS-005 §4` front-matter template, `USIS-008`, `USIS-012` Wave-0 step still say `VOL-023`; ratified baseline is `VOL-024` | `config.py:275`, `volumes.json` | Front-matter `VOL-023` would misclassify (metadata classify precedes path rule) | Author all Wave-1 front-matter with `VOL-024`; treat blueprint VOL-023 as superseded (B1 correction) |
| R-2 | **Chain vs non-chained** ordering for USIS-001…005 | `config.py CHAINS["USIS"]` head-only | Governance choice affects Parent/Child edges | Decide at W1-0; both acyclic; recommend append-only chain (`03` §5) |
| R-3 | **Scope ambiguity** USIS-001…005 vs …021 | roadmap vs Wave-0 shorthand | Wrong scope = over/under build | Confirm Wave 1 = USIS-001…005 with authorizer before W1-1 |
| R-4 | **jsonschema absent locally** | `ukb validate` note | Local schema layer skipped | Install locally; CI already enforces |
| R-5 | **Reuse-First duplication** | LAW USIS-02 | Duplicate universe/registry = constitutional fail | `02` §6 register; obl. 2/3 each phase |
| R-6 | **Frozen-path edit** | Part F inv. 5 | Any freeze/engine edit voids conformance | Author only under `15-…/`; only governed `config.py` append allowed |
| R-7 | **Drift / non-determinism** | guard model | Uncommitted regen = drift | Convergence commit + guard after each capability |
| R-8 | **Multi-session continuity** | roadmap governance note | Partial state across sessions | One UCIC capability per unit; each ends guard-clean and certified |
| R-9 | **DR-RAT-11 external finality PENDING** | establishment determination | none — **non-blocking** | Proceed at PROVISIONAL/engineering-authority tier; carry forward |

## 9 — Explicit non-goals (this plan)

No implementation, no `15-…/` files, no `config.py` edit, no registration
transaction, no commit, no tag, no push, no Wave 2+. This plan is the authoritative
sequence Wave 1 will follow **after explicit authorization**.
