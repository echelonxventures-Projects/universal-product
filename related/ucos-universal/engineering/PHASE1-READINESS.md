# UCOS Ω∞ — Phase 1 Readiness Pack

| Field | Value |
|---|---|
| Document ID | `UCOS-P1-READINESS` |
| Version | 0.1.0 |
| Goal | Everything other than code that must exist for the **Phase 1 exit test**: a D2C store composed purely from `spec/composition/golden/d2c-in-ae.pd.yaml`, certified with `GAP-000`, completing real purchases in India and the UAE, with tax invoices issued. |
| Owners | Platform PM (overall); stewards named per item |

Status legend: ☐ not started · ◐ in progress · ☑ done. Lead time is calendar time, including external parties.

---

## 1. Seed content (data the platform runs on)

| # | Content | Owner universe / steward | Source | Volume | Lead time | Status |
|---|---|---|---|---|---|---|
| S1 | ISO 3166-1/2, ISO 4217, ISO 639/15924, IANA tz (pinned release), UCUM/Rec20 units, ITU calling codes | U08 / Reference steward | ISO, IANA, UN/ECE (licences checked) | ~25k codes | 1 wk | ☐ |
| S2 | ISIC Rev.4, NIC 2008, UN CPC 2.1, HS 2022 + India ITC-HS and UAE extensions, SAC, GS1 GPC*, UNSPSC* (*licence decision D-04) | U08 | UN Stats, CBIC, GS1, UNSPSC | ~60k codes | 2–4 wk (licensing) | ☐ |
| S3 | Address formats and subdivisions for IN and AE; PIN-code and emirate/area lists | U12 / Geo steward | CLDR/libaddressinput, India Post, UAE sources | ~20k | 2 wk | ☐ |
| S4 | Jurisdictions: IN (national, 36 states/UTs), AE (federal, 7 emirates, major free zones), with tax-region and residency-region links | U12 + U67 | Official gazettes | ~60 | 1 wk | ☐ |
| S5 | Holiday calendars 2026–2027: IN national and state, AE federal and emirate; business-hours templates; India and UAE fiscal calendars | U13 / Temporal steward per country | Government notifications | ~1k entries | 1 wk (+ yearly updates) | ☐ |
| S6 | Product taxonomy `ucos.product-category` v1 (~6k nodes), mapped to GS1 GPC, Google and CPC; attribute templates for the top 300 leaves; restricted-category profiles (IN, AE) | U06 + U18 / Taxonomy steward | Internal authoring + mappings | 6k nodes, ~2k attributes | 6–8 wk | ☐ |
| S7 | Regime packs: **GST India** (rates by HSN/SAC, place-of-supply rules, cess, TCS), **VAT UAE** (standard/zero/exempt, designated zones) | U31 / Tax steward + chartered accountant review | CBIC, FTA | ~12k rate rows | 4 wk (with expert review) | ☐ |
| S8 | Compliance library v1: controls and mappings for DPDP 2023 (+ Rules), CERT-In, e-commerce rules 2020, dark-pattern guidelines 2023, Legal Metrology, GST invoicing and e-invoicing, RBI PA and tokenisation, TRAI TCCCPR, UAE PDPL, UAE consumer protection, UAE VAT, PCI DSS v4 (SAQ-A scope), SOC 2 and ISO 27001 baseline, WCAG 2.2 | U67 / GRC + legal counsel (IN, AE) | Statutes; counsel interpretations | ~250 controls | 6 wk | ◐ (16 regulations, 23 controls in `spec/rules/facts`) |
| S9 | Message bundles: platform and storefront UI strings in en, hi and ar (legal strings reviewed by humans); notification templates (order, shipment, refund, OTP) with India DLT template IDs | U15 + U40 / L10n steward | Authoring + professional translation | ~3k keys × 3 locales | 4 wk | ☐ |
| S10 | Document templates: GST tax invoice (B2C and B2B with IRN/QR), bill of supply, credit note, receipt; UAE tax invoice (simple and full, EN/AR), credit note; packing slip; 4×6 label | U42 / Documents steward + tax review | Authoring | 12 templates | 3 wk | ☐ |
| S11 | Default decision tables (returns, COD, holds, stacking, cancellation, SCA requirement, velocity limits, transit matrix IN/AE) | U53 per owning pack | `spec/decisions/*` (4 done) | ~25 tables | 2 wk | ◐ |
| S12 | Platform plans (starter, growth, enterprise) with limits; features and quotas | U28 / Product | Pricing decision | 3 plans, ~30 quotas | 1 wk | ☐ |
| S13 | Industry template `single-brand-d2c@1` (+ `b2b-distribution@1` for testing) | U20 / Solutions architect | Derived from golden PDs | 2 | 1 wk | ◐ (golden PDs exist) |
| S14 | FX rate sources and RatePolicies (display, settlement, accounting) for INR and AED | U14 / Treasury | RBI reference rate, CBUAE, provider feed | — | 1 wk | ☐ |
| S15 | Golden test datasets: synthetic tenants, 10k listings, buyers, orders; payment, carrier and messaging simulator scripts | QA | Generated | — | 2 wk | ☐ |

