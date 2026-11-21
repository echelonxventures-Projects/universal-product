# U100 — Financial Products Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U100-financial-products` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce (fintech) |
| Steward | `ucos:org:fintech` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 (fintech vertical: lending/BNPL distribution, insurance distribution, investment/brokerage), deeper core-banking via specialist packs |
| Depends on | U30 Ledger, U29 Payment, U09 Identity (KYC/AML), U69 Risk (credit/fraud), U53 Decision (eligibility/underwriting), U42 Document (agreements, disclosures), U13 Temporal (schedules, accrual, market sessions), U14 Currency (day-count, rounding), U67 Compliance, U66 Privacy (credit bureau consent) |
| Depended on by | U24 Checkout (BNPL/EMI at checkout), U80 Warranty (protection plans as insurance), U83 Rental (finance leases), industry fintech/brokerage packs (Zerodha-like, Robinhood-like, neobank) |
| Master references | Master §30.1 (Zerodha-like), chat "Insurance Product / Financial Product / Investment Product" |

> Financial Products owns **regulated financial products as composable definitions**: credit (loans, EMI, BNPL, credit lines), insurance (policies, protection plans, embedded insurance), deposits/savings, investment & brokerage (instruments, orders, holdings), and payments-adjacent products (cards issued via partners). It provides the **product model, eligibility/underwriting decisions, disclosures, schedules, servicing and distribution** — while licensed activities (lending book, underwriting risk, custody, exchange connectivity) are performed by **licensed partners via adapters** unless the tenant itself holds the licence.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| FIN-L1 | Every financial product declares the licence-holder of each regulated activity (originate, underwrite, service, custody, distribute) per jurisdiction; distribution without valid licence/partnership is impossible. | Composer rules + gap; Policy forbids activation. |
| FIN-L2 | Pre-contract disclosures (APR/KFS, policy wording, risk disclosures, costs & charges) are generated from the product definition and acknowledged before contracting. | Workflow guard; Document evidence. |
| FIN-L3 | Interest, fees, premiums and schedules are computed by Temporal/Currency primitives (day-count conventions, business calendars) and Ledger postings — reproducible to the paisa/cent. | Calculation engine golden tests. |
| FIN-L4 | Credit/insurance decisions are explainable, non-discriminatory (no protected attributes), and adverse-action reasons are communicated where law requires. | Decision model governance + U49 AI controls. |
| FIN-L5 | Suitability/appropriateness checks precede investment product sales where required. | Workflow step + evidence. |

## 2. Objects
`FinancialProduct { id, family: credit|insurance|deposit|investment|card|payment-account, subtype (term-loan, BNPL, EMI, credit-line, health, motor, device-protection, travel, FD, mutual-fund, equity, ETF, bond, derivative…), jurisdictions, licenceHolders: [{activity, partyOrg, licenceRef}], parameters (rates, tenors, fees, coverage, limits), eligibility: DecisionRef, underwriting: DecisionModelRef, disclosures: DocumentTemplateRefs, schedules: rules, servicingWorkflows }` ·
`Application { product, applicant(s), data, consents (bureau pull), decision, offer terms, status }` ·
`Contract/Account { product, holder, terms snapshot, ledgerAccounts, schedule (Recurrence + amounts), status }` ·
Credit: `RepaymentSchedule`, `Delinquency` (DPD buckets via Temporal), `Collection` workflow ·
Insurance: `Policy { coverage, insured object (unit U79/person/trip), premium schedule, insurer partner }`, `InsuranceClaim` (shared claim pattern with U80) ·
Investment: `Instrument { identifiers ISIN/ticker, exchange, type }`, `TradingOrder { side, type, qty, price, validity (market session Temporal), status }`, `Holding`, `CorporateAction`, `ContractNote`.

## 3. Commands, Queries, Events, APIs
Commands: `DefineFinancialProduct` (governed, compliance review), `Apply`, `Decide` (underwrite), `Accept` (after disclosures), `Disburse` (via partner/ledger), `PostRepayment`, `Restructure`, `Close`; insurance `Bind`, `Endorse`, `FileClaim`; investment `PlaceTradingOrder` (pre-trade risk checks), `Cancel/Modify`, `Settle` (T+N via Temporal SettlementDate).
Events: `financial.application.decided`, `financial.contract.activated`, `financial.repayment.due|missed|received`, `financial.policy.bound`, `financial.order.filled`.
Ports: `lending.partner`, `insurance.partner`, `broker.exchange-gateway`, `credit-bureau`, `account-aggregator` (India AA framework), `kyc` (U09).
```text
GET /v1/financial/products?family=   POST /v1/financial/applications   POST /v1/financial/applications/{id}:decide|:accept
GET /v1/financial/accounts/{id}/schedule      POST /v1/financial/orders (investment)
```

## 4. Compliance (seed)
India: RBI digital lending guidelines (KFS, direct disbursal, FLDG norms), IRDAI (corporate agency/distribution), SEBI (broker, KYC, margin, investor protection), Account Aggregator; EU: CCD2, IDD, MiFID II, PRIIPs KID; US: TILA/Reg Z, ECOA/Reg B, FINRA/SEC; UAE: CBUAE consumer protection. All as U67 regulation packs; product activation blocked until controls implemented.

## 5. Gaps
```prolog
gap(unlicensed_activity, P, A, J) :- financial_product(P), offered_in(P, J), regulated_activity(P, A, J), not licence_holder(P, A, J).
gap(disclosure_template_missing, P, J) :- financial_product(P), offered_in(P, J), required_disclosure(J, family(P), D), not template(P, D).
gap(model_governance_missing, P) :- financial_product(P), underwriting_model(P, M), not certified_model(M).
```

## 6. AI & Ops & UI & Scale
AI: underwriting/fraud models (governed, explainable), collections prioritisation, advice only where licensed (robo-advice is regulated). Signals: `approval_rate{product}`, `dpd_buckets`, `claim_ratio`, `order_latency_ms` (brokerage p99 < 50 ms to gateway). Views: product configurator (governed), application journeys (with disclosure acknowledgements), account/servicing portals, trading screens (pack). Scale & tiers: brokerage trading path T0 with dedicated cells; others T1.

## Appendix
- **A.** Which financial activities UCOS as a platform operator will hold licences for vs partner-only — business/legal decision.
- **C.** 0.1.0.
