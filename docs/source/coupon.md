# Coupons — the parts only a person can write

## Flows

**Issue.** A store administrator chooses a registered coupon kind, value, funder, limits and validity, then issues one code or a batch. The code is shown to staff only at issue time and is stored as a protected lookup value.

**Apply and redeem.** A shopper enters a code in the cart. The platform checks tenant scope, dates, state, usage limits, owner limits and policy rules before showing the resulting cart. Checkout records one redemption against the order. A failed payment or refund voids that redemption and restores the available use.

**Failure states.** An unknown, expired, exhausted, revoked or over-limit code is rejected with a reason and does not alter the cart or ledger.

## Manual: shopper

Enter a code in the cart and choose **Apply**. The cart shows the discount or credit before checkout. An invalid code leaves the cart unchanged and explains the reason. A code is counted only when the order is successfully recorded.

## Manual: store_admin

Open **Offers → Coupons**. Issue a single code or batch, set its kind, value, funder and limits, and give the code to its intended audience. Use the redemption table and analytics to reconcile usage. Void an unused or compromised code; refunds automatically claw back redemptions.

## Manual: platform_admin

Manage coupon kinds, statuses and redemption states in Data Studio. Platform policy can disable promo codes globally. Review cross-store redemption totals and funder attribution from the platform offer surfaces.
