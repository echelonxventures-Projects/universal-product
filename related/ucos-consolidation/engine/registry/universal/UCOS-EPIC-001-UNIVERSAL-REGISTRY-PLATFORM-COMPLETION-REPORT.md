# UCOS-EPIC-001 — Universal Registry Platform — Completion Report

| Field | Value |
|-------|-------|
| Program | **UCOS-EPIC-001** · Terminal T1 · Universal Registry Platform |
| Deliverable | Write-side **single registration authority** for every artifact in UCOS Ω∞ |
| Package | `engine/registry/universal/` (subpackage of the EPIC-002 registry) |
| Contract | `registry.platform` **v1.0.0** (Foundation `Contract`, AR-03 / PL-05) |
| Mode | **ADDITIVE ENGINEERING** — new code only; consumes frozen authorities, redesigns none |
| Authority | **NONE (derived)** — governed by AB-001 architecture and EG-001 engineering governance |
| Determination | **OPERATIONAL · CERTIFICATION-READY** |

> The platform is the governed *write* path complementing the EPIC-002 read-only
> adapter. Where the adapter reads the certified `00-BOOK` corpus, this platform is
> the authority through which an artifact becomes Repository Truth — enforcing
> deterministic identity, no-duplicate + Knowledge-Once, version chains, acyclic
> dependencies, and a tamper-evident audit trail. It never writes to the frozen
> corpus (DP-03) and is stdlib-only (TP-04/TP-05).

---

## 1. Architecture — the thirteen registries

One **Registry Core** (`RegistryCore`) is the single authority; twelve **typed
registries** are thin, kind-bound specialisations composed over it behind one
facade (`UniversalRegistryPlatform`). No architecture is redesigned — this is the
INV-13 *registration + metadata + composition* leg realised as executable code.

| # | Registry | Kind code | Required attributes |
|---|----------|:---------:|---------------------|
| 0 | **Registry Core** | — | (identity, dedup, version, audit, acyclicity authority) |
| 1 | Namespace | `NS` | `scope` |
| 2 | Capability | `CAP` | `summary` |
| 3 | Document | `DOC` | `path` |
| 4 | Engine | `ENG` | `entrypoint` |
| 5 | Component | `CMP` | `layer` |
| 6 | API | `API` | `contract`, `protocol` |
| 7 | Service | `SVC` | `domain` |
| 8 | Application | `APP` | `surface` |
| 9 | Infrastructure | `INF` | `provider` |
| 10 | Dependency | `DEP` | `source`, `target` |
| 11 | Evidence | `EVD` | `subject` |
| 12 | Certification | `CERT` | `subject`, `determination` |

Kind codes reuse the established UCOS native prefixes (Repository Truth) and are
unique, so a `universal_id` is self-describing and the registries never collide in
identity space.

## 2. Requirements conformance

| Requirement | How it is enforced | Evidence |
|-------------|--------------------|----------|
| **Follow AB-001** | Consumes the frozen architecture; adds no authority; no frozen artifact modified | `git status` — only new untracked files + `pyproject` script entry |
| **Follow EG-001** | Versioned contract, structured errors, deterministic path, evidence, tests | §5 / §6 |
| **Repository Truth only** | Append-only records; supersede-not-overwrite; no deletes (INV-10) | `RegistrationState`; `AuditAct` has no DELETE |
| **Knowledge Once** | Identical *substantive* content (kind+name+attributes+deps) under a different identity → `KnowledgeOnceViolation` | `test_knowledge_once_rejects_same_content_new_identity` |
| **No duplicate registrations** | Same `(universal_id, version)` or identical content for an identity → `DuplicateRegistrationError` | `test_duplicate_*` |
| **Deterministic IDs** | `UCOS-<CODE>-<12hex>` = SHA-256 over `(code, namespace, natural_key)`; version-independent | byte-stable CLI digest (§6) |
| **Version aware** | Monotonic semver chains; a new version supersedes the prior active (PL-05) | `test_new_version_supersedes_previous` |
| **Audit trail** | Append-only, hash-chained `AuditJournal`; tamper-evident `verify()` | `test_journal_detects_tampering` |
| Acyclic dependencies (DC-2) | Cycle + self-loop rejection on register; three-colour DFS on `verify()` | `test_dependency_cycle_rejected` |

## 3. Database model

The record schema is materialised as immutable, deterministically-serialisable
value objects and persisted as canonical JSON (never to the frozen corpus).

**`Registration`** (append-only record of record): `universal_id`, `kind`,
`namespace`, `natural_key`, `name`, `version`, `state`
(`ACTIVE|SUPERSEDED|DEPRECATED|RETIRED`), `content_hash`, `owner`, `description`,
`dependencies[]`, `tags[]`, `provenance[]`, `sequence`, `attributes{}`,
`superseded_by`.

