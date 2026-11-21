---

# PART III — MASTER ARCHITECTURE

## {{§§diagram}} Master Architecture Diagram

{{MASTER_DIAGRAM}}

How to read the diagram:

- **Applications** sit on top and contain no code.
- The **Meta-System** composes, generates, proves, certifies and evolves them, reading every universe through its genome.
- The **six left-hand planes** hold the capability universes.
- **Cross-cutting control** (planes G and T) is enforced on every call through the Runtime Fabric (rule D3).
- **Runtime & Operations** executes everything.
- The **Kernel** is the language that every universe is written in.

## {{§§register}} Universe Register

{{REGISTER}}

## {{§§tiers}} Dependency Tiers

```text
 TIER M  META-SYSTEM ── generic over the meta-model; reads every genome via Registry ──┐
                                                                                        │ operates on
 TIER 3  BUSINESS DOMAINS          (Commerce · Money · Supply · People & Work · Customer)│ every tier
            │  depends on                                                               │
            ▼                                                                           │
 TIER 2  CORE SERVICES             (generic engines over metadata + shared services)    │
            │                                                                           │
            ▼                                                                           │
 TIER 1  FOUNDATION & CONTROL      (where · language · units · parties · law · trust)   │
            │                                                                           │
            ▼                                                                           │
 TIER 0  KERNEL                    (registry · identity · tenancy · security · policy ◄─┘
                                    governance · audit · time · event · knowledge ·
                                    runtime · infrastructure)
```

The dependency tier of each universe is listed in the register ({{§register}}). Rules D1–D7 ({{§rules}}) govern every edge. Within Tier 3, business universes **never orchestrate one another**. They reference each other only by UGID and by events. Every cross-domain process (order-to-cash, procure-to-pay, hire-to-retire, …) is a composed Workflow ({{Composition}}).

---

# PART IV — UNIVERSE SPECIFICATIONS

Every entry gives the universe's **mandate** and what it **owns** (canonical objects and concepts). Where the boundary was contested in the sources, the entry also lists what it **provides** (capabilities) and its **boundary** (concepts it does *not* own, and who does). The full specification of each universe is its genome-complete bundle ({{§genome}}, Appendix D). A concept appears in exactly one universe's "Owns" list. Appendix A indexes all of them.

## {{§§planeG}} Plane G — Governance

### {{#Constitution & Law}}

**Mandate:** The supreme rules of UCOS and the only process that can change them.

- **Owns:** the Universal Constitution · universe constitutions · constitutional laws ({{§laws}}) and universe laws · principles · internal standards (architecture, naming, schema, API, security baselines, and coding standards for engines, generators and adapters) · meta-type definitions ({{§object}}) · amendment proposals and amendments · constitutional interpretations · ethical frameworks.
- **Provides:** the amendment process (proposal → impact analysis via {{Evolution}} → simulation via {{Simulation}} → ratification via {{Authority & Governance}} → versioned law) · law retirement · constitutional conformance rules, which {{Platform Intelligence}} consumes.
- **Boundary:** who may ratify → {{Authority & Governance}} · operational policy → {{Policy}} · external statutes and standards → {{Compliance}}.

### {{#Authority & Governance}}

**Mandate:** Who may decide, approve, delegate and own, for every object and every action.

- **Owns:** Authority, in six types: *Foundational* (constitution and laws), *Governance* (policies, approvals, certifications), *Administrative* (configuration, operations), *Domain* (domain-specific governance), *Operational* (runtime execution) and *Autonomous* (AI agents and automation, bounded by risk limits). Also: delegation (including delegation to agents) · ownership, custodianship and stewardship of artifacts · accountability · approval authority and approval records · ratification · reviews · change control · revocation · governance escalation · separation of duties · multi-party approval · ethics reviews · the governance-decision registry · the Autonomy Model ({{§autonomy}}).
- **Core schema:** `Authority { ugid, type, scope, level, holder, constraints, effective (Temporal), delegation_rules, revocation_rules, evidence, audit }`
- **Provides:** authority resolution ("can X approve Y in context C?") · delegation chains · quorum approval · governance automation and auto-governance recommendations.
- **Boundary:** executing an approval step → {{Workflow}} · enforcing access → {{Security}} · policy content → {{Policy}}.

### {{#Policy}}

