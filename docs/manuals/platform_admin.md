# Manual — Platform administrator

Everything a platform administrator does on the platform, domain by domain. Generated from each domain's documentation.

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

## Currencies and exchange

Every unit of value and how they convert: currencies, points and credits, and exchange rates.

_Not yet written._

More: [Currencies and exchange](../domains/currency.md)

## Offers

Every reason a buyer pays less or gets more: offers and discounts of every type, coupons, cashback, rewards, gift cards and vouchers, deals and countdowns, group buying, price matching and trade-ins, the funding and settlement of each, and their governance.

_Not yet written._

More: [Offers](../domains/offer.md)

## Payment gateways

Taking money: the gateways a store accepts and their methods, payment attempts and captures, gateway callbacks, payment links, QR and instant-bank collection, mandates, escrow and split payments.

_Not yet written._

More: [Payment gateways](../domains/payments.md)

## Wallets

Value a party holds: wallets of any definition, the ledger every movement is posted to, holds, transfers between wallets and between people.

1. Wallet definitions are the platform's. Declare or change one with
   `POST /api/platform/wallet-definitions` — `{ key, parent, name: { <language>: text }, aliases,
   settings: { openable, classes, operations, overdraft, max_balance, max_per_owner, hold_minutes } }`.
   Only the settings you state are set; the rest are inherited from the parent definition.
   A platform-console screen for definitions is not built yet.
2. The value classes a definition may hold are Value's classes; the operations are the wallet's
   declared operations — anything else is refused.
3. Every store's ledger check is available to its administrators; the event log it verifies is the
   platform's single tamper-evident record.
4. Holders are stored encrypted and found by a keyed index; rotating the encryption key keeps that
   index usable (it is derived from the keyring's first key).

More: [Wallets](../domains/wallet.md)

## Settlements and payouts

Paying those who are owed: seller settlements, payout batches, bank payouts, reconciliation of what the bank says against what the ledger says, and remittances.

_Not yet written._

More: [Settlements and payouts](../domains/settlement.md)

## Tax

What tax applies and how much: tax modes, rules by place and product, and how tax is shown and charged.

_Not yet written._

More: [Tax](../domains/tax.md)

## Shipping and delivery

Getting goods to the buyer: carriers and rates, shipments and tracking, pickup points and lockers, and fast local delivery from dark stores with slots, riders and dispatch runs.

_Not yet written._

More: [Shipping and delivery](../domains/shipping.md)

## Marketplace

Many sellers in one store: seller onboarding and health, offers competing for the buy box, fulfilment by the store, buyer protection claims, brand protection, and shoppers selling their own items.

_Not yet written._

More: [Marketplace](../domains/marketplace.md)

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

## Security

Protecting the platform: encryption and key rotation, the security policy and scorecard, idempotency and request protection.

_Not yet written._

More: [Security](../domains/security.md)

## AI

Machine help: AI providers and gateways, AI tasks and their metering.

_Not yet written._

More: [AI](../domains/ai.md)

## Integrations and webhooks

Connecting outside systems: connectors and providers registered as data, custom providers, outgoing webhooks and their deliveries, incoming events.

_Not yet written._

More: [Integrations and webhooks](../domains/integration.md)

## Kernel and registries

The foundation every domain is built on: kinds, entities, identifiers, hierarchies, versions in time, settings resolved by context, the event log, and the registries and entity definitions the console edits.

_Not yet written._

More: [Kernel and registries](../domains/kernel.md)

## Rules, states and settings

How behaviour is configured: applicability rules, state machines, settings and their defaults, and platform policy.

_Not yet written._

More: [Rules, states and settings](../domains/rules.md)

## Places and time

Where and when: countries, subdivisions and places, coordinate systems, calendars and time.

_Not yet written._

More: [Places and time](../domains/geography.md)

## Platform knowledge

The platform describing itself: the constitution, its foundations, universes, catalogue, coverage, traceability and documents.

_Not yet written._

More: [Platform knowledge](../domains/knowledge.md)

## Runtime and operations

Running the platform: environments, configuration, the database and its migrations, queues, monitoring, metrics, logs, backup and restore.

_Not yet written._

More: [Runtime and operations](../domains/runtime.md)

