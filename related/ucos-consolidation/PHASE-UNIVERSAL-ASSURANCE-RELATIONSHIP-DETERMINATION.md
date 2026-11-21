# PHASE — UNIVERSAL ASSURANCE RELATIONSHIP DETERMINATION

> **Mission:** Determine `platform/universal_assurance`'s relationship to `engine/certification` (EC-1) and `engine/universal_certification`
> **Mode:** Discovery only. Repository evidence only. No code changes, no merging, no hierarchy assumed.
> **Date:** 2026-08-13
> **HEAD:** `844c5056` (plus the uncommitted `identity_namespace_resolution` binding from the prior phase, unaffected)

---

## 1. Package Shape

`platform/universal_assurance/` (UCOS-EPIC-014, Terminal T7) is a fourteen-module package. Its own docstring frames it as *"the platform's evidence-bearing validation surface"* that "turns an assurance subject into a planned, generated, executed and certified assurance run." The orchestrator (`orchestrator.py`) runs **ten stages** in a fixed order:

```
Validation Planning → Validation Generation → Validation Execution
  → Evidence Collection → Certification Planning → Certification Execution
  → Certification Evidence → Certification Registry
  → Validation Intelligence → Certification Intelligence
```

Only two of these ten stages — **Certification Execution** and **Certification Evidence** — touch either certification engine under review. The other eight (planning, generation, execution, evidence collection, registry, both intelligence stages) are Universal Assurance's own, independently-implemented capabilities with no import relationship to `engine/certification` or `engine/universal_certification` at all.

---

## 2. Import Evidence

```
grep -rn "^from engine\.certification\|^from engine\.universal_certification\|^from platform\.certification" platform/universal_assurance/*.py
```

| Module | Imports from | Imports from EC-1 |
|---|---|---|
| `certification.py` | `engine.universal_certification.{audit,compliance,contracts,engine,errors,pipeline,rules}` — `CertificationAuditLedger`, `ComplianceFrame`, `default_frames`, `CertificationPipeline`, `CertificationRule`, `default_rules`, and the contract types | **None found** |
| `measurement.py` | `engine.universal_certification.contracts` (`RuleSeverity` aliased `CertRuleSeverity`) | **None found** |
| `policy.py` | `engine.universal_certification.contracts` (`MeasurementComparator`) | **None found** |
| every other module (11 of 14) | neither | neither |

**`platform/universal_assurance` has zero relationship to `engine/certification` (EC-1) anywhere in its source** — no file imports it, references it, or mentions it. Its only real coupling is to `engine.universal_certification`, and only in the three files above.

No circular dependency: `grep` for `platform.universal_assurance` inside `engine/certification/*.py` and `engine/universal_certification/*.py` returns nothing — the relationship is strictly one-directional (Assurance depends on Universal Certification; Universal Certification does not know Assurance exists).

---

## 3. What `certification.py` Actually Does

Its own docstring is explicit and decisive:

> "This package issues no certificate of its own and re-judges nothing. The certificate, the hash-chained approval workflow, the append-only audit ledger, the compliance engine and the ten certification rules all come from `engine.universal_certification`."

What it adds on top of the reused engine, per the same docstring:

- **Input adaptation** — projects its own `ValidationExecution`/`MeasurementReport`/repository-truth attestation into the `ValidationInput`/`MeasurementInput`/`RepositoryTruthInput` triple `engine.universal_certification` expects, "so the two engines meet without either knowing the other's identifiers."
- **Declared disclosure binding** — maps its own disclosure rule to the reused certifier's check id via policy data, never hardcoded.
- **Criterion reconciliation + policy severity** — reinterprets every finding under *its own* policy's severity, not the reused engine's.
- **Gate evaluation** — "a certificate that fails a declared gate closes the certification stage **even if the reused rule suite alone would have passed**."

That last point is the determining fact: Universal Assurance's outcome for its own certification stage can differ from what `engine.universal_certification` alone would produce. This rules out a pure read-only projection (which by definition reproduces the source's verdict unchanged, as EC-2 Console does for EC-1). It is real reuse of a component plus real additional judgment layered on top — not a rival authority re-deciding the same question, and not a passive mirror of one either.

---

## 4. Consumers

```
grep -rln "platform\.universal_assurance" --include="*.py" . | grep -v "^platform/universal_assurance/\|/tests/\|test_"
```

