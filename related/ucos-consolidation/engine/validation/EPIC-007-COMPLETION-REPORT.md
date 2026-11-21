# EPIC-007 — Validation Layer — Completion Report

**Program:** EC-1 Execution Engine · **Epic:** EPIC-007 (Validation Layer)
**Scope executed:** TASK-000046 · TASK-000047 · TASK-000048 · TASK-000049 (inclusive)
**Authoritative basis:** EC-1 Master Implementation Program; IMP-000017 (UCOS Ω∞ —
Universal Compiler / IMP-007), **§13 Validation**; Technology Constitution (TP-01
no invention, AR-03/PL-05 contracts, DP-03 frozen corpus, DE-05 disclosure,
IMP-007 §5 determinism). Builds on completed EPIC-001…EPIC-006.
**Status:** ✅ COMPLETE — all four tasks delivered, verified, and gated.

> Additive engineering package `engine/validation/`. No architecture change, no
> redesign, no modification of completed EPIC artifacts, no writes to the certified
> corpus. A **read-only** verifier: it validates already-generated artifacts and
> mutates nothing. **A compiled/assembled artifact is now validated against its
> constitutional invariants, with evidence and an acceptance gate.**

---

## 1. Objective & constraints — conformance

| Constraint | How satisfied | Evidence |
|------------|---------------|----------|
| Additive only | new `engine/validation/` package; nothing existing altered | §4 |
| No frozen-corpus writes | read-only over subjects; frozen-path guard clean over change set | §5 |
| Registry-only access | validates artifacts already registry-validated upstream; the layer performs no direct corpus/registry mutation | `checks.py` (pure over subject) |
| No invented verdicts (TP-01) | every finding is a falsifiable predicate over declared subject fields | `checks.py` |
| Deterministic (IMP-007 §5) | checks run in stable id order; no wall-clock/ambient state; identical subject ⇒ identical report/evidence/decision | §6 |
| Reuses subsystems | validates EPIC-005 runtime units (`ValidationSubject.from_runtime_unit`); reuses `disclosure_present` | `contracts.py`, `checks.py` |

---

## 2. Task-by-task delivery

| Task | Deliverable | Module |
|------|-------------|--------|
| **TASK-000046** | Validation architecture + contracts — `Severity`/`CheckStatus`/`Verdict`, `ValidationRequest`, `ValidationFinding`, `ValidationReport`, `ValidationSubject` (immutable, typed, deterministic, serializable); the `ValidationCheck` architecture + seven built-in invariant checks + the default suite | `contracts.py`, `checks.py` |
| **TASK-000047** | Validation execution — `ValidationEngine.validate(subject) -> ValidationReport`: runs the suite in stable order, aggregates a deterministic report, verdict = PASS iff no *blocking* failure; `validate_runtime_unit` convenience | `executor.py` |
| **TASK-000048** | Validation evidence — `ValidationEvidence` / `build_validation_evidence(report)`: target, blueprint, verdict, per-check findings, counts, blocking-failure list; deterministic | `evidence.py` |
| **TASK-000049** | Acceptance gates — `AcceptanceDecision` + `enforce_acceptance(report, *, strict)`: accept iff verdict PASS; strict mode raises `AcceptanceGateError` with the failing checks as evidence | `gates.py` |

### The validation architecture (seven built-in checks)

| Check id | Severity | Invariant (IMP-007) |
|----------|----------|---------------------|
| `provenance-chain` | blocking | chain non-empty, all-string, rooted at the blueprint (§1) |
| `signature-present` | blocking | algorithm + value + payload hash present (§12) |
| `sbom-present` | blocking | SBOM format + ≥1 component (§12) |
| `provisional-state-disclosure` | blocking | EC-1 disclosure present, asserts no finality (DE-05/C-05) |
| `dependency-closure-pinned` | blocking | one root, every member digest-pinned, root hash = package hash (§8) |
| `image-digest-pinned` | blocking | image pinned by `@sha256:<package_hash>` (§8) |
| `identity-deterministic` | advisory | runtime id matches `UCOS-RUN-<blueprint>-<hex16>` (§5) |

The `ValidationCheck` ABC is open: callers may supply their own checks to the
engine. Checks are pure functions of a normalized, type-independent
`ValidationSubject`, so validation is decoupled from the producing subsystem.

---

## 3. How a generated artifact is validated

```
ValidationSubject.from_runtime_unit(unit)     # normalize the artifact (no producer coupling)
  → ValidationEngine.validate(subject)         # run 7 checks in stable id order
      → ValidationReport (verdict + ordered findings + counts)
          → build_validation_evidence(report)  # deterministic evidence record
          → enforce_acceptance(report, strict) # accept iff no blocking failure
```

