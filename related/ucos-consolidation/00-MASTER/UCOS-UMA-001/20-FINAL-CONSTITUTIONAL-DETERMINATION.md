# 20 — Final Constitutional Determination

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` (branch `governance-reconciliation`) · AUTHORITY = **NONE (DERIVED / DESIGN ONLY)**
> MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED. No code implemented, no existing artifact modified.

---

## VERDICT

# UNIVERSAL MEASUREMENT AUTHORITY — CONSTITUTIONALLY DESIGNED · READY FOR RATIFICATION · NOT YET INSTANTIATED

This program was mandated to **design only** the Universal Measurement Authority — a first-class, standing platform capability that makes measurement independent of repository closure while preserving Repository Truth, Knowledge Once, Single Authority, and fail-closed governance. That design is **complete as a constitutional architecture** across the twenty required outputs. UMA does not yet exist as a runtime; instantiation is a separate, evidence-gated governance action (docs 17–19).

---

## 1. Mandate satisfaction (design-level)

| Mandate | Where satisfied | Status |
|---|---|:---:|
| UMA is the sole standing measurement authority | doc 01 §2, §8 | DESIGNED |
| UMA owns only measurement (11 owned, 8 prohibited) | doc 01 §3–4 | DESIGNED |
| Platform capability with services | docs 02, 03 | DESIGNED |
| Registry-driven, never regex-driven discovery | docs 05, 06, 07 | DESIGNED |
| Reproducible / deterministic measurement | docs 04, 08, 12 | DESIGNED |
| Constitutional measurements defined (Purpose/Formula/Evidence/Authority/Deps/Failure) | docs 04, 08 | DESIGNED |
| Public API (≥12 Measure* operations) | doc 09 (A-1…A-12) | DESIGNED |
| Integration with UKB/Closure/Validation/Cert/Ingestion/Twin/Graph/Registries/Governance | doc 10 | DESIGNED |
| Data model, runtime, governance, evolution, security, quality | docs 11–16 | DESIGNED |
| Reference blueprint, migration, adoption | docs 17–19 | DESIGNED |
| Non-functional agnosticism/scalability/determinism/idempotence | docs 02, 11, 12 | DESIGNED |

## 2. Satisfaction of the inherited Measurement Authority requirements (CLOSURE-007 §05)

| Req | Was | UMA design | Status |
|---|:---:|---|:---:|
| MA-1 registry-driven families | UNMET | docs 05, 06, 07 | ADDRESSED |
| MA-2 every namespace discoverable or explicitly reserved/excluded | UNMET | doc 05 §3, status model | ADDRESSED |
| MA-3 scan-mode + schema stamped | UNMET | doc 04 §4 manifest / §5 envelope | ADDRESSED |
| MA-4 one deterministic canonical mode | UNMET | doc 04 §4 Canonical Manifest; doc 12 §3 | ADDRESSED |
| MA-5 non-text sources have declared disposition | UNMET | doc 07 §3 adapters | ADDRESSED |
| MA-6 prose/ID-less concepts have a measurement path | UNMET | docs 07 §4, 08 Semantic/Ontology | ADDRESSED |
| MA-7 every exclusion in an assumption register | UNMET | doc 07 §6; doc 11 records | ADDRESSED |

**MA requirements addressed by design: 7/7.** (Instantiation converts "addressed by design" to "satisfied in runtime"; that is future work.)

## 3. Preservation of frozen authorities (no redesign — mission constraint)

| Frozen authority | Preserved how |
|---|---|
| Repository Truth / UKB | UMA is read-only consumer; `authority = NONE` on all outputs (docs 01, 10, 15) |
| Knowledge Once | UMA stores descriptors/metrics/pointers, never knowledge; rebuild test (doc 11 §5) |
| Single Authority / Single Canonical Registry | UMA registries are measurement-control, explicitly distinct from canonical registry (doc 10 §4) |
| Governance / Closure / Lifecycle | UMA defers to CEP/CONST; governs only its own control plane (doc 13) |
| Fail-Closed | UNCOVERED→PARTIAL/UNKNOWN throughout; no silent success (docs 07, 08, 09, 12) |

No CONST-*, CEP-*, or prior program artifact is modified by this program.

## 4. Dependency Determination Summary (Mandatory Honesty)

Full register: doc 10 §5 (D-1…D-12). Principle:

- **TRANSFER to UMA** — all *measurement* responsibilities: discovery (`closure_engine.py` families), metric production (`closure.json`/`phase2.json` measurement fields), assimilation counts, coverage/completeness/quality measurement, census catalogs (as seed).
- **RETAIN with current owner (now consuming UMA)** — all *decisions*: closure determination, validation pass/fail, certification signing, planning, enrichment, and Repository Truth (UKB, read-only to UMA).
- **SUPERSEDE** — CLOSURE-007 §05 documentary Measurement Authority charter is permanently succeeded by doc 01; its MA-1…MA-7 become UMA obligations.

No dependency was found that forces UMA to own a decision, or that requires modifying frozen truth/governance. The measurement/decision separation is clean.

## 5. Success-criteria audit (mission)

| Criterion | Met at design level? | Evidence |
|---|:---:|---|
| UMA is the permanent measurement capability | YES | docs 01, 02 |
| No Closure Program owns measurement | YES (by design + adoption gate) | docs 01, 10, 19 |
| Closure/Validation/Certification/Governance consume UMA | YES | docs 09, 10, 19 |
| Repository Truth remains exclusively UKB | YES | docs 01, 10, 15 |
| Measurement is an independent platform capability | YES | docs 02, 12 |
| Do not implement code / modify artifacts | YES | design-only; new files only |
| Dependencies identified + keep/transfer recommended | YES | doc 10 §5; §4 above |

## 6. Instantiation Preconditions (what ratification must require)

Before UMA is declared *satisfied* (not merely designed), instantiation must demonstrate:
1. Conformance test suite passes (doc 17 §6).
2. Migration reaches M3 cutover with parity evidence (doc 18).
3. AdoptionRatio = 1 across measurement consumers (doc 19 §4).
4. Determinism/replay CI green on UMA runs (docs 12, 15, D-12).

Until then, per fail-closed doctrine, UMA is **DESIGNED, not SATISFIED**.

## 7. Seal

| Field | Value |
|---|---|
| Program | UCOS-UMA-001 · PHASE-001 |
| Baseline | `b67a720` (branch `governance-reconciliation`) |
| Determination | **UMA CONSTITUTIONALLY DESIGNED · READY FOR RATIFICATION · NOT YET INSTANTIATED** |
| Outputs produced | 20 / 20 (docs 01–20) + README |
| Inherited MA requirements addressed | 7 / 7 (by design) |
| Dependencies registered | 12 (D-1…D-12), TRANSFER/RETAIN/SUPERSEDE assigned |
| Frozen authorities modified | **NONE** |
| Code implemented | **NONE** |
| Existing artifacts modified | **NONE** |
| Authority of this program | **NONE — DERIVED / DESIGN ONLY** (fail-closed) |

*Measurement is hereby designed as a first-class, standing, registry-driven, deterministic platform capability — owned by no Closure Program, subordinate to Repository Truth, and consumed by all. The counting authority is defined; building it, and proving it counts everything, is the ratified work that follows.*

*END — 20 · UCOS-UMA-001 · FINAL CONSTITUTIONAL DETERMINATION · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
