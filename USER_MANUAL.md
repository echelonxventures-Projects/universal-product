# LUXORA Platform — User Manual

This manual is written for every kind of person who touches the platform: **End
Customers**, **Store Administrators**, **Support Staff**, **Marketplace Sellers**, and
the **Platform Owner / Super Administrator**. Each part is a standalone guide — read the
one that matches how you use the system, and refer to the Appendices for shared topics
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
8. [Part E — Platform Owner / Super Administrator guide](#part-e--platform-owner--super-administrator-guide)
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
| **The One Console** | `http://localhost:8787/console.html` | Anyone holding **both** a store and a platform role |

> The **One Console** is the two consoles as one app: a single sign‑in, one nav grouped by
> scope (your store sections, then the platform sections your role grants), and a **⇄
> switch** in the top bar to flip scopes with no second login. If you operate a store *and*
> hold a platform role, start there — it boots against your unified identity and only ever
> shows you what your roles grant.

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
Left rail navigation, grouped:

| Group | Sections | Purpose |
|---|---|---|
| **◈ Overview** | Dashboard · Analytics · Monitor | KPIs, live traffic, what needs attention |
| **Catalogue** | Products · Brands · Global Catalog · SKUs & Inventory · Taxonomy · Attributes · Search & Discovery · Home Content | The catalogue, its variants/stock, the taxonomy & attribute definitions, and the storefront home |
| **Orders & Fulfilment** | Orders · Returns · RFQs (B2B) · Logistics & Fulfilment · Serialized Items · Planning & Replenishment · Suppliers & Procurement | The sell‑and‑ship pipeline |
| **Marketplace & B2B** | Sellers · Contracts (B2B) · Tenders · Marketplace & Ads | Marketplace partners, standing prices, procurement, advertising |
| **Commerce Ops** | Quick‑commerce · Fintech Ops · Marketplace Ops · Trade Ops | Quick‑commerce dispatch, fintech rails, marketplace & trade operations |
| **Payments & Finance** | Payment Gateways · Settlements · Finance & Settlements · Billing | Money in, money out, and your invoices to the platform |
| **Growth & Retention** | Offers & Coupons · Reviews & Q&A · Support Helpdesk · Influencers & Affiliates · Subscriptions & Members · Experiments · Ω∞ GOIP | Promotions, UGC, support, loyalty, recurring revenue, A/B, the value‑exchange engine |
| **AI & Automation** | AI Studio · Webhooks | The free built‑in AI engine + premium models; outbound webhooks |
| **Identity & Access** | SSO & Integrations · Org Structure · Team & Roles | Sign‑in, the org tree, staff & RBAC |
| **Geo & Localization** | Localizations · Shipping & Tracking · Sitemap & SEO | Translations, carriers, discovery |
| **Compliance & Risk** | Compliance & Certs · Risk & Fraud · Audit Trail · Trash & Retention | Certificates, the fraud queue, the hash‑chained log, soft‑delete recovery |
| **Settings & Data** | Settings · Data Studio · Modules | Branding/copy/commerce settings, entity‑driven data management, paid add‑ons |
| **Reference** | User Manual · Architecture | This document and the architecture reference |

> Sections your role does not grant are absent from your nav *and* refused by the server —
> see **Team & Roles** to scope staff. Some sections are vertical facts about your store:
> e.g. **Serialized Items** appears for tracked‑goods industries and **Planning &
> Replenishment** for physical stock, governed by your store's mode and industries.

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

# Part E — Platform Owner / Super Administrator guide

You run the **whole platform**: you provision it once, launch stores, set the rules every
store inherits, sell subscriptions and modules, and keep the fleet healthy, compliant and
paid. All of it happens in the **Platform Console** (`platform.html`) — sign in with the
platform account (`platform@luxora.shop` in the seed).

Platform identity is separate from any store. A platform admin is *not* "the admin of a
store" — you see every store, a store admin sees exactly one.

> **The one principle behind this console.** Everything — every screen, dataset, provider,
> theme, role, capability and offer — is **declared data**, not code. The left rail is
> organized the way the architecture declares (twelve sections, one canonical home per
> capability), and every navigation leaf resolves to a live view. Nothing is a placeholder,
> and nothing is orphaned.

## E1. Sign in & find your way

1. Open **Platform Console** → `http://localhost:8787/platform.html`.
2. Sign in with your platform email + password (`POST /platform/login`). Repeated failures
   trigger the lockout you configure in Provisioning.
3. The top bar shows your email, your **role**, and **Sign out**. On tablet/phone the rail
   is a drawer opened with the ☰ button.

### The twelve sections

The left rail is a tree: **section → group → leaf**. Sections are collapsible; the current
view's section auto-opens.

| # | Section | What lives there |
|---|---|---|
| **01** | Foundation | Identity (auth, persons, orgs, tenants, users, roles, KYC/KYB, identity graph), Geography (countries, jurisdictions, Geo Registry · Taxes), Temporal (calendars, schedules, slots, SLA), Currency (currencies, FX), Localization |
| **02** | Knowledge | Global Products, product types/variants/attributes, Services, Catalog · SKUs, Industry · Categories (taxonomy), Brands · Manufacturers, Provenance, Knowledge Graph |
| **03** | Business | Parties (customers, sellers, partners, distributors…), CRM (leads, opportunities, pipelines), Agreements (contracts, relationships) |
| **04** | Commerce | Merchandising & price lists, Offers & Incentives (**Ω∞ GOIP**), Marketplace & ads, Trade (RFQ, tenders, letters of credit), Transactions (orders, returns, reviews), Recurring (subscriptions, memberships), Billing & Payment (plans, invoices, Billing Ops, settlements, escrow) |
| **05** | Operations | **🧭 Ops Hub** (fleet overview), Supply, Fulfilment, Service Delivery (work orders, dispatch, riders), Support · SLA |
| **06** | Experience | Surfaces (websites, kiosks, portals), Presentation (**Themes**, branding), Channels & notifications, Journeys |
| **07** | Intelligence | AI · Providers & Plans, models, agents, prompt registry, engines (recommendation, forecasting, digital twins…), Trust (fraud, risk), Autonomy, Analytics · A/B |
| **08** | Governance | Policies, Standards/Regulations, Compliance & privacy, Risk & Security, Oversight (**Global Audit**, **Traceability**, risk/compliance/trash) |
| **09** | Platform | **Capabilities**, **Capability Tree**, **Composition Engine**, Extension (Provider Registry, **Module Marketplace**, connectors), Runtime · Infra (environments, feature flags), Evolution (versioning, migration, self-healing) |
| **10** | Observability | **◈ Command** (KPIs), Monitoring, metrics/logs/traces, health, **Dashboards**, **Data Explorer**, **Data Studio**, Entity Definitions |
| **11** | Administration | Tenancy (**🏬 Tenants**), Access (**Platform Admins**, Roles, Users, Licenses), Configuration (**🛡️ Provisioning**, settings, feature flags) |
| **12** | Architecture | Constitution Ω∞ (**UCII Registry**, **UCOS Constitution**, **Foundations**, **Universes**, **Domains**), Canonical Model, Graphs, Reference architectures, **📘 User Manual** |

### How any leaf resolves

A leaf is never a dead link — it renders in exactly one of three ways:

- **A dedicated view** (e.g. *Tenants*, *Billing Ops*, *Ops Hub*) — purpose-built screens.
- **An entity dataset** — a cross-store table over a declared entity (e.g. *Countries*,
  *Contracts*, *Inventory*), served from `/api/platform/data/<key>` using the *same*
  field definitions the Store Console renders. The platform never carries a second copy of
  a schema.
- **A universe dataset** — a corpus-declared domain: its registry record plus its live
  records (see E8).

### The dataset toolbar (used everywhere a dataset renders)

Every dataset — in a Global Operations view, a universe's records, or the Data Explorer —
carries the same toolbar:

- **Filter box** — per-table, matches any visible column or the record id.
- **+ New / Edit / ✕** — create or change records through the platform write endpoints.
  The form is built from the entity's own declaration (fields, types, validation, required
  marks). A dataset your role may not write **hides** the write buttons — and the endpoints
  refuse the same writes, so the toolbar and the API can never disagree.
