# Scope B · Workstream 5 — Registry Coverage Matrix · Implementation Report

| Field | Value |
|---|---|
| CAPABILITY | Registry Coverage Matrix (RCM) |
| MODE | Implementation + verification. **No certification claimed here.** |
| CONSTITUENT AUTHORITY | **NONE** |
| PREDECESSOR | `SCOPE-B-WORKSTREAM-5-REGISTRY-COVERAGE-MATRIX-DISCOVERY-DETERMINATION.md` |
| PRIOR BASELINE | `B-01` · `B-02` · Universal Lineage Projection — all CERTIFIED, **unmodified** |

---

## 1. Objective

Answer **"what governed objects exist, where are they registered, who owns the registration plane, and what coverage gaps exist?"** as derived coverage intelligence — under one constraint that shaped every decision:

> **The matrix must never become the 141st registry.**

---

## 2. Implementation Summary

| Path | Role |
|---|---|
| `engine/registry_coverage/declarations.json` | **Data** — 5 authority mechanisms · 2 registration planes · 8 disclosed W5-G1 gaps · 53-entry disclosed backlog · scan roots |
| `engine/registry_coverage/matrix.py` | Composition, authority location, validation, `verify()` |
| `engine/registry_coverage/__init__.py` | Public surface |
| `engine/tests/unit/test_registry_coverage_matrix.py` | **30 tests** |
| `pyproject.toml` | `engine/registry_coverage` added to **both** coverage enumerations |

**Nothing persisted. No registry created, no artifact written, no producer home added, no authority declared on anyone's behalf.**

---

## 3. Matrix Architecture

```
artifacts.json · id-ledger.json · generated-artifact-registry.json ·
constitutional-authority-alignment.json · mutation-governance-boundary.json ·
UGA universal object registry
                    │  (read-only)
                    ▼
        REGISTRY COVERAGE MATRIX     (derived · in-memory · stores no object record)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  coverage classification   authority-declaration validation
```

**It stores no object record.** Every object is read from the plane that already registers it; every ownership from the instrument that already declares it. Findings are capped at 100 as bounded diagnostics, never a population — a stored copy would be the duplicate catalogue the matrix exists to detect.

---

## 4. Input Authority Sources

Authority is located through the five mechanisms measured at discovery, tried in declared rank order so the most direct declaration is the one reported:

| Rank | Mechanism | Registries located |
|---|---|---|
| 1 | `TOP_LEVEL_AUTHORITY_KEY` | **94** |
| 2 | `DOMAIN_AUTHORITY_KEY` | 14 |
| 3 | `GENERATED_ARTIFACT_REGISTRY` | 17 |
| 4 | `CONSTITUTIONAL_AUTHORITY_ALIGNMENT` | 3 |
| 5 | `MUTATION_GOVERNANCE_BOUNDARY` | 0 (subsumed by rank 4) |

**187 scanned · 128 declared · 6 disclosed gaps · 53 disclosed backlog · 0 undeclared.**

---

## 5. Coverage Classification

Four states, all four detectable and each constructed in test.

| Plane | Registry | Owner | Entries | **Governed** | Retained |
|---|---|---|---|---|---|
| CORPUS | `artifacts.json` | UMB-IMP-001 | 1,233 | **1,233** | 0 |
| REPOSITORY | `id-ledger.by_object` | UCKP-ART-05 persistence binding | 4,876 | **4,874** | **2** |

| State | Count |
|---|---|
| `COVERED` | **6,112 / 6,112** |
| `PARTIALLY_COVERED` | **0** |
| `UNREGISTERED` | **0** |
| `DUPLICATE_REGISTRATION` | **0** |

Per class, every object COVERED: `EXCLUDED_DOCUMENT` 2,597 · `EXECUTABLE_OBJECT` 1,260+ · `DOCUMENT_ARTIFACT` 1,233 · `TEST_OBJECT` 825+ · `DATA_OBJECT` 125+ · `TOOLING_OBJECT` 36 · `CONFIGURATION_OBJECT` 31.

**Partition constraints, measured:** `artifacts ∩ id-ledger = 0` · `generated-reg ⊆ id-ledger` (**345/345**) · corpus + repository governed = total.

### `registered` is not `governed`, and the difference is reported
The repository plane holds **4,876** entries but **4,874** governed objects. The 2 are `RETIRED` — identity retained append-only and never reissued after the file left version control. The matrix reports `registered`, `governed` and `retained_not_governed` separately, so **correct append-only behaviour can never read as a coverage error**.

---

## 6. W5-G1 Resolution

**Disclosed, never inferred.** Eight producer outputs carry no declared authority. Each is recorded with `producer`, `producer_owner`, `missing`, `remediation` and `referred_to`:

`relationships.json` · `change-ledger.json` · `control-tower.json` · `volumes.json` (→ `ukb.py`) · `certification.json` (→ `governance_telemetry.py`) · `twin.json` · `signals.json` (→ `ukbx.py`) · `connector-cursors.json` (→ `connectors/base.py`) — all referred to **`UCOS-UKB-TOOLING`**.

