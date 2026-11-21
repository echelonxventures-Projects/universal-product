# U53 — Decision Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U53-decision` |
| Layer | L8 Runtime Fabric |
| Domain | 09 Platform |
| Steward | `ucos:org:platform-kernel-decisions` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 |
| Depends on | U04 Meta (input/output types), U02 Governance (changes), U16 Context, U13 Temporal (rule validity), U68 Audit (decision logs) |
| Depended on by | nearly every business universe (configurable business logic), U22 Offer (eligibility), U23 Pricing, U26 Order (returns), U60 Workflow (routing), U69 Risk (P2), U49 AI (model-backed decisions) |
| Master references | §16.2, ADR (Decision engine DMN), L2 (no hard-coded thresholds) |

> Decision owns **configurable business logic expressed as data**: decision tables (DMN-style), decision models (DRDs combining tables, expressions and model scores), decision services (named, versioned endpoints), their tests, versioning, tenant overrides of pack defaults, and decision logs. Packs **declare** the decisions they need (with defaults); tenants **configure** them; no business thresholds live in code (lint `DEC-LINT-001`).

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| DEC-L1 | Business thresholds, eligibility rules, routing rules and policy-like parameters are decisions, not code constants. | Lint: numeric/string literals compared against business fields in pack handlers flagged; certification review. |
| DEC-L2 | Every decision has typed inputs/outputs (U04 types), a hit policy, default rule, tests and an owner. | Registry validation. |
| DEC-L3 | Evaluation is pure and deterministic given inputs + version + asOf; results log the matched rule ids. | Engine design; decision log. |
| DEC-L4 | Tenant overrides may only change rules within the declared `configurableBounds` of the pack decision (e.g. return window ≥ statutory minimum). | Bounds validation (constraint expressions). |
| DEC-L5 | Model-backed decisions (ML/AI scores) include a deterministic fallback rule and are governed by AI controls. | Schema requires `fallback`. |

## 2. Objects
- **`DecisionDefinition`** `{ id (e.g. order.return-eligibility), owner capability, inputs: [{name, type}], outputs: [{name, type}], kind: table|expression|model|drd, hitPolicy: UNIQUE|FIRST|PRIORITY|ANY|COLLECT(SUM|MIN|MAX|COUNT)|RULE_ORDER, defaultsRef, configurableBounds: [CEL constraints], tests, explainTemplate (LocalizedText per rule output), version }`
- **`DecisionTable`** — master §16.2 format; FEEL-compatible cell expressions (subset) or CEL; `*` wildcard.
- **`DecisionModel` (DRD)** — graph of decisions, input data and knowledge sources (e.g. fraud: rules + ML score + thresholds).
- **`TenantDecisionVersion`** `{ tenant, decision, rules, basedOnDefault@version, validity: TemporalPolicyRef?, status }`
- **`DecisionLog`** `{ decision@version, tenant, inputsHash (+ inputs if allowed by classification), matchedRules, outputs, ctxHash, at: TimePoint, latencyUs }` — sampled per decision `logPolicy` (full for financial/eligibility decisions affecting customers).

## 3. Engine
- Compiled in-memory (per cell) from published versions; evaluation p99 < 1 ms for tables ≤ 500 rules.
- Hit-policy semantics per DMN 1.4; `UNIQUE` overlap checked at publish (static analysis of rule conditions where decidable; otherwise test-based).
- `asOf` support via versions' validity.
- Explanations: each rule may carry an explanation key with parameters → user-facing reasons (e.g. "Returns for electronics are accepted within 7 days in India").

## 4. Commands, Queries, Events, APIs
Commands: `RegisterDecision` (by pack publish), `ProposeTenantVersion` (Governance standard/normal), `PublishTenantVersion`, `AddDecisionTest`, `RollbackTenantVersion`.
Queries: `Evaluate(decisionId, inputs, ctx)`, `EvaluateBatch`, `Explain(evaluation)`, `Coverage(decision)` (which rules ever hit), `Simulate(decision, version, dataset)`.
Events: `decision.version.published`, `decision.evaluation.logged` (to analytics, sampled).
```text
POST /v1/decision/{decisionId}:evaluate       POST /v1/decision/{decisionId}:simulate
GET  /v1/decision/definitions?owner=          POST /v1/decision/{decisionId}/tenant-versions
GET  /v1/decision/{decisionId}/coverage
```
Errors: `DEC_OUT_OF_BOUNDS`, `DEC_UNIQUE_VIOLATION`, `DEC_NO_MATCH` (no rule and no default), `DEC_INPUT_TYPE`, `DEC_TEST_FAILED`.

## 5. Security & Compliance
Who can change which decision is policy-controlled (e.g. `order.goodwill-limits` → finance role); decisions affecting consumers' rights are logged fully (explainability, automated decision-making transparency GDPR Art. 22 / DPDP); SPI inputs prohibited unless decision declares purpose + legal basis.

## 6. Gaps
```prolog
gap(decision_without_tests, D) :- decision(D), active(D), not has_tests(D).
gap(rule_never_hit, D, R)      :- decision(D), rule(D, R), active_days(D, N), N > 90, hits(D, R, 0).
gap(model_without_fallback, D) :- decision(D), kind(D, model), not fallback(D).
```

## 7. AI
Natural language → decision table drafting (bounded by configurableBounds, with generated tests), rule coverage analysis, simulation narratives. ML scores enter as model nodes from U49 registry.

## 8. Operations, UI, Scale
Signals: `decision_eval_latency_us`, `decision_no_match_total`, `decision_versions_published`. Views: `decision.table.editor` (spreadsheet-like, hit-policy aware, bounds shown, inline tests, simulation over last 30 days of logged inputs: "this change would alter 3.2% of outcomes"), `decision.drd.viewer`, `decision.log.explorer`. Scale: embedded library in pack SDK + decision service; T0 (embedded).

## Appendix
- **A.** FEEL vs CEL for cell expressions (recommendation: CEL platform-wide, consistent with U04).
- **C.** 0.1.0.
