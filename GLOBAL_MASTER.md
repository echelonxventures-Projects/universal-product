# The Platform Master — one source for every product and service, configured by selection

Adopted 2026-10-21 by the platform owner (amendment AMD-0025, roadmap steps P27–P30, decisions
DEC-015–DEC-021). This document is the design; each phase below records what it delivered as it lands.

The global platform owns one **platform master**: every product, service, variant and SKU of every
industry, described once. Each platform sees a **projection** of it, filtered by its permissions, its
authorities (jurisdictions) and its own overlays. Nothing is copied into a platform, and no level,
type, code or feature is fixed in code.

## 1. What the master holds

| Concern | How it is held | Owner |
|---|---|---|
| Levels (domain, industry, category, subcategory, family, model, product, service, variant, SKU, any added) | **Kinds**, declared as rows, with placement rules; any depth | Registry |
| Every product and service | **Entities** of those kinds, versioned bi-temporally | Identity |
| Classifications (trade taxonomy, tariff nomenclature, scientific nomenclature, tax classes, any added) | **Hierarchies** over the same entities; one entity sits in many | Relationship / Semantic |
| Codes, scientific names, local codes | **Identifiers** under an **identifier scheme**: format, check rule, issuing authority, places it applies in, validity | Identity |
| What a source model calls columns | **Attributes** on kinds, inherited down a hierarchy, applicable by context (place, authority, kind of offering), multilingual through Expression | Registry / Context |
| Bundles, accessories, replacements, cross-sell, upsell | **Relationship types** as rows, edges between entities | Relationship |
| Media, documents | Content registries | Content |
| Units, packaging levels, conversions | Measure registries | Measure |
| Industry rules (weight pricing, expiry, prescription, assembly, rental terms…) | **Rule packs** on the kind | Rule |
| How it is delivered | **Fulfilment modes**: shipped, collected, downloaded, appointment, chat, audio call, video call, visit, any declared | Commerce |

Stock, serial items, prices and seller terms stay per-platform operational records that point at a
master SKU. A platform's product rows become a **read model** rebuilt from the projection, its overlays
and its sellers' offers; orders keep their snapshot.

Day one ships the **maximum** declared content: every level, kind, identifier scheme, unit, packaging
level and relationship type, the existing catalogue merged in, and data packs for public classifications.

## 2. Permissions

The global platform gives each platform permissions on the master. Each has validity dates.

| Dimension | Values (rows, extendable) |
|---|---|
| Scope | subtrees of any hierarchy; authorities; kinds |
| Object | attribute definition, entity, classification node, relationship, media |
| Action | view, select, overlay a value, add, modify, retire |
| Attribute visibility | which attributes the platform sees (default: those applicable to its authorities) |
| Review | every contribution is reviewed (DEC-015) |

## 3. Overlays and contributions

* An **overlay** is a platform's own value held in its own scope (a local name, a local code). The
  master is untouched; resolution answers the most specific value and says where it came from.
* Every **addition, modification or retirement** a platform makes to the master is a **contribution**.
  It enters the global review queue. Nothing is adopted automatically (DEC-015, DEC-017).
* Once approved, the reviewer places it: **apply** (a new version of the master entity), **new** (a new
  entity or attribute), or **addendum** (an extension attached to the entity, applicable in a declared
  context such as one authority or one platform). Otherwise it is **rejected** with a reason.
* Retirement is always a new version. Nothing is erased.

## 4. Configuring a platform

A platform is created by intent › compose › certify › publish. The intent is a **blueprint**: its steps
are rows naming the question, where the options come from, and what each answer unlocks.

| Step | Options come from |
|---|---|
| Official authority (jurisdiction) | Authority / Geo |
| Working authorities | Authority / Geo |
| Languages | Expression |
| Value units (currencies) | Value |
| Taxes | the chosen authorities' tax regimes |
| Identifier schemes | those valid under the chosen authorities |
| Selling model (single seller, marketplace, hybrid, any declared) | Package |
| What it sells — single, several or mixed, products and services | the master, filtered by permissions |
| Features | discovery |
| Sites | Experience |

