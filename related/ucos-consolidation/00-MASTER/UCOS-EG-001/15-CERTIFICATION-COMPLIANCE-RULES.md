# 15 — Certification Compliance Rules

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define certification-compliance rules an implementation SHALL satisfy (CG-10; Certification Review R-9). Consumes CEP-005 (Certification Constitution) and the **CCE ten-gate** (`UCOS-COMP-000001`) via UCIC-001 Stage 10; adds no new certification model.

## 1. Certification Rules (CC)

| # | Rule | Basis | Evidence |
|---|---|---|---|
| CC-1 | **CCE ten-gate** (CC-1…10) all PASS | `UCOS-COMP-000001`; UCIC Stage 10 | CCE certification record |
| CC-2 | **Certifier ≠ executor** (separation of duties) | UCIC Stage 10; CEP-005 | SoD record |
| CC-3 | Certification consumes **validated** evidence (VALIDATED gate first) | UCIC gate order | validation refs |
| CC-4 | A **certification record** with a stable cert id is emitted | CEP-005 | cert id + ledger head |
| CC-5 | Certification is **deterministic / byte-identical** on re-run | CG-14 | determinism evidence |
| CC-6 | Certificate is **issued only when evidence supports it** (never speculative) | CONST-01 §2.13 | evidence chain |
| CC-7 | Traceability **rooted + closed** to the certification (No-Orphan) | CG-13; GOV-002 | trace |

## 2. CCE Ten-Gate (consumed, not redefined)

Certification compliance **is** the CCE ten-gate as invoked at UCIC-001 Stage 10 (`data.certification.cce_gates()` / per-band equivalents). EG does not enumerate or alter the ten gates; it requires their PASS as the CG-10 condition. Band evidence shows the pattern (CC-1…10 CLOSED→CERTIFIED, reused verbatim across bands).

## 3. Certification ≠ Admission ≠ Truth

| Layer | Owner | EG relationship |
|---|---|---|
| Certification | CEP-005 / CCE | EG requires it (CG-10) as a *necessary* admission condition |
| Admission | EG (derived) | EG computes ADMIT (doc 08); certification is one of six conjuncts |
| Truth entry | UKB | UKB performs entry once admitted |

Certification is necessary but **not sufficient** for admission (doc 08 requires conformance + reviews + evidence + governance too). EG never *issues* certificates — CEP-005/CCE does; EG *consumes* them.

## 4. Fail-Closed Conditions

| Condition | Result |
|---|---|
| Any CCE gate FAIL | CG-10 FAIL → REOPEN (evidence preserved) |
| Certifier = executor | CC-2 FAIL → DENY |
| Certificate without supporting evidence | CC-6 FAIL → invalid → DENY |
| Non-deterministic certification | CC-5 FAIL → DENY |

## 5. Determination

**CERTIFICATION COMPLIANCE RULES ARE DEFINED (CC-1…CC-7, fail-closed).** They require CCE ten-gate PASS with SoD, evidence-backed and deterministic, kept distinct from admission and truth — consuming CEP-005/CCE via UCIC Stage 10 without redefining certification.

*END — 15 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
