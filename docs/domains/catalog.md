# Catalogue

> Generated from `_registry/business-domains.json`, the code and `docs/source/catalog.md` — edit those, then run `node scripts/domain-docs.js`.

## Overview

Everything a store sells, described once: products and their variants and SKUs, brands, the category tree, attributes, the platform master every product is described on, the global catalogue and contributions back to it.

**Foundation domain:** Offering · **Used by:** Shopper, Seller, Store staff, Store administrator, Platform administrator

## Switches and settings

Each is switched on per store under ⚙️ Capabilities; its parameters are that store's settings.

### Size guides (`size_guides`)

A table of measurements shown on an item's page, set for an item, a brand or a department.

| Setting | Meaning | Default |
|---|---|---|
| `label` | What the link is called | `"Size guide"` |

### Pre-orders (`preorders`)

Sell an item before it can be sent: the day it ships and how many may be promised.

| Setting | Meaning | Default |
|---|---|---|
| `label` | What the button says | `"Pre-order"` |

## Architecture

| Module | What it is |
|---|---|
| `lib/gcatalog.js` | LUXORA · the global catalogue — the platform master as the platform console and the store import see it (GLOBAL_MASTER.md, P27). |
| `lib/master-contributions.js` | contributions to the platform master and the addenda they leave (GLOBAL_MASTER.md §3, roadmap P28; owner Evolution). |
| `lib/master-permissions.js` | permissions on the platform master (GLOBAL_MASTER.md §2, roadmap P28; owner Authority). |
| `lib/platform-master.js` | the platform master (GLOBAL_MASTER.md, roadmap P27; owners Identity, Semantic, Registry, Relationship and Measure). |
| `lib/preorders.js` | pre-orders: selling an item before it can be sent. |
| `lib/product-counts.js` | an item's own count, and its variant's: the catalog's columns, changed only here. Lowering is one conditional write per row, so a count never goes below zero however many shoppers ask at once; the caller (lib/stock.js) runs it inside its transaction. |
| `lib/size-guides.js` | size guides: the table of measurements that helps a shopper choose a size. |
| `lib/store-attributes.js` | a store's attribute definitions (its "columns"), as a read model of the platform master (GLOBAL_MASTER.md §1, §6; owner Registry). |
| `lib/store-taxonomy.js` | a store's category tree, as a read model of the platform master (GLOBAL_MASTER.md §6, roadmap P27–P28; owner Semantic). |
| `lib/routes/catalog.js` | catalog domain routes (moved from lib/api.js; _registry/business-domains.json). Each handler answers one route of the catalog domain. What it needs from the shared HTTP kit (lib/api.js) is passed in as `kit`. |

**Registry lists** (editable in Data Studio): `contributionStatuses`

## Data model

### `products`

| Column | Type |
|---|---|
| `tenant_id` | INTEGER NOT NULL DEFAULT 1 |
| `id` | TEXT NOT NULL |
| `title` | TEXT NOT NULL |
| `brand` | TEXT NOT NULL |
| `dept` | TEXT NOT NULL |
| `price` | REAL NOT NULL |
| `list_price` | REAL |
| `rating` | REAL |
| `ratings_count` | INTEGER |
| `emoji` | TEXT |
| `hue` | INTEGER |
| `priority` | INTEGER DEFAULT 0 |
| `stock` | INTEGER DEFAULT 0 |
| `flags` | TEXT |
| `keywords` | TEXT |
| `deal_pct` | INTEGER DEFAULT 0 |
| `position` | INTEGER DEFAULT 0 |
| `moq` | INTEGER DEFAULT 1 |
| `compare_enabled` | INTEGER DEFAULT 1 |
| `gift_wrap` | INTEGER DEFAULT 1 |
| `type` | TEXT DEFAULT 'physical' |
| `node_id` | INTEGER |
| `lifecycle` | TEXT DEFAULT 'published' |
| `identity` | TEXT DEFAULT '{}' |
| `attrs` | TEXT DEFAULT '{}' |
| `vertical` | TEXT DEFAULT '{}' |
| `media` | TEXT DEFAULT '[]' |
| `seo` | TEXT DEFAULT '{}' |
| `tax_rule` | TEXT DEFAULT '{}' |
| `geo_rules` | TEXT DEFAULT '[]' |
| `pricing_rules` | TEXT DEFAULT '[]' |
| `logistics` | TEXT DEFAULT '{}' |
| `packaging` | TEXT DEFAULT '[]' |
| `docs` | TEXT DEFAULT '[]' |
| `supplier_id` | INTEGER |
| `uom` | TEXT DEFAULT '{"unit":"ea"}' |
| `tax_profile` | TEXT DEFAULT '' |
| `invoice_profile` | TEXT DEFAULT '' |
| `payment_profiles` | TEXT DEFAULT '[]' |
| `source_universe` | TEXT |
| `source_kind` | TEXT DEFAULT 'seed' |
| `source_global_id` | TEXT |
| `deleted_at` | TEXT |
| `uid` | TEXT |

