# UCOS Universe Constitutions

This folder holds one detailed specification per universe. They are the second level of the UCOS documentation, below `../UCOS-MASTER-ARCHITECTURE.md`. Each spec follows `_TEMPLATE.md` (12 sections, per master §12.5) and MUST NOT contradict the master. Where a spec needs the master to change, it lists the change in its Appendix B. Those changes are collected below for a governed update.

## Shared conventions (apply to every spec)

| Item | Convention | Example |
|---|---|---|
| Universe id | `U<NN>-<slug>` | `U13-temporal` |
| Object type id | `<universe-slug>.<area>.<PascalName>` or `ucos.<slug>.<PascalName>` | `ucos.temporal.Reservation` |
| Object id | `ucos:<kind>:<ULID>`; reference data `ucos:<kind>:<ns>/<key>` | `ucos:tmp:01J…`, `ucos:jur:IN-KA` |
| Command | PascalCase verb phrase | `HoldReservation` |
| Permission / action | `<slug>:<Command>` | `temporal:HoldReservation` |
| Event type | `<slug>.<object-kebab>.<past-tense>` | `temporal.reservation.held` |
| REST | `/v1/<slug>/<collection>[/{id}][:command]` | `POST /v1/temporal/reservations/{id}:confirm` |
| Error code | `<SLUG-UPPER>_<REASON>` | `TMP_CAPACITY_EXHAUSTED` |
| Universe law | `<SLUG-UPPER>-L<n>` | `TMP-L4` |
| Lint rule | `<SLUG-UPPER>-LINT-<nnn>` | `META-LINT-001` |
| Certification gate | `<GATE>-<SLUG>-<nn>` | `ARCH-TMP-02` |
| Gap rules | Datalog, same predicate vocabulary as master §11.3 | `gap(kind, …) :- …` |
| Policies | Cedar | |
| Decision tables | `<slug>.<name>`, tenant-configurable, with defaults | `identity.required-aal` |

## Status of all universes

Legend: ✅ specified (v0.1 draft) · ⬜ planned (phase per master §32).

### Phase 0 — Foundations & kernel (23 universes)

| ID | Universe | Status | Spec |
|---|---|---|---|
| U04 | Meta | ✅ | [U04-meta](U04-meta/constitution.md) |
| U08 | Reference Data | ✅ | [U08-reference-data](U08-reference-data/constitution.md) |
| U09 | Identity | ✅ | [U09-identity](U09-identity/constitution.md) |
| U10 | Organization & Tenant | ✅ | [U10-organization-tenant](U10-organization-tenant/constitution.md) |
| U11 | Person & Party | ✅ | [U11-person-party](U11-person-party/constitution.md) |
| U12 | Geography | ✅ | [U12-geography](U12-geography/constitution.md) |
| U13 | Temporal | ✅ | [U13-temporal](U13-temporal/constitution.md) |
| U14 | Currency & Unit | ✅ | [U14-currency-unit](U14-currency-unit/constitution.md) |
| U15 | Language & Localization | ✅ | [U15-localization](U15-localization/constitution.md) |
| U16 | Context | ✅ | [U16-context](U16-context/constitution.md) |
| U01 | Authority| ✅ | [U01-authority](U01-authority/constitution.md) |
| U02 | Governance| ✅ | [U02-governance](U02-governance/constitution.md) |
| U03 | Policy| ✅ | [U03-policy](U03-policy/constitution.md) |
| U05 | Ontology| ✅ | [U05-ontology](U05-ontology/constitution.md) |
| U06 | Taxonomy| ✅ | [U06-taxonomy](U06-taxonomy/constitution.md) |
| U57 | Capability| ✅ | [U57-capability](U57-capability/constitution.md) |
| U58 | Composition| ✅ | [U58-composition](U58-composition/constitution.md) |
| U61 | Event| ✅ | [U61-event](U61-event/constitution.md) |
| U65 | Security| ✅ | [U65-security](U65-security/constitution.md) |
| U68 | Audit & Evidence| ✅ | [U68-audit-evidence](U68-audit-evidence/constitution.md) |
| U73 | Infrastructure & Deployment| ✅ | [U73-infrastructure-deployment](U73-infrastructure-deployment/constitution.md) |
| U74 | Certification| ✅ | [U74-certification](U74-certification/constitution.md) |
| U75 | Discovery & Gap| ✅ | [U75-discovery-gap](U75-discovery-gap/constitution.md) |

### Phase 1 — Composer + commerce core (23 universes)

