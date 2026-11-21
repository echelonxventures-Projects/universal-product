# EPIC-005 — Runtime Assembly — Completion Report

**Program:** EC-1 Execution Engine · **Epic:** EPIC-005 (Runtime Assembly)
**Scope executed:** TASK-000034 · TASK-000035 · TASK-000036 · TASK-000037 (inclusive)
**Authoritative basis:** EC-1 Master Implementation Program; IMP-000017 (UCOS Ω∞ —
Universal Compiler / IMP-007), **§8 Runtime Assembly**; Technology Constitution
**DE-05** (Provisional-State Disclosure), **IP-08** (reversible deployments). Builds
on completed EPIC-001 (Foundation), EPIC-002 (Registry Adapter), EPIC-003 (Compiler
Core), EPIC-004 (Determinism Framework).
**Status:** ✅ COMPLETE — all four tasks delivered, verified, and gated.

> Additive engineering package `engine/runtime/`. No architecture change, no
> redesign, no writes to the certified corpus. Reuses the Foundation, Registry
> Adapter, Compiler (packaging/signing/publishing), and Determinism APIs verbatim.
> **A compiled artifact becomes a deployable, reversible runtime unit — with
> provenance, signature, SBOM, and provisional-state disclosure preserved.**

---

## 1. Objective & mandatory rules — conformance

| # | Mandatory rule | How satisfied | Evidence |
|---|----------------|---------------|----------|
| 1 | No architecture changes | Additive `engine/runtime/`; nothing existing altered | §4 inventory |
| 2 | No redesign | Reuses Compiler `Package`/`Signer`/`PublishedArtifact`, Foundation obs/config/guards | `assembly.py` imports |
| 3 | No modifications to certified corpus | Engine only **reads** published packages + writes to caller dirs; frozen-path guard clean over the change set | §5 |
| 4 | Reuse existing Foundation/Registry/Compiler APIs | `Signer.verify`, `_hash_manifest`, `PublishedArtifact`, `SecretRef`, telemetry/logging reused | `assembly.py`, `deploy.py` |
| 5 | Determinism preserved | Descriptor + `runtime_id` are deterministic (no timestamps, sorted); identical package ⇒ identical output | §6, `test_assembly_is_deterministic` |
| 6 | Every failure generates evidence | Structured, coded, non-secret errors (`RT-*`) with context at every gate | `errors.py` |
| 7 | No placeholders | Complete, executable implementation | §4 |
| 8 | No pseudocode | Production Python only | §4 |
| 9 | Production-quality only | Typed, immutable, structured errors, stdlib-only, ruff clean | §5 |
| 10 | Coverage ≥ 90% | **99.59% overall**; **100% on every `engine/runtime` module** | §5 |

---

## 2. Task-by-task delivery

| Task | Deliverable | Module |
|------|-------------|--------|
| **TASK-000034** | Runtime Assembly Engine — `assemble(package) -> RuntimeUnit`: consumes a published compiler package, resolves the pinned dependency closure, validates the provenance chain, verifies the signature, validates SBOM presence, binds secrets **by reference only**, and generates a **deterministic runtime descriptor** | `assembly.py` (+ `errors.py`) |
| **TASK-000035** | Deployment Descriptor + Rollback — `descriptor(unit) -> DeploymentDescriptor`, `rollback(unit) -> RollbackDescriptor`: Kubernetes manifests, deployment descriptor, **reversible checkpoint-based** rollback descriptor, dependency-closure record | `deploy.py` |
| **TASK-000036** | Provisional-State Disclosure — `inject_provisional_state(unit)`: the generated runtime carries the EC-1 disclosure (DE-05/C-05) and it **survives packaging and deployment generation** | `disclosure.py` |
| **TASK-000037** | Runtime Assembly Validation — assembly succeeds; deployment descriptors generated; rollback path generated; provenance preserved; signature verified; SBOM verified; disclosure present | `engine/tests/integration/test_runtime.py` (+ unit tests) |

### Required interfaces

