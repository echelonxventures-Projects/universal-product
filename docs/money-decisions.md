# Money — decisions the owner must take (PR-016, PR-029, PR-045, gate 4)

Each record below is **OPEN**. None has been approved. The platform runs on the technical
defaults named in each record so that it can be built and tested; a default is not a policy.
When the owner decides, the decision, its date and its approver are written into the record and
into `PRODUCTION_READINESS.md` (gate 4), and the configuration named under "Where it is applied"
is changed to match. The model itself is described in [docs/money.md](money.md).

## MD-1 — The rounding rule, per currency and jurisdiction

**Status:** OPEN. **Technical default:** `half-up` for every currency (`lib/seed/money.json`
`rounding`), tax rounded once per document (`checkout.tax_per_line` gate off).

| Option | Behaviour | Consequence |
|---|---|---|
| A. `half-up` everywhere | 0.005 → 0.01, −0.005 → −0.01 | What most receipts and shoppers expect; a slight upward bias summed over many roundings; may differ from a tax authority that prescribes another rule |
| B. `half-even` everywhere | 0.005 → 0.00, 0.015 → 0.02 | No systematic bias; the usual choice in accounting and some tax regimes; a shopper may see a half-cent rounded down |
| C. Per currency / per jurisdiction | `currencies.XXX.rounding` overrides | Matches each authority; must be written per market and reviewed by whoever owns tax compliance there |

Also to decide: **tax per line or per document** (per line sums each line's exact tax and rounds
once; per document taxes the total once — both are exact, they can differ by a minor unit), and
**cash rounding** for currencies whose smallest coin is larger than the minor unit (not
implemented; would be a new rule at the payment boundary only).

**Where it is applied:** `lib/seed/money.json` (`rounding`, `currencies`), the
`checkout.tax_per_line` gate. No code change.

## MD-2 — The launch money scope

**Status:** OPEN. **Technical position:** the payment spine is exact (docs/money.md §1); every
other domain's money is still `REAL` (PR-045, `docs/money-inventory.generated.md`).

| Option | Consequence |
|---|---|
| A. Launch with the payment spine only; every domain listed in PR-045 stays disabled (its capability off) until migrated | Smallest risk; those features are unavailable at launch |
| B. Launch with selected PR-045 domains enabled, accepting `REAL` arithmetic there under a written risk acceptance | Features available; their amounts can be a minor unit off and are not reconcilable exactly; any of them that charges or pays through a provider would need migration first |
| C. Migrate named PR-045 domains before launch | Each is a bounded change of the same shape (declare the table in `lib/seed/money.json`, write through `lib/money-store.js`), with its own tests |

**Condition proposed for enabling a PR-045 domain:** its money columns are declared in
`lib/seed/money.json` `store.tables`, written only through `MS.insert`/`MS.update`, its
rounding sites are gone from `node scripts/money-audit.js`, and its tests cover the amounts it
charges or pays.

## MD-3 — Tax and offer effects of a partial refund

**Status:** OPEN. **Technical position:** a partial refund records only its exact amount; it
apportions no tax and reverses no offer redemption. A full refund reverses offer redemptions
and emits `order.refunded` (as before).

| Option | Behaviour | Consequence |
|---|---|---|
| A. Amount only (current) | The refund is a gross amount | Tax reports overstate tax collected by the refunded share until adjusted by hand |
| B. Pro-rata tax | The refund's tax share = order tax × refund / order total, allocated exactly (largest remainder) and recorded on the refund | Tax reports follow refunds automatically; needs a `tax_minor` on refunds and a report change |
| C. Line-based | The operator names the lines and quantities refunded; tax and offers follow those lines | Most precise; needs a line-selection UI and per-line offer attribution |

Offers: reverse a redemption only on a full refund (current), pro rata, or per refunded line —
each changes what a shopper keeps of a discount after a partial return.

## MD-4 — Ambiguous historical records

**Status:** OPEN; **no real database has been migrated** (there is no staging or production
copy, PR-026). On a real migration rehearsal, `node scripts/money.js quarantine` lists every
amount that could not be converted, with its source value and candidates.

| Option | Consequence |
|---|---|
| A. Resolve each entry by hand from source records (provider dashboard, invoice PDF) | Exact; effort grows with the count |
| B. Approve a bulk rule per reason (e.g. "excess_precision → the configured rule's candidate") and apply it with a named approver | Fast; the rule is a recorded decision, not a guess; each application is still audited per row |
| C. Leave entries quarantined | The rows stay visible but cannot be refunded, settled or collected until resolved |

`currency_missing` entries need a currency stated by someone who knows it — the platform never
infers one.

## MD-5 — Removal of the `REAL` projections

**Status:** OPEN. Proposed: within two releases of launch, once every reader listed by
`node scripts/money-audit.js` reads minor units, a migration `money-0002` drops them
(docs/money.md §4). The owner sets the date.
