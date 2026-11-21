# EPIC-VAL-002 — Universal Repository Acceptance Engine — Completion Report

**Program:** EC-1 Execution Engine · **Terminal:** T3 · **Epic:** EPIC-VAL-002
(Universal Repository Acceptance Engine)
**Authoritative basis:** EC-1 Master Implementation Program; IMP-000017 (UCOS Ω∞ —
Universal Compiler / IMP-007), **§13 Validation → §11 Evidence**; the acceptance
discipline of the certified corpus (record-only, evidence-backed, fail-closed,
non-constitutive — URS-L-20/21/25; OP-CERT-001 non-optimistic/fail-closed);
Technology Constitution (TP-01 no invention, TP-05 least-sufficient / reuse,
AR-03/PL-05 contracts, DP-03 frozen corpus, DE-04 pinned dependencies, DE-05
disclosure, IMP-007 §5 determinism). Builds on completed EPIC-001…EPIC-008.
**Status:** ✅ COMPLETE — the final Repository Acceptance Gate delivered, verified,
and gated.

> Additive engineering package `engine/acceptance/`. No architecture change, no
> redesign, no modification of completed EPIC artifacts, no writes to the certified
> corpus. The **final acceptance gate**: it assimilates the acceptance-relevant
> facts of an EPIC / feature / implementation / repository and **aggregates** them
> into a fail-closed acceptance determination — it re-judges no artifact and mutates
> nothing. **Nothing is accepted without this engine.**

---

## 1. Objective & constraints — conformance

| Constraint | How satisfied | Evidence |
|------------|---------------|----------|
| Additive only | new `engine/acceptance/` package; nothing existing altered | §4 |
| Fail closed | verdict is ACCEPTED iff **no blocking gate failed**; every built-in gate is blocking; strict mode raises `ACCEPT-REJECTED-001` | `engine.py`, `gates.py`; §6 |
| Deterministic outputs (IMP-007 §5) | gates run in stable id order; canonical hashing; no wall-clock/ambient state; identical subject ⇒ identical decision/certificate/evidence/readiness | §6 |
| Immutable acceptance certificate | frozen, content-addressed `AcceptanceRecord`; `content_sha256` covers the record core and derives `acceptance_id`; `verify_integrity()`/`require_integrity()` detect any mutation | `contracts.py`; §6 |
| No invented verdicts (TP-01) | every gate is a falsifiable predicate over a **normalized, assimilated subject**; acceptance aggregates the assimilated facts, adding no new judgment | `gates.py` |
| Reuse over reinvention (TP-05) | `content_hash`/`canonical_json`, disclosure, logging, and telemetry are reused from the existing layers; the reuse gate itself enforces the principle | `contracts.py`, `gates.py` |
| No frozen-corpus modification (DP-03) | read-only over an in-memory subject; only `engine/acceptance/**`, `engine/tests/acceptance/**`, and `pyproject.toml` coverage scope touched | §4 |
| Non-constitutive (DE-05 / IP-01) | every certificate + readiness report asserts `ENGINEERING-EXECUTION-ONLY` authority and carries the EC-1 provisional-state disclosure — acceptance records readiness, not finality | `contracts.py`, `readiness.py`, reuse of `runtime.disclosure` |

---

## 2. Deliverables

| Concern | Deliverable | Module |
|---------|-------------|--------|
| **Contracts** | `GateSeverity`/`GateStatus`/`AcceptanceStatus`; the normalized `RepositorySubject` (+ `UnitRecord`, `DependencyRecord`, `ReuseRecord`, `IntegrationRecord`, `RepositoryInventory`, `RepositoryHealth`, `CoverageDimension`/`CoverageProfile`); `AcceptanceFinding`; the **immutable, content-addressed** `AcceptanceRecord` (Repository Acceptance Certificate); `RepositorySubject.from_mapping` context-assimilation entry point | `contracts.py` |
| **Gates** | the `AcceptanceGate` architecture + **20 built-in gates** + the default suite (open for extension) | `gates.py` |
| **Decision** | `AcceptanceEngine.accept(subject) -> AcceptanceDecision`: runs the suite in stable order, aggregates a deterministic fail-closed decision, issues the immutable certificate; `accept_repository` + `enforce_acceptance` | `engine.py` |
| **Evidence** | `AcceptanceEvidence` / `build_acceptance_evidence(decision)`: identity, status, per-gate findings, counts, blocking/advisory lists, the reference to the reproducible subject digest, and the record content hash — closing the subject → decision → evidence chain | `evidence.py` |
| **Repository Readiness** | `RepositoryReadiness` / `build_repository_readiness(decision)`: the per-gate status map + the fail-closed **freeze verdict** (READY / NOT-READY), content-addressed, carrying authority + disclosure | `readiness.py` |
| **Errors** | `ACCEPT-*` taxonomy rooted in `FoundationError` | `errors.py` |

