# EPIC-006 — Factory Layer — Completion Report

**Program:** EC-1 Execution Engine · **Epic:** EPIC-006 (Factory Layer)
**Scope executed:** TASK-000038 · TASK-000039 · TASK-000040 · TASK-000041 ·
TASK-000042 · TASK-000043 · TASK-000044 · TASK-000045 (inclusive)
**Authoritative basis:** EC-1 Master Implementation Program; IMP-000017 (UCOS Ω∞ —
Universal Compiler / IMP-007), **§8 Runtime Assembly** and **§2 blueprint
families**; Technology Constitution (TP-01 no invention, AR-03/PL-05 contracts,
DP-03 frozen corpus, DE-05 disclosure, IMP-007 §5 determinism). Builds on completed
EPIC-001…EPIC-005.
**Status:** ✅ COMPLETE — all eight tasks delivered, verified, and gated.

> Additive engineering package `engine/factory/`. No architecture change, no
> redesign, no modification of completed EPIC artifacts, no writes to the certified
> corpus. Reuses the RegistryAdapter, Compiler pipeline, and Runtime Assembly APIs
> verbatim. **A blueprint-type-independent generation model that orchestrates the
> existing subsystems from registry metadata alone.**

---

## 1. Objective & constraints — conformance

The Factory Layer **SHALL NOT** — verified:

| Prohibition | How prevented | Evidence |
|-------------|---------------|----------|
| bypass RegistryAdapter | all registry access is via `RegistryAdapter` (classification lookup + compiler validation) | `orchestrator.py` |
| bypass certification checks | compilation runs the certified compiler pipeline unchanged; its certification gate is authoritative | `orchestrator._compile` |
| write to frozen corpus | writes only to caller `output_dir`; frozen-path guard clean over the change set | §5 |
| hard-coded blueprint logic | classification is a vocabulary lookup; factories declare only class + capability | `classifier.py`, `factories/` |
| special-case execution paths | every factory delegates to the one `orchestrator.execute` path | `factories/base.py` |

The Factory Layer **SHALL** — verified:

| Requirement | How satisfied |
|-------------|---------------|
| use registry metadata | `resolve_blueprint_class` reads declared/registry metadata; orchestrator prefers a registered `Artifact` when present |
| use blueprint classifications | routing keys on `BlueprintFamily` (the closed §2 vocabulary) |
| use blueprint capabilities | `FactoryCapability` is registered and discoverable (`FactoryRegistry.capabilities`) |
| remain fully deterministic | no timestamps/ambient state; sorted ordering; identical inputs ⇒ identical outputs (§6) |
| remain additive | new package only; nothing existing altered |

---

## 2. Task-by-task delivery

| Task | Deliverable | Module |
|------|-------------|--------|
| **TASK-000038** | Factory contracts — `FactoryRequest`, `FactoryResult`, `FactoryCapability`, `FactoryDescriptor`: immutable, typed, deterministic, serializable, no runtime state | `contracts.py` |
| **TASK-000039** | Blueprint classification — `resolve_blueprint_class(metadata) -> BlueprintClassification` derives the class from registry/blueprint metadata (family field → id prefix → category → tags) across all six families; no hard-coded routing | `classifier.py` |
| **TASK-000040** | Factory registry — `FactoryRegistry.register_factory` / `resolve_factory` / `list_factories` (+ `capabilities`): deterministic ordering, immutable records, duplicate protection, capability discovery, no dynamic imports | `registry.py` |
| **TASK-000041** | Generation orchestrator — `GenerationOrchestrator`: resolve blueprint → classify → resolve factory → compiler pipeline → runtime assembly → `FactoryResult`; uses RegistryAdapter + Compiler + Runtime; provider-injected (no filesystem scanning) | `orchestrator.py` |
| **TASK-000042** | Factory implementations — `DataFactory`, `ApiFactory`, `ServiceFactory`, `ApplicationFactory` on a common `BaseFactory` contract, all reusing the single orchestrator execution path (no duplicated pipeline logic) | `factories/` |
| **TASK-000043** | Factory evidence — `GenerationEvidence` / `build_generation_evidence`: blueprint, classification, compiler artifact, runtime artifact, dependency closure, disclosure state; deterministic | `evidence.py` |
| **TASK-000044** | Multi-blueprint execution — `generate_many`: deterministic ordering (by blueprint id), one result per blueprint, identical inputs ⇒ identical outputs | `batch.py` |
| **TASK-000045** | Factory test suite — classification, registry, orchestrator, evidence, batch tests; 100% coverage of `engine/factory`; validates BP-DATA / BP-API / BP-SERVICE / BP-APPLICATION with real artifacts where practical | `engine/tests/factory/` |

