# TM-TAX-DOCS — Tax determination, e-invoicing and documents

| Field | Value |
|---|---|
| Scope | U31 Tax (GST India, VAT UAE, determination, registrations, e-invoice IRN via IRP), U42 Document (rendering, numbering, signing, delivery) |
| Data classes | FINANCIAL, PII (buyer GSTIN, addresses) |
| Owner | `ucos:org:tax` with `ucos:org:documents` |
| References | U31, U42; CGST Rules (e-invoice), UAE VAT executive regulation |

## STRIDE
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| TX-T1 | Tax rules changed without governance (wrong rates in production) | 2 | 3 | Tax rules are versioned definitions with validity ranges; publication needs approval and regression tests on golden supplies | Rule regression suite |
| TX-T2 | Invoice numbers reused or gapped | 2 | 3 | Per-series sequence allocation in a transaction; cancellations recorded, never deleted | Property tests |
| TX-T3 | Documents altered after issue | 1 | 3 | Rendered documents are content-hashed, stored immutably, and digitally signed where required; the IRN and signed QR come from the IRP | Hash verification job |
| TX-S1 | Fake GSTIN used for B2B input credit | 2 | 2 | GSTIN validation through the government API before applying B2B treatment; mismatch flags | Integration tests |
| TX-I1 | Bulk document download leaks buyer data | 2 | 2 | Signed, expiring URLs scoped to the party; admin exports are audited | Access tests |
| TX-D1 | IRP outage blocks invoicing | 2 | 2 | Queue with retry inside the legal time limit; alert before the deadline; simulator for tests | Chaos tests |
| TX-R1 | Disputed tax computation | 2 | 2 | TaxDetermination stores inputs, rule versions and results (reproducible) | Replay test |

## Abuse cases to test
- Issue two invoices concurrently in one series: the numbers must be unique and consecutive.
- Request a document by guessing its id from another tenant: expect 404.