Every setting is configurable on its own, with an effective time to the minute; existing platforms are
not migrated in bulk (DEC-018).

**Discovery** derives each capability from the answers and states why:

* **Mandatory** — required by a chosen kind's rule pack or an authority's law; cannot be switched off
  while the cause remains.
* **Recommended** — declared relevant by a kind or fulfilment mode; pre-selected.
* **Added** — switched on by the platform's admin.
* **Requested** — not in the permissions or not built yet; captured during configuration and editable by
  the global admin afterwards (DEC-019).

Platform kinds and blends (PLATFORM_TYPES.md) become **starter packages** that pre-fill answers; they no
longer decide features (DEC-021).

## 5. Services and media sessions

A consultation, a lab test or a class is an entity like a product, with its own fulfilment modes.
Appointments use bookings; chat uses conversations; audio and video use a **media session**, carried by
the platform itself or by any connector plugged in as a provider registration. Communication can itself
be offered to others on paid or any other commercial terms (DEC-020).

## 6. What is replaced

| Today | Becomes | Phase |
|---|---|---|
| `global_products` | master entities | 2 |
| `store_product_config` permissions string | permissions | 3 |
| `importToStore` copying | selection into the projection | 3 |
| per-platform `taxonomy`, `attribute_defs` | hierarchies and attributes in the master, overlays per platform | 2 |
| the product localization table | Expression | 1 |
| fixed vocabularies in `lib/meta.js` (verticals, taxonomy levels, relation types, media kinds, packaging levels, shipping classes, identity fields, variant axes) | master rows | 2 |
| catalogue seeding at registration | selection | 5 |
| platform kinds and blends as gates | starter packages | 5 |
| the fixed setup checklist | blueprint steps | 5 |
| `products` edited directly | read model | 6 |

## 7. Phases

Each gate is the full test suite, the registry gate, the hard-coding audit, the white-label scan and the
browser check, plus the phase's own checks.

| Phase | Work | Own gate |
|---|---|---|
| 0 | This design recorded in the registry | registry compiles; every new term has one owner |
| 1 | Kernel: validation rules on kinds, multilingual attributes, view groupings, scoped kinds | each kernel part tested; localization merged into Expression |
| 2 | The master: kinds, hierarchies, identifier schemes, attributes, maximum starter content; existing catalogue merged | counts reconcile; no duplicate catalogue table |
| 3 | Permissions, projections, overlays | a platform sees exactly its permissions; overlays never leak |
| 4 | Contributions: review, apply / new / addendum / reject | an approved contribution reaches a second platform |
| 5 | Blueprint configuration, discovery, starter packages, certification | every platform type launches by answers alone |
| 6 | Read model for cart, checkout and orders | every engine's tests pass unchanged |
| 7 | Fulfilment modes, built-in media sessions, connectors, communication on commercial terms | a consultation booked, held and paid end to end |
| 8 | Documentation, retired paths removed, registry statuses | no retired table or function referenced |
| 9 | The missing engines (section 9) and the offer types (section 10), each a capability atom with typed params, rows and a state machine where it has a life | every coverage row (section 8) launches with no capability left requested |

## 8. Coverage matrix — every type of platform, by blueprint answers

Every type below is described by what it does, never by any company's name. Each row becomes a
blueprint fixture: a test configures a platform from its answers alone and fails while discovery leaves
any capability **requested**. A new type is a new row. The matrix is the gate for phases 5 and 9.

