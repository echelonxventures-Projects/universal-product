# Gift cards — the parts only a person can write

## Flows

**Buying a card.** A shopper chooses one of the store's gift-card items, a denomination or any amount
between the store's minimum and maximum, an occasion, the recipient's name and email and a message,
and adds it to the bag. When the order is placed each unit becomes a card for that amount, addressed
to the recipient. The buyer holds the card and sees its code, and is told it is ready.

**Issuing a card.** Staff issue a card directly — a goodwill gesture, a prize, a refund as a card —
with its value, occasion, recipient and message, and optionally the shopper who holds it. The code is
shown once to staff. An offer may also grant a card (`gift_card_issue`); it is issued the same way.

**Redeeming.** A signed-in shopper types a card's code. If the card can still be redeemed, its whole
value moves into the shopper's gift balance (the wallet definition the capability names) as one
ledger movement, the card is marked redeemed, and the shopper holds it too. Checkout spends the gift
balance first.

**Checking.** Anyone may check a code: what it is worth, its state, whether it can be redeemed and
until when.

**Voiding and expiry.** Staff void a card, saying why. A card expires after the store's validity
(none means it never expires). A voided or expired card cannot be redeemed, and the shopper is told
which.

**Security.** A card's code, recipient, message, buyer and redeemer are sealed. A card is found only
by a keyed index of its code, so the code is never stored readable.

## Manual: shopper

1. Open **Gift Cards** from the store's menu.
2. **Give one**: choose the card, an amount (or type any amount within the limits shown), an occasion,
   the recipient's name and email and your message, then **Add to bag** and check out as usual. The
   card's code appears under **Your cards** once the order is placed.
3. **Redeem a card** (signed in): type the code and **Redeem**. The value is added to your gift
   balance, which is used first when you next check out.
4. **Check a card**: type a code to see what it is worth, whether it can still be used and until when.

## Manual: store_admin

1. Gift cards need the **Gift cards** capability (⚙️ Capabilities). Its settings are the smallest and
   largest card, the denominations offered, how long a card is valid and the gift-balance wallet.
2. Open **Offers → 🎁 Gift Cards**. The heading states your limits and validity.
3. **Issue a card**: give its value, occasion, recipient and their email, the holder (an owner key such
   as `t1:u:42`, optional) and a message, then **Issue**. The code is shown once — give it to its
   recipient.
4. The list shows every card by its last four digits, with its value, how it came to be, recipient,
   occasion, validity and state. **Void** cancels a card that can still be redeemed; you are asked why.
5. To sell cards, publish a product whose facts mark it as a gift card; shoppers then find it on the
   **Gift Cards** page.

## Manual: platform_admin

1. The card's life is the `gift_card` state machine; its states, occasions and sources are platform
   registries (`giftCardStatuses`, `giftCardOccasions`, `giftCardSources`).
2. The **Gift cards** capability and its defaults (amounts, validity, code length, the wallet
   definition a redeemed card pays into) are declared by the platform; each store sets its own values.
3. An offer of type `gift_card_issue` issues a card when it applies; the incentive engine asks the
   Gift card domain to write it.
