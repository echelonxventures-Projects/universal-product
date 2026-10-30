/* LUXORA · universal theme engine — every skin the storefront can wear.
   --------------------------------------------------------------------------
   Themes are DATA. A theme is a set of CSS custom properties stored in
   `theme_presets`; an operator creates one with a single INSERT and it is live —
   no code, no deploy, no limit. That is the "infinitely expandable" part, and it
   is the only honest way to do it: a hardcoded theme gallery is finite by
   construction, a registry is not.

   PRESETS are generated, not hand-picked. Every palette below is derived from a
   hue anchor by the same colour arithmetic (hue → a full ramp of surface/accent/
   deep/soft), so the set is generative rather than a list someone typed in. New
   moods are added by declaring a hue and a name.

   ASSIGNMENTS cascade: platform → tenant → department → product. The most specific
   assignment wins, so a store can wear "Quantum Glass" while one department wears
   "Solar Flare" and a single flagship product wears its own skin. Resolution is a
   pure function of the registry — nothing is cached in code. */
"use strict";
/* seed data (lib/seed/themes.json): data, not code — the registries are seeded from it */
const SEED_THEMES = require("./seed/themes.json");

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const rows = (sql, ...p) => { try { return db().all(sql, ...p) || []; } catch (e) { return []; } };
const get = (sql, ...p) => { try { return db().get(sql, ...p) || null; } catch (e) { return null; } };

/* ---------- the generative palette: one hue → a complete, coherent theme ----------
   Colour math, not taste: a ramp from light to dark on the hue, a complementary
   accent, and the semantic colours every commerce UI needs. Any hue produces a
   usable theme, which is what makes the registry unbounded. */
function ramp(hue, opts) {
  const o = opts || {};
  const dark = o.dark !== false;
  const h = ((Number(hue) % 360) + 360) % 360;
  const ac = o.accentHue != null ? ((Number(o.accentHue) % 360) + 360) % 360 : (h + 180 - 30) % 360;
  if (dark) {
    return {
      bg: `hsl(${h} 30% 7%)`, surface: `hsl(${h} 26% 11%)`, ink: `hsl(${h} 20% 94%)`, muted: `hsl(${h} 14% 62%)`,
      line: `hsl(${h} 22% 20%)`, header: `hsl(${h} 34% 5%)`, headerText: `hsl(${h} 20% 96%)`, headerMuted: `hsl(${h} 14% 68%)`,
      accent: `hsl(${ac} 85% 62%)`, accentDeep: `hsl(${ac} 70% 42%)`, accentSoft: `hsl(${ac} 40% 18%)`,
      price: `hsl(${ac} 90% 70%)`, deal: `hsl(${(ac + 40) % 360} 90% 62%)`, success: `hsl(150 70% 55%)`, star: `hsl(${(ac + 60) % 360} 85% 62%)`,
      link: `hsl(${ac} 80% 68%)`, linkHover: `hsl(${ac} 90% 78%)`
    };
  }
  return {
    bg: `hsl(${h} 30% 96%)`, surface: `hsl(${h} 40% 99%)`, ink: `hsl(${h} 30% 12%)`, muted: `hsl(${h} 12% 42%)`,
    line: `hsl(${h} 24% 88%)`, header: `hsl(${h} 30% 9%)`, headerText: `hsl(${h} 30% 97%)`, headerMuted: `hsl(${h} 14% 70%)`,
    accent: `hsl(${ac} 65% 42%)`, accentDeep: `hsl(${ac} 60% 32%)`, accentSoft: `hsl(${ac} 55% 90%)`,
    price: `hsl(${h} 30% 14%)`, deal: `hsl(${(ac + 40) % 360} 75% 40%)`, success: `hsl(150 55% 38%)`, star: `hsl(${(ac + 60) % 360} 70% 42%)`,
    link: `hsl(${ac} 55% 32%)`, linkHover: `hsl(${ac} 60% 24%)`
  };
}

/* the moods the platform ships. Each is a hue + light/dark + a typographic posture;
   the palette is GENERATED from the hue, so adding a mood is one line, and the set
   already spans light, dark and futurist postures. */
const PRESET_MOODS = SEED_THEMES.PRESET_MOODS;

/* the full vars for a mood: the generated ramp + shape + typography + an animation
   posture the front-end can opt into (the futurist presets carry a subtle drift) */
function varsFor(m) {
  return { ...ramp(m.hue, { dark: m.dark, accentHue: m.accentHue }),
    radius: m.radius, radiusBtn: m.radiusBtn, fontDisplay: m.fontDisplay, fontBody: m.fontBody,
    customCSS: m.dark ? ":root{--glow:0 0 24px hsl(var(--accent-hsl,210 80% 60%) / 18%)}" : "" };
}

/* ---------- seeding: presets are idempotent and never clobber an operator edit ---------- */
function seed() {
  PRESET_MOODS.forEach((m, i) => {
    const ex = get("SELECT key FROM theme_presets WHERE key=?", m.key);
    const v = JSON.stringify(varsFor(m));
    if (!ex) db().run("INSERT INTO theme_presets(key,name,mood,vars,preview,built_in,position) VALUES(?,?,?,?,?,1,?)",
      m.key, m.name, m.mood, v, m.preview, i);
  });
}