| ID | Universe | Status | Spec |
|---|---|---|---|
| U07 | Knowledge Graph | ✅ | [U07-knowledge-graph](U07-knowledge-graph/constitution.md) |
| U18 | Product Intelligence | ✅ | [U18-product-intelligence](U18-product-intelligence/constitution.md) |
| U19 | Service Intelligence | ✅ | [U19-service-intelligence](U19-service-intelligence/constitution.md) |
| U20 | Industry | ✅ | [U20-industry](U20-industry/constitution.md) |
| U21 | Catalog | ✅ | [U21-catalog](U21-catalog/constitution.md) |
| U22 | Offer | ✅ | [U22-offer](U22-offer/constitution.md) |
| U23 | Pricing | ✅ | [U23-pricing](U23-pricing/constitution.md) |
| U24 | Commerce (Cart & Checkout) | ✅ | [U24-commerce-cart-checkout](U24-commerce-cart-checkout/constitution.md) |
| U26 | Order | ✅ | [U26-order](U26-order/constitution.md) |
| U29 | Payment | ✅ | [U29-payment](U29-payment/constitution.md) |
| U31 | Tax | ✅ | [U31-tax](U31-tax/constitution.md) |
| U34 | Inventory | ✅ | [U34-inventory](U34-inventory/constitution.md) |
| U35 | Fulfillment | ✅ | [U35-fulfillment](U35-fulfillment/constitution.md) |
| U40 | Communication | ✅ | [U40-communication](U40-communication/constitution.md) |
| U43 | Asset | ✅ | [U43-asset](U43-asset/constitution.md) |
| U44 | Search | ✅ | [U44-search](U44-search/constitution.md) |
| U53 | Decision | ✅ | [U53-decision](U53-decision/constitution.md) |
| U60 | Workflow | ✅ | [U60-workflow](U60-workflow/constitution.md) |
| U63 | API | ✅ | [U63-api](U63-api/constitution.md) |
| U64 | UI, App & Channel | ✅ | [U64-ui-app-channel](U64-ui-app-channel/constitution.md) |
| U66 | Privacy & Consent | ✅ | [U66-privacy-consent](U66-privacy-consent/constitution.md) |
| U67 | Compliance | ✅ | [U67-compliance](U67-compliance/constitution.md) |
| U72 | Observability & Analytics | ✅ | [U72-observability-analytics](U72-observability-analytics/constitution.md) |

### Coverage expansion — every domain, any frame (24 universes, from the completeness review)

See [COVERAGE-REGISTER.md](COVERAGE-REGISTER.md) for the full map of domains to owners and the extensibility protocol, and [TEMPORAL-BINDING-MATRIX.md](TEMPORAL-BINDING-MATRIX.md) for how every universe uses calendars, scheduling, triggers and time ranges.

| ID | Universe | Phase | Status | Spec |
|---|---|---|---|---|
| U77 | Existence & Reality Frame | P0 | ✅ | [U77-existence-reality-frame](U77-existence-reality-frame/constitution.md) |
| U78 | Product Configuration | P2 | ✅ | [U78-product-configuration](U78-product-configuration/constitution.md) |
| U79 | Physical Asset & Installed Base | P3 | ✅ | [U79-physical-asset-installed-base](U79-physical-asset-installed-base/constitution.md) |
| U80 | Warranty & After-sales | P3 | ✅ | [U80-warranty-after-sales](U80-warranty-after-sales/constitution.md) |
| U81 | Ticketing & Events | P6 | ✅ | [U81-ticketing-events](U81-ticketing-events/constitution.md) |
| U82 | Field Service & Work Management | P5 | ✅ | [U82-field-service-work](U82-field-service-work/constitution.md) |
| U83 | Rental & Leasing | P5 | ✅ | [U83-rental-leasing](U83-rental-leasing/constitution.md) |
| U84 | Stored Value & Wallet | P2 | ✅ | [U84-stored-value-wallet](U84-stored-value-wallet/constitution.md) |
| U85 | Customer Data & Segmentation (CDP) | P3 | ✅ | [U85-customer-data-segmentation](U85-customer-data-segmentation/constitution.md) |
| U86 | Marketing Automation | P4 | ✅ | [U86-marketing-automation](U86-marketing-automation/constitution.md) |
| U87 | Web Presence & SEO | P1 | ✅ | [U87-web-presence-seo](U87-web-presence-seo/constitution.md) |
| U88 | Social & Community | P5 | ✅ | [U88-social-community](U88-social-community/constitution.md) |
| U89 | Contract & Agreement | P2 | ✅ | [U89-contract-agreement](U89-contract-agreement/constitution.md) |
| U90 | Global Trade & Customs | P2 | ✅ | [U90-global-trade-customs](U90-global-trade-customs/constitution.md) |
| U91 | Auction, Bidding & Negotiation | P5 | ✅ | [U91-auction-bidding-negotiation](U91-auction-bidding-negotiation/constitution.md) |
| U92 | IoT & Devices | P5 | ✅ | [U92-iot-devices](U92-iot-devices/constitution.md) |
| U93 | Data Governance & Data Products | P2 | ✅ | [U93-data-governance-products](U93-data-governance-products/constitution.md) |
| U94 | ML Platform | P2 | ✅ | [U94-ml-platform](U94-ml-platform/constitution.md) |
| U95 | Software Delivery & Source Control (Git) | P0 | ✅ | [U95-software-delivery-source-control](U95-software-delivery-source-control/constitution.md) |
| U96 | Work & Collaboration | P5 | ✅ | [U96-work-collaboration](U96-work-collaboration/constitution.md) |
| U97 | Forms, Surveys & Feedback | P3 | ✅ | [U97-forms-surveys-feedback](U97-forms-surveys-feedback/constitution.md) |
| U98 | Sustainability & ESG | P6 | ✅ | [U98-sustainability-esg](U98-sustainability-esg/constitution.md) |
| U99 | Digital Assets & Distributed Ledger | P6 | ✅ | [U99-digital-assets-ledger-tech](U99-digital-assets-ledger-tech/constitution.md) |
| U100 | Financial Products | P6 | ✅ | [U100-financial-products](U100-financial-products/constitution.md) |