### `product_bullets`

| Column | Type |
|---|---|
| `tenant_id` | INTEGER NOT NULL DEFAULT 1 |
| `product_id` | TEXT NOT NULL |
| `pos` | INTEGER NOT NULL |
| `text` | TEXT NOT NULL |
| `uid` | TEXT |

### `brands`

| Column | Type |
|---|---|
| `tenant_id` | INTEGER NOT NULL DEFAULT 1 |
| `key` | TEXT NOT NULL |
| `label` | TEXT NOT NULL |
| `icon` | TEXT |
| `logo` | TEXT |
| `story` | TEXT |
| `country` | TEXT |
| `active` | INTEGER NOT NULL DEFAULT 1 |
| `position` | INTEGER NOT NULL DEFAULT 0 |

### `taxonomy`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL |
| `parent_id` | INTEGER |
| `level` | TEXT NOT NULL |
| `key` | TEXT NOT NULL |
| `name` | TEXT NOT NULL |
| `icon` | TEXT DEFAULT '' |
| `attrs` | TEXT DEFAULT '{}' |
| `active` | INTEGER DEFAULT 1 |
| `position` | INTEGER DEFAULT 0 |
| `deleted_at` | TEXT |
| `node_uid` | TEXT |

### `attribute_defs`

| Column | Type |
|---|---|
| `tenant_id` | INTEGER NOT NULL |
| `key` | TEXT NOT NULL |
| `label` | TEXT NOT NULL |
| `grp` | TEXT DEFAULT 'General' |
| `type` | TEXT DEFAULT 'text' |
| `unit` | TEXT DEFAULT '' |
| `options` | TEXT DEFAULT '[]' |
| `validation` | TEXT DEFAULT '{}' |
| `industry` | TEXT DEFAULT '' |
| `position` | INTEGER DEFAULT 0 |
| `category` | TEXT DEFAULT '' |
| `deleted_at` | TEXT |
| `node_uid` | TEXT |

### `skus`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL |
| `product_id` | TEXT NOT NULL |
| `code` | TEXT NOT NULL |
| `name` | TEXT DEFAULT '' |
| `identity` | TEXT DEFAULT '{}' |
| `variant` | TEXT DEFAULT '{}' |
| `price` | REAL |
| `mrp` | REAL |
| `stock` | INTEGER DEFAULT 0 |
| `active` | INTEGER DEFAULT 1 |
| `group_id` | INTEGER |
| `uid` | TEXT |

### `relationships`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL |
| `from_id` | TEXT NOT NULL |
| `to_id` | TEXT NOT NULL |
| `type` | TEXT NOT NULL |

### `variant_groups`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL |
| `product_id` | TEXT NOT NULL |
| `name` | TEXT NOT NULL |
| `axis` | TEXT DEFAULT 'General' |
| `attr_key` | TEXT DEFAULT '' |
| `position` | INTEGER DEFAULT 0 |
| `active` | INTEGER DEFAULT 1 |
| `deleted_at` | TEXT |
| `uid` | TEXT |

### `size_guides`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL |
| `name` | TEXT NOT NULL |
| `scope` | TEXT NOT NULL |
| `target` | TEXT NOT NULL |
| `rows` | TEXT NOT NULL |
| `note` | TEXT NOT NULL DEFAULT '' |

