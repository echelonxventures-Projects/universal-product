# Runbook — inventory

| Field | Value |
|---|---|
| Service | `inventory` (Stock reservations and movements.) |
| Universe | U34 |
| Tier | T0 |
| Owner | `ucos:org:ops-inventory` |
| SLOs | `spec/slo/inventory.yaml` |

## First five minutes
1. Acknowledge the page and open the service dashboard (U72) for the affected cell.
2. Check for a deployment or blueprint activation in the last hour (U73 activations, Argo CD history). If one exists and correlates, roll it back first.
3. Post status in the incident channel; declare an incident (U65) if customer impact is confirmed.

## Availability fast burn
Customer-visible errors are consuming the monthly budget within hours.
1. Check reservation sub-slot contention.
2. Check expired reservations are being released by triggers.
3. If the cause is a dependency, follow that service's runbook and keep this incident linked.

## Availability slow burn
A steady error rate will exhaust the budget within the window. Open a ticket, find the top error codes (`spec/registries/errors.yaml`) in the dashboard, and fix the leading cause within the sprint.

## Latency breach
The p99 latency of the critical operation exceeded 100 ms for 15 minutes.
1. Check saturation (CPU, memory, connection pools) and scale out within the cell if needed.
2. Check slow dependency calls in traces.
3. Check reservation sub-slot contention.

## After the incident
Write a blameless review within 5 business days, record follow-ups in U39, and update this runbook if a step was missing.
