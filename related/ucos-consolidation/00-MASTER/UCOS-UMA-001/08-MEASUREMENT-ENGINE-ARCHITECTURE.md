# 08 — Measurement Engine Architecture

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define the **Measurement Engine** — the computation model that turns an Observation Set (doc 07) into constitutional metric values (doc 04), and specify the concrete constitutional metrics UMA must supply. The engine is a *metric interpreter*: it executes registered metric definitions; it contains no hard-coded metric logic.

## 1. Engine Model

```
Observation Set ──┐
Upstream metrics ─┼──►  METRIC RESOLVER  ──►  MeasurementResult
Registry snapshot ┘        (interprets metric_id → formula → value)
```

- The engine is a **pure evaluator** of the Metric Definition Schema (doc 04 §1). Adding a metric = registering a definition, not editing the engine (mirrors registry-driven discovery).
- Metric composition is a **DAG**: metrics may depend on other metrics; the resolver topologically orders and memoizes them within a run.
- Every value is wrapped in the Result Envelope (doc 04 §5) with status, evidence, uncovered set, manifest, registry version, source-state hash.

## 2. Metric Status Algebra (fail-closed)

| Condition | Status |
|---|---|
| All dependencies resolved, zero uncovered in scope | `OK` |
| Value computable but uncovered set non-empty | `PARTIAL` |
| A required dependency/evidence missing | `UNKNOWN` |
| A declared failure condition triggered | `FAIL` |

`PARTIAL`/`UNKNOWN`/`FAIL` can never be silently promoted to `OK`. A rolled-up domain metric is at best the *weakest* of its inputs.

## 3. Constitutional Metric Set (each defined per doc 04 §1)

Below, each metric names Purpose · Formula · Evidence · Authority(consumer) · Dependencies · Failure. (Authorship authority is always NONE.)

### 3.1 Repository Integrity Index
- **Purpose:** internal canonical correctness. **Formula:** boolean AND over {duplicate_homes=0, orphans=0, unhomed=0, content-hash-dupes=0}. **Evidence:** UKB registry + `closure.json`. **Consumer:** Closure/Governance. **Deps:** UKB read. **Failure:** any subcount > 0 → FAIL.

### 3.2 Repository Representation Coverage
- **Purpose:** every known entity has a locatable home. **Formula:** homed ÷ known. **Evidence:** Canonical Home Register. **Deps:** Discovery + UKB. **Failure:** any `homed=false` → PARTIAL.

### 3.3 Vision Assimilation Ratio
- **Purpose:** external knowledge assimilated into truth. **Formula:** assimilated ÷ discovered-external. **Evidence:** Observation Set vs UKB. **Consumer:** Closure (Domain B). **Failure:** conversation_only/upload_only > 0 → PARTIAL.

### 3.4 Coverage Ratio (generic)
- **Purpose:** measured/represented ÷ universe. **Formula:** |covered| ÷ (|covered| + |uncovered|). **Evidence:** Discovery ledger. **Failure:** any UNCOVERED → PARTIAL (never 1.0 while blind).

### 3.5 Completeness Index (per domain)
- **Purpose:** domain fully represented, no UNKNOWN. **Formula:** entities-with-disposition ÷ entities. **Evidence:** Ontology + Coverage. **Failure:** any UNKNOWN status → PARTIAL.

### 3.6 Discovery Completeness
- **Purpose:** can the apparatus enumerate the universe? **Formula:** registered-namespaces ⊇ observed-namespaces ∧ zero UNCOVERED-*. **Evidence:** Namespace/Identifier registries vs ledger. **Failure:** any UNCOVERED-NAMESPACE/IDENTIFIER/SOURCE → FAIL. *(This is exactly the metric CLOSURE-007 reported FAIL.)*

### 3.7 Enumeration Completeness
- **Purpose:** complete listing of a defined set. **Formula:** counted ÷ expected (from registry). **Failure:** mismatch → PARTIAL.

### 3.8 Governance Posture Metric
- **Purpose:** authority uniqueness + freeze integrity. **Formula:** boolean AND over {single_authority, single_registry, freeze_intact}. **Evidence:** registry + governance state. **Consumer:** Governance. **Failure:** competing authority → FAIL.

### 3.9 Validation Coverage
- **Purpose:** coverage basis for validation. **Formula:** validated-entities ÷ entities-in-scope. **Consumer:** Validation authority. **Failure:** unvalidated in scope → PARTIAL.

### 3.10 Certification Metric Bundle
- **Purpose:** metric set a certificate consumes. **Formula:** composite of 3.1–3.9. **Consumer:** Certification authority. **Failure:** any input not OK → bundle not clean.

### 3.11 Evolution Delta
- **Purpose:** change of measured state across baselines. **Formula:** metric(baselineₙ) − metric(baselineₙ₋₁). **Evidence:** two sealed results. **Failure:** missing prior baseline → UNKNOWN.

### 3.12 Quality Index
- **Purpose:** measurable structural quality. **Formula:** weighted registered quality checks (doc 16). **Failure:** below registered threshold → PARTIAL.

### 3.13 Knowledge Once Metric
- **Purpose:** no duplicated canonical home. **Formula:** duplicate_canonical_homes = 0 (boolean). **Evidence:** UKB. **Failure:** >0 → FAIL.

### 3.14 Repository Truth Uniqueness
- **Purpose:** exactly one truth authority. **Formula:** count(truth_authorities)=1 ∧ derived-tools-are-derived. **Evidence:** governance registry. **Failure:** ≠1 → FAIL.

## 4. Determinism Guarantees

- Engine execution is pure over `(observations, upstream metrics, registry snapshot, manifest)`.
- Memoization is by content key; no run reads another run's mutable state.
- No metric may be `authority = UMA` (UMA computes; consumers decide) — enforced at registration.

## 5. Extensibility

New metrics, new domains, and new quality checks are added by **registering definitions** (doc 13 governs). The engine binary/logic is stable across metric growth — the CLOSURE-era pattern of "new measurement ⇒ new engine code" is eliminated.

## 6. Dependency Determination

- The measurement-*production* role currently embedded in `closure_engine.py` / `phase2_engine.py` / `phase3_engine.py` **TRANSFERS** to this engine. Those engines' *determination* roles (asserting CLOSED/NOT-CLOSED) **REMAIN** with Closure, now consuming UMA metrics as inputs. Final in doc 20.

*END — 08 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