**Zero results.** No other package, engine, platform service, or live gate (`verify.sh`, `rib-gate`, `aee-gate`, `final_closure_engine.py`) references `platform.universal_assurance` anywhere. This mirrors the exact asymmetry `CERTIFICATION-OWNERSHIP-RECONCILIATION-DETERMINATION.md §3` found for `engine/universal_certification` itself: complete, internally coherent, correctly built — and not yet consumed by anything outside its own package and test suite. `platform/certification` (EC-2 Console, the one confirmed real `PROJECTION` surface in the certification landscape) has no relationship to `universal_assurance` either — zero cross-references found in either direction.

---

## 5. Determination

Evaluating the five options against the evidence above:

- **(A) Certification authority — No.** The package's own docstring disclaims this explicitly ("issues no certificate of its own and re-judges nothing"), and the import evidence confirms it: the certificate, audit ledger, compliance engine and rule suite are all reused, not reimplemented. Universal Assurance does not independently answer "is this subject universally engineering-ready" — it delegates that question wholesale to `engine.universal_certification`.
- **(B) Certification projection — No.** A projection reproduces its source's verdict unchanged (the recorded behavior of EC-2 Console toward EC-1: "reproduces EC-1's decision read-only, byte-for-byte"). Universal Assurance's gate evaluation can close its certification stage even when the reused rule suite alone would have passed — a real, additional judgment layer the reused engine does not itself apply. This is not read-only reproduction.
- **(C) Assurance evidence layer — Partially true, but incomplete as the whole classification.** Universal Assurance does own a real, generic evidence-bundle format (`~.evidence`, `ucos-assurance-evidence-{bundle,manifest}/1.0.0`) that the package explicitly intends "programme-local manifests should generalise to." But evidence is one of ten owned stages, not the defining shape of the package — planning, generation, execution, measurement, intelligence, and registry are equally owned capabilities with no evidence-specific framing.
- **(D) Independent bounded assurance domain — Best fit.** Eight of the ten pipeline stages are Universal Assurance's own, wholly independent capabilities with zero relationship to either certification engine. The two stages that do touch certification reuse `engine.universal_certification` as a declared **component** (per the package's own stated "Reuse First / No Parallel Authority" design posture), not as a peer authority being duplicated, projected, or competed with. The package answers its own, broader bounded question — "did this assurance subject's full planned-generated-executed-measured-certified run satisfy its declared policy?" — of which "is this subject universally certified" (Universal Certification's question) is one *input*, correctly reused rather than re-answered.
- **(E) Other — Not needed.** (D) accounts for the evidence without requiring a new category; the one caveat worth naming explicitly is that (D)'s certification-touching stage is best described as **verified component reuse**, a mechanism this session has already recognized (UKI's reuse of UKDA, UKIP's reuse of UKDA) rather than a certification-specific relationship needing its own label.

**Determination: (D) independent bounded assurance domain**, with a documented, code-confirmed **component-reuse relationship to `engine.universal_certification` specifically** (not EC-1 — zero relationship found there) for exactly two of its ten owned stages. This closes the open question `certification_authority_resolution.surfaces` recorded for `ASSURANCE-CERTIFICATION`: *"Relationship to EC1/UNIVERSAL-CERTIFICATION not established by evidence; recorded as an open question, not assumed either way."* It is now established: no relationship to EC-1, and a confirmed, one-directional, non-competing reuse relationship to Universal Certification — consistent with, and not contradicting, that surface's existing `AUTHORITY` role, since Assurance's own bounded question (policy-obligation satisfaction of a full assurance run) remains genuinely distinct from Universal Certification's (universal engineering-readiness of a normalized subject).

A secondary fact worth carrying forward: like `engine/universal_certification` before it, `platform/universal_assurance` currently has **no consumer anywhere else in the repository**. This is a roadmap observation, not a governance defect — the same conclusion reached for `engine/universal_certification` in the earlier certification determination.

---

## 6. Non-Goals

- No file was modified. No certification system was merged, consolidated, or re-scoped.
- No hierarchy was assumed going in; the one-directional, non-competing relationship reported above is what the import graph and docstrings show, not an inherited assumption.
- No recommendation is made here about whether this finding should be written into `certification_authority_resolution` (updating `ASSURANCE-CERTIFICATION`'s `bounded_question` note from "open question" to the determination above) — that is a future, separately-scoped governance-binding decision, not part of this discovery.
- Phase-8/9 and `verify.sh` were not run — this determination required only static reads of `platform/universal_assurance`'s source, imports, and docstrings, plus the existing `certification_authority_resolution` binding.

---

Stopping after discovery, as instructed.