## 2. External setup (business and vendor, longest lead times first)

| # | Item | Why | Lead time | Owner | Status |
|---|---|---|---|---|---|
| E1 | Legal entity(ies) for operating in IN and AE; tax registrations (GSTIN; UAE TRN if applicable) | Contracts, invoicing, PSP onboarding | 4–12 wk | Finance/legal | ☐ |
| E2 | PSP merchant accounts: Razorpay (platform or aggregator model decided), Network International N-Genius; webhook and sandbox access | Payments | 2–6 wk (KYB) | Payments lead | ☐ |
| E3 | India e-invoicing: GSP access to IRP, API credentials, sandbox | B2B invoices (b2b-in PD) | 2–4 wk | Tax lead | ☐ |
| E4 | India SMS: DLT entity registration, headers and templates on an operator portal; SMS provider account | OTP and notifications (TRAI) | 2–4 wk | Messaging lead | ☐ |
| E5 | UAE SMS sender ID registration (TDRA via provider) | OTP AE | 2–4 wk | Messaging lead | ☐ |
| E6 | WhatsApp Business: BSP account, WABA verification, template approvals | b2b-in channel | 2–4 wk | Messaging lead | ☐ |
| E7 | Email: sending domains, SPF/DKIM/DMARC, provider account, warm-up | Transactional email | 1–2 wk | Messaging lead | ☐ |
| E8 | Carriers: Shiprocket (IN) and Aramex (AE) business accounts, API keys, pickup locations | Shipping | 2–4 wk | Ops lead | ☐ |
| E9 | Cloud: accounts and quota in Mumbai (+ Hyderabad DR) and UAE (+ second UAE region/AZ for DR); KMS/HSM; budgets | Cells, residency | 2–3 wk | SRE lead | ☐ |
| E10 | Maps provider account (Google Maps Platform or Mapbox) with billing | Address autocomplete and geocoding | 1 wk | Platform | ☐ |
| E11 | Legal texts: Terms of Service, privacy notices (DPDP and PDPL; en/hi/ar), cookie policy, DPA template, seller terms (for later), grievance-officer appointment (IN) | Checkout terms; DPDP | 4–6 wk | Legal | ☐ |
| E12 | PCI DSS: confirm SAQ-A scope with a QSA, network-segmentation evidence | Card payments | 4 wk | Security | ☐ |
| E13 | Penetration test vendor booked for the P1 exit window | Gate SEC-* | 2 wk booking | Security | ☐ |
| E14 | Licences: GS1 GPC, UNSPSC redistribution (D-04); OSM vs commercial boundaries (D-12) | Taxonomy and geo seed | 2–6 wk | Legal | ☐ |

## 3. Phase 1 screen inventory (UI meta-model views to author)

