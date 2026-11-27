# Books — the parts only a person can write

## Flows

**A sale.** When a shopper's payment is captured, the books record it at once, in the payment's
currency: what the gateway now owes the store (*Payments to be settled by gateways*), and any store
credit or gift balance the shopper spent (released from *Store credit and gift balances held*),
against the sale itself, split as the order was: *Sales*, *Delivery charged* and *Tax collected*.
The gateway's fee is a second entry: *Payment gateway fees* against what the gateway owes.

**A refund.** Each refund — a returned item, a cancelled order, a refund the gateway refused and
that was handed back — is an entry of its own: *Refunds given* and the tax on it given back,
against what the gateway owes. Partial refunds each post their own amount.

**A chargeback lost.** What was not already refunded becomes *Chargebacks lost*.

**The platform's bill.** An invoice from the platform is a fee the store owes (*Platform fees*
against *Owed to suppliers*); paying it clears what is owed from the *Bank*.

**Money reaching the bank.** When a gateway pays out to the store's bank, the accountant posts it:
*Bank* against *Payments to be settled by gateways*.

**Corrections.** Nothing posted is ever edited or deleted. An accountant's own entry is corrected
by reversing it — a mirror entry, linked to it, allowed once, with the reason. An entry a sale or
refund posted is corrected by the business event that undoes it, never by hand.

**Nothing is lost.** Each automatic entry is posted once, whatever retries happen. A payment the
books cannot post (a currency the platform does not know) still goes through, and the books' check
lists it until it is posted. The same check confirms every entry balances and matches the
tamper-evident log.

## Manual: store_admin

Open **Payments & Finance → 📒 Books**. Your role needs the books section; the Finance role has it.

- **Profit and loss** shows income, expenses and profit; **Balance sheet** shows what the store has
  against what it owes and its equity; **Trial balance** shows every account's debits and credits.
  Each currency the store trades in has its own statements. Add `from` and `to` (or `at` for the
  balance sheet) to the API call for a period.
- **Post an entry**: choose the account to debit and the account to credit, the amount, and what it
  is for. Entries that do not balance are refused.
- **Reverse** an entry you posted, saying why. It can be reversed once.
- **Chart of accounts**: every store starts from the platform's chart. Add your own account under a
  group; it takes the group's type and only your store sees it. Codes are never reused.
- Your accounting system can read the same figures with a store API key with the Finance role:
  `GET /api/admin/books/trial-balance`, `/profit-and-loss`, `/balance-sheet`, `/entries` — see
  `docs/api/README.md`.
