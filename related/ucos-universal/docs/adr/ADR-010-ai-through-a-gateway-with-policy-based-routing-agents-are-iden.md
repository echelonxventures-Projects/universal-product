# ADR-010: AI through a gateway with policy-based routing; agents are identities with bounded authority

| Field | Value |
|---|---|
| Status | Accepted (master v1.0; detailed in U49–U51) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §21; U49 AI/Model; U50 Prompt; U51 Agent |

## Context
AI features span many universes. Without a single entry point, providers, cost, data protection, evaluation and safety cannot be governed, and agents acting autonomously would bypass authorisation.

## Decision
Every model call goes through the **AI gateway** (U49). It resolves the registered AIUseCase, applies guardrails, routes by policy (data class, residency, cost, quality) and records usage and budgets. Default Claude routing: `claude-opus-5-5` for complex reasoning, `claude-sonnet-5-5` for general tasks, `claude-haiku-4-5-20251001` for high-volume low-latency work. Prompts are versioned code with tests (U50). **Agents** (U51) are identities with authority ≤ level 2, tool allow-lists with autonomy levels L0–L4, delegation that only narrows authority, durable runs and a kill switch.

## Alternatives considered
- Direct SDK calls from each pack: fast to start, but ungovernable.
- A single vendor everywhere: simpler, but creates lock-in and residency gaps.

## Consequences
**Positive**
- Vendor-agnostic, with cost and quality visible per use case.
- AI actions are authorised and audited like human actions.

**Negative / costs**
- The gateway adds a hop, so latency budgets must account for it.
- Every AI feature needs a registered use case and eval suite before production.

## Enforcement
`AI-UC-01`, `AI-EVAL-01`, `AI-CARD-01`, `AI-PROMPT-01`, `AI-AGENT-01`, `AI-REDTEAM-01`.
