# Gift cards — the parts only a person can write

## Flows

**Issue or purchase.** A shopper buys a configured gift-card item, or staff issue a card for a recipient. The code is generated once, protected at rest and delivered only through the configured notification path.

**Check and redeem.** Anyone may check whether a code is redeemable and its remaining value without learning its holder. The recipient signs in and redeems it. The platform atomically changes the card state and credits the recipient's gift wallet; the balance is then available at checkout.

**Void and expiry.** Staff may void a redeemable card with a reason. A card past its configured validity enters the expired state. Redeemed, expired and voided cards cannot be redeemed again.

## Manual: shopper

Open **Gift Cards** to buy or check a card. Sign in before redeeming. Enter the code once; after successful redemption the amount appears in your gift balance and is automatically considered at checkout where the store permits wallet payment.

## Manual: store_admin

Open **Gift Cards** to configure the capability, issue a card, provide the recipient details and record the one-time code securely. Use the card list to check state and void compromised or incorrectly issued cards with a reason.

## Manual: platform_admin

Govern gift-card limits, validity, denominations, occasions and sources. Ensure wallet capability and notification transport are enabled before activating gift cards for a tenant.
