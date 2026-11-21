# PHASE — VERDICT VOCABULARY TAXONOMY DETERMINATION

> **Mission:** Determine whether the repository requires a universal verdict taxonomy authority, a translation layer, or documented independent vocabularies
> **Mode:** Discovery only. Repository evidence only. No code changes, no vocabulary merging.
> **Date:** 2026-08-13
> **HEAD:** `844c5056` (plus two uncommitted governance-binding phases from this session, unaffected)

---

## 1. Verdict Vocabulary Landscape

Inspected every certification surface already catalogued in `certification_authority_resolution.surfaces`, plus two consumers discovered during this pass. Each surface's actual verdict representation:

| Surface | Verdict form | Values found | Type |
|---|---|---|---|
| EC1-CERTIFICATION | `engine/certification/contracts.py:73` `CertificationStatus(str, Enum)` | `CERTIFIED`/`NOT_CERTIFIED` ("certified"/"not-certified") | Typed enum |
| UNIVERSAL-CERTIFICATION | `engine/universal_certification/contracts.py:79` `CertificationStatus(str, Enum)` | `CERTIFIED`/`NOT_CERTIFIED` — **identical name and values to EC-1's, independently defined** | Typed enum |
| EC2-CERTIFICATION-CONSOLE | none of its own — projects EC-1's `CertificationStatus` read-only | n/a | Projection, no vocabulary |
| KNOWLEDGE-CERTIFICATION (UKDA) | `engine/knowledge/certification.py:31` `CertStatus(str, Enum)` | `CERTIFIED`/`NOT_CERTIFIED` — **different class name, same values**, independently defined | Typed enum |
| UKIP certification (Part 12, not yet a registered surface — see prior determination) | `engine/knowledge/ukip/certification.py:1-10` — explicitly states *"The status vocabulary is reused from the UKDA certifier (`engine.knowledge.certification.CertStatus`) rather than redefined, so a UKIP certificate and a UKDA certificate mean the same thing by the same words"* | Same as KNOWLEDGE-CERTIFICATION (verbatim reuse, not a new vocabulary) | Reused enum |
| ASSURANCE-CERTIFICATION | `platform/universal_assurance/contracts.py:120-137` `Outcome`, `Verdict`, `GateStatus` (own enums) — internally also consumes reused `engine.universal_certification.CertificationStatus` for its certification sub-stage (per prior determination) | `PASS`/`FAIL` (Outcome, Verdict); `OPEN`/`CLOSED` (GateStatus) | Typed enum (own lexicon) + reused enum internally |
| RIB-CERTIFICATION | `00-MASTER/UCOS-RIB-001/rib_engine.py` — ad-hoc string literals, no Enum type found | `"PASS"`/`"FAIL"` per check; `certification_verdict_absent` boolean flag | Untyped string |
| AEE-CERTIFICATION | `00-MASTER/UCOS-AEE-001/aee_engine.py` — ad-hoc string literals | Per-criterion: `SATISFIED`/`VIOLATED`/`UNRESOLVED`/`NOT-EXECUTED`/`UNAVAILABLE`/`PASS`/`FAIL`; top-level `determination`: `CONVERGED-PROVISIONAL`/`NOT-CONVERGED` | Untyped string |
| CMG-CERTIFICATION | `00-CMG/tools/cmg_validate.py` — ad-hoc string literals | `READY`/`READY-PROVISIONAL` (and presumably a not-ready state) | Untyped string |
| PHASE8-CERTIFICATION | `final_closure_engine.py:368` | `"FIXED POINT CERTIFIED"` / `"NOT PROVEN"` | Untyped string |
| PHASE9-CERTIFICATION | `final_closure_engine.py:448` | `"REPRODUCIBILITY CERTIFIED"` / `"NOT PROVEN"` — same failure word as Phase 8, same engine | Untyped string |
| UCEF-CERTIFICATION | `00-MASTER/UCEF-000001/ucef_engine.py` | Per-gate: `GATE-OPEN`/`GATE-CLOSED`; top-level `determination`: `CERTIFIED-PROVISIONAL`/`NOT-CERTIFIED` | Untyped string |
| UMB017-DIGITAL-TWIN-CERTIFICATION | `00-BOOK/tools/ukbx.py:581,1256` | `CERTIFIED`/`NOT-CERTIFIED` | Untyped string |

