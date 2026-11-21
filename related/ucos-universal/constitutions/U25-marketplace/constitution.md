# U25 — Marketplace Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U25-marketplace` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce |
| Steward | `ucos:org:commerce-marketplace` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 |
| Depends on | U10 Org (sellers as Organizations), U09 Identity (KYB), U89 Contract (seller agreements), U21 Catalog, U26 Order (SellerOrders), U29 Payment (split/route payments, payouts), U30 Ledger (commissions, payables), U31 Tax (marketplace facilitator, TCS), U53 Decision, U70 Trust (seller ratings), U69 Risk, U13 Temporal (onboarding windows, settlement calendars, payout schedules), U28 Entitlement (seller plans) |
| Depended on by | U35 Fulfillment (seller-fulfilled vs operator-fulfilled), U22 Offer (seller-funded), U33 Advertising (sponsored), U107 (partner programs reuse tiers), reference compositions (Amazon-like, Airbnb-like, Uber-like two-sided) |
| Master references | §6.3 (Marketplace vs Commerce), §30 (compositions), master W13 |

> Marketplace owns **multi-sided economics**: seller onboarding and standing, seller agreements and policies, seller performance metrics, commission and fee plans, payout schedules and holds, seller-funded incentives accounting, marketplace facilitator obligations, and buyer–seller dispute escalation entry. Buying flow stays in Commerce/Order; money movement in Payment; books in Ledger.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| MKP-L1 | A seller transacts only after KYB, signed agreement and tax registration checks required by jurisdiction. | Onboarding workflow guard; U09/U89/U31 checks. |
| MKP-L2 | Commissions and fees are computed by versioned plans (decisions) and posted to Ledger; sellers receive itemised statements. | Plan engine + U30 posting rules + statements (U42). |
| MKP-L3 | Payout eligibility respects holds (return windows via Temporal, disputes, risk) and never exceeds the seller's payable balance. | Payout calculation guard (PAY-L5). |
| MKP-L4 | Ranking, fees and policies affecting sellers are transparent and applied equally per published rules (platform-to-business regulations, India e-commerce rules). | Published `MarketplacePolicy`; U44 ranking parameter disclosure; audit. |
| MKP-L5 | Seller standing changes (warnings, restrictions, suspension) follow a documented process with notice and appeal. | Workflow + U71 appeals. |

## 2. Objects
`Seller` = Organization (kind seller) + `SellerAccount { tier, plan (U28), standing, categoriesApproved, fulfilmentModes: [self-ship, marketplace-fulfilled, pickup], payoutAccount (U29 verified bank), taxProfile, metrics }` · `SellerAgreement` (U89) · `CommissionPlan { id, rules: DecisionRef (inputs: category, seller tier, price band, channel, promotion funding), fees: [referral %, fixed closing fee, fulfilment fee, payment fee pass-through, ads], validity }` · `PayoutSchedule { seller, recurrence (U13 on settlement calendar, e.g. T+7 after delivery), holdRules, minimum payout }` · `SellerStatement { seller, period: TimeRange, lines (orders, refunds, fees, commissions, adjustments, TCS/withholding), net }` · `SellerPerformance { seller, period, orderDefectRate, lateDispatchRate, cancellationRate, returnRate, rating (U70), responseTime }` · `MarketplacePolicy { kind: listing|pricing|returns|conduct|ranking-transparency, text, effectiveFrom: TimePoint }`.

## 3. Commands, Queries, Events, APIs
Commands: `ApplyAsSeller`, `CompleteKYB`, `ApproveSeller`/`RejectSeller`, `SignSellerAgreement`, `ApproveCategory`, `SetSellerStanding`, `DefineCommissionPlan`, `AccrueCommission` (from order events), `ComputePayout`, `ReleasePayout`, `HoldPayout`, `IssueStatement`.
Queries: `SellerDashboard`, `PayableBalance(seller)`, `PerformanceScorecard(seller)`, `NextPayout(seller)`.
Events: `marketplace.seller.approved|suspended|reinstated`, `marketplace.commission.accrued`, `marketplace.payout.scheduled|paid|held`, `marketplace.statement.issued`.
```text
POST /v1/marketplace/sellers (apply)   POST /v1/marketplace/sellers/{id}:approve|:suspend|:reinstate
POST /v1/marketplace/commission-plans  GET /v1/marketplace/sellers/{id}/payable   POST /v1/marketplace/payouts:run
```

## 4. Rules, Compliance, Gaps
Payout computation: payable = Σ(delivered order lines past return window − commissions − fees − refunds − chargebacks − TCS/withholding ± adjustments) − holds; scheduled per seller payout recurrence on the settlement calendar. Compliance: India e-commerce rules (seller details display, grievance, no preferential treatment disclosure), GST TCS for operators, EU P2B Regulation / DSA (trader traceability KYBC, ranking transparency), UAE commercial agency/e-commerce rules.
```prolog
gap(seller_without_agreement, S) :- seller(S), active(S), not signed_agreement(S, seller).
gap(no_commission_plan, T)       :- tenant(T), capability(T, marketplace.core), not commission_plan(T, _).
gap(trader_traceability, T, J)   :- tenant(T), in_scope(T, J), dsa_applies(J), not capability(T, identity.kyb).
```
AI: seller onboarding document checks, category approval assistance, listing compliance checks, seller performance coaching (seller assistant agent). Views: seller onboarding wizard, seller hub (master W13), operator seller-management console, commission plan editor, payout run cockpit, statements. T1.

## Appendix
- **C.** 0.1.0.
