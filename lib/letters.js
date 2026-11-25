/* LUXORA Platform — what is written to a shopper, in the shopper's language.

   A letter is lines in each language (lib/seed/letters.json): the first is its subject, and a line
   whose value is empty is left out. The language is the one the shopper last used here — kept on
   their account, and on an order for a guest — else the store's, else the source. */
"use strict";

const db = () => require("./db.js");
const E = () => require("./expression.js");
const SEED = require("./seed/letters.json");
const fill = (line, v) => { let out = true; const s = line.replace(/\{(\w+)\}/g, (_, k) => { const x = v[k]; if (x == null || x === "") { out = false; return ""; } return String(x); }); return out ? s : null; };
/* a state's or a word's name, as the message catalogue has it in the language */
function word(lang, text) { if (!lang || lang === SEED.source) return text; const r = db().get("SELECT text FROM messages WHERE lang=? AND key=?", E().base(lang), "text:" + text); return r ? r.text : text; }
function write(kind, lang, values) {
  const by = SEED.letters[kind]; if (!by) throw new Error("No letter: " + kind);
  const lines = by[E().base(lang)] || by[SEED.source], v = { ...values };
  if (v.state) v.state = word(lang, v.state);
  const body = lines.slice(1).map(l => (l === "" ? "" : fill(l, v))).filter(l => l != null).join("\n").replace(/\n{3,}/g, "\n\n").trim();
  return { subject: (fill(lines[0], v) || "").trim(), text: body };
}
const known = l => { const b = E().base(l || ""); return b && E().speaks(b) ? b : ""; };
function storeLang(tid) { try { return known(require("./settings.js").load(tid).commerce.locale); } catch (e) { return ""; } }
/* the language of an account, or of an order */
function langOf(tid, o) {
  const w = o || {}, m = /:u:(\d+)$/.exec(String(w.owner || "")), id = w.userId || (m && Number(m[1]));
  const u = id ? db().get("SELECT lang FROM users WHERE id=?", Number(id)) : null;
  return known(u && u.lang) || known(w.order && w.order.lang) || storeLang(tid) || SEED.source;
}
/* the language of a request, kept for what is written later */
function heard(req, url, tid) { try { return E().pick(req, url, require("./settings.js").load(tid).commerce.locale).lang; } catch (e) { return SEED.source; } }
module.exports = { write, word, langOf, heard, SEED };
