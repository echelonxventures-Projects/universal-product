# 16 — Quality Model

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define two distinct notions of quality, and keep them strictly separated:
1. **Quality *of* UMA** — the correctness/quality attributes the platform itself must satisfy.
2. **Quality *measured by* UMA** — the registered Quality metrics UMA computes over the repository (metric 3.12).

## 1. Quality *of* UMA (platform quality attributes)

| Attribute | Definition | Verification |
|---|---|---|
| Determinism | identical inputs ⇒ identical results | replay equality (doc 12, CI) |
| Reproducibility | any party reproduces a sealed result | `ReplayResult` (doc 09) |
| Idempotence | re-runs cause no source side-effects | source read-only proof (doc 15) |
| Completeness-honesty | never reports OK while blind | UNCOVERED forces PARTIAL (doc 08) |
| Traceability | every value → manifest → evidence | provenance chain (doc 11) |
| Agnosticism | no coupling to repo/lang/DB/cloud | contract-only design (docs 02, 11) |
| Extensibility | growth by registration, not code | evolution model (doc 14) |

These are the platform's own acceptance criteria; doc 20 audits them at the design level.

## 2. Quality *measured by* UMA (the Quality domain, metric 3.12)

UMA computes repository quality only through **registered, deterministic quality checks** — never subjective judgment. Each check is a Metric Definition (doc 04):

| Quality check (illustrative) | Formula sketch | Status semantics |
|---|---|---|
| Home resolvability | homed ÷ known | PARTIAL if any unhomed |
| Traceability density | resolved edges ÷ required edges | PARTIAL below threshold |
| Evidence backing | entities-with-evidence ÷ entities | PARTIAL if any unbacked |
| Naming conformance | IDs matching a registered family ÷ ID-shaped tokens | PARTIAL for UNCOVERED-IDENTIFIER |
| Disposition completeness | entities-with-disposition ÷ entities | PARTIAL if any UNKNOWN |
| Duplicate-home freedom | boolean (Knowledge Once) | FAIL if duplicates |

**Quality is measurable structure, not opinion.** Any check that cannot be computed deterministically from evidence is inadmissible.

## 3. Quality Index Composition

The Quality Index (3.12) is a registered weighted composite of admitted checks. Rules:
- weights are governed data (doc 13), versioned;
- the index is at best the weakest admissible input if any input is PARTIAL/UNKNOWN (fail-closed roll-up);
- the index cites every constituent check's evidence (no opaque score).

## 4. Thresholds & Gates

- Thresholds are registered, versioned data — not hard-coded. A consumer (e.g., Certification) chooses which threshold/gate to apply to a metric; UMA supplies the value and the threshold record, never the pass/fail decision.
- This preserves Analysis ≠ Authority: UMA measures quality; the consumer decides acceptability.

## 5. Quality Assurance of Metric Definitions

Every registered metric must ship with:
- positive/negative test vectors (like identifier families, doc 06);
- a determinism proof (PURE class);
- an evidence specification.
A metric definition lacking these is rejected at registration — quality is enforced at the control plane, before any measurement runs.

## 6. Continuous Quality Verification

- Replay-equality and metric test-vector checks run in CI (extending `determinism.yml`, D-12).
- Quality regressions in UMA itself (e.g., a metric losing determinism) fail the pipeline fail-closed.

## 7. Dependency Determination

- Existing validation/certification *decision* authority (CLOSURE-004) **RETAINS** the right to set gates and decide acceptability; it now reads UMA quality values + threshold records. Quality *measurement* **TRANSFERS** to UMA (metric 3.12). No frozen quality decision authority modified.

*END — 16 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