- `assemble(package) -> RuntimeUnit` ✅
- `descriptor(unit) -> DeploymentDescriptor` ✅
- `rollback(unit) -> RollbackDescriptor` ✅
- `inject_provisional_state(unit)` ✅ (auto-invoked by `assemble`, idempotent)

---

## 3. How a compiled artifact becomes a deployable, reversible runtime unit

The engine composes IMP-007 §8 assembly over a published EPIC-003 package and
applies four hard gates **before** it emits anything:

- **Provenance gate (§1)** — the backward-traceability chain is extracted from the
  manifest, artifact record, **and** SBOM and must be byte-consistent across all
  three and originate at the blueprint id.
- **Signature gate (§12/§15)** — the package signature is re-verified with a
  caller-supplied `Signer` (the exact `Signer.verify` path the Publisher uses),
  after cross-checking the manifest hash against the record and signature. An
  unverifiable package is refused.
- **SBOM gate (§12)** — a well-formed SBOM whose component count matches the
  manifest must be present.
- **Secrets-by-reference gate (SEC-04)** — configuration binds secrets **only** by
  reference (`env://…` / `SecretRef`); an inline secret value is refused, and a
  defensive scan re-checks the finished descriptor.

It then resolves the **pinned dependency closure** (root + validated dependencies,
each re-validated for provenance/signature/SBOM), binds a deterministic resource
envelope, and generates a **deterministic runtime descriptor** and a stable
`runtime_id` (a SHA-256 over the artifact id, package hash, and closure fingerprint
— no wall-clock/ambient state). Deployment generation pins the image **by digest**
(`ucos-runtime/<name>@sha256:<package_hash>`), references secrets via `secretKeyRef`,
and stamps provenance + disclosure onto every manifest. Rollback is **reversible and
checkpoint-based** (IP-08): the pinned state is captured as a restorable checkpoint,
and a supplied prior unit is recorded as the exact `reverts_to` target.

The factory produces deployable **definitions** only — it does not deploy to or
mutate any live environment (§8; consumed downstream by IMP-008).

---

## 4. Created directories & files

```
engine/runtime/                              (NEW package)
├── __init__.py                              public API surface
├── errors.py                                TASK-000034  runtime error taxonomy (RT-*)
├── assembly.py                              TASK-000034  assemble() + PublishedPackage + RuntimeUnit
├── deploy.py                                TASK-000035  descriptor() + rollback() + closure record
├── disclosure.py                            TASK-000036  EC-1 provisional-state disclosure
└── EPIC-005-COMPLETION-REPORT.md            this report

engine/tests/
├── conftest.py                              (MODIFIED) runtime_signer + published_package fixtures
├── unit/test_runtime_assembly.py            assembly gates + determinism
├── unit/test_runtime_deploy.py              deployment + rollback
├── unit/test_runtime_disclosure.py          provisional-state disclosure
└── integration/test_runtime.py             TASK-000037  success criterion (assembly→deploy→rollback)

pyproject.toml                               (MODIFIED) coverage scope += engine.runtime
```

> Note on test paths: the mission listed `engine/tests/integration/test_runtime.py`,
> delivered as-is. Supporting unit tests are placed under the established
> `engine/tests/unit/` tree so the existing `pytest`/coverage gate discovers them.
> No file under `00-BOOK/`, `00-SOURCE/`, or `99-FREEZE/` was created or modified.

---

## 5. Verification evidence

Commands run in the pinned dev environment (`.ec1-venv`, target Python 3.12+,
executed on 3.14):

**Lint (ruff — CD-01/CD-04):**
```
ruff check engine   →  All checks passed!
```

**Tests + coverage gate (`--cov-fail-under=90`):**
```
335 passed
Required test coverage of 90% reached. Total coverage: 99.59%

engine/runtime/__init__.py      100%
engine/runtime/assembly.py      100%
engine/runtime/deploy.py        100%
engine/runtime/disclosure.py    100%
engine/runtime/errors.py        100%
```

