/* LUXORA Platform — the API described, for any language (owner Integration, roadmap P19).

   An OpenAPI 3.1 description of every route, generated — never written by hand — from the same
   sources the platform itself uses: the route table (each route's method and path), each handler's
   own comment (its summary), and the API register (the domain that owns it, its tag). So the
   description cannot drift from the code: a test compares it with a fresh generation.

   Who may call a route is said by its path's audience (lib/seed/openapi.json): the platform's routes
   need a platform session; a store's admin routes a staff session or a store API key (the same key an
   MCP client uses, issued in Store console → AI → API & MCP keys); the rest serve shoppers and guests.

   A client in any language generates its library from the description with standard tools
   (docs/api/README.md). Usage: node scripts/openapi.js [--write]  */
"use strict";
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, ".."), OUT = path.join(ROOT, "docs", "api", "openapi.json");
const SEED = require("../lib/seed/openapi.json");

function build() {
  const rf = require("../lib/ucos-registry.js").readRegistryFiles();
  const reg = require("../lib/canonical.js").apiRegister(rf);
  const notes = require("./domain-docs.js").routeTable();
  const pkg = require("../package.json");
  const paths = {}, tags = new Set(), seen = new Set();
  for (const [method, p, handler, owner] of reg.routes) {
    const key = method + " " + p;
    if (seen.has(key)) continue; seen.add(key);
    const oaPath = p.replace(/:([A-Za-z0-9_]+)/g, "{$1}");
    const params = [...p.matchAll(/:([A-Za-z0-9_]+)/g)].map(m => ({ name: m[1], in: "path", required: true, schema: { type: "string" } }));
    const aud = SEED.audiences.find(a => new RegExp(a.pattern).test(p)) || SEED.audiences[SEED.audiences.length - 1];
    const note = (notes[key] && notes[key].note) || "";
    const op = {
      operationId: handler + (seen.size && Object.values(paths).some(x => Object.values(x).some(o => o.operationId === handler)) ? "_" + method.toLowerCase() : ""),
      summary: note ? note.charAt(0).toUpperCase() + note.slice(1).split(/(?<=[.;])\s/)[0].slice(0, 160) : handler,
      ...(note.length > 160 ? { description: note } : {}),
      tags: [owner || SEED.untagged],
      ...(params.length ? { parameters: params } : {}),
      ...(["POST", "PUT", "PATCH"].includes(method) ? { requestBody: { required: false, content: { "application/json": { schema: { type: "object" } } } } } : {}),
      responses: SEED.responses,
      security: aud.security,
      "x-audience": aud.key
    };
    tags.add(op.tags[0]);
    (paths[oaPath] = paths[oaPath] || {})[method.toLowerCase()] = op;
  }
  return {
    openapi: "3.1.0",
    info: { title: SEED.title, version: pkg.version, description: SEED.description },
    servers: SEED.servers,
    tags: [...tags].sort().map(name => ({ name })),
    components: { securitySchemes: SEED.securitySchemes },
    paths: Object.fromEntries(Object.entries(paths).sort(([a], [b]) => a.localeCompare(b)))
  };
}
const text = () => JSON.stringify(build(), null, 1) + "\n";
if (require.main === module) {
  if (process.argv.includes("--write")) { fs.writeFileSync(OUT, text()); console.log("docs/api/openapi.json written — " + Object.keys(build().paths).length + " paths"); }
  else process.stdout.write(text());
}
module.exports = { build, text, OUT };
