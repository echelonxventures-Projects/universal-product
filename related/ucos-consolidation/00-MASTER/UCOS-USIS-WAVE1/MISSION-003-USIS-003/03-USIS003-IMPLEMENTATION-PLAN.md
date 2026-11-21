# 03 — USIS-003 IMPLEMENTATION PLAN (constitutional, fail-closed)

**Scope:** USIS-003 = **Universal Science Catalog** (30 seed disciplines under
`USIS-U-SCI`).
**Execution model:** one capability, one complete **UCIC-001** cycle (15 stages,
fail-closed) + the **SCIENCE_INTELLIGENCE lifecycle** (USIS-008).
**This document plans; it does not implement. No implementation begins without a
separate explicit authorization.** The prior blocking prerequisite (USIS-004) is
now satisfied (baseline `e33c05b`).

---

## 1 — Prerequisite status (was the blocker; now cleared)

| Prerequisite | State | Evidence |
|---|:--:|---|
| USIS-002 (owner `USIS-U-SCI`) | ✅ | `UCOS-USIS-000003`, committed `8db7d52` |
| **USIS-004 (meta-model)** | ✅ | `UCOS-USIS-000004`, committed `e33c05b` |
| LAW USIS-00 | ✅ | USIS-001 |

**Dependency-correct order USIS-002 → USIS-004 → USIS-003 is fulfilled.**

## 2 — Implementation strategy

Realize the operational-memory blueprint `03-USIS-UNIVERSAL-SCIENCE-CATALOG.md`
into a single registered corpus capability under `15-…/07-SCIENCES/`, using
exclusively **reused** engines and gates. Author the 30 disciplines as an **open,
append-only registry** (LAW USIS-00 C-00.4), each row owned by `USIS-U-SCI`, each
**conforming to the USIS-004 24-tier meta-model** (Science→Discipline→Domain→…→
Capability tiers), each **cross-linking** to intelligence/analytics/learning
universes by REFERENCE (LAW USIS-02). `USIS-SCI-FUTURE-*` / Unknown slots keep the
set uncapped (LAW USIS-09).

## 3 — Phases (dependency order)

| Phase | Step | Corpus surface | Entry dep | Exit gate |
|---|---|---|---|---|
| **U3-0** | Governed pre-flight: confirm baseline `e33c05b`, guard clean; confirm USIS-002 + USIS-004 registered/certified; resolve home `07-SCIENCES/`; non-chained decision (no `config.py` edit) | — | USIS-002 ✅ + USIS-004 ✅ | `ukb validate` PASS; guard clean |
| **U3-1** | Author Universal Science Catalog artifact (30 seed disciplines) | `15-…/07-SCIENCES/` | U3-0 | UCIC 15/15; obl. 2/3/13 (no dup; capability closure vs meta-model) |
| **U3-2** | Register + synchronize + certify | projections (`00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}`) | U3-1 | certify 10/10; twin 7/7; enforce 0-orphan |
| **U3-3** | Convergence commit (separately authorized) + guard | corpus + regenerated projections (atomic) | U3-2 | `register.sh --guard` PASS; determinism re-proven |

## 4 — Required artifacts (single)

- `15-UNIVERSAL-SCIENCE-INTELLIGENCE/07-SCIENCES/USIS-003-UNIVERSAL-SCIENCE-CATALOG.md`
  - front-matter: USIS · USIS · **VOL-024** · UNIVERSAL-SCIENCE-INTELLIGENCE ·
    science-intelligence; `DEPENDS-ON USIS-002 · USIS-004`; owner `USIS-U-SCI`;
    AUTHORITY NONE-DERIVED; PROVENANCE = registered instantiation of blueprint `03`.
  - content: 30 seed disciplines as registry rows (`USIS-SCI-<NAME>`, home,
    universe `USIS-U-SCI` + cross-links, owner, status, sub-disciplines[]);
    conformance to the USIS-004 Science-tier contract; open `FUTURE-*`/Unknown slots.
- **No** per-science homes (`USIS-SCI-<NAME>/`), **no** capability/tier instances —
  those are later Wave-3 realizations, **excluded** (catalog-only scope).

## 5 — Required registrations

- USIS-003 artifact (`UCOS-USIS-000005` expected, append-only) + portal page.
- Registry EXTEND rows (artifact/page/graph/change-version-lineage/certification).
- `id-ledger` cursor advances append-only. VOL-024 reused (no new volume).
- Graph edges: `Depends-On → USIS-002, USIS-004`; `Parent → USIS-GOV-000`;
  science-row cross-link REFERENCE edges to `USIS-U-SCI` + cross-linked universes.

## 6 — Validation sequence (fail-closed)

`ukb validate` → `ukb enforce` (0 orphan) → `ukbx validate` → `ukbx twin --check`
(C-07 acyclic) → `ukbx certify` (10/10). USIS-011 gating obligations: **2/3** (no
duplicate science/registry), **4** (0 orphans), **5** (acyclic), **13** (capability
closure — each science conforms to the USIS-004 Science-tier chain), **14**
(dependency closure — USIS-002 + USIS-004 satisfied), **10** (registry closure),
**18** (byte-stable).

## 7 — Certification sequence (fail-closed)

`ukbx certify` 10 integrity domains over the new state (scope 1006). USIS-011 obl.
16/17 discharged at UCIC Stage 9/10. FREEZE C2/C3/C4 immutable; no new freeze.

## 8 — Acceptance criteria

- 30 seed disciplines enumerated as registry rows; each owned by `USIS-U-SCI`; each
  cross-links (REFERENCE) without duplication; open slots present.
- Every science row conforms to the USIS-004 meta-model Science tier.
- `Depends-On USIS-002 + USIS-004` both resolve (0 unmet); acyclic; 0 orphans.
- Classification USIS/USIS/VOL-024; single canonical home `07-SCIENCES/`;
  byte-stable regeneration; zero frozen-path/governed-source change; no new volume.

## 9 — Completion criteria

USIS-003 CERTIFIED (USIS-008 lifecycle); guard PASS after the authorized
convergence commit; determinism re-proven; ready for independent acceptance review
— identical rigor to the USIS-001/002/004 baselines.

## 10 — Explicit non-goals

No implementation in this gate; no `15-…/` files; no `config.py` edit; no
registration; no commit/tag/push; no per-science homes; no capability/tier
instances; no USIS-005 content.
