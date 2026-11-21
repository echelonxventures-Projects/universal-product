# ADR-012: Kafka-API event backbone with CloudEvents envelope

| Field | Value |
|---|---|
| Status | Accepted (master v1.0) |
| Deciders | Architecture Board (U01 root authority) |
| References | master §15.4; U61 Event; spec/events/cloudevent-envelope.schema.json |

## Context
Universes integrate by events at high volume, with replay, ordering per aggregate and many consumers (analytics, search, AI). A portable envelope keeps the ecosystem open.

## Decision
The event backbone exposes the **Kafka API** (Apache Kafka, Redpanda or a managed equivalent). Every event uses the **CloudEvents 1.0** envelope with UCOS extensions (tenant, cell, context, frame, data classes, schema version). Topics follow `ucos.<cell>.<universe>.<object>.v<major>`, and the partition key is the aggregate id.

## Alternatives considered
- Cloud-specific buses: lock-in and weaker replay semantics.
- NATS/JetStream: simpler to operate, but a smaller connector ecosystem for analytics and CDC.

## Consequences
**Positive**
- A large ecosystem (CDC, stream processing, connectors).
- Replay supports rebuilds and backfills (e.g. ledger replay A-19).

**Negative / costs**
- Operational weight, so managed offerings are preferred.
- Schema governance is mandatory (registry, compatibility rules).

## Enforcement
Event schema registry compatibility checks; `TEST-CONTRACT-01`.
