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

The offers themselves: every price a buyer pays less or gets more, and every rule about how they apply — the offer record, its types, its scopes, its channels, its funders, its stacking policy and its governance. A coupon, a voucher, a gift card, a cashback, a reward and a group buy are their own domains; this one decides which of them applies.

_Not yet written._

More: [Offers](../domains/offer.md)

## Group buying

A lower price when enough shoppers join before a deadline: staff open a campaign on a product with a group price, how many members it needs and how many it may take; a shopper joins by buying at the group price. A campaign that reaches its members succeeds and its orders go ahead; one that falls short fails and every member's order is cancelled and refunded.

Open **Offers → Group Buying**, create the campaign and monitor members. Use **Settle ended groups** after deadlines, or cancel an open campaign when necessary. Verify wallet refunds and order states after a failed campaign.

More: [Group buying](../domains/groupbuy.md)

## Coupons

The codes a shopper types at the cart: a code that carries a value, issued by staff or in bulk, validated against its kind and its limits, redeemed into the redemption ledger, and voided when the order is refunded. The kinds — a single-use code, a bulk lot, a referral code — are rows.

Open **Offers → Coupons**. Issue a single code or batch, set its kind, value, funder and limits, and give the code to its intended audience. Use the redemption table and analytics to reconcile usage. Void an unused or compromised code; refunds automatically claw back redemptions.

More: [Coupons](../domains/coupon.md)

## Vouchers

An instrument of value that is not the shop's own discount and not a gift card: a bank voucher, a benefits note, an organisation's credit. Who stands behind it, whether it may be spent in part and how long it lives are its kind's rows; the code it travels on belongs to the Coupon domain.

Accept only voucher kinds and issuers enabled by platform policy. Reconcile voucher redemptions by issuer and funder, and investigate mismatches through the audit trail rather than editing ledger rows.

More: [Vouchers](../domains/voucher.md)

## Gift cards

A card bought as an item or issued by staff: a code with a value, sent to its recipient with a message, redeemable into the recipient's gift balance, checked for its balance, voided with a reason and expired after its validity. A card is a node on the kernel; its code is sealed and found by a blind index.

Open **Gift Cards** to configure the capability, issue a card, provide the recipient details and record the one-time code securely. Use the card list to check state and void compromised or incorrectly issued cards with a reason.

More: [Gift cards](../domains/giftcard.md)

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

## Books

A store's accounts: the chart of accounts on the kernel, entries posted to the platform's one ledger — automatically from payments, refunds, chargebacks and invoices, or by an accountant — and the trial balance, profit and loss, balance sheet and account ledgers read from them; and what the stock on hand is worth — cost layers from goods received, each unit that leaves costed first-in-first-out or at the weighted average, posted as cost of goods sold.

Open **Payments & Finance → 📒 Books**. Your role needs the books section; the Finance role has it.

- **Profit and loss** shows income, expenses and profit; **Balance sheet** shows what the store has
  against what it owes and its equity; **Trial balance** shows every account's debits and credits.
  Each currency the store trades in has its own statements. Add `from` and `to` (or `at` for the
  balance sheet) to the API call for a period.
- **Post an entry**: choose the account to debit and the account to credit, the amount, and what it
  is for. Entries that do not balance are refused.
- **Reverse** an entry you posted, saying why. It can be reversed once.
- **Stock value** shows what the stock on hand is worth and whether it matches the books. Choose
  *First in, first out* or *Weighted average*; stock already on hand keeps its cost. Give items
  with no cost yet their opening unit cost.
- **Chart of accounts**: every store starts from the platform's chart. Add your own account under a
  group; it takes the group's type and only your store sees it. Codes are never reused.
- Your accounting system can read the same figures with a store API key with the Finance role:
  `GET /api/admin/books/trial-balance`, `/profit-and-loss`, `/balance-sheet`, `/entries` — see
  `docs/api/README.md`.

More: [Books](../domains/books.md)

