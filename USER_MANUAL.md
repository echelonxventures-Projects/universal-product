# LUXORA Platform — User Manual

This manual is written for every kind of person who touches the platform: **End
Customers**, **Store Administrators**, **Support Staff**, **Marketplace Sellers**, and
the **Platform (Super) Administrator**. Each part is a standalone guide — read the one
that matches how you use the system, and refer to the Appendices for shared topics
(log‑in, security, troubleshooting).

LUXORA is a white‑label, multi‑store commerce platform. Everything you see on a store
— its catalogue, categories, branding, currency, taxes and payment options — is
*configuration data*, not code. The same back end powers tiny single‑brand boutiques
and large multi‑seller marketplaces.

---

## Table of contents

1. [Accessing the platform](#1-accessing-the-platform)
2. [Demo accounts (reference stores)](#2-demo-accounts-reference-stores)
3. [Roles at a glance & capability matrix](#3-roles-at-a-glance--capability-matrix)
4. [Part A — End Customer guide](#part-a--end-customer-guide)
5. [Part B — Store Administrator guide](#part-b--store-administrator-guide)
6. [Part C — Support Staff guide](#part-c--support-staff-guide)
7. [Part D — Marketplace Seller guide](#part-d--marketplace-seller-guide)
8. [Part E — Platform (Super) Administrator guide](#part-e--platform-super-administrator-guide)
9. [Security & account safety (all users)](#9-security--account-safety-all-users)
10. [Appendices](#appendices)

---

## 1. Accessing the platform

There are three "surfaces". Which one you use depends on your role.

| Surface | URL (default install) | Who uses it |
|---|---|---|
| **Storefront** | `http://localhost:8787/` | End customers |
| **Store Console** | `http://localhost:8787/admin.html` | Store administrators, support staff |
| **Platform Console** | `http://localhost:8787/platform.html` | Platform (super) administrators |

> Your host/port may differ (for example `:3000`). Ask whoever runs your instance for
> the correct URL.

### Switching between stores

LUXORA serves many independent stores ("tenants") from one install. You select a store
in three ways — all equivalent:

- **Query string:** append `?store=<slug>` to any URL, e.g. `/admin.html?store=aurum`.
- **Subdomain:** visit `<slug>.localhost:<port>` (e.g. `aurum.localhost:8787`).
- **Store picker cookie:** once you've used `?store=` it is remembered for later visits.

You must sign in **per store** — a Store Administrator of *LUXORA* has no access to
*AURUM*'s data. Data is strictly isolated between stores.

### Secure mode (HTTPS)

If the operator started the instance with TLS enabled, all three surfaces are served over
`https://`. The security behaviour is identical; only the scheme changes.

---

## 2. Demo accounts (reference stores)

The installer seeds **three stores that demonstrate the three deployment modes**, plus a
platform super‑admin and a demo customer. Use them to learn; rotate passwords before any
real use.

| Store | Mode | Region / currency / rails | Role | Email | Password |
|---|---|---|---|---|---|
| **LUXORA** (`luxora`) | Marketplace | US · USD · Stripe | Super admin | `platform@luxora.shop` | `platform123` |
| | | | Store admin | `admin@luxora.shop` | `admin123` |
| | | | Customer | `demo@luxora.shop` | `demo123` |
| **AURUM ATELIER** (`aurum`) | Industry | India · INR · GST · Razorpay/UPI · Delhivery | Store admin | `admin@aurum.shop` | `aurum123` |
| **VELORA** (`velora`) | Brand (jewellery) | UAE · AED · VAT · Tabby BNPL | Store admin | `admin@velora.shop` | `velora123` |

- **Marketplace** — a general store that may host many sellers and the widest catalogue.
- **Industry** — a store scoped to a chosen set of industries (e.g. fashion, home, health).
- **Brand** — a single‑label boutique with bespoke branding, copy and checkout wording.

> **Demo password hints** appear on the sign‑in screens while the seeded passwords are in
> use. They disappear automatically the moment a password is changed, and the operator can
> hide them globally. Change these passwords before exposing the platform to anyone.

---

## 3. Roles at a glance & capability matrix

LUXORA has **two enforced privilege scopes** built in — *Store* and *Platform* — plus the
*Customer*. "Support" and "Seller" are **modes of working** inside those scopes (see
Parts C and D), not separate logins.

| Capability | Customer | Store Admin | Platform Admin |
|---|:--:|:--:|:--:|
| Browse & search a storefront | ✅ | ✅ | ✅ |
| Add to cart, buy, gift cards, wishlist | ✅ | ✅ | — |
| Write product reviews | ✅ | ✅ (moderate) | ✅ |
| Place a B2B RFQ (quote request) | ✅ | respond ✅ | — |
| Open a return request | ✅ | approve/reject ✅ | — |
| View **own** orders only | ✅ | — | — |
| View/manage **all** orders, payments, refunds | — | ✅ | — |
| Manage catalogue, SKUs, inventory, warehouses | — | ✅ | — |
| Configure promotions & coupons | — | ✅ | gate ✅ |
| Edit home content, taxonomy, attributes | — | ✅ | — |
| Manage payment gateways (per store) | — | ✅ | approve registry ✅ |
| Onboard sellers & pay settlements | — | ✅ | — |
| View store analytics, audit trail, monitor | — | ✅ | ✅ |
| Launch / suspend whole stores | — | — | ✅ |
| Global geography, currencies, taxes, plans | — | — | ✅ |
| Install / uninstall / configure **modules** | — | — | ✅ (audited) |
| Global cross‑store audit & monitoring | — | — | ✅ |

*Legend:* ✅ full · "gate" = the platform can enable/disable a feature that store admins then
use · "respond/approve" = the counterparty action on a customer‑initiated request.

---

# Part A — End Customer guide

You are shopping a store (any of the seeded stores, or any store a business launched on
LUXORA). You do **not** need an account to browse or — on most stores — to check out, but
an account lets you track orders, save items and earn faster checkout.

## A1. Browse & find products
1. Open the **Storefront** URL for the store you want.
2. Use the **search bar** (top) for keywords, brands or product names.
3. Use **Departments / category rails** to drill into a category, then **Filters** on the
   results page — e.g. price range, brand, rating, and industry‑specific attributes
   (product type, size, colour, etc.).
4. On a product, read details that adapt to the item's *vertical*: e.g. expiry & allergens
   for groceries, hallmarks/carat for jewellery, or shipping class for logistics.
5. See **related items** and, on enabled stores, **recommendations**.

## A2. Save & track
- **Wishlist / Saved list** — tap the save/heart on any product; find them under *Saved*.
- **Recently viewed** — surfaced on your account/home so you can jump back.
- **Delivery estimate** — enter your ZIP / postal code to see whether an item reaches you
  and roughly when.

## A3. Cart & coupons
1. **Add to cart**, adjust quantities, or **Buy now** to go straight to checkout.
2. In the cart you'll see a running total and any **promotions applied automatically**
   (BOGO, spend‑and‑save, etc.).
3. Have a code? Type it in the **coupon/promo box** and apply. Invalid or expired codes are
   rejected with a reason.
4. Optional: redeem a **gift‑card balance** toward the total.

## A4. Gift cards
Go to **Gift Cards**, choose an amount (within the store's limits), and buy it as a digital
card. Recipients apply the code at checkout.

## A5. Checkout
1. Review the cart, then **Proceed to checkout**.
2. Enter **shipping details** (name, address, city, state, ZIP, phone).
3. Choose a **delivery option** (standard/express; cost and ETA are shown).
4. Choose a **payment method**. Stores present only the rails valid for their country — for
   example card/Stripe (US), Razorpay/UPI (India), or Tabby "buy now, pay later" (UAE). Cash
   on delivery may also appear.
5. Depending on the store's **industry**, checkout may ask for extra *context* — e.g. a GST
   / tax ID for B2B invoice contexts, or UAE VAT details. These are validated before you can
   place the order.
6. **Place order.** You'll get an order number and estimated delivery. (On some stores guest
   checkout is allowed; if a store requires an account, sign in first.)

## A6. Orders, returns & help
- **Your Orders** — see status (processing → shipped → delivered) and tracking/ETA.
- **Returns** — open a return request on an eligible order; add a reason. The store reviews
  it (see Part C for what happens next).
- **RFQ (B2B quotes)** — for wholesale/bulk, submit a **Request for Quote** with quantity
  and target price; the store responds with an offer.
- **Reviews** — after purchase you can rate and review items.
- **Customer Service** — the help centre walks you to order status, returns, shipping and
  contact options.

## A7. Your account
- **Register** with name, email and a password meeting the store's policy (see §9).
- **Sign in / out** anytime. Your cart, saved list, gift balance and orders are tied to your
  account and follow you across devices for that store.

---

# Part B — Store Administrator guide

You run **one** store. Everything under this section happens in the **Store Console**
(`admin.html`). Sign in with the store's admin account, and make sure you're pointed at the
right store (see §1 "Switching between stores").

## B1. The console layout
Left rail navigation:

| Section | Purpose |
|---|---|
| **◈ Dashboard** | At‑a‑glance KPIs, live traffic, things needing attention |
| **📦 Products** | The catalogue; the full product editor |
| **🔖 SKUs & Inventory** | Variants, stock levels, warehouse stock |
| **🧾 Orders** | Fulfilment pipeline |
| **↩️ Returns** | Customer return requests to approve/reject |
| **📋 RFQs (B2B)** | Quote requests to price & respond |
| **🏪 Sellers** | Marketplace partners & their terms |
| **🤝 Settlements** | Payouts to sellers (commission math) |
| **🎯 Promotions** | Rules & coupon codes |
| **🖼️ Home Content** | Banners & category cards on the storefront |
| **🌳 Taxonomy** | The category hierarchy (domain → … → model) |
| **🧬 Attributes** | Reusable product‑attribute definitions (EAV) |
| **💳 Payment Gateways** | Enable/configure/prime the store's payment & shipping providers |
| **🧩 Modules** | Paid add‑ons the platform has enabled for you |
| **⚙️ Settings** | Branding, copy, commerce, tax, deployment mode |
| **🧮 Billing** | Your invoices to the platform; self‑pay |
| **📊 Analytics** | Sales/traffic insight |
| **📜 Audit Trail** | Tamper‑evident log of everything done in your store |
| **📈 Monitor** | Live health & request metrics |
| **🛠️ Data Studio** | Direct, entity‑driven management of any data (incl. customers & custom objects) |

## B2. Manage the catalogue (Products, SKUs, Inventory)
1. **Products → New product** opens the full editor. Fill identity (title, brand,
   department), pricing, lifecycle state, media, and the attribute values that apply to the
   chosen industry.
2. Set **SKU variants** (size/colour/etc.) under **SKUs & Inventory**, and record stock per
   **warehouse**.
3. Control what the public sees via **lifecycle** — e.g. `draft` → `published`; a `suspended`
   product disappears from the storefront. Non‑published items are hidden from customers.
4. Editing a product's vertical/industry fields drives the extra checkout & detail fields
   customers see.

> **Taxonomy** defines the category tree; **Attributes** defines the reusable fields. You
> normally edit products against those definitions rather than inventing fields ad hoc.

## B3. Sell & fulfil (Orders, Returns, RFQs)
- **Orders** — move orders through their status; record shipping; issue **refunds** from a
  payment line. Search and filter by customer, status, date.
- **Returns** — review incoming requests (see Part C for the support workflow).
- **RFQs (B2B)** — a buyer has asked for a price/quantity; respond with an offer. Accepted
  RFQs lead to an order.

## B4. Grow & retain (Promotions, Sellers, Settlements)
- **Promotions** — create discount/BOGO/free‑ship rules with optional **coupon codes**,
  start/end dates and a scope (whole store, category or specific products). Once *active*,
  eligible carts auto‑apply them. (Coupons may be gated by platform policy.)
- **Sellers** (marketplace mode) — onboard partners, set their commission %, and activate or
  suspend them.
- **Settlements** — generate a settlement for a seller over a period; the console computes
  gross, commission and **net payable**. Mark each settlement `pending → paid`.

## B5. Present (Home Content, Settings)
- **Home Content** — build the storefront home: promotional **banners** and department
  **cards**, with ordering, tint and "active" toggles.
- **Settings**
  - **Branding** — store name, wordmark, tagline, colours, fonts, support email, footer.
  - **Copy** — the words customers see (search placeholder, "Add to cart" vs "Reserve",
    review heading, etc.).
  - **Commerce** — country, currency, locale, tax mode & rate, shipping fees/free‑ship
    threshold, gift‑card amounts.
  - **Deployment mode** — marketplace / industry / brand, and (for industry/brand) which
    industries this store sells.

## B6. Money & compliance (Payments, Billing, Audit, Monitor)
- **Payment Gateways** — enable providers available for your country, choose a **primary**,
  set **sandbox vs live** mode, and **test** a gateway before going live. Shipping and
  notification providers appear here too.
- **Billing** — see invoices issued by the platform (e.g. for paid modules) and pay them.
- **Audit Trail** — an append‑only, **hash‑chained** log of actions in your store. Use **Verify
  chain** to prove no entry has been altered. This is your compliance record.
- **Monitor** — live requests, latency and errors for your store.

## B7. Data Studio
Data Studio is the platform's "manage anything" surface. Every table is a declared **entity**
(fields, types, validation, permissions). Use it to:
- Bulk view/edit any object (orders, reviews, customers, attributes, …).
- **Define new entities** and have CRUD + validation + audit + forms appear automatically.
- Register **custom providers** as JSON manifests (no code).

This is how you extend the store without touching the source.

## B8. Offers & Coupons (central engine)
One discount engine powers cart, checkout, billing and AI — everything is configuration.
- **Build an offer**: pick a **type** (`% off`, fixed, free ship, BOGO, buy-X-get-Y, X-for-Y,
  multi-buy, bundle, tier, cashback→wallet, spend-get-credit…), a **scope** (whole store, a
  category, a taxonomy node, specific products, a brand), a **channel** (commerce,
  subscription, AI, any), and a **funder** (self / **bank** / **brand** / partner / platform).
- **Stacking**: exclusive / group-exclusive / max-count, per-order cap, min spend, priority.
- **Coupons**: a single code (or auto-applied), **single-use**, **first-order-only**, **bulk
  generate** codes, or a **gift-card** / **bank voucher**. Every redemption is logged with its
  **funder**, so a bank- or brand-funded discount can be settled back to them.
- **Credits / wallets**: cashback and spend-get awards go to the wallet (double-entry ledger);
  wallet balance is applied at checkout automatically.
- New types / scopes / channels / funders are edited in **Data Studio** (`offerTypes`,
  `offerScopes`, …) — no code.
- This builder is the classic surface over **GOIP Ω∞** (Part E5b): every save goes through the one
  value-exchange writer, so an offer created here is a full constitutional record — it can carry a
  reality, a calendar, a spatial scope, an economic unit, declared conditions, distribution channels,
  a multi-party funding split and a governance state, and it settles like any other exchange. Your
  store can call the same 22 capabilities at `POST /api/goip/<capability>` once the GOIP module is
  installed. The **Ω∞ GOIP** tab next door is where you test it: a decision tester that answers *what
  applies, what does not and why*, the exchanges this store owns and inherits, a subject lookup for
  entitlements and non-money balances, this store's funding budgets, and the capability list it may call.

**Enforced end-to-end (not just preview):**
- **Refund clawback** — refunding a payment (or marking a return *refunded*) voids the coupon/offer
  redemptions for that order, restores coupon usage counts, and reverses any wallet reward credits.
- **Currency safety** — an absolute-value offer (`fixed`, `fixed_per_item`, `bundle`, `multi_buy`,
  `spend_get_credit`) applies only when its currency matches the store currency; percentages / ratios /
  free-shipping are currency-agnostic; global offers honour this per store.
- **Usage + per-owner limits** — `usage_limit` and `per_owner_limit` are counted from live redemptions
  and released again on refund.
- **Auto lifecycle** — scheduled offers activate at start; past-end offers/coupons flip to `expired`.
- **Analytics** — redemption performance by code / funder / type / source, with discount + credit totals.

## B9. AI Studio
Every store gets the **free built-in AI engine** automatically (recommendations, image
processing, data analysis, data cleaning, reporting — computed from your own store data, no
keys, no cost). Turn on a **premium** model (OpenAI / Anthropic / Stability / Google Vision)
per capability only once the store is on a **paid plan** (or buys the AI Premium module) and
has configured provider credentials; otherwise it safely falls back to the free engine.
Usage is metered to an AI ledger and can appear on your invoice.

## B10. The wider catalogue model (what the new tabs add)
- **📝 Contracts** — standing B2B prices for a buyer (fixed/tiered, min qty, validity). A buyer
  with a contract automatically gets the contracted price at cart/checkout.
- **🏛️ Tenders** — open a tender for procurement, then **Award** to auto-create a contract.
- **🚚 Suppliers & Procurement** — your supply partners (lead time, MOQ, terms, certifications,
  price lists) linked to products (a product can have several, one primary).
- **🔢 Serialized Items** — track each physical unit (serial, IMEI/RFID, batch/lot, expiry,
  warranty, custody). Bulk-generate serials.
- **✅ Compliance & Certifications** — structured certificates (issuer, jurisdiction, valid
  dates) shown as badges on the storefront.
- **🌐 Localizations (i18n)** — per-product (and other objects) translations applied at the
  shopper's locale.

---

# Part C — Support Staff guide

> **Important:** LUXORA does **not** have a separate "support login." Support work is done
> *within the Store Console* by an admin account (or a staff account your admin provisions).
> The tasks below are the support duties of a Store Administrator. If you need a restricted
> "support‑only" role, an admin can model the workflow with Data Studio / custom entities and
> hand staff accounts only the console sections they need.

As support, your job is to resolve customer problems quickly while leaving a clean audit
trail.

## C1. Find a customer's order
- **Orders** — search by order number, customer email or name.
- Confirm status, shipping ETA, and whether the payment was captured/refunded.
- Never disclose another store's data — you only see your own store.

## C2. Handle a return request
1. Open **Returns**. New requests appear here when a customer submits one (§A6).
2. Check eligibility (item, timing, reason) against your policy.
3. **Approve** to start a refund/replacement, or **Reject** with a reason. The customer's
   order and payment lines reflect the outcome.
4. Every decision is recorded in **Audit Trail**.

## C3. Answer an RFQ (B2B quote)
- In **RFQs**, open the buyer's request (quantity, target price), then **respond** with your
  offer. A good offer converts to an order the buyer places from the storefront.

## C4. Moderate reviews
- Reviews customers post are visible to you; in the console (or Data Studio → Reviews) you can
  remove content that breaches policy. Removals are audited.

## C5. Direct a customer to self‑service
- Point them to **Customer Service** (order status, returns, shipping, contact), the
  **Gift Cards** and **Wishlist** pages, and the delivery‑estimate box, to deflect routine
  asks.

## C6. Good‑practice checklist
- Resolve within your SLA; keep a written reason on every return/RFQ/refund.
- Prefer the guided console flows over raw edits; use Data Studio only when needed (it audits
  too).
- If a change touches payments, taxes or store configuration and you're unsure, escalate to a
  senior store admin or the Platform team.

---

# Part D — Marketplace Seller guide

A **Seller** is a partner who lists and ships goods through a *marketplace* store (the
LUXORA store runs in marketplace mode). In this build, sellers are **managed by the store
admin** — a seller typically does not self‑log‑in. If you operate a seller portal, model it
on top of LUXORA (Data Studio + providers). The workflow you care about:

1. **Onboarding** — the store admin records you in **Sellers** with your contact, role and a
   **commission %**, and sets your status to `active`.
2. **Selling** — your products are fulfilled through the store; orders land in the store's
   **Orders** pipeline.
3. **Settlement** — the admin periodically generates a **Settlement** for your sales over a
   period: it computes **gross**, the platform **commission**, and your **net payable**, then
   pays you and marks it `paid`.
4. **Disputes / returns** — handled by store **Support** (Part C); keep your listings accurate
   to avoid return liability.

> Your agreement (commission rate, payout cadence, which products you own) is a business
> arrangement with the store; LUXORA records and computes it for you.

---

# Part E — Platform (Super) Administrator guide

You run the **whole platform**: you launch stores, set global rules, sell subscriptions and
modules, and keep the fleet healthy and compliant. All of this happens in the **Platform
Console** (`platform.html`) — sign in with the platform account (`platform@luxora.shop` in
the seed). Platform identity is separate from any store; a platform admin is not "the admin
of a store."

## E1. The console layout

| Section | Purpose |
|---|---|
| **◈ Command** | Platform‑wide KPIs: MRR, collected revenue, GMV, store counts |
| **🛡️ Provisioning** | Policy that governs how stores can be launched (plans, limits, defaults) |
| **🏬 Stores** | Launch wizard + manage all tenants |
| **🌍 Geo · Countries · Taxes** | Countries, currencies & FX, tax modes, and which providers are available per country |
| **💼 Plans** | Subscription tiers & pricing |
| **🔁 Subscriptions** | Each store's plan binding & status |
| **🧾 Invoices** | Platform billing to stores |
| **🧩 Module Marketplace** | Sell/enable add‑ons and install them on stores (audited) |
| **🔌 Provider Registry** | The global catalogue of payment/shipping/notification/tax providers + custom manifests |
| **Ω∞ GOIP · Value Exchange** | The Global Offer Infrastructure Platform control plane — constitution, 22 capabilities, 67 domains, every registry, funding → settlement → payout, attribution, intelligence, commercialization (see **E5b**) |
| **📈 Monitoring** | Fleet‑wide traffic & health |
| **📜 Global Audit** | Cross‑store, tamper‑evident log |

## E2. Launch a new store (Stores → Launch wizard)
Walk through the wizard to provision a tenant in one flow:
1. **Identity** — store name, slug, tagline, owner name/email/phone, legal entity, tax ID.
2. **Jurisdiction & taxation** — pick the country; this sets the default currency, locale and
   tax mode (from your Geo settings). Override only deliberately.
3. **Catalogue scope** — choose the industries/categories the store will sell.
4. **Gateways** — enable the payment/shipping providers available in that country.
5. **Plan** — assign a subscription plan.
The new store appears with its own admin account (owner). Hand credentials to the owner.

## E3. Govern with Provisioning & Plans
- **Provisioning** sets the guardrails every store inherits: allowed industries/features,
  policy gates over store capabilities (e.g. whether coupons or currency overrides are
  permitted), and defaults.
- **Plans** define subscription tiers (price, limits). **Subscriptions** binds a store to a
  plan and tracks `trialing / active / …`. Change a store's tier here.

## E4. Global Geo, currencies & providers (Geo, Provider Registry)
- **Countries** — add/edit the countries stores can operate in (currency, locale, default tax
  mode & rate).
- **Currencies & FX** — manage currency entities and exchange rates (with history; optionally
  sync from a JSON rate feed).
- **Tax modes** — define how tax is applied (e.g. GST vs VAT vs none).
- **Providers & availability** — the provider registry lists all payment/shipping/notify/tax
  integrations and *which countries each is available in* (a relation table). Add **custom
  providers** by registering a JSON manifest — no code.

## E5. Monetise with Modules (Module Marketplace)
Modules are paid add‑ons that light up storefront capability (e.g. SEO Pro, Offers Pro,
Wallet, Recommendation Engine, Identity Pro, Billing Pro, catalog "packs").
1. Author/manage module definitions (price, capabilities) — they are editable entities.
2. **Install** a module on a store — this bills an invoice and applies the module's effect.
3. **Configure** an installed module's options, or **Uninstall** to remove it.
> Every install/uninstall/configure is written to the **Global Audit** trail (with the acting
> admin and IP). After changes, the storefront updates immediately.

## E5b. Ω∞ GOIP — the Global Offer Infrastructure Platform

This screen replaces the old *Global Offers* page. It is not a coupon editor: it is the control plane for
**every** incentive, offer, promotion, benefit, entitlement, subsidy, commission, loyalty construct or
future value-exchange model the platform can express — across any industry, organization, country,
planet, economy, calendar, governance model or reality, without redesign.

**What a value exchange is.** One record that walks one chain: *value exchange → context → conditions →
eligibility → benefit → execution → settlement → audit*. A "10% coupon", a bank cashback, a government
subsidy, a creator commission, a membership upgrade and a Mars-colony credit are the same record with
different registry values.

**The nine surfaces**

| Tab | What you do there |
|---|---|
| **Ω Constitution** | The 8-stage chain, the zero-gap scorecard (capabilities bound, domains with distinct owners, benefits with math), and the experience/access fabrics with what each is bound to |
| **⚡ Capabilities** | All 22 capabilities with stage, engine, the store each writes and the meter each bills — plus a live console that invokes any of them with a JSON body |
| **🌐 67 Domains** | Every constitutional domain, its owning store, the exact discriminator that isolates its rows (this is what makes overlap impossible), and live record counts |
| **💠 Value Exchanges** | Publish a *global* exchange every store inherits — choosing benefit, domain, funder, economic unit, reality, calendar, place prefix, distribution channels, declared conditions, multi-party funding split and governance state — then publish / suspend / version it |
| **📚 Registries** | Calendars, chronologies, temporal units, spatial systems, coordinate systems, hierarchy paths, economic units, reality models and every fabric — all editable in **Data Studio → Registries** |
| **🏦 Funding · Settlement** | Allocate budgets per funder/unit/domain, watch burn, run the settlement, approve, pay out with a reference, reconcile against a bank statement |
| **🔗 Attribution · Graph** | Touchpoints captured from any surface; replay a subject's path through any attribution model to split revenue and commission; the 21-node / 14-relationship incentive graph |
| **🧠 Intelligence** | 15 readings over live data — deal, offer, price, audience, merchant, provider, partner, fraud, optimization, forecast, recommendation, AI offer/incentive generation, autonomous campaign and optimization |
| **💳 Commercialization** | 11 deployment models, 12 billing models with their live metered quantities and accrued charges, and which stores have purchased GOIP |

**Governing an exchange.** Lifecycle is a state machine: `draft → submitted → approved → certified →
published → suspended → retired`. Illegal jumps are refused. *Version* forks a draft that inherits the
public code only when it is published — at which point it supersedes and retires the version it replaced,
so a code is never live on two records at once.

**Settlement is exactly-once.** Every redeemed-but-unsettled redemption is attributed to its funding
parties (including multi-party splits) once and stamped; re-running the settlement settles nothing twice.
Refunding an order recovers the accrual and revokes entitlements granted by it.

**Selling it.** GOIP is a marketplace module (**Value Exchange** category). Every capability call meters
into the billing engine and appears on the store's next invoice; stores without the module are metered at
zero. Agent and MCP callers buy `goip-agent` and speak the same 22 capabilities.

**Test it in five minutes** (everything below ships seeded on first boot):

1. **Platform → Ω∞ GOIP → Value Exchanges.** Seven global exchanges are already published. Note their
   contexts: one is priced in Mars Credits and scoped to Olympus Territory, one is restricted to Bihar,
   one is funded 70/30 by a bank and a brand.
2. **Store console → Ω∞ GOIP → Decision tester.** Enter amount `200`, code `GOIPSOL`, leave the place
   empty → **0**, with the reasons printed: wrong calendar, wrong spatial system, wrong economic unit.
   Set place to `mars.olympus.sector-7` and unit to `MARS_CREDIT` → **30**, and the context line shows
   the Darian calendar, which nobody typed: the place resolved its own temporal authority.
3. Try `GOIPGOV` with place `earth.in.bihar.patna` (→ 25) and then `earth.us` (→ 0, jurisdiction).
4. Try `GOIPWELCOME` with subject `t1:u:999` (no orders → 10%) and then with a subject that has orders
   (→ refused by the declared condition, not by a hardcoded flag).
5. **Storefront → The Edit (`/deals.html`).** The offer strip lists what is available on the in-app
   channel; clicking a code tracks a touchpoint and applies it to the cart. Check out to see the
   benefit land, then look at **Store console → Ω∞ GOIP → Subject lookup** for the wallet, the POINT
   balance and any entitlement granted.
6. **Platform → Ω∞ GOIP → Funding · Settlement.** Press **Run settlement**: redemptions attribute to
   their funding parties (the bank and the brand split 70/30; a points liability settles in POINT, not
   cash). **Pay** one, then **reconcile** it. Press **Run settlement** again — nothing double-counts.
7. **Platform → Ω∞ GOIP → Attribution** (replay a subject's path through any model), **Intelligence**
   (15 live readings), and **Commercialization** (the meters your capability calls just billed).
8. **Capabilities tab → capability console.** Invoke any of the 22 verbs with a JSON body and read the
   raw response — this is exactly what an SDK, an agent or a partner system sees.

**For developers.** One entry point — `POST /api/goip/<capability>` — plus read surfaces
`GET /api/goip` (the machine-readable constitution), `/api/goip/exchanges`, `/api/goip/context`,
`/api/goip/treasury`, `/api/goip/settlements`, `/api/goip/entitlements`, `/api/goip/touchpoints`,
`/api/goip/registry/<name>`, `/api/goip/intelligence/<key>`, `/api/goip/feed/<channel>` and
`/api/goip/widget` (embeddable). Access follows each capability's scope: `any` (a shopper session),
`tenant` (store admin) or `platform` (this console).

## E6. Watch & prove (Monitoring, Global Audit, Security)
- **Monitoring** — fleet traffic, latency and errors per store.
- **Global Audit** — search across all stores; run **Verify chain** on any scope to detect
  tampering.
- **Security scorecard** — `GET /api/platform/security` returns the live 10‑layer posture
  (transport, session/CSRF, credentials, password policy, at‑rest encryption, keyring, audit
  chain, rate/lockout, supply‑chain SRI, isolation) and whether the audit chain is intact.

## E7. Suspend / resume a store
From **Stores**, change a tenant's status. A `suspended` store blocks storefront/API
mutations for everyone except platform admins (a kill‑switch for abuse or non‑payment).

---

## E8. Enterprise ops (Platform → Runtime & store 🔐 SSO & Integrations) — all OFF until configured
- **Database**: set driver **postgres** + connection string → *Test / Dry-run / Apply / Revert* runs the
  async dual-engine + SQLite→Postgres migration planner against your live PG (SQLite until then).
- **SSO/SAML + SCIM**: per-store SSO connection (okta/entra/google/generic + allowed email domains) and
  a bearer-token SCIM endpoint so HR/IdP sync staff accounts (mapped to RBAC roles).
- **Regions / Edge**: manage the region list + CDN base URL; asset URLs rebase to the CDN when set.
- **Observability**: `GET /metrics` (Prometheus), `/healthz`, structured JSON logs, trace ids.
- **Feeds / inventory / tax**: Shopping product feeds, warehouse stock transfers, tax remittance report.

Everything here is fill-in-the-blank **config** (URLs, keys, IdP metadata, connection strings); nothing
activates until you write its config, and all of it is tenant-isolated + audited.

---

## 9. Security & account safety (all users)

Your safety is enforced by a 10‑layer stack; here's what it means for you:

- **Passwords** must meet the store's policy (by default **≥ 8 characters**, letters + digits,
  not a common/guessable password, and not one you've used before). Pick a unique password;
  the platform stores it with a strong, peppered hash — staff never see it.
- **Sessions & CSRF** — logins are pinned to a store and mutations are double‑submit checked,
  so cross‑site tricks are blocked. **Always sign out on shared computers.**
- **Rate limits & lockout** — repeated failed logins temporarily lock an account. If locked,
  wait or ask your admin; don't share credentials.
- **Encryption at rest** — payment‑gateway secrets are envelope‑encrypted per store.
- **Tamper‑evident audit** — every privileged action is hash‑chained and verifiable; nobody
  can quietly edit history.
- **Transport** — enable HTTPS in production; cookies are hardened.

**For operators/admins:** change every seeded password, hide demo hints, set
`LUXORA_MASTER_KEY`/`LUXORA_PEPPER`, and rotate keys from the console (rotation re‑wraps all
secrets). Credentials are configurable via environment variables
(`PLATFORM_EMAIL/PASSWORD`, `ADMIN_EMAIL/PASSWORD`, `DEMO_PASSWORD`, …) before first boot.

---

## Appendices

### A. Password / account change
- **Customer / Store Admin:** sign in to the Store Console (admins) or your storefront
  account → account settings → change password.
- **Platform Admin:** via the Platform Console.
- Changing a password removes the "demo" hints for that account.

### B. Switching stores / finding the right console
Use `?store=<slug>` or the `<slug>.localhost` subdomain. The Store Console shows the store
name/wordmark once signed in — double‑check you're in the intended store before acting.

### C. Glossary
| Term | Meaning |
|---|---|
| Tenant / Store | One independent storefront (`luxora`, `aurum`, `velora`) with isolated data. |
| Deployment mode | `marketplace` · `industry` · `brand`. |
| SKU | A stock‑keeping variant of a product (size/colour/etc.). |
| EAV / Attribute | Flexible attribute model; attributes are reusable definitions. |
| Taxonomy | The category hierarchy (domain→industry→category→subcategory→family→model). |
| Context | Industry data validated at checkout (tax / invoice / payment info). |
| Provider | A pluggable payment/shipping/notification/tax integration. |
| Module | A paid add‑on that enables extra capability on a store. |
| RFQ | Request for Quote (B2B). |
| Settlement | A computed payout to a seller (gross − commission = net). |
| Data Studio | Entity‑driven management & extension surface. |
| Audit chain | Append‑only, hash‑linked action log; verifiable for tampering. |

### D. FAQ
- **Why can't an admin of one store see another store?** Tenant isolation is enforced; use the
  right `?store=` and your store‑specific account.
- **Guest vs account checkout?** Most stores allow guest checkout; some (with Identity‑pro
  type policies) require sign‑in. An admin controls this.
- **A coupon didn't apply?** It may be expired, out of scope, or gated by platform policy —
  the cart will explain.
- **I edited a storefront file but the browser shows old behaviour / a blank console?** The
  server now ships fresh content‑hashes (SRI) with cache‑busting; just **refresh**. If an
  operator runs a long‑lived server, a refresh is enough (no hard‑refresh required).

### E. Troubleshooting quick table
| Symptom | Likely cause | Fix |
|---|---|---|
| Sign‑in fails | Wrong store selected / wrong account scope | Check `?store=`; use the matching console |
| Account locked | Too many failed logins | Wait for the lockout to lapse, or admin reset |
| Console stuck on "Loading…" (older builds) | Stale asset integrity (SRI) blocked scripts | Update to current build (fresh SRI) + refresh |
| Coupon rejected | Expired / scope / policy gate | Verify dates, eligible items, and platform policy |
| Product not visible to customers | Lifecycle not `published` | Set to published in Products |
| Wrong currency/tax shown | Store commerce settings | Adjust in Settings → Commerce / Geo |
| Can't enable a gateway | Provider not available in the country | Enable it in Platform → Provider Registry availability |

### F. Reference — surfaces & key endpoints
- Surfaces: `/` (storefront), `/admin.html` (store), `/platform.html` (platform).
- Health: `GET /healthz`.
- Security scorecard (platform admin): `GET /api/platform/security`.
- Audit chain verification: `GET /api/platform/chain/verify[?tenant=<id>]`,
  store: `GET /api/admin/chain/verify`.

*This is an educational demo platform, unaffiliated with any real retailer. Always change
seeded credentials and enable HTTPS before public use.*
