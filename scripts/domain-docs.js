/* Each business domain's documentation, generated (_registry/business-domains.json + the code +
   docs/source/<domain>.md), so it cannot drift from what is built:
     docs/domains/<domain>.md   overview · users · switches and settings · architecture · data model ·
                                API reference · process flows (state machines) · data flow ·
                                user interface · user flows · a manual section for each of its users
     docs/domains/README.md     the catalogue: every domain, its foundation and its users
     docs/manuals/<user>.md     one manual per type of user, gathered from every domain they use
   What the code says is read from the code; what only a person can say (how a flow is meant to go,
   how each user does each task) is written once in docs/source/<domain>.md under "## Flows" and
   "## Manual: <user type key>", and completeness() lists what is still unwritten.
   Usage: node scripts/domain-docs.js [--check]   (--check: exit 1 when a generated file is stale) */
"use strict";
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, "..");
const read = f => fs.readFileSync(path.join(ROOT, f), "utf8");
const J = f => JSON.parse(read(f));
const { map } = require("./domain-map.js");

/* ---------- reading the code ---------- */
const headerOf = file => { const m = /^\/\*([\s\S]*?)\*\//.exec(read(file)); return m ? m[1].replace(/^\s*LUXORA Platform\s*[—-]\s*/, "").split(/\n\s*\n/)[0].replace(/\s+/g, " ").trim() : ""; };
function tables() {
  const out = {};
  const sql = read("schema.sql");
  for (const m of sql.matchAll(/^CREATE TABLE (?:IF NOT EXISTS )?"?(\w+)"?\s*\(/gm)) {
    /* the body to the matching close; split on commas outside parentheses and quotes */
    let i = m.index + m[0].length, depth = 1, q = false, cur = "", parts = [];
    for (; i < sql.length && depth; i++) {
      const ch = sql[i];
      if (ch === "'") q = !q;
      if (!q && ch === "(") depth++;
      if (!q && ch === ")") { depth--; if (!depth) break; }
      if (!q && depth === 1 && ch === ",") { parts.push(cur); cur = ""; } else cur += ch;
    }
    parts.push(cur);
    out[m[1]] = parts.map(x => x.replace(/\s+/g, " ").trim()).filter(x => x && !/^(PRIMARY|UNIQUE|FOREIGN|CHECK|CONSTRAINT)\b/i.test(x))
      .map(x => { const [n, ...t] = x.split(" "); return { name: n.replace(/"/g, ""), type: t.join(" ") }; });
  }
  return out;
}
function routeTable() {
  const api = read("lib/api.js");
  const out = {};
  for (const m of api.matchAll(/\["(GET|POST|PUT|PATCH|DELETE) (\/api\/[^"]+)",\s*(?:\(r[^)]*\)\s*=>\s*)?(\w+)/g)) {
    const fn = m[3];
    const at = api.search(new RegExp("\\n(?:async )?function " + fn + "\\("));
    let note = "";
    /* the handler's own comment: the block comment that ends right where the handler starts */
    if (at > 0) { const before = api.slice(Math.max(0, at - 1200), at); const c = /\/\*((?:(?!\*\/)[\s\S])*)\*\/\s*$/.exec(before); if (c) note = c[1].replace(/\s+/g, " ").trim(); }
    out[m[1] + " " + m[2]] = { handler: fn, note };
  }
  return out;
}
const machines = () => Object.fromEntries(J("lib/seed/states.json").stateMachines.map(m => [m.key, m]));
const caps = () => Object.fromEntries(J("lib/seed/capabilities.json").CATALOG.map(c => [c.key, c]));
const adminLabels = () => Object.fromEntries([...read("public/js/admin.js").split("const NAVFLAT")[0].matchAll(/\["([a-z_]+)", "([^"]+)"\]/g)].map(m => [m[1], m[2]]));
const platformLabels = () => Object.fromEntries([...read("public/js/platform.js").matchAll(/^\s+\["([a-z0-9_-]+)", "([^"]+)"/gm)].map(m => [m[1], m[2]]));

/* ---------- what a person writes ---------- */
const SRC = path.join(ROOT, "docs", "source");
function authored(key) {
  const f = path.join(SRC, key + ".md");
  if (!fs.existsSync(f)) return { flows: "", manual: {} };
  const t = fs.readFileSync(f, "utf8");
  const sections = {};
  for (const part of t.split(/^## /m).slice(1)) { const nl = part.indexOf("\n"); sections[part.slice(0, nl).trim()] = part.slice(nl + 1).trim(); }
  const manual = {};
  for (const [h, body] of Object.entries(sections)) { const m = /^Manual:\s*([a-z_]+)$/.exec(h); if (m && body) manual[m[1]] = body; }
  return { flows: sections.Flows || "", manual };
}
/* what each domain still lacks: its flows, and a manual section for each of its users */
function completeness() {
  return J("_registry/business-domains.json").domains.map(d => {
    const a = authored(d.key);
    return { domain: d.key, missing: [...(a.flows ? [] : ["flows"]), ...d.users.filter(u => !a.manual[u]).map(u => "manual:" + u)] };
  });
}

/* ---------- writing ---------- */
const mmState = m => {
  const lines = ["stateDiagram-v2", "  [*] --> " + m.initial];
  const t = typeof m.transitions === "object" && !Array.isArray(m.transitions) ? m.transitions : {};
  for (const [from, tos] of Object.entries(t)) for (const to of tos) lines.push(`  ${from === "*" ? "[*]" : from} --> ${to}`);
  for (const [s, meta] of Object.entries(m.meta || {})) if ((meta.tags || []).includes("terminal")) lines.push(`  ${s} --> [*]`);
  return lines.join("\n");
};
function domainDoc(d, ctx) {
  const userName = Object.fromEntries(ctx.cat.userTypes.map(u => [u.key, u.name]));
  const own = k => Object.entries(ctx.m.kinds[k].owned).filter(([, v]) => v === d.key).map(([x]) => x);
  const a = authored(d.key);
  const o = [];
  o.push(`# ${d.name}`, "", `> Generated from \`_registry/business-domains.json\`, the code and \`docs/source/${d.key}.md\` — edit those, then run \`node scripts/domain-docs.js\`.`, "");
  o.push("## Overview", "", d.purpose, "", `**Foundation domain:** ${d.foundation} · **Used by:** ${d.users.map(u => userName[u] || u).join(", ")}`, "");
  const cs = own("capabilities");
  if (cs.length) {
    o.push("## Switches and settings", "", "Each is switched on per store under ⚙️ Capabilities; its parameters are that store's settings.", "");
    for (const k of cs) { const c = ctx.caps[k] || {}; o.push(`### ${c.label || k} (\`${k}\`)`, "", c.description || "", "");
      const ps = Object.entries(c.params || {}); if (ps.length) { o.push("| Setting | Meaning | Default |", "|---|---|---|"); for (const [pk, p] of ps) o.push(`| \`${pk}\` | ${p.label || ""} | \`${JSON.stringify(p.default)}\` |`); o.push(""); } }
  }
  const fs_ = own("files");
  o.push("## Architecture", "");
  if (fs_.length) { o.push("| Module | What it is |", "|---|---|"); for (const f of fs_) o.push(`| \`${f}\` | ${headerOf(f).replace(/\|/g, "\\|")} |`); o.push(""); }
  const regs = own("registries"); if (regs.length) o.push("**Registry lists** (editable in Data Studio): " + regs.map(r => "`" + r + "`").join(", "), "");
  const ts = own("tables");
  if (ts.length) {
    o.push("## Data model", "");
    for (const t of ts) { const cols = ctx.tables[t] || []; o.push(`### \`${t}\``, "", "| Column | Type |", "|---|---|", ...cols.map(c => `| \`${c.name}\` | ${c.type.replace(/\|/g, "\\|")} |`), ""); }
  }
  const rs = own("routes");
  if (rs.length) {
    o.push("## API reference", "", "Every call is JSON over HTTPS; store calls carry the store (`?store=`) and the session; mutating calls accept an `Idempotency-Key` header where noted.", "");
    o.push("| Method and path | Handler | What it does |", "|---|---|---|");
    for (const r of rs) { const x = ctx.routes[r] || {}; const [mth, p] = r.split(" "); o.push(`| \`${mth} ${p}\` | \`${x.handler || ""}\` | ${(x.note || "—").replace(/\|/g, "\\|")} |`); }
    o.push("");
  }
  const ms = own("machines");
  if (ms.length) {
    o.push("## Process flows", "", "Each record's life is a declared state machine (`lib/seed/states.json`): the moves it may make, and the actions that make them.", "");
    for (const k of ms) { const m = ctx.machines[k]; if (!m) continue; o.push(`### ${m.name || k} (\`${k}\`)`, "", "```mermaid", mmState(m), "```", "", "Actions: " + Object.entries(m.actions || {}).map(([v, t]) => `\`${v}\` → ${t}`).join(" · "), ""); }
  }
  o.push("## Data flow", "", "```mermaid", "flowchart LR",
    `  U([${d.users.map(u => userName[u] || u).join(" / ")}]) --> UI[${[...own("pages").map(p => p + ".html"), own("screens").length ? "store console" : "", own("platformScreens").length ? "platform console" : ""].filter(Boolean).join(", ") || "API"}]`,
    `  UI --> API[${rs.length} API routes]`, `  API --> ENG[${fs_.map(f => path.basename(f)).join(", ") || "engines"}]`,
    `  ENG --> DB[(${ts.length ? ts.slice(0, 6).join(", ") + (ts.length > 6 ? ", …" : "") : "kernel"})]`, ms.length ? "  ENG --> SM{{" + ms.length + " state machines}}" : "", "```", "");
  const sc = own("screens"), ps = own("platformScreens"), pg = own("pages");
  o.push("## User interface", "");
  if (pg.length) o.push("**Pages:** " + pg.map(p => "`" + p + ".html`").join(", "), "");
  if (sc.length) o.push("**Store console:** " + sc.map(s => (ctx.admin[s] || s)).join(" · "), "");
  if (ps.length) o.push("**Platform console:** " + ps.map(s => (ctx.platform[s] || s)).join(" · "), "");
  o.push("## User flows", "", a.flows || "_Not yet written — `docs/source/" + d.key + ".md`, section `## Flows`._", "");
  o.push("## Manuals", "");
  for (const u of d.users) o.push(`### ${userName[u] || u}`, "", a.manual[u] || `_Not yet written — \`docs/source/${d.key}.md\`, section \`## Manual: ${u}\`._`, "");
  return o.filter(x => x !== null).join("\n") + "\n";
}
function generate() {
  const ctx = { cat: J("_registry/business-domains.json"), m: map(), tables: tables(), routes: routeTable(), machines: machines(), caps: caps(), admin: adminLabels(), platform: platformLabels() };
  const files = {};
  const userName = Object.fromEntries(ctx.cat.userTypes.map(u => [u.key, u.name]));
  const comp = Object.fromEntries(completeness().map(c => [c.domain, c.missing]));
  const idx = ["# Business domains", "", ctx.cat.law, "", "| Domain | Foundation | Users | Documentation |", "|---|---|---|---|"];
  for (const d of ctx.cat.domains) {
    files["docs/domains/" + d.key + ".md"] = domainDoc(d, ctx);
    idx.push(`| [${d.name}](${d.key}.md) | ${d.foundation} | ${d.users.map(u => userName[u] || u).join(", ")} | ${comp[d.key].length ? comp[d.key].length + " sections to write" : "complete"} |`);
  }
  files["docs/domains/README.md"] = idx.join("\n") + "\n";
  for (const u of ctx.cat.userTypes) {
    const o = [`# Manual — ${u.name}`, "", `Everything a ${u.name.toLowerCase()} does on the platform, domain by domain. Generated from each domain's documentation.`, ""];
    for (const d of ctx.cat.domains.filter(x => x.users.includes(u.key))) o.push(`## ${d.name}`, "", d.purpose, "", authored(d.key).manual[u.key] || "_Not yet written._", "", `More: [${d.name}](../domains/${d.key}.md)`, "");
    files["docs/manuals/" + u.key + ".md"] = o.join("\n") + "\n";
  }
  return files;
}

if (require.main === module) {
  const files = generate();
  const stale = Object.entries(files).filter(([f, t]) => !fs.existsSync(path.join(ROOT, f)) || fs.readFileSync(path.join(ROOT, f), "utf8") !== t).map(([f]) => f);
  if (process.argv.includes("--check")) { if (stale.length) { console.log("stale documentation:", stale.slice(0, 10).join(", "), stale.length > 10 ? "…" : ""); process.exit(1); } console.log("documentation is current"); return; }
  for (const [f, t] of Object.entries(files)) { fs.mkdirSync(path.dirname(path.join(ROOT, f)), { recursive: true }); fs.writeFileSync(path.join(ROOT, f), t); }
  const c = completeness();
  console.log(`${Object.keys(files).length} files written · ${c.filter(x => !x.missing.length).length} of ${c.length} domains fully written · ${c.reduce((n, x) => n + x.missing.length, 0)} sections to write`);
}
/* routes whose handler says nothing about what it does */
function undescribedRoutes() { return Object.values(routeTable()).filter(r => !r.note).length; }
module.exports = { generate, completeness, authored, undescribedRoutes };