- **⇪ Import** — paste a **JSON array or CSV** (header row = column names); only declared
  columns are kept and each row is validated exactly like a hand-entered one. Download a
  **sample file** in the dataset's own current columns, and rejections come back with
  their **row numbers and reasons**. Store-scoped datasets make you **name the store**;
  platform-level registries (countries, currencies, universes…) write at scope 0 so every
  store inherits the row.
- **⇩ Export** — one button, every format the server can emit and a choice of scope
  (platform-wide or one store). The format list is fetched from the export endpoint itself,
  so a format registered server-side appears with no page change.

### Role gating

If your platform role does not grant a section, that leaf is hidden **and** the view refuses
to render even if you reach it by URL — the back-end refuses the same call. (Roles are
edited in *Access → Roles*; see E9.)

---

## E2. First-boot setup flow (do this once)

On a fresh install, *Provisioning* shows a banner: **"Initial platform provisioning
pending."** Walk this path top to bottom; afterwards you can launch stores.

1. **🛡️ Provisioning** (*11 Administration → Configuration*) — save the platform policy.
   This screen is the *platform-level* policy: set it once here, never per store.
   - **Credential policy** — minimum password length, require letter + digit, block
     common/breached passwords, and the scrypt parameters (log₂N / r / p) used for new and
     rotated credentials. Existing hashes upgrade transparently on next login.
   - **Abuse control** — auth and API rate limits per IP, lockout threshold and backoff.
   - **Session & transport** — CSRF double-submit, HSTS under TLS, demo hints on login
     screens, CSP inline-style allowance. *HttpOnly + SameSite cookies are structural and
     cannot be disabled.*
   - **New-store defaults** — default plan, whether new stores get a seeded demo catalogue,
     whether gateways start in **sandbox**, and the policy gates stores inherit: currency
     overrides, customer coupons, **global offers**, fiscal-context pickers.
   - **Save platform policy** — the platform is now marked *Provisioned* (status card shows
     when, plus master-key version and whether the pepper is set).
   - The **Layer scorecard** at the bottom shows the live 10-layer security posture.
