# U44 — Search Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U44-search` |
| Layer | L6 Intelligence (runtime engines in L8) |
| Domain | 06 Experience |
| Steward | `ucos:org:discovery-search` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (keyword + facets + admin search), P4 (semantic/hybrid, personalisation, conversational search) |
| Depends on | U04 Meta (searchProjection), U61 Event (indexing), U06 Taxonomy (facets), U05 Ontology (synonyms/term resolution), U15 Localization (analyzers), U03 Policy (filtering), U49 AI (embeddings, P4), U72 Analytics (click signals), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | Storefronts (PLP/search), all portals (admin search, ⌘K), U51 Agents (tools), U52 Recommendation (retrieval) |
| Master references | §13.1 (OpenSearch, vector), §14.1, §6.2 U44 |

> Search owns **finding things**: index definitions (generated from object types' `searchProjection`), indexing pipelines from events, query understanding (spelling, synonyms, term→concept, intent), ranking profiles (business rules, relevance, personalisation), facets, merchandising controls (boosts, pins, buries), hybrid keyword+vector retrieval, and search analytics. It does not own the indexed data — every index is a rebuildable projection.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| SRCH-L1 | Indexes are projections; full rebuild from events/registries must be possible at any time. | Rebuild job tested monthly (evidence). |
| SRCH-L2 | Search results are authorisation-filtered at query time (tenant, org, policy residuals); no post-hoc filtering that leaks counts/facets. | Query builder injects PDP `PartialEvaluate` filters into the query, including facet aggregations. |
| SRCH-L3 | Merchandising (pins/boosts) and sponsored results are explicit, auditable and, where sponsored, labelled. | Ranking profile metadata + UI label obligation (consumer law). |
| SRCH-L4 | Personalisation uses only consented signals and excludes SPI. | Feature allow-list in ranking config; U66 consent check. |

---

## 2. Objects
- **`IndexDefinition`** `{ id, objectType(s), tenantScope, fields: [{path, analyzer per locale, facet, sortable, boost}], vector?: {source fields, model ref, dims}, refreshPolicy, retention, generatedFrom: searchProjection@version }`
- **`Synonym` / `QueryRule`** `{ tenant, locale, terms ↔ concept (U05), rule: redirect|filter|boost|rewrite, validity: TemporalPolicyRef }`
- **`RankingProfile`** `{ id, scope (catalog/channel), stages: [retrieval: keyword|vector|hybrid(α), rerank: business signals (availability, margin cap, popularity, rating, recency, offer), personalisation weight, diversity], pins/buries (TemporalPolicy-bound), experiments }`
- **`SearchSession` / `SearchEvent`** analytics `{ query, filters, results shown, clicks, add-to-cart, zero-result flag }`.

## 3. Algorithms
- **Query pipeline:** normalise → spell-correct (per locale) → synonym & concept expansion (U05 `ResolveTerm`) → intent detection (category/brand/attribute extraction, e.g. "red running shoes under 3000" → facets + price filter) → retrieval (BM25 + kNN hybrid with reciprocal rank fusion) → filters (policy residuals, availability per ctx, prohibited-in-jurisdiction) → rerank (profile) → facets (from taxonomy template) → result + explain (privileged).
- **Indexing:** event-driven upserts (catalog.listing.*, pricing.price.changed, inventory.stock.*, offer badges, ratings) into denormalised documents; target freshness p99 < 5 s for price/stock, < 60 s others.
- Decision tables: `search.zero-result-fallback`, `search.availability-filter` (hide OOS / show with label), `search.sponsored-slots` (P4 with U33).

## 4. Commands, Queries, Events, APIs
Commands: `DefineIndex` (generated; governed), `Reindex(scope)`, `UpsertSynonyms`, `DefineQueryRule`, `DefineRankingProfile`, `PinResult`.
Queries: `Search(q, filters, sort, page, ctx)`, `Suggest(prefix, ctx)` (autocomplete), `AdminSearch(q, types[])` (⌘K across universes, policy-filtered), `Explain(resultId)` (privileged).
Events: `search.query.performed` (sampled, analytics), `search.index.rebuilt`.
```text
GET  /v1/search?q=&filter=&sort=&page[cursor]=     GET /v1/search/suggest?prefix=
GET  /v1/search/admin?q=&types=                    POST /v1/search/indexes/{id}:reindex
POST /v1/search/synonyms   POST /v1/search/query-rules   POST /v1/search/ranking-profiles
```

## 5. Security & Compliance
Policy-filtered retrieval (incl. vector search pre-filtering), tenant-per-index or tenant-routed shards; PII fields not indexed in storefront indexes; admin indexes mask per obligations; sponsored labelling (consumer law, DSA transparency on ranking parameters for EU marketplaces: ranking main parameters disclosed via a published RankingProfile summary).

## 6. Gaps
```prolog
gap(no_index_for_searchable_type, T) :- object_type(T), has_search_projection(T), not index_definition_for(T).
gap(zero_result_rate_high, T)       :- tenant(T), zero_result_ratio(T, R), R > 0.1.
gap(missing_locale_analyzer, T, L)  :- tenant_locale(T, L), not analyzer_for(L).
gap(index_rebuild_untested, I)      :- index(I), last_rebuild_test_days(I, D), D > 31.
```

## 7. AI
P4: embeddings (product, query) via AI gateway; LLM query understanding for conversational search; zero-result recovery suggestions; synonym mining from logs (proposals). Agents use `search.query` tool (policy-filtered).

## 8. Operations, UI, Scale
Signals: `search_latency_ms` (p95 < 120 ms), `zero_result_ratio`, `ctr@k`, `index_freshness_s{field}`, `reindex_duration_s`. Views: storefront `search.results` (facets, sort, chips), `search.autocomplete`, `search.merchandising.console` (pins/boosts with Temporal windows, preview), `search.synonyms.editor`, `search.analytics` (top queries, zero results, CTR). Scale: OpenSearch clusters per cell; 10⁸ docs per large tenant; vector via OpenSearch kNN or Qdrant. T1 (storefront search T0-like degradation: fallback to category browse).

## Appendix
- **C.** 0.1.0.

## Appendix P1 — Phase 1 behaviour without later-phase dependencies
- **U49 AI/Model (Phase 3):** Phase 1 search is keyword (BM25) with synonyms, facets and merchandising only. There are no embeddings, semantic retrieval or LLM query understanding. `IndexDefinition.vector` stays empty. Migration: vectors are back-filled by a reindex job when U49 and the AI gateway are active.
- **D. Attribute definitions (A-74).** `QueryRule { id, tenant: UGID, locale: LocaleTag, match: {terms, concept?}, rule: redirect|filter|boost|rewrite, action: object, validity: TemporalRef, priority: integer, status: active|paused }`
