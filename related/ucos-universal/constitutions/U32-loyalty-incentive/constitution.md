# U32 — Loyalty & Incentive Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U32-loyalty` |
| Layer | L5 Business Capability |
| Domain | 06 Engagement |
| Steward | `ucos:org:engagement-loyalty` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 |
| Depends on | U84 Stored Value (points balances as instruments), U30 Ledger (points liability, breakage), U13 Temporal (earn/expiry schedules, tier qualification periods, birthday triggers), U22 Offer (rewards as offers), U26 Order (earn on purchase), U53 Decision (earn/burn rules), U11 Party (membership), U69 Risk (abuse) |
| Depended on by | U24 Checkout (burn points), U86 Marketing (segments by tier), U107 Partner (coalition partners), U106/U46 (employee rewards) |
| Master references | §6.2 U32, U84 (balance owner) |

> Loyalty owns **programmes that reward behaviour**: programmes, membership, tiers and qualification, earn rules (purchase, referral, review, engagement), burn rules and catalogues, referral programmes, challenges/badges (gamification), partner/coalition earning, and incentive schemes (sales incentives, cashback). Point balances live in U84 as stored-value instruments; liability accounting in U30.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| LOY-L1 | Points are stored value: every earn/burn/expire is a U84 transaction with ledger posting (liability and breakage under IFRS 15). | U84 + U30 posting rules. |
| LOY-L2 | Earn and expiry follow published programme terms; expiry notices go out before points lapse. | Temporal triggers + U40 notices. |
| LOY-L3 | Points earned on returned/canceled purchases are reversed; pending points mature after the return window. | Earn state `pending → available` on Temporal window. |
| LOY-L4 | Referral and incentive rewards pass abuse checks (self-referral, device rings). | U69 risk scope `promotion`. |

## 2. Objects
`Programme { id, name, currency (points unit, U14 custom unit with Money valuation), terms (U89 doc), tiers, earnRules, burnRules, expiryPolicy }` · `Membership { party, programme, tier, tierPeriod: TimeRange, instrument (U84), joinedAt: TimePoint, status }` · `Tier { name, qualification (spend/points/activity in period), benefits [entitlement/offer refs] }` · `EarnRule { trigger event, condition (CEL), points formula, pendingFor: Duration }` · `BurnRule { conversion, minimum, eligible products/channels }` · `Referral { referrer, referee, code, reward rules, status }` · `Challenge { goal, period: TimeRange, reward }` · `IncentiveScheme { participants (sales reps, partners), metric, slabs, period, payout via U30/U46 }`.

## 3. Commands, Events, APIs
Commands: `Enrol`, `Earn` (from events), `Burn` (at checkout), `ReverseEarn`, `Expire` (scheduled), `EvaluateTier` (period end), `IssueReferral`, `CompleteReferral`, `EnrolChallenge`, `ComputeIncentive`.
Events: `loyalty.points.earned|burned|expired|reversed`, `loyalty.tier.changed`, `loyalty.referral.completed`.
```text
POST /v1/loyalty/programmes   POST /v1/loyalty/memberships   GET /v1/loyalty/memberships/{id}/balance
POST /v1/loyalty/redemptions   POST /v1/loyalty/referrals
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(points_without_ledger, T) :- tenant(T), capability(T, loyalty.core), not capability(T, ledger.core).
gap(no_expiry_notice, P)       :- programme(P), expiry_policy(P, _), not notice_trigger(P, expiry).
```
AI: personalised challenges, churn-risk tier saves, reward catalogue optimisation. Signals: `active_members`, `burn_rate`, `breakage_ratio`, `tier_migration`. Views: programme designer, member wallet (points, tier progress), rewards catalogue, referral share page, incentive statement. T1.

## Appendix
- **C.** 0.1.0.
