# Platform Types — launching any kind of commerce platform by configuration

LUXORA is one master platform configured into any type of commerce platform. Nothing in this
guide needs code: a platform type is a **kind** (what one is called, what registration sets up)
that starts from a **blend** (a named set of capability atoms), and every atom stays one switch
away afterwards. A kind is a starting point, never a limit.

The platform is **white-label**: it names no other company's platform anywhere — code, docs,
seed data or screens. Types are described by what they do. `scripts/white-label.js` enforces
this on every test run.

## 1. The coverage matrix

| Platform type | Kind (`deployModes`) | Starting blend | What it relies on |
|---|---|---|---|
| General multi-seller marketplace | `marketplace` | `blend_marketplace` / `blend_everything_store` | buy-box, seller health, buyer protection, fulfilment centres, sponsored products, brand registry, rich content, reviews, Q&A, deals, coupons, gift cards, lists, alerts, pickup points, memberships, subscribe & save |
| Single-industry marketplace | `industry` | any | the marketplace atoms over one industry's catalogue |
| D2C brand store | `brand` | any | one seller, the storefront atoms |
| Quick commerce (minutes-fast) | `quick_commerce` | `blend_quick_commerce` | dark stores and store stock, delivery slots, batched dispatch, substitutions |
| Omnichannel retail chain | `omnichannel_retail` | `blend_omnichannel_retail` | store stock, pickup at a shop or locker, local delivery, substitutions, memberships, options |
| B2B wholesale marketplace | `b2b_wholesale` | `blend_b2b_trade` | quotes (RFQ), tenders, trade assurance, verified and gold suppliers, export documents, letters of credit, segment pricing, minimum order quantities |
| Payments-led super app | `super_app` | `blend_super_app` | UPI and QR payments, payment links, bill payments, recharges, P2P transfers, pay later, lending, insurance, gift vouchers, KYC — beside a marketplace and fast delivery |
| Resale & classifieds | `resale` | `blend_resale` | shopper selling, buyer–seller messages, make-an-offer, auctions, escrow, buyer protection |
| Auction house | `auction_house` | `blend_auction_house` | timed auctions with automatic bidding, reserve, buy-it-now, messages, escrow |
| Services & appointments | `services` | `blend_services` | bookings in time slots, options, messages, memberships |
| Rentals & stays | `rentals` | `blend_rentals` | bookings by date range, escrow, buyer protection, messages |
| Food & restaurant delivery | `food_delivery` | `blend_food_delivery` | product options (modifiers, add-ons), minutes-fast delivery, batched dispatch |
| Social & group buying | `group_buying` | `blend_group_buying` | group prices, flash deals with countdowns, coupons, shareable lists |
| Payments and financial services | `fintech` | `blend_fintech` | the payment rails without a storefront |
| Ride hailing, taxi and delivery fleets | `mobility` | `blend_mobility` | rides, dispatch, dynamic pricing, fleets |
| ERP and business operations | `operations` | `blend_operations` | people and payroll, procurement, manufacturing, projects |
| Digital goods, subscriptions | any commerce kind | any | product types `download` / `subscribe`, memberships, subscribe & save |

A new type is a new `deployModes` row (*Platform → Administration → Platforms & Kinds*) naming a
blend — or a new blend (*Platform → Capabilities → Presets*). Neither needs code.

## 2. Launching one

1. *Platform console → Administration → Platforms & Kinds* — pick the kind, name the platform,
   its country and its owner. Registration provisions what the kind declares (payment gateways
   and carriers from its country, a warehouse, a shopfront) and switches on the kind's blend.
2. *Store console → ⚙️ Capabilities* — switch any further atom on or off and tune its params.
   A console section appears only when an atom that owns it is on.
3. *Data Studio* — edit the vocabularies (kinds of list, alert, option group, booking resource,
   booking mode, conversation subject, substitution policy, report kind, content module…). Each
   row declares what it does; the engines follow it on the next request.

## 3. The engines a type relies on

Each is a capability atom with typed params, its records' lives are state machines (asked by
what a state *means*, never by its name), and its vocabularies are registry rows.

| Atom | Engine | Console section | Storefront |
|---|---|---|---|
| `product_options` | `lib/options.js` | 🧩 Product Options | option pickers on the product page |
| `bookings` | `lib/bookings.js` | 📅 Bookings | time / date pickers on bookable products |
| `price_negotiation` | `lib/negotiation.js` | 🤝 Offers | 🤝 Make an offer; offers under *Your activity* |
| `auctions` | `lib/auctions.js` | 🔨 Auctions | auction panel; bids under *Your activity* |
| `peer_listings` | `lib/listings.js` | 🏷️ Shopper Listings | *Sell an item* (`sell.html`) |
| `conversations` | `lib/conversations.js` | 💬 Messages | 💬 Ask the seller; *Messages* (`messages.html`) |
| `group_buying` | `lib/groupbuy.js` | 👥 Group Buying | group panel on the product page |
| `substitutions` | `lib/substitutions.js` | 🔄 Substitutions | a choice per bag line; proposals under *Your activity* |
| `wish_lists`, `product_alerts`, `pickup_points`, `rich_content`, `brand_registry`, `sponsored_ads` | see the README | | |

**Line terms.** Several engines change what one bag line costs or carries — chosen options, an
agreed price, a won auction, a booking, a group place, a substitution choice. They register a
*line term* with `lib/lineterms.js`: the cart prices each line through its terms, refuses a line
whose terms no longer hold, keeps the terms on the order line and lets each engine act when the
order is placed. The same product can be in the bag more than once with different terms.

## 4. Connectors are data

Payment, shipping, messaging, tax, marketing and AI connectors are seed rows
(`lib/seed/providers.json`, `lib/seed/ai.json`) written to the Provider Registry once and edited
there afterwards; a connector's protocol is a declarative spec (request, signature scheme, event
mapping), so adding one is a registration, not code. What each seeded deployment starts with is
`FIXTURE_CONNECTORS`; what a new platform starts with is the platform policy's provisioning
(the country's own connectors first).

## 5. Checks

`npm test` runs `test/platform-types.js` (every engine end to end through the cart and checkout,
and a platform launched from each new kind), `test/shopper.js`, `test/white-label.js` and the
registry and hard-coding gates; `npm run check:browser` drives the pages and console screens in
real Chrome (`test/shopper-ui.js`).
