# U18 — Product Intelligence Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U18-product` |
| Layer | L3 Knowledge & Registry (global) / L5 (tenant consumption via Catalog) |
| Domain | 02 Knowledge |
| Steward | `ucos:org:knowledge-products` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (registry, attributes, matching API, tenant contributions), P4 (ingestion network at scale, licensed feeds, AI enrichment pipeline) |
| Depends on | U05 Ontology, U06 Taxonomy, U08 Reference Data (GS1 GPC, UNSPSC, HS), U14 Currency & Unit (attribute units), U43 Asset (media + rights), U07 Knowledge Graph, U15 Localization, U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U21 Catalog (listings), U31 Tax (category hints, HS), U44 Search, U52 Recommendation, U34 Inventory (GTIN), U45 Procurement, U36 Logistics (dims/hazmat), AI agents |
| Master references | §10 (whole section), ADR-008 |

> Product Intelligence owns the **global, tenant-neutral truth about products**: `GlobalProduct` (GPID), `ProductModel` (family), `GlobalVariant`, the **Attribute Registry**, `Brand`, `Manufacturer`, product identifiers (GTIN/MPN/ISBN…), regulatory product facts (hazmat, recalls, energy labels), media with rights, and the ingestion/matching/enrichment pipeline with provenance. Tenant-specific selling data lives in Catalog (U21).

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| PRD-L1 | One real-world product (at variant level) ↔ one GPID. Duplicates are merged with aliasing; GPIDs are never reused. | Matching pipeline + merge workflow; alias table. |
| PRD-L2 | Every fact has provenance (source, method, confidence, licence) and the published value follows survivorship rules. | Fact-level storage (§3.3). |
| PRD-L3 | Facts below the confidence threshold or from AI-only provenance are not published as truth; they are suggestions. | Publish gate. |
| PRD-L4 | Tenant data contributed to the global registry requires the tenant's contribution consent and excludes commercial data (prices, stock, sales). | Contribution contract + schema separation. |
| PRD-L5 | Source licences are enforced on redistribution (fields from restricted sources served only to entitled tenants). | Field-level licence tags + entitlement check (U28). |
| PRD-L6 | Attributes are registered once (typed, unit-dimensioned, localised) and reused across categories. | Attribute Registry uniqueness + ontology dedupe. |

---

## 2. Ontology & Objects

- **`Attribute`** `{ id (e.g. display.diagonal), concept, valueType: Quantity(dimension)|Enumeration(taxonomy)|Boolean|Text|LocalizedText|Number|Range|Color, unitDimension?, allowedValues?, localized: bool, variantAxis: bool (can define variants), family: physical|digital|financial|behavioral|operational|regulatory, overridableByTenant: bool, searchable/facet hints, validation }`
- **`ProductModel`** `{ id (ucos:gproductmodel:…), brand, manufacturer, name, category (ucos.product-category node), variantAxes: [AttributeRef], sharedAttributes, media, launchedAt: TimePoint, discontinuedAt?: TimePoint }`
- **`GlobalProduct`** (= variant-level; master §10.2 schema) `{ id GPID, model, identifiers [{scheme: GTIN-8/12/13/14|UPC|EAN|ISBN|ASIN-like external|MPN|SKU-manufacturer, value}], variantValues, attributes (published facts), classification {ucos, gs1-gpc, unspsc, hs, google}, regulatory {hazmat UN number, battery, eWaste, energyLabel, ageMin, recallStatus, countryOfOrigin}, dims/weight (Quantity), media [AssetRef with rights], quality {score, completeness, conflicts}, status: candidate|published|deprecated|merged, mergedInto? }`
- **`Brand`** `{ id, name, owner: OrgRef?, aliases, logo, verified }`; **`Manufacturer`** = Organization (U10, global tenant) + role.
- **`ProductFact`** `{ product, attribute, value, source, method: manual|import|feed|crawl|tenant|ai, confidence, licence, observedAt: TimePoint, status: candidate|accepted|rejected|superseded }`
- **`MatchCandidate`** / **`MergeCase`** for dedupe review (W9).
- **`Recall`** `{ product(s)/lots, authority, jurisdiction, severity, publishedAt: TimePoint, remedy }`

