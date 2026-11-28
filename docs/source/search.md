# Search and discovery — the parts only a person can write

## Flows

**Learning what goes together.** When a shopper opens a product, it is paired with the other products
they opened in the past day. Opening the same product again does not count twice. When an order is
placed, its products are paired with each other. Every night the purchase pairs are rebuilt from the
last year of orders. That rebuild also pairs products a customer bought in orders up to 30 days apart,
at half weight. Every pair fades, halving every 60 days, so what sells together this season counts more
than last year. A pair names products only, never a person.

**Scoring.** A pair is used once it has been seen enough times: twice for views, once for purchases.
Each pair is measured against how popular each of its products is alone, so a best-seller that turns
up in every order does not crowd out a product that is truly bought with this one.

**The shelves.**
- **A product page** shows:
  - what is bought together, as a set to add in one click (unless the store set a bundle of its own);
  - what was viewed with it;
  - what is like it, by category, brand and price. A new product has suggestions from its first day.
- **The home page** shows, in order:
  - picks for the shopper, each with its reason: "Because you viewed…", "Because you bought…" or
    "Goes with … in your cart". The picks are spread over several departments, and topped up with
    what is popular in the departments the shopper looks at;
  - what they viewed recently;
  - what is popular now.
- **The cart** shows what goes with what is in it.

Out-of-stock and blocked products are never shown.

**Whose history is used.**
- **Always:** what the shopper views in this visit and has in the cart. That is what they are looking
  at now.
- **Past orders of a signed-in shopper:** only with their grant for analytics and personalisation. A
  store can instead use them unless the shopper withdraws it.
- **Asking:** the home page asks a signed-in shopper whether their orders may shape the picks. The
  privacy page turns it off again.

**Measuring.** Each shelf counts:
- **shown:** how many products it showed;
- **clicked:** a product opened from it;
- **bought:** that product ordered within 7 days of the click, with the revenue.

A guest who signs in keeps the clicks of their visit. Clicks older than the window are forgotten.

## Manual: store_admin

Open **Storefront → 🎯 Recommendations**. Your role needs the recommendations section; the Catalog and
Growth roles have it.

- **What has been learnt** shows the pairs bought and viewed together, and how many products have
  partners. It also lists the last rebuilds. **Rebuild from orders now** rebuilds without waiting for
  the night.
- **Shelves** lists each shelf's last 30 days: shown, clicked, click rate, bought, the share of clicks
  that became orders, and revenue. Untick a shelf to switch it off.
- **Settings**:
  - whether past orders shape picks only with the shopper's grant (the default) or unless they
    withdraw it;
  - how fast a signal fades;
  - the most products from one department;
  - the products on a shelf;
  - how many days a click counts toward an order;
  - products never to recommend, and products to lift, as product ids.
- **Preview**: enter a customer's email to see their picks with the reason and score for each, or a
  product id to see that page's shelves.

## Manual: guest

Product pages show what is often bought together, what others viewed with it and what is like it.
The home page suggests products from what you are looking at in this visit.

## Manual: shopper

Your picks on the home page say why each was chosen. If you are signed in, the home page asks whether
your past orders may shape them. **Yes, use my orders** turns that on. You can turn it off on the
privacy page under **Analytics & personalization**. What you view in a visit always shapes the picks.
