# TM-PAYMENT — Payments

| Field | Value |
|---|---|
| Scope | U29 payment intents, attempts, refunds; PSP adapters (Razorpay, Network International), COD; webhooks; payouts (P2) |
| Data classes | FINANCIAL; card data is out of scope by design (PAY-L1) |
| Owner | `ucos:org:payments` |
| References | U29 (PAY-L1…); PCI DSS v4.0.1 (SAQ A target); RBI guidelines on card tokenisation and payment aggregators; ADR-007 |

## STRIDE
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| PY-S1 | Forged PSP webhook marks an intent as captured | 3 | 3 | Verify the webhook signature with the PSP secret and a timestamp tolerance; never trust webhook amounts; re-fetch status from the PSP API before state change; idempotent by provider event id | Webhook tests |
| PY-T1 | Amount or currency changed between checkout and PSP | 2 | 3 | The intent is created server-side from the signed quote; the PSP order references the intent id; capture amount is checked against the intent | Scenario tests |
| PY-T2 | Refund exceeds the captured amount, or double refunds | 2 | 3 | Refund guard: Σ refunds ≤ captured; idempotency keys; approval above a threshold (decision table) | Property tests |
| PY-I1 | Card data enters UCOS scope | 1 | 3 | Provider-hosted fields/SDK only; CSP restricts frames to PSP origins; DLP blocks PAN patterns in logs and requests | `SEC-PAY-01` |
| PY-I2 | Payment instrument tokens leaked | 1 | 3 | Store only PSP/network tokens; encryption at rest with tenant keys; no tokens in events | Data-class lint |
| PY-R1 | Customer disputes payment (chargeback) | 3 | 2 | Evidence retained (order snapshot, delivery proof, communications); dispute handling (U71 from P3; manual queue in P1) | Ops runbook |
| PY-D1 | PSP outage | 2 | 3 | Multiple methods; COD fallback where allowed; circuit breakers; user-facing retry | Chaos tests |
| PY-E1 | COD orders abused (fake orders, RTO cost) | 3 | 2 | COD limits per party and pincode; OTP confirmation; risk band check (`unknown` in P1 treated as medium) | Decision tests |
| PY-E2 | Operator triggers a refund to a different instrument | 1 | 3 | Refund to the original method only by default; exceptions require dual approval and audit | Policy tests |

## Abuse cases to test
- Replay a captured webhook with a modified amount: state must not change and the event must be logged as rejected.
- Send a webhook with a valid signature but a stale timestamp: it must be rejected.
