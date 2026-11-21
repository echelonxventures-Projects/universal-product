# U61 — Event Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U61-event` |
| Layer | L8 Runtime Fabric |
| Domain | 09 Platform |
| Steward | `ucos:org:platform-kernel-eventing` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 |
| Depends on | U04 Meta, U05 Ontology, U16 Context, U65 Security (classification), U73 Infrastructure (Kafka clusters), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | every capability (emit/consume), U13 Temporal (event triggers), U60 Workflow, U62 Integration (webhooks), U72 Analytics (lakehouse), U14 Data lineage |
| Master references | §15.4–§15.6, §13.3 (outbox, ordering), §14.4 (data contracts) |

> Event owns **the vocabulary and the contract of everything that happens**: event types and versioned schemas, the CloudEvents envelope with UCOS extensions, topics and partitioning, subscriptions, delivery guarantees, the outbox/relay and consumer libraries, replay, dead-letter handling, and the event catalog. It does not own the meaning of a business event (owned by the emitting universe) or webhook delivery to external parties (U62 Integration, built on this).

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| EVT-L1 | Only registered event types with a published schema can be produced. | Producer SDK fetches schema id; broker rejects unregistered subjects (schema registry `auto.register=false`). |
| EVT-L2 | Events are published via the transactional outbox, never by direct broker writes from business transactions. | Pack SDK exposes only `outbox.emit()`; lint. |
| EVT-L3 | Events are immutable facts in past tense. Commands are never sent as events. | Naming lint + review. |
| EVT-L4 | Schemas evolve backward-transitively within a major version. Breaking changes require a new major version and dual publishing for ≥ 90 days. | Schema registry compatibility mode. |
| EVT-L5 | Payloads carry references, not copies, of `restricted` data. PII in payloads requires classification and is subject to retention and erasure. | Schema classification lint; PII topics use encrypted fields + crypto-shredding. |
| EVT-L6 | Consumers MUST be idempotent. | Consumer SDK enforces processed-event store; certification test with duplicate injection. |

---

## 2. Ontology
- **Concepts:** `EventType`, `EventSchema` (versioned), `Topic`, `Subscription` (consumer group + filter), `Consumer`, `DeadLetter`, `ReplayJob`, `DataContract` (master §14.4, owned jointly with the producer; registered here).
- **Event categories:**

  | Category | Examples |
  |---|---|
  | `domain` | business facts, e.g. `order.order.placed` |
  | `integration` | stable public facts for external consumers (subset of domain, curated) |
  | `system` | definition and lifecycle events, e.g. `meta.object-type.published` |
  | `signal` | high-volume telemetry-like business signals (location pings, page views), shorter retention |
  | `audit` | written to the audit store; not for business consumption |

---

## 3. Objects

### 3.1 `ucos.event.EventType`
| Attribute | Type | Notes |
|---|---|---|
| `id` | String `<slug>.<object>.<verb>` | `order.order.placed` |
| `concept` | ConceptRef (U05) | |
| `producer` | CapabilityRef | sole producer (ownership) |
| `category` | EventCategory | |
| `subjectType` | ObjectTypeRef | aggregate |
| `schemas` | Array<EventSchemaRef> | per major |
| `classification` | Classification | max class of payload |
| `retention` | Duration | topic retention (default P7D domain, P1D signal; compacted topics for state) |
| `ordering` | `per-subject|none` | partition key = subject id when per-subject |
| `public` | Boolean | allowed for webhooks/integration |
| `consumers` | derived | from subscriptions |
| `status` | DefinitionStatus | |

### 3.2 `EventSchema`
JSON Schema 2020-12 for `data` (Avro or Protobuf optional for high-volume signal topics), with version, compatibility mode, examples (required, at least 1), and field classification annotations.

### 3.3 Envelope (normative; master §15.4)
Required CloudEvents attributes: `specversion`, `id` (ULID), `source`, `type`, `time`, `subject`, `dataschema`, `datacontenttype`.
UCOS extensions: `ucostenant`, `ucosblueprint`, `ucoscontext` (signed envelope), `ucoscausation` (id of the triggering event or command), `ucoscorrelation`, `ucosclassification`, `traceparent`, `ucosschemaversion`.

### 3.4 `Topic`
Name `ucos.<cell>.<slug>.<object>.v<major>`. Partitions are sized by expected throughput (default 24). Replication factor 3, `min.insync.replicas=2`. Cleanup policy `delete` or `compact`. Tenant isolation is logical (`ucostenant` header plus ACL-filtered consumers). Dedicated-tier tenants get dedicated topics: `ucos.<cell>.t-<tenant>.<…>`.

### 3.5 `Subscription`
`{ id, consumer: CapabilityRef|ConnectorRef|ProjectionRef, eventTypes: [..], filter: CEL (e.g. "data.total.currency == 'INR'"), tenantScope: own|all (platform consumers only), startFrom: latest|earliest|timestamp, maxRetries, backoff, dlq: TopicRef, ordering: preserve|parallel(n) }`

---

## 4. Commands, Queries, APIs & SDK

| Command | Notes / Events |
|---|---|
| `RegisterEventType`, `PublishSchema` (via Governance) | compat check → `event.schema.published` |
| `CreateSubscription` | consumer must declare in its manifest `consumes` |
| `Replay(subscription, from, to, filter)` | privileged; replays into the consumer group with `ucosreplay=true` |
| `RedriveDeadLetters(subscription, filter)` | after fix |
| `DeprecateSchema(major)` | sunset date; consumers notified |

