# CONST-01 — Repository Closure Constitution

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only constitutional stabilization
> Baseline commit `b67a720` (branch `governance-reconciliation`)
> AUTHORITY OF THIS DOCUMENT: Constitutional specification (definitional). It does NOT
> assert closure. Closure is asserted only by the canonical engine outputs it references.
> Fail-Closed · Evidence Before Conclusion · Knowledge Once · Single Canonical Authority

---

## 0. Purpose of this Constitution

This document is the permanent constitutional specification for **Repository Closure** in
UCOS Ω∞. It defines every closure-domain term, freezes its meaning, and eliminates the
ambiguity between **CLOSED** and **NOT-CLOSED**. It creates no new state, regenerates no
prior artifact, and executes no implementation. It is definitional only.

The constitution binds all successor programs (UAKOS-CLOSURE-002 / 003 / 004 / 005) and any
future evolution wave. Where a future artifact conflicts with a definition here, this
constitution governs the *terminology*; where evidence conflicts with an assertion, **evidence
governs** (Evidence Before Conclusion).

---

## 1. Constitutional Principles (maintained absolutely)

| Principle | Meaning |
|-----------|---------|
| Repository Truth | The governed repository is the single source of truth; derived tools never become truth. |
| Knowledge Once | Every concept has exactly one canonical home; no duplicated canonical stores. |
| Single Canonical Authority | One authority governs canonical representation (UKB). |
| Single Repository Engine | One engine owns Repository Truth (UKB); pipeline stages are derived. |
| Single Governance Authority | One governance authority; no competing governance. |
| Single Canonical Registry | One canonical registry; no competing registries. |
| Fail-Closed Governance | Absence of evidence never yields a positive closure claim. |
| Deterministic Execution | Analyses are re-runnable and reproduce identical results. |
| Evidence Before Conclusion | No speculation, no inferred completeness, no fabricated closure. |

---

## 2. Defined Constitutional Terms

Each term below carries nine permanent attributes: **Definition · Purpose · Scope · Authority ·
Evidence Requirements · Success Criteria · Failure Criteria · Dependencies · Lifecycle.**

### 2.1 Repository Closure
- **Definition:** The condition in which all *required* concepts of a defined closure domain
  have been assimilated into Repository Truth with zero open gaps for that domain.
- **Purpose:** To give a single, unambiguous predicate for "is this domain done?".
- **Scope:** Applied *per domain* (Integrity, Vision). Never a single global boolean.
- **Authority:** Asserted only by the canonical engine output for that domain; never inferred.
- **Evidence Requirements:** A deterministic engine artifact (e.g. `closure.json`, `phase2.json`)
  physically present at the baseline commit.
- **Success Criteria:** Domain `determination = CLOSED` **and** `gap_total = 0`.
- **Failure Criteria:** Any gap subcount > 0, missing evidence artifact, or non-deterministic output.
- **Dependencies:** Repository Integrity, Knowledge Assimilation, Canonical Representation.
- **Lifecycle:** DISCOVERED → … → ASSIMILATED → (domain) COMPLETE. See CONST-05.

### 2.2 Repository Integrity  (DOMAIN A)
- **Definition:** Internal canonical correctness of the governed repository, measured only
  against governed artifacts.
- **Purpose:** Guarantee the repository is duplicate-free, orphan-free, and fully homed.
- **Scope:** Governed repository artifacts only. Excludes external/unassimilated material.
- **Authority:** `closure_engine.py` → `closure.json` (derived, AUTHORITY=NONE); validated by UKB.
- **Evidence Requirements:** Canonical homes, duplicate-free, orphan-free, Knowledge Once,
  Repository Truth, determinism, governance, registry integrity, traceability integrity.
- **Success Criteria:** 398 concepts, `determination = CLOSED`, `gap_total = 0` (current evidence).
- **Failure Criteria:** Any `in_repo_unhomed`, `orphan_concepts`, `duplicate_canonical_homes`,
  or `ukda_content_hash_duplicates` > 0.
- **Dependencies:** UKB registry, canonical home register, traceability matrices.
- **Lifecycle:** Governed continuously; re-verified on each baseline. Full spec: CONST-02.

### 2.3 Repository Completeness
- **Definition:** The state where every governed concept holds a disposition
  (IMPLEMENTED / SPECIFIED / DEFERRED / REJECTED) with no UNKNOWN.
