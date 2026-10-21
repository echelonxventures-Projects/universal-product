# Business domains

Every artifact the platform is built from — a code file, a table, an API route, a state machine, a capability, a registry list, a console screen, a page — belongs to exactly one business domain below. A business domain is a sub-entity of the foundation domain named as its `foundation`. Nothing is owned twice and nothing is unowned (test/domain-map.js); each domain's documentation — overview, API, architecture, data model, data flow, process flows, user interface and a manual for each of its users — is generated from this file and the code (scripts/domain-docs.js), so it cannot drift.

| Domain | Foundation | Users | Documentation |
|---|---|---|---|
| [Identity](identity.md) | Identity | Guest, Shopper, Seller, Store staff, Store administrator, Platform administrator, Developer | 8 sections to write |
| [Access and roles](access.md) | Authority | Store staff, Store administrator, Platform administrator | 4 sections to write |
| [Customers](customers.md) | Party | Shopper, Store staff, Store administrator, Platform administrator | 5 sections to write |
| [Stores and organisation](stores.md) | Party | Store administrator, Platform administrator | 3 sections to write |
| [Modules and capabilities](modules.md) | Offering | Store administrator, Platform administrator | 3 sections to write |
| [Platform billing](platform_billing.md) | Value | Store administrator, Platform administrator | 3 sections to write |
| [Catalogue](catalog.md) | Offering | Shopper, Seller, Store staff, Store administrator, Platform administrator | 6 sections to write |
| [Product content](product_content.md) | Content | Seller, Store administrator | 3 sections to write |
| [Product options](product_options.md) | Offering | Shopper, Store administrator | 3 sections to write |
| [Inventory](inventory.md) | Offering | Store staff, Store administrator | 3 sections to write |
| [Pricing](pricing.md) | Value | Store administrator, Seller | 3 sections to write |
| [Currencies and exchange](currency.md) | Value | Store administrator, Platform administrator | 3 sections to write |
| [Offers](offer.md) | Commerce | Shopper, Seller, Store administrator, Platform administrator, Partner or affiliate | 6 sections to write |
| [Affiliates and creators](affiliate.md) | Commerce | Partner or affiliate, Store administrator | 3 sections to write |
| [Advertising](advertising.md) | Commerce | Seller, Store administrator | 3 sections to write |
| [Cart and checkout](cart.md) | Commerce | Guest, Shopper | 3 sections to write |
| [Orders](order.md) | Commerce | Shopper, Store staff, Store administrator | 4 sections to write |
| [Returns and refunds](returns.md) | Commerce | Shopper, Store staff, Store administrator | 4 sections to write |
| [Payment gateways](payments.md) | Integration | Shopper, Store administrator, Platform administrator, Developer | 5 sections to write |
| [Wallets](wallet.md) | Value | Shopper, Seller, Store administrator, Platform administrator | complete |
| [Settlements and payouts](settlement.md) | Value | Seller, Store administrator, Platform administrator | 4 sections to write |
| [Financial services](financial_services.md) | Value | Shopper, Store administrator | 3 sections to write |
| [Tax](tax.md) | Rule | Store administrator, Platform administrator | 3 sections to write |
| [Subscriptions and memberships](subscriptions.md) | Commerce | Shopper, Store administrator | 3 sections to write |
| [Shipping and delivery](shipping.md) | Commerce | Shopper, Store staff, Store administrator, Driver or rider, Platform administrator | 6 sections to write |
| [Supply and planning](supply.md) | Operations | Store staff, Store administrator | 3 sections to write |
| [Services and appointments](services.md) | Offering | Shopper, Practitioner, Store staff, Store administrator | 5 sections to write |
| [Digital goods](digital_goods.md) | Offering | Shopper, Store administrator | 3 sections to write |
| [Health and pharmacy](health.md) | Offering | Shopper, Practitioner, Store staff, Store administrator | 5 sections to write |
| [Made to order](made_to_order.md) | Offering | Shopper, Store administrator | 3 sections to write |
| [Mobility](mobility.md) | Operations | Shopper, Driver or rider, Store administrator | 4 sections to write |
| [Business operations](business_operations.md) | Operations | Store staff, Store administrator | 3 sections to write |
| [Marketplace](marketplace.md) | Commerce | Seller, Shopper, Store staff, Store administrator, Platform administrator | 6 sections to write |
| [Negotiation and auctions](price_discovery.md) | Commerce | Shopper, Seller, Store administrator | 4 sections to write |
| [Business-to-business trade](trade.md) | Commerce | Seller, Store administrator, Store staff | 4 sections to write |
| [Lists, alerts and history](engagement.md) | Experience | Shopper, Guest | 3 sections to write |
| [Reviews and questions](reviews.md) | Experience | Shopper, Seller, Store staff, Store administrator | 5 sections to write |
| [Messages and notifications](communication.md) | Communication | Shopper, Seller, Store staff, Store administrator | 5 sections to write |
| [Customer support](support.md) | Communication | Shopper, Store staff, Store administrator | 4 sections to write |
| [Storefront and content](storefront.md) | Experience | Guest, Shopper, Store administrator | 4 sections to write |
| [Search and discovery](search.md) | Search | Guest, Shopper, Store administrator | 4 sections to write |
| [Search engine optimisation](seo.md) | Experience | Store administrator | 2 sections to write |
| [Languages and localisation](localisation.md) | Expression | Store administrator, Platform administrator | 3 sections to write |
| [Consoles](consoles.md) | Experience | Store staff, Store administrator, Platform administrator | 4 sections to write |
| [Analytics and reports](analytics.md) | Insight | Store administrator, Platform administrator | 3 sections to write |
| [Experiments](experiments.md) | Insight | Store administrator | 2 sections to write |
| [Risk and fraud](risk.md) | Security | Store staff, Store administrator, Platform administrator | 4 sections to write |
| [Compliance and privacy](compliance.md) | Compliance | Shopper, Store administrator, Platform administrator | 4 sections to write |
| [Audit](audit.md) | Audit | Store administrator, Platform administrator | 3 sections to write |
| [Security](security.md) | Security | Platform administrator, Developer | 3 sections to write |
| [AI](ai.md) | Agent | Store administrator, Platform administrator | 3 sections to write |
| [Integrations and webhooks](integration.md) | Integration | Store administrator, Platform administrator, Developer | 4 sections to write |
| [Kernel and registries](kernel.md) | Registry | Platform administrator, Developer | 3 sections to write |
| [Rules, states and settings](rules.md) | Rule | Store administrator, Platform administrator | 3 sections to write |
| [Places and time](geography.md) | Geo | Platform administrator | 2 sections to write |
| [Platform knowledge](knowledge.md) | Guidance | Platform administrator, Developer | 3 sections to write |
| [Runtime and operations](runtime.md) | Operations | Platform administrator, Developer | 3 sections to write |