**New, not-previously-catalogued consumer found:** `data/schema_certification.py` (EC3-B10-U04). Its own docstring: *"Certification is aggregation, not re-judgment... It runs through the CERTIFIED EC-1 Certification Engine... No parallel certification model is introduced (UDL-02 reuse-by-reference)."* Confirmed by direct import: `from engine.certification.contracts import CertificationSubject, CriterionStatus` / `from engine.certification.engine import CertificationDecision, CertificationEngine`. This is a second real, code-confirmed reuse of EC-1's vocabulary (alongside `platform/certification`), not a new one.

Twelve genuinely bounded surfaces, of which two independently define a `CERTIFIED`/`NOT_CERTIFIED`-shaped enum, one independently defines a differently-named-but-same-valued enum, one defines its own distinct `PASS`/`FAIL`/`OPEN`/`CLOSED` lexicon, and six use untyped, mutually distinct ad-hoc strings with no shared word between most pairs.

---

## 2. Consumer and Gate Analysis

The determining question is whether anything **reads across** two or more of these vocabularies and needs to reconcile their meaning to make a decision, versus treating each as an opaque, self-contained gate.

`00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py` is the one place in the repository that orchestrates multiple of these certification surfaces together — its `run_chain()` invokes RIB and AEE as prerequisite steps (`_STEPS` table, lines 64–65: `("rib", ("00-MASTER/UCOS-RIB-001/rib_engine.py",))`, `("aee", ("00-MASTER/UCOS-AEE-001/aee_engine.py", "--tier", "standard"))`). Both are invoked as **subprocesses and gated purely on process exit code** — `run_chain` never parses RIB's `"PASS"`/`"FAIL"` strings or AEE's `"CONVERGED-PROVISIONAL"`/`"NOT-CONVERGED"` determination as content; a nonzero exit from either subprocess halts the chain, regardless of what verdict word the subprocess would have printed. `verify.sh`'s own 8-stage pipeline (ruff, tests, `ukb.py enforce`/`validate`, `cmg-gate.sh`, `uga_engine.py gate`) follows the identical pattern: every stage is an independent process, AND-gated on exit code, never on parsed verdict content.

**No consumer anywhere in the repository was found that reads two different surfaces' verdict *values* and compares, translates, or reconciles them semantically.** Every cross-surface dependency found is a black-box pass/fail boolean at the process-exit-code level, not a content-level comparison. This is the same evidence shape §3–4 of `PHASE-KNOWLEDGE-REGISTRY-OWNERSHIP-RECONCILIATION-DETERMINATION.md` found for `ukb.py validate`/`engine.knowledge.validation` — independently-run, independently-scoped checks with no cross-reading.

---

## 3. Determination

