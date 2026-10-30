# Group buying — the parts only a person can write

## Flows

**Opening a campaign.** Staff open a campaign on a published product: a group price above zero and
below the product's price, how many members it needs (at least two), the most it may take
(optional) and a deadline in the future. The campaign is joinable from then on.

**Joining.** A shopper sees the group price on the product page with how many have joined, how many
more are needed and the deadline. **Join the group** puts the product in the bag at the group price;
the shopper becomes a member when that order is placed. A shopper joins a campaign once, may buy at
most the capability's limit, and cannot join a campaign that has closed, passed its deadline or is
full.

**Closing.** When the deadline passes — or, where the capability says so, as soon as the campaign is
full — the campaign closes. With enough members it succeeds: every member is told and their orders go
ahead at the group price. Short of members it fails: every member's order is cancelled and what they
paid goes back to their wallet, and each is told. Campaigns are closed by a sweep; staff can also run
it on demand.

**Cancelling.** Staff may cancel a campaign that is still open; its members are refunded the same way
as a failed campaign.

## Manual: shopper

1. On a product with a group offer, the panel shows the group price, how many have joined, how many
   more are needed and until when.
2. **Join the group** adds the product at the group price; check out as usual.
3. If the group fills in time, your order goes ahead at the group price. If it does not, your order is
   cancelled and what you paid is returned to your wallet. You are told either way.
4. Your groups are listed under **Your activity → 👥 Group buys**.

## Manual: store_admin

1. Group buying needs the **Group buying** capability (⚙️ Capabilities). Its settings are the most one
   member may buy, whether a campaign closes as soon as it is full, and the ledger kind used for
   refunds.
2. Open **Offers → 👥 Group Buying**.
3. **New group**: give the product id, the group price, the members needed, the most members (optional)
   and the end, then **Open group**.
4. The list shows each campaign with its price, members against those needed, its end and its state.
   **Cancel & refund** cancels an open campaign and refunds every member.
5. **Settle ended groups now** closes every campaign whose deadline has passed (or that is full),
   without waiting for the sweep.

## Manual: platform_admin

1. A campaign's life is the `group_campaign` state machine, asked by meaning (joinable, refunds
   members); its states are the platform registry `groupCampaignStatuses`.
2. The **Group buying** capability and its defaults are declared by the platform; each store sets its
   own values and decides whether to offer it.
3. Refunds to members are wallet credits of the capability's refund kind, so they appear in each
   member's wallet statement and in the store's ledger check.
