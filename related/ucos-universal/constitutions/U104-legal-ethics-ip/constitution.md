# U104 — Legal Matters, Ethics & Intellectual Property Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U104-legal` |
| Layer | L5 Business Capability |
| Domain | 08 Governance |
| Steward | `ucos:org:legal` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 |
| Depends on | U89 Contract, U42 Document, U11 Party, U13 Temporal (court dates, limitation periods, renewal deadlines), U60 Workflow, U68 Evidence (legal hold), U66 Privacy (whistleblower confidentiality), U67 Compliance, U18 Product (IP-protected products, counterfeits) |
| Depended on by | U68 (legal holds), U71 Dispute (escalation to litigation), U88 Social / U21 Catalog (IP infringement takedowns, brand protection), U103 (company law matters) |
| Master references | APQC 11.x/12.x legal; master "Legal Universe" (A-51) |

> Legal owns **legal matters, ethics cases and intellectual property**: matters (litigation, arbitration, regulatory investigations, legal advice requests), deadlines (limitation periods, hearings, filing dates), outside counsel & spend, legal holds (issuance, custodians, release — enforcing U68 holds), the **ethics & whistleblowing** channel (anonymous reporting, investigation, non-retaliation), and the **IP portfolio** (trademarks, patents, designs, copyrights, domains: filings, renewals, oppositions, licences) plus **brand protection** (counterfeit and infringement notices, marketplace takedowns).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| LEG-L1 | Matter documents are privileged/confidential by default; access is matter-team-only with audit. | Policy + classification `restricted`. |
| LEG-L2 | Legal holds suspend retention/deletion for all in-scope data until released by legal. | U68/U66 hold integration. |
| LEG-L3 | Whistleblower identity is protected (anonymous intake possible; reporter identity sealed); retaliation risk monitored. | Sealed fields; access only by designated ethics officers; EU Whistleblowing Directive. |
| LEG-L4 | IP renewal and limitation deadlines are SLA-tracked; missed deadlines are critical gaps. | Temporal deadline triggers. |

## 2. Objects
`Matter { kind: litigation|arbitration|regulatory|advisory|transactional|employment|ip, parties, jurisdiction/forum, status, team, counsel (orgs), budget/spend (U30), key dates [{kind, dueAt: TimePoint}], documents }` · `LegalHold { matter, scope (custodians, systems, data categories, date range: TimeRange), issuedAt: TimePoint, acknowledgements, releasedAt?: TimePoint }` · `EthicsReport { channel (web, hotline, email), anonymous: bool, category (fraud, harassment, bribery, safety, privacy…), sealed reporter, investigation, outcome, protections }` · `IPAsset { kind: trademark|patent|design|copyright|domain|trade-secret, title, jurisdictions, registration numbers, classes (Nice/IPC), status, filedAt: TimePoint, renewalDue: TimePoint, owner (org), licences (U89) }` · `InfringementCase { ipAsset, infringer, venue (marketplace listing/social post/domain), evidence, notice sent, takedown status }`.

## 3. Commands, Events, APIs
Commands: `OpenMatter`, `AddKeyDate`, `IssueLegalHold`, `ReleaseLegalHold`, `SubmitEthicsReport` (public, anonymous-capable), `AssignInvestigation`, `RegisterIPAsset`, `RenewIP`, `FileInfringementNotice`.
Events: `legal.hold.issued|released`, `legal.deadline.approaching`, `legal.ip.renewal-due`, `legal.ethics.report-received`, `legal.takedown.completed`.
Integrations: U21/U88 takedown endpoints (internal brand-protection programme for marketplaces: rights-owner registry → automated listing suppression with counter-notice flow).
```text
POST /v1/legal/matters   POST /v1/legal/holds   POST /public/ethics/reports   POST /v1/legal/ip-assets   POST /v1/legal/infringements
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(ip_renewal_missed_risk, A) :- ip_asset(A), renewal_due_within_days(A, 30), not renewal_task(A).
gap(no_ethics_channel, T)     :- tenant(T), employees_over(T, 50), whistleblowing_law(T), not capability(T, legal.ethics).
gap(hold_unacknowledged, H, P) :- legal_hold(H), custodian(H, P), not acknowledged(H, P).
```
AI: document review/summarisation (privileged workspace, zero-retention models), clause risk (with U89), counterfeit listing detection (image/text similarity against registered IP). Views: matter workspace, legal calendar, hold manager, ethics intake (anonymous, multilingual) and case room, IP portfolio map, brand-protection console. T3.

## Appendix
- **C.** 0.1.0.
