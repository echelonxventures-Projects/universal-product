## {{§§planeB}} Plane B — Economic & Business

The 26 business universes fall into five groups: Commerce, Money, Supply, People & Work, and Customer. Industry names (Healthcare, Banking, Retail, Government, …) and suite names (ERP, CRM, HRMS, SCM, OMS, WMS, PIM, LMS, ITSM) are **not** universes here. They are Blueprints ({{Blueprint}}) or composition labels; Appendix A maps each one.

> **Group — Commerce**

### {{#Value & Economics}}

**Mandate:** Units of value, and the economic and commerce models that compositions choose from.

- **Owns:** value · currency (fiat, digital, crypto) · token (value tokens, tokenized-asset definitions) · the money type (amount + currency) · exchange-rate reference data · economic asset and title of ownership · economic models (value systems, incentive systems, reputation, loyalty and attention economies, synthetic economies) · **commerce and monetization model catalog**:
  - *participant topologies:* B2B · B2C · D2C · C2C · P2P · B2G · G2C · B2B2C
  - *monetization models:* sale · marketplace · subscription · rental · auction · booking · licensing · brokerage · advertising · donation · freemium · pay-as-you-go · usage-based · outcome-based · future models
- **Boundary:** accounting and FX operations → {{Finance & Accounting}} · prices → {{Pricing}}.

### {{#Offering}}

**Mandate:** The universal commerce object. Anything that can be offered derives from one constitutional model.

- **Owns:** Offering, with types: physical product · digital product · hybrid · service · experience · subscription plan · membership · rental · asset offering · course · license · bundle/package · reservation/booking offering · contract offering · insurance product · financial product · investment product · digital asset · token · future commerce object. Also SKU · variant · attribute values · specification instances · delivery model · offering lifecycle · offering compliance and certification references.
- **Core schema:** `Offering { ugid, gpid|gsid (GOKN ref), offering_type, family, taxonomy_ref, attributes[], variants[], delivery_model, sla_ref (Legal), capacity_ref (Resource), compliance_refs, policies, lifecycle }`
- **Boundary:** global facts → {{GOKN}} · price → {{Pricing}} · stock → {{Inventory}} · incentives → {{Offer & Incentive}}.

### {{#Catalog & Merchandising}}

**Mandate:** How a tenant curates and presents its offerings.

- **Owns:** commercial catalogs (per tenant, channel and market) · assortments · navigation categories · collections · merchandising rules · listing presentation · per-channel catalog publishing · comparison sets.
- **Boundary:** registries and catalogs of APIs, capabilities and data → {{Registry}} · global taxonomy → {{GOKN}}.

### {{#Pricing}}

**Mandate:** What an offering costs, in any model, currency and context.

- **Owns:** price · price lists and price books · price models (fixed, tiered, volume, usage, dynamic, negotiated, auction-derived, subscription, outcome-based) · the price calculation pipeline · dynamic pricing (demand/supply, competitor, surge) · pricing policies (guardrails, as typed {{Policy}}) · tenant price history · multi-currency pricing.
- **Boundary:** incentives → {{Offer & Incentive}} · tax → {{Tax}} · demand forecasts → {{Intelligence}} · market price intelligence → {{GOKN}}.

### {{#Offer & Incentive}}

**Mandate:** Commercial propositions and every incentive that modifies them. All time behaviour is delegated to {{Temporal}}.

