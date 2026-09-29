# MEMORY.md — project facts

## Project: LUXORA (workspace `/Users/bipin/Desktop/Desktop-10-Sept-26/Amazon`)

Universal white-label multi-tenant commerce platform. **Zero runtime dependencies** — Node ≥ 22.5 with
`node:http` / `node:sqlite` / `node:crypto` only, plus vanilla-JS frontends. The guiding principle is
"everything is entity data, never code" (taxonomy, industries, providers, countries, runtime backends).

### Layout
- `server.js` — multi-tenant routing, security middleware, SRI, static serving
- `lib/api.js` — ~110 REST routes (largest file, ~2 760 lines)
- `lib/db.js` — SQLite schema + column migrations + seed (~1 115 lines)
- `lib/entity.js` — entity engine; `lib/security.js` — L1–L10 primitives
- `lib/registry.js` / `lib/meta.js` / `lib/providers.js` — seed data
- `public/` — storefront + store console (`admin.html`) + platform console (`platform.html`)
- `test/smoke.js` — the whole E2E suite (single file, jsdom)
- Docs: `README.md`, `FLOWS.md` (pictorial flows, §25 = PG cutover), `USER_MANUAL.md`

### Commands
- `npm start` (port 3000), `PORT=8787 ./serve.sh` (supervised), `./stop.sh`
- `npm test` — syntax check + jsdom E2E. Takes ~70s. Run it in the background.

### Conventions worth remembering
- `data/luxora.db` is the default SQLite path; override with `LX_DB`.
- Security layers are referred to as **L1–L10** throughout code comments and docs.
- Features are gated by writing config rows, never by code branches ("OFF-by-default, fill-in-the-blank").
- `INSERT OR IGNORE` is used deliberately for idempotent registry seeding — it matters when translating SQL.

### In-flight work (as of 2026-09-17)
The SQLite→Postgres cutover ("B"). The async dual-engine (`lib/sql.js` dialect translator, `lib/pg.js`
wire client, `lib/migrate.js` planner) is committed; the *request path* now runs through a synchronous
bridge (`lib/pgbridge.js` + `lib/pgworker.js`, worker + SharedArrayBuffer + `Atomics.wait`) gated on
`LX_DB_DRIVER=postgres` + `LX_PG_URL`. That work is uncommitted and reviewed in `REVIEW.md`.

### 2026-09-27 — the corpora are now activated + traceable
The three Architecture documents declare 24,139 concepts / 1,877 universes. They were registered and
instantiated at 100% but NOT transactable (0 published) and there was no map from a corpus declaration
to its runtime artifact. Closed in one pass, all suites green (608 E2E + 539 constitution assertions):

- `lib/ucos.js::productUniverses()` reads the UPIP §1 VISION product-universe vocabulary straight from
  the document (26 universes, no hardcoded list) and seeds it into `meta_lists` as `productUniverses`
  (`lib/registry.js`), merged additively so operator additions survive a corpus re-parse.
- `global_products.universe` column + console picker/filter; unknown universes fall back to
  `physical_products`, never a free string (`validProductUniverse` in `lib/api.js`).
- **Activation** (`lib/ucos-catalog.js`): `activate`/`activateAll` materialize a universe's canonical
  offering from its own corpus-declared fields and publish it — idempotent, limit-bounded. API:
  `POST /api/ucos/catalog/activate[/:key]?tenant_id=N`. Platform-only; refuses unknown tenants.
- **Traceability** (`lib/ucos-trace.js`, console → 🧭 Traceability): any key → 8 runtime layers
  (registry concept → foundation → universe → live entity → records → catalog projection → API →
  console), absent layers reported, `GET /api/ucos/matrix` for the corpus-vs-runtime totals.
- `test/ucos-activation.js` proves 287 universes across 267 families follow the full generic path
  (activate → publish → SKU+inventory → withdraw) — i.e. no family got special treatment.
- `IMPLEMENTATION_MAP.md` is the honest corpus→runtime map, including the gaps that remain by design
  (per-domain UX, per-universe RBAC, activation opt-in and empty by default).

