# UAKOS-CLOSURE-004 — Validation · Evidence Collection · Certification (Program Charter · INITIALIZATION)

| Field | Value |
|-------|-------|
| STATUS | INITIALIZATION (planning only). If a canonical charter already exists, that one governs (Knowledge Once). |
| AUTHORITY | NONE — DERIVED TRUTH. |
| BASELINE | HEAD `b67a720` |
| PREDECESSOR | `UAKOS-CLOSURE-002` (FROZEN); depends on `UAKOS-CLOSURE-003` outputs. |
| STATUS | INITIALIZED — not started. |

## 1. Mission

Validate the enrichments executed by `UAKOS-CLOSURE-003`, collect physical evidence, and execute certification — reusing existing governance, never implementing.

## 2. Responsibilities

- **Validate** executed enrichments: `CEP-004` + `verify.sh` + `ukb validate` (install `jsonschema` to lift the structural-only caveat, AB-5).
- **Collect evidence** per `CEP-008`: traceability materialization (drive G-TR up), Digital Twin refresh (`ukbx ingest`), determinism proofs.
- **Certify**: `CEP-005` + CCE (`UCOS-COMP-000001`) ten-gate; record certifications; run `register.sh --guard` (zero drift).

## 3. Hard constraints (inherited guarantees, doc `67`)

- **Never** implement/enrich (that is -003).
- Reuse existing validators/certifiers/registries/traceability; introduce none.
- Fail-closed: no certification without complete, physically-present evidence (`TRACK-001`).

## 4. Inputs / Outputs

- **Inputs:** -003 enrichment outputs; `CEP-004/005/008`; CCE; Digital Twin.
- **Outputs:** validation reports, evidence bundles, certification records (via existing certification machinery).

## 5. Boundary

Validation/evidence/certification only. Drives quality gates G-TR/G-EV/G-VAL/G-CERT toward PASS (doc `54`); closure is *measured*, not declared.

---

*END — UAKOS-CLOSURE-004 Charter · INITIALIZATION · AUTHORITY = NONE.*