- **Owns:** Offer (offering + price + terms + eligibility + temporal policy, including seller-specific offers) · promotion · discount · coupon · voucher · cashback · loyalty programs and points · reward · referral benefit · gamification · flash sale · bundle offer · subscription benefit · marketplace and seller incentive · eligibility policies (segment, geography, channel, condition) · stacking and exclusivity rules · incentive budgets (posted to {{Finance & Accounting}}).
- **Core schema:** `Offer { ugid, offer_type, offering_refs, pricing_policy_ref, eligibility_policy_ref, temporal_policy_ref, geography_ref, channel_refs, usage_rules, governance_policy_ref, lifecycle }`
- **Trigger classes** (composed from {{Temporal}}, {{Event}} and {{Decision}}):
  - *validity:* valid-from / valid-to windows
  - *recurring:* e.g. every weekend, every month end, every festival
  - *event-based:* first purchase, registration, cart abandonment, shipment
  - *conditional:* inventory or demand thresholds, competitor price change, entering a segment
  - *geo-temporal:* country, region, city, store, time zone, holiday calendar
  - *fiscal:* quarter end, year end, tax season, settlement cycle
  - *marketplace-scoped:* seller, brand, category, channel
  - *AI-driven:* prediction, behaviour, demand forecast
  - *simulation-tested:* "what if a 20% discount?", "what if cashback rises?"
- **Boundary:** campaigns → {{Marketing & Engagement}} · auctions, bids and negotiation → {{Marketplace & Distribution}}.

### {{#Transaction}}

**Mandate:** The commercial exchange, from quote to completion and after-sales.

- **Owns:** Quote · **Cart** (add, remove, update, merge, save, anonymous, multi-device, multi-currency, shared, tax preview via {{Tax}}, promotion preview via {{Offer & Incentive}}, stock reservation via {{Inventory}}) · Checkout · Order (lines, splits, order orchestration state) · the **Commerce Object** `{ buyer, seller, offerings, offer, price, payment_ref, settlement_ref, tax_ref, fulfillment_ref, compliance, audit }` · cancellation · return · exchange · warranty and guarantee · commercial context.
- **Boundary:** money → {{Payment}} · delivery → {{Logistics & Fulfillment}} · recurring agreements → {{Subscription}}.

### {{#Marketplace & Distribution}}

**Mandate:** Multi-sided markets and routes to market.

- **Owns:** Marketplace instances (sides, rules) · participant onboarding (seller, merchant, provider, creator, partner, affiliate, reseller, distributor) · seller listings · marketplace policies · **Channel** as a route to market (online, offline, store, marketplace, social commerce, affiliate, partner, reseller, distributor, API, agent) · partner and affiliate networks · **market mechanisms**: auction · bid · negotiation (human and autonomous agent) · market clearing · marketplace types (goods, services, assets, knowledge, data, labour/gig).
- **Boundary:** commission and fee computation → {{Billing & Revenue}} · reputation → {{Trust & Reputation}} · matching algorithms → {{Search & Recommendation}} · sourcing events → {{Sourcing & Procurement}} · capability and agent stores → {{Capability}}.

### {{#Subscription}}

**Mandate:** Recurring commercial agreements and their lifecycle.

- **Owns:** subscription agreement (plan reference, term, renewal, trial, pause, resume, upgrade, downgrade, proration, cancellation, churn reasons) · commercial membership lifecycle.
- **Boundary:** charging → {{Billing & Revenue}} · rights granted → {{Entitlement}} · renewal clocks → {{Temporal}}.

### {{#Entitlement}}

**Mandate:** What a party has the right to use or access.

- **Owns:** entitlements (features, plans, packages, licenses, seats, quotas, usage limits, content rights, service access) · grants and revocations · the entitlement-check API · tenant plan entitlements for UCOS itself.
- **Boundary:** authorization decisions → {{Security}} (entitlement is an input to them) · experiment toggles → {{Experimentation}}.

> **Group — Money**

### {{#Payment}}

**Mandate:** Moving money, independent of any gateway (L5).

- **Owns:** payment intent · abstract payment instruments (card, bank transfer, UPI, wallet, BNPL, direct debit, crypto, future) · authorization · capture · void · refund · **chargeback flow** · escrow · wallets and stored value (including store credit) · payouts and disbursement · split payments · clearing · settlement · payment routing and orchestration across providers · provider reconciliation · the PSP SPI (provider adapters live in {{Integration}}).
- **Boundary:** ledger postings → {{Finance & Accounting}} · dispute semantics → {{Legal & Agreement}} · fraud → {{Risk}} · tokenization → {{Security}} · BNPL credit → {{Financial Services}}.