| Portal | Views (ViewDefinition ids) | Wireframe | Priority |
|---|---|---|---|
| Storefront web | `storefront.home`, `storefront.plp`, `storefront.search` (+ `search.autocomplete`), `storefront.pdp` (price, offer badge, delivery promise, legal-metrology info), `cart.mini`, `storefront.cart`, `checkout.onepage` (address with `geo.address.form`, `temporal.slot-picker`, `checkout.payment`, `checkout.review`), `checkout.confirmation`, `storefront.account` (profile, addresses, passkeys), `storefront.orders`, `order.detail`/`storefront.order-tracking`, `return.request`, `storefront.page` (about, FAQ, policies, contact, grievance officer), `privacy.center`, `cookie.banner`, 404/500 | W12 (mobile) + to design | Must |
| Tenant admin | `admin.dashboard`, `admin.catalog` (+ `catalog.listing.edit`, `catalog.import.wizard`), `admin.pricing` (`pricing.pricelist.grid`), `admin.offers` (`offer.builder`, `temporal.policy.editor`), `admin.orders` (+ refunds, returns), `admin.inventory` (`inventory.balances.grid`), `admin.settings` (stores, hours, domains, locales, currencies, payment and carrier connections via `integration.instances`, tax registrations, invoice templates), `admin.users` (roles, invitations), `admin.compliance` (posture, DSR inbox), `billing.plan-and-usage` | W2–W10 (patterns) + to design | Must |
| Platform console (operators) | tenant list and provisioning, cells, packs and certifications, gap reports, governance inbox, audit explorer | W1, W6, W11, W16 | Must (minimal) |
| Builder Studio | P3. Phase 1 uses CLI and YAML for platform definitions (`ucos compose`). | W2–W8 | Later |
| Emails and documents | order confirmation, shipped, delivered, refund, OTP, password-less link, invoice PDF and labels (S10) | — | Must |

Design deliverables: design-system tokens and components v1 (master §23), high-fidelity designs for Must views in en (LTR) and ar (RTL), accessibility annotations, copy deck keyed to S9.

## 4. Spikes for open decisions (2-week time-boxes, P0 start)

| ID | Decision | Spike plan | Success criteria |
|---|---|---|---|
| S-01 | Composer Datalog engine (Soufflé vs embedded Rust/Go) | Port `spec/rules/core/closure.dl` and the facts. Reproduce both golden blueprints from `spec/composition/golden/expected/`. Measure with 1M synthetic facts. | Identical blueprints; < 10 s cold on 1M facts; derivation provenance available; incremental re-eval < 1 s for a one-fact change |
| S-02 | Identity provider (Keycloak vs Ory) | Multi-tenant issuers (100 tenants), passkeys, step-up ACR, token exchange (RFC 8693) for agents, 5k logins/s | Meets U09 SLOs; per-tenant issuer isolation; operational cost |
| S-03 | Expression language (CEL) | cel-go in schema constraints, decisions and policies context; parity tests TS/Go | Same results in both SDKs; performance < 50 µs per eval |
| S-04 | Runtime interpretation performance (ADR-001) | Object service with generic plus generated tables; 2k rps of AddLine on a reference cell | p99 < 150 ms end to end; no per-tenant code |
| S-05 | Workflow engine (Temporal.io vs Camunda 8) | Implement `order.lifecycle@3` and `commerce.checkout@1` via the interpreter workflow | Durable timers, sagas, versioning; ops cost |
| S-06 | Licensing D-04 and D-12 | Legal review of GS1, UNSPSC and OSM terms | Written decision recorded as a DecisionRecord |

## 5. Phase 1 exit test (scripted acceptance)
1. `ucos compose spec/composition/golden/d2c-in-ae.pd.yaml` produces the blueprint identical to `expected/d2c-in-ae.blueprint.json`, with `GAP-000` green.
2. Certification run passes ARCH, SEC (pen test with no open critical or high findings), CMP (22 controls implemented with fresh evidence), TEST, PERF (2k AddLine rps per cell), A11Y (WCAG 2.2 AA on Must views), DOC, OBS and DR (restore test).
3. Production activation in `cell-in-mum-1` and `cell-ae-dxb-1` through a governed proposal with canary.
4. **Real transactions:**
   - **IN:** a UPI purchase with GST invoice and delivery by the IN carrier; then a return and refund with a credit note.
   - **AE:** a card purchase (3DS) with an AR/EN VAT invoice; COD delivery with remittance reconciliation.
5. A DSR erasure test completes within its SLA with evidence. The audit chain verifies.
6. **Zero kernel code changes** were needed to add the second country after the first. Proof: git history plus a recorded `ucos coverage` and composition diff.
