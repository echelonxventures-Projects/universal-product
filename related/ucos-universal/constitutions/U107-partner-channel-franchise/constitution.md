# U107 — Partner, Channel & Franchise Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U107-partner` |
| Layer | L5 Business Capability |
| Domain | 03 Business |
| Steward | `ucos:org:partnerships` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P4 (partner programs, deal registration, MDF, reseller orders), P6 (franchise operations) |
| Depends on | U10 Org (partner organisations, TenantLink for franchise networks), U89 Contract (partner/franchise agreements), U23 Pricing (partner price lists, margins), U32 Loyalty & Incentive (affiliate/referral commissions), U30 Ledger (rebates, royalties, MDF accruals), U38 CRM (opportunities, deal registration), U28 Entitlement (partner tiers/benefits), U13 Temporal (program periods, royalty cycles), U101 QHSE (franchise audits) |
| Depended on by | B2B/distribution and franchise industry packs, U25 Marketplace (seller programs reuse tiers), U86 (co-marketing) |
| Master references | Completeness review A-54 (partner/channel/franchise was spread across specs) |

> Partner owns **indirect go-to-market and networked operations**: partner programs and tiers, partner onboarding and certification, deal registration and channel conflict rules, partner price lists and rebates, market development funds (MDF/co-op), reseller/distributor ordering and sell-through/inventory reporting, affiliate & referral programs (commission rules; payouts via U32/U30), and **franchise management** (franchisees as linked tenants/orgs, brand standards, royalty and fee calculation, operations audits, shared catalogues and promotions across the network).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| PRT-L1 | Partner benefits (discounts, MDF, rebates, royalties) derive from tiered program rules (decisions) and contracts — never ad-hoc. | U53 + U89 obligations. |
| PRT-L2 | Deal-registration conflicts resolve by declared rules (first-registered, territory, tier) with an auditable decision. | Decision + DecisionRecord. |
| PRT-L3 | Franchise networks share definitions (catalogue, promotions, standards) via TenantLink scopes; franchisee data stays franchisee-owned unless the agreement grants access. | ORG-L2 + link scopes. |
| PRT-L4 | Royalties/fees are computed from reported or system-observed sales per agreement and posted to Ledger with statements. | Calculation engine + U30. |

## 2. Objects
`PartnerProgram { kind: reseller|distributor|referral|affiliate|technology|service|franchise, tiers [{name, requirements, benefits}], period: TimeRange }` · `PartnerMembership { partner org, program, tier, certifications, status, validity: TimeRange }` · `DealRegistration { partner, customer prospect, opportunity (U38), products, territory, registeredAt: TimePoint, expiresAt: TimePoint, status }` · `MDFRequest { partner, activity, budget: Money, proof of performance, claim }` · `Rebate { program, basis (sell-in/sell-through), tiers, period: TimeRange, accrual }` · `SellThroughReport { partner, period: TimeRange, lines }` · `FranchiseAgreement` (U89) → `Franchisee { org, tenant link, territory (U12), outlets (U10 stores), standards checklist, royaltyRule, feeSchedule: Recurrence }` · `RoyaltyStatement { franchisee, period: TimeRange, base sales, royalty, fees, posted }`.

## 3. Commands, Events, APIs
Commands: `CreateProgram`, `EnrollPartner`, `RegisterDeal`, `ResolveConflict`, `SubmitMDF`, `ApproveMDF`, `ReportSellThrough`, `ComputeRebates`, `OnboardFranchisee`, `PublishNetworkCatalogue`, `ComputeRoyalties`, `AuditOutlet`.
Events: `partner.deal.registered|approved|expired`, `partner.tier.changed`, `franchise.royalty.statement-issued`.
```text
POST /v1/partner/programs   POST /v1/partner/deals   POST /v1/partner/mdf   POST /v1/franchise/franchisees   POST /v1/franchise/royalties:compute
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(franchise_without_agreement, F) :- franchisee(F), not active_agreement(F, franchise).
gap(program_without_rules, P)       :- partner_program(P), benefits(P, _), not decision_for(P).
```
AI: partner performance insights, channel-conflict detection, outlet audit photo checks. Views: partner portal (deal registration, price lists, MDF, training/certification, leads), channel manager console, franchise network dashboard (outlets map, compliance scores, royalties). T3.

## Appendix
- **C.** 0.1.0.
