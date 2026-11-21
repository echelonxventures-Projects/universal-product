# U51 — Agent Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U51-agent` |
| Layer | L6 Intelligence |
| Domain | 07 Intelligence |
| Steward | `ucos:org:intelligence-agents` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 (agent registry, runtime, tools from commands, delegation, autonomy L1–L2, supervision, evals), P4 (multi-agent teams, external agents via MCP/A2A, L3 runbooks), P5 (L4 bounded autonomy in optimisation domains) |
| Depends on | U49 AI (gateway, use cases, guardrails), U50 Prompt, U09 Identity (agent identities, delegation tokens), U01 Authority (agent authorities ≤ level 2, AUTH-L5), U03 Policy (P-003 agent bounds), U63 API (MCP tool generation), U40 Communication (agent-protocol channel), U07 Knowledge Graph (grounding), U60 Workflow (human approval tasks), U28 Entitlement (agent quotas), U68 Audit, U13 Temporal (schedules, budgets windows, run deadlines), U77 Frame (realities for safe autonomy) |
| Depended on by | Catalog enrichment, support triage/bots (U39/U109), seller assistant, negotiation (U91), Studio assistant (U58), AIOps runbooks (U72/U73), Evolution proposals (U76), tenants' custom agents |
| Master references | §21.4–§21.5 (agent object & governance), §29.2 (autonomy levels), L17, P-003 |

> Agent owns **AI agents as accountable actors**: agent definitions (purpose, identity, authority, tools, memory, model route, guardrails, autonomy level, budgets), the **agent runtime** (plan → act → observe loops with policy-checked tool calls), **tools** (generated from capability commands/queries, plus external MCP tools), **memory** (episodic/semantic, tenant-scoped), **teams** (supervisor/worker patterns), **runs** and their full audit, **human-in-the-loop** approvals, **evaluations** and **kill switches**.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| AG-L1 | Every agent has its own identity (U09 kind=agent), an owner (human/org), a registered AI use case (U49) and an Authority (U01, level ≤ 2, no delegation). | Registry validation; runtime refuses unregistered agents. |
| AG-L2 | An agent can only call tools that (a) are in its tool list, (b) map to actions in its authority, (c) pass the PDP with the agent as principal — and when acting for a user, the intersection of agent authority and the user's permissions (delegation token, ID-L5). | Runtime tool broker + P-003 + delegation intersection. |
| AG-L3 | Autonomy level (master §29.2) is declared per agent × action class; actions above the level create a human task instead of executing. Irreversible financial, legal, security-weakening and constitutional actions are never autonomous. | Runtime gate + U60 tasks; forbidden action classes in platform policy. |
| AG-L4 | Agents run within budgets (money, tokens, actions per window, wall-clock deadline); exceeding any budget halts the run safely. | AIBudget (U49) + run limits. |
| AG-L5 | Every run is fully reconstructable: inputs (hashed/redacted), plan steps, tool calls with arguments and results, model/prompt versions, approvals, outcome. | Audit (U68) + run trace store. |
| AG-L6 | Agents treat all retrieved/user content as untrusted data; tool-call plans are validated before execution; high-risk tools require explicit confirmation. | Runtime + U49 guardrails + tool side-effect classes. |
| AG-L7 | Autonomous L4 behaviour is allowed in physical reality only inside declared optimisation bands; experimentation beyond them happens in simulated realities (U77) first. | Frame check + authority constraints. |
| AG-L8 | Any agent can be paused or revoked instantly (kill switch) by its owner, the tenant admin or platform security; revocation cancels in-flight runs and delegations. | Runtime subscription to revocation events; SLA ≤ 60 s. |

## 2. Objects
- `Agent` — master §21.4 schema, plus `kind: assistant|worker|supervisor|external`, `realitiesAllowed`, `killSwitch` state.
- `Tool { id (snake_case), source: command|query|mcp-external|function, maps: operationId | external server + tool name, inputSchema, outputSchema, sideEffect: read|reversible-write|irreversible-write|external-communication|financial, requiresConfirmation: bool, rateLimit }` — command/query tools are **generated** from capability manifests by U63 (`ai.tools` section) and inherit PDP checks.
- `AgentAuthority` — U01 Authority (autonomous type) with `actions`, `limits` (amount caps, counts), `validity`.
- `Memory { agent, tenant, kind: episodic|semantic|working, store (vector/graph), retention: RetentionRuleRef, dataClassesAllowed, consentScope }`
- `AgentTeam { supervisor agent, workers, handoff contracts (input/output schemas), escalation path }`
- `AgentRun { id, agent@version, trigger: user|event|schedule|agent, onBehalfOf?, goal, plan [{step, tool, args (redacted), result ref, status}], approvals [HumanTaskRef], cost: Money, tokens, startedAt: TimePoint, endedAt: TimePoint, outcome: success|partial|escalated|halted|failed, reason }`
- `AgentEvaluation` (U49 EvalSuite applied to agent tasks: task success, safety violations, cost per task, escalation precision).

