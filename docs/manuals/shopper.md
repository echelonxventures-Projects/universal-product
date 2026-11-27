# Manual — Shopper

Everything a shopper does on the platform, domain by domain. Generated from each domain's documentation.

## Identity

Who someone is: accounts, sign-in by every method (password, one-time code, magic link, passkey, single sign-on), sessions, provisioning from directories, and platform administrators' own accounts.

_Not yet written._

More: [Identity](../domains/identity.md)

## Customers

The people and organisations a store sells to: their profiles and addresses, segments they belong to, and leads not yet customers.

_Not yet written._

More: [Customers](../domains/customers.md)

## Catalogue

Everything a store sells, described once: products and their variants and SKUs, brands, the category tree, attributes, the platform master every product is described on, the global catalogue and contributions back to it.

_Not yet written._

More: [Catalogue](../domains/catalog.md)

## Product options

Choices on one product instead of a product per combination: option groups (sizes, toppings, engravings) with their values and price changes, attached to any product.

_Not yet written._

More: [Product options](../domains/product_options.md)

## Offers

The offers themselves: every price a buyer pays less or gets more, and every rule about how they apply — the offer record, its types, its scopes, its channels, its funders, its stacking policy and its governance. A coupon, a voucher, a gift card, a cashback, a reward and a group buy are their own domains; this one decides which of them applies.

_Not yet written._

More: [Offers](../domains/offer.md)

## Group buying

A lower price when enough shoppers join before a deadline: staff open a campaign on a product with a group price, how many members it needs and how many it may take; a shopper joins by buying at the group price. A campaign that reaches its members succeeds and its orders go ahead; one that falls short fails and every member's order is cancelled and refunded.

Open a product with a group offer, review the required member count and deadline, then join through checkout. Track joined groups under your activity. A successful group proceeds normally; a failed or cancelled group returns the paid amount to your wallet.

More: [Group buying](../domains/groupbuy.md)

## Coupons

The codes a shopper types at the cart: a code that carries a value, issued by staff or in bulk, validated against its kind and its limits, redeemed into the redemption ledger, and voided when the order is refunded. The kinds — a single-use code, a bulk lot, a referral code — are rows.

Enter a code in the cart and choose **Apply**. The cart shows the discount or credit before checkout. An invalid code leaves the cart unchanged and explains the reason. A code is counted only when the order is successfully recorded.

More: [Coupons](../domains/coupon.md)

## Vouchers

An instrument of value that is not the shop's own discount and not a gift card: a bank voucher, a benefits note, an organisation's credit. Who stands behind it, whether it may be spent in part and how long it lives are its kind's rows; the code it travels on belongs to the Coupon domain.

Enter an issuer-provided voucher code in the cart. Confirm the issuer, value and resulting discount before placing the order. Contact the issuer if the code is expired or outside its permitted store or audience.

More: [Vouchers](../domains/voucher.md)

## Gift cards

A card bought as an item or issued by staff: a code with a value, sent to its recipient with a message, redeemable into the recipient's gift balance, checked for its balance, voided with a reason and expired after its validity. A card is a node on the kernel; its code is sealed and found by a blind index.

Open **Gift Cards** to buy or check a card. Sign in before redeeming. Enter the code once; after successful redemption the amount appears in your gift balance and is automatically considered at checkout where the store permits wallet payment.

More: [Gift cards](../domains/giftcard.md)

## Cart and checkout

From the bag to a placed order: bag lines and their terms, service fees and tips, buy now, try and buy, the payment step and the order it writes.

_Not yet written._

More: [Cart and checkout](../domains/cart.md)

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

1. Sign in and open **Your Orders**; your wallets are under **Your activity → 👛 Your wallets**.
2. Each wallet shows its name, what kind of wallet it is, what is available now and anything held
   for an order in progress.
3. **Rename** gives a wallet any name you like; earlier names are kept in its history.
4. **Open a …** opens another wallet of that kind (a purpose wallet for a trip, for example) — give
   it a name.
5. **Move value** sends an amount to another of your wallets in the same currency. If you do not
   have enough available, nothing moves and you are told why.
6. Your balance is used at checkout automatically where the store allows it; the amount is held
   while you pay and taken once the order is placed.

More: [Wallets](../domains/wallet.md)

## Campaigns

Email, SMS and in-app messages to a store's customers, a segment, its CRM contacts or a company's people — only to those with a live marketing consent, checked when the list is built and again before each message — with an unsubscribe link in every one, sent once per person even by several servers, scheduled or sent now, and counted.

Every marketing message from a store has a link at the end. Opening it stops that store's marketing
messages to you; you can turn them back on in your account's privacy settings.

More: [Campaigns](../domains/campaigns.md)

## Financial services

Financial products sold to buyers: bill payments, recharges, insurance, and credit — pay later and loans with their instalments.

_Not yet written._

More: [Financial services](../domains/financial_services.md)

## Subscriptions and memberships

Buying again on a schedule and belonging to a programme: subscribe-and-save schedules and their cycles, and membership tiers with their perks.

_Not yet written._

More: [Subscriptions and memberships](../domains/subscriptions.md)

## Shipping and delivery

Getting goods to the buyer: carriers and rates, shipments and tracking, pickup points and lockers, and fast local delivery from dark stores with slots, riders and dispatch runs.

_Not yet written._

More: [Shipping and delivery](../domains/shipping.md)

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

## Marketplace

Many sellers in one store: seller onboarding and health, offers competing for the buy box, fulfilment by the store, buyer protection claims, brand protection, and shoppers selling their own items.

_Not yet written._

More: [Marketplace](../domains/marketplace.md)

## Negotiation and auctions

Prices agreed rather than listed: offers and counter-offers between a buyer and a seller, and timed auctions with proxy bidding.

_Not yet written._

More: [Negotiation and auctions](../domains/price_discovery.md)

## Lists, alerts and history

What a shopper keeps and watches: wish lists and gift registries, saved and compared items, price and stock alerts, and what they viewed.

_Not yet written._

More: [Lists, alerts and history](../domains/engagement.md)

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

## Compliance and privacy

Meeting obligations: controls and their evidence, certifications, know-your-customer checks, consent, and privacy requests to see or erase data.

_Not yet written._

More: [Compliance and privacy](../domains/compliance.md)