### `preorders`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL |
| `product_id` | TEXT NOT NULL |
| `ships_on` | TEXT NOT NULL |
| `max_qty` | INTEGER NOT NULL |
| `taken` | INTEGER NOT NULL DEFAULT 0 |

## API reference

Every call is JSON over HTTPS; store calls carry the store (`?store=`) and the session; mutating calls accept an `Idempotency-Key` header where noted.

| Method and path | Handler | What it does |
|---|---|---|
| `GET /api/products/:id/size-guide` | `apiSizeGuide` | the size guide an item shows |
| `GET /api/admin/size-guides` | `apiAdminGuides` | the store's size guides |
| `POST /api/admin/size-guides` | `apiAdminGuideSave` | adds or changes a size guide |
| `DELETE /api/admin/size-guides/:id` | `apiAdminGuideDelete` | removes a size guide |
| `GET /api/admin/preorders` | `apiAdminPreorders` | the items on pre-order |
| `POST /api/admin/preorders` | `apiAdminPreorderSave` | puts an item on pre-order, or changes its day and how many may be promised |
| `DELETE /api/admin/preorders/:id` | `apiAdminPreorderDelete` | takes an item off pre-order |
| `GET /api/platform/global-products` | `apiGlobalProductList` | ========== Global Product Catalog API ========== The global catalogue is the platform master as the console edits it (lib/gcatalog.js projects a master item into a record and writes a record back as master writes). Every dropdown the form shows comes from the API: universes and media kinds from the registry, categories and lifecycle states from the master, the profile fields from the product entity. |
| `POST /api/platform/global-products` | `apiGlobalProductCreate` | — |
| `PUT /api/platform/global-products/:id` | `apiGlobalProductUpdate` | — |
| `DELETE /api/platform/global-products/:id` | `apiGlobalProductDelete` | — |
| `GET /api/platform/store-product-config` | `apiStoreProductConfig` | — |
| `GET /api/platform/master/tree` | `apiMasterTree` | — |
| `GET /api/platform/master/vocabulary/:key` | `apiMasterVocabulary` | — |
| `GET /api/platform/master/permissions` | `apiMasterPermissions` | — |
| `POST /api/platform/master/permissions` | `apiMasterPermissionGrant` | — |
| `DELETE /api/platform/master/permissions/:id` | `apiMasterPermissionRevoke` | — |
| `GET /api/platform/master/contributions` | `apiMasterContributions` | — |
| `POST /api/platform/master/contributions/:id/review` | `apiMasterContributionReview` | — |
| `GET /api/tenant/master/permissions` | `apiStoreMasterPermissions` | — |
| `GET /api/tenant/master/contributions` | `apiStoreContributions` | — |
| `POST /api/tenant/master/contributions` | `apiStoreContributionPropose` | — |
| `POST /api/tenant/master/contributions/:id/withdraw` | `apiStoreContributionWithdraw` | — |
| `GET /api/tenant/master/items/:ref` | `apiStoreMasterItem` | — |
| `POST /api/platform/store-product-config` | `apiStoreProductConfigSet` | — |
| `DELETE /api/platform/store-product-config/:tenant_id/:global_id` | `apiStoreProductConfigDelete` | — |
| `GET /api/tenant/products` | `apiStoreProductPermissions` | — |
| `GET /api/platform/global-catalog` | `apiGlobalCatalog` | ========== UPIP §1/§5 · Universal Global Catalog ========== The platform's catalogue is populated automatically (one canonical product per corpus universe) and manually (console rows). A store admin may pull a global product into their own catalogue ONLY when the platform has permitted it — the "if the Global Platform permits" clause, enforced by lib/gcatalog.js, never by the store. |
| `GET /api/tenant/catalog/importable` | `apiStoreCatalogImportable` | — |
| `POST /api/tenant/catalog/import` | `apiStoreCatalogImport` | — |
| `GET /api/platform/attributes` | `apiAttributeList` | — |
| `POST /api/platform/attributes` | `apiAttributeCreate` | — |
| `GET /api/taxonomy` | `apiTaxonomy` | — |
| `GET /api/products` | `apiProducts` | — |
| `GET /api/products/:id` | `apiProduct` | — |
| `GET /api/admin/products` | `apiAdminProducts` | — |
| `GET /api/admin/products/:id` | `apiAdminProductGet` | — |
| `POST /api/admin/products` | `apiAdminProductCreate` | — |
| `PUT /api/admin/products/:id` | `apiAdminProductUpdate` | — |
| `PUT /api/admin/products/:id/meta` | `apiAdminProductSaveMeta` | — |
| `POST /api/admin/products/:id/lifecycle` | `apiAdminLifecycle` | — |
| `POST /api/admin/products/:id/relationships` | `apiAdminRelationshipAdd` | — |
| `DELETE /api/admin/products/:id` | `apiAdminProductDelete` | — |
| `GET /api/admin/taxonomy` | `apiAdminTaxonomy` | — |
| `POST /api/admin/taxonomy` | `apiAdminTaxSave` | — |
| `PUT /api/admin/taxonomy/:id` | `apiAdminTaxSave` | — |
| `DELETE /api/admin/taxonomy/:id` | `apiAdminTaxDelete` | — |
| `GET /api/admin/attributes` | `apiAdminAttributes` | — |
| `POST /api/admin/attributes` | `apiAdminAttrSave` | — |
| `DELETE /api/admin/attributes/:key` | `apiAdminAttrDelete` | — |
| `POST /api/admin/skus` | `apiAdminSkuSave` | — |
| `PUT /api/admin/skus/:id` | `apiAdminSkuSave` | — |
| `DELETE /api/admin/skus/:id` | `apiAdminSkuDelete` | — |
| `DELETE /api/admin/relationships/:id` | `apiAdminRelationshipDelete` | — |