- **(A) Universal verdict taxonomy authority — Not supported by evidence.** A universal taxonomy authority would need to answer: what does *any* certification surface's verdict actually mean, in one shared vocabulary? No consumer asks this question today — every gate consumes exactly one surface's verdict as an opaque boolean. Building this would require twelve independently-evolving, independently-scoped surfaces (EC-1 alone answers a different question than CMG, which answers a different question than Phase 8) to converge on one shared verdict schema for a need that has not materialized anywhere in the codebase.
- **(B) Translation / semantic mapping layer — Not supported by evidence.** A translation layer answers a narrower but still-unevidenced question: given two specific surfaces' verdicts, what is the equivalence between them? No code anywhere performs or needs this. `final_closure_engine.py`'s chain — the one place multiple surfaces are actually orchestrated together — deliberately treats each as a black-box exit code, which is itself evidence *against* needing translation: the chain already works correctly without ever interpreting a subordinate surface's specific verdict word.
- **(C) Independent vocabularies with documented relationships — Best fit, and largely already true in fact.** The landscape is not twelve unrelated inventions:
  - `UKIP` explicitly, verbatim reuses `UKDA`'s `CertStatus` (documented in `ukip/certification.py`'s own docstring) — not independent, a real declared relationship.
  - `data/schema_certification.py` explicitly, verbatim reuses `EC-1`'s `CertificationStatus`/`CertificationEngine` (documented in its own docstring, "No parallel certification model is introduced") — likewise a real declared relationship, and a second confirmed consumer of EC-1's vocabulary beyond `platform/certification`.
  - `EC-1` and `Universal Certification`'s identical `CertificationStatus` enum is the one confirmed accidental overlap, already investigated and classified in `CERTIFICATION-OWNERSHIP-RECONCILIATION-DETERMINATION.md §4-6` as narrow, single-enum, coincidental — not evidence of a taxonomy problem at the module level.
  - The remaining six ad-hoc-string surfaces (RIB, AEE, CMG, Phase 8, Phase 9, UCEF) are genuinely independent, each answering a structurally different question over a different population, with no shared code and — critically — **no evidenced need to be shared**, since nothing consumes more than one at the content level.
- **(D) Other — Not needed.** The evidence maps cleanly onto (C): most of the landscape's real relationships (reuse, not duplication) are already correctly implemented and merely undocumented at the verdict-vocabulary grain specifically (the existing `certification_authority_resolution` binding documents *authority* relationships per surface but does not currently enumerate each surface's own verdict vocabulary or which are reused vs. independently coined).

**Determination: (C) — independent vocabularies with documented relationships.** Not (A) or (B): no evidenced consumer need exists for either a universal taxonomy or a translation layer, and inventing either would be speculative infrastructure ahead of any demonstrated requirement — exactly the "build for hypothetical future requirements" this repository's own discipline warns against. What is missing is not a mapping mechanism but a **declaration**: which vocabularies are genuinely independent (six ad-hoc string surfaces, each over its own bounded question) and which are already-reused-not-duplicated (UKIP←UKDA, `data/schema_certification`←EC-1), so a future reader does not have to re-derive this by reading twelve source files, as this determination had to.

A secondary, non-binding observation: `CMG` (`READY-PROVISIONAL`), `AEE` (`CONVERGED-PROVISIONAL`), and `UCEF` (`CERTIFIED-PROVISIONAL`) each independently reached for the qualifier **"-PROVISIONAL"** for what appears to be an analogous concept — a pass with a known, named structural caveat. This is convergent design intent across three independently-authored vocabularies, not a formal relationship and not evidence of a taxonomy gap requiring action — but it is worth naming as the one place a future, evidence-driven documentation pass might find something real to record, should a consumer need ever arise.

---

## 4. Non-Goals

- No file was modified. No vocabulary was merged, mapped, or translated.
- No recommendation is made to build a translation layer or universal taxonomy — the evidence does not support either, and none is proposed as a future step.
- No verdict enum or string literal was renamed.
- The `EC-1`/`Universal Certification` `CertificationStatus` overlap already has its own governing determination (`CERTIFICATION-OWNERSHIP-RECONCILIATION-DETERMINATION.md`) and is not re-litigated here.
- No decision is made about whether the verdict-vocabulary facts in §1 should be written into `certification_authority_resolution` — that is a future, separately-scoped governance-binding decision, consistent with this session's discovery-before-implementation discipline.
- Phase-8/9 and `verify.sh` were not run — this determination required only static reads of each surface's verdict-defining source and the existing `certification_authority_resolution` binding.

---

Stopping after discovery, as instructed.