2. **🌍 Geo Registry · Taxes** (*01 Foundation → Geography*) — confirm the countries stores
   may operate in (each carries its default currency, locale and tax mode), maintain
   **currencies & FX rates** (with history; optionally synced from a JSON feed), and the
   **tax modes** (GST / VAT / sales tax / zero-rate). Jurisdictions, states and cities are
   editable datasets in the same group.
3. **💼 Plans** (*04 Commerce → Billing & Payment*) — create the subscription tiers: name,
   price/month, currency, max products, max orders/month.
4. **🔌 Provider Registry** (*09 Platform → Extension*) — for each payment / shipping /
   notification provider, edit its profile and open **Countries** to set where it is
   available. Checkout only ever offers a gateway that is *both* enabled by the store *and*
   available in its country. Register a **custom provider** with the form (kind, name,
   countries — `*` for all — fees) or a JSON manifest; no code.
5. **🔐 Identity** (*01 Foundation → Identity*) — optionally tune password / MFA / session /
   login settings, add identity providers (SSO), and apply an **identity template** to a
   store to stamp a whole auth configuration onto it at once.

When the banner is gone and the four registries look right, continue to **E3** and launch
your first store.

---

## E3. The tenant lifecycle — launch, manage, suspend, close

Work in **🏬 Tenants** (*11 Administration → Tenancy*). The table shows every store: slug,
jurisdiction, owner, mode, industries, product/order counts, GMV, plan and status.

**Launch a store.** Click **+ New tenant**. It is one form (a tenant is an identity record
the platform provisions): name, slug, country, owner name + email + password, and the
deployment **mode** — `marketplace` (many sellers, all industries), `industry` (one
vertical) or `brand` (single label). Save and the store exists with its own admin account;
hand the credentials to the owner.

**Per-store actions** (row buttons):

| Button | What happens |
|---|---|
| **Open** | Opens the store's storefront in a new tab. |
| **Edit** | Changes the tenant's identity (name, country, owner). Slug is locked after creation. |
| **Manage · Catalog** | **Impersonates** the store — opens its *Store Console* (Part B) with full admin scope, so you can operate a store without its password. Use for support escalations and store setup. |
| **Suspend / Resume** | The kill-switch. A suspended store blocks storefront/API mutations for everyone except platform admins (abuse, non-payment). Resume restores it. |
| **Invoice** | Issues the store's monthly + usage invoice immediately. |
| **✕** | Deletes the store and **all** its data, after a confirm. Destructive — audit trail survives. |

> A store's own Products, SKUs, inventory, orders, suppliers, compliance and settings live
> in **its** Store Console. The platform console reads them *platform-wide* (E6) and writes
> policy, plans and modules *to* them.

---

## E4. Monetize — plans, subscriptions, invoices, billing ops

The money path, in order:

1. **Plans** → define tiers (E2 step 3). Edit price/limits inline.
2. **🔁 Subscriptions** (*04 Commerce → Recurring*) → **+ Assign plan** binds a store to a
   tier; status runs `trialing → active → …`, with started/renews dates. Change a store's
   tier here.
3. **🧾 Invoices** (*04 Commerce → Billing & Payment*) → every invoice across stores with
   period, amount and status. **Collect** on an unpaid invoice picks a gateway
   (stripe / paypal / razorpay / adyen / bank) and records the transaction reference.
