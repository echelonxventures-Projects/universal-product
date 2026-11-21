# CONST-16 — Repository Governance Freeze Record

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Permanently records and freezes the governance topology. Verified against current evidence.

---

## 1. Purpose

Verify and permanently document the governance topology so it cannot silently drift. This is a
freeze record: it states what is true and forbids competing structures.

## 2. Verified & Frozen Facts

| # | Frozen fact | Verification (baseline b67a720) |
|---|-------------|--------------------------------|
| F1 | Repository Truth remains unique | Single governed corpus; `closure.json` derived from it only. |
| F2 | UKB remains the sole authoritative engine | `00-BOOK/tools/ukb.py`; `ukb validate` is the gate (phase3). |
| F3 | `closure_engine.py` is a derived analytical pipeline | Header self-declares `AUTHORITY = NONE (DERIVED TRUTH)`, never mutates corpus, fail-closed (TRACK-001). |
| F4 | `phase2_engine.py` is a planning stage | Emits `phase2.json` (PHASE-002): co-occurrence graph + enrichment gaps. |
| F5 | `phase3_engine.py` is an execution planning stage | Emits `phase3.json` (PHASE-003): planned waves, `planning_complete=true`. |
| F6 | No pipeline stage is an authority | Only UKB owns truth (F2). Stages 1-3/5/8 derived (CONST-08). |
| F7 | Only UKB owns Repository Truth | Confirmed; no competing owner detected. |

## 3. Singularity Freeze (no-competition clauses)

Frozen: there SHALL be exactly one of each, owned by UKB / the governance authority:

- One **authority** (UKB) — no competing authority.
- One **canonical registry** — no competing registry.
- One **governance** — no competing governance.
- One **canonical store** per concept (Knowledge Once) — no competing canonical stores.
- One **traceability** spine — no competing traceability.
- One **lifecycle** (CONST-09) — no competing lifecycle.

Current evidence: `closure.json` reports 0 `duplicate_canonical_homes`, 0
`ukda_content_hash_duplicates`, 0 orphans — consistent with singular governance and Knowledge Once.

## 4. Freeze Effect

Any introduction of a competing authority/registry/governance/canonical store/traceability/
lifecycle is a constitutional violation and MUST fail-closed. Amendment only via CONST-10.

## 5. DETERMINATION

**Repository governance is FROZEN and VERIFIED.** UKB is the singular authority; all engines are
derived, non-authoritative pipeline stages. No competing structures exist at baseline `b67a720`.