### Standards-based completeness (8 universes; ISIC, CPC and APQC mapped)

See [INDUSTRY-PRODUCT-DOMAIN-CATALOGUE.md](INDUSTRY-PRODUCT-DOMAIN-CATALOGUE.md): 88/88 ISIC divisions, 71/71 CPC divisions and 13/13 APQC categories each have an owner.

| ID | Universe | Phase | Status | Spec |
|---|---|---|---|---|
| U101 | Quality, Health, Safety & Environment (QHSE) | P5 | ✅ | [U101-quality-ehs](U101-quality-ehs/constitution.md) |
| U102 | Strategy & Performance Management | P5 | ✅ | [U102-strategy-performance](U102-strategy-performance/constitution.md) |
| U103 | Corporate Governance & Equity | P6 | ✅ | [U103-corporate-governance-equity](U103-corporate-governance-equity/constitution.md) |
| U104 | Legal Matters, Ethics & IP | P6 | ✅ | [U104-legal-ethics-ip](U104-legal-ethics-ip/constitution.md) |
| U105 | Workplace & Facilities | P6 | ✅ | [U105-workplace-facilities](U105-workplace-facilities/constitution.md) |
| U106 | Travel & Expense | P6 | ✅ | [U106-travel-expense](U106-travel-expense/constitution.md) |
| U107 | Partner, Channel & Franchise | P4 | ✅ | [U107-partner-channel-franchise](U107-partner-channel-franchise/constitution.md) |
| U108 | Product Development, R&D & Innovation | P6 | ✅ | [U108-product-development-rnd](U108-product-development-rnd/constitution.md) |

### Phase 1 blockers closed (3 universes)

| ID | Universe | Phase | Status | Spec |
|---|---|---|---|---|
| U28 | Entitlement | P0/P1 | ✅ | [U28-entitlement](U28-entitlement/constitution.md) |
| U42 | Document | P1 | ✅ | [U42-document](U42-document/constitution.md) |
| U62 | Integration | P1 | ✅ | [U62-integration](U62-integration/constitution.md) |

Engineering companions: [../engineering/KERNEL-DESIGN.md](../engineering/KERNEL-DESIGN.md) (core engines), [../engineering/PHASE1-READINESS.md](../engineering/PHASE1-READINESS.md) (seed content, external setup, screens, spikes, exit test), and [../spec/README.md](../spec/README.md) (machine-readable definitions, validated by `tools/ucos_check.py`).

### Communication completeness (1 universe + U40 extension)

| ID | Universe | Phase | Status | Spec |
|---|---|---|---|---|
| U109 | Real-time Communications & Contact Centre | P3 | ✅ | [U109-realtime-comms-contact-center](U109-realtime-comms-contact-center/constitution.md) |

### Phase 2 — Marketplace, finance, logistics

| ID | Universe | Phase | Status | Spec |
|---|---|---|---|---|
| U17 | Resource | P2 | ✅ | [U17-resource](U17-resource/constitution.md) |
| U25 | Marketplace | P2 | ✅ | [U25-marketplace](U25-marketplace/constitution.md) |
| U27 | Subscription & Billing | P2 | ✅ | [U27-subscription](U27-subscription/constitution.md) |
| U30 | Ledger & Finance | P2 | ✅ | [U30-ledger-finance](U30-ledger-finance/constitution.md) |
| U36 | Logistics | P2 | ✅ | [U36-logistics](U36-logistics/constitution.md) |
| U59 | Generation | P2 | ✅ | [U59-generation](U59-generation/constitution.md) |
| U69 | Risk | P2 | ✅ | [U69-risk](U69-risk/constitution.md) |
| U70 | Trust & Reputation | P2 | ✅ | [U70-trust-reputation](U70-trust-reputation/constitution.md) |

### Phase 3 — Builders, CRM/support, AI v1

