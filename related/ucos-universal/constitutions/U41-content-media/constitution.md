# U41 — Content & Media Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U41-content` |
| Layer | L5 Business Capability |
| Domain | 06 Engagement |
| Steward | `ucos:org:engagement-content` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P4 (headless CMS, editorial workflow, scheduling, localisation), P5 (video-on-demand/live streaming with DRM, rights windows) |
| Depends on | U43 Asset (files, renditions), U15 Localization (translations), U13 Temporal (publish/unpublish schedules, embargoes, licence windows), U60 Workflow (editorial review), U64 UI (rendering blocks), U44 Search, U28 Entitlement (paywalls, OTT tiers), U88 Social (comments), U49 AI (drafting, labelled), U67 Compliance (content rating, broadcast codes) |
| Depended on by | U64 storefront pages, blogs/marketing sites (U86 SEO), OTT composition, publishers, U56 Learning (course content), U34 help centre rendering |
| Master references | §6.2 U41, U43 (asset ownership), A-63 (P1 static pages fallback) |

> Content owns **structured editorial content and media programmes**: content types (article, page, landing, collection, video, episode, series, live event), entries with structured fields and rich text blocks, editorial workflow and versions, scheduling and embargoes, localisation variants, content rating, rights and licence windows, and streaming packaging (HLS/DASH, DRM keys via providers). Binary files and renditions live in U43.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| CNT-L1 | Publish and unpublish are Temporal schedules; embargoed content is never served before its time. | Edge cache keyed by publish state; TMP triggers. |
| CNT-L2 | Content is served only within its licence windows and territories. | Rights check (U12 territory × U13 window) at playback/render. |
| CNT-L3 | AI-generated or AI-edited content is labelled and passes guardrails. | U49 provenance (C2PA where applicable). |
| CNT-L4 | Age/content ratings are set per jurisdiction scheme before publishing restricted content; access is gated. | Rating required field + entitlement/age gates. |

## 2. Objects
`ContentType { id, fields (U04 types), blocks allowed, workflow, rating scheme }` · `Entry { type, locale variants, fields, blocks, status: draft|in-review|scheduled|published|archived, versions, publishWindow: TimeRange, embargo?: TimePoint, seo (U86) }` · `MediaProgramme { kind: series|season|episode|film|live-event, assets (U43), rights [{territory, licenceRange: TimeRange, platforms}], ratings [{scheme, rating}], drm: {provider, keyIds} }` · `Playlist/Collection` · `LiveEvent { schedule: TimeRange, ingest, dvrDuration: Duration }`.

## 3. Commands, Events, APIs
Commands: `DefineContentType`, `CreateEntry`, `SubmitForReview`, `Approve`, `SchedulePublish`, `Unpublish`, `Localise`, `PackageMedia`, `GrantRights`, `StartLiveEvent`.
Events: `content.entry.published|unpublished`, `content.rights.expiring`, `content.live.started|ended`.
```text
POST /v1/content/types   POST /v1/content/entries   POST /v1/content/entries/{id}:schedule|:publish|:unpublish
GET /v1/content/delivery/{slug}?locale=   POST /v1/content/playback-token
```

## 4. Gaps, UI
```prolog
gap(content_without_rights, P) :- media_programme(P), published(P), not rights_window_covering_now(P).
```
Views: content type designer, entry editor (blocks, preview per channel/locale), editorial calendar, rights & windows matrix, media library, player. T1 (delivery via CDN with stale-while-revalidate).

## Appendix
- **C.** 0.1.0.
