# Foundations

**Status:** finalised design, 2026-10-17. Nothing in this document is built yet. Building starts
once the owner signs it off, following "The path" (§11).

**How to read it.** Every concern has exactly **one owner**: a kernel part or a domain. It is
defined only in its owner's section. Every other section refers to it by name and never
restates it. The coverage tables (§8, §9) and the gate tests (§10) prove that nothing is
duplicated, partial, missing or left in a gap.

## 1. Purpose

LUXORA must go live anywhere, for anyone, in any combination, by configuration alone.

- **Places:** anywhere from a single coordinate, shelf or mall to a city, a country, an ocean,
  a planet, a galaxy, or a mix.
- **Everything else:** any language, currency, domain, segment or industry, in any combination.

A person with the user manual, or an AI agent, does it through the console or the API. A launch
never needs engineering, architecture or foundation work. The domains are reused across the
platform and are sold to other platforms.

## 2. The constitution

1. **Configuration only.** Launching, extending or changing LUXORA is configuration. Code never
   fixes:
   - a domain value;
   - a place, calendar, currency, language or text direction;
   - a table, field or screen;
   - a workflow, message, report or integration.
2. **Every domain is complete, from zero to infinite.** It covers its whole range, from the
   smallest instance to the largest, with no Earth or single-market assumption.
3. **One owner per concern: zero duplication.** Each concern, fact and capability is defined
   and stored in exactly one place (§8). Everything else references it.
4. **No entity embeds another domain's data.** What one entity needs from another domain is a
   relationship (§5.2, Relationship). A place stores no currency, and a store stores no country.
5. **Everything else is derived.** The resolver (K11) answers from relationships, hierarchies,
   time and context. Nothing is stored twice.
6. **Master data belongs to the platform.** Platforms, tenants and modules select it through
   views (K10) and never copy it. A tenant extends only within its own scope.
7. **Every choice is a selection from the owning entity, in any combination.** Constraints are
   declared by the entities, and every option carries a free or paid offering (§6).
8. **Nothing is invented.** Creating one thing never creates another. Anything missing shows as
   *incomplete* until a person or agent completes it.
9. **Rules belong to kinds.** A format or validation rule, such as an ISO code for an Earth
   country, belongs to the kind that needs it, never to a whole domain.
10. **One kernel: zero partial.** Every domain is built on the same kernel and automatically
    receives every kernel part and every shared service (§3). No domain can lack one.
11. **Everything is configurable from the console,** through one change lifecycle (K9).
    That covers schema and database, screens and themes, workflows, notifications,
    communications, reports, integrations, agents and packages.
12. **One API for everyone.** The console, storefronts, apps, agents, partners and other
    platforms use the same generated API (§5.5, Integration).
13. **Agents are bounded actors.** An agent never exceeds the person or role it acts for
    (§5.5, Agent).
14. **Security and compliance are on by default** and can only be tightened, never weakened
    (§5.3, Trust and Compliance).
15. **Everything is audited, immutably** (§5.3, Audit).
16. **Packages compose domains.** Customisation is an overlay that survives upgrades (§7).
17. **Every existing module has exactly one home: zero missing** (§9).
18. **Gate tests hold every rule** (§10). A rule without a gate test is not finished.

## 3. The kernel

The kernel is built once. A domain is configuration on top of it. Each part below is defined
here and nowhere else.