### {{#Billing & Revenue}}

**Mandate:** Turning usage and agreements into invoices and recognized revenue.

- **Owns:** metering · rating · charging · billing accounts and cycles · invoices and credit notes · usage-based billing · dunning and collections · revenue recognition · **revenue share, commission and fee schedules** · royalties · marketplace fees · statements · executing monetization (advertising billing, licensing fees).
- **Boundary:** invoice tax → {{Tax}} · posting → {{Finance & Accounting}} · collecting money → {{Payment}}.

### {{#Finance & Accounting}}

**Mandate:** The books of record and corporate finance.

- **Owns:** double-entry ledger · chart of accounts · ledger accounts · journals and entries (debit, credit, adjustment) · sub-ledgers (AR, AP) · general reconciliation · financial close · treasury and cash management · FX operations · budgeting · cost accounting · profitability · financial planning and forecasting · funding · financial statements and reporting · financial controls · financial intelligence.
- **Boundary:** revenue rules → {{Billing & Revenue}} · tax → {{Tax}} · regulated financial products → {{Financial Services}}.

### {{#Tax}}

**Mandate:** Every tax, in every jurisdiction, as configuration.

- **Owns:** tax types (sales tax, VAT, GST, withholding, duties, digital-services tax) · tax rules and rates · binding of tax jurisdictions to regions (via {{Compliance}} and {{Spatial}}) · tax classification codes for offerings · tax calculation · exemptions and exemption certificates · tax registration · returns and filing · e-invoicing obligations · tax evidence · tax-law packs.
- **Boundary:** customs process → {{Logistics & Fulfillment}} · tax periods → {{Temporal}}.

### {{#Financial Services}}

**Mandate:** Regulated financial products and their operations.

- **Owns** these families:
  - *Banking:* deposit accounts, card issuing, transfer products
  - *Lending & credit:* origination, underwriting, credit-scoring configuration, servicing, loan collections, BNPL credit
  - *Insurance:* products, underwriting, policy administration, premiums, insurance claims
  - *Investment & wealth:* portfolios, advisory hooks
  - *Securities & trading:* instruments, brokerage, order books and trade execution, market data
  - *Digital-asset custody*
- **Boundary:** money movement → {{Payment}} · ledger → {{Finance & Accounting}} · KYC → {{Trust & Reputation}} · the generic risk framework → {{Risk}} · sellable product definitions → {{Offering}}.

> **Group — Supply**

### {{#Inventory}}

**Mandate:** What stock exists, where it is, and what is available to promise.

- **Owns:** stock items · the quantity ledger · inventory locations (nodes reference {{Logistics & Fulfillment}} and {{Spatial}}) · lots and serials · available-to-promise / capable-to-promise · stock reservations and allocations · safety stock · replenishment rules · the inventory network · valuation inputs for {{Finance & Accounting}}.

### {{#Logistics & Fulfillment}}

**Mandate:** Moving and storing physical things, in any mode of transport.

- **Owns:** fulfillment orchestration (order → shipment) · warehouse operations (receiving, put-away, picking, packing) · shipment · package · movement · route plans · carrier · fleet and logistics vehicles · nodes and hubs · tracking and tracking events · delivery · pickup · last mile · delivery slots (windows from {{Temporal}}) · reverse logistics · customs and global-trade documentation · logistics-network capacity planning · transport modes (road, rail, air, sea, drone, robot, autonomous, future) · autonomous logistics.
- **Boundary:** geometric routing → {{Spatial}} · dispatch and assignment → {{Resource & Capacity}} · device telemetry → {{Cyber-Physical}} · stock → {{Inventory}}.

### {{#Resource & Capacity}}

**Mandate:** Any finite resource: its capacity, availability, allocation, assignment and booking.