## Purchasing

Buying from suppliers: purchase orders (from an approved purchase request or on their own), the goods received against them into a warehouse batch, and suppliers' bills matched against what was received — held beyond the tolerance, approved, paid or voided — each posting to the store's books.

Open **Payments & Finance → 🧾 Purchasing**. Your role needs the purchasing section; the Finance
role has it.

- **New purchase order**: choose the supplier and the warehouse, the item, the quantity and the
  unit cost, then **Draft the order**. Open it and **Send to supplier**.
- **Record goods received**: open the order, set how many of each line arrived (the rest is
  pre-filled), the warehouse, lot and expiry, and record it. Stock goes up immediately.
- **Record the bill**: enter the supplier's invoice number, the net and the tax. If it differs from
  what was received by more than the tolerance it is held: check it, then **Release** it with the
  reason, or **Void** it.
- **Mark paid** when the supplier has been paid. **Owed to suppliers** shows what is due and how
  late, per supplier.
- Your purchasing or ERP system can do the same through `/api/admin/purchasing/…` with a store API
  key with the Finance role — see `docs/api/README.md`.

More: [Purchasing](../domains/purchasing.md)

## Customer relationships

The companies a store sells to and the people there, deals through the store's own pipeline to won or lost with a weighted forecast, the calls, meetings, emails, tasks and notes on a timeline, and one view of each customer — orders, spend, returns, support cases, wallet, segments, deals and activities.

Open **Customer Care → 🤝 CRM**. Your role needs the crm section: the Growth role can change it,
Support can read it.

- **Pipeline**: open a deal, move it between stages with the stage list on its card, and mark it
  **Won** or **Lost** (with the reason). **Open** shows its timeline.
- **Companies** and **Contacts**: add them; open a company to see its people, deals and timeline,
  and record an activity. A contact with a shopper account has **Customer view**.
- **Agenda**: what is still to do, by due date. **Forecast**: the pipeline by month.
- To set your own stages, use `PUT /api/admin/crm/stages`; your CRM or sales tools can use every
  `/api/admin/crm/…` route with a store API key — see `docs/api/README.md`.

More: [Customer relationships](../domains/crm.md)

## Campaigns

Email, SMS and in-app messages to a store's customers, a segment, its CRM contacts or a company's people — only to those with a live marketing consent, checked when the list is built and again before each message — with an unsubscribe link in every one, sent once per person even by several servers, scheduled or sent now, and counted.

Open **Marketing & Growth → 📣 Campaigns**. Your role needs the campaigns section; the Growth role
has it.

- **New campaign**: name it, choose the channel and audience (and the segment or company), write the
  subject and message, then **Draft the campaign**.
- Open it to see how many it would reach and who it would skip, then **Send now** or **Schedule**.
- Afterwards it shows how many were sent, skipped, failed and unsubscribed, and why.
- Email and SMS go through your notification gateway (**Payments & notifications**); without one
  they are counted as failed.

More: [Campaigns](../domains/campaigns.md)

## Consultancy and professional services

The work a store's people do for its clients and how it is billed: projects for a CRM company billed by time and materials, a fixed fee in instalments or not at all; a timesheet per person and week, approved by someone else and priced at each person's rate; expense claims owed and paid back and billed on; invoices to clients drafted from approved, unbilled time and expenses, each billed once, posted to the books; proposals from a deal answered from the client's private link, starting the project and winning the deal; the resource plan and utilisation.

Open **Business Operations → ⏱️ Consulting**. Your role needs the consulting section; the Delivery
and Finance roles have it.

- **Projects**: each project with how it is billed, what is ready to bill, invoiced and paid. Open
  one to set its billing, client, currency, rate an hour, tax and fixed fee, and a person's own rate
  on it. **Draft an invoice** from what is ready, or bill a fixed-fee instalment. Projects
  themselves are added under **Business Operations → Projects**, or start when a proposal is
  accepted.
