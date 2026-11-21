# 05 — NON-AUTHORITATIVE ARTIFACTS

> **Mission:** IAC-001A · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Consolidates everything that carries **no implementation authority**: gitignored generated output, temporary transients, reference evidence, historical/superseded material, and external evidence.

---

## 1. Generated non-artifacts (gitignored) — see `04` for detail

`closure.json`, `phase2.json`, `phase3.json`, `UAKOS-CLOSURE-002/NN-*.md` (incl. registers 20/22/31/37/38/40), `/knowledge/`, `determinism-evidence/`, `00-MASTER/**/evidence/`, `provenance.json`, `10-UNIVERSAL-GAP-DEPENDENCY-GRAPH.json`. **NON-AUTHORITATIVE** by GOV-005 §5.3.

## 2. Temporary artifacts (gitignored transients)

| Pattern | Nature |
|---|---|
| `00-BOOK/tools/.register.lock` | Registration re-entrancy lock (register.sh) |
| `__pycache__/`, `*.pyc` | Python bytecode |
| `.ec1-venv/`, `build/`, `dist/`, `*.egg-info/` | Build/venv transients |
| `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `coverage.xml` | Test/lint transients |
| `~$*` | Office owner/lock temp files |

All non-authoritative, per-run/per-clone.

## 3. External / runtime evidence

| Location | Nature | Authority |
|---|---|---|
| `.runtime/` | Governance runtime telemetry, written solely by `00-BOOK/tools/governance_telemetry.py`; per-clone OPERATIONAL state | External / non-authoritative |
| DR-RAT-11 finality act | Out-of-corpus ratification act (per `07-ARCHITECTURE-FREEZE-EVIDENCE.md`, `EIP-018D/08`) | **External** — not present in corpus by design |

## 4. Reference Evidence (tracked, but evidence-only — no implementation authority)

| Location | Nature |
|---|---|
| `04-REFERENCE/*.docx`, `04-REFERENCE/ARCHITECTURAL-SOURCES/*.docx` | Original source/vision documents (ChatGPT chats, master plans, consolidation plan) |
| `04-REFERENCE/01-REFERENCE-INVENTORY.md`, `02-REFERENCE-ASSIMILATION-MATRIX.md`, `03-REFERENCE-COVERAGE-SUMMARY.md` | Reference assimilation records |
| `data/_evidence/**` (123 json, `UCOS-DATA-*`) | Registered certification-evidence family — authoritative **as a certification record**, but evidence-only for implementation (explicitly excluded from the `00-MASTER/**/evidence/` ignore, so it is a *distinct registered family*) |
| `infrastructure/_evidence/**`, `intelligence/_evidence/**` | Per-band certification evidence (tracked) |

These inform but do not author implementation; conformance is to the canonical constitutions/catalogs/schemas, not to these documents.

## 5. Historical / superseded artifacts (tracked, retained for record)

The repository root carries **overlapping numbered report series from multiple prior missions** (e.g., `01-IMPLEMENTATION-AUTHORITY-ASSESSMENT.md`, `01-CONSTITUTIONAL-COMPLETENESS-CERTIFICATION.md`, `01-READINESS-ASSESSMENT.md`, `05-FINAL-DETERMINATION.md`, `10-FINAL-CERTIFICATION.md`, `11-FINAL-RECOMMENDATION.md`, …). Each is a **Derived** read-only determination of the mission that produced it; where a later mission supersedes an earlier one, the earlier is **Historical**. For authority-classification purposes each is individually classifiable as Derived/Historical — none is a canonical (originating) source. *(Which determination is operative is a readiness/consistency question, explicitly out of this mission's scope.)*

## 6. Quarantined

| Location | Reason | Authority |
|---|---|---|
| `intelligence/die/` | RC-1 pre-sealing audit found `imports.py` an unverified orphan (no `__init__.py`, no importers, no tests, unpackaged); excluded from the RC-1 baseline so it is not sealed as verified implementation | **None** (quarantined; gitignored) |

---
*End of 05-NON-AUTHORITATIVE-ARTIFACTS.md*