## Process flows

Each record's life is a declared state machine (`lib/seed/states.json`): the moves it may make, and the actions that make them.

### Contribution to the platform master (`contribution`)

```mermaid
stateDiagram-v2
  [*] --> proposed
  proposed --> approved
  proposed --> rejected
  proposed --> withdrawn
  approved --> [*]
  rejected --> [*]
  withdrawn --> [*]
```

Actions: `approve` → approved · `reject` → rejected · `withdraw` → withdrawn

## Data flow

```mermaid
flowchart LR
  U([Shopper / Seller / Store staff / Store administrator / Platform administrator]) --> UI[product.html, store console, platform console]
  UI --> API[54 API routes]
  API --> ENG[gcatalog.js, master-contributions.js, master-permissions.js, platform-master.js, preorders.js, product-counts.js, size-guides.js, store-attributes.js, store-taxonomy.js, catalog.js]
  ENG --> DB[(products, product_bullets, brands, taxonomy, attribute_defs, skus, …)]
  ENG --> SM{{1 state machines}}
```

## User interface

**Pages:** `product.html`

**Store console:** 📦 Products · 🔖 SKUs & Inventory · 🏷️ Brands · 🌳 Taxonomy · 🧬 Attributes · 🌐 Global Catalog · 🤝 Master Contributions · 📏 Size Guides · ⏳ Pre-orders

**Platform console:** 🌐 Global Products · 🗳️ Master Review · 🔐 Master Permissions · 👨‍👩‍👧 Product Families · 📦 Product Types · 🧬 Variants · 🧩 Attributes · 📐 Specifications · 🧺 Bundles · Kits · 📚 Collections · 🕸️ Product Graph · 🗄️ Product Registry · 📐 Entity Definitions · 📦 Catalog · SKUs · 🗂️ Industry · Categories · 🏷️ Category Tree · 🌳 Taxonomy Universe · 🚚 Suppliers · 🤝 Vendors · 🏭 Manufacturers · 🧱 Assets · 📄 Documents · 🎬 Media · 📝 Content

## User flows

_Not yet written — `docs/source/catalog.md`, section `## Flows`._

## Manuals

### Shopper

_Not yet written — `docs/source/catalog.md`, section `## Manual: shopper`._

### Seller

_Not yet written — `docs/source/catalog.md`, section `## Manual: seller`._

### Store staff

_Not yet written — `docs/source/catalog.md`, section `## Manual: store_staff`._

### Store administrator

_Not yet written — `docs/source/catalog.md`, section `## Manual: store_admin`._

### Platform administrator

_Not yet written — `docs/source/catalog.md`, section `## Manual: platform_admin`._

