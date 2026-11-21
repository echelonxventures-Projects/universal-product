# Service Level Agreement (template)

> **Template for legal review.** Commitments here must not exceed the internal objectives in `spec/slo/` (the SLA is deliberately looser than the SLOs, so that engineering has error budget before customers are owed credits).

## 1. Uptime commitment
| Plan | Monthly uptime | Service credit |
|---|---|---|
| Starter | 99.5% | 10% of the monthly platform fee per 0.1% below, capped at 50% |
| Growth | 99.9% | same |
| Scale | 99.9% | same |
| Enterprise (dedicated cell) | 99.95% | same, or as negotiated |

**Uptime** is the share of one-minute intervals in a calendar month in which the Tenant Platform's storefront and API answer correctly (no 5xx and within 10 seconds), as measured by UCOS's external probes from at least two locations. It excludes scheduled maintenance announced 72 hours ahead (at most 4 hours a month, outside the Customer's peak hours), Customer-caused issues, and failures of the Customer's own third-party providers (PSP, carrier, messaging).

## 2. How the commitment relates to internal objectives
Synchronous services on the request path have internal availability objectives at or above the highest SLA tier (99.95%). The outbox relay is asynchronous (a delay does not fail a request), and payment depends on external providers that the SLA excludes, so their objectives are sized to their own failure modes:

| Service (tier T0) | Internal objective (28-day) |
|---|---|
| `audit-appender` | 99.99% |
| `checkout` | 99.95% |
| `command-bus` | 99.95% |
| `context-resolver` | 99.95% |
| `gateway` | 99.95% |
| `inventory` | 99.95% |
| `object-service` | 99.95% |
| `order` | 99.95% |
| `outbox-relay` | 99.90% |
| `payment` | 99.90% |
| `pdp` | 99.99% |
| `tax` | 99.95% |
| `temporal-triggers` | 99.95% |

Internal objectives are engineering targets, not contractual commitments. Breaching one opens an incident and an error-budget review, not a credit.

## 3. Claiming credits
The Customer claims within 30 days of the month's end through support. UCOS confirms using its monitoring records (U72), which are available to the Customer on request.

## 4. Support response times
| Severity | Starter | Growth | Scale | Enterprise |
|---|---|---|---|---|
| S1 (platform down) | 8 business hours | 4 hours | 1 hour, 24×7 | 30 minutes, 24×7 |
| S2 (major feature degraded) | 1 business day | 8 business hours | 4 hours | 2 hours |
| S3 (question, minor issue) | 3 business days | 2 business days | 1 business day | 1 business day |