| ID | Universe | Phase | Status | Spec |
|---|---|---|---|---|
| U32 | Loyalty & Incentive | P3 | ✅ | [U32-loyalty-incentive](U32-loyalty-incentive/constitution.md) |
| U38 | CRM | P3 | ✅ | [U38-crm](U38-crm/constitution.md) |
| U39 | Support & Case | P3 | ✅ | [U39-support-case](U39-support-case/constitution.md) |
| U49 | AI/Model | P3 | ✅ | [U49-ai-model](U49-ai-model/constitution.md) |
| U50 | Prompt | P3 | ✅ | [U50-prompt](U50-prompt/constitution.md) |
| U51 | Agent | P3 | ✅ | [U51-agent](U51-agent/constitution.md) |
| U71 | Dispute & Resolution | P3 | ✅ | [U71-dispute-resolution](U71-dispute-resolution/constitution.md) |
| U76 | Evolution | P3 | ✅ | [U76-evolution](U76-evolution/constitution.md) |

### Phase 4–6 — Intelligence, verticals

| ID | Universe | Phase | Status | Spec |
|---|---|---|---|---|
| U33 | Advertising | P4 | ✅ | [U33-advertising](U33-advertising/constitution.md) |
| U41 | Content & Media | P4 | ✅ | [U41-content-media](U41-content-media/constitution.md) |
| U45 | ERP/Procurement | P4 | ✅ | [U45-erp-procurement](U45-erp-procurement/constitution.md) |
| U46 | Workforce/HRMS | P4 | ✅ | [U46-workforce-hrms](U46-workforce-hrms/constitution.md) |
| U52 | Recommendation | P4 | ✅ | [U52-recommendation](U52-recommendation/constitution.md) |
| U37 | Mobility & Dispatch | P5 | ✅ | [U37-mobility-dispatch](U37-mobility-dispatch/constitution.md) |
| U54 | Simulation | P5 | ✅ | [U54-simulation](U54-simulation/constitution.md) |
| U55 | Digital Twin | P5 | ✅ | [U55-digital-twin](U55-digital-twin/constitution.md) |
| U56 | Learning | P5 | ✅ | [U56-learning](U56-learning/constitution.md) |
| U47 | Manufacturing | P6 | ✅ | [U47-manufacturing](U47-manufacturing/constitution.md) |
| U48 | Industry Packs | P6 | ✅ | [U48-industry-packs](U48-industry-packs/constitution.md) |

**Progress:** 109 of 109 universes specified (100%). Phases 0 and 1 are specified in depth; Phases 2–6 at v0.1 depth (laws, objects, commands, events, APIs, gap rules, UI). Communication is complete (U40 + U109). `spec/` checks clean: 165 manifests, 613 object-type schemas, 55 gates, 219 error codes, 0 errors, and three reference platform definitions (D2C IN+AE, B2B IN, omnichannel IN) compose with 0 gaps.

## Amendments register (to fold into the master via a governed change)