### 2026-09-27 (later) — per-domain state machines + universal theming
The last two "not 100%" gaps closed, still Configuration-Over-Code:
- **Per-domain engine** (`lib/ucos-domain.js`): every universe's records move through the state machine the
  corpus declares — states read structurally out of Architecture3 §5.1 (`ucos.lifecycleStates()`, never a
  constant), transitions derived from 5.2's rules (certification for Canonical, dependents-retired for
  Retired), UMQSOCR Art. 10's grammar surfaced as data. Ledger `ucos_record_transitions`, append-only.
  API `GET /api/ucos/domain/:key`, `POST /api/ucos/domain/:key/fire`. Console → 🔀 Domains (kanban board).
- **Universal theming** (`lib/themes.js`): themes are DATA (`theme_presets` + `theme_assignments`).
  Presets are GENERATED from a hue anchor by one `ramp()` function (8 shipped incl. Quantum Glass,
  Neon Noir, CRT Amber), and an operator dials any hue and names it → permanent preset. The assignment
  cascade is product → dept → tenant → platform (`resolve(ctx)`); a store with no assignment keeps its
  own `settings.theme` (zero regression). API `/api/themes*`. Console → 🎨 Themes.
- **Found and fixed a real regression**: `public/css/styles.css` had shrunk from the original 507 lines to
  42 — every storefront class (`pcard`, `buybox`, `pp-grid`, `r-grid`, `pimg`, `banner`…) was missing, so
  the "universal UI" literally had no styles. Restored from the initial commit and appended the adaptive-
  domain card CSS + theme-var hooks (`--glow`, `--font-display`). **When UI looks unstyled, check this file
  against `git show cc78fd6:public/css/styles.css`.**
- The storefront card is now adaptive: affordances derive from the record's own type (`typeMeta()` in
  `public/js/app.js`) — instant access for digital, bookable for services, cycle pricing for subs/rentals.
- Suite: 620 E2E + 585 constitution/theme assertions, all green.

### 2026-09-27 (final) — §394/§395 dashboard & reporting engine
Architecture1 §394/§395 were registered as concepts but had NO generic engine. Closed with
`lib/dashboards.js` — a dashboard is a row in `dashboards`, every widget a row in
`dashboard_widgets` pointing at an ENTITY + a METRIC, and one `aggregate()` computes it.
There is no per-dashboard code anywhere; an operator adds a KPI from the console.

- **Two storage shapes, one engine**: native entities (orders, products…) take one
  parameterized SQL aggregate; JSON entities (the corpus universes `uv_*`) compute the same
  metric over decoded `entity_data`. A widget looks identical either way, because universes
  are first-class entities — "how many Insurance records are Canonical" is a widget, not a
  feature. Uniform output: `{value}` scalar or `{buckets:[{key,value}]}`.
- **Security (L10)**: `specOf()` whitelists metric/kind against vocabularies and
  column/dimension/filter against the entity's *declared* fields — a crafted widget row can
  never smuggle arbitrary SQL. The filter is normalized from string-or-object BEFORE the
  whitelist check, so an unparseable filter is rejected, not silently dropped.