- **People and rates**: what each person is billed at, what they cost and their hours a week.
- **Timesheets**: choose a person and any day of the week, then **Open**. Add time, **Save the
  week**, and **submit** it.
- **Approvals**: weeks and expense claims waiting for you. **approve** or **reject** each one, giving
  a reason. You cannot approve your own.
- **Expenses**: claim an expense, then **submit** it; once approved, **reimburse** it when it is paid
  back.
- **Invoices**: open one to **issue** it (with an email address to send it to), record it **paid**,
  **void** it, or print it.
- **Proposals**: draft one from a deal, one line each as `kind | what | quantity | rate`, then
  **send** it. You get the client's link to copy. Record an answer given another way with **accept**
  or **decline**.
- **Plan** and **Utilisation**: book people onto projects week by week, and see how they are used.

More: [Consultancy and professional services](../domains/consulting.md)

## Leave

Time away a store's people ask for: kinds of leave with yearly allowances and carry-over, requests counted in working days, refused when they overlap or ask for more than is left, approved by someone other than the person, shown in attendance as paid or unpaid for payroll, taken off the resource plan, and cancelled before they start.

Open **Business Operations → 🌴 Leave**. Your role needs the leave section; the People and Delivery
roles have it.

- **Ask for leave**: choose the person, the kind and the dates, then **Ask**. **Show balance** shows
  what they are entitled to, carried in, have taken, are waiting for and have left.
- **Requests**: **approve** or **reject** each one, giving a reason to reject. You cannot approve
  your own. **cancel** withdraws a request, or approved leave that has not started.
- **Who is away**: everyone away on each working day for the next four weeks; a question mark means
  not yet approved.

More: [Leave](../domains/leave.md)

## Fixed assets

What a store owns and uses for years: bought onto the books from the bank or on credit, depreciated month by month once — straight line or declining balance — to its residual value, posted as each month ends, sold or written off with the gain or loss posted, with its whole schedule and the register's totals.

Open **Payments & Finance → 🏷️ Fixed Assets**. Your role needs the fixed assets section; the Finance
role has it.

- **Register an asset**: name, category, cost, residual value, life (left empty, the category's),
  method, the day it was bought and how it was paid.
- **Depreciation**: choose a month and **Post depreciation**. Months already posted are left alone.
- Open an asset to see every month of its schedule, posted or to come, and to **Sell or write off**
  it, saying why.
- The register shows each asset's cost, depreciation to date and book value, with totals by category.

More: [Fixed assets](../domains/assets.md)

## Budgets

A year's plan per income and expense account of the books, month by month in one currency, set by month or spread from a year's amount or from last year's actuals, approved once per year and currency, and set against the books to date with what is off plan flagged.

Open **Payments & Finance → 🎯 Budgets**. Your role needs the budgets section; the Finance role has
it.

- **New budget**: name it, choose the year (and currency), then **Draft**.
- Open it to set an account's amount for the year (**Set, spread evenly**) or **Fill** it from a
  year's actuals with an uplift, then **Approve**.
- The report below shows each account against the books, and flags what is off plan.

More: [Budgets](../domains/budgets.md)

## Material requirements planning

What to make and buy, and by when: bills of materials to any depth without cycles, a master schedule of what must be ready, netting level by level against stock, open purchase and work orders and safety stock, lead times and lateness, and suggestions turned once into draft purchase orders per supplier and planned work orders.

Open **Business Operations → 🏭 Planning (MRP)**. Your role needs the mrp section; the Planning role
has it.

- **Bill of materials**: type the item's code and **Show**. Write one component a line as
  `item code | quantity | % lost`, then **Save the bill**.
- **Planning for an item**: its lead time, safety stock and smallest lot.
- **What must be ready**: add what must be ready by when.
- **Plan**: **Run planning**, check what it suggests, dismiss what you will not do, then **Make the
  orders**. Purchase orders are drafts to check and send under Purchasing.

More: [Material requirements planning](../domains/mrp.md)

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