4. **💳 Billing Ops** — the receivables workbench:
   - **Aging buckets** — current / 1–30 / 31–60 / 60+ / total receivable.
   - **Run dunning sweep** — escalates overdue invoices by stage.
   - **Generate invoice** — issue a specific store's monthly + usage invoice now.
   - **Record metered usage** — log usage of kind `ai` / `orders` / `storage` / `api` /
     `manual` with description, quantity and unit amount; it lands on the next invoice.
   - **Credit / Refund** — issue a credit note (full or partial), optionally credited to
     the store's customer **wallet** via the offers ledger.
   - Credit notes and the billing event stream are listed on the same screen.

Invoices are computed by one engine: plan line (+ proration) + unbilled usage + any
subscription-channel offer discount + tax — the same tax engine checkout uses.

---

## E5. Extend — modules, providers, global products

### Module Marketplace (*09 Platform → Extension*)

Modules are **products**: buying one creates a paid invoice (`MOD-*`) and applies its
manifest instantly — features, payment rails, catalog ranges, engine capabilities.

- Modules are grouped by category; each card shows price, capability list, and a chip per
  store. **Click a store's chip** to open the purchase modal, fill any config fields, and
  **Purchase & install** (free modules install instantly; paid ones bill and mark
  collected). Click an installed chip to **Uninstall / disable**.
- Every store **auto-purchases the free baselines** at provisioning (identity, geo, cart,
  listing, checkout, SEO, recommendations, billing…).
- Every install / uninstall / configure is written to the **Global Audit** with the acting
  admin and IP. Storefronts update immediately.

### Provider Registry

Payment, shipping and notification providers, each with the **countries availability**
relation, supported methods and fee percentage — plus **custom providers** registered from a
form or a JSON manifest spec (`{method, url, auth, body, statusMap…}`). "Add Meta / Google
/ my CRM" is a row of data, not a deploy.

### Global Products (*02 Knowledge → Products*)

Platform-level **master products**, populated automatically from the constitutional corpus
(one archetype per product universe) and manually by you. Filter by category or universe.
The **Store access** button is the gate: only the stores you name may import that product
into their own catalogue. Edit or delete any master; taxonomy and the brand/manufacturer
registry sit beside it and are inherited by every store.

---

## E6. Oversee — Global Operations (every store at once)

The Store Console *edits* one store; these surfaces *watch* all of them. Two primitives back
every view: a **cross-store dataset table** (the same records each store edits, read
platform-wide) and a **fan-out** that runs each store's own read-only handler once per store
and merges — so business logic lives exactly once, and nothing is re-implemented or missing.

- **🧭 Ops Hub** (*05 Operations → Overview*) — fleet KPIs (GMV, orders, customers,
  products), a tenant comparison table, platform-wide low-stock and recent orders.
- Each domain view lives in its **canonical section** (the "one home" rule):

| View | Section | Covers |
|---|---|---|
| **🧾 Orders · Fulfilment** | 04 Commerce → Transactions | Orders, returns, RFQs, shipments, serialized units, quick-commerce dispatch runs & riders |
| **📦 Catalog · SKUs** | 02 Knowledge | Products, SKUs, inventory, warehouses, replenishment plan |
| **🤝 Sellers · B2B · Trade** | 03 Business → Agreements | Sellers & onboarding/offers/performance, suppliers, contracts, tenders, FBA, smart fulfilment, claims, trade assurance, verification, letters of credit |
| **📣 Ads · Marketplace** | 04 Commerce → Marketplace | Sponsored inventory & GSP bidding, seller KPIs (take rate, commission, ad ROI) |
| **💸 Finance · Payments** | 04 Commerce → Billing & Payment | Disputes, payout runs, per-tenant billing, wallet transfers, gateway turnover, configured providers, settlements, UPI/escrow/splits/mandates/BNPL/KYC |
| **🏷️ Offers · Affiliates** | 04 Commerce → Offers & Incentives | Promotions & coupons, recurring schedules, memberships, retention policy, affiliates & payouts |
| **🎧 Support · SLA** | 05 Operations → Support | Cross-store support queue and SLA health/breaches |
| **🖼️ Content · UGC** | 06 Experience → Presentation | Banners/cards/departments/taxonomy/attributes, reviews, moderation queue |
| **🛡️ Risk · Compliance · Trash** | 08 Governance → Oversight | Fraud queue, per-tenant trash/retention, tax report, compliance & localization |
| **👥 Team · Access · Settings** | 11 Administration → Access | Staff, RBAC roles, SSO per tenant, webhooks & deliveries, tenant settings |
| **📊 Analytics · A/B** | 07 Intelligence → Analytics | Inventory value, funnel, top products, revenue by industry, experiments |
| **🧬 Data Explorer** | 10 Observability → Insight | Any entity in the platform, picked from live metadata, filtered via the toolbar |