---

## 3. Rules & Algorithms

### 3.1 Matching (normative cascade)
1. Exact identifier match (GTIN normalised to GTIN-14, MPN+brand).
2. Strong attribute match: brand + model + variant axes values.
3. Fuzzy: title/attribute embedding + image perceptual hash similarity.
Score → `≥ 0.95` auto-link (if no conflicting identifier), `0.75–0.95` steward/seller review (W9), `< 0.75` new candidate.

### 3.2 Survivorship
Per attribute: priority `manufacturer-feed > gs1 > licensed-provider > steward-manual > tenant-contribution > crawl > ai`, then recency, then confidence; steward overrides pinned with reason. Conflicts (two high-priority sources disagree) → conflict flag + review queue.

### 3.3 Quality score
`completeness(category template required attrs) 40% + media (count/quality/rights) 15% + identifier presence 15% + conflicts (negative) 15% + freshness 15%` → publish threshold per category (decision `product.publish-threshold`).

### 3.4 Pipeline (master §10.3) operated as durable workflows per batch; idempotent per source record hash.

---

## 4. Commands, Queries, Events, APIs
Commands: `IngestBatch(source, records)`, `ContributeFromTenant(listing, consent)`, `Match(record)`, `ResolveMatch(case, link|new|reject)`, `MergeProducts`, `AcceptFact`/`RejectFact`, `PublishProduct`, `DeprecateProduct`, `RegisterAttribute` (governed), `RecordRecall`.
Events: `product.global.published|updated|merged|deprecated`, `product.recall.published`, `product.attribute.registered`.
Queries: `GetGlobalProduct(gpid, locale, entitlement)`, `SearchGlobal(q, filters)`, `MatchCandidates(record)`, `AttributesFor(category)` (via taxonomy template), `ByIdentifier(scheme, value)`.
```text
GET  /v1/product/global/{gpid}?locale=        GET /v1/product/global?q=&brand=&category=&gtin=
POST /v1/product/match                        POST /v1/product/ingest/batches
POST /v1/product/match-cases/{id}:resolve      GET /v1/product/attributes?category=
```
Errors: `PRD_IDENTIFIER_CONFLICT`, `PRD_LICENCE_RESTRICTED`, `PRD_BELOW_QUALITY`, `PRD_MERGED` (301-like redirect to survivor GPID).

## 5. Decision tables
`product.publish-threshold` (by category), `product.auto-link-threshold`, `product.source-priority` (overridable per attribute family), `product.contribution-defaults`.

## 6. Security & Compliance
Global registry is `public` (except restricted-licence fields); contributions de-identified of tenant commercial data; recall propagation to Catalog (auto-suppress) and Order (notify buyers) — consumer safety regulations (EU GPSR, CPSC, BIS India). Media rights: usage scope tags (tenant redistribution allowed? attribution?).

## 7. Reuse
Catalog Listings MUST reference GPIDs when matched; Search/Recommendation/AI use the global graph; Tax uses HS/category hints; Logistics uses dims/weight/hazmat.

## 8. Gaps
```prolog
gap(attribute_unregistered, A)     :- used_attribute(A), not registered_attribute(A).
gap(category_template_missing, N)  :- taxonomy_node(N, ucos.product-category), leaf(N), not attributes_template(N).
gap(match_backlog, N)              :- match_queue_size(N), N > 10000.
gap(recall_unpropagated, R)        :- recall(R), affected_listing(R, L), not suppressed(L).
```

## 9. AI
Attribute extraction from text/images/PDF datasheets, classification, title normalisation, translation, image tagging and background quality checks — all as `ProductFact` candidates with `method: ai` and confidence; embedding index for matching and semantic search.

