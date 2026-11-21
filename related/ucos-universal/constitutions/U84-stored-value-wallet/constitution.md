# U84 — Stored Value & Wallet Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U84-stored-value` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce |
| Steward | `ucos:org:payments-stored-value` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 |
| Depends on | U30 Ledger (balances, double entry), U14 Currency (incl. pseudo-currencies, U77 monetary systems), U29 Payment (top-ups, as a payment method), U13 Temporal (expiry, breakage), U09 Identity (KYC limits), U67 Compliance (PPI / e-money rules) |
| Depended on by | U24 Checkout (pay with gift card/wallet/store credit), U26 Order (refund to store credit), U22 Offer (cashback crediting), U32 Loyalty (points as pseudo-currency), U83 Rental (deposits), U99 Digital Assets (custodial wallets bridge) |
| Master references | Gap analysis A-29 (gift cards, wallets, store credit were only listing type names) |

> Stored Value owns **prepaid and credited value held for customers**: gift cards (physical/digital, open/closed loop), store credit, customer wallets (closed-loop prepaid instruments), vouchers with monetary value, cashback balances, and their issuance, activation, redemption, transfer, expiry and breakage — always backed by Ledger accounts (U30) so that balances have one financial truth.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| SV-L1 | Every stored-value balance is a Ledger sub-account; issuance/redemption are journal entries; no balance columns elsewhere. | U30 integration; lint. |
| SV-L2 | Instruments obey regulatory class per jurisdiction (closed-loop PPI, small PPI, full-KYC PPI, e-money) with limits enforced. | Decision `stored-value.regulatory-class`; limit checks on load/spend. |
| SV-L3 | Expiry and breakage follow law (minimum validity, escheatment, unclaimed property) — never shorter than statutory minimums. | Temporal policies validated against jurisdiction rules. |
| SV-L4 | Codes/PINs are stored hashed; balance enquiries are rate-limited and authenticated to prevent enumeration. | Security controls + U69 risk. |

## 2. Objects
`StoredValueProgram { id, kind: gift-card|store-credit|wallet|cashback|voucher, currency (ISO or X- pseudo), regulatoryClass, issuer (Org), loads: {min, max, sources}, spendScope (stores/sellers/categories), expiry: TemporalPolicy rule, refundability, transferability }` · `Instrument { id, program, holder?: PartyRef, code (hashed)/PIN, formFactor: digital|physical-card, status: inactive|active|frozen|expired|closed, ledgerAccount }` · `Transaction { instrument, kind: issue|activate|load|redeem|refund-to|transfer|expire|adjust, amount: Money, refs (order/payment), journal: LedgerEntryRef }`.

## 3. Commands, Queries, Events, APIs
Commands: `IssueInstruments(batch)`, `Activate`, `Load`, `Redeem` (atomic against balance, returns authorisation), `ReverseRedemption`, `RefundToStoredValue`, `Transfer`, `Freeze`, `ExpireDue` (scheduled), `RecordBreakage` (accounting).
Queries: `Balance(instrument)` (auth), `History(instrument)`, `HolderInstruments(party)`.
Events: `stored-value.instrument.issued|activated|redeemed|expired`.
As payment method: implements an internal `payment.provider` adapter (`stored-value`) so Checkout can split tender (gift card + card).
```text
POST /v1/stored-value/programs     POST /v1/stored-value/instruments:issue
POST /v1/stored-value/instruments/{id}:activate|:load|:redeem|:freeze
GET  /v1/stored-value/instruments/{id}/balance
```

## 4. Rules & Compliance
RBI PPI Master Directions (India), EU E-Money Directive & PSD, US CARD Act gift-card rules & state escheat laws, UAE stored-value regulations; KYC tiers drive limits; AML monitoring on loads (U69). Breakage recognition per accounting policy (IFRS 15) via Ledger.

## 5. Gaps
```prolog
gap(stored_value_without_ledger, T) :- tenant(T), stored_value_program(T, _), not capability(T, ledger.core).
gap(expiry_below_statutory, P, J)  :- program(P), in_scope_program(P, J), expiry_days(P, D), statutory_min_days(J, M), D < M.
gap(ppi_licence_required, T, J)    :- tenant(T), wallet_program(T, J), licence_required(J, ppi), not licence_record(T, J, ppi).
```

## 6. AI & Ops & UI & Scale
AI: fraud on gift-card abuse (U69). Signals: `outstanding_liability{program}`, `redemptions_total`, `breakage_amount`, `enumeration_attempts_total`. Views: `gift-card.purchase` (storefront), `wallet.balance` (customer), `stored-value.program.editor`, `stored-value.liability.report` (finance). T0 for redeem path.

## Appendix
- **C.** 0.1.0.