### The acceptance framework (20 built-in gates, all blocking)

| Gate id | Dimension validated |
|---------|---------------------|
| `context-assimilation` | acceptance context was assimilated |
| `repository-discovery` | at least one repository was discovered |
| `constitution-discovery` | the governing constitution was discovered |
| `ownership-resolved` | every unit has a resolved owner (no orphans) |
| `dependencies-resolved` | every dependency is resolved and pinned (DE-04) |
| `reuse-validated` | no unjustified duplicate capability (TP-05) |
| `implementation-complete` | units exist and every unit is implemented |
| `validation-passed` | every unit passed validation (EPIC-007) |
| `certification-passed` | every unit was certified (EPIC-008) |
| `registration-complete` | every unit was registered |
| `traceability-complete` | every unit covers requirement → certification |
| `coverage-complete` | 100% statements/branches/functions/public API/exception paths/repository |
| `zero-missing` | every expected artifact is present |
| `zero-duplication` | no artifact duplicated by id or content |
| `zero-overlap` | no responsibility owned by >1 artifact |
| `repository-reconciliation` | discovered artifacts reconcile with the declared inventory |
| `cross-epic-integration` | every cross-EPIC integration point is satisfied |
| `architecture-consistency` | no architecture-consistency violations |
| `repository-health` | no critical health issues |
| `freeze-readiness` | no outstanding freeze blockers |

The `AcceptanceGate` ABC is open: callers may supply their own gates (including
advisory ones) to the engine.

---

## 3. How a repository is accepted

```
RepositorySubject.from_mapping(facts)          # context assimilation of discovered facts
  → AcceptanceEngine.accept(subject)           # 20 gates in stable id order, fail-closed
      → AcceptanceDecision (status + ordered findings + immutable certificate)
          → build_acceptance_evidence(decision) # deterministic evidence, references subject digest
          → build_repository_readiness(decision)# freeze-readiness verdict (READY / NOT-READY)
  → enforce_acceptance(decision, strict=True)   # raises ACCEPT-REJECTED-001 on rejection
```

Status is **ACCEPTED** iff no *blocking* gate failed; advisory failures are recorded
but never block acceptance. The determination is **fail-closed and non-optimistic**
(OP-CERT-001): any unsatisfied dimension is REJECTED, never a pending pass. The
certificate is immutable and content-addressed, so any post-hoc mutation is detected
(`ACCEPT-INTEGRITY-001`).

---

## 4. Created directories & files

```
engine/acceptance/                           (NEW package)
├── __init__.py                              public API surface
├── errors.py                                ACCEPT-* error taxonomy
├── contracts.py                             enums + normalized subject + immutable certificate
├── gates.py                                 AcceptanceGate ABC + 20 gates + suite
├── engine.py                                AcceptanceEngine + AcceptanceDecision + enforce/accept
├── evidence.py                              AcceptanceEvidence
├── readiness.py                             RepositoryReadiness (freeze-readiness verdict)
└── EPIC-VAL-002-COMPLETION-REPORT.md        this report

engine/tests/acceptance/                     (NEW test package)
├── __init__.py · conftest.py                golden acceptable subject + mutate() helper
├── test_contracts.py · test_gates.py · test_engine.py
├── test_evidence.py · test_readiness.py

pyproject.toml                               (MODIFIED) coverage scope += engine.acceptance
```

No file under `00-BOOK/`, `00-SOURCE/`, or `99-FREEZE/` was created or modified.

---

## 5. Verification evidence

Commands run in the pinned dev environment (`.ec1-venv`, Python 3.12).

**Lint (ruff):** `ruff check engine/acceptance engine/tests/acceptance` → **All checks passed!**

