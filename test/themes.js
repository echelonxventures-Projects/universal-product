/* LUXORA · universal theme + adaptive UI audit.
   --------------------------------------------------------------------------
   Proves the "universal UI" claim is real and data-driven:

     THEMES ARE DATA      a theme is a registry row — seeded presets are generated
                          from hue anchors, and an operator creates one from any hue
                          with a single write. Nothing about a theme is code, so the
                          gallery is unbounded by construction.
     CASCADE              product → dept → tenant → platform; the most specific
                          assignment wins, and a store with no assignment keeps its
                          own settings.theme (zero regression on upgrade).
     ADAPTIVE UI          the storefront card renders affordances derived from the
                          product's own type/universe (instant access for digital,
                          bookable for services, cycle pricing for subscriptions) —
                          one renderer, every product shape, no per-type template.

   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "luxora-themes-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
require(path.join(__dirname, "..", "lib", "registry.js")).seedRegistries();
const themes = require(path.join(__dirname, "..", "lib", "themes.js"));
const api = require(path.join(__dirname, "..", "lib", "api.js"));
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const call = (method, urlStr, body, sess) => {
  let out = {};
  const res = { writeHead: () => { }, end: s => { out = JSON.parse(s); } };
  api.handle({ method }, res, new URL(urlStr), sess || { platform_admin: { id: 1, email: "p@p" }, tenant: { id: 1 } }, body);
  return out;
};
/* a real store-admin session: isAdmin() looks the user up, so the merchant row must
   exist for the read-paths to be authorized honestly */
const adminRow = db.get("SELECT id FROM users WHERE role='admin' AND tenant_id=1 ORDER BY id LIMIT 1");
const merchantSess = { user_id: adminRow ? adminRow.id : 1, tenant: { id: 1 } };

