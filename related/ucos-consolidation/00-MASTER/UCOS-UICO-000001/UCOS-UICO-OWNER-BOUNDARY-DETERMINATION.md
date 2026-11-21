# UCOS-UICO-000001 — Owner Boundary Determination

> **Artifact:** `UCOS-UICO-OWNER-BOUNDARY-DETERMINATION`
> **Programme:** UCOS-UICO-000001 — Phase 1 (discovery)
> **AUTHORITY = NONE — DERIVED TRUTH.** This determination allocates no ownership. Every boundary is
> read from a located instrument.
> **Disposition:** DISCOVERY ONLY. No code. No registry. No ownership modified.

---

## 1. Purpose

To establish that UICO's boundary is **empty of exclusive ownership** — that every responsibility it
touches is held by someone else, and that its own write scope does not intersect any of them.

## 2. The eight forbidden concerns, with their owners and enforcement

| Concern | Canonical owner | Enforcement that would catch a UICO breach |
|---|---|---|
| **Identity** | AIF `A/G-AUTH` — *"exactly one identity authority"*; UGA-001 for artifacts; sole sequence `00-BOOK/DATA/id-ledger.json` `by_object` | `verify.sh` 6b UGA-INV-01/02/03; G-24 `CK-UIS-SELF` *"fails closed if any emitted byte carries an identifier the located ledger does not already record"* |
| **Knowledge** | UCKP-LAW-0001; `engine/uckp/canonical.py` Layer Zero (Art-13, UCKP-INV-03) | `engine/uckp/validation.py` `_probe_zero_duplication` — AST scan over every module in `engine` and `platform`; a second digest definition is a measured violation |
| **Registry** | `engine/registry/universal` (12 typed registries); REG-AUTO-001 for artifacts | `register.sh --guard` exit 3 on drift; `ukb.py enforce` pre/post; UCCEP G-06/G-07 |
| **Security** | SECURITY-001 (SL-0, USL-001..015); `platform/security` record-only | USL-015 (no new primitive/authority/registry/identifier/lifecycle); `SECURITY-004 LR-1` bijection |
| **Certification** | UCOS-EPIC-006 `engine/universal_certification` (T6) | `OP-CERT-001` — a NOT-CERTIFIED decision can never be APPROVED |
| **Governance** | CEP-002 Art 28 / UCDA-000001; CMG-000001 Art L | G-14 Implementation Evidence Gate (Art 28.18/28.20 — cannot be waived); `cmg-gate.sh` CMG-INV-01..12 |
| **Evidence** | `EvidenceRegistry` (`required_attributes = {"subject"}`); SECURITY-001 §16 | UICM-INV-04 `uicm.unevidenced_closure` threshold 0, BLOCKING |
| **Execution mutation** | `engine/constitution/gateway.py` `UCOS-CMG-EXEC-000001` | sole producer of a clean `StateSeal`; `engine.constitution.state` refuses to verify, certify, register, measure or govern under a dirty seal |

**None of these prohibitions relies on UICO's restraint.** Each is enforced by a mechanism that would
fire independently. That is the property that makes the boundary real rather than declared.

## 3. UICO's own write scope

| Path | UICO right | Basis |
|---|---|---|
| `00-MASTER/UCOS-UICO-000001/**` | **write** — its own determination home | UGA ownership rule 1: `00-MASTER/<PROGRAM>/…` → `<PROGRAM>` |
| everything else | **read only** | — |

Intersection with the located record set:

```
UICO write set  ∩  located record set  =  ∅
```

This is the same immutability proof gates G-23, G-24, G-25 and G-26 each assert for themselves, and
it is asserted here in the same form deliberately — a new programme that could not state it would be
a programme with an unbounded blast radius.

Negative write authority, following the `forbidden_write_prefixes` convention every declaration in
this repository carries:

```
forbidden_write_prefixes:
  00-SOURCE/  99-FREEZE/  00-BOOK/  00-CEP/  00-CMG/  adr/  knowledge/
  engine/  platform/  data/  service/  application/  infrastructure/
```

The first three are additionally enforced mechanically —
`FROZEN_PREFIXES = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")` via `ec1-frozen-guard` and the
`ec1-ci.yml` DP-03 step.

## 4. Boundary against each named architecture

