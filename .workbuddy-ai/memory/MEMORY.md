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

### Tooling gotcha
macOS ships BSD grep, which does **not** support `\|` alternation in basic regex — `grep "a\|b"` silently
returns nothing. Use `grep -E` or the Grep tool instead.