| # | From | Amendment |
|---|---|---|
| A-01 | U04 | Register `Classification` as a ValueType owned by U65 Security. |
| A-02 | U11 | Rename U11 to "Person & Party". It owns `Party`, `PartyRole`, `PartyRelationship` and `PartyRoleType`. Master §7.2: CID = PartyRole. |
| A-03 | U13 | Add `LocalDate`, `LocalTime`, `LocalTimeWindow` and `BusinessDuration` value types to master §9.1. Add `SLADefinition` and `Schedule` to U13 "owns". |
| A-04 | U12 | Add `AddressFormat` and `GeocodeResult` to U12 "owns". |
| A-05 | U14 | Add `RoundingRule`, `RatePolicy`, `RateSource`, `Dimension` and `PackagingUnit` to U14 "owns". |
| A-06 | U09 | Add `RoleGrant`, `Delegation`, `FederatedProvider` and `VerificationRecord` to U09 "owns". |
| A-07 | U10 | Add `TenantLink` to U10 "owns". |
| A-08 | U16 | Master §7.6: `ContextEnvelope.jurisdiction` becomes a role-keyed map (actor, buyer-delivery, seller, data-storage, store). |
| A-09 | U01 | Authority object gains `quorum`. `Ratification` and `Annulment` become DecisionRecord types. |
| A-10 | U02 | Add `ChangeTemplate` and `ChangeWindow` to U02 "owns". |
| A-11 | U03 | Master §18.5 gains layered policy precedence (platform → emergency → universe-default/tenant/org) and `PartialEvaluate` for list queries. |
| A-12 | U61 | Master §15.5 gains event categories (domain, integration, system, signal, audit) and the claim-check rule for large payloads. |
| A-13 | U57 | Master §8.3 gains capability kinds `data-pack` and `ui-pack`, and the formal `PackRuntime` gRPC contract. |
| A-14 | U58 | Master §11.4 Blueprint gains `config`, `decisions`, `placement` and `adapters`. PlatformDefinition gains `overrides`. |
| A-15 | U65 | Master §19.7 gains ordered security profiles (standard < high < regulated < sovereign) and the data handling matrix. |
| A-16 | U73 | Master §27 gains `Placement` (sharding by jurisdiction) and `Activation` as first-class objects. |
| A-17 | U74 | Master §28.3 Certification gains `profile`, `subjectDigest` and a DSSE attestation. Invalidation of an active blueprint opens a grace period and never shuts it down automatically. |
| A-18 | U75 | Master §11.6 gains discovery gap kinds and `INSIGHT` severity. The fix catalog becomes a first-class object. |
| A-19 | U26 | Master §32 P1: the Ledger (U30) is absent in P1. Order and payment events are kept and replayed into it when U30 activates in P2. |
| A-20 | U72 | U72 explicitly owns `MetricDefinition`, `AlertRule`, `Experiment` and `FeatureFlag`. |
| A-21 | U66 | Every universe holding personal data implements the `privacy.dsr-handler` extension point (export, rectify, erase). Checked by gate `CMP-PRV-01`. |
| A-22 | U53/U04 | CEL is the single expression language for decisions, constraints and guards (FEEL is not used). |
| A-23 | U77→U12 | Geography becomes frame-aware: places belong to Bodies; jurisdictions can be governed by treaty, station, virtual-world or DAO authorities; address formats are keyed by (body, authority). |
| A-24 | U77→U13 | Temporal becomes frame-aware: time scales (TAI/MTC/LTC/world clocks), calendar systems, light-time facts, plus a synthetic-calendar golden test. |
| A-25 | U77→U14 | Currencies belong to monetary systems (`X-<system>-<code>` for non-ISO currencies); units belong to unit systems; 18-decimal precision for digital assets. |
| A-26 | U77→U15 | Locales belong to language systems; private-use tags for unregistered languages; sign and machine-protocol languages. |
| A-27 | U77→U16 | New Context dimension `frame`. The simulation flag is now derived from the reality kind. |
| A-28 | U77→U03 | Platform policy P-004 generalised to reality isolation with bridging. |
| A-29 | Review | Products and services completed: U78–U84 and U100 added; U18, U19, U21 and U22 extended (relationships, fitment, documents, product natures, listing-type delegation). |
| A-30 | U85 | `SegmentRef` now has an owner (CDP). |
| A-31 | U86 | Marketing campaign orchestration moves from U40 to U86; U40 delivers messages only. |
| A-32 | U87 | SEO and web presence added as a Phase 1 universe (needed by any public storefront). |
| A-33 | U88, U09 | Social & Community universe; social login added to Identity. |
| A-34 | U89 | Contract & Agreement gets a universe number (it was in the master mindmap without one). |
| A-35 | U90 | Global Trade & Customs gets an owner. |
| A-36 | U91 | Auctions, tenders and negotiation (including agent-to-agent) get an owner. |
| A-37 | U96 | Collaboration, projects and the universal comment thread capability. |
| A-38 | U97 | Forms, surveys and feedback. |
| A-39 | U98 | Sustainability and ESG, with anti-greenwashing rules. |
| A-40 | U95 | Git, CI/CD and definitions-as-code as a Phase 0 universe; Studio and Git kept in two-way sync. |
| A-41 | U93 | Data governance becomes a first-class universe (catalogue, contracts, lineage, quality, master data, sharing). |
| A-42 | U94 | Classical ML platform separated from LLMs and agents; one shared model registry with U49. |
| A-43 | U92 | IoT and devices (including robots and edge) get an owner. |
| A-44 | U99 | Digital assets and distributed ledgers (optional, jurisdiction-gated). |
| A-45 | U13 | Calendar and scheduling completeness: ICS calendar feeds, Google/Microsoft/CalDAV sync, invitations, multi-party availability search, waitlists, walk-in queue tokens, reminders, time off; canonical names for time fields; value-type vs service dependency kinds; gate `ARCH-TMP-05`. |
| A-46 | All | `TEMPORAL-BINDING-MATRIX.md` binds every universe's time needs to Temporal mechanisms. 27 specs gained the `U13 Temporal` dependency; planned universes must follow their matrix rows. |
| A-47 | All | Time-field cleanup: 108 informal time fields across 50 specs and the master document now have explicit Temporal types. Non-time fields that collided with the reserved names were renamed (`compareAt` → `compareAtPrice`, `offset` → `additiveOffset`, SLA `at` → `atElapsedPercent`, SLO `window` → `rollingWindow`/`lookback`, master `freshness` → `freshnessObjective`, `deadline` → `deadlineOffset`, model `retention` → `providerRetention`). The naming rule in U13 Appendix E.3 was corrected so `validUntil` and `effectiveFrom` are TimePoints, and it now lists reserved names. A re-scan finds 0 untyped time fields. |
| A-48 | U101 | Quality, Health, Safety & Environment universe (quality management, CAPA, audits, incidents, permits to work, environmental permits). |
| A-49 | U102 | Strategy & Performance (OKRs, scorecards, planning cycles). |
| A-50 | U103 | Corporate Governance & Equity (board, resolutions, cap table, ESOP, statutory filings). Board resolutions are evidence for U01 authorities. |
| A-51 | U104 | Legal Matters, Ethics & IP (matters, legal holds, whistleblowing, IP portfolio, brand protection and takedowns). |
| A-52 | U105 | Workplace & Facilities (spaces, desk and room booking, visitors, occupancy). |
| A-53 | U106 | Travel & Expense. |
| A-54 | U107 | Partner, Channel & Franchise (one owner for partner programs, deal registration, MDF, rebates, affiliates, franchise royalties). |
| A-55 | U08 | Reference vocabularies added for measuring completeness: ISIC Rev.4, NAICS, NACE, NIC, UN CPC 2.1, SAC, APQC PCF, BIAN, eTOM, ISCO-08, ISCED, WIPO classes, clinical code systems (licensed), plus crosswalks. |
| A-56 | U18 | Complete product-nature registry (21 natures, incl. living, perishable/cold chain, energy, real property, data, IP licences, environmental credits, permits/spectrum, labour time) and the `RegulatedGoodsProfile` model with enforcement points. |
| A-57 | U108 | Product Development, R&D & Innovation (stage-gate, design items and revisions, engineering BOM, engineering change, lab notebook / LIMS-lite, launch). |
| A-58 | U86 | Public relations added to Marketing Automation scope (`pr` campaigns, media monitoring via U88). |
| A-59 | All | `INDUSTRY-PRODUCT-DOMAIN-CATALOGUE.md` maps every ISIC division, CPC division and APQC category to owners, with an explicit out-of-scope register, completeness gap rules and the `ucos coverage` report. Temporal Binding Matrix extended to U101–U108. |
| A-60 | U40 / defaults | `communication.core` joins the base capability set, because transactional messages (OTP, order confirmations) are mandatory for every platform. Found by the checker: the D2C blueprint had no messaging capability. |
| A-61 | U28 | Entitlement platform plans and limits move to Phase 0, because tenant provisioning (U10, Phase 0) needs them. Found by the checker's phase-ordering rule. |
| A-62 | U01, U03, U07, U61, U29 | Pack manifests now require `temporal.core` wherever Temporal services are used (ARCH-TMP-05). Simulators were added for the FX and e-invoice ports (INT-L5). New abstract port `identity.federation-provider`. |
| A-63 | All Phase 1 specs | Phase 1 fallback appendices for dependencies on later-phase universes (U17, U30, U36, U41, U49, U54, U69). |
| A-64 | U40 | Communication completeness: channel registry (email, SMS, WhatsApp, web and mobile push, in-app, RCS, Telegram, LINE, WeChat, Viber, Messenger, Instagram, voice, video, live chat, postal, broadcast, agent-protocol); in-app notification centre; inbound routing with opt-out first; real-time conversations; broadcast and emergency alerts with dual approval; agent-to-agent protocol. `communication.inapp` and `communication.inbound` join the base capability set. |
| A-65 | U109 | Real-time Communications & Contact Centre universe: voice, IVR, masked calling, video sessions, live chat, bot hand-off, routing, call-backs, recordings with consent, supervision. |
| A-66 | spec/ | 23 new manifests (5 capabilities, 12 messaging adapters, the `rtc.provider` port, voice and video adapters, a simulator, contact centre, video sessions). New controls for recording consent and bot disclosure. `targetPhase` added to platform definitions. New reference platform `omnichannel-in` (Phase 4). A negative test confirms the checker blocks mobile, voice and video at Phase 1. |
| A-67 | U49–U51, U17, U25, U27, U30, U36, U59, U69, U70 | AI & Agents specs (gateway, prompts as code, agent run loop with autonomy levels and kill switch) and the Phase 2 core. Ledger posting rules are idempotent by `(sourceEventId, ruleId)`, which makes the P1 replay (A-19) deterministic. Marketplace payouts respect Temporal return-window holds. Subscription mandates follow RBI e-mandate and SCA MIT rules. Risk falls back to `unknown` and never to `low`. U59 registers `gen.schema.object-types` for `spec/object-types/`. |
| A-68 | U32, U33, U37–U39, U41, U45–U48, U52, U54–U56, U71, U76 | The remaining 16 universes are specified, so all 109 now have constitutions. Points are U84 stored value with U30 liability postings. Support owns cases while U109 owns routing. Every appeal goes to an independent human reviewer. Sponsored items are always labelled. Simulations run only in the `simulation` reality frame. Industry packs add composition but never fork a universe. |
| A-69 | spec/, tools/ | Machine-readable registries. `spec/certification/gates.yaml` holds 55 gates in 11 families with U74 profiles; every gate referenced anywhere is defined. `spec/registries/errors.yaml` holds 219 codes. `spec/object-types/` holds 613 schemas. The manifest generator moved into the repo as `tools/gen_manifests.py` and now derives `<slug>.core` manifests for the 56 universes without hand-authored ones. The checker enforces gates and registry sync. Naming-rule fixes in the new specs: `window` renamed to `rollingWindow`, `lookback`, `licenceRange`, `arrivalRange`, `biddingRange` and `responseDuration`. |
| A-70 | docs/ | `docs/adr/` holds ADR-001…020: the master's 001–012 plus CEL, U77 frames, communication base set, durable workflows, Go kernel, reference checker, derived manifests and RLS tenancy. Six open decisions are listed as Proposed. `docs/threat-models/` holds ten STRIDE models covering Phases 0–1 plus a P3 communication addendum. Manifests point at their model, and the checker enforces that the file exists (`SEC-TM-001`). |
| A-71 | Master §25 | Wireframes W17–W40 cover the agent desktop, supervisor wallboard, notification centre, period close, payout run, subscription self-service, NDR queue, risk review, reviews, AI use-case gate, CRM pipeline, loyalty wallet, frame registry, coverage dashboard, dispute workbench, configurator, warranty claim, seat map, OKR tree, board portal, shop-floor terminal, course player, dispatcher map and rollout cockpit. Master bumped to v1.2.0. |
| A-72 | business/ | Business pack. `COST-MODEL.md` covers assumptions A1–A8, fixed platform costs, per-tenant unit economics, AI cost formula and FinOps. `COMMERCIAL-MODEL.md` covers segments, plans (platform fee plus GMV take rate), pass-through, the pack revenue share, terms, and billing on UCOS itself. `TEAM-AND-ROADMAP-PLAN.md` covers dated phases, headcount by team, the 3-year budget, break-even and funding need. It also flags the master §32.1 vs constitution phase mismatches (U17, U37) for alignment. |
| A-73 | CI, contracts, decisions | Changes in this round:<br>• CI: deterministic `tools/ci.sh` with a hash-locked toolchain, contract and scenario validators, and an 11-case self-test. GitHub workflows run CI, bot regeneration, nightly checks and releases, with actions pinned by SHA (ADR-036).<br>• Contracts: hand-written kernel gRPC and REST contracts; 118 generated capability APIs; 529 event payload schemas and an AsyncAPI catalogue.<br>• Tests: 11 Gherkin features over a 60-step vocabulary.<br>• Operations: SLOs and runbooks for 17 services.<br>• Phase 2: hand-written manifests for the 8 Phase 2 universes, with 9 regulations and 10 controls, and the golden `marketplace-in-ae` platform.<br>• Decisions: ADR-021…035 close every open decision; master §32.1 phase rows aligned.<br>• Governance and business: governance files, legal templates, the business validation plan, and a regenerated PDF. |
| A-74 | Phase 0 and 1 readiness | Closes the Phase 0–1 gaps:<br>• Phase 0 exit test: `sample.notes` pack, golden `sample-p0` in a simulated reality, exit scenarios.<br>• Composition: phase-aware base set; PD `reality` (regulations apply in the physical reality only; simulators serve simulated realities); `closure.dl` gained the phase-gap and adapter-port rules, and an oracle proves the rules match the checker.<br>• Cedar: syntax fixed (action groups, annotations); 13 policy tests.<br>• Decisions: 16 tables with 44 executable tests.<br>• Workflows: definitions validated; YAML `on` trap fixed.<br>• Object types: attributes for every Phase 0–1 type.<br>• Genesis: record schema and ceremony runbook.<br>• Spikes: S-01…S-05 kits.<br>• Seeds: S1–S15.<br>• Database: kernel schema with RLS, audit chain and tests.<br>• Go: kernel skeleton with property tests and govulncheck.<br>• Deploy: dev stack, Kubernetes baseline, signed container releases.<br>• ADR-037 (cloud provider) proposed. |
| A-75 | Kernel data path | First running kernel code: the command bus (idempotency with byte-identical replays, a savepoint around the handler, audit, outbox), the versioned object store, the audit appender with chain verification, the outbox relay, the trigger engine (daily wall-clock recurrence) and the `sample.notes` pack. A Go end-to-end test runs the Phase 0 exit flow on PostgreSQL in CI. Writing it surfaced three schema defects, fixed by migrations 0011–0013: the appender could not read its chains, jsonb changed replay bytes, and row locking needed a column grant. Error codes used in Go must exist in the registry (CI check). |
| A-76 | Composition engine | `closure.dl` now fully defines composition: adapter `choice()`, plus event-producer and control gaps. Blueprint ids exclude explanation text; provenance moves to a separate `.trace.json`. The checker fails if a golden result changes without a deliberate `--write`. The Go composer (`kernel/internal/composer`, ADR-022) reproduces every golden blueprint byte for byte and evaluates about 1M facts in about 0.6 s, so spike S-01 passed and ADR-022 is accepted. New command: `ucos compose`. |
| A-77 | Kernel runtime | `ucos-kernel` is the first runnable kernel:<br>• The gateway routes only from the generated OpenAPI (API-L1).<br>• OIDC tokens are verified with RS256 against the issuer's JWKS; each issuer maps to exactly one tenant; `alg=none`, tampered and expired tokens are refused.<br>• Claims become a context envelope; commands require an `Idempotency-Key`; errors use RFC 9457 problem responses; queries run read-only.<br>• A Kafka publisher feeds the relay.<br>• Colons in UGIDs and in the `:verb` suffix are resolved by lazy id matching.<br>• The sample pack refuses reminders from non-service actors.<br>• The dev-stack CI job runs the Phase 0 flow through the running kernel: a real Keycloak token, HTTP create and publish, events in Redpanda, and a verified audit chain. |
| A-78 | Control plane | Compose → certify → activate runs in code (`kernel/internal/controlplane`):<br>• Registry snapshots are digest manifests of `spec/` signed with Ed25519 (DSSE).<br>• Certification evaluates the profile's gates: GAP-000, TEST-COMP-01, ARCH-CAP-02 and CMP-MAP-01 are computed; every other gate needs evidence from the last 30 days or an approved waiver. The result is a signed in-toto attestation.<br>• Activation requires a passing, valid, trusted attestation for exactly this blueprint and an approving decision record whose approvers exclude the requester.<br>• The command bus refuses any capability that is not in the tenant's active blueprint (`ACTIVATION_DENIED`); rollback takes it away again.<br>• The control plane listens on a separate operator-only port with a bearer token. |
| A-79 | Provider-agnostic, local-first cell | ADR-037 is accepted as provider-agnostic: a cell is defined by contracts (Kubernetes, PostgreSQL 16+, the Kafka API, OIDC, the S3 API, OpenTelemetry), not by a cloud provider.<br>• The `ucos-kernel` image carries the spec and the migrations, applies the schema itself (`migrate`, append-only, with digests) and reports ready only on a current schema.<br>• `deploy/k8s/apps/kernel` runs on any Kubernetes; `overlays/local` is a complete cell; `tools/cell_smoke.sh` and the CI `cell` job run the Phase 0 exit flow on kind.<br>• An embedded Cedar PEP authorizes every operation (fail closed, obligations enforced or refused); parity with the reference engine is tested.<br>• Prometheus-format metrics. |

