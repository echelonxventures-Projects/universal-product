# UCOS Ω∞ — CMG CONSTITUTIONAL VALIDATION STRATEGY

| Field | Value |
|-------|-------|
| ARTIFACT ID | CMG-000006 |
| ARTIFACT | UCOS Ω∞ CMG Constitutional Validation Strategy |
| CLASSIFICATION | Constitutional Meta Governance (CMG) — Validation Strategy |
| PHASE | PHASE-000 |
| PROGRAM | CMG |
| CATEGORY | CMG |
| VOLUME | VOL-002 |
| STATUS | UNDER REVIEW · DERIVED · NON-NORMATIVE |
| VERSION | 1.0 |
| AUTHORITY | NONE (DERIVED TRUTH) |
| GOVERNED-BY | CMG-000001 |
| DEPENDS-ON | CMG-000001 |
| CANONICAL FORM | This Markdown file |

> Derived strategy under CMG-000001 Article L. Validation **operation** — criteria semantics, gate outcome, remediation, revalidation, closure — is owned by the located validation constitution (`CMG-DLG-04`) and is not restated here. This document states how the meta-constitutional validation subject is realized and executed.

---

## 1 — WHAT IS VALIDATED, AND WHAT IS NOT

CMG-000001 contributes exactly **one** validation subject to the corpus: the meta-constitutional conformance of the corpus. Its criteria are the twelve invariants `CMG-INV-01` … `CMG-INV-12` and nothing else (CMG-000001 L.2).

It validates **no** substance, **no** process compliance, **no** implementation, **no** knowledge content, and **no** property already checked by a located gate (L.7). Adding a check that duplicates a located gate would create a second authority over that property.

---

## 2 — REALIZATION

| Property | Value |
|---|---|
| Entry point | `python3 00-CMG/tools/cmg_validate.py` |
| Convenience entry point | `make cmg-gate` |
| Inputs | `00-CMG/CMG-000001-…md` (canonical), `00-CMG/CMG-REGISTRY.json` (configuration), the repository filesystem |
| Dependencies | Python standard library only. No third-party package, no network, no database, no service |
| Exit status | `0` zero findings · `1` one or more findings · `2` fail-closed abort |
| Evidence emission | `--emit <path>` writes deterministic JSON evidence |
| Output determinism | Byte-identical across runs; verified by double execution and diff |

**Zero hard coding.** The validator contains no member of any constitutional enumeration. Every kind, standing, reach, phase, state, transition, relationship type, tier, namespace, artifact, concern, vacancy, gap, and open question is read from `CMG-REGISTRY.json`. Admitting a new constitutional artifact or a new kind requires a registry entry and **no code change** (CMG-000001 CMG-L-08, LXVI.5). This is the property that makes the gate survive unbounded growth.

---

## 3 — CHECK INVENTORY

Sixteen check groups discharge CMG-000001 L.3(a)–(l) and the fourteen certification preconditions of LXXX.2.

| # | Check group | Clause(s) | What it proves |
|---|---|---|---|
| 1 | Source binding | XV.3, XXVIII.1, XII.6 | The derived registry projects the exact version of the canonical source, and declares itself derived truth |
| 2 | Conformance | L.3(a), LXXIX.7, V.2 | All 80 mandated sections resolve to present Articles; ordinals match; the article sequence is gapless; closing articles present |
| 3 | Identifier families | L.3(b), V.3, XXXI.2–XXXI.6 | Every `CMG-*` identifier used belongs to a declared family; every declared family is used; the `CMG` namespace width is respected |
| 4 | Member uniqueness | L.3(j), CMG-INV-08 | No identifier is duplicated across any registry collection |
| 5 | Canonical homes | L.3(c), LVIII.3, XXXI.8 | Every recognized artifact resolves to a file that exists |
| 6 | Classification | XII.1–XII.4, XIII.1, XVI.2 | Every artifact declares a kind, standing, reach and tier drawn from the declared value sets |
| 7 | Concerns | L.3(d)–(e), CMG-INV-02, CMG-INV-03, XX.8, LXXXII.3, CMG-INV-12 | Concern names are unique; every concern has a located owner; every binding artifact owns a concern; no derived-truth artifact is an owner; RETAIN concerns belong to the meta layer and REUSE concerns do not |
| 8 | Superiors and vacancies | L.3(f), CMG-INV-04, XVII.4, IV.11 | Every declared superior resolves to a located artifact or to a vacancy carrying a closure procedure and a recorded open question |
| 9 | Acyclicity | L.3(g), CMG-INV-05, XXXV.4 | Dependency graph and tier lattice both topologically sortable; every dependency target resolves |
| 10 | Precedence | L.3(h), CMG-INV-06, XVI.4, XVI.6 | Every artifact pair is comparable in the lattice, declared orthogonal, explicitly ranked, or jurisdictionally disjoint |
| 11 | Lifecycle | L.3(i), CMG-INV-07, XXV, XXVI, XXVII.3 | Every recorded state and transition is declared; no POST-EFFECT artifact declares binding standing |
| 12 | Lineage | L.3(k), CMG-INV-11, LXXII.6 | Every lineage predecessor resolves; no artifact is its own predecessor |
| 13 | Gaps and open questions | LXXVIII, LVII.3, LXXX.2 #12 | Every gap is dispositioned; unclosed gaps carry an open question; every open question states its ratification requirement |
| 14 | Closed enumerations | CMG-INV-09, LVI.5 | Every CLOSED enumeration cites a closing invariant that exists in the canonical source, and states its reason |
| 15 | Namespaces | XXXIII.1–XXXIII.6 | Each namespace has one located owner, a declared integer width and a declared status; `CMG` is owned by the meta instrument |
| 16 | Non-persisted conflicts | XXXIV.4, LXXIX.8 | No artifact persists a `CONFLICTS-WITH` relationship |