| # | Part | What it is |
|---|---|---|
| K1 | **Kinds** | The kinds a domain contains. Each kind declares:<ul><li>its attributes (via Schema);</li><li>which kinds it may sit inside;</li><li>its validation rules (constitution 9);</li><li>its identifier schemes;</li><li>whether it carries a shape.</li></ul>Users add kinds. |
| K2 | **Nodes** | The instances, with no limit on count or depth. |
| K3 | **Hierarchies** | Named hierarchies over shared nodes. A node may sit in many hierarchies, and in more than one place within one hierarchy. Stored so that lookups up and down any depth stay fast. |
| K4 | **Identifiers** | A universal ID for every node, plus any number of code schemes (ISO, UN M49, postal, IATA, H3, IAU, a store's own). Schemes are data. |
| K5 | **Shape** | For kinds that declare it: a point, area or volume in a declared coordinate system. A spatial cell index per coordinate system resolves any coordinate to every node that contains it. |
| K6 | **Attributes** | Typed values, declared in Schema. Labels and text are multilingual through Language. Values a declaration marks sensitive are encrypted through Trust. |
| K7 | **Versions** | Bi-temporal: *valid time* (true in reality) and *recorded time* (when entered). Nothing is overwritten, and any past state can be queried. |
| K8 | **Events** | Every change, and every declared business occurrence, emits one event to a single event log. Workflows, notifications, the analytical store, webhooks and audit all read this log. There is no second event bus. |
| K9 | **Change lifecycle** | One path for every configurable thing (data, schema, theme, workflow, template, report, agent, connector, package):<ol><li>draft;</li><li>validate;</li><li>preview and simulate, per device where relevant;</li><li>approve, as declared;</li><li>publish, now or scheduled;</li><li>roll back.</li></ol>**Hide** is reversible. **Delete** is two stages: archive (recoverable for the declared retention), then purge, which needs a separate permission. Nothing that a live relationship, a licence, an audit record or a legal hold depends on can be purged. Running work finishes on the version it started with. |
| K10 | **Views and scope** | **Views:** a platform, tenant, module or subscriber selects hierarchies, subtrees, depth, groupings and labels by reference. **Scope:** everything lives in a namespace (platform, tenant, publisher), so names never collide, and at a scope level (platform, tenant, store, channel, place, language, segment, device type, person). |
| K11 | **Resolution** | One resolver answers "what applies here, now", from:<ul><li>relationships;</li><li>hierarchies (the nearest declaration wins);</li><li>time windows;</li><li>context;</li><li>rules.</li></ul>Answers are cached and invalidated by K8 events. Settings and defaults are resolver answers, not stored copies. |

**Shared services every domain receives automatically.** Each service is defined once, by its
owner:

| Service | Owner |
|---|---|
| Declared fields, validation and storage | Schema |
| Links to any other entity | Relationship |
| Permissions and encryption | Trust |
| An immutable record of every change and access | Audit |
| Obligations and retention | Compliance |
| Names in every language | Language |
| Screens on every device | Experience |
| Generated API, events and webhooks | Integration |
| Being found | Search |
| Being reported on | Insight |
| Being operated by agents, as tools | Agent |
| Being priced and licensed | Offering |
| Help and manual pages | Knowledge |

## 4. The layers

1. **Kernel** (§3).
2. **Domains** (§5): complete, individual entities.
3. **Business entities** (§5.8): built on the kernel from the domains.
4. **Packages** (§7): ready-made, editable compositions for a kind of platform.
5. **Platforms and stores**: instances that install packages and make their own selections (§6).

## 5. The domains

Each domain section states only what the domain **owns**. Everything it uses from other
domains is named, not restated.

### 5.1 Universal facts

**Geo.** Every place, at every scale.
- **Kinds:** universe, galaxy, star system, star, planet, moon, ocean, sea, continent, country,
  region, city, district, site, building, floor, room, shelf, point, and virtual places (realms,
  networks), plus any kind users add.
- **Example nodes:** Milky Way, Solar System, Sun, Earth, Moon, Asia, Indian Ocean, India,
  Bihar, Patna, one mall, one coordinate.
- **Hierarchies:** physical (Earth → Asia → India), political, postal, carrier zones, sales
  territories. Türkiye sits in Europe and Asia.
- **Coordinate systems:** WGS 84, areographic, selenographic, galactic.
- **Address formats:** the fields, order, required parts and postcode pattern, declared per
  place kind.
- **Data placement:** where data may live, which Operations enforces.
- **Relationships it typically holds:** for example, India *uses* INR, *follows* IST and the
  Gregorian calendar, *speaks* Hindi and English, and *is governed by* GST rules. Patna and one
  mall inherit these unless they declare their own.
- **Ships with:** the core down to first-level regions. Deeper levels (cities, postcodes,
  streets) are imported on demand from declared sources (ISO 3166, UN M49, GeoNames, IAU),
  because full depth runs to millions of rows.

**Time.** Every way of measuring and scheduling time.
- Chronologies, calendars (Gregorian, Hijri, Hebrew, fiscal, Darian, any declared), epochs.
- Clocks and zones per body (IANA for Earth).
- Business hours and holidays per place.
- Periods, recurrences, availability, validity windows.
- Signal delay between bodies, so no design assumes an instant network.

**Measure.** Every quantity and unit.
- From Planck scale to light-years, including time and data units.
- Conversions between any systems (metric, imperial, local).

**Value.** Every unit of value.
- Fiat (ISO 4217), colonial, federation, points, carbon, energy, commodity.
- Minor units.
- Rates over time from declared sources.
- Settleability.

**Language.** Every language and every piece of interface text.
- Languages, scripts, direction, plural rules (CLDR).
- Message catalogues for every interface string.
- The multilingual names of every node in every domain, so "India", "भारत" and "Inde" are one
  node.
- Translation, by people or agents, through K9.

**Classification.** Domains, industries, segments and taxonomies at any depth.

**Context.** Declared dimensions (channel, device, segment, audience, occasion, …) and how each
one is resolved from a request.

### 5.2 Structure

**Schema.** The registry of everything declared, and where it is stored.
- **What it declares:** domains, kinds, attributes, types, validation, defaults, sensitivity,
  required-ness and indexes, plus **composite kinds**. A composite kind is a named set of
  dimensions, each one a reference to a domain:

  | Composite | Dimensions |
  |---|---|
  | Shipping | Geo (a carrier's zone hierarchy), Measure (weight, size), Value (rates), Time (transit) |
  | Appointment | Geo (where, which supplies the clock and calendar), Time (availability, slots, recurrence), Party (who), Classification (which service) |
  | Price | Value, Geo, Time, Context, Classification |
  | Tax | Rule, Geo, Time, Classification, Party (buyer and seller status) |

  A Mars clinic therefore schedules in sols, because its place relates to the Darian calendar
  and a Mars clock.
- **Console:** add, edit, hide and delete any declaration through K9.
  - **Add** creates storage from the declaration.
  - **Edit** that would break existing data first shows what breaks and offers a conversion.
  - Every change is a versioned migration: previewed, applied live with background backfill,
    and reversible.
- **Storage adapters:** a domain's database is chosen per domain or per tenant: SQLite,
  PostgreSQL, document, graph or spatial stores.
  - Moving a domain between databases is a migration with preview and verification.
  - Credentials are held by Trust.
- **Guard rails:** kernel parts and Schema itself can be extended but not deleted. A tenant
  extends only within its scope.

**Relationship.** Every link between any two entities.
- **Relation types** declare:
  - the kinds they join;
  - cardinality;
  - inheritance down hierarchies;
  - attributes (primary, position, channel);
  - validity windows.
- **Edges** are owned at platform or tenant scope.

Examples: a place *uses* a currency, *follows* a clock, *speaks* languages, and *is governed by*
rules. A store *serves* places.

**Rule.** Every declared decision. Applicability (where, for whom, for what), eligibility,
pricing, tax rules, feature gates and policies are all rules.
- Rules scope by any dimension from any domain.
- Priority, allow, deny and prefer.
- Most specific wins, and deny wins ties.
- The platform owner's rules bound every tenant's rules.

**Party.** Everyone and everything that acts.
- Platforms, tenants and their hierarchy (organisation, business unit, brand, store, channel).
- Organisations, people, agents, providers.
- The roles a party plays: customer, seller, staff, carrier, partner.

**A customer is a Party in a role.** It is not a separate copy, so Commerce and Appointments
share one customer.

### 5.3 Assurance

**Trust.** Who may do what, and how data is protected.
- **Identity:** the complete list of sign-in methods:
  - email and password, passkeys (WebAuthn), OTP by SMS or email, magic link;
  - social sign-in (Google, Apple, Microsoft, Facebook, …), WhatsApp;
  - enterprise SSO (SAML, OIDC);
  - wallet, guest;
  - any method added.

  Also multi-factor authentication, and short-lived scoped credentials for agents and
  services.
- **Access:** role- and attribute-based, down to domain, kind, node, hierarchy, attribute and
  action. Deny by default. Tenant isolation. Just-in-time access for sensitive operations.
- **Keys and encryption:**
  - envelope encryption (AES-256-GCM) from a key hierarchy, with rotation and a keyring;
  - field-level encryption of every attribute Schema declares sensitive;
  - TLS everywhere;
  - a managed key service or HSM can be configured as an adapter.

  **Sensitive by default:** the coordinates and addresses of people and private sites. Public
  places are not.
- **Threat protection:**
  - abuse rate limits and lockout;
  - bot and fraud detection;
  - input validation driven by Schema;
  - a strict content security policy, with subresource integrity;
  - signed webhooks;
  - secrets scanning, dependency scanning.
- **Response:**
  - security alerts;
  - revoking any session or credential;
  - an incident runbook per incident type;
  - penetration tests before major releases.
- **Policy floor:** operators configure password, MFA, session and network policy, but only
  tighter than the platform baseline.

**Audit.** The immutable record of everything.
- **What is recorded:** every K8 event. That includes every data, configuration, schema, theme,
  workflow, agent, connector and security change, every sign-in, every read of sensitive data,
  every export and every approval.
- **Each record holds:** who, on whose behalf, which agent, when (valid and recorded time),
  where (place, network, device), what, before and after, why, and a correlation ID.
- **Integrity:**
  - append-only and hash-chained;
  - periodically sealed;
  - signed exports;
  - held in its own store, which no one can edit, not even the platform owner.
- **Investigation console:**
  - a timeline per entity, person or agent;
  - "who changed this" with diffs;
  - replay of agent decisions;
  - evidence packs for Compliance.
- **Retention and legal hold** follow Compliance. Sensitive values in the record are encrypted
  or redacted through Trust.

**Compliance.** Every obligation, and the evidence it is met.
- **Regulations catalogue:** GDPR, India's DPDP Act, CCPA, PCI DSS, SOC 2, ISO 27001, HIPAA,
  consumer law, tax e-invoicing, accessibility law, AI regulation, and any regulation added.
- **How a regulation works:**
  - each regulation lists its obligations;
  - each obligation maps to controls;
  - each control maps to the platform features, rules and gate tests that satisfy it;
  - applicability is a Rule (by place, industry, activity, size).
- **Evidence** is collected automatically from Audit, configuration and gate tests. Controls
  are monitored continuously, and attestations and certifications are tracked.
- **Privacy programme:**
  - records of processing and lawful basis;
  - **consent** (owned here; Communication and Notification honour it);
  - **data-subject requests:** access, correction, erasure, export, restriction, objection,
    each run as a Workflow;
  - **retention schedules and legal holds** (owned here; K9 enforces them);
  - **data-residency obligations** (owned here; Geo declares placement, Operations enforces it);
  - impact assessments;
  - the register of processors (every connector and provider);
  - breach notification, together with Trust's incident response.

### 5.4 Interaction

**Experience.** Everything people see and touch.
- **Device types** are kinds:
  - phone, tablet, desktop, TV, watch, wearables;
  - kiosk, point of sale, in-car, voice assistant, AR/VR headset;
  - print, email rendering;
  - any type added.

  Each declares its screen range, inputs (touch, pointer, keys, remote, voice, gaze),
  orientation and offline support. Layouts adapt from those declarations.
- **Design tokens:** colour, type, spacing, radius, elevation, motion and iconography, each
  with light, dark and high-contrast values. **Themes** are named sets of tokens.
- **A component registry,** where each component declares its properties, the data it binds to
  and the devices it supports.
- **Screens and layouts, navigation and menus.**
- **Forms and lists,** rendered from Schema, so a new field appears on screen with no work.
- **Sites:** web domains, certificates, SEO and sitemaps.
- **Scope:** anything at any K10 scope. For example, a festival theme for India only, or a kiosk
  layout for one mall. Text direction comes from Language.
- **Guard rails:**
  - registry components only, so operators never inject scripts and the content security
    policy holds;
  - custom CSS is sanitised;
  - every theme passes an accessibility check (WCAG contrast, focus, text size) before it can
    publish;
  - performance budgets per device type.

**Communication.** Every exchange of messages with people.
- **Channels:** email, SMS, RCS, WhatsApp and other chat apps, push, in-app, voice and IVR,
  video, social messaging, postal mail, and any channel added. Each channel is served by
  providers through Integration, with routing per place and fallbacks.
- **Messages:** one-way and two-way, and **conversations:** threads across channels, a shared
  inbox, routing and assignment (through Workflow), live chat, calls.
- **Agent handling:** agents can handle conversations, with handoff to a person.
- **Templates:** per purpose, channel and language, with variables from Schema, previewed per
  device through Experience.
- **Sender identities:** numbers, sender IDs, email domains with SPF, DKIM and DMARC.
- **Delivery:** sent, delivered, read, failed, bounced, with retries, channel fallback and
  delivery reports.
- **Attachments** through Content. Recording and retention through Compliance.

**Notification.** Deciding who is told what, and when. Notification sends through
Communication and owns no channel, template or delivery of its own.
- **Subscriptions:** which K8 events notify which recipients. A recipient can be a person, a
  role, a group, a segment, or a party resolved from the entity, such as "the order's buyer" or
  "the store's fulfilment staff".
- **Recipient preferences:** channel and frequency per topic, honouring Compliance consent.
  Transactional and marketing messages are kept apart.
- **Timing:** quiet hours in the recipient's own clock (Time), digests, batching, rate per
  recipient, declared urgent overrides.

**Search.** Finding anything.
- Indexes declared per kind, synonyms, boosts and ranking rules, facets from Schema.
- Search in every language, and by place, including "near this coordinate" through K5.
- Results are permission-filtered through Trust.

**Knowledge.** The user manual and all help, generated from declarations.
- Domains, kinds, blueprints, packages, workflows and API contracts produce their own manual
  pages, in every language, kept current by K8.
- Authors add guides, tutorials and a glossary.
- Agents read the same Knowledge, so a layman and an agent follow the same instructions.

### 5.5 Automation

**Workflow.** What happens, in what order, and who does it.
- **Triggers:** K8 events, schedules and deadlines (Time), thresholds (stock low, payment
  overdue), manual starts, agent decisions, inbound webhooks.
- **Steps:**
  - set data;
  - move a state machine;
  - call a connector;
  - assign a task to a person, resolved from roles and places;
  - ask an agent;
  - wait;
  - notify;
  - start another workflow.
- **Control:** conditions (Rule), branches, parallel paths, loops over collections, single or
  multi-level approvals, timeouts and escalation, retries, compensation (undoing earlier steps
  when a later one fails).
- **State machines** are Workflow's own: each declares states, legal moves, meanings (tags) and
  effects.
- **Service levels** are measured in the place's clock and business calendar (Time).
- **Console:**
  - a visual designer, with simulation on sample data;
  - live instances you can watch, pause, resume, retry or cancel.

  Jobs and schedules run here, on Operations' queue.

**Agent.** AI that acts on the platform.
- **What an agent can do:** anything the console can do, through the same API, within its
  permissions. That includes:
  - configure a launch;
  - extend the schema;
  - write content and translations;
  - answer customers;
  - reconcile payments;
  - watch for fraud;
  - run reports;
  - follow Knowledge on an operator's behalf.

  There is no private agent back door.
- **Agents:** purpose, instructions, scope, trigger, the party they act for, and a budget
  (spend, calls, rate, time) with alerts and a hard stop.
- **Models and providers:** a registry, with routing by task, place and plan, and fallbacks.
- **Tools:** every API operation is a tool, generated from Integration's contract, with its
  input schema, its permission and its risk level (read, change, money, irreversible).
  Operators choose each agent's tools.
- **Approval rules:** by risk level, amount, scope or confidence. They decide what an agent
  does alone, what it proposes, and what it may never do.
- **Safety:**
  - effective permissions are the intersection of the agent's own grant and its principal's;
  - untrusted content (messages, documents, pages) is data, never instructions, which protects
    against prompt injection;
  - every change is previewed through K9;
  - sensitive data reaches only models approved for it in that region, and is redacted
    otherwise;
  - a kill switch pauses one agent or all of them.
- **Evaluation:** declared test sets must pass before a model or instruction change publishes.
  Every step is recorded by Audit (input, tools, output, model, cost, approver), and decisions
  can be replayed.

**Integration.** The platform's API and every outside connection.
- **The platform API** is generated from Schema:
  - endpoints for every declaration (create, read, update, hide, archive, query, bulk);
  - REST and GraphQL over the same model;
  - bulk import and export;
  - event streams over K8 (webhooks, server-sent events, WebSocket, queues);
  - query endpoints for Insight.

  Adding a field in the console adds it to the API.
- **Contracts:**
  - OpenAPI and GraphQL schemas per version, documented through Knowledge, with a sandbox;
  - generated SDKs;
  - versioning with declared deprecation; nothing breaks silently.
- **Reliability:** idempotency keys, schema-declared pagination and filters, optimistic
  concurrency, quotas (commercial limits are set in Offering), translated errors.
- **Access:** keys and OAuth clients are scoped through Trust, and partners sign requests.
- **Connectors are data.** Each declares its protocol, authentication, endpoints and its
  mapping onto entities.
  - **Protocols:** REST, GraphQL, SOAP, gRPC, webhooks, files (CSV, XML, JSON, EDI over SFTP or
    cloud storage), queues and streams, database replication, email in, and any protocol added.
  - **Every provider is a connector:** payment, shipping, tax, identity, AI, marketing, ERP,
    accounting, CRM, marketplace, bank, government, IoT, and other LUXORA platforms.
    Communication's channel providers are connectors too.
- **Data flow:**
  - **Direction and timing:** inbound, outbound or both, in real time, scheduled, or triggered
    by a Workflow.
  - **Mapping:** a visual mapper. Values convert through Measure, Value, Time and the domains'
    identifier schemes.
  - **Sync:** incremental with checkpoints, per-field conflict rules, de-duplication by
    identifiers, replay of a time window.
  - **Reliability:** back-off retries, a dead-letter queue (inspect and resend from the
    console), circuit breakers, inbound signature checks, health per connection.
  - **Security:** outbound calls go to declared hosts only. Sensitive data leaves only to
    connectors approved for it in that region. Calls are logged with secrets redacted.
- **Console:**
  - the integration catalogue: connect, test, map, schedule, monitor, disconnect;
  - a connector builder that can import an OpenAPI file;
  - keys and apps: create, scope, rotate, revoke, see usage;
  - webhook subscriptions with delivery logs and resend;
  - monitoring.

### 5.6 Intelligence

**Insight.** Every measurement of the platform and the business.
- **Semantic layer:** metrics declare a formula, a unit (Measure or Value), an aggregation and
  an owner. Dimensions come straight from the domains, so a new attribute becomes a dimension
  automatically. One definition of each metric serves every consumer, so two screens never
  disagree.
- **Correctness:**
  - money in any unit of value, converted at the dated rate or a chosen rate, with the method
    stated;
  - periods in any calendar, including fiscal years and sols;
  - history as known then, or as known now (K7).
- **Builders:**
  - reports (tables, pivots, drill-down to records);
  - dashboards from a widget registry at any K10 scope;
  - charts, maps from Geo shapes, timelines;
  - funnels, cohorts, retention, attribution;
  - **experiments** (A/B tests).
- **Delivery:** scheduled through Notification, exports (CSV, spreadsheet, PDF, signed
  extracts), embedded in any screen.
- **Alerts:** a threshold or anomaly on any metric can notify, start a Workflow or wake an
  Agent. For example, "stock cover below 3 days in Patna" starts a replenishment workflow.
- **Intelligence:** forecasts, anomaly detection, segmentation, what-if simulation. Agents ask
  plain-language questions through the semantic layer and show the query they ran.
- **Privacy:** row and column access through Trust, masking of sensitive values, and
  suppression of small groups.
- **Scale:** queries run on a separate analytical store fed from K8, so reporting never slows
  checkout. Pre-aggregations are declared per metric, and the store uses a Schema storage
  adapter.

### 5.7 Platform

**Content.** Files and media for any entity.
- Images, video, audio, documents, 3D and AR assets.
- Storage adapters, a CDN, image and video transforms.
- Malware scanning.
- Sensitivity and retention declared per kind (Trust, Compliance).

**Offering.** Everything LUXORA sells, and to whom.
- **Every option has an offering:** free, paid, metered, trial or included in a plan, priced in
  any unit of value. Options include sign-in methods, connectors, agents, themes, packages,
  domain catalogues and their hierarchies, depth and regions, update feeds, API usage and
  seats.
- **Plans, subscriptions, trials, metering** (fed from K8), and **quotas** (enforced by
  Integration).
- **The platform's own invoices,** credit notes and dunning.
- **Licences:** a subscription is a K10 view with a licence attached, so a subscriber reads
  only what it paid for.
- **Publishing:** domain catalogues, which LUXORA itself also consumes, and packages are
  published to other platforms.
- **Billing preview:** a configuring platform's bill is the sum of its selections.

**Operations.** Running the platform.
- **Environments** (development, staging, production, any number), with feature flags for
  rollout.
- **Deployments, regions** and data placement (enforcing Geo and Compliance).
- **Runtime adapters:** cache, queue, object storage, session store.
- **Backups and restores:** encrypted and verified, with disaster recovery.
- **Health, logs, traces and request metrics,** feeding Insight.
- **Scaling and incident operations,** with security incidents handled together with Trust.

**Package.** Defined in §7.

### 5.8 Business entities

Built on the kernel from the domains above, and composed by packages:
- Product, Catalogue, Cart, Order, Payment, Invoice, Fulfilment, Shipment, Inventory, Warehouse;
- Offer and Promotion, Review, Asset, Ticket, Ride, Vehicle, Rate card;
- any number more.

Each is finalised in the same detail, on the same kernel, once the domains are built. Rules that
keep them clean:
- **Customer and Seller are Party roles,** not entities of their own.
- **A support ticket is a Communication conversation plus a Workflow,** not a separate inbox.
- **A business event** (an order placed, a ride completed) is a K8 event, not an entity.

## 6. Configuring by selection

Every question a setup asks is answered from the entity that owns the subject. The answer is
stored as relationships (constitution 7).

**How every option list works:**
1. **Source:** the nodes of the owning domain. The sign-in dropdown, for example, lists
   Trust's sign-in methods.
2. **Combination:** single, multiple, ordered (primary and fallbacks), or grouped by audience
   (shoppers, sellers, staff), channel, device or place. Any combination is valid unless an
   entity declares a constraint.
3. **Constraints:** declared by the entities, never by the flow:
   - **requires:** WhatsApp OTP needs a WhatsApp connector;
   - **excludes:** guest sign-in cannot be the only method for staff;
   - **prerequisites:** SSO needs an identity provider;
   - **availability:** decided by Rule, by place, plan, segment or date.
4. **Offering:** every option shows its free or paid terms (Offering).
5. **Incomplete is visible:** a missing credential, provider or translation is shown and
   linked, never defaulted.

**Blueprints are data.** Each package (§7) brings a blueprint that declares only the questions it
cannot answer itself, in order, with the owning domain of each answer. The console renders it,
and an agent walks the same blueprint through the API.

**Example: an e-commerce platform from scratch.**

| Step | Question | Answered from |
|---|---|---|
| 1 | Which packages? | Package: Commerce, Marketplace, Quick commerce, … Most later steps arrive pre-filled and editable |
| 2 | Which industries and segments? | Classification |
| 3 | Where will it operate? | Geo, at any level, in any hierarchy |
| 4 | Which languages? | Language (inherited from the places) |
| 5 | Which currencies and units of value? | Value (inherited from the places) |
| 6 | Which clocks and calendars? | Time (inherited from the places) |
| 7 | How do people sign in, per audience? | Trust: sign-in methods, any mix |
| 8 | Which payment methods and gateways? | Integration connectors available in the places (Rule) |
| 9 | Which carriers and delivery options? | Integration connectors and Geo carrier zones |
| 10 | Which tax regimes and obligations? | Rule (tax) and Compliance (regulations), for the places |
| 11 | Which channels, messages and notifications? | Communication and Notification: the package's defaults, edited |
| 12 | Which workflows? | Workflow: the package's defaults, edited |
| 13 | Which look, on which devices, at which web domains? | Experience |
| 14 | Which AI agents, with what limits? | Agent |
| 15 | Which reports, dashboards and alerts? | Insight |
| 16 | Which outside systems and API access? | Integration |
| 17 | Which plan? | Offering: everything selected, totalled |

Every step allows any combination. A review lists anything incomplete before go-live. The same
mechanism configures a store inside a platform, a launch in a new place, a service, or an agent.

## 7. Packages

There can be any number of entities. A package makes configuring them fast. It is itself an
entity on the kernel, so it is versioned, audited and published through K9.

- **What a package contains:**
  - **Entities,** marked mandatory or optional. Commerce, for example, needs Product,
    Catalogue, Cart, Order, Payment, Invoice and Fulfilment, plus Party roles for customers.
    Reviews, wishlists, gift cards and subscriptions are optional.
  - **Relationships** between those entities.
  - **Starting selections** from every domain.
  - **Workflows** and **state machines.**
  - **Communication templates** and **notification subscriptions.**
  - **Screens and themes.**
  - **Agents,** for example a catalogue writer, a support agent, a fraud watcher.
  - **Reports and dashboards,** with their metrics and alerts.
  - **Connectors.**
  - **A blueprint** (§6).
  - **Offerings,** for the package and each optional part.
- **Composition.**
  - Packages include packages. Marketplace is Commerce plus Sellers, Commission and Payouts.
    Quick commerce is Commerce plus Dark stores, Slots and Riders. Marketing is Workflow
    journeys plus Notification, Communication and Insight.
  - Installing several packages merges their shared entities instead of duplicating them.
- **Customisation without forking.**
  - A platform's or store's changes are an **overlay** on the installed package version: added
    entities, changed selections, edited workflows, hidden parts.
  - On upgrade, the overlay is re-applied, and conflicts are shown for a person or agent to
    resolve.
  - A mandatory entity can be extended or hidden from screens, but not removed. The console
    explains why.
- **Building packages.**
  - Operators build packages in the console from existing entities.
  - Any live platform can be saved as a package.
  - Packages are sold through Offering.
- **Speed:** configuring e-commerce is "install Commerce, answer its blueprint". Typically that
  means places, languages, sign-in methods, payment methods and a theme.

## 8. Coverage: one owner per concern

Every concern, and its single owner. A concern listed twice, or missing, fails the gate (§10).

| Concern | Owner |
|---|---|
| Kinds, nodes, hierarchies, identifiers, shapes, attributes | K1–K6 |
| Versions and history | K7 |
| Events (the single event log) | K8 |
| Draft, preview, publish, rollback, hide, archive, purge | K9 |
| Views, namespaces, scopes | K10 |
| Settings, defaults, inheritance, "what applies here" | K11 |
| Places, coordinates, address formats, data placement | Geo |
| Calendars, clocks, zones, business hours, holidays, recurrence, signal delay | Time |
| Units and conversions | Measure |
| Currencies, units of value, exchange rates | Value |
| Languages, direction, interface text, translations, multilingual names | Language |
| Industries, segments, taxonomies | Classification |
| Request dimensions | Context |
| Fields, types, validation, composite kinds, migrations, databases | Schema |
| Links between entities | Relationship |
| Applicability, eligibility, pricing rules, tax rules, feature gates, policies | Rule |
| Platforms, tenants, organisations, people, agents' identity records, providers, roles (including customer and seller) | Party |
| Sign-in methods, MFA, credentials, permissions, keys, encryption, threat protection, security incidents, penetration tests | Trust |
| The immutable record, investigations, evidence packs | Audit |
| Regulations, controls, evidence, consent, data-subject requests, retention, legal holds, residency obligations, processor register | Compliance |
| Devices, tokens, themes, components, screens, navigation, forms, sites, web domains, SEO | Experience |
| Channels, messages, conversations, inbox, templates, sender identities, delivery | Communication |
| Who is told what and when, preferences, quiet hours, digests | Notification |
| Indexes, ranking, synonyms, facets | Search |
| User manual, help, guides, glossary | Knowledge |
| Workflows, state machines, tasks, approvals, schedules, jobs, service levels | Workflow |
| Agents, models, tools, approval rules, budgets, evaluation | Agent |
| The API, contracts, SDKs, keys and apps, connectors, mapping, sync, webhooks, idempotency | Integration |
| Metrics, dimensions, reports, dashboards, alerts, forecasts, experiments | Insight |
| Files and media | Content |
| Plans, offerings, metering, platform invoices, licences, publishing, quotas | Offering |
| Environments, feature flags, deployments, regions, runtime adapters, backups, health, logs, traces | Operations |
| Ready-made compositions, overlays, blueprints | Package |
| Products, orders, payments and other business records | Business entities (§5.8) |

## 9. Coverage: every existing module has one home

Every file in `lib/`, `public/js/`, `public/docs/` and `scripts/` today, and the single owner that
absorbs it. Where today's code holds duplicates, they consolidate into the one owner.

| Today | Home | Consolidation |
|---|---|---|
| `entity.js`, `meta.js`, `parity-registries.js`, `registry.js`, `global.js`, `canonical.js`, `ucos.js`, `ucos-registry.js`, `ucos-foundations.js`, `ucos-universes.js`, `ucos-domain.js`, `ucos-catalog.js`, `ucos-completeness.js` | Schema | Five registry sets become one schema registry |
| `uid.js` | K4 | |
| `events.js` | K8 (the event log); its outbound webhooks move to Integration | One event log |
| `governance.js` | K9 (archive, restore, purge); retention policy from Compliance | |
| `defaults.js`, `settings.js` | K11 | Defaults and settings become resolver answers |
| `ucos-trace.js` | Audit | |
| `ucos-monitor.js` | Operations | |
| `subdivisions.js`, the country tables, GOIP spatial systems | Geo | GOIP's private spatial domain merges into Geo |
| GOIP calendars and chronologies | Time | Merges into Time |
| GOIP temporal units, `uomUnits` | Measure | Merges into Measure |
| the currency tables, `fx_rates`, GOIP economic units | Value | Merges into Value |
| `localizations` | Language | |
| GOIP context dimensions | Context | Merges with the rules engine's dimensions |
| `rules.js`, `policies.js`, `gates.js`, `tax.js` (its rules) | Rule | Policies and gates become rules |
| `tenancy.js` | Party | |
| `providers.js` | Party (providers) and Integration (their connectors) | |
| `security.js`, `identity.js`, `webauthn.js`, `authz.js`, `rbac.js`, `prbac.js`, `risk.js` | Trust | Three authorisation entry points become one |
| the audit tables, the audit chain in `security.js` | Audit | |
| `compliance.js` | Compliance | |
| `themes.js`, `branding.js`, `bundle.js`, `sitemap.js`, `public/js/admin.js`, `app.js`, `console.js`, `platform.js`, `data.js`, `editors.js`, `provisioning.js`, `rules-ui.js` | Experience | Branding and themes merge; hand-written screens become configured screens and registry components |
| `mailer.js`, `helpdesk.js` (conversations), the notification provider specs and transports | Communication | Channels and transports become Communication channels, served through Integration connectors |
| `search.js` | Search | |
| `public/docs/*` (user manual, references, guides) | Knowledge | Generated from declarations |
| `states.js`, `queue.js` (job semantics) | Workflow | |
| `ai.js` | Agent | |
| `api.js`, `spec.js`, `connect.js`, `idempotency.js` | Integration | Hand-written routes are replaced by the generated API |
| `dashboards.js`, `experiments.js`, `planning.js` (forecasts), GOIP intelligence | Insight | |
| media handling in `ugc.js` and products | Content | |
| `billing.js` (platform subscriptions and metering), `modules.js`, `capabilities.js` | Offering | The capability marketplace becomes offerings |
| `billing.js` (customer invoices, credit notes, dunning) | Business entity Invoice | |
| `env.js`, `config.js`, `adapters.js`, `enterprise.js`, `logger.js`, `metrics.js`, `queue.js` (runtime), `scripts/backup.js`, `scripts/restore.js` | Operations | |
| `db.js`, `dbpool.js`, `sql.js`, `pg.js`, `pgbridge.js`, `pgworker.js`, `migrate.js`, `scripts/schema-dump.js` | Schema (storage adapters) | A PostgreSQL client and migrator already exist and become the PostgreSQL adapter |
| `compose.js`, deploy modes, capability blends | Package | |
| `offers.js`, `goip.js` (its offers engine) | Business entities Offer and Promotion, in an Incentives package | GOIP keeps its offer logic and gives up its private domains |
| `shipping.js`, `logistics.js` | Business entities Shipment and Fulfilment | |
| `fin.js`, `fintech.js` | Business entities Payment, Payout and Dispute; a Financial services package | |
| `marketplace.js`, `marketplace-ext.js`, `affiliate.js`, `trade.js`, `qcommerce.js`, `mobility.js`, `operations.js`, `recurring.js`, `ugc.js`, `gcatalog.js` | Their business entities and packages: Marketplace, Affiliate, B2B trade, Quick commerce, Mobility, Operations, Subscriptions, Reviews, Catalogue | |
| `scripts/audit-hardcoding.js`, `scripts/audit-baseline.json`, `scripts/browser-check.js` | Gate tests (§10) | |

## 10. Gate tests

Each constitutional rule is held by a test in `npm test`, and the build fails if any of them
fails. The tests check that:

1. **No code fixes a configurable value:** domain values, places, calendars, currencies,
   languages, tables, fields, screens, colours, devices, workflows, messages, reports or
   integrations. (This extends today's hard-coding ratchet.)
2. **No master table carries another domain's column,** and no entity embeds another domain's
   data.
3. **No engine reads around the resolver,** and no setting is stored twice.
4. **No concern is owned twice or not at all.** §8 is checked against the schema registry's
   domain declarations.
5. **Every domain has every kernel part and shared service** (§3). No domain is partial.
6. **No module is unplaced.** Every file under `lib/`, `public/js/`, `public/docs/` and
   `scripts/` appears in §9.
7. **Every endpoint, tool and agent action declares a permission.** No secret, key or sensitive
   value is stored or logged in clear text.
8. **Every change emits an event,** and Audit's hash chain verifies.
9. **Every option list comes from an owning domain,** and every option has an offering.
10. **Every theme passes accessibility checks,** and every screen renders on every declared
    device type (extending today's browser check).
11. **Every API change is either compatible or a new version.**

## 11. The path

Each step is committed only once the full test suite passes. Today's data is migrated, not
discarded, so existing stores behave the same throughout. Each step adds its gate tests.

1. **Kernel, Schema, Relationship, Trust and Audit.**
   - K1–K11.
   - The schema registry, migrations, and storage adapters (SQLite, then the existing
     PostgreSQL client).
   - Relation types and edges.
   - The resolver.
   - Trust's permissions and field encryption, and Audit's record, from the start.
   - The console's schema screens.
   - The five registry sets consolidate.
2. **Geo,** with GOIP's spatial domain merged in. Countries and subdivisions migrate, and their
   embedded currency, locale and tax columns become relationships.
3. **Measure and Value,** with GOIP's units merged in.
4. **Time,** with GOIP's calendars merged in.
5. **Language,** and message catalogues for the interface.
6. **Classification, Context, Party and Rule** move onto the kernel. Policies and gates become
   rules, and the three authorisation entry points become one.
7. **Compliance:** regulations, controls, evidence, consent, data-subject requests, retention.
8. **Experience,** with themes and branding merged, plus screens from configuration.
9. **Communication and Notification,** built on today's mailer, helpdesk and providers.
10. **Workflow,** built on today's state machines.
11. **Search, Content and Knowledge.** The user manual is generated.
12. **Integration:** the generated API, connectors, mapping and webhooks, built on today's spec
    engine.
13. **Insight,** built on today's dashboards and experiments.
14. **Agent,** built on today's AI layer.
15. **Offering and Package.** Configuring by selection, blueprints, overlays, and the first
    packages from today's platform kinds.
16. **Operations,** with today's environments, adapters, logging and backups consolidated.
17. **Business entities** move onto the kernel, package by package. Engines read the resolver,
    and stores lose their single country and currency settings.
18. **Launch by configuration, end to end,** for a person with the manual and for an agent.
19. **More storage adapters,** and moving domains between databases from the console.

## 12. Decisions taken

| Question | Decision |
|---|---|
| One tree or several hierarchies? | Several named hierarchies over shared nodes (K3) |
| How much real data ships? | The core down to first-level regions; deeper levels imported on demand from declared sources |
| What is sold to other platforms? | A mix: domains, hierarchies, depth, regions, update feeds, API usage, packages and connectors, all through Offering |
| What is sensitive by default? | Coordinates and addresses of people and private sites; public places are not |
| Can the database and schema change without code? | Yes, through Schema and K9. Delete is archive first, then purge with separate permission |
| Can the interface change without code? | Yes, through Experience, on every declared device type |
| How do agents work? | As bounded Parties using only the public API, with approvals, budgets, a kill switch and Audit |
| When is security built? | From step 1, inside the kernel; policy can only tighten |
| Where do configuration choices come from? | The owning entity, in any combination, with declared constraints and an offering per option |
| How are workflows, communication and notifications split? | Workflow decides what happens. Notification decides who is told and when. Communication owns channels, templates, conversations and delivery |
| How are audit and compliance split? | Audit owns the immutable record. Compliance owns obligations, controls, evidence, consent, data-subject requests and retention. Trust owns the security controls |
| How is configuration made fast? | Packages: editable compositions, with overlays that survive upgrades |
| How do reports and integrations work? | Insight: one semantic layer over the domains. Integration: an API generated from Schema, and connectors as data |
| How is "zero duplication, partial, missing, gap" guaranteed? | One owner per concern (§8), one home per module (§9), every domain built on one kernel (§3), each held by a gate test (§10) |
| Which domains are finalised now? | All of §5. Business entities (§5.8) follow, on the same kernel |
