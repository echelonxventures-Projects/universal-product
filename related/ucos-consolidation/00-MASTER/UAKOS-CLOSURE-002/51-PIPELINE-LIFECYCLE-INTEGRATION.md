# 51 — Pipeline Lifecycle Integration (Phase-004)

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-004 |
| STATUS | PLANNING / GOVERNANCE — no implementation artifact modified |
| AUTHORITY | NONE — DERIVED TRUTH |
| BASELINE | HEAD `b67a720` |
| RULE | No duplicate lifecycle. Reuse existing governance hooks. |

> Maps each pipeline stage onto the repository's **existing** lifecycle hooks. The pipeline plugs in; it does not fork the lifecycle.

## 1. Integration matrix

| Lifecycle event | Existing hook (reused) | Pipeline role | Blocking? |
|-----------------|------------------------|---------------|:---------:|
| **Commit** | git pre-commit (`scripts/install-hooks.sh`) | run EKI fast pass (repo-only) → refresh `closure.json`; advisory closure status | no |
| **Merge / PR** | `.github/workflows/ucos-registration-gate.yml` | run `closure-gate` alongside registration guard; report gaps | advisory (blocking for closure domain) |
| **CI build/test** | `.github/workflows/ec1-ci.yml`, `determinism.yml` | verify pipeline determinism (byte-identical re-run) | blocking (determinism only) |
| **Validation** | `CEP-004` + `verify.sh` + `ukb validate` | S8 consumes these verdicts | reuse |
| **Certification** | `CEP-005` + CCE (`UCOS-COMP-000001`) | S9 consumes CCE verdict | reuse |
| **Architecture review** | `AEOS-001` admission + `EC-3 AP-N` gates | route new capabilities from S7 plan into admission | reuse |
| **Governance** | `CEP-002` + `UCOS-GOV-002` (constitution→impl traceability) | S6/S7 feed governance reconciliation | reuse |
| **Digital Twin** | `00-BOOK/DATA/control-tower.json` + connectors | S8/S9 read twin lifecycle dimensions as evidence | reuse (read) |
| **Repository registration** | `register.sh --guard` | S0 registers ratified outputs; guard proves zero drift | reuse (sole writer) |
| **UKB** | `ukb build/validate/trace/stats` | S0 authoritative engine | reuse |
| **Traceability** | `MCP-006` spine | S5 records closure edges only when evidence exists | reuse |
| **Release / Freeze** | `CEP-007` freeze | freeze the closure-capability spec once certified | reuse |

## 2. Ordering relative to the canonical spine (MCP-006)

The pipeline sits **before** Registration and **feeds** the Vision→…→Certification spine; it never replaces a spine tier:

```
Vision → Conversation → Uploaded Source → Decision → Constitution → Architecture →
Specification → [EKI reconciliation: S1–S7 evidence] → Repository Home → Implementation →
Validation (CEP-004) → Certification (CEP-005/CCE) → Evidence (CEP-008) → Registry (register.sh) → Closure (19)
```

## 3. What the pipeline explicitly does NOT add

- No second commit hook framework (reuses `scripts/install-hooks.sh`).
- No second CI system (reuses `.github/workflows/*`).
- No second validator/certifier (reuses CEP-004/005 + CCE).
- No second registration/drift mechanism (reuses `register.sh --guard`).
- No second traceability graph (reuses MCP-006 + `relationships.json`).

---

*END — 51 · Lifecycle Integration · AUTHORITY = NONE.*
