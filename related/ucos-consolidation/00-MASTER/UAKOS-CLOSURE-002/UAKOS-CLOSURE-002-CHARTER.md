# UAKOS-CLOSURE-002 — UNIVERSAL KNOWLEDGE INGESTION & VISION-TO-REPOSITORY CLOSURE (Program Charter)

| Field | Value |
|-------|-------|
| PROGRAM ID | UAKOS-CLOSURE-002 |
| ARTIFACT | Program Charter — Repository Closure Program |
| CLASSIFICATION | 00-MASTER program (derived-truth tooling; not frozen corpus, not a numbered band) |
| STATUS | ACTIVE · LIVING |
| AUTHORITY | **NONE — DERIVED TRUTH.** Records only what evidence in the repository proves. Asserts no closure without evidence (fail-closed, TRACK-001). |
| ANSWERS | *Does every constitutional concept from every authoritative source exist exactly once inside Repository Truth, with a disposition, traceability, and evidence?* |
| GOVERNED BY | `UCKO-PRIN-0001` (Knowledge Once), `UCKO-PRIN-0002` (Frozen Corpus Read-Only), `UCKO-PRIN-0005` (Determinism), `MCP-006` (Traceability), `UCOS-GOV-002` (Constitution→Implementation traceability) |
| BASELINE | commit `b67a720` · branch `governance-reconciliation` |

---

## 1. Purpose

Guarantee that every architectural concept ever discussed, designed, proposed, uploaded, generated,
or ratified exists inside **Repository Truth exactly once**, carrying exactly one constitutional
disposition, complete traceability, and physical evidence.

This program **does not** redesign architecture, create parallel knowledge, or duplicate Repository
Truth. It is a **reconciliation and audit** program that operationalizes the already-ratified
**Knowledge Once Principle** (`UCKO-PRIN-0001`).

## 2. Constitutional constraints (inherited, not invented)

- **Knowledge Once** — a canonical concept exists exactly once; everything else is derived/linked.
- **Frozen corpus read-only** — `00-BOOK`, `00-SOURCE`, `99-FREEZE` are never mutated by this program.
- **Determinism** — identical inputs at an identical commit produce byte-identical outputs. No
  wall-clock is embedded in canonical content; the git commit is the baseline stamp.
- **Fail-closed (TRACK-001)** — absence of evidence = NOT-DONE. This program **never** issues a
  green closure certificate that evidence does not support. A certificate reads `CLOSED` **only**
  when the machine determination proves zero gaps; otherwise it reads `NOT-CLOSED` with the real
  gap count.

## 3. Constitutional disposition model

Every discovered concept receives **exactly one** disposition. There is no sixth state; an
`UNCLASSIFIED` concept is itself a closure **violation** the engine must surface and drive to zero.

| Disposition | Deterministic evidence rule |
|-------------|------------------------------|
| **IMPLEMENTED** | Concept has code under an engineering root (`engine/ platform/ data/ service/ application/ infrastructure/`) and/or a resolved certification (`UCOS-CERT-*`, `CERTIFICATION-REGISTRY`). |
| **SPECIFIED** | Concept is defined in a constitution/spec (`02-MASTER/`, `00-CEP/`, numbered band `*.md`) but has no implementation/certification evidence yet. |
| **PLANNED** | Concept appears only in a roadmap/charter/plan/`MEP-*` context. |
| **DEFERRED** | Concept occurrence is marked `DEFERRED`/`BLOCKED`. |
| **REJECTED** | Concept occurrence is marked `REJECTED` / appears in a rejected-options record. |

Mapping to the existing `Lifecycle` enum (Part 12) is recorded per concept where a UKDA object exists;
the five closure dispositions are a **projection**, not a competing vocabulary.

## 4. Definition of Repository Truth (closure scope)

**Whole repository** is Repository Truth. A concept is **homed** (canonically present) when its
canonical ID appears in a definitional location: a filename, a constitution/catalog/registry entry
(`02-MASTER/`, `00-CEP/`, `00-BOOK/REGISTRIES/`, `00-BOOK/*CATALOG*`), a numbered band, `adr/`, or
the UKDA store (`knowledge/*.json`). A concept that appears **only** under `00-SOURCE/` or a root
upload, or **only** in the external corpus (conversation/upload material) and nowhere in a
definitional location, is a **gap** (upload-only / conversation-only knowledge — prohibited).

## 5. Deterministic-extraction methodology and its boundary

The engine extracts **canonical concept anchors** — the identifier-bearing abstractions the
repository already uses as its "exists-once" mechanism (`UCKO-*`, `UKDA-DEC-*`, `ARCH-*`, `MEP-*`,
`MCP-*`, `MCS-*`, `CEP-*`, `DATA/SERVICE/APPLICATION/INFRASTRUCTURE/PLATFORM/RUNTIME-*`, `UCOS-COMP-*`,
`UCOS-GOV/EXEC/RAT-*`, `EPIC-*`, concern/relationship meta-classes, band units, foundation anchors,
`Ω∞` laws, phases). This is deterministic, auditable, and re-runnable.

**Boundary (stated honestly):** free-text prose concepts that carry **no** canonical ID cannot be
deterministically deduplicated or matched, and the engine does **not** invent semantic matches for
them. Where a source document contains ID-less prose, the engine reports the document as ingested and
flags it for **human canonicalization** rather than fabricating concept records. This boundary is a
deliberate consequence of the fail-closed rule.

## 6. Outputs (generated, deterministic)

The engine (`closure_engine.py`) regenerates all artifacts in this directory from the live repository
state. See `closure.json` for the machine-readable determination and the numbered `01..14` reports.

## 7. Continuous ingestion

`make closure` re-runs discovery→extraction→matching→disposition→determination. A session hook re-runs
the workflow so new uploads/conversations/reports enter closure automatically. Closure is a
**standing gate**, not a one-time event.

---

*END OF CHARTER — UAKOS-CLOSURE-002 · ACTIVE · LIVING · AUTHORITY = NONE (DERIVED TRUTH)*