## 10. Operations
Signals: `global_products_published`, `match_auto_ratio`, `match_queue_size`, `fact_conflicts_open`, `quality_avg{category}`, `ingest_throughput_rps`. SLO: `GetGlobalProduct` p99 < 20 ms (cached in cells), matching p95 < 500 ms.

## 11. UI
Views: W9 (match & steward review), `product.global.detail` (facts with provenance per attribute, conflicts, history), `product.attribute.registry`, `product.ingest.monitor`, `product.recall.console`, seller-facing `product.match-picker` (in listing editor).

## 12. Scale
Target 10⁸–10⁹ global products long-term (P4+), 10⁶ by end of P4; facts 10¹⁰; stored in control-plane Postgres (sharded) + object store for media + vector index; replicated read model to cells. T1.

## Appendix
- **A.** Data sourcing strategy and licences (GS1 data pools, manufacturer syndication networks, licensed providers) — commercial/legal workstream before P4.
- **C.** 0.1.0.

## Appendix D — Completeness extensions (amendment A-29)
- **Product relationships** (typed, temporal, with provenance): `accessoryOf`, `sparePartOf`, `consumableFor`, `compatibleWith` (with a compatibility condition, e.g. vehicle make/model/year/engine for auto-parts *fitment*, printer model for cartridges, device for cases), `replacedBy` / `successorOf`, `bundleComponentOf`, `variantSiblingOf`, `similarTo` (computed), `frequentlyBoughtWith` (computed, owned by U52 and only referenced here). Query: `Compatible(gpid, targetSpec)`.
- **Fitment / compatibility tables:** `CompatibilityTable { domain (automotive ACES/PIES, electronics, appliances), keys (taxonomy-backed attributes), rows: [{targetSpec, gpid, notes}] }`, ingested from industry standards (ACES/PIES for auto parts).
- **Kits & bundles at product level:** `ProductComposition { parent GPID, components [{gpid, qty}], kind: kit|bundle|set }`. Tenant-level selling bundles are in U21/U78.
- **Product types beyond physical goods:** `productNature: physical|digital-download|digital-licence|digital-streaming-right|virtual-item (reality-bound, U77)|tokenised (U99)|service-bound (U19)`. Digital licences are delivered via U35 DigitalDelivery and U28 Entitlement.
- **Compliance & safety documents:** `ProductDocument { gpid, kind: safety-data-sheet|declaration-of-conformity|certificate (CE, BIS, FCC, UKCA, FSSAI, FDA)|manual|warranty-terms|energy-label|repairability-index, asset (U43), issuer, validity: TimeRange, jurisdictions }`. A required document missing for the sale jurisdiction raises a gap (rules from U67).
- **Digital Product Passport** (EU ESPR) via U99/U98: `passportRef` on GlobalProduct and/or AssetUnit.
- **Lifecycle:** `announced → launched → active → end-of-sale → end-of-support → discontinued` (temporal facts). This drives Catalog suppression and the after-sales availability of spare parts.

## Appendix E — Product natures and regulated goods (amendment A-56)

### E.1 Complete product-nature registry
`productNature` (registry; each nature declares required attributes, its fulfilment model, its stock model and its owning universes):

