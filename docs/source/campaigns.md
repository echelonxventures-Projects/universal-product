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

**Erasure.** Erasing a person removes their rows from every campaign.

## Manual: store_admin

Open **Marketing & Growth → 📣 Campaigns**. Your role needs the campaigns section; the Growth role
has it.

- **New campaign**: name it, choose the channel and audience (and the segment or company), write the
  subject and message, then **Draft the campaign**.
- Open it to see how many it would reach and who it would skip, then **Send now** or **Schedule**.
- Afterwards it shows how many were sent, skipped, failed and unsubscribed, and why.
- Email and SMS go through your notification gateway (**Payments & notifications**); without one
  they are counted as failed.

## Manual: shopper

Every marketing message from a store has a link at the end. Opening it stops that store's marketing
messages to you; you can turn them back on in your account's privacy settings.