| Platform type | What it sells | Selling model | Capabilities it relies on (✚ = built in phase 9) |
|---|---|---|---|
| General everything marketplace | every kind, goods and digital | marketplace | buy box, seller health, buyer protection, fulfilment centres, sponsored listings, brand registry, reviews, Q&A, lists, alerts, pickup points, membership, subscribe & save, every offer type |
| National multi-category marketplace | every kind, in many languages | marketplace | the above, cash on delivery, ✚ payment-instrument offers and instalments without cost, ✚ exchange offers, regional languages, ✚ sale events with early access |
| Cross-border bargain marketplace | goods shipped from other authorities | marketplace | ✚ duties and taxes collected at checkout, ✚ parcel customs declarations, ✚ consolidated long-haul shipping, ✚ supplier-direct fulfilment, buyer protection, coins and ✚ gamified rewards |
| Hypermarket and omnichannel chain | groceries, general goods | single seller or hybrid | store stock, pickup, local delivery, substitutions, membership, ✚ warehouse-club membership pricing, ✚ price match |
| B2B wholesale exchange | goods in bulk | marketplace | quotes, tenders, trade assurance, verified suppliers, export documents, letters of credit, segment pricing, minimum quantities, ✚ sample orders |
| Quick commerce (minutes) | groceries, essentials | single seller, dark stores | store stock, delivery slots, batched dispatch, substitutions, ✚ small-order and late-hour fees, ✚ delivery-fee waivers, ✚ serviceable-area checks by minute |
| Fresh and perishables grocery | produce, meat, dairy, bakery | single seller or hybrid | ✚ sell by weight with weight-adjusted billing, ✚ freshness and best-before windows, ✚ cold-chain handling, ✚ cut-and-pack options, delivery slots, substitutions, subscriptions |
| Online pharmacy and health | medicine, diagnostics, wellness, consultations | single seller or marketplace | ✚ prescription upload and pharmacist verification, ✚ schedule rules per authority, ✚ generic alternatives, ✚ refill reminders, ✚ lab tests with home sample collection and reports, consultations by chat, audio and video, ✚ health records with consent, batch and expiry |
| Food and restaurant delivery | meals | marketplace | product options, minutes-fast delivery, batched dispatch, ✚ kitchen hours and prep times, ✚ tips |
| Fashion and lifestyle | apparel, footwear, accessories | marketplace or brand | variants, ✚ size guides and fit, ✚ try-and-buy, returns, rich content |
| Electronics and appliances | devices | marketplace | ✚ exchange offers, ✚ extended warranty and protection plans, ✚ installation booking, instalments |
| Furniture and home | large items | single seller or marketplace | ✚ assembly booking, ✚ large-item delivery, dimensions, rich content |
| Automotive parts | parts and accessories | marketplace | ✚ fitment by vehicle |
| Digital goods | software, media, courses | any | downloads, ✚ licence-key delivery, subscriptions |
| Education | courses, live classes | any | ✚ course progress, bookings, media sessions |
| Subscription boxes | curated goods | single seller | subscriptions, subscribe & save |
| Services and consultancy (astrology, legal, yoga, any) | consultations | marketplace of practitioners | bookings, conversations, media sessions, ✚ per-minute billing from a wallet, ✚ practitioner verification |
| Rentals and stays | assets by date | marketplace | bookings by date range, escrow, buyer protection |
| Travel | journeys, stays, experiences | marketplace | ✚ travel inventory and itineraries, bookings |
| Event ticketing | events | marketplace | ✚ events, seat maps and timed holds |
| Resale and classifieds | used goods, vehicles, property | peer to peer | shopper selling, messages, make-an-offer, escrow, ✚ lead capture for classifieds |
| Auction house | lots | single seller or marketplace | auctions, escrow |
| Group and social buying | deals | single seller | group prices, flash deals |
| Live and social video selling | goods shown live | marketplace or brand | ✚ live sessions with in-stream buying, media sessions |
| Reseller and social commerce | goods resold with a margin | marketplace | ✚ reseller margins and sharing, ✚ affiliate commissions |
| Dropshipping | goods held by suppliers | single seller | ✚ supplier-direct fulfilment |
| Made-to-order and print on demand | customised goods | single seller | product options, ✚ customisation files and proofs |
| Gifts and flowers | gifts on a date | single seller | ✚ delivery on a chosen date with a message, gift wrap |
| Pre-orders and crowdfunding | not yet available | any | ✚ pre-orders and back-orders, ✚ funding goals |
| Payments-led super app | payments, bills, financial products | platform | payment rails, lending, insurance, beside a marketplace |
| Mobility | rides and deliveries | platform | rides, dispatch, dynamic pricing, fleets |
| Operations | business processes | platform | people, procurement, manufacturing, projects |