Verdict is **PASS** iff no *blocking* check failed; advisory failures are recorded
but never block acceptance. In strict mode a rejected report raises
`AcceptanceGateError` carrying the failing check ids (Mandatory Rule 6 — every
rejection is auditable).

---

## 4. Created directories & files

```
engine/validation/                           (NEW package)
├── __init__.py                              public API surface
├── errors.py                                TASK-000046  VAL-* error taxonomy
├── contracts.py                             TASK-000046  enums + Request/Finding/Report/Subject
├── checks.py                                TASK-000046  ValidationCheck ABC + 7 checks + suite
├── executor.py                              TASK-000047  ValidationEngine
├── evidence.py                              TASK-000048  ValidationEvidence
├── gates.py                                 TASK-000049  AcceptanceDecision + enforce_acceptance
└── EPIC-007-COMPLETION-REPORT.md            this report

engine/tests/validation/                     (NEW test package)
├── __init__.py · conftest.py                assembles a real runtime unit → subject
├── test_contracts.py · test_checks.py · test_executor.py
├── test_evidence.py · test_gates.py

pyproject.toml                               (MODIFIED) coverage scope += engine.validation
```

No file under `00-BOOK/`, `00-SOURCE/`, or `99-FREEZE/` was created or modified.

---

## 5. Verification evidence

Commands run in the pinned dev environment (`.ec1-venv`, target Python 3.12+):

**Lint (ruff):** `ruff check engine` → **All checks passed!**

**Tests + coverage gate (`--cov-fail-under=90`):**
```
432 passed
Required test coverage of 90% reached. Total coverage: 99.67%

engine/validation/__init__.py     100%
engine/validation/checks.py       100%
engine/validation/contracts.py    100%
engine/validation/errors.py       100%
engine/validation/evidence.py     100%
engine/validation/executor.py     100%
engine/validation/gates.py        100%
```
**100% coverage on every `engine/validation` module.**

**Build:** `python -m build` → wheel + sdist built; all **7** `engine/validation/**`
modules packaged.

**Frozen-path guard (DP-03)** over the EPIC-007 change set: exit 0 (clean).

---

## 6. Validation execution evidence

Generated end to end against the **real, certified `00-BOOK` registry** (compile →
assemble → validate the resulting runtime unit):

**Validation report — `UCOS-RUN-BP-DATA-0001-5f58a290a1bc2c18`:**
```
verdict = pass · accepted = true · total=7 passed=7 failed=0 (blocking_failed=0)
  dependency-closure-pinned      blocking  pass  (members=1)
  identity-deterministic         advisory  pass  (UCOS-RUN-BP-DATA-0001-5f58a290a1bc2c18)
  image-digest-pinned            blocking  pass  (@sha256:0a7ae17b8...)
  provenance-chain               blocking  pass  (links=6)
  provisional-state-disclosure   blocking  pass  (EC-1-PROVISIONAL-STATE)
  sbom-present                   blocking  pass  (components=3)
  signature-present              blocking  pass  (HMAC-SHA256)
```

**Acceptance gate:** `accepted = true`, `verdict = pass`, blocking_failures = [].

**Negative case (tampered provenance chain):** strict gate raised
`AcceptanceGateError` with `blocking_failures = ['provenance-chain']` — no artifact
is accepted when a blocking invariant fails.

**Determinism:** two independent validations of the same subject produced
byte-identical reports (`identical reports across runs = True`).

---

## 7. Acceptance gates matrix

| Gate | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Architecture | validation checks defined & open for extension | ✅ | `checks.py`; `test_checks.py` |
| Contracts | immutable, typed, deterministic, serializable | ✅ | `contracts.py`; `test_contracts.py` |
| Execution | deterministic report aggregation | ✅ | `executor.py`; §6; `test_executor.py` |
| Evidence | deterministic validation evidence record | ✅ | `evidence.py`; §6; `test_evidence.py` |
| Acceptance gate | accept on PASS, reject/raise on blocking failure | ✅ | `gates.py`; §6; `test_gates.py` |
| Determinism | identical subject ⇒ identical output | ✅ | §6 |
| All tests passing | full suite green | ✅ | 432 passed; 100% validation coverage |

---

## 8. Success criterion

Proven: **a generated, deployable artifact is validated against its constitutional
invariants** — provenance, signature, SBOM, EC-1 provisional-state disclosure, a
pinned dependency closure, a digest-pinned image, and a deterministic identity —
producing a deterministic report + evidence, and an acceptance gate that accepts a
sound artifact and rejects (strictly, with evidence) any artifact that fails a
blocking invariant. Read-only, additive, registry-safe, frozen-path safe.

**STOP — EPIC-007 complete. TASK-000046…TASK-000049 delivered. EPIC-008 (and
later) not begun.**