- **§1439 identity + personalization**: audience enforced at *render* time, not just in the
  listing (a store admin can't render a platform board by guessing its key); each operator's
  widget order/visibility is a `dashboard_prefs` row.
- **§395 reporting**: a report is a row (`reports`) declaring entity/metrics/dimensions/filter;
  `runReport()` walks Data → Analytics → Visualization → Report from the same aggregate.
  Scheduling is opportunistic — `isDue()`/`runDue()` fire when reports are listed, so there is
  no separate scheduler process to deploy.
- Tables in `lib/db.js`: `dashboards`, `dashboard_widgets`, `dashboard_prefs`, `reports`.
  Seed (`lib/registry.js`) ships 4 canonical boards (store-executive/operational/marketplace +
  platform-compliance) + 3 reports as platform templates (tenant_id NULL), `INSERT OR IGNORE`
  so console edits survive restart.
- API `/api/dashboards*` + `/api/reports*` (thin, no per-dashboard routes); console → 📊 Dashboards.
- **Suite: 620 E2E + 863 audit assertions (68 new), all green.** Nothing declared in the
  architecture remains without an engine.

### 2026-09-28 — the global catalog: every archetype is real, and the platform gates listing
The requirement "products are added automatically AND manually to the global platform; a
store admin may add them to their listings IF the Global Platform permits" was only half
true: `global_products` CRUD existed (manual) but nothing ever seeded it (0 rows on every
boot), and the permission table `store_product_config` existed but had no import action and
no store-console UI — the gate was readable but had no consequence. Closed with
`lib/gcatalog.js` (zero per-archetype code):

- **Automatic**: every universe the corpus declares seeds ONE canonical platform product
  (26 rows, `UPIP-*` SKUs), idempotently — a warm boot writes nothing and the seed never
  clobbers an operator's edit. **Manual**: an operator row is just another row.
- **The gate is real** (`mayList`/`importToStore`): import is refused with no permission
  row, refused on a read-only grant, allowed on list/sell; a store can never widen its own
  access. Retired archetypes refuse even with a grant.
- **Import is honest**: idempotent (re-import refreshes the same row via `source_global_id`,
  never duplicates), typed from the universe itself, creates a default SKU + inventory, and
  is quota-exempt (`source_kind='global'`, same rule as universe activations — platform
  supply is not the merchant's own catalogue).
- **Activation types are derived, not hardcoded**: `projection()` in `ucos-catalog.js` had
  `type: r.type || "service"`, so all 1,877 universes activated as "service". Now
  `typeOfUniverse()` resolves via the productTypes registry vocabulary in three steps
  (record's own type → the §1 archetype map → structural match like `insurance`→insurance),
  falling back to `service` for unmapped universes so Future Unknown never breaks activation.
- **Three latent route bugs found and fixed** (`api.js` router passes params POSITIONALLY as
  `fn(req,res,url,session,body,params[0],params[1],metrics)`, but several route arrows did
  `(r,re,u,s,b,p) => fn(...,p[0])`, so `p` was the string `"27"` and `p[0]` was its FIRST
  CHARACTER `"2"` — every global-products PUT/DELETE and the store-product-config DELETE
  silently targeted the wrong row; harmless only while the catalog was empty).
  **When a route param lands as a single digit, check for `p[0]` on a positional arrow.**
- Console: store console → 🌐 Global Catalog (per-product permitted/denied/imported state +
  import); platform console → Global Products gained a "Store access" column with a
  grant/revoke modal (read/list/sell/none per tenant).
- **Suite: 620 E2E + 921 audit assertions, all green** (58 new global-catalog checks).

### 2026-09-28 (later) — console design system rebuilt (Amazon/AWS caliber, touch-first)
Both consoles were described as "pathetic and cheap". Root causes found by auditing the
CSS: the old `portal.css` was a dark gold-on-black theme, several view classes were
**completely unstyled** (`p-sub`, `p-head`, `p-code`, `p-err`, `p-stats`, all `a-*`), the
sidebar had no mobile story, and touch targets were ~30px.

- `public/css/portal.css` rewritten as one design system for BOTH consoles: light canvas,
  deep-navy sidebar, AWS-style blue primary, sticky table headers, 38px min touch targets,
  visible focus rings (a11y), badge semantics extended (canonical/retired/certified…).
  Every class name the views emit was preserved — no view JS had to change for restyling.
- **Responsive drawer**: ≤1100px the sidebar goes off-canvas; both shells (`shell()` in
  admin.js + platform.js) now emit a hamburger, a close button and a scrim, wired by a
  shared `wireDrawer()` that closes on navigation or scrim tap. ≤720px grids collapse to
  one column and `.p-user` hides.
- Touch: `@media (hover: none) and (pointer: coarse)` adds tap highlight, press feedback,
  momentum scrolling (`-webkit-overflow-scrolling: touch`) on every scrollable surface.
- **Suite still 620 E2E + 921 audit, 0 failures** (the jsdom console renders are part of
  smoke.js — they exercise the new shell markup).

### Tooling gotcha
macOS ships BSD grep, which does **not** support `\|` alternation in basic regex — `grep "a\|b"` silently
returns nothing. Use `grep -E` or the Grep tool instead.

### 2026-09-28 (session) — nav organised, product form made structured + universe-derived
Two console UX asks, both closed Configuration-Over-Code:

**Nav grouped by function.** Both consoles had one flat list (45 store / 30 platform
items). `NAV` in `admin.js`/`platform.js` is now an array of `{g, items:[[key,label]…]}`
groups (store: Overview · Catalogue · Orders & Fulfilment · Marketplace & B2B · Payments &
Finance · Growth & Retention · AI & Automation · Identity & Access · Geo & Localization ·
Compliance & Risk · Settings & Data · Reference; platform: Command · Stores & Billing · Geo
& Global Catalog · Constitution Ω∞ · Identity & Theming · Registry & Runtime · Data,
Insights & Audit · Reference). A `NAVFLAT = NAV.flatMap(g => g.items)` keeps the title
lookup working; `canSee`/`NAVSEC` key off the flat keys and are untouched. Every view key
is byte-identical to before (verified by diffing keysets against `HEAD`). CSS: `.p-nav-grp`
with a `<small>` label, divider between groups.

**The "Add product" form was thin, and the reason was structural.** The platform
`gpModal` (platform.js) was hand-rolled against the bare `global_products` table —
attributes/media were raw JSON textareas. Fix, per the corpus's own declarations:
- **`public/js/editors.js`** (new, loaded by both console shells): `mediaEditor()` and
  `kvEditor()` mount into a host element, own their model, re-render on add/remove, sync
  every keystroke, and return a value accessor the console reads at save time — never a
  textarea. Media rows: kind select (options from the registry's `mediaKinds` vocabulary),
  label, and a URL-or-emoji reference. **`esc` collision gotcha**: editors.js first
  declared `const esc`, which is a *fatal* SyntaxError against the console scripts' own
  global `esc` (classic scripts share one scope). Renamed to a private `escAttr`.
  **jsdom gotcha**: an `input` event dispatched without `{bubbles:true}` never reaches a
  listener attached on the parent row — real user input bubbles, tests must too.
- **Universe-derived configuration**: `GET /api/platform/universe-fields/:key`
  (`universeFieldsOf`) returns the corpus-declared fields for a universe. The corpora
  *disagree on keys*: UPIP §1's `productUniverses` (e.g. `insurance_products`) vs the
  instantiated `uv_*` entity keys (`uv_insurance_product`), only 1 of 26 matched exactly.
  Resolved by normalized matching (strip punctuation/underscores, trailing `s`, filler
  words `product`/`types`) and, on collision, preferring the entity that actually DECLARES
  the most config fields (the bare `*_product` shells carry only name/code/status/attrs).
  17/26 resolve; the rest (Subscriptions, OTT, API Products…) have no entity in the corpus
  at all and the form falls back to custom attributes — never an invented field.
- **Storefront media**: `img()` in app.js now renders a real `<img>`/`<video>` when a media
  entry carries a `url`, and the product gallery's thumbs/main swap by cloning the tile.
  `.pimg-url` CSS in styles.css.
- **API is the last line of defence**: `validMedia()` coerces unknown kinds to `image` and
  drops entries with no label/URL/emoji; `apiGlobalProductList` now PARSES the `media`/
  `attributes` TEXT columns before returning them (the console edits structured data —
  feeding it a JSON string it would stringify again silently wiped the field on edit).
- **Real latent bug found**: `global_products` was empty on the live DB because
  `registry.js` refreshed the `productUniverses` meta_lists row only when the corpus digest
  changed (`if (!seeded.skipped)`) — a database predating the vocabulary never changes the
  digest, so it stayed missing forever and the catalog seeded nothing. The smoke tests use
  a throwaway DB, so they never saw it. Now also refreshes when the row is absent.
  **When a registry list is empty on a warm DB, check whether its seed is digest-gated.**
- **Suite: 635 E2E + 936 audit, 0 failures.** New: 15 structured-form/media assertions in
  smoke.js and 4 warm-boot/catalog-seed checks in ucos-catalog.js (36, was 32).

### 2026-09-28 (later) — the form's vocabularies are the registry's; the universe owns the type
The rebuilt form still hardcoded three things the registry already shipped, and kept a
checkbox that could contradict the universe selection:

- **Removed "Is a service (not a physical good)"** — it duplicated the universe dropdown.
  `universeProductTypes` (a meta_lists row gcatalog.js seeds) maps universe → product type,
  and `typeOfUniverse()` resolves it; the seed, the store listing and the import path all
  derive the type from there. The API now derives `is_service` on create AND update
  (`api.js`), so a product moved between universes moves its type with it, and a caller
  forcing `is_service:true` on a physical universe is ignored. The form shows the derived
  type as a read-only `.gp-derived` badge instead of an editable box. **The universe is the
  authority on type; is_service is its consequence.**
- **Tax class** was a hardcoded 4-item list; `taxClasses` ships 6 (incl. *Digital services*,
  *Groceries*). **Category** was free text despite a 33-entry industries registry and a
  147-row taxonomy. Both are now registry-driven selects; the API returns them
  (`platformCategories()` = industries + category/subcategory taxonomy keys) alongside
  `taxClasses`, `mediaKinds` and `universeProductTypes` in the global-products response.
- **Removed the redundant hint** ("The configuration section below is…") — the section
  header already names the universe. The dropdown's hint now explains what the universe
  actually governs (type + configuration).
- **Live-DB vs throwaway-DB trap (recurring)**: three vocabularies came back empty on the
  live server while tests stayed green, because a stale `node server.js` was still holding
  port 8787 — the new process died with `EADDRINUSE` and my curl hit the old code. **Before
  believing a live check, confirm `pgrep -af "node server.js"` shows ONE process and
  `lsof -iTCP:8787` matches it; `kill` by pid, then `./serve.sh`.**
- **Suite: 646 E2E + 936 audit, 0 failures** (11 new assertions for the vocabularies and
  the derived type, incl. an edit that moves a product between universes).

### 2026-09-29 — two real bugs found by exercising the store console's save paths
The uncommitted console/form work was finished but never committed, and its own test
surfaced two defects when the generic form's SAVE path (not just render) was walked:

- **`wireEditors()` was pasted into the wrong function.** It belongs in `openForm()`
  (which has `fields`/`row`/`registry` in scope and emits the `data-editor` host divs),
  but the call landed in `wirePayments()`' gateway-Configure handler, where those names
  do not exist → a `ReferenceError` thrown *after* the modal was shown but *before* its
  close/save handlers were wired (the gateway modal opened and could never be closed or
  saved). Meanwhile `openForm` never got the call, so the media/attrs host divs stayed
  empty, `collect()` read `.value` off a `<div>` and **silently dropped media on every
  entity-form save**. Both sides fixed; the test now asserts the handlers wire AND that a
  media row round-trips through the form.
- **`apiEntities` stripped string `options`, silently unpublishing products.** The served
  entity def kept `options` only when it was an inline array; `options: "lifecycle"` /
  `"productTypes"` are STRING registry vocabulary references, so they became `undefined`.
  Every vocabulary-backed select rendered with **zero options**, `collect()` submitted `""`,
  and saving any product edit wiped its `lifecycle` (draft → unpublished → invisible on the
  storefront) and its `type`. The console's `fieldInput` has explicit `if (f.options ===
  "lifecycle")` special cases that only work when the string survives — the strip defeated
  them. Fix: keep options when array OR string. Guard assertions: the select is populated
  (≥7 options) and preselected to the record's value, and an edit that never touched
  lifecycle leaves it byte-identical.
- **Test-writing gotcha**: verify a console write through the console's OWN channel
  (`/api/meta/entity/product?id=X` — filtered, uncapped, no published filter). The
  storefront `GET /api/products/:id` is a poor witness: it only serves `published` rows,
  earlier smoke steps mutate the VR-* products, and the entity browse window is capped at
  500 (sorted id DESC) so a storefront product may not even be in the rendered table.
- **Suite: 659 E2E + 828 audit, 0 failures** (13 new store-console assertions).

### 2026-09-29 (session 2) — the six-platform parity layer is now real, and 14 of its writes were broken
The uncommitted "Universal Commerce Parity Layer" (Amazon · Flipkart · Zepto · Blinkit ·
Paytm · Alibaba) shipped five engines + 40 tables + 46 registries, but it had **no test at
all** and was never wired into `npm test`. `test/parity.js` (new, 191 assertions) proved the
engines work and, in proving them, found **14 real defects** — the kind that only appear when
a write path is actually walked:

- **13 INSERT statements were one placeholder short.** Every one was an INSERT whose VALUES
  list held a literal (a status default like `'queued'`/`'issued'`/`'active'`) and whose
  column count was N while placeholders + literals summed to N-1 — so *every* call through
  that path threw `N values for N+1 columns`. Affected: `payment_links`, `bank_payouts`,
  `recharges`, `bnpl_accounts`, `bnpl_emis`, `insurance_policies` (fintech); `gold_suppliers`,
  `company_verifications`, `letters_of_credit`, `rfq_quotes` (trade); `seller_onboarding`,
  `seller_performance`, `buyer_claims`, `smart_fulfilment` (marketplace). The engines had
  never been executed end-to-end — the syntax check passes because the SQL is a string.
  **When an INSERT has an inline literal, count columns vs VALUES entries; `node --check`
  cannot see this.** A paren/quote-aware INSERT audit is now worth keeping (it caught all 13
  in one pass after the hand-counting proved unreliable).
- **`receiveFba` used `ON CONFLICT(tenant_id,sku_id,warehouse_id)`** — the legacy `inventory`
  table has no such UNIQUE constraint → invalid SQL, every FBA receive died. Replaced with a
  read-then-write accumulate.
- **Two ambiguous `id` columns** in `computePerformance` (`returns JOIN orders`, and the
  shipments subquery) — qualified every selected column.
- **`acceptQuote` returned the pre-update row** (status still `submitted`), and `quoteRfq`/
  `bid` returned the row as read *before* ranking rewrote `rank`, so callers saw `rank: 1`
  for both competitors. Now both return a fresh read after the rank pass. **A returned row
  must be re-read after any UPDATE that mutates it — the object you hold is stale.**
- **`quoteRfq` accepted further quotes on an already-accepted RFQ** — `accepted` wasn't in
  the closed-status check.
- **`apiMktClaimOpen` / the two QC dispatch handlers called `logAction(...)` without the
  `req` argument**, so the meta object landed where `req` belonged and `ipOf` broke.
- **`audit()` in db.js silently dropped entries for guest actors.** `actor()` returns
  `["guest", null, s.sid]` and `s.sid` is the whole session *object*; binding an object to
  a TEXT column throws `Provided value cannot be bound to SQLite parameter 4`, swallowed by
  the `catch` — so guest audit rows never landed AND printed a confusing line. `audit()` now
  coerces actor id/name before binding.
- **`upi()` hid a newly-added VPA from its owner** (`status='active'` filter vs
  `addUpi` creating `pending_verification`) — you'd add a bank account and see nothing.
- **`pinCart` had no min-order path**; a cart below `min_order` failed as
  `insufficient_store_stock` with no way to tell the customer the real reason. New
  `below_min_order` reason carrying the gap.
- **`spendBnpl` returned one EMI row** instead of the schedule it generates — the API field
  is named `emis` and the console can't render one row as a plan.

Fixes were applied by *rewriting* `lib/fintech.js`, `lib/trade.js`, `lib/marketplace-ext.js`
whole (a scripted repair corrupted them and, being untracked, `git checkout` could not
restore them — **untracked files have no undo; back them up before a scripted rewrite**).
`test/parity.js` asserts each engine's real contract: registries are the only vocabulary
(an added state becomes usable with no code change), money never leaves the single wallet
ledger, escrow holds/release compose with trade assurance, splits must sum, KYC gates credit,
the buy-box has exactly one winner, and bids rank lowest-first. Added the 4 new files to the
`npm test` syntax-check list. The live DB at 8787 now seeds all 46 registries and 40 parity tables on boot.

### 2026-09-29 (session 3) — the capability layer was never seeded, so marketplace + trade were inert
Resumed on the uncommitted parity work. The memory above claimed "659 + 191, 0 failures"; it was
**not** green — `npm test` died at `test/parity.js`'s buy-box block. Root cause, found by walking it:

- **`lib/capabilities.js::seed()` / `seedPresets()` were never called by anything.** `lib/db.js`'s
  boot block seeded the parity *registries* and the QC demo store, but not the capability catalog.
  Worse, nothing ever wrote a `capability_values` row for any tenant, and `cap()` answers `{}`
  unless the capability is ON for the tenant — so **every `caps().cap()` call in
  `marketplace-ext.js` and `trade.js` was inert** (buy-box returned `winner: null`, FBA, health,
  claims, smart-fulfilment, trade assurance, LCs, RFQ all no-ops). `qcommerce.js` and `fintech.js`
  don't call `cap()` at all, which is why their sections passed and pointed the finger at
  marketplace. **A gate nobody can open is indistinguishable from a broken engine — and a section
  that passes while its neighbours fail usually means it skips the shared gate.**
- Fix: the `db.js` boot block now seeds the catalog + presets and applies `blend_marketplace` to the
  flagship **on first boot only** (guarded on the tenant having no `capability_values` row, so a
  reboot never resets a parameter an operator tuned — same "operator owns the row" rule as every
  other seed). `test/parity.js` asserts the switch itself (a capability no composition enabled is
  off/inert; applying `blend_marketplace` + `blend_b2b_trade` turns the engines on; params are read
  from the layer, not constants) before exercising them.
- Verified on the live DB after a restart: 32 capabilities, 5 presets, tenant 1's marketplace
  composition live with `buy_box` params resolving correctly. Trade stays OFF on live by design
  (the test opts it in) — **the parity layer still has no API route and no console view, so an
  operator cannot currently flip a capability from the UI. That is the next gap.**
- **Suite: 659 E2E + 195 parity (4 new capability assertions) + 197 conformance, 0 failures.**
  Live: single supervised process on 8787, healthz green.
- Reminder honoured: `pgrep -f "node server.js"` matches its OWN shell wrapper (the arg string
  contains the pattern), so it looks like a phantom respawner. **`lsof -iTCP:PORT -sTCP:LISTEN`
  is the authoritative "is it running" check, not pgrep.**

### 2026-09-29 (session 4) — no vendor name is a definition; the platform is configured, never templated
Reviewing the parity layer, the owner's standing rule was violated: **Amazon · Flipkart · Zepto ·
Blinkit · Paytm · Alibaba were baked into the code as definitions** — 62 occurrences across
`lib/*.js` and `test/parity.js`. An audit proved NONE was in an identifier, key, table or branch;
all of it was in comments and in the *seeded descriptions an operator reads* ("Amazon-style account
health", "the composition an Alibaba-style operator would recognise"). The two remaining hits are
legitimate third-party *integrations* (the `paytm` payment gateway in providers.js, the S3 endpoint
in adapters.js) — those are external services the platform connects to, not branding the platform
defines. Closed in one pass:

- **Every definition de-vendored.** The catalog now describes what a capability does, never whose
  it is; the test header/banner reframed from "six-platform parity" to "the configurable platform",
  and `parity.js` now *asserts* the invariant (`/amazon|flipkart|zepto|blinkit|paytm|alibaba/i` must
  not match any served label or description) so it cannot creep back. Key names were already clean
  (`buy_box`, `blend_marketplace`, `qcStoreKinds`).
- **The catalog is now a revisioned, self-healing row set.** `seed()` stamps `cap_v2`; a row nobody
  has touched follows the catalog when the stamp moves, and a new `edited` column (column migration
  in db.js) means the moment an operator edits a row from the console the catalog never clobbers it.
  This also fixed a latent lie: the old self-heal condition (`!seeded_from`) could never fire after
  first boot, so the catalog could never have evolved at all.
- **The missing configuration surface was built** — the layer had no API and no console view, so an
  operator could not configure a thing. Now: `GET/POST /api/capabilities*` (catalog + archetypes +
  composition read; per-store enable/disable; typed param tuning; platform-level switch; archetype
  author/apply/delete) and platform console → ⚙️ Capabilities: domain-grouped catalog, per-store
  on/off, an expander that scaffolds each param from its DECLARED type/default (pre-filled with the
  tenant's effective value, and still scaffolded when the capability is off), plus an archetype
  builder so a custom platform/service is authored as rows.
- **Typed tuning is the safety story**: `coerce()` validates every param against its declared type
  and refuses an unknown capability, unknown param, or uncoercible value — a configured standard is
  validated, never silently dropped. Authority: a store admin composes only its own store
  (`capTenantScope`), platform-only for catalog/archetype writes, and a store cannot enable a
  capability the platform disabled (the gate never widens).
- **Test gotcha caught by the suite**: `enable`/`param`/`applyPreset` return the composition object
  DIRECTLY (`{tenant_id, preset, capabilities}`), not wrapped under `.composition` — my first pass
  asserted `resp.composition` and got 4 false failures that looked like engine bugs. And a probe
  archetype saved with only a phantom capability REPLACES its capability set, so use a separate key
  for the phantom-drop assertion or the subsequent apply enables nothing.
- **CSRF on POST**: live writes need the `azc` cookie echoed in the `x-csrf` header (that's how the
  console's own `api()` does it); a bare `-c/-b` curl jar passes reads but every write 403s.
- **Suite: 666 E2E + 219 parity + 197 conformance, 0 failures.** Live verified: catalog 32,
  presets 5, buy_box tuning round-trips, coercion refuses "heavy" for a number param, a custom
  archetype is authored/applied/deleted from the console, and 0 vendor-named definitions remain.

### 2026-09-29 (session 5) — the catalog became authorable: any platform is now data, not code
The owner's directive: the Global Console must configure **any** tenant, and define **any**
platform type — marketplace, payments, mobility, streaming, ERP, CRM, "and many more" — each
instantiable as a tenant with its own admin console. Verified the any-tenant half already worked
(a platform session enabled/tuned/restored `buy_box` on aurum, tenant 2, from the console). The
real blocker was the second half: **the catalog was capped at the 32 things `CATALOG` in
`capabilities.js` hardcodes.** An operator could toggle and tune, but could NOT define a new
capability — so "surge pricing for a mobility platform" was impossible without a code release,
and "and many more" was a promise, not a feature. Closed:

- **Capability authoring** (`define()` in capabilities.js): a new capability + its own TYPED
  params (number | bool | text | json) is authored from the console and is immediately readable
  by every engine through the same `cap()`/`params()` call — no code path knows it exists. A
  bogus param type, a missing key/label, is refused. Authored rows are stamped
  `seeded_from='operator'` + `edited=1` (the operator owns them permanently). `undefine()`
  deletes one, but refuses a seeded capability ("the code that reads it still exists — disable it
  platform-wide instead") and refuses an authored one while any store has it ON, clearing
  orphaned disabled rows on the way out. **The delete guard keys on `enabled=1`, not row
  presence** — `disable` leaves the row (enabled=0), so a presence check would block deletion
  forever after a single toggle.
- **Catalog floor in `params()`**: for a seeded capability the in-code `CATALOG` params are a
  floor — an operator may add or retune a param but can never accidentally delete one an engine
  reads (else `cap()` answers `undefined` and the engine misbehaves *silently*). An authored
  capability owns its params outright; there is no code catalog to fall back to, by design.
- **API + console**: `POST /api/capabilities/catalog` and `DELETE .../catalog/:key` (platform-
  only). The console gained a capability builder (key/label/domain/icon/description + a dynamic
  typed-param editor that coerces the default client-side) and a per-row ✕ for authored rows.
  Domain headings are now derived from the data, so a new domain (`mobility`, `streaming`, `erp`)
  groups under its own heading instead of falling into a fixed map.
- **Live proof**: authored `surge_pricing` (domain `mobility`, number 1.5 + bool), composed a
  `blend_mobility` archetype, applied it to aurum, tuned surge to 2.3, then exercised all three
  delete guards. Every vendor name the owner listed as an example stays OUT of the code — the
  platform models the *kind* (a mobility platform), never the brand.
- **Suite: 666 E2E + 231 parity + 197 conformance, 0 failures** (12 new authoring assertions).
- **Test gotcha**: `cap()` answers `{}` while a capability is OFF — assert DEFAULTS through
  `params()`, and reserve `cap()` for the on-state. My first assertion used `cap()` for a
  default and read it as an engine bug.
