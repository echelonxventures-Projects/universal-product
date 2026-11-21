# U49 — AI / Model Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U49-ai` |
| Layer | L6 Intelligence |
| Domain | 07 Intelligence |
| Steward | `ucos:org:intelligence-ai-platform` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 (AI gateway, model registry, routing, guardrails, evaluations, budgets), P4 (embeddings at scale, fine-tunes, self-hosted models), P5 (federated/cross-tenant learning per master §20.5) |
| Depends on | U03 Policy, U65 Security (data classes, keys), U66 Privacy (AI purposes, training opt-in), U67 Compliance (EU AI Act, ISO 42001), U62 Integration (provider adapters), U28 Entitlement (AI quotas), U72 Observability (AI telemetry), U74 Certification (AI gates), U13 Temporal (budgets windows, evaluation cadence, price validity), U14 Currency (cost), U94 ML Platform (shared registry) |
| Depended on by | U50 Prompt, U51 Agent, U44 Search (embeddings), U52 Recommendation, U18/U21 (enrichment), U15 (translation), U39/U109 (assist, bots), U58 Composition (intent analysis), U72 (AIOps), every AI feature |
| Master references | §21 (AI fabric, routing example), L15 (vendor agnosticism), L17 (human authority), ADR-010 |

> AI owns **access to and governance of AI models**: the **model registry** (LLMs, embedding, vision, speech, rerankers — and, shared with U94, classical ML models), **providers** and their contracts/data terms, the **AI gateway** (routing, guardrails, caching, budgets, telemetry), **evaluations**, **model cards**, **AI use-case registration and risk classification**, and AI incident handling. Prompts are U50; agents are U51; training of classical ML is U94.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| AI-L1 | All model calls go through the AI gateway; no pack holds provider SDKs or keys. | CAP-L5 + egress allow-lists (INT-L1); lint for provider SDK imports. |
| AI-L2 | Every AI use case is registered with purpose, risk class (EU AI Act tiers + internal), data classes allowed, human-oversight design and owner before production. | `AIUseCase` required by gateway route resolution; gate `AI-UC-01`. |
| AI-L3 | Data sent to a model obeys the handling matrix (§19.7): `restricted` data only to zero-retention, residency-compliant endpoints approved for that data class, with purpose. | Gateway pre-flight classification check + PII redaction guardrail. |
| AI-L4 | Routing is policy (decision tables), never code; every response records model id/version, route, cost and guardrail outcomes. | Gateway contract + AI telemetry. |
| AI-L5 | A model version is servable only with a passing evaluation on the use case's eval suite and a model card. | Certification gates `AI-EVAL-*`, `AI-CARD-01`. |
| AI-L6 | Tenant data is never used to train or tune shared models without explicit opt-in recorded as a contract fact (master §20.5). | Training-purpose check (U66) in U94/U49 fine-tune pipeline. |
| AI-L7 | AI outputs shown to people are labelled as AI-generated where law or policy requires, and outputs used for decisions about people are explainable and contestable. | UI obligation + U53 decision logs. |

## 2. Ontology
- `Provider { id, kind: hosted-api|self-hosted|on-device, vendor, regions, dataTerms: {training: none|opt-in|yes, providerRetention: zero|Duration, residency}, contractRef (U89), status }`
- `Model { id (e.g. model.anthropic.claude-opus-5-5), provider, providerModelId, modality: [text, vision, audio, embedding, rerank, code], capabilities: [reasoning, tool-use, long-context, structured-output, …], contextWindow, residency, dataPolicy, price: PriceRef (U23 price list, temporal validity), evaluations: [EvalResultRef], card: ModelCardRef, riskNotes, status: experimental|certified|deprecated }` (shared registry with U94 classical models).
- `Route { id, rules: DecisionRef (inputs: task, data class, latency budget, tenant AI profile, residency, cost tier), fallbacks: [ModelRef], circuit policy }` — seed routing per master §21.2: `claude-opus-5-5` (complex reasoning/agent planning), `claude-sonnet-5-5` (general/tool use), `claude-haiku-4-5-20251001` (high-volume classification/extraction), self-hosted for on-prem/PHI-restricted tenants.
- `Guardrail { id, stage: input|output|tool-call, kind: pii-redaction|prompt-injection-detection|untrusted-content-isolation|toxicity|jailbreak|schema-validation|grounding-check|copyright|secret-leak, action: block|redact|flag|route-to-human, config }`
- `AIUseCase { id, owner capability, purpose (U66), riskClass: minimal|limited|high|prohibited (+ internal tier), dataClassesAllowed, humanOversight: none|review-sample|approve-each|approve-above-threshold, evalSuite, route, guardrails, userDisclosure: bool, status }`
- `EvalSuite { id, useCase, datasets (U93 data products; golden sets), metrics (accuracy, F1, faithfulness, toxicity, bias slices), thresholds, cadence: Recurrence }`, `EvalResult { suite, model@version, prompt@version, scores, at: TimePoint }`
- `ModelCard { model, intendedUse, limitations, trainingDataSummary (provider-supplied), evals, risks, contacts }`
- `AIBudget { scope: tenant|use-case|agent, limit: Money, rollingWindow: Duration, onExceed: block|downgrade-route|alert }`
- `AIIncident { useCase, kind: harmful-output|data-leak|hallucination-impact|bias|security, severity, reportedAt: TimePoint, actions, notifications (EU AI Act serious incident reporting where applicable) }`

