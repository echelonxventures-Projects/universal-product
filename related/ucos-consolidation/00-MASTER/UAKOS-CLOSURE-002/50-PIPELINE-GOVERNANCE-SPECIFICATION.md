# 50 — Pipeline Governance Specification (Phase-004)

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-004 |
| STATUS | PLANNING / GOVERNANCE — no implementation artifact modified |
| AUTHORITY | NONE — DERIVED TRUTH · governed by `CEP-002` (Governance), `CEP-006` (Ratification), `CEP-008` (Evidence-Traceability) |
| BASELINE | HEAD `b67a720` |

> Reuses existing governance (`CEP-*`, `UCOS-GOV-*`, `register.sh --guard`, CI). It adds **one** advisory gate; it creates **no** parallel governance body.

## 1. Execution schedule — when the pipeline runs

| Mode | Trigger | Blocking? | Owner |
|------|---------|:---------:|-------|
| On-demand | `make closure` | no | any contributor |
| Session | SessionStart hook (`.kiro/hooks/uakos-closure-002.json`, repo-only fast pass) | no | agent runtime |
| Event | new source under `00-SOURCE/**` or root upload; new external/conversation corpus | advisory | EKI capability owner |
| CI | pull request / merge (alongside `ucos-registration-gate.yml`) | advisory → **blocking for closure domain only** | CI |
| Release/Freeze | before `CEP-007` freeze of the closure-capability spec | **blocking** | governance board |

## 2. Roles

| Role | Responsibility |
|------|----------------|
| **EKI capability owner** (Phase-001) | runs S1–S7; maintains `closure_engine.py`, `closure.json` per interface contract |
| **Phase-002 owner** | runs S4 projection; read-only on Phase-001 |
| **Repository engine authority** (`ukb.py` / `UCOS-ARCHITECTURE-BOARD`) | sole writer of Repository Truth; approves registration |
| **Governance / Ratification** (`CEP-002`/`CEP-006`, `UCOS-CONSTITUTIONAL-REVIEW`) | approves capability adoption, waivers, version bumps |
| **Validation / Certification** (`CEP-004`/`CEP-005`, CCE) | issues validation + certification verdicts |

## 3. Evidence requirements (CEP-008)

Every closure determination MUST cite physically-present evidence: `closure.json` (S1–S3), `phase2.json` (S4), consolidated gap register (S6), `ukb validate`/`enforce`/`stats` runs (S8/S0), Digital Twin (`control-tower.json`), and the determination (`19`). Absence of evidence = NOT-DONE (`TRACK-001`). No speculative edges.

## 4. Failure handling

- **Gap detected (NOT-CLOSED):** fail-closed. The **closure certificate** is withheld. This does **not** block unrelated commits; it blocks only claims of closure and the freeze of the closure-capability spec.
- **Interface violation** (schema drift in `closure.json`): hard fail; Phase-002 halts; requires version bump + sign-off (see interface contract §4/§5).
- **Determinism failure** (non-byte-identical re-run at same HEAD): hard fail; pipeline is quarantined until reproducibility restored.
- **Drift** (`register.sh --guard` non-zero): hard fail; Repository Truth is out of sync; closure cannot proceed.

## 5. Exception / waiver policy

Exceptions are never silent. A waiver is a `UKDA` decision record (`UKDA-DEC-*`) with: scope, rationale, compensating evidence, **expiry**, and approver (`UCOS-CONSTITUTIONAL-REVIEW`). Waivers are enumerable and audited (`CEP-010`). No waiver may weaken Knowledge Once or single-writer authority.

## 6. Non-duplication guarantee

This spec introduces: **0** new engines, **0** new registries, **0** new traceability stores, **0** new governance bodies. It reuses `CEP-*`, `UCOS-GOV-002`, `register.sh`, `verify.sh`, and CI. The pipeline's only new governance surface is the advisory `closure-gate` target, scoped to the closure domain.

---

*END — 50 · Pipeline Governance · AUTHORITY = NONE.*