---

## 3. Design — a reusable, honest, type-independent factory

The layer is **one execution path** driven by **metadata**:

```
generate(request)
  ├─ provider.get(blueprint_id)                 # injected provider — no fs scan
  ├─ classify(metadata)                          # registry Artifact if registered, else the document
  ├─ registry.resolve_factory(classification)    # BlueprintFamily → factory (deterministic)
  └─ factory.generate(context, execution=self)   # every factory delegates to ↓
        orchestrator.execute(context)            # THE single compile + assemble path
          ├─ CompilerPipeline.compile_one(...)   # EPIC-003, certified + family-gated
          ├─ assemble / descriptor / rollback    # EPIC-005 runtime assembly
          └─ build_generation_evidence(...)      # deterministic evidence record
```

Because the compiler currently implements **BP-DATA** end-to-end (`SUPPORTED_FAMILIES`),
a BP-DATA request produces **real** compiler + runtime artifacts. A BP-API /
BP-SERVICE / BP-APPLICATION request is classified and routed through the **same**
path, but the compiler's own family gate defers it, so the orchestrator returns a
**faithful `gap`** carrying the compiler's Gap Report — **no artifact is invented**
(TP-01) and there is **no special-case route**. As downstream compiler families are
implemented in later epics, those same factories begin producing real artifacts
with **zero change** to the Factory Layer.

---

## 4. Created directories & files

```
engine/factory/                              (NEW package)
├── __init__.py                              public API surface
├── errors.py                                TASK-000038  factory error taxonomy (FAC-*)
├── contracts.py                             TASK-000038  FactoryRequest/Result/Capability/Descriptor
├── classifier.py                            TASK-000039  resolve_blueprint_class
├── registry.py                              TASK-000040  FactoryRegistry
├── orchestrator.py                          TASK-000041  GenerationOrchestrator (single execution path)
├── evidence.py                              TASK-000043  GenerationEvidence
├── batch.py                                 TASK-000044  generate_many
├── factories/                               TASK-000042
│   ├── __init__.py                          build_default_registry (explicit, no dynamic imports)
│   ├── base.py                              common Factory contract + BaseFactory + execution plumbing
│   ├── data.py / api.py / service.py / application.py
└── EPIC-006-COMPLETION-REPORT.md            this report

engine/tests/factory/                        (NEW test package)
├── __init__.py · conftest.py                in-memory provider + multi-class blueprint fixtures
├── test_contracts.py · test_classifier.py · test_registry.py
├── test_orchestrator.py · test_evidence.py · test_batch.py

pyproject.toml                               (MODIFIED) coverage scope += engine.factory
```

No file under `00-BOOK/`, `00-SOURCE/`, or `99-FREEZE/` was created or modified.

---

## 5. Verification evidence

Commands run in the pinned dev environment (`.ec1-venv`, target Python 3.12+):

**Lint (ruff):** `ruff check engine` → **All checks passed!**

**Tests + coverage gate (`--cov-fail-under=90`):**
```
394 passed
Required test coverage of 90% reached. Total coverage: 99.64%

engine/factory/__init__.py               100%
engine/factory/batch.py                  100%
engine/factory/classifier.py             100%
engine/factory/contracts.py              100%
engine/factory/errors.py                 100%
engine/factory/evidence.py               100%
engine/factory/factories/__init__.py     100%
engine/factory/factories/base.py         100%
engine/factory/factories/api.py          100%
engine/factory/factories/application.py  100%
engine/factory/factories/data.py         100%
engine/factory/factories/service.py      100%
engine/factory/orchestrator.py           100%
engine/factory/registry.py               100%
```
**100% coverage on every `engine/factory` module** (coverage target met).