Every one of these uses the **shared store filter** (applies to all datasets on the view)
plus the per-table filter / import / export toolbar from E1.

---

## E7. Govern capability — Capabilities, Capability Tree, Composition Engine

### Capabilities (*09 Platform*)

The platform's configurable catalog, switched and tuned **per store**. Pick the store,
grouped by domain (Marketplace, Quick-commerce, Fintech, B2B trust & trade…):

- **Toggle** any capability **ON / off for store** — its "platform on/off" state is the
  default stores inherit.
- **⚙ params** — configure each declared parameter (boolean / number / JSON / text) with
  its unit and live effective value. An **edited** badge marks overrides.
- **Presets** — save a whole capability set as a named preset and **Apply** it to any store
  in one click (or delete it).

### Capability Tree (*09 Platform*)

The map: every capability and its sub-capabilities grouped by domain, showing which compose
— the "one canonical home" view of what the platform is made of.

### 🧬 Composition Engine (*09 Platform → Composition*)

The central claim made mechanical: **Application = Capability Composition**. Compose any
declared capability and the platform **materializes its full application surface from the
declaration** — data model, REST API, lifecycle workflow, console UI, dashboard and
security policy. The path contains **no per-capability code**.

1. The candidates table lists **Universes**, **Capabilities** and **Datasets** with where
   each is declared. Filter by name, key or source.
2. Click **Compose** on a declared capability → its surface is materialized; the row flips
   to a **composed** badge.
3. **Recompose** re-derives from the current declaration; **Manifest** shows every artifact
   the composition produced (model, endpoint, field count, records).
4. The **composition ledger** is append-only — every composition and recomposition with its
   provenance, so the platform's evolution is itself traceable.

---

## E8. The constitution surfaces (*12 Architecture*)

These screens make the declared corpus executable and inspectable.

- **🌀 UCII Ω∞ Registry** — the compiled, sealed corpus itself: concepts, documents and
  their declarations, the single source of truth everything else resolves from.
- **♾️ UCOS Ω∞ Constitution** — the constitutional model rendered as data: articles,
  stages of the value-exchange chain, the registries and the fabrics.
- **🏛️ Foundations** — the operational registry. **Verify invariants** checks
  *identities unique, dependencies resolve, acyclic, no orphans*; the **Audit ledger** is
  the append-only record of foundation events. Lifecycle states and the five graphs are
  summarized on the same screen.
- **🧬 Universes** — each universe the corpus declares is instantiated as a live,
  data-defined entity. Watch the coverage %, then **↻ Re-instantiate**. Pick the
  **target store** explicitly (activation publishes into *one* store's catalogue — never a
  silent default), then **⚡ Activate all → storefront** or per-universe **→ Storefront**;
  **Withdraw** removes a universe's offering. **Records** jumps to its dataset.
- **🔀 Domains** — every universe's records advance through the lifecycle the constitution
  declares (states + rules + the transition grammar), as a state board. **Advance** a
  record when its rule holds; blocked transitions show ⛔ and the reason. Every move is
  append-audited. Zero per-domain code — one machine serves every universe.
- **🧭 Traceability** (*08 Governance → Oversight*) — the matrix of every corpus document
  → concepts → foundations → universes → records → API. **Trace a key** to see each runtime
  layer it resolves to; absent layers are reported, not hidden.

---

## E9. Identity & access control

### Identity settings (*01 Foundation → Identity*)

Password policy (length, expiry, required classes), MFA (enabled / required for admins),
session (timeout, max concurrent, remember-me), login (max attempts, lockout, guest
checkout), plus the **identity providers** list (add / edit / delete — the vocabulary of
provider *types* is itself registry data). **Apply a global template** to a store to stamp a
whole auth configuration onto it; manage templates under **Identity Templates**.

### Platform Admins (*11 Administration → Access*)

The accounts that can sign in to *this* console, scoped by role. Add an admin (name, email,
password, role), change a role **inline** (effective on their next sign-in), edit or
delete. You cannot delete your own account, and the platform always keeps at least one
admin.

### Roles (*11 Administration → Access*)

Two role sets, both data in registries:

- **Platform roles** govern this console's operators.
- **Store staff roles** govern every store's team — one platform-wide list every store
  applies.

The **grants editor** gives one control per section the scope knows. A grant is one of
**inherit** (absent — falls back to the wildcard), **off** (explicit deny, beats the
wildcard), **read**, or **write**. The **wildcard** row sets the default every inherited
section resolves to. With ~200 sections possible, use the filter plus the bulk
*filtered → read / write / inherit* buttons to scope just the ones you're editing.

