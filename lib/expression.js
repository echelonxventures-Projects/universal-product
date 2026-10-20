/* LUXORA Platform — Expression (P12, owner Expression).

   Languages are a registry: each names its script and writing direction, so a right-to-left
   language lays out right to left with no code (lib/seed/expression.json). The storefront's
   shipped copy is written in the source language; the message catalogue (the messages table,
   editable in the console as the `message` entity) holds the same keys in other languages.

   A request is answered in the shopper's chosen language, else the best one their browser asks
   for, else the language of the store's locale, else the source language — always one the
   platform can speak: the source, or one with a catalogue. A store's own saved copy overrides the
   catalogue in the store's language only. */
"use strict";

const SEED = require("./seed/expression.json");
const all = (...a) => require("./db.js").all(...a);
const get = (...a) => require("./db.js").get(...a);
const run = (...a) => require("./db.js").run(...a);
const J = (v, d) => { try { return v == null || v === "" ? d : JSON.parse(v); } catch (e) { return d; } };

/* every catalogue row the seed ships, where the row is missing (an operator's edit is kept) */
function seed() {
  let n = 0;
  for (const [lang, msgs] of Object.entries(SEED.catalogues))
    for (const [key, text] of Object.entries(msgs)) n += run("INSERT OR IGNORE INTO messages(lang,key,text) VALUES(?,?,?)", lang, key, text).changes;
  return n;
}
const base = tag => String(tag || "").trim().toLowerCase().split(/[-_]/)[0];
function languages() {
  let l = null; try { l = require("./registry.js").list(SEED.languageList); } catch (e) { l = null; }
  return Array.isArray(l) && l.length ? l : SEED.languages;
}
const language = key => languages().find(x => x && x.key === base(key)) || null;
/* the languages the platform can answer in: the source and every language with a catalogue */
function available() {
  const have = new Set(all("SELECT DISTINCT lang FROM messages").map(r => r.lang));
  have.add(SEED.sourceLanguage);
  return languages().filter(x => x && have.has(x.key));
}
const speaks = key => available().some(x => x.key === base(key));
function catalogue(lang) {
  return Object.fromEntries(all("SELECT key, text FROM messages WHERE lang=?", base(lang)).map(r => [r.key, r.text]));
}
/* the browser's languages, best first (RFC 9110 q-values) */
function accepted(header) {
  return String(header || "").split(",").map((p, i) => {
    const [tag, ...params] = p.trim().split(";");
    const q = params.map(x => x.trim()).find(x => x.startsWith("q="));
    return { tag: tag.trim(), q: q ? Number(q.slice(2)) : 1, i };
  }).filter(x => x.tag && x.tag !== "*" && x.q > 0).sort((a, b) => b.q - a.q || a.i - b.i).map(x => x.tag);
}
function cookieOf(req, name) {
  const m = String((req && req.headers && req.headers.cookie) || "").split(";").map(x => x.trim()).find(x => x.startsWith(name + "="));
  try { return m ? decodeURIComponent(m.slice(name.length + 1)) : null; } catch (e) { return null; }
}
/* the language to answer a request in, and why */
function pick(req, url, storeLocale) {
  const asked = url && url.searchParams ? url.searchParams.get(SEED.query) : null;
  if (asked && speaks(asked)) return { lang: base(asked), from: "query" };
  const chosen = cookieOf(req, SEED.cookie);
  if (chosen && speaks(chosen)) return { lang: base(chosen), from: "choice" };
  for (const tag of accepted(req && req.headers && req.headers["accept-language"])) if (speaks(tag)) return { lang: base(tag), from: "browser" };
  if (storeLocale && speaks(storeLocale)) return { lang: base(storeLocale), from: "store" };
  return { lang: SEED.sourceLanguage, from: "source" };
}
/* the storefront's copy in a language: the shipped copy, the catalogue over it, and the store's
   own saved copy over both in the store's language */
function copyFor(lang, shipped, saved, storeLang) {
  const l = base(lang);
  return { ...(shipped || {}), ...(l === base(SEED.sourceLanguage) ? {} : catalogue(l)), ...(l === base(storeLang) ? (saved || {}) : {}) };
}
const direction = lang => (language(lang) || {}).direction || (language(SEED.sourceLanguage) || {}).direction;
/* a store's own saved copy (not the shipped defaults it is merged with) */
const savedCopy = tid => J((get("SELECT value FROM settings WHERE tenant_id=? AND key='copy'", Number(tid)) || {}).value, {});

module.exports = { SEED, seed, languages, language, available, speaks, catalogue, accepted, pick, copyFor, direction, savedCopy, base };
