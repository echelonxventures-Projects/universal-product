# 04 — USIS-004 IMPLEMENTATION PLAN (constitutional, fail-closed)

**Scope:** USIS-004 = **Universal Capability Meta-Model** (the 24-tier
Science→…→Lifecycle realization chain — LAW USIS-08 operationalized).
**Execution model:** one capability, one complete **UCIC-001** cycle (15 stages,
fail-closed) + the **SCIENCE_INTELLIGENCE lifecycle** (USIS-008).
**This document plans; it does not implement. No implementation begins without a
separate explicit authorization.**

---

## 1 — Implementation strategy (constitutional)

Realize the operational-memory blueprint `04-USIS-UNIVERSAL-CAPABILITY-META-MODEL.md`
into a single registered corpus artifact under `15-…/05-META-MODEL/`, using
exclusively **reused** engines and gates. Author the 24-tier chain, the per-tier
contract, the fail-closed conformance rule, the agnosticism boundary (LAW USIS-04),
the Reuse-First selection rule (LAW USIS-02), and the recursion/open-depth guarantee
(LAW USIS-09) — as the constitutional realization spine every USIS capability
conforms to (LAW USIS-08). **Meta-model only** — no capability/tier instances.

## 2 — Phases (dependency order)

| Phase | Step | Corpus surface | Entry dep | Exit gate |
|---|---|---|---|---|
| **U4-0** | Governed pre-flight: confirm baseline `8db7d52`, guard clean; confirm USIS-001 + USIS-002 registered/certified; non-chained decision (no `config.py` edit) | — | USIS-001 ✅ + USIS-002 ✅ | `ukb validate` PASS; guard clean |
| **U4-1** | Author Universal Capability Meta-Model artifact | `15-…/05-META-MODEL/` | USIS-001 + USIS-002 | UCIC 15/15; obl. 2/3 (no dup meta-model) |
| **U4-2** | Register + synchronize + certify | projections (`00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}`) | U4-1 | certify 10/10; twin 7/7; enforce 0-orphan |
| **U4-3** | Convergence commit (separately authorized) + guard | corpus + regenerated projections (atomic) | U4-2 | `register.sh --guard` PASS; determinism re-proven |

Each step is a complete UCIC-001 cycle producing its own per-capability evidence
and certification. No batching; no forward references.

## 3 — Required artifacts (single)

- `15-UNIVERSAL-SCIENCE-INTELLIGENCE/05-META-MODEL/USIS-004-UNIVERSAL-CAPABILITY-META-MODEL.md`
  - front-matter: USIS · USIS · **VOL-024** · UNIVERSAL-SCIENCE-INTELLIGENCE ·
    science-intelligence; `DEPENDS-ON USIS-001 · USIS-002`; `REALIZES LAW USIS-08`;
    AUTHORITY NONE-DERIVED; PROVENANCE = registered instantiation of blueprint `04`.
  - content: 24-tier chain; per-tier contract table (owner / parent edge / closure);
    fail-closed conformance rule; agnosticism boundary; Reuse-First rule; recursion.
- **No** tier-instance artifacts, **no** per-tier registries populated (those are
  produced per-capability in later waves).

## 4 — Required registrations

- USIS-004 artifact (`UCOS-USIS-000004` expected, append-only) + portal page.
- Registry EXTEND rows (artifact/page/graph/change-version-lineage/certification).
- `id-ledger` page cursor advances from 9139 (append-only). VOL-024 reused (no new volume).
- Graph edges: `Depends-On → USIS-001, USIS-002`; `Parent → USIS-GOV-000`;
  `Realizes → LAW USIS-08`; downward-only, acyclic.

## 5 — Validation sequence (fail-closed)

`ukb validate` → `ukb enforce` (0 orphan) → `ukbx validate` → `ukbx twin --check`
(C-07 acyclic) → `ukbx certify` (10/10). USIS-011 gating obligations: **2/3** (no
duplicate meta-model), **4** (0 orphans), **5** (acyclic), **10** (registry
closure), **14** (dependency closure — USIS-001/USIS-002 satisfied), **18**
(byte-stable regeneration). Obligation **13** (capability closure) is *defined by*
this artifact and verified per-capability in later waves.

## 6 — Certification sequence (fail-closed)

`ukbx certify` 10 integrity domains over the new state (scope 1005). USIS-011 obl.
16 (validation evidence) + 17 (certification recorded) discharged at UCIC Stage
9/10. FREEZE C2/C3/C4 immutable; no new freeze.

## 7 — Acceptance criteria

- The 24-tier chain, per-tier contract, fail-closed conformance rule, agnosticism
  boundary, Reuse-First rule, and recursion guarantee are all present and derived
  verbatim-in-substance from blueprint `04`.
- Classification USIS/USIS/VOL-024; single canonical home `05-META-MODEL/`.
- `Depends-On USIS-001 + USIS-002` both resolve (0 unmet); acyclic; 0 orphans.
- Byte-stable regeneration; zero frozen-path / governed-source change; no new volume.
- No tier *instances* authored (meta-model-only scope honored).

## 8 — Completion criteria

USIS-004 CERTIFIED (USIS-008 lifecycle); guard PASS after the authorized
convergence commit; determinism re-proven; ready for independent acceptance
review — identical rigor to the USIS-001/USIS-002 baselines. On completion,
**USIS-003's dependency root is satisfied** (USIS-003 becomes authorizable).

## 9 — Explicit non-goals

No implementation in this gate; no `15-…/` files; no `config.py` edit; no
registration; no commit/tag/push; no capability/science/universe/tier instances;
no USIS-003 or USIS-005 content.
