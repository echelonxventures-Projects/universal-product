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

### Tooling gotcha
macOS ships BSD grep, which does **not** support `\|` alternation in basic regex — `grep "a\|b"` silently
returns nothing. Use `grep -E` or the Grep tool instead.
