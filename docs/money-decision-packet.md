# Money — owner decision packet for gate 4 (2026-10-29)

**For:** the business owner responsible for financial policy, and whoever owns tax compliance
in each launch market. **Status of every decision below: OPEN. Nothing here is approved, and
nothing has been applied.** The platform keeps running on the technical defaults named in
[docs/money-decisions.md](money-decisions.md) until the owner decides.

This packet adds consequences, impact, risk and an engineering recommendation to the existing
records MD-1 to MD-5. It does not replace them. **How a decision is recorded** (the existing
process in `docs/money-decisions.md`): the owner's choice, the date and the approver's name go
into the MD record. The same entry goes into `PRODUCTION_READINESS.md` gate 4, and the
configuration named under "Where it is applied" is changed in a reviewed commit. A
recommendation in this packet is not a decision.

| # | Decision | Record | Recommended |
|---|---|---|---|
| 1 | Rounding rule per currency and jurisdiction | MD-1 | C: per-market rule, default kept as `half-up` |
| 2 | Launch scope of the exact money model | MD-2 | A: payment spine only |
| 3 | Tax and offer effects of a partial refund | MD-3 | B: pro-rata tax; offers reversed only on a full refund |
| 4 | `REAL` money outside the launch scope | MD-2 (PR-045), MD-5 | disable whatever charges or pays; risk-accept only reporting |
| 5 | Migration rehearsal, quarantine, authorization | MD-4 | rehearsal mandatory; per-reason rules signed by a named approver |

## What is already done (engineering, verified)

- **Payment spine exact end to end.** It covers orders, order lines, payments, invoices, invoice
  lines, credit notes, settlements, disputes, payouts and payout items (21 amount columns), plus
  the new `refunds` table. Each is stored as integer minor units in its own currency and scale,
  through one contract (`lib/money.js`). A database guard on SQLite and Postgres refuses a
  `REAL` value that differs from the minor value.
