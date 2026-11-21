# 02 — CANONICAL IMPLEMENTATION MANIFEST

> **Mission:** IMG-001 · **Baseline:** `ab78f35` · **Branch:** governance-reconciliation · **Date:** 2026-07-23
> **Mode:** READ-ONLY. No implementation, no commits, no tags, no push.
> **Authority:** Repository Truth is sole implementation authority. DERIVED fields carry an explicit rule; fields with no Repository-Truth basis are flagged **ASSUMPTION** and never fabricated into concrete work.

---

## 1. Purpose

This manifest is the single canonical implementation backlog for the 90 unrealized CKOs (`01-UNREALIZED-CKO-INVENTORY.md`). It records, per object, the implementation-planning attributes required by IMG-001. Attributes not carried in `closure.json` are supplied as **family-type templates** (deterministic per Canonical Type), not as invented per-object work.

---

## 2. Derivation rules (deterministic, Repository-Truth-anchored)

| Attribute | Rule |
|---|---|
| Canonical ID | `closure.json.id` (verbatim) |
| Canonical Type | `closure.json.family` |
| Owner | `<TYPE>` program authority (family-scoped) |
| Parent | family sentinel `<TYPE>-000`/`-XXX-000` if present in inventory; else the canonical home document |
| Repository destination | `closure.json.files[0]` (canonical home) |
| Target package | family→package map (§3) |
| Wave / phase | family→constitutional-class→wave map (§4; identical model to `04-IMPLEMENTATION-WAVES.md`) |
| Readiness | precedence rule in `08-IMPLEMENTATION-READINESS-MATRIX.md` |
| Dependencies / reverse-deps | constitutional layer-gate (wave N depends on waves <N) — see `03` |
| Complexity proxy | `trace-completeness (0–5) + zone-count`; a Repository-Truth-derived *structural* proxy, **not** an effort/time estimate (ASSUMPTION if read as effort) |
| Required artifacts/registries/schemas/runtime/validation/certification/traceability/evidence | family-type template (§5) |

---

## 3. Target implementation package map (family → package)

| Canonical Type | Target implementation package | Basis |
|---|---|---|
| LAW (Ω∞) | `00-MASTER` constitutional corpus + `00-BOOK` portal binding | zones `00-MASTER/00-SOURCE/02-MASTER` |
| ARCH | `00-BOOK/CONTROL-TOWER` registries; generative roots → `engine/factory/factories/` | zones `00-BOOK/02-MASTER/06-IMPLEMENTATION` |
| GOV / UCOS-GOV | `00-MASTER` governance + `00-BOOK/DATA` ledgers | zone `00-MASTER` |
| UCOS-RECON | reconciliation registers (`00-BOOK/DATA/id-ledger.json`, tools) | zone `00-BOOK/00-MASTER` |
| UCOS-RAT | ratification determination corpus | zone `00-BOOK/00-MASTER` |
| PHASE / EPIC | roadmap registers (`00-MASTER` plans, `00-BOOK/CONTROL-TOWER`) | zone `00-MASTER` |
| MCP / MEP / MCS / UCOS-EXEC | master context/execution/state (`00-MASTER/MCP-*.md`, `00-CEP`) | zone `00-MASTER/00-CEP` |
| UCOS-COMP | composition registers | zone `00-MASTER` |
| UCKO / UKDA-DEC | canonical knowledge / decision registers | zone `00-MASTER` |
| PLATFORM | `09-PLATFORM` + `10-DATA` platform packages | zones `09-PLATFORM/10-DATA` |
| EC3-GATE | EC-3 gate package (`06-IMPLEMENTATION`) | zone `06-IMPLEMENTATION` |
| DATA | `10-DATA` + `engine/factory/factories/data.py` | zone `10-DATA` |
| SERVICE | `11-SERVICE` + `engine/factory/factories/service.py` | zone `11-SERVICE` |
| APPLICATION | `12-APPLICATION` + `engine/factory/factories/application.py` | zone `12-APPLICATION` |
| INFRASTRUCTURE | `13-INFRASTRUCTURE` | zone `13-INFRASTRUCTURE` |
| RUNTIME | runtime package + (realizer `engine/factory/factories/runtime.py` **absent**) | zone `06-IMPLEMENTATION` |

**Generative realizer gap (Repository Truth):** `engine/factory/factories/` contains `base.py, api.py, application.py, data.py, service.py`. Absent: `event.py`, `workflow.py`, `runtime.py`, `infrastructure.py`. Thus generative roots ARCH-EVENT-001 / ARCH-WORKFLOW-001 / ARCH-RUNTIME-001 have **no realizer present**; ARCH-API-001 has a scaffold (`api.py`) but the concept is SPECIFIED.

---

## 4. Family → constitutional class → wave

| Wave | Constitutional class | Families | Objects |
|---|---|---|---|
| Wave-01 | Constitution | LAW | 20 |
| Wave-02 | Architecture | ARCH | 15 |
| Wave-03 | Governance / Registry / Roadmap / Knowledge | GOV, UCOS-GOV, UCOS-RECON, UCOS-RAT, PHASE, EPIC, MCP, MEP, MCS, UCOS-EXEC, UCOS-COMP, UCKO, UKDA-DEC | 32 |
| Wave-04 | Capability / Platform / Gate | PLATFORM, EC3-GATE | 11 |
| Wave-05 | Realization | DATA, SERVICE, APPLICATION, INFRASTRUCTURE, RUNTIME | 12 |

