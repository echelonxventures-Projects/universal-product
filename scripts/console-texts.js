/* LUXORA Platform — the consoles' wording, kept in step with the code (owner Expression).

   Finds every phrase the console code shows (text between tags, placeholders, titles, labels, a
   toast's message) and every menu label, group and section (lib/seed/consoles.json), and lists
   each in lib/seed/console-texts.json beside its translations. The database is seeded from that
   file (lib/expression.js): each phrase is a message in the source language — what the console
   shows, editable in Data Studio — and in every language that has a translation.

     node scripts/console-texts.js           what is new and what is untranslated
     node scripts/console-texts.js --write   adds new phrases (translations kept) */
"use strict";
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, ".."), JS = path.join(ROOT, "public", "js"), OUT = path.join(ROOT, "lib", "seed", "console-texts.json");
const FILES = () => ["admin.js", "platform.js", "provisioning.js", "console.js", "editors.js", "rules-ui.js"].concat(fs.readdirSync(path.join(JS, "admin")).filter(f => f.endsWith(".js")).map(f => "admin/" + f))
  .filter(f => fs.existsSync(path.join(JS, f)));
/* a code key (camelCase, snake_case, dotted) is not wording */
const CODE = /^([a-z]+([A-Z][a-z0-9]*)+|[a-z0-9]+(_[a-z0-9]+)+|[a-z]+\.[a-z_.]+|[A-Z_]{3,})$/;
const wording = p => p.length >= 2 && /\p{L}{2}/u.test(p) && /[a-z]{2}/.test(p) && !/[{}=;<>]|=>|\bconst\b|\(\)/.test(p) && !CODE.test(p);
const strip = s => String(s || "").replace(/^[^\p{L}]+/u, "").trim();
function phrases(src) {
  const out = new Set();
  for (const m of src.matchAll(/>([^<>`\\]{2,200}?)</g))
    for (const part of m[1].split(/\$\{[^}]*\}/)) { const p = part.trim(); if (p && wording(strip(p))) out.add(strip(p)); }
  for (const m of src.matchAll(/(?:placeholder|title|aria-label)="([^"$<>{}]{2,160})"/g)) if (wording(m[1].trim())) out.add(m[1].trim());
  for (const m of src.matchAll(/\btoast\("([^"\\$]{3,200})"/g)) if (wording(m[1].trim())) out.add(m[1].trim());
  return out;
}
function found() {
  const C = require(path.join(ROOT, "lib", "consoles.js")), out = new Set();
  for (const f of FILES()) for (const p of phrases(fs.readFileSync(path.join(JS, f), "utf8"))) out.add(p);
  for (const w of ["platform", "store"]) for (const r of C.declared(w)) for (const x of [r.label, r.grp, r.section]) if (x && strip(x)) out.add(strip(x));
  return out;
}
const read = () => JSON.parse(fs.readFileSync(OUT, "utf8"));
/* the phrases the storefront's own catalogue already holds are its (lib/seed/texts.json) */
const shop = () => new Set(Object.keys(require(path.join(ROOT, "lib", "seed", "texts.json")).texts));
function write(seed) {
  const keys = Object.keys(seed.texts).sort((a, b) => a.localeCompare(b));
  fs.writeFileSync(OUT, '{"$comment":' + JSON.stringify(seed.$comment) + ',\n"langs":' + JSON.stringify(seed.langs) + ',\n"texts":{\n' + keys.map(k => JSON.stringify(k) + ":" + JSON.stringify(seed.texts[k])).join(",\n") + "\n}}\n");
}
if (require.main === module) {
  const seed = read(), have = new Set(Object.keys(seed.texts)), sh = shop(), all = [...found()].filter(p => !sh.has(p));
  const fresh = all.filter(p => !have.has(p)), gone = [...have].filter(p => !all.includes(p) && !sh.has(p));
  const untranslated = Object.values(seed.texts).filter(v => !v.length).length;
  console.log(`${all.length} phrases · ${fresh.length} new · ${gone.length} no longer in the code · ${untranslated} not yet translated`);
  if (process.argv.includes("--write")) { for (const p of fresh) seed.texts[p] = []; write(seed); console.log("written"); }
}
module.exports = { found, phrases, read, OUT };