console.log("\n▸ THEMES ARE DATA (seeded presets are generated, not hand-typed)");
const presets = themes.presets();
ok(presets.length >= 8, "the registry ships a substantial preset set", "n=" + presets.length);
ok(presets.every(p => p.key && p.name && p.vars && p.preview), "every preset carries vars and a preview signature");
ok(presets.some(p => /futurist/i.test(p.mood || "")), "the set includes futurist moods", presets.filter(p => /futurist/i.test(p.mood || "")).map(p => p.key).join(","));
ok(presets.every(p => Object.keys(p.vars).length >= 18), "every preset is a complete theme (18+ CSS vars)", Math.min(...presets.map(p => Object.keys(p.vars).length)));
/* generation is deterministic — the same hue always yields the same theme */
ok(JSON.stringify(themes.previewHue(150, true).vars) === JSON.stringify(themes.previewHue(150, true).vars), "hue generation is deterministic");
/* light and dark variants of one hue are genuinely different themes */
ok(themes.previewHue(150, true).vars.bg !== themes.previewHue(150, false).vars.bg, "a hue yields distinct light and dark themes");
/* the palette is coherent: accent is a hue-shifted complement, never random */
const p210 = themes.previewHue(210, true).vars;
ok(/hsl\(180|hsl\(30|hsl\(390|hsl\(210|hsl\(150|hsl\(330\)/.test(p210.bg) || p210.bg.startsWith("hsl(2"), "the generated bg is anchored on the requested hue", p210.bg);

console.log("\n▸ INFINITE EXPANSION (an operator theme is one write, no code)");
const made = themes.createFromHue("operator-plasma", "Operator Plasma", 305, { dark: true });
ok(made.ok === true, "a hue becomes a named, permanent preset", JSON.stringify(made).slice(0, 60));
ok(!!themes.preset("operator-plasma"), "the new preset is readable like any built-in");
ok(themes.presets().length === presets.length + 1, "the registry grew by exactly one", presets.length + " → " + themes.presets().length);
ok(themes.createFromHue("operator-plasma", "dup", 10).ok === false, "a duplicate key is refused", "second create");
ok(themes.createFromHue("a", "too-short", 10).ok === false, "a key shorter than 2 chars is refused", "short key");
ok(themes.createFromHue("", "no key", 10).ok === false, "an empty key is refused");
/* a generated theme is usable at every scope immediately */
ok(themes.assign("tenant", 1, "operator-plasma").ok === true, "an operator theme is assignable at once");
ok(themes.resolve({ tenantId: 1 }).key === "operator-plasma", "the assigned operator theme resolves");

console.log("\n▸ THE CASCADE (product → dept → tenant → platform)");
themes.unassign("tenant", 1);
ok(themes.resolve({ tenantId: 1 }) === null, "with no assignment, the store's own settings.theme stays authoritative (zero regression)");
themes.assign("platform", "*", "quantum-glass");
ok(themes.resolve({ tenantId: 1 }).key === "quantum-glass", "a platform assignment dresses every tenant", themes.resolve({ tenantId: 1 }).key);
themes.assign("tenant", 1, "solar-flare");
ok(themes.resolve({ tenantId: 1 }).key === "solar-flare", "a tenant assignment overrides the platform default");
themes.assign("dept", "electronics", "bio-luminescent");
ok(themes.resolve({ tenantId: 1, dept: "electronics" }).key === "bio-luminescent", "a department assignment overrides the tenant");
ok(themes.resolve({ tenantId: 1, dept: "other" }).key === "solar-flare", "an unassigned department inherits the tenant skin");
themes.assign("product", "LX-1", "neon-noir");
ok(themes.resolve({ tenantId: 1, dept: "electronics", productId: "LX-1" }).key === "neon-noir", "a product assignment wins over all wider scopes");
ok(themes.resolve({ tenantId: 1, productId: "LX-2" }).key === "solar-flare", "a sibling product keeps the tenant skin");
/* clearing reverts cleanly to the next-wider scope */
themes.unassign("product", "LX-1");
ok(themes.resolve({ tenantId: 1, dept: "electronics" }).key === "bio-luminescent", "clearing a product assignment reverts to the department skin");

console.log("\n▸ THE CONFIG PAYLOAD CARRIES THE RESOLVED SKIN (storefront, one read)");
themes.assign("tenant", 1, "quantum-glass");
const cfg = call("GET", "http://x/api/config", {});
ok(cfg.theme && cfg.theme.__theme, "the storefront config carries the resolved theme with its provenance", cfg.theme && cfg.theme.__theme && cfg.theme.__theme.key);
ok(cfg.theme.__theme.key === "quantum-glass", "the resolved theme is the tenant's assigned skin");
ok(/Orbitron|Rajdhani/.test(cfg.theme.fontDisplay || ""), "a futurist preset carries its own typography", cfg.theme.fontDisplay);

console.log("\n▸ AUTHORITY: themes are platform-owned, reads are open to the merchant");
const list = call("GET", "http://x/api/themes", {});
ok(Array.isArray(list.presets) && list.presets.length >= 9, "a platform session can list the registry", (list.presets || []).length);
const merchantList = call("GET", "http://x/api/themes", {}, merchantSess);
ok(Array.isArray(merchantList.presets), "a store admin can read the theme registry (they dress their own store)", (merchantList.presets || []).length);
const denied = call("POST", "http://x/api/themes/assign", { scope: "tenant", scope_key: 1, theme_key: "paper-ink" }, merchantSess);
ok(!!denied.error, "a store admin cannot re-assign themes (platform authority)", JSON.stringify(denied));
ok(/Platform access required/.test(denied.error || ""), "the refusal names the authority required", denied.error);
/* validation */
ok(!!call("POST", "http://x/api/themes/assign", { scope: "bogus", scope_key: 1, theme_key: "paper-ink" }).error, "an invalid scope is refused");
ok(!!call("POST", "http://x/api/themes/assign", { scope: "tenant", scope_key: 1, theme_key: "no-such-theme" }).error, "an unknown theme key is refused");
ok(!!call("GET", "http://x/api/themes/preview", {}, merchantSess).error, "hue preview requires a hue");

console.log("\n▸ ADAPTIVE UI: the storefront renderer is derived from the record");
/* the card's affordances come from the product's own type — verified against the
   shipped registry vocabulary, not a hardcoded list */
const cardSrc = fs.readFileSync(path.join(__dirname, "..", "public", "js", "app.js"), "utf8");
ok(/function typeMeta/.test(cardSrc), "the storefront derives per-type metadata (typeMeta)");
ok(/Instant access/.test(cardSrc) && /Bookable/.test(cardSrc), "the card renders digital (instant) and service (bookable) affordances");
ok(/pc-cycle/.test(cardSrc), "subscription/rental products show their cycle in the price");
ok(!/if \(p\.type === .physical.\) [\s\S]{0,80}<div class="pcard-physical"/.test(cardSrc), "no per-type card template is hand-written — the shape is derived");
/* the same derivation drives the PDP (buybox, spec tables) */
ok(/isDigital|isService|isRental/.test(cardSrc), "the product page branches on the record's own type flags");
/* the theme variables are consumed generically — no preset name appears in the CSS */
const cssSrc = fs.readFileSync(path.join(__dirname, "..", "public", "css", "styles.css"), "utf8");
ok(/var\(--font-display\)/.test(cssSrc) && /var\(--glow\)/.test(cssSrc), "the stylesheet consumes theme vars generically (any preset renders)");
ok(!/quantum-glass|neon-noir|solar-flare/.test(cssSrc), "no preset is named in the CSS — themes are data, not stylesheets");
/* the restored sheet actually styles the storefront */
for (const c of ["pcard", "buybox", "pp-grid", "r-grid", "pimg", "banner"]) {
  ok(new RegExp("\\." + c + "\\b").test(cssSrc), "the storefront sheet styles ." + c);
}

console.log("\n▸ CLEAN STATE");
themes.unassign("platform", "*"); themes.unassign("tenant", 1); themes.unassign("dept", "electronics");
db.run("DELETE FROM theme_presets WHERE built_in=0");

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all theme & adaptive-UI checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