This mapping is the repository's own class→wave model (as used by `phase3_engine.py` in `38-DEPENDENCY-REGISTER.md`). It is **derived, not authored**. Note: the `38`/`40` registers themselves were generated at the superseded baseline `b67a720` (`AUTHORITY = NONE`); only their *layering model* is reused here, applied to the current `ab78f35` SPECIFIED set. Flagged **ASSUMPTION**: that the current baseline preserves the same layer semantics (supported by the stable family taxonomy).

---

## 5. Family-type requirement templates

Per Canonical Type, the required implementation elements. These are **type templates**, applied uniformly to every member of the type; they do not assert object-specific work beyond the type contract.

| Type | Required artifacts | Registries | Schemas | Runtime components | Validation | Certification | Traceability | Evidence |
|---|---|---|---|---|---|---|---|---|
| LAW | Constitutional article codified in corpus | constitution registry | n/a | n/a | constitutional consistency check | corpus certification | article→home binding | `verify.sh` corpus pass |
| ARCH (spec) | architecture determination doc | roadmap-reconciliation registry | n/a | n/a | architecture-completeness check | EC-3 gate | ARCH-id→registry | registry entry |
| ARCH (generative root: API/EVENT/WORKFLOW/RUNTIME) | factory realizer (`engine/factory/factories/<x>.py`) + generated catalog assets | artifacts.json | catalog schema | factory pipeline | generation validation | EC-3 gate | root→generated assets | catalog + factory output |
| GOV / UCOS-GOV | governance determination | governance registry | n/a | n/a | governance consistency | governance certification | GOV-id→register | ledger entry |
| UCOS-RECON | reconciliation determination | id-ledger / recon register | n/a | n/a | reconciliation check | recon certification | recon-id→ledger | ledger entry |
| UCOS-RAT | ratification determination | ratification register | n/a | n/a | consistency | (see DR-RAT-11, external) | rat-id→register | register entry |
| PHASE / EPIC | roadmap phase entry | execution-status registry | n/a | n/a | roadmap consistency | roadmap certification | phase-id→plan | plan entry |
| MCP / MEP / MCS / UCOS-EXEC | master context/execution/state artifact | master registers | n/a | execution engine binding | state consistency | execution certification | id→master doc | master doc entry |
| UCOS-COMP | composition determination | composition register | n/a | n/a | composition check | composition certification | comp-id→register | register entry |
| UCKO / UKDA-DEC | canonical knowledge / decision record | knowledge/decision register | n/a | n/a | knowledge consistency | knowledge certification | id→register | register entry |
| PLATFORM | platform capability artifact | platform register (`09-PLATFORM`) | platform schema | platform runtime | capability validation | EC-3 gate | platform-id→register | artifacts.json entry |
| EC3-GATE | gate artifact | EC-3 register | gate schema | gate runtime | gate validation | EC-3 certification | gate-id→register | gate pass |
| DATA | data asset (via `data.py`) | data catalog | data schema | data runtime | schema validation | EC-3 gate | data-id→catalog | catalog + factory output |
| SERVICE | service asset (via `service.py`) | service catalog | service schema | service runtime | contract validation | EC-3 gate | service-id→catalog | catalog + factory output |
| APPLICATION | application asset (via `application.py`) | application catalog | application schema | application runtime | app validation | EC-3 gate | app-id→catalog | catalog + factory output |
| INFRASTRUCTURE | infrastructure asset | infra catalog | infra schema | infra runtime | infra validation | EC-3 gate | infra-id→catalog | catalog entry |
| RUNTIME | runtime asset (realizer `runtime.py` **absent**) | runtime catalog | runtime schema | runtime engine | runtime validation | EC-3 gate | runtime-id→catalog | catalog + factory output |

---

## 6. Manifest completion criteria (per object)

| Criterion type | Deterministic completion signal (from `closure.json` on re-run) |
|---|---|
| Implementation completion | object transitions `disposition: SPECIFIED → IMPLEMENTED`, `in_code = true` |
| Validation completion | object `trace.implementation = true` and validation harness (`verify.sh`) green |
| Certification completion | object `certified = true` |
| Traceability completion | object `homed = true` with `trace.implementation = true` (home→artifact bound) |

Aggregate R1 completion: SPECIFIED count = 0 on the next `closure.json` regeneration.

---

## 7. Manifest summary

| Metric | Value |
|---|---|
| Total unrealized CKOs (manifest scope) | 90 |
| Requires hand-authored constitutional/governance work | 65 (READY 20 + BLOCKED 45) |
| Realized by generator/factory | 12 (GENERATED) |
| Not implementable (family sentinels) | 13 (NOT REQUIRED) |
| Distinct target packages | 16 family packages |
| Distinct canonical destinations | see `01` §3 |

---
*End of 02-IMPLEMENTATION-MANIFEST.md*