**Acceptance suite + per-module coverage:**
```
63 passed
engine/acceptance/__init__.py     100%
engine/acceptance/contracts.py    100%
engine/acceptance/engine.py       100%
engine/acceptance/errors.py       100%
engine/acceptance/evidence.py     100%
engine/acceptance/gates.py        100%
engine/acceptance/readiness.py    100%
TOTAL                             100%  (588 stmts, 64 branches, 0 miss)
```
**100% statement + branch coverage on every `engine/acceptance` module.**

**Full engine + platform suite (`--cov-fail-under=90`):**
```
3172 passed
Required test coverage of 90% reached. Total coverage: 99.78%
```

---

## 6. Acceptance execution evidence

Generated end to end over a fully-assimilated repository subject
(assimilate → accept → evidence → readiness):

**Acceptance decision — `UCOS-ACCEPT-EPIC-VAL-002-813f161862a95f42`:**
```
repository_id        = UCOS-REPO-0001
epic_id              = EPIC-VAL-002
subject_digest       = 6ed5134c85af8466…
acceptance_id        = UCOS-ACCEPT-EPIC-VAL-002-813f161862a95f42
status               = accepted
record.content_sha256= 813f161862a95f42…
record.integrity     = true
gates total/passed   = 20 / 20   (blocking_failed = 0)
```

**Acceptance evidence:** `subject_ref = 6ed5134c85af8466…`, `record_sha256 =
813f161862a95f42…`, `evidence.content_sha256 = 7258fbcb4976124c…` — the
subject → decision → evidence chain is closed and reproducible.

**Repository readiness:** `verdict = READY`, `freeze_ready = true`,
`gates_passed = 20/20`, `readiness_sha256 = 65449d0c9ec0fdca…`.

**Determinism / reproducibility:** two independent acceptances of the same subject
produced byte-identical certificates (`content_sha256` equal ⇒ identical
`acceptance_id`).

**Negative case (freeze blocker present):** `status = rejected`,
`blocking_failures = ['freeze-readiness']`, `acceptance_id =
UCOS-ACCEPT-EPIC-VAL-002-02a5825814024f3b` — nothing is accepted while a required
dimension is unsatisfied (fail-closed).

**Negative case (tampered certificate):** mutating any field breaks the content
hash; `require_integrity()` raises `ACCEPT-INTEGRITY-001`.

---

## 7. Acceptance gates matrix

| Gate | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Architecture | acceptance gates defined & open for extension | ✅ | `gates.py`; `test_gates.py` |
| Contracts | immutable, typed, deterministic, serializable; content-addressed certificate | ✅ | `contracts.py`; `test_contracts.py` |
| Decision | deterministic, fail-closed decision + immutable certificate | ✅ | `engine.py`; §6; `test_engine.py` |
| Evidence | deterministic acceptance evidence, references subject digest | ✅ | `evidence.py`; §6; `test_evidence.py` |
| Repository readiness | freeze-readiness verdict; fail-closed | ✅ | `readiness.py`; §6; `test_readiness.py` |
| Coverage requirement | 100% statements/branches/functions/public API/exception paths/repository | ✅ | `coverage-complete` gate; §5 (100% module coverage) |
| Zero missing / duplication / overlap | inventory reconciliation gates | ✅ | `gates.py`; `test_gates.py` |
| Determinism / reproducibility | identical input ⇒ identical output | ✅ | §6 |
| All tests passing | full suite green | ✅ | 3172 passed; 100% acceptance coverage |

---

## 8. Success criterion

Proven: **an EPIC / feature / implementation / repository is accepted only through
this engine** — it assimilates the acceptance-relevant facts, runs the 20-gate
universal acceptance framework (re-judging nothing, TP-01), and produces a
deterministic, fail-closed decision, an **immutable, content-addressed** Repository
Acceptance Certificate, a reproducible acceptance evidence record that references the
assimilated subject digest, and a **Repository Readiness** freeze verdict. Coverage
is enforced at 100% across statements, branches, functions, public API, exception
paths, and the repository. Record-only, non-constitutive
(`ENGINEERING-EXECUTION-ONLY`, EC-1 disclosure carried), additive, and frozen-path
safe.

This engine records **engineering-execution readiness only**. It carries the EC-1
provisional-state disclosure and asserts **no constitutional finality, authority, or
ratification** (DE-05 / IP-01): the external gates (EC-1…EC-6) remain open.

**STOP — EPIC-VAL-002 complete. Universal Repository Acceptance Engine delivered.
Nothing is accepted without this engine.**
