# Group buying — the parts only a person can write

## Flows

**Open.** A store administrator selects a product, group price, minimum members, optional maximum and deadline. The campaign starts in its declared open state.

**Join and settle.** A shopper joins by purchasing the group line. The campaign counts members and closes early when full if configured. At the deadline, a campaign meeting its minimum succeeds; otherwise it fails, cancels member orders and refunds their payments. Staff may cancel an open campaign, which follows the same refund path.

**Failure states.** A closed, full, expired or cancelled campaign cannot accept another member. A member cannot exceed the configured quantity limit.

## Manual: shopper

Open a product with a group offer, review the required member count and deadline, then join through checkout. Track joined groups under your activity. A successful group proceeds normally; a failed or cancelled group returns the paid amount to your wallet.

## Manual: store_admin

Open **Offers → Group Buying**, create the campaign and monitor members. Use **Settle ended groups** after deadlines, or cancel an open campaign when necessary. Verify wallet refunds and order states after a failed campaign.

## Manual: platform_admin

Govern the `group_buying` capability and its parameters: member quantity, close-when-full behavior and refund kind. Review the state machine and tenant activity through platform monitoring.