## 3. Runtime (normative loop)
```text
run(agent, goal, ctx):
  assert agent.active ∧ use_case.active ∧ killSwitch = off ∧ budgets available
  ctx' ← narrow(ctx, actor=agent, onBehalfOf=user?, purpose=use_case.purpose)      # CTX-L2
  memory ← retrieve(agent.memory, goal, ctx')  ; grounding ← U07.Ground(goal, ctx', minTrust)
  loop until done ∨ budget/deadline exhausted ∨ max_steps:
     proposal ← U49.Complete(prompt=agent.prompt, tools=agent.tools, untrusted=[user input, retrieved docs])
     for call in proposal.tool_calls:
        validate schema; check tool ∈ agent.tools; side-effect class vs autonomy level
        decision ← PDP(principal=agent, onBehalfOf, action=call.operation, resource, ctx')
        if deny → record, feed back denial reason
        elif needs approval (level/side-effect/confirmation) → create HumanTask (U60) and pause (durable)
        else execute via Command Bus with idempotency key (run, step) → observe result
     record step (audit + trace)
  write memory (allowed classes only) ; emit agent.run.completed|escalated|halted
```
Runs execute as durable workflows (U60), so pauses for human approval survive restarts.

## 4. Commands, Queries, Events, APIs
Commands: `RegisterAgent` (governed), `PublishAgentVersion`, `GrantAgentAuthority`, `AttachTools`, `StartRun`, `ApproveStep`/`RejectStep`, `PauseAgent`, `RevokeAgent` (kill switch), `ClearMemory`, `DefineTeam`.
Queries: `RunTrace(run)`, `AgentsFor(useCase)`, `AgentScorecard(agent, range)`.
Events: `ai.agent-run.started|tool-called|awaiting-approval|completed|escalated|halted`, `ai.agent.revoked`.
External: agents are exposed to and can consume **MCP** tools (U63 MCP server; external MCP servers via U62 connectors with allow-lists); agent-to-agent messages via U40 E.6.
```text
POST /v1/agents   POST /v1/agents/{id}/runs   POST /v1/agents/runs/{id}/steps/{n}:approve|:reject
POST /v1/agents/{id}:pause|:revoke   GET /v1/agents/runs/{id}/trace
```
Errors: `AGENT_REVOKED`, `AGENT_TOOL_NOT_ALLOWED`, `AGENT_AUTHORITY_EXCEEDED`, `AGENT_BUDGET_EXHAUSTED`, `AGENT_APPROVAL_REQUIRED`.

## 5. Seed agents (P3–P4)
| Agent | Autonomy | Tools (examples) | Human gate |
|---|---|---|---|
| Catalog enrichment | L2 | get_listing, search_global_products, suggest_taxonomy, propose_attributes, propose_translation | confidence < 0.95 or regulated category |
| Support triage & reply drafting | L1–L2 | get_order, get_case, search_kb, draft_reply, propose_refund | refunds above limit; legal/complaint categories |
| Seller assistant | L1 | listing quality report, price suggestions, offer drafts | seller confirms every change |
| Shopping assistant (buyer-facing) | L1 (actions need confirmation) | search, compare, add_to_cart, track_order, start_return | checkout confirmation by buyer (policy `commerce.checkout.agent-confirmation`) |
| Studio builder assistant | L1 | compose_simulate, why, propose_definition | builder applies via Governance |
| Ops / AIOps responder | L3 within runbooks | scale, restart, failover-prep, open_case | outside runbook → page human |
| Compliance mapper | L1 | map_clause_to_control, gather_evidence | GRC approves mappings |

## 6. Gaps, Security, Ops, UI
```prolog
gap(agent_without_authority, A)   :- agent(A), active(A), not agent_authority(A, _).
gap(agent_tool_without_side_effect_class, T) :- tool(T), not side_effect(T, _).
gap(agent_without_kill_switch_test, A) :- agent(A), production(A), last_kill_switch_drill_days(A, D), D > 90.
gap(agent_irreversible_autonomous, A, T) :- agent(A), tool_of(A, T), side_effect(T, irreversible-write), autonomy(A, T, L), L >= 2.
```
Signals: `agent_runs_total{agent,outcome}`, `agent_task_success_ratio`, `agent_escalation_ratio`, `agent_cost_per_task`, `agent_policy_denials_total`, `agent_kill_switch_latency_s`. Views: master W15 (agent console) extended: agent catalogue, run trace explorer (step-by-step with redaction), approval inbox (U60 tasks), authority & tools editor, memory inspector (with purge), team designer, kill switch. T1.

## Appendix
- **A.** External agent marketplace (third-party agents as packs) — P5, requires publisher KYB and agent certification profile.
- **C.** 0.1.0.
