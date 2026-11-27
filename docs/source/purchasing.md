# Purchasing — the parts only a person can write

## Flows

**Ordering.** A buyer drafts a purchase order to a supplier — from an approved purchase request,
or on its own — with each item, quantity and unit cost, in the supplier's currency unless another
is chosen. Sending it to the supplier stamps it; a request it fills becomes *ordered*.

**Goods arriving.** When a delivery arrives, the warehouse records what came in, line by line, into
the warehouse it reached, with its lot, batch and expiry. No more can be received than was ordered.
The product's and variant's stock and the warehouse's batch go up at once, and the books record the
stock (*Inventory*) against *Received, not yet billed*. When everything has arrived the order is
*received*, and so is the request behind it.

**The supplier's bill.** The bill is recorded with the supplier's own invoice number — once per
supplier — and matched against what was received and not yet billed. Within the tolerance it is
approved and owed: the books clear *Received, not yet billed*, add *Tax to reclaim*, and owe the
supplier the gross. A bill further apart than the tolerance is *held*, with the reason, and is
neither owed nor payable until someone releases it, saying why; the difference becomes a
*Purchase price difference*.

**Paying and voiding.** Marking a bill paid clears what is owed from the bank. Voiding an approved
bill undoes its entry, so the goods are again received and not yet billed.

**Finishing.** An order nothing has arrived against may be cancelled; one with deliveries is
closed instead, when the rest will not come.

## Manual: store_admin

Open **Payments & Finance → 🧾 Purchasing**. Your role needs the purchasing section; the Finance
role has it.

- **New purchase order**: choose the supplier and the warehouse, the item, the quantity and the
  unit cost, then **Draft the order**. Open it and **Send to supplier**.
- **Record goods received**: open the order, set how many of each line arrived (the rest is
  pre-filled), the warehouse, lot and expiry, and record it. Stock goes up immediately.
- **Record the bill**: enter the supplier's invoice number, the net and the tax. If it differs from
  what was received by more than the tolerance it is held: check it, then **Release** it with the
  reason, or **Void** it.
- **Mark paid** when the supplier has been paid. **Owed to suppliers** shows what is due and how
  late, per supplier.
- Your purchasing or ERP system can do the same through `/api/admin/purchasing/…` with a store API
  key with the Finance role — see `docs/api/README.md`.