**The producer is recorded and explicitly NOT adopted as the owner.** Inferring ownership would manufacture the very declaration the finding says is missing. A test asserts the recorded relationship is a *referral*, not an *ownership claim*.

### The finding was larger than eight, and is disclosed at full size
Building the matrix revealed **53 further registry-shaped artifacts** declaring authority through none of the five mechanisms. Rather than narrowing the scan to keep the number at eight, the full set is disclosed as a **ratcheted backlog**: it may shrink or hold, never grow. `validate()` refuses any registry that is neither declared nor disclosed — the same ratchet `UOBC-BSP-001` applies to birth adoption, and the reason disclosure is not permission.

---

## 7. Verification Enhancement

**No new verification stage.** The rule lives in `engine/registry_coverage/validate()` and is exercised by the test suite, which runs inside the **existing** pytest stage of `./verify.sh`.

It was deliberately **not** also added to `ukb validate`: that would place one rule in two places, and `ukb.py` is stdlib-only corpus tooling that must not depend on `engine/`. One rule, one home.

Validated: every registry-like output has an ownership classification · no duplicate authority · no duplicate registry plane (two planes claiming one object class is refused at load) · no orphan governed object.

Refusals exercised in test: an undisclosed registry with no authority · an unregistered object · a duplicate registration · an empty plane · two planes claiming one class · a missing declaration section · a missing file · unparseable JSON.

| Mode | Exit | Stages | Tests | Failed | Coverage |
|---|---|---|---|---|---|
| `--fast` | **0** | 4/4 | 11,987 | 0 | 97% |
| `--change` | **0** | 9/9 | 11,987 | 0 | 97% |
| `--integration` | **0** | 14/14 | 11,987 | 0 | 97% |
| `--full` | **0** | **15/15** | 11,987 | 0 | 97% |

Module coverage: `__init__` 100% · `matrix.py` **95%**.

---

## 8. Determinism Evidence

| Property | Result |
|---|---|
| Two builds byte-identical | **True** |
| Digest stable across builds | **True** |
| `verify()` | `deterministic: True`, `status: PASS`, **0 problems** |
| No wall clock in the matrix | **True** |
| Writes nothing | `git status` byte-unchanged across `build()` + `verify()` |
| Coverage exact after full regeneration | **6,112 / 6,112 COVERED**, 0 in every failure state |

---

## 9. Governance Compliance

| Constraint | Result |
|---|---|
| Not a registry | **HELD** — stores no object record; findings capped as diagnostics |
| Not an authority | **HELD** — `authority: NONE — DERIVED COVERAGE INTELLIGENCE` |
| Not an identity source | **HELD** — mints nothing; `category_seq` **117** unchanged |
| Not an ownership source | **HELD** — ownership read from declaring instruments; W5-G1 producers referred, not adopted |
| Not a mutation source | **HELD** — writes nothing |
| No registry of registries | **HELD** — registry entries are status rows, not registrations |
| No duplicate artifact catalog | **HELD** — objects counted, never copied |
| No duplicate identity ledger | **HELD** |
| No manual coverage database | **HELD** — derived on every call |
| No new verification stage | **HELD** — §7 |
| Births unchanged | **HELD** — 38 |
| Fixed point | **HELD** — pass 1 |
| Tree drift | **NONE** — 0 unstaged |

---

## 10. Remaining Gaps

| Gap | State |
|---|---|
| **W5-G1** (8 producer outputs) | **DISCLOSED, referred** to `UCOS-UKB-TOOLING`. Not resolved here — resolution is a declaration its owner must make. |
| **W5-G1-extended** (53 backlog) | **DISCLOSED and ratcheted.** May shrink or hold, never grow. |
| **W5-G3** — authority declared five ways | **OPEN.** The matrix now *reports* the mechanism per registry, which makes the fragmentation visible; it does not consolidate it. |
| **W5-G4** — `EVERY_CANONICAL_ARTIFACT_REGISTERED` binds only inside declared producer homes | **OPEN**, unchanged. |
| **W5-G5** — no staleness gate on derived registries | **OPEN**, unchanged. |
| `G6` · `GAP B-4` · lineage completeness · Capability Reality | **OPEN**, owned elsewhere, untouched. |

---

## 11. Certification Readiness

| Criterion | Status |
|---|---|
| Four-mode verification | **PASS** — 15/15, 11,987 tests, 0 failures, 97% |
| Object coverage | **6,112 / 6,112 COVERED**, 0 failures in any state |
| Partition constraints | **VERIFIED** — disjoint planes, generated-reg contained |
| Determinism | **PROVEN** |
| Authority preserved | **VERIFIED** — no registry, authority, identity, ownership or mutation source created |
| Identity invariants | **UNCHANGED** — `category_seq` 117 · births 38 |
| Evidence report | **THIS DOCUMENT** |
| Gaps disclosed | **YES** — §10 |

**Ready for certification. Certification is NOT claimed here** — it follows against the final closed state including this report.

---

# IMPLEMENTATION COMPLETE
