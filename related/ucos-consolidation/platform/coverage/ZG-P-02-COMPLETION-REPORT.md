# ZG-P-02 — Universe→Code Coverage Instrument — Completion Report

**Program:** UCOS Ω∞ Follow-On Execution · **Mission:** ZG-P-02 (Terminal 1)
**Source authority:** ZG-D-02 · MIP-ZG-001 · **Target gap:** G4
**Package:** `platform/coverage/` (additive EC-2 platform runtime)
**Status:** ✅ COMPLETE — deterministic, machine-verifiable, fail-closed Universe→Code
coverage instrument delivered, tested at 100% package coverage, and committed.

> Additive engineering package `platform/coverage/`. It closes **G4** — the missing
> machine-verifiable Universe→Code coverage recompute identified by ZG-D-02 / MIP-ZG-001.
> It reconstructs the authoritative coverage spine
> **Universe → Phase → Program → Implementation → Epic → Module → Code Asset → Runtime
> Asset** entirely from repository evidence (no hardcoded universe map, no manual coverage
> table, no synthetic edge), computes fail-closed coverage status, records it in an
> append-only content-addressed registry, exposes `compute`/`verify`/`reconcile`/
> `fingerprint`/`report`, drives nine critical health checks, and emits certification
> evidence for G4. It is strictly **additive**: it reuses the certified Foundation
> contract machinery and the Observability health model, integrates with GOV-002/005/006 ·
> TRACK-001 · STATUS-001 · MIP-ZG-001 **by reference**, imports no `engine.*` module,
> modifies no prior EC-2 epic, and writes nothing to the frozen corpus.

---

## 1. Architecture Determination

The instrument is an additive `platform/coverage/` package mirroring the certified EC-2
topology (errors → contracts → evidence → graph → registry → engine → health →
certification → repository → service → bootstrap). The pure analytical core (graph /
registry / engine / health / certification) is decoupled from evidence acquisition via an
`EvidenceSource` seam, so it is deterministically testable with fixtures while the
`RepositoryEvidenceSource` parses the live repository for production recompute.

## 2. Coverage Domain Model

`CoverageNodeKind` (8 tiers) · `CoverageStatus` (COVERED/PARTIAL/UNCOVERED/ORPHANED) ·
`CoverageNode` (`UCOS-COVN-`, id = hash of kind+ref) · `CoverageEdge` (`UCOS-COVE-`,
adjacency-checked, logical `tick` excluded from identity) · `CoverageVerification`
(`UCOS-COVV-`) · `CoverageReconciliation` (`UCOS-COVR-`) · `CoverageCertification`
(`UCOS-COVC-`) · `CoverageEvidence` (`UCOS-COVE-EV-`). Every identity is content-addressed;
the vocabulary is shape-only — no universe/program is hardcoded.

## 3. Coverage Graph Design

`CoverageGraph` is a deterministic DAG (spine adjacency guarantees acyclicity). Downward
memoized DFS yields COVERED/PARTIAL/UNCOVERED; upward lineage detects ORPHANED. Fail-closed:
a dangling or non-adjacent edge raises `CoverageGraphError`. `fingerprint()` hashes nodes +
edges + computed statuses.

## 4. Registry Design

`CoverageRegistry` — append-only, content-addressed, idempotent; node re-record with
conflicting content is refused (fail-closed); `duplicate_edge_refs()` surfaces one logical
edge asserted under multiple authorities. Reconstructs a graph/bundle at any time.

## 5. Coverage Engine Design

`CoverageEngine.compute/verify/reconcile/fingerprint/report`. `verify()` flags
orphan-code, orphan-universe, duplicate-coverage, and non-deterministic recompute.
`reconcile()` diffs the recorded registry against a fresh recompute. All operations are
pure functions of evidence.

## 6. Health System Design

Nine critical checks via the reused Observability model: four integrity checks (orphan-
universe, orphan-code, duplicate-coverage, coverage-fingerprint-mismatch → UNHEALTHY on
violation) and five completeness checks (missing-universe/program/implementation/module/
runtime → UNHEALTHY under strict certification policy, DEGRADED at baseline).

## 7. Governance Integration Matrix