**Build (DE-01):**
```
python -m build → Successfully built ucos_ec1_engine-0.1.0.tar.gz and
                  ucos_ec1_engine-0.1.0-py3-none-any.whl
  (all 5 engine/runtime/** modules packaged in the wheel)
```

**Frozen-path guard (DP-03) over the EPIC-005 change set** (`engine/` + `pyproject.toml`):
exit 0 (clean). The engine reads published packages and writes only to
caller-provided directories; it never targets the certified corpus.

---

## 6. Runtime assembly, deployment & rollback evidence

Generated end to end against the **real, certified `00-BOOK` registry** (compile
BP-DATA-0001 → publish → `assemble` → `descriptor` → `rollback`):

**Runtime assembly evidence**
```
runtime_id           = UCOS-RUN-BP-DATA-0001-5f58a290a1bc2c18
blueprint_id         = BP-DATA-0001
artifact_id          = UCOS-CMP-BP-DATA-0001-5cdc24681ea75f46   (== EPIC-004 id ⇒ determinism holds)
image_reference      = ucos-runtime/bp-data-0001@sha256:0a7ae17b8ec02f980dd4977d1d339a2d1bb2bc04f3f27d900a9bf3c5046f2cac
package_sha256       = 0a7ae17b8ec02f980dd4977d1d339a2d1bb2bc04f3f27d900a9bf3c5046f2cac
provenance_chain     = BP-DATA-0001 <- UCOS-DAT-000007 <- UCOS-REF-000003 <- UCOS-CAT-000003 <- UCOS-DAT-000002 <- UCOS-DAT-000004
signature            = HMAC-SHA256  (verified ✓)
sbom                 = ucos-sbom/1.0.0  (3 components, verified ✓)
dependency_closure   = [BP-DATA-0001 (root)]
disclosure           = EC-1-PROVISIONAL-STATE  (present ✓)
```

**Deployment descriptor evidence**
```
environment          = production
image                = ucos-runtime/bp-data-0001@sha256:0a7ae17b8...  (digest-pinned, immutable)
kubernetes           = [ConfigMap, Deployment, Service]
annotations          = provenance-chain, package-sha256, generation-framework,
                       authority=ENGINEERING-EXECUTION-ONLY,
                       provisional-state-disclosure=EC-1-PROVISIONAL-STATE (+ statement)
secrets              = bound via secretKeyRef only (never inline)
```

**Rollback evidence (IP-08 — reversible, checkpoint-based)**
```
strategy             = reversible-checkpoint
reversible           = True
checkpoint           = {runtime_id, artifact_id, package_sha256, image, dependency_closure}
kubernetes_rollback  = kubectl rollout undo deployment/bp-data-0001 --namespace runtime
restore_image        = ucos-runtime/bp-data-0001@sha256:0a7ae17b8...  (pinned)
disclosure           = EC-1-PROVISIONAL-STATE
```

**Dependency closure record**
```
ucos-closure/1.0.0 · root_package_sha256 = 0a7ae17b8... · members = [BP-DATA-0001 (root)]
```
(With a second published package supplied, the closure resolves and pins both
members — `root` + `dependency` — see `test_dependency_closure_resolved_and_recorded`.)

---

## 7. Success criterion

Proven: **a compiled BP-DATA artifact is transformed into a deployable runtime
unit, a deployment descriptor, and a rollback descriptor — with provenance,
signature verification, SBOM verification, and disclosure preserved.**

```
assemble(published("BP-DATA-0001"))  →  RuntimeUnit
    ├─ provenance chain      : preserved & consistent (manifest = record = SBOM)
    ├─ signature             : HMAC-SHA256 verified
    ├─ SBOM                  : present, component count matches manifest
    ├─ disclosure            : EC-1-PROVISIONAL-STATE present (survives to deploy + rollback)
    ├─ descriptor(unit)      : DeploymentDescriptor (ConfigMap + Deployment + Service, digest-pinned)
    └─ rollback(unit)        : RollbackDescriptor (reversible, checkpoint-based)
```

**STOP — EPIC-005 complete. EPIC-006 (and later) not begun.**
