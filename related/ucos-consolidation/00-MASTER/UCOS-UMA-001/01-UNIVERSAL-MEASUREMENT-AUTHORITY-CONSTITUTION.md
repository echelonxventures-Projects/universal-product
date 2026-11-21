# 01 — Universal Measurement Authority Constitution

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` (branch `governance-reconciliation`) · AUTHORITY OF THIS DOCUMENT = **NONE (DERIVED / DEFINITIONAL — DESIGN ONLY)**
> MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED. Creates no canonical concept, implements no code, modifies no existing artifact.
> Constitutional principles preserved verbatim: **Repository Truth (UKB) · Knowledge Once · Single Authority · Fail-Closed Governance · Deterministic Execution · Evidence Before Conclusion.**

---

## 0. Purpose of this Constitution

This document is the proposed permanent constitutional charter for the **Universal Measurement Authority (UMA)** in UCOS Ω∞. It elevates *measurement* from a by-product of individual Closure Programs into a **first-class, standing platform capability**. It defines what UMA is, what it owns, what it may never own, and the constitutional relationship it holds to the frozen authorities that precede it.

This Constitution is definitional only. It asserts no measurement, produces no census, and creates no canonical concept. Measurement results are asserted only by the UMA runtime it specifies, once that runtime is built under separate governance action.

This Constitution is the successor materialization of **UAKOS-CLOSURE-007 §05 — Measurement Authority Constitution**, which established (documentary) a *Measurement Authority (MA)* with seven core requirements (MA-1…MA-7), all recorded as **UNMET (0/7)**. UMA is the platform that SHALL satisfy those requirements. See §7 and doc 20 for the dependency determination.

---

## 1. The Constitutional Gap UMA Closes

Evidence at baseline `b67a720`:

| Established capability | State | Authority |
|---|:---:|---|
| Repository Integrity | PASS | UKB / `closure.json` |
| Knowledge Once | PASS | UKB |
| Repository Truth | PASS | UKB |
| Single Authority | PASS | UKB |
| Architectural Completeness (Repository domain) | PASS | CONST-04/15 |
| Vision Assimilation | NOT COMPLETE | `phase2.json` |
| **Universal Measurement Authority** | **DOES NOT EXIST** | — |

The remaining constitutional gap is **not** repository architecture — that domain is closed and frozen. The gap is that the *measurement apparatus itself* is unproven, non-registry-driven, and owned inconsistently by whichever Closure Program happens to be running. CLOSURE-007 proved the discovery universe (26 curated regex families, git-tracked, text-only, corpus-optional) is strictly smaller than the actual architectural universe. UMA exists to make measurement **complete, reproducible, registry-driven, and permanently owned**.

---

## 2. Mandate

> **The Universal Measurement Authority is the sole standing constitutional authority responsible for measuring, enumerating, discovering, and reporting Repository-wide architectural state.**

No claim of coverage, completeness, assimilation, traceability, validation coverage, certification coverage, or repository health is constitutionally valid unless it is produced by, or reproducibly derivable from, a UMA measurement. After UMA ratification:

- **No Closure Program shall own measurement again.** Closure Programs consume UMA.
- **Validation consumes UMA.** Validation asserts pass/fail; UMA supplies the coverage basis.
- **Certification consumes UMA.** Certification signs determinations; UMA supplies the metrics.
- **Governance consumes UMA.** Governance decides; UMA supplies the evidence.
- **Repository Truth remains owned exclusively by UKB.** UMA measures truth; it never becomes truth.

---

## 3. What UMA Owns (exhaustive)

UMA owns exactly the following and **nothing else**:

| # | Owned capability | Meaning |
|---|---|---|
| O-1 | Measurement | Producing a determined quantity from a defined source under a pinned manifest. |
| O-2 | Enumeration | Complete listing of members of a defined set (namespaces, identifiers, artifacts). |
| O-3 | Coverage | The ratio of measured/represented members to the defined universe. |
| O-4 | Discovery | Registry-driven detection of architectural entities across all input sources. |
| O-5 | Evidence Measurement | Quantifying and locating the physical artifacts that back any determination. |
| O-6 | Repository Metrics | Structural, statistical, and relationship counts over the repository. |
| O-7 | Completeness Metrics | Metrics that quantify how completely a defined domain is represented. |
| O-8 | Assimilation Metrics | Metrics quantifying external→canonical knowledge assimilation. |
| O-9 | Quality Metrics | Metrics quantifying measurable structural quality of artifacts/knowledge. |
| O-10 | Governance Metrics | Metrics quantifying governance posture (authority uniqueness, freeze integrity). |
| O-11 | Certification Metrics | Metrics that a certification authority consumes to sign a determination. |

## 4. What UMA SHALL NEVER Own (constitutional prohibitions)

| # | Prohibited | Rightful owner |
|---|---|---|
| P-1 | Repository Truth / canonical knowledge | **UKB** |
| P-2 | Canonical homing, registration, deduplication of knowledge | **UKB** |
| P-3 | Enrichment / mutation of repository content | UAKOS-CLOSURE-003 lineage |
| P-4 | The pass/fail *decision* of validation | Validation authority (CLOSURE-004) |
| P-5 | The signing of certificates | Certification authority (CLOSURE-004) |
| P-6 | Governance decisions, freezes, ratifications | Governance authority (CEP / CONST) |
| P-7 | Lifecycle state transitions of concepts | Repository lifecycle (CONST-05/09) |
| P-8 | Creating, minting, or reserving identifiers | Identifier-issuing authorities (registered in UMA, owned elsewhere) |

UMA **measures** each of the above; it never **decides** any of them. This preserves the Prohibition of Conflation (CONST-01 §3): *Analysis ≠ Authority*. UMA is analysis, elevated to a platform, and permanently separated from decision.

---

## 5. Constitutional Principles UMA SHALL Enforce

| Principle | UMA obligation |
|---|---|
| **Repository Truth** | UMA reads truth from UKB; UMA outputs are derived (AUTHORITY=NONE) and never canonical. |
| **Knowledge Once** | UMA stores no second copy of canonical knowledge; its registries hold *descriptors and metrics*, not knowledge. |
| **Single Authority** | Exactly one UMA per repository; no competing measurement authority may be stood up. |
| **Fail-Closed** | Absence of evidence never yields a positive measurement claim; unknown → declared UNKNOWN, never assumed complete. |
| **Determinism** | Identical input state + identical manifest ⇒ byte-identical measurement. |
| **Replayability** | Every measurement is reproducible from a pinned manifest at any future baseline. |
| **Idempotence** | Re-running a measurement mutates no repository state and yields the same result. |
| **Registry-Driven Discovery** | Discovery is never regex-hardcoded; every namespace, identifier family, and discovery capability self-registers (see docs 05–07). |

---

## 6. The Seven Requirements UMA Satisfies (inherited from CLOSURE-007 §05)

| Req | CLOSURE-007 state | UMA design that satisfies it |
|---|:---:|---|
| MA-1 Discovery is registry-driven, not hard-coded | UNMET | Namespace Registry (doc 05) + Identifier Registry (doc 06) + Discovery Framework (doc 07) |
| MA-2 Every namespace is discoverable or explicitly reserved/excluded with rationale | UNMET | Namespace Registry status model + Exclusion Register (docs 05, 07) |
| MA-3 Scan mode + schema version stamped into every result | UNMET | Measurement Manifest + result envelope (docs 04, 08, 11) |
| MA-4 Canonical measurement uses one deterministic mode | UNMET | Canonical Manifest binding (docs 08, 12) |
| MA-5 Non-text sources have a declared disposition | UNMET | Source Adapter Registry (docs 07, 10) |
| MA-6 Prose-only (ID-less) concepts have a declared measurement path | UNMET | Semantic/Ontology discovery capability (docs 04, 07) |
| MA-7 Every exclusion is enumerated in an Assumption Register | UNMET | Measurement Assumption Register as a first-class UMA data object (doc 11) |

UMA is complete, as a design, only if all seven are addressed by the outputs of this program. Doc 20 audits this.

---

## 7. Dependency Declaration (mandatory honesty)

UMA is a *new* capability but it inherits obligations currently discharged (partially) by Closure Programs. Every such dependency is enumerated in doc 10 §Dependency Register and finally determined in doc 20. In summary:

- **`closure_engine.py` (UAKOS-CLOSURE-002)** is today the *sole discoverer*. Its discovery responsibility SHALL be **TRANSFERRED** to UMA; its closure-decision responsibility SHALL **REMAIN** with the Closure lineage (which will consume UMA discovery).
- **`closure.json` / `phase2.json` / `phase3.json`** are today both *measurement outputs* and *closure evidence*. The measurement-production role SHALL be **TRANSFERRED** to UMA; the closure-determination role SHALL **REMAIN**.
- **UKB** is Repository Truth. It **REMAINS** unchanged; UMA is a read consumer.

---

## 8. Authority Relationship (constitutional placement)

```
                         UKB  ── Repository Truth (canonical, sole)
                          ▲  reads (never writes)
                          │
        ┌─────────────────┴──────────────────┐
        │   UNIVERSAL MEASUREMENT AUTHORITY   │  derived, AUTHORITY=NONE
        │   (measurement · enumeration ·      │  standing platform capability
        │    coverage · discovery · metrics)  │
        └───────┬───────────┬───────────┬─────┘
        supplies│ metrics   │           │
        ┌───────▼──┐  ┌─────▼─────┐  ┌──▼───────────┐
        │ Closure  │  │ Validation │  │ Certification │  each CONSUMES UMA
        │ Programs │  │  Authority │  │  Authority    │  each DECIDES; UMA never decides
        └──────────┘  └───────────┘  └───────────────┘
                          ▲
                          │ decides / freezes / ratifies
                    Governance Authority (CEP / CONST)  ── CONSUMES UMA metrics
```

UMA is **subordinate to Repository Truth** (it measures, never creates knowledge) and **superior to every completeness/coverage claim** (no such claim is valid except through UMA). It is **orthogonal to** and **never overrides** enrichment, validation decision, certification signing, or governance.

---

## 9. Constitutional Determination of this Document

**UNIVERSAL MEASUREMENT AUTHORITY: CONSTITUTIONALLY DEFINED (documentary), NOT YET INSTANTIATED.** This charter is establishable and preserves all frozen authorities. It resolves the CLOSURE-007 gap at the constitutional level. Instantiation (building the UMA runtime) is a separate governance action, blueprinted in docs 17–19 and finally determined in doc 20.

*END — 01 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