### Users

Every account the platform holds across every store, read through the generic dataset
reader — search, export, and (per your role) edit or remove.

---

## E10. Governance — policies, audit, risk

- **🔒 Policies** (*08 Governance → Policy*) — runtime-configurable platform behaviour
  (identity, SEO, reviews, search, checkout, features, provisioning…). Add or edit a
  category with a JSON document; changes take effect **immediately, no restart**.
- **📜 Global Audit** (*08 Governance → Oversight*) — the cross-store, **hash-chained**
  trail: when, which store, which actor, action, entity and detail. Filter to investigate.
  Verify any scope's chain (see E13 endpoints) to detect tampering.
- **🛡️ Risk · Compliance · Trash** — the fraud queue, per-store soft-delete/retention
  counts, and the tax exposure report, platform-wide. Deletions are soft (tombstones) with
  a retention window; purging past retention is the erasure path.

---

## E11. Look & feel — Themes (*06 Experience → Presentation*)

Every theme is a row in a registry — no dep.

- Browse **presets**; **Assign…** one at any scope. Assignments cascade
  **product → department → tenant → platform**, most specific wins; a store's own settings
  remain the default unless a preset is assigned. **Clear** an override to drop back.
- The **generative studio**: dial a **hue** (0–359°), toggle dark mode, **⚡ Preview** — it
  live-dresses the console so you see the skin in situ — then name it and **★ Save as
  preset**. It becomes a reusable theme like any other.

---

## E12. Runtime — environments & feature flags (*09 Platform → Runtime*)

Every backend concern (cache, queue, storage, rate-limit, session, outbound, db) is a
**config choice**.

- Define unlimited **named environments** — bundles of driver choices + secrets + feature
  flags. **Activate** one to swap the whole topology (or boot with `LX_ENV=prod`); edit or
  delete environments inline. Unconfigured or unreachable drivers fall back in-process, so
  nothing hangs.
- **Feature flags** — per flag a default on/off and a **rollout %**; create, edit, delete.
- **🧠 AI · Providers & Plans** (*07 Intelligence*) — decide per capability whether the
  **free built-in engine** or a **premium** model runs, register providers/keys, and set
  the plans that unlock premium. Store usage meters to the AI ledger and appears on
  invoices.

---

## E13. Watch the fleet — observability

- **◈ Command** (*10 Observability → Telemetry*) — the platform dashboard: MRR, collected,
  outstanding, GMV (+ gateway fees), store count, live requests/errors/latency; a
  billing-by-month chart; a per-store table (products, GMV, plan) linking to each
  storefront; system uptime, memory, DB size, runtime.
- **📈 Monitoring** — live traffic across all tenants (last 30 min), top endpoints by
  calls/errors/latency, and per-store status.
- **📊 Dashboards**, **🧬 Data Explorer**, **🛠️ Data Studio**, **📐 Entity Definitions** —
  dashboards over live data; any dataset through the toolbar; direct entity-driven
  management and authoring of new entities (CRUD + validation + audit + forms appear
  automatically); and the declaration list behind all of it.
- **Security scorecard** — `GET /api/platform/security` returns the live 10-layer posture
  (transport, session/CSRF, credentials, password policy, at-rest encryption, keyring,
  audit chain, rate/lockout, supply-chain SRI, isolation) and whether the audit chain is
  intact. The same layers are summarized on the Provisioning screen.

---

## E14. Ω∞ GOIP — the Global Offer Infrastructure Platform

*04 Commerce → Offers & Incentives → Ω∞ GOIP · Value Exchange*

This is **not** a coupon editor: it is the control plane for *every* incentive, offer,
promotion, benefit, entitlement, subsidy, commission, loyalty construct or future
value-exchange model the platform can express — across any industry, organization, country,
planet, economy, calendar, governance model or reality, without redesign.

**What a value exchange is.** One record that walks one chain: *value exchange → context →
conditions → eligibility → benefit → execution → settlement → audit*. A "10% coupon", a bank
cashback, a government subsidy, a creator commission, a membership upgrade and a
Mars-colony credit are the same record with different registry values.

**The nine surfaces**