| Owner | Owns | UICO relationship | What UICO must never do |
|---|---|---|---|
| **UICM** | measurement, gap detection, closure state, observation history | **READ + INVOKE** | assert a closure state; edit a gap; write a register; add an 18th dimension |
| **UAUE** | evolution lifecycle, 11 phases, replay, evolution history | **READ + REFERENCE** | declare a second phase set; write `UAUE-EVOLUTION-HISTORY.json`; bypass AUE-P-05's authorisation record |
| **UCKP** | knowledge law, Layer Zero digest, the 15 canonical stages | **READ + DELEGATE** | define a digest; restate the stage set; fork the cycle |
| **CEP / UCDA** | governance dispositions, decision lifecycle, G-14 | **REFERENCE** | assign a disposition; declare a decision closed; waive G-14 |
| **UGA** | artifact identity, object governance, UGA-INV-01..10 | **READ** | mint an identity; write the registry or the id ledger |
| **Universal Certification** | the verdict | **INVOKE** | reach a verdict; upgrade, retry or reinterpret a refusal |
| **UCIC-001** | the 15-stage capability lifecycle | **BIND, DO NOT FORK** | define a competing lifecycle |
| **CMG-DLG-40 / UCCEP** | gate binding, `verify.sh`, workflows | **REFERENCE** | add a gate; edit `verify.sh`; append to `uccep-bindings.json` unilaterally |
| **Foundation composition** | `derive_order` — the single ordering authority | **REUSE** | hardcode an order (which *"would let a stage be skipped silently"*) |

## 5. Overlap analysis

Two overlap risks exist, and both are resolved.

### 5.1 Orchestration overlap — resolved by composition, not creation

Four orchestrators already exist. UICO does not add a fifth:

| Existing orchestrator | Scope | UICO overlap |
|---|---|---|
| `UicmController.run` | UICM's own 9-step measurement lifecycle | **none** — UICO invokes it whole |
| `EvolutionController` | UAUE's 11 phases | **none** — UICO references phase identity only |
| `RepositoryGovernancePipeline` | validation → certification → acceptance → readiness → freeze | **none** — different subject (runtime units) |
| `verify.sh` + `uccep-bindings.json` | cross-programme gate sequencing | **none** — UICO adds no stage and no gate |

A fifth orchestrator that *sequenced* rather than *composed* would be the parallel machinery CMG-L-14
forbids. The located precedent is explicit about the alternative:
`RepositoryGovernancePipeline` — *"It **reuses** the already-built engines — it creates no new
validation, certification, or acceptance logic — and sequences them."*

### 5.2 Matrix name overlap — resolved by projection

`00-UNIVERSAL-IMPLEMENTATION-CLOSURE-MATRIX.md` **already exists**, rendered by
`engine/uicm/controller.py`. UICO's matrix is a *projection* joining UICM's measured cells to the
Phase-2 ownership and Phase-4 governance determinations. It maintains no truth of its own, and it
must never be hand-edited — the remedy for a discrepancy is to re-derive it, never to correct it.

## 6. Ownership preservation proof

| Property | Measure | Result |
|---|---|---|
| Ownership modified by Phase 1 | files changed outside `00-MASTER/UCOS-UICO-000001/` | **0** |
| New owners introduced | count | **0** |
| New authorities introduced | count | **0** |
| Gaps whose owner changed | vs. UICM Phase 2 | **0** — the Phase-2 owner rule is reused verbatim |
| Distinct resolution owners | 3 central + 40 capability-local | **43**, all located |
| Owner write-scope collisions | at file granularity | **0** |
| Owner write-scope collisions | at subtree granularity | **38** — why file granularity is mandatory |

## 7. The three EXTEND rows belong to other owners

UICO located three gaps. **None is UICO's to execute.**

| ID | Gap | Owner | Why not UICO |
|---|---|---|---|
| UICO-GAP-01 | UICM gap register absent from UAUE `discovery_sources[]` | **UAUE-000001** | it is UAUE's declaration; only UAUE may append to it |
| UICO-GAP-02 | cross-run observation continuity | **UCOS-UICM-000001** | the loader belongs in `engine/uicm/observation.py`; UICO writes no engine code |
| UICO-GAP-03 | gap id → (owner, target file, gate) binding | **UCOS-UICM-000001** | it is an additive block in `uicm.json` |

UICO's role for all three is to have **located and specified** them. Execution is referred.

## 8. Determination

**UICO'S BOUNDARY CONTAINS NO EXCLUSIVE OWNERSHIP.**

Eight forbidden concerns, eight located owners, eight independent enforcement mechanisms. Six
permitted responsibilities, all held as projections over existing owners. One write scope
(`00-MASTER/UCOS-UICO-000001/**`) intersecting the located record set in the empty set. Zero owners
introduced, zero modified, zero overlaps at the mandated granularity.

The honest reading of this determination is that UICO is a **thin projection over a complete
system**, and Article 10.4 of its charter follows from it: if a later determination confirms UICO
owns nothing its owners do not already discharge, the correct outcome is retirement rather than
growth.