**Mandate:** Every declarative constraint — what is allowed, required, forbidden or obligated — authored once and enforced everywhere. Pricing guardrails, approvals, compliance, security, AI behaviour and tax applicability are all policy-driven.

- **Owns:** Policy · Rule · Constraint · Exception and Waiver · policy sets · policy composition · policy conflict detection and resolution · policy languages · policy enforcement modes (enforce · advise · simulate) · policy obligations (side-effects on enforcement, such as *log* or *notify*).
- **Typed policies:** {{Policy}} owns the mechanism and the generic object. The *semantics* of each typed policy belong to its universe. Examples: Temporal Policy ({{Temporal}}), Retention Policy ({{Privacy & Consent}}), Access Policy ({{Security}}), Pricing Policy ({{Pricing}}), Eligibility Policy ({{Offer & Incentive}}).
- **Core schema:** `Policy { ugid, type, scope, rules[], enforcement_mode, exceptions[], compliance_mapping, temporal_ref, authority_ref, audit }`
- **Boundary:** choosing an option (rather than constraining it) → {{Decision}} · regulation text → {{Compliance}} · evaluation runtime → {{Runtime Fabric}}.

### {{#Legal & Agreement}}

**Mandate:** Binding agreements between parties, and the rights, obligations and disputes that follow from them.

- **Owns:** Contract · Agreement · Terms (ToS, MSA, DPA, …) · clause library · Obligation, including SLA commitments · Liability · contractual Rights · Legal Hold · Dispute · generic legal Claim · Investigation · Arbitration · Appeal · Resolution.
- **Provides:** the contract lifecycle (draft → negotiate → sign → execute → renew → terminate) · obligation tracking · automated resolution assistance · legal-hold enforcement, which blocks deletion in {{Data}} and {{Privacy & Consent}}.
- **Boundary:** chargeback money flow → {{Payment}} · negotiation mechanism → {{Marketplace & Distribution}} · consent → {{Privacy & Consent}} · statutes → {{Compliance}} · case engine → {{Workflow}} · signatures → {{Trust & Reputation}}.

### {{#Compliance}}

**Mandate:** Maps every external regulation and standard to controls, evidence and continuous conformance.

- **Owns:** Regulation registry · external-standard registry · Jurisdiction registry (jurisdictions bound to regions in {{Spatial}}) · compliance ontology and compliance knowledge graph (hosted on {{Knowledge}}) · Control library · Control mapping (regulation ↔ control ↔ capability) · compliance profiles and templates · compliance scoring · **constraint intelligence**, i.e. applicability (for example Germany ⇒ GDPR, India ⇒ DPDP, Brazil ⇒ LGPD).
- **Regulation packs** are content, not architecture: GDPR, CCPA, DPDP, LGPD, HIPAA, PCI-DSS, SOC 2, ISO 27001, ISO 42001, NIST, FedRAMP, DORA, PSD2, Open Banking, FINRA, MiFID, SEBI, RBI, TRAI, FDA, EMA, plus country, industry, custom and future regulations. Tax-law packs (GST, VAT) belong to {{Tax}}.
- **Modes:** compliance-as-metadata · compliance-as-code · compliance-as-policy · compliance-by-construction.
- **Provides:** auto-discovery of applicable regulations · compliance-gap signals to {{Platform Intelligence}} · auto-generated controls (via {{Generation}}) · evidence collection and validation (with {{Audit & Evidence}}) · continuous compliance monitoring · compliance simulation (via {{Simulation}}) · audit-package preparation · regulatory-change tracking (with {{Evolution}}).
- **Boundary:** issuing certificates → {{Certification}} · privacy semantics → {{Privacy & Consent}}.

### {{#Privacy & Consent}}

**Mandate:** Lawful, purposeful and minimal use of personal data across every universe.

- **Owns:** Consent (registry, receipts, withdrawal) · Purpose registry · lawful basis · data-usage registry · minimization rules · Retention policies and schedules · deletion and erasure registry · data-subject rights (access, portability, rectification, erasure, objection) · privacy policies and notices · personal-data classification · cross-jurisdiction privacy resolution · consent intelligence.
- **Boundary:** residency → {{Sovereignty & Residency}} · encryption and masking → {{Security}} · retention clocks → {{Temporal}} · physical deletion → {{Data}}.

### {{#Sovereignty & Residency}}

**Mandate:** Where data, compute, models and authority may reside, and who controls them.