| Tab | What you do there |
|---|---|
| **Ω Constitution** | The 8-stage chain, the zero-gap scorecard (capabilities bound, domains with distinct owners, benefits with math), and the experience/access fabrics with what each is bound to |
| **⚡ Capabilities** | All 22 capabilities with stage, engine, the store each writes and the meter each bills — plus a live console that invokes any of them with a JSON body |
| **🌐 67 Domains** | Every constitutional domain, its owning store, the exact discriminator that isolates its rows (this is what makes overlap impossible), and live record counts |
| **💠 Value Exchanges** | Publish a *global* exchange every store inherits — choosing benefit, domain, funder, economic unit, reality, calendar, place prefix, distribution channels, declared conditions, multi-party funding split and governance state — then publish / suspend / version it |
| **📚 Registries** | Calendars, chronologies, temporal units, spatial systems, coordinate systems, hierarchy paths, economic units, reality models and every fabric — all editable in Data Studio → Registries |
| **🏦 Funding · Settlement** | Allocate budgets per funder/unit/domain, watch burn, run the settlement, approve, pay out with a reference, reconcile against a bank statement |
| **🔗 Attribution · Graph** | Touchpoints captured from any surface; replay a subject's path through any attribution model to split revenue and commission; the 21-node / 14-relationship incentive graph |
| **🧠 Intelligence** | 15 readings over live data — deal, offer, price, audience, merchant, provider, partner, fraud, optimization, forecast, recommendation, AI offer/incentive generation, autonomous campaign and optimization |
| **💳 Commercialization** | 11 deployment models, 12 billing models with their live metered quantities and accrued charges, and which stores have purchased GOIP |

**Governing an exchange.** Lifecycle is a state machine: `draft → submitted → approved →
certified → published → suspended → retired`. Illegal jumps are refused. *Version* forks a
draft that inherits the public code only when it is published — at which point it supersedes
and retires the version it replaced, so a code is never live on two records at once.

**Settlement is exactly-once.** Every redeemed-but-unsettled redemption is attributed to its
funding parties (including multi-party splits) once and stamped; re-running the settlement
settles nothing twice. Refunding an order recovers the accrual and revokes entitlements
granted by it.

**Selling it.** GOIP is a marketplace module (**Value Exchange** category). Every capability
call meters into the billing engine and appears on the store's next invoice; stores without
the module are metered at zero. Agent and MCP callers buy `goip-agent` and speak the same
22 capabilities.

**Test it in five minutes** (everything below ships seeded on first boot):

1. **Platform → Ω∞ GOIP → Value Exchanges.** Seven global exchanges are already published.
   Note their contexts: one is priced in Mars Credits and scoped to Olympus Territory, one
   is restricted to Bihar, one is funded 70/30 by a bank and a brand.
2. **Store console → Ω∞ GOIP → Decision tester.** Enter amount `200`, code `GOIPSOL`, leave
   the place empty → **0**, with the reasons printed: wrong calendar, wrong spatial system,
   wrong economic unit. Set place to `mars.olympus.sector-7` and unit to `MARS_CREDIT` →
   **30**, and the context line shows the Darian calendar, which nobody typed: the place
   resolved its own temporal authority.
3. Try `GOIPGOV` with place `earth.in.bihar.patna` (→ 25) and then `earth.us` (→ 0,
   jurisdiction).
4. Try `GOIPWELCOME` with subject `t1:u:999` (no orders → 10%) and then with a subject that
   has orders (→ refused by the declared condition, not by a hardcoded flag).
5. **Storefront → The Edit (`/deals.html`).** The offer strip lists what is available on the
   in-app channel; clicking a code tracks a touchpoint and applies it to the cart. Check out
   to see the benefit land, then look at **Store console → Ω∞ GOIP → Subject lookup** for the
   wallet, the POINT balance and any entitlement granted.
6. **Platform → Ω∞ GOIP → Funding · Settlement.** Press **Run settlement**: redemptions
   attribute to their funding parties (the bank and the brand split 70/30; a points
   liability settles in POINT, not cash). **Pay** one, then **reconcile** it. Press **Run
   settlement** again — nothing double-counts.
7. **Platform → Ω∞ GOIP → Attribution** (replay a subject's path through any model),
   **Intelligence** (15 live readings), and **Commercialization** (the meters your
   capability calls just billed).
8. **Capabilities tab → capability console.** Invoke any of the 22 verbs with a JSON body
   and read the raw response — this is exactly what an SDK, an agent or a partner system
   sees.

**For developers.** One entry point — `POST /api/goip/<capability>` — plus read surfaces
`GET /api/goip` (the machine-readable constitution), `/api/goip/exchanges`, `/api/goip/context`,
`/api/goip/treasury`, `/api/goip/settlements`, `/api/goip/entitlements`, `/api/goip/touchpoints`,
`/api/goip/registry/<name>`, `/api/goip/intelligence/<key>`, `/api/goip/feed/<channel>` and
`/api/goip/widget` (embeddable). Access follows each capability's scope: `any` (a shopper
session), `tenant` (store admin) or `platform` (this console).