- **Purpose:** Ensure no governed concept is unclassified.
- **Scope:** Governed repository concepts.
- **Authority:** `closure.json.dispositions`; UKB validation.
- **Evidence Requirements:** Disposition assigned to 100% of concepts.
- **Success Criteria:** Σ dispositions = concept_total (398 = 313+60+21+4). No `unclassified`.
- **Failure Criteria:** `detail.unclassified` non-empty.
- **Dependencies:** Repository Integrity.
- **Lifecycle:** Re-derived per baseline.

### 2.4 Repository Representation
- **Definition:** Every known concept has a canonical location and identity within the repository.
- **Purpose:** Guarantee locate-ability and single-home addressing.
- **Scope:** All homed concepts.
- **Authority:** Canonical Home Register (UAKOS-CLOSURE-002 doc 22); UKB.
- **Evidence Requirements:** `homed = true`, `def_homes` or `exact_homes` resolvable.
- **Success Criteria:** `not_homed_concepts = 0`.
- **Failure Criteria:** Any concept `homed = false`.
- **Dependencies:** Repository Integrity, Canonical Representation.
- **Lifecycle:** Continuous.

### 2.5 Vision Assimilation  (DOMAIN B)
- **Definition:** The assimilation of *external* knowledge (conversations, uploads, vision and
  historical/future architecture, external constitutional knowledge) into Repository Truth.
- **Purpose:** Bring all discovered external intent into the governed corpus.
- **Scope:** The full discovered concept graph beyond the governed-only set.
- **Authority:** `phase2_engine.py` → `phase2.json` (derived, PHASE-002); planned by `phase3.json`.
- **Evidence Requirements:** Co-occurrence graph + enrichment gap counts at baseline.
- **Success Criteria:** `determination = CLOSED` and `gap_total = 0` for Domain B.
- **Failure Criteria (current):** `determination = NOT-CLOSED`, `gap_total = 110`
  (`conversation_only = 108` + 2 others). **Domain B is NOT closed.**
- **Dependencies:** Knowledge Assimilation, Conversation Assimilation, Upload Assimilation.
- **Lifecycle:** Continuous ingestion (UAKOS-CLOSURE-005). Full spec: CONST-03.

### 2.6 Knowledge Assimilation
- **Definition:** Incorporation of a discovered knowledge unit into a canonical home with governance.
- **Purpose:** Convert discovered knowledge into Repository Truth.
- **Scope:** Any DISCOVERED concept not yet REPRESENTED.
- **Authority:** UKB (home + registration); analytical detection via pipeline.
- **Evidence Requirements:** Concept transitions from source-only to homed+governed.
- **Success Criteria:** Concept leaves `conversation_only`/`upload_only` gap sets.
- **Failure Criteria:** Concept remains external-only.
- **Dependencies:** Conversation/Upload Assimilation, Canonical Representation.
- **Lifecycle:** Per enrichment wave.

### 2.7 Conversation Assimilation
- **Definition:** Assimilation of concepts that exist only in conversation material.
- **Purpose:** Eliminate the `conversation_only` gap.
- **Scope:** Conversation-sourced concepts.
- **Authority:** Pipeline detection (`phase2.json.gaps.conversation_only`); UKB homing.
- **Evidence Requirements:** `conversation_only` count.
- **Success Criteria:** `conversation_only = 0`.
- **Failure Criteria (current):** `conversation_only = 108`.
- **Dependencies:** Knowledge Assimilation.
- **Lifecycle:** Continuous ingestion.

### 2.8 Upload Assimilation
- **Definition:** Assimilation of concepts present only in uploaded documents.
- **Purpose:** Eliminate the `upload_only` gap.
- **Scope:** Upload-sourced concepts (6 docx uploads tracked in Domain A).
- **Authority:** Pipeline detection; UKB homing.
- **Evidence Requirements:** `upload_only` count.
- **Success Criteria:** `upload_only = 0` (Domain A currently satisfies this).
- **Failure Criteria:** `upload_only > 0`.
- **Dependencies:** Knowledge Assimilation.
- **Lifecycle:** Continuous.

### 2.9 Canonical Representation
- **Definition:** The single, authoritative form and location of a concept.
- **Purpose:** Enforce Knowledge Once.
- **Scope:** All homed concepts.
- **Authority:** UKB + Canonical Home Register.
- **Evidence Requirements:** Exactly one canonical home; no duplicate homes.
- **Success Criteria:** `duplicate_canonical_homes = 0`.
- **Failure Criteria:** Duplicate canonical homes present.
- **Dependencies:** Repository Integrity.
- **Lifecycle:** Continuous.

