# The Platform Master — one source for every product and service, configured by selection

Adopted 2026-10-21 by the platform owner (amendment AMD-0025, roadmap steps P27–P30, decisions
DEC-015–DEC-021). This document is the design; each phase below records what it delivered as it lands.

The global platform owns one **platform master**: every product, service, variant and SKU of every
industry, described once. Each platform sees a **projection** of it, filtered by its permissions, its
authorities (jurisdictions) and its own overlays. Nothing is copied into a platform, and no level,
type, code or feature is fixed in code.

## 1. What the master holds

| Concern | How it is held | Owner |
|---|---|---|
| Levels (domain, industry, category, subcategory, family, model, product, service, variant, SKU, any added) | **Kinds**, declared as rows, with placement rules; any depth | Registry |
| Every product and service | **Entities** of those kinds, versioned bi-temporally | Identity |
| Classifications (trade taxonomy, tariff nomenclature, scientific nomenclature, tax classes, any added) | **Hierarchies** over the same entities; one entity sits in many | Relationship / Semantic |
| Codes, scientific names, local codes | **Identifiers** under an **identifier scheme**: format, check rule, issuing authority, places it applies in, validity | Identity |
| What a source model calls columns | **Attributes** on kinds, inherited down a hierarchy, applicable by context (place, authority, kind of offering), multilingual through Expression | Registry / Context |
| Bundles, accessories, replacements, cross-sell, upsell | **Relationship types** as rows, edges between entities | Relationship |
| Media, documents | Content registries | Content |
| Units, packaging levels, conversions | Measure registries | Measure |
| Industry rules (weight pricing, expiry, prescription, assembly, rental terms…) | **Rule packs** on the kind | Rule |
| How it is delivered | **Fulfilment modes**: shipped, collected, downloaded, appointment, chat, audio call, video call, visit, any declared | Commerce |

Stock, serial items, prices and seller terms stay per-platform operational records that point at a
master SKU. A platform's product rows become a **read model** rebuilt from the projection, its overlays
and its sellers' offers; orders keep their snapshot.

Day one ships the **maximum** declared content: every level, kind, identifier scheme, unit, packaging
level and relationship type, the existing catalogue merged in, and data packs for public classifications.

## 2. Permissions

The global platform gives each platform permissions on the master. Each has validity dates.

| Dimension | Values (rows, extendable) |
|---|---|
| Scope | subtrees of any hierarchy; authorities; kinds |
| Object | attribute definition, entity, classification node, relationship, media |
| Action | view, select, overlay a value, add, modify, retire |
| Attribute visibility | which attributes the platform sees (default: those applicable to its authorities) |
| Review | every contribution is reviewed (DEC-015) |

## 3. Overlays and contributions

* An **overlay** is a platform's own value held in its own scope (a local name, a local code). The
  master is untouched; resolution answers the most specific value and says where it came from.
* Every **addition, modification or retirement** a platform makes to the master is a **contribution**.
  It enters the global review queue. Nothing is adopted automatically (DEC-015, DEC-017).
* Once approved, the reviewer places it: **apply** (a new version of the master entity), **new** (a new
  entity or attribute), or **addendum** (an extension attached to the entity, applicable in a declared
  context such as one authority or one platform). Otherwise it is **rejected** with a reason.
* Retirement is always a new version. Nothing is erased.

## 4. Configuring a platform

A platform is created by intent › compose › certify › publish. The intent is a **blueprint**: its steps
are rows naming the question, where the options come from, and what each answer unlocks.

| Step | Options come from |
|---|---|
| Official authority (jurisdiction) | Authority / Geo |
| Working authorities | Authority / Geo |
| Languages | Expression |
| Value units (currencies) | Value |
| Taxes | the chosen authorities' tax regimes |
| Identifier schemes | those valid under the chosen authorities |
| Selling model (single seller, marketplace, hybrid, any declared) | Package |
| What it sells — single, several or mixed, products and services | the master, filtered by permissions |
| Features | discovery |
| Sites | Experience |

Every setting is configurable on its own, with an effective time to the minute; existing platforms are
not migrated in bulk (DEC-018).

**Discovery** derives each capability from the answers and states why:

* **Mandatory** — required by a chosen kind's rule pack or an authority's law; cannot be switched off
  while the cause remains.
* **Recommended** — declared relevant by a kind or fulfilment mode; pre-selected.
* **Added** — switched on by the platform's admin.
* **Requested** — not in the permissions or not built yet; captured during configuration and editable by
  the global admin afterwards (DEC-019).

Platform kinds and blends (PLATFORM_TYPES.md) become **starter packages** that pre-fill answers; they no
longer decide features (DEC-021).

## 5. Services and media sessions

A consultation, a lab test or a class is an entity like a product, with its own fulfilment modes.
Appointments use bookings; chat uses conversations; audio and video use a **media session**, carried by
the platform itself or by any connector plugged in as a provider registration. Communication can itself
be offered to others on paid or any other commercial terms (DEC-020).

## 6. What is replaced

| Today | Becomes | Phase |
|---|---|---|
| `global_products` | master entities | 2 |
| `store_product_config` permissions string | permissions | 3 |
| `importToStore` copying | selection into the projection | 3 |
| per-platform `taxonomy`, `attribute_defs` | hierarchies and attributes in the master, overlays per platform | 2 |
| the product localization table | Expression | 1 |
| fixed vocabularies in `lib/meta.js` (verticals, taxonomy levels, relation types, media kinds, packaging levels, shipping classes, identity fields, variant axes) | master rows | 2 |
| catalogue seeding at registration | selection | 5 |
| platform kinds and blends as gates | starter packages | 5 |
| the fixed setup checklist | blueprint steps | 5 |
| `products` edited directly | read model | 6 |

## 7. Phases

Each gate is the full test suite, the registry gate, the hard-coding audit, the white-label scan and the
browser check, plus the phase's own checks.

| Phase | Work | Own gate |
|---|---|---|
| 0 | This design recorded in the registry | registry compiles; every new term has one owner |
| 1 | Kernel: validation rules on kinds, multilingual attributes, view groupings, scoped kinds | each kernel part tested; localization merged into Expression |
| 2 | The master: kinds, hierarchies, identifier schemes, attributes, maximum starter content; existing catalogue merged | counts reconcile; no duplicate catalogue table |
| 3 | Permissions, projections, overlays | a platform sees exactly its permissions; overlays never leak |
| 4 | Contributions: review, apply / new / addendum / reject | an approved contribution reaches a second platform |
| 5 | Blueprint configuration, discovery, starter packages, certification | every platform type launches by answers alone |
| 6 | Read model for cart, checkout and orders | every engine's tests pass unchanged |
| 7 | Fulfilment modes, built-in media sessions, connectors, communication on commercial terms | a consultation booked, held and paid end to end |
| 8 | Documentation, retired paths removed, registry statuses | no retired table or function referenced |