- **Rounding is configuration.** Seven named rules are supported and selected in
  `lib/seed/money.json`. Rounding happens once per operation, at the points listed in
  [docs/money.md §3](money.md#3-the-rounding-policy). Checked against 5,100 reference vectors
  from an independent decimal implementation.
- **Migration `money-0001`.** It runs in one transaction that checks its own result. Every
  stored amount is classed as exact, normalized (float residue, audited) or quarantined (source
  kept, candidates listed, nothing guessed). A killed migration leaves nothing behind and
  resumes to the same result.
- **Refunds.** A refund is exact and can never exceed what was captured, even with two
  processes racing. It is idempotent per key. A refund with no provider answer stays `unknown`
  until staff resolve it.
- **Evidence.** `test/money.js`, `test/money-store.js`, `test/integrations.js`, 12 mutation
  checks, Postgres identical to SQLite (`PRODUCTION_READINESS.md`, Release evidence), and CI on
  PR #6.

## What is not done (governance and real data)

- No owner has chosen a rounding rule, a launch scope or partial-refund effects (decisions 1–3).
- 106 money columns in 64 tables outside the spine are still `REAL` (PR-045,
  `docs/money-inventory.generated.md`). No domain has been put in or out of scope (decision 4).
- **No real database has been migrated.** No staging or production copy exists (PR-026), so
  the real quarantine volume is unknown (decision 5).
- Nothing has been verified against a payment provider's sandbox (PR-025).
- Pro-rata refund tax (decision 3, option B) **is not implemented**. Choosing it adds
  engineering work before launch.

---

## 1. Rounding rule per currency and jurisdiction (MD-1)

**Today:** `half-up` for every currency. Tax is rounded once per document (the
`checkout.tax_per_line` gate is off). No cash rounding.

| Option | Financial consequence | Implementation impact | Risk |
|---|---|---|---|
| A. `half-up` everywhere | Each rounding point can move an amount by at most half a minor unit. Ties always go up, so the total over many documents carries a small upward bias in the platform's favour. | none (current configuration) | A tax authority that prescribes another rule sees a one-minor-unit difference on some documents |
| B. `half-even` everywhere | No systematic bias. On a tie, a shopper may see the amount rounded down. | one configuration value | Where receipts are expected to round half up, totals can differ by one minor unit from what shoppers or the provider compute |
| **C. Per market (recommended)** | Each market's documents match its authority. The difference between A and B is at most one minor unit per rounding point. | `currencies.XXX.rounding` per currency in `lib/seed/money.json`; per-line or per-document tax via the `checkout.tax_per_line` gate. No code change. | The rule has to be written and reviewed for every launch market. A missing entry falls back to the platform default. |

Also to be decided under MD-1:

- **Tax per line or per document.** Both are exact, and they can differ by one minor unit per
  document. Recommended: per document, unless a launch market's authority requires per line.
- **Cash rounding** (smallest coin larger than the minor unit). It is not implemented.
  Recommended: leave it out of launch unless a launch market requires it for cash on delivery.
  If one does, it becomes engineering work at the payment boundary.

**Recommendation:** C, with the platform default kept at `half-up`. The owner names each launch
currency and jurisdiction with its rule and its tax basis, signed off by the market's tax
owner.

**Evidence that closes it:** the signed rule table, the matching `lib/seed/money.json` commit,
and `test/money.js` green on it.

## 2. Launch scope of the exact money model (MD-2)

| Option | Financial consequence | Implementation impact | Risk |
|---|---|---|---|
| **A. Payment spine only (recommended)** | Everything a shopper pays, is refunded, is invoiced or is settled is exact and reconcilable to the minor unit. Features outside the spine are unavailable at launch. | Each PR-045 domain's capability stays off. Configuration only. | lowest |
| B. Spine plus selected `REAL` domains under a written risk acceptance | Those domains' amounts can be off by a minor unit and cannot be reconciled exactly. | none | A domain that charges, pays out or reaches a provider can misstate real money |
| C. Migrate named domains before launch | Same exactness as the spine. | Per domain: declare its tables in `lib/seed/money.json` `store.tables`, write through `lib/money-store.js`, remove its rounding sites, add tests | The launch date depends on how many domains are named |

**Recommendation:** A. Add C for any domain the owner needs at launch, one domain at a time,
each meeting the MD-2 enabling condition.

**Evidence that closes it:** the approved scope list in MD-2, with the capability state of each
PR-045 domain recorded.

## 3. Tax and offer effects of a partial refund (MD-3)

**Today:** a partial refund records only its exact gross amount. It apportions no tax and
reverses no offer. A full refund reverses offer redemptions.

| Option | Financial consequence | Implementation impact | Risk |
|---|---|---|---|
| A. Amount only (current) | Tax reports overstate tax collected by the refunded share until someone adjusts them by hand. | none | Tax filings diverge from refunds; manual adjustment is error-prone |
| **B. Pro-rata tax (recommended)** | The refund's tax share is order tax × refund ÷ order total, allocated exactly, so the shares of several partial refunds add up to the order's tax. Reports follow refunds automatically. | **Not built.** Needs `tax_minor` on `refunds`, the allocation in `lib/refunds.js`, a tax-report change and tests. | Pro rata may not match an authority that taxes by the returned item |
| C. Line-based | Tax and offers follow the exact lines and quantities returned. | Largest: needs a line-selection UI, offer attribution per line, and provider partial refunds per line | Most build and test effort before launch |

**Offers.** If a partial return drops an order below an offer's threshold, the current rule lets
the shopper keep the whole discount. Reversing pro rata or per line changes what a shopper
keeps after a partial return, and the shopper terms must say so.

**Recommendation:** B for tax. Offers stay reversed only on a full refund, and the refunded
amount is entered net of any discount the staff member judges forfeited. Revisit C after
launch. If B cannot be built before launch, choose A with a written instruction for the manual
tax adjustment.

**Evidence that closes it:** the decision in MD-3; if B, the implementation and tests in CI,
then a partial refund against the provider sandbox (gate 2/3).

## 4. `REAL` money outside the launch scope (MD-2 / PR-045, MD-5)

There are two separate questions:

- **(a) Domains outside the spine** (fintech, payroll, mobility fares and earnings,
  affiliates, ads, auctions, peer listings, group buy, GOIP settlements and others: 106
  columns).
- **(b) The spine's own `REAL` projections.** These are kept, and the database guard forces
  them equal to the exact value, until readers move. The proposed removal is `money-0002`
  within two releases of launch.

| Option for (a) | Financial consequence | Implementation impact | Risk |
|---|---|---|---|
| **Disable every domain that charges, pays out, lends or reaches a provider until migrated (recommended)** | No real money moves through float arithmetic | capability off; configuration | Those features wait |
| Allow reporting-only domains (metrics, attribution) under a risk acceptance | Indicative figures can be off by a minor unit | none | Low, provided no one reconciles or settles from them |
| Migrate | Exact | per domain, as decision 2 option C | Schedule |

**Recommendation:** disable every money-moving domain until it is migrated. Allow
reporting-only domains only under a written, named risk acceptance. For (b), the owner sets the
`money-0002` date in MD-5; recommended no later than two releases after launch.

## 5. Migration rehearsal, quarantine handling and authorization (MD-4)

**Today:** a fresh install has nothing to migrate. Any existing database being upgraded runs
`money-0001` at its first boot on this code. Quarantine reasons are `excess_precision`,
`currency_missing`, `currency_unknown` and `not_a_number`. Float residue (`binary_noise`) is
normalized and audited, not quarantined. A quarantined row cannot be refunded, settled or
collected until it is resolved.

| Option | Financial consequence | Implementation impact | Risk |
|---|---|---|---|
| A. Resolve each entry by hand from source records | Exact | none: `node scripts/money.js resolve`, or the platform API, records who, when and why | Effort grows with the count |
| **B. A signed rule per reason, applied per row with audit (recommended for `excess_precision`)** | Deterministic; the rule is a recorded decision | none: the same tool, one call per row under the approved rule | A wrong rule is applied at scale, so it needs a second reviewer |
| C. Leave entries quarantined | Rows stay visible but frozen | none | Refunds and settlements blocked for those customers |

**Recommendation:**

1. **The rehearsal is mandatory** before launch for any install that has existing data. Restore
   a backup copy into staging, boot this code, run `node scripts/money.js quarantine`, then
   `npm run money:verify`, and record the counts per reason and the migration time.
2. `excess_precision`: rule B. The candidate under the approved MD-1 rule is applied, signed by
   a named finance approver and reviewed by a second person.
3. `currency_missing` and `currency_unknown`: option A only. The currency must be stated by
   someone who knows it, because the platform never infers one.
4. `not_a_number`: option A from source records.
5. Launch only when no open entry remains on any row that a refund or settlement can touch.

**Evidence that closes it:** the rehearsal transcript, the resolved quarantine report with
approver names, and a clean `money:verify` on the staging copy. **Not possible today:** no
staging environment or real data exists (PR-026).

---

## Owner sign-off (blank until decided)

| # | Record | Option chosen | Approver (name, role) | Date | Commit applying it |
|---|---|---|---|---|---|
| 1 | MD-1 | | | | |
| 2 | MD-2 | | | | |
| 3 | MD-3 | | | | |
| 4 | MD-2 / MD-5 | | | | |
| 5 | MD-4 | | | | |