- **Owns:** resources (people as capacity, rooms, seats, equipment, vehicles as capacity, slots, natural resources) · capacity · resource availability · allocation · **assignment and dispatch** · holds and reservations of capacity · the **booking engine** · appointments · waitlists · overbooking policies · business capacity planning.
- **Composition formula:** `Reservation = Resource (what) × Temporal Window (when) × Offer terms (on what terms)`
- **Boundary:** matching algorithms → {{Search & Recommendation}} · optimization → {{Intelligence}} · employment → {{Workforce}} · platform capacity → {{Operations}}.

### {{#Sourcing & Procurement}}

**Mandate:** Buying what an organization needs.

- **Owns:** requisitions · sourcing events (RFI, RFQ, RFP, tender) · supplier onboarding and qualification · supplier management and performance scorecards · purchase orders · receipt and invoice matching (with {{Finance & Accounting}} AP) · procurement catalogs (punch-out) · procurement-contract references · spend management.

### {{#Production}}

**Mandate:** Making things.

- **Owns:** bill of materials · manufacturing routings · work centers · manufacturing work orders · production planning and scheduling · MES execution records · quality control and inspection · equipment maintenance · plant and line twin feeds (to {{Digital Twin}}).

> **Group — People & Work**

### {{#Workforce}}

**Mandate:** People at work, from hire to retire.

- **Owns:** employment · workers (employee, contractor, gig worker, driver, courier) · positions and job roles · skills and competencies · recruitment and hiring · employee onboarding · time and attendance · shift scheduling · leave · payroll calculation (postings go to {{Finance & Accounting}}, payouts to {{Payment}}) · compensation and benefits · performance · workforce planning.

### {{#Work Management}}

**Mandate:** Organizing the work itself.

- **Owns:** projects · tasks · assignments · milestones · task dependencies · boards · workload · timesheets.

### {{#Education & Learning}}

**Mandate:** Human learning. Machine learning belongs to {{Intelligence}}.

- **Owns:** learners · course structures · curricula · enrollment · lessons · assessments and grading · learning paths · learner credentials (issued through {{Trust & Reputation}}).
- **Boundary:** course content → {{Content & Media}} · course as a sellable offering → {{Offering}}.

> **Group — Customer**

### {{#Relationship}}

**Mandate:** Relationships with any party over time, not only for sales. This universe covers what CRM and CDP systems do.

- **Owns:** relationship · engagement · lead · prospect · opportunity · customer account · contacts · customer journey model · interaction log (linked to {{Communication & Collaboration}} threads) · unified profile / CDP · segments and audiences · behavioural profile · customer success · feedback, NPS and CSAT · customer-lifetime-value inputs · customer twin feeds.
- **Boundary:** parties and roles → {{Party & Organization}} · support cases → {{Support & Service}} · campaigns → {{Marketing & Engagement}}.

### {{#Support & Service}}

**Mandate:** Helping customers and delivering service after the sale.

- **Owns:** support cases and tickets (as case types in {{Workflow}}) · service requests · customer-facing incidents · binding SLA policies (commitments from {{Legal & Agreement}}, clocks from {{Temporal}}) · knowledge-base articles (content stored in {{Content & Media}}) · contact-center operations · field service and service work orders · the service desk.
- **Boundary:** platform incidents → {{Operations}} · transport → {{Communication & Collaboration}}.

### {{#Marketing & Engagement}}

**Mandate:** Reaching and engaging audiences.

- **Owns:** marketing campaigns · journey orchestration · marketing plans · lead generation and lead scoring · referral and affiliate *programs* (their benefits come from {{Offer & Incentive}}; their networks from {{Marketplace & Distribution}}) · engagement programs · social media management.
- **Boundary:** message delivery → {{Communication & Collaboration}} · paid media → {{Advertising}}.

### {{#Advertising}}

**Mandate:** Paid media, on both the buy side and the sell side.

- **Owns:** advertisers and ad accounts · ad inventory and placements · paid ad campaigns · creatives (assets in {{Content & Media}}) · targeting · ad serving · frequency capping · attribution and conversion measurement · ad-billing feed to {{Billing & Revenue}}.
- **Boundary:** auction mechanism → {{Marketplace & Distribution}}.
