# U60 — Workflow Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U60-workflow` |
| Layer | L8 Runtime Fabric |
| Domain | 09 Platform |
| Steward | `ucos:org:platform-kernel-workflow` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 |
| Depends on | U04 Meta (lifecycles), U13 Temporal (timers, SLA clocks), U53 Decision (routing, guards), U61 Event (signals), U03 Policy (task authorisation), U09 Identity (assignees), U40 Communication (notifications), U68 Audit |
| Depended on by | U26 Order, U24 Checkout, U35 Fulfillment, U02 Governance (approvals), U39 Support (P3), U66 DSR, U10 Org (provisioning), every long-running process |
| Master references | §16.1 (Workflow DSL), §13.3 (sagas), §13.1 (durable workflow engine) |

> Workflow owns **long-running, stateful orchestration**: workflow definitions (state machines + orchestration steps + sagas), workflow instances on a durable execution engine, human tasks (assignment, approval, escalation, SoD), compensation, signals, and the Workflow Designer model. Short business rules belong to Decision; timers/SLAs are Temporal objects the workflow uses.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| WF-L1 | Any process that spans more than one command/transaction, waits for time/humans/external events, or needs compensation, is a workflow on the durable engine — not ad-hoc state in pack tables + cron. | Certification review `ARCH-WF-01`; TMP-L4 (no own schedulers). |
| WF-L2 | Workflow definitions are versioned; running instances complete on the version they started (unless an explicit governed migration is applied). | Engine versioning + migration objects. |
| WF-L3 | Steps are idempotent and side effects go through commands with idempotency keys derived from (instance, step, attempt). | SDK. |
| WF-L4 | Human tasks enforce assignment policy and SoD (from Identity/Policy); approvals are recorded as DecisionRecords when they exercise authority (U01). | Task completion checks. |
| WF-L5 | Every state of a stateful object type that has a lifecycle is driven by its workflow; direct status writes are rejected. | Object Service guard for lifecycle fields. |

## 2. Objects
- **`WorkflowDefinition`** — master §16.1 DSL: `states`, `on` transitions, `entry`/`exit` actions (commands), `guards` (CEL/Decision), `timers` (Temporal refs), `saga` blocks with compensations, `humanTask`, `subworkflow`, `parallel` regions, `observability.slo`. Compiled to engine code (Temporal.io-class) by a generic interpreter workflow — **no per-definition code**.
- **`WorkflowInstance`** `{ id, definition@version, subject: ObjectRef, state, ctxEnvelope (origin), history (engine), startedAt: TimePoint, status: running|completed|failed|compensating|cancelled|suspended }`
- **`HumanTask`** `{ id, instance, kind: approve|review|input|exception, queue, assignmentRule: DecisionRef, candidates (roles/groups/users), assignee?, sla: SLAClockRef, form: ViewDefinitionRef, data, outcome options, sod: [rules], delegation allowed, status: open|claimed|completed|escalated|expired }`
- **`EscalationPolicy`** `{ levels: [{after: BusinessDuration (Temporal), to: role|manager-of-assignee, notify}], final: auto-decision|cancel|alert }`
- **`Migration`** (instance) `{ from@v, to@v, stateMapping, applicability CEL, approval }`

## 3. Execution model
- Interpreter workflow loads definition@version, executes deterministic transitions; activities = command calls via Command Bus (with context), decision evaluations, temporal operations, waits for signals (events mapped by subscription: e.g. `payment.payment-intent.captured` → `PaymentAuthorized` signal correlated by subject id).
- Sagas: ordered steps with compensations executed in reverse on failure; compensation failures → human task `exception`.
- Retries: per activity policy (exponential, max attempts, non-retryable error codes).
- Parallel regions & joins; subworkflows with result passing.

## 4. Commands, Queries, Events, APIs
Commands: `StartWorkflow(definition, subject, input)`, `Signal(instance, signal, payload)`, `CancelWorkflow`, `SuspendWorkflow`/`Resume`, `MigrateInstances(migration)`, `ClaimTask`, `CompleteTask(outcome, data)`, `ReassignTask`, `DelegateTask`.
Queries: `GetInstance`, `InstancesFor(subject)`, `TaskInbox(principal)`, `Timeline(instance)`, `StuckInstances(age)`.
Events: `workflow.instance.started|transitioned|completed|failed|compensated`, `workflow.task.created|claimed|completed|escalated`.
```text
POST /v1/workflow/instances            POST /v1/workflow/instances/{id}:signal|:cancel|:suspend|:resume
GET  /v1/workflow/tasks?inbox=me       POST /v1/workflow/tasks/{id}:claim|:complete|:reassign|:delegate
GET  /v1/workflow/definitions/{id}     POST /v1/workflow/migrations
```
Errors: `WF_INVALID_TRANSITION` (with allowed transitions), `WF_GUARD_FAILED`, `WF_TASK_NOT_ASSIGNED`, `WF_SOD_VIOLATION`, `WF_VERSION_MISMATCH`.

## 5. Validation
Static checks on definitions: reachability, dead-ends, every waiting state has a timer or external signal, every saga step has compensation or `none` declared, human tasks have forms and SLAs, guards reference existing decisions, commands exist and actor has authority. Simulation (W8): run N synthetic instances with stochastic event timings.

## 6. Security & Compliance
Task authorisation via PDP; approval tasks above authority level require step-up; complete audit of transitions and task outcomes; workflow data classification inherits from subject.

## 7. Gaps
```prolog
gap(workflow_dead_end, W, S)    :- workflow(W), state(W, S), not final(W, S), not exit_transition(W, S).
gap(human_task_without_sla, W, T) :- human_task(W, T), not sla(T).
gap(stuck_instances, W, N)       :- workflow(W), stuck_count(W, N), N > 0.
gap(lifecycle_without_workflow, T) :- object_type(T), has_lifecycle(T), not workflow_for(T).
```
Self-healing: stuck instance detector → retry activity / escalate / human task; engine shard failover.

## 8. AI
Workflow drafting from process descriptions (proposal + static validation + simulation), AI steps (`✦ AI step` in W8: classification, extraction, summarisation via AI gateway with guardrails, output schema validated, confidence → route to human if low), task assistance (pre-fill decisions with explanation).

## 9. Operations, UI, Scale
Signals: `workflow_instances_running{def}`, `transition_latency_ms`, `task_sla_breach_ratio{queue}`, `stuck_instances`, `compensations_total`. Views: W8 designer, `workflow.instance.timeline`, `task.inbox` (unified across universes, keyboard-first), `task.detail` (form + context + history), `workflow.ops.console` (stuck, failed, migrate). Scale: millions of concurrent instances per cell; engine cluster sharded; T0 for commerce workflows.

## Appendix
- **A.** Temporal.io vs Camunda 8 (master §31.1 recommends Temporal.io for durability; BPMN import supported by converter for enterprise customers).
- **D. Attribute definitions (A-74).** `WorkflowDefinition { id, version: string, subjectType: string, initial: string, states: [{name, entry, exit, timers}], transitions: [{from, on, to, guard, actions}], sagas: [{steps, compensations}], humanTasks: [string], subworkflows: [string], slo?: object, publishedAt?: TimePoint, status: draft|published|deprecated }` (master §16.1 DSL)
- **C.** 0.1.0.