- **Owns:** sovereignty domains (tenant, organization, data, AI/model, digital, national) · residency rules · placement constraints · cross-border transfer rules · export-control constraints · sovereign key-custody requirements · sovereign-cloud profiles.
- **Boundary:** placement execution → {{Infrastructure}} · law → {{Compliance}} · key mechanics → {{Security}}.

## {{§§planeT}} Plane T — Protection & Trust

### {{#Security}}

**Mandate:** Zero-trust protection of every identity, object, interaction, runtime and supply chain. Nothing bypasses it (L7).

- **Principles:** zero trust · identity first · policy first · encryption first · least privilege · separation of duties · continuous verification · security by design, by default, by constitution, by runtime, by AI and by evolution.
- **Owns:**
  - *Access control:* authorization decisions · RBAC, ABAC, PBAC, ReBAC, ZBAC, context-based and risk-based access · access roles and permissions · PAM · session security · device and network trust · ZTNA · CASB.
  - *Cryptography:* encryption at rest, in transit and in use · field-level and object-level encryption · confidential computing · tokenization · masking · KMS · HSM · PKI and certificates · secrets management · post-quantum readiness · crypto-agility.
  - *Threat and vulnerability:* threat modeling, discovery, prediction, correlation, intelligence and hunting · vulnerability and dependency scanning · attack-surface discovery · secret and credential leak discovery · supply-chain security (SBOM, signing, provenance verification) · malware · insider threat · behavioural security analytics · DLP.
  - *Security operations:* SIEM · SOAR · SOC · EDR · XDR · incident response · forensics · continuous penetration validation · autonomous remediation (detect → classify → prioritize → mitigate → isolate → recover → verify → certify, within {{§autonomy}}).
  - *Coverage areas* (applied to every universe's genome slot E): identity, application, API, data, database, network, runtime, container, Kubernetes, cloud, infrastructure, AI, model, agent, supply chain, human and operational, cyber-physical, quantum.
- **Boundary:** authentication and credentials → {{Identity}} · business fraud → {{Risk}} · attestations and signatures → {{Trust & Reputation}} · attack-simulation runs → {{Simulation}} (the scenario packs are authored here) · privacy semantics → {{Privacy & Consent}}.

### {{#Trust & Reputation}}

**Mandate:** Makes trust measurable and verifiable for every subject.

- **Owns:** trust registry and trust scores (entity, user, organization, seller, buyer, supplier, partner, product, content, transaction, marketplace, model, agent, capability) · reputation · ratings and reviews · credibility · verification and validation of claims · KYC, KYB and identity proofing · verifiable credentials and credential chains · attestation · digital signatures, proof and non-repudiation · authenticity and integrity proofs · provenance attestation · content moderation · confidence models.
- **Boundary:** identity issuance → {{Identity}} · cryptographic primitives → {{Security}} · risk scoring → {{Risk}} (trust is one of its inputs) · conformance certificates → {{Certification}}.

### {{#Risk}}

**Mandate:** Identifies, quantifies and bounds risk in every domain, before and during operation.

- **Owns:** risk taxonomy and risk register · risk assessment and scoring (fraud, compliance, security, operational, financial, AI, governance, market) · risk appetite and limits · risk-aware decisioning inputs · **Fraud** (typologies, signals catalog, fraud cases, prevention policies) · pre-production risk intelligence.
- **Boundary:** detection models → {{Intelligence}} · cyber threats → {{Security}} · credit underwriting → {{Financial Services}}.

### {{#Audit & Evidence}}

**Mandate:** Captures everything immutably and turns it into evidence (L13).

- **Owns:**
  - *Audit capture* of events, activities, access, decisions, AI inputs and outputs, policy evaluations, security, changes, approvals, governance, runtime, infrastructure, deployments and certifications.
  - *Immutable, cryptographically chained audit trails* covering every audit type: activity, security, financial, compliance, governance, AI, decision, policy, data and operational. Audit runs continuously and in real time.
  - **Evidence**: one canonical evidence object for compliance, knowledge claims, certification and disputes · the evidence registry and evidence collection.
  - *Records and queries:* traceability queries · accountability records · stored explanation records.
- **Provides:** auto-audit · auto-evidence · auto-traceability · lineage stitching across {{Data}}, {{Knowledge}} and {{Evolution}} lineage · audit packages.
- **Boundary:** generating explanations → {{Decision}} · operational telemetry → {{Observability}}.

## {{§§planeF}} Plane F — Foundation

### {{#Identity}}

**Mandate:** Who or what anything is. Every entity gets one global, resolvable identity, and every actor gets proof of identity. Never modified by consumers (L4).

- **Owns:** the UGID scheme and its issuance ({{§ugid}}) · identifier namespaces · entity resolution and golden identity · actor identities (human, organization, government, legal entity, team, agent, AI agent, digital human, machine, robot, device, vehicle, service, digital twin) · credentials (passwords, passkeys, biometrics, certificates as credentials, tokens, decentralized identifiers) · authentication (MFA, adaptive/risk-based, SSO, federation through OIDC and SAML adapters, cryptographic identity) · identity lifecycle (join, move, leave) · session identity claims.
- **Core schema:** `Identity { ugid, identity_type, credentials[], authenticators[], verification_ref (Trust), federation_links[], lifecycle, audit }`
- **Boundary:** roles, permissions and authorization → {{Security}} · profiles, structure and party roles → {{Party & Organization}} · verification → {{Trust & Reputation}} · consent → {{Privacy & Consent}} · delegation → {{Authority & Governance}}.

### {{#Tenancy & Ecosystem}}

**Mandate:** The platform's isolation boundaries and composition boundaries.

- **Owns:** Tenant and sub-tenant hierarchy · workspaces · tenant isolation contracts (data, compute, keys, models) · tenant configuration scope · tenant lifecycle (create, suspend, offboard) · Ecosystem (a federation of tenants) · cross-tenant sharing agreements.
- **Boundary:** tenant sovereignty → {{Sovereignty & Residency}} · the tenant's legal organization → {{Party & Organization}} · the tenant's platform definition → {{Composition}} · plan limits → {{Entitlement}} · cross-tenant learning → {{Intelligence}} · cross-tenant knowledge federation → {{Knowledge}}.

### {{#Party & Organization}}

**Mandate:** Parties (persons and organizations), their structure, and the roles they play.

- **Owns:** Party (person profile, organization) · company · legal-entity structure · government body · Brand · team · department · organizational hierarchy · membership of organizational units · **Party Roles**: customer, buyer, seller, merchant, vendor, supplier, manufacturer, provider, partner, affiliate, reseller, distributor, creator, employee, contractor, driver/courier, plus extension roles (patient, student, citizen, …) · global reference partitions for brands, manufacturers and suppliers.
- **Core schema:** `Party { ugid, party_type, identity_ref, profiles, roles[{role, context, valid}], hierarchy, memberships }`
- **Rule:** customer, vendor, supplier, partner, employee and similar are **roles in context**, not separate entities. The *relationship semantics* of each role belong to {{Relationship}}, {{Sourcing & Procurement}}, {{Workforce}} or {{Marketplace & Distribution}}.

### {{#Spatial}}

**Mandate:** *Where* — every location, geometry and spatial computation, in any physical or virtual space.

- **Owns:** point, line, polygon, region, zone, network, address, place, location · administrative geography (planet, country, state, region, city, district, village, postal zone) · extra-terrestrial and virtual space (galaxy, planet, orbit, station, virtual space, digital space, metaverse space) · coordinate systems · geo-boundaries · geocoding · maps.
- **Provides:** distance · containment · proximity · geofencing · coverage · mapping · navigation · spatial routing primitives (path-finding) · spatial indexing · geo-intelligence.
- **Boundary:** shipment route plans → {{Logistics & Fulfillment}} · jurisdictions → {{Compliance}} · geo-search ranking → {{Search & Recommendation}}.

### {{#Temporal}}

**Mandate:** The **sole owner of time semantics** (L9). No other universe implements its own scheduling, recurrence, validity or trigger logic.

- **Owns:** time point and instant · time range and window · duration · time zone · calendars (civil, business, fiscal, holiday, market, cultural) · recurrence rules · schedules · time triggers · availability windows · timelines · deadlines · SLA clocks · **Temporal Policy** (validity + recurrence + windows + time zone) · temporal validity (valid-from, valid-to) · bitemporal history (valid time × transaction time) · temporal identity (an object at a point in time) · temporal context · temporal lineage and temporal versioning of facts.
- **Provides:** validity evaluation · recurrence expansion · schedule computation · business-day arithmetic · as-of queries · temporal audit · replay · inputs to temporal forecasting ({{Intelligence}}), temporal simulation ({{Simulation}}) and temporal digital twins ({{Digital Twin}}).
- **Consumers** reuse it and never re-implement it: offers, discounts, promotions, coupons, vouchers, campaigns, loyalty, flash sales, dynamic-pricing windows, subscriptions and renewals, billing cycles, invoicing, orders, delivery slots, appointments and bookings, workforce shifts, production plans, finance and tax periods, retention, SLAs, AI retraining, governance terms, credential and key expiry. The worked example is in {{§examples}}.
- **Boundary:** executing timers → {{Runtime Fabric}} · artifact versions → {{Evolution}} · which resources are free → {{Resource & Capacity}}.

### {{#Language & Locale}}

**Mandate:** Every language and cultural convention, with nothing hard-coded (L1).

- **Owns:** languages, scripts and dialects (human, sign, and machine-readable language tags) · locales (formats for numbers, dates, addresses and names) · translation (memory, glossaries) · localization resources · internationalization rules · transliteration · interpretation (speech) · cultural context · the multilingual runtime.
- **Boundary:** semantic mapping between vocabularies → {{Knowledge}} · applying locale in UI → {{Experience}} · currency → {{Value & Economics}} · units → {{Measurement}} · cultural calendars → {{Temporal}}.

### {{#Measurement}}

**Mandate:** Every quantity has a unit, and every unit is defined once.

- **Owns:** quantity · unit · dimension · unit systems (SI, imperial, domain units such as bandwidth, latency, voltage, power and rate) · conversion · precision, rounding and tolerance.
- **Boundary:** money → {{Value & Economics}} · durations → {{Temporal}}.

### {{#Context & Reality}}

**Mandate:** Assembles the Context Frame ({{§context}}) and defines which reality an evaluation happens in.

- **Owns:** the Context Frame · reality types (physical, digital, virtual, mixed, simulated, hypothetical, future) · observer and perspective · assumption sets · environmental conditions as context · context propagation · the context resolution engine · the context registry.
- **Boundary:** the semantics of each context dimension → its owner ({{§context}}) · running scenarios → {{Simulation}}.

## {{§§planeD}} Plane D — Knowledge & Data

### {{#Knowledge}}

**Mandate:** The single canonical source of meaning and truth: the Universal Knowledge Graph.

- **Owns:** ontology · taxonomy · vocabulary · classification schemes · semantics and the semantic layer · the metadata model · Knowledge Objects (claims) · **one** Knowledge Graph with named sub-graphs (ontology, capability, dependency, workflow, security, compliance, runtime, product, service, AI, governance, infrastructure, evolution, context, relationship, lineage). Each sub-graph's *content* is owned by its universe. Also: the truth model and truth management · contradiction detection and resolution · confidence · hypothesis · semantic inference over the ontology (deductive and constraint reasoning) · knowledge provenance and lineage · auto-classification, linking, deduplication and truth verification · cross-tenant knowledge federation · civilization-scale knowledge domains, all living in this one graph.
- **Core schema:** `KnowledgeObject { ugid, type, statement, source, classification, confidence, trust_ref (Trust), lineage, relationships, evidence_refs, validation, certification_ref }`
- **Boundary:** AI reasoning and planning → {{Intelligence}} · registry mechanics → {{Registry}} · data lineage → {{Data}} · evidence objects → {{Audit & Evidence}} · policy reasoning → {{Policy}} · risk reasoning → {{Risk}}.

### {{#Global Offering Knowledge Network}}

**Mandate:** Canonical, shared knowledge of everything that can be offered — every known product and service. It is stored once and reused by every tenant and every platform. It is an intelligence network, not a catalog.

- **Owns:** Global Product Registry (GPID) · Global Service Registry (GSID) · global product and service taxonomies (category trees) · global attribute definitions (with units from {{Measurement}}) · specification registry · variant models · external classification mappings (UNSPSC, GS1, HS, …) · product, service and commerce graphs · product relationships (accessory-of, compatible-with, substitute, successor) · regulatory requirement mappings per product class (references into {{Compliance}}) · global price history and market intelligence · offering templates.
- **Provides:** auto import, crawl, normalize, match, deduplicate, enrich, classify and translate · attribute and taxonomy discovery · new-product and new-service discovery. Example: *Apple iPhone 17* is stored once and consumed by every store, B2B marketplace, ERP, POS, warehouse, analytics view, agent and recommender.
- **Boundary:** what a tenant actually sells (price, stock, terms) → {{Offering}} · tenant catalogs → {{Catalog & Merchandising}} · brand, manufacturer and supplier parties → {{Party & Organization}} · media → {{Content & Media}} · industries → {{Blueprint}}.

### {{#Data}}

**Mandate:** Logical data governance and data products for every universe.

- **Owns:** logical data models (generated from schemas) · data products · data contracts · data catalog · data quality (rules, scores) · data lineage and data-level provenance · master data management · reference-data management (the mechanism; the content belongs to its owners) · data ownership and stewardship assignments · data versioning · replication, federation and virtualization policies · data mesh and fabric topology · logical lakehouse and warehouse layers · internal pipelines (ETL, ELT, CDC, streaming transforms) · data classification tags · archival and deletion execution · data-type support (structured, semi-structured, unstructured, documents, images, audio, video, streams, IoT and sensor, graph, vector, future).
- **Boundary:** physical stores → {{Infrastructure}} · external exchange → {{Integration}} · meaning → {{Knowledge}} · insight → {{Analytics}} · retention policy → {{Privacy & Consent}}.

### {{#Content & Media}}

**Mandate:** Authored content and media, and how it is published and delivered.

- **Owns:** content items · business documents (contract documents, invoice PDFs, reports, certificates, forms — instance generation, versioning, archival) · media assets / DAM (image, video, audio, CAD, 3D, GIS imagery) · collections · publications · CMS · rendition and transcoding · delivery (VOD, live streaming, broadcasting, OTT) · course content · creators and content channels · content-rights metadata · knowledge publishing.
- **Boundary:** platform documentation → {{Documentation}} · messaging → {{Communication & Collaboration}} · signatures → {{Trust & Reputation}} · access rights → {{Entitlement}} · moderation → {{Trust & Reputation}} · recommendation → {{Search & Recommendation}} · ML model artifacts → {{Intelligence}}.

## {{§§planeP}} Plane P — Process & Decision

### {{#Event}}

**Mandate:** The canonical record of what has happened, and the contracts for reacting to it.

- **Owns:** Event · event-type registry and catalog · event schemas and versions · event taxonomy (domain, integration, audit, telemetry) · command/event conventions · event-sourcing patterns · complex-event-processing definitions · event triggers · event and choreography contracts.
- **Core schema:** `Event { ugid, type, source, context, payload, occurred_at (Temporal), policies, security, compliance, audit }`
- **Boundary:** transport (bus, mesh, streaming) → {{Runtime Fabric}} · telemetry → {{Observability}} · audit capture → {{Audit & Evidence}}.

### {{#Workflow}}

**Mandate:** All process behaviour, expressed as state machines and orchestrations. There is no workflow-specific code. The "Automation universe" of the source drafts is part of this universe.

- **Owns:** Workflow (trigger, conditions, actions, policies, approvals, escalations, events, monitoring, audit) · state machines · processes (a BPMN abstraction) · orchestration and choreography definitions · human, AI, agent and hybrid tasks · approval steps · escalation · timers (semantics from {{Temporal}}) · compensation, sagas and long-running transactions · **generic case management** (tickets, claims, disputes, investigations and incidents are all case types whose semantics belong to their owners) · workflow templates · automation modes (rule-, event-, goal- and policy-driven, RPA, agentic, autonomous execution) · cross-universe process compositions.
- **Boundary:** choices made inside steps → {{Decision}} · constraints → {{Policy}} · approval authority → {{Authority & Governance}} · execution → {{Runtime Fabric}}.

### {{#Decision}}

**Mandate:** How choices are made, recorded and explained.

- **Owns:** decision models (decision tables, decision trees, scorecards, rule sets for choices, probabilistic, optimization-backed and AI-backed decisions) · **Decision Record** `{ ugid, type, authority, context, inputs, outputs, evidence, approvals, risk_assessment, compliance_assessment, audit_refs, certification_status }` · decision intelligence and decision support · **explainability** for every decision, including AI decisions.
- **Boundary:** what is allowed → {{Policy}} · model training → {{Intelligence}} · record storage → {{Audit & Evidence}}.