| Nature | Examples | Specific model and owners |
|---|---|---|
| `physical-durable` | electronics, furniture, machines | U18/U21/U34/U35/U79/U80 |
| `physical-consumable` | FMCG, office supplies | U34 lots optional |
| `perishable` | fresh food, flowers, vaccines | lot + `expiresAt` + `coldChain: {minTemp, maxTemp: Quantity}`; U92 temperature telemetry; FEFO (U34) |
| `living` | livestock, plants, pets | species/breed attributes, health certificates (U18 docs), veterinary rules, transport welfare rules (U90 and U67) |
| `bulk-commodity` | grain, metals, crude, chemicals | Quantity-based (weight, volume) with grade/quality specs; U91 auctions/exchanges; U90 |
| `energy` | electricity kWh, gas, fuel, EV charging | metered delivery (U92 meters) + U27 rating; time-of-use pricing (U23 + U13 POL) |
| `water-utility` | water supply, sewerage | metered, utilities pack |
| `real-property` | land, buildings, units, plots | parcel id, title/registry refs, geometry (U12), encumbrances; sale (U89), lease (U83) |
| `vehicle` | cars, two-wheelers, aircraft, vessels | VIN/registration, U79 unit, regulated registration transfer |
| `digital-download` / `digital-licence` / `streaming-right` | software, e-books, media | U28 entitlement + U35 digital delivery + U41 |
| `data-product` | datasets, APIs, data feeds | U93 DataProduct + U28 + licence terms (U89) |
| `ip-licence` / `royalty-right` | brand, patent and music licences | U104 IP asset + U89 agreement + royalty computation (U107/U30) |
| `environmental-credit` | carbon credits, RECs, plastic credits | registry serials, vintage, retirement records (U98); optional on-chain token (U99) |
| `right-permit-spectrum` | permits, licences, spectrum, quotas, airport slots | issuing authority (U77/U12), validity (TimeRange), transferability rules |
| `financial-instrument` | securities, policies, loans | U100 only (never a plain listing) |
| `virtual-item` | in-game items, metaverse land | bound to a U77 reality; redemption via RealityLink |
| `tokenised-asset` | tokenised RWA, NFTs | U99 |
| `labour-time` | gig hours, staffing shifts, freelance hours | U19 service + U17 resource + U46/staffing pack; labour-law decisions |
| `experience-admission` | events, tours, classes | U81 or U13 slots |
| `gift-value` | gift cards, vouchers | U84 |
| `service-plan` | subscriptions, warranties, maintenance contracts | U27 / U80 |

### E.2 Regulated goods model
`RegulatedGoodsProfile` (attached to taxonomy nodes and/or GPIDs; per jurisdiction via U67 rule packs):
`{ category: alcohol|tobacco-nicotine|cannabis|pharmaceutical-rx|pharmaceutical-otc|controlled-substance|medical-device|weapons-ammunition|explosives-fireworks|hazardous-chemical|precursor-chemical|dual-use|adult-content|gambling-product|lottery|financial-product|telecom-sim|drones|wildlife-protected|cultural-property|gold-precious-metals|food-supplement|infant-food|cosmetics|toys-children, jurisdictions: [{jur, status: allowed|licensed|prescription-only|restricted|prohibited, sellerLicence, buyerRequirement (age-min, prescription, permit, KYC), quantityLimits, timeRestrictions: TemporalPolicyRef (e.g. dry days, sale hours), channelRestrictions (no-online, no-cross-border), labellingRequirements, trackAndTrace (serialisation/excise stamps), excise (U31), coolingOff, deliveryRequirements (ID check at delivery, adult signature)}] }`

**Enforcement points:**
- **Catalog:** publish guard.
- **Cart and Checkout:** age gate, prescription upload and verification workflow, quantity limits, sale-hour policies.
- **Fulfillment:** ID check at delivery, no-locker rule.
- **Global Trade:** export controls.
- **Tax:** excise.
- **Search:** filter by jurisdiction.

Gap rule: `gap(regulated_without_profile, N, J) :- taxonomy_node(N), regulated_concept(N), sold_in(N, J), not regulated_profile(N, J).`
- **D. Attribute definitions (A-74).** `MatchCase { id, candidate: UGID (tenant listing or contribution), proposedGlobalProduct?: UGID, scores: {identifier, title, attributes, image}, decision?: match|new-product|reject, decidedBy?: UGID, openedAt: TimePoint, decidedAt?: TimePoint, status: open|auto-matched|in-review|closed }`