## 9. The missing engines

Each is built as a capability atom with typed params, its vocabularies as rows, its lives as state
machines, its effect on a bag line as a line term where it has one, and its console and storefront
screens. Grouped by what they share:

* **Pricing and money:** sell by weight with weight-adjusted billing; per-minute billing from a wallet;
  small-order, late-hour and service fees with waivers; tips; duties and taxes at checkout; instalments
  without cost; warehouse-club membership pricing; reseller margins; affiliate commissions.
* **Fulfilment:** supplier-direct fulfilment; consolidated long-haul shipping and parcel customs
  declarations; cold-chain handling and freshness windows; large-item delivery; delivery on a chosen
  date with a message; serviceable areas by minute; kitchen hours and preparation times.
* **Health:** prescriptions with pharmacist verification; schedule rules per authority (a rule pack);
  generic alternatives; refill reminders; lab tests with home sample collection and reports; health
  records with consent; practitioner verification.
* **Catalogue fit:** fitment by vehicle; size guides and fit; customisation files and proofs; licence-key
  delivery; course progress.
* **Inventory of time and place:** travel inventory and itineraries; events, seat maps and timed holds;
  pre-orders, back-orders and funding goals.
* **Services around a sale:** installation and assembly booking; extended warranty and protection plans;
  try-and-buy; sample orders; lead capture for classifieds.
* **Engagement:** live sessions with in-stream buying; gamified rewards (scratch cards, streaks, spins);
  sale events with early access.

## 10. Every type of deal and offer

The offers engine (`lib/offers.js`) already holds offer types, directions, channels, scopes, funders,
coupon kinds and stacking policies as rows. Today's types: percent, fixed, fixed per item, free
shipping, free shipping over a threshold, buy one get one, buy X get Y, X for Y, multi-buy, bundle
price, quantity tiers, flash percent, cashback, spend and get credit, gift-card credit. Coupon kinds:
code, single use, multi use, first order, bulk issued, gift card, bank voucher, referral.

Phase 9 adds, as rows and the conditions they need:

| Offer | What it needs |
|---|---|
| Payment-instrument offers (card, bank, wallet, any instrument) | a condition on the payment instrument at checkout |
| Instalments without cost | the funder absorbs the interest; a payment-plan condition |
| Exchange offers | a trade-in valuation and its credit on the line |
| Free gift with purchase | a gift line added at no cost |
| Mix and match | a group of items counted together |
| Lightning deals | a claimed share of limited stock, a countdown, a wait list |
| Deal of the day and sale events | an event container with early access for members |
| Clearance | an end-of-life price on the lifecycle state |
| Price match and lowest-price guarantee | a claim, its evidence and its review |
| Price-drop protection | a credit when the price falls after purchase |
| Member-only and tier prices | a condition on membership or loyalty tier |
| Loyalty points (earn, burn, tiers, expiry) | a wallet account kind and tier rows |
| Channel-only offers (app, store, any channel) | a condition on the channel |
| Happy hours and time windows | a schedule to the minute |
| Location-based offers | a condition on the place |
| Clipped digital coupons | a coupon the shopper saves before use |
| Two-sided referrals | a reward to each party |
| Gamified rewards (scratch cards, spins, streaks) | a reward draw with odds as rows |
| Delivery-fee waivers and small-order fees | a fee rule with its waiver condition |
| Subscribe & save, group prices, bulk tiers | already built |

Every offer still states who funds it, how it stacks and where it applies. A new kind of deal is a row,
plus a condition when it needs one the engine does not yet know.