---

## 4 — FAIL-CLOSED SEMANTICS

CMG-000001 L.4 requires that an indeterminate result be a finding, never a pass. The realization:

| Condition | Behaviour |
|---|---|
| Registry file missing, unreadable, or malformed JSON | **Abort**, exit 2 |
| Registry root not an object | **Abort**, exit 2 |
| Canonical source declared but missing or unreadable | **Abort**, exit 2 |
| Canonical source declares no articles | **Abort**, exit 2 |
| Duplicate `## ARTICLE` heading | **Abort**, exit 2 |
| Malformed Roman numeral | **Abort**, exit 2 |
| Any invariant violated | **Finding**, exit 1 |
| Zero findings | Pass, exit 0 |

An abort is distinguished from a finding because an abort means the validator could not reach a determination at all. Both are non-zero; neither is a pass.

---

## 5 — DETERMINISM AND HERMETICITY

CMG-000001 L.5 requires byte-identical output for identical repository state. The realization guarantees this by construction:

- No clock, timestamp, hostname, user, PID, or environment variable appears in any output.
- No network or subprocess call is made.
- Every iteration over a mapping or set is performed over an explicitly sorted sequence; no output ordering depends on dictionary or set iteration order.
- Finding order is insertion order over a fixed check sequence, which is a pure function of the inputs.
- The topological sort is a deterministic Kahn variant with a sorted ready-queue, so a graph with multiple valid orders still yields one fixed order.
- Emitted evidence JSON is written with sorted keys.

**Verified:** two consecutive runs produce byte-identical stdout, and two consecutive `--emit` runs produce byte-identical evidence files.

---

## 6 — EXECUTION POINTS

| When | How | Enforced by |
|---|---|---|
| During authoring | `python3 00-CMG/tools/cmg_validate.py` | Author discipline |
| Before any commit touching `00-CMG/` | `make cmg-gate` | Recommended; see CMG-000013 |
| On any amendment to CMG-000001, the registry, the delegation register, or any invariant | Mandatory re-run | CMG-000001 LXXIX.5 |
| On admission of any new constitutional artifact, kind, tier, namespace, or delegation | Mandatory re-run | CMG-000001 LXXVI.2(g) |
| Before Constitutional Readiness certification | Mandatory; the validator output is the evidence | CMG-000001 LXXX.8 |

CMG-000001 LXVI.7 restricts the meta layer to **exactly one** gate. This is deliberate: a second gate would be a second enforcement authority.

---

## 7 — PRESENT VALIDATION RESULT

```
CMG-000001 META-CONSTITUTIONAL VALIDATION
  canonical source      : 00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md v1.0
  articles present      : 86
  mandated sections     : 80
  artifacts recognized  : 43
  concerns allocated    : 59 (48 delegated, 11 retained)
  vacancies recorded    : 1
  gaps recorded         : 9
  open questions        : 7
  findings              : 0
  readiness outcome     : READY-PROVISIONAL
```

Exit status `0`. The outcome is `READY-PROVISIONAL` rather than `READY` because one vacancy (`VAC-01`) and blocking open questions remain recorded — computed, not asserted (CMG-000001 LXXX.3, LXXX.4).

---

## 8 — WHAT THIS VALIDATION CANNOT PROVE

Stated plainly, because a validation strategy that overclaims is worse than none:

| Not proven | Why | Where it is handled |
|---|---|---|
| That CMG-000001 decides no substantive matter (`CMG-INV-12`) | Not mechanically decidable in general. The validator checks a strong proxy: that no retained concern duplicates a delegated one and that delegated concerns are never meta-owned | Human review under CMG-000001 XLV; audit under `CEP-010` |
| That the corpus contains no latent constitution | The rule is enforceable, but enumerating latent artifacts requires scanning every artifact in the repository against the six conditions of IV.1 — a detection run, not an invariant check | Audit owner (`CEP-010`), CMG-000013 recommendation |
| That the delegation register is complete with respect to the whole corpus | The register is exhaustive of the concerns the meta layer touches, not of the corpus (CMG-000001 LXXXII.6) | Recomputation on every change (LXXIX.5) |
| That any artifact's substance is correct | Out of jurisdiction entirely | The owning constitution |
| That the corpus is ratified | No ratification authority is located | CMG-OQ-01, CMG-OQ-02 |