## 3. AI Gateway (runtime contract)
```proto
service AIGateway {
  rpc Complete(CompletionRequest) returns (CompletionResponse);         // chat/text, tool-use, structured output
  rpc Stream(CompletionRequest) returns (stream CompletionChunk);
  rpc Embed(EmbedRequest) returns (EmbedResponse);
  rpc Rerank(RerankRequest) returns (RerankResponse);
  rpc Transcribe(AudioRequest) returns (TranscriptResponse);            // speech-to-text (U109)
  rpc Speak(TTSRequest) returns (AudioResponse);                        // text-to-speech
}
message CompletionRequest { string use_case = 1; string prompt_ref = 2; map<string,string> variables = 3;
  repeated Message messages = 4; repeated ToolSpec tools = 5; string output_schema = 6;
  string context_token = 7; string idempotency_key = 8; }
```
Pipeline: verify context → resolve `AIUseCase` (must be active, purpose allowed, data classes allowed) → render prompt (U50) → input guardrails (classification, PII redaction per policy, injection detection, untrusted-content tagging) → route (decision) + budget check (U28/AIBudget) → provider call via U62 connector (residency-correct endpoint) with retries/fallback → output guardrails (schema validation, grounding check for RAG, toxicity, secret/PII leak) → telemetry (tokens, cost Money, latency, guardrail outcomes, model/prompt versions) → audit record (prompt hash, output hash) → response with `ai` metadata (label requirement, confidence where available).
Caching: provider prompt caching for long static prefixes; semantic cache only for non-personal, tenant-scoped, idempotent queries (opt-in per use case).

## 4. Commands, Queries, Events, APIs
Commands: `RegisterProvider`, `RegisterModel`, `CertifyModelForUseCase`, `DeprecateModel`, `DefineRoute`, `DefineGuardrail`, `RegisterUseCase` (governed; high-risk → significant change), `DefineEvalSuite`, `RunEval`, `SetBudget`, `ReportAIIncident`.
Queries: `ModelsFor(task, constraints)`, `UseCaseStatus`, `EvalHistory(model, useCase)`, `CostReport(scope, range)`.
Events: `ai.model.certified|deprecated`, `ai.eval.completed|regressed`, `ai.guardrail.triggered`, `ai.budget.exceeded`, `ai.incident.reported`.
```text
POST /v1/ai/complete   POST /v1/ai/embed   POST /v1/ai/rerank
POST /v1/ai/models     POST /v1/ai/use-cases   POST /v1/ai/eval-suites/{id}:run   GET /v1/ai/costs?scope=&from=&to=
```
Errors: `AI_USE_CASE_UNREGISTERED`, `AI_DATA_CLASS_NOT_ALLOWED`, `AI_BUDGET_EXCEEDED`, `AI_GUARDRAIL_BLOCKED` (with category), `AI_NO_ROUTE` (no compliant model), `AI_PROVIDER_UNAVAILABLE`.

## 5. Security & Compliance
Prompt-injection defence (untrusted content isolated in delimited channels, never merged into system instructions; tool-call plans validated against policy before execution; sensitive tools need confirmation), output filtering, secret scanning of outputs, tenant isolation in caches/vector stores, zero-retention endpoints for restricted data. Frameworks: EU AI Act (risk classes, transparency, human oversight, logging, serious incident reporting), ISO/IEC 42001 controls, NIST AI RMF, India DPDP (purpose), sector rules (credit/insurance decisions: explainability, adverse action).

## 6. Gaps
```prolog
gap(ai_feature_without_use_case, C)  :- capability(C), uses_ai(C), not ai_use_case_for(C).
gap(use_case_without_eval, U)        :- ai_use_case(U), active(U), not eval_suite(U, _).
gap(high_risk_without_oversight, U)  :- ai_use_case(U), risk_class(U, high), oversight(U, none).
gap(no_compliant_route, U, J)        :- ai_use_case(U), in_scope(_, J), data_class(U, D), not route_model_allowed(U, J, D).
gap(model_card_missing, M)           :- model(M), certified(M), not model_card(M).
```

## 7. Operations, UI, Scale
Signals: `ai_requests_total{use_case,model}`, `ai_latency_ms`, `ai_tokens_total{in,out}`, `ai_cost{scope}` (Money), `guardrail_triggers_total{kind}`, `eval_score{suite,model}`, `fallback_total`. SLOs: gateway overhead p99 < 30 ms (excl. model); availability 99.95% with provider fallback. Views: AI Ops console (master W15), model registry & cards, use-case registry with risk classes, route editor (decision table), guardrail editor, eval dashboard (regression alerts), cost explorer, incident log. Scale: 10k+ req/s per region; streaming; provider quotas pooled per region with fair-share per tenant. T1 (T0 for fraud/risk ML via U94 inference).

## Appendix
- **A.** Self-hosted model tier (GPU cells) timing — P4 decision based on regulated-tenant demand.
- **C.** 0.1.0.
