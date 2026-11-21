# Runbook — audit-appender

| Field | Value |
|---|---|
| Service | `audit-appender` (Seals audit records into the hash chain.) |
| Universe | U68 |
| Tier | T0 |
| Owner | `ucos:org:governance-audit` |
| SLOs | `spec/slo/audit-appender.yaml` |

## First five minutes
1. Acknowledge the page and open the service dashboard (U72) for the affected cell.
2. Check for a deployment or blueprint activation in the last hour (U73 activations, Argo CD history). If one exists and correlates, roll it back first.
3. Post status in the incident channel; declare an incident (U65) if customer impact is confirmed.

## Availability fast burn
Customer-visible errors are consuming the monthly budget within hours.
1. If the audit store is unreachable, writes fail by design (AUD-L1): restore the store first.
2. Run chain verification for the affected day after recovery.
3. If the cause is a dependency, follow that service's runbook and keep this incident linked.

## Availability slow burn
A steady error rate will exhaust the budget within the window. Open a ticket, find the top error codes (`spec/registries/errors.yaml`) in the dashboard, and fix the leading cause within the sprint.

## Latency breach
The p99 latency of the critical operation exceeded 1000 ms for 15 minutes.
1. Check saturation (CPU, memory, connection pools) and scale out within the cell if needed.
2. Check slow dependency calls in traces.
3. If the audit store is unreachable, writes fail by design (AUD-L1): restore the store first.

## After the incident
Write a blameless review within 5 business days, record follow-ups in U39, and update this runbook if a step was missing.
