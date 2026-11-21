# U20 — Industry Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U20-industry` |
| Layer | L3 Knowledge & Registry |
| Domain | 02 Knowledge |
| Steward | `ucos:org:solutions-architecture` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (registry + first templates: D2C store, multi-vendor marketplace), P6 (vertical templates) |
| Depends on | U06 Taxonomy (ucos.industry), U08 Reference Data (ISIC/NAICS/NACE), U57 Capability (bundles), U58 Composition (PD templates), U67 Compliance (industry regulation packs), U64 UI (templates) |
| Depended on by | Builder Studio (W2 templates), U58 (template expansion), U75 (industry-specific gap rules), U10 Org (organization industry) |
| Master references | §10.5, §30 (reference compositions), W2 |

> Industry owns **industry knowledge as reusable starting points**: the industry classification (mapped to ISIC/NAICS/NACE), `IndustryTemplate`s (pre-filled Platform Definitions with capability bundles, taxonomy subsets, attribute sets, workflows, compliance packs, UI templates, KPIs), industry standards references (e.g. FHIR for health, ACORD for insurance), and industry benchmarks. Templates are *starting points*: everything they set is ordinary, editable PD configuration.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| IND-L1 | Templates contain only references to registered definitions (capabilities, taxonomies, rules, views) — no code, no unique definitions. | Template validation: every ref resolvable in registry. |
| IND-L2 | Each template must compose to a blueprint with zero mandatory gaps for its reference geography (golden PD). | Template certification uses U58 golden suite. |
| IND-L3 | Industry-specific regulation is delivered as compliance rule modules (U67), not as template conditionals. | Review. |

---

## 2. Objects
- **`Industry`** = node in taxonomy `ucos.industry` + mappings (ISIC/NAICS/NACE) + `{ regulatedBy: [RegulationRef], standards: [StandardRef], typicalKPIs }`.
- **`IndustryTemplate`**
```yaml
id: ucos:industry-template:multi-vendor-marketplace
version: 2.0.0
industries: [ucos:industry:retail/general-merchandise]
pdFragment:                       # merged into PlatformDefinition.spec
  businessModel: [B2C, marketplace]
  capabilities: { include: [bundle:marketplace-starter, reviews.core, search.core, support.case] }
  portals: [storefront, seller, admin, support, finance]
taxonomies: { product-category: ucos.product-category/subset:general-merchandise }
decisions: { order.return-eligibility: defaults/marketplace-returns.yaml, catalog.auto-approve: defaults/marketplace-moderation.yaml }
uiTemplates: [storefront.retail-classic@3, seller-hub@2]
kpis: [gmv, take-rate, seller-activation-rate, order-defect-rate]
referenceGeographies: [IN, AE]    # golden PDs
questions:                         # intent wizard questions (W2) mapping answers → PD fragments
  - id: same-day
    text: t("tpl.q.same-day")
    yes: { capabilities.include: [fulfillment.local-delivery, temporal.slots] }
```
- **`Standard`** `{ id, name, body, version, conceptMappings (U05) }` e.g. FHIR R5, HL7v2, ACORD, ISO 20022, GS1, TM Forum SID, IMS LTI.
- **`Benchmark`** `{ industry, kpi, percentiles, source, period: TimeRange }` (aggregated, consent-based cross-tenant per U66/master §20.5).

## 3. Commands, Queries, Events, APIs
Commands: `PublishTemplate` (governed, certified via golden PDs), `DeprecateTemplate`, `RegisterStandard`, `PublishBenchmark`.
Queries: `TemplatesFor(industry|intent)`, `ExpandTemplate(template, answers) → PD fragment`, `IndustryOf(org)`.
Events: `industry.template.published|deprecated`.
```text
GET /v1/industry/templates?industry=&q=    POST /v1/industry/templates/{id}:expand
GET /v1/industry/industries?q=             GET /v1/industry/benchmarks?industry=&kpi=
```

## 4. Seed template catalogue (P1 → P6)
P1: `single-brand-d2c`, `multi-vendor-marketplace`. P3: `b2b-distribution`, `restaurant-food-delivery`. P6: `subscription-media-ott`, `ride-hailing`, `short-term-stays`, `crm-saas`, `itsm`, `clinic`, `lms`, `brokerage`, `p2p-procurement-erp`, `grocery-quick-commerce`, `government-services-portal`.

## 5. Gaps
```prolog
gap(template_not_certified, X) :- template(X), published(X), not golden_pd_pass(X).
gap(industry_regulation_unmapped, I) :- industry(I), regulated(I), not compliance_module_for(I).
```

## 6. Security, AI, Ops, UI, Scale
Templates `public`; benchmarks aggregate only (k-anonymity). AI: intent → template matching and question answering in W2. Signals: `template_usage{template}`, `template_time_to_launch_days`. Views: W2 template gallery, `industry.template.editor` (for solution architects), `industry.benchmark.panel`. Small data; control plane; T2.

## Appendix
- **D. Attribute definitions (A-74).** `IndustryTemplate { id, version: string, name: LocalizedText, industryCodes: [{scheme: isic|naics|nace|nic, code}], platformDefinition: object (pre-filled PlatformDefinition), capabilityBundles: [string], taxonomySubset: UGID, workflows: [string], compliancePacks: [string], uiTemplates: [string], seedData: [UGID], publishedAt: TimePoint, status: draft|published|deprecated }`
- **C.** 0.1.0.