### 2.10 Architectural Completeness
- **Definition:** Every known architectural concept has canonical representation, governance,
  ownership, disposition, authority, and a repository destination — *whether implemented or not*.
- **Purpose:** Separate "architecturally accounted-for" from "assimilated/closed".
- **Scope:** All architectural concepts.
- **Authority:** CONST-04 + CONST-15; evidenced by `closure.json` dispositions and homing.
- **Evidence Requirements:** Each concept satisfies one of: Implemented, Specified, Governed,
  Planned, Deferred, Rejected, Historical, Superseded. No UNKNOWN.
- **Success Criteria:** Zero UNKNOWN-status architectural concepts.
- **Failure Criteria:** Any UNKNOWN status.
- **Dependencies:** Repository Representation.
- **Lifecycle:** Certified independently of closure (CONST-15).

### 2.11 Governance Completeness
- **Definition:** Every governed concept is under a single governance authority with no
  competing governance/registry/authority.
- **Purpose:** Preserve Single Governance Authority.
- **Scope:** Governed concepts.
- **Authority:** UKB (sole).
- **Evidence Requirements:** No competing authority/registry/governance/canonical store.
- **Success Criteria:** One authority, one registry (see CONST-16).
- **Failure Criteria:** Any competing authority detected.
- **Dependencies:** Repository Integrity.
- **Lifecycle:** Frozen (CONST-16).

### 2.12 Validation Completeness
- **Definition:** All governed concepts pass structural + referential validation.
- **Purpose:** Ensure integrity is machine-verified, not asserted.
- **Scope:** Governed concepts; enrichment items require `ukb validate`.
- **Authority:** UAKOS-CLOSURE-004 (validation); UKB validator.
- **Evidence Requirements:** Validation evidence artifacts; determinism proofs.
- **Success Criteria:** Validation passes for the domain under test.
- **Failure Criteria:** Any validation failure.
- **Dependencies:** Repository Integrity.
- **Lifecycle:** Per baseline + per wave.

### 2.13 Certification Completeness
- **Definition:** Independent certification that a domain satisfies its success criteria.
- **Purpose:** Provide an authority-signed determination separate from analysis.
- **Scope:** Per domain.
- **Authority:** UAKOS-CLOSURE-004 (certification).
- **Evidence Requirements:** Certification artifacts referencing engine outputs.
- **Success Criteria:** Certificate issued only when evidence supports it.
- **Failure Criteria:** Certificate issued without supporting evidence (prohibited).
- **Dependencies:** Validation Completeness.
- **Lifecycle:** On demand; never speculative.

### 2.14 Operational Completeness
- **Definition:** The closure pipeline is operable, deterministic, and re-runnable end-to-end.
- **Purpose:** Guarantee the closure model can be reproduced at any future baseline.
- **Scope:** The frozen 8-stage pipeline (CONST-08).
- **Authority:** UAKOS-CLOSURE-002 (pipeline design).
- **Evidence Requirements:** Re-run reproduces identical determinations.
- **Success Criteria:** Deterministic re-run; net-zero repository modification.
- **Failure Criteria:** Non-deterministic or mutating behavior.
- **Dependencies:** All above.
- **Lifecycle:** Frozen.

---

## 3. The Prohibition of Conflation

These terms SHALL NEVER be treated as equivalent:

- Repository Integrity ≠ Vision Assimilation (independent domains — CONST-02, CONST-03).
- Architectural Completeness ≠ Repository Closure (CONST-04, CONST-15).
- Validation ≠ Certification ≠ Closure.
- Analysis (pipeline) ≠ Authority (UKB).

A determination of one SHALL NOT imply a determination of another. Each is reported independently
(see CONST-18).

---

## 4. Current Evidence Snapshot (baseline b67a720)

| Domain | Engine | Concepts | Determination | Gaps |
|--------|--------|----------|---------------|------|
| A — Repository Integrity | `closure.json` | 398 | **CLOSED** | 0 |
| B — Vision Assimilation | `phase2.json` | 506 | **NOT-CLOSED** | 110 (108 conversation-only + 2) |
| B — Execution Planning | `phase3.json` | — | PLANNING-COMPLETE · REPOSITORY NOT-CLOSED | 110 planned |

**Determination of this constitution:** The Repository Closure Model is hereby defined and frozen.
Repository Integrity is CLOSED. Vision Assimilation is NOT-CLOSED. These are independent and are
never merged. See CONST-18 for the full final determination.
