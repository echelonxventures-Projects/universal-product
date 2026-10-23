# Manual — Store administrator

Everything a store administrator does on the platform, domain by domain. Generated from each domain's documentation.

## Identity

Who someone is: accounts, sign-in by every method (password, one-time code, magic link, passkey, single sign-on), sessions, provisioning from directories, and platform administrators' own accounts.

_Not yet written._

More: [Identity](../domains/identity.md)

## Access and roles

What someone may do: store roles and staff, platform roles, permission sections and scopes, and the policies that grant or refuse.

_Not yet written._

More: [Access and roles](../domains/access.md)

## Customers

The people and organisations a store sells to: their profiles and addresses, segments they belong to, and leads not yet customers.

_Not yet written._

More: [Customers](../domains/customers.md)

## Stores and organisation

The stores on the platform and how each is organised: creating and configuring a store from its setup answers, its departments and org units, its tenancy tree and its look.

_Not yet written._

More: [Stores and organisation](../domains/stores.md)

## Modules and capabilities

What a store has switched on: the modules the platform sells to stores, the capabilities inside them, their parameters, presets and availability rules.

_Not yet written._

More: [Modules and capabilities](../domains/modules.md)

## Platform billing

What the platform charges its stores: plans, subscriptions to plans, usage metering, invoices and credit notes.

_Not yet written._

More: [Platform billing](../domains/platform_billing.md)

## Catalogue

Everything a store sells, described once: products and their variants and SKUs, brands, the category tree, attributes, the platform master every product is described on, the global catalogue and contributions back to it.

_Not yet written._

More: [Catalogue](../domains/catalog.md)

## Product content

How a product is presented beyond its facts: rich content modules, images and comparison blocks, reviewed before they show.

_Not yet written._

More: [Product content](../domains/product_content.md)

## Product options

Choices on one product instead of a product per combination: option groups (sizes, toppings, engravings) with their values and price changes, attached to any product.

_Not yet written._

More: [Product options](../domains/product_options.md)

## Inventory

How much of what is where: stock per SKU and warehouse, store-level stock, transfers between locations and serial-numbered items.

_Not yet written._

More: [Inventory](../domains/inventory.md)

## Pricing

The price a buyer pays before any offer: price lists per segment with quantity tiers, and demand-based surge pricing.

_Not yet written._

More: [Pricing](../domains/pricing.md)

## Currencies and exchange

Every unit of value and how they convert: currencies, points and credits, and exchange rates.

_Not yet written._

More: [Currencies and exchange](../domains/currency.md)

## Offers

Every reason a buyer pays less or gets more: offers and discounts of every type, coupons, cashback, rewards, gift cards and vouchers, deals and countdowns, group buying, price matching and trade-ins, the funding and settlement of each, and their governance.

_Not yet written._

More: [Offers](../domains/offer.md)

## Affiliates and creators

Who brings buyers and what they earn: affiliate networks and tiers, tracked clicks and conversions, commission rules and affiliate payouts.

_Not yet written._

More: [Affiliates and creators](../domains/affiliate.md)

## Advertising

Paid placement: sellers' sponsored products and creatives competing in an auction for slots, and what each impression and click costs.

_Not yet written._

More: [Advertising](../domains/advertising.md)

## Orders

What was bought and what happens to it: orders and their lines, their life from placement to delivery, and substitutions proposed when an item is out.

_Not yet written._

More: [Orders](../domains/order.md)

## Returns and refunds

Sending something back: return requests, their inspection and refund, and payment disputes.

_Not yet written._

More: [Returns and refunds](../domains/returns.md)

## Payment gateways

Taking money: the gateways a store accepts and their methods, payment attempts and captures, gateway callbacks, payment links, QR and instant-bank collection, mandates, escrow and split payments.

_Not yet written._

More: [Payment gateways](../domains/payments.md)

## Wallets

Value a party holds: wallets of any definition, the ledger every movement is posted to, holds, transfers between wallets and between people.

1. Wallets need the **Customer Wallets** module (⚙️ Modules). Without it, wallet pages and calls
   say so instead of working.
2. Open **💳 Payments & Finance → 👛 Wallets & Ledger**.
3. **Ledger check** at the top must read "every one balances" and "event chain intact". Anything
   else is shown with the journal or event it concerns — report it; do not try to edit data.
4. **Definitions** lists every kind of wallet with the value it holds, what it allows and its policy,
   as resolved for your store. **Configure** sets your store's own value for one setting (for
   example a lower maximum balance for trip wallets); **Make default** chooses where your
   customers' money lands.
5. **An owner's wallets**: enter the owner (for example `t1:u:42`) and **Show**. For each wallet you
   can open its **Statement** (every movement, its holds and every name it has had), move it to
   another state (**Restrict**, **Suspend**, **Reactivate**, **Close** — each asks why; a wallet
   closes only when empty) or **Adjust** it up or down with a reason.
6. To undo a movement, open the statement and **Reverse** that journal, giving the reason. A journal
   is reversed once; a reversal is not reversed — post a new movement instead.

More: [Wallets](../domains/wallet.md)

## Settlements and payouts

Paying those who are owed: seller settlements, payout batches, bank payouts, reconciliation of what the bank says against what the ledger says, and remittances.

_Not yet written._

More: [Settlements and payouts](../domains/settlement.md)

## Financial services

Financial products sold to buyers: bill payments, recharges, insurance, and credit — pay later and loans with their instalments.

_Not yet written._

More: [Financial services](../domains/financial_services.md)

## Tax

What tax applies and how much: tax modes, rules by place and product, and how tax is shown and charged.

