# UCOS — Commercial Model

| Field | Value |
|---|---|
| Author | Bipin Kumar |
| Version | 0.1 (proposal, to be validated with design partners in P1) |
| Date | 2026-10-03 |
| Related | [COST-MODEL.md](COST-MODEL.md), [TEAM-AND-ROADMAP-PLAN.md](TEAM-AND-ROADMAP-PLAN.md), U27 Subscription, U28 Entitlement, U23 Pricing, U57 pack marketplace |

## 1. Who pays and why
| Segment | Need | Entry phase |
|---|---|---|
| D2C brands (India, UAE) | A compliant storefront with GST/VAT, UPI, COD, WhatsApp and Indian/UAE carriers live in days, not months | P1 |
| B2B distributors | Price lists, credit terms, e-invoicing (IRN), sales rep apps | P1–P2 |
| Marketplace operators | Sellers, commissions, payouts, ledger and trust without building a finance stack | P2 |
| Mid-market and enterprise retailers | Omnichannel, contact centre, dedicated cells, residency, SLAs | P3–P4 |
| Vertical platforms (OTT, mobility, education, healthcare) | A new vertical composed from packs (P6 exit: zero kernel changes) | P5–P6 |
| ISVs and pack authors | Distribution of certified packs to every tenant | P3 onward |
| System integrators | Implementation revenue on a governed platform (U107 partner programme) | P2 onward |

**Positioning.** Other platforms give a fixed product plus apps. UCOS composes a platform per tenant from certified capabilities, with compliance, temporal behaviour and frames built in, and it explains every gap. The commercial promise is **"compliant by composition"**: a tenant sees, before go-live, which controls apply and that they are implemented (W6 gap report).

## 2. Plans (proposed list prices)
Each plan is a U28 entitlement plan. Features and quotas are checked through `Check(feature|quota)`, never hard-coded (ENT-L1).

| | Starter | Growth | Scale | Enterprise |
|---|---|---|---|---|
| Platform fee / month | ₹2,999 | ₹14,999 | ₹59,999 | from ₹4 L |
| GMV take rate | 0.50% | 0.25% | 0.15% | 0.10% (negotiable) |
| Typical tenant | ≤ 2k orders/month | ≤ 25k | ≤ 250k | > 250k, regulated |
| Stores / brands | 1 / 1 | 3 / 2 | 10 / 5 | unlimited |
| Channels | web, WhatsApp, email, SMS | + B2B portal, web push | + mobile apps, live chat | + voice, video, contact centre |
| Jurisdictions | 1 | 2 | 5 | any with packs |
| AI credits included / month | $2 | $15 | $120 | contract |
| Uptime SLA | 99.5% | 99.9% | 99.9% | 99.95% (dedicated cell) |
| Support | email, knowledge base | chat, business hours | 24×7, named CSM | 24×7, TAM, quarterly reviews |
| Data residency | region of the shared cell | region choice | region choice | dedicated cell in chosen region (+₹8 L/month) |

USD and AED price lists are kept in U23, with prices set per currency rather than converted. GST or VAT is charged on top.

**Marketplace operators** use Enterprise plus a marketplace fee of 0.1–0.2% of marketplace GMV, covering seller onboarding, commissions, payouts and ledger. UCOS never holds funds; payouts run through PSP split and route products.

## 3. Usage and pass-through
| Item | Billing |
|---|---|
| SMS (TRAI DLT), WhatsApp conversations, email above 50k/month | Provider cost + 15% handling |
| Voice minutes, video minutes, recordings storage (P3+) | Provider cost + 15% |
| AI usage above included credits | Cost + 20% |
| Maps and geocoding above the included quota | Cost + 15% |
| Carrier shipping labels | Tenant's own carrier contracts (preferred) or aggregator cost + handling |
| PSP fees | Paid by the tenant directly to the PSP under its own contract |

## 4. Pack marketplace
- First-party packs are included in plans according to their entitlements.
- Third-party paid packs: **80% to the author, 20% to UCOS**, collected through U27 and paid through U30 and U25.
- Certification fee for third-party packs: ₹50,000 per major version (covers `ARCH`, `SEC` and `TEST` gates). It is waived for packs from partner-programme members.
- Industry packs (U48) can be sold by partners as solution bundles.

## 5. Services
Onboarding packages (Starter: self-serve; Growth: ₹1.5 L fixed; Scale and Enterprise: scoped), catalogue migration, integrations, and training. Partners (SIs) deliver most services after P2. UCOS keeps a small expert team for the first ten Enterprise customers.

## 6. Contract terms
- Monthly or annual. Annual prepay has a 15% discount on the platform fee.
- SLA service credits: 10% of the monthly platform fee for each 0.1% below target, capped at 50%.
- A data processing agreement, sub-processor list and residency statement come with every contract (U66, U67).
- **No lock-in.** Full data export (objects, documents, events) is available at any time through APIs. Export at termination is free for 90 days.
- Price changes take effect with 60 days' notice. Existing customers keep their current price for 12 months after a change. Changes go through U02 governance.

## 7. Billing runs on UCOS itself
UCOS bills its tenants with its own capabilities: U27 subscriptions and usage rating, U28 entitlements, U23 price lists, U31 tax, U42 invoices, U30 ledger and U29 mandates (UPI AutoPay, cards). "Tenant zero" is the first production tenant and the first proof of the Phase 2 finance stack.

## 8. Targets
| Metric | Target | Source |
|---|---|---|
| Blended gross margin (excluding pass-through) | ≥ 75% | Cost model §3 |
| Net revenue retention | ≥ 110% (GMV growth plus tier upgrades) | U72 business metrics |
| CAC payback | ≤ 18 months (Growth and Scale) | Finance |
| Logo churn | ≤ 2% a month for Starter, ≤ 1% for Growth and above | U27 churn signals |
| Time to first order (Starter) | ≤ 3 days from signup | Genesis flow (W1/W2) |

## 9. Risks
| Risk | Mitigation |
|---|---|
| Merchants resist a GMV take rate | Offer a fixed-fee alternative for Scale and Enterprise (higher platform fee, no take rate) |
| Pass-through margins compress (e.g. WhatsApp price changes) | Pass-through is priced at cost plus a percentage, so price changes flow through. Rate cards are tracked as facts. |
| Large competitors bundle payments | UCOS stays PSP-neutral, with multi-PSP routing as a differentiator |
| Enterprise deals need heavy customisation | Extension points and packs only (ADR-001). Professional services are priced separately. |