| Instrument | Integration (by reference) |
|-----------|----------------------------|
| GOV-002 | traceability link model — coverage edges are the machine form |
| GOV-005 | zero-gap invariant — extended by universe→code recompute |
| GOV-006 | category→volume classification — reused, not replaced |
| TRACK-001 / STATUS-001 | evidence→status, append-only, fail-closed |
| MIP-ZG-001 | authorizing coverage & reconciliation determination |
| Foundation / Observability | `content_hash`, `ContractRef`, `HealthCheck`, `HealthStatus`, `HealthRegistry` reused verbatim |

## 8. Traceability Model

Every `CoverageEdge.trace()` yields `{source, target, authority, evidence, fingerprint,
timestamp}` — machine-reconstructable lineage from any code asset up to its universe and
from any universe down to runtime evidence.

## 9. Test Matrix

12 test modules (contracts, evidence, graph, registry, engine, reconciliation, determinism,
health, orphans, certification, repository, governance) — **107 coverage tests**, part of a
full suite of **1,886 passed / 0 failed**. Fail-closed, orphan, duplicate, non-determinism,
cross-process determinism, and real-repository integration all exercised.

## 10. Determinism Evidence

- In-process fingerprint stable across recomputes.
- **Cross-process byte-identical**: two independent interpreters produced
  `5df69a98589a728282eb57851d13f9660f2507a53bbefb8e0a4c1773f3123f43` (test
  `test_repository_fingerprint_is_reproducible_across_processes`).
- No wall-clock in any identity or ordering (logical ticks only, excluded from hashes).

## 11. Coverage Evidence (live repository at HEAD)

| Metric | Value |
|--------|-------|
| Graph fingerprint | `5df69a98…f3123f43` |
| Nodes / edges | 360 / 400 |
| Universes (parsed / covered) | 112 / 11 |
| Runtime assets (covered) | 2 / 2 (100%) |
| Orphans / duplicates / violations | 0 / 0 / 0 |
| `verify().ok` | **True** |
| Baseline certification | **CERTIFIED** (deterministic) |
| Strict certification | NOT-CERTIFIED — machine-readable reason `coverage-gaps:267` (EC-2 delivery is intentionally partial) |

## 12. G4 Closure Assessment

| G4 success criterion | Status |
|----------------------|--------|
| Universe→Code coverage machine-verifiable | ✅ instrument computes the full spine |
| Coverage recompute deterministic | ✅ byte-identical in- and cross-process |
| Coverage violations fail closed | ✅ integrity checks → UNHEALTHY; verify → violations |
| Coverage graph reconstructable | ✅ from repository evidence, no manual maintenance |
| Coverage evidence reproducible | ✅ deterministic fingerprints + evidence id |
| Certification APIs function | ✅ `assess()` + `certify()` emit all mandated fields |
| Health checks enforce integrity | ✅ nine critical checks |
| No orphan code / universes | ✅ 0 / 0 on the committed repository |
| No duplicate coverage records | ✅ 0 |

**G4 is discharged: the machine-verifiable Universe→Code coverage instrument now exists,
is deterministic, fail-closed, reconstructable, and reproducible.** (Whether G4 is formally
declared CLOSED is a determination act for ZG-D-02/ZG-D-05 reading this evidence; the
instrument they required is delivered.)

## 13. Quality-Gate Summary

| Gate | Result |
|------|--------|
| `ruff check platform engine` | ✅ All checks passed |
| `mypy platform/coverage` | ✅ no issues (12 files) |
| `pytest` full suite | ✅ 1,886 passed, 0 failed |
| Coverage — `platform/coverage` | ✅ 100% (12/12 modules) |
| Coverage — total | ✅ 99.89% |
| Determinism | ✅ byte-identical cross-process |

## 14. Files

Created: `platform/coverage/{__init__,errors,contracts,evidence,graph,registry,engine,
health,certification,repository,service,bootstrap}.py` + this report; tests
`platform/tests/test_coverage_*.py` (12) + `platform/tests/_coverage_helpers.py`.
Modified: `pyproject.toml` (added `platform.coverage` to coverage addopts + source). No
`engine/**`, no prior EC-2 epic, and no frozen-corpus file modified.

## 15. Readiness Determination

**COMPLETE — READY FOR G4 CLOSURE DETERMINATION.** The instrument ZG-D-02 identified as
missing is delivered, tested, deterministic, fail-closed, and committed. It supplies the
evidence necessary for G4 closure and final ZG-D-05 / Extended-Invariant (Conjunct 5)
certification.

**END ZG-P-02 — UNIVERSE→CODE COVERAGE INSTRUMENT — COMPLETE.**
