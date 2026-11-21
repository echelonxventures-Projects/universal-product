# U71 — Dispute & Resolution Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U71-dispute` |
| Layer | Trust Plane |
| Domain | 08 Governance |
| Steward | `ucos:org:trust-disputes` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 |
| Depends on | U39 Support (escalations), U29 Payment (chargebacks, PSP dispute APIs), U25 Marketplace (buyer–seller claims, payout holds), U13 Temporal (response deadlines, evidence windows), U42 Document (evidence), U60 Workflow, U68 Audit, U01 Authority (appeals of governance decisions), U88 Social / U70 Trust (moderation appeals) |
| Depended on by | Moderation appeals (DSA Art. 20), risk adverse-action contests (RSK-L1), marketplace A-to-Z style guarantees, U89 contract disputes, ODR (online dispute resolution) obligations |
| Master references | §6.2 U71 |

> Dispute owns **contested outcomes**: buyer–seller claims, payment chargebacks and representments, moderation/decision appeals, contract disputes, the evidence collected, deadlines, decisions, and remedies executed through owning universes (refunds, reinstatement, payout release). It also provides the external ODR hand-off where law requires.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| DSP-L1 | Each party gets notice, the opposing claims, and a fair window to submit evidence; deadlines are Temporal and visible. | Workflow template; U13 deadlines. |
| DSP-L2 | Decision-makers are independent of the original decision (appeal ≠ same reviewer); automated decisions can be appealed to a human. | Assignment rule; DSA Art. 20, GDPR Art. 22. |
| DSP-L3 | Remedies execute through owning-universe commands and are audited. | Remedy = command ref + result. |
| DSP-L4 | Chargeback representments are submitted before the network deadline with complete evidence or are accepted deliberately (no silent loss). | Deadline alarms; decision record. |

## 2. Objects
`Dispute { id, kind: claim|chargeback|appeal|contract, parties [{party, role: claimant|respondent|operator}], subject refs, reason code (network/category), amount?: Money, status, deadlines [{name, at: TimePoint}], evidence [DocumentRef], decision {outcome, reasons, decidedBy, at: TimePoint}, remedies [{command, target, result}] }` · `Appeal` (dispute kind `appeal` with `appealedDecision` ref) · `ReasonCode { network/category, code, required evidence, responseDuration: Duration }`.

## 3. Lifecycle
`opened → awaiting_response → under_review → decided → (appealed → under_review → decided) → closed`. Chargebacks: `received → evidence → submitted → won|lost` (pre-arbitration/arbitration as extra states).

## 4. Commands, Events, APIs
Commands: `OpenDispute`, `IngestChargeback` (PSP webhook), `SubmitEvidence`, `RespondToClaim`, `Decide`, `Appeal`, `ExecuteRemedy`, `AcceptChargeback`, `Represent`.
Events: `dispute.dispute.opened|decided|appealed|closed`, `dispute.chargeback.received|won|lost`, `dispute.deadline.approaching`.
```text
POST /v1/disputes   POST /v1/disputes/{id}/evidence   POST /v1/disputes/{id}:decide|:appeal|:represent
```

## 5. Gaps, AI, Ops, UI
```prolog
gap(no_appeal_path, T)        :- tenant(T), capability(T, social.moderation), not capability(T, dispute.core).
gap(chargeback_unhandled, T)  :- tenant(T), capability(T, payment.core), phase_at_least(T, 3), not workflow(T, chargeback.flow).
```
AI: evidence pack assembly (order, delivery proof, communications), outcome prediction to decide accept vs represent, summarisation for reviewers. Signals: `chargeback_win_rate`, `dispute_resolution_time`, `appeal_overturn_rate`, `deadline_misses`. Views: dispute workbench (timeline, evidence, deadlines), party claim pages, chargeback queue. T1.

## Appendix
- **C.** 0.1.0.