**`AuditEntry`** (tamper-evident ledger unit): `sequence`, `act`, `universal_id`,
`version`, `content_hash`, `state`, `actor`, `timestamp`, `prev_hash`,
`entry_hash` (= SHA-256 over the canonical body incl. `prev_hash`).

**Persistence artifacts** (via `UniversalRegistryPlatform.export(dir)`):
`registry-snapshot.json` (all identities × versions) and `registry-audit.json`
(the chained journal, re-loadable + re-verifiable).

## 4. API surface

- **Programmatic:** `UniversalRegistryPlatform` → `.namespaces/.capabilities/…`
  (each `TypedRegistry.register/get/history/exists/id_for/all`), plus
  `.core` (`RegistryCore.register/get/get_version/resolve/history/deprecate/
  retire/by_kind/by_namespace/verify/snapshot`).
- **Contract:** `registry.platform@1.0.0` published into a Foundation
  `ContractRegistry` (`register_contract`).
- **CLI:** `ucos-registry <manifest.json> [--export DIR]` — validates a manifest
  through the authority and emits deterministic evidence. Exit codes `0` valid /
  `1` integrity-or-registration failure / `2` malformed manifest.

## 5. Tests, validation & coverage

- New suite: `engine/tests/unit/test_universal_registry.py` — **53 tests, all
  passing**, covering identity, records, audit chain + tamper detection, core
  (dedup / Knowledge-Once / versioning / lifecycle / cycles / resolve / views),
  all twelve typed registries, the facade, persistence, and the CLI.
- Package coverage **97%** (`__init__` 100, identity 100, errors 100, registries
  100, records 99, audit 96, cli 95, core 93).
- Full repository gate: **3762 passed · total coverage 99.17%** (≥90% gate
  reached). Ruff (E/F/I/B/UP/S) **clean**.
- Pre-existing, **unrelated** failures observed in `universal_certification`,
  `universal_validation` CLI, and a flaky `discovery/evidence` test were confirmed
  present without this package and are **out of scope** (not modified).

## 6. Evidence (verified, reproducible)

CLI run over a 4-artifact manifest (namespace, service, capability, certification):

```
identities=4 versions=4 audit_entries=4
contract=registry.platform@1.0.0
audit_head=281880778e4270576195dba67481e752a1966c2013ccc8c40bb9dc8892189309
ids: UCOS-NS-2add1ab7fb44  UCOS-SVC-67672763e996  UCOS-CAP-7be3a6044302  UCOS-CERT-4397fd315f49
```

Determinism proof — two independent CLI runs produced **byte-identical** summary
output (`sha256(stdout) = 0c4ffb3cf3d293ae12e5d32d35443c0cab4b17c32cb12af9a7c10be9eca3b2aa`
both times), and the audit head hash is stable across runs.

## 7. Certification readiness (EG-001 CG mapping)

| CG dimension | Status |
|--------------|:------:|
| Architecture / Constitutions / Repository Truth | ✅ consumed, unmodified |
| Knowledge Once · Determinism (CG-14) | ✅ enforced + proven byte-stable |
| Contract (IC-*) · Versioning (PL-05) | ✅ `registry.platform@1.0.0` |
| Validation · Evidence · Traceability | ✅ tests + exportable snapshot/audit |
| Dependency compliance (DC-2 acyclic) | ✅ enforced on write + verify |
| Quality / secure-coding (ruff S) | ✅ clean; stdlib-only |

## 8. DO-NOT compliance

Architecture **not** redesigned · Constitutions **not** modified · Governance
**not** modified · UMA **not** modified. Only new files under
`engine/registry/universal/` + `engine/tests/unit/test_universal_registry.py`, and
one additive `ucos-registry` console-script entry in `pyproject.toml`.

## 9. File inventory

```
engine/registry/universal/__init__.py        public API surface
engine/registry/universal/identity.py        deterministic IDs + canonical hashing + kinds
engine/registry/universal/errors.py          registration error taxonomy
engine/registry/universal/records.py         RegistrationRequest / Registration / AuditEntry
engine/registry/universal/audit.py           append-only hash-chained audit journal
engine/registry/universal/core.py            RegistryCore — single registration authority
engine/registry/universal/registries.py      12 typed registries + platform facade + contract
engine/registry/universal/cli.py             ucos-registry validation + evidence CLI
engine/tests/unit/test_universal_registry.py  53-test suite (97% package coverage)
```

**END — UCOS-EPIC-001 · UNIVERSAL REGISTRY PLATFORM · OPERATIONAL · CERTIFICATION-READY.**
