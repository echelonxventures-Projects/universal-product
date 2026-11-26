/* LUXORA Platform — the consoles' menus, from the database (owner Experience).

   Every screen of the platform console and the store console is a row of console_screens: which
   console, where it sits (section and group), what it is called, its position, what it shows
   (a dedicated view, a dataset, a universe) and the access section it needs, and for a store
   screen the kinds of store it fits. lib/seed/consoles.json is what a new install starts with;
   sync() adds what is missing and brings every row nobody has edited up to the seed, so an
   operator's edit in Data Studio stands. The backend serves each console its menu from these rows
   (lib/bundle.js); the browser holds only each screen's drawing code.

   declared() is the seed as written — what the compiled registry, the domain map and the grant
   surface are built from at compile time, when there is no database. */
"use strict";

const SEED = require("./seed/consoles.json");
const D = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? d : JSON.parse(v); } catch (e) { return d; } };
const STEP = 1000;

/* the rows the seed declares, in order */
function declared(which) {
  if (which === "platform") {
    let i = 0;
    return SEED.platform.sections.flatMap(s => s.groups.flatMap(g => g.screens.map(x => ({ console: "platform", key: x.key, section: s.section, grp: g.group, label: x.label, position: ++i, shows: x.shows || null, access: x.key, fit: null }))));
  }
  const at = new Map(SEED.store.groups.map((g, i) => [g.group, i]));
  return SEED.store.screens.map(x => ({ console: "store", key: x.key, section: null, grp: x.group, label: x.label,
    position: (at.has(x.group) ? at.get(x.group) : SEED.store.groups.findIndex(g => g.tail)) * STEP + (x.order == null ? STEP - 1 : x.order), shows: null, access: x.section || x.key, fit: x.fit || null }));
}
const COLS = ["section", "grp", "label", "position", "shows", "access", "fit"];
const cell = (c, v) => (c === "shows" || c === "fit") ? (v == null ? null : JSON.stringify(v)) : v;

let synced = false;
function ensure() {
  const db = D();
  /* run, not exec: run speaks every database the platform runs on (lib/sql.js) */
  db.run(`CREATE TABLE IF NOT EXISTS console_screens (
    id INTEGER PRIMARY KEY AUTOINCREMENT, console TEXT NOT NULL, key TEXT NOT NULL, section TEXT, grp TEXT NOT NULL,
    label TEXT NOT NULL, position REAL NOT NULL DEFAULT 0, shows TEXT, access TEXT NOT NULL, fit TEXT, edited INTEGER DEFAULT 0,
    UNIQUE(console, key))`);
}
/* adds what the seed has and the table lacks; brings unedited rows up to the seed; removes an
   unedited row the seed no longer declares (its screen is gone) */
function sync() {
  ensure();
  const db = D();
  for (const which of ["platform", "store"]) {
    const want = declared(which), have = new Map(db.all("SELECT * FROM console_screens WHERE console=?", which).map(r => [r.key, r]));
    for (const w of want) {
      const r = have.get(w.key);
      if (!r) db.run(`INSERT INTO console_screens(console,key,${COLS.join(",")}) VALUES(?,?,${COLS.map(() => "?").join(",")})`, which, w.key, ...COLS.map(c => cell(c, w[c])));
      else if (!r.edited && COLS.some(c => String(r[c] == null ? "" : r[c]) !== String(cell(c, w[c]) == null ? "" : cell(c, w[c]))))
        db.run(`UPDATE console_screens SET ${COLS.map(c => c + "=?").join(",")} WHERE id=?`, ...COLS.map(c => cell(c, w[c])), r.id);
    }
    const keys = new Set(want.map(w => w.key));
    for (const r of have.values()) if (!keys.has(r.key) && !r.edited) db.run("DELETE FROM console_screens WHERE id=?", r.id);
  }
  synced = true;
}
const rows = which => { if (!synced) sync(); return D().all("SELECT * FROM console_screens WHERE console=? ORDER BY position, id", which).map(r => ({ ...r, shows: J(r.shows, null), fit: J(r.fit, null) })); };

/* what a console is served: its menu, in the shape its shell draws */
function served(which) {
  const list = rows(which), groups = [];
  const groupOf = (sec, g) => { let x = groups.find(y => y.section === sec && y.g === g); if (!x) groups.push(x = { section: sec, g, items: [] }); return x; };
  for (const r of list) groupOf(r.section, r.grp).items.push(r);
  if (which === "platform") {
    const secs = [];
    for (const g of groups) { let s = secs.find(x => x.n === g.section); if (!s) secs.push(s = { n: g.section, g: [] }); s.g.push({ g: g.g, l: g.items.map(r => [r.key, r.label, r.shows || {}]) }); }
    return { nav: secs };
  }
  return { groups: groups.map(g => g.g), screens: Object.fromEntries(list.map(r => [r.key, { group: r.grp, label: r.label, position: r.position, access: r.access }])), sections: Object.fromEntries(list.filter(r => r.access !== r.key).map(r => [r.key, r.access])) };
}
module.exports = { declared, ensure, sync, served, SEED };