## Decisions raised by the specs (all recorded as ADRs)

| From | Decision needed | Recommendation |
|---|---|---|
| U04 | Expression language for constraints and rules | **Decided:** CEL (A-22, ADR-013) |
| U08 | Licensing for GS1 GPC and UNSPSC redistribution | **Decided:** Bundle only licences that allow multi-tenant redistribution; otherwise bring-your-own-licence data packs ([ADR-027](../docs/adr/)) |
| U09 | Reference IdP: Keycloak or Ory | **Decided:** Keycloak, provisional until spike S-02 ([ADR-021](../docs/adr/)) |
| U10 | One tenant spanning several residency regions | **Decided:** Yes: one tenant, data shards in several cells ([ADR-028](../docs/adr/)) |
| U12 | Boundary data source: OSM (ODbL) or commercial | **Decided:** OSM (ODbL) with attribution, derived data kept separate ([ADR-027](../docs/adr/)) |
| U13 | Reservation counters at extreme peak: Postgres sharded sub-slots or Redis | **Decided:** Postgres sharded sub-slots; Redis only if the load test fails ([ADR-023](../docs/adr/)) |
| U01 | Membership of the root authority (Architecture Board, at least 3 members with hardware keys) | **Decided:** Board of at least 3 (CTO chair, chief architect, CISO). Chair: Bipin Kumar; two seats open ([ADR-034](../docs/adr/)) |
| U03 | OpenFGA for relationship-heavy (social graph) cases | **Decided:** Cedar only; revisit at P6 against stated triggers ([ADR-026](../docs/adr/)) |
| U57 | gVisor sandbox for all third-party packs | **Decided:** gVisor for all third-party out-of-process packs ([ADR-025](../docs/adr/)) |
| U58 | Datalog engine: Soufflé or an embeddable Rust engine | **Decided:** Embedded Go Datalog evaluator with the Python checker as oracle; spike S-01 passed (A-76) ([ADR-022](../docs/adr/)) |
| U65 | Scope of format-preserving tokenisation (non-PSP flows) | **Decided:** Tokenise national IDs and bank account numbers; encrypt other restricted fields ([ADR-029](../docs/adr/)) |
| U73 | Crossplane or plain OpenTofu for cell provisioning | **Decided:** OpenTofu modules wrapped by Crossplane ([ADR-024](../docs/adr/)) |
| U18 | Global product data sourcing and licences (GS1 data pools, manufacturer syndication, licensed providers) | **Decided:** Syndication and licensed feeds first, then tenant contributions with provenance ([ADR-030](../docs/adr/)) |
| U31 | Build or buy tax engines per regime | **Decided:** In-house packs for India and UAE; engine adapters for US and EU ([ADR-031](../docs/adr/)) |
| U60 | Workflow engine: Temporal.io or Camunda 8 | **Decided:** Temporal.io with a BPMN import converter ([ADR-032](../docs/adr/)) |
| U64 | Mobile renderer: React Native or Flutter | **Decided:** React Native (Expo) ([ADR-033](../docs/adr/)) |
| U67 | Who owns legal interpretations in each jurisdiction | **Decided:** In-house counsel owns each interpretation, with external firms per jurisdiction ([ADR-035](../docs/adr/)) |
