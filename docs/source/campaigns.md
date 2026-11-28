# Campaigns — the parts only a person can write

## Flows

**A campaign.** A store drafts a message — by email, by SMS, or as a note in the shopper's account —
for an audience: every customer, a segment, every CRM contact, or the people at one company.
`{name}` and `{store}` in the subject and message are filled in for each person.

**Who it reaches.** Only people with a live consent for marketing. Before sending, the store sees how
many it would reach and how many it would skip and why (no consent, no address). The list is built
when the campaign starts; consent is checked again right before each message, so someone who
withdrew in the meantime is skipped.

**Unsubscribing.** Every message ends with the person's own link. Opening it withdraws their marketing
consent at once, with a confirmation page; no later campaign reaches them unless they agree again.

**Sending.** Messages go out in batches. Each person is claimed before their message, so two servers
never send the same person the same campaign; a message whose sending was cut off is marked as
interrupted, never sent twice. A campaign may be scheduled for later and goes when its time comes, or
cancelled — whoever has not been sent to yet is not.

**Journeys.** A journey sends messages on its own when something happens to a person: they create
an account, place an order, have an order delivered, or leave items in their cart for a couple of
hours. A journey can also start with an audience you enrol by hand. Each step waits a while after the
one before — straight away, a day, a week — and goes by email, SMS or the shopper's account. A person
enters once, or each time it happens if you choose. A segment can narrow who enters.

**Who a journey reaches.** Only people who agreed to marketing, checked when they enter and again
before every message. Shoppers can tick "Send me offers and news" when they create an account. An
event you choose as the journey's exit takes the person out early: an order ends an abandoned-cart
journey before its reminder goes. Nobody gets more than three journey messages a day; one over the
limit waits until the next day. Unsubscribing from any message takes the person out of every journey.

**Opens and clicks.** Links in every campaign and journey message are tracked: a click is counted and
the reader goes straight on to the link. An email also counts when it is opened, where your email
gateway sends HTML email (SMTP does). Opens are approximate: some mail apps load images on their own
and some block them.

**Erasure.** Erasing a person removes their rows from every campaign and journey.

## Manual: store_admin

Open **Marketing & Growth → 📣 Campaigns**. Your role needs the campaigns section; the Growth role
has it.

- **New campaign**: name it, choose the channel and audience (and the segment or company), write the
  subject and message, then **Draft the campaign**.
- Open it to see how many it would reach and who it would skip, then **Send now** or **Schedule**.
- Afterwards it shows how many were sent, skipped, failed and unsubscribed, and why.
- Email and SMS go through your notification gateway (**Payments & notifications**); without one
  they are counted as failed.

Open **Marketing & Growth → 🧭 Journeys** for journeys:

- **New journey**: name it, choose what starts it and what ends it early, add steps with their wait,
  channel, subject and message, then **Draft the journey**. **Start** it to let people in.
- Open a journey to see each step's sends, opens, clicks and unsubscribes, and who is in it.
- **Pause** stops sending and entering; a paused journey can be changed and started again. **End for
  good** stops everyone in it.
- A journey started "by hand" takes an audience: choose it and **Enrol them**.
- **Send what is due now** sends due steps at once; otherwise the platform sends them on its cycle.

## Manual: shopper

Every marketing message from a store has a link at the end. Opening it stops that store's marketing
messages to you, including any series you are in; you can turn them back on in your account's
privacy settings. When you create an account you choose whether to get offers and news.