---

## E15. Enterprise ops — all OFF until configured

These integrations ship inert; nothing activates until you write its config, and all of it
is tenant-isolated and audited.

- **Database cutover** — set driver **postgres** + connection string → *Test / Dry-run /
  Apply / Revert* runs the async dual-engine + SQLite→Postgres migration planner against
  your live PG (SQLite until then). See *Runtime · Infra*.
- **SSO/SAML + SCIM** — per-store SSO connection (okta/entra/google/generic + allowed email
  domains) and a bearer-token SCIM endpoint so HR/IdP syncs staff accounts (mapped to RBAC
  roles). Configure under each store's console; the platform reads the result in
  *Team · Access · Settings*.
- **Regions / Edge** — manage the region list + CDN base URL; asset URLs rebase to the CDN
  when set.
- **Observability** — `GET /metrics` (Prometheus), `/healthz`, structured JSON logs
  (`LX_LOG=1`), trace ids on every request (`X-Request-Id` / `X-Trace-Id`).
- **Feeds / inventory / tax** — Shopping product feeds, warehouse stock transfers, tax
  remittance report.

### Idempotency & webhooks (built in, always on)

Send an **`Idempotency-Key`** on any POST/PUT/DELETE: the first call executes and stores its
response (24h TTL); the same key + payload replays it, the same key with a *different*
payload is rejected with 422 — so a retried "place order" or "capture payment" can never
double-run. Outbound webhooks are HMAC-signed, delivered through a retrying ledger
(`order.created/paid/refunded`, `ai.usage`, …), with the event catalog itself registry data.

---

## E16. Owner quick-reference — the flows at a glance

| If you want to… | Go to | Action |
|---|---|---|
| Configure the platform for the first time | 11 → 🛡️ Provisioning | Save the policy (banner disappears) |
| Set the countries / currencies / taxes | 01 → 🌍 Geo Registry · Taxes | Edit countries, FX, tax modes |
| Create subscription tiers | 04 → 💼 Plans | + New plan |
| Launch a store | 11 → 🏬 Tenants | + New tenant (one form) |
| Operate a store without its password | 11 → 🏬 Tenants | Manage · Catalog (impersonate) |
| Suspend an abusive / non-paying store | 11 → 🏬 Tenants | Suspend |
| Bind a store to a plan | 04 → 🔁 Subscriptions | + Assign plan |
| Collect money / chase arrears | 04 → 🧾 Invoices · 💳 Billing Ops | Collect · Run dunning sweep |
| Sell an add-on to a store | 09 → 🧩 Module Marketplace | Click the store's chip |
| Add a payment method for a country | 09 → 🔌 Provider Registry | Edit → Countries |
| Allow a store to list a master product | 02 → 🌐 Global Products | Store access |
| See every store's orders / stock / disputes | 05 → 🧭 Ops Hub (+ E6 views) | Use the store filter + toolbar |
| Turn a feature on for one store | 09 → ⚙️ Capabilities | Pick store → toggle / params / preset |
| Materialize a capability's full surface | 09 → 🧬 Composition Engine | Compose |
| Publish the corpus into a store | 12 → 🧬 Universes | Pick target store → Activate |
| Check the corpus is intact | 12 → 🏛️ Foundations | Verify invariants |
| Advance a universe record's state | 12 → 🔀 Domains | Advance (rule-gated) |
| Add a console operator | 11 → 🛡️ Platform Admins | Create admin with a role |
| Scope what a role may touch | 11 → 🎭 Roles | Grants editor (wildcard + per section) |
| Change platform behaviour without a restart | 08 → 🔒 Policies | Edit the category's JSON |
| Prove who did what, across stores | 08 → 📜 Global Audit | Filter + verify the chain |
| Re-skin a store or department | 06 → 🎨 Themes | Assign, or dial a hue and save a preset |
| Swap infra topology | 09 → 🧩 Runtime · Infra | Activate a named environment |
| Check the platform's health | 10 → ◈ Command · 📈 Monitoring | — |
| Change a platform policy gate | 11 → 🛡️ Provisioning | New-store defaults |

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
- Surfaces: `/` (storefront), `/admin.html` (store), `/platform.html` (platform),
  `/console.html` (both scopes, one sign‑in).
- Health: `GET /healthz`.
- Security scorecard (platform admin): `GET /api/platform/security`.
- Audit chain verification: `GET /api/platform/chain/verify[?tenant=<id>]`,
  store: `GET /api/admin/chain/verify`.

*This is an educational demo platform, unaffiliated with any real retailer. Always change
seeded credentials and enable HTTPS before public use.*
