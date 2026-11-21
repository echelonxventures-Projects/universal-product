# 04 — USIS-003 IMPLEMENTATION PLAN (constitutional, fail-closed)

**Scope:** USIS-003 = **Universal Science Catalog** (30 seed disciplines under
`USIS-U-SCI`).
**Execution model:** one capability, one complete **UCIC-001** cycle (15 stages,
fail-closed) + the **SCIENCE_INTELLIGENCE lifecycle** (USIS-008).
**This document plans; it does not implement. No implementation begins without a
separate explicit authorization — and not until the blocking prerequisite is met.**

---

## 0 — BLOCKING PREREQUISITE (must clear before U3 may begin)

**USIS-004 (Universal Capability Meta-Model) must be implemented and registered
first.** USIS-003 `Depends-On USIS-004` (blueprint 03) and every science conforms
to the meta-model (LAW USIS-08; USIS-004 §2 Science tier). Until USIS-004 is a
registered, certified corpus artifact, USIS-003 cannot satisfy UCIC-001 Stage 2 /
USIS-011 obligation 14. **Dependency-correct order: USIS-002 → USIS-004 → USIS-003.**

> The detailed USIS-004 plan is out of scope for this gate (USIS-004 has its own
> Context Assimilation Gate). This plan describes USIS-003 *conditioned on* USIS-004
> being established.

## 1 — Implementation strategy (once unblocked)

Realize the operational-memory blueprint `03-USIS-UNIVERSAL-SCIENCE-CATALOG.md`
into a single registered corpus capability under `15-…/07-SCIENCES/`, using
exclusively **reused** engines and gates. The 30 disciplines are authored as an
**open, append-only registry** (LAW USIS-00 C-00.4), each row owned by `USIS-U-SCI`,
each **conforming to the USIS-004 meta-model** (Science→Discipline→Domain→…→Capability),
each **cross-linking** to intelligence/analytics/learning universes by REFERENCE
(LAW USIS-02). `USIS-SCI-FUTURE-*` / Unknown slots keep the set uncapped.

## 2 — Phases (dependency order)

| Phase | Step | Corpus surface | Entry dep | Exit gate |
|---|---|---|---|---|
| **U3-0** | Governed pre-flight: confirm baseline; **confirm USIS-004 registered + certified**; resolve D-A home (`07-SCIENCES/`) | — | **USIS-004 ✅** + USIS-002 ✅ | `ukb validate` PASS; guard clean |
| **U3-1** | Author Universal Science Catalog artifact (30 seed disciplines) | `15-…/07-SCIENCES/` | USIS-002 + USIS-004 | UCIC 15/15; obl. 2/3/13 (no dup; capability closure) |
| **U3-2** | Register + synchronize + certify | projections (`00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}`) | U3-1 | certify 10/10; twin 7/7; enforce 0-orphan |
| **U3-3** | Convergence commit (separately authorized) + guard | corpus + regenerated projections (atomic) | U3-2 | `register.sh --guard` PASS; determinism re-proven |

## 3 — Required artifacts

- `15-UNIVERSAL-SCIENCE-INTELLIGENCE/07-SCIENCES/USIS-003-UNIVERSAL-SCIENCE-CATALOG.md`
  (front-matter: USIS · USIS · **VOL-024** · UNIVERSAL-SCIENCE-INTELLIGENCE ·
  science-intelligence; DEPENDS-ON `USIS-002` **and** `USIS-004`; owner `USIS-U-SCI`).
- No per-science homes (`USIS-SCI-<NAME>/`) — those are later Wave-3 realizations,
  **excluded** from USIS-003 (catalog only), mirroring the USIS-002 catalog-only scope.

## 4 — Required registrations

- USIS-003 artifact (`UCOS-USIS-000004` expected, append-only) + portal page.
- Registry EXTEND rows (artifact/page/graph/change-version-lineage/certification).
- `id-ledger` page cursor advances from 9139 (append-only). VOL-024 reused (no new volume).
- Graph edges: `Depends-On → USIS-002, USIS-004`; `Parent → USIS-GOV-000`;
  science-row cross-link REFERENCE edges to `USIS-U-SCI` and cross-linked universes.

## 5 — Validation sequence (fail-closed)

`ukb validate` → `ukb enforce` (0 orphan) → `ukbx validate` → `ukbx twin --check`
(C-07 acyclic) → `ukbx certify` (10/10). USIS-011 gating obligations: **2/3** (no
duplicate science/registry), **4** (0 orphans), **5** (acyclic), **13** (capability
closure — each science completes the meta-model chain), **14** (dependency closure —
**USIS-004 now satisfied**), **10** (registry closure), **18** (byte-stable).

## 6 — Certification sequence (fail-closed)

`ukbx certify` 10 integrity domains over the new state (scope 1005+). USIS-011
obl. 16 (validation evidence) + 17 (certification recorded) discharged at UCIC
Stage 9/10. FREEZE C2/C3/C4 immutable; no new freeze.

## 7 — Acceptance criteria

- 30 seed disciplines enumerated as registry rows; each owned by `USIS-U-SCI`;
  each cross-links (REFERENCE) without duplication; open slots present.
- Every science row conforms to the USIS-004 meta-model Science-tier contract.
- Depends-On USIS-002 **and** USIS-004 both resolve (0 unmet).
- Classification USIS/USIS/VOL-024; single canonical home `07-SCIENCES/`; 0 orphans;
  acyclic; byte-stable regeneration; zero frozen-path/governed-source change.

## 8 — Completion criteria

USIS-003 CERTIFIED (USIS-008 lifecycle), guard PASS after the authorized
convergence commit, determinism re-proven, ready for independent acceptance review
— identical rigor to the USIS-002 baseline.

## 9 — Explicit non-goals

No implementation in this gate; no `15-…/` files; no `config.py` edit; no
registration; no commit/tag/push; **no USIS-004 implementation** (separate gate);
no per-science homes; no USIS-005+.
