# TM-COMMERCE — Cart, checkout, pricing, offers and orders

| Field | Value |
|---|---|
| Scope | U24 Cart & Checkout, U23 Pricing, U22 Offers & coupons, U26 Order & returns, U20 Inventory reservations |
| Data classes | PII (addresses, contact), FINANCIAL (totals) |
| Owner | `ucos:org:commerce` |
| References | U22, U23, U24, U26; ORD-L1 (signed quote snapshot) |

## STRIDE
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| CO-T1 | Client tampers with price, quantity or currency | 3 | 3 | The server prices everything; the order embeds a **signed PriceQuote** snapshot (ORD-L1); checkout re-validates the quote hash at payment | Scenario tests |
| CO-T2 | Race conditions oversell stock or double-redeem coupons | 2 | 3 | Atomic reservations (U13/U20) with TTL; redemption uniqueness constraints; idempotent PlaceOrder | Concurrency tests |
| CO-T3 | Return fraud (wardrobing, empty-box returns) | 2 | 2 | Return windows on Temporal, condition evidence, inspection before refund for high-value items, U69 return-abuse scope from P2 | Policy review |
| CO-S1 | Coupon brute force or leaked single-use codes | 3 | 2 | High-entropy codes, attempt rate limits, per-party limits, batch revocation | Abuse tests |
| CO-R1 | Buyer disputes the terms that applied | 2 | 2 | Immutable commercial terms on the order; adjustments are separate records; documents (U42) generated from the snapshot | Audit |
| CO-I1 | Order details visible to other buyers (IDOR) | 2 | 3 | Every read is authorised by the PDP with the buyer relationship; order numbers are not authorisation | IDOR tests |
| CO-D1 | Cart and checkout bot abuse (inventory hoarding) | 3 | 2 | Reservation TTLs, per-session caps, bot management at the edge, queue tokens (U13) for drops | Load and abuse tests |
| CO-E1 | Seller edits another seller's order lines (marketplace) | 1 | 3 | SellerOrder ownership enforced by policy (seller relation) | Policy tests |

## Abuse cases to test
- Edit the `unitPrice` in the checkout request body: the server must ignore it and return the server price.
- Run 50 parallel redemptions of a single-use coupon: exactly one may succeed.
