# 08 — IMPLEMENTATION READINESS MATRIX

> **Mission:** IMG-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. Each object is assigned **exactly one** readiness state by the deterministic precedence rule below, with constitutional justification.

---

## 1. Readiness states & deterministic assignment rule

Precedence (first match wins):

1. **NOT REQUIRED** — canonical home is `.../03-IDENTIFIER-FAMILY-CATALOG.md` (family-taxonomy sentinel; no implementable artifact).
2. **GENERATED** — the object is produced by the engine/factory pipeline: a generative ARCH root `{ARCH-API-001, ARCH-EVENT-001, ARCH-WORKFLOW-001, ARCH-RUNTIME-001}` **or** a realization-span family `{DATA, SERVICE, APPLICATION, INFRASTRUCTURE, RUNTIME}` (non-sentinel).
3. **READY** — no predecessor layer (Wave-01 Constitution).
4. **BLOCKED** — predecessor layer not yet realized (Waves 2–4 hand-authored objects).
5. **DEFERRED** — authorization-gated. *(none among the 90 SPECIFIED — the 23 DEFERRED are a separate disposition, out of scope.)*
6. **DERIVED** — pure derivative of another CKO. *(none assertable — `closure.json` carries no derivation edges; declared 0 rather than inferred.)*

---

## 2. Readiness distribution

| State | Count | % of 90 |
|---|---|---|
| READY | 20 | 22.2% |
| BLOCKED | 45 | 50.0% |
| GENERATED | 12 | 13.3% |
| NOT REQUIRED | 13 | 14.4% |
| DEFERRED | 0 | 0% |
| DERIVED | 0 | 0% |

Executable (READY + BLOCKED + GENERATED) = **77**. Non-executable (NOT REQUIRED) = **13**.

---

## 3. State × Wave matrix

| Wave | READY | BLOCKED | GENERATED | NOT REQUIRED | Total |
|---|---|---|---|---|---|
| Wave-01 | 20 | 0 | 0 | 0 | 20 |
| Wave-02 | 0 | 10 | 4 | 1 | 15 |
| Wave-03 | 0 | 25 | 0 | 7 | 32 |
| Wave-04 | 0 | 10 | 0 | 1 | 11 |
| Wave-05 | 0 | 0 | 8 | 4 | 12 |
| **Total** | **20** | **45** | **12** | **13** | **90** |

---

## 4. Constitutional justification per state

### READY (20) — Wave-01 LAW (Ω∞-001…020)
**Justification:** Constitution is the foundational layer; it has no predecessor. These objects are `homed`, carry specification (and mostly constitution) trace, and can be codified immediately. They are the **implementation roots** and the highest-leverage unblocking action.

### BLOCKED (45) — hand-authored objects in Waves 2–4
**Justification:** Each is gated on the completion of its immediately-lower constitutional layer (Architecture on Constitution; Governance on Architecture; Platform on Governance). The block is **structural / layer-ordering**, not a defect. Breakdown: ARCH 10, GOV 4, UCOS-GOV 3, UCOS-RECON 4, UCOS-RAT 1, PHASE 6, MCP 1, MEP 2, MCS 1, UCOS-COMP 3, PLATFORM 9, EC3-GATE 1.

### GENERATED (12) — factory-realized objects
**Justification:** Realized by the deterministic engine/factory pipeline rather than hand-authored. Members: Wave-02 generative roots `ARCH-API-001, ARCH-EVENT-001, ARCH-WORKFLOW-001, ARCH-RUNTIME-001`; Wave-05 realization span `APPLICATION-015/017/019/020, DATA-027, INFRASTRUCTURE-004, RUNTIME-000/020`. **Repository-Truth caveat:** realizers `event.py`, `workflow.py`, `runtime.py` are **absent** from `engine/factory/factories/`; those must be present for generation to run. `api.py` exists (scaffold) though `ARCH-API-001` is SPECIFIED.

### NOT REQUIRED (13) — family sentinels
**Justification:** Identifier-family catalog registrations (home = `03-IDENTIFIER-FAMILY-CATALOG.md`), representing the family root identifier, not a deliverable. No implementable artifact; specification-only trace. Members: `APPLICATION-000, ARCH-XXX-000, DATA-000, EPIC-XXX-000, INFRASTRUCTURE-000, MEP-00, PLATFORM-000, SERVICE-000, UCKO-XXX-000, UCOS-EXEC-000, UCOS-GOV-000, UCOS-RAT-000, UKDA-DEC-000`.