**Producer SDK:** `outbox.emit(type, subject, data)` inside the aggregate transaction. The relay (Debezium-style log tailing on the outbox table) publishes with exactly-once producer semantics and marks the row relayed. Target lag p99 < 500 ms.

**Consumer SDK:**
- At-least-once delivery with offset commit after processing.
- A processed-event table `(consumer, eventId)` gives idempotency.
- Retries: exponential, up to `maxRetries`, then DLQ.
- Poison-message isolation keeps per-subject ordering by parking only that subject's stream.
- Context is restored from `ucoscontext`, and a tracing span is linked.

**Catalog API:**
```text
GET /v1/events/types?producer=&public=          GET /v1/events/types/{id}  (schemas, examples, consumers, lineage)
GET /v1/events/asyncapi?blueprint=              (generated AsyncAPI 3 doc per blueprint)
POST /v1/events/subscriptions                   POST /v1/events/replays    POST /v1/events/dlq/{sub}:redrive
```
**Errors:** `EVT_UNREGISTERED_TYPE`, `EVT_SCHEMA_VIOLATION`, `EVT_INCOMPATIBLE_SCHEMA`, `EVT_NOT_PRODUCER` (only the owner capability may emit), `EVT_REPLAY_FORBIDDEN`.

---

## 5. Rules
- **Ordering:** guaranteed per `subject` (partition key). There is no global order. Consumers needing cross-aggregate order use workflow sagas or event-time windows.
- **Event time vs processing time:** `time` is when the fact occurred. Late events are accepted, and stream processors use watermarks (Flink) with allowed lateness PT5M by default.
- **Fat vs thin events:** domain events carry the changed state snapshot needed by typical consumers (≤ 64 KB), avoiding call-backs. Larger payloads use a claim-check (object store ref).
- **Replay safety:** consumers with external side effects MUST check `ucosreplay` and skip side effects unless replay mode is `reprocess-with-effects` (requires level 3 authority).

---

## 6. Security & Compliance
- Broker access: mTLS plus ACLs per capability identity, so producers can write only their own topics.
- PII fields in payloads are encrypted with per-tenant DEKs (field-level), so crypto-shredding covers event history too.
- Public (webhook) events are filtered by policy per subscriber.
- Audit: subscription changes, replays, redrives.
- Controls: data flow inventory (records of processing from consumers of PII events), and retention enforcement on topics.

## 7. Validation & Reuse
- Capability manifests declare `emits` and `consumes`. The composer verifies every consumed event has a producer in the blueprint (gap otherwise).
- Data contracts are required for `public` events and for events consumed outside the producing universe.

## 8. Gaps & Evolution
```prolog
gap(consumed_without_producer, C, E) :- in_blueprint(C), consumes(C, E), not produced_in_blueprint(E).
gap(event_without_example, E)        :- event_type(E), not has_example(E).
gap(dlq_backlog, S)                  :- subscription(S), dlq_size(S, N), N > 1000.
gap(missing_data_contract, E)        :- event_type(E), cross_universe_consumed(E), not data_contract(E).
gap(deprecated_schema_in_use, E, M)  :- schema_deprecated(E, M), consumer_on_version(_, E, M).
```
- **Self-healing:** consumer lag auto-scales consumers (KEDA). An outbox relay stall triggers relay restart and an alert. DLQ classification separates transient errors (auto-redrive after fix deploy) from permanent ones (cases opened).
- **Evolution:** an event-sourced storage strategy for selected aggregates, using the same envelopes.

## 9. AI
- **AI uses:** event catalog search ("which event tells me a delivery failed?"), and anomaly detection on event rates as business signals.
- **Agents** consume events through subscriptions declared in their manifest and filtered by their authority. They cannot replay.

## 10. Operations
- **Signals:** `outbox_relay_lag_ms`, `consumer_lag_records{subscription}`, `dlq_size{subscription}`, `events_produced_total{type}`, `schema_violations_total` (must be 0 in prod), `duplicate_deliveries_skipped_total`.
- **SLOs:** end-to-end produce→consume p99 < 2 s for domain events; zero data loss (RPO ≈ 0 within a cell; cross-region replication via MirrorMaker 2 with RPO ≤ 1 min).

## 11. UI
- **Views:** `event.catalog` (search, schema viewer, example payloads, producer and consumers graph, lineage to lakehouse tables), `event.subscription.editor`, `event.dlq.console` (inspect, redrive, discard with reason), `event.replay.wizard`, `event.live-tail` (developer sandbox only, masked).

## 12. Scale
Reference: 100k events/s per cell sustained, 500k/s peak for signal topics. Kafka tiered storage holds long retention. T0.

## Appendix
- **B. Amendments:** master §15.5 gains event categories and the claim-check rule.
- **D. Attribute definitions (A-74).** `EventSchema { id, eventType: string, version: string (semver), format: json-schema|avro|protobuf, schema: object, compatibility: BACKWARD_TRANSITIVE|FORWARD|FULL|NONE, examples: [object], fieldClassifications: [{path, classification: Classification}], registeredAt: TimePoint, deprecatedAt?: TimePoint, status: active|deprecated|retired }`
- **C.** 0.1.0.
