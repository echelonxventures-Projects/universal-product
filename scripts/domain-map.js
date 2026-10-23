/* The business domain map (_registry/business-domains.json): every artifact the platform is built
   from belongs to exactly one business domain. This reads the artifacts from the code itself —
   engine files, tables (schema.sql), API routes (lib/api.js's route table), state machines, capabilities,
   registry lists, store console screens, platform console screens and pages — and says, for each kind
   of artifact, which domain owns each one, which no domain owns, which two domains claim, and which
   claims name nothing that exists.
   Usage: node scripts/domain-map.js [--json]   (exports map() for the gate and the docs generator) */
"use strict";
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, "..");
const read = f => fs.readFileSync(path.join(ROOT, f), "utf8");
const J = f => JSON.parse(read(f));

/* ---------- the artifacts, read from the code ---------- */
/* the screens a domain's own console file registers (public/js/admin/<domain>.js: screen("key", …)) */
function domainScreens() {
  const dir = path.join(ROOT, "public/js/admin");
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter(f => f.endsWith(".js")).flatMap(f => [...read("public/js/admin/" + f).matchAll(/^screen\("([a-z_]+)"/gm)].map(m => ({ key: m[1], domain: f.replace(/\.js$/, ""), file: "public/js/admin/" + f })));
}
/* the route sources: the shared route file and each domain's own (lib/routes/<domain>.js) */
const routeFiles = () => ["lib/api.js", ...(fs.existsSync(path.join(ROOT, "lib/routes")) ? fs.readdirSync(path.join(ROOT, "lib/routes")).filter(f => f.endsWith(".js")).sort().map(f => "lib/routes/" + f) : [])];
function routesIn(file) { return [...read(file).matchAll(/\["(GET|POST|PUT|PATCH|DELETE) (\/api\/[^"]+)"/g)].map(m => m[1] + " " + m[2]); }
function artifacts() {
  const routes = routeFiles().flatMap(routesIn);
  const admin = read("public/js/admin.js").split("const NAVFLAT")[0];
  const platform = read("public/js/platform.js");
  const navStart = platform.indexOf("const NAV = ["), navEnd = platform.indexOf("\n];", navStart);
  const platformScreens = [];
  let group = null;
  for (const line of platform.slice(navStart, navEnd).split("\n")) {
    const g = /\{ g: "([^"]+)"/.exec(line); if (g) group = g[1];
    const l = /^\s+\["([a-z0-9_-]+)", "/.exec(line); if (l) platformScreens.push({ key: l[1], group });
  }
  return {
    files: fs.readdirSync(path.join(ROOT, "lib")).filter(f => f.endsWith(".js")).map(f => "lib/" + f).concat(routeFiles().slice(1)),
    tables: [...read("schema.sql").matchAll(/^CREATE TABLE (?:IF NOT EXISTS )?"?(\w+)/gm)].map(m => m[1]),
    routes,
    machines: J("lib/seed/states.json").stateMachines.map(m => m.key),
    capabilities: J("lib/seed/capabilities.json").CATALOG.map(c => c.key),
    registries: Object.keys(J("lib/seed/parity-registries.json").REG),
    screens: [...admin.matchAll(/\["([a-z_]+)", "/g)].map(m => m[1]).concat(domainScreens().map(x => x.key)),
    platformScreens,
    pages: fs.readdirSync(path.join(ROOT, "public")).filter(f => f.endsWith(".html")).map(f => f.replace(/\.html$/, ""))
  };
}

/* ---------- who owns each ---------- */
function map() {
  const cat = J("_registry/business-domains.json");
  const a = artifacts();
  const out = { kinds: {}, domains: cat.domains.map(d => d.key), mixedGroups: [] };
  const claim = (kind, list, claimsOf) => {
    const owners = new Map(list.map(x => [x, []]));
    const stale = [];
    for (const d of cat.domains) for (const c of claimsOf(d)) {
      const hits = typeof c === "function" ? list.filter(c) : (owners.has(c) ? [c] : []);
      if (!hits.length) stale.push({ domain: d.key, claim: String(c.src || c) });
      for (const h of hits) owners.get(h).push(d.key);
    }
    const owned = {}, unowned = [], double = [];
    for (const [x, ds] of owners) { const u = [...new Set(ds)]; if (!u.length) unowned.push(x); else if (u.length > 1) double.push({ artifact: x, domains: u }); else owned[x] = u[0]; }
    out.kinds[kind] = { total: list.length, owned, unowned, double, stale };
  };
  const re = s => { const r = new RegExp(s); const f = x => r.test(x.replace(/^[A-Z]+ /, "")); f.src = s; return f; };
  /* a domain's own route file is its by convention */
  claim("files", a.files, d => d.owns.files.concat(a.files.includes("lib/routes/" + d.key + ".js") ? ["lib/routes/" + d.key + ".js"] : []));
  claim("tables", a.tables, d => d.owns.tables);
  claim("routes", a.routes, d => d.owns.routes.map(re));
  claim("machines", a.machines, d => d.owns.machines);
  claim("capabilities", a.capabilities, d => d.owns.capabilities);
  claim("registries", a.registries, d => d.owns.registries);
  /* a screen registered in a domain's own console file is that domain's by convention */
  claim("screens", a.screens, d => d.owns.screens.concat(domainScreens().filter(x => x.domain === d.key).map(x => x.key)));
  claim("pages", a.pages, d => d.owns.pages);
  /* platform screens: claimed by key, else by their console group (a key claim wins over a group) */
  const keys = a.platformScreens.map(s => s.key);
  const byKey = new Map(), byGroup = new Map();
  for (const d of cat.domains) { for (const k of d.owns.platformScreens) byKey.set(k, (byKey.get(k) || []).concat(d.key)); for (const g of d.owns.platformGroups || []) byGroup.set(g, (byGroup.get(g) || []).concat(d.key)); }
  const owned = {}, unowned = [], double = [], stale = [];
  for (const d of cat.domains) for (const k of d.owns.platformScreens) if (!keys.includes(k)) stale.push({ domain: d.key, claim: k });
  for (const s of a.platformScreens) {
    const ds = [...new Set(byKey.get(s.key) || byGroup.get(s.group) || [])];
    if (!ds.length) unowned.push(s.key + " (" + s.group + ")"); else if (ds.length > 1) double.push({ artifact: s.key, domains: ds }); else owned[s.key] = ds[0];
  }
  out.kinds.platformScreens = { total: a.platformScreens.length, owned, unowned, double, stale };
  /* a console group whose screens belong to more than one domain mixes domains */
  const groups = {};
  for (const s of a.platformScreens) if (owned[s.key]) (groups[s.group] = groups[s.group] || new Set()).add(owned[s.key]);
  out.mixedGroups = Object.entries(groups).filter(([, ds]) => ds.size > 1).map(([g, ds]) => ({ group: g, domains: [...ds] }));
  return out;
}

if (require.main === module) {
  const m = map();
  if (process.argv.includes("--json")) { console.log(JSON.stringify(m, null, 1)); return; }
  for (const [k, v] of Object.entries(m.kinds))
    console.log(`${k.padEnd(15)} ${String(Object.keys(v.owned).length).padStart(4)} of ${String(v.total).padEnd(4)} owned · ${v.unowned.length} unowned · ${v.double.length} owned twice · ${v.stale.length} stale claims`);
  console.log(`console groups mixing domains: ${m.mixedGroups.length}`);
}
/* two routes one request could match: they must sit in one domain's file, the literal one first */
function overlaps() {
  const seg = p => p.split("/").filter(Boolean);
  const rs = routeFiles().flatMap(f => routesIn(f).map((r, i) => ({ r, f, i })));
  const out = [];
  for (let i = 0; i < rs.length; i++) for (let j = i + 1; j < rs.length; j++) {
    const [ma, pa] = rs[i].r.split(" "), [mb, pb] = rs[j].r.split(" ");
    if (ma !== mb) continue;
    const x = seg(pa), y = seg(pb);
    if (x.length !== y.length || !x.every((v, k) => v === y[k] || v.startsWith(":") || y[k].startsWith(":"))) continue;
    const litFirst = x.filter(v => v.startsWith(":")).length <= y.filter(v => v.startsWith(":")).length;
    out.push({ a: rs[i].r, b: rs[j].r, sameFile: rs[i].f === rs[j].f, ordered: litFirst });
  }
  return out;
}
module.exports = { map, artifacts, overlaps, routeFiles, domainScreens };
