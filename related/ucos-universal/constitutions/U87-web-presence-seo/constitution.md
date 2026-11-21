# U87 — Web Presence & SEO Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U87-seo` |
| Layer | L10 Experience |
| Domain | 06 Experience |
| Steward | `ucos:org:experience-web-presence` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (URLs, metadata, sitemaps, structured data, redirects, robots, hreflang — required for any public storefront), P4 (content pages CMS integration, AI SEO assistance, programmatic landing pages) |
| Depends on | U64 UI (routes, rendering/SSR), U21 Catalog & U18 Product (structured data sources), U15 Localization (hreflang, localised slugs), U10 Org (domains), U41 Content & Media (pages/blogs, P4), U72 Analytics (search console data), U43 Asset (OG images), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | Storefronts, marketplaces, content sites, U86 (landing pages), U33 (ads landing quality) |
| Master references | User requirement "SEO" (A-32) |

> Web Presence owns **how tenant sites are found, addressed and understood on the open web and by AI/answer engines**: URL/route schemes and slugs (localised), canonicalisation, redirects, page metadata (title, description, Open Graph/Twitter cards), structured data (schema.org JSON-LD: Product, Offer, AggregateRating, BreadcrumbList, Organization, LocalBusiness, Event, FAQ), XML sitemaps & indexes, robots directives, hreflang, Core Web Vitals budgets, crawl-budget hygiene for faceted navigation, and AI-crawler policies (llms.txt-style directives).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| SEO-L1 | Every public, indexable view has a canonical URL, title, description and structured data generated from canonical data (never hand-copied facts). | View compile step validates; gap otherwise. |
| SEO-L2 | URL changes always create 301 redirects; slugs are stable identifiers per locale. | Redirect registry auto-created on slug change. |
| SEO-L3 | Structured data must reflect visible page content and real offers (price, availability, ratings) — no fake markup. | Generated from the same BFF data as the page. |
| SEO-L4 | Faceted/filter URLs follow indexation rules (noindex/canonical) to avoid infinite crawl spaces. | Decision `seo.facet-indexation`. |

## 2. Objects
`Route { id, site, pattern (/{locale}/{category-slug}/{product-slug}-{shortId}), view, indexable, canonicalRule }` · `Slug { object, locale, value, history[] }` · `Redirect { from, to, code 301|302|410, reason, createdAt: TimePoint }` · `MetaTemplate { view/objectType, locale, titleTemplate, descriptionTemplate, ogImageRecipe (U43), robots }` · `StructuredDataMapping { objectType → schema.org type, field mappings }` · `Sitemap { site, kinds (products, categories, content, stores), shards, lastmod: TimePoint }` · `SiteSettings { domains (U10), robots.txt rules, ai-crawler policy, hreflang map, trailingSlash, locale strategy: subpath|subdomain|ccTLD }`.

## 3. Commands, Queries, Events, APIs
Commands: `DefineRoute`, `SetSlug`, `CreateRedirect`, `DefineMetaTemplate`, `MapStructuredData`, `RegenerateSitemaps` (event/Temporal driven), `UpdateSiteSettings`.
Queries: `ResolveUrl(path)` (edge-fast: route → view + object | redirect), `SeoAudit(site)` (missing meta, duplicate titles, broken links, schema errors, CWV), `PreviewSnippet(page)`.
Events: `seo.slug.changed`, `seo.redirect.created`, `seo.sitemap.regenerated`.
Public endpoints: `/sitemap.xml`, `/sitemaps/*.xml.gz`, `/robots.txt`, `/llms.txt` (policy), feeds for search engines/merchant centres via U62.
```text
GET /v1/seo/resolve?host=&path=   POST /v1/seo/redirects   GET /v1/seo/audit?site=
POST /v1/seo/meta-templates      POST /v1/seo/structured-data-mappings
```

## 4. Gaps
```prolog
gap(indexable_view_without_meta, V) :- view(V), indexable(V), not meta_template(V, _).
gap(missing_hreflang, S)            :- site(S), multi_locale(S), not hreflang_map(S).
gap(no_structured_data, T)          :- object_type(T), public_product_like(T), not structured_data_mapping(T).
gap(redirect_chain, R)              :- redirect_chain_length(R, N), N > 2.
gap(cwv_budget_exceeded, V)         :- view(V), lcp_p75(V, L), L > 2500.
```

## 5. Security & Compliance
No PII in URLs; robots/ai-crawler policies reflect tenant choice; consumer-law accurate pricing in snippets (SEO-L3); accessibility overlaps (titles, headings).

## 6. AI, Ops, UI, Scale
AI: meta/description generation (human-reviewable), internal-link suggestions, programmatic landing pages from taxonomy × geo (P4, quality-gated to avoid thin content), answer-engine optimisation (FAQ/structured facts from U07). Signals: `indexed_pages`, `crawl_errors`, `redirect_hits`, `cwv_lcp_p75`, `organic_sessions` (U72 + search console connector). Views: `seo.audit.dashboard`, `seo.redirect.manager`, `seo.meta.editor` with SERP preview, `seo.settings` (robots, ai-crawlers, hreflang). Scale: edge-resolved routing (CDN KV); sitemaps sharded (50k URLs/file). T1 (resolve path T0 at edge).

## Appendix
- **C.** 0.1.0.

## Appendix P1 — Phase 1 behaviour without later-phase dependencies
- **U41 Content & Media (Phase 4):** in Phase 1, static pages (About, FAQ, policies, contact) are a minimal `page` ViewDefinition type (U64), with rich text stored as LocalizedText plus U43 assets. SEO routes, meta and structured data apply to them normally. Migration: U41 imports these pages as ContentItems, keeping routes and slugs (SEO-L2).