/* ---------- read API ---------- */
function presets() {
  return rows("SELECT key,name,mood,preview,built_in,position FROM theme_presets ORDER BY position, name")
    .map(p => ({ ...p, vars: JSON.parse((get("SELECT vars v FROM theme_presets WHERE key=?", p.key) || {}).v || "{}") }));
}
function preset(key) {
  const r = get("SELECT * FROM theme_presets WHERE key=?", key);
  if (!r) return null;
  return { ...r, vars: JSON.parse(r.vars || "{}") };
}

/* ---------- the cascade: most specific assignment wins ----------
   Resolution order is product → dept → tenant → platform. Each scope is consulted
   once; the first that has an assignment governs. Absent any assignment, the
   tenant's own settings.theme applies (the legacy path, still authoritative), so
   nothing about an existing store changes by upgrading. */
function assignedTheme(scope, scopeKey) {
  const r = get("SELECT theme_key FROM theme_assignments WHERE scope=? AND scope_key=?", scope, String(scopeKey));
  return r ? preset(r.theme_key) : null;
}
function resolve(ctx) {
  const c = ctx || {};
  for (const [scope, key] of [["product", c.productId], ["dept", c.dept], ["tenant", c.tenantId]]) {
    if (key == null || key === "") continue;
    const t = assignedTheme(scope, key);
    if (t) return { ...t, scope, scopeKey: key, via: scope + ":" + key };
  }
  const plat = assignedTheme("platform", "*");
  if (plat) return { ...plat, scope: "platform", scopeKey: "*", via: "platform" };
  return null;            /* the caller's own theme remains the authority */
}

function assign(scope, scopeKey, themeKey) {
  const t = preset(themeKey);
  if (!t) return { ok: false, error: "unknown theme " + themeKey };
  db().run("INSERT INTO theme_assignments(scope,scope_key,theme_key) VALUES(?,?,?) ON CONFLICT(scope,scope_key) DO UPDATE SET theme_key=excluded.theme_key",
    scope, String(scopeKey), themeKey);
  return { ok: true, scope, scopeKey, themeKey };
}
function unassign(scope, scopeKey) {
  db().run("DELETE FROM theme_assignments WHERE scope=? AND scope_key=?", scope, String(scopeKey));
  return { ok: true };
}
function assignments() {
  return rows("SELECT a.scope, a.scope_key, a.theme_key, p.name theme_name, p.preview FROM theme_assignments a LEFT JOIN theme_presets p ON p.key=a.theme_key ORDER BY a.scope, a.scope_key");
}

/* ---------- generative preview: any hue → a theme, on demand ----------
   The console's "explore" lets an operator dial a hue and see a live theme without
   committing, because the palette is a function. This is the "unlimited" primitive:
   the gallery is finite, the space is not. */
function previewHue(hue, dark) {
  const d = dark !== false;
  return { key: "__preview__", name: "Preview · h" + hue, mood: d ? "futurist" : "light",
    vars: varsFor({ hue: Number(hue) || 0, dark: d, radius: "14px", radiusBtn: "10px",
      fontDisplay: '"Inter","Segoe UI",sans-serif', fontBody: '"Inter","Segoe UI",sans-serif' }),
    preview: "linear-gradient(135deg,hsl(" + hue + " 30% 10%),hsl(" + hue + " 80% 50%))" };
}

/* ---------- an operator creates a permanent preset from any hue ----------
   This is the registry's growth path: a theme that began as a dial becomes a named,
   reusable row the whole platform can assign. Nothing about it is code. */
function createFromHue(key, name, hue, opts) {
  const o = opts || {};
  const k = String(key || "").trim().toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "");
  if (!k || k.length < 2) return { ok: false, error: "a theme key (2+ chars) is required" };
  if (get("SELECT 1 ok FROM theme_presets WHERE key=?", k)) return { ok: false, error: "theme " + k + " already exists" };
  const m = { hue: Number(hue) || 0, dark: o.dark !== false, radius: o.radius || "14px", radiusBtn: o.radiusBtn || "10px",
    fontDisplay: o.fontDisplay || '"Inter","Segoe UI",sans-serif', fontBody: o.fontBody || '"Inter","Segoe UI",sans-serif' };
  const p = previewHue(m.hue, m.dark);
  db().run("INSERT INTO theme_presets(key,name,mood,vars,preview,built_in,position) VALUES(?,?,?,?,?,0,999)",
    k, String(name || k).slice(0, 60), o.mood || (m.dark ? "futurist" : "light"), JSON.stringify(p.vars), p.preview);
  return { ok: true, key: k, ...preset(k) };
}

module.exports = { PRESET_MOODS, ramp, varsFor, seed, presets, preset, resolve, assign, unassign, assignments, previewHue, createFromHue };
