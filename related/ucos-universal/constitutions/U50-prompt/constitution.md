# U50 — Prompt Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U50-prompt` |
| Layer | L6 Intelligence |
| Domain | 07 Intelligence |
| Steward | `ucos:org:intelligence-ai-platform` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 |
| Depends on | U49 AI (use cases, eval suites), U15 Localization (localised prompts, glossaries), U02 Governance (prompt changes), U74 Certification (AI gates), U95 Software Delivery (prompts as code), U13 Temporal (validity) |
| Depended on by | U51 Agent, every AI use case (via U49 gateway) |
| Master references | §21 (prompt registry), §21.5 (rollback to previous prompt) |

> Prompt owns **prompts as versioned, tested, governed definitions**: prompt templates (system/developer/user parts, variables, tool and output-schema bindings), prompt versions and releases, tenant-level overrides within bounds (brand voice, tone, glossary), prompt tests and evaluations, and A/B experiments of prompt variants. No prompt text lives in pack code.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| PR-L1 | Prompts are registered definitions referenced by id@version from use cases; inline prompt strings in code are forbidden. | Lint (`PROMPT-LINT-001`) on packs; gateway requires `prompt_ref`. |
| PR-L2 | Each prompt version ships with tests (golden inputs → assertions) and passes its use case's eval suite before release. | Certification gate `AI-PROMPT-01`. |
| PR-L3 | Variables are typed and classified; restricted data may only bind to variables marked allowed for that class and use case. | Template schema + gateway check (AI-L3). |
| PR-L4 | Untrusted content (user input, retrieved documents, web content) is bound only to delimited untrusted slots, never interpolated into instructions. | Template validator: variables of kind `untrusted` restricted to designated slots. |
| PR-L5 | Tenant overrides may adjust tone/brand/glossary/examples within declared `overrideBounds`; they cannot remove safety or policy instructions. | Override validator + diff review. |

## 2. Objects
- `PromptTemplate { id, useCase, parts: [{role: system|developer|user|assistant-example, text (with {{vars}}), locale}], variables: [{name, type, classification, kind: trusted|untrusted, required}], tools: [ToolRef], outputSchema: JSON Schema ref, modelHints: {minCapability, temperature, maxTokens}, overrideBounds, owner, status }`
- `PromptVersion { template, version (SemVer), contentHash, changelog, evalResults: [EvalResultRef], released: bool, validity: TimeRange }`
- `PromptOverride { tenant, template, fields (tone, brandVoice glossary ref U15, examples), version, approvedBy }`
- `PromptTest { template@version, input variables, assertions: [{kind: schema-valid|contains|not-contains|llm-judge|exact|regex|grounded-in, spec}] }`
- `PromptExperiment { variants: [PromptVersionRef], allocation, primary metric (U72), guardrail metrics, period: TimeRange }`

## 3. Commands, Queries, Events, APIs
Commands: `CreatePromptTemplate`, `ProposePromptVersion` (via Governance; standard class for minor wording with passing evals, significant for safety-related changes), `RunPromptTests`, `ReleasePromptVersion`, `RollbackPromptVersion`, `CreateOverride`, `StartPromptExperiment`.
Queries: `Render(template@version, variables, tenant, locale)` (used by gateway; returns rendered messages + hashes), `Diff(v1, v2)`, `ActiveVersion(template, tenant)`.
Events: `prompt.version.released|rolled-back`, `prompt.test.failed`.
```text
POST /v1/prompts   POST /v1/prompts/{id}/versions   POST /v1/prompts/{id}/versions/{v}:test|:release|:rollback
POST /v1/prompts/{id}/overrides   POST /v1/prompts/{id}:render (internal)
```
Storage: prompts as code in the definitions repo (`spec/ai/prompts/**`), synced with the registry (U95 SDLC-L3).

## 4. Gaps, Security, Ops, UI
```prolog
gap(prompt_without_tests, P)       :- prompt_version(P), released(P), not prompt_tests(P).
gap(untrusted_var_in_instructions, P) :- prompt_template(P), untrusted_variable_in_system_part(P).
gap(inline_prompt_in_code, Pack)   :- pack(Pack), lint_violation(Pack, prompt_lint_001).
```
Security: prompt content `internal`; tenant overrides `confidential`; rendered prompts with personal data never logged in clear (hash + redacted sample). Signals: `prompt_test_pass_ratio`, `prompt_version_eval_delta`, `prompt_rollbacks_total`. Views: prompt editor (parts, variables with classification, live render with sample data, test runner, eval comparison between versions, diff), override editor (bounded fields only), experiment console. T1.

## Appendix
- **C.** 0.1.0.