**Build:** `python -m build` → wheel + sdist built; all **14** `engine/factory/**`
modules packaged.

**Frozen-path guard (DP-03)** over the EPIC-006 change set: exit 0 (clean).

---

## 6. Factory execution & determinism evidence

Generated end to end against the **real, certified `00-BOOK` registry**.

**Factory registry (deterministic ordering + capability discovery):**
```
BP-API           -> api-factory          stages=(classify, compile, assemble, deploy, evidence)
BP-APPLICATION   -> application-factory   stages=(classify, compile, assemble, deploy, evidence)
BP-DATA          -> data-factory          stages=(classify, compile, assemble, deploy, evidence)
BP-SERVICE       -> service-factory       stages=(classify, compile, assemble, deploy, evidence)
```

**Batch generation (deterministic order by blueprint id):**
```
BP-API-0001          class=BP-API          factory=api-factory          status=gap        success=False
BP-APPLICATION-0001  class=BP-APPLICATION  factory=application-factory  status=gap        success=False
BP-DATA-0001         class=BP-DATA         factory=data-factory         status=generated  success=True
BP-SERVICE-0001      class=BP-SERVICE      factory=service-factory      status=gap        success=False
```

**BP-DATA generation evidence (real artifacts):**
```
compiler_artifact : UCOS-CMP-BP-DATA-0001-5cdc24681ea75f46
package_sha256    : 0a7ae17b8ec02f980dd4977d1d339a2d1bb2bc04f3f27d900a9bf3c5046f2cac
runtime_artifact  : UCOS-RUN-BP-DATA-0001-5f58a290a1bc2c18
image_reference   : ucos-runtime/bp-data-0001@sha256:0a7ae17b8...
dependency_closure: [BP-DATA-0001 (root)]
disclosure_state  : EC-1-PROVISIONAL-STATE present, gate EC-1, asserts_constitutional_finality=false
```
(Identical to the EPIC-005 ids — determinism holds across epics.)

**BP-API faithful gap (no invented artifact):**
```
status = gap · success = false · compiler_artifact = null
gap    = { stage: parse, code: CMP-PARSE-001,
           message: "blueprint family is not compilable in EPIC-003 (BP-DATA only)",
           context: { family: BP-API, supported: [BP-DATA] } }
```

**Determinism:** two independent runs, with reversed input ordering, produced
**byte-identical** result tuples (`identical outputs = True`).

---

## 7. Acceptance criteria matrix

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| A1 | Factory contracts implemented | ✅ | `contracts.py`; `test_contracts.py` |
| A2 | Blueprint classification resolution operational | ✅ | `classifier.py`; §6; `test_classifier.py` |
| A3 | Factory registry operational | ✅ | `registry.py`; §6; `test_registry.py` |
| A4 | Generation orchestrator operational | ✅ | `orchestrator.py`; §6; `test_orchestrator.py` |
| A5 | Multiple factory types operational | ✅ | 4 factories routed for 4 classes; §6 |
| A6 | Generation evidence produced | ✅ | `evidence.py`; §6; `test_evidence.py` |
| A7 | Batch generation operational | ✅ | `batch.py`; §6; `test_batch.py` |
| A8 | Deterministic execution verified | ✅ | §6 (identical outputs, reversed input) |
| A9 | All tests passing | ✅ | 394 passed; 100% factory coverage |
| A10 | Factory Layer completion report produced | ✅ | this document |

---

## 8. Success criterion

Proven: **the compiler/runtime pipeline is now a reusable, blueprint-type-independent
Factory Layer.** Generation is orchestrated for multiple blueprint classes from
registry metadata alone — no RegistryAdapter bypass, no certification bypass, no
frozen-corpus write, no hard-coded blueprint logic, no special-case paths — fully
deterministically, producing real artifacts for supported classes and faithful
gaps (never invention) for classes the compiler defers.

**STOP — EPIC-006 complete. TASK-000038…TASK-000045 delivered. EPIC-007 (and
later) not begun.**
