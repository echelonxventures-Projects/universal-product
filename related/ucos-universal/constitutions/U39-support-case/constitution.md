# U39 — Support & Case Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U39-support` |
| Layer | L5 Business Capability |
| Domain | 06 Engagement |
| Steward | `ucos:org:engagement-support` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 |
| Depends on | U40 Communication (inbound conversations, replies), U109 Contact Centre (routing, agent desktop, voice), U13 Temporal (SLA clocks on business calendars, follow-ups), U60 Workflow (case processes), U11 Party, U26 Order / U35 Fulfillment / U29 Payment (context and actions), U34 Knowledge (help centre, answers), U51 Agent (AI support agent), U66 Privacy (DSRs arriving via support) |
| Depended on by | U71 Dispute (escalation), U38 CRM (service history), U82 Field Service (work orders from cases), U80 Warranty (claims intake), U70 Trust (review reports), grievance officer obligations (IN e-commerce, DPDP), U01 (appeals intake) |
| Master references | §6.2 U39, U109 (contact centre), master W17 (agent desktop) |

> Support owns **cases**: a customer's or partner's request or issue, its classification, priority, SLA, assignment, conversation links, actions taken on business objects (refund, reship, reschedule — through the owning universe's commands), resolution, satisfaction, and the help centre (self-service articles from U34). Real-time routing and the agent desktop belong to U109; Support owns the case record and its lifecycle.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| SUP-L1 | Every case has an SLA clock (first response, resolution) on the tenant's support calendar; pauses only in declared states (waiting on customer). | U13 SLA clocks; state-bound pause rules. |
| SUP-L2 | Agents act on business objects only through the owning universe's commands with their own authority; Support stores references, never copies of truth. | Action catalogue = commands of U26/U29/U35… |
| SUP-L3 | Legally mandated grievances (consumer, DPDP, payments) are flagged, routed to the named grievance officer and closed within statutory limits. | Decision `support.grievance-classification` + regulatory SLA. |
| SUP-L4 | AI-proposed replies and actions are labelled; autonomous resolution is limited to the agent's autonomy level (U51), and the customer can always reach a human. | U51 AG-laws; "talk to a human" always available. |

## 2. Objects
`Case { id, requester (party), subject refs (order/shipment/payment/subscription/asset…), channel, category (taxonomy), priority, status, assignee/team, sla: SLAClockRef[], conversations [U40], actions [{command, target, result}], resolution {code, notes}, csat?, grievance: bool, createdAt: TimePoint }` · `CaseCategory { taxonomy node, default priority, SLA policy, queue, required fields, macros }` · `Macro { steps (reply template + actions), category }` · `SLAPolicy { targets per priority: {firstResponse: Duration, resolution: Duration}, calendar (U13), pause states }` · `HelpArticle` (U34 knowledge item, published to help centre) · `SatisfactionSurvey { case, score, comment, at: TimePoint }`.

## 3. Lifecycle
`new → open → pending (waiting on customer; SLA paused) → open → resolved → closed` (reopen within the reopen window → open). Escalation to U71 creates a linked Dispute.

## 4. Commands, Events, APIs
Commands: `OpenCase`, `Classify` (AI-assisted), `Assign`, `Reply`, `ExecuteAction`, `SetPending`, `Resolve`, `Reopen`, `Escalate`, `MergeCases`, `RecordCsat`.
Events: `support.case.opened|assigned|resolved|reopened|escalated`, `support.sla.breached`, `support.csat.recorded`.
```text
POST /v1/support/cases   POST /v1/support/cases/{id}:assign|:reply|:resolve|:reopen|:escalate
POST /v1/support/cases/{id}/actions   GET /v1/support/help/articles?q=
```

## 5. Gaps, AI, Ops, UI
```prolog
gap(no_grievance_officer, T, J) :- tenant(T), in_scope(T, J), grievance_officer_required(J), not grievance_officer(T, J).
gap(case_category_without_sla, C) :- case_category(C), not sla_policy_for(C).
```
AI: classification and routing, suggested replies grounded in knowledge (RAG over U34 with citations), summarisation of long threads, autonomous resolution for low-risk intents ("where is my order") at autonomy L2–L3. Signals: `first_response_time`, `resolution_time`, `sla_breach_rate`, `csat`, `contact_rate_per_order`, `deflection_rate`. Views: case inbox, case detail with object timeline, macro editor, SLA policies, help centre, customer "my requests" page. T1.

## Appendix
- **C.** 0.1.0.
