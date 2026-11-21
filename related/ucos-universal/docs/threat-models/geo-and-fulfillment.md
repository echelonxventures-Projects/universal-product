# TM-GEO-FULFIL — Location, addresses and fulfilment

| Field | Value |
|---|---|
| Scope | U12 Geography (addresses, geocoding, zones, serviceability, maps port), U35 Fulfilment (fulfilment orders, shipments, pickup, tracking pages), carrier adapters |
| Data classes | PII, LOCATION |
| Owner | `ucos:org:ops-fulfilment` |
| References | U12, U35, U36 (P2); LOG-L4 |

## STRIDE
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| GF-I1 | Public tracking page reveals the full address or phone number | 3 | 2 | Tracking links carry an unguessable token; pages show city/area only; full details only after login | Page review |
| GF-I2 | Courier or driver data over-exposed | 2 | 2 | Masked contact via proxy numbers (U40/U109); time-boxed live location (LOG-L4) | Policy tests |
| GF-S1 | Forged carrier tracking webhooks (fake "delivered") | 2 | 3 | Signature or allow-listed source plus a re-fetch from the carrier API for terminal states; delivered state requires proof (OTP or POD) for high-value items | Webhook tests |
| GF-T1 | Address tampering after order (redirect parcels) | 2 | 3 | Address change only before dispatch with re-authentication, notification to the original contact point, and a risk check | Scenario tests |
| GF-D1 | Geocoding provider quota exhaustion | 2 | 2 | Caching of results, per-tenant quotas, fallback to postal-code centroid | Load tests |
| GF-R1 | Disputed delivery | 3 | 2 | Proof of delivery (photo, OTP, geo-stamp) stored as evidence | Ops |

## Abuse cases to test
- Enumerate tracking tokens: expect rate limiting and no data for invalid tokens.
- Change the delivery address after dispatch: expect a rejection with a support route.