### DEFERRED (0) / DERIVED (0)
**Justification:** No SPECIFIED object carries a deferred flag (DEFERRED is a distinct disposition of 23 separate concepts, out of manifest scope). No derivation edges exist in `closure.json`; DERIVED is declared **0** rather than inferred, per the rule "do not infer work not supported by Repository Truth."

---

## 5. Per-object readiness matrix (90)

Legend: **R** READY · **B** BLOCKED · **G** GENERATED · **N** NOT REQUIRED.

| ID | Wave | State | Justification key |
|---|---|---|---|
| Ω∞-001…Ω∞-020 (20) | W1 | **R** | root layer, no predecessor |
| ARCH-API-001 | W2 | **G** | generative root (api.py scaffold present) |
| ARCH-EVENT-001 | W2 | **G** | generative root (event.py absent) |
| ARCH-WORKFLOW-001 | W2 | **G** | generative root (workflow.py absent) |
| ARCH-RUNTIME-001 | W2 | **G** | generative root (runtime.py absent) |
| ARCH-AI-001 | W2 | **B** | gated on W1 |
| ARCH-BCDR-001 | W2 | **B** | gated on W1 |
| ARCH-CERT-001 | W2 | **B** | gated on W1 |
| ARCH-GAP-001 | W2 | **B** | gated on W1 |
| ARCH-INFRA-001 | W2 | **B** | gated on W1 |
| ARCH-INTEGRATION-001 | W2 | **B** | gated on W1 |
| ARCH-MASTER-001 | W2 | **B** | gated on W1 |
| ARCH-OBS-001 | W2 | **B** | gated on W1 |
| ARCH-QUALITY-001 | W2 | **B** | gated on W1 |
| ARCH-TEST-001 | W2 | **B** | gated on W1 |
| ARCH-XXX-000 | W2 | **N** | family sentinel |
| EPIC-XXX-000 | W3 | **N** | family sentinel |
| GOV-007 / GOV-008 / GOV-009 / GOV-010 | W3 | **B** | gated on W2 |
| MCP-000 | W3 | **B** | gated on W2 |
| MCS-000 | W3 | **B** | gated on W2 |
| MEP-00 | W3 | **N** | family sentinel |
| MEP-06 / MEP-08 | W3 | **B** | gated on W2 |
| Phase-001 / -002 / -003 / -020 / -024 / -025 | W3 | **B** | gated on W2 |
| UCKO-XXX-000 | W3 | **N** | family sentinel |
| UCOS-COMP-001000 / -001010 / -009010 | W3 | **B** | gated on W2 |
| UCOS-EXEC-000 | W3 | **N** | family sentinel |
| UCOS-GOV-000 | W3 | **N** | family sentinel |
| UCOS-GOV-001 / -003 / -005 | W3 | **B** | gated on W2 |
| UCOS-RAT-000 | W3 | **N** | family sentinel |
| UCOS-RAT-001 | W3 | **B** | gated on W2 (finality external — DR-RAT-11) |
| UCOS-RECON-0000 / -0001 / -001 / -C1 | W3 | **B** | gated on W2 |
| UKDA-DEC-000 | W3 | **N** | family sentinel |
| EC-3-AP-1 | W4 | **B** | gated on W3 |
| PLATFORM-000 | W4 | **N** | family sentinel |
| PLATFORM-003 / -004 / -007 / -013 / -014 / -015 / -016 / -017 / -018 | W4 | **B** | gated on W3 |
| APPLICATION-000 | W5 | **N** | family sentinel |
| APPLICATION-015 / -017 / -019 / -020 | W5 | **G** | realization span (application.py present) |
| DATA-000 | W5 | **N** | family sentinel |
| DATA-027 | W5 | **G** | realization span (data.py present) |
| INFRASTRUCTURE-000 | W5 | **N** | family sentinel |
| INFRASTRUCTURE-004 | W5 | **G** | realization span |
| RUNTIME-000 / RUNTIME-020 | W5 | **G** | realization span (runtime.py absent) |
| SERVICE-000 | W5 | **N** | family sentinel |

---

## 6. Determinism attestation

Every readiness value is a pure function of `(family, canonical home, wave)` from `closure.json` under the §1 precedence rule. Reproducible; no manual assignment.

---
*End of 08-IMPLEMENTATION-READINESS-MATRIX.md*
