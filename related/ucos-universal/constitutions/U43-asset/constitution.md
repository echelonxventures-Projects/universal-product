# U43 — Asset (Digital Asset Management) Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U43-asset` |
| Layer | L5 Business Capability |
| Domain | 06 Experience |
| Steward | `ucos:org:experience-assets` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 |
| Depends on | U65 Security (classification, encryption, malware scanning), U13 Temporal (rights validity, signed-URL expiry), U66 Privacy (personal images, retention), U73 Infra (object storage, CDN) |
| Depended on by | U18/U21 (product media), U42 Document, U41 Content & Media (P4), U35 (labels, POD), U09 (KYC documents), U64 UI (brand assets), U68 (evidence content) |
| Master references | §6.3 (files → Asset), §6.2 U43 |

> Asset owns **binary files and their derivatives**: upload, storage, malware scanning, metadata extraction, renditions (image sizes/formats, video transcodes, document previews), rights and licences, access (signed URLs, CDN), retention and deletion. Every other universe holds `AssetRef`s; none stores files directly.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| AST-L1 | All files enter via the Asset service (direct-to-storage pre-signed upload + finalize), are malware-scanned and type-verified before use. | Finalize step gates availability; quarantine bucket. |
| AST-L2 | Each asset carries classification, owner, purpose and retention; restricted assets (IDs, medical, POD photos) are encrypted with tenant keys and never served via public CDN. | Schema + delivery policy. |
| AST-L3 | Rights metadata (source, licence, usage scope, expiry) is required for externally sourced media; expired rights → automatic unpublish of dependent usages. | Temporal trigger + dependency graph. |
| AST-L4 | Renditions are derived, reproducible and never edited by hand. | Rendition pipeline from originals + recipe. |

## 2. Objects
- **`BinaryAsset`** `{ id, tenant|global, kind: image|video|audio|document|3d|cad|archive|other, mime (verified), size, checksum sha256, storage: {bucket, key, encryption: sse|tenant-kek}, original filename (PII-tagged), classification, owner, purpose (U66), retention, scan: {status: pending|clean|infected|unsupported, engine, at: TimePoint}, metadata: {dimensions, duration: Duration, exif (stripped of GPS unless purpose allows), pages}, rights?: AssetRights, status: uploading|processing|available|quarantined|deleted }`
- **`Rendition`** `{ asset, recipe (e.g. image:webp:w800:q80, video:hls:1080p), url/key, size, generatedAt: TimePoint }`
- **`AssetRights`** `{ source, licence (CC-BY, commercial, manufacturer-provided), usageScope: [web, print, ads, redistribution-to-tenants], attribution, validity: TimeRange, territories }`
- **`AssetUsage`** (graph edge) — which objects use the asset (for rights expiry and deletion impact).

## 3. Commands, Queries, Events, APIs
Commands: `InitiateUpload(kind, size, purpose)` → pre-signed URL(s) (multipart for large), `FinalizeUpload` (scan + verify + extract), `RequestRendition(recipe)` (also auto per profile), `SetRights`, `DeleteAsset` (blocked if legal hold/usages unless cascade policy), `ShredAsset` (crypto-shred).
Queries: `GetAsset`, `SignedUrl(asset, rendition, ttl ≤ policy)`, `UsagesOf(asset)`.
Events: `asset.asset.available|quarantined|deleted`, `asset.rights.expiring|expired`.
```text
POST /v1/asset/uploads            POST /v1/asset/uploads/{id}:finalize
GET  /v1/asset/assets/{id}        GET  /v1/asset/assets/{id}/url?rendition=&ttl=
POST /v1/asset/assets/{id}/renditions    POST /v1/asset/assets/{id}:delete
```
Errors: `AST_INFECTED`, `AST_TYPE_MISMATCH`, `AST_TOO_LARGE`, `AST_RIGHTS_REQUIRED`, `AST_IN_USE`, `AST_LEGAL_HOLD`.

## 4. Rules
Rendition profiles per use (product gallery, thumbnail, OG image, mobile); image policy checks for product media (decision `asset.product-image-policy`: min resolution, background rules, no watermark/contact info — AI-assisted); EXIF GPS stripped by default; video via HLS/DASH with signed manifests (DRM in U41, P4).

## 5. Security & Compliance
Malware scanning (ClamAV + commercial engine for documents), content moderation for UGC images (CSAM detection mandatory for UGC tenants — legal reporting obligations), private assets via short-TTL signed URLs + watermark obligation for documents; retention per purpose; DSR erasure via `ListReferences` → asset shredding.

## 6. Gaps
```prolog
gap(asset_rights_missing, A)   :- asset(A), externally_sourced(A), published_usage(A), not rights(A).
gap(ugc_without_moderation, T) :- tenant(T), accepts_ugc_media(T), not capability(T, asset.moderation).
gap(rendition_profile_missing, P) :- usage_profile(P), not rendition_recipe(P).
```

## 7. AI
Image tagging/alt-text generation (accessibility; proposals), background removal/enhancement (marked AI-edited), moderation classifiers, OCR for documents (KYC/invoices via U42).

## 8. Operations, UI, Scale
Signals: `uploads_total`, `scan_latency_s`, `quarantined_total`, `rendition_queue_lag_s`, `cdn_hit_ratio`. Views: `asset.library` (grid, filters, usages), `asset.uploader` (drag-drop, progress, resumable), `asset.rights.editor`, `asset.moderation.queue`. Scale: petabytes; S3-compatible storage per cell (residency) + CDN for public renditions; processing workers autoscaled. T1.

## Appendix
- **C.** 0.1.0.