_Not yet written._

More: [Tax](../domains/tax.md)

## Subscriptions and memberships

Buying again on a schedule and belonging to a programme: subscribe-and-save schedules and their cycles, and membership tiers with their perks.

_Not yet written._

More: [Subscriptions and memberships](../domains/subscriptions.md)

## Shipping and delivery

Getting goods to the buyer: carriers and rates, shipments and tracking, pickup points and lockers, and fast local delivery from dark stores with slots, riders and dispatch runs.

_Not yet written._

More: [Shipping and delivery](../domains/shipping.md)

## Supply and planning

Keeping shelves full: suppliers, which supplier provides what, purchase requests and their approval, and replenishment plans.

_Not yet written._

More: [Supply and planning](../domains/supply.md)

## Services and appointments

Selling time and work: bookings of resources and slots, live audio and video sessions and charging them by the minute, and services attached to an item — installation, assembly and extended warranties.

_Not yet written._

More: [Services and appointments](../domains/services.md)

## Digital goods

What is delivered without shipping: licence keys from a pool, course access and progress, and the deliverables machinery other domains use.

_Not yet written._

More: [Digital goods](../domains/digital_goods.md)

## Health and pharmacy

What health commerce needs: prescriptions checked before sale, verified practitioners, lab tests and their reports, and the shopper's own health records shared with consent.

_Not yet written._

More: [Health and pharmacy](../domains/health.md)

## Made to order

Items made for one buyer: the buyer's own artwork proofed before making, and samples sold at their own price.

_Not yet written._

More: [Made to order](../domains/made_to_order.md)

## Mobility

Moving people: rides requested and dispatched, drivers and their vehicles, and fleets.

_Not yet written._

More: [Mobility](../domains/mobility.md)

## Business operations

Running the business behind the store: people and payroll, manufacturing work orders, and projects with their tasks.

_Not yet written._

More: [Business operations](../domains/business_operations.md)

## Marketplace

Many sellers in one store: seller onboarding and health, offers competing for the buy box, fulfilment by the store, buyer protection claims, brand protection, and shoppers selling their own items.

_Not yet written._

More: [Marketplace](../domains/marketplace.md)

## Negotiation and auctions

Prices agreed rather than listed: offers and counter-offers between a buyer and a seller, and timed auctions with proxy bidding.

_Not yet written._

More: [Negotiation and auctions](../domains/price_discovery.md)

## Business-to-business trade

Buying between businesses: requests for quotation and quotes, tenders and bids, contracts, trade assurance, supplier verification and membership tiers, export documents, letters of credit and minimum order quantities.

_Not yet written._

More: [Business-to-business trade](../domains/trade.md)

## Reviews and questions

What buyers say: ratings and reviews with replies and votes, and questions with answers.

_Not yet written._

More: [Reviews and questions](../domains/reviews.md)

## Messages and notifications

Talking to people: conversations between buyers, sellers and staff, notifications to shoppers and staff, email, and marketing campaigns sent through connected messaging providers.

_Not yet written._

More: [Messages and notifications](../domains/communication.md)

## Customer support

Helping people: tickets with service levels and agents, and requests a store decides — price matches, prescriptions, credentials, enquiries, trade-ins — as cases of declared kinds.

_Not yet written._

More: [Customer support](../domains/support.md)

## Storefront and content

What a shopper sees: the home page's banners and cards, themes and their assignment, and the pages and their layout.

_Not yet written._

More: [Storefront and content](../domains/storefront.md)

## Search and discovery

Finding things: search, suggestions and facets, and recommendations.

_Not yet written._

More: [Search and discovery](../domains/search.md)

## Search engine optimisation

Being found from outside: the sitemap and its files, page metadata and product feeds.

_Not yet written._

More: [Search engine optimisation](../domains/seo.md)

## Languages and localisation

Speaking the buyer's language: the message catalogues of every language and a store's own wording.

_Not yet written._

More: [Languages and localisation](../domains/localisation.md)

## Consoles

The frames every domain's screens sit in: the store console and the platform console — signing in, navigation, layout, the shared table, form and chart parts — and nothing of any domain's own.

_Not yet written._

More: [Consoles](../domains/consoles.md)

## Analytics and reports

Knowing how the business does: dashboards and their widgets, reports and store statistics.

_Not yet written._

More: [Analytics and reports](../domains/analytics.md)

## Experiments

Testing what works: experiments with variants, who sees which, and what converts.

_Not yet written._

More: [Experiments](../domains/experiments.md)

## Risk and fraud

Stopping abuse: fraud screening of orders and payments, risk events and the block list.

_Not yet written._

More: [Risk and fraud](../domains/risk.md)

## Compliance and privacy

Meeting obligations: controls and their evidence, certifications, know-your-customer checks, consent, and privacy requests to see or erase data.

_Not yet written._

More: [Compliance and privacy](../domains/compliance.md)

## Audit

What happened, provably: the hash-chained audit trail, its verification, retention, the trash and exports.

_Not yet written._

More: [Audit](../domains/audit.md)

## AI

Machine help: AI providers and gateways, AI tasks and their metering.

_Not yet written._

More: [AI](../domains/ai.md)

## Integrations and webhooks

Connecting outside systems: connectors and providers registered as data, custom providers, outgoing webhooks and their deliveries, incoming events.

_Not yet written._

More: [Integrations and webhooks](../domains/integration.md)

## Rules, states and settings

How behaviour is configured: applicability rules, state machines, settings and their defaults, and platform policy.

_Not yet written._

More: [Rules, states and settings](../domains/rules.md)

